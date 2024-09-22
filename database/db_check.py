from .database import get_db_cursor

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
