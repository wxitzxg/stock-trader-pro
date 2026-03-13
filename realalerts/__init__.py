"""
实时预警模块 - 整合七大预警规则、仓位管理、动态止损、智能分析引擎
"""
from realalerts.engine import RealtimeAlertEngine
from realalerts.types import AlertConfig, AlertLevel, AlertType, AlertResult
from realalerts.rules import (
    CostRule,
    PriceRule,
    VolumeRule,
    TechnicalRule,
    TrailingStopRule,
)
from realalerts.position import PositionMonitor, StopLoss
from realalerts.analysis import SentimentAnalyzer, FundFlowAnalyzer
from realalerts.scheduler import SmartScheduler
from realalerts.report_generator import (
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
