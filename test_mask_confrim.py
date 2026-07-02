import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TIMEOUT = 30


def test_masked_confirmation_matches_updated_data(
    auth_headers,
    banking_payload,
    payment_payload,
):
    """
    Verify that the masked confirmation returned by the API
    matches the data that was submitted.

    
    """

    # ---------------------------------------
    # Update Banking Details
    # ---------------------------------------

    banking_response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert banking_response.status_code == 200

    banking_body = banking_response.json()

    # Verify masked routing number
    assert banking_body["routing_masked"].endswith(
        banking_payload["routing_number"][-4:]
    )

    # Verify masked account number
    assert banking_body["account_masked"].endswith(
        banking_payload["account_number"][-4:]
    )

    # Ensure raw values are never returned
    assert banking_body["routing_masked"] != banking_payload["routing_number"]
    assert banking_body["account_masked"] != banking_payload["account_number"]

    # ---------------------------------------
    # Update Payment Details
    # ---------------------------------------

    payment_response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT,
    )

    assert payment_response.status_code == 200

    payment_body = payment_response.json()

    # Verify only last four digits are returned
    assert payment_body["last4"] == payment_payload["card_number"][-4:]

    # Verify expiry details
    assert payment_body["exp_month"] == payment_payload["exp_month"]
    assert payment_body["exp_year"] == payment_payload["exp_year"]

    # Ensure sensitive information is never returned
    assert "card_number" not in payment_body
    assert "cvc" not in payment_body