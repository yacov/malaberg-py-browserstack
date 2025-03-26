"""
Mock MCP Server for testing backend integration without requiring a real Shopify store.
This provides dummy responses for MCP API calls to facilitate development and testing.
"""

import json
import os
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class MockMCPServer:
    """Mocks the MCP server responses for testing purposes"""
    
    def __init__(self):
        self.orders = self._load_mock_orders()
        self.customers = self._load_mock_customers()
        self.products = self._load_mock_products()
        self.draft_orders = []
        self.discounts = []
        
    def _load_mock_orders(self):
        """Load mock order data"""
        return [
            {
                "id": "1234567890123",
                "name": "#1001",
                "email": "test@example.com",
                "displayFinancialStatus": "OPEN",
                "totalPriceV2": {"amount": "69.90", "currencyCode": "GBP"},
                "shippingAddress": {
                    "address1": "123 Test Street",
                    "city": "London",
                    "zip": "W1A 1AA",
                    "country": "United Kingdom",
                    "name": "Test User"
                },
                "lineItems": {
                    "edges": [
                        {
                            "node": {
                                "name": "Gut Rewild",
                                "quantity": 1,
                                "originalTotalSet": {
                                    "shopMoney": {"amount": "69.90", "currencyCode": "GBP"}
                                }
                            }
                        }
                    ]
                }
            },
            {
                "id": "2345678901234",
                "name": "#1002",
                "email": "another@example.com",
                "displayFinancialStatus": "FULFILLED",
                "totalPriceV2": {"amount": "209.70", "currencyCode": "GBP"},
                "shippingAddress": {
                    "address1": "456 Another Street",
                    "city": "Manchester",
                    "zip": "M1 1AA",
                    "country": "United Kingdom",
                    "name": "Another User"
                },
                "lineItems": {
                    "edges": [
                        {
                            "node": {
                                "name": "Gut Rewild",
                                "quantity": 2,
                                "originalTotalSet": {
                                    "shopMoney": {"amount": "69.90", "currencyCode": "GBP"}
                                }
                            }
                        },
                        {
                            "node": {
                                "name": "Younger You Skin Cream",
                                "quantity": 1,
                                "originalTotalSet": {
                                    "shopMoney": {"amount": "69.90", "currencyCode": "GBP"}
                                }
                            }
                        }
                    ]
                }
            },
            {
                "id": "3456789012345",
                "name": "#1003",
                "email": "2a5f9d12@malaberg.com",
                "displayFinancialStatus": "OPEN",
                "totalPriceV2": {"amount": "69.90", "currencyCode": "GBP"},
                "shippingAddress": {
                    "address1": "789 Test Avenue",
                    "city": "Birmingham",
                    "zip": "B1 1AA",
                    "country": "United Kingdom",
                    "name": "Test Malaberg"
                },
                "lineItems": {
                    "edges": [
                        {
                            "node": {
                                "name": "Gut Rewild",
                                "quantity": 1,
                                "originalTotalSet": {
                                    "shopMoney": {"amount": "69.90", "currencyCode": "GBP"}
                                }
                            }
                        }
                    ]
                }
            }
        ]
    
    def _load_mock_customers(self):
        """Load mock customer data"""
        # Use the existing test users based on our memories
        return [
            {
                "id": "23113161474425",
                "email": "2a5f9d12@malaberg.com",
                "firstName": "Test",
                "lastName": "User",
                "tags": []
            },
            {
                "id": "23113161507193",
                "email": "3bc45e23@malaberg.com",
                "firstName": "John",
                "lastName": "Doe",
                "tags": []
            },
            {
                "id": "23113161539961",
                "email": "4df56f34@malaberg.com",
                "firstName": "Jane",
                "lastName": "Smith",
                "tags": []
            }
        ]
    
    def _load_mock_products(self):
        """Load mock product data"""
        return [
            {
                "id": "gid://shopify/Product/12345",
                "title": "Gut Rewild",
                "description": "Support digestive health",
                "totalInventory": 100,
                "priceRange": {
                    "minVariantPrice": {"amount": "69.90", "currencyCode": "GBP"},
                    "maxVariantPrice": {"amount": "69.90", "currencyCode": "GBP"}
                },
                "variants": {
                    "edges": [
                        {
                            "node": {
                                "id": "gid://shopify/ProductVariant/98765",
                                "price": "69.90"
                            }
                        }
                    ]
                }
            },
            {
                "id": "gid://shopify/Product/67890",
                "title": "Younger You Skin Cream",
                "description": "Anti-aging skin cream",
                "totalInventory": 50,
                "priceRange": {
                    "minVariantPrice": {"amount": "69.90", "currencyCode": "GBP"},
                    "maxVariantPrice": {"amount": "69.90", "currencyCode": "GBP"}
                },
                "variants": {
                    "edges": [
                        {
                            "node": {
                                "id": "gid://shopify/ProductVariant/54321",
                                "price": "69.90"
                            }
                        }
                    ]
                }
            }
        ]
    
    def get_orders(self, query=None, first=10, **kwargs):
        """Mock implementation of get-orders API"""
        logger.info(f"Mock: Getting orders with query: {query}, first: {first}")
        
        orders = self.orders
        filtered_orders = []
        
        # Apply email filter if present
        if query and 'email:' in query:
            email = query.split('email:')[1].strip()
            filtered_orders = [order for order in orders if order.get('email') == email]
        else:
            filtered_orders = orders[:first]  # Just return the first N orders
        
        # Format the response like the real Shopify API
        edges = []
        for order in filtered_orders:
            edges.append({"node": order})
        
        return {
            "orders": {
                "pageInfo": {
                    "hasNextPage": False,
                    "hasPreviousPage": False
                },
                "edges": edges
            }
        }
    
    def get_order(self, orderId):
        """Mock implementation of get-order API"""
        logger.info(f"Mock: Getting order details for order ID: {orderId}")
        
        for order in self.orders:
            if order["id"] == orderId:
                return order
                
        return {}
    
    def get_customers(self, limit=10, next=None):
        """Mock implementation of get-customers API"""
        logger.info(f"Mock: Getting customers with limit: {limit}")
        
        result = self.customers[:limit]
        
        return {"customers": result}
    
    def create_draft_order(self, email, lineItems, note=None, shippingAddress=None):
        """Mock implementation of create-draft-order API"""
        logger.info(f"Mock: Creating draft order for email: {email} with {len(lineItems)} items")
        
        # Generate a new order ID
        order_id = str(uuid.uuid4()).replace("-", "")[:13]
        
        # Create a draft order
        draft_order = {
            "id": order_id,
            "name": f"#D{len(self.draft_orders) + 1001}",
            "email": email,
            "displayFinancialStatus": "PENDING",
            "totalPriceV2": {"amount": "0.00", "currencyCode": "GBP"},
            "shippingAddress": shippingAddress or {},
            "lineItems": {
                "edges": []
            }
        }
        
        # Add line items and calculate total
        total_price = 0.0
        for item in lineItems:
            variant_id = item.get("variantId")
            quantity = item.get("quantity", 1)
            
            # Find product variant
            product_variant = None
            for product in self.products:
                for variant_edge in product["variants"]["edges"]:
                    variant = variant_edge["node"]
                    if variant["id"] == variant_id:
                        product_variant = {
                            "product": product,
                            "variant": variant
                        }
                        break
                if product_variant:
                    break
            
            if product_variant:
                price = float(product_variant["variant"]["price"]) * quantity
                total_price += price
                
                draft_order["lineItems"]["edges"].append({
                    "node": {
                        "name": product_variant["product"]["title"],
                        "quantity": quantity,
                        "originalTotalSet": {
                            "shopMoney": {"amount": str(price), "currencyCode": "GBP"}
                        }
                    }
                })
        
        # Update total price
        draft_order["totalPriceV2"]["amount"] = str(total_price)
        
        # Add to draft orders
        self.draft_orders.append(draft_order)
        
        return {"draftOrder": draft_order}
    
    def complete_draft_order(self, draftOrderId, variantId):
        """Mock implementation of complete-draft-order API"""
        logger.info(f"Mock: Completing draft order: {draftOrderId}")
        
        # Find draft order
        for draft_order in self.draft_orders:
            if draft_order["id"] == draftOrderId:
                # Mark as completed
                draft_order["displayFinancialStatus"] = "OPEN"
                
                # Add to orders
                self.orders.append(draft_order)
                
                return {"order": draft_order}
                
        return {}
    
    def tag_customer(self, customerId, tags):
        """Mock implementation of tag-customer API"""
        logger.info(f"Mock: Adding tags to customer {customerId}: {tags}")
        
        # Find customer
        for customer in self.customers:
            if customer["id"] == customerId:
                # Add tags
                customer["tags"] = list(set(customer.get("tags", []) + tags))
                
                return {"customer": customer}
                
        return {}
    
    def get_products(self, limit=10, searchTitle=None):
        """Mock implementation of get-products API"""
        logger.info(f"Mock: Getting products with limit: {limit}, searchTitle: {searchTitle}")
        
        filtered_products = self.products.copy()
        
        # Filter by title if provided
        if searchTitle:
            filtered_products = [
                product for product in filtered_products 
                if searchTitle.lower() in product["title"].lower()
            ]
        
        # Take only the first N products
        result = filtered_products[:limit]
        
        return {"products": result}
    
    def create_discount(self, code, valueType, value, title, startsAt, endsAt=None, appliesOncePerCustomer=False):
        """Mock implementation of create-discount API"""
        logger.info(f"Mock: Creating discount code: {code}, value: {value}, type: {valueType}")
        
        # Create a discount
        discount = {
            "id": str(uuid.uuid4()),
            "code": code,
            "valueType": valueType,
            "value": value,
            "title": title,
            "startsAt": startsAt,
            "endsAt": endsAt,
            "appliesOncePerCustomer": appliesOncePerCustomer
        }
        
        # Add to discounts
        self.discounts.append(discount)
        
        return {"discount": discount}


