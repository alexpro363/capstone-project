import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import fetch_amazon_products  # Import function to scrape Amazon
from database import insert_product, insert_query, get_product_by_asin  # Import database functions

def main():
    # Get user input for the product query
    search_query = input("Enter the product you are looking for: ")

    # Insert the search query into the 'queries' table and get the query ID
    query_id = insert_query(search_query)
    print(f"Inserted query '{search_query}' into 'queries' table with ID {query_id}.")

    # Fetch products from Amazon using the scraping function
    products = fetch_amazon_products(search_query)

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

    # Fetch and display products stored in the database
    print("\nProducts stored in the database:")
    for product in products:
        db_product = get_product_by_asin(product['ASIN'])
        print(f"Product ID: {db_product[0]}, ASIN: {db_product[2]}, Title: {db_product[3]}, Price: {db_product[4]}")

if __name__ == "__main__":
    main()