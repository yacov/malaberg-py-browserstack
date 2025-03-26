import os
import sys
import time
import json
import logging
import threading
import atexit
import signal
import gc
from behave.model_core import Status
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import requests
from features.utils.shopify_mcp_client import get_shopify_mcp_client

# Global variables for thread tracking and MCP testing
_ACTIVE_THREADS = set()
_BROWSER_THREADS = set()
_CLEANUP_REGISTERED = False
SHOPIFY_TEST_ORDERS = []

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s:%(thread)d] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("behave_run.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

def _track_threads():
    """Track and record all active threads"""
    global _ACTIVE_THREADS
    current_threads = set(threading.enumerate())
    new_threads = current_threads - _ACTIVE_THREADS
    
    if new_threads:
        logger.info(f"New threads detected: {len(new_threads)}")
        for thread in new_threads:
            logger.info(f"New thread: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon})")
            # Mark browser-related threads
            if "browserstack" in thread.name.lower() or "selenium" in thread.name.lower() or "webdriver" in thread.name.lower():
                _BROWSER_THREADS.add(thread)
    
    _ACTIVE_THREADS = current_threads
    return new_threads

def _cleanup_threads():
    """Clean up threads before interpreter shutdown"""
    logger.info("Cleaning up threads before interpreter shutdown")
    
    # First, clean up browser-related threads
    for thread in _BROWSER_THREADS:
        if thread.is_alive() and not thread.daemon:
            logger.info(f"Attempting to join browser thread: {thread.name}")
            try:
                thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error joining browser thread {thread.name}: {str(e)}")
    
    # Then, clean up other non-daemon threads
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

def _signal_handler(signum, frame):
    """Handle signals to ensure proper cleanup"""
    logger.info(f"Signal {signum} received, initiating cleanup")
    _cleanup_threads()
    sys.exit(1)

def _register_cleanup():
    """Register cleanup handlers"""
    global _CLEANUP_REGISTERED
    if not _CLEANUP_REGISTERED:
        # Register cleanup function to run at interpreter shutdown
        atexit.register(_cleanup_threads)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)
        
        _CLEANUP_REGISTERED = True
        logger.info("Cleanup handlers registered")

def _is_browserstack_test():
    """
    Check if we're running in BrowserStack environment
    """
    return 'BROWSERSTACK_USERNAME' in os.environ and 'BROWSERSTACK_ACCESS_KEY' in os.environ

def _is_using_real_mcp_server():
    """
    Check if we should use real MCP server
    """
    return 'SHOPIFY_MCP_SERVER' in os.environ and 'SHOPIFY_API_KEY' in os.environ and os.environ.get('USE_MOCK_MCP') != 'true'

