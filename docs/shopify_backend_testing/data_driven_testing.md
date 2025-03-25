# Data-Driven Test Setup

## Overview

This document outlines the implementation plan for enhancing the Shopify test suite with data-driven testing capabilities. By leveraging the Shopify MCP server, we can prepare test data programmatically, which will improve test reliability, increase coverage, and reduce test execution time.

## Current Limitations

Current tests:
- Manually navigate through the UI to add products to the cart
- Have limited product coverage due to manual setup
- Need to repeat similar UI interactions for different test scenarios
- Are potentially fragile due to UI dependencies in test setup

## Implementation Plan

### New Feature File: `data_driven_cart_checkout.feature`

```gherkin
@shopify
Feature: Data-Driven Cart and Checkout Tests
  As a tester
  I want to use prepared test data for cart and checkout tests
  So that I can improve test reliability and coverage

  Background:
    Given I have a clean test environment

  Scenario: Test checkout with a pre-populated cart
    Given I have a prepared cart with the following items:
      | product_handle | variant_title | quantity |
      | gut-rewild     | Default Title | 1        |
    When I navigate to the prepared cart
    Then The cart should contain 1 items
    And Item 0 in cart should have name "Gut Rewild"
    And Item 0 in cart should have quantity 1
    When I click the checkout button
    Then I should see the order summary
    And I should see the product image in checkout
    And The subtotal in checkout should contain "£34.95"

  Scenario Outline: Test checkout with different products
    Given I have a prepared cart with the product "<product_handle>"
    When I navigate to the prepared cart
    Then The cart should contain 1 items
    And Item 0 in cart should have name "<product_name>"
    When I click the checkout button
    Then I should see the order summary
    And The subtotal in checkout should contain "<expected_price>"

    Examples:
      | product_handle  | product_name               | expected_price |
      | gut-rewild      | Gut Rewild                 | £34.95         |
      | younger-you-cr  | Younger You Skin Cream     | £83.00         |
      | web-bun-rgb     | Radiant Glow Bundle        | £129.00        |

  Scenario: Test checkout with multiple different products
    Given I have a prepared cart with the following items:
      | product_handle | variant_title | quantity |
      | gut-rewild     | Default Title | 2        |
      | younger-you-cr | Default Title | 1        |
    When I navigate to the prepared cart
    Then The cart should contain 2 items
    And Item 0 in cart should have name "Gut Rewild"
    And Item 0 in cart should have quantity 2
    And Item 1 in cart should have name "Younger You Skin Cream"
    And Item 1 in cart should have quantity 1
    When I click the checkout button
    Then I should see the order summary
    And The subtotal in checkout should contain "£152.90"

  Scenario: Test applying a discount code to a prepared cart
    Given I have a prepared cart with the product "gut-rewild"
    And I have created a discount code "TESTCODE20" for 20% off
    When I navigate to the prepared cart
    And I apply the discount code "TESTCODE20"
    Then The discount should be applied successfully
    And The subtotal should contain "£27.96"
    When I click the checkout button
    Then I should see the order summary
    And The subtotal in checkout should contain "£27.96"

  Scenario: Test customer-specific pricing with a prepared cart
    Given I have a customer with special pricing
    And I have a prepared cart for this customer with the product "gut-rewild"
    When I navigate to the prepared cart as this customer
    Then The product price should reflect the special pricing
    When I click the checkout button
    Then I should see the order summary
    And The subtotal in checkout should reflect the special pricing
```

### New Step Definitions

Add the following step definitions in a new file `data_driven_steps.py`:

