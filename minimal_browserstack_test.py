"""
Minimal BrowserStack Test
This script follows BrowserStack's recommended practices for running tests on real mobile devices.
"""

import os
import sys
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Get BrowserStack credentials
username = os.environ.get('BROWSERSTACK_USERNAME')
access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')

if not username or not access_key:
    print("Error: BrowserStack credentials not found in environment variables")
    sys.exit(1)

# Set up desired capabilities for Samsung Galaxy S22
desired_caps = {
    # Set device
    'bstack:options': {
        'deviceName': 'Samsung Galaxy S22',
        'osVersion': '12.0',
        'realMobile': 'true',
        
        # Set test details
        'projectName': 'Malaberg Shopify Test',
        'buildName': 'Minimal Test',
        'sessionName': 'Shopify Main Page',
        
        # Set BrowserStack credentials
        'userName': username,
        'accessKey': access_key,
        
        # Set debug options
        'debug': 'true',
        'networkLogs': 'true'
    }
}

# Initialize the driver
print("Setting up WebDriver...")
options = webdriver.ChromeOptions()
for key, value in desired_caps.items():
    options.set_capability(key, value)

# Create the driver
try:
    driver = webdriver.Remote(
        command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
        options=options
    )
    
    print(f"WebDriver session created with ID: {driver.session_id}")
    
    # Navigate to the Shopify homepage
    print("Navigating to Shopify homepage...")
    driver.get("https://physicalnutrition-uk.myshopify.com/")
    
    # Wait for the main navigation to be visible
    print("Waiting for main navigation...")
    wait = WebDriverWait(driver, 30)
    nav_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "nav.header__inline-menu")))
    
    # Check if the navigation is visible
    if nav_element.is_displayed():
        print("✅ PASS: Main navigation is visible")
        
        # Take a screenshot
        screenshot_path = f"shopify_test_{time.strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Print session URL
        print(f"BrowserStack session URL: https://automate.browserstack.com/dashboard/v2/builds/latest/sessions/{driver.session_id}")
        
        # Mark test as passed
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Main navigation found!"}}'
        )
    else:
        print("❌ FAIL: Main navigation is not visible")
        
        # Mark test as failed
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Main navigation not found"}}'
        )
    
    print("Test completed successfully")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    
    # Try to mark the test as failed if driver exists
    try:
        if 'driver' in locals():
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test encountered an error"}}'
            )
    except:
        pass
    
    sys.exit(1)
    
finally:
    # Quit the driver
    if 'driver' in locals():
        print("Closing WebDriver session...")
        driver.quit()

print("Test execution completed")
