#!/usr/bin/env python3
"""
update-kline 命令 - K 线数据定时更新
基于 APScheduler 实现定时调度
只在交易日执行更新
"""

import argparse
import logging
import signal
import sys
from datetime import datetime

from repositories.database import Database
from services.kline_scheduler import KlineScheduler


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 全局调度器引用，用于信号处理
_scheduler: KlineScheduler = None


def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    logger.info("收到停止信号，正在关闭调度器...")
    if _scheduler:
        _scheduler.stop()
    sys.exit(0)


def run_once(args):
    """
    执行一次 K 线更新（不启动调度器）

    Args:
        args: 命令行参数
    """
    logger.info("执行一次性 K 线更新...")

    db = Database()
    db.init_db()

    try:
        scheduler = KlineScheduler(db)

        # 如果指定了股票代码，只更新该股票
        if hasattr(args, 'stock_code') and args.stock_code:
            session = db.get_session()
            try:
                from repositories.kline_repo import KlineRepository
                kline_repo = KlineRepository(session)
                scheduler.update_single_symbol(
                    args.stock_code,
                    datetime.now().strftime('%Y%m%d'),
                    kline_repo
                )
                logger.info(f"更新完成：{args.stock_code}")
            finally:
                session.close()
        else:
            # 更新所有持仓和收藏股
            scheduler.run_daily_update()
            logger.info("K 线更新完成")

    finally:
        db.close()


def run_continuous(args):
    """
    持续运行调度器

    Args:
        args: 命令行参数
    """
    global _scheduler

    logger.info("启动 K 线定时任务调度器，每日 01:00 执行（自动跳过非交易日）...")

    db = Database()
    db.init_db()

    try:
        _scheduler = KlineScheduler(db)

        # 注册信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("调度器运行中，按 Ctrl+C 停止...")

        # 启动调度器（阻塞）
        _scheduler.start()

    finally:
        db.close()


def cmd_update_kline(args):
    """
    update-kline 命令入口

    Args:
        args: 命令行参数
    """
    if getattr(args, 'once', False):
        # 一次性执行
        run_once(args)
    else:
        # 持续运行调度器
        run_continuous(args)


def setup_parser(parser: argparse.ArgumentParser):
    """
    设置命令行参数

    Args:
        parser: 参数解析器
    """
    parser.add_argument(
        '--once',
        action='store_true',
        help='只执行一次更新（默认：持续运行调度器）'
    )
    parser.add_argument(
        '--stock-code',
        type=str,
        help='只更新指定股票（仅在 --once 模式下有效）'
    )
    parser.add_argument(
        '--log',
        type=str,
        help='日志文件路径'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='输出详细日志'
    )


def main():
    """独立运行入口"""
    parser = argparse.ArgumentParser(
        description='K 线数据定时更新',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动调度器（持续运行，每日 01:00 执行）
  python main.py update-kline

  # 执行一次更新
  python main.py update-kline --once

  # 更新指定股票
  python main.py update-kline --once --stock-code 600519
        """
    )
    setup_parser(parser)
    args = parser.parse_args()

    # 配置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 可选日志文件
    if args.log:
        file_handler = logging.FileHandler(args.log, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)

    cmd_update_kline(args)


if __name__ == "__main__":
    main()
