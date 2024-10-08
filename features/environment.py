from selenium import webdriver
from features.pages.main_page import MainPage
from features.pages.product_page import ProductPage
from features.pages.cart_page import CartPage
from features.pages.checkout_page import CheckoutPage

def before_all(context):
    desired_capabilities = {
        'browserName': 'chrome'
    }
    context.browser = webdriver.Remote(
        desired_capabilities=desired_capabilities,
        command_executor="http://localhost:4444/wd/hub"
    )

def before_scenario(context, scenario):
    context.main_page = MainPage(context.browser)
    context.product_page = ProductPage(context.browser)
    context.cart_page = CartPage(context.browser)
    context.checkout_page = CheckoutPage(context.browser)

def after_all(context):
    context.browser.quit()
