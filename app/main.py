"""
Scraper for used car listings.
"""
import json
import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from constants import (
    BASE_URL,
    LISTING_URL,
)
from database import save_car_to_database


def start_webdriver():
    """
    Initializes a headless Chrome WebDriver instance.
    """
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    print("🚀 Starting Chrome WebDriver...")
    return webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )

def extract_phone_number(url: str):
    """
    Uses Selenium to extract the seller's unmasked phone number from the car listing page.

    Args:
        url (str): The URL of the car listing.

    Returns:
        int or None: Extracted phone number as an integer, or None if unavailable.
    """
    try:
        driver = start_webdriver()
        driver.get(url)

        phone_container = driver.find_elements(By.CLASS_NAME, 'phone')[0]
        show_button = phone_container.find_element(By.CLASS_NAME, 'phone_show_link')
        driver.execute_script("arguments[0].click();", show_button)

        def phone_number_unmasked(driver):
            el = driver.find_elements(By.CLASS_NAME, 'phone')[0]
            return el.get_attribute('data-phone-number')

        phone_number_str = WebDriverWait(driver, 10).until(phone_number_unmasked)
        phone_number = int(re.sub(r'\D', '', phone_number_str))
        driver.quit()
        return phone_number
    except WebDriverException as e:
        print(f"⚠️ WebDriver error: {e}")
    except Exception:
        pass
    return None

def scrape_car_page(url: str):
    """
    Scrapes detailed information from a single car listing page.

    Args:
        url (str): The URL of the car listing.

    Returns:
        dict: A dictionary containing all relevant car data fields.
    """
    print(f"🔍 Scraping car page: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
        return None

    def safe_text(selector, attr=None, cast=None, default=None):
        try:
            el = soup.select_one(selector)
            text = el.get(attr).strip() if attr else el.text.strip()
            return cast(text) if cast else text
        except:
            return default

    title = safe_text('div.heading-cars h1', 'title', default=None)
    price_usd = safe_text(
        'div.price_value strong',
        cast=lambda x: int(re.sub(r'\D', '', x)), default=None,
    )
    mileage_km = safe_text('span.size18', cast=lambda x: int(re.sub(r'\D', '', x)) * 1000, default=None)

    try:
        seller_block = soup.select_one('div.seller_info_name')
        seller_name = seller_block.text.strip() if seller_block else None
        if seller_block and seller_block.find('a'):
            seller_name = seller_block.find('a').text.strip()
    except:
        seller_name = None

    image_url = None
    try:
        img_tag = soup.select_one('div.photo-620x465 img')
        if img_tag and 'src' in img_tag.attrs:
            image_url = img_tag['src']
    except:
        pass

    images_count = safe_text('div.preview-gallery', cast=lambda x: int(re.sub(r'\D', '', x)), default=None)

    license_plate = None
    try:
        license_span = soup.select_one('span.state-num.ua')
        license_plate = ''.join([t for t in license_span.contents if isinstance(t, NavigableString)]).strip()
    except:
        pass

    car_vin = safe_text('span.label-vin', default=None)

    phone_number = extract_phone_number(url)

    return {
        "url": url,
        "title": title,
        "price_usd": price_usd,
        "odometer": mileage_km,
        "username": seller_name,
        "phone_number": phone_number,
        "image_url": image_url,
        "images_count": images_count,
        "car_number": license_plate,
        "car_vin": car_vin,
    }

def get_car_links(page_number):
    """
    Fetches all car listing URLs from a given pagination page.

    Args:
        page_number (int): The pagination page number to scrape.

    Returns:
        list[str]: A list of full car listing URLs found on the page.
    """
    url = LISTING_URL + str(page_number)
    print(f"Fetching listing page: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch page {page_number}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    links = [
        BASE_URL + el['data-link-to-view']
        for el in soup.select('.ticket-item [data-link-to-view]')
    ]

    print(f"Found {len(links)} cars on page {page_number}")
    return links

def scrape_all_links():
    """
    Iterates through all pagination pages, scrapes each car listing,
    stores JSON dump files, and inserts data into the database.

    Returns:
        list[str]: A list of all collected car URLs.
    """
    all_links = []
    page_number = 1
    car_index = 0

    while True:
        links = get_car_links(page_number)
        if not links:
            print("No more cars found. Stopping.")
            break

        for link in links:
            car_data = scrape_car_page(link)
            print(car_data)
            save_car_dump(car_data, car_index)
            save_car_to_database(data=car_data)
            car_index += 1

        all_links.extend(links)
        page_number += 1
        time.sleep(2)

    return all_links

def save_car_dump(data: dict, index: int):
    """
    Saves a single car's scraped data to a JSON file in the 'dumps' directory.

    Creates a folder named with the current date (YYYYMMDD) if it doesn't exist.

    Args:
        data (dict): The dictionary containing car information.
        index (int): An integer index to differentiate dump files.
    """
    date_dir = datetime.now().strftime("%Y_%m_%d")
    path_to_dump_directory = f"/app/dumps/{date_dir}"
    os.makedirs(path_to_dump_directory, exist_ok=True)

    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{path_to_dump_directory}/car_{timestamp}_{index}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved dump to {filename}")


if __name__ == '__main__':
    scrape_all_links()
