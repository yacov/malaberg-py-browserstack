import logging
import time
from behave import given, when, then, step
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def wait_for_element(context, by, selector, timeout=10):
    """Utility function for explicit waits"""
    return WebDriverWait(context.browser, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

@step('user is on the product page')
def step_user_is_on_product_page(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Loading Product Page", "level": "info"}}'
        )
        context.product_page.load()
        logger.info("Successfully loaded product page")
    except TimeoutException:
        logger.error("Failed to load product page")
        raise

@step('user subscribes to product')
def step_user_subscribes_to_product(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Product Subscription", "level": "info"}}'
        )
        context.product_page.click_to_subscribe()
        logger.info("Successfully subscribed to product")
    except TimeoutException:
        logger.error("Failed to subscribe to product")
        raise

@step('user adds the product to the cart')
def step_user_adds_product_to_cart(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Add to Cart Action", "level": "info"}}'
        )
        context.product_page.add_to_cart()
        logger.info("Successfully added product to cart")
    except TimeoutException:
        logger.error("Failed to add product to cart")
        raise

@step('user is on the cart page')
def step_user_is_on_cart_page(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Cart Page Navigation", "level": "info"}}'
        )
        context.cart_page.load()
        assert context.cart_page.is_url_matches(), "User is not on the cart page"
        logger.info("Successfully loaded cart page")
    except (TimeoutException, AssertionError) as e:
        logger.error(f"Failed to verify cart page: {e}")
        raise

@step('user sees the message "{expected_message}"')
def step_user_sees_message(context, expected_message):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Message Verification", "level": "info"}}'
        )
        assert context.cart_page.get_item_count() > 0, "No items found in cart"
        logger.info(f"Successfully verified item was added to cart")
    except AssertionError:
        logger.error("Failed to verify item in cart")
        raise

@step('the purchase type is "{expected_type}"')
def step_verify_purchase_type(context, expected_type):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Purchase Type Check", "level": "info"}}'
        )
        actual_type = context.cart_page.get_purchase_type()
        assert actual_type == expected_type, f"Expected purchase type '{expected_type}', got '{actual_type}'"
        logger.info(f"Successfully verified purchase type: {expected_type}")
    except AssertionError as e:
        logger.error(f"Purchase type verification failed: {e}")
        raise

@step('user applies a valid coupon code "{coupon_code}"')
def step_apply_coupon_code(context, coupon_code):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Coupon Application", "level": "info"}}'
        )
        success, error_message = context.cart_page.apply_coupon(coupon_code)
        assert success, f"Failed to apply coupon: {error_message}"
        logger.info(f"Successfully applied coupon: {coupon_code}")
    except AssertionError:
        logger.error(f"Coupon application failed: {error_message}")
        raise

@step('the discount should be applied')
def step_verify_discount(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Discount Verification", "level": "info"}}'
        )
        assert context.cart_page.verify_discount(), "Discount amount is incorrect"
        logger.info("Successfully verified discount")
    except AssertionError:
        logger.error("Discount verification failed")
        raise

@step('user proceeds to checkout')
def step_proceed_to_checkout(context):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Checkout Navigation", "level": "info"}}'
        )
        assert context.cart_page.proceed_to_checkout(), "Failed to proceed to checkout"
        logger.info("Successfully proceeded to checkout")
    except AssertionError:
        logger.error("Failed to proceed to checkout")
        raise

@when('visit url "{url}"')
def step_visit_url(context, url):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "URL Navigation", "level": "info"}}'
        )
        context.browser.get(url)
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        logger.info(f"Successfully navigated to {url}")
    except TimeoutException:
        logger.error(f"Failed to load URL: {url}")
        raise

@when("item with xpath '{selector}' is present to be added to cart")
def step_verify_item_presence(context, selector):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Item Presence Check", "level": "info"}}'
        )
        item = wait_for_element(context, By.XPATH, selector)
        context.item_to_add = item.text
        logger.info(f"Found item: {context.item_to_add}")
    except TimeoutException:
        logger.error(f"Item not found with selector: {selector}")
        raise

@when("add to cart button '{selector}' for above item is clicked")
def step_click_add_to_cart(context, selector):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Add to Cart Click", "level": "info"}}'
        )
        add_btn = wait_for_element(context, By.XPATH, selector)
        add_btn.click()
        # Wait for cart update animation/process
        WebDriverWait(context.browser, 10).until(
            lambda x: x.execute_script("return jQuery.active == 0")
        )
        logger.info("Successfully clicked add to cart button")
    except (TimeoutException, StaleElementReferenceException):
        logger.error("Failed to click add to cart button")
        raise

@then("item in cart '{selector}' is same as the one which was added")
def step_verify_cart_item(context, selector):
    try:
        context.browser.execute_script(
            'browserstack_executor: {"action": "annotate", "arguments": {"data": "Cart Item Validation", "level": "info"}}'
        )
        item = wait_for_element(context, By.XPATH, selector)
        item_in_cart = item.text
        assert item_in_cart == context.item_to_add, f"Expected {context.item_to_add}, got {item_in_cart}"
        logger.info("Successfully verified cart item")
    except (TimeoutException, AssertionError) as e:
        logger.error(f"Cart item verification failed: {e}")
        raise