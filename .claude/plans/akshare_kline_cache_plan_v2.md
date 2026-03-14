# 实施计划：AKShare K 线历史数据本地缓存（v2）

**创建日期**: 2026-03-14
**状态**: 已完成

---

## 需求重述

1. **结构化存储**：K 线数据按字段存储到数据库表（非 JSON blob）
2. **定时任务**：每天凌晨 12 点使用 APScheduler 自动获取昨天的 K 线数据并更新
3. **初始化功能**：支持一键初始化持仓股/收藏股 K 线数据（默认 250 天），支持指定股票 + 天数初始化
4. **查询优先数据库**：所有 K 线查询优先从数据库读取，没有时调用 AKShare 并同步保存
5. **周期支持**：支持 daily/weekly/monthly 三种周期

---

## 实施阶段

### Phase 1: K 线数据表模型
**文件**: `mystocks/models/kline.py` (新建)

```python
class Kline(Base):
    """K 线数据表 - 结构化存储"""
    __tablename__ = "klines"

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(20), nullable=False, index=True)  # 股票代码
    date = Column(String(10), nullable=False)                     # 交易日期 YYYYMMDD
    period = Column(String(10), nullable=False, default='daily')  # 周期 daily/weekly/monthly
    adjust = Column(String(10), nullable=False, default='qfq')    # 复权 qfq/hfq/none

    # K 线数据字段
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    amount = Column(Float, nullable=True)      # 成交额
    amplitude = Column(Float, nullable=True)   # 振幅
    pct_change = Column(Float, nullable=True)  # 涨跌幅
    change = Column(Float, nullable=True)      # 涨跌额
    turnover = Column(Float, nullable=True)    # 换手率

    # 数据来源和更新时间
    source = Column(String(20), default='akshare')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 唯一约束：同一股票 + 日期 + 周期 + 复权类型只保留一条
    __table_args__ = (
        UniqueConstraint('stock_code', 'date', 'period', 'adjust',
                        name='uq_kline_unique')
    )
```

### Phase 2: K 线 Repository
**文件**: `mystocks/storage/repositories/kline_repo.py` (新建)

```python
class KlineRepository(BaseRepository):
    """K 线数据仓库"""

    def get_klines(self, symbol, start_date, end_date, period='daily', adjust='qfq') -> List[Kline]
    """查询 K 线数据"""

    def get_klines_df(self, symbol, start_date, end_date, period='daily', adjust='qfq') -> pd.DataFrame
    """查询 K 线并返回 DataFrame（兼容现有接口）"""

    def upsert_klines(self, symbol, klines_data, period='daily', adjust='qfq')
    """批量插入或更新 K 线数据"""

    def get_latest_date(self, symbol, period='daily', adjust='qfq') -> str
    """获取某股票最新的 K 线日期"""

    def get_missing_dates(self, symbol, start_date, end_date, period='daily', adjust='qfq') -> List[str]
    """获取缺失的交易日期"""
```

### Phase 3: 定时任务调度器 (APScheduler)
**文件**: `mystocks/services/kline_scheduler.py` (新建)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