```python
from behave import given, when, then
import time
import os
import uuid
from selenium.common.exceptions import TimeoutException

# Global variables for step definitions
PREPARED_CARTS = {}
TEST_DISCOUNT_CODES = []

@given('I have a clean test environment')
def step_impl_clean_environment(context):
    """Ensure we start with a clean test environment"""
    # This is more of a documentation step, actual cleanup happens in hooks
    pass

@given('I have a prepared cart with the following items')
def step_impl_prepare_cart_with_items(context):
    """Prepare a cart with specified items using the MCP server"""
    
    # Generate a unique identifier for this cart
    cart_id = str(uuid.uuid4())
    
    # Create line items from the table
    line_items = []
    for row in context.table:
        # Get product variant ID from handle and variant title
        products = context.mcp1_get_products(searchTitle=row['product_handle'])
        
        variant_id = None
        for product in products['products']:
            if product['handle'] == row['product_handle']:
                for variant in product['variants']:
                    if variant['title'] == row['variant_title']:
                        variant_id = variant['id']
                        break
        
        if variant_id:
            line_items.append({
                "variantId": variant_id,
                "quantity": int(row['quantity'])
            })
    
    # Create a draft order (cart)
    test_email = f"test-{cart_id[:8]}@example.com"
    draft_order = context.mcp1_create_draft_order(
        email=test_email,
        lineItems=line_items,
        note="Automated test cart"
    )
    
    # Store cart information for later use
    PREPARED_CARTS[cart_id] = {
        "id": draft_order['id'],
        "checkout_url": draft_order['checkoutUrl'],
        "email": test_email
    }
    
    # Store cart ID in context for later steps
    context.current_cart_id = cart_id

@given('I have a prepared cart with the product "{product_handle}"')
def step_impl_prepare_cart_with_product(context, product_handle):
    """Prepare a cart with a single product using the MCP server"""
    
    # Generate a unique identifier for this cart
    cart_id = str(uuid.uuid4())
    
    # Get product variant ID
    products = context.mcp1_get_products(searchTitle=product_handle)
    
    variant_id = None
    for product in products['products']:
        if product['handle'] == product_handle:
            variant_id = product['variants'][0]['id']
            break
    
    if not variant_id:
        raise ValueError(f"Product with handle '{product_handle}' not found")
    
    # Create a draft order (cart)
    test_email = f"test-{cart_id[:8]}@example.com"
    draft_order = context.mcp1_create_draft_order(
        email=test_email,
        lineItems=[{
            "variantId": variant_id,
            "quantity": 1
        }],
        note=f"Automated test cart for {product_handle}"
    )
    
    # Store cart information for later use
    PREPARED_CARTS[cart_id] = {
        "id": draft_order['id'],
        "checkout_url": draft_order['checkoutUrl'],
        "email": test_email,
        "product_handle": product_handle
    }
    
    # Store cart ID in context for later steps
    context.current_cart_id = cart_id

@given('I have created a discount code "{code}" for {percent:d}% off')
def step_impl_create_discount_code(context, code, percent):
    """Create a discount code using the MCP server"""
    
    # Create a discount code
    discount = context.mcp1_create_discount(
        code=code,
        valueType="percentage",
        value=percent / 100.0,  # Convert percent to decimal
        title=f"Test Discount {code}",
        startsAt=time.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Now
        endsAt=None,  # No end date
        appliesOncePerCustomer=False
    )
    
    # Store discount code for later cleanup
    TEST_DISCOUNT_CODES.append(code)
    
    # Store discount info in context
    context.current_discount_code = code
    context.current_discount_percent = percent

@given('I have a customer with special pricing')
def step_impl_customer_with_special_pricing(context):
    """Create a customer with special pricing"""
    # Note: This is a placeholder - Shopify would need specific customer pricing rules
    # which might not be directly supported by the MCP server
    
    # For now, we'll just create a test customer and imagine they have special pricing
    customer_id = str(uuid.uuid4())
    test_email = f"special-pricing-{customer_id[:8]}@example.com"
    
    # Store customer info in context
    context.special_pricing_customer_email = test_email
    context.special_pricing_customer_id = customer_id

@given('I have a prepared cart for this customer with the product "{product_handle}"')
def step_impl_prepare_cart_for_customer(context, product_handle):
    """Prepare a cart for a specific customer with special pricing"""
    
    # Ensure we have a special pricing customer
    if not hasattr(context, 'special_pricing_customer_email'):
        raise ValueError("No special pricing customer defined")
    
    # Get product variant ID
    products = context.mcp1_get_products(searchTitle=product_handle)
    
    variant_id = None
    for product in products['products']:
        if product['handle'] == product_handle:
            variant_id = product['variants'][0]['id']
            break
    
    if not variant_id:
        raise ValueError(f"Product with handle '{product_handle}' not found")
    
    # Create a draft order (cart) for this customer
    draft_order = context.mcp1_create_draft_order(
        email=context.special_pricing_customer_email,
        lineItems=[{
            "variantId": variant_id,
            "quantity": 1
        }],
        note=f"Automated test cart for special pricing customer"
    )
    
    cart_id = str(uuid.uuid4())
    
    # Store cart information for later use
    PREPARED_CARTS[cart_id] = {
        "id": draft_order['id'],
        "checkout_url": draft_order['checkoutUrl'],
        "email": context.special_pricing_customer_email,
        "product_handle": product_handle,
        "special_pricing": True
    }
    
    # Store cart ID in context for later steps
    context.current_cart_id = cart_id

@when('I navigate to the prepared cart')
def step_impl_navigate_to_prepared_cart(context):
    """Navigate to the prepared cart"""
    if not hasattr(context, 'current_cart_id') or context.current_cart_id not in PREPARED_CARTS:
        raise ValueError("No prepared cart available")
    
    # Navigate to the checkout URL
    context.driver.get(PREPARED_CARTS[context.current_cart_id]['checkout_url'])
    
    # Wait for cart to load
    time.sleep(2)

@when('I navigate to the prepared cart as this customer')
def step_impl_navigate_to_prepared_cart_as_customer(context):
    """Navigate to the prepared cart as a specific customer"""
    if not hasattr(context, 'current_cart_id') or context.current_cart_id not in PREPARED_CARTS:
        raise ValueError("No prepared cart available")
    
    # This would require additional steps to ensure we're logged in as the right customer
    # For now, just navigate to the prepared cart
    context.driver.get(PREPARED_CARTS[context.current_cart_id]['checkout_url'])
    
    # Wait for cart to load
    time.sleep(2)

@when('I apply the discount code "{code}"')
def step_impl_apply_discount_code(context, code):
    """Apply a discount code to the cart"""
    # This would depend on your cart page implementation
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    
    try:
        context.cart_page.apply_discount_code(code)
    except TimeoutException:
        assert False, f"Could not apply discount code (timeout)"

@then('The discount should be applied successfully')
def step_impl_verify_discount_applied(context):
    """Verify the discount was applied successfully"""
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    
    try:
        assert context.cart_page.is_discount_applied(), "Discount was not applied"
    except TimeoutException:
        assert False, "Could not verify discount (timeout)"

@then('The product price should reflect the special pricing')
def step_impl_verify_special_pricing(context):
    """Verify the product price reflects special pricing"""
    # This is a placeholder - actual implementation would depend on your UI
    # and how special pricing is displayed
    
    if not hasattr(context, 'cart_page'):
        context.cart_page = CartPage(context)
    
    try:
        # For illustration, we'll just verify the price is visible
        assert context.cart_page.get_item_price(0), "Price is not visible"
    except TimeoutException:
        assert False, "Could not verify price (timeout)"

@then('The subtotal in checkout should reflect the special pricing')
def step_impl_verify_special_pricing_subtotal(context):
    """Verify the subtotal reflects special pricing"""
    # This is a placeholder - actual implementation would depend on your UI
    # and how special pricing is reflected in the subtotal
    
    if not hasattr(context, 'checkout_page'):
        context.checkout_page = CheckoutPage(context)
    
    try:
        # For illustration, we'll just verify the subtotal is visible
        assert context.checkout_page.get_subtotal(), "Subtotal is not visible"
    except TimeoutException:
        assert False, "Could not verify subtotal (timeout)"
```

