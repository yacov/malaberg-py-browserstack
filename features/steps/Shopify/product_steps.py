from behave import given, when, then
from features.pages.Shopify.product_page import ProductPage
from selenium.common.exceptions import TimeoutException

@given('I am on the product page for "{product_handle}"')
def step_impl_go_to_product_page(context, product_handle):
    context.product_page = ProductPage(context)
    context.product_page.open_product_page(product_handle)

@when('I select product variant {index} by index')
def step_impl_select_variant_by_index(context, index):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.select_variant_by_index(int(index))
    except TimeoutException:
        assert False, f"Could not select variant by index {index} (timeout)"

@when('I select product variant "{value}" by value')
def step_impl_select_variant_by_value(context, value):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.select_variant_by_value(value)
    except TimeoutException:
        assert False, f"Could not select variant by value '{value}' (timeout)"

@when('I select color "{color_name}"')
def step_impl_select_color(context, color_name):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.select_color_by_name(color_name)
    except TimeoutException:
        assert False, f"Could not select color '{color_name}' (timeout)"

@when('I click gallery thumbnail {index}')
def step_impl_click_gallery_thumbnail(context, index):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.click_gallery_thumbnail(int(index))
    except TimeoutException:
        assert False, f"Could not click gallery thumbnail {index} (timeout)"

@when('I set quantity to {quantity}')
def step_impl_set_quantity(context, quantity):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.set_quantity(quantity)
    except TimeoutException:
        assert False, f"Could not set quantity to {quantity} (timeout)"

@when('I increase the quantity {times} times')
def step_impl_increase_quantity(context, times):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.increase_quantity(int(times))
    except TimeoutException:
        assert False, f"Could not increase quantity {times} times (timeout)"

@when('I decrease the quantity {times} times')
def step_impl_decrease_quantity(context, times):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.decrease_quantity(int(times))
    except TimeoutException:
        assert False, f"Could not decrease quantity {times} times (timeout)"

@when('I click Add to Cart')
def step_impl_click_add_to_cart(context):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.click_add_to_cart()
    except TimeoutException:
        assert False, "Could not click Add to Cart button (timeout)"

@when('I click Buy Now')
def step_impl_click_buy_now(context):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.click_buy_now()
    except TimeoutException:
        assert False, "Could not click Buy Now button (timeout)"

@when('I select Subscribe and Save option')
def step_impl_select_subscribe_and_save(context):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.select_subscribe_and_save()
    except TimeoutException:
        assert False, "Could not select Subscribe and Save option (timeout)"

@when('I select subscription frequency "{frequency_value}"')
def step_impl_select_subscription_frequency(context, frequency_value):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.select_subscription_frequency(frequency_value)
    except TimeoutException:
        assert False, f"Could not select subscription frequency '{frequency_value}' (timeout)"

@when('I expand FAQ item {index}')
def step_impl_expand_faq(context, index):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        context.product_page.expand_faq_by_index(int(index))
    except TimeoutException:
        assert False, f"Could not expand FAQ item {index} (timeout)"

@then('I should see the product title "{title}"')
def step_impl_verify_product_title(context, title):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        actual_title = context.product_page.get_product_title()
        assert title in actual_title, f"Expected title to contain '{title}', but got '{actual_title}'"
    except TimeoutException:
        assert False, "Could not get product title (timeout)"

@then('I should see the product price "{price}"')
def step_impl_verify_product_price(context, price):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        actual_price = context.product_page.get_product_price()
        assert price in actual_price, f"Expected price to contain '{price}', but got '{actual_price}'"
    except TimeoutException:
        assert False, "Could not get product price (timeout)"

@then('I should see {count} FAQ items')
def step_impl_verify_faq_count(context, count):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        actual_count = context.product_page.get_faq_count()
        assert int(count) == actual_count, f"Expected {count} FAQ items, but got {actual_count}"
    except TimeoutException:
        assert False, "Could not get FAQ count (timeout)"

@then('FAQ item {index} should be expanded')
def step_impl_verify_faq_expanded(context, index):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        assert context.product_page.is_faq_expanded(int(index)), f"FAQ item {index} is not expanded"
    except TimeoutException:
        assert False, f"Could not check if FAQ item {index} is expanded (timeout)"

@then('I should see the current quantity is {quantity}')
def step_impl_verify_quantity(context, quantity):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        actual_quantity = context.product_page.get_current_quantity()
        assert int(quantity) == actual_quantity, f"Expected quantity to be {quantity}, but got {actual_quantity}"
    except TimeoutException:
        assert False, "Could not get current quantity (timeout)"

@then('The featured image should be loaded')
def step_impl_verify_featured_image_loaded(context):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        driver = getattr(context, 'driver', None) or getattr(context, 'browser', None)
        featured_image = driver.find_element(*context.product_page.FEATURED_IMAGE)
        assert context.product_page.is_image_loaded(featured_image), "Featured image is not loaded"
    except TimeoutException:
        assert False, "Could not check if featured image is loaded (timeout)"

@then('I should see the product description')
def step_impl_verify_product_description(context):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        driver = getattr(context, 'driver', None) or getattr(context, 'browser', None)
        desc = driver.find_element(*context.product_page.PRODUCT_DESCRIPTION)
        assert desc.is_displayed(), "Product description is not displayed"
    except TimeoutException:
        assert False, "Could not check if product description is displayed (timeout)"

@then('The featured image should change')
def step_impl_verify_featured_image_changed(context):
    # Implementation needed
    pass

@then('The featured image should revert back')
def step_impl_verify_featured_image_reverted(context):
    # Implementation needed
    pass

@then('I should see the cart count is "{count}"')
def step_impl_verify_cart_count(context, count):
    # Implementation needed - this should be moved to navigation_steps.py
    pass

@then('I should be redirected to the "{page_name}" page')
def step_impl_verify_redirected_to_page(context, page_name):
    # Implementation needed - this should be moved to navigation_steps.py
    pass

@then('I should see the prebiotic description contains "{text}"')
def step_impl_verify_prebiotic_description(context, text):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        driver = getattr(context, 'driver', None) or getattr(context, 'browser', None)
        prebiotic_desc = driver.find_element(*context.product_page.PREBIOTIC_DESCRIPTION).text
        assert text in prebiotic_desc, f"Expected prebiotic description to contain '{text}', but it doesn't"
    except TimeoutException:
        assert False, f"Could not check if prebiotic description contains '{text}' (timeout)"

@then('I should see the probiotic description contains "{text}"')
def step_impl_verify_probiotic_description(context, text):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        driver = getattr(context, 'driver', None) or getattr(context, 'browser', None)
        probiotic_desc = driver.find_element(*context.product_page.PROBIOTIC_DESCRIPTION).text
        assert text in probiotic_desc, f"Expected probiotic description to contain '{text}', but it doesn't"
    except TimeoutException:
        assert False, f"Could not check if probiotic description contains '{text}' (timeout)"

@then('I should see the postbiotic description contains "{text}"')
def step_impl_verify_postbiotic_description(context, text):
    if not hasattr(context, 'product_page'):
        context.product_page = ProductPage(context)
    try:
        driver = getattr(context, 'driver', None) or getattr(context, 'browser', None)
        postbiotic_desc = driver.find_element(*context.product_page.POSTBIOTIC_DESCRIPTION).text
        assert text in postbiotic_desc, f"Expected postbiotic description to contain '{text}', but it doesn't"
    except TimeoutException:
        assert False, f"Could not check if postbiotic description contains '{text}' (timeout)"
