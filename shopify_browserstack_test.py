#!/usr/bin/env python
"""
Shopify BrowserStack Test

This script runs a Shopify test on BrowserStack with proper thread management to prevent
the "RuntimeError: can't create new thread at interpreter shutdown" error.

Usage:
    python shopify_browserstack_test.py

Author: Cascade AI Assistant
Date: 2025-03-23
"""

import os
import sys
import time
import json
import logging
import threading
import atexit
import signal
import gc
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"shopify_test_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s:%(thread)d] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Global variables for thread tracking
_ACTIVE_THREADS = set()
_BROWSER_THREADS = set()
_WEBDRIVER_SESSIONS = []
_CLEANUP_REGISTERED = False

def track_threads():
    """Track and record all active threads"""
    global _ACTIVE_THREADS
    current_threads = set(threading.enumerate())
    new_threads = current_threads - _ACTIVE_THREADS
    
    if new_threads:
        logger.info(f"New threads detected: {len(new_threads)}")
        for thread in new_threads:
            logger.info(f"New thread: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon})")
            # Mark browser-related threads
            if any(keyword in thread.name.lower() for keyword in ["browserstack", "selenium", "webdriver", "remote"]):
                _BROWSER_THREADS.add(thread)
                logger.info(f"Marked as browser thread: {thread.name}")
    
    _ACTIVE_THREADS = current_threads
    return new_threads

def dump_thread_info(prefix="threads"):
    """Dump thread information to a JSON file for analysis"""
    thread_info = []
    for thread in threading.enumerate():
        thread_info.append({
            "name": thread.name,
            "id": thread.ident,
            "daemon": thread.daemon,
            "alive": thread.is_alive()
        })
    
    # Save to JSON file
    thread_file = log_dir / f"{prefix}_{timestamp}.json"
    with open(thread_file, "w") as f:
        json.dump(thread_info, f, indent=2)
    
    logger.info(f"Thread information saved to {thread_file}")
    return thread_info

def cleanup_webdriver_sessions():
    """Clean up all WebDriver sessions"""
    global _WEBDRIVER_SESSIONS
    
    logger.info(f"Cleaning up {len(_WEBDRIVER_SESSIONS)} WebDriver sessions")
    for driver in _WEBDRIVER_SESSIONS:
        try:
            session_id = driver.session_id
            logger.info(f"Quitting WebDriver session: {session_id}")
            driver.quit()
            logger.info(f"Successfully quit WebDriver session: {session_id}")
        except Exception as e:
            logger.error(f"Error quitting WebDriver session: {str(e)}")
    
    # Clear the sessions list
    _WEBDRIVER_SESSIONS = []

def cleanup_threads():
    """Clean up threads before interpreter shutdown"""
    logger.info("Cleaning up threads before interpreter shutdown")
    
    # First, clean up WebDriver sessions
    cleanup_webdriver_sessions()
    
    # Then, clean up browser-related threads
    for thread in _BROWSER_THREADS:
        if thread.is_alive() and not thread.daemon:
            logger.info(f"Attempting to join browser thread: {thread.name}")
            try:
                thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error joining browser thread {thread.name}: {str(e)}")
    
    # Finally, clean up other non-daemon threads
    for thread in threading.enumerate():
        if thread != threading.current_thread() and not thread.daemon and thread.is_alive():
            logger.info(f"Attempting to join thread: {thread.name}")
            try:
                thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error joining thread {thread.name}: {str(e)}")
    
    # Force garbage collection
    logger.info("Running garbage collection")
    gc.collect()

def signal_handler(signum, frame):
    """Handle signals to ensure proper cleanup"""
    logger.info(f"Signal {signum} received, initiating cleanup")
    cleanup_threads()
    sys.exit(1)

def register_cleanup():
    """Register cleanup handlers"""
    global _CLEANUP_REGISTERED
    if not _CLEANUP_REGISTERED:
        # Register cleanup function to run at interpreter shutdown
        atexit.register(cleanup_threads)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        _CLEANUP_REGISTERED = True
        logger.info("Cleanup handlers registered")

def get_browserstack_url(driver, build_name=None):
    """Get the BrowserStack session URL safely from the driver capabilities"""
    try:
        session_id = driver.session_id
        
        # Try different ways to get the build name from capabilities
        if build_name is None:
            if 'bstack:options' in driver.capabilities:
                build_name = driver.capabilities['bstack:options'].get('buildName')
            elif 'browserstack.buildName' in driver.capabilities:
                build_name = driver.capabilities['browserstack.buildName']
            else:
                # Use a default build name if not found in capabilities
                build_name = f'Shopify Tests {time.strftime("%Y-%m-%d %H:%M")}'
        
        # Format the build name for URL
        formatted_build = build_name.replace(' ', '%20')
        
        # Create the BrowserStack URL
        bs_url = f"https://automate.browserstack.com/builds/{formatted_build}/sessions/{session_id}"
        logger.info(f"BrowserStack session URL: {bs_url}")
        return bs_url
    except Exception as e:
        logger.error(f"Error getting BrowserStack URL: {str(e)}")
        # Return a generic URL that will at least show the session
        return f"https://automate.browserstack.com/dashboard/v2/search?query={driver.session_id}"

