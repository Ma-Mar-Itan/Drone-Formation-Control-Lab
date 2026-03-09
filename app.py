"""
Drone Formation Control Lab
============================
Streamlit is used ONLY to serve the page.
ALL controls, simulation, and rendering live inside a single
st.components.v1.html call — Streamlit never reruns during use,
so there is zero flicker/stutter.
"""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Drone Formation Control Lab",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimal host-page style (never rerenders)
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],
.main,.block-container{background:#fff!important;padding:0!important;margin:0!important}
[data-testid="stSidebar"]{display:none}
header,[data-testid="stHeader"]{display:none}
.block-container{padding:0!important;max-width:100%!important}
iframe{border:none!important;display:block}
</style>
""", unsafe_allow_html=True)

# ── The entire application lives here ──────────────────────────────────────
components.html("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Drone Formation Control Lab</title>
<style>
/* ── Reset & base ── */
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f4ff;color:#1a1a2e;height:100vh;overflow:hidden;display:flex;flex-direction:column}

/* ── Top bar ── */
#topbar{background:#fff;border-bottom:1px solid #e2e8f0;padding:0 16px;height:48px;display:flex;align-items:center;gap:16px;flex-shrink:0;box-shadow:0 1px 4px rgba(99,102,241,.08)}
#topbar h1{font-size:1.05rem;font-weight:800;color:#1a1a2e;white-space:nowrap}
#topbar .sub{font-size:.72rem;color:#6366f1;font-weight:600;white-space:nowrap}
#topbar .spacer{flex:1}
.tbtn{background:#4f46e5;color:#fff;border:none;border-radius:7px;padding:5px 11px;font-weight:600;font-size:.75rem;cursor:pointer;white-space:nowrap;transition:background .15s}
.tbtn:hover{background:#4338ca}
.tbtn.danger{background:#ef4444}.tbtn.danger:hover{background:#dc2626}
.tbtn.warn{background:#f59e0b}.tbtn.warn:hover{background:#d97706}
.tbtn.green{background:#22c55e}.tbtn.green:hover{background:#16a34a}
.tbtn.ghost{background:#e0e7ff;color:#3730a3}.tbtn.ghost:hover{background:#c7d2fe}

/* ── Main layout ── */
#main{display:flex;flex:1;overflow:hidden;gap:0}

/* ── Left panel ── */
#left{width:230px;flex-shrink:0;background:#fff;border-right:1px solid #e2e8f0;overflow-y:auto;padding:10px 12px;display:flex;flex-direction:column;gap:4px}
#left::-webkit-scrollbar{width:4px}#left::-webkit-scrollbar-thumb{background:#c7d2fe;border-radius:2px}
.panel-section{font-size:.68rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:.06em;margin:8px 0 4px}
.ctrl-row{display:flex;flex-direction:column;margin-bottom:6px}
.ctrl-row label{font-size:.7rem;font-weight:600;color:#374151;margin-bottom:2px;display:flex;justify-content:space-between}
.ctrl-row label span{color:#6366f1;font-weight:700}
input[type=range]{width:100%;height:4px;accent-color:#6366f1;cursor:pointer}
select{width:100%;padding:4px 6px;border:1px solid #c7d2fe;border-radius:6px;font-size:.75rem;color:#1a1a2e;background:#fff;cursor:pointer}
.toggle-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.toggle-row span{font-size:.72rem;font-weight:600;color:#374151}
.toggle{position:relative;width:32px;height:18px}
.toggle input{opacity:0;width:0;height:0}
.slider-tog{position:absolute;inset:0;background:#c7d2fe;border-radius:9px;cursor:pointer;transition:.2s}
.slider-tog:before{content:'';position:absolute;width:12px;height:12px;left:3px;top:3px;background:#fff;border-radius:50%;transition:.2s}
input:checked+.slider-tog{background:#6366f1}
input:checked+.slider-tog:before{transform:translateX(14px)}
.mode-desc{font-size:.67rem;color:#6b7280;background:#f0f4ff;border-radius:6px;padding:5px 7px;line-height:1.45;margin-bottom:4px}

/* ── Canvas area ── */
#canvasWrap{flex:1;position:relative;background:#fafbff;overflow:hidden}
canvas#sim{display:block;width:100%;height:100%}
#overlay{position:absolute;top:8px;left:10px;background:rgba(255,255,255,.92);padding:3px 10px;border-radius:20px;border:1px solid #c7d2fe;font-size:.7rem;font-weight:700;color:#4338ca;pointer-events:none}
#timeov{position:absolute;top:8px;right:10px;background:rgba(255,255,255,.92);padding:3px 10px;border-radius:20px;border:1px solid #e2e8f0;font-size:.7rem;font-weight:600;color:#475569;pointer-events:none}
#pauseBanner{display:none;position:absolute;inset:0;background:rgba(240,244,255,.55);align-items:center;justify-content:center;font-size:1.4rem;font-weight:800;color:#4338ca;pointer-events:none}

/* ── Right panel ── */
#right{width:200px;flex-shrink:0;background:#fff;border-left:1px solid #e2e8f0;overflow-y:auto;padding:10px 10px;display:flex;flex-direction:column;gap:5px}
#right::-webkit-scrollbar{width:4px}#right::-webkit-scrollbar-thumb{background:#c7d2fe;border-radius:2px}
.metric{background:#f0f4ff;border:1px solid #c7d2fe;border-radius:9px;padding:7px 10px}
.metric .mlbl{font-size:.63rem;font-weight:700;color:#6366f1;margin-bottom:1px}
.metric .mval{font-size:1.1rem;font-weight:800;color:#1a1a2e}
#chartCanvas{border:1px solid #e2e8f0;border-radius:8px;background:#f8f9ff;margin-top:2px}
.rpanel-lbl{font-size:.68rem;font-weight:700;color:#4338ca;text-transform:uppercase;letter-spacing:.05em;margin-top:4px}
#log{font-size:.67rem;color:#475569;max-height:130px;overflow-y:auto;background:#f8f9ff;border:1px solid #e2e8f0;border-radius:8px;padding:5px 7px}
#log::-webkit-scrollbar{width:3px}#log::-webkit-scrollbar-thumb{background:#c7d2fe}
.loge{padding:1px 0;border-bottom:1px solid #f0f0f0}
</style>
</head>
<body>

<!-- TOP BAR -->
<div id="topbar">
  <span style="font-size:1.4rem">🚁</span>
  <div>
    <div id="topbar"><h1 style="display:inline">Drone Formation Control Lab</h1>
    &nbsp;<span class="sub">Swarm Intelligence · Decentralised Control · 60 fps</span></div>
  </div>
  <div class="spacer"></div>
  <button class="tbtn" id="btnPlay">▶ Start</button>
  <button class="tbtn ghost" id="btnReset">↺ Reset</button>
  <button class="tbtn ghost" id="btnRandom">🎲 Randomise</button>
  <button class="tbtn ghost" id="btnSwitch">🔄 Formation</button>
  <button class="tbtn danger" id="btnFail">⚠ Fail</button>
  <button class="tbtn warn" id="btnObs">🚧 Obstacle</button>
  <button class="tbtn warn" id="btnGust">💨 Gust</button>
  <button class="tbtn green" id="btnClearWind">✕ Wind</button>
</div>

<!-- MAIN -->
<div id="main">

  <!-- LEFT CONTROLS -->
  <div id="left">
    <div class="panel-section">Swarm</div>
    <div class="ctrl-row">
      <label>Drones <span id="vDrones">12</span></label>
      <input type="range" id="nDrones" min="4" max="40" value="12">
    </div>

    <div class="panel-section">Control Mode</div>
    <select id="controlMode">
      <option value="Virtual Structure" selected>Virtual Structure</option>
      <option value="Leader-Follower">Leader-Follower</option>
      <option value="Consensus-Based">Consensus-Based</option>
      <option value="Behavior-Based">Behavior-Based</option>
      <option value="Potential Field">Potential Field</option>
    </select>
    <div class="mode-desc" id="modeDesc">Formation treated as a rigid virtual body; each drone tracks its slot via PD control. High fidelity.</div>

    <div class="panel-section">Formation</div>
    <select id="formation">
      <option value="Circle" selected>Circle</option>
      <option value="Line">Line</option>
      <option value="Column">Column</option>
      <option value="V-Shape">V-Shape</option>
      <option value="Square">Square</option>
      <option value="Wedge">Wedge</option>
      <option value="Grid">Grid</option>
      <option value="Ring">Ring</option>
      <option value="Spiral">Spiral</option>
      <option value="Expanding Wave">Expanding Wave</option>
    </select>

    <div class="panel-section">Formation Transform</div>
    <div class="ctrl-row"><label>Center X <span id="vCx">0</span></label><input type="range" id="formCx" min="-60" max="60" value="0"></div>
    <div class="ctrl-row"><label>Center Y <span id="vCy">0</span></label><input type="range" id="formCy" min="-60" max="60" value="0"></div>
    <div class="ctrl-row"><label>Scale <span id="vScale">1.0</span></label><input type="range" id="formScale" min="0.3" max="3.0" step="0.1" value="1.0"></div>
    <div class="ctrl-row"><label>Rotation° <span id="vRot">0</span></label><input type="range" id="formRot" min="0" max="360" value="0"></div>

    <div class="panel-section">Communication</div>
    <div class="ctrl-row"><label>Comm Radius <span id="vComm">35</span></label><input type="range" id="commRadius" min="10" max="80" value="35"></div>
    <div class="ctrl-row"><label>Sense Radius <span id="vSense">20</span></label><input type="range" id="senseRadius" min="5" max="50" value="20"></div>

    <div class="panel-section">Dynamics</div>
    <div class="ctrl-row"><label>Max Speed <span id="vSpeed">8.0</span></label><input type="range" id="maxSpeed" min="1" max="25" step="0.5" value="8"></div>
    <div class="ctrl-row"><label>Max Accel <span id="vAccel">4.0</span></label><input type="range" id="maxAccel" min="1" max="15" step="0.5" value="4"></div>
    <div class="ctrl-row"><label>Trans Speed <span id="vTrans">1.0</span></label><input type="range" id="transSpeed" min="0.2" max="2.0" step="0.1" value="1.0"></div>

    <div class="panel-section">Disturbances</div>
    <div class="ctrl-row"><label>Wind X <span id="vWx">0.0</span></label><input type="range" id="windX" min="-5" max="5" step="0.5" value="0"></div>
    <div class="ctrl-row"><label>Wind Y <span id="vWy">0.0</span></label><input type="range" id="windY" min="-5" max="5" step="0.5" value="0"></div>
    <div class="ctrl-row"><label>Noise <span id="vNoise">0.0</span></label><input type="range" id="noiseLevel" min="0" max="3" step="0.1" value="0"></div>

    <div class="panel-section">Collision</div>
    <div class="ctrl-row"><label>Col. Radius <span id="vColR">2.5</span></label><input type="range" id="collisionR" min="1" max="6" step="0.5" value="2.5"></div>
    <div class="ctrl-row"><label>Safety Margin <span id="vSafe">1.5</span></label><input type="range" id="safetyMargin" min="0.5" max="5" step="0.5" value="1.5"></div>

    <div class="panel-section">Visualisation</div>
    <div class="toggle-row"><span>Trails</span><label class="toggle"><input type="checkbox" id="showTrails" checked><span class="slider-tog"></span></label></div>
    <div class="toggle-row"><span>Comm Links</span><label class="toggle"><input type="checkbox" id="showLinks" checked><span class="slider-tog"></span></label></div>
    <div class="toggle-row"><span>Target Points</span><label class="toggle"><input type="checkbox" id="showTargets" checked><span class="slider-tog"></span></label></div>
  </div>

  <!-- CANVAS -->
  <div id="canvasWrap">
    <canvas id="sim"></canvas>
    <div id="overlay">Virtual Structure · Circle</div>
    <div id="timeov">t = 0.0 s</div>
    <div id="pauseBanner">⏸ PAUSED</div>
  </div>

  <!-- RIGHT METRICS -->
  <div id="right">
    <div class="rpanel-lbl">📊 Live Metrics</div>
    <div class="metric"><div class="mlbl">Formation Error</div><div class="mval" id="mFE">—</div></div>
    <div class="metric"><div class="mlbl">Spacing Error</div><div class="mval" id="mSE">—</div></div>
    <div class="metric"><div class="mlbl">Alignment Error</div><div class="mval" id="mAE">—</div></div>
    <div class="metric"><div class="mlbl">Coverage Area</div><div class="mval" id="mCA">—</div></div>
    <div class="metric"><div class="mlbl">Connectivity</div><div class="mval" id="mCN">—</div></div>
    <div class="metric"><div class="mlbl">Cohesion</div><div class="mval" id="mCO">—</div></div>
    <div class="metric"><div class="mlbl">Collisions</div><div class="mval" id="mCL">—</div></div>
    <div class="rpanel-lbl">📈 Error History</div>
    <canvas id="chartCanvas" width="180" height="90"></canvas>
    <div class="rpanel-lbl">📋 Event Log</div>
    <div id="log"></div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════
// LIVE CONFIG — reads directly from DOM controls, no Python needed
// ═══════════════════════════════════════════════════════════════
const C = {
  get nDrones()     { return +document.getElementById('nDrones').value },
  get controlMode() { return document.getElementById('controlMode').value },
  get formation()   { return document.getElementById('formation').value },
  get formCx()      { return +document.getElementById('formCx').value },
  get formCy()      { return +document.getElementById('formCy').value },
  get formScale()   { return +document.getElementById('formScale').value },
  get formRot()     { return +document.getElementById('formRot').value },
  get commRadius()  { return +document.getElementById('commRadius').value },
  get senseRadius() { return +document.getElementById('senseRadius').value },
  get maxSpeed()    { return +document.getElementById('maxSpeed').value * +document.getElementById('transSpeed').value },
  get maxAccel()    { return +document.getElementById('maxAccel').value },
  get windX()       { return +document.getElementById('windX').value },
  get windY()       { return +document.getElementById('windY').value },
  get noiseLevel()  { return +document.getElementById('noiseLevel').value },
  get collisionR()  { return +document.getElementById('collisionR').value },
  get safetyMargin(){ return +document.getElementById('safetyMargin').value },
  get showTrails()  { return document.getElementById('showTrails').checked },
  get showLinks()   { return document.getElementById('showLinks').checked },
  get showTargets() { return document.getElementById('showTargets').checked },
};

const MODE_DESC = {
  'Leader-Follower':   'One designated leader; others maintain relative offsets. Simple hierarchy — leader failure propagates errors.',
  'Consensus-Based':   'Agents average neighbour states iteratively. Convergent and robust; requires network connectivity.',
  'Behavior-Based':    'Emergent formation from blended local behaviours: separation, cohesion, alignment, goal-seeking.',
  'Virtual Structure': 'Formation treated as a rigid virtual body; each drone tracks its slot via PD control. High fidelity.',
  'Potential Field':   'Goal positions attract; drones and obstacles repel via inverse-square fields. Physically intuitive.',
};

// Slider label updates
const SLIDERS = [
  ['nDrones','vDrones',1,0],['formCx','vCx',1,0],['formCy','vCy',1,0],
  ['formScale','vScale',0.1,1],['formRot','vRot',1,0],
  ['commRadius','vComm',1,0],['senseRadius','vSense',1,0],
  ['maxSpeed','vSpeed',0.5,1],['maxAccel','vAccel',0.5,1],['transSpeed','vTrans',0.1,1],
  ['windX','vWx',0.5,1],['windY','vWy',0.5,1],['noiseLevel','vNoise',0.1,1],
  ['collisionR','vColR',0.5,1],['safetyMargin','vSafe',0.5,1],
];
SLIDERS.forEach(([id,vid])=>{
  const el=document.getElementById(id);
  const vl=document.getElementById(vid);
  el.oninput=()=>{ vl.textContent=parseFloat(el.value).toFixed(el.step&&el.step<1?1:0); };
});
document.getElementById('controlMode').onchange = () => {
  document.getElementById('modeDesc').textContent = MODE_DESC[C.controlMode] || '';
};

// ═══════════════════════════════════════════════════════════════
// CANVAS SETUP
// ═══════════════════════════════════════════════════════════════
const canvas = document.getElementById('sim');
const ctx    = canvas.getContext('2d');
const MAP    = 100;

function resizeCanvas(){
  const wrap = document.getElementById('canvasWrap');
  canvas.width  = wrap.clientWidth;
  canvas.height = wrap.clientHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const w2s = (wx,wy) => [
  (wx + MAP) / (2*MAP) * canvas.width,
  (MAP - wy) / (2*MAP) * canvas.height
];
const worldScale = () => canvas.width / (2*MAP);

// ═══════════════════════════════════════════════════════════════
// RNG
// ═══════════════════════════════════════════════════════════════
let _s = 12345;
const rand  = () => { _s^=_s<<13;_s^=_s>>17;_s^=_s<<5;return(_s>>>0)/4294967296; };
const rr    = (a,b) => a+(b-a)*rand();
const randN = () => { let u,v; do u=rand();while(!u); do v=rand();while(!v); return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); };

// ═══════════════════════════════════════════════════════════════
// FORMATION GEOMETRY
// ═══════════════════════════════════════════════════════════════
function genFormation(n){
  const pts=[], sp=8*C.formScale, f=C.formation;
  if(f==='Line')        { for(let i=0;i<n;i++) pts.push([(i-(n-1)/2)*sp,0]); }
  else if(f==='Column') { for(let i=0;i<n;i++) pts.push([0,(i-(n-1)/2)*sp]); }
  else if(f==='V-Shape'){ pts.push([0,0]); for(let i=1;i<n;i++){const s=i%2===0?1:-1,r=Math.ceil(i/2);pts.push([s*r*sp*.8,-r*sp*.6]);} }
  else if(f==='Circle') { const r=sp*n/(2*Math.PI); for(let i=0;i<n;i++){const a=2*Math.PI*i/n;pts.push([r*Math.cos(a),r*Math.sin(a)]);} }
  else if(f==='Square') { const s=Math.max(2,Math.ceil(Math.sqrt(n))); for(let i=0;i<n;i++){const row=Math.floor(i/s),col=i%s;pts.push([(col-(s-1)/2)*sp,(row-(s-1)/2)*sp]);} }
  else if(f==='Wedge')  { pts.push([0,0]);let row=1,co=1,idx=1;while(idx<n){pts.push([-co*sp*.7,-row*sp*.7]);idx++;if(idx<n){pts.push([co*sp*.7,-row*sp*.7]);idx++;}row++;co++;} }
  else if(f==='Grid')   { const cols=Math.max(2,Math.ceil(Math.sqrt(n)));for(let i=0;i<n;i++){const r=Math.floor(i/cols),c=i%cols;pts.push([(c-(cols-1)/2)*sp,(r-(Math.ceil(n/cols)-1)/2)*sp]);} }
  else if(f==='Ring')   { const ir=sp*Math.max(3,Math.floor(n/4))/(2*Math.PI),or=ir*1.8,split=Math.floor(n/2);for(let i=0;i<split;i++){const a=2*Math.PI*i/split;pts.push([ir*Math.cos(a),ir*Math.sin(a)]);}for(let i=0;i<n-split;i++){const a=2*Math.PI*i/(n-split);pts.push([or*Math.cos(a),or*Math.sin(a)]);} }
  else if(f==='Spiral') { for(let i=0;i<n;i++){const t=i/Math.max(n-1,1)*4*Math.PI,r=sp*.5*t/(2*Math.PI)+sp;pts.push([r*Math.cos(t),r*Math.sin(t)]);} }
  else if(f==='Expanding Wave'){ const w=n*sp;for(let i=0;i<n;i++){const x=(i/Math.max(n-1,1)-.5)*w,y=sp*1.5*Math.sin(2*Math.PI*i/Math.max(n-1,1));pts.push([x,y]);} }
  const cr=Math.cos(C.formRot*Math.PI/180),sr=Math.sin(C.formRot*Math.PI/180);
  return pts.map(([px,py])=>[px*cr-py*sr+C.formCx, px*sr+py*cr+C.formCy]);
}

function optAssign(drones,targets){
  const res=new Array(drones.length).fill(-1),used=new Array(targets.length).fill(false);
  for(let di=0;di<drones.length;di++){
    let best=Infinity,bi=-1;
    for(let ti=0;ti<targets.length;ti++){
      if(used[ti])continue;
      const d=Math.hypot(drones[di].x-targets[ti][0],drones[di].y-targets[ti][1]);
      if(d<best){best=d;bi=ti;}
    }
    if(bi>=0){res[di]=bi;used[bi]=true;}
  }
  return res;
}

// ═══════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════
let drones=[], obstacles=[], simTime=0, collisions=0, events=[], errHist=[];

function mkDrone(id){ return {id,x:rr(-45,45),y:rr(-45,45),vx:rr(-1,1),vy:rr(-1,1),heading:0,tx:0,ty:0,isLeader:id===0,failed:false,battery:rr(75,100),trail:[]}; }

function resetSim(seed){
  if(seed!==undefined)_s=seed;
  drones=[];obstacles=[];simTime=0;collisions=0;events=[];errHist=[];
  for(let i=0;i<C.nDrones;i++) drones.push(mkDrone(i));
  assignTargets();
  logEv('✅ Simulation reset');
}

function assignTargets(){
  const tgts=genFormation(drones.length), asgn=optAssign(drones,tgts);
  drones.forEach((d,i)=>{ const ti=asgn[i]>=0?asgn[i]:i%tgts.length; d.tx=tgts[ti][0]; d.ty=tgts[ti][1]; });
}

// ═══════════════════════════════════════════════════════════════
// CONTROL LAWS
// ═══════════════════════════════════════════════════════════════
function goto(d,tx,ty){
  const dx=tx-d.x,dy=ty-d.y,dist=Math.hypot(dx,dy)+1e-6;
  const k=Math.min(2,dist/10)*C.maxAccel;
  return [k*dx/dist - d.vx, k*dy/dist - d.vy];
}

function computeForce(d){
  const active = drones.filter(x=>!x.failed);
  const nb  = active.filter(n=>n.id!==d.id && Math.hypot(d.x-n.x,d.y-n.y)<C.commRadius);
  const sns = active.filter(n=>n.id!==d.id && Math.hypot(d.x-n.x,d.y-n.y)<C.senseRadius);
  const m   = C.controlMode;
  let fx=0,fy=0;

  if(m==='Leader-Follower'){
    const ldr=active.find(x=>x.isLeader);
    if(d.isLeader||!ldr){[fx,fy]=goto(d,d.tx,d.ty);}
    else {[fx,fy]=goto(d,ldr.x+(d.tx-ldr.tx),ldr.y+(d.ty-ldr.ty));}
  }
  else if(m==='Consensus-Based'){
    fx=1.5*(d.tx-d.x)-.8*d.vx; fy=1.5*(d.ty-d.y)-.8*d.vy;
    if(nb.length){ fx+=.3*(nb.reduce((s,n)=>s+n.x,0)/nb.length-d.x); fy+=.3*(nb.reduce((s,n)=>s+n.y,0)/nb.length-d.y); }
  }
  else if(m==='Behavior-Based'){
    const dg=Math.hypot(d.tx-d.x,d.ty-d.y)+1e-6;
    fx=2*(d.tx-d.x)/dg; fy=2*(d.ty-d.y)/dg;
    if(sns.length){
      let sx=0,sy=0,cx=0,cy=0,avx=0,avy=0;
      sns.forEach(n=>{ const dn=Math.hypot(d.x-n.x,d.y-n.y)+1e-6; if(dn<C.senseRadius*.5){sx+=(d.x-n.x)/dn;sy+=(d.y-n.y)/dn;} cx+=n.x;cy+=n.y;avx+=n.vx;avy+=n.vy; });
      const nb2=sns.length;
      fx+=1.5*sx/nb2+.3*(cx/nb2-d.x)+.4*(avx/nb2-d.vx);
      fy+=1.5*sy/nb2+.3*(cy/nb2-d.y)+.4*(avy/nb2-d.vy);
    }
  }
  else if(m==='Virtual Structure'){
    fx=2*(d.tx-d.x)-d.vx; fy=2*(d.ty-d.y)-d.vy;
  }
  else { // Potential Field
    const dd=Math.hypot(d.tx-d.x,d.ty-d.y)+1e-6;
    fx=2.5*(d.tx-d.x)/(dd+1); fy=2.5*(d.ty-d.y)/(dd+1);
    sns.forEach(n=>{ const dn=Math.hypot(d.x-n.x,d.y-n.y)+.1; if(dn<C.senseRadius){const s=3/(dn*dn);fx+=s*(d.x-n.x)/dn;fy+=s*(d.y-n.y)/dn;} });
  }
  return [fx,fy];
}

// ═══════════════════════════════════════════════════════════════
// PHYSICS STEP
// ═══════════════════════════════════════════════════════════════
const DT = 0.05;
const TRAIL = 45;

function step(){
  const active=drones.filter(d=>!d.failed);
  const forces=new Map();

  active.forEach(d=>{
    let [fx,fy]=computeForce(d);
    fx += C.windX + C.noiseLevel*randN();
    fy += C.windY + C.noiseLevel*randN();

    // Drone repulsion
    active.forEach(o=>{ if(o.id===d.id)return; const dn=Math.hypot(d.x-o.x,d.y-o.y)+1e-6,rep=C.collisionR+C.safetyMargin; if(dn<rep){const f=(rep-dn)/rep*C.maxAccel*2;fx+=(d.x-o.x)/dn*f;fy+=(d.y-o.y)/dn*f;} });
    // Obstacle repulsion
    obstacles.forEach(ob=>{ const dn=Math.hypot(d.x-ob.x,d.y-ob.y)+1e-6,rep=ob.r+C.collisionR+C.safetyMargin*2; if(dn<rep){const f=(rep-dn)/rep*C.maxAccel*3;fx+=(d.x-ob.x)/dn*f;fy+=(d.y-ob.y)/dn*f;} });
    // Boundary
    const B=MAP-5;
    if(d.x> B)fx-=C.maxAccel*(d.x-B)/5; if(d.x<-B)fx+=C.maxAccel*(-B-d.x)/5;
    if(d.y> B)fy-=C.maxAccel*(d.y-B)/5; if(d.y<-B)fy+=C.maxAccel*(-B-d.y)/5;
    forces.set(d.id,[fx,fy]);
  });

  active.forEach(d=>{
    let [fx,fy]=forces.get(d.id)||[0,0];
    const am=Math.hypot(fx,fy); if(am>C.maxAccel){fx=fx/am*C.maxAccel;fy=fy/am*C.maxAccel;}
    d.vx+=fx*DT; d.vy+=fy*DT;
    const spd=Math.hypot(d.vx,d.vy); if(spd>C.maxSpeed){d.vx=d.vx/spd*C.maxSpeed;d.vy=d.vy/spd*C.maxSpeed;}
    d.trail.push([d.x,d.y]); if(d.trail.length>TRAIL)d.trail.shift();
    d.x+=d.vx*DT; d.y+=d.vy*DT;
    if(Math.hypot(d.vx,d.vy)>.1) d.heading=Math.atan2(d.vy,d.vx);
    d.battery=Math.max(0,d.battery-.004);
  });

  for(let i=0;i<active.length;i++) for(let j=i+1;j<active.length;j++) if(Math.hypot(active[i].x-active[j].x,active[i].y-active[j].y)<C.collisionR) collisions++;

  simTime+=DT;
  errHist.push(fmtErr()); if(errHist.length>220)errHist.shift();
}

// ═══════════════════════════════════════════════════════════════
// METRICS
// ═══════════════════════════════════════════════════════════════
const act = () => drones.filter(d=>!d.failed);
function fmtErr(){ const a=act(); return a.length ? a.reduce((s,d)=>s+Math.hypot(d.x-d.tx,d.y-d.ty),0)/a.length : 0; }
function spErr(){  const a=act(); if(a.length<2)return 0; const ideal=8*C.formScale; let s=0,c=0; for(let i=0;i<a.length;i++) for(let j=i+1;j<a.length;j++){s+=Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y);c++;} return Math.abs(s/c-ideal); }
function alnErr(){ const a=act(); if(a.length<2)return 0; const mh=a.reduce((s,d)=>s+d.heading,0)/a.length; return Math.sqrt(a.reduce((s,d)=>s+(d.heading-mh)**2,0)/a.length); }
function covArea(){ const a=act(); if(a.length<3)return 0; const xs=a.map(d=>d.x),ys=a.map(d=>d.y); return(Math.max(...xs)-Math.min(...xs))*(Math.max(...ys)-Math.min(...ys)); }
function conn(){   const a=act(); if(a.length<2)return 1; let e=0,me=a.length*(a.length-1)/2; for(let i=0;i<a.length;i++) for(let j=i+1;j<a.length;j++) if(Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y)<C.commRadius)e++; return e/me; }
function cohe(){   const a=act(); if(!a.length)return 0; const cx=a.reduce((s,d)=>s+d.x,0)/a.length,cy=a.reduce((s,d)=>s+d.y,0)/a.length; return Math.max(0,100-a.reduce((s,d)=>s+Math.hypot(d.x-cx,d.y-cy),0)/a.length); }

// ═══════════════════════════════════════════════════════════════
// RENDER
// ═══════════════════════════════════════════════════════════════
function drawArrow(sx,sy,heading,sz,fill){
  ctx.save(); ctx.translate(sx,sy); ctx.rotate(heading+Math.PI/2);
  ctx.beginPath(); ctx.moveTo(0,-sz); ctx.lineTo(sz*.55,sz*.65); ctx.lineTo(0,sz*.2); ctx.lineTo(-sz*.55,sz*.65); ctx.closePath();
  ctx.fillStyle=fill; ctx.fill();
  ctx.strokeStyle='rgba(255,255,255,.85)'; ctx.lineWidth=1.5; ctx.stroke();
  ctx.restore();
}

function render(){
  const W=canvas.width, H=canvas.height, S=worldScale();
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#fafbff'; ctx.fillRect(0,0,W,H);

  // Grid
  ctx.strokeStyle='#e8ecf7'; ctx.lineWidth=1;
  for(let gx=-MAP;gx<=MAP;gx+=10){ const [sx,sy0]=w2s(gx,MAP),[,sy1]=w2s(gx,-MAP); ctx.beginPath();ctx.moveTo(sx,sy0);ctx.lineTo(sx,sy1);ctx.stroke(); }
  for(let gy=-MAP;gy<=MAP;gy+=10){ const [sx0,sy]=w2s(-MAP,gy),[sx1]=w2s(MAP,gy);  ctx.beginPath();ctx.moveTo(sx0,sy);ctx.lineTo(sx1,sy);ctx.stroke(); }
  ctx.strokeStyle='#d1d5e8'; ctx.lineWidth=1.5;
  { const [sx,sy0]=w2s(0,MAP),[,sy1]=w2s(0,-MAP); ctx.beginPath();ctx.moveTo(sx,sy0);ctx.lineTo(sx,sy1);ctx.stroke(); }
  { const [sx0,sy]=w2s(-MAP,0),[sx1]=w2s(MAP,0);  ctx.beginPath();ctx.moveTo(sx0,sy);ctx.lineTo(sx1,sy);ctx.stroke(); }

  // Obstacles
  obstacles.forEach(ob=>{ const [ox,oy]=w2s(ob.x,ob.y),r=ob.r*S; ctx.beginPath();ctx.arc(ox,oy,r,0,2*Math.PI);ctx.fillStyle='rgba(239,68,68,.12)';ctx.fill();ctx.strokeStyle='#ef4444';ctx.lineWidth=2;ctx.stroke(); });

  // Comm links
  if(C.showLinks){ const a=act(); ctx.strokeStyle='rgba(99,102,241,.13)';ctx.lineWidth=1; for(let i=0;i<a.length;i++) for(let j=i+1;j<a.length;j++){ if(Math.hypot(a[i].x-a[j].x,a[i].y-a[j].y)<C.commRadius){ const [ax,ay]=w2s(a[i].x,a[i].y),[bx,by]=w2s(a[j].x,a[j].y); ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke(); } } }

  // Target crosses
  if(C.showTargets){ drones.filter(d=>!d.failed).forEach(d=>{ const [tx,ty]=w2s(d.tx,d.ty),s=5; ctx.strokeStyle='rgba(99,102,241,.4)';ctx.lineWidth=1.5; ctx.beginPath();ctx.moveTo(tx-s,ty-s);ctx.lineTo(tx+s,ty+s);ctx.moveTo(tx+s,ty-s);ctx.lineTo(tx-s,ty+s);ctx.stroke(); }); }

  // Trails
  if(C.showTrails){ drones.filter(d=>!d.failed&&d.trail.length>1).forEach(d=>{ for(let i=1;i<d.trail.length;i++){ ctx.strokeStyle=`rgba(99,102,241,${(0.03+.27*(i/d.trail.length)).toFixed(2)})`; ctx.lineWidth=1.2; const [ax,ay]=w2s(d.trail[i-1][0],d.trail[i-1][1]),[bx,by]=w2s(d.trail[i][0],d.trail[i][1]); ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke(); } }); }

  // Drones
  drones.forEach(d=>{
    const [sx,sy]=w2s(d.x,d.y);
    if(d.failed){ ctx.save();ctx.globalAlpha=.35;ctx.beginPath();ctx.arc(sx,sy,8,0,2*Math.PI);ctx.fillStyle='#9ca3af';ctx.fill();ctx.restore();ctx.fillStyle='#6b7280';ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('✕',sx,sy);return; }
    const err=Math.hypot(d.x-d.tx,d.y-d.ty),t=Math.min(err/20,1);
    const r=Math.round(99+t*(244-99)),g=Math.round(102+t*(63-102)),b=Math.round(241+t*(63-241));
    const fill = d.isLeader ? '#f59e0b' : `rgb(${r},${g},${b})`;
    drawArrow(sx,sy,d.heading,d.isLeader?11:8,fill);
    ctx.fillStyle='#64748b';ctx.font='8px sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText(d.id,sx+12,sy);
    const bw=13,bh=2.5;
    ctx.fillStyle='#e2e8f0';ctx.fillRect(sx-bw/2,sy+12,bw,bh);
    ctx.fillStyle=d.battery>50?'#22c55e':d.battery>25?'#f59e0b':'#ef4444';ctx.fillRect(sx-bw/2,sy+12,bw*d.battery/100,bh);
  });

  // Leader halo
  const ldr=drones.find(d=>d.isLeader&&!d.failed);
  if(ldr){ const [lx,ly]=w2s(ldr.x,ldr.y);ctx.beginPath();ctx.arc(lx,ly,17,0,2*Math.PI);ctx.strokeStyle='rgba(245,158,11,.4)';ctx.lineWidth=2.5;ctx.stroke(); }
}

function drawChart(){
  const cc=document.getElementById('chartCanvas'),cx2=cc.getContext('2d'),cw=cc.width,ch=cc.height;
  cx2.clearRect(0,0,cw,ch);
  if(errHist.length<2)return;
  const mx=Math.max(...errHist,1);
  cx2.strokeStyle='rgba(99,102,241,.1)';cx2.lineWidth=1;
  for(let i=0;i<=4;i++){const y=ch-ch*(i/4)*.85-6;cx2.beginPath();cx2.moveTo(0,y);cx2.lineTo(cw,y);cx2.stroke();}
  cx2.beginPath();
  errHist.forEach((v,i)=>{ const x=cw*i/errHist.length,y=ch-(v/mx)*(ch-14)-5; i===0?cx2.moveTo(x,y):cx2.lineTo(x,y); });
  cx2.strokeStyle='#6366f1';cx2.lineWidth=2;cx2.stroke();
  cx2.lineTo(cw,ch);cx2.lineTo(0,ch);cx2.closePath();cx2.fillStyle='rgba(99,102,241,.08)';cx2.fill();
  cx2.fillStyle='#312e81';cx2.font='bold 9px sans-serif';cx2.textAlign='right';cx2.fillText(errHist[errHist.length-1].toFixed(1),cw-2,11);
}

function updateUI(){
  document.getElementById('mFE').textContent = fmtErr().toFixed(2)+' u';
  document.getElementById('mSE').textContent = spErr().toFixed(2)+' u';
  document.getElementById('mAE').textContent = alnErr().toFixed(3)+' rad';
  document.getElementById('mCA').textContent = Math.round(covArea())+' u²';
  document.getElementById('mCN').textContent = Math.round(conn()*100)+'%';
  document.getElementById('mCO').textContent = cohe().toFixed(1);
  document.getElementById('mCL').textContent = collisions;
  document.getElementById('overlay').textContent = C.controlMode+' · '+C.formation;
  document.getElementById('timeov').textContent  = 't = '+simTime.toFixed(1)+' s';
  drawChart();
}

function logEv(msg){
  events.unshift(msg); if(events.length>20)events.pop();
  document.getElementById('log').innerHTML = events.map(e=>`<div class="loge">${e}</div>`).join('');
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP — fixed timestep accumulator, no Streamlit reruns
// ═══════════════════════════════════════════════════════════════
let running=false, lastT=0, acc=0;
const STEP_MS = DT*1000;

function loop(now){
  requestAnimationFrame(loop);
  const dt=Math.min(now-lastT, 80); lastT=now;
  if(running){
    acc+=dt;
    let stepped=false;
    while(acc>=STEP_MS){ step(); acc-=STEP_MS; stepped=true; }
    if(stepped) updateUI();
  }
  render();
}

// ═══════════════════════════════════════════════════════════════
// BUTTONS
// ═══════════════════════════════════════════════════════════════
document.getElementById('btnPlay').onclick = function(){
  running=!running;
  this.textContent = running ? '⏸ Pause' : '▶ Start';
  document.getElementById('pauseBanner').style.display = running ? 'none' : 'flex';
};
document.getElementById('btnReset').onclick = () => {
  running=false; document.getElementById('btnPlay').textContent='▶ Start';
  document.getElementById('pauseBanner').style.display='none';
  resetSim(12345); render(); updateUI();
};
document.getElementById('btnRandom').onclick = () => { resetSim(Math.floor(Math.random()*999999)); };
document.getElementById('btnSwitch').onclick = () => { assignTargets(); logEv('🔄 Formation → '+C.formation); };
document.getElementById('btnFail').onclick   = () => { const c=drones.filter(d=>!d.failed&&!d.isLeader); if(c.length){const v=c[Math.floor(rand()*c.length)];v.failed=true;logEv(`⚠️ Drone #${v.id} failed at t=${simTime.toFixed(1)}s`);} };
document.getElementById('btnObs').onclick    = () => { const ob={x:rr(-55,55),y:rr(-55,55),r:rr(4,9)};obstacles.push(ob);logEv(`🚧 Obstacle at (${ob.x.toFixed(0)},${ob.y.toFixed(0)})`); };
document.getElementById('btnGust').onclick   = () => { document.getElementById('windX').value=rr(-4,4).toFixed(1);document.getElementById('windY').value=rr(-4,4).toFixed(1);document.getElementById('vWx').textContent=parseFloat(document.getElementById('windX').value).toFixed(1);document.getElementById('vWy').textContent=parseFloat(document.getElementById('windY').value).toFixed(1);logEv(`💨 Wind gust (${C.windX.toFixed(1)},${C.windY.toFixed(1)})`); };
document.getElementById('btnClearWind').onclick = () => { document.getElementById('windX').value=0;document.getElementById('windY').value=0;document.getElementById('vWx').textContent='0.0';document.getElementById('vWy').textContent='0.0';logEv('🔕 Wind cleared'); };

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════
resetSim(12345);
render();
updateUI();
requestAnimationFrame(loop);
</script>
</body>
</html>
""", height=820, scrolling=False)