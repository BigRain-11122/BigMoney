"""R299 bm-a CN_SECTOR_LEADER_P1 probe census (queue #4, R99 freeze-first leg-3).

FACTS ONLY -- zero strategy runs, zero returns accounting. Freezes the
engineering-frozen (EF) leader encoding and counts trigger events on the
P1C bars panel (Money02 read-only, WILD-S1/KLINE precedent, cutoff
2026-09-22) under the SW L2 point-in-time taxonomy from the official SW
2021 classification workbook (data/basic/sw_stock_classify_2021.xls).

Frozen EF encoding (candidate face for prereg; numbers may only be
referenced, not tuned, after this freeze):
  U_static  = bars ok_static & rows>=500 & last==cutoff & med(amount, own last20)>=30M
              (KLINE-identical per-file derive; 3106 expected)
  sector(t) = SW L2 (industry_code[:4]) active at t per official start_date history
  hot(t)    = L2 sectors with >=5 valid U_static members at t, EW 20d-ret ranked
              top K=3 AND EW 20d-ret > 0
  leader    = argmax member 20d-ret within hot sector
  trigger   = leader day d where close[d] is NOT at/near board limit
              (r1 = c[d]/c[d-1]-1 < floor(board, d) - 0.002)
"""
import glob
import json
import os
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
XLS = os.path.join(ROOT, "data", "basic", "sw_stock_classify_2021.xls")
OUT = os.path.join(ROOT, "results", "cn_sector_leader_probe.json")

CUTOFF = "2026-09-22"
MIN_ROWS = 500
MIN_AMT20 = 3e7
W = 20                 # EF: sector/leader lookback (trading days)
K_TOP = 3              # EF: hot-sector rank cap
MIN_SECT = 5           # EF: min valid members for a hot sector
LIMIT_EXCL_TOL = 0.002  # EF: close-face exclusion (WILD-S1 LIMIT_OPEN_TOL family)
MAIN_FLOOR, WIDE_FLOOR = 0.0975, 0.1975
CN_20CM_FROM = pd.Timestamp("2020-08-24")
STAR_FROM = pd.Timestamp("2019-07-22")

t0 = time.time()
meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
# r105 regeneration-refusing gate, constant = the ACTUAL frozen cache stamp
# (wild_route_lab.py asserts '2026-09-24 03:42:50' -- stale latent gate in a
# judged-closed runner, disclosed in round report; cross-check file below is
# this batch's own cache-vs-bars validation)
assert meta["generated"] == "2026-09-23 18:12:59", "census drift: cache regenerated"
xcc = json.load(open(os.path.join(ROOT, "results", "_r299bma_cache_crosscheck.json"),
                    encoding="utf-8"))
assert xcc["bars_files"] == 5222 and xcc["cache_last_date"] == CUTOFF
assert all(v.get("finite_mask_mismatches") == 0 for k, v in xcc.items()
           if isinstance(v, dict) and "finite_mask_mismatches" in v)
idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
assert str(idx[-1].date()) == CUTOFF, "panel end != cutoff"
close = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
amount = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
syms = [os.path.basename(p)[:-8] for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
assert len(syms) == meta["shape"]["N"] and len(idx) == meta["shape"]["T"], "cache shape drift"
T, N = len(idx), len(syms)
col = {s: j for j, s in enumerate(syms)}

# ---------- universe re-derive (KLINE-identical per-file method)
mask = pd.read_csv(MASK, dtype={"code": str})
ok = set(mask.loc[mask["ok_static"] == True, "code"])
u_cols = []
skip = {"not_ok": 0, "rows": 0, "last": 0, "liq": 0}
for p in sorted(glob.glob(os.path.join(BARS, "*.parquet"))):
    code = os.path.basename(p)[:-8]
    if code not in ok:
        skip["not_ok"] += 1
        continue
    df = pd.read_parquet(p, columns=["date", "amount"])
    if len(df) < MIN_ROWS:
        skip["rows"] += 1
        continue
    if str(df["date"].iloc[-1])[:10] != CUTOFF:
        skip["last"] += 1
        continue
    if float(np.median(df["amount"].values[-20:])) < MIN_AMT20:
        skip["liq"] += 1
        continue
    u_cols.append(col[code])
u_cols = np.array(sorted(u_cols), dtype=np.int64)
universe_n = len(u_cols)
in_u = np.zeros(N, dtype=bool)
in_u[u_cols] = True

# ---------- SW L2 point-in-time taxonomy (per-stock segments -> (T,N) int16)
clf = pd.read_excel(XLS, dtype={"股票代码": "str", "行业代码": "str"})
clf.columns = ["symbol", "start_date", "industry_code", "update_time"]
clf = clf[clf["symbol"].isin(set(syms))].sort_values(["symbol", "start_date"])
l2_codes = sorted(clf["industry_code"].str[:4].unique())
l2_id = {c: i + 1 for i, c in enumerate(l2_codes)}
n_l2 = len(l2_codes)
sect = np.zeros((T, N), dtype=np.int16)
unmapped_days = 0
for sym, g in clf.groupby("symbol"):
    j = col[sym]
    prev_sid = 0
    for sd, ic in zip(g["start_date"], g["industry_code"]):
        sd = pd.Timestamp(sd)
        p = int(np.searchsorted(idx, sd.to_pydatetime(), side="right") - 1)
        p = max(p, 0)
        sid = l2_id.get(ic[:4], 0)
        if sid != 0:
            sect[p:, j] = sid
            prev_sid = sid

# ---------- daily hot sectors + leaders + triggers
events = []            # (day_pos, col, sector_id)
limit_excluded = 0
hot_day_years = {}
ev_years = {}
per_day = {}
leader_counts = {}
unmapped_leader_skips = 0
for t in range(W + 1, T):
    c_now = np.asarray(close[t], dtype=np.float64)
    c_then = np.asarray(close[t - W], dtype=np.float64)
    c_prev = np.asarray(close[t - 1], dtype=np.float64)
    with np.errstate(invalid="ignore"):
        r20 = c_now / c_then - 1.0
        r1 = c_now / c_prev - 1.0
    srow = sect[t]
    valid = np.isfinite(r20) & np.isfinite(c_now) & np.isfinite(r1) & in_u & (srow > 0)
    cols_v = np.where(valid)[0]
    if cols_v.size == 0:
        continue
    sids = srow[cols_v]
    r20v = r20[cols_v]
    counts = np.bincount(sids, minlength=n_l2 + 1)
    sums = np.bincount(sids, weights=r20v, minlength=n_l2 + 1)
    with np.errstate(invalid="ignore"):
        ew = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)
    hot_ids = [s for s in range(1, n_l2 + 1) if counts[s] >= MIN_SECT and ew[s] > 0]
    if not hot_ids:
        continue
    yy = str(idx[t].year)
    hot_day_years[yy] = hot_day_years.get(yy, 0) + 1
    hot_rank = sorted(hot_ids, key=lambda s: -ew[s])[:K_TOP]
    for s in hot_rank:
        m = sids == s
        cand = cols_v[m]
        rv = r20v[m]
        j = int(np.argmax(rv))
        lead = int(cand[j])
        board_floor = WIDE_FLOOR if ((syms[lead].startswith("30") and idx[t] >= CN_20CM_FROM)
                                     or (syms[lead].startswith("68") and idx[t] >= STAR_FROM)) else MAIN_FLOOR
        if float(r1[lead]) >= board_floor - LIMIT_EXCL_TOL:
            limit_excluded += 1
            continue
        events.append((t, lead, int(s)))
        per_day[t] = per_day.get(t, 0) + 1
        ev_years[yy] = ev_years.get(yy, 0) + 1
        leader_counts[syms[lead]] = leader_counts.get(syms[lead], 0) + 1

