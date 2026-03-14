# SKILL.md Bash Comments Enhancement Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance all Bash script comments in SKILL.md with detailed business context so AI can understand the purpose, data flow, and expected output of each command.

**Architecture:** Systematically update each section's Bash code blocks, adding explanatory comments that describe:
- What business problem the command solves
- What data it operates on (input/output)
- Key parameters and their effects
- Expected output format and meaning

**Tech Stack:** Markdown documentation, Bash command examples

---

## Files to Modify

**Modify:** `SKILL.md` (lines 40-1080, all Bash code blocks)

**Approach:** Work section by section, ensuring each Bash command has comments that explain:
1. **Business purpose** - Why would a user run this command?
2. **Data flow** - What API is called, what data is returned
3. **Parameter effects** - What each flag does
4. **Output meaning** - What the results indicate

---

### Task 1: Installation & Quick Start Section (Lines 40-123)

**Files:**
- Modify: `SKILL.md:40-123`

- [ ] **Step 1: Update git clone comments**

Replace:
```bash
git clone <repository-url> stock-trader-pro
cd stock-trader-pro
```

With:
```bash
# 克隆项目到本地 - 从 Git 仓库下载完整的股票交易系统代码
# 业务目的：获取项目源码，准备本地开发环境
git clone <repository-url> stock-trader-pro
cd stock-trader-pro
```

- [ ] **Step 2: Update pip install comment**

Replace:
```bash
pip install -r requirements.txt
```

With:
```bash
# 安装项目依赖 - 使用 pip 安装 requirements.txt 中定义的所有 Python 包
# 依赖包括：pandas(数据处理)、numpy(数值计算)、ta(技术指标)、
# sqlalchemy(数据库 ORM)、akshare(股票数据 API)、requests(HTTP 请求)
# 业务目的：准备运行环境，所有第三方库安装完成后才能执行交易分析功能
pip install -r requirements.txt
```

- [ ] **Step 3: Update init-db command comment**

Replace:
```bash
python3 main.py init-db
```

With:
```bash
# 初始化 SQLite 数据库 - 创建所有必需的表结构
# 数据表包括：accounts(账户)、positions(持仓)、position_lots(持仓批次)、
# transactions(交易记录)、watchlist(收藏股)、kline_cache(K 线缓存)
# stock_params(股票策略参数)
# 业务目的：首次使用前必须执行，为后续持仓管理、交易记录存储准备数据库
# 输出：✅ 数据库初始化成功：/path/to/storage/investment.db
python3 main.py init-db
```

- [ ] **Step 4: Update Quick Start commands with detailed comments**

Replace the quick start block with:
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

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance installation and quick start comments with business context"
```

---

### Task 2: Technical Analysis Section (Lines 193-210)

**Files:**
- Modify: `SKILL.md:193-210`

- [ ] **Step 1: Update analyze command comments**

Replace the analyze commands block with:
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

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance technical analysis comments with business purpose"
```

---

### Task 3: Real-time Quotes & Money Flow (Lines 368-416)

**Files:**
- Modify: `SKILL.md:368-416`

- [ ] **Step 1: Update query command comments**

Replace:
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

- [ ] **Step 2: Update flow command comment**

Replace:
```bash
# 分析单只股票资金流向 - 查看主力资金/大单/中单/小单净流入数据
# 业务目的：判断主力资金态度，辅助买卖决策
# 数据流：AKShare API → 主力净流入 (>100 万), 大单净流入 (50-100 万),
# 中单/小单分类统计
# 返回数据：main_force_in(主力), big_order_in(大单), sentiment(多空情绪)
python3 main.py flow 600519
```

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance quotes and money flow comments with data source details"
```

---

### Task 4: Smart Alert & Monitoring (Lines 524-566)

**Files:**
- Modify: `SKILL.md:524-566`

- [ ] **Step 1: Update smart-monitor commands**

Replace:
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
```

- [ ] **Step 2: Update monitor and alert commands**

Replace:
```bash
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
```

- [ ] **Step 3: Update update-prices and update-kline commands**

Replace:
```bash
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

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance smart alert comments with scheduling details"
```

---

### Task 5: Portfolio Management (Lines 694-734)

**Files:**
- Modify: `SKILL.md:694-734`

- [ ] **Step 1: Update mystocks commands**

Replace:
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
```

- [ ] **Step 2: Update account and holdings commands**

Replace:
```bash
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
```

- [ ] **Step 3: Update mystocks module direct usage**

Replace:
```bash
# 直接使用 mystocks 模块（备用方式） - 不通过 main.py 直接调用模块
# 使用场景：脚本集成/自动化任务，避免参数解析开销
python3 -m mystocks pos           # 查看持仓
python3 -m mystocks buy 600519 --qty 100 --price 1500 --name 贵州茅台  # 买入
python3 -m mystocks sell 600519 --qty 50 --price 1600  # 卖出
python3 -m mystocks summary       # 资产汇总
python3 -m mystocks history --limit 50  # 交易历史
python3 -m mystocks init --code 600519 --qty 100 --cost 1500 --name 贵州茅台  # 初始化持仓
python3 -m mystocks update-prices --once  # 更新持仓价格
```

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance portfolio management comments with FIFO accounting details"
```

---

### Task 6: Watchlist & Sector Analysis (Lines 837-905)

**Files:**
- Modify: `SKILL.md:837-905`

- [ ] **Step 1: Update watchlist commands**

Replace:
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

- [ ] **Step 2: Update sector commands**

Replace:
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

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance watchlist and sector comments with usage scenarios"
```

---

### Task 7: Data Export & Stock Search (Lines 452-478, 943-955)

**Files:**
- Modify: `SKILL.md:452-478` and `SKILL.md:943-955`

- [ ] **Step 1: Update search commands**

Replace:
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

- [ ] **Step 2: Update export commands**

Replace:
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

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance search and export comments with data structure details"
```

---

### Task 8: Parameters Management (Lines 993-1008)

**Files:**
- Modify: `SKILL.md:993-1008`

- [ ] **Step 1: Update params commands**

Replace:
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

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: enhance parameters management comments with parameter explanations"
```

---

### Task 9: Final Review and Verification

**Files:**
- Read: `SKILL.md` (full file)

- [ ] **Step 1: Verify all Bash code blocks have detailed comments**

Check each section:
- Installation (✅)
- Quick Start (✅)
- Technical Analysis (✅)
- Real-time Quotes (✅)
- Money Flow (✅)
- Smart Alerts (✅)
- Portfolio Management (✅)
- Watchlist (✅)
- Sector Analysis (✅)
- Data Export (✅)
- Stock Search (✅)
- Parameters Management (✅)

- [ ] **Step 2: Verify comment consistency**

Ensure all comments follow the pattern:
- First line: What the command does (action)
- Second line: Business purpose (why)
- Third line: Data flow or parameters (how)
- Fourth line: Expected output (result)

- [ ] **Step 3: Final commit**

```bash
git add SKILL.md
git commit -m "docs: complete SKILL.md bash comments enhancement with AI-friendly business context"
```

---

## Completion Criteria

All Bash commands in SKILL.md should have comments that:
1. Explain the **business purpose** - what problem does this solve for the user?
2. Describe the **data flow** - which API is called, what data is returned?
3. Clarify **key parameters** - what do the flags do?
4. Specify **expected output** - what format and what does it mean?

After completion, an AI reading SKILL.md should understand:
- What each command does and why a user would run it
- What data sources are involved (AKShare/新浪/东方财富)
- What the output format means and how to interpret results
- Common usage scenarios for each command
