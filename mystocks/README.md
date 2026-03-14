# 我的股票 (MyStocks) - 综合资产管理模块

## 概述

`我的股票` 是一个整合了**持仓管理**、**收藏管理**、**数据存储**三大功能的综合资产管理模块。

采用分层架构设计：
- **模型层 (models)** - 数据模型定义
- **存储层 (storage)** - 数据库连接与数据访问
- **业务层 (services)** - 业务逻辑处理
- **Facade (主入口)** - 统一 API 接口

---

## 功能特性

### 1. 持仓管理
- ✅ 买入/卖出股票
- ✅ 自动计算持仓成本（含手续费）
- ✅ FIFO 分批建仓追踪
- ✅ 实现盈亏/浮动盈亏分开计算
- ✅ 交易记录完整保存

### 2. 收藏管理
- ✅ 添加/删除收藏股
- ✅ 标签分类管理
- ✅ 目标价/止损价设置
- ✅ 备注信息记录

### 3. 资产分析
- ✅ 持仓汇总（总市值/总盈亏）
- ✅ 持仓集中度分析（HHI 指数）
- ✅ 风险敞口计算
- ✅ 交易历史查询

### 4. 数据存储
- ✅ SQLite 数据库持久化
- ✅ 自动同步最新股价
- ✅ 数据导出功能

---

## 模块结构

```
mystocks/
├── __init__.py              # 主入口 (Facade 模式)
├── __main__.py              # CLI 入口
├── README.md
│
├── models/                  # 模型层
│   ├── __init__.py
│   ├── base.py              # SQLAlchemy Base
│   ├── position.py          # Position, PositionLot 模型
│   ├── transaction.py       # Transaction 模型
│   └── watchlist.py         # Watchlist 模型
│
├── storage/                 # 存储层
│   ├── __init__.py
│   ├── database.py          # Database 类 (引擎/会话管理)
│   └── repositories/        # 数据访问对象
│       ├── __init__.py
│       ├── position_repo.py
│       ├── transaction_repo.py
│       └── watchlist_repo.py
│
└── services/                # 业务层
    ├── __init__.py
    ├── portfolio_service.py   # 持仓业务逻辑
    ├── watchlist_service.py   # 收藏业务逻辑
    └── analysis_service.py    # 资产分析逻辑
```

---

## 使用方法

### 方式一：独立模块调用

```bash
# 查看持仓
python3 -m mystocks pos

# 买入股票
python3 -m mystocks buy 600519 --qty 100 --price 1500 --name "贵州茅台"

# 卖出股票
python3 -m mystocks sell 600519 --qty 50 --price 1600

# 收藏管理
python3 -m mystocks watch --add 000001 --name "平安银行" --tags "银行，蓝筹"
python3 -m mystocks watch --list

# 资产汇总
python3 -m mystocks summary

# 交易历史
python3 -m mystocks history --limit 20
```

### 方式二：通过 main.py 调用

```bash
# 通过主程序调用
python3 main.py mystocks pos
python3 main.py mystocks buy 600519 --qty 100 --price 1500 --name "贵州茅台"
python3 main.py mystocks summary
```

### 方式三：Python 代码调用

```python
from mystocks import MyStocks

# 使用上下文管理器（自动关闭连接）
with MyStocks() as ms:
    # 买入
    position = ms.buy(
        stock_code="600519",
        stock_name="贵州茅台",
        quantity=100,
        price=1500.0,
        commission=48.0
    )

    # 卖出
    ms.sell(
        stock_code="600519",
        quantity=50,
        price=1600.0
    )

    # 查看持仓
    positions = ms.get_all_positions()
    for p in positions:
        print(f"{p.stock_code}: {p.quantity}股，成本{p.avg_cost}")

    # 添加收藏
    ms.add_to_watchlist(
        stock_code="000001",
        stock_name="平安银行",
        tags="银行，蓝筹",
        target_price=12.5
    )

    # 资产汇总
    summary = ms.get_portfolio_summary()
    print(f"总市值：{summary['total_value']:.2f}")
    print(f"已实现盈亏：{summary['total_realized_profit']:.2f}")

    # 持仓集中度
    concentration = ms.get_concentration()
    print(f"HHI 指数：{concentration['herfindahl_index']:.3f}")
```

---

## 分层架构说明

### 模型层 (models/)

负责数据模型定义，使用 SQLAlchemy ORM：

| 模型 | 说明 |
|------|------|
| `Position` | 持仓表 |
| `PositionLot` | 持仓批次表（FIFO 成本计算） |
| `Transaction` | 交易记录表 |
| `Watchlist` | 收藏股表 |

### 存储层 (storage/)

负责数据库连接和数据访问：

