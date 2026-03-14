"""
持仓价格更新服务
定时更新持仓股的现价和盈亏计算
"""

from typing import Dict, List, Optional
from datetime import datetime

from domain.portfolio.models.position import Position
from domain.portfolio.repositories.position_repo import PositionRepository
from common.trading_time import TradingTimeUtils
from infrastructure.unified_service import get_default_service


class PriceUpdateService:
    """
    持仓价格更新服务

    功能:
    - 批量更新所有持仓股的现价
    - 自动重新计算盈亏（支持负成本）
    - 只在交易时间执行更新
    """

    def __init__(self, session):
        """
        初始化价格更新服务

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self._position_repo = PositionRepository(session)
        self._stock_service = None

    def _get_stock_service(self):
        """懒加载股票查询服务"""
        if self._stock_service is None:
            self._stock_service = get_default_service(timeout=10)
        return self._stock_service

    def should_update_now(self) -> bool:
        """
        判断当前是否应该更新价格

        Returns:
            bool: 是否是交易时间
        """
        result = TradingTimeUtils.is_trading_time()
        return result["is_trading"]

    def get_update_skip_reason(self) -> str:
        """
        获取跳过更新的原因

        Returns:
            str: 原因说明
        """
        result = TradingTimeUtils.is_trading_time()
        return result["reason"]

    def update_single_position_price(self, stock_code: str) -> Optional[Dict]:
        """
        更新单只持仓的价格

        Args:
            stock_code: 股票代码

        Returns:
            更新结果字典，失败返回 None
        """
        position = self._position_repo.get(stock_code)
        if not position:
            return {"success": False, "reason": "持仓不存在"}

        try:
            stock_service = self._get_stock_service()
            quote = stock_service.get_quote(stock_code)

            if not quote or 'error' in quote:
                return {
                    "success": False,
                    "reason": "获取行情失败",
                    "stock_code": stock_code
                }

            price = quote.get('price', 0)
            if price <= 0:
                return {
                    "success": False,
                    "reason": "价格无效",
                    "stock_code": stock_code
                }

            # 更新价格
            old_price = position.current_price
            position.current_price = price

            # 重新计算盈亏
            self._calculate_and_update_profit_loss(position, price)

            self.session.commit()

            return {
                "success": True,
                "stock_code": stock_code,
                "old_price": old_price,
                "new_price": price,
                "profit_loss": position.profit_loss,
                "profit_rate": position.profit_rate
            }

        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "reason": f"更新失败：{str(e)}",
                "stock_code": stock_code
            }

    def update_all_positions_prices(self) -> Dict:
        """
        批量更新所有持仓价格

        Returns:
            更新结果统计
        """
        # 先判断是否交易时间
        if not self.should_update_now():
            return {
                "success": False,
                "skipped": True,
                "reason": self.get_update_skip_reason(),
                "updated_count": 0,
                "failed_count": 0,
                "total_count": 0
            }

        positions = self._position_repo.get_all()

        if not positions:
            return {
                "success": True,
                "reason": "无持仓",
                "updated_count": 0,
                "failed_count": 0,
                "total_count": 0
            }

        # 批量获取行情
        stock_codes = [p.stock_code for p in positions]
        stock_service = self._get_stock_service()

        results = {
            "success": True,
            "skipped": False,
            "updated_count": 0,
            "failed_count": 0,
            "total_count": len(positions),
            "details": []
        }

        for position in positions:
            try:
                quote = stock_service.get_quote(position.stock_code)

                if not quote or 'error' in quote:
                    results["failed_count"] += 1
                    results["details"].append({
                        "stock_code": position.stock_code,
                        "success": False,
                        "reason": "获取行情失败"
                    })
                    continue

                price = quote.get('price', 0)
                if price <= 0:
                    results["failed_count"] += 1
                    results["details"].append({
                        "stock_code": position.stock_code,
                        "success": False,
                        "reason": "价格无效"
                    })
                    continue

                # 更新价格
                old_price = position.current_price
                position.current_price = price

                # 重新计算盈亏
                self._calculate_and_update_profit_loss(position, price)

                results["updated_count"] += 1
                results["details"].append({
                    "stock_code": position.stock_code,
                    "success": True,
                    "old_price": old_price,
                    "new_price": price,
                    "profit_loss": position.profit_loss,
                    "profit_rate": position.profit_rate
                })

            except Exception as e:
                results["failed_count"] += 1
                results["details"].append({
                    "stock_code": position.stock_code,
                    "success": False,
                    "reason": str(e)
                })

        # 提交所有更新
        if results["updated_count"] > 0:
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                results["success"] = False
                results["commit_error"] = str(e)

        return results

    def _calculate_and_update_profit_loss(
        self,
        position: Position,
        current_price: float
    ) -> None:
        """
        重新计算持仓盈亏

        负成本规则:
        - 当 avg_cost < 0 时，不计算盈亏率（返回 None）
        - 盈利金额 = (|成本价 | + 现价) × 数量

        Args:
            position: 持仓对象
            current_price: 当前价
        """
        avg_cost = position.avg_cost
        quantity = position.quantity

        if avg_cost < 0:
            # 负成本：盈利 = (|成本 | + 现价) × 数量
            profit_loss = (abs(avg_cost) + current_price) * quantity
            profit_rate = None  # 负成本时盈亏率无意义
        else:
            # 正成本：标准公式
            profit_loss = (current_price - avg_cost) * quantity
            profit_rate = (
                ((current_price - avg_cost) / avg_cost * 100)
                if avg_cost > 0 else 0
            )

        # 精度控制：四舍五入到 4 位小数
        from decimal import Decimal, ROUND_HALF_UP
        profit_loss = float(
            Decimal(str(profit_loss)).quantize(
                Decimal('0.0001'),
                rounding=ROUND_HALF_UP
            )
        )
        if profit_rate is not None:
            profit_rate = float(
                Decimal(str(profit_rate)).quantize(
                    Decimal('0.0001'),
                    rounding=ROUND_HALF_UP
                )
            )

        position.profit_loss = profit_loss
        position.profit_rate = profit_rate

    def get_portfolio_summary_after_update(self) -> Dict:
        """
        获取更新后的持仓汇总

        Returns:
            包含总市值、盈亏等的字典
        """
        positions = self._position_repo.get_all()

        total_cost = sum(p.avg_cost * p.quantity for p in positions)
        total_value = sum(p.current_price * p.quantity for p in positions)
        total_profit = sum(p.profit_loss for p in positions)

        # 总盈亏率计算：当存在负成本持仓时，只对正成本部分计算
        has_negative_cost = any(p.avg_cost < 0 for p in positions)
        if has_negative_cost:
            total_profit_rate = None
        else:
            total_profit_rate = (
                (total_profit / total_cost * 100)
                if total_cost > 0 else 0
            )

        return {
            "total_cost": total_cost,
            "total_value": total_value,
            "total_profit": total_profit,
            "total_profit_rate": total_profit_rate,
            "position_count": len(positions),
            "has_negative_cost": has_negative_cost
        }
