@shopify
Feature: Shopify Backend Connection Test
  As a tester
  I want to verify the MCP server connection works
  So that I can implement backend verification tests

  Scenario: Verify Shopify MCP server is accessible
    Given I have a backend connection to Shopify
    When I query for products
    Then I should receive product data from the backend
