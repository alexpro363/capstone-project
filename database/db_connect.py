import psycopg2
from contextlib import contextmanager

# Database connection details
DB_NAME = "project_db" 
DB_USER = "postgres"    
DB_PASSWORD = "MAN0nTH3m00n$"
DB_HOST = "localhost"
DB_PORT = "5432"

@contextmanager
def get_db_connection():
    """Context manager for PostgreSQL database connection."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    try:
        yield conn
    finally:
        conn.close()