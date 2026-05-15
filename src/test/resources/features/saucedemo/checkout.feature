@saucedemo
Feature: SauceDemo End-to-End Checkout
  As a returning shopper
  I want to add items to my cart and complete a purchase
  So that the full e-commerce funnel is verified

  Background:
    Given I open the SauceDemo login page
    When I log in as "standard_user" with password "secret_sauce"
    Then I should see the products inventory

  Scenario: Add a single item to the cart
    When I add the "Sauce Labs Backpack" to my cart
    Then the cart badge should show "1"

  Scenario: Add multiple items and verify cart contents
    When I add the "Sauce Labs Backpack" to my cart
    And I add the "Sauce Labs Bike Light" to my cart
    And I add the "Sauce Labs Bolt T-Shirt" to my cart
    Then the cart badge should show "3"
    When I open the shopping cart
    Then the cart should contain 3 items

  Scenario: Complete a full purchase
    When I add the "Sauce Labs Backpack" to my cart
    And I open the shopping cart
    And I checkout as "Jane" "Doe" with zip "94016"
    Then I should see the order confirmation "Thank you for your order"
