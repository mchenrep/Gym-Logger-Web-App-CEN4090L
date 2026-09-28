from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    templates = db.relationship("WorkoutTemplate", backref="user", cascade="all, delete-orphan")
    sessions = db.relationship("WorkoutSession", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Exercise(db.Model):
    """One exercise in the library, ex: 'Barbell Bench Press' / Barbell / Chest."""
    
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(60), nullable=False)      # e.g. Barbell, Dumbbell, Cable, Machine, Cardio, etc.
    muscle_group = db.Column(db.String(60), nullable=False)  # e.g. Chest, Quads, etc.


class WorkoutTemplate(db.Model):
    """A reusable routine, ex: 'Push Day' = bench + overhead press + triceps."""
    
    __tablename__ = "workout_templates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    exercises = db.relationship(
        "TemplateExercise", backref="template", cascade="all, delete-orphan",
        order_by="TemplateExercise.position",
    )


class TemplateExercise(db.Model):
    """One exercise inside a template (position = its order in the routine)."""
    
    __tablename__ = "template_exercises"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("workout_templates.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    position = db.Column(db.Integer, default=0)

    exercise = db.relationship("Exercise")


class WorkoutSession(db.Model):
    """One logged workout. template_id is optional (you can log without a template)."""
    
    __tablename__ = "workout_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey("workout_templates.id"), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    template = db.relationship("WorkoutTemplate")
    sets = db.relationship(
        "SetEntry", backref="session", cascade="all, delete-orphan",
        order_by="SetEntry.id",
    )


class SetEntry(db.Model):
    """One set: '135 lbs x 5 reps of Bench Press' inside a session."""
    
    __tablename__ = "set_entries"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    reps = db.Column(db.Integer, nullable=False)

    exercise = db.relationship("Exercise")