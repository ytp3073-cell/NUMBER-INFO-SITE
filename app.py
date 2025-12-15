from flask import Flask, request, jsonify, render_template_string, session, redirect
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "OGGY_SECRET_KEY_CHANGE_ME"

# ---------------- ADMIN CONFIG ----------------
ADMIN_ID = "admin"
ADMIN_PASS = "admin123"

# ---------------- TEMP STORAGE (Vercel) ----------------
USERS = {}
# USERS = {
#   "username": {
#       "history": [
#           {time, type, value, result}
#       ]
#   }
# }

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>OGGY INFO SITE</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;font-family:Segoe UI;background:#0f0c29;color:#fff}
.card{max-width:750px;margin:auto;padding:20px}
input,button{width:100%;padding:12px;margin:6px 0;border-radius:10px;border:none}
button{background:linear-gradient(135deg,#ff0844,#ff512f);color:#fff;font-weight:bold;cursor:pointer}
.small{width:auto;padding:10px 14px}
.row{display:flex;gap:10px;flex-wrap:wrap}
pre{background:#111;padding:12px;border-radius:10px;max-height:300px;overflow:auto;white-space:pre-wrap}
a{color:#0ff;text-decoration:none}
</style>
</head>

<body>
<div class="card">

{% if not session.get("user") %}
<h2>👤 Enter Your Name</h2>
<form method="post" action="/set-user">
 <input name="username" placeholder="Your Name" required>
 <button>Continue</button>
</form>

{% else %}

<h3>Welcome, {{session['user']}}</h3>

<div class="row">
 <input id="num" placeholder="10 digit Mobile">
 <button onclick="mobile()">Check Mobile</button>
</div>

<div class="row">
 <input id="aad" placeholder="12 digit Aadhaar">
 <button onclick="aadhaar()">Check Aadhaar</button>
</div>

<div class="row">
 <button class="small" onclick="copy()">📋 Copy</button>
 <button class="small" onclick="clean()">🧹 Clean</button>
 <button class="small" onclick="loadHistory()">🕘 History</button>
 <button class="small" onclick="clearHistory()">🗑️ Clear History</button>
</div>

<pre id="out">Result will appear here...</pre>
<pre id="hist"></pre>

<hr>
<a href="/admin">🔐 Admin Login</a>

{% endif %}
</div>

<script>
function mobile(){
 fetch('/api/mobile?number='+num.value)
 .then(r=>r.json())
 .then(d=>out.textContent=JSON.stringify(d,null,2))
}
function aadhaar(){
 fetch('/api/aadhaar?aadhar='+aad.value)
 .then(r=>r.json())
 .then(d=>out.textContent=JSON.stringify(d,null,2))
}
function loadHistory(){
 fetch('/history')
 .then(r=>r.json())
 .then(d=>hist.textContent=JSON.stringify(d,null,2))
}
function clearHistory(){
 fetch('/clear-history').then(()=>hist.textContent="")
}
function copy(){navigator.clipboard.writeText(out.textContent||"")}
function clean(){out.textContent="";hist.textContent=""}
</script>
</body>
</html>
"""

# ---------------- ADMIN HTML ----------------
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Admin Panel</title>
<style>
body{font-family:Segoe UI;background:#111;color:#fff;padding:20px}
input,button{padding:10px;margin:5px;border-radius:8px;border:none}
button{background:#ff0844;color:#fff}
pre{background:#000;padding:12px;border-radius:10px;max-height:450px;overflow:auto;white-space:pre-wrap}
a{color:#0ff}
</style>
</head>
<body>

{% if not session.get("admin") %}
<h2>🔐 Admin Login</h2>
<form method="post">
 <input name="aid" placeholder="Admin ID">
 <input name="apass" type="password" placeholder="Password">
 <button>Login</button>
</form>

{% else %}
<h2>👑 Admin Dashboard</h2>
<a href="/admin/logout">Logout</a>

<h3>🔎 Search User</h3>
<form method="get">
 <input name="q" placeholder="Username">
 <button>Search</button>
</form>

<pre>{{ data }}</pre>
{% endif %}

</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/set-user", methods=["POST"])
def set_user():
    u = request.form.get("username", "").strip()
    if not u:
        return redirect("/")
    session["user"] = u
    USERS.setdefault(u, {"history": []})
    return redirect("/")

# ---------------- MOBILE API (FIXED) ----------------
@app.route("/api/mobile")
def mobile_api():
    user = session.get("user")
    number = request.args.get("number")

    r = requests.get(
        f"https://abbas-number-info.vercel.app/track?num={number}",
        timeout=15
    )

    try:
        data = r.json()
    except:
        data = {
            "success": False,
            "raw_output": r.text
        }

    USERS[user]["history"].append({
        "time": str(datetime.now()),
        "type": "mobile",
        "value": number,
        "result": data
    })

    return jsonify(data)

# ---------------- AADHAAR API (FIXED) ----------------
@app.route("/api/aadhaar")
def aadhaar_api():
    user = session.get("user")
    a = request.args.get("aadhar")

    r = requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={a}",
        timeout=15
    )

    try:
        data = r.json()
    except:
        data = {
            "success": False,
            "raw_output": r.text
        }

    USERS[user]["history"].append({
        "time": str(datetime.now()),
        "type": "aadhaar",
        "value": a,
        "result": data
    })

    return jsonify(data)

@app.route("/history")
def history():
    return jsonify(USERS.get(session.get("user"), {}).get("history", []))

@app.route("/clear-history")
def clear_history():
    u = session.get("user")
    if u in USERS:
        USERS[u]["history"] = []
    return "ok"

# ---------------- ADMIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("aid") == ADMIN_ID and request.form.get("apass") == ADMIN_PASS:
            session["admin"] = True

    if not session.get("admin"):
        return render_template_string(ADMIN_HTML)

    q = request.args.get("q")
    data = USERS if not q else {q: USERS.get(q)}
    return render_template_string(ADMIN_HTML, data=data)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

# --------- VERCEL ENTRY ---------
app = app
