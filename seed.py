
"""
Script to fill the exercise library with starter exercises.

Safe to run multiple times:
- Adds exercises that do not exist.
- Updates the category and muscle group of existing exercises.

To run: python3 seed.py
"""

from app import create_app, db
from app.models import Exercise


# (name, category, muscle_group)
EXERCISES = [
    # CHEST
    ("Barbell Bench Press", "Barbell", "Chest"),
    ("Incline Barbell Bench Press", "Barbell", "Chest"),
    ("Dumbbell Bench Press", "Dumbbell", "Chest"),
    ("Incline Dumbbell Fly", "Dumbbell", "Chest"),
    ("Cable Chest Fly", "Cable", "Chest"),
    ("Chest Press Machine", "Machine", "Chest"),
    ("Push-Up", "Bodyweight", "Chest"),

    # BACK
    ("Deadlift", "Barbell", "Back"),
    ("Barbell Row", "Barbell", "Back"),
    ("Dumbbell Row", "Dumbbell", "Back"),
    ("Lat Pulldown", "Cable", "Back"),
    ("Seated Cable Row", "Cable", "Back"),
    ("Assisted Pull-Up", "Machine", "Back"),
    ("Pull-Up", "Bodyweight", "Back"),

    # SHOULDERS
    ("Overhead Press", "Barbell", "Shoulders"),
    ("Dumbbell Shoulder Press", "Dumbbell", "Shoulders"),
    ("Dumbbell Lateral Raise", "Dumbbell", "Shoulders"),
    ("Cable Lateral Raise", "Cable", "Shoulders"),
    ("Shoulder Press Machine", "Machine", "Shoulders"),

    # BICEPS
    ("Barbell Curl", "Barbell", "Biceps"),
    ("Dumbbell Curl", "Dumbbell", "Biceps"),
    ("Hammer Curl", "Dumbbell", "Biceps"),
    ("Cable Bicep Curl", "Cable", "Biceps"),
    ("Preacher Curl Machine", "Machine", "Biceps"),

    # TRICEPS
    ("Close-Grip Bench Press", "Barbell", "Triceps"),
    ("Overhead Dumbbell Extension", "Dumbbell", "Triceps"),
    ("Tricep Pushdown", "Cable", "Triceps"),
    ("Tricep Extension Machine", "Machine", "Triceps"),
    ("Bench Dip", "Bodyweight", "Triceps"),

    # LEGS
    ("Barbell Back Squat", "Barbell", "Legs"),
    ("Front Squat", "Barbell", "Legs"),
    ("Dumbbell Lunges", "Dumbbell", "Legs"),
    ("Leg Press", "Machine", "Legs"),
    ("Leg Extension", "Machine", "Legs"),
    ("Leg Curl", "Machine", "Legs"),

    # CORE
    ("Crunch", "Bodyweight", "Core"),
    ("Plank", "Bodyweight", "Core"),
    ("Cable Crunch", "Cable", "Core"),
    ("Ab Crunch Machine", "Machine", "Core"),

    # GLUTES
    ("Barbell Hip Thrust", "Barbell", "Glutes"),
    ("Dumbbell Glute Bridge", "Dumbbell", "Glutes"),
    ("Cable Kickback", "Cable", "Glutes"),

    # CALVES
    ("Standing Calf Raise", "Machine", "Calves"),
    ("Seated Calf Raise", "Machine", "Calves"),
    ("Dumbbell Calf Raise", "Dumbbell", "Calves"),

    # FULL BODY
    ("Burpee", "Bodyweight", "Full Body"),
    ("Treadmill Run", "Cardio", "Full Body"),
    ("Jump Rope", "Cardio", "Full Body"),
    ("Rowing Machine", "Cardio", "Full Body"),
    ("Stationary Bike", "Cardio", "Legs"),
]


def seed_exercises():
    """Add new exercises and update existing exercise classifications."""
    added = 0
    updated = 0

    for name, category, muscle_group in EXERCISES:
        exercise = Exercise.query.filter_by(name=name).first()

        if exercise is None:
            exercise = Exercise(
                name=name,
                category=category,
                muscle_group=muscle_group,
            )
            db.session.add(exercise)
            added += 1
        else:
            # Update existing records so corrections reach older databases.
            if (
                exercise.category != category
                or exercise.muscle_group != muscle_group
            ):
                exercise.category = category
                exercise.muscle_group = muscle_group
                updated += 1

    db.session.commit()

    return added, updated


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        added, updated = seed_exercises()

        print(
            f"Seed complete: {added} added, "
            f"{updated} updated, "
            f"{len(EXERCISES)} exercises checked."
        )

