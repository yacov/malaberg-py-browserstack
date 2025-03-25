from selenium.webdriver.common.by import By
from .base_page import BasePage
from .header_page import HeaderPage

class CheckoutPage(BasePage):
    """Page object for the Shopify checkout page"""
    
    # Checkout sections and containers
    ORDER_SUMMARY_SECTION = (By.CSS_SELECTOR, ".order-summary__section")
    SHOPPING_CART_HEADING = (By.CSS_SELECTOR, ".order-summary__section__content__title")
    PRODUCT_LIST = (By.CSS_SELECTOR, ".product-table")
    PRODUCT_IMAGE = (By.CSS_SELECTOR, ".product-thumbnail__image")
    PRODUCT_QUANTITY = (By.CSS_SELECTOR, ".product__quantity")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".product__price")
    
    # Cost summaries
    SUBTOTAL = (By.CSS_SELECTOR, ".payment-due__price")
    SHIPPING_COST = (By.CSS_SELECTOR, ".total-line__price--shipping")
    TOTAL_TAXES = (By.CSS_SELECTOR, ".total-line__price--taxes")
    TOTAL_COST = (By.CSS_SELECTOR, ".payment-due__price")
    
    # Shipping form fields
    EMAIL_INPUT = (By.ID, "email")
    FIRST_NAME_INPUT = (By.ID, "TextField393")  # These IDs might be dynamic
    LAST_NAME_INPUT = (By.ID, "TextField394")
    ADDRESS_INPUT = (By.ID, "shipping-address1")
    CITY_INPUT = (By.ID, "TextField9")
    POSTCODE_INPUT = (By.ID, "TextField10")
    PHONE_INPUT = (By.ID, "TextField399")
    
    # Checkboxes
    REMEMBER_ME_CHECKBOX = (By.ID, "RememberMe-RememberMeCheckbox")
    USE_SHIPPING_AS_BILLING_CHECKBOX = (By.ID, "billingAddress")
    
    # Payment options
    CREDIT_CARD_OPTION = (By.ID, "basic-creditCards")
    PAYPAL_OPTION = (By.ID, "basic-paypal")
    KLARNA_OPTION = (By.ID, "basic-klarna")
    GOOGLE_PAY_OPTION = (By.ID, "basic-googlePay")
    
    # Buttons and links
    PAY_NOW_BUTTON = (By.ID, "checkout-pay-button")
    TERMS_OF_SERVICE_LINK = (By.XPATH, "//a[contains(@href, 'terms-of-service')]")
    PRIVACY_POLICY_LINK = (By.XPATH, "//a[contains(@href, 'privacy/app-users')]")
    
    # Error messages
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".field__message--error")
    
    # Order confirmation elements
    ORDER_CONFIRMATION_TITLE = (By.CSS_SELECTOR, ".os-header__title")
    ORDER_CONFIRMATION_NUMBER = (By.CSS_SELECTOR, ".os-order-number")
    ORDER_CONFIRMATION_EMAIL = (By.CSS_SELECTOR, ".os-step__info")
    
    # Test credit card details (for test mode only)
    TEST_CARD_NUMBER = "4242 4242 4242 4242"  # Standard Shopify test card
    TEST_CARD_EXPIRY = "12/25"
    TEST_CARD_CVV = "123"
    TEST_CARD_NAME = "Test User"
    
    # Credit card form fields (may need to be adjusted based on actual iframe implementation)
    CARD_NUMBER_FRAME = (By.CSS_SELECTOR, "iframe[id^='card-fields-number']")
    CARD_NUMBER_INPUT = (By.ID, "number")
    CARD_EXPIRY_FRAME = (By.CSS_SELECTOR, "iframe[id^='card-fields-expiry']")
    CARD_EXPIRY_INPUT = (By.ID, "expiry")
    CARD_CVV_FRAME = (By.CSS_SELECTOR, "iframe[id^='card-fields-verification']")
    CARD_CVV_INPUT = (By.ID, "verification_value")
    CARD_NAME_INPUT = (By.ID, "name")
    
    def is_order_summary_visible(self):
        """
        Check if the order summary section is visible
        
        Returns:
            True if the order summary is visible, False otherwise
        """
        return self.is_element_present(self.ORDER_SUMMARY_SECTION)
    
    def is_shopping_cart_heading_displayed(self):
        """
        Check if the shopping cart heading is displayed
        
        Returns:
            True if the shopping cart heading is displayed, False otherwise
        """
        return self.is_element_present(self.SHOPPING_CART_HEADING)
    
    def is_product_image_displayed(self):
        """
        Check if the product image is displayed
        
        Returns:
            True if the product image is displayed, False otherwise
        """
        return self.is_element_present(self.PRODUCT_IMAGE)
    
    def get_product_quantity(self):
        """
        Get the quantity of the product in checkout
        
        Returns:
            The quantity as a string
        """
        return self.get_element_text(self.PRODUCT_QUANTITY)
    
    def get_product_price(self):
        """
        Get the price of the product in checkout
        
        Returns:
            The price as a string
        """
        return self.get_element_text(self.PRODUCT_PRICE)
    
    def get_subtotal(self):
        """
        Get the subtotal cost
        
        Returns:
            The subtotal as a string
        """
        return self.get_element_text(self.SUBTOTAL)
    
    def get_shipping_cost(self):
        """
        Get the shipping cost
        
        Returns:
            The shipping cost as a string
        """
        return self.get_element_text(self.SHIPPING_COST)
    
    def get_total_cost(self):
        """
        Get the total cost
        
        Returns:
            The total cost as a string
        """
        return self.get_element_text(self.TOTAL_COST)
    
    def fill_shipping_information(self, email, first_name, last_name, address, city, postcode, phone):
        """
        Fill in the shipping information form
        
        Args:
            email: Email address
            first_name: First name
            last_name: Last name
            address: Address
            city: City
            postcode: Postal code
            phone: Phone number
        """
        self.clear_and_type(self.EMAIL_INPUT, email)
        self.clear_and_type(self.FIRST_NAME_INPUT, first_name)
        self.clear_and_type(self.LAST_NAME_INPUT, last_name)
        self.clear_and_type(self.ADDRESS_INPUT, address)
        self.clear_and_type(self.CITY_INPUT, city)
        self.clear_and_type(self.POSTCODE_INPUT, postcode)
        self.clear_and_type(self.PHONE_INPUT, phone)
    
    def check_remember_me(self):
        """Check the 'Remember me' checkbox"""
        remember_me = self.wait_for_element(self.REMEMBER_ME_CHECKBOX)
        if not remember_me.is_selected():
            remember_me.click()
    
    def check_use_shipping_as_billing(self):
        """Check the 'Use shipping address as billing address' checkbox"""
        use_shipping = self.wait_for_element(self.USE_SHIPPING_AS_BILLING_CHECKBOX)
        if not use_shipping.is_selected():
            use_shipping.click()
    
    def select_payment_method(self, method):
        """
        Select a payment method
        
        Args:
            method: The payment method to select ('credit_card', 'paypal', 'klarna', or 'google_pay')
        """
        if method == 'credit_card':
            self.click_element(self.CREDIT_CARD_OPTION)
        elif method == 'paypal':
            self.click_element(self.PAYPAL_OPTION)
        elif method == 'klarna':
            self.click_element(self.KLARNA_OPTION)
        elif method == 'google_pay':
            self.click_element(self.GOOGLE_PAY_OPTION)
    
    def click_pay_now(self):
        """Click the 'Pay now' button"""
        self.click_element(self.PAY_NOW_BUTTON)
    
    def click_terms_of_service(self):
        """Click the Terms of Service link"""
        self.click_element(self.TERMS_OF_SERVICE_LINK)
    
    def click_privacy_policy(self):
        """Click the Privacy Policy link"""
        self.click_element(self.PRIVACY_POLICY_LINK)
    
    def is_pay_now_button_enabled(self):
        """
        Check if the 'Pay now' button is enabled
        
        Returns:
            True if the button is enabled, False otherwise
        """
        pay_now_button = self.wait_for_element(self.PAY_NOW_BUTTON)
        return pay_now_button.is_enabled()
    
    def get_error_message(self):
        """
        Get the error message text if present
        
        Returns:
            The error message text, or None if no error message is present
        """
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_element_text(self.ERROR_MESSAGE)
        return None
    
    def enter_invalid_credit_card(self):
        """Enter an invalid credit card for testing error handling"""
        # Implement credit card entry logic here
        pass
    
    def complete_test_purchase(self):
        """
        Complete a test purchase with a test credit card
        
        This method fills in test credit card information and completes the purchase
        It is designed to work in a test environment where real charges are not processed
        """
        try:
            # Handle credit card details in iframes (standard Shopify checkout approach)
            # Card Number
            card_number_frame = self.wait_for_element(self.CARD_NUMBER_FRAME)
            self.driver.switch_to.frame(card_number_frame)
            self.clear_and_type(self.CARD_NUMBER_INPUT, self.TEST_CARD_NUMBER)
            self.driver.switch_to.default_content()
            
            # Card Expiry
            card_expiry_frame = self.wait_for_element(self.CARD_EXPIRY_FRAME)
            self.driver.switch_to.frame(card_expiry_frame)
            self.clear_and_type(self.CARD_EXPIRY_INPUT, self.TEST_CARD_EXPIRY)
            self.driver.switch_to.default_content()
            
            # Card CVV
            card_cvv_frame = self.wait_for_element(self.CARD_CVV_FRAME)
            self.driver.switch_to.frame(card_cvv_frame)
            self.clear_and_type(self.CARD_CVV_INPUT, self.TEST_CARD_CVV)
            self.driver.switch_to.default_content()
            
            # Card Name (may be outside iframe)
            if self.is_element_present(self.CARD_NAME_INPUT):
                self.clear_and_type(self.CARD_NAME_INPUT, self.TEST_CARD_NAME)
                
            # Click pay now to complete purchase
            self.click_pay_now()
            
            # Wait for order confirmation page to load
            import time
            time.sleep(5)  # Allow time for processing
            
            return True
        except Exception as e:
            import logging
            logging.error(f"Error completing test purchase: {str(e)}")
            return False
    
    def is_order_confirmation_visible(self):
        """
        Check if the order confirmation page is displayed
        
        Returns:
            True if the order confirmation page is visible, False otherwise
        """
        return self.is_element_present(self.ORDER_CONFIRMATION_TITLE)
    
    def get_order_confirmation_number(self):
        """
        Get the order confirmation number
        
        Returns:
            The order confirmation number as a string
        """
        if self.is_element_present(self.ORDER_CONFIRMATION_NUMBER):
            return self.get_element_text(self.ORDER_CONFIRMATION_NUMBER)
        return None
    
    def get_order_confirmation_email(self):
        """
        Get the email address on the order confirmation page
        
        Returns:
            The email address as a string
        """
        if self.is_element_present(self.ORDER_CONFIRMATION_EMAIL):
            confirmation_text = self.get_element_text(self.ORDER_CONFIRMATION_EMAIL)
            # Extract email from text which might be in format "We've sent order confirmation to: email@example.com"
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', confirmation_text)
            if email_match:
                return email_match.group(0)
        return None
