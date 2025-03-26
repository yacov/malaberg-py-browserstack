from selenium.webdriver.common.by import By
from .base_page import BasePage

class ProductPage(BasePage):
    """Page object for Shopify product page"""

    # Product information locators
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1.product__title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "span.price-item--regular")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, "div.product__description")
    
    # Product options and variants
    VARIANT_SELECTOR = (By.CSS_SELECTOR, "select.product-form__input")
    VARIANT_OPTIONS = (By.CSS_SELECTOR, "select.product-form__input option")
    COLOR_BUTTONS = (By.CSS_SELECTOR, "fieldset[data-option-selector] input[type='radio']")
    
    # Product gallery
    FEATURED_IMAGE = (By.CSS_SELECTOR, "img.product__media-item--featured")
    GALLERY_THUMBNAILS = (By.CSS_SELECTOR, "div.product__media-list button.thumbnail")
    
    # Quantity selector
    QUANTITY_INPUT = (By.CSS_SELECTOR, "input.quantity__input")
    QUANTITY_INCREASE = (By.CSS_SELECTOR, "button[name='plus']")
    QUANTITY_DECREASE = (By.CSS_SELECTOR, "button[name='minus']")
    
    # Add to cart and buy now buttons
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "button[name='add']")
    BUY_NOW_BUTTON = (By.CSS_SELECTOR, "button[data-shopify='payment-button']")
    
    # Cart icon in header
    CART_ICON = (By.CSS_SELECTOR, "a.header__icon--cart")
    
    # Subscribe and save
    SUBSCRIBE_OPTION = (By.CSS_SELECTOR, "input#subscribe-and-save")
    SUBSCRIPTION_FREQUENCY = (By.CSS_SELECTOR, "select#subscription-frequency")
    
    # FAQ section
    FAQ_ITEMS = (By.CSS_SELECTOR, "div.faq_item")
    FAQ_BUTTONS = (By.CSS_SELECTOR, "div.faq_item button")
    FAQ_TEXT_CONTAINERS = (By.CSS_SELECTOR, "div.faq_item div.text_cont")
    
    # Science section
    SCIENCE_HEADER = (By.CSS_SELECTOR, "div.container > h3.h3")
    BACTERIA_DESCRIPTION = (By.CSS_SELECTOR, "h4.h4.smaller-ingredients-header")
    PREBIOTIC_IMAGE = (By.CSS_SELECTOR, "div.column_item:nth-child(1) img")
    PROBIOTIC_IMAGE = (By.CSS_SELECTOR, "div.column_item:nth-child(2) img")
    POSTBIOTIC_IMAGE = (By.CSS_SELECTOR, "div.column_item:nth-child(3) img")
    PREBIOTIC_DESCRIPTION = (By.CSS_SELECTOR, "div.column_item:nth-child(1) p.text")
    PROBIOTIC_DESCRIPTION = (By.CSS_SELECTOR, "div.column_item:nth-child(2) p.text")
    POSTBIOTIC_DESCRIPTION = (By.CSS_SELECTOR, "div.column_item:nth-child(3) p.text")
    
    def open_product_page(self, product_handle):
        """
        Open a specific product page
        
        Args:
            product_handle: The product handle in the URL (e.g., 'gut-rewild')
        """
        # Use a proper Shopify URL
        shopify_url = "https://physicalnutrition-uk.myshopify.com"
        
        # Check if we have a base_url in the context
        if hasattr(self.context, 'base_url') and self.context.base_url:
            shopify_url = self.context.base_url
        
        # Log the URL we're trying to access
        self.context.logger.info(f"Opening product page: {shopify_url}/products/{product_handle}")
        
        # Navigate to the product page
        self.open(f"{shopify_url}/products/{product_handle}")
    
    def get_product_title(self):
        """Get the product title text"""
        return self.get_element_text(self.PRODUCT_TITLE)
    
    def get_product_price(self):
        """Get the product price text"""
        return self.get_element_text(self.PRODUCT_PRICE)
    
    def get_product_description(self):
        """Get the product description text"""
        return self.get_element_text(self.PRODUCT_DESCRIPTION)
    
    def select_variant_by_index(self, index):
        """
        Select a product variant by its index
        
        Args:
            index: The index of the variant option to select
        """
        variant_select = self.wait_for_element(self.VARIANT_SELECTOR)
        options = variant_select.find_elements(*self.VARIANT_OPTIONS[0])
        if 0 <= index < len(options):
            options[index].click()
    
    def select_variant_by_value(self, value):
        """
        Select a product variant by its value
        
        Args:
            value: The value of the variant option to select
        """
        variant_select = self.wait_for_element(self.VARIANT_SELECTOR)
        self.driver.execute_script(f"arguments[0].value = '{value}';", variant_select)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", variant_select)
    
    def select_color_by_name(self, color_name):
        """
        Select a product color by its name
        
        Args:
            color_name: The name of the color to select
        """
        color_buttons = self.driver.find_elements(*self.COLOR_BUTTONS)
        for button in color_buttons:
            if button.get_attribute("value").lower() == color_name.lower():
                button.click()
                break
    
    def click_gallery_thumbnail(self, index):
        """
        Click on a gallery thumbnail by index
        
        Args:
            index: The index of the thumbnail to click
        """
        thumbnails = self.driver.find_elements(*self.GALLERY_THUMBNAILS)
        if 0 <= index < len(thumbnails):
            thumbnails[index].click()
    
    def set_quantity(self, quantity):
        """
        Set the product quantity
        
        Args:
            quantity: The quantity to set
        """
        self.clear_and_type(self.QUANTITY_INPUT, str(quantity))
    
    def increase_quantity(self, times=1):
        """
        Increase the product quantity by clicking the plus button
        
        Args:
            times: Number of times to click the increase button
        """
        for _ in range(times):
            self.click_element(self.QUANTITY_INCREASE)
    
    def decrease_quantity(self, times=1):
        """
        Decrease the product quantity by clicking the minus button
        
        Args:
            times: Number of times to click the decrease button
        """
        for _ in range(times):
            self.click_element(self.QUANTITY_DECREASE)
    
    def get_current_quantity(self):
        """Get the current quantity value"""
        quantity_input = self.wait_for_element(self.QUANTITY_INPUT)
        return int(quantity_input.get_attribute("value"))
    
    def click_add_to_cart(self):
        """Click the Add to Cart button"""
        self.click_element(self.ADD_TO_CART_BUTTON)
    
    def click_buy_now(self):
        """Click the Buy Now button"""
        self.click_element(self.BUY_NOW_BUTTON)
    
    def select_subscribe_and_save(self):
        """Select the Subscribe & Save option"""
        self.click_element(self.SUBSCRIBE_OPTION)
    
    def select_subscription_frequency(self, frequency_value):
        """
        Select a subscription frequency
        
        Args:
            frequency_value: The value of the frequency option to select
        """
        subscription_select = self.wait_for_element(self.SUBSCRIPTION_FREQUENCY)
        self.driver.execute_script(f"arguments[0].value = '{frequency_value}';", subscription_select)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", subscription_select)
    
    def expand_faq_by_index(self, index):
        """
        Expand an FAQ item by index
        
        Args:
            index: The index of the FAQ item to expand
        """
        faq_buttons = self.driver.find_elements(*self.FAQ_BUTTONS)
        if 0 <= index < len(faq_buttons):
            faq_buttons[index].click()
    
    def is_faq_expanded(self, index):
        """
        Check if an FAQ item is expanded
        
        Args:
            index: The index of the FAQ item to check
            
        Returns:
            True if the FAQ is expanded, False otherwise
        """
        faq_text_containers = self.driver.find_elements(*self.FAQ_TEXT_CONTAINERS)
        if 0 <= index < len(faq_text_containers):
            return faq_text_containers[index].is_displayed()
        return False
    
    def get_faq_count(self):
        """Get the total number of FAQ items"""
        faq_items = self.driver.find_elements(*self.FAQ_ITEMS)
        return len(faq_items)
    
    def get_faq_text(self, index):
        """
        Get the text content of an FAQ item
        
        Args:
            index: The index of the FAQ item
            
        Returns:
            Dictionary containing question and answer
        """
        faq_buttons = self.driver.find_elements(*self.FAQ_BUTTONS)
        faq_text_containers = self.driver.find_elements(*self.FAQ_TEXT_CONTAINERS)
        
        if 0 <= index < len(faq_buttons) and 0 <= index < len(faq_text_containers):
            question = faq_buttons[index].text
            # Expand the FAQ if not already expanded
            if not self.is_faq_expanded(index):
                faq_buttons[index].click()
            answer = faq_text_containers[index].text
            return {
                "question": question,
                "answer": answer
            }
        return None
    
    def click_cart_icon(self):
        """Click the cart icon in the header"""
        self.click_element(self.CART_ICON)
