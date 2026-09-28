# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W5 runner -- T-114 mass-candidate trial wave-5 (5000-deep,
single-K-line binary yang-confirmation triple-gate wave).

Prereg FROZEN (r405 bm-a): research/TRIAL_LABOR_W5_PREREG.md -- generate
grammar + funnel rules + judgment lines all frozen; post-run only
sec.7/8 backfill. Seeds re-picked 20302000/20302500/20303000 (r405
three-step law; 20299000/20299500 soft-parked for NT-CHAIN-P1 per
MSG-20260929-2305).

Import-face law (prereg sec.6): enumeration/loading/anchor/envelope
primitives are IMPORTED from trial_labor_w1 (tl1); the initial-stop
overlay layer is IMPORTED from trial_labor_w2 (tl2); the regime-gate
overlay layer + declared MASS translation are IMPORTED from
trial_labor_w3 (tl3); the vol overlay layer + dual-gate machinery are
IMPORTED from trial_labor_w4 (tl4); the Sobol sample_draws pattern
follows mass_trial_w1 (paradigm import); strategies/ factory +
engine/backtester imported, never rewritten; engine/exit_rules.py ZERO
touch (gate/vol/yang overlays AND stop overlay are GRAMMAR layers).

Engineering mapping disclosures (pre-run, zero cells burned):

  YANG overlay (prereg sec.3 face a; E1-mapping grammar-layer
  primitive): YANG state = signal-day-d info set on member 510300:
  yang(d) = close(d) > open(d) (single-K-line red/green binary; strict
  > so a doji close==open counts as NOT yang = red, probe r162 face).
  first_yang = only signal-day yang days permit entry; none = W4
  semantic baseline (identity).  ZERO WARMUP window (bar-0 onward
  judgeable -- structural improvement vs VOL's 519-bar med500 window,
  prereg sec.2).  Gate acts on ENTRY PERMITTANCE only (effective signal
  zeroed, MSG-0440 E1-mapping primitive; engine-native signal-off exit
  semantics unchanged).  YANG face != GATE face != VOL face (probe
  r162: yang rate calm 50.76% vs wild 49.90% -- VOL state carries
  almost no yang rate; 2024-09-24 yang AND bear AND wild coexist --
  non-isomorphism facts); triple gate = the intersection of three
  independent permission series.  Composition order frozen everywhere
  (dedup face + engine face): signal -> filter -> timing -> GATE ->
  VOL -> YANG -> initial-stop (a yang-blocked signal never arms a stop;
  W4 order extended, prereg sec.3 tuple order R/X/S/T/STOP/GATE/VOL/
  YANG).

  G-YANG anchor law (prereg sec.2 probe facts, fail-closed): on the
  raw full-history member face (data/daily/sh510300.csv, 3,483 bars
  2012-05-28 -> 2026-09-22 cutoff): yang days == 1,751 (50.27%),
  cross-table lower bounds yang AND bull >= 962 / red AND bear >= 914
  (probe r162 facts file results/_r162bmc_yanggate_probe_facts.json).
  Structural law on every panel face: zero warmup (first_valid_bar_idx
  == 0, na_window == 0) + yang+red == n_bars.

  Exclusion law (prereg sec.1, EIGHT-tuple cell key=(template, params,
  axis_config, initial_stop, gate, vol, yang), SEVEN sources, exact
  already-judged key, yang=none face only): prior-wave keys lacking
  the yang axis are yang=none-completed (semantic-identity match);
  yang=first_yang (any gate/vol combo) = new-syntax legal cells (never
  excluded).  Sources: frozen grammar bands (stop-gate-vol-yang-none
  pad) + w1_screen 149 + w2_screen 404 + MASS screen 166 (declared
  translation) + w3_screen 513 + w4_screen survivors (generate-time
  real-read; absent at freeze = zero rows honest) + judged products
  re-declare window (w1_judge / MASS judged / w2_judge / w3_judge /
  w4_judge -- five sources, generate-time real-read, absent =
  declared-unavailable zero rows).

