# Realalerts 实时预警模块

整合七大预警规则、仓位管理、动态止损、智能分析的完整风控系统

## 架构

```
realalerts/
├── __init__.py              # 模块入口，导出统一接口
├── engine.py                # 实时预警引擎
├── types.py                 # 预警类型和配置
├── rules/                   # 预警规则层
│   ├── __init__.py
│   ├── cost_alert.py        # 成本百分比预警
│   ├── price_alert.py       # 价格涨跌幅预警
│   ├── volume_alert.py      # 成交量异动预警
│   ├── technical_alert.py   # 技术指标预警
│   └── trailing_stop.py     # 动态止盈止损
├── position/                # 仓位管理层
│   ├── __init__.py
│   ├── position_monitor.py  # 仓位管理 (Kelly 公式)
│   └── stop_loss.py         # 动态止损
├── analysis/                # 智能分析层
│   ├── __init__.py
│   ├── sentiment.py         # 舆情分析
│   └── fund_flow.py         # 资金流向分析
└── scheduler/               # 调度层
    ├── __init__.py
    └── smart_schedule.py    # 智能调度 (北京时间)
```

## 七大预警规则

| 规则 | 预警类型 | 权重 | 说明 |
|------|----------|------|------|
| **CostRule** | 盈利达标/亏损止损 | 3 | 持仓成本涨跌幅 |
| **PriceRule** | 价格突破/日内涨跌 | 1-3 | 固定价格突破，日内涨跌幅 |
| **VolumeRule** | 放量/缩量 | 1-2 | 成交量相对 5 日均量倍数 |
| **TechnicalRule** | MA 金叉/死叉，RSI 超买/超卖，跳空缺口 | 2-3 | 技术指标信号 |
| **TrailingStopRule** | 利润回撤 5%/10% | 2-3 | 动态止盈止损 |

## 预警级别

| 权重 | 级别 | 标识 | 处理建议 |
|------|------|------|----------|
| 3 | 高危 | 🔴 | 立即处理 |
| 2 | 警告 | 🟡 | 密切关注 |
| 1 | 提示 | 🔵 | 保持观察 |

## 使用示例

### 基础用法

```python
from realalerts import (
    RealtimeAlertEngine,
    AlertConfig,
)

# 初始化引擎
engine = RealtimeAlertEngine(total_capital=1000000)

# 配置预警参数
config = AlertConfig(
    cost_pct_above=15.0,    # 盈利 15% 预警
    cost_pct_below=-12.0,   # 亏损 12% 预警
    change_pct_above=4.0,   # 日内大涨 4%
    change_pct_below=-4.0,  # 日内大跌 4%
    volume_surge=2.0,       # 放量 2 倍
    ma_monitor=True,        # 均线监控
    rsi_monitor=True,       # RSI 监控
    gap_monitor=True,       # 跳空监控
    trailing_stop=True,     # 动态止盈
)

# 检查预警
alerts = engine.check(
    code="000001",
    name="平安银行",
    cost=10.5,              # 持仓成本
    price=11.2,             # 当前价格
    data={
        'high': 11.3,
        'low': 10.8,
        'open': 10.9,
        'prev_high': 10.5,
        'prev_low': 10.2,
        'volume': 10000000,
        'ma5_volume': 8000000,
        'change_pct': 2.5,
        'ma5': 11.0,
        'ma10': 10.8,
        'prev_ma5': 10.9,
        'prev_ma10': 10.7,
        'rsi': 55,
    },
    config=config
)

# 处理预警
for alert in alerts:
    print(f"[{alert.weight}] {alert.alert_type}: {alert.message}")
```

### 仓位管理

```python
from realalerts import PositionMonitor

# 初始化仓位管理器
monitor = PositionMonitor(total_capital=1000000)

# 计算建议仓位
suggestion = monitor.calculate_position_size(
    signal_strength='BUY',      # 信号强度：STRONG_BUY/BUY/HOLD
    confidence_score=75,        # 置信度 0-100
    win_rate=0.55,              # 胜率 (可选)
    profit_loss_ratio=2.0       # 盈亏比 (可选)
)

print(f"建议仓位：{suggestion['position_percentage']:.2%}")
print(f"建议金额：¥{suggestion['position_amount']:,.2f}")
print(f"可用资金：¥{suggestion['available_capital']:,.2f}")

# 检查持仓集中度风险
positions = {
    '000001': 0.15,
    '000002': 0.10,
    '000003': 0.08,
}
risk = monitor.check_concentration_risk(positions)
print(f"HHI 指数：{risk['hhi']:.4f}")
print(f"风险等级：{risk['risk_level']}")
print(f"建议：{risk['message']}")
```

