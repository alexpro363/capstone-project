import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from database import get_db_cursor

def clear_database():
    """Clear all entries from products and reviews tables and reset ID sequences."""
    with get_db_cursor() as cursor:
        # Delete all entries from reviews and products
        cursor.execute("DELETE FROM reviews;")
        cursor.execute("DELETE FROM products;")
        
        # Reset the sequence for the id column in reviews and products table
        cursor.execute("ALTER SEQUENCE reviews_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1;")
        
        # Commit changes to the database
        cursor.connection.commit()
        print("Database cleared and ID sequences reset.")

if __name__ == "__main__":
    clear_database()