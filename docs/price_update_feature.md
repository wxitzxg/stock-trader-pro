# 持仓价格定时更新功能

## 功能概述

为股票模块新增持仓股现价定时更新功能，基于 `schedule` 库实现调度，**只在交易时间执行更新**。

## 核心特性

1. **交易时间判断**：使用统一的 `TradingTimeUtils` 工具类
   - 自动识别工作日/周末
   - 自动识别法定节假日（配置在 `config/trading_calendar.py`）
   - 支持调休工作日识别
   - 交易时段：09:30-11:30, 13:00-15:00（北京时间）

2. **智能调度**：
   - 非交易时间自动跳过更新
   - 可配置检查间隔（默认 60 秒）
   - 可配置更新频率（默认 300 秒，交易时间内每 5 分钟更新一次）

3. **盈亏自动计算**：
   - 支持正成本：标准盈亏公式
   - 支持负成本：特殊规则（不计算盈亏率）

## 文件结构

```
config/
├── trading_calendar.py      # 交易日历配置（节假日、调休日）
└── settings.py              # 主配置（含价格更新配置）

common/
├── __init__.py
└── trading_time.py          # 交易时间判断工具类

realalerts/scheduler/
├── smart_schedule.py        # 智能调度器（使用 TradingTimeUtils）
└── price_scheduler.py       # 价格更新调度器（基于 schedule 库）

mystocks/services/
└── price_update_service.py  # 价格更新服务

commands/
└── update_prices.py         # 命令行工具
```

## 使用方法

### 1. 启动调度器（持续运行）

```bash
# 默认模式：持续运行，只在交易时间更新
python3 -m mystocks update-prices
```

### 2. 执行一次更新

```bash
# 立即执行一次更新（忽略交易时间）
python3 -m mystocks update-prices --once

# 更新指定股票
python3 -m mystocks update-prices --once --stock-code 300003
```

### 3. 指定更新频率

```bash
# 指定更新间隔为 600 秒（10 分钟）
python3 -m mystocks update-prices --interval 600
```

### 4. 详细日志

```bash
# 输出详细日志
python3 -m mystocks update-prices -v

# 输出到日志文件
python3 -m mystocks update-prices --log ./price_update.log
```

## 配置说明

### config/settings.py

```python
MONITOR_CONFIG = {
    # 价格更新配置
    "price_update_enabled": True,           # 是否启用价格更新
    "price_update_check_interval": 60,      # 检查间隔（秒）
    "price_update_interval_market": 300,    # 交易时段更新频率（秒）
}
```

### config/trading_calendar.py

```python
# 2026 年 A 股法定节假日
CHINA_HOLIDAYS_2026 = {
    "2026-01-01": "元旦",
    "2026-02-17": "春节",
    # ...
}

# 2026 年调休工作日（周末需要上班）
CHINA_MAKEUP_WORKDAYS_2026 = {
    # 如有调休，在此配置
}
```

## 交易时间规则

| 条件 | 结果 | 说明 |
|------|------|------|
| 周六/周日 | 非交易日 | 自动跳过 |
| 法定节假日 | 非交易日 | 自动跳过 |
| 调休工作日 | 交易日 | 虽然是周末，但是开市 |
| 09:30-11:30 | 交易时段 | 更新价格 |
| 13:00-15:00 | 交易时段 | 更新价格 |
| 其他时间 | 非交易时段 | 跳过更新 |

## 代码复用

### realalerts 预警模块

```python
from common.trading_time import TradingTimeUtils

# 判断是否交易时间
result = TradingTimeUtils.is_trading_time()
if result["is_trading"]:
    # 执行预警逻辑
    pass
```

### mystocks 价格更新模块

```python
from common.trading_time import TradingTimeUtils

# 判断是否应该更新价格
if not TradingTimeUtils.is_trading_time()["is_trading"]:
    return {"skipped": True, "reason": "非交易时间"}
```

## 日志示例

```
2026-03-13 10:30:00,123 - commands.update_prices - INFO - 启动价格更新调度器 - 检查间隔：60 秒，更新频率：300 秒
2026-03-13 10:30:01,456 - commands.update_prices - INFO - 开始更新持仓价格（交易时间：market）
2026-03-13 10:30:02,789 - commands.update_prices - INFO - 价格更新完成 - 成功：3, 失败：0, 总计：3
2026-03-13 10:35:01,123 - commands.update_prices - INFO - 跳过价格更新：午休时间 (13:00 开盘)
```

## 测试

运行单元测试：

```bash
python3 -m unittest test_trading_time -v
```

测试覆盖：
- 节假日配置读取
- 调休工作日识别
- 交易时间判断
- 市场阶段识别

## 依赖

```
schedule>=1.2.0
```

已在 `requirements.txt` 中添加。
