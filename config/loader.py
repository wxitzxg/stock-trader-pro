#!/usr/bin/env python3
"""
Configuration Loader - 统一配置加载器
从 config.json 加载所有配置，提供统一的访问接口
"""
import json
import os
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime


class ConfigLoader:
    """配置加载器单例类"""

    _instance = None
    _config: Dict = {}
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config = self._load_config()
        self._initialized = True

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent / 'config.json'
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点分隔路径）

        Args:
            key: 配置键，支持点分隔路径，如 "database.path"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict:
        """获取完整配置字典"""
        return self._config.copy()

    # ========== 便捷访问方法 ==========

    @property
    def base_dir(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent

    @property
    def database_path(self) -> Path:
        """获取数据库路径"""
        return self.base_dir / self.get("database.path", "storage/investment.db")

    @property
    def akshare_timeout(self) -> int:
        """获取 AKShare 超时时间"""
        return self.get("akshare.timeout", 30)

    @property
    def strategy_params(self) -> Dict:
        """获取策略参数"""
        return self.get("strategy_params", {})

    @property
    def trading_fees(self) -> Dict:
        """获取交易费用配置"""
        return self.get("trading_fees", {})

    @property
    def monitor_config(self) -> Dict:
        """获取监控配置"""
        return self.get("monitor_config", {})

    @property
    def stock_params(self) -> Dict:
        """获取股票参数"""
        return self.get("stock_params", {})

    def get_stock_params(self, symbol: str, param_key: str, default: Any = None) -> Any:
        """
        获取股票特定参数（优先使用股票特定参数，否则回退到默认值）

        Args:
            symbol: 股票代码
            param_key: 参数键 (如 'vcp', 'zigzag')
            default: 默认值

        Returns:
            参数字典或值
        """
        stock_params = self.get(f"stock_params.stocks.{symbol}", {})
        stock_value = stock_params.get(param_key)
        default_value = self.get(f"stock_params.defaults.{param_key}", default)

        if isinstance(stock_value, dict) and isinstance(default_value, dict):
            return {**default_value, **stock_value}

        return stock_value if stock_value is not None else default_value

    # ========== 日历相关方法 ==========

    def get_holidays(self, year: int = None) -> Dict[str, str]:
        """
        获取指定年份的节假日配置

        Args:
            year: 年份，默认为当前年份

        Returns:
            节假日字典，格式：{"YYYY-MM-DD": "节日名称"}
        """
        if year is None:
            year = datetime.now().year

        holidays = self.get("calendar.holidays", {})
        return holidays.get(str(year), {})

    def get_makeup_workdays(self, year: int = None) -> Dict[str, str]:
        """
        获取指定年份的调休工作日

        Args:
            year: 年份，默认为当前年份

        Returns:
            调休日字典，格式：{"YYYY-MM-DD": "调休原因"}
        """
        if year is None:
            year = datetime.now().year

        makeup = self.get("calendar.makeup_workdays", {})
        return makeup.get(str(year), {})

    def is_holiday(self, date_str: str) -> bool:
        """
        判断指定日期是否是节假日

        Args:
            date_str: 日期字符串，格式 "YYYY-MM-DD"

        Returns:
            bool: 是否是节假日
        """
        try:
            year = int(date_str.split("-")[0])
            holidays = self.get_holidays(year)
            return date_str in holidays
        except (ValueError, IndexError):
            return False

    def is_makeup_workday(self, date_str: str) -> bool:
        """
        判断指定日期是否是调休工作日

        Args:
            date_str: 日期字符串，格式 "YYYY-MM-DD"

        Returns:
            bool: 是否是调休工作日
        """
        try:
            year = int(date_str.split("-")[0])
            makeup = self.get_makeup_workdays(year)
            return date_str in makeup
        except (ValueError, IndexError):
            return False

    # ========== 股票参数管理方法 ==========

    def get_vcp_params(self, symbol: str) -> Dict:
        """获取 VCP 参数"""
        default_vcp = {
            'min_drops': 2,
            'max_drops': 4,
            'min_contraction': 0.5
        }
        return self.get_stock_params(symbol, 'vcp', default_vcp)

    def get_zigzag_params(self, symbol: str) -> Dict:
        """获取 ZigZag 参数"""
        default_zigzag = {'threshold': 0.05}
        return self.get_stock_params(symbol, 'zigzag', default_zigzag)

    def get_td_params(self, symbol: str) -> Dict:
        """获取 TD Sequential 参数"""
        default_td = {'period': 9, 'compare_period': 4}
        return self.get_stock_params(symbol, 'td', default_td)

    def get_rsi_params(self, symbol: str) -> Dict:
        """获取 RSI 参数"""
        default_rsi = {'period': 14, 'overbought': 70, 'oversold': 30}
        return self.get_stock_params(symbol, 'rsi', default_rsi)

    def get_macd_params(self, symbol: str) -> Dict:
        """获取 MACD 参数"""
        default_macd = {'fast': 12, 'slow': 26, 'signal': 9}
        return self.get_stock_params(symbol, 'macd', default_macd)

    def get_divergence_params(self, symbol: str) -> Dict:
        """获取 Divergence 背离检测参数"""
        default_divergence = {'window': 20}
        return self.get_stock_params(symbol, 'divergence', default_divergence)

    def list_all_stocks(self) -> list:
        """列出所有配置了参数的股票"""
        stocks = self.get("stock_params.stocks", {})
        return list(stocks.keys())

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """获取股票基本信息"""
        return self.get(f"stock_params.stocks.{symbol}")

    def get_defaults(self) -> Dict:
        """获取默认参数"""
        return self.get("stock_params.defaults", {})

    def set_stock_params(self, symbol: str, name: str = None, **kwargs):
        """
        设置股票参数

        Args:
            symbol: 股票代码
            name: 股票名称
            **kwargs: 参数字典 (如 vcp={'min_drops': 3})
        """
        stocks = self._config.setdefault("stock_params", {}).setdefault("stocks", {})
        if symbol not in stocks:
            stocks[symbol] = {}
        if name:
            stocks[symbol]['name'] = name
        for key, value in kwargs.items():
            stocks[symbol][key] = value

    def remove_stock_params(self, symbol: str) -> bool:
        """删除股票参数配置"""
        stocks = self._config.get("stock_params", {}).get("stocks", {})
        if symbol in stocks:
            del stocks[symbol]
            return True
        return False

    def save_params(self):
        """保存参数到文件"""
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)


