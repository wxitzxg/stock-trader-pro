#!/usr/bin/env python3
"""
每日 K 线数据更新脚本

用法:
    python scripts/daily_kline_update.py  # 手动执行一次更新
    python scripts/daily_kline_update.py --start  # 启动定时任务（阻塞式）
"""
import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mystocks.storage.database import Database
from mystocks.services.kline_scheduler import KlineScheduler


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='每日 K 线数据更新脚本')
    parser.add_argument('--start', action='store_true',
                        help='启动定时任务（阻塞式，持续运行）')
    parser.add_argument('--once', action='store_true',
                        help='手动执行一次更新（默认）')

    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # 初始化数据库
    logger.info("初始化数据库连接...")
    db = Database()
    db.init_db()

    try:
        if args.start:
            # 启动定时任务
            logger.info("启动 K 线定时任务调度器，每日 00:00 执行...")
            scheduler = KlineScheduler(db)
            scheduler.start()
        else:
            # 手动执行一次
            logger.info("手动执行每日 K 线数据更新...")
            scheduler = KlineScheduler(db)
            scheduler.run_daily_update()
            logger.info("更新完成")

    except KeyboardInterrupt:
        logger.info("收到中断信号，停止调度器...")
    except Exception as e:
        logger.error(f"执行失败：{e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