# Create singleton instance
mock_mcp_server = MockMCPServer()

# Wrapper functions to match the actual MCP client interface
def mcp1_get_orders(query=None, first=10, **kwargs):
    """Get orders from mock Shopify"""
    logger.info(f"Mock: Getting orders with query: {query}, first: {first}")
    
    orders = mock_mcp_server.orders
    filtered_orders = []
    
    # Apply email filter if present
    if query and 'email:' in query:
        email = query.split('email:')[1].strip()
        filtered_orders = [order for order in orders if order.get('email') == email]
    else:
        filtered_orders = orders[:first]  # Just return the first N orders
    
    # Format the response like the real Shopify API
    edges = []
    for order in filtered_orders:
        edges.append({"node": order})
    
    return {
        "orders": {
            "pageInfo": {
                "hasNextPage": False,
                "hasPreviousPage": False
            },
            "edges": edges
        }
    }

def mcp1_get_order(orderId):
    """Get order from mock Shopify"""
    return mock_mcp_server.get_order(orderId)

def mcp1_get_customers(limit=10, next=None):
    """Get customers from mock Shopify"""
    return mock_mcp_server.get_customers(limit, next)

def mcp1_create_draft_order(email, lineItems, note=None, shippingAddress=None):
    """Create draft order in mock Shopify"""
    return mock_mcp_server.create_draft_order(email, lineItems, note, shippingAddress)

def mcp1_complete_draft_order(draftOrderId, variantId):
    """Complete draft order in mock Shopify"""
    return mock_mcp_server.complete_draft_order(draftOrderId, variantId)

def mcp1_tag_customer(customerId, tags):
    """Tag customer in mock Shopify"""
    return mock_mcp_server.tag_customer(customerId, tags)

def mcp1_get_products(limit=10, searchTitle=None):
    """Get products from mock Shopify"""
    return mock_mcp_server.get_products(limit, searchTitle)

def mcp1_create_discount(code, valueType, value, title, startsAt, endsAt=None, appliesOncePerCustomer=False):
    """Create discount in mock Shopify"""
    return mock_mcp_server.create_discount(code, valueType, value, title, startsAt, endsAt, appliesOncePerCustomer)
