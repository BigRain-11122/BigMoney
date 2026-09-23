"""G2_FOLK deepening batch: factory gate for 9 G1' candidate cells (5 fams).

PRE-REGISTERED (research/shortline/G2_FOLK.md, written first). G2_DEEPENING /
G2_NSP1 paradigm: center reproduction + fixed neighborhood grid + x3 cost
info + per-year no-crash clause. Passing families REGISTER as traders
(INTERN) -- registration JSONs + SIGNAL_BUILDERS wiring happen in the GM
session AFTER this script's verdict (script = evidence machine only).

Order chain: CEO O-20260923-2210 -> MSG-20260923-2212 claim.

G2 clauses per prereg s2:
  1. center reproduction: |full - recorded| < 0.005 AND trades exact;
  2. neighborhood: red points (full_sharpe < regime i-line) must be
     <= half of the family's neighborhood grid, else FAIL;
  3. x2-cost: representative cell x2 full sharpe > vi 0.4004 (recorded
     batch evidence cited; x3 re-run here as info);
  4. yearly: worst calendar year of representative cell > -35%;
  5. trades >= 30 (recorded).

Products: research/shortline/g2_folk_results.csv +
results/shortline_g2_folk.json (incl. registration packets for passers).
Trial ledger: prev from shortline_p4_folk.json (2299) + 47 = 2346.
"""
import csv
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from live.paper import (OOS_START, CostPatch, ExitPatch, _evidence_matches,
                        build_panels, load_core, seg_metrics,
                        self_test_patches)
from firm.hr import TRADERS_DIR, load_trader
from p3_portfolio import member_run

import strategies.ta as ta
import strategies.patterns as pt

EVIDENCE_CUT = "2026-09-22"
SLEEVE_MAX_CORR = 0.30  # unused here, kept for packet parity
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
VI_BAR = 0.4004
I_LINE = {"default": 0.3521, "ce": 0.4474}
WORST_YEAR_FLOOR = -0.35
REPRO_TOL = 0.005
TRIALS_PRIOR = "shortline_p4_folk.json"   # chain head 2299
LEDGER_KEY = "shortline-g2-folk"


# family -> (signal builder(P, overrides), survivor regimes, recorded
# centers {regime: (full, oos, trades, x2)}, neighborhood override points)
def _engulf(P, ov):
    return ta.engulf_reversal(P["open"], P["close"],
                              drop_th=ov.get("drop_th", -0.05))


def _volbreak(P, ov):
    return ta.vol_breakout(P["high"], P["low"], P["close"], P["volume"],
                           brk_len=ov.get("brk_len", 20),
                           vol_mult=ov.get("vol_mult", 1.5),
                           vol_avg_len=20,
                           exit_len=ov.get("exit_len", 10))


def _needle(P, ov):
    return pt.needle_probe(P["open"], P["high"], P["low"], P["close"],
                           drop_th=ov.get("drop_th", -0.05),
                           shadow_pct=ov.get("shadow_pct", 0.02))


def _drought(P, ov):
    return pt.vol_drought_reversal(P["open"], P["high"], P["low"],
                                   P["close"], P["volume"],
                                   vol_floor=ov.get("vol_floor", 0.55),
                                   drop_th=ov.get("drop_th", -0.05))


def _duck(P, ov):
    return pt.duck_head(P["open"], P["high"], P["low"], P["close"],
                        neck=ov.get("neck", 8))


FAMILIES = {
    "engulf_reversal": {
        "build": _engulf, "regimes": ["default", "ce"],
        "centers": {"default": (0.482, 0.300, 196, 0.291),
                    "ce": (0.539, 0.294, 143, 0.402)},
        "points": [{"drop_th": -0.04}, {"drop_th": -0.06}],
    },
    "vol_breakout": {
        "build": _volbreak, "regimes": ["ce"],
        "centers": {"ce": (0.467, 1.267, 803, 0.201)},
        "points": [{"brk_len": 15}, {"brk_len": 25}, {"vol_mult": 1.2},
                   {"vol_mult": 1.8}, {"exit_len": 7}, {"exit_len": 14}],
    },
    "needle_probe": {
        "build": _needle, "regimes": ["default", "ce"],
        "centers": {"default": (0.662, 0.409, 73, 0.574),
                    "ce": (0.639, 0.402, 63, 0.564)},
        "points": [{"drop_th": -0.04}, {"drop_th": -0.06},
                   {"shadow_pct": 0.015}, {"shadow_pct": 0.025}],
    },
    "vol_drought_reversal": {
        "build": _drought, "regimes": ["default", "ce"],
        "centers": {"default": (0.686, 1.230, 145, 0.525),
                    "ce": (0.724, 1.213, 120, 0.590)},
        "points": [{"vol_floor": 0.50}, {"vol_floor": 0.60},
                   {"drop_th": -0.04}, {"drop_th": -0.06}],
    },
    "duck_head": {
        "build": _duck, "regimes": ["default", "ce"],
        "centers": {"default": (0.682, 0.823, 947, 0.258),
                    "ce": (0.535, 0.606, 798, 0.210)},
        "points": [{"neck": 6}, {"neck": 10}],
    },
}


