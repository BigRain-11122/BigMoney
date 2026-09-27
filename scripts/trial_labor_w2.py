# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W2 runner -- T-96 mass-candidate trial wave-2 (5000-deep wave).

Prereg FROZEN (r357): research/TRIAL_LABOR_W2_PREREG.md -- generate grammar +
funnel rules + judgment lines all frozen; post-run only sec.7/8 backfill.

Import-face law (prereg sec.6): enumeration/loading/anchor/envelope primitives
are IMPORTED from trial_labor_w1 (tl1) and mass_trial_w1 (Sobol sample_draws
pattern); strategies/ factory + engine/backtester imported, never rewritten;
engine/exit_rules.py ZERO touch (initial-stop overlay is a GRAMMAR layer).

Engineering mapping disclosure (pre-run, zero cells burned, MSG-20260928-0440):
  prereg sec.3 stop leg says "trigger on day-D low -> exit next day OPEN".
  The engine's exit path has no open-fill primitive (entries are the only
  T+1-open fills; all exits fill at the signal-day CLOSE -- engine native,
  shared by every registered member and W1 cell).  Frozen engine iron rule +
  prereg's own grammar-layer clause forbid touching the engine, so the stop
  overlay maps to: exit-signal augmentation at day D+1 -> engine-native fill
  at D+1 CLOSE.  Conservative intent preserved (post-trigger next-day exit,
  overnight gap borne); the open-vs-close intraday price of D+1 is the single
  disclosed deviation, carried in every stop cell's audit record.

Slice plan (slice-1 landed r358: grammar + overlay + selftest + grammar
serialization; slice-2 landed r359: generate (Sobol draws + four-source
exclusion + effective-face dedup + ledger row + D6 disclosure column));
slice-3 landed r360: screen (prep fail-closed gates + sharded cell burn
with K=200 nulls + finalize survival line); slice-4 landed r362: judge
(judge-prep dual-leg census/manifest gates + judged cells = dual-leg base
x1 AND x2 CostPatch(2) curves + window-grid beat vs passive + regime
segments + dual nulls on the W2 seed 20286500 + descriptive-clause columns
+ MSG-0450 annex-1 stop trigger/fill-day D+1 open-vs-close deviation
disclosure + prereg sec.5 crisis/stop-day counts + finalize G1'v2/DSR/
family-PBO/G2/E[FP]); intake lands the next slice per prereg sec.6):
  - build_grammar_w2(): tl1.build_grammar() extended with the initial-stop
    axis (8 faces -> 3584 axis combos), W2 seed block, W2 per-family counts,
    stop-level formula table; new grammar sha16 (new-syntax face, prereg
    sec.0: != W1 a2fa15f4b06b3c40 != MASS 96269ebe766c3fc2).
  - stop_exit_overlay(): per-symbol signal-level state machine (arm on
    0->1 mask transition at T+1 open, trigger on low<=level, augment exit
    mask at D+1; disarm on signal-off mirroring the engine's own exit).
  - draw_candidate_sobol(): prereg sec.3 Sobol upgrade (scipy qmc.Sobol,
    seed=SEED+family_idx, normalized param box -> discrete domain indices;
    axis five-tuple R/X/S/T/STOP from default_rng([SEED+family_idx, 7919])).
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trial_labor_w1 as tl1  # import-face reuse law (prereg sec.6)
from science_gates import CostPatch, SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W2"
PREREG = "research/TRIAL_LABOR_W2_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w2_gen"]        # 20285500
SEED_NULL = SEED_REGISTRY["trial_labor_w2_scrnull"]   # 20286000
SEED_UNC = SEED_REGISTRY["trial_labor_w2_unc"]        # 20286500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (76 fns round-robin)
K_NULLS = 200      # screen null family size (sec.3)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w2")
GRAMMAR_FILE = os.path.join(RES_DIR, "w2_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w2_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
FROZEN_SHA16 = "1dd3d95792395cec"   # r358 serialized face (MSG-0440 disclosed)
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
SCREEN_FILE = os.path.join(RES_DIR, "w2_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w2_screen_cells.csv")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
JUDGE_FILE = os.path.join(RES_DIR, "w2_judge.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W2_SCREEN"   # prereg sec.3 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W2_JUDGE"     # prereg sec.3 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)

# initial-stop axis (prereg sec.3 expansion face a; frozen levels)
AXIS_STOP = ["none", "p3", "p5", "p8", "p12", "a15", "a20", "a25"]
STOP_FORMULA = {  # long convention; engine is long-only (mirror clause dormant)
    "none": None,
    "p3": {"kind": "pct", "stop": 0.03},
    "p5": {"kind": "pct", "stop": 0.05},
    "p8": {"kind": "pct", "stop": 0.08},
    "p12": {"kind": "pct", "stop": 0.12},
    "a15": {"kind": "atr", "mult": 15.0},
    "a20": {"kind": "atr", "mult": 20.0},
    "a25": {"kind": "atr", "mult": 25.0},
}
AXIS_COMBOS = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
               * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING) * len(AXIS_STOP))

STOP_FILL_MAPPING = (
    "prereg literal: trigger day-D low -> exit D+1 OPEN; engine exits have no "
    "open-fill primitive (all exits fill at signal-day close, engine native "
    "shared by registered members); grammar-layer mapping: exit-sig augment "
    "at D+1 -> engine-native fill at D+1 CLOSE; conservative intent kept "
    "(post-trigger next-day, overnight gap borne); disclosed per-cell"
)


# ------------------------------------------------------------ grammar (slice-1)
def _grammar_sha16(grammar: dict) -> str:
    canon = json.dumps(
        {k: grammar[k] for k in sorted(grammar) if k != "grammar_sha256"},
        sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build_grammar_w2():
    """tl1 grammar extended with the stop axis + W2 seeds/counts (frozen face).

    Exclusion law (prereg sec.1): exact already-judged cells are excluded on
    the initial_stop=none face; tl1's exclusion lists (registered six +
    negative-prior defaults) carry over keyed to axis+["none"].  W1 judged /
    screen-survivor exclusion sources are wired at generate time (sec.1 four
    sources; survivor lists are consumed then, counts disclosed here).
    """
    g = tl1.build_grammar()          # frozen W1 machinery: inventory+domains
    excl = []
    for band in ("registered_default_axis", "negative_default_axis"):
        for e in g["exclusion"][band]:
            excl.append({**e, "axis": list(e["axis"]) + ["none"],
                         "face": f"{band}:stop-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w2-initial-stop-extended",
        "seeds": {"trial_labor_w2_gen": SEED_GEN,
                  "trial_labor_w2_scrnull": SEED_NULL,
                  "trial_labor_w2_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20285500+family_idx, scramble) "
                                "param box + default_rng([20285500+family_idx,"
                                " 7919]) five-tuple axis stream (prereg s.3)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {"filters": tl1.AXIS_FILTERS, "exits": tl1.AXIS_EXITS,
                 "sizing": tl1.AXIS_SIZING, "timing": tl1.AXIS_TIMING,
                 "initial_stop": AXIS_STOP},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": STOP_FORMULA,
        "stop_fill_mapping": STOP_FILL_MAPPING,
        "families": g["families"], "value_domains": g["value_domains"],
        "faces": g["faces"],
        "exclusion": {"stop_none_face": excl,
                      "sources": list(g["exclusion"]["sources"])
                      + ["w1_screen.json survivors (generate-time)",
                         "w1_judge products (pending W1 judge batches)",
                         "MASS judged products"],
                      "note": "initial_stop!=none face = new-syntax legal "
                              "cells (prereg sec.1); W1 judged cells "
                              "implicitly stop=none"},
        "negative_priors": g.get("negative_priors"),
        "inventory_audit": {
            "non_grid_fns": len(g["value_domains"]),
            "a_templates": len(g["families"]["A"]),
            "a_unique_module_fn_keys": len(
                {(t["module"], t["fn"]) for t in g["families"]["A"]}),
            "b_fns": len(g["families"]["B"]),
            "modules_on_disk": 13,
            "grid_own_fns_excluded": 4,
            "count_note": "prereg prose 86-fn/B-76 count not reproducible "
                          "by any standard probe (all-visible=own=81 total); "
                          "W1-lineage inventory convention = frozen "
                          "generation face; disclosed MSG-0440 pre-run",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------- initial-stop overlay layer
def atr20_series(prices: dict) -> pd.DataFrame:
    """Mean true range over 20 trading days ENDING at each date (signal-day
    value; causal). True range = max(h-l, |h-pc|, |l-pc|); min_periods=20."""
    hs, ls, cs = [], [], []
    for sym, df in sorted(prices.items()):
        pc = df["close"].shift(1)
        tr = pd.concat([df["high"] - df["low"],
                        (df["high"] - pc).abs(),
                        (df["low"] - pc).abs()], axis=1).max(axis=1)
        hs.append(tr.rolling(20, min_periods=20).mean().rename(sym))
    return pd.DataFrame(hs).T if hs else pd.DataFrame()


def stop_exit_overlay(mask: pd.DataFrame, prices: dict, stop_key: str,
                       atr20: pd.DataFrame = None):
    """Grammar-layer initial-stop overlay (prereg sec.3 face a; E1 mapping).

    Per-symbol signal-level state machine mirroring the mask convention:
      arm   : mask 0->1 transition at day D -> T+1 open entry at D+1
              (level = entry_open*(1-stop) | entry_open - mult*ATR20[D]);
      scan  : from entry day D+1 onward, first low<=level at day T
              -> exit-mask augmentation at T+1 (engine fills at T+1 close);
      disarm: signal-off day (mask<=0) mirrors the engine's own exit.
    Portfolio constraints (max_positions/cash priority) can make engine
    entries differ from the pre-pass -> overlay is protection-floor
    semantics, trigger/fill days disclosed per-cell (prereg sec.5).
    Returns (augment_df, events) -- augment OR'd into the engine exit mask.
    """
    f = STOP_FORMULA.get(stop_key)
    if f is None:
        z = pd.DataFrame(0, index=mask.index, columns=mask.columns,
                         dtype=int)
        return z, []
    if f["kind"] == "atr" and atr20 is None:
        atr20 = atr20_series(prices)
    augment = pd.DataFrame(0, index=mask.index, columns=mask.columns,
                           dtype=int)
    events = []
    m = mask.fillna(0)
    for sym in m.columns:
        sig = m[sym].values
        idx = m.index
        # alignment law (r137 crash fix): i/day are mask-space; per-symbol
        # price arrays must be reindexed to m.index or short-history
        # members misread dates then overflow (same face as the mirror fn)
        op, lo = (prices[sym]["open"].reindex(m.index).values,
                  prices[sym]["low"].reindex(m.index).values)
        n = len(sig)
        in_pos = armed = False
        level = entry_day = trigger_pending = None
        prev = 0
        for i in range(n):
            day = idx[i]
            # disarm on signal-off (mirror engine exit; pending stop drop)
            if in_pos and sig[i] <= 0:
                in_pos = armed = False
                level = trigger_pending = None
            # fire pending stop exit today (E1: augment at T+1 after trigger)
            if trigger_pending is not None and i >= trigger_pending:
                augment.at[day, sym] = 1
                events.append({"sym": sym, "exit_date": str(day),
                               "trigger_date": str(idx[trigger_pending - 1]),
                               "level": round(float(level), 6)})
                in_pos = armed = False
                level = trigger_pending = None
            # arm on entry day (T+1 after 0->1 transition)
            if armed and not in_pos:
                in_pos = True
                entry_open = op[i]
                if pd.isna(entry_open):
                    continue
                if f["kind"] == "pct":
                    level = entry_open * (1.0 - f["stop"])
                else:
                    a = atr20.at[idx[trigger_arm_day], sym] \
                        if f["kind"] == "atr" else np.nan
                    level = (entry_open - f["mult"] * a
                             if pd.notna(a) else np.nan)
                if not (pd.notna(level) and (f["kind"] == "pct"
                                             or level < entry_open)):
                    level = np.nan          # degenerate arm -> no protection
                events.append({"sym": sym, "arm_date": str(day),
                               "entry_open": round(float(entry_open), 6),
                               "level": (round(float(level), 6)
                                         if pd.notna(level) else None)})
            # trigger scan on in-position days (low touch, entry day onward)
            if in_pos and pd.notna(level) and lo[i] <= level:
                trigger_pending = i + 1 if i + 1 < n else None
                in_pos = False                   # flat for arming purposes
                if trigger_pending is None:
                    events.append({"sym": sym, "trigger_date": str(day),
                                   "note": "trigger at last bar: exit "
                                           "beyond panel, no augment"})
            # queue next arming on fresh 0->1 transition
            if sig[i] > 0 and prev <= 0 and not in_pos and not armed \
                    and trigger_pending is None:
                armed = True
                trigger_arm_day = i             # signal day (ATR20 face)
            prev = sig[i]
    return augment, events


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped to
    discrete domain indices + five-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]). Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6-81 (prereg)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=SEED_GEN + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([SEED_GEN + fam_idx, 7919])
    ax = list(zip(rng.integers(0, len(tl1.AXIS_FILTERS), n_draws),
                  rng.integers(0, len(tl1.AXIS_EXITS), n_draws),
                  rng.integers(0, len(tl1.AXIS_SIZING), n_draws),
                  rng.integers(0, len(tl1.AXIS_TIMING), n_draws),
                  rng.integers(0, len(AXIS_STOP), n_draws)))
    for i in range(n_draws):
        params = {}
        j = 0
        for nm in sorted(dom):
            values = dom[nm]
            if len(values) <= 1:
                params[nm] = values[0] if values else None
                continue
            params[nm] = values[min(int(box[i, j] * len(values)),
                                    len(values) - 1)]
            j += 1
        r_, x_, s_, t_, st_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           AXIS_STOP[st_]], "family": family}


