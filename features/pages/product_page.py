import signal
from typing import Self

from yaml import scan
from .base_page import BasePage
from selenium.webdriver.common.by import By

class ProductPage(BasePage):
    """
    Page object for the product page, containing specific elements and methods.
    """

    def __init__(self, browser):
        """
        Initialize the ProductPage with a browser instance and set the URL.
        
        :param browser: Selenium WebDriver instance
        """
        super().__init__(browser)
        self.url = "https://aeonstest.info/products/aeons-total-harmony"

    @property
    def add_to_cart_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, "button.add-to-cart")

    @property
    def size_radio_button_250ml(self):
        return self.browser.find_element(By.ID, "sylius_add_to_cart_cartItem_variant_0")

    @property
    def size_radio_button_3bottles(self):
        return self.browser.find_element(By.ID, "sylius_add_to_cart_cartItem_variant_1")

    @property
    def subscribe_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".purchase-option[data-variant-option-subscription='yes']")

    @property
    def faq_title(self):
        return self.browser.find_element(By.CSS_SELECTOR, "p.h1")

    @property
    def accordion_buttons(self):
        return self.browser.find_elements(By.CSS_SELECTOR, ".accordion-button")

    @property
    def expanded_sections(self):
        return self.browser.find_elements(By.CSS_SELECTOR, ".accordion-collapse.show")

    def load(self):
        """
        Navigate to the product page URL.
        """
        self.browser.get(self.url)
        self.wait_for_page_to_load()

    def add_to_cart(self):
        """
        Click the 'Add to Cart' button on the product page.
        """
        self.scroll_to_element(self.add_to_cart_button)
        self.add_to_cart_button.click()

    def select_size(self, size_option):
        """
        Select the size of the product.
        
        :param size_option: string, either '250ml' or '3bottles'
        :raises ValueError: if an invalid size option is provided
        """
        if size_option == '250ml':
            self.scroll_to_element(self.size_radio_button_250ml)
            self.size_radio_button_250ml.click()
        elif size_option == '3bottles':
            self.scroll_to_element(self.size_radio_button_3bottles)
            self.size_radio_button_3bottles.click()
        else:
            raise ValueError("Invalid size option")

    def click_to_subscribe(self):
        """
        Click the subscribe button for the product.
        """
        self.scroll_to_element(self.subscribe_button)
        self.subscribe_button.click()

    def get_faq_title(self):
        """
        Get the text of the FAQ title.
        
        :return: string containing the FAQ title text
        """
        return self.faq_title.text

    def click_accordion_button(self, index):
        """
        Click on a specific accordion button.
        
        :param index: zero-based index of the accordion button to click
        :raises ValueError: if the provided index is out of range
        """
        buttons = self.accordion_buttons
        if 0 <= index < len(buttons):
            self.scroll_to_element(buttons[index])
            buttons[index].click()
        else:
            raise ValueError("Invalid accordion button index")

    def is_section_expanded(self, index):
        """
        Check if a specific accordion section is expanded.
        
        :param index: zero-based index of the accordion section to check
        :return: True if the section is expanded, False otherwise
        """
        expanded_sections = self.expanded_sections
        return len(expanded_sections) > index

    def select_product_by_name(self, product_name):
        """
        Select the product by its name.
        
        :param product_name: Name of the product to select
        """
        product_link = self.browser.find_element(By.LINK_TEXT, product_name)
        self.scroll_to_element(product_link)
        product_link.click()