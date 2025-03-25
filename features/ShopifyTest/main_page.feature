@shopify @mobile
Feature: Shopify Main Page Tests
  As a user
  I want to browse the Shopify homepage
  So that I can learn about products and navigate the site

  Background:
    Given I am on the Shopify homepage

  Scenario: Verify navigation links
    Then I should see the main navigation
    When I click on the "HOME" navigation link
    Then I should be redirected to the homepage
    When I click on the "ABOUT" navigation link
    Then I should be redirected to the "about us" page
    When I click on the "PRODUCTS" navigation link
    Then I should be redirected to the "products" page
    When I click on the "CONTACT US" navigation link
    Then I should be redirected to the "contact us" page

  Scenario: Verify logo navigation
    When I click on the logo
    Then I should be redirected to the homepage

  Scenario: Verify main page images load correctly
    Then I should see the main navigation
    And The featured image should be loaded
    When I scroll down to the product section
    Then All product images should be loaded

  Scenario: Verify Learn More button
    When I click the Learn More button
    Then I should be redirected to the "about us" page

  Scenario: Verify left banner functionality
    When I click on the left banner
    Then I should be redirected to the "products" page

  Scenario: Check cofounder information is displayed
    Then I should see the cofounder information
    And The cofounder image should be loaded

  Scenario: Verify Buy Now functionality
    When I click on the Buy Now link
    Then I should be redirected to the product page

  Scenario: Mobile menu functionality
    When I open the mobile menu
    Then I should see the mobile menu
    When I click on the login link in the mobile menu
    Then I should be redirected to the "login" page
