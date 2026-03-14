#!/usr/bin/env python3
"""
flow 命令 - 查看资金流向分析
"""

import json
from infrastructure.unified_service import UnifiedStockQueryService


def format_flow_json(code: str, flow_data: dict) -> str:
    """格式化资金流向数据为 JSON"""
    if not flow_data or 'error' in flow_data:
        return json.dumps({"error": "数据获取失败"}, ensure_ascii=False, indent=2)

    summary = flow_data.get('summary', {})
    if not summary:
        return json.dumps({"code": code, "data": None, "message": "暂无资金流向数据"}, ensure_ascii=False, indent=2)

    output = {
        "code": code,
        "date": summary.get('date', 'N/A'),
        "data": {
            "main_force_in": summary.get('main_force_in', 0) / 10000,
            "big_order_in": summary.get('big_order_in', 0) / 10000,
            "medium_order_in": summary.get('medium_order_in', 0) / 10000,
            "small_order_in": summary.get('small_order_in', 0) / 10000
        },
        "sentiment": "bullish" if summary.get('main_force_in', 0) > 0 else "bearish"
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_flow(args):
    """flow 命令处理 - 查看资金流向分析"""
    if not args.code:
        print("Usage: python3 main.py flow <code>")
        print("Example: python3 main.py flow 600519")
        return

    stock_query = UnifiedStockQueryService()
    flow_data = stock_query.get_fund_flow(args.code)

    # JSON 输出
    if getattr(args, 'json', False):
        print(format_flow_json(args.code, flow_data))
        return

    # 文本输出
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
