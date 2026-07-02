import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TIMEOUT = 30


def test_update_banking_success(auth_headers, banking_payload):
    """
    Verify banking details are updated successfully.
    """

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code == 200

    body = response.json()

    # -------------------------
    # Contract validation
    # -------------------------

    assert "routing_masked" in body
    assert "account_masked" in body
    assert "token" in body

    assert isinstance(body["routing_masked"], str)
    assert isinstance(body["account_masked"], str)
    assert isinstance(body["token"], str)

    # -------------------------
    # Verify masking
    # -------------------------

    routing = banking_payload["routing_number"]
    account = banking_payload["account_number"]

    assert body["routing_masked"].endswith(routing[-4:])
    assert body["account_masked"].endswith(account[-4:])

    # -------------------------
    # Never leak sensitive values
    # -------------------------

    assert body["routing_masked"] != routing
    assert body["account_masked"] != account

    assert "routing_number" not in body
    assert "account_number" not in body


@pytest.mark.parametrize(
    "routing",
    [
        "123",
        "12345",
        "12345678",
        "1234567890",
    ],
)
def test_invalid_routing_length(auth_headers, banking_payload, routing):
    """
    Invalid routing length should be rejected.
    """

    banking_payload["routing_number"] = routing

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (400, 422)

    body = response.json()

    # API should provide validation information
    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


@pytest.mark.parametrize(
    "routing",
    [
        "ABCDEFGHI",
        "12ABC4567",
        "!@#$56789",
    ],
)
def test_invalid_routing_format(auth_headers, banking_payload, routing):
    """
    Routing number must contain only digits.
    """

    banking_payload["routing_number"] = routing

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_missing_account_number(auth_headers, banking_payload):
    """
    Account number is mandatory.
    """

    banking_payload.pop("account_number")

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_missing_routing_number(auth_headers, banking_payload):
    """
    Routing number is mandatory.
    """

    banking_payload.pop("routing_number")

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_missing_bearer_token(banking_payload):
    """
    Request without bearer token should be rejected.
    """

    response = requests.put(
        f"{BASE_URL}/account/banking",
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (401, 403)

    body = response.json()

    # Ensure no sensitive data leaked
    assert "routing_masked" not in body
    assert "account_masked" not in body
    assert "token" not in body


def test_invalid_bearer_token(banking_payload):
    """
    Invalid bearer token should be rejected.
    """

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers={
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json",
        },
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code in (401, 403)

    body = response.json()

    assert "routing_masked" not in body
    assert "account_masked" not in body


def test_no_sensitive_information_returned(auth_headers, banking_payload):
    """
    Ensure raw banking details are never returned.
    """

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code == 200

    response_text = response.text

    assert banking_payload["routing_number"] not in response_text
    assert banking_payload["account_number"] not in response_text


def test_banking_token_returned(auth_headers, banking_payload):
    """
    Verify the API returns a banking token.
    """

    response = requests.put(
        f"{BASE_URL}/account/banking",
        headers=auth_headers,
        json=banking_payload,
        timeout=TIMEOUT,
    )

    assert response.status_code == 200

    body = response.json()

    assert "token" in body
    assert body["token"].startswith("btok_")