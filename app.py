"""
Drone Formation Control Lab
============================
A research-grade interactive swarm simulation built with Streamlit + Plotly.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
import json
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum

# ─────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Drone Formation Control Lab",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# WHITE THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global background & text ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #f8f9fc !important;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * { color: #1a1a2e !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #f0f4ff;
    border: 1px solid #c7d2fe;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 6px;
}
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #6366f1 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { font-size: 1.4rem !important; color: #1a1a2e !important; font-weight: 700 !important; }

/* ── Buttons ── */
.stButton > button {
    background: #4f46e5;
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 0.85rem;
    transition: background 0.2s;
}
.stButton > button:hover { background: #4338ca; }

/* ── Headers ── */
h1 { color: #1a1a2e !important; font-weight: 800 !important; letter-spacing: -0.5px; }
h2 { color: #312e81 !important; font-weight: 700 !important; }
h3 { color: #4338ca !important; font-weight: 600 !important; }

/* ── Sliders & inputs ── */
[data-testid="stSlider"] > div > div { background: #c7d2fe; }
[data-baseweb="select"] { background: #fff !important; border-radius: 8px !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #eef2ff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: #312e81 !important;
}

/* ── Info / warning boxes ── */
.stInfo { background: #eef2ff !important; color: #312e81 !important; border-left: 4px solid #6366f1 !important; }
.stWarning { background: #fffbeb !important; border-left: 4px solid #f59e0b !important; }
.stSuccess { background: #f0fdf4 !important; border-left: 4px solid #22c55e !important; }

/* ── Dividers ── */
hr { border-color: #e2e8f0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENUMS & CONSTANTS
# ─────────────────────────────────────────────
class ControlMode(str, Enum):
    LEADER_FOLLOWER  = "Leader-Follower"
    CONSENSUS        = "Consensus-Based"
    BEHAVIOR_BASED   = "Behavior-Based"
    VIRTUAL_STRUCTURE= "Virtual Structure"
    POTENTIAL_FIELD  = "Potential Field"

class FormationType(str, Enum):
    LINE     = "Line"
    COLUMN   = "Column"
    V_SHAPE  = "V-Shape"
    CIRCLE   = "Circle"
    SQUARE   = "Square"
    WEDGE    = "Wedge"
    GRID     = "Grid"
    RING     = "Ring"
    SPIRAL   = "Spiral"
    WAVE     = "Expanding Wave"
    CUSTOM   = "Custom"

CONTROL_DESCRIPTIONS = {
    ControlMode.LEADER_FOLLOWER:
        "One drone acts as leader; others maintain relative offsets from leader or predecessor. "
        "Simple but fragile — leader failure propagates errors.",
    ControlMode.CONSENSUS:
        "Agents exchange state estimates with neighbors and converge to agreement through averaging. "
        "Robust to individual failures; requires connectivity.",
    ControlMode.BEHAVIOR_BASED:
        "Each drone blends primitive behaviors: separation, cohesion, alignment, and goal-seeking. "
        "Emergent formation from local rules — biologically inspired.",
    ControlMode.VIRTUAL_STRUCTURE:
        "The formation is treated as a rigid virtual body. Each drone tracks its slot on the body. "
        "High formation fidelity; centralized virtual reference.",
    ControlMode.POTENTIAL_FIELD:
        "Goal positions attract; other drones and obstacles repel. Smooth, physically intuitive. "
        "Risk of local minima; oscillation near obstacles.",
}

CANVAS_SIZE = 800
MAP_RANGE   = 100.0   # world units
DT          = 0.05    # simulation timestep (seconds)


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────
@dataclass
class Obstacle:
    x: float
    y: float
    radius: float

@dataclass
class Drone:
    id: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    heading: float = 0.0          # radians
    target_x: float = 0.0
    target_y: float = 0.0
    is_leader: bool = False
    failed: bool = False
    battery: float = 100.0
    trail_x: List[float] = field(default_factory=list)
    trail_y: List[float] = field(default_factory=list)
    collision_count: int = 0

    def distance_to(self, other: "Drone") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def distance_to_point(self, px: float, py: float) -> float:
        return math.hypot(self.x - px, self.y - py)


# ─────────────────────────────────────────────
# FORMATION GEOMETRY GENERATORS
# ─────────────────────────────────────────────
def generate_formation(
    formation: FormationType,
    n: int,
    cx: float = 0.0,
    cy: float = 0.0,
    scale: float = 1.0,
    rotation: float = 0.0,
    custom_points: Optional[List[Tuple[float, float]]] = None,
) -> List[Tuple[float, float]]:
    pts: List[Tuple[float, float]] = []
    spacing = 8.0 * scale

    if formation == FormationType.LINE:
        for i in range(n):
            pts.append(((i - (n - 1) / 2) * spacing, 0.0))

    elif formation == FormationType.COLUMN:
        for i in range(n):
            pts.append((0.0, (i - (n - 1) / 2) * spacing))

    elif formation == FormationType.V_SHAPE:
        half = n // 2
        pts.append((0.0, 0.0))
        for i in range(1, n):
            side = 1 if i % 2 == 0 else -1
            row = (i + 1) // 2
            pts.append((side * row * spacing * 0.8, -row * spacing * 0.6))

    elif formation == FormationType.CIRCLE:
        r = spacing * n / (2 * math.pi)
        for i in range(n):
            angle = 2 * math.pi * i / n
            pts.append((r * math.cos(angle), r * math.sin(angle)))

    elif formation == FormationType.SQUARE:
        side = max(2, int(math.ceil(math.sqrt(n))))
        for i in range(n):
            row, col = divmod(i, side)
            pts.append(((col - (side - 1) / 2) * spacing, (row - (side - 1) / 2) * spacing))

    elif formation == FormationType.WEDGE:
        pts.append((0.0, 0.0))
        row, col_offset = 1, 1
        idx = 1
        while idx < n:
            pts.append((-col_offset * spacing * 0.7, -row * spacing * 0.7))
            idx += 1
            if idx < n:
                pts.append((col_offset * spacing * 0.7, -row * spacing * 0.7))
                idx += 1
            row += 1
            col_offset += 1

    elif formation == FormationType.GRID:
        cols = max(2, int(math.ceil(math.sqrt(n))))
        rows = int(math.ceil(n / cols))
        for i in range(n):
            r, c = divmod(i, cols)
            pts.append(((c - (cols - 1) / 2) * spacing, (r - (rows - 1) / 2) * spacing))

    elif formation == FormationType.RING:
        inner_r = spacing * max(3, n // 4) / (2 * math.pi)
        outer_r = inner_r * 1.8
        split = n // 2
        for i in range(split):
            a = 2 * math.pi * i / split
            pts.append((inner_r * math.cos(a), inner_r * math.sin(a)))
        for i in range(n - split):
            a = 2 * math.pi * i / (n - split)
            pts.append((outer_r * math.cos(a), outer_r * math.sin(a)))

    elif formation == FormationType.SPIRAL:
        for i in range(n):
            t = i / max(n - 1, 1) * 4 * math.pi
            r = spacing * 0.5 * t / (2 * math.pi) + spacing
            pts.append((r * math.cos(t), r * math.sin(t)))

    elif formation == FormationType.WAVE:
        width = n * spacing
        for i in range(n):
            x = (i / max(n - 1, 1) - 0.5) * width
            y = spacing * 1.5 * math.sin(2 * math.pi * i / max(n - 1, 1))
            pts.append((x, y))

    elif formation == FormationType.CUSTOM:
        if custom_points and len(custom_points) >= n:
            pts = list(custom_points[:n])
        else:
            pts = [(0.0, 0.0)] * n

    # Apply rotation & translation
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    result = []
    for (px, py) in pts:
        rx = px * cos_r - py * sin_r + cx
        ry = px * sin_r + py * cos_r + cy
        result.append((rx, ry))

    return result


# ─────────────────────────────────────────────
# OPTIMAL ASSIGNMENT (greedy distance)
# ─────────────────────────────────────────────
def optimal_assignment(drones: List[Drone], targets: List[Tuple[float, float]]) -> List[int]:
    n = len(drones)
    m = len(targets)
    assigned = [-1] * n
    used = [False] * m
    for di in range(n):
        best_dist = float("inf")
        best_ti = -1
        for ti in range(m):
            if not used[ti]:
                d = math.hypot(drones[di].x - targets[ti][0], drones[di].y - targets[ti][1])
                if d < best_dist:
                    best_dist = d
                    best_ti = ti
        if best_ti >= 0:
            assigned[di] = best_ti
            used[best_ti] = True
    return assigned


# ─────────────────────────────────────────────
# SWARM SIMULATION ENGINE
# ─────────────────────────────────────────────
class SwarmSimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        n = st.session_state.get("n_drones", 12)
        self.drones: List[Drone] = []
        self.obstacles: List[Obstacle] = []
        self.time: float = 0.0
        self.collisions: int = 0
        self.convergence_time: Optional[float] = None
        self.formation_history: List[str] = []
        self.event_log: List[str] = []
        self.wind_x: float = 0.0
        self.wind_y: float = 0.0

        rng = np.random.default_rng(42)
        for i in range(n):
            d = Drone(
                id=i,
                x=float(rng.uniform(-40, 40)),
                y=float(rng.uniform(-40, 40)),
                vx=float(rng.uniform(-1, 1)),
                vy=float(rng.uniform(-1, 1)),
                is_leader=(i == 0),
                battery=float(rng.uniform(75, 100)),
            )
            self.drones.append(d)

        self._regenerate_targets()

    def _regenerate_targets(self):
        cfg = self._cfg()
        formation = FormationType(cfg["formation"])
        targets = generate_formation(
            formation, len(self.drones),
            cx=cfg["form_cx"], cy=cfg["form_cy"],
            scale=cfg["form_scale"], rotation=math.radians(cfg["form_rotation"]),
        )
        assignment = optimal_assignment(self.drones, targets)
        for i, d in enumerate(self.drones):
            ti = assignment[i] if assignment[i] >= 0 else i % len(targets)
            d.target_x, d.target_y = targets[ti]

    def _cfg(self) -> Dict:
        return {
            "n_drones":       st.session_state.get("n_drones", 12),
            "control_mode":   st.session_state.get("control_mode", ControlMode.VIRTUAL_STRUCTURE),
            "formation":      st.session_state.get("formation", FormationType.CIRCLE),
            "comm_radius":    st.session_state.get("comm_radius", 35.0),
            "sense_radius":   st.session_state.get("sense_radius", 20.0),
            "max_speed":      st.session_state.get("max_speed", 8.0),
            "max_accel":      st.session_state.get("max_accel", 4.0),
            "wind_x":         st.session_state.get("wind_x", 0.0),
            "wind_y":         st.session_state.get("wind_y", 0.0),
            "noise_level":    st.session_state.get("noise_level", 0.0),
            "collision_r":    st.session_state.get("collision_r", 2.5),
            "safety_margin":  st.session_state.get("safety_margin", 1.5),
            "show_trails":    st.session_state.get("show_trails", True),
            "show_links":     st.session_state.get("show_links", True),
            "show_targets":   st.session_state.get("show_targets", True),
            "form_cx":        st.session_state.get("form_cx", 0.0),
            "form_cy":        st.session_state.get("form_cy", 0.0),
            "form_scale":     st.session_state.get("form_scale", 1.0),
            "form_rotation":  st.session_state.get("form_rotation", 0.0),
            "trans_speed":    st.session_state.get("trans_speed", 1.0),
        }

    def step(self):
        cfg = self._cfg()
        rng = np.random.default_rng(int(self.time * 1000) % 100000)
        noise = cfg["noise_level"]
        wind_x = cfg["wind_x"]
        wind_y = cfg["wind_y"]
        max_spd = cfg["max_speed"] * cfg["trans_speed"]
        max_acc = cfg["max_accel"]
        col_r   = cfg["collision_r"]
        safety  = cfg["safety_margin"]
        mode    = cfg["control_mode"]

        active = [d for d in self.drones if not d.failed]

        for d in active:
            if len(d.trail_x) > 40:
                d.trail_x.pop(0); d.trail_y.pop(0)
            d.trail_x.append(d.x); d.trail_y.append(d.y)
            d.battery = max(0, d.battery - 0.01)

        # Compute desired velocities per control mode
        desired = {}
        for d in active:
            neighbors = [o for o in active if o.id != d.id and d.distance_to(o) < cfg["comm_radius"]]

            if mode == ControlMode.LEADER_FOLLOWER:
                fx, fy = self._leader_follower(d, active, cfg)
            elif mode == ControlMode.CONSENSUS:
                fx, fy = self._consensus(d, neighbors, cfg)
            elif mode == ControlMode.BEHAVIOR_BASED:
                fx, fy = self._behavior_based(d, neighbors, cfg)
            elif mode == ControlMode.VIRTUAL_STRUCTURE:
                fx, fy = self._virtual_structure(d, cfg)
            else:  # POTENTIAL_FIELD
                fx, fy = self._potential_field(d, neighbors, cfg)

            # Add wind + noise
            fx += wind_x + float(rng.normal(0, noise))
            fy += wind_y + float(rng.normal(0, noise))

            # Collision avoidance — repulsion from nearby drones
            for o in active:
                if o.id == d.id: continue
                dist = d.distance_to(o)
                rep_dist = col_r + safety
                if 0.01 < dist < rep_dist:
                    rep = (rep_dist - dist) / rep_dist * max_acc * 2
                    fx += (d.x - o.x) / dist * rep
                    fy += (d.y - o.y) / dist * rep

            # Obstacle repulsion
            for obs in self.obstacles:
                dist = math.hypot(d.x - obs.x, d.y - obs.y)
                rep_dist = obs.radius + col_r + safety * 2
                if 0.01 < dist < rep_dist:
                    rep = (rep_dist - dist) / rep_dist * max_acc * 3
                    fx += (d.x - obs.x) / dist * rep
                    fy += (d.y - obs.y) / dist * rep

            # Boundary repulsion
            boundary = MAP_RANGE - 5
            if d.x > boundary:  fx -= max_acc * (d.x - boundary) / 5
            if d.x < -boundary: fx += max_acc * (-boundary - d.x) / 5
            if d.y > boundary:  fy -= max_acc * (d.y - boundary) / 5
            if d.y < -boundary: fy += max_acc * (-boundary - d.y) / 5

            desired[d.id] = (fx, fy)

        # Integrate
        for d in active:
            fx, fy = desired.get(d.id, (0.0, 0.0))
            # Clamp acceleration
            amag = math.hypot(fx, fy)
            if amag > max_acc:
                fx, fy = fx / amag * max_acc, fy / amag * max_acc

            d.vx += fx * DT
            d.vy += fy * DT

            # Clamp speed
            spd = math.hypot(d.vx, d.vy)
            if spd > max_spd:
                d.vx, d.vy = d.vx / spd * max_spd, d.vy / spd * max_spd

            d.x += d.vx * DT
            d.y += d.vy * DT

            if math.hypot(d.vx, d.vy) > 0.1:
                d.heading = math.atan2(d.vy, d.vx)

        # Count collisions
        for i, a in enumerate(active):
            for b in active[i + 1:]:
                if a.distance_to(b) < col_r:
                    self.collisions += 1

        self.time += DT

    # ── Control implementations ──

    def _leader_follower(self, d: Drone, active: List[Drone], cfg) -> Tuple[float, float]:
        leader = next((a for a in active if a.is_leader), None)
        if d.is_leader:
            # Leader moves to its target
            return self._goto(d, d.target_x, d.target_y, cfg["max_accel"])
        if leader:
            # Follow leader with offset
            off_x = d.target_x - (leader.target_x if not leader.failed else 0)
            off_y = d.target_y - (leader.target_y if not leader.failed else 0)
            tx = leader.x + off_x
            ty = leader.y + off_y
            return self._goto(d, tx, ty, cfg["max_accel"])
        return self._goto(d, d.target_x, d.target_y, cfg["max_accel"])

    def _consensus(self, d: Drone, neighbors: List[Drone], cfg) -> Tuple[float, float]:
        k_p = 1.5; k_v = 0.8
        fx = k_p * (d.target_x - d.x) - k_v * d.vx
        fy = k_p * (d.target_y - d.y) - k_v * d.vy
        if neighbors:
            avg_x = sum(n.x for n in neighbors) / len(neighbors)
            avg_y = sum(n.y for n in neighbors) / len(neighbors)
            fx += 0.3 * (avg_x - d.x)
            fy += 0.3 * (avg_y - d.y)
        return fx, fy

    def _behavior_based(self, d: Drone, neighbors: List[Drone], cfg) -> Tuple[float, float]:
        # Goal
        dx_g = d.target_x - d.x; dy_g = d.target_y - d.y
        dist_g = math.hypot(dx_g, dy_g) + 1e-6
        fx = 2.0 * dx_g / dist_g
        fy = 2.0 * dy_g / dist_g

        if neighbors:
            # Separation
            sep_x = sep_y = 0.0
            for n in neighbors:
                dist = d.distance_to(n)
                if dist < cfg["sense_radius"] * 0.5 and dist > 0.01:
                    sep_x += (d.x - n.x) / dist
                    sep_y += (d.y - n.y) / dist
            fx += 1.5 * sep_x / len(neighbors)
            fy += 1.5 * sep_y / len(neighbors)

            # Cohesion
            cx = sum(n.x for n in neighbors) / len(neighbors)
            cy = sum(n.y for n in neighbors) / len(neighbors)
            fx += 0.3 * (cx - d.x)
            fy += 0.3 * (cy - d.y)

            # Alignment
            avg_vx = sum(n.vx for n in neighbors) / len(neighbors)
            avg_vy = sum(n.vy for n in neighbors) / len(neighbors)
            fx += 0.4 * (avg_vx - d.vx)
            fy += 0.4 * (avg_vy - d.vy)

        return fx, fy

    def _virtual_structure(self, d: Drone, cfg) -> Tuple[float, float]:
        k_p = 2.0; k_d = 1.0
        fx = k_p * (d.target_x - d.x) - k_d * d.vx
        fy = k_p * (d.target_y - d.y) - k_d * d.vy
        return fx, fy

    def _potential_field(self, d: Drone, neighbors: List[Drone], cfg) -> Tuple[float, float]:
        # Attractive to target
        dx = d.target_x - d.x; dy = d.target_y - d.y
        dist = math.hypot(dx, dy) + 1e-6
        fx = 2.5 * dx / (dist + 1.0)
        fy = 2.5 * dy / (dist + 1.0)
        # Repulsion from neighbors
        for n in neighbors:
            d2 = d.distance_to(n) + 0.1
            if d2 < cfg["sense_radius"]:
                strength = 3.0 / (d2 ** 2)
                fx += strength * (d.x - n.x) / d2
                fy += strength * (d.y - n.y) / d2
        return fx, fy

    def _goto(self, d: Drone, tx: float, ty: float, max_acc: float) -> Tuple[float, float]:
        dx = tx - d.x; dy = ty - d.y
        dist = math.hypot(dx, dy) + 1e-6
        k = min(2.0, dist / 10.0) * max_acc
        fx = k * dx / dist - 1.0 * d.vx
        fy = k * dy / dist - 1.0 * d.vy
        return fx, fy

    # ── Metrics ──

    def formation_error(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if not active: return 0.0
        errors = [d.distance_to_point(d.target_x, d.target_y) for d in active]
        return float(np.mean(errors))

    def spacing_error(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if len(active) < 2: return 0.0
        cfg = self._cfg()
        ideal = 8.0 * cfg["form_scale"]
        dists = []
        for i, a in enumerate(active):
            for b in active[i + 1:]:
                dists.append(a.distance_to(b))
        return float(abs(np.mean(dists) - ideal))

    def alignment_error(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if len(active) < 2: return 0.0
        headings = [d.heading for d in active]
        mean_h = np.mean(headings)
        return float(np.std([h - mean_h for h in headings]))

    def coverage_area(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if len(active) < 3: return 0.0
        xs = [d.x for d in active]; ys = [d.y for d in active]
        return (max(xs) - min(xs)) * (max(ys) - min(ys))

    def connectivity(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if len(active) < 2: return 1.0
        cfg = self._cfg()
        r = cfg["comm_radius"]
        edges = sum(
            1 for i, a in enumerate(active)
            for b in active[i + 1:] if a.distance_to(b) < r
        )
        max_edges = len(active) * (len(active) - 1) / 2
        return edges / max_edges if max_edges > 0 else 1.0

    def cohesion_score(self) -> float:
        active = [d for d in self.drones if not d.failed]
        if not active: return 0.0
        cx = np.mean([d.x for d in active])
        cy = np.mean([d.y for d in active])
        dists = [math.hypot(d.x - cx, d.y - cy) for d in active]
        return max(0.0, 100.0 - float(np.mean(dists)))

    def inject_failure(self):
        active = [d for d in self.drones if not d.failed and not d.is_leader]
        if active:
            rng = np.random.default_rng()
            victim = rng.choice(active)
            victim.failed = True
            self.event_log.append(f"⚠️ t={self.time:.1f}s  Drone #{victim.id} failed")

    def inject_obstacle(self):
        rng = np.random.default_rng()
        obs = Obstacle(
            x=float(rng.uniform(-50, 50)),
            y=float(rng.uniform(-50, 50)),
            radius=float(rng.uniform(4, 10)),
        )
        self.obstacles.append(obs)
        self.event_log.append(f"🚧 t={self.time:.1f}s  Obstacle added at ({obs.x:.0f},{obs.y:.0f})")

    def switch_formation(self):
        self._regenerate_targets()
        formation_name = st.session_state.get("formation", "Unknown")
        self.event_log.append(f"🔄 t={self.time:.1f}s  Formation → {formation_name}")


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "n_drones":      12,
        "control_mode":  ControlMode.VIRTUAL_STRUCTURE,
        "formation":     FormationType.CIRCLE,
        "comm_radius":   35.0,
        "sense_radius":  20.0,
        "max_speed":     8.0,
        "max_accel":     4.0,
        "wind_x":        0.0,
        "wind_y":        0.0,
        "noise_level":   0.0,
        "collision_r":   2.5,
        "safety_margin": 1.5,
        "show_trails":   True,
        "show_links":    True,
        "show_targets":  True,
        "form_cx":       0.0,
        "form_cy":       0.0,
        "form_scale":    1.0,
        "form_rotation": 0.0,
        "trans_speed":   1.0,
        "running":       False,
        "sim":           None,
        "step_count":    0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state["sim"] is None:
        st.session_state["sim"] = SwarmSimulation()

init_state()
sim: SwarmSimulation = st.session_state["sim"]


# ─────────────────────────────────────────────
# PLOTLY FIGURE BUILDER
# ─────────────────────────────────────────────
def build_figure(sim: SwarmSimulation) -> go.Figure:
    cfg = sim._cfg()
    fig = go.Figure()

    # Background grid
    fig.update_layout(
        plot_bgcolor="#fafbff",
        paper_bgcolor="#ffffff",
        xaxis=dict(range=[-MAP_RANGE, MAP_RANGE], showgrid=True, gridcolor="#e8ecf7",
                   zeroline=False, showticklabels=True, color="#94a3b8"),
        yaxis=dict(range=[-MAP_RANGE, MAP_RANGE], showgrid=True, gridcolor="#e8ecf7",
                   zeroline=False, showticklabels=True, color="#94a3b8", scaleanchor="x"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=620,
        showlegend=False,
        title=dict(
            text=f"<b>Drone Formation Control Lab</b>  ·  {cfg['control_mode']}  ·  {cfg['formation']}  ·  t = {sim.time:.1f}s",
            font=dict(size=14, color="#312e81"),
            x=0.5,
        ),
    )

    # ── Obstacles ──
    for obs in sim.obstacles:
        theta = np.linspace(0, 2 * np.pi, 40)
        ox = obs.x + obs.radius * np.cos(theta)
        oy = obs.y + obs.radius * np.sin(theta)
        fig.add_trace(go.Scatter(
            x=ox.tolist(), y=oy.tolist(),
            fill="toself", fillcolor="rgba(239,68,68,0.18)",
            line=dict(color="#ef4444", width=1.5),
            mode="lines", hoverinfo="skip",
        ))

    # ── Communication links ──
    if cfg["show_links"]:
        active = [d for d in sim.drones if not d.failed]
        for i, a in enumerate(active):
            for b in active[i + 1:]:
                if a.distance_to(b) < cfg["comm_radius"]:
                    fig.add_trace(go.Scatter(
                        x=[a.x, b.x, None], y=[a.y, b.y, None],
                        mode="lines",
                        line=dict(color="rgba(99,102,241,0.18)", width=1),
                        hoverinfo="skip",
                    ))

    # ── Formation target points ──
    if cfg["show_targets"]:
        active = [d for d in sim.drones if not d.failed]
        tx = [d.target_x for d in active]
        ty = [d.target_y for d in active]
        fig.add_trace(go.Scatter(
            x=tx, y=ty,
            mode="markers",
            marker=dict(size=8, color="rgba(99,102,241,0.3)",
                        symbol="x", line=dict(color="#6366f1", width=1)),
            hoverinfo="skip",
        ))

    # ── Trails ──
    if cfg["show_trails"]:
        for d in sim.drones:
            if not d.failed and len(d.trail_x) > 1:
                n_t = len(d.trail_x)
                alphas = [f"rgba(99,102,241,{0.05 + 0.25 * i / n_t:.2f})" for i in range(n_t)]
                fig.add_trace(go.Scatter(
                    x=d.trail_x, y=d.trail_y,
                    mode="lines",
                    line=dict(color="rgba(99,102,241,0.2)", width=1),
                    hoverinfo="skip",
                ))

    # ── Drones ──
    for d in sim.drones:
        if d.failed:
            color = "#9ca3af"
            symbol = "circle"
            size = 8
        elif d.is_leader:
            color = "#f59e0b"
            symbol = "triangle-up"
            size = 16
        else:
            err = d.distance_to_point(d.target_x, d.target_y)
            t = min(err / 20.0, 1.0)
            # Interpolate: low error = indigo, high error = rose
            r = int(99 + t * (244 - 99))
            g = int(102 + t * (63 - 102))
            b_c = int(241 + t * (63 - 241))
            color = f"rgb({r},{g},{b_c})"
            symbol = "triangle-up"
            size = 13

        # Arrow marker rotated by heading
        angle_deg = math.degrees(d.heading) - 90

        label = (
            f"Drone #{d.id}"
            + (" [LEADER]" if d.is_leader else "")
            + (" [FAILED]" if d.failed else "")
            + f"<br>Pos: ({d.x:.1f}, {d.y:.1f})"
            + f"<br>Speed: {math.hypot(d.vx, d.vy):.1f}"
            + f"<br>Error: {d.distance_to_point(d.target_x, d.target_y):.1f}"
            + f"<br>Battery: {d.battery:.0f}%"
        )

        fig.add_trace(go.Scatter(
            x=[d.x], y=[d.y],
            mode="markers+text",
            marker=dict(
                size=size,
                color=color,
                symbol=symbol,
                angle=angle_deg,
                line=dict(color="white", width=1.5),
            ),
            text=[f"  {d.id}"],
            textposition="middle right",
            textfont=dict(size=9, color="#475569"),
            hovertemplate=label + "<extra></extra>",
        ))

    return fig


# ─────────────────────────────────────────────
# SIDEBAR — CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Swarm Configuration")
    st.markdown("---")

    st.markdown("### 🚁 Swarm")
    st.session_state["n_drones"] = st.slider("Number of Drones", 4, 40, st.session_state["n_drones"])

    st.markdown("### 🧠 Control Mode")
    mode_names = [m.value for m in ControlMode]
    mode_idx = mode_names.index(st.session_state["control_mode"]) if st.session_state["control_mode"] in mode_names else 0
    sel_mode = st.selectbox("Mode", mode_names, index=mode_idx, key="sel_mode")
    st.session_state["control_mode"] = sel_mode

    with st.expander("ℹ️ Mode description"):
        st.caption(CONTROL_DESCRIPTIONS.get(sel_mode, ""))

    st.markdown("### 🔷 Formation")
    form_names = [f.value for f in FormationType if f != FormationType.CUSTOM]
    form_idx = form_names.index(st.session_state["formation"]) if st.session_state["formation"] in form_names else 0
    sel_form = st.selectbox("Formation", form_names, index=form_idx, key="sel_form")
    st.session_state["formation"] = sel_form

    st.markdown("### 📐 Formation Transform")
    st.session_state["form_cx"]       = st.slider("Center X", -60.0, 60.0, float(st.session_state["form_cx"]))
    st.session_state["form_cy"]       = st.slider("Center Y", -60.0, 60.0, float(st.session_state["form_cy"]))
    st.session_state["form_scale"]    = st.slider("Scale", 0.3, 3.0, float(st.session_state["form_scale"]), 0.1)
    st.session_state["form_rotation"] = st.slider("Rotation (°)", 0, 360, int(st.session_state["form_rotation"]))

    st.markdown("### 📡 Communication")
    st.session_state["comm_radius"]  = st.slider("Comm. Radius", 10.0, 80.0, float(st.session_state["comm_radius"]))
    st.session_state["sense_radius"] = st.slider("Sensing Radius", 5.0, 50.0, float(st.session_state["sense_radius"]))

    st.markdown("### 🏎️ Dynamics")
    st.session_state["max_speed"]    = st.slider("Max Speed", 1.0, 25.0, float(st.session_state["max_speed"]))
    st.session_state["max_accel"]    = st.slider("Max Accel.", 1.0, 15.0, float(st.session_state["max_accel"]))
    st.session_state["trans_speed"]  = st.slider("Transition Speed", 0.2, 2.0, float(st.session_state["trans_speed"]), 0.1)

    st.markdown("### 💨 Disturbances")
    st.session_state["wind_x"]      = st.slider("Wind X", -5.0, 5.0, float(st.session_state["wind_x"]), 0.5)
    st.session_state["wind_y"]      = st.slider("Wind Y", -5.0, 5.0, float(st.session_state["wind_y"]), 0.5)
    st.session_state["noise_level"] = st.slider("Motion Noise", 0.0, 3.0, float(st.session_state["noise_level"]), 0.1)

    st.markdown("### 🛡️ Collision")
    st.session_state["collision_r"]    = st.slider("Collision Radius", 1.0, 6.0, float(st.session_state["collision_r"]), 0.5)
    st.session_state["safety_margin"]  = st.slider("Safety Margin", 0.5, 5.0, float(st.session_state["safety_margin"]), 0.5)

    st.markdown("### 🎨 Visualization")
    st.session_state["show_trails"]  = st.toggle("Show Trails", st.session_state["show_trails"])
    st.session_state["show_links"]   = st.toggle("Show Comm. Links", st.session_state["show_links"])
    st.session_state["show_targets"] = st.toggle("Show Target Points", st.session_state["show_targets"])


# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; gap:12px; margin-bottom:4px;'>
  <span style='font-size:2rem;'>🚁</span>
  <div>
    <h1 style='margin:0; font-size:1.7rem;'>Drone Formation Control Lab</h1>
    <p style='margin:0; color:#6366f1; font-size:0.9rem; font-weight:500;'>
      Swarm Intelligence · Decentralized Control · Real-Time Simulation
    </p>
  </div>
</div>
<hr style='margin:8px 0 16px 0;'>
""", unsafe_allow_html=True)

