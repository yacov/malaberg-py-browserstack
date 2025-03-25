import logging
from behave import given, when
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

@given('the browser is open')
def step_browser_is_open(context):
    """Verify that the browser is initialized and ready."""
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Browser Initialization Check", "level": "info"}}'
        )
        assert hasattr(context, 'browser'), "Browser is not initialized"
        assert context.browser is not None, "Browser is not initialized"
        
        # Verify browser is responsive
        WebDriverWait(context.browser, 10).until(
            lambda x: x.execute_script('return document.readyState') == 'complete'
        )
        
        context.logger.info("Browser is initialized and ready")
    except Exception as e:
        context.logger.error(f"Browser initialization check failed: {e}")
        raise

@given('the website is accessible')
def step_website_is_accessible(context):
    """Verify website is accessible by loading the main page."""
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Website Accessibility Check", "level": "info"}}'
        )
        
        # Get environment-specific URL
        env = context.config.userdata.get('ENV', 'dev')
        target_url = context.base_urls.get(env, context.base_url)
        
        context.browser.get(target_url)
        
        # Wait for page to be fully loaded
        WebDriverWait(context.browser, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Wait for any AJAX calls to complete
        WebDriverWait(context.browser, 10).until(
            lambda x: x.execute_script('return jQuery.active == 0')
        )
        
        # Verify no error messages are present
        error_elements = context.browser.find_elements(By.CLASS_NAME, 'error-message')
        assert len(error_elements) == 0, "Error message found on page"
        
        context.logger.info(f"Website is accessible at {target_url}")
    except Exception as e:
        context.logger.error(f"Website accessibility check failed: {e}")
        # Add detailed error information to BrowserStack
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", '
            f'{{"arguments": {{"data": "Accessibility Check Failed: {str(e)}", "level": "error"}}}}'
        )
        raise

@given('environment is "{env_name}"')
def step_set_environment(context, env_name):
    """Set the testing environment."""
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", '
            f'{{"arguments": {{"data": "Setting Environment: {env_name}", "level": "info"}}}}'
        )
        
        env_name = env_name.lower()
        assert env_name in context.base_urls, f"Unknown environment: {env_name}"
        
        context.base_url = context.base_urls[env_name]
        context.config.userdata['ENV'] = env_name
        
        context.logger.info(f"Environment set to {env_name}: {context.base_url}")
    except Exception as e:
        context.logger.error(f"Failed to set environment {env_name}: {e}")
        raise