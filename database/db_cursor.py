from contextlib import contextmanager
from .db_connect import get_db_connection

@contextmanager
def get_db_cursor(commit=False):
    # Context manager for PostgreSQL database cursor.
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()