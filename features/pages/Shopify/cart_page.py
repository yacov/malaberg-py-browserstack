from selenium.webdriver.common.by import By
from .base_page import BasePage
from .header_page import HeaderPage

class CartPage(BasePage):
    """Page object for the Shopify cart page"""
    
    # Base URL for the cart page
    CART_URL = HeaderPage.BASE_URL + "cart"
    
    # Cart content locators
    CART_ITEMS = (By.CSS_SELECTOR, "cart-items .cart-item")
    CART_ITEM_NAME = (By.CSS_SELECTOR, ".cart-item__name")
    ITEM_QUANTITY_INPUT = (By.CSS_SELECTOR, "input.quantity__input")
    INCREASE_BUTTON = (By.CSS_SELECTOR, "button[name='plus']")
    DECREASE_BUTTON = (By.CSS_SELECTOR, "button[name='minus']")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "cart-remove-button")
    
    # Cart summary locators
    SUBTOTAL = (By.CSS_SELECTOR, ".totals__subtotal-value")
    ESTIMATED_TOTAL = (By.CSS_SELECTOR, ".estimated-total")
    ESTIMATED_TOTAL_VALUE = (By.CSS_SELECTOR, ".estimated-total-value")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, ".cart__checkout-button")
    SHIPPING_CALCULATOR_LINK = (By.CSS_SELECTOR, "a[href*='shipping']")
    EMPTY_CART_MESSAGE = (By.CSS_SELECTOR, ".cart__warnings")
    TAX_NOTE = (By.CSS_SELECTOR, ".tax-note")
    
    def open_cart(self):
        """Open the cart page"""
        self.open(self.CART_URL)
    
    def get_item_count(self):
        """
        Get the number of items in the cart
        
        Returns:
            The number of items in the cart
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        return len(items)
    
    def get_item_name(self, index=0):
        """
        Get the name of an item in the cart
        
        Args:
            index: The index of the item (0-based)
            
        Returns:
            The name of the item
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            item_name = items[index].find_element(*self.CART_ITEM_NAME)
            return item_name.text
        return None
    
    def get_item_quantity(self, index=0):
        """
        Get the quantity of an item in the cart
        
        Args:
            index: The index of the item (0-based)
            
        Returns:
            The quantity of the item as an integer
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            quantity_input = items[index].find_element(*self.ITEM_QUANTITY_INPUT)
            return int(quantity_input.get_attribute("value"))
        return 0
    
    def set_item_quantity(self, index, quantity):
        """
        Set the quantity of an item in the cart
        
        Args:
            index: The index of the item (0-based)
            quantity: The quantity to set
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            quantity_input = items[index].find_element(*self.ITEM_QUANTITY_INPUT)
            self.driver.execute_script("arguments[0].value = '';", quantity_input)
            quantity_input.send_keys(str(quantity))
            # Trigger change event to update cart
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", quantity_input)
    
    def increase_item_quantity(self, index=0):
        """
        Increase the quantity of an item in the cart
        
        Args:
            index: The index of the item (0-based)
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            increase_button = items[index].find_element(*self.INCREASE_BUTTON)
            increase_button.click()
    
    def decrease_item_quantity(self, index=0):
        """
        Decrease the quantity of an item in the cart
        
        Args:
            index: The index of the item (0-based)
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            decrease_button = items[index].find_element(*self.DECREASE_BUTTON)
            decrease_button.click()
    
    def remove_item(self, index=0):
        """
        Remove an item from the cart
        
        Args:
            index: The index of the item (0-based)
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        if 0 <= index < len(items):
            remove_button = items[index].find_element(*self.REMOVE_BUTTON)
            remove_button.click()
    
    def get_subtotal(self):
        """
        Get the cart subtotal
        
        Returns:
            The subtotal as a string
        """
        return self.get_element_text(self.SUBTOTAL)
    
    def get_estimated_total(self):
        """
        Get the cart estimated total
        
        Returns:
            The estimated total as a string
        """
        return self.get_element_text(self.ESTIMATED_TOTAL_VALUE)
    
    def click_checkout(self):
        """Click the checkout button"""
        self.click_element(self.CHECKOUT_BUTTON)
    
    def click_shipping_calculator(self):
        """Click the shipping calculator link"""
        self.click_element(self.SHIPPING_CALCULATOR_LINK)
    
    def is_cart_empty(self):
        """
        Check if the cart is empty
        
        Returns:
            True if the cart is empty, False otherwise
        """
        return self.is_element_present(self.EMPTY_CART_MESSAGE)
    
    def clear_cart(self):
        """Clear all items from the cart"""
        self.open(self.CART_URL + "?clear")
    
    def is_checkout_button_enabled(self):
        """
        Check if the checkout button is enabled
        
        Returns:
            True if the checkout button is enabled, False otherwise
        """
        checkout_button = self.wait_for_element(self.CHECKOUT_BUTTON)
        return checkout_button.is_enabled()
