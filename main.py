from utils.driver_factory import create_driver
from pages.subtitle_page import SubtitlePage
from config import KTUVIT_EMAIL, KTUVIT_PASSWORD


def main():
    # Get URL from user
    url = input("Please enter the subtitle page URL: ")
    
    # Initialize the driver
    driver = create_driver()
    
    try:
        # Create page object
        page = SubtitlePage(driver)
        
        # Navigate and login
        if not page.navigate_to(url, KTUVIT_EMAIL, KTUVIT_PASSWORD):
            print("Failed to navigate to page or login. Please check your credentials.")
            return
            
        # Print available seasons
        seasons = page.get_seasons()
        if not seasons:
            print("No seasons found!")
            return
            
        # Ask user which season to download
        print("\nAvailable seasons:")
        for season in seasons:
            print(f"{season['season_name']}")
            
        season_num = input("\nEnter season number (e.g. 1 for Season 1): ")
        try:
            season_num = int(season_num)
        except ValueError:
            print("Invalid season number")
            return
            
        # Select the season
        if not page.select_season(season_num):
            print(f"Failed to select season {season_num}")
            return
            
        # Download all episodes in the season
        print(f"\nDownloading all episodes for season {season_num}...")
        downloaded_files = page.download_all_episodes_in_season(season_num)
        
        if downloaded_files:
            print(f"\nSuccessfully downloaded {len(downloaded_files)} subtitles:")
            for filename in downloaded_files:
                print(f"- {filename}")
        else:
            print("Failed to download any subtitles")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        input("Press Enter to close the browser...")
        driver.quit()


if __name__ == "__main__":
    main() 