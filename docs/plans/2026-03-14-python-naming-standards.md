# Python 命名规范实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 统一项目中所有函数、类、变量的命名规范，使其符合 Python PEP 8 标准并体现业务场景语义

**Architecture:** 基于业务领域（技术分析、投资策略、实时行情、智能预警、持仓管理）建立命名规范，对现有代码进行审查和重构

**Tech Stack:** Python 3.9+, 遵循 PEP 8 命名规范

---

## 命名规范总则

### 1. 类命名（Class Names）
- **规则**: 使用大驼峰命名法（UpperCamelCase/PascalCase）
- **业务语义**: 类名应体现其业务职责
- **示例**:
  - `UnifiedStockQueryService` (统一股票查询服务)
  - `SignalGenerator` (信号生成器)
  - `SmartScheduler` (智能调度器)
  - `WatchlistService` (收藏股管理服务)
  - `PositionRepository` (持仓数据仓库)

### 2. 函数命名（Function Names）
- **规则**: 使用蛇形命名法（snake_case）
- **业务语义**: 动词 + 名词结构，清晰表达操作意图
- **示例**:
  - `analyze_stock()` (分析股票)
  - `get_historical_data()` (获取历史数据)
  - `generate_buy_signal()` (生成买入信号)
  - `calculate_stop_loss()` (计算止损价)
  - `format_analysis_report()` (格式化分析报告)

### 3. 变量命名（Variable Names）
- **规则**: 使用蛇形命名法（snake_case）
- **业务语义**: 名称应清晰表达变量用途
- **示例**:
  - `symbol` / `stock_code` (股票代码)
  - `current_price` / `latest_price` (当前价格)
  - `profit_loss` (盈亏金额)
  - `profit_rate` (盈亏比例)
  - `position_quantity` (持仓数量)

### 4. 常量命名（Constant Names）
- **规则**: 全大写，单词间用下划线分隔（SCREAMING_SNAKE_CASE）
- **示例**:
  - `DATABASE_PATH` (数据库路径)
  - `SIGNAL_THRESHOLD` (信号阈值)
  - `MONITOR_CONFIG` (监控配置)

### 5. 私有成员命名（Private Members）
- **规则**: 单下划线前缀（`_internal_method`）
- **示例**:
  - `_calculate_stop_loss()` (内部计算方法)
  - `_default_service` (默认服务实例)

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

### 投资策略域（Investment Strategy）
| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 策略 | `strategy` | `VCPBreakoutStrategy`, `TDGoldenPitStrategy` |
| 战法 | `strategy` (统一用语) | `VCP 爆发突击` → `VCPBreakoutStrategy` |
| 入场 | `entry` | `entry_price`, `entry_condition` |
| 止损 | `stop_loss` | `stop_loss_price`, `calculate_stop_loss()` |
| 目标价 | `target` | `target_price`, `target_return` |
| 置信度 | `confidence` | `confidence_level`, `confidence_score` |

### 实时行情域（Real-time Quote）
| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 行情 | `quote` | `QuoteData`, `get_quote()` |
| 实时 | `realtime` / `real_time` | `realtime_quote`, `real_time_data` |
| 历史数据 | `historical` | `get_historical_data()`, `historical_kline` |
| 资金流向 | `fund_flow` | `FundFlowAnalysis`, `get_fund_flow()` |
| 板块 | `sector` | `SectorData`, `get_sector_rank()` |

### 智能预警域（Smart Alert）
| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 预警/警报 | `alert` | `AlertService`, `generate_alert()` |
| 监控 | `monitor` | `MonitorService`, `monitor_stock()` |
| 调度 | `scheduler` | `SmartScheduler`, `schedule_job()` |
| 规则 | `rule` | `AlertRule`, `price_alert_rule` |
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

### 收藏管理域（Watchlist Management）
| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 收藏股 | `watchlist` | `WatchlistService`, `add_to_watchlist()` |
| 标签 | `tag` | `stock_tags`, `tag_manager` |

### 数据仓库域（Repository Pattern）
| 中文 | 英文规范 | 示例 |
|------|----------|------|
| 仓库 | `repository` / `repo` | `PositionRepository`, `WatchlistRepo` |
| 服务 | `service` | `PositionService`, `AccountService` |
| 模型 | `model` | `Position`, `Account`, `Transaction` |

