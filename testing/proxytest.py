from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
from fake_useragent import UserAgent

# ScraperAPI endpoint for proxies with render enabled
API_KEY = 'e0e951fc3f95783399a1c547fa055f17'
PROXY = f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001?render=true&country=us'

# Set up Chrome options
def set_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # To avoid detection
    chrome_options.add_argument(f"--proxy-server={PROXY}")

    # Randomize user agent and window size
    ua = UserAgent()
    chrome_options.add_argument(f"user-agent={ua.random}")
    window_size = random.choice(["1920,1080", "1366,768", "1440,900", "1536,864"])
    chrome_options.add_argument(f"--window-size={window_size}")
    return chrome_options

# Path to ChromeDriver executable
service = Service(r"C:\Users\Alexp\chromedriver-win64\chromedriver.exe")  # Correct path format

def fetch_amazon_products(search_query, max_pages=5):
    # Set up WebDriver with options
    chrome_options = set_chrome_options()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Amazon search URL
        url = f"https://www.amazon.com/s?k={search_query}"
        driver.get(url)
        all_products = []
        current_page = 1
        retries = 3  # Number of retries for each request

        while current_page <= max_pages:
            print(f"Scraping page {current_page}...")

            # Debugging: Print page source to check what is loaded
            print(driver.page_source[:1000])  # Print the first 1000 characters for better debugging

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

            # Explicit wait to ensure the search results are fully loaded
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-result-item"))
                )
            except Exception as e:
                print(f"Error loading page content: {e}")
                retries -= 1
                if retries <= 0:
                    break
                continue  # Retry the current page

            # Random mouse movement
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(0, 100), random.randint(0, 100)).perform()
            time.sleep(random.uniform(1, 3))

            product_elements = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item")

            # Extract product information from the current page
            for product in product_elements:
                try:
                    # Validate and extract product title
                    title_element = product.find_elements(By.TAG_NAME, "h2")
                    title = title_element[0].text if title_element else None  # Error handling for title
                    if not title or title.lower() in ["results", "related searches", "need help?", "no title"]:
                        continue  # Skip non-product elements

                    # Extract price details, if available
                    price_whole = product.find_element(By.CLASS_NAME, "a-price-whole").text if product.find_elements(By.CLASS_NAME, "a-price-whole") else None
                    price_fraction = product.find_element(By.CLASS_NAME, "a-price-fraction").text if product.find_elements(By.CLASS_NAME, "a-price-fraction") else ""
                    price = f"{price_whole}.{price_fraction}" if price_whole else "No Price"  # Error handling for price

                    # Extract ASIN (Amazon Standard Identification Number)
                    asin = product.get_attribute("data-asin") if product.get_attribute("data-asin") else "No ASIN"  # Error handling for ASIN
                    
                    # Extract product image URL
                    image_element = product.find_elements(By.CSS_SELECTOR, "img.s-image")
                    image_url = image_element[0].get_attribute("src") if image_element else "No Image URL"  # Error handling for image

                    # Filter out items without proper data
                    if asin != "No ASIN" and price != "No Price":
                        all_products.append({
                            'Title': title,
                            'Price': price,
                            'ASIN': asin,
                            'Image URL': image_url
                        })

                except Exception as e:
                    print(f"Error parsing product: {e}")

            # Find the "Next" button and click it to go to the next page
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next"))
                )
                if "disabled" in next_button.get_attribute("class"):
                    print("Reached the last page.")
                    break  # Exit the loop if the "Next" button is disabled (last page)
                next_button.click()
                current_page += 1

                # Wait for the new page to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-item"))
                )
                time.sleep(random.uniform(2, 4))  # Random delay to mimic human behavior

            except Exception as e:
                print("No more pages to scrape or 'Next' button not found.")
                break

        return all_products

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the browser is closed properly
        driver.quit()

# Test the function
if __name__ == "__main__":
    search_query = 'headphones'
    max_pages = 5  # Set the number of pages you want to scrape
    products = fetch_amazon_products(search_query, max_pages=max_pages)
    
    # Print the fetched products
    if products:
        for product in products:
            print(product)
    else:
        print("No products found or failed to fetch data.")