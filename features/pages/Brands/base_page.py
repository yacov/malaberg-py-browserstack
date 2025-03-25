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
    
    def open(self):
        """
        Open the page using its URL.
        """
        self.browser.get(self.URL)
        self.wait_for_page_to_load()

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

    def get_element_text(self, by_locator):
        """
        Scroll to and get the text content of an element identified by the provided locator.

        :param by_locator: tuple containing Selenium By strategy and locator
        :return: string containing the text of the element
        """
        element = self.find_element(by_locator)
        self.scroll_to_element(element)
        return element.text

    def is_element_visible(self, by_locator):
        """
        Check if an element is visible on the page.

        :param by_locator: tuple containing Selenium By strategy and locator
        :return: True if element is visible, False otherwise
        """
        try:
            element = WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(by_locator))
            self.scroll_to_element(element)
            return True
        except TimeoutException:
            return False

    def is_element_present(self, by_locator):
        """
        Check if an element is present in the DOM.

        :param by_locator: tuple containing Selenium By strategy and locator
        :return: True if element is present, False otherwise
        """
        try:
            self.find_element(by_locator)
            return True
        except NoSuchElementException:
            return False

    def select_dropdown_option(self, by_locator, option_text):
        """
        Scroll to and select an option from a dropdown menu by visible text.

        :param by_locator: tuple containing Selenium By strategy and locator for the dropdown
        :param option_text: visible text of the option to be selected
        """
        element = self.find_element(by_locator)
        self.scroll_to_element(element)
        select = Select(element)
        select.select_by_visible_text(option_text)

    def get_page_title(self):
        """
        Get the title of the current page.

        :return: string containing the page title
        """
        return self.browser.title

    def get_current_url(self):
        """
        Get the URL of the current page.

        :return: string containing the current URL
        """
        return self.browser.current_url

    def wait_for_url_to_be(self, url):
        """
        Wait for the browser to navigate to a specific URL.

        :param url: expected URL
        :return: True if navigation is successful, False otherwise
        """
        return WebDriverWait(self.browser, 10).until(EC.url_to_be(url))

    def switch_to_frame(self, by_locator):
        """
        Switch the focus to an iframe on the page.

        :param by_locator: tuple containing Selenium By strategy and locator for the iframe
        """
        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it(by_locator))

    def switch_to_default_content(self):
        """
        Switch the focus back to the default content (out of any iframes).
        """
        self.browser.switch_to.default_content()

    def get_element_attribute(self, by_locator, attribute_name):
        """
        Get the value of an attribute from an element.

        :param by_locator: tuple containing Selenium By strategy and locator
        :param attribute_name: name of the attribute
        :return: value of the attribute
        """
        element = self.find_element(by_locator)
        self.scroll_to_element(element)
        return element.get_attribute(attribute_name)

    def wait_for_element_to_disappear(self, by_locator, timeout=10):
        """
        Wait until the specified element disappears from the page.

        :param by_locator: tuple containing Selenium By strategy and locator
        :param timeout: maximum time to wait in seconds
        """
        WebDriverWait(self.browser, timeout).until(EC.invisibility_of_element_located(by_locator))

    def is_element_not_present(self, by_locator, timeout=10):
        """
        Check if an element is not present on the page.

        :param by_locator: tuple containing Selenium By strategy and locator
        :param timeout: maximum time to wait in seconds
        :return: True if element is not present, False otherwise
        """
        try:
            WebDriverWait(self.browser, timeout).until_not(EC.presence_of_element_located(by_locator))
            return True
        except TimeoutException:
            return False

    def wait_for_page_to_load(self, timeout=10):
        """
        Wait for the page to complete loading.

        :param timeout: maximum time to wait in seconds
        """
        WebDriverWait(self.browser, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
