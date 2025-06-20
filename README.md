# Python Selenium Automation Framework

## Overview

This is a professional and robust base for a Python Selenium automation framework, built using the Page Object Model (POM) design pattern. It provides a solid foundation for creating scalable and maintainable web automation scripts.

The framework is designed to be easily extensible. You can add new page objects, tests, and utility functions to suit your specific needs.

## Features

- **Page Object Model (POM):** A design pattern that creates a clear separation between test code and page-specific code.
- **Cross-Browser Support:** Easily run tests on Chrome, Firefox, and Edge.
- **Explicit Waits:** Uses `WebDriverWait` to handle dynamic elements, avoiding unreliable `time.sleep()` calls.
- **Centralized Driver Management:** A `DriverFactory` to manage WebDriver instances.
- **Dependency Management:** All required packages are listed in `requirements.txt`.
- **Professional Structure:** A clean and organized project structure that is easy to understand and maintain.

## Project Structure

```
.
├── config/
│   └── config.py
├── pages/
│   ├── __init__.py
│   └── base_page.py
├── utils/
│   ├── __init__.py
│   └── driver_factory.py
├── .gitignore
├── main.py
└── requirements.txt
```

- **`config/`**: Contains configuration files, such as URLs, credentials, and other settings.
- **`pages/`**: Contains page object classes. Each class represents a page in the web application and contains the locators and methods for interacting with that page.
- **`utils/`**: Contains utility classes and functions, such as the `DriverFactory` for creating WebDriver instances.
- **`main.py`**: The entry point of the application.
- **`requirements.txt`**: A file listing the Python packages required for the project.
- **`.gitignore`**: Specifies which files and directories to ignore in a Git repository.

## Getting Started

### Prerequisites

- Python 3.6+
- `pip` (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
        # Create a virtual environment
        python -m venv .venv

        # Activate the virtual environment:

        # On Mac/Linux:
        source .venv/bin/activate

        # On Windows:

        # Git Bash:
        source .venv/Scripts/activate

        # CMD:
        .venv\Scripts\activate.bat

        # PowerShell:
        .venv\Scripts\Activate.ps1
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Automation

To run the automation script, execute the `main.py` file from the root directory:

```bash
python main.py
```

The script will prompt you to enter a URL and choose a browser (chrome, firefox, or edge).

## Page Object Model (POM)

This framework uses the Page Object Model (POM), which is a design pattern that enhances test maintenance and reduces code duplication. In POM, each web page in the application is represented as a class. This class contains the locators for the elements on the page and the methods to interact with those elements.

The `pages/base_page.py` file contains a `BasePage` class from which all other page object classes should inherit. This base class includes common methods like finding elements, clicking, sending keys, etc., using explicit waits for robustness.

## Dependencies

- `selenium`: The main library for browser automation.
- `webdriver-manager`: A library that automatically manages the binaries for web drivers (e.g., chromedriver, geckodriver).
