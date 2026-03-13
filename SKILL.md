# Stock Trader Pro - 专业 A 股波段交易系统 v2.5

> 基于 Python 构建的专业级股票量化分析系统，整合技术指标、策略信号、实时行情、智能预警、持仓管理五大核心能力

---

## 🎯 核心能力总览

| 能力域 | 子能力 | 说明 |
|--------|--------|------|
| **技术分析** | 五维共振评估 | 6 大指标 × 5 维度综合评分系统 |
| **策略信号** | 三大战法 | VCP 爆发/九转黄金坑/顶部背离 |
| **实时行情** | 多源数据 | 新浪 +AKShare+ 东方财富智能路由 |
| **智能预警** | 七大规则 | 成本/价格/成交量/技术/止损实时监控 |
| **持仓管理** | FIFO 核算 | 先进先出成本核算 + 风险分析 |
| **收藏管理** | 标签分类 | 目标价/止损价设置 + 批量监控 |
| **板块分析** | 涨幅排行 | 行业/概念/地域板块数据 |
| **资金流向** | 主力监控 | 主力/大单/中单/小单净流入 |
| **数据导出** | CSV/JSON | 历史 K 线数据导出 |
| **智能调度** | 北京时间 | 交易时段自适应频率控制 |
| **配置中心** | 统一配置 | 监控间隔/报告模版/输出位置可配置 |

---

## 📊 能力一：技术分析引擎

### 1.1 五维共振评估系统

基于六大核心指标的五维度综合评分系统，满分 100 分：

| 维度 | 角色 | 核心指标 | 权重 | 评分标准 |
|------|------|----------|------|----------|
| **D1 趋势维** | 过滤器 | EMA50/200, ZigZag | 20 分 | 多头排列 +10, ZigZag 向上 +10 |
| **D2 形态维** | 结构师 | VCP, 布林带收口 | 30 分 | VCP 突破 +20, 布林收口 +10 |
| **D3 位置维** | 定位器 | 布林带位置，RSI | 20 分 | 超卖区域 +10~20 |
| **D4 动能维** | 测谎仪 | MACD 背离，成交量 | 10 分 | 底背离 +6, 放量 +4 |
| **D5 触发维** | 发令枪 | 神奇九转，枢轴突破 | 20 分 | 有效低九 +10, 突破确认 +10 |

**决策输出:**
```
S 级 (≥85 分): STRONG_BUY - 满仓 20%
A 级 (≥65 分): BUY - 半仓 10%
B 级 (40-64 分): HOLD - 轻仓观察
C 级 (<40 分): WAIT - 观望
```

### 1.2 六大核心技术指标

#### 1.2.1 神奇九转 (TD Sequential)
- **低九信号**: 连续 9 日收盘价 < 4 日前收盘价 → 下跌衰竭，买入信号
- **高九信号**: 连续 9 日收盘价 > 4 日前收盘价 → 上涨衰竭，卖出信号
- **有效性判断**: 仅当趋势向上且位置超卖时，低九才有效
- **应用场景**: 九转黄金坑策略核心触发条件

#### 1.2.2 VCP 形态识别 (核心中的核心)
- **形态检测**: 自动识别 2-4 次回调，幅度递减 (如 -20% → -10% → -5%)
- **成交量分析**: 回调时成交量逐级萎缩
- **枢轴点识别**: 自动标记最后一次回调的高点 (Pivot)
- **突破确认**: 股价放量 (>1.5 倍均量) 突破枢轴点
- **应用场景**: VCP 爆发突击策略核心条件

#### 1.2.3 MACD 背离检测
- **底背离**: 股价创新低但 MACD 未创新低 → 买入信号
- **顶背离**: 股价创新高但 MACD 未创新高 → 卖出信号
- **强度分级**: 弱背离/标准背离/强背离
- **应用场景**: 顶部背离止盈策略、九转黄金坑确认

#### 1.2.4 布林带 (Bollinger Bands)
- **收口检测**: 带宽创近期新低，预示大变盘
- **位置判断**: 下轨支撑/上轨压力/中轨趋势
- **超卖超买**: 触及下轨 + 低九 = 黄金坑；突破上轨 = 主升浪
- **带宽分位数**: 计算带宽历史分位数，判断极度收口

#### 1.2.5 RSI 相对强弱指标
- **超买区**: RSI > 70，警惕回调风险
- **超卖区**: RSI < 30，可能反弹机会
- **中性区**: RSI 45-55，趋势不明
- **分水岭**: RSI > 55 趋势转强确认

#### 1.2.6 ZigZag 之字转向
- **噪音过滤**: 过滤小幅波动，连接显著高低点
- **趋势判断**: 识别上升/下降/震荡趋势
- **复盘专用**: ⚠️ 仅用于盘后分析，严禁实时预测
- **波段结构**: 识别波段高低点，辅助趋势判断

