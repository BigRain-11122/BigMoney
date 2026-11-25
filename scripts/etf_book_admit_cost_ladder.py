#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""two arms pass the yearly gate by 0.32pp and 0.09pp of top-2 share -- how much
cost shock does that margin actually survive?

WHY THIS FILE EXISTS
--------------------
r1460/r1921 measured why the supply floor stays empty: every candidate book is
refused by the same calendar gate, and adding phases does not help. The last
remaining claim on the table is that a *lever* can buy the gate:
`etf_book_concentration_levers` prints two ADMIT arms (rebal=10 at top-2 0.6968,
vol_target=None at 0.6991) against a 0.70 line.

Both pass by less than a third of one point. The published face cost-stressed
only the arm its own summary recommended (rebal=10 -> CONDITIONAL at 20bp). The
other ADMIT arm -- the one whose CAGR is 4pp higher (15.18% vs 11.16% control) --
was never priced against cost at all, and neither arm was ever priced past 20bp.

This file prices every gate-passing arm (plus the nearest non-passing ones) on a
cost ladder, and answers one question: is the pass a property of the lever, or of
the 10bp cost assumption the whole yard is calibrated on?

Readings are honest by construction:
  * the 10bp rung is not re-estimated here: it is taken from the published arm and
    the rung is marked as such (a self-computed 10bp number could quietly disagree
    with the face it is qualifying);
  * every other rung re-derives its yearly rows from its own equity curve, so a
    difference is a difference in the cost, never in the gate;
  * the gate, the yearly definition and the stats are imported, not transcribed;
  * a max drawdown that widens is printed next to every pass, because buying the
    gate with a larger drawdown is a toll even when the verdict says ADMIT.

self  python scripts/etf_book_admit_cost_ladder.py selftest    # synthetic, fast
run   python scripts/etf_book_admit_cost_ladder.py run         # real panel, minutes
check python scripts/etf_book_admit_cost_ladder.py check       # re-derive from receipt
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

import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import candidate_year_gate as G
import etf_book_year_gate as YG

OUT = os.path.join(ROOT, "results", "etf_book_admit_cost_ladder.json")
PUBLISHED = os.path.join(ROOT, "results", "etf_book_concentration_levers.json")
CONTROL_RECEIPT = os.path.join(ROOT, "results", "etf_nobond_vt.json")

CONTROL = {"rebal": 20, "n_hold": 5, "cost": 0.0010, "vol_target": 0.08}
CONTROL_CAGR_TOL = 5e-4          # 0.05pp: a reproduction, not a re-estimate
BARS_PER_COHORT = 60.0
COHORTS_MAX = 4
LADDER_BP = [10, 20, 30]         # per side; 10bp is the yard's own calibration
NEAR_MISS_PP = 0.04              # a non-passing arm within 4pp of the line is priced
MAX_ARMS = 4                     # keeps a round bounded; the receipt names any drop


