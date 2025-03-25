from behave import given, when, then
from features.pages.Shopify import HeaderPage, MainPage
from selenium.common.exceptions import TimeoutException

@given('I am on the Shopify homepage')
def step_impl_go_to_shopify_homepage(context):
    context.header_page = HeaderPage(context)
    context.header_page.open_homepage()

@when('I click on the logo')
def step_impl_click_logo(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    context.header_page.click_logo()

@when('I click on the "{nav_item}" navigation link')
def step_impl_click_nav_item(context, nav_item):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    
    nav_map = {
        "HOME": context.header_page.click_nav_home,
        "ABOUT": context.header_page.click_nav_about,
        "PRODUCTS": context.header_page.click_nav_products,
        "CONTACT US": context.header_page.click_nav_contact,
        "BLOG": context.header_page.click_nav_blog
    }
    
    nav_function = nav_map.get(nav_item.upper())
    if nav_function:
        nav_function()
    else:
        raise ValueError(f"Unknown navigation item: {nav_item}")

@when('I open the mobile menu')
def step_impl_open_mobile_menu(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    context.header_page.open_menu_drawer()

@when('I click on the login link in the mobile menu')
def step_impl_click_drawer_login(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    context.header_page.click_drawer_login()

@when('I click on the cart icon')
def step_impl_click_cart_icon(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    context.header_page.click_cart_icon()

@when('I search for "{search_term}"')
def step_impl_search(context, search_term):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    context.header_page.search_for(search_term)

@when('I click the Learn More button')
def step_impl_click_learn_more(context):
    context.main_page = getattr(context, 'main_page', MainPage(context))
    context.main_page.click_learn_more()

@when('I click on the left banner')
def step_impl_click_left_banner(context):
    context.main_page = getattr(context, 'main_page', MainPage(context))
    context.main_page.click_left_banner()

@when('I click on the right banner')
def step_impl_click_right_banner(context):
    context.main_page = getattr(context, 'main_page', MainPage(context))
    context.main_page.click_right_banner()

@when('I click on the Buy Now link')
def step_impl_click_buy_now(context):
    context.main_page = getattr(context, 'main_page', MainPage(context))
    context.main_page.click_buy_now()

@when('I click on the product image')
def step_impl_click_product_image(context):
    context.main_page = getattr(context, 'main_page', MainPage(context))
    context.main_page.click_product_image()

@then('I should be redirected to the homepage')
def step_impl_verify_homepage(context):
    current_url = context.driver.current_url
    assert "physicalnutrition-uk.myshopify.com/" in current_url, f"Expected to be on homepage, but was on {current_url}"

@then('I should be redirected to the "{page_name}" page')
def step_impl_verify_page_redirect(context, page_name):
    current_url = context.driver.current_url
    
    page_url_patterns = {
        "about us": "/pages/about-us",
        "products": "/collections/products",
        "contact us": "/pages/contact",
        "login": "/account/login",
        "cart": "/cart"
    }
    
    expected_pattern = page_url_patterns.get(page_name.lower())
    if expected_pattern:
        assert expected_pattern in current_url, f"Expected to be on {page_name} page, but was on {current_url}"
    else:
        assert page_name.lower() in current_url.lower(), f"Expected to be on {page_name} page, but was on {current_url}"

@then('I should see the mobile menu')
def step_impl_verify_mobile_menu(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    try:
        assert context.header_page.is_element_present(context.header_page.DRAWER_CONTAINER), "Mobile menu drawer is not visible"
    except TimeoutException:
        assert False, "Mobile menu drawer is not visible (timeout)"

@then('I should see the main navigation')
def step_impl_verify_main_navigation(context):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    assert context.header_page.is_navigation_visible(), "Main navigation is not visible"

@then('I should see the cart count is "{count}"')
def step_impl_verify_cart_count(context, count):
    if not hasattr(context, 'header_page'):
        context.header_page = HeaderPage(context)
    actual_count = context.header_page.get_cart_count()
    assert str(actual_count) == count, f"Expected cart count to be {count}, but was {actual_count}"
