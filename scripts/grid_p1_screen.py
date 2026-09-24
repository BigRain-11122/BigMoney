"""GRID_P1 grid-harvest A-layer migration screen (QUANT_STYLE_ATLAS row 8,
T-202609-25-40 slice-2, lane bm-b per MSG-20260925-0300).

Pre-registered in research/GRID_P1.md BEFORE any run (frozen commit 1b4bffd2
r136, pre-run zero cells). Iron rules: no threshold tuning, no re-run after
results (BACKTEST_PLAN rule 3), cutoff lockbox 2026-09-24 (new bars never
flow back into this batch), OOS blind + costs always on.

Fixed faces (prereg sec.0/sec.3), NO search -- single-point NSP1 precedent:
  1 entry (strategies/grid.grid_channel_harvest frozen params
  channel_len=60 n_grids=6 n_targets=12 top_k=5 rebal_days=10 vol_win=30)
  x 2 exit regimes (default | CE) x 2 cost faces (V1 13bp | CostPatch(2.0))
  = 4 cell runs
  + 100 random-signal nulls (50/exit regime, p in {0.02,0.05} x 25 seeds,
    seed base 55_500 per SEED_REGISTRY['grid_p1'], r137 registration)
  + 2 passive baselines (J8 formulas, consistency info)
  + 6 registered-member anchor reruns (member_run 1x, own cutoffs)
  = 112 trials (prereg sec.0 N_eff count).

Gates (prereg sec.4): G1' v2 via science_gates.g1_prime_v2 -- data-driven
skill line (ledger head + shared null collector), zero hand-copied constants;
batch-level descriptive clauses (ann>0, OOS double positive, dd>=-35%,
x2 face) disclosed, never replacing the v2 gate. D6 admission (sec.1):
max|corr| of daily returns vs the registered 6 >= 0.70 -> REJECT from the
candidate pool (mechanism-novelty clause, honest value disclosure).

D6 wording resolution (pre-run, zero cells, r71 ambiguity protocol): sec.1
"registered 6 + same-batch cells" -- the registered face REJECTS (>=0.70),
the same-batch face follows the repo-established T-33 merge semantics
(later-priority cell merges into the earlier when both would pass; the two
cells here are one entry under two exit regimes, so a pair-corr >= 0.70
cannot mean mechanism-novelty failure). Both faces disclosed per-pair in
the results JSON; resolution frozen in this docstring before burn.

Hard gates (any FAIL = batch VOID, exit 2, no verdicts): patch self-test,
48/48 panel at cutoff, anchor reproduction 6/6. Checkpoint row-level
resume (t22 law) for cells + nulls; finalize reads the checkpoint file,
never in-memory state (T-33 law).

Usage: python scripts/grid_p1_screen.py run | selftest
Products: results/grid_p1.json + research/grid_p1_results.csv
+ gate_attrition row + trials-ledger append (finalize, single-shot guard).
"""
import argparse
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

TICKET = "T-2026-09-25-40"
PREREG_PATH = os.path.join("research", "GRID_P1.md")
CUTOFF = "2026-09-24"            # prereg sec.2 lockbox (pinned, no reflow)
BATCH_CELLS = 112                # prereg sec.0 N_eff count (frozen)
N_RAND = 50                      # per exit regime (prereg sec.3)
BASELINE_P = (0.02, 0.05)        # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 55_500               # SEED_REGISTRY['grid_p1'] (r137)
D6_LINE = 0.70                   # prereg sec.1 rejection line
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
GRID_PARAMS = dict(channel_len=60, n_grids=6, n_targets=12, top_k=5,
                    rebal_days=10, vol_win=30)
SIZING = {"max_positions": 5, "position_size_pct": 0.19,
          "report_num_entries": True}     # 0.95/5 composite convention
NAMED_SIX = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
             "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
