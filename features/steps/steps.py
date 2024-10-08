import time
from selenium.webdriver.common.by import By
from behave import given, when, then, step
from features.pages.main_page import MainPage
from features.pages.product_page import ProductPage
from features.pages.cart_page import CartPage
from features.pages.checkout_page import CheckoutPage

# Remove these steps as they're not using the POM:
# @step('visit url "{url}"')
# @step("item with xpath '{selector}' is present to be added to cart")
# @step("add to cart button '{selector}' for above item is clicked")
# @step("item in cart '{selector}' is same as the one which was added")

@step('title contains "{title}"')
def check_title(context, title):
    assert title in context.browser.title

@step('user clicks on the SHOP NOW button')
def click_shop_now(context):
    context.main_page.click_shop_now()

@step('user proceeds to checkout')
def step_user_proceeds_to_checkout(context):
    context.cart_page.proceed_to_checkout()

@step('user fills out the checkout form')
def step_user_fills_checkout_form(context):
    context.checkout_page.fill_in_checkout_form(
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        phone='123456789',
        address='123 Main St',
        city='Testville',
        postcode='12345',
        country='US'
    )

@step('the purchase should be successfully completed')
def step_purchase_completed(context):
    assert "Thank you for your purchase!" in context.browser.page_source

@step('user is on the product page')
def step_user_is_on_product_page(context):
    context.product_page.load()

@step('user subscribes to product')
def step_user_subscribes_to_product(context):
    context.product_page.click_to_subscribe()

@step('user adds the product to the cart')
def step_user_adds_product_to_cart(context):
    context.product_page.add_to_cart()

@step('user is on the cart page')
def step_user_is_on_cart_page(context):
    context.cart_page.load()
    assert context.cart_page.is_url_matches(), "User is not on the cart page"

@step('user sees the message "Item has been added to cart"')
def step_user_sees_success_message(context):
    assert context.cart_page.is_success_message_displayed(), "Success message is not displayed"

@step('the purchase type is "Subscribe & Save"')
def step_purchase_type_is_subscribe_and_save(context):
    purchase_type = context.cart_page.get_purchase_type()
    assert purchase_type == "Subscribe & Save", f"Purchase type is {purchase_type}, expected 'Subscribe & Save'"

@step('user is on the FAQ section')
def step_user_is_on_faq_section(context):
    context.product_page.load()
    # You might want to add a method in ProductPage to scroll to the FAQ section
    # context.product_page.scroll_to_faq_section()

@step('the FAQ title is "{expected_title}"')
def step_check_faq_title(context, expected_title):
    actual_title = context.product_page.get_faq_title()
    assert actual_title == expected_title, f"Expected FAQ title '{expected_title}', but got '{actual_title}'"

@step('user clicks on accordion button {index}')
def step_click_accordion_button(context, index):
    context.product_page.click_accordion_button(int(index) - 1)  # Convert to 0-based index

@step('accordion section {index} should be expanded')
def step_check_accordion_section_expanded(context, index):
    assert context.product_page.is_section_expanded(int(index) - 1), f"Accordion section {index} is not expanded"

@step('only one accordion section should be expanded')
def step_check_only_one_section_expanded(context):
    expanded_sections = context.product_page.get_expanded_sections()
    assert len(expanded_sections) == 1, f"Expected 1 expanded section, but found {len(expanded_sections)}"

@step('accordion section {index} should be collapsed')
def step_check_accordion_section_collapsed(context, index):
    assert not context.product_page.is_section_expanded(int(index) - 1), f"Accordion section {index} is not collapsed"

@step('user should see the cart title "{expected_title}"')
def step_user_should_see_cart_title(context, expected_title):
    actual_title = context.cart_page.get_cart_title()
    assert actual_title == expected_title, f"Expected cart title '{expected_title}', but got '{actual_title}'"

@step('user should see the product "{product_name}" with correct image and description')
def step_user_sees_product_in_cart(context, product_name):
    assert context.cart_page.is_product_displayed(product_name), f"Product '{product_name}' is not displayed in the cart"
    assert context.cart_page.is_product_image_displayed(), "Product image is not displayed"

@step('user increases the quantity to {quantity:d}')
def step_user_increases_quantity(context, quantity):
    context.cart_page.update_quantity(quantity)
    context.cart_page.update_cart()
    context.cart_page.wait_for_cart_to_update()

@step('the total price should be updated correctly')
def step_total_price_updated_correctly(context):
    unit_price = context.cart_page.get_unit_price()
    quantity = context.cart_page.get_quantity()
    expected_total = unit_price * quantity
    actual_total = context.cart_page.get_total_price()
    assert actual_total == expected_total, f"Total price is {actual_total}, expected {expected_total}"

@step('user decreases the quantity to {quantity:d}')
def step_user_decreases_quantity(context, quantity):
    context.cart_page.update_quantity(quantity)
    context.cart_page.update_cart()
    context.cart_page.wait_for_cart_to_update()

@step('user removes the item')
def step_user_removes_item(context):
    context.cart_page.remove_item()
    context.cart_page.wait_for_cart_to_update()

@step('the cart should be empty')
def step_cart_should_be_empty(context):
    assert context.cart_page.is_cart_empty(), "Cart is not empty"

@step('user adds the product "{product_name}" to the cart')
def step_user_adds_specific_product_to_cart(context, product_name):
    context.product_page.load()
    # Assuming a method to select product by name exists
    context.product_page.select_product_by_name(product_name)
    context.product_page.add_to_cart()

@step('user applies a valid coupon code "{coupon_code}"')
def step_apply_coupon_code(context, coupon_code):
    context.cart_page.apply_coupon(coupon_code)
    context.cart_page.wait_for_cart_to_update()

@step('the discount should be applied')
def step_discount_should_be_applied(context):
    assert context.cart_page.is_discount_applied(), "Discount was not applied"

@step('user applies an invalid coupon code "{coupon_code}"')
def step_apply_invalid_coupon(context, coupon_code):
    context.cart_page.apply_coupon(coupon_code)
    context.cart_page.wait_for_cart_to_update()

@step('an error message should be displayed')
def step_error_message_displayed(context):
    assert context.cart_page.is_error_message_displayed(), "Error message was not displayed"

@step('user should be on the checkout page')
def step_user_should_be_on_checkout_page(context):
    assert context.checkout_page.is_url_matches(), "User is not on the checkout page"

@step('user tries to proceed to checkout with an empty cart')
def step_user_tries_proceed_checkout_empty_cart(context):
    context.cart_page.proceed_to_checkout()

@step('user should be prevented from proceeding')
def step_user_prevented_from_proceeding(context):
    assert context.cart_page.is_prevented_from_checkout(), "User was not prevented from proceeding with an empty cart"