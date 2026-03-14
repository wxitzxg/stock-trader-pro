#!/usr/bin/env python3
"""
K 线数据初始化脚本

用法:
    python scripts/init_kline_data.py --position --days 250   # 初始化持仓股
    python scripts/init_kline_data.py --watchlist --days 250  # 初始化收藏股
    python scripts/init_kline_data.py --symbol 601857 --days 250  # 指定股票
    python scripts/init_kline_data.py --all --days 250  # 初始化所有
"""
import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mystocks.storage.database import Database
from mystocks.services.kline_init_service import KlineInitService
from infrastructure.sources.akshare_source import AKShareDataSource


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='K 线数据初始化脚本')
    parser.add_argument('--position', action='store_true', help='初始化持仓股 K 线数据')
    parser.add_argument('--watchlist', action='store_true', help='初始化收藏股 K 线数据')
    parser.add_argument('--symbol', type=str, help='指定股票代码')
    parser.add_argument('--days', type=int, default=250, help='初始化天数（默认 250 天）')
    parser.add_argument('--period', type=str, default='daily',
                        choices=['daily', 'weekly', 'monthly'],
                        help='K 线周期（默认 daily）')
    parser.add_argument('--adjust', type=str, default='qfq',
                        choices=['qfq', 'hfq', 'none'],
                        help='复权类型（默认 qfq）')
    parser.add_argument('--all', action='store_true', dest='init_all',
                        help='初始化所有持仓股和收藏股')

    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # 至少需要一个参数
    if not any([args.position, args.watchlist, args.symbol, args.init_all]):
        parser.print_help()
        print("\n错误：请至少指定一个初始化选项")
        print("  --position: 初始化持仓股")
        print("  --watchlist: 初始化收藏股")
        print("  --symbol: 指定股票")
        print("  --all: 初始化所有持仓股和收藏股")
        sys.exit(1)

    # 初始化数据库和服务
    logger.info("初始化数据库连接...")
    db = Database()
    db.init_db()

    akshare_source = AKShareDataSource(db=db)
    init_service = KlineInitService(db, akshare_source)

    try:
        if args.init_all:
            # 初始化所有持仓股和收藏股
            logger.info(f"开始初始化所有股票 K 线数据（{args.days}天）...")
            init_service.init_position_klines(days=args.days, period=args.period, adjust=args.adjust)
            init_service.init_watchlist_klines(days=args.days, period=args.period, adjust=args.adjust)

        else:
            # 按选项初始化
            if args.position:
                logger.info(f"开始初始化持仓股 K 线数据（{args.days}天）...")
                init_service.init_position_klines(days=args.days, period=args.period, adjust=args.adjust)

            if args.watchlist:
                logger.info(f"开始初始化收藏股 K 线数据（{args.days}天）...")
                init_service.init_watchlist_klines(days=args.days, period=args.period, adjust=args.adjust)

            if args.symbol:
                logger.info(f"开始初始化 {args.symbol} K 线数据（{args.days}天）...")
                init_service.init_symbol_klines(
                    symbol=args.symbol,
                    days=args.days,
                    period=args.period,
                    adjust=args.adjust
                )

        logger.info("K 线数据初始化完成")

    except Exception as e:
        logger.error(f"初始化失败：{e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
