@shopify
Feature: Shopify Product Page Tests
  As a user
  I want to browse product details and interact with product options
  So that I can make informed purchasing decisions

  Background:
    Given I am on the product page for "gut-rewild"

  Scenario: Verify product details are displayed correctly
    Then I should see the product title "Gut Rewild"
    And I should see the product price "£34.95"
    And The featured image should be loaded
    And I should see the product description
    
  Scenario: Verify variant selection
    When I select product variant 1 by index
    Then I should see the current quantity is 1
    When I select product variant "30-day-supply" by value
    Then I should see the product price "£34.95"
    
  Scenario: Verify quantity controls
    When I set quantity to 2
    Then I should see the current quantity is 2
    When I increase the quantity 1 times
    Then I should see the current quantity is 3
    When I decrease the quantity 2 times
    Then I should see the current quantity is 1
    
  Scenario: Verify Add to Cart functionality
    When I set quantity to 2
    And I click Add to Cart
    Then I should see the cart count is "2"
    
  Scenario: Verify Buy Now functionality
    When I click Buy Now
    Then I should be redirected to the "checkout" page
    
  Scenario: Verify subscription option
    When I select Subscribe and Save option
    And I select subscription frequency "30"
    Then I should see the product price contains discount
    
  Scenario: Verify gallery thumbnails
    When I click gallery thumbnail 1
    Then The featured image should change
    When I click gallery thumbnail 0
    Then The featured image should revert back
    
  Scenario: Verify FAQ section
    Then I should see 5 FAQ items
    When I expand FAQ item 0
    Then FAQ item 0 should be expanded
    When I expand FAQ item 1
    Then FAQ item 1 should be expanded
    And FAQ item 0 should be expanded
    
  Scenario: Verify science section content
    Then I should see the prebiotic description contains "feed"
    And I should see the probiotic description contains "bacteria"
    And I should see the postbiotic description contains "byproducts"
