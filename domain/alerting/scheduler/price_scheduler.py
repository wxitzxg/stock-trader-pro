"""
基于 APScheduler 的价格更新调度器
"""

import logging
from datetime import datetime
from typing import Optional, Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from domain.common.trading_time import TradingTimeUtils


logger = logging.getLogger(__name__)


class PriceUpdateScheduler:
    """
    基于 APScheduler 的价格更新调度器

    特性:
    - 只在交易时间执行价格更新
    - 支持自定义检查间隔和更新频率
    - 优雅停止机制
    """

    def __init__(
        self,
        update_func: Callable,
        check_interval: int = 60,
        update_interval: int = 300
    ):
        """
        初始化调度器

        Args:
            update_func: 价格更新函数
            check_interval: 检查间隔（秒），默认 60 秒检查一次
            update_interval: 更新频率（秒），默认 300 秒（交易时间内每 5 分钟更新一次）
        """
        self._update_func = update_func
        self._check_interval = check_interval
        self._update_interval = update_interval
        self._running = False
        self._last_update_time: Optional[datetime] = None
        self._update_count = 0
        self._skip_count = 0

        # 创建 APScheduler 实例
        self.scheduler = BlockingScheduler()

    def _job(self) -> None:
        """
        定时任务执行函数
        先判断是否交易时间，是则执行更新
        """
        # 使用统一工具类判断交易时间
        result = TradingTimeUtils.is_trading_time()

        if not result["is_trading"]:
            # 非交易时间，跳过更新
            reason = result["reason"]
            logger.info(f"跳过价格更新：{reason}")
            self._skip_count += 1
            return

        # 交易时间，执行价格更新
        logger.info(f"开始更新持仓价格（交易时间：{result['market_phase']}）")
        try:
            self._update_func()
            self._last_update_time = datetime.now()
            self._update_count += 1
            logger.info(f"价格更新完成，累计更新 {self._update_count} 次")
        except Exception as e:
            logger.error(f"价格更新失败：{e}", exc_info=True)

    def start(self) -> None:
        """
        启动调度器
        阻塞运行，直到调用 stop()
        """
        logger.info(
            f"价格更新调度器启动 - "
            f"检查间隔：{self._check_interval}秒，"
            f"更新频率：{self._update_interval}秒"
        )
        self._running = True

        # 添加定时任务到 APScheduler
        self.scheduler.add_job(
            self._job,
            trigger=IntervalTrigger(seconds=self._check_interval),
            id='price_update',
            name='价格更新',
            max_instances=1  # 防止并发执行
        )

        self.scheduler.start()

        logger.info("价格更新调度器已停止")

    def stop(self) -> None:
        """停止调度器"""
        logger.info("正在停止价格更新调度器...")
        self._running = False
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

    @property
    def stats(self) -> dict:
        """
        获取调度统计

        Returns:
            {
                "update_count": int,      # 更新次数
                "skip_count": int,        # 跳过次数
                "last_update_time": str,  # 上次更新时间
            }
        """
        return {
            "update_count": self._update_count,
            "skip_count": self._skip_count,
            "last_update_time": (
                self._last_update_time.isoformat()
                if self._last_update_time else None
            )
        }

    def reset_stats(self) -> None:
        """重置统计"""
        self._update_count = 0
        self._skip_count = 0
        self._last_update_time = None


def create_scheduler(
    update_func: Callable,
    interval: int = 300,
    check_interval: int = 60
) -> PriceUpdateScheduler:
    """
    创建价格更新调度器的工厂函数

    Args:
        update_func: 价格更新函数
        interval: 更新频率（秒）
        check_interval: 检查间隔（秒）

    Returns:
        PriceUpdateScheduler 实例
    """
    return PriceUpdateScheduler(
        update_func=update_func,
        check_interval=check_interval,
        update_interval=interval
    )
