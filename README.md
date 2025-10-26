# Test Automation Framework

This project implements a comprehensive test automation framework using Python, Behave, and Selenium WebDriver. It includes multiple testing levels from unit tests to acceptance tests, along with image and PDF processing capabilities.

## Project Structure

```
├── app.py                 # Main application file
├── features/             # Behave test features
│   ├── steps/            # Step definitions
│   ├── environment.py    # Behave environment configuration
│   ├── 01_unit_tests.feature
│   ├── 02_integration_tests.feature
│   ├── 03_functional_tests.feature
│   ├── 04_ui_tests.feature
│   ├── 05_acceptance_tests.feature
│   ├── image_conversion.feature
│   └── pdf.feature
├── static/              # Static assets
│   └── style.css
├── templates/           # HTML templates
│   └── index.html
└── uploads/            # Upload directory for file processing
```

## Prerequisites

- Python 3.x
- Google Chrome or Firefox browser
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running Tests

The project includes different types of tests that can be run using Behave:

- Unit Tests:
  ```
  behave features/01_unit_tests.feature
  ```

- Integration Tests:
  ```
  behave features/02_integration_tests.feature
  ```

- Functional Tests:
  ```
  behave features/03_functional_tests.feature
  ```

- UI Tests:
  ```
  behave features/04_ui_tests.feature
  ```

- Acceptance Tests:
  ```
  behave features/05_acceptance_tests.feature
  ```

To run all tests:
```
behave
```

## Features

- **Multiple Test Levels**: Comprehensive testing from unit to acceptance tests
- **UI Testing**: Automated browser testing using Selenium WebDriver
- **Image Processing**: Support for image conversion and manipulation
- **PDF Processing**: Capabilities for PDF file handling
- **File Upload Handling**: Support for file upload testing

## Project Components

- `app.py`: Main application entry point
- `features/`: Contains all Behave feature files and step definitions
- `static/`: Contains CSS and other static assets
- `templates/`: Contains HTML templates
- `uploads/`: Directory for temporary file storage during tests

## Best Practices

- Feature files are organized by test type (unit, integration, etc.)
- Step definitions are modular and reusable
- File cleanup operations include retry mechanisms for Windows compatibility
- Proper error handling and logging throughout the test suite

## Contributing

When contributing to this project:

1. Create descriptive feature files using Gherkin syntax
2. Implement reusable step definitions
3. Include proper cleanup in your test scenarios
4. Add appropriate error handling
5. Document any new features or changes

## Running the Application

To run the web application:

```
python app.py
```

The application will be available at `http://localhost:5000` (default port).