| 组件 | 说明 |
|------|------|
| `Database` | 数据库引擎和会话管理 |
| `PositionRepository` | 持仓数据访问对象 |
| `WatchlistRepository` | 收藏股数据访问对象 |
| `TransactionRepository` | 交易记录数据访问对象 |

### 业务层 (services/)

负责业务逻辑处理：

| 服务 | 说明 |
|------|------|
| `PortfolioService` | 持仓管理（买入/卖出/查询） |
| `WatchlistService` | 收藏管理（添加/删除/更新） |
| `AnalysisService` | 资产分析（汇总/集中度/风险） |

### Facade (主入口)

`MyStocks` 类作为统一入口，采用 Facade 模式组合各服务层：

```python
class MyStocks:
    def __init__(self, db_path=None):
        self._db = Database(db_path)
        self._session = self._db.get_session()
        self._portfolio_service = PortfolioService(self._session)
        self._watchlist_service = WatchlistService(self._session)
        self._analysis_service = AnalysisService(self._session)
```

---

## API 参考

### MyStocks 类

#### 初始化
```python
ms = MyStocks(db_path=None)  # db_path 默认为 DATABASE_PATH
```

#### 持仓管理方法
| 方法 | 说明 |
|------|------|
| `buy(stock_code, stock_name, quantity, price, commission, notes)` | 买入股票 |
| `sell(stock_code, quantity, price, commission, notes)` | 卖出股票（FIFO） |
| `get_position(stock_code)` | 获取单个持仓 |
| `get_all_positions()` | 获取所有持仓 |
| `get_transactions(stock_code, limit)` | 获取交易历史 |

#### 收藏管理方法
| 方法 | 说明 |
|------|------|
| `add_to_watchlist(stock_code, stock_name, tags, notes, target_price, stop_loss)` | 添加收藏 |
| `remove_from_watchlist(stock_code)` | 删除收藏 |
| `get_watchlist(tag)` | 获取收藏列表 |
| `update_watchlist(stock_code, tags, notes, target_price, stop_loss)` | 更新收藏信息 |

#### 资产分析方法
| 方法 | 说明 |
|------|------|
| `get_portfolio_summary()` | 获取持仓汇总 |
| `get_concentration()` | 计算持仓集中度 |
| `get_position_weights()` | 计算各持仓权重 |
| `get_risk_exposure()` | 计算风险敞口 |
| `calculate_commission(amount, operation)` | 计算手续费 |

#### 工具方法
| 方法 | 说明 |
|------|------|
| `sync_prices(price_fetcher)` | 同步最新股价 |
| `export_data(format)` | 导出数据 |
| `close()` | 关闭会话 |

---

## 手续费计算

手续费按照 `config/settings.py` 中的 `TRADING_FEES` 配置计算：

```python
TRADING_FEES = {
    "stamp_duty": 0.0005,      # 印花税（卖出收取 0.05%）
    "exchange_fee": 0.00002,   # 交易所规费（0.002%）
    "broker_commission": 0.00025,  # 券商佣金（0.025%）
    "min_commission": 5.0      # 最低佣金 5 元
}
```

---

## 注意事项

1. **数据库路径**: 默认使用 `config/settings.py` 中的 `DATABASE_PATH`
2. **线程安全**: SQLite 设置 `check_same_thread=False` 以支持多线程
3. **FIFO 成本**: 卖出时自动按最早买入批次扣减（FIFO）
4. **手续费**: 自动计入持仓成本，实现盈亏计算时扣除
5. **清仓处理**: 当持仓数量为 0 时自动删除持仓记录

---

## 示例输出

### 持仓列表
```
═══════════════════════════════════════════════════════
  持仓列表
═══════════════════════════════════════════════════════

📌 600519 (贵州茅台)
   持仓：100 股
   成本价：¥1500.48
   当前价：¥1500.00
   市值：¥150000.00
   盈亏：¥-48.00 (-0.0%)
   实现盈亏：¥+0.00

───────────────────────────────────────────────────────
合计 市值：¥150525.00
合计 成本：¥150575.51
合计 盈亏：¥-50.51 (-0.0%)
持仓数量：2 只

持仓集中度 (HHI): 0.993
前三大持仓占比：100.0%
═══════════════════════════════════════════════════════
```

### 资产汇总
```
═══════════════════════════════════════════════════════
  资产汇总
═══════════════════════════════════════════════════════

💰 总市值：¥150525.00
📊 总成本：¥150575.51
📈 浮动盈亏：¥-50.51 (-0.0%)
💵 已实现盈亏：¥+69.69
📦 持仓数量：2 只

───────────────────────────────────────────────────────
持仓集中度 (HHI): 0.993
前三大持仓占比：100.0%
最大单一持仓：99.7%
═══════════════════════════════════════════════════════
```
