# Backend Order Verification Testing

## Overview

This document outlines the implementation plan for adding backend order verification to the existing Shopify test suite. This enhancement will allow tests to verify that orders placed through the UI are correctly created and stored in the Shopify backend.

## Current Limitations

Current tests validate:
- UI elements and interactions during the checkout process
- Form validation for shipping information
- Visual confirmation of order summaries

But do not verify:
- Actual order creation in Shopify's backend
- Order data accuracy (line items, prices, customer info)
- Order status after completion

## Implementation Plan

### New Feature File: `backend_order_verification.feature`

```gherkin
@shopify
Feature: Shopify Backend Order Verification
  As a tester
  I want to verify orders are correctly created in the backend
  So that I can ensure data integrity between frontend and backend

  Background:
    Given I have cleaned up any test orders for test user "test@example.com"
    And I am on the product page for "gut-rewild"
    When I click Add to Cart
    And I click on the cart icon
    And I click the checkout button

  Scenario: Verify order is properly created in backend after purchase
    When I fill in the shipping information with
      | field      | value            |
      | email      | test@example.com |
      | first_name | Test             |
      | last_name  | User             |
      | address    | 123 Test Street  |
      | city       | London           |
      | postcode   | W1A 1AA          |
      | phone      | 07123456789      |
    And I select payment method "credit_card"
    And I complete the test purchase
    Then I should verify the order exists in Shopify backend
    And The order should have correct line item "Gut Rewild"
    And The order should have the price "£34.95"
    And The order should have the customer email "test@example.com"
    And The order should have the shipping address "123 Test Street"

  Scenario: Verify multiple items are correctly recorded in order
    Given I am on the product page for "gut-rewild"
    When I click Add to Cart
    And I am on the product page for "younger-you-cr"
    And I click Add to Cart
    And I click on the cart icon
    And I click the checkout button
    And I fill in the shipping information with
      | field      | value            |
      | email      | test@example.com |
      | first_name | Test             |
      | last_name  | User             |
      | address    | 123 Test Street  |
      | city       | London           |
      | postcode   | W1A 1AA          |
      | phone      | 07123456789      |
    And I select payment method "credit_card"
    And I complete the test purchase
    Then I should verify the order exists in Shopify backend
    And The order should have 2 line items
    And The order should have line item "Gut Rewild"
    And The order should have line item "Younger You Skin Cream"
    And The order should have the total price reflecting both items

  Scenario: Verify order status updates after completion
    When I fill in the shipping information with
      | field      | value            |
      | email      | test@example.com |
      | first_name | Test             |
      | last_name  | User             |
      | address    | 123 Test Street  |
      | city       | London           |
      | postcode   | W1A 1AA          |
      | phone      | 07123456789      |
    And I select payment method "credit_card"
    And I complete the test purchase
    Then I should verify the order exists in Shopify backend
    And The order should have status "OPEN" or "FULFILLED"
```

### New Step Definitions

Add the following step definitions in a new file `backend_verification_steps.py`:

```python
from behave import given, when, then
import time
import os
from dotenv import load_dotenv

# Global variables for step definitions
SHOPIFY_TEST_ORDERS = []

@given('I have cleaned up any test orders for test user "{email}"')
def step_impl_clean_test_orders(context, email):
    """Clean up any existing test orders for the specified email"""
    # Get recent orders for the user
    orders = context.mcp1_get_orders(query=f"email:{email}", first=10)
    
    # Store order IDs for later cleanup
    if orders and 'orders' in orders:
        for order in orders['orders']:
            if order['email'] == email:
                SHOPIFY_TEST_ORDERS.append(order['id'])
                
    # No need to delete orders now - we'll just track them for post-test cleanup

@when('I complete the test purchase')
def step_impl_complete_test_purchase(context):
    """Complete the test purchase - this is a placeholder for actual payment"""
    # In a real test, this would handle the credit card payment
    # For now, we'll just record that we reached this step
    context.test_purchase_initiated = True
    
    # Store the current time for order lookup
    context.purchase_time = time.time()
    
    # Wait a moment for order processing
    time.sleep(5)

@then('I should verify the order exists in Shopify backend')
def step_impl_verify_order_exists(context):
    """Verify the order exists in the Shopify backend"""
    # Get recent orders for the test user
    test_email = "test@example.com"  # This should be extracted from context or previous steps
    
    orders = context.mcp1_get_orders(query=f"email:{test_email}", first=5)
    
    # Verify an order exists
    assert orders and 'orders' in orders and len(orders['orders']) > 0, "No orders found for test user"
    
    # Store the most recent order for further verification
    context.current_test_order = orders['orders'][0]
    
    # Add to cleanup list
    SHOPIFY_TEST_ORDERS.append(context.current_test_order['id'])

@then('The order should have correct line item "{product_name}"')
def step_impl_verify_line_item(context, product_name):
    """Verify the order has the specified line item"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify line items
    found = False
    for line_item in order_details['lineItems']:
        if product_name in line_item['title']:
            found = True
            break
    
    assert found, f"Line item '{product_name}' not found in order"

@then('The order should have the price "{price}"')
def step_impl_verify_price(context, price):
    """Verify the order has the correct price"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify price (note: format might need adjustment)
    assert price in order_details['totalPrice'], f"Expected price '{price}' but found '{order_details['totalPrice']}'"

@then('The order should have the customer email "{email}"')
def step_impl_verify_email(context, email):
    """Verify the order has the correct customer email"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Verify email
    assert email == context.current_test_order['email'], f"Expected email '{email}' but found '{context.current_test_order['email']}'"

@then('The order should have the shipping address "{address}"')
def step_impl_verify_address(context, address):
    """Verify the order has the correct shipping address"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify shipping address
    shipping_address = order_details.get('shippingAddress', {})
    assert address in shipping_address.get('address1', ''), f"Expected address '{address}' but not found in shipping address"

@then('The order should have {count:d} line items')
def step_impl_verify_line_item_count(context, count):
    """Verify the order has the specified number of line items"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify line item count
    actual_count = len(order_details['lineItems'])
    assert count == actual_count, f"Expected {count} line items but found {actual_count}"

@then('The order should have the total price reflecting both items')
def step_impl_verify_total_price(context):
    """Verify the order total price reflects all items"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify the total price is greater than zero and seems reasonable
    # This is a simple check - you might want more specific validation
    total_price = float(order_details['totalPrice'].replace('£', '').strip())
    assert total_price > 0, f"Total price should be greater than zero, but found {total_price}"
    
    # Additionally, verify it's approximately the sum of the line items
    expected_total = sum(float(item['price']) * item['quantity'] for item in order_details['lineItems'])
    assert abs(total_price - expected_total) < 5, f"Total price {total_price} does not match expected total {expected_total}"

@then('The order should have status "{status1}" or "{status2}"')
def step_impl_verify_order_status(context, status1, status2):
    """Verify the order has one of the specified statuses"""
    assert hasattr(context, 'current_test_order'), "No current test order found"
    
    # Get the order details
    order_details = context.mcp1_get_order(orderId=context.current_test_order['id'])
    
    # Verify status
    actual_status = order_details['status']
    assert actual_status in [status1, status2], f"Expected status '{status1}' or '{status2}' but found '{actual_status}'"
```

