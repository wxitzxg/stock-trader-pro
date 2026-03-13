#!/usr/bin/env python3
"""
search 命令 - 搜索股票
"""

from mystocks.services import search_stock


def cmd_search(args):
    """search 命令处理 - 搜索股票"""
    if not args.keyword:
        print("Usage: python main.py search <keyword>")
        print("Example: python main.py search 平安")
        return

    print(f"搜索股票：{args.keyword}...\n")

    results = search_stock(args.keyword)

    if not results:
        print("未找到匹配的股票")
        return

    print(f"找到 {len(results)} 只匹配股票:\n")
    print(f"{'代码':<10} {'名称':<15} {'最新价':>10} {'涨跌幅':>10}")
    print("-" * 50)

    for r in results:
        code = r.get('代码', 'N/A')
        name = r.get('名称', 'N/A')
        price = r.get('最新价', 0)
        change_pct = r.get('涨跌幅', 0)
        print(f"{code:<10} {name:<15} {price:>10.2f} {change_pct:>10.2f}%")
