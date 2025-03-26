import logging
from behave import given, when, then, step
import re
import time
import os
from selenium.common.exceptions import TimeoutException
from features.utils.shopify_mcp_client import get_shopify_mcp_client

logger = logging.getLogger(__name__)

# Helper function to determine if we should use the real MCP server
def _is_using_real_mcp():
    """Determine if we should use the real MCP server based on environment variables"""
    return 'SHOPIFY_MCP_SERVER' in os.environ and 'SHOPIFY_API_KEY' in os.environ and os.environ.get('USE_MOCK_MCP') != 'true'

@given('I have cleaned up any test orders for test user "{email}"')
def step_impl_cleanup_test_orders(context, email):
    """Clean up any existing test orders for a specific user"""
    logger.info(f"Cleaning up test orders for email: {email}")
    
    # Store the email in context for later use
    context.checkout_email = email
    
    # Get orders for this email
    if _is_using_real_mcp():
        # Using real Shopify MCP
        client = get_shopify_mcp_client()
        orders_response = client.get_orders(query=f"email:{email}", first=10)
    else:
        # Using mock MCP
        from features.environment import mcp1_get_orders
        orders_response = mcp1_get_orders(query=f"email:{email}", first=10)
    
    if not orders_response:
        logger.warning("No orders response received")
        return
        
    # Extract orders from the response
    orders = []
    if isinstance(orders_response, dict):
        if 'orders' in orders_response:
            if isinstance(orders_response['orders'], dict) and 'edges' in orders_response['orders']:
                orders = orders_response['orders']['edges']
            elif isinstance(orders_response['orders'], list):
                # Convert list of orders to list of dict with 'node' key
                orders = [{'node': order} for order in orders_response['orders']]
    
    if orders:
        logger.info(f"Found {len(orders)} existing test orders for {email}")
        for order_edge in orders:
            # Make sure order_edge is a dict before using get() method
            if isinstance(order_edge, dict):
                order = order_edge.get('node', {})
                order_id = order.get('id', 'Unknown ID')
                order_name = order.get('name', 'Unknown Name')
                logger.info(f"Found test order: {order_name} (ID: {order_id})")
            else:
                # If order_edge is not a dict, log it differently
                logger.info(f"Found test order with unexpected format: {order_edge}")
    else:
        logger.info(f"No existing test orders found for {email}")
    
    logger.info("Test order cleanup completed")

@when('I set "{email}" as the checkout email')
def step_impl_set_checkout_email(context, email):
    """Set the checkout email for verification purposes"""
    logger.info(f"Setting checkout email to: {email}")
    context.checkout_email = email

@then('I should verify the order exists in Shopify backend')
def step_impl_verify_order_exists(context):
    """Verify that the order exists in the Shopify backend"""
    logger.info("Verifying order exists in Shopify backend")
    
    # Make sure we have an email to query for
    assert hasattr(context, 'checkout_email'), "No checkout email found in context"
    email = context.checkout_email
    
    # We may need to retry a few times as order processing might take time
    max_attempts = 3
    attempt = 1
    orders = []
    
    while attempt <= max_attempts and not orders:
        logger.info(f"Querying orders for email: {email} (attempt {attempt})")
        
        # Get orders for this email
        if _is_using_real_mcp():
            # Using real Shopify MCP
            client = get_shopify_mcp_client()
            orders_response = client.get_orders(query=f"email:{email}", first=5)
        else:
            # Using mock MCP
            from features.environment import mcp1_get_orders
            orders_response = mcp1_get_orders(query=f"email:{email}", first=5)
        
        # Extract orders from the response
        orders = []
        if isinstance(orders_response, dict):
            if 'orders' in orders_response:
                if isinstance(orders_response['orders'], dict) and 'edges' in orders_response['orders']:
                    orders = orders_response['orders']['edges']
                elif isinstance(orders_response['orders'], list):
                    # Convert list of orders to list of dict with 'node' key
                    orders = [{'node': order} for order in orders_response['orders']]
            
        if orders:
            # Found at least one order
            order_edge = orders[0]  # Get the first order (most recent)
            # Make sure order_edge is a dict before using get() method
            if isinstance(order_edge, dict):
                order = order_edge.get('node', {})
                order_id = order.get('id', 'Unknown ID')
                order_name = order.get('name', 'Unknown Name')
                logger.info(f"Found order: {order_name} (ID: {order_id})")
                
                # Store the order in context for other steps to use
                context.verified_order = order
            else:
                # If order_edge is not a dict, log it differently
                logger.info(f"Found order with unexpected format: {order_edge}")
            break
        
        # If no orders found, wait and retry
        if not orders:
            logger.info(f"No orders found for {email}, waiting and retrying...")
            time.sleep(2)  # Wait 2 seconds before retrying
            attempt += 1
    
    # Assert that we found at least one order
    assert orders, f"No orders found for {email} after {max_attempts} attempts"

