"""
Debug BrowserStack Test
This script runs a test on BrowserStack with detailed logging enabled
to help debug threading issues during interpreter shutdown.
"""

import os
import sys
import time
import logging
import threading
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Configure logging
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'browserstack_debug_{time.strftime("%Y%m%d_%H%M%S")}.log')

# Set up logging to file and console with thread information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s:%(thread)d] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Log all active threads at the start
def log_active_threads(prefix=""):
    """Log all active threads"""
    active_threads = threading.enumerate()
    logger.debug(f"{prefix} Active threads ({len(active_threads)}): {[t.name for t in active_threads]}")
    for thread in active_threads:
        logger.debug(f"Thread: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon})")

def run_test():
    """Run a simple test on BrowserStack"""
    # Get BrowserStack credentials
    username = os.environ.get('BROWSERSTACK_USERNAME')
    access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    if not username or not access_key:
        logger.error("BrowserStack credentials not found in environment variables")
        return 1
    
    logger.info("Starting BrowserStack test with debug logging")
    log_active_threads("Before WebDriver setup")
    
    driver = None
    try:
        # Set up Chrome options
        logger.debug("Setting up Chrome options")
        options = webdriver.ChromeOptions()
        
        # Set BrowserStack options
        bstack_options = {
            'deviceName': 'Samsung Galaxy S22',
            'osVersion': '12.0',
            'realMobile': 'true',
            'projectName': 'Debug Test',
            'buildName': f'Debug Build {time.strftime("%Y-%m-%d %H:%M")}',
            'sessionName': 'Debug Session',
            'debug': 'true',
            'consoleLogs': 'verbose',
            'networkLogs': 'true',
            'userName': username,
            'accessKey': access_key
        }
        options.set_capability('bstack:options', bstack_options)
        
        # Create WebDriver instance
        logger.info("Creating WebDriver instance")
        driver = webdriver.Remote(
            command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
            options=options
        )
        
        session_id = driver.session_id
        logger.info(f"WebDriver session created with ID: {session_id}")
        
        # Log active threads after WebDriver setup
        log_active_threads("After WebDriver setup")
        
        # Navigate to a simple page
        logger.info("Navigating to example.com")
        driver.get("https://example.com")
        
        # Wait for the page to load
        logger.info("Waiting for page to load")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Log active threads after page load
        log_active_threads("After page load")
        
        # Take a screenshot
        screenshot_path = os.path.join(log_dir, f'screenshot_{time.strftime("%Y%m%d_%H%M%S")}.png')
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        # Log BrowserStack session URL
        logger.info(f"BrowserStack session URL: https://automate.browserstack.com/dashboard/v2/builds/latest/sessions/{session_id}")
        
        # Mark test as passed
        logger.info("Marking test as passed")
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test completed successfully"}}'
        )
        
        return 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to mark the test as failed if driver exists
        if driver and hasattr(driver, 'session_id'):
            try:
                driver.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test encountered an error"}}'
                )
            except:
                pass
        
        return 1
    finally:
        # Log active threads before driver quit
        log_active_threads("Before driver quit")
        
        # Quit the driver
        if driver:
            logger.info("Quitting WebDriver session")
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error quitting WebDriver session: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Log active threads after driver quit
        log_active_threads("After driver quit")

# Register a cleanup function to run at interpreter shutdown
def cleanup():
    """Cleanup function to run at interpreter shutdown"""
    logger.info("Interpreter shutdown detected, running cleanup")
    log_active_threads("During interpreter shutdown")
    
    # Try to join all non-daemon threads
    for thread in threading.enumerate():
        if not thread.daemon and thread != threading.current_thread():
            logger.info(f"Attempting to join thread: {thread.name}")
            try:
                thread.join(timeout=1.0)
                logger.info(f"Successfully joined thread: {thread.name}")
            except Exception as e:
                logger.error(f"Error joining thread {thread.name}: {str(e)}")

# Register the cleanup function
import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    # Log Python and package versions
    logger.info(f"Python version: {sys.version}")
    try:
        import selenium
        logger.info(f"Selenium version: {selenium.__version__}")
    except:
        logger.error("Could not determine Selenium version")
    
    # Log initial thread state
    log_active_threads("Initial state")
    
    # Run the test
    exit_code = run_test()
    
    # Log final thread state
    log_active_threads("Final state")
    
    # Write a marker to indicate normal script termination
    logger.info("Script execution completed normally")
    
    # Exit with the appropriate code
    sys.exit(exit_code)
