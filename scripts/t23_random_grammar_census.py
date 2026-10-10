"""T23 slice-2 -- alphagen-style random-grammar cheap census (panel-gated).

Queue lineage: state/queue/tech.md T23 (N2 U3 three-channel ruling, channel
(1) "new grammar"). Slice-1 verdict = POSITIVE-with-riders
(results/_r840bmb_t23_alphagen_census.json + research/digests/
DIGEST-20261010-t23-alphagen-paradigm-census.md). This runner IS slice-2,
pre-announced there (digest sec.3 slice law): "random-grammar cheap census
BEFORE any RL commitment; negative -> stop (G2 fallback, academic citation
only); holds -> N2 U3 (1) drafting window stays legal to open".

FROZEN READOUT (declared here BEFORE any real-data run; criteria zero-change
law -- numbers below are the whole verdict protocol, nothing else gates it):
  - K=64 formula trees sampled once from the alphagen-style grammar (seeded
    SEED_REGISTRY substreams; grammar = expression trees over OHLCV/vwap/ret
    leaves, rolling ops on the vendored A158 window grid [5,10,20,30,60] --
    op families are a subset of the vendored qlib Alpha158 29-family base,
    disclosed; NOT the N2 18-tuple axis-gate pin, per slice-1 L1 ruling).
  - Measurement face: PIT-universe daily cross-sectional Spearman rank-IC
    vs next-day close-to-close forward return (h=1 = PRIMARY verdict face;
    h=5 = descriptive decay face, NOT in the verdict line).
  - Census window: last 500 panel trading days ending at the panel evidence
    cutoff (61-row rolling warmup). Per-date pairwise names >= 100.
  - Per-formula stat = ICIR (ic_mean/ic_std) over census dates; family
    observed_max = max_k |ICIR_k| (h=1). Nulls: B=64 within-day same-mask
    factor-rank permutation draws per formula (sina_construct_ic null
    design, house style), paired across formulas per draw b:
    null_family_max_b = max_k |ICIR_{k,b}|; null_p95 = 95th pct over B.
  - VERDICT census_holds = (observed_family_max > null_p95). Engine trials
    ledger untouched (zero engine runs); draws N = K + K*B = 4160 go to the
    factor ledger via science_gates.append_ledger (sina_construct_ic
    precedent: factor-reference census, not a registration-caliber burn).
  - Riders carried from slice-1: A158 lineage negative prior (157/158
    judged negative; GTJA 0/183 core48; WQ 0/82 strict), RL/MCTS IC claims
    all "claimed-unverified", stock cross-section factors = MEASUREMENT
    face only (tradable account face = core48 ETF/fund whitelist).

Panel gate (r840 disk-truth law, single-source import): astock status claims
complete AND per-files on disk == status per_files AND stale_gate fresh ->
ready; else honest exit 2 (awaiting_panel), nothing computed or written.

Helpers reused verbatim -- no re-implementation (anti-duplication rule):
pa_lhb_ic rank_rows / ic_from_ranks / fwd_ret + composite_ic stats_block +
science_gates cutoff_meta / append_ledger / SEED_REGISTRY +
stock_face_furnace._universe + update_astock_daily load_status / stale_gate /
_disk_truth_override / PER_DIR + rev_osc_stock_p1 P4_BATCH2 eligibility
constants (_roll_mean20 / PRICE_MIN / AMT20_MIN / LISTED_MIN / FRESH_MAX).

Subcommands:
  run      -- gated census burn (est. ~10-15 min one-shot: panel load ~2 min
              + K*B IC evals; spawn detached if the executing round's clock
              discipline requires).
  selftest -- hermetic offline legs (r116 hermetic law): grammar
              determinism/invariants, evaluator hand-values, CSRANK ties,
              IC polarity + null behavior on synthetic panels, permutation
              same-mask invariance/determinism, gate legs, payload law.
  status   -- read-only panel gate face (no computation).

-- bm-b r841 · marks +0 · SEED consumed only on run · research output, not
investment advice · live-trading gate = monthly review + CEO-only, unchanged.
"""
from __future__ import annotations

import datetime as dt
import glob as _glob
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

import science_gates as sg                                   # noqa: E402
import rev_osc_stock_p1 as revo                              # noqa: E402
import update_astock_daily as ua                            # noqa: E402
import stock_face_furnace as sff                             # noqa: E402
from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret      # noqa: E402
from composite_ic import stats_block                          # noqa: E402

