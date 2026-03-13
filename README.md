# Stock Trader Pro v2.5

专业的股票技术分析交易系统，整合技术指标分析、持仓管理、实时行情、板块排行、资金流向分析、智能预警监控等功能。

## 📊 核心功能

### 技术分析模块
- ✅ **五维共振分析** - 趋势、形态、位置、动能、触发五维度评分
- ✅ **VCP 爆发突击策略** - 波动收缩形态识别
- ✅ **九转黄金坑策略** - TD Sequential 九转序列
- ✅ **顶部背离止盈策略** -  divergence 背离检测
- ✅ **多策略共振** - 策略信号综合判断

### 实时行情模块 (整合自 stock-pro)
- ✅ **实时股票行情** - 使用新浪财经 API 获取个股实时数据
- ✅ **板块涨幅排行** - 基于东方财富网数据的行业/概念板块排行
- ✅ **历史 K 线数据** - 使用 AKShare 获取 A 股历史交易数据
- ✅ **资金流向分析** - 主力资金、大单、中单、小单净流入数据
- ✅ **股票搜索功能** - 支持代码或名称模糊匹配搜索
- ✅ **数据导出功能** - 支持 CSV/JSON 格式导出历史数据

### 智能预警监控 (整合自 stock-monitor-pro-2.1.0)
- ✅ **七大预警规则** - 成本百分比/涨跌幅/成交量/均线/RSI/跳空/动态止盈
- ✅ **智能频率控制** - 基于北京时间的动态监控频率
- ✅ **后台常驻进程** - 7x24 小时自动监控
- ✅ **分级预警** - 紧急级/警告级/提醒级三级预警
- ✅ **防骚扰机制** - 同类预警 30 分钟内不重复

### 交易管理模块
- ✅ **持仓管理** - 买入/卖出/持仓查看
- ✅ **收藏股管理** - 添加/删除/标签管理
- ✅ **信号监控** - 监控收藏股技术信号
- ✅ **仓位管理** - Kelly 公式仓位控制
- ✅ **止损管理** - 移动止损、成本价止损

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install pandas numpy ta sqlalchemy akshare requests matplotlib pyyaml python-json-logger
```

### 2. 初始化数据库

```bash
python main.py init-db
```

### 3. 使用命令

#### 技术分析

```bash
# 分析单只股票
python main.py analyze 600519

# 完整分析（所有策略）
python main.py analyze 600519 --full

# 指定策略分析
python main.py analyze 600519 --strategy vcp

# JSON 格式输出
python main.py analyze 600519 --json

# 分析收藏股列表
python main.py analyze --watchlist
```

#### 实时行情

```bash
# 查询单只股票
python main.py query 600519

# 查询多只股票
python main.py query 600519 000001 300750
```

#### 板块排行

```bash
# 行业板块排行（默认）
python main.py sector

# 概念板块排行
python main.py sector --concept

# 地域板块排行
python main.py sector --region

# 指定返回数量
python main.py sector --limit 30
```

#### 资金流向

```bash
# 查询个股资金流向
python main.py flow 600519
```

#### 股票搜索

```bash
# 按名称搜索
python main.py search 平安

# 按代码搜索
python main.py search 600519
```

#### 数据导出

```bash
# 导出 CSV 格式（默认 60 天）
python main.py export 600519

# 导出 120 天数据
python main.py export 600519 --days 120

# 导出 JSON 格式
python main.py export 600519 --format json

# 指定输出文件
python main.py export 600519 -o my_data.csv
```

#### 持仓管理

```bash
# 查看持仓
python main.py portfolio --list

# 买入
python main.py portfolio --buy --symbol 600519 --qty 100 --price 1500.00 --name 贵州茅台

# 卖出
python main.py portfolio --sell --symbol 600519 --qty 50 --price 1600.00
```

#### 收藏股管理

```bash
# 查看收藏股
python main.py watchlist --list

# 添加收藏股
python main.py watchlist --add 600519 --name 贵州茅台 --tags 白酒，龙头

# 删除收藏股
python main.py watchlist --remove 600519
```

#### 信号监控

```bash
# 监控收藏股信号
python main.py monitor
```

#### 智能预警 (新增)

```bash
# 执行一次预警检查
python main.py alert

