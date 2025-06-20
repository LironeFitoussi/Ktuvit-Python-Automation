from utils.driver_factory import create_driver
from pages.subtitle_page import SubtitlePage
from config import KTUVIT_EMAIL, KTUVIT_PASSWORD


def main():
    url = input("URL: ")
    driver = create_driver()
    
    try:
        page = SubtitlePage(driver)
        if not page.navigate_to(url, KTUVIT_EMAIL, KTUVIT_PASSWORD):
            print("❌ Access failed")
            return
            
        seasons = page.get_seasons()
        if not seasons:
            print("❌ No seasons")
            return
            
        print(f"Seasons: {', '.join(str(s) for s in sorted(seasons))}")
            
        try:
            season_num = int(input("Season: "))
            if season_num not in seasons:
                print("❌ Invalid season")
                return
        except ValueError:
            print("❌ Invalid input")
            return
            
        if not page.select_season(season_num):
            print("❌ Season selection failed")
            return
            
        downloaded = page.download_all_episodes_in_season(season_num)
        
        if downloaded:
            print(f"✓ {len(downloaded)} subtitles")
        else:
            print("❌ Download failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main() 