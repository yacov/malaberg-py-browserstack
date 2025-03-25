"""
Direct BrowserStack Test Script
This script bypasses the BrowserStack SDK and directly uses Selenium with BrowserStack capabilities
to avoid threading issues during interpreter shutdown.
"""

import os
import sys
import time
import logging
import traceback
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s][%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("direct_browserstack_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("browserstack_direct")

def setup_driver():
    """Set up WebDriver with BrowserStack capabilities"""
    # Get BrowserStack credentials
    bs_user = os.environ.get('BROWSERSTACK_USERNAME')
    bs_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    if not bs_user or not bs_key:
        logger.error("BrowserStack credentials not found in environment variables")
        sys.exit(1)
    
    # Set up BrowserStack capabilities for Samsung Galaxy S22
    options = webdriver.ChromeOptions()
    bstack_options = {
        'deviceName': 'Samsung Galaxy S22',
        'osVersion': '12.0',
        'realMobile': 'true',
        'projectName': 'Malaberg Shopify Tests',
        'buildName': 'Direct BrowserStack Test',
        'sessionName': 'Shopify Homepage Test',
        'local': 'false',
        'debug': 'true',
        'networkLogs': 'true',
        'userName': bs_user,
        'accessKey': bs_key
    }
    options.set_capability('bstack:options', bstack_options)
    
    # Create WebDriver instance
    logger.info("Creating WebDriver instance with BrowserStack capabilities")
    driver = webdriver.Remote(
        command_executor=f'https://{bs_user}:{bs_key}@hub-cloud.browserstack.com/wd/hub',
        options=options
    )
    
    return driver

def run_test():
    """Run the Shopify homepage test"""
    driver = None
    try:
        # Set up WebDriver
        driver = setup_driver()
        
        # Navigate to Shopify homepage
        logger.info("Navigating to Shopify homepage")
        driver.get("https://physicalnutrition-uk.myshopify.com/")
        
        # Wait for main navigation to be visible
        logger.info("Waiting for main navigation to be visible")
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "nav.header__inline-menu"))
        )
        
        # Verify main navigation is present
        nav_element = driver.find_element(By.CSS_SELECTOR, "nav.header__inline-menu")
        if nav_element.is_displayed():
            logger.info("Main navigation is visible - Test PASSED")
            mark_test_status(driver.session_id, "passed", "Main navigation is visible")
        else:
            logger.error("Main navigation is not visible - Test FAILED")
            mark_test_status(driver.session_id, "failed", "Main navigation is not visible")
        
        # Take screenshot
        logger.info("Taking screenshot")
        driver.save_screenshot("shopify_homepage.png")
        
        # Print BrowserStack session URL
        session_url = f"https://automate.browserstack.com/builds/latest/sessions/{driver.session_id}"
        logger.info(f"BrowserStack session URL: {session_url}")
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error(traceback.format_exc())
        if driver and driver.session_id:
            mark_test_status(driver.session_id, "failed", str(e))
        return False
    finally:
        # Clean up
        if driver:
            logger.info("Closing WebDriver session")
            driver.quit()

def mark_test_status(session_id, status, reason=None):
    """Mark the test status in BrowserStack"""
    import requests
    
    bs_user = os.environ.get('BROWSERSTACK_USERNAME')
    bs_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    url = f"https://api.browserstack.com/automate/sessions/{session_id}.json"
    
    # Prepare data for the API call
    data = {'status': status}
    if reason:
        data['reason'] = reason
    
    try:
        response = requests.put(
            url,
            json=data,
            auth=(bs_user, bs_key)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully marked test as {status}")
        else:
            logger.error(f"Failed to mark test status: {response.text}")
    except Exception as e:
        logger.error(f"Error marking test status: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting direct BrowserStack test")
    success = run_test()
    
    if success:
        logger.info("Test completed successfully")
        sys.exit(0)
    else:
        logger.error("Test failed")
        sys.exit(1)
