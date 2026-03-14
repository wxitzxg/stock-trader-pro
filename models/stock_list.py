"""
StockList 模型 - A 股股票列表缓存表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index

from models.base import Base


class StockList(Base):
    """A 股股票列表缓存表"""
    __tablename__ = "stock_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False)           # 股票代码
    name = Column(String(50), nullable=False)           # 股票名称
    latest_price = Column(Float, nullable=True)         # 最新价
    change_pct = Column(Float, nullable=True)           # 涨跌幅
    volume = Column(Float, nullable=True)               # 成交量
    amount = Column(Float, nullable=True)               # 成交额
    market_cap = Column(Float, nullable=True)           # 总市值
    pe_ratio = Column(Float, nullable=True)             # 市盈率
    industry = Column(String(100), nullable=True)       # 所属行业

    # 更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 索引：支持代码和名称模糊搜索
    __table_args__ = (
        Index('idx_stock_list_code', 'code'),
        Index('idx_stock_list_name', 'name'),
    )

    def __repr__(self):
        return f"<StockList {self.code} {self.name}>"
