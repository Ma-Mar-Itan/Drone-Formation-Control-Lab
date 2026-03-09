"""
Drone Formation Control Lab
============================
Smooth 60 fps simulation rendered entirely on an HTML5 Canvas via
st.components.v1.html — zero Streamlit reruns during the animation loop.
All physics, control laws, and rendering run in JavaScript.
Streamlit only hosts the sidebar controls and passes config as JSON.
"""

import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Drone Formation Control Lab",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── White-theme CSS for the Streamlit shell ──────────────────────────────────
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main,.block-container{
  background:#fff!important;color:#1a1a2e!important}
[data-testid="stSidebar"]{background:#f8f9fc!important;border-right:1px solid #e2e8f0}
[data-testid="stSidebar"] *{color:#1a1a2e!important}
h1{color:#1a1a2e!important;font-weight:800!important}
h2{color:#312e81!important;font-weight:700!important}
h3{color:#4338ca!important;font-weight:600!important}
.stButton>button{background:#4f46e5;color:#fff!important;border:none;border-radius:8px;
  padding:8px 18px;font-weight:600;font-size:.85rem}
.stButton>button:hover{background:#4338ca}
[data-testid="stSlider"]>div>div{background:#c7d2fe}
hr{border-color:#e2e8f0!important}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-thumb{background:#c7d2fe;border-radius:3px}
.streamlit-expanderHeader{background:#eef2ff!important;border-radius:8px!important;
  font-weight:600!important;color:#312e81!important}
</style>
""", unsafe_allow_html=True)

# ── Sidebar controls ─────────────────────────────────────────────────────────
CONTROL_DESCRIPTIONS = {
    "Leader-Follower":   "One designated leader; others maintain relative offsets. Simple but fragile — leader failure propagates errors.",
    "Consensus-Based":   "Agents average neighbour states iteratively. Convergent and robust; requires connectivity.",
    "Behavior-Based":    "Emergent formation from blended local behaviours: separation, cohesion, alignment, goal-seeking.",
    "Virtual Structure": "Formation treated as a rigid virtual body; each drone tracks its slot via PD control. High fidelity.",
    "Potential Field":   "Goal positions attract; drones and obstacles repel via inverse-square fields. Physically intuitive.",
}

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    st.markdown("### 🚁 Swarm")
    n_drones = st.slider("Number of Drones", 4, 40, 12)

    st.markdown("### 🧠 Control Mode")
    control_mode = st.selectbox("Mode", list(CONTROL_DESCRIPTIONS.keys()), index=3)
    with st.expander("ℹ️ Mode description"):
        st.caption(CONTROL_DESCRIPTIONS[control_mode])

    st.markdown("### 🔷 Formation")
    formation = st.selectbox("Formation", [
        "Circle","Line","Column","V-Shape","Square","Wedge","Grid","Ring","Spiral","Expanding Wave"
    ], index=0)

    st.markdown("### 📐 Formation Transform")
    form_cx       = st.slider("Center X", -60, 60, 0)
    form_cy       = st.slider("Center Y", -60, 60, 0)
    form_scale    = st.slider("Scale", 0.3, 3.0, 1.0, 0.1)
    form_rotation = st.slider("Rotation (°)", 0, 360, 0)

    st.markdown("### 📡 Communication")
    comm_radius  = st.slider("Comm. Radius",  10, 80, 35)
    sense_radius = st.slider("Sensing Radius", 5, 50, 20)

    st.markdown("### 🏎️ Dynamics")
    max_speed   = st.slider("Max Speed",  1.0, 25.0, 8.0)
    max_accel   = st.slider("Max Accel.", 1.0, 15.0, 4.0)
    trans_speed = st.slider("Transition Speed", 0.2, 2.0, 1.0, 0.1)

    st.markdown("### 💨 Disturbances")
    wind_x      = st.slider("Wind X", -5.0, 5.0, 0.0, 0.5)
    wind_y      = st.slider("Wind Y", -5.0, 5.0, 0.0, 0.5)
    noise_level = st.slider("Motion Noise", 0.0, 3.0, 0.0, 0.1)

    st.markdown("### 🛡️ Collision")
    collision_r   = st.slider("Collision Radius", 1.0, 6.0, 2.5, 0.5)
    safety_margin = st.slider("Safety Margin",   0.5, 5.0, 1.5, 0.5)

    st.markdown("### 🎨 Visualisation")
    show_trails  = st.toggle("Show Trails",        True)
    show_links   = st.toggle("Show Comm. Links",   True)
    show_targets = st.toggle("Show Target Points", True)

# ── Pack config as JSON for JS ────────────────────────────────────────────────
cfg = json.dumps({
    "nDrones":      n_drones,
    "controlMode":  control_mode,
    "formation":    formation,
    "formCx":       form_cx,
    "formCy":       form_cy,
    "formScale":    form_scale,
    "formRotation": form_rotation,
    "commRadius":   comm_radius,
    "senseRadius":  sense_radius,
    "maxSpeed":     max_speed * trans_speed,
    "maxAccel":     max_accel,
    "windX":        wind_x,
    "windY":        wind_y,
    "noiseLevel":   noise_level,
    "collisionR":   collision_r,
    "safetyMargin": safety_margin,
    "showTrails":   show_trails,
    "showLinks":    show_links,
    "showTargets":  show_targets,
})

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:4px'>
  <span style='font-size:2rem'>🚁</span>
  <div>
    <h1 style='margin:0;font-size:1.7rem'>Drone Formation Control Lab</h1>
    <p style='margin:0;color:#6366f1;font-size:.9rem;font-weight:500'>
      Swarm Intelligence &middot; Decentralised Control &middot; Real-Time 60 fps Simulation
    </p>
  </div>
</div><hr style='margin:8px 0 16px 0'>
""", unsafe_allow_html=True)

# ── Embedded simulation (HTML5 Canvas + JS) ───────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#fff;font-family:'Segoe UI',system-ui,sans-serif;color:#1a1a2e;padding:4px}
  #wrap{display:flex;gap:10px;width:100%}
  #canvasWrap{flex:1;min-width:0;background:#fafbff;border:1px solid #e2e8f0;
    border-radius:12px;overflow:hidden;position:relative}
  canvas{display:block;width:100%!important}
  #right{width:210px;flex-shrink:0;display:flex;flex-direction:column;gap:6px}
  .card{background:#f0f4ff;border:1px solid #c7d2fe;border-radius:10px;padding:8px 12px}
  .card .lbl{font-size:.66rem;font-weight:600;color:#6366f1;margin-bottom:1px}
  .card .val{font-size:1.2rem;font-weight:700;color:#1a1a2e}
  #btns{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
  button{background:#4f46e5;color:#fff;border:none;border-radius:7px;
    padding:5px 12px;font-weight:600;font-size:.78rem;cursor:pointer;transition:background .15s}
  button:hover{background:#4338ca}
  .danger{background:#ef4444} .danger:hover{background:#dc2626}
  .warn{background:#f59e0b}   .warn:hover{background:#d97706}
  .green{background:#22c55e}  .green:hover{background:#16a34a}
  #chartCanvas{background:#f8f9ff;border:1px solid #e2e8f0;border-radius:10px}
  #log{font-size:.7rem;color:#475569;max-height:110px;overflow-y:auto;
    background:#f8f9ff;border:1px solid #e2e8f0;border-radius:10px;padding:6px}
  .loge{padding:1px 0;border-bottom:1px solid #f0f0f0}
  #overlay{position:absolute;top:7px;left:10px;background:rgba(255,255,255,.88);
    padding:3px 9px;border-radius:20px;border:1px solid #c7d2fe;
    font-size:.7rem;font-weight:600;color:#6366f1}
  #timeov{position:absolute;top:7px;right:10px;background:rgba(255,255,255,.88);
    padding:3px 9px;border-radius:20px;border:1px solid #e2e8f0;
    font-size:.7rem;font-weight:600;color:#475569}
  .sec-label{font-size:.72rem;font-weight:600;color:#4338ca;margin-top:2px}
</style>
</head>
<body>
<div id="btns">
  <button id="btnPlay">&#9654; Start</button>
  <button id="btnReset">&#8635; Reset</button>
  <button id="btnRandom">&#127922; Randomise</button>
  <button id="btnSwitch">&#128260; Switch Formation</button>
  <button class="danger" id="btnFail">&#9888; Fail Drone</button>
  <button class="warn"   id="btnObs">&#128679; Add Obstacle</button>
  <button class="warn"   id="btnGust">&#128168; Wind Gust</button>
  <button class="green"  id="btnClearWind">Clear Wind</button>
</div>
<div id="wrap">
  <div id="canvasWrap">
    <canvas id="c" width="880" height="620"></canvas>
    <div id="overlay">—</div>
    <div id="timeov">t = 0.0 s</div>
  </div>
  <div id="right">
    <div class="card"><div class="lbl">Formation Error</div><div class="val" id="mFE">—</div></div>
    <div class="card"><div class="lbl">Spacing Error</div><div class="val" id="mSE">—</div></div>
    <div class="card"><div class="lbl">Alignment Error</div><div class="val" id="mAE">—</div></div>
    <div class="card"><div class="lbl">Coverage Area</div><div class="val" id="mCA">—</div></div>
    <div class="card"><div class="lbl">Connectivity</div><div class="val" id="mCN">—</div></div>
    <div class="card"><div class="lbl">Cohesion Score</div><div class="val" id="mCO">—</div></div>
    <div class="card"><div class="lbl">Collisions</div><div class="val" id="mCL">—</div></div>
    <div class="sec-label">&#128200; Formation Error History</div>
    <canvas id="chartCanvas" width="210" height="100"></canvas>
    <div class="sec-label">&#128203; Event Log</div>
    <div id="log"></div>
  </div>
</div>

<script>
// ── Config injected from Python ───────────────────────────────────────
const CFG = PYTHON_CFG_PLACEHOLDER;

// ── Constants ─────────────────────────────────────────────────────────
const MAP = 100, DT = 0.05, TRAIL = 45;

// ── Seeded RNG ────────────────────────────────────────────────────────
let _s = 12345;
const rand = () => { _s ^= _s<<13; _s ^= _s>>17; _s ^= _s<<5; return (_s>>>0)/4294967296; };
const rr   = (a,b) => a+(b-a)*rand();
const rn   = () => { let u,v; do u=rand(); while(!u); do v=rand(); while(!v); return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); };

// ── Formation geometry ────────────────────────────────────────────────
function genFormation(n) {
  const pts=[], sp=8*CFG.formScale, f=CFG.formation;
  if(f==="Line")    { for(let i=0;i<n;i++) pts.push([(i-(n-1)/2)*sp,0]); }
  else if(f==="Column") { for(let i=0;i<n;i++) pts.push([0,(i-(n-1)/2)*sp]); }
  else if(f==="V-Shape") {
    pts.push([0,0]);
    for(let i=1;i<n;i++){const s=i%2===0?1:-1,r=Math.ceil(i/2);pts.push([s*r*sp*.8,-r*sp*.6]);}
  }
  else if(f==="Circle") {
    const r=sp*n/(2*Math.PI);
    for(let i=0;i<n;i++){const a=2*Math.PI*i/n;pts.push([r*Math.cos(a),r*Math.sin(a)]);}
  }
  else if(f==="Square") {
    const s=Math.max(2,Math.ceil(Math.sqrt(n)));
    for(let i=0;i<n;i++){const row=Math.floor(i/s),col=i%s;pts.push([(col-(s-1)/2)*sp,(row-(s-1)/2)*sp]);}
  }
  else if(f==="Wedge") {
    pts.push([0,0]); let row=1,co=1,idx=1;
    while(idx<n){pts.push([-co*sp*.7,-row*sp*.7]);idx++;if(idx<n){pts.push([co*sp*.7,-row*sp*.7]);idx++;}row++;co++;}
  }
  else if(f==="Grid") {
    const cols=Math.max(2,Math.ceil(Math.sqrt(n)));
    for(let i=0;i<n;i++){const r=Math.floor(i/cols),c=i%cols;pts.push([(c-(cols-1)/2)*sp,(r-(Math.ceil(n/cols)-1)/2)*sp]);}
  }
  else if(f==="Ring") {
    const ir=sp*Math.max(3,Math.floor(n/4))/(2*Math.PI),or=ir*1.8,split=Math.floor(n/2);
    for(let i=0;i<split;i++){const a=2*Math.PI*i/split;pts.push([ir*Math.cos(a),ir*Math.sin(a)]);}
    for(let i=0;i<n-split;i++){const a=2*Math.PI*i/(n-split);pts.push([or*Math.cos(a),or*Math.sin(a)]);}
  }
  else if(f==="Spiral") {
    for(let i=0;i<n;i++){const t=i/Math.max(n-1,1)*4*Math.PI,r=sp*.5*t/(2*Math.PI)+sp;pts.push([r*Math.cos(t),r*Math.sin(t)]);}
  }
  else if(f==="Expanding Wave") {
    const w=n*sp;
    for(let i=0;i<n;i++){const x=(i/Math.max(n-1,1)-.5)*w,y=sp*1.5*Math.sin(2*Math.PI*i/Math.max(n-1,1));pts.push([x,y]);}
  }
  const cr=Math.cos(CFG.formRotation*Math.PI/180), sr=Math.sin(CFG.formRotation*Math.PI/180);
  return pts.map(([px,py])=>[px*cr-py*sr+CFG.formCx, px*sr+py*cr+CFG.formCy]);
}

function assign(drones, targets) {
  const res=new Array(drones.length).fill(-1), used=new Array(targets.length).fill(false);
  for(let di=0;di<drones.length;di++){
    let best=Infinity,bi=-1;
    for(let ti=0;ti<targets.length;ti++){
      if(used[ti]) continue;
      const d=Math.hypot(drones[di].x-targets[ti][0],drones[di].y-targets[ti][1]);
      if(d<best){best=d;bi=ti;}
    }
    if(bi>=0){res[di]=bi;used[bi]=true;}
  }
  return res;
}

// ── State ─────────────────────────────────────────────────────────────
let drones=[], obstacles=[], simTime=0, collisions=0, events=[], errHist=[];

function mkDrone(id){ return {id,x:rr(-45,45),y:rr(-45,45),vx:rr(-1,1),vy:rr(-1,1),heading:0,tx:0,ty:0,isLeader:id===0,failed:false,battery:rr(75,100),trail:[]}; }

function resetSim(seed){ if(seed!==undefined)_s=seed; drones=[];obstacles=[];simTime=0;collisions=0;events=[];errHist=[]; for(let i=0;i<CFG.nDrones;i++)drones.push(mkDrone(i)); assignTargets(); logEv("Simulation reset"); }

function assignTargets(){ const tgts=genFormation(drones.length),asgn=assign(drones,tgts); drones.forEach((d,i)=>{const ti=asgn[i]>=0?asgn[i]:i%tgts.length;d.tx=tgts[ti][0];d.ty=tgts[ti][1];}); }

// ── Control laws ──────────────────────────────────────────────────────
function goto(d,tx,ty){ const dx=tx-d.x,dy=ty-d.y,dist=Math.hypot(dx,dy)+1e-6,k=Math.min(2,dist/10)*CFG.maxAccel; return [k*dx/dist-d.vx, k*dy/dist-d.vy]; }

function ctrl(d){
  const active=drones.filter(x=>!x.failed);
  const nb=active.filter(n=>n.id!==d.id&&Math.hypot(d.x-n.x,d.y-n.y)<CFG.commRadius);
  const sns=active.filter(n=>n.id!==d.id&&Math.hypot(d.x-n.x,d.y-n.y)<CFG.senseRadius);
  const m=CFG.controlMode;

  if(m==="Leader-Follower"){
    const ldr=active.find(x=>x.isLeader);
    if(d.isLeader||!ldr) return goto(d,d.tx,d.ty);
    return goto(d,ldr.x+(d.tx-ldr.tx),ldr.y+(d.ty-ldr.ty));
  }
  if(m==="Consensus-Based"){
    let fx=1.5*(d.tx-d.x)-.8*d.vx, fy=1.5*(d.ty-d.y)-.8*d.vy;
    if(nb.length){fx+=.3*(nb.reduce((s,n)=>s+n.x,0)/nb.length-d.x);fy+=.3*(nb.reduce((s,n)=>s+n.y,0)/nb.length-d.y);}
    return [fx,fy];
  }
  if(m==="Behavior-Based"){
    const dg=Math.hypot(d.tx-d.x,d.ty-d.y)+1e-6;
    let fx=2*(d.tx-d.x)/dg, fy=2*(d.ty-d.y)/dg;
    if(sns.length){
      let sx=0,sy=0,cx=0,cy=0,avx=0,avy=0;
      sns.forEach(n=>{const dn=Math.hypot(d.x-n.x,d.y-n.y)+1e-6;if(dn<CFG.senseRadius*.5){sx+=(d.x-n.x)/dn;sy+=(d.y-n.y)/dn;}cx+=n.x;cy+=n.y;avx+=n.vx;avy+=n.vy;});
      const nb2=sns.length;
      fx+=1.5*sx/nb2+.3*(cx/nb2-d.x)+.4*(avx/nb2-d.vx);
      fy+=1.5*sy/nb2+.3*(cy/nb2-d.y)+.4*(avy/nb2-d.vy);
    }
    return [fx,fy];
  }
  if(m==="Virtual Structure") return [2*(d.tx-d.x)-d.vx, 2*(d.ty-d.y)-d.vy];
  // Potential Field
  const dd=Math.hypot(d.tx-d.x,d.ty-d.y)+1e-6;
  let fx=2.5*(d.tx-d.x)/(dd+1), fy=2.5*(d.ty-d.y)/(dd+1);
  sns.forEach(n=>{const dn=Math.hypot(d.x-n.x,d.y-n.y)+.1;if(dn<CFG.senseRadius){const s=3/(dn*dn);fx+=s*(d.x-n.x)/dn;fy+=s*(d.y-n.y)/dn;}});
  return [fx,fy];
}

// ── Physics step ──────────────────────────────────────────────────────
function step(){
  const active=drones.filter(d=>!d.failed);
  const forces=new Map();
  active.forEach(d=>{
    let [fx,fy]=ctrl(d);
    fx+=CFG.windX+CFG.noiseLevel*rn();
    fy+=CFG.windY+CFG.noiseLevel*rn();
    // Drone repulsion
    active.forEach(o=>{
      if(o.id===d.id)return;
      const dn=Math.hypot(d.x-o.x,d.y-o.y)+1e-6,rep=CFG.collisionR+CFG.safetyMargin;
      if(dn<rep){const f=(rep-dn)/rep*CFG.maxAccel*2;fx+=(d.x-o.x)/dn*f;fy+=(d.y-o.y)/dn*f;}
    });
    // Obstacle repulsion
    obstacles.forEach(ob=>{
      const dn=Math.hypot(d.x-ob.x,d.y-ob.y)+1e-6,rep=ob.r+CFG.collisionR+CFG.safetyMargin*2;
      if(dn<rep){const f=(rep-dn)/rep*CFG.maxAccel*3;fx+=(d.x-ob.x)/dn*f;fy+=(d.y-ob.y)/dn*f;}
    });
    // Boundary
    const B=MAP-5;
    if(d.x> B)fx-=CFG.maxAccel*(d.x-B)/5; if(d.x<-B)fx+=CFG.maxAccel*(-B-d.x)/5;
    if(d.y> B)fy-=CFG.maxAccel*(d.y-B)/5; if(d.y<-B)fy+=CFG.maxAccel*(-B-d.y)/5;
    forces.set(d.id,[fx,fy]);
  });
  active.forEach(d=>{
    let [fx,fy]=forces.get(d.id)||[0,0];
    const am=Math.hypot(fx,fy);
    if(am>CFG.maxAccel){fx=fx/am*CFG.maxAccel;fy=fy/am*CFG.maxAccel;}
    d.vx+=fx*DT; d.vy+=fy*DT;
    const spd=Math.hypot(d.vx,d.vy);
    if(spd>CFG.maxSpeed){d.vx=d.vx/spd*CFG.maxSpeed;d.vy=d.vy/spd*CFG.maxSpeed;}
    d.trail.push([d.x,d.y]);
    if(d.trail.length>TRAIL)d.trail.shift();
    d.x+=d.vx*DT; d.y+=d.vy*DT;
    if(Math.hypot(d.vx,d.vy)>.1)d.heading=Math.atan2(d.vy,d.vx);
    d.battery=Math.max(0,d.battery-.005);
  });
  for(let i=0;i<active.length;i++)
    for(let j=i+1;j<active.length;j++)
      if(Math.hypot(active[i].x-active[j].x,active[i].y-active[j].y)<CFG.collisionR)collisions++;
  simTime+=DT;
  errHist.push(fmtErr());
  if(errHist.length>200)errHist.shift();
}

// ── Metrics ───────────────────────────────────────────────────────────
const act=()=>drones.filter(d=>!d.failed);
function fmtErr(){const a=act();return a.length?a.reduce((s,d)=>s+Math.hypot(d.x-d.tx,d.y-d.ty),0)/a.length:0;}
function spErr(){const a=act();if(a.length<2)return 0;const ideal=8*CFG.formScale;let s=0,c=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){s+=Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y);c++;}return Math.abs(s/c-ideal);}
function alnErr(){const a=act();if(a.length<2)return 0;const mh=a.reduce((s,d)=>s+d.heading,0)/a.length;return Math.sqrt(a.reduce((s,d)=>s+(d.heading-mh)**2,0)/a.length);}
function covArea(){const a=act();if(a.length<3)return 0;const xs=a.map(d=>d.x),ys=a.map(d=>d.y);return(Math.max(...xs)-Math.min(...xs))*(Math.max(...ys)-Math.min(...ys));}
function conn(){const a=act();if(a.length<2)return 1;let e=0,me=a.length*(a.length-1)/2;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y)<CFG.commRadius)e++;return e/me;}
function cohesion(){const a=act();if(!a.length)return 0;const cx=a.reduce((s,d)=>s+d.x,0)/a.length,cy=a.reduce((s,d)=>s+d.y,0)/a.length;return Math.max(0,100-a.reduce((s,d)=>s+Math.hypot(d.x-cx,d.y-cy),0)/a.length);}

// ── Rendering ─────────────────────────────────────────────────────────
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
const W=canvas.width, H=canvas.height;
const w2s=(wx,wy)=>[(wx+MAP)/(2*MAP)*W,(MAP-wy)/(2*MAP)*H];
const sc=()=>W/(2*MAP);

function drawArrow(sx,sy,heading,sz,fill){
  ctx.save();
  ctx.translate(sx,sy);
  ctx.rotate(heading+Math.PI/2);
  ctx.beginPath();
  ctx.moveTo(0,-sz);
  ctx.lineTo(sz*.55,sz*.65);
  ctx.lineTo(0,sz*.2);
  ctx.lineTo(-sz*.55,sz*.65);
  ctx.closePath();
  ctx.fillStyle=fill;
  ctx.fill();
  ctx.strokeStyle='rgba(255,255,255,.9)';
  ctx.lineWidth=1.5;
  ctx.stroke();
  ctx.restore();
}

function render(){
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#fafbff'; ctx.fillRect(0,0,W,H);

  // Grid lines
  ctx.strokeStyle='#e8ecf7'; ctx.lineWidth=1;
  for(let gx=-MAP;gx<=MAP;gx+=10){
    const [sx,sy0]=w2s(gx,MAP),[,sy1]=w2s(gx,-MAP);
    ctx.beginPath();ctx.moveTo(sx,sy0);ctx.lineTo(sx,sy1);ctx.stroke();
  }
  for(let gy=-MAP;gy<=MAP;gy+=10){
    const [sx0,sy]=w2s(-MAP,gy),[sx1]=w2s(MAP,gy);
    ctx.beginPath();ctx.moveTo(sx0,sy);ctx.lineTo(sx1,sy);ctx.stroke();
  }
  // Axes
  ctx.strokeStyle='#d1d5e8'; ctx.lineWidth=1.5;
  {const [sx,sy0]=w2s(0,MAP),[,sy1]=w2s(0,-MAP);ctx.beginPath();ctx.moveTo(sx,sy0);ctx.lineTo(sx,sy1);ctx.stroke();}
  {const [sx0,sy]=w2s(-MAP,0),[sx1]=w2s(MAP,0);ctx.beginPath();ctx.moveTo(sx0,sy);ctx.lineTo(sx1,sy);ctx.stroke();}

  const S=sc();

  // Obstacles
  obstacles.forEach(ob=>{
    const [ox,oy]=w2s(ob.x,ob.y),r=ob.r*S;
    ctx.beginPath();ctx.arc(ox,oy,r,0,2*Math.PI);
    ctx.fillStyle='rgba(239,68,68,.13)';ctx.fill();
    ctx.strokeStyle='#ef4444';ctx.lineWidth=2;ctx.stroke();
  });

  // Comm links
  if(CFG.showLinks){
    const a=act();
    ctx.strokeStyle='rgba(99,102,241,.14)';ctx.lineWidth=1;
    for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){
      if(Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y)<CFG.commRadius){
        const [ax,ay]=w2s(a[i].x,a[i].y),[bx,by]=w2s(a[j].x,a[j].y);
        ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke();
      }
    }
  }

  // Target crosses
  if(CFG.showTargets){
    drones.filter(d=>!d.failed).forEach(d=>{
      const [tx,ty]=w2s(d.tx,d.ty),s=5;
      ctx.strokeStyle='rgba(99,102,241,.38)';ctx.lineWidth=1.5;
      ctx.beginPath();ctx.moveTo(tx-s,ty-s);ctx.lineTo(tx+s,ty+s);
      ctx.moveTo(tx+s,ty-s);ctx.lineTo(tx-s,ty+s);ctx.stroke();
    });
  }

  // Trails
  if(CFG.showTrails){
    drones.filter(d=>!d.failed&&d.trail.length>1).forEach(d=>{
      for(let i=1;i<d.trail.length;i++){
        const alpha=(0.04+.28*(i/d.trail.length)).toFixed(2);
        ctx.strokeStyle=`rgba(99,102,241,${alpha})`;
        ctx.lineWidth=1.2;
        const [ax,ay]=w2s(d.trail[i-1][0],d.trail[i-1][1]);
        const [bx,by]=w2s(d.trail[i][0],d.trail[i][1]);
        ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke();
      }
    });
  }

  // Drones
  drones.forEach(d=>{
    const [sx,sy]=w2s(d.x,d.y);
    if(d.failed){
      ctx.save();ctx.globalAlpha=.35;
      ctx.beginPath();ctx.arc(sx,sy,8,0,2*Math.PI);
      ctx.fillStyle='#9ca3af';ctx.fill();
      ctx.restore();
      ctx.fillStyle='#6b7280';ctx.font='bold 9px sans-serif';
      ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('✕',sx,sy);
      return;
    }
    const err=Math.hypot(d.x-d.tx,d.y-d.ty),t=Math.min(err/20,1);
    const r=Math.round(99+t*(244-99)),g=Math.round(102+t*(63-102)),b=Math.round(241+t*(63-241));
    const fill=d.isLeader?'#f59e0b':`rgb(${r},${g},${b})`;
    const sz=d.isLeader?11:8;
    drawArrow(sx,sy,d.heading,sz,fill);
    // ID
    ctx.fillStyle='#64748b';ctx.font='8px sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillText(d.id,sx+sz+3,sy);
    // Battery bar
    const bw=13,bh=2.5;
    ctx.fillStyle='#e2e8f0';ctx.fillRect(sx-bw/2,sy+sz+3,bw,bh);
    ctx.fillStyle=d.battery>50?'#22c55e':d.battery>25?'#f59e0b':'#ef4444';
    ctx.fillRect(sx-bw/2,sy+sz+3,bw*d.battery/100,bh);
  });

  // Leader halo
  const ldr=drones.find(d=>d.isLeader&&!d.failed);
  if(ldr){
    const [lx,ly]=w2s(ldr.x,ldr.y);
    ctx.beginPath();ctx.arc(lx,ly,17,0,2*Math.PI);
    ctx.strokeStyle='rgba(245,158,11,.4)';ctx.lineWidth=2.5;ctx.stroke();
  }
}

function drawChart(){
  const cc=document.getElementById('chartCanvas'),cx2=cc.getContext('2d'),cw=cc.width,ch=cc.height;
  cx2.clearRect(0,0,cw,ch);
  if(errHist.length<2)return;
  const mx=Math.max(...errHist,1);
  cx2.strokeStyle='rgba(99,102,241,.12)';cx2.lineWidth=1;
  for(let i=0;i<=4;i++){const y=ch-ch*(i/4)*.85-8;cx2.beginPath();cx2.moveTo(0,y);cx2.lineTo(cw,y);cx2.stroke();}
  cx2.beginPath();
  errHist.forEach((v,i)=>{const x=cw*i/errHist.length,y=ch-(v/mx)*(ch-14)-6;i===0?cx2.moveTo(x,y):cx2.lineTo(x,y);});
  cx2.strokeStyle='#6366f1';cx2.lineWidth=2;cx2.stroke();
  cx2.lineTo(cw,ch);cx2.lineTo(0,ch);cx2.closePath();
  cx2.fillStyle='rgba(99,102,241,.08)';cx2.fill();
  cx2.fillStyle='#312e81';cx2.font='bold 9px sans-serif';cx2.textAlign='right';
  cx2.fillText(errHist[errHist.length-1].toFixed(1),cw-2,11);
}

function updateUI(){
  document.getElementById('mFE').textContent=fmtErr().toFixed(2)+' u';
  document.getElementById('mSE').textContent=spErr().toFixed(2)+' u';
  document.getElementById('mAE').textContent=alnErr().toFixed(3)+' rad';
  document.getElementById('mCA').textContent=Math.round(covArea())+' u²';
  document.getElementById('mCN').textContent=Math.round(conn()*100)+'%';
  document.getElementById('mCO').textContent=cohesion().toFixed(1);
  document.getElementById('mCL').textContent=collisions;
  document.getElementById('overlay').textContent=CFG.controlMode+' · '+CFG.formation;
  document.getElementById('timeov').textContent='t = '+simTime.toFixed(1)+' s';
  drawChart();
}

function logEv(msg){
  events.unshift(msg);if(events.length>20)events.pop();
  document.getElementById('log').innerHTML=events.map(e=>`<div class="loge">${e}</div>`).join('');
}

// ── Main animation loop ───────────────────────────────────────────────
let running=false, lastT=0, acc=0;
const STEP_MS=DT*1000;

function loop(now){
  requestAnimationFrame(loop);
  const dt=Math.min(now-lastT,80);
  lastT=now;
  if(running){
    acc+=dt;
    let stepped=false;
    while(acc>=STEP_MS){step();acc-=STEP_MS;stepped=true;}
    if(stepped)updateUI();
  }
  render();
}

// ── Buttons ───────────────────────────────────────────────────────────
document.getElementById('btnPlay').onclick=function(){
  running=!running;this.textContent=running?'⏸ Pause':'▶ Start';
};
document.getElementById('btnReset').onclick=()=>{
  running=false;document.getElementById('btnPlay').textContent='▶ Start';resetSim(12345);render();updateUI();
};
document.getElementById('btnRandom').onclick=()=>{resetSim(Math.floor(Math.random()*999999));};
document.getElementById('btnSwitch').onclick=()=>{assignTargets();logEv('Formation → '+CFG.formation);};
document.getElementById('btnFail').onclick=()=>{
  const c=drones.filter(d=>!d.failed&&!d.isLeader);
  if(c.length){const v=c[Math.floor(rand()*c.length)];v.failed=true;logEv('Drone #'+v.id+' failed');}
};
document.getElementById('btnObs').onclick=()=>{
  const ob={x:rr(-55,55),y:rr(-55,55),r:rr(4,9)};obstacles.push(ob);
  logEv('Obstacle at ('+ob.x.toFixed(0)+','+ob.y.toFixed(0)+')');
};
document.getElementById('btnGust').onclick=()=>{
  CFG.windX=rr(-4,4);CFG.windY=rr(-4,4);
  logEv('Wind gust ('+CFG.windX.toFixed(1)+','+CFG.windY.toFixed(1)+')');
};
document.getElementById('btnClearWind').onclick=()=>{CFG.windX=0;CFG.windY=0;logEv('Wind cleared');};

// ── Init ──────────────────────────────────────────────────────────────
resetSim(12345);
requestAnimationFrame(loop);
</script>
</body>
</html>
"""

# Inject config — use a unique placeholder that won't conflict with JS syntax
HTML_FINAL = HTML_TEMPLATE.replace("PYTHON_CFG_PLACEHOLDER", cfg)

components.html(HTML_FINAL, height=830, scrolling=False)

# ── Info tabs ─────────────────────────────────────────────────────────────────
st.markdown("<hr style='margin:16px 0'>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🎯 Preset Scenarios", "ℹ️ Usage Tips", "📖 About"])

with tab1:
    st.markdown("**Configure these via the sidebar, then click Switch Formation or Reset:**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**🏙️ Urban Navigation**")
        st.caption("Wedge · Potential Field · 8 drones · add obstacles with the button")
    with c2:
        st.markdown("**🌾 Agricultural Scan**")
        st.caption("Grid · Virtual Structure · 16 drones · scale 1.5×")
    with c3:
        st.markdown("**🔍 Search & Rescue**")
        st.caption("Expanding Wave · Behavior-Based · 20 drones · comm radius 45")
    with c4:
        st.markdown("**💥 Failure Recovery**")
        st.caption("Circle · Consensus · 14 drones · hit ⚠️ Fail Drone several times")

with tab2:
    st.info(
        "**Sidebar sliders update the simulation in real time** — no restart needed for most params. "
        "After changing **Formation** or **Number of Drones**, click **🔄 Switch Formation** "
        "inside the canvas to apply the new geometry. Use **↺ Reset** to start fresh."
    )
    st.markdown("""
- **Color coding:** drones shift from **indigo** (on-target) → **red** (high error)
- **Gold drone** = leader (Leader-Follower mode)
- **Battery bars** appear below each drone — drain over time
- **× marker** = failed drone
- Dashed crosses = formation target slots
    """)

with tab3:
    st.markdown("""
### About

**Drone Formation Control Lab** — smooth 60 fps swarm simulation.

The entire physics engine, control laws, and canvas renderer run **client-side in JavaScript**
via `st.components.v1.html`, so there are zero Streamlit page reruns during simulation.
The Python layer only provides the sidebar UI and injects the config JSON on each sidebar change.

#### Control Strategies
| Mode | Principle |
|---|---|
| **Leader-Follower** | Hierarchical offsets from leader. Fast but fragile. |
| **Consensus-Based** | Iterative neighbour averaging. Robust to failures. |
| **Behavior-Based** | Separation + cohesion + alignment + goal. Emergent. |
| **Virtual Structure** | Rigid-body slot tracking via PD control. High fidelity. |
| **Potential Field** | Attractive/repulsive force fields. Smooth and physical. |

#### Stack
`Streamlit` sidebar + `st.components.v1.html` + `HTML5 Canvas` + `requestAnimationFrame`
    """)