### 1.3 基础技术指标

- **均线系统**: MA5/10/20/50/200, EMA50/200
- **成交量指标**: 量比、成交量比率 (VR)
- **MACD**: DIF/DEA/金叉死叉/零轴位置
- **布林带**: 上轨/中轨/下轨/带宽位置

---

## 🎯 能力二：投资策略系统

### 2.1 战法 A: VCP 爆发突击 (胜率最高)

**适用环境**: 牛市或震荡市中的强势股

**入场条件 (五重确认)**:
1. ✅ 趋势：股价 > EMA50 > EMA200 (多头排列)
2. ✅ 形态：识别出完整的 VCP 结构 (至少 2 次收缩)
3. ✅ 状态：布林带极度收口，成交量缩至地量
4. ✅ 触发：股价放量 (>1.5 倍均量) 突破 VCP 枢轴点
5. ✅ 确认：MACD 在零轴上方金叉或红柱放大

**操作建议**:
- 仓位：50%-70% (根据置信度调整)
- 止损：枢轴点下方 3% 或 VCP 最低点
- 目标：20% 涨幅
- 盈亏比：通常 > 3:1

**信号强度分级**:
- 置信度≥80%: 重仓 (70%)
- 置信度 60-80%: 中仓 (50%)
- 置信度<60%: 轻仓 (30%)

### 2.2 战法 B: 九转黄金坑 (抄底策略)

**适用环境**: 上升趋势中的回调，或箱体震荡

**入场条件 (核心条件必须满足)**:
1. ✅ 趋势：股价 > EMA60 (长期趋势未坏)
2. ✅ 位置：股价触及/跌破布林带下轨
3. ✅ 触发：出现神奇九转"低九"信号
4. ✅ 确认：MACD 出现底背离 (绿柱缩短)
5. ✅ 超卖：RSI < 30 (增强信号)

**操作建议**:
- 仓位：30%-50% (抄底策略相对保守)
- 止损："低九"期间最低价下方 2%
- 目标：15% 涨幅
- 盈亏比：通常 2:1 以上

**核心条件**: 趋势、布林下轨、低九 必须同时满足

### 2.3 战法 C: 顶部背离止盈 (风控策略)

**适用环境**: 任何市场环境

**触发条件 (任一即可)**:
1. ⚠️ MACD 顶背离：股价创新高但 MACD 未创新高
2. ⚠️ 神奇九转"高九"信号
3. ⚠️ RSI > 80 (极度超买)
4. ⚠️ 股价远离布林带上轨 > 5% (乖离率过大)

**操作建议**:
- 紧急程度分级：IMMEDIATE(立即)/HIGH(高)/MODERATE(中)/LOW(低)
- 减仓比例：30%-100% (根据紧急程度)
- 移动止盈：获利 10% 后止盈上移至成本价，之后沿 EMA10/布林中轨移动

**风险警告**:
- 双强卖出信号 (2 个 STRONG_SELL): 立即清仓
- 单强卖出信号：减仓 70%
- 普通警告：减仓 30%-50%

### 2.4 策略信号输出格式

```json
{
  "strategy": "VCP_BREAKOUT",
  "action": "BUY",
  "symbol": "600519",
  "quantity": 700,
  "entry_price": 1500.00,
  "stop_loss": 1455.00,
  "target_price": 1800.00,
  "position_size": 105000,
  "confidence": 85.0,
  "risk_reward_ratio": 6.67,
  "conditions": { ... },
  "generated_at": "2026-03-12 10:30:00"
}
```

---

## 📈 能力三：实时行情系统

### 3.1 多源数据智能路由

| 数据类型 | 主数据源 | 备用源 | 路由策略 |
|----------|----------|--------|----------|
| 实时行情 | 新浪财经 | AKShare | 新浪优先，故障自动切换 |
| 历史 K 线 | AKShare | - | 唯一数据源，支持前复权 |
| 股票信息 | 东方财富 | AKShare | 东财优先 |
| 资金流向 | AKShare | - | 唯一数据源 |
| 板块排行 | 东方财富 | AKShare | 东财优先 |
| 股票搜索 | AKShare | - | 唯一数据源 |

### 3.2 实时行情数据

**获取字段**:
- 当前价、涨跌幅、涨跌额
- 开盘价、最高价、最低价、昨收价
- 成交量、成交额
- 买一至买五、卖一至卖五

**数据特点**:
- 毫秒级延迟
- 自动识别沪深市场 (sh/sz)
- 故障转移机制

### 3.3 历史 K 线数据

**支持周期**: 日线/周线/月线

**复权类型**: 前复权 (qfq)/后复权 (hfq)/不复权

