"""
动态止损模块 (Stop Loss)
根据策略类型和持仓情况，动态计算和调整止损位

止损策略:
1. VCP 爆发：枢轴点下方 3% 或 VCP 最低点
2. 九转抄底：低九期间最低价下方 2%
3. 移动止损：获利 10% 后上移至成本价，之后沿 EMA10/MA20 移动
"""

from typing import Dict, Optional, List
from datetime import datetime


class StopLoss:
    """动态止损管理器"""

    def __init__(self):
        """
        初始化止损管理器
        """
        self.stop_loss_levels = {}  # 存储各股票的止损位

    def set_stop_loss(
        self,
        stock_code: str,
        stop_loss_price: float,
        stop_loss_type: str = 'fixed'
    ):
        """
        设置止损位

        Args:
            stock_code: 股票代码
            stop_loss_price: 止损价
            stop_loss_type: 止损类型 (fixed, trailing, vcp, td)
        """
        self.stop_loss_levels[stock_code] = {
            'price': stop_loss_price,
            'type': stop_loss_type,
            'updated_at': datetime.now()
        }

    def get_stop_loss(self, stock_code: str) -> Optional[Dict]:
        """
        获取止损位

        Args:
            stock_code: 股票代码

        Returns:
            止损位信息字典
        """
        return self.stop_loss_levels.get(stock_code)

    def calculate_vcp_stop_loss(
        self,
        pivot_price: float,
        vcp_lowest_price: float,
        entry_price: float
    ) -> float:
        """
        计算 VCP 爆发策略的止损价

        Args:
            pivot_price: 枢轴点价格
            vcp_lowest_price: VCP 形态最低点
            entry_price: 入场价

        Returns:
            止损价
        """
        # 枢轴点下方 3%
        pivot_stop = pivot_price * (1 - 0.03)

        # VCP 最低点
        vcp_stop = vcp_lowest_price

        # 取两者中较近的
        stop_loss = max(pivot_stop, vcp_stop)

        return stop_loss

    def calculate_td_stop_loss(
        self,
        td_lowest_price: float,
        entry_price: float
    ) -> float:
        """
        计算九转黄金坑策略的止损价

        Args:
            td_lowest_price: 低九期间最低价
            entry_price: 入场价

        Returns:
            止损价
        """
        # 低九期间最低价下方 2%
        stop_loss = td_lowest_price * (1 - 0.02)

        return stop_loss

    def update_trailing_stop(
        self,
        stock_code: str,
        current_price: float,
        entry_price: float,
        ema10: float = None,
        ma20: float = None
    ) -> Dict:
        """
        更新移动止损位

        Args:
            stock_code: 股票代码
            current_price: 当前价
            entry_price: 入场价
            ema10: EMA10 (可选)
            ma20: MA20 (可选)

        Returns:
            止损更新结果
        """
        if stock_code not in self.stop_loss_levels:
            return {
                'updated': False,
                'reason': '止损位未设置'
            }

        stop_info = self.stop_loss_levels[stock_code]
        current_stop = stop_info['price']

        # 计算盈利比例
        profit_pct = (current_price - entry_price) / entry_price * 100

        new_stop = current_stop
        action = 'HOLD'

        # 获利 10% 后，止损上移至成本价
        if profit_pct >= 10:
            break_even_stop = entry_price * 1.02  # 保留 2% 利润
            if break_even_stop > current_stop:
                new_stop = break_even_stop
                action = 'MOVE_TO_BREAK_EVEN'

        # 之后沿 EMA10 或 MA20 移动
        trailing_stop = None
        if ema10 is not None:
            trailing_stop = ema10
        elif ma20 is not None:
            trailing_stop = ma20

        if trailing_stop and trailing_stop > current_stop:
            new_stop = trailing_stop
            action = 'TRAILING'

        # 更新止损位
        if new_stop > current_stop:
            self.stop_loss_levels[stock_code]['price'] = new_stop
            self.stop_loss_levels[stock_code]['updated_at'] = datetime.now()

            return {
                'updated': True,
                'old_stop': current_stop,
                'new_stop': new_stop,
                'action': action,
                'profit_pct': profit_pct
            }

        return {
            'updated': False,
            'reason': '无需上移',
            'current_stop': current_stop,
            'profit_pct': profit_pct
        }

    def check_stop_loss_triggered(
        self,
        stock_code: str,
        current_price: float
    ) -> Dict:
        """
        检查是否触发止损

        Args:
            stock_code: 股票代码
            current_price: 当前价

        Returns:
            止损触发检查结果
        """
        if stock_code not in self.stop_loss_levels:
            return {
                'triggered': False,
                'reason': '止损位未设置'
            }

        stop_info = self.stop_loss_levels[stock_code]
        stop_price = stop_info['price']
        stop_type = stop_info['type']

        if current_price <= stop_price:
            return {
                'triggered': True,
                'stock_code': stock_code,
                'current_price': current_price,
                'stop_price': stop_price,
                'stop_type': stop_type,
                'action': 'SELL',
                'message': f'{stock_code} 触发止损 ({stop_type})，建议卖出'
            }

        # 检查是否接近止损位 (Within 2%)
        distance_to_stop = (current_price - stop_price) / stop_price * 100

        if distance_to_stop < 3:
            return {
                'triggered': False,
                'warning': True,
                'stock_code': stock_code,
                'current_price': current_price,
                'stop_price': stop_price,
                'distance_pct': distance_to_stop,
                'message': f'{stock_code} 接近止损位，当前距离{distance_to_stop:.1f}%'
            }

        return {
            'triggered': False,
            'stock_code': stock_code,
            'current_price': current_price,
            'stop_price': stop_price,
            'distance_pct': distance_to_stop,
            'message': f'{stock_code} 止损位正常，当前距离{distance_to_stop:.1f}%'
        }

    def get_all_stop_losses(self) -> Dict[str, Dict]:
        """
        获取所有止损位

        Returns:
            所有止损位字典
        """
        return self.stop_loss_levels.copy()

    def remove_stop_loss(self, stock_code: str):
        """
        移除止损位 (清仓后调用)

        Args:
            stock_code: 股票代码
        """
        if stock_code in self.stop_loss_levels:
            del self.stop_loss_levels[stock_code]

    def generate_stop_loss_report(self, positions: List[Dict]) -> str:
        """
        生成止损报告

        Args:
            positions: 持仓列表 [{'code': xxx, 'current_price': xxx, 'entry_price': xxx}, ...]

        Returns:
            格式化报告字符串
        """
        report = "📊 **止损位报告**\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        for position in positions:
            code = position.get('stock_code')
            current_price = position.get('current_price')
            entry_price = position.get('entry_price')

            if code not in self.stop_loss_levels:
                report += f"\n{code}: 未设置止损\n"
                continue

            stop_info = self.stop_loss_levels[code]
            stop_price = stop_info['price']
            stop_type = stop_info['type']

            distance = (current_price - stop_price) / stop_price * 100
            profit_pct = (current_price - entry_price) / entry_price * 100 if entry_price else 0

            report += f"\n📌 {code}\n"
            report += f"   当前价：¥{current_price:.2f}\n"
            report += f"   止损价：¥{stop_price:.2f} ({stop_type})\n"
            report += f"   距离：{distance:.1f}%\n"
            report += f"   盈亏：{profit_pct:+.1f}%\n"

        return report
