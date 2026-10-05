# -*- coding: utf-8 -*-
"""SINA_MF_IC_P1 pre-freeze probe (coverage/structure facts ONLY).

R99 law note: this probe runs BEFORE the prereg freeze commit by design --
it is a data-coverage probe (pre-freeze probe-facts, PREREG_TEMPLATE S2 /
W14 freeze-banner precedent), NOT a result inspection: zero IC computation,
zero factor-vs-return correlation, zero gated-stat faces. It measures panel
breadth, mask widths, window arithmetic, and D6 material availability so the
prereg can freeze the width gate / period gates / weak-check declarations
honestly. The batch RUNNER touches the real panel only after the freeze
commit.

Faces probed:
  1. p1c_stock cache anchors (T/N/cutoff/dates.npy unit) -- G-ANCHOR quadruple
  2. sina panel breadth (files, rows, tail-after-cutoff, selfcheck aggregate)
  3. validity-mask cross-section widths for the 5 frozen-candidate cells
     (small_share d1/d5/d10/d20 + retail_group d5, shift1 T+1 convention)
  4. eligible-day counts + IS/OOS positional split under candidate width
     gates {300, 500, 1000}
  5. D6 material availability (ths_ggzjl daily coverage, lhb parquet window)
  6. warmup first-decidable dates per cell
"""
import glob
import json
import os
import sys
import datetime as _dt

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS = os.path.join(ROOT, "Money02", "data", "bars")
SINA_DIR = os.path.join(ROOT, "data", "sina_mf", "per")
THS_DIR = os.path.join(ROOT, "data", "ths_ggzjl", "daily")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT = os.path.join(ROOT, "results", "_r719bma_sina_mf_ic_p1_probe.json")

FACTOR_COLS = ["opendate", "ratioamount", "r0", "r1", "r2", "r3",
               "r0_net", "r1_net", "r2_net", "r3_net", "netamount"]
SELFCHK_TOL = 1e-3
H_GATE = 10


