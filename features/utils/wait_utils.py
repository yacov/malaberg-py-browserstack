"""
Utility functions for explicit waits and common test operations.
Designed to improve test reliability, especially when running on BrowserStack.
"""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException

class WaitUtils:
    """
    Helper class for explicit waits and common test operations.
    Provides methods to wait for elements with retry logic for flaky tests.
    """
    
    def __init__(self, driver, timeout=10, poll_frequency=0.5):
        """
        Initialize WaitUtils with a WebDriver instance.
        
        Args:
            driver: WebDriver instance
            timeout: Default timeout in seconds
            poll_frequency: How often to poll for the condition
        """
        self.driver = driver
        self.timeout = timeout
        self.poll_frequency = poll_frequency
    
    def wait_for_element_visible(self, locator, timeout=None, message=None):
        """
        Wait for an element to be visible with retry logic for flaky elements.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Timeout in seconds (uses default if None)
            message: Custom error message
            
        Returns:
            The WebElement once it's visible
            
        Raises:
            TimeoutException if the element is not visible within the timeout
        """
        timeout = timeout or self.timeout
        message = message or f"Element {locator} not visible after {timeout} seconds"
        
        # Use a longer timeout with retry logic for flaky elements
        end_time = time.time() + timeout
        last_exception = None
        
        while time.time() < end_time:
            try:
                element = WebDriverWait(self.driver, min(2, timeout), self.poll_frequency).until(
                    EC.visibility_of_element_located(locator)
                )
                return element
            except (TimeoutException, StaleElementReferenceException) as e:
                last_exception = e
                # Small sleep before retry
                time.sleep(0.5)
        
        # If we get here, all retries failed
        raise TimeoutException(message) from last_exception
    
    def wait_for_element_clickable(self, locator, timeout=None, message=None):
        """
        Wait for an element to be clickable with retry logic for flaky elements.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Timeout in seconds (uses default if None)
            message: Custom error message
            
        Returns:
            The WebElement once it's clickable
            
        Raises:
            TimeoutException if the element is not clickable within the timeout
        """
        timeout = timeout or self.timeout
        message = message or f"Element {locator} not clickable after {timeout} seconds"
        
        # Use a longer timeout with retry logic for flaky elements
        end_time = time.time() + timeout
        last_exception = None
        
        while time.time() < end_time:
            try:
                element = WebDriverWait(self.driver, min(2, timeout), self.poll_frequency).until(
                    EC.element_to_be_clickable(locator)
                )
                return element
            except (TimeoutException, StaleElementReferenceException) as e:
                last_exception = e
                # Small sleep before retry
                time.sleep(0.5)
        
        # If we get here, all retries failed
        raise TimeoutException(message) from last_exception
    
    def safe_click(self, element, timeout=None, retry_count=3):
        """
        Safely click an element with retry logic for flaky clicks.
        
        Args:
            element: WebElement to click
            timeout: Timeout in seconds for each attempt
            retry_count: Number of times to retry if click fails
            
        Returns:
            True if click was successful
            
        Raises:
            WebDriverException if all click attempts fail
        """
        timeout = timeout or self.timeout
        last_exception = None
        
        for attempt in range(retry_count):
            try:
                # Scroll element into view before clicking
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                
                # Small wait after scrolling
                time.sleep(0.5)
                
                # Try regular click first
                element.click()
                return True
            except (StaleElementReferenceException, WebDriverException) as e:
                last_exception = e
                
                # If regular click fails, try JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_e:
                    # If both methods fail, retry after a short delay
                    time.sleep(1)
                    continue
        
        # If we get here, all retries failed
        raise WebDriverException(f"Failed to click element after {retry_count} attempts") from last_exception
    
    def wait_for_page_load(self, timeout=None):
        """
        Wait for page to fully load.
        
        Args:
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            True if page loaded successfully
            
        Raises:
            TimeoutException if page doesn't load within timeout
        """
        timeout = timeout or self.timeout
        
        # Wait for document.readyState to be 'complete'
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Additional wait for any JavaScript frameworks to finish loading
        try:
            # Wait for jQuery if it's present
            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0")
            )
        except TimeoutException:
            # jQuery might not be present or might be taking too long, continue anyway
            pass
        
        return True
    
    def wait_for_url_contains(self, text, timeout=None):
        """
        Wait for URL to contain specific text.
        
        Args:
            text: Text to look for in URL
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            True if URL contains the text
            
        Raises:
            TimeoutException if URL doesn't contain text within timeout
        """
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.url_contains(text)
        )
    
    def wait_for_text_in_element(self, locator, text, timeout=None):
        """
        Wait for element to contain specific text.
        
        Args:
            locator: Tuple of (By, selector)
            text: Text to look for in element
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            True if element contains the text
            
        Raises:
            TimeoutException if element doesn't contain text within timeout
        """
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element(locator, text)
        )
    
    def wait_for_staleness(self, element, timeout=None):
        """
        Wait for an element to become stale (no longer attached to DOM).
        Useful for waiting for page transitions.
        
        Args:
            element: WebElement to check for staleness
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            True if element becomes stale
            
        Raises:
            TimeoutException if element doesn't become stale within timeout
        """
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.staleness_of(element)
        )
