from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
import time
import re
import os


class SubtitlePage(BasePage):
    # Locators
    LOGIN_DROPDOWN = (By.ID, "navbar_loginMenu")
    LOGIN_EMAIL = (By.ID, "navbarlogin_tb_loginEmail")
    LOGIN_PASSWORD = (By.ID, "navbarlogin_tb_loginPassword")
    LOGIN_BUTTON = (By.ID, "navbarlogin_button_doLogin")
    LOGIN_SUCCESS = (By.XPATH, "//a[contains(@class, 'dropdown-toggle') and contains(text(), 'שלום')]")
    MAIN_CONTENT = (By.XPATH, "//div[@class='col-md-12']//div[@class='col-md-8']")
    SERIES_TITLE = (By.ID, "FilmSecondaryTitle")
    
    # Season and episode selectors
    SEASON_BUTTONS = (By.CSS_SELECTOR, "input.btn-success[data-season-id]")
    EPISODE_BUTTONS = (By.CSS_SELECTOR, "input.btn-success[data-episode-id]")
    
    # Subtitle list and download selectors
    SUBTITLE_TABLE = (By.ID, "subtitlesList")
    DOWNLOAD_BUTTON = (By.XPATH, "(//a[@title='הורדה ישירה'])[1]")
    SUBTITLE_NAME = (By.CSS_SELECTOR, "td.ltr.text-right div")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(text(), 'ההורדה נכשלה')]")

    def __init__(self, driver):
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 10)
        self.series_name = None
        
        # Create downloads directory using absolute path
        self.downloads_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads'))
        os.makedirs(self.downloads_dir, exist_ok=True)
        print(f"Downloads directory: {self.downloads_dir}")

    def login(self, email, password):
        """Login to Ktuvit.me"""
        try:
            print("\nAttempting to log in...")
            
            # Click login dropdown to open form
            login_dropdown = self.wait.until(EC.element_to_be_clickable(self.LOGIN_DROPDOWN))
            login_dropdown.click()
            time.sleep(1)  # Wait for dropdown animation
            
            # Fill login form
            email_input = self.wait.until(EC.presence_of_element_located(self.LOGIN_EMAIL))
            email_input.clear()  # Clear any existing value
            email_input.send_keys(email)
            
            password_input = self.driver.find_element(*self.LOGIN_PASSWORD)
            password_input.clear()  # Clear any existing value
            password_input.send_keys(password)
            
            # Submit form
            login_btn = self.driver.find_element(*self.LOGIN_BUTTON)
            login_btn.click()
            
            # Wait for page reload and verify login success
            try:
                self.wait.until(EC.presence_of_element_located(self.LOGIN_SUCCESS))
                print("Login successful - Found welcome message")
                return True
            except TimeoutException:
                print("Login failed - Welcome message not found")
                return False
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def navigate_to(self, url, email=None, password=None):
        """Navigate to the subtitle page URL and login if credentials provided."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"\nAttempting to navigate to page (attempt {attempt + 1}/{max_retries})...")
                self.driver.get(url)
                time.sleep(3)  # Initial wait for JavaScript
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                
                if email and password:
                    if not self.login(email, password):
                        print("Failed to login, cannot proceed with season listing")
                        return False
                    # After successful login, wait a bit for page to stabilize
                    time.sleep(2)
                
                return True
            except WebDriverException as e:
                print(f"Navigation error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print("Failed to navigate after all retries.")
                    raise

    def get_main_content(self):
        """Get the main content div containing season buttons."""
        try:
            print("\nLooking for main content...")
            element = self.wait.until(
                EC.presence_of_element_located(self.MAIN_CONTENT)
            )
            if element:
                print("Main content found.")
                return element
            print("Main content not found.")
            return None
        except TimeoutException:
            print("Timeout while looking for main content.")
            self.debug_page_content()
            return None

    def get_seasons(self):
        """Get all available seasons"""
        try:
            season_buttons = self.wait.until(EC.presence_of_all_elements_located(self.SEASON_BUTTONS))
            seasons = []
            
            for button in season_buttons:
                season_id = button.get_attribute('data-season-id')
                season_name = button.get_attribute('value')
                seasons.append({
                    'season_id': season_id,
                    'season_name': season_name
                })
                print(f"Season ID: {season_id}, Name: {season_name}")
                
            return seasons
            
        except Exception as e:
            print(f"Error getting seasons: {str(e)}")
            return []

    def get_episodes(self):
        """Get all available episodes for the current season"""
        try:
            episode_buttons = self.wait.until(EC.presence_of_all_elements_located(self.EPISODE_BUTTONS))
            episodes = []
            
            for button in episode_buttons:
                episode_id = button.get_attribute('data-episode-id')
                episode_name = button.get_attribute('value')
                episodes.append({
                    'episode_id': episode_id,
                    'episode_name': episode_name
                })
                
            return episodes
            
        except Exception as e:
            print(f"Error getting episodes: {str(e)}")
            return []

    def debug_page_content(self):
        """Print debug information about the page content."""
        print("\nDEBUG INFO:")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Check for specific elements
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            print("\nPage contains text:", "Yes" if body_text.strip() else "No")
            
            # Check login status
            welcome_msg = self.driver.find_elements(*self.LOGIN_SUCCESS)
            if welcome_msg:
                print("User is logged in - Found welcome message")
            else:
                print("User is not logged in - No welcome message found")
                
            if "עונה" in body_text:
                print("Found season text on page")
        except Exception as e:
            print(f"Error during debug: {str(e)}")

    def list_seasons(self):
        """List all available seasons with their IDs and names."""
        seasons = []
        buttons = self.get_seasons()
        
        for btn in buttons:
            try:
                season_id = btn['season_id']
                season_name = btn['season_name']
                if season_id and season_name:
                    seasons.append({
                        'season_id': season_id,
                        'season_name': season_name
                    })
                    print(f"Found season: ID={season_id}, Name={season_name}")
            except Exception as e:
                print(f"Error processing season button: {str(e)}")
                continue
        
        return seasons

    def print_seasons(self):
        """Print all available seasons in a formatted way."""
        print("\nSearching for available seasons...")
        seasons = self.list_seasons()
        if not seasons:
            print("\nNo seasons found. This could be because:")
            print("1. The page hasn't loaded completely")
            print("2. The content is protected or requires authentication")
            print("3. The page structure is different than expected")
            return
        
        print("\nAvailable seasons:")
        for season in seasons:
            print(f"Season ID: {season['season_id']}, Name: {season['season_name']}")

    def select_season(self, season_number):
        """Select a specific season by its number."""
        try:
            season_buttons = self.wait.until(EC.presence_of_all_elements_located(self.SEASON_BUTTONS))
            for button in season_buttons:
                if button.get_attribute('value').strip() == f"עונה {season_number}":
                    print(f"Clicking season {season_number} button")
                    button.click()
                    time.sleep(1)  # Wait for episode list to update
                    return True
            print(f"Season {season_number} not found")
            return False
        except Exception as e:
            print(f"Error selecting season: {str(e)}")
            return False

    def select_episode(self, episode_number):
        """Select a specific episode by its number."""
        try:
            episode_buttons = self.wait.until(EC.presence_of_all_elements_located(self.EPISODE_BUTTONS))
            for button in episode_buttons:
                if button.get_attribute('value').strip() == f"פרק {episode_number}":
                    print(f"Clicking episode {episode_number} button")
                    button.click()
                    time.sleep(1)  # Wait for subtitle list to update
                    return True
            print(f"Episode {episode_number} not found")
            return False
        except Exception as e:
            print(f"Error selecting episode: {str(e)}")
            return False

    def get_subtitle_info(self):
        """Get information about available subtitles."""
        try:
            subtitle_table = self.wait.until(EC.presence_of_element_located(self.SUBTITLE_TABLE))
            download_buttons = subtitle_table.find_elements(*self.DOWNLOAD_BUTTON)
            subtitle_names = subtitle_table.find_elements(*self.SUBTITLE_NAME)
            
            subtitles = []
            for name_elem, download_elem in zip(subtitle_names, download_buttons):
                subtitles.append({
                    'name': name_elem.text.strip().split('\n')[0],
                    'download_id': download_elem.get_attribute('data-subtitle-id')
                })
            return subtitles
        except Exception as e:
            print(f"Error getting subtitle info: {str(e)}")
            return []

    def download_subtitle(self, subtitle_id, season_num, episode_num):
        """Download a subtitle and return its suggested filename."""
        try:
            # Find and click the download button with matching subtitle_id
            download_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[data-subtitle-id='{subtitle_id}']"))
            )
            download_button.click()
            
            # Generate proper filename
            series_name = self.get_series_name()
            series_name = ''.join(word.capitalize() for word in series_name.split())
            filename = f"{series_name}S{season_num:02d}E{episode_num:02d}-sub.srt"
            
            print(f"Subtitle downloaded, suggested filename: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error downloading subtitle: {str(e)}")
            return None

    def get_series_name(self):
        """Get the series name from the page title."""
        if not self.series_name:
            try:
                title_elem = self.wait.until(EC.presence_of_element_located(self.SERIES_TITLE))
                # Format as The.Big.Bang.Theory
                self.series_name = title_elem.text.strip().replace(' ', '.')
            except:
                self.series_name = "Unknown.Series"
        return self.series_name

    def download_with_retry(self, download_button, filename, max_retries=3, retry_interval=3):
        """Attempt to download with retries on failure."""
        for attempt in range(max_retries):
            try:
                # Click download
                download_button.click()
                time.sleep(retry_interval)  # Wait for download to start/error to appear
                
                # Check for error message
                error_elements = self.driver.find_elements(*self.ERROR_MESSAGE)
                if not error_elements:
                    print(f"Download successful on attempt {attempt + 1}")
                    return True
                    
                print(f"Download failed on attempt {attempt + 1}, retrying...")
                if attempt < max_retries - 1:  # Don't wait on last attempt
                    time.sleep(retry_interval)
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:  # Don't wait on last attempt
                    time.sleep(retry_interval)
                
        print(f"Failed to download after {max_retries} attempts")
        return False

    def download_first_subtitle(self, season_num, episode_num):
        """Download the first available subtitle for a given season/episode."""
        try:
            # Wait for download button to be clickable
            download_button = self.wait.until(
                EC.element_to_be_clickable(self.DOWNLOAD_BUTTON)
            )
            
            # Generate proper filename (e.g., The.Big.Bang.Theory.S11E09.srt)
            series_name = self.get_series_name()
            filename = f"{series_name}.S{season_num:02d}E{episode_num:02d}.srt"
            filepath = os.path.join(self.downloads_dir, filename)
            
            print(f"Attempting to download: {filename}")
            
            # Try download with retry mechanism
            if self.download_with_retry(download_button, filename):
                print(f"Successfully downloaded: {filename}")
                return filename
            else:
                print(f"Failed to download: {filename}")
                return None
            
        except Exception as e:
            print(f"Error downloading subtitle: {str(e)}")
            return None

    def download_all_episodes_in_season(self, season_num):
        """Download subtitles for all episodes in a season."""
        try:
            # Get all episode buttons
            episode_buttons = self.wait.until(EC.presence_of_all_elements_located(self.EPISODE_BUTTONS))
            total_episodes = len(episode_buttons)
            print(f"\nFound {total_episodes} episodes in season {season_num}")
            
            downloaded_files = []
            for idx, button in enumerate(episode_buttons, 1):
                try:
                    # Get episode number from button value (e.g. "פרק 1" -> 1)
                    episode_text = button.get_attribute('value').strip()
                    episode_num = int(''.join(filter(str.isdigit, episode_text)))
                    
                    print(f"\nProcessing episode {episode_num} ({idx}/{total_episodes})")
                    
                    # Click the episode button
                    button.click()
                    time.sleep(1)  # Wait for subtitle list to update
                    
                    # Download the subtitle
                    filename = self.download_first_subtitle(season_num, episode_num)
                    if filename:
                        downloaded_files.append(filename)
                    
                    time.sleep(1)  # Wait between episodes
                    
                except Exception as e:
                    print(f"Error processing episode {idx}: {str(e)}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            print(f"Error downloading season: {str(e)}")
            return [] 