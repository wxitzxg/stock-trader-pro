#!/usr/bin/env python3
"""
export 命令 - 导出历史 K 线数据
"""

from mystocks.services import get_historical_kline, export_kline_data


def cmd_export(args):
    """export 命令处理 - 导出历史 K 线数据"""
    if not args.code:
        print("Usage: python main.py export <code> [--days N] [-o output.csv]")
        print("Example: python main.py export 600519 --days 60 -o data.csv")
        return

    days = args.days or 60
    output = args.output or f"{args.code}_kline.csv"
    format_type = args.format or 'csv'

    print(f"导出 {args.code} 最近{days}天 K 线数据...\n")

    # 获取历史数据
    df = get_historical_kline(args.code, days=days)

    if df is None or df.empty:
        print("获取历史数据失败")
        return

    # 导出
    export_kline_data(df, output, format=format_type)
