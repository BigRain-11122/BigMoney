"""TRIAL_LABOR_W21 runner -- wave-21 CONDITIONED entry-syntax
GENERATE regression batch machinery (frozen prereg
research/TRIAL_LABOR_W21_PREREG.md, bm-b r1077 freeze).

Design (prereg sec.3, FROZEN): 3 new entry fn families derived from the
E21 leg-3 conditioned overnight decomposition
(results/overnight_gap_census/LEG3-2026-10-19.json) x census grid = 18
cells (8 + 4 + 6; A-side = 3 researcher-designated anchor cells, B-side
= 15 enumerated cells; census full-enumeration, zero random, zero
selection degrees of freedom, gen seed 20660000 HELD zero-consumption)
+ K=200 isomorphic random-signal nulls = 218 screen trials.  SINGLE
EXECUTION CONFIG, identical across all cells: X=template_default,
S=equal_weight cell-native, T=daily_signal, all 16 overlay axes "none"
-- the ENTRY MASK is the ONLY tested dimension.

Lineage (import-face reuse law): W21 re-derives ZERO overlay/curve/
null/judge machinery -- imports tl1/tl2/tl16/tl17/tl18 (and through
tl19's chain) verbatim, and pins the W21 grammar as the fifth lineage
anchor.  The ONLY new faces are the fn-family mask layer (E21 leg-3
verbatim math: self-relative liquidity percentile / overnight gap /
overnight-share rank), the 18-cell census enumerator, the fixed-config
single-variable design face, and the G-LEG3ANCHOR gate (mask math
parity against the leg-3 percentile semantics + the pinned leg-3
product readings).

Three-command closeout law (r446bmb/r467bma surgical pit law, prereg
sec.8): screen-prep / screen-finalize / judge-prep real-data
identity-face first-runs BEFORE the runner is declared landed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
# GBK console swallow chain entry law (r236): reconfigure BEFORE any
# child-output print; idempotent, never rely on survivorship bias.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import trial_labor_w1 as tl1   # import-face reuse law (prereg sec.6)
import science_gates           # M1 t-face: t_from_sharpe + m1_t_value_gate
import trial_labor_w2 as tl2   # survival math + dual-nulls + D6 core
import trial_labor_w16 as tl16  # W16 runner: exclusion book loader,
                                # overlay states, curve-caliber lineage
import trial_labor_w17 as tl17  # W17 runner: shared low-level helpers
                                # (dump / park / claim / worker-claim)
from science_gates import (CostPatch, SEED_REGISTRY,  # noqa: E402
                           REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                           REFORM_TOPN_PER_WAVE, REFORM_Q_LEVEL,
                           reform_weight_freeze_integrity,
                           g2_reform_fdr4d)

# ------------------------------------------------------------- frozen (prereg)
WAVE = "TRIAL_LABOR_W21"
PREREG = "research/TRIAL_LABOR_W21_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w21_gen"]         # 20660000 (held)
SEED_NULL = SEED_REGISTRY["trial_labor_w21_scrnull"]   # 20660500
SEED_UNC = SEED_REGISTRY["trial_labor_w21_unc"]        # 20661000
K_NULLS = 200          # screen null family size (sec.0; frozen)
JUDGE_CAP_CELLS = 90   # sec.0 frozen cap (18 cells full-set < 90 -- cap
                       # clause cannot trigger; asserted live anyway)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w21")
GRAMMAR_FILE = os.path.join(RES_DIR, "w21_grammar.json")
CANDS_FILE = os.path.join(RES_DIR, "w21_candidates.json")
# control-source anchor (prereg sec.2 four-tuple; NOT consumed as entry:
# the W16 cell-expansion pairing face is explicitly NOT enabled this
# batch -- the file is the G-ENTRY lineage anchor only)
ENTRY_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                          "w16_candidates.json")
ENTRY_SHA16 = "22179881b7537193"          # sec.2 control-source anchor
KIN_PROBE_FILE = os.path.join(tl1.PATHS.results_dir,
                              "_r1027bmc_w21_kin_orthogonality.json")
SCREEN_FILE = os.path.join(RES_DIR, "w21_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w21_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w21_judge.json")
REFORM_FILE = os.path.join(RES_DIR, "w21_reform_face.json")
INTAKE_FILE = os.path.join(RES_DIR, "w21_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
W14_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w14",
                                "w14_grammar.json")
W16_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                                "w16_grammar.json")
W17_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17",
                                "w17_grammar.json")
W18_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w18",
                                "w18_grammar.json")
W20_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w20",
                                "w20_grammar.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W21_SCREEN"    # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W21_JUDGE"       # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                   # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "08259059b9302e69"   # Slice-B pin (== w21_grammar.json sha16; pinned at first build per W17/W18/W19/W20 precedent) (== w21_grammar.json
# sha16; pinned at first build per W17 r789 / W16 r722 / W18 r880 /
# W19 e15a4a7b3a3b2b36 Slice-B precedent; selftest fail-closed
# verifies the pin == built sha)

# grammar lineage anchors (prereg sec.2 A4 / freeze facts; W19-runner
# verified lineage carried verbatim: w14 + w16 + w17 + w18 internal
# shas == TRIAL_GRAMMAR_LEDGER rows)
W14_GRAMMAR_SHA16 = "a231bf10940e7878"   # w14_grammar internal sha ==
                                          # TRIAL_GRAMMAR_LEDGER W14 row
W16_GRAMMAR_SHA16 = "ebf15822d2c8472e"   # W16 runner Slice-B pin ==
                                          # ledger W16 row
W17_GRAMMAR_SHA16 = "09476ecc5beb2304"   # W17 runner Slice-B pin ==
                                          # ledger W17 row
W18_GRAMMAR_SHA16 = "724b6135a5fdb6ae"
W20_GRAMMAR_SHA16 = "ff00b0896b088b5a"   # w20_grammar internal sha ==
                                          # TRIAL_GRAMMAR_LEDGER W20 row
                                          # (fifth lineage anchor)
LEG3_FILE = os.path.join(tl1.PATHS.results_dir, "overnight_gap_census",
                         "LEG3-2026-10-19.json")
LEG3_SHA16 = "c3eecf0facec0c85"      # pinned leg-3 product (E21 census)
LEG3_GAP_LT2_RON = -0.00446465       # gap<-2% next-day overnight mean
LEG3_LIQ_Q1_RON = -0.00019276        # liquidity q1 overnight mean
                                          # ledger W18 row (carried from
                                          # the W19 runner verbatim)

# X/S/T consumption faces (prereg sec.0 banner, three-wave chain):
X_CONSUMED = "template_default"   # W17 sec.0 consumer (3)
S_CONSUMED = "equal_weight"        # W18 sec.0 consumer (2) -- cell-native
T_CONSUMED = "daily_signal"        # W19 sec.0 consumer (2)
# sec.0/§3 single execution config -- the FIXED 20-tuple, identical for
# every W21 cell and every null: R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
# STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT/MAX/RANK = engine-default
# face, all overlays none.  tl1.DEFAULT_AXIS (4-tuple) + 16x "none".
AXIS_FIXED = [tl1.DEFAULT_AXIS[0], X_CONSUMED, S_CONSUMED, T_CONSUMED] \
    + ["none"] * 16

# sec.5 frozen prediction faces (recorded for honest post-run accounting)
PRED_FAMILY_SURVIVORS_BAND = (1, 3)   # sec.5.1 family-level screen
PRED_JUDGE_REFORM_BAND = (0, 3)        # sec.5.1 judge eligible_reform
PRED_CELL_RATE_BAND = (0.15, 0.40)     # sec.5.2 cell-level survival rate
NULL_P95_BAND = (0.50, 0.53)          # sec.4/sec.5.3 reference band
# registered roster for the D6 reform sub-item (paper six: O-1555 five
# + 511010 cash leg; engine-face daily-return caliber, reeval18 canon)
REGISTERED_D6_SYMBOLS = ("510300", "510050", "510500", "512100",
                         "588000", "511010")
# M3 closed-family key (prereg sec.3): TRIAL_LABOR not in CLOSED_FAMILIES
FAMILY_KEY = "TRIAL_LABOR"

_grammar_sha16 = tl16._grammar_sha16
_j = tl1._j


def _dump(path, payload):
    tl17._dump(path, payload)


# --------------------------------------------------- fn-family mask layer
# E21 leg-3 conditioning verbatim math (scripts/overnight_gap_conditioned.py
# is the W21 kin face; prereg sec.3 table FROZEN).  liq_pct(i) = percentile
# rank of amount(i) inside the stock's OWN trailing WIN_W bars with
# min_periods MIN_WIN -- the leg-3 self-relative liquidity definition,
# applied per-symbol on the shared panel face.
WIN_W = 250
MIN_WIN = 60


def _liq_rank(amount: pd.Series) -> pd.Series:
    return amount.rolling(WIN_W, min_periods=MIN_WIN).rank(pct=True)


def _mask_liq_rank_gate(amount: pd.Series, thr: float, mode: str):
    """Entry mask on the self-relative liquidity state: level = every bar
    with liq_pct >= thr; onset = only the first bar of each such stretch
    (hysteresis-free level crossing, W21 turnover_regime onset analogue)."""
    hi = (_liq_rank(amount) >= thr).fillna(False).to_numpy()
    if mode == "level":
        return pd.Series(hi, index=amount.index)
    onset = np.zeros(len(hi), dtype=bool)
    if len(hi) > 1:
        onset[1:] = hi[1:] & ~hi[:-1]
    return pd.Series(onset, index=amount.index)


def _mask_gap_reversal_gate(close: pd.Series, open_: pd.Series,
                            depth: float):
    """Entry mask on the overnight gap: gap(t) = open(t)/close(t-1) - 1;
    mask = gap <= -depth (the leg-3 gap_lt_-2 bucket mechanized)."""
    gap = open_ / close.shift(1) - 1.0
    return (gap <= -depth).fillna(False)


def _mask_on_share_rank(close: pd.Series, open_: pd.Series, n: int,
                        thr: float):
    """Entry mask on the trailing overnight-share rank: share(t) =
    mean_n(overnight leg) / (mean_n|overnight| + mean_n|intraday|),
    rank inside the stock's own trailing WIN_W bars; mask = rank <= thr
    (names that have been earning their return intraday = less toll)."""
    on = open_ / close.shift(1) - 1.0
    intr = close / open_ - 1.0
    num = on.rolling(n).mean()
    den = (on.abs().rolling(n).mean()
           + intr.abs().rolling(n).mean()).replace(0.0, np.nan)
    share = (num / den).replace([np.inf, -np.inf], np.nan)
    r = _liq_rank(share)
    return (r <= thr).fillna(False)


# mech-family namespace map (prereg sec.1: liq=liquidity-state line,
# gap=reversal-after-deep-gap line, onshare=name-level toll-avoidance
# line; runner-native namespaces -- structurally disjoint from every
# strategies/ module)
FN_MODULE = {
    "liq_rank_gate": "w21_lq",
    "gap_reversal_gate": "w21_gp",
    "on_share_rank": "w21_on",
}
FN_MECH = {
    "liq_rank_gate": "liquidity-state line (attention/participation "
                     "episode mechanized; leg-3 q5 toll = 10x q1)",
    "gap_reversal_gate": "reversal line (deep overnight gap == forced-"
                         "seller overhang; leg-3 gap<-2% next-day "
                         "overnight -44.6bp)",
    "on_share_rank": "name-level toll-avoidance line (trailing overnight "
                     "share of the return; leg-1/leg-2 bleed is linear "
                     "in hold length)",
}
FN_DEFS = {
    "liq_rank_gate": "liq_pct(t)=pct-rank of amount(t) in own trailing "
                     "250 bars (min 60); mask = liq_pct >= thr "
                     "(mode=level) or its strict onset (mode=onset)",
    "gap_reversal_gate": "gap(t)=open(t)/close(t-1)-1; "
                         "mask = gap <= -depth",
    "on_share_rank": "share(t)=mean_n(on)/(mean_n|on|+mean_n|in|); "
                     "rank in own trailing 250 bars; mask = rank <= thr",
}


def _w21_mask_series(fn: str, params: dict, close: pd.Series,
                     volume: pd.Series, open_: pd.Series,
                     amount: pd.Series) -> pd.Series:
    """One cell's entry mask on ONE symbol (leg-3-verbatim math)."""
    if fn == "liq_rank_gate":
        return _mask_liq_rank_gate(amount, params["thr"], params["mode"])
    if fn == "gap_reversal_gate":
        return _mask_gap_reversal_gate(close, open_, params["depth"])
    if fn == "on_share_rank":
        return _mask_on_share_rank(close, open_, params["n"],
                                   params["thr"])
    raise ValueError(fn)


