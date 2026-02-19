#!/usr/bin/env python3
"""
Test script for user authentication and user API endpoints.

Usage:
  cd backend
  pip install requests   # if not already installed
  uvicorn main:app --reload   # in another terminal
  python scripts/test_user_auth_api.py

Override base URL: BASE_URL=http://127.0.0.1:8000 python scripts/test_user_auth_api.py
"""
import os
import sys

import requests

# Configure base URL (no trailing slash)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

# Test user data (Ivorian phone format +225XXXXXXXX)
TEST_PHONE = "+22507000001"
TEST_PASSWORD = "TestPass123"
TEST_FULL_NAME = "Test User"
TEST_EMAIL = "testuser@example.com"

# Second user for list/get/update/delete tests
TEST_PHONE_2 = "+22507000002"
TEST_PASSWORD_2 = "SecondUser99"


def url(path: str) -> str:
    return f"{BASE_URL}{API_PREFIX}{path}"


def run(name: str, ok: bool, detail: str = ""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
    return ok


def main():
    print("=" * 60)
    print("User Auth & User API Test Script")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}\n")

    all_ok = True

    # --- Health check ---
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        run("Health check", r.status_code == 200)
        if r.status_code != 200:
            print("  Backend not responding. Start with: uvicorn main:app --reload")
            sys.exit(1)
    except requests.RequestException as e:
        run("Health check", False, str(e))
        print("  Start the backend first: uvicorn main:app --reload")
        sys.exit(1)

    # --- Auth: Register ---
    print("\n--- Auth: Register ---")
    register_payload = {
        "phone": TEST_PHONE,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
        "email": TEST_EMAIL,
    }
    r = requests.post(url("/auth/register"), json=register_payload, timeout=10)
    if r.status_code == 201:
        run("POST /auth/register (new user)", True)
        user1 = r.json()
        user1_id = user1.get("id")
    elif r.status_code == 400 and "already registered" in (r.json().get("detail") or "").lower():
        run("POST /auth/register (already exists)", True, "user exists, continuing")
        # Get token via login to fetch user id
        r2 = requests.post(
            url("/auth/login"),
            data={"username": TEST_PHONE, "password": TEST_PASSWORD},
            timeout=10,
        )
        if r2.status_code == 200:
            # Get me to retrieve id
            token = r2.json().get("access_token")
            r3 = requests.get(url("/users/me"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
            user1_id = r3.json().get("id") if r3.status_code == 200 else None
        else:
            user1_id = None
    else:
        run("POST /auth/register", False, f"{r.status_code} {r.text[:200]}")
        user1_id = None
        all_ok = False

    # --- Auth: Duplicate register (expect 400) ---
    r = requests.post(url("/auth/register"), json=register_payload, timeout=10)
    all_ok &= run("POST /auth/register (duplicate → 400)", r.status_code == 400)

    # --- Auth: Login ---
    print("\n--- Auth: Login ---")
    r = requests.post(
        url("/auth/login"),
        data={"username": TEST_PHONE, "password": TEST_PASSWORD},
        timeout=10,
    )
    if r.status_code != 200:
        run("POST /auth/login", False, f"{r.status_code} {r.text[:200]}")
        all_ok = False
        token = None
    else:
        run("POST /auth/login", True)
        token = r.json().get("access_token")

    # --- Auth: Wrong password (expect 401) ---
    r = requests.post(
        url("/auth/login"),
        data={"username": TEST_PHONE, "password": "WrongPassword1"},
        timeout=10,
    )
    all_ok &= run("POST /auth/login (wrong password → 401)", r.status_code == 401)

    if not token:
        print("\nSkipping user API tests (no token).")
        print("=" * 60)
        sys.exit(1 if not all_ok else 0)

    headers = {"Authorization": f"Bearer {token}"}

    # --- User API: Get me ---
    print("\n--- User API: Current user ---")
    r = requests.get(url("/users/me"), headers=headers, timeout=10)
    all_ok &= run("GET /users/me", r.status_code == 200)
    if r.status_code == 200 and not user1_id:
        user1_id = r.json().get("id")

    # --- User API: Update me ---
    r = requests.put(
        url("/users/me"),
        json={"full_name": "Test User Updated"},
        headers=headers,
        timeout=10,
    )
    all_ok &= run("PUT /users/me", r.status_code == 200)

    # --- User API: List users (expect 403 unless superuser) ---
    print("\n--- User API: List / Get / Update / Delete (superuser) ---")
    r = requests.get(url("/users/"), headers=headers, timeout=10)
    is_superuser = r.status_code == 200
    run("GET /users/ (list)", r.status_code in (200, 403), "403 = normal user, 200 = superuser")

    if is_superuser and user1_id:
        r = requests.get(url(f"/users/{user1_id}"), headers=headers, timeout=10)
        all_ok &= run("GET /users/{id}", r.status_code == 200)

        r = requests.put(
            url(f"/users/{user1_id}"),
            json={"full_name": "Updated by admin"},
            headers=headers,
            timeout=10,
        )
        all_ok &= run("PUT /users/{id}", r.status_code == 200)

        # Create a second user to delete (avoid deleting main test user)
        r2 = requests.post(url("/auth/register"), json={
            "phone": TEST_PHONE_2,
            "password": TEST_PASSWORD_2,
            "full_name": "To Delete",
        }, timeout=10)
        if r2.status_code in (201, 400):
            r3 = requests.post(url("/auth/login"), data={"username": TEST_PHONE_2, "password": TEST_PASSWORD_2}, timeout=10)
            if r3.status_code == 200:
                uid2 = r3.json().get("user_id")
                if not uid2:
                    r4 = requests.get(url("/users/me"), headers={"Authorization": f"Bearer {r3.json().get('access_token')}"}, timeout=10)
                    uid2 = r4.json().get("id") if r4.status_code == 200 else None
                if uid2:
                    r_del = requests.delete(url(f"/users/{uid2}"), headers=headers, timeout=10)
                    all_ok &= run("DELETE /users/{id}", r_del.status_code == 204)
    else:
        run("GET /users/{id}", True, "skipped (not superuser)")
        run("PUT /users/{id}", True, "skipped (not superuser)")
        run("DELETE /users/{id}", True, "skipped (not superuser)")

    # --- Unauthorized access (no token) ---
    print("\n--- Security ---")
    r = requests.get(url("/users/me"), timeout=10)
    all_ok &= run("GET /users/me (no token → 401)", r.status_code == 401)

    print("\n" + "=" * 60)
    print("PASS" if all_ok else "FAIL")
    print("=" * 60)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
