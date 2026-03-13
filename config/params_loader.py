#!/usr/bin/env python3
"""
股票参数加载器
支持每支股票独立的策略参数配置，默认回退到全局参数
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any


class StockParamsLoader:
    """股票参数加载器"""

    def __init__(self, params_file: str = None):
        """
        初始化参数加载器

        Args:
            params_file: 参数文件路径 (默认为 config/stock_params.json)
        """
        self.params_file = Path(params_file) if params_file else self._default_path()
        self._params = self._load_params()
        self._defaults = self._params.get('defaults', {})
        self._stocks = self._params.get('stocks', {})

    def _default_path(self) -> Path:
        """获取默认参数文件路径"""
        return Path(__file__).parent / 'stock_params.json'

    def _load_params(self) -> Dict:
        """加载参数文件"""
        if not self.params_file.exists():
            return {'defaults': {}, 'stocks': {}}
        try:
            with open(self.params_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {'defaults': {}, 'stocks': {}}

    def get_params(self, symbol: str, param_key: str, default: Any = None) -> Any:
        """
        获取股票参数（优先使用股票特定参数，否则回退到默认值）

        Args:
            symbol: 股票代码
            param_key: 参数键 (如 'vcp', 'zigzag')
            default: 默认值

        Returns:
            参数字典或值
        """
        stock_params = self._stocks.get(symbol, {})
        stock_value = stock_params.get(param_key)
        default_value = self._defaults.get(param_key, default)

        if isinstance(stock_value, dict) and isinstance(default_value, dict):
            return {**default_value, **stock_value}

        return stock_value if stock_value is not None else default_value

    def get_vcp_params(self, symbol: str) -> Dict:
        """获取 VCP 参数"""
        default_vcp = {
            'min_drops': 2,
            'max_drops': 4,
            'min_contraction': 0.5
        }
        return self.get_params(symbol, 'vcp', default_vcp)

    def get_zigzag_params(self, symbol: str) -> Dict:
        """获取 ZigZag 参数"""
        default_zigzag = {'threshold': 0.05}
        return self.get_params(symbol, 'zigzag', default_zigzag)

    def get_td_params(self, symbol: str) -> Dict:
        """获取 TD Sequential 参数"""
        default_td = {'period': 9, 'compare_period': 4}
        return self.get_params(symbol, 'td', default_td)

    def get_rsi_params(self, symbol: str) -> Dict:
        """获取 RSI 参数"""
        default_rsi = {'period': 14, 'overbought': 70, 'oversold': 30}
        return self.get_params(symbol, 'rsi', default_rsi)

    def get_macd_params(self, symbol: str) -> Dict:
        """获取 MACD 参数"""
        default_macd = {'fast': 12, 'slow': 26, 'signal': 9}
        return self.get_params(symbol, 'macd', default_macd)

    def get_divergence_params(self, symbol: str) -> Dict:
        """获取 Divergence 背离检测参数"""
        default_divergence = {'window': 20}
        return self.get_params(symbol, 'divergence', default_divergence)

    def save_params(self):
        """保存参数到文件"""
        self._params['defaults'] = self._defaults
        self._params['stocks'] = self._stocks
        with open(self.params_file, 'w', encoding='utf-8') as f:
            json.dump(self._params, f, indent=2, ensure_ascii=False)

    def set_stock_params(self, symbol: str, name: str = None, **kwargs):
        """
        设置股票参数

        Args:
            symbol: 股票代码
            name: 股票名称
            **kwargs: 参数字典 (如 vcp={'min_drops': 3})
        """
        if symbol not in self._stocks:
            self._stocks[symbol] = {}
        if name:
            self._stocks[symbol]['name'] = name
        for key, value in kwargs.items():
            self._stocks[symbol][key] = value

    def remove_stock_params(self, symbol: str) -> bool:
        """删除股票参数配置"""
        if symbol in self._stocks:
            del self._stocks[symbol]
            return True
        return False

    def list_all_stocks(self) -> list:
        """列出所有配置了参数的股票"""
        return list(self._stocks.keys())

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """获取股票基本信息"""
        return self._stocks.get(symbol)

    def get_defaults(self) -> Dict:
        """获取默认参数"""
        return self._defaults
