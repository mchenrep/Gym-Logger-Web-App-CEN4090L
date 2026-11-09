from datetime import datetime, timedelta, timezone



from app import db
from app.models import User, Exercise, WorkoutSession, SetEntry
from app.workouts.analytics import (
    total_volume,
    exercise_history,
    personal_record,
    personal_records,
    sets_by_muscle_group,
    volume_per_workout,
    workouts_per_week
)

from conftest import exercise_id, make_user


#testing the volume of how much weight pushed
def test_total_volume_user_specific(client):
    #creating 2 users
    timmy = User(username="timmy",email="timmy@example.com")
    timmy.set_password("password123")

    bob = User(username="bob", email="bob@example.com")
    bob.set_password("1234password")

    db.session.add_all([timmy,bob])
    db.session.commit()

    bench = Exercise.query.filter_by(name="Barbell Bench Press").first()

    timmy_workout = WorkoutSession(user_id=timmy.id)
    bob_workout = WorkoutSession(user_id=bob.id)
    db.session.add_all([timmy_workout, bob_workout])
    db.session.commit()
#timmys volume
    db.session.add(
        SetEntry(
            session_id=timmy_workout.id,
            exercise_id=bench.id,
            weight=135,
            reps=7,
            set_number=1
        ))  #totoal should be 945
#bobs volume
    db.session.add(
        SetEntry(
            session_id=bob_workout.id,
            exercise_id=bench.id,
            weight=225,
            reps=5,
            set_number=1
            ))  #1125

    db.session.commit()

    #timmys private data shoudlnt includes bob
    assert total_volume(timmy.id) == 945
    assert total_volume(bob.id) == 1125



#John code here down

#This test data set below was generated with claude
# ---------------------------------------------------------------------------
# Small hand-computed data set used by the tests below (user "alice"):
#
#   Session A (10 days ago): Bench 100x5 = 500 | Overhead Press 50x10 = 500   -> volume 1000
#   Session B (3 days ago):  Bench 120x3 = 360 | Bench 120x5 = 600
#                            Tricep Pushdown 40x12 = 480                      -> volume 1440
#   Session C (today):       no sets logged                                   -> volume 0
#
#   Total volume = 1000 + 1440 + 0 = 2440
#   Sets: Chest 3 (bench x3), Shoulders 1, Triceps 1
#   Best sets: Bench 120x5 (ties with 120x3, more reps wins), OHP 50x10, Pushdown 40x12
# ---------------------------------------------------------------------------

def add_session(user, days_ago, sets=()):
    """Create a session `days_ago` days back; sets are (exercise name, weight, reps) in logged order."""
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


def build_alice():
    alice = make_user("alice")
    a = add_session(alice, 10, [("Barbell Bench Press", 100, 5), ("Overhead Press", 50, 10)])
    b = add_session(alice, 3, [
        ("Barbell Bench Press", 120, 3), ("Barbell Bench Press", 120, 5), ("Tricep Pushdown", 40, 12),
    ])
    c = add_session(alice, 0)
    return alice, a, b, c


def test_volume_per_workout_is_oldest_first_and_includes_empty_sessions(app):
    alice, a, b, c = build_alice()

    result = volume_per_workout(alice.id)

    assert [(session.id, volume) for session, volume in result] == [
        (a.id, 1000.0), (b.id, 1440.0), (c.id, 0.0),
    ]
    assert sum(volume for _, volume in result) == total_volume(alice.id) == 2440.0


def test_workouts_per_week_counts_each_week_including_zeros(app):
    alice = make_user("alice")
    today = datetime.now(timezone.utc).date()
    this_monday = today - timedelta(days=today.weekday())
    # two workouts this week, one on the Sunday just before this week, one the Sunday before that
    add_session(alice, (today - this_monday).days)       # this Monday
    add_session(alice, (today - this_monday).days)       # this Monday again
    add_session(alice, (today - this_monday).days + 1)   # Sunday of last week
    add_session(alice, (today - this_monday).days + 8)   # Sunday two weeks back

    weeks = workouts_per_week(alice.id)  # default: last 8 weeks

    assert [start for start, _ in weeks] == [this_monday - timedelta(weeks=i) for i in range(7, -1, -1)]
    assert [count for _, count in weeks] == [0, 0, 0, 0, 0, 1, 1, 2]
    assert len(workouts_per_week(alice.id, weeks=3)) == 3


