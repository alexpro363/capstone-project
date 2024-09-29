from .db_cursor import get_db_cursor
from .db_fetch import get_cheapest_products
from scraper import (
    fetch_amazon_products,
    fetch_amazon_reviews
)
from sentiment import analyze_sentiment

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

def fetch_and_store_products(user_search, query_id):

    #Fetch products from Amazon based on the user search query and insert them into the database.
    
    #param user_search: The search query entered by the user.
    #param query_id: The ID of the query in the 'queries' table to link the products.

    #return: A list of product dictionaries inserted into the database.
    
    # Fetch products from Amazon
    products = fetch_amazon_products(user_search)
    
    # Store fetched products into the 'products' table
    for product in products:
        insert_product(
            query_id=query_id,  # Link the product to the search query
            asin=product['ASIN'],
            title=product['Title'],
            price=product['Price'],
            image_url=product['Image URL']
        )
        print(f"Inserted product '{product['Title']}' with ASIN {product['ASIN']} into 'products' table.")
    
    return products  # Return the products list if needed for further operations

def fetch_and_store_reviews(query_id, max_pages=3):

    #Fetch reviews for the 10 cheapest products of a query and store them in the database.
    
    #param query_id: The ID of the query in the 'queries' table.
    #param max_pages: The maximum number of review pages to scrape.

    # Get the 10 cheapest products
    cheapest_products = get_cheapest_products(query_id)
    
    # Loop through each product and fetch reviews
    for product in cheapest_products:
        product_id = product[0]  # 'id' from products table
        asin = product[1]        # 'asin' from products table
        title = product[2]       # 'title' from products table
        
        print(f"Fetching reviews for product: {title} (ASIN: {asin})...")
        
        # Fetch reviews using the fetch_amazon_reviews function
        reviews = fetch_amazon_reviews(asin, max_pages=max_pages)
        
        # Store fetched reviews in the database
        for review in reviews:
            review_text = review['Review Text']
            sentiment_score = analyze_sentiment(review_text)
            insert_review(
                product_id=product_id,
                review_text=review_text,
                review_sentiment_score=sentiment_score
            )

        print(f"Stored reviews for product {title} (ASIN: {asin}).")

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