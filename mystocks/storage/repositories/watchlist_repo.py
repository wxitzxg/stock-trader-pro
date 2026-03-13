"""
WatchlistRepository - 收藏股数据访问对象
"""
from typing import Optional, List

from mystocks.models.watchlist import Watchlist
from mystocks.storage.repositories.base import BaseRepository


class WatchlistRepository(BaseRepository):
    """Watchlist 数据访问对象"""

    def get(self, stock_code: str) -> Optional[Watchlist]:
        """获取单个收藏股"""
        return self.session.query(Watchlist).filter(
            Watchlist.stock_code == stock_code
        ).first()

    def get_all(self, tag: str = None) -> List[Watchlist]:
        """
        获取所有收藏股

        Args:
            tag: 按标签筛选（可选）

        Returns:
            收藏股列表
        """
        query = self.session.query(Watchlist).order_by(Watchlist.created_at.desc())

        if tag:
            query = query.filter(Watchlist.tags.like(f"%{tag}%"))

        return query.all()

    def add(self, watchlist: Watchlist) -> Watchlist:
        """添加收藏股"""
        self.session.add(watchlist)
        self.session.commit()
        self.session.refresh(watchlist)
        return watchlist

    def update(self, watchlist: Watchlist) -> Watchlist:
        """更新收藏股"""
        self.session.commit()
        self.session.refresh(watchlist)
        return watchlist

    def delete(self, stock_code: str) -> bool:
        """
        删除收藏股

        Args:
            stock_code: 股票代码

        Returns:
            是否删除成功
        """
        item = self.get(stock_code)
        if item:
            self.session.delete(item)
            self.session.commit()
            return True
        return False
