from selenium.webdriver.common.by import By
from .base_page import BasePage

class HeaderPage(BasePage):
    """Page object for the Shopify header section that appears on all pages"""
    
    # Base URL for the Shopify website
    BASE_URL = "https://physicalnutrition-uk.myshopify.com/"
    
    # Locators
    LOGO = (By.CSS_SELECTOR, "a.header__heading-link")
    NAV_HOME = (By.XPATH, "//nav//a[normalize-space()='HOME']")
    NAV_ABOUT = (By.CSS_SELECTOR, "nav a[href*='/pages/about-us']")
    NAV_PRODUCTS = (By.CSS_SELECTOR, "nav a[href*='/collections/products']")
    NAV_CONTACT = (By.CSS_SELECTOR, "nav a[href*='/pages/contact']")
    NAV_BLOG = (By.CSS_SELECTOR, "nav a[href*='blog.physicalnutrition.com']")
    CART_ICON = (By.CSS_SELECTOR, "a.header__icon--cart")
    CART_COUNT = (By.CSS_SELECTOR, "div.cart-count-bubble span")
    MENU_BUTTON = (By.CSS_SELECTOR, "header-drawer summary.header__icon--menu")
    DRAWER_CONTAINER = (By.ID, "menu-drawer")
    DRAWER_LOGIN = (By.CSS_SELECTOR, "a[href*='/account/login']")
    LOCALIZATION_SELECTOR = (By.CSS_SELECTOR, "button.disclosure__button.localization-form__select")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "summary.header__icon--search")
    SEARCH_INPUT = (By.ID, "Search-In-Modal")
    SEARCH_SUBMIT = (By.CSS_SELECTOR, "button.search__button")
    
    def open_homepage(self):
        """Open the Shopify homepage"""
        self.open(self.BASE_URL)
        
    def click_logo(self):
        """Click on the logo to navigate to homepage"""
        self.click_element(self.LOGO)
        
    def click_nav_home(self):
        """Click on the HOME navigation link"""
        self.click_element(self.NAV_HOME)
        
    def click_nav_about(self):
        """Click on the ABOUT navigation link"""
        self.click_element(self.NAV_ABOUT)
        
    def click_nav_products(self):
        """Click on the PRODUCTS navigation link"""
        self.click_element(self.NAV_PRODUCTS)
        
    def click_nav_contact(self):
        """Click on the CONTACT US navigation link"""
        self.click_element(self.NAV_CONTACT)
        
    def click_nav_blog(self):
        """Click on the BLOG navigation link"""
        self.click_element(self.NAV_BLOG)
        
    def click_cart_icon(self):
        """Click on the cart icon"""
        self.click_element(self.CART_ICON)
        
    def get_cart_count(self):
        """Get the current cart count"""
        if self.is_element_present(self.CART_COUNT):
            return int(self.get_element_text(self.CART_COUNT))
        return 0
        
    def open_menu_drawer(self):
        """Open the mobile menu drawer"""
        self.click_element(self.MENU_BUTTON)
        self.wait_for_element(self.DRAWER_CONTAINER)
        
    def click_drawer_login(self):
        """Click on login link in the drawer menu"""
        self.open_menu_drawer()
        self.click_element(self.DRAWER_LOGIN)
        
    def get_selected_country(self):
        """Get the currently selected country/region"""
        return self.get_element_text(self.LOCALIZATION_SELECTOR)
        
    def search_for(self, search_term):
        """
        Perform a search using the search bar
        
        Args:
            search_term: Text to search for
        """
        self.click_element(self.SEARCH_BUTTON)
        self.clear_and_type(self.SEARCH_INPUT, search_term)
        self.click_element(self.SEARCH_SUBMIT)
        
    def is_navigation_visible(self):
        """Check if the main navigation is visible"""
        return (self.is_element_present(self.NAV_HOME) and 
                self.is_element_present(self.NAV_ABOUT) and
                self.is_element_present(self.NAV_PRODUCTS))
