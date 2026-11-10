from app.models import WorkoutTemplate
from conftest import make_user, login, exercise_id
def create_push_day(client):
    return client.post(
        "/templates/new",
        data={
            "name": "Push Day",
            "exercise_ids": [
                exercise_id("Overhead Press"),
                exercise_id("Barbell Bench Press"),
            ],
        },
        follow_redirects=True,
    )
def test_edit_template_name(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "Upper Body",
            "exercise_ids": [
                exercise_id("Overhead Press"),
                exercise_id("Barbell Bench Press"),
            ],
        },
        follow_redirects=True,
    )

    updated = WorkoutTemplate.query.get(template.id)

    assert response.status_code == 200
    assert updated.name == "Upper Body"
def test_edit_template_exercises(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "Push Day",
            "exercise_ids": [
                exercise_id("Tricep Pushdown")
            ],
        },
        follow_redirects=True,
    )

    updated = WorkoutTemplate.query.get(template.id)

    assert response.status_code == 200

    exercise_names = [
        item.exercise.name
        for item in updated.exercises
    ]

    assert exercise_names == ["Tricep Pushdown"]
def test_cannot_edit_other_users_template(client):
    make_user("alice")
    make_user("bob")

    login(client, "alice")
    create_push_day(client)

    template = WorkoutTemplate.query.first()

    client.get("/auth/logout")

    login(client, "bob")

    response = client.get(
        f"/templates/{template.id}/edit"
    )

    assert response.status_code == 404
def test_edit_template_allows_keeping_same_name(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "Push Day",
            "exercise_ids": [
                exercise_id("Overhead Press")
            ],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    updated = WorkoutTemplate.query.get(template.id)
    assert updated.name == "Push Day"
def test_edit_template_blank_name(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "",
            "exercise_ids": [
                exercise_id("Overhead Press")
            ],
        },
        follow_redirects=True,
    )

    assert "Please give your template a name." in response.get_data(as_text=True)
def test_edit_template_requires_exercise(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "Updated Template",
            "exercise_ids": [],
        },
        follow_redirects=True,
    )

    assert "Pick at least one exercise." in response.get_data(as_text=True)
def test_edit_template_invalid_exercise(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    template = WorkoutTemplate.query.first()

    response = client.post(
        f"/templates/{template.id}/edit",
        data={
            "name": "Updated Template",
            "exercise_ids": ["9999"],
        },
        follow_redirects=True,
    )

    updated = WorkoutTemplate.query.get(template.id)

    assert updated.name == "Push Day"
    
def test_edit_template_duplicate_name(client):
    make_user("alice")
    login(client, "alice")

    create_push_day(client)

    client.post(
        "/templates/new",
        data={
            "name": "Leg Day",
            "exercise_ids": [
                exercise_id("Overhead Press")
            ],
        },
    )

    push_day = WorkoutTemplate.query.filter_by(
        name="Push Day"
    ).first()

    response = client.post(
        f"/templates/{push_day.id}/edit",
        data={
            "name": "Leg Day",
            "exercise_ids": [
                exercise_id("Overhead Press")
            ],
        },
        follow_redirects=True,
    )

    assert "already have a template with that name" in response.get_data(as_text=True)