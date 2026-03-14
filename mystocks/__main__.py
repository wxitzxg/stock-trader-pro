#!/usr/bin/env python3
"""
我的股票 - 命令行工具

Commands:
  mystocks buy          买入股票
  mystocks sell         卖出股票
  mystocks pos          查看持仓
  mystocks watch        收藏管理
  mystocks summary      资产汇总
  mystocks history      交易历史
  mystocks init         初始化持仓（导入已有持仓）
  mystocks update-prices 定时更新持仓价格
"""

import sys
import argparse
from datetime import datetime

from domain.portfolio.services import MyStocks
from commands.update_prices import cmd_update_prices, setup_parser as setup_update_prices_parser


def cmd_init(args):
    """初始化持仓"""
    with MyStocks() as ms:
        if args.file:
            # 从文件批量导入（JSON/CSV）
            file_format = args.format or ('json' if args.file.endswith('.json') else 'csv')
            positions = ms.initialize_positions_from_file(
                args.file,
                file_format=file_format,
                mode=args.mode
            )
            print(f"✅ 成功导入 {len(positions)} 只持仓")
            for p in positions:
                print(f"   📌 {p.stock_code} ({p.stock_name}): {p.quantity}股 @ ¥{p.avg_cost:.4f}")

        else:
            # 单只初始化（支持自动获取股票信息）
            position = ms.initialize_position(
                stock_code=args.code,
                quantity=args.qty,
                avg_cost=args.cost,
                current_price=args.price,  # 可为 None，自动获取
                stock_name=args.name,  # 可为 None，自动获取
                purchase_date=args.date,
                mode=args.mode
            )
            print(f"✅ 初始化成功：{args.code}")
            print(f"   持仓：{position.quantity} 股")
            print(f"   成本价：¥{position.avg_cost:.4f}")
            print(f"   当前价：¥{position.current_price:.2f}")
            # 负成本盈亏计算
            if position.avg_cost < 0:
                profit = (abs(position.avg_cost) + position.current_price) * position.quantity
                print(f"   浮动盈亏：¥{profit:+.2f} (N/A - 负成本)")
            else:
                profit = (position.current_price - position.avg_cost) * position.quantity
                profit_rate = profit / position.avg_cost / position.quantity * 100
                print(f"   浮动盈亏：¥{profit:+.2f} ({profit_rate:+.1f}%)")


def cmd_buy(args):
    """买入股票"""
    with MyStocks() as ms:
        commission = ms.calculate_commission(args.qty * args.price, "buy")
        position = ms.buy(
            stock_code=args.code,
            stock_name=args.name or args.code,
            quantity=args.qty,
            price=args.price,
            commission=commission,
            notes=args.notes
        )
        print(f"✅ 买入成功：{args.code} +{args.qty} @ ¥{args.price:.2f}")
        print(f"   手续费：¥{commission:.2f}")
        print(f"   当前持仓：{position.quantity} 股，成本价 ¥{position.avg_cost:.2f}")


def cmd_sell(args):
    """卖出股票"""
    with MyStocks() as ms:
        commission = ms.calculate_commission(args.qty * args.price, "sell")
        position = ms.sell(
            stock_code=args.code,
            quantity=args.qty,
            price=args.price,
            commission=commission,
            notes=args.notes
        )
        if position:
            print(f"✅ 卖出成功：{args.code} -{args.qty} @ ¥{args.price:.2f}")
            print(f"   手续费：¥{commission:.2f}")
            print(f"   剩余持仓：{position.quantity} 股")
        else:
            print(f"✅ 已清仓：{args.code}")


