#!/usr/bin/env python3
"""
中国 A 股交易日历配置
从 config.json 加载节假日数据

每年初更新 config.json 中的当年节假日配置
"""
from datetime import datetime
from .loader import get_config


def get_holidays(year: int = None) -> dict:
    """
    获取指定年份的节假日配置

    Args:
        year: 年份，默认为当前年份

    Returns:
        节假日字典，格式：{"YYYY-MM-DD": "节日名称"}
    """
    config = get_config()
    return config.get_holidays(year)


def get_makeup_workdays(year: int = None) -> dict:
    """
    获取指定年份的调休工作日

    Args:
        year: 年份，默认为当前年份

    Returns:
        调休日字典，格式：{"YYYY-MM-DD": "调休原因"}
    """
    config = get_config()
    return config.get_makeup_workdays(year)


def is_holiday(date_str: str) -> bool:
    """
    判断指定日期是否是节假日

    Args:
        date_str: 日期字符串，格式 "YYYY-MM-DD"

    Returns:
        bool: 是否是节假日
    """
    config = get_config()
    return config.is_holiday(date_str)


def is_makeup_workday(date_str: str) -> bool:
    """
    判断指定日期是否是调休工作日

    Args:
        date_str: 日期字符串，格式 "YYYY-MM-DD"

    Returns:
        bool: 是否是调休工作日
    """
    config = get_config()
    return config.is_makeup_workday(date_str)