**数据字段**:
```
日期、开盘、最高、最低、收盘、成交量、成交额
```

**数据质量**:
- 自动校验数据完整性
- 支持自定义时间范围
- 默认 250 个交易日 (约 1 年)

### 3.4 板块涨幅排行

**支持板块类型**:
- 行业板块 (37 个)
- 概念板块 (100+ 个)
- 地域板块 (31 个)

**输出数据**:
- 板块名称、涨跌幅
- 上涨家数、下跌家数
- 领涨股名称、涨跌幅

### 3.5 资金流向分析

**监控指标**:
- 主力净流入 (万元)
- 大单净流入 (万元)
- 中单净流入 (万元)
- 小单净流入 (万元)
- 主力占比、大单占比

**预警意义**:
- 主力持续流入 → 关注机会
- 主力大幅流出 → 警惕风险
- 背离分析：股价涨但主力流出 → 谨慎

### 3.6 股票搜索功能

**搜索方式**:
- 按代码搜索 (精确/模糊)
- 按名称搜索 (模糊匹配)
- 按拼音首字母搜索

**返回结果**:
- 股票代码、名称
- 市场类型 (沪深/港美股)
- 当前价格、涨跌幅

---

## 🚨 能力四：智能预警监控系统

### 4.1 七大预警规则

#### 4.1.1 成本百分比预警
- **盈利预警**: 盈利 > 15% → 提醒止盈
- **亏损预警**: 亏损 > 12% → 警惕止损
- **可配置阈值**: 支持自定义百分比

#### 4.1.2 价格涨跌幅预警
- **大涨预警**: 日内涨幅 > 4% (个股) / > 2% (ETF)
- **大跌预警**: 日内跌幅 > 4% (个股) / > 2% (ETF)
- **可配置阈值**: 支持自定义涨跌幅

#### 4.1.3 成交量异动预警
- **放量预警**: 成交量 > 2 倍均量
- **缩量预警**: 成交量 < 0.5 倍均量
- **天量预警**: 成交量创近期新高

#### 4.1.4 技术指标预警
- **均线金叉**: MA5 上穿 MA10 → 买入信号
- **均线死叉**: MA5 下穿 MA10 → 卖出信号
- **RSI 超买**: RSI > 70 → 警惕回调
- **RSI 超卖**: RSI < 30 → 关注反弹
- **跳空缺口**: 向上/向下跳空 > 1%

#### 4.1.5 动态止盈止损
- **盈利 10% 后**: 止盈上移至成本价
- **盈利 20% 后**: 沿 EMA10 移动止盈
- **VCP 止损**: 枢轴点下方 3%
- **九转止损**: 低九最低价下方 2%

### 4.2 智能频率控制 (基于北京时间)

| 时段 | 时间范围 | 监控频率 | 监控范围 |
|------|----------|----------|----------|
| **交易时间** | 9:30-11:30, 13:00-15:00 | 每 5 分钟 | 全部股票 |
| **午休时段** | 11:30-13:00 | 每 10 分钟 | 全部股票 |
| **收盘之后** | 15:00-24:00 | 每 30 分钟 | 全部股票 |
| **凌晨时段** | 0:00-9:30 | 每 1 小时 | 仅黄金 |
| **周末** | 周六、周日 | 每 1 小时 | 仅黄金 |

**智能调度器功能**:
- `should_run_now()`: 判断当前是否应该执行监控
- `is_market_hours()`: 判断是否是 A 股交易时间
- `get_next_market_open()`: 计算下次开盘时间

### 4.3 分级预警机制

| 级别 | 触发条件 | 标识 | 响应 |
|------|----------|------|------|
| **紧急级** | ≥3 个条件或权重≥5 | 🔴 高危 | 立即处理 |
| **警告级** | 2 个条件或权重≥3 | 🟡 警告 | 尽快处理 |
| **提醒级** | 单一条件触发 | 🔵 提示 | 关注即可 |

### 4.4 防骚扰机制

- **同类预警 30 分钟内不重复**
- **预警去重**: 相同预警类型自动合并
- **冷静期设置**: 可配置冷静期时长

### 4.5 智能分析报告

**报告内容**:
1. 价格异动分析
2. 舆情分析 (新闻抓取 + 情感分析)
3. 资金流向分析
4. 智能操作建议

**报告格式**:
```
📊 贵州茅台 (600519) 深度分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 价格异动:
• 当前：¥1688.00 (+3.25%)
• 触发：成交量异动、RSI 超买

📰 舆情分析 (正面):
• 最近新闻：15 条
• 正面：12 | 负面：3

💰 资金流向:
• 主力净流入：+2.3 亿元
• 大单净流入：+8000 万元

💡 智能建议:
建议减仓 30%，警惕技术性回调
```

