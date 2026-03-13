#!/usr/bin/env python3
"""
query 命令 - 查询股票实时行情
"""

from mystocks.services import get_stock_quote, format_stock_info


def cmd_query(args):
    """query 命令处理 - 查询股票实时行情"""
    if not args.codes:
        print("Usage: python main.py query <code1> [code2] ...")
        print("Example: python main.py query 600519 000001 300750")
        return

    print(f"查询 {len(args.codes)} 只股票实时行情...\n")

    for code in args.codes:
        quote = get_stock_quote(code)
        print(format_stock_info(quote))
        print()
