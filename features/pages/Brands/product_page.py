import logging
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from .base_page import BasePage
import time
from selenium.webdriver.support.select import Select

logger = logging.getLogger(__name__)

class ProductPage(BasePage):
    """
    Page object for the product page with enhanced error handling and validation.
    """
    URL = "https://aeonstest.info/products/aeons-total-harmony"

    # Element Selectors with more specific XPaths and CSS selectors
    SELECTORS = {
        'add_to_cart_button': (By.CSS_SELECTOR, "button.btn.color-btn.add-product"),
        'subscribe_button': (By.CSS_SELECTOR, "input#sylius_add_to_cart_cartItem_variant_0"),
        'one_time_button': (By.CSS_SELECTOR, "input#sylius_add_to_cart_cartItem_variant_1"),
        'quantity_input': (By.CSS_SELECTOR, "input#sylius_add_to_cart_cartItem_quantity"),
        'size_dropdown': (By.CSS_SELECTOR, "select[name='subscription_frequency_select[aeons-total-harmony-vip]']"),
        'success_message': (By.CSS_SELECTOR, ".alert-success, .success-message, .cart-notification"),
        'price_amount': (By.CSS_SELECTOR, "span#product-price"),
        'faq_title': (By.CSS_SELECTOR, ".accordion-header"),
        'accordion_buttons': (By.CSS_SELECTOR, ".accordion-button"),
        'expanded_sections': (By.CSS_SELECTOR, ".accordion-collapse.show")
    }

    def __init__(self, browser):
        super().__init__(browser)
        self.url = self.URL

    def load(self, timeout: int = 10) -> None:
        """Load the product page and wait for essential elements."""
        logger.info(f"Loading product page: {self.URL}")
        self.browser.get(self.URL)
        try:
            self.wait_for_page_to_load(timeout)
            # Log page title and URL for debugging
            logger.debug(f"Page title: {self.browser.title}")
            logger.debug(f"Current URL: {self.browser.current_url}")
            # Log a preview of the page source
            page_source_preview = self.browser.page_source[:1000] if self.browser.page_source else "No page source available"
            logger.debug(f"Page source preview: {page_source_preview}")
            logger.info("Product page loaded successfully")
        except TimeoutException as e:
            logger.error("Product page failed to load within timeout")
            logger.error(f"Current URL: {self.browser.current_url}")
            raise TimeoutException("Page load timeout") from e

    def scroll_and_click(self, element, use_js=False) -> bool:
        """Scroll to element and attempt to click it using various methods."""
        try:
            # First scroll the element into view
            self.browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            # Add a small wait to allow any animations to complete
            self.browser.implicitly_wait(1)
            
            if use_js:
                # Try JavaScript click
                self.browser.execute_script("arguments[0].click();", element)
            else:
                # Try regular click
                element.click()
            
            return True
        except Exception as e:
            logger.warning(f"Click failed: {str(e)}")
            return False

    def add_to_cart(self, retries=3, timeout=10):
        """
        Adds the product to cart with enhanced error handling and retry mechanism.
        """
        logging.info("Attempting to add product to cart")
        
        # Wait for page to be fully loaded
        time.sleep(2)
        
        for attempt in range(retries):
            try:
                # Try to find the add to cart button
                add_to_cart_button = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_element_located(self.SELECTORS['add_to_cart_button'])
                )
                
                # Scroll to button and ensure it's in view
                self.browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_to_cart_button)
                time.sleep(1)
                
                try:
                    # Try regular click first
                    add_to_cart_button.click()
                except ElementClickInterceptedException:
                    try:
                        # Try JavaScript click if regular click fails
                        self.browser.execute_script("arguments[0].click();", add_to_cart_button)
                    except:
                        # Try ActionChains as last resort
                        ActionChains(self.browser).move_to_element(add_to_cart_button).click().perform()
                
                # Wait for success message or cart update
                if self.wait_for_success_message(timeout):
                    logging.info("Successfully added product to cart")
                    return True
                    
            except Exception as e:
                logging.warning(f"Add to cart attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    logging.error("Failed to add product to cart after all retries")
                    return False
                time.sleep(2)
                
        return False

    def wait_for_success_message(self, timeout=10):
        """
        Waits for success message after adding to cart.
        
        Args:
            timeout (int): Maximum time to wait for success message
            
        Returns:
            bool: True if success message appears, False otherwise
        """
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .success-message, .cart-notification"))
            )
            return True
        except TimeoutException:
            logging.warning("Success message not found after adding to cart")
            return False

    def select_subscription_option(self):
        """
        Select the subscription purchase option and verify the selection.
        
        Returns:
            bool: True if subscription was successfully selected, False otherwise
        """
        try:
            # Wait for subscription option to be clickable
            subscription_radio = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='radio'][@value='subscription']"))
            )
            
            # Scroll to element and click
            self.scroll_to_element(subscription_radio)
            
            # Use JavaScript to ensure the click happens
            self.browser.execute_script("arguments[0].click();", subscription_radio)
            
            # Add a small delay to let the UI update
            time.sleep(1)
            
            # Verify selection
            is_selected = self.browser.execute_script(
                "return arguments[0].checked;", 
                subscription_radio
            )
            
            if not is_selected:
                logger.error("Subscription radio button is not selected after clicking")
                return False
                
            # Select frequency if available
            try:
                frequency_select = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select.subscription-frequency"))
                )
                select = Select(frequency_select)
                select.select_by_index(1)  # Select first available frequency
            except TimeoutException:
                logger.warning("Frequency selector not found, continuing anyway")
                
            logger.info("Successfully selected subscription option")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting subscription option: {e}")
            return False

    def wait_for_subscription_selected(self, timeout: int = 5) -> None:
        """Wait for subscription option to be selected."""
        WebDriverWait(self.browser, timeout).until(
            lambda d: d.find_element(*self.SELECTORS['subscribe_button']).is_selected()
        )

    def click_accordion_button(self, index: int) -> None:
        """Click FAQ accordion button at specified index."""
        try:
            buttons = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located(self.SELECTORS['accordion_buttons'])
            )
            if 0 <= index < len(buttons):
                self.scroll_to_element(buttons[index])
                buttons[index].click()
            else:
                raise ValueError(f"Invalid accordion button index: {index}")
        except Exception as e:
            logger.error(f"Failed to click accordion button: {e}")
            raise