from behave import given, when, then
from features.pages.Shopify import CartPage
from selenium.common.exceptions import TimeoutException

@given('I am on the cart page')
def step_impl_go_to_cart_page(context):
    context.cart_page = CartPage(context)
    context.cart_page.open_cart()

@when('I increase the quantity of item {index} in cart')
def step_impl_increase_item_quantity(context, index):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.increase_item_quantity(int(index))
    except TimeoutException:
        assert False, f"Could not increase item quantity (timeout)"

@when('I decrease the quantity of item {index} in cart')
def step_impl_decrease_item_quantity(context, index):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.decrease_item_quantity(int(index))
    except TimeoutException:
        assert False, f"Could not decrease item quantity (timeout)"

@when('I set the quantity of item {index} to {quantity}')
def step_impl_set_item_quantity(context, index, quantity):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.set_item_quantity(int(index), int(quantity))
    except TimeoutException:
        assert False, f"Could not set item quantity (timeout)"

@when('I remove item {index} from cart')
def step_impl_remove_item(context, index):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.remove_item(int(index))
    except TimeoutException:
        assert False, f"Could not remove item (timeout)"

@when('I click the checkout button')
def step_impl_click_checkout(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.click_checkout()
    except TimeoutException:
        assert False, f"Could not click checkout button (timeout)"

@when('I click the shipping calculator link')
def step_impl_click_shipping_calculator(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.click_shipping_calculator()
    except TimeoutException:
        assert False, f"Could not click shipping calculator link (timeout)"

@when('I clear the cart')
def step_impl_clear_cart(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        context.cart_page.clear_cart()
    except TimeoutException:
        assert False, f"Could not clear cart (timeout)"

@when('I click on the cart icon')
def step_impl_click_cart_icon(context):
    # If we're already on the product page, click the cart icon there
    if hasattr(context, 'product_page'):
        try:
            context.product_page.click_cart_icon()
        except TimeoutException:
            assert False, "Could not click cart icon on product page (timeout)"
    # Otherwise we need to ensure the cart page is initialized
    else:
        context.cart_page = CartPage(context)
        context.cart_page.open_cart()

@then('The cart should contain {count} items')
def step_impl_verify_item_count(context, count):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        actual_count = context.cart_page.get_item_count()
        assert int(count) == actual_count, f"Expected {count} items in cart, but got {actual_count}"
    except TimeoutException:
        assert False, f"Could not get cart item count (timeout)"

@then('Item {index} in cart should have name "{name}"')
def step_impl_verify_item_name(context, index, name):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        actual_name = context.cart_page.get_item_name(int(index))
        assert name in actual_name, f"Expected item name to contain '{name}', but got '{actual_name}'"
    except TimeoutException:
        assert False, f"Could not get item name (timeout)"

@then('Item {index} in cart should have quantity {quantity}')
def step_impl_verify_item_quantity(context, index, quantity):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        actual_quantity = context.cart_page.get_item_quantity(int(index))
        assert int(quantity) == actual_quantity, f"Expected item quantity to be {quantity}, but got {actual_quantity}"
    except TimeoutException:
        assert False, f"Could not get item quantity (timeout)"

@then('The subtotal should be visible')
def step_impl_verify_subtotal_visible(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        subtotal = context.cart_page.get_subtotal()
        assert subtotal, "Subtotal is not visible"
    except TimeoutException:
        assert False, "Subtotal is not visible (timeout)"

@then('The subtotal should contain "{value}"')
def step_impl_verify_subtotal_value(context, value):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        subtotal = context.cart_page.get_subtotal()
        assert value in subtotal, f"Expected subtotal to contain '{value}', but got '{subtotal}'"
    except TimeoutException:
        assert False, f"Could not get subtotal (timeout)"

@then('The estimated total should contain "{value}"')
def step_impl_verify_estimated_total(context, value):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        estimated_total = context.cart_page.get_estimated_total()
        assert value in estimated_total, f"Expected estimated total to contain '{value}', but got '{estimated_total}'"
    except TimeoutException:
        assert False, f"Could not get estimated total (timeout)"

@then('The checkout button should be enabled')
def step_impl_verify_checkout_button_enabled(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        assert context.cart_page.is_checkout_button_enabled(), "Checkout button is not enabled"
    except TimeoutException:
        assert False, "Could not check if checkout button is enabled (timeout)"

@then('The checkout button should be disabled')
def step_impl_verify_checkout_button_disabled(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        assert not context.cart_page.is_checkout_button_enabled(), "Checkout button is enabled"
    except TimeoutException:
        assert False, "Could not check if checkout button is disabled (timeout)"

@then('The cart should be empty')
def step_impl_verify_cart_empty(context):
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    try:
        assert context.cart_page.is_cart_empty(), "Cart is not empty"
    except TimeoutException:
        assert False, "Could not check if cart is empty (timeout)"
