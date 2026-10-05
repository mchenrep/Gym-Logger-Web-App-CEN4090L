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
import math

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Exercise, WorkoutSession, WorkoutTemplate, SetEntry

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")

@workouts_bp.route("/")
@login_required
def history():
    sessions = (
        WorkoutSession.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc())
        .all()
    )
    return render_template("workouts/history.html", sessions=sessions)

@workouts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_workout():
    templates = (
        WorkoutTemplate.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutTemplate.name)
        .all()
    )

    # if starting a workout:
    if request.method == "POST":
        template_id = request.form.get("template_id", type=int)  # blank = no template

        # a template is optional, but if one was picked it must be one of mine
        if template_id is not None:
            template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first()
            if template is None:
                flash("That template doesn't exist.", "danger")
                return render_template("workouts/new.html", templates=templates)

        workout = WorkoutSession(user_id=current_user.id, template_id=template_id)
        db.session.add(workout)
        db.session.commit()

        flash("Workout started. Log your sets below.", "success")
        return redirect(url_for("workouts.view_workout", workout_id=workout.id))

    return render_template("workouts/new.html", templates=templates)

@workouts_bp.route("/<int:workout_id>")
@login_required
def view_workout(workout_id):
    # 404 if the workout doesn't exist OR belongs to someone else
    workout = WorkoutSession.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()
    exercises = Exercise.query.order_by(Exercise.name).all()

    # group the sets by exercise, in the order each exercise was first logged
    sets_by_exercise = {}
    for set_entry in workout.sets:
        sets_by_exercise.setdefault(set_entry.exercise, []).append(set_entry)

    # template checklist: an exercise counts as done once it has at least one set
    template_exercises = workout.template.exercises if workout.template else []
    done_ids = {set_entry.exercise_id for set_entry in workout.sets}

    # pre-fill the "add a set" form: repeat the last set, or start on the first unfinished template exercise
    last_set = workout.sets[-1] if workout.sets else None
    if last_set:
        default_exercise_id = last_set.exercise_id
    else:
        default_exercise_id = template_exercises[0].exercise_id if template_exercises else None

    return render_template(
        "workouts/view.html",
        workout=workout,
        exercises=exercises,
        sets_by_exercise=sets_by_exercise,
        template_exercises=template_exercises,
        done_ids=done_ids,
        last_set=last_set,
        default_exercise_id=default_exercise_id,
    )

@workouts_bp.route("/<int:workout_id>/sets", methods=["POST"])
@login_required
def add_set(workout_id):
    workout = WorkoutSession.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()

    exercise_id = request.form.get("exercise_id", type=int)
    weight = request.form.get("weight", type=float)  # None if it isn't a number
    reps = request.form.get("reps", type=int)

    # input validation
    error = None
    if exercise_id is None or db.session.get(Exercise, exercise_id) is None:
        error = "Please pick an exercise."
    elif weight is None or not math.isfinite(weight) or weight < 0:
        error = "Weight must be a number (0 or more)."
    elif reps is None or reps < 1:
        error = "Reps must be a whole number (1 or more)."

    if error:
        flash(error, "danger")
        return redirect(url_for("workouts.view_workout", workout_id=workout.id))

    # set_number = number of sets of this exercise already in the workout + 1
    set_number = SetEntry.query.filter_by(session_id=workout.id, exercise_id=exercise_id).count() + 1

    set_entry = SetEntry(
        session_id=workout.id, exercise_id=exercise_id, set_number=set_number, weight=weight, reps=reps
    )
    db.session.add(set_entry)
    db.session.commit()

    return redirect(url_for("workouts.view_workout", workout_id=workout.id))

@workouts_bp.route('/stats')
@login_required
def stats():
    total_workouts = WorkoutSession.query.filter_by(user_id=current_user.id).count()
    return render_template('workouts/stats.html', total_workouts=total_workouts)
