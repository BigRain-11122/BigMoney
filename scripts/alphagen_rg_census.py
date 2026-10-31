#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E16 alphagen slice-2 random-grammar stock census (pool-sharded runner).

Prereg (FROZEN, precedes this build, precedes ANY run): research/
E16_ALPHAGEN_RG_CENSUS_P1.md -- measurement census batch, K=200 formula
draws (120 depth-1 + 80 depth-2) from the vendored A158 29-op grammar over
8 base inputs x 5 windows, per-formula daily cross-sectional Spearman
rank-IC vs 1d close-to-close forward return, window 2018-01-01..cutoff
(2026-10-09 D2 lockbox), B=200 per-date same-mask factor-rank permutation
nulls per formula (t23 machinery verbatim import), verdict
census_holds = observed_family_max_abs_icir > null_family_p95.

Roster (leg-1 frozen facts): results/alphagen_rg/e16_roster.json
sha16=1d06d218b2cbf870. Seeds registered at prereg freeze: science_gates.
SEED_REGISTRY e16_alphagen_rg_gen=20620000 / e16_alphagen_rg_null=20620100.

Laws honored: zero judgment claims / zero registration power / zero engine
runs / zero network; NaN policy = full-window (n==d, t23 primitives law);
MIN_CROSS=100 / MIN_PERIODS=30 / MAX_SKIP_FRAC=0.10 (t23 verbatim);
per-formula checkpoint resume across kills; refuse-if-exists finalize.

Usage:
  python scripts/alphagen_rg_census.py run --shard k --shards 12 [--workers N]
  python scripts/alphagen_rg_census.py finalize
  python scripts/alphagen_rg_census.py status
  python scripts/alphagen_rg_census.py selftest

-- bm-b r878 leg-2 | marks +0 | SEED substreams consumed only on run
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg                                    # noqa: E402
import stock_face_furnace as sff                              # noqa: E402
import rev_osc_stock_p1 as revo                               # noqa: E402
import update_astock_daily as ua                              # noqa: E402
import t23_random_grammar_census as t23                       # noqa: E402
from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret       # noqa: E402
from composite_ic import stats_block                           # noqa: E402
from parallel_runner import run_cells_parallel, worker_cap     # noqa: E402

# ------------------------------------------------------------ frozen constants
BATCH = "E16_ALPHAGEN_RG_CENSUS_P1"
SEED_KEY_GEN = "e16_alphagen_rg_gen"
SEED_KEY_NULL = "e16_alphagen_rg_null"
K_DEPTH1 = 120
K_DEPTH2 = 80
K_TOTAL = K_DEPTH1 + K_DEPTH2
B_NULLS = 200                 # per-formula permutation draws (roster pin)
N_TRIALS_LEDGER = K_TOTAL      # roster pin: nulls are calibration, not trials
CENSUS_START = "2018-01-01"
WARMUP_ROWS = 130
MIN_CROSS = 100                # t23 law: per-date pairwise names floor
MIN_PERIODS = 30               # stats_block floor per formula
MAX_SKIP_FRAC = 0.10           # t23 law: >10% formulas skipped -> exit 2
N_SHARDS = 12
WINDOWS = (5, 10, 20, 30, 60)
BASE_INPUTS = ("open", "high", "low", "close", "volume", "amount",
               "vwap", "turnover")
GATE_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
OUT_DIR = os.path.join(ROOT, "results", "alphagen_rg")
CKPT_DIR = os.path.join(OUT_DIR, "ckpt")
A158_CMP = os.path.join(ROOT, "scripts", "alpha158_compare.py")
# probe-frozen window facts (prereg sec.2 G-CAL; r878 anchor probe)
CAL_CUTOFF_ROWS = 3490        # 510300 dates <= 2026-10-09
CAL_FIRST_2018_IDX = 1365     # first row with date >= 2018-01-01
CAL_WINDOW_ROWS = 2255        # warmup 130 + census 2125
CENSUS_ROWS_N = 2125
CAL_FIRST_WIN = "2017-06-26"
CAL_LAST = "2026-10-09"
UNIVERSE_N_PROBE = 3514       # sff._universe() r878 probe fact
UNIVERSE_BAND = (3400, 3600)  # gate band, exact count disclosed at burn
ROSTER_SHA16 = "1d06d218b2cbf870"
# op-label alias pairs whose generalized templates coincide (dedup on
# canonical template string collapses them; prereg sec.3 disclosed)
OP_ALIAS = {"VSUMP": "SUMP", "VSUMN": "SUMN", "VSUMD": "SUMD"}


