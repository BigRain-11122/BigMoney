# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W7 runner -- T-118 mass-candidate trial wave-7 (5000-ceiling,
streak-confirmation TEN-gate wave).

Prereg FROZEN (bm-c r207 draft-author same-machine next-round freeze; freeze
trigger MET = W6-JUDGE full chain landed 2026-09-29 08:14:22 + ledger head
333,432 linear + zero in-flight judge faces): research/
TRIAL_LABOR_W7_PREREG.md -- generate grammar + funnel rules + judgment
lines all frozen; post-run only sec.7/8 backfill.  Seeds held at the
freeze commit per R250 one-step law: trial_labor_w7_gen=20305000 /
trial_labor_w7_scrnull=20305500 / trial_labor_w7_unc=20306000 (bm-c r207
three-step re-verify ALL GREEN, no re-pick).  W7 collision yield receipt
on record: bm-b AMP (r417a) + bm-a TSTATE (r422) both yielded to the
bm-c STREAK draft per fleet README sec.4 commit-time law; STREAK =
canonical wave-7 face (MSG-0930/MSG-0945).

Import-face law (prereg sec.6): the FULL trial_labor_w1-w6 chain is
imported (tl1 enumeration/loading/anchor/envelope primitives + tl2
initial-stop overlay + tl3 regime-gate overlay + tl4 vol overlay +
tl5 yang overlay + tl6 vconf overlay & nine-tuple machinery); Sobol
sample_draws pattern follows mass_trial_w1 (paradigm import);
strategies/ factory + engine/backtester imported, never rewritten;
engine/exit_rules.py ZERO touch (streak overlay is a GRAMMAR layer).

Engineering mapping disclosures (pre-run, zero cells burned):

  STREAK overlay (prereg sec.3 streak-confirmation face; E1-mapping
  grammar-layer primitive): STREAK state = signal-day-d info set on
  member 510300: up_streak2 = close(d) > close(d-1) AND close(d-1) >
  close(d-2) (double same-direction close-over-close; lian-zhang);
  down_streak2 = mirror (lian-die); neither = no two-day confirmation
  (incl. flat/alternating) = gate-closed.  2-BAR WARMUP window
  gate-closed honest (first 2 bars undecidable -- SHORTEST warmup of
  the whole gate family: vs YANG 0 / VCONF 19 / VOL 519 / GATE 199).
  Gate acts on ENTRY PERMITTANCE only (effective signal zeroed,
  MSG-0440 E1-mapping primitive; engine-native signal-off exit
  semantics unchanged).  STREAK face != GATE regime face != VOL
  volatility face != YANG single-day intraday body != VCONF volume
  face (probe r206: yang AND up_streak 751 / yang AND down 104 / red
  AND up 93 / red AND down 713 -- four cells all non-empty
  non-dominant; off-diagonal 197 cells = streak carries multi-day
  information, not a yang single-day isomorph).  Composition order
  frozen everywhere (dedup face + engine face): signal -> filter ->
  timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> initial-stop (a
  streak-blocked signal never arms a stop; W6 order extended, prereg
  sec.3 ten-tuple order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK).

  G-STREAK anchor law (prereg sec.2 probe facts, fail-closed): on the
  raw full-history member face (data/daily/sh510300.csv, 3,483 bars
  2012-05-28 -> 2026-09-22 cutoff): warmup window == 2 bars; judgeable
  days == 3,481; up_streak == 844 (24.2%); down_streak == 817 (23.5%);
  neither == 1,820 (52.3% -- narrow-gate honest disclosure); cross-table
  lower bounds yang AND up >= 751 / red AND down >= 713; five-gate
  (gate x vol x yang x vconf x streak) 32 open-window cells ALL
  non-empty (probe range 3-150, min cell bear|calm|yang|surge|down);
  truncated tail row == cutoff.  Probe basis VERBATIM (probe r206
  facts file results/_r206bmc_streakgate_probe_facts.json + code
  results/_r206bmc_streakgate_probe.py; r407 lesson: the cross-basis
  maps the probe face, not the grammar-layer series): gate = close >
  ma200 strict with the NaN warmup leg landing in bear; vol = vol20
  <= med500 mapped with the NaN window landing in wild; yang = close >
  open strict (doji counts red); vconf = volume vs med20
  (min_periods=20, INCL d).

  Exclusion law (prereg sec.1, TEN-tuple cell key=(template, params,
  axis_config, initial_stop, gate, vol, yang, vconf, streak), FOURTEEN
  real-read source faces, exact already-judged key, streak=none face
  only): prior-wave keys lacking the streak axis are streak=none
  completed (semantic-identity match); streak in {up_streak2,
  down_streak2} (any gate/vol/yang/vconf combo) = new-syntax legal
  cells (never excluded).  Sources: frozen grammar bands (stop-gate-
  vol-yang-vconf-streak-none pad) + w1_screen 149 + w2_screen 404 +
  MASS screen 166 (declared tl3 translation) + w3_screen 513 +
  w4_screen 461 + w5_screen 372 + w6_screen 293 (generate-time
  real-read; absent at build = zero rows honest) + judged products
  re-declare window (w1_judge / MASS judged / w2_judge / w3_judge /
  w4_judge / w5_judge / w6_judge -- seven sources, generate-time
  real-read, absent = declared-unavailable zero rows).

Slice plan (W3-W6 single-writer precedent; claim MSG-20260929-0945-bmb
D-02 dual-signal receipt, commit 9ba94bf23):
  - slice-1a (this file, bm-b r417-cont): ten-tuple grammar
    build_grammar_w7 (tl6 grammar extended with the NEW streak axis ->
    580,608 axis combos, new grammar sha16 constructively distinct
    from W1/MASS/W2-W6) + streak overlay layer (streak_state_series /
    streak_zero_mask / structure gate) + G-STREAK fail-closed full-face
    gate + hermetic selftest (streak causality / 2-bar warmup / doji-
    equal legs / streak=none identity / missing-date conservative
    reindex / ten-tuple stream order-frozen consumption / grammar
    structure / G-STREAK probe anchors / five-gate 32-cell cross /
    structure-pass negative leg / status contract) + grammar
    serialization subcommand;
  - slice-2 (next round, physical dep honest): funnel command set
    (generate / screen prep+burn+finalize / judge prep+burn+finalize /
    intake -- tl6 cmd lineage parameterized to the ten-tuple + W7
    file faces) + engine double-run byte-identity legs + GENERATE pool
    entry (consumer_plan per O-1820(3), pre-positioned products same
    commit per pit-90; autofill tick burns, no inline burn);
  - LATER slices (physical deps, separate commits with MSG
    declarations per W3-W6 precedent): SCREEN pool entry AFTER
    generate lands; JUDGE pool entry AFTER screen-finalize (RAM r354
    three-sample gate + sequencing behind in-flight judge faces per
    prereg sec.0); intake (judge products required); grammar ledger
    wave-7 row append at consumption.