REGIMES = ("default", "ce")
OUT_JSON = os.path.join("results", "grid_p1.json")
OUT_CSV = os.path.join("research", "grid_p1_results.csv")
CELLS_PATH = os.path.join("results", "grid_p1_cells.jsonl")
ATT_JSON = os.path.join("results", "gate_attrition.json")
LOG_PATH = os.path.join("results", "grid_p1.log")


def _log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def _sha256_file(path):
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _pearson(a: pd.Series, b: pd.Series) -> float:
    """Inner-join by date (members run at their own 09-22 cutoffs; the tail
    short by 2 days drops honestly, r69 date-alignment law, min 20 overlap)."""
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def _false_panel(idx, syms):
    return pd.DataFrame(False, index=idx, columns=syms)


def null_seed(regime: str, k: int) -> int:
    """Prereg sec.3 seed recipe: default 55_500+k, ce 55_550+k (k<50)."""
    return SEED_BASE + (k if regime == "default" else N_RAND + k)


def null_entry(idx, syms, p: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame((rng.random((len(idx), len(syms))) < p).astype(int),
                        index=idx, columns=syms)


def run_cell(prices, idx, entry, exit_, params, ce, cost_mult=None):
    """NSP1-isomorphic cell runner (CostPatch single source, ExitPatch CE)."""
    from engine import run_backtest
    from live.paper import ExitPatch, seg_metrics
    import science_gates as sg
    pp = dict(params or {})
    if ce:
        pp.update(CE_PARAMS)
    cctx = sg.CostPatch(cost_mult) if cost_mult else nullcontext()
    xctx = ExitPatch(CE_OVERRIDES) if ce else nullcontext()
    with cctx, xctx:
        res = run_backtest(prices, pp, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_ts = sum(1 for tr in res["trades"] if str(tr["date"]) >= "2025-01-01")
    return {"eq": eq, "full": res["metrics"], "oos": seg_metrics(eq, "2025-01-01"),
            "n_trades": res["metrics"]["num_trades"],
            "n_entries": res["metrics"].get("num_entries", -1),
            "oos_trades": oos_ts}


# ---------------------------------------------------------------- checkpoint

def load_rows(path):
    """All parseable rows (truncated tail tolerated, t22 law)."""
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for ln in lines:
        try:
            r = json.loads(ln)
            rows[r["key"]] = r
        except (ValueError, KeyError):
            continue
    return rows


def _append_row(row):
    with open(CELLS_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=bool) + "\n")


# ------------------------------------------------------------- D6 resolution

def d6_resolve(pass_by_regime: dict, corr_pair: float,
               line: float = D6_LINE) -> dict:
    """Pure rule-selector (r71 double-reading fixture law applies).

    Inputs: pass_by_regime = {regime: bool} -- G1' v2 pass AND registered-face
    admission per cell; corr_pair = |corr| between the two cells' daily returns.
    Same-batch face = T-33 merge semantics: pair-corr >= line merges the
    later-priority cell (ce) into the earlier (default) when both would
    pass; a merged cell is not an independent candidate. A merge target that
    itself did not pass leaves the later cell standing (nothing to merge
    into -- disclosed). Registered-face rejection is applied by the caller
    BEFORE this function (pass_by_regime already false).
    """
    out = {}
    both = bool(pass_by_regime.get("default")) and bool(pass_by_regime.get("ce"))
    merge = both and np.isfinite(corr_pair) and corr_pair >= line
    for reg in ("default", "ce"):
        survivor = bool(pass_by_regime.get(reg))
        status, merged_into = "unique", None
        if reg == "ce" and merge:
            status, merged_into, survivor = "d6-merged", "default", False
        out[reg] = {"survivor": survivor, "d6_same_batch": status,
                    "merged_into": merged_into}
    out["pair_corr"] = (round(float(corr_pair), 4)
                        if np.isfinite(corr_pair) else None)
    return out


# --------------------------------------------------------------- anchor face

def anchor_ok_1x(t: dict, r1: dict) -> bool:
    """Registered 1x evidence reproduction (live.paper.anchor_gate core,
    member_run same code path; IS + OOS segment matches, ANCHOR_TOL)."""
    from live.paper import OOS_START, _evidence_matches, seg_metrics
    got_is = {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
              "trades": r1["n_trades"] - r1["oos_trades"]}
    got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
    return bool(_evidence_matches(got_is, t["backtest"]["in_sample"])
                and _evidence_matches(got_oos, t["backtest"]["out_sample"]))


# ------------------------------------------------------------------ finalize

def finalize(cell_rows, verdict_cells, nulls, passive_rows, anchors, gates,
             t0, void=False):
    import science_gates as sg
    if os.path.exists(OUT_JSON) and os.environ.get("GRID_P1_REFINALIZE") != "1":
        print("finalize refused: OUT_JSON exists (single-shot guard; "
              "GRID_P1_REFINALIZE=1 to redo)")
        return 2

    line = None
    cand_rows = []
    for c in verdict_cells:              # verdict face = base (x1) cost
        g1 = sg.g1_prime_v2(c["full"]["sharpe"], c["_rets"], BATCH_CELLS,
                            n_trades=c["n_trades"], n_entries=c["n_entries"])
        line = g1["skill_line"]
        reg_max, reg_arg = 0.0, None
        for rid, rseries in anchors["rets"].items():
            cc = abs(_pearson(c["_rets"], rseries))
            if np.isfinite(cc) and cc > reg_max:
                reg_max, reg_arg = cc, rid
        cand_rows.append({
            "name": "grid_channel_harvest", "exit_regime": c["exit_regime"],
            "sharpe_full": c["full"]["sharpe"],
            "annual_return": c["full"]["annual_return"],
            "max_drawdown": c["full"]["max_drawdown"],
            "oos_sharpe": c["oos"]["sharpe"],
            "oos_annual_return": c["oos"]["annual_return"],
            "n_trades": c["n_trades"], "n_entries": c["n_entries"],
            "x2_full_sharpe": c["x2_full_sharpe"],
            "x2_oos_sharpe": c["x2_oos_sharpe"],
            "descriptive": {
                "ann_positive": bool(c["full"]["annual_return"] > 0),
                "oos_double_positive": bool(
                    c["oos"]["sharpe"] > 0 and c["oos"]["annual_return"] > 0),
                "dd_ok": bool(c["full"]["max_drawdown"] >= -0.35),
            },
            "g1_prime_v2": g1,
            "g1_pass": bool(g1["pass_v2"]),
            "d6": {"max_corr_vs_registered": round(reg_max, 4),
                   "vs_registered_argmax": reg_arg,
                   "registered_ok": bool(reg_max < D6_LINE)},
        })

    survivors, d6_registered_rejects = [], []
    pass_by_regime = {}
    for r in cand_rows:
        admitted = bool(r["g1_pass"] and r["d6"]["registered_ok"])
        pass_by_regime[r["exit_regime"]] = admitted
        if r["g1_pass"] and not r["d6"]["registered_ok"]:
            d6_registered_rejects.append(r["exit_regime"])
    pair_corr = (abs(_pearson(verdict_cells[0]["_rets"],
                              verdict_cells[1]["_rets"]))
                 if len(verdict_cells) == 2 else float("nan"))
    d6 = d6_resolve(pass_by_regime, pair_corr) if cand_rows else None
    if d6:
        for r in cand_rows:
            face = d6[r["exit_regime"]]
            r["d6"]["same_batch"] = face["d6_same_batch"]
            r["d6"]["merged_into"] = face["merged_into"]
            r["d6"]["pair_corr_same_batch"] = d6["pair_corr"]
            if face["survivor"]:
                survivors.append(f"{r['name']}@{r['exit_regime']}")

    led = None
    if not void:
        led = sg.append_ledger("GRID-P1", BATCH_CELLS,
                               file_name="results/grid_p1.json",
                               evidence_cutoff=CUTOFF,
                               note="2 cells x(x1+x2) + 100 nulls + 2 passive"
                                    " + 6 anchors; prereg research/GRID_P1.md"
                                    " frozen 1b4bffd2 r136")
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        att["entries"].append({
            "batch": "GRID-P1", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement", "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": led["total"],
            "gates": {
                "skill_line_v2": None if line is None else line["line"],
                "g1_prime_v2_pass": len(survivors),
                "d6_registered_rejects": d6_registered_rejects,
                "d6_same_batch_merged": (None if d6 is None
                                         else d6["ce"]["merged_into"]),
                "anchor_repro_all_pass": bool(gates["anchors_ok"]),
                "best_cell": (max(cand_rows, key=lambda r: r["sharpe_full"])
                              ["exit_regime"] if cand_rows else None),
                "best_full_sharpe": (round(max(r["sharpe_full"]
                                               for r in cand_rows), 4)
                                     if cand_rows else None),
            },
            "eliminated": (len(cand_rows) - len(survivors)) if cand_rows else 0,
            "refs": {"results": "results/grid_p1.json",
                     "prereg": "research/GRID_P1.md",
                     "csv": "research/grid_p1_results.csv",
                     "ticket": TICKET},
        })
        with open(ATT_JSON, "w", encoding="utf-8") as fh:
            json.dump(att, fh, ensure_ascii=False, indent=1)

    def _cell_public(c):
        return {k: v for k, v in c.items()
                if k not in ("_rets", "_eq_index", "key")}

    out = {
        **sg.cutoff_meta(CUTOFF),
        "batch": "GRID-P1", "ticket": TICKET,
        "prereg": "research/GRID_P1.md",
        "prereg_sha256_16": _sha256_file(PREREG_PATH)[:16],
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "void": bool(void),
        "universe": {"pool": "core48-bare-codes", "cutoff": CUTOFF,
                     "oos_start": "2025-01-01",
                     "data_end_raw": gates["data_end_raw"]},
        "hard_gates": {k: gates[k] for k in
                       ("patch_selftest", "panel", "anchors_ok")},
        "grid_params": GRID_PARAMS, "sizing": SIZING,
        "cost": "V1 legacy 13bp base + CostPatch(2.0) x2 stress face",
        "cells": [_cell_public(c) for c in cell_rows],
        "candidates": cand_rows,
        "nulls": nulls, "passive": passive_rows,
        "anchors": {"repro": anchors.get("repro", []),
                    "n_members": len(anchors.get("repro", []))},
        "d6_resolution": ("sec.1 registered-face REJECTS at >=0.70 (mechanism"
                          "-novelty clause); same-batch face = T-33 merge "
                          "semantics (pre-run resolution at zero cells, r71 "
                          "protocol, runner docstring); per-pair values "
                          "disclosed per candidate"),
        "survivors_g1_prime": survivors,
        "survivors_are": ("G1' CANDIDATES ONLY -- no registration this batch; "
                          "G2 deepening requires a separate pre-registration"),
        "trials_ledger": led,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": (sum(1 for c in cell_rows
                                      if c.get("status") == "ok")
                                   + len(nulls.get("rows", []))
                                   + len(anchors.get("repro", []))),
                  "workers": 1, "cpu_parallel": "serial (single-process)",
                  "prereg_frozen_before_run": True},
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    print(f"saved: {OUT_JSON}")

    import csv as _csv
    cols = ["name", "exit_regime", "cost_face", "status", "n_trades",
            "n_entries", "annual_return", "sharpe", "max_drawdown",
            "oos_sharpe", "oos_annual_return", "skill_line", "g1_pass",
            "d6_registered_ok", "d6_same_batch", "max_corr_vs_registered",
            "note"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for c in cell_rows:
            g1row = next((r for r in cand_rows
                          if r["exit_regime"] == c.get("exit_regime")), None)
            w.writerow([
                c.get("name", "grid_channel_harvest"),
                c.get("exit_regime", ""), c.get("cost_face", ""),
                c.get("status", ""), c.get("n_trades", ""),
                c.get("n_entries", ""),
                c.get("full", {}).get("annual_return", ""),
                c.get("full", {}).get("sharpe", ""),
                c.get("full", {}).get("max_drawdown", ""),
                c.get("oos", {}).get("sharpe", ""),
                c.get("oos", {}).get("annual_return", ""),
                (g1row["g1_prime_v2"]["skill_line"]["line"]
                 if g1row else ""),
                (g1row["g1_pass"] if g1row else ""),
                (g1row["d6"]["registered_ok"] if g1row else ""),
                (g1row["d6"]["same_batch"] if g1row else ""),
                (g1row["d6"]["max_corr_vs_registered"] if g1row else ""),
                c.get("note", "")])
        for r in nulls.get("rows", []):
            w.writerow([r["name"], r["exit_regime"], "x1", "ok", "", "",
                        r["full"]["annual_return"], r["full"]["sharpe"],
                        r["full"]["max_drawdown"], r["oos"]["sharpe"],
                        r["oos"]["annual_return"], "", "", "", "", "",
                        f"p={r['p']} seed={r['seed']}"])
        for k, v in passive_rows.items():
            w.writerow([k, "none", "formula", "ok", 0, 0,
                        v["full"]["annual_return"], v["full"]["sharpe"],
                        v["full"]["max_drawdown"], v["oos"]["sharpe"],
                        v["oos"]["annual_return"], "", "", "", "", "",
                        "J8 formula, consistency info"])
    print(f"saved: {OUT_CSV}")
    print(f"survivors: {survivors}")
    return 0


# ---------------------------------------------------------------------- run

def cmd_run(_) -> int:
    t0 = time.time()
    from live.paper import (OOS_START, PAPER_LEVELS, build_panels, load_core,
                            seg_metrics, self_test_patches)
    from strategies.grid import grid_channel_harvest
    from firm.hr import TRADERS_DIR, load_trader
    from p3_portfolio import member_run
    from p2_null_calibration import passive_buyhold, passive_monthly_rebal
    from knowledge.rules import FeeSchedule

    if not self_test_patches():
        _log("patch self-test FAILED -- batch void (fake-evidence guard)")
        return 2
    _log("patch self-tests: PASS")

    prices_full = load_core()
    data_end_raw = str(prices_full["510300"].index[-1].date())
    if pd.Timestamp(data_end_raw) < pd.Timestamp(CUTOFF):
        _log(f"panel short: end {data_end_raw} < cutoff {CUTOFF} -- VOID")
        return 2
    ps = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    close, idx, syms = P["close"], P["close"].index, list(P["close"].columns)
    if len(syms) != 48:
        _log(f"panel gate FAILED: {len(syms)}/48 syms -- VOID")
        return 2
    _log(f"panel: {len(syms)} syms, {idx[0].date()}..{idx[-1].date()} "
         f"(raw end {data_end_raw}, lockbox {CUTOFF})")

    done = load_rows(CELLS_PATH)
    entry = grid_channel_harvest(close, **GRID_PARAMS)
    exit_ = (entry <= 0)

    # ---------- cells: 2 regimes x 2 cost faces (checkpointed) ----------
    for ce in (False, True):
        regime = "ce" if ce else "default"
        for face, mult in (("x1", None), ("x2", 2.0)):
            key = f"grid|{regime}|{face}"
            if key in done:
                _log(f"cell {key}: resume-skip")
                continue
            try:
                r = run_cell(prices, idx, entry, exit_, SIZING, ce, mult)
                row = {"key": key, "name": "grid_channel_harvest",
                       "exit_regime": regime, "cost_face": face,
                       "status": "ok",
                       "full": {k: (round(float(v), 6)
                                    if isinstance(v, (int, float)) else v)
                                for k, v in r["full"].items()},
                       "oos": {k: round(float(v), 6) for k, v in
                               r["oos"].items()},
                       "n_trades": r["n_trades"], "n_entries": r["n_entries"],
                       "oos_trades": r["oos_trades"], "note": ""}
                if face == "x1":
                    rets = r["eq"].pct_change().dropna()
                    row["_rets"] = [round(float(x), 8) for x in rets.to_numpy()]
                    row["_eq_index"] = [str(d.date()) for d in r["eq"].index]
                _append_row(row)
                _log(f"cell {key}: s={r['full']['sharpe']:.4f} "
                     f"entries={r['n_entries']} trades={r['n_trades']}")
            except Exception as ex:
                _append_row({"key": key, "exit_regime": regime,
                             "cost_face": face,
                             "status": f"cell_error: {type(ex).__name__}: {ex}"})
                _log(f"cell {key}: ERROR {ex}")

    # ---------- nulls: 50 per exit regime (checkpointed) ----------
    for ce in (False, True):
        regime = "ce" if ce else "default"
        for k in range(N_RAND):
            p = BASELINE_P[k // 25]
            seed = null_seed(regime, k)
            key = f"null|{regime}|{k}"
            if key in done:
                continue
            e = null_entry(idx, syms, p, seed)
            r = run_cell(prices, idx, e, _false_panel(idx, syms), {}, ce)
            _append_row({"key": key, "name": f"rand_{regime}_p{p}_s{k}",
                         "exit_regime": regime, "status": "ok", "p": p,
                         "seed": seed,
                         "full": {"sharpe": round(float(r["full"]["sharpe"]), 6),
                                  "annual_return": round(float(r["full"]["annual_return"]), 6),
                                  "max_drawdown": round(float(r["full"]["max_drawdown"]), 6)},
                         "oos": {kk: round(float(vv), 6)
                                 for kk, vv in r["oos"].items()}})
        _log(f"nulls regime={regime}: checked {N_RAND}")

    # ---------- rebuild from checkpoint (T-33 law: file, not memory) ------
    rows = load_rows(CELLS_PATH)
    cell_rows = [rows[f"grid|{reg}|{face}"] for reg in REGIMES
                 for face in ("x1", "x2") if f"grid|{reg}|{face}" in rows]
    null_rows = [rows[k] for k in rows
                 if k.startswith("null|") and rows[k].get("status") == "ok"]
    gates = {"patch_selftest": True, "panel": True, "anchors_ok": False,
             "data_end_raw": data_end_raw}
    if len(cell_rows) != 4 or any(c["status"] != "ok" for c in cell_rows):
        _log(f"cells incomplete: {len(cell_rows)}/4 ok -- VOID (no verdict)")
        return finalize(cell_rows, [], {"rows": null_rows, "summary": {}},
                        {}, {"repro": [], "rets": {}}, gates, t0, void=True)
    if len(null_rows) != 2 * N_RAND:
        _log(f"nulls incomplete: {len(null_rows)}/{2 * N_RAND} -- VOID")
        return finalize(cell_rows, [], {"rows": null_rows, "summary": {}},
                        {}, {"repro": [], "rets": {}}, gates, t0, void=True)

    # verdict cells = x1 faces, DatetimeIndex re-attached (r69 law)
    verdict_cells = []
    for reg in REGIMES:
        c = dict(rows[f"grid|{reg}|x1"])
        c["_rets"] = pd.Series(c["_rets"],
                               index=pd.DatetimeIndex(c["_eq_index"][1:]))
        c.pop("_eq_index", None)
        verdict_cells.append(c)

    nulls_vals = [float(r["full"]["sharpe"]) for r in null_rows]
    p95 = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in null_rows
         if r["exit_regime"] == reg], 95)), 4) for reg in REGIMES}
    nulls = {"rows": null_rows,
             "summary": {"n": len(null_rows),
                         "mu": round(float(np.mean(nulls_vals)), 4),
                         "sigma": round(float(np.std(nulls_vals, ddof=1)), 4),
                         "p95_inbatch_full": p95,
                         "note": "in-batch controls (disclosure); skill line "
                                 "is data-driven from the shared collector"}}

    # ---------- passive baselines (consistency info) ----------
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee
                 + fee.supervision_fee + fee.slippage_a)
    passive_rows = {}
    for k, eq in (("ew48_buyhold", passive_buyhold(close, cost_rate)),
                  ("ew48_monthly_rebal", passive_monthly_rebal(close, cost_rate))):
        passive_rows[k] = {"full": seg_metrics(eq),
                           "oos": seg_metrics(eq, OOS_START)}
    _log(f"passive: bh_s={passive_rows['ew48_buyhold']['full']['sharpe']:.4f} "
         f"mr_s={passive_rows['ew48_monthly_rebal']['full']['sharpe']:.4f}")

    # ---------- anchors: registered 6 (hard gate + D6 reference) ----------
    anchors = {"repro": [], "rets": {}}
    anchors_ok = True
    for tid in NAMED_SIX:
        t = load_trader(tid)
        if t.get("level") not in PAPER_LEVELS:
            _log(f"anchor {tid}: level {t.get('level')} not in PAPER_LEVELS"
                 " -- VOID (registration face changed)")
            anchors_ok = False
            continue
        r1 = member_run(t, prices_full)       # own evidence cutoff, 1x
        ok = anchor_ok_1x(t, r1)
        anchors["repro"].append({"member": tid, "anchor_ok": bool(ok),
                                 "cutoff": r1["cutoff"],
                                 "full_sharpe": round(r1["full"]["sharpe"], 4)})
        anchors["rets"][tid] = r1["eq"].pct_change().dropna()
        anchors_ok &= ok
        _log(f"anchor {tid}: full_s={r1['full']['sharpe']:.4f} "
             f"{'OK' if ok else 'BROKEN'}")
    extra = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_") or path.stem in NAMED_SIX:
            continue
        try:
            with open(path, encoding="utf-8-sig") as fh:   # r131 BOM law
                if json.load(fh).get("level") in PAPER_LEVELS:
                    extra.append(path.stem)
        except (OSError, ValueError):
            continue
    if extra:
        _log(f"disclosure: extra PAPER_LEVELS members beyond prereg six: {extra}")
    if not anchors_ok or len(anchors["repro"]) != 6:
        _log("ANCHOR gate FAILED -- batch VOID (prereg sec.2)")
        return finalize(cell_rows, verdict_cells, nulls, passive_rows,
                        anchors, gates, t0, void=True)

    gates["anchors_ok"] = True
    _log("all hard gates PASS -- finalizing")
    return finalize(cell_rows, verdict_cells, nulls, passive_rows, anchors,
                    gates, t0)


