"""
Configuration module - 统一配置中心

所有配置从 config.json 加载，通过 loader.py 提供统一访问接口
"""
from .loader import (
    ConfigLoader,
    get_config,
    # 常量导出
    BASE_DIR,
    DATABASE_PATH,
    AKSHARE_TIMEOUT,
    AKSHARE_SEARCH_LIMIT,
    AKSHARE_EXPORT_DAYS_DEFAULT,
    KLINE_CACHE_ENABLED,
    KLINE_DEFAULT_DAYS,
    KLINE_DAILY_UPDATE_TIME,
    STRATEGY_PARAMS,
    SIGNAL_THRESHOLD,
    FIVE_DIMENSION_WEIGHTS,
    DECISION_THRESHOLD,
    POSITION_PARAMS,
    PRICE_ALERT_THRESHOLD,
    TRADING_FEES,
    STOP_LOSS_PARAMS,
    MONITOR_CONFIG,
    REPORT_CONFIG,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    STOCK_PARAMS,
    # 日历函数导出
    get_holidays,
    get_makeup_workdays,
    is_holiday,
    is_makeup_workday,
)

__all__ = [
    # 加载器类
    'ConfigLoader',
    'get_config',
    # 常量
    'BASE_DIR',
    'DATABASE_PATH',
    'AKSHARE_TIMEOUT',
    'AKSHARE_SEARCH_LIMIT',
    'AKSHARE_EXPORT_DAYS_DEFAULT',
    'KLINE_CACHE_ENABLED',
    'KLINE_DEFAULT_DAYS',
    'KLINE_DAILY_UPDATE_TIME',
    'STRATEGY_PARAMS',
    'SIGNAL_THRESHOLD',
    'FIVE_DIMENSION_WEIGHTS',
    'DECISION_THRESHOLD',
    'POSITION_PARAMS',
    'PRICE_ALERT_THRESHOLD',
    'TRADING_FEES',
    'STOP_LOSS_PARAMS',
    'MONITOR_CONFIG',
    'REPORT_CONFIG',
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_FILE',
    'STOCK_PARAMS',
    # 日历函数
    'get_holidays',
    'get_makeup_workdays',
    'is_holiday',
    'is_makeup_workday',
]
