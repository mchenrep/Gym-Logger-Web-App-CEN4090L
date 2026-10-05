from app.models import WorkoutSession, WorkoutTemplate, SetEntry
from conftest import make_user, login, exercise_id


def test_pages_require_login(client):
    response = client.get("/workouts/new")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_start_empty_workout(client):
    make_user("alice")
    login(client, "alice")

    response = client.post("/workouts/new", data={"template_id": ""})
    workout = WorkoutSession.query.first()
    assert response.status_code == 302
    assert workout is not None
    assert workout.template_id is None
    assert client.get(f"/workouts/{workout.id}").status_code == 200


def test_start_workout_from_template_shows_checklist(client):
    make_user("alice")
    login(client, "alice")
    client.post("/templates/new", data={"name": "Push Day", "exercise_ids": [exercise_id("Overhead Press")]})
    template = WorkoutTemplate.query.first()

    client.post("/workouts/new", data={"template_id": template.id})
    workout = WorkoutSession.query.first()
    assert workout.template_id == template.id

    page = client.get(f"/workouts/{workout.id}").get_data(as_text=True)
    assert "Checklist" in page
    assert "Overhead Press" in page


def test_cannot_start_workout_from_someone_elses_template(client):
    make_user("alice")
    make_user("bob")
    login(client, "alice")
    client.post("/templates/new", data={"name": "Push Day", "exercise_ids": [exercise_id("Overhead Press")]})
    template = WorkoutTemplate.query.first()
    client.get("/auth/logout")

    login(client, "bob")
    page = client.post("/workouts/new", data={"template_id": template.id}).get_data(as_text=True)
    assert "That template doesn&#39;t exist." in page
    assert WorkoutSession.query.count() == 0


def test_log_sets_numbers_them_per_exercise(client):
    make_user("alice")
    login(client, "alice")
    client.post("/workouts/new", data={"template_id": ""})
    workout = WorkoutSession.query.first()
    bench = exercise_id("Barbell Bench Press")
    press = exercise_id("Overhead Press")

    client.post(f"/workouts/{workout.id}/sets", data={"exercise_id": bench, "weight": "135", "reps": "5"})
    client.post(f"/workouts/{workout.id}/sets", data={"exercise_id": bench, "weight": "145", "reps": "5"})
    client.post(f"/workouts/{workout.id}/sets", data={"exercise_id": press, "weight": "95", "reps": "8"})

    sets = SetEntry.query.order_by(SetEntry.id).all()
    assert [(s.exercise_id, s.set_number, s.weight, s.reps) for s in sets] == [
        (bench, 1, 135.0, 5),
        (bench, 2, 145.0, 5),
        (press, 1, 95.0, 8),
    ]

    page = client.get(f"/workouts/{workout.id}").get_data(as_text=True)
    assert "Barbell Bench Press" in page
    assert "<td>145</td>" in page


def test_log_set_validation(client):
    make_user("alice")
    login(client, "alice")
    client.post("/workouts/new", data={"template_id": ""})
    workout = WorkoutSession.query.first()
    bench = exercise_id("Barbell Bench Press")

    bad_inputs = [
        {"exercise_id": "9999", "weight": "135", "reps": "5"},
        {"exercise_id": bench, "weight": "abc", "reps": "5"},
        {"exercise_id": bench, "weight": "-10", "reps": "5"},
        {"exercise_id": bench, "weight": "nan", "reps": "5"},
        {"exercise_id": bench, "weight": "135", "reps": "0"},
        {"exercise_id": bench, "weight": "135", "reps": "2.5"},
    ]
    for data in bad_inputs:
        client.post(f"/workouts/{workout.id}/sets", data=data)
    assert SetEntry.query.count() == 0


def test_history_is_newest_first_and_private(client):
    make_user("alice")
    make_user("bob")
    login(client, "alice")
    client.post("/workouts/new", data={"template_id": ""})
    client.post("/templates/new", data={"name": "Push Day", "exercise_ids": [exercise_id("Overhead Press")]})
    client.post("/workouts/new", data={"template_id": WorkoutTemplate.query.first().id})

    page = client.get("/workouts/").get_data(as_text=True)
    assert page.index("Push Day") < page.index(">\n                Workout\n")  # newer one listed first
    client.get("/auth/logout")

    login(client, "bob")
    alices_workout = WorkoutSession.query.first()
    assert "No workouts logged yet." in client.get("/workouts/").get_data(as_text=True)
    assert client.get(f"/workouts/{alices_workout.id}").status_code == 404
    response = client.post(f"/workouts/{alices_workout.id}/sets",
                           data={"exercise_id": exercise_id("Overhead Press"), "weight": "95", "reps": "8"})
    assert response.status_code == 404


def test_stats_page_counts_workouts(client):
    make_user("alice")
    login(client, "alice")
    client.post("/workouts/new", data={"template_id": ""})
    client.post("/workouts/new", data={"template_id": ""})

    response = client.get("/workouts/stats")
    assert response.status_code == 200
    assert "2" in response.get_data(as_text=True)
