"""
AKShare 数据源
提供历史数据、实时行情、资金流向、股票搜索等功能
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import akshare as ak

from infrastructure.sources.base import BaseDataSource


class AKShareDataSource(BaseDataSource):
    """AKShare 数据源 - 带数据库缓存"""

    name = "akshare"

    def __init__(self, db=None, timeout: int = 30):
        """
        初始化 AKShare 数据源

        Args:
            db: Database 实例（用于缓存）
            timeout: 请求超时时间 (秒)
        """
        self.db = db
        self.timeout = timeout
        self._kline_repo = None

    @property
    def kline_repo(self):
        """延迟初始化 KlineRepository"""
        if self._kline_repo is None and self.db:
            from mystocks.storage.repositories.kline_repo import KlineRepository
            self._kline_repo = KlineRepository(self.db.get_session())
        return self._kline_repo

    def get_historical_data(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据（优先从数据库读取，没有时调用 AKShare 并保存）

        Args:
            symbol: 股票代码 (如 "601857")
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly)
            adjust: 复权类型 (qfq/hfq/none)

        Returns:
            pandas DataFrame with OHLCV data
        """
        # 默认获取最近 250 天的数据
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=250)).strftime('%Y%m%d')

        # 优先从数据库读取
        if self.kline_repo:
            try:
                df = self.kline_repo.get_klines_df(symbol, start_date, end_date, period, adjust)
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                print(f"数据库读取失败，切换到 AKShare API: {e}")

        # 数据库没有数据，调用 AKShare API
        df = self._fetch_from_akshare(symbol, start_date, end_date, period, adjust)

        # 同步保存到数据库
        if df is not None and not df.empty and self.kline_repo:
            try:
                self._save_to_database(symbol, df, period, adjust)
            except Exception as e:
                print(f"数据库保存失败：{e}")

        return df

    def _fetch_from_akshare(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str,
        adjust: str
    ) -> Optional[pd.DataFrame]:
        """从 AKShare 获取数据"""
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )

            if df.empty:
                return None

            # 重命名列以匹配技术指标要求
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })

            # 删除不需要的列
            if '股票代码' in df.columns:
                df = df.drop(columns=['股票代码'])

            # 确保日期列为 datetime 类型
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # 确保数值列为 float 类型
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except Exception as e:
            print(f"AKShare 历史数据获取失败：{e}")
            return None

    def _save_to_database(
        self,
        symbol: str,
        df: pd.DataFrame,
        period: str,
        adjust: str
    ):
        """
        将数据保存到数据库

        Args:
            symbol: 股票代码
            df: DataFrame 数据
            period: 周期
            adjust: 复权类型
        """
        df_reset = df.reset_index()
        klines_data = []
        for _, row in df_reset.iterrows():
            date_str = row['date']
            if isinstance(date_str, pd.Timestamp):
                date_str = date_str.strftime('%Y%m%d')
            elif isinstance(date_str, datetime):
                date_str = date_str.strftime('%Y%m%d')

            klines_data.append({
                'date': date_str,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
                'amount': float(row.get('amount', 0)),
                'amplitude': float(row.get('amplitude', 0)),
                'pct_change': float(row.get('pct_change', 0)),
                'change': float(row.get('change', 0)),
                'turnover': float(row.get('turnover', 0))
            })

        self.kline_repo.upsert_klines(symbol, klines_data, period, adjust)

    def get_historical_data_raw(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据（原始方法，直接从 AKShare 获取，不使用缓存）
        用于初始化服务和定时任务

        Args:
            symbol: 股票代码 (如 "601857")
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly)
            adjust: 复权类型 (qfq/hfq/none)

        Returns:
            pandas DataFrame with OHLCV data
        """
        # 默认获取最近 250 天的数据
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=250)).strftime('%Y%m%d')

        return self._fetch_from_akshare(symbol, start_date, end_date, period, adjust)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            实时行情字典
        """
        try:
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol]

            if stock_data.empty:
                return None

            row = stock_data.iloc[0]
            return {
                'source': self.name,
                'code': row['代码'],
                'name': row['名称'],
                'price': float(row['最新价']),
                'change': float(row['涨跌额']),
                'change_percent': float(row['涨跌幅']),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'volume': int(row['成交量']),
                'amount': float(row['成交额']),
                'market': 'A 股'
            }

        except Exception as e:
            print(f"AKShare 实时行情获取失败：{e}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典
        """
        try:
            df = ak.stock_individual_info_em(symbol=symbol)

            if df.empty:
                return None

            # 转换为字典
            info_dict = {}
            for _, row in df.iterrows():
                key = row.get('item', '')
                value = row.get('value', '')
                info_dict[key] = value

            return {
                'source': self.name,
                'symbol': symbol,
                'name': info_dict.get('股票简称', ''),
                'code': symbol,
                'market': info_dict.get('市场', ''),
                'industry': info_dict.get('行业', ''),
                'pe_ratio': info_dict.get('市盈率 - 动态', 0),
                'pb_ratio': info_dict.get('市净率', 0),
                'market_cap': info_dict.get('总市值', 0),
                'float_cap': info_dict.get('流通市值', 0)
            }

        except Exception as e:
            print(f"AKShare 股票信息获取失败：{e}")
            return None

    def get_fund_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取个股资金流向分析

        Args:
            symbol: 股票代码

        Returns:
            资金流向数据
        """
        try:
            # 自动判断市场
            market = 'sh' if symbol.startswith(('6', '9')) else 'sz'

            df = ak.stock_individual_fund_flow(stock=symbol, market=market)

            if df.empty:
                return None

            result = {
                'source': self.name,
                'code': symbol,
                'market': market,
                'data': df.to_dict(orient='records')
            }

            # 提取主力流入数据
            if len(df) > 0:
                latest = df.iloc[0]
                result['summary'] = {
                    'date': latest.get('日期', 'N/A'),
                    'main_force_in': float(latest.get('主力净流入 - 净额', 0)),
                    'big_order_in': float(latest.get('大单净流入 - 净额', 0)),
                    'medium_order_in': float(latest.get('中单净流入 - 净额', 0)),
                    'small_order_in': float(latest.get('小单净流入 - 净额', 0))
                }

            return result

        except Exception as e:
            print(f"AKShare 资金流向获取失败：{e}")
            return None

    def search_stock(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """
        搜索股票（支持代码或名称模糊匹配）- 优先使用本地缓存

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的股票列表
        """
        # 优先从数据库缓存搜索
        if self.db:
            try:
                from mystocks.storage.repositories.stock_list_repo import StockListRepository
                stock_list_repo = StockListRepository(self.db.get_session())
                results = stock_list_repo.search(keyword, limit=20)

                if results:
                    return [
                        {
                            '代码': stock.code,
                            '名称': stock.name,
                            '最新价': stock.latest_price or 0,
                            '涨跌幅': stock.change_pct or 0,
                        }
                        for stock in results
                    ]
            except Exception as e:
                print(f"数据库搜索失败，切换到 AKShare API: {e}")

        # 数据库搜索失败或无数据，调用 AKShare API
        return self._search_from_akshare(keyword)

    def _search_from_akshare(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """从 AKShare 搜索股票（备用方案）"""
        try:
            df = ak.stock_zh_a_spot_em()

            # 模糊匹配代码或名称
            mask = df['代码'].str.contains(keyword, na=False) | \
                   df['名称'].str.contains(keyword, na=False)
            result = df[mask]

            return result.head(20).to_dict(orient='records')

        except Exception as e:
            print(f"AKShare 股票搜索失败：{e}")
            return None

    def refresh_stock_list(self, incremental: bool = False) -> int:
        """
        刷新股票列表缓存

        Args:
            incremental: 是否增量更新（只更新已有股票的价格）

        Returns:
            更新的股票数量
        """
        from mystocks.storage.repositories.stock_list_repo import StockListRepository

        if not self.db:
            print("错误：数据库实例未初始化")
            return 0

        stock_list_repo = StockListRepository(self.db.get_session())

        try:
            print("正在从 AKShare 获取 A 股列表...")
            df = ak.stock_zh_a_spot_em()
            print(f"获取到 {len(df)} 只股票数据")

            count = 0
            for _, row in df.iterrows():
                code = row['代码']

                # 增量更新模式：只更新已存在的股票
                if incremental:
                    existing = stock_list_repo.get(code)
                    if not existing:
                        continue

                data = {
                    'code': code,
                    'name': row['名称'],
                    'latest_price': float(row['最新价']) if row['最新价'] else None,
                    'change_pct': float(row['涨跌幅']) if row['涨跌幅'] else None,
                    'volume': float(row['成交量']) if row['成交量'] else None,
                    'amount': float(row['成交额']) if row['成交额'] else None,
                    'market_cap': float(row['总市值']) if row['总市值'] else None,
                    'pe_ratio': float(row['市盈率 - 动态']) if row.get('市盈率 - 动态') else None,
                }

                stock_list_repo.upsert(data)
                count += 1

                # 每 100 只打印进度
                if count % 100 == 0:
                    print(f"  已处理 {count} 只股票...")

            stock_list_repo.session.commit()
            print(f"✅ 刷新完成，共更新 {count} 只股票")
            return count

        except Exception as e:
            print(f"AKShare 股票列表刷新失败：{e}")
            return 0

    def get_sector_rank(self, sector_type: int = 1, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取板块排行

        Args:
            sector_type: 1=行业板块，2=概念板块
            limit: 返回数量

        Returns:
            板块排行数据
        """
        try:
            if sector_type == 1:
                df = ak.stock_board_industry_name_em()
            elif sector_type == 2:
                df = ak.stock_board_concept_name_em()
            else:
                return None

            return {
                'source': self.name,
                'type': sector_type,
                'sectors': df.head(limit).to_dict(orient='records')
            }

        except Exception as e:
            print(f"AKShare 板块排行获取失败：{e}")
            return None

    def get_realtime_quotes(self, symbols: List[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        批量获取实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            行情数据列表
        """
        try:
            df = ak.stock_zh_a_spot_em()
            if symbols:
                df = df[df['代码'].isin(symbols)]
            return df.to_dict(orient='records')

        except Exception as e:
            print(f"AKShare 批量行情获取失败：{e}")
            return None
