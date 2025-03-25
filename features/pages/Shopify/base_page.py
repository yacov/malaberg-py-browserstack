from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
import time
import os
import sys

# Add the project root to the Python path to enable imports from features
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from features.utils.wait_utils import WaitUtils
from features.utils.browserstack_utils import BrowserStackUtils

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, context):
        """
        Initialize the base page
        
        Args:
            context: The behave context
        """
        # Store context for access to scenario information
        self.context = context
        
        # Handle both browserstack context (SDK managed) and local driver
        self.driver = getattr(context, 'driver', None)
        
        # If we're running via BrowserStack SDK, it might be in a different attribute
        if self.driver is None:
            self.driver = getattr(context, 'browser', None)
            
        # If still None, something is wrong with WebDriver initialization
        if self.driver is None:
            raise ValueError("No WebDriver found in context (neither 'driver' nor 'browser' attribute)")
            
        # Create wait object with 10 second timeout by default
        self.wait = WebDriverWait(self.driver, 10)
        
        # Initialize utility classes
        self.wait_utils = WaitUtils(self.driver)
        self.is_browserstack = BrowserStackUtils.is_browserstack_enabled()
        
        # Create BrowserStack utils if running on BrowserStack
        if self.is_browserstack:
            self.bs_utils = BrowserStackUtils(context)
        
    def open(self, url):
        """
        Open a URL
        
        Args:
            url: The URL to open
        """
        self.driver.get(url)
        # Wait for page to fully load
        self.wait_utils.wait_for_page_load()
        
        # Add annotation in BrowserStack
        if self.is_browserstack:
            self.bs_utils.add_session_annotation(f"Navigated to: {url}")
        
    def wait_for_element(self, locator, timeout=10):
        """
        Wait for an element to be visible with improved reliability
        
        Args:
            locator: Element locator (By.XXX, "value")
            timeout: Maximum time to wait in seconds
            
        Returns:
            The WebElement once visible
        """
        try:
            return self.wait_utils.wait_for_element_visible(locator, timeout)
        except TimeoutException as e:
            # Add more context to the exception for better debugging
            message = f"Element {locator} not visible after {timeout} seconds on page {self.driver.current_url}"
            
            # Add annotation in BrowserStack for debugging
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"ERROR: {message}")
                
            # Re-raise with better message
            raise TimeoutException(message) from e
        
    def wait_for_clickable(self, locator, timeout=10):
        """
        Wait for an element to be clickable with improved reliability
        
        Args:
            locator: Element locator (By.XXX, "value")
            timeout: Maximum time to wait in seconds
            
        Returns:
            The WebElement once clickable
        """
        try:
            return self.wait_utils.wait_for_element_clickable(locator, timeout)
        except TimeoutException as e:
            # Add more context to the exception for better debugging
            message = f"Element {locator} not clickable after {timeout} seconds on page {self.driver.current_url}"
            
            # Add annotation in BrowserStack for debugging
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"ERROR: {message}")
                
            # Re-raise with better message
            raise TimeoutException(message) from e
        
    def wait_for_presence(self, locator, timeout=10):
        """
        Wait for an element to be present in the DOM
        
        Args:
            locator: Element locator (By.XXX, "value")
            timeout: Maximum time to wait in seconds
            
        Returns:
            The WebElement once present
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def is_element_present(self, locator, timeout=5):
        """
        Check if an element is present
        
        Args:
            locator: Element locator (By.XXX, "value")
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element is present, False otherwise
        """
        try:
            self.wait_for_presence(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def click_element(self, locator):
        """
        Click on an element with improved reliability
        
        Args:
            locator: Element locator (By.XXX, "value")
        """
        try:
            element = self.wait_for_clickable(locator)
            self.wait_utils.safe_click(element)
            
            # Add annotation in BrowserStack
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"Clicked element: {locator}")
        except (TimeoutException, WebDriverException) as e:
            # Add more context to the exception for better debugging
            message = f"Failed to click element {locator} on page {self.driver.current_url}"
            
            # Add annotation in BrowserStack for debugging
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"ERROR: {message}")
                
            # Re-raise with better message
            raise type(e)(message) from e
    
    def get_element_text(self, locator):
        """
        Get text from an element with improved reliability
        
        Args:
            locator: Element locator (By.XXX, "value")
            
        Returns:
            The text content of the element
        """
        try:
            element = self.wait_for_element(locator)
            return element.text
        except (TimeoutException, StaleElementReferenceException) as e:
            # Retry once with a fresh element reference
            try:
                element = self.wait_for_element(locator)
                return element.text
            except Exception as retry_e:
                # Add more context to the exception for better debugging
                message = f"Failed to get text from element {locator} on page {self.driver.current_url}"
                
                # Add annotation in BrowserStack for debugging
                if self.is_browserstack:
                    self.bs_utils.add_session_annotation(f"ERROR: {message}")
                    
                # Re-raise with better message
                raise type(retry_e)(message) from retry_e
    
    def clear_and_type(self, locator, text):
        """
        Clear a field and type text with improved reliability
        
        Args:
            locator: Element locator (By.XXX, "value")
            text: Text to type
        """
        try:
            element = self.wait_for_element(locator)
            
            # Try to clear using standard method first
            try:
                element.clear()
            except:
                # If standard clear fails, try JavaScript clear
                self.driver.execute_script("arguments[0].value = '';", element)
            
            # Type the text
            element.send_keys(text)
            
            # Add annotation in BrowserStack
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"Typed '{text}' into element: {locator}")
        except (TimeoutException, WebDriverException) as e:
            # Add more context to the exception for better debugging
            message = f"Failed to type '{text}' into element {locator} on page {self.driver.current_url}"
            
            # Add annotation in BrowserStack for debugging
            if self.is_browserstack:
                self.bs_utils.add_session_annotation(f"ERROR: {message}")
                
            # Re-raise with better message
            raise type(e)(message) from e
    
    def scroll_to_element(self, element):
        """
        Scroll to an element with improved reliability
        
        Args:
            element: The WebElement to scroll to
        """
        try:
            # Scroll element to center of viewport for better interaction
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            # Adding a small pause after scrolling
            time.sleep(0.5)
            
            # Add annotation in BrowserStack
            if self.is_browserstack:
                self.bs_utils.add_session_annotation("Scrolled to element")
        except Exception as e:
            # Log the error but don't fail the test for scroll issues
            if hasattr(self.context, 'logger'):
                self.context.logger.warning(f"Failed to scroll to element: {str(e)}")
    
    def is_image_loaded(self, image_element):
        """
        Check if an image is fully loaded
        
        Args:
            image_element: The image WebElement
            
        Returns:
            True if image is loaded, False otherwise
        """
        try:
            return self.driver.execute_script(
                "return arguments[0].complete && typeof arguments[0].naturalWidth != 'undefined' && arguments[0].naturalWidth > 0;", 
                image_element
            )
        except Exception as e:
            # Log the error but return False for image load issues
            if hasattr(self.context, 'logger'):
                self.context.logger.warning(f"Failed to check if image is loaded: {str(e)}")
            return False
    
    def wait_for_url_contains(self, text, timeout=10):
        """
        Wait for URL to contain specific text
        
        Args:
            text: Text to look for in URL
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if URL contains the text
        """
        return self.wait_utils.wait_for_url_contains(text, timeout)
    
    def wait_for_text_in_element(self, locator, text, timeout=10):
        """
        Wait for element to contain specific text
        
        Args:
            locator: Element locator (By.XXX, "value")
            text: Text to look for in element
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element contains the text
        """
        return self.wait_utils.wait_for_text_in_element(locator, text, timeout)
    
    def get_element_attribute(self, locator, attribute):
        """
        Get attribute value from an element
        
        Args:
            locator: Element locator (By.XXX, "value")
            attribute: Attribute name
            
        Returns:
            The attribute value
        """
        element = self.wait_for_element(locator)
        return element.get_attribute(attribute)
    
    def select_option_by_text(self, locator, option_text):
        """
        Select an option from a dropdown by visible text
        
        Args:
            locator: Element locator (By.XXX, "value")
            option_text: Text of the option to select
        """
        from selenium.webdriver.support.ui import Select
        element = self.wait_for_element(locator)
        select = Select(element)
        select.select_by_visible_text(option_text)
        
        # Add annotation in BrowserStack
        if self.is_browserstack:
            self.bs_utils.add_session_annotation(f"Selected option '{option_text}' from dropdown: {locator}")
    
    def select_option_by_value(self, locator, option_value):
        """
        Select an option from a dropdown by value
        
        Args:
            locator: Element locator (By.XXX, "value")
            option_value: Value of the option to select
        """
        from selenium.webdriver.support.ui import Select
        element = self.wait_for_element(locator)
        select = Select(element)
        select.select_by_value(option_value)
        
        # Add annotation in BrowserStack
        if self.is_browserstack:
            self.bs_utils.add_session_annotation(f"Selected option with value '{option_value}' from dropdown: {locator}")
