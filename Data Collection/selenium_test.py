from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()

driver = webdriver.Chrome(options=options)

print("Opening Air India...")

driver.get("https://www.airindia.com/en-in/book-flights")

time.sleep(8)

prices = driver.find_elements(
    By.XPATH,
    "//*[contains(text(), 'INR')]"
)

print("Prices found:")

for price in prices:
    text = price.text.strip()

    if text:
        print(text)

driver.quit()

print("Browser closed.")