# 实施计划：AKShare 历史 K 线数据本地缓存

**创建日期**: 2026-03-14
**状态**: 待实施

---

## 需求确认

为 `stockquery` 模块的 AKShare 历史 K 线数据获取功能添加本地数据库缓存：

- **缓存范围**：仅 AKShare 的 `get_historical_data()` 方法
- **缓存存储**：本地 SQLite 数据库 `investment.db`（与现有 `mystocks` 模块共用）
- **缓存有效期**：24 小时（从缓存写入时间开始计算）
- **缓存粒度**：按 `symbol + start_date + end_date + period + adjust` 作为缓存 key
- **缓存统计**：不需要
- **目的**：减少 AKShare API 调用频率，提高数据获取稳定性和响应速度

---

## 当前架构分析

```
stockquery/
├── sources/
│   ├── base.py              # BaseDataSource 基类
│   ├── akshare_source.py    # AKShareDataSource (需修改)
│   ├── eastmoney_source.py
│   └── sina_source.py
├── unified_service.py       # UnifiedStockQueryService
└── models.py

mystocks/
├── storage/
│   ├── database.py          # Database 管理类
│   └── repositories/
│       ├── base.py          # BaseRepository 基类
│       ├── account_repo.py
│       └── ...
└── models/
    ├── base.py              # SQLAlchemy Base
    └── ...
```

---

## 实施阶段

### Phase 1: 数据模型设计
**文件**: `mystocks/models/kline_cache.py` (新建)

创建 K 线缓存数据模型：

```python
class KlineCache(Base):
    """AKShare K 线数据缓存"""
    __tablename__ = 'kline_cache'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)   # 股票代码
    start_date = Column(String(10), nullable=False)           # YYYYMMDD
    end_date = Column(String(10), nullable=False)             # YYYYMMDD
    period = Column(String(20), nullable=False)               # daily/weekly/monthly
    adjust = Column(String(10), nullable=False)               # qfq/hfq/none
    data_json = Column(Text, nullable=False)                  # K 线数据 JSON
    cached_at = Column(DateTime, nullable=False)              # 缓存时间
    expires_at = Column(DateTime, nullable=False)             # 过期时间

    # 唯一约束：相同参数的缓存只保留一份
    __table_args__ = (
        UniqueConstraint('symbol', 'start_date', 'end_date', 'period', 'adjust',
                        name='uq_kline_cache_unique')
    )
```

### Phase 2: 缓存 Repository 实现
**文件**: `mystocks/storage/repositories/kline_cache_repo.py` (新建)

实现缓存操作仓库：

```python
class KlineCacheRepository(BaseRepository):
    """K 线缓存仓库"""

    def get_cache(self, symbol, start_date, end_date, period, adjust) -> Optional[Dict]
    """获取未过期的缓存数据"""

    def set_cache(self, symbol, start_date, end_date, period, adjust, data, ttl_hours=24)
    """设置缓存，TTL 默认 24 小时"""

    def delete_cache(self, symbol, start_date, end_date, period, adjust)
    """删除指定缓存"""

    def cleanup_expired(self)
    """清理所有过期缓存（可选，惰性清理）"""
```

### Phase 3: AKShare 数据源集成缓存
**文件**: `stockquery/sources/akshare_source.py` (修改)

修改 `AKShareDataSource` 类：

```python
class AKShareDataSource(BaseDataSource):

    def __init__(self, db=None, cache_enabled: bool = True, cache_ttl_hours: int = 24):
        """
        初始化 AKShare 数据源

        Args:
            db: Database 实例（用于缓存）
            cache_enabled: 是否启用缓存
            cache_ttl_hours: 缓存有效期（小时）
        """
        self.db = db
        self.cache_enabled = cache_enabled
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_repo = KlineCacheRepository(db.get_session()) if db and cache_enabled else None

    def get_historical_data(self, symbol, start_date, end_date, period, adjust):
        """
        获取股票历史数据（带缓存）

        缓存逻辑：
        1. 检查缓存是否启用
        2. 查询缓存，如未过期则直接返回
        3. 缓存过期或不存在，调用 AKShare API
        4. 将新数据写入缓存
        5. 返回数据
        """
```

### Phase 4: 配置项添加
**文件**: `config/settings.py` (修改)

在配置文件中添加缓存配置：

```python
# ========== K 线缓存配置 ==========
KLINE_CACHE_ENABLED = True       # 是否启用缓存
KLINE_CACHE_TTL_HOURS = 24       # 缓存有效期（小时）
```

---

## 依赖关系

```
Phase 1 (模型)
    ↓
Phase 2 (Repository)
    ↓
Phase 3 (集成缓存)
    ↓
Phase 4 (配置)
```

---

## 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 数据库连接异常 | LOW | try-except 包裹，失败时降级到 API 直连 |
| 缓存数据序列化失败 | LOW | DataFrame to_json 使用 orient='split' 保证精度 |
| 缓存与实时数据不一致 | LOW | 24 小时有效期，盘后自动失效 |

---

## 测试要点

1. **缓存命中**：相同参数第二次调用，返回缓存数据
2. **缓存过期**：超过 24 小时后调用，重新获取并刷新缓存
3. **缓存降级**：数据库不可用时，直接调用 API 不报错
4. **参数隔离**：不同股票代码、日期范围、复权类型的缓存互不干扰

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `mystocks/models/kline_cache.py` | 新建 | K 线缓存模型 |
| `mystocks/models/__init__.py` | 修改 | 导出 KlineCache |
| `mystocks/storage/repositories/kline_cache_repo.py` | 新建 | 缓存仓库 |
| `mystocks/storage/repositories/__init__.py` | 修改 | 导出 KlineCacheRepository |
| `stockquery/sources/akshare_source.py` | 修改 | 集成缓存逻辑 |
| `config/settings.py` | 修改 | 添加缓存配置 |

---

## 验收标准

- [ ] 首次调用 `get_historical_data()` 时，数据写入缓存
- [ ] 24 小时内相同参数调用，直接返回缓存数据
- [ ] 超过 24 小时后调用，重新获取并刷新缓存
- [ ] 数据库不可用时，功能降级但不影响使用
- [ ] 所有现有测试通过
