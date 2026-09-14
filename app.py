from flask import Flask
from flask import render_template, redirect, url_for, request, abort, flash

app = Flask(__name__)

# ---------------------------- API routes -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

# --------------------------- Main ------------------------------------
if __name__ == "__main__":
    app.run()