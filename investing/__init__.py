"""
投资策略模块 (Investing Strategies Module)

整合九转黄金坑策略、顶部背离止盈策略、VCP 爆发突击策略，
以及 indicators 各种指标分析、买卖信号生成器、五维共振总控引擎等功能

子模块:
- strategies: 三大策略 (VCP 爆发突击、九转黄金坑、顶部背离止盈)
- indicators: 技术指标 (基础指标、TD 九转、VCP 检测、背离检测、ZigZag)
- engines: 分析引擎 (五维共振总控引擎、买卖信号生成器)

使用示例:
    from investing import VCPBreakoutStrategy, TDGoldenPitStrategy, TopDivergenceStrategy
    from investing import UltimateEngine, SignalGenerator
    from investing.indicators import BaseIndicators, TDSequential, VCPDetector
"""

# 策略
from investing.strategies import (
    VCPBreakoutStrategy,
    TDGoldenPitStrategy,
    TopDivergenceStrategy,
)

# 引擎
from investing.engines import (
    UltimateEngine,
    SignalGenerator,
)

# 指标 (快捷访问)
from investing.indicators import (
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
