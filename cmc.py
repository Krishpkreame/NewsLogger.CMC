# Environment variables and datetime
import os
from datetime import datetime
import time
# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By

# For waiting for web elements to load instead of time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class API:
    # Initialize class variables and environment variables
    def __init__(self, __keywords=None):
        self.__account_name = "Quality Kiwi Shop Ltd"
        self.cmc_started = False  # Flag to check if CMC Markets is running
        self.cmc_loggedin = False  # Flag to check if logged into CMC Markets
        # Get Selenium URL from environment variable
        self.selenium_url = os.environ.get("SELENIUM_URL", "")
        # Get CMC username from environment variable
        self.username = os.environ.get("CMC_USERNAME", "")
        # Get CMC password from environment variable
        self.password = os.environ.get("CMC_PASSWORD", "")

        self.browser_options = webdriver.EdgeOptions()
        self.browser_options.add_argument('--start-maximized')
        self.cmc_url = "https://platform.cmcmarkets.com/#/login"

        # List of keywords for news filtering
        self.keywords = __keywords

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
            time.sleep(3)
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
                options=self.browser_options)

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

            try:
                # Wait for the account select page to load
                if self.wait_for_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
                    """, seconds=25):
                    print("CMC account tab switch needed.")
                else:
                    raise TimeoutError
                # Select the account
                self.click_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
                    """)
            except TimeoutError:
                print("CMC account tab switch not needed.")
                pass

            self.cmc.implicitly_wait(15)
            time.sleep(3)
            # Sometimes CMC asks for account selection, if needed select the account otherwise, wait for 20 second timeout
            try:
                # Wait for the account select page to load
                span_list = self.cmc.find_elements(By.TAG_NAME, "span")
                for span in span_list:
                    if self.__account_name in span.text:
                        span.click()
                        print("CMC account selection and account selected")
                        raise ValueError
                raise TimeoutError("Account not found")
            except ValueError:
                pass

            # Check if the main page has loaded by checking if there are more than 501 news items
            # if not wait and try again
            for time_ran in range(10):
                if self.cmc_loggedin == True:  # If the flag is already True, break the loop
                    break
                # Wait for the main page to load (cant use wait_for_element because the elements are unique)
                time.sleep(30)
                if len(self.cmc.find_elements(By.CLASS_NAME, 'news-list-item')) > 399:
                    print("The main page news loaded.")
                    self.cmc_loggedin = True  # Set the flag to True
                else:
                    print(
                        "The main page news failed to load, trying again. attempt: " + str(time_ran))
            if not self.cmc_loggedin:
                raise Exception("CMC News failed to load in.")
        else:
            # Raise exception if CMC is already running
            raise Exception("CMC News service is already running.")

    def stop_service(self):
        if self.cmc_started:  # If CMC is running, stop it
            try:
                time.sleep(1)
                self.cmc.quit()  # Close the browser
                self.cmc_started = False  # Set the flag to False
            except Exception as e:
                print(e)
        else:  # If CMC is not running, raise exception
            raise Exception("CMC News service is not running.")

    # Get the news from CMC Markets, filter and format it
    def get_news(self):
        self.filtered_news = []

        # Get the close buttons before opening anything so see the difference
        close_buttons_before = self.cmc.find_elements(
            By.CLASS_NAME, 'window-header__action-button ')

        if self.cmc_started and self.cmc_loggedin:  # If CMC is running and logged in, get the news
            # Get the raw news items using class name
            raw_news = self.cmc.find_elements(By.CLASS_NAME, 'news-list-item')
            print(f"Number of news items: {len(raw_news)}\nGetting news...")
            self.news_counter = 0
            for unformatted in raw_news:
                self.news_counter += 1
                # Get the 2 children of the news item, the title and the datetime as a list
                self.news_item = unformatted.find_elements(By.XPATH, '*')

                # Print the last 33 characters of the news item (time and end of title from debug)
                print(str(self.news_counter) + "/" + str(len(raw_news)), unformatted.text.replace(
                    "\n", " ----- "), sep=": ")

                # If the title contains any of the keywords, add it to the filtered news
                if any(keyword in self.news_item[0].text for keyword in self.keywords):
                    # Get the title and datetime from the list
                    self.news_item_title = self.news_item[0].text
                    self.news_item_datetime = self.news_item[1].text

                    # Get the market from the title
                    self.news_item_market = [
                        k for k in self.keywords if k in self.news_item_title][0]

                    # Click the news item to load the content
                    try:
                        unformatted.click()
                        # Wait for the news content to load
                        self.cmc.implicitly_wait(3)
                        time.sleep(3)
                        # Get the news contents
                        temp1 = self.cmc.find_element(
                            By.CLASS_NAME, 'news-contents').text
                        temp1 = temp1.split("---")[0]
                        self.news_item_content = temp1.split("Pivot: ")[-1]
                        # Wait before closing the news
                        self.cmc.implicitly_wait(2)
                        # Get the close buttons after opening the news
                        close_buttons_after = self.cmc.find_elements(
                            By.CLASS_NAME, 'window-header__action-button ')

                        # Find all buttons that were not there before opening the news
                        try:  # Sometimes the button is not found or clickable, so catch exception
                            for crnt_button in list(set(close_buttons_before) ^ set(close_buttons_after)):
                                # Do 2 children down, (workaround because of bug in selenium)
                                temp = crnt_button.find_element(
                                    By.XPATH, "*").find_element(
                                    By.XPATH, "*")
                                # If the button is the close button, click it and wait
                                if ("close" in str(temp.get_attribute("class"))):
                                    temp.click()
                                    self.cmc.implicitly_wait(3)
                        except:
                            pass

                        print(f"News Context loaded. \n--- {unformatted.text}")
                    except Exception as e:  # If the news content failed to load, catch exception
                        self.news_item_content = "Placeholder"
                        print(
                            f"News Context failed to load.\n--- {unformatted.text}")

                    # Add the news item to the filtered news dict, with the unique datetime as the key
                    self.filtered_news.append({
                        "market": self.news_item_market,
                        "datetime": self.news_item_datetime,
                        "title": self.news_item_title,
                        "content": self.news_item_content
                    })
        else:
            # If CMC is not running or logged in, raise exception
            raise Exception(
                "CMC News service is not running. Or is not logged in.")
        return self.filtered_news