---

## 💼 能力五：持仓管理系统

### 5.0 持仓初始化

**功能概述**: 支持批量导入已有持仓，适用于首次使用系统时导入历史持仓数据。

**支持的导入方式**:

| 方式 | 命令 | 说明 |
|------|------|------|
| 单只手动 | `mystocks init --code ...` | 手动输入单只持仓信息 |
| JSON/CSV | `mystocks init --file ...` | 从 JSON/CSV 文件批量导入 |
| 券商交割单 | `mystocks init --broker-file ...` | 从券商导出的交割单导入 |

**导入模式**:
- **overwrite (覆盖)**: 已存在持仓时，覆盖原有数据
- **add (累加)**: 已存在持仓时，累加到原有持仓（类似买入）

**JSON 格式示例**:
```json
[
  {
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "quantity": 100,
    "avg_cost": 1500.00,
    "current_price": 1520.00,
    "purchase_date": "2025-12-01"
  },
  {
    "stock_code": "300760",
    "stock_name": "迈瑞医疗",
    "quantity": 200,
    "avg_cost": 280.50,
    "current_price": 285.00
  }
]
```

**CSV 格式示例**:
```csv
stock_code,stock_name,quantity,avg_cost,current_price,purchase_date
600519，贵州茅台，100,1500.00,1520.00,2025-12-01
300760，迈瑞医疗，200,280.50,285.00,2025-11-15
```

**券商交割单支持**:
- 华泰证券（含涨乐财富通）
- 中信证券
- 国泰君安（含君弘）
- 东方财富
- 其他券商（通用解析器自动匹配列名）

**Python API**:
```python
from mystocks import MyStocks

with MyStocks() as ms:
    # 单只初始化
    position = ms.initialize_position(
        stock_code="600519",
        stock_name="贵州茅台",
        quantity=100,
        avg_cost=1500.0,
        current_price=1520.0,
        mode="overwrite"  # 或 "add"
    )

    # 从 JSON 文件导入
    positions = ms.initialize_positions_from_file(
        file_path="positions.json",
        file_format="json",
        mode="overwrite"
    )

    # 从券商交割单导入
    positions = ms.initialize_from_broker_statement(
        file_path="huatai_statement.csv",
        broker="auto",  # 自动检测券商
        mode="overwrite"
    )
```

### 5.1 FIFO 成本核算

**核算原理**: 先进先出 (First In, First Out)

**核算内容**:
- 买入批次管理
- 卖出时自动匹配最早批次
- 精确计算每股成本
- 实现盈亏/浮动盈亏分离

**交易历史**:
- 完整的买卖记录
- 交易时间、价格、数量
- 交易手续费
- 备注信息

### 5.2 持仓分析

**实时数据**:
- 持仓数量、持仓成本
- 当前价格、市值
- 浮动盈亏、盈亏率
- 实现盈亏 (已卖出部分)

**持仓汇总**:
- 总市值、总成本
- 总浮动盈亏、总实现盈亏
- 持仓数量统计

### 5.3 风险分析

#### 5.3.1 持仓集中度分析
- **前三大持仓占比**: 预警过度集中
- **最大单一持仓占比**: 控制在 20% 以内
- **HHI 赫芬达尔指数**: 衡量集中度 (0-1)
  - HHI < 0.1: 分散
  - HHI 0.1-0.2: 适度集中
  - HHI > 0.2: 高度集中

#### 5.3.2 风险敞口计算
- **总市场价值**: 当前持仓市值
- **总浮动盈亏**: 未实现盈亏
- **总实现盈亏**: 已卖出部分盈亏
- **总盈亏**: 浮动 + 实现

#### 5.3.3 仓位管理
- **Kelly 公式改良版**: 根据胜率和盈亏比计算最优仓位
- **单只最大仓位**: 20% (可配置)
- **信号强度分级**: STRONG_BUY/BUY/HOLD
- **置信度调整**: 根据五维评分调整仓位

---

## 🏷️ 能力六：收藏股管理系统

### 6.1 收藏股操作

- **添加收藏**: 代码 + 名称 + 标签
- **删除收藏**: 按代码删除
- **批量查看**: 支持标签筛选
- **信息更新**: 目标价、止损价、备注

### 6.2 标签管理

- **标签格式**: 逗号分隔 (如：白酒，龙头，蓝筹)
- **标签筛选**: 按标签查看子集
- **标签建议**: 行业/概念/风格/市值

### 6.3 价格提醒

- **目标价设置**: 预期卖出价格
- **止损价设置**: 风险止损价格
- **现价监控**: 实时对比触发提醒

### 6.4 批量监控

- **一键扫描**: 对全部收藏股执行技术分析
- **信号汇总**: 输出所有触发信号的股票
- **排序筛选**: 按评分/涨跌幅排序

