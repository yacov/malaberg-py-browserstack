from typing import List, Dict, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from features.pages.Common.base_page import BasePage
import re
import logging

logger = logging.getLogger(__name__)

class ConfirmationPage(BasePage):
    """Page object for the order confirmation page."""

    SELECTORS = {
        'ORDER_ITEMS': (By.CSS_SELECTOR, '.ui.celled.table tbody tr'),
        'PRODUCT_NAME': (By.CSS_SELECTOR, '.product-description h3'),
        'QUANTITY': (By.CSS_SELECTOR, '.text-center'),
        'PRICE': (By.CSS_SELECTOR, '.text-center:last-child'),
        'SHIPPING_INFO': (By.CSS_SELECTOR, '.card-header:contains("Shipping address")'),
        'ORDER_SUMMARY': (By.CSS_SELECTOR, '.order-summary-component'),
        'SUBTOTAL': (By.CSS_SELECTOR, '.ch-subtotal-value span'),
        'SHIPPING_COST': (By.CSS_SELECTOR, '.ch-shipping-value span'),
        'TOTAL': (By.CSS_SELECTOR, '.ch-total-value span'),
        'SHIPPING_METHOD': (By.CSS_SELECTOR, '.shipping-method'),
        'ADDRESS': (By.CSS_SELECTOR, '.card-body address'),
        'PURCHASE_TYPE': (By.CSS_SELECTOR, 'span[data-sylius-option-name="Purchase type"]'),
        'FLAVOR': (By.CSS_SELECTOR, 'span[data-sylius-option-name="Flavour"]'),
        'ORDER_NUMBER': (By.CSS_SELECTOR, '.order-number'),
        'SUBSCRIPTION_BADGE': (By.CSS_SELECTOR, '.ui.label.label-success'),
        'SUBSCRIPTION_FREQUENCY': (By.CSS_SELECTOR, '.ui.label.label-success'),
        'THANK_YOU_SECTION': (By.CSS_SELECTOR, '.section-thank-you h1')
    }

    def __init__(self, browser):
        super().__init__(browser)
        self.url = '/confirmation'

    def wait_for_page_load(self, timeout: int = 10) -> None:
        """Wait for the confirmation page to fully load."""
        try:
            logger.info("Waiting for confirmation page to load")

            # Wait for page load
            WebDriverWait(self.browser, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Wait for customer details
            WebDriverWait(self.browser, timeout).until(
                lambda driver: driver.execute_script(
                    "return typeof window.customerDetails !== 'undefined' && window.customerDetails !== null"
                )
            )

            # Wait for transaction data
            WebDriverWait(self.browser, timeout).until(
                lambda driver: driver.execute_script(
                    "return typeof window.dataLayer !== 'undefined' && "
                    "window.dataLayer !== null && "
                    "window.dataLayer.length > 0 && "
                    "typeof window.dataLayer[0].ecommerce !== 'undefined'"
                )
            )

            # Wait for thank you section
            WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located(self.SELECTORS['THANK_YOU_SECTION'])
            )

            logger.info("Confirmation page loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load confirmation page: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_order_number(self) -> str:
        """Get the order number from the confirmation page."""
        try:
            logger.info("Attempting to get order number")
            order_number = self.browser.execute_script(
                "return window.dataLayer[0].ecommerce.transaction_id"
            )
            logger.info(f"Successfully retrieved order number: {order_number}")
            return order_number
        except Exception as e:
            error_msg = f"Failed to get order number: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_customer_email(self) -> str:
        """Get the customer email from the confirmation page."""
        try:
            logger.info("Attempting to get customer email")
            email = self.browser.execute_script(
                "return window.customerDetails.email"
            )
            logger.info("Successfully retrieved customer email")
            return email
        except Exception as e:
            error_msg = f"Failed to get customer email: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_shipping_address(self) -> str:
        """Get the shipping address from the confirmation page."""
        try:
            logger.info("Attempting to get shipping address")
            address_element = self.browser.find_element(
                By.XPATH,
                "//div[contains(@class, 'card-header') and contains(text(), 'Shipping address')]"
                "/../div[@class='card-body']/address"
            )
            address = address_element.text
            logger.info("Successfully retrieved shipping address")
            return address
        except NoSuchElementException as e:
            error_msg = f"Failed to get shipping address: {str(e)}"
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def get_product_name(self) -> str:
        """Get the product name from the confirmation page."""
        element = self.browser.find_element(*self.SELECTORS['PRODUCT_NAME'])
        return element.text.strip()

    def get_product_quantity(self) -> int:
        """Get the product quantity from the confirmation page."""
        element = self.browser.find_element(By.CSS_SELECTOR, 'td.text-center:nth-child(3)')
        return int(element.text.strip())

    def get_subtotal_sum(self) -> int:
        """Get the subtotal sum from the confirmation page."""
        element = self.browser.find_element(By.CSS_SELECTOR, 'td.text-center:nth-child(4)')
        return int(element.text.strip())

    def normalize_address_text(self, address: str) -> str:
        """Normalize address text for comparison."""
        # Remove HTML tags while preserving line breaks
        address = re.sub('<br\s*/?>', ' ', address)

        # Remove other HTML tags
        address = re.sub('<[^>]+>', '', address)

        # Normalize whitespace
        address = ' '.join(address.split())

        # Split into components
        parts = address.split()

        # Reconstruct address in expected format
        name = f"{parts[0]} {parts[1]}"  # First and Last name
        phone = parts[2]  # Phone
        street = f"{parts[3]} {parts[4]} {parts[5]}"  # Street address
        city = parts[6]
        postcode = parts[7]
        country = parts[-1]  # Last element is country

        return f"{name} {phone} {street} {city}, {postcode} n/a {country}"

    def get_ordered_products(self) -> List[Dict[str, Union[str, int, float, bool]]]:
        """Get all ordered products with their details."""
        try:
            logger.info("Attempting to get ordered products")
            products = []
            rows = self.browser.find_elements(*self.SELECTORS['ORDER_ITEMS'])

            for row in rows:
                name_element = row.find_element(*self.SELECTORS['PRODUCT_NAME'])
                quantity_element = row.find_element(*self.SELECTORS['QUANTITY'])
                price_element = row.find_element(*self.SELECTORS['PRICE'])

                products.append({
                    'name': name_element.text.strip(),
                    'quantity': int(quantity_element.text.strip()),
                    'price': self._parse_price(price_element.text),
                    'subscription': self._is_subscription_product(name_element)
                })

            logger.info(f"Successfully retrieved {len(products)} ordered products")
            return products
        except NoSuchElementException as e:
            error_msg = f"Failed to get ordered products: {str(e)}"
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def get_shipping_info(self) -> Dict[str, str]:
        """Get complete shipping information."""
        try:
            logger.info("Attempting to get shipping information")
            info = {
                'method': self.browser.find_element(*self.SELECTORS['SHIPPING_METHOD']).text,
                'cost': self.browser.find_element(*self.SELECTORS['SHIPPING_COST']).text,
                'address': self._get_formatted_address()
            }
            logger.info("Successfully retrieved shipping information")
            return info
        except NoSuchElementException as e:
            error_msg = f"Failed to get shipping information: {str(e)}"
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def has_free_shipping(self) -> bool:
        """Check if free shipping was applied."""
        try:
            shipping_cost = self.browser.find_element(*self.SELECTORS['SHIPPING_COST']).text
            return shipping_cost.upper().strip() == 'FREE'
        except NoSuchElementException:
            return False

    def get_order_totals(self) -> Dict[str, float]:
        """Get all order totals."""
        try:
            logger.info("Attempting to get order totals")
            totals = {
                'subtotal': self._parse_price(
                    self.browser.find_element(*self.SELECTORS['SUBTOTAL']).text
                ),
                'shipping': self._parse_price(
                    self.browser.find_element(*self.SELECTORS['SHIPPING_COST']).text
                ),
                'total': self._parse_price(
                    self.browser.find_element(*self.SELECTORS['TOTAL']).text
                )
            }
            logger.info("Successfully retrieved order totals")
            return totals
        except NoSuchElementException as e:
            error_msg = f"Failed to get order totals: {str(e)}"
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def _is_subscription_product(self, element) -> bool:
        """Check if a product is a subscription."""
        try:
            return 'subscription' in element.text.lower()
        except Exception:
            return False

    def _get_formatted_address(self) -> str:
        """Get formatted address from the page."""
        address_element = self.browser.find_element(*self.SELECTORS['ADDRESS'])
        return self.normalize_address_text(address_element.text)

    def _parse_price(self, price_text: str) -> float:
        """Parse price text to float value."""
        return float(re.sub(r'[^0-9.]', '', price_text))

    def has_warning_in_instructions(self, warning: str) -> bool:
        """Check if specific warning exists in instructions."""
        try:
            instructions = self.browser.find_elements(By.CSS_SELECTOR, '.order-instructions .warning')
            return any(warning in instruction.text for instruction in instructions)
        except NoSuchElementException:
            return False

    def get_selected_flavor(self) -> Optional[str]:
        """Get the selected flavor from the confirmation page."""
        try:
            flavor_element = self.browser.find_element(*self.SELECTORS['FLAVOR'])
            return flavor_element.text.strip()
        except NoSuchElementException:
            return None

    def verify_selected_flavor(self, expected_flavor: str) -> bool:
        """Verify if the selected flavor matches the expected one."""
        actual_flavor = self.get_selected_flavor()

        if actual_flavor is None:
            return True

        if actual_flavor != expected_flavor:
            raise RuntimeError(
                f'Expected flavor "{expected_flavor}", but got "{actual_flavor}" '
                'on confirmation page'
            )

        return True

    def get_mixed_cart_order_details(self) -> List[Dict[str, Union[str, int, float]]]:
        """Get details for mixed cart orders."""
        order_details = []
        items = self.browser.find_elements(*self.SELECTORS['ORDER_ITEMS'])

        for item in items:
            item_details = {
                'name': item.find_element(*self.SELECTORS['PRODUCT_NAME']).text,
                'quantity': int(item.find_element(*self.SELECTORS['QUANTITY']).text),
                'price': self._parse_price(item.find_element(*self.SELECTORS['PRICE']).text),
                'type': 'subscription' if item.find_elements(*self.SELECTORS['SUBSCRIPTION_BADGE']) else 'one-time'
            }

            if item_details['type'] == 'subscription':
                item_details['frequency'] = item.find_element(
                    *self.SELECTORS['SUBSCRIPTION_FREQUENCY']
                ).text

            order_details.append(item_details)

        return order_details
