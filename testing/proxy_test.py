import os
import sys


# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import create_driver


def test_proxy():
    driver = create_driver()

    try:
        # Query the IPinfo API endpoint instead of the public website
        driver.get("http://ipinfo.io/json")
        print(driver.page_source)  # This should print out JSON data with IP info
    except Exception as e:
        print(f"Proxy test failed: {e}")
    finally:
        driver.quit()

# Test the function
if __name__ == "__main__":
    test_proxy()