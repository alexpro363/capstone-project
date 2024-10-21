from .db_cursor import get_db_cursor
from .db_fetch import get_cheapest_products
from scraper import (
    fetch_amazon_products,
    fetch_amazon_reviews
)

# Func: Inserts a product into the products table
# Parameters: query_id (int), asin (str), title (str), price (float), image_url (str), sentiment_score (float or None)
# Returns: None
def insert_product(query_id, asin, title, price, image_url, sentiment_score=None):

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO products (asin, query_id, title, price, image_url, sentiment_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (asin) DO NOTHING;
            """,
            (asin, query_id, title, price, image_url, sentiment_score)
        )

# Func: Inserts a search query into the queries table and returns the query ID
# Parameters: query_text (str)
# Returns: query_id (int)
def insert_query(query_text):

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO queries (query_text) VALUES (%s) RETURNING id;
            """,
            (query_text,)
        )
        query_id = cursor.fetchone()[0]
        return query_id

# Func: Inserts a review into the reviews table
# Parameters: product_id (int), review_text (str), review_sentiment_score (float or None)
# Returns: None
def insert_review(product_id, review_text, review_sentiment_score=None):

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO reviews (product_id, review_text, review_sentiment_score)
            VALUES (%s, %s, %s);
            """,
            (product_id, review_text, review_sentiment_score)
        )

# Func: Fetches products from Amazon based on a user search and stores them in the database
# Parameters: user_search (str), query_id (int)
# Returns: List of fetched products
def fetch_and_store_products(user_search, query_id):
    
    # Fetch products from Amazon
    products = fetch_amazon_products(user_search)
    
    # Store fetched products in the database
    for product in products:
        price_str = product['Price'].replace(",", "")
        try:
            price = float(price_str) if price_str != "No Price" else None
        except ValueError:
            price = None

        insert_product(
            query_id=query_id,
            asin=product['ASIN'],
            title=product['Title'],
            price=price,
            image_url=product['Image URL']
        )
        print(f"Inserted product '{product['Title']}' with ASIN {product['ASIN']} into 'products' table.")
    
    return products

# Func: Fetches reviews for the cheapest products and stores them in the database
# Parameters: query_id (int), max_pages (int), max_workers (int)
# Returns: None
def fetch_and_store_reviews(query_id, max_pages=3, max_workers=3):

    # Imports for dealing with fetching reviews for multiple products at a time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from sentiment import analyze_sentiment
    from database import update_product_sentiment_score

    # Fetch the cheapest products
    cheapest_products = get_cheapest_products(query_id)

    #Developed with the help of ChatGPT 4o
    def fetch_and_store_for_product(product):

        product_id = product[0]
        asin = product[1]
        title = product[2]

        print(f"Fetching reviews for product: {title} (ASIN: {asin})...")
        total_sentiment_score = 0.0
        review_count = 0

        reviews = fetch_amazon_reviews(asin, max_pages=max_pages)

        for review in reviews:
            review_text = review['Review Text']
            sentiment_score = analyze_sentiment(review_text)

            # Insert each review into the database
            insert_review(
                product_id=product_id,
                review_text=review_text,
                review_sentiment_score=sentiment_score
            )

            # Accumulate sentiment score and review count
            total_sentiment_score += sentiment_score
            review_count += 1

        avg_sentiment_score = (total_sentiment_score / review_count) * 100 if review_count > 0 else 0

        # Update the sentiment score in the products table
        update_product_sentiment_score(product_id, avg_sentiment_score)

        print(f"Stored reviews and updated sentiment score for {title} (ASIN: {asin}). Avg Sentiment: {avg_sentiment_score}")

    # Scrape reviews for multiple products at a time
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_and_store_for_product, product) for product in cheapest_products]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error while fetching reviews: {e}")

# Func: Updates the sentiment score for a product in the database
# Parameters: product_id (int), avg_sentiment_score (float)
# Returns: None
def update_product_sentiment_score(product_id, avg_sentiment_score):
    query = """
    UPDATE products
    SET sentiment_score = %s
    WHERE id = %s
    """
    
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (avg_sentiment_score, product_id))
