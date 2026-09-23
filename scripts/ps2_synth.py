"""P-S v2: lhb_pair promotion batch (PS2_SYNTH.md pre-reg, claim
MSG-20260923-2012). Second look at the P-S material family with the
multiplicity declared up front: the pair (count_20 -1, amt_share_20 +1,
min_valid 2) was the strongest REPORT-ONLY column in P-S v1; this batch
gates it as the primary against an exhaustive 28-pair null (all C(8,2)
oriented pairs from the same 8-member shelf, primary included = same
bias, same scale, P-2 precedent) plus a 50-draw K=2 white-noise null.

Factor-layer IC batch: ZERO engine runs -> strategy engine ledger N
untouched. Helpers and panel construction copied verbatim from
pb_synth.py (delivered batch stays frozen); reproduction enforced by the
determinism anchor vs the v1 lhb_pair_2 record (tol 5e-5).

Outputs: research/shortline/ps2_synth_results.csv
         results/shortline/ps2_synth.json
"""
import glob
import itertools
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
from engine.factors import FACTORS  # delivered registry, called as-is

CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
V1_JSON = os.path.join(ROOT, "results", "shortline", "pb_synth.json")
RES_DIR = os.path.join(ROOT, "research", "shortline")
OUT_DIR = os.path.join(ROOT, "results", "shortline")

WIN_START = "2007-01-01"
H_GATE = 10
H_REPORT = [5, 20]
N_NULLB = 50
SEED0 = 20260923
SEED_NULLB = 3000          # fresh draw family (v1 used 2000)
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
W_COUNT, W_NETBUY, W_SHARE, W_DECAY = 20, 60, 20, 252
MIN_Z_NAMES = 5
ANCHOR_TOL = 5e-5
IS_END_TS = pd.Timestamp(IS_END)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400

SHELF = ["lhb_count_20", "lhb_days_since", "lhb_amt_share_20",
         "lhb_netbuy_amt_60", "vol_60", "intraday_range", "mom_12_1",
         "price_position"]
PRIMARY = ("lhb_count_20", "lhb_amt_share_20")
ORIENT = {"lhb_count_20": -1.0, "lhb_days_since": 1.0,
          "lhb_amt_share_20": 1.0, "lhb_netbuy_amt_60": 1.0,
          "vol_60": -1.0, "intraday_range": -1.0, "mom_12_1": 1.0,
          "price_position": 1.0}

warnings.filterwarnings("ignore")


# ------------------------------------------------- copied verbatim from pb_synth.py
def rolling_sum(arr, w):
    cs = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(arr, axis=0)])
    out = np.empty_like(arr)
    out[:w - 1] = cs[1:w]
    out[w - 1:] = cs[w:] - cs[:-w]
    return out


def shift1(a, fill=np.nan):
    out = np.full_like(a, fill)
    out[1:] = a[:-1]
    return out


def rank_rows(eff, values):
    return pd.DataFrame(np.where(eff, values, np.nan)).rank(axis=1).values


def ic_from_ranks(F, R, dates):
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


