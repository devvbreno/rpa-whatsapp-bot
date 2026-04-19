import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WhatsAppBot:
    def __init__(self, profile_path: str):

        self.profile_path = profile_path
        self.driver = None
        self.wait = None

    def start_browser(self):

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.profile_path}")
        
        # anti ban
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        self.wait = WebDriverWait(self.driver, 35)
        
        self.driver.get("https://web.whatsapp.com")
        print("⏳ Waiting for WhatsApp Web to fully load...")
        time.sleep(15)
        
    def close_browser(self):

        if self.driver:
            self.driver.quit()
            
    def send_message(self, phone_number: str, message: str) -> tuple[bool, str]:
        encoded_message = urllib.parse.quote(message)
        link = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        self.driver.get(link)

        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "main")))

            box_selector = '#main footer div[contenteditable="true"]'
            text_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, box_selector)))
            
            time.sleep(random.uniform(2.5, 4.5))
            
            text_box.send_keys(Keys.ENTER)
            
            time.sleep(2)
            
            return True, "Sent Successfully"

        except Exception as e:
            return False, "Invalid Number or Timeout"