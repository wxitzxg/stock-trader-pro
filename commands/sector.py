#!/usr/bin/env python3
"""
sector 命令 - 查看板块涨幅排行
"""

from stockquery import UnifiedStockQueryService


def format_sector_report(data: dict, limit: int = 50) -> str:
    """格式化板块报告"""
    if not data or 'error' in data:
        return "数据获取失败"

    name = data.get('name', 'Unknown')
    change_pct = data.get('change_pct', 0)

    if change_pct > 0:
        color = "🔴"
        sign = "+"
    elif change_pct < 0:
        color = "🟢"
        sign = ""
    else:
        color = "⚪"
        sign = ""

    return f"{color} {name}\n" \
           f"  涨跌幅：{sign}{change_pct:.2f}%\n" \
           f"  上涨：{data.get('up_count', 0)}\n" \
           f"  下跌：{data.get('down_count', 0)}\n" \
           f"  领涨股：{data.get('top_stock', 'N/A')}"


def cmd_sector(args):
    """sector 命令处理 - 查看板块涨幅排行"""
    sector_type = 1  # 默认行业板块
    if args.concept:
        sector_type = 2
    elif args.region:
        sector_type = 3

    limit = args.limit or 50

    stock_query = UnifiedStockQueryService()
    data = stock_query.get_sector_rank(sector_type=sector_type, limit=limit)
    report = format_sector_report(data, limit=limit)
    print(report)
