"""
KlineInitService - K 线数据初始化服务
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from mystocks.storage.repositories.position_repo import PositionRepository
from mystocks.storage.repositories.watchlist_repo import WatchlistRepository
from mystocks.storage.repositories.kline_repo import KlineRepository
from stockquery.sources.akshare_source import AKShareDataSource

logger = logging.getLogger(__name__)


class KlineInitService:
    """K 线数据初始化服务"""

    def __init__(self, db, akshare_source: Optional[AKShareDataSource] = None):
        """
        初始化 K 线初始化服务

        Args:
            db: Database 实例
            akshare_source: AKShare 数据源实例
        """
        self.db = db
        self.position_repo = PositionRepository(db.get_session())
        self.watchlist_repo = WatchlistRepository(db.get_session())
        self.kline_repo = KlineRepository(db.get_session())
        self.akshare_source = akshare_source or AKShareDataSource()

    def init_position_klines(self, days: int = 250, period: str = 'daily', adjust: str = 'qfq'):
        """
        一键初始化所有持仓股的 K 线数据

        Args:
            days: 初始化天数（默认 250 天）
            period: 周期 daily/weekly/monthly
            adjust: 复权 qfq/hfq/none
        """
        positions = self.position_repo.get_all(include_empty=False)
        if not positions:
            logger.info("没有持仓股票，跳过初始化")
            return

        logger.info(f"开始初始化 {len(positions)} 只持仓股的 K 线数据（{days}天）...")

        for position in positions:
            try:
                self._init_single_symbol(position.stock_code, days, period, adjust)
            except Exception as e:
                logger.error(f"初始化持仓股 {position.stock_code} 失败：{e}")

        logger.info("持仓股 K 线初始化完成")

    def init_watchlist_klines(self, days: int = 250, period: str = 'daily', adjust: str = 'qfq'):
        """
        一键初始化所有收藏股的 K 线数据

        Args:
            days: 初始化天数（默认 250 天）
            period: 周期 daily/weekly/monthly
            adjust: 复权 qfq/hfq/none
        """
        watchlists = self.watchlist_repo.get_all()
        if not watchlists:
            logger.info("没有收藏股票，跳过初始化")
            return

        logger.info(f"开始初始化 {len(watchlists)} 只收藏股的 K 线数据（{days}天）...")

        for watchlist in watchlists:
            try:
                self._init_single_symbol(watchlist.stock_code, days, period, adjust)
            except Exception as e:
                logger.error(f"初始化收藏股 {watchlist.stock_code} 失败：{e}")

        logger.info("收藏股 K 线初始化完成")

    def init_symbol_klines(
        self,
        symbol: str,
        days: int = 250,
        period: str = 'daily',
        adjust: str = 'qfq'
    ):
        """
        初始化指定股票的 K 线数据

        Args:
            symbol: 股票代码
            days: 初始化天数（默认 250 天）
            period: 周期 daily/weekly/monthly
            adjust: 复权 qfq/hfq/none
        """
        logger.info(f"开始初始化 {symbol} 的 K 线数据（{days}天）...")
        self._init_single_symbol(symbol, days, period, adjust)
        logger.info(f"{symbol} K 线初始化完成")

    def _init_single_symbol(
        self,
        symbol: str,
        days: int,
        period: str,
        adjust: str
    ):
        """
        初始化单只股票的 K 线数据

        Args:
            symbol: 股票代码
            days: 天数
            period: 周期
            adjust: 复权类型
        """
        session = self.db.get_session()
        try:
            kline_repo = KlineRepository(session)

            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')

            # 获取缺失的日期
            missing_dates = kline_repo.get_missing_dates(
                symbol, start_date_str, end_date_str, period, adjust
            )

            if not missing_dates:
                logger.debug(f"{symbol} 数据已完整，跳过初始化")
                return

            # 如果缺失数据较多，直接全量获取
            if len(missing_dates) > days * 0.5:
                logger.info(f"{symbol} 缺失数据较多（{len(missing_dates)}天），全量获取...")
                self._fetch_and_save(symbol, start_date_str, end_date_str, period, adjust)
            else:
                # 只获取缺失的日期范围
                min_date = min(missing_dates)
                max_date = max(missing_dates)
                logger.info(f"{symbol} 补充缺失数据 {min_date}-{max_date}...")
                self._fetch_and_save(symbol, min_date, max_date, period, adjust)

        finally:
            session.close()

    def _fetch_and_save(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str,
        adjust: str
    ):
        """
        从 AKShare 获取数据并保存到数据库

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期
            adjust: 复权类型
        """
        # 调用 AKShare 获取数据
        df = self.akshare_source.get_historical_data_raw(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust
        )

        if df is None or df.empty:
            logger.warning(f"{symbol} AKShare 返回空数据")
            return

        # 转换为 dict 列表
        df_reset = df.reset_index()
        klines_data = []
        for _, row in df_reset.iterrows():
            klines_data.append({
                'date': str(row['date']) if not isinstance(row['date'], str) else row['date'],
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

        # 保存到数据库
        session = self.db.get_session()
        try:
            kline_repo = KlineRepository(session)
            kline_repo.upsert_klines(symbol, klines_data, period, adjust)
            logger.info(f"{symbol} 成功保存 {len(klines_data)} 条 K 线数据")
        finally:
            session.close()
