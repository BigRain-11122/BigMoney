# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W4 runner -- T-98 mass-candidate trial wave-4 (5000-deep,
volatility-gate dual-gate superposition wave).

Prereg FROZEN (r396): research/TRIAL_LABOR_W4_PREREG.md -- generate
grammar + funnel rules + judgment lines all frozen; post-run only
sec.7/8 backfill.

Import-face law (prereg sec.6): enumeration/loading/anchor/envelope
primitives are IMPORTED from trial_labor_w1 (tl1); the initial-stop
overlay layer is IMPORTED from trial_labor_w2 (tl2); the regime-gate
overlay layer + dual-gate machinery + declared MASS translation are
IMPORTED from trial_labor_w3 (tl3); the Sobol sample_draws pattern
follows mass_trial_w1 (paradigm import); strategies/ factory +
engine/backtester imported, never rewritten; engine/exit_rules.py ZERO
touch (gate/vol overlays AND stop overlay are GRAMMAR layers).

Engineering mapping disclosures (pre-run, zero cells burned):

  VOL overlay (prereg sec.3 face a; E1-mapping grammar-layer primitive):
  VOL state = signal-day-d info set on member 510300: ret(d)=close(d)/
  close(d-1)-1; vol20(d)=ret rolling 20 sample std (ddof=1,
  min_periods=20, inclusive of d); med500(d)=vol20 rolling 500-obs
  median (min_periods=500, all <=d info).  calm = vol20<=med500 permits
  entry; wild = vol20>med500 permits entry; vol-closed window (first
  519 bars, med500 NaN) -> gate-closed on BOTH calm/wild faces
  (conservative, disclosed).  Gate acts on ENTRY PERMITTANCE only
  (effective signal zeroed, MSG-0440 E1-mapping primitive; the engine-
  native signal-off exit semantics are the SAME primitive every
  template/cell uses when its own signal turns off -- no exit-rule
  change).  vol=none = W3 semantic baseline (identity).  VOL face !=
  GATE face (probe r396: 2014-12-31 wild AND bull coexist -- non-
  isomorphism fact); dual gate = the intersection of two independent
  permission series.  Composition order frozen everywhere (dedup face
  + engine face): signal -> filter -> timing -> GATE -> VOL ->
  initial-stop (stop arms only after BOTH entry gates -- a vol-blocked
  signal never arms a stop).

  G-VOL anchor law (prereg sec.2 probe facts, fail-closed): on the
  core48/leg-L face (data/daily/sh510300.csv, 3,483 bars 2012-05-28 ->
  2026-09-22 cutoff): med500 first valid bar-idx == 519 (2014-07-17),
  open-state split calm 1,523 / wild 1,441.  Structural law on every
  panel face: na_window == 519 bars + first_valid_bar_idx == 519 +
  calm+wild+na == n_bars (series-structure invariants); probe anchors
  {1523, 1441} asserted only on the raw full-history face where the
  probe ran (data/daily/sh510300.csv, r396 basis); the W1-floored
  load_core/leg-L pool faces carry only the structural invariants --
  their calm/wild counts differ by construction (r381 live refusal
  root cause; fix = raw-face loader, MSG-20260928-1215).

  Exclusion law (prereg sec.1, SEVEN sources, exact already-judged key,
  vol=none face only): W4 cell key=(template, params, axis_config,
  initial_stop, gate, vol); prior-wave keys lacking the vol axis are
  vol=none-completed (semantic-identity match); vol in {calm, wild}
  faces = new-syntax legal cells (never excluded).  Sources: frozen
  grammar bands (stop-gate-vol-none pad) + w1_screen 149 + w2_screen
  404 + MASS screen 166 (declared conservative translation, tl3 import)
  + w3_screen 513 (NEW vs W3) + judged products re-declare window
  (w1_judge / MASS judged / w2_judge / w3_judge -- four sources,
  generate-time real-read, absent = declared-unavailable zero rows).

Slice plan (W3 r392/r395/r370 precedent; this commit = slice-1 + 1b):
  - slice-1 (this round): build_grammar_w4 (tl1 grammar extended with
    stop axis (tl2) + gate axis (tl3) + the NEW vol axis -> 32,256 axis
    combos, new grammar sha16 != W1 a2fa15f4b06b3c40 != MASS
    96269ebe766c3fc2 != W2 1dd3d95792395cec != W3 cc59eab79db53436)
    + vol overlay layer + full funnel command set (generate/screen/
    judge trios) + selftest (hermetic: vol causality / NaN window /
    vol=none==W3 identity / dual-gate intersection legs);
  - slice-1b (this round): pool entry TRIAL-LABOR-W4-GENERATE (CPU
    pool face, lane_owner=null; generate/screen lawful NOW per MSG-
    20260928-0930 sec.2 -- judge face queued behind the W2/W3-JUDGE +
    RAM r354 sequencing gate per prereg sec.0);
  - NEXT slices (physical deps, separate commits with MSG declarations
    per W2 r366/W3 precedent): intake (judge products required).
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
import trial_labor_w3 as tl3  # regime-gate overlay + dual-gate machinery
from science_gates import (CostPatch, SEED_REGISTRY,  # noqa: E402
                           finalize_already_landed)  # pit-95 guard

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W4"
PREREG = "research/TRIAL_LABOR_W4_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w4_gen"]        # 20289500
SEED_NULL = SEED_REGISTRY["trial_labor_w4_scrnull"]   # 20290000
SEED_UNC = SEED_REGISTRY["trial_labor_w4_unc"]        # 20290500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (72-fn machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; burned by the
                   # screen subcommand, frozen here)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w4")
GRAMMAR_FILE = os.path.join(RES_DIR, "w4_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w4_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
FROZEN_SHA16 = "d498e9343ee57460"   # slice-1 serialized face (this round)
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
SCREEN_FILE = os.path.join(RES_DIR, "w4_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w4_screen_cells.csv")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
JUDGE_FILE = os.path.join(RES_DIR, "w4_judge.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W4_SCREEN"   # prereg sec.3 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W4_JUDGE"     # prereg sec.3 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)

# initial-stop axis: imported from tl2 (frozen levels, zero re-declare)
AXIS_STOP = tl2.AXIS_STOP
STOP_FORMULA = tl2.STOP_FORMULA
STOP_FILL_MAPPING = tl2.STOP_FILL_MAPPING

# regime entry-gate axis: imported from tl3 (frozen definition)
AXIS_GATE = tl3.AXIS_GATE
GATE_MEMBER = tl3.GATE_MEMBER
GATE_SPEC = tl3.GATE_SPEC

# volatility entry-gate axis (prereg sec.3 face a; NEW W4 frozen layer)
AXIS_VOL = ["none", "calm", "wild"]
AXIS_COMBOS = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
               * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING)
               * len(AXIS_STOP) * len(AXIS_GATE) * len(AXIS_VOL))
VOL_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
VOL_SPEC = {
    "member": VOL_MEMBER,
    "ret": "close(d)/close(d-1)-1",
    "vol20_window": 20, "vol20_min": 20, "vol20_ddof": 1,
    "med500_window": 500, "med500_min": 500,
    "vol20": "ret rolling 20 sample std (ddof=1, min_periods=20, incl d)",
    "med500": "vol20 rolling 500-obs median (min_periods=500, all <=d)",
    "calm": "vol20 <= med500 permits entry (low-vol regime face)",
    "wild": "vol20 > med500 permits entry (high-vol regime face)",
    "none": "no gate (W3 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as the signal, zero lookahead)",
    "nan_window": "first 519 bars med500=NaN -> vol-closed on BOTH "
                  "calm/wild faces (conservative; panel-level na-window "
                  "count disclosed)",
    "overlay": "vol-closed signal day -> effective signal zeroed "
               "(grammar layer, MSG-0440 E1-mapping primitive; engine/"
               "exit_rules.py ZERO touch; engine-native signal-off exit "
               "semantics shared by every template/cell)",
    "non_isomorphism": "VOL face != GATE face (probe r396: 2014-12-31 "
                       "wild AND bull coexist)",
    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "
                         "initial-stop (frozen identically on the dedup "
                         "face and the engine face; stop arms only after "
                         "BOTH entry gates)",
}

# G-VOL probe anchors (prereg sec.2 frozen facts, fail-closed on the
# raw full-history face where the probe ran: data/daily/sh510300.csv)
VOL_ANCHOR_FIRST_VALID_BAR = 519
VOL_ANCHOR_CALM_DAYS = 1523
VOL_ANCHOR_WILD_DAYS = 1441

MASS_SCREEN_CKPT = tl3.MASS_SCREEN_CKPT
MASS_JUDGE_FILE = tl3.MASS_JUDGE_FILE
W1_JUDGE_FILE = tl3.W1_JUDGE_FILE
W2_JUDGE_FILE = tl3.W2_JUDGE_FILE
W3_JUDGE_FILE = os.path.join(tl3.RES_DIR, "w3_judge.json")

MASS_TRANSLATION_NOTE = (
    "declared conservative exact-key translation imported verbatim from "
    "tl3 (W3 law); W4 pads vol=none on the translated 6-tuple axis")


# ------------------------------------------------------------ grammar (slice-1)
def _grammar_sha16(grammar: dict) -> str:
    return tl3._grammar_sha16(grammar)


