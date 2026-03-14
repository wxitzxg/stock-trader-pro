# Stock Trader Pro - 专业 A 股波段交易系统

> **版本**: v2.7
> **作者**: Stock Trader Pro Team
> **许可**: MIT
> **Python**: 3.9+
> **最后更新**: 2026-03-14

基于 Python 构建的专业级股票量化分析系统，整合技术指标、策略信号、实时行情、智能预警、持仓管理五大核心能力。

---

## 📋 目录

- [安装说明](#-安装说明)
- [快速开始](#-快速开始)
- [核心能力总览](#-核心能力总览)
- [技术分析](#-技术分析)
- [投资策略](#-投资策略)
- [实时行情](#-实时行情)
- [智能预警](#-智能预警)
- [持仓管理](#-持仓管理)
- [收藏管理](#-收藏管理)
- [板块分析](#-板块分析)
- [数据导出](#-数据导出)
- [配置说明](#-配置说明)

---

## 📦 安装说明

### 1. 环境要求

- Python 3.9 或更高版本
- pip 包管理器
- 支持的操作系统：Linux / macOS / Windows (WSL)

### 2. 克隆项目

```bash
# 克隆项目到本地 - 从 Git 仓库下载完整的股票交易系统代码
# 业务目的：获取项目源码，准备本地开发环境
git clone <repository-url> stock-trader-pro
cd stock-trader-pro
```

### 3. 安装依赖

```bash
# 安装项目依赖 - 使用 pip 安装 requirements.txt 中定义的所有 Python 包
# 依赖包括：pandas(数据处理)、numpy(数值计算)、ta(技术指标)、
# sqlalchemy(数据库 ORM)、akshare(股票数据 API)、requests(HTTP 请求)
# 业务目的：准备运行环境，所有第三方库安装完成后才能执行交易分析功能
pip install -r requirements.txt
```

### 4. 初始化数据库

系统使用 SQLite 数据库存储持仓、交易记录、收藏股等数据。首次使用前需要初始化数据库。

**初始化默认数据库：**
```bash
# 初始化 SQLite 数据库 - 创建所有必需的表结构
# 数据表包括：accounts(账户)、positions(持仓)、position_lots(持仓批次)、
# transactions(交易记录)、watchlist(收藏股)、kline_cache(K 线缓存)
# stock_params(股票策略参数)
# 业务目的：首次使用前必须执行，为后续持仓管理、交易记录存储准备数据库
# 输出：✅ 数据库初始化成功：/path/to/storage/investment.db
python3 main.py init-db
```

**输出示例：**
```
✅ 数据库初始化成功：/path/to/stock-trader-pro/data/stock_trader.db
```

**数据库文件位置：**
- 默认位置：`storage/investment.db`
- 可通过修改 `config/settings.py` 中的 `DATABASE_PATH` 自定义路径

**数据库表结构：**
| 表名 | 说明 |
|------|------|
| `accounts` | 账户信息表 |
| `positions` | 持仓表 |
| `position_lots` | 持仓批次表（FIFO 成本核算） |
| `transactions` | 交易记录表 |
| `watchlist` | 收藏股表 |
| `kline_cache` | K 线数据缓存表 |
| `stock_list` | A 股股票列表缓存 |
| `stock_params` | 股票策略参数表 |

**注意事项：**
- 初始化数据库会创建所有必需的表结构
- 已存在的数据库不会被覆盖
- 如需重置数据库，删除 `data/stock_trader.db` 文件后重新执行初始化

### 5. 验证安装

```bash
# 验证安装 - 显示所有可用命令及其参数说明，新用户了解系统功能的入口
# 输出内容：命令列表 (analyze/query/sector/mystocks 等)、参数说明、使用示例
python3 main.py --help
```

### 核心依赖

| 库 | 版本 | 用途 |
|------|------|------|
| pandas | >=2.0.0 | 数据处理核心 |
| numpy | >=1.24.0 | 数值计算 |
| ta | >=0.10.0 | 技术指标库 |
| sqlalchemy | >=2.0.0 | 数据库 ORM |
| akshare | >=1.10.0 | A 股数据获取 |
| requests | >=2.28.0 | HTTP 请求 |
| pyyaml | >=6.0 | 配置管理 |

---

## 🚀 快速开始

```bash
# 1. 查看帮助 - 显示所有可用命令及其参数说明，新用户了解系统功能的入口
python3 main.py --help

# 2. 分析股票（技术分析） - 对贵州茅台 (600519) 进行完整技术分析
# 业务目的：选股决策前评估股票趋势、形态、动能，输出 S/A/B/C 四级建议
# 数据流：调用 AKShare API 获取 250 天 K 线 → 计算 EMA/MACD/RSI/布林带等指标 →
# 五维评分 → 输出操作建议（仓位/止损/目标价）
python3 main.py analyze 600519 --full

# 3. 查询实时行情 - 获取贵州茅台实时股价（新浪 API）
# 业务目的：交易时间查看当前市场价格，用于买入/卖出决策参考
# 数据流：请求新浪行情接口 → 返回股价/涨跌幅/成交量/成交额 → JSON 格式输出
python3 main.py query 600519

# 4. 查看持仓 - 显示当前账户所有持仓股票的盈亏状况
# 业务目的：跟踪持仓表现，查看浮动盈亏、持仓成本、当前市值
# 数据流：读取 SQLite 持仓表 → 获取最新股价 → 计算盈亏 = (现价 - 成本) × 数量
python3 main.py mystocks pos

# 5. 启动智能监控 - 后台运行预警调度器，实时监控持仓和收藏股
# 业务目的：交易时间自动扫描预警条件（大涨/大跌/突破/止损），解放人工盯盘
# 运行模式：交易时段每 5 分钟检查一次，休市后降低频率
python3 main.py smart-monitor
```

---

## 🎯 核心能力总览

| 能力域 | 子能力 | 说明 |
|--------|--------|------|
| **技术分析** | 五维共振评估 | 6 大指标 × 5 维度综合评分系统 |
| **投资策略** | 三大战法 | VCP 爆发/九转黄金坑/顶部背离 |
| **实时行情** | 多源数据 | 新浪 +AKShare+ 东方财富智能路由 |
| **智能预警** | 七大规则 | 成本/价格/成交量/技术/止损实时监控 |
| **持仓管理** | FIFO 核算 | 先进先出成本核算 + 风险分析 |
| **收藏管理** | 标签分类 | 目标价/止损价设置 + 批量监控 |
| **板块分析** | 涨幅排行 | 行业/概念/地域板块数据 |
| **数据导出** | CSV/JSON | 历史 K 线数据导出 |

### 项目架构

```
stock-trader-pro/
├── controllers/     # 命令处理层（View/Controller）
├── services/        # 业务服务层（Service）
├── repositories/    # 数据访问层 + 外部数据源（Repository）
├── models/          # 数据模型层（Model）
├── domain/          # 纯业务规则（预警引擎、分析策略）
├── config/          # 配置文件
├── scripts/         # 工具脚本
└── main.py          # 主入口
```

**架构说明：**
- **controllers/**: 命令行请求处理，参数解析，结果输出
- **services/**: 业务逻辑服务，Facade 模式整合
- **repositories/**: 数据访问抽象，整合 AKShare/新浪财经/东方财富数据源
- **models/**: SQLAlchemy ORM 数据模型
- **domain/**: 纯业务规则（alerting 预警引擎、analysis 分析策略）

---

## 📊 技术分析

### 功能描述

提供基于六大核心指标的五维度综合评分系统，对股票进行全方位技术分析，输出 S/A/B/C 四级决策建议。

### 五维评估体系

| 维度 | 权重 | 核心指标 | 评分标准 |
|------|------|----------|----------|
| **趋势维** | 20 分 | EMA50/200, ZigZag | 多头排列 +10, ZigZag 向上 +10 |
| **形态维** | 30 分 | VCP, 布林带收口 | VCP 突破 +20, 布林收口 +10 |
| **位置维** | 20 分 | 布林带位置，RSI | 超卖区域 +10~20 |
| **动能维** | 10 分 | MACD 背离，成交量 | 底背离 +6, 放量 +4 |
| **触发维** | 20 分 | 神奇九转，枢轴突破 | 有效低九 +10, 突破确认 +10 |

**决策输出**:
- S 级 (≥85 分): STRONG_BUY - 满仓 20%
- A 级 (≥65 分): BUY - 半仓 10%
- B 级 (40-64 分): HOLD - 轻仓观察
- C 级 (<40 分): WAIT - 观望

### 适用场景

- 选股决策前的技术分析
- 持仓股票的定期评估
- 收藏股的批量扫描

### 使用说明

```bash
# 完整分析（所有策略） - 对股票进行五维共振评估 + 三大策略信号分析
# 业务目的：全面技术分析，输出 S/A/B/C 决策建议和具体操作方案
# 评分维度：趋势 (20 分) + 形态 (30 分) + 位置 (20 分) + 动能 (10 分) + 触发 (20 分)
# 策略信号：VCP 爆发突击 + 九转黄金坑 + 顶部背离止盈
python3 main.py analyze 600519 --full

# 指定策略分析 - 仅分析单个策略信号，快速验证特定形态
# --strategy vcp: 检查 VCP 波动收缩形态，识别枢轴突破买点
# --strategy td: 检查神奇九转序列，寻找低九抄底信号
# --strategy divergence: 检查 MACD 背离，识别顶部止盈/底部抄底时机
python3 main.py analyze 600519 --strategy vcp      # 仅 VCP 形态分析
python3 main.py analyze 600519 --strategy td       # 仅九转序列分析
python3 main.py analyze 600519 --strategy divergence  # 仅背离分析

# JSON 格式输出（便于程序处理） - 结构化数据输出，适合集成到其他系统
# 输出字段：score(综合评分), level(等级), action(操作), dimensions(五维得分),
# strategies(策略信号), suggestion(操作建议)
python3 main.py analyze 600519 --json

# 分析收藏股列表 - 批量分析所有收藏股的技术信号，快速筛选买入机会
# 业务目的：同时监控多只关注股票，找出评分最高/信号最强的标的
python3 main.py analyze --watchlist

# 自定义历史数据天数 - 修改分析使用的 K 线数据长度（默认 250 天）
# 使用场景：分析新股上市数据 / 拉长周期看长期趋势
python3 main.py analyze 600519 --days 120
```

### 返回数据格式

**文本输出示例**:
```
═══════════════════════════════════════════════════
  600519 - 贵州茅台 技术分析
═══════════════════════════════════════════════════

【综合评分】85/100 - S 级 (STRONG_BUY)

【五维评分】
  趋势维：18/20 ✅
  形态维：25/30 ✅
  位置维：15/20
  动能维：8/10 ✅
  触发维：19/20 ✅

【策略信号】
  VCP 爆发突击：买入信号 ✅
  九转黄金坑：观察
  顶部背离：无风险 ✅

【操作建议】
  建议仓位：20%
  止损位：¥1455.00
  目标位：¥1800.00
```

**JSON 输出格式**:
```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "score": 85,
  "level": "S",
  "action": "STRONG_BUY",
  "dimensions": {
    "trend": 18,
    "pattern": 25,
    "position": 15,
    "momentum": 8,
    "trigger": 19
  },
  "strategies": {
    "vcp_breakout": {"signal": "BUY", "confidence": 85},
    "td_sequential": {"signal": "HOLD", "confidence": 40},
    "divergence": {"signal": "NONE", "confidence": 0}
  },
  "suggestion": {
    "position": 0.20,
    "stop_loss": 1455.00,
    "target": 1800.00
  }
}
```

---

## 🎯 投资策略

### 功能描述

提供三种核心战法策略：VCP 爆发突击、九转黄金坑、顶部背离止盈，每种策略包含完整的入场条件、操作建议和风险警告。

### 三大战法

#### VCP 爆发突击（胜率最高）

**适用环境**: 牛市或震荡市中的强势股

**入场条件**:
1. ✅ 趋势：股价 > EMA50 > EMA200 (多头排列)
2. ✅ 形态：识别出完整的 VCP 结构 (至少 2 次收缩)
3. ✅ 状态：布林带极度收口，成交量缩至地量
4. ✅ 触发：股价放量 (>1.5 倍均量) 突破 VCP 枢轴点
5. ✅ 确认：MACD 在零轴上方金叉或红柱放大

**操作建议**: 仓位 50%-70%，止损枢轴点下方 3%，目标 20% 涨幅

#### 九转黄金坑（抄底策略）

**适用环境**: 上升趋势中的回调，或箱体震荡

**入场条件**:
1. ✅ 趋势：股价 > EMA60
2. ✅ 位置：触及/跌破布林带下轨
3. ✅ 触发：出现神奇九转"低九"信号
4. ✅ 确认：MACD 底背离

**操作建议**: 仓位 30%-50%，止损"低九"最低价下方 2%，目标 15% 涨幅

#### 顶部背离止盈（风控策略）

**触发条件**: MACD 顶背离、神奇九转"高九"、RSI>80、乖离率过大

**操作建议**: 根据紧急程度减仓 30%-100%

### 适用场景

- 买入决策前的策略确认
- 持仓股票的止盈止损判断
- 策略回测和参数优化

### 使用说明

策略信号集成在 `analyze` 命令中输出，通过 `--strategy` 参数指定单一策略：

```bash
# 仅分析 VCP 策略
python3 main.py analyze 600519 --strategy vcp

# 仅分析九转策略
python3 main.py analyze 600519 --strategy td

# 仅分析背离策略
python3 main.py analyze 600519 --strategy divergence
```

### 返回数据格式

**策略信号输出**:
```
【VCP 爆发突击】
  信号：BUY
  置信度：85%
  建议仓位：70%
  入场价：¥1500.00
  止损价：¥1455.00
  目标价：¥1800.00
  盈亏比：6.67:1
```

---

## 📈 实时行情

### 功能描述

提供多源智能路由的实时行情查询，支持沪深 A 股、ETF 的秒级行情获取。

**数据源优先级**:
| 数据类型 | 主数据源 | 备用源 |
|----------|----------|--------|
| 实时行情 | 新浪财经 | AKShare |
| 历史 K 线 | AKShare | - |
| 股票信息 | 东方财富 | AKShare |
| 资金流向 | AKShare | - |

### 适用场景

- 实时股价查询
- 批量股票估值
- 行情数据获取

### 使用说明

```bash
# 查询单只股票 - 获取实时行情数据（新浪 API，交易时间秒级更新）
# 业务目的：查看当前市场价格，用于即时买卖决策
# 返回数据：price(现价), change_pct(涨跌幅), open/high/low/close, volume(成交量)
python3 main.py query 600519

# 查询多只股票 - 批量获取多只股票实时行情
# 业务目的：同时监控多个目标，比较涨跌幅/成交量等指标
python3 main.py query 600519 000001 300760

# 查询 ETF - 支持 ETF 基金实时行情查询
# 业务目的：查看指数基金/行业 ETF 价格，辅助大盘/板块判断
python3 main.py query 510300
```

### 返回数据格式

**JSON 输出示例**:
```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "price": 1688.00,
  "change_pct": 3.25,
  "open": 1650.00,
  "high": 1695.00,
  "low": 1645.00,
  "close": 1635.00,
  "volume": 1234567
}
```

> 注：所有行情查询命令统一输出 JSON 格式。

---

## 💰 资金流向

### 功能描述

分析单只股票的资金流向数据，包括主力净流入、大单净流入、中单净流入、小单净流入。

### 适用场景

- 判断主力资金态度
- 辅助买卖决策
- 监控大资金动向

### 使用说明

```bash
# 分析单只股票资金流向 - 查看主力资金/大单/中单/小单净流入数据
# 业务目的：判断主力资金态度，辅助买卖决策
# 数据流：AKShare API → 主力净流入 (>100 万), 大单净流入 (50-100 万),
# 中单/小单分类统计
# 返回数据：main_force_in(主力), big_order_in(大单), sentiment(多空情绪)
python3 main.py flow 600519
```

### 返回数据格式

**JSON 输出示例**:
```json
{
  "code": "600519",
  "date": "2026-03-14",
  "data": {
    "main_force_in": 2300.00,
    "big_order_in": 1500.00,
    "medium_order_in": 500.00,
    "small_order_in": 300.00
  },
  "sentiment": "bullish"
}
```

---

## 🔍 股票搜索

### 功能描述

根据关键词搜索股票，支持按代码、名称模糊匹配。使用本地数据库缓存，搜索速度快。

### 适用场景

- 忘记股票代码
- 查找相关股票
- 批量发现股票

### 使用说明

```bash
# 按名称搜索 - 根据股票名称关键词模糊匹配
# 业务目的：忘记股票代码时，通过名称查找代码
# 数据源：本地股票列表缓存（AKShare 全量 A 股列表）
# 返回数据：code(代码), name(名称), price(现价), change_pct(涨跌幅)
python3 main.py search 平安

# 按代码搜索 - 根据代码前缀匹配（如输入 600 查找所有沪市主板股票）
# 使用场景：记得代码前几位，不确定完整代码
python3 main.py search 600

# 更新股票列表缓存（全量） - 从 AKShare 获取最新 A 股完整列表
# 使用场景：新股上市后首次使用，或定期刷新缓存
# 数据流：调用 AKShare 股票列表 API → 写入本地 stock_list 表
python3 main.py update-stock-list --full

# 更新股票列表缓存（增量） - 仅更新已有股票的信息（名称/价格等）
# 使用场景：日常快速更新，不获取新上市股票
python3 main.py update-stock-list --incremental
```

### 返回数据格式

**JSON 输出示例**:
```json
{
  "results": [
    {
      "code": "600000",
      "name": "浦发银行",
      "price": 8.50,
      "change_pct": 1.20
    },
    {
      "code": "000001",
      "name": "平安银行",
      "price": 12.30,
      "change_pct": 2.10
    }
  ],
  "total": 2
}
```

---

## 🚨 智能预警

### 功能描述

基于七大预警规则的智能监控系统，支持交易时段自适应频率控制，分级预警输出。

**七大预警规则**:
| 规则 | 阈值 | 说明 |
|------|------|------|
| 成本盈利 | >15% | 提醒止盈 |
| 成本亏损 | <-12% | 警惕止损 |
| 日内大涨 | >4% | 大涨预警 |
| 日内大跌 | <-4% | 大跌预警 |
| 成交量异动 | >2 倍均量 | 放量预警 |
| 技术指标 | 金叉/死叉/超买/超卖 | MA/RSI 信号 |
| 动态止盈 | 移动止损 | 盈利后自动上移 |

**智能频率控制**:
| 时段 | 频率 | 范围 |
|------|------|------|
| 交易时间 | 5 分钟 | 全部股票 |
| 午休时段 | 10 分钟 | 全部股票 |
| 收盘之后 | 30 分钟 | 全部股票 |
| 凌晨/周末 | 1 小时 | 仅黄金股 |

### 适用场景

- 实时持仓监控
- 自动预警提醒
- 批量股票扫描

### 使用说明

```bash
# 启动智能调度器（持续运行） - 后台 7x24 小时监控预警
# 业务目的：交易时间自动扫描持仓股/收藏股，触发预警条件时输出提醒
# 智能频率：交易时段 5 分钟/次，午休 10 分钟，收盘 30 分钟，凌晨/周末 1 小时
python3 main.py smart-monitor

# 执行一次监控 - 单次执行预警检查，不持续运行
# 使用场景：手动检查当前持仓状态，测试预警规则是否触发
python3 main.py smart-monitor --once

# 指定报告输出目录 - 将监控报告保存到指定文件夹
# 使用场景：定期归档监控记录，便于后续复盘分析
python3 main.py smart-monitor --output-dir ./reports

# 自定义监控间隔（秒） - 修改检查频率（默认根据交易时段自动调整）
# 使用场景：高频监控（如 60 秒）捕捉快速波动，或降低频率减少 API 调用
python3 main.py smart-monitor --interval 180

# 导出 Markdown 报告 - 生成人类可读的监控报告文件
# 输出内容：持仓股列表、各股预警状态、触发规则详情、操作建议
python3 main.py monitor --output report.md

# 只监控持仓股 - 排除收藏股，仅检查当前持有的股票
# 使用场景：已有持仓，不需要监控未买入的收藏股
python3 main.py monitor --no-watchlist

# 只监控收藏股 - 排除持仓股，仅检查关注列表
# 使用场景：空仓观望期，专注于筛选潜在买入机会
python3 main.py monitor --no-position

# 执行一次预警检查（仅收藏股） - 快速检查收藏股是否触发预警
# 与 monitor 区别：alert 只检查收藏股，不读取持仓数据
# 使用场景：快速扫描关注股票，不关心当前持仓
python3 main.py alert

# 定时更新持仓价格（后台运行） - 周期性刷新持仓股的当前价格
# 业务目的：保持持仓数据最新，计算实时盈亏
# 默认间隔：根据交易时段自动调整（交易时间 5 分钟）
python3 main.py update-prices

# 定时更新持仓价格（只执行一次） - 单次刷新，不持续运行
# 使用场景：手动查看持仓前快速更新一次
python3 main.py update-prices --once

# 定时更新持仓价格（指定股票） - 仅更新单只股票价格
# 使用场景：重点监控股，快速刷新特定目标
python3 main.py update-prices --once --stock-code 600519

# 定时更新 K 线数据（后台运行） - 每日 01:00 自动获取最新 K 线
# 业务目的：保持技术分析数据最新，确保分析结果基于最新行情
python3 main.py update-kline

# 定时更新 K 线数据（只执行一次） - 单次手动更新 K 线
# 使用场景：盘后手动获取当日 K 线，或补充历史数据
python3 main.py update-kline --once

# 定时更新 K 线数据（指定股票） - 仅更新单只股票 K 线
# 使用场景：重点股票单独更新，确保分析数据最新
python3 main.py update-kline --once --stock-code 600519
```

### 返回数据格式

**JSON 输出示例** (`smart-monitor --json`, `monitor --json`, `alert --json`):

无预警时:
```json
{
  "report_time": "2026-03-14 11:54:20",
  "market_status": "盘后",
  "summary": {
    "position_count": 5,
    "watchlist_count": 4,
    "total_alerts": 0,
    "high_alerts": 0,
    "medium_alerts": 0,
    "low_alerts": 0
  },
  "positions": [],
  "watchlist": []
}
```

有预警时:
```json
{
  "report_time": "2026-03-14 11:54:20",
  "market_status": "交易时间",
  "summary": {
    "position_count": 5,
    "watchlist_count": 4,
    "total_alerts": 2,
    "high_alerts": 2,
    "medium_alerts": 0,
    "low_alerts": 0
  },
  "positions": [
    {
      "stock_code": "000858",
      "stock_name": "五粮液",
      "quantity": 100,
      "avg_cost": 180.00,
      "current_price": 145.20,
      "profit_loss": -3480.00,
      "profit_rate": -19.33,
      "market_value": 14520.00,
      "alerts": [
        {
          "stock_code": "000858",
          "stock_name": "五粮液",
          "alert_type": "cost_below",
          "alert_level": "高危",
          "message": "亏损 12%",
          "weight": 3
        }
      ],
      "rule_details": [
        {
          "rule_name": "cost_below",
          "rule_type": "成本规则",
          "triggered": true,
          "threshold": "<=-12.0%",
          "current_value": "-19.3%",
          "message": "亏损 19.3%"
        }
      ]
    }
  ],
  "watchlist": []
}
```

**预警检查输出** (`alert --json`):
```json
{
  "watchlist_count": 4,
  "alert_count": 2,
  "alerts": [
    {
      "stock_code": "600519",
      "stock_name": "贵州茅台",
      "price": 1688.00,
      "change_pct": 3.25,
      "alert_type": "cost_above",
      "alert_level": "高危",
      "message": "盈利 18.5%",
      "weight": 3
    },
    {
      "stock_code": "300760",
      "stock_name": "迈瑞医疗",
      "price": 285.00,
      "change_pct": 1.20,
      "alert_type": "pct_up",
      "alert_level": "警告",
      "message": "日内大涨 4.5%",
      "weight": 2
    }
  ]
}
```

> 注：所有监控预警命令统一输出 JSON 格式，包含汇总统计、持仓股详情、收藏股详情、预警规则详情。

---

## 💼 持仓管理

### 功能描述

基于 FIFO（先进先出）算法的持仓管理系统，支持买入/卖出/盈亏分析/风险分析等完整功能。

**核心功能**:
- FIFO 成本核算
- 实现盈亏/浮动盈亏分离
- 持仓集中度分析（HHI 指数）
- 交易历史记录
- 账户管理（现金/资产）

### 适用场景

- 持仓盈亏跟踪
- 交易记录管理
- 资产汇总分析

### 使用说明

```bash
# 查看持仓 - 显示所有持仓股票的成本/现价/盈亏/持仓数量
# 核算方式：FIFO 先进先出算法，多次买入同一股票按批次计算成本
# 输出字段：avg_cost(平均成本), current_price(现价),
# profit_loss(盈亏额), profit_rate(盈亏率)
python3 main.py mystocks pos

# 买入股票 - 记录买入交易，增加持仓数量
# 业务目的：建仓或加仓，系统自动计算持仓成本并记录交易历史
# 参数说明：--qty(股数，100 股=1 手), --price(成交价), --name(股票名称)
# 数据流：创建持仓记录 → 记录交易流水 → 更新账户现金
python3 main.py mystocks buy 600519 --qty 100 --price 1500 --name 贵州茅台

# 卖出股票 - 记录卖出交易，减少持仓数量
# 业务目的：平仓或减仓，FIFO 算法计算已实现盈亏
# 参数说明：--qty(卖出股数), --price(成交价)
# 数据流：减少持仓 → 计算已实现盈亏 → 增加账户现金 → 记录交易流水
python3 main.py mystocks sell 600519 --qty 50 --price 1600

# 资产汇总 - 统计所有持仓的总市值、总成本、总盈亏
# 业务目的：查看整体账户表现，计算持仓集中度 (HHI 指数)
# 输出字段：total_market_value(总市值), total_cost(总成本),
# concentration(集中度分析)
python3 main.py mystocks summary

# 交易历史 - 查看所有交易记录（买入/卖出）
# 业务目的：复盘历史操作，分析交易胜率/盈亏比
# 参数说明：--limit(返回数量，默认 20 条)
python3 main.py mystocks history --limit 50

# 账户总览 - 显示账户完整财务状况
# 输出字段：cash_balance(现金余额), market_value(持仓市值),
# total_assets(总资产), position_ratio(仓位比),
# floating_profit(浮动盈亏), realized_profit(已实现盈亏)
python3 main.py account --summary

# 持仓详情（含仓位比） - 查看各股票持仓占比
# 业务目的：分析仓位分布，避免单一股票风险过于集中
# --refresh 参数：获取最新股价后再计算盈亏
python3 main.py holdings --refresh

# 初始化持仓（从文件导入） - 批量导入已有持仓数据
# 使用场景：首次使用系统，导入券商账户的历史持仓
# --file 参数：JSON/CSV 格式文件路径，包含股票代码/数量/成本
python3 main.py init-position --file positions.json

# 初始化持仓（单只股票模式） - 手动录入单只持仓
# 参数说明：--code(股票代码), --qty(数量), --cost(成本价), --name(名称)
python3 main.py init-position --code 600519 --qty 100 --cost 1500 --name 贵州茅台

# 存入现金 - 向账户充值（模拟银证转账）
# 业务目的：增加可用资金，用于买入股票
# 数据流：增加 cash_balance 字段，不影响持仓
python3 main.py account --deposit 100000

# 取出现金 - 从账户提现（模拟银证转账）
# 业务目的：减少可用资金，模拟资金转出
# 数据流：减少 cash_balance 字段，需余额充足
python3 main.py account --withdraw 50000


### 返回数据格式

**JSON 输出示例** (`mystocks pos --json`):
```json
{
  "positions": [
    {
      "stock_code": "600519",
      "stock_name": "贵州茅台",
      "quantity": 100,
      "avg_cost": 1500.48,
      "current_price": 1688.00,
      "profit_loss": 18752.00,
      "profit_rate": 12.5,
      "market_value": 168800.00
    }
  ],
  "summary": {
    "total_market_value": 168800.00,
    "total_cost": 150048.00,
    "total_profit": 18752.00,
    "profit_rate": 12.5,
    "count": 1
  },
  "concentration": {
    "herfindahl_index": 1.000,
    "top3_concentration": 100.0
  }
}
```

**资产汇总输出** (`mystocks summary --json`):
```json
{
  "total_market_value": 168800.00,
  "total_cost": 150048.00,
  "floating_profit": 18752.00,
  "floating_profit_rate": 12.5,
  "position_count": 1,
  "concentration": {
    "herfindahl_index": 1.000,
    "top3_concentration": 100.0
  }
}
```

**账户总览输出** (`account --summary --json`):
```json
{
  "account_name": "默认账户",
  "cash_balance": 50000.00,
  "market_value": 168800.00,
  "total_assets": 218800.00,
  "position_ratio": 77.15,
  "floating_profit": 18752.00,
  "floating_profit_rate": 12.50,
  "realized_profit": 0.00,
  "total_profit": 18752.00,
  "total_invested": 200048.00
}
```

**持仓详情输出** (`holdings --refresh --json`):
```json
{
  "holdings": [
    {
      "stock_name": "贵州茅台",
      "quantity": 100,
      "current_price": 1688.00,
      "market_value": 168800.00,
      "avg_cost": 1500.00,
      "profit_loss": 18800.00,
      "profit_rate": 12.53,
      "position_ratio": 77.15
    }
  ],
  "summary": {
    "total_market_value": 168800.00,
    "total_cost": 150000.00,
    "total_profit": 18800.00
  }
}
```

---

## 🏷️ 收藏管理

### 功能描述

收藏股管理系统，支持标签分类、目标价/止损价设置、批量监控等功能。

### 适用场景

- 关注股票列表管理
- 批量技术分析
- 价格提醒设置

### 使用说明

```bash
# 查看收藏列表 - 显示所有关注股票的清单及标签
# 业务目的：管理自选股列表，查看目标价/止损价设置
# 输出字段：stock_code(代码), stock_name(名称), tags(标签),
# target_price(目标价), stop_loss(止损价)
python3 main.py watchlist --list

# 添加收藏 - 将股票加入关注列表
# 业务目的：跟踪潜在买入机会，设置价格提醒
# 参数说明：--name(名称，可选), --tags(标签，逗号分隔，用于分类)
python3 main.py watchlist --add 600519 --name 贵州茅台 --tags "白酒，龙头"

# 设置目标价和止损价 - 为收藏股配置价格提醒
# 业务目的：到达目标价位时收到提醒，及时止盈/止损
# 参数说明：--target(目标价), --stop-loss(止损价)
python3 main.py watchlist --add 600519 --target 1800 --stop-loss 1400

# 删除收藏 - 从关注列表移除股票
# 使用场景：不再关注该股票，或已买入转为持仓
python3 main.py watchlist --remove 600519
```

### 返回数据格式

**JSON 输出示例** (`watchlist --list --json`):
```json
{
  "watchlist": [
    {
      "stock_code": "600519",
      "stock_name": "贵州茅台",
      "tags": "白酒，龙头",
      "target_price": 1800.00,
      "stop_loss": 1400.00,
      "notes": "高端白酒龙头"
    },
    {
      "stock_code": "300760",
      "stock_name": "迈瑞医疗",
      "tags": "医疗器械",
      "target_price": 320.00,
      "stop_loss": 250.00,
      "notes": ""
    }
  ],
  "total": 2
}
```

---

## 📊 板块分析

### 功能描述

提供行业板块、概念板块、地域板块的涨幅排行数据。

### 适用场景

- 发现热门板块
- 行业趋势分析
- 选股方向参考

### 使用说明

```bash
# 行业板块排行 - 显示各行业指数涨幅排名
# 业务目的：发现当天热门行业，判断资金流向和板块轮动
# 数据来源：东方财富 API，包含行业名称/涨跌幅/上涨家数/领涨股
python3 main.py sector

# 概念板块排行 - 显示概念题材涨幅排名
# 业务目的：追踪热点题材（如 AI/半导体/新能源），捕捉短线机会
# 与行业区别：概念更灵活，跨行业主题分类
python3 main.py sector --concept

# 地域板块排行 - 显示各省市区域板块涨幅
# 业务目的：分析区域经济发展，捕捉地方政策利好
python3 main.py sector --region

# 指定返回数量 - 控制输出排名数量（默认 50 个）
# 使用场景：只看头部热门板块，减少输出信息量
python3 main.py sector --limit 20
```

### 返回数据格式

**JSON 输出示例** (`sector --json`):
```json
{
  "sectors": [
    {
      "name": "白酒行业",
      "change_pct": 5.23,
      "up_count": 15,
      "down_count": 3,
      "top_stock": "贵州茅台",
      "top_stock_change": 6.8
    }
  ],
  "total": 1
}
```

---

## 📁 数据导出

### 功能描述

导出历史 K 线数据，支持 CSV/JSON 格式。

### 适用场景

- 数据备份
- 离线分析
- 第三方工具导入

### 使用说明

```bash
# 导出 CSV 格式（默认 60 天） - 导出历史 K 线数据到 CSV 文件
# 业务目的：数据备份/离线分析/导入第三方工具（Excel/同花顺等）
# 输出列：date(日期), open(开盘), high(最高), low(最低),
# close(收盘), volume(成交量), amount(成交额)
# 数据源：AKShare API，前复权数据
python3 main.py export 600519

# 导出 JSON 格式 - JSON 结构化输出，适合程序处理
# 使用场景：集成到其他 Python 脚本/数据分析系统
python3 main.py export 600519 --format json

# 指定获取天数 - 修改导出历史数据长度（默认 60 天）
# 使用场景：分析长期趋势需要更多历史数据
python3 main.py export 600519 --days 120

# 指定输出文件 - 自定义输出文件名和路径
# 使用场景：批量导出时区分不同股票/不同时间段
python3 main.py export 600519 -o custom_output.csv
```

### 返回数据格式

**CSV 格式**:
```csv
date,open,high,low,close,volume,amount
2026-03-12,1680.00,1695.00,1675.00,1688.00,1234567,2087654321
2026-03-11,1670.00,1685.00,1665.00,1680.00,1100000,1845000000
```

**JSON 格式**:
```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "data": [
    {"date": "2026-03-12", "open": 1680, "high": 1695, "low": 1675, "close": 1688, "volume": 1234567, "amount": 2087654321}
  ]
}
```

---

## 🔧 参数管理

### 功能描述

管理每支股票的独立策略参数，支持 VCP、ZigZag、TD Sequential 等指标的个性化配置。

### 适用场景

- 为不同股票设置不同的策略参数
- 查看当前生效的参数配置
- 恢复默认参数

### 使用说明

```bash
# 列出所有配置了参数的股票 - 查看哪些股票有自定义策略参数
# 业务目的：检查参数配置情况，管理个性化设置
python3 main.py params list

# 获取某股票的参数配置 - 查看特定股票的所有参数值
# 业务目的：确认当前生效的参数，或复制到其他股票
# 返回内容：VCP 参数、ZigZag 参数、TD Sequential 参数、RSI/MACD 参数
python3 main.py params get --symbol 600519

# 设置股票参数 - 为特定股票配置个性化策略参数
# 业务目的：不同股票波动特性不同，需要调整参数适配
# 参数格式：key=value 形式，支持 vcp/zigzag/td/rsi/macd/divergence
# 示例：vcp.min_drops=3 表示 VCP 至少检测 3 次回调
python3 main.py params set --symbol 600519 --name 贵州茅台 \
  --params "vcp.min_drops=3,zigzag.threshold=0.08,td.period=9"

# 查看默认参数 - 显示系统全局默认参数配置
# 业务目的：了解未配置参数的股票使用的默认值
# 参数类别：vcp(形态), zigzag(之字转向), td(九转),
# rsi(相对强弱), macd(指数平滑), divergence(背离)
python3 main.py params defaults

# 删除股票参数配置（恢复默认） - 清除自定义参数，使用系统默认值
# 使用场景：参数效果不佳，重置回标准配置
python3 main.py params remove --symbol 600519
```

**支持的参数类型**:
- `vcp.*` - VCP 形态参数 (min_drops, max_drops, min_contraction)
- `zigzag.*` - ZigZag 参数 (threshold)
- `td.*` - 神奇九转参数 (period, compare_period)
- `rsi.*` - RSI 参数 (period, overbought, oversold)
- `macd.*` - MACD 参数 (fast, slow, signal)
- `divergence.*` - 背离检测参数 (window)

### 返回数据格式

**列出股票输出** (`params list`):
```
已配置 3 只股票:

  600519 - 贵州茅台
    备注：白酒龙头
  300760 - 迈瑞医疗
  000858 - 五粮液
```

**获取参数输出** (`params get`):
```
股票 600519 参数配置:

名称：贵州茅台
备注：白酒龙头

VCP 参数:
{
  "min_drops": 3,
  "max_drops": 4,
  "min_contraction": 0.4
}

ZigZag 参数:
{
  "threshold": 0.08
}

TD Sequential 参数:
{
  "period": 9,
  "compare_period": 4
}
```

**设置参数输出** (`params set`):
```
✅ 已更新股票 600519 参数配置

设置的参数:
  vcp.min_drops = 3
  zigzag.threshold = 0.08
  名称：贵州茅台
  备注：白酒龙头
```

**默认参数输出** (`params defaults`):
```
默认参数配置:

{
  "vcp": {"min_drops": 2, "max_drops": 4, "min_contraction": 0.5},
  "zigzag": {"threshold": 0.05},
  "td": {"period": 9, "compare_period": 4},
  ...
}
```

---

## ⚙️ 配置说明

### 配置文件位置

| 文件 | 说明 |
|------|------|
| `config/settings.py` | 主配置文件 |
| `config/stock_params.json` | 股票特定参数 |
| `config/monitor_report_template.md` | 监控报告模版 |

### 主要配置项

**策略参数**:
```python
STRATEGY_PARAMS = {
    'vcp': {'min_contraction': 0.05, 'max_pullbacks': 4},
    'td': {'td_period': 9},
}
```

**五维评分权重**:
```python
FIVE_DIMENSION_WEIGHTS = {
    'D1': 20, 'D2': 30, 'D3': 20, 'D4': 10, 'D5': 20,
}
```

**监控预警配置**:
```python
MONITOR_CONFIG = {
    'cost_pct_above': 15.0,    # 盈利预警阈值
    'cost_pct_below': -12.0,   # 亏损预警阈值
    'change_pct_above': 4.0,   # 大涨预警阈值
    'interval_market': 300,    # 交易时间监控间隔（秒）
}
```

**交易手续费**:
```python
TRADING_FEES = {
    'commission': 0.0003,   # 佣金万分之三
    'stamp_tax': 0.001,     # 印花税千分之一
}
```

---

## 📝 版本历史

完整的版本历史记录请参阅 [CHANGELOG.md](CHANGELOG.md)。

### v2.7 (MVC Architecture Refactor) - 2026-03-14
- ✅ 完成 MVC 架构重构 - controllers/services/repositories/models/domain 五层分离
- ✅ 整合数据源到 Repository 层（AKShare/新浪财经/东方财富）
- ✅ 删除废弃的 domain/portfolio/{models,services,repositories}/ 目录
- ✅ 删除废弃的 infrastructure/ 目录
- ✅ 统一导入路径，提升代码可维护性

### v2.6 (Documentation Update) - 2026-03-14
- ✅ 删除券商交割单支持功能
- ✅ 优化文档结构，添加安装说明

### v2.5 (Trading Day Scheduler) - 2026-03-13
- ✅ 交易日判断功能 - 周末和法定节假日不执行预警
- ✅ 支持 2026 年 A 股法定节假日配置

---

*最后更新：2026-03-14 (v2.7)*