# ── Action buttons ──
b_cols = st.columns(8)
with b_cols[0]:
    if st.button("▶ Start" if not st.session_state["running"] else "⏸ Pause"):
        st.session_state["running"] = not st.session_state["running"]
with b_cols[1]:
    if st.button("↺ Reset"):
        st.session_state["sim"] = SwarmSimulation()
        sim = st.session_state["sim"]
        st.session_state["running"] = False
with b_cols[2]:
    if st.button("🎲 Randomize"):
        st.session_state["sim"] = SwarmSimulation()
        sim = st.session_state["sim"]
with b_cols[3]:
    if st.button("🔄 Switch Formation"):
        sim.switch_formation()
with b_cols[4]:
    if st.button("⚠️ Fail Drone"):
        sim.inject_failure()
with b_cols[5]:
    if st.button("🚧 Add Obstacle"):
        sim.inject_obstacle()
with b_cols[6]:
    if st.button("💨 Gust"):
        st.session_state["wind_x"] = float(np.random.uniform(-4, 4))
        st.session_state["wind_y"] = float(np.random.uniform(-4, 4))
with b_cols[7]:
    if st.button("🔕 Clear Wind"):
        st.session_state["wind_x"] = 0.0
        st.session_state["wind_y"] = 0.0

# ── Main canvas + metrics ──
main_col, metric_col = st.columns([3, 1])

