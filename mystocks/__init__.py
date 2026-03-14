#!/usr/bin/env python3
"""
我的股票 - 综合资产管理模块（兼容性包装器）

注意：此文件仅为向后兼容保留，新代码请直接使用：
    from domain.portfolio.services import MyStocks
"""

from domain.portfolio.services.my_stocks import MyStocks
from domain.portfolio.models import Position, Watchlist, Transaction, PositionLot, Account

__all__ = [
    'MyStocks',
    'Account',
    'Position',
    'PositionLot',
    'Transaction',
    'Watchlist',
]
