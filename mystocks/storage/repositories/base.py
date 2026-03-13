"""
Repository 基类
"""


class BaseRepository:
    """Repository 基类"""

    def __init__(self, session):
        """
        初始化 Repository

        Args:
            session: SQLAlchemy session
        """
        self.session = session