---

## 🛠️ 能力七：数据导出与集成

### 7.1 数据导出格式

**CSV 格式**:
```csv
date,open,high,low,close,volume,amount
2026-03-12,1680.00,1695.00,1675.00,1688.00,1234567,2087654321
```

**JSON 格式**:
```json
{
  "symbol": "600519",
  "data": [
    {"date": "2026-03-12", "open": 1680, "high": 1695, ...}
  ]
}
```

### 7.2 导出参数

- **数据天数**: 默认 60 天，可配置 (如 120 天)
- **输出文件**: 自定义文件路径
- **数据字段**: OHLCV + 成交额

---

## 📋 命令行接口 (CLI)

### 完整命令列表

| 命令 | 功能 | 数据源 | 示例 |
|------|------|--------|------|
| `analyze` | 股票技术分析 | AKShare | `python main.py analyze 600519 --full` |
| `query` | 实时行情查询 | 新浪财经 | `python main.py query 600519 000001` |
| `sector` | 板块涨幅排行 | 东方财富 | `python main.py sector --concept` |
| `flow` | 资金流向分析 | AKShare | `python main.py flow 600519` |
| `search` | 股票搜索 | AKShare | `python main.py search 平安` |
| `export` | 历史数据导出 | AKShare | `python main.py export 600519 --format json` |
| `portfolio` | 持仓管理 | 本地数据库 | `python main.py portfolio --list` |
| `watchlist` | 收藏股管理 | 本地数据库 | `python main.py watchlist --add 600519` |
| `monitor` | 监控持仓股和收藏股 | 新浪+AKShare | `python main.py monitor --output report.md` |
| `alert` | 智能预警检查 | 新浪+AKShare | `python main.py alert` |
| `daemon` | 后台监控进程 | 新浪+AKShare | `python main.py daemon --output-dir ./reports` |
| `mystocks` | 综合资产管理 | 本地数据库 | `python main.py mystocks pos` |
| `params` | 参数管理 | 本地配置 | `python main.py params list` |
| `init-db` | 初始化数据库 | - | `python main.py init-db` |
| `init-position` | 初始化持仓 | 本地数据库 | `python main.py init-position --file positions.json` |

### analyze 命令参数详解

```bash
# 完整分析 (所有策略)
python main.py analyze 600519 --full

# 指定策略分析
python main.py analyze 600519 --strategy vcp    # 仅 VCP
python main.py analyze 600519 --strategy td     # 仅九转
python main.py analyze 600519 --strategy divergence  # 仅背离

# JSON 格式输出 (便于程序处理)
python main.py analyze 600519 --json

# 分析收藏股列表
python main.py analyze --watchlist

# 自定义历史数据天数
python main.py analyze 600519 --days 120
```

### params 命令参数详解

```bash
# 列出所有配置了参数的股票
python main.py params list

# 获取某股票的参数配置
python main.py params get --symbol 600519

# 设置股票参数 (支持多个参数)
python main.py params set --symbol 600519 --name 贵州茅台 \
  --params "vcp.min_drops=3,zigzag.threshold=0.08,td.period=9"

# 删除股票参数配置
python main.py params remove --symbol 600519
```

**支持的参数类型:**
- `vcp.*` - VCP 形态参数 (min_drops, max_drops, min_contraction)
- `zigzag.*` - ZigZag 参数 (threshold)
- `td.*` - 神奇九转参数 (period, compare_period)
- `rsi.*` - RSI 参数 (period, overbought, oversold)
- `macd.*` - MACD 参数 (fast, slow, signal)
- `divergence.*` - 背离检测参数 (window)

### init-position 命令参数详解

```bash
# 单只持仓初始化
python main.py init-position --code 600519 --name 贵州茅台 --qty 100 --cost 1500 --price 1520

# 从 JSON 文件批量导入
python main.py init-position --file positions.json

# 从 CSV 文件批量导入
python main.py init-position --file positions.csv --format csv

# 从券商交割单导入（自动检测券商）
python main.py init-position --broker-file huatai_statement.csv

# 从券商交割单导入（指定券商）
python main.py init-position --broker-file statement.csv --broker huatai

# 累加模式（不覆盖原有持仓）
python main.py init-position --file positions.json --mode add

# 指定建仓日期
python main.py init-position --code 600519 --qty 100 --cost 1500 --price 1520 --date 2025-12-01
```

### mystocks init 命令（等效）

```bash
# 与 init-position 命令等效，直接调用 mystocks 模块
python3 -m mystocks init --code 600519 --name 贵州茅台 --qty 100 --cost 1500 --price 1520
python3 -m mystocks init --file positions.json
python3 -m mystocks init --broker-file huatai_statement.csv
```

