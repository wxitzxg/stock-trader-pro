#!/usr/bin/env python3
"""
Controller 层 - 处理命令行请求
"""

from controllers.account import cmd_account, cmd_holdings
from controllers.alert import cmd_alert
from controllers.analyze import cmd_analyze
from controllers.export import cmd_export
from controllers.flow import cmd_flow
from controllers.monitor import cmd_monitor
from controllers.params import cmd_params
from controllers.portfolio import cmd_portfolio
from controllers.query import cmd_query
from controllers.search import cmd_search
from controllers.sector import cmd_sector
from controllers.smart_monitor import cmd_smart_monitor
from controllers.update_kline import cmd_update_kline
from controllers.update_prices import cmd_update_prices
from controllers.update_stock_list import cmd_update_stock_list
from controllers.watchlist import cmd_watchlist

__all__ = [
    'cmd_account',
    'cmd_holdings',
    'cmd_alert',
    'cmd_analyze',
    'cmd_export',
    'cmd_flow',
    'cmd_monitor',
    'cmd_params',
    'cmd_portfolio',
    'cmd_query',
    'cmd_search',
    'cmd_sector',
    'cmd_smart_monitor',
    'cmd_update_kline',
    'cmd_update_prices',
    'cmd_update_stock_list',
    'cmd_watchlist',
]