# ----------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    import tempfile
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("GRID_P1 runner selftest (offline hermetic, zero repo products):")
    # -- seed recipe: disjoint families inside the registered band
    sd = [null_seed("default", k) for k in range(N_RAND)]
    sc = [null_seed("ce", k) for k in range(N_RAND)]
    ok("seed families disjoint + banded + deterministic",
       not (set(sd) & set(sc)) and sd == list(range(55_500, 55_550))
       and sc == list(range(55_550, 55_600)) and sd[0] == 55_500)
    # -- null entry panel: deterministic, binary, shape
    idx = pd.date_range("2020-01-02", periods=40, freq="B")
    e1 = null_entry(idx, ["a", "b"], 0.05, 55_500)
    ok("null entry deterministic + binary",
       e1.equals(null_entry(idx, ["a", "b"], 0.05, 55_500))
       and set(np.unique(e1.to_numpy())) <= {0, 1} and e1.shape == (40, 2))
    # -- D6 resolver three-state fixtures (r71 double-reading law)
    r = d6_resolve({"default": True, "ce": True}, 0.42)
    ok("D6 both-pass + low corr -> both survivors",
       r["default"]["survivor"] and r["ce"]["survivor"]
       and r["ce"]["d6_same_batch"] == "unique")
    r = d6_resolve({"default": True, "ce": True}, 0.88)
    ok("D6 both-pass + pair>=0.70 -> ce merges into default",
       r["default"]["survivor"] and not r["ce"]["survivor"]
       and r["ce"]["d6_same_batch"] == "d6-merged"
       and r["ce"]["merged_into"] == "default")
    r = d6_resolve({"default": True, "ce": True}, 0.70)
    ok("D6 boundary corr==0.70 merges (frozen >= semantics)",
       r["ce"]["d6_same_batch"] == "d6-merged")
    r = d6_resolve({"default": False, "ce": True}, 0.95)
    ok("D6 merge target failed -> later cell stands",
       r["ce"]["survivor"] and r["ce"]["d6_same_batch"] == "unique")
    r = d6_resolve({"default": False, "ce": False}, 0.10)
    ok("D6 all-fail -> zero survivors", not r["default"]["survivor"]
       and not r["ce"]["survivor"])
    r = d6_resolve({"default": True, "ce": True}, float("nan"))
    ok("D6 nan corr -> no merge (honest)", r["ce"]["d6_same_batch"] == "unique")
    # -- pearson: date inner-join drops tail honestly
    s1 = pd.Series(np.random.default_rng(1).normal(0, .01, 300),
                   index=pd.date_range("2024-01-01", periods=300, freq="B"))
    s2 = s1.iloc[:250] * 2.0
    ok("pearson inner-join + finite", abs(abs(_pearson(s1, s2)) - 1.0) < 1e-6
       and np.isnan(_pearson(s1.iloc[:5], s2)))
    # -- checkpoint resume: truncated tail tolerated (t22 law)
    with tempfile.TemporaryDirectory() as tmp:
        cp = os.path.join(tmp, "cells.jsonl")
        with open(cp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"key": "a"}) + "\n")
            fh.write(json.dumps({"key": "b"}) + "\n")
            fh.write(json.dumps({"key": "c", "pad": "x" * 40})[:20])
        ok("checkpoint row reload (truncation-tolerant)",
           set(load_rows(cp)) == {"a", "b"})
    # -- anchor 1x face: seg_metrics monkeypatched (pure wiring check on the
    #    tolerant key names + exact-match semantics of _evidence_matches)
    import live.paper as lp
    orig = lp.seg_metrics
    lp.seg_metrics = lambda eq, start=None: (
        {"sharpe": 1.0, "max_drawdown": -0.1, "annual_return": 0.1}
        if start is None
        else {"sharpe": 0.8, "max_drawdown": -0.2, "annual_return": 0.05})
    try:
        fake_t = {"backtest": {
            "in_sample": {"sharpe": 1.0, "max_drawdown": -0.1,
                          "annual": 0.1, "trades": 50},
            "out_sample": {"sharpe": 0.8, "max_dd": -0.2,
                           "annual_return": 0.05, "trades": 12}}}
        eq = pd.Series(np.linspace(1.0, 2.0, 500),
                       index=pd.date_range("2023-01-02", periods=500,
                                           freq="B"))
        r1 = {"eq": eq, "oos": {"sharpe": 0.8, "max_drawdown": -0.2,
                                "annual_return": 0.05},
              "n_trades": 62, "oos_trades": 12}
        ok("anchor 1x tolerant key names + exact-match",
           anchor_ok_1x(fake_t, r1)
           and not anchor_ok_1x(fake_t, {**r1, "oos": {**r1["oos"],
                                                       "sharpe": 0.5}}))
    finally:
        lp.seg_metrics = orig
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return {"run": cmd_run, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
