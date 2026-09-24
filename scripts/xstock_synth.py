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
    grids. Returns (count_s, days_s, share_s, netbuy60_s, meta)."""
    from pa_lhb_ic import (LHB_PATH, W_COUNT, W_DECAY, W_NETBUY, W_SHARE,
                           rolling_sum, shift1)
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
    nb_grid = np.zeros((T, n_cols))
    nb_grid[r_idx, c_idx] = ev["龙虎榜净买额"].values[keep]
    count20 = rolling_sum(ind, W_COUNT)
    share20 = rolling_sum(sh_grid, W_SHARE)
    netbuy60 = rolling_sum(nb_grid, W_NETBUY)
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
            shift1(amt_share20), shift1(netbuy60), meta)


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
    count_s, days_s, share_s, _nb60, gmeta = _lhb_event_grids(cal, col_map, len(syms))
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

# ------------------------------------------------------- staged run (r88)
# run = stage1 build (resumable per-member z-cache + manifest checkpoint;
# backgroundable per r52 lane-age law) -> stage2 post (repro hard gate ->
# clustering -> primary/sensitivity -> streaming nulls with the real-cache
# equivalence gate BEFORE any null number -> V1/V2/V3 -> outputs).

IC_IS_DIR = os.path.join(Z_CACHE_DIR, "ic_is")
CLOSE_FFILL_NPY = os.path.join(Z_CACHE_DIR, "close_ffill.npy")
BUILD_LOCK = os.path.join(Z_CACHE_DIR, "build.lock")
FREE_RAM_MIN_GB = 5.5          # panels ~3.3GB + event grids transient
MAX_ATTEMPTS = 3


def _atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, default=str)
    os.replace(tmp, path)


def _load_manifest():
    if os.path.exists(Z_MANIFEST):
        try:
            with open(Z_MANIFEST, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"meta": {}, "members": {}}


def _record_table():
    """Recorded h10 IS/OOS IC per member (source-tagged). Prereg SS4 null
    orientation = these recorded signs (matched-null letter)."""
    rec = {}
    for r in _load(PA_JSON)["rows"]:
        rec[r["factor"]] = {"source": "pa",
                            "is_ic": r.get("h10_is_ic_mean"),
                            "oos_ic": r.get("h10_oos_ic_mean")}
    for r in _load(P1C_JSON)["rows"]:
        rec[r["factor"]] = {"source": "p1c",
                            "is_ic": r.get("h10_is_ic"),
                            "oos_ic": r.get("h10_oos_ic")}
    for r in _load(P1D_JSON)["rows"]:
        rec[r["factor"]] = {"source": "p1d",
                            "is_ic": r.get("h10_is_ic_mean"),
                            "oos_ic": r.get("h10_oos_ic_mean")}
    return rec


def _recorded_sign(entry, fallback_ic):
    v = entry.get("is_ic") if entry else None
    if isinstance(v, (int, float)) and np.isfinite(v):
        return 1.0 if v >= 0 else -1.0
    if isinstance(fallback_ic, (int, float)) and np.isfinite(fallback_ic):
        return 1.0 if fallback_ic >= 0 else -1.0
    return 1.0


def _try_lock():
    """Single-instance build lock (PID liveness via psutil; stale = take)."""
    os.makedirs(Z_CACHE_DIR, exist_ok=True)
    if os.path.exists(BUILD_LOCK):
        alive = False
        try:
            with open(BUILD_LOCK) as f:
                pid = int((f.read() or "0").strip() or 0)
            if pid:
                import psutil
                alive = psutil.pid_exists(pid)
        except Exception:
            alive = False
        if alive:
            return False
    with open(BUILD_LOCK, "w") as f:
        f.write(str(os.getpid()))
    return True


def _event_member_grids(panels, syms, cal_us):
    """Era-gated event-member factor grids on the unified p1c grid
    (prereg SS3: within-era 0-fill, pre-era NaN). p1d math verbatim;
    LHB core = _lhb_event_grids (PA2-verbatim) + netbuy (PA2-verbatim)."""
    import p1d_ext_slots_ic as p1d
    T, N = len(cal_us), len(syms)
    col_map = {s: i for i, s in enumerate(syms)}
    grids, meta = {}, {}

    count_s, days_s, share_s, nb60_s, gmeta = _lhb_event_grids(
        cal_us, col_map, N)
    pre_lhb = cal_us < LHB_ERA
    for g in (count_s, days_s, share_s, nb60_s):
        g[pre_lhb] = np.nan
    grids["lhb_count_20"] = count_s
    grids["lhb_days_since"] = days_s
    grids["lhb_amt_share_20"] = share_s
    amt_vals = panels["amount"].values
    with np.errstate(invalid="ignore", divide="ignore"):
        grids["lhb_netbuy_amt_60"] = nb60_s / amt_vals
    meta["lhb"] = gmeta
    del nb60_s

    amt0 = np.nan_to_num(amt_vals)
    ind, amtg, premw, deepg, dz_meta = p1d.build_dzjy(
        cal_us, col_map, T, N, lambda m: print("  " + m, flush=True))
    amt20 = p1d.rolling_sum(amt0, p1d.W_DZJY)
    cnt20 = p1d.rolling_sum(ind, p1d.W_DZJY)
    prem_sum = p1d.rolling_sum(premw, p1d.W_DZJY)
    deep5 = p1d.rolling_sum(deepg, p1d.W_DEEP)
    with np.errstate(invalid="ignore", divide="ignore"):
        share20 = np.where(amt20 > 0,
                           p1d.rolling_sum(amtg, p1d.W_DZJY) / amt20, np.nan)
        prem20 = np.where(cnt20 > 0, prem_sum / cnt20, np.nan)
    grids["dzjy_count_20"] = p1d.shift_n(cnt20, p1d.DZJY_SHIFT, 0.0)
    grids["dzjy_deep_disc_5"] = p1d.shift_n(deep5, p1d.DZJY_SHIFT, 0.0)
    grids["dzjy_amt_share_20"] = p1d.shift_n(share20, p1d.DZJY_SHIFT)
    grids["dzjy_prem_mean_20"] = p1d.shift_n(prem20, p1d.DZJY_SHIFT)
    meta["dzjy"] = dz_meta
    del ind, amtg, premw, deepg, amt20, cnt20, prem_sum, deep5, share20, prem20

    mg, mg_meta = p1d.build_margin(
        cal_us, col_map, T, N, lambda m: print("  " + m, flush=True))
    with np.errstate(invalid="ignore", divide="ignore"):
        bal_ratio = mg["bal"] / p1d.shift_n(mg["bal"], p1d.W_BAL)
        grids["margin_bal_chg_20"] = p1d.shift_n(
            np.log(bal_ratio), p1d.MARGIN_SHIFT)
        buy5 = p1d.rolling_sum(np.nan_to_num(mg["buy"]), p1d.W_BUY)
        amt5 = p1d.rolling_sum(amt0, p1d.W_BUY)
        grids["margin_buy_int_5"] = p1d.shift_n(
            np.where(amt5 > 0, buy5 / amt5, np.nan), p1d.MARGIN_SHIFT)
        ss20 = p1d.rolling_sum(np.nan_to_num(mg["ssell"]), p1d.W_SHORT)
        sb20 = p1d.rolling_sum(np.nan_to_num(mg["sbal"]), p1d.W_SHORT)
        grids["margin_short_int_20"] = p1d.shift_n(
            np.where(sb20 > 0, ss20 / sb20, np.nan), p1d.MARGIN_SHIFT)
    meta["margin"] = mg_meta
    del mg, bal_ratio, buy5, amt5, ss20, sb20, amt0

    pre_ext = cal_us < EXT_ERA
    for n in ("dzjy_count_20", "dzjy_deep_disc_5", "dzjy_amt_share_20",
              "dzjy_prem_mean_20", "margin_buy_int_5", "margin_bal_chg_20",
              "margin_short_int_20"):
        grids[n][pre_ext] = np.nan
    return grids, meta


def _vendor_context(panels):
    """Lazy GTJA191 module + WQ101 engine on the unified panels (p1c
    glue reused: load_alpha191_bigpanel / _wq_engine; zero rebuild)."""
    ctx = {}

    def gtja():
        if "gtja" not in ctx:
            from p1c_stock_ic_batch import load_alpha191_bigpanel
            ctx["gtja"] = load_alpha191_bigpanel()
        return ctx["gtja"]

    def wq():
        if "wq" not in ctx:
            from p1c_stock_ic_batch import _wq_engine
            ctx["wq"] = _wq_engine(panels)
        return ctx["wq"]

    return gtja, wq


def _compute_member(name, panels, grids, gtja, wq):
    """(T,N) float64 values on the unified grid (vendor hygiene: object
    dtype -> to_numeric, XLIB precedent)."""
    if name in grids:
        return grids[name]
    if name.startswith("alpha191_"):
        out = getattr(gtja(), name)(dict(panels))
        arr = out.values if isinstance(out, pd.DataFrame) else np.asarray(out)
    elif name.startswith("wq101_alpha"):
        n = int(name.replace("wq101_alpha", ""))
        out = getattr(wq(), f"alpha{n:03d}")()
        arr = (out.values if isinstance(out, pd.DataFrame)
               else np.asarray(out))
    else:
        raise KeyError(f"unknown member family: {name}")
    if arr.dtype == object:
        arr = pd.DataFrame(arr).apply(pd.to_numeric,
                                      errors="coerce").values
    return np.asarray(arr, dtype=np.float64)


def _run_build(report, shelf, population):
    """Stage 1: per-member z-cache build. Shelf -> full-era files; non-shelf
    population -> IS-prefix files (IS dates are a row-prefix; shared
    coordinates). Manifest = per-member checkpoint (atomic rewrite)."""
    if not _try_lock():
        print("build lock held by a live process - exiting (other build "
              "in flight, resume via next invocation)", flush=True)
        return "locked"
    try:
        import psutil
        free_gb = psutil.virtual_memory().available / 2**30
        if free_gb < FREE_RAM_MIN_GB:
            print(f"free RAM {free_gb:.1f}GB < {FREE_RAM_MIN_GB}GB floor - "
                  "honest exit (retry later round)", flush=True)
            return "ram_floor"
        from p1c_stock_ic_batch import load_panels, load_universe
        from shortline_p1_ic import _ic_series_fast
        from ps2_synth import z_rows
        from composite_ic import stats_block

        t0 = time.time()
        idx, syms, cmeta = load_universe()
        assert idx[-1] <= CUTOFF, (
            f"cache ends {idx[-1].date()} > evidence_cutoff "
            f"{CUTOFF.date()} - rebuild cache per its own convention first")
        T, N = len(idx), len(syms)
        cal_us = idx.values.astype("datetime64[us]").astype("int64")
        is_rows = int((idx <= IS_END_TS).sum())
        assert is_rows >= MIN_PERIODS, "IS segment too short"
        is_cal = cal_us[:is_rows]
        print(f"build: panel T={T} N={N} IS_rows={is_rows} "
              f"(cutoff {CUTOFF.date()})", flush=True)

        panels = load_panels(idx, syms)
        close = panels["close"]
        maskC = close.notna().values
        fwd10_df = close.shift(-H_GATE) / close - 1.0
        if not os.path.exists(CLOSE_FFILL_NPY):
            np.save(CLOSE_FFILL_NPY, close.values)   # float64, streaming
        os.makedirs(IC_IS_DIR, exist_ok=True)

        manifest = _load_manifest()
        members = manifest.setdefault("members", {})
        rec = _record_table()
        shelf_set = set(shelf)

        pending = [n for n in population
                   if (members.get(n) or {}).get("status") != "ok"]
        grids, gmeta = {}, {}
        if any(n.startswith(("lhb_", "dzjy_", "margin_")) for n in pending):
            print(f"event grids for pending event members "
                  f"({sum(1 for n in pending if n.startswith(('lhb_', 'dzjy_', 'margin_')))})...",
                  flush=True)
            grids, gmeta = _event_member_grids(panels, syms, cal_us)

        gtja, wq = _vendor_context(panels)
        t1 = time.time()
        n_done = 0
        for i, name in enumerate(population, 1):
            row = members.get(name) or {}
            if row.get("status") == "ok":
                continue
            if row.get("status") == "error" and \
                    row.get("attempts", 0) >= MAX_ATTEMPTS:
                continue
            row["attempts"] = row.get("attempts", 0) + 1
            tc = time.time()
            try:
                arr = _compute_member(name, panels, grids, gtja, wq)
                s = _ic_series_fast(
                    pd.DataFrame(arr, index=idx, columns=syms), fwd10_df)
                z = z_rows(arr, maskC).astype(np.float32)
                del arr
                rows = T if name in shelf_set else is_rows
                z_cache_write(name, z[:rows])
                del z
                s_is = s[s.index <= IS_END_TS]
                s_oos = s[s.index > IS_END_TS]
                blk_is, blk_oos = stats_block(s_is), stats_block(s_oos)
                ical = np.full(is_rows, np.nan)
                if len(s_is):
                    pos = np.searchsorted(
                        is_cal,
                        s_is.index.values.astype("datetime64[us]")
                        .astype("int64"))
                    ical[pos] = s_is.values
                np.save(os.path.join(IC_IS_DIR, name + ".npy"), ical)
                e = rec.get(name) or {}
                fic = blk_is.get("ic_mean")
                ric = e.get("is_ic")
                row.update({
                    "member": name, "status": "ok",
                    "kind": "shelf" if name in shelf_set else "pop",
                    "z_kind": "full" if name in shelf_set else "is",
                    "z_rows": rows,
                    "is_ic": fic, "is_ir": blk_is.get("ic_ir"),
                    "is_n": blk_is.get("n_periods", 0),
                    "oos_ic": blk_oos.get("ic_mean"),
                    "oos_ir": blk_oos.get("ic_ir"),
                    "oos_n": blk_oos.get("n_periods", 0),
                    "recorded_source": e.get("source"),
                    "recorded_is_ic": ric,
                    "delta_is": (abs(float(fic) - float(ric))
                                 if isinstance(ric, (int, float))
                                 and ric is not None and fic is not None
                                 else None),
                    "recorded_oos_ic": e.get("oos_ic"),
                    "sign": _recorded_sign(e, fic),
                    "compute_s": round(time.time() - tc, 2),
                })
            except Exception as ex:
                row["member"] = name
                row["status"] = "error"
                row["error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
                print(f"  ERROR {name}: {row['error']}", flush=True)
            members[name] = row
            _atomic_write_json(Z_MANIFEST, manifest)
            n_done += 1
            if n_done % 10 == 0:
                ok_n = sum(1 for r in members.values()
                           if r.get("status") == "ok")
                print(f"  {i}/{len(population)} ok={ok_n} "
                      f"({time.time() - t1:.0f}s)", flush=True)

        ok_n = sum(1 for r in members.values() if r.get("status") == "ok")
        err = sorted(n for n, r in members.items()
                     if r.get("status") == "error")
        complete = ok_n == len(population)
        manifest["meta"].update({
            "T": T, "N": N, "is_rows": is_rows,
            "cutoff": str(CUTOFF.date()), "is_end": str(IS_END_TS.date()),
            "grid": "p1c full-cache panel, close-ffill-finite mask; "
                    "ok_universe=5130 = cache build status (disclosed, "
                    "r84 adjudication)",
            "era_gates": {"lhb": "2007-01-01", "ext": "2010-01-01"},
            "event_grid_meta": gmeta,
            "built_at": time.strftime("%Y-%m-%d %H:%M"),
            "build_complete": bool(complete),
            "build_errors": err,
        })
        _atomic_write_json(Z_MANIFEST, manifest)
        print(f"build: {ok_n}/{len(population)} ok complete={complete} "
              f"errors={len(err)} ({time.time() - t0:.0f}s)", flush=True)
        return "complete" if complete else "incomplete"
    finally:
        try:
            os.remove(BUILD_LOCK)
        except OSError:
            pass


def _z_path(name):
    return os.path.join(Z_CACHE_DIR, name.replace("/", "_") + ".npy")


def _run_post(report, shelf, population):
    """Stage 2: repro hard gate -> clustering -> primary/sensitivity ->
    streaming nulls (real-cache equivalence BEFORE any null number) ->
    V1/V2/V3 -> JSON/CSV outputs. Deterministic; safe to re-run."""
    import hashlib
    import subprocess
    from ps2_synth import (composite_z, fwd_ret, ic_from_ranks, rank_rows)
    from composite_ic import stats_block
    from shortline_p1_ic import _ic_series_fast
    from xlib_synth import chain_head_total

    t0 = time.time()
    manifest = _load_manifest()
    members = manifest["members"]
    meta = manifest["meta"]
    T, N, is_rows = meta["T"], meta["N"], meta["is_rows"]
    from p1c_stock_ic_batch import load_universe
    idx, syms, _ = load_universe()
    assert len(idx) == T and len(syms) == N, "cache drifted vs manifest"
    cal_us = idx.values.astype("datetime64[us]").astype("int64")
    is_cal = cal_us[:is_rows]

    # ---- [1] hard reproduction gate (prereg SS2, before ANY number)
    #   GTJA/WQ shelf (32): recomputed IS IC vs p1c records <= 1e-4
    #   LHB/dzjy shelf (4): per-source legs re-run (PA2 / p1d conventions)
    bad = []
    for n in shelf:
        r = members.get(n) or {}
        if r.get("status") != "ok":
            bad.append([n, "missing_member"])
            continue
        if r.get("recorded_source") == "p1c":
            d = r.get("delta_is")
            if d is None or d > REPRO_TOL:
                bad.append([n, f"delta_is={d}"])
    out_lhb, ok_lhb = repro_lhb(write=False)
    out_dzjy, ok_dzjy = repro_dzjy(write=False)
    if not ok_lhb:
        bad.append(["lhb_leg", "repro_lhb FAIL"])
    if not ok_dzjy:
        bad.append(["dzjy_leg", "repro_dzjy FAIL"])
    p1c_deltas = [members[n].get("delta_is") for n in shelf
                  if (members.get(n) or {}).get("recorded_source") == "p1c"
                  and members[n].get("delta_is") is not None]
    repro_max = max(p1c_deltas) if p1c_deltas else None
    print(f"repro gate: p1c_shelf_max_delta={repro_max} "
          f"legs lhb={ok_lhb} dzjy={ok_dzjy} bad={bad}", flush=True)
    if bad:
        print("REPRODUCTION FAIL - batch VOID (no numbers produced)",
              flush=True)
        cm = cutoff_meta(CUTOFF.date())
        _atomic_write_json(os.path.join(OUT_DIR, "xstock_synth.json"), {
            "meta": {"batch": "XSTOCK_SYNTH", "verdict": "VOID",
                     "date": time.strftime("%Y-%m-%d %H:%M")},
            "repro_bad": bad, "evidence_cutoff": cm.get("evidence_cutoff")})
        return "void"

    # ---- [2] clustering (prereg SS1: IS IC-series corr, greedy |IS IC| desc)
    ic_series_is = {n: np.load(os.path.join(IC_IS_DIR, n + ".npy"))
                    for n in shelf}

    def corr_fn(a, b):
        x, y = ic_series_is[a], ic_series_is[b]
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() < MIN_OVERLAP:
            return np.nan
        return float(np.corrcoef(x[m], y[m])[0, 1])

    def sort_key(n):
        v = (members.get(n) or {}).get("is_ic")
        fin = isinstance(v, (int, float)) and np.isfinite(v)
        return (0 if fin else 1, -abs(v) if fin else 0.0, n)

    order = sorted(shelf, key=sort_key)
    reps, families = greedy_cluster(order, corr_fn, CLUSTER_CORR)
    top_reps = reps[:max(K_PRIMARY, max(k for k, _ in K_SENS))]
    tops = [(r, round(members[r]["is_ic"], 4), len(families[r]))
            for r in top_reps]
    print(f"clustering: {len(reps)} families; top reps={tops}", flush=True)

    # ---- [3] primary + sensitivity (sign-oriented ps2 path; XLIB convention)
    close_arr = np.asarray(np.load(CLOSE_FFILL_NPY, mmap_mode="r"),
                           dtype=np.float64)
    maskC = np.isfinite(close_arr)
    fwd10 = fwd_ret(close_arr, H_GATE)

    def load_z(name, rows):
        return np.asarray(np.load(_z_path(name), mmap_mode="r")[:rows],
                          dtype=np.float64)

    def comp_eval(names, min_valid, h):
        fwd = fwd10 if h == H_GATE else fwd_ret(close_arr, h)
        zs = [load_z(n, T) * members[n]["sign"] for n in names]
        comp = composite_z(zs, min_valid)
        del zs
        eff = maskC & np.isfinite(comp) & np.isfinite(fwd)
        s = ic_from_ranks(rank_rows(eff, comp), rank_rows(eff, fwd), cal_us)
        return s, comp

    def seg(s):
        return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
                stats_block(s[s.index > IS_END_TS]))

    s_prim, comp_prim = comp_eval(top_reps[:K_PRIMARY], MV_PRIMARY, H_GATE)
    b_full, b_is, b_oos = seg(s_prim)
    # pandas cross-check (XLIB convention) <= 1e-6 on the IS mean
    close_df = pd.DataFrame(close_arr, index=idx, columns=syms)
    s_pd = _ic_series_fast(pd.DataFrame(comp_prim, index=idx, columns=syms),
                           close_df.shift(-H_GATE) / close_df - 1.0)
    pd_is = stats_block(s_pd[s_pd.index <= IS_END_TS]).get("ic_mean")
    xcheck = (abs(float(b_is.get("ic_mean")) - float(pd_is))
              if pd_is is not None else None)
    print(f"primary: is_ic={b_is.get('ic_mean')} is_ir={b_is.get('ic_ir')} "
          f"oos_ic={b_oos.get('ic_mean')} pandas_xcheck={xcheck}",
          flush=True)
    if xcheck is None or xcheck > EQUIV_TOL_STREAM:
        print("PRIMARY PATH EQUIVALENCE FAIL - abort (no numbers)",
              flush=True)
        return "equiv_fail"

    sens_rows = []
    for k, mv in K_SENS:
        s_k, _ = comp_eval(top_reps[:k], mv, H_GATE)
        kf, ki, ko = seg(s_k)
        sens_rows.append({"k": k, "min_valid": mv,
                          "names": top_reps[:k],
                          "is_ic": ki.get("ic_mean"),
                          "is_ir": ki.get("ic_ir"),
                          "is_n": ki.get("n_periods", 0),
                          "oos_ic": ko.get("ic_mean"),
                          "oos_ir": ko.get("ic_ir"),
                          "oos_n": ko.get("n_periods", 0),
                          "full_ic": kf.get("ic_mean")})

    # ---- [4] nulls (streaming; real-cache equivalence BEFORE numbers)
    shelf_names, pop_names = list(shelf), list(population)
    filesA = [_z_path(n) for n in shelf_names]
    filesB = [_z_path(n) for n in pop_names]
    drawsA = draw_indices(shelf_names, K_PRIMARY, SEED_NULLA)
    drawsB = draw_indices(pop_names, K_PRIMARY, SEED_NULLB)
    signsA = np.array([[members[shelf_names[int(mi)]]["sign"]
                        for mi in row] for row in drawsA])
    signsB = np.array([[members[pop_names[int(mi)]]["sign"]
                        for mi in row] for row in drawsB])
    print(f"nullA streaming ({len(shelf_names)} shelf members)...",
          flush=True)
    t1 = time.time()
    icA, metaA = streaming_null_pass(CLOSE_FFILL_NPY, 0, N, is_cal,
                                     filesA, drawsA, signsA, MV_PRIMARY)
    # equivalence: draws 0/1 direct vs streaming (real cache, prereg gate)
    worst, mismatches = 0.0, 0
    for d in (0, 1):
        zs = [load_z(shelf_names[int(drawsA[d, j])], is_rows) * signsA[d, j]
              for j in range(K_PRIMARY)]
        comp = composite_z(zs, MV_PRIMARY)
        del zs
        eff = maskC[:is_rows] & np.isfinite(comp) & np.isfinite(
            fwd10[:is_rows])
        s_ref = ic_from_ranks(rank_rows(eff, comp),
                              rank_rows(eff, fwd10[:is_rows]), is_cal)
        ref = np.full(is_rows, np.nan)
        pos = np.searchsorted(
            is_cal, s_ref.index.values.astype("datetime64[us]")
            .astype("int64"))
        ref[pos] = s_ref.values
        mismatches += int((np.isfinite(icA[d]) ^ np.isfinite(ref)).sum())
        m = np.isfinite(icA[d]) & np.isfinite(ref)
        if m.any():
            worst = max(worst, float(
                np.abs(icA[d][m] - ref[m]).max()))
    print(f"  nullA equivalence: worst={worst:.2e} "
          f"mismatches={mismatches} ({time.time() - t1:.0f}s)", flush=True)
    if worst > EQUIV_TOL_STREAM or mismatches:
        print("STREAMING EQUIVALENCE FAIL - abort before null numbers",
              flush=True)
        return "equiv_fail"
    p95A, nA = null_abs_ic_p95(icA, 0, len(drawsA))
    del icA
    print(f"  nullA p95={p95A:.4f} (n={nA})", flush=True)
    print(f"nullB streaming ({len(pop_names)} population members)...",
          flush=True)
    t1 = time.time()
    icB, metaB = streaming_null_pass(CLOSE_FFILL_NPY, 0, N, is_cal,
                                     filesB, drawsB, signsB, MV_PRIMARY)
    p95B, nB = null_abs_ic_p95(icB, 0, len(drawsB))
    del icB
    print(f"  nullB p95={p95B:.4f} (n={nB}) ({time.time() - t1:.0f}s)",
          flush=True)

    # ---- [5] gates (prereg SS4, h10 primary judgement)
    is_ic = b_is.get("ic_mean")
    is_ir = b_is.get("ic_ir")
    oos_ic = b_oos.get("ic_mean")
    is_n = b_is.get("n_periods", 0)
    v1 = bool(abs(is_ic) > max(V1_FLOOR, p95A, p95B))
    v2 = bool(abs(is_ir) >= V2_IR)
    v3 = bool(np.sign(oos_ic) == np.sign(is_ic)
              and abs(oos_ic) >= V3_RETAIN * abs(is_ic))
    period_ok = bool(is_n >= MIN_PERIODS)
    passed = bool(v1 and v2 and v3 and period_ok)
    print(f"gates: V1={v1} V2={v2} V3={v3} period={period_ok} "
          f"PASS={passed}", flush=True)

    h20_row = None
    if v1:
        s20, _ = comp_eval(top_reps[:K_PRIMARY], MV_PRIMARY, 20)
        hf, hi, ho = seg(s20)
        h20_row = {"names": top_reps[:K_PRIMARY],
                   "is_ic": hi.get("ic_mean"), "is_ir": hi.get("ic_ir"),
                   "is_n": hi.get("n_periods", 0),
                   "oos_ic": ho.get("ic_mean"),
                   "oos_ir": ho.get("ic_ir"),
                   "full_ic": hf.get("ic_mean"),
                   "snooping_discount": True}

    # ---- [6] outputs (ledger gated on compute-audit CLEAN, prereg SS0)
    try:
        subprocess.run([sys.executable,
                        os.path.join(ROOT, "scripts", "compute_audit.py")],
                       capture_output=True, text=True, timeout=180)
        with open(os.path.join(ROOT, "results", "compute_audit.json"),
                  encoding="utf-8") as f:
            aj = json.load(f)
        latest = aj.get("history", aj)
        if isinstance(latest, list) and latest:
            latest = latest[-1]
        audit = {"verdict": latest.get("verdict"),
                 "flags": latest.get("flags"),
                 "asof": latest.get("ts") or latest.get("asof")}
    except Exception as ex:
        audit = {"verdict": "unavailable", "error": str(ex)[:120]}
    audit_clean = audit.get("verdict") == "CLEAN"

    added = 3 + 2 * N_NULLS + (1 if h20_row else 0)
    prev = chain_head_total()
    cm = cutoff_meta(CUTOFF.date())
    ledger = {"prev": prev,
              "added": added if audit_clean else 0,
              "total": prev + (added if audit_clean else 0),
              "audit_counted": bool(audit_clean),
              "note": "" if audit_clean else
              "audit not CLEAN - not counted per prereg SS0"}
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8") as f:
            machine_id = json.load(f).get("machine_id")
    except Exception:
        machine_id = "unknown"
    prereg_path = os.path.join(RES_DIR, "XSTOCK_SYNTH.md")
    with open(prereg_path, "rb") as f:
        prereg_sha = hashlib.sha256(f.read()).hexdigest()

    out = {
        "meta": {
            "batch": "XSTOCK_SYNTH (stock-pool cross-library small-K "
                     "synthesis)", "prereg": "research/shortline/"
                     "XSTOCK_SYNTH.md", "prereg_sha256": prereg_sha,
            "claim": "MSG-20260924-0905", "machine": machine_id,
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "elapsed_s": round(time.time() - t0, 1),
            "grid": meta.get("grid"), "era_gates": meta.get("era_gates"),
            "orientation": "recorded IS IC signs (prereg SS4); "
                           "recorded==recomputed for all shelf members "
                           "(repro gate <=1e-4)",
        },
        "shelf_report": report,
        "repro": {"p1c_shelf_max_delta_is": repro_max,
                  "leg_lhb_pass": bool(ok_lhb),
                  "leg_dzjy_pass": bool(ok_dzjy)},
        "clustering": {"n_families": len(reps), "rep_order": reps,
                       "families": families, "top_reps": top_reps},
        "primary": {"names": top_reps[:K_PRIMARY],
                    "k": K_PRIMARY, "min_valid": MV_PRIMARY,
                    "is_ic": is_ic, "is_ir": is_ir, "is_n": is_n,
                    "oos_ic": oos_ic,
                    "oos_ir": b_oos.get("ic_ir"),
                    "oos_n": b_oos.get("n_periods", 0),
                    "full_ic": b_full.get("ic_mean"),
                    "pandas_xcheck_is": xcheck},
        "sensitivity": sens_rows,
        "h20_report": h20_row,
        "nulls": {"nullA": {"p95_abs_is_ic": p95A, "n_draws": nA,
                            "seed": SEED_NULLA, **metaA},
                  "nullB": {"p95_abs_is_ic": p95B, "n_draws": nB,
                            "seed": SEED_NULLB, **metaB},
                  "equivalence_worst": worst,
                  "equivalence_mismatches": mismatches},
        "verdict": {"v1": v1, "v2": v2, "v3": v3,
                    "period_gate": period_ok, "pass": passed,
                    "lines": {"v1_floor": V1_FLOOR, "v2_ir": V2_IR,
                              "v3_retain": V3_RETAIN,
                              "nullA_p95": p95A, "nullB_p95": p95B,
                              "min_periods": MIN_PERIODS}},
        "trials_ledger": {**ledger, **cm},
        "evidence_cutoff": cm.get("evidence_cutoff"),
        "audit": audit,
    }
    jpath = os.path.join(OUT_DIR, "xstock_synth.json")
    _atomic_write_json(jpath, out)
    print(f"saved: {jpath}", flush=True)

    import csv
    cpath = os.path.join(RES_DIR, "xstock_synth_results.csv")
    with open(cpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row", "names", "k", "min_valid", "is_ic", "is_ir",
                    "is_n", "oos_ic", "oos_ir", "oos_n", "full_ic",
                    "note"])
        w.writerow(["primary", "+".join(top_reps[:K_PRIMARY]), K_PRIMARY,
                    MV_PRIMARY, is_ic, is_ir, is_n, oos_ic,
                    b_oos.get("ic_ir"), b_oos.get("n_periods", 0),
                    b_full.get("ic_mean"),
                    "PASS" if passed else
                    "FAIL " + ",".join(
                        k for k, v in (("V1", v1), ("V2", v2), ("V3", v3),
                                       ("period", period_ok)) if not v)])
        for r in sens_rows:
            w.writerow([f"sens_k{r['k']}", "+".join(r["names"]), r["k"],
                        r["min_valid"], r["is_ic"], r["is_ir"], r["is_n"],
                        r["oos_ic"], r["oos_ir"], r["oos_n"], r["full_ic"],
                        "report-only"])
        if h20_row:
            w.writerow(["h20_report", "+".join(h20_row["names"]), K_PRIMARY,
                        MV_PRIMARY, h20_row["is_ic"], h20_row["is_ir"],
                        h20_row["is_n"], h20_row["oos_ic"],
                        h20_row["oos_ir"], "", h20_row["full_ic"],
                        "snooping-discount report column"])
        w.writerow(["nullA_band", f"shelf {len(shelf_names)}", K_PRIMARY,
                    MV_PRIMARY, p95A, "", nA, "", "", "", "",
                    "p95 of 1000 oriented draws"])
        w.writerow(["nullB_band", f"pop {len(pop_names)}", K_PRIMARY,
                    MV_PRIMARY, p95B, "", nB, "", "", "", "",
                    "p95 of 1000 oriented draws"])
    print(f"saved: {cpath}", flush=True)
    print(f"[XSTOCK_SYNTH] post done verdict={'PASS' if passed else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return "done"


def run_batch(stage="auto"):
    """Staged run: build (resumable) -> post. Exit codes: 0 done / 2 hard
    fail (gates, repro VOID, equivalence) / 3 build incomplete."""
    t0 = time.time()
    print("[XSTOCK_SYNTH] staged run (prereg frozen pre-WQ finalize; "
          "claim MSG-20260924-0905)", flush=True)
    gates_out, ok = run_gates()
    if not ok:
        print("GATES FAIL - run blocked (prereg discipline)", flush=True)
        return 2
    report, shelf, population, _ = build_shelf_and_population()
    manifest = _load_manifest()
    complete = bool(manifest.get("meta", {}).get("build_complete")) and all(
        (manifest["members"].get(n) or {}).get("status") == "ok"
        for n in population)
    if stage in ("auto", "build") and not complete:
        status = _run_build(report, shelf, population)
        if status != "complete":
            print(f"build status={status} - post deferred (resumable)",
                  flush=True)
            return 3 if status == "incomplete" else 2
        complete = True
    if stage == "build":
        print(f"build-only complete ({time.time() - t0:.0f}s)", flush=True)
        return 0
    if not complete:
        print("build incomplete - post blocked (run `run` to finish build)",
              flush=True)
        return 3
    status = _run_post(report, shelf, population)
    return 0 if status == "done" else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["gates", "run", "selftest", "repro"])
    ap.add_argument("--src", choices=["lhb", "dzjy"], default="lhb")
    ap.add_argument("--stage", choices=["auto", "build", "post"],
                    default="auto")
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
        sys.exit(run_batch(stage=args.stage))
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
