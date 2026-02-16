import os
import requests
import threading
import time
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

# fetched these from the system's environment variables. 
# No real keys are written here to keep the account safe on GitHub.
BS_USER = os.getenv("BROWSERSTACK_USERNAME")
BS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")
RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")

# Safety check: If any key is missing, stop the script and tell the user how to fix it.
if not all([BS_USER, BS_KEY, RAPID_API_KEY]):
    print("\n ERROR: Missing Environment Variables!")
    print("Please set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY, and RAPIDAPI_KEY in your terminal.")
    exit(1)

# List of browsers and devices for the cloud tests
PLATFORMS = [
    {"browserName": "chrome", "browserVersion": "latest", "os": "Windows", "osVersion": "11", "name": "Win11-Chrome"},
    {"browserName": "firefox", "browserVersion": "latest", "os": "Windows", "osVersion": "10", "name": "Win10-Firefox"},
    {"browserName": "safari", "browserVersion": "latest", "os": "OS X", "osVersion": "Sonoma", "name": "Mac-Safari"},
    {"browserName": "chrome", "deviceName": "Samsung Galaxy S23", "osVersion": "13.0", "name": "Android-S23"},
    {"browserName": "safari", "deviceName": "iPhone 15", "osVersion": "17", "name": "iOS-iPhone15"}
]

class ElPaisCEAutomation:
    def __init__(self, config=None):
        self.config = config
        self.is_cloud = config is not None
        # Naming the test run so it shows up clearly on the dashboard
        self.session_name = config.get("name", "LocalRun") if self.is_cloud else "LocalRun"
        self.is_success = False

        if self.is_cloud:
            # Picking the right options class for the specific browser
            browser = config.get("browserName", "chrome").lower()
            if browser == "firefox": options = FirefoxOptions()
            elif browser == "safari": options = SafariOptions()
            else: options = ChromeOptions()

            # Setting up all the platform requirements
            for k, v in config.items():
                if k != "name": options.set_capability(k, v)
            
            # BrowserStack specific settings for the project dashboard
            options.set_capability('bstack:options', {
                "userName": BS_USER, "accessKey": BS_KEY,
                "projectName": "El Pais CE Assessment","buildName": "El Pais Assessment", "sessionName": self.session_name
            })
            # Connecting to the remote cloud server
            self.driver = webdriver.Remote("https://hub-cloud.browserstack.com/wd/hub", options=options)
        else:
            # Simple setup for running on my own computer
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # Setting a 20-second wait time for finding elements
        self.wait = WebDriverWait(self.driver, 20)

    def translate_via_api(self, text_to_translate):
        # Using Translate Plus on RapidAPI to turn Spanish titles into English
        url = "https://translate-plus.p.rapidapi.com/translate"
        
        payload = {
            "text": text_to_translate,
            "source": "es",
            "target": "en"
        }
        
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "translate-plus.p.rapidapi.com"
        }

        try:
            # Sending the request to the API
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # Finding the translated string inside the API's response data
                return result.get('translations', {}).get('translation', text_to_translate)
            else:
                print(f"[{self.session_name}] API problem: {response.text}")
                return text_to_translate
        except Exception as e:
            print(f"[{self.session_name}] API connection failed: {e}")
            return text_to_translate

    def run(self):
        try:
            # Opening the Opinion section of the news site
            self.driver.get("https://elpais.com/opinion/")

            # ensuring text is in Spanish
            page_lang = self.driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
            if "es" not in page_lang.lower():
                print(f"[{self.session_name}] Warning: Page language is {page_lang}, not Spanish.")
            
            # Clicking 'Accept' on the cookie pop-up if it gets in the way
            try:
                cookie_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
                self.driver.execute_script("arguments[0].click();", cookie_btn)
            except: pass 

            # Waiting for the articles to show up on the page
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
            # Picking only the first five articles
            articles = self.driver.find_elements(By.TAG_NAME, "article")[:5]
            
            spanish_headers = []
            for i, article in enumerate(articles):
                # Scrolling to each article so it loads images and text properly
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
                time.sleep(1.5)

                # Fetching the title and the teaser text
                title_es = article.find_element(By.TAG_NAME, "h2").text
                try:
                    content_es = article.find_element(By.TAG_NAME, "p").text
                except:
                    content_es = "No preview available"

                print(f"\n[{self.session_name}] Article {i+1} found:")
                print(f"Title: {title_es}")
                print(f"Content: {content_es}")

                # Saving the article photos to my folder if I'm running this locally
                if not self.is_cloud:
                    try:
                        img_element = article.find_element(By.TAG_NAME, "img")
                        img_url = img_element.get_attribute("src")
                        if img_url:
                            with open(f"cover_{i+1}.jpg", "wb") as f: 
                                f.write(requests.get(img_url).content)
                    except: pass

                spanish_headers.append(title_es)

            # Translating all the titles we collected
            print(f"\n--- Translating titles for {self.session_name} ---")
            translated_headers = []
            for header in spanish_headers:
                en_text = self.translate_via_api(header)
                print(f"[{self.session_name}] English: {en_text}")
                translated_headers.append(en_text)

            # Counting how many times each word appears in the translated titles
            all_words = " ".join(translated_headers).lower().split()
            word_counts = Counter(all_words)
            # Only keeping words that show up more than 2 times
            repeats = {word: count for word, count in word_counts.items() if count > 2}

            print(f"\n[{self.session_name}] Common words: {repeats}")
            self.is_success = True

        except Exception as e:
            # Telling the BrowserStack dashboard if the test failed
            if self.is_cloud:
                self.driver.execute_script(f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"failed", "reason": "{str(e)[:50]}"}}}}')
            print(f"[{self.session_name}] Error during run: {e}")
        finally:
            # Marking the test as passed if we got to the end without errors
            if self.is_cloud and self.is_success:
                 self.driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Success"}}')
            # Closing the browser session
            self.driver.quit()

def start_thread(config):
    # This function helps run multiple browsers at the same time
    ElPaisCEAutomation(config).run()

if __name__ == "__main__":
    # First run a quick local check
    print(">>> RUNNING LOCAL VALIDATION")
    ElPaisCEAutomation().run()

    # Now start the parallel tests on BrowserStack
    print("\n>>> STARTING CLOUD TESTS ON ALL PLATFORMS")
    threads = []
    for p in PLATFORMS:
        t = threading.Thread(target=start_thread, args=(p,))
        threads.append(t)
        t.start()

    # Waiting for all browsers to finish before closing the script
    for t in threads:
        t.join()
        
    print("\nProject complete! check your browserstack dashboard")