def import_a158_ops():
    """Vendored A158 parse gate verbatim import (roster leg-1 same face)."""
    spec = importlib.util.spec_from_file_location("alpha158_compare",
                                                  A158_CMP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    kbar_names, ops, expr, price_names, gate = mod.build_inventory()
    assert gate["total_is_158"] and gate["rolling_ops"] == 29, gate
    return ops, gate

# ------------------------------------------------------- numeric primitives
# full-window law (n==d) throughout: a window with ANY NaN outputs NaN.


def _clean(x):
    return np.where(np.isfinite(x), x, np.nan)


def _ref(x, d):
    return t23._ref(x, d)


def _roll_mean(x, d):
    return t23._roll_mean(x, d)


def _roll_std(x, d):
    return t23._roll_std(x, d)


def _roll_sum(x, d):
    return t23._roll_sum(x, d)


def _roll_max(x, d):
    return t23._roll_maxmin(x, d, np.max)


def _roll_min(x, d):
    return t23._roll_maxmin(x, d, np.min)


def _roll_corr(x, y, d):
    return t23._roll_corr(x, y, d)


def _chunk_rows(T, d, target_mb=80.0, ncols=None):
    ncols = ncols or 1
    per_row = d * ncols * 8 / 1e6
    r = max(8, int(target_mb / max(per_row, 1e-9)))
    return max(8, min(r, max(T - d + 1, 8)))


def _roll_quantile(x, d, q):
    """Rolling q-quantile, full-window (NaN in window -> NaN naturally)."""
    T, N = x.shape
    out = np.full((T, N), np.nan)
    if T < d:
        return out
    step = _chunk_rows(T, d, ncols=N)
    v = np.lib.stride_tricks.sliding_window_view(
        np.asarray(x, dtype=np.float64), d, axis=0)
    for lo in range(0, v.shape[0], step):
        hi = min(lo + step, v.shape[0])
        with np.errstate(invalid="ignore"):
            out[d - 1 + lo:d - 1 + hi] = np.quantile(
                v[lo:hi], q, axis=-1)
    return out


def _roll_rank_pct(x, d):
    """Percentile rank of current value inside its own window (pandas
    rolling.rank(pct=True) average-tie semantics), full-window rule."""
    T, N = x.shape
    out = np.full((T, N), np.nan)
    if T < d:
        return out
    step = _chunk_rows(T, d, ncols=N)
    v = np.lib.stride_tricks.sliding_window_view(
        np.asarray(x, dtype=np.float64), d, axis=0)
    for lo in range(0, v.shape[0], step):
        hi = min(lo + step, v.shape[0])
        w = v[lo:hi]                          # (R, N, d)
        cur = w[..., d - 1]                    # (R, N)
        fin = np.isfinite(w)
        valid = fin.all(axis=-1) & np.isfinite(cur)
        with np.errstate(invalid="ignore"):
            n_less = (w < cur[..., None]).sum(axis=-1)
            n_eq = (w == cur[..., None]).sum(axis=-1)  # includes self
        pct = (n_less + (n_eq + 1.0) / 2.0) / d
        out[d - 1 + lo:d - 1 + hi] = np.where(valid, pct, np.nan)
    return out


def _roll_argextreme(x, d, is_max):
    """1-based position of window max/min (tsgate IdxMax/IdxMin semantics),
    full-window rule."""
    T, N = x.shape
    out = np.full((T, N), np.nan)
    if T < d:
        return out
    step = _chunk_rows(T, d, ncols=N)
    v = np.lib.stride_tricks.sliding_window_view(
        np.asarray(x, dtype=np.float64), d, axis=0)
    fn = np.argmax if is_max else np.argmin
    for lo in range(0, v.shape[0], step):
        hi = min(lo + step, v.shape[0])
        w = v[lo:hi]
        valid = np.isfinite(w).all(axis=-1)
        pos = fn(w, axis=-1).astype(np.float64) + 1.0
        out[d - 1 + lo:d - 1 + hi] = np.where(valid, pos, np.nan)
    return out


def _ols_cumsums(x):
    """Per-column cumsums for closed-form rolling OLS vs t=1..d."""
    T = x.shape[0]
    fin = np.isfinite(x)
    xf = np.where(fin, x, 0.0).astype(np.float64)
    r = np.arange(T, dtype=np.float64)[:, None]
    return (np.cumsum(xf, axis=0), np.cumsum(xf * xf, axis=0),
            np.cumsum(xf * r, axis=0), np.cumsum(fin.astype(np.float64),
                                                axis=0))


def _roll_ols(x, d):
    """Full-window closed-form rolling OLS vs t=1..d within the window.
    Returns (slope, rsquare, resid_last); constant windows -> NaN guards
    (tsgate rsquare std~0 guard law)."""
    T, N = x.shape
    s1, sxx, srx, cn = _ols_cumsums(x)
    w1, wxx, wrx, wn = (t23._win(s1, d), t23._win(sxx, d),
                        t23._win(srx, d), t23._win(cn, d))
    out_shape = (T, N)
    slope = np.full(out_shape, np.nan)
    rsqr = np.full(out_shape, np.nan)
    resi = np.full(out_shape, np.nan)
    if w1.shape[0] == 0:
        return slope, rsqr, resi
    ok = wn == d
    # within-window time index t'' = row - a (0-based, runs 0..d-1); t-bar
    # and the fitted-at-last-point must use the SAME t'' origin (shift
    # invariance holds only for slope/rsquare, never for mixed origins).
    tbar = (d - 1.0) / 2.0
    stt = d * (d * d - 1.0) / 12.0
    # window start row a = i-d+1 -> within-window t = row - a + 1
    rows = np.arange(d - 1, T, dtype=np.float64)[:, None]
    a = rows - (d - 1.0)
    stx = wrx - a * w1                    # sum of t''*x over the window
    sxy = stx - tbar * w1
    sxx_dev = wxx - w1 * w1 / d
    with np.errstate(invalid="ignore", divide="ignore"):
        b = sxy / stt
        intercept = w1 / d - b * tbar
        resid_last = x[d - 1:] - (intercept + b * (d - 1.0))
        r2 = (sxy * sxy) / (stt * sxx_dev)
    ok_b = ok & (sxx_dev > 0)
    slope[d - 1:] = np.where(ok_b, b, np.nan)
    rsqr[d - 1:] = np.where(ok_b, np.clip(r2, 0.0, 1.0), np.nan)
    resi[d - 1:] = np.where(ok_b, resid_last, np.nan)
    return slope, rsqr, resi

def _roll_pos_sums(x, d):
    """SUMP/SUMN/SUMD family: window sums of positive/negative/abs parts of
    dx = x - Ref(x,1), full-window rule, denominator Sum(Abs(dx),d)+1e-12
    (vendored template verbatim under the X-substitution rule)."""
    T, N = x.shape
    dx = _clean(x - _ref(x, 1))
    fin = np.isfinite(dx)
    dxf = np.where(fin, dx, 0.0)
    pos = np.where(fin & (dx > 0), dxf, 0.0)
    neg = np.where(fin & (dx < 0), -dxf, 0.0)
    ab = np.where(fin, np.abs(dxf), 0.0)
    cs = {k: np.cumsum(v, axis=0) for k, v in
          (("p", pos), ("n", neg), ("a", ab), ("c", fin.astype(np.float64)))}
    w = {k: t23._win(v, d) for k, v in cs.items()}
    sump = np.full((T, N), np.nan)
    sumn = np.full((T, N), np.nan)
    sumd = np.full((T, N), np.nan)
    if w["p"].shape[0] == 0:
        return sump, sumn, sumd
    ok = w["c"] == d
    denom = w["a"] + 1e-12
    sump[d - 1:] = np.where(ok, w["p"] / denom, np.nan)
    sumn[d - 1:] = np.where(ok, w["n"] / denom, np.nan)
    sumd[d - 1:] = np.where(ok, (w["p"] - w["n"]) / denom, np.nan)
    return sump, sumn, sumd


def _cmp(x, ref, strict_gt):
    fin = np.isfinite(x) & np.isfinite(ref)
    val = (x > ref) if strict_gt else (x < ref)
    return np.where(fin, val.astype(np.float64), np.nan)


def _log1p_pos(v):
    with np.errstate(invalid="ignore", divide="ignore"):
        return _clean(np.log(v + 1.0))


# --------------------------------------------------------------- op registry
# Generalization rule (prereg sec.3, frozen): every PRICE-family field slot
# in the vendored qlib template takes the sampled input X; $volume slots
# stay the raw volume series verbatim. Single-field templates with X=close
# reproduce A158-verbatim features (ROC/MA/STD/BETA/RSQR/RESI/QTLU/QTLD/
# RANK/CNTP/CNTN/CNTD/SUMP/SUMN/SUMD); two-field templates (MAX/LOW/RSV/
# IMAX/IMIN/IMXD/CORR/CORD/WVMA) produce generalized forms -- disclosed.

def _mk_op_impl():
    impl = {}

    def roc(X, d, L):
        return _clean(_ref(X, d) / X)

    def ma(X, d, L):
        return _clean(_roll_mean(X, d) / X)

    def std(X, d, L):
        return _clean(_roll_std(X, d) / X)

    def beta(X, d, L):
        s, _, _ = _roll_ols(X, d)
        return _clean(s / X)

    def rsqr(X, d, L):
        _, r, _ = _roll_ols(X, d)
        return r

    def resi(X, d, L):
        _, _, r = _roll_ols(X, d)
        return _clean(r / X)

    def fmax(X, d, L):
        return _clean(_roll_max(X, d) / X)

    def fmin(X, d, L):
        return _clean(_roll_min(X, d) / X)

    def qtlu(X, d, L):
        return _clean(_roll_quantile(X, d, 0.8) / X)

    def qtld(X, d, L):
        return _clean(_roll_quantile(X, d, 0.2) / X)

    def rank(X, d, L):
        return _roll_rank_pct(X, d)

    def rsv(X, d, L):
        lo = _roll_min(X, d)
        hi = _roll_max(X, d)
        with np.errstate(invalid="ignore", divide="ignore"):
            return _clean((X - lo) / (hi - lo + 1e-12))

    def imax(X, d, L):
        return _clean(_roll_argextreme(X, d, True) / d)

    def imin(X, d, L):
        return _clean(_roll_argextreme(X, d, False) / d)

    def imxd(X, d, L):
        return _clean((_roll_argextreme(X, d, True)
                       - _roll_argextreme(X, d, False)) / d)

    def corr(X, d, L):
        return _roll_corr(X, _log1p_pos(L["volume"]), d)

    def cord(X, d, L):
        vol = L["volume"]
        with np.errstate(invalid="ignore", divide="ignore"):
            a = _clean(X / _ref(X, 1))
            b = _log1p_pos(_clean(vol / _ref(vol, 1)))
        return _roll_corr(a, b, d)

    def cntp(X, d, L):
        return _roll_mean(_cmp(X, _ref(X, 1), True), d)

    def cntn(X, d, L):
        return _roll_mean(_cmp(X, _ref(X, 1), False), d)

    def cntd(X, d, L):
        return _clean(cntp(X, d, L) - cntn(X, d, L))

    def sump(X, d, L):
        return _roll_pos_sums(X, d)[0]

    def sumn(X, d, L):
        return _roll_pos_sums(X, d)[1]

    def sumd(X, d, L):
        return _roll_pos_sums(X, d)[2]

    def vma(X, d, L):
        with np.errstate(invalid="ignore", divide="ignore"):
            return _clean(_roll_mean(X, d) / (X + 1e-12))

    def vstd(X, d, L):
        with np.errstate(invalid="ignore", divide="ignore"):
            return _clean(_roll_std(X, d) / (X + 1e-12))

    def wvma(X, d, L):
        vol = L["volume"]
        with np.errstate(invalid="ignore", divide="ignore"):
            w = _clean(np.abs(X / _ref(X, 1) - 1.0)) * vol
        return _clean(_roll_std(w, d) / (_roll_mean(w, d) + 1e-12))

    impl.update({
        "ROC": roc, "MA": ma, "STD": std, "BETA": beta, "RSQR": rsqr,
        "RESI": resi, "MAX": fmax, "LOW": fmin, "QTLU": qtlu,
        "QTLD": qtld, "RANK": rank, "RSV": rsv, "IMAX": imax,
        "IMIN": imin, "IMXD": imxd, "CORR": corr, "CORD": cord,
        "CNTP": cntp, "CNTN": cntn, "CNTD": cntd, "SUMP": sump,
        "SUMN": sumn, "SUMD": sumd, "VMA": vma, "VSTD": vstd,
        "WVMA": wvma, "VSUMP": sump, "VSUMN": sumn, "VSUMD": sumd,
    })
    return impl


OP_IMPL = _mk_op_impl()

# ------------------------------------------------------------------- grammar
# node forms (picklable tuples):
#   depth-1: ("d1", op, inp, w)
#   depth-2: ("d2", op2, w2, sub_node)


def formula_str(node):
    if node[0] == "d1":
        return f"{node[1]}({node[2]},{node[3]})"
    return f"{node[1]}({formula_str(node[3])},{node[2]})"


def canonical_key(node):
    """Dedup key on the generalized template (op-label aliases collapse:
    VSUMP==SUMP family under the X-substitution rule, prereg disclosed)."""
    if node[0] == "d1":
        op = OP_ALIAS.get(node[1], node[1])
        return f"{op}|{node[2]}|{node[3]}"
    op2 = OP_ALIAS.get(node[1], node[1])
    return f"{op2}|{node[2]}|{canonical_key(node[3])}"


def node_depth(node):
    return 1 if node[0] == "d1" else 2


def _draw_node(rng, ops, depth):
    inp = BASE_INPUTS[int(rng.integers(len(BASE_INPUTS)))]
    op = ops[int(rng.integers(len(ops)))]
    w = WINDOWS[int(rng.integers(len(WINDOWS)))]
    if depth == 1:
        return ("d1", op, inp, w)
    op2 = ops[int(rng.integers(len(ops)))]
    w2 = WINDOWS[int(rng.integers(len(WINDOWS)))]
    return ("d2", op2, w2, ("d1", op, inp, w))


def sample_formulas(ops, seed_gen):
    """K=200 deterministic draws, in-stream rejection until the canonical
    key is unique (cap 10k draws per formula, then keep duplicate honestly)."""
    out = []
    seen = set()
    for i in range(K_TOTAL):
        rng = np.random.default_rng([int(seed_gen), int(i)])
        depth = 1 if i < K_DEPTH1 else 2
        node = None
        for _attempt in range(10000):
            cand = _draw_node(rng, ops, depth)
            key = canonical_key(cand)
            if key not in seen:
                seen.add(key)
                node = cand
                break
        if node is None:               # cap hit: keep duplicate, disclose
            node = _draw_node(rng, ops, depth)
            seen.add(canonical_key(node))
        out.append(node)
    return out


def evaluate(node, leaves):
    if node[0] == "d1":
        X = np.asarray(leaves[node[2]], dtype=np.float64)
        return OP_IMPL[node[1]](X, int(node[3]), leaves)
    X = evaluate(node[3], leaves)
    return OP_IMPL[node[1]](X, int(node[2]), leaves)

# ------------------------------------------------------------------ gates
def _roster_sha16():
    import hashlib
    p = os.path.join(OUT_DIR, "e16_roster.json")
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def gate_face():
    """t23 disk-truth panel gate verbatim import + E16 window anchors."""
    face = t23.gate_face()
    face["roster_sha16"] = _roster_sha16()
    face["roster_sha_ok"] = face["roster_sha16"] == ROSTER_SHA16
    face["seeds_ok"] = (sg.SEED_REGISTRY[SEED_KEY_GEN] == 20_620_000
                        and sg.SEED_REGISTRY[SEED_KEY_NULL] == 20_620_100)
    cal_ok = False
    try:
        cal_all = pd.read_csv(GATE_CSV, usecols=["date"])["date"].astype(
            str).tolist()
        cal_c = [d for d in cal_all if d <= CAL_LAST]
        idx = next(i for i, d in enumerate(cal_c) if d >= CENSUS_START)
        lo = max(0, idx - WARMUP_ROWS)
        cal_ok = (len(cal_c) == CAL_CUTOFF_ROWS
                  and idx == CAL_FIRST_2018_IDX
                  and len(cal_c) - lo == CAL_WINDOW_ROWS
                  and cal_c[lo] == CAL_FIRST_WIN
                  and cal_c[-1] == CAL_LAST)
        face["cal_window_ok"] = cal_ok
    except Exception as exc:                       # noqa: BLE001
        face["cal_window_ok"] = False
        face["cal_error"] = str(exc)
    face["panel_cutoff_ok"] = bool(
        (face.get("cutoff") or "") >= CAL_LAST)
    face["ready"] = bool(face["ready"] and face["roster_sha_ok"]
                         and face["seeds_ok"] and cal_ok
                         and face["panel_cutoff_ok"])
    return face


# ------------------------------------------------------------- panel + cache
PANEL_COLS = ("open", "high", "low", "close", "volume", "amount", "turnover")


def _cal_slice():
    cal_all = pd.read_csv(GATE_CSV, usecols=["date"])["date"].astype(
        str).tolist()
    cal_c = [d for d in cal_all if d <= CAL_LAST]
    idx = next(i for i, d in enumerate(cal_c) if d >= CENSUS_START)
    lo = max(0, idx - WARMUP_ROWS)
    cal = cal_c[lo:]
    census_rows = np.arange(idx - lo, len(cal))
    assert len(cal) == CAL_WINDOW_ROWS and len(census_rows) == CENSUS_ROWS_N
    return cal, census_rows


def _prefix_fingerprint(path, cutoff):
    """(bytes, sha256) of the file prefix the census is a function of.

    Rows dated after the frozen cutoff are dropped at load, so an appended bar
    must NOT invalidate the cache; a repaired bar INSIDE the window must, and
    no stamp, date count or file name moves when one is repaired (E289 class).
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    keep = []
    for line in raw.split(b"\n"):
        head = line.split(b",", 1)[0].strip().strip(b'"')
        if len(head) == 10 and head[:1].isdigit() and head.decode() > cutoff:
            break
        keep.append(line)
    blob = b"\n".join(keep)
    return len(blob), hashlib.sha256(blob).hexdigest()


def member_fingerprints(uni):
    """code -> (consumed bytes, sha256) for every member file present on disk."""
    out = {}
    for code in uni:
        path = os.path.join(ua.PER_DIR, code + ".csv")
        if os.path.exists(path):
            out[code] = _prefix_fingerprint(path, CAL_LAST)
    return out


def _rule_fingerprint():
    """The frozen constants build_cache reads: a moved gate must rebuild too."""
    return {"cutoff": CAL_LAST, "census_start": CENSUS_START,
            "warmup_rows": WARMUP_ROWS, "cal_window_rows": CAL_WINDOW_ROWS,
            "census_rows_n": CENSUS_ROWS_N, "panel_cols": list(PANEL_COLS),
            "base_inputs": list(BASE_INPUTS), "universe_band": list(UNIVERSE_BAND),
            "price_min": revo.PRICE_MIN, "amt20_min": revo.AMT20_MIN,
            "listed_min": revo.LISTED_MIN, "fresh_max": revo.FRESH_MAX}


def panel_inputs_sha256(members):
    """Digest of the rule block plus every member's consumed bytes."""
    h = hashlib.sha256()
    h.update(json.dumps(_rule_fingerprint(), sort_keys=True).encode())
    for code in sorted(members):
        size, sha = members[code]
        h.update(b"\0" + code.encode() + b"|" + str(size).encode()
                 + b"|" + sha.encode())
    return h.hexdigest()


def cache_meta_valid(meta, members):
    """Is this stored cache a cache of the SAME world it is about to answer for?

    A cutoff stamp, a row count and the cache file's own name all stay green
    while a bar inside the frozen window is repaired, so the identity is the
    member bytes themselves. A cache written before the digest existed is a
    MISS, never a hit: unreadable is not clean.
    """
    if not meta:
        return False, "no meta"
    if meta.get("cutoff") != CAL_LAST:
        return False, "cutoff moved"
    want = meta.get("inputs_sha256")
    if not want:
        return False, "written before the inputs digest existed"
    have = panel_inputs_sha256(members)
    if want != have:
        return False, f"inputs digest moved {want[:12]} -> {have[:12]}"
    return True, "inputs digest matches"


def build_cache(cutoff):
    """Deterministic panel cache (first shard builds; later shards reuse).
    Universe = sff._universe() single source; eligibility = P4_BATCH2
    dynamic per-date clauses verbatim (t23 load_panel law)."""
    cal, census_rows = _cal_slice()
    uni = sff._universe()
    assert UNIVERSE_BAND[0] <= len(uni) <= UNIVERSE_BAND[1], len(uni)
    T, N = len(cal), len(uni)
    F = {k: np.full((T, N), np.nan, dtype=np.float64) for k in PANEL_COLS}
    dpos = {d: i for i, d in enumerate(cal)}
    mfp = {}
    for j, code in enumerate(uni):
        path = os.path.join(ua.PER_DIR, code + ".csv")
        if not os.path.exists(path):
            continue
        mfp[code] = _prefix_fingerprint(path, CAL_LAST)
        df = pd.read_csv(path)
        df = df[df["date"].astype(str) <= CAL_LAST]
        pos = df["date"].astype(str).map(dpos)
        m = pos.notna().to_numpy()
        if not m.any():
            continue
        r = pos[m].to_numpy(dtype=np.int64)
        for col in PANEL_COLS:
            F[col][r, j] = df[col].to_numpy(dtype=np.float64)[m]
    with np.errstate(invalid="ignore", divide="ignore"):
        vwap = F["amount"] / F["volume"]
    leaves = dict(F)
    leaves["vwap"] = vwap
    # P4_BATCH2 dynamic eligibility (t23 load_panel verbatim face)
    mask = pd.read_csv(MASK_CSV, dtype={"code": str}).set_index("code")
    board = {s: (mask.loc[s, "board"] if s in mask.index else "main")
             for s in uni}
    close = F["close"]
    fin = np.isfinite(close)
    amt20 = revo._roll_mean20(F["amount"])
    listed = fin.cumsum(axis=0)
    lvidx = np.where(fin, np.arange(T)[:, None], -1)
    lastvalid = np.maximum.accumulate(lvidx, axis=0)
    fresh = (np.arange(T)[:, None] - lastvalid) <= revo.FRESH_MAX
    ok_row = np.array([board.get(s) not in ("other", None) for s in uni])
    elig = (ok_row[None, :] & fin & (close >= revo.PRICE_MIN)
            & np.isfinite(amt20) & (amt20 >= revo.AMT20_MIN)
            & (listed >= revo.LISTED_MIN) & fresh)
    fwd1 = fwd_ret(close, 1)
    os.makedirs(CKPT_DIR, exist_ok=True)
    path = cache_path(cutoff)
    tmp = path + ".tmp.npz"
    meta = {"cutoff": CAL_LAST, "cal_first": cal[0], "cal_last": cal[-1],
            "window_rows": int(T), "census_rows": int(len(census_rows)),
            "universe_n": int(N), "roster_sha16": _roster_sha16(),
            "inputs_sha256": panel_inputs_sha256(mfp),
            "inputs_members": int(len(mfp))}
    np.savez(tmp, meta=json.dumps(meta), cal=np.array(cal),
             universe=np.array(uni), elig=elig, fwd1=fwd1,
             census_rows=census_rows.astype(np.int64),
             **{f"leaf_{k}": leaves[k] for k in BASE_INPUTS})
    os.replace(tmp, path)
    return path, meta


def cache_path(cutoff):
    return os.path.join(OUT_DIR, f"panel_cache_{cutoff}.npz")


def ensure_cache(cutoff):
    path = cache_path(cutoff)
    if os.path.exists(path):
        try:
            with np.load(path, allow_pickle=False) as z:
                meta = json.loads(str(z["meta"]))
            reusable, why = cache_meta_valid(meta, member_fingerprints(
                sff._universe()))
            if reusable:
                return path, meta
            print(f"[e16] panel cache MISS: {why}")
        except Exception as exc:                    # noqa: BLE001
            print(f"[e16] panel cache MISS: unreadable cache ({exc!r})")
    print("[e16] building panel cache (deterministic, one-time) ...")
    t0 = time.time()
    path, meta = build_cache(cutoff)
    print(f"[e16] cache built {path} ({time.time() - t0:.0f}s)")
    return path, meta

# ------------------------------------------------------------- census core
_W = {}          # worker globals (mmap-free npz member cache, per process)


def _worker_init(npz_path):
    _W["npz_path"] = npz_path


def _load_member(name):
    if name not in _W:
        with np.load(_W["npz_path"], allow_pickle=False) as z:
            _W[name] = z[name]
    return _W[name]


def _leaves_for(inp):
    """Load only the members a formula needs (sampled input + close/volume
    auxiliaries); per-process member cache keeps re-reads zero-cost."""
    need = {inp, "close", "volume"}
    for k in need:
        _load_member(f"leaf_{k}")
    return {k: _W[f"leaf_{k}"] for k in need}


def task_formula(idx, node, seed_null):
    """One formula: eval + real IC face + B=200 same-mask permutation nulls.
    Pure function of (frozen cache, node, seeds) -- deterministic."""
    node = tuple(node[:3]) + (tuple(node[3]),) if node[0] == "d2" else node
    inp = node[2] if node[0] == "d1" else None
    if inp is None:
        inp = node[3][2]
    leaves = _leaves_for(inp)
    elig_c = _load_member("elig")
    fwd_c = _load_member("fwd1")
    rows = _load_member("census_rows")
    cal = _load_member("cal")
    F = evaluate(node, leaves)
    rec = {"idx": int(idx), "formula": formula_str(node),
           "depth": node_depth(node), "skip": None,
           "nulls_abs_ir": [None] * B_NULLS}
    try:
        eff = (elig_c[rows, :] & np.isfinite(F[rows, :])
               & np.isfinite(fwd_c[rows, :]))
        cal_us = np.asarray(pd.to_datetime(
            np.asarray(list(cal), dtype="datetime64[us]")))[rows]
        nser = pd.Series(eff.sum(axis=1),
                         index=pd.DatetimeIndex(cal_us))
        keep = nser >= MIN_CROSS
        Fr = rank_rows(eff, F[rows, :])
        Rr = rank_rows(eff, fwd_c[rows, :])
        s = ic_from_ranks(Fr, Rr, cal_us)
        s = s[s.index.isin(nser.index[keep])]
        blk = stats_block(s)
        rec["n_dates"] = int(keep.sum())
        rec["eligible_median"] = int(float(np.median(
            nser[keep]))) if keep.any() else 0
        if "ic_mean" not in blk or blk.get("n_periods", 0) < MIN_PERIODS:
            rec["skip"] = "insufficient census periods (h1)"
            rec.update({"n_dates": int(keep.sum())})
            return rec
        rec["h1"] = blk
        nulls = np.full(B_NULLS, np.nan)
        for bj in range(B_NULLS):
            rng = np.random.default_rng([int(seed_null), int(idx), int(bj)])
            Fp = t23._permute_ranks_within_mask(Fr, eff, rng)
            s_b = ic_from_ranks(Fp, Rr, cal_us)
            s_b = s_b[s_b.index.isin(s.index)]
            blk_b = stats_block(s_b)
            if "ic_ir" in blk_b:
                nulls[bj] = abs(blk_b["ic_ir"])
        fin = np.isfinite(nulls)
        rec["nulls_abs_ir"] = [round(float(v), 4) if np.isfinite(v)
                               else None for v in nulls]
        rec["null_abs_ir_p50"] = (round(float(np.nanquantile(
            nulls, 0.50)), 3) if fin.any() else None)
        rec["null_abs_ir_p95"] = (round(float(np.nanquantile(
            nulls, 0.95)), 3) if fin.any() else None)
        rec["null_draws_ok"] = int(fin.sum())
    finally:
        for k in list(_W.keys()):
            if k.startswith("leaf_"):
                del _W[k]
    return rec

# ------------------------------------------------------------ run / finalize
def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _ckpt_path(shard):
    return os.path.join(CKPT_DIR, f"shard_{shard}of{N_SHARDS}.jsonl")


def _ckpt_done(shard):
    p = _ckpt_path(shard)
    done = {}
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[int(rec["idx"])] = rec
                except Exception:                   # noqa: BLE001
                    continue        # truncated tail tolerated (t22 law)
    return done


def _ckpt_flush(fp, rec):
    fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
    fp.flush()


# pool harvest handshake (O-20260930-2355 window; r942 gap fix -- third
# live instance = E16 shards 0/1 completed 2026-10-11 ~13:0x then falsely
# fed the crash fuse because this runner lacked the worker-side half;
# claims for 0/1 backfilled r881 per r497/r860 canonical remedy): the
# worker-side half mirrors lowamp_p1._pool_claim /
# thermo_overlay_p1._pool_claim verbatim (per-shard parameterized) -- on
# a successful burn (incl. the idempotent ckpt-skip fast path) write the
# closed+ok claim so the autofill harvest flip lands the shard done;
# without it a completed burn reads as a crash to the fuse (r496 family).
def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _pool_claim(shard, shards, started, detail):
    entry = f"E16-ALPHAGEN-RG-SHARD-{shard}OF{shards}"
    shard_key = f"e16-rg-{shard}of{shards}"
    d = os.path.join(ROOT, "results", "pool_claims", entry)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(fp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"machine_id": _machine_id(), "state": "closed",
                   "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
                   "exit_code": 0, "started": started, "closed_at": now,
                   "result_ref": detail}, fh,
                  ensure_ascii=False, indent=2, sort_keys=True)
    print("pool claim closed:", os.path.basename(fp))


