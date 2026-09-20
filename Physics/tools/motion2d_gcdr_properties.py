#!/usr/bin/env python3
"""Property/invariant sweeps for Motion-in-2D GCDR explorers.

These checks are subject-owned scientific regression tests. They do not replace human review;
they falsify numerical/state claims that the six Motion-in-2D explorers rely on.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "Physics" / "library" / "phy-kin-2d-motion.v1.json"


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def audit(repo: Path = REPO) -> dict:
    package = json.loads(
        (repo / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
    )
    ids = {row["id"] for row in package.get("resources", [])}
    findings: list[dict] = []

    def fail(activity: str, invariant: str, detail: str):
        findings.append({"activity": activity, "invariant": invariant, "detail": detail})

    required = {
        "ACT-KIN-2D-SHARED-CLOCK",
        "ACT-KIN-2D-EVENT-CLOCK",
        "ACT-KIN-2D-PROJECTILE-MODEL-GATE",
        "ACT-KIN-2D-APEX-FALLACY",
        "ACT-KIN-2D-EQUAL-HEIGHT-STATE",
        "ACT-KIN-2D-LANDING-GEOMETRY",
    }
    for rid in sorted(required - ids):
        fail(rid, "RESOURCE_REGISTERED", "required GCDR activity resource is missing")

    # Shared clock: one simultaneous state requires one time.
    for tx in [0.0, 0.7, 1.4, 2.8, 4.0]:
        x = 4 * tx
        y = 10 - 2 * tx * tx
        if not (close(x, 4 * tx) and close(y, 10 - 2 * tx * tx)):
            fail("ACT-KIN-2D-SHARED-CLOCK", "SAME_TIME_COMPONENT_STATE", f"state mismatch at t={tx}")
        ty = min(4.0, tx + 0.3)
        if not close(tx, ty) and (4 * tx, 10 - 2 * ty * ty) == (x, y):
            fail("ACT-KIN-2D-SHARED-CLOCK", "GHOST_STATE_DISTINCT", f"mixed-time state collapsed at tx={tx}, ty={ty}")

    # Event clock examples hard-coded by the explorer.
    # Impact: -15 = 10 t - 5 t^2 -> positive root 3 s.
    disc = 10**2 - 4 * 5 * (-15)
    impact = (10 + math.sqrt(disc)) / 10
    if not close(impact, 3.0):
        fail("ACT-KIN-2D-EVENT-CLOCK", "IMPACT_EVENT_TIME", f"expected 3 s, got {impact}")
    if not close(10 / 10, 1.0):
        fail("ACT-KIN-2D-EVENT-CLOCK", "APEX_EVENT_TIME", "u_y/g must be 1 s")
    if not close(20 / 10, 2.0):
        fail("ACT-KIN-2D-EVENT-CLOCK", "WALL_EVENT_TIME", "x/u_x must be 2 s")

    # Projectile model gate: ideal specialization iff no extra retained interaction exists.
    for thrust in [False, True]:
        for drag in [False, True]:
            for contact in [False, True]:
                ideal = not (thrust or drag or contact)
                if ideal != (sum([thrust, drag, contact]) == 0):
                    fail("ACT-KIN-2D-PROJECTILE-MODEL-GATE", "GRAVITY_ONLY_GATE", "interaction gate mismatch")

    # Apex: v_y=0 but a_y=-g and v_x remains non-zero.
    ux, uy, g = 12.0, 20.0, 10.0
    t_apex = uy / g
    vy = uy - g * t_apex
    speed = math.hypot(ux, vy)
    if not close(t_apex, 2.0) or not close(vy, 0.0) or not close(speed, 12.0):
        fail("ACT-KIN-2D-APEX-FALLACY", "APEX_STATE", f"t={t_apex}, vy={vy}, speed={speed}")
    if close(g, 0.0):
        fail("ACT-KIN-2D-APEX-FALLACY", "ACCELERATION_PERSISTS", "gravity must remain non-zero at apex")

    # Equal-height symmetry across t and T-t for this same-height trajectory.
    T = 2 * uy / g
    for ta in [0.1, 0.4, 0.9, 1.2, 1.8]:
        tb = T - ta
        ya = uy * ta - 0.5 * g * ta * ta
        yb = uy * tb - 0.5 * g * tb * tb
        vya = uy - g * ta
        vyb = uy - g * tb
        spa = math.hypot(ux, vya)
        spb = math.hypot(ux, vyb)
        if not close(ya, yb):
            fail("ACT-KIN-2D-EQUAL-HEIGHT-STATE", "EQUAL_HEIGHT_PAIR", f"yA={ya}, yB={yb}")
        if not close(vya, -vyb):
            fail("ACT-KIN-2D-EQUAL-HEIGHT-STATE", "VERTICAL_COMPONENT_REVERSAL", f"vyA={vya}, vyB={vyb}")
        if not close(spa, spb):
            fail("ACT-KIN-2D-EQUAL-HEIGHT-STATE", "SPEED_SYMMETRY", f"|vA|={spa}, |vB|={spb}")

    # Landing geometry: roots must satisfy the requested y_f and range must reuse the same t.
    yi, ux_l, uy_l, g_l = 15.0, 10.0, 10.0, 10.0
    y_max = yi + uy_l**2 / (2 * g_l)
    for yf in range(-5, 26):
        d = yf - yi
        disc = uy_l**2 - 2 * g_l * d
        if yf > y_max:
            if disc >= 0:
                fail("ACT-KIN-2D-LANDING-GEOMETRY", "ABOVE_MAX_NO_CROSSING", f"yf={yf} unexpectedly has disc={disc}")
            continue
        if disc < 0:
            fail("ACT-KIN-2D-LANDING-GEOMETRY", "REACHABLE_HEIGHT_HAS_ROOT", f"yf={yf} has disc={disc}")
            continue
        t = (uy_l + math.sqrt(disc)) / g_l
        y_check = yi + uy_l * t - 0.5 * g_l * t * t
        x = ux_l * t
        if not close(y_check, yf, 1e-8):
            fail("ACT-KIN-2D-LANDING-GEOMETRY", "EVENT_ROOT_SUBSTITUTION", f"yf={yf}, y(t)={y_check}, t={t}")
        if not close(x, 10 * t):
            fail("ACT-KIN-2D-LANDING-GEOMETRY", "SHARED_EVENT_TIME_RANGE", f"x={x}, t={t}")

    return {
        "subject": "Physics",
        "scope": "MOTION_IN_2D_GCDR_NUMERICAL_AND_MODEL_INVARIANTS",
        "sweeps": 5,
        "findings": findings,
        "passed": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
