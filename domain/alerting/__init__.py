"""
实时预警模块 - 整合七大预警规则、仓位管理、动态止损、智能分析引擎
"""
from domain.alerting.engine import RealtimeAlertEngine
from domain.alerting.types import AlertConfig, AlertLevel, AlertType, AlertResult
from domain.alerting.rules import (
    CostRule,
    PriceRule,
    VolumeRule,
    TechnicalRule,
    TrailingStopRule,
)
from domain.alerting.scheduler import SmartScheduler
from domain.alerting.report_generator import (
    MonitorReportGenerator,
    PositionStock,
    WatchlistStock,
    StockAlert,
    StockData,
)

__all__ = [
    # 核心引擎
    'RealtimeAlertEngine',
    # 预警类型
    'AlertConfig',
    'AlertLevel',
    'AlertType',
    'AlertResult',
    # 预警规则
    'CostRule',
    'PriceRule',
    'VolumeRule',
    'TechnicalRule',
    'TrailingStopRule',
    # 调度器
    'SmartScheduler',
    # 报告生成器
    'MonitorReportGenerator',
    'PositionStock',
    'WatchlistStock',
    'StockAlert',
    'StockData',
]
