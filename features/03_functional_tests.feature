Feature: Functional Tests
  Testing complete workflows and business logic

  @functional @image-workflow
  Scenario Outline: Image format conversion workflow
    Given I have an image in "<source_format>" format
    When I convert it to "<target_format>"
    Then the conversion should be successful
    And the output image should be in "<target_format>" format
    And the image dimensions should be preserved

    Examples:
      | source_format | target_format |
      | png          | jpg           |
      | jpg          | webp          |
      | webp         | png           |
      | png          | webp          |

  @functional @pdf-workflow
  Scenario Outline: PDF compression quality levels
    Given I have a PDF document
    When I compress it with level "<level>"
    Then the compression should be successful
    And the output file should be smaller than input
    And the PDF should be readable

    Examples:
      | level    |
      | screen   |
      | ebook    |
      | printer  |
      | prepress |

  @functional @batch-processing
  Scenario: Batch image conversion
    Given I have multiple images in different formats
    When I convert all images to "webp"
    Then all conversions should be successful
    And all output files should be in WebP format