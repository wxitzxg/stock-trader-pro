"""
WatchlistService - 收藏业务逻辑
"""
from typing import Optional, List

from domain.portfolio.models.watchlist import Watchlist
from domain.portfolio.repositories.watchlist_repo import WatchlistRepository


class WatchlistService:
    """收藏业务逻辑"""

    def __init__(self, session):
        """
        初始化收藏服务

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self._watchlist_repo = WatchlistRepository(session)

    def add(
        self,
        stock_code: str,
        stock_name: str = None,
        tags: str = None,
        notes: str = None,
        target_price: float = None,
        stop_loss: float = None
    ) -> Watchlist:
        """
        添加收藏股

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            tags: 标签（逗号分隔）
            notes: 备注
            target_price: 目标价
            stop_loss: 止损价

        Returns:
            收藏股对象
        """
        # 检查是否已存在
        existing = self._watchlist_repo.get(stock_code)

        if existing:
            return existing

        watchlist_item = Watchlist(
            stock_code=stock_code,
            stock_name=stock_name or "",
            tags=tags or "",
            notes=notes or "",
            target_price=target_price,
            stop_loss=stop_loss
        )
        return self._watchlist_repo.add(watchlist_item)

    def remove(self, stock_code: str) -> bool:
        """
        删除收藏股

        Args:
            stock_code: 股票代码

        Returns:
            是否删除成功
        """
        return self._watchlist_repo.delete(stock_code)

    def get_stock(self, stock_code: str) -> Optional[Watchlist]:
        """获取单个收藏股"""
        return self._watchlist_repo.get(stock_code)

    def get_all(self, tag: str = None) -> List[Watchlist]:
        """
        获取所有收藏股

        Args:
            tag: 按标签筛选（可选）

        Returns:
            收藏股列表
        """
        return self._watchlist_repo.get_all(tag)

    def update(
        self,
        stock_code: str,
        tags: str = None,
        notes: str = None,
        target_price: float = None,
        stop_loss: float = None
    ) -> Optional[Watchlist]:
        """
        更新收藏股信息

        Args:
            stock_code: 股票代码
            tags: 标签
            notes: 备注
            target_price: 目标价
            stop_loss: 止损价

        Returns:
            更新后的收藏股对象，或 None
        """
        item = self._watchlist_repo.get(stock_code)

        if not item:
            return None

        if tags is not None:
            item.tags = tags
        if notes is not None:
            item.notes = notes
        if target_price is not None:
            item.target_price = target_price
        if stop_loss is not None:
            item.stop_loss = stop_loss

        return self._watchlist_repo.update(item)
