"""
Shopify Main Page Test on Samsung Galaxy S22
This script runs the Shopify main page test on a Samsung Galaxy S22 real device using BrowserStack.
It bypasses the BrowserStack SDK to avoid threading issues during interpreter shutdown.
"""

import os
import sys
import time
import json
import logging
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/shopify_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

class ShopifyTest:
    def __init__(self):
        self.username = os.environ.get('BROWSERSTACK_USERNAME')
        self.access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
        self.driver = None
        self.session_id = None
        
        if not self.username or not self.access_key:
            logger.error("BrowserStack credentials not found in environment variables")
            sys.exit(1)
    
    def setup(self):
        """Set up the WebDriver with BrowserStack capabilities"""
        try:
            logger.info("Setting up WebDriver with BrowserStack capabilities")
            
            # Set up Chrome options for Samsung Galaxy S22
            options = webdriver.ChromeOptions()
            
            # Set BrowserStack options
            bstack_options = {
                'deviceName': 'Samsung Galaxy S22',
                'osVersion': '12.0',
                'realMobile': 'true',
                'projectName': 'Malaberg Shopify Tests',
                'buildName': f'Shopify Main Page Test {time.strftime("%Y-%m-%d %H:%M")}',
                'sessionName': 'Shopify Main Page Test',
                'debug': 'true',
                'networkLogs': 'true',
                'consoleLogs': 'verbose',
                'video': 'true',
                'userName': self.username,
                'accessKey': self.access_key
            }
            options.set_capability('bstack:options', bstack_options)
            
            # Create the WebDriver instance
            url = f"https://{self.username}:{self.access_key}@hub-cloud.browserstack.com/wd/hub"
            self.driver = webdriver.Remote(command_executor=url, options=options)
            self.session_id = self.driver.session_id
            
            logger.info(f"WebDriver session created with ID: {self.session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set up WebDriver: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def run_test(self):
        """Run the Shopify main page test"""
        try:
            # Navigate to the Shopify homepage
            logger.info("Navigating to Shopify homepage")
            self.driver.get("https://physicalnutrition-uk.myshopify.com/")
            
            # Wait for the page to load
            logger.info("Waiting for page to load")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for main navigation
            logger.info("Checking for main navigation")
            try:
                nav_element = WebDriverWait(self.driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "nav.header__inline-menu"))
                )
                logger.info("✅ Main navigation is visible")
                self.update_test_status("passed", "Main navigation is visible")
            except Exception as e:
                logger.error(f"❌ Main navigation is not visible: {str(e)}")
                self.update_test_status("failed", f"Main navigation is not visible: {str(e)}")
                return False
            
            # Check for logo
            logger.info("Checking for logo")
            try:
                logo_element = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".header__heading-link"))
                )
                logger.info("✅ Logo is visible")
            except Exception as e:
                logger.error(f"❌ Logo is not visible: {str(e)}")
                self.update_test_status("failed", f"Logo is not visible: {str(e)}")
                return False
            
            # Check for product images
            logger.info("Checking for product images")
            try:
                product_images = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card__image"))
                )
                if product_images:
                    logger.info(f"✅ Found {len(product_images)} product images")
                else:
                    logger.warning("⚠️ No product images found, but test continues")
            except Exception as e:
                logger.warning(f"⚠️ Could not find product images: {str(e)}")
            
            # Take a screenshot
            os.makedirs('screenshots', exist_ok=True)
            screenshot_path = f"screenshots/shopify_main_page_{time.strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Test passed
            self.update_test_status("passed", "All checks passed")
            return True
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            logger.error(traceback.format_exc())
            self.update_test_status("failed", str(e))
            return False
    
    def update_test_status(self, status, reason=None):
        """Update the test status in BrowserStack"""
        if not self.session_id:
            logger.error("No session ID available to update test status")
            return
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        data = {"status": status}
        if reason:
            data["reason"] = reason
        
        try:
            response = requests.put(
                url,
                json=data,
                auth=(self.username, self.access_key)
            )
            if response.status_code == 200:
                logger.info(f"Successfully updated test status to {status}")
            else:
                logger.error(f"Failed to update test status: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error updating test status: {str(e)}")
    
    def get_session_details(self):
        """Get the BrowserStack session details"""
        if not self.session_id:
            logger.error("No session ID available to get session details")
            return None
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key)
            )
            if response.status_code == 200:
                session_details = response.json()
                return session_details
            else:
                logger.error(f"Failed to get session details: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting session details: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                logger.info("Quitting WebDriver session")
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error quitting WebDriver session: {str(e)}")
    
    def run(self):
        """Run the complete test flow"""
        try:
            # Set up WebDriver
            if not self.setup():
                return 1
            
            # Run the test
            test_result = self.run_test()
            
            # Get session details
            session_details = self.get_session_details()
            if session_details:
                public_url = session_details.get('automation_session', {}).get('public_url')
                if public_url:
                    logger.info(f"BrowserStack session URL: {public_url}")
                    
                    # Save session details to file
                    os.makedirs('reports', exist_ok=True)
                    with open(f"reports/browserstack_session_{self.session_id}.json", 'w') as f:
                        json.dump(session_details, f, indent=2)
            
            return 0 if test_result else 1
        finally:
            # Clean up
            self.cleanup()

if __name__ == "__main__":
    logger.info("Starting Shopify main page test on Samsung Galaxy S22")
    test = ShopifyTest()
    exit_code = test.run()
    logger.info(f"Test completed with exit code: {exit_code}")
    sys.exit(exit_code)
