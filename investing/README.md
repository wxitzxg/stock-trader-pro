# Investing 投资策略模块

整合三大投资策略、六大技术指标、五维共振引擎的完整投资分析系统

## 架构

```
investing/
├── __init__.py              # 模块入口，导出统一接口
├── strategies/              # 策略层
│   ├── __init__.py
│   ├── vcp_breakout.py      # VCP 爆发突击策略
│   ├── td_golden_pit.py     # 九转黄金坑策略
│   └── top_divergence.py    # 顶部背离止盈策略
├── indicators/              # 技术指标层
│   ├── __init__.py
│   ├── base_indicators.py   # 基础指标 (MA/EMA/MACD/RSI/布林带等)
│   ├── td_sequential.py     # TD 九转指标
│   ├── vcp_detector.py      # VCP 形态检测
│   ├── divergence_check.py  # 背离检测
│   └── zigzag.py            # ZigZag 趋势指标
└── engines/                 # 引擎层
    ├── __init__.py
    ├── ultimate_engine.py   # 五维共振总控引擎
    └── signal_generator.py  # 买卖信号生成器
```

## 三大策略

| 策略 | 胜率 | 盈亏比 | 适用环境 | 仓位 |
|------|------|--------|----------|------|
| **VCP 爆发突击** | 高 | 大 | 牛市/震荡市强势股 | 50%-70% |
| **九转黄金坑** | 中 | 中 | 下跌趋势末期 | 30%-50% |
| **顶部背离止盈** | - | - | 高位止盈信号 | 减仓/清仓 |

## 五维评分系统

### 评分维度

| 维度 | 分值 | 评估内容 |
|------|------|----------|
| **D1 趋势维** | 20 分 | EMA 多头排列、ZigZag 上升趋势 |
| **D2 形态维** | 30 分 | VCP 形态、布林带收口 |
| **D3 位置维** | 20 分 | 布林带位置、RSI 位置 |
| **D4 动能维** | 10 分 | MACD 背离、成交量确认 |
| **D5 触发维** | 20 分 | 神奇九转、枢轴突破 |

### 决策阈值

| 等级 | 分数 | 决策 | 建议仓位 |
|------|------|------|----------|
| **S 级** | ≥85 | STRONG_BUY | 20% (满仓) |
| **A 级** | ≥65 | BUY | 10% (半仓) |
| **B 级** | ≥40 | HOLD | 5% (观察) |
| **C 级** | <40 | WAIT | 0% (观望) |

## 使用示例

### 基础用法

```python
from investing import (
    UltimateEngine,
    SignalGenerator,
    VCPBreakoutStrategy,
    TDGoldenPitStrategy,
    TopDivergenceStrategy,
)
import pandas as pd

# 准备 OHLCV 数据 (DataFrame, index 为日期)
df = pd.read_csv("stock_data.csv", index_col="date", parse_dates=True)

# 五维共振分析
engine = UltimateEngine(df)
result = engine.evaluate_all()

print(f"总分：{result['total_score']}/100")
print(f"决策：{result['action']}")
print(f"置信度：{result['confidence_level']}级")
print(f"建议仓位：{result['position_suggestion'] * 100:.0f}%")

# 买卖信号生成
signal_gen = SignalGenerator(df)
full_analysis = signal_gen.get_full_analysis()

print(f"买入信号：{full_analysis['buy_signal']}")
print(f"卖出信号：{full_analysis['sell_signal']}")
print(f"最终推荐：{full_analysis['recommendation']}")
```

### 策略分析

```python
# VCP 爆发突击策略
vcp_strategy = VCPBreakoutStrategy(df)
vcp_signal = vcp_strategy.generate_signal()

if vcp_signal:
    print(f"VCP 入场价：¥{vcp_signal['entry_price']:.2f}")
    print(f"VCP 止损价：¥{vcp_signal['stop_loss']:.2f}")
    print(f"VCP 目标价：¥{vcp_signal['target_price']:.2f}")
    print(f"置信度：{vcp_signal['confidence']:.0f}%")

# 九转黄金坑策略
td_strategy = TDGoldenPitStrategy(df)
td_signal = td_strategy.generate_signal()

if td_signal:
    print(f"九转入场价：¥{td_signal['entry_price']:.2f}")
    print(f"九转止损价：¥{td_signal['stop_loss']:.2f}")
    print(f"九转目标价：¥{td_signal['target_price']:.2f}")

# 顶部背离止盈策略
top_strategy = TopDivergenceStrategy(df)
top_signal = top_strategy.generate_signal()

if top_signal:
    print(f"顶部背离建议：{top_signal['suggested_action']}")
    print(f"紧急度：{top_signal['urgency']}")
```

### 技术指标分析

