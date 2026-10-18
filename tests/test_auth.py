from app.models import User
from conftest import make_user, login


def test_register_user(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert User.query.filter_by(username="alice").first() is not None


def test_duplicate_username(client):
    make_user("alice")

    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "different@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert "already taken" in response.get_data(as_text=True)
    assert User.query.count() == 1


def test_duplicate_email(client):
    client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    response = client.post(
        "/auth/register",
        data={
            "username": "bob",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert "already registered" in response.get_data(as_text=True)


def test_short_password(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@test.com",
            "password": "123",
            "confirm_password": "123",
        },
    )

    assert "at least 8 characters" in response.get_data(as_text=True)


def test_password_mismatch(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "differentpassword",
        },
    )

    assert "Passwords do not match" in response.get_data(as_text=True)


def test_login_success(client):
    make_user("alice")

    response = client.post(
        "/auth/login",
        data={
            "username": "alice",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200


def test_login_failure(client):
    make_user("alice")

    response = client.post(
        "/auth/login",
        data={
            "username": "alice",
            "password": "wrongpassword",
        },
    )

    assert "Invalid username or password" in response.get_data(as_text=True)


def test_logout(client):
    make_user("alice")
    login(client, "alice")

    response = client.get(
        "/auth/logout",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "logged out" in response.get_data(as_text=True)


def test_profile_requires_login(client):
    response = client.get("/auth/profile")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]