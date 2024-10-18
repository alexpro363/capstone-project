from .db_cursor import get_db_cursor
from .db_fetch import get_query_id
from .db_insert import insert_query
from .db_delete import delete_products_and_reviews


def query_exists(search_query):
    
    #Check if a specific search query exists in the database.

    #param search_query: The search query to check.
    #return: True if the query exists, False otherwise.
    
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS(SELECT 1 FROM queries WHERE query_text = %s);
            """,
            (search_query,)
        )
        exists = cursor.fetchone()[0]  # Fetch the result, which is a boolean value
    
    return exists

def manage_query(search_query):

    if query_exists(search_query):
        print(f"The search query '{search_query}' already exists in the database.")
        query_id = get_query_id(search_query)

        if query_id:
            # Delete the products and reviews for this query
            delete_products_and_reviews(query_id)
            print(f"Deleted all data for the query '{search_query}'.")
        else:
            print(f"Failed to fetch query ID for '{search_query}'.")
    else:
        # Insert the new query and get its ID
        query_id = insert_query(search_query)
        print(f"Inserted new query '{search_query}' with ID {query_id}.")
    
    return query_id

def best_products(query_id, limit=5):
    # Fetch the best products (cheapest with highest sentiment) for a given query ID
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, asin, title, price, image_url, sentiment_score
            FROM products
            WHERE query_id = %s
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
        best_products_list.append({
            'id': product[0],
            'asin': asin,
            'title': product[2],
            'price': product[3],
            'image_url': product[4],
            'sentiment_score': product[5],
            'product_url': product_url  # Amazon URL from asin
        })

    return best_products_list