# 启动后台监控 (7x24 小时)
python main.py daemon
```

## 📋 命令参考

| 命令 | 说明 | 数据源 |
|------|------|--------|
| `analyze` | 股票技术分析 | AKShare |
| `query` | 实时行情查询 | 新浪财经 |
| `sector` | 板块涨幅排行 | 东方财富 |
| `flow` | 资金流向分析 | AKShare |
| `search` | 股票搜索 | AKShare |
| `export` | 数据导出 | AKShare |
| `portfolio` | 持仓管理 | 本地数据库 |
| `watchlist` | 收藏股管理 | 本地数据库 |
| `monitor` | 信号监控 | AKShare |
| `alert` | 智能预警检查 | 新浪+AKShare |
| `daemon` | 后台监控进程 | 新浪+AKShare |
| `init-db` | 初始化数据库 | - |

## 🗂️ 目录结构

```
stock-trader-pro/
├── main.py                      # 主入口
├── commands/                    # CLI 命令处理
│   ├── analyze.py               # 股票技术分析
│   ├── portfolio.py             # 持仓管理
│   ├── watchlist.py             # 收藏股管理
│   ├── monitor.py               # 信号监控
│   ├── alert.py                 # 智能预警
│   ├── query.py                 # 实时行情查询
│   ├── sector.py                # 板块排行
│   ├── flow.py                  # 资金流向
│   ├── search.py                # 股票搜索
│   └── export.py                # 数据导出
├── investing/                   # 投资策略 (核心)
│   ├── engines/                 # 分析引擎
│   │   ├── ultimate_engine.py   # 五维共振总控引擎
│   │   └── signal_generator.py  # 买卖信号生成器
│   ├── strategies/              # 策略实现
│   │   ├── vcp_breakout.py      # VCP 爆发突击
│   │   ├── td_golden_pit.py     # 九转黄金坑
│   │   └── top_divergence.py    # 顶部背离止盈
│   └── indicators/              # 技术指标
│       ├── base_indicators.py   # 基础指标
│       ├── td_sequential.py     # 神奇九转
│       ├── vcp_detector.py      # VCP 形态识别
│       ├── divergence_check.py  # MACD 背离检测
│       └── zigzag.py            # ZigZag 之字转向
├── mystocks/                    # 持仓/收藏管理
│   ├── models/                  # 数据模型
│   ├── services/                # 业务服务
│   └── storage/                 # 数据存储
├── realalerts/                  # 智能预警监控
│   ├── engine.py                # 预警引擎
│   ├── rules/                   # 预警规则
│   ├── position/                # 仓位管理
│   ├── analysis/                # 智能分析
│   └── scheduler/               # 智能调度
├── stockquery/                  # 股票查询服务
│   ├── sources/                 # 数据源
│   │   ├── akshare_source.py    # AKShare
│   │   ├── sina_source.py       # 新浪财经
│   │   └── eastmoney_source.py  # 东方财富
│   └── unified_service.py       # 统一服务
├── config/                      # 配置文件
│   ├── settings.py              # 统一配置
│   └── monitor_report_template.md  # 监控报告模版
├── utils/                       # 工具函数
│   └── helpers.py               # 通用工具
└── storage/                     # 运行数据
    ├── investment.db            # SQLite 数据库
    └── stock-trader.log         # 日志文件
```

## 📈 数据源

| 功能 | API | 说明 |
|------|-----|------|
| 技术分析 | AKShare | A 股历史 K 线数据 (前复权) |
| 实时行情 | 新浪 API | 实时行情数据，稳定可靠 |
| 板块排行 | 东方财富 API | 行业/概念板块涨幅排名 |
| 资金流向 | AKShare | 主力/大单/中单/小单净流入 |

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `INVEST_DB_PATH` | 数据库路径 | `storage/investment.db` |
| `INVEST_LOG_LEVEL` | 日志级别 | `INFO` |

### 策略参数

在 `config/settings.py` 中可以配置：
- 均线参数（MA5/20/50/200）
- RSI 参数（周期、超买/超卖阈值）
- 布林带参数（周期、标准差）
- MACD 参数（快线、慢线、信号线）
- VCP 参数（回调次数、收缩比例）
- 仓位管理参数（单只最大仓位、Kelly 系数）

## ⚠️ 注意事项

### 数据获取超时
检查网络连接，API 可能需要几秒钟响应。

### 股票代码
使用正确的 6 位 A 股代码：
- 沪市：600xxx, 601xxx, 603xxx
- 深市：000xxx, 002xxx, 300xxx

### 数据延迟
- 新浪实时行情：基本实时
- 东方财富板块：约 15 分钟延迟
- AKShare 历史数据：T+1 更新

### 合规提醒
所有数据和分析仅供参考，不构成投资建议。用户应自行承担投资风险。

## 💡 版本特性

### v2.1 (realalerts Integration) - 2026-03-11
- **整合 stock-monitor-pro-2.1.0**: 智能预警监控系统
- **新增 alert 命令**: 执行一次智能预警检查
- **新增 daemon 命令**: 后台常驻监控进程 (7x24 小时)
- **七大预警规则**: 成本百分比/涨跌幅/成交量/均线/RSI/跳空/动态止盈
- **智能频率控制**: 基于北京时间的动态监控频率
- **分级预警**: 紧急级/警告级/提醒级三级预警
- **智能分析引擎**: 舆情分析 + 资金流向关联分析
- **新增 realalerts/ 模块**:
  - `engine.py` - 预警引擎
  - `rules/` - 七大预警规则
  - `position/` - 仓位监控和止损
  - `analysis/` - 智能分析引擎
  - `scheduler/` - 智能调度器
- **重构目录结构**:
  - `core/` → `investing/engines/`
  - `strategies/` → `investing/strategies/`
  - `indicators/` → `investing/indicators/`
  - `portfolio/` → `mystocks/`
  - `risk/` → 合并到 `realalerts/`
  - `monitor/` → 合并到 `realalerts/`
  - `data/` → `stockquery/`
  - `scripts/utils/` → `stockquery/sources/`

### v2.0 (Integration Edition) - 2026-03-11
- **整合 stock-pro 功能**: 实时行情、板块排行、资金流向、股票搜索、数据导出
- **新增 query 命令**: 使用新浪 API 快速查询实时行情
- **新增 sector 命令**: 东方财富行业/概念板块排行
- **新增 flow 命令**: 个股资金流向分析
- **新增 search 命令**: 股票搜索功能
- **新增 export 命令**: 历史数据导出 CSV/JSON
- **新增三大数据源 API 封装**:
  - `stockquery/sources/sina_source.py` - 新浪财经 API
  - `stockquery/sources/eastmoney.py` - 东方财富 API
  - `stockquery/sources/akshare.py` - AKShare 增强版

### v1.0
- 五维共振分析引擎
- VCP/九转/顶部背离三大策略
- 持仓管理和收藏股管理
- 信号监控和预警