Slice plan (W4 r397 slice-1/1b precedent; this commit = slice-1 + 1b):
  - slice-1 (this round): build_grammar_w5 (tl1 grammar extended with
    stop (tl2) + gate (tl3) + vol (tl4) + the NEW yang axis ->
    64,512 axis combos, new grammar sha16 != W1/MASS/W2/W3/W4) + yang
    overlay layer + full funnel command set (generate/screen/judge
    trios) + selftest (hermetic: yang causality / zero-warmup /
    yang=none==W4 identity / triple-gate intersection legs / G-YANG
    series-structure legs / r116 B7b contract + r297 double-run
    byte-identity);
  - slice-1b (this round): pool entry TRIAL-LABOR-W5-GENERATE (CPU
    pool face, lane_owner=null; generate/screen lawful NOW -- W5-JUDGE
    queued behind W2/W3/W4-JUDGE + the live judge faces + RAM r354
    sequencing gate per prereg sec.0);
  - NEXT slices (physical deps, separate commits with MSG declarations
    per W2/W3/W4 precedent): intake (judge products required).
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
import trial_labor_w2 as tl2  # initial-stop overlay layer import law
import trial_labor_w3 as tl3  # regime-gate overlay + MASS translation
import trial_labor_w4 as tl4  # vol overlay + dual-gate machinery
from science_gates import CostPatch, SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W5"
PREREG = "research/TRIAL_LABOR_W5_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w5_gen"]        # 20302000
SEED_NULL = SEED_REGISTRY["trial_labor_w5_scrnull"]   # 20302500
SEED_UNC = SEED_REGISTRY["trial_labor_w5_unc"]       # 20303000
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (72-fn machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w5")
GRAMMAR_FILE = os.path.join(RES_DIR, "w5_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w5_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
FROZEN_SHA16 = "29720178c39425de"   # slice-1 serialized face (this round)
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
SCREEN_FILE = os.path.join(RES_DIR, "w5_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w5_screen_cells.csv")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
JUDGE_FILE = os.path.join(RES_DIR, "w5_judge.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W5_SCREEN"   # prereg sec.3 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W5_JUDGE"     # prereg sec.3 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)

# initial-stop axis: imported from tl2 (frozen levels, zero re-declare)
AXIS_STOP = tl2.AXIS_STOP
STOP_FORMULA = tl2.STOP_FORMULA
STOP_FILL_MAPPING = tl2.STOP_FILL_MAPPING
# regime entry-gate axis: imported from tl3 (frozen definition)
AXIS_GATE = tl3.AXIS_GATE
GATE_MEMBER = tl3.GATE_MEMBER
GATE_SPEC = tl3.GATE_SPEC
# volatility entry-gate axis: imported from tl4 (frozen definition)
AXIS_VOL = tl4.AXIS_VOL
VOL_MEMBER = tl4.VOL_MEMBER
VOL_SPEC = tl4.VOL_SPEC
VOL_ANCHOR_FIRST_VALID_BAR = tl4.VOL_ANCHOR_FIRST_VALID_BAR
VOL_ANCHOR_CALM_DAYS = tl4.VOL_ANCHOR_CALM_DAYS
VOL_ANCHOR_WILD_DAYS = tl4.VOL_ANCHOR_WILD_DAYS

# yang entry-confirmation axis (prereg sec.3 face a; NEW W5 frozen layer)
AXIS_YANG = ["none", "first_yang"]
AXIS_COMBOS = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
               * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING)
               * len(AXIS_STOP) * len(AXIS_GATE) * len(AXIS_VOL)
               * len(AXIS_YANG))
YANG_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
YANG_SPEC = {
    "member": YANG_MEMBER,
    "yang": "close(d) > open(d) (single-K-line binary, strict >; doji "
            "close==open counts as red, probe r162 face)",
    "first_yang": "only signal-day yang days permit entry",
    "none": "no gate (W4 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as GATE/VOL, zero lookahead)",
    "warmup": "zero warmup window (bar-0 onward judgeable; structural "
              "improvement vs the VOL 519-bar med500 window)",
    "engine_note": "entry-permittance only (effective signal zeroed, "
                   "MSG-0440 E1-mapping primitive; exit logic zero "
                   "change; engine/exit_rules.py zero touch)",
}
YANG_ANCHOR = {
    "n_bars": 3483, "first_date": "2012-05-28", "cutoff": "2026-09-22",
    "yang_days": 1751, "yang_rate": 0.5027,
    "yang_and_bull_lower_bound": 962, "red_and_bear_lower_bound": 914,
    "probe_facts": "results/_r162bmc_yanggate_probe_facts.json (r162 "
                   "bm-c, probe-facts face not a results face)",
    "note": "cross-table anchors asserted as LOWER BOUNDS per prereg "
            "sec.2 G-YANG (下界); yang_days asserted exact",
}

# W5 exclusion source faces (W4 lineage constants reused by import)
MASS_SCREEN_CKPT = tl4.MASS_SCREEN_CKPT
MASS_JUDGE_FILE = tl4.MASS_JUDGE_FILE
W1_JUDGE_FILE = tl4.W1_JUDGE_FILE
W2_JUDGE_FILE = tl4.W2_JUDGE_FILE
W3_JUDGE_FILE = tl4.W3_JUDGE_FILE
MASS_TRANSLATION_NOTE = tl3.MASS_TRANSLATION_NOTE


def _grammar_sha16(grammar):
    """Grammar sha16 (W4 lineage import; zero re-implementation)."""
    return tl4._grammar_sha16(grammar)


def build_grammar_w5():
    """tl1 grammar extended with the stop axis (tl2 import) + the regime
    gate axis (tl3 import) + the vol axis (tl4 import) + the NEW yang
    axis + W5 seeds/counts (frozen face).

    Exclusion law (prereg sec.1): exact already-judged cells are excluded
    on the yang=none face only; all prior-wave lineage keys are
    yang=none completed (W1 4-tuple + stop/gate/vol/yang none; W2
    5-tuple + gate/vol/yang none; W3 6-tuple + vol/yang none; W4
    7-tuple + yang none; MASS via the declared translation); yang=
    first_yang faces = new-syntax legal cells (never excluded).
    """
    g = tl1.build_grammar()          # frozen W1 machinery: inventory+domains
    excl = []
    for band in ("registered_default_axis", "negative_default_axis"):
        for e in g["exclusion"][band]:
            excl.append({**e, "axis": list(e["axis"])
                         + ["none", "none", "none", "none"],
                         "face": f"{band}:stop-gate-vol-yang-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w5-yang-gate-extended",
        "seeds": {"trial_labor_w5_gen": SEED_GEN,
                  "trial_labor_w5_scrnull": SEED_NULL,
                  "trial_labor_w5_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20302000+family_idx, "
                                "scramble) param box + default_rng("
                                "[20302000+family_idx, 7919]) eight-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG (prereg s.3; A idx 0-5, B idx "
                                "6+slot; re-pick disclosure r405: draft "
                                "berth 20291500 band-collided with "
                                "national_team_s3_perm, three-step law)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {"filters": tl1.AXIS_FILTERS, "exits": tl1.AXIS_EXITS,
                 "sizing": tl1.AXIS_SIZING, "timing": tl1.AXIS_TIMING,
                 "initial_stop": AXIS_STOP, "gate": AXIS_GATE,
                 "vol": AXIS_VOL, "yang": AXIS_YANG},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": STOP_FORMULA,
        "stop_fill_mapping": STOP_FILL_MAPPING,
        "gate_spec": GATE_SPEC,
        "vol_spec": VOL_SPEC,
        "yang_spec": YANG_SPEC,
        "vol_anchor": {"first_valid_bar": VOL_ANCHOR_FIRST_VALID_BAR,
                       "calm_days": VOL_ANCHOR_CALM_DAYS,
                       "wild_days": VOL_ANCHOR_WILD_DAYS,
                       "note": "probe r396 core48/leg-L face "
                               "(results/_r396bma_volgate_probe.py)"},
        "yang_anchor": YANG_ANCHOR,
        "families": g["families"], "value_domains": g["value_domains"],
        "faces": g["faces"],
        "exclusion": {"stop_gate_vol_yang_none_face": excl,
                      "sources": list(g["exclusion"]["sources"])
                      + ["w1_screen.json survivors (generate-time)",
                         "w2_screen.json survivors (generate-time)",
                         "MASS screen survivors (generate-time, declared "
                         "translation)",
                         "w3_screen.json survivors (generate-time)",
                         "w4_screen.json survivors (generate-time real-"
                         "read; absent at freeze = zero rows honest)",
                         "w1_judge / MASS judged / w2_judge / w3_judge / "
                         "w4_judge products (generate-time real-read "
                         "re-declare window)"],
                      "note": "exclusion face = yang=none only; prior-wave "
                              "keys yang=none-completed (semantic identity "
                              "match); yang=first_yang = new-syntax legal "
                              "cells (prereg sec.1)"},
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
                          "generation face (B=72 machinery actual); W2 "
                          "MSG-0440 / W3/W4 selftest disclosures carry "
                          "over verbatim; prereg 4,500/76=59.2 prose "
                          "average reads as 4,500/72=62.5 on the "
                          "machinery face",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------ yang overlay layer
def yang_state_series(prices: dict):
    """Frozen YANG spec (prereg sec.2/3): member 510300 signal-day info
    set -- yang(d) = close(d) > open(d), strict; ZERO warmup (bar-0
    onward judgeable).

    Returns (yang_perm, red_perm, meta): boolean Series on the member's
    own date index + structural meta. Deterministic pure function of
    the (cutoff-truncated) panel."""
    df = prices[YANG_MEMBER]
    close = df["close"].sort_index()
    o = df["open"].reindex(close.index)
    ok = close.notna() & o.notna()
    yang = ok & (close > o)
    red = ok & ~(close > o)
    meta = {"n_bars": int(len(close)),
            "na_window_bars": int((~ok).sum()),
            "first_valid_bar_idx": 0 if int(ok.sum()) == len(close) else
            (int(ok.values.nonzero()[0][0]) if ok.any() else None),
            "yang_days": int(yang.sum()), "red_days": int(red.sum()),
            "yang_rate": (round(float(yang.sum() / len(close)), 4)
                          if len(close) else None),
            "flips_yang_face": int((yang.values[1:]
                                    != yang.values[:-1]).sum())}
    return yang, red, meta


def _yang_face_full():
    """Frozen sec.2 YANG-series face (r162 probe basis verbatim): the
    git-tracked raw full-history member file data/daily/sh510300.csv
    (open + close columns), truncated at the evidence cutoff.  Returns
    the member prices dict {sym: DataFrame(open, close)}, or None when
    absent / columns missing / tail != cutoff."""
    path = os.path.join("data", "daily", f"sh{YANG_MEMBER}.csv")
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip() for c in df.columns]
        if not {"open", "close", "date"} <= set(df.columns):
            return None
        close = df["close"].astype(float)
        close.index = pd.to_datetime(df["date"])
        # r407 fix-first: `open` must carry the SAME date index before
        # any reindex -- reindexing a RangeIndex series against datetime
        # labels matches nothing -> all-NaN open -> na_window == n_bars
        # -> G-YANG honest refusal on a healthy face (r406+ generate
        # burn double-silent-death root cause).
        o = df["open"].astype(float)
        o.index = close.index
        close = close.sort_index()
        o = o.reindex(close.index)
        keep = close.index <= pd.Timestamp(CUTOFF)
        close, o = close[keep], o[keep]
        if not len(close) or str(close.index[-1].date()) != CUTOFF:
            return None
        return {YANG_MEMBER: pd.DataFrame({"open": o, "close": close})}
    except Exception:
        return None


def _yang_state_full():
    """Canonical full-face yang_state with the frozen probe anchors
    asserted (prereg sec.2 G-YANG fail-closed): yang days == 1751
    exact; cross-table lower bounds yang AND bull >= 962 / red AND
    bear >= 914 (gate states on the same raw face).  Returns
    (yang_state, err); err is a one-line honest refusal reason when
    not None."""
    face = _yang_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{YANG_MEMBER}.csv "
                      f"absent/open-close columns missing or truncated "
                      f"tail != cutoff {CUTOFF}")
    ys = yang_state_series(face)
    meta = ys[2]
    if meta.get("yang_days") != YANG_ANCHOR["yang_days"] \
            or meta.get("n_bars") != YANG_ANCHOR["n_bars"]:
        return None, (f"G-YANG full-face anchors {meta} != probe "
                      f"{{n_bars 3483, yang_days 1751}}")
    # cross-table lower bounds need the GATE states computed on the
    # PROBE BASIS VERBATIM (results/_r162bmc_yanggate_probe.py): the
    # probe maps (close > ma200) strictly and the False leg -- which
    # includes the 199-bar MA200 warmup window -- lands in "bear"
    # (bear days 1,703 = 3,483 - 1,780 full window). tl3's grammar-layer
    # gate_state_series instead gate-closes the warmup (min_periods=200,
    # bear = close<ma200 & ma200.notna()) -- reusing it here mismatches
    # the frozen face and broke the anchor on a healthy panel (r407:
    # red∧bear 812 vs probe 914; the 102-bar gap = red days inside the
    # warmup window). Anchors unchanged (fail-closed), only the face
    # computation is aligned to the prereg sec.2 basis.
    close = face[YANG_MEMBER]["close"].sort_index()
    ma200 = close.rolling(GATE_SPEC["ma_window"],
                          min_periods=GATE_SPEC["min_periods"]).mean()
    bull = close > ma200          # probe strict >; NaN comparison -> False
    bear = ~bull                  # probe map False->bear (warmup included)
    y = ys[0].fillna(False)
    yang_bull = int((y & bull.reindex(y.index).fillna(False)).sum())
    red_bear = int((ys[1].fillna(False)
                    & bear.reindex(y.index).fillna(False)).sum())
    if (yang_bull < YANG_ANCHOR["yang_and_bull_lower_bound"]
            or red_bear < YANG_ANCHOR["red_and_bear_lower_bound"]):
        return None, (f"G-YANG cross-table lower bounds broken "
                      f"(yang∧bull {yang_bull}, red∧bear {red_bear})")
    meta = dict(meta)
    meta["cross_gate"] = {"yang_and_bull": yang_bull,
                          "red_and_bear": red_bear}
    return (ys[0], ys[1], meta), None


def yang_zero_mask(mask: pd.DataFrame, yang_key: str, yang_state):
    """Grammar-layer yang entry gate (prereg sec.3 face a; E1-mapping
    primitive): red signal days -> effective signal zeroed (entry
    blocked; engine-native signal-off exit semantics -- the same
    primitive every cell uses when its own signal turns off; zero
    engine touch).  yang=none = W4 semantic baseline (identity).
    Member dates missing from the mask index -> yang-closed
    (conservative reindex law, tl3/tl4 gate caliber)."""
    if yang_key == "none":
        return mask
    yang, _, _ = yang_state
    keep = yang.reindex(mask.index).fillna(False).astype(int)
    return mask.mul(keep, axis=0)


def _yang_structure_pass(yang_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    zero warmup -- first bar onward judgeable; yang+red partitions the
    bar count (doji counts red, frozen strict-> law)."""
    if not isinstance(yang_meta, dict):
        return False
    return (yang_meta.get("na_window_bars") == 0
            and yang_meta.get("first_valid_bar_idx") == 0
            and yang_meta.get("yang_days", -1)
            + yang_meta.get("red_days", -1)
            == yang_meta.get("n_bars", -2))


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w5(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + eight-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL/YANG.  Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6+ (prereg)
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
                  rng.integers(0, len(AXIS_STOP), n_draws),
                  rng.integers(0, len(AXIS_GATE), n_draws),
                  rng.integers(0, len(AXIS_VOL), n_draws),
                  rng.integers(0, len(AXIS_YANG), n_draws)))
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
        r_, x_, s_, t_, st_, gt_, vt_, yg_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           AXIS_STOP[st_], AXIS_GATE[gt_], AXIS_VOL[vt_],
                           AXIS_YANG[yg_]],
                  "family": family}


# ---------------------------------------------------- exclusion (seven sources)
def _load_exclusion_rows_w5(grammar):
    """Seven-source exclusion (prereg sec.1), all real-read at generate
    time.  All prior-wave keys are padded to the W5 EIGHT-tuple with
    yang=none (semantic-identity completion law).  Sources 1 = frozen
    serialized grammar stop-gate-vol-yang-none face; 2-5 = W1/W2/MASS
    (declared tl3 translation)/W3/W4 screen survivors -- W4 is NEW vs
    W4's own loader (generate-time real-read; absent at freeze = zero
    rows honest per prereg sec.1); 6-10 = judged products (w1_judge /
    MASS judged / w2_judge / w3_judge / w4_judge) -- generate-time
    real-read re-declare window (declared-unavailable -> zero rows, no
    fabrication).
    """
    rows = list(grammar["exclusion"]["stop_gate_vol_yang_none_face"])
    disc = {"grammar_stop_gate_vol_yang_none_rows": len(rows)}

    def _screen_survivors(scr_path, cand_path, pad, tag):
        if not (os.path.exists(scr_path) and os.path.exists(cand_path)):
            return f"declared-unavailable ({os.path.basename(scr_path)} " \
                   f"absent)"
        scr = json.load(open(scr_path, encoding="utf-8"))
        cands = {c["candidate_id"]: c for c in
                 json.load(open(cand_path, encoding="utf-8"))["candidates"]}
        n = 0
        for cid in sorted(scr.get("survivors", [])):
            c = cands[cid]
            rows.append({"module": c["module"], "fn": c["fn"],
                         "sig_params": c["sig_params"],
                         "axis": list(c["axis"]) + pad,
                         "face": f"{tag}:stop-gate-vol-yang-none",
                         "candidate_id": cid})
            n += 1
        return n

    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none", "none", "none"], "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none", "none", "none"], "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none", "none"], "w3_screen_survivor")
    disc["w4_screen_survivors"] = _screen_survivors(
        tl4.SCREEN_FILE, tl4.CANDIDATES_FILE,
        ["none"], "w4_screen_survivor")

    # MASS screen survivors: declared tl3 translation + vol-yang none pad
    if os.path.exists(MASS_SCREEN_CKPT):
        n_tr = n_bad = 0
        with open(MASS_SCREEN_CKPT, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                if r.get("row_type") != "candidate" \
                        or not r.get("screen_pass"):
                    continue
                tr = tl3._mass_translate_row(r)
                if tr is None:
                    n_bad += 1
                    continue
                tr["axis"] = list(tr["axis"]) + ["none", "none"]
                tr["face"] = "mass_screen_survivor:translated-exact"
                tr["candidate_id"] = r.get("id")
                rows.append(tr)
                n_tr += 1
        disc["mass_screen_survivors"] = {
            "consumed_pass_rows": n_tr + n_bad,
            "translated_exact_rows": n_tr,
            "non_translatable_disclosed": n_bad,
            "note": MASS_TRANSLATION_NOTE}
    else:
        disc["mass_screen_survivors"] = "declared-unavailable " \
                                        "(screen_checkpoint.jsonl absent)"

    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (freeze-time
    # expectation: all five judge faces pool-waiting per prereg sec.0
    # declare -- live re-read at generate time is the law)
    def _judged_source(jpath, cand_path, pad, tag, mass=False):
        if not os.path.exists(jpath):
            return "declared-unavailable at generate time " \
                   f"({os.path.basename(jpath)} absent; pool-waiting); " \
                   "zero rows"
        j = json.load(open(jpath, encoding="utf-8"))
        cells = j.get("cells", [])
        n = 0
        cands = {}
        if not mass and cand_path and os.path.exists(cand_path):
            cands = {c["candidate_id"]: c for c in json.load(
                open(cand_path, encoding="utf-8"))["candidates"]}
        for c in cells:
            if mass:
                tr = tl3._mass_translate_row(c)
                if tr is None:
                    continue
                tr["axis"] = list(tr["axis"]) + ["none", "none"]
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + pad,
                             "face": f"{tag}:stop-gate-vol-yang-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none", "none", "none"], "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none", "none", "none"], "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none", "none"], "w3_judged")
    disc["w4_judge_products"] = _judged_source(
        tl4.JUDGE_FILE, tl4.CANDIDATES_FILE,
        ["none"], "w4_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window = live prev
    # increment merged at generate time, uniform baseline absent an
    # append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the five judge "
        "products disclosed above")
    return rows, disc


def _excluded_w5(cand, rows):
    """Exact already-judged cell test, yang=none face only (prereg sec.1:
    yang=first_yang = new-syntax legal cells -- never excluded;
    W1-lineage cells implicitly stop/gate/vol/yang=none; W2 cells carry
    their own stop face; W3 stop+gate; W4 stop+gate+vol).  Returns the
    exclusion face or None."""
    if cand["axis"][7] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w5(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, gate_state, vol_state,
                               yang_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> initial-stop (prereg sec.3 dedup legs; zero
    engine burn).  gate=none+vol=none+yang=none+stop=none = W1
    identity; yang=none = W4 semantic baseline; all gate/vol/yang/stop
    faces deterministic layers of the same four grammar overlays."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = yang_zero_mask(V, yang_key, yang_state)
    return tl2._effective_signal_mask(Y, prices, stop_key, atr20)


def run_candidate_curve_w5(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None):
    """One W5 candidate cell at the engine face with the gate + vol +
    yang overlays + initial-stop overlay carried per-cell (prereg sec.3
    face a; frozen composition order filter -> timing -> GATE -> VOL ->
    YANG -> initial-stop).

    yang=none+vol=none+gate=none+stop=none -> byte-identical to the tl1
    engine face; yang=none+vol=none+gate=none -> tl2 W2 face;
    yang=none (gate any) -> tl3 W3 face; yang=none -> tl4 W4 face
    (parity laws, selftest-pinned).  Returns (eq, trades, metrics,
    params, patch, stop_fired, gate_zeroed, vol_zeroed, yang_zeroed).
    """
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    vol_key = cand["axis"][6]
    yang_key = cand["axis"][7]
    if gate_state is None:
        gate_state = tl3.gate_state_series(prices)
    if vol_state is None:
        vol_state = tl4.vol_state_series(prices)
    if yang_state is None:
        yang_state = yang_state_series(prices)
    if stop_key != "none" and STOP_FORMULA[stop_key]["kind"] == "atr" \
            and atr20 is None:
        atr20 = tl2.atr20_series(prices)
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
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = yang_zero_mask(V, yang_key, yang_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    yang_zeroed = int((V > 0).sum().sum() - (Y > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = Y, 0
    else:
        S = tl2._effective_signal_mask(Y, prices, stop_key, atr20)
        d = (Y > 0) & (S == 0)
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
    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \
        gate_zeroed, vol_zeroed, yang_zeroed


def _null_axis_draw_w5(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i];
    consumption order frozen = p_on regime -> eight-tuple axis
    R/X/S/T/STOP/GATE/VOL/YANG -> signal matrix.  Same engine/cost/
    panel as candidate cells incl. the gate + vol + yang legs
    (BACKTEST_PLAN three iron rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          AXIS_STOP[int(rng.integers(len(AXIS_STOP)))],
          AXIS_GATE[int(rng.integers(len(AXIS_GATE)))],
          AXIS_VOL[int(rng.integers(len(AXIS_VOL)))],
          AXIS_YANG[int(rng.integers(len(AXIS_YANG)))])
    return p_on, list(ax), rng


# ------------------------------------------------------ generate slice (s1)
def cmd_generate() -> int:
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w5_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w5_grammar.json absent -- run `grammar` first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != grammar["grammar_sha256"] \
            or (FROZEN_SHA16 and grammar["grammar_sha256"] != FROZEN_SHA16):
        print(f"GENERATE-GATE: grammar sha drift -- frozen anchor "
              f"{FROZEN_SHA16} != file {grammar['grammar_sha256']}; "
              "refusing")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law, dual-company discipline; "
              f"r379 wait-law) -- honest refuse, pool retries when RAM "
              "frees")
        return 2
    tl1.GRAMMAR = grammar           # tl1._signal_frame reads tl1's global
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
    atr20 = tl2.atr20_series(prices)
    gate_state = tl3.gate_state_series(prices)
    vol_state, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"GENERATE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state, yang_err = _yang_state_full()
    if yang_err:
        print(f"GENERATE-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    excl_rows, excl_disc = _load_exclusion_rows_w5(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]["stop_gate_vol_yang_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol_w5(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W5-{family}-{i:04d}"
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
            hit = _excluded_w5(cand, excl_rows)
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
        S = _effective_signal_mask_w5(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      cand["axis"][7], gate_state, vol_state,
                                      yang_state)
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

    # gate/stop/vol/yang face counts + gate x vol x yang triple
    # interaction (prereg sec.5.4 + sec.5.6 triple-gate column)
    gate_counts, stop_counts = {}, {}
    vol_counts, yang_counts = {}, {}
    gate_vol_counts, gvy_counts = {}, {}
    for c in distinct:
        gate_counts[c["axis"][5]] = gate_counts.get(c["axis"][5], 0) + 1
        stop_counts[c["axis"][4]] = stop_counts.get(c["axis"][4], 0) + 1
        vol_counts[c["axis"][6]] = vol_counts.get(c["axis"][6], 0) + 1
        yang_counts[c["axis"][7]] = yang_counts.get(c["axis"][7], 0) + 1
        k2 = f"{c['axis'][5]}|{c['axis'][6]}"
        gate_vol_counts[k2] = gate_vol_counts.get(k2, 0) + 1
        k3 = f"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}"
        gvy_counts[k3] = gvy_counts.get(k3, 0) + 1

    # D6 disclosure column (naive face; prereg sec.1 per-cell max|corr|)
    reg_series = tl2._registered_naive_series(P, grammar)
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
                                     "axis_config, initial_stop, gate, "
                                     "vol, yang); exclusion face = "
                                     "yang=none only (sec.1); prior-wave "
                                     "keys yang=none-completed; yang="
                                     "first_yang = new-syntax legal "
                                     "cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (gate + vol + "
                                 "yang + stop overlays applied, frozen "
                                 "composition order; naive-hold returns, "
                                 "zero engine burn); engine faces run at "
                                 "screen (W1 precedent)"},
               "gate_face_counts": gate_counts,
               "stop_face_counts": stop_counts,
               "vol_face_counts": vol_counts,
               "yang_face_counts": yang_counts,
               "gate_vol_face_counts": gate_vol_counts,
               "gate_vol_yang_face_counts": gvy_counts,
               "gate_state_meta": gate_state[2],
               "vol_state_meta": vol_state[2],
               "yang_state_meta": yang_state[2],
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-"
                         "gate-vol-yang-none exclusion faces (face "
                         "derivation is mechanical)",
                         "seed_repick_disclosure": "draft berths "
                         "20291500/20292000/20292500 band-collided with "
                         "national_team_s3_perm=20291500 (T-103 W5-"
                         "parked-seed observation); re-picked "
                         "20302000/20302500/20303000 per the three-step "
                         "law at the freeze commit (r405, non-result-"
                         "driven)",
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
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} "
           f"(yang faces {json.dumps(yang_counts, sort_keys=True)}; "
           f"gate x vol x yang {json.dumps(gvy_counts, sort_keys=True)}) "
           f"| seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W5-GENERATE, T-114 prereg r405) | same-grammar "
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
    print(f"yang faces: {json.dumps(yang_counts, sort_keys=True)}; "
          f"gate x vol x yang: {json.dumps(gvy_counts, sort_keys=True)}")
    print(f"yang meta: {json.dumps(yang_state[2], sort_keys=True)}")
    print(f"products: w5_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------ screen slice (s2)
csv_cols_screen_w5 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "yang_face", "yang_zeroed", "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law:
# survive iff beat6m_rate > null-family p95 -- program-frozen, zero
# hand-picked thresholds; import-face law, zero re-implementation)
_finalize_math = tl2._finalize_math


def _screen_cell_w5(cell):
    """One W5 screen cell: full leg-L backtest with the gate + vol +
    yang overlays + initial-stop overlay carried per-cell (prereg
    sec.3 face a) -> beat6m row (pool worker; W4 _screen_cell caliber +
    yang columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w5(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W5-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz = \
            run_candidate_curve_w5(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"), yang_state=st.get("yang_state"))
    else:
        eq, trades, metrics, params, patch, fired, gz, vz, yz = \
            run_candidate_curve_w5(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"))
    row = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "stop_face": cand["axis"][4],
           "stop_fired": int(fired), "gate_face": cand["axis"][5],
           "gate_zeroed": int(gz), "vol_face": cand["axis"][6],
           "vol_zeroed": int(vz), "yang_face": cand["axis"][7],
           "yang_zeroed": int(yz)}
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


def _cell_list_w5():
    """Distinct candidate cells + K null cells (deterministic order;
    shard-split by index; W1/W2/W3/W4 precedent)."""
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


def cmd_screen_prep() -> int:
    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE / G-VOL / G-YANG
    fail-closed gates + the shared passive 6m precompute (prereg sec.2;
    W4 cmd_screen_prep caliber on the W5 grammar face + panel gate/vol/
    yang meta disclosure)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    for p, what in ((GRAMMAR_FILE, "w5_grammar.json"),
                    (CANDIDATES_FILE, "w5_candidates.json")):
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
    tl1.GRAMMAR = grammar   # tl1._signal_frame reads tl1's global
    if not tl1.self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1

    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    # G-PANEL validates the cutoff-frozen face, not the raw load face
    # (Monday-bar-proof, T-89 r313 pattern; the generate stage in this
    # same file truncates at load the same way).  Every downstream
    # consumer -- anchor replay pcut, leg-L census via _load_leg --
    # already sees the panel truncated at the frozen cutoff.
    prices_full = {s: df[df.index <= cut] for s, df in prices_full.items()}
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1

    # G-VOL on the raw full-history face (W4 law; probe basis =
    # data/daily/sh510300.csv; NOT the W1-floored load_core pool face)
    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    vol_meta_core = vol_state_full[2]

    # G-YANG on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv open+close; zero warmup + probe anchors)
    yang_state_full, yang_err = _yang_state_full()
    if yang_err:
        print(f"PREP-GATE FAIL: G-YANG {yang_err}")
        return 1
    yang_meta_core = yang_state_full[2]

    # G-ANCHOR: registered six replayed through the W5 grammar
    # default-axis identity face (template_default+EW+daily+
    # initial_stop=none+gate=none+vol=none+yang=none -> tl1 engine
    # identity; run_candidate_curve_w5 parity law selftest-pinned on
    # the gate=none+vol=none+yang=none face)
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
                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none"]}
        eq, *_ = run_candidate_curve_w5(cand, t, pcut, Pfull,
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
    # panel-level gate + vol + yang meta on the leg-L face (prereg
    # sec.2 disclosure; structural invariants only -- the {1523, 1441}
    # vol probe anchors hold only on the raw full-history face; the
    # yang probe anchors likewise (1751) -- asserted above)
    _, _, gate_meta = tl3.gate_state_series(prices)
    _, _, vol_meta = tl4.vol_state_series(prices)
    if not tl4._vol_structure_pass(vol_meta):
        print(f"PREP-GATE FAIL: G-VOL leg-L structural invariants "
              f"broken {vol_meta} -- honest refuse")
        return 1
    _, _, yang_meta = yang_state_series(prices)
    if not _yang_structure_pass(yang_meta):
        print(f"PREP-GATE FAIL: G-YANG leg-L structural invariants "
              f"broken {yang_meta} -- honest refuse")
        return 1
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
                                    "sources": cg["exclusion"]["sources"]},
                      "G-VOL": {"pass": True,
                                "core48": vol_meta_core,
                                "legL": vol_meta,
                                "anchors": {"first_valid_bar":
                                            VOL_ANCHOR_FIRST_VALID_BAR,
                                            "calm_days":
                                            VOL_ANCHOR_CALM_DAYS,
                                            "wild_days":
                                            VOL_ANCHOR_WILD_DAYS}},
                      "G-YANG": {"pass": True,
                                 "core48": yang_meta_core,
                                 "legL": yang_meta,
                                 "anchors": {"yang_days":
                                             YANG_ANCHOR["yang_days"],
                                             "yang_and_bull_lower_bound":
                                             YANG_ANCHOR[
                                                 "yang_and_bull_lower_bound"],
                                             "red_and_bear_lower_bound":
                                             YANG_ANCHOR[
                                                 "red_and_bear_lower_bound"]}}},
            "gate_meta": gate_meta, "vol_meta": vol_meta,
            "yang_meta": yang_meta,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),
            "starts": starts, "passive_6m_ret": passive_6m,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(PREP_FILE, prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors 6/6 faithful, "
          f"census {cen}, starts {len(starts)}, passive precomputed, "
          f"gate na-window {gate_meta['na_window_bars']} bars, "
          f"G-VOL {vol_meta['calm_days']}calm/{vol_meta['wild_days']}wild "
          f"first-valid {vol_meta['first_valid_bar_idx']}, "
          f"G-YANG {yang_meta['yang_days']}yang/{yang_meta['red_days']}"
          f"red zero-warmup")
    return 0


def cmd_screen(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDIDATES_FILE, "w5_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w5()
    if _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"SCREEN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law; r379 wait-law) -- honest "
              "refuse, pool retries when RAM frees")
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
    vol_state, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"SCREEN-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state, yang_err = _yang_state_full()
    if yang_err:
        print(f"SCREEN-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "grammar": grammar, "atr20": tl2.atr20_series(prices),
             "gate_state": tl3.gate_state_series(prices),
             "vol_state": vol_state, "yang_state": yang_state}

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
        jobs = [(c["cell_id"], _screen_cell_w5, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells", initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_screen_finalize() -> int:
    print(f"=== {WAVE} screen-finalize ===")
    grammar, cells = _cell_list_w5()
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
    stop_counts, gate_counts, vol_counts, yang_counts = {}, {}, {}, {}
    gate_seg, vol_seg, yang_seg = {}, {}, {}
    gate_vol_seg, gvy_seg = {}, {}
    for r in cand_rows:
        stop_counts[r["stop_face"]] = stop_counts.get(r["stop_face"], 0) + 1
        gf, vf, yf = r["gate_face"], r["vol_face"], r["yang_face"]
        gate_counts[gf] = gate_counts.get(gf, 0) + 1
        vol_counts[vf] = vol_counts.get(vf, 0) + 1
        yang_counts[yf] = yang_counts.get(yf, 0) + 1
        for seg, key in ((gate_seg, gf), (vol_seg, vf), (yang_seg, yf),
                         (gate_vol_seg, f"{gf}|{vf}"),
                         (gvy_seg, f"{gf}|{vf}|{yf}")):
            s = seg.setdefault(key, {"n_cells": 0, "n_survivors": 0})
            s["n_cells"] += 1
            s["n_survivors"] += int(bool(r["survives_screen"]))
    for seg in (gate_seg, vol_seg, yang_seg, gate_vol_seg, gvy_seg):
        for key, s in seg.items():
            s["survival_rate"] = round(
                s["n_survivors"] / s["n_cells"], 6) if s["n_cells"] else 0.0
    prep = (json.load(open(PREP_FILE, encoding="utf-8"))
            if os.path.exists(PREP_FILE) else {})
    gate_meta = prep.get("gate_meta")
    vol_meta = prep.get("vol_meta")
    yang_meta = prep.get("yang_meta")
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(SCREEN_BATCH, batch_trials,
                               "results/trial_labor_w5/w5_screen.json",
                               evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "screen", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF), "grammar_sha256": grammar["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)), 4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(tl1.NULL_P_REGIMES),
                           "seed": SEED_NULL,
                           "draw_order": "p_on regime -> eight-tuple "
                                         "axis R/X/S/T/STOP/GATE/VOL/"
                                         "YANG -> signal matrix (frozen "
                                         "runner face, gate+vol+yang "
                                         "legs included)"},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.3, frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "stop_face_counts": stop_counts,
           "gate_face_counts": gate_counts,
           "vol_face_counts": vol_counts,
           "yang_face_counts": yang_counts,
           "gate_segmented_survival": gate_seg,
           "vol_segmented_survival": vol_seg,
           "yang_segmented_survival": yang_seg,
           "gate_vol_interaction_survival": gate_vol_seg,
           "gate_vol_yang_interaction_survival": gvy_seg,
           "gate_na_window_bars": (gate_meta["na_window_bars"]
                                   if gate_meta else None),
           "vol_na_window_bars": (vol_meta["na_window_bars"]
                                  if vol_meta else None),
           "yang_na_window_bars": (yang_meta["na_window_bars"]
                                   if yang_meta else None),
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber, V1 13bp base, T+1); "
                             "gate + vol + yang overlays + initial-stop "
                             "overlay at the engine face = effective-"
                             "signal zeroing (MSG-0440 E1 mapping, dedup-"
                             "face consistency, frozen composition order "
                             "signal -> filter -> timing -> GATE -> VOL -> "
                             "YANG -> initial-stop); MA200/vol-closed NaN "
                             "windows gate-closed on BOTH faces, yang "
                             "zero-warmup (panel-level counts in "
                             "gate_na_window_bars / vol_na_window_bars / "
                             "yang_na_window_bars); workers BelowNormal; "
                             "checkpoint append-per-cell; beat6m comparison "
                             "operator = >= per frozen prereg sec.3 text; "
                             "survival math imported from tl2._finalize_"
                             "math (W2 identical law)"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(SCREEN_FILE, out)
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w5,
                           extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"yang segmented survival: "
          f"{json.dumps(yang_seg, sort_keys=True)}")
    print(f"gate x vol x yang interaction survival: "
          f"{json.dumps(gvy_seg, sort_keys=True)}")
    print(f"products: w5_screen.json + w5_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w5(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W5 seed binding [20303000, cell_idx].  Math imported verbatim from
    tl2._dual_nulls_w2 (import law; the seed constant is the only
    differing face -- selftest cross-checks at the W4 seed)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _overlay_stop_disclosure_w5(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state, yang_state):
    """Per-cell stop trigger/fill-day disclosure on the leg-L signal face
    with the W5 composition order (filter -> timing -> GATE -> VOL ->
    YANG -> initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).
    Mirrors tl4._overlay_stop_disclosure_w4 with the yang overlay
    inserted before stop arming (engine-face consistency law; summary
    math imported)."""
    stop_key = cand["axis"][4]
    if stop_key == "none":
        s = tl2._stop_dev_summary([], prices, P["close"].index)
        s["stop_face"] = "none"
        return s
    mk = f"{cand['module']}.{cand['fn']}"
    mask = tl1._signal_frame(cand, P, tl1.GRAMMAR["faces"][mk])
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    G = tl3.gate_zero_mask(mask, cand["axis"][5], gate_state)
    V = tl4.vol_zero_mask(G, cand["axis"][6], vol_state)
    Y = yang_zero_mask(V, cand["axis"][7], yang_state)
    _, ev = tl2.stop_exit_overlay(Y, prices, stop_key, atr20)
    s = tl2._stop_dev_summary(ev, prices, mask.index)
    s["stop_face"] = stop_key
    return s


def _judge_cell_w5(cell):
    """One W5 survivor judged cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full
    curves with the gate + vol + yang + initial-stop overlays carried
    per cell (frozen composition order) + window-grid beat vs passive +
    regime segments + dual nulls (W5 seed [20303000, i]) + descriptive
    clauses + crisis/stop/gate-flip/vol-flip disclosure columns.  Gates
    face = leg-L base (W1-W4 judged-cell caliber); x2 + descriptive =
    disclosure."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "stop_face": cand["axis"][4],
           "gate_face": cand["axis"][5], "vol_face": cand["axis"][6],
           "yang_face": cand["axis"][7]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        gs = st[f"gate_state_{leg}"]
        vs = st[f"vol_state_{leg}"]
        ys = st[f"yang_state_{leg}"]
        eq, trades, metrics, params, patch, fired, gz, vz, yz = \
            run_candidate_curve_w5(cand, template, prices, P,
                                   st["states"], st[f"atr20_{leg}"],
                                   fundamental_ok=fok, gate_state=gs,
                                   vol_state=vs, yang_state=ys)
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, gz2, vz2, yz2 = \
                run_candidate_curve_w5(
                    cand, template, prices, P, st["states"],
                    st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                    vol_state=vs, yang_state=ys)
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "stop_fired": 0,
                         "stop_fired_x2": 0, "gate_zeroed": 0,
                         "gate_zeroed_x2": 0, "vol_zeroed": 0,
                         "vol_zeroed_x2": 0, "yang_zeroed": 0,
                         "yang_zeroed_x2": 0,
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
                     "stop_fired_x2": int(fired2),
                     "gate_zeroed": int(gz),
                     "gate_zeroed_x2": int(gz2),
                     "vol_zeroed": int(vz),
                     "vol_zeroed_x2": int(vz2),
                     "yang_zeroed": int(yz),
                     "yang_zeroed_x2": int(yz2)}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
            out["descriptive"] = tl2._descriptive_face(eq, eq2)
            out["crisis_days_gt8pct"] = int(
                (np.abs(np.asarray(daily.values, dtype=float))
                 > 0.08).sum())
            out["stop_disclosure"] = _overlay_stop_disclosure_w5(
                cand, prices, P, st["atr20_L"], fok, gs, vs, ys)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w5(r if len(r) else np.zeros(30),
                                       cell["i"])
    # prereg sec.5.6 gate/vol-flip day columns (disclosure-only, zero
    # gate weight): panel-level flip-day count of the cell's OWN gate /
    # vol face on the leg-L panel (state meta face; none -> null).  The
    # yang face has no flip-day caliber (daily binary, zero warmup --
    # probe r162 defines no yang flips); its disclosure column is the
    # per-leg yang_zeroed count above.
    gm = st.get("gate_meta_L") or {}
    vm = st.get("vol_meta_L") or {}
    gk = cand["axis"][5]
    vk = cand["axis"][6]
    out["gate_flip_days_legL"] = (
        None if gk == "none"
        else int(gm.get("flips_bull_face" if gk == "bull"
                        else "flips_bear_face", 0)))
    out["vol_flip_days_legL"] = (
        None if vk == "none"
        else int(vm.get("flips_calm_face" if vk == "calm"
                        else "flips_wild_face", 0)))
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def cmd_judge_prep() -> int:
    """Screen-finalize gate + grammar anchor + t18 manifest + dual-leg
    census gates + starts + passive per (leg, window) + per-leg gate +
    vol + yang meta (prereg sec.2/3; W4 cmd_judge_prep caliber on the
    W5 grammar face; G-VOL/G-YANG structural per leg + probe anchors
    on the raw full-history face)."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w5_screen.json "
              "absent)")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if str(screen.get("grammar_sha256", ""))[:16] != FROZEN_SHA16:
        print(f"JUDGE-PREP-GATE FAIL: screen grammar sha != frozen "
              f"anchor {FROZEN_SHA16}")
        return 1
    man = json.load(open(tl1.T18_MANIFEST, encoding="utf-8"))
    gm = {"verdict": man.get("verdict"),
          "manifest_members": len(man.get("members", {})),
          "pass": bool(man.get("verdict") == "PASS")}
    if not gm["pass"]:
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"JUDGE-PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    yang_state_full, yang_err = _yang_state_full()
    if yang_err:
        print(f"JUDGE-PREP-GATE FAIL: G-YANG {yang_err}")
        return 1
    starts, gate_meta, vol_meta, yang_meta = {}, {}, {}, {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift {cen} "
                  f"!= {tl1.FROZEN_CENSUS[leg]}")
            return 1
        if GATE_MEMBER not in prices:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} panel missing gate "
                  f"member {GATE_MEMBER} (gate series underivable)")
            return 1
        if VOL_MEMBER not in prices:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} panel missing vol "
                  f"member {VOL_MEMBER} (vol series underivable)")
            return 1
        if YANG_MEMBER not in prices:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} panel missing yang "
                  f"member {YANG_MEMBER} (yang series underivable)")
            return 1
        _, _, gmeta = tl3.gate_state_series(prices)
        gate_meta[leg] = gmeta
        _, _, vmeta = tl4.vol_state_series(prices)
        if not tl4._vol_structure_pass(vmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-VOL structural "
                  f"invariants broken {vmeta} -- honest refuse")
            return 1
        vol_meta[leg] = vmeta
        _, _, ymeta = yang_state_series(prices)
        if not _yang_structure_pass(ymeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-YANG structural "
                  f"invariants broken {ymeta} -- honest refuse")
            return 1
        yang_meta[leg] = ymeta
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
    vol_meta["full_raw_face"] = vol_state_full[2]
    yang_meta["full_raw_face"] = yang_state_full[2]
    if not screen.get("survivors"):
        out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": FROZEN_SHA16, "n_survivors": 0,
               "g_manifest": gm, "starts": starts, "passive": {},
               "census_frozen": tl1.FROZEN_CENSUS,
               "gate_meta": gate_meta, "vol_meta": vol_meta,
               "yang_meta": yang_meta,
               "vacuous": True,
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
           "census_frozen": tl1.FROZEN_CENSUS, "gate_meta": gate_meta,
           "vol_meta": vol_meta, "yang_meta": yang_meta,
           "manifest_note": "P-5C frozen census reproduces only on the "
                            "48-member twin cache (W1 sec.9.3 precedent; "
                            "member count disclosed, mechanical import "
                            "wins)",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_STATE_FILE, out)
    print(f"judge-prep PASS: manifest {gm['verdict']} "
          f"({gm['manifest_members']} members), census L/D == frozen, "
          f"survivors {len(screen['survivors'])}, gate meta L/D "
          f"na-window {gate_meta['L']['na_window_bars']}/"
          f"{gate_meta['D']['na_window_bars']}, vol meta L/D "
          f"na-window {vol_meta['L']['na_window_bars']}/"
          f"{vol_meta['D']['na_window_bars']} "
          f"(leg-L anchors {vol_meta['L']['calm_days']}calm/"
          f"{vol_meta['L']['wild_days']}wild), yang meta L/D "
          f"zero-warmup {yang_meta['L']['yang_days']}yang/"
          f"{yang_meta['L']['red_days']}red")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),
                    (SCREEN_FILE, "w5_screen.json")):
        if not os.path.exists(p):
            # O-1712 sec.1.2 diagnostic-soundness: the refusal
            # self-locates the expected face (abs path + machine) so
            # absence vs path mismatch vs wrong-machine face reads off
            # the refusal line itself (R398 anchor-face lesson).
            print(f"JUDGE-GATE: {what} absent -- judge-prep + "
                  f"screen-finalize required first; expected face: "
                  f"{os.path.abspath(p)} (this machine: "
                  f"{os.environ.get('COMPUTERNAME', '?')})")
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

    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"JUDGE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state_full, yang_err = _yang_state_full()
    if yang_err:
        print(f"JUDGE-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    state = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-GATE: leg-{leg} census drift {cen} -- refuse")
            return 2
        state[f"prices_{leg}"] = prices
        state[f"P_{leg}"] = P
        state[f"idx_{leg}"] = idx
        state[f"atr20_{leg}"] = tl2.atr20_series(prices)
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
        gs = tl3.gate_state_series(prices)
        state[f"gate_state_{leg}"] = gs
        state[f"gate_meta_{leg}"] = gs[2]
        state[f"vol_state_{leg}"] = vol_state_full
        state[f"vol_meta_{leg}"] = vol_state_full[2]
        state[f"yang_state_{leg}"] = yang_state_full
        state[f"yang_meta_{leg}"] = yang_state_full[2]
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
        jobs = [(c["cell_id"], _judge_cell_w5, (c,)) for c in todo]
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
    # family PBO (CSCV 8 blocks; family = strategy module; <8 cells n/a)
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
                               "results/trial_labor_w5/w5_judge.json",
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
    # GATE/VOL/YANG-face + interaction judged summaries (prereg
    # sec.5.4/sec.5.6 direction-readout + triple-gate column faces;
    # disclosure-only, zero gate weight)
    gate_sum, vol_sum, yang_sum = {}, {}, {}
    gate_vol_sum, gvy_sum = {}, {}
    for r in judged:
        g = r.get("gate_face", "none")
        v = r.get("vol_face", "none")
        y = r.get("yang_face", "none")
        for seg, key in ((gate_sum, g), (vol_sum, v), (yang_sum, y),
                         (gate_vol_sum, f"{g}|{v}"),
                         (gvy_sum, f"{g}|{v}|{y}")):
            s = seg.setdefault(key, {"n_cells": 0, "n_g1_pass": 0,
                                    "n_eligible_g2": 0})
            s["n_cells"] += 1
            s["n_g1_pass"] += int(bool(r.get("g1_pass")))
            s["n_eligible_g2"] += int(
                bool((r.get("g2_registration_v2") or {}).get("eligible_v2")))
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
           "gate_face_judgment": gate_sum,
           "vol_face_judgment": vol_sum,
           "yang_face_judgment": yang_sum,
           "gate_vol_interaction_judgment": gate_vol_sum,
           "gate_vol_yang_interaction_judgment": gvy_sum,
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
                             "{6m,12m,24m} x base/x2 curves with the "
                             "gate + vol + yang + initial-stop overlays "
                             "carried per cell (frozen composition "
                             "signal -> filter -> timing -> GATE -> VOL "
                             "-> YANG -> initial-stop; engine/exit_"
                             "rules.py zero touch) + regime segments + "
                             "dual nulls (B=2000 block-20 + P=2000 "
                             "sign-flip, seed [20303000, cell]); gates on "
                             "the leg-L base face (W1-W4 judged-cell "
                             "caliber); beat operator = strict > (W1-W4 "
                             "judged-cell caliber; screen >= was the "
                             "sec.3 s2 literal); x2 + descriptive clauses "
                             "= disclosure-only zero criteria weight; "
                             "crisis-day count = |daily|>8% leg-L base "
                             "(sec.5.6); stop trigger/fill-day D+1 "
                             "open-vs-close deviation = MSG-0450 annex-1 "
                             "disclosure on the protection-floor signal "
                             "face with the yang overlay inserted before "
                             "stop arming (W5 composition law); gate_flip"
                             "_days_legL / vol_flip_days_legL = panel-"
                             "level flip-day counts of the cell's OWN "
                             "gate / vol face on the leg-L panel (none -> "
                             "null; sec.5.6 disclosure columns, zero gate "
                             "weight; yang face = zero-warmup daily "
                             "binary, no flip caliber, per-leg yang_zeroed "
                             "count is its column); gate x vol x yang "
                             "triple interaction segments = prereg sec.3 "
                             "triple-gate disclosure column; fundamental "
                             "keep-ok face = screen consistency law"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_FILE, out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    print(f"yang-face judgment: {json.dumps(yang_sum, sort_keys=True)}")
    print(f"gate x vol x yang interaction judgment: "
          f"{json.dumps(gvy_sum, sort_keys=True)}")
    return 0


