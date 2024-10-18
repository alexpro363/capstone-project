import ssl
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
from .chrome_options import create_driver  # Import the Chrome options function

def fetch_amazon_products(search_query, max_pages=5):
    # Fetches products for a specific search query on Amazon concurrently

    retries = 6  # Number of retries for each request in case of failure

    def get_driver_with_retry():
        """Attempt to create a WebDriver with retries for SSL errors or WebDriverExceptions."""
        attempt = 0
        while attempt < retries:
            try:
                return create_driver()  # Use proxy-enabled driver creation function
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                attempt += 1
                print(f"SSL or WebDriver error encountered: {e}. Retrying...")
                time.sleep(3)  # Wait a bit before retrying
        raise Exception("Max retries reached. Could not create a WebDriver instance.")

    def scrape_product_page(search_query, page_number):
        """Scrapes a single product page."""
        driver = get_driver_with_retry()
        products = []
        try:
            print(f"Scraping page {page_number}...")
            url = f"https://www.amazon.com/s?k={search_query}&page={page_number}"

            try:
                driver.get(url)
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                print(f"SSL or WebDriver error while accessing {url}: {e}. Retrying with a new driver...")
                driver.quit()
                driver = get_driver_with_retry()
                return []  # Return an empty list to indicate failure

            # Check if page is blocked or contains CAPTCHA
            if "Enter the characters you see below" in driver.page_source or "Sorry, we just need to make sure you're not a robot." in driver.page_source:
                print("CAPTCHA encountered or request blocked. Retrying...")
                time.sleep(random.uniform(5, 10))
                driver.quit()
                driver = get_driver_with_retry()  # Retry with a new driver and proxy
                return []  # Return an empty list to indicate CAPTCHA block

            # Random scroll to a position on the page to mimic human behavior
            scroll_position = random.randint(500, 1500)
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(1, 2))  # Random delay

            # Scroll to the bottom of the page to ensure all content loads
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 5))  # Wait for new content to load (if needed)

            # Explicit wait to ensure the search results are fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-result-item"))
            )

            # Random mouse movement to mimic human behavior
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(0, 100), random.randint(0, 100)).perform()
            time.sleep(random.uniform(1, 3))

            # Extract product information from the current page
            product_elements = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item")

            for product in product_elements:
                try:
                    # Try extracting title from multiple potential CSS selectors
                    title_element = product.find_elements(By.CSS_SELECTOR, "h2 a span")
                    title = title_element[0].text if title_element else None

                    # Fallback: Try another possible selector
                    if not title or title.lower() in ["results", "related searches", "need help?", "no title"]:
                        alt_title_element = product.find_elements(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal")
                        title = alt_title_element[0].text if alt_title_element else None

                    if not title or title.lower() in ["results", "related searches", "need help?", "no title"]:
                        continue  # Skip non-product elements

                    # Extract price details, if available
                    price_whole = product.find_element(By.CLASS_NAME, "a-price-whole").text if product.find_elements(By.CLASS_NAME, "a-price-whole") else None
                    price_fraction = product.find_element(By.CLASS_NAME, "a-price-fraction").text if product.find_elements(By.CLASS_NAME, "a-price-fraction") else "00"
                    price = f"{price_whole}.{price_fraction}" if price_whole else "No Price"

                    # Extract ASIN (Amazon Standard Identification Number)
                    asin = product.get_attribute("data-asin") if product.get_attribute("data-asin") else "No ASIN"

                    # Extract product image URL
                    image_element = product.find_elements(By.CSS_SELECTOR, "img.s-image")
                    image_url = image_element[0].get_attribute("src") if image_element else "No Image URL"

                    # Filter out items without proper data
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

    # Run scraping tasks concurrently
    all_products = []
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust the number of workers as needed
        futures = [executor.submit(scrape_product_page, search_query, page) for page in range(1, max_pages + 1)]
        
        for future in as_completed(futures):
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                print(f"Error in a concurrent task: {e}")

    return all_products