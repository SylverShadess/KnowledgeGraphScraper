from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Scraper:
    def __init__(self):
        self.chrome_options = Options()

        self.chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)        
        self.chrome_options.add_argument("--disable-features=BraveShields") # Disable Brave Shields
        # self.chrome_options.add_argument('--ignore-certificate-errors')  # Disable SSL certificate verification
        # self.chrome_options.add_argument('--ignore-ssl-errors')

        # self.chrome_options.add_argument('--incognito') # Incognito mode
        # self.chrome_options.add_argument('--no-sandbox') # Bypass OS security model
        # self.chrome_options.add_argument('--disable-dev-shm-usage') # Overcome limited resource problems

        self.chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'  
        self.service = Service('C:\\Program Files\\chromedriver-win64\\chromedriver.exe') 

    def scrape(self, url: str, search: str="") -> list:
        try:
            with webdriver.Chrome(service=self.service, options=self.chrome_options) as driver:
                driver.get(url)

                # From the wonderful Kimi
                # Wait for the page to load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                # # Use JavaScript to extract all text from the <body> tag
                # all_text = driver.execute_script("return document.body.innerText;")

                # # Split the text into meaningful chunks
                # text_chunks = [chunk.strip() for chunk in all_text.split('\n') if chunk.strip()]

                # Extract the content
                # result = driver.find_elements(By.XPATH, f"//a[contains(text(), '{search}')]")
                result = driver.find_elements(By.XPATH, f"//body//*[contains(text(), '{search}')]")

                # Print the results
                result_text = [item.text for item in result]
                # print(result_text)
                driver.quit()


        except Exception as e:
            driver.quit()
            print(f"An error occurred: {e}")
            return []
        
        return result_text