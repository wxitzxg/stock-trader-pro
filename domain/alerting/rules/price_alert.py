"""
价格涨跌幅预警规则
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


class PriceRule:
    """价格涨跌幅预警规则"""

    def __init__(self):
        self.alert_log = []
        self.alert_timeout = 1800

    def check(
        self,
        code: str,
        price: float,
        change_pct: float,
        config: Dict
    ) -> List[AlertResult]:
        """
        检查价格涨跌幅预警

        Args:
            code: 股票代码
            price: 当前价格
            change_pct: 涨跌幅百分比
            config: 预警配置

        Returns:
            预警结果列表
        """
        alerts = []

        # 固定价格突破
        price_above = _get_config_value(config, 'price_above')
        if price_above and price >= price_above:
            if not self._alerted_recently(code, 'price_above'):
                alerts.append(AlertResult(
                    alert_type='price_above',
                    message=f"🚀 价格突破¥{price_above:.2f}",
                    weight=2
                ))

        price_below = _get_config_value(config, 'price_below')
        if price_below and price <= price_below:
            if not self._alerted_recently(code, 'price_below'):
                alerts.append(AlertResult(
                    alert_type='price_below',
                    message=f"📉 价格跌破¥{price_below:.2f}",
                    weight=2
                ))

        # 日内大涨
        change_pct_above = _get_config_value(config, 'change_pct_above', 4.0)
        if change_pct >= change_pct_above:
            if not self._alerted_recently(code, 'pct_up'):
                weight = 3 if change_pct >= 7 else (2 if change_pct >= 5 else 1)
                alerts.append(AlertResult(
                    alert_type='pct_up',
                    message=f"📈 日内大涨{change_pct:+.2f}%",
                    weight=weight
                ))

        # 日内大跌
        change_pct_below = _get_config_value(config, 'change_pct_below', -4.0)
        if change_pct <= change_pct_below:
            if not self._alerted_recently(code, 'pct_down'):
                weight = 3 if change_pct <= -7 else (2 if change_pct <= -5 else 1)
                alerts.append(AlertResult(
                    alert_type='pct_down',
                    message=f"📉 日内大跌{change_pct:+.2f}%",
                    weight=weight
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
