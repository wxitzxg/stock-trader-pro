#!/usr/bin/env python3
"""
portfolio 命令 - 持仓管理
使用新的 MyStocks 综合模块
"""

import json
from mystocks import MyStocks


def format_positions_json(positions: list, concentration: dict) -> str:
    """格式化持仓列表为 JSON"""
    output = {
        "positions": [],
        "summary": {},
        "concentration": {}
    }

    total_value = 0
    total_cost = 0

    for p in positions:
        market_value = p.current_price * p.quantity
        cost_value = p.avg_cost * p.quantity
        profit = market_value - cost_value
        profit_pct = profit / cost_value * 100 if cost_value > 0 else 0

        output["positions"].append({
            "stock_code": p.stock_code,
            "stock_name": p.stock_name,
            "quantity": p.quantity,
            "avg_cost": p.avg_cost,
            "current_price": p.current_price,
            "market_value": market_value,
            "profit": profit,
            "profit_pct": profit_pct,
            "realized_profit": p.realized_profit
        })

        total_value += market_value
        total_cost += cost_value

    total_profit = total_value - total_cost
    total_profit_pct = total_profit / total_cost * 100 if total_cost > 0 else 0

    output["summary"] = {
        "total_market_value": total_value,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_profit_pct": total_profit_pct,
        "count": len(positions)
    }

    output["concentration"] = {
        "herfindahl_index": concentration.get('herfindahl_index', 0),
        "top3_concentration": concentration.get('top3_concentration', 0)
    }

    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_portfolio(args):
    """portfolio 命令处理"""
    with MyStocks() as ms:
        if args.buy:
            # 买入
            if not args.symbol or not args.qty or not args.price:
                print("买入需要提供 --symbol, --qty, --price")
                return

            commission = ms.calculate_commission(args.qty * args.price, "buy")
            position = ms.buy(
                stock_code=args.symbol,
                stock_name=args.name or args.symbol,
                quantity=args.qty,
                price=args.price,
                commission=commission,
                notes=args.notes
            )
            print(f"✅ 买入成功：{args.symbol} +{args.qty} @ ¥{args.price:.2f}")
            print(f"   手续费：¥{commission:.2f}")
            print(f"   当前持仓：{position.quantity} 股，成本价 ¥{position.avg_cost:.2f}")

        elif args.sell:
            # 卖出
            if not args.symbol or not args.price:
                print("卖出需要提供 --symbol, --price")
                return

            # 清仓模式：卖出全部持仓
            if args.all:
                position = ms.get_position(args.symbol)
                if not position:
                    print(f"❌ 未找到持仓：{args.symbol}")
                    return
                args.qty = position.quantity

            commission = ms.calculate_commission(args.qty * args.price, "sell")
            position = ms.sell(
                stock_code=args.symbol,
                quantity=args.qty,
                price=args.price,
                commission=commission,
                notes=args.notes
            )

            if position:
                print(f"✅ 卖出成功：{args.symbol} -{args.qty} @ ¥{args.price:.2f}")
                print(f"   手续费：¥{commission:.2f}")
                print(f"   剩余持仓：{position.quantity} 股")
            else:
                print(f"✅ 已清仓：{args.symbol}")

        elif args.list or True:  # 默认显示持仓列表
            positions = ms.get_all_positions()

            if not positions:
                if getattr(args, 'json', False):
                    print(json.dumps({"positions": [], "summary": None, "concentration": None}, ensure_ascii=False, indent=2))
                else:
                    print("当前无持仓")
                return

            # JSON 输出
            if getattr(args, 'json', False):
                concentration = ms.get_concentration()
                print(format_positions_json(positions, concentration))
                return

            # 文本输出
            print("\n═══════════════════════════════════════════════════════")
            print("  持仓列表")
            print("═══════════════════════════════════════════════════════\n")

            total_value = 0
            total_cost = 0

            for p in positions:
                market_value = p.current_price * p.quantity
                cost_value = p.avg_cost * p.quantity
                profit = market_value - cost_value
                profit_pct = profit / cost_value * 100 if cost_value > 0 else 0

                print(f"📌 {p.stock_code} ({p.stock_name})")
                print(f"   持仓：{p.quantity} 股")
                print(f"   成本价：¥{p.avg_cost:.2f}")
                print(f"   当前价：¥{p.current_price:.2f}")
                print(f"   市值：¥{market_value:.2f}")
                print(f"   盈亏：¥{profit:+.2f} ({profit_pct:+.1f}%)")
                print(f"   实现盈亏：¥{p.realized_profit:+.2f}")
                print()

                total_value += market_value
                total_cost += cost_value

            # 汇总
            total_profit = total_value - total_cost
            total_profit_pct = total_profit / total_cost * 100 if total_cost > 0 else 0

            print("───────────────────────────────────────────────────────")
            print(f"合计 市值：¥{total_value:.2f}")
            print(f"合计 成本：¥{total_cost:.2f}")
            print(f"合计 盈亏：¥{total_profit:+.2f} ({total_profit_pct:+.1f}%)")
            print(f"持仓数量：{len(positions)} 只")

            # 集中度分析
            concentration = ms.get_concentration()
            print(f"\n持仓集中度 (HHI): {concentration['herfindahl_index']:.3f}")
            print(f"前三大持仓占比：{concentration['top3_concentration']:.1%}")
            print("═══════════════════════════════════════════════════════\n")
