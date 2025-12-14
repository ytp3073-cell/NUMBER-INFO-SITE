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

  --card:rgba(255,255,255,0.16);
  --text:#ffffff;

  --btn1:#ff0844;
  --btn2:#ff512f;

  --box:rgba(0,0,0,.45);
  --glow:#ff2f6d;
}

body.light{
  --bg1:#ffecec;
  --bg2:#ffd6e0;
  --bg3:#fff0f5;

  --card:rgba(255,255,255,0.97);
  --text:#000;

  --btn1:#ff3b3b;
  --btn2:#ff6a6a;

  --box:#ffe9ef;
  --glow:#ff3b3b;
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
  animation:bgMove 14s ease infinite;
  color:var(--text);
  position:relative;
  overflow:hidden;
}

/* 🔁 REPEATED + MOVING WATERMARK */
body::before{
  content:"Devlaper TELEGRAM USERNAME @BAN8T  •  ";
  position:fixed;
  inset:-200%;
  font-size:clamp(16px,3.5vw,42px);
  font-weight:800;
  letter-spacing:3px;
  color:rgba(255,255,255,0.06);
  white-space:nowrap;
  transform:rotate(-25deg);
  pointer-events:none;
  z-index:0;
  animation:waterMove 60s linear infinite;
}

/* Mobile watermark smaller */
@media (max-width:600px){
  body::before{
    font-size:14px;
    letter-spacing:2px;
    animation-duration:80s;
  }
}

@keyframes waterMove{
  0%{transform:translateX(0) rotate(-25deg)}
  100%{transform:translateX(-50%) rotate(-25deg)}
}

@keyframes bgMove{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

/* CARD */
.card{
  width:98%;
  max-width:640px;
  min-height:88vh;
  padding:40px 28px;
  border-radius:24px;
  background:var(--card);
  backdrop-filter:blur(22px);
  box-shadow:0 0 80px rgba(255,47,109,.35);
  display:flex;
  flex-direction:column;
  position:relative;
  z-index:1;
}

/* HEADER */
.topbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:18px;
}
h1{margin:0;font-size:24px}

.toggle{
  cursor:pointer;
  font-size:14px;
  padding:8px 18px;
  border-radius:30px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  color:#fff;
}

/* TABS */
.tabs{display:flex;margin:20px 0}
.tab{
  flex:1;
  padding:14px;
  cursor:pointer;
  border-radius:18px;
  background:rgba(255,255,255,.18);
  color:var(--text);
  text-align:center;
}
.tab.active{
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  color:#fff;
  font-weight:bold;
}

/* INPUT + BUTTON */
.section{display:none}
.section.active{display:block}

input{
  width:100%;
  padding:15px;
  border-radius:16px;
  border:none;
  margin-bottom:10px;
  font-size:15px;
}

button{
  width:100%;
  padding:15px;
  border:none;
  border-radius:18px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  font-weight:bold;
  cursor:pointer;
  margin-bottom:8px;
  color:#fff;
  box-shadow:0 6px 20px rgba(255,47,109,.45);
}
button.small{
  padding:12px;
  font-size:13px;
}
.actions{display:flex;gap:10px}

/* RESULT */
pre{
  background:var(--box);
  padding:16px;
  border-radius:16px;
  max-height:260px;
  overflow-y:auto;
  white-space:pre-wrap;
  word-break:break-word;
  font-size:13px;
}

/* HISTORY */
.history{
  display:none;
  margin-top:14px;
  background:var(--box);
  padding:12px;
  border-radius:16px;
  font-size:12px;
  max-height:160px;
  overflow-y:auto;
}
.history div{
  border-bottom:1px solid rgba(255,255,255,.2);
  padding:4px 0;
}

/* FOOTER */
.footer{
  margin-top:auto;
  text-align:center;
  padding-top:22px;
  font-size:13px;
  letter-spacing:2px;
  font-weight:bold;
  background:linear-gradient(135deg,#ff0844,#ff512f);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  animation:glow 3s ease-in-out infinite;
}
@keyframes glow{
  0%{text-shadow:0 0 10px #ff0844}
  50%{text-shadow:0 0 28px #ff512f}
  100%{text-shadow:0 0 10px #ff0844}
}

/* BACK TO TOP */
#topBtn{
  position:fixed;
  bottom:26px;
  right:26px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  border:none;
  border-radius:50%;
  width:66px;
  height:66px;
  cursor:pointer;
  font-size:26px;
  display:none;
  color:#fff;
  box-shadow:0 0 30px rgba(255,47,109,.9);
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
    return jsonify(requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=NEXTGEN&number={request.args.get('number')}",
        timeout=15
    ).json())

@app.route("/api/aadhaar")
def aadhaar_api():
    return jsonify(requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={request.args.get('aadhar')}",
        timeout=15
    ).json())
