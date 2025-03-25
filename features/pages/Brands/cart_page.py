import logging
from decimal import Decimal
from typing import Optional, Tuple, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_page import BasePage
from urllib.parse import urlparse
import time
from selenium.common.exceptions import ElementClickInterceptedException

logger = logging.getLogger(__name__)

class CartPage(BasePage):
    """Enhanced cart page object with improved validation and error handling."""
    
    SELECTORS = {
        'CART_ITEM': (By.CSS_SELECTOR, '.cart-table tbody tr'),
        'PRODUCT_NAME': (By.CSS_SELECTOR, '.product-description h3'),
        'UNIT_PRICE': (By.CSS_SELECTOR, 'td.numbers span'),
        'QUANTITY': (By.ID, 'sylius_cart_items_0_quantity'),
        'TOTAL': (By.CSS_SELECTOR, 'td.numbers:nth-child(4)'),
        'SHIPPING_TOTAL': (By.CSS_SELECTOR, '.summary-section .ch-shipping-value span'),
        'ORDER_TOTAL': (By.CSS_SELECTOR, '.summary-section .ch-total-value span'),
        'SUCCESS_MESSAGE': (By.CSS_SELECTOR, '.alert-success, .success-message, .cart-notification, .notification-success'),
        'ERROR_MESSAGE': (By.CSS_SELECTOR, '.alert.alert-danger, .notification-error'),
        'SUBSCRIPTION_BADGE': (By.CSS_SELECTOR, '.subscription-badge'),
        'SUBSCRIPTION_FREQUENCY': (By.CSS_SELECTOR, '.subscription-frequency'),
        'CART_ITEMS': (By.CSS_SELECTOR, '.cart-table tbody tr'),
        'CART_TITLE': (By.CSS_SELECTOR, '.cart-title h1'),
        'PRODUCT_IMAGE': (By.CSS_SELECTOR, '.product-image-and-description img'),
        'REMOVE_BUTTON': (By.CSS_SELECTOR, '.remove-item-button'),
        'COUPON_INPUT': (By.ID, 'sylius_cart_promotionCoupon'),
        'APPLY_COUPON_BUTTON': (By.CSS_SELECTOR, '.coupon-section button'),
        'UPDATE_CART_BUTTON': (By.CSS_SELECTOR, '.update-cart-button'),
        'CHECKOUT_BUTTON': (By.CSS_SELECTOR, 'button.checkout-btn'),
        'CART_LIMIT_MESSAGE': (By.CSS_SELECTOR, '.cart-limit-message'),
        'ENFORCE_CHECKOUT_MESSAGE': (By.CSS_SELECTOR, '.enforce-checkout-message'),
        'PRE_UPSELL_TOTAL': (By.CSS_SELECTOR, '.pre-upsell-total .amount'),
        'EMPTY_CART_MESSAGE': (By.CSS_SELECTOR, '.cart-title .alert'),
        'CHECKOUT_ERROR': (By.CSS_SELECTOR, '.checkout-error-message'),
        'ITEMS_TOTAL': (By.CSS_SELECTOR, '.summary-section .ch-subtotal-value span'),
        'PROMOTION_DISCOUNT': (By.CSS_SELECTOR, '.summary-section .ch-discount-value span')
    }

    def __init__(self, browser):
        super().__init__(browser)
        self.url = '/cart'

    def load(self, timeout: int = 10) -> None:
        """Load the cart page and wait for essential elements."""
        logger.info(f"Loading cart page: {self.url}")
        self.browser.get(f"https://aeonstest.info{self.url}")
        try:
            self.wait_for_page_load(timeout)
            logger.debug(f"Page title: {self.browser.title}")
            logger.debug(f"Current URL: {self.browser.current_url}")
            logger.info("Cart page loaded successfully")
        except TimeoutException as e:
            logger.error("Cart page failed to load within timeout")
            logger.error(f"Current URL: {self.browser.current_url}")
            raise TimeoutException("Cart page load timeout") from e

    def is_url_matches(self) -> bool:
        """Check if current URL matches the cart page URL."""
        current_url = urlparse(self.browser.current_url)
        expected_url = urlparse(f"https://aeonstest.info{self.url}")
        
        # Compare only the path components, ignoring query parameters
        current_path = current_url.path.rstrip('/')
        expected_path = expected_url.path.rstrip('/')
        
        logger.info(f"URL Match Check:")
        logger.info(f"  Current path: {current_path}")
        logger.info(f"  Expected path: {expected_path}")
        matches = current_path == expected_path
        logger.info(f"  Paths match: {matches}")
        return matches

    def wait_for_page_load(self, timeout: int = 10) -> None:
        """Wait for the cart page to load completely."""
        WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located(self.SELECTORS['CART_TITLE'])
        )

    def get_cart_title(self) -> str:
        """Get the cart page title text."""
        element = self.browser.find_element(*self.SELECTORS['CART_TITLE'])
        return element.text.strip()

    def is_product_displayed(self, product_name: str) -> bool:
        """Check if a specific product is displayed in the cart."""
        try:
            element = self.browser.find_element(*self.SELECTORS['PRODUCT_NAME'])
            return element.text.strip() == product_name
        except NoSuchElementException:
            return False

    def is_product_image_displayed(self) -> bool:
        """Check if the product image is displayed."""
        try:
            element = self.browser.find_element(*self.SELECTORS['PRODUCT_IMAGE'])
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def update_quantity(self, quantity: int) -> None:
        """Update the quantity of the product in cart."""
        element = self.browser.find_element(*self.SELECTORS['QUANTITY'])
        element.clear()
        element.send_keys(str(quantity))

    def get_quantity(self) -> int:
        """Get the current quantity value."""
        element = self.browser.find_element(*self.SELECTORS['QUANTITY'])
        return int(element.get_attribute('value'))

    def get_unit_price(self) -> float:
        """Get the unit price of the product."""
        element = self.browser.find_element(*self.SELECTORS['UNIT_PRICE'])
        return self._parse_price(element.text)

    def get_total_price(self) -> float:
        """Get the total price from the cart."""
        element = self.browser.find_element(*self.SELECTORS['TOTAL'])
        return self._parse_price(element.text)

    def get_shipping_cost(self) -> float:
        """Get the shipping cost."""
        element = self.browser.find_element(*self.SELECTORS['SHIPPING_TOTAL'])
        return self._parse_price(element.text)

    def get_pre_upsell_total(self) -> float:
        """Get the total before upsell items."""
        try:
            element = self.browser.find_element(*self.SELECTORS['PRE_UPSELL_TOTAL'])
            return self._parse_price(element.text)
        except NoSuchElementException:
            return self.get_total_price()

    def verify_upsell_price_addition(self, upsell_price: float) -> bool:
        """Verify if the upsell price was correctly added to the total."""
        try:
            pre_upsell_total = self.get_pre_upsell_total()
            final_total = self.get_total_price()
            return abs((pre_upsell_total + upsell_price) - final_total) < 0.01
        except Exception as e:
            logger.error(f"Error verifying upsell price: {e}")
            return False

    def remove_item(self) -> None:
        """Remove the item from cart."""
        element = self.browser.find_element(*self.SELECTORS['REMOVE_BUTTON'])
        element.click()

    def is_remove_button_displayed(self) -> bool:
        """Check if remove button is displayed."""
        try:
            element = self.browser.find_element(*self.SELECTORS['REMOVE_BUTTON'])
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def apply_coupon(self, coupon_code: str) -> Tuple[bool, Optional[str]]:
        """Apply a coupon code to the cart.
        
        Returns:
            Tuple[bool, Optional[str]]: A tuple containing (success, error_message)
        """
        try:
            input_element = self.browser.find_element(*self.SELECTORS['COUPON_INPUT'])
            self.scroll_to_element(input_element)
            input_element.clear()
            input_element.send_keys(coupon_code)

            apply_button = self.browser.find_element(*self.SELECTORS['APPLY_COUPON_BUTTON'])
            apply_button.click()

            # Wait for either success or error message
            WebDriverWait(self.browser, 3).until(
                lambda x: self.is_success_message_displayed() or self.is_error_message_displayed()
            )

            if self.is_success_message_displayed():
                return True, None
            elif self.is_error_message_displayed():
                error_msg = self.browser.find_element(*self.SELECTORS['ERROR_MESSAGE']).text
                return False, error_msg
            else:
                return False, "No response after applying coupon"
        except Exception as e:
            logger.error(f"Error applying coupon: {e}")
            return False, str(e)

    def wait_for_success_message(self, timeout: int = 10) -> bool:
        """Wait for success message to appear and return True if found."""
        try:
            # Log all possible success message elements
            logger.info("Looking for success message with selectors:")
            for selector in ['.alert-success', '.success-message', '.cart-notification', '.notification-success']:
                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"  {selector}: found {len(elements)} elements")
                for elem in elements:
                    logger.info(f"    Text: {elem.text}")
                    logger.info(f"    Classes: {elem.get_attribute('class')}")
                    logger.info(f"    Visible: {elem.is_displayed()}")

            # Try to find any element with success-related text
            success_elements = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'Success') or contains(text(), 'added')]")
            logger.info(f"Found {len(success_elements)} elements with success-related text:")
            for elem in success_elements:
                logger.info(f"  Tag: {elem.tag_name}")
                logger.info(f"  Text: {elem.text}")
                logger.info(f"  Classes: {elem.get_attribute('class')}")
                logger.info(f"  Visible: {elem.is_displayed()}")

            # Original wait logic
            WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located(self.SELECTORS['SUCCESS_MESSAGE'])
            )
            return True
        except TimeoutException:
            logger.warning("Success message not found within timeout")
            return False

    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed."""
        try:
            element = WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located(self.SELECTORS['SUCCESS_MESSAGE'])
            )
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed."""
        try:
            element = self.browser.find_element(*self.SELECTORS['ERROR_MESSAGE'])
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def update_cart(self) -> None:
        """Click update cart button."""
        element = self.browser.find_element(*self.SELECTORS['UPDATE_CART_BUTTON'])
        element.click()

    def wait_for_cart_update(self, timeout: int = 10) -> None:
        """Wait for cart to update."""
        WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located(self.SELECTORS['SUCCESS_MESSAGE'])
        )

    def verify_order_total(self) -> bool:
        """Verify order total calculation."""
        try:
            # Using XPath for specific text matches
            items_total = self._get_numeric_value("//div[contains(@class, 'summary-section')]//p[contains(text(), 'Items total:')]//span[@class='numbers']")
            promotion_discount = self._get_numeric_value("//div[contains(@class, 'summary-section')]//p[contains(text(), 'Promotion discount:')]//span[@class='numbers']")
            shipping_cost = self._get_numeric_value("//div[contains(@class, 'summary-section')]//p[contains(text(), 'Shipping:')]//span[@class='numbers']")
            displayed_total = self._get_numeric_value("//div[contains(@class, 'summary-section')]//p[contains(text(), 'Order total:')]//span[@class='numbers']")

            calculated_total = items_total - promotion_discount + shipping_cost
            return abs(calculated_total - displayed_total) < 0.01
        except Exception:
            return False

    def is_cart_empty(self) -> bool:
        """Check if cart is empty."""
        try:
            element = self.browser.find_element(*self.SELECTORS['EMPTY_CART_MESSAGE'])
            return element.text.strip() == 'Your cart is empty'
        except NoSuchElementException:
            return False

    def proceed_to_checkout(self) -> bool:
        """Proceed to checkout.
        
        Returns:
            bool: True if successfully proceeded to checkout, False otherwise
        """
        try:
            # Find the checkout button
            element = self.browser.find_element(*self.SELECTORS['CHECKOUT_BUTTON'])
            
            # Scroll the button into view
            self.browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(1)  # Wait for scroll to complete
            
            # Try to click the button
            try:
                element.click()
            except ElementClickInterceptedException:
                # If regular click fails, try JavaScript click
                self.browser.execute_script("arguments[0].click();", element)
            
            # Wait for URL to change
            WebDriverWait(self.browser, 5).until(
                lambda x: '/checkout' in x.current_url
            )
            
            return True
        except Exception as e:
            logger.error(f"Error proceeding to checkout: {e}")
            return False

    def get_product_name(self) -> str:
        """Get the product name from cart."""
        element = self.browser.find_element(*self.SELECTORS['PRODUCT_NAME'])
        return element.text.strip()

    def get_subscription_frequency(self) -> str:
        """Get the subscription frequency."""
        element = self.browser.find_element(*self.SELECTORS['SUBSCRIPTION_FREQUENCY'])
        return element.text.strip()

    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        items = self.browser.find_elements(*self.SELECTORS['CART_ITEMS'])
        return len(items)

    def get_subscription_item_count(self) -> int:
        """Get number of subscription items in cart."""
        items = self.browser.find_elements(*self.SELECTORS['CART_ITEMS'])
        subscription_items = [item for item in items if item.find_element(*self.SELECTORS['SUBSCRIPTION_BADGE'])]
        return len(subscription_items)

    def get_one_time_purchase_item_count(self) -> int:
        """Get number of one-time purchase items."""
        return self.get_item_count() - self.get_subscription_item_count()

    def get_subscription_frequencies(self) -> List[str]:
        """Get list of subscription frequencies."""
        frequencies = []
        items = self.browser.find_elements(*self.SELECTORS['CART_ITEMS'])
        for item in items:
            try:
                freq_element = item.find_element(*self.SELECTORS['SUBSCRIPTION_FREQUENCY'])
                frequencies.append(freq_element.text.strip())
            except NoSuchElementException:
                continue
        return frequencies

    def is_cart_limit_message_displayed(self, message: str) -> bool:
        """Check if cart limit message is displayed."""
        try:
            element = self.browser.find_element(*self.SELECTORS['CART_LIMIT_MESSAGE'])
            return message in element.text
        except NoSuchElementException:
            return False

    def is_checkout_enforced(self) -> bool:
        """Check if checkout is enforced."""
        try:
            element = self.browser.find_element(*self.SELECTORS['ENFORCE_CHECKOUT_MESSAGE'])
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def _parse_price(self, price_text: str) -> float:
        """Parse price text to float value."""
        return float(''.join(filter(str.isdigit, price_text))) / 100

    def _get_numeric_value(self, xpath: str) -> float:
        """Get numeric value from element text using XPath."""
        element = self.browser.find_element(By.XPATH, xpath)
        return self._parse_price(element.text)

    def get_success_message(self) -> str:
        """Get the text of the success message."""
        try:
            element = self.browser.find_element(*self.SELECTORS['SUCCESS_MESSAGE'])
            return element.text.strip()
        except NoSuchElementException:
            return ""

    def verify_discount(self) -> bool:
        """Verify if the discount was correctly applied to the cart total."""
        try:
            # Wait for cart totals to update
            WebDriverWait(self.browser, 5).until(
                lambda x: len(x.find_elements(By.XPATH, "//span[contains(text(), 'Promotion discount:')]")) > 0
            )
            
            # Get the items total (non-strikethrough value)
            items_total_elem = self.browser.find_element(By.XPATH, "//p[.//span[text()='Items total:']]//span[@class='numbers' and not(contains(@class, 'strikethrough'))]")
            items_total_value = self._parse_price(items_total_elem.text)
            
            # Get the promotion discount
            discount_elem = self.browser.find_element(By.XPATH, "//p[.//span[text()='Promotion discount:']]//span[@class='numbers']")
            discount_text = discount_elem.text.strip()
            # Remove the minus sign if present and parse the price
            discount_value = self._parse_price(discount_text.replace('-', ''))
            
            if discount_value <= 0:
                logger.warning("No discount amount found")
                return False
                
            if discount_value > (items_total_value * 0.5):
                logger.warning(f"Discount amount {discount_value} seems too high compared to total {items_total_value}")
                return False
                
            logger.info(f"Discount verification successful: Original total: {items_total_value}, Discount: {discount_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying discount: {e}")
            return False

    def get_purchase_type(self):
        """
        Get the current purchase type displayed in the cart.
        
        Returns:
            str: The purchase type text or None if not found
        """
        try:
            # Wait for purchase type element with more specific selector
            purchase_type_elem = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//div[contains(@class, 'cart-item')]//span[contains(@class, 'purchase-type')] | " +
                    "//div[contains(@class, 'cart-item')]//div[contains(text(), 'Subscribe & Save')] | " +
                    "//div[contains(@class, 'cart-item')]//div[contains(text(), 'One-time purchase')]"
                ))
            )
            
            # Scroll to element to ensure it's in view
            self.scroll_to_element(purchase_type_elem)
            
            # Get text and clean it up
            purchase_type = purchase_type_elem.text.strip()
            logger.info(f"Found purchase type in cart: {purchase_type}")
            return purchase_type
            
        except TimeoutException:
            logger.error("Purchase type element not found in cart")
            return None
        except Exception as e:
            logger.error(f"Error getting purchase type: {e}")
            return None