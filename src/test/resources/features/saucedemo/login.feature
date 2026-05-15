@saucedemo
Feature: SauceDemo Login
  As a user of SauceDemo
  I want to log in with valid credentials
  So that I can browse the product inventory

  Scenario: Standard user can log in and see the inventory
    Given I open the SauceDemo login page
    When I log in as "standard_user" with password "secret_sauce"
    Then I should see the products inventory

  Scenario: Locked-out user gets a clear error message
    Given I open the SauceDemo login page
    When I log in as "locked_out_user" with password "secret_sauce"
    Then I should see an error containing "locked out"
