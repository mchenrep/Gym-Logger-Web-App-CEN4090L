
"""Tests for editing, duplicating, and deleting workout templates."""

from app import db
from app.models import WorkoutTemplate, TemplateExercise, WorkoutSession
from conftest import make_user, login, exercise_id


def create_template(client, name, *exercise_names):
    client.post("/templates/new", data={
        "name": name, "exercise_ids": [exercise_id(n) for n in exercise_names],
    })
    return WorkoutTemplate.query.filter_by(name=name).first()


def exercise_names(template):
    return [item.exercise.name for item in template.exercises]


# ---------- edit (#28) ----------

def test_edit_page_is_prefilled(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press", "Barbell Bench Press")

    page = client.get(f"/templates/{template.id}/edit").get_data(as_text=True)
    assert 'value="Push Day"' in page
    assert "Save changes" in page
    assert f'name="order_{exercise_id("Overhead Press")}"' in page
    assert page.count("checked") == 2


def test_edit_renames_and_changes_exercises(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press", "Barbell Bench Press")

    response = client.post(f"/templates/{template.id}/edit", data={
        "name": "Push Day v2",
        "exercise_ids": [exercise_id("Barbell Bench Press"), exercise_id("Tricep Pushdown")],
    }, follow_redirects=True)
    assert "updated" in response.get_data(as_text=True)

    template = db.session.get(WorkoutTemplate, template.id)
    assert template.name == "Push Day v2"
    assert exercise_names(template) == ["Barbell Bench Press", "Tricep Pushdown"]
    assert TemplateExercise.query.count() == 2  # old rows removed


def test_edit_reorders_with_order_boxes(client):
    make_user("alice")
    login(client, "alice")
    bench, press, pushdown = (exercise_id(n) for n in ("Barbell Bench Press", "Overhead Press", "Tricep Pushdown"))
    template = create_template(client, "Push Day", "Barbell Bench Press", "Overhead Press", "Tricep Pushdown")

    client.post(f"/templates/{template.id}/edit", data={
        "name": "Push Day",
        "exercise_ids": [bench, press, pushdown],
        f"order_{bench}": "3", f"order_{press}": "1", f"order_{pushdown}": "",  # blank goes last
    })
    template = db.session.get(WorkoutTemplate, template.id)
    assert exercise_names(template) == ["Overhead Press", "Barbell Bench Press", "Tricep Pushdown"]
    assert [item.position for item in template.exercises] == [0, 1, 2]


def test_new_template_respects_order_boxes(client):
    make_user("alice")
    login(client, "alice")
    bench, press = exercise_id("Barbell Bench Press"), exercise_id("Overhead Press")

    client.post("/templates/new", data={
        "name": "Push Day", "exercise_ids": [bench, press], f"order_{bench}": "2", f"order_{press}": "1",
    })
    assert exercise_names(WorkoutTemplate.query.first()) == ["Overhead Press", "Barbell Bench Press"]


def test_edit_validation(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press")
    create_template(client, "Leg Day", "Barbell Back Squat")

    page = client.post(f"/templates/{template.id}/edit", data={"name": "Push Day"})
    assert "Pick at least one exercise." in page.get_data(as_text=True)

    page = client.post(f"/templates/{template.id}/edit", data={
        "name": "Leg Day", "exercise_ids": [exercise_id("Overhead Press")],
    })
    assert "already have a template with that name" in page.get_data(as_text=True)

    # nothing was saved
    template = db.session.get(WorkoutTemplate, template.id)
    assert template.name == "Push Day"
    assert exercise_names(template) == ["Overhead Press"]


def test_cannot_edit_someone_elses_template(client):
    make_user("alice")
    make_user("bob")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press")
    client.get("/auth/logout")

    login(client, "bob")
    assert client.get(f"/templates/{template.id}/edit").status_code == 404
    response = client.post(f"/templates/{template.id}/edit", data={
        "name": "Hacked", "exercise_ids": [exercise_id("Deadlift")],
    })
    assert response.status_code == 404
    assert db.session.get(WorkoutTemplate, template.id).name == "Push Day"


# ---------- duplicate (#29) ----------

def test_duplicate_copies_exercises_in_order(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press", "Barbell Bench Press")
    client.post("/workouts/new", data={"template_id": template.id})

    response = client.post(f"/templates/{template.id}/duplicate", follow_redirects=True)
    assert response.status_code == 200
    assert "Push Day (copy)" in response.get_data(as_text=True)

    duplicate = WorkoutTemplate.query.filter_by(name="Push Day (copy)").first()
    assert duplicate is not None and duplicate.id != template.id
    assert exercise_names(duplicate) == ["Overhead Press", "Barbell Bench Press"]

    # workout sessions stay with the original
    assert WorkoutSession.query.filter_by(template_id=duplicate.id).count() == 0
    assert WorkoutSession.query.filter_by(template_id=template.id).count() == 1


def test_duplicate_picks_a_free_name(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press")

    for _ in range(3):
        client.post(f"/templates/{template.id}/duplicate")

    names = sorted(t.name for t in WorkoutTemplate.query.all())
    assert names == ["Push Day", "Push Day (copy 2)", "Push Day (copy 3)", "Push Day (copy)"]


def test_duplicate_long_name_stays_within_limit(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "x" * 120, "Overhead Press")

    client.post(f"/templates/{template.id}/duplicate")
    duplicate = WorkoutTemplate.query.filter(WorkoutTemplate.id != template.id).first()
    assert len(duplicate.name) == 120
    assert duplicate.name.endswith(" (copy)")


def test_cannot_duplicate_someone_elses_template(client):
    make_user("alice")
    make_user("bob")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press")
    client.get("/auth/logout")

    login(client, "bob")
    assert client.post(f"/templates/{template.id}/duplicate").status_code == 404
    assert WorkoutTemplate.query.count() == 1


# ---------- buttons + confirm before delete (#30) ----------

def test_template_pages_show_edit_duplicate_and_confirm(client):
    make_user("alice")
    login(client, "alice")
    template = create_template(client, "Push Day", "Overhead Press")

    view = client.get(f"/templates/{template.id}").get_data(as_text=True)
    assert f"/templates/{template.id}/edit" in view
    assert f"/templates/{template.id}/duplicate" in view
    assert 'data-confirm="Delete this template?' in view

    listing = client.get("/templates/").get_data(as_text=True)
    assert f"/templates/{template.id}/edit" in listing
    assert f"/templates/{template.id}/duplicate" in listing
