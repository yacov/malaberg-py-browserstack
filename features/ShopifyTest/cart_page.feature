@shopify
Feature: Shopify Cart Page Tests
  As a user
  I want to modify items in my cart and proceed to checkout
  So that I can complete my purchase

  Background:
    Given I am on the product page for "gut-rewild"
    When I click Add to Cart
    And I click on the cart icon

  Scenario: Verify cart displays correct item details
    Then The cart should contain 1 items
    And Item 0 in cart should have name "Gut Rewild"
    And Item 0 in cart should have quantity 1
    And The subtotal should be visible
    And The subtotal should contain "£34.95"
    And The estimated total should contain "£34.95"

  Scenario: Verify item quantity can be increased
    When I increase the quantity of item 0 in cart
    Then Item 0 in cart should have quantity 2
    And The subtotal should contain "£69.90"

  Scenario: Verify item quantity can be decreased
    When I increase the quantity of item 0 in cart
    And I decrease the quantity of item 0 in cart
    Then Item 0 in cart should have quantity 1
    And The subtotal should contain "£34.95"

  Scenario: Verify item quantity can be directly set
    When I set the quantity of item 0 to 3
    Then Item 0 in cart should have quantity 3
    And The subtotal should contain "£104.85"

  Scenario: Verify item can be removed from cart
    When I remove item 0 from cart
    Then The cart should be empty

  Scenario: Verify checkout button functionality
    Then The checkout button should be enabled
    When I click the checkout button
    Then I should be redirected to the "checkout" page

  Scenario: Verify checkout button is disabled for empty cart
    When I clear the cart
    Then The cart should be empty
    And The checkout button should be disabled

  Scenario: Verify multiple items can be added to cart
    When I clear the cart
    And I am on the product page for "gut-rewild"
    And I click Add to Cart
    And I am on the product page for "good-skin"
    And I click Add to Cart
    And I click on the cart icon
    Then The cart should contain 2 items
    And Item 0 in cart should have name "Gut Rewild"
    And Item 1 in cart should have name "Good Skin"
