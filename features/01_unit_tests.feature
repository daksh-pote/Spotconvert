Feature: Unit Tests
  Testing individual functions and components in isolation

  @unit @image-processing
  Scenario: Image format validation
    Given I have a file with extension ".xyz"
    When I check if it is a valid image format
    Then the validation should return "false"

  @unit @image-processing
  Scenario: Supported image formats list
    When I request the list of supported image formats
    Then the list should contain "png"
    And the list should contain "jpg"
    And the list should contain "webp"

  @unit @pdf-processing
  Scenario: PDF compression level validation
    Given I have a compression level "invalid"
    When I validate the compression level
    Then the validation should return "false"

  @unit @pdf-processing
  Scenario: PDF merge validation
    Given I have a list of 0 PDF files
    When I validate the merge request
    Then the validation should return "false"
    And the error message should be "At least two PDFs required"