from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = "dev-secret"  # change in prod

def get_connection():
    return psycopg2.connect(
        dbname="appointments_db",
        user="postgres",
        password="1234hihi",
        host="localhost",
        port="5432"
    )

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM appointments ORDER BY date, time")
    appointments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("list.html", appointments=appointments)

@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        date = request.form.get("date")
        time = request.form.get("time")
        service = request.form.get("service")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO appointments (client_name, date, time, service)
            VALUES (%s, %s, %s, %s)
        """, (client_name, date, time, service))
        conn.commit()
        cur.close()
        conn.close()
        flash("Rendez-vous ajouté !", "success")
        return redirect(url_for("index"))

    return render_template("form.html", appointment=None, action="Create")

@app.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == "POST":
        client_name = request.form.get("client_name")
        date = request.form.get("date")
        time = request.form.get("time")
        service = request.form.get("service")

        cur.execute("""
            UPDATE appointments
            SET client_name=%s, date=%s, time=%s, service=%s
            WHERE id=%s
        """, (client_name, date, time, service, appointment_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Rendez-vous modifié !", "success")
        return redirect(url_for("index"))

    
    cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
    appointment = cur.fetchone()
    cur.close()
    conn.close()
    if not appointment:
        flash("Rendez-vous introuvable.", "danger")
        return redirect(url_for("index"))
    return render_template("form.html", appointment=appointment, action="Edit")


@app.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
def delete_appointment(appointment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Rendez-vous supprimé.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