def before_all(context):
    """
    Runs at the start of the entire behave run.
    """
    global _CLEANUP_REGISTERED
    if not _CLEANUP_REGISTERED:
        _register_cleanup()
        _CLEANUP_REGISTERED = True

    logger.info("Initial thread state:")
    _track_threads()

    # Load environment variables first
    load_dotenv()
    
    # Set up context variables
    context.config.setup_logging()
    
    # Add logger to context for access in page objects
    context.logger = logger
    
    # Log environment variables for debugging
    logger.info(f"USE_MOCK_MCP: {os.environ.get('USE_MOCK_MCP')}")
    logger.info(f"SHOPIFY_MCP_SERVER: {os.environ.get('SHOPIFY_MCP_SERVER')}")
    logger.info(f"SHOPIFY_API_KEY exists: {'SHOPIFY_API_KEY' in os.environ}")
    
    # Initialize shopify client based on environment
    if _is_using_real_mcp_server():
        logger.info("Using REAL MCP server for testing")
        from features.utils.shopify_mcp_client import get_shopify_mcp_client
        context.shopify_mcp_client = get_shopify_mcp_client(os.environ.get('SHOPIFY_MCP_SERVER'))
    else:
        logger.info("Using MOCK MCP server for testing")
        from features.mocks.mock_mcp_server import mock_mcp_server
        context.shopify_mcp_server = os.environ.get('SHOPIFY_MCP_SERVER', 'http://localhost:3000')
    
    # Set up base URLs
    context.dev_url = os.environ.get('DEV_URL')
    context.stage_url = os.environ.get('STAGE_URL')
    context.base_url = os.environ.get('BASE_URL')
    context.shopify_url = os.environ.get('SHOPIFY_URL')
    
    # Set up BrowserStack credentials
    context.browserstack_username = os.environ.get('BROWSERSTACK_USERNAME')
    context.browserstack_access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    # Set up Shopify MCP client
    context.shopify_api_key = os.environ.get('SHOPIFY_API_KEY')
    context.shopify_mcp_server = os.environ.get('SHOPIFY_MCP_SERVER', 'http://localhost:3000')
    
    # Check if we should use mock MCP server
    context.use_mock_mcp = not _is_using_real_mcp_server()
    
    # Set up MCP client functions
    if context.use_mock_mcp:
        logger.info("Using MOCK MCP server for testing")
        from features.mocks.mock_mcp_server import (
            mcp1_get_orders, mcp1_get_order, mcp1_get_customers, 
            mcp1_create_draft_order, mcp1_complete_draft_order, 
            mcp1_tag_customer, mcp1_get_products, mcp1_create_discount
        )
    else:
        logger.info(f"Using REAL MCP server: {context.shopify_mcp_server}")
        # Use the real MCP client functions we defined below
    
    # Add MCP helper methods to context
    context.mcp1_get_orders = mcp1_get_orders
    context.mcp1_get_order = mcp1_get_order
    context.mcp1_get_customers = mcp1_get_customers
    context.mcp1_create_draft_order = mcp1_create_draft_order
    context.mcp1_complete_draft_order = mcp1_complete_draft_order
    context.mcp1_tag_customer = mcp1_tag_customer
    context.mcp1_get_products = mcp1_get_products
    context.mcp1_create_discount = mcp1_create_discount
    
    # Set up test run attributes
    context.retries = {}
    context.max_retries = 2
    context.results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'untested': 0,
        'scenarios': []
    }
    context.SHOPIFY_TEST_ORDERS = []
    
    # Create WebDriver once for all scenarios
    logger.info("Creating WebDriver for the entire test run")
    
    # Set up BrowserStack capabilities if running on BrowserStack
    if hasattr(context, 'config') and hasattr(context.config, 'userdata') and 'BROWSERSTACK_USERNAME' in context.config.userdata:
        # Using BrowserStack
        logger.info("Setting up BrowserStack capabilities")
        
        options = webdriver.ChromeOptions()
        bstack_options = {
            'deviceName': 'Samsung Galaxy S22',
            'osVersion': '12.0',
            'realMobile': 'true',
            'projectName': 'Malaberg Shopify Tests',
            'buildName': f'Behave Tests {time.strftime("%Y-%m-%d %H:%M")}',
            'sessionName': 'Test Run',
            'debug': 'true',
            'consoleLogs': 'verbose',
            'networkLogs': 'true',
            'userName': context.browserstack_username,
            'accessKey': context.browserstack_access_key
        }
        options.set_capability('bstack:options', bstack_options)
        
        # Create WebDriver instance
        logger.info("Creating BrowserStack WebDriver instance")
        try:
            context.driver = webdriver.Remote(
                command_executor=f'https://{context.browserstack_username}:{context.browserstack_access_key}@hub-cloud.browserstack.com/wd/hub',
                options=options
            )
            context.browser = context.driver
            context.wait = WebDriverWait(context.driver, 30)
            
            # Track new threads after WebDriver creation
            _track_threads()
            
        except Exception as e:
            logger.error(f"Failed to create BrowserStack WebDriver: {str(e)}")
            raise
    else:
        # Local WebDriver setup
        logger.info("Setting up local WebDriver")
        try:
            service = Service(ChromeDriverManager().install())
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            context.driver = webdriver.Chrome(service=service, options=options)
            context.browser = context.driver
            context.wait = WebDriverWait(context.driver, 30)
            
            # Track new threads after WebDriver creation
            _track_threads()
            
        except Exception as e:
            logger.error(f"Failed to create local WebDriver: {str(e)}")
            raise

