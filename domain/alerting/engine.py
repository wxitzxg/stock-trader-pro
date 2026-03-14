"""
实时预警引擎 (Realtime Alert Engine)
整合七大预警规则、仓位管理、动态止损、智能分析
"""

from typing import Dict, List, Optional
from domain.alerting.rules.cost_alert import CostRule
from domain.alerting.rules.price_alert import PriceRule
from domain.alerting.rules.volume_alert import VolumeRule
from domain.alerting.rules.technical_alert import TechnicalRule
from domain.alerting.rules.trailing_stop import TrailingStopRule
from domain.portfolio.services.position_monitor import PositionMonitor
from domain.portfolio.services.stop_loss import StopLoss
from domain.portfolio.services.sentiment import SentimentAnalyzer
from domain.portfolio.services.fund_flow import FundFlowAnalyzer


class RealtimeAlertEngine:
    """实时预警引擎"""

    def __init__(self, total_capital: float = 1000000):
        """
        初始化预警引擎

        Args:
            total_capital: 总资金 (默认 100 万)
        """
        # 预警规则
        self.cost_rule = CostRule()
        self.price_rule = PriceRule()
        self.volume_rule = VolumeRule()
        self.technical_rule = TechnicalRule()
        self.trailing_stop_rule = TrailingStopRule()

        # 仓位管理
        self.position_monitor = PositionMonitor(total_capital)
        self.stop_loss = StopLoss()

        # 智能分析
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fund_flow_analyzer = FundFlowAnalyzer()

    def check(
        self,
        code: str,
        name: str,
        cost: float,
        price: float,
        data: Dict,
        config: Dict
    ) -> List[Dict]:
        """
        检查所有预警规则

        Args:
            code: 股票代码
            name: 股票名称
            cost: 持仓成本
            price: 当前价格
            data: 行情数据 (high, volume, ma5, ma10, prev_ma5, prev_ma10, rsi, open, etc.)
            config: 预警配置

        Returns:
            预警结果列表
        """
        all_alerts = []

        # 1. 成本百分比预警
        cost_alerts = self.cost_rule.check(code, cost, price, config)
        all_alerts.extend(cost_alerts)

        # 2. 价格涨跌幅预警
        change_pct = data.get('change_pct', 0)
        price_alerts = self.price_rule.check(code, price, change_pct, config)
        all_alerts.extend(price_alerts)

        # 3. 成交量异动预警
        volume_alerts = self.volume_rule.check(code, data, config)
        all_alerts.extend(volume_alerts)

        # 4. 技术指标预警 (MA, RSI, Gap)
        technical_alerts = self.technical_rule.check(code, data, config)
        all_alerts.extend(technical_alerts)

        # 5. 动态止盈止损
        trailing_alerts = self.trailing_stop_rule.check(code, cost, price, data, config)
        all_alerts.extend(trailing_alerts)

        # 按权重排序 (权重高的优先)
        all_alerts.sort(key=lambda x: x.weight, reverse=True)

        return all_alerts

    def get_position_suggestion(
        self,
        signal_strength: str,
        confidence_score: float,
        win_rate: float = None,
        profit_loss_ratio: float = None
    ) -> Dict:
        """
        获取仓位建议

        Args:
            signal_strength: 信号强度 (STRONG_BUY, BUY, HOLD)
            confidence_score: 置信度分数 (0-100)
            win_rate: 胜率 (可选)
            profit_loss_ratio: 盈亏比 (可选)

        Returns:
            仓位建议字典
        """
        return self.position_monitor.calculate_position_size(
            signal_strength=signal_strength,
            confidence_score=confidence_score,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio
        )

    def check_concentration_risk(self, current_positions: Dict[str, float]) -> Dict:
        """
        检查持仓集中度风险

        Args:
            current_positions: 当前持仓 {stock_code: weight}

        Returns:
            风险分析结果
        """
        return self.position_monitor.check_concentration_risk(current_positions)

    def set_stop_loss(
        self,
        stock_code: str,
        stop_loss_price: float,
        stop_loss_type: str = 'fixed'
    ):
        """
        设置止损位

        Args:
            stock_code: 股票代码
            stop_loss_price: 止损价
            stop_loss_type: 止损类型 (fixed, trailing, vcp, td)
        """
        self.stop_loss.set_stop_loss(stock_code, stop_loss_price, stop_loss_type)

    def check_stop_loss_triggered(
        self,
        stock_code: str,
        current_price: float
    ) -> Dict:
        """
        检查是否触发止损

        Args:
            stock_code: 股票代码
            current_price: 当前价

        Returns:
            止损触发检查结果
        """
        return self.stop_loss.check_stop_loss_triggered(stock_code, current_price)

    def generate_analysis_report(
        self,
        code: str,
        name: str,
        price: float,
        change_pct: float,
        alerts: List
    ) -> str:
        """
        生成智能分析报告

        Args:
            code: 股票代码
            name: 股票名称
            price: 当前价格
            change_pct: 涨跌幅
            alerts: 预警列表

        Returns:
            分析报告字符串
        """
        # 获取新闻和情感分析
        news_list = self.sentiment_analyzer.fetch_news(code, name)
        sentiment = self.sentiment_analyzer.analyze_sentiment(news_list)

        # 获取资金流向
        fund_flow = self.fund_flow_analyzer.fetch_fund_flow(code)

        # 构建报告
        report = f"📊 {name} ({code}) 深度分析\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        report += f"💰 价格异动:\n"
        report += f"• 当前：¥{price:.2f} ({change_pct:+.2f}%)\n"
        report += f"• 触发：{', '.join([a.alert_type for a in alerts])}\n\n"

        report += f"📰 舆情分析 ({sentiment.get('overall', '未知')}):\n"
        report += f"• 最近新闻：{len(news_list)} 条\n"
        report += f"• 正面：{sentiment.get('positive', 0)} | 负面：{sentiment.get('negative', 0)}\n"

        # 添加最新新闻
        if news_list:
            report += "\n最新动态:\n"
            for n in news_list[:2]:
                title = n.get('title', '无标题')
                report += f"• {title[:40]}...\n"

        # 添加资金流向
        if 'error' not in fund_flow:
            report += f"\n💰 资金流向:\n"
            report += f"• 主力净流入：{fund_flow.get('main_inflow', 'N/A')}万元\n"
            report += f"• 大单净流入：{fund_flow.get('big_order_in', 'N/A')}万元\n"

        # 智能建议
        suggestion = self.sentiment_analyzer.generate_suggestion(sentiment, alerts)
        report += f"\n💡 智能建议:\n{suggestion}"

        return report

    def format_alerts(
        self,
        code: str,
        name: str,
        price: float,
        change_pct: float,
        cost: float,
        alerts: List
    ) -> str:
        """
        格式化预警信息

        Args:
            code: 股票代码
            name: 股票名称
            price: 当前价格
            change_pct: 涨跌幅
            cost: 持仓成本
            alerts: 预警列表

        Returns:
            格式化预警字符串
        """
        if not alerts:
            return ""

        # 确定预警级别
        max_weight = max(a.weight for a in alerts) if alerts else 0
        if max_weight >= 3:
            level = "🔴 高危"
        elif max_weight >= 2:
            level = "🟡 警告"
        else:
            level = "🔵 提示"

        # 计算盈亏
        profit_pct = ((price - cost) / cost * 100) if cost > 0 else 0

        # 构建预警信息
        msg = f"{level} {name} ({code})\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"当前价：¥{price:.2f} ({change_pct:+.2f}%)\n"
        msg += f"持仓成本：¥{cost:.2f} ({profit_pct:+.2f}%)\n\n"

        for alert in alerts:
            msg += f"{alert.message}\n"

        return msg