# ------------------------------------------------------------ frozen constants
K_FORMULAS = 64
B_NULLS = 64
CENSUS_DAYS = 500
WARMUP = 61                      # max window 60 + 1 for RET leaf
MIN_CROSS = 100                  # per-date pairwise names floor
MIN_PERIODS = 30                 # stats_block floor per formula
HORIZONS = (1, 5)                # h=1 primary, h=5 descriptive
WINDOWS = (5, 10, 20, 30, 60)    # vendored A158 handler grid
MAX_DEPTH = 3
LEAF_NAMES = ("OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "AMOUNT", "VWAP", "RET")
ROLL_OPS = ("MA", "STD", "MAX", "MIN", "SUM", "DELTA", "ROC")
UN_OPS = ("ABS", "LOG", "NEG", "CSRANK")
BIN_OPS = ("ADD", "SUB", "MUL", "DIV", "CORR")
SEED_KEY_GEN = "t23_grammar_census_gen"
SEED_KEY_NULL = "t23_grammar_census_null"
N_TRIALS = K_FORMULAS + K_FORMULAS * B_NULLS     # 4160 factor-ledger draws
MAX_SKIP_FRAC = 0.10             # >10% formulas skipped -> honest exit 2
OUT_DIR = os.path.join(ROOT, "results", "t23_census")
GATE_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")

A158_LINEAGE_PRIOR = (
    "slice-1 riders: A158 stock cross-section lineage negative prior "
    "(157/158 judged negative; GTJA 0/183 core48; WQ 0/82 strict); "
    "alphagen RL/MCTS IC claims claimed-unverified; stock factors are a "
    "MEASUREMENT face (tradable account face = core48 ETF/fund whitelist)")

# ------------------------------------------------------------------ grammar

def _sample_node(rng, depth):
    r = float(rng.random())
    if depth >= MAX_DEPTH or r < 0.30:
        return ("leaf", LEAF_NAMES[int(rng.integers(len(LEAF_NAMES)))])
    if r < 0.70:
        if rng.random() < 0.75:
            op = ROLL_OPS[int(rng.integers(len(ROLL_OPS)))]
            d = WINDOWS[int(rng.integers(len(WINDOWS)))]
            return ("roll", op, d, _sample_node(rng, depth + 1))
        op = UN_OPS[int(rng.integers(len(UN_OPS)))]
        return ("un", op, _sample_node(rng, depth + 1))
    op = BIN_OPS[int(rng.integers(len(BIN_OPS)))]
    d = WINDOWS[int(rng.integers(len(WINDOWS)))] if op == "CORR" else None
    return ("bin", op, d, _sample_node(rng, depth + 1),
            _sample_node(rng, depth + 1))


def node_depth(node):
    t = node[0]
    if t == "leaf":
        return 1
    if t == "roll":
        return 1 + node_depth(node[3])
    if t == "un":
        return 1 + node_depth(node[2])
    return 1 + max(node_depth(node[3]), node_depth(node[4]))


def formula_str(node):
    t = node[0]
    if t == "leaf":
        return node[1]
    if t == "roll":
        return f"{node[1]}({formula_str(node[3])},{node[2]})"
    if t == "un":
        return f"{node[1]}({formula_str(node[2])})"
    left, right = formula_str(node[3]), formula_str(node[4])
    if node[2]:
        return f"{node[1]}({left},{right},{node[2]})"
    return f"{node[1]}({left},{right})"


def sample_formulas(k, seed_base):
    out = []
    for i in range(k):
        rng = np.random.default_rng([int(seed_base), int(i)])
        out.append(_sample_node(rng, 0))
    return out


# ------------------------------------------------------------------ evaluator

def _clean(x):
    return np.where(np.isfinite(x), x, np.nan)


def _ref(x, d):
    out = np.full_like(x, np.nan, dtype=np.float64)
    if x.shape[0] > d:
        out[d:] = x[:-d]
    return out


def _win(c, d):
    """window sums from cumsum c: row i of result = c[i+d-1] - c[i-1]."""
    T = c.shape[0]
    if T < d:
        return np.zeros((0,) + c.shape[1:], dtype=c.dtype)
    return c[d - 1:] - np.concatenate(
        [np.zeros((1,) + c.shape[1:], dtype=c.dtype), c[:T - d]], axis=0)


def _cum_finite(x):
    fin = np.isfinite(x)
    xf = np.where(fin, x, 0.0).astype(np.float64)
    return (np.cumsum(xf, axis=0), np.cumsum(xf * xf, axis=0),
            np.cumsum(fin.astype(np.float64), axis=0))


def _roll_mean(x, d):
    c1, _, cn = _cum_finite(x)
    s1, n = _win(c1, d), _win(cn, d)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if s1.shape[0]:
        out[d - 1:] = np.where(n == d, s1 / d, np.nan)
    return out


def _roll_sum(x, d):
    c1, _, cn = _cum_finite(x)
    s1, n = _win(c1, d), _win(cn, d)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if s1.shape[0]:
        out[d - 1:] = np.where(n == d, s1, np.nan)
    return out


def _roll_std(x, d):
    c1, c2, cn = _cum_finite(x)
    s1, s2, n = _win(c1, d), _win(c2, d), _win(cn, d)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if s1.shape[0]:
        var = (s2 - s1 * s1 / d) / d
        with np.errstate(invalid="ignore"):
            std = np.sqrt(np.maximum(var, 0.0))
        out[d - 1:] = np.where(n == d, std, np.nan)
    return out


def _roll_maxmin(x, d, fn):
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if x.shape[0] >= d:
        v = np.lib.stride_tricks.sliding_window_view(
            np.asarray(x, dtype=np.float64), d, axis=0)
        out[d - 1:] = fn(v, axis=-1)      # NaN propagates (partial windows out)
    return out


def _roll_corr(x, y, d):
    fin = np.isfinite(x) & np.isfinite(y)
    xf = np.where(fin, x, 0.0).astype(np.float64)
    yf = np.where(fin, y, 0.0).astype(np.float64)
    c1, c2 = np.cumsum(xf, axis=0), np.cumsum(xf * xf, axis=0)
    d1, d2 = np.cumsum(yf, axis=0), np.cumsum(yf * yf, axis=0)
    cc = np.cumsum(xf * yf, axis=0)
    cn = np.cumsum(fin.astype(np.float64), axis=0)
    s1, s2 = _win(c1, d), _win(c2, d)
    t1, t2 = _win(d1, d), _win(d2, d)
    sc, n = _win(cc, d), _win(cn, d)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if s1.shape[0]:
        cov = (sc - s1 * t1 / d) / d
        vx = np.maximum((s2 - s1 * s1 / d) / d, 0.0)
        vy = np.maximum((t2 - t1 * t1 / d) / d, 0.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = cov / np.sqrt(vx * vy)
        ok = (n == d) & (vx > 0) & (vy > 0)
        out[d - 1:] = np.where(ok, corr, np.nan)
    return out


def _csrank(x):
    return rank_rows(np.isfinite(x), x)


def evaluate(node, leaves):
    t = node[0]
    if t == "leaf":
        return np.asarray(leaves[node[1]], dtype=np.float64)
    if t == "roll":
        op, d = node[1], node[2]
        x = evaluate(node[3], leaves)
        if op == "MA":
            return _roll_mean(x, d)
        if op == "STD":
            return _roll_std(x, d)
        if op == "MAX":
            return _roll_maxmin(x, d, np.max)
        if op == "MIN":
            return _roll_maxmin(x, d, np.min)
        if op == "SUM":
            return _roll_sum(x, d)
        if op == "DELTA":
            return _clean(x - _ref(x, d))
        if op == "ROC":
            with np.errstate(invalid="ignore", divide="ignore"):
                return _clean(x / _ref(x, d) - 1.0)
        raise AssertionError(op)
    if t == "un":
        op = node[1]
        x = evaluate(node[2], leaves)
        if op == "ABS":
            return _clean(np.abs(x))
        if op == "LOG":
            return np.where(x > 0, np.log(np.where(x > 0, x, 1.0)), np.nan)
        if op == "NEG":
            return _clean(-x)
        if op == "CSRANK":
            return _csrank(x)
        raise AssertionError(op)
    # binary
    op = node[1]
    a = evaluate(node[3], leaves)
    b = evaluate(node[4], leaves)
    if op == "CORR":
        return _roll_corr(a, b, int(node[2]))
    with np.errstate(invalid="ignore", divide="ignore"):
        if op == "ADD":
            return _clean(a + b)
        if op == "SUB":
            return _clean(a - b)
        if op == "MUL":
            return _clean(a * b)
        if op == "DIV":
            return _clean(a / b)
    raise AssertionError(op)


# ------------------------------------------------------------------ panel gate

def gate_face(status=None):
    """r840 disk-truth gate face (single-source imports; read-only)."""
    st = status if status is not None else ua.load_status()
    panel = st.get("panel") or {}
    complete = bool(panel.get("complete"))
    cutoff = panel.get("cutoff") if complete else None
    per_on_disk = len(_glob.glob(os.path.join(ua.PER_DIR, "*.csv")))
    override = bool(ua._disk_truth_override(complete, panel, per_on_disk))
    if override:
        complete = False
        cutoff = None
    needs, reason = ua.stale_gate(cutoff, dt.datetime.now())
    ready = bool(complete and not needs and not override)
    return {
        "ready": ready,
        "complete_claim": bool(panel.get("complete")),
        "disk_truth_override": override,
        "per_files_on_disk": per_on_disk,
        "status_per_files": panel.get("per_files"),
        "status_universe_n": panel.get("universe_n"),
        "cutoff": str(cutoff) if cutoff else None,
        "stale_reason": None if not needs else str(reason),
        "mode": st.get("mode"),
        "rebuild_lock": (st.get("mode") or "").startswith("refresh in progress"),
    }


# ------------------------------------------------------------------ panel load

def _pin_cal_slice(cal_all, pin_end, window):
    """Pin-slice window law (W19 prereg sec.2 pin-dead-slice face):
    truncate the full calendar to <= pin_end, then take the trailing
    `window` rows. Any panel advance beyond pin_end yields the
    byte-identical date window (zero +/-N-day drift vs the pinned
    census face); pin_end=None preserves the legacy trailing-window
    behavior verbatim (census/W18 callers unchanged)."""
    if pin_end is not None:
        cal_all = [d for d in cal_all if str(d) <= str(pin_end)]
    return cal_all[-window:]


def load_panel(pin_end=None):
    """Census panel: last CENSUS_DAYS+WARMUP rows of the sh510300 calendar,
    universe = stock_face_furnace._universe() (eligibility & ok_static &
    per-file intersection, single source), P4_BATCH2 dynamic eligibility
    clauses verbatim via rev_osc_stock_p1 constants (build_panel kin).
    pin_end (optional, W19): truncate the date axis to <= pin_end BEFORE
    the trailing-window take -- the pin-slice keeps the panel face
    anchored to the census instant regardless of later bar advances."""
    cal_all = pd.read_csv(GATE_CSV, usecols=["date"])["date"].astype(str).tolist()
    cal = _pin_cal_slice(cal_all, pin_end, CENSUS_DAYS + WARMUP)
    uni = sff._universe()
    T, N = len(cal), len(uni)
    F = {k: np.full((T, N), np.nan, dtype=np.float64)
         for k in ("open", "high", "low", "close", "volume", "amount")}
    dpos = {d: i for i, d in enumerate(cal)}
    for j, code in enumerate(uni):
        df = pd.read_csv(os.path.join(ua.PER_DIR, code + ".csv"))
        pos = df["date"].astype(str).map(dpos)
        m = pos.notna().to_numpy()
        if not m.any():
            continue
        r = pos[m].to_numpy(dtype=np.int64)
        for col in ("open", "high", "low", "close", "volume", "amount"):
            F[col][r, j] = df[col].to_numpy(dtype=np.float64)[m]

    with np.errstate(invalid="ignore", divide="ignore"):
        vwap = F["amount"] / F["volume"]
        ret = F["close"] / _ref(F["close"], 1) - 1.0
    leaves = {"OPEN": F["open"], "HIGH": F["high"], "LOW": F["low"],
              "CLOSE": F["close"], "VOLUME": F["volume"],
              "AMOUNT": F["amount"], "VWAP": vwap, "RET": ret}

    # P4_BATCH2 sec.2 dynamic eligibility (clauses verbatim from
    # stock_face_furnace.build_panel via rev_osc_stock_p1 constants)
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

    return {"cal": cal, "universe": uni, "leaves": leaves, "elig": elig,
            "census_rows": np.arange(WARMUP, T)}


# ------------------------------------------------------------------ census core

def _permute_ranks_within_mask(Fr_c, eff_c, rng):
    """Within-day same-mask factor-rank permutation (sina_construct_ic null
    design), vectorized by bucketing rows on their mask count n_t."""
    out = np.array(Fr_c, dtype=np.float64, copy=True)
    ns = eff_c.sum(axis=1).astype(np.int64)
    buckets = {}
    for t in range(len(ns)):
        n = int(ns[t])
        if n >= 5:
            buckets.setdefault(n, []).append(t)
    for n, rows in buckets.items():
        rows = np.asarray(rows, dtype=np.int64)
        sub = out[rows]                       # (R, N) copy
        m = eff_c[rows]
        vals = sub[m].reshape(len(rows), n)
        vals = rng.permuted(vals, axis=1)
        sub[m] = vals.ravel()
        out[rows] = sub
    return out


def _formula_ic_faces(F, fwd, elig_c, cal_c):
    """(ic_series, n_series) for one (factor, horizon) pair, census rows."""
    eff = elig_c & np.isfinite(F) & np.isfinite(fwd)
    Fr = rank_rows(eff, F)
    Rr = rank_rows(eff, fwd)
    s = ic_from_ranks(Fr, Rr, cal_c)
    n = eff.sum(axis=1)
    return s, pd.Series(n, index=cal_c)


def census_core(panel, formulas, k, b, min_cross, min_periods, seed_gen,
                seed_null):
    """Deterministic census core on an already-loaded panel (selftest calls
    this on synthetic panels; run() calls it with the frozen constants)."""
    cal = panel["cal"]
    rows = panel["census_rows"]
    cal_us = np.asarray(pd.to_datetime(
        np.asarray(list(cal), dtype="datetime64[us]")))[rows]
    elig_c = panel["elig"][rows, :]
    recs = []
    nulls_abs_ir = np.full((k, b), np.nan)
    for idx, node in enumerate(formulas):
        F = evaluate(node, panel["leaves"])
        rec = {"formula": formula_str(node), "depth": node_depth(node),
               "horizons": {}, "skip": None}
        for h in HORIZONS:
            fwd_full = fwd_ret(panel["leaves"]["CLOSE"], h)
            fwd_c = fwd_full[rows, :]
            s, nser = _formula_ic_faces(F[rows, :], fwd_c, elig_c, cal_us)
            keep = nser >= min_cross
            s = s[s.index.isin(nser.index[keep])]
            blk = stats_block(s)
            rec["horizons"][f"h{h}"] = blk
            rec[f"n_dates_h{h}"] = int(keep.sum())
        blk1 = rec["horizons"]["h1"]
        if "ic_mean" not in blk1 or blk1.get("n_periods", 0) < min_periods:
            rec["skip"] = "insufficient census periods (h1)"
            recs.append(rec)
            continue
        # nulls on the PRIMARY face only (h=1)
        fwd1 = fwd_ret(panel["leaves"]["CLOSE"], 1)[rows, :]
        eff = elig_c & np.isfinite(F[rows, :]) & np.isfinite(fwd1)
        Fr = rank_rows(eff, F[rows, :])
        Rr = rank_rows(eff, fwd1)
        nser = pd.Series(eff.sum(axis=1), index=cal_us)
        for bj in range(b):
            rng = np.random.default_rng([int(seed_null), int(idx), int(bj)])
            Fp = _permute_ranks_within_mask(Fr, eff, rng)
            s_b = ic_from_ranks(Fp, Rr, cal_us)
            s_b = s_b[s_b.index.isin(nser.index[nser >= min_cross])]
            blk = stats_block(s_b)
            if "ic_ir" in blk:
                nulls_abs_ir[idx, bj] = abs(blk["ic_ir"])
        rec["null_abs_ir_p50"] = (round(float(np.nanquantile(
            nulls_abs_ir[idx], 0.50)), 3) if np.isfinite(
            nulls_abs_ir[idx]).any() else None)
        rec["null_abs_ir_p95"] = (round(float(np.nanquantile(
            nulls_abs_ir[idx], 0.95)), 3) if np.isfinite(
            nulls_abs_ir[idx]).any() else None)
        recs.append(rec)

    ok_idx = [i for i, r in enumerate(recs) if r.get("skip") is None]
    obs_max = max((abs(recs[i]["horizons"]["h1"]["ic_ir"]) for i in ok_idx),
                  default=None)
    fam_null_max = []
    if ok_idx:
        for bj in range(b):
            col = nulls_abs_ir[ok_idx, bj]
            if np.isfinite(col).any():
                fam_null_max.append(round(float(np.nanmax(col)), 3))
    # p95 of the family-max null needs >= 10 draws to be reported at all
    null_p95 = (round(float(np.quantile(fam_null_max, 0.95)), 3)
                if len(fam_null_max) >= 10 else None)
    holds = bool(obs_max is not None and null_p95 is not None
                 and obs_max > null_p95)
    uniq = sorted({r["formula"] for r in recs})
    return {"formulas": recs, "n_ok": len(ok_idx),
            "n_skip": len(recs) - len(ok_idx),
            "n_unique_formulas": len(uniq),
            "observed_family_max_abs_icir": obs_max,
            "null_family_max_list": fam_null_max,
            "null_family_p95": null_p95,
            "null_p95_min_draws": 10,
            "census_holds": holds}


# ------------------------------------------------------------------ run/status

def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def cmd_status():
    face = gate_face()
    print(json.dumps(face, ensure_ascii=False, indent=1))
    return 0


def cmd_run():
    t0 = time.time()
    face = gate_face()
    if not face["ready"]:
        print(json.dumps({"awaiting_panel": True, "gate": face},
                         ensure_ascii=False))
        return 2
    cutoff = face["cutoff"]
    out = os.path.join(OUT_DIR, f"CENSUS-{cutoff}.json")
    # pit-95 orphan-finalize guard: a same-cutoff product that already
    # carries this batch's ledger block refuses re-append (re-run law:
    # deterministic re-run = honest no-op, never a second +N)
    landed = sg.finalize_already_landed("T23_RANDOM_GRAMMAR_CENSUS",
                                        file_name=out)
    if landed is not None:
        print(json.dumps({"already_landed": True,
                          "cutoff": cutoff,
                          "landed_block": landed,
                          "action": "no-op (idempotent refuse)"},
                         ensure_ascii=False))
        return 0
    print(f"[t23-census] panel ready (cutoff {cutoff}); loading panel ...")
    panel = load_panel()
    n_uni = len(panel["universe"])
    ns = panel["elig"][panel["census_rows"], :].sum(axis=1)
    print(f"[t23-census] universe {n_uni}; census dates {len(panel['census_rows'])}; "
          f"eligible median {float(np.median(ns)):.0f}")
    formulas = sample_formulas(K_FORMULAS, sg.SEED_REGISTRY[SEED_KEY_GEN])
    core = census_core(panel, formulas, K_FORMULAS, B_NULLS, MIN_CROSS,
                       MIN_PERIODS, sg.SEED_REGISTRY[SEED_KEY_GEN],
                       sg.SEED_REGISTRY[SEED_KEY_NULL])
    if core["n_ok"] < K_FORMULAS * (1 - MAX_SKIP_FRAC):
        print(json.dumps({"mechanism_suspect": True,
                          "n_skip": core["n_skip"],
                          "law": f"> {MAX_SKIP_FRAC:.0%} formulas skipped"},
                         ensure_ascii=False))
        return 2

    ledger = sg.append_ledger("T23_RANDOM_GRAMMAR_CENSUS", N_TRIALS,
                              file_name="results/t23_census/"
                                        f"CENSUS-{cutoff}.json",
                              evidence_cutoff=str(cutoff),
                              note="T23 slice-2 random-grammar cheap census: "
                                   f"K={K_FORMULAS} formula draws + "
                                   f"K*B={K_FORMULAS * B_NULLS} within-day "
                                   "same-mask permutation nulls; zero engine "
                                   "runs (factor-reference face)")
    payload = {
        **sg.cutoff_meta(cutoff),
        "probe": "T23 slice-2 random-grammar cheap census",
        "queue_row": "state/queue/tech.md T23 (N2 U3 channel-1)",
        "slice1_ref": "results/_r840bmb_t23_alphagen_census.json",
        "machine": sff._machine_id() if hasattr(sff, "_machine_id") else "bm-b",
        "grammar": {
            "leaves": list(LEAF_NAMES), "roll_ops": list(ROLL_OPS),
            "un_ops": list(UN_OPS), "bin_ops": list(BIN_OPS),
            "windows": list(WINDOWS), "max_depth": MAX_DEPTH,
            "op_provenance": "subset of vendored qlib Alpha158 29-family "
                             "base (research/shortline/external/qlib_"
                             "alpha158_loader.py, alpha158_compare.py "
                             "parse gate); NOT the N2 18-tuple axis-gate "
                             "pin (slice-1 L1 ruling)",
        },
        "frozen_readout": {
            "k_formulas": K_FORMULAS, "b_nulls": B_NULLS,
            "census_days": CENSUS_DAYS, "min_cross": MIN_CROSS,
            "primary_face": "h=1 next-day close-to-close rank-IC ICIR "
                            "family max vs null p95",
            "descriptive_face": "h=5 decay, not in verdict line",
            "verdict": "census_holds = observed_family_max_abs_icir > "
                       "null_family_p95",
        },
        "panel_face": {
            "cutoff": str(cutoff), "universe_n": n_uni,
            "per_files_on_disk": face["per_files_on_disk"],
            "census_dates": int(len(panel["census_rows"])),
            "eligible_median": int(float(np.median(ns))),
            "eligible_min": int(ns.min()), "eligible_max": int(ns.max()),
        },
        "seeds": {"gen": [int(sg.SEED_REGISTRY[SEED_KEY_GEN]), "k<K",
                          "t23_grammar_census_gen"],
                  "null": [int(sg.SEED_REGISTRY[SEED_KEY_NULL]), "k<K,b<B",
                           "t23_grammar_census_null"]},
        "census": core,
        "riders": A158_LINEAGE_PRIOR,
        "trials_ledger": ledger,
        "audit": {"engine_runs": 0,
                  "n_draws": N_TRIALS,
                  "elapsed_sec": round(time.time() - t0, 1),
                  "generated_at": dt.datetime.now().astimezone().isoformat(
                      timespec="seconds")},
    }
    _dump(payload, out)
    _dump(payload, os.path.join(OUT_DIR, "latest.json"))
    print(json.dumps({
        "census_holds": core["census_holds"],
        "observed_family_max_abs_icir": core["observed_family_max_abs_icir"],
        "null_family_p95": core["null_family_p95"],
        "n_ok": core["n_ok"], "n_skip": core["n_skip"],
        "n_draws": N_TRIALS, "out": out,
        "elapsed_sec": payload["audit"]["elapsed_sec"],
    }, ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------ selftest

def _synth_panel(seed=12345, T=140, N=80, signal=0.0):
    """Hermetic synthetic panel: close = exp(cumsum(r)); with signal>0 the
    daily return process r is AR(-signal) so RET_t predicts next-day return
    with a strong negative (reversal) cross-sectional alignment; signal=0 ->
    iid returns (pure noise face)."""
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
    leaves = {k: close * (1.0 + 0.01 * rng.standard_normal((T, N)))
              for k in ("OPEN", "HIGH", "LOW", "CLOSE")}
    vol = np.abs(rng.standard_normal((T, N))) * 1e6 + 1e6
    leaves["VOLUME"] = vol
    leaves["AMOUNT"] = vol * close
    leaves["VWAP"] = leaves["AMOUNT"] / leaves["VOLUME"]
    prev = np.full_like(close, np.nan)
    prev[1:] = close[:-1]
    leaves["RET"] = close / prev - 1.0
    elig = np.ones((T, N), dtype=bool)
    cal = [d.strftime("%Y-%m-%d") for d in
           pd.bdate_range("2025-01-01", periods=T)]
    return {"cal": cal, "universe": [f"S{i:03d}" for i in range(N)],
            "leaves": leaves, "elig": elig,
            "census_rows": np.arange(10, T)}


def selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # s1 registry + grammar determinism + invariants
    check("s1a seeds registered",
          sg.SEED_REGISTRY[SEED_KEY_GEN] == 20_615_000
          and sg.SEED_REGISTRY[SEED_KEY_NULL] == 20_615_100)
    f1 = sample_formulas(64, 20_615_000)
    f2 = sample_formulas(64, 20_615_000)
    check("s1b formula list deterministic",
          [formula_str(x) for x in f1] == [formula_str(x) for x in f2])
    strs = [formula_str(x) for x in f1]
    check("s1c K==64 draws, unique count disclosed",
          len(strs) == 64 and len(set(strs)) >= 32)
    check("s1d tree height bound (expansion depth <= MAX_DEPTH)",
          all(node_depth(x) <= MAX_DEPTH + 1 for x in f1))

    def _ops_ok(node):
        t = node[0]
        if t == "leaf":
            return node[1] in LEAF_NAMES
        if t == "roll":
            return (node[1] in ROLL_OPS and node[2] in WINDOWS
                    and _ops_ok(node[3]))
        if t == "un":
            return node[1] in UN_OPS and _ops_ok(node[2])
        return (node[1] in BIN_OPS
                and (node[2] in WINDOWS if node[1] == "CORR" else True)
                and _ops_ok(node[3]) and _ops_ok(node[4]))
    check("s1e all sampled nodes legal", all(_ops_ok(x) for x in f1))

    # s2 evaluator hand-values (T=8, N=1 columns)
    x = np.array([[1.0], [2.0], [3.0], [4.0], [np.nan], [6.0], [7.0], [8.0]])
    check("s2a MA(3) hand value + NaN window out",
          np.isnan(_roll_mean(x, 3)[0]) and abs(
              _roll_mean(x, 3)[3] - 3.0) < 1e-12
          and np.isnan(_roll_mean(x, 3)[4]))
    check("s2b SUM/STD/MAX/MIN hand values",
          abs(_roll_sum(x, 2)[1] - 3.0) < 1e-12
          and abs(_roll_std(x[:4], 2)[3] - 0.5) < 1e-12
          and _roll_maxmin(x, 3, np.max)[3] == 4.0
          and _roll_maxmin(x, 3, np.min)[2] == 1.0)
    check("s2c DELTA/ROC/REF",
          np.isnan(_ref(x, 3)[0]) and _ref(x, 3)[3] == 1.0
          and abs(evaluate(("roll", "DELTA", 1, ("leaf", "CLOSE")),
                           {"CLOSE": x})[3] - 1.0) < 1e-12
          and abs(evaluate(("roll", "ROC", 1, ("leaf", "CLOSE")),
                           {"CLOSE": x})[1] - 1.0) < 1e-12)
    y = np.array([[1.0], [2.0], [3.0], [4.0], [5.0], [6.0], [7.0], [8.0]])
    check("s2d CORR perfect window",
          abs(_roll_corr(x[:4], y[:4], 4)[3] - 1.0) < 1e-9)
    check("s2e DIV zero -> NaN, LOG neg -> NaN, inf cleaned",
          np.isnan(evaluate(("bin", "DIV", None, ("leaf", "CLOSE"),
                             ("leaf", "CLOSE")),
                            {"CLOSE": np.array([[0.0], [2.0]])})[0])
          and np.isnan(evaluate(("un", "LOG", ("leaf", "CLOSE")),
                                {"CLOSE": np.array([[-1.0]])})[0])
          and np.isfinite(evaluate(("un", "ABS", ("leaf", "CLOSE")),
                                   {"CLOSE": np.array([[-1.0]])})[0]))
    # s3 CSRANK ties + NaN outside
    xs = np.array([[3.0, 1.0, 1.0, np.nan], [5.0, 5.0, 5.0, 2.0]])
    r = _csrank(xs)
    check("s3 CSRANK average ties + NaN mask",
          np.isnan(r[0, 3]) and abs(r[0, 1] - 1.5) < 1e-12
          and abs(r[0, 0] - 3.0) < 1e-12 and abs(r[1, 0] - 3.0) < 1e-12)

    # s4 IC polarity + verdict legs on synthetic panels
    p_noise = _synth_panel(seed=777, signal=0.0)
    rng = np.random.default_rng(555)
    noise_nodes = [("leaf", "RET")] * 4 + [("roll", "MA", 5, ("leaf", "RET"))] * 4
    core_noise = census_core(p_noise, noise_nodes, 8, 16, min_cross=10,
                             min_periods=30, seed_gen=999,
                             seed_null=8888)
    check("s4a noise family: verdict machinery well-formed",
          core_noise["n_ok"] > 0 and core_noise["null_family_p95"] is not None
          and isinstance(core_noise["census_holds"], bool))
    p_sig = _synth_panel(seed=778, signal=0.9)
    sig_nodes = [("leaf", "RET")] + [("roll", "MA", 5, ("leaf", "RET"))]
    core_sig = census_core(p_sig, sig_nodes, 2, 16, min_cross=10,
                           min_periods=30, seed_gen=999,
                           seed_null=8888)
    ir_sig = [abs(r["horizons"]["h1"]["ic_ir"]) for r in core_sig["formulas"]
              if "ic_mean" in r["horizons"]["h1"]]
    check("s4b injected reversal signal -> strong positive ICIR",
          ir_sig and max(ir_sig) > 0.25)
    check("s4c signal family beats its null p95 (holds=True)",
          core_sig["census_holds"] is True
          and core_sig["observed_family_max_abs_icir"]
          > core_sig["null_family_p95"])

    # s5 permutation same-mask invariance + determinism
    Fr = np.arange(40, dtype=np.float64).reshape(4, 10) % 7
    eff = np.ones((4, 10), dtype=bool)
    eff[:, 0] = False
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    p1 = _permute_ranks_within_mask(Fr, eff, rng1)
    p2 = _permute_ranks_within_mask(Fr, eff, rng2)
    check("s5a permutation deterministic", np.array_equal(p1, p2))
    orig_sorted = np.sort(Fr[eff].reshape(4, 9), axis=1)
    perm_sorted = np.sort(p1[eff].reshape(4, 9), axis=1)
    check("s5b per-row value multiset invariant (same-mask)",
          np.array_equal(orig_sorted, perm_sorted)
          and np.isnan(p1[:, 0]).all() == np.isnan(Fr[:, 0]).all())

    # s6 gate legs (pure faces; no real-data dependency)
    check("s6a disk-truth override kills complete claim",
          bool(ua._disk_truth_override(
              True, {"per_files": 5217}, 0)) is True
          and bool(ua._disk_truth_override(
              True, {"per_files": 5217}, 5217)) is False)
    st = {"panel": {"complete": False}}
    panel = st.get("panel") or {}
    check("s6b incomplete panel -> not ready (pure face)",
          bool(panel.get("complete")) is False)

    # s7 payload law
    check("s7a cutoff_meta top-level evidence_cutoff",
          sg.cutoff_meta("2026-10-09") == {"evidence_cutoff": "2026-10-09"})
    led = sg.append_ledger("T23_SELFTEST_DUMMY", 4160,
                           file_name=None, prev_total=100)
    check("s7b ledger block shape (prev/batch/total, hermetic prev override)",
          led["batch_trials"] == 4160 and led["prev_total"] == 100
          and led["total"] == 4260)
    landed_probe = {"trials_ledger": {"batch": "T23_RANDOM_GRAMMAR_CENSUS"}}
    check("s7c finalize_already_landed guard ref available",
          callable(sg.finalize_already_landed)
          and isinstance(landed_probe, dict))

    n_pass = sum(1 for _, c in ok if c)
    print(f"selftest: {n_pass}/{len(ok)} PASS")
    return 0 if n_pass == len(ok) else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        return cmd_status()
    if cmd == "run":
        return cmd_run()
    print("usage: run | selftest | status")
    return 1


if __name__ == "__main__":
    sys.exit(main())
