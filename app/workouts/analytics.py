"""WORKOUT ANALYTICS ("EDA")  --  Increment 2, owner: John

Pure functions that turn a user's logged sets into numbers for the Stats page.
Keep them free of Flask/request code so they are easy to test (Hector: tests/test_analytics.py).
Every function takes `user_id` and must only ever look at THAT user's data.

Reused by:
  - workouts/stats.html via stats()       (John)
  - the dashboard "Quick Analytics" card  (Matthew)
  - the exercise detail page              (Mawi, uses exercise_history + personal_record)

Useful query shape: join SetEntry -> WorkoutSession and filter on WorkoutSession.user_id.
Volume of a set = weight * reps.

Delete the NotImplementedError lines as you implement each function; keep the signatures
(and return shapes in the docstrings) stable so the other pages don't break.
"""
from app import db  # noqa: F401
from app.models import Exercise, SetEntry, WorkoutSession  # noqa: F401


def total_volume(user_id):
    """Total weight lifted ever (sum of weight * reps over all sets). Returns a float (0.0 if none)."""
    raise NotImplementedError("TODO (John)")


def volume_per_workout(user_id):
    """Volume for each workout, oldest -> newest.
    Returns a list of (WorkoutSession, volume_float) tuples."""
    raise NotImplementedError("TODO (John)")


def workouts_per_week(user_id, weeks=8):
    """Workouts logged in each of the last `weeks` weeks, oldest -> newest, INCLUDING weeks with 0.
    Returns a list of (week_start_date, count) tuples."""
    raise NotImplementedError("TODO (John)")


def sets_by_muscle_group(user_id):
    """How many sets the user has done per muscle group, most-trained first.
    Returns a list of (muscle_group_name, set_count) tuples."""
    raise NotImplementedError("TODO (John)")


def personal_records(user_id):
    """Heaviest set ever for each exercise the user has logged (ties: more reps wins).
    Returns a list of (Exercise, SetEntry) tuples, sorted by exercise name."""
    raise NotImplementedError("TODO (John)")


def personal_record(user_id, exercise_id):
    """The single best SetEntry for one exercise, or None if never logged. (Used by Mawi's detail page.)"""
    raise NotImplementedError("TODO (John)")


def exercise_history(user_id, exercise_id, limit=10):
    """The user's most recent sets for one exercise, newest first.
    Returns a list of (WorkoutSession, SetEntry) tuples. (Used by Mawi's detail page.)"""
    raise NotImplementedError("TODO (John)")
