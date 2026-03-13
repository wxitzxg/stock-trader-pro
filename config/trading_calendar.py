"""
中国 A 股交易日历配置
每年初更新当年的节假日安排

配置说明:
- CHINA_HOLIDAYS_YYYY: 法定节假日（休市）
- CHINA_MAKEUP_WORKDAYS_YYYY: 调休工作日（周末上班，开市）

数据来源：国务院办公厅关于节假日安排的通知
"""

# ========== 2025 年 A 股法定节假日 ==========
CHINA_HOLIDAYS_2025 = {
    # 元旦：1 月 1 日放假
    "2025-01-01": "元旦",

    # 春节：1 月 28 日 (除夕) 至 2 月 4 日放假
    "2025-01-28": "春节",
    "2025-01-29": "春节",
    "2025-01-30": "春节",
    "2025-01-31": "春节",
    "2025-02-03": "春节",
    "2025-02-04": "春节",

    # 清明节：4 月 4 日至 4 月 6 日放假
    "2025-04-04": "清明节",
    "2025-04-05": "清明节",
    "2025-04-06": "清明节",

    # 劳动节：5 月 1 日至 5 月 5 日放假
    "2025-05-01": "劳动节",
    "2025-05-02": "劳动节",
    "2025-05-03": "劳动节",
    "2025-05-04": "劳动节",
    "2025-05-05": "劳动节",

    # 端午节：5 月 31 日至 6 月 2 日放假
    "2025-05-31": "端午节",
    "2025-06-01": "端午节",
    "2025-06-02": "端午节",

    # 国庆节 + 中秋：10 月 1 日至 10 月 8 日放假
    "2025-10-01": "国庆节",
    "2025-10-02": "国庆节",
    "2025-10-03": "国庆节",
    "2025-10-04": "国庆节",
    "2025-10-05": "国庆节",
    "2025-10-06": "国庆节",
    "2025-10-07": "国庆节",
    "2025-10-08": "国庆节",
}

# 2025 年调休工作日（周末需要上班）
CHINA_MAKEUP_WORKDAYS_2025 = {
    # 春节调休
    "2025-01-26": "春节调休",  # 周日上班
    "2025-02-08": "春节调休",  # 周六上班

    # 劳动节调休
    "2025-04-27": "劳动节调休",  # 周日上班
}


# ========== 2026 年 A 股法定节假日 ==========
CHINA_HOLIDAYS_2026 = {
    # 元旦：1 月 1 日放假
    "2026-01-01": "元旦",

    # 春节：2 月 17 日 (除夕) 至 2 月 20 日放假
    "2026-02-17": "春节",
    "2026-02-18": "春节",
    "2026-02-19": "春节",
    "2026-02-20": "春节",

    # 清明节：4 月 5 日放假
    "2026-04-05": "清明节",

    # 劳动节：5 月 1 日至 5 月 3 日放假
    "2026-05-01": "劳动节",
    "2026-05-02": "劳动节",
    "2026-05-03": "劳动节",

    # 端午节：6 月 19 日放假
    "2026-06-19": "端午节",

    # 中秋节：9 月 25 日放假
    "2026-09-25": "中秋节",

    # 国庆节：10 月 1 日至 10 月 8 日放假
    "2026-10-01": "国庆节",
    "2026-10-02": "国庆节",
    "2026-10-03": "国庆节",
    "2026-10-04": "国庆节",
    "2026-10-05": "国庆节",
    "2026-10-06": "国庆节",
    "2026-10-07": "国庆节",
    "2026-10-08": "国庆节",
}

# 2026 年调休工作日（周末需要上班）
CHINA_MAKEUP_WORKDAYS_2026 = {
    # 如有调休，在此配置
}


def get_holidays(year: int = None) -> dict:
    """
    获取指定年份的节假日配置

    Args:
        year: 年份，默认为当前年份

    Returns:
        节假日字典，格式：{"YYYY-MM-DD": "节日名称"}
    """
    if year is None:
        from datetime import datetime
        year = datetime.now().year

    holidays_map = {
        2025: CHINA_HOLIDAYS_2025,
        2026: CHINA_HOLIDAYS_2026,
        # 后续年份逐年添加
    }

    return holidays_map.get(year, {})


def get_makeup_workdays(year: int = None) -> dict:
    """
    获取指定年份的调休工作日

    Args:
        year: 年份，默认为当前年份

    Returns:
        调休日字典，格式：{"YYYY-MM-DD": "调休原因"}
    """
    if year is None:
        from datetime import datetime
        year = datetime.now().year

    makeup_map = {
        2025: CHINA_MAKEUP_WORKDAYS_2025,
        2026: CHINA_MAKEUP_WORKDAYS_2026,
    }

    return makeup_map.get(year, {})


def is_holiday(date_str: str) -> bool:
    """
    判断指定日期是否是节假日

    Args:
        date_str: 日期字符串，格式 "YYYY-MM-DD"

    Returns:
        bool: 是否是节假日
    """
    try:
        year = int(date_str.split("-")[0])
        holidays = get_holidays(year)
        return date_str in holidays
    except (ValueError, IndexError):
        return False


def is_makeup_workday(date_str: str) -> bool:
    """
    判断指定日期是否是调休工作日

    Args:
        date_str: 日期字符串，格式 "YYYY-MM-DD"

    Returns:
        bool: 是否是调休工作日
    """
    try:
        year = int(date_str.split("-")[0])
        makeup = get_makeup_workdays(year)
        return date_str in makeup
    except (ValueError, IndexError):
        return False
