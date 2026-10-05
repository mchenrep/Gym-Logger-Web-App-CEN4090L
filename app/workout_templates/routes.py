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
from flask import Blueprint, render_template, request, redirect, url_for, flash
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
