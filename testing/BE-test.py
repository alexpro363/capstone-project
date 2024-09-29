from database import (
     manage_query,
     fetch_and_store_products,
     fetch_and_store_reviews
)
from sentiment import update_product_sentiment_scores


def main():
    user_search = input("Search Product: ")

    query_id = manage_query(user_search)

    fetch_and_store_products(user_search,query_id)

    fetch_and_store_reviews(query_id)

    update_product_sentiment_scores()

if __name__ == "__main__":
    main()