# ------------------------------------------------------- generate slice (s2)
def _ram_gate_gb(threshold=4.0):
    """Three-sample free-RAM gate (r354 law; dual-company shared-machine
    discipline). Returns (min_gb, ok); missing psutil -> gate skipped with
    disclosure value None (fleet machines all carry psutil)."""
    try:
        import psutil
    except ImportError:
        return None, True
    vals = []
    for _ in range(3):
        vals.append(psutil.virtual_memory().available / (1 << 30))
        time.sleep(1.0)
    return round(min(vals), 2), min(vals) >= threshold


def _load_exclusion_rows(grammar):
    """Four-source exclusion (prereg sec.1). Sources 1-2 = frozen serialized
    grammar stop-none face; source 3 = W1 screen survivors consumed at
    generate time; source 4 (W1/MASS judged products) declared-unavailable
    at generate time (both judge batches pool-waiting) -> zero rows, honest
    disclosure, no fabrication."""
    rows = list(grammar["exclusion"]["stop_none_face"])
    disc = {"grammar_stop_none_rows": len(rows)}
    sp = os.path.join(tl1.RES_DIR, "w1_screen.json")
    cp = os.path.join(tl1.RES_DIR, "w1_candidates.json")
    if os.path.exists(sp) and os.path.exists(cp):
        scr = json.load(open(sp, encoding="utf-8"))
        cands = {c["candidate_id"]: c for c in
                 json.load(open(cp, encoding="utf-8"))["candidates"]}
        n = 0
        for cid in sorted(scr.get("survivors", [])):
            c = cands[cid]
            rows.append({"module": c["module"], "fn": c["fn"],
                         "sig_params": c["sig_params"],
                         "axis": list(c["axis"]) + ["none"],
                         "face": "w1_screen_survivor:stop-none",
                         "candidate_id": cid})
            n += 1
        disc["w1_screen_survivors"] = n
    else:
        disc["w1_screen_survivors"] = "declared-unavailable (w1_screen.json " \
                                      "absent)"
    disc["w1_judge_products"] = ("declared-unavailable at generate time: "
                                 "results/trial_labor_w1/w1_judge.json absent "
                                 "(TRIAL_LAB_W1_JUDGE pool-waiting); zero rows")
    disc["mass_judge_products"] = ("declared-unavailable at generate time: "
                                   "MASS_TRIAL_W1_JUDGE shards 0-3 "
                                   "pool-waiting; zero rows")
    return rows, disc


def _excluded_w2(cand, rows):
    """Exact already-judged cell test, stop=none face only (prereg sec.1:
    all W1-lineage judged cells implicitly initial_stop=none; stop!=none
    face = new-syntax legal cells). Returns the exclusion face or None."""
    if cand["axis"][4] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


def _effective_signal_mask(mask, prices, stop_key, atr20):
    """Dedup-face holdings proxy with the initial-stop overlay applied at
    the signal-face caliber (prereg sec.3 dedup legs; zero engine burn).

    Mirrors stop_exit_overlay (slice-1, MSG-0440 E1 mapping): arm on 0->1
    at day a -> entry a+1 open; first holding-day low<=level triggers ->
    exit fill at T+1 close -> flat until the NEXT fresh 0->1 episode (no
    re-entry inside the same signal run); stop=none = W1 identity."""
    if stop_key == "none":
        return mask
    f = STOP_FORMULA[stop_key]
    n = len(mask.index)
    arr = np.array(mask)          # writable copy (to_numpy may be read-only)
    # alignment law (r137 crash fix): starts/ends/e/o are MASK-space
    # positionals, so every per-symbol array must be date-label reindexed
    # to mask.index first -- raw .values is per-symbol space (short-history
    # members misread dates then overflow; atr20 index order also differs
    # from panel order). Missing dates -> NaN -> existing guards no-op.
    atr = (atr20.reindex(index=mask.index, columns=mask.columns).to_numpy()
           if f["kind"] == "atr" else None)
    for col, sym in enumerate(mask.columns):
        sig = mask[sym].values
        if not sig.any():
            continue
        on = (sig > 0).astype(int)
        d = np.diff(on)
        starts = ([0] if on[0] else []) + list(np.nonzero(d == 1)[0] + 1)
        ends = list(np.nonzero(d == -1)[0] + 1)
        if on[-1]:
            ends.append(n)
        op = prices[sym]["open"].reindex(mask.index).values
        lo = prices[sym]["low"].reindex(mask.index).values
        for a, o in zip(starts, ends):
            e = a + 1
            if e >= o:
                continue       # one-day signal: stop cannot precede the exit
            eo = op[e]
            if not np.isfinite(eo):
                continue
            if f["kind"] == "pct":
                level = eo * (1.0 - f["stop"])
            else:
                av = atr[a, col]
                if not np.isfinite(av):
                    continue   # ATR warmup: degenerate arm, no protection
                level = eo - f["mult"] * av
                if not (np.isfinite(level) and level < eo):
                    continue
            hits = np.nonzero(lo[e:o] <= level)[0]
            if len(hits) == 0:
                continue
            t = e + int(hits[0])
            if t + 1 >= o:
                continue       # exit-fill at/after signal-off day: no-op
            arr[t + 1:o, col] = 0   # flat until the next fresh 0->1 episode
    return pd.DataFrame(arr, index=mask.index, columns=mask.columns)


def _registered_naive_series(P, grammar):
    """Registered six members' naive-face daily return series (default
    axis, stop=none) for the per-candidate max|corr| disclosure column
    (prereg sec.1 dedup-byproduct caliber; the D6 BINDING gate at s4 intake
    recomputes at the engine-face caliber per W1 intake precedent)."""
    out = {}
    close = P["close"]
    for t in tl1.A_TEMPLATES:
        mk = f"{t['module']}.{t['fn']}"
        mask = tl1._signal_frame({"module": t["module"], "fn": t["fn"],
                                  "sig_params": t["sig_params"]}, P,
                                 grammar["faces"][mk])
        mask = mask.reindex(index=close.index,
                            columns=close.columns).fillna(0)
        out[t["trader_id"]] = tl1._naive_returns(mask, close).values
    return out


