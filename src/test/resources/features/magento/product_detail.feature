@magento
Feature: Magento Product Detail Navigation
  As a shopper drilling into search results
  I want to open a product and see its full details
  So that I can decide whether to buy

  Scenario: Open the first jacket from the results and verify the detail page
    Given I open the Magento store home page
    When I search for "jacket"
    And I open the first product in the results
    Then the product detail page name should mention "jacket"
    And the product price should be displayed
    And the Add to Cart button should be available
