from .db_cursor import get_db_cursor

# Func: Deletes products and their associated reviews for a specific query ID
# Parameters: query_id (int) - The ID of the query whose products and reviews will be deleted
# Returns: N/A
def delete_products_and_reviews(query_id):
    
    with get_db_cursor(commit=True) as cursor:
        # Delete reviews associated with the products for the given query
        cursor.execute(
            """
            DELETE FROM reviews
            WHERE product_id IN (
                SELECT id FROM products WHERE query_id = %s
            );
            """,
            (query_id,)
        )
        
        # Delete products associated with the given query
        cursor.execute(
            """
            DELETE FROM products
            WHERE query_id = %s;
            """,
            (query_id,)
        )
    
    print(f"Deleted all products and reviews for query ID {query_id}.")