def cmd_run(shard, shards, workers):
    t0 = time.time()
    started_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    face = gate_face()
    if not face["ready"]:
        print(json.dumps({"awaiting_panel": True, "gate": face},
                         ensure_ascii=False, default=str), flush=True)
        # r491 data-wait park marker (r797 landing law: every runner's
        # data-gate refusal path carries it): honest zero-burn rc2 parks
        # the entry instead of feeding the crash fuse a false crash.
        print(f"AUTOFILL-PARK: {time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"panel gate not ready -- honest zero-burn, NOT a crash "
              f"(r491 law)", flush=True)
        return 2
    # batch cutoff is FROZEN (D2 lockbox): the live panel cutoff is only a
    # readiness signal; later bars are truncated at load either way.
    cutoff = CAL_LAST
    ops, gate158 = import_a158_ops()
    npz_path, meta = ensure_cache(cutoff)
    formulas = sample_formulas(ops, sg.SEED_REGISTRY[SEED_KEY_GEN])
    idxs = [i for i in range(K_TOTAL) if i % shards == shard]
    done = _ckpt_done(shard)
    jobs = [(i, task_formula,
             (i, list(formulas[i]) if isinstance(
                 formulas[i], tuple) else formulas[i],
              int(sg.SEED_REGISTRY[SEED_KEY_NULL])))
            for i in idxs if i not in done]
    print(f"[e16] shard {shard}of{shards}: {len(idxs)} formulas, "
          f"{len(jobs)} pending, cache={os.path.basename(npz_path)}")
    if jobs:
        with open(_ckpt_path(shard), "a", encoding="utf-8") as fp:

            def on_result(key, payload):
                _ckpt_flush(fp, payload)

            # inside the with: fp must stay open for every on_result flush
            # (r878 indent bug: call sat at with-header level = block exited
            # before first flush -> ValueError I/O on closed file, 19min burn
            # zero-checkpoint loss)
            run_cells_parallel(
                jobs, workers=workers or min(worker_cap(), 8),
                desc=f"e16-shard{shard}",
                initializer=_worker_init, initargs=(npz_path,),
                on_result=on_result)
    merged = dict(done)
    merged.update({i: r for i, r in _ckpt_done(shard).items()})
    recs = [merged[i] for i in idxs if i in merged]
    n_ok = sum(1 for r in recs if r.get("skip") is None)
    product = {
        "batch": BATCH, "shard": f"{shard}of{shards}",
        "cutoff": str(cutoff), "cache_meta": meta,
        "gate_158": gate158, "gate_face": {k: v for k, v in face.items()
                                           if k != "cal_error"},
        "n_formulas": len(idxs), "n_ok": n_ok,
        "n_skip": len(idxs) - n_ok,
        "workers": (workers or min(worker_cap(), 8)),
        "formulas": recs,
        "audit": {"engine_runs": 0, "elapsed_sec": round(time.time() - t0, 1),
                  "generated_at": dt.datetime.now().astimezone().isoformat(
                      timespec="seconds")},
    }
    out = os.path.join(OUT_DIR, f"shard_{shard}of{shards}.json")
    _dump(product, out)
    print(json.dumps({"shard": product["shard"], "out": out,
                      "n_ok": n_ok, "n_skip": product["n_skip"],
                      "elapsed_sec": product["audit"]["elapsed_sec"]},
                     ensure_ascii=False))
    _pool_claim(shard, shards, started_iso,
                out + f" (n_ok={n_ok}, n_skip={product['n_skip']})")
    return 0


