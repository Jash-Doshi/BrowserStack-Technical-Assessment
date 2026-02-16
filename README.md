# El País Editorial Scraper & Cross-Platform Analysis

# Project Overview
This project is an automated Selenium-based solution designed to scrape editorial content from the Spanish news outlet **El País**, translate article headlines using a third-party translation API, and perform linguistic analysis on the translated results.

The solution is integrated with **BrowserStack Automate** to demonstrate cross-platform reliability across both desktop and mobile environments.

# Key Features

1) **Web Scraping with Selenium**  
  Extracts the first five articles from the Opinion section of El País, including titles, preview content, and cover images (when available).

2) **Compliance Verification**
Programmatically verifies that the website is displayed in Spanish before scraping to ensure data integrity.

3) **Translation API Integration**  
  Uses the Translate Plus API (via RapidAPI) to translate Spanish headlines into English.

4) **Linguistic Analysis**  
  Performs word frequency analysis on translated headlines and identifies words that appear more than twice.

5) **Parallel Cross-Browser Testing**  
  Executes simultaneously across 5 platforms using Python's `threading` module:
1)Windows 11 – Chrome
2)Windows 10 – Firefox
3)macOS – Safari
4)Android – Samsung Galaxy S23
5)iOS – iPhone 15

6) **Secure Credential Handling**  
  All sensitive credentials are managed using environment variables (`os.getenv`), ensuring no secrets are exposed in the source code.


# BrowserStack Build Results

You can view the public build execution here:

[View BrowserStack Build](https://automate.browserstack.com/projects/El+Pais+CE+Assessment/builds/El+Pais+Assessment/1?tab=tests&testListView=flat&public_token=18cdbed6337af7600656153c888e4e8aa089c9edf8695e5ea70fbe4b1cb1f2bf)


# Setup & Execution

# 1. Prerequisites

Ensure Python 3.x is installed.

Install required dependencies:

```bash
pip install selenium webdriver-manager requests

# 2. Set Environment Variables

The script retrieves credentials securely from your local environment.


Windows (PowerShell)
$env:BROWSERSTACK_USERNAME="your_username"
$env:BROWSERSTACK_ACCESS_KEY="your_access_key"
$env:RAPIDAPI_KEY="your_rapidapi_key"


macOS / Linux
export BROWSERSTACK_USERNAME="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"
export RAPIDAPI_KEY="your_rapidapi_key"

# 3. Run the Script
python assessment-code.py