def _on_share_series(close: pd.Series, open_: pd.Series,
                     n: int) -> pd.Series:
    """Trailing overnight-share series (mask-free face; selftest + gate)."""
    on = open_ / close.shift(1) - 1.0
    intr = close / open_ - 1.0
    num = on.rolling(n).mean()
    den = (on.abs().rolling(n).mean()
           + intr.abs().rolling(n).mean()).replace(0.0, np.nan)
    return (num / den).replace([np.inf, -np.inf], np.nan)


def _w21_mask_frame(cand: dict, P: dict) -> pd.DataFrame:
    """One cell's 0/1 entry mask (date x sym) on the given panel --
    per-symbol application of the leg-3-verbatim series math."""
    close, open_ = P["close"], P["open"]
    volume, amount = P["volume"], P["amount"]
    cols = {}
    for s in close.columns:
        if s not in amount.columns:
            cols[s] = pd.Series(False, index=close.index)
            continue
        cols[s] = _w21_mask_series(cand["fn"], cand["sig_params"],
                                   close[s], volume[s], open_[s],
                                   amount[s])
    m = pd.DataFrame(cols, index=close.index, columns=close.columns)
    return m.fillna(False).astype(int)


# ---------------------------------------------------- 18-cell census roster
# prereg sec.3 table FROZEN (18 cells; canonical order = sec.3 table
# enumeration; A-side = 3 researcher-designated anchor cells, B-side =
# the remaining 15 -- census full-enumeration, zero random)
_LQ_GRID = [(thr, mode) for mode in ("level", "onset")
            for thr in (0.60, 0.70, 0.80, 0.90)]
_GP_GRID = [(0.005,), (0.01,), (0.02,), (0.03,)]
_ON_GRID = [(n, thr) for n in (20, 60) for thr in (0.20, 0.35, 0.50)]
# A-side anchors (prereg sec.3 A/B side; researcher-signed) -- stored
# in _param_key canonical form (fn + sorted param items) so the roster
# membership test is an exact set hit
ANCHORS = {
    ("liq_rank_gate", ("mode", "level"), ("thr", 0.80)),
    ("gap_reversal_gate", ("depth", 0.02)),
    ("on_share_rank", ("n", 20), ("thr", 0.35)),
}


def _param_key(fn: str, params: dict):
    return (fn,) + tuple(sorted(params.items()))


def build_roster_w21():
    """18-cell census roster in canonical order with A/B ids and the
    fixed 20-tuple axis (deterministic, zero random)."""
    roster = []
    for thr, mode in _LQ_GRID:
        roster.append({"fn": "liq_rank_gate",
                       "sig_params": {"thr": thr, "mode": mode}})
    for (dp,) in _GP_GRID:
        roster.append({"fn": "gap_reversal_gate",
                       "sig_params": {"depth": dp}})
    for n, thr in _ON_GRID:
        roster.append({"fn": "on_share_rank",
                       "sig_params": {"n": n, "thr": thr}})
    if len(roster) != 18:
        raise SystemExit(f"ROSTER-GATE FAIL: census {len(roster)} != 18")
    a_n = b_n = 0
    out = []
    for c in roster:
        key = _param_key(c["fn"], c["sig_params"])
        is_anchor = key in ANCHORS
        cid = (f"W21-A-{a_n + 1:04d}" if is_anchor
               else f"W21-B-{b_n + 1:04d}")
        if is_anchor:
            a_n += 1
        else:
            b_n += 1
        out.append({"candidate_id": cid, "cell_id": cid,
                    "fn": c["fn"], "sig_params": c["sig_params"],
                    "module": FN_MODULE[c["fn"]],
                    "family": "A" if is_anchor else "B",
                    "axis": list(AXIS_FIXED)})
    if a_n != 3 or b_n != 15:
        raise SystemExit(f"ROSTER-GATE FAIL: A/B split {a_n}/{b_n} "
                         "!= 3/15")
    if len({c["cell_id"] for c in out}) != 18:
        raise SystemExit("ROSTER-GATE FAIL: cell-key collision")
    return out


def _fam_of(cand):
    return cand["fn"]


# ------------------------------------------------------------- anchor gates
def _entry_load():
    """Control-source anchor gate (prereg sec.2 four-tuple): frozen W16
    candidates product, CRLF-canonical sha256_16 verbatim, zero
    re-derivation -- the anchor was pinned on a CRLF worktree face, so
    hash the CRLF-canonical face: LF-only checkouts of the identical
    blob must not false-mismatch (r890 bm-b crash-loop repair); any
    content drift still fails closed.  W21 does NOT consume these
    cells as entry (sec.2: W16 cell-expansion pairing face explicitly
    NOT enabled) -- the file is the G-ENTRY lineage anchor only."""
    with open(ENTRY_FILE, "rb") as fh:
        raw = fh.read()
    canon = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    sha16 = hashlib.sha256(canon).hexdigest()[:16]
    if sha16 != ENTRY_SHA16:
        raise SystemExit(f"ENTRY-GATE FAIL: w16_candidates.json sha "
                         f"{sha16} != frozen {ENTRY_SHA16}")
    d = json.loads(raw)
    if len(d["candidates"]) != 173:
        raise SystemExit(f"ENTRY-GATE FAIL: n={len(d['candidates'])} != 173")
    return d


def _roster_fn_gate():
    """G-ROSTER (prereg sec.0 banner, three fn-gates, LIVE re-run):
    the three W21 fn names have ZERO literal intersection with the
    58-fn W16 frozen roster (live read = w16_candidates.json fn set +
    W16 grammar families fn names) NOR with the W20 census roster,
    and the three modules are runner-native namespaces absent from
    every prior-wave row."""
    ed = _entry_load()
    roster16 = {c["fn"] for c in ed["candidates"]}
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    for fam, slots in (w16g.get("families") or {}).items():
        for sl in slots:
            roster16.add(sl["fn"])
    w20g = json.load(open(W20_GRAMMAR_FILE, encoding="utf-8"))
    roster16 |= {r_["fn"] for r_ in w20g.get("roster", [])}
    w21_fns = set(FN_MODULE)
    inter = sorted(w21_fns & roster16)
    return (not inter), {"w21_fns": sorted(w21_fns),
                         "roster16_n": len(roster16),
                         "intersection": inter}


def _seeds_gate():
    """G-SEEDS (prereg sec.0 seeds three-step law): the three berths
    live in SEED_REGISTRY at the frozen values (freeze-commit same-
    commit R250 one-step law) and the family band [20660000, 20662500)
    is disjoint from every OTHER registry key."""
    want = {"trial_labor_w21_gen": SEED_GEN,
            "trial_labor_w21_scrnull": SEED_NULL,
            "trial_labor_w21_unc": SEED_UNC}
    have = {k: SEED_REGISTRY.get(k) for k in want}
    if have != want:
        return False, {"want": want, "have": have}
    lo, hi = SEED_GEN, SEED_GEN + 2500
    hits = []
    for k, v in SEED_REGISTRY.items():
        if k in want:
            continue
        if isinstance(v, int) and lo <= v < hi:
            hits.append({k: v})
    return (not hits), {"berths": want, "band": [lo, hi],
                        "foreign_hits": hits}


def _exitcfg_gate():
    """A9 fail-closed gate: live engine defaults == frozen table
    (tl17 verbatim reuse; X=template_default consumed face -- the
    default exit stack is the tested baseline, so the A9 drift gate
    stays load-bearing)."""
    return tl17._exitcfg_gate()


def _probe_face():
    """G-510300-FACE (prereg sec.2 panel anchor): the kin-probe face =
    data/daily/sh510300.csv raw read truncated at CUTOFF.  Returns
    (close, volume, open, amount, face_facts); amount = close*volume is
    the panel-native turnover proxy (the raw ETF csv carries no amount
    column -- disclosed in the prereg sec.2 face note)."""
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] <= CUTOFF].set_index("date").astype(float)
    close, volume = df["close"], df["volume"]
    return close, volume, df["open"], close * volume, {
        "n_bars": int(len(df)), "first": str(df.index[0].date()),
        "last": str(df.index[-1].date())}


def _norm_probe_params(params):
    """Normalize the kin-probe JSON param face (values serialized as
    strings in the committed probe product) to the numeric roster
    caliber -- int when integral, float otherwise."""
    out = {}
    for k, v in params.items():
        if isinstance(v, str):
            try:
                f = float(v)
                out[k] = int(f) if f == int(f) and "." not in v \
                    and "e" not in v.lower() else f
            except ValueError:
                out[k] = v
        else:
            out[k] = v
    return out


def _leg3_anchor_gate():
    """G-LEG3ANCHOR (prereg sec.2/§8 runner-build clause -- the batch
    identity face): (a) the W21 mask math reproduces the leg-3
    self-relative percentile semantics on the probe face (pandas
    rolling rank vs the leg-3 first principles percentile, exact match
    over every usable bar) and (b) the pinned leg-3 product readings
    are still on disk byte-identically (sha16 + two headline numbers),
    so the conditioning facts this batch cites cannot silently drift.
    Also returns the 18 census mask_days/fingerprints on the probe
    face (T-84s3 zero-collapse expectation, 18/18 unique)."""
    raw = open(LEG3_FILE, "rb").read()
    sha16 = hashlib.sha256(raw).hexdigest()[:16]
    prod = json.loads(raw)
    by_gap = {r["gap_bucket"]: r for r in prod["faces"]["by_gap"]}
    by_liq = {r["liq_q"]: r for r in prod["faces"]["by_liq"]}
    g_lt2 = float(by_gap["gap_lt_-2"]["r_on"]["mean"])
    q1 = float(by_liq["q1"]["r_on"]["mean"])
    pin_ok = (sha16 == LEG3_SHA16
              and abs(g_lt2 - LEG3_GAP_LT2_RON) < 1e-8
              and abs(q1 - LEG3_LIQ_Q1_RON) < 1e-8)
    close, volume, open_, amount, face = _probe_face()
    # (a) percentile-semantics parity: rolling rank == fraction of the
    # trailing window <= today, computed from first principles on the
    # same series (exact, zero tolerance)
    r_roll = _liq_rank(amount).to_numpy()
    arr = amount.to_numpy()
    n_checked = n_ok = 0
    for i in range(MIN_WIN - 1, len(arr)):
        if np.isnan(arr[i]):
            continue
        w = arr[max(0, i - WIN_W + 1):i + 1]
        w = w[~np.isnan(w)]
        if len(w) < MIN_WIN:
            continue
        ref = float((w <= arr[i]).mean())
        n_checked += 1
        if abs(float(r_roll[i]) - ref) <= 1e-12:
            n_ok += 1
    parity = bool(n_checked > 0 and n_ok == n_checked)
    roster = build_roster_w21()
    rows, fps = [], []
    for c in roster:
        m = _w21_mask_series(c["fn"], c["sig_params"], close, volume,
                             open_, amount)
        md = int(m.sum())
        fp = tl1._fingerprint(pd.DataFrame({"510300": m}))
        rows.append({"cell_id": c["cell_id"], "fn": c["fn"],
                     "sig_params": c["sig_params"], "mask_days": md,
                     "fingerprint": fp})
        fps.append(fp)
    ok = bool(pin_ok and parity and len(set(fps)) == 18
              and face["n_bars"] == 3483)
    from collections import Counter
    count_collisions = {k: v for k, v in
                        Counter([r["mask_days"] for r in rows]).items()
                        if v > 1}
    return ok, {"leg3_sha16": sha16, "leg3_pin": LEG3_SHA16,
                "gap_lt_-2_ron": g_lt2, "liq_q1_ron": q1,
                "percentile_parity": {"checked": n_checked,
                                      "matched": n_ok},
                "probe_face": face,
                "n_match": len(rows),
                "fingerprints_unique": len(set(fps)),
                "mask_days_count_collisions": count_collisions,
                "rows": rows}


