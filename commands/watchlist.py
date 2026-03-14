#!/usr/bin/env python3
"""
watchlist 命令 - 收藏管理
使用新的 MyStocks 综合模块
"""

import json
from domain.portfolio.services import MyStocks


def format_watchlist_json(stocks: list) -> str:
    """格式化收藏列表为 JSON"""
    output = {
        "watchlist": [],
        "total": len(stocks)
    }

    for wl in stocks:
        output["watchlist"].append({
            "stock_code": wl.stock_code,
            "stock_name": wl.stock_name,
            "tags": wl.tags,
            "target_price": wl.target_price,
            "stop_loss": wl.stop_loss,
            "notes": wl.notes
        })

    return json.dumps(output, ensure_ascii=False, indent=2)


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
            if getattr(args, 'json', False):
                print(json.dumps({
                    "success": True,
                    "stock_code": wl.stock_code,
                    "stock_name": wl.stock_name
                }, ensure_ascii=False, indent=2))
            else:
                print(f"✅ 添加收藏股：{args.add} {args.name or ''}")

        elif args.remove:
            # 删除收藏
            success = ms.remove_from_watchlist(args.remove)
            if getattr(args, 'json', False):
                print(json.dumps({
                    "success": success,
                    "stock_code": args.remove
                }, ensure_ascii=False, indent=2))
            else:
                if success:
                    print(f"✅ 已删除：{args.remove}")
                else:
                    print(f"❌ 未找到：{args.remove}")

        elif args.list or True:  # 默认显示列表
            stocks = ms.get_watchlist()

            if not stocks:
                if getattr(args, 'json', False):
                    print(json.dumps({"watchlist": [], "total": 0}, ensure_ascii=False, indent=2))
                else:
                    print("收藏股列表为空")
                return

            # JSON 输出
            if getattr(args, 'json', False):
                print(format_watchlist_json(stocks))
                return

            # 文本输出
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