**命令行参数:**
- `--code`: 股票代码（单只初始化模式）
- `--name`: 股票名称
- `--qty`: 持仓数量
- `--cost`: 成本价
- `--price`: 当前价
- `--date`: 建仓日期（格式：YYYY-MM-DD）
- `--file`: 导入文件路径（JSON/CSV）
- `--broker-file`: 券商交割单文件路径（CSV/XLSX）
- `--broker`: 券商名称（默认 auto 自动检测）
- `--format`: 文件格式（json/csv，默认根据扩展名判断）
- `--mode`: 导入模式（overwrite=覆盖，add=累加，默认 overwrite）

### monitor 命令参数详解

监控持仓股和收藏股，生成 Markdown 格式报告。

```bash
# 执行一次监控（控制台输出）
python main.py monitor

# 导出 Markdown 报告到文件
python main.py monitor --output monitor_report.md

# 只监控持仓股
python main.py monitor --no-watchlist

# 只监控收藏股
python main.py monitor --no-position
```

**命令行参数:**
- `--output`, `-o`: 输出文件路径（Markdown 格式）
- `--no-position`: 不监控持仓股
- `--no-watchlist`: 不监控收藏股

**报告内容:**
- 汇总统计（持仓股/收藏股数量、总市值、盈亏等）
- 预警信息汇总（按高危/警告/提示分级）
- **预警规则详情**（阈值 vs 当前值，已触发/正常状态）
- 持仓股监控详情（表格 + 个股详情）
- 收藏股监控详情（表格 + 个股详情）
- 风险提示（持仓集中度、亏损股票、大涨股票等）

**预警规则详情包括:**
- 成本百分比规则：盈利/亏损百分比与阈值对比
- 价格涨跌幅规则：日内大涨/大跌检测
- 成交量规则：放量/缩量倍数
- 技术指标规则：MA 金叉/死叉、RSI 超买/超卖

### daemon 命令参数详解

启动后台监控进程，周期性执行监控并生成报告。

```bash
# 启动后台监控（默认 5 分钟间隔）
python main.py daemon

# 自定义监控间隔（10 分钟）
python main.py daemon --interval 600

# 自动保存报告到指定目录
python main.py daemon --output-dir ./monitor_reports

# 组合使用
python main.py daemon --interval 300 --output-dir ./reports
```

**命令行参数:**
- `--interval`: 监控间隔（秒，默认 300）
- `--output-dir`: 报告输出目录（自动生成带时间戳的报告文件）

**工作模式:**
- 交易时间：自动提高监控频率（基于 SmartScheduler）
- 盘后/周末：降低监控频率，节省资源
- 按 Ctrl+C 停止监控

---

## ⚙️ 配置系统

### config/settings.py 配置项

```python
# 策略参数
STRATEGY_PARAMS = {
    'vcp': {
        'min_contraction': 0.05,  # 最小收缩比例
        'max_pullbacks': 4,       # 最大回调次数
    },
    'td': {
        'td_period': 9,           # 九转周期
    },
    # ...
}

# 五维评分权重
FIVE_DIMENSION_WEIGHTS = {
    'D1': 20,
    'D2': 30,
    'D3': 20,
    'D4': 10,
    'D5': 20,
}

# 决策阈值
DECISION_THRESHOLD = {
    'strong_buy': 85,
    'buy': 65,
    'hold': 40,
}

# 仓位管理参数
POSITION_PARAMS = {
    'max_single_position': 0.20,  # 单只最大 20%
    'kelly_factor': 0.5,          # Kelly 保守系数
}

# ========== 监控预警配置 ==========
MONITOR_CONFIG = {
    # 预警规则默认值
    'cost_pct_above': 15.0,    # 盈利 15% 预警
    'cost_pct_below': -12.0,   # 亏损 12% 预警
    'change_pct_above': 4.0,   # 日内大涨
    'change_pct_below': -4.0,  # 日内大跌
    'volume_surge': 2.0,       # 放量倍数

    # 智能频率（秒）- 支持自定义配置
    'interval_market': 300,     # 交易时间 5 分钟
    'interval_lunch': 600,      # 午休 10 分钟
    'interval_after_hours': 1800,  # 收盘后 30 分钟
    'interval_night': 3600,     # 凌晨 1 小时
    'interval_weekend': 3600,   # 周末 1 小时
}

# ========== 报告输出配置 ==========
REPORT_CONFIG = {
    # 默认输出位置
    'default_output_dir': './monitor_reports',  # 默认报告输出目录
    'output_format': 'markdown',  # 输出格式：markdown/html/json

    # 模版文件配置
    'template_file': None,  # 自定义模版文件路径，None 使用内置模版

    # 报告内容配置（可配置是否包含各部分）
    'include_summary': True,       # 包含汇总统计
    'include_alerts': True,        # 包含预警信息
    'include_positions': True,     # 包含持仓股详情
    'include_watchlist': True,     # 包含收藏股详情
    'include_risk_tips': True,     # 包含风险提示
    'include_rule_details': True,  # 包含预警规则详情

    # 预警规则详情配置
    'rule_details': {
        'cost_rule': True,         # 成本百分比规则
        'price_rule': True,        # 价格涨跌幅规则
        'volume_rule': True,       # 成交量规则
        'technical_rule': True,    # 技术指标规则
        'trailing_stop': True,     # 动态止盈止损
    }
}

# 交易手续费
TRADING_FEES = {
    'commission': 0.0003,      # 佣金万分之三
    'stamp_tax': 0.001,        # 印花税千分之一
    'transfer_fee': 0.00002,   # 过户费万分之二
}
```

