from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import sys
# import pypyodbc as odbc
import pyodbc

DRIVER = 'SQL SERVER'
SERVER_NAME = 'ACER_DB\SQLEXPRESS'
DATABASE_NAME = 'e_charge_stations'

conn_str = f"""" 
    Driver = {{{DRIVER}}};
    Server = {SERVER_NAME};
    Database = {DATABASE_NAME};
    Trust_Connection = yes;
"""

try:
    #connection = odbc.connect(conn_str)
    connection = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS;Database=e_charge_stations;Trusted_Connection=yes;')
except Exception as e:
    print(e)
    print("Unable to connect to the database")
    sys.exit()
else:
    print("Connected to the database")
    cursor = connection.cursor()

sql = """
    INSERT INTO e_charge_stations (
       [Station Name], [Station Code], 
        [Station Coordinate], [Station Address], 
        [Station Tech], [Station Status]
    ) VALUES (?, ?, ?, ?, ?, ?)
    """


def log(message):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")


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


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

log("Connecting to Selenium Grid / Hub...")
try:
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=options,
        keep_alive=True
    )

    log("Successfully connected to Selenium Grid / Hub")
    driver.maximize_window()
except Exception as e:
    log(f"Failed to connect to Selenium Grid / Hub: {e}")
    raise

driver.get("https://esarj.com/harita")

# Find and click the toggle button to open the menu
toggle_button = find_element_with_retry(driver, By.CLASS_NAME, "side-box-toggle")
time.sleep(2)
driver.execute_script("arguments[0].click();", toggle_button)
time.sleep(2)

# Locate the station elements
station_elements = WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.XPATH, "//tr[@ng-repeat='station in stations']"))
)

items_content = []

for station_index in range(len(station_elements)):
    try:
        # Re-find the station element to avoid stale element reference
        station = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@ng-repeat='station in stations']"))
        )[station_index]

        # Click the station to display the info window
        station_td = WebDriverWait(station, 30).until(
            EC.element_to_be_clickable((By.TAG_NAME, "td"))
        )
        driver.execute_script("arguments[0].click();", station_td)
        time.sleep(10)
        log("Station display works")

        tab_menu = find_element_with_retry(driver, By.ID,
                                           'tab-menu')  # TEKRARLI DENEME SONUCU STATION DISLPAY WORK VE SONRA DEVAM BİR İSTASYONU ATLADI AKGÜN
        # DEVAM VE SONRASINDA TEKRARDAN STATION DISPLAY ÇALIŞMADI Failed to fetch data for a station: Message: stale element reference: stale element not found in the current frame
        # SONRASINDA DEVAM OLDUĞU YERDEN

        li_elements = WebDriverWait(tab_menu, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'li'))
        )

        # Dictionary to store specific tab contents
        tab_content = {
            "tab-station": '',
            "tab-location": '',
            "tab-services": '',
            "tab-tech": '',
            "tab-status": ''
        }

        # Click each li element and extract specific td elements
        for li_index in range(len(li_elements)):
            try:
                # Re-find the li element to avoid stale element reference
                li_elements = WebDriverWait(tab_menu, 30).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'li'))
                )
                li = li_elements[li_index]
                # time.sleep(2)
                log("burada")

                # Extract href attributes to iterate between li elements
                a_element = WebDriverWait(li, 30).until(
                    EC.element_to_be_clickable((By.TAG_NAME, 'a'))
                )
                tab_id = a_element.get_attribute("href").split("#")[-1]
                driver.execute_script("arguments[0].click();", a_element)
                log(f"Clicked tab: {a_element.text}")
                time.sleep(2)

                # Extract specific td elements based on tab_id
                if tab_id == "tab-station":
                    td_elements = WebDriverWait(driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='{tab_id}']//td"))
                    )
                    tab_content['tab-station'] = td_elements[5].text if len(td_elements) > 5 else ''
                    tab_content['tab-station-code'] = td_elements[7].text if len(td_elements) > 7 else ''
                elif tab_id == "tab-location":
                    td_elements = WebDriverWait(driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='{tab_id}']//td"))
                    )
                    tab_content['tab-location'] = td_elements[1].text if len(td_elements) > 1 else ''
                    tab_content['tab-address'] = td_elements[7].text if len(td_elements) > 7 else ''
                elif tab_id == "tab-tech":
                    td_elements = WebDriverWait(driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='{tab_id}']//td"))
                    )
                    tab_content['tab-tech'] = td_elements[3].text if len(td_elements) > 3 else ''
                elif tab_id == "tab-services":
                    td_elements = WebDriverWait(driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='{tab_id}']//td"))
                    )
                    tab_content['tab-services'] = td_elements[1].text if len(td_elements) > 1 else ''

            except Exception as e:
                log(f"Failed to click tab or extract data: {e}")

        log(f"Extracted tab contents: {tab_content}")

        try:
            extracted_data = {
                "station_name": tab_content['tab-station'],
                "station_code": tab_content.get('tab-station-code', ''),
                "station_coordinate": tab_content['tab-location'],
                "station_address": tab_content.get('tab-address', ''),
                "station_tech": tab_content['tab-tech'],
                "station_status": tab_content['tab-services']
            }
            items_content.append(extracted_data)

        except Exception as e:
            log(f"Failed to extract specific data: {e}")

        driver.execute_script("arguments[0].scrollIntoView();", station)
        time.sleep(10)

    except Exception as e:
        log(f"Failed to fetch data for a station: {e}")

# Write data to a CSV file
output_file = "e_charge_stations.csv"
try:
    with open(output_file, "w", encoding="utf-8-sig", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Station Name", "Station Code", "Station Coordinate",
                         "Station Address", "Station Tech", "Station Status"])
        for item in items_content:
            cursor.execute(sql, (
                item["station_name"],
                item.get("station_code", ''),
                item.get("station_coordinate", ''),
                item.get("station_address", ''),
                item.get("station_tech", ''),
                item.get("station_status", '')
            ))
            writer.writerow([
                item["station_name"],
                item.get("station_code", ''),
                item.get("station_coordinate", ''),
                item.get("station_address", ''),
                item.get("station_tech", ''),
                item.get("station_status", '')
            ])
    log(f"Data saved to {output_file}")
except Exception as e:
    cursor.rollback()
    log(f"Failed to save data to CSV file: {e}")
    log(f"Cursor failed")
else:
    cursor.commit()
    cursor.close()
finally:
    driver.quit()
    connection.close()


# df = pd.read_csv(output_file)
#
# connection = sqlite3.connect("e_charge_stations.db")
#
# df.to_sql("e_charge_stations", connection, if_exists="replace")
#
# connection.close()
