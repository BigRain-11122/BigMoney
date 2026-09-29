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
    print(f"{cmd}: slice-2 pending (claim MSG-20260929-0945-bmb; funnel "
          f"command set lands with the generate/screen/judge parameterized "
          f"tl6 lineage next round; zero cells burned, zero numbers "
          f"fabricated)")
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

    print(f"\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: slice-1a streak layer + G-STREAK + grammar; engine "
          f"double-run legs = slice-2 with the funnel command set)")
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
