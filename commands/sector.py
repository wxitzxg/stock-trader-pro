#!/usr/bin/env python3
"""
sector 命令 - 查看板块涨幅排行
"""

from mystocks.services import get_sector_rank, format_sector_report


def cmd_sector(args):
    """sector 命令处理 - 查看板块涨幅排行"""
    sector_type = 1  # 默认行业板块
    if args.concept:
        sector_type = 2
    elif args.region:
        sector_type = 3

    limit = args.limit or 50

    data = get_sector_rank(sector_type=sector_type, limit=limit)
    report = format_sector_report(data, limit=limit)
    print(report)
