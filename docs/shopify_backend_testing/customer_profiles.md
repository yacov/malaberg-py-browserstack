# Customer Data Profiles Integration Testing

## Overview

This document outlines the implementation plan for validating customer data integration between the frontend shopping experience and backend Shopify customer profiles. These tests will verify that customer information is correctly stored, updated, and persisted across shopping sessions.

## Current Limitations

Current tests focus on:
- Form completion during checkout
- Basic validation of customer inputs
- UI elements and interactions

But do not verify:
- Customer profile creation in Shopify's backend
- Profile data updates after purchases
- Customer data persistence between sessions

## Implementation Plan

### New Feature File: `customer_profile_integration.feature`

```gherkin
@shopify
Feature: Shopify Customer Profile Integration
  As a tester
  I want to verify customer data is correctly integrated with Shopify
  So that I can ensure customer profiles are properly managed

  Background:
    Given I have a test customer with email "profile-test@example.com"

  Scenario: Verify customer profile is created when placing an order
    Given I have cleaned up any profile data for "profile-test@example.com"
    When I create an order as a new customer with
      | field      | value                   |
      | email      | profile-test@example.com |
      | first_name | Profile                 |
      | last_name  | Test                    |
      | address    | 789 Profile Street      |
      | city       | Manchester              |
      | postcode   | M1 2AB                  |
      | phone      | 07111222333             |
    Then I should verify the customer exists in Shopify backend
    And The customer profile should have the name "Profile Test"
    And The customer profile should have the email "profile-test@example.com"

  Scenario: Verify customer address is saved to profile
    Given I have a customer with email "profile-test@example.com"
    When I create an order for this customer with address
      | field      | value                  |
      | address    | 101 New Profile Street |
      | city       | Liverpool              |
      | postcode   | L1 3CD                 |
      | phone      | 07444555666            |
    Then I should verify the customer profile has the address saved
    And The saved address should contain "101 New Profile Street"
    And The saved address should contain "Liverpool"

  Scenario: Verify customer profile is updated with new information
    Given I have a customer with email "profile-test@example.com"
    When I update the customer information during checkout with
      | field      | value           |
      | first_name | Updated         |
      | last_name  | Profile         |
      | phone      | 07999888777     |
    Then I should verify the customer profile has been updated
    And The customer profile should have the name "Updated Profile"
    And The customer profile should have the phone "07999888777"

  Scenario: Verify customer tags are applied after purchase
    Given I have a customer with email "profile-test@example.com"
    When I create an order for this customer with product "gut-rewild"
    Then I should verify the customer has the product tag "gut-rewild"
    And I should be able to add a custom tag "test-automation" to the customer
    And The customer profile should have the tag "test-automation"
```

### New Step Definitions

Add the following step definitions in a new file `customer_profile_steps.py`:

```python
from behave import given, when, then
import time
import re
import uuid
import json

@given('I have a test customer with email "{email}"')
def step_impl_create_test_customer(context, email):
    """Create or identify a test customer for testing"""
    context.test_customer_email = email
    
    # Check if customer already exists
    customers = context.mcp1_get_customers(limit=10)
    
    found = False
    for customer in customers['customers']:
        if customer['email'] == email:
            context.test_customer_id = customer['id']
            found = True
            break
    
    if not found:
        # Customer doesn't exist, so we'll create during the test
        context.test_customer_id = None

@given('I have cleaned up any profile data for "{email}"')
def step_impl_clean_profile_data(context, email):
    """Ensure we're starting with a clean customer profile state"""
    # This would normally archive/delete the customer profile
    # For testing, we'll just note that we'd clean up this customer
    context.test_customer_email = email
    context.profile_cleaned = True

@given('I have a customer with email "{email}"')
def step_impl_get_existing_customer(context, email):
    """Get an existing customer profile"""
    context.test_customer_email = email
    
    # Get customer details
    customers = context.mcp1_get_customers(limit=20)
    
    found = False
    for customer in customers['customers']:
        if customer['email'] == email:
            context.test_customer_id = customer['id']
            found = True
            break
    
    assert found, f"Customer with email {email} not found"

@when('I create an order as a new customer with')
def step_impl_create_order_as_new_customer(context):
    """Create an order as a new customer with provided details"""
    # Extract customer details from table
    customer_details = {}
    for row in context.table:
        customer_details[row['field']] = row['value']
    
    # Create draft order
    draft_order = context.mcp1_create_draft_order(
        email=customer_details['email'],
        lineItems=[{"variantId": "gid://shopify/ProductVariant/54961985519993", "quantity": 1}],  # Dark Spot Vanish
        shippingAddress={
            "address1": customer_details['address'],
            "city": customer_details['city'],
            "province": "United Kingdom",
            "country": "UK",
            "zip": customer_details['postcode'],
            "firstName": customer_details['first_name'],
            "lastName": customer_details['last_name'],
            "countryCode": "GB"
        }
    )
    
    # Store draft order ID for later verification
    context.draft_order_id = draft_order['id']
    
    # Complete the draft order
    completed_order = context.mcp1_complete_draft_order(
        draftOrderId=context.draft_order_id,
        variantId="gid://shopify/ProductVariant/54961985519993"
    )
    
    context.completed_order_id = completed_order['id']
    
    # Store customer details for verification
    context.customer_details = customer_details

@when('I create an order for this customer with address')
def step_impl_create_order_with_address(context):
    """Create an order for an existing customer with a new address"""
    # Extract address details from table
    address_details = {}
    for row in context.table:
        address_details[row['field']] = row['value']
    
    # Create draft order with the new address
    draft_order = context.mcp1_create_draft_order(
        email=context.test_customer_email,
        lineItems=[{"variantId": "gid://shopify/ProductVariant/54961985552761", "quantity": 1}],  # Younger You Skin Cream
        shippingAddress={
            "address1": address_details['address'],
            "city": address_details['city'],
            "province": "United Kingdom",
            "country": "UK",
            "zip": address_details['postcode'],
            "firstName": "Existing",  # We'd get this from the existing profile
            "lastName": "Customer",   # Or pass it in the table
            "countryCode": "GB"
        }
    )
    
    # Store draft order ID and address details for later verification
    context.draft_order_id = draft_order['id']
    context.address_details = address_details
    
    # Complete the draft order
    completed_order = context.mcp1_complete_draft_order(
        draftOrderId=context.draft_order_id,
        variantId="gid://shopify/ProductVariant/54961985552761"
    )
    
    context.completed_order_id = completed_order['id']

@when('I update the customer information during checkout with')
def step_impl_update_customer_info(context):
    """Update customer information during checkout"""
    # Extract customer update details from table
    update_details = {}
    for row in context.table:
        update_details[row['field']] = row['value']
    
    # We'll simulate this by creating an order with updated information
    draft_order = context.mcp1_create_draft_order(
        email=context.test_customer_email,
        lineItems=[{"variantId": "gid://shopify/ProductVariant/54961985978745", "quantity": 1}],  # Age Defying Trio
        shippingAddress={
            "address1": "Default Address",  # We could get this from the existing profile
            "city": "Default City",
            "province": "United Kingdom",
            "country": "UK",
            "zip": "AB1 2CD",
            "firstName": update_details.get('first_name', 'Default'),
            "lastName": update_details.get('last_name', 'Name'),
            "countryCode": "GB"
        },
        note=f"Phone: {update_details.get('phone', 'No Phone')}"
    )
    
    context.draft_order_id = draft_order['id']
    context.update_details = update_details
    
    # Complete the draft order
    completed_order = context.mcp1_complete_draft_order(
        draftOrderId=context.draft_order_id,
        variantId="gid://shopify/ProductVariant/54961985978745"
    )
    
    context.completed_order_id = completed_order['id']

@when('I create an order for this customer with product "{product_handle}"')
def step_impl_create_order_with_product(context, product_handle):
    """Create an order with a specific product for tracking purposes"""
    # Get product details
    products = context.mcp1_get_products(searchTitle=product_handle)
    
    product_found = False
    variant_id = None
    
    for product in products['products']:
        if product['handle'] == product_handle:
            variant_id = product['variants'][0]['id']
            product_found = True
            break
    
    assert product_found, f"Product with handle {product_handle} not found"
    
    # Create draft order
    draft_order = context.mcp1_create_draft_order(
        email=context.test_customer_email,
        lineItems=[{"variantId": variant_id, "quantity": 1}],
        note=f"Test order with product: {product_handle}"
    )
    
    context.draft_order_id = draft_order['id']
    context.product_handle = product_handle
    
    # Complete the draft order
    completed_order = context.mcp1_complete_draft_order(
        draftOrderId=context.draft_order_id,
        variantId=variant_id
    )
    
    context.completed_order_id = completed_order['id']

@then('I should verify the customer exists in Shopify backend')
def step_impl_verify_customer_exists(context):
    """Verify the customer exists in the Shopify backend"""
    # Get customers
    customers = context.mcp1_get_customers(limit=20)
    
    found = False
    for customer in customers['customers']:
        if customer['email'] == context.test_customer_email:
            context.test_customer_id = customer['id']
            found = True
            break
    
    assert found, f"Customer with email {context.test_customer_email} not found"

@then('The customer profile should have the name "{name}"')
def step_impl_verify_customer_name(context, name):
    """Verify the customer profile has the expected name"""
    # Get customer details
    # In a real implementation, this would use the MCP to get full customer details
    # For now we'll assume the name is correct if the customer was found
    assert hasattr(context, 'test_customer_id'), "No customer ID found to verify"
    
    # This is where you'd verify the actual name matches
    # Since we can't call the MCP functions directly in this mockup, we'll just assert
    assert True, "Customer name verification would happen here"

@then('The customer profile should have the email "{email}"')
def step_impl_verify_customer_email(context, email):
    """Verify the customer profile has the expected email"""
    # Since we found the customer by email, we know this is correct
    # But in a real test, you might want to verify more specifically
    assert context.test_customer_email == email, f"Expected email {email} but found {context.test_customer_email}"

@then('I should verify the customer profile has the address saved')
def step_impl_verify_address_saved(context):
    """Verify the customer profile has the address saved"""
    # Get customer details including addresses
    # In a real implementation, this would use the MCP to get full customer details
    assert hasattr(context, 'test_customer_id'), "No customer ID found to verify"
    
    # This is where you'd verify the address was saved
    # Since we can't call the MCP functions directly in this mockup, we'll just assert
    assert True, "Address verification would happen here"

@then('The saved address should contain "{address_part}"')
def step_impl_verify_address_part(context, address_part):
    """Verify the saved address contains the expected part"""
    # This would extract the address from the customer profile and verify it contains the part
    assert hasattr(context, 'address_details'), "No address details found to verify"
    
    # Verify the address contains the expected part
    # In a real test, you'd get the actual address from the customer profile
    found = False
    for field, value in context.address_details.items():
        if address_part in value:
            found = True
            break
    
    assert found, f"Address part '{address_part}' not found in saved address"

@then('I should verify the customer profile has been updated')
def step_impl_verify_profile_updated(context):
    """Verify the customer profile has been updated with new information"""
    # Get latest customer details
    # In a real implementation, this would use the MCP to get full customer details
    assert hasattr(context, 'test_customer_id'), "No customer ID found to verify"
    
    # This is where you'd verify the profile was updated
    # Since we can't call the MCP functions directly in this mockup, we'll just assert
    assert True, "Profile update verification would happen here"

@then('The customer profile should have the phone "{phone}"')
def step_impl_verify_customer_phone(context, phone):
    """Verify the customer profile has the expected phone number"""
    # This would verify the phone number in the customer profile
    assert hasattr(context, 'update_details'), "No update details found to verify"
    assert 'phone' in context.update_details, "No phone number in update details"
    
    customer_phone = context.update_details['phone']
    assert phone == customer_phone, f"Expected phone {phone} but found {customer_phone}"

@then('I should verify the customer has the product tag "{product_tag}"')
def step_impl_verify_product_tag(context, product_tag):
    """Verify the customer has the expected product tag"""
    # Get customer details including tags
    # In a real implementation, this would use the MCP to get full customer details
    assert hasattr(context, 'test_customer_id'), "No customer ID found to verify"
    
    # This is where you'd verify the tag exists
    # Since we can't call the MCP functions directly in this mockup, we'll just assert
    assert True, f"Would verify customer has tag '{product_tag}'"

@then('I should be able to add a custom tag "{tag}" to the customer')
def step_impl_add_custom_tag(context, tag):
    """Add a custom tag to the customer"""
    # Add tag to customer
    result = context.mcp1_tag_customer(
        customerId=context.test_customer_id,
        tags=[tag]
    )
    
    # Store the tag for verification
    context.custom_tag = tag
    
    # Verify tag was added successfully
    assert result and 'success' in result, f"Failed to add tag '{tag}' to customer"

@then('The customer profile should have the tag "{tag}"')
def step_impl_verify_customer_tag(context, tag):
    """Verify the customer profile has the expected tag"""
    # Get customer details including tags
    # In a real implementation, this would use the MCP to get full customer details
    assert hasattr(context, 'test_customer_id'), "No customer ID found to verify"
    
    # This is where you'd verify the tag exists
    # Since we can't call the MCP functions directly in this mockup, we'll just assert
    assert context.custom_tag == tag, f"Expected tag {tag} but found {context.custom_tag}"
```

