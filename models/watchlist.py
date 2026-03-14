"""
Watchlist 模型 - 收藏股表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text

from models.base import Base


class Watchlist(Base):
    """收藏股表"""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), unique=True, nullable=False, index=True)
    stock_name = Column(String(50))
    tags = Column(String(200))  # 逗号分隔的标签
    notes = Column(Text)
    target_price = Column(Float)  # 目标价
    stop_loss = Column(Float)     # 止损价
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Watchlist {self.stock_code} {self.stock_name}>"
