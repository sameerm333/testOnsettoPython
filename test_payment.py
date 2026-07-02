import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TIMEOUT = 30


def test_update_payment_success(auth_headers, payment_payload):
    """
    Verify payment details are updated successfully.
    """

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    # -----------------------------
    # Contract Validation
    # -----------------------------

    assert "card_brand" in body
    assert "last4" in body
    assert "exp_month" in body
    assert "exp_year" in body
    assert "token" in body

    assert body["last4"] == payment_payload["card_number"][-4:]
    assert body["exp_month"] == payment_payload["exp_month"]
    assert body["exp_year"] == payment_payload["exp_year"]

    assert isinstance(body["token"], str)
    assert body["token"].startswith("tok_")

    # -----------------------------
    # Security Validation
    # -----------------------------

    assert "card_number" not in body
    assert "cvc" not in body

    response_text = response.text

    assert payment_payload["card_number"] not in response_text
    assert payment_payload["cvc"] not in response_text


@pytest.mark.parametrize(
    "card_number",
    [
        "4111111111111112",   # Luhn fail
        "1234567812345678",
        "9999999999999999",
        "4000000000000001"
    ]
)
def test_luhn_fail_cards(auth_headers, payment_payload, card_number):
    """
    Invalid card numbers should be rejected.
    """

    payment_payload["card_number"] = card_number

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_missing_card_number(auth_headers, payment_payload):
    """
    Card number is mandatory.
    """

    payment_payload.pop("card_number")

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)


def test_missing_cvc(auth_headers, payment_payload):
    """
    CVC is mandatory.
    """

    payment_payload.pop("cvc")

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)


def test_missing_cardholder(auth_headers, payment_payload):
    """
    Cardholder name is mandatory.
    """

    payment_payload.pop("cardholder_name")

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)


def test_missing_bearer_token(payment_payload):
    """
    Request without bearer token should be rejected.
    """

    response = requests.put(
        f"{BASE_URL}/account/payment",
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (401, 403)

    body = response.json()

    assert "last4" not in body
    assert "token" not in body


def test_invalid_bearer_token(payment_payload):
    """
    Invalid bearer token should be rejected.
    """

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers={
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json"
        },
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (401, 403)

    body = response.json()

    assert "last4" not in body
    assert "token" not in body


def test_only_last4_returned(auth_headers, payment_payload):
    """
    Verify only last four digits are returned.
    """

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    assert body["last4"] == payment_payload["card_number"][-4:]

    assert len(body["last4"]) == 4

    assert body["last4"] != payment_payload["card_number"]


def test_payment_token_returned(auth_headers, payment_payload):
    """
    Verify payment token is returned.
    """

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token"].startswith("tok_")


@pytest.mark.parametrize(
    "month",
    [0, 13, 20]
)
def test_invalid_expiry_month(auth_headers, payment_payload, month):
    """
    Invalid expiry month should be rejected.
    """

    payment_payload["exp_month"] = month

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)


def test_expired_card(auth_headers, payment_payload):
    """
    Expired card should be rejected.
    """

    payment_payload["exp_year"] = 2020

    response = requests.put(
        f"{BASE_URL}/account/payment",
        headers=auth_headers,
        json=payment_payload,
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)