### config/stock_params.json 股票特定参数

**支持每支股票独立的策略参数配置，默认回退到全局参数**

**配置格式:**
```json
{
  "defaults": {
    "vcp": {"min_drops": 2, "max_drops": 4, "min_contraction": 0.5},
    "zigzag": {"threshold": 0.05},
    "td": {"period": 9, "compare_period": 4},
    "rsi": {"period": 14, "overbought": 70, "oversold": 30},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "divergence": {"window": 20}
  },
  "stocks": {
    "600519": {
      "name": "贵州茅台",
      "vcp": {"min_drops": 3, "min_contraction": 0.4},
      "zigzag": {"threshold": 0.08}
    },
    "000858": {
      "name": "五粮液",
      "td": {"period": 7}
    }
  }
}
```

**参数优先级:** 构造函数参数 > 股票特定配置 > 全局默认值

**管理命令:**
```bash
# 列出所有配置参数的股票
python main.py params list

# 获取某股票的参数
python main.py params get --symbol 600519

# 设置股票参数
python main.py params set --symbol 600519 --name 贵州茅台 \
  --params "vcp.min_drops=3,zigzag.threshold=0.08,td.period=9"

# 删除股票参数配置
python main.py params remove --symbol 600519
```

---

## 🏗️ 系统架构

### 模块依赖关系

