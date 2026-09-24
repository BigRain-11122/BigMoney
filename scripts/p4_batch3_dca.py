"""P4-B3-DCA: staged vs single-shot mechanism-level comparison (zoo #14,
T-2026-09-25-44, lane bm-b per MSG-20260925-0410).

Pre-registered in research/P4_BATCH3.md BEFORE any run (frozen commit prior
to any command touching batch products, R99 law). Iron rules: no threshold
tuning, no re-run after results (BACKTEST_PLAN rule 3), cutoff lockbox
2026-09-24 (new bars never flow back), OOS blind + costs always on.

Fixed faces (prereg sec.0/sec.3), NO search:
  2 oversold triggers x 2 entry modes x 2 exit regimes x 2 cost faces
  = 16 cell runs
    triggers (constructions verbatim = p4_batch1_screen.build_entries,
              frozen prereg P4_BATCH1.md sec.3, imported zero-rewrite):
      ovb    = oversold_bounce_20_15 (zoo#9 state, params={})
      low252 = low252_prox_top5_r20   (zoo#12 rotation, top5 asc frozen 20d)
    entry modes:
      single = legacy engine path (staged_entry=None, T-42 byte-identity)
      staged = staged_entry {"grid_fracs": (0.40, 0.30, 0.30),
                            "add_triggers": (0.0, -0.05, -0.10)}
               (spec sec.2 frozen values; VWAP accounting, hwm/trailing
                not reset, max_adds=2 cap)
    exit regimes: default | CE registration contract
    cost faces:   x1 (V1 legacy 13bp) | x2 (CostPatch 2.0 stress)
  + 100 random-signal nulls (50/exit regime, p {0.02,0.05} x 25 seeds,
    seed base 56_500 per SEED_REGISTRY['p4_batch3_dca'], single-shot)
  + 2 passive baselines (J8 formulas, consistency info)
  + 6 NAMED_SIX registered-member anchor reruns (hard gate, own cutoffs)
  + 1 PROS-OVB-CE-01 member_run (D6 nearest-kin reference, spec sec.5)
  = 125 trials (prereg sec.0 N_eff count, frozen).

PRIMARY READOUT FACE (prereg sec.4, the batch's first verdict): per
(trigger, exit) pair -- dSharpe / dMaxDrawdown / stop-bite rate
(reason=="stop_loss" share of all closed legs; both sides + delta +
per-cell exit-reason histogram disclosed). No pass line on this face
(honest mechanism-level reading); G1' v2 remains the only registration
gate.

Gates: G1' v2 via science_gates.g1_prime_v2 (data-driven skill line,
zero hand-copied constants); G1' passers only -> informational G2 face
(DSR via deflated_sharpe_ratio raw returns n_trials=125 + family PBO
via screening/pbo.cscv_pbo 8 blocks on the same-trigger 4-cell family
grid {single,staged} x {def,ce}, g25_retro precedent). Registration =
separate prereg (GRID-P1 convention unchanged).

D6 (prereg sec.1): registered face line 0.70 vs NAMED_SIX +
PROS-OVB-CE-01 -> REJECT from candidate pool (mechanism-novelty
clause; the paired judgment face is NOT invalidated by D6 rejection).
Same-batch face = T-33 merge semantics, generalized: cells that pass
G1' + registered-face D6 are walked in the FROZEN priority order
below; a cell with |corr| >= 0.70 vs an earlier-standing survivor
merges into it (merged cells are never merge targets). Priority order
(earlier = higher priority, frozen at zero cells, r71 protocol):
  (ovb,single,default) (ovb,staged,default) (ovb,single,ce)
  (ovb,staged,ce) (low252,single,default) (low252,staged,default)
  (low252,single,ce) (low252,staged,ce)

Hard gates (any FAIL = batch VOID, exit 2, no verdicts): patch
self-test, 48/48 panel at cutoff, NAMED_SIX anchor reproduction 6/6
(PAPER_LEVELS membership). PROS-OVB-CE-01 load failure = D6 reference
gap disclosed honestly, NOT a void condition (prereg sec.2).
Checkpoint row-level resume (t22 law) for cells + nulls; finalize
reads the checkpoint file, never in-memory state (T-33 law);
finalize single-shot guard (OUT_JSON exists -> refuse).

Usage: python scripts/p4_batch3_dca.py run | selftest
Products: results/shortline_p4_batch3.json
+ research/shortline/p4_batch3_results.csv + gate_attrition row
+ trials-ledger append (finalize, single-shot guard).
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

TICKET = "T-2026-09-25-44"
PREREG_PATH = os.path.join("research", "P4_BATCH3.md")
CUTOFF = "2026-09-24"            # prereg sec.2 lockbox (pinned, no reflow)
BATCH_CELLS = 125                # prereg sec.0 N_eff count (frozen)
N_RAND = 50                      # per exit regime (prereg sec.3)
BASELINE_P = (0.02, 0.05)        # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 56_500               # SEED_REGISTRY['p4_batch3_dca'] (this batch)
D6_LINE = 0.70                   # prereg sec.1 rejection line
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
STAGED = {"grid_fracs": (0.40, 0.30, 0.30),
          "add_triggers": (0.0, -0.05, -0.10)}   # spec sec.2 frozen
STAGED_METRIC_KEYS = ("num_adds_filled", "num_adds_dropped",
                      "avg_cost_first", "avg_cost_end", "adds_per_entry")
TRIGGERS = ("ovb", "low252")
MODES = ("single", "staged")
REGIMES = ("default", "ce")
FACES = ("x1", "x2")
# frozen same-batch D6 priority order (earlier = higher priority)
PRIO = [("ovb", "single", "default"), ("ovb", "staged", "default"),
        ("ovb", "single", "ce"), ("ovb", "staged", "ce"),
        ("low252", "single", "default"), ("low252", "staged", "default"),
        ("low252", "single", "ce"), ("low252", "staged", "ce")]
NAMED_SIX = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
             "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
D6_KIN = "PROS-OVB-CE-01"        # spec sec.5 nearest-kin reference
OOS_START = "2025-01-01"
OUT_JSON = os.path.join("results", "shortline_p4_batch3.json")
OUT_CSV = os.path.join("research", "shortline", "p4_batch3_results.csv")
CELLS_PATH = os.path.join("results", "p4_batch3_cells.jsonl")
ATT_JSON = os.path.join("results", "gate_attrition.json")
LOG_PATH = os.path.join("results", "p4_batch3.log")


def _log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def _sha256_file(path):
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _pearson(a: pd.Series, b: pd.Series) -> float:
    """Inner-join by date (r69 date-alignment law), min 20 overlap days."""
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def _false_panel(idx, syms):
    return pd.DataFrame(False, index=idx, columns=syms)


def cell_key(trig, mode, regime, face):
    return f"cell|{trig}|{mode}|{regime}|{face}"


def null_seed(regime: str, k: int) -> int:
    """Prereg sec.3 seed recipe: default 56_500+k, ce 56_550+k (k<50)."""
    return SEED_BASE + (k if regime == "default" else N_RAND + k)


def null_entry(idx, syms, p: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame((rng.random((len(idx), len(syms))) < p).astype(int),
                        index=idx, columns=syms)


def stop_bite_face(trades):
    """Stop-bite rate = stop_loss legs / all closed legs (prereg sec.4).
    Every trade record is a sell leg; tier scale-outs count in the
    denominator, stop_loss always closes 100%."""
    n_legs = len(trades)
    hist = {}
    for tr in trades:
        hist[tr["reason"]] = hist.get(tr["reason"], 0) + 1
    n_stop = hist.get("stop_loss", 0)
    return {"n_exit_legs": n_legs, "n_stop_loss": n_stop,
            "stop_bite_rate": round(n_stop / n_legs, 6) if n_legs else 0.0,
            "exit_reasons": hist}


def build_triggers(P: dict):
    """Two oversold triggers, constructions VERBATIM from the frozen
    batch-1 prereg (p4_batch1_screen.build_entries = single source of
    truth, imported zero-rewrite; report_num_entries=True added as a
    metrics-only disclosure flag, zero engine behavior change)."""
    from p4_batch1_screen import build_entries as b1_entries
    wanted = {"oversold_bounce_20_15": "ovb",
              "low252_prox_top5_r20": "low252"}
    out = {}
    for (name, family, params, entry, exit_, note) in b1_entries(P):
        if name not in wanted:
            continue
        pp = dict(params or {})
        pp["report_num_entries"] = True
        out[wanted[name]] = {"name": name, "family": family, "params": pp,
                             "entry": entry, "exit": exit_, "note": note}
    missing = set(wanted.values()) - set(out)
    if missing:
        raise RuntimeError(f"batch1 construction import missing: {missing}")
    return out


def run_cell(prices, idx, entry, exit_, params, ce, cost_mult=None,
             staged=None):
    """GRID-P1-isomorphic cell runner + staged_entry flag + stop-bite
    face (CostPatch single source, ExitPatch CE)."""
    from engine import run_backtest
    from live.paper import ExitPatch, seg_metrics
    import science_gates as sg
    pp = dict(params or {})
    if ce:
        pp.update(CE_PARAMS)
    cctx = sg.CostPatch(cost_mult) if cost_mult else nullcontext()
    xctx = ExitPatch(CE_OVERRIDES) if ce else nullcontext()
    with cctx, xctx:
        res = run_backtest(prices, pp, entry_signal=entry, exit_signal=exit_,
                           staged_entry=staged)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_ts = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    sb = stop_bite_face(res["trades"])
    staged_m = {k: res["metrics"][k] for k in STAGED_METRIC_KEYS
                if k in res["metrics"]}
    return {"eq": eq, "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"],
            "n_entries": res["metrics"].get("num_entries", -1),
            "oos_trades": oos_ts, "stop_bite": sb, "staged_metrics": staged_m}


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

def d6_same_batch_merge(passing, corr_fn, line: float = D6_LINE) -> dict:
    """Pure rule-selector (r71 double-reading fixture law applies).

    passing: list of (trig, mode, regime) tuples that passed G1' AND the
    registered-face D6 admission. Cells are walked in the frozen PRIO
    order; a cell whose |corr| >= line vs an earlier-standing SURVIVOR
    merges into the argmax-corr survivor (merged cells never become
    merge targets -- a later cell correlating only with a merged cell
    still stands, T-33 'merge target failed -> later stands' family).
    """
    out = {}
    survivors = []
    ordered = [c for c in PRIO if c in set(passing)]
    for cell in ordered:
        best, arg = 0.0, None
        for s in survivors:
            c = corr_fn(cell, s)
            if np.isfinite(c) and abs(c) >= line and abs(c) > best:
                best, arg = abs(c), s
        if arg is not None:
            out[cell] = {"survivor": False, "d6_same_batch": "d6-merged",
                         "merged_into": arg,
                         "max_corr_vs_earlier": round(best, 4)}
        else:
            out[cell] = {"survivor": True, "d6_same_batch": "unique",
                         "merged_into": None,
                         "max_corr_vs_earlier":
                             (round(best, 4) if best else None)}
            survivors.append(cell)
    return out


# --------------------------------------------------------------- anchor face

def anchor_ok_1x(t: dict, r1: dict) -> bool:
    """Registered 1x evidence reproduction (live.paper.anchor_gate core,
    member_run same code path; IS + OOS segment matches, tolerant keys)."""
    from live.paper import _evidence_matches, seg_metrics
    got_is = {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
              "trades": r1["n_trades"] - r1["oos_trades"]}
    got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
    return bool(_evidence_matches(got_is, t["backtest"]["in_sample"])
                and _evidence_matches(got_oos, t["backtest"]["out_sample"]))


# ------------------------------------------------------------------ finalize

def finalize(cell_rows, verdict_cells, pair_rows, nulls, passive_rows,
             anchors, gates, t0, void=False):
    import science_gates as sg
    from screening import pbo as pbo_mod
    if os.path.exists(OUT_JSON) and os.environ.get("P4B3_REFINALIZE") != "1":
        print("finalize refused: OUT_JSON exists (single-shot guard; "
              "P4B3_REFINALIZE=1 to redo)")
        return 2

    # ---- per-cell G1' v2 + registered-face D6 ----
    cand_rows = []
    line = None
    for c in verdict_cells:            # verdict face = x1 cost
        g1 = sg.g1_prime_v2(c["full"]["sharpe"], c["_rets"], BATCH_CELLS,
                            n_trades=c["n_trades"], n_entries=c["n_entries"])
        line = g1["skill_line"]
        reg_max, reg_arg = 0.0, None
        for rid, rseries in anchors["rets"].items():
            cc = abs(_pearson(c["_rets"], rseries))
            if np.isfinite(cc) and cc > reg_max:
                reg_max, reg_arg = cc, rid
        cand_rows.append({
            "cell": "|".join(c["key"].split("|")[1:4]),
            "trigger": c["trigger"], "entry_mode": c["mode"],
            "exit_regime": c["regime"],
            "sharpe_full": c["full"]["sharpe"],
            "annual_return": c["full"]["annual_return"],
            "max_drawdown": c["full"]["max_drawdown"],
            "oos_sharpe": c["oos"]["sharpe"],
            "oos_annual_return": c["oos"]["annual_return"],
            "n_trades": c["n_trades"], "n_entries": c["n_entries"],
            "stop_bite_rate": c["stop_bite"]["stop_bite_rate"],
            "x2_full_sharpe": c["x2_full_sharpe"],
            "x2_oos_sharpe": c["x2_oos_sharpe"],
            "staged_metrics": c.get("staged_metrics", {}),
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

    # ---- same-batch D6 merge (T-33 semantics, frozen PRIO order) ----
    admitted = [r for r in cand_rows if r["g1_pass"] and r["d6"]["registered_ok"]]
    passing = [(r["trigger"], r["entry_mode"], r["exit_regime"])
               for r in admitted]
    rets_by_cell = {c["key"]: c["_rets"] for c in verdict_cells}

    def corr_fn(a, b):
        ka = cell_key(a[0], a[1], a[2], "x1")
        kb = cell_key(b[0], b[1], b[2], "x1")
        return _pearson(rets_by_cell[ka], rets_by_cell[kb])

    d6m = d6_same_batch_merge(passing, corr_fn) if passing else {}
    for r in cand_rows:
        t3 = (r["trigger"], r["entry_mode"], r["exit_regime"])
        r["d6"]["same_batch"] = (d6m.get(t3, {}).get("d6_same_batch")
                                 if t3 in d6m else "not_admitted")
        r["d6"]["merged_into"] = d6m.get(t3, {}).get("merged_into")
        r["d6"]["max_corr_vs_earlier"] = d6m.get(t3, {}).get(
            "max_corr_vs_earlier")
    survivors = [f"{r['cell']}" for r in cand_rows
                 if d6m.get((r["trigger"], r["entry_mode"],
                             r["exit_regime"]), {}).get("survivor")]

    # ---- informational G2 face: G1' passers only (prereg sec.4) ----
    g2_face = []
    for r in cand_rows:
        if not r["g1_pass"]:
            continue
        c = next(x for x in verdict_cells
                 if x["trigger"] == r["trigger"]
                 and x["mode"] == r["entry_mode"]
                 and x["regime"] == r["exit_regime"])
        dsr = sg.deflated_sharpe_ratio(c["_rets"], BATCH_CELLS)
        fam = {cell_key(r["trigger"], m, reg, "x1"): rets_by_cell[
                   cell_key(r["trigger"], m, reg, "x1")]
               for m in MODES for reg in REGIMES}
        pb = pbo_mod.cscv_pbo(pbo_mod.align_returns(fam))
        g2 = sg.g2_registration_v2(True, dsr["dsr"], pb["pbo"])
        g2_face.append({
            "cell": r["cell"],
            "dsr": round(dsr["dsr"], 4),
            "dsr_sr_annualized": round(dsr["sr_annualized"], 4),
            "family_pbo": round(pb["pbo"], 4),
            "family_pbo_verdict": pb["verdict"],
            "family_grid": [k for k in fam],
            "g2_registration_v2": g2,
        })

    led = None
    if not void:
        led = sg.append_ledger("P4-B3-DCA", BATCH_CELLS,
                               file_name="results/shortline_p4_batch3.json",
                               evidence_cutoff=CUTOFF,
                               note="16 cells (8 x x1+x2) + 100 nulls + 2"
                                    " passive + 6 NAMED_SIX anchors + 1"
                                    " PROS-OVB D6 ref; prereg"
                                    " research/P4_BATCH3.md frozen pre-run")
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        att["entries"].append({
            "batch": "P4-B3-DCA", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement", "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": led["total"],
            "gates": {
                "skill_line_v2": None if line is None else line["line"],
                "g1_prime_v2_pass": len([r for r in cand_rows
                                         if r["g1_pass"]]),
                "d6_registered_rejects": [r["cell"] for r in cand_rows
                                          if r["g1_pass"]
                                          and not r["d6"]["registered_ok"]],
                "d6_same_batch_merged": [r["cell"] for r in cand_rows
                                         if r["d6"].get("merged_into")],
                "anchor_repro_all_pass": bool(gates["anchors_ok"]),
                "g2_info_face": {g["cell"]: {
                    "dsr": g["dsr"], "family_pbo": g["family_pbo"]}
                    for g in g2_face},
                "best_cell": (max(cand_rows,
                                  key=lambda r: r["sharpe_full"])["cell"]
                              if cand_rows else None),
                "best_full_sharpe": (round(max(r["sharpe_full"]
                                                for r in cand_rows), 4)
                                     if cand_rows else None),
                "pair_delta_sharpe": {f"{p['trigger']}@{p['exit_regime']}":
                                      p["delta_sharpe"] for p in pair_rows},
            },
            "eliminated": (len(cand_rows) - len(survivors)) if cand_rows
                          else 0,
            "refs": {"results": "results/shortline_p4_batch3.json",
                     "prereg": "research/P4_BATCH3.md",
                     "csv": "research/shortline/p4_batch3_results.csv",
                     "ticket": TICKET},
        })
        with open(ATT_JSON, "w", encoding="utf-8") as fh:
            json.dump(att, fh, ensure_ascii=False, indent=1)

    def _cell_public(c):
        return {k: v for k, v in c.items()
                if k not in ("_rets", "_eq_index", "key")}

    out = {
        **sg.cutoff_meta(CUTOFF),
        "batch": "P4-B3-DCA", "ticket": TICKET,
        "prereg": "research/P4_BATCH3.md",
        "prereg_sha256_16": _sha256_file(PREREG_PATH)[:16],
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "void": bool(void),
        "universe": {"pool": "core48-bare-codes", "cutoff": CUTOFF,
                     "oos_start": OOS_START,
                     "data_end_raw": gates["data_end_raw"]},
        "hard_gates": {k: gates[k] for k in
                       ("patch_selftest", "panel", "anchors_ok")},
        "staged_params": STAGED,
        "cost": "V1 legacy 13bp base + CostPatch(2.0) x2 stress face",
        "cells": [_cell_public(c) for c in cell_rows],
        "candidates": cand_rows,
        "paired_judgment_face": pair_rows,
        "g2_informational_face": g2_face,
        "nulls": nulls, "passive": passive_rows,
        "anchors": {"repro": anchors.get("repro", []),
                    "n_members": len(anchors.get("repro", [])),
                    "d6_kin_ref": {
                        "member": D6_KIN,
                        "available": D6_KIN in anchors.get("rets", {}),
                        "note": "spec sec.5 nearest-kin (oversold sleeve2"
                                " family); load failure = disclosed gap,"
                                " not a void condition"}},
        "d6_resolution": ("registered face: line 0.70 vs NAMED_SIX + "
                         "PROS-OVB-CE-01, REJECT on >= (mechanism-novelty"
                         " clause); same-batch face: T-33 merge semantics"
                         " generalized, frozen PRIO order in runner "
                         "docstring (r71 zero-cells protocol); per-pair "
                         "values disclosed per candidate"),
        "survivors_g1_prime": survivors,
        "survivors_are": ("G1' CANDIDATES ONLY -- no registration this "
                          "batch; registration requires a separate "
                          "pre-registration (GRID-P1 convention)"),
        "trials_ledger": led,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": (sum(1 for c in cell_rows
                                      if c.get("status") == "ok")
                                  + len(nulls.get("rows", []))
                                  + len(anchors.get("repro", []))
                                  + (1 if D6_KIN in anchors.get("rets", {})
                                     else 0)),
                  "workers": 1, "cpu_parallel": "serial (single-process)",
                  "prereg_frozen_before_run": True},
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    print(f"saved: {OUT_JSON}")

    import csv as _csv
    cols = ["name", "trigger", "entry_mode", "exit_regime", "cost_face",
            "status", "n_trades", "n_entries", "annual_return", "sharpe",
            "max_drawdown", "oos_sharpe", "oos_annual_return",
            "stop_bite_rate", "skill_line", "g1_pass",
            "d6_registered_ok", "d6_same_batch", "delta_sharpe",
            "delta_max_drawdown", "delta_stop_bite", "note"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for c in cell_rows:
            t3 = (c.get("trigger"), c.get("mode"), c.get("regime"))
            grow = next((r for r in cand_rows
                         if (r["trigger"], r["entry_mode"],
                             r["exit_regime"]) == t3), None)
            prow = next((p for p in pair_rows
                         if p["trigger"] == c.get("trigger")
                         and p["exit_regime"] == c.get("regime")), None)
            w.writerow([
                c.get("name", ""), c.get("trigger", ""), c.get("mode", ""),
                c.get("regime", ""), c.get("cost_face", ""),
                c.get("status", ""), c.get("n_trades", ""),
                c.get("n_entries", ""),
                c.get("full", {}).get("annual_return", ""),
                c.get("full", {}).get("sharpe", ""),
                c.get("full", {}).get("max_drawdown", ""),
                c.get("oos", {}).get("sharpe", ""),
                c.get("oos", {}).get("annual_return", ""),
                c.get("stop_bite", {}).get("stop_bite_rate", ""),
                (grow["g1_prime_v2"]["skill_line"]["line"]
                 if grow else ""),
                (grow["g1_pass"] if grow else ""),
                (grow["d6"]["registered_ok"] if grow else ""),
                (grow["d6"].get("same_batch", "") if grow else ""),
                (prow["delta_sharpe"] if (prow and c.get("cost_face")
                                          == "x1") else ""),
                (prow["delta_max_drawdown"] if (prow and c.get("cost_face")
                                                == "x1") else ""),
                (prow["delta_stop_bite"] if (prow and c.get("cost_face")
                                             == "x1") else ""),
                c.get("note", "")])
        for r in nulls.get("rows", []):
            w.writerow([r["name"], "", r["exit_regime"], "x1", "ok", "", "",
                        r["full"]["annual_return"], r["full"]["sharpe"],
                        r["full"]["max_drawdown"], r["oos"]["sharpe"],
                        r["oos"]["annual_return"], "", "", "", "", "", "",
                        "", f"p={r['p']} seed={r['seed']}"])
        for k, v in passive_rows.items():
            w.writerow([k, "passive_null", "none", "formula", "ok", 0, 0,
                        v["full"]["annual_return"], v["full"]["sharpe"],
                        v["full"]["max_drawdown"], v["oos"]["sharpe"],
                        v["oos"]["annual_return"], "", "", "", "", "", "",
                        "", "J8 formula, consistency info"])
    print(f"saved: {OUT_CSV}")
    print(f"survivors: {survivors}")
    print("paired face (dSharpe staged-single): "
          + ", ".join(f"{p['trigger']}@{p['exit_regime']}="
                      f"{p['delta_sharpe']:+.4f}" for p in pair_rows))
    return 0


# ---------------------------------------------------------------------- run

def cmd_run(_) -> int:
    t0 = time.time()
    from live.paper import (PAPER_LEVELS, build_panels, load_core,
                            seg_metrics, self_test_patches)
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

    trig = build_triggers(P)
    done = load_rows(CELLS_PATH)

    # ---------- cells: 2 triggers x 2 modes x 2 regimes x 2 faces ----------
    for tk in TRIGGERS:
        T = trig[tk]
        for mode in MODES:
            staged = dict(STAGED) if mode == "staged" else None
            for ce in (False, True):
                regime = "ce" if ce else "default"
                for face, mult in (("x1", None), ("x2", 2.0)):
                    key = cell_key(tk, mode, regime, face)
                    if key in done:
                        _log(f"cell {key}: resume-skip")
                        continue
                    try:
                        r = run_cell(prices, idx, T["entry"], T["exit"],
                                     T["params"], ce, mult, staged)
                        row = {"key": key, "name": T["name"],
                               "family": T["family"], "trigger": tk,
                               "mode": mode, "regime": regime,
                               "cost_face": face, "status": "ok",
                               "full": {k: (round(float(v), 6)
                                            if isinstance(v, (int, float))
                                            else v)
                                        for k, v in r["full"].items()},
                               "oos": {k: round(float(v), 6)
                                       for k, v in r["oos"].items()},
                               "n_trades": r["n_trades"],
                               "n_entries": r["n_entries"],
                               "oos_trades": r["oos_trades"],
                               "stop_bite": r["stop_bite"],
                               "staged_metrics": r["staged_metrics"],
                               "note": T["note"]}
                        if face == "x1":
                            rets = r["eq"].pct_change().dropna()
                            row["_rets"] = [round(float(x), 8)
                                            for x in rets.to_numpy()]
                            row["_eq_index"] = [str(d.date())
                                                for d in r["eq"].index]
                        _append_row(row)
                        _log(f"cell {key}: s={r['full']['sharpe']:.4f} "
                             f"sb={r['stop_bite']['stop_bite_rate']:.4f} "
                             f"trades={r['n_trades']}")
                    except Exception as ex:
                        _append_row({"key": key, "trigger": tk, "mode": mode,
                                     "regime": regime, "cost_face": face,
                                     "status": f"cell_error: "
                                               f"{type(ex).__name__}: {ex}"})
                        _log(f"cell {key}: ERROR {ex}")

    # ---------- nulls: 50 per exit regime, single-shot (checkpointed) ------
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
    cell_rows, keys16 = [], []
    for tk in TRIGGERS:
        for mode in MODES:
            for reg in REGIMES:
                for face in FACES:
                    k = cell_key(tk, mode, reg, face)
                    keys16.append(k)
                    if k in rows:
                        cell_rows.append(rows[k])
    null_rows = [rows[k] for k in rows
                 if k.startswith("null|") and rows[k].get("status") == "ok"]
    gates = {"patch_selftest": True, "panel": True, "anchors_ok": False,
             "data_end_raw": data_end_raw}
    if len(cell_rows) != 16 or any(c["status"] != "ok" for c in cell_rows):
        _log(f"cells incomplete: {len(cell_rows)}/16 ok -- VOID (no verdict)")
        return finalize(cell_rows, [], [], {"rows": null_rows, "summary": {}},
                        {}, {"repro": [], "rets": {}}, gates, t0, void=True)
    if len(null_rows) != 2 * N_RAND:
        _log(f"nulls incomplete: {len(null_rows)}/{2 * N_RAND} -- VOID")
        return finalize(cell_rows, [], [], {"rows": null_rows, "summary": {}},
                        {}, {"repro": [], "rets": {}}, gates, t0, void=True)

    # verdict cells = x1 faces, DatetimeIndex re-attached (r69 law),
    # x2 stress sharpes wired in from the x2 rows
    verdict_cells = []
    for tk in TRIGGERS:
        for mode in MODES:
            for reg in REGIMES:
                c = dict(rows[cell_key(tk, mode, reg, "x1")])
                x2r = rows[cell_key(tk, mode, reg, "x2")]
                c["x2_full_sharpe"] = x2r["full"]["sharpe"]
                c["x2_oos_sharpe"] = x2r["oos"]["sharpe"]
                c["_rets"] = pd.Series(c["_rets"],
                                       index=pd.DatetimeIndex(c["_eq_index"][1:]))
                c.pop("_eq_index", None)
                verdict_cells.append(c)

    # ---------- primary readout: paired judgment face (prereg sec.4) ------
    pair_rows = []
    for tk in TRIGGERS:
        for reg in REGIMES:
            s = rows[cell_key(tk, "single", reg, "x1")]
            t = rows[cell_key(tk, "staged", reg, "x1")]
            pair_rows.append({
                "trigger": tk, "exit_regime": reg,
                "single": {"sharpe_full": s["full"]["sharpe"],
                           "max_drawdown": s["full"]["max_drawdown"],
                           "stop_bite_rate": s["stop_bite"]["stop_bite_rate"],
                           "n_trades": s["n_trades"],
                           "exit_reasons": s["stop_bite"]["exit_reasons"]},
                "staged": {"sharpe_full": t["full"]["sharpe"],
                           "max_drawdown": t["full"]["max_drawdown"],
                           "stop_bite_rate": t["stop_bite"]["stop_bite_rate"],
                           "n_trades": t["n_trades"],
                           "exit_reasons": t["stop_bite"]["exit_reasons"],
                           "staged_metrics": t.get("staged_metrics", {})},
                "delta_sharpe": round(t["full"]["sharpe"]
                                      - s["full"]["sharpe"], 6),
                "delta_max_drawdown": round(t["full"]["max_drawdown"]
                                            - s["full"]["max_drawdown"], 6),
                "delta_stop_bite": round(t["stop_bite"]["stop_bite_rate"]
                                         - s["stop_bite"]["stop_bite_rate"],
                                         6),
            })
    for p in pair_rows:
        _log(f"pair {p['trigger']}@{p['exit_regime']}: "
             f"dSharpe={p['delta_sharpe']:+.4f} "
             f"dBdd={p['delta_max_drawdown']:+.4f} "
             f"dsb={p['delta_stop_bite']:+.4f}")

    # ---------- nulls summary (in-batch controls, disclosure) -------------
    nulls_vals = [float(r["full"]["sharpe"]) for r in null_rows]
    p95 = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in null_rows
         if r["exit_regime"] == reg], 95)), 4) for reg in REGIMES}
    nulls = {"rows": null_rows,
             "summary": {"n": len(null_rows),
                         "mu": round(float(np.mean(nulls_vals)), 4),
                         "sigma": round(float(np.std(nulls_vals, ddof=1)), 4),
                         "p95_inbatch_full": p95,
                         "note": "in-batch single-shot controls "
                                 "(disclosure); skill line is data-driven "
                                 "from the shared collector"}}

    # ---------- passive baselines (consistency info) ----------------------
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee
                 + fee.supervision_fee + fee.slippage_a)
    passive_rows = {}
    for k, eq in (("ew48_buyhold", passive_buyhold(close, cost_rate)),
                  ("ew48_monthly_rebal",
                   passive_monthly_rebal(close, cost_rate))):
        passive_rows[k] = {"full": seg_metrics(eq),
                           "oos": seg_metrics(eq, OOS_START)}
    _log(f"passive: bh_s={passive_rows['ew48_buyhold']['full']['sharpe']:.4f}"
         f" mr_s={passive_rows['ew48_monthly_rebal']['full']['sharpe']:.4f}")

    # ---------- anchors: NAMED_SIX hard gate + PROS-OVB D6 reference ------
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
    try:
        kin = load_trader(D6_KIN)
        r1 = member_run(kin, prices_full)
        anchors["rets"][D6_KIN] = r1["eq"].pct_change().dropna()
        anchors["repro"].append({"member": D6_KIN, "anchor_ok": None,
                                 "d6_kin_ref": True,
                                 "cutoff": r1["cutoff"],
                                 "full_sharpe": round(r1["full"]["sharpe"], 4)})
        _log(f"D6 kin ref {D6_KIN}: full_s={r1['full']['sharpe']:.4f} "
             f"(reference, not a hard gate)")
    except Exception as ex:
        _log(f"D6 kin ref {D6_KIN}: LOAD FAILED -> disclosed gap ({ex}); "
             "judgment face unaffected (prereg sec.2)")
    if not anchors_ok or len([a for a in anchors["repro"]
                              if not a.get("d6_kin_ref")]) != 6:
        _log("ANCHOR gate FAILED -- batch VOID (prereg sec.2)")
        return finalize(cell_rows, verdict_cells, pair_rows, nulls,
                        passive_rows, anchors, gates, t0, void=True)

    gates["anchors_ok"] = True
    _log("all hard gates PASS -- finalizing")
    return finalize(cell_rows, verdict_cells, pair_rows, nulls, passive_rows,
                    anchors, gates, t0)


# ----------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    import tempfile
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("P4-B3-DCA runner selftest (offline hermetic, zero repo products):")
    # -- seed recipe: disjoint families inside the registered band
    sd = [null_seed("default", k) for k in range(N_RAND)]
    sc = [null_seed("ce", k) for k in range(N_RAND)]
    ok("seed families disjoint + banded + deterministic",
       not (set(sd) & set(sc)) and sd == list(range(56_500, 56_550))
       and sc == list(range(56_550, 56_600)) and sd[0] == 56_500)
    # -- null entry panel: deterministic, binary, shape
    idx = pd.date_range("2020-01-02", periods=40, freq="B")
    e1 = null_entry(idx, ["a", "b"], 0.05, 56_500)
    ok("null entry deterministic + binary",
       e1.equals(null_entry(idx, ["a", "b"], 0.05, 56_500))
       and set(np.unique(e1.to_numpy())) <= {0, 1} and e1.shape == (40, 2))
    # -- staged params sanity (spec sec.2 frozen values)
    ok("staged fracs sum <= 1.0 + triggers align 1:1",
       sum(STAGED["grid_fracs"]) <= 1.0
       and len(STAGED["grid_fracs"]) == len(STAGED["add_triggers"])
       and STAGED["add_triggers"][0] == 0.0)
    # -- stop-bite face: synthetic trades histogram
    sb = stop_bite_face([{"reason": "stop_loss"}, {"reason": "stop_loss"},
                         {"reason": "take_profit_tier_1"},
                         {"reason": "signal_reversal"}])
    ok("stop-bite 2/4 + histogram",
       sb["n_exit_legs"] == 4 and sb["n_stop_loss"] == 2
       and abs(sb["stop_bite_rate"] - 0.5) < 1e-9
       and sb["exit_reasons"]["stop_loss"] == 2)
    ok("stop-bite zero-legs edge", stop_bite_face([])["stop_bite_rate"] == 0.0)
    # -- cell-key/prio integrity: 8 keys unique, PRIO = frozen order
    keys = [cell_key(*p, "x1") for p in PRIO]
    ok("PRIO 8 unique cells + key builder round-trip",
       len(set(keys)) == 8
       and set(keys) == {cell_key(t, m, r, "x1")
                         for t in TRIGGERS for m in MODES
                         for r in REGIMES})
    # -- D6 same-batch merge: three-state fixtures (r71 double-reading law)
    corr_map = {}

    def corr_fn(a, b):
        return corr_map.get((a, b), corr_map.get((b, a), 0.0))

    r = d6_same_batch_merge([PRIO[0], PRIO[1]], corr_fn)
    ok("D6 both-pass + low corr -> both survivors",
       r[PRIO[0]]["survivor"] and r[PRIO[1]]["survivor"]
       and r[PRIO[1]]["d6_same_batch"] == "unique")
    corr_map[(PRIO[0], PRIO[1])] = 0.88
    r = d6_same_batch_merge([PRIO[0], PRIO[1]], corr_fn)
    ok("D6 both-pass + corr>=0.70 -> later merges into earlier",
       r[PRIO[0]]["survivor"] and not r[PRIO[1]]["survivor"]
       and r[PRIO[1]]["d6_same_batch"] == "d6-merged"
       and r[PRIO[1]]["merged_into"] == PRIO[0])
    corr_map[(PRIO[0], PRIO[1])] = 0.70
    r = d6_same_batch_merge([PRIO[0], PRIO[1]], corr_fn)
    ok("D6 boundary corr==0.70 merges (frozen >= semantics)",
       r[PRIO[1]]["d6_same_batch"] == "d6-merged")
    corr_map[(PRIO[0], PRIO[1])] = 0.95
    r = d6_same_batch_merge([PRIO[1]], corr_fn)
    ok("D6 merge target absent -> later cell stands",
       r[PRIO[1]]["survivor"] and r[PRIO[1]]["d6_same_batch"] == "unique")
    # three-cell chain: B merges into A; C correlates only with merged B
    corr_map.clear()
    corr_map[(PRIO[0], PRIO[1])] = 0.90
    corr_map[(PRIO[1], PRIO[2])] = 0.95
    r = d6_same_batch_merge([PRIO[0], PRIO[1], PRIO[2]], corr_fn)
    ok("D6 merged cells never merge targets -> C stands",
       r[PRIO[2]]["survivor"] and r[PRIO[1]]["merged_into"] == PRIO[0]
       and r[PRIO[2]]["d6_same_batch"] == "unique")
    r = d6_same_batch_merge([], corr_fn)
    ok("D6 empty passing -> empty result", r == {})
    corr_map.clear()
    corr_map[(PRIO[0], PRIO[1])] = float("nan")
    r = d6_same_batch_merge([PRIO[0], PRIO[1]], corr_fn)
    ok("D6 nan corr -> no merge (honest)",
       r[PRIO[1]]["d6_same_batch"] == "unique")
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
    # -- anchor 1x face: tolerant key names + exact-match semantics
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
