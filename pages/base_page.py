from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def find_element(self, by, value):
        try:
            return self.wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            print(f"Element with locator ({by}, {value}) not found within the timeout period.")
            return None

    def find_elements(self, by, value):
        try:
            return self.wait.until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            print(f"Elements with locator ({by}, {value}) not found within the timeout period.")
            return []

    def click(self, by, value):
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def send_keys(self, by, value, text):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        element = self.find_element(by, value)
        return element.text

    def is_element_visible(self, by, value):
        try:
            self.wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url 