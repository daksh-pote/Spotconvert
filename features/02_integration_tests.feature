Feature: Integration Tests
  Testing API endpoints and their interactions

  @integration @api
  Scenario: Image conversion endpoint response codes
    Given the application is running
    When I send an empty POST request to "/convert-image"
    Then the response status code should be 400
    And the response should contain an error message

  @integration @api
  Scenario: PDF compression endpoint response codes
    Given the application is running
    When I send an empty POST request to "/compress-pdf"
    Then the response status code should be 400
    And the response should contain an error message

  @integration @api @error-handling
  Scenario: Invalid file upload handling
    Given I have a text file
    When I try to convert it to "png"
    Then the response status code should be 415
    And the response should contain "Unsupported file type"

  @integration @api @headers
  Scenario: CORS headers validation
    Given the application is running
    When I send an OPTIONS request to "/convert-image"
    Then the response should include CORS headers
    And the response status code should be 200