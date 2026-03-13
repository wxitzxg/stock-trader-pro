#!/usr/bin/env python3
"""
watchlist 命令 - 收藏管理
使用新的 MyStocks 综合模块
"""

from mystocks import MyStocks


def cmd_watchlist(args):
    """watchlist 命令处理"""
    with MyStocks() as ms:
        if args.add:
            # 添加收藏
            wl = ms.add_to_watchlist(
                stock_code=args.add,
                stock_name=args.name,
                tags=args.tags,
                notes=args.notes,
                target_price=args.target,
                stop_loss=args.stop_loss
            )
            print(f"✅ 添加收藏股：{args.add} {args.name or ''}")

        elif args.remove:
            # 删除收藏
            if ms.remove_from_watchlist(args.remove):
                print(f"✅ 已删除：{args.remove}")
            else:
                print(f"❌ 未找到：{args.remove}")

        elif args.list or True:  # 默认显示列表
            stocks = ms.get_watchlist()

            if not stocks:
                print("收藏股列表为空")
                return

            print("\n═══════════════════════════════════════════════════════")
            print("  收藏股列表")
            print("═══════════════════════════════════════════════════════\n")

            for wl in stocks:
                print(f"📌 {wl.stock_code} ({wl.stock_name})")
                if wl.tags:
                    print(f"   标签：{wl.tags}")
                if wl.target_price:
                    print(f"   目标价：¥{wl.target_price:.2f}")
                if wl.stop_loss:
                    print(f"   止损价：¥{wl.stop_loss:.2f}")
                print()

            print(f"共 {len(stocks)} 只股票")
            print("═══════════════════════════════════════════════════════\n")