class KlineScheduler:
    """K 线定时任务调度器"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.kline_service = KlineService()

    def start(self):
        # 每天凌晨 12 点执行
        self.scheduler.add_job(
            self.run_daily_update,
            CronTrigger(hour=0, minute=0),
            id='daily_kline_update'
        )
        self.scheduler.start()

    def run_daily_update(self):
        """
        每日凌晨 12 点执行
        获取所有持仓股和收藏股的昨天 K 线数据并更新
        """
```

### Phase 4: K 线初始化服务
**文件**: `mystocks/services/kline_init_service.py` (新建)

```python
class KlineInitService:
    """K 线数据初始化服务"""

    def init_position_klines(self, days: int = 250)
    """一键初始化所有持仓股的 K 线数据（默认 250 天）"""

    def init_watchlist_klines(self, days: int = 250)
    """一键初始化所有收藏股的 K 线数据（默认 250 天）"""

    def init_symbol_klines(self, symbol: str, days: int = 250)
    """初始化指定股票的 K 线数据"""
```

### Phase 5: AKShare 数据源改造
**文件**: `stockquery/sources/akshare_source.py` (修改)

```python
class AKShareDataSource(BaseDataSource):
    """AKShare 数据源 - 带数据库缓存"""

    def __init__(self, db=None):
        self.db = db
        self.kline_repo = KlineRepository(db.get_session()) if db else None

    def get_historical_data(self, symbol, start_date, end_date, period, adjust):
        """
        获取历史 K 线数据
        1. 优先从数据库查询
        2. 数据库没有时，调用 AKShare API
        3. 同步保存新数据到数据库
        """
```

### Phase 6: 统一服务改造
**文件**: `stockquery/unified_service.py` (修改)

修改 `get_historical_data()` 方法，确保调用 AKShare 时能利用数据库缓存。

### Phase 7: 配置项添加
**文件**: `config/settings.py` (修改)

```python
# ========== K 线缓存配置 ==========
KLINE_CACHE_ENABLED = True           # 是否启用数据库缓存
KLINE_DEFAULT_DAYS = 250             # 默认初始化天数
KLINE_DAILY_UPDATE_TIME = "00:00"    # 每日更新时间
```

### Phase 8: 命令行脚本
**文件**: `scripts/init_kline_data.py` (新建)

```python
#!/usr/bin/env python3
"""
K 线数据初始化脚本

用法:
    python scripts/init_kline_data.py --position --days 250   # 初始化持仓股
    python scripts/init_kline_data.py --watchlist --days 250  # 初始化收藏股
    python scripts/init_kline_data.py --symbol 601857 --days 250  # 指定股票
```

---

## 依赖关系

```
Phase 1 (模型)
    ↓
Phase 2 (Repository)
    ↓
Phase 5 (AKShare 改造) ← Phase 4 (初始化服务)
    ↓                        ↓
Phase 6 (统一服务)      Phase 8 (命令行脚本)
    ↓
Phase 3 (定时任务)
    ↓
Phase 7 (配置)
```

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `mystocks/models/kline.py` | 新建 | K 线数据模型 |
| `mystocks/models/__init__.py` | 修改 | 导出 Kline |
| `mystocks/storage/repositories/kline_repo.py` | 新建 | K 线仓库 |
| `mystocks/storage/repositories/__init__.py` | 修改 | 导出 KlineRepository |
| `mystocks/services/kline_scheduler.py` | 新建 | 定时调度器 |
| `mystocks/services/kline_init_service.py` | 新建 | 初始化服务 |
| `mystocks/services/__init__.py` | 修改 | 导出新服务 |
| `stockquery/sources/akshare_source.py` | 修改 | 集成数据库缓存 |
| `stockquery/unified_service.py` | 修改 | 调用链适配 |
| `config/settings.py` | 修改 | 添加 K 线配置 |
| `scripts/init_kline_data.py` | 新建 | 初始化脚本 |
| `scripts/daily_kline_update.py` | 新建 | 定时任务脚本 |

---

## 验收标准

- [x] K 线数据表创建成功，字段完整
- [x] 查询 K 线优先从数据库读取
- [x] 数据库无数据时自动调用 AKShare 并保存
- [x] 一键初始化持仓股 K 线数据正常工作（默认 250 天）
- [x] 一键初始化收藏股 K 线数据正常工作（默认 250 天）
- [x] 指定股票初始化功能正常工作
- [x] 定时任务使用 APScheduler 并正确执行（每天 00:00）
- [x] 支持 daily/weekly/monthly 三种周期
- [x] 现有功能不受影响

---

## 依赖项

需要在 `requirements.txt` 中添加：
```
APScheduler>=3.9.0
```
