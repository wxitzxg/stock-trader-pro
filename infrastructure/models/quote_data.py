"""
统一数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class QuoteData:
    """实时行情数据"""
    source: str = ""
    code: str = ""
    symbol: str = ""
    name: str = ""
    price: float = 0.0
    change: float = 0.0  # 涨跌额
    change_percent: float = 0.0  # 涨跌幅
    change_amount: float = 0.0  # 涨跌额
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: int = 0
    amount: float = 0.0
    market: str = ""
    date: str = ""
    time: str = ""
    prev_close: float = 0.0  # 昨收价

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['QuoteData']:
        """从字典创建"""
        if not data:
            return None
        return cls(
            source=data.get('source', ''),
            code=data.get('code', ''),
            symbol=data.get('symbol', data.get('code', '')),
            name=data.get('name', ''),
            price=float(data.get('price', 0)),
            change=float(data.get('change', 0)),
            change_percent=float(data.get('change_percent', 0)),
            change_amount=float(data.get('change_amount', data.get('change', 0))),
            open=float(data.get('open', 0)),
            high=float(data.get('high', 0)),
            low=float(data.get('low', 0)),
            volume=int(data.get('volume', 0)),
            amount=float(data.get('amount', 0)),
            market=data.get('market', ''),
            date=data.get('date', ''),
            time=data.get('time', ''),
            prev_close=float(data.get('prev_close', 0)),
        )


@dataclass
class StockInfo:
    """股票基本信息"""
    source: str = ""
    symbol: str = ""
    name: str = ""
    market: str = ""
    industry: str = ""
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    market_cap: float = 0.0
    float_cap: float = 0.0
    total_shares: float = 0.0
    float_shares: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['StockInfo']:
        """从字典创建"""
        if not data:
            return None
        return cls(
            source=data.get('source', ''),
            symbol=data.get('symbol', ''),
            name=data.get('name', ''),
            market=data.get('market', ''),
            industry=data.get('industry', ''),
            pe_ratio=float(data.get('pe_ratio', 0)),
            pb_ratio=float(data.get('pb_ratio', 0)),
            market_cap=float(data.get('market_cap', 0)),
            float_cap=float(data.get('float_cap', 0)),
            total_shares=float(data.get('total_shares', 0)),
            float_shares=float(data.get('float_shares', 0)),
        )


@dataclass
class FundFlowSummary:
    """资金流向摘要"""
    date: str = ""
    main_force_in: float = 0.0
    big_order_in: float = 0.0
    medium_order_in: float = 0.0
    small_order_in: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['FundFlowSummary']:
        """从字典创建"""
        if not data:
            return None
        return cls(
            date=data.get('date', ''),
            main_force_in=float(data.get('main_force_in', 0)),
            big_order_in=float(data.get('big_order_in', 0)),
            medium_order_in=float(data.get('medium_order_in', 0)),
            small_order_in=float(data.get('small_order_in', 0)),
        )


@dataclass
class SectorData:
    """板块数据"""
    code: str = ""
    name: str = ""
    current: float = 0.0
    change_percent: float = 0.0
    change: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    turnover: float = 0.0
    pe: float = 0.0
    amplitude: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['SectorData']:
        """从字典创建"""
        if not data:
            return None
        return cls(
            code=data.get('code', ''),
            name=data.get('name', ''),
            current=float(data.get('current', 0)),
            change_percent=float(data.get('change_percent', 0)),
            change=float(data.get('change', 0)),
            open=float(data.get('open', 0)),
            high=float(data.get('high', 0)),
            low=float(data.get('low', 0)),
            volume=float(data.get('volume', 0)),
            amount=float(data.get('amount', 0)),
            turnover=float(data.get('turnover', 0)),
            pe=float(data.get('pe', 0)),
            amplitude=float(data.get('amplitude', 0)),
        )


@dataclass
class UnifiedStockData:
    """统一股票数据 - 整合所有数据源的信息"""
    quote: Optional[QuoteData] = None
    stock_info: Optional[StockInfo] = None
    historical: Optional[pd.DataFrame] = None
    fund_flow: Optional[Dict[str, Any]] = None
    sector_rank: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_source(self, source_name: str, data_type: str):
        """记录数据来源"""
        if 'sources' not in self.metadata:
            self.metadata['sources'] = {}
        self.metadata['sources'][data_type] = source_name
