#!/usr/bin/env python3
"""
export 命令 - 导出历史 K 线数据
"""

from datetime import datetime, timedelta
from repositories.sources.akshare_source import AKShareDataSource
import pandas as pd


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

    # 计算日期范围
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

    # 获取历史数据
    akshare = AKShareDataSource()
    df = akshare.get_historical_data(args.code, start_date=start_date, end_date=end_date)

    if df is None or df.empty:
        print("获取历史数据失败")
        return

    # 导出
    if format_type == 'csv':
        df.to_csv(output, index=False)
    elif format_type == 'json':
        df.to_json(output, orient='records', force_ascii=False)
    print(f"已导出数据到：{output}")
