#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HOW FAR IS EACH CALENDAR REFUSAL FROM FLIPPING -- in the units of the only
number that can still move.

WHY THIS FILE EXISTS
--------------------
compute_audit has been printing, round after round:

    supply_candidates.verdict = AGENDA_DEBT
    agenda_cause              = calendar
    verdict                   = NO_CANDIDATE_PASSES_CALENDAR
    n_candidates = 4, n_refused = 4

A refusal without a distance is indistinguishable from "we do not know": the
reader cannot tell whether the desk should wait a month, wait a year, or open a
different family. r1415/r1418 built the gate, r1420 let it answer "cannot tell",
r1425 showed Y4 is an annual-Sharpe test in disguise, r1459 pointed at supply as
the next block. None of them answered the question a desk actually asks of a red
line: *how far away is it?*

Every one of these refusals is a function of seven annual numbers, and six of
them are finished. The seventh -- the partial current year -- is the only one
that can still move, so each refusal has a distance in that year's return, and
a hurdle for the months that are left. This file computes both from published
receipts. It re-prices nothing, computes no returns, and moves no line.

WHAT IS COMPUTED
----------------
For every candidate in results/supply_calendar.json, from its published yearly
block (results/etf_book_year_gate/YEAR-GATE.json, results/admission/CANDIDATES.json,
results/etf_book_phase_gate.json fallback):

  1. the verdict now, re-derived through candidate_year_gate.year_checks (the
     frozen thresholds are imported, never transcribed);
  2. the smallest value of the partial year's return that makes every calendar
     check pass (a sweep in 0.01pp steps, so the answer is not a closed form
     that can disagree with the rule);
  3. the implied hurdle for the rest of that year: with `cohorts` of the year's
     four already booked, the remaining cohorts must return
     (1 + v*)/(1 + v0) - 1;
  4. UNREACHABLE_THIS_YEAR when no value of the partial year can flip the
     verdict -- because the failing check sits on a completed year, or because
     Y4's share is already above the line on the completed years alone.

Three refusals are printed side by side in every case:
  - a candidate that already reads ADMIT at its current numbers,
  - a candidate whose distance is finite (this is the nearest supply),
  - a candidate the current year cannot fix (do not wait on it).
Conflating the second and the third is the defect this file is written against:
"wait another year" and "open another family" are opposite instructions.

READS ONLY PUBLISHED RECEIPTS. No returns are computed here.

  python scripts/etf_book_calendar_distance.py run
  python scripts/etf_book_calendar_distance.py selftest
  python scripts/etf_book_calendar_distance.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import candidate_year_gate as cyg  # noqa: E402  (frozen thresholds live there)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_calendar_distance.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_calendar_distance.md")

SUPPLY = "results/supply_calendar.json"
YEAR_GATE = "results/etf_book_year_gate/YEAR-GATE.json"
CANDIDATES = "results/admission/CANDIDATES.json"

STEP = 0.01
V_MIN = -100.0
V_MAX = 300.0
COHORTS_PER_YEAR = 4

CHECKS = ("Y1_positive_years_share", "Y2_median_positive",
          "Y3_worst_year", "Y4_top2_share")


