"""Routes for managing workout templates."""

import math
from itertools import count

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Exercise, WorkoutTemplate, TemplateExercise, WorkoutSession

workout_templates_bp = Blueprint("workout_templates", __name__, url_prefix="/templates")

NAME_MAX_LENGTH = 120

def _read_template_form(template_id=None):
    """Validate the form data for creating or editing a template."""
    name = request.form.get("name", "").strip()
    exercise_ids = list(dict.fromkeys(request.form.getlist("exercise_ids", type=int)))
    exercise_ids.sort(key=lambda exercise_id: request.form.get(f"order_{exercise_id}", type=int) or math.inf)

    # input validation
    error = None
    if not name:
        error = "Please give your template a name."
    elif len(name) > NAME_MAX_LENGTH:
        error = f"Template name must be {NAME_MAX_LENGTH} characters or less."
    elif not exercise_ids:
        error = "Pick at least one exercise."
    elif Exercise.query.filter(Exercise.id.in_(exercise_ids)).count() != len(exercise_ids):
        error = "One of the chosen exercises doesn't exist."
    elif WorkoutTemplate.query.filter(
        WorkoutTemplate.user_id == current_user.id,
        WorkoutTemplate.name == name,
        WorkoutTemplate.id != template_id,  # template's own name doesn't count when ediitng
    ).first():
        error = "You already have a template with that name."
    return name, exercise_ids, error

def _build_exercises(exercise_ids):
    """Create template exercises in the selected order."""
    return [
        TemplateExercise(exercise_id=exercise_id, position=position)
        for position, exercise_id in enumerate(exercise_ids)
    ]


@workout_templates_bp.route("/")
@login_required
def list_templates():
    templates = (
        WorkoutTemplate.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutTemplate.name)
        .all()
    )
    return render_template("workout_templates/list.html", templates=templates)


@workout_templates_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_template():
    exercises = Exercise.query.order_by(Exercise.name).all()

    # if creating a template
    if request.method == "POST":
        name, exercise_ids, error = _read_template_form()
        if error:
            flash(error, "danger")
            return render_template(
                "workout_templates/new.html", exercises=exercises, template=None, 
                name=name, selected_ids=exercise_ids
            )

        template = WorkoutTemplate(user_id=current_user.id, name=name, exercises=_build_exercises(exercise_ids))
        db.session.add(template)
        db.session.commit()

        flash(f'Template "{name}" created.', "success")
        return redirect(url_for("workout_templates.view_template", template_id=template.id))

    return render_template("workout_templates/new.html", exercises=exercises, template=None, name="", selected_ids=[])


@workout_templates_bp.route("/<int:template_id>")
@login_required
def view_template(template_id):
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()
    return render_template("workout_templates/view.html", template=template)


@workout_templates_bp.route("/<int:template_id>/delete", methods=["POST"])
@login_required
def delete_template(template_id):
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()
    name = template.name

    WorkoutSession.query.filter_by(template_id=template.id).update({"template_id": None})

    db.session.delete(template)
    db.session.commit()

    flash(f'Template "{name}" deleted.', "info")
    return redirect(url_for("workout_templates.list_templates"))


@workout_templates_bp.route("/<int:template_id>/edit", methods=["GET", "POST"])
@login_required
def edit_template(template_id):
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()
    exercises = Exercise.query.order_by(Exercise.name).all()

    # if saving changes
    if request.method == "POST":
        name, exercise_ids, error = _read_template_form(template.id)
        if error:
            flash(error, "danger")
            return render_template(
                "workout_templates/new.html", exercises=exercises, template=template, name=name, selected_ids=exercise_ids
            )

        template.name = name
        template.exercises = _build_exercises(exercise_ids)
        db.session.commit()

        flash(f'Template "{name}" updated.', "success")
        return redirect(url_for("workout_templates.view_template", template_id=template.id))

    return render_template(
        "workout_templates/new.html", exercises=exercises, template=template,
        name=template.name, selected_ids=[item.exercise_id for item in template.exercises],
    )


@workout_templates_bp.route("/<int:template_id>/duplicate", methods=["POST"])
@login_required
def duplicate_template(template_id):
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()

    taken = {
        name for (name,) in
        WorkoutTemplate.query.filter_by(user_id=current_user.id).with_entities(WorkoutTemplate.name)
    }
    for number in count(1):
        suffix = " (copy)" if number == 1 else f" (copy {number})"
        copy_name = template.name[:NAME_MAX_LENGTH - len(suffix)] + suffix  # stay within the name column's limit
        if copy_name not in taken:
            break

    # same exercises in the same order, past workout sessions aren't copied
    duplicate = WorkoutTemplate(
        user_id=current_user.id, name=copy_name,
        exercises=_build_exercises(item.exercise_id for item in template.exercises),
    )
    db.session.add(duplicate)
    db.session.commit()

    flash(f'Template "{template.name}" duplicated as "{copy_name}".', "success")
    return redirect(url_for("workout_templates.view_template", template_id=duplicate.id))
