@shopify
Feature: Shopify Backend Order Verification With Mock Data
  As a tester
  I want to verify mock orders in the backend
  So that I can validate the verification process

  Scenario: Verify existing test order in backend
    Given I have cleaned up any test orders for test user "test@example.com"
    When I set "test@example.com" as the checkout email
    Then I should verify the order exists in Shopify backend
    And The order should have line item "Gut Rewild"
    And The order should have the price "GBP69.90"
    And The order should have the customer email "test@example.com"
    And The order should have the shipping address "123 Test Street"
    And The order should have a status of either "OPEN" or "FULFILLED"

  Scenario: Verify multiple line items in an order
    Given I have cleaned up any test orders for test user "another@example.com"
    When I set "another@example.com" as the checkout email
    Then I should verify the order exists in Shopify backend
    And The order should have 2 line items
    And The order should have line item "Gut Rewild" 
    And The order should have line item "Younger You Skin Cream"
    And The order should have the total price reflecting both items
    
  Scenario: Verify order with a real test user from the store
    Given I have cleaned up any test orders for test user "2a5f9d12@malaberg.com"
    When I set "2a5f9d12@malaberg.com" as the checkout email
    Then I should verify the order exists in Shopify backend
    And The order should have line item "Gut Rewild"
    And The order should have a status of either "OPEN" or "FULFILLED"
    And The order should have the customer email "2a5f9d12@malaberg.com"