# --------------------------------------------------------------------------- io
def _load(rel: str) -> dict:
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def _sha16(rel: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _rows(years) -> list[dict]:
    """Accept the two published shapes: {year: {net_pct, cohorts}} or a row list."""
    if isinstance(years, list):
        rows = []
        for r in years:
            n, c = r.get("net_pct"), r.get("cohorts")
            if n is None or c is None:
                continue
            rows.append({"year": str(r["year"]), "net_pct": float(n), "cohorts": int(c),
                         "partial": int(c) < COHORTS_PER_YEAR})
        rows.sort(key=lambda r: r["year"])
        return rows
    out = []
    for y, blk in (years or {}).items():
        if isinstance(blk, dict):
            n, c = blk.get("net_pct"), blk.get("cohorts")
        else:
            n, c = blk, COHORTS_PER_YEAR
        if n is None or c is None:
            continue
        out.append({"year": str(y), "net_pct": float(n), "cohorts": int(c),
                    "partial": int(c) < COHORTS_PER_YEAR})
    out.sort(key=lambda r: r["year"])
    return out


# ------------------------------------------------------------------ the sweep
def judge(rows: list[dict], capacity_cny: float | None) -> tuple[str, dict]:
    y = cyg.year_checks(rows, capacity_cny)
    return cyg.verdict(y), y


def distance(rows: list[dict], capacity_cny: float | None) -> dict:
    """Smallest partial-year return that flips the calendar verdict to ADMIT.

    The sweep exists so this file cannot disagree with the frozen rule: the
    question "what would it take" is answered by running the rule, not by
    re-deriving its algebra.
    """
    verdict0, y0 = judge(rows, capacity_cny)
    if verdict0 == "CAPACITY_LIMITED":
        return {"state": "CAPACITY_LIMITED", "verdict_now": verdict0,
                "checks_now": y0["checks"], "metrics_now": y0["metrics"],
                "note": "capacity is not a calendar check; nothing here can flip it",
                "flip_min_pct": None, "hurdle_pct": None}

    partial = [r for r in rows if r["partial"]]
    if all(y0["checks"][k] for k in CHECKS):
        # already passing: the distance is zero, and waiting cannot improve on that
        return {"state": "ADMIT_NOW", "verdict_now": verdict0,
                "checks_now": y0["checks"], "metrics_now": y0["metrics"],
                "partial_year": (partial[-1]["year"] if partial else None),
                "partial_now_pct": (round(partial[-1]["net_pct"], 4) if partial else None),
                "cohorts": (partial[-1]["cohorts"] if partial else None),
                "flip_min_pct": None, "distance_pp": 0.0, "hurdle_pct": None,
                "note": "the published numbers already pass; nothing to wait for"}

    if not partial:
        return {"state": "NO_PARTIAL_YEAR", "verdict_now": verdict0,
                "checks_now": y0["checks"], "metrics_now": y0["metrics"],
                "note": "every year is complete, so no number can still move",
                "flip_min_pct": None, "hurdle_pct": None}

    target = partial[-1]
    v0 = target["net_pct"]

    flip_min = None
    v = V_MIN
    steps = int(round((V_MAX - V_MIN) / STEP)) + 1
    for i in range(steps):
        v = V_MIN + i * STEP
        trial = [dict(r) for r in rows]
        for r in trial:
            if r["year"] == target["year"]:
                r["net_pct"] = v
        verdict, _ = judge(trial, capacity_cny)
        if verdict == "ADMIT":
            flip_min = round(v, 2)
            break

    if flip_min is None:
        return {"state": "UNREACHABLE_THIS_YEAR", "verdict_now": verdict0,
                "checks_now": y0["checks"], "metrics_now": y0["metrics"],
                "partial_year": target["year"], "partial_now_pct": round(v0, 4),
                "cohorts": target["cohorts"],
                "note": ("no value of the partial year flips the verdict; the failing "
                         "check sits on a completed year or on the completed-years share"),
                "flip_min_pct": None, "hurdle_pct": None}

    if v0 >= flip_min:
        return {"state": "ADMIT_NOW", "verdict_now": verdict0,
                "checks_now": y0["checks"], "metrics_now": y0["metrics"],
                "partial_year": target["year"], "partial_now_pct": round(v0, 4),
                "cohorts": target["cohorts"],
                "flip_min_pct": flip_min, "distance_pp": 0.0, "hurdle_pct": None,
                "note": "the published numbers already pass; nothing to wait for"}

    # hurdle for the remaining cohorts of the year
    hurdle = None
    if target["cohorts"] > 0:
        hurdle = round(((1.0 + flip_min / 100.0) / (1.0 + v0 / 100.0) - 1.0) * 100.0, 4)

    return {"state": "FINITE_DISTANCE", "verdict_now": verdict0,
            "checks_now": y0["checks"], "metrics_now": y0["metrics"],
            "partial_year": target["year"], "partial_now_pct": round(v0, 4),
            "cohorts": target["cohorts"],
            "cohorts_booked": target["cohorts"],
            "cohorts_left": max(0, COHORTS_PER_YEAR - target["cohorts"]),
            "flip_min_pct": flip_min,
            "distance_pp": round(flip_min - v0, 4),
            "hurdle_pct": hurdle,
            "note": ("the remaining cohorts of this year must return hurdle_pct to end it at "
                     "flip_min_pct and pass every calendar check")}


# ------------------------------------------------------------------ agreement
def _agrees(single_phase_state: str, supply_pass) -> bool:
    """Does this file's single-phase reading say the same thing the supply face says?

    The defect this guards: a phase-median refusal printed as a single-phase pass turns
    "cannot tell across phases" back into "already passes" (E206/E319 class).
    """
    admits = single_phase_state == "ADMIT_NOW"
    return admits == bool(supply_pass)


# ------------------------------------------------------------------- sources
def candidates() -> tuple[list[dict], dict]:
    """One row per candidate in the supply face, with its published yearly block."""
    sup = _load(SUPPLY)
    yg = _load(YEAR_GATE)
    cand = _load(CANDIDATES)

    by_book = {}
    for b in yg.get("books", []):
        by_book[b.get("book")] = b
    for c in cand.get("candidates", []):
        name = c.get("candidate") or c.get("arm") or c.get("book")
        if name and name not in by_book:
            by_book[name] = c
    for a in cand.get("arms", []) or []:
        name = a.get("candidate") or a.get("arm")
        if name and name not in by_book:
            by_book[name] = a

    rows = []
    for s in sup.get("candidates", []):
        name = s.get("candidate")
        src = by_book.get(name)
        if src is None:
            rows.append({"candidate": name, "state": "NO_YEARLY_BLOCK",
                         "note": "the supply face lists this candidate but no receipt "
                                 "publishes its yearly rows",
                         "supply_receipt": s.get("receipt"),
                         "supply_pass": s.get("pass")})
            continue
        yrs = src.get("years") or src.get("by_year") or src.get("per_year")
        yr_rows = _rows(yrs)
        cap = src.get("capacity_cny_1day_5pct")
        rows.append({
            "candidate": name,
            "supply_state": s.get("state"),
            "supply_pass": s.get("pass"),
            "supply_median_top2": s.get("median_top2_share"),
            "supply_phases": s.get("phases"),
            "supply_receipt": s.get("receipt"),
            "yearly_receipt": YEAR_GATE if name in
                              {b.get("book") for b in yg.get("books", [])} else CANDIDATES,
            "capacity_cny": cap,
            "rows": yr_rows,
        })
    return rows, {"supply": {"path": SUPPLY, "sha16": _sha16(SUPPLY)},
                  "year_gate": {"path": YEAR_GATE, "sha16": _sha16(YEAR_GATE)},
                  "candidates": {"path": CANDIDATES, "sha16": _sha16(CANDIDATES)}}


# ----------------------------------------------------------------------- run
def run() -> dict:
    t0 = time_now()
    sup_rows, sources = candidates()
    out = []
    for r in sup_rows:
        if "rows" not in r:
            out.append(r)
            continue
        d = distance(r["rows"], r.get("capacity_cny"))
        d.update({"candidate": r["candidate"], "supply_state": r.get("supply_state"),
                  "supply_pass": r.get("supply_pass"),
                  "supply_median_top2": r.get("supply_median_top2"),
                  "supply_phases": r.get("supply_phases"),
                  "supply_receipt": r.get("supply_receipt"),
                  "yearly_receipt": r.get("yearly_receipt"),
                  "capacity_cny": r.get("capacity_cny"),
                  "years": [{"year": x["year"], "net_pct": round(x["net_pct"], 4),
                             "cohorts": x["cohorts"]} for x in r["rows"]]})
        # The supply face judges on a MEDIAN over decision phases; this file reads one
        # yearly block. When the two disagree the distance is a distance on a reading
        # the supply face does not trust, and printing it as the nearest supply would
        # turn "cannot tell across phases" back into "already passes" (E206 class).
        agrees = _agrees(d.get("state"), r.get("supply_pass"))
        d["reading_agrees_with_supply"] = agrees
        if not agrees:
            d["state"] = "READINGS_DISAGREE"
            d["note"] = ("single-phase block reads %s while the supply face reads %s "
                         "across %s phases; no distance is claimed on the untrusted reading"
                         % (d.get("verdict_now"), r.get("supply_state"),
                            r.get("supply_phases")))
            d["distance_pp"] = None
            d["hurdle_pct"] = None
        out.append(d)

    finite = [c for c in out if c.get("state") == "FINITE_DISTANCE"]
    unreachable = [c for c in out if c.get("state") == "UNREACHABLE_THIS_YEAR"]
    admitting = [c for c in out if c.get("state") == "ADMIT_NOW"]
    disagreeing = [c for c in out if c.get("state") == "READINGS_DISAGREE"]

    nearest = min(finite, key=lambda c: abs(c.get("distance_pp") or 1e9)) if finite else None
    if admitting:
        summary_verdict = "CANDIDATE_ALREADY_PASSES"
        sentence = ("%d candidate(s) already read ADMIT on published numbers"
                    % len(admitting))
    elif nearest is not None:
        summary_verdict = "WAIT_ON_A_WATCHABLE_NUMBER"
        sentence = ("%s is %.2fpp of %s return away from ADMIT; the remaining %d cohort(s) "
                    "must return %.2f%%"
                    % (nearest["candidate"], nearest["distance_pp"], nearest["partial_year"],
                       nearest.get("cohorts_left") or 0, nearest.get("hurdle_pct") or 0.0))
    elif out:
        summary_verdict = "NO_WAIT_CAN_HELP"
        sentence = "no candidate can be flipped by this year's return; the block is structural"
    else:
        summary_verdict = "NO_CANDIDATES"
        sentence = "the supply face declares no candidate to measure"

    return {
        "face": "etf_book_calendar_distance",
        "asof": now_iso(),
        "evidence_cutoff": max((c.get("years") or [{}])[-1].get("year", "") for c in out) or "",
        "question": "how far is each refused supply candidate from passing its own calendar?",
        "rule": {"source": "scripts/candidate_year_gate.py (imported, not transcribed)",
                 "checks": list(CHECKS),
                 "sweep_pp": [V_MIN, V_MAX, STEP],
                 "note": "the flip point is found by running the frozen rule, never by algebra"},
        "sources": sources,
        "candidates": out,
        "summary": {"verdict": summary_verdict, "sentence": sentence,
                    "n_candidates": len(out), "n_finite": len(finite),
                    "n_unreachable": len(unreachable), "n_admit_now": len(admitting),
                    "n_readings_disagree": len(disagreeing),
                    "nearest": (nearest or {}).get("candidate"),
                    "nearest_distance_pp": (nearest or {}).get("distance_pp")},
        "honest": [
            "no book is re-priced here: every yearly row is copied from a published receipt",
            "the partial year is not annualised; the hurdle is the return needed over the "
            "remaining cohorts, which is a different number from an annualised rate",
            "a finite distance is not a forecast: it says what the current year must deliver "
            "for the calendar gate to pass, not what it will deliver",
            "distance is measured on the return of one year; a book can also be re-cut, and "
            "that path is not priced here",
        ],
        "elapsed_sec": round(time_now() - t0, 1),
    }


def time_now() -> float:
    import time
    return time.time()


def now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def render_md(d: dict) -> str:
    s = d["summary"]
    lines = ["# Calendar distance: how far each refusal is from flipping", "",
             "asof %s | evidence_cutoff %s" % (d["asof"], d["evidence_cutoff"]), "",
             "**%s** — %s" % (s["verdict"], s["sentence"]), "",
             "| candidate | verdict now | failing | %s now | flip at | distance | hurdle left |"
             % "partial year",
             "|---|---|---|---|---|---|---|"]
    for c in d["candidates"]:
        if "checks_now" not in c:
            lines.append("| %s | %s | — | — | — | — | — |"
                         % (c["candidate"], c.get("state")))
            continue
        failing = ",".join(k for k, v in c["checks_now"].items() if v is False) or "none"
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            c["candidate"], c["verdict_now"], failing,
            ("%.2f%%" % c["partial_now_pct"]) if c.get("partial_now_pct") is not None else "—",
            ("%.2f%%" % c["flip_min_pct"]) if c.get("flip_min_pct") is not None else
            c.get("state"),
            ("%.2fpp" % c["distance_pp"]) if c.get("distance_pp") is not None else "—",
            ("%.2f%%" % c["hurdle_pct"]) if c.get("hurdle_pct") is not None else "—"))
    lines += ["", "## What this does not say", ""]
    lines += ["- %s" % h for h in d["honest"]]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------- selftest
