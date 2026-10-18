"""
INCREMENT 2 (owner: Mawi):
  - detail() below is a bare-bones stub: it shows name / category / muscle group.
    TODO: link to it from each card in library.html, then show THIS user's history
    for the exercise (best set, recent sets) using analytics.exercise_history()
    from app/workouts/analytics.py once John has built it.
  - TODO: library.html uses `exercise.description`, but the Exercise model has no such
    column. Either drop it from the template or add the column (tell the team first:
    it needs a database reset).
  - Tests live in tests/test_exercise_detail.py (Hector).
"""
from flask import Blueprint, render_template, request, abort
from flask_login import login_required

from app import db
from app.models import Exercise

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

@exercises_bp.route("/<int:exercise_id>")
@login_required
def detail(exercise_id):
    # STUB (Increment 2, Mawi): see the module docstring for the TODO list.
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        abort(404)
    return render_template("exercises/detail.html", exercise=exercise)