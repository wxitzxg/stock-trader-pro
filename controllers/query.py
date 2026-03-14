#!/usr/bin/env python3
"""
query 命令 - 查询股票实时行情
"""

import json
from repositories.sources.akshare_source import AKShareDataSource


def format_stock_info(quote: dict) -> str:
    """格式化股票信息"""
    if not quote or 'error' in quote:
        return "数据获取失败"

    name = quote.get('name', 'Unknown')
    code = quote.get('symbol', quote.get('code', 'N/A'))
    price = quote.get('price', 0)
    change_pct = quote.get('change_pct', 0)

    # 中国习惯：红涨绿跌
    if change_pct > 0:
        color = "🔴"
        sign = "+"
    elif change_pct < 0:
        color = "🟢"
        sign = ""
    else:
        color = "⚪"
        sign = ""

    return f"{color} {name} ({code})\n" \
           f"  当前价：¥{price:.2f} ({sign}{change_pct:.2f}%)\n" \
           f"  今开：¥{quote.get('open', 'N/A')}\n" \
           f"  最高：¥{quote.get('high', 'N/A')}\n" \
           f"  最低：¥{quote.get('low', 'N/A')}\n" \
           f"  昨收：¥{quote.get('prev_close', 'N/A')}\n" \
           f"  成交量：{quote.get('volume', 0):,}"


def format_quote_json(quotes: list) -> str:
    """格式化行情数据为 JSON"""
    return json.dumps({
        "stocks": quotes,
        "total": len(quotes)
    }, ensure_ascii=False, indent=2)


def cmd_query(args):
    """query 命令处理 - 查询股票实时行情"""
    if not args.codes:
        print("Usage: python main.py query <code1> [code2] ...")
        print("Example: python main.py query 600519 000001 300750")
        return

    stock_query = AKShareDataSource()
    quotes = []

    for code in args.codes:
        quote = stock_query.get_quote(code)
        if quote:
            quotes.append(quote)

    # JSON 输出
    if getattr(args, 'json', False):
        print(format_quote_json(quotes))
    else:
        # 文本输出
        if not quotes:
            print("查询失败，未获取到任何数据")
            return

        print(f"查询 {len(args.codes)} 只股票实时行情...\n")
        for quote in quotes:
            print(format_stock_info(quote))
            print()
