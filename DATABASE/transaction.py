from contextlib import contextmanager
from psycopg2 import DatabaseError

@contextmanager
def transaction(conn):
    """
    事务管理上下文管理器
    使用示例：
    with transaction(conn):
        cursor.execute(...)
    """
    try:
        yield conn  # 注意这里yield conn以便在with块内使用
        conn.commit()
    except DatabaseError as e:
        conn.rollback()
        raise RuntimeError(f"Database transaction failed: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Operation failed: {str(e)}")