---

## 文件组织结构

### 当前项目结构
```
stock-trader-pro/
├── commands/              # CLI 命令处理
│   ├── analyze.py         # analyze 命令
│   ├── portfolio.py       # portfolio 命令
│   ├── watchlist.py       # watchlist 命令
│   ├── monitor.py         # monitor 命令
│   ├── alert.py           # alert 命令
│   ├── query.py           # query 命令
│   ├── sector.py          # sector 命令
│   ├── flow.py            # flow 命令
│   ├── search.py          # search 命令
│   ├── export.py          # export 命令
│   ├── params.py          # params 命令
│   ├── account.py         # account 命令
│   ├── update_prices.py   # update_prices 命令
│   ├── update_kline.py    # update_kline 命令
│   ├── smart_monitor.py   # smart_monitor 命令
│   └── update_stock_list.py # update_stock_list 命令
├── common/                # 通用工具
│   └── trading_time.py    # 交易时间工具
├── config/                # 配置管理
│   ├── settings.py        # 主配置
│   ├── params_loader.py   # 参数加载
│   └── trading_calendar.py # 交易日历
├── investing/             # 投资策略引擎
│   ├── engines/           # 分析引擎
│   │   ├── ultimate_engine.py
│   │   └── signal_generator.py
│   ├── indicators/        # 技术指标
│   │   ├── base_indicators.py
│   │   ├── vcp_detector.py
│   │   ├── td_sequential.py
│   │   ├── divergence_check.py
│   │   └── zigzag.py
│   └── strategies/        # 策略实现
│       ├── vcp_breakout.py
│       ├── td_golden_pit.py
│       └── top_divergence.py
├── mystocks/              # 持仓管理模块
│   ├── models/            # 数据模型
│   │   ├── account.py
│   │   ├── position.py
│   │   ├── transaction.py
│   │   ├── watchlist.py
│   │   └── kline.py
│   ├── services/          # 业务服务
│   │   ├── account_service.py
│   │   ├── portfolio_service.py
│   │   └── watchlist_service.py
│   └── storage/           # 数据存储
│       ├── repositories/  # 数据仓库
│       │   ├── account_repo.py
│       │   ├── position_repo.py
│       │   └── watchlist_repo.py
│       └── database.py    # 数据库连接
├── realalerts/            # 智能预警模块
│   ├── analysis/          # 分析引擎
│   │   ├── fund_flow.py
│   │   └── sentiment.py
│   ├── position/          # 持仓监控
│   │   ├── position_monitor.py
│   │   └── stop_loss.py
│   ├── rules/             # 预警规则
│   │   ├── cost_alert.py
│   │   ├── price_alert.py
│   │   ├── technical_alert.py
│   │   ├── trailing_stop.py
│   │   └── volume_alert.py
│   ├── scheduler/         # 调度器
│   │   ├── smart_schedule.py
│   │   └── monitor_scheduler.py
│   └── engine.py          # 预警引擎
├── stockquery/            # 股票查询服务
│   ├── sources/           # 数据源
│   │   ├── akshare_source.py
│   │   ├── eastmoney_source.py
│   │   └── sina_source.py
│   ├── models.py          # 数据模型
│   └── unified_service.py # 统一服务
├── main.py                # 主入口
└── SKILL.md               # 项目文档
```

---

## 任务列表

### Task 1: 核心技术域命名审查

**Files:**
- `investing/engines/ultimate_engine.py`
- `investing/engines/signal_generator.py`
- `investing/indicators/base_indicators.py`

- [ ] **Step 1: 审查 UltimateEngine 类命名**
  - 检查类名 `UltimateEngine` 是否符合业务语义
  - 检查方法命名：`evaluate_all()`, `generate_report()`
  - 确认变量命名：`dimension_details`, `total_score`

- [ ] **Step 2: 审查 SignalGenerator 类命名**
  - 检查方法命名：`generate_buy_signal()`, `generate_sell_signal()`
  - 检查私有方法：`_calculate_stop_loss()`, `_calculate_target_price()`
  - 确认符合蛇形命名法

