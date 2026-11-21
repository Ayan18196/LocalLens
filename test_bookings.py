import copy

import pytest
from fastapi.testclient import TestClient

from main import app
from mock_data import bookings

ORIGINAL_BOOKINGS = copy.deepcopy(bookings)

client = TestClient(app)

USER_A = {"Authorization": "Bearer user-a-token"}
USER_B = {"Authorization": "Bearer user-b-token"}
ADMIN = {"Authorization": "Bearer admin-token"}
BAD_TOKEN = {"Authorization": "Bearer wrong-token"}


@pytest.fixture(autouse=True)
def reset_bookings():
    bookings[:] = copy.deepcopy(ORIGINAL_BOOKINGS)
    yield


# ---------- List bookings ----------

def test_user_a_lists_only_own_bookings():
    response = client.get("/api/v1/bookings", headers=USER_A)
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert [b["id"] for b in body["data"]] == [101, 102]
    assert body["meta"] == {"total": 2, "page": 1, "perPage": 10}


def test_user_b_lists_only_own_bookings():
    response = client.get("/api/v1/bookings", headers=USER_B)

    assert response.status_code == 200
    assert [b["id"] for b in response.json()["data"]] == [103, 104]


def test_admin_lists_all_bookings():
    response = client.get("/api/v1/bookings", headers=ADMIN)

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 4


def test_list_pagination():
    response = client.get("/api/v1/bookings?page=2&perPage=1", headers=USER_A)
    body = response.json()

    assert response.status_code == 200
    assert [b["id"] for b in body["data"]] == [102]
    assert body["meta"] == {"total": 2, "page": 2, "perPage": 1}


def test_list_page_past_the_end_is_empty():
    response = client.get("/api/v1/bookings?page=5", headers=USER_A)

    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.parametrize("query", ["page=0", "page=abc", "perPage=0", "perPage=51"])
def test_list_invalid_pagination(query):
    response = client.get(f"/api/v1/bookings?{query}", headers=USER_A)
    body = response.json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_list_without_token():
    response = client.get("/api/v1/bookings")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_list_with_invalid_token():
    response = client.get("/api/v1/bookings", headers=BAD_TOKEN)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


# ---------- View one booking ----------

def test_user_a_views_own_booking():
    response = client.get("/api/v1/bookings/101", headers=USER_A)

    assert response.status_code == 200
    assert response.json()["data"]["id"] == 101


def test_user_a_cannot_view_user_b_booking():
    response = client.get("/api/v1/bookings/103", headers=USER_A)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "BOOKING_FORBIDDEN"


def test_user_b_cannot_view_user_a_booking():
    response = client.get("/api/v1/bookings/101", headers=USER_B)

    assert response.status_code == 403


def test_admin_views_any_booking():
    response = client.get("/api/v1/bookings/103", headers=ADMIN)

    assert response.status_code == 200
    assert response.json()["data"]["ownerId"] == "user-b"


def test_view_missing_booking():
    response = client.get("/api/v1/bookings/999", headers=USER_A)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BOOKING_NOT_FOUND"


@pytest.mark.parametrize("booking_id", ["abc", "0", "-1"])
def test_view_invalid_id(booking_id):
    response = client.get(f"/api/v1/bookings/{booking_id}", headers=USER_A)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_view_without_token():
    response = client.get("/api/v1/bookings/101")

    assert response.status_code == 401


# ---------- Update booking ----------

def test_user_a_updates_own_booking():
    response = client.put("/api/v1/bookings/101", headers=USER_A, json={"slotId": 206})
    body = response.json()

    assert response.status_code == 200
    assert body["data"] == {"id": 101, "slotId": 206, "ownerId": "user-a", "status": "confirmed"}

    # The change is saved.
    saved = client.get("/api/v1/bookings/101", headers=USER_A).json()["data"]
    assert saved["slotId"] == 206


def test_admin_updates_any_booking():
    response = client.put("/api/v1/bookings/103", headers=ADMIN, json={"slotId": 207})

    assert response.status_code == 200
    assert response.json()["data"]["ownerId"] == "user-b"


def test_user_a_cannot_update_user_b_booking():
    response = client.put("/api/v1/bookings/103", headers=USER_A, json={"slotId": 206})

    assert response.status_code == 403
    # The booking did not change.
    assert client.get("/api/v1/bookings/103", headers=ADMIN).json()["data"]["slotId"] == 203


def test_user_b_cannot_update_user_a_booking():
    response = client.put("/api/v1/bookings/101", headers=USER_B, json={"slotId": 206})

    assert response.status_code == 403


def test_update_missing_booking():
    response = client.put("/api/v1/bookings/999", headers=USER_A, json={"slotId": 206})

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload, field",
    [
        ({}, "slotId"),
        ({"slotId": "206"}, "slotId"),
        ({"slotId": 0}, "slotId"),
        ({"slotId": -3}, "slotId"),
        ({"slotId": 2.5}, "slotId"),
        ({"slotId": 206, "ownerId": "user-b"}, "ownerId"),
    ],
)
def test_update_invalid_body(payload, field):
    response = client.put("/api/v1/bookings/101", headers=USER_A, json=payload)
    body = response.json()

    assert response.status_code == 400
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert field in [d["field"] for d in body["error"]["details"]]


def test_update_without_token():
    response = client.put("/api/v1/bookings/101", json={"slotId": 206})

    assert response.status_code == 401


# ---------- Other errors ----------

def test_unsupported_method():
    response = client.patch("/api/v1/bookings/101", headers=USER_A, json={"slotId": 206})

    assert response.status_code == 405
    assert response.json()["success"] is False