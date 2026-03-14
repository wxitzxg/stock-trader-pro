# StockQuery 模块

统一股票查询服务 - 整合 AKShare、东方财富、新浪财经三个数据源

## 架构

```
stockquery/
├── __init__.py              # 模块入口，导出统一接口
├── unified_service.py       # 统一服务类
├── models.py                # 数据模型
├── sources/                 # 数据源层
│   ├── __init__.py
│   ├── base.py              # 基类 BaseDataSource
│   ├── akshare_source.py    # AKShare 数据源
│   ├── eastmoney_source.py  # 东方财富数据源
│   └── sina_source.py       # 新浪财经数据源
```

## 统一服务路由策略

| 方法 | 主数据源 | 备选数据源 |
|------|----------|------------|
| `get_quote()` | 新浪财经 | AKShare |
| `get_historical_data()` | AKShare | - |
| `get_stock_info()` | 东方财富 | AKShare |
| `get_fund_flow()` | AKShare | - |
| `get_sector_rank()` | 东方财富 | AKShare |
| `search_stock()` | AKShare | - |

## 使用示例

### 使用统一服务类

```python
from stockquery import UnifiedStockQueryService

service = UnifiedStockQueryService()

# 获取实时行情
quote = service.get_quote("600519")

# 获取历史 K 线
hist = service.get_historical_data("600519", start_date="20250101", end_date="20250311")

# 获取股票信息
info = service.get_stock_info("600519")

# 获取资金流向
flow = service.get_fund_flow("600519")

# 获取板块排行
sector = service.get_sector_rank(sector_type=1, limit=20)

# 搜索股票
results = service.search_stock("茅台")

# 获取综合数据（一键获取所有数据）
data = service.get_comprehensive_data("600519", include_historical=True)
print(f"行情来源：{data.metadata['sources'].get('quote')}")
print(f"股票信息来源：{data.metadata['sources'].get('stock_info')}")
```

### 使用便捷函数

```python
from stockquery import get_default_service

service = get_default_service()
quote = service.get_quote("600519")
```

## 数据模型

```python
from stockquery.models import QuoteData, StockInfo, UnifiedStockData

# QuoteData - 实时行情
@dataclass
class QuoteData:
    source: str
    code: str
    name: str
    price: float
    change: float
    change_percent: float
    open: float
    high: float
    low: float
    volume: int
    amount: float
    market: str
    date: str
    time: str

# StockInfo - 股票基本信息
@dataclass
class StockInfo:
    source: str
    symbol: str
    name: str
    market: str
    industry: str
    pe_ratio: float
    pb_ratio: float
    market_cap: float
    float_cap: float
    total_shares: float
    float_shares: float

# UnifiedStockData - 统一股票数据（整合所有数据源）
@dataclass
class UnifiedStockData:
    quote: Optional[QuoteData]
    stock_info: Optional[StockInfo]
    historical: Optional[pd.DataFrame]
    fund_flow: Optional[Dict[str, Any]]
    sector_rank: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]  # 记录数据来源
```

## 数据来源说明

### 新浪财经 (Sina)
- **优势**: 实时行情，更新快
- **用途**: `get_quote()` 主数据源
- **限制**: 不提供历史数据、股票信息

### 东方财富 (Eastmoney)
- **优势**: 股票信息详细，板块排行准确
- **用途**: `get_stock_info()`, `get_sector_rank()` 主数据源
- **限制**: 不提供单只股票实时行情、历史 K 线

### AKShare
- **优势**: 数据全面，功能丰富
- **用途**: `get_historical_data()`, `get_fund_flow()`, `search_stock()` 唯一数据源；其他方法备选
- **限制**: 速度相对较慢

## 错误处理

所有方法在失败时返回 `None`（除了 `get_quotes_batch()` 返回空列表），不会抛出异常。

```python
quote = service.get_quote("INVALID")
if quote is None:
    print("获取失败")
```

## 性能优化建议

1. **批量查询**: 使用 `get_quotes_batch()` 而不是循环调用 `get_quote()`
2. **综合数据**: 使用 `get_comprehensive_data()` 一次性获取多种数据
3. **外部缓存**: 可在应用层添加缓存，如：
   - 行情数据：缓存 30-60 秒
   - 股票信息：缓存 5-10 分钟
   - 历史数据：缓存 1 小时
