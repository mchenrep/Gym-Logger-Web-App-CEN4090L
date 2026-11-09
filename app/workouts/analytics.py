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
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app import db
from app.models import Exercise, SetEntry, WorkoutSession


def _user_sets():
    """Base query: every SetEntry joined to its session (callers add the user_id filter)."""
    return db.session.query(SetEntry).join(WorkoutSession, SetEntry.session_id == WorkoutSession.id)


def total_volume(user_id):
    """Total weight lifted ever (sum of weight * reps over all sets). Returns a float (0.0 if none)."""
    total = (
        db.session.query(func.coalesce(func.sum(SetEntry.weight * SetEntry.reps), 0))
        .join(WorkoutSession, SetEntry.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .scalar()
    )
    return float(total)


def volume_per_workout(user_id):
    """Volume for each workout, oldest -> newest.
    Returns a list of (WorkoutSession, volume_float) tuples."""
    rows = (
        db.session.query(
            WorkoutSession, func.coalesce(func.sum(SetEntry.weight * SetEntry.reps), 0)
        )
        .outerjoin(SetEntry, SetEntry.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .group_by(WorkoutSession.id)
        .order_by(WorkoutSession.date.asc(), WorkoutSession.id.asc())
        .all()
    )
    return [(session, float(volume)) for session, volume in rows]


def workouts_per_week(user_id, weeks=8):
    """Workouts logged in each of the last `weeks` weeks, oldest -> newest, INCLUDING weeks with 0.
    Returns a list of (week_start_date, count) tuples. Weeks start on Monday."""
    today = datetime.now(timezone.utc).date()  # session dates are stored as naive UTC
    this_monday = today - timedelta(days=today.weekday())
    week_starts = [this_monday - timedelta(weeks=i) for i in range(weeks - 1, -1, -1)]
    counts = {start: 0 for start in week_starts}

    first_day = datetime.combine(week_starts[0], datetime.min.time())
    dates = (
        db.session.query(WorkoutSession.date)
        .filter(WorkoutSession.user_id == user_id, WorkoutSession.date >= first_day)
        .all()
    )
    for (when,) in dates:
        day = when.date()
        monday = day - timedelta(days=day.weekday())
        if monday in counts:  # ignore anything dated in the future
            counts[monday] += 1
    return [(start, counts[start]) for start in week_starts]


def sets_by_muscle_group(user_id):
    """How many sets the user has done per muscle group, most-trained first.
    Returns a list of (muscle_group_name, set_count) tuples."""
    set_count = func.count(SetEntry.id)
    rows = (
        db.session.query(Exercise.muscle_group, set_count)
        .join(SetEntry, SetEntry.exercise_id == Exercise.id)
        .join(WorkoutSession, SetEntry.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .group_by(Exercise.muscle_group)
        .order_by(set_count.desc(), Exercise.muscle_group.asc())
        .all()
    )
    return [(group, count) for group, count in rows]


def personal_records(user_id):
    """Heaviest set ever for each exercise the user has logged (ties: more reps wins).
    Returns a list of (Exercise, SetEntry) tuples, sorted by exercise name."""
    rows = (
        db.session.query(Exercise, SetEntry)
        .join(SetEntry, SetEntry.exercise_id == Exercise.id)
        .join(WorkoutSession, SetEntry.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .order_by(Exercise.name.asc(), SetEntry.weight.desc(), SetEntry.reps.desc(), SetEntry.id.asc())
        .all()
    )
    best = {}
    for exercise, set_entry in rows:
        best.setdefault(exercise.id, (exercise, set_entry))  # first row per exercise is its best
    return list(best.values())


def personal_record(user_id, exercise_id):
    """The single best SetEntry for one exercise, or None if never logged. (Used by Mawi's detail page.)"""
    return (
        _user_sets()
        .filter(WorkoutSession.user_id == user_id, SetEntry.exercise_id == exercise_id)
        .order_by(SetEntry.weight.desc(), SetEntry.reps.desc(), SetEntry.id.asc())
        .first()
    )


def exercise_history(user_id, exercise_id, limit=10):
    """The user's most recent sets for one exercise, newest first.
    Returns a list of (WorkoutSession, SetEntry) tuples. (Used by Mawi's detail page.)"""
    rows = (
        db.session.query(WorkoutSession, SetEntry)
        .join(SetEntry, SetEntry.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id, SetEntry.exercise_id == exercise_id)
        .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc(), SetEntry.id.desc())
        .limit(limit)
        .all()
    )
    return [(session, set_entry) for session, set_entry in rows]