# ----------------------------------------------------------- curve machinery
def run_candidate_curve_w21(cand, prices, P, states, rng_matrix=None,
                            p_on=None):
    """One W21 cell at the engine face: the W16 overlay pipeline
    (filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK ->
    TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> CNT -> MAX
    -> RANK -> initial-stop) with the ENTRY MASK as the only variable
    (prereg sec.3 -- single execution config: every cell carries the
    same fixed 20-tuple, all overlays "none" = identity pass-through,
    so the 17 zero-mask counters are honest zeros by construction;
    engine params = candidate_engine_params(cand, None) = engine
    defaults {} + None patch (B-caliber, X=template_default consumed);
    sizing = tl1.sizing_pieces at axis[2]=equal_weight; P1 signal
    reversal = runner-native exit_signal=(S<=0)).  Curve/overlay
    machinery = tl16 import-face reuse, zero re-derivation; the mask
    comes from the W21 fn-family layer (probe-verbatim math), nulls
    from the tl1._signal_frame rng_matrix verbatim path."""
    ax = cand["axis"]
    if ax != AXIS_FIXED:
        raise SystemExit(f"CURVE-GATE FAIL: axis drift {ax} != "
                         "AXIS_FIXED (single execution config violated)")
    stop_key, gate_key = ax[4], ax[5]
    vol_key, yang_key, vconf_key = ax[6], ax[7], ax[8]
    streak_key, tstate_key, amp_key = ax[9], ax[10], ax[11]
    mom_key, std_key, rsqr_key = ax[12], ax[13], ax[14]
    sumn_key, resi_key, cnt_key = ax[15], ax[16], ax[17]
    max_key, rank_key = ax[18], ax[19]
    if rng_matrix is not None:   # null leg: random signals, verbatim path
        mask = tl1._signal_frame(None, P, "null", rng_matrix=rng_matrix,
                                 p_on=p_on)
    else:
        mask = _w21_mask_frame(cand, P)
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, ax[0], P, None)
    mask = tl1.apply_timing(mask, ax[3])
    # all-overlay-none identity chain (states not required -- the
    # frozen config keys are "none" 16x, asserted above; counters stay
    # honest zeros; pipeline face = tl16 verbatim call path)
    G = tl16.tl3.gate_zero_mask(mask, gate_key, None)
    V = tl16.tl4.vol_zero_mask(G, vol_key, None)
    Y = tl16.tl5.yang_zero_mask(V, yang_key, None)
    VC = tl16.tl6.vconf_zero_mask(Y, vconf_key, None)
    SK = tl16.tl7.streak_zero_mask(VC, streak_key, None)
    TS = tl16.tl8.tstate_zero_mask(SK, tstate_key, None)
    AP = tl16.tl9.amp_zero_mask(TS, amp_key, None)
    MO = tl16.mom_zero_mask(AP, mom_key, None)
    SD = tl16.std_zero_mask(MO, std_key, None)
    RQ = tl16.rsqr_zero_mask(SD, rsqr_key, None)
    NQ = tl16.sumn_zero_mask(RQ, sumn_key, None)
    RE = tl16.resi_zero_mask(NQ, resi_key, None)
    CN = tl16.cnt_zero_mask(RE, cnt_key, None)
    MX = tl16.max_zero_mask(CN, max_key, None)
    RK = tl16.rank_zero_mask(MX, rank_key, None)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    yang_zeroed = int((V > 0).sum().sum() - (Y > 0).sum().sum())
    vconf_zeroed = int((Y > 0).sum().sum() - (VC > 0).sum().sum())
    streak_zeroed = int((VC > 0).sum().sum() - (SK > 0).sum().sum())
    tstate_zeroed = int((SK > 0).sum().sum() - (TS > 0).sum().sum())
    amp_zeroed = int((TS > 0).sum().sum() - (AP > 0).sum().sum())
    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())
    std_zeroed = int((MO > 0).sum().sum() - (SD > 0).sum().sum())
    rsqr_zeroed = int((SD > 0).sum().sum() - (RQ > 0).sum().sum())
    sumn_zeroed = int((RQ > 0).sum().sum() - (NQ > 0).sum().sum())
    resi_zeroed = int((NQ > 0).sum().sum() - (RE > 0).sum().sum())
    cnt_zeroed = int((RE > 0).sum().sum() - (CN > 0).sum().sum())
    max_zeroed = int((CN > 0).sum().sum() - (MX > 0).sum().sum())
    rank_zeroed = int((MX > 0).sum().sum() - (RK > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = CN, 0
    else:
        atr20 = tl2.atr20_series(prices)
        S = tl2._effective_signal_mask(CN, prices, stop_key, atr20)
        d = (CN > 0) & (S == 0)
        stop_fired = int(sum(int((d[c] & ~d[c].shift(1, fill_value=False
                                                    ).sum())
                                 for c in d.columns)))
    params, patch = tl1.candidate_engine_params(cand, None)
    params, scale = tl1.sizing_pieces(cand, P, states, params)
    params["report_num_entries"] = True
    with tl1.ExitPatch(patch):
        res = tl1.run_backtest(prices, params, entry_signal=S,
                               exit_signal=(S <= 0),
                               entry_size_scale=scale, dd_control=None)
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \
        std_zeroed, rsqr_zeroed, sumn_zeroed, resi_zeroed, cnt_zeroed, \
        max_zeroed, rank_zeroed


def _null_axis_draw_w21(i):
    """Deterministic null-cell draw per prereg sec.0/sec.2: rng=
    [SEED_NULL, i] (W21 berth 20660500, band [20660500,20660700));
    consumption order frozen = p_on regime FIRST, then the caller
    draws the signal matrix from the SAME rng stream (returned rng).
    The execution config is the FIXED single tuple -- zero axis draws
    (the candidate space shares the identical config; the null family
    differs ONLY in the random entry mask, same-grid same-param-space
    by construction, BACKTEST_PLAN three iron rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    return p_on, list(AXIS_FIXED), rng


# ------------------------------------------------------------ grammar build
def build_grammar_w21():
    """Serialize the W21 grammar face: the three fn-family definitions
    (verbatim) + the 18-cell census roster + the fixed single
    execution config + lineage anchors + null/judge constants
    (deterministic, zero random; sec.3 GENERATE leg)."""
    roster = build_roster_w21()
    fam_census = {}
    for c in roster:
        fam_census[c["fn"]] = fam_census.get(c["fn"], 0) + 1
    g = {"wave": WAVE, "grammar_kind": "w21-entry-grammar-generate-census",
         "prereg": PREREG, "evidence_cutoff": CUTOFF,
         "grammar_sha256": None,
         "seeds": {"gen_held": SEED_GEN, "scrnull": SEED_NULL,
                   "unc": SEED_UNC,
                   "band": [SEED_GEN, SEED_GEN + 2500],
                   "note": "gen 20660000 HELD zero-consumption this wave "
                           "(census full-enumeration, zero sampling, "
                           "zero selection degrees of freedom -- berth "
                           "kept for family-band continuity + future "
                           "W21-derived generation faces); scrnull rng("
                           "[20660500,i]) i<200; unc rng([20661000,"
                           "cell_idx]) cell_idx<18"},
         "fn_families": {fn: {"module": FN_MODULE[fn],
                              "mech_line": FN_MECH[fn],
                              "definition": FN_DEFS[fn],
                              "source": "kin-probe verbatim "
                              "(results/_r1027bmc_w21_kin_ortho-"
                              "gonality.py same-form; r1027 freeze-"
                              "window measured face)",
                              "n_cells": fam_census[fn]}
                         for fn in FN_MODULE},
         "roster": [{"cell_id": c["cell_id"], "fn": c["fn"],
                     "sig_params": c["sig_params"],
                     "module": c["module"], "family": c["family"],
                     "axis": c["axis"]} for c in roster],
         "a_side_anchors": [{"fn": a[0], "sig_params": dict(a[1:])}
                            for a in sorted(ANCHORS)],
         "fixed_execution_config": {
             "axis": list(AXIS_FIXED),
             "x_consumed": {"face": X_CONSUMED,
                             "basis": "W17 sec.0 consumer (3): W17-JUDGE "
                                      "344 all-negative + 7 exit faces "
                                      "paired median delta 0.0"},
             "s_consumed": {"face": S_CONSUMED,
                            "basis": "W18 sec.0 consumer (2): W18-JUDGE "
                                     "188 lawful-zero + 4 sizing faces "
                                     "paired median delta ~0 = cell-"
                                     "native for census cells = "
                                     "equal_weight"},
             "t_consumed": {"face": T_CONSUMED,
                            "basis": "W19 sec.0 consumer (2): W19-JUDGE "
                                     "112 lawful-zero + weekly->daily "
                                     "paired direction +0.0942 p=0.01 "
                                     "below registration line"},
             "note": "single execution config, identical across all 18 "
                     "cells + 200 nulls -- the entry mask is the ONLY "
                     "tested dimension (three-axis consumption "
                     "dividend, zero axis-crossing)"},
         "k_nulls": K_NULLS,
         "null_p95_band": list(NULL_P95_BAND),
         "judge_cap_cells": JUDGE_CAP_CELLS,
         "control_source": {"file": "results/trial_labor_w16/"
                          "w16_candidates.json",
                            "sha256_16": ENTRY_SHA16, "n": 173,
                            "role": "G-ENTRY lineage anchor ONLY -- "
                                    "W16 cell-expansion pairing face "
                                    "explicitly NOT enabled (sec.2 "
                                    "frozen; reuse = re-burning judged "
                                    "negatives violates the negative-"
                                    "true-close line)"},
         "w14_lineage": {"grammar_sha16": W14_GRAMMAR_SHA16,
                         "file": "results/trial_labor_w14/w14_grammar.json"},
         "w16_grammar_ref": {"file": "results/trial_labor_w16/"
                          "w16_grammar.json",
                          "grammar_sha16": W16_GRAMMAR_SHA16},
         "w17_grammar_ref": {"file": "results/trial_labor_w17/"
                          "w17_grammar.json",
                          "grammar_sha16": W17_GRAMMAR_SHA16},
         "w18_grammar_ref": {"file": "results/trial_labor_w18/"
                          "w18_grammar.json",
                          "grammar_sha16": W18_GRAMMAR_SHA16},
         "w20_grammar_ref": {"file": "results/trial_labor_w20/"
                          "w20_grammar.json",
                          "grammar_sha16": W20_GRAMMAR_SHA16},
         "leg3_ref": {"file": "results/overnight_gap_census/"
                      "LEG3-2026-10-19.json",
                      "sha16": LEG3_SHA16,
                      "role": "G-LEG3ANCHOR provenance + mask math "
                              "parity source (18/18 cell mask_days "
                              "readings, probe face)"},
         "closed_family_check": {"family_key": FAMILY_KEY,
                                 "in_closed": FAMILY_KEY in
                                 getattr(science_gates,
                                         "CLOSED_FAMILIES", {}),
                                 "note": "M3: TRIAL_LABOR not in "
                                         "CLOSED_FAMILIES = open; "
                                         "lowamp/n2/perpetual family "
                                         "keys disjoint (sec.3)"},
         "cell_key": "cell_id (single execution config -- no face dim)",
         "n_cells": 18,
         "family_split": {"A": 3, "B": 15},
         "screen_trials": 18 + K_NULLS}
    g["grammar_sha256"] = _grammar_sha16(g)
    return g


def cmd_grammar() -> int:
    print(f"=== {WAVE} grammar ===")
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w21()
    _dump(GRAMMAR_FILE, g)
    print(f"grammar done -> {GRAMMAR_FILE} (sha16 "
          f"{g['grammar_sha256'][:16]})")
    return 0


def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    for p, what in ((GRAMMAR_FILE, "w21_grammar.json"),
                    (CANDS_FILE, "w21_candidates.json"),
                    (SCREEN_FILE, "w21_screen.json"),
                    (JUDGE_FILE, "w21_judge.json"),
                    (REFORM_FILE, "w21_reform_face.json"),
                    (INTAKE_FILE, "w21_intake.json")):
        print(f"  {'[x]' if os.path.exists(p) else '[ ]'} {what}")
    ok, detail = _exitcfg_gate()
    print(f"  A9 exitcfg gate: {'PASS' if ok else 'FAIL'} {detail or ''}")
    ok, detail = _roster_fn_gate()
    print(f"  G-ROSTER fn gate: {'PASS' if ok else 'FAIL'} "
          f"{detail['intersection']}")
    ok, detail = _seeds_gate()
    print(f"  G-SEEDS gate: {'PASS' if ok else 'FAIL'} "
          f"foreign={detail['foreign_hits']}")
    return 0


# ------------------------------------------------------------------ generate
def _excluded_w21(cand, rows):
    """Exclusion-book matcher (prereg sec.3 live-read 17-source): exact
    (module, fn, sig_params, axis) test.  W21 modules/fns are new
    namespaces (three-gate proven) so a hit is structurally impossible
    -- the live-read assertion still runs at GENERATE (对号零撞)."""
    for e in rows:
        if (cand["module"], cand["fn"]) == (e.get("module"),
                                            e.get("fn")) \
                and cand["sig_params"] == e.get("sig_params") \
                and list(cand["axis"]) == list(e.get("axis", [])):
            return e.get("face", "exclusion_row")
    return None


def cmd_generate() -> int:
    """GENERATE leg (sec.3, deterministic zero-random): 18-cell census
    enumeration + G-ROSTER three fn-gates live re-run + G-SEEDS live +
    exclusion-book 17-source live-read 对号零撞 + probe-face fingerprint
    census (T-84s3 zero-collapse) + w21_candidates.json +
    TRIAL_GRAMMAR_LEDGER wave-20 row (W11/W17 practice precedent).
    Same-grammar rerun forbidden (TRIAL_LABOR_LAW sec.4)."""
    t0 = time.time()
    print(f"=== {WAVE} generate ===")
    if os.path.exists(CANDS_FILE):
        print("GENERATE-GATE: w21_candidates.json already landed -- "
              "same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4)")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"GENERATE-GATE FAIL: grammar sha drift != frozen "
              f"{FROZEN_SHA16}")
        return 1
    if grammar.get("closed_family_check", {}).get("in_closed"):
        print("GENERATE-GATE FAIL: family key in CLOSED_FAMILIES "
              "(M3 face) -- refuse")
        return 1
    # -- G-ROSTER (three fn-gates, live re-run)
    ok, rost = _roster_fn_gate()
    if not ok:
        print(f"GENERATE-GATE FAIL: G-ROSTER intersection "
              f"{rost['intersection']} != empty (58-fn W16 frozen "
              "roster) -- honest refuse")
        return 1
    # -- G-SEEDS (berths + band disjoint, live re-run)
    ok, seeds = _seeds_gate()
    if not ok:
        print(f"GENERATE-GATE FAIL: G-SEEDS {seeds} -- honest refuse")
        return 1
    # -- G-ENTRY control-source anchor (raises on drift)
    ed = _entry_load()
    # -- G-LINEAGE (w14+w16+w17+w18 pins == ledger rows)
    w14g = json.load(open(W14_GRAMMAR_FILE, encoding="utf-8"))
    if str(w14g.get("grammar_sha256", ""))[:16] != W14_GRAMMAR_SHA16:
        print(f"GENERATE-GATE FAIL: w14_grammar internal sha != "
              f"{W14_GRAMMAR_SHA16}")
        return 1
    lineage = {}
    for tag, path, pin in (("W16", W16_GRAMMAR_FILE, W16_GRAMMAR_SHA16),
                           ("W17", W17_GRAMMAR_FILE, W17_GRAMMAR_SHA16),
                           ("W18", W18_GRAMMAR_FILE, W18_GRAMMAR_SHA16),
                           ("W20", W20_GRAMMAR_FILE, W20_GRAMMAR_SHA16)):
        gg = json.load(open(path, encoding="utf-8"))
        if _grammar_sha16(gg)[:16] != pin:
            print(f"GENERATE-GATE FAIL: {tag.lower()}_grammar sha drift "
                  f"!= {pin}")
            return 1
        lineage[tag] = pin
    led_rows = {}
    if os.path.exists(tl1.GRAMMAR_LEDGER):
        for ln in open(tl1.GRAMMAR_LEDGER, encoding="utf-8"):
            parts = [p.strip() for p in ln.split("|")]
            if len(parts) > 3 and parts[1].startswith("TRIAL_LABOR"):
                led_rows[parts[1]] = parts[2]
    for tag, pin in (("TRIAL_LABOR_W14", W14_GRAMMAR_SHA16),
                     ("TRIAL_LABOR_W16", W16_GRAMMAR_SHA16),
                     ("TRIAL_LABOR_W17", W17_GRAMMAR_SHA16),
                     ("TRIAL_LABOR_W18", W18_GRAMMAR_SHA16),
                     ("TRIAL_LABOR_W20", W20_GRAMMAR_SHA16)):
        if led_rows.get(tag) != pin:
            print(f"GENERATE-GATE FAIL: ledger lineage mismatch {tag}="
                  f"{led_rows.get(tag)} != {pin}")
            return 1
    # -- exclusion book 17-source live read (W1-W14 + N2-W15 + W16
    # burned cells via the W16 grammar face loader)
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    rows, _excl_disc = tl16._load_exclusion_rows_w16(w16g)
    roster = build_roster_w21()
    hits = [{"cell_id": c["cell_id"], "source": _excluded_w21(c, rows)}
            for c in roster if _excluded_w21(c, rows)]
    if hits:
        print(f"GENERATE-GATE FAIL: {len(hits)} exclusion-book hits "
              f"(structurally impossible for new namespaces -- face "
              f"misconfig) sample {hits[:3]}")
        return 1
    # -- probe-face fingerprint census (T-84s3; zero-collapse gate +
    # mask_days alignment vs the kin probe = G-LEG3ANCHOR live re-run)
    ok, md = _leg3_anchor_gate()
    if not ok:
        print(f"GENERATE-GATE FAIL: G-LEG3ANCHOR alignment {md['probe_face']}"
              f" n_match={md['n_match']}/18 fps_unique="
              f"{md['fingerprints_unique']}/18 -- honest refuse")
        return 1
    fp_by_cell = {r["cell_id"]: r["fingerprint"] for r in md["rows"]}
    days_by_cell = {r["cell_id"]: r["mask_days"] for r in md["rows"]}
    # -- products
    cells = []
    for c in roster:
        cells.append({**c, "mask_days_510300": days_by_cell[c["cell_id"]],
                      "fingerprint_510300": fp_by_cell[c["cell_id"]]})
    prod = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "control_sha256_16": ENTRY_SHA16,
            "n_cells": 18, "family_split": {"A": 3, "B": 15},
            "fn_census": {fn: sum(1 for c in cells if c["fn"] == fn)
                          for fn in FN_MODULE},
            "exclusion": {"sources": "17-source live read (W1-W14 + "
                          "N2-W15 + W16 burned via tl16 loader)",
                          "prev_rows": len(rows), "hits": 0},
            "g_face": {"G-ROSTER": {"intersection": [],
                                    "roster16_n": rost["roster16_n"]},
                       "G-SEEDS": {"berths": seeds["berths"],
                                   "band": seeds["band"],
                                   "foreign_hits": []},
                       "G-ENTRY": {"sha256_16": ENTRY_SHA16,
                                   "n": len(ed["candidates"])},
                       "G-LINEAGE": lineage,
                       "G-LEG3ANCHOR": {"n_match": md["n_match"],
                                      "fingerprints_unique":
                                      md["fingerprints_unique"],
                                      "probe_face": md["probe_face"],
                                      "mask_days_count_collisions":
                                      md["mask_days_count_collisions"],
                                      "note": "count collisions (174x2/"
                                              "113x2 on the probe face) "
                                              "are NOT fingerprint "
                                              "collapses -- the "
                                              "operative T-84s3 dedup "
                                              "unit is the mask "
                                              "fingerprint; 18/18 "
                                              "unique, zero collapse "
                                              "(honest disclosure vs "
                                              "the sec.3 'mask_days "
                                              "all-different' "
                                              "wording: the claim "
                                              "holds at the "
                                              "fingerprint level)"}},
            "seeds": grammar["seeds"],
            "cells": cells}
    _dump(CANDS_FILE, prod)
    # grammar consumption ledger row (append-only; W11/W17 caliber)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"3 new-entry fn families census grid (8+4+6=18 cells, "
           f"zero random; gen seed {SEED_GEN} HELD zero-consumption; "
           f"X={X_CONSUMED} per W17 consumer(3) / S={S_CONSUMED} "
           f"native per W18 consumer(2) / T={T_CONSUMED} per W19 "
           f"consumer(2) -- single execution config, entry mask = "
           f"the only variable) | cells 18 + nulls {K_NULLS} = "
           f"{18 + K_NULLS} (fingerprint census 18/18 unique probe "
           f"face; control anchor w16_candidates {ENTRY_SHA16} "
           f"G-ENTRY only, pairing face NOT enabled) | seeds "
           f"gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (prereg bm-c r1027 "
           f"frozen 06f323b92 / runner bm-c r1028 entry-grammar "
           f"build) | same-grammar rerun FORBIDDEN "
           f"(TRIAL_LABOR_LAW sec.4) |\n")
    gl = tl1.GRAMMAR_LEDGER
    os.makedirs(os.path.dirname(gl), exist_ok=True)
    if not os.path.exists(gl):
        with open(gl, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; "
                     "TRIAL_LABOR_LAW sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(gl, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)
    print(f"generate done: 18 census cells (A 3 / B 15), exclusion "
          f"hits 0, G-LEG3ANCHOR 18/18, fingerprints 18/18 unique")
    print(f"products: {CANDS_FILE} + ledger row (sha16 "
          f"{grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# --------------------------------------------------------------- screen (s2)
csv_cols_screen_w21 = ["cell_id", "candidate_id", "family", "module",
                       "fn", "sig_params", "no_entries", "beat6m_k",
                       "beat6m_n", "beat6m_rate", "binom_z", "binom_p",
                       "sharpe_full", "dd_full", "n_trades", "n_entries",
                       "stop_face", "stop_fired", "gate_face",
                       "gate_zeroed", "vol_face", "vol_zeroed",
                       "yang_face", "yang_zeroed", "vconf_face",
                       "vconf_zeroed", "streak_face", "streak_zeroed",
                       "tstate_face", "tstate_zeroed", "amp_face",
                       "amp_zeroed", "mom_face", "mom_zeroed",
                       "std_face", "std_zeroed", "rsqr_face",
                       "rsqr_zeroed", "sumn_face", "sumn_zeroed",
                       "resi_face", "resi_zeroed", "cnt_face",
                       "cnt_zeroed", "max_face", "max_zeroed",
                       "rank_face", "rank_zeroed", "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law)
_finalize_math = tl2._finalize_math


def _screen_cell_w21(cell):
    """One W21 screen cell: full leg-L backtest -> beat6m row (pool
    worker; W19 _screen_cell caliber, single-config face)."""
    st = tl1._ST
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    kind = cell["kind"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w21(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W21-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(P["close"].index), len(P["close"].columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w21(cand, prices, P, states,
                                     rng_matrix=mat, p_on=p_on)
        cid = cand["candidate_id"]
        fam = "NULL"
        fnm, sp = cand["fn"], None
    else:
        cand = cell["cand"]
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w21(cand, prices, P, states)
        cid = cand["candidate_id"]
        fam = cand["family"]
        fnm, sp = cand["fn"], json.dumps(cand["sig_params"],
                                         sort_keys=True)
    row = {"cell_id": cid, "candidate_id": cid, "family": fam,
           "module": cand.get("module"), "fn": fnm, "sig_params": sp,
           "stop_face": cand["axis"][4], "stop_fired": int(fired),
           "gate_face": cand["axis"][5], "gate_zeroed": int(gz),
           "vol_face": cand["axis"][6], "vol_zeroed": int(vz),
           "yang_face": cand["axis"][7], "yang_zeroed": int(yz),
           "vconf_face": cand["axis"][8], "vconf_zeroed": int(cz),
           "streak_face": cand["axis"][9], "streak_zeroed": int(sz),
           "tstate_face": cand["axis"][10], "tstate_zeroed": int(tz),
           "amp_face": cand["axis"][11], "amp_zeroed": int(az),
           "mom_face": cand["axis"][12], "mom_zeroed": int(mz),
           "std_face": cand["axis"][13], "std_zeroed": int(dz),
           "rsqr_face": cand["axis"][14], "rsqr_zeroed": int(rz),
           "sumn_face": cand["axis"][15], "sumn_zeroed": int(nz),
           "resi_face": cand["axis"][16], "resi_zeroed": int(rz2),
           "cnt_face": cand["axis"][17], "cnt_zeroed": int(cnz),
           "max_face": cand["axis"][18], "max_zeroed": int(mxz),
           "rank_face": cand["axis"][19], "rank_zeroed": int(rkz)}
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
        if cret >= passive[p]:        # prereg sec.4 literal ">="
            k += 1
    rate = k / n_win if n_win else 0.0
    n = len(starts)
    z = (k - 0.5 * n) / math.sqrt(0.25 * n) if n else 0.0
    pval = 2 * (1 - tl1._norm_cdf(abs(z)))
    row.update({"no_entries": False, "beat6m_k": k, "beat6m_n": n_win,
                "beat6m_rate": round(rate, 6), "binom_z": round(z, 4),
                "binom_p": round(pval, 6),
                "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                "dd_full": round(float(tl1.max_drawdown(eq)), 4),
                "n_trades": int(metrics.get("num_trades", 0)),
                "n_entries": int(metrics.get("num_entries", 0))})
    return row


def _cell_list_w21():
    """18 census cells + K null cells (deterministic order; shard-split
    by index; W19 precedent, no face dim)."""
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    prod = json.load(open(CANDS_FILE, encoding="utf-8"))
    cells = []
    for cell in prod["cells"]:
        cells.append({"cell_id": cell["cell_id"], "kind": "cand",
                      "cand": cell})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None})
    return grammar, cells


def cmd_screen_prep() -> int:
    """G-PANEL / G-510300-FACE / G-ENTRY / G-LINEAGE / G-EXITCFG /
    G-ROSTER / G-SEEDS / G-LEG3ANCHOR fail-closed gates (prereg sec.2
    anchors) + the shared passive 6m precompute.  Identity-first-run
    law (r446bmb): every panel/anchor identity face runs BEFORE the
    cells-presence refusal so the full identity face exercises on
    real data pre-generate (rc=2 honest 'generate pending' lands at
    the TAIL)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    # G-EXITCFG (A9): live engine defaults == frozen table
    ok, drift = _exitcfg_gate()
    if not ok:
        print(f"PREP-GATE FAIL: G-EXITCFG drift {drift} -- fail-closed")
        return 1
    # G-ROSTER three fn-gates + G-SEEDS berths (live re-run)
    ok, rost = _roster_fn_gate()
    if not ok:
        print(f"PREP-GATE FAIL: G-ROSTER {rost} -- fail-closed")
        return 1
    ok, seeds = _seeds_gate()
    if not ok:
        print(f"PREP-GATE FAIL: G-SEEDS {seeds} -- fail-closed")
        return 1
    # G-LINEAGE (A4): w14 + w16 + w17 + w18 pins == ledger rows
    w14g = json.load(open(W14_GRAMMAR_FILE, encoding="utf-8"))
    if str(w14g.get("grammar_sha256", ""))[:16] != W14_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w14_grammar internal sha != "
              f"{W14_GRAMMAR_SHA16}")
        return 1
    lineage = {}
    for tag, path, pin in (("w16", W16_GRAMMAR_FILE, W16_GRAMMAR_SHA16),
                           ("w17", W17_GRAMMAR_FILE, W17_GRAMMAR_SHA16),
                           ("w18", W18_GRAMMAR_FILE, W18_GRAMMAR_SHA16),
                           ("w20", W20_GRAMMAR_FILE, W20_GRAMMAR_SHA16)):
        gg = json.load(open(path, encoding="utf-8"))
        if _grammar_sha16(gg)[:16] != pin:
            print(f"PREP-GATE FAIL: {tag}_grammar sha != {pin}")
            return 1
        lineage[tag] = pin
    led_rows = {}
    if os.path.exists(tl1.GRAMMAR_LEDGER):
        for ln in open(tl1.GRAMMAR_LEDGER, encoding="utf-8"):
            parts = [p.strip() for p in ln.split("|")]
            if len(parts) > 3 and parts[1].startswith("TRIAL_LABOR"):
                led_rows[parts[1]] = parts[2]
    if led_rows.get("TRIAL_LABOR_W14") != W14_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W16") != W16_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W17") != W17_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W18") != W18_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W20") != W20_GRAMMAR_SHA16:
        print("PREP-GATE FAIL: ledger lineage mismatch "
              f"w14={led_rows.get('TRIAL_LABOR_W14')} "
              f"w16={led_rows.get('TRIAL_LABOR_W16')} "
              f"w17={led_rows.get('TRIAL_LABOR_W17')} "
              f"w18={led_rows.get('TRIAL_LABOR_W18')}")
        return 1
    if not tl1.self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1
    # G-PANEL (A1/A2): cutoff-frozen face, 48 members
    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices_full = {s: df[df.index <= cut] for s, df in prices_full.items()}
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(
               df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1
    # G-510300-FACE + G-LEG3ANCHOR (probe anchor + 18/18 alignment --
    # the batch-unique identity face, real data)
    md_ok, md = _leg3_anchor_gate()
    if not md_ok:
        print(f"PREP-GATE FAIL: G-LEG3ANCHOR {md['probe_face']} n_match="
              f"{md['n_match']}/18 fps={md['fingerprints_unique']}/18 "
              "-- face mismatch, fail-closed")
        return 1
    # G-ENTRY (A3): control-source anchor (raises on drift)
    ed = _entry_load()
    # G-GRAMMAR: W21 grammar pin
    grammar = None
    if os.path.exists(GRAMMAR_FILE):
        grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
            print(f"PREP-GATE FAIL: w21 grammar sha drift != frozen "
                  f"{FROZEN_SHA16}")
            return 1
        if grammar.get("control_source", {}).get("sha256_16") != ENTRY_SHA16:
            print("PREP-GATE FAIL: grammar control-source anchor drift")
            return 1
    # starts + passive 6m precompute (W16 caliber on the shared panel)
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen}")
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
    # cells-presence gate at the TAIL (identity-first-run law)
    if not os.path.exists(CANDS_FILE):
        print("PREP-GATE FAIL: w21_candidates.json absent -- generate "
              "pending (identity faces above ALL PASS on real data)")
        return 2
    prod = json.load(open(CANDS_FILE, encoding="utf-8"))
    if grammar is not None and str(prod.get("grammar_sha256", "")
                                   )[:16] != grammar["grammar_sha256"][:16]:
        print("PREP-GATE FAIL: cells grammar_sha256 != grammar anchor")
        return 1
    if len(prod.get("cells", [])) != 18:
        print(f"PREP-GATE FAIL: cells census {len(prod.get('cells', []))}"
              " != 18 -- roster drift, honest refuse")
        return 1
    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,
            **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": (grammar or {}).get("grammar_sha256"),
            "gates": {"G-PANEL": gp,
                      "G-510300-FACE": md["probe_face"],
                      "G-ENTRY": {"sha256_16": ENTRY_SHA16, "n": 173,
                                  "pass": True},
                      "G-LINEAGE": {"w14": W14_GRAMMAR_SHA16,
                                    **lineage, "ledger_match": True,
                                    "pass": True},
                      "G-EXITCFG": {"pass": True},
                      "G-ROSTER": {"intersection": [],
                                   "roster16_n": rost["roster16_n"],
                                   "pass": True},
                      "G-SEEDS": {"berths": seeds["berths"],
                                  "foreign_hits": [], "pass": True},
                      "G-LEG3ANCHOR": {"n_match": md["n_match"],
                                     "fingerprints_unique":
                                     md["fingerprints_unique"],
                                     "mask_days_count_collisions":
                                     md["mask_days_count_collisions"],
                                     "pass": True}},
            "starts": starts, "passive_6m_ret": passive_6m}
    _dump(PREP_FILE, prep)
    print(f"prep done: {len(starts)} starts, passive 6m precomputed -> "
          f"{PREP_FILE}")
    return 0


