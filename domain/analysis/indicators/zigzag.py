#!/usr/bin/env python3
"""
ZigZag 指标模块 (之字转向指标)
用于过滤噪音，识别显著的波段高低点

重要警示:
- ZigZag 仅用于盘后分析，严禁用于实时预测
- 最新一个转折点可能会随价格变化而重新绘制
- 适合用于识别历史波段结构和 VCP 形态分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import get_config


class ZigZag:
    """ZigZag 指标计算器"""

    def __init__(self, df: pd.DataFrame, symbol: str = None, threshold: float = None):
        """
        初始化 ZigZag 计算器

        Args:
            df: pandas DataFrame，必须包含 'high', 'low' 列
            symbol: 股票代码 (用于加载股票特定参数)
            threshold: 转折阈值 (默认 0.05 即 5%)
        """
        self.df = df.copy()
        self.symbol = symbol

        # Load per-stock parameters
        self._config = get_config() if symbol else None
        zigzag_params = self._config.get_zigzag_params(symbol) if symbol else {}

        # Allow constructor args to override config
        self.threshold = threshold if threshold is not None else zigzag_params.get('threshold', 0.05)
        self._validate_data()
        self._zigzag_high = None
        self._zigzag_low = None
        self._pivot_points = None

    def _validate_data(self):
        """验证数据格式"""
        required_columns = ['high', 'low']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"缺少必需的列：{col}")

    def calculate_zigzag(self) -> pd.DataFrame:
        """
        计算 ZigZag 指标

        Returns:
            包含 ZigZag 线的 DataFrame
        """
        n = len(self.df)
        zigzag = np.full(n, np.nan)
        pivot_high = np.full(n, np.nan)
        pivot_low = np.full(n, np.nan)

        # 初始化
        swing_high = self.df['high'].iloc[0]
        swing_low = self.df['low'].iloc[0]
        last_pivot_type = None  # 'high' or 'low'
        last_pivot_idx = 0

        for i in range(1, n):
            current_high = self.df['high'].iloc[i]
            current_low = self.df['low'].iloc[i]

            if last_pivot_type is None:
                # 寻找第一个转折点
                if current_high > swing_high:
                    swing_high = current_high
                if current_low < swing_low:
                    swing_low = current_low

                # 检查是否形成转折
                if swing_high > swing_low * (1 + self.threshold):
                    last_pivot_type = 'high'
                    last_pivot_idx = i
                    zigzag[i] = swing_high
                    pivot_high[i] = swing_high
                elif swing_low < swing_high * (1 - self.threshold):
                    last_pivot_type = 'low'
                    last_pivot_idx = i
                    zigzag[i] = swing_low
                    pivot_low[i] = swing_low
            else:
                if last_pivot_type == 'high':
                    # 从高点向下找低点
                    if current_low < swing_low:
                        swing_low = current_low

                    # 检查是否形成新低
                    if swing_low < zigzag[last_pivot_idx] * (1 - self.threshold):
                        zigzag[i] = swing_low
                        pivot_low[i] = swing_low
                        last_pivot_type = 'low'
                        last_pivot_idx = i
                        swing_high = current_high  # 重置 swing_high
                else:
                    # 从低点向上找高点
                    if current_high > swing_high:
                        swing_high = current_high

                    # 检查是否形成新高
                    if swing_high > zigzag[last_pivot_idx] * (1 + self.threshold):
                        zigzag[i] = swing_high
                        pivot_high[i] = swing_high
                        last_pivot_type = 'high'
                        last_pivot_idx = i
                        swing_low = current_low  # 重置 swing_low

        self._zigzag_high = zigzag
        self._pivot_points = {'high': pivot_high, 'low': pivot_low}

        self.df['zigzag'] = zigzag
        return self.df

    def get_pivot_points(self) -> Dict:
        """
        获取枢轴点

        Returns:
            包含高低枢轴点的字典
        """
        if self._pivot_points is None:
            self.calculate_zigzag()

        pivot_high = self._pivot_points['high']
        pivot_low = self._pivot_points['low']

        # 提取非空的枢轴点
        highs = [(i, self.df['high'].iloc[i]) for i in range(len(self.df)) if not np.isnan(pivot_high[i])]
        lows = [(i, self.df['low'].iloc[i]) for i in range(len(self.df)) if not np.isnan(pivot_low[i])]

        return {
            'highs': highs,
            'lows': lows
        }

    def get_wave_structure(self) -> Dict:
        """
        获取波段结构

        Returns:
            包含波段信息的字典
        """
        pivots = self.get_pivot_points()
        highs = pivots['highs']
        lows = pivots['lows']

        if len(highs) < 2 or len(lows) < 2:
            return {
                'trend': 'insufficient_data',
                'waves': [],
                'message': '数据不足，无法分析波段结构'
            }

        waves = []

        # 分析上涨波
        for i in range(1, len(lows)):
            if i < len(highs):
                wave_start = lows[i - 1]
                wave_peak = highs[i - 1] if i <= len(highs) else highs[-1]

                if wave_start[1] > 0:
                    wave_magnitude = (wave_peak[1] - wave_start[1]) / wave_start[1]
                    waves.append({
                        'type': 'up',
                        'start_idx': wave_start[0],
                        'start_price': wave_start[1],
                        'end_idx': wave_peak[0],
                        'end_price': wave_peak[1],
                        'magnitude': wave_magnitude
                    })

        # 分析下跌波
        for i in range(1, len(highs)):
            if i <= len(lows):
                wave_start = highs[i - 1]
                wave_trough = lows[i - 1] if i <= len(lows) else lows[-1]

                if wave_start[1] > 0:
                    wave_magnitude = (wave_trough[1] - wave_start[1]) / wave_start[1]
                    waves.append({
                        'type': 'down',
                        'start_idx': wave_start[0],
                        'start_price': wave_start[1],
                        'end_idx': wave_trough[0],
                        'end_price': wave_trough[1],
                        'magnitude': wave_magnitude
                    })

        # 判断当前趋势
        if highs and lows:
            last_high = highs[-1]
            last_low = lows[-1]

            if last_high[0] > last_low[0]:
                current_trend = 'down'  # 最后一个枢轴是高点和下降趋势
            else:
                current_trend = 'up'
        else:
            current_trend = 'unknown'

        return {
            'trend': current_trend,
            'waves': waves,
            'wave_count': len(waves),
            'message': f'检测到{len(waves)}个波段，当前趋势：{current_trend}'
        }

    def calculate_wave_depths(self) -> List[float]:
        """
        计算下跌波深度 (用于 VCP 分析)

        Returns:
            下跌波深度列表
        """
        structure = self.get_wave_structure()
        depths = []

        for wave in structure['waves']:
            if wave['type'] == 'down':
                depths.append(abs(wave['magnitude']))

        return depths

    def get_zigzag_signal(self) -> Dict:
        """
        获取 ZigZag 信号

        Returns:
            包含 ZigZag 信号的字典
        """
        self.calculate_zigzag()
        structure = self.get_wave_structure()

        latest_price = self.df['close'].iloc[-1]
        latest_zigzag = self.df['zigzag'].iloc[-1]

        # 判断当前位置
        if not np.isnan(latest_zigzag):
            if latest_price > latest_zigzag:
                position = 'above_zigzag'
            elif latest_price < latest_zigzag:
                position = 'below_zigzag'
            else:
                position = 'at_zigzag'
        else:
            position = 'between_pivots'

        return {
            'latest_zigzag': latest_zigzag if not np.isnan(latest_zigzag) else None,
            'position': position,
            'trend': structure['trend'],
            'wave_count': structure.get('wave_count', 0),
            'message': structure['message']
        }

    @staticmethod
    def warn_about_limitations() -> str:
        """
        返回 ZigZag 指标的警示信息

        Returns:
            警示信息字符串
        """
        return """
        ⚠️ ZigZag 指标重要警示:
        1. 仅用于盘后分析，严禁用于实时预测
        2. 最新一个转折点可能会随价格变化而重新绘制 (Repainting)
        3. 适合用于识别历史波段结构和 VCP 形态分析
        4. 不可用于实时交易信号生成
        """