def build_grammar_w4():
    """tl1 grammar extended with the stop axis (tl2 import) + the regime
    gate axis (tl3 import) + the NEW vol axis + W4 seeds/counts (frozen
    face).

    Exclusion law (prereg sec.1): exact already-judged cells are excluded
    on the vol=none face only; all prior-wave lineage keys are vol=none
    completed (W1 4-tuple + stop/gate/vol none; W2 5-tuple + gate/vol
    none; W3 6-tuple + vol none; MASS via the declared translation);
    vol=calm/wild faces = new-syntax legal cells (never excluded).
    """
    g = tl1.build_grammar()          # frozen W1 machinery: inventory+domains
    excl = []
    for band in ("registered_default_axis", "negative_default_axis"):
        for e in g["exclusion"][band]:
            excl.append({**e, "axis": list(e["axis"])
                         + ["none", "none", "none"],
                         "face": f"{band}:stop-gate-vol-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w4-vol-gate-extended",
        "seeds": {"trial_labor_w4_gen": SEED_GEN,
                  "trial_labor_w4_scrnull": SEED_NULL,
                  "trial_labor_w4_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20289500+family_idx, scramble) "
                                "param box + default_rng([20289500+family_"
                                "idx, 7919]) seven-tuple axis stream "
                                "R/X/S/T/STOP/GATE/VOL (prereg s.3; A idx "
                                "0-5, B idx 6+slot)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {"filters": tl1.AXIS_FILTERS, "exits": tl1.AXIS_EXITS,
                 "sizing": tl1.AXIS_SIZING, "timing": tl1.AXIS_TIMING,
                 "initial_stop": AXIS_STOP, "gate": AXIS_GATE,
                 "vol": AXIS_VOL},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": STOP_FORMULA,
        "stop_fill_mapping": STOP_FILL_MAPPING,
        "gate_spec": GATE_SPEC,
        "vol_spec": VOL_SPEC,
        "vol_anchor": {"first_valid_bar": VOL_ANCHOR_FIRST_VALID_BAR,
                       "calm_days": VOL_ANCHOR_CALM_DAYS,
                       "wild_days": VOL_ANCHOR_WILD_DAYS,
                       "note": "probe r396 core48/leg-L face "
                               "(results/_r396bma_volgate_probe.py)"},
        "families": g["families"], "value_domains": g["value_domains"],
        "faces": g["faces"],
        "exclusion": {"stop_gate_vol_none_face": excl,
                      "sources": list(g["exclusion"]["sources"])
                      + ["w1_screen.json survivors (generate-time)",
                         "w2_screen.json survivors (generate-time)",
                         "MASS screen survivors (generate-time, declared "
                         "translation)",
                         "w3_screen.json survivors (generate-time)",
                         "w1_judge / MASS judged / w2_judge / w3_judge "
                         "products (generate-time real-read re-declare "
                         "window)"],
                      "note": "exclusion face = vol=none only; prior-wave "
                              "keys vol=none-completed (semantic identity "
                              "match); vol=calm/wild = new-syntax legal "
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
                          "MSG-0440 / W3 selftest disclosures carry over "
                          "verbatim; prereg 4,500/76=59.2 prose average "
                          "reads as 4,500/72=62.5 on the machinery face",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------ vol overlay layer
def vol_state_series(prices: dict):
    """Frozen VOL spec (prereg sec.2/3): member 510300 signal-day info
    set -- ret -> vol20 (rolling 20, ddof=1, min_periods=20) vs med500
    (rolling 500-obs median of vol20, min_periods=500).

    Returns (calm_perm, wild_perm, meta): boolean Series on the member's
    own date index + panel-level flip counts + structural invariants.
    vol-closed NaN window (first 519 bars) -> BOTH faces gate-closed
    (conservative).  Deterministic pure function of the (cutoff-
    truncated) panel."""
    close = prices[VOL_MEMBER]["close"].sort_index()
    ret = close / close.shift(1) - 1.0
    vol20 = ret.rolling(VOL_SPEC["vol20_window"],
                        min_periods=VOL_SPEC["vol20_min"]).std(
                            ddof=VOL_SPEC["vol20_ddof"])
    med500 = vol20.rolling(VOL_SPEC["med500_window"],
                           min_periods=VOL_SPEC["med500_min"]).median()
    ok = vol20.notna() & med500.notna()
    calm = ok & (vol20 <= med500)
    wild = ok & (vol20 > med500)
    pos = int(ok.values.nonzero()[0][0]) if ok.any() else None
    meta = {"n_bars": int(len(close)),
            "na_window_bars": int((~ok).sum()),
            "first_valid_bar_idx": pos,
            "first_valid": (str(close.index[pos].date())
                            if pos is not None else None),
            "calm_days": int(calm.sum()), "wild_days": int(wild.sum()),
            "flips_calm_face": int((calm.values[1:]
                                    != calm.values[:-1]).sum()),
            "flips_wild_face": int((wild.values[1:]
                                    != wild.values[:-1]).sum())}
    return calm, wild, meta


def _vol_face_full():
    """Frozen sec.2 VOL-series face (r396 probe basis verbatim): the
    git-tracked raw full-history member file data/daily/sh510300.csv,
    truncated at the evidence cutoff.  NOT the W1-floored load_core
    pool face (2020-01-02 start): med500 needs the full 2012 history
    so gate states exist for every trial signal day.  Returns the
    member prices dict, or None when absent / tail != cutoff."""
    path = os.path.join("data", "daily", f"sh{VOL_MEMBER}.csv")
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip() for c in df.columns]
        close = df["close"].astype(float)
        close.index = pd.to_datetime(df["date"])
        close = close.sort_index()
        close = close[close.index <= pd.Timestamp(CUTOFF)]
        if not len(close) or str(close.index[-1].date()) != CUTOFF:
            return None
        return {VOL_MEMBER: pd.DataFrame({"close": close})}
    except Exception:
        return None


def _vol_state_full():
    """Canonical full-face vol_state with the frozen probe anchors
    asserted (prereg sec.2 G-VOL fail-closed).  Returns (vol_state,
    err); err is a one-line honest refusal reason when not None."""
    face = _vol_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{VOL_MEMBER}.csv "
                      f"absent or truncated tail != cutoff {CUTOFF}")
    vs = vol_state_series(face)
    if not _vol_anchor_pass(vs[2]):
        return None, (f"G-VOL full-face anchors {vs[2]} "
                      "!= probe {519, 1523, 1441}")
    return vs, None


def vol_zero_mask(mask: pd.DataFrame, vol_key: str, vol_state):
    """Grammar-layer volatility entry gate (prereg sec.3 face a;
    E1-mapping primitive): vol-closed signal days -> effective signal
    zeroed (entry blocked; engine-native signal-off exit semantics --
    the same primitive every cell uses when its own signal turns off;
    zero engine touch).  vol=none = W3 semantic baseline (identity).
    Member dates missing from the mask index -> vol-closed
    (conservative reindex law, tl3 gate_zero_mask caliber)."""
    if vol_key == "none":
        return mask
    calm, wild, _ = vol_state
    perm = calm if vol_key == "calm" else wild
    keep = perm.reindex(mask.index).fillna(False).astype(int)
    return mask.mul(keep, axis=0)


def _vol_structure_pass(vol_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    the med500 window needs exactly 519 bars regardless of history
    depth; calm+wild+na partitions the bar count."""
    if not isinstance(vol_meta, dict):
        return False
    return (vol_meta.get("na_window_bars") == VOL_ANCHOR_FIRST_VALID_BAR
            and vol_meta.get("first_valid_bar_idx")
            == VOL_ANCHOR_FIRST_VALID_BAR
            and vol_meta.get("calm_days", -1) + vol_meta.get("wild_days", -1)
            + vol_meta.get("na_window_bars", -1) == vol_meta.get("n_bars"))


def _vol_anchor_pass(vol_meta) -> bool:
    """Probe anchors (prereg sec.2 G-VOL): core48/leg-L face only --
    first_valid 519 + calm 1,523 / wild 1,441 (r396 probe facts)."""
    return (_vol_structure_pass(vol_meta)
            and vol_meta.get("calm_days") == VOL_ANCHOR_CALM_DAYS
            and vol_meta.get("wild_days") == VOL_ANCHOR_WILD_DAYS)


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w4(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + seven-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL.  Deterministic, zero band use."""
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
                  rng.integers(0, len(AXIS_VOL), n_draws)))
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
        r_, x_, s_, t_, st_, gt_, vt_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           AXIS_STOP[st_], AXIS_GATE[gt_], AXIS_VOL[vt_]],
                  "family": family}


# ---------------------------------------------------- exclusion (seven sources)
def _load_exclusion_rows_w4(grammar):
    """Seven-source exclusion (prereg sec.1), all real-read at generate
    time.  All prior-wave keys are padded to the W4 seven-tuple with
    vol=none (semantic-identity completion law).  Sources 1 = frozen
    serialized grammar stop-gate-vol-none face; 2 = W1 screen survivors
    (implicit stop/gate/vol=none); 3 = W2 screen survivors (explicit
    stop face + implicit gate/vol=none); 4 = MASS screen survivors via
    the declared tl3 translation + vol=none; 5 = W3 screen survivors
    (explicit stop/gate faces + implicit vol=none -- NEW vs W3);
    6-9 = judged products (w1_judge / MASS judged / w2_judge /
    w3_judge) -- generate-time real-read re-declare window
    (declared-unavailable -> zero rows, no fabrication).
    """
    rows = list(grammar["exclusion"]["stop_gate_vol_none_face"])
    disc = {"grammar_stop_gate_vol_none_rows": len(rows)}

    def _screen_survivors(scr_path, cand_path, gate_vol_pad, tag):
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
                         "axis": list(c["axis"]) + gate_vol_pad,
                         "face": f"{tag}:stop-gate-vol-none",
                         "candidate_id": cid})
            n += 1
        return n

    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none", "none"], "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none", "none"], "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"], "w3_screen_survivor")

    # MASS screen survivors: declared tl3 translation + vol=none pad
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
                tr["axis"] = list(tr["axis"]) + ["none"]
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
    # sec.1/sec.9); absent -> declared-unavailable zero rows (expected:
    # all four judge batches pool-waiting at freeze time)
    def _judged_source(jpath, cand_path, gate_vol_pad, tag, mass=False):
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
                tr["axis"] = list(tr["axis"]) + ["none"]
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + gate_vol_pad,
                             "face": f"{tag}:stop-gate-vol-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none", "none"], "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none", "none"], "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"], "w3_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window unexercised absent
    # a pre-generate append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the four judge "
        "products disclosed above")
    return rows, disc


