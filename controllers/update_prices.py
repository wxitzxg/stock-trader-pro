#!/usr/bin/env python3
"""
update-prices 命令 - 持仓价格定时更新
基于 schedule 库实现定时调度
只在交易时间执行更新
"""

import argparse
import logging
import signal
import sys

from services.my_stocks import MyStocks
from services.price_update_service import PriceUpdateService
from domain.alerting.scheduler.price_scheduler import PriceUpdateScheduler, create_scheduler
from config.settings import MONITOR_CONFIG
from domain.common.trading_time import TradingTimeUtils


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 全局调度器引用，用于信号处理
_scheduler: PriceUpdateScheduler = None


def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    logger.info("收到停止信号，正在关闭调度器...")
    if _scheduler:
        _scheduler.stop()
    sys.exit(0)


def create_update_func(session):
    """
    创建价格更新函数

    Args:
        session: SQLAlchemy session

    Returns:
        价格更新函数
    """
    service = PriceUpdateService(session)

    def update_prices():
        """执行价格更新"""
        result = service.update_all_positions_prices()

        if result.get("skipped"):
            logger.info(f"跳过更新：{result.get('reason')}")
            return

        logger.info(
            f"价格更新完成 - "
            f"成功：{result.get('updated_count')}, "
            f"失败：{result.get('failed_count')}, "
            f"总计：{result.get('total_count')}"
        )

        # 输出详细信息
        for detail in result.get("details", []):
            if detail.get("success"):
                logger.debug(
                    f"  {detail.get('stock_code')}: "
                    f"{detail.get('old_price')} -> {detail.get('new_price')}"
                )
            else:
                logger.warning(
                    f"  {detail.get('stock_code')}: {detail.get('reason')}"
                )

    return update_prices


def run_once(args):
    """
    执行一次价格更新（不启动调度器）

    Args:
        args: 命令行参数
    """
    logger.info("执行一次性价格更新...")

    with MyStocks() as ms:
        service = PriceUpdateService(ms._session)

        # 如果指定了股票代码，只更新该股票
        if hasattr(args, 'stock_code') and args.stock_code:
            result = service.update_single_position_price(args.stock_code)
            logger.info(f"更新结果：{result}")
            return

        # 更新所有持仓
        result = service.update_all_positions_prices()

        if result.get("skipped"):
            logger.info(f"跳过更新：{result.get('reason')}")
            return

        logger.info(
            f"价格更新完成 - "
            f"成功：{result.get('updated_count')}, "
            f"失败：{result.get('failed_count')}, "
            f"总计：{result.get('total_count')}"
        )

        # 显示汇总
        summary = service.get_portfolio_summary_after_update()
        logger.info(
            f"持仓汇总 - "
            f"总市值：{summary.get('total_value'):.2f}, "
            f"总盈亏：{summary.get('total_profit'):.2f}"
        )


def run_continuous(args):
    """
    持续运行调度器

    Args:
        args: 命令行参数
    """
    global _scheduler

    # 从配置或参数获取间隔
    check_interval = MONITOR_CONFIG.get("price_update_check_interval", 60)
    update_interval = getattr(args, 'interval', None) or MONITOR_CONFIG.get(
        "price_update_interval_market", 300
    )

    logger.info(
        f"启动价格更新调度器 - "
        f"检查间隔：{check_interval}秒，"
        f"更新频率：{update_interval}秒"
    )

    with MyStocks() as ms:
        update_func = create_update_func(ms._session)
        _scheduler = create_scheduler(
            update_func=update_func,
            interval=update_interval,
            check_interval=check_interval
        )

        # 注册信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("调度器运行中，按 Ctrl+C 停止...")

        # 显示下次开盘时间
        next_open = TradingTimeUtils.get_next_market_open()
        logger.info(f"下次开盘时间：{next_open}")

        # 启动调度器（阻塞）
        _scheduler.start()


def cmd_update_prices(args):
    """
    update-prices 命令入口

    Args:
        args: 命令行参数
    """
    # 检查是否启用了价格更新
    if not MONITOR_CONFIG.get("price_update_enabled", True):
        logger.warning("价格更新功能已禁用，请在配置中启用")
        return

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
        '--interval',
        type=int,
        default=None,
        help='更新间隔（秒），默认从配置读取 (300)'
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
        description='持仓价格定时更新',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动调度器（持续运行，只在交易时间更新）
  python -m mystocks update-prices

  # 执行一次更新
  python -m mystocks update-prices --once

  # 更新指定股票
  python -m mystocks update-prices --once --stock-code 300003

  # 指定更新间隔（60 秒检查，300 秒更新）
  python -m mystocks update-prices --interval 300
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

    cmd_update_prices(args)


if __name__ == "__main__":
    main()