def _mk(years: dict, partial_year: str, cohorts: int) -> list[dict]:
    return [{"year": str(y), "net_pct": float(v),
             "cohorts": cohorts if str(y) == partial_year else COHORTS_PER_YEAR,
             "partial": (str(y) == partial_year and cohorts < COHORTS_PER_YEAR)}
            for y, v in years.items()]


def selftest() -> int:
    ok = 0
    fail = []

    def leg(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    # L1: a book that already passes reports ADMIT_NOW, not a zero-distance refusal
    rows = _mk({"2020": 8, "2021": 9, "2022": 10, "2023": 11, "2024": 12,
                "2025": 13, "2026": 5}, "2026", 2)
    r = distance(rows, None)
    leg("L1 already-passing book reads ADMIT_NOW", r["state"] == "ADMIT_NOW")

    # L2: Y4 can be flipped by a big enough partial year -> finite distance with a hurdle
    rows = _mk({"2020": 2, "2021": 3, "2022": 4, "2023": 5, "2024": 30,
                "2025": 40, "2026": 1}, "2026", 2)
    r = distance(rows, None)
    leg("L2 concentrated book has a finite distance", r["state"] == "FINITE_DISTANCE")
    leg("L2 the distance is positive", (r.get("distance_pp") or 0) > 0)
    leg("L2 the hurdle is computed from the booked part", r.get("hurdle_pct") is not None)
    # the flip must actually pass the frozen rule when applied
    if r["state"] == "FINITE_DISTANCE":
        trial = [dict(x) for x in rows]
        for x in trial:
            if x["partial"]:
                x["net_pct"] = r["flip_min_pct"]
        v, _ = judge(trial, None)
        leg("L2 the reported flip point passes the rule", v == "ADMIT")
        # one step lower must not pass, otherwise the reported minimum is not minimal
        trial = [dict(x) for x in rows]
        for x in trial:
            if x["partial"]:
                x["net_pct"] = r["flip_min_pct"] - STEP
        v, _ = judge(trial, None)
        leg("L2 nothing below the flip point passes", v != "ADMIT")

    # L3: worst year on a COMPLETED year -> no partial-year value can fix it
    rows = _mk({"2020": -20, "2021": 9, "2022": 10, "2023": 11, "2024": 12,
                "2025": 13, "2026": 5}, "2026", 2)
    r = distance(rows, None)
    leg("L3 completed-year failure is UNREACHABLE_THIS_YEAR",
        r["state"] == "UNREACHABLE_THIS_YEAR")

    # L4: a fully booked book that fails has no number left to move
    rows = _mk({"2020": -20, "2021": 9, "2022": 10, "2023": 11, "2024": 12,
                "2025": 13, "2026": 14}, "2026", 4)
    r = distance(rows, None)
    leg("L4 a fully booked book publishes NO_PARTIAL_YEAR", r["state"] == "NO_PARTIAL_YEAR")

    # L4b: a book whose partial year reads ADMIT while the supply face refuses it must not
    # be printed as "already passes" -- the two readings are different objects
    leg("L4b agreement flag separates a single-phase pass from a phase refusal",
        _agrees("ADMIT_NOW", False) is False and _agrees("ADMIT_NOW", True) is True
        and _agrees("FINITE_DISTANCE", False) is True)

    # L5: capacity is not a calendar check and cannot be flipped here
    rows = _mk({"2020": 8, "2021": 9, "2022": 10, "2023": 11, "2024": 12,
                "2025": 13, "2026": 5}, "2026", 4)
    r = distance(rows, 1_000_000.0)
    leg("L5 capacity-limited is reported without a calendar distance",
        r["state"] == "CAPACITY_LIMITED")

    # L6: raising the partial year cannot make a passing book fail through Y1/Y2 medians
    rows = _mk({"2020": 1, "2021": 2, "2022": 3, "2023": 4, "2024": 5,
                "2025": 6, "2026": -3}, "2026", 1)
    r = distance(rows, None)
    leg("L6 a negative partial year still reports a calendar state",
        r["state"] in ("FINITE_DISTANCE", "UNREACHABLE_THIS_YEAR", "ADMIT_NOW"))

    # L7: the two published row shapes normalise to the same rows
    dict_shape = {"2026": {"net_pct": 1.9, "cohorts": 3}, "2025": {"net_pct": 43.1, "cohorts": 4}}
    list_shape = [{"year": "2026", "net_pct": 1.9, "cohorts": 3},
                  {"year": "2025", "net_pct": 43.1, "cohorts": 4}]
    leg("L7 both published year shapes normalise identically",
        _rows(dict_shape) == _rows(list_shape))

    # L8: a zero-cohort partial year publishes no hurdle instead of inventing one
    rows = _mk({"2020": 2, "2021": 3, "2022": 4, "2023": 5, "2024": 30,
                "2025": 40, "2026": 1}, "2026", 0)
    r = distance(rows, None)
    leg("L8 zero cohorts publishes no hurdle",
        r.get("hurdle_pct") is None or r["state"] != "FINITE_DISTANCE")

    # L9: the same numbers judged twice give the same flip point (no hidden randomness)
    rows = _mk({"2020": 2, "2021": 3, "2022": 4, "2023": 5, "2024": 30,
                "2025": 40, "2026": 1}, "2026", 2)
    leg("L9 distance is deterministic",
        distance(rows, None).get("flip_min_pct") == distance(rows, None).get("flip_min_pct"))

    print("selftest %d/%d PASS" % (ok, ok + len(fail)))
    if fail:
        for f in fail:
            print("  FAIL: %s" % f)
        return 1
    return 0


# ---------------------------------------------------------------------- check
def check() -> int:
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL: no published receipt yet")
        return 1
    pub = _load("results/etf_book_calendar_distance.json")
    now = run()
    probs = []
    pc = {c["candidate"]: c for c in pub.get("candidates", [])}
    nc = {c["candidate"]: c for c in now.get("candidates", [])}
    if set(pc) != set(nc):
        probs.append("candidate set changed: %s vs %s" % (sorted(pc), sorted(nc)))
    for name, c in nc.items():
        p = pc.get(name)
        if not p:
            continue
        for k in ("state", "verdict_now", "flip_min_pct", "hurdle_pct", "distance_pp"):
            if p.get(k) != c.get(k):
                probs.append("%s.%s published=%r now=%r" % (name, k, p.get(k), c.get(k)))
        if p.get("checks_now") != c.get("checks_now"):
            probs.append("%s.checks_now drifted" % name)
    if pub.get("summary", {}).get("verdict") != now["summary"]["verdict"]:
        probs.append("summary verdict drifted")
    if probs:
        for p in probs[:12]:
            print("CHECK_FAIL: %s" % p)
        return 1
    print("CHECK_OK: %d candidates re-derived, no drift" % len(nc))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.check:
        return check()
    d = run()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(d))
    print(json.dumps(d["summary"], ensure_ascii=False))
    for c in d["candidates"]:
        print("  %-26s %-22s %s" % (c["candidate"], c.get("state"),
                                    c.get("distance_pp") if c.get("distance_pp") is not None else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())