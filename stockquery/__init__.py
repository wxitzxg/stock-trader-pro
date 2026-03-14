"""
股票查询模块 - 兼容层（导出到 infrastructure）
"""
from infrastructure.models.quote_data import (
    QuoteData,
    StockInfo,
    FundFlowSummary,
    SectorData,
    UnifiedStockData,
)
from infrastructure.sources.base import BaseDataSource
from infrastructure.sources.akshare_source import AKShareDataSource
from infrastructure.sources.sina_source import SinaDataSource
from infrastructure.sources.eastmoney_source import EastmoneyDataSource
from infrastructure.unified_service import (
    UnifiedStockQueryService,
    get_default_service,
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
