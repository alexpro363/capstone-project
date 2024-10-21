import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database functions
from database import get_db_cursor  

# Query to retrieve a product that has a non-null sentiment score

def test_retrieve_product_with_sentiment():

    query = """
    SELECT title, price, sentiment_score
    FROM products
    WHERE sentiment_score IS NOT NULL
    LIMIT 1;
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        product = cursor.fetchone()

        if product:
            title = product[0]
            price = product[1]
            sentiment_score = product[2]
            print(f"Product: {title}, Price: ${price}, Sentiment Score: {sentiment_score}")
        else:
            print("No product found with a sentiment score.")

if __name__ == "__main__":
    test_retrieve_product_with_sentiment()