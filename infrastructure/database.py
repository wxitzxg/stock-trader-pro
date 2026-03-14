"""
Database - 兼容层
"""
from domain.portfolio.repositories.database import Database, get_db, init_database

__all__ = ['Database', 'get_db', 'init_database']
