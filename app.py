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

/* WATERMARK */
body::before{
 content:"Devlaper TELEGRAM USERNAME @BAN8T  •  ";
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
.dev{
 font-size:13px;letter-spacing:2px;
 color:var(--glow);animation:glow 2.5s infinite;
}
.dev a{color:inherit;text-decoration:none}
@keyframes glow{
 0%{opacity:.5}50%{opacity:1}100%{opacity:.5}
}

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
.error{font-size:12px;color:#ffd0d0;display:none}

button{
 width:100%;padding:15px;border:none;
 border-radius:16px;
 background:linear-gradient(135deg,var(--btn1),var(--btn2));
 color:#fff;font-weight:bold;cursor:pointer;
 margin-bottom:8px;
}
button:disabled{opacity:.5;cursor:not-allowed}
.loading::after{content:" ⏳";animation:pulse 1s infinite}
@keyframes pulse{0%{opacity:.4}50%{opacity:1}100%{opacity:.4}}

.actions{display:flex;gap:10px}
button.small{padding:12px;font-size:13px}

pre{
 background:var(--box);padding:16px;
 border-radius:16px;font-size:13px;
 max-height:300px;overflow-y:auto;
}

.history{
 display:none;margin-top:12px;
 background:var(--box);padding:12px;
 border-radius:14px;font-size:12px;
 max-height:160px;overflow-y:auto;
}

.footer{
 margin-top:auto;text-align:center;
 font-size:13px;letter-spacing:2px;
 background:linear-gradient(135deg,#ff0844,#ff512f);
 -webkit-background-clip:text;
 -webkit-text-fill-color:transparent;
}

#topBtn{
 position:fixed;bottom:26px;right:26px;
 width:66px;height:66px;border-radius:50%;
 border:none;font-size:26px;
 background:linear-gradient(135deg,var(--btn1),var(--btn2));
 color:#fff;cursor:pointer;display:none;
}
</style>
</head>

<body>
<div class="card" id="top">
 <div class="toggle" onclick="toggleMode()">🌙 / ☀️</div>

 <div class="top">
  <h1>OGGY INFO SITE</h1>
  <div class="dev">Developer :
   <a href="https://t.me/BAN8T" target="_blank">@BAN8T</a>
  </div>
 </div>

 <div class="tabs">
  <div class="tab active" onclick="tab('mobile',this)">📱 Mobile</div>
  <div class="tab" onclick="tab('aadhaar',this)">🆔 Aadhaar</div>
 </div>

 <div id="mobile" class="section active">
  <input id="m" placeholder="Enter 10 digit Mobile"
   inputmode="numeric" maxlength="10"
   oninput="vm()">
  <div class="error" id="me">Enter exactly 10 digits</div>
  <button id="mb" onclick="cm()" disabled>Check Mobile</button>
 </div>

 <div id="aadhaar" class="section">
  <input id="a" placeholder="Enter 12 digit Aadhaar"
   inputmode="numeric" maxlength="12"
   oninput="va()">
  <div class="error" id="ae">Enter exactly 12 digits</div>
  <button id="ab" onclick="ca()" disabled>Check Aadhaar</button>
 </div>

 <div class="actions">
  <button class="small" onclick="copy()">📋 Copy</button>
  <button class="small" onclick="clearR()">🧹 Clear</button>
 </div>

 <pre id="out">Result will appear here...</pre>

 <div class="actions">
  <button class="small" onclick="th()">🕘 History</button>
  <button class="small" onclick="ch()">🗑️ Clear History</button>
 </div>
 <div class="history" id="h"></div>

 <div class="footer">2025 : OGGY INFO SITE</div>
</div>

<button id="topBtn" onclick="scrollTo({top:0,behavior:'smooth'})">⬆</button>

<script>
let hist=[],timer=null;
if(localStorage.theme==="light")document.body.classList.add("light");
function toggleMode(){
 document.body.classList.toggle("light");
 localStorage.theme=document.body.classList.contains("light")?"light":"dark";
}
function tab(id,e){
 document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
 document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
 e.classList.add('active');document.getElementById(id).classList.add('active');
 clearR();
}
function d(el,max){el.value=el.value.replace(/\\D/g,'').slice(0,max)}
function vm(){d(m,10);me.style.display=m.value.length==10?"none":"block";mb.disabled=m.value.length!=10}
function va(){d(a,12);ae.style.display=a.value.length==12?"none":"block";ab.disabled=a.value.length!=12}
function load(b,s){
 if(s){b.disabled=true;b.dataset.t=b.innerText;b.innerText="Checking";b.classList.add("loading")}
 else{b.disabled=false;b.innerText=b.dataset.t;b.classList.remove("loading")}
}
function show(d,l){
 out.textContent=JSON.stringify(d,null,2);
 hist.unshift(l);if(hist.length>20)hist.pop();
 h.innerHTML=hist.map(x=>"<div>"+x+"</div>").join("");
 if(timer)clearTimeout(timer);
 timer=setTimeout(clearR,60000);
}
function cm(){
 load(mb,true);
 fetch('/api/mobile?number='+m.value).then(r=>r.json()).then(d=>show(d,"📱 "+m.value))
 .finally(()=>load(mb,false));
}
function ca(){
 load(ab,true);
 fetch('/api/aadhaar?aadhar='+a.value).then(r=>r.json()).then(d=>show(d,"🆔 "+a.value))
 .finally(()=>load(ab,false));
}
function copy(){navigator.clipboard.writeText(out.textContent||"")}
function clearR(){out.textContent="";m.value="";a.value="";mb.disabled=true;ab.disabled=true}
function th(){h.style.display=h.style.display=="none"?"block":"none"}
function ch(){hist=[];h.innerHTML=""}
window.onscroll=()=>topBtn.style.display=scrollY>200?"block":"none";
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
        timeout=15).json())

@app.route("/api/aadhaar")
def aadhaar_api():
    return jsonify(requests.get(
        f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={request.args.get('aadhar')}",
        timeout=15).json())

if __name__=="__main__":
    app.run()
