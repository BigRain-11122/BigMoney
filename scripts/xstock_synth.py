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
  run      staged batch; NOT YET IMPLEMENTED (exit 3; WQ gate blocks anyway)

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

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"SELFTEST {'PASS' if n_fail == 0 else 'FAIL'} "
          f"({len(results) - n_fail}/{len(results)}, "
          f"{time.time() - t0:.1f}s)", flush=True)
    return 0 if n_fail == 0 else 1


# -------------------------------------------------------------------- main

def run_batch():
    """Staged batch (population z-cache -> reproduction -> clustering ->
    primary -> streaming nulls -> gates). Implementation lands in the next
    rounds; WQ finalize gate blocks execution regardless today."""
    print("run: NOT YET IMPLEMENTED (staged implementation in progress; "
          "WQ finalize gate must be green first - see gates)", flush=True)
    sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["gates", "run", "selftest"])
    args = ap.parse_args()
    if args.mode == "selftest":
        sys.exit(run_selftest())
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
