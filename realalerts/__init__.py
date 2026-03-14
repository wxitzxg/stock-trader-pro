"""
实时预警模块 - 兼容层（导出到 domain.alerting）
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
from domain.portfolio.services import PositionMonitor, StopLoss
from domain.portfolio.services import SentimentAnalyzer, FundFlowAnalyzer
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
    # 仓位管理
    'PositionMonitor',
    'StopLoss',
    # 智能分析
    'SentimentAnalyzer',
    'FundFlowAnalyzer',
    # 调度器
    'SmartScheduler',
    # 报告生成器
    'MonitorReportGenerator',
    'PositionStock',
    'WatchlistStock',
    'StockAlert',
    'StockData',
]
