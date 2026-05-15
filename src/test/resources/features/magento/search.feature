@magento
Feature: Magento Product Search
  As a shopper on the Magento demo store
  I want to search for products
  So that I can find what I'm looking for

  Scenario: Searching for jackets shows relevant results
    Given I open the Magento store home page
    When I search for "jacket"
    Then at least one product result should mention "jacket"

  Scenario: The page title reflects the search term
    Given I open the Magento store home page
    When I search for "bag"
    Then the page title should mention "bag"
