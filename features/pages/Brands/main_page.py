from features.pages.Common.base_page import BasePage
from selenium.webdriver.common.by import By

class MainPage(BasePage):
    """
    Page object for the main page, containing specific elements and methods.
    """

    def __init__(self, browser):
        """
        Initialize the MainPage with a browser instance.

        :param browser: Selenium WebDriver instance
        """
        super().__init__(browser)

    @property
    def shop_now_button(self):
        return self.browser.find_element(By.CSS_SELECTOR, "a.btn[href='/range']")

    @property
    def page_title(self):
        return self.browser.find_element(By.TAG_NAME, "title")

    def click_shop_now(self):
        """
        Click on the 'SHOP NOW' button on the main page.
        """
        self.scroll_to_element(self.shop_now_button)
        self.shop_now_button.click()

    def get_page_title(self):
        """
        Get the page title text.

        :return: str: The page title text
        """
        return self.page_title.text

    def select_product(self, product_name):
        """
        Select a product by its name.

        :param product_name: str: The name of the product to select
        """
        product_link = self.browser.find_element(By.LINK_TEXT, product_name)
        self.scroll_to_element(product_link)
        product_link.click()
