# 账户管理与交易系统功能文档

## 功能概述

本次更新新增了完整的账户管理与交易系统，实现了资金流与持仓的联动管理。

---

## 新增功能

### 1. 账户管理（My Account）

#### 功能说明
- 追踪当前现金余额
- 计算持仓总市值
- 统计盈亏金额（浮动盈亏 + 已实现盈亏）
- 计算仓位比

#### 核心指标

| 指标 | 计算公式 |
|------|---------|
| 当前现金 | 账户现金余额 |
| 持仓市值 | ∑(持仓数量 × 当前股价) |
| 总资产 | 持仓市值 + 当前现金 |
| 仓位比 | 持仓市值 / 总资产 |
| 浮动盈亏 | ∑(当前价 - 成本价) × 数量 |
| 已实现盈亏 | 累计卖出实现盈亏 |
| 总盈亏 | 浮动盈亏 + 已实现盈亏 |

#### CLI 命令

```bash
# 显示账户总览
python3 main.py account

# 存入现金
python3 main.py account --deposit 100000

# 取出现金
python3 main.py account --withdraw 10000
```

#### 输出示例

```
═══════════════════════════════════════════════════════
  账户总览 - 默认账户
═══════════════════════════════════════════════════════

📊 资产信息
   当前现金：¥252,500.00
   持仓市值：¥135,814.00
   总资产：¥388,314.00

📈 仓位信息
   仓位比：35.0%
   累计投入：¥100,000.00

💰 盈亏信息
   浮动盈亏：¥-2,293.80 (-1.7%)
   已实现盈亏：¥+12,500.00
   总盈亏：¥+10,206.20

═══════════════════════════════════════════════════════
```

---

### 2. 持仓详情（Holdings）

#### 功能说明
- 自动获取最新股价
- 计算每只股票的浮动盈亏
- 显示仓位比（每只股票占总资产比例）

#### CLI 命令

```bash
# 显示持仓详情
python3 main.py holdings

# 刷新最新股价后显示
python3 main.py holdings --refresh
```

#### 输出示例

```
═══════════════════════════════════════════════════════
  持仓详情
═══════════════════════════════════════════════════════

📌 000858 (五粮液)
   持仓：150 股
   成本价：¥165.00
   当前价：¥168.50
   市值：¥25,275.00
   浮动盈亏：¥+525.00 (+2.1%)
   仓位比：6.5%

📌 600519 (贵州茅台)
   持仓：100 股
   成本价：¥1500.00
   当前价：¥1520.00
   市值：¥152,000.00
   浮动盈亏：¥+2,000.00 (+1.3%)
   仓位比：39.2%

═══════════════════════════════════════════════════════
```

---

### 3. 清仓功能（Sell All）

#### 功能说明
- 一键卖出全部持仓
- 自动计算已实现盈亏
- 更新账户现金和累计盈亏

#### CLI 命令

```bash
# 清仓卖出（自动获取持仓数量）
python3 main.py portfolio --sell --symbol 600519 --price 1650 --all

# 部分卖出
python3 main.py portfolio --sell --symbol 600519 --price 1650 --qty 50
```

---

## 数据联动机制

### 买入操作

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Account       │────▶│   Transaction   │────▶│   Position      │
│   cash -= cost  │     │   Create record │     │   Add/Update    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**影响**：
- 现金余额 ↓
- 持仓数量 ↑
- 总资产不变（现金转换为股票）

### 卖出操作

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Position      │────▶│   Transaction   │────▶│   Account       │
│   Reduce        │     │   Calc P/L      │     │   cash += proceeds │
│                 │     │   Record P/L    │     │   realized_pnl += P/L │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**影响**：
- 现金余额 ↑
- 持仓数量 ↓
- 已实现盈亏更新
- 总资产 = 新现金 + 剩余持仓市值

### 价格更新

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   External API  │────▶│   Position      │────▶│   Account       │
│   Fetch price   │     │   Update price  │     │   Update        │
│                 │     │   Recalc P/L    │     │   unrealized    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**影响**：
- 浮动盈亏更新
- 持仓市值更新
- 总资产更新
- 仓位比重新计算

---

## 技术实现

### 数据模型

#### Account（账户表）

```python
class Account(Base):
    id: int                      # 主键
    name: str                    # 账户名称
    cash_balance: float          # 当前现金
    total_invested: float        # 累计投入本金
    total_realized_pnl: float    # 累计已实现盈亏
    created_at: datetime
    updated_at: datetime
```

### 服务层

| 服务类 | 职责 |
|--------|------|
| AccountService | 账户管理、存款、取款、总览计算 |
| PortfolioService | 买入、卖出、持仓管理 |
| AccountRepository | 账户数据访问 |

### 核心方法

```python
# AccountService
get_account_summary()       # 获取账户总览
get_holdings_with_details() # 获取持仓详情
deposit(amount)             # 存入现金
withdraw(amount)            # 取出现金

# PortfolioService
buy(stock_code, quantity, price, account_id)  # 买入
sell(stock_code, quantity, price, account_id) # 卖出
```

---

## 使用流程

### 初始化账户

```bash
# 1. 存入初始资金
python3 main.py account --deposit 100000

# 2. 查看账户总览
python3 main.py account
```

### 买入股票

```bash
# 买入 100 股贵州茅台
python3 main.py portfolio --buy --symbol 600519 --name "贵州茅台" --qty 100 --price 1500
```

### 查看持仓

```bash
# 查看持仓详情（含仓位比）
python3 main.py holdings
```

### 卖出/清仓

```bash
# 清仓卖出
python3 main.py portfolio --sell --symbol 600519 --price 1650 --all

# 部分卖出
python3 main.py portfolio --sell --symbol 600519 --price 1650 --qty 50
```

---

## 数据库迁移

执行迁移脚本添加 Account 表：

```bash
python3 scripts/migrate_add_account.py
```

---

## 测试验证

运行测试脚本验证功能：

```bash
python3 test_account_feature.py
```

测试覆盖：
- 存款/取款
- 买入操作（现金扣减）
- 卖出操作（现金增加、已实现盈亏计算）
- 清仓操作
- 账户总览计算
- 持仓详情和仓位比计算

---

## 注意事项

1. **现金余额检查**：买入时会自动检查现金余额，不足会报错
2. **取款限制**：取款金额不能超过当前现金余额
3. **负成本支持**：保留了原有的负成本计算逻辑
4. **FIFO 成本计算**：卖出时按先进先出原则计算成本
5. **单账户模式**：当前默认使用"默认账户"，后续可扩展多账户

---

## 文件清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `mystocks/models/account.py` | Account 模型 |
| `mystocks/storage/repositories/account_repo.py` | Account 数据仓库 |
| `mystocks/services/account_service.py` | 账户业务逻辑 |
| `commands/account.py` | account/holdings命令 |
| `scripts/migrate_add_account.py` | 数据库迁移脚本 |
| `test_account_feature.py` | 功能测试脚本 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `mystocks/__init__.py` | 添加 Account 模型导出，增加账户服务方法 |
| `mystocks/services/__init__.py` | 导出 AccountService |
| `mystocks/services/portfolio_service.py` | buy/sell 方法增加账户集成 |
| `mystocks/models/__init__.py` | 导出 Account 模型 |
| `mystocks/storage/repositories/__init__.py` | 导出 AccountRepository |
| `commands/__init__.py` | 导出新命令处理函数 |
| `commands/portfolio.py` | 增加--all清仓参数 |
| `main.py` | 注册 account/holdings 命令 |
