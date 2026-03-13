"""
成交量异动预警规则
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


class VolumeRule:
    """成交量异动预警规则"""

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
        检查成交量异动预警

        Args:
            code: 股票代码
            data: 行情数据 (volume, ma5_volume)
            config: 预警配置

        Returns:
            预警结果列表
        """
        alerts = []

        current_volume = data.get('volume', 0)
        ma5_volume = data.get('ma5_volume', 0)
        volume_surge = _get_config_value(config, 'volume_surge', 2.0)

        if current_volume > 0 and ma5_volume > 0:
            volume_ratio = current_volume / ma5_volume

            # 放量
            if volume_ratio >= volume_surge:
                if not self._alerted_recently(code, 'volume_surge'):
                    alerts.append(AlertResult(
                        alert_type='volume_surge',
                        message=f"📊 放量{volume_ratio:.1f}倍 (5 日均量)",
                        weight=2
                    ))

            # 缩量
            elif volume_ratio <= 0.5:
                if not self._alerted_recently(code, 'volume_shrink'):
                    alerts.append(AlertResult(
                        alert_type='volume_shrink',
                        message=f"📉 缩量{volume_ratio:.1f}倍 (5 日均量)",
                        weight=1
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
