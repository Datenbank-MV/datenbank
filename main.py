import random
from flask import Flask, render_template, request, redirect, url_for, session, g, send_file, send_from_directory
import sqlite3
import os
import csv
import io
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
DATABASE = "datenbank.db"

USERS = {
    "MarlonGartmann": os.getenv("MARLONGARTMANN", "default_password"),
    "FriedrichOelze": os.getenv("FRIEDRICHOELZE", "default_password"),
    "KonradLorenzen": os.getenv("KONRADLORENZEN", "default_password")
}
ADMIN_USERNAME = "AdminGartmann"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_admin_password")

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def log_event(username, action, details=""):
    db = get_db()
    db.execute(
        "INSERT INTO logs (event_time, username, action, details) VALUES (datetime('now'), ?, ?, ?)",
        (username, action, details)
    )
    db.commit()

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as db:
            cursor = db.cursor()
            cursor.execute(
                """CREATE TABLE data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personen_id TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    vorname TEXT,
                    nachname TEXT,
                    geschlecht TEXT,
                    geburtsdatum TEXT,
                    geburtsort TEXT,
                    nationalitaeten TEXT,
                    sprachen TEXT,
                    strasse TEXT,
                    plz TEXT,
                    stadt TEXT,
                    telefonnummer TEXT,
                    email TEXT,
                    instagram TEXT,
                    weitere_links TEXT,
                    mutter TEXT,
                    vater TEXT,
                    geschwister TEXT,
                    partner TEXT,
                    kinder TEXT,
                    freunde TEXT,
                    beruf TEXT,
                    arbeitgeber TEXT,
                    ausbildung TEXT,
                    gesundheitsdaten TEXT,
                    marke TEXT,
                    modell TEXT,
                    farbe TEXT,
                    kennzeichen TEXT,
                    erkennungsmerkmale TEXT,
                    hobbys TEXT,
                    mitgliedschaften TEXT,
                    notizen TEXT,
                    quelle TEXT,
                    status TEXT,
                    profile_photo TEXT,
                    album_folder TEXT
                )"""
            )
            cursor.execute(
                """CREATE TABLE logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_time TEXT,
                    username TEXT,
                    action TEXT,
                    details TEXT
                )"""
            )
            db.commit()
    else:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(data)")
        columns = [info[1] for info in cursor.fetchall()]
        if "profile_photo" not in columns:
            cursor.execute("ALTER TABLE data ADD COLUMN profile_photo TEXT")
        if "album_folder" not in columns:
            cursor.execute("ALTER TABLE data ADD COLUMN album_folder TEXT")
        db.commit()
        db.close()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and password == USERS[username]:
            session["user"] = username
            log_event(username, "login", "Benutzer hat sich eingeloggt")
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="Falsche Zugangsdaten!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/welcome")
def welcome():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("welcome.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        # Nur das Feld "Zuletzt geändert" ist zwingend erforderlich.
        updated_at = request.form.get("updated_at")
        if not updated_at:
            return render_template("add.html", error="Das Feld 'Zuletzt geändert' muss ausgefüllt werden.")

        personen_id = "{:06d}".format(random.randint(0, 999999))
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Grunddaten
        vorname = request.form.get("vorname")
        nachname = request.form.get("nachname")
        geschlecht = request.form.get("geschlecht")
        # Bei "geburtsdatum" wird kein Format erzwungen – freie Eingabe
        geburtsdatum = request.form.get("geburtsdatum")
        geburtsort = request.form.get("geburtsort")
        nationalitaeten = request.form.get("nationalitaeten")
        sprachen = request.form.get("sprachen")

        # 2. Kontaktinformationen
        strasse = request.form.get("strasse")
        plz = request.form.get("plz")
        stadt = request.form.get("stadt")
        telefonnummer = request.form.get("telefonnummer")
        email = request.form.get("email")
        instagram = request.form.get("instagram")
        weitere_links = request.form.get("weitere_links")

        # 3. Familiäre & Soziale Beziehungen
        mutter = request.form.get("mutter")
        vater = request.form.get("vater")
        geschwister = request.form.get("geschwister")
        partner = request.form.get("partner")
        kinder = request.form.get("kinder")
        freunde = request.form.get("freunde")

        # 4. Beruf & Bildung
        beruf = request.form.get("beruf")
        arbeitgeber = request.form.get("arbeitgeber")
        ausbildung = request.form.get("ausbildung")

        # 5. Gesundheitsdaten
        gesundheitsdaten = request.form.get("gesundheitsdaten")

        # 6. Fahrzeuginformationen
        marke = request.form.get("marke")
        modell = request.form.get("modell")
        farbe = request.form.get("farbe")
        kennzeichen = request.form.get("kennzeichen")
        erkennungsmerkmale = request.form.get("erkennungsmerkmale")

        # 7. Sonstige Informationen
        hobbys = request.form.get("hobbys")
        mitgliedschaften = request.form.get("mitgliedschaften")
        notizen = request.form.get("notizen")

        # 8. Verwaltungsinformationen
        quelle = request.form.get("quelle")
        status = request.form.get("status")

        db = get_db()
        placeholders = ", ".join("?" for _ in range(37))
        sql = f"""INSERT INTO data (
                    personen_id, created_at, updated_at,
                    vorname, nachname, geschlecht, geburtsdatum, geburtsort, nationalitaeten, sprachen,
                    strasse, plz, stadt, telefonnummer, email, instagram, weitere_links,
                    mutter, vater, geschwister, partner, kinder, freunde,
                    beruf, arbeitgeber, ausbildung,
                    gesundheitsdaten,
                    marke, modell, farbe, kennzeichen, erkennungsmerkmale,
                    hobbys, mitgliedschaften, notizen,
                    quelle, status
                ) VALUES ({placeholders})"""
        values = (personen_id, created_at, updated_at,
                  vorname, nachname, geschlecht, geburtsdatum, geburtsort, nationalitaeten, sprachen,
                  strasse, plz, stadt, telefonnummer, email, instagram, weitere_links,
                  mutter, vater, geschwister, partner, kinder, freunde,
                  beruf, arbeitgeber, ausbildung,
                  gesundheitsdaten,
                  marke, modell, farbe, kennzeichen, erkennungsmerkmale,
                  hobbys, mitgliedschaften, notizen,
                  quelle, status)
        cursor = db.execute(sql, values)
        db.commit()
        new_entry_id = cursor.lastrowid
        log_event(session["user"], "entry_created", f"Neues Profil erstellt: ID {new_entry_id}, {vorname} {nachname}")

        # Datei-Upload: Profilfoto
        profile_photo = request.files.get("profile_photo")
        if profile_photo and profile_photo.filename != "":
            filename = secure_filename(profile_photo.filename)
            photo_filename = f"{new_entry_id}_profile_{filename}"
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            profile_photo.save(photo_path)
            db.execute("UPDATE data SET profile_photo = ? WHERE id = ?", (photo_filename, new_entry_id))
            db.commit()

        # Datei-Upload: Album (mehrere Dateien)
        album_files = request.files.getlist("album_files")
        if album_files and any(f.filename for f in album_files):
            album_folder = os.path.join("album", str(new_entry_id))
            full_album_folder = os.path.join(app.config["UPLOAD_FOLDER"], album_folder)
            os.makedirs(full_album_folder, exist_ok=True)
            for f in album_files:
                if f and f.filename != "":
                    file_name = secure_filename(f.filename)
                    file_path = os.path.join(full_album_folder, file_name)
                    f.save(file_path)
            db.execute("UPDATE data SET album_folder = ? WHERE id = ?", (album_folder, new_entry_id))
            db.commit()

        return redirect(url_for("daten"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    if request.method == "POST":
        # Nur das Feld "Zuletzt geändert" ist zwingend erforderlich.
        updated_at = request.form.get("updated_at")
        if not updated_at:
            cursor = db.execute("SELECT * FROM data WHERE id = ?", (id,))
            entry = cursor.fetchone()
            return render_template("edit.html", entry=entry, error="Das Feld 'Zuletzt geändert' muss ausgefüllt werden.")

        old_entry = db.execute("SELECT * FROM data WHERE id = ?", (id,)).fetchone()

        vorname = request.form.get("vorname")
        nachname = request.form.get("nachname")
        geschlecht = request.form.get("geschlecht")
        # Bei "geburtsdatum" wird kein Format erzwungen – freie Eingabe
        geburtsdatum = request.form.get("geburtsdatum")
        geburtsort = request.form.get("geburtsort")
        nationalitaeten = request.form.get("nationalitaeten")
        sprachen = request.form.get("sprachen")
        strasse = request.form.get("strasse")
        plz = request.form.get("plz")
        stadt = request.form.get("stadt")
        telefonnummer = request.form.get("telefonnummer")
        email = request.form.get("email")
        instagram = request.form.get("instagram")
        weitere_links = request.form.get("weitere_links")
        mutter = request.form.get("mutter")
        vater = request.form.get("vater")
        geschwister = request.form.get("geschwister")
        partner = request.form.get("partner")
        kinder = request.form.get("kinder")
        freunde = request.form.get("freunde")
        beruf = request.form.get("beruf")
        arbeitgeber = request.form.get("arbeitgeber")
        ausbildung = request.form.get("ausbildung")
        gesundheitsdaten = request.form.get("gesundheitsdaten")
        marke = request.form.get("marke")
        modell = request.form.get("modell")
        farbe = request.form.get("farbe")
        kennzeichen = request.form.get("kennzeichen")
        erkennungsmerkmale = request.form.get("erkennungsmerkmale")
        hobbys = request.form.get("hobbys")
        mitgliedschaften = request.form.get("mitgliedschaften")
        notizen = request.form.get("notizen")
        quelle = request.form.get("quelle")
        status = request.form.get("status")

        fields = ["updated_at", "vorname", "nachname", "geschlecht", "geburtsdatum", "geburtsort", "nationalitaeten", "sprachen",
                  "strasse", "plz", "stadt", "telefonnummer", "email", "instagram", "weitere_links",
                  "mutter", "vater", "geschwister", "partner", "kinder", "freunde",
                  "beruf", "arbeitgeber", "ausbildung",
                  "gesundheitsdaten",
                  "marke", "modell", "farbe", "kennzeichen", "erkennungsmerkmale",
                  "hobbys", "mitgliedschaften", "notizen",
                  "quelle", "status"]
        new_values = [updated_at, vorname, nachname, geschlecht, geburtsdatum, geburtsort, nationalitaeten, sprachen,
                      strasse, plz, stadt, telefonnummer, email, instagram, weitere_links,
                      mutter, vater, geschwister, partner, kinder, freunde,
                      beruf, arbeitgeber, ausbildung,
                      gesundheitsdaten,
                      marke, modell, farbe, kennzeichen, erkennungsmerkmale,
                      hobbys, mitgliedschaften, notizen,
                      quelle, status]
        diffs = []
        for i, field in enumerate(fields):
            old_val = old_entry[field]
            new_val = new_values[i]
            if old_val != new_val:
                diffs.append(f"{field}: '{old_val}' -> '{new_val}'")
        diff_message = ", ".join(diffs) if diffs else "Keine Änderungen"

        db.execute(
            """UPDATE data SET 
                    updated_at = ?,
                    vorname = ?,
                    nachname = ?,
                    geschlecht = ?,
                    geburtsdatum = ?,
                    geburtsort = ?,
                    nationalitaeten = ?,
                    sprachen = ?,
                    strasse = ?,
                    plz = ?,
                    stadt = ?,
                    telefonnummer = ?,
                    email = ?,
                    instagram = ?,
                    weitere_links = ?,
                    mutter = ?,
                    vater = ?,
                    geschwister = ?,
                    partner = ?,
                    kinder = ?,
                    freunde = ?,
                    beruf = ?,
                    arbeitgeber = ?,
                    ausbildung = ?,
                    gesundheitsdaten = ?,
                    marke = ?,
                    modell = ?,
                    farbe = ?,
                    kennzeichen = ?,
                    erkennungsmerkmale = ?,
                    hobbys = ?,
                    mitgliedschaften = ?,
                    notizen = ?,
                    quelle = ?,
                    status = ?
                WHERE id = ?""",
            (updated_at, vorname, nachname, geschlecht, geburtsdatum, geburtsort, nationalitaeten, sprachen,
             strasse, plz, stadt, telefonnummer, email, instagram, weitere_links,
             mutter, vater, geschwister, partner, kinder, freunde,
             beruf, arbeitgeber, ausbildung,
             gesundheitsdaten,
             marke, modell, farbe, kennzeichen, erkennungsmerkmale,
             hobbys, mitgliedschaften, notizen,
             quelle, status, id)
        )
        db.commit()
        log_event(session["user"], "entry_edited", f"Profil bearbeitet: ID {id}. Änderungen: {diff_message}")

        # Datei-Upload: Profilfoto (Update, falls neu hochgeladen)
        profile_photo = request.files.get("profile_photo")
        if profile_photo and profile_photo.filename != "":
            filename = secure_filename(profile_photo.filename)
            photo_filename = f"{id}_profile_{filename}"
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            profile_photo.save(photo_path)
            db.execute("UPDATE data SET profile_photo = ? WHERE id = ?", (photo_filename, id))
            db.commit()

        # Datei-Upload: Album (zusätzliche Dateien anhängen)
        album_files = request.files.getlist("album_files")
        if album_files and any(f.filename for f in album_files):
            album_folder = os.path.join("album", str(id))
            full_album_folder = os.path.join(app.config["UPLOAD_FOLDER"], album_folder)
            os.makedirs(full_album_folder, exist_ok=True)
            for f in album_files:
                if f and f.filename != "":
                    file_name = secure_filename(f.filename)
                    file_path = os.path.join(full_album_folder, file_name)
                    f.save(file_path)
            db.execute("UPDATE data SET album_folder = ? WHERE id = ?", (album_folder, id))
            db.commit()

        return redirect(url_for("daten"))
    else:
        cursor = db.execute("SELECT * FROM data WHERE id = ?", (id,))
        entry = cursor.fetchone()
        return render_template("edit.html", entry=entry)

@app.route("/daten")
def daten():
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.execute("SELECT id, vorname, nachname FROM data ORDER BY created_at DESC")
    profiles = cursor.fetchall()
    return render_template("daten.html", profiles=profiles)

@app.route("/profile/<int:id>")
def profile(id):
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.execute("SELECT * FROM data WHERE id = ?", (id,))
    profile = cursor.fetchone()
    if not profile:
        return redirect(url_for("daten"))
    return render_template("profile.html", profile=profile)

@app.route("/search", methods=["GET"])
def search():
    if "user" not in session:
        return redirect(url_for("login"))
    query = request.args.get("query", "")
    db = get_db()
    like_query = f"%{query}%"
    sql = """
    SELECT * FROM data 
    WHERE personen_id LIKE ? OR created_at LIKE ? OR updated_at LIKE ? OR vorname LIKE ? OR nachname LIKE ? 
      OR geschlecht LIKE ? OR geburtsdatum LIKE ? OR geburtsort LIKE ? OR nationalitaeten LIKE ? OR sprachen LIKE ? 
      OR strasse LIKE ? OR plz LIKE ? OR stadt LIKE ? OR telefonnummer LIKE ? OR email LIKE ? OR instagram LIKE ? 
      OR weitere_links LIKE ? OR mutter LIKE ? OR vater LIKE ? OR geschwister LIKE ? OR partner LIKE ? OR kinder LIKE ? 
      OR freunde LIKE ? OR beruf LIKE ? OR arbeitgeber LIKE ? OR ausbildung LIKE ? OR gesundheitsdaten LIKE ? 
      OR marke LIKE ? OR modell LIKE ? OR farbe LIKE ? OR kennzeichen LIKE ? OR erkennungsmerkmale LIKE ? 
      OR hobbys LIKE ? OR mitgliedschaften LIKE ? OR notizen LIKE ? OR quelle LIKE ? OR status LIKE ?
    """
    params = (like_query,) * 37
    cursor = db.execute(sql, params)
    results = cursor.fetchall()
    return render_template("search.html", query=query, results=results)

@app.route("/info")
def info():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("info.html")

@app.route("/download")
def download():
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.execute("SELECT * FROM data")
    data = cursor.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Personen-ID", "Erstellungsdatum", "Änderungsdatum", 
        "Vorname", "Nachname", "Geschlecht", "Geburtsdatum", "Geburtsort",
        "Nationalität/-en", "Sprache(n)", 
        "Straße", "PLZ", "Stadt", "Telefonnummer", "E-Mail", 
        "Instagram", "Weitere Links",
        "Mutter", "Vater", "Geschwister", "Partner", "Kinder", "Freunde", 
        "Beruf", "Arbeitgeber", "Ausbildung",
        "Gesundheitsdaten",
        "Marke", "Modell", "Farbe", "Kennzeichen", "Erkennungsmerkmale",
        "Hobbys", "Mitgliedschaften", "Notizen",
        "Quelle", "Status"
    ])
    for row in data:
        writer.writerow([
            row["personen_id"], row["created_at"], row["updated_at"],
            row["vorname"], row["nachname"], row["geschlecht"], row["geburtsdatum"], row["geburtsort"],
            row["nationalitaeten"], row["sprachen"],
            row["strasse"], row["plz"], row["stadt"], row["telefonnummer"], row["email"],
            row["instagram"], row["weitere_links"],
            row["mutter"], row["vater"], row["geschwister"], row["partner"], row["kinder"], row["freunde"],
            row["beruf"], row["arbeitgeber"], row["ausbildung"],
            row["gesundheitsdaten"],
            row["marke"], row["modell"], row["farbe"], row["kennzeichen"], row["erkennungsmerkmale"],
            row["hobbys"], row["mitgliedschaften"], row["notizen"],
            row["quelle"], row["status"]
        ])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="daten.csv")

