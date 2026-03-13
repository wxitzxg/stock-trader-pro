"""
新浪财经数据源
提供 A 股、港股、美股实时行情
"""
import requests
from typing import Optional, Dict, Any, List
import pandas as pd

from stockquery.sources.base import BaseDataSource


class SinaDataSource(BaseDataSource):
    """新浪财经数据源"""

    name = "sina"

    def __init__(self, timeout: int = 10):
        """
        初始化新浪财经数据源

        Args:
            timeout: 请求超时时间 (秒)
        """
        self.timeout = timeout

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票行情

        Args:
            symbol: 股票代码（6 位数字，或带市场前缀）

        Returns:
            股票行情数据字典
        """
        code = symbol.strip().upper()

        # 判断市场并添加前缀
        if not code.startswith(('SH', 'SZ', 'HK', 'US')):
            if code.startswith('6') or code.startswith('5'):
                code = f"sh{code}"
            elif code.startswith('0') or code.startswith('3'):
                code = f"sz{code}"

        url = f"https://hq.sinajs.cn/list={code}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn',
        }

        try:
            response = requests.get(url, timeout=self.timeout, headers=headers)

            if response.status_code != 200:
                return None

            data = response.text.strip()

            if 'v_hq_str' in data or '不存在' in data:
                return None

            # 解析数据
            if '=' not in data:
                return None

            # 提取=号后面的内容
            parts = data.split('=')
            if len(parts) < 2:
                return None

            content = parts[1].strip().strip('";')
            values = content.split(',')

            if len(values) < 32:
                return None

            name = values[0]
            open_price = float(values[1]) if values[1] else 0
            yesterday_close = float(values[2]) if values[2] else 0
            current_price = float(values[3]) if values[3] else 0
            high_price = float(values[4]) if values[4] else 0
            low_price = float(values[5]) if values[5] else 0

            # 计算涨跌
            change = current_price - yesterday_close
            if current_price > 0 and yesterday_close > 0:
                change_percent = (change / yesterday_close) * 100
            else:
                change_percent = 0

            # 获取成交量和成交额
            try:
                volume_raw = values[8] if len(values) > 8 and values[8] else '0'
                volume = int(float(volume_raw))  # 成交量 (股)
            except:
                volume = 0

            try:
                amount_raw = values[9] if len(values) > 9 and values[9] else '0'
                amount = float(amount_raw)  # 成交额 (元)
            except:
                amount = 0

            # 获取时间
            date = values[30] if len(values) > 30 else ''
            time = values[31] if len(values) > 31 else ''

            # 判断市场
            market = 'A 股'
            stock_code = code
            if code.startswith('sh'):
                market = '沪市 A 股'
                stock_code = code[2:].upper()
            elif code.startswith('sz'):
                market = '深市 A 股'
                stock_code = code[2:].upper()

            return {
                'source': self.name,
                'code': stock_code,
                'name': name,
                'price': current_price,
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'volume': volume,
                'amount': amount,
                'market': market,
                'date': date,
                'time': time,
            }

        except Exception as e:
            print(f"新浪财经数据获取失败：{e}")
            return None

    def get_historical_data(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[pd.DataFrame]:
        """
        新浪财经不提供历史数据，返回 None
        """
        return None

    def get_quotes_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取行情

        Args:
            symbols: 股票代码列表

        Returns:
            行情数据列表
        """
        results = []
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                results.append(quote)
        return results