def cmd_pos(args):
    """查看持仓"""
    with MyStocks() as ms:
        positions = ms.get_all_positions()

        if not positions:
            print("当前无持仓")
            return

        print("\n═══════════════════════════════════════════════════════")
        print("  持仓列表")
        print("═══════════════════════════════════════════════════════\n")

        total_value = 0
        total_cost = 0

        for p in positions:
            market_value = p.current_price * p.quantity
            cost_value = p.avg_cost * p.quantity
            # 使用已计算的 profit_loss，而不是重新计算
            profit = p.profit_loss
            # 负成本时盈亏率无意义
            if p.avg_cost < 0:
                profit_pct_str = "N/A (负成本)"
            else:
                profit_pct = p.profit_rate if p.profit_rate is not None else 0
                profit_pct_str = f"{profit_pct:+.1f}%"

            print(f"📌 {p.stock_code} ({p.stock_name})")
            print(f"   持仓：{p.quantity} 股")
            print(f"   成本价：¥{p.avg_cost:.4f}")
            print(f"   当前价：¥{p.current_price:.2f}")
            print(f"   市值：¥{market_value:.2f}")
            print(f"   盈亏：¥{profit:+.2f} ({profit_pct_str})")
            print(f"   实现盈亏：¥{p.realized_profit:+.2f}")
            print()

            total_value += market_value
            total_cost += cost_value

        total_profit = sum(p.profit_loss for p in positions)  # 使用已计算的 profit_loss
        # 检查是否存在负成本持仓
        has_negative_cost = any(p.avg_cost < 0 for p in positions)
        if has_negative_cost:
            total_profit_pct_str = "N/A (存在负成本持仓)"
        else:
            total_profit_pct = total_profit / total_cost * 100 if total_cost > 0 else 0
            total_profit_pct_str = f"{total_profit_pct:+.1f}%"

        print("───────────────────────────────────────────────────────")
        print(f"合计 市值：¥{total_value:.2f}")
        print(f"合计 成本：¥{total_cost:.2f}")
        print(f"合计 盈亏：¥{total_profit:+.2f} ({total_profit_pct_str})")
        print(f"持仓数量：{len(positions)} 只")

        # 集中度分析
        concentration = ms.get_concentration()
        print(f"\n持仓集中度 (HHI): {concentration['herfindahl_index']:.3f}")
        print(f"前三大持仓占比：{concentration['top3_concentration']:.1%}")
        print("═══════════════════════════════════════════════════════\n")


def cmd_watch(args):
    """收藏管理"""
    with MyStocks() as ms:
        if args.add:
            # 添加收藏
            wl = ms.add_to_watchlist(
                stock_code=args.add,
                stock_name=args.name,
                tags=args.tags,
                target_price=args.target,
                stop_loss=args.stop_loss
            )
            print(f"✅ 添加收藏：{args.add} {args.name or ''}")

        elif args.remove:
            # 删除收藏
            if ms.remove_from_watchlist(args.remove):
                print(f"✅ 已删除：{args.remove}")
            else:
                print(f"❌ 未找到：{args.remove}")

        elif args.list or True:
            # 显示列表
            stocks = ms.get_watchlist()

            if not stocks:
                print("收藏股列表为空")
                return

            print("\n═══════════════════════════════════════════════════════")
            print("  收藏股列表")
            print("═══════════════════════════════════════════════════════\n")

            for wl in stocks:
                print(f"📌 {wl.stock_code} ({wl.stock_name})")
                if wl.tags:
                    print(f"   标签：{wl.tags}")
                if wl.target_price:
                    print(f"   目标价：¥{wl.target_price:.2f}")
                if wl.stop_loss:
                    print(f"   止损价：¥{wl.stop_loss:.2f}")
                print()

            print(f"共 {len(stocks)} 只股票")
            print("═══════════════════════════════════════════════════════\n")


def cmd_summary(args):
    """资产汇总"""
    with MyStocks() as ms:
        summary = ms.get_portfolio_summary()
        concentration = ms.get_concentration()

        print("\n═══════════════════════════════════════════════════════")
        print("  资产汇总")
        print("═══════════════════════════════════════════════════════\n")

        print(f"💰 总市值：¥{summary['total_value']:.2f}")
        print(f"📊 总成本：¥{summary['total_cost']:.2f}")
        # 负成本时盈亏率显示为 N/A
        if summary.get('total_profit_rate') is None or summary.get('has_negative_cost'):
            print(f"📈 浮动盈亏：¥{summary['total_profit']:+.2f} (N/A - 存在负成本持仓)")
        else:
            print(f"📈 浮动盈亏：¥{summary['total_profit']:+.2f} ({summary['total_profit_rate']:+.1f}%)")
        print(f"💵 已实现盈亏：¥{summary['total_realized_profit']:+.2f}")
        print(f"📦 持仓数量：{summary['position_count']} 只")

        print(f"\n───────────────────────────────────────────────────────")
        print(f"持仓集中度 (HHI): {concentration['herfindahl_index']:.3f}")
        print(f"前三大持仓占比：{concentration['top3_concentration']:.1%}")
        print(f"最大单一持仓：{concentration['max_position_concentration']:.1%}")
        print("═══════════════════════════════════════════════════════\n")


