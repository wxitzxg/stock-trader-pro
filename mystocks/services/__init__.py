"""
Services - 业务层导出
"""
from typing import Optional
from mystocks.services.portfolio_service import PortfolioService
from mystocks.services.watchlist_service import WatchlistService
from mystocks.services.analysis_service import AnalysisService
from mystocks.services.price_update_service import PriceUpdateService
from mystocks.storage.database import get_db

__all__ = [
    'PortfolioService',
    'WatchlistService',
    'AnalysisService',
    'PriceUpdateService',
    # Compatibility functions
    'get_stock_quote',
    'format_stock_info',
    'export_kline_data',
    'get_sector_rank',
    'format_sector_report',
    'get_fund_flow',
    'search_stock',
    'get_historical_kline',
    'WatchlistManager',
]


# ========== Compatibility Layer for old commands ==========
try:
    from stockquery import UnifiedStockQueryService
    _service = UnifiedStockQueryService()
except Exception:
    _service = None


def get_stock_quote(symbol: str):
    """获取股票实时行情（兼容旧版 API）"""
    if _service:
        return _service.get_quote(symbol)
    return {"error": "Service not available"}


def format_stock_info(quote: dict) -> str:
    """格式化股票信息（兼容旧版 API）"""
    if not quote or 'error' in quote:
        return "数据获取失败"

    name = quote.get('name', 'Unknown')
    code = quote.get('symbol', quote.get('code', 'N/A'))
    price = quote.get('price', 0)
    change_pct = quote.get('change_pct', 0)

    # 中国习惯：红涨绿跌
    if change_pct > 0:
        color = "🔴"
        sign = "+"
    elif change_pct < 0:
        color = "🟢"
        sign = ""
    else:
        color = "⚪"
        sign = ""

    return f"{color} {name} ({code})\n" \
           f"  当前价：¥{price:.2f} ({sign}{change_pct:.2f}%)\n" \
           f"  今开：¥{quote.get('open', 'N/A')}\n" \
           f"  最高：¥{quote.get('high', 'N/A')}\n" \
           f"  最低：¥{quote.get('low', 'N/A')}\n" \
           f"  昨收：¥{quote.get('prev_close', 'N/A')}\n" \
           f"  成交量：{quote.get('volume', 0):,}"


def get_historical_kline(symbol: str, days: int = 60):
    """获取历史 K 线数据（兼容旧版 API）"""
    if _service:
        return _service.get_historical_data(symbol, days=days)
    return None


def export_kline_data(df, output: str, format: str = 'csv'):
    """导出 K 线数据（兼容旧版 API）"""
    if df is None:
        return
    if format == 'csv':
        df.to_csv(output, index=False)
    print(f"已导出数据到：{output}")


def get_sector_rank(sector_type: str = 'industry', limit: int = 50):
    """获取板块排行（兼容旧版 API）"""
    if _service:
        return _service.get_sector_rank(sector_type=sector_type, limit=limit)
    return {"error": "Service not available"}


def format_sector_report(sector_data: dict, limit: int = 50) -> str:
    """格式化板块报告（兼容旧版 API）"""
    if not sector_data or 'error' in sector_data:
        return "数据获取失败"

    name = sector_data.get('name', 'Unknown')
    change_pct = sector_data.get('change_pct', 0)

    if change_pct > 0:
        color = "🔴"
        sign = "+"
    elif change_pct < 0:
        color = "🟢"
        sign = ""
    else:
        color = "⚪"
        sign = ""

    return f"{color} {name}\n" \
           f"  涨跌幅：{sign}{change_pct:.2f}%\n" \
           f"  上涨：{sector_data.get('up_count', 0)}\n" \
           f"  下跌：{sector_data.get('down_count', 0)}\n" \
           f"  领涨股：{sector_data.get('top_stock', 'N/A')}"


def get_fund_flow(symbol: str):
    """获取资金流向（兼容旧版 API）"""
    if _service:
        return _service.get_fund_flow(symbol)
    return {"error": "Service not available"}


def search_stock(keyword: str):
    """搜索股票（兼容旧版 API）"""
    if _service:
        return _service.search_stock(keyword)
    return []


# WatchlistManager compatibility
from sqlalchemy.orm import Session
try:
    from mystocks.models.watchlist import Watchlist

    class WatchlistManager:
        """收藏股管理器（兼容旧版 API）"""

        def __init__(self, session: Session):
            self.session = session

        def get_all(self):
            """获取所有收藏股"""
            return self.session.query(Watchlist).all()
except Exception:
    WatchlistManager = None
