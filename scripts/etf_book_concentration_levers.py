#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""which knob, if any, buys the concentration gate without giving back the book?

WHY THIS FILE EXISTS
--------------------
r1460 measured the refusal: the adopted bond-free book (nobond_vt08) fails Y4 by
1.24pp of this year's return, and its 2025 leg alone is 43.06% of a 81.06% sum.
The only path that receipt printed is "wait for 2026". That is a forecast, not an
action. The book has knobs that change which years carry it -- width, rebalance
period, and the vol target -- and none of them had ever been priced against the
year axis.

This file prices ONE knob at a time off the published control cell (20-bar
rebalance, 5 names, 10bp, 8% vol target) and re-issues the frozen calendar gate
on every arm. It is deliberately a single-factor sweep, not a grid: r1449 showed
three rulers do not add, so mixing width and rebalance in one cell would publish
an interaction nobody asked for.

Readings are honest by construction:
  * the control arm must reproduce the published nobond_vt08 CAGR, else the run
    aborts instead of publishing a book it cannot identify;
  * a partial year keeps its raw return and its cohort count (a cohort is 60
    bars ~= 2.9 months) and is never annualised into the gate;
  * every arm re-derives its yearly rows from its own equity curve -- nothing is
    transcribed from another receipt.

self  python scripts/etf_book_concentration_levers.py selftest    # synthetic, fast
run   python scripts/etf_book_concentration_levers.py run         # real panel, minutes
check python scripts/etf_book_concentration_levers.py check       # re-derive from receipt
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import candidate_year_gate as G
import etf_book_year_gate as YG        # the published calendar-year definition

OUT = os.path.join(ROOT, "results", "etf_book_concentration_levers.json")
CONTROL_RECEIPT = os.path.join(ROOT, "results", "etf_nobond_vt.json")

CONTROL = {"rebal": 20, "n_hold": 5, "cost": 0.0010, "vol_target": 0.08}
CONTROL_CAGR_TOL = 5e-4          # 0.05pp: a reproduction, not a re-estimate
FREE_COST_PP = 0.25              # giving back <= 0.25pp/yr is not a toll
BARS_PER_COHORT = 60.0
COHORTS_MAX = 4

# one knob at a time, everything else at the control value
LEVERS = [
    ("n_hold", [3, 5, 8, 10]),
    ("rebal", [10, 20, 40]),
    ("vol_target", [None, 0.08, 0.10]),
]


