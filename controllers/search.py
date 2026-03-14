#!/usr/bin/env python3
"""
search 命令 - 搜索股票
"""

import json
from repositories.stock_list_repo import StockListRepository


def cmd_search(args):
    """search 命令处理 - 搜索股票"""
    if not args.keyword:
        print("Usage: python main.py search <keyword>")
        print("Example: python main.py search 平安")
        return

    # 从股票列表缓存中搜索
    from repositories.database import get_db
    db = get_db()
    db.init_db()
    session = db.get_session()

    try:
        repo = StockListRepository(session)
        results = repo.search(args.keyword)

        if not results:
            if getattr(args, 'json', False):
                print(json.dumps({"results": [], "total": 0, "keyword": args.keyword}, ensure_ascii=False, indent=2))
            else:
                print("未找到匹配的股票")
            return

        # JSON 输出
        if getattr(args, 'json', False):
            output = {
                "keyword": args.keyword,
                "total": len(results),
                "results": []
            }
            for r in results:
                output["results"].append({
                    "code": r.code,
                    "name": r.name,
                    "price": float(r.latest_price or 0),
                    "change_pct": float(r.change_pct or 0)
                })
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # 文本输出
            print(f"找到 {len(results)} 只匹配股票:\n")
            print(f"{'代码':<10} {'名称':<15} {'最新价':>10} {'涨跌幅':>10}")
            print("-" * 50)

            for r in results:
                print(f"{r.code:<10} {r.name:<15} {float(r.latest_price or 0):>10.2f} {float(r.change_pct or 0):>10.2f}%")
    finally:
        session.close()
