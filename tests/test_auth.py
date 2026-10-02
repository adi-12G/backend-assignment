def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"


def test_login(client):
    client.post(
        "/auth/signup",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "Password@123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "bob@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"