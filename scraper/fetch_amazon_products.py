#Developed with the help of ChatGPT 4o

import ssl
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
from .chrome_options import create_driver

# Func: Fetches products for a specific search query on Amazon concurrently
# Parameters: search_query (str) - The search to query Amazon; max_pages (int) - Maximum number of pages to scrape
# Returns: A list of dictionaries containing product data like title, price, ASIN, and image URL
def fetch_amazon_products(search_query, max_pages=5):
    retries = 5  # Number of retries for each request in case of failure

    # Func: Attempts to create a webdriver with retries for errors
    # Returns: A webdriver instance or raises an Exception after max retries has been reached
    def get_driver_with_retry():
        attempt = 0
        while attempt < retries:
            try:
                driver = create_driver()

                driver.set_page_load_timeout(120)


                return driver
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                attempt += 1
                print(f"SSL or WebDriver error encountered: {e}. Retrying...")
                time.sleep(2)  # Wait before retrying
        raise Exception("Max retries reached. Could not create a WebDriver instance.")

    # Func: Scrapes a product page on Amazon
    # Parameters: search_query (str) - The search; page_number (int) - The page number to scrape
    # Returns: A list of product dictionaries scraped from the page
    def scrape_product_page(search_query, page_number):
        driver = get_driver_with_retry()  # Create driver
        products = []
        try:
            print(f"Scraping page {page_number}...")
            url = f"https://www.amazon.com/s?k={search_query}&page={page_number}"

            # Navigate to the URL and handle possible SSL or webdriver errors
            try:
                driver.get(url)
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                print(f"SSL or WebDriver error while accessing {url}: {e}. Retrying with a new driver...")
                driver.quit()
                driver = get_driver_with_retry()
                return []  # Return empty list on failure

            # Check if page contains CAPTCHA or is blocked
            if "Enter the characters you see below" in driver.page_source or "Sorry, we just need to make sure you're not a robot." in driver.page_source:
                print("CAPTCHA encountered or request blocked. Retrying...")
                driver.quit()
                driver = get_driver_with_retry()
                return []  # Return empty list on CAPTCHA block

            # Mimic human behavior with random scroll and delays
            scroll_position = random.randint(500, 1500)
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(1, 2)) 

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  

            # Wait until search results are loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-result-item"))
            )

            # Extract product details from the page
            product_elements = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item")

            for product in product_elements:
                try:
                    # Extract product title using CSS selectors
                    title_element = product.find_elements(By.CSS_SELECTOR, "h2 a span")
                    title = title_element[0].text if title_element else None

                    # If title extraction fails, try alternative selectors
                    if not title or title.lower() in ["results", "related searches", "need help?", "no title"]:
                        alt_title_element = product.find_elements(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal")
                        title = alt_title_element[0].text if alt_title_element else None

                    # Skip non-product elements
                    if not title or title.lower() in ["results", "related searches", "need help?", "no title"]:
                        continue  

                    # Extract product price
                    price_whole = product.find_element(By.CLASS_NAME, "a-price-whole").text if product.find_elements(By.CLASS_NAME, "a-price-whole") else None
                    price_fraction = product.find_element(By.CLASS_NAME, "a-price-fraction").text if product.find_elements(By.CLASS_NAME, "a-price-fraction") else "00"
                    price = f"{price_whole}.{price_fraction}" if price_whole else "No Price"

                    # Extract product ASIN
                    asin = product.get_attribute("data-asin") if product.get_attribute("data-asin") else "No ASIN"

                    # Extract product image URL
                    image_element = product.find_elements(By.CSS_SELECTOR, "img.s-image")
                    image_url = image_element[0].get_attribute("src") if image_element else "No Image URL"

                    # Only add products that have both ASIN and price
                    if asin != "No ASIN" and price != "No Price":
                        products.append({
                            'Title': title,
                            'Price': price,
                            'ASIN': asin,
                            'Image URL': image_url
                        })

                except Exception as e:
                    print(f"Error parsing product: {e}")

        except Exception as e:
            print(f"An error occurred on page {page_number}: {e}")
        finally:
            driver.quit()

        return products

    # Run scraping tasks concurrently to speed up scraping
    all_products = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_product_page, search_query, page) for page in range(1, max_pages + 1)]

        # collect results as each page is scraped
        for future in as_completed(futures):
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                print(f"Error in a concurrent task: {e}")

    return all_products
