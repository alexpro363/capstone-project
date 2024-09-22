import psycopg2
from contextlib import contextmanager
from scraper import fetch_amazon_products
from scraper import fetch_amazon_reviews

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

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for PostgreSQL database cursor."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

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
    
def fetch_and_store_reviews(query_id, max_pages=3):
    """Fetch reviews for the 10 cheapest products of a query and store them in the database."""
    # Get the 10 cheapest products
    cheapest_products = get_cheapest_products(query_id)
    
    # Loop through each product and fetch reviews
    for product in cheapest_products:
        product_id = product[0]  # 'id' from products table
        asin = product[1]        # 'asin' from products table
        
        print(f"Fetching reviews for product: {asin} ({product[2]})...")
        
        # Fetch reviews using the fetch_amazon_reviews function
        reviews = fetch_amazon_reviews(asin, max_pages=max_pages)
        
        # Store fetched reviews in the database
        for review in reviews:
            review_text = review['Review Text']
            insert_review(product_id, review_text)
        
        print(f"Stored reviews for product {asin}.")

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



