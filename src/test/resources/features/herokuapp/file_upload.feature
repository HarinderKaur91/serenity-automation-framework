@herokuapp
Feature: Heroku File Upload
  As a user with a document to share
  I want to upload a file
  So that the server confirms it was received

  Scenario: Uploading a generated file shows the file name on the response page
    Given I open the Heroku file upload page
    When I upload a file named "report.txt"
    Then the uploaded file name should contain "report.txt"
