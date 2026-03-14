#!/usr/bin/env python3
"""
战法 B: 九转黄金坑策略
适合震荡市抄底

适用环境：上升趋势中的回调，或箱体震荡

入场条件:
1. 趋势：股价 > EMA 60 (长期趋势未坏)
2. 位置：股价触及/跌破布林带下轨
3. 触发：出现神奇九转"低九"信号
4. 确认：MACD 出现底背离 (绿柱缩短)
5. 风控：RSI < 30 (超卖)

操作：买入 30%-50% 仓位
止损："低九"期间最低价下方 2%
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime

from domain.analysis.indicators.base_indicators import BaseIndicators
from domain.analysis.indicators.td_sequential import TDSequential
from domain.analysis.indicators.divergence_check import DivergenceCheck
from config import POSITION_PARAMS


class TDGoldenPitStrategy:
    """九转黄金坑策略"""

    def __init__(self, df: pd.DataFrame, symbol: str = None):
        """
        初始化九转黄金坑策略

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

    def check_entry_conditions(self) -> Dict:
        """
        检查入场条件

        Returns:
            包含检查结果和详细信息的字典
        """
        conditions = {
            'trend': self._check_trend(),
            'bb_lower_touch': self._check_bb_lower_touch(),
            'td_low_nine': self._check_td_low_nine(),
            'macd_divergence': self._check_macd_divergence(),
            'rsi_oversold': self._check_rsi_oversold()
        }

        # 计算满足的条件数
        satisfied_count = sum(1 for v in conditions.values() if v['met'])
        total_conditions = len(conditions)

        # 判断是否可以入场 (核心条件必须满足)
        core_conditions = ['trend', 'bb_lower_touch', 'td_low_nine']
        core_met = all(conditions[c]['met'] for c in core_conditions)

        return {
            'can_enter': core_met,
            'satisfied_count': satisfied_count,
            'total_conditions': total_conditions,
            'conditions': conditions,
            'confidence': satisfied_count / total_conditions * 100,
            'core_conditions_met': core_met
        }

    def _check_trend(self) -> Dict:
        """检查趋势条件：股价 > EMA60"""
        latest = self.df.iloc[-1]

        if 'ema50' not in self.df.columns:
            # 尝试使用 MA60
            if 'ma50' in self.df.columns:
                ma60_approx = latest['ma50']
                is_uptrend = latest['close'] > ma60_approx
                return {
                    'met': is_uptrend,
                    'reason': f'当前价={latest["close"]:.2f}, MA50≈{ma60_approx:.2f}' +
                             (' - 趋势向上' if is_uptrend else ' - 趋势向下'),
                    'price': latest['close'],
                    'ema60': ma60_approx
                }
            return {
                'met': True,  # 数据不足时默认满足
                'reason': 'EMA 数据不足，跳过趋势检查',
                'price': latest['close'],
                'ema60': None
            }

        # 使用 EMA50 作为近似 (因为可能没有 EMA60)
        ema50 = latest['ema50']
        is_uptrend = latest['close'] > ema50

        return {
            'met': is_uptrend,
            'reason': f'当前价={latest["close"]:.2f}, EMA50={ema50:.2f}' +
                     (' - 趋势向上' if is_uptrend else ' - 趋势向下'),
            'price': latest['close'],
            'ema60': ema50
        }

    def _check_bb_lower_touch(self) -> Dict:
        """检查布林带下轨触及"""
        latest = self.df.iloc[-1]

        if 'bb_lower' not in self.df.columns:
            return {
                'met': False,
                'reason': '布林带数据不足'
            }

        bb_lower = latest['bb_lower']
        current_price = latest['close']

        # 触及或跌破下轨
        is_touch = current_price <= bb_lower * 1.02  # 允许 2% 的误差

        return {
            'met': is_touch,
            'reason': f'当前价={current_price:.2f}, 下轨={bb_lower:.2f}' +
                     (' - 触及下轨' if is_touch else ' - 未触及下轨'),
            'bb_lower': bb_lower,
            'price': current_price,
            'distance_to_lower': (current_price - bb_lower) / bb_lower * 100
        }

    def _check_td_low_nine(self) -> Dict:
        """检查神奇九转低九信号"""
        td_result = self.td_sequential.get_td_sequential()

        is_low_nine = td_result['td_buy_signal']

        return {
            'met': is_low_nine,
            'reason': td_result['status'],
            'td_buy_count': td_result['td_buy_count'],
            'td_sell_count': td_result['td_sell_count'],
            'signal': td_result['td_buy_signal']
        }

    def _check_macd_divergence(self) -> Dict:
        """检查 MACD 底背离"""
        divergence_result = self.divergence_check.detect_all_divergences()

        has_bullish_divergence = divergence_result['bullish_divergence']['detected']

        return {
            'met': has_bullish_divergence,
            'reason': divergence_result['bullish_divergence']['message'],
            'strength': divergence_result['bullish_divergence'].get('strength', 0),
            'detected': has_bullish_divergence
        }

    def _check_rsi_oversold(self) -> Dict:
        """检查 RSI 超卖"""
        latest = self.df.iloc[-1]

        if 'rsi' not in self.df.columns:
            return {
                'met': False,
                'reason': 'RSI 数据不足'
            }

        rsi = latest['rsi']
        is_oversold = rsi < 30

        return {
            'met': is_oversold,
            'reason': f'RSI={rsi:.2f}' + (' - 超卖' if is_oversold else ' - 未超卖'),
            'rsi': rsi
        }

    def calculate_position_size(self, total_capital: float, confidence: float) -> float:
        """
        计算建议仓位

        Args:
            total_capital: 总资金
            confidence: 置信度 (0-100)

        Returns:
            建议仓位金额
        """
        # 基础仓位 30% (抄底策略相对保守)
        base_position = 0.30

        # 根据置信度调整
        if confidence >= 80:
            position_pct = min(base_position + 0.20, POSITION_PARAMS['max_single_position'])
        elif confidence >= 60:
            position_pct = base_position + 0.10
        else:
            position_pct = base_position

        return total_capital * position_pct

    def calculate_stop_loss(self) -> float:
        """
        计算止损价 (低九期间最低价下方 2%)

        Returns:
            止损价
        """
        # 获取低九期间的最低价
        td_result = self.td_sequential.get_td_sequential()

        if td_result['td_buy_count'] >= 9:
            # 获取过去 9 天的最低价
            lookback = min(td_result['td_buy_count'] + 4, len(self.df))
            lowest_price = self.df['low'].tail(lookback).min()
            stop_loss = lowest_price * 0.98  # 下方 2%
        else:
            # fallback: 当前价下方 5%
            stop_loss = self.latest_price * 0.95

        return stop_loss

    def calculate_target_price(self, entry_price: float) -> float:
        """
        计算目标价

        Args:
            entry_price: 入场价

        Returns:
            目标价
        """
        # 保守目标：15% 涨幅 (抄底策略目标较低)
        return entry_price * 1.15

    def generate_signal(self, total_capital: float = 100000) -> Optional[Dict]:
        """
        生成交易信号

        Args:
            total_capital: 总资金

        Returns:
            交易信号字典，如果不满足条件则返回 None
        """
        entry_result = self.check_entry_conditions()

        if not entry_result['can_enter']:
            return None

        entry_price = self.latest_price
        stop_loss = self.calculate_stop_loss()
        target_price = self.calculate_target_price(entry_price)

        position_size = self.calculate_position_size(total_capital, entry_result['confidence'])
        quantity = int(position_size / entry_price / 100) * 100  # 取整到 100 股

        risk_per_share = entry_price - stop_loss
        total_risk = risk_per_share * quantity
        reward_per_share = target_price - entry_price
        risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0

        return {
            'strategy': 'TD_GOLDEN_PIT',
            'action': 'BUY',
            'symbol': None,  # 由外部填充
            'quantity': quantity,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'position_size': position_size,
            'confidence': entry_result['confidence'],
            'risk_reward_ratio': risk_reward_ratio,
            'conditions': entry_result['conditions'],
            'generated_at': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
        }
