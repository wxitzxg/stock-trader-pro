"""
技术指标预警规则 - 均线金叉死叉、RSI 超买超卖、跳空缺口
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AlertResult:
    """预警结果"""
    alert_type: str
    message: str
    weight: int


def _get_config_value(config, key: str, default=None):
    """获取配置值 (支持 dict 和 dataclass)"""
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


class TechnicalRule:
    """技术指标预警规则"""

    def __init__(self):
        self.alert_log = []
        self.alert_timeout = 1800

    def check(
        self,
        code: str,
        data: Dict,
        config: Dict
    ) -> List[AlertResult]:
        """
        检查技术指标预警

        Args:
            code: 股票代码
            data: 行情数据 (ma5, ma10, prev_ma5, prev_ma10, rsi, prev_high, prev_low, open)
            config: 预警配置

        Returns:
            预警结果列表
        """
        alerts = []

        # 1. 均线金叉/死叉
        ma_monitor = _get_config_value(config, 'ma_monitor', True)
        if ma_monitor:
            ma5 = data.get('ma5', 0)
            ma10 = data.get('ma10', 0)
            prev_ma5 = data.get('prev_ma5', 0)
            prev_ma10 = data.get('prev_ma10', 0)

            if ma5 > 0 and ma10 > 0 and prev_ma5 > 0 and prev_ma10 > 0:
                # 金叉
                if prev_ma5 <= prev_ma10 and ma5 > ma10:
                    if not self._alerted_recently(code, 'ma_golden'):
                        alerts.append(AlertResult(
                            alert_type='ma_golden',
                            message=f"🌟 均线金叉 (MA5¥{ma5:.2f}上穿 MA10¥{ma10:.2f})",
                            weight=3
                        ))

                # 死叉
                if prev_ma5 >= prev_ma10 and ma5 < ma10:
                    if not self._alerted_recently(code, 'ma_death'):
                        alerts.append(AlertResult(
                            alert_type='ma_death',
                            message=f"⚠️ 均线死叉 (MA5¥{ma5:.2f}下穿 MA10¥{ma10:.2f})",
                            weight=3
                        ))

        # 2. RSI 超买/超卖
        rsi_monitor = _get_config_value(config, 'rsi_monitor', True)
        if rsi_monitor:
            rsi = data.get('rsi', 0)
            if rsi > 0:
                if rsi > 70:
                    if not self._alerted_recently(code, 'rsi_high'):
                        alerts.append(AlertResult(
                            alert_type='rsi_high',
                            message=f"🔥 RSI 超买 ({rsi:.1f})，可能回调",
                            weight=2
                        ))
                elif rsi < 30:
                    if not self._alerted_recently(code, 'rsi_low'):
                        alerts.append(AlertResult(
                            alert_type='rsi_low',
                            message=f"❄️ RSI 超卖 ({rsi:.1f})，可能反弹",
                            weight=2
                        ))

        # 3. 跳空缺口
        gap_monitor = _get_config_value(config, 'gap_monitor', True)
        if gap_monitor:
            prev_high = data.get('prev_high', 0)
            prev_low = data.get('prev_low', 0)
            current_open = data.get('open', 0)

            if prev_high > 0 and current_open > prev_high * 1.01:
                gap_pct = (current_open - prev_high) / prev_high * 100
                if not self._alerted_recently(code, 'gap_up'):
                    alerts.append(AlertResult(
                        alert_type='gap_up',
                        message=f"⬆️ 向上跳空{gap_pct:.1f}%",
                        weight=2
                    ))
            elif prev_low > 0 and current_open < prev_low * 0.99:
                gap_pct = (prev_low - current_open) / prev_low * 100
                if not self._alerted_recently(code, 'gap_down'):
                    alerts.append(AlertResult(
                        alert_type='gap_down',
                        message=f"⬇️ 向下跳空{gap_pct:.1f}%",
                        weight=2
                    ))

        for alert in alerts:
            self._record_alert(code, alert.alert_type)

        return alerts

    def _alerted_recently(self, code: str, atype: str) -> bool:
        """检查是否最近已触发"""
        import time
        now = time.time()
        self.alert_log = [l for l in self.alert_log if now - l['t'] < self.alert_timeout]
        for l in self.alert_log:
            if l['c'] == code and l['a'] == atype:
                return True
        return False

    def _record_alert(self, code: str, atype: str):
        """记录预警"""
        import time
        self.alert_log.append({
            'c': code,
            'a': atype,
            't': time.time()
        })
