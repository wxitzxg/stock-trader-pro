"""
Kline 模型 - K 线数据表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Index

from models.base import Base


class Kline(Base):
    """K 线数据表 - 结构化存储"""
    __tablename__ = "klines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)   # 股票代码
    date = Column(String(10), nullable=False)                     # 交易日期 YYYYMMDD
    period = Column(String(10), nullable=False, default='daily')  # 周期 daily/weekly/monthly
    adjust = Column(String(10), nullable=False, default='qfq')    # 复权 qfq/hfq/none

    # K 线数据字段
    open = Column(Float, nullable=False)       # 开盘价
    high = Column(Float, nullable=False)       # 最高价
    low = Column(Float, nullable=False)        # 最低价
    close = Column(Float, nullable=False)      # 收盘价
    volume = Column(Float, nullable=False)     # 成交量
    amount = Column(Float, nullable=True)      # 成交额
    amplitude = Column(Float, nullable=True)   # 振幅
    pct_change = Column(Float, nullable=True)  # 涨跌幅
    change = Column(Float, nullable=True)      # 涨跌额
    turnover = Column(Float, nullable=True)    # 换手率

    # 数据来源和更新时间
    source = Column(String(20), default='akshare')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 唯一约束：同一股票 + 日期 + 周期 + 复权类型只保留一条
    __table_args__ = (
        UniqueConstraint('stock_code', 'date', 'period', 'adjust',
                        name='uq_kline_unique'),
        Index('idx_kline_code_period_adjust', 'stock_code', 'period', 'adjust'),
    )

    def __repr__(self):
        return f"<Kline {self.stock_code} {self.date} {self.period} {self.adjust}>"
