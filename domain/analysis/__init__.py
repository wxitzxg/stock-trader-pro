"""
Analysis domain - 技术分析领域

整合九转黄金坑策略、顶部背离止盈策略、VCP 爆发突击策略，
以及 indicators 各种指标分析、买卖信号生成器、五维共振总控引擎等功能
"""

# 策略
from domain.analysis.strategies import (
    VCPBreakoutStrategy,
    TDGoldenPitStrategy,
    TopDivergenceStrategy,
)

# 引擎
from domain.analysis.engines import UltimateEngine
from domain.analysis.signals import SignalGenerator

# 指标 (快捷访问)
from domain.analysis.indicators import (
    BaseIndicators,
    TDSequential,
    VCPDetector,
    DivergenceCheck,
    ZigZag,
)

__all__ = [
    # 策略
    'VCPBreakoutStrategy',
    'TDGoldenPitStrategy',
    'TopDivergenceStrategy',
    # 引擎
    'UltimateEngine',
    'SignalGenerator',
    # 指标
    'BaseIndicators',
    'TDSequential',
    'VCPDetector',
    'DivergenceCheck',
    'ZigZag',
]
