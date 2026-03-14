#!/usr/bin/env python3
"""
买卖信号生成器 (Signal Generator)
基于五维共振引擎结果，生成具体的买卖信号和建议
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from domain.analysis.engines.ultimate_engine import UltimateEngine
from config.settings import SIGNAL_THRESHOLD


class SignalGenerator:
    """买卖信号生成器"""

    def __init__(self, df: pd.DataFrame):
        """
        初始化信号生成器

        Args:
            df: pandas DataFrame，包含 OHLCV 数据
        """
        self.df = df.copy()
        self.engine = UltimateEngine(df)
        self.latest_price = df['close'].iloc[-1]
        self.analysis_date = df.index[-1]

    def generate_buy_signal(self) -> Optional[Dict]:
        """
        生成买入信号

        Returns:
            买入信号字典，如果不满足买入条件则返回 None
        """
        result = self.engine.evaluate_all()

        if result['action'] not in ['BUY', 'STRONG_BUY']:
            return None

        # 计算建议入场价 (当前价)
        suggested_entry = self.latest_price

        # 计算止损价
        stop_loss = self._calculate_stop_loss(result)

        # 计算目标价
        target_price = self._calculate_target_price(result)

        # 风险收益比
        risk_reward_ratio = (target_price - suggested_entry) / (suggested_entry - stop_loss) if suggested_entry > stop_loss else 0

        return {
            'type': 'BUY',
            'strength': result['action'],
            'confidence': result['total_score'],
            'entry_price': suggested_entry,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward_ratio': risk_reward_ratio,
            'position_suggestion': result['position_suggestion'],
            'reasons': self._get_signal_reasons(result),
            'generated_at': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
        }

    def generate_sell_signal(self) -> Optional[Dict]:
        """
        生成卖出信号

        Returns:
            卖出信号字典，如果不满足卖出条件则返回 None
        """
        result = self.engine.evaluate_all()

        # 检查是否有顶部信号
        d5_details = self.dimension_details.get('D5', {})

        if d5_details.get('td_sequential') == 'high_nine':
            return {
                'type': 'SELL',
                'strength': 'WARNING',
                'reason': '神奇九转高九信号',
                'confidence': result['total_score'],
                'suggested_action': '减仓或止盈',
                'generated_at': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
            }

        # 检查是否有顶背离
        d4_details = self.dimension_details.get('D4', {})
        if d4_details.get('macd_divergence') == 'bearish':
            return {
                'type': 'SELL',
                'strength': 'CAUTION',
                'reason': 'MACD 顶背离信号',
                'confidence': result['total_score'],
                'suggested_action': '警惕回调风险',
                'generated_at': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
            }

        return None

    def _calculate_stop_loss(self, result: Dict) -> float:
        """
        计算止损价

        Args:
            result: 五维评估结果

        Returns:
            止损价
        """
        # 根据信号类型选择止损策略
        d2_details = self.dimension_details.get('D2', {})

        if d2_details.get('vcp') in ['breakout_confirmed', 'ready_to_breakout']:
            # VCP 突破：枢轴点下方 3%
            # 简化处理，使用近期低点
            recent_low = self.df['low'].rolling(20).min().iloc[-1]
            return recent_low * 0.97
        else:
            # 通用止损：当前价下方 5%
            return self.latest_price * 0.95

    def _calculate_target_price(self, result: Dict) -> float:
        """
        计算目标价

        Args:
            result: 五维评估结果

        Returns:
            目标价
        """
        # 根据置信度设置目标涨幅
        if result['confidence_level'] == 'S':
            target_pct = 0.20  # 20% 涨幅
        elif result['confidence_level'] == 'A':
            target_pct = 0.15  # 15% 涨幅
        else:
            target_pct = 0.10  # 10% 涨幅

        return self.latest_price * (1 + target_pct)

    def _get_signal_reasons(self, result: Dict) -> List[str]:
        """
        获取信号原因列表

        Args:
            result: 五维评估结果

        Returns:
            原因列表
        """
        reasons = []

        # D1 趋势
        d1_details = self.dimension_details.get('D1', {})
        if d1_details.get('ema_alignment') == 'bullish':
            reasons.append('均线多头排列')
        if d1_details.get('zigzag_trend') == 'up':
            reasons.append('ZigZag 上升趋势')

        # D2 形态
        d2_details = self.dimension_details.get('D2', {})
        if d2_details.get('vcp') == 'breakout_confirmed':
            reasons.append('VCP 突破确认')
        elif d2_details.get('vcp') == 'ready_to_breakout':
            reasons.append('VCP 待突破')
        if d2_details.get('bb_squeeze') == 'strong':
            reasons.append('布林带极度收口')

        # D3 位置
        d3_details = self.dimension_details.get('D3', {})
        if d3_details.get('bb_position') == 'oversold':
            reasons.append('布林带超卖')
        if d3_details.get('rsi') == 'oversold':
            reasons.append('RSI 超卖')

        # D4 动能
        d4_details = self.dimension_details.get('D4', {})
        if d4_details.get('macd_divergence') == 'bullish':
            reasons.append('MACD 底背离')
        if d4_details.get('volume') == 'surge':
            reasons.append('成交量放大')

        # D5 触发
        d5_details = self.dimension_details.get('D5', {})
        if d5_details.get('td_sequential') == 'valid_low_nine':
            reasons.append('有效神奇九转低九')
        if d5_details.get('pivot_breakout') == 'confirmed':
            reasons.append('枢轴突破确认')

        return reasons

    @property
    def dimension_details(self) -> Dict:
        """获取维度详情 (用于内部访问)"""
        return self.engine.dimension_details

    def get_full_analysis(self) -> Dict:
        """
        获取完整分析结果

        Returns:
            包含所有分析结果的字典
        """
        buy_signal = self.generate_buy_signal()
        sell_signal = self.generate_sell_signal()
        engine_result = self.engine.evaluate_all()

        return {
            'symbol': None,  # 由外部填充
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d'),
            'current_price': self.latest_price,
            'engine_result': engine_result,
            'buy_signal': buy_signal,
            'sell_signal': sell_signal,
            'recommendation': self._get_final_recommendation(buy_signal, sell_signal, engine_result)
        }

    def _get_final_recommendation(
        self,
        buy_signal: Optional[Dict],
        sell_signal: Optional[Dict],
        engine_result: Dict
    ) -> str:
        """
        获取最终推荐

        Args:
            buy_signal: 买入信号
            sell_signal: 卖出信号
            engine_result: 引擎结果

        Returns:
            推荐字符串
        """
        if buy_signal and sell_signal:
            return 'HOLD - 多空信号并存，建议观望'
        elif buy_signal:
            return f"{buy_signal['strength']} - 建议{'重仓' if buy_signal['strength'] == 'STRONG_BUY' else '轻仓'}参与"
        elif sell_signal:
            return f"SELL - {sell_signal['reason']}"
        else:
            return 'WAIT - 等待明确信号'
