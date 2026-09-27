"""TRIAL_LABOR_W1 runner -- T-94 s2/s3/s4 mass-candidate trial wave-1.

Prereg FROZEN (R99): research/TRIAL_LABOR_W1_PREREG.md (r347 bm-b,
commit fe0fa81c + sec.9.3 P-5C census-grid binding f92993e5).
Laws: firm/TRIAL_LABOR_LAW v1.0 + firm/RANDOM_LARGE_SAMPLE_LAW +
firm/REFINE_BENCH_LAW + research/BACKTEST_SCIENCE.md v2.

Import-face reuse (zero rewrite, prereg sec.6):
  engine.run_backtest / engine.exit_rules (untouched), strategies/ factory
  (81 fns/13 modules), live.paper (SIGNAL_BUILDERS faces, anchor_gate,
  build_panels, load_core, ExitPatch, self_test_patches, v3_state_series),
  scripts/p5c_virtual_timepoint (EVIDENCE_CUTOFF_GRID, FROZEN_CENSUS,
  MIN_LISTED, LEG_* floors, _load_leg/_census -- sec.9.3 wholesale binding),
  scripts/p5_random_entry (passive_rel, slice_metrics, WARMUP_TD),
  scripts/parallel_runner (run_cells_parallel + on_result incremental
  persistence, r340 pitlaw), scripts/science_gates (g1_prime_v2,
  g2_registration_v2, append_ledger, cutoff_meta, ledger_head,
  deflated_sharpe_ratio, SEED_REGISTRY, _norm_cdf), screening/pbo.py.

Subcommands (prereg sec.6):
  generate          grammar freeze + uniform draws + exclusion + dedup
                    (LIGHT: zero engine cells burned; naive-hold face)
  screen-prep       G-PANEL/G-CENSUS/G-ANCHOR/G-EXCLUDE + passive 6m precompute
  screen            sharded cell burn (candidates + K=200 nulls, leg-L full
                    history one backtest per cell -> beat6m rows),
                    checkpoint jsonl append-per-cell (kill-safe resume)
  screen-finalize   null p95 survival line + ledger append + products
  judge             survivor cells (dual-axis leg-L + leg-D full curves,
                    window grid, regime segments, G1'/DSR inputs, dual nulls)
  judge-finalize    family PBO (CSCV) + G2 + E[FP] + ledger + product
  intake            s4 D6 binding gate + registration rows (pipeline face)
  status            checkpoint progress readout
  selftest          hermetic offline fixtures (r116 law; no repo data files)

Exit codes: 0 = ok/no-op, 1 = gate fail (VOID, zero products), 2 = machinery
error / blocked dependency (honest report, never mask).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (ANCHOR_TOL, OOS_START, ExitPatch, anchor_gate,
                        build_panels, load_core, self_test_patches,
                        v3_state_series)
from p5_random_entry import WARMUP_TD, passive_rel
from parallel_runner import run_cells_parallel, worker_cap
from p5c_virtual_timepoint import (EVIDENCE_CUTOFF_GRID, FROZEN_CENSUS,
                                   LEG_D_CACHE, LEG_D_FLOOR, LEG_L_FLOOR,
                                   MIN_LISTED, WINDOWS, _census, _load_leg)
from science_gates import (SEED_REGISTRY, append_ledger, cutoff_meta,
                           deflated_sharpe_ratio, g1_prime_v2,
                           g2_registration_v2, ledger_head, _norm_cdf)
from screening.pbo import align_returns, cscv_pbo

# ------------------------------------------------------------------ frozen
WAVE = "TRIAL_LABOR_W1"
PREREG = "research/TRIAL_LABOR_W1_PREREG.md"
CUTOFF = EVIDENCE_CUTOFF_GRID                  # "2026-09-22" (sec.9.3 binding)
SEED_GEN = SEED_REGISTRY["trial_labor_w1_gen"]           # 20283500
SEED_NULL = SEED_REGISTRY["trial_labor_w1_scrnull"]      # 20284000
SEED_UNC = SEED_REGISTRY["trial_labor_w1_unc"]          # 20284500
N_PER_FAMILY = 500            # raw draws per family (prereg sec.0: cap not quota)
K_NULLS = 200                  # screen null family (prereg sec.3)
NULL_P_REGIMES = (0.02, 0.05)  # t18 family-A Bernoulli precedent
RES_DIR = os.path.join(PATHS.results_dir, "trial_labor_w1")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
GRAMMAR_LEDGER = os.path.join(PATHS.root, "research", "TRIAL_GRAMMAR_LEDGER.md")
P4_BATCH_CSVS = ["p4_batch1_results.csv", "p4_batch2a_results.csv",
                 "p4_folk_results.csv", "p4_queue_results.csv",
                 "p4_batch2_results.csv"]
T18_MANIFEST = os.path.join(PATHS.results_dir, "shortline",
                            "t18_deep_manifest.json")
B_LAYER_MASK = os.path.join("data", "fundamental", "b_layer_mask.csv")

# Registered six templates (family A anchors; configs frozen from the trader
# files' registered faces -- G-ANCHOR re-verifies each vs live.paper at
# screen-prep; module faces resolved via SIGNAL_BUILDERS lineage).
A_TEMPLATES = [
    {"trader_id": "VOLATILITY-CE-01", "module": "volatility",
     "fn": "low_vol_long",
     "sig_params": {"n": 60, "top_k": 5, "rebal_days": None},
     "registered_params": {"max_positions": 5, "position_size_pct": 0.1,
                           "time_decay_period": 25,
                           "time_decay_threshold": 0.05,
                           "trailing_stop_activate": 0.1},
     "registered_ovr": {"loss_time_days": 16},
     "entry_key": "low_vol_long(n=60, top_k=5, daily)"},
    {"trader_id": "COMPOSITE-CE-01", "module": "composite_rotation",
     "fn": "top_n_rotation", "sig_params": {"top_n": 5, "rebal_days": 20},
     "registered_params": {"max_positions": 5, "position_size_pct": 0.19,
                           "time_decay_period": 25,
                           "time_decay_threshold": 0.05,
                           "trailing_stop_activate": 0.1,
                           "take_profit_levels": [0.05, 0.08]},
     "registered_ovr": {"loss_time_days": 16,
                        "take_profit_fractions": [0.5, 0.5]},
     "entry_key": "top_n_rotation(composite, n=5, rebal_days=20)"},
    {"trader_id": "COMPOSITE-CE-02", "module": "composite_rotation",
     "fn": "top_n_rotation", "sig_params": {"top_n": 8, "rebal_days": 20},
     "registered_params": {"max_positions": 8, "position_size_pct": 0.1187,
                           "time_decay_period": 25,
                           "time_decay_threshold": 0.05,
                           "trailing_stop_activate": 0.03,
                           "take_profit_levels": [0.05, 0.08],
                           "trailing_lock": 0.05},
     "registered_ovr": {"loss_time_days": 16,
                        "take_profit_fractions": [0.5, 0.5]},
     "entry_key": "top_n_rotation(composite, n=8, rebal_days=20)"},
    {"trader_id": "ENGULF-CE-01", "module": "ta", "fn": "engulf_reversal",
     "sig_params": {"drop_th": -0.05},
     "registered_params": {"time_decay_period": 25,
                           "time_decay_threshold": 0.05,
                           "trailing_stop_activate": 0.03,
                           "take_profit_levels": [0.05, 0.08],
                           "trailing_lock": 0.05},
     "registered_ovr": {"loss_time_days": 16,
                        "take_profit_fractions": [0.5, 0.5]},
     "entry_key": "engulf_reversal(drop_th=-0.05)"},
    {"trader_id": "NEEDLE-DE-01", "module": "patterns", "fn": "needle_probe",
     "sig_params": {"drop_th": -0.05, "shadow_pct": 0.02},
     "registered_params": {},
     "registered_ovr": {},
     "entry_key": "needle_probe(drop_th=-0.05, shadow_pct=0.02)"},
    {"trader_id": "DROUGHT-CE-01", "module": "patterns",
     "fn": "vol_drought_reversal",
     "sig_params": {"vol_floor": 0.55, "drop_th": -0.05},
     "registered_params": {"time_decay_period": 25,
                           "time_decay_threshold": 0.05,
                           "trailing_stop_activate": 0.1},
     "registered_ovr": {"loss_time_days": 16},
     "entry_key": "vol_drought_reversal(vol_floor=0.55, drop_th=-0.05)"},
]

# Engine-chassis field (T-78 DD overlay): mechanically read from the LIVE
# trader files at import (never hand-copied); inherited by ALL family-A
# candidates (mother-engine chassis law -- signal params + axis grid vary,
# the registered chassis incl. dd_control does not). B-family: none.
# Not part of the serialized generation grammar (domains/axes/dedup) --
# G-ANCHOR re-verifies the whole chassis vs live.paper every screen-prep.
for _t in A_TEMPLATES:
    try:
        _t["registered_dd_control"] = load_trader(
            _t["trader_id"]).get("dd_control")
    except Exception:
        _t["registered_dd_control"] = None

# 12 non-grid strategy modules (grid module excluded by prereg sec.3)
B_MODULES = ["composite_rotation", "event", "folk", "macro", "mean_reversion",
             "momentum", "patterns", "seasonal", "sentiment", "ta", "trend",
             "volatility"]

# Axis grids (REFINE_BENCH_LAW sec.2 standard axes, discrete; frozen here,
# serialized verbatim into w1_grammar.json at generate time).
AXIS_FILTERS = ["none", "depth_thresh", "amplitude", "liquidity", "trend_slope",
                "dual_window", "fundamental_mask"]
AXIS_EXITS = ["template_default", "ce_machine", "time_stop_5d", "time_stop_7d",
              "time_stop_10d", "time_stop_20d", "trailing_stop",
              "profit_ladder"]
AXIS_SIZING = ["equal_weight", "inverse_vol", "cap20", "regime_delever"]
AXIS_TIMING = ["daily_signal", "weekly_grid"]

# Exit machines: {bridged engine kwargs} + {ExitPatch-only fields}. P1 signal
# reversal stays native (exit_signal = entry<=0). "Pure time stop N":
# time_decay fires at N days for ANY pnl<10.0 (never-true stop/tp disabled).
_TS_BASE = {
    "bridged": {"time_decay_period": 5, "time_decay_threshold": 10.0,
                "initial_stop": -1.0, "take_profit_levels": [10.0],
                "trailing_stop_activate": 10.0, "trailing_lock": 10.0},
    "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0]},
    "provenance": "pure holding-period exit (TRIAL_LABOR_LAW sec.3)",
}
EXIT_MACHINES = {
    "ce_machine": {
        "bridged": {"time_decay_period": 25, "time_decay_threshold": 0.05,
                    "trailing_stop_activate": 0.03,
                    "take_profit_levels": [0.05, 0.08], "trailing_lock": 0.05},
        "patch": {"loss_time_days": 16, "take_profit_fractions": [0.5, 0.5]},
        "provenance": "CE-registered machine (ENGULF/COMPOSITE-02 frozen face)"},
    "time_stop_5d": _TS_BASE,
    "time_stop_7d": {**_TS_BASE, "bridged": {**_TS_BASE["bridged"],
                                             "time_decay_period": 7}},
    "time_stop_10d": {**_TS_BASE, "bridged": {**_TS_BASE["bridged"],
                                              "time_decay_period": 10}},
    "time_stop_20d": {**_TS_BASE, "bridged": {**_TS_BASE["bridged"],
                                              "time_decay_period": 20}},
    "trailing_stop": {
        "bridged": {"trailing_stop_activate": 0.03, "trailing_lock": 0.03,
                    "initial_stop": -0.05, "take_profit_levels": [10.0],
                    "time_decay_period": 1000, "time_decay_threshold": 0.02},
        "patch": {"loss_time_days": 16, "take_profit_fractions": [1.0]},
        "provenance": "trailing-dominant machine (REFINE_BENCH sec.2)"},
    "profit_ladder": {
        "bridged": {"take_profit_levels": [0.03, 0.06, 0.10],
                    "trailing_stop_activate": 0.10, "trailing_lock": 0.01,
                    "initial_stop": -0.08, "time_decay_period": 25,
                    "time_decay_threshold": 0.02},
        "patch": {"loss_time_days": 16,
                  "take_profit_fractions": [1 / 3, 1 / 3, 1.0]},
        "provenance": "ladder-dominant machine (REFINE_BENCH sec.2)"},
}
BRIDGED_EXIT_KEYS = ("take_profit_levels", "trailing_stop_activate",
                     "trailing_lock", "initial_stop", "time_decay_period",
                     "time_decay_threshold")
DEFAULT_AXIS = ("none", "template_default", "equal_weight", "daily_signal")
REGIME_MAP = {"GREEN": "bull", "YELLOW": "chop", "ORANGE": "bear",
              "RED": "bear"}   # T-22 sec.3 frozen 3-way proxy (p5c verbatim)
BENCH_SYM = "510300"
GRAMMAR = None               # module global set by generate/screen/judge/selftest


# ------------------------------------------------------------- small helpers
def _j(x):
    """JSON-safe converter (numpy -> python primitives)."""
    if isinstance(x, dict):
        return {str(k): _j(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_j(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _dump(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(_j(payload), fh, ensure_ascii=False, indent=1,
                  default=float)


def _grammar_sha(grammar: dict) -> str:
    canon = json.dumps(_j({k: grammar[k] for k in sorted(grammar)
                           if k != "grammar_sha256"}), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ------------------------------------------------------- grammar construction
def _factory_inventory():
    """(module, fn) -> function object, per B_MODULES (grid excluded)."""
    inv = {}
    for m in B_MODULES:
        mod = __import__(f"strategies.{m}", fromlist=[m])
        for n, f in inspect.getmembers(mod, inspect.isfunction):
            if f.__module__ == f"strategies.{m}" and not n.startswith("_"):
                inv[(m, n)] = f
    return inv


def _param_domain(name, default):
    """Frozen uniform-draw value domain per parameter (rule-based, frozen at
    grammar build; prereg sec.3: serialized into w1_grammar.json)."""
    if name in ("top_k", "top_n", "n_targets"):
        return [3, 5, 8]
    if name == "month":
        return list(range(1, 13))
    if name == "weekday":
        return [0, 1, 2, 3, 4]
    if name == "window" and default in (2, 3, 5):
        return [2, 3, 5]
    if name == "pre_days":
        return [1, 3, 5]
    if name == "target_vol":
        return [0.10, 0.15, 0.20]
    if name == "rebal_days" and default is None:
        return [None, 10, 20]
    if default is None:
        return [None]
    if isinstance(default, bool):
        return [default]
    if isinstance(default, int):
        lo = max(2, default // 2)
        return sorted({lo, default, default * 2})
    # float
    d = float(default)
    if d == 0.0:
        return [0.0]
    if d > 0:
        return sorted({round(d * 0.5, 6), d, round(d * 1.5, 6)})
    return sorted({round(d * 1.5, 6), d, round(d * 0.5, 6)})  # negative


def _face_of(mod_name, fn_name, func):
    """Signal face: panel (DataFrame out), persym (Series out per symbol),
    calendar (date-indexed Series broadcast)."""
    if mod_name == "seasonal" and fn_name in ("month_end_effect",
                                              "month_seasonality",
                                              "weekday_effect"):
        return "calendar"
    first = next(iter(func.__annotations__.values()), None)
    ann = str(first)
    return "panel" if "DataFrame" in ann else "persym"


def _load_negative_priors(inv):
    """Judged-negative factory functions from the p4 batch CSVs (mechanical,
    prereg sec.1 'negative prior labels carried per-cell')."""
    neg = set()
    srcs = []
    for f in P4_BATCH_CSVS:
        p = os.path.join(PATHS.root, "research", "shortline", f)
        if not os.path.exists(p):
            continue
        srcs.append(f)
        df = pd.read_csv(p)
        for _, r in df.iterrows():
            status = str(r.get("status", "")).lower()
            if "fail" in status or "reject" in status or "void" in status \
                    or r.get("g1_pass") is False:
                neg.add(str(r["name"]))
    known = {k[1] for k in inv}
    return {n for n in neg if n in known}, srcs


def _defaults_tuple(func):
    """param -> default mapping via inspect (excludes data args)."""
    data_args = set()
    for pname, ann in func.__annotations__.items():
        if "DataFrame" in str(ann) or "Series" in str(ann):
            data_args.add(pname)
    out = {}
    for pname, p in inspect.signature(func).parameters.items():
        if pname in data_args or p.default is inspect.Parameter.empty:
            continue
        out[pname] = p.default
    return out


def build_grammar():
    inv = _factory_inventory()
    a_keys = {(t["module"], t["fn"]) for t in A_TEMPLATES}
    b_fns = sorted(k for k in inv if k not in a_keys)
    neg_names, neg_srcs = _load_negative_priors(inv)
    domains, faces, neg_defaults = {}, {}, {}
    for key, func in sorted(inv.items()):
        mk = f"{key[0]}.{key[1]}"
        dom = {}
        for pname, p in inspect.signature(func).parameters.items():
            ann = str(p.annotation)
            if "DataFrame" in ann or "Series" in ann:
                continue
            dom[pname] = _param_domain(pname, p.default)
        domains[mk] = dom
        faces[mk] = _face_of(key[0], key[1], func)
        if key[1] in neg_names:
            neg_defaults[mk] = {k: v for k, v in _defaults_tuple(func).items()}
    # exclusion set: registered six default-axis cells + negative functions'
    # signature-default cells on the default axis (prereg sec.1 exclusion law)
    exclusion = {
        "registered_default_axis": [
            {"module": t["module"], "fn": t["fn"],
             "sig_params": t["sig_params"], "axis": list(DEFAULT_AXIS)}
            for t in A_TEMPLATES],
        "negative_default_axis": [
            {"module": mk.split(".")[0], "fn": mk.split(".")[1],
             "sig_params": params, "axis": list(DEFAULT_AXIS)}
            for mk, params in sorted(neg_defaults.items())],
        "sources": neg_srcs,
    }
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "seeds": {"trial_labor_w1_gen": SEED_GEN,
                  "trial_labor_w1_scrnull": SEED_NULL,
                  "trial_labor_w1_unc": SEED_UNC,
                  "derivation": "np.random.default_rng([base, family_idx, "
                                 "draw_idx]) PCG64 (prereg sec.3)"},
        "n_per_family": N_PER_FAMILY, "k_nulls": K_NULLS,
        "families": {
            "A": [{"module": t["module"], "fn": t["fn"],
                   "trader_id": t["trader_id"], "sig_params": t["sig_params"],
                   "registered_params": t["registered_params"],
                   "registered_ovr": t["registered_ovr"]}
                  for t in A_TEMPLATES],
            "B": [{"module": m, "fn": f} for (m, f) in b_fns]},
        "value_domains": domains, "faces": faces,
        "axis": {"entry_filters": AXIS_FILTERS, "exits": AXIS_EXITS,
                 "sizing": AXIS_SIZING, "timing": AXIS_TIMING,
                 "exit_machines": EXIT_MACHINES, "default_axis": DEFAULT_AXIS,
                 "filter_defs": {
                     "none": "no entry filter",
                     "depth_thresh": "sym drawdown vs 60d high > -0.10 "
                                     "(no deep-crash catching)",
                     "amplitude": "20d return std <= cross-sectional median "
                                  "on signal day",
                     "liquidity": "20d mean amount >= cross-sectional median",
                     "trend_slope": "close > MA5 AND close > prior close "
                                    "(first-yang confirmation)",
                     "dual_window": "MA5 > MA20 (dual-window resonance)",
                     "fundamental_mask": "b_layer_mask ok_static hard filter "
                                         "(keep-ok codes only; core48 overlap "
                                         "disclosed at generate)"},
                 "sizing_defs": {
                     "equal_weight": "engine default nominal (template/params)",
                     "inverse_vol": "entry_size_scale = clip(0.15 / "
                                    "vol20ann(510300), max 1.0)",
                     "cap20": "sizing_mode=equity_fraction + "
                              "position_size_pct=0.20 (single-name cap)",
                     "regime_delever": "entry_size_scale = 0.5 on bear-state "
                                       "days (REGIME_MAP), else 1.0"}},
        "negative_prior_functions": sorted(neg_names),
        "negative_prior_default_cells": neg_defaults,
        "exclusion": exclusion,
        "grid_module_excluded": "strategies/grid (4 fns; GRID line has its "
                                "own judgment lane GRID-SLEEVE-P1, prereg "
                                "sec.3)",
        "audit": {
            "provenance": "value domains rule-frozen from signature defaults "
                          "at grammar build (prereg sec.3); faces from "
                          "signature annotations + seasonal calendar set",
            "b_family_count_note": f"B={len(b_fns)} = 77 non-grid fns - "
                                   f"{len(a_keys)} distinct A functions; "
                                   "prereg sec.3 prose said 71 (81-6-4 "
                                   "counts top_n_rotation's two A slots as "
                                   "two); mechanical inventory wins, raw "
                                   "N=500/family unchanged",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha(grammar)
    return grammar


# ------------------------------------------------------- candidate generation
def _draw_candidate(rng, family, slot, grammar):
    """One uniform draw: sig params within domains + axis combo (448)."""
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    sig_params = {}
    for pname, values in dom.items():
        sig_params[pname] = values[int(rng.integers(len(values)))]
    ax = (AXIS_FILTERS[int(rng.integers(len(AXIS_FILTERS)))],
          AXIS_EXITS[int(rng.integers(len(AXIS_EXITS)))],
          AXIS_SIZING[int(rng.integers(len(AXIS_SIZING)))],
          AXIS_TIMING[int(rng.integers(len(AXIS_TIMING)))])
    return {"module": spec["module"], "fn": spec["fn"], "sig_params": sig_params,
            "axis": list(ax)}


def _excluded(cand, grammar):
    """Exact already-judged cell test (prereg sec.1 exclusion law)."""
    ax = tuple(cand["axis"])
    if ax != DEFAULT_AXIS:
        return False
    for e in grammar["exclusion"]["registered_default_axis"]:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"]:
            return True
    for e in grammar["exclusion"]["negative_default_axis"]:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"]:
            return True
    return False


def _bench_of(P):
    """Shared bench series (510300 close); None when absent from the panel
    (honest zero-signal face for bench-requiring fns, disclosed upstream)."""
    if BENCH_SYM in P["close"].columns:
        return P["close"][BENCH_SYM]
    return None


def _zero_mask(P):
    return pd.DataFrame(0, index=P["close"].index,
                        columns=P["close"].columns)


def _data_arg_names(func):
    return [p for p in inspect.signature(func).parameters
            if p in ("open", "open_", "high", "low", "close", "volume",
                     "amount", "bench")]


def _panel_call(fn, P, kw):
    """Panel-face call assembling positional data panels (+ shared bench) in
    signature order; bench-requiring fn on a bench-absent panel -> None
    (caller emits the honest zero mask)."""
    args = []
    for n in _data_arg_names(fn):
        if n == "bench":
            b = _bench_of(P)
            if b is None:
                return None
            args.append(b)
        elif n == "open_":
            args.append(P["open"])
        else:
            args.append(P[n] if n in P else P["close"])
    return fn(*args, **kw)


def _binarize(out, P):
    """p4 batch convention: entry = (pos > 0), exit = (pos <= 0) -- state
    signals may carry -1; continuous faces (scores/vol-fractions) binarize
    under the same established rule (no-op for the registered 0/1 six)."""
    if out is None:
        return _zero_mask(P)
    return (out.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0) > 0).astype(int)


def _signal_frame(cand_or_spec, P, face, rng_matrix=None, p_on=None):
    """Build the raw 0/1 entry mask (date x sym) from the frozen factory."""
    if rng_matrix is not None:                      # null leg: random signals
        m = (rng_matrix < p_on).astype(int)
        return pd.DataFrame(m, index=P["close"].index,
                            columns=P["close"].columns).fillna(0)
    mod = __import__(f"strategies.{cand_or_spec['module']}",
                     fromlist=[cand_or_spec["module"]])
    fn = getattr(mod, cand_or_spec["fn"])
    kw = cand_or_spec["sig_params"]
    if face == "panel":
        return _binarize(_panel_call(fn, P, kw), P)
    if face == "calendar":
        s = fn(P["close"], **kw)
        out = pd.DataFrame(np.tile((s > 0).astype(int).values[:, None],
                                   (1, len(P["close"].columns))),
                           index=P["close"].index,
                           columns=P["close"].columns)
        return out.fillna(0).astype(int)
    # persym: per-symbol Series constructors applied column-wise; bench args
    # (same shared series for every symbol) assembled in signature order
    b = None
    args_names = _data_arg_names(fn)
    if "bench" in args_names:
        b = _bench_of(P)
        if b is None:
            return _zero_mask(P)
    cols = {}
    for s in P["close"].columns:
        parts = []
        for n in args_names:
            if n == "bench":
                parts.append(b)
            elif n == "open_":
                parts.append(P["open"][s])
            else:
                parts.append(P[n][s])
        cols[s] = fn(*parts, **kw)
    return _binarize(pd.DataFrame(cols), P)


def apply_filter(mask, filt, P, fundamental_ok=None):
    """Entry-filter axis leg (causal: all inputs are signal-day known)."""
    if filt == "none":
        return mask
    close = P["close"]
    if filt == "fundamental_ok":     # unreachable; kept for clarity
        return mask
    if filt == "fundamental_mask":
        if fundamental_ok is None:
            return mask * 0
        return mask & fundamental_ok.reindex(columns=mask.columns).fillna(
            False)
    if filt == "depth_thresh":
        dd = close / close.rolling(60).max() - 1.0
        return mask & (dd > -0.10).fillna(False)
    if filt == "amplitude":
        vol = close.pct_change().rolling(20).std()
        med = vol.median(axis=1)
        return mask & (vol.le(med, axis=0)).fillna(False)
    if filt == "liquidity":
        am = P["amount"].rolling(20).mean()
        med = am.median(axis=1)
        return mask & (am.ge(med, axis=0)).fillna(False)
    if filt == "trend_slope":
        ma5 = close.rolling(5).mean()
        return mask & ((close > ma5) & (close > close.shift(1))).fillna(False)
    if filt == "dual_window":
        return mask & (close.rolling(5).mean()
                       > close.rolling(20).mean()).fillna(False)
    raise ValueError(filt)


def apply_timing(mask, timing):
    if timing == "daily_signal":
        return mask
    # weekly_grid: new entries only on the first trading day of each ISO week
    idx = mask.index
    isoweek = pd.Series(idx.isocalendar().week.values, index=idx)
    isoyear = pd.Series(idx.isocalendar().year.values, index=idx)
    first_of_week = (isoweek != isoweek.shift(1)) | (isoyear != isoyear.shift(1))
    return mask & pd.DataFrame(np.tile(first_of_week.values[:, None],
                                       (1, mask.shape[1])),
                               index=idx, columns=mask.columns)


def sizing_pieces(cand, P, states, base_engine_params):
    """Sizing axis -> (engine params update, entry_size_scale series|None)."""
    mode = cand["axis"][2]
    close = P["close"]
    if mode == "equal_weight":
        return dict(base_engine_params), None
    if mode == "cap20":
        out = dict(base_engine_params)
        out["sizing_mode"] = "equity_fraction"
        out["position_size_pct"] = 0.20
        return out, None
    if mode == "inverse_vol":
        if BENCH_SYM not in close.columns:
            return dict(base_engine_params), None   # bench absent: no-op
        vol = close[BENCH_SYM].pct_change().rolling(20).std() * math.sqrt(252)
        scale = (0.15 / vol).clip(upper=1.0).fillna(1.0)
        return dict(base_engine_params), scale
    if mode == "regime_delever":
        s = states.reindex(close.index)
        bear = s.map(lambda x: REGIME_MAP.get(x) == "bear").fillna(False)
        scale = pd.Series(np.where(bear, 0.5, 1.0), index=close.index)
        return dict(base_engine_params), scale
    raise ValueError(mode)


def candidate_engine_params(cand, template):
    """Full engine params + ExitPatch overrides for one candidate cell.

    Exit axis: template_default -> A: registered exit face / B: engine
    defaults; machine axes -> frozen EXIT_MACHINES (registered bridged exit
    fields are absent so the patch machine wins). Sizing axis: equal_weight
    keeps the template's sizing fields (A) / engine defaults (B); other
    sizing axes take over sizing wholly (cap20 sets its own fields,
    scale-series axes leave nominal fields to the base).
    """
    sizing = cand["axis"][2]
    exit_axis = cand["axis"][1]
    if template is not None:
        reg = template["registered_params"]
        if exit_axis == "template_default":
            base = dict(reg)
            patch = dict(template["registered_ovr"])
            if sizing != "equal_weight":
                base = {k: v for k, v in base.items()
                        if k not in ("position_size_pct", "max_positions")}
            return base, patch
        mach = EXIT_MACHINES[exit_axis]
        base = dict(mach["bridged"])
        if sizing == "equal_weight":
            for k in ("position_size_pct", "max_positions"):
                if k in reg:
                    base[k] = reg[k]
        return base, dict(mach["patch"])
    if exit_axis == "template_default":
        return {}, None
    mach = EXIT_MACHINES[exit_axis]
    return dict(mach["bridged"]), dict(mach["patch"])


def run_candidate_curve(cand, template, prices, P, states,
                        fundamental_ok=None, rng_matrix=None, p_on=None):
    """One candidate cell: signal face -> axis transforms -> engine run on
    the given panel. Returns (equity Series, trades, params, patch, scale)."""
    mk = f"{cand['module']}.{cand['fn']}"
    face = "null" if rng_matrix is not None else GRAMMAR["faces"][mk]
    if rng_matrix is not None:
        mask = _signal_frame(None, P, face, rng_matrix=rng_matrix, p_on=p_on)
    else:
        mask = _signal_frame(cand, P, face)
    mask = mask.reindex(index=P["close"].index, columns=P["close"].columns
                        ).fillna(0)
    mask = apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = apply_timing(mask, cand["axis"][3])
    params, patch = candidate_engine_params(cand, template)
    params, scale = sizing_pieces(cand, P, states, params)
    params["report_num_entries"] = True
    dd_control = (template.get("registered_dd_control")
                  if template is not None else None)
    with ExitPatch(patch):
        res = run_backtest(prices, params, entry_signal=mask,
                           exit_signal=(mask <= 0), entry_size_scale=scale,
                           dd_control=dd_control)
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    return eq, res["trades"], res["metrics"], params, patch


# ------------------------------------------------------------ naive dedup leg
def _naive_returns(mask, close):
    """Naive-hold daily returns (generate-stage dedup leg 2; NO engine)."""
    w = mask.div(mask.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    r = close.pct_change().fillna(0.0)
    return (w.shift(1) * r).sum(axis=1)


def _fingerprint(mask):
    """sha256 over per-rebalance-day sorted (sym, round(w,4)) (prereg sec.3
    dedup leg 1). Columns are panel-sorted, so sorted-by-sym order == column
    order; changed-row detection is vectorized (O(n) not O(n log n))."""
    w = mask.div(mask.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    w4 = w.round(4)
    changed = (w4 != w4.shift()).any(axis=1).fillna(True)
    rows = np.nonzero(changed.values)[0]
    wvals = w4.values
    idx_dates = [str(d.date()) for d in w.index]
    h = hashlib.sha256()
    for i in rows:
        h.update(idx_dates[i].encode("utf-8"))
        h.update(wvals[i].tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------ generate
def cmd_generate() -> int:
    t0 = time.time()
    global GRAMMAR
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    grammar = build_grammar()
    GRAMMAR = grammar
    prices = load_core()
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = build_panels(prices)
    close = P["close"]

    # fundamental_mask overlap disclosure (keep-ok semantics; core48 face)
    try:
        bl = pd.read_csv(B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in close.columns if s in ok_codes)
    except Exception as e:
        overlap, ok_codes = [], set()
        grammar["audit"]["fundamental_mask_load_error"] = str(e)[:200]
    grammar["audit"]["fundamental_mask_overlap_core48"] = overlap
    # keep-ok mask identical to the screen-stage face (consistency law)
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=close.index,
                                      columns=close.columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None     # apply_filter -> honest empty for all 48

    # ---- draws (A/B), exclusion-gated, deterministic
    candidates, excl_hits = [], {"A": 0, "B": 0}
    for fam_idx, family in ((0, "A"), (1, "B")):
        slots = grammar["families"][family]
        n_slots = len(slots)
        accepted, draw_idx = 0, 0
        while accepted < N_PER_FAMILY:
            rng = np.random.default_rng([SEED_GEN, fam_idx, draw_idx])
            slot = draw_idx % n_slots
            cand = _draw_candidate(rng, family, slot, grammar)
            draw_idx += 1
            if _excluded(cand, grammar):
                excl_hits[family] += 1
                continue
            cand["family"] = family
            cand["candidate_id"] = f"W1-{family}-{accepted:04d}"
            cand["provenance"] = {"seed": SEED_GEN, "family_idx": fam_idx,
                                  "draw_idx": draw_idx - 1}
            if family == "A":
                cand["template_trader"] = slots[slot]["trader_id"]
                cand["negative_prior"] = False
            else:
                cand["negative_prior"] = (
                    f"{cand['module']}.{cand['fn']}" in
                    grammar["negative_prior_default_cells"])
            candidates.append(cand)
            accepted += 1
    print(f"raw draws: A=500 B=500 | exclusion hits: {excl_hits}")

    # ---- dedup gate (T-84 s3): fingerprint + naive-corr collapse
    # (streaming: masks are dropped after fp+series derivation -- RAM law
    # under the concurrent W2-A burn on this machine)
    fps, series = [], []
    for j, cand in enumerate(candidates):
        mk = f"{cand['module']}.{cand['fn']}"
        mask = _signal_frame(cand, P, GRAMMAR["faces"][mk])
        mask = mask.reindex(index=close.index, columns=close.columns).fillna(0)
        mask = apply_filter(mask, cand["axis"][0], P, fundamental_ok)
        mask = apply_timing(mask, cand["axis"][3])
        fps.append(_fingerprint(mask))
        series.append(_naive_returns(mask, close).values)
        del mask
        if (j + 1) % 100 == 0:
            print(f"  [dedup face] {j + 1}/{len(candidates)}", flush=True)

    fp_groups = {}
    for i, fp in enumerate(fps):
        fp_groups.setdefault(fp, []).append(i)
    keep = set()
    fp_collapsed = []
    for fp, members in fp_groups.items():
        members.sort(key=lambda i: candidates[i]["candidate_id"])
        keep.add(members[0])
        fp_collapsed.append({"kept": candidates[members[0]]["candidate_id"],
                             "eliminated": [candidates[m]["candidate_id"]
                                            for m in members[1:]]})
    # corr leg among fingerprint-survivors (zero-variance pairs skipped)
    idx_keep = sorted(keep)
    mat = np.vstack([series[i] for i in idx_keep])
    sd = mat.std(axis=1)
    live_rows = [j for j in range(len(idx_keep)) if sd[j] > 1e-12]
    corr_elim = []
    dead = set()
    if len(live_rows) >= 2:
        sub = mat[live_rows]
        corr = np.corrcoef(sub)
        for a in range(len(live_rows)):
            for b in range(a + 1, len(live_rows)):
                if abs(corr[a, b]) >= 0.999:
                    ia, ib = idx_keep[live_rows[a]], idx_keep[live_rows[b]]
                    # keep deterministic lowest candidate_id
                    ka = candidates[ia]["candidate_id"]
                    kb = candidates[ib]["candidate_id"]
                    dead.add(ib if ka < kb else ia)
                    corr_elim.append({"pair": sorted([ka, kb]),
                                      "corr": round(float(corr[a, b]), 6),
                                      "eliminated": candidates[
                                          ib if ka < kb else ia]
                                      ["candidate_id"]})
    final_keep = [i for i in idx_keep if i not in dead]
    distinct = [candidates[i] for i in final_keep]

    grammar["dedup"] = {
        "raw": len(candidates), "fingerprint_collapse_groups":
            fp_collapsed, "corr_collapses": corr_elim,
        "distinct": len(distinct),
        "note": "dedup legs operate on the generate-stage signal face "
                "(fingerprint = rebalance-day weights sha256; corr = "
                "naive-hold daily return series, no engine burn); engine "
                "faces run at screen",
    }
    grammar["audit"]["exclusion_hits"] = excl_hits
    grammar["grammar_sha256"] = _grammar_sha(grammar)
    GRAMMAR = grammar

    os.makedirs(RES_DIR, exist_ok=True)
    _dump(os.path.join(RES_DIR, "w1_grammar.json"), grammar)
    _dump(os.path.join(RES_DIR, "w1_candidates.json"),
          {"wave": WAVE, "evidence_cutoff": CUTOFF,
           **cutoff_meta(CUTOFF), "n": len(distinct),
           "candidates": distinct})

    # grammar consumption ledger (append-only, prereg sec.4/sec.6)
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"raw 1000 (A500/B500) | dedup -> {len(distinct)} | "
           f"seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"consumed {time.strftime('%Y-%m-%d %H:%M:%S')} by bm-b r348 | "
           f"same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |\n")
    os.makedirs(os.path.dirname(GRAMMAR_LEDGER), exist_ok=True)
    if not os.path.exists(GRAMMAR_LEDGER):
        with open(GRAMMAR_LEDGER, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; TRIAL_LABOR_LAW "
                     "sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(GRAMMAR_LEDGER, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)

    print(f"generate done: raw 1000 -> distinct {len(distinct)} "
          f"(fp-collapses {len(fp_collapsed)}, corr-collapses "
          f"{len(corr_elim)}), exclusions {excl_hits}")
    print(f"products: w1_grammar.json + w1_candidates.json + ledger row")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ---------------------------------------------------------------- screen prep
def cmd_screen_prep() -> int:
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    global GRAMMAR
    gpath = os.path.join(RES_DIR, "w1_grammar.json")
    if not os.path.exists(gpath):
        print("PREP-GATE FAIL: generate not run (w1_grammar.json absent)")
        return 2
    GRAMMAR = json.load(open(gpath, encoding="utf-8"))
    if not self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1

    prices_full = load_core()
    cut = pd.Timestamp(CUTOFF)
    # G-PANEL: 48/48 members, >=60 rows each, last row == cutoff, OHLCV cols
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}

    # G-ANCHOR: registered six replayed through the grammar default-axis path
    anchors = {}
    for t in A_TEMPLATES:
        trader = load_trader(t["trader_id"])
        a = anchor_gate(trader, prices_full)
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        cand = {"module": t["module"], "fn": t["fn"],
                "sig_params": t["sig_params"], "axis": list(DEFAULT_AXIS)}
        pcut = {s: df[df.index <= cut] for s, df in prices_full.items()}
        Pfull = build_panels(pcut)
        eq, trades, metrics, params, patch = run_candidate_curve(
            cand, t, pcut, Pfull, v3_state_series())
        got_is = sharpe(eq[eq.index < OOS_START])
        got_oos = sharpe(eq[eq.index >= OOS_START])
        # anchor gate returns 4dp-rounded faces (seg_metrics law) -- compare
        # at the same 4dp caliber (same engine + same inputs => exact match)
        mine_ok = (abs(round(float(got_is), 4)
                       - a["got"]["in_sample"]["sharpe"]) < 1e-9
                   and abs(round(float(got_oos), 4)
                           - a["got"]["out_sample"]["sharpe"]) < 1e-9)
        anchors[t["trader_id"]] = {
            "live_ok": True, "grammar_replay_is": round(float(got_is), 4),
            "grammar_replay_oos": round(float(got_oos), 4),
            "grammar_face_faithful": bool(mine_ok)}
        if not mine_ok:
            print(f"PREP-GATE FAIL: grammar replay != live anchor "
                  f"{t['trader_id']} (is {got_is:.4f} vs "
                  f"{a['got']['in_sample']['sharpe']}, "
                  f"oos {got_oos:.4f} vs {a['got']['out_sample']['sharpe']})")
            return 1
    ga = {"pass": all(x["grammar_face_faithful"] for x in anchors.values()),
          "anchors": anchors}

    # leg-L panel + G-CENSUS (P-5C frozen grid, sec.9.3 wholesale binding)
    prices, P, idx, listed, cen = _load_leg("L")
    if cen != FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen} != "
              f"{FROZEN_CENSUS['L']}")
        return 1
    gc_ = {"pass": True, "census": cen, "frozen": FROZEN_CENSUS["L"]}
    close = P["close"]
    n = len(idx)

    # eligible 6m starts (census caliber) + passive 6m rets (shared artifact)
    W6 = WINDOWS["6m"]
    starts = [p for p in range(n)
              if idx[p] >= LEG_L_FLOOR and p >= WARMUP_TD
              and p <= n - 1 - W6 and listed.iloc[p] >= MIN_LISTED]
    if len(starts) != FROZEN_CENSUS["L"]["6m"]:
        print(f"PREP-GATE FAIL: 6m starts {len(starts)} != "
              f"{FROZEN_CENSUS['L']['6m']}")
        return 1
    passive_6m = {}
    for p in starts:
        sdate = idx[p]
        edate = idx[p + W6 - 1]
        syms = close.columns[close.loc[sdate].notna()]
        rel = passive_rel(close, syms, sdate, edate)
        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)

    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF, **cutoff_meta(CUTOFF),
            "gates": {"G-PANEL": gp, "G-ANCHOR": ga, "G-CENSUS": gc_,
                      "G-EXCLUDE": {"pass": True, "hits_disclosed":
                                    json.load(open(gpath, encoding="utf-8"))
                                    ["audit"]["exclusion_hits"]}},
            "n_starts_6m": len(starts), "starts": starts,
            "passive_6m_ret": passive_6m,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _dump(os.path.join(RES_DIR, "prep_state.json"), prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors 6/6 faithful, "
          f"census {cen}, starts {len(starts)}, passive precomputed")
    return 0


# ---------------------------------------------------------------- screen burn
_ST = None       # per-worker shared state (initializer)


def _init_worker(state):
    global _ST, GRAMMAR
    _ST = state
    # Windows spawn workers re-import the module: runtime globals set by the
    # parent cmd_* never propagate. GRAMMAR rides initargs (87KB, cheap) --
    # without it run_candidate_curve L672 GRAMMAR["faces"][mk] is NoneType
    # (r121 bm-c crash #1, zero cells burned, checkpoint empty).
    g = state.get("grammar")
    if g is not None:
        GRAMMAR = g
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _screen_cell(cell):
    """One screen cell: full leg-L backtest -> beat6m row (pool worker)."""
    st = _ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        rng = np.random.default_rng([SEED_NULL, cell["i"]])
        p_on = NULL_P_REGIMES[int(rng.integers(len(NULL_P_REGIMES)))]
        ax = (AXIS_FILTERS[int(rng.integers(len(AXIS_FILTERS)))],
              AXIS_EXITS[int(rng.integers(len(AXIS_EXITS)))],
              AXIS_SIZING[int(rng.integers(len(AXIS_SIZING)))],
              AXIS_TIMING[int(rng.integers(len(AXIS_TIMING)))])
        cand = {"module": "null", "fn": "random_signal", "sig_params":
                {"p_on": p_on}, "axis": list(ax), "candidate_id":
                f"W1-NULL-{cell['i']:04d}", "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch = run_candidate_curve(
            cand, None, prices, P, states, rng_matrix=mat, p_on=p_on)
    else:
        eq, trades, metrics, params, patch = run_candidate_curve(
            cand, template, prices, P, states,
            fundamental_ok=st["fundamental_ok"])
    if len(eq) < 30 or float(eq.iloc[0]) <= 0:
        return {"cell_id": cell["cell_id"], "candidate_id":
                cand["candidate_id"], "family": cand["family"],
                "no_entries": True, "beat6m_k": 0,
                "beat6m_n": len(st["starts"]),
                "beat6m_rate": 0.0, "sharpe_full": None,
                "n_trades": int(metrics.get("num_trades", 0)),
                "n_entries": int(metrics.get("num_entries", 0))}
    k = 0
    n_win = 0
    for p in starts:
        if p + WINDOWS["6m"] - 1 >= len(eq):
            continue
        n_win += 1
        cret = float(eq.iloc[p + WINDOWS["6m"] - 1] / eq.iloc[p] - 1.0)
        if cret > passive[p]:
            k += 1
    rate = k / n_win if n_win else 0.0
    n = len(starts)
    z = (k - 0.5 * n) / math.sqrt(0.25 * n) if n else 0.0
    pval = 2 * (1 - _norm_cdf(abs(z)))
    return {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
            "family": cand["family"], "no_entries": False,
            "module": cand.get("module"), "fn": cand.get("fn"),
            "beat6m_k": k, "beat6m_n": n_win, "beat6m_rate": round(rate, 6),
            "binom_z": round(z, 4), "binom_p": round(pval, 6),
            "sharpe_full": round(float(sharpe(eq)), 4),
            "dd_full": round(float(max_drawdown(eq)), 4),
            "n_trades": int(metrics.get("num_trades", 0)),
            "n_entries": int(metrics.get("num_entries", 0))}


def _cell_list():
    """Candidate cells + null cells (deterministic order; shard-split by
    index)."""
    gpath = os.path.join(RES_DIR, "w1_grammar.json")
    cpath = os.path.join(RES_DIR, "w1_candidates.json")
    grammar = json.load(open(gpath, encoding="utf-8"))
    cands = json.load(open(cpath, encoding="utf-8"))["candidates"]
    a_by_trader = {t["trader_id"]: t for t in A_TEMPLATES}
    cells = []
    for c in cands:
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"SCREEN|{c['candidate_id']}", "kind": "cand",
                      "cand": c, "template": template})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None})
    return grammar, cells


def cmd_screen(shard: int, shards: int, workers: int | None) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    global GRAMMAR
    ppath = os.path.join(RES_DIR, "prep_state.json")
    if not os.path.exists(ppath):
        print("SCREEN-GATE: prep_state absent -- run screen-prep first")
        return 2
    prep = json.load(open(ppath, encoding="utf-8"))
    grammar, cells = _cell_list()
    GRAMMAR = grammar
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = _load_leg("L")
    states = v3_state_series()
    try:
        bl = pd.read_csv(B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    fundamental_ok = (pd.DataFrame(True, index=P["close"].index,
                                   columns=P["close"].columns)
                      if overlap else None)
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "fundamental_overlap": overlap,
             "grammar": grammar}

    ck = os.path.join(CKPT_DIR, f"screen_shard_{shard}of{shards}.jsonl")
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["cell_id"])
                except Exception:
                    pass
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(_j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell, (c,)) for c in todo]
        run_cells_parallel(jobs, workers=workers or worker_cap(),
                           desc="screen cells", initializer=_init_worker,
                           initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    return 0


def _load_screen_rows():
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("screen_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln:
                        rows.append(json.loads(ln))
    return rows


def cmd_screen_finalize() -> int:
    print(f"=== {WAVE} screen-finalize ===")
    grammar, cells = _cell_list()
    rows = _load_screen_rows()
    by_id = {r["cell_id"]: r for r in rows}
    missing = [c["cell_id"] for c in cells if c["cell_id"] not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} cells incomplete -- "
              f"finalize refused (checkpoint retained); first missing: "
              f"{missing[:3]}")
        return 2
    null_rows = [by_id[f"SCREEN|NULL-{i:04d}"] for i in range(K_NULLS)]
    null_rates = [r["beat6m_rate"] for r in null_rows]
    p95 = float(np.percentile(null_rates, 95))
    cand_rows = [by_id[c["cell_id"]] for c in cells if c["kind"] == "cand"]
    survivors = []
    for r in cand_rows:
        r["survives_screen"] = bool(r["beat6m_rate"] > p95)
        if r["survives_screen"]:
            survivors.append(r["candidate_id"])
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    prev = ledger_head()["total"]
    ledger = append_ledger(f"{WAVE}_SCREEN", batch_trials,
                           "results/trial_labor_w1/w1_screen.json",
                           evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "screen", "prereg": PREREG,
           **cutoff_meta(CUTOFF), "grammar_sha256": grammar["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)), 4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(NULL_P_REGIMES),
                           "seed": SEED_NULL},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.3, frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber); workers "
                             "BelowNormal; checkpoint append-per-cell"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _dump(os.path.join(RES_DIR, "w1_screen.json"), out)
    csv_path = os.path.join(RES_DIR, "w1_screen_cells.csv")
    cols = ["cell_id", "candidate_id", "family", "module", "fn", "no_entries",
            "beat6m_k", "beat6m_n", "beat6m_rate", "binom_z", "binom_p",
            "sharpe_full", "dd_full", "n_trades", "n_entries",
            "survives_screen"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"products: w1_screen.json + w1_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------------------- judge
def _judge_cell(cell):
    """Survivor judged cell: dual-axis full curves + window grid + regime
    segments + G1'/DSR/dual-null inputs (pool worker)."""
    st = _ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, starts_map = (
            st[f"prices_{leg}"], st[f"P_{leg}"], st[f"idx_{leg}"],
            st[f"listed_{leg}"], st["starts"][leg])
        eq, trades, metrics, params, patch = run_candidate_curve(
            cand, template, prices, P, st["states"],
            fundamental_ok=st["fundamental_ok"])
        daily = eq.pct_change().fillna(0.0)
        segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
        beat = {}
        s_series = st["states"].reindex(idx)
        for wname, w in WINDOWS.items():
            starts = starts_map[wname]
            k = tot = 0
            for p in starts:
                if p + w - 1 >= len(eq):
                    continue
                tot += 1
                cret = float(eq.iloc[p + w - 1] / eq.iloc[p] - 1.0)
                # passive for this leg/window precomputed at judge-prep
                pret = st["passive"][leg][wname][str(p)]
                if cret > pret:
                    k += 1
                d = s_series.iloc[p] if p < len(s_series) else None
                st_ = REGIME_MAP.get(d, "na") if d == d else "na"
                segs[st_] += 1
            beat[wname] = {"k": k, "n": tot,
                           "rate": round(k / tot, 6) if tot else 0.0}
        legs[leg] = {"beat": beat, "regime_start_windows": segs,
                     "sharpe_full": round(float(sharpe(eq)), 4),
                     "n_trades": int(metrics.get("num_trades", 0)),
                     "n_entries": int(metrics.get("num_entries", 0))}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
    out["legs"] = legs
    # dual nulls on the leg-L base daily returns (RANDOM_LARGE_SAMPLE_LAW
    # sec.3; rng usage pinned to the two resample faces only)
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    ci = _dual_nulls(r, cell["i"])
    out["dual_nulls"] = ci
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def _dual_nulls(returns, cell_idx):
    """Block bootstrap B=2000 (block=20 circular) + sign-flip P=2000 on the
    cell's mean daily return (two-sided). Vectorized, seed [SEED_UNC, i]."""
    rng = np.random.default_rng([SEED_UNC, cell_idx])
    r = np.asarray(returns, dtype=float)
    n = len(r)
    mu = float(r.mean())
    # block bootstrap of the mean
    B, block = 2000, 20
    n_blocks = int(math.ceil(n / block))
    idx0 = rng.integers(0, max(1, n), size=(B, n_blocks))
    offs = np.arange(block)[None, None, :]
    gather = (idx0[:, :, None] + offs) % n           # circular blocks
    boots = r[gather].reshape(B, -1)[:, :n].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    # sign-flip permutation on the mean
    P = 2000
    signs = rng.choice([-1.0, 1.0], size=(P, n))
    perms = (r[None, :] * signs).mean(axis=1)
    p_two = float((np.abs(perms) >= abs(mu)).mean())
    return {"bootstrap_ci": [round(float(lo), 8), round(float(hi), 8)],
            "ci_lower_positive": bool(lo > 0),
            "signflip_p": round(p_two, 6),
            "B": B, "P": P, "block": block}


