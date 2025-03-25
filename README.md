# behave-browserstack

[Behave](https://github.com/behave/behave) Integration with BrowserStack.

![BrowserStack Logo](https://d98b8t1nnulk5.cloudfront.net/production/images/layout/logo-header.png?1469004780)

## Malaberg Shopify Tests

This repository contains automated tests for Shopify using Behave and Selenium, with support for both local execution and BrowserStack integration.

## Prerequisites
```
- Python 3.7 or higher
- Chrome/Firefox browser installed for local testing
- BrowserStack account for cloud testing
```

## Setup
* Clone the repository 
  ```
  git clone -b sdk https://github.com/browserstack/behave-browserstack.git
  ```
* It is recommended to use a virtual environment to install dependencies:
  ```
  python -m venv env
  source env/bin/activate # on Mac/Linux
  env\Scripts\activate # on Windows
  ```
* Install dependencies 
  ```
  pip install -r requirements.txt
  ```

## Set BrowserStack Credentials
* Add your BrowserStack username and access key in the `browserstack.yml` config file.
* You can also export them as environment variables:
  #### For Windows
  ```
  set BROWSERSTACK_USERNAME=<browserstack-username>
  set BROWSERSTACK_ACCESS_KEY=<browserstack-access-key>
  
  # For permanent setting:
  setx BROWSERSTACK_USERNAME <browserstack-username>
  setx BROWSERSTACK_ACCESS_KEY <browserstack-access-key>
  ```
  #### For Linux/MacOS
  ```
  export BROWSERSTACK_USERNAME=<browserstack-username>
  export BROWSERSTACK_ACCESS_KEY=<browserstack-access-key>
  ```

## Running Tests Locally

To run tests locally using your installed Chrome browser:

```bash
# Run all Shopify tests
behave features/ShopifyTest --tags=@shopify

# Run specific feature
behave features/ShopifyTest/cart.feature

# Run with specific tags
behave features/ShopifyTest --tags=@cart

# Run with JUnit report generation
behave features/ShopifyTest --tags=@shopify --junit --junit-directory=reports
```

## Running Tests on BrowserStack

To run tests on BrowserStack using the SDK:

```bash
# Run all Shopify tests on BrowserStack
browserstack-sdk behave features/ShopifyTest --tags=@shopify

# Run specific feature on BrowserStack
browserstack-sdk behave features/ShopifyTest/cart.feature

# Run with specific tags on BrowserStack
browserstack-sdk behave features/ShopifyTest --tags=@cart

# Using the run_browserstack_tests.py helper script
python run_browserstack_tests.py --feature features/ShopifyTest --tags=@shopify
```

> **Note:** These tests are configured to run directly against the remote Shopify site. BrowserStack Local testing is disabled as it's not needed for these tests.

## Test Configuration

### Local Configuration
* Local WebDriver settings can be modified in `features/environment.py`
* Default timeout settings can be adjusted in `features/pages/Shopify/base_page.py`

### BrowserStack Configuration
* BrowserStack settings are defined in `browserstack.yml`
* You can modify the platforms, browsers, and devices in this file
* To test on a different set of browsers, check out the [platform configurator](https://www.browserstack.com/docs/automate/selenium/sdk-config-generator)

## Test Structure

```
features/
├── ShopifyTest/          # Feature files for Shopify tests
├── pages/                # Page objects
│   └── Shopify/          # Shopify-specific page objects
├── steps/                # Step definitions
│   └── Shopify/          # Shopify-specific step definitions
├── utils/                # Utility functions
│   ├── wait_utils.py     # Utilities for explicit waits
│   └── browserstack_utils.py # BrowserStack-specific utilities
└── environment.py        # Behave environment setup
```

## Debugging Tests

### Local Debugging
* Screenshots are automatically captured on test failures in the `screenshots` directory
* Page source is also captured for HTML analysis
* Check the console output for detailed error messages

### BrowserStack Debugging
* View test results on the [BrowserStack Automate dashboard](https://www.browserstack.com/automate)
* Screenshots, videos, and logs are automatically captured
* Session details and network logs are available for debugging

## Best Practices

1. **Page Objects**: Always use page objects for better maintainability
2. **Error Handling**: Use try/except blocks with descriptive error messages
3. **Explicit Waits**: Avoid hardcoded sleeps, use explicit waits instead
4. **Reuse Page Objects**: Store page objects in context to avoid creating new instances
5. **Retry Mechanism**: Flaky tests will be automatically retried based on the MAX_RETRIES setting

## Additional Resources
* [Behave Documentation](https://behave.readthedocs.io/en/latest/)
* [Selenium Python Documentation](https://selenium-python.readthedocs.io/)
* [BrowserStack Documentation](https://www.browserstack.com/docs/automate/selenium)
* [Documentation for writing Automate test scripts in Python](https://www.browserstack.com/automate/python)
* [Customizing your tests on BrowserStack](https://www.browserstack.com/automate/capabilities)
* [Browsers & mobile devices for selenium testing on BrowserStack](https://www.browserstack.com/list-of-browsers-and-platforms?product=automate)
* [Using REST API to access information about your tests via the command-line interface](https://www.browserstack.com/automate/rest-api)

## Notes
* You can view your test results on the [BrowserStack Automate dashboard](https://www.browserstack.com/automate)
* To test on a different set of browsers, check out our [platform configurator](https://www.browserstack.com/docs/automate/selenium/sdk-config-generator)
* Understand how many parallel sessions you need by using our [Parallel Test Calculator](https://www.browserstack.com/automate/parallel-calculator?ref=github)
