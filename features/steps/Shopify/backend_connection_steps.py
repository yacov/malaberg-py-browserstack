import logging
from behave import given, when, then
import os
import time

logger = logging.getLogger(__name__)

@given('I have a backend connection to Shopify')
def step_impl_check_backend_connection(context):
    """Verify backend connection to Shopify MCP server"""
    logger.info("Checking connection to Shopify MCP server")
    
    # Check if required environment variables are set
    if context.use_mock_mcp:
        logger.info("Using mock MCP server for testing")
    else:
        assert os.environ.get('SHOPIFY_MCP_SERVER') or context.shopify_mcp_server, \
            "SHOPIFY_MCP_SERVER environment variable or context.shopify_mcp_server not set"
    
    # Log the MCP server URL being used
    mcp_server = os.environ.get('SHOPIFY_MCP_SERVER', context.shopify_mcp_server)
    logger.info(f"Using Shopify MCP server: {mcp_server}")
    
    # For testing purposes, we'll just consider the connection successful
    # if the environment variables are properly set
    context.mcp_connection_successful = True

@when('I query for products')
def step_impl_query_products(context):
    """Query for products from the Shopify backend"""
    assert context.mcp_connection_successful, "Backend connection not established"
    
    try:
        # Try to get products from Shopify
        logger.info("Querying for products from Shopify backend")
        
        # Call the MCP client method to get products
        products_response = context.mcp1_get_products(limit=5)
        
        # Store the response in context for the next step
        context.products_response = products_response
        
        # Log product count for debugging
        if 'products' in products_response:
            product_count = len(products_response['products'])
            logger.info(f"Retrieved {product_count} products from Shopify backend")
        else:
            logger.warning("No products data found in response")
            
    except Exception as e:
        logger.error(f"Error querying products: {str(e)}")
        raise

@then('I should receive product data from the backend')
def step_impl_verify_product_data(context):
    """Verify product data was received from the backend"""
    assert hasattr(context, 'products_response'), "No product response found in context"
    
    # Verify that the products data exists and is non-empty
    assert 'products' in context.products_response, "No products data in response"
    assert len(context.products_response['products']) > 0, "No products found in response"
    
    # Log a few product details for verification
    for i, product in enumerate(context.products_response['products'][:3]):
        logger.info(f"Product {i+1}: {product.get('title')}, ID: {product.get('id')}")
        
    logger.info("Successfully verified product data from Shopify backend")