def before_scenario(context, scenario):
    """
    Runs before each scenario.
    """
    # Track threads before scenario
    logger.info(f"Starting scenario: {scenario.name}")
    context.scenario_threads = set(threading.enumerate())
    
    # Set up retry tracking
    scenario_id = f"{scenario.filename}:{scenario.line}:{scenario.name}"
    if scenario_id not in context.retries:
        context.retries[scenario_id] = 0
    
    # Update BrowserStack session name if using BrowserStack
    if hasattr(context, 'config') and hasattr(context.config, 'userdata') and 'BROWSERSTACK_USERNAME' in context.config.userdata:
        try:
            context.driver.execute_script(
                f'browserstack_executor: {{"action": "setSessionName", "arguments": {{"name": "{scenario.name}"}}}}'
            )
            logger.info(f"Updated BrowserStack session name to: {scenario.name}")
        except Exception as e:
            logger.error(f"Failed to update BrowserStack session name: {str(e)}")

def after_scenario(context, scenario):
    """
    Runs after each scenario.
    """
    logger.info(f"Finishing scenario: {scenario.name} with status: {scenario.status}")
    
    # Track threads created during scenario
    current_threads = set(threading.enumerate())
    new_threads = current_threads - context.scenario_threads
    logger.info(f"Scenario created {len(new_threads)} new threads")
    
    # Update results
    scenario_result = {
        'name': scenario.name,
        'status': scenario.status.name,
        'duration': scenario.duration,
        'location': f"{scenario.filename}:{scenario.line}"
    }
    context.results['scenarios'].append(scenario_result)
    
    if scenario.status == Status.passed:
        context.results['passed'] += 1
    elif scenario.status == Status.failed:
        context.results['failed'] += 1
        
        # Capture screenshot and page source on failure
        if context.driver:
            try:
                # Create screenshots directory if it doesn't exist
                screenshot_dir = "screenshots"
                if not os.path.exists(screenshot_dir):
                    os.makedirs(screenshot_dir)
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(screenshot_dir, f"FAILED_{scenario.name.replace(' ', '_')}_{timestamp}.png")
                context.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
                
                # Save page source
                page_source_dir = "page_sources"
                if not os.path.exists(page_source_dir):
                    os.makedirs(page_source_dir)
                
                page_source_path = os.path.join(page_source_dir, f"FAILED_{scenario.name.replace(' ', '_')}_{timestamp}.html")
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(context.driver.page_source)
                logger.info(f"Page source saved to {page_source_path}")
                
                # Mark test as failed in BrowserStack
                if hasattr(context, 'config') and hasattr(context.config, 'userdata') and 'BROWSERSTACK_USERNAME' in context.config.userdata:
                    try:
                        error_message = getattr(context, 'error_message', 'Test failed')
                        context.driver.execute_script(
                            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "' + error_message + '"}}'
                        )
                        logger.info("Marked test as failed in BrowserStack")
                    except Exception as e:
                        logger.error(f"Failed to mark test as failed in BrowserStack: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to capture failure evidence: {str(e)}")
    
    # Mark test as passed in BrowserStack if not already marked as failed
    if hasattr(context, 'config') and hasattr(context.config, 'userdata') and 'BROWSERSTACK_USERNAME' in context.config.userdata and scenario.status == Status.passed:
        try:
            context.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test passed successfully"}}'
            )
            logger.info("Marked test as passed in BrowserStack")
        except Exception as e:
            logger.error(f"Failed to mark test as passed in BrowserStack: {str(e)}")
    
    # Check if we need to retry the scenario
    if scenario.status == Status.failed:
        scenario_id = f"{scenario.filename}:{scenario.line}:{scenario.name}"
        if context.retries[scenario_id] < context.max_retries:
            context.retries[scenario_id] += 1
            logger.info(f"Retrying scenario: {scenario.name} (Attempt {context.retries[scenario_id]} of {context.max_retries})")
            scenario.reset()
            # Don't navigate here, let the scenario's Given step handle it

def after_all(context):
    """
    Runs at the end of the entire behave run.
    """
    # Clean up any test orders created during testing
    if hasattr(context, 'SHOPIFY_TEST_ORDERS') and context.SHOPIFY_TEST_ORDERS:
        logger.info(f"Cleaning up {len(context.SHOPIFY_TEST_ORDERS)} test orders")
        for order_id in context.SHOPIFY_TEST_ORDERS:
            try:
                # Note: In a real implementation, cancel orders but don't delete for audit purposes
                logger.info(f"Would cancel test order {order_id}")
            except Exception as e:
                logger.error(f"Error cleaning up test order {order_id}: {str(e)}")
    
    if context.driver:
        try:
            logger.info("Closing WebDriver")
            context.driver.quit()
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")
    
    # Final thread check and cleanup attempt
    logger.info("Final active threads:")
    _track_threads()
    _cleanup_threads()
    
    # Log final results
    logger.info(f"Test run results: {context.results}")

