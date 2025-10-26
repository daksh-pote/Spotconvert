Feature: Image conversion
  Convert images between PNG, JPG, JPEG and WebP formats using the webapp endpoints

  Scenario: Convert PNG to JPG
    Given I have a PNG image
    When I convert it to "jpg"
    Then the response content-type should be "image/jpeg"
    And the response filename should end with ".jpg"

  Scenario: Convert JPG to WebP
    Given I have a JPG image
    When I convert it to "webp"
    Then the response content-type should be "image/webp"
    And the response filename should end with ".webp"

  Scenario: Convert WebP to PNG
    Given I have a WebP image
    When I convert it to "png"
    Then the response content-type should be "image/png"
    And the response filename should end with ".png"