# ========== 全局单例 ==========
_config_loader = ConfigLoader()


def get_config() -> ConfigLoader:
    """获取配置加载器单例"""
    return _config_loader


# ========== 模块级导出（保持向后兼容） ==========
# 这些常量从 JSON 配置加载，保持现有导入方式不变

BASE_DIR = _config_loader.base_dir
DATABASE_PATH = _config_loader.database_path
AKSHARE_TIMEOUT = _config_loader.akshare_timeout
STRATEGY_PARAMS = _config_loader.strategy_params
TRADING_FEES = _config_loader.trading_fees
MONITOR_CONFIG = _config_loader.monitor_config
STOCK_PARAMS = _config_loader.stock_params

# 其他配置导出
AKSHARE_SEARCH_LIMIT = _config_loader.get("akshare.search_limit", 20)
AKSHARE_EXPORT_DAYS_DEFAULT = _config_loader.get("akshare.export_days_default", 60)
KLINE_CACHE_ENABLED = _config_loader.get("kline.cache_enabled", True)
KLINE_DEFAULT_DAYS = _config_loader.get("kline.default_days", 250)
KLINE_DAILY_UPDATE_TIME = _config_loader.get("kline.daily_update_time", "00:00")
SIGNAL_THRESHOLD = _config_loader.get("signal_threshold", {})
FIVE_DIMENSION_WEIGHTS = _config_loader.get("five_dimension_weights", {})
DECISION_THRESHOLD = _config_loader.get("decision_threshold", {})
POSITION_PARAMS = _config_loader.get("position_params", {})
PRICE_ALERT_THRESHOLD = _config_loader.get("price_alert_threshold", {})
STOP_LOSS_PARAMS = _config_loader.get("stop_loss_params", {})
REPORT_CONFIG = _config_loader.get("report_config", {})
LOG_LEVEL = _config_loader.get("log.level", "INFO")
LOG_FORMAT = _config_loader.get("log.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = BASE_DIR / _config_loader.get("log.file", "storage/stock-trader.log")

# 日历函数（从 JSON 加载数据）
get_holidays = _config_loader.get_holidays
get_makeup_workdays = _config_loader.get_makeup_workdays
is_holiday = _config_loader.is_holiday
is_makeup_workday = _config_loader.is_makeup_workday
