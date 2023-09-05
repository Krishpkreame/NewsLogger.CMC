import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class API:
    def __init__(self):
        self.cmc_started = False
        self.selenium_url = os.environ.get("SELENIUM_URL", "")
        self.username = os.environ.get("CMC_USERNAME", "")
        self.password = os.environ.get("CMC_PASSWORD", "")

        self.firefox_options = webdriver.FirefoxOptions()
        self.cmc_url = "https://platform.cmcmarkets.com/#/login"
        self.keywords = [  # ! This is a placeholder list - SQL database will be used instead
            "S&P-ASX 200 ST",  # Australia 200 - Cash
            "_placeholder",  # UK 100 - Cash
            "_placeholder",  # US 30 - Cash
            "_placeholder",  # HONG KONG 50 - Cash
            "_placeholder",  # US NDAQ 100 - Cash
            "_placeholder"  # Crude Oil Brent - Cash
        ]

    def click_element(self, xpath_str):  # Use //*[@id="#####"] for ID
        if not self.cmc_started:  # Is CMC Markets running?
            print("CMC News service is not running.")
            return

        # If CMC Markets is running, click the element
        self.cmc.find_element(
            By.XPATH,
            xpath_str
        ).click()

    def type_element(self, xpath_str, typing):  # Use //*[@id="#####"] for ID
        if not self.cmc_started:  # Is CMC Markets running?
            print("CMC News service is not running.")
            return

        # If CMC Markets is running, type into the element
        self.cmc.find_element(
            By.XPATH,
            xpath_str
        ).send_keys(typing)

    def wait_for_element(self, xpath_str):
        try:
            WebDriverWait(self.cmc, 60).until(
                EC.presence_of_element_located((By.XPATH, xpath_str)))
            self.cmc.implicitly_wait(3)
            return True
        except Exception as e:
            print(e)
            return False

    def start_service(self):
        if not self.cmc_started:
            print("CMC News service started.")
            self.cmc_started = True

            # Start the browser
            self.cmc = webdriver.Remote(
                command_executor=self.selenium_url,
                options=self.firefox_options)
            # Go to the CMC Markets login page
            self.cmc.get(self.cmc_url)
            # Wait for the page to load and zooming out
            self.cmc.execute_script("document.body.style.zoom='50%'")

            # Wait for the page to load
            self.wait_for_element('//*[@id="username"]')

            # Login to CMC Markets
            self.type_element('//*[@id="username"]', self.username)
            self.type_element('//*[@id="password"]', self.password)
            self.click_element(
                '/html/body/div[1]/div/cmc-login/div/section/div[1]/div[1]/form/div[4]/input')  # Login button

            # Wait for the page to load
            if self.wait_for_element('/html/body/div[1]/div/main/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]/div[3]/div/div/section/div[1]/section/header/a/svg'):
                print("CMC Markets logged in.")
            else:
                raise Exception("CMC Markets login failed.")

            input("TESTING")  # ! ________REMOVE THIS LINE________
        else:
            raise Exception("CMC News service is already running.")

    def stop_service(self):
        if self.cmc_started:
            try:
                self.cmc.quit()
                self.cmc_started = False
            except Exception as e:
                print(e)
        else:
            raise Exception("CMC News service is not running.")

    def get_news(self):
        print("Fetching the latest news...")
