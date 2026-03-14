"""
AccountService - 账户服务
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session

from mystocks.storage.repositories.account_repo import AccountRepository
from mystocks.models.account import Account


class AccountService:
    """账户服务"""

    def __init__(self, session: Session):
        """
        初始化账户服务

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.account_repo = AccountRepository(session)

    def get_account_summary(self, account_id: int = None) -> Dict:
        """
        获取账户总览

        Args:
            account_id: 账户 ID，为 None 时使用默认账户

        Returns:
            账户总览字典
        """
        if account_id is None:
            account = self.account_repo.get_default()
        else:
            account = self.account_repo.get(account_id)

        if not account:
            return {
                "account_id": None,
                "account_name": "默认账户",
                "cash_balance": 0,
                "stock_market_value": 0,
                "total_account_value": 0,
                "position_ratio": 0,
                "floating_pnl": 0,
                "floating_pnl_rate": 0,
                "realized_pnl": 0,
                "total_pnl": 0,
                "total_invested": 0,
            }

        return {
            "account_id": account.id,
            "account_name": account.name,
            "cash_balance": account.cash_balance,
            "stock_market_value": 0,  # 需要计算持仓市值
            "total_account_value": account.cash_balance,
            "position_ratio": 0,
            "floating_pnl": 0,
            "floating_pnl_rate": 0,
            "realized_pnl": 0,
            "total_pnl": 0,
            "total_invested": account.total_invested,
        }

    def get_holdings_with_details(self) -> list:
        """获取持仓详情列表"""
        return []

    def deposit(self, amount: float) -> Account:
        """
        存入现金

        Args:
            amount: 存入金额

        Returns:
            更新后的账户对象
        """
        account = self.account_repo.get_default()
        if not account:
            # 创建默认账户
            account = Account(
                name="默认账户",
                cash_balance=amount,
                total_invested=amount,
                is_default=True
            )
            return self.account_repo.add(account)

        account.cash_balance += amount
        account.total_invested += amount
        return self.account_repo.update(account)

    def withdraw(self, amount: float) -> Account:
        """
        取出现金

        Args:
            amount: 取出金额

        Returns:
            更新后的账户对象
        """
        account = self.account_repo.get_default()
        if not account:
            raise ValueError("账户不存在")

        if account.cash_balance < amount:
            raise ValueError("余额不足")

        account.cash_balance -= amount
        return self.account_repo.update(account)
