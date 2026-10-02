from datetime import datetime, timedelta


def test_create_booking(client, auth_headers):
    appointment = (
        datetime.now() + timedelta(days=7)
    ).replace(microsecond=0).isoformat()

    response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "centre_id": 1,
            "test_id": 1,
            "appointment_datetime": appointment,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["centre_id"] == 1
    assert data["test_id"] == 1
    assert data["amount"] == "500.00"
    assert data["status"] == "PENDING"


def test_invalid_booking_requires_auth(client):
    appointment = (
        datetime.now() + timedelta(days=7)
    ).replace(microsecond=0).isoformat()

    response = client.post(
        "/bookings",
        json={
            "centre_id": 1,
            "test_id": 1,
            "appointment_datetime": appointment,
        },
    )

    assert response.status_code in [401, 403]


def test_invalid_centre_or_test(client, auth_headers):
    appointment = (
        datetime.now() + timedelta(days=7)
    ).replace(microsecond=0).isoformat()

    response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "centre_id": 99999,
            "test_id": 1,
            "appointment_datetime": appointment,
        },
    )

    assert response.status_code == 404