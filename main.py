#!/usr/bin/env python3
"""
Technical Indicators Pro - 主入口
精简版：所有命令处理已分离到 commands/ 模块

约 100 行代码
"""

import sys
import argparse

# 导入所有命令处理函数
from commands import (
    cmd_analyze,
    cmd_portfolio,
    cmd_watchlist,
    cmd_monitor,
    cmd_alert,
    cmd_query,
    cmd_sector,
    cmd_flow,
    cmd_search,
    cmd_export,
    cmd_params,
    cmd_account,
    cmd_holdings,
)
from mystocks.storage.database import init_database


def cmd_init_db(args):
    """init-db 命令处理"""
    from config.settings import DATABASE_PATH
    init_database()
    print(f"✅ 数据库初始化成功：{DATABASE_PATH}")


def cmd_init_position(args):
    """init-position 命令处理 - 初始化持仓"""
    import subprocess
    import sys

    # 构建 mystocks init 命令
    cmd = [sys.executable, "-m", "mystocks", "init"]

    if args.code:
        cmd.extend(["--code", args.code])
    if args.name:
        cmd.extend(["--name", args.name])
    if args.qty:
        cmd.extend(["--qty", str(args.qty)])
    if args.cost:
        cmd.extend(["--cost", str(args.cost)])
    if args.price:
        cmd.extend(["--price", str(args.price)])
    if args.date:
        cmd.extend(["--date", args.date])
    if args.file:
        cmd.extend(["--file", args.file])
    if args.broker_file:
        cmd.extend(["--broker-file", args.broker_file])
    if args.broker:
        cmd.extend(["--broker", args.broker])
    if args.format:
        cmd.extend(["--format", args.format])
    if args.mode:
        cmd.extend(["--mode", args.mode])

    subprocess.run(cmd)


def cmd_daemon(args):
    """daemon 命令处理 - 启动后台监控进程"""
    from pathlib import Path
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from realalerts import SmartScheduler
    from commands.monitor import cmd_monitor
    from argparse import Namespace

    # 监控间隔（秒）
    interval = getattr(args, 'interval', 300)  # 默认 5 分钟
    output_dir = getattr(args, 'output_dir', None)

    print("🚀 启动后台监控进程...")
    print(f"📊 监控策略：仅交易日交易时段预警")
    print(f"📁 报告输出目录：{output_dir or '控制台'}")
    print("按 Ctrl+C 停止监控")
    print()

    run_count = [0]  # 使用列表以便在嵌套函数中修改

    def run_monitor():
        """监控任务执行函数"""
        result = SmartScheduler.should_run_now()

        if not result.get("run"):
            reason = result.get("reason", "未知原因")
            print(f"⏸️  跳过监控：{reason}")
            return

        run_count[0] += 1
        mode = result.get('mode', 'default')
        print(f"\n{'='*60}")
        print(f"🕐 执行监控 #{run_count[0]} (模式：{mode})")
        print(f"{'='*60}\n")

        # 构建 monitor 命令参数
        monitor_args = Namespace()
        monitor_args.output = None
        monitor_args.no_position = False
        monitor_args.no_watchlist = False

        # 如果指定了输出目录，生成报告文件
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            monitor_args.output = str(output_path / f"monitor_{timestamp}.md")

        # 执行监控
        try:
            cmd_monitor(monitor_args)
        except Exception as e:
            print(f"⚠️ 监控执行失败：{e}")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_monitor,
        trigger=IntervalTrigger(seconds=interval),
        id='market_monitor',
        name='市场监控',
        max_instances=1
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        print(f"\n👋 监控已停止（共执行 {run_count[0]} 次）")


