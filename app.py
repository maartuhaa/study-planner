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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/oppgaver")
def tasks():
    return render_template("tasks.html")


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

    flash("Logget ut.")

    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)