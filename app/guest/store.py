"""Where a guest's workout lives: inside the Flask session (a signed cookie in the browser).

Nothing in this file touches the db. That's the point of guest mode:
  - the workout only exists in the visitor's browser
  - it disappears when the browser session ends (no permanent sessions)
  - and no guest data can ever end up in the database by accident.

What is stored in session["guest_workout"]:
    {
        "started_at": "2026-11-13T15:04:05",     # UTC, ISO format
        "finished":   False,
        "sets":       [[exercise_id, weight, reps], ...],   # in the order they were logged
    }
Sets are plain [id, weight, reps] lists (not dicts) to keep the cookie small, because browsers
drop cookies bigger than about 4 KB. MAX_SETS / MAX_WEIGHT / MAX_REPS keep it under that.
Set numbers (set 1, set 2, ...) aren't stored, they're worked out when the workout is shown.
"""

from datetime import datetime, timezone

from flask import session

KEY = "guest" # replace with secure key in prod

MAX_SETS = 60  # a guest workout can't have more sets than this (cookie size)
MAX_WEIGHT = 5000  # lbs, per set. 
MAX_REPS = 1000  # per set. 

def _is_valid(data):
    """True if data looks like something this file saved. Anything else is ignored, so a bad or
    old cookie shows up as "no workout" instead of crashing a page."""
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("finished"), bool):
        return False
    started_at = data.get("started_at")
    if not isinstance(started_at, str):
        return False
    try:
        datetime.fromisoformat(started_at)
    except ValueError:
        return False
    sets = data.get("sets")
    if not isinstance(sets, list) or len(sets) > MAX_SETS:
        return False
    for entry in sets:
        if not isinstance(entry, list) or len(entry) != 3:
            return False
        exercise_id, weight, reps = entry
        if isinstance(exercise_id, bool) or not isinstance(exercise_id, int):
            return False
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            return False
        if isinstance(reps, bool) or not isinstance(reps, int):
            return False
    return True

def get_workout():
    """
        The guest's workout (a dict, see the top of this file) or None if there isn't one.
    """
    data = session.get(KEY)
    return data if _is_valid(data) else None


def set_count():
    """
        How many sets the guest has logged (0 if there is no guest workout).
    """
    workout = get_workout()
    return len(workout["sets"]) if workout else 0

def start_workout():
    """
        Start a new empty guest workout. Replaces any old one.
    """
    workout = {
        "started_at": datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0).isoformat(),
        "finished": False,
        "sets": [],
    }
    session[KEY] = workout
    return workout


def add_set(exercise_id, weight, reps):
    """Add one (already validated) set. Returns an error message, or None if it worked."""
    workout = get_workout()
    if workout is None:
        return "Start a guest workout first."
    if workout["finished"]:
        return "This workout is finished. Start a new one to log more sets."
    if len(workout["sets"]) >= MAX_SETS:
        return f"Guest workouts are limited to {MAX_SETS} sets. Create an account to log more."

    # build a new dict and assign it: changing the old one in place wouldn't get saved to the cookie
    session[KEY] = {**workout, "sets": workout["sets"] + [[exercise_id, round(float(weight), 2), reps]]}
    return None

def finish_workout():
    """Mark the workout as finished. Returns an error message, or None if it worked."""
    workout = get_workout()
    if workout is None:
        return "There is no guest workout to finish."
    if workout["finished"]:
        return "This workout is already finished."
    if not workout["sets"]:
        return "Log at least one set before finishing."
    session[KEY] = {**workout, "finished": True}
    return None


def clear_workout():
    """
        Clear the guest workout
    """
    session.pop(KEY, None)


def summarize(workout, exercises_by_id):
    """
    Turn the stored workout into what the page shows.

    exercises_by_id is {exercise id: Exercise}. Sets whose exercise isn't in it are skipped.
    
    Sets are grouped by exercise (in the order each exercise was first logged), like the
    logged-in workout page, and each set gets its number within its exercise.
    """
    groups = {}
    total_sets = 0
    total_volume = 0.0
    last_set = None

    for exercise_id, weight, reps in workout["sets"]:
        exercise = exercises_by_id.get(exercise_id)
        if exercise is None:
            continue
        group = groups.setdefault(exercise_id, {"exercise": exercise, "sets": []})
        group["sets"].append({"number": len(group["sets"]) + 1, "weight": weight, "reps": reps})
        total_sets += 1
        total_volume += weight * reps
        last_set = {"exercise_id": exercise_id, "weight": weight, "reps": reps}

    return {
        "started_at": datetime.fromisoformat(workout["started_at"]),
        "finished": workout["finished"],
        "groups": list(groups.values()),
        "total_sets": total_sets,
        "exercise_count": len(groups),
        "total_volume": round(total_volume, 2),
        "last_set": last_set,  # lets the "add a set" form pre-fill the previous weight and reps
    }