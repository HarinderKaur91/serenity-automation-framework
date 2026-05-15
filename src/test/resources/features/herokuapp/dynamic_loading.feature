@herokuapp
Feature: Heroku Dynamic Loading
  As a tester verifying explicit waits
  I want to confirm an asynchronously loaded element appears
  So that wait strategies are validated

  Scenario: Element appears after dynamic loading completes
    Given I open the Heroku dynamic loading page
    When I click the Start button
    Then I should see the loaded text "Hello World!"
