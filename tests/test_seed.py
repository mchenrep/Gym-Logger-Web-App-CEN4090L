# tests/test_seed.py // HectorM

from app.models import Exercise


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