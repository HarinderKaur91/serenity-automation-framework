@herokuapp
Feature: Heroku Dropdown Selection
  As a user filling a form
  I want to choose options from a dropdown
  So that the selection is preserved

  Scenario Outline: Selecting an option updates the dropdown value
    Given I open the Heroku dropdown page
    When I select dropdown option "<option>"
    Then the selected dropdown option should be "<option>"

    Examples:
      | option   |
      | Option 1 |
      | Option 2 |
