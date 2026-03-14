#!/usr/bin/env python3
"""
我的股票 - 综合资产管理模块
整合持仓管理、收藏管理、数据存储三大功能

功能:
- 持仓管理：买入/卖出/查询/盈亏分析
- 收藏管理：添加/删除/标签/目标价
- 数据存储：交易记录/持仓批次/自动同步
- 资产分析：持仓集中度/风险敞口/收益统计
"""

from typing import Optional, List, Dict
import json
import csv

from domain.portfolio import Position, Watchlist, Transaction, PositionLot, Account
from domain.portfolio.repositories import Database
from domain.portfolio.services import PortfolioService, WatchlistService, AnalysisService, AccountService
from domain.portfolio.services.portfolio_service import InitMode


class MyStocks:
    """
    我的股票 - 综合资产管理（Facade 模式）

    整合持仓管理、收藏管理、数据存储三大功能
    """

    def __init__(self, db_path: str = None):
        """
        初始化我的股票管理器

        Args:
            db_path: 数据库文件路径
        """
        self._db = Database(db_path)
        self._db.init_db()
        self._session = self._db.get_session()

        # 组合服务层
        self._portfolio_service = PortfolioService(self._session)
        self._watchlist_service = WatchlistService(self._session)
        self._analysis_service = AnalysisService(self._session)
        self._account_service = AccountService(self._session)

    # ========== 持仓管理 API ==========

    def buy(
        self,
        stock_code: str,
        stock_name: str,
        quantity: int,
        price: float,
        commission: float = 0.0,
        notes: str = None,
        account_id: int = None
    ) -> Position:
        """
        买入股票

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            quantity: 股数
            price: 成交价
            commission: 手续费
            notes: 备注
            account_id: 账户 ID，为 None 时使用默认账户

        Returns:
            持仓对象
        """
        return self._portfolio_service.buy(
            stock_code=stock_code,
            stock_name=stock_name,
            quantity=quantity,
            price=price,
            commission=commission,
            notes=notes,
            account_id=account_id
        )

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        commission: float = 0.0,
        notes: str = None,
        account_id: int = None
    ) -> Optional[Position]:
        """
        卖出股票（FIFO 成本计算）

        Args:
            stock_code: 股票代码
            quantity: 卖出股数
            price: 成交价
            commission: 手续费
            notes: 备注
            account_id: 账户 ID，为 None 时使用默认账户

        Returns:
            更新后的持仓对象，或 None（清仓）
        """
        return self._portfolio_service.sell(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            commission=commission,
            notes=notes,
            account_id=account_id
        )

    def get_position(self, stock_code: str) -> Optional[Position]:
        """获取单个持仓"""
        return self._portfolio_service.get_position(stock_code)

    def get_all_positions(self) -> List[Position]:
        """获取所有持仓"""
        return self._portfolio_service.get_all_positions()

    def get_transactions(self, stock_code: str = None, limit: int = 50) -> List[Transaction]:
        """获取交易历史"""
        return self._portfolio_service.get_transactions(stock_code, limit)

    # ========== 收藏管理 API ==========

    def add_to_watchlist(
        self,
        stock_code: str,
        stock_name: str = None,
        tags: str = None,
        notes: str = None,
        target_price: float = None,
        stop_loss: float = None
    ) -> Watchlist:
        """添加收藏股"""
        return self._watchlist_service.add(
            stock_code=stock_code,
            stock_name=stock_name,
            tags=tags,
            notes=notes,
            target_price=target_price,
            stop_loss=stop_loss
        )

    def remove_from_watchlist(self, stock_code: str) -> bool:
        """删除收藏股"""
        return self._watchlist_service.remove(stock_code)

    def get_watchlist(self, tag: str = None) -> List[Watchlist]:
        """获取收藏股列表"""
        return self._watchlist_service.get_all(tag)

    def update_watchlist(
        self,
        stock_code: str,
        tags: str = None,
        notes: str = None,
        target_price: float = None,
        stop_loss: float = None
    ) -> Optional[Watchlist]:
        """更新收藏股信息"""
        return self._watchlist_service.update(
            stock_code=stock_code,
            tags=tags,
            notes=notes,
            target_price=target_price,
            stop_loss=stop_loss
        )

    # ========== 资产分析 API ==========

    def get_portfolio_summary(self) -> Dict:
        """获取持仓汇总"""
        return self._analysis_service.get_portfolio_summary()

    def get_concentration(self) -> Dict:
        """计算持仓集中度"""
        return self._analysis_service.get_concentration()

    def get_position_weights(self) -> Dict[str, float]:
        """计算各持仓权重"""
        return self._analysis_service.get_position_weights()

    def get_risk_exposure(self) -> Dict:
        """计算风险敞口"""
        return self._analysis_service.get_risk_exposure()

    # ========== 账户管理 API ==========

    def get_account_summary(self) -> Dict:
        """
        获取账户总览

        Returns:
            {
                "account_id": int,
                "account_name": str,
                "cash_balance": float,           # 当前现金
                "stock_market_value": float,     # 持仓总市值
                "total_account_value": float,    # 总资产 = 持仓市值 + 现金
                "position_ratio": float,         # 仓位比 = 持仓市值 / 总资产
                "floating_pnl": float,           # 浮动盈亏 (未实现)
                "floating_pnl_rate": float,      # 浮动盈亏比
                "realized_pnl": float,           # 已实现盈亏
                "total_pnl": float,              # 总盈亏 = 浮动 + 已实现
                "total_invested": float,         # 累计投入本金
            }
        """
        return self._account_service.get_account_summary()

    def get_holdings_with_details(self) -> List[Dict]:
        """
        获取持仓详情列表（含仓位比）

        Returns:
            [
                {
                    "stock_code": str,
                    "stock_name": str,
                    "quantity": int,
                    "current_price": float,
                    "market_value": float,         # 市值 = 现价 × 数量
                    "avg_cost": float,
                    "floating_pnl": float,         # 浮动盈亏
                    "floating_pnl_rate": float,    # 浮动盈亏比
                    "position_ratio": float,       # 仓位比 = 该持仓市值 / 总资产
                }
            ]
        """
        return self._account_service.get_holdings_with_details()

    def deposit(self, amount: float) -> Account:
        """
        存入现金

        Args:
            amount: 存入金额

        Returns:
            更新后的账户对象
        """
        return self._account_service.deposit(amount)

    def withdraw(self, amount: float) -> Account:
        """
        取出现金

        Args:
            amount: 取出金额

        Returns:
            更新后的账户对象
        """
        return self._account_service.withdraw(amount)

    # ========== 工具方法 ==========

    def calculate_commission(self, amount: float, operation: str = "buy") -> float:
        """计算交易手续费"""
        return self._portfolio_service.calculate_commission(amount, operation)

    def initialize_position(
        self,
        stock_code: str,
        quantity: int,
        avg_cost: float,
        current_price: float = None,
        stock_name: str = None,
        total_cost: float = None,
        purchase_date: str = None,
        mode: str = "overwrite",
        notes: str = None
    ) -> Position:
        """
        初始化持仓（用于首次导入已有持仓）

        Args:
            stock_code: 股票代码（必需）
            quantity: 持仓数量（必需）
            avg_cost: 成本价，可为负数，精度为 4 位小数（必需）
            current_price: 当前价，为 None 时自动从 API 获取（可选）
            stock_name: 股票名称，为 None 时自动从 API 获取（可选）
            total_cost: 总成本（可选）
            purchase_date: 建仓日期（可选，格式：YYYY-MM-DD）
            mode: 模式（overwrite=覆盖，add=累加）
            notes: 备注

        Returns:
            创建的持仓对象

        股票信息获取逻辑：
            - 当 current_price 或 stock_name 为 None 时
            - 调用 UnifiedStockQueryService.get_quote(stock_code) 获取
            - 数据源优先级：新浪财经 → AKShare（备用）
        """
        init_mode = InitMode.OVERWRITE if mode == "overwrite" else InitMode.ADD
        return self._portfolio_service.initialize_position(
            stock_code=stock_code,
            quantity=quantity,
            avg_cost=avg_cost,
            current_price=current_price,
            stock_name=stock_name,
            total_cost=total_cost,
            purchase_date=purchase_date,
            mode=init_mode,
            notes=notes
        )

    def initialize_positions_from_file(
        self,
        file_path: str,
        file_format: str = "json",
        mode: str = "overwrite"
    ) -> List[Position]:
        """
        从文件导入持仓

        Args:
            file_path: 文件路径
            file_format: 文件格式（json/csv）
            mode: 模式（overwrite=覆盖，add=累加）

        Returns:
            List[Position]: 创建的持仓列表
        """
        init_mode = InitMode.OVERWRITE if mode == "overwrite" else InitMode.ADD

        # 读取文件
        if file_format.lower() == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                positions_data = json.load(f)
        elif file_format.lower() == "csv":
            positions_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 转换 CSV 字符串为适当类型
                    row_data = {
                        "stock_code": row.get("stock_code"),
                        "stock_name": row.get("stock_name"),
                        "quantity": int(row.get("quantity", 0)),
                        "avg_cost": float(row.get("avg_cost", 0)),
                        "current_price": float(row.get("current_price", row.get("avg_cost", 0))),
                        "purchase_date": row.get("purchase_date"),
                        "notes": row.get("notes")
                    }
                    if "total_cost" in row:
                        row_data["total_cost"] = float(row.get("total_cost", 0))
                    positions_data.append(row_data)
        else:
            raise ValueError(f"不支持的文件格式：{file_format}")

        return self._portfolio_service.initialize_positions_batch(positions_data, init_mode)

    def sync_prices(self, price_fetcher):
        """
        同步最新股价

        Args:
            price_fetcher: 价格获取函数，接收 stock_code 返回 price
        """
        positions = self.get_all_positions()
        for position in positions:
            try:
                price = price_fetcher(position.stock_code)
                if price and price > 0:
                    position.current_price = price
                    # 负成本盈亏计算
                    if position.avg_cost < 0:
                        position.profit_loss = (abs(position.avg_cost) + price) * position.quantity
                        position.profit_rate = None  # 负成本时盈亏率无意义
                    else:
                        position.profit_loss = (price - position.avg_cost) * position.quantity
                        position.profit_rate = ((price - position.avg_cost) / position.avg_cost * 100) if position.avg_cost > 0 else 0
            except Exception as e:
                pass
        self._session.commit()

    def export_data(self, format: str = "dict") -> Dict:
        """导出数据"""
        positions = self.get_all_positions()
        watchlist = self.get_watchlist()
        transactions = self.get_transactions(limit=100)

        return {
            "positions": [
                {
                    "stock_code": p.stock_code,
                    "stock_name": p.stock_name,
                    "quantity": p.quantity,
                    "avg_cost": p.avg_cost,
                    "current_price": p.current_price,
                    "profit_loss": p.profit_loss,
                    "realized_profit": p.realized_profit
                }
                for p in positions
            ],
            "watchlist": [
                {
                    "stock_code": w.stock_code,
                    "stock_name": w.stock_name,
                    "tags": w.tags,
                    "target_price": w.target_price,
                    "stop_loss": w.stop_loss
                }
                for w in watchlist
            ],
            "recent_transactions": [
                {
                    "stock_code": t.stock_code,
                    "operation": t.operation,
                    "quantity": t.quantity,
                    "price": t.price,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in transactions
            ]
        }

    def close(self):
        """关闭会话"""
        self._session.close()
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


__all__ = [
    'MyStocks',
    'Account',
    'Position',
    'PositionLot',
    'Transaction',
    'Watchlist',
]
