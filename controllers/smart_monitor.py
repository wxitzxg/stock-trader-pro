#!/usr/bin/env python3
"""
smart-monitor 命令 - 智能监控预警调度
支持一次性执行和持续调度两种模式
"""

import argparse
import logging
import signal
import sys
from pathlib import Path

from controllers.monitor import cmd_monitor
from domain.alerting.scheduler.monitor_scheduler import MonitorScheduler, create_scheduler
from config import MONITOR_CONFIG


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 全局调度器引用，用于信号处理
_scheduler: MonitorScheduler = None


def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    logger.info("收到停止信号，正在关闭调度器...")
    if _scheduler:
        _scheduler.stop()
    sys.exit(0)


def run_monitor_task(output_dir: str = None, json_output: bool = False):
    """
    执行监控任务（一次性执行）

    Args:
        output_dir: 报告输出目录
        json_output: 是否输出 JSON 格式
    """
    logger.info("执行监控预警...")

    from argparse import Namespace

    # 构建 monitor 命令参数
    monitor_args = Namespace()
    monitor_args.output = None
    monitor_args.no_position = False
    monitor_args.no_watchlist = False
    monitor_args.json = json_output

    # 如果指定了输出目录，生成报告文件
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ext = "json" if json_output else "md"
        monitor_args.output = str(output_path / f"monitor_{timestamp}.{ext}")

    # 执行监控
    cmd_monitor(monitor_args)


def run_once(args):
    """
    执行一次监控（不启动调度器）

    Args:
        args: 命令行参数
    """
    output_dir = getattr(args, 'output_dir', None)
    json_output = getattr(args, 'json', False)
    run_monitor_task(output_dir, json_output)


def run_continuous(args):
    """
    持续运行调度器

    Args:
        args: 命令行参数
    """
    global _scheduler

    # 从配置或参数获取间隔
    interval = getattr(args, 'interval', None) or MONITOR_CONFIG.get(
        "interval_market", 300
    )
    output_dir = getattr(args, 'output_dir', None)
    json_output = getattr(args, 'json', False)

    logger.info(f"启动监控预警调度器 - 检查间隔：{interval}秒")
    logger.info("监控策略：仅在交易日交易时段执行")
    if output_dir:
        logger.info(f"报告输出目录：{output_dir}")
    else:
        logger.info("报告输出：控制台")
    if json_output:
        logger.info("输出格式：JSON")
    else:
        logger.info("输出格式：Markdown")
    logger.info("按 Ctrl+C 停止监控")

    # 创建调度器
    _scheduler = create_scheduler(
        monitor_func=run_monitor_task,
        output_dir=output_dir,
        interval=interval,
        json_output=json_output
    )

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动调度器（阻塞）
    _scheduler.start()


def cmd_smart_monitor(args):
    """
    smart-monitor 命令入口

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
        help='只执行一次监控（默认：持续运行调度器）'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=None,
        help='监控间隔（秒），默认从配置读取 (300)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='报告输出目录'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON 格式输出'
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
        description='智能监控预警调度',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动调度器（持续运行，交易时间执行）
  python main.py smart-monitor

  # 执行一次监控
  python main.py smart-monitor --once

  # 指定输出目录
  python main.py smart-monitor --output-dir ./reports

  # 指定监控间隔（180 秒）
  python main.py smart-monitor --interval 180
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

    cmd_smart_monitor(args)


if __name__ == "__main__":
    main()
