@shopify
Feature: Shopify Checkout Process Tests
  As a user
  I want to complete the checkout process
  So that I can purchase products

  Background:
    Given I am on the product page for "gut-rewild"
    When I click Add to Cart
    And I click on the cart icon
    And I click the checkout button

  Scenario: Verify checkout page displays order summary
    Then I should see the order summary
    And I should see the shopping cart heading
    And I should see the product image in checkout
    And The subtotal in checkout should contain "£34.95"

  Scenario: Verify shipping information form completion
    When I fill in the shipping information
    Then The "Pay now" button should be enabled
    
  Scenario: Verify shipping information form with custom data
    When I fill in the shipping information with
      | field      | value            |
      | email      | test@example.com |
      | first_name | Jane             |
      | last_name  | Smith            |
      | address    | 456 Test Avenue  |
      | city       | Manchester       |
      | postcode   | M1 1AA           |
      | phone      | 07987654321      |
    Then The "Pay now" button should be enabled

  Scenario: Verify payment method selection
    When I fill in the shipping information
    And I select payment method "credit_card"
    Then The "Pay now" button should be enabled

  Scenario: Verify terms of service link
    When I click the Terms of Service link
    Then I should be redirected to the "terms-of-service" page

  Scenario: Verify privacy policy link
    When I click the Privacy Policy link
    Then I should be redirected to the "privacy/app-users" page

  Scenario: Verify "Remember me" checkbox functionality
    When I fill in the shipping information
    And I check "Remember me"
    Then The "Pay now" button should be enabled

  Scenario: Verify form validation - missing email
    When I fill in the shipping information with
      | field      | value           |
      | first_name | John            |
      | last_name  | Doe             |
      | address    | 123 Test Street |
      | city       | London          |
      | postcode   | W1A 1AA         |
      | phone      | 07123456789     |
    Then I should see an error message containing "email"

  Scenario: Verify form validation - missing address
    When I fill in the shipping information with
      | field      | value            |
      | email      | test@example.com |
      | first_name | John             |
      | last_name  | Doe              |
      | city       | London           |
      | postcode   | W1A 1AA          |
      | phone      | 07123456789      |
    Then I should see an error message containing "address"

  Scenario: Verify shipping cost calculation
    When I fill in the shipping information
    Then The shipping cost should contain "£0.00"
    And The total cost should contain "£34.95"

  Scenario: Complete purchase flow
    When I fill in the shipping information
    And I select payment method "credit_card"
    And I check "Use shipping address as billing address"
    And I click "Pay now"
    # This step would typically lead to payment processing page
    # But for testing purposes we're stopping at the confirmation
