from .db_cursor import get_db_cursor
from .db_fetch import get_cheapest_products
from scraper import (
    fetch_amazon_products,
    fetch_amazon_reviews
)

def insert_product(query_id, asin, title, price, image_url, sentiment_score=None):
    #Insert a product into the products table.
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
    #Insert a search query into the queries table.
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO queries (query_text) VALUES (%s) RETURNING id;
            """,
            (query_text,)
        )
        query_id = cursor.fetchone()[0]

        return query_id  # Return the generated query ID
    
def insert_review(product_id, review_text, review_sentiment_score=None):
    """Insert a review into the reviews table."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO reviews (product_id, review_text, review_sentiment_score)
            VALUES (%s, %s, %s);
            """,
            (product_id, review_text, review_sentiment_score)
        )

def fetch_and_store_products(user_search, query_id):

    # Fetch products from Amazon based on the user search query and insert them into the database
    
    # Fetch products from Amazon
    products = fetch_amazon_products(user_search)
    
    # Store fetched products into the 'products' table
    for product in products:
        # Clean the price by removing commas and converting to a float
        price_str = product['Price'].replace(",", "")
        try:
            price = float(price_str) if price_str != "No Price" else None
        except ValueError:
            price = None  # Handle any edge cases where the price isn't a valid float

        insert_product(
            query_id=query_id,  # Link the product to the search query
            asin=product['ASIN'],
            title=product['Title'],
            price=price,
            image_url=product['Image URL']
        )
        print(f"Inserted product '{product['Title']}' with ASIN {product['ASIN']} into 'products' table.")
    
    return products  # Return the products list if needed for further operations

def fetch_and_store_reviews(query_id, max_pages=3, max_workers=5):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from sentiment import analyze_sentiment

    # Fetch reviews for the 10 cheapest products of a query and store them in the database concurrently.
    
    # Get the 10 cheapest products
    cheapest_products = get_cheapest_products(query_id)

    def fetch_and_store_for_product_page(product, page_number):
        """Fetch and store reviews for a specific product's page."""
        product_id = product[0]  # 'id' from products table
        asin = product[1]        # 'asin' from products table
        title = product[2]       # 'title' from products table
        
        print(f"Fetching reviews for product: {title} (ASIN: {asin}) - Page {page_number}...")
        
        # Fetch reviews for the specific page using fetch_amazon_reviews
        reviews = fetch_amazon_reviews(asin, max_pages=page_number)
        
        # Store fetched reviews in the database
        for review in reviews:
            review_text = review['Review Text']
            sentiment_score = analyze_sentiment(review_text)
            insert_review(
                product_id=product_id,
                review_text=review_text,
                review_sentiment_score=sentiment_score
            )

        print(f"Stored reviews for product {title} (ASIN: {asin}) - Page {page_number}.")
    
    # Create a list of futures to handle both products and pages concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for product in cheapest_products:
            for page in range(1, max_pages + 1):
                futures.append(executor.submit(fetch_and_store_for_product_page, product, page))
        
        for future in as_completed(futures):
            try:
                future.result()  # Ensure exceptions are raised, if any
            except Exception as e:
                print(f"Error while fetching reviews: {e}")


def update_product_sentiment_score(product_id, avg_sentiment_score):
    """
    Update the sentiment score of a product in the 'products' table.
    """
    query = """
    UPDATE products
    SET sentiment_score = %s
    WHERE id = %s
    """
    
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (avg_sentiment_score, product_id))