# ==========================================================
# ShareFlow - Startup File Sharing SaaS
# Modern Cloud File Distribution Platform
# ==========================================================

import os
import uuid
import sqlite3
from datetime import datetime

from flask import (
    Flask, request, redirect, url_for,
    render_template_string, session,
    send_from_directory
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# =================== CONFIG ===================

APP_NAME = "ShareFlow"
APP_VERSION = "1.0"

UPLOAD_FOLDER = "storage"
DATABASE = "shareflow.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =================== APP ===================

app = Flask(__name__)
app.secret_key = "dev-secret"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =================== DATABASE ===================

def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS files(
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        filename TEXT,
        path TEXT,
        size INTEGER,
        downloads INTEGER,
        created TEXT
    )
    """)

    conn.commit()
    conn.close()


# =================== USER ===================

def current_user():

    if "user_id" not in session:
        return None

    conn = db()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return user


# =================== AUTH ===================

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = db()

        conn.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return """
    <h2>Register</h2>
    <form method="post">
    <input name="username">
    <input name="password" type="password">
    <button>Register</button>
    </form>
    """


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"],password):

            session["user_id"] = user["id"]

            return redirect("/dashboard")

    return """
    <h2>Login</h2>
    <form method="post">
    <input name="username">
    <input name="password" type="password">
    <button>Login</button>
    </form>
    """


# =================== DASHBOARD ===================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    user = current_user()

    if not user:
        return redirect("/login")

    conn = db()

    files = conn.execute(
        "SELECT * FROM files WHERE user_id=?",
        (user["id"],)
    ).fetchall()

    conn.close()

    return render_template_string(DASHBOARD_HTML, files=files)


# =================== UPLOAD ===================

@app.route("/upload", methods=["POST"])
def upload():

    user = current_user()

    if not user:
        return redirect("/login")

    file = request.files["file"]

    filename = secure_filename(file.filename)

    file_id = str(uuid.uuid4())[:10]

    path = os.path.join(
        UPLOAD_FOLDER,
        file_id + "_" + filename
    )

    file.save(path)

    size = os.path.getsize(path)

    conn = db()

    conn.execute("""
    INSERT INTO files
    VALUES(?,?,?,?,?,?,?)
    """,(
        file_id,
        user["id"],
        filename,
        path,
        size,
        0,
        datetime.now()
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =================== DOWNLOAD ===================

@app.route("/f/<file_id>")
def download(file_id):

    conn = db()

    file = conn.execute(
        "SELECT * FROM files WHERE id=?",
        (file_id,)
    ).fetchone()

    conn.close()

    if not file:
        return "File not found"

    conn = db()

    conn.execute(
        "UPDATE files SET downloads = downloads + 1 WHERE id=?",
        (file_id,)
    )

    conn.commit()
    conn.close()

    directory = os.path.dirname(file["path"])
    filename = os.path.basename(file["path"])

    return send_from_directory(directory, filename, as_attachment=True)


# =================== DELETE ===================

@app.route("/delete/<file_id>")
def delete(file_id):

    conn = db()

    file = conn.execute(
        "SELECT * FROM files WHERE id=?",
        (file_id,)
    ).fetchone()

    if file:

        try:
            os.remove(file["path"])
        except:
            pass

        conn.execute(
            "DELETE FROM files WHERE id=?",
            (file_id,)
        )

        conn.commit()

    conn.close()

    return redirect("/dashboard")


# =================== UI ===================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>

<head>

<title>ShareFlow</title>

<script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="bg-gray-100">

<div class="max-w-4xl mx-auto p-8">

<h1 class="text-3xl font-bold mb-6">ShareFlow Dashboard</h1>

<form
action="/upload"
method="post"
enctype="multipart/form-data"
class="mb-6 p-6 bg-white rounded shadow">

<input type="file" name="file" class="mb-3">

<button class="bg-blue-500 text-white px-4 py-2 rounded">
Upload File
</button>

</form>

<div class="bg-white shadow rounded">

<table class="w-full">

<tr class="border-b">
<th class="p-3 text-left">File</th>
<th>Size</th>
<th>Downloads</th>
<th>Share</th>
<th></th>
</tr>

{% for f in files %}

<tr class="border-b">

<td class="p-3">{{f.filename}}</td>

<td>{{(f.size/1024/1024)|round(2)}} MB</td>

<td>{{f.downloads}}</td>

<td>
<a class="text-blue-600"
href="/f/{{f.id}}">
link
</a>
</td>

<td>
<a class="text-red-500"
href="/delete/{{f.id}}">
delete
</a>
</td>

</tr>

{% endfor %}

</table>

</div>

</div>

</body>

</html>
"""


# =================== START ===================

if __name__ == "__main__":

    init_db()

    print("ShareFlow starting...")
    print("http://127.0.0.1:5000")

    app.run(debug=True)