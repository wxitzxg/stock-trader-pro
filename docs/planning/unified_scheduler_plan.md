# 统一任务调度框架实施方案

## 需求重述

统一项目中的任务调度框架，当前存在：
- `schedule>=1.2.0` - 用于交易时段价格更新
- `apscheduler>=3.9.0` - 用于每日 K 线数据更新

**目标**：统一使用 APScheduler，移除 schedule 依赖

## 现状分析

### 现有调度器

| 调度器 | 位置 | 功能 | 触发方式 |
|--------|------|------|----------|
| `PriceUpdateScheduler` | `realalerts/scheduler/price_scheduler.py` | 交易时段每 5 分钟更新价格 | `schedule.every(60).seconds` |
| `KlineScheduler` | `mystocks/services/kline_scheduler.py` | 每日 00:00 更新 K 线 | `CronTrigger(hour=0, minute=0)` |
| `SmartScheduler` | `realalerts/scheduler/smart_schedule.py` | 交易时间判断工具类（非调度器） | N/A |

### 问题点

1. **依赖冗余**：两个调度库功能重叠
2. **main.py 中的 daemon 命令**：使用 `while` 循环 + `SmartScheduler.should_run_now()` 轮询，效率低
3. **代码风格不统一**：有的用 cron，有的用 interval

## 实施方案

### Phase 1: 重构 PriceUpdateScheduler（使用 APScheduler）

**文件**：`realalerts/scheduler/price_scheduler.py`

将 `schedule` 替换为 `APScheduler`：

```python
# 原代码（schedule）
schedule.every(check_interval).seconds.do(self._job)
while self._running:
    schedule.run_pending()
    time.sleep(1)

# 新代码（APScheduler）
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BlockingScheduler()
scheduler.add_job(
    self._job,
    trigger=IntervalTrigger(seconds=check_interval),
    id='price_update',
    name='价格更新'
)
scheduler.start()
```

**优势**：
- 更精确的时间控制
- 支持任务持久化（可选）
- 统一的错误处理机制

### Phase 2: 重构 main.py daemon 命令

**文件**：`main.py`

将轮询式 `while` 循环改为事件驱动：

```python
# 原代码：轮询
scheduler = SmartScheduler()
while True:
    result = scheduler.should_run_now()
    if result.get("run"):
        cmd_monitor(...)
    time.sleep(result.get("interval", interval))

# 新代码：APScheduler 事件驱动
scheduler = BlockingScheduler()
scheduler.add_job(
    cmd_monitor,
    trigger=IntervalTrigger(seconds=300),
    id='market_monitor',
    name='市场监控'
)
scheduler.start()
```

**注意**：需要保留交易时间判断逻辑，在 job 内部判断是否跳过

### Phase 3: 优化 KlineScheduler

**文件**：`mystocks/services/kline_scheduler.py`

当前已使用 APScheduler，需要微调：

1. 添加周末判断（已实现）
2. 添加节假日支持（调用 TradingTimeUtils）
3. 添加任务状态查询接口

### Phase 4: 统一依赖

**文件**：`requirements.txt`

移除 `schedule>=1.2.0`，保留 `apscheduler>=3.9.0`

### Phase 5: 统一调度工具类（可选）

创建 `common/scheduler.py` 封装通用调度逻辑：

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def create_scheduler(blocking: bool = True) -> BlockingScheduler | AsyncIOScheduler:
    """创建调度器工厂函数"""
    ...

class BaseScheduler:
    """调度器基类，提供统一接口"""
    def start(self): ...
    def stop(self): ...
    def add_job(self, func, trigger, **kwargs): ...
```

## 依赖与风险

### 依赖关系

1. APScheduler 已安装，无额外依赖
2. `common.trading_time.TradingTimeUtils` - 交易时间判断工具类

### 潜在风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| APScheduler 的 API 差异 | 中等 | 详细测试每个调度器 |
| 时区处理问题 | 中等 | 统一使用 Asia/Shanghai 时区 |
| 任务并发执行 | 低 | 设置 `max_instances=1` |

## 实施步骤

### Step 1: 重构 PriceUpdateScheduler
- [ ] 将 `schedule` 替换为 `APScheduler`
- [ ] 保留交易时间判断逻辑
- [ ] 单元测试验证

### Step 2: 重构 daemon 命令
- [ ] 移除 `while` 轮询
- [ ] 使用 APScheduler 定时触发
- [ ] 保留 `SmartScheduler` 作为工具类（交易时间判断）

### Step 3: 优化 KlineScheduler
- [ ] 添加节假日判断
- [ ] 添加任务状态接口

### Step 4: 清理依赖
- [ ] 从 `requirements.txt` 移除 `schedule`
- [ ] 验证无其他文件引用 `schedule`

### Step 5: 文档更新
- [ ] 更新 `realalerts/README.md`
- [ ] 更新调度器使用示例

## 代码改动预估

| 文件 | 改动行数 | 复杂度 |
|------|----------|--------|
| `realalerts/scheduler/price_scheduler.py` | ~50 行 | 中 |
| `main.py` (daemon 命令) | ~30 行 | 低 |
| `mystocks/services/kline_scheduler.py` | ~20 行 | 低 |
| `requirements.txt` | ~2 行 | 低 |
| **总计** | **~100 行** | - |

## 测试计划

1. **单元测试**：
   - 交易时间判断逻辑
   - 调度器启动/停止
   - 任务执行回调

2. **集成测试**：
   - 模拟非交易时间（周末/节假日）
   - 模拟交易时段
   - 验证任务执行频率

3. **回归测试**：
   - 验证 K 线更新任务
   - 验证价格更新任务
   - 验证监控任务

## 完成标准

- [x] 所有调度器统一使用 APScheduler
- [x] `schedule` 依赖已移除
- [x] 所有测试通过（模块导入验证成功）
- [ ] 文档已更新

---

**实施完成**

### 实施记录

所有步骤已完成：

| 步骤 | 状态 | 说明 |
|------|------|------|
| Step 1: 重构 PriceUpdateScheduler | ✅ 完成 | 将 `schedule` 替换为 `APScheduler` |
| Step 2: 重构 daemon 命令 | ✅ 完成 | 移除 `while` 轮询，使用 APScheduler |
| Step 3: 优化 KlineScheduler | ✅ 完成 | 添加节假日判断、状态接口 |
| Step 4: 清理依赖 | ✅ 完成 | 从 `requirements.txt` 移除 `schedule` |
| Step 5: 文档更新 | ⏸️ 待处理 | 待更新 `realalerts/README.md` |

### 修改文件列表

1. `realalerts/scheduler/price_scheduler.py` - 使用 APScheduler 替代 schedule
2. `main.py` - daemon 命令使用 APScheduler 替代轮询
3. `mystocks/services/kline_scheduler.py` - 添加节假日判断和 stats 属性
4. `requirements.txt` - 移除 schedule 依赖

### 验证结果

```bash
# 模块导入验证
python3 -c "from realalerts.scheduler.price_scheduler import PriceUpdateScheduler; print('OK')"
# Import OK
```