def sha16(path: str) -> str:
    with io.open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def cohorts_of(n_bars: int) -> int:
    """A cohort is 60 bars. Floor, capped at 4: an under-filled year is partial."""
    return max(1, min(COHORTS_MAX, int(n_bars // BARS_PER_COHORT)))


def yearly_rows(ser: pd.Series) -> dict:
    """Calendar-year net returns on the PUBLISHED definition.

    The year's own first and last level (etf_book_year_gate.yearly_returns, which
    is what etf_equity_alpha.stats2 publishes), imported rather than restated.
    Re-deriving it here with a different cut is exactly how two receipts end up
    quoting two different top-2 shares for one book (r1450 class).
    """
    raw = YG.yearly_returns(ser)
    return {y: {"net_pct": round(float(v["net_pct"]), 4),
                "cohorts": cohorts_of(int(v.get("bars") or 0)),
                "bars": int(v.get("bars") or 0)}
            for y, v in raw.items()}


def arm_stats(ser: pd.Series) -> dict:
    m = A.stats2(ser, "arm")
    return {
        "cagr_pct": round(float(m.get("cagr", float("nan"))) * 100.0, 4),
        "sharpe": round(float(m.get("sharpe", float("nan"))), 4),
        "maxdd_pct": round(float(m.get("maxdd", float("nan"))) * 100.0, 4),
    }


def gate_of(years: dict, capacity_cny=None) -> dict:
    """Re-issue the frozen calendar gate on rows this file derived itself."""
    rows = G._year_rows(years)
    y = G.year_checks(rows, capacity_cny)
    return {"verdict": G.verdict(y), "metrics": y["metrics"], "checks": y["checks"],
            "years": rows}


def row_result(label: str, lever: str, value, ser: pd.Series, turn: float,
               control_cagr: float) -> dict:
    years = yearly_rows(ser)
    g = gate_of(years)
    st = arm_stats(ser)
    return {
        "arm": label,
        "lever": lever,
        "value": value,
        "cagr_pct": st["cagr_pct"],
        "sharpe": st["sharpe"],
        "maxdd_pct": st["maxdd_pct"],
        "turnover": round(float(turn), 6),
        "delta_cagr_pp": round(st["cagr_pct"] - control_cagr, 4),
        "verdict": g["verdict"],
        "checks": g["checks"],
        "year_metrics": g["metrics"],
        "years": g["years"],
        "cohorts_left_this_year": 4 - int(g["years"][-1]["cohorts"]) if g["years"] else None,
        "top2_distance_pp": (None if g["metrics"]["top2_share"] is None
                             else round((g["metrics"]["top2_share"] - G.TOP2_SHARE_MAX) * 100.0, 4)),
    }


def published_yearly_rows() -> dict | None:
    """The control book's own calendar-year rows from the published year gate."""
    p = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as f:
        rec = json.load(f)
    for b in rec.get("books", []):
        if b.get("book") == "nobond_vt08_adopted":
            return {str(y): round(float(v), 4)
                    for y, v in (b.get("yearly_returns_pct") or {}).items()} or None
    return None


def summarize(control: dict, arms: list[dict]) -> dict:
    if control.get("cagr_pct") is None or not np.isfinite(control["cagr_pct"]):
        return {"verdict": "CONTROL_FAILED",
                "sentence": "the control arm did not reproduce the published book; nothing is claimed"}
    admits = [a for a in arms if a["verdict"] == "ADMIT"]
    # "free" is risk-adjusted, not raw: an arm that buys the gate by taking on more
    # drawdown is a toll even when its CAGR is higher (r1449: rulers do not add).
    free = [a for a in admits
            if a["delta_cagr_pp"] >= -FREE_COST_PP and a["sharpe"] >= control["sharpe"]]
    if free:
        best = max(free, key=lambda a: (a["sharpe"], a["cagr_pct"]))
        return {
            "verdict": "Y4_PASSABLE_WITHOUT_A_TOLL",
            "sentence": ("%s=%r passes Y4 with CAGR %+.2fpp and Sharpe %.3f (vs %.3f), "
                         "top-2 %.4f, maxdd %.2f%% (vs %.2f%%)"
                         % (best["lever"], best["value"], best["delta_cagr_pp"],
                            best["sharpe"], control["sharpe"],
                            best["year_metrics"]["top2_share"], best["maxdd_pct"],
                            control["maxdd_pct"])),
            "best_arm": best["arm"],
            "n_admit": len(admits),
            "n_admit_free": len(free),
        }
    if admits:
        best = max(admits, key=lambda a: a["cagr_pct"])
        return {
            "verdict": "Y4_PASSABLE_AT_A_TOLL",
            "sentence": ("only %.2fpp/yr or worse buys Y4 (%s=%r, top-2 %.4f)"
                         % (-best["delta_cagr_pp"], best["lever"], best["value"],
                            best["year_metrics"]["top2_share"])),
            "best_arm": best["arm"],
            "n_admit": len(admits),
            "n_admit_free": 0,
        }
    nearest = None
    if arms:
        cand = [a for a in arms if a["top2_distance_pp"] is not None]
        if cand:
            nearest = min(cand, key=lambda a: abs(a["top2_distance_pp"]))
    return {
        "verdict": "NO_LEVER_PASSES",
        "sentence": ("no single knob clears Y4; nearest is %s=%r at %.4f top-2 (%.2fpp over)"
                     % (nearest["lever"], nearest["value"],
                        nearest["year_metrics"]["top2_share"], nearest["top2_distance_pp"])
                     if nearest else "no arm published a top-2 share"),
        "nearest_arm": nearest["arm"] if nearest else None,
        "n_admit": 0,
        "n_admit_free": 0,
    }


def run() -> int:
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    print("bond-free universe %d (flips repaired %d)" % (len(cols), n_flip), flush=True)

    def burn(**kw):
        p = dict(CONTROL)
        p.update(kw)
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                          p["rebal"], p["n_hold"], p["cost"],
                                          vol_target=p["vol_target"])
        return ser, turn, p

    # ---- control: must reproduce the published book before anything is claimed
    ser, turn, _p = burn()
    control = row_result("control", "none", None, ser, turn, float("nan"))
    published_cagr = None
    if os.path.exists(CONTROL_RECEIPT):
        with io.open(CONTROL_RECEIPT, encoding="utf-8") as f:
            rec = json.load(f)
        for r in rec.get("runs", []):
            if r.get("label") == "nobond_vt08":
                published_cagr = float(r["cagr"]) * 100.0
                break
    control["published_cagr_pct"] = (None if published_cagr is None
                                     else round(published_cagr, 4))
    # A CAGR match alone is too weak to identify a book: r1450 showed two different
    # constructions share the headline. Re-derive this arm's calendar-year rows and
    # require them to equal the published ones before any lever is priced.
    pub_years = published_yearly_rows()
    control["published_yearly_pct"] = pub_years
    year_gaps = {}
    for y, want in (pub_years or {}).items():
        got = next((r["net_pct"] for r in control["years"] if r["year"] == y), None)
        if got is None:
            year_gaps[y] = None
        elif abs(got - want) > 1e-2:
            year_gaps[y] = round(got - want, 4)
    control["published_year_gaps_pp"] = year_gaps
    control["reproduces_published"] = (
        published_cagr is not None
        and abs(control["cagr_pct"] - published_cagr) <= CONTROL_CAGR_TOL * 100
        and bool(pub_years) and not year_gaps)
    # deltas are measured against this run's control, not the receipt
    control["delta_cagr_pp"] = 0.0
    print("control cagr %.4f vs published %r reproduces=%s"
          % (control["cagr_pct"], published_cagr, control["reproduces_published"]), flush=True)
    if not control["reproduces_published"]:
        print("[ABORT] control does not reproduce the published nobond_vt08 book", flush=True)

    arms = []
    if control["reproduces_published"]:
        for lever, values in LEVERS:
            for v in values:
                if v == CONTROL[lever]:
                    continue          # the control arm already covers this cell
                ser_a, turn_a, _ = burn(**{lever: v})
                r = row_result("%s=%r" % (lever, v), lever, v, ser_a, turn_a,
                               control["cagr_pct"])
                arms.append(r)
                print("  %-18s %-10s cagr %7.4f (%+6.2fpp) sharpe %5.3f top2 %s %s"
                      % (r["arm"], r["verdict"], r["cagr_pct"], r["delta_cagr_pp"],
                         r["sharpe"], r["year_metrics"]["top2_share"], r["verdict"]),
                      flush=True)

    s = summarize(control, arms)

    # A lever that trades more often has to survive a cost shock: the free band is
    # measured at 10bp/side, so double it on the arm the verdict would recommend.
    stress = None
    best_arm = s.get("best_arm")
    if best_arm and best_arm != "control":
        best = next((a for a in arms if a["arm"] == best_arm), None)
        if best is not None:
            ser_s, turn_s, _ = burn(cost=CONTROL["cost"] * 2.0,
                                    **{best["lever"]: best["value"]})
            stress = row_result(best_arm + "@20bp", best["lever"], best["value"], ser_s,
                                turn_s, control["cagr_pct"])
            print("  cost stress %-14s %-10s cagr %7.4f top2 %s %s"
                  % (stress["arm"], stress["verdict"], stress["cagr_pct"],
                     stress["year_metrics"]["top2_share"], stress["verdict"]), flush=True)

    s["cost_stress_arm"] = stress["arm"] if stress else None
    s["cost_stress_verdict"] = stress["verdict"] if stress else None
    s["cost_stress_survives"] = bool(stress and stress["verdict"] == "ADMIT")
    if stress is not None and not s["cost_stress_survives"]:
        s["sentence"] += ("; but at 20bp/side the same arm is %s (top-2 %.4f) -- the pass"
                          " depends on the cost assumption, not only on the lever"
                          % (stress["verdict"], stress["year_metrics"]["top2_share"]))

    out = {
        "face": "etf_book_concentration_levers",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": "which single sizing knob, if any, buys the top-2 concentration gate?",
        "rule": {
            "source": "scripts/candidate_year_gate.py (imported, not transcribed)",
            "checks": ["Y1_positive_years_share", "Y2_median_positive",
                       "Y3_worst_year", "Y4_top2_share"],
            "top2_share_max": G.TOP2_SHARE_MAX,
            "free_cost_pp": FREE_COST_PP,
            "cohort": "60 bars ~= 2.9 months; partial year = cohorts < 4",
            "note": "one knob at a time off the control cell; the gate never annualises a partial year",
        },
        "control": control,
        "arms": arms,
        "cost_stress": stress,
        "summary": s,
        "honest": [
            "no arm is a forecast: a yearly row is that arm's own realised return",
            "the 2026 row is partial and counted raw, so a lever can pass today and fail after the next cohort",
            "width, rebalance and vol target are priced one at a time; interactions are not claimed here",
            "a passing arm that drops CAGR is still a toll, printed in delta_cagr_pp",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("[run] %s | %s" % (s["verdict"], s["sentence"]), flush=True)
    print("saved", OUT, flush=True)
    return 0 if control["reproduces_published"] else 1


def check() -> int:
    """Re-derive every published verdict from the receipt's own rows."""
    if not os.path.exists(OUT):
        print("[check] no receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        rec = json.load(f)
    errs = []
    for a in ([rec["control"]] + rec["arms"]
              + ([rec["cost_stress"]] if rec.get("cost_stress") else [])):
        g = gate_of({r["year"]: {"net_pct": r["net_pct"], "cohorts": r["cohorts"]}
                     for r in a["years"]})
        if g["verdict"] != a["verdict"]:
            errs.append("%s: verdict %s != re-derived %s" % (a["arm"], a["verdict"], g["verdict"]))
        for k, v in g["checks"].items():
            if bool(v) != bool(a["checks"][k]):
                errs.append("%s: %s %r != re-derived %r" % (a["arm"], k, a["checks"][k], v))
    s2 = summarize(rec["control"], rec["arms"])
    if s2["verdict"] != rec["summary"]["verdict"]:
        errs.append("summary verdict %s != re-derived %s"
                    % (rec["summary"]["verdict"], s2["verdict"]))
    if not rec["control"].get("reproduces_published"):
        errs.append("control did not reproduce the published book")
    st = rec.get("cost_stress")
    if rec["summary"].get("cost_stress_arm") and st is None:
        errs.append("summary claims a cost-stress arm but none is published")
    if bool(rec["summary"].get("cost_stress_survives")) != bool(st and st["verdict"] == "ADMIT"):
        errs.append("the cost-stress survival flag disagrees with the published arm")
    if errs:
        for e in errs:
            print("[check] DRIFT", e)
        return 1
    print("[check] CHECK_OK  verdict=%s  arms=%d  control_cagr=%.4f"
          % (rec["summary"]["verdict"], len(rec["arms"]), rec["control"]["cagr_pct"]))
    return 0


def _synth_ser(yearly_pct: dict) -> pd.Series:
    """Build a level curve whose calendar-year returns are exactly yearly_pct."""
    idx, lvl, level = [], [], 1.0
    for y, p in yearly_pct.items():
        n = 250
        end = level * (1.0 + p / 100.0)
        step = (end / level) ** (1.0 / (n - 1))
        days = pd.date_range("%s-01-01" % y, "%s-12-31" % y, periods=n)
        # the year's FIRST bar is the level it inherits, so the published
        # last/first definition reproduces the injected return exactly
        for i, _d in enumerate(days):
            idx.append(_d)
            lvl.append(level * (step ** i))
        level = end
    return pd.Series(lvl, index=pd.DatetimeIndex(idx)).sort_index()


def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # A yearly rows compound to the headline and are not annualised.
    # The first year is measured from the curve's first published level (exactly what
    # open_to_open_equity publishes), so it carries one bar of the injected return less.
    s = _synth_ser({"2020": 10.0, "2021": -5.0, "2022": 20.0})
    rows = yearly_rows(s)
    leg("A three years, three rows", len(rows) == 3, rows)
    leg("B every year matches its injected return",
        abs(rows["2020"]["net_pct"] - 10.0) < 1e-2
        and abs(rows["2021"]["net_pct"] - -5.0) < 1e-2
        and abs(rows["2022"]["net_pct"] - 20.0) < 1e-2,
        [rows[y]["net_pct"] for y in ("2020", "2021", "2022")])
    leg("C the first year starts at the first published level",
        abs(rows["2020"]["net_pct"] - 10.0) < 1e-2, rows["2020"]["net_pct"])

    # D cohorts: a full year is 4, a short year is partial
    leg("D full year has 4 cohorts", cohorts_of(250) == 4, cohorts_of(250))
    leg("E short year is partial", cohorts_of(150) == 2, cohorts_of(150))
    leg("F a one-bar year is still one cohort", cohorts_of(1) == 1, cohorts_of(1))

    # G the gate flips exactly at the frozen line, and only there
    gate_pass = gate_of({"2020": {"net_pct": 20, "cohorts": 4},
                         "2021": {"net_pct": 20, "cohorts": 4},
                         "2022": {"net_pct": 10, "cohorts": 4},
                         "2023": {"net_pct": 10, "cohorts": 4},
                         "2024": {"net_pct": 10, "cohorts": 4},
                         "2025": {"net_pct": 10, "cohorts": 4},
                         "2026": {"net_pct": 10, "cohorts": 4}})
    leg("G a 60/120 book passes Y4", gate_pass["checks"]["Y4_top2_share"], gate_pass["checks"])
    gate_fail = gate_of({"2020": {"net_pct": 50, "cohorts": 4},
                         "2021": {"net_pct": 40, "cohorts": 4},
                         "2022": {"net_pct": 5, "cohorts": 4},
                         "2023": {"net_pct": 5, "cohorts": 4},
                         "2024": {"net_pct": 5, "cohorts": 4},
                         "2025": {"net_pct": 5, "cohorts": 4},
                         "2026": {"net_pct": 5, "cohorts": 4}})
    leg("H a 90/125 book fails Y4", not gate_fail["checks"]["Y4_top2_share"], gate_fail["checks"])
    leg("I failing Y4 alone still reads CONDITIONAL",
        gate_fail["verdict"] == "CONDITIONAL", gate_fail["verdict"])

    # J a partial year is counted raw, never annualised
    part = gate_of({"2025": {"net_pct": 10, "cohorts": 4},
                    "2026": {"net_pct": 1, "cohorts": 1}})
    leg("J partial year counted raw", part["years"][-1]["net_pct"] == 1.0, part["years"][-1])

    # K summary never reads a control failure as progress
    bad = {"cagr_pct": float("nan"), "verdict": "ADMIT"}
    leg("K control failure wins", summarize(bad, [])["verdict"] == "CONTROL_FAILED")

    # L a passing arm inside the free band is a pass without a toll
    ctrl = {"cagr_pct": 10.0, "sharpe": 1.10, "maxdd_pct": -10.0, "verdict": "CONDITIONAL"}
    arm = {"arm": "n_hold=8", "lever": "n_hold", "value": 8, "cagr_pct": 9.9,
           "delta_cagr_pp": -0.1, "verdict": "ADMIT", "sharpe": 1.20, "maxdd_pct": -10.0,
           "year_metrics": {"top2_share": 0.65}, "top2_distance_pp": -5.0}
    leg("L free pass is named", summarize(ctrl, [arm])["verdict"] == "Y4_PASSABLE_WITHOUT_A_TOLL")

    # M a passing arm outside the band is a toll, not a recommendation
    arm2 = dict(arm, cagr_pct=7.0, delta_cagr_pp=-3.0)
    leg("M expensive pass is a toll", summarize(ctrl, [arm2])["verdict"] == "Y4_PASSABLE_AT_A_TOLL")

    # N no admit at all is reported as such, with the nearest distance
    near = dict(arm, verdict="CONDITIONAL", year_metrics={"top2_share": 0.72},
                top2_distance_pp=2.0)
    leg("N no pass reported honestly", summarize(ctrl, [near])["verdict"] == "NO_LEVER_PASSES")

    # O years compound back to the level curve
    s2 = _synth_ser({"2020": 12.0, "2021": 8.0})
    comp = 1.0
    for r in yearly_rows(s2).values():
        comp *= 1.0 + r["net_pct"] / 100.0
    leg("O years compound to the curve", abs(comp - float(s2.iloc[-1])) < 1e-2, comp)

    ok = sum(1 for _n, o, _e in legs if o)
    for name, o, extra in legs:
        if not o:
            print("[FAIL] %s %s" % (name, extra))
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="selftest",
                    choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))