from contextlib import contextmanager
from .db_connect import get_db_connection

# Func: Provides a PostgreSQL database cursor to interact with database
# Parameters: commit (bool) - If True, commits the transaction after execution
# Returns: A cursor object within the context of usage, closing it afterward
@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as conn:  # Establish the database connection
        cursor = conn.cursor()  # Create a cursor for executing SQL commands
        try:
            yield cursor  # Return the cursor for operations
            if commit:  
                conn.commit()  # Commit the transaction if specified
        finally:
            cursor.close()  # Ensure the cursor is closed after use
