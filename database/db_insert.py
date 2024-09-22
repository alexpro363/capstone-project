from .database import get_db_cursor

def insert_product(query_id, asin, title, price, image_url, sentiment_score=None):
    """Insert a product into the products table."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO products (asin, query_id, title, price, image_url, sentiment_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (asin) DO NOTHING;  -- To avoid inserting duplicates
            """,
            (asin, query_id, title, price, image_url, sentiment_score)
        )

def insert_query(query_text):
    """Insert a search query into the queries table."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO queries (query_text) VALUES (%s) RETURNING id;
            """,
            (query_text,)
        )
        query_id = cursor.fetchone()[0]

        return query_id  # Return the generated query ID
    
def insert_review(product_id, review_text, sentiment_score=None):
    """Insert a review into the reviews table."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO reviews (product_id, review_text, sentiment_score)
            VALUES (%s, %s, %s);
            """,
            (product_id, review_text, sentiment_score)
        )
