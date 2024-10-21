from .db_cursor import get_db_cursor

# Func: Fetches products linked to a specific query ID
# Parameters: query_id (int) - The ID of the query to search for
# Returns: A list of products as tuples containing id, asin, and title
def get_products_by_query_id(query_id):
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, asin, title FROM products
            WHERE query_id = %s;
            """,
            (query_id,)
        )
        products = cursor.fetchall()

    return products


# Func: Fetches 10 cheapest products for a specific query
# Parameters: query_id (int), limit (int) - Max number of products to return
# Returns: A list of the cheapest products as tuples containing id, asin, title, and price
def get_cheapest_products(query_id, limit=10):
    
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


# Func: Fetches reviews for a specific product
# Parameters: product_id (int) - The ID of the product to retrieve reviews for
# Returns: A list of reviews as tuples containing id and review text
def get_reviews_by_product_id(product_id):
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, review_text
            FROM reviews
            WHERE product_id = %s;
            """,
            (product_id,)
        )
        reviews = cursor.fetchall()

    return reviews


# Func: Fetches the query ID for a specific search query
# Parameters: search_query (str) - The search query to search for
# Returns: The query ID if found, otherwise None
def get_query_id(search_query):
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM queries WHERE query_text = %s;
            """,
            (search_query,)
        )
        result = cursor.fetchone()  # Fetch the first result (if any)
    
    return result[0] if result else None  # Return query ID or None


# Func: Fetches products that have associated reviews for a specific query
# Parameters: query_id (int) - The ID of the query to search for
# Returns: A list of products with reviews
def fetch_products_with_reviews(query_id):
    
    query = """
    SELECT p.id, p.asin, p.title
    FROM products p
    JOIN reviews r ON p.id = r.product_id
    WHERE p.query_id = %s
    GROUP BY p.id, p.asin, p.title
    """
    
    with get_db_cursor() as cursor:
        cursor.execute(query, (query_id,))
        products = cursor.fetchall()
        
    return products