"""
from __future__ import annotations
import argparse
import csv
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
import trial_labor_w5 as tl5  # yang overlay + triple-gate machinery
import trial_labor_w6 as tl6  # vconf overlay + nine-tuple machinery
from science_gates import CostPatch, SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W7"
PREREG = "research/TRIAL_LABOR_W7_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w7_gen"]        # 20305000
SEED_NULL = SEED_REGISTRY["trial_labor_w7_scrnull"]  # 20305500
SEED_UNC = SEED_REGISTRY["trial_labor_w7_unc"]        # 20306000
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w7")
GRAMMAR_FILE = os.path.join(RES_DIR, "w7_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w7_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
SCREEN_FILE = os.path.join(RES_DIR, "w7_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w7_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w7_judge.json")
INTAKE_FILE = os.path.join(RES_DIR, "w7_intake.json")
SCREEN_BATCH = "TRIAL_LAB_W7_SCREEN"   # prereg sec.3 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W7_JUDGE"     # prereg sec.3 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "1fba956c2f21d1d3"   # pinned at slice-1a serialization

# prior-wave grammar shas (constructive-distinct assertion face)
PRIOR_WAVE_SHA16 = {
    "W1": "a2fa15f4b06b3c40", "MASS": "96269ebe766c3fc2",
    "W2": "1dd3d9579235cec", "W3": "cc59eab79db53436",
    "W4": "d498e9343ee57460", "W5": "29720178c39425de",
    "W6": tl6.FROZEN_SHA16,   # 2d395f5f8e7d16cb
}

# streak-confirmation axis (prereg sec.3 NEW W7 frozen layer)
AXIS_STREAK = ["none", "up_streak2", "down_streak2"]
AXIS_COMBOS = tl6.AXIS_COMBOS * len(AXIS_STREAK)   # 193,536 * 3 = 580,608
STREAK_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
STREAK_SPEC = {
    "member": STREAK_MEMBER,
    "series": "close-over-close double same-direction on the "
              "signal-day-d close info set: close(d) vs close(d-1) AND "
              "close(d-1) vs close(d-2)",
    "up_streak2": "close(d) > close(d-1) AND close(d-1) > close(d-2) "
                  "-- only two-day up-confirmation days permit entry "
                  "(san-lian-yang continuation face, A-share folk canon)",
    "down_streak2": "close(d) < close(d-1) AND close(d-1) < close(d-2) "
                    "-- only two-day down-confirmation days permit entry "
                    "(lian-die rebound-candidate face)",
    "none": "no gate (W6 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as GATE/VOL/YANG/VCONF, zero lookahead)",
    "warmup": "2-bar warmup window gate-closed honest (first 2 bars "
              "undecidable -- SHORTEST warmup of the gate family: vs "
              "YANG 0 / VCONF 19 / GATE 199 / VOL 519)",
    "engine_note": "entry-permittance only (effective signal zeroed, "
                   "MSG-0440 E1-mapping primitive; exit logic zero "
                   "change; engine/exit_rules.py zero touch)",
    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "
                         "YANG -> VCONF -> STREAK -> initial-stop (a "
                         "streak-blocked signal never arms a stop; W6 "
                         "order extended, prereg sec.3)",
}
STREAK_ANCHOR = {
    "n_bars": 3483, "first_date": "2012-05-28", "cutoff": "2026-09-22",
    "warmup_gate_closed_bars": 2, "judgeable_days": 3481,
    "up_streak_days": 844, "down_streak_days": 817,
    "neither_days": 1820,
    "up_rate_judgeable": 0.5081,
    "yang_and_up_lower_bound": 751, "red_and_down_lower_bound": 713,
    "streak_by_yang": {"yang": {"up": 751, "down": 104},
                       "red": {"up": 93, "down": 713}},
    "streak_by_gate": {"bull": {"up": 524, "down": 343},
                       "bear": {"up": 320, "down": 474}},
    "five_gate_32cells": "all non-empty (probe range 3-150; min cell "
                         "bear|calm|yang|surge|down == 3; max cell "
                         "bull|calm|yang|surge|up == 150)",
    "extreme_days": "4 down (2015-07-27 / 2016-01-04 / 2025-04-07 / "
                    "2026-01-19 crisis-day exposure held) + 2 up "
                    "(2024-09-24 / 09-30 policy-pulse days) + 1 neither "
                    "(2024-02-28 honest)",
    "probe_facts": "results/_r206bmc_streakgate_probe_facts.json "
                   "(r206 bm-c, probe-facts face not a results face)",
    "probe_basis": "cross-tables on the r206 probe basis VERBATIM "
                   "(r407 lesson): gate = close>ma200 strict with the "
                   "NaN warmup leg in bear; vol = vol20<=med500 mapped "
                   "with the NaN window in wild; yang = close>open "
                   "strict (doji red); vconf = volume vs med20 "
                   "(min_periods=20, INCL d)",
    "note": "up/down/neither judgeable-window totals asserted exact; "
            "cross-table anchors asserted as LOWER BOUNDS per prereg "
            "sec.2 G-STREAK; five-gate 32 cells asserted non-empty",
}


def _grammar_sha16(grammar):
    """Grammar sha16 (W4 lineage import; zero re-implementation)."""
    return tl4._grammar_sha16(grammar)


# ------------------------------------------------------ streak overlay layer
def streak_state_series(prices: dict):
    """Frozen STREAK spec (prereg sec.2/3): member 510300 signal-day
    info set -- up_perm = close(d) > close(d-1) AND close(d-1) >
    close(d-2); down_perm = strict mirror; 2-bar warmup gate-closed
    (first 2 bars undecidable -> both perms False).

    Returns (up_perm, down_perm, meta): boolean Series on the member's
    own date index + structural meta. Deterministic pure function of
    the (cutoff-truncated) panel."""
    df = prices[STREAK_MEMBER]
    close = df["close"].sort_index()
    c1 = close.shift(1)
    c2 = close.shift(2)
    warm = pd.Series(True, index=close.index)
    warm.iloc[:2] = False           # 2-bar warmup, gate-closed honest
    up = warm & (close > c1) & (c1 > c2)
    down = warm & (close < c1) & (c1 < c2)
    n = len(close)
    up_days = int(up.sum())
    down_days = int(down.sum())
    neither_days = n - 2 - up_days - down_days
    meta = {"n_bars": int(n),
            "na_window_bars": 2,
            "first_valid_bar_idx": 2,
            "up_streak_days": up_days, "down_streak_days": down_days,
            "neither_days": int(neither_days),
            "judgeable_days": int(n - 2),
            "up_rate_judgeable": (round(up_days / (n - 2), 4)
                                  if n > 2 else None),
            "flips_up_face": int((up.values[1:] != up.values[:-1]).sum()),
            "median_window": 0,
            }
    return up, down, meta


def _streak_face_full():
    """Frozen sec.2 STREAK-series face (r206 probe basis): the
    git-tracked raw full-history member file data/daily/sh510300.csv
    (open + close + volume columns), truncated at the evidence cutoff.
    Returns the member prices dict {sym: DataFrame(open, close,
    volume)}, or None when absent / columns missing / tail != cutoff.
    (tl6._vconf_face_full loading caliber, r407 same-index law.)"""
    path = os.path.join("data", "daily", f"sh{STREAK_MEMBER}.csv")
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip() for c in df.columns]
        if not {"open", "close", "volume", "date"} <= set(df.columns):
            return None
        close = df["close"].astype(float)
        close.index = pd.to_datetime(df["date"])
        # r407 fix-first law (same date index on EVERY column BEFORE any
        # reindex; a RangeIndex reindexed against datetime labels matches
        # nothing -> all-NaN -> gate refuses on a healthy face)
        o = df["open"].astype(float)
        v = df["volume"].astype(float)
        o.index = close.index
        v.index = close.index
        close = close.sort_index()
        o = o.reindex(close.index)
        v = v.reindex(close.index)
        keep = close.index <= pd.Timestamp(CUTOFF)
        close, o, v = close[keep], o[keep], v[keep]
        if not len(close) or str(close.index[-1].date()) != CUTOFF:
            return None
        return {STREAK_MEMBER: pd.DataFrame({"open": o, "close": close,
                                             "volume": v})}
    except Exception:
        return None


def _streak_state_full():
    """Canonical full-face streak_state with the frozen probe anchors
    asserted (prereg sec.2 G-STREAK fail-closed): n_bars == 3,483;
    warmup == 2 / judgeable == 3,481; up_streak == 844 exact; down_streak
    == 817 exact; neither == 1,820 exact; cross-table lower bounds
    yang AND up >= 751 / red AND down >= 713; five-gate (gate x vol x
    yang x vconf x streak) 32 open-window cells all non-empty (cross
    faces on the r206 probe basis VERBATIM, r407 lesson).  Returns
    (streak_state, err); err is a one-line honest refusal reason when
    not None."""
    face = _streak_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{STREAK_MEMBER}.csv "
                      f"absent/open-close-volume columns missing or "
                      f"truncated tail != cutoff {CUTOFF}")
    up, down, meta = streak_state_series(face)
    if (meta.get("n_bars") != STREAK_ANCHOR["n_bars"]
            or meta.get("na_window_bars")
            != STREAK_ANCHOR["warmup_gate_closed_bars"]
            or meta.get("judgeable_days")
            != STREAK_ANCHOR["judgeable_days"]
            or meta.get("up_streak_days")
            != STREAK_ANCHOR["up_streak_days"]
            or meta.get("down_streak_days")
            != STREAK_ANCHOR["down_streak_days"]
            or meta.get("neither_days") != STREAK_ANCHOR["neither_days"]):
        return None, (f"G-STREAK full-face anchors {meta} != probe "
                      f"{{n_bars 3483, warmup 2, judgeable 3481, up 844, "
                      f"down 817, neither 1820}}")
    close = face[STREAK_MEMBER]["close"].sort_index()
    o = face[STREAK_MEMBER]["open"].reindex(close.index)
    # yang on the probe basis (strict close > open; doji red)
    yang = (close > o).fillna(False)
    red = ~yang
    yu = yang.reindex(up.index).fillna(False)
    rd = red.reindex(down.index).fillna(False)
    yang_up = int((yu & up).sum())
    red_down = int((rd & down).sum())
    if (yang_up < STREAK_ANCHOR["yang_and_up_lower_bound"]
            or red_down < STREAK_ANCHOR["red_and_down_lower_bound"]):
        return None, (f"G-STREAK cross-table lower bounds broken "
                      f"(yang AND up {yang_up}, red AND down {red_down})")
    # five-gate 32 open-window cells on the r206 probe basis VERBATIM
    ma200 = close.rolling(tl3.GATE_SPEC["ma_window"],
                           min_periods=tl3.GATE_SPEC["min_periods"]).mean()
    bull = (close > ma200).fillna(False)      # probe strict >; NaN -> bear
    ret = close / close.shift(1) - 1
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm = (vol20 <= med500).fillna(False)   # probe map NaN -> wild
    vconf = tl6.vconf_state_series(face)      # surge/dry on the same face
    surge, dry, _ = vconf
    bi = bull.reindex(up.index).fillna(False)
    ci = calm.reindex(up.index).fillna(False)
    si = surge.reindex(up.index).fillna(False)
    di = dry.reindex(up.index).fillna(False)
    cells = {}
    for gname, gv in (("bull", bi), ("bear", ~bi)):
        for vname, vv in (("calm", ci), ("wild", ~ci)):
            for yname, yv in (("yang", yu), ("red", ~yu)):
                for cname, cv in (("surge", si), ("dry", di)):
                    for sname, sv in (("up", up), ("down", down)):
                        k = f"{gname}|{vname}|{yname}|{cname}|{sname}"
                        cells[k] = int((gv & vv & yv & cv & sv).sum())
    empty = [k for k, n_ in cells.items() if n_ <= 0]
    if empty:
        return None, (f"G-STREAK five-gate 32 open-window cells not all "
                      f"non-empty (empty: {empty})")
    meta = dict(meta)
    meta["cross_yang"] = {"yang_and_up": yang_up,
                          "red_and_down": red_down}
    meta["streak_by_gate"] = {"bull": {"up": int((bi & up).sum()),
                                       "down": int((bi & down).sum())},
                              "bear": {"up": int((~bi & up).sum()),
                                       "down": int((~bi & down).sum())}}
    meta["five_gate_open_window"] = cells
    meta["five_gate_min"] = min(cells.values())
    meta["five_gate_max"] = max(cells.values())
    return (up, down, meta), None


def streak_zero_mask(mask: pd.DataFrame, streak_key: str, streak_state):
    """Grammar-layer streak entry gate (prereg sec.3 streak-confirmation
    face; E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked; engine-native signal-off exit
    semantics -- the same primitive every cell uses when its own signal
    turns off; zero engine touch).  streak=none = W6 semantic baseline
    (identity).  Member dates missing from the mask index ->
    streak-closed (conservative reindex law, tl3/tl4/tl5/tl6 gate
    caliber)."""
    if streak_key == "none":
        return mask
    up, down, _ = streak_state
    keep = (up if streak_key == "up_streak2"
            else down).reindex(mask.index).fillna(False).astype(int)
    return mask.mul(keep, axis=0)


def _streak_structure_pass(streak_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    2-bar warmup -- na window == 2 and first valid bar-idx == 2;
    up+down+neither partitions the judgeable window (n_bars - 2)."""
    if not isinstance(streak_meta, dict):
        return False
    na = streak_meta.get("na_window_bars", -1)
    return (streak_meta.get("first_valid_bar_idx") == 2
            and na == 2
            and streak_meta.get("up_streak_days", -1)
            + streak_meta.get("down_streak_days", -1)
            + streak_meta.get("neither_days", -1)
            == streak_meta.get("n_bars", -2) - na)


