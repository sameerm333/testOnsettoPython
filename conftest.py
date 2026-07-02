import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
MFA_CODE = os.getenv("MFA_CODE")

TIMEOUT = 30


@pytest.fixture(scope="session")
def access_token():
    """
    Authenticate once and return the Bearer token.
    """

    # --------------------------------------------
    # Step 1 - Username & Password
    # --------------------------------------------
    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": EMAIL,
            "password": PASSWORD
        },
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    assert body["mfa_required"] is True
    assert "mfa_token" in body
    assert body["mfa_token"] != ""

    mfa_token = body["mfa_token"]

    # --------------------------------------------
    # Step 2 - MFA
    # --------------------------------------------
    response = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "mfa_token": mfa_token,
            "code": MFA_CODE
        },
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] > 0

    return body["access_token"]


@pytest.fixture(scope="session")
def auth_headers(access_token):
    """
    Returns Authorization header for authenticated requests.
    """

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def banking_payload():
    """
    Valid banking payload.
    """

    return {
        "routing_number": os.getenv("ROUTING_NUMBER"),
        "account_number": os.getenv("ACCOUNT_NUMBER")
    }


@pytest.fixture
def payment_payload():
    """
    Valid payment payload.
    """

    return {
        "cardholder_name": os.getenv("CARDHOLDER_NAME"),
        "card_number": os.getenv("CARD_NUMBER"),
        "exp_month": int(os.getenv("EXP_MONTH")),
        "exp_year": int(os.getenv("EXP_YEAR")),
        "cvc": os.getenv("CVC")
    }