"""Shared test setup: a fresh in-memory database for every test, plus helpers to log in."""
import pytest
from pandas.core.indexes import category

from app import create_app, db
from app.models import User, Exercise


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",  # in-memory, so workout.db is never touched
    })
    with app.app_context():
        #The tests were failing, so I Added the missing exercises(Hector)
        db.session.add_all([
            #Chest workouts
            Exercise(name="Barbell Bench Press", category="Barbell", muscle_group="Chest"),
            Exercise(name="Incline Barbell Bench Press", category="Barbell", muscle_group="Chest"),
            Exercise(name="Dumbbell Bench Press", category="Dumbbell", muscle_group="Chest"),
            Exercise(name="Incline Dumbbell Fly", category="Dumbbell", muscle_group="Chest"),
            Exercise(name="Cable Chest Fly", category="Cable", muscle_group="Chest"),
            Exercise(name="Chest Press Machine", category="Machine", muscle_group="Chest"),
            Exercise(name="Push-Up", category="Bodyweight", muscle_group="Chest"),
            #Shoulder workouts
            Exercise(name="Overhead Press", category="Barbell", muscle_group="Shoulders"),
            Exercise(name="Dumbbell Shoulder Press", category="Dumbbell", muscle_group="Shoulders"),
            Exercise(name="Dumbbell Lateral Raise", category="Dumbbell", muscle_group="Shoulders"),
            Exercise(name="Cable Lateral Raise", category="Cable", muscle_group="Shoulders"),
            Exercise(name="Shoulder Press Machine", category="Machine", muscle_group="Shoulders"),
            #Tricep workouts
            Exercise(name="Tricep Pushdown", category="Cable", muscle_group="Triceps"),
            Exercise(name="Tricep Extension Machine", category="Machine", muscle_group="Triceps"),
            Exercise(name="Bench Dip", category="Bodyweight", muscle_group="Triceps"),
            Exercise(name="Close-Grip Bench Press", category="Barbell", muscle_group="Triceps"),
            Exercise(name="Overhead Dumbbell Extension", category="Dumbbell", muscle_group="Triceps"),
            #bicep workouts
            Exercise(name="Dumbbell Curl", category="Dumbbell", muscle_group="Biceps"),
            Exercise(name="Barbell Curl", category="Barbell", muscle_group="Biceps"),
            Exercise(name="Hammer Curl",  category="Dumbbell", muscle_group="Biceps"),
            Exercise(name="Cable Bicep Curl",  category="Cable", muscle_group="Biceps"),
            Exercise(name="Preacher Curl Machine",  category="Machine", muscle_group="Biceps"),
            #back workouts
            Exercise(name="Deadlift", category="Barbell", muscle_group="Back"),
            Exercise(name="Pull-Up", category="Bodyweight" ,muscle_group="Back"),
            Exercise(name="Barbell Row", category="Barbell", muscle_group="Back"),
            Exercise(name="Lat Pulldown", category="Cable", muscle_group="Back"),
            Exercise(name="Dumbbell Row", category="Dumbbell", muscle_group="Back"),
            Exercise(name="Seated Cable Row", category="Cable", muscle_group="Back"),
            Exercise(name="Assisted Pull-Up", category="Machine", muscle_group="Back"),
            #Full-body workouts
            Exercise(name="Burpee", category="Bodyweight", muscle_group="Full Body"),
            Exercise(name="Treadmill Run", category="Cardio", muscle_group="Full Body"),
            Exercise(name="Jump Rope", category="Cardio", muscle_group="Full Body"),
            Exercise(name="Rowing Machine", category="Cardio", muscle_group="Full Body"),
            #leg workouts
            Exercise(name="Stationary Bike", category="Cardio", muscle_group="Legs"),
            Exercise(name="Barbell Back Squat", category="Barbell", muscle_group="Legs"),
            Exercise(name="Front Squat", category="Barbell", muscle_group="Legs"),
            Exercise(name="Dumbbell Lunges", category="Dumbbell", muscle_group="Legs"),
            Exercise(name="Leg Press", category="Machine", muscle_group="Legs"),
            Exercise(name="Leg Extension", category="Machine", muscle_group="Legs"),
            Exercise(name="Leg Curl", category="Machine", muscle_group="Legs"),
            # CORE
            Exercise(name="Crunch", category="Bodyweight", muscle_group="Core"),
            Exercise(name="Plank", category="Bodyweight", muscle_group="Core"),
            Exercise(name="Cable Crunch", category="Cable", muscle_group="Core"),
            Exercise(name="Ab Crunch Machine", category="Machine", muscle_group="Core"),
            # GLUTES
            Exercise(name="Barbell Hip Thrust", category="Barbell", muscle_group="Glutes"),
            Exercise(name="Dumbbell Glute Bridge", category="Dumbbell", muscle_group="Glutes"),
            Exercise(name="Cable Kickback", category="Cable", muscle_group="Glutes"),
            # CALVES
            Exercise(name="Standing Calf Raise", category="Machine", muscle_group="Calves"),
            Exercise(name="Seated Calf Raise", category="Machine", muscle_group="Calves"),
            Exercise(name="Dumbbell Calf Raise", category="Dumbbell", muscle_group="Calves"),

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
