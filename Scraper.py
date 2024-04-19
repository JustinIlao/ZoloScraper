import time
import re
import requests
import bs4
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Lists to store scraped data
new_address = []
new_cities = []
new_postal = []

# Function to login using Selenium
def login_with_requests():
    # Path to Chrome webdriver
    driver_path = r'yourpath'
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service)
    driver.get('https://www.zolo.ca/sign-in')

    time.sleep(5)  # Wait for page to load

    # Find and input email
    email = WebDriverWait(driver, 100).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.text-input.rounded.fill-grey-bg.xs-pr4')))
    for char in 'YOUR_EMAIL':
        email.send_keys(char)
        time.sleep(0.1)

    # Click on login button
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.button--large.fill-primary'))).click()
    time.sleep(5)  # Wait for login

    # Find and input PIN
    pin = WebDriverWait(driver, 100).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.text-input.rounded.fill-grey-bg')))
    for char1 in 'YOUR_PIN':
        pin.send_keys(char1)
        time.sleep(0.1)

    # Click on PIN submit button
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.button--large.fill-primary'))).click()
    driver.get('https://www.zolo.ca/')  # Redirect to Zolo homepage

    while True:
        url = "https://www.zolo.ca/index.php"
        query_params = {
            "attribute_terms": "",
            "has_photos": "",
            "days_on_zolo": "0",
            "ptype_condo": "0",
            "ptype_townhouse": "1",
            "ptype_house": "1",
            "stype": "",
            "min_price": "0",
            "max_price": "0",
            "min_beds": "0",
            "min_baths": "0",
            "min_sqft": "0",
            "openhouse_search": "0",
            "filter": "1",
            "s_r": "1",
            "search_order": "3"
        }

        # Ask user for the sort order
        days_on_site = input("Would you like to sort by Most Recent, or Oldest: ").lower()
        if days_on_site == "most recent":
            query_params["search_order"] = "3"
        elif days_on_site == "oldest":
            query_params["search_order"] = "4"
        else:
            print("Invalid input. Please try again.")
            continue

        # Ask user for the area
        area = input("Enter desired location:")
        if " " in area:
            area = area.replace(" ", "%20").lower()
        if not area:
            print("No area entered. Please try again.")
            continue

        query_params["sarea"] = area

        pages = int(input("Enter how many pages you want queried:"))

        start_on = int(input("Enter which page you want to start on:"))

        query_string = "&".join([f"{key}={value}" for key, value in query_params.items() if value])
        final_url = f"{url}?{query_string}"
        actual_url1 = ""

        print("Final URL:", final_url)
        break  # Exit loop after URL is generated

    driver.get(final_url)  # Open final URL in browser

    # Scraping addresses and cities
    if pages >= 1:
        if area == "greater%20toronto%20area":
            area = "Greater+Toronto+Area"
            for i in range(start_on, pages+1):
                url2 = "https://www.zolo.ca/index.php?sarea={num}&s={i_i}".format(num=area, i_i=i)
                driver.get(url2)
                time.sleep(5)
                soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
                addresses = soup.find_all('span', itemprop='streetAddress')
                cities = soup.find_all('span', itemprop='addressLocality')
                for city in cities:
                    city1 = city.get_text()
                    new_cities.append(city1)
                for address in addresses:
                    address_text = address.get_text()  # Call get_text() on each individual element
                    new_address.append(address_text)
        else:
            if "%20" in area:
                area = area.replace("%20", "-")
            for i in range(start_on, pages+1):
                url3 = "https://www.zolo.ca/{num}-real-estate/page-{i_i}".format(num=area, i_i=i)
                driver.get(url3)
                time.sleep(5)
                soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
                addresses = soup.find_all('span', itemprop='streetAddress')
                cities = soup.find_all('span', itemprop='addressLocality')
                for city in cities:
                    city1 = city.get_text()
                    new_cities.append(city1)
                for address in addresses:
                    address_text = address.get_text()  # Call get_text() on each individual element
                    new_address.append(address_text)


# Function to get postal code from Google Maps API
def get_postal_code(addy, city):
    API_KEY = 'YOUR_API_KEY'  # Your Google Maps API key
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": addy,
        "components": f"locality:{city}|country:CA",
        "key": API_KEY
    }

    response = requests.get(base_url, params=params)
    results = response.json()
    print(results)  # Debug: print API response

    if results["status"] == "OK":
        address_components = results["results"][0]["address_components"]
        postal_code = next((item["short_name"] for item in address_components if "postal_code" in item["types"]), None)
        return postal_code
    else:
        return "No postal code found"


if __name__ == '__main__':
    login_with_requests()  # Ensure this function populates new_address and new_cities

    filtered_address = []
    filtered_cities = []
    filtered_postal = []

    # Iterate through addresses and cities, get postal codes
    for i, address in enumerate(new_address):
        city = new_cities[i]
        postal_code = get_postal_code(address, city)

        # Check for valid postal code format
        if postal_code is not None and postal_code != "No postal code found" and re.search('[a-zA-Z]\d[a-zA-Z] \d[a-zA-Z]\d', postal_code):
            filtered_postal.append(postal_code)
            filtered_address.append(address)
            filtered_cities.append(city)

    # Create DataFrame with collected data
    df = pd.DataFrame({
        "Title": "Homeowner",
        "ADDRESS": filtered_address,
        "CITY": filtered_cities,
        "PC": filtered_postal,
        "PROV": "ON"
    })
    df.to_csv('Test32.csv', index=False)  # Save DataFrame to CSV file
