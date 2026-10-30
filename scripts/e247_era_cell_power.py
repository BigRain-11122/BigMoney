"""E247 - what would it take for the era cells of the star-direction matrix to decide?

The published E246 face (results/state_tilt/STARDIR-<cutoff>.json) counts six cells:
one headline, one "pre-2020" window, three era slices and one early neighbour slice.
Four of the six print ``unresolved_matrix_too_wide``: their median confidence
half-width sits between 0.42 and 0.51 against a frozen 0.30 bound.

The obvious next sentence is "collect more data". This study refuses to say that
without a number, because for a calendar slice the second sentence is "the slice
is over and the sessions will never arrive".

Design notes
------------
* Everything is derived from the published face; no re-estimation, no network.
* A CI half-width shrinks like ``h(n) ~ h0 * sqrt(n0/n)`` for a fixed design, so
  the session count that reaches a target half-width is ``n0 * (h0/target)**2``.
  That is a *lower bound on sessions*, not on calendar time: sessions inside a
  closed window do not exist, which is exactly the point the table makes.
* A cell's window is treated as closed when its ``window_inclusive`` upper end is
  a date (or when it is a historical "pre-2020"/early slice that the face pins).
  Only the last era cell, whose upper end is open, can grow.
* The "minimum detectable slope at 80% power" is ``z * SE`` with ``SE = h/1.96``
  and ``z = 2.802`` (two-sided 5%, 80% power) - the same formula used in E162.

Run:  python scripts/e247_era_cell_power.py run [--face <path>]
      python scripts/e247_era_cell_power.py selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE_DEFAULT = os.path.join(ROOT, "results", "state_tilt", "STARDIR-2026-10-29.json")
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")

Z_80 = 2.802  # two-sided 5%, 80% power
TARGETS = (0.30, 0.20, 0.15)  # half-width goals; 0.30 is the frozen bound


def _load_face(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _window_closed(cell: dict) -> bool:
    win = cell.get("window_inclusive") or [None, None]
    if cell.get("kind") == "headline":
        return False
    return win[1] is not None


def sessions_needed(n: int, halfwidth: float, target: float) -> int | None:
    """Sessions required to bring ``halfwidth`` down to ``target``."""
    if not n or not halfwidth or halfwidth <= 0:
        return None
    if halfwidth <= target:
        return 0
    return int(math.ceil(n * (halfwidth / target) ** 2))


def minimum_detectable(halfwidth: float) -> float:
    """Smallest |slope| distinguishable from zero at 80% power."""
    return Z_80 * (halfwidth / 1.96)


def build(face: dict) -> dict:
    frozen = face.get("frozen_spec") or {}
    bound = float(frozen.get("resolution_max_halfwidth", 0.30))
    cells = []
    for cell in face["cells"]:
        n = int(cell.get("sessions") or 0)
        h = cell.get("resolution_median_halfwidth")
        closed = _window_closed(cell)
        need = {f"{t:.2f}": sessions_needed(n, h, t) for t in TARGETS}
        row = {
            "label": cell["label"],
            "kind": cell.get("kind"),
            "sessions": n,
            "halfwidth": h,
            "frozen_bound": bound,
            "decided_now": bool(h is not None and h <= bound),
            "window_closed": closed,
            "sessions_for": need,
            "sessions_short": None,
            "min_detectable_slope_now": None if h is None else minimum_detectable(h),
            "min_detectable_slope_at_bound": minimum_detectable(bound),
            "verdict": None,
        }
        for t in TARGETS:
            if abs(t - bound) < 1e-12:
                n_target = need[f"{t:.2f}"]
        if row["decided_now"]:
            row["verdict"] = "decided_at_published_bound"
        else:
            n_bound = need[f"{bound:.2f}"]
            row["sessions_short"] = None if n_bound is None else max(0, n_bound - n)
            row["verdict"] = (
                "unreachable_window_closed" if closed else "open_but_needs_sessions"
            )
        cells.append(row)

    open_short = [c["sessions_short"] for c in cells if c["verdict"] == "open_but_needs_sessions"]
    closed_unresolved = [c["label"] for c in cells if c["verdict"] == "unreachable_window_closed"]
    decided = [c["label"] for c in cells if c["verdict"] == "decided_at_published_bound"]

    if not closed_unresolved:
        headline = "only_session_count_stands_between_here_and_a_verdict"
    elif not open_short:
        headline = "the_unresolved_cells_are_closed_windows"
    else:
        headline = "some_unresolved_cells_are_closed_windows"

    return {
        "study": "E247",
        "title": "What it would take for the era cells of the star-direction matrix to decide",
        "evidence_cutoff": face.get("evidence_cutoff"),
        "source_face": os.path.relpath(FACE_DEFAULT, ROOT).replace("\\", "/")
        if face.get("_source_path") is None
        else face["_source_path"],
        "formula": {
            "sessions_needed": "ceil(n0 * (h0/target)**2)",
            "minimum_detectable_slope": f"{Z_80} * (halfwidth / 1.96)",
            "power": {"z": Z_80, "two_sided_alpha": 0.05, "power": 0.80},
            "targets": list(TARGETS),
            "frozen_bound": bound,
        },
        "cells": cells,
        "summary": {
            "verdict": headline,
            "decided": decided,
            "unresolved_open": [
                c["label"] for c in cells if c["verdict"] == "open_but_needs_sessions"
            ],
            "unresolved_closed": closed_unresolved,
            "largest_session_shortfall": max(open_short) if open_short else None,
            "honest_note": (
                "Sessions, not days: a closed calendar slice cannot be extended, so an "
                "'unreachable_window_closed' cell needs a different design (a longer "
                "window or a different star), never more patience."
            ),
        },
    }


def _selftest() -> int:
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # pure functions
    leg("needs_zero_when_already_inside", sessions_needed(100, 0.20, 0.30) == 0)
    leg("quadruple_for_halving", sessions_needed(100, 0.40, 0.20) == 400)
    leg("monotone_in_target", sessions_needed(100, 0.40, 0.30) < sessions_needed(100, 0.40, 0.15))
    leg("none_on_missing_halfwidth", sessions_needed(0, 0.0, 0.30) is None)
    leg("mde_matches_hand_calc", abs(minimum_detectable(0.30) - Z_80 * 0.30 / 1.96) < 1e-12)

    # synthetic face: one decided, one open, one closed
    face = {
        "evidence_cutoff": "2026-01-01",
        "frozen_spec": {"resolution_max_halfwidth": 0.30},
        "cells": [
            {
                "label": "ok",
                "kind": "headline",
                "sessions": 1000,
                "resolution_median_halfwidth": 0.20,
                "window_inclusive": [None, None],
            },
            {
                "label": "open",
                "kind": "era",
                "sessions": 400,
                "resolution_median_halfwidth": 0.45,
                "window_inclusive": ["2025-01-01", None],
            },
            {
                "label": "closed",
                "kind": "era",
                "sessions": 400,
                "resolution_median_halfwidth": 0.45,
                "window_inclusive": ["2020-01-01", "2022-12-31"],
            },
        ],
    }
    out = build(face)
    by = {c["label"]: c for c in out["cells"]}
    leg("decided_reads_decided", by["ok"]["verdict"] == "decided_at_published_bound")
    leg("open_needs_sessions", by["open"]["verdict"] == "open_but_needs_sessions")
    leg("closed_is_unreachable", by["closed"]["verdict"] == "unreachable_window_closed")
    leg("shortfall_math", by["open"]["sessions_short"] == int(math.ceil(400 * (0.45 / 0.30) ** 2)) - 400)
    leg("closed_shortfall_not_claimed", by["closed"]["sessions_short"] is not None)
    leg("headline_flags_closed", out["summary"]["verdict"] == "some_unresolved_cells_are_closed_windows")
    leg("cutoff_carried", out["evidence_cutoff"] == "2026-01-01")
    leg("deterministic", json.dumps(build(face), sort_keys=True) == json.dumps(out, sort_keys=True))

    bad = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"selftest {len(legs) - len(bad)}/{len(legs)}")
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--face", default=FACE_DEFAULT)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()

    face = _load_face(args.face)
    face["_source_path"] = os.path.relpath(args.face, ROOT).replace("\\", "/")
    out = build(face)
    cutoff = (out.get("evidence_cutoff") or "unknown").replace("-", "")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"ERAPOWER-{cutoff}.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    s = out["summary"]
    print(json.dumps({
        "face": path,
        "verdict": s["verdict"],
        "decided": s["decided"],
        "unresolved_open": s["unresolved_open"],
        "unresolved_closed": s["unresolved_closed"],
        "largest_session_shortfall": s["largest_session_shortfall"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())