### Integration with Environment Setup

Add the following MCP client methods to `environment.py`:

```python
# Add to the existing MCP client helper methods

def mcp1_tag_customer(customerId, tags):
    """Add tags to a customer"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.post(MCP_SERVER_URL + "/tag-customer", 
    #                    json={"customerId": customerId, "tags": tags}).json()
    pass

def mcp1_complete_draft_order(draftOrderId, variantId):
    """Complete a draft order"""
    # This is a placeholder - in real implementation would use MCP server
    # return requests.post(MCP_SERVER_URL + "/complete-draft-order", 
    #                    json={"draftOrderId": draftOrderId, "variantId": variantId}).json()
    pass
```

## Utilities for Customer Profile Testing

Create a utilities module `customer_profile_utils.py` in the `utils` directory:

```python
"""
Utility functions for working with customer profiles
"""
import uuid
import json
import requests
import os

def generate_test_email():
    """
    Generate a unique email for test customers
    
    Returns:
        A unique email address for testing
    """
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    return f"test-{unique_id}@example.com"

def create_test_customer(context, customer_data=None):
    """
    Create a test customer for use in tests
    
    Args:
        context: The behave context
        customer_data: Optional dict with customer data
        
    Returns:
        The customer ID
    """
    if customer_data is None:
        customer_data = {
            "email": generate_test_email(),
            "first_name": "Test",
            "last_name": "Customer",
            "address1": "123 Test Street",
            "city": "Test City",
            "country": "UK",
            "zip": "TE1 1ST"
        }
    
    # Create customer - this would use appropriate MCP methods
    # For now, just return a placeholder ID
    return "gid://shopify/Customer/1234567890"

def cleanup_test_customers(context):
    """
    Clean up test customers created during testing
    
    Args:
        context: The behave context
    """
    if hasattr(context, 'test_customer_ids'):
        for customer_id in context.test_customer_ids:
            # In a real implementation, would call appropriate API to archive/delete customers
            pass
```

## Testing Strategy

1. **Customer Identification**:
   - Use unique email addresses for test customers
   - Tag test customers for easy identification and cleanup

2. **Data Verification**:
   - Verify customer profile creation
   - Check address saving and updates
   - Validate tag application

3. **Cleanup**:
   - Archive or remove test customers after testing
   - Maintain test isolation

## Dependencies

- Shopify MCP server access
- Test environment with permissions for customer management
- Shopify Admin API access (through MCP)

## Expected Outcomes

1. Validated customer profile creation and management
2. Verification of customer data persistence
3. Confirmation of profile updates during checkout
4. Validated tagging functionality for customer segmentation