### 动态止损

```python
from realalerts import StopLoss

# 初始化管理器
stop_loss = StopLoss()

# 设置 VCP 策略止损
vcp_stop = stop_loss.calculate_vcp_stop_loss(
    pivot_price=20.0,           # 枢轴点价格
    vcp_lowest_price=19.0,      # VCP 最低点
    entry_price=20.5            # 入场价
)
stop_loss.set_stop_loss("000001", vcp_stop, stop_loss_type='vcp')

# 设置 TD 策略止损
td_stop = stop_loss.calculate_td_stop_loss(
    td_lowest_price=18.0,       # 低九期间最低价
    entry_price=18.5            # 入场价
)
stop_loss.set_stop_loss("000002", td_stop, stop_loss_type='td')

# 检查是否触发止损
result = stop_loss.check_stop_loss_triggered(
    stock_code="000001",
    current_price=19.0
)

if result['triggered']:
    print(f"⚠️ {result['message']}")
elif result.get('warning'):
    print(f"⚠️ {result['message']}")
else:
    print(f"✅ {result['message']}")

# 更新移动止损
update_result = stop_loss.update_trailing_stop(
    stock_code="000001",
    current_price=22.0,
    entry_price=20.0,
    ema10=20.5
)
print(f"止损更新：{update_result['updated']}")
print(f"操作：{update_result.get('action', 'N/A')}")
```

### 舆情分析

```python
from realalerts import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# 获取新闻
news_list = analyzer.fetch_news(
    symbol="600519",
    name="贵州茅台",
    limit=5
)

# 情感分析
sentiment = analyzer.analyze_sentiment(news_list)
print(f"正面：{sentiment['positive']} 条")
print(f"负面：{sentiment['negative']} 条")
print(f"中性：{sentiment['neutral']} 条")
print(f"整体：{sentiment['overall']}")

# 生成建议
alerts = [('cost_above', '盈利达标')]
suggestion = analyzer.generate_suggestion(sentiment, alerts)
print(f"智能建议：{suggestion}")
```

### 资金流向分析

```python
from realalerts import FundFlowAnalyzer

analyzer = FundFlowAnalyzer()

# 获取资金流向数据
flow_data = analyzer.fetch_fund_flow(symbol="600519")

# 分析资金流向
analysis = analyzer.analyze_flow(flow_data)
print(f"方向：{analysis['direction']}")
print(f"强度：{analysis['strength']}")
print(f"总结：{analysis['summary']}")

# 生成报告
report = analyzer.generate_flow_report(flow_data)
print(report)
```

### 智能调度

```python
from realalerts import SmartScheduler

# 判断当前是否应该执行监控
result = SmartScheduler.should_run_now()
print(f"执行：{result['run']}")
print(f"模式：{result['mode']}")
print(f"监控范围：{result['stocks']}")
print(f"间隔：{result['interval']}秒")

# 判断是否是交易时间
is_market = SmartScheduler.is_market_hours()
print(f"交易时间：{is_market}")

# 获取下次开盘时间
next_open = SmartScheduler.get_next_market_open()
print(f"下次开盘：{next_open}")
```

### 完整工作流

```python
from realalerts import RealtimeAlertEngine, AlertConfig, SmartScheduler

# 初始化
engine = RealtimeAlertEngine(total_capital=1000000)
config = AlertConfig()

# 智能调度
schedule = SmartScheduler.should_run_now()
if not schedule['run']:
    print("当前不需要监控")
    exit()

# 监控的股票列表
stocks_to_monitor = [
    {"code": "000001", "name": "平安银行", "cost": 10.5},
    {"code": "600519", "name": "贵州茅台", "cost": 1800.0},
]

# 批量检查
for stock in stocks_to_monitor:
    # 获取实时数据 (需要集成 stockquery)
    from stockquery import UnifiedStockQueryService
    service = UnifiedStockQueryService()

    quote = service.get_quote(stock['code'])
    if not quote:
        continue

    # 准备数据
    data = {
        'high': quote.get('high', 0),
        'low': quote.get('low', 0),
        'open': quote.get('open', 0),
        'volume': quote.get('volume', 0),
        'change_pct': quote.get('change_percent', 0),
        # ... 其他数据
    }

    # 检查预警
    alerts = engine.check(
        code=stock['code'],
        name=stock['name'],
        cost=stock['cost'],
        price=quote.get('price', 0),
        data=data,
        config=config
    )

    # 格式化输出
    if alerts:
        formatted = engine.format_alerts(
            code=stock['code'],
            name=stock['name'],
            price=quote.get('price', 0),
            change_pct=quote.get('change_percent', 0),
            cost=stock['cost'],
            alerts=alerts
        )
        print(formatted)

        # 生成深度分析报告
        report = engine.generate_analysis_report(
            code=stock['code'],
            name=stock['name'],
            price=quote.get('price', 0),
            change_pct=quote.get('change_percent', 0),
            alerts=alerts
        )
        print(report)
```

