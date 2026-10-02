def create_booking(client, auth_headers):
    from datetime import datetime, timedelta

    appointment = (
        datetime.now() + timedelta(days=10)
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
    return response.json()


def test_successful_payment(client, auth_headers):
    booking = create_booking(client, auth_headers)

    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "simulate_success": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["status"] == "SUCCESS"
    assert data["amount"] == "500.00"
    assert "provider_payment_id" in data
    assert data["event_id"] is None


def test_failed_payment(client, auth_headers):
    booking = create_booking(client, auth_headers)

    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "simulate_success": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["status"] == "FAILED"


def test_invalid_payment_booking(client, auth_headers):
    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "booking_id": 99999,
            "simulate_success": True,
        },
    )

    assert response.status_code == 404


def test_payment_webhook(client, auth_headers):
    booking = create_booking(client, auth_headers)

    payment_response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "simulate_success": True,
        },
    )

    assert payment_response.status_code == 201

    payment = payment_response.json()

    # The webhook event ID comes from the payment provider.
    event_id = "evt_test_webhook_001"

    webhook_response = client.post(
        "/payments/webhook",
        json={
            "event_id": event_id,
            "provider_payment_id": payment["provider_payment_id"],
            "status": "SUCCESS",
        },
    )

    assert webhook_response.status_code == 200

    data = webhook_response.json()

    assert data["payment_id"] == payment["id"]
    assert data["booking_id"] == booking["id"]
    assert data["status"] == "SUCCESS"


def test_webhook_idempotency(client, auth_headers):
    booking = create_booking(client, auth_headers)

    payment_response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "simulate_success": True,
        },
    )

    assert payment_response.status_code == 201

    payment = payment_response.json()

    webhook_data = {
        "event_id": "evt_test_idempotency_001",
        "provider_payment_id": payment["provider_payment_id"],
        "status": "SUCCESS",
    }

    # First webhook
    first_response = client.post(
        "/payments/webhook",
        json=webhook_data,
    )

    # Same webhook again
    second_response = client.post(
        "/payments/webhook",
        json=webhook_data,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        second_response.json()["message"]
        == "Webhook already processed"
    )