import os
import sys

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import fetch_amazon_products

# Test the function
if __name__ == "__main__":
    search_query = 'headphones'
    max_pages = 3  # Set the number of pages you want to scrape
    products = fetch_amazon_products(search_query, max_pages=max_pages)
    
    # Print the fetched products
    if products:
        for product in products:
            print(product)
    else:
        print("No products found or failed to fetch data.")