from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OGGY INFO SITE</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
:root{
  --bg1:#0a1a2f;
  --bg2:#0b2b4f;
  --card:rgba(255,255,255,0.12);
  --text:#ffffff;
  --btn1:#00c6ff;
  --btn2:#0072ff;
  --box:rgba(0,0,0,.45);
  --glow:#00c6ff;
}
body.light{
  --bg1:#e6f2ff;
  --bg2:#cce6ff;
  --card:rgba(255,255,255,0.9);
  --text:#000;
  --btn1:#1e90ff;
  --btn2:#0066cc;
  --box:#eef6ff;
  --glow:#1e90ff;
}
*{box-sizing:border-box;font-family:'Segoe UI',sans-serif}
html{scroll-behavior:smooth}

body{
  margin:0;min-height:100vh;
  display:flex;align-items:center;justify-content:center;
  background:linear-gradient(-45deg,var(--bg1),var(--bg2));
  background-size:400% 400%;
  animation:gradient 10s ease infinite;
  color:var(--text);
}
@keyframes gradient{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

.card{
  width:95%;max-width:500px;
  padding:22px;border-radius:18px;
  background:var(--card);
  backdrop-filter:blur(18px);
  box-shadow:0 0 40px rgba(0,0,0,.5);
}

.topbar{
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:10px;
}
h1{margin:0;font-size:22px}

.toggle{
  cursor:pointer;font-size:14px;
  padding:6px 12px;border-radius:20px;
  background:var(--box);
}

.tabs{display:flex;margin:12px 0}
.tab{
  flex:1;padding:10px;cursor:pointer;
  border:1px solid rgba(255,255,255,.3);
  background:transparent;color:var(--text);
  text-align:center;
}
.tab.active{background:rgba(255,255,255,.25)}

.section{display:none}
.section.active{display:block}

input{
  width:100%;padding:11px;
  border-radius:10px;border:none;
  margin-bottom:8px;
}

button{
  width:100%;padding:11px;
  border:none;border-radius:10px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  font-weight:bold;cursor:pointer;
  margin-bottom:6px;
  color:#000;
}
button.small{padding:8px;font-size:13px}
.actions{display:flex;gap:6px}

/* RESULT – thodi scroll */
pre{
  background:var(--box);
  padding:12px;
  border-radius:10px;
  max-height:180px;
  overflow-y:auto;
  white-space:pre-wrap;
  word-break:break-word;
  font-size:13px;
}

/* HISTORY (SAFE – clear nahi hogi) */
.history{
  margin-top:8px;
  background:var(--box);
  padding:8px;
  border-radius:10px;
  font-size:12px;
  max-height:120px;
  overflow-y:auto;
}
.history div{
  border-bottom:1px solid rgba(255,255,255,.2);
  padding:4px 0;
}

/* FOOTER GLOW */
.footer{
  text-align:center;
  margin-top:16px;
  font-size:13px;
  letter-spacing:2px;
  font-weight:bold;
  color:var(--glow);
  animation:glow 2.5s ease-in-out infinite;
}
@keyframes glow{
  0%{text-shadow:0 0 5px var(--glow);opacity:.6}
  50%{
    text-shadow:
      0 0 10px var(--glow),
      0 0 20px var(--glow),
      0 0 30px var(--glow);
    opacity:1
  }
  100%{text-shadow:0 0 5px var(--glow);opacity:.6}
}

/* BACK TO TOP */
#topBtn{
  position:fixed;
  bottom:20px;
  right:20px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  border:none;
  border-radius:50%;
  width:45px;
  height:45px;
  cursor:pointer;
  font-size:18px;
  display:none;
}
</style>
</head>

<body class="dark">

<div class="card" id="top">
  <div class="topbar">
    <h1>🔍 INFO LOOKUP</h1>
    <div class="toggle" onclick="toggleMode()">🌙 / ☀️</div>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="tabSwitch('mobile',this)">📱 Mobile</div>
    <div class="tab" onclick="tabSwitch('aadhaar',this)">🆔 Aadhaar</div>
  </div>

  <div id="mobile" class="section active">
    <input id="m" placeholder="Enter Mobile Number">
    <button onclick="checkMobile()">Check Mobile</button>
  </div>

  <div id="aadhaar" class="section">
    <input id="a" placeholder="Enter Aadhaar Number">
    <button onclick="checkAadhaar()">Check Aadhaar</button>
  </div>

  <div class="actions">
    <button class="small" onclick="copyResult()">📋 Copy</button>
    <button class="small" onclick="clearResult()">🧹 Clear</button>
  </div>

  <pre id="out">Result will appear here...</pre>

  <div class="history" id="history"></div>

  <div class="footer">2025 : OGGY INFO SITE</div>
</div>

<button id="topBtn" onclick="scrollTop()">⬆</button>

<script>
let autoClearTimer = null;
let historyData = [];

function toggleMode(){
  document.body.classList.toggle("light");
}

function tabSwitch(id, el){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(id).classList.add('active');
  clearResult();
}

function startAutoClear(){
  if(autoClearTimer) clearTimeout(autoClearTimer);
  autoClearTimer = setTimeout(clearResult, 60000); // ⏱️ 1 minute
}

function showResult(data,label){
  out.textContent = typeof data === 'object'
    ? JSON.stringify(data,null,2)
    : data;
  if(label) addHistory(label);
  startAutoClear();
}

function clearResult(){
  out.textContent = "";
  m.value = "";
  a.value = "";
}

function copyResult(){
  navigator.clipboard.writeText(out.textContent || "");
  alert("Result copied");
}

function addHistory(text){
  historyData.unshift(text);
  if(historyData.length > 20) historyData.pop();
  history.innerHTML = historyData.map(h=>"<div>"+h+"</div>").join("");
}

function checkMobile(){
  if(!m.value) return;
  fetch('/api/mobile?number='+m.value)
    .then(r=>r.json())
    .then(d=>showResult(d,"📱 "+m.value));
}

function checkAadhaar(){
  if(!a.value) return;
  fetch('/api/aadhaar?aadhar='+a.value)
    .then(r=>r.json())
    .then(d=>showResult(d,"🆔 "+a.value));
}

window.onscroll = function(){
  topBtn.style.display = window.scrollY > 200 ? "block" : "none";
}
function scrollTop(){
  window.scrollTo({top:0,behavior:'smooth'});
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/mobile")
def mobile_api():
    number = request.args.get("number")
    if not number:
        return jsonify({"error":"number missing"})
    url = f"https://darkie.x10.mx/numapi.php?action=api&key=NEXTGEN&number={number}"
    return jsonify(requests.get(url, timeout=15).json())

@app.route("/api/aadhaar")
def aadhaar_api():
    a = request.args.get("aadhar")
    if not a:
        return jsonify({"error":"aadhar missing"})
    url = f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={a}"
    return jsonify(requests.get(url, timeout=15).json())
