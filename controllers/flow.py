#!/usr/bin/env python3
"""
flow 命令 - 查看资金流向分析
"""

import json
from services.fund_flow import FundFlowAnalyzer


def format_flow_json(code: str, flow_data: dict) -> str:
    """格式化资金流向数据为 JSON"""
    if not flow_data or 'error' in flow_data:
        return json.dumps({"error": "数据获取失败"}, ensure_ascii=False, indent=2)

    output = {
        "code": code,
        "data": flow_data,
        "sentiment": "bullish" if flow_data.get('main_inflow', 0) > 0 else "bearish"
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_flow(args):
    """flow 命令处理 - 查看资金流向分析"""
    if not args.code:
        print("Usage: python3 main.py flow <code>")
        print("Example: python3 main.py flow 600519")
        return

    analyzer = FundFlowAnalyzer()
    flow_data = analyzer.fetch_fund_flow(args.code)

    # JSON 输出
    if getattr(args, 'json', False):
        print(format_flow_json(args.code, flow_data))
        return

    # 文本输出
    if 'error' in flow_data:
        print(f"获取失败：{flow_data['error']}")
        return

    report = analyzer.generate_flow_report(flow_data)
    print(report)
