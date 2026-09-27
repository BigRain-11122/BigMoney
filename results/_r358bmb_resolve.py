# -*- coding: utf-8 -*-
"""r358 bm-b push-storm #3 UU resolver for 7 non-lane faces (r185 receipt law).

Context: r357 push rejected -> pull --rebase onto bm-c r129 addendum (26c07ea1),
14 UU faces. 7 lane faces closed via scripts/merge_lane_views.py resolve
(r377 canonical). This script closes the remaining 7 per skill recipes:
  - docs/daily_report/REPORT-2026-09-28.{json,md} : snapshot twins, take-new by
    'generated' ts, BOTH twins same side (r98/r99/r100)
  - results/dashboard_status.{js,json}           : js-wrapper + json twin,
    whole-byte take-side by embedded ts (R209: never json.dumps the .js)
  - results/fundamental_b_layer_filter.json      : take-new by 'updated' (R216)
  - results/scorecard_v1.json                    : hardened deep-ts probe (r100/R350)
  - results/strategy_scorecard.json              : hardened deep-ts probe (r100/R350)

Laws applied: stage read via subprocess bytes (r209 PS-UTF16 law); probe on
STAGED blobs not working tree (r100); key normalize strip '_','-'+lower before
prefix match (r100); value must be ts-shaped ^20\\d{2}- ; wall-clock probes
require time-of-day in value, date-only must not feed wall-clock max (R350);
NO key-exclusion lists (R350); parse-verify before write (r185); same-second
tie -> replay side :3: (newer commit by construction, r140 family).
"""
import json, re, subprocess, sys

TS_SHAPE = re.compile(r"^20\d{2}-")
WALL_CLOCK = re.compile(r"[T ]\d{2}:\d{2}")
PREFIXES = ("asof", "updated", "generated", "statets", "lastts", "cutoffts")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "cat-file", "-p", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {path}:{stage}: {r.stderr[:200]!r}")
    return r.stdout


def probe(doc):
    """Hardened deep-ts probe (r100/R350). Returns (wall_clock_max, date_only_max, hits)."""
    wall, date, hits = "", "", []

    def walk(node, path):
        nonlocal wall, date
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + [k])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + [i])
        else:
            if not isinstance(node, str) or not TS_SHAPE.match(node):
                return
            nk = re.sub(r"[_\-]", "", str(path[-1])).lower() if path else ""
            if not any(nk.startswith(p) for p in PREFIXES):
                return
            hits.append((".".join(map(str, path[-2:])), node))
            if WALL_CLOCK.search(node):
                if node > wall:
                    wall = node
            else:
                if node > date:
                    date = node

    walk(doc, [])
    return wall, date, hits


def load_side(path, stage):
    raw = stage_bytes(path, stage)
    if path.endswith(".md"):
        return None, raw  # markdown twin: no json parse, byte-take only
    if path.endswith(".js"):
        m = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?", raw, re.S)
        if not m:
            raise SystemExit(f"no DASH_DATA wrapper in {path}:{stage}")
        return json.loads(m.group(1).decode("utf-8")), raw
    return json.loads(raw.decode("utf-8")), raw


def pick_side(wall2, wall3, date2, date3):
    """Return 2 or 3. Wall-clock wins over date-only (R350); tie -> :3: replay."""
    if wall2 and wall3:
        return 2 if wall2 > wall3 else 3
    if wall2 and not wall3 and not date3:
        return 2
    if wall3 and not wall2 and not date2:
        return 3
    if date2 and date3:
        return 2 if date2 > date3 else 3
    return 3  # tie / missing probes -> replay side (newer commit)


def take_new_single(path, label):
    d2, raw2 = load_side(path, 2)
    d3, raw3 = load_side(path, 3)
    w2, x2, h2 = probe(d2)
    w3, x3, h3 = probe(d3)
    side = pick_side(w2, w3, x2, x3)
    picked = {2: (w2 or x2, raw2), 3: (w3 or x3, raw3)}[side]
    json.loads(picked[1].decode("utf-8") if path.endswith((".json", ".js"))
               else "{}")  # parse-verify (json faces only here)
    with open(path, "wb") as f:
        f.write(picked[1])
    print(f"[{label}] side=:{side}: ts={picked[0] or 'TIE->:3:'} "
          f"probe2={h2[:3]} probe3={h3[:3]} wrote={len(picked[1])}B parse-ok")
    return side


def twins_same_side(paths, label):
    """Whole-byte take of ONE side applied to all twin files (probe on json twin)."""
    json_idx = next(i for i, p in enumerate(paths) if p.endswith((".json", ".js")))
    jp = paths[json_idx]
    d2, _ = load_side(jp, 2)
    d3, _ = load_side(jp, 3)
    w2, x2, _ = probe(d2)
    w3, x3, _ = probe(d3)
    side = pick_side(w2, w3, x2, x3)
    for p in paths:
        raw = stage_bytes(p, side)
        if p.endswith((".json", ".js")):
            load_side(p, side)  # parse-verify
        with open(p, "wb") as f:
            f.write(raw)
        print(f"[{label}] side=:{side}: wrote {p} ({len(raw)}B)")
    print(f"[{label}] probe evidence ({jp}): origin(:2:)={w2 or x2} "
          f"replay(:3:)={w3 or x3} -> :{side}:")
    return side


if __name__ == "__main__":
    twins_same_side(["docs/daily_report/REPORT-2026-09-28.json",
                     "docs/daily_report/REPORT-2026-09-28.md"], "daily-report")
    twins_same_side(["results/dashboard_status.json",
                     "results/dashboard_status.js"], "dashboard")
    take_new_single("results/fundamental_b_layer_filter.json", "blf")
    take_new_single("results/scorecard_v1.json", "scorecard-v1")
    take_new_single("results/strategy_scorecard.json", "scorecard-strategy")
    print("receipt: r358 bm-b push-storm #3, 7 non-lane faces closed, "
          "whole-byte take-new, parse-verified, zero hand-union")
