import csv
import sqlite3
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def save_full_page_screenshot(driver, filename):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    driver.execute_script("document.body.style.zoom='100%'")
    # driver.save_screenshot(filename)

def find_element_with_retry(driver, by, value, retries=30, delay=10):
    for i in range(retries):
        try:
            time.sleep(delay)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            log(f"Retry {i + 1}/{retries} - Failed to locate element: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to locate element after {retries} retries")



def log(message):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')

log("Connecting to Selenium Grid / Hub...")
try:
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=options,
        keep_alive=True
    )
    log("Successfully connected to Selenium Grid / Hub")
except Exception as e:
    log(f"Failed to connect to Selenium Grid / Hub: {e}")
    raise

log("Navigating to the website...")
try:
    # driver = webdriver.Chrome()
    driver.get("https://zes.net/sarj-istasyonlari")
    log(f"Page title: {driver.title}")
except Exception as e:
    log(f"Failed to navigate to the website: {e}")
    driver.quit()
    raise

items_content = []
item_index = 1
driver.set_window_size(1920, 1080)

try:
    items = driver.find_elements(By.CSS_SELECTOR, '.items .item')
    log(f"Found {len(items)} items")
except Exception as e:
    log(f"Failed to find items: {e}")
    driver.quit()
    raise

while item_index < len(items):
    try:
        item_xpath = f"/html/body/section[3]/div[1]/div[3]/div/div[{item_index}]"
        item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, item_xpath)))
        log("name")
        driver.execute_script("arguments[0].click()", item)
        time.sleep(2)
        log("Item clicked")
        item_text = item.text

        detail_active = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[3]/div[1]/div[4]")))
        time.sleep(10)
        log("Detail active")

        driver.execute_script("arguments[0].scrollIntoView();", detail_active)
        time.sleep(10)
        save_full_page_screenshot(driver, "fullpage_screenshot.png")
        deneme =1
        try:
            if(deneme==1):
                log("Attempting to locate wrapper element")
                wrapper = WebDriverWait(detail_active, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".detail.active .wrapper"))
                )
            else:
                wrapper = find_element_with_retry(detail_active, By.CSS_SELECTOR, ".detail.active .wrapper")
                log("Wrapper element located")
        except Exception as e:
            log(f"Failed to locate wrapper element: {e}")
            driver.save_screenshot("error_screenshot.png")
            continue

        type_info = wrapper.find_elements(By.XPATH, "/html/body/section[3]/div[1]/div[4]/div[2]/div[1]/span")
        tech = type_info[0].text if len(type_info) > 0 else "N/A"
        log("tech")

        address_title = driver.find_elements(By.CLASS_NAME, "address")
        address = address_title[0].text if len(address_title) > 0 else "N/A"
        log("address")

        usage_info_title = driver.find_elements(By.CLASS_NAME, "infos")
        status = usage_info_title[0].text if len(usage_info_title) > 0 else "N/A"
        log("status")

        try:
            rotate_button = WebDriverWait(detail_active, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "body > section.locations.detail-active > div.list > div.detail.active > a"))
            )
            driver.execute_script("arguments[0].click()", rotate_button)
            time.sleep(2)
        except Exception as e:
            log(f"Failed to click rotate button: {e}")
            continue

        driver.switch_to.window(driver.window_handles[-1])
        log("Switched to the new tab")

        try:
            time.sleep(5)
            location = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div:nth-child(1) > h1")
            ))
            time.sleep(2)
            location_text = location.text
        except Exception as e:
            log(f"Failed to locate location element: {e}")
            driver.save_screenshot("error_location.png")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            location_text = "N/A"
            continue

        items_content.append({
            'Station Name': item_text,
            'Station Code': "N/A",  # Assuming 'Station Code' is not available
            'Station Coordinate': location_text,  # Set location_text as Station Coordinate
            'Station Address': address,
            'Station Tech': tech,
            'Station Status': status
        })

        item_index += 1
        log(f"Scrolled to item {item_index}")

        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        log(f"Failed to fetch item at index {item_index}: {e}")
        log(traceback.format_exc())
        break

output_file = "items_content.csv"
try:
    with open(output_file, "w", newline='', encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Station Name", "Station Code", "Station Coordinate",
            "Station Address", "Station Tech", "Station Status"
        ])
        writer.writeheader()
        for item in items_content:
            writer.writerow(item)
    log(f"Items content saved to {output_file}")
except Exception as e:
    log(f"Failed to save items content: {e}")

driver.quit()

df = pd.read_csv(output_file)

connection = sqlite3.connect("e_charge_stations.db")

df.to_sql("e_charge_stations", connection, if_exists="append", index= False)

connection.close()
