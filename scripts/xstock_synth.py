"""XSTOCK_SYNTH harness (stock-pool cross-library small-K synthesis).

Pre-reg (frozen BEFORE the run): research/shortline/XSTOCK_SYNTH.md
Claim: MSG-20260924-0905 (commit cb8f03d, F-04 lane lock). Prereg was frozen
BEFORE WQ finalize (rule-based material selection = snooping-proof).

Shelf (prereg SS2, rule-frozen):
  LHB 3  = pa_lhb_ic.json V1&V2&V3 passers (count_20/days_since/amt_share_20)
  GTJA   = p1c_stock_ic.json pool_h10 members with alpha191_ prefix (21)
  WQ     = pool_h1d0 members without the prefix (count unknown until finalize)
  dzjy 1 = p1d_ext_slots_ic.json passer dzjy_amt_share_20
Population (nullB, SS4): GTJA ok + WQ ok + LHB 4 (incl netbuy) + dzjy/margin 7.

Implementation notes (honest, engineering layer only - science unchanged):
  - prereg SS0's wall-clock budget ("nulls 6-11min") under-costed the nullB
    member storage: 274 IS-segment z-panels at T_is~8.4k x N 5222 float32
    ~= 175MB/member ~= 48GB RAM = infeasible to hold. Execution mechanics =
    disk z-cache (Money02/data/cache/xstock_z/, gitignored regenerable, same
    precedent as p1c_stock cache) + date-block streaming nulls. Same draws,
    same seeds, same z/min_valid/sign orientation as primary - symmetric.
  - unified synthesis grid = full p1c cache panel (all 5222 cols, dates
    truncated to evidence_cutoff 2026-09-22; the cache itself ends 09-22).
    Prereg SS3 parenthetical binds to "P-1c factor-batch convention", which
    is the full-cache NaN-masked panel (close-finite tradability) - that is
    also the only grid on which per-source reproduction at 1e-4 can hold.
    ok_universe=5130 describes cache build status, disclosed in JSON meta.
  - event-source members are era-gated: LHB grids NaN before 2007-01-01
    (P-A WIN_START; LHB history begins 2007-01-04), dzjy/margin grids NaN
    before 2010-01-01 (P-1d WIN_START). Within-era 0-fill per prereg SS3
    ("no-event baseline is information, pre-era absence is not"). Uniform
    across shelf AND population -> primary/nulls symmetric.

Subcommands:
  gates    run-blocked gate stack (exit 0 = run allowed):
             G1 WQ finalize (meta.wq_complete true)  -> exit 2 if unmet
             G2 shelf rules vs recorded JSONs        -> exit 2 on mismatch
             G3 population composition              -> exit 2 on mismatch
             G4 data presence (caches/parquets)      -> exit 2 on missing
             G5 disk >= 60GB free (z-cache ~48GB)    -> exit 2 if tight
             G6 seeds 51000/52000 in SEED_REGISTRY  -> exit 2 if missing
  selftest offline logic gates (synthetic; zero vendor/panel loads)
  repro --src {lhb,dzjy}
           shelf-member reproduction legs vs recorded evidence (prereg
           SS2 hard gate; PA2-verbatim / p1d-verbatim conventions)
  run      staged batch; WQ-gated (exit 3 until gates G1 green). The
           streaming-null machinery + z-cache io + repro legs are
           delivered (r85); remaining stages: member grid build on the
           unified panel, z-cache build, clustering, primary, nulls.

Ledger: zero engine runs (engine N untouched); factor ledger added per prereg
SS0 = 1 primary + 2 sensitivity + 2000 nulls (+1 h20 if primary passes V1);
member series reproductions NOT counted (XLIB/PS2/g25 precedent).

Outputs (when run lands): results/shortline/xstock_synth.json (top-level
evidence_cutoff via science_gates.cutoff_meta) +
research/shortline/xstock_synth_results.csv + prereg SS7/SS8 backfill.
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END                       # '2024-12-31' convention
from science_gates import cutoff_meta

OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")
PA_JSON = os.path.join(OUT_DIR, "pa_lhb_ic.json")
P1C_JSON = os.path.join(OUT_DIR, "p1c_stock_ic.json")
P1D_JSON = os.path.join(OUT_DIR, "p1d_ext_slots_ic.json")
Z_CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "xstock_z")

CUTOFF = pd.Timestamp("2026-09-22")                   # evidence_cutoff (prereg SS3)
IS_END_TS = pd.Timestamp(IS_END)
LHB_ERA = np.datetime64("2007-01-01", "us").astype("int64")   # P-A WIN_START
EXT_ERA = np.datetime64("2010-01-01", "us").astype("int64")   # P-1d WIN_START

H_GATE = 10
N_NULLS = 1000
SEED_NULLA = 51000          # prereg SS4 (registered; 51100 deprecated)
SEED_NULLB = 52000
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
CLUSTER_CORR = 0.5
MIN_OVERLAP = 200
K_PRIMARY, MV_PRIMARY = 4, 3
K_SENS = [(3, 2), (5, 3)]
REPRO_TOL = 1e-4             # prereg SS2 letter (dense members, full-precision records)
REPRO_TOL_ROUNDED = 0.5e-4   # 4dp-rounded records (pa/p1d); half of last digit
DISK_MIN_GB = 60.0           # z-cache ~48GB + headroom
EXPECTED = {
    "lhb_shelf": {"lhb_count_20", "lhb_days_since", "lhb_amt_share_20"},
    "lhb_pop": {"lhb_count_20", "lhb_days_since", "lhb_amt_share_20",
                "lhb_netbuy_amt_60"},
    "dzjy_shelf": {"dzjy_amt_share_20"},
    "dzjy_pop": {"dzjy_count_20", "dzjy_deep_disc_5", "dzjy_amt_share_20",
                 "dzjy_prem_mean_20", "margin_buy_int_5", "margin_bal_chg_20",
                 "margin_short_int_20"},
    "gtja_shelf_n": 21,
}


# ------------------------------------------------------------------ rules

def _load(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def build_shelf_and_population():
    """Prereg SS2/SS4 rule loader (recorded JSONs only; zero panel loads).

    Returns (report, shelf, population, p1c_rows) where shelf/population are
    sorted name lists and report carries per-source counts + rule outcomes.
    """
    pa = _load(PA_JSON)
    p1c = _load(P1C_JSON)
    p1d = _load(P1D_JSON)

    lhb_pass = {r["factor"] for r in pa["rows"] if r.get("pass")}
    lhb_all = {r["factor"] for r in pa["rows"] if r.get("status") == "ok"}
    pool = list(p1c.get("pool_h10") or [])
    gtja_shelf = sorted(n for n in pool if n.startswith("alpha191_"))
    wq_shelf = sorted(n for n in pool if not n.startswith("alpha191_"))
    p1c_ok = sorted(r["factor"] for r in p1c["rows"] if r.get("status") == "ok")
    dzjy_pass = {r["factor"] for r in p1d["rows"]
                 if r.get("pass") and not r["factor"].startswith("gdhs_")}
    dzjy_all = {r["factor"] for r in p1d["rows"]
                if r.get("status") == "ok"
                and not r["factor"].startswith("gdhs_")}

    shelf = sorted(lhb_pass | set(gtja_shelf) | set(wq_shelf) | dzjy_pass)
    population = sorted(set(p1c_ok) | lhb_all | dzjy_all)
    report = {
        "lhb_shelf": sorted(lhb_pass),
        "lhb_pop": sorted(lhb_all),
        "gtja_shelf": gtja_shelf,
        "wq_shelf": wq_shelf,
        "dzjy_shelf": sorted(dzjy_pass),
        "dzjy_pop": sorted(dzjy_all),
        "p1c_ok_n": len(p1c_ok),
        "shelf_n": len(shelf),
        "population_n": len(population),
        "wq_complete": bool(p1c.get("meta", {}).get("wq_complete")),
        "shelf_is_subset_of_population": bool(set(shelf) <= set(population)),
    }
    return report, shelf, population, p1c


def era_mask(dates_us, which):
    """Era gate for event-source member grids (prereg SS3 0-fill clause).

    dates_us: int64 us timestamps (cache convention). Returns boolean array:
    True where the date is at/after the source era start.
    """
    era = LHB_ERA if which == "lhb" else EXT_ERA
    return dates_us >= era


def draw_indices(names, k, seed):
    """Deterministic oriented-draw index table (prereg SS4 matched nulls).

    Returns (n_nulls, k) int array; row i uses rng(seed+i), draw without
    replacement - frozen construction, identical across primary/null runs.
    """
    names = list(names)
    out = np.empty((N_NULLS, k), dtype=np.int64)
    for i in range(N_NULLS):
        rng = np.random.default_rng(seed + i)
        out[i] = rng.choice(len(names), k, replace=False)
    return out


def greedy_cluster(order, corr_fn, threshold=CLUSTER_CORR):
    """Prereg SS1 clustering: |IS IC| descending greedy, first cluster with
    corr>=threshold wins, else own family; rep = strongest |IS IC| (order[0]
    of the family). corr_fn(a, b) -> float (pairwise-complete IC-series corr).
    """
    reps, families = [], {}
    for name in order:
        placed = None
        for r in reps:
            c = corr_fn(name, r)
            if np.isfinite(c) and c >= threshold:
                placed = r
                break
        if placed is None:
            reps.append(name)
            families[name] = [name]
        else:
            families[placed].append(name)
    return reps, families


# ------------------------------------------------------------------- gates

def run_gates():
    t0 = time.time()
    report, shelf, population, p1c = build_shelf_and_population()
    checks = {}
    # G1 WQ finalize
    checks["g1_wq_finalize"] = {
        "wq_complete": report["wq_complete"],
        "pass": bool(report["wq_complete"]),
    }
    # G2 shelf rules vs recorded JSONs
    g2 = {
        "lhb_shelf_ok": set(report["lhb_shelf"]) == EXPECTED["lhb_shelf"],
        "dzjy_shelf_ok": set(report["dzjy_shelf"]) == EXPECTED["dzjy_shelf"],
        "gtja_shelf_n_ok": len(report["gtja_shelf"]) == EXPECTED["gtja_shelf_n"],
        "wq_shelf_n": len(report["wq_shelf"]),
        "shelf_subset_ok": report["shelf_is_subset_of_population"],
    }
    checks["g2_shelf_rules"] = {**g2, "pass": bool(
        g2["lhb_shelf_ok"] and g2["dzjy_shelf_ok"] and g2["gtja_shelf_n_ok"]
        and g2["shelf_subset_ok"])}
    # G3 population composition
    n_expected_pop = (report["p1c_ok_n"] + len(EXPECTED["lhb_pop"])
                      + len(EXPECTED["dzjy_pop"]))
    g3 = {
        "population_n": report["population_n"],
        "expected_approx": n_expected_pop,
        "lhb_pop_ok": set(report["lhb_pop"]) == EXPECTED["lhb_pop"],
        "dzjy_pop_ok": set(report["dzjy_pop"]) == EXPECTED["dzjy_pop"],
        "gdhs_excluded_ok": not any(n.startswith("gdhs_")
                                     for n in population),
    }
    checks["g3_population"] = {**g3, "pass": bool(
        g3["lhb_pop_ok"] and g3["dzjy_pop_ok"] and g3["gdhs_excluded_ok"]
        and report["population_n"] >= 200)}
    # G4 data presence
    cache = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
    g4_paths = {
        "p1c_cache_meta": os.path.join(cache, "meta.json"),
        "p1c_cache_close": os.path.join(cache, "close.npy"),
        "lhb_parquet": os.path.join(ROOT, "Money02", "data", "lhb",
                                    "lhb_detail.parquet"),
        "ext_dzjy_dir": os.path.join(ROOT, "data", "ext_slots", "dzjy"),
        "ext_margin_dir": os.path.join(ROOT, "data", "ext_slots", "margin"),
    }
    g4 = {k: os.path.exists(v) for k, v in g4_paths.items()}
    checks["g4_data_presence"] = {**g4, "pass": bool(all(g4.values()))}
    # G5 disk headroom for the z-cache (~48GB)
    try:
        import shutil
        free_gb = shutil.disk_free(ROOT) / 2**30 if hasattr(
            shutil, "disk_free") else shutil.disk_usage(ROOT).free / 2**30
    except Exception:
        free_gb = -1.0
    checks["g5_disk"] = {"free_gb": round(free_gb, 1),
                         "need_gb": DISK_MIN_GB,
                         "pass": bool(free_gb >= DISK_MIN_GB)}
    # G6 seeds registered (SEED_REGISTRY: batch_name -> seed base; 'policy'
    # key holds a prose string -> numeric values only)
    try:
        from science_gates import SEED_REGISTRY
        regs = {int(v) for v in SEED_REGISTRY.values()
                if isinstance(v, (int, float))}
        g6 = bool(SEED_NULLA in regs and SEED_NULLB in regs)
        detail = "in-registry"
    except Exception as e:
        regs, g6, detail = set(), False, f"load-fail: {type(e).__name__}"
    checks["g6_seeds"] = {"nullA": SEED_NULLA, "nullB": SEED_NULLB,
                          "pass": bool(g6), "detail": detail}

    all_pass = all(c["pass"] for c in checks.values())
    out = {
        "meta": {"batch": "XSTOCK_SYNTH gates", "prereg":
                 "research/shortline/XSTOCK_SYNTH.md SS2/SS4",
                 "claim": "MSG-20260924-0905", "date":
                 time.strftime("%Y-%m-%d %H:%M"),
                 "elapsed_s": round(time.time() - t0, 1)},
        "shelf_report": report,
        "checks": checks,
        "pass": bool(all_pass),
    }
    print(json.dumps({"checks": {k: v["pass"] for k, v in checks.items()},
                      "shelf_n": report["shelf_n"],
                      "population_n": report["population_n"],
                      "wq_shelf_n": len(report["wq_shelf"])}, indent=1))
    return out, all_pass


# ---------------------------------------------------------------- run path
# Delivered r85 (implementation round 2/N); execution stages stay WQ-gated
# via `gates` (G1). Design frozen in r84 notes + module header:
#   z-cache    = one float32 .npy per member, row 0 = cache date 0. IS dates
#                are a PREFIX of the full panel, so shelf (full-era) and
#                population (IS-only) files share IS row coordinates.
#   streaming  = date-block tasks (Z_BLOCK dates); each member file read
#                exactly once across the whole job (~48GB I/O total); worker
#                RAM ~0.4-0.8GB (member blocks dict-cached per task).
#   equivalence= streaming per-draw IC vs direct composite materialization
#                must hold <=1e-6 BEFORE any null number (selftest now on a
#                synthetic panel; real-cache gate reruns in the null stage).

Z_BLOCK = 64                      # dates per streaming block task
EQUIV_TOL_STREAM = 1e-6
REPRO_TOL_MEAN_R4 = 0.5e-4        # 4dp-rounded records (pa/p1d): half last digit
REPRO_TOL_IR_R3 = 0.5e-3          # 3dp-rounded IR records
Z_MANIFEST = os.path.join(OUT_DIR, "xstock_z_manifest.json")


def z_cache_write(name, z):
    """Write one member z-panel (float32). Callers pass the z of the member
    on the unified grid (ps2 z_rows: per-date cross-section, MIN_Z_NAMES=5
    floor, close-finite mask). kind ('shelf' full-era / 'pop' IS-only) is
    recorded in the manifest by the build stage."""
    os.makedirs(Z_CACHE_DIR, exist_ok=True)
    path = os.path.join(Z_CACHE_DIR, name.replace("/", "_") + ".npy")
    np.save(path, np.asarray(z, dtype=np.float32))
    return path


def z_read_block(path, row0, nrows):
    arr = np.load(path, mmap_mode="r")
    return np.asarray(arr[row0:row0 + nrows], dtype=np.float64)


def _null_block_task(payload):
    """One date-block pass: per-draw per-date IC values over the z-cache.

    Top-level picklable (parallel_runner contract: no closures). Semantics
    identical to the direct reference (ps2_synth composite_z + rank_rows +
    ic_from_ranks; eff = close-finite & finite(comp) & finite(fwd)):
    equivalence-gated before any number is consumed.
    payload keys: row0, nrows (IS-segment window), close_path, close_row0
    (p1c cache row of IS row 0), n_cols, h, files (member z-cache paths,
    draw indices point here), draws (n,K) int, signs (n,K) float,
    min_valid, cal (nrows int64-us IS slice).
    Returns {draw_id, date_pos, ic} arrays (date_pos = absolute IS row).
    """
    from ps2_synth import composite_z, fwd_ret, ic_from_ranks, rank_rows
    row0, nrows = payload["row0"], payload["nrows"]
    h, mv, cal = payload["h"], payload["min_valid"], payload["cal"]
    files, draws, signs = payload["files"], payload["draws"], payload["signs"]
    cm = np.load(payload["close_path"], mmap_mode="r")
    c0 = payload["close_row0"] + row0     # cache row of this block's start
    end = min(cm.shape[0], c0 + nrows + h)
    close_ext = np.asarray(cm[c0:end], dtype=np.float64)
    fwd = fwd_ret(close_ext, h)[:nrows]          # tail fwd from +h rows
    finite = np.isfinite(close_ext[:nrows])
    n_draws, k = draws.shape
    blocks = {}                                   # member block cache
    out_d, out_p, out_v = [], [], []
    for d in range(n_draws):
        zs = []
        for j in range(k):
            mi = int(draws[d, j])
            if mi not in blocks:
                blocks[mi] = z_read_block(files[mi], row0, nrows)
            z = blocks[mi]
            zs.append(z if signs[d, j] > 0 else -z)
        comp = composite_z(zs, mv)
        eff = finite & np.isfinite(comp) & np.isfinite(fwd)
        if not eff.any():
            continue
        s = ic_from_ranks(rank_rows(eff, comp), rank_rows(eff, fwd), cal)
        if len(s) == 0:
            continue
        idx_us = s.index.values.astype("datetime64[us]").astype("int64")
        pos = np.searchsorted(cal, idx_us)         # cal sorted; exact hits
        out_d.append(np.full(len(s), d, dtype=np.int32))
        out_p.append((row0 + pos).astype(np.int32))
        out_v.append(s.values.astype(np.float64))
    if out_d:
        return {"draw_id": np.concatenate(out_d),
                "date_pos": np.concatenate(out_p),
                "ic": np.concatenate(out_v)}
    return {"draw_id": np.empty(0, np.int32),
            "date_pos": np.empty(0, np.int32),
            "ic": np.empty(0, np.float64)}


def streaming_null_pass(close_path, close_row0, n_cols, is_cal, files,
                        draws, signs, min_valid, h=H_GATE,
                        block=Z_BLOCK, parallel=True):
    """Block the IS calendar; run _null_block_task per block (serial or
    parallel_runner); assemble the (n_draws, T_is) IC matrix.

    Returns (ic_matrix, meta) - per-draw per-IS-row IC values (NaN where
    the date dropped out). Deterministic: rows keyed by date, not schedule.
    """
    t0 = time.time()
    T_is = len(is_cal)
    jobs = []
    for row0 in range(0, T_is, block):
        nrows = min(block, T_is - row0)
        payload = {"row0": row0, "nrows": nrows, "close_path": close_path,
                   "close_row0": close_row0, "n_cols": n_cols, "h": h,
                   "files": list(files), "draws": draws, "signs": signs,
                   "min_valid": min_valid, "cal": is_cal[row0:row0 + nrows]}
        jobs.append((f"blk{row0}", _null_block_task, (payload,)))
    if parallel:
        from parallel_runner import run_cells_parallel, worker_cap
        n_workers = worker_cap()
        try:
            import psutil
            free_gb = psutil.virtual_memory().available / 2**30
            n_workers = max(1, min(n_workers, int(free_gb * 0.8 / 1.1)))
        except Exception:
            pass
        out = run_cells_parallel(jobs, workers=n_workers,
                                 desc="null-blocks")
        blocks = [out[k] for k in
                  [f"blk{r}" for r in range(0, T_is, block)]]
        workers_used = out.get("__workers__", n_workers)
    else:
        blocks = [_null_block_task(j[2][0]) for j in jobs]
        workers_used = 1
    ic = np.full((len(draws), T_is), np.nan)
    for b in blocks:
        ic[b["draw_id"], b["date_pos"]] = b["ic"]
    meta = {"blocks": len(jobs), "workers": workers_used,
            "block_rows": block, "elapsed_s": round(time.time() - t0, 1)}
    return ic, meta


def null_abs_ic_p95(ic_matrix, lo, hi):
    """Per-draw IS |mean IC| over rows [lo, hi) of the draw table -> p95."""
    abs_mean = []
    for d in range(lo, hi):
        v = ic_matrix[d][np.isfinite(ic_matrix[d])]
        if len(v):
            abs_mean.append(abs(float(v.mean())))
    if not abs_mean:
        return float("nan"), 0
    return float(np.quantile(abs_mean, 0.95)), len(abs_mean)


# ------------------------------------------------- member reproduction legs
# Prereg SS2 hard gate (before ANY number): shelf members recomputed per
# their source-library convention vs recorded evidence. PA2 precedent:
# construction copied verbatim, anchor gate adjudicates fidelity.

def _lhb_event_grids(cal, col_map, n_cols):
    """PA2-verbatim LHB event-grid core (calendar-agnostic): dedup per
    (code,date) = max LHB turnover row, rolling windows, shift-1 signal
    grids. Returns (count_s, days_s, share_s, meta)."""
    from pa_lhb_ic import (LHB_PATH, W_COUNT, W_DECAY, W_SHARE, rolling_sum,
                           shift1)
    T = len(cal)
    lhb = pd.read_parquet(LHB_PATH)
    n_raw = len(lhb)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    n_events = len(ev)
    ev_us = (pd.to_datetime(ev["上榜日"]).values
             .astype("datetime64[us]").astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["代码"].map(col_map)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    r_idx, c_idx = pos[keep], cols.values[keep].astype(int)
    ind = np.zeros((T, n_cols))
    ind[r_idx, c_idx] = 1.0
    sh_grid = np.zeros((T, n_cols))
    sh_grid[r_idx, c_idx] = ev["成交额占总成交比"].values[keep]
    count20 = rolling_sum(ind, W_COUNT)
    share20 = rolling_sum(sh_grid, W_SHARE)
    with np.errstate(invalid="ignore", divide="ignore"):
        amt_share20 = np.where(count20 > 0, share20 / count20, np.nan)
    ev_pos = np.where(ind > 0, np.arange(T)[:, None], -1.0)
    last_ev = np.maximum.accumulate(ev_pos, axis=0)
    days_since = np.arange(T)[:, None] - last_ev
    days_since[last_ev < 0] = np.nan
    days_capped = np.where(days_since <= W_DECAY, days_since, np.nan)
    meta = {"raw_rows": n_raw, "dedup_events": n_events,
            "placed": int(keep.sum()), "T": T, "n_cols": n_cols}
    return (shift1(count20, 0.0), shift1(days_capped),
            shift1(amt_share20), meta)


def _seg_ic(mask, vals, fwd, cal):
    """ps2-verbatim masked rank IC -> (full, is, oos) stat blocks."""
    from ps2_synth import ic_from_ranks, rank_rows
    from composite_ic import stats_block
    eff = mask & np.isfinite(vals) & np.isfinite(fwd)
    if not eff.any():
        return {}, {}, {}
    s = ic_from_ranks(rank_rows(eff, vals), rank_rows(eff, fwd), cal)
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


def repro_lhb(write=True):
    """LHB shelf members (3) on the PA2-verbatim slice vs pa_lhb_ic.json
    records: is_ic/is_ir/is_n + oos_ic/oos_ir/oos_n (PA2 anchor tolerances,
    stricter than prereg 1e-4)."""
    from pa_lhb_ic import (BARS_DIR, CACHE_DIR, H_GATE, WIN_START, fwd_ret)
    t0 = time.time()
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(
        dates_all, np.datetime64(WIN_START, "us").astype("int64")))
    cal = dates_all[i0:]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms = [os.path.basename(p)[:-8] for p in files]
    col_map = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                               mmap_mode="r")[i0:], dtype=np.float64)
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                mmap_mode="r")[i0:], dtype=np.float64)
    count_s, days_s, share_s, gmeta = _lhb_event_grids(cal, col_map, len(syms))
    A = np.isfinite(close) & np.isfinite(amount)
    B = A & (count_s >= 1)
    C = A & np.isfinite(days_s)
    fwd10 = fwd_ret(close, H_GATE)
    pa = _load(PA_JSON)
    recs = {r["factor"]: r for r in pa["rows"]}
    rows, ok_all = [], True
    for name, vals, mask in (("lhb_count_20", count_s, A),
                             ("lhb_days_since", days_s, C),
                             ("lhb_amt_share_20", share_s, B)):
        _, bis, bos = _seg_ic(mask, vals, fwd10, cal)
        reg = recs[name]
        checks = {
            "is_ic": abs(bis["ic_mean"] - reg["h10_is_ic_mean"])
                     < REPRO_TOL_MEAN_R4,
            "is_ir": abs(bis["ic_ir"] - reg["h10_is_ic_ir"]) < REPRO_TOL_IR_R3,
            "is_n": bis["n_periods"] == reg["h10_is_n_periods"],
            "oos_ic": abs(bos["ic_mean"] - reg["h10_oos_ic_mean"])
                      < REPRO_TOL_MEAN_R4,
            "oos_ir": abs(bos["ic_ir"] - reg["h10_oos_ic_ir"])
                      < REPRO_TOL_IR_R3,
            "oos_n": bos["n_periods"] == reg["h10_oos_n_periods"],
        }
        ok = all(checks.values())
        ok_all &= ok
        rows.append({"factor": name, "ok": bool(ok),
                     "reproduced_is_ic": bis["ic_mean"],
                     "recorded_is_ic": reg["h10_is_ic_mean"],
                     "reproduced_oos_ic": bos["ic_mean"],
                     "recorded_oos_ic": reg["h10_oos_ic_mean"],
                     "checks": {k: bool(v) for k, v in checks.items()}})
        print(f"  repro {name}: is_ic={bis['ic_mean']:.5f} vs "
              f"{reg['h10_is_ic_mean']} oos_ic={bos['ic_mean']:.5f} vs "
              f"{reg['h10_oos_ic_mean']} ok={ok}", flush=True)
    out = {"meta": {"batch": "XSTOCK_SYNTH repro LHB leg",
                    "convention": "PA2-verbatim (WIN_START slice, masks A/B/C)",
                    "tol_mean": REPRO_TOL_MEAN_R4, "tol_ir": REPRO_TOL_IR_R3,
                    "elapsed_s": round(time.time() - t0, 1)},
           "grids": gmeta, "rows": rows, "pass": bool(ok_all)}
    if write:
        path = os.path.join(OUT_DIR, "xstock_repro_lhb.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False, default=str)
        print(f"saved: {path}", flush=True)
    print(f"REPRO-LHB {'PASS 3/3' if ok_all else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return out, bool(ok_all)


def repro_dzjy(write=True):
    """dzjy shelf member (dzjy_amt_share_20) on the p1d-verbatim panel
    (b_layer universe, WIN_START 2010 slice) vs p1d records."""
    import p1d_ext_slots_ic as p1d
    t0 = time.time()
    cal, col, close, amount, meta = p1d.load_panel()
    T, N = len(cal), len(col)
    A = np.isfinite(close) & np.isfinite(amount)
    amt0 = np.nan_to_num(amount)
    fwd10 = p1d.fwd_ret(close, p1d.H_GATE)

    def log(msg):
        print(msg, flush=True)

    ind, amtg, premw, deepg, dz_meta = p1d.build_dzjy(cal, col, T, N, log)
    amt20 = p1d.rolling_sum(amt0, p1d.W_DZJY)
    cnt20 = p1d.rolling_sum(ind, p1d.W_DZJY)
    with np.errstate(invalid="ignore", divide="ignore"):
        share20 = np.where(amt20 > 0,
                           p1d.rolling_sum(amtg, p1d.W_DZJY) / amt20, np.nan)
    f_share = p1d.shift_n(share20, p1d.DZJY_SHIFT)
    f_count = p1d.shift_n(cnt20, p1d.DZJY_SHIFT, 0.0)
    B_dzjy = A & (f_count >= 1)
    p1d_json = _load(P1D_JSON)
    reg = next(r for r in p1d_json["rows"]
               if r["factor"] == "dzjy_amt_share_20")
    _, bis, bos = _seg_ic(B_dzjy, f_share, fwd10, cal)
    checks = {
        "is_ic": abs(bis["ic_mean"] - reg["h10_is_ic_mean"]) < REPRO_TOL_MEAN_R4,
        "is_ir": abs(bis["ic_ir"] - reg["h10_is_ic_ir"]) < REPRO_TOL_IR_R3,
        "is_n": bis["n_periods"] == reg["h10_is_n_periods"],
        "oos_ic": abs(bos["ic_mean"] - reg["h10_oos_ic_mean"]) < REPRO_TOL_MEAN_R4,
        "oos_ir": abs(bos["ic_ir"] - reg["h10_oos_ic_ir"]) < REPRO_TOL_IR_R3,
        "oos_n": bos["n_periods"] == reg["h10_oos_n_periods"],
    }
    ok = all(checks.values())
    out = {"meta": {"batch": "XSTOCK_SYNTH repro dzjy leg",
                    "convention": "p1d-verbatim (b_layer universe, 2010 slice,"
                                   " mask B_dzjy, shift 2)",
                    "tol_mean": REPRO_TOL_MEAN_R4, "tol_ir": REPRO_TOL_IR_R3,
                    "elapsed_s": round(time.time() - t0, 1)},
           "panel": meta, "grids": dz_meta,
           "rows": [{"factor": "dzjy_amt_share_20", "ok": bool(ok),
                     "reproduced_is_ic": bis["ic_mean"],
                     "recorded_is_ic": reg["h10_is_ic_mean"],
                     "reproduced_oos_ic": bos["ic_mean"],
                     "recorded_oos_ic": reg["h10_oos_ic_mean"],
                     "checks": {k: bool(v) for k, v in checks.items()}}],
           "pass": bool(ok)}
    if write:
        path = os.path.join(OUT_DIR, "xstock_repro_dzjy.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False, default=str)
        print(f"saved: {path}", flush=True)
    print(f"REPRO-DZJY {'PASS' if ok else 'FAIL'} "
          f"is_ic={bis['ic_mean']:.5f} vs {reg['h10_is_ic_mean']} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return out, bool(ok)


# ---------------------------------------------------------------- selftest

def run_selftest():
    """Offline logic gates; zero vendor/panel/network. Exit 0 iff all pass."""
    t0 = time.time()
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)

    # [1] shelf/population rule loader on the real recorded JSONs
    report, shelf, population, _ = build_shelf_and_population()
    check("shelf_rules_lhb", set(report["lhb_shelf"]) == EXPECTED["lhb_shelf"],
          f"lhb_shelf={report['lhb_shelf']}")
    check("shelf_rules_dzjy",
          set(report["dzjy_shelf"]) == EXPECTED["dzjy_shelf"],
          f"dzjy_shelf={report['dzjy_shelf']}")
    check("shelf_rules_gtja21",
          len(report["gtja_shelf"]) == EXPECTED["gtja_shelf_n"],
          f"gtja={len(report['gtja_shelf'])}")
    check("shelf_subset_of_population",
          report["shelf_is_subset_of_population"],
          f"shelf={report['shelf_n']} pop={report['population_n']}")
    check("population_gdhs_excluded",
          not any(n.startswith("gdhs_") for n in population),
          f"pop_n={report['population_n']}")

    # [2] era gate semantics (synthetic dates)
    dates = np.array([np.datetime64(d, "us").astype("int64") for d in
                      ("2006-12-29", "2007-01-04", "2009-12-31",
                       "2010-01-04", "2013-01-04")])
    m_lhb = era_mask(dates, "lhb")
    m_ext = era_mask(dates, "ext")
    check("era_gate_lhb", list(m_lhb) == [False, True, True, True, True],
          f"{list(m_lhb)}")
    check("era_gate_ext", list(m_ext) == [False, False, False, True, True],
          f"{list(m_ext)}")

    # [3] draw determinism + seed disjointness (prereg SS4)
    names = [f"m{i}" for i in range(30)]
    d1 = draw_indices(names, K_PRIMARY, SEED_NULLA)
    d2 = draw_indices(names, K_PRIMARY, SEED_NULLA)
    d3 = draw_indices(names, K_PRIMARY, SEED_NULLB)
    ok_det = np.array_equal(d1, d2)
    ok_disj = not np.array_equal(d1[:50], d3[:50])
    ok_rows = d1.shape == (N_NULLS, K_PRIMARY)
    ok_wo_repl = all(len(set(row)) == K_PRIMARY for row in d1[:200])
    check("draw_determinism", ok_det and ok_rows and ok_wo_repl,
          f"shape={d1.shape}")
    check("seed_disjointness", ok_disj)

    # [4] greedy clustering on synthetic IC series (prereg SS1 letter:
    #     |IS IC| descending, first cluster with corr>=0.5, else own family)
    rng = np.random.default_rng(7)
    base = rng.standard_normal(500)
    series = {
        "a": pd.Series(base),                       # strongest |IC| family head
        "a2": pd.Series(base * 0.9 + rng.standard_normal(500) * 0.1),
        "b": pd.Series(rng.standard_normal(500)),   # independent
    }
    ic_is = {"a": -0.08, "a2": -0.05, "b": 0.04}
    order = sorted(series, key=lambda n: (-abs(ic_is[n]), n))
    corr_cache = {}

    def corr_fn(x, y):
        key = (x, y)
        if key not in corr_cache:
            corr_cache[key] = series[x].corr(series[y])
        return corr_cache[key]

    reps, fams = greedy_cluster(order, corr_fn)
    ok_cluster = (len(reps) == 2 and set(fams.get("a", [])) >= {"a", "a2"}
                  and "b" in fams and fams.get("b") == ["b"])
    check("greedy_cluster", ok_cluster, f"reps={reps} fams={fams}")

    # [5] z/composite semantics via ps2_synth (XLIB construction precedent;
    #     MIN_Z_NAMES=5 per-date cross-section floor is library semantics)
    from ps2_synth import MIN_Z_NAMES, composite_z, z_rows
    vals = np.array([[1.0, 2.0, np.nan, 4.0, 3.0, 5.0],   # 5 valid -> z-able
                     [5.0, np.nan, np.nan, 9.0, 7.0, np.nan]])  # 4 -> floor NaN
    mask = np.isfinite(vals)
    z = z_rows(vals, mask)
    exp0 = np.array([1.0, 2.0, 4.0, 3.0, 5.0])          # row-0 valid values
    mu, sd = exp0.mean(), exp0.std()
    z0_exp = (exp0 - mu) / sd
    ok_z = (z.shape == vals.shape
            and np.isnan(z[1]).all()                    # MIN_Z_NAMES floor
            and np.isnan(z[0, 2])
            and np.allclose(z[0][[0, 1, 3, 4, 5]], z0_exp, atol=1e-9)
            and abs(z[0, 4]) < 1e-9)                    # value==mean -> z 0
    zc = composite_z([z, z * -1.0], 2)   # opposite pair cancels where valid
    ok_c = np.allclose(zc[0][[0, 1, 3, 4, 5]], 0.0) and np.isnan(zc[1]).all()
    mv = composite_z([z, np.full_like(z, np.nan)], 2)   # min_valid blocks
    ok_mv = bool(np.isnan(mv).all())
    check("z_rows_semantics", ok_z,
          f"MIN_Z_NAMES={MIN_Z_NAMES} z0={np.round(z[0], 3).tolist()}")
    check("composite_min_valid", ok_c and ok_mv)

    # [6] gates math letter (V1/V2/V3 + period gate, prereg SS4)
    def gates_letter(is_ic, is_ir, oos_ic, n_periods, thr):
        v1 = abs(is_ic) > max(V1_FLOOR, thr)
        v2 = abs(is_ir) >= V2_IR
        v3 = ((oos_ic > 0) == (is_ic > 0)
              and abs(oos_ic) >= V3_RETAIN * abs(is_ic))
        pg = n_periods >= MIN_PERIODS
        return bool(v1 and v2 and v3 and pg), (v1, v2, v3, pg)

    g_pass, flags = gates_letter(0.08, 0.5, 0.06, 2000, 0.05)
    g_fail1, f1 = gates_letter(0.06, 0.5, 0.06, 2000, 0.07)   # V1 vs nullA band
    g_fail2, f2 = gates_letter(0.08, 0.25, 0.06, 2000, 0.05)  # V2 IR wall
    g_fail3, f3 = gates_letter(0.08, 0.5, -0.04, 2000, 0.05)  # V3 sign flip
    g_fail4, f4 = gates_letter(0.08, 0.5, 0.06, 400, 0.05)    # period gate
    check("gates_letter", g_pass and not any([g_fail1, g_fail2, g_fail3,
                                              g_fail4]),
          f"flags={flags},{f1},{f2},{f3},{f4}")

    # [7] C2 key contract: cutoff_meta yields the evidence_cutoff string
    cm = cutoff_meta(CUTOFF.date())
    ok_cm = (isinstance(cm, dict) and cm.get("evidence_cutoff")
             == "2026-09-22")
    check("cutoff_meta_key", ok_cm, f"{cm}")

    # [8]-[11] streaming null engine (synthetic panel; offline, temp dir)
    import tempfile
    import shutil
    from ps2_synth import (composite_z, fwd_ret, ic_from_ranks, rank_rows,
                           z_rows)
    tmp = tempfile.mkdtemp(prefix="xstock_z_test_")
    try:
        rng = np.random.default_rng(11)
        T_full, N, n_is, h = 300, 60, 280, 10
        close = (np.cumprod(1 + 0.001 * rng.standard_normal((T_full, N)),
                            axis=0) * 10.0)
        close[0, 40:] = np.nan            # late-listed names
        close[150:160, 10:20] = np.nan    # suspension gap
        dates = (pd.bdate_range("2020-01-01", periods=T_full).values
                 .astype("datetime64[us]").astype("int64"))
        cal_is = dates[:n_is]
        fin_full = np.isfinite(close)

        # [8] z-cache roundtrip: write float32, read a block, byte equality
        z_probe = rng.standard_normal((T_full, N)).astype(np.float32)
        p8 = os.path.join(tmp, "roundtrip.npy")
        np.save(p8, z_probe)
        back = z_read_block(p8, 120, 40)
        ok_rt = (back.dtype == np.float64
                 and np.array_equal(back, z_probe[120:160].astype(np.float64)))
        check("z_cache_roundtrip", ok_rt, f"block={back.shape}")

        # synthetic members: mixed era patterns; z on close-finite mask
        names = [f"m{i}" for i in range(8)]
        files, z_full = [], {}
        for i, nm in enumerate(names):
            v = rng.standard_normal((T_full, N))
            if i % 2 == 0:
                v[:100] = np.nan          # era-like pre-window absence
            v[~fin_full] = np.nan
            z = z_rows(v, fin_full)
            z_full[i] = z
            rows = T_full if i < 4 else n_is    # shelf full-era vs pop IS-only
            p = os.path.join(tmp, nm + ".npy")
            np.save(p, z[:rows].astype(np.float32))
            files.append(p)

        # draws: 6 x K=3, min_valid=2 (draw 1 = sign-flip of draw 0)
        draws = np.array([[0, 1, 2], [0, 1, 2], [3, 4, 5],
                          [6, 7, 0], [1, 4, 7], [5, 6, 3]], dtype=np.int64)
        signs = np.array([[1, 1, 1], [-1, -1, -1], [1, -1, 1],
                          [1, 1, -1], [1, 1, 1], [-1, 1, 1]], dtype=np.float64)
        mv = 2

        # streaming (serial in-process: exercises the real task function)
        close_path = os.path.join(tmp, "close.npy")
        np.save(close_path, close)
        ic_m, smeta = streaming_null_pass(
            close_path, 0, N, cal_is, files, draws,
            signs, mv, h=h, parallel=False)

        # direct reference: full IS materialization, ps2-verbatim path
        fwd_is = fwd_ret(close, h)[:n_is]
        fin_is = fin_full[:n_is]
        worst = 0.0
        set_mismatch = 0
        for d in range(len(draws)):
            zs = [z_full[int(m)][:n_is] for m in draws[d]]
            zs = [z if signs[d, j] > 0 else -z
                  for j, z in enumerate(zs)]
            comp = composite_z(zs, mv)
            eff = fin_is & np.isfinite(comp) & np.isfinite(fwd_is)
            s_ref = ic_from_ranks(rank_rows(eff, comp),
                                  rank_rows(eff, fwd_is), cal_is)
            st = ic_m[d][np.isfinite(ic_m[d])]
            if len(s_ref) != len(st) or not np.allclose(
                    st, s_ref.values, atol=EQUIV_TOL_STREAM, rtol=0):
                set_mismatch += 1
            if len(s_ref):
                worst = max(worst, float(np.max(np.abs(st - s_ref.values)))
                            if len(st) == len(s_ref) else 9.9)
        check("stream_vs_direct_equiv", set_mismatch == 0
              and worst <= EQUIV_TOL_STREAM,
          f"worst|d|={worst:.2e} mismatches={set_mismatch} "
          f"blocks={smeta['blocks']}")

        # [10] tail-block fwd edge: last IS rows' IC uses fwd from beyond-IS
        # close rows (rows 270..279 -> close 280..289); assert the direct
        # reference produces tail values and streaming captured them
        tail_ts = pd.Timestamp(
            np.datetime64(int(cal_is[n_is - h - 1]), "us"))
        tail_ref_ok = True
        for d in (0, 2):
            zs = [z_full[int(m)][:n_is] * (1 if signs[d, j] > 0 else -1)
                  for j, m in enumerate(draws[d])]
            comp = composite_z(zs, mv)
            eff = fin_is & np.isfinite(comp) & np.isfinite(fwd_is)
            s_ref = ic_from_ranks(rank_rows(eff, comp),
                                  rank_rows(eff, fwd_is), cal_is)
            if len(s_ref[s_ref.index >= tail_ts]) == 0:
                tail_ref_ok = False
        st_tail = ic_m[0][n_is - h - 1:n_is]
        check("tail_block_fwd_edge", tail_ref_ok
              and np.isfinite(st_tail).sum() > 0,
          f"tail finite={int(np.isfinite(st_tail).sum())}/{len(st_tail)}")

        # [11] orientation symmetry: draw 1 (all signs flipped) = -draw 0
        d0 = ic_m[0][np.isfinite(ic_m[0])]
        d1 = ic_m[1][np.isfinite(ic_m[1])]
        ok_flip = (len(d0) == len(d1) and len(d0) > 0
                   and np.max(np.abs(d1 + d0)) <= 1e-12)
        check("orientation_symmetry", ok_flip,
              f"max|d1+d0|={np.max(np.abs(d1 + d0)):.2e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"SELFTEST {'PASS' if n_fail == 0 else 'FAIL'} "
          f"({len(results) - n_fail}/{len(results)}, "
          f"{time.time() - t0:.1f}s)", flush=True)
    return 0 if n_fail == 0 else 1


# -------------------------------------------------------------------- main

def run_batch():
    """Staged batch (population z-cache -> reproduction -> clustering ->
    primary -> streaming nulls -> gates). WQ finalize gate blocks execution
    until green; the block/null machinery and the LHB/dzjy repro legs are
    delivered and validated (r85) so the post-finalize run is mechanics."""
    print("run: staged execution pending WQ finalize gate (gates G1); "
          "machinery delivered r85 (streaming nulls + z-cache + repro "
          "legs) - see selftest / repro", flush=True)
    sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["gates", "run", "selftest", "repro"])
    ap.add_argument("--src", choices=["lhb", "dzjy"], default="lhb")
    args = ap.parse_args()
    if args.mode == "selftest":
        sys.exit(run_selftest())
    if args.mode == "repro":
        if args.src == "lhb":
            _, ok = repro_lhb()
        else:
            _, ok = repro_dzjy()
        sys.exit(0 if ok else 1)
    if args.mode == "run":
        run_batch()
    out, ok = run_gates()
    path = os.path.join(OUT_DIR, "xstock_synth_gates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {path}", flush=True)
    if not ok:
        print("GATES FAIL - run blocked (prereg discipline: no batch "
              "before all gates green)", flush=True)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
