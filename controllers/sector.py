#!/usr/bin/env python3
"""
sector 命令 - 查看板块涨幅排行
"""

import json
from repositories.sources.akshare_source import AKShareDataSource


def format_sector_report(data: dict, limit: int = 50) -> str:
    """格式化板块报告"""
    if not data or 'error' in data:
        return "数据获取失败"

    # 板块数据格式处理
    if isinstance(data, list):
        # 板块排行列表
        report = f"{'排名':<6} {'板块名称':<20} {'涨跌幅':>12} {'上涨':>8} {'下跌':>8}\n"
        report += "=" * 60 + "\n"
        for i, sector in enumerate(data[:limit], 1):
            name = sector.get('name', 'N/A')
            change_pct = float(sector.get('change_pct', 0) or 0)
            up_count = sector.get('up_count', 0)
            down_count = sector.get('down_count', 0)
            sign = "+" if change_pct > 0 else ""
            report += f"{i:<6} {name:<20} {sign}{change_pct:>10.2f}% {up_count:>8} {down_count:>8}\n"
        return report

    # 单个板块
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

    akshare = AKShareDataSource()
    data = akshare.get_sector_rank(sector_type=sector_type, limit=limit)

    # JSON 输出
    if getattr(args, 'json', False):
        print(format_sector_json(data, sector_type, limit))
    else:
        # 文本输出
        report = format_sector_report(data, limit=limit)
        print(report)