def create_browserstack_driver():
    """Create a WebDriver instance for BrowserStack with proper error handling"""
    # Get BrowserStack credentials
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    
    if not username or not access_key:
        logger.error("BrowserStack credentials not found in environment variables")
        raise ValueError("BrowserStack credentials not found. Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables.")
    
    logger.info("Setting up BrowserStack capabilities")
    options = webdriver.ChromeOptions()
    build_name = f'Shopify Tests {time.strftime("%Y-%m-%d %H:%M")}'
    bstack_options = {
        'deviceName': 'Samsung Galaxy S22',
        'osVersion': '12.0',
        'realMobile': 'true',
        'projectName': 'Malaberg Shopify Tests',
        'buildName': build_name,
        'sessionName': 'Shopify Main Page Test',
        'debug': 'true',
        'consoleLogs': 'verbose',
        'networkLogs': 'true',
        'userName': username,
        'accessKey': access_key
    }
    options.set_capability('bstack:options', bstack_options)
    
    # Track threads before creating WebDriver
    before_threads = set(threading.enumerate())
    
    # Create WebDriver instance
    logger.info("Creating BrowserStack WebDriver instance")
    try:
        driver = webdriver.Remote(
            command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
            options=options
        )
        
        # Track the session
        global _WEBDRIVER_SESSIONS
        _WEBDRIVER_SESSIONS.append(driver)
        
        # Track new threads after WebDriver creation
        after_threads = set(threading.enumerate())
        new_threads = after_threads - before_threads
        logger.info(f"Created {len(new_threads)} new threads after WebDriver initialization")
        
        # Log session information
        session_id = driver.session_id
        logger.info(f"WebDriver session created with ID: {session_id}")
        
        # Get BrowserStack session URL using the new helper function
        bs_url = get_browserstack_url(driver, build_name)
        logger.info(f"BrowserStack session URL: {bs_url}")
        
        return driver
    except Exception as e:
        logger.error(f"Failed to create BrowserStack WebDriver: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def run_shopify_test():
    """Run a Shopify test on BrowserStack with proper thread management"""
    logger.info("Starting Shopify main page test on Samsung Galaxy S22")
    
    # Register cleanup handlers
    register_cleanup()
    
    # Track initial threads
    logger.info("Initial thread state:")
    track_threads()
    dump_thread_info("initial_threads")
    
    driver = None
    test_status = "failed"  # Default status
    test_reason = "Test did not complete"  # Default reason
    
    try:
        # Create WebDriver instance
        logger.info("Setting up WebDriver with BrowserStack capabilities")
        driver = create_browserstack_driver()
        
        # Navigate to Shopify homepage
        shopify_url = os.environ.get("SHOPIFY_URL", "https://physicalnutrition-uk.myshopify.com/")
        logger.info(f"Navigating to Shopify homepage: {shopify_url}")
        driver.get(shopify_url)
        
        # Wait for page to load
        logger.info("Waiting for page to load")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check for main navigation
        logger.info("Checking for main navigation")
        nav = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav, .header, .main-nav"))
        )
        logger.info("Navigation found successfully")
        
        # Set test as passed
        test_status = "passed"
        test_reason = "Navigation found successfully"
        
        return 0
    except Exception as e:
        logger.error(f"Error running Shopify test: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Set test as failed with specific reason
        test_status = "failed"
        test_reason = f"Test failed: {str(e)}"
        
        return 1
    finally:
        # Update test status in BrowserStack
        if driver:
            try:
                # Mark test status in BrowserStack
                status_script = f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"{test_status}", "reason": "{test_reason}"}}}}'
                driver.execute_script(status_script)
                logger.info(f"Successfully updated test status to {test_status}: {test_reason}")
                
                # Log BrowserStack session URL
                bs_url = get_browserstack_url(driver)
                logger.info(f"BrowserStack session URL: {bs_url}")
            except Exception as e:
                logger.error(f"Error updating test status: {str(e)}")
            
            # Clean up WebDriver session
            logger.info("Quitting WebDriver session")
            try:
                driver.quit()
                logger.info("WebDriver session closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver session: {str(e)}")
        
        # Dump final thread information
        dump_thread_info("final_threads")
        
        # Final cleanup
        logger.info("Performing final cleanup")
        cleanup_threads()

def main():
    """Main function to run the Shopify BrowserStack test"""
    try:
        # Run the Shopify test
        exit_code = run_shopify_test()
        
        # Log completion
        logger.info(f"Test completed with exit code: {exit_code}")
        
        # Return the exit code
        return exit_code
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        # Ensure all resources are cleaned up
        cleanup_threads()

if __name__ == "__main__":
    # Run the main function and exit with the appropriate code
    exit_code = main()
    sys.exit(exit_code)