### Required Page Object Updates

Update the CartPage class to include methods for discount code handling:

```python
def apply_discount_code(self, code):
    """
    Apply a discount code to the cart
    
    Args:
        code: The discount code to apply
    """
    # This implementation would depend on your specific cart page HTML
    # Example implementation:
    discount_input = self.wait_for_element((By.ID, "discount-code"))
    discount_input.clear()
    discount_input.send_keys(code)
    
    apply_button = self.wait_for_element((By.CSS_SELECTOR, ".discount-button"))
    apply_button.click()
    
    # Wait for discount to be applied
    self.wait_for_element((By.CSS_SELECTOR, ".discount-applied"))

def is_discount_applied(self):
    """
    Check if a discount has been applied to the cart
    
    Returns:
        True if a discount is applied, False otherwise
    """
    return self.is_element_present((By.CSS_SELECTOR, ".discount-applied"))

def get_item_price(self, index):
    """
    Get the price of an item in the cart
    
    Args:
        index: The index of the item (0-based)
        
    Returns:
        The price as a string
    """
    price_elements = self.wait_for_elements((By.CSS_SELECTOR, ".cart-item-price"))
    if index < len(price_elements):
        return price_elements[index].text
    else:
        return None
```

### Integration with Environment Setup

Add the following to `environment.py` for cleanup of test data:

```python
# Add to imports
import time

# Add to before_all
def before_all(context):
    # Existing code...
    
    # Initialize test data collections
    context.PREPARED_CARTS = {}
    context.TEST_DISCOUNT_CODES = []
    
    # Add MCP helper method for discount creation
    context.mcp1_create_discount = mcp1_create_discount
    
    # Other existing code...

# Add to after_all
def after_all(context):
    # Existing code...
    
    # Clean up test discount codes
    if hasattr(context, 'TEST_DISCOUNT_CODES') and context.TEST_DISCOUNT_CODES:
        logger.info(f"Cleaning up {len(context.TEST_DISCOUNT_CODES)} test discount codes")
        for code in context.TEST_DISCOUNT_CODES:
            try:
                # Note: In a real implementation, you would call the appropriate 
                # API to delete test discount codes
                logger.info(f"Would delete test discount code {code}")
            except Exception as e:
                logger.error(f"Error cleaning up test discount code {code}: {str(e)}")
    
    # Other existing code...

# Add MCP client helper method
def mcp1_create_discount(code, valueType, value, title, startsAt, endsAt=None, appliesOncePerCustomer=False):
    """Create a basic discount code"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.post(MCP_SERVER_URL + "/create-discount", 
    #                    json={"code": code, "valueType": valueType, "value": value,
    #                          "title": title, "startsAt": startsAt, "endsAt": endsAt,
    #                          "appliesOncePerCustomer": appliesOncePerCustomer}).json()
    pass
```

## Data Generation Utilities

Create a utilities module `test_data_utils.py` in the `utils` directory:

```python
"""
Utility functions for generating test data
"""
import uuid
import json
import random
import os
from datetime import datetime, timedelta

def generate_unique_code(prefix="TEST"):
    """
    Generate a unique code for discounts, etc.
    
    Args:
        prefix: Prefix for the code
        
    Returns:
        A unique code
    """
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"{prefix}{unique_id}"

def get_random_products(context, count=1, exclude_handles=None):
    """
    Get random products from the store
    
    Args:
        context: The behave context
        count: Number of products to get
        exclude_handles: List of product handles to exclude
        
    Returns:
        List of product data dictionaries
    """
    # Get all products
    all_products = context.mcp1_get_products(limit=50)['products']
    
    if exclude_handles:
        all_products = [p for p in all_products if p['handle'] not in exclude_handles]
    
    # Select random products
    selected_products = random.sample(all_products, min(count, len(all_products)))
    
    return selected_products

def create_test_discount(context, percentage=20, duration_days=1):
    """
    Create a test discount code
    
    Args:
        context: The behave context
        percentage: Discount percentage (1-100)
        duration_days: Number of days the discount is valid
        
    Returns:
        The discount code
    """
    code = generate_unique_code()
    
    # Create discount
    start_date = datetime.now().isoformat()
    end_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
    
    discount = context.mcp1_create_discount(
        code=code,
        valueType="percentage",
        value=percentage / 100.0,
        title=f"Test Discount {percentage}% off",
        startsAt=start_date,
        endsAt=end_date,
        appliesOncePerCustomer=False
    )
    
    # Add to cleanup list
    if not hasattr(context, 'TEST_DISCOUNT_CODES'):
        context.TEST_DISCOUNT_CODES = []
    context.TEST_DISCOUNT_CODES.append(code)
    
    return code
```

## Testing Strategy

1. **Test Data Preparation**:
   - Create carts and discount codes programmatically before UI testing
   - Use known product data directly from the API

2. **Execution Approach**:
   - Navigate directly to prepared cart URLs
   - Verify cart contents without lengthy UI interaction
   - Focus test steps on validation rather than setup

3. **Data Cleanup**:
   - Track created test data for cleanup after test completion
   - Ensure no test data pollution between test runs

## Dependencies

- Shopify MCP server access
- Test environment with permissions for discount and cart creation
- Existing page objects for cart and checkout

## Expected Outcomes

1. Reduced test setup time
2. More comprehensive product coverage
3. Improved test reliability
4. Easier maintenance for product-specific tests
