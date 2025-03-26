@shopify @live
Feature: Shopify Live Backend Order Verification
  As a tester
  I want to verify orders are correctly created in the actual Shopify backend
  So that I can ensure data integrity between frontend and backend

  Background:
    Given I have a valid Shopify API connection
    And I have cleaned up any test orders for test user "test@example.com"

  Scenario: Verify real order in Shopify backend
    Given I am on the product page for "gut-rewild"
    When I click Add to Cart
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
    Then I should verify the order exists in Shopify backend using the real API
    And The real order should have line item "Gut Rewild"
    And The real order should have the correct price
    And The real order should have the customer email "test@example.com"
    And The real order should have the shipping address "123 Test Street"

  Scenario: Verify multiple items in real Shopify order
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
    Then I should verify the order exists in Shopify backend using the real API
    And The real order should have 2 line items
    And The real order should have line item "Gut Rewild"
    And The real order should have line item "Younger You Skin Cream"
    And The real order should have the total price reflecting both items

  Scenario: Create draft order via API and verify in backend
    Given I create a draft order via API with
      | email      | test@example.com          |
      | product    | Gut Rewild                |
      | address    | 123 Test Street, London   |
      | first_name | Test                      |
      | last_name  | User                      |
    When I complete the draft order with payment
    Then I should verify the order exists in Shopify backend using the real API
    And The real order should have line item "Gut Rewild"
    And The real order should have a status of either "OPEN" or "FULFILLED"
