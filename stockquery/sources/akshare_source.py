"""
AKShare 数据源
提供历史数据、实时行情、资金流向、股票搜索等功能
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import akshare as ak

from stockquery.sources.base import BaseDataSource


class AKShareDataSource(BaseDataSource):
    """AKShare 数据源"""

    name = "akshare"

    def __init__(self, timeout: int = 30):
        """
        初始化 AKShare 数据源

        Args:
            timeout: 请求超时时间 (秒)
        """
        self.timeout = timeout

    def get_historical_data(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据

        Args:
            symbol: 股票代码 (如 "601857")
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly)
            adjust: 复权类型 (qfq/hfq/none)

        Returns:
            pandas DataFrame with OHLCV data
        """
        try:
            # 默认获取最近 250 天的数据
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=250)).strftime('%Y%m%d')

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
        搜索股票（支持代码或名称模糊匹配）

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的股票列表
        """
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
