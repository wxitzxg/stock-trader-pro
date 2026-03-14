#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加 Account 表
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect
from config import DATABASE_PATH
from models.base import Base
from models.account import Account


def check_table_exists(engine, table_name):
    """检查表是否已存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate():
    """执行迁移"""
    print("🔄 开始数据库迁移...")
    print(f"📁 数据库路径：{DATABASE_PATH}")

    # 创建引擎
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")

    # 检查 Account 表是否已存在
    if check_table_exists(engine, "accounts"):
        print("✅ Account 表已存在，无需迁移")
        return

    print("📝 创建 Account 表...")

    # 只创建 Account 表
    Base.metadata.create_all(bind=engine, tables=[Account.__table__])

    print("✅ Account 表创建成功")

    # 验证
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('accounts')]
    print(f"   字段：{', '.join(columns)}")

    print("\n✅ 数据库迁移完成！")


if __name__ == "__main__":
    migrate()
