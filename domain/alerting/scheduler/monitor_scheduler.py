#!/usr/bin/env python3
"""
监控预警调度器
基于 APScheduler，在交易时间内定期执行监控预警
"""

import logging
from datetime import datetime
from typing import Optional, Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from common.trading_time import TradingTimeUtils
from domain.alerting.scheduler.smart_schedule import SmartScheduler

logger = logging.getLogger(__name__)


class MonitorScheduler:
    """
    监控预警调度器

    特性:
    - 只在交易时间执行监控
    - 支持自定义检查间隔
    - 支持报告输出到文件
    - 优雅停止机制
    """

    def __init__(
        self,
        monitor_func: Callable,
        output_dir: Optional[str] = None,
        check_interval: int = 60
    ):
        """
        初始化调度器

        Args:
            monitor_func: 监控函数（cmd_monitor）
            output_dir: 报告输出目录，None 表示输出到控制台
            check_interval: 检查间隔（秒），默认 60 秒
        """
        self._monitor_func = monitor_func
        self._output_dir = output_dir
        self._check_interval = check_interval
        self._running = False
        self._run_count = 0
        self._last_run_time: Optional[datetime] = None
        self._skip_count = 0

        # 创建 APScheduler 实例
        self.scheduler = BlockingScheduler()

    def _run_monitor(self) -> None:
        """
        执行监控任务
        先判断是否交易时间，是则执行监控
        """
        # 使用统一工具类判断交易时间
        result = TradingTimeUtils.is_trading_time()

        if not result["is_trading"]:
            # 非交易时间，跳过监控
            reason = result["reason"]
            logger.info(f"跳过监控：{reason}")
            self._skip_count += 1
            return

        # 交易时间内，执行监控
        self._run_count += 1
        mode = result.get('market_phase', 'market')
        logger.info(f"开始执行监控 #{self._run_count} (市场状态：{mode})")

        try:
            self._monitor_func(self._output_dir)
            self._last_run_time = datetime.now()
            logger.info(f"监控完成，累计执行 {self._run_count} 次")
        except Exception as e:
            logger.error(f"监控执行失败：{e}", exc_info=True)

    def start(self) -> None:
        """
        启动调度器
        阻塞运行，直到调用 stop()
        """
        logger.info(f"启动监控预警调度器 - 检查间隔：{self._check_interval}秒")
        logger.info("监控策略：仅在交易日交易时段执行")
        if self._output_dir:
            logger.info(f"报告输出目录：{self._output_dir}")
        else:
            logger.info("报告输出：控制台")
        logger.info("按 Ctrl+C 停止监控")

        self._running = True

        # 添加定时任务到 APScheduler
        self.scheduler.add_job(
            self._run_monitor,
            trigger=IntervalTrigger(seconds=self._check_interval),
            id='market_monitor',
            name='市场监控',
            max_instances=1  # 防止并发执行
        )

        self.scheduler.start()

        logger.info("监控预警调度器已停止")

    def stop(self) -> None:
        """停止调度器"""
        logger.info("正在停止监控预警调度器...")
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
                "run_count": int,         # 运行次数
                "skip_count": int,        # 跳过次数
                "last_run_time": str,     # 上次运行时间
            }
        """
        return {
            "run_count": self._run_count,
            "skip_count": self._skip_count,
            "last_run_time": (
                self._last_run_time.isoformat()
                if self._last_run_time else None
            )
        }

    def reset_stats(self) -> None:
        """重置统计"""
        self._run_count = 0
        self._skip_count = 0
        self._last_run_time = None


def create_scheduler(
    monitor_func: Callable,
    output_dir: Optional[str] = None,
    interval: int = 300
) -> MonitorScheduler:
    """
    创建监控预警调度器的工厂函数

    Args:
        monitor_func: 监控函数
        output_dir: 报告输出目录
        interval: 检查间隔（秒）

    Returns:
        MonitorScheduler 实例
    """
    return MonitorScheduler(
        monitor_func=monitor_func,
        output_dir=output_dir,
        check_interval=interval
    )
