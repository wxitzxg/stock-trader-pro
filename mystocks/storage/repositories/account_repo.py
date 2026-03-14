"""
AccountRepository - 账户数据访问对象
"""
from typing import Optional, List
from datetime import datetime

from mystocks.models.account import Account
from mystocks.storage.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    """Account 数据访问对象"""

    def get(self, account_id: int) -> Optional[Account]:
        """获取单个账户"""
        return self.session.query(Account).filter(
            Account.id == account_id
        ).first()

    def get_default(self) -> Optional[Account]:
        """获取默认账户"""
        return self.session.query(Account).filter(
            Account.is_default == True
        ).first()

    def get_all(self) -> List[Account]:
        """获取所有账户"""
        return self.session.query(Account).order_by(Account.id).all()

    def add(self, account: Account) -> Account:
        """添加账户"""
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def update(self, account: Account) -> Account:
        """更新账户"""
        self.session.commit()
        self.session.refresh(account)
        return account

    def delete(self, account_id: int):
        """删除账户"""
        account = self.get(account_id)
        if account:
            self.session.delete(account)
            self.session.commit()
