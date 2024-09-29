import os
import pickle
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

class XComLoginAutomation:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies_file_path = "cookies.pkl"
        self.local_storage_file_path = "local_storage.pkl"
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def load_cookies(self):
        if os.path.exists(self.cookies_file_path):
            self.driver.get("https://x.com")
            with open(self.cookies_file_path, "rb") as cookies_file:
                cookies = pickle.load(cookies_file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(3)

    def load_local_storage(self):
        if os.path.exists(self.local_storage_file_path):
            with open(self.local_storage_file_path, "rb") as storage_file:
                local_storage = pickle.load(storage_file)
                for key, value in local_storage.items():
                    self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
            self.driver.refresh()

    def save_cookies(self):
        with open(self.cookies_file_path, "wb") as cookies_file:
            pickle.dump(self.driver.get_cookies(), cookies_file)

    def save_local_storage(self):
        local_storage = self.driver.execute_script("return window.localStorage;")
        with open(self.local_storage_file_path, "wb") as storage_file:
            pickle.dump(local_storage, storage_file)

    def login(self):
        self.driver.get("https://x.com/i/flow/login")
        time.sleep(5)
        username_field = self.driver.find_element(By.NAME, "text")
        username_field.send_keys(self.username)
        username_field.send_keys(Keys.RETURN)
        time.sleep(3)
        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

    def perform_login(self):
        self.load_cookies()
        if os.path.exists(self.cookies_file_path):
            self.load_local_storage()
        else:
            self.login()
            self.save_cookies()
            self.save_local_storage()

    def perform_post_search(self, message):
        self.driver.get("https://x.com/search?q=%24SOL&src=typed_query&f=live") #change this to query url where you see posts on specific topic
        time.sleep(5)

        def process_posts():
            try:
                container = self.driver.find_element(By.XPATH,
                                                     '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div')
                divs = container.find_elements(By.XPATH, './div')
                time.sleep(2)

                for div in divs:
                    time.sleep(random.randint(1,5))
                    try:
                        button_like = div.find_element(By.XPATH,'./div/div/article/div/div/div[2]/div[2]/div[4]/div/div/div[3]/button')
                        button_like.click()
                        time.sleep(2)
                        button_repost = div.find_element(By.XPATH,'./div/div/article/div/div/div[2]/div[2]/div[4]/div/div/div[2]/button')
                        button_repost.click()
                        time.sleep(2)
                        button_repost_confirm = div.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div[2]/div/div[3]/div/div/div/div')
                        button_repost_confirm.click()
                        time.sleep(2)
                        button = div.find_element(By.XPATH,
                                                  './div/div/article/div/div/div[2]/div[2]/div[4]/div/div/div[1]/button')
                        button.click()
                        time.sleep(3)

                        text_area = self.driver.find_element(By.XPATH,
                                                             '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div')
                        text_area.send_keys(message)

                        reply_button = self.driver.find_element(By.XPATH,
                                                                '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div/button')
                        reply_button.click()
                        time.sleep(2)

                    except Exception as post_error:
                        print(f"Error processing individual post: {post_error}")
                        continue

            except Exception as e:
                print(f"Error fetching posts: {e}")

        process_posts()

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            process_posts()

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def close(self):
        self.driver.quit()


# Usage
if __name__ == "__main__":
    username = "your Username"
    password = "your Password"
    automation = XComLoginAutomation(username, password)
    automation.perform_login()
    automation.perform_post_search(message="Your Message.")
    automation.close()
