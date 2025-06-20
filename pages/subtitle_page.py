from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
from utils.file_handler import rename_subtitle_file
from tqdm import tqdm
import time
import re
import os
import sys


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
            # Click login dropdown with explicit wait and timeout
            login_dropdown = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.LOGIN_DROPDOWN)
            )
            login_dropdown.click()
            
            # Wait for form to be visible and interactive
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "navbarLoginForm"))
            )
            
            # Fill login form with explicit waits
            email_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.LOGIN_EMAIL)
            )
            email_input.clear()
            email_input.send_keys(email)
            
            password_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.LOGIN_PASSWORD)
            )
            password_input.clear()
            password_input.send_keys(password)
            
            # Submit form with explicit wait
            login_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.LOGIN_BUTTON)
            )
            login_btn.click()
            
            # Wait for either success or failure
            try:
                # Check for success first
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(self.LOGIN_SUCCESS)
                )
                return True
            except TimeoutException:
                # Check if we're still on login form
                try:
                    self.driver.find_element(*self.LOGIN_EMAIL)
                    return False  # Still on login form means failure
                except:
                    pass  # Not finding login form might mean success
                    
                # Double check for success message
                try:
                    if self.driver.find_element(*self.LOGIN_SUCCESS):
                        return True
                except:
                    return False
            
        except Exception:
            return False

    def navigate_to(self, url, email=None, password=None):
        """Navigate to the subtitle page URL and login if credentials provided."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"\nAttempting to access page (attempt {attempt + 1}/{max_retries})")
                self.driver.get(url)
                
                # Wait for page load with shorter timeout
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                if email and password:
                    if not self.login(email, password):
                        if attempt == max_retries - 1:
                            return False
                        continue
                    
                # Verify we can access content
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(self.MAIN_CONTENT)
                    )
                    return True
                except TimeoutException:
                    if attempt == max_retries - 1:
                        return False
                    continue
                    
            except WebDriverException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

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
            return [int(btn.get_attribute('value').split()[-1]) for btn in season_buttons]
        except Exception:
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

    def select_season(self, season_number):
        """Select a specific season by its number."""
        try:
            season_buttons = self.wait.until(EC.presence_of_all_elements_located(self.SEASON_BUTTONS))
            for button in season_buttons:
                if button.get_attribute('value').strip() == f"עונה {season_number}":
                    button.click()
                    time.sleep(1)
                    return True
            return False
        except Exception:
            return False

    def select_episode(self, episode_number):
        """Select a specific episode by its number."""
        try:
            episode_buttons = self.wait.until(EC.presence_of_all_elements_located(self.EPISODE_BUTTONS))
            for button in episode_buttons:
                if button.get_attribute('value').strip() == f"פרק {episode_number}":
                    button.click()
                    time.sleep(1)
                    return True
            return False
        except Exception:
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

    def update_progress(self, current, total, episode_num, status=""):
        """Update progress in a single line."""
        bar_width = 40
        filled = int(bar_width * current / total)
        bar = "█" * filled + "░" * (bar_width - filled)
        percent = current / total * 100
        
        sys.stdout.write(f"\rProgress: {percent:3.0f}% |{bar}| {current}/{total} Episode {episode_num} {status}")
        sys.stdout.flush()

    def download_first_subtitle(self, season_num, episode_num, current, total):
        """Download the first available subtitle for a specific episode."""
        try:
            self.wait.until(EC.presence_of_element_located(self.SUBTITLE_TABLE))
            download_button = self.wait.until(EC.element_to_be_clickable(self.DOWNLOAD_BUTTON))
            if not download_button:
                return False
                
            if not self.series_name:
                self.series_name = self.get_series_name()
            
            max_download_attempts = 3
            for attempt in range(max_download_attempts):
                self.update_progress(current, total, episode_num, f"[Attempt {attempt + 1}/{max_download_attempts}]")
                
                download_button.click()
                
                success, _ = rename_subtitle_file(
                    downloads_dir=self.downloads_dir,
                    show_name=self.series_name,
                    season=season_num,
                    episode=episode_num,
                    max_retries=2,
                    retry_interval=2
                )
                
                if success:
                    self.update_progress(current, total, episode_num, "✓")
                    return True
                    
                if attempt < max_download_attempts - 1:
                    time.sleep(2)
                    download_button = self.wait.until(EC.element_to_be_clickable(self.DOWNLOAD_BUTTON))
            
            self.update_progress(current, total, episode_num, "✗")
            return False
            
        except Exception:
            self.update_progress(current, total, episode_num, "✗")
            return False

    def download_all_episodes_in_season(self, season_num):
        """Download subtitles for all episodes in the selected season."""
        downloaded_files = []
        episodes = self.get_episodes()
        
        if not episodes:
            return downloaded_files
            
        total = len(episodes)
        current = 0
        
        for episode in episodes:
            episode_num = int(re.search(r'\d+', episode['episode_name']).group())
            
            max_episode_attempts = 2
            for attempt in range(max_episode_attempts):
                if not self.select_episode(episode_num):
                    continue
                
                if self.download_first_subtitle(season_num, episode_num, current, total):
                    filename = f"{self.series_name}.S{season_num:02d}E{episode_num:02d}.srt"
                    downloaded_files.append(filename)
                    current += 1
                    break
                
                if attempt < max_episode_attempts - 1:
                    time.sleep(2)
            
            time.sleep(1)
            
        sys.stdout.write("\n")
        return downloaded_files 