def cmd_finalize():
    t0 = time.time()
    face = gate_face()
    if not face["ready"]:
        print(json.dumps({"awaiting_panel": True, "gate": face},
                         ensure_ascii=False, default=str))
        return 2
    # batch cutoff FROZEN (D2 lockbox) -- see cmd_run note
    cutoff = CAL_LAST
    out = os.path.join(OUT_DIR, f"CENSUS-{cutoff}.json")
    landed = sg.finalize_already_landed(BATCH, file_name=out)
    if landed is not None:
        print(json.dumps({"already_landed": True, "cutoff": cutoff,
                          "landed_block": landed,
                          "action": "no-op (idempotent refuse)"},
                         ensure_ascii=False, default=str))
        return 0
    recs = []
    shard_files = []
    for k in range(N_SHARDS):
        p = os.path.join(OUT_DIR, f"shard_{k}of{N_SHARDS}.json")
        if not os.path.exists(p):
            print(json.dumps({"incomplete": True, "missing_shard": p},
                             ensure_ascii=False))
            return 2
        with open(p, "r", encoding="utf-8") as f:
            prod = json.load(f)
        shard_files.append(os.path.basename(p))
        recs.extend(prod["formulas"])
    recs.sort(key=lambda r: r["idx"])
    assert len(recs) == K_TOTAL, len(recs)
    ok_idx = [i for i, r in enumerate(recs) if r.get("skip") is None]
    if len(recs) - len(ok_idx) > K_TOTAL * MAX_SKIP_FRAC:
        print(json.dumps({"mechanism_suspect": True,
                         "n_skip": len(recs) - len(ok_idx),
                         "law": f"> {MAX_SKIP_FRAC:.0%} formulas skipped"},
                         ensure_ascii=False))
        return 2
    obs_max = max((abs(recs[i]["h1"]["ic_ir"]) for i in ok_idx),
                  default=None)
    nulls = np.full((K_TOTAL, B_NULLS), np.nan)
    for r in recs:
        if r.get("skip") is None:
            nulls[r["idx"]] = [np.nan if v is None else float(v)
                               for v in r["nulls_abs_ir"]]
    fam_null_max = []
    for bj in range(B_NULLS):
        col = nulls[ok_idx, bj]
        if np.isfinite(col).any():
            fam_null_max.append(round(float(np.nanmax(col)), 3))
    null_p95 = (round(float(np.quantile(fam_null_max, 0.95)), 3)
                if len(fam_null_max) >= 10 else None)
    holds = bool(obs_max is not None and null_p95 is not None
                 and obs_max > null_p95)
    ledger = sg.append_ledger(BATCH, N_TRIALS_LEDGER, file_name=out,
                              evidence_cutoff=cutoff,
                              note="E16 alphagen slice-2 random-grammar "
                                   f"census: K={K_TOTAL} formula draws on "
                                   "the batch ledger face (roster pin: "
                                   f"nulls are calibration, not trials); "
                                   f"B={B_NULLS} same-mask permutation "
                                   "nulls per formula; zero engine runs")
    d1 = [abs(r["h1"]["ic_ir"]) for r in recs
          if r.get("skip") is None and r["depth"] == 1]
    d2 = [abs(r["h1"]["ic_ir"]) for r in recs
          if r.get("skip") is None and r["depth"] == 2]
    payload = {
        **sg.cutoff_meta(cutoff),
        "batch": BATCH,
        "probe": "E16 alphagen slice-2 random-grammar stock census",
        "queue_row": "state/queue/explore.md E16",
        "prereg_ref": "research/E16_ALPHAGEN_RG_CENSUS_P1.md FROZEN "
                      "(bm-b r878, precedes runner build precedes ANY run)",
        "roster_ref": "results/alphagen_rg/e16_roster.json "
                      f"sha16={ROSTER_SHA16}",
        "verdict": {"census_holds": holds,
                    "line": "observed_family_max_abs_icir > "
                            "null_family_p95",
                    "observed_family_max_abs_icir": obs_max,
                    "null_family_p95": null_p95,
                    "null_p95_min_draws": 10,
                    "n_ok": len(ok_idx),
                    "n_skip": K_TOTAL - len(ok_idx)},
        "descriptive": {
            "n_unique_formulas": len({r["formula"] for r in recs}),
            "abs_icir_lt_005_frac": (round(float(np.mean(
                [abs(r["h1"]["ic_ir"]) < 0.05 for i, r in enumerate(recs)
                 if i in ok_idx])), 4) if ok_idx else None),
            "depth1_mean_abs_icir": (round(float(np.mean(d1)), 4)
                                     if d1 else None),
            "depth2_mean_abs_icir": (round(float(np.mean(d2)), 4)
                                     if d2 else None),
        },
        "seeds": {"gen": [int(sg.SEED_REGISTRY[SEED_KEY_GEN]), "i<K",
                          SEED_KEY_GEN],
                  "null": [int(sg.SEED_REGISTRY[SEED_KEY_NULL]),
                           "i<K,b<B", SEED_KEY_NULL]},
        "grammar": {"ops": 29, "base_inputs": list(BASE_INPUTS),
                    "windows": list(WINDOWS), "k_depth1": K_DEPTH1,
                    "k_depth2": K_DEPTH2, "k_total": K_TOTAL,
                    "b_nulls": B_NULLS,
                    "generalization_rule": "all price-field slots -> X; "
                    "$volume slots stay raw volume (prereg sec.3)",
                    "dedup": "canonical generalized template string; "
                    "op-label aliases SUMP/VSUMP, SUMN/VSUMN, SUMD/VSUMD "
                    "collapse"},
        "census": {"formulas": [{k: v for k, v in r.items()
                                 if k != "nulls_abs_ir"} for r in recs],
                   "nulls_abs_ir_matrix_shape": [K_TOTAL, B_NULLS]},
        "riders": t23.A158_LINEAGE_PRIOR,
        "shard_files": shard_files,
        "trials_ledger": ledger,
        "audit": {"engine_runs": 0, "n_draws": N_TRIALS_LEDGER,
                  "elapsed_sec": round(time.time() - t0, 1),
                  "generated_at": dt.datetime.now().astimezone().isoformat(
                      timespec="seconds")},
    }
    _dump(payload, out)
    _dump(payload, os.path.join(OUT_DIR, "latest.json"))
    print(json.dumps({"census_holds": holds,
                      "observed_family_max_abs_icir": obs_max,
                      "null_family_p95": null_p95,
                      "n_ok": len(ok_idx),
                      "n_skip": K_TOTAL - len(ok_idx),
                      "out": out, "elapsed_sec":
                          payload["audit"]["elapsed_sec"]},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_status():
    face = gate_face()
    shards_done = sum(
        1 for k in range(N_SHARDS)
        if os.path.exists(os.path.join(OUT_DIR, f"shard_{k}of{N_SHARDS}.json")))
    caches = sorted(os.path.basename(p) for p in
                    [os.path.join(OUT_DIR, f"panel_cache_{d}.npz")
                     for d in [CAL_LAST]] if os.path.exists(p))
    print(json.dumps({"gate": {k: v for k, v in face.items()
                               if k != "cal_error"},
                      "shards_done": shards_done, "of": N_SHARDS,
                      "caches": caches,
                      "finalize_product": os.path.exists(
                          os.path.join(OUT_DIR, f"CENSUS-{CAL_LAST}.json"))},
                     ensure_ascii=False, default=str, indent=1))
    return 0

# ------------------------------------------------------------------ selftest
def _synth_cache(path, seed=777, T=140, N=120, signal=0.0, warmup=30):
    """Hermetic synthetic panel cache (same member schema as build_cache)."""
    rng = np.random.default_rng(seed)
    eps = rng.standard_normal((T, N)) * 0.02
    if signal:
        r = np.zeros((T, N))
        r[0] = eps[0]
        for t in range(1, T):
            r[t] = -signal * r[t - 1] + eps[t]
    else:
        r = eps
    close = 10.0 * np.exp(np.cumsum(r, axis=0))
    leaves = {}
    leaves["close"] = close
    leaves["open"] = close * (1.0 + 0.01 * rng.standard_normal((T, N)))
    leaves["high"] = leaves["open"] * (1.0 + 0.01 * np.abs(
        rng.standard_normal((T, N))))
    leaves["low"] = leaves["open"] * (1.0 - 0.01 * np.abs(
        rng.standard_normal((T, N))))
    vol = np.abs(rng.standard_normal((T, N))) * 1e6 + 1e6
    leaves["volume"] = vol
    leaves["amount"] = vol * close
    leaves["vwap"] = leaves["amount"] / leaves["volume"]
    leaves["turnover"] = np.abs(rng.standard_normal((T, N))) * 1e-3
    elig = np.ones((T, N), dtype=bool)
    cal = [d.strftime("%Y-%m-%d") for d in
           pd.bdate_range("2025-01-01", periods=T)]
    rows = np.arange(warmup, T)
    meta = {"cutoff": cal[-1], "window_rows": T,
            "census_rows": int(len(rows)), "universe_n": N,
            "roster_sha16": ROSTER_SHA16}
    np.savez(path, meta=json.dumps(meta), cal=np.array(cal),
             universe=np.array([f"S{i:03d}" for i in range(N)]),
             elig=elig, fwd1=fwd_ret(close, 1),
             census_rows=rows.astype(np.int64),
             **{f"leaf_{k}": leaves[k] for k in BASE_INPUTS})


def selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # s1 seeds + parse gate + sampling determinism/invariants
    check("s1a seeds registered",
          sg.SEED_REGISTRY[SEED_KEY_GEN] == 20_620_000
          and sg.SEED_REGISTRY[SEED_KEY_NULL] == 20_620_100)
    ops, gate = import_a158_ops()
    check("s1b parse gate 29 ops / 158 total",
          gate["rolling_ops"] == 29 and gate["total_is_158"])
    f1 = sample_formulas(ops, 20_620_000)
    f2 = sample_formulas(ops, 20_620_000)
    s1 = [formula_str(x) for x in f1]
    check("s1c K==200, deterministic list", len(f1) == 200 and
          s1 == [formula_str(x) for x in f2])
    check("s1d depth split 120/80",
          sum(1 for x in f1 if x[0] == "d1") == 120)
    check("s1e canonical unique count",
          len({canonical_key(x) for x in f1}) == 200)
    check("s1f alias canonical collapse",
          canonical_key(("d1", "SUMP", "close", 5))
          == canonical_key(("d1", "VSUMP", "close", 5)))

    def _legal(node):
        if node[0] == "d1":
            return (node[1] in OP_IMPL and node[2] in BASE_INPUTS
                    and node[3] in WINDOWS)
        return (node[1] in OP_IMPL and node[2] in WINDOWS
                and _legal(node[3]))
    check("s1g all sampled nodes legal", all(_legal(x) for x in f1))

    # s2 op hand-values (T rows, N=1)
    x = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
    L = {"close": x, "volume": x * 100.0}
    check("s2a MA hand value", abs(OP_IMPL["MA"](x, 3, L)[2, 0]
                                   - (2.0 / 3.0)) < 1e-12)
    check("s2b ROC = Ref/X verbatim", abs(
        OP_IMPL["ROC"](x, 2, L)[2, 0] - (1.0 / 3.0)) < 1e-12)
    b, r2, res = _roll_ols(x, 4)
    check("s2c OLS slope/rsquare/resid on linear ramp",
          abs(b[3, 0] - 1.0) < 1e-9 and abs(r2[3, 0] - 1.0) < 1e-9
          and abs(res[3, 0]) < 1e-9)
    check("s2d BETA = slope/X", abs(OP_IMPL["BETA"](x, 4, L)[3, 0]
                                    - 0.25) < 1e-9)
    check("s2e IMAX 1-based/d", abs(
        OP_IMPL["IMAX"](np.array([[3.0], [1.0], [2.0]]), 3, L)[2, 0]
        - (1.0 / 3.0)) < 1e-12)
    check("s2f RANK pct average ties", abs(
        OP_IMPL["RANK"](np.array([[1.0], [3.0], [2.0], [2.0]]), 4,
                        L)[3, 0] - 0.625) < 1e-12)
    check("s2g QTLU 0.8 quantile / X", abs(
        OP_IMPL["QTLU"](np.array([[1.0], [2.0], [3.0], [4.0]]), 4,
                        L)[3, 0] - (3.4 / 4.0)) < 1e-12)
    xs = np.array([[10.0], [11.0], [10.0], [12.0], [12.0]])
    check("s2h SUMP window ratio", abs(
        OP_IMPL["SUMP"](xs, 3, L)[3, 0] - 0.75) < 1e-9)
    check("s2i CNTP up-day fraction", abs(
        OP_IMPL["CNTP"](xs, 3, L)[3, 0] - (2.0 / 3.0)) < 1e-12)
    check("s2j VMA mean/X", abs(
        OP_IMPL["VMA"](x, 2, L)[1, 0] - (1.5 / 2.0)) < 1e-12)
    yl = {"close": np.array([[1.0], [2.0], [3.0], [4.0]]),
          "volume": np.exp(np.array([[1.0], [2.0], [3.0], [4.0]])) - 1.0}
    check("s2k CORR perfect vs log-vol", abs(
        OP_IMPL["CORR"](yl["close"], 4, yl)[3, 0] - 1.0) < 1e-9)

    # s3 NaN policy: full-window (hole kills its windows)
    xh = np.array([[1.0], [2.0], [np.nan], [4.0], [5.0], [6.0]])
    mh = OP_IMPL["MA"](xh, 3, {"close": xh, "volume": xh})
    check("s3a hole kills overlapping windows, recovers at +3",
          np.isnan(mh[2, 0]) and np.isnan(mh[3, 0])
          and np.isnan(mh[4, 0]) and abs(mh[5, 0] - (5.0 / 6.0)) < 1e-12)
    qh = OP_IMPL["QTLD"](xh, 3, {"close": xh, "volume": xh})
    check("s3b quantile hole -> NaN windows, row5 finite",
          np.isnan(qh[2, 0]) and np.isnan(qh[3, 0])
          and np.isnan(qh[4, 0]) and np.isfinite(qh[5, 0]))

    # s4 permutation determinism + same-mask invariance (t23 s5 law)
    Fr = np.arange(40, dtype=np.float64).reshape(4, 10) % 7
    eff = np.ones((4, 10), dtype=bool)
    eff[:, 0] = False
    p1 = t23._permute_ranks_within_mask(
        Fr, eff, np.random.default_rng(42))
    p2 = t23._permute_ranks_within_mask(
        Fr, eff, np.random.default_rng(42))
    check("s4a permutation deterministic", np.array_equal(p1, p2))
    check("s4b per-row multiset invariant",
          np.array_equal(np.sort(Fr[eff].reshape(4, 9), axis=1),
                         np.sort(p1[eff].reshape(4, 9), axis=1)))

    # s5 end-to-end task on synthetic cache (worker glue, signal + noise)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "panel_cache_syn.npz")
        _synth_cache(cp, seed=777, signal=0.9)
        _worker_init(cp)
        rec_sig = task_formula(
            0, ("d1", "ROC", "close", 5), 20_620_100)
        check("s5a injected reversal signal -> strong ICIR",
              rec_sig.get("skip") is None
              and abs(rec_sig["h1"]["ic_ir"]) > 0.25)
        check("s5b nulls full B=200 draws",
              rec_sig.get("null_draws_ok") == B_NULLS)
        cp2 = os.path.join(td, "panel_cache_noise.npz")
        _synth_cache(cp2, seed=778, signal=0.0)
        _worker_init(cp2)
        rec_noise = task_formula(
            1, ("d1", "MA", "close", 10), 20_620_100)
        check("s5c noise face machinery well-formed",
              rec_noise.get("skip") is None
              and "h1" in rec_noise
              and len(rec_noise["nulls_abs_ir"]) == B_NULLS)
        check("s5d signal beats its own null p95",
              abs(rec_sig["h1"]["ic_ir"])
              > (rec_sig.get("null_abs_ir_p95") or 1.0))
        d2node = ("d2", "STD", 5, ("d1", "MA", "volume", 10))
        rec_d2 = task_formula(120, d2node, 20_620_100)
        check("s5e depth-2 node evaluates through worker",
              rec_d2.get("skip") is None or
              rec_d2.get("skip") == "insufficient census periods (h1)")
        _W.clear()

    # s6 shard split math
    sizes = [sum(1 for i in range(K_TOTAL) if i % N_SHARDS == k)
             for k in range(N_SHARDS)]
    check("s6a 12 shards partition K=200",
          sum(sizes) == K_TOTAL and set(sizes) == {16, 17})

    # s7 payload law
    check("s7a cutoff_meta top-level evidence_cutoff",
          sg.cutoff_meta("2026-10-09") == {"evidence_cutoff": "2026-10-09"})
    led = sg.append_ledger("E16_SELFTEST_DUMMY", 4, file_name=None,
                           prev_total=100)
    check("s7b ledger block shape (prev override)",
          led["batch_trials"] == 4 and led["total"] == 104)
    check("s7c finalize_already_landed guard available",
          callable(sg.finalize_already_landed))

    # s8 wiring guards (r878 closed-selftest law + r797 landing grep law
    # + r942 landing requirement): the claim-close leg must sit inside
    # cmd_run on the success path and the r491 park marker on its
    # data-gate refusal path -- a closed selftest without wiring legs
    # reads green while the real run silently drops the handshake
    # (r496 family, third live instance on this runner 2026-10-11).
    import ast as _ast
    _self_src = open(os.path.abspath(__file__), encoding="utf-8").read()
    _tree = _ast.parse(_self_src)
    _run_fn = None
    for _n in _ast.walk(_tree):
        if isinstance(_n, _ast.FunctionDef) and _n.name == "cmd_run":
            _run_fn = _n
            break
    _ok_claim = False
    if _run_fn is not None:
        for _n in _ast.walk(_run_fn):
            if (isinstance(_n, _ast.Call)
                    and isinstance(_n.func, _ast.Name)
                    and _n.func.id == "_pool_claim"):
                _ok_claim = True
                break
    check("s8a pool claim-close call wired inside cmd_run", _ok_claim)
    check("s8b r491 park marker on cmd_run gate-refusal path",
          _run_fn is not None
          and "AUTOFILL-PARK" in _ast.get_source_segment(_self_src, _run_fn))

    # s9 cache identity (r1380): the panel cache used to be validated by its
    # own name and its own cutoff literal -- both sides the same constant -- so
    # a repaired bar inside the frozen window left every shard resuming on a
    # world that no longer existed. The identity is now the consumed bytes.
    import tempfile
    _tmp = tempfile.mkdtemp(prefix="e16s9_")
    _fx = os.path.join(_tmp, "AAA.csv")
    _lines = ["date,open", "2026-01-02,1.0", "2026-01-03,2.0"]
    with open(_fx, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(_lines + ["2026-10-10,3.0"]) + "\n")
    _a = _prefix_fingerprint(_fx, CAL_LAST)
    with open(_fx, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("2026-10-12,4.0\n")
    _b = _prefix_fingerprint(_fx, CAL_LAST)
    check("s9a an appended bar does not move the cache identity", _a == _b)
    with open(_fx, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(["date,open", "2026-01-02,1.0",
                            "2026-01-03,2.5", "2026-10-10,3.0"]) + "\n")
    _c = _prefix_fingerprint(_fx, CAL_LAST)
    check("s9b a bar repaired inside the window DOES move it", _c != _a)
    _mem = {"AAA": _a}
    _d1 = panel_inputs_sha256(_mem)
    _saved = WARMUP_ROWS
    try:
        globals()["WARMUP_ROWS"] = _saved + 1
        _d2 = panel_inputs_sha256(_mem)
    finally:
        globals()["WARMUP_ROWS"] = _saved
    check("s9c a moved rule constant changes the digest", _d1 != _d2)
    _ok_hit, _ = cache_meta_valid({"cutoff": CAL_LAST, "inputs_sha256": _d1},
                                  _mem)
    _ok_old, _why_old = cache_meta_valid({"cutoff": CAL_LAST}, _mem)
    _ok_drift, _why_drift = cache_meta_valid(
        {"cutoff": CAL_LAST, "inputs_sha256": _d1}, {"AAA": _c})
    check("s9d a matching digest is a hit, a pre-digest cache is not, and a "
          "repaired member is a named MISS",
          _ok_hit and not _ok_old and not _ok_drift
          and "digest" in _why_old and "digest" in _why_drift)

    n_pass = sum(1 for _, c in ok if c)
    print(f"selftest: {n_pass}/{len(ok)} PASS")
    return 0 if n_pass == len(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--shards", type=int, default=N_SHARDS)
    r.add_argument("--workers", type=int, default=None)
    sub.add_parser("finalize")
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "finalize":
        return cmd_finalize()
    if not (0 <= a.shard < a.shards):
        print("shard out of range")
        return 1
    return cmd_run(a.shard, a.shards, a.workers)


if __name__ == "__main__":
    sys.exit(main())



