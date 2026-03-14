# 代码重构优化实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构项目代码结构，消除重复代码，建立清晰的领域边界，实现高内聚低耦合的架构

**Architecture:** 采用领域驱动设计 (DDD) 分层架构：
- `domain/` - 核心业务逻辑（分析、投资组合、预警三大领域）
- `infrastructure/` - 外部依赖（数据源、数据库、API）
- `application/` - 应用服务层（用例编排）
- `commands/` - CLI 入口层（参数处理）

**Tech Stack:** Python 3.9+, SQLAlchemy, pandas, numpy, ta-lib

---

## 前置检查清单

在开始重构之前，需要确认当前代码可以正常工作：

- [ ] **Step 1: 运行现有测试**

```bash
cd /home/zxg/workspace/stock-trader-pro
python -m pytest -v  # 或 python test_*.py
```

预期：所有现有测试通过

- [ ] **Step 2: 验证主要功能**

```bash
# 验证分析功能
python main.py analyze 600519 --json | head -20

# 验证查询功能
python main.py query 600519 --json | head -10

# 验证持仓功能
python main.py portfolio --list
```

预期：命令正常执行，输出正确

- [ ] **Step 3: 创建 git 分支**

```bash
git checkout -b refactor/ddd-architecture
```

预期：创建新的重构分支

---

## Chunk 1: 删除重复目录

### Task 1: 清理重复的 `core/` 目录

**背景:** `core/analysis/` 与 `investing/` 内容重复，保留 `investing/`（更成熟）

**Files:**
- 删除：`core/` 目录

- [ ] **Step 1: 确认 core/ 没有被引用**

```bash
grep -r "from core" --include="*.py" .
grep -r "import core" --include="*.py" .
```

预期：无结果或仅有测试文件引用

- [ ] **Step 2: 删除 core/ 目录**

```bash
rm -rf core/
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: 删除重复的 core/ 目录"
```

### Task 2: 清理重复的 `data/` 目录

**背景:** `data/` 与 `stockquery/` 内容重复，保留 `stockquery/`（被 main.py 引用）

**Files:**
- 删除：`data/` 目录
- 保留：`stockquery/` 目录

- [ ] **Step 1: 确认 data/ 状态**

```bash
grep -r "from data" --include="*.py" .
grep -r "import data" --include="*.py" .
```

预期：无结果

- [ ] **Step 2: 删除 data/ 目录**

```bash
rm -rf data/
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: 删除重复的 data/ 目录"
```

### Task 3: 整合 `services/` 到 `mystocks/services/`

**背景:** 根目录 `services/` 与 `mystocks/services/` 职责不清

**Files:**
- 检查：`services/` 目录内容
- 合并到：`mystocks/services/` 或删除

- [ ] **Step 1: 检查 services/ 内容**

```bash
ls -la services/
```

- [ ] **Step 2: 根据内容决定处理方式**

如果 `services/` 是旧的或空的：
```bash
rm -rf services/
```

如果 `services/` 有新的服务：
```bash
# 移动到 mystocks/services/
mv services/alert_service mystocks/services/
mv services/analysis_service mystocks/services/
# ... 其他服务
```

- [ ] **Step 3: 更新导入路径**

