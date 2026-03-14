"""
StockListRepository - A 股股票列表数据访问对象
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from mystocks.models.stock_list import StockList
from mystocks.storage.repositories.base import BaseRepository


class StockListRepository(BaseRepository):
    """StockList 数据访问对象"""

    def get(self, code: str) -> Optional[StockList]:
        """获取单只股票"""
        return self.session.query(StockList).filter(
            StockList.code == code
        ).first()

    def get_all(self) -> List[StockList]:
        """获取全部股票"""
        return self.session.query(StockList).order_by(StockList.code).all()

    def get_count(self) -> int:
        """获取股票总数"""
        return self.session.query(StockList).count()

    def search(self, keyword: str, limit: int = 20) -> List[StockList]:
        """
        模糊搜索股票（代码或名称）

        Args:
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的股票列表
        """
        # 模糊匹配代码或名称
        results = self.session.query(StockList).filter(
            (StockList.code.like(f"%{keyword}%")) |
            (StockList.name.like(f"%{keyword}%"))
        ).order_by(StockList.code).limit(limit).all()

        return results

    def upsert(self, data: Dict[str, Any]) -> StockList:
        """
        插入或更新单只股票

        Args:
            data: 股票数据字典，包含 code, name 等字段

        Returns:
            插入或更新后的 StockList 对象
        """
        existing = self.get(data['code'])

        if existing:
            # 更新现有记录
            existing.name = data.get('name', existing.name)
            existing.latest_price = data.get('latest_price')
            existing.change_pct = data.get('change_pct')
            existing.volume = data.get('volume')
            existing.amount = data.get('amount')
            existing.market_cap = data.get('market_cap')
            existing.pe_ratio = data.get('pe_ratio')
            existing.industry = data.get('industry')
            existing.updated_at = datetime.now()
            return existing
        else:
            # 插入新记录
            stock = StockList(
                code=data['code'],
                name=data.get('name', ''),
                latest_price=data.get('latest_price'),
                change_pct=data.get('change_pct'),
                volume=data.get('volume'),
                amount=data.get('amount'),
                market_cap=data.get('market_cap'),
                pe_ratio=data.get('pe_ratio'),
                industry=data.get('industry')
            )
            self.session.add(stock)
            return stock

    def batch_upsert(self, data_list: List[Dict[str, Any]]) -> int:
        """
        批量插入或更新股票数据

        Args:
            data_list: 股票数据列表

        Returns:
            处理的股票数量
        """
        count = 0
        for data in data_list:
            self.upsert(data)
            count += 1

        self.session.commit()
        return count

    def get_latest_update_time(self) -> Optional[datetime]:
        """获取最后更新时间"""
        latest = self.session.query(StockList.updated_at).order_by(
            StockList.updated_at.desc()
        ).first()
        return latest[0] if latest else None

    def delete_all(self):
        """删除所有股票数据"""
        self.session.query(StockList).delete()
        self.session.commit()

    def delete_by_code(self, code: str) -> bool:
        """
        删除指定股票

        Args:
            code: 股票代码

        Returns:
            是否删除成功
        """
        stock = self.get(code)
        if stock:
            self.session.delete(stock)
            self.session.commit()
            return True
        return False