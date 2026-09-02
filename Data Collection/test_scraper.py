import requests
from bs4 import BeautifulSoup

url = "https://www.airindia.com/en-in/book-flights"

print("Connecting to Air India...")

try:
    response = requests.get(url, timeout=10)

    print("Status code:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    prices = soup.find_all(string=lambda text: text and "INR" in text)

    print("Prices found:")

    for price in prices:
        print(price.strip())

except requests.exceptions.Timeout:
    print("The website took too long to respond.")

except requests.exceptions.RequestException as e:
    print("Error:", e)