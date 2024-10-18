import ssl
import logging
import traceback
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from .chrome_options import create_driver  # Import Chrome options setup function

# Configure logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

def fetch_amazon_reviews(asin, max_pages=3):
    """Fetches reviews for a specific Amazon product using its ASIN concurrently."""
    retries = 6  # Number of retries for each request if one fails due to SSL error or page error

    def get_driver_with_retry():
        """Attempt to create a WebDriver with retries for SSL errors or WebDriverExceptions."""
        attempt = 0
        while attempt < retries:
            try:
                driver = create_driver()
                return driver
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                attempt += 1
                logging.error(f"SSL or WebDriver error encountered: {e}. Retrying {attempt}/{retries}...")
                time.sleep(2)  # Wait a bit before retrying
        raise Exception("Max retries reached. Could not create a WebDriver instance.")

    def scrape_review_page(asin, page_number):
        """Scrapes a single review page with retry mechanism."""
        max_page_retries = 3  # Number of retries for a single page
        retries = 0
        reviews = []

        while retries < max_page_retries:
            driver = get_driver_with_retry()
            try:
                logging.info(f"Scraping reviews page {page_number} for ASIN: {asin} (Attempt {retries + 1}/{max_page_retries})...")
                url = f"https://www.amazon.com/product-reviews/{asin}/?pageNumber={page_number}"
                driver.get(url)

                # Check if the page contains CAPTCHA or is blocked
                if "Enter the characters you see below" in driver.page_source or "Sorry, we just need to make sure you're not a robot." in driver.page_source:
                    logging.warning(f"CAPTCHA encountered on page {page_number}. Retrying...")
                    time.sleep(random.uniform(3, 5))  # Random delay to mimic human behavior
                    driver.quit()
                    retries += 1
                    continue  # Retry the page with a new driver instance

                # Random scroll to a position on the page to mimic human behavior
                scroll_position = random.randint(500, 1500)
                driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(random.uniform(1, 2))  # Random delay

                # Scroll to the bottom of the page to ensure all content loads
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 5))  # Wait for new content to load (if needed)

                # Increase WebDriverWait timeout to 20 seconds to allow slower page loads
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.review"))
                )

                # Extract reviews from the page
                review_elements = driver.find_elements(By.CSS_SELECTOR, "div.review")
                for review in review_elements:
                    try:
                        review_text_element = review.find_elements(By.CSS_SELECTOR, "span.review-text-content span")
                        review_text = review_text_element[0].text if review_text_element else "No Review Text"
                        reviews.append({'Review Text': review_text})
                    except Exception as e:
                        logging.error(f"Error parsing review on page {page_number} for ASIN {asin}: {e}")
                        logging.error(traceback.format_exc())  # Log the full stack trace

                break  # Exit retry loop if the page was successfully scraped

            except (TimeoutException, ssl.SSLError, MaxRetryError, WebDriverException) as e:
                logging.error(f"Error scraping page {page_number} for ASIN {asin}: {e}. Retrying...")
                retries += 1
                time.sleep(random.uniform(1, 3))
                driver.quit()  # Close the driver before retrying

            finally:
                driver.quit()  # Ensure driver is closed after the attempt

        return reviews

    # Run scraping tasks concurrently
    all_reviews = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # Adjust the number of workers as needed
        futures = [executor.submit(scrape_review_page, asin, page) for page in range(1, max_pages + 1)]

        for future in as_completed(futures):
            try:
                reviews = future.result()
                all_reviews.extend(reviews)
            except Exception as e:
                logging.error(f"Error in a concurrent task for ASIN {asin}: {e}")
                logging.error(traceback.format_exc())  # Log the full stack trace for the failed task

    return all_reviews