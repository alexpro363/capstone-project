import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from database import get_db_cursor

def reset_database():
    #Deletes all queries, products, and reviews from the database.

    with get_db_cursor(commit=True) as cursor:
        try:
            # Delete all reviews
            cursor.execute("DELETE FROM reviews;")
            print("Deleted all reviews.")

            # Delete all products
            cursor.execute("DELETE FROM products;")
            print("Deleted all products.")

            # Delete all queries
            cursor.execute("DELETE FROM queries;")
            print("Deleted all queries.")

        except Exception as e:
            print(f"Error while resetting the database: {e}")

if __name__ == "__main__":
    reset_database()
