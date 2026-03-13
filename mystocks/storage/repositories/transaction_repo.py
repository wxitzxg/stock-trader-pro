"""
TransactionRepository - 交易记录数据访问对象
"""
from typing import Optional, List

from mystocks.models.transaction import Transaction
from mystocks.storage.repositories.base import BaseRepository


class TransactionRepository(BaseRepository):
    """Transaction 数据访问对象"""

    def add(self, transaction: Transaction) -> Transaction:
        """添加交易记录"""
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def get_by_stock(self, stock_code: str, limit: int = 50) -> List[Transaction]:
        """
        获取单个股票的交易历史

        Args:
            stock_code: 股票代码
            limit: 返回数量限制

        Returns:
            交易记录列表
        """
        return self.session.query(Transaction).filter(
            Transaction.stock_code == stock_code
        ).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()

    def get_all(self, limit: int = 50) -> List[Transaction]:
        """
        获取所有交易历史

        Args:
            limit: 返回数量限制

        Returns:
            交易记录列表
        """
        return self.session.query(Transaction).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()
