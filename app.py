from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT, SECRET_KEY
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

@app.context_processor
def inject_today_events():

    today_events = []

    if session.get("user_id"):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM events
            WHERE user_id = %s
            AND event_date = CURDATE()
            """,
            (session["user_id"],)
        )

        today_events = cursor.fetchall()

        cursor.close()
        conn.close()

    return dict(today_events=today_events)

@app.route("/")
def home():

    events = []
    today_events = []

    if session.get("user_id"):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM events
            WHERE user_id = %s
            ORDER BY event_date
            """,
            (session["user_id"],)
        )

        events = cursor.fetchall()

        from datetime import date

        today = date.today()

        for event in events:

            if event["event_date"] == today:
                today_events.append(event)

        cursor.close()
        conn.close()

    return render_template(
        "index.html",
        events=events,
        today_events=today_events
    )

@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):

    if not session.get("user_id"):
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM events
        WHERE id = %s
        AND user_id = %s
        """,
        (
            event_id,
            session["user_id"]
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"].strip()
    password = request.form["password"]

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            """,
            (username, password_hash)
        )

        conn.commit()

        session["user_id"] = cursor.lastrowid
        session["username"] = username

    except mysql.connector.Error:

        flash("Brukernavn finnes allerede.")

    finally:

        cursor.close()
        conn.close()

    return redirect(url_for("home"))


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(
        user["password_hash"],
        password
    ):

        session["user_id"] = user["id"]
        session["username"] = user["username"]


    else:

        flash("Feil brukernavn eller passord.")

    return redirect(url_for("home"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

@app.route("/add_event", methods=["POST"])
def add_event():

    if not session.get("user_id"):
        return redirect(url_for("home"))

    title = request.form["title"]
    event_date = request.form["event_date"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO events
        (user_id, title, event_date)
        VALUES (%s, %s, %s)
        """,
        (
            session["user_id"],
            title,
            event_date
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/oppgaver")
def tasks():

    if not session.get("user_id"):
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    todo_count = len([
    task for task in tasks
    if task["status"] == "todo"
])

    progress_count = len([
    task for task in tasks
    if task["status"] == "progress"
])

    done_count = len([
    task for task in tasks
    if task["status"] == "done"
])

    return render_template(
    "tasks.html",
    tasks=tasks,
    todo_count=todo_count,
    progress_count=progress_count,
    done_count=done_count
)

@app.route("/add_task", methods=["POST"])
def add_task():

    if not session.get("user_id"):
        return redirect(url_for("home"))

    title = request.form["title"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (user_id, title)
        VALUES (%s, %s)
        """,
        (
            session["user_id"],
            title
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("tasks"))

@app.route("/move_task/<int:task_id>/<status>")
def move_task(task_id, status):

    if not session.get("user_id"):
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = %s
        WHERE id = %s
        AND user_id = %s
        """,
        (
            status,
            task_id,
            session["user_id"]
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("tasks"))

@app.route("/profil")
def profile():

    if not session.get("user_id"):
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Antall hendelser

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    events_count = cursor.fetchone()["count"]

    # Antall oppgaver

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    tasks_count = cursor.fetchone()["count"]

    # Fullførte oppgaver

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE user_id = %s
        AND status = 'done'
        """,
        (session["user_id"],)
    )

    completed_count = cursor.fetchone()["count"]

    # Brukerinfo

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        events_count=events_count,
        tasks_count=tasks_count,
        completed_count=completed_count
    )

if __name__ == "__main__":
    app.run(debug=True)