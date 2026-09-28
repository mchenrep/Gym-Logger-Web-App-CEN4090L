"""
    Script to fill the exercise library with starter exercises.
    NOTE: it's safe to run more than once (skips exercises that already exist)
    To run: python3 seed.py
"""
from app import create_app, db
from app.models import Exercise

EXERCISES = [
    # (name, category, muscle_group)
    ("Barbell Back Squat", "Barbell", "Legs"),
    ("Deadlift", "Barbell", "Back"),
    ("Barbell Bench Press", "Barbell", "Chest"),
    ("Overhead Press", "Barbell", "Shoulders"),
    ("Pull-Up", "Bodyweight", "Back"),
    ("Barbell Row", "Barbell", "Back"),
    ("Lat Pulldown", "Dumbbell", "Back"),
    ("Dumbbell Curl", "Dumbbell", "Biceps"),
    ("Tricep Pushdown", "Cable", "Triceps"),
    ("Treadmill Run", "Cardio", "Full Body"),
    ("Stationary Bike", "Cardio", "Legs"),
]

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        added = 0
        for name, category, muscle_group in EXERCISES:
            if not Exercise.query.filter_by(name=name).first():
                db.session.add(Exercise(name=name, category=category, muscle_group=muscle_group))
                added += 1
        db.session.commit()
        print(f"Added {added} exercises ({len(EXERCISES) - added} already existed).")
