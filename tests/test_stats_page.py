"""Tests for the /workouts/stats page and the analytics helpers behind it."""
from datetime import datetime, timedelta, timezone

from app import db
from app.models import SetEntry, WorkoutSession
from app.workouts import analytics
from tests.conftest import exercise_id, login, make_user


def add_session(user, days_ago=0, sets=()):
    """Create a session `days_ago` days back with sets given as (exercise name, weight, reps)."""
    when = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days_ago)
    session = WorkoutSession(user_id=user.id, date=when)
    db.session.add(session)
    db.session.commit()
    for number, (name, weight, reps) in enumerate(sets, start=1):
        db.session.add(SetEntry(
            session_id=session.id, exercise_id=exercise_id(name),
            set_number=number, weight=weight, reps=reps,
        ))
    db.session.commit()
    return session


# ---------- page ----------

def test_stats_requires_login(client):
    response = client.get("/workouts/stats")
    assert response.status_code == 302


def test_stats_empty_state_for_new_user(client):
    make_user("alice")
    login(client, "alice")

    response = client.get("/workouts/stats")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "No stats yet" in body
    assert "Personal Records" not in body


def test_stats_with_workouts_but_no_sets_does_not_crash(client):
    user = make_user("alice")
    add_session(user)
    login(client, "alice")

    response = client.get("/workouts/stats")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "No stats yet" not in body
    assert "No sets logged yet" in body


def test_stats_page_shows_all_cards_for_user_with_data(client):
    user = make_user("alice")
    add_session(user, days_ago=8, sets=[("Barbell Bench Press", 100, 5)])
    add_session(user, days_ago=0, sets=[
        ("Barbell Bench Press", 135, 5),
        ("Overhead Press", 65, 8),
    ])
    login(client, "alice")

    response = client.get("/workouts/stats")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Total Volume" in body
    assert "1,695 lbs" in body            # 100*5 + 135*5 + 65*8
    assert "Workouts per Week" in body
    assert "Sets per Muscle Group" in body
    assert "Chest" in body and "Shoulders" in body
    assert "Personal Records" in body
    assert "Barbell Bench Press" in body and "135" in body


def test_stats_only_show_my_own_data(client):
    alice = make_user("alice")
    bob = make_user("bob")
    add_session(alice, sets=[("Barbell Bench Press", 100, 5)])
    add_session(bob, sets=[("Tricep Pushdown", 999, 1)])
    login(client, "alice")

    body = client.get("/workouts/stats").get_data(as_text=True)
    assert "Tricep Pushdown" not in body
    assert "999" not in body


# ---------- helpers ----------

def test_total_volume(app):
    user = make_user("alice")
    assert analytics.total_volume(user.id) == 0.0
    add_session(user, sets=[("Barbell Bench Press", 100, 5), ("Overhead Press", 50, 10)])
    assert analytics.total_volume(user.id) == 1000.0


def test_volume_per_workout_oldest_first_includes_empty_sessions(app):
    user = make_user("alice")
    newer = add_session(user, days_ago=1, sets=[("Barbell Bench Press", 100, 5)])
    older = add_session(user, days_ago=5)  # no sets
    result = analytics.volume_per_workout(user.id)
    assert [(s.id, v) for s, v in result] == [(older.id, 0.0), (newer.id, 500.0)]


def test_workouts_per_week_includes_zero_weeks(app):
    user = make_user("alice")
    add_session(user, days_ago=0)
    add_session(user, days_ago=0)
    add_session(user, days_ago=21)

    weeks = analytics.workouts_per_week(user.id, weeks=8)
    assert len(weeks) == 8
    assert weeks == sorted(weeks)                      # oldest -> newest
    assert all(start.weekday() == 0 for start, _ in weeks)  # Mondays
    assert weeks[-1][1] == 2                           # this week
    assert sum(count for _, count in weeks) == 3
    assert sum(1 for _, count in weeks if count == 0) == 6


def test_workouts_per_week_ignores_sessions_older_than_window(app):
    user = make_user("alice")
    add_session(user, days_ago=200)
    assert sum(count for _, count in analytics.workouts_per_week(user.id)) == 0


def test_sets_by_muscle_group_most_trained_first(app):
    user = make_user("alice")
    add_session(user, sets=[
        ("Overhead Press", 65, 8), ("Barbell Bench Press", 100, 5), ("Barbell Bench Press", 100, 5),
    ])
    assert analytics.sets_by_muscle_group(user.id) == [("Chest", 2), ("Shoulders", 1)]


def test_personal_records_heaviest_wins_and_ties_go_to_more_reps(app):
    user = make_user("alice")
    add_session(user, days_ago=3, sets=[("Barbell Bench Press", 135, 5), ("Overhead Press", 60, 5)])
    add_session(user, days_ago=1, sets=[("Barbell Bench Press", 135, 8), ("Overhead Press", 65, 3)])

    records = analytics.personal_records(user.id)
    assert [(ex.name, s.weight, s.reps) for ex, s in records] == [
        ("Barbell Bench Press", 135, 8),
        ("Overhead Press", 65, 3),
    ]


def test_personal_record_and_exercise_history(app):
    user = make_user("alice")
    other = make_user("bob")
    bench = exercise_id("Barbell Bench Press")
    assert analytics.personal_record(user.id, bench) is None

    older = add_session(user, days_ago=4, sets=[("Barbell Bench Press", 150, 1)])
    newer = add_session(user, days_ago=1, sets=[("Barbell Bench Press", 100, 5)])
    add_session(other, sets=[("Barbell Bench Press", 300, 1)])

    assert analytics.personal_record(user.id, bench).weight == 150
    history = analytics.exercise_history(user.id, bench)
    assert [(s.id, e.weight) for s, e in history] == [(newer.id, 100), (older.id, 150)]
    assert len(analytics.exercise_history(user.id, bench, limit=1)) == 1