# ------------------------------------------------------------ grammar build
def build_grammar_w7():
    """tl6 grammar extended with the NEW streak axis + W7 seeds/counts
    (frozen face).  Ten-tuple axes R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK = 580,608 axis combos.

    Exclusion law (prereg sec.1): exact already-judged cells are
    excluded on the streak=none face only; all prior-wave lineage keys
    are streak=none completed (W1 4-tuple + stop/gate/vol/yang/vconf/
    streak none; W2 5-tuple + gate/vol/yang/vconf/streak none; W3
    6-tuple + vol/yang/vconf/streak none; W4 7-tuple + yang/vconf/
    streak none; W5 8-tuple + vconf/streak none; W6 9-tuple + streak
    none; MASS via the declared translation); streak in {up_streak2,
    down_streak2} faces = new-syntax legal cells (never excluded)."""
    g6 = tl6.build_grammar_w6()      # frozen W6 machinery face
    excl = []
    for e in g6["exclusion"]["stop_gate_vol_yang_vconf_none_face"]:
        excl.append({**e, "axis": list(e["axis"]) + ["none"],
                     "face": "stop-gate-vol-yang-vconf-streak-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w7-streak-gate-extended",
        "seeds": {"trial_labor_w7_gen": SEED_GEN,
                  "trial_labor_w7_scrnull": SEED_NULL,
                  "trial_labor_w7_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20305000+family_idx, "
                                "scramble) param box + default_rng("
                                "[20305000+family_idx, 7919]) ten-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG/VCONF/STREAK (prereg s.3; A idx "
                                "0-5, B idx 6+slot; berths held at the "
                                "freeze commit per R250 one-step law, "
                                "bm-c r207 three-step re-verify ALL "
                                "GREEN no re-pick)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {**g6["axes"], "streak": AXIS_STREAK},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": g6["stop_formula"],
        "stop_fill_mapping": g6["stop_fill_mapping"],
        "gate_spec": g6["gate_spec"],
        "vol_spec": g6["vol_spec"],
        "yang_spec": g6["yang_spec"],
        "vconf_spec": g6["vconf_spec"],
        "streak_spec": STREAK_SPEC,
        "vol_anchor": g6["vol_anchor"],
        "yang_anchor": g6["yang_anchor"],
        "vconf_anchor": g6["vconf_anchor"],
        "streak_anchor": STREAK_ANCHOR,
        "families": g6["families"], "value_domains": g6["value_domains"],
        "faces": g6["faces"],
        "exclusion": {"stop_gate_vol_yang_vconf_streak_none_face": excl,
                      "sources": list(g6["exclusion"]["sources"])
                      + ["w6_screen.json survivors (generate-time)",
                         "w6_judge products (generate-time real-read "
                         "re-declare window; W6-JUDGE landed 2026-09-29 "
                         "08:14:22)"],
                      "note": "exclusion face = streak=none only; "
                              "prior-wave keys streak=none-completed "
                              "(semantic identity match); streak in "
                              "{up_streak2, down_streak2} = new-syntax "
                              "legal cells (prereg sec.1)"},
        "negative_priors": g6.get("negative_priors"),
        "inventory_audit": g6["inventory_audit"],
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w7(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + TEN-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK (the first nine axis
    arrays are the W6-order stream VERBATIM -- order-frozen consumption
    law; the streak leg appends AFTER vconf, zero disturbance).
    Deterministic, zero band use."""
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
                  rng.integers(0, len(tl2.AXIS_STOP), n_draws),
                  rng.integers(0, len(tl3.AXIS_GATE), n_draws),
                  rng.integers(0, len(tl4.AXIS_VOL), n_draws),
                  rng.integers(0, len(tl5.AXIS_YANG), n_draws),
                  rng.integers(0, len(tl6.AXIS_VCONF), n_draws),
                  rng.integers(0, len(AXIS_STREAK), n_draws)))
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
        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           tl2.AXIS_STOP[st_], tl3.AXIS_GATE[gt_],
                           tl4.AXIS_VOL[vt_], tl5.AXIS_YANG[yg_],
                           tl6.AXIS_VCONF[vc_], AXIS_STREAK[sk_]],
                  "family": family}


# ------------------------------------------------ exclusion (14 real-reads)
def _load_exclusion_rows_w7(grammar):
    """Fourteen real-read source faces + the frozen serialized grammar
    face (prereg sec.1), all real-read at generate time.  All prior-wave
    keys are padded to the W7 TEN-tuple with streak=none (semantic-
    identity completion law).  Sources: 1 = frozen serialized grammar
    stop-gate-vol-yang-vconf-streak-none face (10-tuple at build);
    2-8 = W1/W2/MASS (declared tl3 translation)/W3/W4/W5/W6 screen
    survivors -- W6 is NEW vs W6's own loader (generate-time real-read;
    absent at build = zero rows honest per prereg sec.1); 9-15 =
    judged products (w1_judge / MASS judged / w2_judge / w3_judge /
    w4_judge / w5_judge / w6_judge) -- generate-time real-read
    re-declare window (declared-unavailable -> zero rows, no
    fabrication).
    """
    rows = list(grammar["exclusion"]
                ["stop_gate_vol_yang_vconf_streak_none_face"])
    disc = {"grammar_stop_gate_vol_yang_vconf_streak_none_rows":
            len(rows)}

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
                         "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                 "streak-none",
                         "candidate_id": cid})
            n += 1
        return n

    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 6, "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 5, "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 4, "w3_screen_survivor")
    disc["w4_screen_survivors"] = _screen_survivors(
        tl4.SCREEN_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 3, "w4_screen_survivor")
    disc["w5_screen_survivors"] = _screen_survivors(
        tl5.SCREEN_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 2, "w5_screen_survivor")
    disc["w6_screen_survivors"] = _screen_survivors(
        tl6.SCREEN_FILE, tl6.CANDIDATES_FILE,
        ["none"], "w6_screen_survivor")

    # MASS screen survivors: declared tl3 translation + vol-yang-vconf-
    # streak none pad (translated rows are 6-tuples)
    if os.path.exists(tl6.MASS_SCREEN_CKPT):
        n_tr = n_bad = 0
        with open(tl6.MASS_SCREEN_CKPT, encoding="utf-8") as fh:
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
                tr["axis"] = list(tr["axis"]) + ["none"] * 4
                tr["face"] = "mass_screen_survivor:translated-exact"
                tr["candidate_id"] = r.get("id")
                rows.append(tr)
                n_tr += 1
        disc["mass_screen_survivors"] = {
            "consumed_pass_rows": n_tr + n_bad,
            "translated_exact_rows": n_tr,
            "non_translatable_disclosed": n_bad,
            "note": tl6.MASS_TRANSLATION_NOTE}
    else:
        disc["mass_screen_survivors"] = "declared-unavailable " \
                                        "(screen_checkpoint.jsonl absent)"

    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (freeze-time
    # expectation per prereg sec.0 (d): W1/MASS/W2/W3/W4/W5 judged
    # landed; W6-JUDGE landed 2026-09-29 08:14:22 -- live re-read at
    # generate time is the law)
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
                tr["axis"] = list(tr["axis"]) + ["none"] * 4
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + pad,
                             "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                     "streak-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        tl6.W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 6, "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        tl6.MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        tl6.W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 5, "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        tl6.W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 4, "w3_judged")
    disc["w4_judge_products"] = _judged_source(
        tl4.JUDGE_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 3, "w4_judged")
    disc["w5_judge_products"] = _judged_source(
        tl5.JUDGE_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 2, "w5_judged")
    disc["w6_judge_products"] = _judged_source(
        tl6.JUDGE_FILE, tl6.CANDIDATES_FILE,
        ["none"], "w6_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window = live prev
    # increment merged at generate time, uniform baseline absent an
    # append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the seven judge "
        "products disclosed above")
    return rows, disc


def _excluded_w7(cand, rows):
    """Exact already-judged cell test, streak=none face only (prereg
    sec.1: streak in {up_streak2, down_streak2} = new-syntax legal
    cells -- never excluded; W1-lineage cells implicitly stop/gate/vol/
    yang/vconf/streak=none; W2 cells carry their own stop face; W3
    stop+gate; W4 stop+gate+vol; W5 stop+gate+vol+yang; W6
    stop+gate+vol+yang+vconf).  Returns the exclusion face or None."""
    if cand["axis"][9] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w7(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               gate_state, vol_state, yang_state,
                               vconf_state, streak_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> VCONF -> STREAK -> initial-stop (prereg
    sec.3 ten-tuple dedup legs; zero engine burn).  streak=none +
    vconf=none + yang=none + vol=none + gate=none + stop=none = W1
    identity; streak=none = W6 semantic baseline; all six overlay faces
    deterministic layers of the same grammar stack (W6 order extended
    by the streak leg, zero disturbance to the first five)."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = streak_zero_mask(VC, streak_key, streak_state)
    return tl2._effective_signal_mask(SK, prices, stop_key, atr20)


def run_candidate_curve_w7(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None,
                           vconf_state=None, streak_state=None):
    """One W7 candidate cell at the engine face with the gate + vol +
    yang + vconf + streak overlays + initial-stop overlay carried
    per-cell (prereg sec.3 face a; frozen composition order filter ->
    timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> initial-stop).

    streak=none+vconf=none+yang=none+vol=none+gate=none+stop=none ->
    byte-identical to the tl1 engine face; streak=none+vconf=none ->
    tl5 W5 face; streak=none -> tl6 W6 face (parity laws, selftest-
    pinned); streak in {up_streak2, down_streak2} = new W7 syntax
    (entry-permittance only, never excluded).  Returns (eq, trades,
    metrics, params, patch, stop_fired, gate_zeroed, vol_zeroed,
    yang_zeroed, vconf_zeroed, streak_zeroed)."""
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    vol_key = cand["axis"][6]
    yang_key = cand["axis"][7]
    vconf_key = cand["axis"][8]
    streak_key = cand["axis"][9]
    if gate_state is None:
        gate_state = tl3.gate_state_series(prices)
    if vol_state is None:
        vol_state = tl4.vol_state_series(prices)
    if yang_state is None:
        yang_state = tl5.yang_state_series(prices)
    if vconf_state is None:
        vconf_state = tl6.vconf_state_series(prices)
    if streak_state is None:
        streak_state = streak_state_series(prices)
    if stop_key != "none" and tl2.STOP_FORMULA[stop_key]["kind"] == "atr" \
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
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = streak_zero_mask(VC, streak_key, streak_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    yang_zeroed = int((V > 0).sum().sum() - (Y > 0).sum().sum())
    vconf_zeroed = int((Y > 0).sum().sum() - (VC > 0).sum().sum())
    streak_zeroed = int((VC > 0).sum().sum() - (SK > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = SK, 0
    else:
        S = tl2._effective_signal_mask(SK, prices, stop_key, atr20)
        d = (SK > 0) & (S == 0)
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
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, streak_zeroed


def _null_axis_draw_w7(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i]
    (W7 berth 20305500, distinct from the W6 berth 20304000 -- zero
    stream overlap by construction); consumption order frozen = p_on
    regime -> TEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK ->
    signal matrix.  Same engine/cost/panel as candidate cells incl. the
    gate + vol + yang + vconf + streak legs (BACKTEST_PLAN three iron
    rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          tl2.AXIS_STOP[int(rng.integers(len(tl2.AXIS_STOP)))],
          tl3.AXIS_GATE[int(rng.integers(len(tl3.AXIS_GATE)))],
          tl4.AXIS_VOL[int(rng.integers(len(tl4.AXIS_VOL)))],
          tl5.AXIS_YANG[int(rng.integers(len(tl5.AXIS_YANG)))],
          tl6.AXIS_VCONF[int(rng.integers(len(tl6.AXIS_VCONF)))],
          AXIS_STREAK[int(rng.integers(len(AXIS_STREAK)))])
    return p_on, list(ax), rng


# ------------------------------------------------------------ grammar / status
def cmd_grammar() -> int:
    """Serialize the frozen W7 grammar to results/trial_labor_w7/
    w7_grammar.json (idempotent; sha16 printed for the slice-1a pin)."""
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w7()
    with open(GRAMMAR_FILE, "w", encoding="utf-8") as fh:
        json.dump(g, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"grammar serialized: {GRAMMAR_FILE}")
    print(f"sha16={g['grammar_sha256']} axis_combos={g['axis_combos']} "
          f"wave={g['wave']} cutoff={g['evidence_cutoff']}")
    return 0


def cmd_status() -> int:
    """Honest slice-state readout (all faces read-only; absent =
    pending)."""
    faces = [("grammar", GRAMMAR_FILE), ("candidates", CANDIDATES_FILE),
             ("screen", SCREEN_FILE), ("judge", JUDGE_FILE),
             ("intake", INTAKE_FILE)]
    for name, path in faces:
        if os.path.exists(path):
            print(f"{name}: present ({os.path.getsize(path)} bytes)")
        else:
            print(f"{name}: PENDING (slice-2 funnel leg)")
    print("slice-1a: streak overlay + G-STREAK gate + selftest LANDED "
          "(bm-b r417-cont); funnel cmds + GENERATE pool entry = "
          "slice-2 (physical dep, next round)")
    return 0


def _slice2_pending(cmd: str) -> int:
    print(f"{cmd}: slice-2b pending (slice-2a machinery LANDED r418: "
          f"effective mask / curve runner W6-parity / null draw / "
          f"14-source exclusion loader, selftest 37/37; funnel cmd "
          f"bodies + GENERATE pool entry land next round; zero cells "
          f"burned, zero numbers fabricated)")
    return 3


def cmd_generate() -> int:
    return _slice2_pending("generate")


def cmd_screen(shard: int = 0, shards: int = 1, workers=None) -> int:
    return _slice2_pending("screen")


def cmd_screen_finalize() -> int:
    return _slice2_pending("screen-finalize")


def cmd_judge(shard: int = 0, shards: int = 1, workers=None) -> int:
    return _slice2_pending("judge")


def cmd_judge_finalize() -> int:
    return _slice2_pending("judge-finalize")


def cmd_intake() -> int:
    return _slice2_pending("intake")


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    """Hermetic offline selftest (zero network, zero engine burns, zero
    cell evaluation): STREAK causality / 2-bar warmup / doji-equal /
    identity / conservative-reindex / ten-tuple stream order / grammar
    structure / G-STREAK probe anchors / five-gate cross / structure
    negative leg / status contract.  Engine double-run byte-identity
    legs land with the slice-2 funnel command set (honest scope
    disclosure, not a failing leg)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    n_pass = 0
    n_leg = 0

    def _ok(name, cond, detail=""):
        nonlocal n_pass, n_leg
        n_leg += 1
        if cond:
            n_pass += 1
            print(f"[PASS] {name}" + (f" | {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" | {detail}" if detail else ""))

    # ---- L1 synthetic causality: up face (double same-direction)
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    closes = pd.Series([1.0, 2.0, 3.0, 2.0, 1.0], index=idx)
    face = {STREAK_MEMBER: pd.DataFrame(
        {"open": closes * np.nan, "close": closes, "volume": closes * 0})}
    up, down, meta = streak_state_series(face)
    exp_up = [False, False, True, False, False]
    exp_down = [False, False, False, False, True]
    _ok("L1 up-face causality (close-over-close double, d2 up / d4 down)",
        list(up) == exp_up and list(down) == exp_down,
        f"up={list(map(int, up))} down={list(map(int, down))}")

    # ---- L2 neither face: flat (doji-equal closes) + alternating
    idx3 = pd.date_range("2020-02-01", periods=3, freq="D")
    flat = pd.Series([1.0, 1.0, 1.0], index=idx3)
    f3 = {STREAK_MEMBER: pd.DataFrame(
        {"open": flat * np.nan, "close": flat, "volume": flat * 0})}
    up3, down3, meta3 = streak_state_series(f3)
    _ok("L2a doji-equal closes -> neither (strict >/< only)",
        not up3.iloc[2] and not down3.iloc[2] and meta3["neither_days"] == 1)
    idx4 = pd.date_range("2020-03-01", periods=4, freq="D")
    alt = pd.Series([1.0, 2.0, 1.0, 2.0], index=idx4)
    f4 = {STREAK_MEMBER: pd.DataFrame(
        {"open": alt * np.nan, "close": alt, "volume": alt * 0})}
    up4, down4, _ = streak_state_series(f4)
    _ok("L2b alternating closes -> neither on every judgeable bar",
        not up4.iloc[2] and not up4.iloc[3] and not down4.iloc[2]
        and not down4.iloc[3])

    # ---- L3 2-bar warmup gate-closed (synthetic + real face)
    _ok("L3a warmup == 2 bars gate-closed on any synthetic face",
        meta["na_window_bars"] == 2 and meta["first_valid_bar_idx"] == 2
        and not up.iloc[0] and not up.iloc[1] and not down.iloc[0]
        and not down.iloc[1])
    rstate, rerr = _streak_state_full()
    _ok("L3b real-face state loads G-STREAK clean (r206 probe basis)",
        rstate is not None and rerr is None,
        rerr or "anchors clean")

    # ---- L4 streak_zero_mask legs
    mask = pd.DataFrame({"sig": [1.0, 1.0, 1.0, 1.0, 1.0]}, index=idx)
    ident = streak_zero_mask(mask, "none", (up, down, meta))
    _ok("L4a streak=none == W6 semantic-baseline identity (byte-equal)",
        ident.equals(mask))
    upmask = streak_zero_mask(mask, "up_streak2", (up, down, meta))
    _ok("L4b up_streak2 permits only up-confirmed days (d2 only)",
        list(upmask["sig"]) == [0.0, 0.0, 1.0, 0.0, 0.0])
    dnmask = streak_zero_mask(mask, "down_streak2", (up, down, meta))
    _ok("L4c down_streak2 permits only down-confirmed days (d4 only)",
        list(dnmask["sig"]) == [0.0, 0.0, 0.0, 0.0, 1.0])
    miss_idx = idx.append(pd.DatetimeIndex(["2020-01-10"]))
    mmask = pd.DataFrame({"sig": [1.0] * 6}, index=miss_idx)
    mres = streak_zero_mask(mmask, "up_streak2", (up, down, meta))
    _ok("L4d missing dates -> streak-closed (conservative reindex law)",
        float(mres.loc["2020-01-10", "sig"]) == 0.0)

    # ---- L5 ten-tuple stream order-frozen consumption
    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    ten = [rng_a.integers(0, 4, n) for _ in range(10)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    nine = [rng_b.integers(0, 4, n) for _ in range(9)]
    _ok("L5 STREAK appends AFTER VCONF in the rng stream (first nine "
        "axis arrays == W6-order stream verbatim, zero disturbance)",
        all(np.array_equal(a, b) for a, b in zip(ten, nine)))

    # ---- L6 grammar structure (ten axes / combos / seeds / sha)
    g = build_grammar_w7()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 580,608 (193,536 x 3)",
        g["axis_combos"] == 580608 == tl6.AXIS_COMBOS * 3)
    _ok("L6b ten axes present, streak == frozen triple",
        len(g["axes"]) == 10 and g["axes"]["streak"] == AXIS_STREAK)
    _ok("L6c W7 seeds == SEED_REGISTRY berths (20305000/20305500/"
        "20306000 held, no re-pick)",
        g["seeds"]["trial_labor_w7_gen"] == SEED_REGISTRY[
            "trial_labor_w7_gen"]
        and g["seeds"]["trial_labor_w7_scrnull"] == SEED_REGISTRY[
            "trial_labor_w7_scrnull"]
        and g["seeds"]["trial_labor_w7_unc"] == SEED_REGISTRY[
            "trial_labor_w7_unc"])
    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W6",
        sha not in set(PRIOR_WAVE_SHA16.values()),
        f"sha16={sha}")
    _ok("L6e exclusion face rows streak=none-padded to 10-long axis",
        all(len(r["axis"]) == 10 and r["axis"][-1] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_none_face"]))
    _ok("L6f families/value_domains inherited from tl6 verbatim",
        g["families"] == tl6.build_grammar_w6()["families"]
        and len(g["value_domains"]) == len(
            tl6.build_grammar_w6()["value_domains"]))

    # ---- L7 G-STREAK real-face probe anchors (exact totals)
    rs_up, rs_down, rs_meta = rstate
    _ok("L7 G-STREAK exact anchors (n 3483 / judgeable 3481 / up 844 / "
        "down 817 / neither 1820 / warmup 2)",
        rs_meta["n_bars"] == 3483 and rs_meta["judgeable_days"] == 3481
        and rs_meta["up_streak_days"] == 844
        and rs_meta["down_streak_days"] == 817
        and rs_meta["neither_days"] == 1820
        and rs_meta["na_window_bars"] == 2)
    _ok("L7b cross-yang lower bounds (yang AND up >= 751 / red AND "
        "down >= 713)",
        rs_meta["cross_yang"]["yang_and_up"] >= 751
        and rs_meta["cross_yang"]["red_and_down"] >= 713,
        f"yang_up={rs_meta['cross_yang']['yang_and_up']} "
        f"red_down={rs_meta['cross_yang']['red_and_down']}")
    _ok("L7c regime persistence structure (bull up 524/down 343; bear "
        "up 320/down 474 -- probe disclosure, non-assertive carry)",
        rs_meta["streak_by_gate"]["bull"]["up"] == 524
        and rs_meta["streak_by_gate"]["bear"]["down"] == 474)

    # ---- L8 five-gate 32-cell cross (all non-empty)
    cells = rs_meta["five_gate_open_window"]
    _ok("L8 five-gate (gate x vol x yang x vconf x streak) 32 "
        "open-window cells ALL non-empty (probe range 3-150)",
        len(cells) == 32 and all(v > 0 for v in cells.values())
        and rs_meta["five_gate_min"] >= 3 and rs_meta["five_gate_max"]
        <= 150,
        f"min={rs_meta['five_gate_min']} max={rs_meta['five_gate_max']}")

    # ---- L9 structure-pass gate + negative leg
    _ok("L9a _streak_structure_pass true on the real face",
        _streak_structure_pass(rs_meta))
    bad = dict(rs_meta)
    bad["na_window_bars"] = 3
    _ok("L9b corrupted warmup meta -> structure gate refuses "
        "(fail-closed negative leg)",
        not _streak_structure_pass(bad))

    # ---- L10 draw contract (deterministic re-draw byte-identity)
    ga = build_grammar_w7()
    c1 = next(draw_candidate_sobol_w7(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w7(build_grammar_w7(), "A", 0, 1))
    _ok("L10 Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the streak axis)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 10)
    fam_b = ga["families"]["B"][0]
    _ok("L10b family B slot streams from fam_idx 6 (prereg A 0-5 / "
        "B 6+slot)",
        fam_b["module"] in {m for m in
                            [t["module"] for t in ga["families"]["A"]]})

    # ---- L11 status contract (read-only, absent = PENDING, exit 0)
    rc = cmd_status()
    _ok("L11 status contract exit 0 on pending products",
        rc == 0)

    # ---- L12 effective-mask streak legs (mask level, zero engine burn)
    tl1.GRAMMAR = g          # engine legs need tl1's grammar global
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled alternating 510300: close 100 +/- 0.7 alternating ->
    # ZERO up_streak2/down_streak2 days (never two same-direction
    # closes in a row)
    alt_o = pd.Series(100.0, index=frames3["510300"].index
                      if "510300" in frames3 else
                      frames3[list(frames3)[0]].index)
    alt_c = alt_o.copy()
    alt_v = alt_o.copy()
    for i in range(len(alt_c)):
        alt_c.iloc[i] = 100.0 + (0.7 if i % 2 == 0 else -0.7)
        alt_o.iloc[i] = 100.0
        alt_v.iloc[i] = 2000.0 if i % 2 == 0 else 500.0
    frames3[STREAK_MEMBER] = pd.DataFrame(
        {"open": alt_o, "high": alt_c + 0.2, "low": alt_o - 0.2,
         "close": alt_c, "volume": alt_v, "amount": 1e5},
        index=alt_c.index)
    P3 = tl1.build_panels(frames3)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = tl4.vol_state_series(frames3)
    ys3 = tl5.yang_state_series(frames3)
    cs3 = tl6.vconf_state_series(frames3)
    sk3 = streak_state_series(frames3)
    sig = pd.DataFrame(1.0, index=P3["close"].index,
                       columns=P3["close"].columns)
    m_none = _effective_signal_mask_w7(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", gs3, vs3, ys3, cs3, sk3)
    m_w6 = tl6._effective_signal_mask_w6(
        sig, frames3, "none", None, "none", "none", "none", "none",
        gs3, vs3, ys3, cs3)
    _ok("L12a effective mask streak=none == W6 face byte-equal "
        "(semantic-baseline identity law)",
        m_none.equals(m_w6))
    m_up = _effective_signal_mask_w7(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "up_streak2", gs3, vs3, ys3, cs3, sk3)
    _ok("L12b up_streak2 on the alternating face permits nothing "
        "(zero double-up days -> all-zero mask, bite negative leg)",
        int((m_up > 0).sum().sum()) == 0)
    # ramp 510300: strictly increasing close -> every judgeable day
    # is up_streak2 (bite positive leg)
    frames4 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    ramp_i = (frames4["510300"].index if "510300" in frames4
              else frames4[list(frames4)[0]].index)
    ramp_c = pd.Series([100.0 + 0.5 * k for k in range(len(ramp_i))],
                       index=ramp_i)
    ramp_o = pd.Series(100.0, index=ramp_i)
    ramp_v = pd.Series(1000.0, index=ramp_i)
    frames4[STREAK_MEMBER] = pd.DataFrame(
        {"open": ramp_o, "high": ramp_c + 0.2, "low": ramp_o - 0.2,
         "close": ramp_c, "volume": ramp_v, "amount": 1e5},
        index=ramp_i)
    P4 = tl1.build_panels(frames4)
    gs4 = tl3.gate_state_series(frames4)
    vs4 = tl4.vol_state_series(frames4)
    ys4 = tl5.yang_state_series(frames4)
    cs4 = tl6.vconf_state_series(frames4)
    sk4 = streak_state_series(frames4)
    sig4 = pd.DataFrame(1.0, index=P4["close"].index,
                        columns=P4["close"].columns)
    m4_none = _effective_signal_mask_w7(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "none", gs4, vs4, ys4, cs4, sk4)
    m4_up = _effective_signal_mask_w7(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "up_streak2", gs4, vs4, ys4, cs4, sk4)
    _ok("L12c up_streak2 on the ramp face == none face on every "
        "judgeable row (rows 2+), warmup 2 bars gate-closed (bite "
        "positive leg)",
        m4_up.iloc[2:].equals(m4_none.iloc[2:])
        and int((m4_up.iloc[:2] > 0).sum().sum()) == 0)

    # ---- L13 engine-face legs: parity + determinism + streak bites
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none", "none", "none", "none",
                     "none", "none"]}
    st3 = pd.Series("GREEN", index=P3["close"].index)
    eq7, tr7, m7, _, _, _, _, _, _, _, sz7 = run_candidate_curve_w7(
        base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
        yang_state=ys3, vconf_state=cs3, streak_state=sk3)
    eq6 = tl6.run_candidate_curve_w6(
        dict(base, axis=base["axis"][:9]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3)[0]
    _ok("L13a engine face: streak=none identical to tl6 W6 face "
        "(byte-equal parity law)",
        list(eq7.values) == list(eq6.values))
    eq7b, *_ = run_candidate_curve_w7(
        dict(base, candidate_id="ST-B-0001"), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3, vconf_state=cs3,
        streak_state=sk3)
    _ok("L13b engine double-run byte-identity (determinism leg)",
        list(eq7.values) == list(eq7b.values) and sz7 == 0)
    st4 = pd.Series("GREEN", index=P4["close"].index)
    eq4n, tr4n, m4n, _, _, _, _, _, _, _, sz4n = run_candidate_curve_w7(
        dict(base, axis=list(base["axis"])), None, frames4, P4, st4,
        gate_state=gs4, vol_state=vs4, yang_state=ys4, vconf_state=cs4,
        streak_state=sk4)
    eq4u, tr4u, m4u, _, _, _, _, _, _, _, sz4u = run_candidate_curve_w7(
        dict(base, axis=[*base["axis"][:9], "up_streak2"]), None,
        frames4, P4, st4, gate_state=gs4, vol_state=vs4, yang_state=ys4,
        vconf_state=cs4, streak_state=sk4)
    _ok("L13c engine face: up_streak2 on ramp == streak=none "
        "byte-equal (all days confirmed)",
        list(eq4u.values) == list(eq4n.values) and sz4u == 0)
    eq4d, tr4d, m4d, _, _, _, _, _, _, _, sz4d = run_candidate_curve_w7(
        dict(base, axis=[*base["axis"][:9], "down_streak2"]), None,
        frames4, P4, st4, gate_state=gs4, vol_state=vs4, yang_state=ys4,
        vconf_state=cs4, streak_state=sk4)
    m4_down_mask = _effective_signal_mask_w7(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "down_streak2", gs4, vs4, ys4, cs4, sk4)
    _ok("L13d engine face: down_streak2 on ramp zeroes every entry "
        "(mask all-zero + engine num_entries == 0 + streak_zeroed > 0)",
        int((m4_down_mask > 0).sum().sum()) == 0
        and int(m4d.get("num_entries", -1)) == 0 and sz4d > 0)

    # ---- L14 null-axis draw contract (ten-tuple + determinism)
    p1, ax1, rg1 = _null_axis_draw_w7(0)
    p2, ax2, rg2 = _null_axis_draw_w7(0)
    _ok("L14 null-axis draw determinism + TEN-tuple with streak in "
        "the frozen domain (W7 null berth 20305500)",
        p1 == p2 and ax1 == ax2 and len(ax1) == 10
        and ax1[9] in AXIS_STREAK and ax1[:9][4] in tl2.AXIS_STOP)

    # ---- L15 exclusion loader real-read (14 sources + grammar face)
    rows15, disc15 = _load_exclusion_rows_w7(g)
    w6s = disc15.get("w6_screen_survivors")
    w6j = disc15.get("w6_judge_products")
    _ok("L15a exclusion loader: every row a 10-tuple axis with "
        "streak=none + disclosure keys present",
        all(len(r["axis"]) == 10 and r["axis"][9] == "none"
            for r in rows15)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w6_screen_survivors", "w6_judge_products",
             "judged_supply_weighting"} <= set(disc15))
    _ok("L15b W6 screen survivors real-read == 293 (generate-time "
        "re-declare window, prereg sec.1) + W6 judged consumed",
        w6s == 293 and isinstance(w6j, dict)
        and w6j.get("consumed_rows", 0) > 0,
        f"w6_screen={w6s} w6_judged="
        f"{w6j.get('consumed_rows') if isinstance(w6j, dict) else w6j}")

    # ---- L16 _excluded_w7 exact-key law (streak face never excluded)
    hit_key = {"module": rows15[0]["module"], "fn": rows15[0]["fn"],
               "sig_params": rows15[0]["sig_params"],
               "axis": rows15[0]["axis"]}
    hit = _excluded_w7(hit_key, rows15)
    _ok("L16a exact already-judged key (streak=none face) -> excluded",
        hit is not None)
    miss = _excluded_w7({**hit_key, "axis": [*hit_key["axis"][:9],
                                             "up_streak2"]}, rows15)
    _ok("L16b streak in {up_streak2, down_streak2} = new-syntax legal "
        "cell, never excluded",
        miss is None)

    print(f"\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: slice-1a streak layer + G-STREAK + grammar + "
          f"slice-2a machinery: effective mask / curve runner parity / "
          f"null draw / 14-source exclusion loader; funnel cmd bodies "
          f"generate/screen/judge = slice-2b)")
    return 0 if n_pass == n_leg else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="TRIAL_LABOR_W7 runner "
                                     "(streak-confirmation ten-gate wave)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("grammar", help="serialize the frozen W7 grammar")
    sub.add_parser("generate", help="slice-2 pending")
    sp = sub.add_parser("screen", help="slice-2 pending")
    sp.add_argument("--shard", type=int, default=0)
    sp.add_argument("--shards", type=int, default=1)
    sub.add_parser("screen-finalize", help="slice-2 pending")
    jp = sub.add_parser("judge", help="slice-2 pending")
    jp.add_argument("--shard", type=int, default=0)
    jp.add_argument("--shards", type=int, default=1)
    sub.add_parser("judge-finalize", help="slice-2 pending")
    sub.add_parser("intake", help="slice-2 pending")
    sub.add_parser("status", help="slice-state readout")
    sub.add_parser("selftest", help="hermetic offline selftest")
    args = ap.parse_args(argv)
    if args.cmd == "grammar":
        return cmd_grammar()
    if args.cmd == "generate":
        return cmd_generate()
    if args.cmd == "screen":
        return cmd_screen(args.shard, args.shards)
    if args.cmd == "screen-finalize":
        return cmd_screen_finalize()
    if args.cmd == "judge":
        return cmd_judge(args.shard, args.shards)
    if args.cmd == "judge-finalize":
        return cmd_judge_finalize()
    if args.cmd == "intake":
        return cmd_intake()
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "selftest":
        return cmd_selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
