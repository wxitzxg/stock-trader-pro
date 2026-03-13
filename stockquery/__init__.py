"""
股票查询模块
整合 AKShare、东方财富、新浪财经三个数据源
"""
from stockquery.unified_service import (
    UnifiedStockQueryService,
    get_default_service,
)
from stockquery.models import (
    QuoteData,
    StockInfo,
    FundFlowSummary,
    SectorData,
    UnifiedStockData,
)
from stockquery.sources import (
    BaseDataSource,
    AKShareDataSource,
    SinaDataSource,
    EastmoneyDataSource,
)

__all__ = [
    # 统一服务
    'UnifiedStockQueryService',
    'get_default_service',
    # 数据模型
    'QuoteData',
    'StockInfo',
    'FundFlowSummary',
    'SectorData',
    'UnifiedStockData',
    # 数据源
    'BaseDataSource',
    'AKShareDataSource',
    'SinaDataSource',
    'EastmoneyDataSource',
]
