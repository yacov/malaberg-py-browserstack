from .base_page import BasePage
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

    def click_shop_now(self):
        """
        Click on the 'SHOP NOW' button on the main page.
        """
        self.scroll_to_element(self.shop_now_button)
        self.shop_now_button.click()