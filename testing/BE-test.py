import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
     manage_query,
     fetch_and_store_products,
     fetch_and_store_reviews,
     best_products
)
from sentiment import update_product_sentiment_scores
from display import display_best_products


def main():
    user_search = input("Search Product: ")

    query_id = manage_query(user_search)

    fetch_and_store_products(user_search,query_id)

    fetch_and_store_reviews(query_id)

    update_product_sentiment_scores(query_id)

    best = best_products(query_id)

    display_best_products(best)

if __name__ == "__main__":
    main()