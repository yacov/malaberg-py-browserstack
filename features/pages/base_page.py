from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BasePage:
    """
    Base class for all page objects. Provides common methods for interacting with web elements.
    """

    def __init__(self, browser):
        """
        Initialize the BasePage with a browser instance.
        
        :param browser: Selenium WebDriver instance
        """
        self.browser = browser

    def find_element(self, by_locator):
        """
        Find and return a web element using the provided locator.
        
        :param by_locator: tuple containing Selenium By strategy and locator
        :return: WebElement if found
        :raises: TimeoutException if element is not found within 10 seconds
        """
        return WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(by_locator))

    def find_elements(self, by_locator):
        """
        Find and return a list of web elements using the provided locator.
        
        :param by_locator: tuple containing Selenium By strategy and locator
        :return: list of WebElements if found
        :raises: TimeoutException if no elements are found within 10 seconds
        """
        return WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located(by_locator))

    def scroll_to_element(self, element):
        """
        Scroll the page to bring an element into view.
        
        :param element: WebElement to scroll to
        """
        self.browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

    def click_element(self, by_locator):
        """
        Click on a web element identified by the provided locator.
        
        :param by_locator: tuple containing Selenium By strategy and locator
        """
        element = self.find_element(by_locator)
        self.scroll_to_element(element)
        element.click()

    def enter_text(self, by_locator, text):
        """
        Enter text into an input field identified by the provided locator.
        
        :param by_locator: tuple containing Selenium By strategy and locator
        :param text: string to be entered into the input field
        """
        element = self.find_element(by_locator)
        self.scroll_to_element(element)
        element.clear()
        element.send_keys(text)

    # ... existing methods remain unchanged ...