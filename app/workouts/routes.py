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
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db  # noqa: F401
from app.models import Exercise, WorkoutSession,WorkoutTemplate, SetEntry  # noqa: F401

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")

@workouts_bp.route("/")
@login_required
def history():
    #sessions = []  # TODO: query current_user's sessions, newest first
    sessions = (WorkoutSession.query.filter_by(user_id=current_user.id)
                .order_by(WorkoutSession.date.desc()).all())

    return render_template("workouts/history.html", sessions=sessions)

@workouts_bp.route('/stats')
@login_required
def stats():
    total_workouts = WorkoutSession.query.filter_by(user_id=current_user.id).count()
    return render_template('workouts/stats.html', total_workouts=total_workouts)

@workouts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_workout():
    if request.method == "POST":
        session = WorkoutSession(user_id=current_user.id)
        db.session.add(session)
        db.session.commit()
        return redirect(url_for("workout.view._session", id=session.id))
    return render_template("workouts/new.html")

@workouts_bp.route("/<int:id>")
@login_required
def view_session(id):
    session = WorkoutSession.query.get_or_404(id)
    if session.user_id != current_user.id:
        abort(403)
    return render_template("workouts/detail.html", session=session)

@workouts_bp.route("/<int:id>/sets", methods=["POST"])
@login_required
def add_set(id):
    session =WorkoutSession.query.get_or_404(id)
    if session.user_id != current_user.id:
        abort(403)


    exercise_id = int(request.form.get("exercise_id"))
    weight = float (request.form.get("weight"))
    reps = int(request.form.get("reps"))

    set_count = SetEntry.query.filter_by(session_id=id, exercise_id=exercise_id).count()
    set_number = set_count + 1

    new_set = SetEntry(exercise_id=exercise_id,session_id=id, weight=weight, reps=reps, set_number=set_number)
    db.session.add(new_set)
    db.session.commit()

    return redirect(url_for("workout.view._session", id=id))