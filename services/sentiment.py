"""
舆情分析模块 (Sentiment Analysis)
获取个股新闻并进行情感分析
"""

import requests
from typing import List, Dict


class SentimentAnalyzer:
    """股票舆情分析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        # 情感词库
        self.positive_words = [
            '利好', '增长', '突破', '买入', '增持', '涨停',
            '超预期', '业绩大增', '创新高', '放量上涨'
        ]
        self.negative_words = [
            '利空', '减持', '下跌', '卖出', '亏损', '暴雷',
            '跌停', '不及预期', '创新低', '缩量下跌'
        ]

    def fetch_news(self, symbol: str, name: str, limit: int = 5) -> List[Dict]:
        """
        获取个股新闻 (东方财富)

        Args:
            symbol: 股票代码
            name: 股票名称
            limit: 获取数量

        Returns:
            新闻列表 [{'title': xxx, 'url': xxx, 'time': xxx}, ...]
        """
        url = f"https://searchapi.eastmoney.com/api/suggest/get"
        params = {
            "input": name,
            "type": 14,
            "count": limit
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            news_list = []
            for item in data.get("QuotationCodeTable", {}).get("Data", []):
                news_list.append({
                    "title": item.get("Title", ""),
                    "url": item.get("Url", ""),
                    "time": item.get("ShowTime", "")
                })
            return news_list
        except Exception:
            return []

    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        简单情感分析

        Args:
            news_list: 新闻列表

        Returns:
            情感分析结果 {'positive': int, 'negative': int, 'neutral': int, 'overall': str}
        """
        sentiment = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "overall": "中性"
        }

        for news in news_list:
            title = news.get("title", "")
            p_count = sum(1 for w in self.positive_words if w in title)
            n_count = sum(1 for w in self.negative_words if w in title)

            if p_count > n_count:
                sentiment["positive"] += 1
            elif n_count > p_count:
                sentiment["negative"] += 1
            else:
                sentiment["neutral"] += 1

        # 生成情感判断
        if sentiment["positive"] > sentiment["negative"]:
            sentiment["overall"] = "偏多"
        elif sentiment["negative"] > sentiment["positive"]:
            sentiment["overall"] = "偏空"

        return sentiment

    def generate_suggestion(
        self,
        sentiment: Dict,
        alerts: List
    ) -> str:
        """
        基于数据生成建议

        Args:
            sentiment: 情感分析结果
            alerts: 预警列表

        Returns:
            建议字符串
        """
        alert_types = []
        for a in alerts:
            if isinstance(a, tuple):
                alert_types.append(a[0].value if hasattr(a[0], 'value') else str(a[0]))
            else:
                alert_types.append(str(a))

        overall = sentiment.get("overall", "中性")

        # 价格下跌 + 舆情偏空 = 谨慎
        if any('below' in t or 'down' in t for t in alert_types) and overall == "偏空":
            return "⚠️ 价格跌破支撑位，且舆情偏空，建议观察等待，不急于抄底。"

        # 价格下跌 + 舆情偏多 = 可能是机会
        if any('below' in t or 'down' in t for t in alert_types) and overall == "偏多":
            return "🔍 价格下跌但舆情偏多，可能是情绪错杀，关注是否有反弹机会。"

        # 价格突破 + 舆情偏多 = 确认趋势
        if any('above' in t or 'up' in t for t in alert_types) and overall == "偏多":
            return "🚀 价格突破且舆情配合，趋势可能延续，可考虑顺势而为。"

        # 大涨
        if any('pct_up' in t for t in alert_types):
            return "📈 短期涨幅较大，注意获利了结风险。"

        # 大跌
        if any('pct_down' in t for t in alert_types):
            return "📉 短期跌幅较大，关注是否超跌反弹，但勿急于抄底。"

        # 盈利达标
        if any('cost_above' in t for t in alert_types):
            return "✅ 盈利达标，可考虑分批减仓锁定利润，或继续持有观察趋势。"

        # 亏损止损
        if any('cost_below' in t for t in alert_types):
            return "⚠️ 亏损达到止损位，建议严格执行止损纪律，或等待反弹减仓。"

        return "⏳ 建议保持观察，等待更明确信号。"
