#!/usr/bin/env python3
"""
monitor 命令 - 智能监控预警
监控持仓股和收藏股，生成 JSON 格式报告
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from domain.portfolio.services import MyStocks
from domain.portfolio.models.position import Position
from domain.portfolio.models.watchlist import Watchlist
from domain.alerting import RealtimeAlertEngine, AlertConfig
from domain.alerting.report_generator import (
    MonitorReportGenerator,
    PositionStock,
    WatchlistStock,
    StockAlert,
    RuleDetail
)
from infrastructure.unified_service import UnifiedStockQueryService
from config.settings import REPORT_CONFIG


def calculate_technical_indicators(stock_query: UnifiedStockQueryService, code: str) -> dict:
    """
    计算技术指标

    Args:
        stock_query: 股票查询服务
        code: 股票代码

    Returns:
        包含技术指标的字典
    """
    data = {
        'ma5': 0,
        'ma10': 0,
        'prev_ma5': 0,
        'prev_ma10': 0,
        'rsi': 0,
    }

    try:
        df = stock_query.get_historical_data(code, days=30)
        if df is not None and len(df) >= 20:
            closes = df['close'].tolist()

            # 计算 MA
            data['ma5'] = sum(closes[-5:]) / 5
            data['ma10'] = sum(closes[-10:]) / 10
            data['prev_ma5'] = sum(closes[-6:-1]) / 5
            data['prev_ma10'] = sum(closes[-11:-1]) / 5

            # 计算 RSI
            gains, losses = [], []
            for i in range(1, 14):
                change = closes[-i] - closes[-i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0
            data['rsi'] = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss else 100

    except Exception as e:
        pass

    return data


def check_stock_alerts(
    engine: RealtimeAlertEngine,
    code: str,
    name: str,
    price: float,
    change_pct: float,
    volume: float,
    cost: float = 0,
    indicators: dict = None
) -> list:
    """
    检查股票预警

    Args:
        engine: 预警引擎
        code: 股票代码
        name: 股票名称
        price: 当前价
        change_pct: 涨跌幅
        volume: 成交量
        cost: 成本价（持仓股）
        indicators: 技术指标

    Returns:
        预警列表
    """
    data = {
        'price': price,
        'change_pct': change_pct,
        'volume': volume,
        'ma5': indicators.get('ma5', 0) if indicators else 0,
        'ma10': indicators.get('ma10', 0) if indicators else 0,
        'prev_ma5': indicators.get('prev_ma5', 0) if indicators else 0,
        'prev_ma10': indicators.get('prev_ma10', 0) if indicators else 0,
        'rsi': indicators.get('rsi', 0) if indicators else 0,
    }

    config = AlertConfig(
        cost_pct_above=15.0,
        cost_pct_below=-12.0,
        change_pct_above=4.0,
        change_pct_below=-4.0,
        volume_surge=2.0,
        ma_monitor=True,
        rsi_monitor=True,
        gap_monitor=True,
        trailing_stop=True
    )

    alerts = engine.check(
        code=code,
        name=name,
        cost=cost,
        price=price,
        data=data,
        config=config
    )

    return alerts


def convert_alerts(stock: object, alerts: list) -> list:
    """
    转换预警格式

    Args:
        stock: 股票对象（Position 或 Watchlist）
        alerts: 原始预警列表

    Returns:
        StockAlert 列表
    """
    result = []
    for alert in alerts:
        result.append(StockAlert(
            stock_code=stock.stock_code,
            stock_name=stock.stock_name,
            alert_type=alert.alert_type,
            alert_level="高危" if alert.weight >= 3 else ("警告" if alert.weight >= 2 else "提示"),
            message=alert.message,
            weight=alert.weight
        ))
    return result


def generate_rule_details(
    code: str,
    name: str,
    price: float,
    change_pct: float,
    volume: float,
    cost: float = 0,
    indicators: dict = None,
    config: dict = None
) -> list:
    """
    生成预警规则详情

    Args:
        code: 股票代码
        name: 股票名称
        price: 当前价
        change_pct: 涨跌幅
        volume: 成交量
        cost: 成本价
        indicators: 技术指标
        config: 预警配置

    Returns:
        RuleDetail 列表
    """
    if config is None:
        config = {
            'cost_pct_above': 15.0,
            'cost_pct_below': -12.0,
            'change_pct_above': 4.0,
            'change_pct_below': -4.0,
            'volume_surge': 2.0,
        }

    rule_details = []

    # 计算当前值
    profit_pct = ((price - cost) / cost * 100) if cost > 0 else 0

    # 1. 成本百分比规则
    if cost > 0:
        rule_details.append(RuleDetail(
            rule_name="cost_above",
            rule_type="成本规则",
            triggered=profit_pct >= config.get('cost_pct_above', 15.0),
            details={'stock_code': code, 'stock_name': name},
            threshold=f">={config.get('cost_pct_above', 15.0)}%",
            current_value=f"{profit_pct:+.1f}%",
            message=f"盈利 {profit_pct:+.1f}%"
        ))
        rule_details.append(RuleDetail(
            rule_name="cost_below",
            rule_type="成本规则",
            triggered=profit_pct <= config.get('cost_pct_below', 12.0),
            details={'stock_code': code, 'stock_name': name},
            threshold=f"<={config.get('cost_pct_below', -12.0)}%",
            current_value=f"{profit_pct:+.1f}%",
            message=f"亏损 {profit_pct:+.1f}%"
        ))

    # 2. 价格涨跌幅规则
    rule_details.append(RuleDetail(
        rule_name="pct_up",
        rule_type="价格规则",
        triggered=change_pct >= config.get('change_pct_above', 4.0),
        details={'stock_code': code, 'stock_name': name},
        threshold=f">={config.get('change_pct_above', 4.0)}%",
        current_value=f"{change_pct:+.1f}%",
        message=f"日内大涨 {change_pct:+.1f}%"
    ))
    rule_details.append(RuleDetail(
        rule_name="pct_down",
        rule_type="价格规则",
        triggered=change_pct <= config.get('change_pct_below', -4.0),
        details={'stock_code': code, 'stock_name': name},
        threshold=f"<={config.get('change_pct_below', -4.0)}%",
        current_value=f"{change_pct:+.1f}%",
        message=f"日内大跌 {change_pct:+.1f}%"
    ))

    # 3. 成交量规则 (需要计算量比)
    if indicators:
        avg_volume = indicators.get('avg_volume', 0)
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            rule_details.append(RuleDetail(
                rule_name="volume_surge",
                rule_type="成交量规则",
                triggered=volume_ratio >= config.get('volume_surge', 2.0),
                details={'stock_code': code, 'stock_name': name},
                threshold=f">={config.get('volume_surge', 2.0)} 倍",
                current_value=f"{volume_ratio:.2f} 倍",
                message=f"放量 {volume_ratio:.2f} 倍"
            ))
            rule_details.append(RuleDetail(
                rule_name="volume_shrink",
                rule_type="成交量规则",
                triggered=volume_ratio <= 0.5,
                details={'stock_code': code, 'stock_name': name},
                threshold="<=0.5 倍",
                current_value=f"{volume_ratio:.2f} 倍",
                message=f"缩量 {volume_ratio:.2f} 倍"
            ))

    # 4. 技术指标规则
    if indicators:
        ma5 = indicators.get('ma5', 0)
        ma10 = indicators.get('ma10', 0)
        prev_ma5 = indicators.get('prev_ma5', 0)
        prev_ma10 = indicators.get('prev_ma10', 0)
        rsi = indicators.get('rsi', 0)

        # 金叉死叉
        golden_cross = ma5 > ma10 and prev_ma5 <= prev_ma10 if ma5 and ma10 else False
        death_cross = ma5 < ma10 and prev_ma5 >= prev_ma10 if ma5 and ma10 else False

        rule_details.append(RuleDetail(
            rule_name="ma_golden",
            rule_type="技术指标",
            triggered=golden_cross,
            details={'stock_code': code, 'stock_name': name},
            threshold="MA5 上穿 MA10",
            current_value=f"MA5:{ma5:.2f}, MA10:{ma10:.2f}",
            message=f"金叉信号 (MA5={ma5:.2f} > MA10={ma10:.2f})" if golden_cross else f"MA5={ma5:.2f}, MA10={ma10:.2f}"
        ))
        rule_details.append(RuleDetail(
            rule_name="ma_death",
            rule_type="技术指标",
            triggered=death_cross,
            details={'stock_code': code, 'stock_name': name},
            threshold="MA5 下穿 MA10",
            current_value=f"MA5:{ma5:.2f}, MA10:{ma10:.2f}",
            message=f"死叉信号 (MA5={ma5:.2f} < MA10={ma10:.2f})" if death_cross else f"MA5={ma5:.2f}, MA10={ma10:.2f}"
        ))

        # RSI 超买超卖
        rsi_overbought = rsi > 70 if rsi else False
        rsi_oversold = rsi < 30 if rsi else False

        rule_details.append(RuleDetail(
            rule_name="rsi_high",
            rule_type="技术指标",
            triggered=rsi_overbought,
            details={'stock_code': code, 'stock_name': name},
            threshold=">70",
            current_value=f"{rsi:.1f}" if rsi else "N/A",
            message=f"RSI 超买 (RSI={rsi:.1f})" if rsi_overbought else f"RSI={rsi:.1f}" if rsi else "RSI=N/A"
        ))
        rule_details.append(RuleDetail(
            rule_name="rsi_low",
            rule_type="技术指标",
            triggered=rsi_oversold,
            details={'stock_code': code, 'stock_name': name},
            threshold="<30",
            current_value=f"{rsi:.1f}" if rsi else "N/A",
            message=f"RSI 超卖 (RSI={rsi:.1f})" if rsi_oversold else f"RSI={rsi:.1f}" if rsi else "RSI=N/A"
        ))

    return rule_details


def format_monitor_json(
    position_stocks: list,
    watchlist_stocks: list,
    market_status: str,
    report_time: str
) -> str:
    """格式化监控报告为 JSON"""

    def convert_alert(alert: StockAlert) -> dict:
        return {
            "stock_code": alert.stock_code,
            "stock_name": alert.stock_name,
            "alert_type": alert.alert_type,
            "alert_level": alert.alert_level,
            "message": alert.message,
            "weight": alert.weight
        }

    def convert_rule_detail(rule: RuleDetail) -> dict:
        return {
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "triggered": rule.triggered,
            "threshold": rule.threshold,
            "current_value": rule.current_value,
            "message": rule.message
        }

    # 持仓股数据
    positions = []
    for p in position_stocks:
        positions.append({
            "stock_code": p.stock_code,
            "stock_name": p.stock_name,
            "quantity": p.quantity,
            "avg_cost": p.avg_cost,
            "current_price": p.current_price,
            "profit_loss": p.profit_loss,
            "profit_rate": p.profit_rate,
            "market_value": p.current_price * p.quantity,
            "alerts": [convert_alert(a) for a in p.alerts],
            "rule_details": [convert_rule_detail(r) for r in (p.rule_details or [])]
        })

    # 收藏股数据
    watchlist = []
    for w in watchlist_stocks:
        watchlist.append({
            "stock_code": w.stock_code,
            "stock_name": w.stock_name,
            "current_price": w.current_price,
            "change_pct": w.change_pct,
            "tags": w.tags,
            "target_price": w.target_price,
            "stop_loss": w.stop_loss,
            "alerts": [convert_alert(a) for a in w.alerts],
            "rule_details": [convert_rule_detail(r) for r in (w.rule_details or [])]
        })

    # 汇总统计
    total_alerts = sum(len(p.alerts) for p in positions) + sum(len(w.alerts) for w in watchlist)
    high_alerts = [a for a in (alerts for p in positions for alerts in p.alerts) if a.alert_level == "高危"]
    medium_alerts = [a for a in (alerts for p in positions for alerts in p.alerts) if a.alert_level == "警告"]
    low_alerts = [a for a in (alerts for p in positions for alerts in p.alerts) if a.alert_level == "提示"]

    output = {
        "report_time": report_time,
        "market_status": market_status,
        "summary": {
            "position_count": len(positions),
            "watchlist_count": len(watchlist),
            "total_alerts": total_alerts,
            "high_alerts": len(high_alerts),
            "medium_alerts": len(medium_alerts),
            "low_alerts": len(low_alerts)
        },
        "positions": positions,
        "watchlist": watchlist
    }

    return json.dumps(output, ensure_ascii=False, indent=2)


def cmd_monitor(args):
    """monitor 命令处理 - 智能监控预警"""

    # 初始化服务
    with MyStocks() as ms:
        stock_query = UnifiedStockQueryService()
        engine = RealtimeAlertEngine()

        # 使用配置文件中的模版
        template_file = REPORT_CONFIG.get("template_file")
        report_generator = MonitorReportGenerator(template_file=template_file)

        # 获取持仓股
        positions = ms.get_all_positions()

        # 获取收藏股
        watchlist = ms.get_watchlist()

        if not positions and not watchlist:
            if getattr(args, 'json', False):
                print(json.dumps({"error": "持仓股和收藏股均为空"}, ensure_ascii=False, indent=2))
            else:
                print("⚠️ 持仓股和收藏股均为空，无法监控")
            return

        # 监控持仓股
        position_stocks = []
        for p in positions:
            code = p.stock_code
            quote = stock_query.get_quote(code)

            if not quote or 'error' in quote:
                continue

            price = quote.get('price', p.current_price)
            if price <= 0:
                price = p.current_price

            change_pct = quote.get('change_pct', 0)
            volume = quote.get('volume', 0)

            # 更新当前价
            p.current_price = price
            # 负成本盈亏计算
            if p.avg_cost < 0:
                p.profit_loss = (abs(p.avg_cost) + price) * p.quantity
                p.profit_rate = None  # 负成本时盈亏率无意义
            else:
                p.profit_loss = (price - p.avg_cost) * p.quantity
                p.profit_rate = ((price - p.avg_cost) / p.avg_cost * 100) if p.avg_cost > 0 else 0

            # 计算技术指标
            indicators = calculate_technical_indicators(stock_query, code)

            # 检查预警
            alerts = check_stock_alerts(
                engine, code, p.stock_name, price, change_pct, volume,
                cost=p.avg_cost, indicators=indicators
            )

            # 生成规则详情
            rule_details = generate_rule_details(
                code, p.stock_name, price, change_pct, volume,
                cost=p.avg_cost, indicators=indicators
            )

            position_stocks.append(PositionStock(
                stock_code=p.stock_code,
                stock_name=p.stock_name,
                quantity=p.quantity,
                avg_cost=p.avg_cost,
                current_price=p.current_price,
                profit_loss=p.profit_loss,
                profit_rate=p.profit_rate,
                alerts=convert_alerts(p, alerts),
                rule_details=rule_details
            ))

        # 监控收藏股
        watchlist_stocks = []
        for wl in watchlist:
            code = wl.stock_code
            quote = stock_query.get_quote(code)

            if not quote or 'error' in quote:
                continue

            price = quote.get('price', 0)
            if price <= 0:
                continue

            change_pct = quote.get('change_pct', 0)
            volume = quote.get('volume', 0)

            # 计算技术指标
            indicators = calculate_technical_indicators(stock_query, code)

            # 检查预警
            alerts = check_stock_alerts(
                engine, code, wl.stock_name, price, change_pct, volume,
                cost=0, indicators=indicators
            )

            # 生成规则详情
            rule_details = generate_rule_details(
                code, wl.stock_name, price, change_pct, volume,
                cost=0, indicators=indicators
            )

            watchlist_stocks.append(WatchlistStock(
                stock_code=wl.stock_code,
                stock_name=wl.stock_name,
                current_price=price,
                change_pct=change_pct,
                tags=wl.tags,
                target_price=wl.target_price,
                stop_loss=wl.stop_loss,
                alerts=convert_alerts(wl, alerts),
                rule_details=rule_details
            ))

        # 确定市场状态
        market_status = "交易时间" if is_market_hours() else "盘后"
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # JSON 输出
        if getattr(args, 'json', False):
            json_output = format_monitor_json(
                position_stocks=position_stocks,
                watchlist_stocks=watchlist_stocks,
                market_status=market_status,
                report_time=report_time
            )

            if hasattr(args, 'output') and args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                print(f"✅ 报告已导出到：{output_path}")
            else:
                print(json_output)
            return

        # 文本输出
        print("🔍 开始监控...\n")
        print(f"📊 持仓股：{len(positions)} 只")
        print(f"🏷️ 收藏股：{len(watchlist)} 只")

        # 生成报告
        report = report_generator.generate_full_report(
            positions=position_stocks,
            watchlist=watchlist_stocks,
            market_status=market_status
        )

        # 输出报告
        print("\n" + "=" * 60)
        print("📊 监控报告")
        print("=" * 60)

        if hasattr(args, 'output') and args.output:
            # 导出到文件
            output_path = Path(args.output)
            report_generator.export_to_file(report, output_path)
            print(f"✅ 报告已导出到：{output_path}")
        else:
            # 控制台输出
            print(report)

        # 统计预警
        total_alerts = sum(len(p.alerts) for p in position_stocks) + sum(len(w.alerts) for w in watchlist_stocks)
        print(f"\n🔔 共触发 {total_alerts} 条预警")


def is_market_hours() -> bool:
    """判断是否是交易时间"""
    now = datetime.now()

    # 检查是否是周末
    if now.weekday() >= 5:
        return False

    # 检查时间
    hour = now.hour
    minute = now.minute

    # 上午 9:30-11:30
    if hour == 9 and minute >= 30:
        return True
    if hour == 10:
        return True
    if hour == 11 and minute < 30:
        return True

    # 下午 13:00-15:00
    if hour == 13:
        return True
    if hour == 14:
        return True
    if hour == 15 and minute == 0:
        return True

    return False


def setup_parser(parser: argparse.ArgumentParser):
    """设置命令行参数"""
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--no-position', action='store_true', help='不监控持仓股')
    parser.add_argument('--no-watchlist', action='store_true', help='不监控收藏股')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')


def main():
    """独立运行入口"""
    parser = argparse.ArgumentParser(description='股票监控预警')
    setup_parser(parser)
    args = parser.parse_args()
    cmd_monitor(args)


if __name__ == "__main__":
    main()
