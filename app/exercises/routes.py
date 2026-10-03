"""EXERCISE LIBRARY  --  TODO: owner ________

Goal: a page that lists the seeded exercises (name, category, muscle group).

Steps:
  1. In library(), query the exercises:
         exercises = Exercise.query.order_by(Exercise.name).all()
     and pass them to the template (template already loops over `exercises`).
  2. Add a search box: read request.args.get("q") and filter with
         Exercise.query.filter(Exercise.name.ilike(f"%{q}%"))
  3. (Nice to have) filter by category / muscle group with a dropdown.
  4. Write tests in tests/test_exercises.py.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models import Exercise  # noqa: F401  (you'll need this)

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.route("/")
@login_required
def library():
    # get the search query and filters from the URL
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    muscle_group = request.args.get("muscle_group", "").strip()

    # start with all exercises
    exercise_query = Exercise.query
    
    # search by name
    if q:
        exercise_query = exercise_query.filter(Exercise.name.ilike(f"%{q}%"))

    # filter by category
    if category:
        exercise_query = exercise_query.filter(Exercise.category == category)

    # filter by muscle group
    if muscle_group:
        exercise_query = exercise_query.filter(Exercise.muscle_group == muscle_group)

    # order final results alphabetically
    exercises = exercise_query.order_by(Exercise.name).all()

    # get list of categories for the dropdown
    categories = [
        category_name
        for (category_name,) in (
            Exercise.query
            .with_entities(Exercise.category) # only the category column
            .distinct() # remove duplicate values 
            .order_by(Exercise.category)
            .all()
        )
    ]

    # get list of muscle groups for the dropdown
    muscle_groups = [
        muscle_group_name
        for (muscle_group_name,) in (
            Exercise.query
            .with_entities(Exercise.muscle_group)
            .distinct()
            .order_by(Exercise.muscle_group)
            .all()
        )
    ]
    
    return render_template(
        "exercises/library.html", 
        exercises=exercises, 
        q=q,
        categories=categories,
        muscle_groups=muscle_groups,
        selected_category=category,
        selected_muscle_group=muscle_group
    )
