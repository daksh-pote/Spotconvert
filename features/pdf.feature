Feature: PDF compression and merging
  Test PDF compression and merging endpoints

  Scenario: Compress a PDF and receive a PDF back
    Given I have a generated PDF file
    When I compress it with level "ebook"
    Then the response content-type should be "application/pdf"
    And the compressed PDF size should be greater than 0

  Scenario: Merge two PDFs
    Given I have two generated PDF files
    When I merge them
    Then the response content-type should be "application/pdf"
    And the merged PDF size should be greater than 0