## 预警规则详细说明

### CostRule - 成本百分比预警

**触发条件：**
- 盈利达标：(现价 - 成本) / 成本 × 100% ≥ 15%
- 亏损止损：(现价 - 成本) / 成本 × 100% ≤ -12%

**权重：** 3（高危）

### PriceRule - 价格涨跌幅预警

**触发条件：**
- 日内大涨：change_pct ≥ 4%（权重随涨幅递增）
- 日内大跌：change_pct ≤ -4%（权重随跌幅递增）
- 价格突破：price ≥ price_above（配置值）
- 价格跌破：price ≤ price_below（配置值）

**权重：** 1-3（根据涨跌幅度）

### VolumeRule - 成交量异动预警

**触发条件：**
- 放量：volume / ma5_volume ≥ 2.0
- 缩量：volume / ma5_volume ≤ 0.5

**权重：** 放量 2，缩量 1

### TechnicalRule - 技术指标预警

**触发条件：**
- MA 金叉：MA5 上穿 MA10
- MA 死叉：MA5 下穿 MA10
- RSI 超买：RSI > 70
- RSI 超卖：RSI < 30
- 向上跳空：open > prev_high × 1.01
- 向下跳空：open < prev_low × 0.99

**权重：** 金叉/死叉 3，RSI 2，跳空 2

### TrailingStopRule - 动态止盈止损

**触发条件：**
- 利润回撤 10%：盈利≥10% 后，从最高点回撤≥10% → 清仓
- 利润回撤 5%：盈利≥10% 后，从最高点回撤≥5% → 减仓

**权重：** 回撤 10% 为 3，回撤 5% 为 2

## 智能调度时间表

| 时段 | 时间 (北京时间) | 模式 | 监控范围 | 频率 |
|------|----------------|------|----------|------|
| 交易时段 | 9:30-11:30, 13:00-15:00 | market | 全部股票 | 5 分钟 |
| 午休时段 | 11:30-13:00 | lunch | 全部股票 | 10 分钟 |
| 收盘后 | 15:00-24:00 | after_hours | 全部股票 | 30 分钟 |
| 凌晨时段 | 0:00-9:30 | night | 仅黄金 | 1 小时 |
| 周末 | 周六日 | weekend | 仅黄金 | 1 小时 |

## 配置参数

在 `config/settings.py` 中配置：

```python
# 监控预警配置
MONITOR_CONFIG = {
    "cost_pct_above": 15.0,    # 盈利 15% 预警
    "cost_pct_below": -12.0,   # 亏损 12% 预警
    "change_pct_above": 4.0,   # 日内大涨
    "change_pct_below": -4.0,  # 日内大跌
    "volume_surge": 2.0,       # 放量倍数
    "interval_market": 300,    # 交易时间 5 分钟
    "interval_lunch": 600,     # 午休 10 分钟
    "interval_after_hours": 1800,  # 收盘后 30 分钟
    "interval_night": 3600,    # 凌晨 1 小时
}
```

## 与 stockquery 集成

```python
from stockquery import UnifiedStockQueryService
from realalerts import RealtimeAlertEngine, AlertConfig

service = UnifiedStockQueryService()
engine = RealtimeAlertEngine()
config = AlertConfig()

# 获取数据
quote = service.get_quote("600519")
info = service.get_stock_info("600519")

# 检查预警
alerts = engine.check(
    code="600519",
    name=info['name'],
    cost=1800.0,
    price=quote['price'],
    data=quote,
    config=config
)
```

## 错误处理

所有方法在失败时返回 `None`、空列表或包含 `'error'` 键的字典，不会抛出异常。

```python
flow_data = analyzer.fetch_fund_flow("INVALID")
if 'error' in flow_data:
    print("获取失败")
```

## 性能优化建议

1. **批量查询：** 使用 `get_quotes_batch()` 批量获取行情
2. **防骚扰机制：** 同一预警 30 分钟内不重复触发
3. **按需分析：** 仅在预警触发时才进行舆情和资金流向分析
4. **智能调度：** 根据交易时段自动调整监控频率