```
┌─────────────────────────────────────────────────────────┐
│                      main.py (CLI)                       │
├─────────────────────────────────────────────────────────┤
│  commands/  │  analyze │ portfolio │ watchlist │ alert  │
│             │  query   │ sector    │ monitor   │ daemon │
├─────────────────────────────────────────────────────────┤
│  investing  │  engines  │ strategies │ indicators        │
│             │  Ultimate │ VCP/TD/Div │ 6 大技术指标       │
├─────────────────────────────────────────────────────────┤
│  mystocks   │  models   │ services   │ storage           │
│             │  Position │ Portfolio  │ Database/Repo     │
├─────────────────────────────────────────────────────────┤
│  realalerts │  engine   │ rules      │ scheduler         │
│             │  Alert    │ 7 大规则    │ SmartScheduler    │
├─────────────────────────────────────────────────────────┤
│  stockquery │  unified  │ sources    │ models            │
│             │  Service  │ Sina/AK/EM │ QuoteData         │
├─────────────────────────────────────────────────────────┤
│  config/    │  settings.py (统一配置)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 依赖说明

### 核心依赖

| 库 | 版本 | 用途 |
|------|------|------|
| pandas | >=2.0.0 | 数据处理核心 |
| numpy | >=1.24.0 | 数值计算 |
| ta | >=0.10.0 | 技术指标库 |
| sqlalchemy | >=2.0.0 | 数据库 ORM |
| akshare | >=1.10.0 | A 股数据获取 |
| requests | >=2.28.0 | HTTP 请求 |
| matplotlib | >=3.7.0 | 可视化 (可选) |
| pyyaml | >=6.0 | 配置管理 |

---

## ⚠️ 风险提示

1. **ZigZag 警示**: 该指标具有滞后性，仅用于盘后复盘分析，严禁用于实时预测
2. **数据质量**: AKShare 数据稳定性需要持续验证，建议关键决策前多源验证
3. **参数调优**: VCP 阈值、均线周期等参数需要通过历史回测优化
4. **合规声明**: 本系统所有分析仅供参考，不构成投资建议，用户应自行承担投资风险
5. **技术限制**: 系统无法预测突发利空、政策变化等黑天鹅事件

---

## 📝 版本历史

### v2.5 (Trading Day Scheduler) - 2026-03-13
- ✅ 交易日判断功能 - 周末和法定节假日不执行预警
- ✅ 支持 2026 年 A 股法定节假日配置（元旦/春节/清明/劳动/端午/中秋/国庆）
- ✅ 优化调度逻辑 - 仅交易日的交易时段（9:30-11:30, 13:00-15:00）执行预警
- ✅ 午休时间不预警 - 11:30-13:00 跳过监控
- ✅ 收盘后不预警 - 15:00 后跳过监控
- ✅ 自定义 MD 报告模版 - `config/monitor_report_template.md`
- ✅ 报告模版变量替换 - 支持 `{{key}}` 语法
- ✅ 规则详情表格展示 - 已触发规则 vs 正常状态规则

### v2.4 (Configuration Enhancement) - 2026-03-13
- ✅ 配置化监控间隔时间 - 在 `config/settings.py` 的 `MONITOR_CONFIG` 中配置
- ✅ 配置化报告输出位置 - `REPORT_CONFIG.default_output_dir`
- ✅ 报告模版文件支持 - 支持自定义 Markdown 模版文件
- ✅ 预警规则详情输出 - 报告中显示阈值与当前值对比
- ✅ 七大预警规则计算结果展示：
  - 成本百分比规则（盈利/亏损百分比）
  - 价格涨跌幅规则（日内大涨/大跌）
  - 成交量规则（放量/缩量）
  - 技术指标规则（金叉/死叉、RSI 超买/超卖）
- ✅ 报告分块配置 - 可配置是否包含汇总/预警/持仓/收藏/风险提示/规则详情

### v2.3 (Monitor Report) - 2026-03-13
- ✅ 新增持仓股监控功能
- ✅ 新增 Markdown 格式监控报告生成
- ✅ 增强 `monitor` 命令 - 同时监控持仓股和收藏股
- ✅ 增强 `daemon` 命令 - 真正的实时监控进程
- ✅ 报告内容包括：汇总统计/预警信息/持仓详情/收藏股详情/风险提示
- ✅ 支持导出报告到文件（便于分享和存档）
- ✅ 智能调度器 - 交易时间自动提高监控频率

### v2.2 (Position Initialization) - 2026-03-12
- ✅ 新增持仓初始化功能 - 支持批量导入已有持仓
- ✅ 新增 `init-position` 命令 - 单只/批量导入持仓
- ✅ 支持 JSON/CSV 文件格式导入
- ✅ 支持券商交割单导入（华泰/中信/国泰君安/东方财富等）
- ✅ 两种导入模式：overwrite（覆盖）/ add（累加）
- ✅ 通用解析器 - 自动匹配不同列名格式
- ✅ Python API: `initialize_position()`, `initialize_positions_from_file()`

### v2.1 (realalerts Integration) - 2026-03-11
- ✅ 整合 stock-monitor-pro-2.1.0 智能预警监控系统
- ✅ 新增 `alert` 命令 - 执行一次智能预警检查
- ✅ 新增 `daemon` 命令 - 后台常驻监控进程 (7x24 小时)
- ✅ 七大预警规则：成本百分比/涨跌幅/成交量/均线/RSI/跳空/动态止盈
- ✅ 智能频率控制 - 基于北京时间的动态监控频率
- ✅ 分级预警 - 紧急级/警告级/提醒级三级预警
- ✅ 智能分析引擎 - 舆情分析 + 资金流向关联分析
- ✅ 防骚扰机制 - 同类预警 30 分钟内不重复
- ✅ 重构目录结构，统一模块命名

### v2.0 (Integration Edition) - 2026-03-11
- ✅ 整合 stock-pro-1.1.0 实时行情功能
- ✅ 新增 `query`/`sector`/`flow`/`search`/`export` 命令
- ✅ 新增三大数据源：新浪财经、东方财富、AKShare 增强版
- ✅ 智能路由和故障转移机制

### v1.9 (Ultimate Edition) - 2026-03-11
- ✅ 整合持仓管理模块 (FIFO 成本计算)
- ✅ 实现五维共振评分系统
- ✅ 实现六大核心指标
- ✅ 实现三大战法策略
- ✅ 实现动态止损和仓位管理
- ✅ 新增 CLI 命令行工具

---

## 💡 使用建议

### 最佳实践

1. **盘前**: 使用 `analyze --watchlist` 扫描收藏股，筛选目标
2. **盘中**: 运行 `daemon` 后台监控，接收实时预警
3. **盘后**: 使用 `analyze --full` 深度复盘，更新策略

### 策略组合

- **进攻型**: VCP 爆发突击 (主) + 九转黄金坑 (辅)
- **防守型**: 顶部背离止盈 (必配) + 动态止损
- **平衡型**: 三策略共振，等待多重确认

### 仓位管理

- 单只股票不超过 20%
- 总仓位根据市场状态调整 (牛市 80%+/震荡市 50%/熊市 20%)
- 永不满仓单只股票

---

*最后更新：2026-03-13 (v2.5)*
