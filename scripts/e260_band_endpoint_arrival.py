#!/usr/bin/env python3
"""E260 -- at how many draws does a window band endpoint stop moving?

E259 published 52 of 640 per-seed draw multipliers reading EXACTLY 1.0. A multiplier of one is
not a rounding accident: the prefix-nested band endpoint cannot move again once the draw that set
it has already arrived inside the base prefix. That turns "how many draws" from a prose worry into
a per-window measurable, and this face measures it -- off the edge tables E259 already published,
with no new draws and no new estimation:

    for every window and leg, the first draw count at which each seed's own band endpoint is
    ATTAINED (equal to that same seed's endpoint at the top of the grid), its distribution, and
    whether the draw count the family actually publishes sits below it.

The answer is one number per window: the arrival count. If the published base count is below it,
the band a reader sees was read off a stream that had not finished moving, and the face says by
how many draws and how much of the seed population is still moving.

Three pins, inherited unchanged from E259/E258:

  1. THE WINDOW is the published cell's own first/last dates.
  2. THE GRID is E259's draw grid, and 1920 is its top -- arrival is measured against that, never
     against an idealised infinite stream.
  3. PREFIX NESTING is preserved: a seed's series is read off one stream, so a smaller count is
     literally a prefix of the larger one. Arrival is therefore the first count at which the seed
     stops moving, not a coincidence between two independent samples.

Cross-check, published as a pin rather than a claim: re-deriving arrival per published row and
counting the seeds whose arrival sits at or below that row's own base draw count must reproduce
E259's seeds_endpoint_already_attained (52). If it does not, this face is reading a different
table than the one E259 published and nothing else on it is worth reading.

NO BILL, NO ADOPTION, NO RE-PRICING, NO PANEL TRADE: measurement only.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e252_star_prices_itself as e252  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E260_band_endpoint_arrival"
TITLE = "at how many draws does a window band endpoint stop moving?"
CUTOFF = "2026-10-29"
LEGS = ("self", "cross")
TOL = 1e-12
BASE_DEFAULT = 200          # E259's own rule: a row without band_draws was published at 200
SETTLED_SHARE = 0.95        # a row counts as settled at its base only if ~all seeds already were
NO_BILL = ("measurement only: arrival counts are read off the per-seed edge tables E259 already "
           "published; no draw is redrawn, no coefficient is re-priced, nothing is adopted")


# ------------------------------------------------------------------ load
def _p(name):
    return os.path.join(OUTDIR, name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


def _try_load(name):
    try:
        return load(name)
    except Exception:
        return None


def e259_face(tag="latest"):
    """E259's face: the dated one if present, else the latest pointer."""
    return _try_load("BANDWINDIST-%s.json" % CUTOFF) or _try_load("bandwindist_%s.json" % tag)


# ------------------------------------------------------------------ arrival maths
def grid_of(face):
    spec = (face or {}).get("frozen_spec") or {}
    grid = spec.get("draw_grid") or [60, 120, 200, 480, 960, 1920]
    return tuple(sorted(int(d) for d in grid))


def seed_series(edges_by_draw, leg, i):
    """{draw: edge} for seed `i` on `leg`, straight off E259's windows_raw table."""
    out = {}
    for d, legs in (edges_by_draw or {}).items():
        vals = (legs or {}).get(leg) or []
        v = vals[i] if i < len(vals) else None
        out[int(d)] = None if v is None else abs(float(v))
    return out


def arrival_of(series, top, tol=TOL):
    """First draw count at which this seed's endpoint equals its own value at `top`.

    The series is prefix-nested, so it is non-decreasing; the first count that reaches the top
    value is the count at which the seed stopped moving. Returns None when the series carries no
    finite value at `top` (the seed cannot be judged, and is published as such rather than as 0).
    """
    target = (series or {}).get(top)
    if target is None:
        return None
    target = abs(float(target))
    scale = max(1.0, target)
    for d in sorted(series):
        v = series.get(d)
        if v is None:
            continue
        if abs(abs(float(v)) - target) <= tol * scale:
            return int(d)
    return None


def nonmonotone_steps(series):
    """Count of prefix steps where the endpoint SHRANK -- nesting says this must be zero."""
    steps, prev = 0, None
    for d in sorted(series):
        v = series.get(d)
        if v is None:
            continue
        if prev is not None and float(v) < prev - TOL * max(1.0, prev):
            steps += 1
        prev = float(v)
    return steps