def cmd_judge(shard: int, shards: int, workers: int | None) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    global GRAMMAR
    jpath = os.path.join(RES_DIR, "judge_state.json")
    spath = os.path.join(RES_DIR, "w1_screen.json")
    for p in (jpath, spath):
        if not os.path.exists(p):
            print("JUDGE-GATE: screen finalize + judge-prep required first "
                  f"({p} absent)")
            return 2
    jstate = json.load(open(jpath, encoding="utf-8"))
    grammar = json.load(open(os.path.join(RES_DIR, "w1_grammar.json"),
                             encoding="utf-8"))
    GRAMMAR = grammar
    screen = json.load(open(spath, encoding="utf-8"))
    a_by_trader = {t["trader_id"]: t for t in A_TEMPLATES}
    cands = {c["candidate_id"]: c for c in json.load(
        open(os.path.join(RES_DIR, "w1_candidates.json"),
             encoding="utf-8"))["candidates"]}
    cells = []
    for i, cid in enumerate(sorted(screen["survivors"])):
        c = cands[cid]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"JUDGE|{cid}", "candidate_id": cid, "i": i,
                      "cand": c, "template": template})
    mine = [c for i, c in enumerate(cells) if i % shards == shard]

    legL = _load_leg("L")
    legD = _load_leg("D")
    # fundamental_ok identical to the screen-stage face (consistency law)
    try:
        bl = pd.read_csv(B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in legL[1]["close"].columns
                         if s in ok_codes)
    except Exception:
        overlap = []
    fundamental_ok = (pd.DataFrame(True, index=legL[1]["close"].index,
                                  columns=legL[1]["close"].columns)
                      if overlap else None)
    state = {"prices_L": legL[0], "P_L": legL[1],
             "idx_L": legL[2], "listed_L": legL[3],
             "prices_D": legD[0], "P_D": legD[1],
             "idx_D": legD[2], "listed_D": legD[3],
             "starts": jstate["starts"], "passive": jstate["passive"],
             "states": v3_state_series(),
             "fundamental_ok": fundamental_ok,
             "grammar": grammar}
    state["bench_absent_D"] = (BENCH_SYM not in legD[1]["close"].columns)

    ck = os.path.join(CKPT_DIR, f"judge_shard_{shard}of{shards}.jsonl")
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["cell_id"])
                except Exception:
                    pass
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"judge shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(_j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell, (c,)) for c in todo]
        run_cells_parallel(jobs, workers=workers or worker_cap(),
                           desc="judge cells", initializer=_init_worker,
                           initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_judge_prep() -> int:
    """Dual-leg census gates + manifest gate + passive per (leg, window)."""
    print(f"=== {WAVE} judge-prep ===")
    spath = os.path.join(RES_DIR, "w1_screen.json")
    if not os.path.exists(spath):
        print("JUDGE-PREP-GATE: screen not finalized")
        return 2
    man = json.load(open(T18_MANIFEST, encoding="utf-8"))
    gm = {"verdict": man.get("verdict"),
          "manifest_members": len(man.get("members", {})),
          "pass": bool(man.get("verdict") == "PASS")}
    if not gm["pass"]:
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    starts, passive = {}, {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = _load_leg(leg)
        if cen != FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift {cen}")
            return 1
        close = P["close"]
        n = len(idx)
        starts[leg] = {}
        passive[leg] = {}
        for wname, w in WINDOWS.items():
            st = [p for p in range(n)
                  if idx[p] >= (LEG_L_FLOOR if leg == "L" else LEG_D_FLOOR)
                  and p >= WARMUP_TD and p <= n - 1 - w
                  and (listed.iloc[p] >= MIN_LISTED if leg == "L" else True)]
            if len(st) != FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st)} != {FROZEN_CENSUS[leg][wname]}")
                return 1
            starts[leg][wname] = st
            passive[leg][wname] = {}
            for p in st:
                sdate = idx[p]
                edate = idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = passive_rel(close, syms, sdate, edate)
                passive[leg][wname][str(p)] = round(
                    float(rel.iloc[-1] - 1.0), 6)
    out = {"wave": WAVE, **cutoff_meta(CUTOFF), "g_manifest": gm,
           "starts": starts, "passive": passive,
           "census_frozen": FROZEN_CENSUS,
           "manifest_note": "prereg sec.2 prose said 18 members; the "
                            "sec.9.3-bound P-5C frozen census (D 3104/2978/"
                            "2726) reproduces only on the 48-member twin "
                            "cache -- mechanical wholesale import wins, "
                            "member count disclosed",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _dump(os.path.join(RES_DIR, "judge_state.json"), out)
    print(f"judge-prep PASS: manifest {gm['verdict']} "
          f"({gm['manifest_members']} members), census L/D == frozen")
    return 0


def cmd_judge_finalize() -> int:
    print(f"=== {WAVE} judge-finalize ===")
    grammar = json.load(open(os.path.join(RES_DIR, "w1_grammar.json"),
                             encoding="utf-8"))
    screen = json.load(open(os.path.join(RES_DIR, "w1_screen.json"),
                            encoding="utf-8"))
    cands = {c["candidate_id"]: c for c in json.load(
        open(os.path.join(RES_DIR, "w1_candidates.json"),
             encoding="utf-8"))["candidates"]}
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        rows.append(json.loads(ln))
    by_id = {r["cell_id"]: r for r in rows}
    missing = [f"JUDGE|{cid}" for cid in screen["survivors"]
               if f"JUDGE|{cid}" not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} judged cells incomplete; "
              f"refused (checkpoint retained)")
        return 2
    judged = [by_id[f"JUDGE|{cid}"] for cid in sorted(screen["survivors"])]

    # G1'v2 + DSR per cell (n_trials = live chain head AFTER screen append)
    n_trials = ledger_head()["total"]
    batch_cells = screen["batch_cells"]
    g1s, dsrs = [], []
    for r in judged:
        rets = r["legL_daily_returns"]
        g1 = g1_prime_v2(r["legL_sharpe_full"], rets, batch_cells,
                         pool="core48", n_trades=r["legL_n_trades"],
                         n_entries=r["legL_n_entries"])
        dsr = deflated_sharpe_ratio(rets, n_trials=n_trials)
        r["g1_prime_v2"] = g1
        r["dsr"] = {"dsr": round(float(dsr["dsr"]), 6), "n_trials": n_trials}
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample" if not r[
                            "sample_sufficient"] else "fail")
        g1s.append(r)
    # family PBO (CSCV 8 blocks; family = strategy module; <8 cells -> n/a)
    fam_map = {}
    for r in judged:
        c = cands[r["candidate_id"]]
        fam_map.setdefault(c["module"], []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        if len(rs) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        series = {r["candidate_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs}
        mat = align_returns(series)
        pbo = cscv_pbo(mat)
        pbos[fam] = {"pbo": round(float(pbo["pbo"]), 4) if isinstance(
            pbo, dict) else round(float(pbo), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # G2 columns
    for r in judged:
        g2 = g2_registration_v2(r["g1_pass"], r["dsr"], r.get("family_pbo"))
        r["g2_registration_v2"] = g2
    n_judged = len(judged)
    e_fp = round(0.05 * n_judged, 2)
    eligible = [r["candidate_id"] for r in judged
                if r["g2_registration_v2"]["eligible_v2"]]
    ledger = append_ledger(f"{WAVE}_JUDGE", n_judged,
                           "results/trial_labor_w1/w1_judge.json",
                           evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "judge", "prereg": PREREG,
           **cutoff_meta(CUTOFF), "grammar_sha256": grammar["grammar_sha256"],
           "n_judged_cells": n_judged,
           "n_wave_disclosure": {"screen_cells": screen["batch_cells"],
                                 "judged_cells": n_judged,
                                 "E_FP_nominal_5pct": e_fp,
                                 "note": "DSR>=0.95 gate IS the multiple-"
                                         "testing correction (cumulative "
                                         "N折减); E[FP] disclosed at "
                                         "nominal 5% caliber"},
           "family_pbo": pbos,
           "eligible_g2": eligible, "n_eligible_g2": len(eligible),
           "trials_ledger": ledger,
           "cells": [{k: v for k, v in r.items()
                      if k != "legL_daily_returns"} for r in judged],
           "audit": {"note": "judged face = dual-axis x {6m,12m,24m} x "
                             "base/x2 descriptive + regime segments + dual "
                             "nulls (B=2000 block bootstrap + P=2000 "
                             "sign-flip); x2 face = descriptive clause per "
                             "prereg sec.3 (cost-face stability), Sharpe "
                             "gates on base face"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _dump(os.path.join(RES_DIR, "w1_judge.json"), out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    return 0


# ------------------------------------------------------------------- intake
def cmd_intake() -> int:
    print(f"=== {WAVE} intake (s4 D6 binding gate) ===")
    jpath = os.path.join(RES_DIR, "w1_judge.json")
    if not os.path.exists(jpath):
        print("INTAKE-GATE: judge not finalized")
        return 2
    judge = json.load(open(jpath, encoding="utf-8"))
    cands = {c["candidate_id"]: c for c in json.load(
        open(os.path.join(RES_DIR, "w1_candidates.json"),
             encoding="utf-8"))["candidates"]}
    eligible = list(judge["eligible_g2"])
    if not eligible:
        out = {"wave": WAVE, **cutoff_meta(CUTOFF), "n_eligible": 0,
               "intake": [], "note": "zero G2-eligible survivors = lawful "
               "outcome, reported as-is (prereg sec.4 pred.3 modal zero)",
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
        _dump(os.path.join(RES_DIR, "w1_intake.json"), out)
        print("intake: zero eligible survivors -- lawful zero, product "
              "written")
        return 0
    # D6 binding gate needs daily-return faces: re-derive from judged rows
    rows = {r["candidate_id"]: r for r in judge["cells"]}
    prices = load_core()
    cut = pd.Timestamp(CUTOFF)
    pcut = {s: df[df.index <= cut] for s, df in prices.items()}
    P = build_panels(pcut)
    reg_ret = {}
    for t in A_TEMPLATES:
        trader = load_trader(t["trader_id"])
        entry = trader["params"]["entry"]
        from live.paper import SIGNAL_BUILDERS
        sig = SIGNAL_BUILDERS[entry](P)
        params = {k: v for k, v in trader["params"].items() if k != "entry"}
        with ExitPatch(trader.get("exit_overrides")):
            res = run_backtest(pcut, params, entry_signal=sig,
                               exit_signal=(sig <= 0))
        eq = pd.Series(res["equity_curve"],
                       index=P["close"].index[:len(res["equity_curve"])])
        reg_ret[t["trader_id"]] = eq.pct_change().fillna(0.0)
    cand_ret = {}
    ck_path = os.path.join(CKPT_DIR, "judge_shard_0of1.jsonl")
    # judge checkpoint rows carry legL_daily_returns
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    r = json.loads(ln)
                    if r["candidate_id"] in eligible:
                        idx_ret = pd.Series(
                            r["legL_daily_returns"],
                            index=P["close"].index[
                                :len(r["legL_daily_returns"])])
                        cand_ret[r["candidate_id"]] = idx_ret
    all_series = {**reg_ret, **cand_ret}
    names = sorted(all_series)
    mat = pd.concat([all_series[n] for n in names], axis=1).fillna(0.0)
    corr = np.corrcoef(mat.values.T)
    d6 = {}
    survivors = list(eligible)
    for cid in eligible:
        mx = 0.0
        clash = None
        for rn in reg_ret:
            mx_r = abs(float(corr[names.index(cid), names.index(rn)]))
            if mx_r > mx:
                mx, clash = mx_r, rn
        d6[cid] = {"max_corr_vs_registered": round(mx, 4), "clash": clash}
    # survivor-cluster collapse (>=0.7 keep highest DSR, tie lowest id);
    # registered-corr >=0.7 -> outright reject FIRST (prereg sec.1 binding
    # literal ">=0.7 reject"; r366 bm-b fix: the original precedence only
    # cluster-eliminated, so a registered clone could sail into admitted --
    # caught by the W2 hermetic intake leg, mirrored here pre-run, zero
    # W1 cells consumed by the buggy path: W1 judge still pool-waiting)
    eliminated = []
    for cid in eligible:
        if d6[cid]["max_corr_vs_registered"] >= 0.7:
            eliminated.append(cid)
    for a in eligible:
        if a in eliminated:
            continue
        for b in eligible:
            if b <= a or b in eliminated:
                continue
            c = abs(float(corr[names.index(a), names.index(b)]))
            if c >= 0.7:
                dsr_a = rows[a]["dsr"]["dsr"]
                dsr_b = rows[b]["dsr"]["dsr"]
                loser = b if (dsr_a, b) > (dsr_b, a) else a
                eliminated.append(loser)
    admitted = [c for c in eligible if c not in eliminated]
    rejected = [{"candidate_id": c,
                 "reason": "registered-corr" if d6[c][
                     "max_corr_vs_registered"] >= 0.7 else "survivor-cluster",
                 "d6": d6[c]} for c in eligible if c not in admitted]
    intake_rows = []
    for cid in admitted:
        c = cands[cid]
        intake_rows.append({
            "candidate_id": cid, "module": c["module"], "fn": c["fn"],
            "sig_params": c["sig_params"], "axis": c["axis"],
            "family": c["family"],
            "signal_builder_expression": _builder_expression(c),
            "evidence_cutoff": CUTOFF,
            "registration_row": "STRATEGY_LIBRARY row emitted; hr write + "
                                "smoke anchor re-run belongs to the "
                                "registration pipeline (prereg sec.4)",
            "paper_onboarding": f"TRIAL-{c['module'].upper()}-01 PROSPECT-"
                                "machine observation lane (O-2045 reuse)"})
    out = {"wave": WAVE, **cutoff_meta(CUTOFF), "n_eligible": len(eligible),
           "admitted": admitted, "rejected": rejected,
           "d6_binding": d6, "intake": intake_rows,
           "ceo_report_due": "48h from intake (prereg sec.4)",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _dump(os.path.join(RES_DIR, "w1_intake.json"), out)
    print(f"intake: eligible {len(eligible)} -> admitted {len(admitted)} "
          f"(D6 rejects {len(rejected)})")
    return 0


def _builder_expression(cand):
    ps = ", ".join(f"{k}={v}" for k, v in cand["sig_params"].items())
    return f"{cand['fn']}({ps})"


# ------------------------------------------------------------------- status
def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    for f in ("w1_grammar.json", "w1_candidates.json", "prep_state.json",
              "w1_screen.json", "judge_state.json", "w1_judge.json",
              "w1_intake.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'present' if os.path.exists(p) else 'absent'}")
    if os.path.isdir(CKPT_DIR):
        for f in sorted(os.listdir(CKPT_DIR)):
            if f.endswith(".jsonl"):
                n = sum(1 for _ in open(os.path.join(CKPT_DIR, f),
                                        encoding="utf-8"))
                print(f"  checkpoint/{f}: {n} rows")
    gpath = os.path.join(RES_DIR, "w1_grammar.json")
    if os.path.exists(gpath):
        g = json.load(open(gpath, encoding="utf-8"))
        print(f"  grammar sha: {g['grammar_sha256'][:16]} "
              f"(dedup {g['dedup']['raw']} -> {g['dedup']['distinct']})")
    spath = os.path.join(RES_DIR, "w1_screen.json")
    if os.path.exists(spath):
        s = json.load(open(spath, encoding="utf-8"))
        print(f"  screen: survivors {s['n_survivors']}/{s['n_distinct']} "
              f"(null p95 {s['null_family']['p95_line']})")
    return 0


# ------------------------------------------------------------------ selftest
def _synth_prices(n_days=300, n_syms=6, seed=11):
    """Hermetic synthetic panel (r116 law: no repo data files, no network)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=n_days)
    frames = {}
    for s in range(n_syms):
        ret = rng.normal(0.0004, 0.012, n_days)
        close = 100 * np.exp(np.cumsum(ret))
        high = close * (1 + np.abs(rng.normal(0, 0.006, n_days)))
        low = close * (1 - np.abs(rng.normal(0, 0.006, n_days)))
        open_ = close * (1 + rng.normal(0, 0.004, n_days))
        vol = rng.integers(1000, 5000, n_days).astype(float)
        frames[f"5{s:05d}"] = pd.DataFrame(
            {"open": open_, "high": high, "low": low, "close": close,
             "volume": vol, "amount": vol * close}, index=idx)
    frames["510300"] = frames[list(frames)[0]].copy()
    return frames


def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic) ===")
    ok_n = 0
    ok_fail = [0]

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_n += 1
        if not cond:
            ok_fail[0] += 1
        return bool(cond)

    # [1] grammar build determinism + seed registry binding
    g1 = build_grammar()
    g2g = build_grammar()
    ok("grammar build deterministic (sha equal)",
       g1["grammar_sha256"] == g2g["grammar_sha256"])
    ok("seeds bound to SEED_REGISTRY (20283500/20284000/20284500)",
       (SEED_GEN, SEED_NULL, SEED_UNC) == (20283500, 20284000, 20284500))
    ok("B family = mechanical inventory (77 non-grid - 5 A fns)",
       len(g1["families"]["B"]) == 72)
    ok("axis grid = 7x8x4x2 = 448 combos/template",
       len(AXIS_FILTERS) * len(AXIS_EXITS) * len(AXIS_SIZING)
       * len(AXIS_TIMING) == 448)
    ok("value domains include registered A anchors",
       all(t["sig_params"][k] in g1["value_domains"][
           f"{t['module']}.{t['fn']}"][k]
           for t in A_TEMPLATES for k in t["sig_params"]))

    # [2] draws deterministic + exclusion gate bites
    rng_a = np.random.default_rng([SEED_GEN, 0, 0])
    rng_b = np.random.default_rng([SEED_GEN, 0, 0])
    c1 = _draw_candidate(rng_a, "A", 0, g1)
    c2 = _draw_candidate(rng_b, "A", 0, g1)
    ok("uniform draw deterministic (PCG64 double-int derivation)",
       c1 == c2)
    reg_cand = {"module": "ta", "fn": "engulf_reversal",
                "sig_params": {"drop_th": -0.05}, "axis": list(DEFAULT_AXIS)}
    ok("exclusion law: registered default-axis cell rejected",
       _excluded(reg_cand, g1))
    reg_cand2 = dict(reg_cand, axis=["none", "ce_machine", "equal_weight",
                                     "daily_signal"])
    ok("exclusion law: same config on non-default axis NOT excluded",
       not _excluded(reg_cand2, g1))

    # [3] axis transforms on a synthetic panel
    prices = _synth_prices()
    P = build_panels(prices)
    close = P["close"]
    mask = pd.DataFrame(1, index=close.index, columns=close.columns)
    wk = apply_timing(mask, "weekly_grid")
    ok("weekly_grid reduces entry days (ISO first-day gate)",
       0 < int((wk.sum(axis=1) > 0).sum()) < int(len(close) / 3))
    ok("daily_signal is a no-op", (apply_timing(mask, "daily_signal")
                                   == mask).all().all())
    flt = apply_filter(mask, "depth_thresh", P)
    ok("depth_thresh filter keeps a strict subset",
       int(flt.values.sum()) < int(mask.values.sum()))
    # fundamental_mask on synthetic (no mask file -> keep-empty face)
    ok("fundamental_mask with absent mask = honest empty",
       apply_filter(mask, "fundamental_mask", P, None).values.sum() == 0)

    # [4] dedup legs: identical signals collapse; near-twins detected
    fp1 = _fingerprint(mask)
    fp2 = _fingerprint(mask.copy())
    ok("fingerprint leg: identical masks same sha256", fp1 == fp2)
    mask2 = mask.copy()
    mask2.iloc[10, 0] = 0          # near-twin: single-day single-sym flip
    mask3 = mask.copy()
    mask3.iloc[:, 0] = 0           # structurally different signal
    ok("fingerprint leg: different masks differ",
       fp1 != _fingerprint(mask2) and fp1 != _fingerprint(mask3))
    r1 = _naive_returns(mask, close)
    r2 = _naive_returns(mask2, close)
    ok("naive-return leg: near-twins corr >= 0.999 detected",
       abs(np.corrcoef(r1.values, r2.values)[0, 1]) >= 0.999)

    # [5] engine legs: pure time-stop cycles faster than a longer one
    # (low_vol_long = panel face with an always-held top-k sleeve)
    states = pd.Series("GREEN", index=close.index)
    base_cand = {"module": "volatility", "fn": "low_vol_long",
                 "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
                 "family": "B", "candidate_id": "ST-B-0000",
                 "axis": ["none", "time_stop_5d", "equal_weight",
                          "daily_signal"]}
    global GRAMMAR
    GRAMMAR = g1
    eq5, tr5, m5, _, _ = run_candidate_curve(base_cand, None, prices, P,
                                             states)
    c20 = dict(base_cand, axis=["none", "time_stop_20d", "equal_weight",
                                "daily_signal"])
    eq20, tr20, m20, _, _ = run_candidate_curve(c20, None, prices, P,
                                               states)
    ok("pure time stop: 5d machine cycles MORE trades than 20d",
       m5["num_trades"] > m20["num_trades"] > 0)
    ok("engine runs deterministic (equity curve byte-equal)",
       list(eq5.values) == list(run_candidate_curve(base_cand, None, prices,
                                                    P, states)[0].values))

    # [6] dual nulls machinery (vectorized, seeded)
    rng = np.random.default_rng(3)
    r = rng.normal(0.0005, 0.01, 500)
    dn = _dual_nulls(r, 7)
    dn2 = _dual_nulls(r, 7)
    ok("dual nulls deterministic (seed [20284500, cell])",
       dn == dn2 and dn["B"] == 2000 and dn["P"] == 2000)

    # [7] B7b contract leg: consumer keys ⊆ constructor keys (constructor
    # face = cell worker keys + finalize enrichment)
    constructor_keys = {"cell_id", "candidate_id", "family", "module", "fn",
                        "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                        "binom_z", "binom_p", "sharpe_full", "dd_full",
                        "n_trades", "n_entries", "survives_screen"}
    consumer_keys = set(csv_cols_screen)
    ok("B7b contract: screen-csv consumer keys subset-of cell constructor keys",
       consumer_keys <= constructor_keys)

    n_fail = ok_fail[0]
    print(f"selftest: {ok_n} checks, "
          f"{'ALL PASS' if n_fail == 0 else str(n_fail) + ' FAIL'}")
    return 0 if n_fail == 0 else 1


csv_cols_screen = ["cell_id", "candidate_id", "family", "module", "fn",
                   "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                   "binom_z", "binom_p", "sharpe_full", "dd_full",
                   "n_trades", "n_entries", "survives_screen"]


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate")
    sub.add_parser("screen-prep")
    p = sub.add_parser("screen")
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize")
    sub.add_parser("judge-prep")
    p = sub.add_parser("judge")
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize")
    sub.add_parser("intake")
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "generate":
        return cmd_generate()
    if a.cmd == "screen-prep":
        return cmd_screen_prep()
    if a.cmd == "screen":
        return cmd_screen(a.shard, a.shards, a.workers)
    if a.cmd == "screen-finalize":
        return cmd_screen_finalize()
    if a.cmd == "judge-prep":
        return cmd_judge_prep()
    if a.cmd == "judge":
        return cmd_judge(a.shard, a.shards, a.workers)
    if a.cmd == "judge-finalize":
        return cmd_judge_finalize()
    if a.cmd == "intake":
        return cmd_intake()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "selftest":
        return cmd_selftest()
    return 2


if __name__ == "__main__":
    sys.exit(main())
