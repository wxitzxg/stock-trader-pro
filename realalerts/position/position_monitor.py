"""
仓位管理模块 (Position Monitor)
基于 Kelly 公式改良版，结合持仓权重管理

仓位管理原则:
1. 单只股票最大仓位 20%
2. 根据信号强度分级建仓
3. Kelly 公式改良版计算最优仓位
4. 持仓集中度控制 (HHI 指数)
"""

from typing import Dict, List


class PositionMonitor:
    """仓位管理器"""

    def __init__(self, total_capital: float):
        """
        初始化仓位管理器

        Args:
            total_capital: 总资金
        """
        self.total_capital = total_capital
        self.max_single_position = 0.20  # 20%
        self.kelly_factor = 0.5  # 保守系数
        self.min_position = 0.02  # 2% 最小仓位

    def calculate_kelly_position(
        self,
        win_rate: float,
        profit_loss_ratio: float
    ) -> float:
        """
        使用 Kelly 公式计算最优仓位

        Kelly Formula:
        f* = (p * b - q) / b
        其中:
        - p = 胜率
        - q = 败率 (1 - p)
        - b = 盈亏比 (平均盈利/平均亏损)

        Args:
            win_rate: 胜率 (0-1)
            profit_loss_ratio: 盈亏比

        Returns:
            Kelly 建议仓位 (0-1)
        """
        p = win_rate
        q = 1 - win_rate
        b = profit_loss_ratio

        if b <= 0:
            return 0

        kelly_fraction = (p * b - q) / b

        # 应用保守系数，避免过度杠杆
        adjusted_kelly = kelly_fraction * self.kelly_factor

        # 限制在合理范围内
        kelly_position = max(0, min(adjusted_kelly, self.max_single_position))

        return kelly_position

    def calculate_position_size(
        self,
        signal_strength: str,
        confidence_score: float,
        win_rate: float = None,
        profit_loss_ratio: float = None
    ) -> Dict:
        """
        计算建议仓位

        Args:
            signal_strength: 信号强度 (STRONG_BUY, BUY, HOLD)
            confidence_score: 置信度分数 (0-100)
            win_rate: 胜率 (可选)
            profit_loss_ratio: 盈亏比 (可选)

        Returns:
            包含仓位建议的字典
        """
        # 基础仓位根据信号强度
        if signal_strength == 'STRONG_BUY':
            base_position = self.max_single_position  # 20%
        elif signal_strength == 'BUY':
            base_position = 0.10  # 10%
        else:
            base_position = 0.05  # 5% 观察仓

        # 根据置信度调整
        confidence_factor = min(confidence_score / 100, 1.0)
        adjusted_position = base_position * confidence_factor

        # 如果有胜率和盈亏比数据，使用 Kelly 公式优化
        if win_rate is not None and profit_loss_ratio is not None:
            kelly_position = self.calculate_kelly_position(win_rate, profit_loss_ratio)
            # 取 Kelly 和基础仓位的较小值，控制风险
            final_position = min(adjusted_position, kelly_position)
        else:
            final_position = adjusted_position

        # 确保不低于最小仓位
        if final_position > 0:
            final_position = max(final_position, self.min_position)

        # 计算具体金额和股数
        position_amount = self.total_capital * final_position

        return {
            'position_percentage': final_position,
            'position_amount': position_amount,
            'available_capital': self.total_capital * (1 - final_position),
            'signal_strength': signal_strength,
            'confidence_score': confidence_score,
            'kelly_used': win_rate is not None and profit_loss_ratio is not None
        }

    def check_concentration_risk(
        self,
        current_positions: Dict[str, float]
    ) -> Dict:
        """
        检查持仓集中度风险

        Args:
            current_positions: 当前持仓字典 {stock_code: weight}

        Returns:
            集中度风险分析结果
        """
        if not current_positions:
            return {
                'hhi': 0,
                'max_position': 0,
                'top3_concentration': 0,
                'risk_level': 'LOW',
                'message': '无持仓'
            }

        weights = list(current_positions.values())

        # HHI 指数 (Herfindahl-Hirschman Index)
        hhi = sum(w ** 2 for w in weights)

        # 最大单一持仓占比
        max_position = max(weights)

        # 前三大持仓占比
        sorted_weights = sorted(weights, reverse=True)
        top3_concentration = sum(sorted_weights[:3])

        # 风险等级评估
        if hhi > 0.25 or max_position > 0.30:
            risk_level = 'HIGH'
            message = '持仓集中度过高，建议分散'
        elif hhi > 0.15 or max_position > 0.25:
            risk_level = 'MODERATE'
            message = '持仓集中度适中'
        else:
            risk_level = 'LOW'
            message = '持仓分散良好'

        return {
            'hhi': hhi,
            'max_position': max_position,
            'top3_concentration': top3_concentration,
            'risk_level': risk_level,
            'message': message,
            'position_count': len(weights)
        }

    def suggest_rebalance(
        self,
        current_positions: Dict[str, float],
        target_positions: Dict[str, float]
    ) -> List[Dict]:
        """
        生成再平衡建议

        Args:
            current_positions: 当前持仓 {stock_code: weight}
            target_positions: 目标持仓 {stock_code: weight}

        Returns:
            调仓建议列表
        """
        suggestions = []

        all_codes = set(current_positions.keys()) | set(target_positions.keys())

        for code in all_codes:
            current_weight = current_positions.get(code, 0)
            target_weight = target_positions.get(code, 0)

            diff = target_weight - current_weight

            if abs(diff) > 0.02:  # 超过 2% 的差异才建议调仓
                action = 'BUY' if diff > 0 else 'SELL'
                suggestions.append({
                    'stock_code': code,
                    'action': action,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'adjustment': abs(diff),
                    'message': f"{'增持' if diff > 0 else '减持'}至{target_weight:.1%}"
                })

        return suggestions

    def get_available_capital(
        self,
        current_positions: Dict[str, float]
    ) -> float:
        """
        获取可用资金

        Args:
            current_positions: 当前持仓 {stock_code: weight}

        Returns:
            可用资金金额
        """
        total_used = sum(current_positions.values())
        available_percentage = 1 - total_used
        return self.total_capital * available_percentage
