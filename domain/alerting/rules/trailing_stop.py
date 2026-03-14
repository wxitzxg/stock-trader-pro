"""
动态止盈止损规则
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


class TrailingStopRule:
    """动态止盈止损规则"""

    def __init__(self):
        self.alert_log = []
        self.alert_timeout = 1800

    def check(
        self,
        code: str,
        cost: float,
        price: float,
        data: Dict,
        config: Dict
    ) -> List[AlertResult]:
        """
        检查动态止盈止损预警

        Args:
            code: 股票代码
            cost: 持仓成本
            price: 当前价格
            data: 行情数据 (high)
            config: 预警配置

        Returns:
            预警结果列表
        """
        alerts = []

        trailing_stop = _get_config_value(config, 'trailing_stop', True)
        if cost <= 0 or not trailing_stop:
            return alerts

        profit_pct = (price - cost) / cost * 100

        # 只有盈利>=10% 时才启用动态止盈
        if profit_pct >= 10:
            high_since = data.get('high', price)
            drawdown = (high_since - price) / high_since * 100 if high_since > cost else 0

            # 利润回撤 10% 清仓
            if drawdown >= 10:
                if not self._alerted_recently(code, 'trailing_stop_10'):
                    alerts.append(AlertResult(
                        alert_type='trailing_stop_10',
                        message=f"🚨 利润回撤{drawdown:.1f}%，建议清仓",
                        weight=3
                    ))

            # 利润回撤 5% 减仓
            elif drawdown >= 5:
                if not self._alerted_recently(code, 'trailing_stop_5'):
                    alerts.append(AlertResult(
                        alert_type='trailing_stop_5',
                        message=f"📉 利润回撤{drawdown:.1f}%，建议减仓",
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