def arrival_table(face):
    """{window: {leg: [arrival per seed]}} plus the non-monotone audit."""
    grid = grid_of(face)
    top = grid[-1]
    raw = (face or {}).get("windows_raw") or {}
    table, audit = {}, {}
    for cell, rec in raw.items():
        by_draws = (rec or {}).get("by_draws") or {}
        n_seeds = 0
        for legs in by_draws.values():
            for leg in LEGS:
                n_seeds = max(n_seeds, len((legs or {}).get(leg) or []))
        table[cell], audit[cell] = {}, {}
        for leg in LEGS:
            arrivals, bad = [], 0
            for i in range(n_seeds):
                series = seed_series(by_draws, leg, i)
                arrivals.append(arrival_of(series, top))
                bad += 1 if nonmonotone_steps(series) else 0
            table[cell][leg] = arrivals
            audit[cell][leg] = {"n_seeds": n_seeds, "n_nonmonotone": bad}
    return table, audit


def _dist(values):
    vals = [int(v) for v in (values or []) if v is not None]
    if not vals:
        return {"n": 0, "min": None, "median": None, "max": None,
                "n_unjudgeable": len(values or [])}
    return {"n": len(vals), "min": min(vals), "median": statistics.median(vals),
            "max": max(vals)}


def window_record(arrivals, grid):
    """Per (window, leg): the arrival distribution and the shares at the two published bases."""
    vals = [int(v) for v in (arrivals or []) if v is not None]
    n = len(arrivals or [])
    dist = _dist(arrivals)
    hist = {str(d): sum(1 for v in vals if v == d) for d in grid}
    rec = {
        "n_seeds": n,
        "n_judged": dist["n"],
        "n_unjudgeable": n - dist["n"],
        "arrival_min": dist["min"],
        "arrival_median": dist["median"],
        "arrival_max": dist["max"],
        "arrival_hist": hist,
        "share_at_or_before_60": (sum(1 for v in vals if v <= 60) / dist["n"]) if dist["n"] else None,
        "share_at_or_before_200": (sum(1 for v in vals if v <= 200) / dist["n"]) if dist["n"] else None,
        "n_only_at_top": sum(1 for v in vals if v >= grid[-1]),
        "share_only_at_top": (sum(1 for v in vals if v >= grid[-1]) / dist["n"]) if dist["n"] else None,
        "n_endpoint_already_attained_at_60": sum(1 for v in vals if v <= 60),
    }
    return rec


def rows_of(face, arrivals):
    """Every published row re-read against its own base draw count."""
    out = []
    for r in (face or {}).get("rows") or []:
        cell = r.get("cell")
        row = r.get("row") or "self"
        leg = "cross" if row == "cross" else "self"
        base = int(float(r.get("band_draws") or BASE_DEFAULT))
        vals = [v for v in ((arrivals.get(cell) or {}).get(leg) or []) if v is not None]
        rec = {
            "cell": cell, "row": row, "leg": leg, "base_draws": base,
            "window_measured": cell in arrivals,
        }
        if not vals:
            rec.update({"n_at_base": None, "share_at_base": None,
                        "verdict": "window_not_measured"})
            out.append(rec)
            continue
        n_at_base = sum(1 for v in vals if v <= base)
        moving = [v for v in vals if v > base]
        share = n_at_base / len(vals)
        rec.update({
            "n_seeds": len(vals),
            "n_at_base": n_at_base,
            "share_at_base": share,
            "share_still_moving_at_base": 1.0 - share,
            "extra_draws_median": statistics.median([v - base for v in moving]) if moving else 0,
            "extra_draws_max": max([v - base for v in moving]) if moving else 0,
            "verdict": ("settled_at_base" if share >= SETTLED_SHARE
                        else "pre_settlement"),
        })
        out.append(rec)
    return out


def _arm_key(key):
    """'cross:200' -> ('cross', 200). The base and the leg are BOTH part of the arm."""
    leg, _, base = str(key).partition(":")
    return (leg or "self"), int(float(base or BASE_DEFAULT))


