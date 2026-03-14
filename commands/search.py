#!/usr/bin/env python3
"""
search 命令 - 搜索股票
"""

import json
from stockquery import UnifiedStockQueryService


def cmd_search(args):
    """search 命令处理 - 搜索股票"""
    if not args.keyword:
        print("Usage: python main.py search <keyword>")
        print("Example: python main.py search 平安")
        return

    stock_query = UnifiedStockQueryService()
    results = stock_query.search_stock(args.keyword)

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
            if isinstance(r, dict):
                output["results"].append({
                    "code": r.get('代码', 'N/A'),
                    "name": r.get('名称', 'N/A'),
                    "price": float(r.get('最新价', 0) or 0),
                    "change_pct": float(r.get('涨跌幅', 0) or 0)
                })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 文本输出
        print(f"找到 {len(results)} 只匹配股票:\n")
        print(f"{'代码':<10} {'名称':<15} {'最新价':>10} {'涨跌幅':>10}")
        print("-" * 50)

        for r in results:
            if isinstance(r, dict):
                code = r.get('代码', 'N/A')
                name = r.get('名称', 'N/A')
                price = float(r.get('最新价', 0) or 0)
                change_pct = float(r.get('涨跌幅', 0) or 0)
                print(f"{code:<10} {name:<15} {price:>10.2f} {change_pct:>10.2f}%")
            else:
                continue
