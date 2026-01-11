
import math
from tinydb import TinyDB, Query
import json
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import pickle
import os
import locale

# Set the locale to English with fallback options
try:
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'C.UTF-8')
    except locale.Error:
        # If all else fails, use the default locale
        pass

def save_cookies(driver, location):
    """
    Saves the cookies of the current session to a file.

    :param driver: The Selenium WebDriver.
    :param location: The path where the cookie file will be saved.
    """
    pickle.dump(driver.get_cookies(), open(location, "wb"))

def load_cookies(driver, location):
    """
    Loads cookies from a file into the WebDriver.

    :param driver: The Selenium WebDriver.
    :param location: The path from where the cookie file will be loaded.
    """
    cookies = pickle.load(open(location, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

def login(driver, url, username, password):
    """
    Logs into a website using given credentials.
    :param url: The URL of the login page.
    :param username: The username for login.
    :param password: The password for login.
    """
    driver.get(url)

    # Wait for elements to load (implicit wait)
    driver.implicitly_wait(10)

    # Wait for the cookies pop-up to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "displayCookiePop"))
    )

    # Click the 'Accept cookies' button
    cookie_button = driver.find_element(By.CSS_SELECTOR, "a.cookieBtn.cookieBtnAccept")
    cookie_button.click()

    # Click the 'Sign in' button
    sign_in_button = driver.find_element(By.ID, "navSignInBtn")
    sign_in_button.click()

    # Input email
    email_input = driver.find_element(By.ID, "enterEmailinp")
    email_input.send_keys(username)

    # Input password
    password_input = driver.find_element(By.ID, "enterPWinp")
    password_input.send_keys(password)

    # Click the 'Remember Me' checkbox
    remember_me_checkbox = driver.find_element(By.ID, "RememberMe")
    remember_me_checkbox.click()

    # Click the 'Sign in' submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-success")
    submit_button.click()

def parse_html_waist(html_content):
    """
    Parses the HTML content and extracts weight entries, stripping the 'cm' waist from data
    and preserving the date in its original format.

    :param html_content: HTML content of the webpage.
    :return: List of extracted data with dates and weight values.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    waist_entries = soup.find_all('table', class_='dataTableContent dataTableOther')
    data = []

    for table in waist_entries:
        rows = table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='colDate')
            waist_td = row.find('td', class_='colMeasureType')

            if date_td and waist_td:
                date_text = date_td.text.strip()
                waist_text = waist_td.text.replace('cm', '').strip()
                date_obj = datetime.strptime(date_text, '%a %d %b %Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')

                data.append({'Date': formatted_date, 'Waist': float(waist_text)})

    return data

def parse_html_mass(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    weight_entries = soup.find_all('table', class_='dataTableContent')
    data = []

    for table in weight_entries:
        rows = table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='colDate')
            weight_td = row.find('td', class_='colWeight colorPrimary')

            if date_td and weight_td:
                date_text = date_td.text.strip()
                weight_text = weight_td.text.replace(' Kg', '').strip()
                date_obj = datetime.strptime(date_text, '%a %d %b %Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')

                data.append({'Date': formatted_date, 'Mass': float(weight_text)})

    return data

def parse_html_kcal(html_content):
    """
    Parses the HTML content and extracts diary entries, including exercise,
    converting dates to 'YYYY-MM-DD' format.

    :param html_content: HTML content of the webpage.
    :return: List of extracted data with dates in ISO 8601 format and exercise values.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    diary_entries = soup.find_all('div', class_='printDiary')
    data = []
    for entry in diary_entries:
        # Extract the date and convert it to 'YYYY-MM-DD' format
        date_text = entry.find('h1').text.strip()
        date_obj = datetime.strptime(date_text, '%A %d %B %Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')

        categories = entry.find_all('div', class_='occasionTags')
        exercise_section = entry.find('div', class_='occasionExercise')

        daily_data = {'Date': formatted_date}
        for category in categories:
            category_name = category['data-occasioname']
            kcal = category.find('th', class_='colNutri subtot').text.strip()
            daily_data[category_name] = float(kcal)

        # Extract exercise value
        if exercise_section:
            exercise_kcal = exercise_section.find('th', class_='colNutri subtot').text.strip()
            daily_data['Exercise'] = float(exercise_kcal)

        data.append(daily_data)
    return data

def save_to_tinydb(data, db_path='data.json', db_table='table'):
    db = TinyDB(db_path)
    table = db.table(db_table)
    Date = Query()

    for entry in data:
        # Check if an entry for this date already exists
        existing_entry = table.search(Date.Date == entry['Date'])

        if existing_entry:
            # Remove existing entry
            table.remove(Date.Date == entry['Date'])

        # Insert (or re-insert) the entry
        table.insert(entry)

def merge_data(data_mass, data_weight):
    # Convert the lists to dictionaries keyed by date for easy merging
    mass_dict = {data['Date']: data for data in data_mass}
    weight_dict = {data['Date']: data for data in data_weight}

    # Combined data
    combined_data = {}

    # Merge data
    for date in set(mass_dict.keys()).union(set(weight_dict.keys())):
        combined_data[date] = {}
        if date in mass_dict:
            combined_data[date].update(mass_dict[date])
        if date in weight_dict:
            combined_data[date].update(weight_dict[date])

    # Convert back to list of dictionaries
    return list(combined_data.values())

def calc_kcal(data):
    for record in data:
        # Calculate 'net_kcal' for each record, using get() with default value 0
        record['net_kcal'] = (
            record.get('Breakfast', 0) + record.get('Lunch', 0) +
            record.get('Dinner', 0) + record.get('Snacks', 0) +
            record.get('Drinks', 0) - record.get('Exercise', 0)
        )
    return data

def calc_navy_fat(data):
    for record in data:
        if 'Waist' in record:
            # Assuming height and neck are constant for all records. If not, adjust accordingly.
            height = 178  # height in cm
            neck = 41.5  # Neck value in cm
            waist_in_inches = record['Waist'] / 2.54
            neck_in_inches = neck / 2.54
            height_in_inches = height / 2.54
            #record['Navy_fat'] = round(495 / (1.0324 - 0.19077 * math.log10(waist_in_inches - neck_in_inches) + 0.15456 * math.log10(height_in_inches)) - 450, 1)
            Army_fat = round((86.010 * math.log10(waist_in_inches - neck_in_inches)) - ( 70.041 *  math.log10(height_in_inches)) +36.76, 1)
            record['Navy_fat'] = Army_fat
    return data

def fetch_nutracheck_site_data(headless=True):
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[fetch_site_data] Loaded environment variables from .env file")
    except ImportError:
        print("[fetch_site_data] python-dotenv not installed, using system environment variables only")
    except Exception as e:
        print(f"[fetch_site_data] Warning: Could not load .env file: {e}")

    # Get credentials from environment variables
    username = os.getenv('NUTRACHECK_EMAIL')
    password = os.getenv('NUTRACHECK_PASSWORD')
    cookies_file = os.getenv('COOKIES_FILE', 'cookies.pkl')

    # Validate required environment variables
    if not username or not password:
        print("[fetch_site_data] ERROR: NUTRACHECK_EMAIL and NUTRACHECK_PASSWORD environment variables are required!")
        print("[fetch_site_data] Please set them in .env file or as environment variables")
        exit(1)

    print(f"[fetch_site_data] Using email: {username[:3]}...{username[-10:]}")

    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")

    # Required options for running Chrome in Docker
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")

    # Set binary location explicitly
    chrome_options.binary_location = "/usr/bin/google-chrome"

    # Enable verbose logging for debugging
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-level=0")

    # Pass the options when initializing the driver
    print("[fetch_site_data] Starting Chrome WebDriver...")

    # Enable verbose ChromeDriver logging
    service = Service(log_output=os.path.join(os.getcwd(), 'chromedriver.log'), service_args=['--verbose'])

    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("[fetch_site_data] Chrome WebDriver started successfully")

    # Load cookies if they exist, otherwise login and save cookies
    #if os.path.exists(cookies_file):
    if False:
        driver.get('https://www.nutracheck.co.uk')
        load_cookies(driver, cookies_file)
        driver.get('https://www.nutracheck.co.uk')
    else:
        login_url = 'https://www.nutracheck.co.uk'
        login(driver, login_url, username, password)
        save_cookies(driver, cookies_file)

    date_seven_days_ago = datetime.now() - timedelta(days=6)
    formatted_date = date_seven_days_ago.strftime('%Y-%m-%d')
    target_url_kcal = f'https://www.nutracheck.co.uk/Diary/Reports/DiaryPrint?d1={formatted_date}&days=7&time=7days'
    target_url_mass = "https://www.nutracheck.co.uk/Diary/MyProgress?measureID=1"
    target_url_waist = "https://www.nutracheck.co.uk/Diary/MyProgress?measureID=2"

    driver.get(target_url_kcal)
    time.sleep(1)  # Adjust time as necessary
    html_content_kcal = driver.page_source
    driver.get(target_url_mass)
    time.sleep(1)  # Adjust time as necessary
    html_content_mass = driver.page_source

    driver.get(target_url_waist)
    time.sleep(1)  # Adjust time as necessary
    html_content_waist = driver.page_source
    driver.quit()

    data_kcal = parse_html_kcal(html_content_kcal)
    data_mass = parse_html_mass(html_content_mass)
    data_weight = parse_html_waist(html_content_waist)

    data_mass_waist = merge_data(data_mass, data_weight)

    data_kcal = calc_kcal(data_kcal)
    data_mass_waist_navy = calc_navy_fat(data_mass_waist)

    print(f"data_kcal:")
    for element in data_kcal:
        print(element)
    print(f"data_mass_waist:")
    for element in data_mass_waist:
        print(element)

    # Get data file path from environment variables
    data_file = os.getenv('DATA_FILE', 'daily_data.json')
    print(f"[fetch_site_data] Saving to data file: {data_file}")

    save_to_tinydb(data= data_kcal, db_path=data_file, db_table='daily_kcal')
    save_to_tinydb(data= data_mass_waist_navy, db_path=data_file, db_table='daily_mass_waist')

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[fetch_site_data] Loaded environment variables from .env file")
    except ImportError:
        print("[fetch_site_data] python-dotenv not installed, using system environment variables only")
    except Exception as e:
        print(f"[fetch_site_data] Warning: Could not load .env file: {e}")

    fetch_nutracheck_site_data(headless=False)
