<div align="center">

```
██████╗ ██████╗  ██████╗ ███╗   ██╗███████╗
██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝
██║  ██║██████╔╝██║   ██║██╔██╗ ██║█████╗
██║  ██║██╔══██╗██║   ██║██║╚██╗██║██╔══╝
██████╔╝██║  ██║╚██████╔╝██║ ╚████║███████╗
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

███████╗ ██████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝██╔═══██╗██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
█████╗  ██║   ██║██████╔╝██╔████╔██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

              C O N T R O L   L A B
        ── swarm intelligence in your browser ──
```

<br/>

[![Live Demo](https://img.shields.io/badge/🚀_LIVE_DEMO-Streamlit-FF4B4B?style=for-the-badge&logoColor=white)](https://drone-formation-control-lab-fjcnxvfbbv6r48tbffmrns.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![60 FPS](https://img.shields.io/badge/Animation-60_FPS-00D4AA?style=for-the-badge)]()
[![Zero Reruns](https://img.shields.io/badge/Streamlit_Reruns-ZERO-6366F1?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **A research-grade, real-time multi-drone swarm simulator.**
> Watch decentralised agents self-organise into geometric formations, survive failures,
> dodge obstacles, and reconfigure on the fly — all at a buttery smooth 60 fps.

</div>

---

## ⚡ What Is This?

**Drone Formation Control Lab** is an interactive swarm intelligence playground built for:

- 🎓 **Robotics researchers** studying decentralised multi-agent coordination
- 🛠️ **Engineers** prototyping UAV formation algorithms without hardware
- 🧪 **Students** who want to *see* control theory actually work
- 💼 **Portfolio builders** who want something that looks serious

It simulates **up to 40 autonomous drones** that sense their local neighbourhood, communicate with peers, and collectively converge into one of **10 geometric formations** — using five distinct control strategies borrowed directly from the swarm robotics literature.

**No fake animations. No pre-scripted paths.** Every drone computes its own forces on every single frame.

---

## 🎮 Live Demo

**[drone-formation-control-lab.streamlit.app](https://drone-formation-control-lab-fjcnxvfbbv6r48tbffmrns.streamlit.app/)**

Hit **▶ Start**, pick a formation, watch the swarm self-organise.
Then break things — inject failures, drop obstacles, crank up the wind.

---

## 🧠 Control Strategies

Five fundamentally different answers to: *how do N agents with no global knowledge form a shape?*

### 🟡 Leader-Follower

```
Leader ──▶ Follower₁ ──▶ Follower₂ ──▶ ... ──▶ Followerₙ
```

One drone is designated leader. All others maintain rigid relative offsets from it.
Fast to converge, easy to understand.
**Weakness:** Leader dropout collapses the entire formation.

---

### 🔵 Consensus-Based

```
xᵢ(t+1) = xᵢ(t) + ε · Σⱼ∈Nᵢ [ xⱼ(t) − xᵢ(t) ]
```

Drones exchange state estimates with neighbours and iteratively average toward agreement.
Provably convergent if the communication graph stays connected.
**Strength:** Gracefully degrades when individual drones fail.

---

### 🟢 Behavior-Based (Reynolds Rules)

```
F_total = w₁·F_separation + w₂·F_cohesion + w₃·F_alignment + w₄·F_goal
```

Inspired by Craig Reynolds' Boids (1987). Four primitive steering behaviours combine into emergent formation. No explicit geometry — the shape falls out of local rules alone.
**Strength:** Biologically plausible, robust to noise and dropout.

---

### 🟣 Virtual Structure

```
Formation = rigid virtual body  P(t)
Drone i target: pᵢ* = P(t) · offsetᵢ
Control: Fᵢ = Kp·(pᵢ* − pᵢ) − Kd·ṗᵢ
```

The formation is a single rigid virtual body. Each drone runs a PD controller to track its assigned slot on that body. Smooth, precise, high fidelity.
**Strength:** Best formation accuracy of all five modes.

---

### 🔴 Potential Field

```
U_attract = ½ · ξ · ‖p − p_goal‖²
U_repel   = ½ · η · (1/ρ − 1/ρ₀)²   for ρ < ρ₀
F = −∇U
```

Goal positions pull; drones and obstacles push. Each agent follows the gradient of the combined energy landscape.
**Strength:** Collision avoidance is intrinsic to the control law.
**Weakness:** Local minima can trap drones.

---

## 🔷 Formation Library

| # | Formation | Description | Best With |
|---|---|---|---|
| 1 | **Circle** | Equal-spaced ring | Virtual Structure |
| 2 | **Line** | Horizontal row | Leader-Follower |
| 3 | **Column** | Vertical column | Leader-Follower |
| 4 | **V-Shape** | Classic chevron | Leader-Follower |
| 5 | **Square** | 2D grid square | Virtual Structure |
| 6 | **Wedge** | Forward-pointing arrow | Potential Field |
| 7 | **Grid** | Rectangular lattice | Virtual Structure |
| 8 | **Ring** | Concentric double ring | Consensus |
| 9 | **Spiral** | Archimedean spiral | Behavior-Based |
| 10 | **Expanding Wave** | Sinusoidal spread | Behavior-Based |

All formations support **live scale, rotation, and translation** — drag any slider and the swarm reshapes mid-flight, no restart needed.

---

## 💥 Chaos Injection

Because a simulator that never breaks isn't interesting.

| Button | What Happens |
|---|---|
| `⚠️ Fail Drone` | Kills a random non-leader drone instantly. Watch the swarm adapt — or fall apart. |
| `🚧 Add Obstacle` | Spawns a repulsive obstacle with a wide quadratic force field. Drones route around it. |
| `💨 Wind Gust` | Fires a random directional wind perturbation across the whole swarm. |
| `✕ Clear Wind` | Kills all wind. Swarm re-stabilises. |
| `🎲 Randomise` | Scrambles all drone positions with a new random seed. |
| `🔄 Switch Formation` | Reassigns all targets to the current formation — triggers a live reconfiguration. |

---

## 📊 Live Metrics

Seven metrics update every frame in the right panel:

```
Formation Error  ─── mean distance of each drone to its assigned target slot  (world units)
Spacing Error    ─── deviation from the ideal inter-drone spacing
Alignment Error  ─── heading variance across the active swarm  (radians)
Coverage Area    ─── bounding box area of the active swarm  (u²)
Connectivity     ─── fraction of possible comm links currently live  (%)
Cohesion Score   ─── inverse mean distance from swarm centroid  (0 – 100)
Collisions       ─── cumulative inter-drone collision count since last reset
```

Plus a rolling **Formation Error history chart** — watch convergence speed differ between modes.

---

## 🏗️ Architecture

The key architectural decision is why this runs smoothly at 60 fps while typical Streamlit sims flicker:

```
┌─────────────────────────────────────────────────────────────┐
│                       app.py                                │
│                                                             │
│   st.components.v1.html(ENTIRE_APP)  ◄── runs ONCE         │
│                          │                                  │
│          ┌───────────────┼──────────────────┐               │
│          │               │                  │               │
│     Left Panel      Canvas (JS)        Right Panel          │
│     HTML controls   requestAnimationFrame   Metrics         │
│     read by JS      60 fps physics loop     HTML            │
│                          │                                  │
│              ┌───────────▼────────────┐                     │
│              │   Fixed-step physics   │                     │
│              │   Δt = 50ms accumulator│                     │
│              │   All 5 control laws   │                     │
│              │   Repulsion fields     │                     │
│              │   Collision detection  │                     │
│              └────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘

  Python runs ONCE.  Zero reruns.  Zero flicker.
  Everything after page load = pure browser JS.
```

**The standard Streamlit approach** calls `st.rerun()` in a loop → full Python re-execution + iframe teardown + rebuild on every frame → catastrophic flicker at any reasonable speed.

**This approach** embeds everything — controls, physics, renderer — inside a single `components.html` call. Python's job is done in 20 lines. The browser's `requestAnimationFrame` drives the rest at native GPU-composited speed.

---

## 🔬 Physics Engine

Each simulation step (`Δt = 50 ms`):

```
1. Force computation     control law + wind + noise
2. Drone repulsion       soft zone, quadratic falloff
3. Obstacle repulsion    wide influence field (4× radius + 20 units)
4. Boundary enforcement  soft MAP_EDGE repulsion
5. Acceleration clamp    |F| ≤ maxAccel
6. Velocity integration  v += F · Δt
7. Speed clamp           |v| ≤ maxSpeed
8. Position integration  p += v · Δt
9. Heading update        θ = atan2(vy, vx)
10. Collision counting   O(n²) pairwise check
```

The main loop uses a **fixed-timestep accumulator** — physics advances in exact 50 ms chunks regardless of frame rate, preventing time-step instability on slow machines.

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/yourusername/drone-formation-control-lab
cd drone-formation-control-lab

# 2. Install the one dependency
pip install streamlit

# 3. Launch
streamlit run app.py
```

Open `http://localhost:8501`. Done.

---

## 📁 Project Structure

```
drone-formation-control-lab/
│
├── app.py              ← The entire application
│                         ~20 lines Python, ~650 lines JS
├── requirements.txt    ← streamlit>=1.32.0
└── README.md           ← You are here
```

One file. One dependency. The whole physics engine, all five control laws, all ten formation generators, the renderer, the metrics panel — all of it lives in `app.py`.

---

## 🔭 Roadmap

- [ ] 3D mode with altitude control layer
- [ ] MAVLink bridge — stream targets to real PX4/ArduPilot hardware
- [ ] Reinforcement learning formation policy (replace hand-coded laws)
- [ ] Multi-stage mission mode with waypoint sequences
- [ ] Side-by-side comparison of two control modes converging simultaneously
- [ ] Simulation replay recorder and playback
- [ ] Custom formation painter — click to place arbitrary target points
- [ ] Communication delay and packet loss simulation

---

## 📚 References

- Reynolds, C. (1987). *Flocks, Herds, and Schools: A Distributed Behavioral Model.* SIGGRAPH.
- Olfati-Saber, R. (2006). *Flocking for Multi-Agent Dynamic Systems: Algorithms and Theory.* IEEE TAC.
- Lewis & Tan (1997). *High Precision Formation Control of Mobile Robots Using Virtual Structure Approach.* Autonomous Robots.
- Beard, Lawton & Hadaegh (2001). *A Coordination Architecture for Spacecraft Formation Control.* IEEE TSMC.
- Ge & Cui (2002). *Dynamic Motion Planning for Mobile Robots Using Potential Field Method.* Autonomous Robots.

---

<div align="center">

**Built with Python, Streamlit, and an unreasonable amount of JavaScript.**

*Star it · Fork it · Break it · Improve it.*

<br/>

```
    ▲         ▲     ▲       ▲   ▲
   ▲ ▲    ▲     ▲     ▲   ▲   ▲
  ▲   ▲     ▲     ▲ ▲   ▲       ▲

       s w a r m   o n .
```

</div>