with main_col:
    sim_placeholder = st.empty()

with metric_col:
    st.markdown("### 📊 Live Metrics")
    m1 = st.empty()
    m2 = st.empty()
    m3 = st.empty()
    m4 = st.empty()
    m5 = st.empty()
    m6 = st.empty()
    m7 = st.empty()

    st.markdown("### 📈 Convergence")
    chart_placeholder = st.empty()

    st.markdown("### 📋 Event Log")
    log_placeholder = st.empty()

# ─────────────────────────────────────────────
# SIMULATION LOOP
# ─────────────────────────────────────────────
MAX_STEPS   = 300   # steps per Streamlit run
STEPS_PER_FRAME = 3

error_history: List[float] = st.session_state.get("error_history", [])

if st.session_state["running"]:
    for _ in range(STEPS_PER_FRAME):
        sim.step()
    st.session_state["step_count"] += STEPS_PER_FRAME

    err = sim.formation_error()
    error_history.append(err)
    if len(error_history) > 150:
        error_history.pop(0)
    st.session_state["error_history"] = error_history

# Always render current state
with sim_placeholder:
    fig = build_figure(sim)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Metrics
with m1: st.metric("Formation Error", f"{sim.formation_error():.2f} u")
with m2: st.metric("Spacing Error",   f"{sim.spacing_error():.2f} u")
with m3: st.metric("Alignment Error", f"{sim.alignment_error():.3f} rad")
with m4: st.metric("Coverage Area",   f"{sim.coverage_area():.0f} u²")
with m5: st.metric("Connectivity",    f"{sim.connectivity() * 100:.0f}%")
with m6: st.metric("Cohesion Score",  f"{sim.cohesion_score():.1f}")
with m7: st.metric("Collisions",      str(sim.collisions))