def run_cell(prices, idx, state, regime, cost_mult=None):
    pp = dict(CE_PARAMS) if regime == "ce" else {}
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    xctx = ExitPatch(CE_OVERRIDES) if regime == "ce" else nullcontext()
    with cctx, xctx:
        res = run_backtest(prices, pp, entry_signal=(state > 0),
                           exit_signal=(state <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_ts = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    return {"eq": eq, "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_ts}


def yearly_worst(eq):
    """Worst calendar-year return of the equity curve."""
    if eq is None or len(eq) < 2:
        return None
    yearly = eq.resample("YE").last()
    first = eq.index[0]
    yearly = pd.concat([pd.Series([eq.iloc[0]], index=[first]), yearly])
    rets = yearly.pct_change().dropna()
    return float(rets.min()) if len(rets) else None


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort")
        return 2
    print("patch self-tests: PASS")

    prices_full = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    prices = {s: df.loc[:cut].copy() for s, df in prices_full.items()
              if df.index[-1] > cut} or {s: df for s, df in
                                         prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index

    # trader anchors (hard gate)
    tids = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
            if not p.name.startswith("_")]
    anchors = {}
    for tid in tids:
        r1 = member_run(load_trader(tid), prices_full, None)
        ok = (_evidence_matches(
                  {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
                   "trades": r1["n_trades"] - r1["oos_trades"]},
                  load_trader(tid)["backtest"]["in_sample"])
              and _evidence_matches(
                  {**r1["oos"], "trades": r1["oos_trades"]},
                  load_trader(tid)["backtest"]["out_sample"]))
        anchors[tid] = {"anchor_ok": bool(ok),
                        "full_sharpe": r1["full"]["sharpe"]}
        print(f"  anchor {tid:<16} {'OK' if ok else 'BROKEN'}")
    if not all(a["anchor_ok"] for a in anchors.values()):
        print("ANCHOR BROKEN -- batch void")
        return 2

    rows, verdicts = [], []
    n_runs = len(anchors)  # ledger counter

    for fam, spec in FAMILIES.items():
        fam_rows = {"family": fam, "repro_ok": True, "red": 0,
                    "points": 0, "x2": None, "x3": None, "worst_year": None,
                    "pass": True, "reasons": []}
        center_cells = {}
        for regime in spec["regimes"]:
            full_r, oos_r, tr_r, x2_r = spec["centers"][regime]
            state = spec["build"](P, {})
            r = run_cell(prices, idx, state, regime)
            n_runs += 1
            d = abs(r["full"]["sharpe"] - full_r)
            repro = d < REPRO_TOL and r["n_trades"] == tr_r
            fam_rows["repro_ok"] &= bool(repro)
            rows.append([fam, "center", regime, round(r["full"]["sharpe"], 4),
                         round(r["oos"]["sharpe"], 4), r["n_trades"],
                         f"repro={'OK' if repro else 'FAIL'} d={d:.4f}"])
            center_cells[regime] = r
            if not repro:
                fam_rows["pass"] = False
                fam_rows["reasons"].append(f"repro fail @{regime}")

        # representative cell = highest recorded full
        rep_regime = max(spec["regimes"],
                         key=lambda rg: spec["centers"][rg][0])
        rep = center_cells[rep_regime]

        # neighborhood (per surviving regime)
        for regime in spec["regimes"]:
            for point in spec["points"]:
                state = spec["build"](P, point)
                r = run_cell(prices, idx, state, regime)
                n_runs += 1
                red = r["full"]["sharpe"] <= I_LINE[regime]
                fam_rows["points"] += 1
                fam_rows["red"] += int(red)
                rows.append([fam, f"nbhd {point}", regime,
                             round(r["full"]["sharpe"], 4),
                             round(r["oos"]["sharpe"], 4), r["n_trades"],
                             "RED" if red else "green"])
        if fam_rows["points"] and fam_rows["red"] * 2 > fam_rows["points"]:
            fam_rows["pass"] = False
            fam_rows["reasons"].append(
                f"neighborhood red {fam_rows['red']}/{fam_rows['points']}")

        # x2 clause (recorded) + x3 info (re-run)
        x2_rep = spec["centers"][rep_regime][3]
        fam_rows["x2"] = x2_rep
        if not x2_rep > VI_BAR:
            fam_rows["pass"] = False
            fam_rows["reasons"].append(f"x2 {x2_rep} <= vi {VI_BAR}")
        r3 = run_cell(prices, idx, spec["build"](P, {}), rep_regime,
                      cost_mult=3)
        n_runs += 1
        fam_rows["x3"] = round(r3["full"]["sharpe"], 4)

        # yearly clause
        wy = yearly_worst(rep["eq"])
        fam_rows["worst_year"] = None if wy is None else round(wy, 4)
        if wy is None or wy <= WORST_YEAR_FLOOR:
            fam_rows["pass"] = False
            fam_rows["reasons"].append(f"worst year {wy}")

        # trades clause (recorded)
        if spec["centers"][rep_regime][2] < 30:
            fam_rows["pass"] = False
            fam_rows["reasons"].append("trades<30")

        # registration packet (evidence blocks for the rep cell)
        is_m = seg_metrics(rep["eq"][rep["eq"].index < pd.Timestamp(OOS_START)])
        oos_m = seg_metrics(rep["eq"], OOS_START)
        fam_rows["packet"] = {
            "rep_regime": rep_regime,
            "in_sample": {**is_m, "trades": rep["n_trades"] - rep["oos_trades"]},
            "out_sample": {**oos_m, "trades": rep["oos_trades"]},
            "cost_x2": {"sharpe": x2_rep, "survive": bool(x2_rep > VI_BAR)},
        }
        verdicts.append(fam_rows)
        print(f"{fam:<22} pass={fam_rows['pass']} "
              f"red={fam_rows['red']}/{fam_rows['points']} "
              f"x2={x2_rep} x3={fam_rows['x3']} "
              f"worst_year={fam_rows['worst_year']} "
              f"reasons={'; '.join(fam_rows['reasons']) or '-'}")

    # outputs
    csv_path = os.path.join(PATHS.root, "research", "shortline",
                            "g2_folk_results.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "cell", "regime", "full_sharpe",
                    "oos_sharpe", "trades", "note"])
        w.writerows(rows)
    print(f"saved: {csv_path}")

    with open(os.path.join(PATHS.results_dir, TRIALS_PRIOR),
              encoding="utf-8") as fh:
        prev_total = int(json.load(fh)["trials_ledger"]["total"])
    out = {
        "batch": LEDGER_KEY,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/G2_FOLK.md",
        "universe": {"pool": "core48-bare-codes",
                     "evidence_cutoff": EVIDENCE_CUT,
                     "oos_start": OOS_START},
        "gates": {"vi_bar": VI_BAR, "i_line": I_LINE,
                  "worst_year_floor": WORST_YEAR_FLOOR,
                  "repro_tol": REPRO_TOL},
        "anchors": anchors,
        "verdicts": [{k: v for k, v in f.items()} for f in verdicts],
        "registered": [f["family"] for f in verdicts if f["pass"]],
        "trials_ledger": {"prev_total": prev_total, "batch_trials": n_runs,
                          "note": f"{n_runs} runs = 9 center + 30 nbhd + "
                                  f"5 x3 + 3 anchors (prereg s7 says 47; "
                                  f"counted live: {n_runs})",
                          "total": prev_total + n_runs},
        "audit": {"elapsed_sec": round(time.time() - t0, 1)},
    }
    json_path = os.path.join(PATHS.results_dir, "shortline_g2_folk.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"registered (G2 PASS): {out['registered']}")
    print(f"runs={n_runs} elapsed={time.time()-t0:.0f}s "
          f"ledger N={prev_total + n_runs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
