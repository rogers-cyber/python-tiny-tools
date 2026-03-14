# ==========================================================
# FileShare PRO - Secure File Sharing Web App
# Professional Web Tool
# ==========================================================

import os
import uuid
import hashlib
from datetime import datetime

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    send_from_directory,
    abort
)

# =================== APP CONFIG ===================

APP_NAME = "FileShare PRO"
APP_VERSION = "1.0.0"

UPLOAD_FOLDER = "shared_files"
MAX_FILE_SIZE = 1024 * 1024 * 500   # 500 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


# =================== MEMORY DATABASE ===================

files_db = {}


# =================== UTIL ===================

def generate_id():
    return str(uuid.uuid4())[:8]


def hash_file(path):

    md5 = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)

    return md5.hexdigest()


def get_file_size(path):
    return round(os.path.getsize(path) / 1024 / 1024, 2)


# =================== HTML TEMPLATE ===================

PAGE = """

<!DOCTYPE html>
<html>
<head>
<title>{{app_name}}</title>

<style>

body{
font-family:Segoe UI;
background:#0f172a;
color:white;
padding:40px;
}

.container{
max-width:900px;
margin:auto;
}

h1{
color:#38bdf8;
}

.upload{
margin-bottom:30px;
padding:20px;
background:#1e293b;
border-radius:10px;
}

.files{
background:#1e293b;
padding:20px;
border-radius:10px;
}

table{
width:100%;
border-collapse:collapse;
}

td,th{
padding:10px;
border-bottom:1px solid #334155;
}

a{
color:#22c55e;
text-decoration:none;
}

button{
background:#38bdf8;
border:none;
padding:8px 14px;
border-radius:6px;
cursor:pointer;
}

</style>

</head>

<body>

<div class="container">

<h1>{{app_name}} v{{version}}</h1>

<div class="upload">

<form method="POST" enctype="multipart/form-data">

<input type="file" name="file" required>
<button type="submit">Upload File</button>

</form>

</div>

<div class="files">

<h2>Shared Files</h2>

<table>

<tr>
<th>Name</th>
<th>Size</th>
<th>Date</th>
<th>Download</th>
<th>Delete</th>
</tr>

{% for id,file in files.items() %}

<tr>

<td>{{file.name}}</td>
<td>{{file.size}} MB</td>
<td>{{file.date}}</td>

<td>
<a href="/download/{{id}}">Download</a>
</td>

<td>
<a href="/delete/{{id}}">Delete</a>
</td>

</tr>

{% endfor %}

</table>

</div>

</div>

</body>
</html>

"""


# =================== ROUTES ===================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        f = request.files["file"]

        if not f:
            return redirect("/")

        file_id = generate_id()

        filename = f.filename
        path = os.path.join(app.config["UPLOAD_FOLDER"], file_id + "_" + filename)

        f.save(path)

        files_db[file_id] = {
            "name": filename,
            "path": path,
            "size": get_file_size(path),
            "hash": hash_file(path),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        return redirect("/")

    return render_template_string(
        PAGE,
        app_name=APP_NAME,
        version=APP_VERSION,
        files=files_db
    )


# =================== DOWNLOAD ===================

@app.route("/download/<file_id>")
def download(file_id):

    file = files_db.get(file_id)

    if not file:
        abort(404)

    directory = os.path.dirname(file["path"])
    filename = os.path.basename(file["path"])

    return send_from_directory(directory, filename, as_attachment=True)


# =================== DELETE ===================

@app.route("/delete/<file_id>")
def delete(file_id):

    file = files_db.get(file_id)

    if not file:
        abort(404)

    try:
        os.remove(file["path"])
    except:
        pass

    files_db.pop(file_id, None)

    return redirect("/")


# =================== API ===================

@app.route("/api/files")
def api_files():

    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "files": files_db
    }


# =================== START ===================

if __name__ == "__main__":

    print(f"{APP_NAME} v{APP_VERSION} starting...")
    print("Open browser: http://127.0.0.1:5000")

    app.run(host="0.0.0.0", port=5000)
