from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>OGGY INFO SITE</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
 --bg1:#0f0c29;--bg2:#302b63;--bg3:#ff4ecd;
 --card:rgba(255,255,255,.18);
 --text:#fff;
 --btn1:#ff0844;--btn2:#ff512f;
 --box:rgba(0,0,0,.45);
 --glow:#ff2f6d;
}
body.light{
 --bg1:#fff0f5;--bg2:#ffe6ec;--bg3:#ffd6e0;
 --card:#fff;--text:#000;
 --btn1:#ff3b3b;--btn2:#ff6a6a;
 --box:#f4f4f4;
}
*{box-sizing:border-box;font-family:Segoe UI,sans-serif}
body{
 margin:0;min-height:100vh;
 display:flex;justify-content:center;align-items:center;
 background:linear-gradient(-45deg,var(--bg1),var(--bg2),var(--bg3));
 background-size:400% 400%;
 animation:bg 14s infinite;
 color:var(--text);overflow:hidden;
}
@keyframes bg{
 0%{background-position:0% 50%}
 50%{background-position:100% 50%}
 100%{background-position:0% 50%}
}
body::before{
 content:"Developer TELEGRAM USERNAME @BAN8T  •  ";
 position:fixed;inset:-200%;
 font-size:clamp(16px,4vw,44px);
 font-weight:800;letter-spacing:3px;
 color:rgba(255,255,255,.06);
 white-space:nowrap;
 transform:rotate(-25deg);
 animation:wm 60s linear infinite;
 pointer-events:none;
}
@keyframes wm{
 from{transform:translateX(0) rotate(-25deg)}
 to{transform:translateX(-50%) rotate(-25deg)}
}
.card{
 width:96%;max-width:650px;min-height:90vh;
 padding:40px 28px;border-radius:24px;
 background:var(--card);backdrop-filter:blur(20px);
 box-shadow:0 0 80px rgba(255,47,109,.4);
 display:flex;flex-direction:column;z-index:1;
}
.top{text-align:center;margin-bottom:20px}
.top h1{margin:0;font-size:26px}
.dev{font-size:13px;letter-spacing:2px;color:var(--glow)}
.toggle{
 position:absolute;top:20px;right:20px;
 padding:8px 16px;border-radius:20px;
 background:linear-gradient(135deg,var(--btn1),var(--btn2));
 cursor:pointer;color:#fff;font-size:13px;
}
.tabs{display:flex;gap:10px;margin:18px 0}
.tab{
 flex:1;padding:14px;border-radius:16px;
 background:rgba(255,255,255,.2);
 text-align:center;cursor:pointer;
}
.tab.active{background:linear-gradient(135deg,var(--btn1),var(--btn2))}
.section{display:none}
.section.active{display:block}
input{
 width:100%;padding:15px;border-radius:14px;
 border:none;margin-bottom:6px;font-size:15px;
}
button{
 width:100%;padding:15px;border:none;
 border-radius:16px;
 background:linear-gradient(135deg,var(--btn1),var(--btn2));
 color:#fff;font-weight:bold;cursor:pointer;
 margin-bottom:8px;
}
pre{
 background:var(--box);padding:16px;
 border-radius:16px;font-size:13px;
 max-height:300px;overflow-y:auto;
}
</style>
</head>

<body>
<div class="card">
 <div class="toggle" onclick="document.body.classList.toggle('light')">🌙 / ☀️</div>

 <div class="top">
  <h1>OGGY INFO SITE</h1>
  <div class="dev">Developer : <a href="https://t.me/BAN8T" target="_blank">@BAN8T</a></div>
 </div>

 <div class="tabs">
  <div class="tab active" onclick="showTab('mobile',this)">📱 Mobile</div>
  <div class="tab" onclick="showTab('aadhaar',this)">🆔 Aadhaar</div>
 </div>

 <div id="mobile" class="section active">
  <input id="m" placeholder="Enter 10 digit Mobile" maxlength="10" oninput="checkM()">
  <button id="mb" onclick="cm()" disabled>Check Mobile</button>
 </div>

 <div id="aadhaar" class="section">
  <input id="a" placeholder="Enter 12 digit Aadhaar" maxlength="12" oninput="checkA()">
  <button id="ab" onclick="ca()" disabled>Check Aadhaar</button>
 </div>

 <pre id="out">Result will appear here...</pre>
</div>

<script>
function showTab(id,e){
 document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
 document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
 e.classList.add('active');
 document.getElementById(id).classList.add('active');
}

function checkM(){ mb.disabled = m.value.length !== 10 }
function checkA(){ ab.disabled = a.value.length !== 12 }

function cm(){
 out.textContent="Loading...";
 fetch('/api/mobile?number='+m.value)
 .then(r=>r.json())
 .then(d=>out.textContent=JSON.stringify(d,null,2))
 .catch(()=>out.textContent="Error fetching data");
}

function ca(){
 out.textContent="Loading...";
 fetch('/api/aadhaar?aadhar='+a.value)
 .then(r=>r.json())
 .then(d=>out.textContent=JSON.stringify(d,null,2))
 .catch(()=>out.textContent="Error fetching data");
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

# 📱 MOBILE API
@app.route("/api/mobile")
def mobile_api():
    number = request.args.get("number", "")
    if not number.isdigit() or len(number) != 10:
        return jsonify({"error": "Invalid mobile number"}), 400
    try:
        url = f"https://abbas-number-info.vercel.app/track?num={number}"
        r = requests.get(url, timeout=15)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🆔 AADHAAR API
@app.route("/api/aadhaar")
def aadhaar_api():
    aadhar = request.args.get("aadhar", "")
    if not aadhar.isdigit() or len(aadhar) != 12:
        return jsonify({"error": "Invalid Aadhaar number"}), 400
    try:
        url = (
            "https://darkie.x10.mx/numapi.php"
            "?action=api&key=aa89dd725a6e5773ed4384fce8103d8a"
            f"&aadhar={aadhar}"
        )
        r = requests.get(url, timeout=15)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