def cross_check(face, arrivals):
    """Arrival-derived degeneracy must reproduce E259's published count ARM BY ARM.

    E259 published 16 arms (4 windows x 2 base counts x 2 legs) of 40 seeds each. A multiplier of
    exactly 1.0 on an arm means the endpoint already arrived at or before that arm's base count, so
    this face's arrival table must reproduce every arm's count, not just the total -- the published
    ROWS are a different 16 (they carry the row's own base and leg), and summing over those is not
    a reproduction of anything.
    """
    arms, bad = [], 0
    for cell, table in ((face or {}).get("windows") or {}).items():
        for key, rec in (table or {}).items():
            leg, base = _arm_key(key)
            vals = [v for v in ((arrivals.get(cell) or {}).get(leg) or []) if v is not None]
            mine = sum(1 for v in vals if v <= base)
            want = rec.get("n_endpoint_already_attained")
            ok = (want is not None and mine == want)
            if not ok:
                bad += 1
            arms.append({"cell": cell, "arm": key, "leg": leg, "base_draws": base,
                         "n_seeds": len(vals), "n_at_base": mine, "e259_published": want,
                         "matches": ok})
    published = ((face or {}).get("summary") or {}).get("seeds_endpoint_already_attained")
    total = sum(a["n_at_base"] for a in arms)
    return {
        "arms": arms,
        "n_arms": len(arms),
        "arms_mismatched": bad,
        "recomputed": total,
        "e259_published": published,
        "matches": (bad == 0 and published is not None and total == published),
        "pin": ("a multiplier of exactly 1.0 means the endpoint already arrived at or before the "
                "arm's base count, so this face must reproduce E259 arm by arm (16 arms x 40 "
                "seeds); the published rows are a different 16 and cannot stand in for them"),
    }


# ------------------------------------------------------------------ verdict
def verdict_from(face, arrivals, rows, grid):
    top = grid[-1]
    measured = sorted(arrivals.keys())
    if not measured:
        return "no_windows_measured", "E259's edge tables are absent, so there is no stream to read"
    settled = [r for r in rows if r.get("verdict") == "settled_at_base"]
    pre = [r for r in rows if r.get("verdict") == "pre_settlement"]
    med = [v for cell in measured for leg in LEGS
           for v in [window_record(arrivals[cell][leg], grid).get("arrival_median")]
           if v is not None]
    median_arrival = statistics.median(med) if med else None
    n_at_top = sum(window_record(arrivals[cell][leg], grid).get("n_only_at_top") or 0
                   for cell in measured for leg in LEGS)
    n_total = sum(window_record(arrivals[cell][leg], grid).get("n_judged") or 0
                  for cell in measured for leg in LEGS)
    if pre:
        v = "published_base_below_arrival"
        why = ("%d of %d published rows are read off a stream that had not stopped moving: at their "
               "own base draw count a median of %s%% of seeds still had a moving endpoint "
               "(arrival median %s draws across windows vs published bases 60/200); %d of %d "
               "seeds across the measured windows reach their final endpoint only at the top of "
               "the grid (%d draws), so the grid -- not the seed stream -- is the binding "
               "constraint there"
               % (len(pre), len(rows),
                  round(100 * statistics.median([r.get("share_still_moving_at_base") or 0
                                                 for r in pre])),
                  (("%g" % median_arrival) if median_arrival is not None else "n/a"),
                  n_at_top, n_total, top))
        return v, why
    return ("endpoint_settles_before_published_base",
            "%d of %d published rows settle at or before their own base draw count (>= %d%% of "
            "seeds already final); median arrival %s draws against published bases 60/200, so the "
            "family publishes bands that have finished moving"
            % (len(settled), len(rows), int(100 * SETTLED_SHARE),
               ("%g" % median_arrival) if median_arrival is not None else "n/a"))


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face = e259_face()
    if face is None:
        out = {"study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
               "generated": datetime.now().isoformat(timespec="seconds"),
               "verdict": "no_windows_measured",
               "verdict_reason": "E259's BANDWINDIST face is absent; no arrival can be read",
               "windows": {}, "rows": [], "no_bill": NO_BILL}
        out["summary"] = _summary(out)
        if save:
            _write(out, outdir)
        return out

    grid = grid_of(face)
    arrivals, audit = arrival_table(face)
    windows = {cell: {leg: window_record(arrivals[cell][leg], grid) for leg in LEGS}
               for cell in arrivals}
    rows = rows_of(face, arrivals)
    v, why = verdict_from(face, arrivals, rows, grid)
    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": face.get("evidence_cutoff") or CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": {
            "design": "read each seed's band endpoint back at every draw count and find the first "
                      "count at which it equals its own value at the top of the grid",
            "grid": list(grid),
            "top_draws": grid[-1],
            "prefix_nesting": "one stream per seed; a smaller count is a literal prefix of a "
                              "larger one, so arrival is where the seed stops moving",
            "tolerance": TOL,
            "base_rule": "a published row without band_draws is read at %d (E259's own rule)"
                         % BASE_DEFAULT,
            "settled_share": SETTLED_SHARE,
            "source": "E259 windows_raw per-seed edge tables -- no new draws, no new estimate",
        },
        "source_face": "results/state_tilt/BANDWINDIST-%s.json" % (face.get("evidence_cutoff") or CUTOFF),
        "windows": windows,
        "arrivals_per_seed": {cell: {leg: arrivals[cell][leg] for leg in LEGS} for cell in arrivals},
        "monotone_audit": audit,
        "rows": rows,
        "cross_check": cross_check(face, arrivals),
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    out["summary"] = _summary(out)
    if save:
        _write(out, outdir)
    return out


