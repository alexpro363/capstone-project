from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wire_webdriver  # Import Selenium Wire
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import random


def set_chrome_options():
    chrome_options = Options()

    # Ensure headless mode is enabled to avoid browser popping up
    chrome_options.add_argument("--headless")

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Randomize user agent and window size
    ua = UserAgent()
    chrome_options.add_argument(f"user-agent={ua.random}")
    window_size = random.choice(["1920,1080", "1366,768", "1440,900", "1536,864"])
    chrome_options.add_argument(f"--window-size={window_size}")

    # Disable extensions and popup-blocker
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    return chrome_options

def create_driver():
    """Creates a new WebDriver instance using Selenium Wire for brightdata proxy."""

    BRIGHTDATA_USERNAME = "brd-customer-hl_363c581a-zone-residential_proxy1-country-us"
    BRIGHTDATA_PASSWORD = "len1mr14ww8c"
    BRIGHTDATA_ENDPOINT = "brd.superproxy.io:22225"
    proxy_url = f'http://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@{BRIGHTDATA_ENDPOINT}'

    PROXY_OPTIONS = {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
        }
    }
    
    chrome_options = set_chrome_options()
    return wire_webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options, 
        seleniumwire_options=PROXY_OPTIONS
    )