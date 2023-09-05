# Environment variables and datetime
import os
from datetime import datetime

# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By

# For waiting for web elements to load instead of time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class API:
    # Initialize class variables and environment variables
    def __init__(self):
        self.cmc_started = False  # Flag to check if CMC Markets is running
        self.cmc_loggedin = False  # Flag to check if logged into CMC Markets
        # Get Selenium URL from environment variable
        self.selenium_url = os.environ.get("SELENIUM_URL", "")
        # Get CMC username from environment variable
        self.username = os.environ.get("CMC_USERNAME", "")
        # Get CMC password from environment variable
        self.password = os.environ.get("CMC_PASSWORD", "")

        self.firefox_options = webdriver.FirefoxOptions()
        self.cmc_url = "https://platform.cmcmarkets.com/#/login"

        # ! Use database later for keywords
        self.keywords = [      # List of keywords for news filtering
            "S&P-ASX 200 ST",  # Australia 200 - Cash
            "FTSE 100 MT",     # UK 100 - Cash
            "Dow Jones ST",    # US 30 - Cash
            "Hang Seng ST",    # HONG KONG 50 - Cash
            "Nasdaq 100 ST"    # US NDAQ 100 - Cash
        ]

    # Use //*[@id="#####"] for ID element search
    def click_element(self, xpath_str):
        if self.cmc_started:  # If CMC Markets is running, click the element
            self.cmc.find_element(By.XPATH, xpath_str).click()
        else:  # If CMC Markets is not running, raise exception
            raise Exception("CMC News service is not running.")

    # Use //*[@id="#####"] for ID element search
    def type_element(self, xpath_str, typing):
        if self.cmc_started:  # If CMC Markets is running, type into the element
            self.cmc.find_element(By.XPATH, xpath_str).send_keys(typing)
        else:  # If CMC Markets is not running, raise exception
            raise Exception("CMC News service is not running.")

    # Use //*[@id="#####"] for ID element search
    def wait_for_element(self, xpath_str, seconds=60):
        try:
            # Wait for the element to load (default timeout is 60 seconds)
            WebDriverWait(self.cmc, seconds).until(
                EC.presence_of_element_located((By.XPATH, xpath_str)))
            self.cmc.implicitly_wait(3)
            return True
        except Exception as e:  # If the element does not load, catch exception
            print(e)
            return False

    def start_service(self):  # Start CMC Markets
        if not self.cmc_started:  # If CMC is not running, start it
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

            # Wait for the login page to load
            if self.wait_for_element('//*[@id="username"]'):
                print("Login page loaded.\n--- waiting for selection...")
            else:
                raise Exception("CMC login page failed to load.")

            # Login to CMC Markets
            self.type_element('//*[@id="username"]', self.username)
            self.type_element('//*[@id="password"]', self.password)

            # Click login button
            self.click_element("""
                /html/body/div[1]/div/cmc-login/div/section/div[1]/div[1]/form/div[4]/input
                """)

            # Sometimes CMC asks for account selection, if needed select the account otherwise, wait for 20 second timeout
            try:
                # Wait for the account select page to load
                if self.wait_for_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[2]/div[2]/div[2]/div[4]/span
                    """, seconds=15):  # ! This is a placeholder - CHANGE TO 20 or higher for production
                    print("CMC account selection page needed.")
                else:
                    raise TimeoutError
                # Select the account
                self.click_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[2]/div[2]/div[2]/div[4]/span
                    """)
            except TimeoutError:
                print("CMC account selection page not needed.")
                pass

            # Wait for the main page to load (cant use wait_for_element because the elements are unique)
            # ! This is a placeholder - CHANGE TO 45 or higher for production
            self.cmc.implicitly_wait(15)
            # ! This is a placeholder - CHANGE TO 45 or higher for production

            # Check if the main page has loaded by checking if there are more than 10 news items
            if len(self.cmc.find_elements(By.CLASS_NAME, 'news-list-item')) > 10:
                print("The main page news loaded.")
                self.cmc_loggedin = True  # Set the flag to True
            else:
                raise Exception(
                    f"CMC main page failed to load.")  # Raise exception if the main page failed to load
        else:
            # Raise exception if CMC is already running
            raise Exception("CMC News service is already running.")

    def stop_service(self):
        if self.cmc_started:  # If CMC is running, stop it
            try:
                self.cmc.quit()  # Close the browser
                self.cmc_started = False  # Set the flag to False
            except Exception as e:
                print(e)
        else:  # If CMC is not running, raise exception
            raise Exception("CMC News service is not running.")

    # Get the news from CMC Markets, filter and format it
    def get_news(self):
        self.filtered_news = []

        if self.cmc_started and self.cmc_loggedin:  # If CMC is running and logged in, get the news
            # Get the raw news items using class name
            raw_news = self.cmc.find_elements(By.CLASS_NAME, 'news-list-item')
            print(f"Number of news items: {len(raw_news)}\nGetting news...")
            for unformatted in raw_news:
                # Get the 2 children of the news item, the title and the datetime as a list
                self.news_item = unformatted.find_elements(By.XPATH, '*')

                print(unformatted.text[-45:])  # ! REMOVE THIS LATER

                # If the title contains any of the keywords, add it to the filtered news
                if any(keyword in self.news_item[0].text for keyword in self.keywords):
                    # Get the title and datetime from the list
                    self.news_item_title = self.news_item[0].text
                    self.news_item_datetime = self.news_item[1].text

                    # Click the news item to load the content
                    try:
                        unformatted.click()
                        # Wait for the news content to load
                        self.cmc.implicitly_wait(2)
                        # Get the news content
                        self.news_item_content = self.cmc.find_element(
                            By.CLASS_NAME, 'news-contents').text
                        print(
                            f"News Context loaded. \n--- {unformatted.text}")
                    except Exception as e:  # If the news content failed to load, catch exception
                        self.news_item_content = "Placeholder"
                        print(
                            f"News Context failed to load.\n--- {unformatted.text}")

                    # Add the news item to the filtered news dict, with the unique datetime as the key
                    self.filtered_news.append({
                        "datetime": self.news_item_datetime,
                        "title": self.news_item_title,
                        "content": self.news_item_content
                    })
        else:
            # If CMC is not running or logged in, raise exception
            raise Exception(
                "CMC News service is not running. Or is not logged in.")
        return self.filtered_news
