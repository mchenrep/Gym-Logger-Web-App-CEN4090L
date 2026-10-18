"""
    Script to fill the exercise library with starter exercises.
    NOTE: it's safe to run more than once (skips exercises that already exist)
    To run: python3 seed.py
"""
from app import create_app, db
from app.models import Exercise

# INCREMENT 2 (owner: John) - TODO:
#   1. Grow this list to ~40-50 exercises covering every muscle group (Chest, Back, Shoulders,
#      Biceps, Triceps, Legs, Core, Glutes, Calves, Full Body) and every category (Barbell,
#      Dumbbell, Cable, Machine, Bodyweight, Cardio).
#   2. Fix a data bug: "Lat Pulldown" is filed under "Dumbbell" - it's a Cable/Machine exercise.
#   3. The loop at the bottom skips existing names, so fixes to existing rows never apply to a
#      database that was already seeded. Make it UPDATE category/muscle_group when the name exists.
#   4. Keep category / muscle group spelling consistent (they feed the library dropdown filters).
#   5. Keep it safe to run more than once. Tests: tests/test_seed.py (Hector).
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
