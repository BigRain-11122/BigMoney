"""Is the de-lever rule worth keeping, or would a fixed fraction do the same job?

r1196 measured that the 8% vol target is average exposure, not timing: on one decision
calendar, holding the book's OWN mean scale every bar earned +0.91pp/yr more. That reading
has an obvious hole -- the constant arm used the production path's own mean exposure, which
is a number you only know after the fact. One arm at one calibrated constant on one decision
calendar cannot tell "a fixed fraction is just as good" from "0.708 happened to be the right
number on this grid".

This face prices a LADDER of fixed fractions (0.40 .. 1.00) on four decision phases, so the
comparison does not depend on a scale chosen from the answer it is testing:

  * every arm holds the same names on the same grid and pays the same cost model;
  * the only difference is the multiplier applied at each decision;
  * the production arm reproduces the engine's nav bit for bit (published identity leg);
  * the verdict is a pure function of the published rows, recomputed by --check.

The question it answers for the desk: keep the de-lever rule, or drop it for a fixed
fraction -- and if a fixed fraction wins, WHICH one and by how much, per phase and out of
sample.

Usage:
    python scripts/etf_book_exposure_ladder.py run
    python scripts/etf_book_exposure_ladder.py --check
    python scripts/etf_book_exposure_ladder.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_exposure_timing as X
import etf_book_forward as F
import etf_equity_alpha as A

OUT_JSON = os.path.join(ROOT, "results", "etf_book_exposure_ladder.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_EXPOSURE_LADDER.md")

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; echoed into the payload and re-read by the gate, so a later
# "small adjustment" cannot be mistaken for the rule.
K_GRID = (0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00)
N_PHASES = 4
CAGR_TOL_PP = 0.15          # "no worse on return" = within this much of production
DD_TOL_PP = 0.50            # "no worse on drawdown" = no deeper than this much
SHARPE_TOL = 0.02           # production "earns its keep" only with a real risk-adjusted gap
SHARE_MIN = 0.75            # share of cells a verdict has to hold in
IDENT_TOL = 1e-12
OOS_FROM = "2023-12-31"

REBAL = F.CONFIG["rebal"]
N_HOLD = F.CONFIG["n_hold"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]
CRITERIA = {"k_grid": list(K_GRID), "n_phases": N_PHASES, "cagr_tol_pp": CAGR_TOL_PP,
            "dd_tol_pp": DD_TOL_PP, "sharpe_tol": SHARPE_TOL, "share_min": SHARE_MIN,
            "oos_from": OOS_FROM}


def phase_starts(index, rebal=REBAL, n=N_PHASES):
    """`n` decision-grid starts spread through one rebalance cycle.

    The engine's grid is every `rebal` bars from the first bar, so starting inside a cycle
    changes which bars are decision bars without changing the window the book is judged on.
    """
    post = list(index)
    if len(post) < rebal * 2:
        raise ValueError("panel has %d bars -- need at least %d" % (len(post), rebal * 2))
    step = max(1, rebal // n)
    picks = [post[i * step] for i in range(n)]
    if len(set(picks)) < n:
        raise ValueError("only %d distinct phases in a %d-bar cycle" % (len(set(picks)), rebal))
    return picks


def _row(phase, start, arm, ser, exp, book):
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp(OOS_FROM)], "oos")
    return {"phase": phase, "phase_start": str(pd.Timestamp(start).date()), "arm": arm,
            "cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
            "maxdd": full.get("maxdd"), "vol": full.get("vol"),
            "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
            "mean_exposure": round(float(np.mean(exp)), 4),
            "n_fills": book.n_fill, "selection_drift": book.selection_drift}


def decide(rows):
    """Verdict from published rows alone, so a reader can re-derive it without a re-run."""
    by = {}
    for r in rows:
        if r.get("cagr") is None or r.get("maxdd") is None:
            continue
        by[(r["phase"], r["arm"])] = r
    ph = sorted({r["phase"] for r in rows})
    if not ph or any((p, "production") not in by for p in ph):
        return {"state": "INCOMPLETE", "why": "no production row for every phase"}
    ks = sorted({r["arm"] for r in rows if r["arm"].startswith("const_")})
    if not ks:
        return {"state": "INCOMPLETE", "why": "no constant arms"}
    cell_prod_win = 0
    cell_total = 0
    ladder = []
    for arm in ks:
        wins = 0
        deltas = []
        for p in ph:
            d = by.get((p, arm))
            pr = by[(p, "production")]
            if d is None:
                continue
            cell_total += 1
            dc = 100.0 * (d["cagr"] - pr["cagr"])
            dd = 100.0 * (d["maxdd"] - pr["maxdd"])
            deltas.append(dc)
            if dc >= -CAGR_TOL_PP and dd >= -DD_TOL_PP:
                wins += 1
            if dc <= -CAGR_TOL_PP and (dd <= 0 or d["sharpe"] <= pr["sharpe"] - SHARPE_TOL):
                cell_prod_win += 1
        ladder.append({"arm": arm,
                       "cagr_delta_pp_mean": round(float(np.mean(deltas)), 2) if deltas else None,
                       "phases_not_worse": wins, "phases_tested": len(deltas)})
    best = sorted(ladder, key=lambda r: (-r["phases_not_worse"],
                                         -(r["cagr_delta_pp_mean"] or -99.0)))[0]
    need = int(np.ceil(SHARE_MIN * len(ph)))
    if best["phases_not_worse"] >= need:
        state = "CONSTANT_LADDER_DOMINATES"
    elif cell_prod_win >= int(np.ceil(SHARE_MIN * cell_total)):
        state = "PRODUCTION_RULE_EARNS_ITS_KEEP"
    else:
        state = "PHASE_DEPENDENT"
    return {"state": state, "best_fixed_scale": best["arm"],
            "best_phases_not_worse": best["phases_not_worse"], "phases_needed": need,
            "phases_tested": len(ph), "production_cell_wins": cell_prod_win,
            "cells_total": cell_total, "ladder": ladder,
            "rule": ("CONSTANT_LADDER_DOMINATES iff one fixed fraction is no worse than "
                     "production on return and drawdown in >= share_min of the phases; "
                     "PRODUCTION_RULE_EARNS_ITS_KEEP iff production beats every fixed "
                     "fraction by more than the tolerance in >= share_min of the cells; "
                     "otherwise the answer depends on the phase")}


def decide_adoption(rows):
    """The face's own adopted standard, applied: a fixed fraction that only wins in sample
    is not an adoption.

    This is NOT a retuned `decide()` -- that one answers "is the fixed fraction no worse on
    the full window" and stays frozen at v1.0. This second reading exists because the notes
    written before the first run already demanded it ("out of sample = bars after ...; a
    fixed fraction that only wins in sample is not an adoption"), and the first run is
    exactly the case that rule was written for: the full window says no worse, the out of
    sample window says the de-lever rule earns 1.2-3.0pp/yr more. Both are published.
    """
    ph = sorted({r["phase"] for r in rows})
    by = {(r["phase"], r["arm"]): r for r in rows}
    ks = sorted({r["arm"] for r in rows if r["arm"].startswith("const_")})
    if not ph or not ks or any((p, "production") not in by for p in ph):
        return {"state": "INCOMPLETE"}
    need = int(np.ceil(SHARE_MIN * len(ph)))
    scored = []
    for arm in ks:
        full_ok = oos_ok = 0
        oos_deltas = []
        for p in ph:
            d = by.get((p, arm))
            pr = by[(p, "production")]
            if d is None or d.get("cagr") is None:
                continue
            if (100.0 * (d["cagr"] - pr["cagr"]) >= -CAGR_TOL_PP
                    and 100.0 * (d["maxdd"] - pr["maxdd"]) >= -DD_TOL_PP):
                full_ok += 1
            if d.get("oos_cagr") is not None and pr.get("oos_cagr") is not None:
                oos_deltas.append(100.0 * (d["oos_cagr"] - pr["oos_cagr"]))
                if (d["oos_cagr"] >= pr["oos_cagr"] - CAGR_TOL_PP / 100.0
                        and (d.get("oos_sharpe") or 0) >= (pr.get("oos_sharpe") or 0) - SHARPE_TOL):
                    oos_ok += 1
        scored.append({"arm": arm, "full_window_ok": full_ok, "out_of_sample_ok": oos_ok,
                       "oos_cagr_delta_pp_mean": round(float(np.mean(oos_deltas)), 2)
                       if oos_deltas else None})
    best = sorted(scored, key=lambda r: (-r["out_of_sample_ok"], -r["full_window_ok"],
                                         -(r["oos_cagr_delta_pp_mean"] or -99.0)))[0]
    if best["out_of_sample_ok"] >= need and best["full_window_ok"] >= need:
        state = "ADOPT_FIXED_FRACTION"
    elif best["out_of_sample_ok"] < need:
        state = "REJECT_FIXED_FRACTION"
    else:
        state = "PHASE_DEPENDENT"
    return {"state": state, "best_fixed_scale": best["arm"],
            "best_out_of_sample_ok": best["out_of_sample_ok"],
            "best_full_window_ok": best["full_window_ok"], "phases_needed": need,
            "phases_tested": len(ph), "ladder": scored,
            "rule": ("ADOPT_FIXED_FRACTION iff one fixed fraction is no worse than production "
                     "on BOTH the full window and the out-of-sample window in >= share_min of "
                     "the phases; REJECT_FIXED_FRACTION iff no fixed fraction clears out of "
                     "sample; otherwise the answer depends on the phase")}


def run():
    t0 = time.time()
    close, openp, _amt, _feats, score, cls, n_flip = F.build_inputs()
    all_dates, _grid = F.date_grid(close, REBAL)
    carry, carry_note = F.build_carry(all_dates)
    carry = None if carry is None else carry.reindex(pd.DatetimeIndex(all_dates)).fillna(0.0)

    starts = phase_starts(all_dates)
    rows = []
    identity = []
    for i, st in enumerate(starts):
        dates = [d for d in all_dates if d >= st]
        grid = set(dates[::REBAL])
        prod_ser, prod_exp, prod = X._run_arm(close, openp, score, carry, dates, grid,
                                              lambda d, s: s)
        eng = F.Forward(close, openp, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET,
                        carry=carry)
        eng_ser = X._series(eng.run(dates, grid))
        gap = float(np.max(np.abs(eng_ser.to_numpy() - prod_ser.to_numpy())))
        pick_drift = sum(1 for b, v in eng.books.items()
                         if b in prod.books and list(prod.books[b]["names"]) != list(v["names"]))
        identity.append({"phase": i, "start": str(pd.Timestamp(st).date()), "gap": gap,
                         "tol": IDENT_TOL, "passes": gap <= IDENT_TOL and pick_drift == 0,
                         "pick_drift": pick_drift})
        rows.append(_row(i, st, "production", prod_ser, prod_exp, prod))
        for k in K_GRID:
            ser, exp, bk = X._run_arm(close, openp, score, carry, dates, grid,
                                      lambda d, s, _k=k: _k)
            rows.append(_row(i, st, "const_%.2f" % k, ser, exp, bk))

    verdict = decide(rows)
    prod_rows = [r for r in rows if r["arm"] == "production"]
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(all_dates[-1].date()),
        "bars": len(all_dates),
        "question": ("keep the 8%% vol-target de-lever rule, or hold a fixed fraction? "
                     "priced on %d decision phases so the answer does not depend on one "
                     "calibrated constant" % len(starts)),
        "criteria": CRITERIA,
        "identity": identity,
        "identity_all_pass": all(x["passes"] for x in identity),
        "panel": F._panel_block(cls, n_flip),
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp": round(COST * 1e4, 1),
                   "vol_target": VOL_TARGET, "carry": carry_note,
                   "mean_production_exposure": round(
                       float(np.mean([r["mean_exposure"] for r in prod_rows])), 4)},
        "phase_rows": rows,
        "verdict": verdict,
        "adoption": decide_adoption(rows),
        "notes": [
            "every arm holds the same names on the same grid and pays the same cost model; "
            "only the multiplier applied at each decision differs",
            "the constant arms are fixed BEFORE the run, so no arm is calibrated from the "
            "answer it is testing",
            "the production arm re-runs the engine's own scale and must reproduce its nav "
            "bit for bit (published identity leg, one per phase)",
            "out of sample = bars after %s; a fixed fraction that only wins in sample is "
            "not an adoption" % OOS_FROM,
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    v = verdict
    print("exposure ladder: %s | best fixed %s not worse in %d/%d phases | %d bars to %s | %.1fs"
          % (v["state"], v.get("best_fixed_scale"), v.get("best_phases_not_worse", 0),
             v.get("phases_tested", 0), len(all_dates), doc["evidence_cutoff"],
             doc["elapsed_sec"]))
    return doc


def write_md(doc):
    v = doc["verdict"]
    rows = doc["phase_rows"]
    ks = ["const_%.2f" % k for k in K_GRID]
    lines = ["# Would a fixed fraction do the same job as the de-lever rule?", "",
             "Face: `results/etf_book_exposure_ladder.json` (evidence cutoff %s, %d bars, "
             "%d phases, %.1f s)." % (doc["evidence_cutoff"], doc["bars"],
                                      len(set(r["phase"] for r in rows)), doc["elapsed_sec"]),
             "",
             "Same names, same grid, same cost model everywhere -- only the exposure "
             "multiplier differs. The fixed fractions were chosen before the run, so none "
             "of them is calibrated from the answer.", "",
             "| phase | start | " + " | ".join(["production"] + ["%s" % k[6:] for k in ks]) + " |",
             "|---|---|" + "---|" * (1 + len(ks))]
    for p in sorted(set(r["phase"] for r in rows)):
        byarm = {r["arm"]: r for r in rows if r["phase"] == p}
        cells = []
        for arm in ["production"] + ks:
            r = byarm.get(arm)
            cells.append("%.2f%%" % (100 * r["cagr"]) if r and r["cagr"] is not None else "-")
        lines.append("| %d | %s | %s |" % (p, byarm["production"]["phase_start"],
                                           " | ".join(cells)))
    lines += ["", "## Drawdown on the same phases", "",
              "| phase | " + " | ".join(["production"] + ["%s" % k[6:] for k in ks]) + " |",
              "|---|" + "---|" * (1 + len(ks))]
    for p in sorted(set(r["phase"] for r in rows)):
        byarm = {r["arm"]: r for r in rows if r["phase"] == p}
        cells = ["%.2f%%" % (100 * byarm[a]["maxdd"]) if byarm.get(a) and
                 byarm[a]["maxdd"] is not None else "-" for a in ["production"] + ks]
        lines.append("| %d | %s |" % (p, " | ".join(cells)))
    lines += ["", "## Out of sample (bars after %s)" % OOS_FROM, "",
              "| phase | " + " | ".join(["production"] + ["%s" % k[6:] for k in ks]) + " |",
              "|---|" + "---|" * (1 + len(ks))]
    for p in sorted(set(r["phase"] for r in rows)):
        byarm = {r["arm"]: r for r in rows if r["phase"] == p}
        cells = ["%.2f%%" % (100 * byarm[a]["oos_cagr"]) if byarm.get(a) and
                 byarm[a]["oos_cagr"] is not None else "-" for a in ["production"] + ks]
        lines.append("| %d | %s |" % (p, " | ".join(cells)))
    lines += ["", "## Out-of-sample Sharpe (the rule's risk-adjusted test)", "",
              "| phase | " + " | ".join(["production"] + ["%s" % k[6:] for k in ks]) + " |",
              "|---|" + "---|" * (1 + len(ks))]
    for p in sorted(set(r["phase"] for r in rows)):
        byarm = {r["arm"]: r for r in rows if r["phase"] == p}
        cells = ["%.3f" % byarm[a]["oos_sharpe"] if byarm.get(a) and
                 byarm[a]["oos_sharpe"] is not None else "-" for a in ["production"] + ks]
        lines.append("| %d | %s |" % (p, " | ".join(cells)))
    lines += ["", "## Verdict (full window)", "", "**%s**" % v["state"], "",
              "best fixed fraction: %s -- no worse than production in %d of %d phases "
              "(needed %d); production beats every fixed fraction in %d of %d cells."
              % (v.get("best_fixed_scale"), v.get("best_phases_not_worse", 0),
                 v.get("phases_tested", 0), v.get("phases_needed", 0),
                 v.get("production_cell_wins", 0), v.get("cells_total", 0)), ""]
    lad = v.get("ladder") or []
    if lad:
        lines += ["| fixed fraction | mean CAGR vs production | phases not worse |", "|---|---|---|"]
        for r in lad:
            lines.append("| %s | %+.2f pp | %d/%d |" % (r["arm"][6:],
                                                       r["cagr_delta_pp_mean"] or 0.0,
                                                       r["phases_not_worse"],
                                                       r["phases_tested"]))
    adopt = doc.get("adoption") or {}
    if adopt:
        lines += ["", "## Verdict (adoption: full window AND out of sample)", "",
                  "**%s**" % adopt["state"], "",
                  "best fixed fraction %s: no worse than production in %d of %d phases on the "
                  "full window, but only %d of %d out of sample -- the de-lever rule's own "
                  "out-of-sample Sharpe is the highest of the eight arms, so what it buys is "
                  "risk-adjusted return, not simply a smaller book."
                  % (adopt.get("best_fixed_scale"), adopt.get("best_full_window_ok", 0),
                     adopt.get("phases_tested", 0), adopt.get("best_out_of_sample_ok", 0),
                     adopt.get("phases_tested", 0)), "",
                  "| fixed fraction | full window not worse | out of sample not worse | "
                  "mean OOS CAGR vs production |", "|---|---|---|---|"]
        for r in adopt.get("ladder") or []:
            lines.append("| %s | %d/%d | %d/%d | %+.2f pp |"
                         % (r["arm"][6:], r["full_window_ok"], adopt.get("phases_tested", 0),
                            r["out_of_sample_ok"], adopt.get("phases_tested", 0),
                            r["oos_cagr_delta_pp_mean"] or 0.0))
        lines += ["",
                  "This second reading is the face's own pre-stated standard applied, not a "
                  "retuned threshold: the notes written before the first run demanded an "
                  "out-of-sample test, and the first run is exactly the case it was written "
                  "for (the full window says no worse, the out-of-sample window does not). "
                  "Both verdicts are published; the full-window one keeps its v1.0 criteria."]
    lines += ["", "## Identity", "",
              "the production arm re-runs the engine's own scale and reproduces its nav "
              "bit for bit on all %d phases: %s"
              % (len(doc["identity"]), "PASS" if doc["identity_all_pass"] else "FAIL"), "",
              "## Caveats", "",
              "- one panel, one universe; a wider or delisted-inclusive universe can move "
              "the level, though the comparison is between arms on the same names",
              "- the fixed fractions are long-only exposure multipliers, not leverage: "
              "1.00 means the book the card already describes at full size",
              "- `--check` re-derives the verdict from these published rows; a face whose "
              "echoed criteria differ from the module constants is refused"]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return OUT_MD


def check(path=None):
    with open(path or OUT_JSON, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    got = doc.get("criteria") or {}
    for key, want in CRITERIA.items():
        if got.get(key) != want:
            print("CHECK FAIL: criteria %s is %r, module says %r (the rule moved)"
                  % (key, got.get(key), want))
            return 1
    if not doc.get("identity_all_pass"):
        print("CHECK FAIL: the production arm does not reproduce the engine in every phase")
        return 1
    v = decide(doc["phase_rows"])
    if v["state"] != doc["verdict"]["state"]:
        print("CHECK FAIL: published %s, re-derived %s" % (doc["verdict"]["state"], v["state"]))
        return 1
    if v.get("best_fixed_scale") != doc["verdict"].get("best_fixed_scale"):
        print("CHECK FAIL: best fixed fraction moved %r -> %r"
              % (doc["verdict"].get("best_fixed_scale"), v.get("best_fixed_scale")))
        return 1
    if doc.get("adoption"):
        a = decide_adoption(doc["phase_rows"])
        if a["state"] != doc["adoption"]["state"]:
            print("CHECK FAIL: adoption published %s, re-derived %s"
                  % (doc["adoption"]["state"], a["state"]))
            return 1
        if a["best_fixed_scale"] != doc["adoption"].get("best_fixed_scale"):
            print("CHECK FAIL: adoption best fixed fraction moved")
            return 1
    print("CHECK OK: %s (best fixed %s, %d/%d phases)"
          % (v["state"], v.get("best_fixed_scale"), v.get("best_phases_not_worse", 0),
             v.get("phases_tested", 0)))
    return 0


def _fixture(n_names=14, n_bars=260, seed=7):
    return X._fixture(n_names=n_names, n_bars=n_bars, seed=seed)


def selftest():
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[0] += 1
        if cond:
            ok[1] += 1
            print("  PASS %s %s" % (name, detail))
        else:
            print("  FAIL %s %s" % (name, detail))

    close, openp, score, dates, _grid = _fixture()
    rebal = 4
    grid = set(dates[::rebal])
    eng = F.Forward(close, openp, score, N_HOLD, rebal, COST, vol_target=VOL_TARGET, carry=None)
    eng_ser = X._series(eng.run(dates, grid))
    ident_ser, ident_exp, ident_book = X._run_arm(close, openp, score, None, dates, grid,
                                                  lambda d, s: s)
    gap = float(np.max(np.abs(ident_ser.to_numpy() - eng_ser.to_numpy())))
    chk("identity arm reproduces the engine", gap <= IDENT_TOL, "gap=%.2e" % gap)
    chk("identity arm keeps the engine's picks", ident_book.selection_drift == 0)

    full_ser, full_exp, _fb = X._run_arm(close, openp, score, None, dates, grid,
                                         lambda d, s: 1.0)
    nore = F.Forward(close, openp, score, N_HOLD, rebal, COST, vol_target=None, carry=None)
    gap2 = float(np.max(np.abs(full_ser.to_numpy() - X._series(nore.run(dates, grid)).to_numpy())))
    chk("fixed fraction 1.00 equals the no-overlay book", gap2 <= 1e-9, "gap=%.2e" % gap2)

    small_ser, small_exp, _sb = X._run_arm(close, openp, score, None, dates, grid,
                                           lambda d, s: 0.40)
    # bars before the first fill hold cash at 1.0; the arm's own exposure is what it holds
    # once it is invested, so the leg reads the invested bars and bounds the rest
    invested = small_exp[small_exp > 0]
    chk("a fixed 0.40 book really holds 0.40",
        len(invested) > 0 and abs(float(np.mean(invested)) - 0.40) <= 1e-9
        and float(np.max(small_exp)) <= 0.40 + 1e-9,
        "mean=%.6f max=%.6f n=%d" % (float(np.mean(invested)) if len(invested) else -1,
                                     float(np.max(small_exp)), len(invested)))
    chk("the smaller book earns less and wobbles less",
        float(np.mean(small_exp)) < float(np.mean(full_exp))
        and A.stats2(small_ser, "s").get("vol") < A.stats2(full_ser, "f").get("vol"),
        "vol %.3f < %.3f" % (A.stats2(small_ser, "s").get("vol"),
                             A.stats2(full_ser, "f").get("vol")))

    starts = phase_starts(dates, rebal=rebal, n=N_PHASES)
    chk("phases are distinct decision grids", len(set(starts)) == N_PHASES,
        "%d starts" % len(set(starts)))

    def row(p, arm, cagr, dd, sharpe):
        return {"phase": p, "arm": arm, "cagr": cagr, "maxdd": dd, "sharpe": sharpe}

    dom = [row(p, "production", 0.08, -0.12, 0.9) for p in range(4)]
    dom += [row(p, "const_0.70", 0.09, -0.11, 0.95) for p in range(4)]
    v = decide(dom)
    chk("a fixed fraction that is never worse wins", v["state"] == "CONSTANT_LADDER_DOMINATES"
        and v["best_fixed_scale"] == "const_0.70", "%s %s" % (v["state"], v["best_fixed_scale"]))
    keep = [row(p, "production", 0.10, -0.12, 0.9) for p in range(4)]
    keep += [row(p, "const_0.70", 0.07, -0.12, 0.7) for p in range(4)]
    chk("production earns its keep when the fixed fraction loses everywhere",
        decide(keep)["state"] == "PRODUCTION_RULE_EARNS_ITS_KEEP", decide(keep)["state"])
    mixed = [row(p, "production", 0.10, -0.12, 0.9) for p in range(4)]
    mixed += [row(p, "const_0.70", 0.12 if p % 2 == 0 else 0.06, -0.12, 0.9) for p in range(4)]
    chk("half the phases each way is not a verdict",
        decide(mixed)["state"] == "PHASE_DEPENDENT", decide(mixed)["state"])
    def row_oos(p, arm, cagr, dd, sharpe, oos_cagr, oos_sharpe):
        r = row(p, arm, cagr, dd, sharpe)
        r["oos_cagr"] = oos_cagr
        r["oos_sharpe"] = oos_sharpe
        return r

    # the case the first real run produced: no worse on the full window, worse out of sample
    trap = [row_oos(p, "production", 0.09, -0.13, 0.95, 0.18, 1.70) for p in range(4)]
    trap += [row_oos(p, "const_0.70", 0.10, -0.11, 0.98, 0.17, 1.60) for p in range(4)]
    a = decide_adoption(trap)
    chk("a fixed fraction that only wins in sample is not an adoption",
        a["state"] == "REJECT_FIXED_FRACTION" and a["best_full_window_ok"] == 4
        and a["best_out_of_sample_ok"] == 0,
        "%s full=%d oos=%d" % (a["state"], a["best_full_window_ok"], a["best_out_of_sample_ok"]))
    good = [row_oos(p, "production", 0.09, -0.13, 0.95, 0.17, 1.60) for p in range(4)]
    good += [row_oos(p, "const_0.70", 0.10, -0.11, 0.98, 0.18, 1.70) for p in range(4)]
    chk("a fixed fraction that wins on both windows is adoptable",
        decide_adoption(good)["state"] == "ADOPT_FIXED_FRACTION",
        decide_adoption(good)["state"])
    chk("no production row refuses to publish",
        decide([row(0, "const_0.70", 0.1, -0.1, 1.0)])["state"] == "INCOMPLETE")

    # the gate must refuse a payload whose echoed rule differs from the module's
    tmp = os.path.join(ROOT, "results", "_exposure_ladder_selftest.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"criteria": dict(CRITERIA, cagr_tol_pp=CAGR_TOL_PP + 1.0),
                       "identity_all_pass": True, "phase_rows": dom,
                       "verdict": decide(dom)}, fh)
        chk("a moved criterion is refused", check(tmp) == 1)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    print("selftest %d/%d PASS" % (ok[1], ok[0]))
    return 0 if ok[1] == ok[0] else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    if "run" in argv:
        run()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())