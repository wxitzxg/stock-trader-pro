"""
KlineRepository - K 线数据访问对象
"""
from typing import Optional, List
from datetime import datetime
import pandas as pd

from mystocks.models.kline import Kline
from mystocks.storage.repositories.base import BaseRepository


class KlineRepository(BaseRepository):
    """Kline 数据访问对象"""

    def get_klines(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = 'daily',
        adjust: str = 'qfq'
    ) -> List[Kline]:
        """
        查询 K 线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            period: 周期 daily/weekly/monthly
            adjust: 复权 qfq/hfq/none

        Returns:
            Kline 对象列表
        """
        return self.session.query(Kline).filter(
            Kline.stock_code == symbol,
            Kline.date >= start_date,
            Kline.date <= end_date,
            Kline.period == period,
            Kline.adjust == adjust
        ).order_by(Kline.date.asc()).all()

    def get_klines_df(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = 'daily',
        adjust: str = 'qfq'
    ) -> Optional[pd.DataFrame]:
        """
        查询 K 线并返回 DataFrame（兼容现有接口）

        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            period: 周期 daily/weekly/monthly
            adjust: 复权 qfq/hfq/none

        Returns:
            pandas DataFrame with OHLCV data
        """
        klines = self.get_klines(symbol, start_date, end_date, period, adjust)
        if not klines:
            return None

        # 转换为 DataFrame
        data = []
        for k in klines:
            data.append({
                'date': k.date,
                'open': k.open,
                'high': k.high,
                'low': k.low,
                'close': k.close,
                'volume': k.volume,
                'amount': k.amount,
                'amplitude': k.amplitude,
                'pct_change': k.pct_change,
                'change': k.change,
                'turnover': k.turnover
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        return df

    def get_latest_date(
        self,
        symbol: str,
        period: str = 'daily',
        adjust: str = 'qfq'
    ) -> Optional[str]:
        """
        获取某股票最新的 K 线日期

        Args:
            symbol: 股票代码
            period: 周期
            adjust: 复权类型

        Returns:
            最新日期 YYYYMMDD，不存在返回 None
        """
        kline = self.session.query(Kline).filter(
            Kline.stock_code == symbol,
            Kline.period == period,
            Kline.adjust == adjust
        ).order_by(Kline.date.desc()).first()

        return kline.date if kline else None

    def get_missing_dates(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = 'daily',
        adjust: str = 'qfq'
    ) -> List[str]:
        """
        获取缺失的交易日期

        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            period: 周期
            adjust: 复权类型

        Returns:
            缺失的日期列表
        """
        # 获取已存在的日期
        existing = self.session.query(Kline.date).filter(
            Kline.stock_code == symbol,
            Kline.date >= start_date,
            Kline.date <= end_date,
            Kline.period == period,
            Kline.adjust == adjust
        ).all()

        existing_dates = set(d[0] for d in existing)

        # 生成完整日期范围
        from datetime import timedelta
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')

        all_dates = []
        current = start
        while current <= end:
            # 跳过周末（简单处理，不考虑节假日）
            if current.weekday() < 5:
                all_dates.append(current.strftime('%Y%m%d'))
            current += timedelta(days=1)

        # 返回缺失的日期
        missing = [d for d in all_dates if d not in existing_dates]
        return missing

    def upsert_klines(
        self,
        symbol: str,
        klines_data: List[dict],
        period: str = 'daily',
        adjust: str = 'qfq'
    ):
        """
        批量插入或更新 K 线数据

        Args:
            symbol: 股票代码
            klines_data: K 线数据列表，每项包含 date, open, high, low, close, volume 等字段
            period: 周期
            adjust: 复权类型
        """
        for data in klines_data:
            kline = Kline(
                stock_code=symbol,
                date=data['date'],
                period=period,
                adjust=adjust,
                open=float(data['open']),
                high=float(data['high']),
                low=float(data['low']),
                close=float(data['close']),
                volume=float(data['volume']),
                amount=float(data.get('amount', 0)),
                amplitude=float(data.get('amplitude', 0)),
                pct_change=float(data.get('pct_change', 0)),
                change=float(data.get('change', 0)),
                turnover=float(data.get('turnover', 0)),
                source='akshare'
            )

            # 使用 ON CONFLICT DO UPDATE (SQLite)
            from sqlalchemy.dialects.sqlite import insert
            stmt = insert(Kline).values(
                stock_code=kline.stock_code,
                date=kline.date,
                period=kline.period,
                adjust=kline.adjust,
                open=kline.open,
                high=kline.high,
                low=kline.low,
                close=kline.close,
                volume=kline.volume,
                amount=kline.amount,
                amplitude=kline.amplitude,
                pct_change=kline.pct_change,
                change=kline.change,
                turnover=kline.turnover,
                source=kline.source
            ).on_conflict_do_update(
                index_elements=['stock_code', 'date', 'period', 'adjust'],
                set_={
                    'open': kline.open,
                    'high': kline.high,
                    'low': kline.low,
                    'close': kline.close,
                    'volume': kline.volume,
                    'amount': kline.amount,
                    'amplitude': kline.amplitude,
                    'pct_change': kline.pct_change,
                    'change': kline.change,
                    'turnover': kline.turnover,
                    'updated_at': datetime.now()
                }
            )
            self.session.execute(stmt)

        self.session.commit()

    def delete_by_symbol(
        self,
        symbol: str,
        period: str = 'daily',
        adjust: str = 'qfq'
    ):
        """
        删除指定股票的所有 K 线数据

        Args:
            symbol: 股票代码
            period: 周期
            adjust: 复权类型
        """
        self.session.query(Kline).filter(
            Kline.stock_code == symbol,
            Kline.period == period,
            Kline.adjust == adjust
        ).delete()
        self.session.commit()