def _park_stamp():
    return tl17._park_stamp()


def _claim_machine_id() -> str:
    """Worker-claim identity (fleet/machine.json; honest fallback)."""
    return tl17._claim_machine_id()


def _worker_claim(entry_id: str, shard_key: str, result_ref: str) -> None:
    """r497 worker-side harvest handshake (tl17 verbatim reuse; only
    called from the real-burn completion paths -- the hermetic selftest
    never reaches here).  The worker NEVER writes runnable_pool.json
    (pool single-writer law)."""
    tl17._worker_claim(entry_id, shard_key, result_ref)


def cmd_screen(shard: int, shards: int, workers) -> int:
    import datetime
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDS_FILE, "w21_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w21()
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        # flush=True mandatory (r691 four-piece law, r800 live case)
        print(f"AUTOFILL-PARK: {_park_stamp()} screen RAM gate "
              f"{ram_min}GB < 4GB after bounded wait (r354/r379) -- "
              "honest zero-burn, NOT a crash (r491 park law); "
              "un-park = session flip when RAM frees", flush=True)
        print(f"SCREEN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law; r379 wait-law) -- honest "
              "refuse, pool retries when RAM frees", flush=True)
        return 2
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = tl1._load_leg("L")
    states = tl1.v3_state_series()
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()}}
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
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell_w21, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                               desc="screen cells",
                               initializer=tl1._init_worker,
                               initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    _worker_claim(f"TRIAL-LABOR-W21-SCREEN-SHARD-{shard}",
                  f"w21-screen-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def cmd_screen_finalize() -> int:
    """Screen-finalize: survival line (null p95 via the frozen W2 math)
    + G-face assertion battery + family-level survival readout (sec.4
    族级读数面) + sec.5 prediction accounting + ledger append +
    products."""
    print(f"=== {WAVE} screen-finalize ===")
    landed = tl16.tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if landed is not None:
        print(f"finalize: already landed (ledger total "
              f"{landed['total']}) -- idempotent no-op")
        return 0
    for p, what in ((GRAMMAR_FILE, "w21_grammar.json"),
                    (CANDS_FILE, "w21_candidates.json"),
                    (PREP_FILE, "prep_state.json")):
        if not os.path.exists(p):
            print(f"FINALIZE-GATE: {what} absent -- honest refuse "
                  "(identity face: no products to finalize)")
            return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"FINALIZE-GATE: grammar sha drift != {FROZEN_SHA16}")
        return 1
    _entry_load()   # G-ENTRY re-assert (raises on drift)
    ok, drift = _exitcfg_gate()
    if not ok:
        print(f"FINALIZE-GATE: G-EXITCFG drift {drift} -- VOID refuse")
        return 1
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("screen_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    try:
                        rows.append(json.loads(ln))
                    except Exception:
                        pass
    cand_rows = [r for r in rows
                 if not str(r["candidate_id"]).startswith("W21-NULL")]
    null_rows = [r for r in rows
                 if str(r["candidate_id"]).startswith("W21-NULL")]
    if len(cand_rows) != 18 or len(null_rows) != K_NULLS:
        print(f"FINALIZE-GATE: incomplete checkpoint ({len(cand_rows)}/18"
              f" cand, {len(null_rows)}/{K_NULLS} nulls) -- honest "
              "refuse (burn pending)")
        return 2
    # survival line (frozen W2 math; survive iff beat6m > null p95;
    # trial unit = CELL, candidate_id == cell_id this wave)
    p95, survivors = _finalize_math(cand_rows, null_rows)
    surv_set = set(survivors)
    for r in cand_rows:
        r["survives_screen"] = r["cell_id"] in surv_set
    null_p95 = round(float(p95), 6)
    band_hit = bool(NULL_P95_BAND[0] <= null_p95 <= NULL_P95_BAND[1])
    # family-level survival readout (sec.4 族级读数面 -- 族轴 ≠ 轴波)
    fam_axe = {}
    for fn in FN_MODULE:
        fr = [r for r in cand_rows if r["fn"] == fn]
        n_s = sum(1 for r in fr if r["survives_screen"])
        fam_axe[fn] = {"n_cells": len(fr), "n_survivors": n_s,
                       "survival_rate": round(n_s / max(1, len(fr)), 6),
                       "lawful_zero": n_s == 0}
    n_fam_surv = sum(1 for v in fam_axe.values() if v["n_survivors"] > 0)
    pred_51 = {"predicted_family_band": list(PRED_FAMILY_SURVIVORS_BAND),
               "observed_family_survivors": n_fam_surv,
               "verdict": "HIT" if PRED_FAMILY_SURVIVORS_BAND[0]
               <= n_fam_surv <= PRED_FAMILY_SURVIVORS_BAND[1] else "MISS",
               "cell_rate_band": list(PRED_CELL_RATE_BAND),
               "observed_cell_rate": round(len(survivors) / 18, 6)}
    ledger = tl1.append_ledger(SCREEN_BATCH, len(cand_rows) + len(null_rows),
                               "results/trial_labor_w21/w21_screen.json",
                               evidence_cutoff=CUTOFF)
    prod = {"wave": WAVE, "stage": "screen-finalize", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "n_cells": 18, "k_nulls": len(null_rows),
            "survival_rule": "beat6m_rate > null_p95 (prereg sec.4, "
                             "frozen W2 math, zero hand-picked)",
            "null_p95": null_p95, "null_p95_band": list(NULL_P95_BAND),
            "null_p95_band_hit": band_hit,
            "n_survivors": len(survivors), "survivors": survivors,
            "family_axe": fam_axe,
            "g_face_battery": {"G-ENTRY": {"sha256_16": ENTRY_SHA16},
                               "G-EXITCFG": {"pass": True},
                               "G-LEG3ANCHOR": {"pass": True}},
            "sec51_prediction_accounting": pred_51,
            "trials_ledger": ledger}
    _dump(SCREEN_FILE, prod)
    with open(SCREEN_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w21,
                           extrasaction="ignore")
        w.writeheader()
        for r in sorted(cand_rows + null_rows,
                        key=lambda r: r["cell_id"]):
            w.writerow({k: r.get(k) for k in csv_cols_screen_w21})
    print(f"screen-finalize done: null p95 {null_p95} "
          f"(band {'HIT' if band_hit else 'MISS'}), survivors "
          f"{len(survivors)}/18")
    fam_summary = {k: (v["n_survivors"], v["n_cells"])
                  for k, v in fam_axe.items()}
    print(f"family axe: {json.dumps(fam_summary, sort_keys=True)}")
    print(f"sec.5.1 prediction accounting: {json.dumps(pred_51)}")
    print(f"products: {SCREEN_FILE} + {SCREEN_CSV} "
          f"(ledger total {ledger['total']})")
    return 0


# --------------------------------------------------------------- judge (s3)
def _dual_nulls_w21(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.2):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W21 unc-berth seed binding rng([20661000, cell_idx]), cell_idx<18.
    Math imported verbatim from tl2._dual_nulls_w2 (import law)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _judge_cell_w21(cell):
    """One W21 judged cell (prereg sec.3 family-block, pool worker):
    dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full curves
    + window-grid beat vs passive + regime segments + dual nulls (W21
    unc berth) + member-metrics raw materials (four-dim reform face,
    sec.4 canon)."""
    st = tl1._ST
    cand = cell["cand"]
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "sig_params": cand["sig_params"],
           "block": cell["block"]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w21(cand, prices, P, st["states"])
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, *_ = run_candidate_curve_w21(
                cand, prices, P, st["states"])
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "regime_start_windows":
                         {"bear": 0, "bull": 0, "chop": 0, "na": 0},
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
                dd = s_series.iloc[p] if p < len(s_series) else None
                st_ = tl1.REGIME_MAP.get(dd, "na") if dd == dd else "na"
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
                     "degenerate": False}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_sharpe_full_x2"] = legs[leg]["sharpe_full_x2"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
            out["legL_beat6m_rate"] = legs[leg]["beat"].get(
                "6m", {}).get("rate")
            out["legL_beat12m_rate"] = legs[leg]["beat"].get(
                "12m", {}).get("rate")
            n_bars = max(2, len(eq))
            out["legL_annualized_ret"] = round(
                float((eq.iloc[-1] / eq.iloc[0]) ** (252.0 / n_bars)
                     - 1.0), 6)
            seg_sharpes = []
            for seg in ("bear", "bull", "chop"):
                mask = (tl1.REGIME_MAP.get(s_series.reindex(
                    eq.index).iloc[i], "na") == seg
                    for i in range(len(eq)))
                marr = np.fromiter((1.0 if x else 0.0 for x in mask),
                                   dtype=float, count=len(eq))
                if marr.sum() < 60:
                    continue
                dr = daily.values[marr > 0]
                if dr.std() > 0:
                    seg_sharpes.append(float(
                        dr.mean() / dr.std() * math.sqrt(252)))
            out["legL_regime_min_sharpe"] = (round(min(seg_sharpes), 4)
                                             if seg_sharpes else None)
            out["descriptive"] = tl2._descriptive_face(eq, eq2)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_sharpe_full_x2"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
        out["legL_beat6m_rate"] = None
        out["legL_beat12m_rate"] = None
        out["legL_annualized_ret"] = None
        out["legL_regime_min_sharpe"] = None
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w21(
        r if len(r) else np.zeros(30), cell["i"])
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def _block_selection(screen):
    """sec.3 frozen deterministic family-block selection: any family
    (block) with >=1 cell surviving screen enters JUDGE with ALL its
    cells (block completeness law, 族级配对读数面); 18 cells full-set
    < cap 90 (asserted live)."""
    prod = json.load(open(CANDS_FILE, encoding="utf-8"))
    fam_cells = {}
    for c in prod["cells"]:
        fam_cells.setdefault(c["fn"], []).append(c)
    surv = set(screen["survivors"])
    blocks = []
    for fn in FN_MODULE:      # canonical family order
        cells = fam_cells.get(fn, [])
        n_surv = sum(1 for c in cells if c["cell_id"] in surv)
        if n_surv >= 1:
            blocks.append({"block": fn, "n_cells": len(cells),
                           "n_surviving_cells": n_surv})
    capped = sum(b["n_cells"] for b in blocks) > JUDGE_CAP_CELLS
    return blocks, capped