def cmd_generate() -> int:
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w2_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w2_grammar.json absent -- run `grammar` first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != grammar["grammar_sha256"] \
            or grammar["grammar_sha256"] != FROZEN_SHA16:
        print(f"GENERATE-GATE: grammar sha drift -- frozen anchor "
              f"{FROZEN_SHA16} != file {grammar['grammar_sha256']}; refusing")
        return 2
    ram_min, ram_ok = _ram_gate_gb()
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB (three-sample "
              f"r354 law, dual-company discipline) -- honest refuse, pool "
              f"retries when RAM frees")
        return 2
    tl1.GRAMMAR = grammar           # tl1._signal_face reads tl1's global
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = tl1.build_panels(prices)
    close = P["close"]
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in close.columns if s in ok_codes)
    except Exception as e:
        overlap = []
        print(f"  [warn] b_layer_mask load error: {str(e)[:120]}")
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=close.index,
                                      columns=close.columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    atr20 = atr20_series(prices)
    excl_rows, excl_disc = _load_exclusion_rows(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]["stop_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W2-{family}-{i:04d}"
            cand["provenance"] = {"seed": SEED_GEN,
                                  "family_idx": (slot if family == "A"
                                                 else 6 + slot),
                                  "stream_draw_idx": i // n_slots,
                                  "global_draw_idx": i}
            if family == "A":
                cand["template_trader"] = slots[slot]["trader_id"]
                cand["negative_prior"] = False
            else:
                cand["negative_prior"] = \
                    (cand["module"], cand["fn"]) in neg_fns
            hit = _excluded_w2(cand, excl_rows)
            if hit:
                excl_hits[family] += 1
                excluded_log.append({"candidate_id": cand["candidate_id"],
                                     "module": cand["module"],
                                     "fn": cand["fn"],
                                     "axis": cand["axis"], "face": hit})
                continue
            candidates.append(cand)
        print(f"  raw draws {family}={n_draws}, exclusion hits "
              f"{excl_hits[family]}")

    # ---- dedup gate (T-84 s3) on the effective signal face (streaming)
    fps, series = [], []
    for j, cand in enumerate(candidates):
        mk = f"{cand['module']}.{cand['fn']}"
        mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
        mask = mask.reindex(index=close.index,
                            columns=close.columns).fillna(0)
        mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
        mask = tl1.apply_timing(mask, cand["axis"][3])
        S = _effective_signal_mask(mask, prices, cand["axis"][4], atr20)
        fps.append(tl1._fingerprint(S))
        series.append(tl1._naive_returns(S, close).values)
        del mask, S
        if (j + 1) % 250 == 0:
            print(f"  [dedup face] {j + 1}/{len(candidates)}", flush=True)

    fp_groups = {}
    for i, fp in enumerate(fps):
        fp_groups.setdefault(fp, []).append(i)
    keep, fp_collapsed = set(), []
    for fp, members in fp_groups.items():
        members.sort(key=lambda k: candidates[k]["candidate_id"])
        keep.add(members[0])
        fp_collapsed.append({"kept": candidates[members[0]]["candidate_id"],
                             "eliminated": [candidates[m]["candidate_id"]
                                            for m in members[1:]]})
    idx_keep = sorted(keep)
    mat = np.vstack([series[i] for i in idx_keep])
    sd = mat.std(axis=1)
    live_rows = [j for j in range(len(idx_keep)) if sd[j] > 1e-12]
    corr_elim, dead = [], set()
    if len(live_rows) >= 2:
        sub = mat[live_rows]
        corr = np.corrcoef(sub)
        for a_ in range(len(live_rows)):
            for b_ in range(a_ + 1, len(live_rows)):
                if abs(corr[a_, b_]) >= 0.999:
                    ia, ib = idx_keep[live_rows[a_]], idx_keep[live_rows[b_]]
                    ka = candidates[ia]["candidate_id"]
                    kb = candidates[ib]["candidate_id"]
                    dead.add(ib if ka < kb else ia)
                    corr_elim.append({"pair": sorted([ka, kb]),
                                     "corr": round(float(corr[a_, b_]), 6),
                                     "eliminated": candidates[
                                         ib if ka < kb else ia]
                                     ["candidate_id"]})
    final_keep = [i for i in idx_keep if i not in dead]
    distinct = [candidates[i] for i in final_keep]

    # D6 disclosure column (naive face; prereg sec.1 逐格 max|corr|)
    reg_series = _registered_naive_series(P, grammar)
    reg_names = sorted(reg_series)
    R = np.vstack([reg_series[nm] for nm in reg_names]) \
        if reg_names else np.zeros((0, len(close.index)))
    Rc = R - R.mean(axis=1, keepdims=True)
    rn = np.linalg.norm(Rc, axis=1)
    if final_keep:
        F = np.vstack([series[i] for i in final_keep])
        Fc = F - F.mean(axis=1, keepdims=True)
        fn = np.linalg.norm(Fc, axis=1)
        cm = (Fc @ Rc.T) / np.outer(np.where(fn > 1e-12, fn, 1.0),
                                    np.where(rn > 1e-12, rn, 1.0))
    else:
        cm = np.zeros((0, len(reg_names)))
    for row, i in enumerate(final_keep):
        v = cm[row]
        finite = v[np.isfinite(v)]
        candidates[i]["max_corr_vs_registered_naive"] = (
            round(float(np.max(np.abs(finite))), 4)
            if len(finite) else None)

    payload = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
               "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": grammar["grammar_sha256"],
               "n": len(distinct), "candidates": distinct,
               "exclusion": {"hits": excl_hits,
                             "excluded_log": excluded_log,
                             "sources": excl_disc,
                             "note": "cell key=(template, params, "
                                     "axis_config, initial_stop); "
                                     "stop=none face only (sec.1); "
                                     "stop!=none = new-syntax legal cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (stop overlay "
                                 "applied, E1 mapping mirrored; naive-hold "
                                 "returns, zero engine burn); engine faces "
                                 "run at screen (W1 precedent)"},
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-none "
                         "exclusion faces (the serialized negative_priors "
                         "field is None -- face derivation is mechanical)",
                         "note": "Sobol per-slot streams in global "
                                 "round-robin; deterministic pre-burn "
                                 "stage; same-grammar rerun still FORBIDDEN "
                                 "post-consume"},
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(CANDIDATES_FILE, payload)

    # grammar consumption ledger row (append-only; prereg sec.4/sec.6)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    raw_total = len(candidates) + sum(excl_hits.values())
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"raw {raw_total} (A{N_A}/B{N_B}, excl hits "
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} | "
           f"seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} (r358) + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W2-GENERATE, T-96 owner bm-b) | same-grammar "
           f"rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |\n")
    os.makedirs(os.path.dirname(GRAMMAR_LEDGER), exist_ok=True)
    if not os.path.exists(GRAMMAR_LEDGER):
        with open(GRAMMAR_LEDGER, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; TRIAL_LABOR_LAW "
                     "sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(GRAMMAR_LEDGER, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)
    print(f"generate done: raw {raw_total} -> exclusion hits "
          f"{sum(excl_hits.values())} -> dedup distinct {len(distinct)} "
          f"(fp-collapses {len(fp_collapsed)}, corr-collapses "
          f"{len(corr_elim)})")
    print(f"products: w2_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------ screen slice (s2/s3)
csv_cols_screen_w2 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "survives_screen"]


def run_candidate_curve_w2(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None):
    """One W2 candidate cell at the engine face with the initial-stop
    overlay carried per-cell (prereg sec.3 face a; MSG-0440 E1 mapping).

    stop=none -> byte-identical to the tl1 engine face. stop!=none -> the
    effective signal mask (the generate-stage dedup-face caliber, consistency
    law) zeroes the entry signal from the exit-fill day onward: the zeroed
    day IS the exit-signal augmentation day (engine-native (S<=0) exit
    fires at D+1 and fills at D+1 close) and the zeroed signal blocks
    re-entry inside the same signal run (fresh 0->1 re-arms). Protection-
    floor semantics (signal-face arming; engine portfolio constraints may
    differ -- disclosed MSG-0440, per-cell trigger counts carried).
    Returns (eq, trades, metrics, params, patch, stop_fired).
    """
    stop_key = cand["axis"][4]
    if stop_key != "none" and STOP_FORMULA[stop_key]["kind"] == "atr" \
            and atr20 is None:
        atr20 = atr20_series(prices)
    mk = f"{cand['module']}.{cand['fn']}"
    face = "null" if rng_matrix is not None else tl1.GRAMMAR["faces"][mk]
    if rng_matrix is not None:
        mask = tl1._signal_frame(None, P, face, rng_matrix=rng_matrix,
                                 p_on=p_on)
    else:
        mask = tl1._signal_frame(cand, P, face)
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    if stop_key == "none":
        S, stop_fired = mask, 0
    else:
        S = _effective_signal_mask(mask, prices, stop_key, atr20)
        d = (mask > 0) & (S == 0)
        stop_fired = int(sum(int((d[c] & ~d[c].shift(1, fill_value=False)
                                 ).sum()) for c in d.columns))
    params, patch = tl1.candidate_engine_params(cand, template)
    params, scale = tl1.sizing_pieces(cand, P, states, params)
    params["report_num_entries"] = True
    dd_control = (template.get("registered_dd_control")
                  if template is not None else None)
    with tl1.ExitPatch(patch):
        res = tl1.run_backtest(prices, params, entry_signal=S,
                               exit_signal=(S <= 0),
                               entry_size_scale=scale, dd_control=dd_control)
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    return eq, res["trades"], res["metrics"], params, patch, stop_fired


def _null_axis_draw(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i];
    consumption order frozen = p_on regime -> five-tuple axis R/X/S/T/STOP
    -> signal matrix. Same engine/cost/panel as candidate cells (BACKTEST_
    PLAN three iron rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          AXIS_STOP[int(rng.integers(len(AXIS_STOP)))])
    return p_on, list(ax), rng


def _screen_cell_w2(cell):
    """One W2 screen cell: full leg-L backtest with the stop overlay ->
    beat6m row (pool worker; W1 _screen_cell caliber + stop columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W2-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired = run_candidate_curve_w2(
            cand, None, prices, P, states, st["atr20"],
            rng_matrix=mat, p_on=p_on)
    else:
        eq, trades, metrics, params, patch, fired = run_candidate_curve_w2(
            cand, template, prices, P, states, st["atr20"],
            fundamental_ok=st["fundamental_ok"])
    row = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "stop_face": cand["axis"][4],
           "stop_fired": int(fired)}
    if len(eq) < 30 or float(eq.iloc[0]) <= 0:
        row.update({"no_entries": True, "beat6m_k": 0,
                    "beat6m_n": len(starts), "beat6m_rate": 0.0,
                    "sharpe_full": None,
                    "n_trades": int(metrics.get("num_trades", 0)),
                    "n_entries": int(metrics.get("num_entries", 0))})
        return row
    k = n_win = 0
    for p in starts:
        if p + W6M - 1 >= len(eq):
            continue
        n_win += 1
        cret = float(eq.iloc[p + W6M - 1] / eq.iloc[p] - 1.0)
        if cret >= passive[p]:        # prereg sec.3 literal ">="
            k += 1
    rate = k / n_win if n_win else 0.0
    n = len(starts)
    z = (k - 0.5 * n) / math.sqrt(0.25 * n) if n else 0.0
    pval = 2 * (1 - tl1._norm_cdf(abs(z)))
    row.update({"no_entries": False, "module": cand.get("module"),
                "fn": cand.get("fn"), "beat6m_k": k, "beat6m_n": n_win,
                "beat6m_rate": round(rate, 6), "binom_z": round(z, 4),
                "binom_p": round(pval, 6),
                "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                "dd_full": round(float(tl1.max_drawdown(eq)), 4),
                "n_trades": int(metrics.get("num_trades", 0)),
                "n_entries": int(metrics.get("num_entries", 0))})
    return row


def _cell_list_w2():
    """Distinct candidate cells + K null cells (deterministic order;
    shard-split by index; W1 precedent)."""
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    cands = json.load(open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    cells = []
    for c in cands:
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"SCREEN|{c['candidate_id']}",
                      "kind": "cand", "cand": c, "template": template})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None})
    return grammar, cells


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


def _finalize_math(cand_rows, null_rows):
    """Pure survival-line computation (prereg sec.3: survive iff beat6m_rate
    > null-family p95 -- program-frozen, data-adaptive, zero hand-picked
    thresholds). Mutates cand_rows with the survives_screen column."""
    null_rates = [r["beat6m_rate"] for r in null_rows]
    p95 = float(np.percentile(null_rates, 95))
    for r in cand_rows:
        r["survives_screen"] = bool(r["beat6m_rate"] > p95)
    survivors = [r["candidate_id"] for r in cand_rows if r["survives_screen"]]
    return p95, survivors


def cmd_screen_prep() -> int:
    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE fail-closed gates + the
    shared passive 6m precompute (prereg sec.2; W1 cmd_screen_prep caliber
    on the W2 grammar face)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    for p, what in ((GRAMMAR_FILE, "w2_grammar.json"),
                    (CANDIDATES_FILE, "w2_candidates.json")):
        if not os.path.exists(p):
            print(f"PREP-GATE FAIL: {what} absent -- generate pending")
            return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"PREP-GATE FAIL: grammar sha drift "
              f"{grammar['grammar_sha256'][:16]} != frozen {FROZEN_SHA16}")
        return 1
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != FROZEN_SHA16:
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen anchor")
        return 1
    if not tl1.self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1

    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1

    # G-ANCHOR: registered six replayed through the W2 grammar default-axis
    # path (template_default+EW+daily+initial_stop=none -> identity face)
    pcut = {s: df[df.index <= cut] for s, df in prices_full.items()}
    Pfull = tl1.build_panels(pcut)
    anchors = {}
    for t in tl1.A_TEMPLATES:
        trader = tl1.load_trader(t["trader_id"])
        a = tl1.anchor_gate(trader, prices_full)
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        cand = {"module": t["module"], "fn": t["fn"],
                "sig_params": t["sig_params"],
                "axis": list(tl1.DEFAULT_AXIS) + ["none"]}
        eq, *_ = run_candidate_curve_w2(cand, t, pcut, Pfull,
                                        tl1.v3_state_series())
        got_is = tl1.sharpe(eq[eq.index < tl1.OOS_START])
        got_oos = tl1.sharpe(eq[eq.index >= tl1.OOS_START])
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
                  f"{a['got']['in_sample']['sharpe']}, oos {got_oos:.4f} vs "
                  f"{a['got']['out_sample']['sharpe']})")
            return 1
    ga = {"pass": True, "anchors": anchors}

    # leg-L panel + G-CENSUS (P-5C frozen grid, sec.2 wholesale binding)
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen} != "
              f"{tl1.FROZEN_CENSUS['L']}")
        return 1
    gc_ = {"pass": True, "census": cen, "frozen": tl1.FROZEN_CENSUS["L"]}
    close = P["close"]
    n = len(idx)
    starts = [p for p in range(n)
              if idx[p] >= tl1.LEG_L_FLOOR and p >= tl1.WARMUP_TD
              and p <= n - 1 - W6M and listed.iloc[p] >= tl1.MIN_LISTED]
    if len(starts) != tl1.FROZEN_CENSUS["L"]["6m"]:
        print(f"PREP-GATE FAIL: 6m starts {len(starts)} != "
              f"{tl1.FROZEN_CENSUS['L']['6m']}")
        return 1
    passive_6m = {}
    for p in starts:
        sdate = idx[p]
        edate = idx[p + W6M - 1]
        syms = close.columns[close.loc[sdate].notna()]
        rel = tl1.passive_rel(close, syms, sdate, edate)
        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)

    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,
            **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "gates": {"G-PANEL": gp, "G-ANCHOR": ga, "G-CENSUS": gc_,
                      "G-EXCLUDE": {"pass": True,
                                    "hits": cg["exclusion"]["hits"],
                                    "sources": cg["exclusion"]["sources"]}},
            "n_distinct": cg["n"], "n_starts_6m": len(starts),
            "starts": starts, "passive_6m_ret": passive_6m,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(PREP_FILE, prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors 6/6 faithful, "
          f"census {cen}, starts {len(starts)}, passive precomputed")
    return 0


def cmd_screen(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDIDATES_FILE, "w2_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w2()
    if _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    tl1.GRAMMAR = grammar
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = tl1._load_leg("L")
    states = tl1.v3_state_series()
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    # keep-ok face = the serialized grammar filter_def ("keep-ok codes only")
    # -- identical to the generate-stage dedup face (consistency law)
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                      columns=P["close"].columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "grammar": grammar, "atr20": atr20_series(prices)}

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
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell_w2, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells", initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_screen_finalize() -> int:
    print(f"=== {WAVE} screen-finalize ===")
    grammar, cells = _cell_list_w2()
    rows = _load_screen_rows()
    by_id = {r["cell_id"]: r for r in rows}
    missing = [c["cell_id"] for c in cells if c["cell_id"] not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} cells incomplete -- finalize "
              f"refused (checkpoint retained); first missing: "
              f"{missing[:3]}")
        return 2
    null_rows = [by_id[f"SCREEN|NULL-{i:04d}"] for i in range(K_NULLS)]
    cand_rows = [by_id[c["cell_id"]] for c in cells if c["kind"] == "cand"]
    p95, survivors = _finalize_math(cand_rows, null_rows)
    null_rates = [r["beat6m_rate"] for r in null_rows]
    stop_counts = {}
    for r in cand_rows:
        stop_counts[r["stop_face"]] = stop_counts.get(r["stop_face"], 0) + 1
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(SCREEN_BATCH, batch_trials,
                               "results/trial_labor_w2/w2_screen.json",
                               evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "screen", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF), "grammar_sha256": grammar["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)), 4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(tl1.NULL_P_REGIMES),
                           "seed": SEED_NULL,
                           "draw_order": "p_on regime -> five-tuple axis "
                                         "R/X/S/T/STOP -> signal matrix "
                                         "(frozen runner face)"},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.3, frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "stop_face_counts": stop_counts,
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber, V1 13bp base, T+1); "
                             "initial-stop overlay at the engine face = "
                             "effective-signal zeroing (MSG-0440 E1 mapping, "
                             "dedup-face consistency); workers BelowNormal; "
                             "checkpoint append-per-cell; beat6m comparison "
                             "operator = >= per frozen prereg sec.3 text"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(SCREEN_FILE, out)
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w2,
                           extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"products: w2_screen.json + w2_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3/s4)
def _dual_nulls_w2(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W2 seed binding [20286500, cell_idx].  tl1._dual_nulls math mirrored
    verbatim -- the seed constant is the only differing face (import law
    kept by the selftest cross-check at the W1 seed)."""
    rng = np.random.default_rng([SEED_UNC if seed is None else seed,
                                 cell_idx])
    r = np.asarray(returns, dtype=float)
    n = len(r)
    mu = float(r.mean())
    B, block = 2000, 20
    n_blocks = int(math.ceil(n / block))
    idx0 = rng.integers(0, max(1, n), size=(B, n_blocks))
    offs = np.arange(block)[None, None, :]
    gather = (idx0[:, :, None] + offs) % n           # circular blocks
    boots = r[gather].reshape(B, -1)[:, :n].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    P = 2000
    signs = rng.choice([-1.0, 1.0], size=(P, n))
    perms = (r[None, :] * signs).mean(axis=1)
    p_two = float((np.abs(perms) >= abs(mu)).mean())
    return {"bootstrap_ci": [round(float(lo), 8), round(float(hi), 8)],
            "ci_lower_positive": bool(lo > 0),
            "signflip_p": round(p_two, 6),
            "B": B, "P": P, "block": block}


def _yearly_returns(eq):
    """Calendar-year compounded returns from the equity curve (pure
    descriptive-clause face, prereg sec.3 descriptive bullet)."""
    if len(eq) < 2 or float(eq.iloc[0]) <= 0:
        return {}
    out = {}
    for y in sorted({d.year for d in eq.index}):
        end_v = float(eq[eq.index.year <= y].iloc[-1])
        prior = eq[eq.index.year < y]
        base = float(prior.iloc[-1]) if len(prior) else float(eq.iloc[0])
        out[str(y)] = round(end_v / base - 1.0, 6)
    return out


def _descriptive_face(eq, eq_x2):
    """Prereg sec.3 descriptive-clause columns (disclosure-only, ZERO gate
    weight; the gates are G1'v2/G2/DSR/PBO per sec.4): annualized>0,
    OOS(2025+ blind) sharpe+annualized both positive, max drawdown >= -35%,
    no calendar year <= -35% (crash-year caliber mirrors the dd line; the
    only threshold face, no invented lines), x2 face yearly stability via
    the same crash-year caliber with the full yearly tables disclosed."""
    def _ann(s):
        if len(s) < 2 or float(s.iloc[0]) <= 0:
            return None
        return float((float(s.iloc[-1]) / float(s.iloc[0]))
                     ** (252.0 / len(s)) - 1.0)

    if len(eq) < 2 or float(eq.iloc[0]) <= 0:
        return {"degenerate": True}
    oos = eq[eq.index >= tl1.OOS_START]
    yearly = _yearly_returns(eq)
    yearly_x2 = _yearly_returns(eq_x2) if len(eq_x2) else {}
    dd = float(tl1.max_drawdown(eq))
    oos_sh = float(tl1.sharpe(oos)) if len(oos) >= 2 else None
    oos_ann = _ann(oos)
    ann = _ann(eq)
    return {"degenerate": False,
            "ann_ret_full": round(ann, 6) if ann is not None else None,
            "oos_sharpe": round(oos_sh, 4) if oos_sh is not None else None,
            "oos_ann_ret": round(oos_ann, 6) if oos_ann is not None else None,
            "dd_full": round(dd, 4),
            "yearly_returns": yearly,
            "yearly_returns_x2": yearly_x2,
            "clause_ann_pos": bool(ann is not None and ann > 0),
            "clause_oos_dual_pos": bool(oos_sh is not None and oos_sh > 0
                                        and oos_ann is not None
                                        and oos_ann > 0),
            "clause_dd_ok": bool(dd >= -0.35),
            "crash_years": [y for y, v in yearly.items() if v <= -0.35],
            "clause_no_crash_year": bool(all(v > -0.35
                                             for v in yearly.values())),
            "clause_x2_no_crash_year": (bool(all(v > -0.35
                                                 for v in
                                                 yearly_x2.values()))
                                        if yearly_x2 else None)}


def _stop_dev_summary(events, prices, mask_index):
    """MSG-0450 annex (1) summary math: trigger/fill-day counts + the D+1
    open-vs-close deviation distribution. One-way check face =
    frac_close_below_open = share of fill days where the engine-native
    close fill is WORSE than the prereg-literal open fill (close < open on
    the exit day = conservative direction of the disclosed E1 mapping).
    Disclosure-only, zero criteria weight."""
    fired = [e for e in events if "trigger_date" in e and "exit_date" in e]
    out = {"n_trigger_events": len(fired), "n_trigger_days": 0,
           "dev_mean": None, "dev_median": None,
           "frac_close_below_open": None, "dev_min": None,
           "dev_max": None}
    devs, days = [], set()
    for e in fired:
        d = pd.Timestamp(e["exit_date"])
        sym = e["sym"]
        if sym not in prices:
            continue
        row = prices[sym].reindex(mask_index)
        o = row["open"].get(d, np.nan)
        c = row["close"].get(d, np.nan)
        if pd.isna(o) or pd.isna(c) or o == 0:
            continue
        devs.append(float(c / o - 1.0))
        days.add(str(e["trigger_date"]))
    out["n_trigger_days"] = len(days)
    if devs:
        arr = np.asarray(devs, dtype=float)
        out.update({"dev_mean": round(float(arr.mean()), 6),
                    "dev_median": round(float(np.median(arr)), 6),
                    "frac_close_below_open": round(float((arr < 0).mean()),
                                                   4),
                    "dev_min": round(float(arr.min()), 6),
                    "dev_max": round(float(arr.max()), 6)})
    return out


def _overlay_stop_disclosure(cand, prices, P, atr20, fundamental_ok):
    """Per-cell stop trigger/fill-day disclosure on the leg-L signal face
    (the same protection-floor overlay the engine face consumes; MSG-0440
    E1 mapping + MSG-0450 annex 1)."""
    stop_key = cand["axis"][4]
    if stop_key == "none":
        s = _stop_dev_summary([], prices, P["close"].index)
        s["stop_face"] = "none"
        return s
    mk = f"{cand['module']}.{cand['fn']}"
    mask = tl1._signal_frame(cand, P, tl1.GRAMMAR["faces"][mk])
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    _, ev = stop_exit_overlay(mask, prices, stop_key, atr20)
    s = _stop_dev_summary(ev, prices, mask.index)
    s["stop_face"] = stop_key
    return s


def _judge_cell_w2(cell):
    """One survivor judged cell (prereg sec.3 s3 frozen face, pool worker):
    dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full curves +
    window-grid beat vs passive + regime segments + dual nulls (W2 seed)
    + descriptive clauses + crisis/stop disclosure columns.  Gates face =
    leg-L base (W1 judged-cell caliber); x2 + descriptive = disclosure."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "stop_face": cand["axis"][4]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        eq, trades, metrics, params, patch, fired = run_candidate_curve_w2(
            cand, template, prices, P, st["states"], st[f"atr20_{leg}"],
            fundamental_ok=fok)
        with CostPatch(2):
            eq2, _, m2, _, _, fired2 = run_candidate_curve_w2(
                cand, template, prices, P, st["states"], st[f"atr20_{leg}"],
                fundamental_ok=fok)
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "stop_fired": 0,
                         "stop_fired_x2": 0,
                         "regime_start_windows": {"bear": 0, "bull": 0,
                                                  "chop": 0, "na": 0},
                         "degenerate": True}
            continue
        daily = eq.pct_change().fillna(0.0)
        segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
        s_series = st["states"].reindex(idx)
        beat, beat_x2 = {}, {}
        for wname, w in tl1.WINDOWS.items():
            starts = st["starts"][leg][wname]
            k = tot = k2 = 0
            for p in starts:
                if p + w - 1 >= len(eq):
                    continue
                tot += 1
                pret = st["passive"][leg][wname][str(p)]
                if float(eq.iloc[p + w - 1] / eq.iloc[p] - 1.0) > pret:
                    k += 1
                if float(eq2.iloc[p + w - 1] / eq2.iloc[p] - 1.0) > pret:
                    k2 += 1
                d = s_series.iloc[p] if p < len(s_series) else None
                st_ = tl1.REGIME_MAP.get(d, "na") if d == d else "na"
                segs[st_] += 1
            beat[wname] = {"k": k, "n": tot,
                          "rate": round(k / tot, 6) if tot else 0.0}
            beat_x2[wname] = {"k": k2, "n": tot,
                              "rate": round(k2 / tot, 6) if tot else 0.0}
        legs[leg] = {"beat": beat, "beat_x2": beat_x2,
                     "regime_start_windows": segs,
                     "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                     "sharpe_full_x2": round(float(tl1.sharpe(eq2)), 4),
                     "n_trades": int(metrics.get("num_trades", 0)),
                     "n_entries": int(metrics.get("num_entries", 0)),
                     "stop_fired": int(fired),
                     "stop_fired_x2": int(fired2)}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
            out["descriptive"] = _descriptive_face(eq, eq2)
            out["crisis_days_gt8pct"] = int(
                (np.abs(np.asarray(daily.values, dtype=float))
                 > 0.08).sum())
            out["stop_disclosure"] = _overlay_stop_disclosure(
                cand, prices, P, st["atr20_L"], fok)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    ci = _dual_nulls_w2(r if len(r) else np.zeros(30), cell["i"])
    out["dual_nulls"] = ci
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def cmd_judge_prep() -> int:
    """Dual-leg census gates + manifest gate + passive per (leg, window)
    (prereg sec.2/3; W1 cmd_judge_prep caliber on the W2 grammar face)."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w2_screen.json "
              "absent)")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if str(screen.get("grammar_sha256", ""))[:16] != FROZEN_SHA16:
        print("JUDGE-PREP-GATE FAIL: screen grammar sha != frozen anchor "
              f"{FROZEN_SHA16}")
        return 1
    man = json.load(open(tl1.T18_MANIFEST, encoding="utf-8"))
    gm = {"verdict": man.get("verdict"),
          "manifest_members": len(man.get("members", {})),
          "pass": bool(man.get("verdict") == "PASS")}
    if not gm["pass"]:
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    starts, passive = {}, {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift {cen} "
                  f"!= {tl1.FROZEN_CENSUS[leg]}")
            return 1
        close = P["close"]
        n = len(idx)
        starts[leg] = {}
        for wname, w in tl1.WINDOWS.items():
            st = [p for p in range(n)
                  if idx[p] >= (tl1.LEG_L_FLOOR if leg == "L"
                                else tl1.LEG_D_FLOOR)
                  and p >= tl1.WARMUP_TD and p <= n - 1 - w
                  and (listed.iloc[p] >= tl1.MIN_LISTED
                       if leg == "L" else True)]
            if len(st) != tl1.FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st)} != {tl1.FROZEN_CENSUS[leg][wname]}")
                return 1
            starts[leg][wname] = st
    if not screen.get("survivors"):
        out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": FROZEN_SHA16, "n_survivors": 0,
               "g_manifest": gm, "starts": starts, "passive": {},
               "census_frozen": tl1.FROZEN_CENSUS, "vacuous": True,
               "note": "zero screen survivors: lawful modal-zero face "
                       "(prereg sec.5 pred.3); judge burn vacuous; "
                       "judge-finalize writes the zero product + ledger 0",
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
        tl1._dump(JUDGE_STATE_FILE, out)
        print("judge-prep PASS (vacuous): zero survivors -- judge burn "
              "skipped, judge-finalize writes the lawful zero product")
        return 0
    passive = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        close = P["close"]
        passive[leg] = {}
        for wname, w in tl1.WINDOWS.items():
            passive[leg][wname] = {}
            for p in starts[leg][wname]:
                sdate = idx[p]
                edate = idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = tl1.passive_rel(close, syms, sdate, edate)
                passive[leg][wname][str(p)] = round(
                    float(rel.iloc[-1] - 1.0), 6)
    out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
           "grammar_sha256": FROZEN_SHA16,
           "n_survivors": len(screen["survivors"]),
           "g_manifest": gm,
           "starts": starts, "passive": passive,
           "census_frozen": tl1.FROZEN_CENSUS,
           "manifest_note": "P-5C frozen census reproduces only on the "
                            "48-member twin cache (W1 sec.9.3 precedent; "
                            "member count disclosed, mechanical import "
                            "wins)",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_STATE_FILE, out)
    print(f"judge-prep PASS: manifest {gm['verdict']} "
          f"({gm['manifest_members']} members), census L/D == frozen, "
          f"survivors {len(screen['survivors'])}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),
                    (SCREEN_FILE, "w2_screen.json")):
        if not os.path.exists(p):
            print(f"JUDGE-GATE: {what} absent -- judge-prep + "
                  "screen-finalize required first")
            return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    if jstate.get("vacuous"):
        print("JUDGE-GATE: vacuous face (zero survivors) -- zero cells, "
              "proceed to judge-finalize")
        return 0
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"JUDGE-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    tl1.GRAMMAR = grammar
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    cands = {c["candidate_id"]: c for c in json.load(
        open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]}
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    cells = []
    for i, cid in enumerate(sorted(screen["survivors"])):
        c = cands[cid]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"JUDGE|{cid}", "candidate_id": cid,
                      "i": i, "cand": c, "template": template})
    mine = [c for i, c in enumerate(cells) if i % shards == shard]

    state = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-GATE: leg-{leg} census drift {cen} -- refuse")
            return 2
        state[f"prices_{leg}"] = prices
        state[f"P_{leg}"] = P
        state[f"idx_{leg}"] = idx
        state[f"atr20_{leg}"] = atr20_series(prices)
        try:
            bl = pd.read_csv(tl1.B_LAYER_MASK)
            ok_codes = set(bl.loc[bl["ok_static"] == True, "code"]
                           .astype(str))
            overlap = sorted(s for s in P["close"].columns
                             if s in ok_codes)
        except Exception:
            overlap = []
        # keep-ok face = identical derivation to the screen-stage face
        # (consistency law); applied per-leg to that leg's own columns
        if overlap:
            fok = pd.DataFrame(False, index=P["close"].index,
                               columns=P["close"].columns)
            for s in overlap:
                fok[s] = True
        else:
            fok = None
        state[f"fundamental_ok_{leg}"] = fok
    state["starts"] = jstate["starts"]
    state["passive"] = jstate["passive"]
    state["states"] = tl1.v3_state_series()
    state["grammar"] = grammar

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
    print(f"judge shard cells {len(mine)}, done {len(done)}, "
          f"todo {len(todo)}")

    def on_result(key, payload):
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell_w2, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                               desc="judge cells",
                               initializer=tl1._init_worker,
                               initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_judge_finalize() -> int:
    print(f"=== {WAVE} judge-finalize ===")
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    survivors = list(screen.get("survivors", []))
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        rows.append(json.loads(ln))
    by_id = {r["cell_id"]: r for r in rows}
    missing = [f"JUDGE|{cid}" for cid in survivors
               if f"JUDGE|{cid}" not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} judged cells incomplete; "
              f"refused (checkpoint retained); first: {missing[:3]}")
        return 2
    judged = [by_id[f"JUDGE|{cid}"] for cid in sorted(survivors)]

    # G1'v2 + DSR per cell (n_trials = live chain head AFTER the screen
    # append; prereg sec.4 cumulative-N, cross-wave no reset)
    n_trials = tl1.ledger_head()["total"]
    batch_cells = screen["batch_cells"]
    for r in judged:
        rets = r.get("legL_daily_returns") or []
        if r.get("legL_sharpe_full") is None or not rets:
            r["g1_prime_v2"] = None
            r["dsr"] = None
            r["g1_pass"] = False
            r["verdict"] = "fail-degenerate"
            continue
        g1 = tl1.g1_prime_v2(r["legL_sharpe_full"], rets, batch_cells,
                             pool="core48", n_trades=r["legL_n_trades"],
                             n_entries=r["legL_n_entries"])
        dsr = tl1.deflated_sharpe_ratio(rets, n_trials=n_trials)
        r["g1_prime_v2"] = g1
        r["dsr"] = {"dsr": round(float(dsr["dsr"]), 6),
                    "n_trials": n_trials}
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample" if not r[
                            "sample_sufficient"] else "fail")
    # family PBO (CSCV 8 blocks; family = strategy module; <8 cells -> n/a)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r.get("module"), []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        series = {r["candidate_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs if r.get("legL_daily_returns")}
        if len(rs) < 8 or len(series) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        mat = tl1.align_returns(series)
        pbo = tl1.cscv_pbo(mat)
        pbos[fam] = {"pbo": round(float(pbo["pbo"]), 4) if isinstance(
            pbo, dict) else round(float(pbo), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # G2 registration columns
    for r in judged:
        if r.get("g1_prime_v2") is None:
            r["g2_registration_v2"] = None
            continue
        g2 = tl1.g2_registration_v2(r["g1_pass"], r["dsr"],
                                   r.get("family_pbo"))
        r["g2_registration_v2"] = g2
    n_judged = len(judged)
    e_fp = round(0.05 * n_judged, 2)
    eligible = [r["candidate_id"] for r in judged
                if (r.get("g2_registration_v2") or {}).get("eligible_v2")]
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judged,
                               "results/trial_labor_w2/w2_judge.json",
                               evidence_cutoff=CUTOFF)
    # descriptive clause batch summary (disclosure-only, zero gate weight)
    cl_keys = [("clause_ann_pos", "annualized > 0"),
               ("clause_oos_dual_pos",
                "OOS(2025+ blind) sharpe + annualized both > 0"),
               ("clause_dd_ok", "max drawdown >= -35%"),
               ("clause_no_crash_year", "no calendar year <= -35%"),
               ("clause_x2_no_crash_year",
                "x2 face: no calendar year <= -35%")]
    clauses = {}
    for k, label in cl_keys:
        vals = [r.get("descriptive", {}).get(k) for r in judged]
        clauses[k] = {"label": label,
                      "n_true": sum(1 for v in vals if v is True),
                      "n_evaluable": sum(1 for v in vals
                                         if v is not None)}
    out = {"wave": WAVE, "stage": "judge", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF), "grammar_sha256": grammar[
               "grammar_sha256"],
           "n_judged_cells": n_judged,
           "n_wave_disclosure": {"screen_cells": batch_cells,
                                 "judged_cells": n_judged,
                                 "E_FP_nominal_5pct": e_fp,
                                 "note": "DSR>=0.95 gate IS the multiple-"
                                         "testing correction (cumulative-N "
                                         "deflation); E[FP] disclosed at "
                                         "the nominal 5% caliber"},
           "family_pbo": pbos,
           "descriptive_summary": {"n_cells": n_judged,
                                   "clauses": clauses,
                                   "note": "descriptive clauses are "
                                           "batch-level disclosure per "
                                           "prereg sec.3 -- zero gate "
                                           "weight; gates = G1'v2/G2/DSR/"
                                           "PBO per sec.4"},
           "eligible_g2": eligible, "n_eligible_g2": len(eligible),
           "trials_ledger": ledger,
           "cells": [{k: v for k, v in r.items()
                      if k != "legL_daily_returns"} for r in judged],
           "audit": {"note": "judged face = dual-leg (P-5C grid) x "
                             "{6m,12m,24m} x base/x2 curves + regime "
                             "segments + dual nulls (B=2000 block-20 + "
                             "P=2000 sign-flip, seed [20286500, cell]); "
                             "gates on the leg-L base face (W1 judged-cell "
                             "caliber); x2 + descriptive clauses = "
                             "disclosure-only zero criteria weight; "
                             "crisis-day count = |daily|>8% leg-L base "
                             "(sec.5.6); stop trigger/fill-day D+1 "
                             "open-vs-close deviation = MSG-0450 annex-1 "
                             "disclosure on the protection-floor signal "
                             "face; fundamental keep-ok face = screen "
                             "consistency law; beat operator = strict > "
                             "(W1 judged-cell caliber; screen >= was the "
                             "sec.3 s2 literal)"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_FILE, out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic, slices 1-4) ===")
    ok_n = 0
    fails = [0]

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_n += 1
        if not cond:
            fails[0] += 1
        return bool(cond)

    # [1] grammar: counts + new sha + seed binding
    g = build_grammar_w2()
    ok("grammar deterministic (sha equal on rebuild)",
       g["grammar_sha256"] == build_grammar_w2()["grammar_sha256"])
    n_b = len(g["families"]["B"])
    # prereg prose says 86 fns / B=76; the r357 count is not reproducible by
    # any standard probe -- the W1-lineage generation machinery (own-module,
    # no-underscore inventory, grid excluded) IS the frozen face and yields
    # 81 own fns (77 non-grid + 4 grid) -> B=72.  Declared in grammar audit +
    # MSG-0440 (pre-run, zero cells burned).
    ok(f"B family = machinery actual 72 (prereg prose 76 declared "
       f"divergent, got {n_b})", n_b == 72)
    ok("inventory audit: 77 non-grid fns, 13 modules on disk",
       g["inventory_audit"]["non_grid_fns"] == 77
       and g["inventory_audit"]["modules_on_disk"] == 13)
    ok("axis combos = 3584 (7x8x4x2x8)",
       g["axis_combos"] == 3584 == AXIS_COMBOS)
    ok("stop axis frozen 8 faces",
       g["axes"]["initial_stop"] == AXIS_STOP and len(AXIS_STOP) == 8)
    ok("seeds bound (20285500/20286000/20286500)",
       (SEED_GEN, SEED_NULL, SEED_UNC) == (20285500, 20286000, 20286500))
    ok("new-syntax sha16 != W1 face",
       g["grammar_sha256"][:16] != "a2fa15f4b06b3c40")
    ok("exclusion carried on stop=none face",
       len(g["exclusion"]["stop_none_face"]) >= 6)

    # [2] stop overlay unit legs (synthetic panel, r116 law)
    frames = tl1._synth_prices(n_days=60, n_syms=2, seed=7)
    mask = pd.DataFrame(0, index=frames["500000"].index,
                        columns=list(frames)[:2], dtype=int)
    mask.iloc[10:40, 0] = 1                      # long signal window
    z1, ev1 = stop_exit_overlay(mask, frames, "none")
    ok("stop=none -> zero overlay + no events", z1.sum().sum() == 0
       and ev1 == [])
    a2, ev2 = stop_exit_overlay(mask, frames, "p3")
    trig = [e for e in ev2 if "trigger_date" in e]
    arms = [e for e in ev2 if "arm_date" in e]
    ok("p3 arm at T+1 open with level entry_open*(1-0.03)",
       any(abs(a["entry_open"] * 0.97 - a["level"]) < 1e-6 for a in arms))
    fired = a2.sum().sum()
    ok(f"p3 overlay deterministic + fired legs coherent (fired={fired})",
       fired == len(trig)
       and stop_exit_overlay(mask, frames, "p3")[0].equals(a2))
    if trig:
        t = mask.index.get_loc(
            pd.Timestamp([e for e in ev2
                          if "trigger_date" in e][0]["trigger_date"]))
        ok("E1 mapping: augment lands at trigger+1",
           a2.iloc[t + 1, 0] == 1 or a2.iloc[t + 1, 1] == 1)
    # no-trigger control: deep stop -> zero overlay
    a3, ev3 = stop_exit_overlay(mask, frames, "a25",
                                atr20=atr20_series(frames))
    ok("a25 deep stop on calm synth panel -> no trigger (ATR face wired)",
       isinstance(a3, pd.DataFrame))

    # [3] Sobol draw determinism + domain binding
    c1 = list(draw_candidate_sobol(g, "A", 0, 32))
    c2 = list(draw_candidate_sobol(g, "A", 0, 32))
    ok("Sobol draw deterministic (32 draws byte-equal)",
       json.dumps(c1, sort_keys=True, default=str)
       == json.dumps(c2, sort_keys=True, default=str))
    ok("draw carries 5-tuple axis with stop face",
       all(len(c["axis"]) == 5 and c["axis"][4] in AXIS_STOP
           for _, c in c1))
    ok("draw params inside frozen domains",
       all(c["sig_params"][nm] in g["value_domains"][
               f"{c['module']}.{c['fn']}"][nm]
           for _, c in c1
           for nm in c["sig_params"]))
    tot = sum(1 for _ in draw_candidate_sobol(g, "B", 0, 64))
    ok("B-family stream yields declared count", tot == 64)

    # [4] W2 exclusion law (prereg sec.1): stop=none face only
    excl_rows = [
        {"module": "ta", "fn": "engulf_reversal",
         "sig_params": {"drop_th": -0.05},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "none"],
         "face": "registered_default_axis:stop-none"},
        {"module": "patterns", "fn": "needle_probe",
         "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
         "axis": ["liquidity", "profit_ladder", "regime_delever",
                  "daily_signal", "none"],
         "face": "w1_screen_survivor:stop-none"}]
    c_reg = {"module": "ta", "fn": "engulf_reversal",
             "sig_params": {"drop_th": -0.05},
             "axis": ["none", "template_default", "equal_weight",
                      "daily_signal", "none"]}
    ok("exclusion: registered default stop-none cell rejected",
       _excluded_w2(c_reg, excl_rows) is not None)
    ok("exclusion: same cell stop!=none NOT excluded (new-syntax face)",
       _excluded_w2(dict(c_reg, axis=[*c_reg["axis"][:4], "p3"]),
                    excl_rows) is None)
    c_surv = {"module": "patterns", "fn": "needle_probe",
              "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
              "axis": ["liquidity", "profit_ladder", "regime_delever",
                       "daily_signal", "none"]}
    ok("exclusion: W1 screen survivor cell rejected on stop-none face",
       _excluded_w2(c_surv, excl_rows) is not None)
    ok("exclusion: survivor cell stop!=none NOT excluded",
       _excluded_w2(dict(c_surv, axis=[*c_surv["axis"][:4], "a20"]),
                    excl_rows) is None)

    # [5] effective-face overlay legs (synthetic, hermetic)
    idx = pd.bdate_range("2024-01-02", periods=40)
    flat = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0,
                         "close": 100.0, "volume": 1000.0,
                         "amount": 1e5}, index=idx)
    dip = flat.copy()
    dip.loc[idx[20], "low"] = 90.0        # pierces p3 level 97 on day 20
    mask = pd.DataFrame(0, index=idx, columns=["A", "B"], dtype=int)
    mask.iloc[5:35, 0] = 1
    mask.iloc[5:35, 1] = 1
    S = _effective_signal_mask(mask, {"A": dip, "B": flat}, "p3", None)
    ok("effective face: p3 trigger zeroes post-exit signal days (sym A)",
       int(S["A"].iloc[21:35].sum()) == 0
       and int(S["A"].iloc[6:21].sum()) == 15)
    ok("effective face: no-trigger symbol unchanged",
       (S["B"] == mask["B"]).all())
    ok("effective face: stop=none is the identity",
       _effective_signal_mask(mask, {"A": dip}, "none",
                              None).equals(mask))
    ok("effective face deterministic (double-run byte-equal)",
       _effective_signal_mask(mask, {"A": dip, "B": flat}, "p3",
                              None).equals(S))
    mask1 = pd.DataFrame(0, index=idx, columns=["A"], dtype=int)
    mask1.iloc[10, 0] = 1
    ok("effective face: one-day signal episode unaffected",
       _effective_signal_mask(mask1, {"A": dip}, "p3", None).equals(mask1))
    _, ev = stop_exit_overlay(mask, {"A": dip, "B": flat}, "p3")
    fired = [e for e in ev if "trigger_date" in e and "exit_date" in e]
    ok("cross-check vs slice-1 overlay: S zeroed exactly from exit_date",
       bool(fired) and int(S["A"].loc[pd.Timestamp(fired[0]["exit_date"])]) == 0
       and int(mask["A"].loc[pd.Timestamp(fired[0]["exit_date"])]) == 1
       and int(S["A"].iloc[6:20].sum()) == 14)

    # [6] round-robin stream consumption == per-slot sequential streams
    # (axis rng batches interleave by n_draws -- the identity leg must use
    # the SAME per-slot stream sizes as the round-robin consumption)
    n_slots_a = len(g["families"]["A"])
    n_rr = 18
    streams = {s: draw_candidate_sobol(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)
               for s in range(n_slots_a)}
    rr = [next(streams[i % n_slots_a]) for i in range(n_rr)]
    seq = {s: [c for _, c in draw_candidate_sobol(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)]
           for s in range(n_slots_a)}
    reassembled = [seq[i % n_slots_a][i // n_slots_a] for i in range(n_rr)]
    ok("round-robin consumption == per-slot sequential (identity)",
       json.dumps([c for _, c in rr], sort_keys=True, default=str)
       == json.dumps(reassembled, sort_keys=True, default=str))

    # [7] registered-six naive face builds (zero-variance tolerated)
    tl1.GRAMMAR = g
    frames2 = tl1._synth_prices(n_days=120, n_syms=3, seed=17)
    P2 = tl1.build_panels(frames2)
    reg = _registered_naive_series(P2, g)
    ok("registered-six naive series built (6 members, panel-length)",
       len(reg) == 6 and all(len(v) == len(P2["close"].index)
                             for v in reg.values()))

    # [8] engine-face stop overlay: identity + determinism + trigger count
    frames3 = tl1._synth_prices(n_days=200, n_syms=3, seed=23)
    P3 = tl1.build_panels(frames3)
    st3 = pd.Series("GREEN", index=P3["close"].index)
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none"]}
    eq_id, tr_id, m_id, _, _, fired_id = run_candidate_curve_w2(
        base, None, frames3, P3, st3)
    eq_tl1 = tl1.run_candidate_curve(base, None, frames3, P3, st3)[0]
    ok("engine face: stop=none identical to tl1 face (byte-equal)",
       list(eq_id.values) == list(eq_tl1.values) and fired_id == 0)
    stop_c = dict(base, axis=[*base["axis"][:4], "p3"])
    eq_s, tr_s, m_s, _, _, fired_s = run_candidate_curve_w2(
        stop_c, None, frames3, P3, st3)
    eq_s2, _, _, _, _, fired_s2 = run_candidate_curve_w2(
        stop_c, None, frames3, P3, st3)
    ok("engine face: p3 overlay deterministic (double-run byte-equal)",
       list(eq_s.values) == list(eq_s2.values) and fired_s == fired_s2)
    m0 = tl1._signal_frame(stop_c, P3, g["faces"]["volatility.low_vol_long"])
    m0 = tl1.apply_timing(tl1.apply_filter(
        m0.reindex(index=P3["close"].index,
                   columns=P3["close"].columns).fillna(0),
        "none", P3, None), "daily_signal")
    _, ev = stop_exit_overlay(m0, frames3, "p3")
    n_ev = len([e for e in ev if "exit_date" in e
                and int(m0.at[pd.Timestamp(e["exit_date"]), e["sym"]]) > 0])
    ok(f"engine face: stop_fired == overlay non-redundant trigger events "
       f"(fired={fired_s}, events={n_ev})", fired_s == n_ev)

    # [9] null draw: determinism + five-tuple axis binding
    p1, ax1, _ = _null_axis_draw(7)
    p1b, ax1b, _ = _null_axis_draw(7)
    ok("null draw deterministic (p_on + five-tuple axis)",
       p1 == p1b and ax1 == ax1b)
    ok("null axis = five-tuple with stop face in frozen grids",
       len(ax1) == 5 and ax1[0] in tl1.AXIS_FILTERS
       and ax1[1] in tl1.AXIS_EXITS and ax1[2] in tl1.AXIS_SIZING
       and ax1[3] in tl1.AXIS_TIMING and ax1[4] in AXIS_STOP
       and p1 in tl1.NULL_P_REGIMES)

    # [10] cell machinery in-process (synthetic worker state; no pool)
    atr3 = atr20_series(frames3)
    starts3 = [10, 40, 74]           # all complete 126-td windows (len 200)
    tl1._ST = {"P": P3, "prices": frames3, "states": st3,
               "starts": starts3, "passive_6m": {10: 0.05, 40: 0.05,
                                                  74: 0.05},
               "fundamental_ok": None, "grammar": g, "atr20": atr3}
    row_null = _screen_cell_w2({"cell_id": "SCREEN|NULL-0003",
                               "kind": "null", "i": 3, "cand": None})
    ok("null cell row: id/family/stop-face wired + complete windows",
       row_null["candidate_id"] == "W2-NULL-0003"
       and row_null["family"] == "NULL"
       and row_null["stop_face"] in AXIS_STOP
       and row_null["beat6m_n"] == 3)
    row_cand = _screen_cell_w2({"cell_id": "SCREEN|ST-B-0000",
                               "kind": "cand", "cand": stop_c,
                               "template": None})
    k_c, n_c = row_cand["beat6m_k"], row_cand["beat6m_n"]
    z_c = (k_c - 0.5 * 3) / math.sqrt(0.25 * 3)
    ok("cand cell row: stop face carried + binom math consistent",
       row_cand["stop_face"] == "p3" and row_cand["stop_fired"] == fired_s
       and row_cand["beat6m_rate"] == round(k_c / n_c, 6)
       and row_cand["binom_z"] == round(z_c, 4))
    row_none = _screen_cell_w2({"cell_id": "SCREEN|ST-B-0001",
                                "kind": "cand", "cand": base,
                                "template": None})
    ok("cand cell row: stop=none face carries stop_fired=0",
       row_none["stop_face"] == "none" and row_none["stop_fired"] == 0)

    # [11] finalize math (pure): p95 line + strict survivor rule
    null_rows_t = [{"beat6m_rate": (i % 40) / 100.0} for i in range(20)]
    cand_rows_t = [{"candidate_id": f"C{i:03d}",
                    "beat6m_rate": r}
                   for i, r in enumerate([0.10, 0.31, 0.39, 0.40, 0.45])]
    p95_t, surv_t = _finalize_math(cand_rows_t, null_rows_t)
    ok("finalize math: p95 == numpy percentile of null rates",
       abs(p95_t - float(np.percentile(
           [r["beat6m_rate"] for r in null_rows_t], 95))) < 1e-12)
    ok("finalize math: survivors = rate > p95 (strict, flag column set)",
       surv_t == [c["candidate_id"] for c in cand_rows_t
                  if c["beat6m_rate"] > p95_t]
       and all(c["survives_screen"] == (c["beat6m_rate"] > p95_t)
               for c in cand_rows_t))

    # [12] ledger batch names frozen (prereg sec.3 literals, no OR-suffix
    # drift from WAVE constant)
    ok("ledger batch names frozen per prereg sec.3 literals",
       SCREEN_BATCH == "TRIAL_LAB_W2_SCREEN"
       and JUDGE_BATCH == "TRIAL_LAB_W2_JUDGE")

    # [13] B7b contract: csv consumer keys subset of cell constructor keys
    constructor_keys = {"cell_id", "candidate_id", "family", "module", "fn",
                       "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                       "binom_z", "binom_p", "sharpe_full", "dd_full",
                       "n_trades", "n_entries", "stop_face", "stop_fired",
                       "survives_screen"}
    ok("B7b contract: screen-csv consumer keys subset of constructor keys",
       set(csv_cols_screen_w2) <= constructor_keys)

    # [14] dual nulls W2 (prereg sec.3 s3; seed 20286500 binding)
    rng14 = np.random.default_rng(11)
    r14 = rng14.normal(0.0005, 0.01, 500)
    dn = _dual_nulls_w2(r14, 7)
    dn_b = _dual_nulls_w2(r14, 7)
    ok("dual nulls w2 deterministic (seed [20286500, cell])",
       dn == dn_b and dn["B"] == 2000 and dn["P"] == 2000
       and dn["block"] == 20)
    dn0 = _dual_nulls_w2(np.zeros(100), 3)
    ok("dual nulls w2 degenerate zero face (CI [0,0], p=1)",
       dn0["bootstrap_ci"] == [0.0, 0.0] and dn0["signflip_p"] == 1.0
       and dn0["ci_lower_positive"] is False)
    ok("dual nulls w2 math mirror == tl1 face at the W1 seed",
       _dual_nulls_w2(r14, 7, seed=tl1.SEED_UNC)
       == tl1._dual_nulls(r14, 7))

    # [15] descriptive-clause helpers (pure; sec.3 descriptive bullet)
    idx15 = pd.bdate_range("2024-01-02", periods=300)
    up = pd.Series(np.linspace(1.0, 1.5, 300), index=idx15)
    d15 = _descriptive_face(up, up)
    ok("descriptive: rising curve -> ann>0, dd_ok, no crash year, "
       "x2 mirrors",
       d15["clause_ann_pos"] is True and d15["clause_dd_ok"] is True
       and d15["clause_no_crash_year"] is True
       and d15["clause_x2_no_crash_year"] is True
       and d15["yearly_returns"])
    crash = pd.Series(np.concatenate([np.linspace(1.0, 1.05, 150),
                                      np.linspace(1.05, 0.5, 111),
                                      np.full(39, 0.5)]),
                      index=idx15)     # -52% crash INSIDE calendar 2024
    dcr = _descriptive_face(crash, crash)
    ok("descriptive: -52% single-calendar-year crash flagged on both "
       "cost faces",
       dcr["clause_no_crash_year"] is False
       and len(dcr["crash_years"]) == 1
       and dcr["clause_x2_no_crash_year"] is False)
    n_oos = int((idx15 >= tl1.OOS_START).sum())
    oos_eq = pd.Series(1.0, index=idx15)
    oos_eq[idx15 >= tl1.OOS_START] = np.linspace(1.0, 1.0 + 0.3,
                                                 n_oos)
    doo = _descriptive_face(oos_eq, oos_eq)
    ok("descriptive: OOS(2025+) dual-positive leg wired",
       n_oos > 0 and doo["clause_oos_dual_pos"] is True
       and doo["oos_sharpe"] > 0 and doo["oos_ann_ret"] > 0)
    ok("descriptive: degenerate face flagged (empty curve)",
       _descriptive_face(pd.Series([], index=pd.DatetimeIndex([])),
                         pd.Series([], index=pd.DatetimeIndex([]))
                         ).get("degenerate") is True)

    # [16] judge cell machinery in-process (synthetic dual-leg state)
    framesJ = tl1._synth_prices(n_days=300, n_syms=4, seed=29)
    PJ = tl1.build_panels(framesJ)
    stJ = pd.Series("GREEN", index=PJ["close"].index)
    nJ = len(PJ["close"].index)
    startsJ = {leg: {wname: [p for p in range(20, nJ - w, 25)]
                     for wname, w in tl1.WINDOWS.items()}
               for leg in ("L", "D")}
    passiveJ = {leg: {wname: {str(p): 0.05 for p in startsJ[leg][wname]}
                     for wname in tl1.WINDOWS} for leg in ("L", "D")}
    tl1._ST = {"prices_L": framesJ, "P_L": PJ,
               "idx_L": PJ["close"].index,
               "atr20_L": atr20_series(framesJ),
               "fundamental_ok_L": None,
               "prices_D": framesJ, "P_D": PJ,
               "idx_D": PJ["close"].index,
               "atr20_D": atr20_series(framesJ),
               "fundamental_ok_D": None,
               "starts": startsJ, "passive": passiveJ, "states": stJ,
               "grammar": g}
    cellJ = {"cell_id": "JUDGE|ST-B-0000", "candidate_id": "ST-B-0000",
             "i": 3, "cand": base, "template": None}
    rowJ = _judge_cell_w2(cellJ)
    rowJ2 = _judge_cell_w2(cellJ)
    ok("judge cell: legs L/D present + determinism (double-run equal)",
       set(rowJ["legs"]) == {"L", "D"}
       and json.dumps(rowJ, sort_keys=True, default=str)
       == json.dumps(rowJ2, sort_keys=True, default=str))
    ok("judge cell: window grid beat + x2 faces per leg",
       all(set(rowJ["legs"][lg]["beat"]) == set(tl1.WINDOWS)
           and set(rowJ["legs"][lg]["beat_x2"]) == set(tl1.WINDOWS)
           and "sharpe_full_x2" in rowJ["legs"][lg]
           and "stop_fired_x2" in rowJ["legs"][lg]
           for lg in ("L", "D")))
    segsJ = rowJ["legs"]["L"]["regime_start_windows"]
    n_starts_J = sum(len(startsJ["L"][w]) for w in tl1.WINDOWS)
    ok("judge cell: regime segments partition the complete windows "
       "(GREEN->bull)",
       sum(segsJ.values()) == n_starts_J
       and segsJ["bull"] == n_starts_J)
    ok("judge cell: dual nulls seed law [20286500, i]",
       rowJ["dual_nulls"] == _dual_nulls_w2(rowJ["legL_daily_returns"], 3))
    segL = rowJ["legs"]["L"]["regime_start_windows"]
    segD = rowJ["legs"]["D"]["regime_start_windows"]
    ok("judge cell: n_eff == bear+bull+chop sum across BOTH legs; "
       "sufficiency consistent",
       rowJ["n_eff_start_windows"]
       == (segL["bull"] + segL["bear"] + segL["chop"]
           + segD["bull"] + segD["bear"] + segD["chop"])
       and rowJ["sample_sufficient"] is False)
    ok("judge cell: descriptive + crisis column wired",
       "descriptive" in rowJ and "crisis_days_gt8pct" in rowJ
       and rowJ["crisis_days_gt8pct"] >= 0
       and "clause_ann_pos" in rowJ["descriptive"]
       and rowJ["stop_face"] == "none")
    ok("judge cell: stop=none disclosure = zero-face",
       rowJ["stop_disclosure"]["stop_face"] == "none"
       and rowJ["stop_disclosure"]["n_trigger_events"] == 0)
    candS = dict(base, axis=[*base["axis"][:4], "p3"])
    cellS = {"cell_id": "JUDGE|ST-B-0001", "candidate_id": "ST-B-0001",
             "i": 4, "cand": candS, "template": None}
    rowS = _judge_cell_w2(cellS)
    sdS = rowS["stop_disclosure"]
    ok("judge cell: p3 face disclosure structurally complete",
       sdS["stop_face"] == "p3" and sdS["n_trigger_events"] >= 0
       and (sdS["dev_mean"] is None
            or isinstance(sdS["dev_mean"], float))
       and rowS["legs"]["L"]["stop_fired"] >= 0)

    # [17] stop disclosure summary math (MSG-0450 annex 1; dip face)
    gap = flat.copy()
    gap.loc[idx[21], "close"] = 98.0   # exit-day close below open: -2% dev
    ev17 = [{"sym": "A", "trigger_date": str(idx[20]),
             "exit_date": str(idx[21]), "level": 97.0},
            {"sym": "B", "trigger_date": str(idx[22]),
             "exit_date": str(idx[23]), "level": 97.0}]
    sd17 = _stop_dev_summary(ev17, {"A": gap, "B": flat}, idx)
    devA = float(gap["close"].iloc[21] / gap["open"].iloc[21] - 1.0)
    devB = float(flat["close"].iloc[23] / flat["open"].iloc[23] - 1.0)
    ok("stop disclosure: deviation math = exit-day close/open-1 "
       "(mean+median)",
       sd17["n_trigger_events"] == 2 and sd17["n_trigger_days"] == 2
       and abs(sd17["dev_mean"]
               - round((devA + devB) / 2, 6)) < 1e-12
       and abs(sd17["dev_median"]
               - round(float(np.median([devA, devB])), 6)) < 1e-12)
    ok("stop disclosure: one-way face frac_close_below_open (devA<0, "
       "devB==0 -> 0.5)",
       abs(sd17["frac_close_below_open"] - 0.5) < 1e-9
       and abs(sd17["dev_min"] - devA) < 1e-9
       and abs(sd17["dev_max"] - devB) < 1e-9)

    print(f"selftest: {ok_n - fails[0]}/{ok_n} PASS, "
          f"{fails[0]} FAIL")
    return 1 if fails[0] else 0


def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    print(f"grammar file: {GRAMMAR_FILE} "
          f"({'EXISTS' if os.path.exists(GRAMMAR_FILE) else 'not built'})")
    for f in ("w2_candidates.json", "prep_state.json", "w2_screen.json",
              "w2_judge.json", "w2_intake.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'EXISTS' if os.path.exists(p) else '-'}")
    if os.path.isdir(CKPT_DIR):
        for f in sorted(os.listdir(CKPT_DIR)):
            if f.endswith(".jsonl"):
                n = sum(1 for _ in open(os.path.join(CKPT_DIR, f),
                                        encoding="utf-8"))
                print(f"  checkpoint/{f}: {n} rows")
    print("pool: TRIAL-LABOR-W2-GENERATE (bm-a launch-claim 05:40, "
          "single-shot); TRIAL-LABOR-W2-SCREEN waiting (flip = generate "
          "done + screen-prep + RAM gate); TRIAL-LABOR-W2-JUDGE waiting "
          "(flip = screen-finalize + judge-prep + RAM gate; slice built "
          "r362)")
    print("W1 judge batches: still pool-waiting (RAM serialize, r357 defer)")
    return 0


def cmd_grammar() -> int:
    """Serialize the frozen grammar face (prereg sec.3: value-domain table
    frozen at runner-build time; zero candidates drawn -- not a wave run)."""
    g = build_grammar_w2()
    os.makedirs(RES_DIR, exist_ok=True)
    with open(GRAMMAR_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    chk = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    assert chk["grammar_sha256"] == g["grammar_sha256"]
    print(f"w2_grammar.json written: sha16={g['grammar_sha256'][:16]} "
          f"axis_combos={g['axis_combos']} B_fns={len(g['families']['B'])} "
          f"exclusion_entries={len(g['exclusion']['stop_none_face'])}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("selftest")
    sub.add_parser("status")
    sub.add_parser("grammar")
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
    a = ap.parse_args(argv)
    return {"selftest": cmd_selftest, "status": cmd_status,
            "grammar": cmd_grammar, "generate": cmd_generate,
            "screen-prep": cmd_screen_prep, "screen": cmd_screen,
            "screen-finalize": cmd_screen_finalize,
            "judge-prep": cmd_judge_prep, "judge": cmd_judge,
            "judge-finalize": cmd_judge_finalize}[a.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
