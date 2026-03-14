"""
东方财富数据源
提供板块排行、资金流向等数据
"""
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd

from infrastructure.sources.base import BaseDataSource


class EastmoneyDataSource(BaseDataSource):
    """东方财富数据源"""

    name = "eastmoney"

    def __init__(self, timeout: int = 10):
        """
        初始化东方财富数据源

        Args:
            timeout: 请求超时时间 (秒)
        """
        self.timeout = timeout

    def get_sector_rank(self, sector_type: int = 1, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取板块涨幅排行榜

        Args:
            sector_type: 1=行业板块，2=概念板块，3=地域板块
            limit: 返回数量

        Returns:
            板块排行数据
        """
        url = "http://push2.eastmoney.com/api/qt/clist/get"

        # 板块类型参数
        fs_map = {
            1: "m:90+t:2",  # 行业板块
            2: "m:90+t:3",  # 概念板块
            3: "m:90+t:4",  # 地域板块
        }

        fs = fs_map.get(sector_type, "m:90+t:2")

        params = {
            "pn": 1,
            "pz": limit,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fid": "f3",  # 按涨跌幅排序
            "fs": fs,
            "fields": "f12,f14,f2,f3,f5,f6,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
            'Accept': 'application/json',
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code != 200:
                return None

            data = response.json()

            if data.get('rc') != 0:
                return None

            diff_list = data.get('data', {}).get('diff', [])

            sectors = []
            for item in diff_list:
                sectors.append({
                    'code': item.get('f12', ''),
                    'name': item.get('f14', ''),
                    'current': item.get('f2', 0),
                    'change_percent': item.get('f3', 0),
                    'change': item.get('f4', 0),
                    'open': item.get('f5', 0),
                    'high': item.get('f6', 0),
                    'low': item.get('f7', 0),
                    'volume': item.get('f5', 0),
                    'amount': item.get('f6', 0),
                    'turnover': item.get('f8', 0),
                    'pe': item.get('f9', 0),
                    'amplitude': item.get('f10', 0),
                })

            return {
                'source': self.name,
                'type': sector_type,
                'sectors': sectors
            }

        except Exception as e:
            print(f"东方财富板块排行获取失败：{e}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        东方财富不提供单只股票行情，返回 None
        """
        return None

    def get_historical_data(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        东方财富不提供历史 K 线数据，返回 None
        """
        return None

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息（使用东方财富 API）

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典
        """
        try:
            url = "http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": f"1.{symbol}" if symbol.startswith('6') else f"0.{symbol}",
                "fields": "f12,f14,f116,f117,f118,f119,f120,f121,f122,f124,f125,f126,f127"
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quote.eastmoney.com',
            }

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code != 200:
                return None

            data = response.json()
            if data.get('rc') != 0:
                return None

            item = data.get('data', {})

            return {
                'source': self.name,
                'symbol': symbol,
                'name': item.get('f14', ''),
                'code': symbol,
                'pe_ratio': item.get('f116', 0),  # 市盈率
                'pb_ratio': item.get('f117', 0),  # 市净率
                'market_cap': item.get('f118', 0),  # 总市值
                'float_cap': item.get('f119', 0),  # 流通市值
                'total_shares': item.get('f120', 0),  # 总股本
                'float_shares': item.get('f121', 0),  # 流通股本
            }

        except Exception as e:
            print(f"东方财富股票信息获取失败：{e}")
            return None
