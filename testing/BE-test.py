import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required functions
from database import (
     manage_query,
     fetch_and_store_products,
     fetch_and_store_reviews,
     best_products
)
from display import display_best_products


# Main function to handle user input and product search flow.
def main():
    # Prompt the user to enter a product to search for
    user_search = input("Search Product: ")

    # Manage the query (insert new or delete existing query data)
    query_id = manage_query(user_search)

    # Fetch and store products related to the query
    fetch_and_store_products(user_search, query_id)

    # Fetch and store reviews for the products fetched above
    fetch_and_store_reviews(query_id)

    # Get the best products based on sentiment and price
    best = best_products(query_id)

    # Display the best products
    display_best_products(best)

if __name__ == "__main__":
    main()
