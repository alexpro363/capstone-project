from .database import get_db_cursor

def get_product_by_asin(asin):
    """Fetch a product by its ASIN."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM products WHERE asin = %s;
            """,
            (asin,)
        )
        return cursor.fetchone()
    
def get_cheapest_products(query_id, limit=10):
    """Fetch the 10 cheapest products for a given query from the database."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, asin, title, price FROM products
            WHERE query_id = %s
            ORDER BY price ASC
            LIMIT %s;
            """,
            (query_id, limit)
        )
        return cursor.fetchall()


def get_reviews_by_product_id(product_id):
    
    #Fetch all reviews for a given product ID from the database.
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, review_text
            FROM reviews
            WHERE product_id = %s;
            """,
            (product_id,)
        )

        # Fetch all reviews from the result
        reviews = cursor.fetchall()

    return reviews

def get_query_id(search_query):
    
    #Fetch the query ID for a specific search query from the database.

    #param search_query: The search query to look for.
    #return: The query ID if found, otherwise None.
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM queries WHERE query_text = %s;
            """,
            (search_query,)
        )
        result = cursor.fetchone()  # Fetch the first result (if any)
    
    if result:
        return result[0]  # Return the query ID
    else:
        return None  # If no query found, return None
