"""
交易时间判断工具类
供 realalerts 预警模块和 mystocks 价格更新模块共用

A 股交易时间规则:
- 交易日：周一至周五 AND 非法定节假日 (OR 调休工作日)
- 交易时段：09:30-11:30, 13:00-15:00 (北京时间)
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from config import get_holidays, get_makeup_workdays


class TradingTimeUtils:
    """
    A 股交易时间判断工具类

    交易时间规则:
    - 交易日：周一至周五 AND 非法定节假日 (OR 调休工作日)
    - 交易时段：09:30-11:30, 13:00-15:00 (北京时间)
    """

    # 交易时段定义 (北京时间)
    MORNING_START = (9, 30)    # 上午开盘
    MORNING_END = (11, 30)     # 上午收盘
    AFTERNOON_START = (13, 0)  # 下午开盘
    AFTERNOON_END = (15, 0)    # 下午收盘

    @classmethod
    def _get_beijing_time(cls) -> datetime:
        """
        获取当前北京时间

        Returns:
            datetime: 北京时间
        """
        now = datetime.now()

        # 如果是 UTC 时间，转换为北京时间 (UTC+8)
        if now.tzinfo is not None:
            try:
                bj_now = now + timedelta(hours=8)
            except Exception:
                bj_now = now
        else:
            # 假设本地时间已是北京时间
            bj_now = now

        return bj_now

    @classmethod
    def is_trading_day(cls, date: Optional[datetime] = None) -> bool:
        """
        判断是否是 A 股交易日

        Args:
            date: 要判断的日期，默认为今天

        Returns:
            bool: 是否是交易日
        """
        check_date = date or cls._get_beijing_time()
        date_str = check_date.strftime("%Y-%m-%d")

        # 1. 检查是否是周末
        is_weekend = check_date.weekday() >= 5

        # 2. 获取当年节假日和调休日
        year = check_date.year
        holidays = get_holidays(year)
        makeup_workdays = get_makeup_workdays(year)

        # 3. 判断逻辑
        if date_str in makeup_workdays:
            # 调休工作日：虽然是周末，但是交易日
            return True

        if is_weekend:
            # 周末且非调休：非交易日
            return False

        if date_str in holidays:
            # 法定节假日：非交易日
            return False

        return True

    @classmethod
    def is_market_hours(cls) -> bool:
        """
        判断当前是否是交易时段（不判断是否是交易日）

        Returns:
            bool: 是否是交易时段
        """
        bj_now = cls._get_beijing_time()

        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute

        # 上午交易时段：09:30-11:30
        morning = 930 <= time_val <= 1130

        # 下午交易时段：13:00-15:00
        afternoon = 1300 <= time_val <= 1500

        return morning or afternoon

    @classmethod
    def is_trading_time(cls) -> Dict[str, Any]:
        """
        综合判断当前是否是交易时间（既要是交易日，也要是交易时段）

        Returns:
            {
                "is_trading": bool,       # 是否是交易时间（综合结果）
                "is_trading_day": bool,   # 是否是交易日
                "is_market_hours": bool,  # 是否是交易时段
                "market_phase": str,      # 市场阶段
                "reason": str,            # 原因说明
                "beijing_time": datetime, # 北京时间
            }
        """
        bj_now = cls._get_beijing_time()
        date_str = bj_now.strftime("%Y-%m-%d")
        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute

        # 1. 判断是否是交易日
        trading_day = cls.is_trading_day(bj_now)

        # 2. 判断市场阶段
        is_weekend = bj_now.weekday() >= 5
        holidays = get_holidays(bj_now.year)
        is_holiday = date_str in holidays
        is_makeup = date_str in get_makeup_workdays(bj_now.year)

        morning = 930 <= time_val <= 1130
        afternoon = 1300 <= time_val <= 1500
        is_market = morning or afternoon

        # 3. 综合判断
        is_trading = trading_day and is_market

        # 4. 确定市场阶段和原因
        if is_weekend and not is_makeup:
            phase = "weekend"
            reason = "周末休市"
        elif is_holiday:
            phase = "holiday"
            reason = f"节假日：{holidays[date_str]}"
        elif not is_market:
            if time_val < 930:
                phase = "pre_market"
                reason = "盘前时间 (09:30 开盘)"
            elif 1130 < time_val < 1300:
                phase = "lunch_break"
                reason = "午休时间 (13:00 开盘)"
            elif time_val >= 1500:
                phase = "closed"
                reason = "已收盘 (15:00 收盘)"
            else:
                phase = "unknown"
                reason = "未知状态"
        else:
            phase = "afternoon" if afternoon else "market"
            reason = "交易时间"

        return {
            "is_trading": is_trading,
            "is_trading_day": trading_day,
            "is_market_hours": is_market,
            "market_phase": phase,
            "reason": reason,
            "beijing_time": bj_now,
        }

    @classmethod
    def get_next_market_open(cls) -> datetime:
        """
        获取下次开盘时间（北京时间 9:30）

        Returns:
            datetime: 下次开盘时间
        """
        bj_now = cls._get_beijing_time()
        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute

        # 如果已经收盘或午休，返回下午或明天开盘
        if time_val >= 1500:
            # 已收盘，返回下一个交易日 9:30
            check_date = bj_now + timedelta(days=1)
            for _ in range(8):  # 最多找 8 天
                if cls.is_trading_day(check_date):
                    return check_date.replace(hour=9, minute=30, second=0, microsecond=0)
                check_date = check_date + timedelta(days=1)
            return check_date.replace(hour=9, minute=30, second=0, microsecond=0)

        if 1130 < time_val < 1300:
            # 午休时间，返回今天 13:00（如果今天是交易日）
            if cls.is_trading_day(bj_now):
                return bj_now.replace(hour=13, minute=0, second=0, microsecond=0)

        if time_val < 930:
            # 盘前时间，返回今天或下一个交易日 9:30
            if cls.is_trading_day(bj_now):
                return bj_now.replace(hour=9, minute=30, second=0, microsecond=0)
            # 今天不是交易日，找下一个交易日
            check_date = bj_now + timedelta(days=1)
            for _ in range(8):
                if cls.is_trading_day(check_date):
                    return check_date.replace(hour=9, minute=30, second=0, microsecond=0)
                check_date = check_date + timedelta(days=1)

        # 交易时间内
        return bj_now

    @classmethod
    def get_market_phase(cls) -> str:
        """
        获取当前市场阶段

        Returns:
            str: market(上午)/lunch(午休)/afternoon(下午)/closed(收盘)/weekend/holiday
        """
        result = cls.is_trading_time()
        return result["market_phase"]

    @classmethod
    def get_trading_date_range(cls, start_date: datetime, end_date: datetime) -> list:
        """
        获取指定日期范围内的所有交易日

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            交易日列表 [datetime, ...]
        """
        trading_days = []
        current = start_date

        while current <= end_date:
            if cls.is_trading_day(current):
                trading_days.append(current)
            current = current + timedelta(days=1)

        return trading_days
