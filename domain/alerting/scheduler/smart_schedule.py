"""
智能调度模块 (Smart Scheduler)
基于北京时间的智能频率控制
支持交易日判断、节假日跳过

注意：交易时间判断逻辑已统一迁移到 common.trading_time.TradingTimeUtils
"""

from datetime import datetime
from typing import Dict, Optional

from config.settings import MONITOR_CONFIG
from domain.common.trading_time import TradingTimeUtils


class SmartScheduler:
    """智能频率控制 (基于北京时间)"""

    @classmethod
    def get_interval(cls, mode: str) -> int:
        """
        获取指定模式的监控间隔（从配置读取）

        Args:
            mode: 模式名称 (market/lunch/after_hours/night/weekend)

        Returns:
            间隔时间（秒）
        """
        key_map = {
            "market": "interval_market",
            "lunch": "interval_lunch",
            "after_hours": "interval_after_hours",
            "night": "interval_night",
            "weekend": "interval_weekend"
        }
        key = key_map.get(mode, "interval_market")
        return MONITOR_CONFIG.get(key, 300)

    @classmethod
    def is_trading_day(cls, date: Optional[datetime] = None) -> bool:
        """
        判断是否是 A 股交易日

        Args:
            date: 要判断的日期，默认为今天

        Returns:
            bool: 是否是交易日
        """
        return TradingTimeUtils.is_trading_day(date)

    @classmethod
    def should_run_now(cls) -> Dict:
        """
        判断当前是否应该执行监控
        只在交易日的交易时段执行预警

        Returns:
            {"run": bool, "mode": str, "stocks": list, "interval": int}
        """
        # 使用统一工具类判断
        result = TradingTimeUtils.is_trading_time()

        if not result["is_trading"]:
            return {"run": False, "reason": result["reason"]}

        # 交易时间内，获取对应区间的间隔
        mode = "market" if result["market_phase"] == "market" else "afternoon"
        interval = cls.get_interval(mode)

        return {
            "run": True,
            "mode": mode,
            "stocks": "all",
            "interval": interval,
            "market_phase": result["market_phase"],
        }

    @classmethod
    def is_market_hours(cls) -> bool:
        """
        判断是否是 A 股交易时间

        Returns:
            bool
        """
        return TradingTimeUtils.is_market_hours()

    @classmethod
    def get_next_market_open(cls) -> datetime:
        """
        获取下次开盘时间

        Returns:
            datetime
        """
        return TradingTimeUtils.get_next_market_open()
