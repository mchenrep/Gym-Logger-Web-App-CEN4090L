from conftest import make_user, login, exercise_id


def test_detail_requires_login(client):
    bench_id = exercise_id("Barbell Bench Press")

    response = client.get(
        f"/exercises/{bench_id}"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_detail_page_loads(client):
    make_user("alice")
    login(client, "alice")

    bench_id = exercise_id("Barbell Bench Press")

    response = client.get(
        f"/exercises/{bench_id}"
    )

    assert response.status_code == 200


def test_detail_shows_exercise_name(client):
    make_user("alice")
    login(client, "alice")

    bench_id = exercise_id("Barbell Bench Press")

    page = client.get(
        f"/exercises/{bench_id}"
    ).get_data(as_text=True)

    assert "Barbell Bench Press" in page


def test_detail_shows_category_and_muscle_group(client):
    make_user("alice")
    login(client, "alice")

    bench_id = exercise_id("Barbell Bench Press")

    page = client.get(
        f"/exercises/{bench_id}"
    ).get_data(as_text=True)

    assert "Barbell" in page
    assert "Chest" in page


def test_detail_returns_404_for_invalid_exercise(client):
    make_user("alice")
    login(client, "alice")

    response = client.get(
        "/exercises/9999"
    )

    assert response.status_code == 404