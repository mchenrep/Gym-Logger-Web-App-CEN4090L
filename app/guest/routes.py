"""
GUEST WORKOUTS: someone who isn't logged in can start a workout, log sets, and see a
summary of the finished workout. Nothing is saved to the database. It all lives in the
browser's session cookie (see app/guest/store.py) and goes away when the browser is closed.

Guests can NOT: save a workout permanently, use templates, keep notes, or see stats/history.
Those pages stay @login_required. Guest code never imports or writes to the workout tables,
so a guest can't reach them even by accident.

Routes:
    GET  /guest/workout          the guest workout page (start button, active workout or summary)
    POST /guest/start            start a guest workout
    POST /guest/workout/sets     log a set
    POST /guest/workout/finish   finish the workout (shows the summary)
    POST /guest/workout/discard  throw the workout away
    POST /guest/workout/save     (logged in) copy the guest workout into the user's account
"""
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from app import db
from app.guest import store
from app.models import Exercise, SetEntry, WorkoutSession
from app.workouts.validation import validate_set

guest_bp = Blueprint("guest", __name__, url_prefix="/guest")


def guests_only(view):
    """Logged-in users already have their workouts saved, so send them to the normal pages."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You're logged in, so your workouts are saved to your account.", "info")
            return redirect(url_for("workouts.new_workout"))
        return view(*args, **kwargs)

    return wrapper


@guest_bp.route("/workout")
@guests_only
def workout():
    exercises = Exercise.query.order_by(Exercise.name).all()
    exercises_by_id = {exercise.id: exercise for exercise in exercises}

    stored = store.get_workout()
    summary = store.summarize(stored, exercises_by_id) if stored else None

    # exercise_id comes from the exercise detail page's "Start a Workout With This Exercise" button
    requested_exercise_id = request.args.get("exercise_id", type=int)
    if requested_exercise_id not in exercises_by_id:
        requested_exercise_id = None

    # which exercise is pre-selected in the "log a set" form: the requested one, else the last one used
    if requested_exercise_id is not None:
        default_exercise_id = requested_exercise_id
    elif summary and summary["last_set"]:
        default_exercise_id = summary["last_set"]["exercise_id"]
    else:
        default_exercise_id = None

    return render_template(
        "guest/workout.html",
        summary=summary,
        exercises=exercises,
        default_exercise_id=default_exercise_id,
        requested_exercise_id=requested_exercise_id,
        max_sets=store.MAX_SETS,
        max_weight=store.MAX_WEIGHT,
        max_reps=store.MAX_REPS,
    )


@guest_bp.route("/start", methods=["POST"])
@guests_only
def start():
    exercise_id = request.form.get("exercise_id", type=int)

    existing = store.get_workout()
    if existing and not existing["finished"]:
        # don't wipe a workout that's in progress just because the button was clicked again
        flash("You already have a guest workout in progress.", "info")
    else:
        store.start_workout()
        flash("Guest workout started. Nothing is saved, it only lives in this browser.", "success")

    return redirect(url_for("guest.workout", exercise_id=exercise_id))


@guest_bp.route("/workout/sets", methods=["POST"])
@guests_only
def add_set():
    exercise_id, weight, reps, error = validate_set(
        request.form, max_weight=store.MAX_WEIGHT, max_reps=store.MAX_REPS
    )
    if error is None:
        error = store.add_set(exercise_id, weight, reps)  # also checks: workout exists, not finished, set limit

    if error:
        flash(error, "danger")
    return redirect(url_for("guest.workout"))


@guest_bp.route("/workout/finish", methods=["POST"])
@guests_only
def finish():
    error = store.finish_workout()
    if error:
        flash(error, "danger")
    else:
        flash("Workout finished. Here's your summary.", "success")
    return redirect(url_for("guest.workout"))


@guest_bp.route("/workout/discard", methods=["POST"])
def discard():
    # not guests_only: a user who logs in with an unsaved guest workout can discard it too
    store.clear_workout()
    flash("Guest workout discarded.", "info")
    return redirect(url_for("index") if current_user.is_authenticated else url_for("guest.workout"))


@guest_bp.route("/workout/save", methods=["POST"])
@login_required
def save():
    """
        Only  place guest data reaches the database, and only when a logged in user asks for it.
        A guest who signs up or logs in keeps their workout in the cookie, and the dashboard offers this.
    """
    workout = store.get_workout()
    if workout is None or not workout["sets"]:
        flash("There is no guest workout to save.", "info")
        return redirect(url_for("index"))

    # only keep sets whose exercise is (still) in the library
    exercise_ids = {exercise_id for exercise_id, _, _ in workout["sets"]}
    known_ids = {exercise.id for exercise in Exercise.query.filter(Exercise.id.in_(exercise_ids)).all()}
    sets = [entry for entry in workout["sets"] if entry[0] in known_ids]
    if not sets:
        store.clear_workout()
        flash("None of the exercises in that guest workout exist anymore, so it wasn't saved.", "danger")
        return redirect(url_for("index"))

    saved = WorkoutSession(user_id=current_user.id, date=datetime.fromisoformat(workout["started_at"]))
    db.session.add(saved)
    db.session.flush()  # gives `saved` its id so the sets can point at it

    set_numbers = {}  # exercise id -> how many sets of it are saved so far
    for exercise_id, weight, reps in sets:
        set_numbers[exercise_id] = set_numbers.get(exercise_id, 0) + 1
        db.session.add(SetEntry(
            session_id=saved.id, exercise_id=exercise_id, set_number=set_numbers[exercise_id],
            weight=weight, reps=reps,
        ))
    db.session.commit()

    store.clear_workout()
    flash("Guest workout saved to your account.", "success")
    return redirect(url_for("workouts.view_workout", workout_id=saved.id))
