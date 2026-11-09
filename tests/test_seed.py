# tests/test_seed.py // HectorM

from app.models import Exercise

from app import db
from seed import seed_exercises


def test_seed_contains_exercises(client):
    assert Exercise.query.count() > 0


def test_seed_contains_barbell_bench_press(client):
    exercise = Exercise.query.filter_by(
        name="Barbell Bench Press"
    ).first()

    assert exercise is not None
    assert exercise.category == "Barbell"
    assert exercise.muscle_group == "Chest"


def test_seed_contains_overhead_press(client):
    exercise = Exercise.query.filter_by(
        name="Overhead Press"
    ).first()

    assert exercise is not None
    assert exercise.category == "Barbell"
    assert exercise.muscle_group == "Shoulders"


def test_seed_contains_cardio_exercise(client):
    exercise = Exercise.query.filter_by(
        name="Treadmill Run"
    ).first()

    assert exercise is not None
    assert exercise.category == "Cardio"
    assert exercise.muscle_group == "Full Body"


def test_seed_contains_multiple_categories(client):
    categories = {
        exercise.category
        for exercise in Exercise.query.all()
    }

    assert "Barbell" in categories
    assert "Bodyweight" in categories
    assert "Cable" in categories
    assert "Cardio" in categories


# More seed tests - John


def test_seed_adds_all_exercises(client):
    seed_exercises()

    assert Exercise.query.count() == 50


def test_seed_updates_existing_exercises(client):
    # Simulate an incorrect existing database record.
    exercise = Exercise.query.filter_by(name="Lat Pulldown").first()

    exercise.category = "Dumbbell"
    db.session.commit()

    seed_exercises()

    exercise = Exercise.query.filter_by(name="Lat Pulldown").first()

    assert exercise.category == "Cable"
    assert exercise.muscle_group == "Back"


def test_seed_is_safe_to_run_twice(client):
    seed_exercises()

    first_count = Exercise.query.count()

    seed_exercises()

    second_count = Exercise.query.count()

    assert first_count == second_count
    assert second_count == 50
