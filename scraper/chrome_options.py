from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import random

# ScraperAPI endpoint for proxies with render enabled
API_KEY = 'e0e951fc3f95783399a1c547fa055f17'
PROXY = f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001?render=true&country=us'

def set_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"--proxy-server={PROXY}")

    # Randomize user agent and window size
    ua = UserAgent()
    chrome_options.add_argument(f"user-agent={ua.random}")
    window_size = random.choice(["1920,1080", "1366,768", "1440,900", "1536,864"])
    chrome_options.add_argument(f"--window-size={window_size}")
    return chrome_options