def z_rows(values, mask):
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
    eff = mask & np.isfinite(values) & np.isfinite(fwd)
    if not eff.any():
        return pd.Series(dtype=float)
    return ic_from_ranks(rank_rows(eff, values), rank_rows(eff, fwd), cal)


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- panel (verbatim from pb_synth.py main)
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

    lhb = pd.read_parquet(LHB_PATH)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["代码"].map(sym_col)
    keep = pos_ok & cols.notna().values
    r_idx, c_idx = pos[keep], cols.values[keep].astype(int)

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

    # ---- gate 1: equivalence
    print("equivalence gate...", flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(SEED0)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub].astype("datetime64[us]"))
    ref = ic_series(pd.DataFrame(probe[sub], index=sub_idx),
                    pd.DataFrame(fwd10[sub], index=sub_idx))
    eff = A[sub] & np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    fast = ic_from_ranks(rank_rows(eff, probe[sub]),
                         rank_rows(eff, fwd10[sub]), cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    print(f"  max|diff|={worst:.2e}", flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - abort (no numbers produced)")
        sys.exit(1)

    # ---- oriented z shelf (8 members, v1 constants)
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
    print(f"registry factors ({time.time()-t1:.0f}s)", flush=True)
    values = {"lhb_count_20": count_s, "lhb_amt_share_20": share_s,
              "lhb_days_since": days_s, "lhb_netbuy_amt_60": netbuy_s}
    values.update(internal)
    mask_of = {"lhb_count_20": "A", "lhb_amt_share_20": "B",
               "lhb_days_since": "C", "lhb_netbuy_amt_60": "B",
               "vol_60": "A", "intraday_range": "A", "mom_12_1": "A",
               "price_position": "A"}
    z_panels = {n: z_rows(values[n], masks[mask_of[n]]) * ORIENT[n]
                for n in SHELF}

    # ---- primary pair
    t1 = time.time()
    comp = composite_z([z_panels[PRIMARY[0]], z_panels[PRIMARY[1]]], 2)
    s_comp = ic_of(comp, A, fwd10, cal)
    _, bis, bos = seg_stats(s_comp)
    print(f"primary pair: is_ic={bis.get('ic_mean')} "
          f"ir={bis.get('ic_ir')} ({time.time()-t1:.0f}s)", flush=True)

    # ---- gate 3: determinism anchor vs v1 record
    with open(V1_JSON, encoding="utf-8") as f:
        v1 = json.load(f)
    v1_pair = [r for r in v1["rows"]
               if r.get("name") == "lhb_pair_2"][0]
    anchor = {"is_ic": {"v1": v1_pair["h10_is_ic_mean"],
                        "v2": bis.get("ic_mean"),
                        "delta": abs(float(bis.get("ic_mean", 9))
                                     - float(v1_pair["h10_is_ic_mean"]))},
              "is_ir": {"v1": v1_pair["h10_is_ic_ir"],
                        "v2": bis.get("ic_ir"),
                        "delta": abs(float(bis.get("ic_ir", 9))
                                     - float(v1_pair["h10_is_ic_ir"]))},
              "oos_ic": {"v1": v1_pair["h10_oos_ic_mean"],
                         "v2": bos.get("ic_mean"),
                         "delta": abs(float(bos.get("ic_mean", 9))
                                      - float(v1_pair["h10_oos_ic_mean"]))}}
    anchor_ok = all(a["delta"] <= ANCHOR_TOL for a in anchor.values())
    print(f"determinism anchor: {anchor} ok={anchor_ok}", flush=True)
    if not anchor_ok:
        print("DETERMINISM ANCHOR FAIL - batch VOID (no numbers produced)")
        sys.exit(2)

    # ---- nullA: exhaustive 28 oriented pairs
    print("nullA: exhaustive C(8,2)=28 shelf pairs...", flush=True)
    t1 = time.time()
    nulla = []
    primary_is_ic = None
    for (a, b) in itertools.combinations(SHELF, 2):
        s = ic_of(composite_z([z_panels[a], z_panels[b]], 2), A, fwd10, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        icv = abs(blk["ic_mean"]) if "ic_mean" in blk else np.nan
        if (a, b) == PRIMARY:
            primary_is_ic = icv
        nulla.append({"pair": f"{a}+{b}", "abs_is_ic": icv,
                      "is_primary": (a, b) == PRIMARY})
    nulla_p95 = float(np.nanquantile([n["abs_is_ic"] for n in nulla], 0.95))
    rank = sorted(nulla, key=lambda n: -n["abs_is_ic"])
    primary_rank = [i for i, n in enumerate(rank)
                    if n["is_primary"]][0] + 1
    print(f"  nullA p95={nulla_p95:.4f} primary rank={primary_rank}/28 "
          f"({time.time()-t1:.0f}s)", flush=True)

    # ---- nullB: 50 K=2 noise pairs
    print("nullB: 50 noise pairs...", flush=True)
    t1 = time.time()
    nullb_abs = []
    for k in range(N_NULLB):
        rng = np.random.default_rng(SEED0 + SEED_NULLB + k)
        noise_z = []
        for _ in range(2):
            nz = z_rows(rng.standard_normal((T, N)), A)
            nz *= rng.choice([-1.0, 1.0])
            noise_z.append(nz)
        s = ic_of(composite_z(noise_z, 2), A, fwd10, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        if "ic_mean" in blk:
            nullb_abs.append(abs(blk["ic_mean"]))
    nullb_p95 = float(np.quantile(nullb_abs, 0.95)) if nullb_abs else 9.9
    print(f"  nullB p95={nullb_p95:.4f} ({time.time()-t1:.0f}s)", flush=True)

    # ---- gates
    v1_thr = max(V1_FLOOR, nulla_p95, nullb_p95)
    rec = {"role": "primary", "name": "lhb_pair_2", "mask": "A"}
    for seg, blk in [("full", seg_stats(s_comp)[0]), ("is", bis),
                     ("oos", bos)]:
        for k in ("ic_mean", "ic_ir", "n_periods"):
            rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
    v1g = abs(bis["ic_mean"]) > v1_thr
    v2 = abs(bis["ic_ir"]) >= V2_IR
    v3 = ((bos["ic_mean"] > 0) == (bis["ic_mean"] > 0)
          and abs(bos["ic_mean"]) >= V3_RETAIN * abs(bis["ic_mean"]))
    pg = bis.get("n_periods", 0) >= MIN_PERIODS
    rec.update({"v1_thr": round(v1_thr, 4), "v1": bool(v1g), "v2": bool(v2),
                "v3": bool(v3), "period_gate": bool(pg),
                "pass": bool(v1g and v2 and v3 and pg)})
    if rec["pass"]:
        for h in H_REPORT:
            fw = fwd_ret(close, h)
            sh_ = ic_of(comp, A, fw, cal)
            _, b2is, b2os = seg_stats(sh_)
            rec[f"h{h}_is_ic"] = b2is.get("ic_mean", "")
            rec[f"h{h}_oos_ic"] = b2os.get("ic_mean", "")
    print(f"gates: thr={v1_thr:.4f} v1={v1g} v2={v2} v3={v3} "
          f"pass={rec['pass']}", flush=True)

    # ---- outputs
    df = pd.DataFrame([rec] + [{"role": "nullA", "name": n["pair"],
                                "mask": "A", "abs_is_ic": n["abs_is_ic"],
                                "is_primary": n["is_primary"]}
                               for n in nulla])
    df.to_csv(os.path.join(RES_DIR, "ps2_synth_results.csv"), index=False,
              encoding="utf-8")
    n_ic = 1 + len(nulla) + N_NULLB + (len(H_REPORT) if rec["pass"] else 0)
    out = {
        "meta": {"batch": "P-S v2 lhb_pair promotion",
                 "pre_reg": "research/shortline/PS2_SYNTH.md",
                 "claim": "MSG-20260923-2012",
                 "multiplicity": "family second look, declared; nullA "
                                 "exhaustive 28 pairs includes primary "
                                 "(same bias, same scale)",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "engine_runs": 0,
                 "ledger_note": "factor layer: engine ledger N untouched"},
        "equivalence": {"max_abs_diff": worst, "pass": worst <= EQUIV_TOL},
        "determinism_anchor": {"tol": ANCHOR_TOL, "detail": anchor,
                               "pass": anchor_ok},
        "thresholds": {"nullA_p95": round(nulla_p95, 4),
                       "nullB_p95": round(nullb_p95, 4),
                       "v1_thr": round(v1_thr, 4),
                       "primary_rank_of_28": primary_rank},
        "nullA_pairs": nulla,
        "primary": rec,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "ic_computations": n_ic, "workers": 1,
                  "cpu_cap_policy": "O-20260923-1738"},
    }
    with open(os.path.join(OUT_DIR, "ps2_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n=== P-S v2: primary pass={rec['pass']} "
          f"rank={primary_rank}/28 ({time.time()-t0:.0f}s) ===", flush=True)


if __name__ == "__main__":
    main()
