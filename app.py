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
  --card:rgba(255,255,255,0.18);
  --text:#ffffff;
  --btn1:#ff0844;
  --btn2:#ff512f;
  --box:rgba(0,0,0,.45);
  --glow:#ff2f6d;
}

*{box-sizing:border-box;font-family:Segoe UI,sans-serif}

body{
  margin:0;
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  background:linear-gradient(-45deg,var(--bg1),var(--bg2),var(--bg3));
  background-size:400% 400%;
  animation:bg 12s ease infinite;
  color:var(--text);
}

@keyframes bg{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

.card{
  width:95%;
  max-width:620px;
  min-height:85vh;
  background:var(--card);
  backdrop-filter:blur(18px);
  border-radius:22px;
  padding:36px 26px;
  box-shadow:0 0 60px rgba(255,47,109,.4);
}

h1{
  text-align:center;
  margin:0;
}

.dev{
  text-align:center;
  font-size:13px;
  color:var(--glow);
  margin-bottom:22px;
}

.tabs{
  display:flex;
  gap:10px;
  margin-bottom:20px;
}

.tab{
  flex:1;
  padding:14px;
  text-align:center;
  border-radius:16px;
  cursor:pointer;
  background:rgba(255,255,255,.2);
}

.tab.active{
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
}

.section{display:none}
.section.active{display:block}

input{
  width:100%;
  padding:15px;
  border-radius:14px;
  border:none;
  margin-bottom:6px;
  font-size:15px;
}

.error{
  font-size:12px;
  color:#ffd0d0;
  margin-bottom:8px;
  display:none;
}

button{
  width:100%;
  padding:15px;
  border:none;
  border-radius:16px;
  background:linear-gradient(135deg,var(--btn1),var(--btn2));
  color:#fff;
  font-weight:bold;
  cursor:pointer;
}

button:disabled{
  opacity:.5;
  cursor:not-allowed;
}

.loading::after{
  content:" ⏳";
  animation:pulse 1s infinite;
}

@keyframes pulse{
  0%{opacity:.4}
  50%{opacity:1}
  100%{opacity:.4}
}

pre{
  margin-top:18px;
  background:var(--box);
  padding:16px;
  border-radius:16px;
  max-height:260px;
  overflow-y:auto;
  font-size:13px;
}
</style>
</head>

<body>

<div class="card">

<h1>OGGY INFO SITE</h1>
<div class="dev">Developer : @BAN8T</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('mobile',this)">📱 Mobile</div>
  <div class="tab" onclick="switchTab('aadhaar',this)">🆔 Aadhaar</div>
</div>

<!-- MOBILE -->
<div id="mobile" class="section active">
  <input id="m" placeholder="Enter 10 digit Mobile Number"
         inputmode="numeric" maxlength="10"
         oninput="validateMobile()">
  <div class="error" id="mErr">Enter exactly 10 digits</div>
  <button id="mBtn" onclick="checkMobile()" disabled>Check Mobile</button>
</div>

<!-- AADHAAR -->
<div id="aadhaar" class="section">
  <input id="a" placeholder="Enter 12 digit Aadhaar Number"
         inputmode="numeric" maxlength="12"
         oninput="validateAadhaar()">
  <div class="error" id="aErr">Enter exactly 12 digits</div>
  <button id="aBtn" onclick="checkAadhaar()" disabled>Check Aadhaar</button>
</div>

<pre id="out">Result will appear here...</pre>

</div>

<script>
function switchTab(id,el){
 document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
 document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
 el.classList.add('active');
 document.getElementById(id).classList.add('active');
 out.textContent="";
}

function onlyDigits(el,max){
 el.value = el.value.replace(/\\D/g,'').slice(0,max);
}

function validateMobile(){
 onlyDigits(m,10);
 if(m.value.length===10){
   mErr.style.display="none";
   mBtn.disabled=false;
 }else{
   mErr.style.display="block";
   mBtn.disabled=true;
 }
}

function validateAadhaar(){
 onlyDigits(a,12);
 if(a.value.length===12){
   aErr.style.display="none";
   aBtn.disabled=false;
 }else{
   aErr.style.display="block";
   aBtn.disabled=true;
 }
}

function setLoading(btn,state){
 if(state){
   btn.disabled=true;
   btn.dataset.txt=btn.innerText;
   btn.innerText="Checking";
   btn.classList.add("loading");
 }else{
   btn.disabled=false;
   btn.innerText=btn.dataset.txt;
   btn.classList.remove("loading");
 }
}

function checkMobile(){
 setLoading(mBtn,true);
 fetch('/api/mobile?number='+m.value)
  .then(r=>r.json())
  .then(d=>out.textContent=JSON.stringify(d,null,2))
  .finally(()=>setLoading(mBtn,false));
}

function checkAadhaar(){
 setLoading(aBtn,true);
 fetch('/api/aadhaar?aadhar='+a.value)
  .then(r=>r.json())
  .then(d=>out.textContent=JSON.stringify(d,null,2))
  .finally(()=>setLoading(aBtn,false));
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
    return jsonify(
        requests.get(
            f"https://darkie.x10.mx/numapi.php?action=api&key=NEXTGEN&number={request.args.get('number')}",
            timeout=15
        ).json()
    )

@app.route("/api/aadhaar")
def aadhaar_api():
    return jsonify(
        requests.get(
            f"https://darkie.x10.mx/numapi.php?action=api&key=aa89dd725a6e5773ed4384fce8103d8a&aadhar={request.args.get('aadhar')}",
            timeout=15
        ).json()
    )

if __name__ == "__main__":
    app.run(debug=True)
