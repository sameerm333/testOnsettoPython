import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TIMEOUT = 30


def test_auth_token_success():
    """
    Verify valid username/password returns an MFA token.
    """

    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL"),
            "password": os.getenv("PASSWORD")
        },
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    # Contract validation
    assert body["mfa_required"] is True
    assert isinstance(body["mfa_token"], str)
    assert len(body["mfa_token"]) > 0
    assert "message" in body

    # Security validation
    assert "access_token" not in body
    assert "refresh_token" not in body
    assert "password" not in body


def test_auth_token_invalid_password():
    """
    Verify invalid password is rejected.
    """

    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL"),
            "password": "WrongPassword123"
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 401)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )

    # Never leak MFA token
    assert "mfa_token" not in body


def test_auth_token_missing_email():
    """
    Verify email is mandatory.
    """

    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "password": os.getenv("PASSWORD")
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_auth_token_missing_password():
    """
    Verify password is mandatory.
    """

    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL")
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


def test_verify_mfa_success():
    """
    Verify MFA step returns bearer token.
    """

    # Step 1
    token_response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL"),
            "password": os.getenv("PASSWORD")
        },
        timeout=TIMEOUT
    )

    assert token_response.status_code == 200

    mfa_token = token_response.json()["mfa_token"]

    # Step 2
    response = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "mfa_token": mfa_token,
            "code": os.getenv("MFA_CODE")
        },
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    body = response.json()

    # Contract validation
    assert "access_token" in body
    assert body["access_token"] != ""

    assert body["token_type"] == "Bearer"
    assert body["expires_in"] > 0
    assert "refresh_token" in body

    # Security
    assert "password" not in body
    assert "mfa_token" not in body


def test_verify_invalid_mfa_code():
    """
    Verify invalid MFA code is rejected.
    """

    token_response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL"),
            "password": os.getenv("PASSWORD")
        },
        timeout=TIMEOUT
    )

    assert token_response.status_code == 200

    mfa_token = token_response.json()["mfa_token"]

    response = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "mfa_token": mfa_token,
            "code": "9999"
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 401, 403)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )

    assert "access_token" not in body


def test_verify_missing_mfa_token():
    """
    Verify MFA token is mandatory.
    """

    response = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "code": os.getenv("MFA_CODE")
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 422)

    body = response.json()

    assert any(
        key in body
        for key in ("message", "error", "errors")
    )


@pytest.mark.parametrize(
    "code",
    [
        "",
        "12",
        "abcd",
        "0000"
    ]
)
def test_invalid_mfa_formats(code):
    """
    Verify invalid MFA formats are rejected.
    """

    token_response = requests.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": os.getenv("EMAIL"),
            "password": os.getenv("PASSWORD")
        },
        timeout=TIMEOUT
    )

    mfa_token = token_response.json()["mfa_token"]

    response = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "mfa_token": mfa_token,
            "code": code
        },
        timeout=TIMEOUT
    )

    assert response.status_code in (400, 401, 403, 422)