def _summary(face):
    wins = face.get("windows") or {}
    rows = face.get("rows") or []
    meds = [w.get("arrival_median") for table in wins.values() for w in (table or {}).values()
            if w.get("arrival_median") is not None]
    cc = face.get("cross_check") or {}
    return {
        "windows_measured": len(wins),
        "legs": list(LEGS),
        "seeds": sum((face.get("monotone_audit") or {}).get(c, {}).get(l, {}).get("n_seeds") or 0
                     for c in (face.get("monotone_audit") or {})
                     for l in LEGS),
        "arrival_median_across_windows": statistics.median(meds) if meds else None,
        "arrival_min_across_windows": min(meds) if meds else None,
        "arrival_max_across_windows": max(meds) if meds else None,
        "seeds_only_at_top": sum(w.get("n_only_at_top") or 0
                                 for table in wins.values() for w in (table or {}).values()),
        "seeds_at_or_before_60": sum(w.get("n_endpoint_already_attained_at_60") or 0
                                     for table in wins.values() for w in (table or {}).values()),
        "rows": len(rows),
        "rows_settled_at_base": sum(1 for r in rows if r.get("verdict") == "settled_at_base"),
        "rows_pre_settlement": sum(1 for r in rows if r.get("verdict") == "pre_settlement"),
        "rows_window_not_measured": sum(1 for r in rows
                                        if r.get("verdict") == "window_not_measured"),
        "nonmonotone_steps": sum((v or {}).get("n_nonmonotone") or 0
                                 for table in (face.get("monotone_audit") or {}).values()
                                 for v in (table or {}).values()),
        "cross_check_arms": cc.get("n_arms"),
        "cross_check_arms_mismatched": cc.get("arms_mismatched"),
        "cross_check_recomputed": cc.get("recomputed"),
        "cross_check_e259_published": cc.get("e259_published"),
        "cross_check_matches": cc.get("matches"),
    }


