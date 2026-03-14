#!/usr/bin/env python3
"""
MACD 背离检测模块 (Divergence Check)
用于识别价格与 MACD 指标之间的背离信号

背离类型:
1. 底背离 (Bullish Divergence): 价格创新低，但 MACD 未创新低 (买入信号)
2. 顶背离 (Bearish Divergence): 价格创新高，但 MACD 未创新高 (卖出信号)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from ta.trend import MACD
from config import get_config


class DivergenceCheck:
    """MACD 背离检测器"""

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: str = None,
        window: int = None
    ):
        """
        初始化 MACD 背离检测器

        Args:
            df: pandas DataFrame，必须包含 'close', 'high', 'low' 列
            symbol: 股票代码 (用于加载股票特定参数)
            window: 检测窗口大小 (默认 20，可从 config/config.json 加载)
        """
        self.df = df.copy()
        self.symbol = symbol
        self.window = window

        # 加载股票特定参数
        self._config = get_config() if symbol else None
        div_params = self._config.get_divergence_params(symbol) if symbol else {}

        # 构造函数参数优先于配置文件
        self.window = window if window is not None else div_params.get('window', 20)

        self._validate_data()
        self._calculate_macd()

    def _validate_data(self):
        """验证数据格式"""
        required_columns = ['close', 'high', 'low']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"缺少必需的列：{col}")

    def _calculate_macd(self):
        """计算 MACD 指标"""
        macd = MACD(
            close=self.df['close'],
            window_fast=12,
            window_slow=26,
            window_sign=9
        )
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['macd_histogram'] = macd.macd_diff()

    def _find_price_peaks(self, lookback: int = None) -> List[Tuple[int, float]]:
        """
        寻找价格高点

        Args:
            lookback: 回溯窗口大小

        Returns:
            价格高点列表 [(index, price), ...]
        """
        if lookback is None:
            lookback = self.window

        peaks = []
        n = len(self.df)
        start_idx = max(0, n - lookback)

        for i in range(start_idx + 2, n - 2):
            # 检查是否为局部高点
            if (self.df['high'].iloc[i] > self.df['high'].iloc[i - 1] and
                self.df['high'].iloc[i] > self.df['high'].iloc[i - 2] and
                self.df['high'].iloc[i] > self.df['high'].iloc[i + 1] and
                self.df['high'].iloc[i] > self.df['high'].iloc[i + 2]):
                peaks.append((i, self.df['high'].iloc[i]))

        return peaks

    def _find_price_troughs(self, lookback: int = None) -> List[Tuple[int, float]]:
        """
        寻找价格低点

        Args:
            lookback: 回溯窗口大小

        Returns:
            价格低点列表 [(index, price), ...]
        """
        if lookback is None:
            lookback = self.window

        troughs = []
        n = len(self.df)
        start_idx = max(0, n - lookback)

        for i in range(start_idx + 2, n - 2):
            # 检查是否为局部低点
            if (self.df['low'].iloc[i] < self.df['low'].iloc[i - 1] and
                self.df['low'].iloc[i] < self.df['low'].iloc[i - 2] and
                self.df['low'].iloc[i] < self.df['low'].iloc[i + 1] and
                self.df['low'].iloc[i] < self.df['low'].iloc[i + 2]):
                troughs.append((i, self.df['low'].iloc[i]))

        return troughs

    def _find_macd_peaks(self, lookback: int = None) -> List[Tuple[int, float]]:
        """
        寻找 MACD 高点

        Args:
            lookback: 回溯窗口大小

        Returns:
            MACD 高点列表 [(index, macd_value), ...]
        """
        if lookback is None:
            lookback = self.window

        peaks = []
        n = len(self.df)
        start_idx = max(0, n - lookback)

        for i in range(start_idx + 2, n - 2):
            if (self.df['macd'].iloc[i] > self.df['macd'].iloc[i - 1] and
                self.df['macd'].iloc[i] > self.df['macd'].iloc[i - 2] and
                self.df['macd'].iloc[i] > self.df['macd'].iloc[i + 1] and
                self.df['macd'].iloc[i] > self.df['macd'].iloc[i + 2]):
                peaks.append((i, self.df['macd'].iloc[i]))

        return peaks

    def _find_macd_troughs(self, lookback: int = None) -> List[Tuple[int, float]]:
        """
        寻找 MACD 低点

        Args:
            lookback: 回溯窗口大小

        Returns:
            MACD 低点列表 [(index, macd_value), ...]
        """
        if lookback is None:
            lookback = self.window

        troughs = []
        n = len(self.df)
        start_idx = max(0, n - lookback)

        for i in range(start_idx + 2, n - 2):
            if (self.df['macd'].iloc[i] < self.df['macd'].iloc[i - 1] and
                self.df['macd'].iloc[i] < self.df['macd'].iloc[i - 2] and
                self.df['macd'].iloc[i] < self.df['macd'].iloc[i + 1] and
                self.df['macd'].iloc[i] < self.df['macd'].iloc[i + 2]):
                troughs.append((i, self.df['macd'].iloc[i]))

        return troughs

    def detect_bullish_divergence(self) -> Dict:
        """
        检测底背离 (Bullish Divergence)

        条件:
        1. 价格创新低
        2. MACD 未创新低 (形成更高的低点)

        Returns:
            检测结果字典
        """
        troughs = self._find_price_troughs()
        macd_troughs = self._find_macd_troughs()

        if len(troughs) < 2 or len(macd_troughs) < 2:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0,
                'message': '数据点不足，无法检测底背离'
            }

        # 找最近的两个价格低点和 MACD 低点
        recent_price_troughs = troughs[-2:]
        recent_macd_troughs = macd_troughs[-2:]

        if len(recent_price_troughs) < 2 or len(recent_macd_troughs) < 2:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0,
                'message': '未找到足够的低点'
            }

        # 检查价格是否创新低
        price_lower = recent_price_troughs[1][1] < recent_price_troughs[0][1]

        # 检查 MACD 是否形成更高的低点
        macd_higher = recent_macd_troughs[1][1] > recent_macd_troughs[0][1]

        # 检查时间对应关系 (MACD 低点应该对应价格低点)
        time_aligned = True
        for pt, mt in zip(recent_price_troughs, recent_macd_troughs):
            if abs(pt[0] - mt[0]) > 5:  # 允许 5 天之内的偏差
                time_aligned = False
                break

        detected = price_lower and macd_higher and time_aligned

        if detected:
            # 计算背离强度
            price_change = (recent_price_troughs[1][1] - recent_price_troughs[0][1]) / recent_price_troughs[0][1]
            macd_change = recent_macd_troughs[1][1] - recent_macd_troughs[0][1]

            strength = abs(macd_change) / (abs(price_change) + 0.001)  # 避免除零

            return {
                'detected': True,
                'type': 'bullish',
                'strength': min(strength * 10, 10),  # 归一化到 0-10
                'price_troughs': recent_price_troughs,
                'macd_troughs': recent_macd_troughs,
                'message': f'🟢 底背离检测！价格创新低但 MACD 未创新低，强度：{strength:.1f}/10'
            }

        return {
            'detected': False,
            'type': 'none',
            'strength': 0,
            'message': '未检测到底背离'
        }

    def detect_bearish_divergence(self) -> Dict:
        """
        检测顶背离 (Bearish Divergence)

        条件:
        1. 价格创新高
        2. MACD 未创新高 (形成更低的高点)

        Returns:
            检测结果字典
        """
        peaks = self._find_price_peaks()
        macd_peaks = self._find_macd_peaks()

        if len(peaks) < 2 or len(macd_peaks) < 2:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0,
                'message': '数据点不足，无法检测顶背离'
            }

        # 找最近的两个价格高点和 MACD 高点
        recent_price_peaks = peaks[-2:]
        recent_macd_peaks = macd_peaks[-2:]

        if len(recent_price_peaks) < 2 or len(recent_macd_peaks) < 2:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0,
                'message': '未找到足够的高点'
            }

        # 检查价格是否创新高
        price_higher = recent_price_peaks[1][1] > recent_price_peaks[0][1]

        # 检查 MACD 是否形成更低的高点
        macd_lower = recent_macd_peaks[1][1] < recent_macd_peaks[0][1]

        # 检查时间对应关系
        time_aligned = True
        for pp, mp in zip(recent_price_peaks, recent_macd_peaks):
            if abs(pp[0] - mp[0]) > 5:  # 允许 5 天之内的偏差
                time_aligned = False
                break

        detected = price_higher and macd_lower and time_aligned

        if detected:
            # 计算背离强度
            price_change = (recent_price_peaks[1][1] - recent_price_peaks[0][1]) / recent_price_peaks[0][1]
            macd_change = recent_macd_peaks[0][1] - recent_macd_peaks[1][1]

            strength = abs(macd_change) / (abs(price_change) + 0.001)  # 避免除零

            return {
                'detected': True,
                'type': 'bearish',
                'strength': min(strength * 10, 10),  # 归一化到 0-10
                'price_peaks': recent_price_peaks,
                'macd_peaks': recent_macd_peaks,
                'message': f'🔴 顶背离检测！价格创新高但 MACD 未创新高，强度：{strength:.1f}/10'
            }

        return {
            'detected': False,
            'type': 'none',
            'strength': 0,
            'message': '未检测到顶背离'
        }

    def detect_all_divergences(self) -> Dict:
        """
        检测所有背离信号

        Returns:
            包含所有背离检测结果的字典
        """
        bullish = self.detect_bullish_divergence()
        bearish = self.detect_bearish_divergence()

        return {
            'bullish_divergence': bullish,
            'bearish_divergence': bearish,
            'has_divergence': bullish['detected'] or bearish['detected'],
            'current_signal': 'bullish' if bullish['detected'] else ('bearish' if bearish['detected'] else 'neutral')
        }
