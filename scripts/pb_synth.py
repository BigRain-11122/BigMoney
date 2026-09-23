"""P-B LHB x internal-factor small-K synthesis IC batch
(research/shortline/PB_SYNTH.md pre-reg, claim MSG-20260923-1937).

GM-session continuous-R&D lane (O-1819). Factor-layer synthesis: ZERO
engine runs -> strategy engine ledger N untouched; registers no traders
(IC != strategy; stock-pool strategy layer needs a stock cost model =
separate lane).

Recipe (frozen before run): 6-member equal-weight oriented-z composite =
2 LHB survivors (orientation constants from PA_LHB_IC SS6 records) +
4 J6-DNA internal factors computed by calling the engine.factors registry
on the stock panel (core48 -> stock-pool transfer test, orientation
constants from core48 records). Gates V1/V2/V3 h10 IS-segment strict,
dual nulls (nullA random-member synth from the 8-member shelf, nullB
white-noise composite), determinism anchor vs the PA batch records.

Panel slicing, LHB dedup/placement, event grids, rank/IC fast path are
copied verbatim from pa_lhb_ic.py (delivered batch stays frozen; no
refactor). Reproduction is enforced by the determinism anchor gate.

Outputs: research/shortline/pb_synth_results.csv
         results/shortline/pb_synth.json
"""
import glob
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from composite_ic import IS_END, ic_series, stats_block  # established methodology
from engine.factors import FACTORS  # delivered registry, called as-is (transfer test)

CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
PA_JSON = os.path.join(ROOT, "results", "shortline", "pa_lhb_ic.json")
RES_DIR = os.path.join(ROOT, "research", "shortline")
OUT_DIR = os.path.join(ROOT, "results", "shortline")

WIN_START = "2007-01-01"
H_GATE = 10            # sole gating horizon (pre-reg SS3)
H_REPORT = [5, 20]     # report-only, computed for passers only
N_NULLS = 50
SEED0 = 20260923
SEED_NULLA = 1000     # nullA offset (pre-reg SS3)
SEED_NULLB = 2000     # nullB offset (pre-reg SS3)
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
W_COUNT, W_NETBUY, W_SHARE, W_DECAY = 20, 60, 20, 252
MIN_Z_NAMES = 5       # cross-sectional z minimum valid names (composite_ic convention)
MIN_VALID = 3         # composite minimum valid members (pre-reg SS2)
SHELF_K = 6            # primary composite size
ANCHOR_TOL = 5e-5      # determinism anchor tolerance (CSV half-digit)
IS_END_TS = pd.Timestamp(IS_END)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400

# members: (name, orientation const, mask_key, kind)
MEMBERS = [
    ("lhb_count_20",    -1.0, "A", "lhb"),
    ("lhb_amt_share_20", 1.0, "B", "lhb"),
    ("vol_60",          -1.0, "A", "internal"),
    ("intraday_range",  -1.0, "A", "internal"),
    ("mom_12_1",         1.0, "A", "internal"),
    ("price_position",   1.0, "A", "internal"),
]
# nullA shelf = members + days_since (+1, PA SS6 record) + netbuy (+1, spec direction)
SHELF_EXTRA = [("lhb_days_since", 1.0, "C"), ("lhb_netbuy_amt_60", 1.0, "B")]


# ------------------------------------------------- copied verbatim from pa_lhb_ic.py
def rolling_sum(arr, w):
    """Trailing w-row sum; partial windows at panel start count what exists."""
    cs = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(arr, axis=0)])
    out = np.empty_like(arr)
    out[:w - 1] = cs[1:w]
    out[w - 1:] = cs[w:] - cs[:-w]
    return out


def shift1(a, fill=np.nan):
    """Event-time grid -> signal position: row t holds events <= t-1."""
    out = np.full_like(a, fill)
    out[1:] = a[:-1]
    return out


def rank_rows(eff, values):
    """Mask-first then rank (J7 pitfall family): average ties, NaN outside eff."""
    return pd.DataFrame(np.where(eff, values, np.nan)).rank(axis=1).values


