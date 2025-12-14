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
  --bg1:#0f0c29;
  --bg2:#302b63;
  --bg3:#ff4ecd;
  --card:rgba(255,255,255,0.14);
  --text:#ffffff;
  --btn1:#00c6ff;
  --btn2:#ff4ecd;
  --box:rgba(0,0,0,.45);
  --glow:#ff4ecd;
}
body.light{
  --bg1:#e6f0ff;
  --bg2:#ffd6f0;
  --bg3:#cce0ff;
  --card:rgba(255,255,255,0.95);
  --text:#000;
  --btn1:#1e90ff;
  --btn2:#ff4ecd;
  --box:#eef3ff;
  --glow:#ff4ecd;
}

*{box-sizing:border-box;font-family:'Segoe UI',sans-serif}
html{scroll-behavior:smooth}

body{
  margin:0;
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  background:linear-gradient(-45deg,var(--bg1),var(--bg2),var(--bg3));
  background-size:400% 400%;
  animation:bgMove 12s ease infinite;
  color:var(--text);
}
@keyframes bgMove{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

.card{
  width:98%;
  max-width:640px;
  padding:26px;
  border-radius:20px;
  background:var(--card);
  backdrop-filter:blur(20px);
  box-shadow:0 0 60px rgba(255,78,205,.35);
}

.topbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:12px;
}
h1{margin:0;font-size:23px}

.toggle{
  cursor:pointer;
  font-size:14px;
  padding:7px 14px;
  border-radius:22px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  color:#000;
}

.tabs{display:flex;margin:14px 0}
.tab{
  flex:1;
  padding:13px;
  cursor:pointer;
  border-radius:14px;
  background:rgba(255,255,255,.12);
  color:var(--text);
  text-align:center;
}
.tab.active{
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  color:#000;
  font-weight:bold;
}

.section{display:none}
.section.active{display:block}

input{
  width:100%;
  padding:13px;
  border-radius:12px;
  border:none;
  margin-bottom:8px;
}

button{
  width:100%;
  padding:13px;
  border:none;
  border-radius:14px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  font-weight:bold;
  cursor:pointer;
  margin-bottom:6px;
  color:#000;
}
button.small{padding:10px;font-size:13px}
.actions{display:flex;gap:8px}

pre{
  background:var(--box);
  padding:15px;
  border-radius:14px;
  max-height:260px;
  overflow-y:auto;
  white-space:pre-wrap;
  word-break:break-word;
  font-size:13px;
}

.history{
  display:none;
  margin-top:10px;
  background:var(--box);
  padding:10px;
  border-radius:14px;
  font-size:12px;
  max-height:160px;
  overflow-y:auto;
}
.history div{
  border-bottom:1px solid rgba(255,255,255,.2);
  padding:4px 0;
}

.footer{
  text-align:center;
  margin-top:18px;
  font-size:13px;
  letter-spacing:2px;
  font-weight:bold;
  background:linear-gradient(135deg,#00c6ff,#ff4ecd);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  animation:glow 3s ease-in-out infinite;
}
@keyframes glow{
  0%{text-shadow:0 0 8px #00c6ff}
  50%{text-shadow:0 0 20px #ff4ecd}
  100%{text-shadow:0 0 8px #00c6ff}
}

#topBtn{
  position:fixed;
  bottom:24px;
  right:24px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  border:none;
  border-radius:50%;
  width:62px;
  height:62px;
  cursor:pointer;
  font-size:26px;
  display:none;
  box-shadow:0 0 25px rgba(255,78,205,.8);
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

  <div class="actions">
    <button class="small" onclick="toggleHistory()">🕘 History</button>
    <button class="small" onclick="clearHistory()">🗑️ Clear History</button>
  </div>

  <div class="history" id="history"></div>

  <div class="footer">2025 : OGGY INFO SITE</div>
</div>

<button id="topBtn" onclick="scrollTop()">⬆</button>

<script>
let autoClearTimer=null;
let historyData=[];

function toggleMode(){document.body.classList.toggle("light");}
function tabSwitch(id,el){
 document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
 document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
 el.classList.add('active');
 document.getElementById(id).classList.add('active');
 clearResult();
}
function startAutoClear(){
 if(autoClearTimer)clearTimeout(autoClearTimer);
 autoClearTimer=setTimeout(clearResult,60000);
}
function showResult(d,label){
 out.textContent=typeof d==='object'?JSON.stringify(d,null,2):d;
 if(label)addHistory(label);
 startAutoClear();
}
function clearResult(){out.textContent="";m.value="";a.value="";}
function copyResult(){navigator.clipboard.writeText(out.textContent||"");}
function toggleHistory(){history.style.display=history.style.display==="none"?"block":"none";}
function addHistory(t){
 historyData.unshift(t);
 if(historyData.length>20)historyData.pop();
 history.innerHTML=historyData.map(h=>"<div>"+h+"</div>").join("");
}
function clearHistory(){historyData=[];history.innerHTML="";}
function checkMobile(){
 if(!m.value)return;
 fetch('/api/mobile?number='+m.value).then(r=>r.json()).then(d=>showResult(d,"📱 "+m.value));
}
function checkAadhaar(){
 if(!a.value)return;
 fetch('/api/aadhaar?aadhar='+a.value).then(r=>r.json()).then(d=>showResult(d,"🆔 "+a.value));
}
window.onscroll=()=>{topBtn.style.display=window.scrollY>200?"block":"none";}
function scrollTop(){window.scrollTo({top:0,behavior:'smooth'});}
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
    return jsonify(requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=NEXTGEN&number={number}",
        timeout=15
    ).json())

@app.route("/api/aadhaar")
def aadhaar_api():
    a = request.args.get("aadhar")
    return jsonify(requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={a}",
        timeout=15
    ).json())
