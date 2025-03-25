from selenium.webdriver.common.by import By
from .base_page import BasePage

class MainPage(BasePage):
    """Page object for the Shopify main page"""
    
    # Base URL for the Shopify website
    BASE_URL = "https://physicalnutrition-uk.myshopify.com/"
    
    # Hero Section Locators
    LEARN_MORE_BUTTON = (By.CSS_SELECTOR, "a.green_btn")
    LEFT_BANNER_LINK_LEFT = (By.CSS_SELECTOR, ".left_side a.internal-link-left")
    LEFT_BANNER_LINK_RIGHT = (By.CSS_SELECTOR, ".left_side a.internal-link-right")
    BANNER_IMAGE_LEFT = (By.CSS_SELECTOR, ".left_side img.back")
    NATURAL_LABEL_IMAGE = (By.CSS_SELECTOR, ".left_side .natural_label img")
    COFOUNDER_IMAGE = (By.CSS_SELECTOR, ".cofounder_cont img")
    COFOUNDER_NAME = (By.CSS_SELECTOR, ".cofounder_cont .name")
    COFOUNDER_POSITION = (By.CSS_SELECTOR, ".cofounder_cont .position")
    
    # Part 3 - Product Content Sections
    PRODUCT_SECTION_TITLE = (By.CSS_SELECTOR, ".info_content h3")
    PRODUCT_SECTION_DESC = (By.CSS_SELECTOR, ".info_content p")
    
    # Part 4 - Product Image and Buy Now Links
    PRODUCT_IMAGE = (By.CSS_SELECTOR, ".product_image img")
    BUY_NOW_LINK = (By.CSS_SELECTOR, "a.buy_now")
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".product_details h3")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, ".product_details p")
    
    def open_main_page(self):
        """Open the Shopify main page"""
        self.open(self.BASE_URL)
        
    def click_learn_more(self):
        """Click on the Learn More button in the hero section"""
        learn_more = self.wait_for_clickable(self.LEARN_MORE_BUTTON)
        self.scroll_to_element(learn_more)
        learn_more.click()
        
    def click_left_banner(self):
        """Click on the left banner link"""
        left_banner = self.wait_for_clickable(self.LEFT_BANNER_LINK_LEFT)
        self.scroll_to_element(left_banner)
        left_banner.click()
        
    def click_right_banner(self):
        """Click on the right banner link"""
        right_banner = self.wait_for_clickable(self.LEFT_BANNER_LINK_RIGHT)
        self.scroll_to_element(right_banner)
        right_banner.click()
        
    def get_cofounder_info(self):
        """
        Get the cofounder information displayed on the page
        
        Returns:
            Dictionary containing name and position
        """
        name = self.get_element_text(self.COFOUNDER_NAME)
        position = self.get_element_text(self.COFOUNDER_POSITION)
        return {
            "name": name,
            "position": position
        }
        
    def check_images_loaded(self):
        """
        Check if all images on the main page are properly loaded
        
        Returns:
            Dictionary with image names as keys and boolean values indicating load status
        """
        banner_image = self.wait_for_element(self.BANNER_IMAGE_LEFT)
        natural_label = self.wait_for_element(self.NATURAL_LABEL_IMAGE)
        cofounder_image = self.wait_for_element(self.COFOUNDER_IMAGE)
        
        return {
            "banner_image": self.is_image_loaded(banner_image),
            "natural_label": self.is_image_loaded(natural_label),
            "cofounder_image": self.is_image_loaded(cofounder_image)
        }
        
    def get_product_section_content(self, index=0):
        """
        Get the content of a product section
        
        Args:
            index: Index of the product section to get content from
            
        Returns:
            Dictionary containing title and description
        """
        # Modify locators to target specific section by index
        title_locator = (By.CSS_SELECTOR, f".info_content:nth-child({index+1}) h3")
        desc_locator = (By.CSS_SELECTOR, f".info_content:nth-child({index+1}) p")
        
        title = self.get_element_text(title_locator)
        description = self.get_element_text(desc_locator)
        
        return {
            "title": title,
            "description": description
        }
        
    def click_buy_now(self, index=0):
        """
        Click on Buy Now link for a specific product
        
        Args:
            index: Index of the product to click Buy Now for
        """
        buy_now_locator = (By.CSS_SELECTOR, f"a.buy_now:nth-child({index+1})")
        self.click_element(buy_now_locator)
        
    def click_product_image(self, index=0):
        """
        Click on a product image
        
        Args:
            index: Index of the product image to click
        """
        product_image_locator = (By.CSS_SELECTOR, f".product_image:nth-child({index+1}) img")
        product_image = self.wait_for_clickable(product_image_locator)
        self.scroll_to_element(product_image)
        product_image.click()
