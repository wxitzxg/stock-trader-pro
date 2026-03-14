"""
数据源基类
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd


class BaseDataSource(ABC):
    """数据源基类"""

    name: str = "base"  # 数据源名称

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            实时行情数据字典
        """
        pass

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly)
            adjust: 复权类型 (qfq/hfq/none)

        Returns:
            pandas DataFrame with OHLCV data
        """
        pass

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典
        """
        pass

    def get_sector_rank(self, sector_type: int = 1, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取板块排行

        Args:
            sector_type: 板块类型
            limit: 返回数量

        Returns:
            板块排行数据
        """
        pass

    def get_fund_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取资金流向

        Args:
            symbol: 股票代码

        Returns:
            资金流向数据
        """
        pass

    def search_stock(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """
        搜索股票

        Args:
            keyword: 搜索关键词

        Returns:
            股票列表
        """
        pass
