from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
from .chrome_options import set_chrome_options  # Import Chrome options setup function

# Path to ChromeDriver executable
service = Service(r"C:\Users\Alexp\chromedriver-win64\chromedriver.exe")

def fetch_amazon_reviews(asin, max_pages=5):
    #Fetches reviews for a specific Amazon product using its ASIN.
    
    #param asin: The ASIN of the product to fetch reviews for.
    #param max_pages: The maximum number of review pages to scrape.
    #return: A list of dictionaries containing review data.
    
    # Set up WebDriver with options
    chrome_options = set_chrome_options()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Amazon reviews URL for a specific ASIN
    url = f"https://www.amazon.com/product-reviews/{asin}/"
    driver.get(url)
    
    all_reviews = []
    current_page = 1
    retries = 3  # Number of retries for each request if one fails

    try:
        while current_page <= max_pages:
            print(f"Scraping reviews page {current_page} for ASIN: {asin}...")

            # Check if page is blocked or contains CAPTCHA
            if "Enter the characters you see below" in driver.page_source or "Sorry, we just need to make sure you're not a robot." in driver.page_source:
                print("CAPTCHA encountered or request blocked. Retrying...")
                time.sleep(random.uniform(5, 10))
                driver.get(url)  # Retry the request
                continue

            # Random scroll to a position on the page to mimic human behavior
            scroll_position = random.randint(500, 1500)
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(1, 2))  # Random delay

            # Scroll to the bottom of the page to ensure all content loads
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 5))  # Wait for new content to load (if needed)

            # Wait to ensure the reviews are fully loaded
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.review"))
                )
            except Exception as e:
                print(f"Error loading page content: {e}")
                retries -= 1
                if retries <= 0:
                    break
                continue  # Retry the current page if failed

            # Random mouse movement
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(0, 100), random.randint(0, 100)).perform()
            time.sleep(random.uniform(1, 3))

            # Extract review elements from the current page
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div.review")

            # Extract review information from the current page
            for review in review_elements:
                try:

                    # Extract review text
                    review_text_element = review.find_elements(By.CSS_SELECTOR, "span.review-text-content span")
                    review_text = review_text_element[0].text if review_text_element else "No Review Text"

                    # Collect review data
                    all_reviews.append({'Review Text': review_text,})

                except Exception as e:
                    print(f"Error parsing review: {e}")

            # Find the "Next" button and click it to go to the next page of reviews
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.a-last a"))
                )
                if not next_button:
                    print("Reached the last page of reviews.")
                    break  # Exit the loop if the "Next" button is not found
                next_button.click()
                current_page += 1

                # Wait for the new page to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.review"))
                )
                time.sleep(random.uniform(2, 4))  # Random delay to mimic human behavior

            except Exception as e:
                print("No more pages to scrape or 'Next' button not found.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the browser is closed properly
        driver.quit()

    return all_reviews