# Convergence chart
if error_history:
    conv_fig = go.Figure()
    conv_fig.add_trace(go.Scatter(
        y=error_history, mode="lines",
        line=dict(color="#6366f1", width=2),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.1)",
    ))
    conv_fig.update_layout(
        height=180,
        margin=dict(l=5, r=5, t=5, b=5),
        plot_bgcolor="#fafbff", paper_bgcolor="#ffffff",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e8ecf7", color="#94a3b8", tickfont=dict(size=9)),
    )
    chart_placeholder.plotly_chart(conv_fig, use_container_width=True, config={"displayModeBar": False})

# Event log
if sim.event_log:
    log_placeholder.markdown(
        "<div style='font-size:0.78rem; color:#475569; max-height:160px; overflow-y:auto;'>"
        + "<br>".join(reversed(sim.event_log[-12:]))
        + "</div>",
        unsafe_allow_html=True,
    )

# Auto-rerun while running
if st.session_state["running"]:
    time.sleep(0.05)
    st.rerun()


# ─────────────────────────────────────────────
# BOTTOM TABS — Presets, Export, About
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🎯 Preset Scenarios", "📤 Export", "📖 About"])

with tab1:
    st.markdown("**Load a pre-configured scenario to explore specific behaviors:**")
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        st.markdown("**🏙️ Urban Navigation**")
        st.caption("Tight wedge formation, high obstacle density, potential field avoidance.")
        if st.button("Load Urban"):
            st.session_state.update({
                "formation": FormationType.WEDGE, "control_mode": ControlMode.POTENTIAL_FIELD,
                "n_drones": 8, "max_speed": 6.0, "noise_level": 0.5,
            })
            st.session_state["sim"] = SwarmSimulation()
            for _ in range(3): st.session_state["sim"].inject_obstacle()
            st.rerun()
    with pc2:
        st.markdown("**🌾 Agricultural Scan**")
        st.caption("Grid formation, wide spacing, virtual structure control.")
        if st.button("Load Agricultural"):
            st.session_state.update({
                "formation": FormationType.GRID, "control_mode": ControlMode.VIRTUAL_STRUCTURE,
                "n_drones": 16, "max_speed": 5.0, "form_scale": 1.5,
            })
            st.session_state["sim"] = SwarmSimulation()
            st.rerun()
    with pc3:
        st.markdown("**🔍 Search & Rescue**")
        st.caption("Expanding wave, behavior-based, wide coverage area.")
        if st.button("Load Search & Rescue"):
            st.session_state.update({
                "formation": FormationType.WAVE, "control_mode": ControlMode.BEHAVIOR_BASED,
                "n_drones": 20, "max_speed": 7.0, "comm_radius": 45.0,
            })
            st.session_state["sim"] = SwarmSimulation()
            st.rerun()
    with pc4:
        st.markdown("**💥 Failure Recovery**")
        st.caption("Circle, consensus control, multiple drone failures injected.")
        if st.button("Load Failure Test"):
            st.session_state.update({
                "formation": FormationType.CIRCLE, "control_mode": ControlMode.CONSENSUS,
                "n_drones": 14, "max_speed": 6.0,
            })
            st.session_state["sim"] = SwarmSimulation()
            for _ in range(4): st.session_state["sim"].inject_failure()
            st.rerun()

