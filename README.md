# Workout Tracker + Gym Log

A Flask web app for logging workouts and building reusable workout templates.
Stack: Flask, Flask-SQLAlchemy, Flask-Login, Jinja2 templates, SQLite (Postgres optional).

## Run it (5 minutes)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed.py                  # fills the exercise library (safe to re-run)
python run.py                   # open http://127.0.0.1:5000
```

No database install needed: tables are created automatically in a local `workout.db` file.
If you change a column in `app/models.py`, delete `workout.db`, then run `python seed.py` again.

Run the tests: `pytest`

## How the code is organized

Each feature has its own folder, so we can all work at once without stepping on each other:

| Folder | What it does | Status |
|---|---|---|
| `app/auth/` | register, login, logout, profile | DONE |
| `app/models.py` | all database tables | DONE |
| `app/templates/base.html` | shared layout + nav bar | DONE |
| `app/exercises/` | exercise library page | DONE |
| `app/workout_templates/` | create/view/delete workout templates | TODO |
| `app/workouts/` | log a workout + workout history | TODO |

Open your feature's `routes.py`: the top of the file explains exactly what to build.
Every page already loads, so you can start from a working app.

## Git workflow

1. Make an issue for the task.
2. Branch off `main`: `git checkout -b feature/exercise-library`
3. Commit small and often; put the issue number in the message (`Add exercise query, #12`).
4. Open a pull request that links the issue ("Closes #12"). Have one teammate review it before merging.

Each feature lives in its own folder, so merge conflicts should be rare.
The shared files (`models.py`, `base.html`, `app/__init__.py`) need a heads-up in the group chat before editing.

## Shared UI helpers

- Add `data-confirm="Are you sure?"` to any `<form>` and the browser will ask before submitting it (handled in `static/js/main.js`).
- Page styles live in `static/css/styles.css` (cards, buttons, forms, tables, alerts, grids). Reuse those classes instead of inline styles.
- Flash messages: `flash("text", "success" | "danger" | "info")`. Success/info fade out automatically.