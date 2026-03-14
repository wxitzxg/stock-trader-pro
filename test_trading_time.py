#!/usr/bin/env python3
"""
交易时间判断工具类测试
"""
import unittest
from datetime import datetime
from unittest.mock import patch

from domain.common.trading_time import TradingTimeUtils
from config import get_holidays, get_makeup_workdays, is_holiday, is_makeup_workday


class TestTradingCalendar(unittest.TestCase):
    """测试交易日历配置"""

    def test_get_holidays(self):
        """测试获取节假日"""
        holidays_2025 = get_holidays(2025)
        self.assertIn("2025-01-01", holidays_2025)
        self.assertIn("2025-01-28", holidays_2025)

        holidays_2026 = get_holidays(2026)
        self.assertIn("2026-01-01", holidays_2026)
        self.assertIn("2026-02-17", holidays_2026)

    def test_get_makeup_workdays(self):
        """测试获取调休日"""
        makeup_2025 = get_makeup_workdays(2025)
        self.assertIn("2025-01-26", makeup_2025)

    def test_is_holiday(self):
        """测试是否是节假日"""
        self.assertTrue(is_holiday("2025-01-01"))
        self.assertFalse(is_holiday("2025-01-02"))

    def test_is_makeup_workday(self):
        """测试是否是调休工作日"""
        self.assertTrue(is_makeup_workday("2025-01-26"))
        self.assertFalse(is_makeup_workday("2025-01-27"))


class TestTradingTimeUtils(unittest.TestCase):
    """测试交易时间判断工具类"""

    def test_is_trading_day_weekday(self):
        """测试工作日判断"""
        # 创建一个普通的周三
        wednesday = datetime(2025, 3, 12)
        self.assertTrue(TradingTimeUtils.is_trading_day(wednesday))

    def test_is_trading_day_weekend(self):
        """测试周末判断"""
        # 创建一个周六
        saturday = datetime(2025, 3, 15)
        self.assertFalse(TradingTimeUtils.is_trading_day(saturday))

    def test_is_trading_day_holiday(self):
        """测试节假日判断"""
        # 2025 年元旦
        new_year = datetime(2025, 1, 1)
        self.assertFalse(TradingTimeUtils.is_trading_day(new_year))

        # 2025 年春节
        spring_festival = datetime(2025, 1, 28)
        self.assertFalse(TradingTimeUtils.is_trading_day(spring_festival))

    def test_is_trading_day_makeup(self):
        """测试调休工作日判断"""
        # 2025-01-26 是调休工作日（周日上班）
        makeup_day = datetime(2025, 1, 26)
        self.assertTrue(TradingTimeUtils.is_trading_day(makeup_day))

    def test_is_market_hours_morning(self):
        """测试上午交易时段判断"""
        # 模拟上午 10:30
        morning = datetime(2025, 3, 12, 10, 30)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=morning):
            self.assertTrue(TradingTimeUtils.is_market_hours())

    def test_is_market_hours_lunch(self):
        """测试午休时间判断"""
        # 模拟中午 12:00
        lunch = datetime(2025, 3, 12, 12, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=lunch):
            self.assertFalse(TradingTimeUtils.is_market_hours())

    def test_is_market_hours_afternoon(self):
        """测试下午交易时段判断"""
        # 模拟下午 14:00
        afternoon = datetime(2025, 3, 12, 14, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=afternoon):
            self.assertTrue(TradingTimeUtils.is_market_hours())

    def test_is_market_hours_closed(self):
        """测试收盘后判断"""
        # 模拟下午 16:00
        closed = datetime(2025, 3, 12, 16, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=closed):
            self.assertFalse(TradingTimeUtils.is_market_hours())

    def test_is_trading_time_trading(self):
        """测试交易时间综合判断（交易时段）"""
        # 模拟周三下午 14:00（非节假日）
        trading = datetime(2025, 3, 12, 14, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=trading):
            result = TradingTimeUtils.is_trading_time()
            self.assertTrue(result["is_trading"])
            self.assertEqual(result["market_phase"], "afternoon")

    def test_is_trading_time_weekend(self):
        """测试交易时间综合判断（周末）"""
        # 模拟周六下午 14:00
        weekend = datetime(2025, 3, 15, 14, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=weekend):
            result = TradingTimeUtils.is_trading_time()
            self.assertFalse(result["is_trading"])
            self.assertEqual(result["market_phase"], "weekend")

    def test_is_trading_time_holiday(self):
        """测试交易时间综合判断（节假日）"""
        # 模拟 2025 年元旦下午 14:00
        holiday = datetime(2025, 1, 1, 14, 0)
        with patch.object(TradingTimeUtils, '_get_beijing_time', return_value=holiday):
            result = TradingTimeUtils.is_trading_time()
            self.assertFalse(result["is_trading"])
            self.assertEqual(result["market_phase"], "holiday")


if __name__ == "__main__":
    unittest.main()
