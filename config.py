import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Default: a local SQLite file (workout.db) so nobody needs to install a database.
    # To use Postgres instead, set DATABASE_URL in your environment.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "workout.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False