with tab2:
    st.markdown("**Export current simulation state as JSON:**")
    if st.button("📄 Generate Export"):
        export = {
            "timestamp": sim.time,
            "control_mode": sim._cfg()["control_mode"],
            "formation": sim._cfg()["formation"],
            "n_drones": len(sim.drones),
            "metrics": {
                "formation_error": sim.formation_error(),
                "spacing_error":   sim.spacing_error(),
                "alignment_error": sim.alignment_error(),
                "coverage_area":   sim.coverage_area(),
                "connectivity":    sim.connectivity(),
                "cohesion_score":  sim.cohesion_score(),
                "collisions":      sim.collisions,
            },
            "drones": [
                {"id": d.id, "x": round(d.x, 2), "y": round(d.y, 2),
                 "vx": round(d.vx, 2), "vy": round(d.vy, 2),
                 "heading": round(d.heading, 3),
                 "failed": d.failed, "battery": round(d.battery, 1)}
                for d in sim.drones
            ],
            "obstacles": [{"x": o.x, "y": o.y, "radius": o.radius} for o in sim.obstacles],
            "events": sim.event_log,
        }
        st.json(export)
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(export, indent=2),
            file_name="swarm_scenario.json",
            mime="application/json",
        )

with tab3:
    st.markdown("""
### About This Simulator

**Drone Formation Control Lab** is a research-grade interactive simulation of multi-agent swarm systems.

#### Control Strategies
| Mode | Description |
|---|---|
| **Leader-Follower** | One designated leader; others maintain relative offsets. Simple hierarchy but single point of failure. |
| **Consensus-Based** | Agents average neighbor states iteratively. Convergent and robust; requires network connectivity. |
| **Behavior-Based** | Emergent formation from blended local behaviors: separation, cohesion, alignment, and goal-seeking. |
| **Virtual Structure** | Formation treated as rigid body; each drone tracks a slot via PD controller. High fidelity. |
| **Potential Field** | Goal positions attract; drones and obstacles repel via inverse-square fields. Physically intuitive. |

#### Formation Logic
Formations are generated as sets of target points relative to a configurable center. 
Assignment of drones to slots uses a greedy nearest-neighbor approach to minimize total travel distance.
Transitions happen by recomputing targets and letting the control law drive drones to new slots.

#### Physics
- Discrete-time integration at 50 ms timesteps
- Acceleration-limited velocity control
- Boundary and obstacle repulsion fields
- Inter-agent repulsion for collision avoidance
- Wind and Gaussian motion noise injection

#### Stack
- **Streamlit** — UI and reactive state management  
- **Plotly** — Interactive canvas rendering  
- **NumPy** — Numerical simulation  

#### Future Extensions
- 3D simulation with altitude control  
- Real drone telemetry ingestion via MAVLink  
- Reinforcement learning formation policies  
- Multi-stage mission planner  
- Hardware-in-the-loop testing  
    """)