def cmd_judge_prep() -> int:
    """Judge-prep: screen-finalize gate + T18 manifest + dual-leg
    census/member gates + per-(leg, window) starts/passive + family-
    block selection + judge state serialization."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w21_screen.json "
              "absent) -- honest refuse (identity face)")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and str(screen.get("grammar_sha256", ""))[:16] \
            != FROZEN_SHA16:
        print(f"JUDGE-PREP-GATE FAIL: screen grammar sha != frozen "
              f"{FROZEN_SHA16}")
        return 1
    man = json.load(open(tl1.T18_MANIFEST, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    blocks, capped = _block_selection(screen)
    if not blocks:
        print("JUDGE-PREP-GATE: zero surviving families (honest "
              "negative screen -- judge batch empty, 族级 lawful-zero "
              "readout already landed in screen face)")
        return 2
    starts, passive = {}, {}
    jstate = {"wave": WAVE, "prereg": PREREG,
              "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
              "grammar_sha256": screen["grammar_sha256"],
              "blocks": blocks, "n_blocks": len(blocks),
              "cell_cap": JUDGE_CAP_CELLS,
              "block_cap_applied": capped}
    reform_baseline = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift")
            return 1
        if leg == "L":
            # reform-baseline precompute (light face; sec.4 canon):
            # five-member EW annualized + registered-six daily returns
            five = [s for s in ("510300", "510050", "510500", "512100",
                                "588000") if s in P["close"].columns]
            cl = P["close"][five]
            ew = cl.pct_change().mean(axis=1).fillna(0.0).cumsum()
            reform_baseline["five_member_ew_ann"] = round(
                float((1.0 + ew.iloc[-1]) ** (252.0 / max(2, len(ew)))
                     - 1.0), 6)
            reform_baseline["reg_rets"] = {
                s: [round(float(x), 8)
                    for x in P["close"][s].pct_change().fillna(0.0).values]
                for s in REGISTERED_D6_SYMBOLS
                if s in P["close"].columns}
        starts[leg], passive[leg] = {}, {}
        close = P["close"]
        n = len(idx)
        for wname, w in tl1.WINDOWS.items():
            if leg == "L":
                st_ = [p for p in range(n)
                       if idx[p] >= tl1.LEG_L_FLOOR
                       and p >= tl1.WARMUP_TD
                       and p <= n - 1 - w
                       and listed.iloc[p] >= tl1.MIN_LISTED]
            else:
                st_ = [p for p in range(n)
                       if idx[p] >= tl1.LEG_D_FLOOR
                       and p >= tl1.WARMUP_TD
                       and p <= n - 1 - w]
            if len(st_) != tl1.FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st_)} != census "
                      f"{tl1.FROZEN_CENSUS[leg][wname]}")
                return 1
            pas = {}
            for p in st_:
                sdate, edate = idx[p], idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = tl1.passive_rel(close, syms, sdate, edate)
                pas[str(p)] = round(float(rel.iloc[-1] - 1.0), 6)
            starts[leg][wname] = st_
            passive[leg][wname] = pas
    jstate["starts"] = starts
    jstate["passive"] = passive
    jstate["reform_baseline"] = reform_baseline
    # judged cell list: family-major, roster order within family
    # (cell_idx binding for the unc seed streams; i < 18 declared band)
    prod = json.load(open(CANDS_FILE, encoding="utf-8"))
    fam_cells = {}
    for c in prod["cells"]:
        fam_cells.setdefault(c["fn"], []).append(c)
    judged = []
    i = 0
    for b in blocks:
        for c in fam_cells[b["block"]]:
            judged.append({"cell_id": c["cell_id"], "kind": "cand",
                           "cand": _j(c), "block": b["block"], "i": i})
            i += 1
    if capped or i > JUDGE_CAP_CELLS:
        print(f"JUDGE-PREP-GATE FAIL: cell cap {i} > {JUDGE_CAP_CELLS} "
              "-- prereg sec.0 cap clause (18 full-set) violated")
        return 1
    jstate["judged_cells"] = judged
    _dump(JUDGE_STATE_FILE, jstate)
    print(f"judge-prep done: {len(blocks)} family blocks, "
          f"{len(judged)} judged cells -> {JUDGE_STATE_FILE}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    if not os.path.exists(JUDGE_STATE_FILE):
        print("JUDGE-GATE: judge_state.json absent -- run judge-prep")
        return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"AUTOFILL-PARK: {_park_stamp()} judge RAM gate "
              f"{ram_min}GB < 4GB after bounded wait (r354/r379) -- "
              "honest zero-burn, NOT a crash (r491 park law); "
              "un-park = session flip when RAM frees", flush=True)
        print(f"JUDGE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait -- honest refuse (RAM gate r354)", flush=True)
        return 2
    # heavy worker state rebuilt live (jstate is the light metadata
    # face; W19 cmd_judge caliber): legs + starts + passive
    state = {"wave": WAVE, "starts": jstate["starts"],
             "passive": jstate["passive"],
             "judged_cells": jstate["judged_cells"],
             "states": tl1.v3_state_series()}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        state[f"prices_{leg}"] = prices
        state[f"P_{leg}"] = P
        state[f"idx_{leg}"] = idx
    mine = [c for i, c in enumerate(jstate["judged_cells"])
            if i % shards == shard]
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
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell_w21, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                               desc="judge cells",
                               initializer=tl1._init_worker,
                               initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    _worker_claim("TRIAL-LABOR-W21-JUDGE",
                  f"w21-judge-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def cmd_judge_finalize() -> int:
    """Judge-finalize: G1'v2 + G2-v2 verdicts + M1 t-face + family PBO
    + the REFORM FACE BLOCK (member_metrics four-dim + dual-nulls +
    g2_reform_fdr4d + D6 + top-3 -- W16 sec.8 gap lesson, prereg sec.4
    mandated) + family-axe readout (三族三行 lawful-zero face) + E[FP]
    disclosure + ledger append + products."""
    print(f"=== {WAVE} judge-finalize ===")
    landed = tl16.tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if landed is not None:
        print(f"finalize: already landed (ledger total "
              f"{landed['total']}) -- idempotent no-op")
        return 0
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),):
        if not os.path.exists(p):
            print(f"FINALIZE-GATE: {what} absent -- honest refuse "
                  "(identity face: judge prep/burn pending)")
            return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    try:
                        rows.append(json.loads(ln))
                    except Exception:
                        pass
    expected = len(jstate["judged_cells"])
    if len(rows) != expected:
        print(f"FINALIZE-GATE: incomplete checkpoint ({len(rows)}/"
              f"{expected}) -- honest refuse (judge burn pending)")
        return 2
    by_id = {r["cell_id"]: r for r in rows}
    judged = [by_id[c["cell_id"]] for c in jstate["judged_cells"]]
    n_judged = len(judged)
    batch_cells = n_judged
    prev = tl1.ledger_head()
    n_trials = prev["total"]   # screen already landed in the chain
    e_fp = round(0.05 * n_judged, 2)
    # -- per-cell verdicts (G1'v2 + DSR + M1 t-face)
    for r in judged:
        rets = r.get("legL_daily_returns") or []
        r["zero_variance"] = bool(rets) and len(set(
            float(x) for x in rets)) == 1
        if r["legs"].get("L", {}).get("degenerate") or not rets:
            r["dsr"] = None
            r["g1_pass"] = False
            r["verdict"] = "fail-degenerate"
            r["t_face"] = None
            continue
        g1 = tl1.g1_prime_v2(r["legL_sharpe_full"], rets, batch_cells,
                             pool="core48", n_trades=r["legL_n_trades"],
                             n_entries=r["legL_n_entries"])
        if r["zero_variance"]:
            r["g1_prime_v2"] = g1
            r["dsr"] = None
        else:
            dsr = tl1.deflated_sharpe_ratio(rets, n_trials=n_trials)
            r["g1_prime_v2"] = g1
            r["dsr"] = {"dsr": round(float(dsr["dsr"]), 6),
                        "n_trials": n_trials}
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample" if not r[
                            "sample_sufficient"] else "fail")
        t_stat = science_gates.t_from_sharpe(r["legL_sharpe_full"], len(rets))
        r["t_face"] = science_gates.m1_t_value_gate(t_stat)
    # -- family PBO (CSCV 8 blocks; family = mech-module namespace;
    # <8 n/a -- near_52w_high 6 cells honest insufficient)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r.get("module"), []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        series = {r["cell_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs if r.get("legL_daily_returns")}
        if len(rs) < 8 or len(series) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        mat = tl1.align_returns(series)
        pbo = tl1.cscv_pbo(mat)
        pbos[fam] = {"pbo": round(float(pbo["pbo"]) if isinstance(
            pbo, dict) else float(pbo), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # -- G2 registration columns (historical caliber, sec.4(b))
    for r in judged:
        if r.get("g1_prime_v2") is None or r.get("dsr") is None:
            r["g2_registration_v2"] = None
            continue
        r["g2_registration_v2"] = tl1.g2_registration_v2(
            r["g1_pass"], r["dsr"], r.get("family_pbo"))
    # -- REFORM FACE BLOCK (sec.4(a) canon; W16 sec.8 gap lesson)
    rb = jstate.get("reform_baseline", {})
    base_ann = rb.get("five_member_ew_ann")
    reg_rets = {}
    for s, vals in (rb.get("reg_rets") or {}).items():
        if vals:
            reg_rets[s] = pd.Series(vals)
    member_metrics, batch_p, cand_rets = {}, {}, {}
    for r in judged:
        if (r["legs"].get("L", {}).get("degenerate")
                or r.get("zero_variance")):
            continue
        mm = {
            "ret": {"sharpe_full_L": r["legL_sharpe_full"],
                    "annualized_ret_L": r["legL_annualized_ret"],
                    "return_ceiling_O1126": (
                        None if base_ann is None
                        else round(r["legL_annualized_ret"] - base_ann,
                                   6)),
                    "beat6m_rate_L": r["legL_beat6m_rate"],
                    "beat12m_rate_L": r["legL_beat12m_rate"]},
            "robust": {"cost_x2_sharpe_L": r["legL_sharpe_full_x2"],
                       "regime_min_sharpe_L": r[
                           "legL_regime_min_sharpe"],
                       "bootstrap_ci_low_L": r["dual_nulls"]
                       ["bootstrap_ci"][0]},
            "anti_overfit": {"family_pbo": r.get("family_pbo"),
                             "d6_max_abs_corr": None},
            "anti_luck": {"batch_dsr": (r["dsr"] or {}).get("dsr")},
        }
        member_metrics[r["cell_id"]] = mm
        batch_p[r["cell_id"]] = r["dual_nulls"]["signflip_p"]
        if r.get("legL_daily_returns"):
            cand_rets[r["cell_id"]] = pd.Series(
                r["legL_daily_returns"]).round(8)
    dsr_by_id = {cid: member_metrics[cid]["anti_luck"]["batch_dsr"]
                 for cid in member_metrics}
    eligible_pool = [cid for cid in member_metrics
                     if cid in cand_rets]
    admitted, rejected, d6 = tl2._d6_admit_core(
        sorted(eligible_pool), cand_rets, reg_rets, dsr_by_id)
    for cid, d in d6.items():
        member_metrics[cid]["anti_overfit"]["d6_max_abs_corr"] = \
            d["max_corr_vs_registered"]
    g2 = g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS,
                         REFORM_SUB_WEIGHTS, batch_p, q=REFORM_Q_LEVEL)
    if g2.get("error"):
        print(f"FINALIZE-GATE FAIL: reform gate error {g2['error']}")
        return 2
    eligible_reform = [cid for cid, m in g2["members"].items()
                       if m["eligible_reform"] and cid in admitted]
    eligible_reform.sort(key=lambda c: (
        -(g2["members"][c]["composite"] or 0.0), c))
    onboard = eligible_reform[:REFORM_TOPN_PER_WAVE]
    reform_prod = {"wave": WAVE, "stage": "reform-face",
                   "evidence_cutoff": CUTOFF,
                   **tl1.cutoff_meta(CUTOFF),
                   "member_metrics": _j(member_metrics),
                   "batch_p_values": batch_p,
                   "g2_reform": _j(g2),
                   "d6": {"admitted": admitted, "rejected": rejected},
                   "eligible_reform": eligible_reform,
                   "top_n_per_wave": REFORM_TOPN_PER_WAVE,
                   "onboard_list": [{"cell_id": c,
                                     "composite":
                                     g2["members"][c]["composite"]}
                                    for c in onboard],
                   "five_member_ew_baseline_ann": base_ann,
                   "zero_variance_arms_excluded": sorted(
                       [r["cell_id"] for r in judged
                        if r.get("zero_variance")]),
                   "constants": {"dim_weights": REFORM_DIM_WEIGHTS,
                                 "sub_weights": REFORM_SUB_WEIGHTS,
                                 "q": REFORM_Q_LEVEL,
                                 "topn": REFORM_TOPN_PER_WAVE,
                                 "ceiling_baseline":
                                 "five_member_ew (O-1555 five)"}}
    _dump(REFORM_FILE, reform_prod)
    # -- family-axe readout (sec.4 族级读数面: 三族三行 lawful-zero 照报)
    family_axe = {}
    for fn in FN_MODULE:
        rs = [r for r in judged if r["fn"] == fn]
        family_axe[fn] = {
            "n_cells": len(rs),
            "n_g1_pass": sum(1 for r in rs if r.get("g1_pass")),
            "n_eligible_v2": sum(1 for r in rs
                                 if (r.get("g2_registration_v2") or {})
                                 .get("eligible_v2")),
            "n_eligible_reform": sum(1 for r in rs
                                      if r["cell_id"] in
                                      eligible_reform),
            "best_sharpe_full_L": max(
                (r.get("legL_sharpe_full") or 0.0) for r in rs)
            if rs else None,
            "lawful_zero": bool(rs) and not any(
                (r.get("g2_registration_v2") or {}).get("eligible_v2")
                or r["cell_id"] in eligible_reform for r in rs)}
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judged,
                               "results/trial_labor_w21/w21_judge.json",
                               evidence_cutoff=CUTOFF)
    eligible_v2 = [r["cell_id"] for r in judged
                   if (r.get("g2_registration_v2") or {}).get(
                       "eligible_v2")]
    pred_51 = {"predicted_judge_reform_band":
               list(PRED_JUDGE_REFORM_BAND),
               "observed_eligible_reform": len(eligible_reform),
               "verdict": "HIT" if PRED_JUDGE_REFORM_BAND[0]
               <= len(eligible_reform) <= PRED_JUDGE_REFORM_BAND[1]
               else "MISS"}
    prod = {"wave": WAVE, "stage": "judge-finalize", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": jstate["grammar_sha256"],
            "n_blocks": jstate["n_blocks"],
            "block_cap_applied": jstate["block_cap_applied"],
            "n_judged": n_judged, "E_FP_nominal": e_fp,
            "g1_pass_n": sum(1 for r in judged if r.get("g1_pass")),
            "eligible_v2": eligible_v2,
            "eligible_reform": eligible_reform,
            "onboard_list": reform_prod["onboard_list"],
            "family_pbo": pbos,
            "family_axe": family_axe,
            "sec51_prediction_accounting": pred_51,
            "verdicts": {r["cell_id"]: r["verdict"] for r in judged},
            "cells": _j(judged),
            "trials_ledger": ledger}
    _dump(JUDGE_FILE, prod)
    print(f"judge-finalize done: {n_judged} cells, G1 "
          f"{prod['g1_pass_n']}, G2-v2 {len(eligible_v2)}, "
          f"eligible_reform {len(eligible_reform)}, onboard "
          f"{len(onboard)}; E[FP]={e_fp}")
    fam_summary = {k: (v["n_g1_pass"], v["n_cells"])
                  for k, v in family_axe.items()}
    print(f"family axe: {json.dumps(fam_summary, sort_keys=True)}")
    print(f"products: {JUDGE_FILE} + {REFORM_FILE} "
          f"(ledger total {ledger['total']})")
    return 0


def cmd_intake() -> int:
    """s4 intake (prereg sec.6): D6 binding gate face -- eligible_reform
    -> TRIAL-ENTRYGRM-* paper-probation listing (registration itself =
    separate GM face per law); lawful-zero when none."""
    print(f"=== {WAVE} intake ===")
    if not os.path.exists(REFORM_FILE):
        print("INTAKE-GATE: w21_reform_face.json absent -- judge "
              "finalize pending")
        return 2
    reform = json.load(open(REFORM_FILE, encoding="utf-8"))
    onboard = reform.get("onboard_list", [])
    prod = {"wave": WAVE, "stage": "intake",
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "n_eligible": len(onboard),
            "accounts": [{"name": f"TRIAL-ENTRYGRM-{i+1:02d}",
                          "cell_id": o["cell_id"],
                          "composite": o["composite"]}
                         for i, o in enumerate(onboard)],
            "lawful_zero": len(onboard) == 0,
            "note": "registration + paper-probation onboarding = "
                    "separate GM slice (D6 binding gate -> "
                    "STRATEGY_LIBRARY row); marks non-trial ledger +0; "
                    "negative wave -> entry-grammar GENERATE supply "
                    "line demotion canonical basis (prereg sec.0 "
                    "supply-contract clause)"}
    _dump(INTAKE_FILE, prod)
    print(f"intake done: n_eligible {len(onboard)} "
          f"({'lawful-zero' if not onboard else 'listing'}) -> "
          f"{INTAKE_FILE}")
    return 0


# ------------------------------------------------------------ selftest (hermetic)
def cmd_selftest() -> int:
    """Hermetic selftest (zero panel load, zero network, zero engine
    burn; synthetic fixtures only).  The real-data identity faces run
    via the three-command first-run law (screen-prep / screen-finalize
    / judge-prep)."""
    import tempfile
    ok_n = 0
    fails = []

    def ok(name, cond, detail=""):
        nonlocal ok_n
        if cond:
            ok_n += 1
            print(f"[PASS] {name}")
        else:
            fails.append(name)
            print(f"[FAIL] {name} {detail}")

    # L1: GBK entry law (r236)
    ok("L1 gbk-reconfigure entry law",
       (sys.stdout.encoding or "").lower() == "utf-8")
    # L2: A9 ExitConfig default table == frozen values (live import,
    # read-only; X=template_default consumed face)
    ok("L2 exitcfg defaults == A9 frozen table", *_exitcfg_gate())
    # L3: fn masks on synthetic series (leg-3-verbatim math bites)
    idx = pd.date_range("2020-01-01", periods=400, freq="B")
    rng = np.random.default_rng(7)
    close = pd.Series(np.exp(np.cumsum(rng.normal(0, 0.01, 400))),
                      index=idx)
    volume = pd.Series(100.0 + rng.random(400) * 50.0, index=idx)
    amount = close * volume
    open_ = close * (1.0 + rng.normal(0, 0.004, 400))
    m_lq = _mask_liq_rank_gate(amount, 0.80, "level")
    r_amt = _liq_rank(amount)
    ok("L3a liq_rank_gate level bite",
       int(m_lq.sum()) > 0
       and all(bool(r_amt.iloc[i] >= 0.80) for i in range(400)
               if m_lq.iloc[i]))
    m_lqo = _mask_liq_rank_gate(amount, 0.80, "onset")
    # onset semantics: first bar of each >=thr stretch
    hi = (r_amt.fillna(0) >= 0.80).to_numpy()
    onset = np.zeros(400, dtype=bool)
    onset[1:] = hi[1:] & ~hi[:-1]
    ok("L3b liq_rank_gate onset semantics",
       int(m_lqo.sum()) > 0 and bool((m_lqo.to_numpy() == onset).all()))
    m_gp = _mask_gap_reversal_gate(close, open_, 0.01)
    gap = (open_ / close.shift(1) - 1.0)
    ok("L3c gap_reversal_gate bite",
       int(m_gp.sum()) > 0
       and all(bool(gap.iloc[i] <= -0.01) for i in range(400)
               if m_gp.iloc[i]))
    m_on = _mask_on_share_rank(close, open_, 20, 0.50)
    ok("L3d on_share_rank bite",
       int(m_on.sum()) > 0
       and all(bool(_liq_rank(_on_share_series(close, open_, 20)
                              ).iloc[i] <= 0.50)
               for i in range(400) if m_on.iloc[i]))
    # L4: census enumerator -- 18 cells, 8/4/6, A/B 3/15, anchors
    roster = build_roster_w21()
    fam_n = {}
    for c in roster:
        fam_n[c["fn"]] = fam_n.get(c["fn"], 0) + 1
    anchors = [c for c in roster if c["family"] == "A"]
    ok("L4 census 8/4/6 + A3/B15 + anchor params",
       len(roster) == 18 and fam_n == {"liq_rank_gate": 8,
                                       "gap_reversal_gate": 4,
                                       "on_share_rank": 6}
       and len(anchors) == 3
       and {a["fn"] for a in anchors} == set(FN_MODULE)
       and any(a["fn"] == "liq_rank_gate"
               and a["sig_params"] == {"thr": 0.80, "mode": "level"}
               for a in anchors)
       and any(a["fn"] == "gap_reversal_gate"
               and a["sig_params"] == {"depth": 0.02}
               for a in anchors)
       and any(a["fn"] == "on_share_rank"
               and a["sig_params"] == {"n": 20, "thr": 0.35}
               for a in anchors)
       and len({c["cell_id"] for c in roster}) == 18)
    # L4b: determinism (roster rebuild byte-identical)
    ok("L4b census deterministic",
       build_roster_w21() == roster)
    # L5: fixed execution config == DEFAULT_AXIS + 16 none; consumed
    # faces pinned (X/S/T consumption chain)
    ok("L5 single execution config == engine-default face",
       AXIS_FIXED == [tl1.DEFAULT_AXIS[0], X_CONSUMED, S_CONSUMED,
                      T_CONSUMED] + ["none"] * 16
       and AXIS_FIXED[1] == "template_default"
       and AXIS_FIXED[2] == "equal_weight"
       and AXIS_FIXED[3] == "daily_signal"
       and all(c["axis"] == AXIS_FIXED for c in roster))
    # L6: engine params on the fixed face = B-caliber engine defaults
    # (template None: X=template_default -> {} + None for EVERY cell,
    # A-label anchors included -- the A/B label is a researcher
    # designation, not a registered-template family this wave)
    p0, pa0 = tl1.candidate_engine_params(roster[0], None)
    pA, paA = tl1.candidate_engine_params(anchors[0], None)
    ok("L6 engine params {} + None all cells (B-caliber)",
       p0 == {} and pa0 is None and pA == {} and paA is None)
    # L7: null draw determinism + fixed axis + band structure
    p1, ax1, r1 = _null_axis_draw_w21(7)
    p2, ax2, r2 = _null_axis_draw_w21(7)
    p3, ax3, r3 = _null_axis_draw_w21(8)
    ok("L7 null draw determinism + fixed axis zero-draw",
       p1 == p2 and ax1 == ax2 == list(AXIS_FIXED) and ax1[1]
       == X_CONSUMED
       and p1 in tuple(tl1.NULL_P_REGIMES)
       and r1.random() != r3.random())
    # L8: grammar serialization determinism + anchor constants
    g1s, g2s = build_grammar_w21(), build_grammar_w21()
    ok("L8 grammar deterministic + lineage anchors",
       g1s["grammar_sha256"] == g2s["grammar_sha256"]
       and g1s["control_source"]["sha256_16"] == ENTRY_SHA16
       and g1s["w14_lineage"]["grammar_sha16"] == W14_GRAMMAR_SHA16
       and g1s["w16_grammar_ref"]["grammar_sha16"] == W16_GRAMMAR_SHA16
       and g1s["w17_grammar_ref"]["grammar_sha16"] == W17_GRAMMAR_SHA16
       and g1s["w18_grammar_ref"]["grammar_sha16"] == W18_GRAMMAR_SHA16
       and g1s["w20_grammar_ref"]["grammar_sha16"] == W20_GRAMMAR_SHA16
       and g1s["n_cells"] == 18 and g1s["family_split"] == {"A": 3,
                                                            "B": 15}
       and g1s["screen_trials"] == 218
       and g1s["closed_family_check"]["in_closed"] is False)
    # L8b: FROZEN pin check (Slice-B face)
    if FROZEN_SHA16:
        ok("L8b frozen sha pin == built grammar",
           g1s["grammar_sha256"][:16] == FROZEN_SHA16)
    else:
        ok_n += 1
        print("[PASS] L8b frozen pin not yet set (pre-generate face)")
    # L9: family-block selection deterministic rule (roster math face;
    # the file-reading _block_selection itself is exercised by the
    # real-data judge-prep first-run)
    fam_cells = {}
    for c in roster:
        fam_cells.setdefault(c["fn"], []).append(c)
    surv = {roster[0]["cell_id"], roster[-1]["cell_id"]}
    blocks_manual = [{"block": fn, "n_cells": len(fam_cells[fn]),
                      "n_surviving_cells": sum(
                          1 for c in fam_cells[fn]
                          if c["cell_id"] in surv)}
                     for fn in FN_MODULE
                     if sum(1 for c in fam_cells[fn]
                            if c["cell_id"] in surv) >= 1]
    ok("L9 family-block selection rule (survivor family enters full)",
       len(blocks_manual) == 2
       and {b["block"] for b in blocks_manual}
       == {roster[0]["fn"], roster[-1]["fn"]}
       and all(b["n_cells"] == len(fam_cells[b["block"]])
               for b in blocks_manual)
       and sum(b["n_cells"] for b in blocks_manual) <= JUDGE_CAP_CELLS)
    # L10: reform constants import integrity (禁手抄律)
    ok("L10 reform constants integrity",
       reform_weight_freeze_integrity()
       and abs(sum(REFORM_DIM_WEIGHTS.values()) - 1.0) < 1e-9
       and REFORM_TOPN_PER_WAVE == 3 and REFORM_Q_LEVEL == 0.10
       and set(REFORM_DIM_WEIGHTS) == {"ret", "robust",
                                       "anti_overfit", "anti_luck"})
    # L11: g2_reform_fdr4d joint verdict on a synthetic batch
    mm = {f"C{i}": {"ret": {"sharpe_full_L": 1.0 + i * 0.1,
                            "annualized_ret_L": 0.1,
                            "return_ceiling_O1126": 0.01,
                            "beat6m_rate_L": 0.6,
                            "beat12m_rate_L": 0.55},
                    "robust": {"cost_x2_sharpe_L": 0.8,
                               "regime_min_sharpe_L": 0.3,
                               "bootstrap_ci_low_L": 0.001},
                    "anti_overfit": {"family_pbo": 0.1,
                                     "d6_max_abs_corr": 0.2},
                    "anti_luck": {"batch_dsr": 0.9}}
          for i in range(10)}
    bp = {f"C{i}": (0.001 if i < 2 else 0.5) for i in range(10)}
    g2t = g2_reform_fdr4d(mm, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                          bp, q=REFORM_Q_LEVEL)
    ok("L11 g2_reform_fdr4d synthetic joint verdict",
       not g2t.get("error") and g2t["members"]["C0"]["fdr_pass"]
       and not g2t["members"]["C5"]["fdr_pass"]
       and g2t["members"]["C0"]["composite"] is not None)
    # L12: dual-nulls W21 unc-berth binding (determinism)
    r = np.random.default_rng(3).normal(0.0005, 0.01, 300)
    d1 = _dual_nulls_w21(r, 5)
    d2 = _dual_nulls_w21(r, 5)
    ok("L12 dual-nulls unc-berth determinism",
       d1 == d2 and d1["B"] == 2000 and d1["P"] == 2000
       and len(d1["bootstrap_ci"]) == 2)
    # L13: exclusion matcher (new-namespace zero-hit + planted-hit
    # catch -- 对号 semantics)
    rows = [{"module": "mean_reversion", "fn": "pullback_bounce",
             "sig_params": {"trend_n": 60, "pullback_n": 10},
             "axis": list(AXIS_FIXED), "face": "planted"}]
    ok("L13 exclusion matcher zero-hit + planted catch",
       _excluded_w21(roster[0], rows) is None
       and _excluded_w21({"module": "mean_reversion",
                          "fn": "pullback_bounce",
                          "sig_params": {"trend_n": 60,
                                         "pullback_n": 10},
                          "axis": list(AXIS_FIXED)}, rows) == "planted")
    # L14: fingerprint dedup comparator (identical masks collapse-
    # detected; different masks pass -- T-84s3 face)
    m_a = pd.DataFrame({"S": [0, 1, 1, 0]}, index=idx[:4]) > 0
    m_b = pd.DataFrame({"S": [1, 0, 0, 1]}, index=idx[:4]) > 0
    ok("L14 fingerprint dedup comparator",
       tl1._fingerprint(m_a) == tl1._fingerprint(m_a.copy())
       and tl1._fingerprint(m_a) != tl1._fingerprint(m_b))
    # L15: seeds gate (berths + band disjoint -- live registry read,
    # read-only, hermetic)
    ok("L15 G-SEEDS berths + band disjoint", *_seeds_gate())
    # L16: products writer idempotence
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "x.json")
        _dump(fp, {"a": 1})
        _dump(fp, {"a": 1})
        ok("L16 dump idempotent + ascii-safe",
           json.load(open(fp, encoding="utf-8")) == {"a": 1})
    print(f"selftest: {ok_n} PASS, {len(fails)} FAIL"
          f"{'' if not fails else ' -- ' + ', '.join(fails)}")
    return 0 if not fails else 1


# ------------------------------------------------------------------ argparse
def _build_parser():
    p = argparse.ArgumentParser(description=WAVE + " runner "
                               "(entry-grammar GENERATE regression "
                               "census; frozen prereg " + PREREG + ")")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grammar", help="serialize w21_grammar.json")
    sub.add_parser("generate", help="18-cell census + fn-gates live + "
                   "exclusion book + G-LEG3ANCHOR + w21_candidates.json "
                   "+ ledger row")
    sub.add_parser("status", help="product presence + gates")
    sub.add_parser("screen-prep", help="fail-closed gates + passive 6m")
    sp = sub.add_parser("screen", help="screen shard burn")
    sp.add_argument("shard", type=int)
    sp.add_argument("shards", type=int)
    sp.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize", help="survival line + family axe "
                   "+ G-face battery + ledger append")
    sub.add_parser("judge-prep", help="family blocks + dual-leg judge "
                   "state")
    jp = sub.add_parser("judge", help="judge shard burn")
    jp.add_argument("shard", type=int)
    jp.add_argument("shards", type=int)
    jp.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize", help="verdicts + reform face + "
                   "family axe + ledger append")
    sub.add_parser("intake", help="s4 intake face")
    sub.add_parser("selftest", help="hermetic selftest")
    return p


def main(argv=None):
    args = _build_parser().parse_args(argv)
    return {"grammar": cmd_grammar, "generate": cmd_generate,
            "status": cmd_status, "screen-prep": cmd_screen_prep,
            "screen": lambda: cmd_screen(args.shard, args.shards,
                                         args.workers),
            "screen-finalize": cmd_screen_finalize,
            "judge-prep": cmd_judge_prep,
            "judge": lambda: cmd_judge(args.shard, args.shards,
                                       args.workers),
            "judge-finalize": cmd_judge_finalize,
            "intake": cmd_intake,
            "selftest": cmd_selftest}[args.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
