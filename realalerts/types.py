"""
预警类型和配置
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"       # 提醒级
    WARNING = "warning"  # 警告级
    CRITICAL = "critical"  # 紧急级


class AlertType(Enum):
    """预警类型"""
    COST_ABOVE = "cost_above"      # 盈利达标
    COST_BELOW = "cost_below"      # 亏损止损
    PRICE_ABOVE = "price_above"    # 价格突破
    PRICE_BELOW = "price_below"    # 价格跌破
    CHANGE_UP = "pct_up"           # 日内大涨
    CHANGE_DOWN = "pct_down"       # 日内大跌
    VOLUME_SURGE = "volume_surge"  # 放量
    VOLUME_SHRINK = "volume_shrink"  # 缩量
    MA_GOLDEN = "ma_golden"        # 均线金叉
    MA_DEATH = "ma_death"          # 均线死叉
    RSI_OVERBOUGHT = "rsi_high"    # RSI 超买
    RSI_OVERSOLD = "rsi_low"       # RSI 超卖
    GAP_UP = "gap_up"              # 向上跳空
    GAP_DOWN = "gap_down"          # 向下跳空
    TRAILING_STOP_5 = "trailing_stop_5"   # 回撤 5% 减仓
    TRAILING_STOP_10 = "trailing_stop_10" # 回撤 10% 清仓


@dataclass
class AlertConfig:
    """预警配置"""
    # 成本百分比预警
    cost_pct_above: float = 15.0   # 盈利 15% 提醒
    cost_pct_below: float = -12.0  # 亏损 12% 提醒

    # 日内涨跌幅预警
    change_pct_above: float = 4.0  # 日内大涨
    change_pct_below: float = -4.0  # 日内大跌

    # 成交量异动
    volume_surge: float = 2.0      # 放量>2 倍均量

    # 技术指标开关
    ma_monitor: bool = True        # 均线金叉死叉
    rsi_monitor: bool = True       # RSI 超买超卖
    gap_monitor: bool = True       # 跳空缺口
    trailing_stop: bool = True     # 动态止盈

    # 固定价格预警 (可选)
    price_above: Optional[float] = None
    price_below: Optional[float] = None

    # 目标价位 (可选)
    target_buy: Optional[float] = None
    target_reduce: Optional[float] = None
    stop_loss: Optional[float] = None


@dataclass
class AlertResult:
    """预警结果"""
    alert_type: str
    message: str
    weight: int  # 权重 1-3
