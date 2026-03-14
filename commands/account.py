#!/usr/bin/env python3
"""
account 命令 - 账户管理
显示账户总览、存入现金、取出现金
"""

import json
from typing import Any
from mystocks import MyStocks
from mystocks.services.price_update_service import PriceUpdateService
from mystocks.storage.database import get_db


def format_account_summary_json(summary: dict) -> str:
    """格式化账户总览为 JSON"""
    output = {
        "account_name": summary.get('account_name', 'Unknown'),
        "cash_balance": summary.get('cash_balance', 0),
        "stock_market_value": summary.get('stock_market_value', 0),
        "total_account_value": summary.get('total_account_value', 0),
        "position_ratio": summary.get('position_ratio', 0),
        "total_invested": summary.get('total_invested', 0),
        "floating_pnl": summary.get('floating_pnl', 0),
        "floating_pnl_rate": summary.get('floating_pnl_rate', 0),
        "realized_pnl": summary.get('realized_pnl', 0),
        "total_pnl": summary.get('total_pnl', 0)
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_account(args: Any) -> None:
    """account 命令处理"""
    with MyStocks() as ms:
        if args.deposit:
            # 存入现金
            if args.deposit <= 0:
                print("❌ 存入金额必须大于 0")
                return

            account = ms.deposit(args.deposit)
            print(f"✅ 存入成功：¥{args.deposit:.2f}")
            print(f"   当前现金余额：¥{account.cash_balance:.2f}")
            print(f"   累计投入本金：¥{account.total_invested:.2f}")

        elif args.withdraw:
            # 取出现金
            if args.withdraw <= 0:
                print("❌ 取出金额必须大于 0")
                return

            try:
                account = ms.withdraw(args.withdraw)
                print(f"✅ 取出成功：¥{args.withdraw:.2f}")
                print(f"   当前现金余额：¥{account.cash_balance:.2f}")
            except ValueError as e:
                print(f"❌ 取款失败：{e}")

        else:  # 默认显示账户总览
            # 显示账户总览
            summary = ms.get_account_summary()

            # JSON 输出
            if getattr(args, 'json', False):
                print(format_account_summary_json(summary))
                return

            # 文本输出
            print("\n═══════════════════════════════════════════════════════")
            print(f"  账户总览 - {summary['account_name']}")
            print("═══════════════════════════════════════════════════════\n")

            # 资产信息
            print("📊 资产信息")
            print(f"   当前现金：¥{summary['cash_balance']:,.2f}")
            print(f"   持仓市值：¥{summary['stock_market_value']:,.2f}")
            print(f"   总资产：¥{summary['total_account_value']:,.2f}")
            print()

            # 仓位信息
            print("📈 仓位信息")
            print(f"   仓位比：{summary['position_ratio']:.1%}")
            print(f"   累计投入：¥{summary['total_invested']:,.2f}")
            print()

            # 盈亏信息
            print("💰 盈亏信息")
            print(f"   浮动盈亏：¥{summary['floating_pnl']:+,.2f} ({summary['floating_pnl_rate']:+.1%})")
            print(f"   已实现盈亏：¥{summary['realized_pnl']:+,.2f}")
            print(f"   总盈亏：¥{summary['total_pnl']:+,.2f}")
            print()

            print("═══════════════════════════════════════════════════════\n")


def format_holdings_json(holdings: list, total_market_value: float, total_cost: float) -> str:
    """格式化持仓详情为 JSON"""
    output = {
        "holdings": [],
        "summary": {
            "total_market_value": total_market_value,
            "total_cost": total_cost,
            "total_pnl": total_market_value - total_cost,
            "total_pnl_rate": (total_market_value - total_cost) / total_cost * 100 if total_cost > 0 else 0,
            "count": len(holdings)
        }
    }

    for h in holdings:
        output["holdings"].append({
            "stock_code": h.get('stock_code', ''),
            "stock_name": h.get('stock_name', ''),
            "quantity": h.get('quantity', 0),
            "avg_cost": h.get('avg_cost', 0),
            "current_price": h.get('current_price', 0),
            "market_value": h.get('market_value', 0),
            "floating_pnl": h.get('floating_pnl', 0),
            "floating_pnl_rate": h.get('floating_pnl_rate', 0),
            "position_ratio": h.get('position_ratio', 0)
        })

    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_holdings(args: Any) -> None:
    """holdings 命令处理 - 显示持仓详情"""
    with MyStocks() as ms:
        # 如果需要刷新价格
        if args.refresh:
            print("🔄 正在更新最新股价...")
            session = get_db().get_session()
            price_service = PriceUpdateService(session)
            price_service.update_all_positions_prices()
            session.close()
            print("✅ 股价更新完成")

        holdings = ms.get_holdings_with_details()

        if not holdings:
            if getattr(args, 'json', False):
                print(json.dumps({"holdings": [], "summary": None}, ensure_ascii=False, indent=2))
            else:
                print("当前无持仓")
            return

        # JSON 输出
        if getattr(args, 'json', False):
            total_market_value = sum(h.get('market_value', 0) for h in holdings)
            total_cost = sum(h.get('avg_cost', 0) * h.get('quantity', 0) for h in holdings)
            print(format_holdings_json(holdings, total_market_value, total_cost))
            return

        # 文本输出
        print("\n═══════════════════════════════════════════════════════")
        print("  持仓详情")
        print("═══════════════════════════════════════════════════════\n")

        for h in holdings:
            print(f"📌 {h['stock_code']} ({h['stock_name']})")
            print(f"   持仓：{h['quantity']} 股")
            print(f"   成本价：¥{h['avg_cost']:.2f}")
            print(f"   当前价：¥{h['current_price']:.2f}")
            print(f"   市值：¥{h['market_value']:,.2f}")
            print(f"   浮动盈亏：¥{h['floating_pnl']:+,.2f} ({h['floating_pnl_rate']:+.1f}%)")
            print(f"   仓位比：{h['position_ratio']:.1%}")
            print()

        print("═══════════════════════════════════════════════════════\n")