# MCP client helper methods
def mcp1_get_orders(query=None, first=10, **kwargs):
    """Get orders from Shopify"""
    try:
        logging.info(f"Getting orders with query: {query}, first: {first}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.get_orders(query=query, first=first, **kwargs)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_get_orders as mock_get_orders
            return mock_get_orders(query=query, first=first, **kwargs)
            
    except Exception as e:
        logging.error(f"Error getting orders: {str(e)}")
        return {"orders": []}

def mcp1_get_order(orderId):
    """Get specific order details"""
    try:
        logging.info(f"Getting order details for order ID: {orderId}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.get_order(orderId)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_get_order as mock_get_order
            return mock_get_order(orderId)
            
    except Exception as e:
        logging.error(f"Error getting order details: {str(e)}")
        return {}

def mcp1_get_customers(limit=10, next=None):
    """Get customers from Shopify"""
    try:
        logging.info(f"Getting customers with limit: {limit}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.get_customers(limit=limit, next_cursor=next)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_get_customers as mock_get_customers
            return mock_get_customers(limit=limit, next=next)
            
    except Exception as e:
        logging.error(f"Error getting customers: {str(e)}")
        return {"customers": []}

def mcp1_create_draft_order(email, lineItems, note=None, shippingAddress=None):
    """Create a draft order in Shopify"""
    try:
        logging.info(f"Creating draft order for email: {email} with {len(lineItems)} items")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.create_draft_order(email, lineItems, note, shippingAddress)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_create_draft_order as mock_create_draft_order
            return mock_create_draft_order(email, lineItems, note, shippingAddress)
            
    except Exception as e:
        logging.error(f"Error creating draft order: {str(e)}")
        return {}

def mcp1_complete_draft_order(draftOrderId, variantId):
    """Complete a draft order"""
    try:
        logging.info(f"Completing draft order: {draftOrderId}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.complete_draft_order(draftOrderId, variantId)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_complete_draft_order as mock_complete_draft_order
            return mock_complete_draft_order(draftOrderId, variantId)
            
    except Exception as e:
        logging.error(f"Error completing draft order: {str(e)}")
        return {}

def mcp1_tag_customer(customerId, tags):
    """Add tags to a customer"""
    try:
        logging.info(f"Adding tags to customer {customerId}: {tags}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.tag_customer(customerId, tags)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_tag_customer as mock_tag_customer
            return mock_tag_customer(customerId, tags)
            
    except Exception as e:
        logging.error(f"Error tagging customer: {str(e)}")
        return {}

def mcp1_get_products(limit=10, searchTitle=None):
    """Get products from Shopify"""
    try:
        logging.info(f"Getting products with limit: {limit}, searchTitle: {searchTitle}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.get_products(limit=limit, search_title=searchTitle)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_get_products as mock_get_products
            return mock_get_products(limit=limit, searchTitle=searchTitle)
            
    except Exception as e:
        logging.error(f"Error getting products: {str(e)}")
        return {"products": []}

def mcp1_create_discount(code, valueType, value, title, startsAt, endsAt=None, appliesOncePerCustomer=False):
    """Create a basic discount code"""
    try:
        logging.info(f"Creating discount code: {code}, value: {value}, type: {valueType}")
        
        if _is_using_real_mcp_server():
            # Use our client for real MCP server
            client = get_shopify_mcp_client()
            return client.create_discount(code, valueType, value, title, startsAt, endsAt, appliesOncePerCustomer)
        else:
            # Use mock MCP server
            from features.mocks.mock_mcp_server import mcp1_create_discount as mock_create_discount
            return mock_create_discount(code, valueType, value, title, startsAt, endsAt, appliesOncePerCustomer)
            
    except Exception as e:
        logging.error(f"Error creating discount code: {str(e)}")
        return {}