def _excluded_w4(cand, rows):
    """Exact already-judged cell test, vol=none face only (prereg sec.1:
    vol=calm/wild = new-syntax legal cells -- never excluded; W1-lineage
    cells implicitly stop/gate/vol=none; W2 cells carry their own stop
    face; W3 cells carry their own stop+gate faces).  Returns the
    exclusion face or None."""
    if cand["axis"][6] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w4(mask, prices, stop_key, atr20, gate_key,
                               vol_key, gate_state, vol_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> initial-stop (prereg sec.3 dedup legs; zero engine
    burn).  gate=none+vol=none+stop=none = W1 identity; vol=none = W3
    semantic baseline; all gate/vol/stop faces deterministic layers of
    the same three grammar overlays."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = vol_zero_mask(G, vol_key, vol_state)
    return tl2._effective_signal_mask(V, prices, stop_key, atr20)


def run_candidate_curve_w4(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None):
    """One W4 candidate cell at the engine face with the gate + vol
    overlays + initial-stop overlay carried per-cell (prereg sec.3 face
    a; frozen composition order filter -> timing -> GATE -> VOL ->
    initial-stop).

    vol=none+gate=none+stop=none -> byte-identical to the tl1 engine
    face; vol=none+gate=none -> byte-identical to the tl2 W2 engine
    face; vol=none (gate any) -> byte-identical to the tl3 W3 engine
    face (parity laws, selftest-pinned).  Returns (eq, trades, metrics,
    params, patch, stop_fired, gate_zeroed, vol_zeroed).
    """
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    vol_key = cand["axis"][6]
    if gate_state is None:
        gate_state = tl3.gate_state_series(prices)
    if vol_state is None:
        vol_state = vol_state_series(prices)
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
    V = vol_zero_mask(G, vol_key, vol_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = V, 0
    else:
        S = tl2._effective_signal_mask(V, prices, stop_key, atr20)
        d = (V > 0) & (S == 0)
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
        gate_zeroed, vol_zeroed


def _null_axis_draw_w4(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i];
    consumption order frozen = p_on regime -> seven-tuple axis
    R/X/S/T/STOP/GATE/VOL -> signal matrix.  Same engine/cost/panel as
    candidate cells incl. the gate + vol legs (BACKTEST_PLAN three iron
    rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          AXIS_STOP[int(rng.integers(len(AXIS_STOP)))],
          AXIS_GATE[int(rng.integers(len(AXIS_GATE)))],
          AXIS_VOL[int(rng.integers(len(AXIS_VOL)))])
    return p_on, list(ax), rng


# ------------------------------------------------------- generate slice (s2)
def cmd_generate() -> int:
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w4_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w4_grammar.json absent -- run `grammar` first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != grammar["grammar_sha256"] \
            or grammar["grammar_sha256"] != FROZEN_SHA16:
        print(f"GENERATE-GATE: grammar sha drift -- frozen anchor "
              f"{FROZEN_SHA16} != file {grammar['grammar_sha256']}; "
              "refusing")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law, dual-company discipline; "
              f"r379 wait-law) -- honest refuse, pool retries when RAM "
              f"frees")
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
    vol_state, vol_err = _vol_state_full()
    if vol_err:
        print(f"GENERATE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    excl_rows, excl_disc = _load_exclusion_rows_w4(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]["stop_gate_vol_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol_w4(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W4-{family}-{i:04d}"
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
            hit = _excluded_w4(cand, excl_rows)
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
        S = _effective_signal_mask_w4(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      gate_state, vol_state)
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

    # gate/stop/vol face counts + gate x vol interaction (prereg sec.5.4)
    gate_counts, stop_counts = {}, {}
    vol_counts, gate_vol_counts = {}, {}
    for c in distinct:
        gate_counts[c["axis"][5]] = gate_counts.get(c["axis"][5], 0) + 1
        stop_counts[c["axis"][4]] = stop_counts.get(c["axis"][4], 0) + 1
        vol_counts[c["axis"][6]] = vol_counts.get(c["axis"][6], 0) + 1
        k = f"{c['axis'][5]}|{c['axis'][6]}"
        gate_vol_counts[k] = gate_vol_counts.get(k, 0) + 1

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
                                     "vol); exclusion face = vol=none only "
                                     "(sec.1); prior-wave keys vol=none-"
                                     "completed; vol=calm/wild = "
                                     "new-syntax legal cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (gate + vol + "
                                 "stop overlays applied, frozen composition "
                                 "order; naive-hold returns, zero engine "
                                 "burn); engine faces run at screen "
                                 "(W1 precedent)"},
               "gate_face_counts": gate_counts,
               "stop_face_counts": stop_counts,
               "vol_face_counts": vol_counts,
               "gate_vol_face_counts": gate_vol_counts,
               "gate_state_meta": gate_state[2],
               "vol_state_meta": vol_state[2],
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-"
                         "gate-vol-none exclusion faces (face derivation "
                         "is mechanical)",
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
           f"(vol faces {json.dumps(vol_counts, sort_keys=True)}; "
           f"gate x vol {json.dumps(gate_vol_counts, sort_keys=True)}) | "
           f"seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W4-GENERATE, T-98 prereg r396) | same-grammar "
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
    print(f"vol faces: {json.dumps(vol_counts, sort_keys=True)}; "
          f"gate x vol: {json.dumps(gate_vol_counts, sort_keys=True)}")
    print(f"vol meta: {json.dumps(vol_state[2], sort_keys=True)}")
    print(f"products: w4_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------ screen slice (s2)
csv_cols_screen_w4 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law:
# survive iff beat6m_rate > null-family p95 -- program-frozen, zero
# hand-picked thresholds; import-face law, zero re-implementation)
_finalize_math = tl2._finalize_math


def _screen_cell_w4(cell):
    """One W4 screen cell: full leg-L backtest with the gate + vol
    overlays + initial-stop overlay carried per-cell (prereg sec.3 face
    a) -> beat6m row (pool worker; W3 _screen_cell caliber + vol
    columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w4(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W4-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz = \
            run_candidate_curve_w4(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"))
    else:
        eq, trades, metrics, params, patch, fired, gz, vz = \
            run_candidate_curve_w4(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"))
    row = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "stop_face": cand["axis"][4],
           "stop_fired": int(fired), "gate_face": cand["axis"][5],
           "gate_zeroed": int(gz), "vol_face": cand["axis"][6],
           "vol_zeroed": int(vz)}
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


def _cell_list_w4():
    """Distinct candidate cells + K null cells (deterministic order;
    shard-split by index; W1/W2/W3 precedent)."""
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
    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE / G-VOL fail-closed
    gates + the shared passive 6m precompute (prereg sec.2; W3
    cmd_screen_prep caliber on the W4 grammar face + panel gate/vol
    meta disclosure)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    for p, what in ((GRAMMAR_FILE, "w4_grammar.json"),
                    (CANDIDATES_FILE, "w4_candidates.json")):
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

    # G-VOL on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv; NOT the W1-floored load_core pool face)
    vol_state_full, vol_err = _vol_state_full()
    if vol_err:
        print(f"PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    vol_meta_core = vol_state_full[2]

    # G-ANCHOR: registered six replayed through the W4 grammar
    # default-axis identity face (template_default+EW+daily+
    # initial_stop=none+gate=none+vol=none -> tl1 engine identity;
    # run_candidate_curve_w4 parity law selftest-pinned on the
    # gate=none+vol=none face)
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
                "axis": list(tl1.DEFAULT_AXIS) + ["none", "none", "none"]}
        eq, *_ = run_candidate_curve_w4(cand, t, pcut, Pfull,
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
    # panel-level gate + vol meta on the leg-L face (prereg sec.2
    # disclosure; structural invariants only -- the {1523, 1441} probe
    # anchors hold only on the raw full-history face, asserted above)
    _, _, gate_meta = tl3.gate_state_series(prices)
    _, _, vol_meta = vol_state_series(prices)
    if not _vol_structure_pass(vol_meta):
        print(f"PREP-GATE FAIL: G-VOL leg-L structural invariants "
              f"broken {vol_meta} -- honest refuse")
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
                                            VOL_ANCHOR_WILD_DAYS}}},
            "gate_meta": gate_meta, "vol_meta": vol_meta,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),
            "starts": starts, "passive_6m_ret": passive_6m,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(PREP_FILE, prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors 6/6 faithful, "
          f"census {cen}, starts {len(starts)}, passive precomputed, "
          f"gate na-window {gate_meta['na_window_bars']} bars, "
          f"G-VOL {vol_meta['calm_days']}calm/{vol_meta['wild_days']}wild "
          f"first-valid {vol_meta['first_valid_bar_idx']}")
    return 0


def cmd_screen(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDIDATES_FILE, "w4_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w4()
    if _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"SCREEN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law; r379 wait-law) -- honest "
              f"refuse, pool retries when RAM frees")
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
    vol_state, vol_err = _vol_state_full()
    if vol_err:
        print(f"SCREEN-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "grammar": grammar, "atr20": tl2.atr20_series(prices),
             "gate_state": tl3.gate_state_series(prices),
             "vol_state": vol_state}

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
        jobs = [(c["cell_id"], _screen_cell_w4, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells", initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_screen_finalize() -> int:
    print(f"=== {WAVE} screen-finalize ===")
    landed = finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if landed is not None:
        print(f"FINALIZE-IDEMPOTENT-GUARD: {SCREEN_BATCH} already landed "
              f"(ledger total={landed.get('total')}); re-run refused "
              "(pit-95 double-append guard; re-run channel = fresh prereg "
              "+ fresh batch name)")
        return 2
    grammar, cells = _cell_list_w4()
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
    stop_counts, gate_counts, vol_counts = {}, {}, {}
    gate_seg, vol_seg, gate_vol_seg = {}, {}, {}
    for r in cand_rows:
        stop_counts[r["stop_face"]] = stop_counts.get(r["stop_face"], 0) + 1
        gf, vf = r["gate_face"], r["vol_face"]
        gate_counts[gf] = gate_counts.get(gf, 0) + 1
        vol_counts[vf] = vol_counts.get(vf, 0) + 1
        for seg, key in ((gate_seg, gf), (vol_seg, vf),
                         (gate_vol_seg, f"{gf}|{vf}")):
            s = seg.setdefault(key, {"n_cells": 0, "n_survivors": 0})
            s["n_cells"] += 1
            s["n_survivors"] += int(bool(r["survives_screen"]))
    for seg in (gate_seg, vol_seg, gate_vol_seg):
        for key, s in seg.items():
            s["survival_rate"] = round(
                s["n_survivors"] / s["n_cells"], 6) if s["n_cells"] else 0.0
    prep = (json.load(open(PREP_FILE, encoding="utf-8"))
            if os.path.exists(PREP_FILE) else {})
    gate_meta = prep.get("gate_meta")
    vol_meta = prep.get("vol_meta")
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(SCREEN_BATCH, batch_trials,
                               "results/trial_labor_w4/w4_screen.json",
                               evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "screen", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF), "grammar_sha256": grammar["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)), 4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(tl1.NULL_P_REGIMES),
                           "seed": SEED_NULL,
                           "draw_order": "p_on regime -> seven-tuple axis "
                                         "R/X/S/T/STOP/GATE/VOL -> signal "
                                         "matrix (frozen runner face, "
                                         "gate+vol legs included)"},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.3, frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "stop_face_counts": stop_counts,
           "gate_face_counts": gate_counts,
           "vol_face_counts": vol_counts,
           "gate_segmented_survival": gate_seg,
           "vol_segmented_survival": vol_seg,
           "gate_vol_interaction_survival": gate_vol_seg,
           "gate_na_window_bars": (gate_meta["na_window_bars"]
                                   if gate_meta else None),
           "vol_na_window_bars": (vol_meta["na_window_bars"]
                                  if vol_meta else None),
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber, V1 13bp base, T+1); "
                             "gate + vol overlays + initial-stop overlay at "
                             "the engine face = effective-signal zeroing "
                             "(MSG-0440 E1 mapping, dedup-face consistency, "
                             "frozen composition order signal -> filter -> "
                             "timing -> GATE -> VOL -> initial-stop); "
                             "MA200/vol-closed NaN windows gate-closed on "
                             "BOTH faces (panel-level counts in "
                             "gate_na_window_bars / vol_na_window_bars); "
                             "workers BelowNormal; checkpoint append-per-"
                             "cell; beat6m comparison operator = >= per "
                             "frozen prereg sec.3 text; survival math "
                             "imported from tl2._finalize_math (W2 "
                             "identical law)"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(SCREEN_FILE, out)
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w4,
                           extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"vol segmented survival: "
          f"{json.dumps(vol_seg, sort_keys=True)}")
    print(f"gate x vol interaction survival: "
          f"{json.dumps(gate_vol_seg, sort_keys=True)}")
    print(f"products: w4_screen.json + w4_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w4(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W4 seed binding [20290500, cell_idx].  Math imported verbatim from
    tl2._dual_nulls_w2 (import law; the seed constant is the only
    differing face -- selftest cross-checks at the W1 seed)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _overlay_stop_disclosure_w4(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state):
    """Per-cell stop trigger/fill-day disclosure on the leg-L signal face
    with the W4 composition order (filter -> timing -> GATE -> VOL ->
    initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors tl3.
    _overlay_stop_disclosure with the vol overlay inserted before stop
    arming (engine-face consistency law; summary math imported)."""
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
    V = vol_zero_mask(G, cand["axis"][6], vol_state)
    _, ev = tl2.stop_exit_overlay(V, prices, stop_key, atr20)
    s = tl2._stop_dev_summary(ev, prices, mask.index)
    s["stop_face"] = stop_key
    return s


def _judge_cell_w4(cell):
    """One W4 survivor judged cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full
    curves with the gate + vol + initial-stop overlays carried per cell
    (frozen composition order) + window-grid beat vs passive + regime
    segments + dual nulls (W4 seed [20290500, i]) + descriptive clauses +
    crisis/stop/gate-flip/vol-flip disclosure columns.  Gates face =
    leg-L base (W1/W2/W3 judged-cell caliber); x2 + descriptive =
    disclosure."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "stop_face": cand["axis"][4],
           "gate_face": cand["axis"][5], "vol_face": cand["axis"][6]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        gs = st[f"gate_state_{leg}"]
        vs = st[f"vol_state_{leg}"]
        eq, trades, metrics, params, patch, fired, gz, vz = \
            run_candidate_curve_w4(cand, template, prices, P,
                                   st["states"], st[f"atr20_{leg}"],
                                   fundamental_ok=fok, gate_state=gs,
                                   vol_state=vs)
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, gz2, vz2 = run_candidate_curve_w4(
                cand, template, prices, P, st["states"],
                st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                vol_state=vs)
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "stop_fired": 0,
                         "stop_fired_x2": 0, "gate_zeroed": 0,
                         "gate_zeroed_x2": 0, "vol_zeroed": 0,
                         "vol_zeroed_x2": 0,
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
                     "vol_zeroed_x2": int(vz2)}
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
            out["stop_disclosure"] = _overlay_stop_disclosure_w4(
                cand, prices, P, st["atr20_L"], fok, gs, vs)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w4(r if len(r) else np.zeros(30),
                                       cell["i"])
    # prereg sec.5.6 gate/vol-flip day columns (disclosure-only, zero
    # gate weight): panel-level flip-day count of the cell's OWN gate /
    # vol face on the leg-L panel (state meta face; none -> null)
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
    vol meta (prereg sec.2/3; W3 cmd_judge_prep caliber on the W4
    grammar face; G-VOL structural per leg + probe anchors on the raw
    full-history face)."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w4_screen.json "
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
    vol_state_full, vol_err = _vol_state_full()
    if vol_err:
        print(f"JUDGE-PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    starts, gate_meta, vol_meta = {}, {}, {}
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
        _, _, gmeta = tl3.gate_state_series(prices)
        gate_meta[leg] = gmeta
        _, _, vmeta = vol_state_series(prices)
        if not _vol_structure_pass(vmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-VOL structural "
                  f"invariants broken {vmeta} -- honest refuse")
            return 1
        vol_meta[leg] = vmeta
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
    if not screen.get("survivors"):
        out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": FROZEN_SHA16, "n_survivors": 0,
               "g_manifest": gm, "starts": starts, "passive": {},
               "census_frozen": tl1.FROZEN_CENSUS,
               "gate_meta": gate_meta, "vol_meta": vol_meta,
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
           "vol_meta": vol_meta,
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
          f"{vol_meta['L']['wild_days']}wild)")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),
                    (SCREEN_FILE, "w4_screen.json")):
        if not os.path.exists(p):
            # O-1712 sec.1.2 diagnostic-soundness: the refusal self-locates
            # the expected face (abs path + machine) so absence vs path
            # mismatch vs wrong-machine face reads off the refusal line
            # itself (R398 anchor-face lesson applied to the judge gate).
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

    vol_state_full, vol_err = _vol_state_full()
    if vol_err:
        print(f"JUDGE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
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
        jobs = [(c["cell_id"], _judge_cell_w4, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="judge cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_judge_finalize() -> int:
    print(f"=== {WAVE} judge-finalize ===")
    landed = finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if landed is not None:
        print(f"FINALIZE-IDEMPOTENT-GUARD: {JUDGE_BATCH} already landed "
              f"(ledger total={landed.get('total')}); re-run refused "
              "(pit-95 double-append guard; re-run channel = fresh prereg "
              "+ fresh batch name)")
        return 2
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
                               "results/trial_labor_w4/w4_judge.json",
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
    # GATE/VOL-face + gate x vol interaction judged summaries (prereg
    # sec.5.4 direction-readout faces; disclosure-only, zero gate weight)
    gate_sum, vol_sum, gate_vol_sum = {}, {}, {}
    for r in judged:
        g = r.get("gate_face", "none")
        v = r.get("vol_face", "none")
        for seg, key in ((gate_sum, g), (vol_sum, v),
                         (gate_vol_sum, f"{g}|{v}")):
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
           "gate_vol_interaction_judgment": gate_vol_sum,
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
                             "gate + vol + initial-stop overlays "
                             "carried per cell (frozen composition "
                             "signal -> filter -> timing -> GATE -> VOL "
                             "-> initial-stop; engine/exit_rules.py zero "
                             "touch) + regime segments + dual nulls "
                             "(B=2000 block-20 + P=2000 sign-flip, seed "
                             "[20290500, cell]); gates on the leg-L "
                             "base face (W1/W2/W3 judged-cell caliber); "
                             "beat operator = strict > (W1/W2/W3 judged-"
                             "cell caliber; screen >= was the sec.3 s2 "
                             "literal); x2 + descriptive clauses = "
                             "disclosure-only zero criteria weight; "
                             "crisis-day count = |daily|>8% leg-L base "
                             "(sec.5.6); stop trigger/fill-day D+1 "
                             "open-vs-close deviation = MSG-0450 annex-1 "
                             "disclosure on the protection-floor signal "
                             "face with the vol overlay inserted before "
                             "stop arming (W4 composition law); "
                             "gate_flip_days_legL / vol_flip_days_legL "
                             "= panel-level flip-day counts of the "
                             "cell's OWN gate / vol face on the leg-L "
                             "panel (none -> null; sec.5.6 disclosure "
                             "columns, zero gate weight); gate x vol "
                             "interaction segments = prereg sec.3 "
                             "dual-gate disclosure column; fundamental "
                             "keep-ok face = screen consistency law"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_FILE, out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    print(f"vol-face judgment: {json.dumps(vol_sum, sort_keys=True)}")
    print(f"gate x vol interaction judgment: "
          f"{json.dumps(gate_vol_sum, sort_keys=True)}")
    return 0


# ------------------------------------------------------------ status / grammar
def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    print(f"grammar file: {GRAMMAR_FILE} "
          f"({'EXISTS' if os.path.exists(GRAMMAR_FILE) else 'not built'})")
    for f in ("w4_candidates.json", "prep_state.json", "w4_screen.json",
              "w4_judge.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'EXISTS' if os.path.exists(p) else '-'}")
    if os.path.isdir(CKPT_DIR):
        for f in sorted(os.listdir(CKPT_DIR)):
            if f.endswith(".jsonl"):
                n = sum(1 for _ in open(os.path.join(CKPT_DIR, f),
                                        encoding="utf-8"))
                print(f"  checkpoint/{f}: {n} rows")
    print("slice map (W3 r392/r395/r370 precedent): slice-1 grammar + "
          "vol overlay + full funnel command set + selftest LANDED this "
          "round (bm-a r397); slice-1b pool entry TRIAL-LABOR-W4-"
          "GENERATE entered same round (CPU pool face lawful per MSG-"
          "20260928-0930 sec.2; W4-JUDGE queued behind W2/W3-JUDGE + "
          "RAM r354 sequencing gate per prereg sec.0); NEXT slices: "
          "generate burn (autofill tick) -> screen-prep/screen burn -> "
          "screen-finalize -> judge trio -> intake (physical dep: judge "
          "products; separate commits with MSG declarations per W2 r366 "
          "precedence); parallel claim legal per T-50/T-64 slice "
          "precedent after MSG-declare")
    return 0


def cmd_grammar() -> int:
    """Serialize the frozen grammar face (prereg sec.3: value-domain table
    frozen at runner-build time; zero candidates drawn -- not a wave run)."""
    if FROZEN_SHA16 and os.path.exists(GRAMMAR_FILE):
        g = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if g["grammar_sha256"] == FROZEN_SHA16:
            print(f"w4_grammar.json already frozen at anchor "
                  f"{FROZEN_SHA16}; refusing overwrite (append-only face)")
            return 0
    g = build_grammar_w4()
    os.makedirs(RES_DIR, exist_ok=True)
    with open(GRAMMAR_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    chk = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    assert chk["grammar_sha256"] == g["grammar_sha256"]
    print(f"w4_grammar.json written: sha16={g['grammar_sha256'][:16]} "
          f"axis_combos={g['axis_combos']} B_fns={len(g['families']['B'])} "
          f"exclusion_entries={len(g['exclusion']['stop_gate_vol_none_face'])}")
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

    # [1] grammar: counts + new sha + seed binding
    g = build_grammar_w4()
    ok("grammar deterministic (sha equal on rebuild)",
       g["grammar_sha256"] == build_grammar_w4()["grammar_sha256"])
    n_b = len(g["families"]["B"])
    ok(f"B family = machinery actual 72 (prereg prose 76 declared "
       f"divergent, got {n_b})", n_b == 72)
    ok("inventory audit: 77 non-grid fns, 13 modules on disk",
       g["inventory_audit"]["non_grid_fns"] == 77
       and g["inventory_audit"]["modules_on_disk"] == 13)
    ok("axis combos = 32256 (7x8x4x2x8x3x3)",
       g["axis_combos"] == 32256 == AXIS_COMBOS)
    ok("vol axis frozen 3 faces",
       g["axes"]["vol"] == AXIS_VOL and len(AXIS_VOL) == 3)
    ok("stop axis imported from tl2 (8 faces, zero re-declare)",
       g["axes"]["initial_stop"] == tl2.AXIS_STOP
       and g["stop_formula"] is tl2.STOP_FORMULA)
    ok("gate axis imported from tl3 (3 faces, zero re-declare)",
       g["axes"]["gate"] == tl3.AXIS_GATE and g["gate_spec"] is tl3.GATE_SPEC)
    ok("seeds bound (20289500/20290000/20290500)",
       (SEED_GEN, SEED_NULL, SEED_UNC) == (20289500, 20290000, 20290500))
    ok("new-syntax sha16 != W1/MASS/W2/W3 faces",
       g["grammar_sha256"][:16] not in
       ("a2fa15f4b06b3c40", "96269ebe766c3fc2", "1dd3d95792395cec",
        "cc59eab79db53436"))
    if FROZEN_SHA16:
        ok("serialized anchor == build face (FROZEN_SHA16 pinned)",
           g["grammar_sha256"] == FROZEN_SHA16)
    ok("exclusion carried on stop-gate-vol-none face",
       len(g["exclusion"]["stop_gate_vol_none_face"]) >= 6)
    ok("vol spec frozen fields present",
       all(k in g["vol_spec"] for k in
           ("member", "vol20", "med500", "nan_window", "overlay",
            "non_isomorphism", "composition_order")))
    ok("vol probe anchors embedded in grammar",
       g["vol_anchor"]["first_valid_bar"] == 519
       and g["vol_anchor"]["calm_days"] == 1523
       and g["vol_anchor"]["wild_days"] == 1441)

    # [2] vol series math on a synthetic controlled panel (640 bars:
    # flat 100 -> calm zone; alternating +-2% returns -> wild zone)
    idx = pd.bdate_range("2020-01-01", periods=640)
    flat = np.full(561, 100.0)
    path = [100.0]
    for t in range(561, 640):
        path.append(path[-1] * (1.02 if t % 2 == 0 else 0.98))
    vol_path = np.concatenate([flat, np.asarray(path[1:])])
    vol_frames = {"510300": pd.DataFrame(
        {"open": vol_path, "high": vol_path * 1.03, "low": vol_path * 0.97,
         "close": vol_path, "volume": 1e4, "amount": 1e6}, index=idx)}
    calm, wild, vmeta = vol_state_series(vol_frames)
    close_s = pd.Series(vol_path, index=idx)
    ret_s = close_s / close_s.shift(1) - 1.0
    vol20_s = ret_s.rolling(20, min_periods=20).std(ddof=1)
    med500_s = vol20_s.rolling(500, min_periods=500).median()
    ok_s = vol20_s.notna() & med500_s.notna()
    exp_calm = ok_s & (vol20_s <= med500_s)
    exp_wild = ok_s & (vol20_s > med500_s)
    ok("vol20/med500 == literal rolling spec (20/std ddof1 + 500/median)",
       int(vol20_s.isna().sum()) == 20
       and int(med500_s.isna().sum()) == 519)
    ok("structural anchor: med500 first valid bar-idx == 519 "
       "(na window 519 bars)",
       vmeta["first_valid_bar_idx"] == 519
       and vmeta["na_window_bars"] == 519
       and med500_s.first_valid_index() == idx[519])
    ok("NaN window vol-closed BOTH faces (first 519 bars)",
       not calm.iloc[:519].any() and not wild.iloc[:519].any())
    ok("calm/wild == literal spec booleans (complementary on valid days)",
       calm.equals(exp_calm) and wild.equals(exp_wild)
       and bool((calm[ok_s] == ~wild[ok_s]).all()))
    ok("calm zone = flat segment, wild zone = alternating segment "
       "(controlled fixture)",
       int(calm.sum()) == 42 and int(wild.sum()) == 79
       and bool(calm.iloc[519:561].all())
       and bool(wild.iloc[561:640].all()))
    ok("meta counts == series sums; flips deterministic",
       vmeta["calm_days"] == int(calm.sum())
       and vmeta["wild_days"] == int(wild.sum())
       and vmeta["flips_calm_face"] == int((calm.values[1:]
                                            != calm.values[:-1]).sum())
       and vmeta["n_bars"] == 640
       and vmeta["calm_days"] + vmeta["wild_days"]
       + vmeta["na_window_bars"] == 640)
    calm2, wild2, vmeta2 = vol_state_series(vol_frames)
    ok("vol state deterministic (double-run equal)",
       calm.equals(calm2) and wild.equals(wild2) and vmeta == vmeta2)
    # causality leg (point-in-time): truncated-panel state at day d ==
    # full-series state at day d (no lookahead; rolling <=d info only)
    trunc = {"510300": vol_frames["510300"].iloc[:580]}
    calm_t, wild_t, _ = vol_state_series(trunc)
    ok("causality: truncated-panel state at d == full-series state at d "
       "(signal-day info set, zero lookahead)",
       bool(calm_t.iloc[570:579].equals(calm.iloc[570:579]))
       and bool(wild_t.iloc[570:579].equals(wild.iloc[570:579])))
    # G-VOL gate fns: structural + anchor faces
    ok("_vol_structure_pass law: fixture meta passes structure, fails "
       "probe anchors (synthetic != core48 counts)",
       _vol_structure_pass(vmeta) is True
       and _vol_anchor_pass(vmeta) is False)
    real_like = {"n_bars": 3483, "na_window_bars": 519,
                 "first_valid_bar_idx": 519, "first_valid": "2014-07-17",
                 "calm_days": 1523, "wild_days": 1441,
                 "flips_calm_face": 0, "flips_wild_face": 0}
    ok("_vol_anchor_pass law: probe-anchor meta passes; drift fails",
       _vol_anchor_pass(real_like) is True
       and _vol_anchor_pass(dict(real_like, calm_days=1522)) is False
       and _vol_anchor_pass(dict(real_like, first_valid_bar_idx=518))
       is False)

    # [3] vol_zero_mask unit legs (synthetic mask; reindex law)
    cols = ["500000", "500001"]
    mask = pd.DataFrame(0, index=idx, columns=cols, dtype=int)
    mask.iloc[100:640, 0] = 1          # spans NaN window + calm + wild
    mask.iloc[100:640, 1] = 1
    z_none = vol_zero_mask(mask, "none", (calm, wild, vmeta))
    ok("vol=none is the identity (W3 semantic baseline)",
       z_none is mask)
    keep_calm_win = calm.reindex(idx).fillna(False).astype(int)
    keep_wild_win = wild.reindex(idx).fillna(False).astype(int)
    z_calm = vol_zero_mask(mask, "calm", (calm, wild, vmeta))
    ok("calm face == mask * calm-permission (exact elementwise law)",
       z_calm["500000"].equals(mask["500000"].mul(keep_calm_win))
       and z_calm["500001"].equals(mask["500001"].mul(keep_calm_win)))
    z_wild = vol_zero_mask(mask, "wild", (calm, wild, vmeta))
    ok("wild face == mask * wild-permission (exact elementwise law)",
       z_wild["500000"].equals(mask["500000"].mul(keep_wild_win))
       and z_wild["500001"].equals(mask["500001"].mul(keep_wild_win)))
    ok("NaN-window signals blocked on BOTH faces (conservative)",
       int(z_calm.iloc[:519].sum().sum()) == 0
       and int(z_wild.iloc[:519].sum().sum()) == 0)
    ok("vol zero deterministic (double-run byte-equal)",
       vol_zero_mask(mask, "calm", (calm, wild, vmeta)).equals(z_calm))

    # [4] dual-gate intersection legs (gate x vol = two-condition AND)
    gs_v = tl3.gate_state_series(vol_frames)
    g_both = tl3.gate_zero_mask(mask, "bull", gs_v)
    gv = vol_zero_mask(g_both, "calm", (calm, wild, vmeta))
    bull_s = gs_v[0].reindex(idx).fillna(False).astype(int)
    both_perm = (bull_s == 1) & (keep_calm_win == 1)
    ok("dual gate: composed face == mask * (bull AND calm) intersection",
       gv["500000"].equals(mask["500000"].mul(both_perm.astype(int)))
       and gv["500001"].equals(mask["500001"].mul(both_perm.astype(int))))
    vg = vol_zero_mask(mask, "calm", (calm, wild, vmeta))
    vgg = tl3.gate_zero_mask(vg, "bull", gs_v)
    ok("dual gate: gate and vol overlays commute (elementwise AND law)",
       vgg.equals(gv))
    blocked_gv = int((gv > 0).mul(
        ~both_perm, axis=0).sum().sum())
    ok("dual gate: gate-open+vol-closed and gate-closed+vol-open both "
       "blocked (zero survivors outside the intersection)",
       blocked_gv == 0
       and int((gv > 0).mul(both_perm, axis=0).sum().sum())
       == int((gv > 0).sum().sum()))

    # [5] Sobol seven-tuple draw determinism + domain binding
    c1 = list(draw_candidate_sobol_w4(g, "A", 0, 32))
    c2 = list(draw_candidate_sobol_w4(g, "A", 0, 32))
    ok("Sobol draw deterministic (32 draws byte-equal)",
       json.dumps(c1, sort_keys=True, default=str)
       == json.dumps(c2, sort_keys=True, default=str))
    ok("draw carries seven-tuple axis with vol face",
       all(len(c["axis"]) == 7 and c["axis"][6] in AXIS_VOL
           for _, c in c1))
    ok("draw params inside frozen domains",
       all(c["sig_params"][nm] in g["value_domains"][
               f"{c['module']}.{c['fn']}"][nm]
           for _, c in c1
           for nm in c["sig_params"]))
    tot = sum(1 for _ in draw_candidate_sobol_w4(g, "B", 0, 64))
    ok("B-family stream yields declared count", tot == 64)

    # [6] exclusion law (prereg sec.1): vol=none face only; seven-source
    # pads (W1 4+3 / W2 5+2 / W3 6+1 / MASS translated 6+1)
    excl_rows = [
        {"module": "ta", "fn": "engulf_reversal",
         "sig_params": {"drop_th": -0.05},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "none", "none", "none"],
         "face": "registered_default_axis:stop-gate-vol-none"},
        {"module": "patterns", "fn": "needle_probe",
         "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
         "axis": ["liquidity", "profit_ladder", "regime_delever",
                  "daily_signal", "p3", "none", "none"],
         "face": "w2_screen_survivor:stop-gate-vol-none"},
        {"module": "trend", "fn": "donchian_breakout",
         "sig_params": {"entry_n": 34, "exit_n": 7},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "p3", "bear", "none"],
         "face": "w3_screen_survivor:stop-gate-vol-none"},
        {"module": "ta", "fn": "bb_squeeze_breakout",
         "sig_params": {"entry_n": 34, "exit_n": 7},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "none", "none", "none"],
         "face": "mass_screen_survivor:translated-exact"}]
    c_reg = {"module": "ta", "fn": "engulf_reversal",
             "sig_params": {"drop_th": -0.05},
             "axis": ["none", "template_default", "equal_weight",
                      "daily_signal", "none", "none", "none"]}
    ok("exclusion: registered default stop-gate-vol-none cell rejected",
       _excluded_w4(c_reg, excl_rows) is not None)
    ok("exclusion: same cell stop!=none NOT excluded (new-syntax face)",
       _excluded_w4(dict(c_reg, axis=[*c_reg["axis"][:4], "p3",
                                      "none", "none"]),
                    excl_rows) is None)
    ok("exclusion: same cell gate!=none NOT excluded (legal new face)",
       _excluded_w4(dict(c_reg, axis=[*c_reg["axis"][:5], "bull",
                                      "none"]),
                    excl_rows) is None)
    ok("exclusion: same cell vol=calm NOT excluded (legal new face)",
       _excluded_w4(dict(c_reg, axis=[*c_reg["axis"][:6], "calm"]),
                    excl_rows) is None)
    ok("exclusion: same cell vol=wild NOT excluded (legal new face)",
       _excluded_w4(dict(c_reg, axis=[*c_reg["axis"][:6], "wild"]),
                    excl_rows) is None)
    c_w2 = {"module": "patterns", "fn": "needle_probe",
            "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
            "axis": ["liquidity", "profit_ladder", "regime_delever",
                     "daily_signal", "p3", "none", "none"]}
    ok("exclusion: W2 survivor explicit stop=p3 face rejected on exact "
       "key (vol=none pad law)",
       _excluded_w4(c_w2, excl_rows) is not None)
    c_w3 = {"module": "trend", "fn": "donchian_breakout",
            "sig_params": {"entry_n": 34, "exit_n": 7},
            "axis": ["none", "template_default", "equal_weight",
                     "daily_signal", "p3", "bear", "none"]}
    ok("exclusion: W3 survivor explicit stop+gate faces rejected on "
       "exact key (vol=none pad law)",
       _excluded_w4(c_w3, excl_rows) is not None)
    c_w3v = dict(c_w3, axis=[*c_w3["axis"][:6], "calm"])
    ok("exclusion: same W3 key vol=calm NOT excluded (new-syntax)",
       _excluded_w4(c_w3v, excl_rows) is None)
    c_mass = {"module": "ta", "fn": "bb_squeeze_breakout",
              "sig_params": {"entry_n": 34, "exit_n": 7},
              "axis": ["none", "template_default", "equal_weight",
                       "daily_signal", "none", "none", "none"]}
    ok("exclusion: MASS translated-exact cell rejected (vol=none pad)",
       _excluded_w4(c_mass, excl_rows) is not None)
    tr_yes = tl3._mass_translate_row(
        {"family": "ta.bb_squeeze_breakout",
         "params": {"entry_n": 34, "exit_n": 7},
         "axes": {"R": "none", "X": "own", "S": "full", "T": "daily"}})
    ok("MASS translation import: tl3 exact face + W4 vol=none pad law",
       tr_yes is not None
       and tr_yes["axis"] == ["none", "template_default", "equal_weight",
                              "daily_signal", "none", "none"]
       and list(tr_yes["axis"]) + ["none"] == c_mass["axis"])

    # [7] effective-face composition legs (gate -> vol -> stop; synthetic)
    flatA = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0,
                          "close": 100.0, "volume": 1000.0,
                          "amount": 1e5}, index=idx)
    dip = flatA.copy()
    dip.loc[idx[540], "low"] = 90.0       # pierces any p3 level INSIDE the
    # calm-open window (bars 519-560; close unchanged -> vol/gate series
    # untouched -> the stop bite is observable on the composed face)
    mask7 = pd.DataFrame(0, index=idx, columns=["A", "B"], dtype=int)
    mask7.iloc[519:640, 0] = 1            # vol-valid zone only
    mask7.iloc[100:640, 1] = 1            # spans NaN window + valid zone
    vs = (calm, wild, vmeta)
    S_id = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                     "none", None, "none", "none",
                                     gs_v, vs)
    ok("effective face: gate=none+vol=none+stop=none is the identity",
       S_id.equals(mask7))
    S_vonly = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                        "none", None, "none", "calm",
                                        gs_v, vs)
    ok("effective face: vol-only face == mask * calm-permission (exact)",
       S_vonly["A"].equals(mask7["A"].mul(keep_calm_win)))
    S_gs = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                     "p3", None, "none", "calm", gs_v, vs)
    S_gs2 = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                       "p3", None, "none", "calm", gs_v, vs)
    ok("effective face: vol+stop composed, deterministic (double-run "
       "byte-equal)",
       S_gs.equals(S_gs2))
    S_w3face = tl3._effective_signal_mask_w3(mask7, {"A": dip, "B": flatA},
                                             "none", None, "none", gs_v)
    S_w4none = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                          "none", None, "none", "none",
                                          gs_v, vs)
    ok("effective face: vol=none == W3 face byte-equal (semantic "
       "baseline identity law)",
       S_w4none.equals(S_w3face))
    S_tl2 = tl2._effective_signal_mask(mask7, {"A": dip, "B": flatA},
                                       "p3", None)
    S_w4tl2 = _effective_signal_mask_w4(mask7, {"A": dip, "B": flatA},
                                         "p3", None, "none", "none",
                                         gs_v, vs)
    ok("effective face: gate=none+vol=none+stop=p3 == tl2 W2 face "
       "byte-equal (parity law)",
       S_w4tl2.equals(S_tl2))
    ok("effective face: composed vol face never holds on vol-closed "
       "days (vol precedes stop arming)",
       int(((S_gs > 0) & (keep_calm_win == 0)).sum().sum()) == 0)
    ok("effective face: composed calm face differs from vol-only face "
       "(stop bites inside the calm-open window)",
       not S_gs.equals(S_vonly)
       and int(((S_gs["A"] == 0) & (mask7["A"] == 1)
                & (keep_calm_win == 1)).sum()) > 0)

    # [8] round-robin stream consumption == per-slot sequential streams
    n_slots_a = len(g["families"]["A"])
    n_rr = 18
    streams = {s: draw_candidate_sobol_w4(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)
               for s in range(n_slots_a)}
    rr = [next(streams[i % n_slots_a]) for i in range(n_rr)]
    seq = {s: [c for _, c in draw_candidate_sobol_w4(
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

    # [10] engine-face legs: parity + determinism + vol bites (null path)
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled 510300 path = the [2] vol fixture (calm flat + wild
    # alternating); engine faces below ride its vol_state
    frames3["510300"] = vol_frames["510300"].copy()
    P3 = tl1.build_panels(frames3)
    st3 = pd.Series("GREEN", index=P3["close"].index)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = vol_state_series(frames3)
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none", "none", "none"]}
    eq_w4, *_ = run_candidate_curve_w4(base, None, frames3, P3, st3,
                                       gate_state=gs3, vol_state=vs3)
    eq_tl1 = tl1.run_candidate_curve(
        dict(base, axis=base["axis"][:4]), None, frames3, P3, st3)[0]
    ok("engine face: vol=none+gate=none+stop=none identical to tl1 face "
       "(byte-equal)",
       list(eq_w4.values) == list(eq_tl1.values))
    stop_c = dict(base, axis=[*base["axis"][:4], "p3", "none", "none"])
    eq_s, tr_s, m_s, _, _, fired_s, gz_s, vz_s = run_candidate_curve_w4(
        stop_c, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3)
    eq_s2 = tl2.run_candidate_curve_w2(
        dict(stop_c, axis=stop_c["axis"][:5]), None, frames3, P3, st3)[0]
    ok("engine face: vol=none+gate=none+stop=p3 identical to tl2 W2 "
       "face (byte-equal parity law)",
       list(eq_s.values) == list(eq_s2.values) and fired_s >= 0)
    gate_c = dict(base, axis=[*base["axis"][:5], "bull", "none"])
    eq_w4g, *_ = run_candidate_curve_w4(gate_c, None, frames3, P3, st3,
                                        gate_state=gs3, vol_state=vs3)
    eq_w3g = tl3.run_candidate_curve_w3(
        dict(gate_c, axis=gate_c["axis"][:6]), None, frames3, P3, st3,
        gate_state=gs3)[0]
    ok("engine face: vol=none (gate=bull) identical to tl3 W3 face "
       "(byte-equal semantic-baseline identity law)",
       list(eq_w4g.values) == list(eq_w3g.values))
    eq_s3, *_ = run_candidate_curve_w4(stop_c, None, frames3, P3, st3,
                                        gate_state=gs3, vol_state=vs3)
    ok("engine face: deterministic (double-run byte-equal)",
       list(eq_s3.values) == list(eq_s.values))
    # vol bites at the engine face: same random null signals, vol=calm
    # vs vol=none -> different curves (deterministic double-run)
    rng_n = np.random.default_rng([4242, 1])
    mat_n = rng_n.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    null_c = {"module": "null", "fn": "random_signal",
              "sig_params": {"p_on": 0.05},
              "axis": ["none", "template_default", "equal_weight",
                       "daily_signal", "none", "none", "none"],
              "candidate_id": "ST-NULL-0", "family": "NULL"}
    eq_ng, _, m_ng, _, _, _, _, _ = run_candidate_curve_w4(
        null_c, None, frames3, P3, st3, rng_matrix=mat_n, p_on=0.05,
        gate_state=gs3, vol_state=vs3)
    null_v = dict(null_c, axis=[*null_c["axis"][:6], "calm"])
    eq_vg, _, m_vg, _, _, _, gz_v, vz_v = run_candidate_curve_w4(
        null_v, None, frames3, P3, st3, rng_matrix=mat_n, p_on=0.05,
        gate_state=gs3, vol_state=vs3)
    eq_vg2, *_ = run_candidate_curve_w4(
        null_v, None, frames3, P3, st3, rng_matrix=mat_n, p_on=0.05,
        gate_state=gs3, vol_state=vs3)
    ok("engine face: vol=calm bites (null-signal curve differs from "
       "vol=none; deterministic double-run; vol_zeroed > 0)",
       list(eq_vg.values) != list(eq_ng.values)
       and list(eq_vg.values) == list(eq_vg2.values)
       and vz_v > 0 and gz_v == 0)

    # [11] null draw: determinism + seven-tuple axis binding (prereg
    # sec.3 frozen consumption order p_on -> R/X/S/T/STOP/GATE/VOL)
    p1, ax1, rng1 = _null_axis_draw_w4(7)
    p1b, ax1b, rng1b = _null_axis_draw_w4(7)
    ok("null draw deterministic (p_on + seven-tuple axis + rng state)",
       p1 == p1b and ax1 == ax1b
       and list(rng1.random(3)) == list(rng1b.random(3)))
    ok("null axis = seven-tuple with stop+gate+vol faces in frozen grids",
       len(ax1) == 7 and ax1[0] in tl1.AXIS_FILTERS
       and ax1[1] in tl1.AXIS_EXITS and ax1[2] in tl1.AXIS_SIZING
       and ax1[3] in tl1.AXIS_TIMING and ax1[4] in AXIS_STOP
       and ax1[5] in AXIS_GATE and ax1[6] in AXIS_VOL
       and p1 in tl1.NULL_P_REGIMES)

    # [12] ledger batch names frozen (prereg sec.3 literals)
    ok("ledger batch names frozen per prereg sec.3 literals",
       SCREEN_BATCH == "TRIAL_LAB_W4_SCREEN"
       and JUDGE_BATCH == "TRIAL_LAB_W4_JUDGE")

    # [13] grammar serialization round-trip (tempfile; no repo writes)
    import tempfile
    with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8",
            newline="\n") as tf:
        json.dump(g, tf, ensure_ascii=False, indent=1, sort_keys=True)
        tmp_path = tf.name
    try:
        chk = json.load(open(tmp_path, encoding="utf-8"))
        ok("grammar serialization round-trip (sha stable)",
           chk["grammar_sha256"] == g["grammar_sha256"]
           and _grammar_sha16(chk) == g["grammar_sha256"])
    finally:
        os.unlink(tmp_path)

    # [14] screen cell machinery in-process (synthetic worker state;
    # [10] fixtures reused; vol columns wired)
    starts3 = [10, 60, 110, 150, 600]   # complete 126-td windows (len 640)
    tl1._ST = {"P": P3, "prices": frames3, "states": st3,
               "starts": starts3, "passive_6m": {10: 0.05, 60: 0.05,
                                                  110: 0.05, 150: 0.05,
                                                  600: 0.05},
               "fundamental_ok": None, "grammar": g,
               "atr20": tl2.atr20_series(frames3), "gate_state": gs3,
               "vol_state": vs3}
    row_null = _screen_cell_w4({"cell_id": "SCREEN|NULL-0003",
                                "kind": "null", "i": 3, "cand": None})
    ok("screen null cell row: id/family/stop+gate+vol faces wired + "
       "complete windows (gate+vol legs included)",
       row_null["candidate_id"] == "W4-NULL-0003"
       and row_null["family"] == "NULL"
       and row_null["stop_face"] in AXIS_STOP
       and row_null["gate_face"] in AXIS_GATE
       and row_null["vol_face"] in AXIS_VOL
       and row_null["beat6m_n"] == 5)
    vol_c = dict(base, candidate_id="ST-B-0001",
                 axis=[*base["axis"][:4], "p3", "bull", "calm"])
    row_v1 = _screen_cell_w4({"cell_id": "SCREEN|ST-B-0001",
                               "kind": "cand", "cand": vol_c,
                               "template": None})
    row_v2 = _screen_cell_w4({"cell_id": "SCREEN|ST-B-0001",
                              "kind": "cand", "cand": vol_c,
                              "template": None})
    ok("screen cand cell row: gate+vol+stop faces carried + "
       "deterministic (double-run byte-equal)",
       row_v1["stop_face"] == "p3" and row_v1["gate_face"] == "bull"
       and row_v1["vol_face"] == "calm"
       and row_v1["gate_zeroed"] >= 0 and row_v1["vol_zeroed"] >= 0
       and row_v1["stop_fired"] >= 0
       and json.dumps(row_v1, sort_keys=True)
       == json.dumps(row_v2, sort_keys=True))
    if row_v1.get("no_entries"):
        ok("screen cand cell row: degenerate face honest (beat6m zeros, "
           "no binom columns)",
           row_v1["beat6m_k"] == 0 and row_v1["beat6m_rate"] == 0.0
           and "binom_z" not in row_v1)
    else:
        k_c, n_c = row_v1["beat6m_k"], row_v1["beat6m_n"]
        z_c = (k_c - 0.5 * 5) / math.sqrt(0.25 * 5)
        ok("screen cand cell row: binom math consistent (n=5 starts)",
           row_v1["beat6m_rate"] == round(k_c / n_c, 6)
           and row_v1["binom_z"] == round(z_c, 4)
           and row_v1["binom_p"] == round(
               2 * (1 - tl1._norm_cdf(abs(z_c))), 6))
    row_none = _screen_cell_w4({"cell_id": "SCREEN|ST-B-0000",
                                "kind": "cand", "cand": base,
                                "template": None})
    ok("screen cand cell row: gate=none+vol=none+stop=none faces carry "
       "zero counters (identity face)",
       row_none["stop_face"] == "none" and row_none["gate_face"] == "none"
       and row_none["vol_face"] == "none"
       and row_none["stop_fired"] == 0 and row_none["gate_zeroed"] == 0
       and row_none["vol_zeroed"] == 0)

    # [15] finalize math (pure): p95 line + strict survivor rule --
    # imported tl2 face (W2 identical frozen law, zero re-implementation)
    ok("finalize math import: W4 alias == tl2._finalize_math",
       _finalize_math is tl2._finalize_math)
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

    # [16] B7b contract: csv consumer keys subset of cell constructor keys
    constructor_keys = {"cell_id", "candidate_id", "family", "module",
                        "fn", "no_entries", "beat6m_k", "beat6m_n",
                        "beat6m_rate", "binom_z", "binom_p", "sharpe_full",
                        "dd_full", "n_trades", "n_entries", "stop_face",
                        "stop_fired", "gate_face", "gate_zeroed",
                        "vol_face", "vol_zeroed", "survives_screen"}
    ok("B7b contract: screen-csv consumer keys subset of constructor keys",
       set(csv_cols_screen_w4) <= constructor_keys)

    # [17] dual nulls W4 (prereg sec.3 s3; seed 20290500 binding)
    rng17 = np.random.default_rng(11)
    r17 = rng17.normal(0.0005, 0.01, 500)
    dn17 = _dual_nulls_w4(r17, 7)
    dn17b = _dual_nulls_w4(r17, 7)
    ok("dual nulls w4 deterministic (seed [20290500, cell])",
       dn17 == dn17b and dn17["B"] == 2000 and dn17["P"] == 2000
       and dn17["block"] == 20)
    dn17z = _dual_nulls_w4(np.zeros(100), 3)
    ok("dual nulls w4 degenerate zero face (CI [0,0], p=1)",
       dn17z["bootstrap_ci"] == [0.0, 0.0]
       and dn17z["signflip_p"] == 1.0
       and dn17z["ci_lower_positive"] is False)
    ok("dual nulls w4 math mirror == tl1 face at the W1 seed",
       _dual_nulls_w4(r17, 7, seed=tl1.SEED_UNC)
       == tl1._dual_nulls(r17, 7))
    ok("dual nulls w4 seed law: W4 face != W3 default-seed face "
       "(seed binding differs, draws differ)",
       dn17 != tl3._dual_nulls_w3(r17, 7))

    # [18] judge cell machinery in-process (synthetic dual-leg state;
    # [10] fixture family reused with the controlled 510300 vol path)
    framesJ = tl1._synth_prices(n_days=640, n_syms=4, seed=29)
    framesJ["510300"] = vol_frames["510300"].copy()
    PJ = tl1.build_panels(framesJ)
    stJ = pd.Series("GREEN", index=PJ["close"].index)
    nJ = len(PJ["close"].index)
    startsJ = {leg: {wname: [p for p in range(530, nJ - w, 25)]
                     for wname, w in tl1.WINDOWS.items()}
               for leg in ("L", "D")}
    passiveJ = {leg: {wname: {str(p): 0.05 for p in startsJ[leg][wname]}
                     for wname in tl1.WINDOWS} for leg in ("L", "D")}
    gsJ = tl3.gate_state_series(framesJ)
    vsJ = vol_state_series(framesJ)
    tl1._ST = {"prices_L": framesJ, "P_L": PJ,
               "idx_L": PJ["close"].index,
               "atr20_L": tl2.atr20_series(framesJ),
               "fundamental_ok_L": None,
               "prices_D": framesJ, "P_D": PJ,
               "idx_D": PJ["close"].index,
               "atr20_D": tl2.atr20_series(framesJ),
               "fundamental_ok_D": None,
               "starts": startsJ, "passive": passiveJ, "states": stJ,
               "grammar": g, "gate_state_L": gsJ, "gate_state_D": gsJ,
               "gate_meta_L": gsJ[2], "gate_meta_D": gsJ[2],
               "vol_state_L": vsJ, "vol_state_D": vsJ,
               "vol_meta_L": vsJ[2], "vol_meta_D": vsJ[2]}
    cellJ = {"cell_id": "JUDGE|ST-B-0000", "candidate_id": "ST-B-0000",
             "i": 3, "cand": base, "template": None}
    rowJ = _judge_cell_w4(cellJ)
    rowJ2 = _judge_cell_w4(cellJ)
    ok("judge cell: legs L/D present + determinism (double-run equal)",
       set(rowJ["legs"]) == {"L", "D"}
       and json.dumps(rowJ, sort_keys=True, default=str)
       == json.dumps(rowJ2, sort_keys=True, default=str))
    ok("judge cell: window-grid beat + x2 faces per leg + gate+vol "
       "counters",
       all(set(rowJ["legs"][lg]["beat"]) == set(tl1.WINDOWS)
           and set(rowJ["legs"][lg]["beat_x2"]) == set(tl1.WINDOWS)
           and "sharpe_full_x2" in rowJ["legs"][lg]
           and "stop_fired_x2" in rowJ["legs"][lg]
           and "gate_zeroed" in rowJ["legs"][lg]
           and "gate_zeroed_x2" in rowJ["legs"][lg]
           and "vol_zeroed" in rowJ["legs"][lg]
           and "vol_zeroed_x2" in rowJ["legs"][lg]
           for lg in ("L", "D")))
    segsJ = rowJ["legs"]["L"]["regime_start_windows"]
    n_starts_J = sum(len(startsJ["L"][w]) for w in tl1.WINDOWS)
    ok("judge cell: regime segments partition the complete windows "
       "(GREEN->bull)",
       sum(segsJ.values()) == n_starts_J
       and segsJ["bull"] == n_starts_J)
    ok("judge cell: dual nulls seed law [20290500, i]",
       rowJ["dual_nulls"] == _dual_nulls_w4(rowJ["legL_daily_returns"], 3))
    segL = rowJ["legs"]["L"]["regime_start_windows"]
    segD = rowJ["legs"]["D"]["regime_start_windows"]
    ok("judge cell: n_eff == bear+bull+chop sum across BOTH legs; "
       "sufficiency consistent",
       rowJ["n_eff_start_windows"]
       == (segL["bull"] + segL["bear"] + segL["chop"]
           + segD["bull"] + segD["bear"] + segD["chop"])
       and rowJ["sample_sufficient"] is False)
    ok("judge cell: descriptive + crisis + flip columns wired (none "
       "faces -> null flip columns)",
           "descriptive" in rowJ and "crisis_days_gt8pct" in rowJ
           and rowJ["crisis_days_gt8pct"] >= 0
           and "clause_ann_pos" in rowJ["descriptive"]
           and rowJ["stop_face"] == "none" and rowJ["gate_face"] == "none"
           and rowJ["vol_face"] == "none"
           and rowJ["gate_flip_days_legL"] is None
           and rowJ["vol_flip_days_legL"] is None)
    ok("judge cell: stop=none disclosure = zero-face",
       rowJ["stop_disclosure"]["stop_face"] == "none"
       and rowJ["stop_disclosure"]["n_trigger_events"] == 0)
    candV = dict(base, candidate_id="ST-B-0002",
                 axis=[*base["axis"][:4], "p3", "bull", "calm"])
    cellV = {"cell_id": "JUDGE|ST-B-0002", "candidate_id": "ST-B-0002",
             "i": 5, "cand": candV, "template": None}
    rowV = _judge_cell_w4(cellV)
    sdV = rowV["stop_disclosure"]
    ok("judge cell: p3+bull+calm face structurally complete (stop+gate+"
       "vol disclosures; flip columns == panel meta counts)",
       sdV["stop_face"] == "p3" and sdV["n_trigger_events"] >= 0
       and (sdV["dev_mean"] is None or isinstance(sdV["dev_mean"], float))
       and rowV["legs"]["L"]["stop_fired"] >= 0
       and rowV["gate_face"] == "bull" and rowV["vol_face"] == "calm"
       and rowV["gate_flip_days_legL"] == gsJ[2]["flips_bull_face"]
       and rowV["vol_flip_days_legL"] == vsJ[2]["flips_calm_face"])

    # [19] judged-row consumer contract (B7b r297 law): judge-finalize
    # strips exactly the daily-returns series; finalize columns are
    # finalize-added (absent from the burn row by construction)
    ok("B7b contract: judge strip face = daily-returns only; finalize "
       "columns disjoint from the burn row",
       {"legL_daily_returns"} <= set(rowJ)
       and {"g1_prime_v2", "dsr", "g1_pass", "verdict", "family_pbo",
            "g2_registration_v2"}.isdisjoint(set(rowJ)))

    print(f"selftest: {ok_n - fails[0]}/{ok_n} PASS, "
          f"{fails[0]} FAIL")
    return 1 if fails[0] else 0


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
    return {"selftest": cmd_selftest, "status": cmd_status,
            "grammar": cmd_grammar, "generate": cmd_generate,
            "screen-prep": cmd_screen_prep,
            "screen-finalize": cmd_screen_finalize,
            "judge-prep": cmd_judge_prep,
            "judge-finalize": cmd_judge_finalize}[a.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
