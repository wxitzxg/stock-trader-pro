#!/usr/bin/env python3
"""
sector 命令 - 查看板块涨幅排行
"""

import json
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


def format_sector_json(data: dict, sector_type: int, limit: int) -> str:
    """格式化板块数据为 JSON"""
    if not data:
        return json.dumps({"error": "数据获取失败"}, ensure_ascii=False, indent=2)

    type_map = {1: "industry", 2: "concept", 3: "region"}

    output = {
        "type": type_map.get(sector_type, "unknown"),
        "type_code": sector_type,
        "limit": limit,
        "data": data
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


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

    # JSON 输出
    if getattr(args, 'json', False):
        print(format_sector_json(data, sector_type, limit))
    else:
        # 文本输出
        report = format_sector_report(data, limit=limit)
        print(report)
