#!/usr/bin/env python
"""
BrowserStack Fix Script

This script provides a comprehensive solution to the "RuntimeError: can't create new thread at interpreter shutdown" 
error when running BrowserStack tests. It implements proper thread management, WebDriver session handling,
and detailed logging to help diagnose and fix the issue.

Usage:
    python browserstack_fix.py

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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"browserstack_fix_{timestamp}.log"

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

def create_browserstack_driver(test_name="BrowserStack Test"):
    """Create a WebDriver instance for BrowserStack with proper error handling"""
    # Get BrowserStack credentials
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    
    if not username or not access_key:
        logger.error("BrowserStack credentials not found in environment variables")
        raise ValueError("BrowserStack credentials not found. Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables.")
    
    logger.info("Setting up BrowserStack capabilities")
    options = webdriver.ChromeOptions()
    bstack_options = {
        'deviceName': 'Samsung Galaxy S22',
        'osVersion': '12.0',
        'realMobile': 'true',
        'projectName': 'Malaberg Shopify Tests',
        'buildName': f'Fix Tests {time.strftime("%Y-%m-%d %H:%M")}',
        'sessionName': test_name,
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
        
        # Get BrowserStack session URL
        session_url = f"https://automate.browserstack.com/builds/{bstack_options['buildName'].replace(' ', '%20')}/sessions/{session_id}"
        logger.info(f"BrowserStack session URL: {session_url}")
        
        return driver
    except Exception as e:
        logger.error(f"Failed to create BrowserStack WebDriver: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def run_shopify_test():
    """Run a simple Shopify test on BrowserStack with proper thread management"""
    logger.info("Starting Shopify test with proper thread management")
    
    # Register cleanup handlers
    register_cleanup()
    
    # Track initial threads
    logger.info("Initial thread state:")
    track_threads()
    dump_thread_info("initial_threads")
    
    driver = None
    try:
        # Create WebDriver instance
        driver = create_browserstack_driver("Shopify Main Page Test")
        
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
        try:
            nav = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav, .header, .main-nav"))
            )
            logger.info("Navigation found successfully")
            
            # Mark test as passed in BrowserStack
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Navigation found successfully"}}'
            )
            logger.info("Marked test as passed in BrowserStack")
            
        except Exception as e:
            logger.error(f"Error finding navigation: {str(e)}")
            
            # Mark test as failed in BrowserStack
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Navigation not found"}}'
            )
            logger.info("Marked test as failed in BrowserStack")
            
        # Dump thread information after test
        dump_thread_info("after_test_threads")
        
    except Exception as e:
        logger.error(f"Error running Shopify test: {str(e)}")
        logger.error(traceback.format_exc())
        
        if driver:
            try:
                # Mark test as failed in BrowserStack
                driver.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test failed with exception"}}'
                )
            except:
                pass
    finally:
        # Clean up WebDriver session
        if driver:
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
        
        logger.info("Test completed")

def check_browserstack_status():
    """Check the status of BrowserStack sessions using the BrowserStack API"""
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    
    if not username or not access_key:
        logger.error("BrowserStack credentials not found in environment variables")
        return
    
    import requests
    from requests.auth import HTTPBasicAuth
    
    logger.info("Checking BrowserStack session status")
    
    try:
        # Get recent sessions
        response = requests.get(
            "https://api.browserstack.com/automate/sessions.json",
            auth=HTTPBasicAuth(username, access_key)
        )
        
        if response.status_code == 200:
            sessions = response.json()
            logger.info(f"Found {len(sessions)} recent BrowserStack sessions")
            
            # Log session information
            for session in sessions:
                logger.info(f"Session ID: {session['automation_session']['hashed_id']}")
                logger.info(f"Status: {session['automation_session']['status']}")
                logger.info(f"Browser: {session['automation_session']['browser']}")
                logger.info(f"OS: {session['automation_session']['os']}")
                logger.info(f"Device: {session['automation_session'].get('device', 'N/A')}")
                logger.info(f"Build: {session['automation_session']['build_name']}")
                logger.info(f"Project: {session['automation_session']['project_name']}")
                logger.info(f"Created At: {session['automation_session']['created_at']}")
                logger.info(f"Session URL: {session['automation_session']['public_url']}")
                logger.info("-" * 50)
        else:
            logger.error(f"Failed to get BrowserStack sessions: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"Error checking BrowserStack status: {str(e)}")
        logger.error(traceback.format_exc())

def main():
    """Main function to run the BrowserStack fix script"""
    logger.info("Starting BrowserStack fix script")
    
    # Register cleanup handlers
    register_cleanup()
    
    # Check BrowserStack status
    check_browserstack_status()
    
    # Run Shopify test
    run_shopify_test()
    
    # Final cleanup
    logger.info("Script completed successfully")

if __name__ == "__main__":
    main()
