from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os


def create_driver():
    """Create and configure Chrome WebDriver."""
    options = Options()
    
    # Headless mode
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    
    # Suppress unnecessary logging
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Improve performance
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    
    # Additional headless optimizations
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-notifications')
    
    # Set download directory
    downloads_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads'))
    os.makedirs(downloads_dir, exist_ok=True)
    
    prefs = {
        'download.default_directory': downloads_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
        'profile.default_content_settings.popups': 0,
        'profile.default_content_setting_values.automatic_downloads': 1
    }
    options.add_experimental_option('prefs', prefs)
    
    # Create and return driver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver 