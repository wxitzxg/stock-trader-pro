"""
Position 模型 - 持仓表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from mystocks.models.base import Base


class Position(Base):
    """持仓表"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), unique=True, nullable=False, index=True)
    stock_name = Column(String(50))
    quantity = Column(Integer, default=0)
    avg_cost = Column(Float, default=0.0)  # 支持负数（负成本）
    current_price = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)       # 浮动盈亏（未实现）
    profit_rate = Column(Float, nullable=True, default=0.0)  # 盈亏率（负成本时为 NULL）
    realized_profit = Column(Float, default=0.0)   # 已实现盈亏
    total_cost = Column(Float, default=0.0)        # 累计投入成本（含手续费）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联交易记录
    transactions = relationship("Transaction", back_populates="position", cascade="all, delete-orphan")
    # 关联持仓批次
    lots = relationship("PositionLot", back_populates="position", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Position {self.stock_code} qty={self.quantity} cost={self.avg_cost}>"


class PositionLot(Base):
    """持仓批次表 - 支持分批建仓追踪（FIFO 成本计算）"""
    __tablename__ = "position_lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    stock_code = Column(String(20), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)           # 买入股数
    cost_price = Column(Float, nullable=False)           # 买入单价
    commission = Column(Float, default=0.0)              # 手续费
    total_cost = Column(Float, nullable=False)           # 总成本（含手续费）
    purchase_date = Column(DateTime, default=datetime.now)
    remaining_quantity = Column(Integer, nullable=False) # 剩余股数（用于卖出扣减）

    # 关联持仓
    position = relationship("Position", back_populates="lots")

    def __repr__(self):
        return f"<PositionLot {self.stock_code} qty={self.quantity} remaining={self.remaining_quantity}>"
