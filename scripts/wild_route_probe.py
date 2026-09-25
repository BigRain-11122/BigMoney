"""T-57 s2 pre-freeze data-face probe (R99: probe facts only, zero strategy runs).

Writes results/wild_route/wild_route_probe.json -- the §2 evidence file for
research/WILD_ROUTE_PREREG_S1.md. Every number here is a DATA FACE FACT
(panel shapes/coverage/limit-cliff detection thresholds/regime-axis
computability), not a strategy result; frozen BEFORE the prereg freeze commit.

Faces probed (per WILD_ROUTE_LAB_S1_CARDS.md §一 frozen spec):
  census     P-1c Stage-A cache identity (r105 census-drift law: refuse regen)
  boards     board-type distribution + Beijing-exchange absence
  turnover   turnover field liveness (#5/#6 换手 legs feasibility)
  cliff      sealed limit-up return cliffs per board (detection thresholds)
  deepband   same cliff in f<1 qfq region (1995-2005 main board)
  zhaban     炸板 (touched-not-sealed) face + 炸板率 computability
  regime     emotion-cycle 3-axis (涨停数/炸板率/市场高度) daily computability
  listing    first-bar proxy (上市<365d exclusion face) + ok-set (bars>=250)
  eligibility ST snapshot coverage + 龙字辈 name enumeration (#11)
  gaps       internal NaN-gap semantics (suspension face, r179 listed-range law)
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS = os.path.join(ROOT, "Money02", "data", "bars")
OUT_DIR = os.path.join(ROOT, "results", "wild_route")
OUT = os.path.join(OUT_DIR, "wild_route_probe.json")

# frozen detection thresholds (candidate -> verified by cliff probe below)
MAIN_FLOOR = 0.0975      # main board sealed floor (cliff mass >=0.098)
WIDE_FLOOR = 0.1975      # ChiNext/STAR 20cm sealed floor (cliff mass >=0.199)
CN_20CM_FROM = "2020-08-24"   # ChiNext 20% regime start (pre: 10%)
STAR_FROM = "2019-07-22"      # STAR inception (20% since day one)

W_RECENT = ("2024-06-01", "2026-09-22")   # f=1 region cliff probe
W_DEEP = ("1995-01-01", "2005-12-31")     # f<1 region band-widening probe


def load(name):
    return np.load(os.path.join(CACHE, name + ".npy"), mmap_mode="r")


def main():
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
    meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
    T, N = len(idx), len(syms)
    rep = {"probe": "T-57 s2 wild-route data-face probe",
           "run_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
           "census": {
               "generated": meta.get("generated"),
               "shape": [T, N],
               "ok_universe_meta": meta.get("ok_universe"),
               "date_range": [str(idx[0].date()), str(idx[-1].date())],
               "census_drift_gate": (T == meta["shape"]["T"]
                                     and N == meta["shape"]["N"]
                                     and meta.get("ok_universe") == 5130),
           }}
    assert rep["census"]["census_drift_gate"], "r105 census drift: regenerated cache"

    # ---- boards ---------------------------------------------------------
    def board_of(s):
        if s.startswith("30"):
            return "chinext"
        if s.startswith("68"):
            return "star"
        if s[0] in "48":
            return "bse"
        return "main"
    boards = np.array([board_of(s) for s in syms])
    bd = {b: int((boards == b).sum()) for b in np.unique(boards)}
    rep["boards"] = {"dist": bd, "bse_absent": bd.get("bse", 0) == 0}

    # ---- turnover liveness ----------------------------------------------
    turn = load("turnover")
    rep["turnover"] = {
        "non_nan_frac": float(np.isfinite(turn).mean()),
        "verdict": "DEAD_FACE" if np.isfinite(turn).mean() < 0.01 else "alive",
        "encoding_law": "换手率阈值腿(#5 20-30%/#6>20%) 无数据面=缺席披露,"
                        "量能腿一律用 vol/amount 面替代",
    }

    # ---- price faces -----------------------------------------------------
    close = load("close"); high = load("high"); low = load("low")
    open_ = load("open"); vol = load("volume"); amt = load("amount")
    pct = load("pct_chg")
    r1 = np.asarray(pct, dtype=np.float64) / 100.0     # qfq day-over-day ret
    r1 = np.where(np.isfinite(r1), r1, np.nan)
    sealed = np.isfinite(r1) & (np.asarray(high) == np.asarray(close))

    def cliff(win, floor, hi, name):
        w0, w1 = (np.argmax(idx >= pd.Timestamp(win[0])),
                  int(np.argmax(idx > pd.Timestamp(win[1]))
                      or len(idx)))
        if w1 <= w0:
            w1 = len(idx)
        v = r1[w0:w1][sealed[w0:w1]]
        v = v[np.isfinite(v) & (v > floor - 0.015) & (v < hi)]
        hist, edges = np.histogram(v, bins=np.arange(floor - 0.015, hi, 0.001))
        inband = int((v >= floor).sum())
        below = int((v < floor).sum())
        return {"window": list(win), "n_band": int(len(v)), "n_in": inband,
                "n_below_floor": below,
                "capture": round(inband / max(1, inband + below), 5),
                "hist": {f"{e:.4f}": int(c) for e, c in zip(edges[:-1], hist)
                         if c}}

    main_cols = np.where(boards == "main")[0]
    cn_cols = np.where(boards == "chinext")[0]
    star_cols = np.where(boards == "star")[0]

    def cliff_cols(cols, win, floor, hi, name):
        w0 = int(np.argmax(idx >= pd.Timestamp(win[0])))
        w1 = int(np.argmax(idx > pd.Timestamp(win[1])) or len(idx))
        rr = r1[w0:w1][:, cols]
        ss = sealed[w0:w1][:, cols]
        v = rr[ss]
        v = v[np.isfinite(v) & (v > floor - 0.015) & (v < hi)]
        hist, edges = np.histogram(v, bins=np.arange(floor - 0.015, hi, 0.001))
        inb = int((v >= floor).sum()); below = int((v < floor).sum())
        return {"n_band": int(len(v)), "n_in": inb, "n_below_floor": below,
                "capture": round(inb / max(1, inb + below), 5),
                "hist": {f"{e:.4f}": int(c) for e, c in zip(edges[:-1], hist)
                         if c}}

    rep["cliff"] = {
        "recent_main": cliff_cols(main_cols, W_RECENT, MAIN_FLOOR, 0.105, "main"),
        "recent_chinext": cliff_cols(cn_cols, W_RECENT, WIDE_FLOOR, 0.21, "cn"),
        "recent_star": cliff_cols(star_cols, W_RECENT, WIDE_FLOOR, 0.21, "star"),
        "deep_main_1995_2005": cliff_cols(main_cols, W_DEEP, MAIN_FLOOR, 0.105, "deep"),
        "frozen_thresholds": {
            "main_floor": MAIN_FLOOR, "wide_floor": WIDE_FLOOR,
            "chinext_20cm_from": CN_20CM_FROM, "star_from": STAR_FROM,
            "sealed_def": "close==high (float-exact) AND qfq ret >= floor(board,date)",
        },
    }

    # ---- full-history sealed limit-up matrix (engine face, facts only) ----
    # floor per (date, board): main=0.0975; chinext=0.1975 only from
    # 2020-08-24 (else 0.0975); star=0.1975 since inception 2019-07-22.
    post_wide = np.asarray(idx >= pd.Timestamp(CN_20CM_FROM))
    star_era = np.asarray(idx >= pd.Timestamp(STAR_FROM))
    lim = np.zeros((T, N), dtype=bool)
    # main board
    rr = r1[:, main_cols]
    lim[:, main_cols] = np.isfinite(rr) & (rr >= MAIN_FLOOR) & sealed[:, main_cols]
    # chinext: date-aware floor
    rr = r1[:, cn_cols]
    fl_t = np.where(post_wide, WIDE_FLOOR, MAIN_FLOOR)[:, None]
    lim[:, cn_cols] = np.isfinite(rr) & (rr >= fl_t) & sealed[:, cn_cols]
    # star: wide floor only within star era (pre-inception rows are NaN anyway)
    rr = r1[:, star_cols]
    era = star_era[:, None]
    lim[:, star_cols] = (np.isfinite(rr) & (rr >= WIDE_FLOOR) & sealed[:, star_cols]
                         & era)

    # daily stats (regime axes computability + sanity vs public daily counts)
    daily_n = lim.sum(axis=1)
    recent = (idx >= pd.Timestamp("2024-06-01"))
    dn_recent = daily_n[recent]
    rep["sanity_daily_limitup"] = {
        "recent_daily_mean": round(float(dn_recent.mean()), 2),
        "recent_daily_median": float(np.median(dn_recent)),
        "recent_daily_p90": float(np.percentile(dn_recent, 90)),
        "note": "public reality main+20cm boards: typical 30-150/day; "
                "probe sanity band",
    }

    # ---- 炸板 face (touched-not-sealed) -----------------------------------
    cl = np.asarray(close, dtype=np.float64)
    hi = np.asarray(high, dtype=np.float64)
    prev_c = np.vstack([np.full((1, N), np.nan), cl[:-1]])
    with np.errstate(invalid="ignore"):
        touch = hi / prev_c - 1.0
    zh = np.isfinite(touch) & (touch >= MAIN_FLOOR) & ~sealed
    zr_recent = zh[:, main_cols].sum(axis=1)[recent]
    lim_recent = lim[:, main_cols].sum(axis=1)[recent]
    rep["zhaban"] = {
        "touched_not_sealed_def": "high/prev-1 >= floor AND NOT sealed",
        "recent_main_daily_zhaban_mean": round(float(zr_recent.mean()), 2),
        "recent_main_daily_limitup_mean": round(float(lim_recent.mean()), 2),
        "zhaban_rate_recent_mean": round(
            float(zr_recent.sum() / max(1, (zr_recent + lim_recent).sum())), 4),
    }

    # ---- regime 3-axis computability --------------------------------------
    # market height: consecutive limit-up run length per stock, daily max
    runs = np.zeros(N, dtype=np.int32)
    heights = np.zeros(T, dtype=np.int32)
    for t in range(T):
        runs = np.where(lim[t], runs + 1, 0)
        heights[t] = runs.max() if runs.size else 0
    rep["regime"] = {
        "axes": ["daily_limitup_count", "zhaban_rate", "market_max_height"],
        "all_daily_computable": True,
        "height_recent_median": int(np.median(heights[recent])),
        "height_recent_p90": int(np.percentile(heights[recent], 90)),
        "frozen_gates_ref": "CARDS §一 hiquant emotion-cycle table "
                            "(>80/<30涨停, <10/10-25/>25% 炸板率, >5/3-5/<3 高度)",
    }

    # ---- listing / ok-set face --------------------------------------------
    first_bar = np.full(N, -1, dtype=np.int64)
    for j in range(N):
        c = np.asarray(close[:, j])
        fin = np.flatnonzero(np.isfinite(c))
        if fin.size:
            first_bar[j] = int(fin[0])
    ok_mask = np.zeros(N, dtype=bool)
    for j in range(N):
        ok_mask[j] = np.isfinite(np.asarray(close[:, j])).sum() >= 250
    rep["listing"] = {
        "ok_set_recomputed": int(ok_mask.sum()),
        "matches_meta": int(ok_mask.sum()) == 5130,
        "short_history_excluded": int(N - ok_mask.sum()),
        "exclusion_law": "上市<365d proxy = bars>=250 (P-1c MIN_ROWS caliber)",
    }

    # ---- eligibility / names ------------------------------------------------
    import csv
    rows = list(csv.DictReader(open(os.path.join(
        ROOT, "data", "fundamental", "eligibility.csv"), encoding="utf-8-sig")))
    have = {r["code"] for r in rows}
    st = {r["code"] for r in rows if r.get("r2_st") == "True"}
    names = {r["code"]: (r.get("name") or "") for r in rows}
    rep["eligibility"] = {
        "rows": len(rows), "bars_syms_covered": f"{len([s for s in syms if s in have])}/{N}",
        "st_true_in_universe": int(len([s for s in syms if s in st])),
        "dragon_name_syms": int(len([s for s in syms if "龙" in names.get(s, "")])),
        "snapshot_mtime": pd.Timestamp(os.path.getmtime(os.path.join(
            ROOT, "data", "fundamental", "eligibility.csv")), unit="s",
            ).strftime("%Y-%m-%d %H:%M:%S") + " (point-in-time ST caveat: "
            "historical ST transitions unavailable in-repo -> static "
            "approximation disclosed in prereg)",
    }

    # ---- internal-gap / suspension semantics -------------------------------
    # within listed range: close finite but volume NaN (ffilled close, no trade)
    fin_c = np.isfinite(np.asarray(close))
    fin_v = np.isfinite(np.asarray(vol))
    susp = fin_c & ~fin_v          # price carried (ffill source) but no volume
    in_range = fin_c
    rep["gaps"] = {
        "internal_susp_rows": int((susp & in_range).sum()),
        "listed_bar_rows": int(in_range.sum()),
        "susp_frac_of_listed": round(float((susp & in_range).sum()
                                           / max(1, in_range.sum())), 5),
        "law": "suspension day = close finite & volume NaN -> T+1 open entry "
               "on susp day untradeable (entry rejected); exit on susp day "
               "rolls to next tradable open (prereg §3)",
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("probe written:", OUT)
    print("census gate:", rep["census"]["census_drift_gate"])
    print("cliff main capture:", rep["cliff"]["recent_main"]["capture"],
          "deep capture:", rep["cliff"]["deep_main_1995_2005"]["capture"])
    print("daily limit-up recent mean:", rep["sanity_daily_limitup"]["recent_daily_mean"])
    print("zhaban rate:", rep["zhaban"]["zhaban_rate_recent_mean"])
    print("ok set:", rep["listing"]["ok_set_recomputed"],
          "matches:", rep["listing"]["matches_meta"])
    print("regime height median/p90:", rep["regime"]["height_recent_median"],
          rep["regime"]["height_recent_p90"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
