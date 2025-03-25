"""
Simplified BrowserStack Test Script
This script uses a minimal approach to run tests on BrowserStack,
avoiding unnecessary configuration and thread management issues.
"""

import os
import sys
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("simplified_browserstack_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def main():
    """Main function to run the test"""
    # Get BrowserStack credentials
    username = os.environ.get('BROWSERSTACK_USERNAME')
    access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    if not username or not access_key:
        logger.error("BrowserStack credentials not found in environment variables")
        return 1
    
    driver = None
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        
        # Set BrowserStack options
        bstack_options = {
            'deviceName': 'Samsung Galaxy S22',
            'osVersion': '12.0',
            'realMobile': 'true',
            'projectName': 'Malaberg Shopify Tests',
            'buildName': 'Simplified Test',
            'sessionName': 'Shopify Homepage Test',
            'debug': 'true',
            'networkLogs': 'true',
            'userName': username,
            'accessKey': access_key
        }
        options.set_capability('bstack:options', bstack_options)
        
        # Create the driver
        logger.info("Creating WebDriver instance")
        url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
        driver = webdriver.Remote(command_executor=url, options=options)
        
        # Navigate to the Shopify homepage
        logger.info("Navigating to Shopify homepage")
        driver.get("https://physicalnutrition-uk.myshopify.com/")
        
        # Wait for the main navigation to be visible
        logger.info("Waiting for main navigation to be visible")
        wait = WebDriverWait(driver, 30)
        nav_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "nav.header__inline-menu")))
        
        # Verify the main navigation is present
        if nav_element.is_displayed():
            logger.info("✅ Test PASSED: Main navigation is visible")
            update_test_status(driver.session_id, username, access_key, "passed")
        else:
            logger.error("❌ Test FAILED: Main navigation is not visible")
            update_test_status(driver.session_id, username, access_key, "failed")
        
        # Get and display the BrowserStack session URL
        session_url = f"https://automate.browserstack.com/dashboard/v2/builds/latest/sessions/{driver.session_id}"
        logger.info(f"BrowserStack session URL: {session_url}")
        
        return 0
    except Exception as e:
        logger.error(f"❌ Test FAILED: {str(e)}")
        if driver and hasattr(driver, 'session_id'):
            update_test_status(driver.session_id, username, access_key, "failed", str(e))
        return 1
    finally:
        # Quit the driver
        if driver:
            logger.info("Closing WebDriver session")
            driver.quit()

def update_test_status(session_id, username, access_key, status, reason=None):
    """Update the test status in BrowserStack"""
    url = f"https://api.browserstack.com/automate/sessions/{session_id}.json"
    data = {"status": status}
    if reason:
        data["reason"] = reason
    
    try:
        response = requests.put(
            url,
            json=data,
            auth=(username, access_key)
        )
        if response.status_code == 200:
            logger.info(f"Successfully updated test status to {status}")
        else:
            logger.error(f"Failed to update test status: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error updating test status: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting simplified BrowserStack test")
    sys.exit(main())
