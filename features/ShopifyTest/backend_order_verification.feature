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
