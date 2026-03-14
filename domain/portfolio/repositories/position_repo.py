"""
PositionRepository - 持仓数据访问对象
"""
from typing import Optional, List

from domain.portfolio.models.position import Position, PositionLot
from domain.portfolio.models.transaction import Transaction
from domain.portfolio.repositories.base import BaseRepository


class PositionRepository(BaseRepository):
    """Position 数据访问对象"""

    def get(self, stock_code: str) -> Optional[Position]:
        """获取单个持仓"""
        return self.session.query(Position).filter(
            Position.stock_code == stock_code
        ).first()

    def get_all(self, include_empty: bool = False) -> List[Position]:
        """
        获取所有持仓

        Args:
            include_empty: 是否包含持仓为 0 的记录

        Returns:
            持仓列表
        """
        query = self.session.query(Position)
        if not include_empty:
            query = query.filter(Position.quantity > 0)
        return query.order_by(Position.stock_code).all()

    def add(self, position: Position) -> Position:
        """添加持仓"""
        self.session.add(position)
        self.session.commit()
        self.session.refresh(position)
        return position

    def update(self, position: Position) -> Position:
        """更新持仓"""
        self.session.commit()
        self.session.refresh(position)
        return position

    def delete(self, position: Position):
        """删除持仓"""
        self.session.delete(position)
        self.session.commit()

    def add_lot(self, lot: PositionLot) -> PositionLot:
        """添加持仓批次"""
        self.session.add(lot)
        self.session.commit()
        self.session.refresh(lot)
        return lot

    def get_lots(self, stock_code: str) -> List[PositionLot]:
        """获取持仓批次（按日期升序，用于 FIFO）"""
        return self.session.query(PositionLot).filter(
            PositionLot.stock_code == stock_code,
            PositionLot.remaining_quantity > 0
        ).order_by(PositionLot.purchase_date.asc()).all()

    def update_lot(self, lot: PositionLot) -> PositionLot:
        """更新持仓批次"""
        self.session.commit()
        return lot
