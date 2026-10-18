"""
INCREMENT 2 (owner: Richard) - the two stub routes at the bottom of this file:
  - GET/POST /templates/<id>/edit       rename + add/remove/reorder exercises
  - POST     /templates/<id>/duplicate  copy a template (name it "<name> (copy)")
  Also: add Edit / Duplicate buttons to workout_templates/view.html (and list.html),
  and add data-confirm="Delete this template?" to the delete form
  (static/js/main.js already shows the browser confirm for it).
  Tests live in tests/test_template_edit.py (Hector).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Exercise, WorkoutTemplate, TemplateExercise, WorkoutSession

workout_templates_bp = Blueprint("workout_templates", __name__, url_prefix="/templates")


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

    # if creating a template:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        # type=int drops anything that isn't a number; dict.fromkeys removes duplicates but keeps order
        exercise_ids = list(dict.fromkeys(request.form.getlist("exercise_ids", type=int)))

        # input validation
        error = None
        if not name:
            error = "Please give your template a name."
        elif len(name) > 120:
            error = "Template name must be 120 characters or less."
        elif not exercise_ids:
            error = "Pick at least one exercise."
        elif Exercise.query.filter(Exercise.id.in_(exercise_ids)).count() != len(exercise_ids):
            error = "One of the chosen exercises doesn't exist."
        elif WorkoutTemplate.query.filter_by(user_id=current_user.id, name=name).first():
            error = "You already have a template with that name."

        if error:
            flash(error, "danger")
            return render_template(
                "workout_templates/new.html", exercises=exercises, name=name, selected_ids=exercise_ids
            )

        # create the template + one TemplateExercise per chosen exercise (position = its order in the list)
        template = WorkoutTemplate(user_id=current_user.id, name=name)
        for position, exercise_id in enumerate(exercise_ids):
            template.exercises.append(TemplateExercise(exercise_id=exercise_id, position=position))
        db.session.add(template)
        db.session.commit()

        flash(f'Template "{name}" created.', "success")
        return redirect(url_for("workout_templates.view_template", template_id=template.id))

    return render_template("workout_templates/new.html", exercises=exercises, name="", selected_ids=[])


@workout_templates_bp.route("/<int:template_id>")
@login_required
def view_template(template_id):
    # 404 if the template doesn't exist OR belongs to someone else
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()
    return render_template("workout_templates/view.html", template=template)


@workout_templates_bp.route("/<int:template_id>/delete", methods=["POST"])
@login_required
def delete_template(template_id):
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()
    name = template.name

    # keep past workouts that used this template, just unlink them from it
    WorkoutSession.query.filter_by(template_id=template.id).update({"template_id": None})

    db.session.delete(template)  # its TemplateExercise rows are deleted too (cascade)
    db.session.commit()

    flash(f'Template "{name}" deleted.', "info")
    return redirect(url_for("workout_templates.list_templates"))


@workout_templates_bp.route("/<int:template_id>/edit", methods=["GET", "POST"])
@login_required
def edit_template(template_id):
    # STUB (Increment 2, Richard). Ownership check is done for you; delete the abort(501) when you start.
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()  # noqa: F841
    # TODO 1: GET  -> render workout_templates/edit.html (copy new.html) pre-filled with the template's
    #                 name and current exercise ids (see how new_template() passes selected_ids).
    # TODO 2: POST -> reuse the same validation as new_template(), BUT allow keeping the template's
    #                 own name (only reject a name used by a *different* template of this user).
    # TODO 3: update template.name, then rebuild template.exercises with positions in the new order
    #         (clearing the list is fine: delete-orphan removes the old TemplateExercise rows).
    # TODO 4: flash a success message and redirect to view_template.
    abort(501)


@workout_templates_bp.route("/<int:template_id>/duplicate", methods=["POST"])
@login_required
def duplicate_template(template_id):
    # STUB (Increment 2, Richard).
    template = WorkoutTemplate.query.filter_by(id=template_id, user_id=current_user.id).first_or_404()  # noqa: F841
    # TODO 1: pick a free name: "<name> (copy)", then "<name> (copy 2)", ... (names are unique per user).
    # TODO 2: create a new WorkoutTemplate for current_user with a TemplateExercise per original
    #         exercise, keeping the same positions. Do NOT copy workout sessions.
    # TODO 3: flash success and redirect to the new template's page.
    abort(501)
