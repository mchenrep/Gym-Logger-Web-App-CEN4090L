from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from app.guest import store
from app.models import Exercise
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