"""
智能调度模块 (Smart Scheduler)
基于北京时间的智能频率控制
支持交易日判断、节假日跳过
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from config.settings import MONITOR_CONFIG


# A 股法定节假日（需每年更新，这里放 2026 年示例）
# 格式："YYYY-MM-DD": "节日名称"
CHINA_HOLIDAYS = {
    # 2026 年元旦
    "2026-01-01": "元旦",
    # 2026 年春节
    "2026-02-17": "春节",
    "2026-02-18": "春节",
    "2026-02-19": "春节",
    "2026-02-20": "春节",
    # 2026 年清明
    "2026-04-05": "清明节",
    # 2026 年劳动节
    "2026-05-01": "劳动节",
    "2026-05-02": "劳动节",
    "2026-05-03": "劳动节",
    # 2026 年端午
    "2026-06-19": "端午节",
    # 2026 年中秋
    "2026-09-25": "中秋节",
    # 2026 年国庆
    "2026-10-01": "国庆节",
    "2026-10-02": "国庆节",
    "2026-10-03": "国庆节",
    "2026-10-04": "国庆节",
    "2026-10-05": "国庆节",
    "2026-10-06": "国庆节",
    "2026-10-07": "国庆节",
    "2026-10-08": "国庆节",
}


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
        check_date = date or datetime.now()
        date_str = check_date.strftime("%Y-%m-%d")

        # 检查是否是周末
        if check_date.weekday() >= 5:
            return False

        # 检查是否是法定节假日
        if date_str in CHINA_HOLIDAYS:
            return False

        return True

    @classmethod
    def should_run_now(cls) -> Dict:
        """
        判断当前是否应该执行监控
        只在交易日的交易时段执行预警

        Returns:
            {"run": bool, "mode": str, "stocks": list, "interval": int}
        """
        now = datetime.now()

        # 转换为北京时间 (假设服务器在 UTC)
        try:
            bj_now = now + timedelta(hours=8) if now.tzinfo else now
        except Exception:
            bj_now = now

        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute
        weekday = bj_now.weekday()

        # 1. 周末不预警
        if weekday >= 5:
            return {"run": False, "reason": "周末休市"}

        # 2. 法定节假日不预警
        date_str = bj_now.strftime("%Y-%m-%d")
        if date_str in CHINA_HOLIDAYS:
            return {"run": False, "reason": f"节假日：{CHINA_HOLIDAYS[date_str]}"}

        # 3. 交易时间 (9:30-11:30, 13:00-15:00) - 5 分钟
        morning = 930 <= time_val <= 1130
        afternoon = 1300 <= time_val <= 1500

        if morning or afternoon:
            interval = cls.get_interval("market")
            return {
                "run": True,
                "mode": "market",
                "stocks": "all",
                "interval": interval
            }

        # 4. 午休时间 (11:30-13:00) - 不预警
        if 1130 < time_val < 1300:
            return {"run": False, "reason": "午休时间"}

        # 5. 收盘后 (15:00-24:00) - 不预警
        if 1500 <= time_val <= 2359:
            return {"run": False, "reason": "已收盘"}

        # 6. 凌晨时间 (0:00-9:30) - 不预警
        if 0 <= time_val < 930:
            return {"run": False, "reason": "盘前时间"}

        return {"run": False, "reason": "未知状态"}

    @classmethod
    def is_market_hours(cls) -> bool:
        """
        判断是否是 A 股交易时间

        Returns:
            bool
        """
        now = datetime.now()
        try:
            bj_now = now + timedelta(hours=8) if now.tzinfo else now
        except Exception:
            bj_now = now

        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute
        weekday = bj_now.weekday()

        # 周末非交易日
        if weekday >= 5:
            return False

        # 上午或下午交易时段
        morning = 930 <= time_val <= 1130
        afternoon = 1300 <= time_val <= 1500

        return morning or afternoon

    @classmethod
    def get_next_market_open(cls) -> datetime:
        """
        获取下次开盘时间

        Returns:
            datetime
        """
        now = datetime.now()
        try:
            bj_now = now + timedelta(hours=8) if now.tzinfo else now
        except Exception:
            bj_now = now

        hour = bj_now.hour
        minute = bj_now.minute
        time_val = hour * 100 + minute
        weekday = bj_now.weekday()

        # 如果是周末，返回下周一 9:30
        if weekday >= 5:
            days_until_monday = 7 - weekday
            next_open = bj_now.replace(
                hour=9, minute=30, second=0, microsecond=0
            ) + timedelta(days=days_until_monday)
            return next_open

        # 下午交易时段，返回 13:00
        if time_val >= 1130 and time_val < 1300:
            return bj_now.replace(hour=13, minute=0, second=0, microsecond=0)

        # 已经收盘，返回明天 9:30
        if time_val >= 1500:
            next_day = bj_now + timedelta(days=1)
            if next_day.weekday() >= 5:
                days_until_monday = 7 - next_day.weekday()
                return next_day.replace(
                    hour=9, minute=30, second=0, microsecond=0
                ) + timedelta(days=days_until_monday)
            return next_day.replace(hour=9, minute=30, second=0, microsecond=0)

        # 凌晨时段，返回今天 9:30
        if time_val < 930:
            return bj_now.replace(hour=9, minute=30, second=0, microsecond=0)

        # 交易时间内
        return bj_now
