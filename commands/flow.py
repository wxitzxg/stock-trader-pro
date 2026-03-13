#!/usr/bin/env python3
"""
flow 命令 - 查看资金流向分析
"""

from mystocks.services import get_fund_flow


def cmd_flow(args):
    """flow 命令处理 - 查看资金流向分析"""
    if not args.code:
        print("Usage: python main.py flow <code>")
        print("Example: python main.py flow 600519")
        return

    print(f"分析 {args.code} 资金流向...\n")

    flow_data = get_fund_flow(args.code)

    if 'error' in flow_data:
        print(f"获取失败：{flow_data['error']}")
        return

    summary = flow_data.get('summary', {})
    if not summary:
        print("暂无资金流向数据")
        return

    print(f"""═══════════════════════════════════════════════════════
  {args.code} 资金流向分析
═══════════════════════════════════════════════════════
日期：{summary.get('date', 'N/A')}

主力净流入：¥{summary.get('main_force_in', 0)/10000:.2f} 万元
├─ 大单净流入：¥{summary.get('big_order_in', 0)/10000:.2f} 万元
├─ 中单净流入：¥{summary.get('medium_order_in', 0)/10000:.2f} 万元
└─ 小单净流入：¥{summary.get('small_order_in', 0)/10000:.2f} 万元
═══════════════════════════════════════════════════════""")

    # 判断主力态度
    main_in = summary.get('main_force_in', 0)
    if main_in > 0:
        print(f"💰 主力净流入 {main_in/10000:.2f} 万元，偏向多头")
    else:
        print(f"💸 主力净流出 {abs(main_in)/10000:.2f} 万元，偏向空头")
