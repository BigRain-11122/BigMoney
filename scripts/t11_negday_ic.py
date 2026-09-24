"""scripts/t11_negday_ic.py -- T11_NEGDAY_IC runner (T-11 first consumption batch).

Prereg (frozen pre-run; J18: fix implementation, never criteria):
research/shortline/T11_NEGDAY_MASK.md

Factor-layer IC exploration of the QuantBull negative-announcement ban mask:
2 scopes (H hard-core 10-kw / W wide 15-kw) x 4 ban windows N in
{5,10,20,40} trading days = 8 cells; K=50 event-permutation nulls per cell
(seed family 20260929+i, SEED_REGISTRY "t11_negday_ic"); gates V1/V2/V3 +
IS n_periods >= 80 (prereg SS4); IS <= 2025-06-30 / OOS after (batch split,
prereg SS3 -- company IS_END degenerates on the 2024 library hole); h10 sole
gating horizon, h5/h20 report-only for passers. Engine ledger N untouched
(IC batch, P-4-2a precedent). ZERO-TOUCH: QuantBull/ read-only.

Lane: runnable_pool entry T11-NEGDAY-IC, lane_owner=bm-b (p1c_stock price
cache is bm-b-resident; physical data dependency disclosed in ticket).

Subcommands:
  run       -- data gates -> equivalence gate -> 400 null draws (parallel,
               per-draw checkpoint resume) -> 8 real cells -> gates -> JSON+CSV
  selftest  -- hermetic offline checks (no panel, no Money02 dependency)

Exit codes: 0 = normal, 2 = data-gate/machinery fault (report honestly).
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))  # R116: spawn-safe path

from pa_lhb_ic import (BARS_DIR, CACHE_DIR, fwd_ret, ic_from_ranks,  # noqa: E402
                       rank_rows)
from composite_ic import ic_series, stats_block  # noqa: E402
import science_gates  # noqa: E402

EVENTS_PATH = os.path.join(ROOT, "QuantBull", "data", "negative_events.parquet")
PREREG_PATH = os.path.join(ROOT, "research", "shortline", "T11_NEGDAY_MASK.md")
OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")
NULL_CKPT_DIR = os.path.join(OUT_DIR, "t11_negday_ic_nulls")

EVIDENCE_CUTOFF = "2026-09-22"          # frozen panel truncation (prereg SS2)
WIN_START = "2023-01-01"                # probe warmup + pre-event slice
T11_IS_END = pd.Timestamp("2025-06-30")  # batch split (prereg SS3)
COMPANY_IS_END = pd.Timestamp("2024-12-31")  # descriptive period count only

H_GATE = 10
H_REPORT = [5, 20]
N_GRID = [5, 10, 20, 40]
N_NULLS = 50
SEED_BASE = 20260929                    # SEED_REGISTRY "t11_negday_ic"
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
IS_MIN_PERIODS = 80                     # prereg SS4 adapted period gate
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400
WORKERS = 12
MIN_EVENTS_ROWS = 4000
MIN_PANEL_COLS = 5000
LAG_FIRST = 2                           # ban active from T+2 (prereg SS2)

KW_ALL = ["立案", "行政处罚", "处罚决定", "退市风险", "终止上市", "警示函",
          "监管函", "资金占用", "占用资金", "失信", "债务逾期", "违规",
          "冻结", "立案调查", "问询函"]
KW_HARD = ["立案", "行政处罚", "处罚决定", "退市风险", "终止上市", "失信",
           "债务逾期", "资金占用", "占用资金", "冻结"]
SCOPES = [("H", KW_HARD), ("W", KW_ALL)]


# ---------------------------------------------------------- pure functions
def scope_mask(titles, keywords):
    pat = "|".join(keywords)
    return titles.astype(str).str.contains(pat, na=False)


def dedup_events(ev):
    """Frozen dedup rule: (code,date) multi-announcement = 1 event, keep first."""
    return ev.drop_duplicates(subset=["date", "code"], keep="first")


def build_ban(ind, n):
    """Binary ban panel from event indicator grid: ban rows r+2 .. r+1+n."""
    ban = np.zeros_like(ind, dtype=bool)
    for k in range(LAG_FIRST, n + LAG_FIRST):
        ban[k:] |= ind[:-k]
    return ban.astype(np.float64)


def make_ind(r_idx, c_idx, shape):
    ind = np.zeros(shape, dtype=bool)
    ind[r_idx, c_idx] = True
    return ind


def draw_null_codes(date_rows, date_counts, rng, ncols):
    """Permutation null: same dates, same per-date counts, random identity."""
    r_parts, c_parts = [], []
    for r, m in zip(date_rows, date_counts):
        cs = rng.choice(ncols, size=int(m), replace=False)
        r_parts.append(np.full(int(m), r, dtype=np.int64))
        c_parts.append(cs.astype(np.int64))
    if not r_parts:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    return np.concatenate(r_parts), np.concatenate(c_parts)


def gate_row(blk_is, blk_oos, v1_thr):
    """V1/V2/V3 + period gate (prereg SS4, |absolute value| verdicts)."""
    if "ic_mean" not in blk_is or "ic_mean" not in blk_oos:
        return {"v1": False, "v2": False, "v3": False, "period_gate": False,
                "pass": False}
    v1 = abs(blk_is["ic_mean"]) > v1_thr
    v2 = abs(blk_is["ic_ir"]) >= V2_IR
    v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
          and abs(blk_oos["ic_mean"]) >= V3_RETAIN * abs(blk_is["ic_mean"]))
    pg = blk_is["n_periods"] >= IS_MIN_PERIODS
    return {"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
            "period_gate": bool(pg), "pass": bool(v1 and v2 and v3 and pg)}


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= T11_IS_END]),
            stats_block(s[s.index > T11_IS_END]))


# ------------------------------------------------- parallel null machinery
_W = {}


def _worker_init(eff, r_fwd, cal_us):
    _W["eff"] = eff
    _W["r_fwd"] = r_fwd
    _W["cal"] = cal_us


def _null_task(job):
    scope, i, seed, date_rows, date_counts, ncols, shape = job
    fp = os.path.join(NULL_CKPT_DIR, "%s_%02d.json" % (scope, i))
    if os.path.exists(fp):
        try:
            with open(fp, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            pass  # corrupt partial -> redo (atomic replace on write)
    rng = np.random.default_rng(seed)
    r_idx, c_idx = draw_null_codes(date_rows, date_counts, rng, ncols)
    ind = make_ind(r_idx, c_idx, shape)
    out = {"scope": scope, "draw": i, "seed": seed, "n": {}}
    for n in N_GRID:
        s = ic_from_ranks(rank_rows(_W["eff"], build_ban(ind, n)),
                          _W["r_fwd"], _W["cal"])
        blk = stats_block(s[s.index <= T11_IS_END])
        out["n"][str(n)] = {"abs_is_ic": abs(blk.get("ic_mean", np.nan))
                            if "ic_mean" in blk else None,
                            "abs_is_ir": abs(blk.get("ic_ir", np.nan))
                            if "ic_mean" in blk else None,
                            "is_n_periods": blk.get("n_periods")}
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    os.replace(tmp, fp)
    return out


# ----------------------------------------------------------------- helpers
def _data_gates():
    if not os.path.exists(EVENTS_PATH):
        return "events parquet missing: " + EVENTS_PATH
    ev = pd.read_parquet(EVENTS_PATH)
    if len(ev) < MIN_EVENTS_ROWS:
        return "events rows %d < %d" % (len(ev), MIN_EVENTS_ROWS)
    for f in ("dates.npy", "close.npy", "amount.npy"):
        if not os.path.exists(os.path.join(CACHE_DIR, f)):
            return "panel cache missing: " + os.path.join(CACHE_DIR, f)
    return None


def _machine_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id", "")
    except (OSError, ValueError):
        return ""


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# --------------------------------------------------------------------- run
def run():
    t0 = time.time()
    err = _data_gates()
    if err:
        print("DATA GATE FAIL:", err, flush=True)
        sys.exit(2)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(NULL_CKPT_DIR, exist_ok=True)

    # ---- panel slice (dates int64 microseconds; truncate to cutoff)
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    cut_us = np.datetime64(EVIDENCE_CUTOFF + "T00:00:00", "us")
    win_us = np.datetime64(WIN_START + "T00:00:00", "us")
    i0 = int(np.searchsorted(dates_all, win_us.astype("int64")))
    i1 = int(np.searchsorted(dates_all, cut_us.astype("int64"), side="right"))
    cal = dates_all[i0:i1]
    if len(cal) == 0 or cal[-1] < cut_us.astype("int64"):
        print("DATA GATE FAIL: panel does not cover evidence cutoff "
              + EVIDENCE_CUTOFF, flush=True)
        sys.exit(2)
    T = len(cal)
    files = sorted(glob_bars())
    syms = [os.path.basename(p)[:-8] for p in files]
    N = len(syms)
    if N < MIN_PANEL_COLS:
        print("DATA GATE FAIL: panel cols %d < %d" % (N, MIN_PANEL_COLS),
              flush=True)
        sys.exit(2)
    sym_col = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                                mmap_mode="r")[i0:i1], dtype=np.float64)
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                mmap_mode="r")[i0:i1], dtype=np.float64)
    print("panel slice: T=%d (%s -> %s) x N=%d (%.0fs)"
          % (T, str(cal[0].astype("datetime64[us]"))[:10],
             str(cal[-1].astype("datetime64[us]"))[:10], N, time.time() - t0),
          flush=True)

    # ---- events: dedup -> W refilter -> scope placement
    ev_raw = pd.read_parquet(EVENTS_PATH)
    n_raw = len(ev_raw)
    ev = dedup_events(ev_raw)
    n_dedup = len(ev)
    wmask = scope_mask(ev["title"], KW_ALL)
    ev = ev[wmask].copy()
    n_refilter_drop = n_dedup - len(ev)
    ev_us = (pd.to_datetime(ev["date"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["code"].map(sym_col)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    ev = ev[keep]
    r_all = pos[keep]
    c_all = cols.values[keep].astype(int)
    scope_events = {}
    for name, kw in SCOPES:
        m = scope_mask(ev["title"], kw).values
        scope_events[name] = (r_all[m], c_all[m])
    n_drop_col = int((~col_ok & pos_ok).sum())
    n_drop_date = int((~pos_ok & col_ok).sum())
    print("events: raw=%d dedup=%d refilter_drop=%d placed_all=%d "
          "(drop_no_col=%d delisted-era, drop_no_date=%d) (%.0fs)"
          % (n_raw, n_dedup, n_refilter_drop, len(ev), n_drop_col,
             n_drop_date, time.time() - t0), flush=True)
    if len(ev) == 0:
        print("DATA GATE FAIL: no events map to panel", flush=True)
        sys.exit(2)

    # ---- availability mask, forward returns, shared fwd ranks
    A = np.isfinite(close) & np.isfinite(amount)
    fwd10 = fwd_ret(close, H_GATE)
    eff = A & np.isfinite(fwd10)
    R_fwd = rank_rows(eff, fwd10)

    # ---- equivalence gate: fast path vs composite_ic.ic_series reference
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(20260923)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub].astype("datetime64[us]"))
    ref = ic_series(pd.DataFrame(probe[sub], index=sub_idx),
                    pd.DataFrame(fwd10[sub], index=sub_idx))
    eff_sub = eff[sub] & np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    fast = ic_from_ranks(rank_rows(eff_sub, probe[sub]),
                         rank_rows(eff_sub, fwd10[sub]), cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) \
        else 9.9
    print("equivalence gate: n_ref=%d n_fast=%d common=%d max|diff|=%.2e"
          % (len(ref), len(fast), len(common), worst), flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting batch (no numbers produced)",
              flush=True)
        sys.exit(2)

    # ---- null draws (parallel, per-draw checkpoint resume)
    jobs = []
    for name, _kw in SCOPES:
        r_idx, _c = scope_events[name]
        date_rows, date_counts = np.unique(r_idx, return_counts=True)
        for i in range(N_NULLS):
            seed = SEED_BASE + (i if name == "H" else N_NULLS + i)
            jobs.append((name, i, seed, date_rows, date_counts, N, (T, N)))
    t1 = time.time()
    n_skip = sum(os.path.exists(os.path.join(
        NULL_CKPT_DIR, "%s_%02d.json" % (j[0], j[1]))) for j in jobs)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_worker_init,
                             initargs=(eff, R_fwd, cal)) as ex:
        null_results = list(ex.map(_null_task, jobs))
    print("null draws: %d jobs (%d checkpoint-skipped) in %.0fs"
          % (len(jobs), n_skip, time.time() - t1), flush=True)

    thresholds = {}
    for name, _kw in SCOPES:
        draws = [r for r in null_results if r["scope"] == name]
        for n in N_GRID:
            icv = [d["n"][str(n)]["abs_is_ic"] for d in draws
                   if d["n"][str(n)]["abs_is_ic"] is not None]
            irv = [d["n"][str(n)]["abs_is_ir"] for d in draws
                   if d["n"][str(n)]["abs_is_ir"] is not None]
            thresholds["%s_%d" % (name, n)] = {
                "p95_abs_ic": round(float(np.quantile(icv, 0.95)), 4),
                "p95_abs_ir": round(float(np.quantile(irv, 0.95)), 4),
                "n_nulls": len(icv)}

    # ---- real cells + gates
    rows = []
    for name, _kw in SCOPES:
        r_idx, c_idx = scope_events[name]
        ind = make_ind(r_idx, c_idx, (T, N))
        for n in N_GRID:
            tw = time.time()
            s = ic_from_ranks(rank_rows(eff, build_ban(ind, n)), R_fwd, cal)
            blk_full, blk_is, blk_oos = seg_stats(s)
            key = "%s_%d" % (name, n)
            rec = {"cell": "negban_%s_%d" % (name, n), "scope": name,
                   "ban_days": n, "status": "ok",
                   "v1_thr": max(V1_FLOOR, thresholds[key]["p95_abs_ic"])}
            for seg, blk in [("full", blk_full), ("is", blk_is),
                             ("oos", blk_oos)]:
                for k in ("ic_mean", "ic_ir", "n_periods"):
                    rec["h%d_%s_%s" % (H_GATE, seg, k)] = blk.get(k, "")
            s_cis = s[s.index <= COMPANY_IS_END]
            rec["company_is_n_periods_desc"] = int(len(s_cis.dropna()))
            rec.update(gate_row(blk_is, blk_oos, rec["v1_thr"]))
            if rec["pass"]:
                for h in H_REPORT:
                    fw = fwd_ret(close, h)
                    eff_h = A & np.isfinite(fw)
                    sh_ = ic_from_ranks(rank_rows(eff_h, build_ban(ind, n)),
                                        rank_rows(eff_h, fw), cal)
                    _, bis, bos = seg_stats(sh_)
                    rec["h%d_is_ic" % h] = bis.get("ic_mean", "")
                    rec["h%d_oos_ic" % h] = bos.get("ic_mean", "")
            rec["compute_s"] = round(time.time() - tw, 1)
            rows.append(rec)
            print("  %s is_ic=%s ir=%s pass=%s (%.0fs)"
                  % (rec["cell"], rec.get("h10_is_ic_mean"),
                     rec.get("h10_is_ic_ir"), rec["pass"],
                     rec["compute_s"]), flush=True)

    n_pass = int(sum(r["pass"] for r in rows))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES_DIR, "t11_negday_ic_results.csv"),
              index=False, encoding="utf-8")

    batch_trials = 8 + N_NULLS * 2 * len(N_GRID) + 2 * n_pass
    ledger = science_gates.append_ledger(
        "T11_NEGDAY_IC", batch_trials,
        file_name="results/shortline/t11_negday_ic.json",
        note="T-11 first consumption batch: negban mask 2 scopes x N{5,10,20,"
             "40} IC cells + 400 event-permutation nulls + passer report cols"
             " (XSTOCK counting); engine ledger N untouched",
        evidence_cutoff=EVIDENCE_CUTOFF)
    out = {
        "meta": {"batch": "T11_NEGDAY_IC (QuantBull negative-event ban-mask "
                          "factor IC, T-11 first consumption)",
                 "pre_reg": "research/shortline/T11_NEGDAY_MASK.md",
                 "prereg_sha256": _sha256(PREREG_PATH),
                 "order": "O-20260924-1045", "claim": "MSG-20260924-2232",
                 "ticket": "T-2026-09-24-11",
                 "machine": _machine_id(),
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": str(T11_IS_END.date()),
                 "split_note": "batch split IS<=2025-06-30 (prereg SS3; "
                               "company IS_END=2024-12-31 degenerates on the "
                               "2024 library hole - desc column carries "
                               "company-IS period count only)",
                 "gate_horizon": H_GATE, "report_horizons": H_REPORT,
                 "n_nulls_per_cell": N_NULLS, "seed_base": SEED_BASE,
                 "lag_trade_days": LAG_FIRST,
                 "window": "%s -> %s (evidence cutoff truncated)"
                           % (WIN_START, EVIDENCE_CUTOFF),
                 "dedup_rule": "per (code,date) keep first",
                 "scopes": {"H": KW_HARD, "W": KW_ALL},
                 "engine_runs": 0},
        "science_gates": science_gates.cutoff_meta(EVIDENCE_CUTOFF),
        "equivalence": {"max_abs_diff": worst, "n_common": int(len(common)),
                        "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "thresholds": thresholds,
        "events": {"raw_rows": n_raw, "dedup_stock_days": n_dedup,
                   "refilter_dropped": n_refilter_drop, "placed": len(ev),
                   "dropped_no_cache_col": n_drop_col,
                   "dropped_no_calendar_date": n_drop_date,
                   "n_event_dates": int(len(np.unique(r_all))),
                   "coverage_note": "109/~690 trading days sampled; 2024 "
                                    "year-zero hole + monthly holes (source "
                                    "day-fetch partial success); uncovered-"
                                    "date events pollute the 0-group -> "
                                    "dilution bias is |IC|-downward "
                                    "(conservative), prereg SS2/SS5.7",
                   "survivorship_note": "event codes beyond the bars cache "
                                        "are delisted-era names; post-event "
                                        "returns unmeasurable (PA precedent)"},
        "panel": {"T": T, "N": N,
                  "start": str(cal[0].astype("datetime64[us]"))[:10],
                  "end": str(cal[-1].astype("datetime64[us]"))[:10]},
        "counts": {"computed": len(rows), "pass": n_pass},
        "rows": rows,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "workers": WORKERS,
                  "ic_computations": batch_trials,
                  "lane": "in-round inline (elapsed see elapsed_sec; O-2100 "
                          "<5min threshold; p1c panel local to this machine)",
                  "cpu_cap_policy": "O-20260924-1136 low-priority full-load "
                                    "(BelowNormal pool workers)"},
    }
    with open(os.path.join(OUT_DIR, "t11_negday_ic.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\n=== T11_NEGDAY_IC: computed=%d pass=%d (%.0fs) ==="
          % (len(rows), n_pass, time.time() - t0), flush=True)


def glob_bars():
    import glob
    return glob.glob(os.path.join(BARS_DIR, "*.parquet"))


# ---------------------------------------------------------------- selftest
def selftest():
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))

    print("T11_NEGDAY_IC selftest (hermetic, no panel):")
    # 1. ban window math: event at r -> ban rows r+2..r+1+n inclusive
    ind = np.zeros((30, 3), dtype=bool)
    ind[10, 1] = True
    ban = build_ban(ind, 5)
    ok("ban window rows r+2..r+1+n",
       ban[12:17, 1].all() and not ban[11, 1] and not ban[17, 1]
       and ban[:, 1].sum() == 5 and not ban[:, 0].any())
    # 2. scope filter: H subset of W; soft letters only in W
    titles = pd.Series(["收到立案告知书", "关于问询函的回复", "债务逾期公告",
                        "日常经营公告"])
    w = scope_mask(titles, KW_ALL)
    h = scope_mask(titles, KW_HARD)
    ok("scope filter H subset of W",
       bool(w[0] and not h[1] and h[2] and not w[3] and h[0]
            and (h & ~w).sum() == 0))
    # 3. dedup rule keep-first
    ev = pd.DataFrame({"date": ["2025-01-01", "2025-01-01"],
                      "code": ["000001", "000001"],
                      "title": ["a", "b"]})
    ok("dedup (code,date) keep first", len(dedup_events(ev)) == 1)
    # 4. null draw: per-date count preserved, deterministic, no replacement
    rng1 = np.random.default_rng(7)
    rng2 = np.random.default_rng(7)
    rng3 = np.random.default_rng(8)
    r1, c1 = draw_null_codes(np.array([5, 9]), np.array([3, 2]), rng1, 50)
    r2, c2 = draw_null_codes(np.array([5, 9]), np.array([3, 2]), rng2, 50)
    r3, c3 = draw_null_codes(np.array([5, 9]), np.array([3, 2]), rng3, 50)
    ok("null determinism same seed", np.array_equal(r1, r2)
       and np.array_equal(c1, c2))
    ok("null seeds differ", not np.array_equal(c1, c3))
    ok("null per-date counts preserved",
       (r1 == 5).sum() == 3 and (r1 == 9).sum() == 2
       and len(set(c1[r1 == 5].tolist())) == 3)
    # 5. gates math (synthetic blocks)
    g = gate_row({"ic_mean": -0.03, "ic_ir": -0.35, "n_periods": 100},
                 {"ic_mean": -0.02, "ic_ir": -0.2, "n_periods": 50}, 0.02)
    ok("gates all-pass case", g["v1"] and g["v2"] and g["v3"]
       and g["period_gate"] and g["pass"])
    g2 = gate_row({"ic_mean": 0.019, "ic_ir": 0.5, "n_periods": 100},
                  {"ic_mean": 0.019, "ic_ir": 0.5, "n_periods": 50}, 0.02)
    ok("gates v1 floor block", not g2["v1"] and not g2["pass"])
    g3 = gate_row({"ic_mean": 0.05, "ic_ir": 0.35, "n_periods": 79},
                  {"ic_mean": 0.06, "ic_ir": 0.4, "n_periods": 50}, 0.02)
    ok("gates period gate block", not g3["period_gate"] and not g3["pass"])
    g4 = gate_row({"ic_mean": 0.05, "ic_ir": 0.35, "n_periods": 100},
                  {"ic_mean": -0.01, "ic_ir": 0.0, "n_periods": 50}, 0.02)
    ok("gates v3 sign block", not g4["v3"] and not g4["pass"])
    # 6. split boundary
    s = pd.Series([1.0, 2.0, 3.0], index=pd.DatetimeIndex(
        ["2025-06-30", "2025-07-01", "2025-07-02"]))
    full, iss, oos = seg_stats(s)
    ok("T11 split boundary", iss["n_periods"] == 1 and oos["n_periods"] == 2)
    # 7. IC path sign: banned group with lower fwd -> negative IC
    T, N = 6, 10
    close = np.full((T, N), 10.0)
    fwd = np.full((T, N), 0.01)
    fwd[:, [0, 1]] = -0.05           # banned names underperform
    vals = np.zeros((T, N))
    vals[:, [0, 1]] = 1.0
    eff = np.ones((T, N), dtype=bool)
    cal_test = np.array([int(np.datetime64("2025-01-0%d" % d, "us")
                                .astype("int64")) for d in range(1, 7)])
    s2 = ic_from_ranks(rank_rows(eff, vals), rank_rows(eff, fwd), cal_test)
    ok("IC machinery sign on synthetic", len(s2) > 0 and (s2 < -0.9).all())
    # 8. ledger block shape (temp dir, empty head -> prev 0)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        led = science_gates.append_ledger("SELFTEST", 8, "x.json",
                                          results_dir=td,
                                          evidence_cutoff="2026-09-22")
        ok("ledger block shape",
           led["prev_total"] == 0 and led["batch_trials"] == 8
           and led["total"] == 8 and led["evidence_cutoff"] == "2026-09-22")
    print("SELFTEST", "PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "run":
        run()
    else:
        selftest()
