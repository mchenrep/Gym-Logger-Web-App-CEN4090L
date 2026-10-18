from conftest import make_user, login
#test 1login required
def test_library_requires_login(client):
    response = client.get("/exercises/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


#test 2 library loads or logged-in user
def test_library_page_loads(client):
    make_user("alice")
    login(client, "alice")

    response = client.get("/exercises/")

    assert response.status_code == 200
#test 3 Shows Seeded Exercises
def test_library_displays_exercises(client):
    make_user("alice")
    login(client, "alice")

    page = client.get("/exercises/").get_data(as_text=True)

    assert "Barbell Bench Press" in page
    assert "Overhead Press" in page

#test 4 Search Works
def test_search_filters_results(client):
    make_user("alice")
    login(client, "alice")

    page = client.get(
        "/exercises/?q=Bench"
    ).get_data(as_text=True)

    assert "Barbell Bench Press" in page

#test 5 Category Filter
def test_category_filter(client):
    make_user("alice")
    login(client, "alice")

    page = client.get(
        "/exercises/?category=Barbell"
    ).get_data(as_text=True)

    assert "Barbell Bench Press" in page
#Test 6: Muscle Group Filter
def test_muscle_group_filter(client):
    make_user("alice")
    login(client, "alice")

    page = client.get(
        "/exercises/?muscle_group=Chest"
    ).get_data(as_text=True)

    assert "Barbell Bench Press" in page
#Test 7: Combined Filtering
def test_search_and_filter_together(client):
    make_user("alice")
    login(client, "alice")

    page = client.get(
        "/exercises/?q=Bench&category=Barbell"
    ).get_data(as_text=True)

    assert "Barbell Bench Press" in page