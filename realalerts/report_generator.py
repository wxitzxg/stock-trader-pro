"""
Monitor Report Generator - 监控报告生成器
生成 Markdown 格式的持仓股和收藏股监控报告
支持模版配置和预警规则详情输出
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from config.settings import REPORT_CONFIG


@dataclass
class StockAlert:
    """预警信息"""
    stock_code: str
    stock_name: str
    alert_type: str  # 预警类型
    alert_level: str  # 预警级别：高危/警告/提示
    message: str  # 预警内容
    weight: int  # 权重
    rule_details: Optional[Dict] = None  # 预警规则详情


@dataclass
class RuleDetail:
    """预警规则详情"""
    rule_name: str  # 规则名称
    rule_type: str  # 规则类型
    triggered: bool  # 是否触发
    details: Dict  # 详情数据
    threshold: str  # 阈值
    current_value: str  # 当前值
    message: str  # 描述


@dataclass
class StockData:
    """股票数据"""
    stock_code: str
    stock_name: str
    current_price: float
    change_pct: float
    volume: float
    ma5: float = 0
    ma10: float = 0
    rsi: float = 0


@dataclass
class PositionStock:
    """持仓股"""
    stock_code: str
    stock_name: str
    quantity: int
    avg_cost: float
    current_price: float
    profit_loss: float
    profit_rate: float
    alerts: List[StockAlert]
    rule_details: List[RuleDetail] = None  # 预警规则详情


@dataclass
class WatchlistStock:
    """收藏股"""
    stock_code: str
    stock_name: str
    current_price: float
    change_pct: float
    tags: Optional[str]
    target_price: Optional[float]
    stop_loss: Optional[float]
    alerts: List[StockAlert]
    rule_details: List[RuleDetail] = None  # 预警规则详情


class MonitorReportGenerator:
    """监控报告生成器"""

    def __init__(self, template_file: str = None):
        self.report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.template_file = template_file or REPORT_CONFIG.get("template_file")
        self.config = REPORT_CONFIG

    def generate_full_report(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock],
        market_status: str = "交易时间"
    ) -> str:
        """
        生成完整监控报告

        Args:
            positions: 持仓股列表
            watchlist: 收藏股列表
            market_status: 市场状态

        Returns:
            Markdown 格式报告
        """
        # 如果使用自定义模版
        if self.template_file and Path(self.template_file).exists():
            return self._generate_from_template(positions, watchlist, market_status)

        # 使用内置模版
        return self._generate_builtin_report(positions, watchlist, market_status)

    def _generate_from_template(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock],
        market_status: str
    ) -> str:
        """从自定义模版生成报告"""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            template = f.read()

        # 准备数据
        data = self._prepare_template_data(positions, watchlist, market_status)

        # 简单的字符串替换
        report = template
        for key, value in data.items():
            report = report.replace(f"{{{{{key}}}}}", str(value))

        # 处理没有预警信息的情况
        if not self._collect_all_alerts(positions, watchlist):
            report = report.replace("{{alerts_section}}", "*暂无预警信息*")

        return report

    def _prepare_template_data(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock],
        market_status: str
    ) -> Dict:
        """准备模版数据"""
        all_alerts = self._collect_all_alerts(positions, watchlist)
        all_rule_details = self._collect_all_rule_details(positions, watchlist)

        # 汇总统计
        total_value = sum(p.current_price * p.quantity for p in positions) if positions else 0
        total_cost = sum(p.avg_cost * p.quantity for p in positions) if positions else 0
        total_profit = total_value - total_cost
        profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0

        # 预警数量统计
        position_alerts = sum(len(p.alerts) for p in positions)
        watchlist_alerts = sum(len(w.alerts) for w in watchlist)

        # 规则详情分组
        triggered_rules = [r for r in all_rule_details if r.triggered]
        normal_rules = [r for r in all_rule_details if not r.triggered][:10]

        return {
            "report_time": self.report_time,
            "market_status": market_status,
            "position_count": len(positions),
            "watchlist_count": len(watchlist),
            "total_value": f"¥{total_value:,.2f}",
            "total_cost": f"¥{total_cost:,.2f}",
            "total_profit": f"¥{total_profit:+,.2f}",
            "profit_rate": f"{profit_rate:+.1f}%",
            "position_alerts": position_alerts,
            "watchlist_alerts": watchlist_alerts,
            "positions_table": self._generate_positions_table(positions),
            "positions_detail": self._generate_positions_detail(positions),
            "watchlist_table": self._generate_watchlist_table(watchlist),
            "watchlist_detail": self._generate_watchlist_detail(watchlist),
            "alerts_section": self._generate_alert_summary(all_alerts),
            "triggered_rules_table": self._generate_triggered_rules_table(triggered_rules),
            "normal_rules_table": self._generate_normal_rules_table(normal_rules),
            "risk_tips": self._generate_risk_tips(positions, watchlist),
        }

    def _collect_all_rule_details(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock]
    ) -> List[RuleDetail]:
        """收集所有规则详情"""
        all_rule_details = []
        for p in positions:
            if p.rule_details:
                all_rule_details.extend(p.rule_details)
        for w in watchlist:
            if w.rule_details:
                all_rule_details.extend(w.rule_details)
        return all_rule_details

    def _generate_triggered_rules_table(self, triggered_rules: List[RuleDetail]) -> str:
        """生成已触发规则表格"""
        if not triggered_rules:
            return "*暂无已触发规则*"

        lines = []
        lines.append("| 股票 | 规则类型 | 规则名称 | 阈值 | 当前值 | 状态 |")
        lines.append("|------|----------|----------|------|--------|------|")

        for r in triggered_rules:
            stock_info = f"{r.details.get('stock_name', 'N/A')}({r.details.get('stock_code', 'N/A')})"
            lines.append(
                f"| {stock_info} | {r.rule_type} | {r.rule_name} | "
                f"{r.threshold} | {r.current_value} | 🔴 |"
            )

        return "\n".join(lines)

    def _generate_normal_rules_table(self, normal_rules: List[RuleDetail]) -> str:
        """生成正常状态规则表格"""
        if not normal_rules:
            return "*暂无正常状态规则*"

        lines = []
        lines.append("| 股票 | 规则类型 | 规则名称 | 阈值 | 当前值 | 状态 |")
        lines.append("|------|----------|----------|------|--------|------|")

        for r in normal_rules:
            stock_info = f"{r.details.get('stock_name', 'N/A')}({r.details.get('stock_code', 'N/A')})"
            lines.append(
                f"| {stock_info} | {r.rule_type} | {r.rule_name} | "
                f"{r.threshold} | {r.current_value} | ✅ |"
            )

        return "\n".join(lines)

    def _generate_positions_detail(self, positions: List[PositionStock]) -> str:
        """生成持仓股详情（用于模版）"""
        if not positions:
            return "*无持仓数据*"

        lines = []
        for p in positions:
            profit_color = "🟢" if p.profit_loss >= 0 else "🔴"
            alert_indicator = "⚠️" if p.alerts else "✅"

            lines.append(f"#### {p.stock_name} ({p.stock_code})")
            lines.append("")
            lines.append(f"- **持仓数量**: {p.quantity} 股")
            lines.append(f"- **成本价**: ¥{p.avg_cost:.2f}")
            lines.append(f"- **当前价**: ¥{p.current_price:.2f}")
            lines.append(f"- **市值**: ¥{p.current_price * p.quantity:,.2f}")
            lines.append(f"- **浮动盈亏**: {profit_color}¥{p.profit_loss:+,.2f} ({p.profit_rate:+.1f}%)")
            lines.append(f"- **状态**: {alert_indicator}")

            if p.alerts:
                lines.append(f"- **预警**:")
                for a in p.alerts:
                    lines.append(f"  - {a.alert_level}: {a.message}")

            if p.rule_details:
                lines.append(f"- **规则详情**:")
                for r in p.rule_details:
                    status = "🔴" if r.triggered else "✅"
                    lines.append(f"  - {status} {r.rule_name}: {r.message}")

            lines.append("")

        return "\n".join(lines)

    def _generate_watchlist_detail(self, watchlist: List[WatchlistStock]) -> str:
        """生成收藏股详情（用于模版）"""
        if not watchlist:
            return "*无收藏股数据*"

        lines = []
        for w in watchlist:
            change_color = "🟢" if w.change_pct >= 0 else "🔴"
            alert_indicator = "⚠️" if w.alerts else "✅"

            lines.append(f"#### {w.stock_name} ({w.stock_code})")
            lines.append("")

            if w.tags:
                lines.append(f"- **标签**: {w.tags}")

            lines.append(f"- **当前价**: ¥{w.current_price:.2f}")
            lines.append(f"- **涨跌幅**: {change_color}{w.change_pct:+.1f}%")
            lines.append(f"- **状态**: {alert_indicator}")

            if w.target_price:
                target_status = "✅ 已达到" if w.current_price >= w.target_price else "⏳ 未达到"
                lines.append(f"- **目标价**: ¥{w.target_price:.2f} {target_status}")

            if w.stop_loss:
                stop_status = "⚠️ 已跌破" if w.current_price <= w.stop_loss else "✅ 未跌破"
                lines.append(f"- **止损价**: ¥{w.stop_loss:.2f} {stop_status}")

            if w.alerts:
                lines.append(f"- **预警**:")
                for a in w.alerts:
                    lines.append(f"  - {a.alert_level}: {a.message}")

            if w.rule_details:
                lines.append(f"- **规则详情**:")
                for r in w.rule_details:
                    status = "🔴" if r.triggered else "✅"
                    lines.append(f"  - {status} {r.rule_name}: {r.message}")

            lines.append("")

        return "\n".join(lines)

    def _generate_builtin_report(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock],
        market_status: str
    ) -> str:
        """使用内置模版生成报告"""
        report = []

        # 标题
        report.append("# 📊 股票监控报告")
        report.append("")
        report.append(f"**生成时间**: {self.report_time}")
        report.append(f"**市场状态**: {market_status}")
        report.append("")

        # 汇总统计
        if self.config.get("include_summary", True):
            report.append("## 📈 汇总统计")
            report.append("")
            report.append(self._generate_summary(positions, watchlist))
            report.append("")

        # 预警汇总
        all_alerts = self._collect_all_alerts(positions, watchlist)
        if all_alerts and self.config.get("include_alerts", True):
            report.append("## 🚨 预警信息")
            report.append("")
            report.append(self._generate_alert_summary(all_alerts))
            report.append("")

        # 预警规则详情
        if self.config.get("include_rule_details", True):
            report.append("## 📋 预警规则详情")
            report.append("")
            report.append(self._generate_rule_details_section(positions, watchlist))
            report.append("")

        # 持仓股详情
        if positions and self.config.get("include_positions", True):
            report.append("## 💼 持仓股监控")
            report.append("")
            report.append(self._generate_positions_report(positions))
            report.append("")

        # 收藏股详情
        if watchlist and self.config.get("include_watchlist", True):
            report.append("## 🏷️ 收藏股监控")
            report.append("")
            report.append(self._generate_watchlist_report(watchlist))
            report.append("")

        # 风险提示
        if self.config.get("include_risk_tips", True):
            report.append("## ⚠️ 风险提示")
            report.append("")
            report.append(self._generate_risk_tips(positions, watchlist))
            report.append("")

        # 页脚
        report.append("---")
        report.append("*本报告由 Technical Indicators Pro 自动生成*")

        return "\n".join(report)

    def _generate_summary(self, positions: List[PositionStock], watchlist: List[WatchlistStock]) -> str:
        """生成汇总统计"""
        lines = []

        # 持仓股统计
        if positions:
            total_value = sum(p.current_price * p.quantity for p in positions)
            total_cost = sum(p.avg_cost * p.quantity for p in positions)
            total_profit = total_value - total_cost
            profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
            alert_count = sum(len(p.alerts) for p in positions)

            lines.append("### 持仓股")
            lines.append(f"| 项目 | 数值 |")
            lines.append(f"|------|------|")
            lines.append(f"| 持仓数量 | {len(positions)} 只 |")
            lines.append(f"| 总市值 | ¥{total_value:,.2f} |")
            lines.append(f"| 总成本 | ¥{total_cost:,.2f} |")
            lines.append(f"| 浮动盈亏 | ¥{total_profit:+,.2f} ({profit_rate:+.1f}%) |")
            lines.append(f"| 预警数量 | {alert_count} 条 |")
            lines.append("")

        # 收藏股统计
        if watchlist:
            up_count = sum(1 for w in watchlist if w.change_pct > 0)
            down_count = sum(1 for w in watchlist if w.change_pct < 0)
            alert_count = sum(len(w.alerts) for w in watchlist)

            lines.append("### 收藏股")
            lines.append(f"| 项目 | 数值 |")
            lines.append(f"|------|------|")
            lines.append(f"| 收藏数量 | {len(watchlist)} 只 |")
            lines.append(f"| 上涨 | {up_count} 只 |")
            lines.append(f"| 下跌 | {down_count} 只 |")
            lines.append(f"| 预警数量 | {alert_count} 条 |")

        return "\n".join(lines)

    def _collect_all_alerts(self, positions: List[PositionStock], watchlist: List[WatchlistStock]) -> List[StockAlert]:
        """收集所有预警"""
        alerts = []
        for p in positions:
            alerts.extend(p.alerts)
        for w in watchlist:
            alerts.extend(w.alerts)
        # 按权重排序
        alerts.sort(key=lambda x: x.weight, reverse=True)
        return alerts

    def _generate_alert_summary(self, alerts: List[StockAlert]) -> str:
        """生成预警汇总"""
        lines = []

        # 按级别分组
        high_alerts = [a for a in alerts if a.alert_level == "高危"]
        medium_alerts = [a for a in alerts if a.alert_level == "警告"]
        low_alerts = [a for a in alerts if a.alert_level == "提示"]

        if high_alerts:
            lines.append("### 🔴 高危预警")
            for a in high_alerts:
                lines.append(f"- **{a.stock_name}({a.stock_code})**: {a.message}")
            lines.append("")

        if medium_alerts:
            lines.append("### 🟡 警告")
            for a in medium_alerts:
                lines.append(f"- **{a.stock_name}({a.stock_code})**: {a.message}")
            lines.append("")

        if low_alerts:
            lines.append("### 🔵 提示")
            for a in low_alerts:
                lines.append(f"- **{a.stock_name}({a.stock_code})**: {a.message}")
            lines.append("")

        return "\n".join(lines)

    def _generate_rule_details_section(
        self,
        positions: List[PositionStock],
        watchlist: List[WatchlistStock]
    ) -> str:
        """生成预警规则详情部分"""
        lines = []

        # 汇总所有规则详情
        all_rule_details = []
        for p in positions:
            if p.rule_details:
                all_rule_details.extend(p.rule_details)
        for w in watchlist:
            if w.rule_details:
                all_rule_details.extend(w.rule_details)

        if not all_rule_details:
            lines.append("*暂无预警规则详情数据*")
            return "\n".join(lines)

        # 按规则类型分组
        triggered_rules = [r for r in all_rule_details if r.triggered]
        normal_rules = [r for r in all_rule_details if not r.triggered]

        # 已触发的规则
        if triggered_rules:
            lines.append("### 已触发规则")
            lines.append("")
            lines.append("| 股票 | 规则类型 | 规则名称 | 阈值 | 当前值 | 状态 |")
            lines.append("|------|----------|----------|------|--------|------|")

            for r in triggered_rules:
                lines.append(
                    f"| {r.details.get('stock_code', 'N/A')} | {r.rule_type} | {r.rule_name} | "
                    f"{r.threshold} | {r.current_value} | 🔴 |"
                )
            lines.append("")

        # 未触发的规则（正常状态）
        if normal_rules:
            lines.append("### 正常状态规则")
            lines.append("")
            lines.append("| 股票 | 规则类型 | 规则名称 | 阈值 | 当前值 | 状态 |")
            lines.append("|------|----------|----------|------|--------|------|")

            for r in normal_rules[:10]:  # 限制显示数量
                lines.append(
                    f"| {r.details.get('stock_code', 'N/A')} | {r.rule_type} | {r.rule_name} | "
                    f"{r.threshold} | {r.current_value} | ✅ |"
                )
            lines.append("")

        # 规则详情说明
        lines.append("### 规则说明")
        lines.append("")
        lines.append("#### 成本百分比规则")
        lines.append("- **cost_above**: 盈利超过设定百分比（默认 15%）")
        lines.append("- **cost_below**: 亏损超过设定百分比（默认 12%）")
        lines.append("")
        lines.append("#### 价格涨跌幅规则")
        lines.append("- **pct_up**: 日内大涨（默认≥4%）")
        lines.append("- **pct_down**: 日内大跌（默认≤-4%）")
        lines.append("- **price_above**: 价格突破设定值")
        lines.append("- **price_below**: 价格跌破设定值")
        lines.append("")
        lines.append("#### 成交量规则")
        lines.append("- **volume_surge**: 放量（当前量/5 日均量≥2）")
        lines.append("- **volume_shrink**: 缩量（当前量/5 日均量≤0.5）")
        lines.append("")
        lines.append("#### 技术指标规则")
        lines.append("- **ma_golden**: MA5 上穿 MA10（金叉）")
        lines.append("- **ma_death**: MA5 下穿 MA10（死叉）")
        lines.append("- **rsi_high**: RSI 超买（>70）")
        lines.append("- **rsi_low**: RSI 超卖（<30）")
        lines.append("- **gap_up**: 向上跳空（>1%）")
        lines.append("- **gap_down**: 向下跳空（>1%）")

        return "\n".join(lines)

    def _generate_positions_report(self, positions: List[PositionStock]) -> str:
        """生成持仓股报告"""
        lines = []

        # 表格头部
        lines.append("| 代码 | 名称 | 持仓 | 成本价 | 当前价 | 盈亏 | 盈亏率 | 预警 |")
        lines.append("|------|------|------|--------|--------|------|--------|------|")

        for p in positions:
            # 颜色标记
            profit_color = "🟢" if p.profit_loss >= 0 else "🔴"
            alert_indicator = "⚠️" if p.alerts else "✅"

            lines.append(
                f"| {p.stock_code} | {p.stock_name} | {p.quantity} | "
                f"¥{p.avg_cost:.2f} | ¥{p.current_price:.2f} | "
                f"{profit_color}¥{p.profit_loss:+,.0f} | {p.profit_rate:+.1f}% | "
                f"{alert_indicator} |"
            )

        # 持仓详情
        lines.append("")
        lines.append("### 持仓详情")
        lines.append("")

        for p in positions:
            lines.append(f"#### {p.stock_name} ({p.stock_code})")
            lines.append("")
            lines.append(f"- **持仓数量**: {p.quantity} 股")
            lines.append(f"- **成本价**: ¥{p.avg_cost:.2f}")
            lines.append(f"- **当前价**: ¥{p.current_price:.2f}")
            lines.append(f"- **市值**: ¥{p.current_price * p.quantity:,.2f}")
            lines.append(f"- **浮动盈亏**: ¥{p.profit_loss:+,.2f} ({p.profit_rate:+.1f}%)")

            if p.alerts:
                lines.append(f"- **预警**:")
                for a in p.alerts:
                    lines.append(f"  - {a.alert_level}: {a.message}")
            else:
                lines.append(f"- **状态**: 正常")

            # 显示规则详情
            if p.rule_details:
                lines.append(f"- **规则详情**:")
                for r in p.rule_details:
                    status = "🔴" if r.triggered else "✅"
                    lines.append(f"  - {status} {r.rule_name}: {r.message}")

            lines.append("")

        return "\n".join(lines)

    def _generate_positions_table(self, positions: List[PositionStock]) -> str:
        """生成持仓股表格（用于模版）"""
        if not positions:
            return "*无持仓数据*"

        lines = []
        lines.append("| 代码 | 名称 | 持仓 | 成本价 | 当前价 | 盈亏 | 盈亏率 |")
        lines.append("|------|------|------|--------|--------|------|--------|")

        for p in positions:
            profit_color = "🟢" if p.profit_loss >= 0 else "🔴"
            lines.append(
                f"| {p.stock_code} | {p.stock_name} | {p.quantity} | "
                f"¥{p.avg_cost:.2f} | ¥{p.current_price:.2f} | "
                f"{profit_color}¥{p.profit_loss:+,.0f} | {p.profit_rate:+.1f}% |"
            )

        return "\n".join(lines)

    def _generate_watchlist_report(self, watchlist: List[WatchlistStock]) -> str:
        """生成收藏股报告"""
        lines = []

        # 表格头部
        lines.append("| 代码 | 名称 | 当前价 | 涨跌幅 | 目标价 | 止损价 | 预警 |")
        lines.append("|------|------|--------|--------|--------|--------|------|")

        for w in watchlist:
            # 颜色标记
            change_color = "🟢" if w.change_pct >= 0 else "🔴"
            alert_indicator = "⚠️" if w.alerts else "✅"
            target_indicator = "🎯" if w.target_price and w.current_price >= w.target_price else ""

            target_price_str = f"¥{w.target_price:.2f}" if w.target_price else "-"
            stop_loss_str = f"¥{w.stop_loss:.2f}" if w.stop_loss else "-"

            lines.append(
                f"| {w.stock_code} | {w.stock_name} | ¥{w.current_price:.2f} | "
                f"{change_color}{w.change_pct:+.1f}% | {target_price_str}{target_indicator} | "
                f"{stop_loss_str} | {alert_indicator} |"
            )

        # 收藏股详情
        lines.append("")
        lines.append("### 收藏股详情")
        lines.append("")

        for w in watchlist:
            lines.append(f"#### {w.stock_name} ({w.stock_code})")
            lines.append("")

            if w.tags:
                lines.append(f"- **标签**: {w.tags}")

            lines.append(f"- **当前价**: ¥{w.current_price:.2f}")
            lines.append(f"- **涨跌幅**: {change_color}{w.change_pct:+.1f}%")

            if w.target_price:
                target_status = "✅ 已达到" if w.current_price >= w.target_price else "⏳ 未达到"
                lines.append(f"- **目标价**: ¥{w.target_price:.2f} {target_status}")

            if w.stop_loss:
                stop_status = "⚠️ 已跌破" if w.current_price <= w.stop_loss else "✅ 未跌破"
                lines.append(f"- **止损价**: ¥{w.stop_loss:.2f} {stop_status}")

            if w.alerts:
                lines.append(f"- **预警**:")
                for a in w.alerts:
                    lines.append(f"  - {a.alert_level}: {a.message}")

            # 显示规则详情
            if w.rule_details:
                lines.append(f"- **规则详情**:")
                for r in w.rule_details:
                    status = "🔴" if r.triggered else "✅"
                    lines.append(f"  - {status} {r.rule_name}: {r.message}")

            lines.append("")

        return "\n".join(lines)

    def _generate_watchlist_table(self, watchlist: List[WatchlistStock]) -> str:
        """生成收藏股表格（用于模版）"""
        if not watchlist:
            return "*无收藏股数据*"

        lines = []
        lines.append("| 代码 | 名称 | 当前价 | 涨跌幅 | 目标价 | 止损价 |")
        lines.append("|------|------|--------|--------|--------|--------|")

        for w in watchlist:
            change_color = "🟢" if w.change_pct >= 0 else "🔴"
            target_price_str = f"¥{w.target_price:.2f}" if w.target_price else "-"
            stop_loss_str = f"¥{w.stop_loss:.2f}" if w.stop_loss else "-"

            lines.append(
                f"| {w.stock_code} | {w.stock_name} | ¥{w.current_price:.2f} | "
                f"{change_color}{w.change_pct:+.1f}% | {target_price_str} | {stop_loss_str} |"
            )

        return "\n".join(lines)

    def _generate_risk_tips(self, positions: List[PositionStock], watchlist: List[WatchlistStock]) -> str:
        """生成风险提示"""
        tips = []

        # 检查持仓集中度
        if positions:
            total_value = sum(p.current_price * p.quantity for p in positions)
            if total_value > 0:
                max_position = max((p.current_price * p.quantity / total_value) for p in positions)
                if max_position > 0.3:
                    tips.append(f"- ⚠️ 持仓集中度较高，最大持仓占比 {max_position:.1%}")

        # 检查亏损股票
        loss_positions = [p for p in positions if p.profit_rate < -10]
        if loss_positions:
            stocks = [f"{p.stock_name}({p.profit_rate:.1f}%)" for p in loss_positions]
            tips.append(f"- 🔴 以下股票亏损超过 10%: {', '.join(stocks)}")

        # 检查大涨股票
        surge_stocks = [w for w in watchlist if w.change_pct > 5]
        if surge_stocks:
            stocks = [f"{w.stock_name}({w.change_pct:+.1f}%)" for w in surge_stocks]
            tips.append(f"- 🟢 以下股票大涨超过 5%: {', '.join(stocks)}")

        # 检查跌破止损
        stop_loss_broken = [w for w in watchlist if w.stop_loss and w.current_price <= w.stop_loss]
        if stop_loss_broken:
            stocks = [f"{w.stock_name}" for w in stop_loss_broken]
            tips.append(f"- ⚠️ 以下股票跌破止损价：{', '.join(stocks)}")

        if not tips:
            tips.append("- ✅ 暂无重大风险")

        return "\n".join(tips)

    def export_to_file(self, report: str, file_path: str):
        """
        导出报告到文件

        Args:
            report: 报告内容
            file_path: 文件路径
        """
        # 确保目录存在
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)


# 导出函数
__all__ = [
    'MonitorReportGenerator',
    'StockAlert',
    'RuleDetail',
    'PositionStock',
    'WatchlistStock',
    'StockData',
]