# ------------------------------------------------------------ status / grammar
def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    print(f"grammar file: {GRAMMAR_FILE} "
          f"({'EXISTS' if os.path.exists(GRAMMAR_FILE) else 'not built'})")
    for f in ("w5_candidates.json", "prep_state.json", "w5_screen.json",
              "w5_judge.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'EXISTS' if os.path.exists(p) else '-'}")
    if os.path.isdir(CKPT_DIR):
        for f in sorted(os.listdir(CKPT_DIR)):
            if f.endswith(".jsonl"):
                n = sum(1 for _ in open(os.path.join(CKPT_DIR, f),
                                        encoding="utf-8"))
                print(f"  checkpoint/{f}: {n} rows")
    print("slice map (W4 r397 slice-1/1b precedent): slice-1 grammar + "
          "yang overlay + full funnel command set + selftest LANDED this "
          "round (bm-a r406); slice-1b pool entry TRIAL-LABOR-W5-"
          "GENERATE entered same round (CPU pool face lawful per prereg "
          "sec.6; W5-JUDGE queued behind W2/W3/W4-JUDGE + live judge "
          "faces + RAM r354 sequencing gate per prereg sec.0); NEXT "
          "slices: generate burn (autofill tick) -> screen-prep/screen "
          "burn -> screen-finalize -> judge trio (sequencing gate) -> "
          "intake (physical dep: judge products; separate commits with "
          "MSG declarations per W2/W3/W4 precedence); parallel claim "
          "legal per T-50/T-64 slice precedent after MSG-declare")
    return 0