def cmd_history(args):
    """交易历史"""
    with MyStocks() as ms:
        transactions = ms.get_transactions(limit=args.limit or 20)

        if not transactions:
            print("暂无交易记录")
            return

        print(f"\n最近 {len(transactions)} 条交易记录:\n")
        print(f"{'时间':<20} {'代码':<10} {'操作':<6} {'数量':>10} {'价格':>10} {'金额':>12}")
        print("-" * 70)

        for t in transactions:
            time_str = t.timestamp.strftime("%Y-%m-%d %H:%M")
            op = "买入" if t.operation == "buy" else "卖出"
            amount = t.quantity * t.price
            print(f"{time_str:<20} {t.stock_code:<10} {op:<6} {t.quantity:>10} {t.price:>10.2f} {amount:>12.2f}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description='我的股票 - 综合资产管理',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # buy 命令
    buy_parser = subparsers.add_parser('buy', help='买入股票')
    buy_parser.add_argument('code', help='股票代码')
    buy_parser.add_argument('--qty', type=int, required=True, help='股数')
    buy_parser.add_argument('--price', type=float, required=True, help='成交价')
    buy_parser.add_argument('--name', help='股票名称')
    buy_parser.add_argument('--notes', help='备注')
    buy_parser.set_defaults(func=cmd_buy)

    # sell 命令
    sell_parser = subparsers.add_parser('sell', help='卖出股票')
    sell_parser.add_argument('code', help='股票代码')
    sell_parser.add_argument('--qty', type=int, required=True, help='股数')
    sell_parser.add_argument('--price', type=float, required=True, help='成交价')
    sell_parser.add_argument('--notes', help='备注')
    sell_parser.set_defaults(func=cmd_sell)

    # pos 命令
    pos_parser = subparsers.add_parser('pos', help='查看持仓')
    pos_parser.set_defaults(func=cmd_pos)

    # watch 命令
    watch_parser = subparsers.add_parser('watch', help='收藏管理')
    watch_parser.add_argument('--list', action='store_true', help='查看收藏')
    watch_parser.add_argument('--add', help='添加收藏 (代码)')
    watch_parser.add_argument('--remove', help='删除收藏 (代码)')
    watch_parser.add_argument('--name', help='股票名称')
    watch_parser.add_argument('--tags', help='标签 (逗号分隔)')
    watch_parser.add_argument('--target', type=float, help='目标价')
    watch_parser.add_argument('--stop-loss', type=float, help='止损价')
    watch_parser.set_defaults(func=cmd_watch)

    # summary 命令
    summary_parser = subparsers.add_parser('summary', help='资产汇总')
    summary_parser.set_defaults(func=cmd_summary)

    # history 命令
    history_parser = subparsers.add_parser('history', help='交易历史')
    history_parser.add_argument('--limit', type=int, default=20, help='返回数量')
    history_parser.set_defaults(func=cmd_history)

    # init 命令 - 初始化持仓
    init_parser = subparsers.add_parser('init', help='初始化持仓（导入已有持仓）')
    init_parser.add_argument('--code', help='股票代码（单只初始化模式）')
    init_parser.add_argument('--name', help='股票名称')
    init_parser.add_argument('--qty', type=int, help='持仓数量')
    init_parser.add_argument('--cost', type=float, help='成本价')
    init_parser.add_argument('--price', type=float, help='当前价')
    init_parser.add_argument('--date', help='建仓日期（格式：YYYY-MM-DD）')
    init_parser.add_argument('--file', help='导入文件路径（JSON/CSV）')
    init_parser.add_argument('--format', choices=['json', 'csv'], help='文件格式（默认根据扩展名判断）')
    init_parser.add_argument('--mode', choices=['overwrite', 'add'], default='overwrite',
                            help='导入模式：overwrite=覆盖原有持仓，add=累加到原有持仓')
    init_parser.set_defaults(func=cmd_init)

    # update-prices 命令 - 定时更新持仓价格
    update_prices_parser = subparsers.add_parser('update-prices', help='定时更新持仓价格')
    setup_update_prices_parser(update_prices_parser)
    update_prices_parser.set_defaults(func=cmd_update_prices)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