def ic_from_ranks(F, R, dates):
    """Spearman IC per date from rank arrays with identical support."""
    with np.errstate(invalid="ignore"):
        fm = np.nanmean(F, axis=1)
        rm = np.nanmean(R, axis=1)
        dF = F - fm[:, None]
        dR = R - rm[:, None]
        cov = np.nansum(dF * dR, axis=1)
        sf = np.sqrt(np.nansum(dF * dF, axis=1))
        sr = np.sqrt(np.nansum(dR * dR, axis=1))
        ic = cov / (sf * sr)
    n = (np.isfinite(F) & np.isfinite(R)).sum(axis=1)
    ok = np.isfinite(ic) & (sf > 0) & (sr > 0) & (n >= 5)
    idx = pd.DatetimeIndex(dates[ok].astype("datetime64[us]"))
    return pd.Series(ic[ok], index=idx).dropna()


def fwd_ret(close, h):
    out = np.full_like(close, np.nan)
    out[:-h] = close[h:] / close[:-h] - 1.0
    return out


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


# ------------------------------------------------- batch-specific helpers
def z_rows(values, mask):
    """Per-date cross-sectional z on the mask support; <5 names or std=0 -> NaN."""
    v = np.where(mask & np.isfinite(values), values, np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        cnt = np.isfinite(v).sum(axis=1)
        mean = np.nanmean(v, axis=1)
        std = np.nanstd(v, axis=1)
    mean = np.where(cnt >= MIN_Z_NAMES, mean, np.nan)
    std = np.where(cnt >= MIN_Z_NAMES, std, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (v - mean[:, None]) / std[:, None]
    return z


def composite_z(z_list, min_valid):
    """Equal-weight mean of member z panels; rows with < min_valid finite -> NaN."""
    acc = None
    cnt = None
    for z in z_list:
        f = np.isfinite(z).astype(np.float64)
        v = np.where(f > 0, z, 0.0)
        acc = v if acc is None else acc + v
        cnt = f if cnt is None else cnt + f
    with np.errstate(invalid="ignore", divide="ignore"):
        comp = acc / cnt
    comp[cnt < min_valid] = np.nan
    return comp


def ic_of(values, mask, fwd, cal):
    """IC series of a factor/composite on mask & finite support."""
    eff = mask & np.isfinite(values) & np.isfinite(fwd)
    if not eff.any():
        return pd.Series(dtype=float)
    return ic_from_ranks(rank_rows(eff, values), rank_rows(eff, fwd), cal)


def row_of(role, name, mask, s, t1, gates=None, thr=None):
    blk_full, blk_is, blk_oos = seg_stats(s)
    rec = {"role": role, "name": name, "mask": mask,
           "compute_s": round(time.time() - t1, 1)}
    for seg, blk in [("full", blk_full), ("is", blk_is), ("oos", blk_oos)]:
        for k in ("ic_mean", "ic_ir", "n_periods"):
            rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
    if gates is not None:
        bis, bos = blk_is, blk_oos
        if "ic_mean" in bis and "ic_mean" in bos:
            v1 = abs(bis["ic_mean"]) > thr
            v2 = abs(bis["ic_ir"]) >= V2_IR
            v3 = ((bos["ic_mean"] > 0) == (bis["ic_mean"] > 0)
                  and abs(bos["ic_mean"]) >= V3_RETAIN * abs(bis["ic_mean"]))
            pg = bis.get("n_periods", 0) >= MIN_PERIODS
            rec.update({"v1_thr": round(float(thr), 4), "v1": bool(v1),
                        "v2": bool(v2), "v3": bool(v3),
                        "period_gate": bool(pg),
                        "pass": bool(v1 and v2 and v3 and pg)})
        else:
            rec.update({"v1_thr": thr, "v1": False, "v2": False,
                        "v3": False, "period_gate": False, "pass": False})
    return rec


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- panel slice (float32 memmap -> float64, dates int64 microseconds)
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(dates_all,
                             np.datetime64(WIN_START, "us").astype("int64")))
    cal = dates_all[i0:]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms = [os.path.basename(p)[:-8] for p in files]
    N = len(syms)
    sym_col = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                                mmap_mode="r")[i0:], dtype=np.float64)
    high = np.asarray(np.load(os.path.join(CACHE_DIR, "high.npy"),
                              mmap_mode="r")[i0:], dtype=np.float64)
    low = np.asarray(np.load(os.path.join(CACHE_DIR, "low.npy"),
                             mmap_mode="r")[i0:], dtype=np.float64)
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                 mmap_mode="r")[i0:], dtype=np.float64)
    print(f"panel slice: T={T} x N={N} ({time.time()-t0:.0f}s)", flush=True)

    # ---- LHB event grids (verbatim from pa_lhb_ic.py main)
    lhb = pd.read_parquet(LHB_PATH)
    n_raw = len(lhb)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    n_events = len(ev)
    ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["代码"].map(sym_col)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    r_idx, c_idx = pos[keep], cols.values[keep].astype(int)
    n_placed = int(keep.sum())
    print(f"events: raw={n_raw} dedup={n_events} placed={n_placed} "
          f"({time.time()-t0:.0f}s)", flush=True)

    ind = np.zeros((T, N))
    ind[r_idx, c_idx] = 1.0
    nb_grid = np.zeros((T, N))
    nb_grid[r_idx, c_idx] = ev["龙虎榜净买额"].values[keep]
    sh_grid = np.zeros((T, N))
    sh_grid[r_idx, c_idx] = ev["成交额占总成交比"].values[keep]

    count20 = rolling_sum(ind, W_COUNT)
    netbuy60 = rolling_sum(nb_grid, W_NETBUY)
    share20 = rolling_sum(sh_grid, W_SHARE)
    with np.errstate(invalid="ignore", divide="ignore"):
        amt_share20 = np.where(count20 > 0, share20 / count20, np.nan)
    ev_pos = np.where(ind > 0, np.arange(T)[:, None], -1.0)
    last_ev = np.maximum.accumulate(ev_pos, axis=0)
    days_since = np.arange(T)[:, None] - last_ev
    days_since[last_ev < 0] = np.nan
    days_capped = np.where(days_since <= W_DECAY, days_since, np.nan)

    count_s = shift1(count20, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        netbuy_s = shift1(netbuy60) / amount
    days_s = shift1(days_capped)
    share_s = shift1(amt_share20)

    A = np.isfinite(close) & np.isfinite(amount)
    B = A & (count_s >= 1)
    C = A & np.isfinite(days_s)
    masks = {"A": A, "B": B, "C": C}

    fwd10 = fwd_ret(close, H_GATE)

    # ---- gate 1: equivalence (probe = -60d momentum @ A, as P-A)
    print("equivalence gate: fast IC vs reference on probe factor...", flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(SEED0)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub].astype("datetime64[us]"))
    probe_df = pd.DataFrame(probe[sub], index=sub_idx)
    fwd_df = pd.DataFrame(fwd10[sub], index=sub_idx)
    ref = ic_series(probe_df, fwd_df)
    eff = A[sub] & np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    fast = ic_from_ranks(rank_rows(eff, probe[sub]),
                         rank_rows(eff, fwd10[sub]), cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    print(f"  n_ref={len(ref)} n_fast={len(fast)} common={len(common)} "
          f"max|diff|={worst:.2e}", flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- gate 2: composite recipe anchor (synthetic monotone panel -> IC=+1)
    sT, sN = 60, 30
    sdates = (pd.date_range("2000-01-01", periods=sT).values
              .astype("datetime64[us]").astype("int64"))
    sbase = np.tile(np.arange(sN, dtype=float), (sT, 1))
    smask = np.isfinite(sbase)
    sz = [z_rows(sbase, smask) for _ in range(SHELF_K)]
    scomp = composite_z(sz, MIN_VALID)
    sic = ic_of(scomp, smask, sbase, sdates)
    recipe_anchor = float(np.nanmean(sic.values)) if len(sic) else 9.9
    print(f"recipe anchor: mean IC={recipe_anchor:.6f}", flush=True)
    if abs(recipe_anchor - 1.0) > 1e-9 or len(sic) != sT:
        print("RECIPE ANCHOR FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- internal factors: call the delivered registry on the stock panel
    print("engine registry factors on stock panel (transfer test)...",
          flush=True)
    t1 = time.time()
    dates_idx = pd.DatetimeIndex(cal.astype("datetime64[us]"))
    d = {"close": pd.DataFrame(close, index=dates_idx, columns=syms),
         "high": pd.DataFrame(high, index=dates_idx, columns=syms),
         "low": pd.DataFrame(low, index=dates_idx, columns=syms)}
    internal = {"vol_60": FACTORS["vol_60"](d).values,
                "intraday_range": FACTORS["intraday_range"](d).values,
                "mom_12_1": FACTORS["mom_12_1"](d).values,
                "price_position": FACTORS["price_position"](d).values}
    d.clear()
    print(f"  4 registry factors computed ({time.time()-t1:.0f}s)", flush=True)

    # ---- member value panels
    values = {"lhb_count_20": count_s, "lhb_amt_share_20": share_s,
              "lhb_days_since": days_s, "lhb_netbuy_amt_60": netbuy_s}
    values.update(internal)

    # ---- oriented z panels (shelf: 6 members + 2 extras)
    z_panels, orientations = {}, {}
    for name, orient, mkey, *_ in (MEMBERS
                                   + [(n, o, m) for n, o, m in SHELF_EXTRA]):
        z_panels[name] = z_rows(values[name], masks[mkey]) * orient
        orientations[name] = orient
    shelf_names = [m[0] for m in MEMBERS] + [e[0] for e in SHELF_EXTRA]
    print(f"oriented z panels: {len(z_panels)} shelf members "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- member IC rows (transfer evidence) + determinism anchor gate
    member_rows = []
    for name, orient, mkey, kind in MEMBERS:
        t1 = time.time()
        s = ic_of(values[name], masks[mkey], fwd10, cal)
        member_rows.append(row_of("member", name, mkey, s, t1))
        bis = seg_stats(s)[1]
        print(f"  member {name}[{mkey}] is_ic={bis.get('ic_mean')} "
              f"ir={bis.get('ic_ir')}", flush=True)

    with open(PA_JSON, encoding="utf-8") as f:
        pa_rows = {r["factor"]: r for r in json.load(f)["rows"]
                   if r.get("status") == "ok"}
    anchors = {}
    for mname in ("lhb_count_20", "lhb_amt_share_20"):
        got = [r for r in member_rows if r["name"] == mname][0]
        ref_v = float(pa_rows[mname]["h10_is_ic_mean"])
        delta = abs(float(got["h10_is_ic_mean"]) - ref_v)
        anchors[mname] = {"this_batch": got["h10_is_ic_mean"],
                          "pa_record": pa_rows[mname]["h10_is_ic_mean"],
                          "abs_delta": round(delta, 8)}
    anchor_ok = all(a["abs_delta"] <= ANCHOR_TOL for a in anchors.values())
    print(f"determinism anchor: {anchors} ok={anchor_ok}", flush=True)
    if not anchor_ok:
        print("DETERMINISM ANCHOR FAIL - batch VOID (no numbers produced)")
        sys.exit(2)

    # ---- primary composite (K=6, min_valid=3)
    t1 = time.time()
    comp = composite_z([z_panels[m[0]] for m in MEMBERS], MIN_VALID)
    s_comp = ic_of(comp, A, fwd10, cal)
    primary_raw = row_of("primary", "pb_composite_6", "A", s_comp, t1)
    print(f"primary composite: is_ic={primary_raw.get('h10_is_ic_mean')} "
          f"ir={primary_raw.get('h10_is_ic_ir')} "
          f"({primary_raw['compute_s']}s)", flush=True)

    # ---- nullA: 50 random K=6 draws from the 8-member shelf
    print("nullA: 50 random-member composites...", flush=True)
    t1 = time.time()
    nulla_abs = []
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + SEED_NULLA + k)
        pick = rng.choice(len(shelf_names), size=SHELF_K, replace=False)
        zsel = [z_panels[shelf_names[i]] for i in pick]
        s = ic_of(composite_z(zsel, MIN_VALID), A, fwd10, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        if "ic_mean" in blk:
            nulla_abs.append(abs(blk["ic_mean"]))
        if (k + 1) % 10 == 0:
            print(f"  nullA {k+1}/{N_NULLS} ({time.time()-t1:.0f}s)",
                  flush=True)
    nulla_p95 = float(np.quantile(nulla_abs, 0.95)) if nulla_abs else 9.9
    print(f"  nullA p95|IS IC|={nulla_p95:.4f} ({time.time()-t1:.0f}s)",
          flush=True)

    # ---- nullB: 50 white-noise composites on the A support
    print("nullB: 50 white-noise composites...", flush=True)
    t1 = time.time()
    nullb_abs = []
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + SEED_NULLB + k)
        noise_z = []
        for _ in range(SHELF_K):
            nz = z_rows(rng.standard_normal((T, N)), A)
            nz *= rng.choice([-1.0, 1.0])
            noise_z.append(nz)
        s = ic_of(composite_z(noise_z, MIN_VALID), A, fwd10, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        if "ic_mean" in blk:
            nullb_abs.append(abs(blk["ic_mean"]))
        if (k + 1) % 10 == 0:
            print(f"  nullB {k+1}/{N_NULLS} ({time.time()-t1:.0f}s)",
                  flush=True)
    nullb_p95 = float(np.quantile(nullb_abs, 0.95)) if nullb_abs else 9.9
    print(f"  nullB p95|IS IC|={nullb_p95:.4f} ({time.time()-t1:.0f}s)",
          flush=True)

    if not nulla_abs or not nullb_abs:
        print("NULL ANCHOR FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- gates for the primary composite
    v1_thr = max(V1_FLOOR, nulla_p95, nullb_p95)
    primary = row_of("primary", "pb_composite_6", "A", s_comp, t1,
                     gates=True, thr=v1_thr)
    if primary["pass"]:
        for h in H_REPORT:
            fw = fwd_ret(close, h)
            sh_ = ic_of(comp, A, fw, cal)
            _, bis, bos = seg_stats(sh_)
            primary[f"h{h}_is_ic"] = bis.get("ic_mean", "")
            primary[f"h{h}_oos_ic"] = bos.get("ic_mean", "")
    print(f"gates: v1_thr={v1_thr:.4f} v1={primary['v1']} "
          f"v2={primary['v2']} v3={primary['v3']} "
          f"pass={primary['pass']}", flush=True)

    # ---- secondary report-only composites (non-gating, multiplicity disclosed)
    secondary_rows = []
    t1 = time.time()
    pair = composite_z([z_panels["lhb_count_20"],
                        z_panels["lhb_amt_share_20"]], 2)
    secondary_rows.append(row_of("secondary_report_only", "lhb_pair_2",
                                 "A", ic_of(pair, A, fwd10, cal), t1))
    t1 = time.time()
    int4 = composite_z([z_panels[m] for m in
                        ("vol_60", "intraday_range", "mom_12_1",
                         "price_position")], 2)
    secondary_rows.append(row_of("secondary_report_only", "internal_4",
                                 "A", ic_of(int4, A, fwd10, cal), t1))
    for r in secondary_rows:
        print(f"secondary {r['name']}: is_ic={r.get('h10_is_ic_mean')} "
              f"oos_ic={r.get('h10_oos_ic_mean')}", flush=True)

    # ---- outputs
    all_rows = member_rows + [primary] + secondary_rows
    df = pd.DataFrame(all_rows)
    df.to_csv(os.path.join(RES_DIR, "pb_synth_results.csv"), index=False,
              encoding="utf-8")
    n_ic = (len(MEMBERS) + 1 + len(secondary_rows) + 2 * N_NULLS
            + (len(H_REPORT) if primary["pass"] else 0))
    out = {
        "meta": {"batch": "P-B LHB x internal small-K synthesis",
                 "pre_reg": "research/shortline/PB_SYNTH.md",
                 "claim": "MSG-20260923-1937",
                 "order": "O-1819 continuous lane + CEO standing R&D directive",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "recipe": {"members": [m[0] for m in MEMBERS],
                            "orientations": {m[0]: m[1] for m in MEMBERS},
                            "orientation_source":
                                "PA_LHB_IC SS6 (LHB) / J6 core48 records (internal)",
                            "min_valid": MIN_VALID, "equal_weight": True,
                            "shelf_for_nullA": shelf_names},
                 "window": f"{WIN_START} -> cache cutoff",
                 "engine_runs": 0,
                 "ledger_note": "factor-layer synthesis: strategy engine "
                                "ledger N untouched (P-A precedent)"},
        "equivalence": {"max_abs_diff": worst, "n_common": int(len(common)),
                        "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "recipe_anchor": {"mean_ic": recipe_anchor, "pass":
                           abs(recipe_anchor - 1.0) <= 1e-9},
        "determinism_anchor": {"tol": ANCHOR_TOL, "detail": anchors,
                               "pass": anchor_ok},
        "thresholds": {"nullA_p95_abs_ic": round(nulla_p95, 4),
                       "nullB_p95_abs_ic": round(nullb_p95, 4),
                       "v1_thr": round(v1_thr, 4),
                       "v1_floor": V1_FLOOR},
        "rows": all_rows,
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "workers": 1,
                  "ic_computations": n_ic,
                  "cpu_cap_policy": "O-20260923-1738 (vectorized single-proc,"
                                    " memory-bound rank ops)"},
    }
    with open(os.path.join(OUT_DIR, "pb_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n=== P-B synthesis batch: primary pass={primary['pass']} "
          f"({time.time()-t0:.0f}s) ===", flush=True)


if __name__ == "__main__":
    main()