在所有引用文件中更新：
```python
# 旧
from services.alert_service import AlertService
# 新
from mystocks.services.alert_service import AlertService
```

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "refactor: 整合 services/ 到 mystocks/services/"
```

---

## Chunk 2: 建立新的领域层结构

### Task 4: 创建 domain 目录结构

**Files:**
- 创建：`domain/__init__.py`
- 创建：`domain/analysis/__init__.py`
- 创建：`domain/analysis/engines/__init__.py`
- 创建：`domain/analysis/strategies/__init__.py`
- 创建：`domain/analysis/indicators/__init__.py`
- 创建：`domain/analysis/signals/__init__.py`
- 创建：`domain/portfolio/__init__.py`
- 创建：`domain/portfolio/models/__init__.py`
- 创建：`domain/portfolio/services/__init__.py`
- 创建：`domain/portfolio/repositories/__init__.py`
- 创建：`domain/alerting/__init__.py`
- 创建：`domain/alerting/rules/__init__.py`
- 创建：`domain/alerting/engine.py`
- 创建：`domain/alerting/scheduler.py`
- 创建：`domain/common/__init__.py`
- 创建：`domain/common/trading_time.py`
- 创建：`domain/common/calendar.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p domain/{analysis/{engines,strategies,indicators,signals},portfolio/{models,services,repositories},alerting/{rules},common}
```

- [ ] **Step 2: 创建 __init__.py 文件**

```bash
touch domain/__init__.py
touch domain/analysis/__init__.py
touch domain/analysis/engines/__init__.py
touch domain/analysis/strategies/__init__.py
touch domain/analysis/indicators/__init__.py
touch domain/analysis/signals/__init__.py
touch domain/portfolio/__init__.py
touch domain/portfolio/models/__init__.py
touch domain/portfolio/services/__init__.py
touch domain/portfolio/repositories/__init__.py
touch domain/alerting/__init__.py
touch domain/alerting/rules/__init__.py
touch domain/alerting/engine.py
touch domain/alerting/scheduler.py
touch domain/common/__init__.py
```

- [ ] **Step 3: 提交**

```bash
git add domain/
git commit -m "feat: 创建 domain 领域层目录结构"
```

### Task 5: 迁移 investing 到 domain/analysis

**Files:**
- 移动：`investing/engines/` → `domain/analysis/engines/`
- 移动：`investing/strategies/` → `domain/analysis/strategies/`
- 移动：`investing/indicators/` → `domain/analysis/indicators/`
- 废弃：`investing/` 目录

- [ ] **Step 1: 移动 engines**

```bash
mv investing/engines/* domain/analysis/engines/
```

- [ ] **Step 2: 移动 strategies**

```bash
mv investing/strategies/* domain/analysis/strategies/
```

- [ ] **Step 3: 移动 indicators**

```bash
mv investing/indicators/* domain/analysis/indicators/
```

- [ ] **Step 4: 创建 signal_generator 到 signals**

```bash
mv investing/engines/signal_generator.py domain/analysis/signals/
```

- [ ] **Step 5: 更新所有导入路径**

需要更新的文件：
- `commands/analyze.py`
- `commands/monitor.py`
- 其他引用 investing 的文件

```python
# 旧
from investing import UltimateEngine, SignalGenerator
# 新
from domain.analysis import UltimateEngine
from domain.analysis.signals import SignalGenerator
```

- [ ] **Step 6: 提交**

```bash
git add -A
git commit -m "refactor: 迁移 investing 到 domain/analysis"
```

### Task 6: 迁移 mystocks 到 domain/portfolio

**Files:**
- 移动：`mystocks/models/` → `domain/portfolio/models/`
- 移动：`mystocks/services/` → `domain/portfolio/services/`
- 移动：`mystocks/storage/repositories/` → `domain/portfolio/repositories/`
- 保留：`mystocks/` 作为兼容层（后续删除）

- [ ] **Step 1: 移动 models**

```bash
mv mystocks/models/* domain/portfolio/models/
```

- [ ] **Step 2: 移动 services**

```bash
mv mystocks/services/* domain/portfolio/services/
```

- [ ] **Step 3: 移动 repositories**

```bash
mv mystocks/storage/repositories/* domain/portfolio/repositories/
```

- [ ] **Step 4: 更新所有导入路径**

```python
# 旧
from mystocks.models import Position, Account
from mystocks.services import PortfolioService
# 新
from domain.portfolio.models import Position, Account
from domain.portfolio.services import PortfolioService
```

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "refactor: 迁移 mystocks 到 domain/portfolio"
```

### Task 7: 迁移 realalerts 到 domain/alerting

**Files:**
- 移动：`realalerts/rules/` → `domain/alerting/rules/`
- 移动：`realalerts/engine.py` → `domain/alerting/engine.py`
- 移动：`realalerts/scheduler/` → `domain/alerting/scheduler/`
- 保留：`realalerts/position/` → `domain/portfolio/` (仓位管理属于投资组合领域)

- [ ] **Step 1: 移动 rules**

```bash
mv realalerts/rules/* domain/alerting/rules/
```

- [ ] **Step 2: 移动 engine 和 scheduler**

```bash
mv realalerts/engine.py domain/alerting/
mv realalerts/scheduler/* domain/alerting/scheduler/
```

- [ ] **Step 3: 移动 position 到 portfolio**

```bash
mv realalerts/position/* domain/portfolio/services/
```

- [ ] **Step 4: 更新所有导入路径**

```python
# 旧
from realalerts.engine import AlertEngine
from realalerts.rules import PriceAlert
# 新
from domain.alerting.engine import AlertEngine
from domain.alerting.rules import PriceAlert
```

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "refactor: 迁移 realalerts 到 domain/alerting"
```

---

## Chunk 3: 建立基础设施层

### Task 8: 创建 infrastructure 目录结构

**Files:**
- 创建：`infrastructure/__init__.py`
- 创建：`infrastructure/database.py`
- 创建：`infrastructure/models/__init__.py`
- 创建：`infrastructure/models/kline.py`
- 创建：`infrastructure/models/stock_list.py`
- 创建：`infrastructure/models/position.py`
- 创建：`infrastructure/models/transaction.py`
- 创建：`infrastructure/models/account.py`
- 创建：`infrastructure/models/watchlist.py`
- 创建：`infrastructure/sources/__init__.py`
- 创建：`infrastructure/sources/base.py`
- 创建：`infrastructure/sources/akshare_source.py`
- 创建：`infrastructure/sources/sina_source.py`
- 创建：`infrastructure/sources/eastmoney_source.py`
- 创建：`infrastructure/repositories/__init__.py`
- 创建：`infrastructure/repositories/kline_repo.py`
- 创建：`infrastructure/repositories/stock_list_repo.py`
- 创建：`infrastructure/repositories/position_repo.py`
- 创建：`infrastructure/repositories/transaction_repo.py`
- 创建：`infrastructure/repositories/account_repo.py`
- 创建：`infrastructure/repositories/watchlist_repo.py`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p infrastructure/{models,sources,repositories}
```

- [ ] **Step 2: 创建 __init__.py 文件**

```bash
touch infrastructure/__init__.py
touch infrastructure/database.py
touch infrastructure/models/__init__.py
touch infrastructure/sources/__init__.py
touch infrastructure/repositories/__init__.py
```

- [ ] **Step 3: 提交**

```bash
git add infrastructure/
git commit -m "feat: 创建 infrastructure 基础设施层"
```

### Task 9: 迁移 stockquery 到 infrastructure

**Files:**
- 移动：`stockquery/sources/` → `infrastructure/sources/`
- 删除：`stockquery/unified_service.py` (缓存逻辑移到 application 层)
- 移动：`stockquery/models.py` → `infrastructure/models/`

- [ ] **Step 1: 移动数据源**

```bash
mv stockquery/sources/* infrastructure/sources/
mv stockquery/models.py infrastructure/models/
```

- [ ] **Step 2: 更新导入路径**

```python
# 旧
from stockquery.sources.akshare import AKShareDataSource
# 新
from infrastructure.sources.akshare import AKShareDataSource
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: 迁移 stockquery 到 infrastructure"
```

### Task 10: 迁移数据库和 ORM 模型

**Files:**
- 移动：`mystocks/storage/database.py` → `infrastructure/database.py`
- 移动：`mystocks/models/*.py` → `infrastructure/models/`
- 移动：`mystocks/storage/repositories/*.py` → `infrastructure/repositories/`

- [ ] **Step 1: 移动数据库文件**

```bash
mv mystocks/storage/database.py infrastructure/database.py
mv mystocks/models/*.py infrastructure/models/
mv mystocks/storage/repositories/*.py infrastructure/repositories/
```

- [ ] **Step 2: 更新所有导入路径**

```python
# 旧
from mystocks.storage.database import get_db, init_database
from mystocks.models import KLine, Position
# 新
from infrastructure.database import get_db, init_database
from infrastructure.models import KLine, Position
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: 迁移数据库和 ORM 模型到 infrastructure"
```

---

## Chunk 4: 建立应用层

### Task 11: 创建 application 服务层

**Files:**
- 创建：`application/__init__.py`
- 创建：`application/analysis_service.py`
- 创建：`application/portfolio_service.py`
- 创建：`application/alerting_service.py`
- 创建：`application/query_service.py`

- [ ] **Step 1: 创建应用服务目录**

```bash
mkdir -p application
touch application/__init__.py
```

- [ ] **Step 2: 创建分析应用服务**

```python
# application/analysis_service.py
"""分析应用服务 - 编排分析用例"""

from domain.analysis.engines import UltimateEngine
from domain.analysis.strategies import VCPBreakoutStrategy, TDGoldenPitStrategy, TopDivergenceStrategy
from domain.analysis.signals import SignalGenerator
from infrastructure.data.unified_service import UnifiedStockQueryService


class AnalysisAppService:
    """分析应用服务"""

    def __init__(self):
        self.data_service = UnifiedStockQueryService()

    def analyze_stock(self, symbol: str, days: int = 250) -> dict:
        """分析单只股票"""
        df = self.data_service.get_historical_data(symbol)
        if df is None or df.empty:
            return {"error": f"无法获取 {symbol} 的历史数据"}

        engine = UltimateEngine(df, symbol=symbol)
        engine_result = engine.evaluate_all()

        signal_gen = SignalGenerator(df)
        full_analysis = signal_gen.get_full_analysis()

        return {
            'symbol': symbol,
            'engine_result': engine_result,
            'signal_analysis': full_analysis,
        }
```

- [ ] **Step 3: 提交**

```bash
git add application/
git commit -m "feat: 创建 application 应用服务层"
```

### Task 12: 重构 commands 使用应用服务

**Files:**
- 修改：`commands/analyze.py`
- 修改：`commands/query.py`
- 修改：`commands/portfolio.py`
- 修改：`commands/alert.py`

- [ ] **Step 1: 重构 analyze.py**

```python
# commands/analyze.py
from application.analysis_service import AnalysisAppService

def cmd_analyze(args):
    """analyze 命令处理"""
    service = AnalysisAppService()
    result = service.analyze_stock(args.symbol, days=args.days)
    print(format_analysis_report(result))
```

- [ ] **Step 2: 更新其他命令**

类似地更新其他命令文件，让它们只依赖 application 层

- [ ] **Step 3: 提交**

```bash
git add commands/
git commit -m "refactor: 重构 commands 使用应用服务"
```

---

## Chunk 5: 清理和验证

### Task 13: 删除旧的废弃目录

**Files:**
- 删除：`investing/` (已迁移到 domain/analysis)
- 删除：`mystocks/` (已迁移到 domain/portfolio)
- 删除：`realalerts/` (已迁移到 domain/alerting)
- 删除：`stockquery/` (已迁移到 infrastructure/data)

- [ ] **Step 1: 确认所有引用已更新**

```bash
grep -r "from investing" --include="*.py" .
grep -r "from mystocks" --include="*.py" .
grep -r "from realalerts" --include="*.py" .
grep -r "from stockquery" --include="*.py" .
```

预期：无结果或仅有废弃目录内部

- [ ] **Step 2: 删除旧目录**

```bash
rm -rf investing/ mystocks/ realalerts/ stockquery/
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: 删除废弃的旧目录"
```

### Task 14: 运行测试验证

- [ ] **Step 1: 运行所有测试**

```bash
python -m pytest -v
```

预期：所有测试通过

- [ ] **Step 2: 验证主要功能**

```bash
python main.py analyze 600519 --json | head -20
python main.py query 600519 --json | head -10
python main.py portfolio --list
python main.py alert
```

预期：所有命令正常工作

- [ ] **Step 3: 提交标记**

```bash
git commit --allow-empty -m "test: 重构完成，所有测试通过"
```

### Task 15: 更新文档

**Files:**
- 修改：`README.md` - 更新目录结构说明

- [ ] **Step 1: 更新 README.md 中的目录结构**

```markdown
## 🗂️ 目录结构

```
stock-trader-pro/
├── main.py                          # 主入口
├── commands/                        # CLI 命令层 (薄层)
├── application/                     # 应用服务层 (用例编排)
├── domain/                          # 领域层 (核心业务逻辑)
│   ├── analysis/                    # 技术分析领域
│   │   ├── engines/                 # 分析引擎
│   │   ├── strategies/              # 交易策略
│   │   ├── indicators/              # 技术指标
│   │   └── signals/                 # 信号生成
│   ├── portfolio/                   # 投资组合领域
│   │   ├── services/                # 领域服务
│   │   └── repositories/ (接口)     # 仓储接口
│   └── alerting/                    # 预警领域
│       ├── rules/                   # 预警规则
│       ├── engine/                  # 预警引擎
│       └── scheduler/               # 调度器
├── infrastructure/                  # 基础设施层
│   ├── database.py                  # 数据库连接
│   ├── models/                      # ORM 模型
│   ├── sources/                     # 外部数据源
│   │   ├── base.py                  # 数据源抽象基类
│   │   ├── akshare_source.py        # AKShare 适配器
│   │   ├── sina_source.py           # 新浪财经适配器
│   │   └── eastmoney_source.py      # 东方财富适配器
│   └── repositories/                # 仓储实现
│       ├── kline_repo.py            # K 线仓储
│       ├── position_repo.py         # 持仓仓储
│       └── ...
└── config/                          # 配置
```
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: 更新目录结构说明"
```

---

## 最终检查清单

- [ ] 所有测试通过
- [ ] 所有主要功能命令正常
- [ ] 代码中无废弃目录引用
- [ ] README 文档已更新
- [ ] git 提交历史清晰

---

## 风险缓解

1. **导入错误** - 每迁移一个模块立即更新导入并测试
2. **功能回归** - 每个 chunk 完成后运行完整测试
3. **循环依赖** - 保持 domain → infrastructure 的单向依赖

## 预期结果

重构完成后：
- ✅ 无重复代码
- ✅ 清晰的领域边界
- ✅ 低耦合的模块关系
- ✅ 易于测试和扩展的架构
