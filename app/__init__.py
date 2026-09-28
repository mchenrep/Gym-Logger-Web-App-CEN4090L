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


    # *blueprints here*


    @app.route("/")
    def index():
        return render_template("index.html")

    # Create any missing tables on startup (no migrations needed for this project).
    # NOTE: if you change a model's columns, delete workout.db and restart.
    with app.app_context():
        from app import models  # noqa: F401  (registers the models with SQLAlchemy)
        db.create_all()

    return app
