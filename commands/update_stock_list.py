#!/usr/bin/env python3
"""
update-stock-list 命令 - 更新 A 股股票列表缓存
"""
from infrastructure.unified_service import UnifiedStockQueryService
from domain.portfolio.repositories.database import get_db


def cmd_update_stock_list(args):
    """update-stock-list 命令处理"""
    db = get_db()
    db.init_db()

    service = UnifiedStockQueryService(db=db)

    if args.full:
        # 全量更新：获取所有股票并更新缓存
        print("执行全量更新股票列表...\n")
        count = service.akshare.refresh_stock_list(incremental=False)
        print(f"\n全量更新完成，共 {count} 只股票")

    elif args.incremental:
        # 增量更新：只更新已有股票的价格信息
        print("执行增量更新股票列表...\n")
        count = service.akshare.refresh_stock_list(incremental=True)
        print(f"\n增量更新完成，共更新 {count} 只股票")

    else:
        # 默认：检查缓存状态，如果没有数据则全量更新，否则增量更新
        from domain.portfolio.repositories.stock_list_repo import StockListRepository
        repo = StockListRepository(db.get_session())
        stock_count = repo.get_count()

        if stock_count == 0:
            print(f"当前缓存为空 ({stock_count} 只股票)，执行全量更新...\n")
            count = service.akshare.refresh_stock_list(incremental=False)
            print(f"\n全量更新完成，共 {count} 只股票")
        else:
            print(f"当前缓存有 {stock_count} 只股票，执行增量更新...\n")
            count = service.akshare.refresh_stock_list(incremental=True)
            print(f"\n增量更新完成，共更新 {count} 只股票")

        db.close()