@app.route("/protokoll", methods=["GET", "POST"])
def protokoll():
    if not session.get("admin"):
        if request.method == "POST":
            admin_username = request.form.get("admin_username")
            admin_password = request.form.get("admin_password")
            if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
                session["admin"] = admin_username
                log_event(admin_username, "admin_login", "Admin hat sich ins Protokoll eingeloggt")
                return redirect(url_for("protokoll"))
            else:
                error = "Falsche Admin-Zugangsdaten!"
                return render_template("admin_login.html", error=error)
        return render_template("admin_login.html")
    db = get_db()
    cursor = db.execute("SELECT * FROM logs ORDER BY event_time DESC")
    logs = cursor.fetchall()
    return render_template("protokoll.html", logs=logs)

@app.route("/download_logs")
def download_logs():
    if not session.get("admin"):
        return redirect(url_for("protokoll"))
    db = get_db()
    cursor = db.execute("SELECT * FROM logs ORDER BY event_time DESC")
    logs = cursor.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Event Time", "Username", "Action", "Details"])
    for log in logs:
        writer.writerow([log["id"], log["event_time"], log["username"], log["action"], log["details"]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="protokoll.csv")

@app.route("/delete_logs", methods=["POST"])
def delete_logs():
    if not session.get("admin"):
        return redirect(url_for("protokoll"))
    db = get_db()
    db.execute("DELETE FROM logs")
    db.commit()
    return redirect(url_for("protokoll"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    db.execute("DELETE FROM data WHERE id = ?", (id,))
    db.commit()
    log_event(session["user"], "entry_deleted", f"Profil gelöscht: ID {id}")
    return redirect(url_for("daten"))

@app.route("/album/<int:id>")
def album(id):
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.execute("SELECT album_folder FROM data WHERE id = ?", (id,))
    row = cursor.fetchone()
    album_folder = row["album_folder"] if row else None
    album_files = []
    if album_folder:
        full_album_folder = os.path.join(app.config["UPLOAD_FOLDER"], album_folder)
        if os.path.exists(full_album_folder):
            album_files = os.listdir(full_album_folder)
    return render_template("album.html", album_files=album_files, album_folder=album_folder, id=id)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