# ------------------------------------------------------------------ write / verify
def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDARRIVAL-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    latest = os.path.join(outdir, "bandarrival_latest.json")
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive every arrival, share and row verdict straight off the published per-seed table."""
    outdir = outdir or OUTDIR
    problems = []
    face = e259_face()
    path = os.path.join(outdir, "BANDARRIVAL-%s%s.json" % (CUTOFF, tag))
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    if face is None:
        return ["E259 face absent: cannot verify"]
    grid = grid_of(face)
    if got.get("frozen_spec", {}).get("grid") != list(grid):
        problems.append("grid published does not match E259's")
    raw = face.get("windows_raw") or {}
    if not raw:
        problems.append("E259 face carries no raw edge table")
    recomputed, _ = arrival_table(face)
    for cell, legs in recomputed.items():
        for leg in LEGS:
            pub = ((got.get("arrivals_per_seed") or {}).get(cell) or {}).get(leg)
            if pub != legs[leg]:
                problems.append("%s/%s: published arrivals differ from a re-derivation" % (cell, leg))
            rec = ((got.get("windows") or {}).get(cell) or {}).get(leg) or {}
            fresh = window_record(legs[leg], grid)
            for k in ("n_judged", "arrival_min", "arrival_median", "arrival_max",
                      "n_only_at_top", "n_endpoint_already_attained_at_60"):
                if rec.get(k) != fresh.get(k):
                    problems.append("%s/%s: %s published %r != %r"
                                    % (cell, leg, k, rec.get(k), fresh.get(k)))
            if sum(rec.get("arrival_hist", {}).values()) != rec.get("n_judged"):
                problems.append("%s/%s: arrival hist does not sum to the judged seeds" % (cell, leg))
    rows = rows_of(face, recomputed)
    pub_rows = got.get("rows") or []
    if len(rows) != len(pub_rows):
        problems.append("row count published %d != re-derived %d" % (len(pub_rows), len(rows)))
    for a, b in zip(pub_rows, rows):
        for k in ("n_at_base", "share_at_base", "verdict", "base_draws", "extra_draws_median"):
            if a.get(k) != b.get(k):
                problems.append("row %s/%s: %s published %r != %r"
                                % (a.get("cell"), a.get("row"), k, a.get(k), b.get(k)))
    cc = cross_check(face, recomputed)
    pub_cc = got.get("cross_check") or {}
    if (cc.get("arms") or []) != (pub_cc.get("arms") or []):
        problems.append("cross-check arm table does not re-derive")
    if cc.get("recomputed") != pub_cc.get("recomputed"):
        problems.append("cross-check recomputed %r != published %r"
                        % (cc.get("recomputed"), pub_cc.get("recomputed")))
    if not cc.get("matches"):
        problems.append("cross-check FAILS: arrival-derived degeneracy %r != E259 published %r"
                        % (cc.get("recomputed"), cc.get("e259_published")))
    v, why = verdict_from(face, recomputed, rows, grid)
    if got.get("verdict") != v or got.get("verdict_reason") != why:
        problems.append("verdict/reason do not re-derive")
    if got.get("summary") != _summary(got):
        problems.append("summary does not re-derive from the published face")
    return problems


# ------------------------------------------------------------------ selftest
def _legs(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def selftest():
    legs = []
    grid = (60, 120, 200, 480, 960, 1920)

    # --- arrival is the FIRST count that reaches the top value
    s = {60: 0.30, 120: 0.31, 200: 0.33, 480: 0.40, 960: 0.40, 1920: 0.40}
    legs.append(_legs(arrival_of(s, 1920) == 480, "arrival is the first draw count that reaches "
                                                  "the endpoint at the top", arrival_of(s, 1920)))

    # --- a seed that never moves after the smallest count arrives at the smallest count
    flat = {d: 0.25 for d in grid}
    legs.append(_legs(arrival_of(flat, 1920) == 60, "a seed that never moves arrives at 60",
                      arrival_of(flat, 1920)))

    # --- a seed that keeps moving to the last draw arrives at the last draw
    rising = {d: 0.20 + 0.01 * i for i, d in enumerate(grid)}
    legs.append(_legs(arrival_of(rising, 1920) == 1920,
                      "a seed still moving at the top arrives at the top", arrival_of(rising, 1920)))

    # --- a seed with no finite value at the top is unjudgeable, never silently 0
    legs.append(_legs(arrival_of({60: 0.3, 1920: None}, 1920) is None,
                      "a seed without a finite top value is unjudgeable, not zero"))

    # --- equality floor: tiny float drift inside the tolerance still counts as arrived
    drift = {60: 0.3000000000000000, 1920: 0.30000000000000004}
    legs.append(_legs(arrival_of(drift, 1920) == 60,
                      "sub-tolerance float drift still reads as arrived", arrival_of(drift, 1920)))

    # --- non-monotone audit: nesting says the endpoint never shrinks
    legs.append(_legs(nonmonotone_steps({60: 0.3, 120: 0.2}) == 1,
                      "a shrinking prefix is counted as a non-monotone step", 1))
    legs.append(_legs(nonmonotone_steps({60: 0.2, 120: 0.3, 200: 0.3}) == 0,
                      "a non-shrinking prefix reports zero non-monotone steps", 0))

    # --- fixture window record: 4 seeds arriving at 60/60/480/1920
    arrivals = [60, 60, 480, 1920]
    rec = window_record(arrivals, grid)
    legs.append(_legs(rec["arrival_median"] == 270.0, "median arrival of [60,60,480,1920] is 270",
                      rec["arrival_median"]))
    legs.append(_legs(rec["share_at_or_before_60"] == 0.5, "half the fixture arrives at 60",
                      rec["share_at_or_before_60"]))
    legs.append(_legs(rec["n_only_at_top"] == 1, "one fixture seed arrives only at the top",
                      rec["n_only_at_top"]))
    legs.append(_legs(sum(rec["arrival_hist"].values()) == 4, "the fixture hist sums to 4 seeds",
                      sum(rec["arrival_hist"].values())))

    # --- row rule: base 200 with two of four seeds already final = pre_settlement
    e259fake = {"rows": [{"cell": "fx", "row": "self", "band_draws": 200}],
                "summary": {"seeds_endpoint_already_attained": 2},
                "windows_raw": {}, "frozen_spec": {"draw_grid": list(grid)}}
    rows = rows_of(e259fake, {"fx": {"self": arrivals, "cross": arrivals}})
    r = rows[0]
    legs.append(_legs(r["n_at_base"] == 2 and abs(r["share_at_base"] - 0.5) < 1e-12,
                      "two of four seeds sit at or before a 200-draw base", r["n_at_base"]))
    legs.append(_legs(r["verdict"] == "pre_settlement",
                      "a base with half the seeds still moving is pre_settlement", r["verdict"]))
    legs.append(_legs(r["extra_draws_median"] == 1000.0,
                      "the two moving seeds need 280 and 1720 extra draws (median 1000)",
                      r["extra_draws_median"]))

    # --- the settled side of the same rule
    rows2 = rows_of({"rows": [{"cell": "fx", "row": "self", "band_draws": 1920}],
                     "summary": {}, "windows_raw": {}, "frozen_spec": {"draw_grid": list(grid)}},
                    {"fx": {"self": arrivals, "cross": arrivals}})
    legs.append(_legs(rows2[0]["verdict"] == "settled_at_base",
                      "a base at the top settles every seed", rows2[0]["verdict"]))

    # --- a row whose window was never measured is named, not silently zeroed
    rows3 = rows_of({"rows": [{"cell": "ghost", "row": "cross"}], "summary": {}}, {"fx": {"self": []}})
    legs.append(_legs(rows3[0]["verdict"] == "window_not_measured"
                      and rows3[0]["base_draws"] == BASE_DEFAULT,
                      "an unmeasured window is published as such and defaults to a 200 base",
                      rows3[0]["verdict"]))

    # --- cross-check: ARM sums must equal E259's published degeneracy count. Row sums must NOT
    # be used for this -- the published rows are a different 16 than E259's distribution arms.
    armfake = {"windows": {"fx": {"self:200": {"n_endpoint_already_attained": 2},
                                  "cross:200": {"n_endpoint_already_attained": 2}}},
               "summary": {"seeds_endpoint_already_attained": 4}}
    cc = cross_check(armfake, {"fx": {"self": arrivals, "cross": arrivals}})
    legs.append(_legs(cc["recomputed"] == 4 and cc["matches"] is True and cc["n_arms"] == 2,
                      "the arm-level cross-check reproduces the published count", cc["matches"]))
    rowsum = sum(r.get("n_at_base") or 0 for r in rows)
    legs.append(_legs(rowsum == 2 and rowsum != cc["recomputed"],
                      "row sums are NOT the arm total, which is why the pin is per arm", rowsum))
    cc_bad = cross_check({"windows": {"fx": {"self:200": {"n_endpoint_already_attained": 2}}},
                          "summary": {"seeds_endpoint_already_attained": 3}},
                         {"fx": {"self": arrivals}})
    legs.append(_legs(cc_bad["matches"] is False and cc_bad["arms_mismatched"] == 0,
                      "a total-only mismatch is caught even when every arm agrees", cc_bad))

    # --- summary self-consistency on the fixture face
    face_fx = {"windows": {"fx": {"self": rec, "cross": rec}}, "rows": rows,
               "monotone_audit": {"fx": {"self": {"n_seeds": 4, "n_nonmonotone": 0},
                                         "cross": {"n_seeds": 4, "n_nonmonotone": 0}}},
               "cross_check": cc}
    s = _summary(face_fx)
    legs.append(_legs(s["windows_measured"] == 1 and s["rows_pre_settlement"] == 1,
                      "summary counts the fixture windows and row verdicts", s["rows_pre_settlement"]))
    legs.append(_legs(s["seeds"] == 8, "summary counts both legs' seeds", s["seeds"]))

    ok = all(r["ok"] for r in legs)
    return {"ok": ok, "legs": legs, "passed": sum(1 for r in legs if r["ok"]), "total": len(legs)}


# ------------------------------------------------------------------ cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=TITLE)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "verify", "summarize"])
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        res = selftest()
        for r in res["legs"]:
            print("%-4s %s" % ("ok" if r["ok"] else "FAIL", r["leg"]))
        print("selftest %d/%d" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        problems = verify(outdir=args.outdir, tag=args.tag)
        for p in problems:
            print("PROBLEM %s" % p)
        print("verify %s (%d problems)" % ("OK" if not problems else "FAILED", len(problems)))
        return 0 if not problems else 1
    if args.cmd == "summarize":
        face = run(save=False)
        print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
        print(face.get("verdict_reason"))
        return 0
    face = run(outdir=args.outdir)
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
    print(face.get("verdict"))
    print(face.get("verdict_reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())