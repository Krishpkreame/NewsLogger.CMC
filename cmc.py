import os
import re
import time
from exceptions import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *


class API:
    # Initialize class variables and environment variables
    def __init__(self):
        self.__account_name = "Quality Kiwi Shop Ltd"
        self.cmc_started = False  # Flag to check if CMC Markets is running
        self.cmc_loggedin = False  # Flag to check if logged into CMC Markets
        # Get Selenium URL from environment variable
        self.selenium_url = os.environ.get("SELENIUM_URL", "")
        # Get CMC username from environment variable
        self.username = os.environ.get("CMC_USERNAME", "")
        # Get CMC password from environment variable
        self.password = os.environ.get("CMC_PASSWORD", "")

        if not self.selenium_url or not self.username or not self.password:
            raise EnvironmentVariableNotFound(
                "SELENIUM_URL, CMC_USERNAME or CMC_PASSWORD environment variable not correctly")

        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument('--start-maximized')
        self.cmc_url = "https://platform.cmcmarkets.com/#/login"

    def set_keywords(self, keywords):
        self.keywords = keywords

    def close_new_windows(self):
        if not self.cmc_started or not self.cmc_loggedin:
            raise NotRunningError(
                "CMC News service is not running. Or is not logged in.")
        self.after_close_btns = self.cmc.find_elements(
            By.XPATH, '//*[@title="Close"]')
        print("Btns to close - ", len(self.after_close_btns))
        self.new_close_btns = [
            btn for btn in self.after_close_btns if btn not in self.init_close_btns]
        try:
            for closewrapper in self.new_close_btns[::-1]:
                closewrapper.find_element(By.XPATH, "*").click()
                time.sleep(1)
        except StaleElementReferenceException:
            self.after_close_btns = self.cmc.find_elements(
                By.XPATH, '//*[@title="Close"]')
            print("Buttons after fail - ", len(self.after_close_btns))
            if len(self.after_close_btns) == 1:
                pass
            else:
                raise CMCError("Could not close tabs properly")

    # TODO Redo this function
    def click_element(self, xpath_str):
        if self.cmc_started:  # If CMC Markets is running, click the element
            self.cmc.find_element(By.XPATH, xpath_str).click()
        else:  # If CMC Markets is not running, raise exception
            raise NotRunningError("CMC News service is not running.")

    # TODO Redo this function
    def type_element(self, xpath_str, typing):
        if self.cmc_started:  # If CMC Markets is running, type into the element
            self.cmc.find_element(By.XPATH, xpath_str).send_keys(typing)
        else:  # If CMC Markets is not running, raise exception
            raise NotRunningError("CMC News service is not running.")

    # TODO Redo this function
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

    # TODO Redo this function
    def start_service(self):  # Start CMC Markets
        if self.cmc_started:  # If CMC is already running, raise exception
            raise AlreadyRunningError("CMC News service is already running.")
        if not self.keywords:
            raise ValueError("No keywords found")

        print("CMC News service started.")
        # Start the browser
        self.cmc = webdriver.Remote(
            command_executor=self.selenium_url,
            options=self.browser_options)

        self.actions = ActionChains(self.cmc)

        # Go to the CMC Markets login page
        self.cmc.get(self.cmc_url)
        # Wait for the page to load and zooming out
        self.cmc.execute_script("document.body.style.zoom='50%'")
        # Set the flag to True
        self.cmc_started = True
        # Wait for the login page to load
        if self.wait_for_element('//*[@id="username"]'):
            print("Login page loaded.\n--- waiting for login...")
        else:
            raise CMCError("CMC login page failed to load.")

        # Login to CMC Markets
        self.type_element('//*[@id="username"]', self.username)
        self.type_element('//*[@id="password"]', self.password)

        # Click login button
        self.click_element("""
            /html/body/div[1]/div/cmc-login/div/section/div[1]/div[1]/form/div[4]/input
            """)

        # Wait for the account select page to load
        if self.wait_for_element("""
            /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
            """, seconds=25):
            print("CMC account tab switch needed.")
        else:
            raise CMCError("CMC account tab switch not needed.")

        # Select the account
        self.click_element("""
            /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
            """)

        self.cmc.implicitly_wait(15)
        time.sleep(3)
        # Sometimes CMC asks for account selection, if needed select the account otherwise, wait for 20 second timeout

        span_list = self.cmc.find_elements(By.TAG_NAME, "span")
        if self.__account_name not in [span.text for span in span_list]:
            raise CMCError("Account not found")

        for span in span_list:
            if self.__account_name in span.text:
                span.click()
                print("CMC account selection and account selected")
                break

        # Wait for the markets to load
        time.sleep(10)  # ! Might need to increase
        self.all_markets = self.cmc.find_elements(
            By.CLASS_NAME, "grid-tile__header")
        print("MARKETS - ", len(self.all_markets))

        # Check if all markets are found
        if not self.all_markets:
            raise CMCError("No markets found")
        elif len(self.all_markets) != len(self.keywords):
            raise ValueError("Markets found and keywords do not match")
        # Check if logged in using number of markets in list
        if len(self.all_markets) == len(self.keywords):
            # Set the flag to True
            print("CMC login successfull.")
            self.cmc_loggedin = True
            time.sleep(3)
            self.init_close_btns = self.cmc.find_elements(
                By.XPATH, '//*[@title="Close"]')
            print("INIT BTNS - ", len(self.init_close_btns))

    def stop_service(self):
        if self.cmc_started:  # If CMC is running, stop it
            try:
                time.sleep(1)
                self.cmc.quit()  # Close the browser
                self.cmc_started = False  # Set the flag to False
            except Exception as e:
                print(e)
        else:  # If CMC is not running, raise exception
            raise NotRunningError("CMC News service is not running.")

    # Get the news from CMC Markets, filter and format it
    def get_news(self):
        # Check if CMC Markets is running and logged in
        if not self.cmc_started or not self.cmc_loggedin:
            raise NotRunningError(
                "CMC News service is not running. Or is not logged in.")

        # Create filtered news list to return once done
        self.final_news = []

        # Loop over all markets
        for market in self.all_markets:
            # Open the context menu
            market.find_elements(By.TAG_NAME, "*")[0].click()
            time.sleep(3)
            self.context_menu = self.cmc.find_element(
                By.CLASS_NAME, "context-menu")
            time.sleep(1)
            # Find the news button
            self.found_news_btn = next((
                item for item in
                self.context_menu.find_elements(By.TAG_NAME, "span")
                if "Reuters News" in item.text), None)
            # If the news button is not found, raise exception, else click it
            if not self.found_news_btn:
                raise CMCError("Could Find News Button")
            self.found_news_btn.click()

            # To force the news to load, refresh the search bar
            # Find the news window search bar and click it
            self.current_news_wrapper = [
                tab for tab in
                self.cmc.find_elements(
                    By.CLASS_NAME, "window-header__tab-label")
                if tab.text != "NewsLogger"][0]
            self.current_news_wrapper.click()
            time.sleep(1)

            # Find the input field of news search bar
            self.news_search_bar = self.cmc.find_element(
                By.CLASS_NAME, "window-header__search-input"
            ).find_element(By.XPATH, "*")

            # Remove last letter and refresh the search bar
            self.news_search_bar.send_keys(Keys.ARROW_RIGHT)
            self.news_search_bar.send_keys(Keys.BACK_SPACE)
            time.sleep(3)
            self.news_search_bar.send_keys(Keys.ENTER)
            # Wait for the news to load
            time.sleep(10)  # ! Might need to increase
            # Get all the raw news
            print("Getting news...")
            self.raw_news = self.cmc.find_elements(
                By.CLASS_NAME, 'news-list-item')
            # Check if news is found
            if not self.raw_news:
                raise CMCError("No news found")

            # If any of the keywords in the news text, using list compression and generator
            print("Filtering news...")
            self.filtered_news = (
                news for news in self.raw_news
                if any(keyword in news.text for keyword in self.keywords))

            # TODO get news contect and format it
            for news_artical in list(self.filtered_news):
                # Click the news item and wait to load
                news_artical.click()
                time.sleep(2)

                # Get the news title, datetime, content and keyword
                self.news_title = self.cmc.find_element(
                    By.XPATH, '//*[@data-testid="news-content-title"]').text
                self.news_datetime = self.cmc.find_element(
                    By.XPATH, '//*[@data-testid="news-content-date"]').text
                self.unformatted_news_content = self.cmc.find_element(
                    By.XPATH, '//*[@data-testid="news-content"]').text
                self.keyword_in_title = [
                    kw for kw in self.keywords if kw in self.news_title][0]

                # Format the news content
                self.regex_for_news_content = re.search(
                    r"Pivot:(.*?)---", self.unformatted_news_content, re.DOTALL)
                if self.regex_for_news_content:
                    self.news_content = f"Pivot: {self.regex_for_news_content.group(1).strip()}"
                else:
                    raise CMCError(
                        "News content format error, incorrect news found")

                # Add the news item to the filtered news dict, with the unique datetime as the key
                self.final_news.append({
                    "keyword": self.keyword_in_title,
                    "datetime": self.news_datetime,
                    "title": self.news_title,
                    "content": self.news_content
                })

            time.sleep(3)
            self.close_new_windows()
            time.sleep(3)
        return self.final_news
