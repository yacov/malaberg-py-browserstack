from .base_page import BasePage
from selenium.webdriver.common.by import By

class CartPage(BasePage):
    """
    Page object for the cart page, containing specific elements and methods.
    """

    URL = "https://aeonstest.info/cart/"

    def __init__(self, browser):
        """
        Initialize the CartPage with a browser instance.
        
        :param browser: Selenium WebDriver instance
        """
        super().__init__(browser)

    @property
    def cart_title(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".cart-title h1")

    @property
    def product_image(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".product-image-and-description img")

    @property
    def product_description(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".product-description h3")

    @property
    def quantity_input(self):
        return self.browser.find_element(By.ID, "sylius_cart_items_0_quantity")

    @property
    def unit_price(self):
        return self.browser.find_element(By.CSS_SELECTOR, "td.numbers span")

    @property
    def total_price(self):
        return self.browser.find_element(By.CSS_SELECTOR, "td.numbers:nth-child(4)")

    @property
    def remove_item_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".remove-item-button")

    @property
    def coupon_input(self):
        return self.browser.find_element(By.ID, "sylius_cart_promotionCoupon")

    @property
    def apply_coupon_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".coupon-section button[type=submit]")

    @property
    def update_cart_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".update-cart-button")

    @property
    def checkout_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".checkout-btn")

    # Additional properties for elements not in the provided correct selectors list
    @property
    def discount_amount(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".discount-amount")

    @property
    def error_message(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".alert-danger")

    @property
    def empty_cart_message(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".empty-cart-message")

    @property
    def success_message(self):
        return self.browser.find_element(By.CSS_SELECTOR, '.alert-success')

    @property
    def purchase_type(self):
        return self.browser.find_element(By.XPATH, "//td[contains(text(), 'Purchase type:')]//following-sibling::td")

    @property
    def checkout_error_message(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".checkout-error-message")

    def load(self):
        """
        Navigate to the cart page URL.
        """
        self.browser.get(self.URL)
        self.wait_for_page_to_load()

    def is_url_matches(self):
        """
        Check if the current URL matches the cart page URL.
        
        :return: True if URLs match, False otherwise
        """
        return self.get_current_url() == self.URL

    def get_cart_title(self):
        """
        Get the title text of the cart page.
        
        :return: string containing the cart title
        """
        return self.get_element_text(self.CART_TITLE).strip()

    def is_product_displayed(self, product_name):
        """
        Check if the specified product is displayed in the cart.
        
        :param product_name: Name of the product
        :return: True if product is displayed, False otherwise
        """
        if self.is_element_present(self.PRODUCT_DESCRIPTION):
            displayed_name = self.get_element_text(self.PRODUCT_DESCRIPTION).strip()
            return displayed_name == product_name
        return False

    def is_product_image_displayed(self):
        """
        Check if the product image is displayed.
        
        :return: True if product image is displayed, False otherwise
        """
        return self.is_element_visible(self.PRODUCT_IMAGE)

    def update_quantity(self, quantity):
        """
        Update the quantity of the product in the cart.
        
        :param quantity: Desired quantity as integer
        """
        self.enter_text(self.QUANTITY_INPUT, str(quantity))

    def get_quantity(self):
        """
        Get the current quantity value from the quantity input.
        
        :return: Quantity as integer
        """
        return int(self.get_element_attribute(self.QUANTITY_INPUT, 'value'))

    def get_unit_price(self):
        """
        Get the unit price of the product.
        
        :return: Unit price as float
        """
        price_text = self.get_element_text(self.UNIT_PRICE).strip('£').replace(',', '')
        return float(price_text)

    def get_total_price(self):
        """
        Get the total price from the cart.
        
        :return: Total price as float
        """
        price_text = self.get_element_text(self.TOTAL_PRICE).strip('£').replace(',', '')
        return float(price_text)

    def remove_item(self):
        """
        Remove the item from the cart.
        """
        self.click_element(self.REMOVE_ITEM_BUTTON)

    def is_remove_button_displayed(self):
        """
        Check if the remove item button is displayed.
        
        :return: True if displayed, False otherwise
        """
        return self.is_element_visible(self.REMOVE_ITEM_BUTTON)

    def apply_coupon(self, coupon_code):
        """
        Apply a coupon code to the cart.
        
        :param coupon_code: Coupon code as string
        """
        self.enter_text(self.COUPON_INPUT, coupon_code)
        self.click_element(self.APPLY_COUPON_BUTTON)

    def is_discount_applied(self):
        """
        Check if the discount is applied.
        
        :return: True if discount amount is displayed, False otherwise
        """
        return self.is_element_visible(self.DISCOUNT_AMOUNT)

    def is_error_message_displayed(self):
        """
        Check if an error message is displayed.
        
        :return: True if error message is displayed, False otherwise
        """
        return self.is_element_visible(self.ERROR_MESSAGE)

    def update_cart(self):
        """
        Click the update cart button to update the cart details.
        """
        self.click_element(self.UPDATE_CART_BUTTON)

    def wait_for_cart_to_update(self, timeout=10):
        """
        Wait for the cart to update.
        
        :param timeout: Maximum time to wait in seconds
        """
        self.wait_for_page_to_load(timeout=timeout)

    def wait_for_cart_to_load(self, timeout=10):
        """
        Wait for the cart page to load.
        
        :param timeout: Maximum time to wait in seconds
        """
        self.wait_for_page_to_load(timeout=timeout)

    def is_cart_empty(self):
        """
        Check if the cart is empty.
        
        :return: True if cart is empty, False otherwise
        """
        return self.is_element_visible(self.EMPTY_CART_MESSAGE)

    def is_empty_cart_message_displayed(self):
        """
        Check if the empty cart message is displayed.
        
        :return: True if message is displayed, False otherwise
        """
        return self.is_element_visible(self.EMPTY_CART_MESSAGE)

    def proceed_to_checkout(self):
        """
        Click the checkout button to proceed to the checkout page.
        """
        self.click_element(self.CHECKOUT_BUTTON)

    def is_success_message_displayed(self):
        """
        Check if the success message for adding an item to the cart is displayed.
        
        :return: True if the success message is displayed and contains the expected text, False otherwise
        """
        return self.is_element_visible(self.SUCCESS_MESSAGE) and "Item has been added to cart" in self.get_element_text(self.SUCCESS_MESSAGE)

    def get_purchase_type(self):
        """
        Get the purchase type text from the cart page.
        
        :return: string containing the purchase type
        """
        return self.get_element_text(self.PURCHASE_TYPE).strip()

    def is_prevented_from_checkout(self):
        """
        Check if the user is prevented from proceeding to checkout due to an empty cart.
        
        :return: True if prevented with an error message, False otherwise
        """
        return self.is_element_visible(self.CHECKOUT_ERROR_MESSAGE)