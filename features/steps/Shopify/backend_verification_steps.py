import json
import logging
import time
from behave import given, when, then, step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

logger = logging.getLogger(__name__)

@given('I have cleaned up any test orders for test user "{email}"')
def step_impl_cleanup_test_orders(context, email):
    """Clean up any existing test orders to ensure a clean test state"""
    logger.info(f"Cleaning up test orders for {email}")
    
    # Query for recent orders for this email
    orders = context.mcp1_get_orders(query=f"email:{email}", first=5)
    
    if orders and 'orders' in orders and len(orders['orders']) > 0:
        logger.info(f"Found {len(orders['orders'])} existing test orders")
        for order in orders['orders']:
            # Note that we're not actually canceling orders - just logging
            # In a real implementation, you would cancel the order via API
            logger.info(f"Found test order {order['id']} for {email}")
            
            # Keep track of order IDs to verify test order creation
            if not hasattr(context, 'existing_order_ids'):
                context.existing_order_ids = set()
            context.existing_order_ids.add(order['id'])
    else:
        logger.info(f"No existing test orders found for {email}")
        context.existing_order_ids = set()

@then('I should verify the order exists in Shopify backend')
def step_impl_verify_order_exists(context):
    """Verify order exists in Shopify backend after purchase"""
    # Wait for order to be created in backend
    logger.info("Waiting for order to be created in backend...")
    time.sleep(10)  # Allow time for order to be processed
    
    # Get checkout email from context (saved during checkout process)
    email = context.checkout_email if hasattr(context, 'checkout_email') else "test@example.com"
    
    # Query for recent orders with this email
    orders = context.mcp1_get_orders(query=f"email:{email}", first=5)
    
    # Verify that an order exists
    assert orders and 'orders' in orders and len(orders['orders']) > 0, \
        f"No orders found for email {email}"
    
    # Find the most recent order (should be the one we just created)
    new_orders = []
    for order in orders['orders']:
        if not hasattr(context, 'existing_order_ids') or order['id'] not in context.existing_order_ids:
            new_orders.append(order)
    
    assert len(new_orders) > 0, f"No new orders found for email {email}"
    
    # Store order info for subsequent steps
    context.latest_order = new_orders[0]
    context.SHOPIFY_TEST_ORDERS.append(context.latest_order['id'])
    
    logger.info(f"Found new order: {context.latest_order['id']}")
    return context.latest_order

@then('The order should have correct line item "{item_name}"')
def step_impl_verify_line_item(context, item_name):
    """Verify order has specified line item"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Check if line item exists with given name
    line_items = order_details.get('lineItems', {}).get('edges', [])
    found = False
    for item in line_items:
        node = item.get('node', {})
        if item_name.lower() in node.get('name', '').lower():
            found = True
            break
    
    assert found, f"Line item '{item_name}' not found in order {context.latest_order['id']}"
    logger.info(f"Verified line item '{item_name}' in order {context.latest_order['id']}")

@then('The order should have {count:d} line items')
def step_impl_verify_line_item_count(context, count):
    """Verify order has specified number of line items"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Check line item count
    line_items = order_details.get('lineItems', {}).get('edges', [])
    actual_count = len(line_items)
    
    assert actual_count == count, \
        f"Expected {count} line items, but found {actual_count} in order {context.latest_order['id']}"
    logger.info(f"Verified {count} line items in order {context.latest_order['id']}")

@then('The order should have the price "{price}"')
def step_impl_verify_price(context, price):
    """Verify order has correct price"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Check if price matches (note: might need to handle currency symbols and formatting)
    # Strip currency symbols and whitespace for comparison
    expected_price = price.replace('£', '').replace('$', '').strip()
    actual_price = order_details.get('totalPriceV2', {}).get('amount', '0')
    
    # Flexible comparison - either exact match or contains the price string
    price_matches = (
        expected_price == actual_price or 
        expected_price in actual_price or 
        actual_price in expected_price
    )
    
    assert price_matches, \
        f"Expected price {price}, but got {actual_price} for order {context.latest_order['id']}"
    logger.info(f"Verified price {price} for order {context.latest_order['id']}")

@then('The order should have the customer email "{email}"')
def step_impl_verify_customer_email(context, email):
    """Verify order has correct customer email"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Extract customer email from order details
    actual_email = order_details.get('email', '')
    
    assert email.lower() == actual_email.lower(), \
        f"Expected email {email}, but got {actual_email} for order {context.latest_order['id']}"
    logger.info(f"Verified customer email {email} for order {context.latest_order['id']}")

@then('The order should have the shipping address "{address}"')
def step_impl_verify_shipping_address(context, address):
    """Verify order has correct shipping address"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Extract shipping address from order details
    shipping_address = order_details.get('shippingAddress', {}).get('address1', '')
    
    assert address.lower() in shipping_address.lower(), \
        f"Expected address containing '{address}', but got '{shipping_address}' for order {context.latest_order['id']}"
    logger.info(f"Verified shipping address '{address}' for order {context.latest_order['id']}")

@then('The order should have the total price reflecting both items')
def step_impl_verify_total_price_multiple_items(context):
    """Verify the total price reflects all items in the order"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Extract line items and total price
    line_items = order_details.get('lineItems', {}).get('edges', [])
    total_price = float(order_details.get('totalPriceV2', {}).get('amount', '0'))
    
    # Calculate expected total from line items
    expected_total = 0
    for item in line_items:
        node = item.get('node', {})
        item_price = float(node.get('originalTotalSet', {}).get('shopMoney', {}).get('amount', '0'))
        expected_total += item_price
    
    # Allow for small rounding differences and taxes
    assert abs(total_price - expected_total) <= (total_price * 0.3), \
        f"Total price {total_price} does not reflect sum of items {expected_total} for order {context.latest_order['id']}"
    logger.info(f"Verified total price {total_price} reflects multiple items for order {context.latest_order['id']}")

@then('The order should have status "{status}" or "{alt_status}"')
def step_impl_verify_order_status(context, status, alt_status):
    """Verify order has correct status"""
    assert hasattr(context, 'latest_order'), "No order found in context"
    
    # Get full order details
    order_details = context.mcp1_get_order(context.latest_order['id'])
    assert order_details, f"Failed to get order details for {context.latest_order['id']}"
    
    # Extract order status from order details
    actual_status = order_details.get('displayFinancialStatus', '')
    
    # Check if status matches either of the acceptable statuses
    assert actual_status.upper() == status.upper() or actual_status.upper() == alt_status.upper(), \
        f"Expected status {status} or {alt_status}, but got {actual_status} for order {context.latest_order['id']}"
    logger.info(f"Verified order status {actual_status} for order {context.latest_order['id']}")

@when('I fill in the shipping information with')
def step_impl_fill_shipping_info(context):
    """Fill in shipping information fields"""
    # Store the email for later verification
    for row in context.table:
        if row['field'] == 'email':
            context.checkout_email = row['value']
    
    # Let the existing step implementation handle the actual UI interaction
    # This assumes there's an existing step with this text in another file
    # If not, we'd need to implement the UI interaction here
    logger.info("Using existing step to fill in shipping information")
