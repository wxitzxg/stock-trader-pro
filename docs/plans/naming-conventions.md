# Python 命名规范

> **版本**: v1.0
> **最后更新**: 2026-03-14
> **适用范围**: Stock Trader Pro 项目

本文档定义了 Stock Trader Pro 项目中所有 Python 代码的命名规范。所有新代码必须遵循此规范，现有代码在修改时应逐步向规范靠拢。

---

## 目录

1. [命名规范总则](#命名规范总则)
2. [业务领域命名映射](#业务领域命名映射)
3. [各模块命名审查结果](#各模块命名审查结果)
4. [常见问题解答](#常见问题解答)

---

## 命名规范总则

### 1. 类命名（Class Names）

**规则**: 使用大驼峰命名法（UpperCamelCase/PascalCase）

**业务语义**: 类名应体现其业务职责

**示例**:
```python
# 服务层类
class UnifiedStockQueryService:  # 统一股票查询服务
class AccountService:            # 账户服务
class PortfolioService:          # 持仓服务
class WatchlistService:          # 收藏股服务

# 数据仓库类
class PositionRepository:        # 持仓数据仓库
class AccountRepository:         # 账户数据仓库

# 数据模型类
class Account:                   # 账户
class Position:                  # 持仓
class Transaction:               # 交易记录
class Watchlist:                 # 收藏股

# 策略类
class VCPBreakoutStrategy:       # VCP 爆发突击策略
class TDGoldenPitStrategy:       # 九转黄金坑策略
class TopDivergenceStrategy:     # 顶部背离策略

# 引擎类
class UltimateEngine:            # 五维共振总控引擎
class SignalGenerator:           # 买卖信号生成器
class RealtimeAlertEngine:       # 实时预警引擎
```

### 2. 函数命名（Function Names）

**规则**: 使用蛇形命名法（snake_case）

**业务语义**: 动词 + 名词结构，清晰表达操作意图

**示例**:
```python
# 数据获取类
def get_quote() -> dict:                    # 获取实时行情
def get_historical_data() -> DataFrame:     # 获取历史数据
def get_stock_info() -> dict:               # 获取股票信息
def get_fund_flow() -> dict:                # 获取资金流向

# 业务操作类
def analyze_stock(symbol: str) -> dict:     # 分析股票
def format_analysis_report(result: dict) -> str:  # 格式化分析报告
def generate_buy_signal() -> dict:          # 生成买入信号
def calculate_stop_loss() -> float:         # 计算止损价
def check_entry_conditions() -> dict:       # 检查入场条件

# 命令处理类
def cmd_analyze(args):                      # analyze 命令处理
def cmd_portfolio(args):                    # portfolio 命令处理
def cmd_watchlist(args):                    # watchlist 命令处理
```

### 3. 变量命名（Variable Names）

**规则**: 使用蛇形命名法（snake_case）

**业务语义**: 名称应清晰表达变量用途

**示例**:
```python
# 股票标识
symbol          # 股票代码（6 位数字）
stock_code      # 股票代码（同 symbol）
stock_name      # 股票名称

# 价格相关
current_price   # 当前价格
latest_price    # 最新价格
entry_price     # 入场价
stop_loss       # 止损价
target_price    # 目标价
avg_cost        # 平均成本价

# 盈亏相关
profit_loss     # 盈亏金额
profit_rate     # 盈亏比例
realized_profit # 已实现盈亏

# 数量相关
position_quantity   # 持仓数量
total_capital       # 总资金
position_size       # 仓位金额

# 状态标识
is_trading_day      # 是否交易日
market_status       # 市场状态
signal_strength     # 信号强度
confidence_score    # 置信度分数
```

### 4. 常量命名（Constant Names）

**规则**: 全大写，单词间用下划线分隔（SCREAMING_SNAKE_CASE）

**示例**:
```python
# 配置常量
DATABASE_PATH = "/path/to/database.db"
SIGNAL_THRESHOLD = 0.7
MONITOR_CONFIG = {...}

# 业务常量
FIVE_DIMENSION_WEIGHTS = {
    'D1': 20,  # 趋势维
    'D2': 30,  # 形态维
    'D3': 20,  # 位置维
    'D4': 10,  # 动能维
    'D5': 20,  # 触发维
}

DECISION_THRESHOLD = {
    'strong_buy': 85,
    'buy': 65,
    'hold': 40,
}

TRADING_FEES = {
    'stamp_duty': 0.001,      # 印花税
    'exchange_fee': 0.00002,  # 交易所规费
    'broker_commission': 0.0003,  # 券商佣金
    'min_commission': 5.0,    # 最低佣金
}
```

### 5. 私有成员命名（Private Members）

**规则**: 单下划线前缀（`_internal_method`）

**示例**:
```python
class BaseIndicators:
    def _validate_data(self):           # 验证数据格式
    def _calculate_adx(self):           # 计算 ADX 指标
    def _get_ma_trend(self) -> str:     # 获取均线趋势

_default_service: Optional[UnifiedStockQueryService]  # 默认服务实例
_position_repo: PositionRepository      # 持仓数据仓库
```

---

## 业务领域命名映射

### 技术分析域（Technical Analysis）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 分析 | `analyze` / `analysis` | `analyze_stock()`, `technical_analysis` |
| 指标 | `indicator` | `BaseIndicators`, `calculate_indicators()` |
| 信号 | `signal` | `SignalGenerator`, `generate_signal()` |
| 评估 | `evaluate` / `evaluation` | `evaluate_all()`, `engine_result` |
| 评分 | `score` | `total_score`, `dimension_score` |
| 维度 | `dimension` | `dimension_scores`, `dimension_details` |

### 投资策略域（Investment Strategy）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 策略 | `strategy` | `VCPBreakoutStrategy`, `TDGoldenPitStrategy` |
| 战法 | `strategy` (统一用语) | VCP 爆发突击 → `VCPBreakoutStrategy` |
| 入场 | `entry` | `entry_price`, `entry_condition` |
| 止损 | `stop_loss` | `stop_loss_price`, `calculate_stop_loss()` |
| 目标价 | `target` | `target_price`, `target_return` |
| 置信度 | `confidence` | `confidence_level`, `confidence_score` |
| 盈亏比 | `risk_reward_ratio` | `risk_reward_ratio` |

### 实时行情域（Real-time Quote）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 行情 | `quote` | `QuoteData`, `get_quote()` |
| 实时 | `realtime` / `real_time` | `realtime_quote`, `real_time_data` |
| 历史数据 | `historical` | `get_historical_data()`, `historical_kline` |
| 资金流向 | `fund_flow` | `FundFlowAnalyzer`, `get_fund_flow()` |
| 板块 | `sector` | `SectorData`, `get_sector_rank()` |

### 智能预警域（Smart Alert）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 预警/警报 | `alert` | `AlertEngine`, `generate_alert()` |
| 监控 | `monitor` | `MonitorService`, `monitor_stock()` |
| 调度 | `scheduler` | `MonitorScheduler`, `schedule_job()` |
| 规则 | `rule` | `CostRule`, `PriceRule`, `TechnicalRule` |
| 阈值 | `threshold` | `price_threshold`, `volume_threshold` |

### 持仓管理域（Position Management）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 持仓 | `position` | `PositionService`, `get_position()` |
| 账户 | `account` | `AccountService`, `get_account()` |
| 交易 | `transaction` / `trade` | `TransactionService`, `record_transaction()` |
| 买入 | `buy` | `buy_stock()`, `buy_order` |
| 卖出 | `sell` | `sell_stock()`, `sell_order` |
| 盈亏 | `profit_loss` | `calculate_profit_loss()`, `profit_loss_rate` |
| 仓位 | `position_ratio` | `position_ratio`, `position_weight` |
| 批次 | `lot` | `PositionLot`, `get_lots()` |

### 收藏管理域（Watchlist Management）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 收藏股 | `watchlist` | `WatchlistService`, `add_to_watchlist()` |
| 标签 | `tag` | `stock_tags`, `tag_manager` |
| 目标价 | `target_price` | `target_price` |
| 止损价 | `stop_loss` | `stop_loss` |

### 数据仓库域（Repository Pattern）

| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 仓库 | `repository` / `repo` | `PositionRepository`, `WatchlistRepo` |
| 服务 | `service` | `PositionService`, `AccountService` |
| 模型 | `model` | `Position`, `Account`, `Transaction` |

---

## 各模块命名审查结果

### ✅ investing/ (投资策略引擎)

| 文件 | 类/函数 | 状态 |
|------|---------|------|
| `ultimate_engine.py` | `UltimateEngine` | ✅ 符合规范 |
| `signal_generator.py` | `SignalGenerator` | ✅ 符合规范 |
| `base_indicators.py` | `BaseIndicators` | ✅ 符合规范 |
| `vcp_detector.py` | `VCPDetector` | ✅ 符合规范 |
| `td_sequential.py` | `TDSequential` | ✅ 符合规范 |
| `divergence_check.py` | `DivergenceCheck` | ✅ 符合规范 |
| `zigzag.py` | `ZigZag` | ✅ 符合规范 |
| `vcp_breakout.py` | `VCPBreakoutStrategy` | ✅ 符合规范 |
| `td_golden_pit.py` | `TDGoldenPitStrategy` | ✅ 符合规范 |
| `top_divergence.py` | `TopDivergenceStrategy` | ✅ 符合规范 |

### ✅ stockquery/ (股票查询服务)

| 文件 | 类/函数 | 状态 |
|------|---------|------|
| `unified_service.py` | `UnifiedStockQueryService` | ✅ 符合规范 |
| `models.py` | `QuoteData`, `StockInfo`, `FundFlowSummary`, `SectorData` | ✅ 符合规范 |
| `akshare_source.py` | `AKShareDataSource` | ✅ 符合规范 |
| `eastmoney_source.py` | `EastmoneyDataSource` | ✅ 符合规范 |
| `sina_source.py` | `SinaDataSource` | ✅ 符合规范 |

### ✅ mystocks/ (持仓管理模块)

| 目录 | 类/函数 | 状态 |
|------|---------|------|
| `models/` | `Account`, `Position`, `PositionLot`, `Transaction`, `Watchlist` | ✅ 符合规范 |
| `services/` | `AccountService`, `PortfolioService`, `WatchlistService` | ✅ 符合规范 |
| `storage/repositories/` | `AccountRepository`, `PositionRepository`, `WatchlistRepository` | ✅ 符合规范 |

### ✅ realalerts/ (智能预警模块)

| 文件 | 类/函数 | 状态 |
|------|---------|------|
| `engine.py` | `RealtimeAlertEngine` | ✅ 符合规范 |
| `rules/cost_alert.py` | `CostRule` | ✅ 符合规范 |
| `rules/price_alert.py` | `PriceRule` | ✅ 符合规范 |
| `rules/volume_alert.py` | `VolumeRule` | ✅ 符合规范 |
| `rules/technical_alert.py` | `TechnicalRule` | ✅ 符合规范 |
| `rules/trailing_stop.py` | `TrailingStopRule` | ✅ 符合规范 |
| `position/position_monitor.py` | `PositionMonitor` | ✅ 符合规范 |
| `position/stop_loss.py` | `StopLoss` | ✅ 符合规范 |
| `scheduler/monitor_scheduler.py` | `MonitorScheduler` | ✅ 符合规范 |
| `scheduler/smart_schedule.py` | `SmartScheduler` | ✅ 符合规范 |

### ✅ commands/ (CLI 命令)

| 文件 | 函数 | 状态 |
|------|------|------|
| `analyze.py` | `cmd_analyze()`, `analyze_stock()`, `format_analysis_report()` | ✅ 符合规范 |
| `portfolio.py` | `cmd_portfolio()`, `format_positions_json()` | ✅ 符合规范 |
| `watchlist.py` | `cmd_watchlist()`, `format_watchlist_json()` | ✅ 符合规范 |
| `monitor.py` | `cmd_monitor()`, `format_monitor_json()` | ✅ 符合规范 |
| `alert.py` | `cmd_alert()` | ✅ 符合规范 |
| `query.py` | `cmd_query()` | ✅ 符合规范 |
| `sector.py` | `cmd_sector()` | ✅ 符合规范 |
| `flow.py` | `cmd_flow()` | ✅ 符合规范 |
| `search.py` | `cmd_search()` | ✅ 符合规范 |
| `export.py` | `cmd_export()` | ✅ 符合规范 |

---

## 常见问题解答

### Q: 为什么类名使用大驼峰而不是其他命名方式？

A: 大驼峰命名（PascalCase）是 Python PEP 8 官方推荐的类命名约定，与内置类（如 `Exception`, `dict`, `list`）保持一致。

### Q: 为什么函数名使用蛇形命名而不是小驼峰？

A: 蛇形命名（snake_case）是 Python PEP 8 官方推荐的函数和方法命名约定，具有良好的可读性。

### Q: 缩写词应该如何处理？

A:
- 类名中的缩写词：全部大写，如 `VCPDetector`, `TDSequential`, `AKShareDataSource`
- 函数名中的缩写词：全部小写，如 `get_quote()`, `calculate_kelly_position()`

### Q: 私有方法和公有方法如何区分？

A: 私有方法使用单下划线前缀（`_internal_method`），但这只是约定，不会阻止外部访问。双下划线（`__private`）会触发名称修饰，一般不推荐。

### Q: 常量必须全部大写吗？

A: 模块级常量应该全部大写，这是 Python 社区的通用约定。类内部的常量可以使用类属性方式定义，命名遵循一般属性规则。

---

*本文档由命名规范审查自动生成，最后审查日期：2026-03-14*
