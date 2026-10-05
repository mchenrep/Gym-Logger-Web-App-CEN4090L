"""Shared test setup: a fresh in-memory database for every test, plus helpers to log in."""
import pytest

from app import create_app, db
from app.models import User, Exercise


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",  # in-memory, so workout.db is never touched
    })
    with app.app_context():
        db.session.add_all([
            Exercise(name="Barbell Bench Press", category="Barbell", muscle_group="Chest"),
            Exercise(name="Overhead Press", category="Barbell", muscle_group="Shoulders"),
            Exercise(name="Tricep Pushdown", category="Cable", muscle_group="Triceps"),
        ])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(username):
    user = User(username=username, email=f"{username}@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username):
    return client.post("/auth/login", data={"username": username, "password": "password123"})


def exercise_id(name):
    return Exercise.query.filter_by(name=name).first().id
