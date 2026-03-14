"""
Transaction 模型 - 交易记录表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from domain.portfolio.models.base import Base


class Transaction(Base):
    """交易记录表"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(50))
    operation = Column(String(10), nullable=False)  # buy/sell
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # 总金额
    commission = Column(Float, default=0.0)       # 手续费
    realized_pnl = Column(Float, default=0.0)     # 该笔交易实现盈亏
    notes = Column(Text)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # 外键关联持仓
    position_id = Column(Integer, ForeignKey("positions.id"))
    lot_id = Column(Integer, ForeignKey("position_lots.id"))  # 关联批次 ID（卖出时）
    position = relationship("Position", back_populates="transactions")
    lot = relationship("PositionLot", backref="transactions")

    def __repr__(self):
        return f"<Transaction {self.operation} {self.stock_code} @{self.price}>"
