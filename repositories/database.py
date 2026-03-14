"""
Database - 数据库管理类
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models.base import Base
from config import DATABASE_PATH


class Database:
    """数据库管理类"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or DATABASE_PATH
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

    def init_db(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


_db_instance = None


def get_db():
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.init_db()
    return _db_instance


def init_database():
    """初始化数据库"""
    db = Database()
    db.init_db()
    return db


__all__ = ['Database', 'get_db', 'init_database']
