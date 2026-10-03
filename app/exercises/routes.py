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
    # get the search query from the URL
    q = request.args.get("q", "").strip()

    # if a search query is provided, search exercises by name
    if q:
        exercises = (
            Exercise.query
            .filter(Exercise.name.ilike(f"%{q}%"))
            .order_by(Exercise.name)  # alphabetical order
            .all()
        )
    # otherwise, display all exercises
    else:
        exercises = Exercise.query.order_by(Exercise.name).all()
    
    return render_template("exercises/library.html", exercises=exercises, q=q)
