#!/usr/bin/env python3
"""
战法 A: VCP 爆发突击策略
胜率最高，盈亏比最大的策略

适用环境：牛市或震荡市中的强势股

入场条件:
1. 趋势：股价 > EMA 50 > EMA 200
2. 形态：识别出完整的 VCP 结构 (至少 2 次收缩)
3. 状态：布林带极度收口，成交量缩至地量
4. 触发：股价放量 (>1.5 倍均量) 突破 VCP 枢轴点 (Pivot)
5. 确认：MACD 在零轴上方金叉或红柱放大

操作：立即买入 50%-70% 仓位
止损：跌破枢轴点 3% 或 VCP 最低点
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime

from investing.indicators.base_indicators import BaseIndicators
from investing.indicators.vcp_detector import VCPDetector
from config.settings import STRATEGY_PARAMS, POSITION_PARAMS


class VCPBreakoutStrategy:
    """VCP 爆发突击策略"""

    def __init__(self, df: pd.DataFrame, symbol: str = None):
        """
        初始化 VCP 策略

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

        self.vcp_detector = VCPDetector(self.df, symbol=symbol)

    def check_entry_conditions(self) -> Dict:
        """
        检查入场条件

        Returns:
            包含检查结果和详细信息的字典
        """
        conditions = {
            'trend': self._check_trend(),
            'vcp_pattern': self._check_vcp_pattern(),
            'bb_squeeze': self._check_bb_squeeze(),
            'volume_surge': self._check_volume_surge(),
            'macd_confirmation': self._check_macd_confirmation()
        }

        # 计算满足的条件数
        satisfied_count = sum(1 for v in conditions.values() if v['met'])
        total_conditions = len(conditions)

        # 判断是否可以入场
        can_enter = all(v['met'] for v in conditions.values())

        return {
            'can_enter': can_enter,
            'satisfied_count': satisfied_count,
            'total_conditions': total_conditions,
            'conditions': conditions,
            'confidence': satisfied_count / total_conditions * 100
        }

    def _check_trend(self) -> Dict:
        """检查趋势条件：股价 > EMA50 > EMA200"""
        latest = self.df.iloc[-1]

        if 'ema50' not in self.df.columns:
            return {
                'met': False,
                'reason': 'EMA 数据不足'
            }

        ema50 = latest['ema50']
        current_price = latest['close']

        # 检查是否有 EMA200 数据
        if 'ema200' not in self.df.columns or np.isnan(latest.get('ema200', np.nan)):
            # 如果没有 EMA200，使用 MA50 作为替代
            if 'ma50' in self.df.columns:
                ma50 = latest['ma50']
                is_bullish = current_price > ma50
                return {
                    'met': is_bullish,
                    'reason': f'当前价={current_price:.2f}, MA50={ma50:.2f} (EMA200 数据不足)' +
                             (' - 趋势向上' if is_bullish else ' - 趋势向下'),
                    'ema50': ema50,
                    'ema200': None,
                    'price': current_price
                }
            return {
                'met': current_price > ema50,
                'reason': f'当前价={current_price:.2f}, EMA50={ema50:.2f} (EMA200 数据不足)',
                'ema50': ema50,
                'ema200': None,
                'price': current_price
            }

        ema200 = latest['ema200']
        is_bullish = current_price > ema50 > ema200

        return {
            'met': is_bullish,
            'reason': f'当前价={current_price:.2f}, EMA50={ema50:.2f}, EMA200={ema200:.2f}' +
                     (' - 多头排列' if is_bullish else ' - 非多头排列'),
            'ema50': ema50,
            'ema200': ema200,
            'price': current_price
        }

    def _check_vcp_pattern(self) -> Dict:
        """检查 VCP 形态"""
        vcp_result = self.vcp_detector.detect_vcp()

        is_ready = vcp_result['is_vcp'] and vcp_result['stage'] in [
            'ready_to_breakout',
            'tightening'
        ]
        is_breakout = vcp_result['breakout_detected']

        return {
            'met': is_ready or is_breakout,
            'reason': vcp_result['message'],
            'stage': vcp_result['stage'],
            'breakout_detected': is_breakout,
            'contraction_ratio': vcp_result.get('contraction_ratio', 0)
        }

    def _check_bb_squeeze(self) -> Dict:
        """检查布林带收口"""
        if 'bb_bandwidth' not in self.df.columns:
            return {
                'met': False,
                'reason': '布林带数据不足'
            }

        bb_bandwidth = self.df['bb_bandwidth']
        current_bb = bb_bandwidth.iloc[-1]

        # 计算带宽分位数
        rolling_min = bb_bandwidth.rolling(120).min()
        rolling_max = bb_bandwidth.rolling(120).max()
        bb_percentile = (rolling_min / rolling_max).iloc[-1]

        is_squeeze = bb_percentile < 0.3 if not pd.isna(bb_percentile) else False

        return {
            'met': is_squeeze,
            'reason': f'带宽分位数={bb_percentile:.2%}' + (' - 极度收口' if is_squeeze else ''),
            'bb_bandwidth': current_bb,
            'bb_percentile': bb_percentile if not pd.isna(bb_percentile) else 0
        }

    def _check_volume_surge(self) -> Dict:
        """检查成交量放大"""
        latest = self.df.iloc[-1]

        if 'volume_ratio' not in self.df.columns:
            return {
                'met': False,
                'reason': '成交量数据不足'
            }

        volume_ratio = latest['volume_ratio']
        is_surge = volume_ratio > 1.5

        return {
            'met': is_surge,
            'reason': f'量比={volume_ratio:.2f}' + (' - 放量' if is_surge else ''),
            'volume_ratio': volume_ratio
        }

    def _check_macd_confirmation(self) -> Dict:
        """检查 MACD 确认"""
        latest = self.df.iloc[-1]

        if 'macd' not in self.df.columns or 'macd_signal' not in self.df.columns:
            return {
                'met': False,
                'reason': 'MACD 数据不足'
            }

        macd = latest['macd']
        macd_signal = latest['macd_signal']
        macd_histogram = latest.get('macd_histogram', macd - macd_signal)

        # MACD 金叉或红柱放大
        is_bullish = macd > macd_signal or macd_histogram > 0

        return {
            'met': is_bullish,
            'reason': f'MACD={macd:.4f}, Signal={macd_signal:.4f}, Histogram={macd_histogram:.4f}' +
                     (' - 金叉/红柱' if is_bullish else ''),
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram
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
        # 基础仓位 50%
        base_position = 0.50

        # 根据置信度调整
        if confidence >= 80:
            position_pct = min(base_position + 0.20, POSITION_PARAMS['max_single_position'])
        elif confidence >= 60:
            position_pct = base_position + 0.10
        else:
            position_pct = base_position

        return total_capital * position_pct

    def calculate_stop_loss(self, entry_price: float) -> float:
        """
        计算止损价

        Args:
            entry_price: 入场价

        Returns:
            止损价
        """
        # 获取 VCP 最低点
        vcp_result = self.vcp_detector.detect_vcp()

        if vcp_result['drops'] and len(vcp_result['drops']) > 0:
            # 使用最后一次回调的最低点
            lowest_point = min(d['trough_price'] for d in vcp_result['drops'])
            stop_loss = lowest_point * 0.97  # 最低点下方 3%
        else:
            #  fallback: 入场价下方 5%
            stop_loss = entry_price * 0.95

        return stop_loss

    def calculate_target_price(self, entry_price: float) -> float:
        """
        计算目标价

        Args:
            entry_price: 入场价

        Returns:
            目标价
        """
        # 保守目标：20% 涨幅
        return entry_price * 1.20

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
        stop_loss = self.calculate_stop_loss(entry_price)
        target_price = self.calculate_target_price(entry_price)

        position_size = self.calculate_position_size(total_capital, entry_result['confidence'])
        quantity = int(position_size / entry_price / 100) * 100  # 取整到 100 股

        risk_per_share = entry_price - stop_loss
        total_risk = risk_per_share * quantity
        reward_per_share = target_price - entry_price
        risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0

        return {
            'strategy': 'VCP_BREAKOUT',
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