```python
from investing.indicators import (
    BaseIndicators,
    TDSequential,
    VCPDetector,
    DivergenceCheck,
    ZigZag,
)

# 基础指标
base = BaseIndicators(df)
df_with_indicators = base.calculate_all_indicators()
# 包含：MA5/10/20/50/200, EMA, MACD, RSI, 布林带等

# TD 九转
td = TDSequential(df)
td_result = td.get_td_sequential()
print(f"TD 买入信号：{td_result['td_buy_signal']}")
print(f"TD 卖出信号：{td_result['td_sell_signal']}")

# VCP 检测
vcp = VCPDetector(df)
vcp_result = vcp.detect_vcp()
print(f"是否 VCP 形态：{vcp_result['is_vcp']}")
print(f"突破确认：{vcp_result['breakout_detected']}")

# 背离检测
div = DivergenceCheck(df)
div_result = div.detect_all_divergences()
print(f"底背离：{div_result['bullish_divergence']['detected']}")
print(f"顶背离：{div_result['bearish_divergence']['detected']}")

# ZigZag 趋势
zigzag = ZigZag(df)
zigzag_signal = zigzag.get_zigzag_signal()
print(f"当前趋势：{zigzag_signal['trend']}")
```

### 生成分析报告

```python
# 生成人类可读的分析报告
report = engine.generate_report()
print(report)
```

## 策略详细说明

### VCP 爆发突击策略

**入场条件：**
1. 趋势：股价 > EMA50 > EMA200（多头排列）
2. 形态：识别出完整的 VCP 结构（至少 2 次收缩）
3. 状态：布林带极度收口，成交量缩至地量
4. 触发：股价放量（>1.5 倍均量）突破 VCP 枢轴点
5. 确认：MACD 在零轴上方金叉或红柱放大

**操作：** 立即买入 50%-70% 仓位

**止损：** 跌破枢轴点 3% 或 VCP 最低点

### 九转黄金坑策略

**入场条件：**
1. 趋势：短期下跌，但长期趋势向上
2. 位置：股价接近或跌破布林带下轨
3. 信号：TD 九转出现有效低九
4. 确认：RSI 超卖（<30）

**操作：** 分批建仓 30%-50%

**止损：** 低九期间最低价下方 2%

### 顶部背离止盈策略

**触发条件：**
1. 股价创新高但 MACD 未创新高（顶背离）
2. RSI 超买（>70）
3. TD 九转出现高九

**操作：** 减仓或清仓止盈

## 技术指标说明

### 基础指标 (BaseIndicators)

| 指标 | 说明 |
|------|------|
| MA5/10/20/50/200 | 移动平均线 |
| EMA | 指数移动平均线 |
| MACD | 平滑异同移动平均线 |
| RSI | 相对强弱指标 |
| 布林带 | Bollinger Bands（上轨/中轨/下轨/带宽） |
| 成交量比率 | 当日成交量/5 日均量 |

### TD 九转 (TDSequential)

神奇九转指标，用于识别趋势转折点：
- **低九：** 连续 9 根 K 线收盘价低于 4 根前的收盘价，可能见底
- **高九：** 连续 9 根 K 线收盘价高于 4 根前的收盘价，可能见顶

### VCP 检测 (VCPDetector)

识别 Volatility Contraction Pattern（波动收缩形态）：
- 检测至少 2 次逐渐收窄的价格回调
- 识别枢轴点（突破位）
- 判断是否放量突破

### 背离检测 (DivergenceCheck)

识别价格与指标的背离：
- **底背离：** 价格创新低但 MACD/RSI 未创新低
- **顶背离：** 价格创新高但 MACD/RSI 未创新高

### ZigZag

过滤小幅波动，识别主要趋势转折点：
- 默认阈值：5%
- 输出：上升趋势/下降趋势/震荡

## 配置参数

在 `config/settings.py` 中配置：

```python
# 五维评分权重
FIVE_DIMENSION_WEIGHTS = {
    "D1_trend": 20,
    "D2_pattern": 30,
    "D3_position": 20,
    "D4_momentum": 10,
    "D5_trigger": 20,
}

# 决策阈值
DECISION_THRESHOLD = {
    "strong_buy": 85,
    "buy": 65,
    "hold": 40,
}

# 策略参数
STRATEGY_PARAMS = {
    "vcp_min_drops": 2,
    "vcp_max_drops": 4,
    "vcp_min_contraction": 0.5,
    "td_period": 9,
    "zigzag_threshold": 0.05,
}
```

## 与 stockquery 集成

```python
from stockquery import UnifiedStockQueryService
from investing import UltimateEngine

# 获取数据
service = UnifiedStockQueryService()
df = service.get_historical_data("600519")

# 分析
engine = UltimateEngine(df)
result = engine.evaluate_all()
```

## 错误处理

所有方法在数据不足时返回 `None` 或空字典，不会抛出异常。

```python
signal = vcp_strategy.generate_signal()
if signal is None:
    print("无买入信号")
```

## 性能优化建议

1. **批量分析：** 复用 DataFrame，避免重复计算指标
2. **延迟计算：** 指标在首次使用时才计算
3. **数据缓存：** 在应用层缓存历史数据，避免重复请求
