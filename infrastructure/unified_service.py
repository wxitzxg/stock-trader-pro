"""
统一股票查询服务
整合 AKShare、东方财富、新浪财经三个数据源
提供智能路由和故障转移机制
"""
from typing import Optional, Dict, Any, List
import pandas as pd

from infrastructure.sources.akshare_source import AKShareDataSource
from infrastructure.sources.eastmoney_source import EastmoneyDataSource
from infrastructure.sources.sina_source import SinaDataSource
from infrastructure.models.quote_data import (
    UnifiedStockData,
    QuoteData,
    StockInfo,
    FundFlowSummary,
    SectorData,
)


class UnifiedStockQueryService:
    """
    统一股票查询服务

    智能路由策略：
    - get_quote(): 新浪财经 (主) → AKShare(备)
    - get_historical_data(): AKShare (唯一) - 带数据库缓存
    - get_stock_info(): 东方财富 (主) → AKShare(备)
    - get_fund_flow(): AKShare (唯一)
    - get_sector_rank(): 东方财富 (主) → AKShare(备)
    - search_stock(): AKShare (唯一)
    """

    def __init__(self, db=None, timeout: int = 10):
        """
        初始化统一服务

        Args:
            db: Database 实例（用于 K 线缓存）
            timeout: 请求超时时间 (秒)
        """
        self.akshare = AKShareDataSource(db=db, timeout=timeout)
        self.eastmoney = EastmoneyDataSource(timeout=timeout)
        self.sina = SinaDataSource(timeout=timeout)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        路由策略：新浪财经 (主) → AKShare(备)

        Args:
            symbol: 股票代码

        Returns:
            实时行情数据字典
        """
        # 优先使用新浪财经（快速、实时）
        result = self.sina.get_quote(symbol)
        if result:
            result['_source_used'] = 'sina'
            return result

        # 新浪财经失败，使用 AKShare 作为备选
        result = self.akshare.get_quote(symbol)
        if result:
            result['_source_used'] = 'akshare'
            return result

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
        获取历史 K 线数据

        路由策略：AKShare (唯一数据源)

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly)
            adjust: 复权类型 (qfq/hfq/none)

        Returns:
            pandas DataFrame with OHLCV data
        """
        result = self.akshare.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust
        )
        if result is not None and not result.empty:
            result['_source_used'] = 'akshare'
        return result

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        路由策略：东方财富 (主) → AKShare(备)

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典
        """
        # 优先使用东方财富
        result = self.eastmoney.get_stock_info(symbol)
        if result:
            result['_source_used'] = 'eastmoney'
            return result

        # 东方财富失败，使用 AKShare 作为备选
        result = self.akshare.get_stock_info(symbol)
        if result:
            result['_source_used'] = 'akshare'
            return result

        return None

    def get_fund_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取资金流向分析

        路由策略：AKShare (唯一数据源)

        Args:
            symbol: 股票代码

        Returns:
            资金流向数据
        """
        result = self.akshare.get_fund_flow(symbol)
        if result:
            result['_source_used'] = 'akshare'
        return result

    def get_sector_rank(self, sector_type: int = 1, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取板块排行

        路由策略：东方财富 (主) → AKShare(备)

        Args:
            sector_type: 1=行业板块，2=概念板块，3=地域板块
            limit: 返回数量

        Returns:
            板块排行数据
        """
        # 优先使用东方财富
        result = self.eastmoney.get_sector_rank(sector_type=sector_type, limit=limit)
        if result:
            result['_source_used'] = 'eastmoney'
            return result

        # 东方财富失败，使用 AKShare 作为备选
        result = self.akshare.get_sector_rank(sector_type=sector_type, limit=limit)
        if result:
            result['_source_used'] = 'akshare'
            return result

        return None

    def search_stock(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """
        搜索股票

        路由策略：优先数据库缓存 → AKShare(备)

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的股票列表
        """
        result = self.akshare.search_stock(keyword)
        return result

    def get_comprehensive_data(
        self,
        symbol: str,
        include_historical: bool = False,
        historical_days: int = 60
    ) -> Optional[UnifiedStockData]:
        """
        获取股票综合数据

        Args:
            symbol: 股票代码
            include_historical: 是否包含历史数据
            historical_days: 历史数据天数

        Returns:
            UnifiedStockData 对象
        """
        from datetime import datetime, timedelta

        result = UnifiedStockData()

        # 获取实时行情（新浪财经）
        quote_data = self.get_quote(symbol)
        if quote_data:
            result.quote = QuoteData.from_dict(quote_data)
            result.add_source(quote_data['_source_used'], 'quote')

        # 获取股票信息（东方财富）
        info_data = self.get_stock_info(symbol)
        if info_data:
            result.stock_info = StockInfo.from_dict(info_data)
            result.add_source(info_data['_source_used'], 'stock_info')

        # 获取资金流向（AKShare）
        flow_data = self.get_fund_flow(symbol)
        if flow_data:
            result.fund_flow = flow_data
            result.add_source('akshare', 'fund_flow')

        # 获取历史数据（可选）
        if include_historical:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=historical_days)).strftime('%Y%m%d')

            hist_data = self.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            if hist_data is not None:
                result.historical = hist_data
                result.add_source('akshare', 'historical')

        return result

    def get_quotes_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            行情数据列表
        """
        results = []
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                results.append(quote)
        return results

    def get_all_sector_ranks(
        self,
        limit: int = 20
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        获取所有板块排行

        Args:
            limit: 每个板块返回数量

        Returns:
            包含行业、概念、地域板块的字典
        """
        return {
            'industry': self.get_sector_rank(sector_type=1, limit=limit),
            'concept': self.get_sector_rank(sector_type=2, limit=limit),
            'region': self.get_sector_rank(sector_type=3, limit=limit),
        }


# 便捷实例
_default_service: Optional[UnifiedStockQueryService] = None


def get_default_service(db=None, timeout: int = 10) -> UnifiedStockQueryService:
    """获取默认服务实例"""
    global _default_service
    if _default_service is None:
        _default_service = UnifiedStockQueryService(db=db, timeout=timeout)
    return _default_service
