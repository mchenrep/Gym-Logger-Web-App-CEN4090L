from app import db
from app.models import WorkoutTemplate, TemplateExercise, WorkoutSession
from conftest import make_user, login, exercise_id


def create_push_day(client):
    return client.post("/templates/new", data={
        "name": "Push Day",
        "exercise_ids": [exercise_id("Overhead Press"), exercise_id("Barbell Bench Press")],
    }, follow_redirects=True)


def test_pages_require_login(client):
    response = client.get("/templates/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_template(client):
    make_user("alice")
    login(client, "alice")

    response = create_push_day(client)
    template = WorkoutTemplate.query.filter_by(name="Push Day").first()
    assert response.status_code == 200
    assert "created" in response.get_data(as_text=True)
    assert template is not None
    # exercises keep the order they were submitted in
    assert [item.exercise.name for item in template.exercises] == ["Overhead Press", "Barbell Bench Press"]

    page = client.get("/templates/").get_data(as_text=True)
    assert "Push Day" in page


def test_create_template_validation(client):
    make_user("alice")
    login(client, "alice")

    page = client.post("/templates/new", data={"name": "", "exercise_ids": [exercise_id("Overhead Press")]})
    assert "Please give your template a name." in page.get_data(as_text=True)

    page = client.post("/templates/new", data={"name": "Leg Day"})
    assert "Pick at least one exercise." in page.get_data(as_text=True)

    page = client.post("/templates/new", data={"name": "Leg Day", "exercise_ids": ["9999"]})
    assert "doesn&#39;t exist" in page.get_data(as_text=True)

    create_push_day(client)
    page = create_push_day(client)
    assert "already have a template with that name" in page.get_data(as_text=True)
    assert WorkoutTemplate.query.count() == 1


def test_view_template(client):
    make_user("alice")
    login(client, "alice")
    create_push_day(client)
    template = WorkoutTemplate.query.first()

    page = client.get(f"/templates/{template.id}").get_data(as_text=True)
    assert "Push Day" in page
    assert "Overhead Press" in page


def test_cannot_see_or_delete_someone_elses_template(client):
    make_user("alice")
    make_user("bob")
    login(client, "alice")
    create_push_day(client)
    template = WorkoutTemplate.query.first()
    client.get("/auth/logout")

    login(client, "bob")
    assert client.get(f"/templates/{template.id}").status_code == 404
    assert client.post(f"/templates/{template.id}/delete").status_code == 404
    assert "Push Day" not in client.get("/templates/").get_data(as_text=True)
    assert db.session.get(WorkoutTemplate, template.id) is not None


def test_delete_template_keeps_past_workouts(client):
    make_user("alice")
    login(client, "alice")
    create_push_day(client)
    template = WorkoutTemplate.query.first()
    client.post("/workouts/new", data={"template_id": template.id})

    response = client.post(f"/templates/{template.id}/delete")
    assert response.status_code == 302
    assert WorkoutTemplate.query.count() == 0
    assert TemplateExercise.query.count() == 0
    # the workout is still there, just no longer linked to the template
    workout = WorkoutSession.query.first()
    assert workout is not None
    assert workout.template_id is None