- [ ] **Step 3: 审查指标模块命名**
  - 检查 `VCPDetector`, `TDSequential`, `DivergenceCheck`, `ZigZag` 类名
  - 确保使用大驼峰命名法

---

### Task 2: 数据服务域命名审查

**Files:**
- `stockquery/unified_service.py`
- `stockquery/sources/akshare_source.py`
- `stockquery/sources/eastmoney_source.py`
- `stockquery/sources/sina_source.py`

- [ ] **Step 1: 审查 UnifiedStockQueryService 命名**
  - 服务类名符合 `XxxService` 模式
  - 方法命名：`get_quote()`, `get_historical_data()`, `get_stock_info()`
  - 确认符合 `get_xxx()` 动宾结构

- [ ] **Step 2: 审查数据源类命名**
  - `AKShareDataSource`, `EastmoneyDataSource`, `SinaDataSource`
  - 统一使用 `XxxDataSource` 模式

- [ ] **Step 3: 审查模型命名**
  - `UnifiedStockData`, `QuoteData`, `StockInfo`, `FundFlowSummary`, `SectorData`
  - 数据模型使用大驼峰命名

---

### Task 3: 持仓管理域命名审查

**Files:**
- `mystocks/models/`
- `mystocks/services/`
- `mystocks/storage/repositories/`

- [ ] **Step 1: 审查模型类命名**
  - `Account`, `Position`, `PositionLot`, `Transaction`, `Watchlist`, `Kline`
  - 确认使用大驼峰命名法

- [ ] **Step 2: 审查服务类命名**
  - `AccountService`, `PortfolioService`, `WatchlistService`
  - 统一 `XxxService` 模式
  - 方法命名：`get_all()`, `create()`, `update()`, `delete()`

- [ ] **Step 3: 审查仓库类命名**
  - `AccountRepository`, `PositionRepository`, `WatchlistRepository`
  - 统一 `XxxRepository` 模式

---

### Task 4: 预警监控域命名审查

**Files:**
- `realalerts/engine.py`
- `realalerts/scheduler/smart_schedule.py`
- `realalerts/rules/*.py`
- `realalerts/position/*.py`

- [ ] **Step 1: 审查 SmartScheduler 命名**
  - 类名符合业务语义
  - 方法命名：`get_interval()`, `is_trading_day()`, `should_run_now()`

- [ ] **Step 2: 审查预警规则命名**
  - `CostAlert`, `PriceAlert`, `TechnicalAlert`, `TrailingStop`, `VolumeAlert`
  - 统一 `XxxAlert` 或 `XxxRule` 模式

- [ ] **Step 3: 审查监控相关方法**
  - `monitor_positions()`, `check_alerts()`, `generate_report()`

---

### Task 5: CLI 命令域命名审查

**Files:**
- `commands/*.py`
- `main.py`

- [ ] **Step 1: 审查命令处理函数命名**
  - 统一使用 `cmd_xxx` 前缀：`cmd_analyze`, `cmd_portfolio`, `cmd_watchlist`
  - 确认符合蛇形命名法

- [ ] **Step 2: 审查业务函数命名**
  - `analyze_stock()`, `format_analysis_report()`, `analyze_watchlist()`
  - 动宾结构，语义清晰

---

### Task 6: 创建命名规范文档

**Files:**
- Create: `docs/coding-standards/naming-conventions.md`

- [ ] **Step 1: 编写命名规范文档**
  - 记录所有命名约定
  - 包含业务术语映射表
  - 提供代码示例

- [ ] **Step 2: 更新 SKILL.md 文档**
  - 在适当位置引用命名规范

---

## 执行检查点

完成每个 Task 后：
1. 运行 `python3 -m py_compile` 验证语法
2. 运行相关测试确保功能正常
3. 提交 git commit

---

## 验证命令

```bash
# 验证 Python 语法
python3 -m py_compile main.py
python3 -m py_compile commands/analyze.py
# ... 对其他文件执行

# 运行测试（如果有）
python3 -m pytest tests/ -v

# 检查命名规范（使用 pylint）
pylint --enable=C0103 commands/analyze.py
```

---

*计划创建日期：2026-03-14*
