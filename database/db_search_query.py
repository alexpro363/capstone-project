from .db_cursor import get_db_cursor
from .db_fetch import get_query_id
from .db_insert import insert_query
from .db_delete import delete_products_and_reviews

# Func: Check if a specific search query exists in the database
# Parameters: search_query (str) - The search query to check
# Returns: Boolean - True if the query exists, False otherwise
def query_exists(search_query):

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS(SELECT 1 FROM queries WHERE query_text = %s);
            """,
            (search_query,)
        )
        exists = cursor.fetchone()[0]  # Fetch the result, which is a boolean value
    
    return exists

# Func: Manages search queries by checking if the query already exists, deletes old data if found, and inserts a new query
# This ensures the query is "reloaded" by removing it and adding it fresh to update the timestamp
# Parameters: search_query (str) - The user's search query
# Returns: query_id (int) - The ID of the managed query
def manage_query(search_query):
    
    if query_exists(search_query):
        print(f"The search query '{search_query}' already exists in the database.")
        query_id = get_query_id(search_query)

        if query_id:
            # Delete the query so it is a fresh entry
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM queries WHERE id = %s;
                    """, 
                    (query_id,)
                )
                print(f"Deleted the query '{search_query}' from the database.")
    
    # Now insert the new query (this ensures a new timestamp is set)
    query_id = insert_query(search_query)
    print(f"Inserted new query '{search_query}' with ID {query_id}.")

    return query_id

# Func: Fetch the best products (cheapest with highest sentiment) for a given query ID
# Parameters: query_id (int), limit (int) - The maximum number of products to fetch
# Returns: List of best products with details such as id, asin, title, price, image URL, sentiment score, and product URL
def best_products(query_id, limit=5):

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, asin, title, price, image_url, sentiment_score
            FROM products
            WHERE query_id = %s AND sentiment_score IS NOT NULL
            ORDER BY sentiment_score DESC, price ASC
            LIMIT %s;
            """, (query_id, limit)
        )
        products = cursor.fetchall()

    # Format the results into a list of dictionaries
    best_products_list = []
    for product in products:
        asin = product[1]
        product_url = f"https://www.amazon.com/dp/{asin}"
        sentiment_score = product[5]
        best_products_list.append({
            'id': product[0],
            'asin': asin,
            'title': product[2],
            'price': product[3],
            'image_url': product[4],
            'sentiment_score': sentiment_score,
            'product_url': product_url 
        })

    return best_products_list

# Func: Fetch the most recent search queries and their corresponding best products
# Parameters: limit (int) - The maximum number of recent searches to fetch
# Returns: A list of dictionaries containing the query text and its best products
def fetch_recent_searches(limit=5):
    
    try:
        # Fetch the most recent queries
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT q.id, q.query_text, q.created_at
                FROM queries q
                ORDER BY q.created_at DESC
                LIMIT %s;
            """, (limit,))

            recent_searches = cursor.fetchall()

        # Fetch best products for each recent query
        recent_search_results = []
        for search in recent_searches:
            query_id = search[0]
            query_text = search[1]  # Get the query text
            best_products_list = best_products(query_id)  # Get the best products for the query
            recent_search_results.append({
                'query_text': query_text,  # Include the query text in the response
                'best_products': best_products_list
            })

        return recent_search_results

    except Exception as e:
        raise Exception(f"Error fetching recent searches: {str(e)}")