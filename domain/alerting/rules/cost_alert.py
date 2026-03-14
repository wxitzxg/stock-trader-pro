"""
成本百分比预警规则
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AlertResult:
    """预警结果"""
    alert_type: str
    message: str
    weight: int  # 权重 1-3


def _get_config_value(config, key: str, default):
    """获取配置值 (支持 dict 和 dataclass)"""
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


class CostRule:
    """成本百分比预警规则"""

    def __init__(self):
        self.alert_log = []
        self.alert_timeout = 1800  # 30 分钟防骚扰

    def check(
        self,
        code: str,
        cost: float,
        price: float,
        config: Dict
    ) -> List[AlertResult]:
        """
        检查成本百分比预警

        Args:
            code: 股票代码
            cost: 持仓成本
            price: 当前价格
            config: 预警配置

        Returns:
            预警结果列表
        """
        alerts = []

        if cost <= 0 or price <= 0:
            return alerts

        cost_change_pct = (price - cost) / cost * 100

        # 盈利达标
        cost_pct_above = _get_config_value(config, 'cost_pct_above', 15.0)
        if cost_change_pct >= cost_pct_above:
            if not self._alerted_recently(code, 'cost_above'):
                target = cost * (1 + cost_pct_above / 100)
                alerts.append(AlertResult(
                    alert_type='cost_above',
                    message=f"🎯 盈利{cost_pct_above:.0f}% (目标价¥{target:.2f})",
                    weight=3
                ))

        # 亏损止损
        cost_pct_below = _get_config_value(config, 'cost_pct_below', -12.0)
        if cost_change_pct <= cost_pct_below:
            if not self._alerted_recently(code, 'cost_below'):
                target = cost * (1 + cost_pct_below / 100)
                alerts.append(AlertResult(
                    alert_type='cost_below',
                    message=f"🛑 亏损{abs(cost_pct_below):.0f}% (止损价¥{target:.2f})",
                    weight=3
                ))

        # 记录预警
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