def cmd_mystocks(args):
    """mystocks 命令处理 - 综合资产管理"""
    import subprocess
    import sys

    # 构建子命令
    cmd = [sys.executable, "-m", "mystocks", args.action]

    if args.code:
        cmd.extend(["--code", args.code])
    if args.qty:
        cmd.extend(["--qty", str(args.qty)])
    if args.price:
        cmd.extend(["--price", str(args.price)])
    if args.name:
        cmd.extend(["--name", args.name])
    if args.tags:
        cmd.extend(["--tags", args.tags])
    if args.target:
        cmd.extend(["--target", str(args.target)])
    if args.stop_loss:
        cmd.extend(["--stop-loss", str(args.stop_loss)])
    if args.notes:
        cmd.extend(["--notes", args.notes])
    if args.limit and args.action == "history":
        cmd.extend(["--limit", str(args.limit)])

    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description='Technical Indicators Pro - 专业波段交易系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze 600519 --full          # 完整技术分析
  python main.py query 600519 000001            # 查询实时行情
  python main.py sector                         # 查看行业板块排行
  python main.py flow 600519                    # 查看资金流向
  python main.py search 平安                      # 搜索股票
  python main.py export 600519 --days 60        # 导出历史数据
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析股票')
    analyze_parser.add_argument('symbol', nargs='?', help='股票代码')
    analyze_parser.add_argument('--days', type=int, default=250, help='历史数据天数')
    analyze_parser.add_argument('--full', action='store_true', help='完整分析 (所有策略)')
    analyze_parser.add_argument('--strategy', choices=['vcp', 'td', 'divergence'], help='指定策略')
    analyze_parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    analyze_parser.add_argument('--watchlist', action='store_true', help='分析收藏股列表')
    analyze_parser.set_defaults(func=cmd_analyze)

    # portfolio 命令 - 使用新的 mystocks 模块
    portfolio_parser = subparsers.add_parser('portfolio', help='持仓管理')
    portfolio_parser.add_argument('--list', action='store_true', help='查看持仓')
    portfolio_parser.add_argument('--buy', action='store_true', help='买入')
    portfolio_parser.add_argument('--sell', action='store_true', help='卖出')
    portfolio_parser.add_argument('--symbol', help='股票代码')
    portfolio_parser.add_argument('--qty', type=int, help='股数')
    portfolio_parser.add_argument('--price', type=float, help='成交价')
    portfolio_parser.add_argument('--name', help='股票名称')
    portfolio_parser.add_argument('--notes', help='备注')
    portfolio_parser.add_argument('--all', action='store_true', help='清仓（卖出全部）')
    portfolio_parser.set_defaults(func=cmd_portfolio)

    # account 命令 - 账户管理
    account_parser = subparsers.add_parser('account', help='账户管理')
    account_parser.add_argument('--summary', action='store_true', help='显示账户总览')
    account_parser.add_argument('--deposit', type=float, help='存入现金')
    account_parser.add_argument('--withdraw', type=float, help='取出现金')
    account_parser.set_defaults(func=cmd_account)

    # holdings 命令 - 持仓详情
    holdings_parser = subparsers.add_parser('holdings', help='持仓详情（含仓位比）')
    holdings_parser.add_argument('--refresh', action='store_true', help='刷新最新股价')
    holdings_parser.set_defaults(func=cmd_holdings)

    # watchlist 命令 - 使用新的 mystocks 模块
    watchlist_parser = subparsers.add_parser('watchlist', help='收藏股管理')
    watchlist_parser.add_argument('--list', action='store_true', help='查看收藏股')
    watchlist_parser.add_argument('--add', help='添加收藏股 (代码)')
    watchlist_parser.add_argument('--remove', help='删除收藏股 (代码)')
    watchlist_parser.add_argument('--name', help='股票名称')
    watchlist_parser.add_argument('--tags', help='标签 (逗号分隔)')
    watchlist_parser.add_argument('--notes', help='备注')
    watchlist_parser.add_argument('--target', type=float, help='目标价')
    watchlist_parser.add_argument('--stop-loss', type=float, help='止损价')
    watchlist_parser.set_defaults(func=cmd_watchlist)

    # mystocks 命令 - 新的综合资产管理
    mystocks_parser = subparsers.add_parser('mystocks', help='我的股票 (综合资产管理)')
    mystocks_parser.add_argument('action', choices=['pos', 'buy', 'sell', 'watch', 'summary', 'history'], help='操作类型')
    mystocks_parser.add_argument('--code', help='股票代码')
    mystocks_parser.add_argument('--qty', type=int, help='股数')
    mystocks_parser.add_argument('--price', type=float, help='价格')
    mystocks_parser.add_argument('--name', help='股票名称')
    mystocks_parser.add_argument('--tags', help='标签')
    mystocks_parser.add_argument('--target', type=float, help='目标价')
    mystocks_parser.add_argument('--stop-loss', type=float, help='止损价')
    mystocks_parser.add_argument('--notes', help='备注')
    mystocks_parser.add_argument('--limit', type=int, default=20, help='返回数量')
    mystocks_parser.set_defaults(func=cmd_mystocks)

    # monitor 命令 - 监控持仓股和收藏股
    monitor_parser = subparsers.add_parser('monitor', help='监控持仓股和收藏股信号')
    monitor_parser.add_argument('--output', '-o', help='输出文件路径（Markdown 格式）')
    monitor_parser.add_argument('--no-position', action='store_true', help='不监控持仓股')
    monitor_parser.add_argument('--no-watchlist', action='store_true', help='不监控收藏股')
    monitor_parser.set_defaults(func=cmd_monitor)

    # ========== stock-pro 整合命令 ==========

    # query 命令 - 查询实时行情
    query_parser = subparsers.add_parser('query', help='查询股票实时行情 (新浪 API)')
    query_parser.add_argument('codes', nargs='*', help='股票代码列表')
    query_parser.set_defaults(func=cmd_query)

    # sector 命令 - 板块排行
    sector_parser = subparsers.add_parser('sector', help='查看板块涨幅排行 (东方财富)')
    sector_parser.add_argument('--industry', action='store_true', help='行业板块 (默认)')
    sector_parser.add_argument('--concept', action='store_true', help='概念板块')
    sector_parser.add_argument('--region', action='store_true', help='地域板块')
    sector_parser.add_argument('--limit', type=int, default=50, help='返回数量')
    sector_parser.set_defaults(func=cmd_sector)

    # flow 命令 - 资金流向
    flow_parser = subparsers.add_parser('flow', help='查看资金流向分析 (AKShare)')
    flow_parser.add_argument('code', help='股票代码')
    flow_parser.set_defaults(func=cmd_flow)

    # search 命令 - 股票搜索
    search_parser = subparsers.add_parser('search', help='搜索股票 (AKShare)')
    search_parser.add_argument('keyword', help='搜索关键词 (代码或名称)')
    search_parser.set_defaults(func=cmd_search)

    # export 命令 - 数据导出
    export_parser = subparsers.add_parser('export', help='导出历史 K 线数据 (AKShare)')
    export_parser.add_argument('code', help='股票代码')
    export_parser.add_argument('--days', type=int, default=60, help='获取天数')
    export_parser.add_argument('-o', '--output', help='输出文件路径')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='导出格式')
    export_parser.set_defaults(func=cmd_export)

    # init-db 命令
    init_db_parser = subparsers.add_parser('init-db', help='初始化数据库')
    init_db_parser.set_defaults(func=cmd_init_db)

    # init-position 命令 - 初始化持仓
    init_position_parser = subparsers.add_parser('init-position', help='初始化持仓（导入已有持仓）')
    init_position_parser.add_argument('--code', help='股票代码（单只初始化模式）')
    init_position_parser.add_argument('--name', help='股票名称')
    init_position_parser.add_argument('--qty', type=int, help='持仓数量')
    init_position_parser.add_argument('--cost', type=float, help='成本价')
    init_position_parser.add_argument('--price', type=float, help='当前价')
    init_position_parser.add_argument('--date', help='建仓日期（格式：YYYY-MM-DD）')
    init_position_parser.add_argument('--file', help='导入文件路径（JSON/CSV）')
    init_position_parser.add_argument('--broker-file', help='券商交割单文件路径（CSV/XLSX）')
    init_position_parser.add_argument('--broker', help='券商名称（默认 auto 自动检测）')
    init_position_parser.add_argument('--format', choices=['json', 'csv'], help='文件格式')
    init_position_parser.add_argument('--mode', choices=['overwrite', 'add'], default='overwrite',
                                     help='导入模式：overwrite=覆盖，add=累加')
    init_position_parser.set_defaults(func=cmd_init_position)

    # ========== stock-monitor 整合命令 ==========

    # alert 命令 - 执行一次预警检查
    alert_parser = subparsers.add_parser('alert', help='执行一次智能预警检查')
    alert_parser.set_defaults(func=cmd_alert)

    # daemon 命令 - 后台常驻监控
    daemon_parser = subparsers.add_parser('daemon', help='启动后台监控进程 (7x24 小时)')
    daemon_parser.add_argument('--interval', type=int, default=300, help='监控间隔（秒，默认 300）')
    daemon_parser.add_argument('--output-dir', help='报告输出目录')
    daemon_parser.set_defaults(func=cmd_daemon)

    # params 命令 - 管理股票策略参数
    params_parser = subparsers.add_parser('params', help='管理股票策略参数')
    params_parser.add_argument('action', choices=['list', 'get', 'set', 'remove', 'defaults'],
                              help='操作类型')
    params_parser.add_argument('--symbol', help='股票代码')
    params_parser.add_argument('--name', help='股票名称')
    params_parser.add_argument('--params', help='参数配置 (逗号分隔，如 vcp.min_drops=3,zigzag.threshold=0.08)')
    params_parser.add_argument('--notes', help='备注说明')
    params_parser.set_defaults(func=cmd_params)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
