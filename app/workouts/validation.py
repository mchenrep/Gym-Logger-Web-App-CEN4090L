"""
    Validation for one logged set (an exercise, a weight and a number of reps).

    The guest workout routes use this (app/guest/routes.py). The checks and the error
    messages are the same ones the logged-in add_set() route in app/workouts/routes.py
    does inline, so a guest and a logged-in user get the same rules.

    max_weight / max_reps are optional upper limits. Logged-in sets are saved in the
    database so they don't need one, but guest sets live inside the browser cookie
    (roughly 4 KB), so the guest routes pass limits to keep every set small.
"""

import math

from app import db
from app.models import Exercise

def validate_set(form, max_weight=None, max_reps=None):
    """Check the "add a set" form.

    Returns (exercise_id, weight, reps, error). error is None when the input is fine,
    otherwise it is a message to flash and the other three values are None.
    """
    exercise_id = form.get("exercise_id", type=int)
    weight = form.get("weight", type=float)  # None if it isn't a number
    reps = form.get("reps", type=int)  # None if it isn't a whole number

    if exercise_id is None or db.session.get(Exercise, exercise_id) is None:
        return None, None, None, "Please pick an exercise."

    if weight is None or not math.isfinite(weight) or weight < 0:
        return None, None, None, "Weight must be a number (0 or more)."
    if max_weight is not None and weight > max_weight:
        return None, None, None, f"Weight must be {max_weight:g} or less."

    if reps is None or reps < 1:
        return None, None, None, "Reps must be a whole number (1 or more)."
    if max_reps is not None and reps > max_reps:
        return None, None, None, f"Reps must be {max_reps} or less."

    return exercise_id, weight, reps, None