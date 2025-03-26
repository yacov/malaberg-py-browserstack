"""
Shopify MCP Client for interacting with the Shopify store backend.
Provides methods to retrieve and manage orders, products, and customer data.
"""

import os
import requests
import logging
import json
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ShopifyMCPClient:
    """Client for interacting with the Shopify MCP server"""
    
    def __init__(self, base_url=None):
        """
        Initialize the Shopify MCP client
        :param base_url: Base URL for the MCP server, defaults to environment variable
        """
        self.base_url = base_url or os.environ.get('SHOPIFY_MCP_SERVER')
        if not self.base_url:
            raise ValueError("SHOPIFY_MCP_SERVER environment variable or base_url must be set")
        
        # Ensure the URL ends with a slash
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        logger.info(f"Initialized Shopify MCP client with base URL: {self.base_url}")
    
    def _call_api(self, endpoint, method='GET', params=None, data=None):
        """
        Make an API call to the MCP server
        :param endpoint: API endpoint to call
        :param method: HTTP method (GET, POST, etc.)
        :param params: Query parameters
        :param data: Request body data
        :return: Response data as JSON
        """
        url = urljoin(self.base_url, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            logger.debug(f"Making {method} request to {url}")
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, params=params, json=data, headers=headers)
            else:
                logger.error(f"Unsupported method: {method}")
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API call to {url} failed: {str(e)}")
            raise
    
    def get_orders(self, query=None, first=10, **kwargs):
        """
        Get orders from Shopify
        :param query: Query string to filter orders (e.g., 'email:test@example.com')
        :param first: Number of orders to return
        :return: List of orders
        """
        logger.info(f"Getting orders with query: {query}, first: {first}")
        params = {
            'query': query,
            'first': first
        }
        # Add any additional kwargs as params
        params.update(kwargs)
        
        return self._call_api('mcp1_get-orders', params=params)
    
    def get_order(self, order_id):
        """
        Get a specific order by ID
        :param order_id: Order ID to retrieve
        :return: Order details
        """
        logger.info(f"Getting order with ID: {order_id}")
        params = {
            'orderId': order_id
        }
        
        return self._call_api('mcp1_get-order', params=params)
    
    def get_customers(self, limit=10, next_cursor=None):
        """
        Get customers from Shopify
        :param limit: Number of customers to return
        :param next_cursor: Cursor for pagination
        :return: List of customers
        """
        logger.info(f"Getting customers with limit: {limit}, next: {next_cursor}")
        params = {
            'limit': limit
        }
        
        if next_cursor:
            params['next'] = next_cursor
            
        return self._call_api('mcp1_get-customers', params=params)
    
    def get_products(self, limit=10, search_title=None):
        """
        Get products from Shopify
        :param limit: Number of products to return
        :param search_title: Filter products by title
        :return: List of products
        """
        logger.info(f"Getting products with limit: {limit}, search: {search_title}")
        params = {
            'limit': limit
        }
        
        if search_title:
            params['searchTitle'] = search_title
            
        return self._call_api('mcp1_get-products', params=params)
    
    # Add other methods as needed for your implementation

# Create a singleton instance for easy access
shopify_mcp_client = None

def get_shopify_mcp_client(base_url=None):
    """
    Get or create a singleton instance of the Shopify MCP client
    :param base_url: Optional base URL
    :return: ShopifyMCPClient instance
    """
    global shopify_mcp_client