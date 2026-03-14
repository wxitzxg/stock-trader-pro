"""
AnalysisService - 资产分析业务逻辑
"""
from typing import Dict, List

from models.position import Position
from repositories.position_repo import PositionRepository


class AnalysisService:
    """资产分析业务逻辑"""

    def __init__(self, session):
        """
        初始化分析服务

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self._position_repo = PositionRepository(session)

    def get_portfolio_summary(self) -> Dict:
        """
        获取持仓汇总

        Returns:
            包含总市值、盈亏等的字典
        """
        positions = self._position_repo.get_all()

        total_cost = sum(p.avg_cost * p.quantity for p in positions)
        total_value = sum(p.current_price * p.quantity for p in positions)
        total_profit = sum(p.profit_loss for p in positions)  # 直接使用已计算的 profit_loss

        # 总盈亏率计算：当存在负成本持仓时，只对正成本部分计算
        has_negative_cost = any(p.avg_cost < 0 for p in positions)
        if has_negative_cost:
            # 存在负成本持仓，总盈亏率标注为 None
            total_profit_rate = None
        else:
            total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0

        total_realized = sum(p.realized_profit for p in positions)

        return {
            "total_cost": total_cost,
            "total_value": total_value,
            "total_profit": total_profit,
            "total_profit_rate": total_profit_rate,
            "total_realized_profit": total_realized,
            "position_count": len(positions),
            "has_negative_cost": has_negative_cost  # 标记是否存在负成本持仓
        }

    def get_concentration(self) -> Dict:
        """
        计算持仓集中度

        Returns:
            包含前三大持仓占比、HHI 指数的字典
        """
        positions = self._position_repo.get_all()
        total_value = sum(p.current_price * p.quantity for p in positions)

        if total_value == 0:
            return {
                "top3_concentration": 0,
                "max_position_concentration": 0,
                "position_count": 0,
                "herfindahl_index": 0
            }

        weights = sorted(
            [(p.current_price * p.quantity / total_value) for p in positions],
            reverse=True
        )

        top3_concentration = sum(weights[:3]) if len(weights) >= 3 else sum(weights)
        hhi = sum(w ** 2 for w in weights)

        return {
            "top3_concentration": top3_concentration,
            "max_position_concentration": weights[0] if weights else 0,
            "position_count": len(positions),
            "herfindahl_index": hhi
        }

    def get_position_weights(self) -> Dict[str, float]:
        """
        计算各持仓权重

        Returns:
            字典，key 为股票代码，value 为持仓权重（0-1 之间）
        """
        positions = self._position_repo.get_all()
        total_value = sum(p.current_price * p.quantity for p in positions)

        if total_value == 0:
            return {}

        return {
            p.stock_code: (p.current_price * p.quantity / total_value)
            for p in positions
        }

    def get_risk_exposure(self) -> Dict:
        """
        计算风险敞口

        Returns:
            包含总风险敞口、各持仓风险贡献的字典
        """
        positions = self._position_repo.get_all()
        total_value = sum(p.current_price * p.quantity for p in positions)

        # 计算总浮动盈亏
        total_unrealized_pnl = sum(p.profit_loss for p in positions)

        # 计算总实现盈亏
        total_realized_pnl = sum(p.realized_profit for p in positions)

        # 总体盈亏
        total_profit = total_unrealized_pnl + total_realized_pnl

        return {
            "total_market_value": total_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_profit": total_profit,
            "unrealized_profit_rate": (total_unrealized_pnl / total_value * 100) if total_value > 0 else 0
        }
