"""FUND-VALUE-P1 ignition-gate probes (data side, fail-closed, zero-network).

Three legs per research/FUND-VALUE-P1.md §2 (data-completeness gate):
  leg1  price panel gate (universe/canonical loader via p1c_stock_ic_batch)
  leg2  value-face TRANSFER landing + export gate:
        n_symbols >= 5100 AND per-symbol anchor median >= 550
        AND anchor_date coverage 2001-01 .. 2026-09
        AND per-symbol zero duplicate dates AND monotonic ascending
  leg3  monthly joined DATA coverage + start census:
        - start census == 401 (monthly first-trading-day starts, window
          1992-09-01..2026-03-02, eligibility pos>=252 AND fwd>=126 AND
          active members >= 24; T-22 monthly enumeration spirit)
        - per start t: coverage = members with a non-null pe_ttm anchor at
          or before t (anchor_date <= t forward-fill, PIT law) over the
          active universe (raw close notna, no ffill) -- the (0,200]
          valuation band is a SELECTION eligibility, NOT data coverage,
          and is reported separately as eligibility_ratio
        - gate: from first-signal date t0 (first start with coverage
          >= 0.80) onward, every month must hold coverage >= 0.80; months
          below floor are whole-month skipped (never interpolated) and
          counted honestly -- gate requires zero below-floor months after
          t0 (fail-closed, per prereg "逐月覆盖率>=80%").

Output: results/_fund_value_p1_transfer_probe.json (probe facts only).
Exit 0 = all gates green; exit 2 = any gate red (no masking).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "scripts")
import numpy as np
import pandas as pd

import p1c_stock_ic_batch as P1C  # established harness: universe/panel loader (single source)

PARQUET = "data/fund_history_export/value_faces.parquet"
OUT = "results/_fund_value_p1_transfer_probe.json"
TZ = timezone(timedelta(hours=8))

PE_MIN, PE_MAX = 0.0, 200.0   # frozen valuation eligibility (§2, selection layer)
COV_FLOOR = 0.80              # monthly data-coverage gate


def _now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def main() -> int:
    facts: dict = {"probe": "FUND-VALUE-P1 ignition data-side probes",
                   "generated": _now(), "machine": "bm-a"}
    gates: dict[str, bool] = {}

    # ---- leg1 price panel via canonical loader ----
    idx, syms, meta = P1C.load_universe()
    close_raw = np.load(f"{P1C.CACHE_DIR}/close.npy", mmap_mode="r")
    n_bars = len(idx)
    facts["panel"] = {"n_bars": n_bars, "n_syms_panel": len(syms),
                      "first": str(idx[0].date()), "last": str(idx[-1].date()),
                      "ok_universe": meta.get("ok_universe")}
    gates["leg1_price_panel"] = bool(
        n_bars == 8792 and str(idx[-1].date()) == "2026-09-22" and len(syms) >= 5100)

    # ---- leg2 TRANSFER landing + export gate ----
    df = pd.read_parquet(PARQUET)
    n_symbols = int(df["code"].nunique())
    anchor_counts = df.groupby("code")["anchor_date"].size()
    median_anchors = float(anchor_counts.median())
    date_min = str(df["anchor_date"].min()); date_max = str(df["anchor_date"].max())
    per = df.groupby("code")["anchor_date"]
    dup_any = bool(per.apply(lambda s: s.duplicated().any()).any())
    mono_all = bool(per.apply(lambda s: s.is_monotonic_increasing).all())
    sym_set = set(syms)
    facts["value_face"] = {
        "rows": int(len(df)), "n_symbols": n_symbols,
        "n_symbols_in_panel_universe": int(sum(1 for c in set(df["code"]) if c in sym_set)),
        "anchor_median": median_anchors, "anchor_p10": float(anchor_counts.quantile(0.10)),
        "date_min": date_min, "date_max": date_max,
        "dup_dates_any": dup_any, "monotonic_all": mono_all,
    }
    gates["leg2_transfer_export"] = bool(
        n_symbols >= 5100 and median_anchors >= 550
        and date_min[:7] <= "2001-01" and date_max[:7] >= "2026-09"
        and (not dup_any) and mono_all)

    # ---- leg3 monthly joined data coverage + census ----
    d = df.assign(_d=df["anchor_date"].astype("string").str.replace("-", "", regex=False).astype("int64"))
    by_sym: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, g in d.groupby("code", sort=False):
        g = g.sort_values("_d")
        by_sym[str(code)] = (g["_d"].to_numpy(), g["pe_ttm"].to_numpy())

    mask = (idx >= pd.Timestamp("1992-09-01")) & (idx <= pd.Timestamp("2026-03-02"))
    sub = idx[mask]; mk = sub.strftime("%Y-%m")
    month_first_pos: list[int] = []
    prev = None
    for p, k in zip(np.where(mask)[0], mk):
        if k != prev:
            month_first_pos.append(int(p)); prev = k

    # T-22 monthly eligibility: pos>=252, fwd>=126, active members >= 24
    starts: list[int] = []
    for p in month_first_pos:
        if p < 252 or (n_bars - 1 - p) < 126:
            continue
        if int((~np.isnan(close_raw[p])).sum()) < 24:
            continue
        starts.append(p)
    facts["start_census"] = {"months_in_window": len(month_first_pos),
                             "eligible_starts": len(starts),
                             "expected": 401}

    cov_rows = []
    for p in starts:
        t_date = int(idx[p].strftime("%Y%m%d"))
        act = np.where(~np.isnan(close_raw[p]))[0]
        n_active = int(act.size)
        n_cov = 0; n_elig = 0
        for j in act:
            pack = by_sym.get(syms[j])
            if pack is None:
                continue
            ad, pe = pack
            k = int(np.searchsorted(ad, t_date, side="right")) - 1
            if k >= 0 and not np.isnan(pe[k]):
                n_cov += 1
                if PE_MIN < pe[k] <= PE_MAX:
                    n_elig += 1
        cov_rows.append({"t": t_date, "n_active": n_active, "n_cov": n_cov,
                         "cov_ratio": round(n_cov / n_active, 4),
                         "elig_ratio": round(n_elig / n_active, 4)})

    ratios = [r["cov_ratio"] for r in cov_rows]
    t0 = next((r for r in cov_rows if r["cov_ratio"] >= COV_FLOOR), None)
    after = [r for r in cov_rows if t0 and r["t"] >= t0["t"]]
    below_after = [r["t"] for r in after if r["cov_ratio"] < COV_FLOOR]
    facts["coverage"] = {
        "first_signal_date_t0": t0["t"] if t0 else None,
        "months_evaluated": len(cov_rows),
        "months_below_floor_after_t0": below_after,
        "n_below_after_t0": len(below_after),
        "cov_median": float(np.median(ratios)) if ratios else None,
        "cov_min": float(np.min(ratios)) if ratios else None,
        "cov_min_after_t0": float(np.min([r["cov_ratio"] for r in after])) if after else None,
        "elig_ratio_median_after_t0": float(np.median([r["elig_ratio"] for r in after])) if after else None,
        "worst_five": sorted(cov_rows, key=lambda r: r["cov_ratio"])[:5],
    }
    gates["leg3_monthly_coverage"] = bool(
        len(starts) == 401 and t0 is not None and len(below_after) == 0)

    facts["gates"] = gates
    facts["verdict"] = "GREEN" if all(gates.values()) else "RED"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": facts["verdict"], "gates": gates,
                      "starts": len(starts), "t0": t0["t"] if t0 else None,
                      "n_below_after_t0": len(below_after),
                      "cov_min_after_t0": facts["coverage"]["cov_min_after_t0"]}, ensure_ascii=False))
    return 0 if facts["verdict"] == "GREEN" else 2


if __name__ == "__main__":
    sys.exit(main())
