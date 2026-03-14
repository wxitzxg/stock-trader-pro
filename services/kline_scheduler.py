"""
KlineScheduler - K 线定时任务调度器
基于 APScheduler，支持交易日判断和节假日跳过
"""
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from repositories.database import Database
from services.kline_init_service import KlineInitService
from repositories.kline_repo import KlineRepository
from repositories.sources.akshare_source import AKShareDataSource
from domain.common.trading_time import TradingTimeUtils

logger = logging.getLogger(__name__)


class KlineScheduler:
    """K 线定时任务调度器"""

    def __init__(self, db: Database = None):
        """
        初始化 K 线调度器

        Args:
            db: Database 实例
        """
        self.db = db or Database()
        self.scheduler = BlockingScheduler()
        self.akshare_source = AKShareDataSource()
        self._update_count = 0
        self._last_update_time = None

    def start(self):
        """启动调度器"""
        # 每天凌晨 1 点执行（避开周末和节假日，在 job 内部判断）
        self.scheduler.add_job(
            self.run_daily_update,
            CronTrigger(hour=1, minute=0),
            id='daily_kline_update',
            name='每日 K 线数据更新',
            misfire_grace_time=3600  # 1 小时的容错时间
        )

        logger.info("K 线定时任务调度器已启动，每日 01:00 执行（自动跳过非交易日）")
        self.scheduler.start()

    def run_daily_update(self):
        """
        每日凌晨 1 点执行
        获取所有持仓股和收藏股的最近交易日 K 线数据并更新
        """
        logger.info("开始执行每日 K 线数据更新任务...")

        try:
            # 判断是否是交易日
            from domain.common.trading_time import TradingTimeUtils
            if not TradingTimeUtils.is_trading_day():
                logger.info("今天不是 A 股交易日，跳过 K 线更新")
                return

            # 获取昨天的日期（如果是周一则获取上周五）
            today = datetime.now()
            days_back = 3 if today.weekday() == 1 else 1  # 周一回溯 3 天，其他回溯 1 天
            target_date = today - timedelta(days=days_back)
            target_date_str = target_date.strftime('%Y%m%d')

            session = self.db.get_session()
            try:
                kline_repo = KlineRepository(session)

                # 获取所有持仓股代码
                from repositories.position_repo import PositionRepository
                position_repo = PositionRepository(session)
                positions = position_repo.get_all(include_empty=False)
                position_codes = [p.stock_code for p in positions]

                # 获取所有收藏股代码
                from repositories.watchlist_repo import WatchlistRepository
                watchlist_repo = WatchlistRepository(session)
                watchlists = watchlist_repo.get_all()
                watchlist_codes = [w.stock_code for w in watchlists]

                # 合并去重
                all_codes = set(position_codes + watchlist_codes)

                if not all_codes:
                    logger.info("没有持仓股和收藏股，跳过更新")
                    return

                logger.info(f"需要更新 {len(all_codes)} 只股票的 K 线数据（日期：{target_date_str}）")

                # 更新每只股票的 K 线
                updated_count = 0
                error_count = 0

                for code in all_codes:
                    try:
                        self._update_single_symbol(code, target_date_str, kline_repo)
                        updated_count += 1
                    except Exception as e:
                        logger.error(f"更新 {code} 的 K 线失败：{e}")
                        error_count += 1

                logger.info(
                    f"每日 K 线更新完成：成功 {updated_count} 只，"
                    f"失败 {error_count} 只"
                )

                # 更新统计信息
                self._last_update_time = datetime.now()
                self._update_count += 1

            finally:
                session.close()

        except Exception as e:
            logger.error(f"每日 K 线更新任务执行失败：{e}")

    def update_single_symbol(
        self,
        symbol: str,
        date: str,
        kline_repo: KlineRepository
    ):
        """
        更新单只股票的 K 线数据

        Args:
            symbol: 股票代码
            date: 日期 YYYYMMDD
            kline_repo: KlineRepository 实例
        """
        # 检查是否已存在
        existing = kline_repo.get_klines(symbol, date, date, 'daily', 'qfq')
        if existing:
            logger.debug(f"{symbol} {date} 数据已存在，跳过")
            return

        # 从 AKShare 获取数据
        df = self.akshare_source.get_historical_data_raw(
            symbol=symbol,
            start_date=date,
            end_date=date,
            period='daily',
            adjust='qfq'
        )

        if df is None or df.empty:
            logger.warning(f"{symbol} {date} AKShare 返回空数据")
            return

        # 转换为 dict 列表
        df_reset = df.reset_index()
        klines_data = []
        for _, row in df_reset.iterrows():
            klines_data.append({
                'date': row['date'] if isinstance(row['date'], str) else str(row['date']),
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
        kline_repo.upsert_klines(symbol, klines_data, 'daily', 'qfq')
        logger.info(f"{symbol} {date} K 线数据已更新")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("K 线定时任务调度器已停止")

    @property
    def stats(self) -> dict:
        """
        获取调度统计信息

        Returns:
            {
                "update_count": int,       # 更新次数
                "last_update_time": str,   # 上次更新时间
                "is_running": bool         # 是否正在运行
            }
        """
        return {
            "update_count": self._update_count,
            "last_update_time": (
                self._last_update_time.isoformat()
                if self._last_update_time else None
            ),
            "is_running": self.scheduler.running
        }


def run_scheduler():
    """运行调度器（阻塞式）"""
    scheduler = KlineScheduler()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    run_scheduler()
