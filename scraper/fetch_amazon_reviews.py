#Developed with the help of ChatGPT 4o

import ssl
import logging
import traceback
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from .chrome_options import create_driver

# Configure logging for scraping errors
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

# Func: Fetches reviews for a specific Amazon product using its ASIN
# Parameters: asin (str) - The ASIN of the product to fetch reviews for; max_pages (int) - Maximum number of review pages to scrape
# Returns: A list of dictionaries containing review data
def fetch_amazon_reviews(asin, max_pages=3):
    retries = 5  # Number of retries for each request if one fails due to error

    # Func: Attempts to create a webdriver with retries for errors
    # Returns: A webdriver instance or raises an Exception after max retries
    def get_driver_with_retry():
        attempt = 0
        while attempt < retries:
            try:
                driver = create_driver()
                driver.set_page_load_timeout(90)
                return driver
            except (ssl.SSLError, MaxRetryError, WebDriverException) as e:
                attempt += 1
                logging.error(f"SSL or WebDriver error encountered: {e}. Retrying {attempt}/{retries}...")
                time.sleep(2)  # Wait before retrying
        raise Exception("Max retries reached. Could not create a WebDriver instance.")

    # Func: Scrapes a review page for a product using its ASIN
    # Parameters: asin (str) - The ASIN of the product; page_number (int) - The page number to scrape
    # Returns: A list of reviews scraped from the page
    def scrape_review_page(asin, page_number):
        max_page_retries = 3  # Number of retries for a single page
        retries = 0
        reviews = []

        while retries < max_page_retries:
            driver = get_driver_with_retry()
            try:
                logging.info(f"Scraping reviews page {page_number} for ASIN: {asin} (Attempt {retries + 1}/{max_page_retries})...")
                url = f"https://www.amazon.com/product-reviews/{asin}/?pageNumber={page_number}"
                driver.get(url)

                # Check if page is blocked or contains CAPTCHA
                if "Enter the characters you see below" in driver.page_source or "Sorry, we just need to make sure you're not a robot." in driver.page_source:
                    logging.warning(f"CAPTCHA encountered on page {page_number}. Retrying...")
                    driver.quit()
                    retries += 1
                    continue  # Retry the page with a new driver instance

                # Scroll to the bottom of the page to ensure all content loads
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))  # Wait for new content to load if needed

                # Wait for the presence of reviews
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.review"))
                )

                # Extract reviews from the page
                review_elements = driver.find_elements(By.CSS_SELECTOR, "div.review")
                for review in review_elements:
                    try:
                        # Extract review text
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
                driver.quit()  # Close the driver before retrying

            finally:
                driver.quit()  # Ensure driver is closed after the attempt

        return reviews

    # Run scraping tasks concurrently for faster scraping
    all_reviews = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_review_page, asin, page) for page in range(1, max_pages + 1)]

        # Collect reviews from all pages
        for future in as_completed(futures):
            try:
                reviews = future.result()
                all_reviews.extend(reviews)
            except Exception as e:
                logging.error(f"Error in a concurrent task for ASIN {asin}: {e}")
                logging.error(traceback.format_exc())  # Log the full stack trace for the failed task

    return all_reviews