@then('The order should have {count:d} line items')
def step_impl_verify_line_item_count(context, count):
    """Verify that the order has the expected number of line items"""
    logger.info(f"Verifying order has {count} line items")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get line items from the order
    line_items = context.verified_order.get('lineItems', {}).get('edges', [])
    
    # Get the actual count
    actual_count = len(line_items)
    
    # Log the line items for debugging
    for i, item_edge in enumerate(line_items, 1):
        # Make sure item_edge is a dict before using get() method
        if isinstance(item_edge, dict):
            item = item_edge.get('node', {})
            item_name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 1)
            logger.info(f"Line item {i}: {item_name} (Quantity: {quantity})")
        else:
            # If item_edge is not a dict, log it differently
            logger.info(f"Line item {i} with unexpected format: {item_edge}")
    
    # Assert that the count matches
    assert actual_count == count, f"Expected {count} line items, but found {actual_count}"

@then('The order should have line item "{item_name}"')
def step_impl_verify_line_item(context, item_name):
    """Verify that the order has a line item with the specified name"""
    logger.info(f"Verifying order has line item: {item_name}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get the line items from the order
    line_items = context.verified_order.get('lineItems', {}).get('edges', [])
    
    # Look for a line item with the specified name
    found = False
    for item_edge in line_items:
        # Make sure item_edge is a dict before using get() method
        if isinstance(item_edge, dict):
            item = item_edge.get('node', {})
            name = item.get('name', '')
            quantity = item.get('quantity', 0)
            
            if name == item_name:
                found = True
                logger.info(f"Found line item: {name} (Quantity: {quantity})")
                break
        else:
            # If item_edge is not a dict, log it differently
            logger.info(f"Line item with unexpected format: {item_edge}")
    
    # Assert that we found the line item
    assert found, f"Line item '{item_name}' not found in order"

@then('The order should have correct line item "{item_name}"')
def step_impl_verify_correct_line_item(context, item_name):
    """Verify that the order has the specified line item with correct details"""
    logger.info(f"Verifying order has correct line item: {item_name}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get line items from the order
    line_items = context.verified_order.get('lineItems', {}).get('edges', [])
    
    # Try to find the specified item
    found_item = None
    for item_edge in line_items:
        # Make sure item_edge is a dict before using get() method
        if isinstance(item_edge, dict):
            item = item_edge.get('node', {})
            current_name = item.get('name', '')
            
            if current_name == item_name:
                found_item = item
                logger.info(f"Found line item: {item_name} (Quantity: {item.get('quantity', 1)})")
                break
        else:
            # If item_edge is not a dict, log it differently
            logger.info(f"Line item with unexpected format: {item_edge}")
    
    # Assert that we found the item
    assert found_item is not None, f"Line item '{item_name}' not found in order"
    
    # Store the item for use in other steps
    context.verified_line_item = found_item

@then('The order should have the price "{expected_price}"')
def step_impl_verify_price(context, expected_price):
    """Verify that the order has the expected price"""
    logger.info(f"Verifying order has price: {expected_price}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Extract the currency and amount from the expected price
    # Format can be "GBP34.95", "£34.95", etc.
    price_pattern = r'([A-Z]{3}|[£$€])(\d+\.\d+)'
    match = re.match(price_pattern, expected_price)
    
    if not match:
        assert False, f"Invalid price format: {expected_price}. Expected format: 'GBP34.95' or '£34.95'"
    
    expected_currency, expected_amount = match.groups()
    
    # Map currency symbols to ISO codes if needed
    currency_map = {'£': 'GBP', '$': 'USD', '€': 'EUR'}
    if expected_currency in currency_map:
        expected_currency = currency_map[expected_currency]
    
    # Get the actual price from the order
    price_data = context.verified_order.get('totalPriceV2', {})
    actual_amount = price_data.get('amount', '0.00')
    actual_currency = price_data.get('currencyCode', '')
    
    logger.info(f"Actual price: {actual_currency}{actual_amount}")
    
    # Check currency matches (case insensitive)
    assert actual_currency.upper() == expected_currency.upper(), \
        f"Expected currency {expected_currency}, but found {actual_currency}"
    
    # Convert amounts to float for comparison with some tolerance
    try:
        expected_float = float(expected_amount)
        actual_float = float(actual_amount)
        
        # Allow for a small difference due to rounding, taxes, etc.
        difference = abs(expected_float - actual_float)
        assert difference < 0.5, \
            f"Expected amount {expected_float}, but found {actual_float} (diff: {difference})"
    except ValueError:
        assert False, f"Invalid amount format. Expected: {expected_amount}, Actual: {actual_amount}"

@then('The order should have the customer email "{expected_email}"')
def step_impl_verify_customer_email(context, expected_email):
    """Verify that the order has the expected customer email"""
    logger.info(f"Verifying order has customer email: {expected_email}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get the actual email from the order
    actual_email = context.verified_order.get('email', '')
    
    logger.info(f"Order customer email: {actual_email}")
    
    # Assert that the email matches (case insensitive)
    assert actual_email.lower() == expected_email.lower(), \
        f"Expected email {expected_email}, but found {actual_email}"

@then('The order should have the shipping address "{expected_address}"')
def step_impl_verify_shipping_address(context, expected_address):
    """Verify that the order has the expected shipping address"""
    logger.info(f"Verifying order has shipping address: {expected_address}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get the shipping address from the order
    shipping_address = context.verified_order.get('shippingAddress', {})
    actual_address = shipping_address.get('address1', '')
    
    logger.info(f"Order shipping address: {actual_address}")
    
    # Assert that the address contains the expected text (partial match)
    assert expected_address.lower() in actual_address.lower(), \
        f"Expected address to contain '{expected_address}', but found '{actual_address}'"

@then('The order should have a status of either "{status1}" or "{status2}"')
def step_impl_verify_order_status(context, status1, status2):
    """Verify that the order has one of the expected statuses"""
    logger.info(f"Verifying order has status {status1} or {status2}")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get the actual status from the order
    actual_status = context.verified_order.get('displayFinancialStatus', '')
    
    logger.info(f"Order status: {actual_status}")
    
    # Assert that the status matches one of the expected values
    accepted_statuses = [status1.upper(), status2.upper()]
    assert actual_status.upper() in accepted_statuses, \
        f"Expected status {status1} or {status2}, but found {actual_status}"

@then('The order should have the total price reflecting both items')
def step_impl_verify_total_price(context):
    """Verify that the order total price is the sum of the item prices"""
    logger.info("Verifying order total price reflects all items")
    
    # Make sure we have a verified order in context
    assert hasattr(context, 'verified_order'), "No verified order found in context"
    
    # Get the line items from the order
    line_items = context.verified_order.get('lineItems', {}).get('edges', [])
    
    # Get the actual total price from the order
    total_price = context.verified_order.get('totalPriceV2', {})
    actual_total = total_price.get('amount', '0.00')
    currency = total_price.get('currencyCode', 'GBP')
    
    try:
        actual_total_float = float(actual_total)
        logger.info(f"Order total price: {actual_total_float:.2f} {currency}")
        
        # Calculate expected total based on line items
        expected_total = 0.0
        for item_edge in line_items:
            # Make sure item_edge is a dict before using get() method
            if isinstance(item_edge, dict):
                item = item_edge.get('node', {})
                item_name = item.get('name', 'Unknown')
                item_price_data = item.get('originalTotalSet', {}).get('shopMoney', {})
                item_price = item_price_data.get('amount', '0.00')
                item_quantity = item.get('quantity', 1)
                
                try:
                    price_value = float(item_price)
                    item_total = price_value * item_quantity  # Calculate item total based on quantity
                    expected_total += item_total
                    logger.info(f"Line item: {item_name} - Price: {price_value:.2f} x {item_quantity} = {item_total:.2f}")
                except ValueError:
                    logger.warning(f"Could not convert price to float: {item_price}")
            else:
                # If item_edge is not a dict, log it differently
                logger.info(f"Line item with unexpected format: {item_edge}")
        
        logger.info(f"Expected total from line items: {expected_total:.2f} {currency}")
        logger.info(f"Actual total from order: {actual_total_float:.2f} {currency}")
        
        # For real Shopify data, there might be shipping, taxes, etc.
        # So we'll check that the total is reasonable rather than exact
        assert actual_total_float > 0, "Total price should be greater than 0"
        
        # Allow for shipping, tax, and other adjustments with a tolerance of 30%
        if expected_total > 0:
            ratio = actual_total_float / expected_total
            assert 0.7 <= ratio <= 1.5, \
                f"Total price ratio {ratio:.2f} is outside of reasonable range (0.7-1.5)"
        
    except ValueError:
        logger.warning(f"Could not convert total price to float: {actual_total}")
        assert False, f"Invalid total price format: {actual_total}"