# mapped-day burden (unmapped period faces)
mapped_any = (sect > 0) & in_u[:, None].T if False else None  # (skipped; disclosure via clf)
max_day = max(per_day.items(), key=lambda kv: kv[1]) if per_day else (None, 0)
sec_of_event = {}
for (t, j, s) in events:
    sec_of_event[l2_codes[s - 1]] = sec_of_event.get(l2_codes[s - 1], 0) + 1

meta_sw = json.load(open(os.path.join(ROOT, "results", "_r299bma_sw_clf_meta.json"), encoding="utf-8"))
res = {
    "batch": "CN_SECTOR_LEADER_P1",
    "kind": "pre-freeze probe, FACTS ONLY (R99: zero strategy runs)",
    "machine": "bm-a",
    "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    "panel": {"source": "Money02/data/bars + p1c cache (read-only, WILD-S1/KLINE precedent)",
               "files": N, "T": T, "cutoff": CUTOFF},
    "taxonomy": {
        "source": "official SW 2021 classification workbook (sw_stock_classify_2021.xls)",
        "sha256": meta_sw["sha256"], "fetched_at": meta_sw["ts"],
        "tls_disclosure": meta_sw["tls"],
        "granularity": "L2 = industry_code[:4]", "n_l2": n_l2,
        "point_in_time": True,
        "retrofit_disclosure": "SW 2021 standard applied retroactively pre-2021 (official published history); within-standard changes honored via start_date; unmapped pre-first-classification (stock,day) pairs excluded from sector stats",
    },
    "universe_filter": {"b_layer_ok_static": True, "rows_ge": MIN_ROWS, "last_eq_cutoff": True,
                         "med_amount_own_last20_ge_cny": MIN_AMT20},
    "universe_n": int(universe_n),
    "universe_skipped": skip,
    "EF_params": {"W": W, "K_TOP": K_TOP, "MIN_SECT": MIN_SECT,
                   "limit_excl_tol": LIMIT_EXCL_TOL,
                   "floors": {"main": MAIN_FLOOR, "wide": WIDE_FLOOR,
                                "cn_20cm_from": str(CN_20CM_FROM.date()),
                                "star_from": str(STAR_FROM.date())}},
    "census": {
        "trigger_events_n": len(events),
        "trigger_by_year": dict(sorted(ev_years.items())),
        "distinct_trigger_days": len(per_day),
        "max_events_one_day": int(max_day[1]),
        "max_day_date": str(idx[max_day[0]].date()) if max_day[0] is not None else None,
        "hot_sector_days_by_year": dict(sorted(hot_day_years.items())),
        "distinct_leaders": len(leader_counts),
        "leader_concentration_top10": dict(sorted(leader_counts.items(), key=lambda kv: -kv[1])[:10]),
        "limit_face_excluded_events": int(limit_excluded),
        "sector_concentration_top10": dict(sorted(sec_of_event.items(), key=lambda kv: -kv[1])[:10]),
        "first": str(idx[events[0][0]].date()) if events else None,
        "last": str(idx[events[-1][0]].date()) if events else None,
    },
    "elapsed_sec": round(time.time() - t0, 1),
}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("universe_n", "universe_skipped", "census", "EF_params", "elapsed_sec")},
                 ensure_ascii=False, indent=1)[:3200])
