#!/usr/bin/env python3
"""
params 命令 - 管理股票策略参数
支持查看、设置、删除每支股票的独立策略参数
"""

import json
from config.params_loader import StockParamsLoader


def cmd_params(args):
    """params 命令处理"""
    loader = StockParamsLoader()

    if args.action == 'list':
        _cmd_list(loader)
    elif args.action == 'get':
        _cmd_get(loader, args.symbol)
    elif args.action == 'set':
        _cmd_set(loader, args)
    elif args.action == 'remove':
        _cmd_remove(loader, args.symbol)
    elif args.action == 'defaults':
        _cmd_defaults(loader)


def _cmd_list(loader):
    """列出所有配置了参数的股票"""
    stocks = loader.list_all_stocks()
    if not stocks:
        print("暂无配置股票特定参数")
        print("\n使用以下命令添加股票参数:")
        print("  python main.py params set --symbol 600519 --name 贵州茅台 --params \"vcp.min_drops=3,zigzag.threshold=0.08\"")
        return

    print(f"已配置 {len(stocks)} 只股票:\n")
    for symbol in stocks:
        params = loader.get_stock_info(symbol)
        name = params.get('name', 'Unknown')
        notes = params.get('notes', '')
        print(f"  {symbol} - {name}")
        if notes:
            print(f"    备注：{notes}")


def _cmd_get(loader, symbol):
    """获取股票参数"""
    if not symbol:
        print("错误：请指定股票代码")
        print("用法：python main.py params get --symbol 600519")
        return

    params = loader.get_stock_info(symbol)
    if not params:
        print(f"股票 {symbol} 未配置特定参数（使用默认值）")
        print("\n使用以下命令设置参数:")
        print(f"  python main.py params set --symbol {symbol} --params \"vcp.min_drops=3,zigzag.threshold=0.08\"")
        return

    # 获取合并后的参数
    vcp_params = loader.get_vcp_params(symbol)
    zigzag_params = loader.get_zigzag_params(symbol)
    td_params = loader.get_td_params(symbol)

    print(f"股票 {symbol} 参数配置:\n")
    print(f"名称：{params.get('name', 'N/A')}")
    if params.get('notes'):
        print(f"备注：{params.get('notes')}")
    print("\nVCP 参数:")
    print(json.dumps(vcp_params, indent=2, ensure_ascii=False))
    print("\nZigZag 参数:")
    print(json.dumps(zigzag_params, indent=2, ensure_ascii=False))
    print("\nTD Sequential 参数:")
    print(json.dumps(td_params, indent=2, ensure_ascii=False))


def _cmd_set(loader, args):
    """设置股票参数"""
    if not args.symbol:
        print("错误：请指定股票代码")
        print("用法：python main.py params set --symbol 600519 --params \"vcp.min_drops=3\"")
        return

    # 解析参数字符串 (如 "vcp.min_drops=3,zigzag.threshold=0.08")
    updates = {}
    if args.params:
        for item in args.params.split(','):
            if '=' in item:
                key, value = item.split('=', 1)
                # 支持嵌套键 (如 vcp.min_drops)
                if '.' in key:
                    parent, child = key.split('.', 1)
                    if parent not in updates:
                        updates[parent] = {}
                    # 类型转换
                    try:
                        updates[parent][child] = json.loads(value)
                    except json.JSONDecodeError:
                        updates[parent][child] = value
                else:
                    try:
                        updates[key] = json.loads(value)
                    except json.JSONDecodeError:
                        updates[key] = value

    if not updates:
        print("错误：请指定参数配置")
        print("用法：python main.py params set --symbol 600519 --params \"vcp.min_drops=3,zigzag.threshold=0.08\"")
        return

    # 设置参数
    stock_info = loader.get_stock_info(args.symbol)
    name = args.name or (stock_info.get('name') if stock_info else None)
    loader.set_stock_params(args.symbol, name=name, **updates)

    if args.notes:
        stock_info = loader.get_stock_info(args.symbol) or {}
        existing_notes = stock_info.get('notes', '')
        loader._stocks[args.symbol]['notes'] = args.notes

    loader.save_params()

    # 显示确认信息
    print(f"✅ 已更新股票 {args.symbol} 参数配置")
    print("\n设置的参数:")
    for key, value in updates.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                print(f"  {key}.{sub_key} = {sub_value}")
        else:
            print(f"  {key} = {value}")
    if name:
        print(f"  名称：{name}")
    if args.notes:
        print(f"  备注：{args.notes}")


def _cmd_remove(loader, symbol):
    """删除股票参数配置"""
    if not symbol:
        print("错误：请指定股票代码")
        print("用法：python main.py params remove --symbol 600519")
        return

    if loader.remove_stock_params(symbol):
        loader.save_params()
        print(f"✅ 已删除股票 {symbol} 参数配置")
    else:
        print(f"股票 {symbol} 未配置参数")


def _cmd_defaults(loader):
    """查看默认参数"""
    defaults = loader.get_defaults()
    if not defaults:
        print("暂无默认参数配置")
        return

    print("默认参数配置:\n")
    print(json.dumps(defaults, indent=2, ensure_ascii=False))
