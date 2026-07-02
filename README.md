# Onsetto API Test Assignment

## Overview

This project contains automated API tests for the Onsetto REST API using **Python**, **pytest**, and **requests**. The tests authenticate using the required two-step MFA flow, update banking and payment information, validate API contracts, verify security requirements, and perform a cross-layer consistency check between the API and the UI.

## Project Structure

```text
testOnsetoPython/
│
├── .env
├── requirements.txt
├── conftest.py
├── test_auth.py
├── test_banking.py
├── test_payment.py
├── test_mask_confirm.py
└── README.md
```

## Prerequisites

- Python 3.10 or later
- pip

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <project>
```
## 🛠️ Environment Setup

Follow these steps to create and activate an isolated Python virtual environment for this project.

###  Create the Virtual Environment

Open your terminal, navigate to the project root directory, and run the command for your operating system:

```bash
# macOS / Linux
python3 -m venv .venv

# Windows
python -m venv .venv
```
*(Note: `.venv` is the folder where your environment dependencies will be stored).*

###  Activate the Environment

You must activate the virtual environment before installing packages or running scripts.

```bash
# macOS / Linux (Bash/Zsh)
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with the following values:

```properties
BASE_URL=https://exampl.com

EMAIL=your_email@example.com
PASSWORD=your_password
MFA_CODE=1234

ROUTING_NUMBER=021000021
ACCOUNT_NUMBER=1234567890

CARDHOLDER_NAME=Test User
CARD_NUMBER=4242424242424242
EXP_MONTH=12
EXP_YEAR=2027
CVC=123
```

## Running the Tests

Run the complete test suite:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest test_banking.py -v
```

Generate an HTML report (optional):

```bash
pytest --html=report.html --self-contained-html
```

## Test Coverage

The suite includes:

- **Authentication**
  - Valid login
  - Invalid credentials
  - Invalid MFA code
  - Missing required fields

- **Banking**
  - Successful update
  - Invalid routing number
  - Missing required fields
  - Authorization checks
  - Response contract validation

- **Payment**
  - Successful update
  - Invalid (Luhn-fail) card
  - Invalid expiry values
  - Missing required fields
  - Response contract validation

- **Security**
  - Missing bearer token
  - Invalid bearer token
  - Sensitive data is never returned in API responses
  - Unauthorized requests do not leak account information

## Cross-Layer Validation

One of the primary objectives of this assignment is verifying consistency between the backend and the UI.

After updating banking or payment information, the tests compare:

- the masked confirmation returned by the REST API, and
- the "Last Updated" summary shown in the UI.

This detects **cross-layer data consistency bugs**, where the backend successfully stores one value but the UI displays a different value because of stale data, incorrect mapping, caching issues, or formatting defects.

If the API and UI use different masking characters (for example, `•••••0021` versus `*****0021`) but reveal the same last four digits, the tests record the difference rather than treating it as a failure, since the protected data remains consistent.

A UI-only test cannot verify what was actually stored in the backend, while an API test that only checks for `200 OK` cannot verify what the user ultimately sees. Comparing both layers provides stronger confidence that the application behaves correctly end-to-end.

## Approach

The implementation intentionally uses a lightweight structure based on `pytest` and `requests`
The focus was on:

- verifying API contracts rather than only HTTP status codes
- validating returned fields and response structure
- checking security requirements
- testing negative scenarios
- keeping the tests readable and easy to review

Authentication is performed once per test session using a shared pytest fixture to reduce unnecessary authentication requests.

## AI Tooling

Generative AI was used as a development aid to help:

- organize the test structure,
- draft test cases,
- improve code readability,
- refine documentation