def main():
    doc = {"probe": "SINA_MF_IC_P1 pre-freeze coverage probe (no IC faces)"}

    # ---- 1. p1c cache anchors
    dates = np.load(os.path.join(CACHE, "dates.npy"))
    close_mm = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
    all_str = [_dt.datetime.fromtimestamp(int(d) / 1e6).strftime("%Y-%m-%d")
               for d in dates]
    doc["p1c_cache"] = {
        "path": "Money02/data/cache/p1c_stock (dates.npy us-epoch + close.npy memmap)",
        "load_fn": "np.load dates/close + bars parquet roster (census lineage)",
        "T": int(len(dates)), "N_bars": len(syms),
        "close_shape": list(close_mm.shape),
        "first": all_str[0], "last": all_str[-1],
        "dates_npy_unit": "microseconds since epoch (r717 pinned law)",
        "cutoff": all_str[-1],
    }

    # ---- 2. sina panel breadth + selfcheck (single pass, census loader law)
    symset = set(syms)
    rows = n_files = n_read_err = 0
    chk_ok = chk_n = 0
    earliest = None
    tail_after_cutoff = 0
    per_small = {}   # code -> Series(small_share validity values)
    per_retail = {}  # code -> Series(retail_group validity values)
    sina_only = 0
    for path in sorted(glob.glob(os.path.join(SINA_DIR, "*.csv"))):
        code = os.path.basename(path)[:-4]
        n_files += 1
        if code not in symset:
            sina_only += 1
            continue
        try:
            df = pd.read_csv(path, usecols=FACTOR_COLS)
        except Exception:
            n_read_err += 1
            continue
        rows += len(df)
        na = pd.to_numeric(df["netamount"], errors="coerce").to_numpy(float)
        tot = (df["r0_net"].to_numpy(float) + df["r1_net"].to_numpy(float)
               + df["r2_net"].to_numpy(float) + df["r3_net"].to_numpy(float))
        d = np.abs(na - tot)
        scale = np.maximum(np.abs(tot), 1.0)
        fin = np.isfinite(d) & np.isfinite(tot)
        chk_ok += int((d[fin] <= SELFCHK_TOL * scale[fin]).sum())
        chk_n += int(fin.sum())
        idx = df["opendate"].astype(str).to_numpy()
        if earliest is None:
            earliest = str(idx.min())
        elif str(idx.min()) < earliest:
            earliest = str(idx.min())
        tail_after_cutoff += int((pd.Series(idx) > all_str[-1]).sum())
        # factor faces (values -> validity only downstream; construction law
        # = census _factor_frames: shares of same-row tier buy sum)
        r0 = df["r0"].to_numpy(float); r1 = df["r1"].to_numpy(float)
        r2 = df["r2"].to_numpy(float); r3 = df["r3"].to_numpy(float)
        n0 = df["r0_net"].to_numpy(float); n1 = df["r1_net"].to_numpy(float)
        n2 = df["r2_net"].to_numpy(float); n3 = df["r3_net"].to_numpy(float)
        buy = r0 + r1 + r2 + r3
        ok = np.isfinite(buy) & (buy > 0) & np.isfinite(n3)
        small = np.where(ok, n3 / np.where(ok, buy, np.nan), np.nan)
        okr = ok & np.isfinite(n2)
        retail = np.where(okr, (n2 + n3) / np.where(okr, buy, np.nan), np.nan)
        per_small[code] = pd.Series(small, index=idx)
        per_retail[code] = pd.Series(retail, index=idx)
    doc["sina_panel"] = {
        "files": n_files, "sina_only_structural_exclusions": sina_only,
        "panel_rows_read": rows, "read_errors": n_read_err,
        "earliest_opendate": earliest,
        "rows_after_p1c_cutoff_unconsumable": tail_after_cutoff,
        "selfcheck_rows_within_1e-3": chk_ok, "selfcheck_rows_total": chk_n,
    }

    # ---- 3. window + mask widths per candidate cell
    ws = next(i for i, s in enumerate(all_str) if s >= earliest)
    win_str = all_str[ws:]
    cutoff_i = len(all_str) - 1
    close = np.asarray(close_mm[ws:], dtype=np.float64)
    close_df = pd.DataFrame(close, index=pd.Index(win_str), columns=syms)
    fwd10 = close_df.shift(-H_GATE) / close_df - 1.0
    del close_df, close

    small_df = pd.DataFrame(per_small)
    small_df.index = pd.Index(small_df.index.astype(str), name="date")
    small_df = small_df.reindex(win_str)
    retail_df = pd.DataFrame(per_retail)
    retail_df.index = pd.Index(retail_df.index.astype(str), name="date")
    retail_df = retail_df.reindex(win_str)

    cells = {}
    for name, base, w, mp in [
        ("small_share_d1", small_df, 1, 1),
        ("small_share_d5", small_df, 5, 3),
        ("small_share_d10", small_df, 10, 6),
        ("small_share_d20", small_df, 20, 12),
        ("retail_group_d5", retail_df, 5, 3),
    ]:
        fac = base if w == 1 else base.rolling(w, min_periods=mp).mean()
        # shift1 T+1 strict lag (family law): panel row at d -> signal at d+1
        fac = fac.shift(1)
        m = fac.notna() & fwd10.notna()
        cnt = m.sum(axis=1)
        ok_days = cnt[cnt > 0]
        first_dec = None
        nz = np.where(cnt.values > 0)[0]
        if len(nz):
            first_dec = win_str[nz[0]]
        cells[name] = {
            "min_periods": mp, "window": w,
            "width_min": int(cnt.min()) if len(cnt) else 0,
            "width_median": float(np.median(cnt)) if len(cnt) else 0.0,
            "width_p25": float(np.quantile(cnt, 0.25)) if len(cnt) else 0.0,
            "width_p75": float(np.quantile(cnt, 0.75)) if len(cnt) else 0.0,
            "first_decidable": first_dec,
            "eligible_days_gte300": int((cnt >= 300).sum()),
            "eligible_days_gte500": int((cnt >= 500).sum()),
            "eligible_days_gte1000": int((cnt >= 1000).sum()),
        }
    doc["cells_coverage"] = cells

    # ---- 4. positional split arithmetic on the primary cell (small_share_d5)
    fac = small_df.rolling(5, min_periods=3).mean().shift(1)
    m = fac.notna() & fwd10.notna()
    for gate in (300, 500, 1000):
        elig = m.sum(axis=1) >= gate
        n = int(elig.sum())
        is_n = n * 2 // 3
        doc[f"split_gate{gate}"] = {
            "eligible_days": n, "is_days": is_n, "oos_days": n - is_n,
            "period_gates_is100_oos30": bool(is_n >= 100 and n - is_n >= 30),
        }

    # ---- 5. D6 material availability
    ths_fps = sorted(glob.glob(os.path.join(THS_DIR, "*.csv")))
    ths_days = [os.path.basename(f)[:-4] for f in ths_fps]
    ths_in_win = [d for d in ths_days if win_str[0] <= d <= win_str[-1]]
    doc["d6_material"] = {
        "ths_files": len(ths_fps),
        "ths_first": ths_days[0] if ths_days else None,
        "ths_last": ths_days[-1] if ths_days else None,
        "ths_days_in_eval_window": len(ths_in_win),
        "ths_weak_check_expected": len(ths_in_win) < 30,
        "lhb_parquet_exists": os.path.exists(LHB_PATH),
    }
    if os.path.exists(LHB_PATH):
        lhb = pd.read_parquet(LHB_PATH)
        evd = pd.to_datetime(lhb["上榜日"])
        in_win = ((evd >= pd.Timestamp(win_str[0]))
                  & (evd <= pd.Timestamp(win_str[-1]))).sum()
        doc["d6_material"]["lhb_events_in_window"] = int(in_win)
        doc["d6_material"]["lhb_first"] = str(evd.min().date())
        doc["d6_material"]["lhb_last"] = str(evd.max().date())

    doc["generated"] = _dt.datetime.now().isoformat(timespec="seconds")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1)[:4000])
    print("probe written", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
