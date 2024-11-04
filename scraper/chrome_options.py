#Developed with the help of ChatGPT 4o

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wire_webdriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import random


# Func: Configures and returns Chrome options
# Returns: Configured chrome_options object
def set_chrome_options():
    chrome_options = Options()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    ua = UserAgent()
    chrome_options.add_argument(f"user-agent={ua.random}")

    window_size = random.choice(["1920,1080", "1366,768", "1440,900", "1536,864"])
    chrome_options.add_argument(f"--window-size={window_size}")

    # Disable image loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


# Func: Creates and returns a new WebDriver instance using Selenium Wire for proxy configuration.
# Returns: A configured WebDriver instance.
def create_driver():

    # BrightData proxy credentials
    BRIGHTDATA_USERNAME = ""
    BRIGHTDATA_PASSWORD = ""
    BRIGHTDATA_ENDPOINT = "brd.superproxy.io:22225"
    proxy_url = f'http://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@{BRIGHTDATA_ENDPOINT}'

    # Configure proxy options
    PROXY_OPTIONS = {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
        }
    }
    
    # Initialize Chrome WebDriver with proxy and custom Chrome options
    chrome_options = set_chrome_options()
    return wire_webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options, 
        seleniumwire_options=PROXY_OPTIONS
    )
