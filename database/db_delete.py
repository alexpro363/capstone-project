from .db_cursor import get_db_cursor

def delete_products_and_reviews(query_id):
   
    #Delete all products and reviews for a specific query ID.

    #param query_id: The ID of the query whose products and reviews should be deleted.
    
    with get_db_cursor(commit=True) as cursor:
        # Delete all reviews associated with the products for the given query
        cursor.execute(
            """
            DELETE FROM reviews
            WHERE product_id IN (
                SELECT id FROM products WHERE query_id = %s
            );
            """,
            (query_id,)
        )
        
        # Delete all products associated with the given query
        cursor.execute(
            """
            DELETE FROM products
            WHERE query_id = %s;
            """,
            (query_id,)
        )
    
    print(f"Deleted all products and reviews for query ID {query_id}.")
