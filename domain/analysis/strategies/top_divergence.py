#!/usr/bin/env python3
"""
战法 C: 顶部背离止盈策略
用于识别顶部风险，及时止盈离场

适用环境：任何市场环境

触发条件:
1. 股价创新高
2. MACD 出现顶背离 (价格创新高但 MACD 未创新高)
3. 或出现神奇九转"高九"信号
4. 或 RSI > 80 (极度超买)
5. 或股价远离布林带上轨 (乖离率过大)

操作：卖出 50%-100% 仓位，或设置移动止盈
"""

import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime

from domain.analysis.indicators.base_indicators import BaseIndicators
from domain.analysis.indicators.td_sequential import TDSequential
from domain.analysis.indicators.divergence_check import DivergenceCheck
from config import STRATEGY_PARAMS


class TopDivergenceStrategy:
    """顶部背离止盈策略"""

    def __init__(self, df: pd.DataFrame, symbol: str = None):
        """
        初始化顶部背离策略

        Args:
            df: pandas DataFrame，包含 OHLCV 数据
            symbol: 股票代码 (用于加载股票特定参数)
        """
        self.df = df.copy()
        self.symbol = symbol
        self.latest_price = df['close'].iloc[-1]
        self.analysis_date = df.index[-1]

        # 初始化指标计算器并计算所有指标
        self.base_indicators = BaseIndicators(self.df, symbol=symbol)
        self.df = self.base_indicators.calculate_all_indicators()

        self.td_sequential = TDSequential(self.df, symbol=symbol)
        self.divergence_check = DivergenceCheck(self.df, symbol=symbol)

    def check_exit_conditions(self) -> Dict:
        """
        检查出场条件

        Returns:
            包含检查结果和详细信息的字典
        """
        conditions = {
            'macd_top_divergence': self._check_macd_top_divergence(),
            'td_high_nine': self._check_td_high_nine(),
            'rsi_overbought': self._check_rsi_overbought(),
            'bb_upper_deviation': self._check_bb_upper_deviation()
        }

        # 计算满足的条件数
        satisfied_count = sum(1 for v in conditions.values() if v['met'])
        total_conditions = len(conditions)

        # 判断是否应该出场 (任一核心条件满足即可)
        should_exit = any(v['met'] for v in conditions.values())

        return {
            'should_exit': should_exit,
            'satisfied_count': satisfied_count,
            'total_conditions': total_conditions,
            'conditions': conditions,
            'urgency': self._calculate_urgency(conditions)
        }

    def _check_macd_top_divergence(self) -> Dict:
        """检查 MACD 顶背离"""
        divergence_result = self.divergence_check.detect_all_divergences()

        has_bearish_divergence = divergence_result['bearish_divergence']['detected']

        result = {
            'met': has_bearish_divergence,
            'reason': divergence_result['bearish_divergence']['message'] if has_bearish_divergence else '未检测到顶背离',
            'strength': divergence_result['bearish_divergence'].get('strength', 0),
            'detected': has_bearish_divergence
        }

        if has_bearish_divergence:
            result['signal'] = 'STRONG_SELL'

        return result

    def _check_td_high_nine(self) -> Dict:
        """检查神奇九转高九信号"""
        td_result = self.td_sequential.get_td_sequential()

        is_high_nine = td_result['td_sell_signal']

        result = {
            'met': is_high_nine,
            'reason': td_result['status'],
            'td_buy_count': td_result['td_buy_count'],
            'td_sell_count': td_result['td_sell_count'],
            'signal': td_result['td_sell_signal']
        }

        if is_high_nine:
            result['signal'] = 'SELL'

        return result

    def _check_rsi_overbought(self) -> Dict:
        """检查 RSI 超买"""
        latest = self.df.iloc[-1]

        if 'rsi' not in self.df.columns:
            return {
                'met': False,
                'reason': 'RSI 数据不足'
            }

        rsi = latest['rsi']
        is_overbought = rsi > 70
        is_extreme_overbought = rsi > 80

        result = {
            'met': is_overbought,
            'reason': f'RSI={rsi:.2f}' + (' - 超买' if is_overbought else ''),
            'rsi': rsi
        }

        if is_extreme_overbought:
            result['signal'] = 'STRONG_SELL'
        elif is_overbought:
            result['signal'] = 'CAUTION'

        return result

    def _check_bb_upper_deviation(self) -> Dict:
        """检查布林带上轨乖离"""
        latest = self.df.iloc[-1]

        if 'bb_upper' not in self.df.columns:
            return {
                'met': False,
                'reason': '布林带数据不足'
            }

        bb_upper = latest['bb_upper']
        current_price = latest['close']

        # 计算乖离率
        deviation = (current_price - bb_upper) / bb_upper * 100 if bb_upper > 0 else 0
        is_overextended = deviation > 5  # 超过上轨 5% 以上

        result = {
            'met': is_overextended,
            'reason': f'当前价={current_price:.2f}, 上轨={bb_upper:.2f}, 乖离率={deviation:.2f}%' +
                     (' - 乖离过大' if is_overextended else ''),
            'deviation': deviation,
            'bb_upper': bb_upper,
            'price': current_price
        }

        if is_overextended:
            result['signal'] = 'CAUTION'

        return result

    def _calculate_urgency(self, conditions: Dict) -> str:
        """
        计算出场紧急程度

        Args:
            conditions: 条件检查结果

        Returns:
            紧急程度字符串
        """
        strong_sell_signals = sum(
            1 for v in conditions.values()
            if v.get('signal') == 'STRONG_SELL'
        )

        if strong_sell_signals >= 2:
            return 'IMMEDIATE'  # 立即出场
        elif strong_sell_signals >= 1:
            return 'HIGH'  # 高紧急度
        elif sum(1 for v in conditions.values() if v['met']) >= 2:
            return 'MODERATE'  # 中等紧急度
        else:
            return 'LOW'  # 低紧急度

    def generate_signal(self, current_position: Dict = None) -> Optional[Dict]:
        """
        生成交易信号

        Args:
            current_position: 当前持仓信息 (可选)

        Returns:
            交易信号字典，如果不满足条件则返回 None
        """
        exit_result = self.check_exit_conditions()

        if not exit_result['should_exit']:
            return None

        urgency = exit_result['urgency']

        # 根据紧急程度建议卖出比例
        if urgency == 'IMMEDIATE':
            sell_ratio = 1.0  # 100% 清仓
            action_strength = 'STRONG_SELL'
        elif urgency == 'HIGH':
            sell_ratio = 0.7  # 70% 减仓
            action_strength = 'SELL'
        elif urgency == 'MODERATE':
            sell_ratio = 0.5  # 50% 减仓
            action_strength = 'REDUCE'
        else:
            sell_ratio = 0.3  # 30% 减仓
            action_strength = 'TRIM'

        # 收集触发原因
        reasons = []
        for condition_name, condition in exit_result['conditions'].items():
            if condition['met']:
                reasons.append(condition['reason'])

        return {
            'strategy': 'TOP_DIVERGENCE',
            'action': action_strength,
            'symbol': None,  # 由外部填充
            'sell_ratio': sell_ratio,
            'suggested_action': f'建议{int(sell_ratio * 100)}%减仓',
            'urgency': urgency,
            'reasons': reasons,
            'conditions': exit_result['conditions'],
            'generated_at': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_trailing_stop_suggestion(self, entry_price: float, current_price: float) -> Dict:
        """
        生成移动止盈建议

        Args:
            entry_price: 入场价
            current_price: 当前价

        Returns:
            移动止盈建议字典
        """
        # 计算当前盈利比例
        profit_pct = (current_price - entry_price) / entry_price * 100

        if profit_pct < 0:
            return {
                'action': 'HOLD',
                'reason': '尚未盈利，不建议移动止盈',
                'profit_pct': profit_pct,
                'suggested_stop': None
            }

        # 获利 10% 后，止盈上移至成本价
        if profit_pct >= 10:
            break_even_stop = entry_price * 1.02  # 保留 2% 利润
            return {
                'action': 'MOVE_TO_BREAK_EVEN',
                'reason': f'已获利{profit_pct:.1f}%，建议止盈上移至成本价附近',
                'profit_pct': profit_pct,
                'suggested_stop': break_even_stop
            }

        # 之后沿 EMA10 或布林带中轨移动止盈
        latest = self.df.iloc[-1]
        trailing_stop = None

        if 'ma20' in self.df.columns:
            trailing_stop = latest['ma20']  # 使用 MA20 作为移动止盈
        elif 'bb_middle' in self.df.columns:
            trailing_stop = latest['bb_middle']  # 使用布林带中轨

        if trailing_stop and current_price > trailing_stop:
            return {
                'action': 'TRAILING_STOP',
                'reason': f'已获利{profit_pct:.1f}%，建议移动止盈价位',
                'profit_pct': profit_pct,
                'suggested_stop': trailing_stop
            }

        return {
            'action': 'HOLD',
            'reason': f'已获利{profit_pct:.1f}%，继续持有',
            'profit_pct': profit_pct,
            'suggested_stop': None
        }

    def get_risk_warning(self) -> List[str]:
        """
        获取风险警告列表

        Returns:
            风险警告列表
        """
        warnings = []
        exit_result = self.check_exit_conditions()

        for condition_name, condition in exit_result['conditions'].items():
            if condition.get('signal') == 'STRONG_SELL':
                warnings.append(f"⚠️ 强烈警告：{condition['reason']}")
            elif condition.get('signal') == 'SELL':
                warnings.append(f"⚠️ 警告：{condition['reason']}")
            elif condition.get('signal') == 'CAUTION':
                warnings.append(f"⚠️ 注意：{condition['reason']}")

        return warnings
