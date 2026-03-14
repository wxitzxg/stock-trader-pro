#!/usr/bin/env python3
"""
alert 命令 - 执行一次预警检查
使用新的 realalerts 模块
"""

from mystocks.storage.database import get_db
from mystocks.services import WatchlistService
from realalerts import RealtimeAlertEngine, AlertConfig
from stockquery import UnifiedStockQueryService


def cmd_alert(args):
    """alert 命令处理 - 执行一次预警检查"""
    db = get_db()
    db.init_db()
    session = db.get_session()

    watchlist_svc = WatchlistService(session)
    watchlist_stocks = watchlist_svc.get_all()

    if not watchlist_stocks:
        print("收藏股列表为空")
        return

    print(f"智能监控 {len(watchlist_stocks)} 只收藏股...\n")

    # 使用新的 realalerts 引擎
    engine = RealtimeAlertEngine()
    stock_query = UnifiedStockQueryService()

    # 将收藏股转换为监控配置
    alerts_triggered = []
    for wl in watchlist_stocks:
        code = wl.stock_code
        name = wl.stock_name

        # 获取实时行情
        quote = stock_query.get_quote(code)
        if not quote or 'error' in quote:
            continue

        price = quote.get('price', 0)
        if price <= 0:
            continue

        # 获取历史数据计算技术指标
        try:
            df = stock_query.get_historical_data(code, days=30)
            if df is not None and len(df) >= 20:
                closes = df['close'].tolist()
                ma5 = sum(closes[-5:]) / 5
                ma10 = sum(closes[-10:]) / 10
                prev_ma5 = sum(closes[-6:-1]) / 5
                prev_ma10 = sum(closes[-11:-1]) / 10

                # 计算 RSI
                gains, losses = [], []
                for i in range(1, 15):
                    change = closes[-i] - closes[-i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                avg_gain = sum(gains) / 14
                avg_loss = sum(losses) / 14
                rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss else 100
            else:
                ma5 = ma10 = prev_ma5 = prev_ma10 = rsi = 0
        except Exception:
            ma5 = ma10 = prev_ma5 = prev_ma10 = rsi = 0

        # 构建数据字典
        data = {
            'price': price,
            'change_pct': quote.get('change_pct', 0),
            'volume': quote.get('volume', 0),
            'open': quote.get('open', 0),
            'high': quote.get('high', 0),
            'ma5': ma5,
            'ma10': ma10,
            'prev_ma5': prev_ma5,
            'prev_ma10': prev_ma10,
            'rsi': rsi,
        }

        # 检查预警
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
            cost=0,  # 可以从持仓获取
            price=price,
            data=data,
            config=config
        )

        if alerts:
            msg = engine.format_alerts(
                code=code,
                name=name,
                price=price,
                change_pct=data['change_pct'],
                cost=0,
                alerts=alerts
            )
            alerts_triggered.append(msg)

    if alerts_triggered:
        print("=" * 60)
        print(f"触发 {len(alerts_triggered)} 条预警:")
        print("=" * 60)
        for alert in alerts_triggered:
            print(alert)
            print("-" * 40)
    else:
        print("暂无预警")

    session.close()
