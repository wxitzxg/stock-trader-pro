#!/usr/bin/env python3
"""
analyze 命令 - 股票技术分析
"""

import json
from datetime import datetime
from typing import Optional

from infrastructure.unified_service import UnifiedStockQueryService
from domain.analysis import (
    UltimateEngine,
    SignalGenerator,
    VCPBreakoutStrategy,
    TDGoldenPitStrategy,
    TopDivergenceStrategy,
)


def analyze_stock(symbol: str, days: int = 250, full: bool = False, strategy: str = None) -> dict:
    """
    分析单个股票

    Args:
        symbol: 股票代码
        days: 历史数据天数
        full: 是否完整分析 (包括所有策略)
        strategy: 指定策略 (vcp, td, divergence)

    Returns:
        分析结果字典
    """
    print(f"分析 {symbol}...")

    # 获取历史数据
    service = UnifiedStockQueryService()
    df = service.get_historical_data(symbol)

    if df is None or df.empty:
        return {"error": f"无法获取 {symbol} 的历史数据"}

    print(f"获取到 {len(df)} 条数据")

    # 五维共振分析
    engine = UltimateEngine(df, symbol=symbol)
    engine_result = engine.evaluate_all()

    # 信号生成
    signal_gen = SignalGenerator(df)
    full_analysis = signal_gen.get_full_analysis()
    full_analysis['symbol'] = symbol

    # 策略分析
    strategies_result = {}

    if full or strategy == 'vcp' or strategy is None:
        vcp_strategy = VCPBreakoutStrategy(df, symbol=symbol)
        vcp_signal = vcp_strategy.generate_signal()
        strategies_result['vcp_breakout'] = vcp_signal

    if full or strategy == 'td' or strategy is None:
        td_strategy = TDGoldenPitStrategy(df, symbol=symbol)
        td_signal = td_strategy.generate_signal()
        strategies_result['td_golden_pit'] = td_signal

    if full or strategy == 'divergence' or strategy is None:
        top_strategy = TopDivergenceStrategy(df, symbol=symbol)
        top_signal = top_strategy.generate_signal()
        strategies_result['top_divergence'] = top_signal

    return {
        'symbol': symbol,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'current_price': df['close'].iloc[-1],
        'engine_result': engine_result,
        'signal_analysis': full_analysis,
        'strategies': strategies_result,
        'report': engine.generate_report()
    }


def format_analysis_report(result: dict) -> str:
    """格式化分析报告"""
    if 'error' in result:
        return f"❌ 分析失败：{result['error']}"

    report = f"""
═══════════════════════════════════════════════════════
  {result['symbol']} 技术分析报告
═══════════════════════════════════════════════════════
分析日期：{result['analysis_date']}
当前价格：¥{result['current_price']:.2f}

{result['report']}

───────────────────────────────────────────────────────
【策略信号】
"""

    # VCP 策略
    vcp = result['strategies'].get('vcp_breakout')
    if vcp:
        report += f"\n🔹 VCP 爆发突击：{'✅ 买入信号' if vcp else '⏸️ 无信号'}\n"
        if vcp:
            report += f"   入场价：¥{vcp['entry_price']:.2f}\n"
            report += f"   止损价：¥{vcp['stop_loss']:.2f}\n"
            report += f"   目标价：¥{vcp['target_price']:.2f}\n"
            report += f"   置信度：{vcp['confidence']:.0f}%\n"

    # 九转策略
    td = result['strategies'].get('td_golden_pit')
    if td:
        report += f"\n🔹 九转黄金坑：{'✅ 买入信号' if td else '⏸️ 无信号'}\n"
        if td:
            report += f"   入场价：¥{td['entry_price']:.2f}\n"
            report += f"   止损价：¥{td['stop_loss']:.2f}\n"
            report += f"   目标价：¥{td['target_price']:.2f}\n"
            report += f"   置信度：{td['confidence']:.0f}%\n"

    # 顶部背离策略
    top = result['strategies'].get('top_divergence')
    if top:
        report += f"\n🔹 顶部背离止盈：{'⚠️ 卖出信号' if top else '⏸️ 无信号'}\n"
        if top:
            report += f"   建议：{top['suggested_action']}\n"
            report += f"   紧急度：{top['urgency']}\n"

    # 最终推荐
    signal_analysis = result.get('signal_analysis', {})
    recommendation = signal_analysis.get('recommendation', 'N/A')
    report += f"\n───────────────────────────────────────────────────────"
    report += f"\n【最终推荐】{recommendation}"
    report += f"\n═══════════════════════════════════════════════════════\n"

    return report


def cmd_analyze(args):
    """analyze 命令处理"""
    from domain.portfolio.repositories.database import get_db
    from domain.portfolio.services.watchlist_service import WatchlistService

    if args.watchlist:
        # 分析收藏股列表
        return analyze_watchlist(args)

    # 分析单个股票
    result = analyze_stock(
        symbol=args.symbol,
        days=args.days,
        full=args.full,
        strategy=args.strategy
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_analysis_report(result))


def analyze_watchlist(args):
    """分析收藏股列表"""
    from domain.portfolio.repositories.database import get_db
    from domain.portfolio.services.watchlist_service import WatchlistService

    db = get_db()
    db.init_db()
    session = db.get_session()

    watchlist_mgr = WatchlistService(session)
    watchlist_stocks = watchlist_mgr.get_all()

    if not watchlist_stocks:
        print("收藏股列表为空")
        return

    print(f"分析收藏股列表 ({len(watchlist_stocks)} 只股票)...\n")

    for wl in watchlist_stocks:
        try:
            result = analyze_stock(wl.stock_code, days=args.days, full=args.full)
            print(format_analysis_report(result))
        except Exception as e:
            print(f"分析 {wl.stock_code} 失败：{e}")

    session.close()
