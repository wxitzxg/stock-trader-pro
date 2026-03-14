#!/usr/bin/env python3
"""
account 命令 - 账户管理
显示账户总览、存入现金、取出现金
"""

from typing import Any
from mystocks import MyStocks
from mystocks.services.price_update_service import PriceUpdateService
from mystocks.storage.database import get_db


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
            print("当前无持仓")
            return

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
