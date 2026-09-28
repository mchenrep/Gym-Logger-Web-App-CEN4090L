"""WORKOUT TEMPLATES  --  TODO: owner ________

Goal: users can create reusable routines (e.g. "Push Day") made of exercises.

Routes to build (all should be @login_required and only touch current_user's data):
  - GET  /templates/          list my templates                (stub below)
  - GET/POST /templates/new   form: name + pick exercises -> create WorkoutTemplate
                              and one TemplateExercise per chosen exercise
  - GET  /templates/<id>      view one template and its exercises
  - POST /templates/<id>/delete   delete a template

Hints:
  - current_user.templates gives you the logged-in user's templates.
  - Get the chosen exercises from a multi-select with request.form.getlist("exercise_ids").
  - Return 404 (abort(404)) if the template isn't found or isn't the user's.
  - Write tests in tests/test_workout_templates.py.
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app import db  # noqa: F401
from app.models import Exercise, WorkoutTemplate, TemplateExercise  # noqa: F401

workout_templates_bp = Blueprint("workout_templates", __name__, url_prefix="/templates")


@workout_templates_bp.route("/")
@login_required
def list_templates():
    templates = []  # TODO: use current_user.templates
    return render_template("workout_templates/list.html", templates=templates)
