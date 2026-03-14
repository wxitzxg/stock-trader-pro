#!/usr/bin/env python3
"""
账户功能测试脚本
测试买入、卖出、清仓、账户总览等功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mystocks import MyStocks


def test_account_functions():
    """测试账户功能"""
    print("=" * 60)
    print("  账户功能测试")
    print("=" * 60)

    with MyStocks() as ms:
        # 1. 初始存款
        print("\n[测试 1] 存入现金...")
        try:
            account = ms.deposit(100000)  # 存入 10 万
            print(f"✅ 存入成功：¥100,000")
            print(f"   当前现金：¥{account.cash_balance:,.2f}")
        except Exception as e:
            print(f"❌ 存入失败：{e}")
            return

        # 2. 显示账户总览
        print("\n[测试 2] 显示账户总览...")
        summary = ms.get_account_summary()
        print(f"   账户名称：{summary['account_name']}")
        print(f"   当前现金：¥{summary['cash_balance']:,.2f}")
        print(f"   总资产：¥{summary['total_account_value']:,.2f}")
        print(f"   仓位比：{summary['position_ratio']:.1%}")

        # 3. 买入股票
        print("\n[测试 3] 买入股票...")
        try:
            position = ms.buy(
                stock_code="600519",
                stock_name="贵州茅台",
                quantity=100,
                price=1500.00,
                notes="测试买入"
            )
            print(f"✅ 买入成功：600519 +100 股 @ ¥1500.00")
            print(f"   当前持仓：{position.quantity} 股")
            print(f"   成本价：¥{position.avg_cost:.2f}")
        except Exception as e:
            print(f"❌ 买入失败：{e}")

        # 4. 显示账户总览（买入后）
        print("\n[测试 4] 显示账户总览（买入后）...")
        summary = ms.get_account_summary()
        print(f"   当前现金：¥{summary['cash_balance']:,.2f}")
        print(f"   持仓市值：¥{summary['stock_market_value']:,.2f}")
        print(f"   总资产：¥{summary['total_account_value']:,.2f}")
        print(f"   仓位比：{summary['position_ratio']:.1%}")

        # 5. 显示持仓详情
        print("\n[测试 5] 显示持仓详情...")
        holdings = ms.get_holdings_with_details()
        for h in holdings:
            print(f"   {h['stock_code']} ({h['stock_name']})")
            print(f"      市值：¥{h['market_value']:,.2f}")
            print(f"      仓位比：{h['position_ratio']:.1%}")

        # 6. 部分卖出
        print("\n[测试 6] 部分卖出...")
        try:
            position = ms.sell(
                stock_code="600519",
                quantity=50,
                price=1600.00,
                notes="测试卖出"
            )
            if position:
                print(f"✅ 卖出成功：600519 -50 股 @ ¥1600.00")
                print(f"   剩余持仓：{position.quantity} 股")
        except Exception as e:
            print(f"❌ 卖出失败：{e}")

        # 7. 显示账户总览（卖出后）
        print("\n[测试 7] 显示账户总览（卖出后）...")
        summary = ms.get_account_summary()
        print(f"   当前现金：¥{summary['cash_balance']:,.2f}")
        print(f"   已实现盈亏：¥{summary['realized_pnl']:+,.2f}")
        print(f"   总盈亏：¥{summary['total_pnl']:+,.2f}")

        # 8. 清仓
        print("\n[测试 8] 清仓...")
        try:
            position = ms.get_position("600519")
            if position:
                ms.sell(
                    stock_code="600519",
                    quantity=position.quantity,
                    price=1650.00,
                    notes="清仓"
                )
                print(f"✅ 已清仓：600519")
        except Exception as e:
            print(f"❌ 清仓失败：{e}")

        # 9. 显示账户总览（清仓后）
        print("\n[测试 9] 显示账户总览（清仓后）...")
        summary = ms.get_account_summary()
        print(f"   当前现金：¥{summary['cash_balance']:,.2f}")
        print(f"   持仓市值：¥{summary['stock_market_value']:,.2f}")
        print(f"   已实现盈亏：¥{summary['realized_pnl']:+,.2f}")
        print(f"   总盈亏：¥{summary['total_pnl']:+,.2f}")

        # 10. 测试取款
        print("\n[测试 10] 测试取款...")
        try:
            account = ms.withdraw(10000)
            print(f"✅ 取出成功：¥10,000")
            print(f"   当前现金：¥{account.cash_balance:,.2f}")
        except Exception as e:
            print(f"❌ 取款失败：{e}")

        print("\n" + "=" * 60)
        print("  测试完成")
        print("=" * 60)


if __name__ == "__main__":
    test_account_functions()
