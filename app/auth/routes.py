from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # if already authenticated: redirect to index
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # if registering:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # input validation
        error = None
        if not username or not email or not password:
            error = "All fields are required."
        elif "@" not in email:
            error = "Please enter a valid email."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif User.query.filter_by(username=username).first():
            error = "That username is already taken."
        elif User.query.filter_by(email=email).first():
            error = "That email is already registered."

        if error:
            flash(error, "danger")
            return render_template("auth/register.html", username=username, email=email)

        # register user
        user = User(username=username, email=email)
        user.set_password(password)  # stores a hash, never the real password
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created. Welcome!", "success")
        return redirect(url_for("index"))
    
    return render_template("auth/register.html", username="", email="")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # if already authenticated: redirect to index
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # if logging in:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # validate credentials
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")    

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html")