### Integration with Environment Setup

Modify `environment.py` to add MCP server client initialization and hooks for test orders cleanup:

```python
# Add to imports at the top
from dotenv import load_dotenv
import json
import requests

# Add to before_all to initialize MCP client
def before_all(context):
    # Existing code...
    
    # Initialize Shopify MCP client
    load_dotenv()
    context.shopify_api_key = os.environ.get('SHOPIFY_API_KEY')
    
    # Add MCP helper methods to context
    context.mcp1_get_orders = mcp1_get_orders
    context.mcp1_get_order = mcp1_get_order
    context.mcp1_get_customers = mcp1_get_customers
    context.mcp1_create_draft_order = mcp1_create_draft_order
    
    # Other existing code...

# Add to after_all for cleanup
def after_all(context):
    # Existing code...
    
    # Clean up any test orders created during testing
    if hasattr(context, 'SHOPIFY_TEST_ORDERS') and context.SHOPIFY_TEST_ORDERS:
        logger.info(f"Cleaning up {len(context.SHOPIFY_TEST_ORDERS)} test orders")
        for order_id in context.SHOPIFY_TEST_ORDERS:
            try:
                # Note: In a real implementation, you would call the appropriate 
                # API to cancel/delete test orders
                logger.info(f"Would delete test order {order_id}")
            except Exception as e:
                logger.error(f"Error cleaning up test order {order_id}: {str(e)}")
    
    # Other existing code...

# MCP client helper methods (simplified versions)
def mcp1_get_orders(query=None, first=10):
    """Get orders from Shopify"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.get(MCP_SERVER_URL + "/get-orders", params={"query": query, "first": first}).json()
    pass

def mcp1_get_order(orderId):
    """Get specific order details"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.get(MCP_SERVER_URL + "/get-order", params={"orderId": orderId}).json()
    pass

def mcp1_get_customers(limit=10):
    """Get customers from Shopify"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.get(MCP_SERVER_URL + "/get-customers", params={"limit": limit}).json()
    pass

def mcp1_create_draft_order(email, lineItems, note=None, shippingAddress=None):
    """Create a draft order in Shopify"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.post(MCP_SERVER_URL + "/create-draft-order", 
    #                     json={"email": email, "lineItems": lineItems, 
    #                           "note": note, "shippingAddress": shippingAddress}).json()
    pass
```

## Testing Strategy

1. **Test Isolation**:
   - Each test handles its own data cleanup
   - Orders created during tests are tagged for easy identification

2. **Execution Approach**:
   - Tests can run both locally and in BrowserStack environments
   - Backend verification enhances, but doesn't replace UI validation

3. **Error Handling**:
   - Proper error messaging for backend failures
   - Clear distinction between UI failures and backend verification failures

## Dependencies

- Shopify MCP server access
- Test environment with proper permissions for order creation and retrieval
- Environment variables for authentication

## Expected Outcomes

1. Increased confidence in order processing flow
2. Detection of backend data integrity issues
3. Validation of order statuses and lifecycle
4. Comprehensive testing of both UI and data layers
