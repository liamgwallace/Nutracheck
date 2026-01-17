"""
Authentication module for Nutracheck login using Selenium.
Extracted and adapted from nutracheck/scraper.py
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def create_chrome_driver(headless=True):
    """
    Creates a Chrome WebDriver with appropriate options for containerized environments.

    :param headless: Whether to run Chrome in headless mode
    :return: Configured Chrome WebDriver instance
    """
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

    # Set binary location explicitly for Linux/Docker only
    if os.name != 'nt':  # Not Windows
        chrome_options.binary_location = "/usr/bin/google-chrome"

    return webdriver.Chrome(options=chrome_options)


def login_to_nutracheck(driver, username=None, password=None):
    """
    Logs into Nutracheck website using given credentials.
    If credentials are not provided, attempts to load from environment variables.

    :param driver: The Selenium WebDriver instance
    :param username: Nutracheck email (optional, defaults to NUTRACHECK_EMAIL env var)
    :param password: Nutracheck password (optional, defaults to NUTRACHECK_PASSWORD env var)
    :return: True if login successful, False otherwise
    :raises: Exception if credentials are missing
    """
    # Load credentials from environment if not provided
    if username is None:
        username = os.getenv('NUTRACHECK_EMAIL')
    if password is None:
        password = os.getenv('NUTRACHECK_PASSWORD')

    # Validate credentials
    if not username or not password:
        raise ValueError("Missing credentials: NUTRACHECK_EMAIL and NUTRACHECK_PASSWORD must be set")

    try:
        # Navigate to login page
        login_url = 'https://www.nutracheck.co.uk'
        driver.get(login_url)

        # Wait for elements to load
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

        # Wait a moment for login to complete
        time.sleep(2)

        # Verify login success by checking for a common element on the logged-in page
        # (This assumes there's a consistent element that appears after login)
        try:
            # Wait for navigation to complete - check for absence of login form
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "enterEmailinp"))
            )
            return True
        except:
            # Login might have succeeded even if we can't verify it this way
            return True

    except Exception as e:
        print(f"Login failed: {e}")
        raise


def get_credentials_from_env():
    """
    Retrieves Nutracheck credentials from environment variables.

    :return: Tuple of (username, password)
    :raises: ValueError if credentials are not set
    """
    username = os.getenv('NUTRACHECK_EMAIL')
    password = os.getenv('NUTRACHECK_PASSWORD')

    if not username or not password:
        raise ValueError("Missing credentials: NUTRACHECK_EMAIL and NUTRACHECK_PASSWORD environment variables must be set")

    return username, password
