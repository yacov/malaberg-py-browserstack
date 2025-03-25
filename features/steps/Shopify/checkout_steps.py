from behave import given, when, then
from features.pages.Shopify import CheckoutPage
from selenium.common.exceptions import TimeoutException

@given('I am on the checkout page')
def step_impl_go_to_checkout_page(context):
    # This step assumes that we can't directly go to the checkout page
    # The user normally needs to navigate from the cart page
    # So this step should ensure we're in the checkout flow context
    context.execute_steps('''
        Given I am on the cart page
        When I click the checkout button
    ''')
    context.checkout_page = CheckoutPage(context)

@when('I fill in the shipping information')
def step_impl_fill_shipping_info(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        # Using test data - in a real test these could come from a context table or test config
        context.checkout_page.fill_shipping_information(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            address="123 Test Street",
            city="London",
            postcode="W1A 1AA",
            phone="07123456789"
        )
    except TimeoutException:
        assert False, "Could not fill shipping information (timeout)"

@when('I fill in the shipping information with')
def step_impl_fill_shipping_info_with_data(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    
    try:
        # Extract data from context table
        data = {}
        for row in context.table:
            data[row['field']] = row['value']
        
        # Store email for backend verification
        if 'email' in data:
            context.checkout_email = data['email']
        
        # Fill in the form with the provided data
        context.checkout_page.fill_shipping_information(
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            postcode=data.get('postcode', ''),
            phone=data.get('phone', '')
        )
    except TimeoutException:
        assert False, "Could not fill shipping information with provided data (timeout)"

@when('I check "Remember me"')
def step_impl_check_remember_me(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.check_remember_me()
    except TimeoutException:
        assert False, "Could not check 'Remember me' option (timeout)"

@when('I check "Use shipping address as billing address"')
def step_impl_check_use_shipping_as_billing(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.check_use_shipping_as_billing()
    except TimeoutException:
        assert False, "Could not check 'Use shipping address as billing address' option (timeout)"

@when('I select payment method "{method}"')
def step_impl_select_payment_method(context, method):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.select_payment_method(method)
    except TimeoutException:
        assert False, f"Could not select payment method '{method}' (timeout)"

@when('I click "Pay now"')
def step_impl_click_pay_now(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.click_pay_now()
    except TimeoutException:
        assert False, "Could not click 'Pay now' button (timeout)"

@when('I click the Terms of Service link')
def step_impl_click_terms_of_service(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.click_terms_of_service()
    except TimeoutException:
        assert False, "Could not click Terms of Service link (timeout)"

@when('I click the Privacy Policy link')
def step_impl_click_privacy_policy(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.click_privacy_policy()
    except TimeoutException:
        assert False, "Could not click Privacy Policy link (timeout)"

@when('I enter invalid credit card information')
def step_impl_enter_invalid_credit_card(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        context.checkout_page.enter_invalid_credit_card()
    except TimeoutException:
        assert False, "Could not enter invalid credit card information (timeout)"

@when('I complete the test purchase')
def step_impl_complete_test_purchase(context):
    """
    Complete a test purchase without actually charging a credit card
    This step will simulate a successful purchase for testing purposes
    """
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    
    try:
        # In test mode, you might have a special payment method or test card
        # that can be used without actually creating a charge
        context.checkout_page.complete_test_purchase()
        
        # Give the system time to process the order
        import time
        time.sleep(5)
        
        # Verify success page is shown
        assert context.checkout_page.is_order_confirmation_visible(), "Order confirmation page is not visible"
    except TimeoutException:
        assert False, "Could not complete test purchase (timeout)"
    except Exception as e:
        assert False, f"Error completing test purchase: {str(e)}"

@then('I should see the order summary')
def step_impl_verify_order_summary(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        assert context.checkout_page.is_order_summary_visible(), "Order summary is not visible"
    except TimeoutException:
        assert False, "Could not check if order summary is visible (timeout)"

@then('I should see the shopping cart heading')
def step_impl_verify_shopping_cart_heading(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        assert context.checkout_page.is_shopping_cart_heading_displayed(), "Shopping cart heading is not displayed"
    except TimeoutException:
        assert False, "Could not check if shopping cart heading is displayed (timeout)"

@then('I should see the product image in checkout')
def step_impl_verify_product_image(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        assert context.checkout_page.is_product_image_displayed(), "Product image is not displayed"
    except TimeoutException:
        assert False, "Could not check if product image is displayed (timeout)"

@then('The subtotal in checkout should contain "{value}"')
def step_impl_verify_checkout_subtotal(context, value):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        subtotal = context.checkout_page.get_subtotal()
        assert value in subtotal, f"Expected subtotal to contain '{value}', but got '{subtotal}'"
    except TimeoutException:
        assert False, f"Could not get subtotal (timeout)"

@then('The shipping cost should contain "{value}"')
def step_impl_verify_shipping_cost(context, value):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        shipping_cost = context.checkout_page.get_shipping_cost()
        assert value in shipping_cost, f"Expected shipping cost to contain '{value}', but got '{shipping_cost}'"
    except TimeoutException:
        assert False, f"Could not get shipping cost (timeout)"

@then('The total cost should contain "{value}"')
def step_impl_verify_total_cost(context, value):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        total_cost = context.checkout_page.get_total_cost()
        assert value in total_cost, f"Expected total cost to contain '{value}', but got '{total_cost}'"
    except TimeoutException:
        assert False, f"Could not get total cost (timeout)"

@then('The "Pay now" button should be enabled')
def step_impl_verify_pay_now_enabled(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        assert context.checkout_page.is_pay_now_button_enabled(), "Pay now button is not enabled"
    except TimeoutException:
        assert False, "Could not check if 'Pay now' button is enabled (timeout)"

@then('The "Pay now" button should be disabled')
def step_impl_verify_pay_now_disabled(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        assert not context.checkout_page.is_pay_now_button_enabled(), "Pay now button is enabled"
    except TimeoutException:
        assert False, "Could not check if 'Pay now' button is disabled (timeout)"

@then('I should see an error message')
def step_impl_verify_error_message(context):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        error_message = context.checkout_page.get_error_message()
        assert error_message, "No error message was displayed"
    except TimeoutException:
        assert False, "Could not check for error message (timeout)"

@then('I should see an error message containing "{text}"')
def step_impl_verify_error_message_text(context, text):
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    try:
        error_message = context.checkout_page.get_error_message()
        assert error_message and text in error_message, f"Expected error message to contain '{text}', but got '{error_message}'"
    except TimeoutException:
        assert False, f"Could not check if error message contains '{text}' (timeout)"
