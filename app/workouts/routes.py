"""WORKOUT LOGGING  --  TODO: owner ________

Goal: log a workout (sets of weight x reps) and see past workouts.

Routes to build (all @login_required, only the current user's data):
  - GET  /workouts/           history: list my past sessions, newest first   (stub below)
  - GET/POST /workouts/new    start a session (optionally pick one of my templates)
  - GET  /workouts/<id>       view a session and its sets
  - POST /workouts/<id>/sets  add a set: exercise_id, weight, reps
                              (set_number = number of existing sets for that exercise + 1)

Hints:
  - Create a WorkoutSession(user_id=current_user.id), db.session.add(...), db.session.commit().
  - If a template was chosen, you can show its exercises as a checklist on the session page.
  - Return 403/404 if the session belongs to someone else.
  - Write tests in tests/test_workouts.py.
"""
from flask import render_template
from flask_login import login_required, current_user
from app.workouts import workouts_bp
from app.models import Workout

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app import db  # noqa: F401
from app.models import Exercise, WorkoutSession, SetEntry  # noqa: F401

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")

@workouts_bp.route("/")
@login_required
def history():
    sessions = []  # TODO: query current_user's sessions, newest first
    return render_template("workouts/history.html", sessions=sessions)

@workouts_bp.route('/stats')
@login_required
def stats():
    total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
    return render_template('workouts/stats.html', total_workouts=total_workouts)