from flask import Flask
from flask import render_template, redirect, url_for, request, abort, flash

app = Flask(__name__)

# ---------------------------- API routes -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/workout")
def workout():
    return render_template("workout.html")

@app.route("/exercises")
def exercises():
    return render_template("exercises.html")

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.route("/account")
def account():
    return render_template("account.html")

# --------------------------- Main ------------------------------------
if __name__ == "__main__":
    app.run()