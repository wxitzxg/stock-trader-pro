"""
Account 模型 - 账号表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

from domain.portfolio.models.base import Base


class Account(Base):
    """账号表 - 管理现金余额和累计盈亏"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), default="默认账户", nullable=False)  # 账户名称
    cash_balance = Column(Float, default=0.0, nullable=False)  # 当前现金余额
    total_invested = Column(Float, default=0.0, nullable=False)  # 累计投入本金
    total_realized_pnl = Column(Float, default=0.0, nullable=False)  # 累计已实现盈亏
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认账户
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Account {self.name} cash={self.cash_balance} invested={self.total_invested}>"

    @property
    def total_account_value(self) -> float:
        """总资产 = 现金 + 已实现盈亏（持仓市值在外部计算）"""
        return self.cash_balance + self.total_realized_pnl

    def deposit(self, amount: float) -> float:
        """
        存入现金
        :param amount: 存入金额
        :return: 新的现金余额
        """
        if amount <= 0:
            raise ValueError("存入金额必须大于 0")
        self.cash_balance += amount
        self.total_invested += amount
        return self.cash_balance

    def withdraw(self, amount: float) -> float:
        """
        取出现金
        :param amount: 取出金额
        :return: 新的现金余额
        """
        if amount <= 0:
            raise ValueError("取出金额必须大于 0")
        if amount > self.cash_balance:
            raise ValueError(f"现金余额不足：当前余额={self.cash_balance}, 请求取出={amount}")
        self.cash_balance -= amount
        return self.cash_balance

    def add_realized_pnl(self, amount: float) -> float:
        """
        添加已实现盈亏
        :param amount: 盈亏金额（正数为盈利，负数为亏损）
        :return: 新的累计已实现盈亏
        """
        self.total_realized_pnl += amount
        return self.total_realized_pnl

    def credit_cash(self, amount: float) -> float:
        """
        增加现金（不改变投入本金，用于卖出所得）
        :param amount: 增加金额
        :return: 新的现金余额
        """
        if amount <= 0:
            raise ValueError("增加金额必须大于 0")
        self.cash_balance += amount
        return self.cash_balance
