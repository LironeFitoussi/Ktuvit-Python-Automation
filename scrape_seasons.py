import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import time


def list_seasons(url):
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(2)  # Wait for JS to render if needed

        # Find the main element
        try:
            inner_div = driver.find_element(By.XPATH, "//div[@class='col-md-12']//div[@class='col-md-8']")
        except NoSuchElementException:
            print('Main content div not found.')
            return

        # Find all season buttons by XPath
        season_buttons = inner_div.find_elements(By.XPATH, ".//button[contains(@class, 'btn-success') and @data-season-id]")
        if not season_buttons:
            print('No season buttons found.')
            return

        print('Available seasons:')
        for btn in season_buttons:
            season_id = btn.get_attribute('data-season-id')
            season_name = btn.text.strip()
            print(f'Season ID: {season_id}, Name: {season_name}')
    finally:
        driver.quit()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python scrape_seasons.py <URL>')
        sys.exit(1)
    url = sys.argv[1]
    list_seasons(url) 