def test_workouts_per_week_ignores_workouts_older_than_the_window(app):
    alice = make_user("alice")
    add_session(alice, 200)
    assert sum(count for _, count in workouts_per_week(alice.id)) == 0


def test_sets_by_muscle_group_counts_sets_most_trained_first(app):
    alice, *_ = build_alice()

    # Chest 3 sets; Shoulders and Triceps tie at 1 so they fall back to alphabetical order
    assert sets_by_muscle_group(alice.id) == [("Chest", 3), ("Shoulders", 1), ("Triceps", 1)]


def test_personal_records_heaviest_set_per_exercise_ties_go_to_more_reps(app):
    alice, *_ = build_alice()

    records = personal_records(alice.id)

    assert [(exercise.name, s.weight, s.reps) for exercise, s in records] == [
        ("Barbell Bench Press", 120, 5),   # 120x3 and 120x5 tie on weight; 5 reps wins
        ("Overhead Press", 50, 10),
        ("Tricep Pushdown", 40, 12),
    ]


def test_personal_record_for_one_exercise(app):
    alice, *_ = build_alice()
    bob = make_user("bob")

    best = personal_record(alice.id, exercise_id("Barbell Bench Press"))
    assert (best.weight, best.reps) == (120, 5)
    assert personal_record(alice.id, exercise_id("Overhead Press")).weight == 50
    # bob has never logged bench, so there is no record
    assert personal_record(bob.id, exercise_id("Barbell Bench Press")) is None


def test_exercise_history_is_newest_first_and_respects_limit(app):
    alice, a, b, _ = build_alice()
    bench = exercise_id("Barbell Bench Press")

    history = exercise_history(alice.id, bench)

    # session B (newer) first, its later set first, then session A
    assert [(session.id, s.weight, s.reps) for session, s in history] == [
        (b.id, 120, 5), (b.id, 120, 3), (a.id, 100, 5),
    ]
    assert [(s.weight, s.reps) for _, s in exercise_history(alice.id, bench, limit=2)] == [(120, 5), (120, 3)]


def test_every_helper_only_uses_the_given_users_data(app):
    alice, a, b, c = build_alice()
    bob = make_user("bob")
    add_session(bob, 1, [("Barbell Bench Press", 300, 1), ("Overhead Press", 200, 1)])
    bench = exercise_id("Barbell Bench Press")

    # alice's numbers are exactly what they were without bob's heavy sets
    assert total_volume(alice.id) == 2440.0
    assert [s.id for s, _ in volume_per_workout(alice.id)] == [a.id, b.id, c.id]
    assert sum(count for _, count in workouts_per_week(alice.id)) == 3
    assert sets_by_muscle_group(alice.id) == [("Chest", 3), ("Shoulders", 1), ("Triceps", 1)]
    assert [s.weight for _, s in personal_records(alice.id)] == [120, 50, 40]
    assert personal_record(alice.id, bench).weight == 120
    assert len(exercise_history(alice.id, bench)) == 3

    # and bob's are his own: 300 + 200
    assert total_volume(bob.id) == 500.0
    assert personal_record(bob.id, bench).weight == 300


def test_helpers_return_empty_results_for_a_user_with_no_data(app):
    nobody = make_user("nobody")
    bench = exercise_id("Barbell Bench Press")

    assert total_volume(nobody.id) == 0.0
    assert volume_per_workout(nobody.id) == []
    assert [count for _, count in workouts_per_week(nobody.id)] == [0] * 8
    assert sets_by_muscle_group(nobody.id) == []
    assert personal_records(nobody.id) == []
    assert personal_record(nobody.id, bench) is None
    assert exercise_history(nobody.id, bench) == []