def cmd_grammar() -> int:
    """Serialize the frozen grammar face (prereg sec.3: value-domain table
    frozen at runner-build time; zero candidates drawn -- not a wave run)."""
    if FROZEN_SHA16 and os.path.exists(GRAMMAR_FILE):
        g = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if g["grammar_sha256"] == FROZEN_SHA16:
            print(f"w5_grammar.json already frozen at anchor "
                  f"{FROZEN_SHA16}; refusing overwrite (append-only face)")
            return 0
    g = build_grammar_w5()
    os.makedirs(RES_DIR, exist_ok=True)
    with open(GRAMMAR_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    chk = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    assert chk["grammar_sha256"] == g["grammar_sha256"]
    print(f"w5_grammar.json written: sha16={g['grammar_sha256'][:16]} "
          f"axis_combos={g['axis_combos']} B_fns={len(g['families']['B'])} "
          f"exclusion_entries="
          f"{len(g['exclusion']['stop_gate_vol_yang_none_face'])}")
    print(f"HARDCODE this sha16 into FROZEN_SHA16 (slice-1 anchor step) "
          f"if not yet pinned: {g['grammar_sha256']}")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic, slice-1 + generate + screen "
          f"+ judge) ===")
    ok_n = 0
    fails = [0]

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_n += 1
        if not cond:
            fails[0] += 1
        return bool(cond)

    # [1] grammar legs
    g = build_grammar_w5()
    g2 = build_grammar_w5()
    ok("grammar deterministic (sha equal on rebuild)",
       g["grammar_sha256"] == g2["grammar_sha256"])
    ok(f"B family = machinery actual 72 (prereg prose 76 declared "
       f"carries as disclosure)",
       len(g["families"]["B"]) == 72)
    ok("inventory audit: 77 non-grid fns, 13 modules on disk",
       len(g["value_domains"]) == 77 and
       g["inventory_audit"]["modules_on_disk"] == 13)
    ok("axis combos = 64512 (7x8x4x2x8x3x3x2)",
       g["axis_combos"] == 64512 == AXIS_COMBOS)
    ok("yang axis frozen 2 faces",
       g["axes"]["yang"] == ["none", "first_yang"] == AXIS_YANG)
    ok("stop axis imported from tl2 (8 faces, zero re-declare)",
       g["axes"]["initial_stop"] == tl2.AXIS_STOP and len(AXIS_STOP) == 8)
    ok("gate axis imported from tl3 (3 faces, zero re-declare)",
       g["axes"]["gate"] == tl3.AXIS_GATE and len(AXIS_GATE) == 3)
    ok("vol axis imported from tl4 (3 faces, zero re-declare)",
       g["axes"]["vol"] == tl4.AXIS_VOL and len(AXIS_VOL) == 3)
    ok("seeds bound (20302000/20302500/20303000)",
       SEED_GEN == 20302000 and SEED_NULL == 20302500
       and SEED_UNC == 20303000)
    prior = {"a2fa15f4b06b3c40", "96269ebe766c3fc2", "1dd3d95792395cec",
             "cc59eab79db53436", tl4.FROZEN_SHA16}
    ok("new-syntax sha16 != W1/MASS/W2/W3/W4 faces",
       g["grammar_sha256"][:16] not in prior)
    if FROZEN_SHA16:
        ok("serialized anchor == build face (FROZEN_SHA16 pinned)",
           g["grammar_sha256"][:16] == FROZEN_SHA16
           and json.load(open(GRAMMAR_FILE, encoding="utf-8"))
           ["grammar_sha256"] == FROZEN_SHA16)
    else:
        ok("FROZEN_SHA16 unpinned (pre-serialization face; pin after "
           "`grammar`)", True)
    ok("exclusion carried on stop-gate-vol-yang-none face",
       len(g["exclusion"]["stop_gate_vol_yang_none_face"]) > 0
       and all(e["face"].endswith("stop-gate-vol-yang-none")
               for e in g["exclusion"]["stop_gate_vol_yang_none_face"]))
    ok("yang spec frozen fields present",
       all(k in YANG_SPEC for k in ("yang", "first_yang", "none",
                                    "info_set", "warmup", "engine_note")))
    ok("yang probe anchors embedded in grammar",
       g["yang_anchor"]["yang_days"] == 1751
       and g["yang_anchor"]["yang_and_bull_lower_bound"] == 962
       and g["yang_anchor"]["red_and_bear_lower_bound"] == 914)
    ok("ledger batch names frozen per prereg sec.3 literals",
       SCREEN_BATCH == "TRIAL_LAB_W5_SCREEN"
       and JUDGE_BATCH == "TRIAL_LAB_W5_JUDGE")

    # [2] synthetic yang series legs (zero warmup; strict-> law)
    rngf = np.random.default_rng([20260929, 1])
    n_synth = 80
    idx = pd.bdate_range("2024-01-02", periods=n_synth)
    o_s = pd.Series(100.0, index=idx)
    c_s = pd.Series(100.0, index=idx)
    for i in range(n_synth):
        if i % 3 == 0:            # yang: close strictly above open
            o_s.iloc[i], c_s.iloc[i] = 99.0, 101.0
        elif i % 3 == 1:          # red: close strictly below open
            o_s.iloc[i], c_s.iloc[i] = 101.0, 99.0
        else:                     # doji: close == open -> red (strict law)
            o_s.iloc[i], c_s.iloc[i] = 100.0, 100.0
    yface = {YANG_MEMBER: pd.DataFrame(
        {"open": o_s, "high": c_s + 1, "low": o_s - 1, "close": c_s,
         "volume": 1000.0, "amount": 1e5}, index=idx)}
    y1, r1, m1 = yang_state_series(yface)
    y2, r2, m2 = yang_state_series(yface)
    ok("yang == literal spec (close > open strict; doji counts red)",
       int(y1.sum()) == int((c_s > o_s).sum())
       == sum(1 for i in range(n_synth) if i % 3 == 0)
       and bool((y1 == (c_s > o_s)).all())
       and int(r1.sum()) == int((~(c_s > o_s)).sum()))
    ok("zero warmup: bar-0 onward judgeable (na_window 0)",
       m1["na_window_bars"] == 0 and m1["first_valid_bar_idx"] == 0
       and bool(y1.iloc[0] or r1.iloc[0]))
    ok("meta counts == series sums; yang+red == n_bars partition",
       m1["yang_days"] == int(y1.sum()) and m1["red_days"] == int(r1.sum())
       and m1["yang_days"] + m1["red_days"] == m1["n_bars"] == n_synth)
    ok("yang state deterministic (double-run equal)",
       bool(y1.equals(y2)) and m1 == m2)
    ok("_yang_structure_pass law: fixture meta passes; corrupted meta "
       "fails",
       _yang_structure_pass(m1)
       and not _yang_structure_pass({"na_window_bars": 5})
       and not _yang_structure_pass({"na_window_bars": 0,
                                     "first_valid_bar_idx": 0,
                                     "yang_days": 10, "red_days": 10,
                                     "n_bars": 19}))
    # causality: truncated-panel state at d == full-series state at d
    trunc = {YANG_MEMBER: yface[YANG_MEMBER].iloc[:40]}
    y_tr, _, m_tr = yang_state_series(trunc)
    ok("causality: truncated-panel state at d == full-series state at d "
       "(bar-wise zero lookahead)",
       bool(y_tr.equals(y1.iloc[:40])) and m_tr["yang_days"]
       == int(y1.iloc[:40].sum()))

    # [3] yang_zero_mask legs
    maskY = pd.DataFrame(0, index=idx, columns=["A", "B"], dtype=int)
    maskY.iloc[::2, 0] = 1
    maskY.iloc[5::3, 1] = 1
    ys_state = (y1, r1, m1)
    ok("yang=none is the identity (W4 semantic baseline)",
       yang_zero_mask(maskY, "none", ys_state).equals(maskY))
    SY = yang_zero_mask(maskY, "first_yang", ys_state)
    keep_y = y1.reindex(maskY.index).fillna(False).astype(int)
    ok("first_yang face == mask * yang-permission (exact elementwise law)",
       SY["A"].equals(maskY["A"].mul(keep_y))
       and SY["B"].equals(maskY["B"].mul(keep_y)))
    ok("yang zero deterministic (double-run byte-equal)",
       SY.equals(yang_zero_mask(maskY, "first_yang", ys_state)))
    ok("red-day signals blocked (first_yang face never holds on red "
       "days)",
       int(((SY > 0) & (keep_y == 0)).sum().sum()) == 0)
    # conservative reindex law: mask dates beyond the member index
    idx_ext = maskY.index.append(
        pd.DatetimeIndex([maskY.index[-1] + pd.Timedelta(days=3)]))
    mask_ext = maskY.reindex(idx_ext).fillna(0).astype(int)
    SY_ext = yang_zero_mask(mask_ext, "first_yang", ys_state)
    ok("member-missing mask dates -> yang-closed (conservative reindex)",
       int(SY_ext.iloc[-1].sum()) == 0)

    # [4] triple-gate intersection legs (gate AND vol AND yang)
    n_tri = 700
    tri_idx = pd.bdate_range("2022-01-02", periods=n_tri)
    tri_close = pd.Series(100.0, index=tri_idx)
    tri_open = pd.Series(100.0, index=tri_idx)
    for i in range(n_tri):
        tri_close.iloc[i] = 100.0 + (1.0 if i % 2 == 0 else -1.0)
        tri_open.iloc[i] = 100.0
    flat = pd.DataFrame({"open": tri_open, "high": tri_close + 1,
                         "low": tri_open - 1, "close": tri_close,
                         "volume": 1000.0, "amount": 1e5}, index=tri_idx)
    tri_face = {YANG_MEMBER: flat.copy()}
    # flat close -> no trend -> gate bear face mostly closed early (MA
    # warmup), calm/wild alternating; yang alternating with the close
    gs_tri = tl3.gate_state_series(tri_face)
    vs_tri = tl4.vol_state_series(tri_face)
    ys_tri = yang_state_series(tri_face)
    mask3 = pd.DataFrame(0, index=tri_idx, columns=["A"], dtype=int)
    mask3.iloc[560:640, 0] = 1
    S3 = _effective_signal_mask_w5(mask3, tri_face, "none", None,
                                   "bull", "calm", "first_yang",
                                   gs_tri, vs_tri, ys_tri)
    bull_p = gs_tri[0].reindex(tri_idx).fillna(False).astype(int)
    calm_p = vs_tri[0].reindex(tri_idx).fillna(False).astype(int)
    yang_p = ys_tri[0].reindex(tri_idx).fillna(False).astype(int)
    ok("triple gate: composed face == mask * (bull AND calm AND yang) "
       "intersection",
       bool((S3["A"] == (mask3["A"] * bull_p * calm_p * yang_p)).all()))
    S3_perm = _effective_signal_mask_w5(
        mask3, tri_face, "none", None, "bull", "calm", "first_yang",
        (vs_tri[0], vs_tri[1], {}),   # bull-face slot reads calm perm
        (ys_tri[0], ys_tri[1], {}),   # calm-face slot reads yang perm
        (bull_p, None, {}))           # first_yang slot reads bull perm
    ok("triple gate: intersection commutes (elementwise AND law)",
       bool(S3_perm["A"].equals(S3["A"])))

    # [5] Sobol draw legs
    draws1 = [c for _, c in draw_candidate_sobol_w5(g, "B", 0, 32)]
    draws2 = [c for _, c in draw_candidate_sobol_w5(g, "B", 0, 32)]
    ok("Sobol draw deterministic (32 draws byte-equal)",
       json.dumps(draws1, sort_keys=True, default=str)
       == json.dumps(draws2, sort_keys=True, default=str))
    ok("draw carries eight-tuple axis with yang face",
       all(len(c["axis"]) == 8 and c["axis"][7] in AXIS_YANG
           and c["axis"][4] in AXIS_STOP and c["axis"][5] in AXIS_GATE
           and c["axis"][6] in AXIS_VOL for c in draws1))
    dom_ok = all(
        c["sig_params"][nm] in g["value_domains"][
            f"{c['module']}.{c['fn']}"][nm]
        for c in draws1
        for nm, vs in g["value_domains"][
            f"{c['module']}.{c['fn']}"].items() if len(vs) > 1)
    ok("draw params inside frozen domains", dom_ok)
    tot = sum(1 for _ in draw_candidate_sobol_w5(g, "B", 5, 64))
    ok("B-family stream yields declared count", tot == 64)

    # [6] exclusion legs (data-driven on the real loaded rows)
    excl_rows, excl_disc = _load_exclusion_rows_w5(g)
    ok("exclusion sources disclosed (10 faces incl. w4 screen + 5 "
       "judged)",
       "w4_screen_survivors" in excl_disc
       and "w4_judge_products" in excl_disc)
    if excl_rows:
        e0 = excl_rows[0]
        c_e0 = {"module": e0["module"], "fn": e0["fn"],
                "sig_params": e0["sig_params"],
                "axis": list(e0["axis"])}
        hit = _excluded_w5(c_e0, excl_rows)
        ok("exclusion: first loaded row exact key rejected "
           "(yang=none face)",
           hit is not None)
        c_flip = dict(c_e0, axis=[*c_e0["axis"][:7], "first_yang"])
        ok("exclusion: same key yang=first_yang NOT excluded "
           "(new-syntax legal face)",
           _excluded_w5(c_flip, excl_rows) is None)
    else:
        ok("exclusion rows non-empty (grammar bands always in tree)",
           False)
    # four-face prior-wave pad law: W4 survivor explicit faces rejected
    w4_screen = (os.path.exists(tl4.SCREEN_FILE)
                 and os.path.exists(tl4.CANDIDATES_FILE))
    if w4_screen:
        scr4 = json.load(open(tl4.SCREEN_FILE, encoding="utf-8"))
        cands4 = {c["candidate_id"]: c for c in json.load(
            open(tl4.CANDIDATES_FILE, encoding="utf-8"))["candidates"]}
        if scr4.get("survivors"):
            c4 = cands4[sorted(scr4["survivors"])[0]]
            c_w4 = {"module": c4["module"], "fn": c4["fn"],
                    "sig_params": c4["sig_params"],
                    "axis": list(c4["axis"]) + ["none"]}
            ok("exclusion: W4 survivor explicit stop+gate+vol faces "
               "rejected on exact key (yang=none pad law)",
               _excluded_w5(c_w4, excl_rows) is not None)
            c_w4f = dict(c_w4, axis=[*c_w4["axis"][:7], "first_yang"])
            ok("exclusion: same W4 key yang=first_yang NOT excluded "
               "(new-syntax)",
               _excluded_w5(c_w4f, excl_rows) is None)
        else:
            ok("W4 screen survivors present for the pad-law leg",
               False)
    else:
        ok("W4 screen products absent = declared-unavailable zero rows "
           "honest (freeze-time expectation; leg vacuous-skipped)",
           True)

    # [7] effective-face composition legs (gate -> vol -> yang -> stop)
    flatA = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0,
                          "close": 100.0, "volume": 1000.0,
                          "amount": 1e5}, index=idx)
    dip = flatA.copy()
    dip.loc[idx[8], "low"] = 90.0        # pierces any p3 level on a
    # yang-open day (bar 8 even = yang; close unchanged -> gate/vol/yang
    # series untouched -> the stop bite is observable on the composed
    # face)
    # yang-member face: a CONTIGUOUS yang run bars 4-20 (close above
    # open) + alternating yang/red elsewhere, so the stop overlay can
    # ARM (mask 0->1 at bar 4, entry bar 5, p3 level 97) and the bar-8
    # low-pierce 90 bites INSIDE the armed yang-open window (an
    # alternating-only face disarms every red day and never scans far
    # enough -- the contiguous run is load-bearing for this leg)
    yang_flat = flatA.copy()
    for i in range(len(idx)):
        if 4 <= i <= 20:
            yang_flat.iloc[i, yang_flat.columns.get_loc("close")] = 100.5
        else:
            yang_flat.iloc[i, yang_flat.columns.get_loc("close")] = \
                100.5 if i % 2 == 0 else 99.5
    mask7 = pd.DataFrame(0, index=idx, columns=["A", "B"], dtype=int)
    mask7.iloc[0:60, 0] = 1            # yang-valid zone only (zero warmup)
    mask7.iloc[20:60, 1] = 1
    gs_v = tl3.gate_state_series({"A": flatA, YANG_MEMBER: flatA})
    vs_v = tl4.vol_state_series({YANG_MEMBER: flatA})
    ysv = yang_state_series({YANG_MEMBER: yang_flat})
    S_id = _effective_signal_mask_w5(mask7, {"A": dip, "B": flatA},
                                     "none", None, "none", "none", "none",
                                     gs_v, vs_v, ysv)
    ok("effective face: all-none is the identity",
       S_id.equals(mask7))
    S_yonly = _effective_signal_mask_w5(mask7, {"A": dip, "B": flatA},
                                        "none", None, "none", "none",
                                        "first_yang", gs_v, vs_v, ysv)
    keep_f = ysv[0].reindex(mask7.index).fillna(False).astype(int)
    ok("effective face: yang-only face == mask * yang-permission "
       "(exact)",
       S_yonly["A"].equals(mask7["A"].mul(keep_f)))
    S_gs = _effective_signal_mask_w5(mask7, {"A": dip, "B": flatA},
                                     "p3", None, "none", "none",
                                     "first_yang", gs_v, vs_v, ysv)
    S_gs2 = _effective_signal_mask_w5(mask7, {"A": dip, "B": flatA},
                                       "p3", None, "none", "none",
                                       "first_yang", gs_v, vs_v, ysv)
    ok("effective face: yang+stop composed, deterministic (double-run "
       "byte-equal)",
       S_gs.equals(S_gs2))
    S_w4face = tl4._effective_signal_mask_w4(
        mask7, {"A": dip, "B": flatA}, "none", None, "none", "none",
        gs_v, vs_v)
    ok("effective face: yang=none == W4 face byte-equal (semantic "
       "baseline identity law)",
       S_id.equals(S_w4face))
    S_tl2 = tl2._effective_signal_mask(mask7, {"A": dip, "B": flatA},
                                       "p3", None)
    S_w5tl2 = _effective_signal_mask_w5(mask7, {"A": dip, "B": flatA},
                                        "p3", None, "none", "none",
                                        "none", gs_v, vs_v, ysv)
    ok("effective face: gate=none+vol=none+yang=none+stop=p3 == tl2 W2 "
       "face byte-equal (parity law)",
       S_w5tl2.equals(S_tl2))
    ok("effective face: composed yang face never holds on red days "
       "(yang precedes stop arming)",
       int(((S_gs > 0) & (keep_f == 0)).sum().sum()) == 0)
    ok("effective face: composed first_yang face differs from yang-only "
       "face (stop bites inside the yang-open window)",
       not S_gs.equals(S_yonly)
       and int(((S_gs["A"] == 0) & (mask7["A"] == 1)
                 & (keep_f == 1)).sum()) > 0)

    # [8] round-robin stream consumption == per-slot sequential streams
    n_slots_a = len(g["families"]["A"])
    n_rr = 18
    streams = {s: draw_candidate_sobol_w5(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)
               for s in range(n_slots_a)}
    rr = [next(streams[i % n_slots_a]) for i in range(n_rr)]
    seq = {s: [c for _, c in draw_candidate_sobol_w5(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)]
           for s in range(n_slots_a)}
    reassembled = [seq[i % n_slots_a][i // n_slots_a] for i in range(n_rr)]
    ok("round-robin consumption == per-slot sequential (identity)",
       json.dumps([c for _, c in rr], sort_keys=True, default=str)
       == json.dumps(reassembled, sort_keys=True, default=str))

    # [9] registered-six naive face via tl2 import (zero-variance ok)
    tl1.GRAMMAR = g
    frames2 = tl1._synth_prices(n_days=120, n_syms=3, seed=17)
    P2 = tl1.build_panels(frames2)
    reg = tl2._registered_naive_series(P2, g)
    ok("registered-six naive series built (6 members, panel-length)",
       len(reg) == 6 and all(len(v) == len(P2["close"].index)
                             for v in reg.values()))

    # [10] engine-face legs: parity + determinism + yang bites (null path)
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled 510300 path: alternating yang/red (close above/below
    # open) + flat-ish vol face; engine faces below ride its states
    alt_o = pd.Series(100.0, index=frames3["510300"].index
                      if "510300" in frames3 else
                      frames3[list(frames3)[0]].index)
    alt_c = alt_o.copy()
    for i in range(len(alt_c)):
        alt_c.iloc[i] = 100.0 + (0.7 if i % 2 == 0 else -0.7)
        alt_o.iloc[i] = 100.0
    alt_df = pd.DataFrame({"open": alt_o, "high": alt_c + 0.2,
                           "low": alt_o - 0.2, "close": alt_c,
                           "volume": 1000.0, "amount": 1e5},
                          index=alt_c.index)
    frames3[YANG_MEMBER] = alt_df
    P3 = tl1.build_panels(frames3)
    st3 = pd.Series("GREEN", index=P3["close"].index)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = tl4.vol_state_series(frames3)
    ys3 = yang_state_series(frames3)
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none", "none", "none", "none"]}
    eq_w5, *_ = run_candidate_curve_w5(base, None, frames3, P3, st3,
                                       gate_state=gs3, vol_state=vs3,
                                       yang_state=ys3)
    eq_tl1 = tl1.run_candidate_curve(
        dict(base, axis=base["axis"][:4]), None, frames3, P3, st3)[0]
    ok("engine face: yang=none+vol=none+gate=none+stop=none identical "
       "to tl1 face (byte-equal)",
       list(eq_w5.values) == list(eq_tl1.values))
    stop_c = dict(base, axis=[*base["axis"][:4], "p3", "none", "none",
                              "none"])
    eq_s, tr_s, m_s, _, _, fired_s, gz_s, vz_s, yz_s = \
        run_candidate_curve_w5(stop_c, None, frames3, P3, st3,
                               gate_state=gs3, vol_state=vs3,
                               yang_state=ys3)
    eq_s2 = tl2.run_candidate_curve_w2(
        dict(stop_c, axis=stop_c["axis"][:5]), None, frames3, P3, st3)[0]
    ok("engine face: yang=none+vol=none+gate=none+stop=p3 identical to "
       "tl2 W2 face (byte-equal parity law)",
       list(eq_s.values) == list(eq_s2.values) and fired_s >= 0)
    gate_c = dict(base, axis=[*base["axis"][:5], "bull", "none", "none"])
    eq_w5g, *_ = run_candidate_curve_w5(gate_c, None, frames3, P3, st3,
                                        gate_state=gs3, vol_state=vs3,
                                        yang_state=ys3)
    eq_w3g = tl3.run_candidate_curve_w3(
        dict(gate_c, axis=gate_c["axis"][:6]), None, frames3, P3, st3,
        gate_state=gs3)[0]
    ok("engine face: yang=none+vol=none (gate=bull) identical to tl3 W3 "
       "face (byte-equal semantic-baseline identity law)",
       list(eq_w5g.values) == list(eq_w3g.values))
    vol_c = dict(base, axis=[*base["axis"][:6], "calm", "none"])
    eq_w5v, *_ = run_candidate_curve_w5(vol_c, None, frames3, P3, st3,
                                        gate_state=gs3, vol_state=vs3,
                                        yang_state=ys3)
    eq_w4v = tl4.run_candidate_curve_w4(
        dict(vol_c, axis=vol_c["axis"][:7]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3)[0]
    ok("engine face: yang=none (vol=calm) identical to tl4 W4 face "
       "(byte-equal semantic-baseline identity law)",
       list(eq_w5v.values) == list(eq_w4v.values))
    eq_s3, *_ = run_candidate_curve_w5(stop_c, None, frames3, P3, st3,
                                        gate_state=gs3, vol_state=vs3,
                                        yang_state=ys3)
    ok("engine face: deterministic (double-run byte-equal)",
       list(eq_s3.values) == list(eq_s.values))
    # yang bites at the engine face: same random null signals,
    # yang=first_yang vs yang=none -> different curves
    rng_n = np.random.default_rng([4242, 1])
    mat_n = rng_n.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    eq_n5, *_ = run_candidate_curve_w5(
        {"module": "null", "fn": "random_signal",
         "sig_params": {"p_on": tl1.NULL_P_REGIMES[0]},
         "axis": ["none", "template_default", "equal_weight",
                  "daily_signal", "none", "none", "none", "first_yang"],
         "candidate_id": "ST-NULL-0", "family": "NULL"},
        None, frames3, P3, st3, rng_matrix=mat_n,
        p_on=tl1.NULL_P_REGIMES[0], gate_state=gs3, vol_state=vs3,
        yang_state=ys3)
    rng_n2 = np.random.default_rng([4242, 1])
    mat_n2 = rng_n2.random((len(P3["close"].index),
                            len(P3["close"].columns)))
    eq_n5b, *_ = run_candidate_curve_w5(
        {"module": "null", "fn": "random_signal",
         "sig_params": {"p_on": tl1.NULL_P_REGIMES[0]},
         "axis": ["none", "template_default", "equal_weight",
                  "daily_signal", "none", "none", "none", "first_yang"],
         "candidate_id": "ST-NULL-0", "family": "NULL"},
        None, frames3, P3, st3, rng_matrix=mat_n2,
        p_on=tl1.NULL_P_REGIMES[0], gate_state=gs3, vol_state=vs3,
        yang_state=ys3)
    eq_none_face, *_ = run_candidate_curve_w5(
        {"module": "null", "fn": "random_signal",
         "sig_params": {"p_on": tl1.NULL_P_REGIMES[0]},
         "axis": ["none", "template_default", "equal_weight",
                  "daily_signal", "none", "none", "none", "none"],
         "candidate_id": "ST-NULL-0", "family": "NULL"},
        None, frames3, P3, st3, rng_matrix=mat_n,
        p_on=tl1.NULL_P_REGIMES[0], gate_state=gs3, vol_state=vs3,
        yang_state=ys3)
    ok("engine face: yang=first_yang bites (differs from yang=none on "
       "the same null signals; deterministic double-run)",
       list(eq_n5.values) == list(eq_n5b.values)
       and list(eq_n5.values) != list(eq_none_face.values))

    # [11] null draw legs (eight-tuple)
    p1, ax1, rg1 = _null_axis_draw_w5(0)
    p2, ax2, rg2 = _null_axis_draw_w5(0)
    ok("null draw deterministic (p_on + eight-tuple axis + rng state)",
       p1 == p2 and ax1 == ax2)
    ok("null axis = eight-tuple with stop+gate+vol+yang faces in "
       "frozen grids",
       len(ax1) == 8 and ax1[4] in AXIS_STOP and ax1[5] in AXIS_GATE
       and ax1[6] in AXIS_VOL and ax1[7] in AXIS_YANG)
    p3d, ax3d, _ = _null_axis_draw_w5(1)
    ok("null draws differ across cells (stream law)",
       (p1, ax1) != (p3d, ax3d))

    # [12] B7b contract legs (r116 law)
    ok("B7b contract: screen-csv consumer keys subset of constructor "
       "keys",
       set(csv_cols_screen_w5) <= set(csv_cols_screen_w5)
       and {"yang_face", "yang_zeroed"} <= set(csv_cols_screen_w5))
    ok("finalize math import: W5 alias == tl2._finalize_math",
       _finalize_math is tl2._finalize_math)
    nr = [0.31, 0.32, 0.33, 0.40, 0.41, 0.55, 0.57, 0.60]
    p95c = float(np.percentile(nr, 95))
    cand_rows_c = [{"candidate_id": f"C{i}", "beat6m_rate": v,
                    "survives_screen": bool(v > p95c)}
                   for i, v in enumerate([0.30, 0.35, 0.50, 0.58,
                                          0.615])]
    p95x, survx = _finalize_math(
        cand_rows_c,
        [{"candidate_id": f"N{i}", "beat6m_rate": v,
          "survives_screen": False} for i, v in enumerate(nr)])
    ok("finalize math: p95 == numpy percentile of null rates",
       abs(p95x - p95c) < 1e-12)
    ok("finalize math: survivors = rate > p95 (strict, flag column set)",
       survx == [r["candidate_id"] for r in cand_rows_c
                 if r["beat6m_rate"] > p95x]
       and all(bool(r["survives_screen"])
               == (r["beat6m_rate"] > p95x) for r in cand_rows_c))

    # [13] dual nulls legs (W5 seed binding)
    rets13 = np.random.default_rng([13, 1]).normal(0.0005, 0.01, 200)
    dn1 = _dual_nulls_w5(rets13, 0)
    dn2 = _dual_nulls_w5(rets13, 0)
    ok("dual nulls w5 deterministic (seed [20303000, cell])",
       json.dumps(dn1, sort_keys=True) == json.dumps(dn2, sort_keys=True))
    dn0 = _dual_nulls_w5(np.zeros(30), 0)
    ok("dual nulls w5 degenerate zero face (CI [0,0], p=1)",
       dn0["bootstrap_ci"][0] == 0.0 and dn0["bootstrap_ci"][1] == 0.0
       and abs(dn0["signflip_p"] - 1.0) < 1e-9)
    dn_w4mirror = tl4._dual_nulls_w4(rets13, 0, seed=SEED_UNC)
    ok("dual nulls w5 math mirror == tl4 face at the same seed",
       json.dumps(dn1, sort_keys=True)
       == json.dumps(dn_w4mirror, sort_keys=True))
    dn_w4def = tl4._dual_nulls_w4(rets13, 0)
    ok("dual nulls w5 seed law: W5 face != W4 default-seed face "
       "(seed constants differ)",
       json.dumps(dn1, sort_keys=True)
       != json.dumps(dn_w4def, sort_keys=True))

    # [14] judge-cell legs (synthetic dual-leg state)
    jstate = {"starts": {"L": {"6m": [10, 60, 110], "12m": [10, 60],
                               "24m": [10]},
                         "D": {"6m": [10, 60, 110], "12m": [10, 60],
                               "24m": [10]}},
              "passive": {"L": {"6m": {"10": 0.01, "60": 0.02,
                                        "110": 0.0},
                                "12m": {"10": 0.01, "60": 0.02},
                                "24m": {"10": 0.01}},
                          "D": {"6m": {"10": 0.01, "60": 0.02,
                                       "110": 0.0},
                                "12m": {"10": 0.01, "60": 0.02},
                                "24m": {"10": 0.01}}}}
    jcell_cand = {"module": "volatility", "fn": "low_vol_long",
                  "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
                  "axis": ["none", "time_stop_5d", "equal_weight",
                           "daily_signal", "p3", "bull", "calm",
                           "first_yang"],
                  "candidate_id": "ST-J-0000", "family": "B"}
    tl1.GRAMMAR = g
    jout = None
    jout2 = None
    for leg in ("L", "D"):
        fr_l = tl1._synth_prices(n_days=640, n_syms=3, seed=41 if leg
                                 == "L" else 43)
        fr_l[YANG_MEMBER] = alt_df.copy()
        P_l = tl1.build_panels(fr_l)
        globals()["_jstate_cache"] = globals().get("_jstate_cache", {})
        globals()["_jstate_cache"][leg] = (fr_l, P_l)
    fr_L, P_L = globals()["_jstate_cache"]["L"]
    fr_D, P_D = globals()["_jstate_cache"]["D"]
    stj = {"prices_L": fr_L, "P_L": P_L, "idx_L": P_L["close"].index,
           "atr20_L": tl2.atr20_series(fr_L),
           "fundamental_ok_L": None,
           "gate_state_L": tl3.gate_state_series(fr_L),
           "gate_meta_L": tl3.gate_state_series(fr_L)[2],
           "vol_state_L": tl4.vol_state_series(fr_L),
           "vol_meta_L": tl4.vol_state_series(fr_L)[2],
           "yang_state_L": yang_state_series(fr_L),
           "yang_meta_L": yang_state_series(fr_L)[2],
           "prices_D": fr_D, "P_D": P_D, "idx_D": P_D["close"].index,
           "atr20_D": tl2.atr20_series(fr_D),
           "fundamental_ok_D": None,
           "gate_state_D": tl3.gate_state_series(fr_D),
           "vol_state_D": tl4.vol_state_series(fr_D),
           "yang_state_D": yang_state_series(fr_D),
           "starts": jstate["starts"], "passive": jstate["passive"],
           "states": pd.Series("GREEN", index=P_L["close"].index),
           "grammar": g}
    cellj = {"cell_id": "JUDGE|ST-J-0000", "i": 0, "cand": jcell_cand,
             "template": None}
    tl1._ST = stj
    jout = _judge_cell_w5(cellj)
    jout2 = _judge_cell_w5(cellj)
    ok("judge cell: legs L/D present + determinism (double-run equal)",
       set(jout["legs"]) == {"L", "D"}
       and json.dumps(jout, sort_keys=True, default=float)
       == json.dumps(jout2, sort_keys=True, default=float))
    ok("judge cell: window-grid beat + x2 faces per leg + gate+vol+yang "
       "zeroed columns wired",
       all(set(jout["legs"][lg]["beat"]) == set(tl1.WINDOWS)
           and set(jout["legs"][lg]["beat_x2"]) == set(tl1.WINDOWS)
           and "yang_zeroed" in jout["legs"][lg]
           and "yang_zeroed_x2" in jout["legs"][lg]
           for lg in ("L", "D")))
    ok("judge cell: regime segments partition the complete windows "
       "(bear+bull+chop+na == per-window n sum)",
       all(sum(jout["legs"][lg]["regime_start_windows"][s]
               for s in ("bear", "bull", "chop", "na"))
           == sum(jout["legs"][lg]["beat"][w]["n"]
                  for w in tl1.WINDOWS)
           for lg in ("L", "D")))
    ok("judge cell: dual nulls seed law [20303000, i]",
       jout["dual_nulls"] == _dual_nulls_w5(
           np.asarray(jout["legL_daily_returns"]), 0))
    ok("judge cell: n_eff == bear+bull+chop sum across BOTH legs; "
       "faces wired",
       jout["n_eff_start_windows"]
       == sum(jout["legs"][lg]["regime_start_windows"][s]
              for lg in ("L", "D") for s in ("bear", "bull", "chop"))
       and jout["yang_face"] == "first_yang"
       and jout["stop_face"] == "p3" and jout["gate_face"] == "bull"
       and jout["vol_face"] == "calm")
    ok("judge cell: descriptive + crisis + flip columns wired (yang "
       "face = zero-warmup daily binary, per-leg yang_zeroed is its "
       "column)",
       "descriptive" in jout and "crisis_days_gt8pct" in jout
       and "gate_flip_days_legL" in jout and "vol_flip_days_legL" in jout
       and jout["gate_flip_days_legL"] is not None
       and jout["vol_flip_days_legL"] is not None)
    ok("judge cell: stop disclosure face wired (p3+bull+calm+first_yang "
       "structurally complete)",
       jout["stop_disclosure"]["stop_face"] == "p3")
    cell_none = {"cell_id": "JUDGE|ST-J-0001", "i": 1,
                 "cand": dict(jcell_cand,
                              axis=["none", "template_default",
                                    "equal_weight", "daily_signal",
                                    "none", "none", "none", "none"]),
                 "template": None}
    jn = _judge_cell_w5(cell_none)
    ok("judge cell: stop=none disclosure = zero-face + flips null "
       "(none faces)",
       jn["stop_disclosure"]["stop_face"] == "none"
       and jn["gate_flip_days_legL"] is None
       and jn["vol_flip_days_legL"] is None)
    ok("B7b contract: judge strip face = daily-returns only; finalize "
       "consumes cells without the raw series",
       "legL_daily_returns" in jout
       and "legL_daily_returns" not in {
           k: v for k, v in jout.items()
           if k != "legL_daily_returns"})

    # [15] grammar serialization round-trip (sha stable; r297 double-run
    # byte-identity law on the serialized face)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        gp = os.path.join(td, "w5_grammar.json")
        with open(gp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(g, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(gp, "rb") as fh:
            b1 = fh.read()
        with open(gp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(build_grammar_w5(), fh, ensure_ascii=False,
                      indent=1, sort_keys=True)
            fh.write("\n")
        with open(gp, "rb") as fh:
            b2 = fh.read()
        ok("grammar serialization round-trip (sha + bytes stable)",
           b1 == b2 and json.loads(b1)["grammar_sha256"]
           == g["grammar_sha256"])

    print(f"selftest: {ok_n - fails[0]}/{ok_n} PASS, {fails[0]} FAIL")
    if fails[0]:
        return 1
    print("SELFTEST ALL PASS")
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
    # r141 crash-lane law: explicit per-command forwarding; no zero-arg
    # dict dispatch; subcommands not yet built (intake -- physical dep:
    # judge products) are NOT registered here (half-built dispatch =
    # forbidden face)
    if a.cmd == "screen":
        return cmd_screen(a.shard, a.shards, a.workers)
    if a.cmd == "judge":
        return cmd_judge(a.shard, a.shards, a.workers)
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "grammar":
        return cmd_grammar()
    if a.cmd == "generate":
        return cmd_generate()
    if a.cmd == "screen-prep":
        return cmd_screen_prep()
    if a.cmd == "screen-finalize":
        return cmd_screen_finalize()
    if a.cmd == "judge-prep":
        return cmd_judge_prep()
    if a.cmd == "judge-finalize":
        return cmd_judge_finalize()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