# --------------------------------------------------------------------------- gate
def cohorts_of(n_bars: int) -> int:
    return max(1, min(COHORTS_MAX, int(n_bars // BARS_PER_COHORT) + (1 if n_bars % BARS_PER_COHORT else 0)))


def yearly_rows(ser: pd.Series) -> dict:
    raw = YG.yearly_returns(ser)
    return {y: {"net_pct": round(float(v["net_pct"]), 4),
                "cohorts": cohorts_of(int(v.get("bars") or 0)),
                "bars": int(v.get("bars") or 0)}
            for y, v in raw.items()}


def gate_of(years: dict, capacity_cny=None) -> dict:
    """Re-issue the frozen calendar gate on rows this file derived itself."""
    rows = G._year_rows(years)
    y = G.year_checks(rows, capacity_cny)
    return {"verdict": G.verdict(y), "metrics": y["metrics"], "checks": y["checks"], "years": rows}


def rung(label: str, lever: str, value, cost_bp: float, ser: pd.Series, turn: float,
         source: str) -> dict:
    years = yearly_rows(ser)
    g = gate_of(years)
    st = A.stats2(ser, "arm")
    top2 = g["metrics"]["top2_share"]
    return {
        "arm": label,
        "lever": lever,
        "value": value,
        "cost_bp_per_side": cost_bp,
        "source": source,
        "verdict": g["verdict"],
        "checks": g["checks"],
        "top2_share": top2,
        "top2_distance_pp": (None if top2 is None
                             else round((top2 - G.TOP2_SHARE_MAX) * 100.0, 4)),
        "cagr_pct": round(float(st.get("cagr", float("nan"))) * 100.0, 4),
        "sharpe": round(float(st.get("sharpe", float("nan"))), 4),
        "maxdd_pct": round(float(st.get("maxdd", float("nan"))) * 100.0, 4),
        "turnover": round(float(turn), 6),
        "years": g["years"],
    }


# ------------------------------------------------------------------ verdict logic
def verdict_of(ladder: list[dict], not_selected: list[str] | None = None) -> dict:
    """What the ladder says, derived only from the rungs it actually holds."""
    by_arm: dict[str, list[dict]] = {}
    for r in ladder:
        by_arm.setdefault(r["arm"], []).append(r)
    arms_out = []
    for arm, rungs in sorted(by_arm.items()):
        rungs = sorted(rungs, key=lambda r: r["cost_bp_per_side"])
        passing = [r["cost_bp_per_side"] for r in rungs if r["verdict"] == "ADMIT"]
        best = max(passing) if passing else None
        r10 = next((r for r in rungs if r["cost_bp_per_side"] == 10), None)
        r20 = next((r for r in rungs if r["cost_bp_per_side"] == 20), None)
        arms_out.append({
            "arm": arm,
            "lever": rungs[0]["lever"],
            "value": rungs[0]["value"],
            "passing_costs_bp": passing,
            "survives_20bp": bool(r20 and r20["verdict"] == "ADMIT"),
            "highest_passing_bp": best,
            "top2_at_10bp": r10["top2_share"] if r10 else None,
            "top2_at_20bp": r20["top2_share"] if r20 else None,
            "top2_moved_pp_10_to_20": (None if not (r10 and r20)
                                       or r10["top2_share"] is None or r20["top2_share"] is None
                                       else round((r20["top2_share"] - r10["top2_share"]) * 100.0, 4)),
            "maxdd_at_10bp": r10["maxdd_pct"] if r10 else None,
            "maxdd_at_20bp": r20["maxdd_pct"] if r20 else None,
            "cagr_at_20bp": r20["cagr_pct"] if r20 else None,
        })
    survivors = [a["arm"] for a in arms_out if a["survives_20bp"]]
    robust = [a["arm"] for a in arms_out if 30 in a["passing_costs_bp"]]
    line_pct = G.TOP2_SHARE_MAX * 100.0
    passed_at_10 = [a for a in arms_out if a["top2_at_10bp"] is not None
                    and a["top2_at_10bp"] <= G.TOP2_SHARE_MAX]
    near = [a for a in arms_out if a not in passed_at_10]
    if not arms_out:
        word = "NO_ARMS_PRICED"
        sentence = "no gate-passing arm was available to price; the ladder says nothing"
    elif survivors:
        word = "ADOPTABLE_AT_20BP"
        sentence = ("%s still passes at 20bp/side; the gate can be bought by a lever, "
                    "not only by waiting" % " and ".join(survivors))
    else:
        word = "PASS_IS_A_COST_ASSUMPTION"
        flips = "; ".join("%s %.4f -> %.4f" % (a["arm"], a["top2_at_10bp"], a["top2_at_20bp"])
                          for a in passed_at_10 if a["top2_at_20bp"] is not None)
        margins = ", ".join("%.2f" % (line_pct - a["top2_at_10bp"] * 100.0)
                            for a in passed_at_10)
        sentence = ("every arm that clears the top-2 line at 10bp flips at 20bp/side (%s); "
                    "those passes were margins of %s pp against a %.2f line -- the pass "
                    "belongs to the 10bp cost, not to the lever"
                    % (flips or "none", margins or "none", line_pct / 100.0))
        if near:
            sentence += ("; the near misses it also priced (%s) never cleared the line at any cost"
                         % ", ".join("%s %.4f" % (a["arm"], a["top2_at_20bp"])
                                     for a in near if a["top2_at_20bp"] is not None))
    return {
        "verdict": word,
        "sentence": sentence,
        "arms": arms_out,
        "n_arms": len(arms_out),
        "n_survive_20bp": len(survivors),
        "survivors_20bp": survivors,
        "robust_at_30bp": robust,
        "not_selected": not_selected or [],
    }


# --------------------------------------------------------------------------- data
def panel():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], sc, n_flip


def published_arms() -> list[dict]:
    if not os.path.exists(PUBLISHED):
        return []
    with io.open(PUBLISHED, encoding="utf-8") as f:
        rec = json.load(f)
    rows = []
    for a in rec.get("arms", []):
        ym = a.get("year_metrics") or {}
        rows.append({"arm": a["arm"], "lever": a.get("lever"), "value": a.get("value"),
                     "verdict": a.get("verdict"), "top2_share": ym.get("top2_share"),
                     "cagr_pct": a.get("cagr_pct"), "maxdd_pct": a.get("maxdd_pct")})
    return rows


def select_arms(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Every ADMIT arm plus the nearest refusals, capped so a round stays bounded.

    The second return value names every arm that did not make the ladder -- both
    the ones too far from the line to price and the ones cut by the bound -- so a
    reader can tell "not priced" from "priced and refused".
    """
    admits = [r for r in rows if r["verdict"] == "ADMIT"]
    near = [r for r in rows if r["verdict"] != "ADMIT"
            and r["top2_share"] is not None
            and r["top2_share"] <= G.TOP2_SHARE_MAX + NEAR_MISS_PP]
    near.sort(key=lambda r: r["top2_share"])
    chosen = admits + near
    not_selected = [r["arm"] for r in rows if r["arm"] not in {c["arm"] for c in chosen}]
    if len(chosen) > MAX_ARMS:
        not_selected = [r["arm"] for r in chosen[MAX_ARMS:]] + not_selected
        chosen = chosen[:MAX_ARMS]
    return chosen, not_selected


def published_ten_bp(arm: dict) -> dict | None:
    """The 10bp rung is read from the face that published it, never re-estimated."""
    if arm.get("top2_share") is None:
        return None
    return {"top2_share": arm["top2_share"], "cagr_pct": arm["cagr_pct"],
            "maxdd_pct": arm["maxdd_pct"], "verdict": arm["verdict"]}


# ---------------------------------------------------------------------------- run
def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = panel()
    print("bond-free universe %d (flips repaired %d)" % (len(close.columns), n_flip), flush=True)

    def burn(**kw):
        p = dict(CONTROL)
        p.update(kw)
        ser, turn = R.open_to_open_equity(close, openp, amt, sc,
                                          p["rebal"], p["n_hold"], p["cost"],
                                          vol_target=p["vol_target"])
        return ser, turn, p

    # ---- control reproduction: same identification rule as the face we qualify
    ser, turn, _ = burn()
    control = rung("control", "none", None, 10.0, ser, turn, "computed")
    published_cagr = None
    if os.path.exists(CONTROL_RECEIPT):
        with io.open(CONTROL_RECEIPT, encoding="utf-8") as f:
            rec = json.load(f)
        for r in rec.get("runs", []):
            if r.get("label") == "nobond_vt08":
                published_cagr = float(r["cagr"]) * 100.0
                break
    control["published_cagr_pct"] = None if published_cagr is None else round(published_cagr, 4)
    reproduces = (published_cagr is not None
                  and abs(control["cagr_pct"] - published_cagr) <= CONTROL_CAGR_TOL * 100)
    control["reproduces_published"] = bool(reproduces)
    print("control cagr %.4f vs published %r reproduces=%s"
          % (control["cagr_pct"], published_cagr, reproduces), flush=True)
    if not reproduces:
        print("[ABORT] control does not reproduce the published book", flush=True)

    rows = published_arms()
    chosen, not_selected = select_arms(rows)
    print("arms selected %d (%s), not priced %s"
          % (len(chosen), ", ".join(r["arm"] for r in chosen), not_selected or "none"), flush=True)

    ladder = []
    if reproduces:
        for arm in chosen:
            pub10 = published_ten_bp(arm)
            if pub10 is None:
                continue
            # the 10bp rung is quoted, not recomputed
            ladder.append({
                "arm": arm["arm"], "lever": arm["lever"], "value": arm["value"],
                "cost_bp_per_side": 10.0, "source": "published@10bp",
                "verdict": pub10["verdict"], "checks": None,
                "top2_share": pub10["top2_share"],
                "top2_distance_pp": round((pub10["top2_share"] - G.TOP2_SHARE_MAX) * 100.0, 4),
                "cagr_pct": pub10["cagr_pct"], "sharpe": None,
                "maxdd_pct": pub10["maxdd_pct"], "turnover": None, "years": None,
            })
            for bp in LADDER_BP:
                if bp == 10:
                    continue
                ser_a, turn_a, _ = burn(cost=bp / 10000.0, **{arm["lever"]: arm["value"]})
                r = rung(arm["arm"], arm["lever"], arm["value"], float(bp), ser_a, turn_a, "computed")
                ladder.append(r)
                print("  %-18s %2dbp %-12s cagr %7.3f top2 %s maxdd %s"
                      % (r["arm"], bp, r["verdict"], r["cagr_pct"], r["top2_share"],
                         r["maxdd_pct"]), flush=True)

    s = verdict_of(ladder, not_selected)

    out = {
        "face": "etf_book_admit_cost_ladder",
        "book_family": "nobond_vt08",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(close.index[-1].date()),
        "inputs": input_digests(),
        "question": ("the gate has two ADMIT arms that clear the top-2 line by less than a third "
                     "of a point -- is that margin a property of the lever or of the 10bp cost?"),
        "rule": {
            "gate": "scripts/candidate_year_gate.py (imported, not transcribed)",
            "yearly": "scripts/etf_book_year_gate.py::yearly_returns (imported)",
            "stats": "scripts/etf_equity_alpha.py::stats2 (imported)",
            "top2_share_max": G.TOP2_SHARE_MAX,
            "ladder_bp_per_side": LADDER_BP,
            "ten_bp_rung": "quoted from results/etf_book_concentration_levers.json, never recomputed",
            "near_miss_pp": NEAR_MISS_PP,
            "max_arms": MAX_ARMS,
            "control": dict(CONTROL),
        },
        "control": control,
        "selected_arms": [r["arm"] for r in chosen],
        "ladder": ladder,
        "summary": s,
        "honest": [
            "the 10bp rung is quoted; only the 20/30bp rungs are recomputed here, so the ladder cannot disagree with the face it qualifies at 10bp",
            "each recomputed rung re-derives its own yearly rows; a difference is a difference in cost, never in the gate",
            "the 2026 row is partial and counted raw, so a lever that passes today can fail after the next cohort",
            "a pass bought with a wider drawdown is printed with that drawdown, not hidden behind the verdict",
            "no line is moved: this file never proposes a different top-2 threshold",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("[run] %s | %s" % (s["verdict"], s["sentence"]), flush=True)
    print("saved", OUT, flush=True)
    return 0 if reproduces else 1


# -------------------------------------------------------------------------- check
def check() -> int:
    """Re-derive the verdict from the receipt's own rungs; no network, no engine."""
    if not os.path.exists(OUT):
        print("[check] missing receipt %s" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        rec = json.load(f)
    s = verdict_of(rec.get("ladder") or [], rec.get("summary", {}).get("not_selected"))
    problems = []
    if s["verdict"] != rec["summary"]["verdict"]:
        problems.append("verdict %r -> %r" % (rec["summary"]["verdict"], s["verdict"]))
    if s["n_arms"] != rec["summary"]["n_arms"]:
        problems.append("n_arms %r -> %r" % (rec["summary"]["n_arms"], s["n_arms"]))
    if s["survivors_20bp"] != rec["summary"]["survivors_20bp"]:
        problems.append("survivors %r -> %r" % (rec["summary"]["survivors_20bp"], s["survivors_20bp"]))
    # every arm that passed at 10bp must keep its quoted top-2 inside the published face
    pub = {a["arm"]: a for a in published_arms()}
    for r in rec.get("ladder") or []:
        if r.get("source") == "published@10bp":
            p = pub.get(r["arm"])
            if p is None:
                problems.append("quoted arm vanished from the published face: %s" % r["arm"])
            elif p["top2_share"] is not None and abs(p["top2_share"] - r["top2_share"]) > 1e-6:
                problems.append("quoted top-2 drifted for %s: %r vs %r"
                                % (r["arm"], r["top2_share"], p["top2_share"]))
    # r2093: the reproduction is judged against the receipt as it stands now, not
    # against the boolean this face wrote down when it last ran. A receipt rewritten
    # by its own chain leg leaves the stored flag true (or false) about a number that
    # no longer exists, and a probe that never says STALE never gets re-derived.
    ctrl = rec.get("control", {}) or {}
    live_pub = receipt_cagr()
    stored_pub = ctrl.get("published_cagr_pct")
    live_inputs = input_digests()
    if inputs_moved(rec.get("inputs"), live_inputs):
        problems.append("STALE a quoted face moved: stored %r vs now %r"
                        % (rec.get("inputs"), live_inputs))
    elif live_pub is None:
        problems.append("STALE the quoted receipt cannot be read: %s" % CONTROL_RECEIPT)
    elif quote_moved(stored_pub, live_pub):
        problems.append("STALE the quoted receipt moved: published %r -> %.4f"
                        % (stored_pub, live_pub))
    elif abs(float(ctrl.get("cagr_pct") or float("nan")) - live_pub) > CONTROL_CAGR_TOL * 100:
        problems.append("control does not reproduce the published book (%.4f vs %.4f)"
                        % (ctrl.get("cagr_pct"), live_pub))
    elif not ctrl.get("reproduces_published"):
        problems.append("STALE the receipt's own flag is stale: it says reproduces=False "
                        "while %.4f re-derives against the receipt" % live_pub)
    ok = not problems
    print("[check] %s | verdict=%s | n_arms=%d survivors_20bp=%s | problems=%s"
          % ("OK" if ok else "PROBLEMS", s["verdict"], s["n_arms"], s["survivors_20bp"], problems))
    return 0 if ok else 3


# ---------------------------------------------------------------------- selftest
def _synth_ser(yearly_pct: dict) -> pd.Series:
    """A daily level whose calendar-year returns are exactly yearly_pct."""
    idx = []
    vals = []
    level = 1.0
    for y, pct in yearly_pct.items():
        days = pd.date_range("%d-01-01" % y, "%d-12-31" % y, freq="D")
        n = len(days)
        ramp = [level * (1.0 + pct / 100.0 * (i / max(1, n - 1))) for i in range(n)]
        idx.extend(list(days))
        vals.extend(ramp)
        level = level * (1.0 + pct / 100.0)
    return pd.Series(vals, index=pd.DatetimeIndex(idx))


def _rung(arm, bp, top2, verdict=None, cagr=10.0, maxdd=-10.0):
    return {"arm": arm, "lever": "rebal", "value": 10, "cost_bp_per_side": float(bp),
            "source": "synthetic", "verdict": verdict or ("ADMIT" if top2 <= G.TOP2_SHARE_MAX else "CONDITIONAL"),
            "checks": None, "top2_share": top2,
            "top2_distance_pp": round((top2 - G.TOP2_SHARE_MAX) * 100.0, 4),
            "cagr_pct": cagr, "sharpe": 1.0, "maxdd_pct": maxdd, "turnover": 1.0, "years": None}


def selftest() -> int:
    fails = []

    def ok(name, cond, detail=""):
        if not cond:
            fails.append(name)
            print("  [FAIL] %s %s" % (name, detail))
        else:
            print("  [PASS] %s %s" % (name, detail))

    # L1 an arm that still passes at 20bp is named as adoptable
    s = verdict_of([_rung("rebal=10", 10, 0.69), _rung("rebal=10", 20, 0.695), _rung("rebal=10", 30, 0.71)])
    ok("L1 survives_20bp -> ADOPTABLE_AT_20BP", s["verdict"] == "ADOPTABLE_AT_20BP", s["verdict"])
    ok("L1b the arm is named", s["survivors_20bp"] == ["rebal=10"], str(s["survivors_20bp"]))
    ok("L1c 30bp is not credited", s["robust_at_30bp"] == [], str(s["robust_at_30bp"]))

    # L2 every arm flipping at 20bp is a cost assumption, not a lever
    s = verdict_of([_rung("rebal=10", 10, 0.6968), _rung("rebal=10", 20, 0.7238),
                    _rung("vol_target=None", 10, 0.6991), _rung("vol_target=None", 20, 0.7350)])
    ok("L2 all flip -> PASS_IS_A_COST_ASSUMPTION", s["verdict"] == "PASS_IS_A_COST_ASSUMPTION", s["verdict"])
    ok("L2b no survivor", s["survivors_20bp"] == [], str(s["survivors_20bp"]))
    ok("L2c margin is printed in the sentence", "0.09" in s["sentence"] or "0.3" in s["sentence"], s["sentence"][:120])

    # L3 an empty ladder says nothing rather than impersonating a pass
    s = verdict_of([])
    ok("L3 empty -> NO_ARMS_PRICED", s["verdict"] == "NO_ARMS_PRICED", s["verdict"])

    # L4 the top-2 movement between rungs is reported, not left to the reader
    s = verdict_of([_rung("a", 10, 0.6968), _rung("a", 20, 0.7100)])
    m = s["arms"][0]["top2_moved_pp_10_to_20"]
    ok("L4 movement 10->20 is 1.32pp", m is not None and abs(m - 1.32) < 1e-9, repr(m))

    # L5 the drawdown that buys a pass is carried on the arm
    s = verdict_of([_rung("a", 10, 0.6968, maxdd=-12.7), _rung("a", 20, 0.695, maxdd=-16.04)])
    ok("L5 maxdd travels with the arm", s["arms"][0]["maxdd_at_20bp"] == -16.04,
       str(s["arms"][0]["maxdd_at_20bp"]))

    # L6 cohorts floor at 1 and cap at 4
    ok("L6 cohorts", (cohorts_of(30) == 1 and cohorts_of(60) == 1 and cohorts_of(61) == 2
                      and cohorts_of(300) == 4), "")

    # L7 a synthetic yearly series reproduces its own gate word
    ser = _synth_ser({2023: 10.0, 2024: 11.0, 2025: 12.0, 2026: 6.0})
    g = gate_of(yearly_rows(ser))
    ok("L7 synthetic year rows read back", g["verdict"] in ("ADMIT", "CONDITIONAL"), g["verdict"])
    ok("L7b top-2 is computable", g["metrics"]["top2_share"] is not None, str(g["metrics"]["top2_share"]))

    # L8 selection: ADMIT arms always in, refusals only when near the line, capped
    rows = [{"arm": "a", "lever": "rebal", "value": 10, "verdict": "ADMIT", "top2_share": 0.6968,
             "cagr_pct": 11.8, "maxdd_pct": -12.7},
            {"arm": "b", "lever": "vol_target", "value": None, "verdict": "ADMIT", "top2_share": 0.6991,
             "cagr_pct": 15.2, "maxdd_pct": -16.0},
            {"arm": "c", "lever": "n_hold", "value": 10, "verdict": "CONDITIONAL", "top2_share": 0.7389,
             "cagr_pct": 9.9, "maxdd_pct": -11.0},
            {"arm": "d", "lever": "n_hold", "value": 8, "verdict": "CONDITIONAL", "top2_share": 0.7738,
             "cagr_pct": 10.3, "maxdd_pct": -11.4}]
    chosen, dropped = select_arms(rows)
    ok("L8 near miss kept", [r["arm"] for r in chosen] == ["a", "b", "c"], str([r["arm"] for r in chosen]))
    ok("L8b far miss not priced", dropped == ["d"], str(dropped))

    # L9 the cap is honest about what it dropped
    rows9 = [{"arm": str(i), "lever": "x", "value": i, "verdict": "ADMIT", "top2_share": 0.69,
              "cagr_pct": 10.0, "maxdd_pct": -10.0} for i in range(6)]
    chosen9, dropped9 = select_arms(rows9)
    ok("L9 bound keeps MAX_ARMS", len(chosen9) == MAX_ARMS, str(len(chosen9)))
    ok("L9b dropped are named", len(dropped9) == 2, str(dropped9))

    # L10 only an arm that really cleared the line carries a "margin": r1928's first
    # run printed a negative margin for a near miss and read like a pass that failed
    s = verdict_of([_rung("pass", 10, 0.6968), _rung("pass", 20, 0.7835),
                    _rung("miss", 10, 0.7389), _rung("miss", 20, 0.7949)])
    ok("L10 only line-clearing arms carry a margin", "margins of 0.32 pp" in s["sentence"],
       s["sentence"][:160])
    ok("L10b the near miss is named with its own number", "miss 0.7949" in s["sentence"],
       s["sentence"][:220])

    # L11 the quoted receipt is a clock of its own (r2093): a receipt rewritten under
    # the face must read STALE even when the panel has not moved, and a quote that
    # still matches must not (so the chain is not asked to pay every round).
    ok("L11 a moved receipt quote reads STALE", quote_moved(11.16, 11.11) is True,
       (11.16, 11.11))
    ok("L11b an unmoved quote reads SAME", quote_moved(11.11, 11.11) is False,
       (11.11, 11.11))
    ok("L11c an unreadable quote is not evidence of movement",
       quote_moved(None, 11.11) is False and quote_moved(11.11, None) is False,
       (None, 11.11))
    # L12 the quoted faces are compared by bytes, and a face priced before the digests
    # existed is STALE once rather than silently assumed unchanged.
    ok("L12 a moved quoted face is caught by its bytes",
       inputs_moved({"a": "1", "b": "2"}, {"a": "1", "b": "3"}) is True)
    ok("L12b identical bytes are not a move",
       inputs_moved({"a": "1", "b": "2"}, {"a": "1", "b": "2"}) is False)
    ok("L12c a face with no recorded digests re-prices once",
       inputs_moved(None, {"a": "1"}) is True and inputs_moved(None, {"a": None}) is False)

    print("selftest %d/%d PASS" % (24 - len(fails), 24) if not fails
          else "selftest %d/24 PASS, %d FAIL" % (24 - len(fails), len(fails)))
    return 0 if not fails else 1


# ------------------------------------------------------------------------ refresh
def panel_last_bar():
    close, openp, amt, feats = E.build_panel()
    return str(close.index[-1].date())


def receipt_cagr():
    """The control CAGR the quoted receipt states right now (None if unreadable).

    r2093: this face reproduces `results/etf_nobond_vt.json`, and that receipt is
    rewritten by its own chain leg -- so the panel is not the only clock this face
    runs on. On 2026-11-25 the panel had not moved (11-24) but the receipt had
    (11.16 -> 11.11): every probe said SAME, the face kept a quote nobody could
    reproduce, and the ladder priced no arm who knows how many rounds.
    """
    if not os.path.exists(CONTROL_RECEIPT):
        return None
    try:
        with io.open(CONTROL_RECEIPT, encoding="utf-8") as f:
            rec = json.load(f)
        for r in rec.get("runs", []):
            if r.get("label") == "nobond_vt08":
                return float(r["cagr"]) * 100.0
    except Exception:
        return None
    return None


def quote_moved(stored, live):
    """True when the quoted number is no longer the number the receipt states."""
    if stored is None or live is None:
        return False
    return abs(float(live) - float(stored)) > 1e-4


def _sha256(path):
    try:
        with io.open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def input_digests():
    """Both faces this ladder quotes, by content rather than by date (r2093)."""
    return {"published_arms": _sha256(PUBLISHED), "control_receipt": _sha256(CONTROL_RECEIPT)}


def inputs_moved(stored, live):
    """True when either quoted face is not the one this ladder was priced on.

    A receipt keeps its cutoff while its numbers move (a cost model is re-estimated),
    so the date alone cannot answer this -- the bytes have to.
    """
    if not isinstance(stored, dict):
        # nothing recorded is not a reproduction: an older face was priced before the
        # digests existed, and this run is what records them (one-time cost).
        return isinstance(live, dict) and any(live.values())
    for k, v in live.items():
        if stored.get(k) and v and stored[k] != v:
            return True
    return False


def refresh() -> int:
    had = None
    had_pub = None
    if os.path.exists(OUT):
        try:
            with io.open(OUT, encoding="utf-8") as f:
                rec = json.load(f)
            had = rec.get("evidence_cutoff")
            had_pub = (rec.get("control") or {}).get("published_cagr_pct")
        except Exception:
            had = None
    live = panel_last_bar()
    live_pub = receipt_cagr()
    recorded = None
    if os.path.exists(OUT):
        try:
            with io.open(OUT, encoding="utf-8") as f:
                recorded = json.load(f).get("inputs")
        except Exception:
            recorded = None
    live_inputs = input_digests()
    if not had or not live:
        print("REFRESH_UNKNOWN receipt=%s panel=%s; leaving the face as it stands" % (had, live))
        return 2
    moved = quote_moved(had_pub, live_pub)
    moved_inputs = inputs_moved(recorded, live_inputs)
    if str(had) >= str(live) and not moved and not moved_inputs:
        print("REFRESH_NOOP evidence_cutoff=%s (the panel and both quoted faces are unmoved)"
              % live)
        return 0
    if moved_inputs:
        print("REFRESH_STALE a quoted face moved since this ladder was priced: %r -> %r"
              % (recorded, live_inputs))
    if moved:
        print("REFRESH_STALE the quoted receipt moved: published %r -> %.4f"
              % (had_pub, live_pub))
    started = time.time()
    rc = run()
    print("REFRESH_RAN %s -> %s (%.1fs) rc=%d" % (had, live, time.time() - started, rc))
    return rc


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "refresh"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "refresh":
        return refresh()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
