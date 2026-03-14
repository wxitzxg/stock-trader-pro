"""
资金流向分析模块 (Fund Flow Analysis)
获取并分析个股资金流向数据
"""

from typing import Dict


class FundFlowAnalyzer:
    """资金流向分析器"""

    def fetch_fund_flow(self, symbol: str, market: str = "sz") -> Dict:
        """
        获取个股资金流向

        Args:
            symbol: 股票代码
            market: 市场 (sz/sh)

        Returns:
            资金流向数据 {'main_inflow': float, 'big_order_in': float, ...}
        """
        try:
            from infrastructure.models.quote_data import UnifiedStockQueryService
            service = UnifiedStockQueryService()
            flow_data = service.get_fund_flow(symbol)

            if flow_data and 'summary' in flow_data:
                summary = flow_data['summary']
                return {
                    "main_inflow": summary.get('main_force_in', 0) / 10000,  # 万元
                    "big_order_in": summary.get('big_order_in', 0) / 10000,
                    "medium_order_in": summary.get('medium_order_in', 0) / 10000,
                    "small_order_in": summary.get('small_order_in', 0) / 10000,
                }
        except Exception:
            pass

        return {"error": "获取失败"}

    def analyze_flow(self, flow_data: Dict) -> Dict:
        """
        分析资金流向

        Args:
            flow_data: 资金流向数据

        Returns:
            分析结果 {'direction': str, 'strength': str, 'summary': str}
        """
        if 'error' in flow_data:
            return {
                'direction': 'unknown',
                'strength': 'unknown',
                'summary': '数据获取失败'
            }

        main_inflow = flow_data.get('main_inflow', 0)
        big_order_in = flow_data.get('big_order_in', 0)

        # 判断方向
        if main_inflow > 0:
            direction = 'inflow'
        elif main_inflow < 0:
            direction = 'outflow'
        else:
            direction = 'balanced'

        # 判断强度
        abs_inflow = abs(main_inflow)
        if abs_inflow > 10000:  # 1 亿以上
            strength = 'strong'
        elif abs_inflow > 5000:  # 5000 万以上
            strength = 'moderate'
        elif abs_inflow > 1000:  # 1000 万以上
            strength = 'weak'
        else:
            strength = 'minimal'

        # 生成总结
        if direction == 'inflow':
            summary = f"主力净流入{main_inflow:.1f}万元，大单净流入{big_order_in:.1f}万元"
        elif direction == 'outflow':
            summary = f"主力净流出{abs(main_inflow):.1f}万元，大单净流出{abs(big_order_in):.1f}万元"
        else:
            summary = "资金流向平衡"

        return {
            'direction': direction,
            'strength': strength,
            'summary': summary
        }

    def generate_flow_report(self, flow_data: Dict) -> str:
        """
        生成资金流向报告

        Args:
            flow_data: 资金流向数据

        Returns:
            格式化报告字符串
        """
        analysis = self.analyze_flow(flow_data)

        report = "💰 资金流向分析\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        if 'error' in flow_data:
            report += "数据获取失败\n"
            return report

        report += f"方向：{analysis['direction']}\n"
        report += f"强度：{analysis['strength']}\n"
        report += f"\n{analysis['summary']}\n"

        if 'main_inflow' in flow_data:
            report += f"\n明细:\n"
            report += f"• 主力净流入：{flow_data.get('main_inflow', 0):.1f}万元\n"
            report += f"• 大单净流入：{flow_data.get('big_order_in', 0):.1f}万元\n"
            report += f"• 中单净流入：{flow_data.get('medium_order_in', 0):.1f}万元\n"
            report += f"• 小单净流入：{flow_data.get('small_order_in', 0):.1f}万元\n"

        return report
