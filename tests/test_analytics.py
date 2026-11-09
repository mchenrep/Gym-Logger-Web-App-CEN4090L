from app import db
from app.models import User, Exercise, WorkoutSession, SetEntry
from app.workouts.analytics import total_volume

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

