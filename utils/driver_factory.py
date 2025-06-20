from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os


def setup_chrome_options():
    """Setup Chrome options for better compatibility and automation."""
    options = ChromeOptions()
    
    # Set download directory to project's downloads folder - using absolute path
    downloads_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads'))
    os.makedirs(downloads_dir, exist_ok=True)
    print(f"Setting download directory to: {downloads_dir}")
    
    prefs = {
        "download.default_directory": downloads_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,  # Don't open PDFs in browser
        "profile.default_content_settings.popups": 0,  # Disable popup blocker
        "profile.default_content_setting_values.automatic_downloads": 1  # Allow multiple downloads
    }
    options.add_experimental_option("prefs", prefs)
    
    # Bypass SSL errors
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    
    # Additional options for better compatibility
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_argument('--safebrowsing-disable-download-protection')  # Disable safe browsing for downloads
    
    # Add user agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    return options


def create_driver():
    """Create and return a configured Chrome WebDriver instance."""
    options = setup_chrome_options()
    driver = webdriver.Chrome(options=options)
    return driver 