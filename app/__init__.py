from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # where @login_required sends logged-out users

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object("config.Config")
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    # Each feature lives in its own blueprint (its own folder) so teammates
    # can work in parallel without editing the same files.
    from app.auth.routes import auth_bp
    from app.exercises.routes import exercises_bp
    from app.workout_templates.routes import workout_templates_bp
    from app.workouts.routes import workouts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(workout_templates_bp)
    app.register_blueprint(workouts_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    # Custom error pages
    def render_error(code, title, message):
        return render_template("errors/error.html", code=code, title=title, message=message), code

    @app.errorhandler(403)
    def forbidden(_error):
        return render_error(403, "Access denied", "You don't have permission to view this page.")

    @app.errorhandler(404)
    def not_found(_error):
        return render_error(404, "Page not found", "That page doesn't exist, or it isn't yours to view.")

    @app.errorhandler(501)
    def not_implemented(_error):
        # Increment 2 stub routes abort(501) until their owner builds them.
        return render_error(501, "Coming soon", "This feature hasn't been built yet.")

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()  # leave the database session clean after a failed request
        return render_error(500, "Something went wrong", "An unexpected error occurred. Please try again.")

    # Create any missing tables on startup (no migrations needed for this project).
    # NOTE: if you change a model's columns, delete workout.db and restart.
    with app.app_context():
        from app import models  # noqa: F401  (registers the models with SQLAlchemy)
        db.create_all()

    return app
