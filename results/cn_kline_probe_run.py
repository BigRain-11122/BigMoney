# cn_kline_probe.py -- CN_KLINE_PATTERN_P1 pre-freeze probe (R99: FACTS ONLY, zero strategy runs)
# Universe derive + folklore 4-pattern event census on Money02/data/bars (read-only, WILD-S1 precedent).
# Encodings here = the exact frozen encodings the prereg will cite (DIGEST-20260927-kline-folklore
# canonical 4 families; engineering-frozen params explicitly marked EF).
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
OUT = os.path.join(ROOT, "results", "cn_kline_probe.json")
CUTOFF = "2026-09-22"           # D2 lockbox (Stage-A panel last bar)
MIN_ROWS = 500                  # >= ~2y history
MIN_AMT20 = 3e7                 # last-20-bar median daily turnover >= 30M CNY (current liquidity face)
HEAD_TOP = 0.3                  # EF: close in top 30% of range (guangtou)
BODY_RATIO = 2.0                # EF: max/min body <= 2.0 (dengchang)
RISE_5D = 1.05                  # EF: prior 5-day rise >= 5% (shengshi-hou context)
CROW_TOP = 0.3                  # EF: close in bottom 30% of range (near-day-low)
YANG_BODY_FRAC = 0.5           # EF: changyang body >= 50% of range

t0 = time.time()
mask = pd.read_csv(MASK)
ok = set(int(x) for x in mask.loc[mask["ok_static"] == True, "code"])
print(f"mask ok_static={len(ok)}/{len(mask)}")

years = {}
stocks_with_event = {k: set() for k in ("MS", "TWS", "DCC", "TBC")}
day_cross = {k: {} for k in ("MS", "TWS", "DCC", "TBC")}
stats = {k: {"n": 0, "per_year": {}, "max_day": 0, "max_day_date": None,
             "first": None, "last": None} for k in ("MS", "TWS", "DCC", "TBC")}
uni_n = 0
skip = {"not_ok": 0, "rows": 0, "last": 0, "liq": 0}
board_n = {}

files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
for pi, p in enumerate(files):
    code = int(os.path.basename(p)[:-8])
    if code not in ok:
        skip["not_ok"] += 1
        continue
    df = pd.read_parquet(p)
    if len(df) < MIN_ROWS or str(df["date"].iloc[-1])[:10] != CUTOFF:
        skip["rows" if len(df) < MIN_ROWS else "last"] += 1
        continue
    if float(np.median(df["amount"].values[-20:])) < MIN_AMT20:
        skip["liq"] += 1
        continue
    uni_n += 1
    b = mask.loc[mask["code"] == code, "board"].iloc[0]
    board_n[b] = board_n.get(b, 0) + 1

    o = df["open"].values.astype(float); h = df["high"].values.astype(float)
    l = df["low"].values.astype(float); c = df["close"].values.astype(float)
    n = len(c)
    body = np.abs(c - o); rng = h - l
    eps = 1e-12
    with np.errstate(divide="ignore", invalid="ignore"):
        small = (body / np.maximum(np.abs(o), eps)) < 0.005          # a1 part1: tiny body
        long_shadow = (rng / np.maximum(body, eps)) > 2.0            # a1 part2: long shadow
        a1 = small & long_shadow
        head_ok = (h - c) <= HEAD_TOP * np.maximum(rng, eps)          # EF guangtou
        crow_ok = (c - l) <= CROW_TOP * np.maximum(rng, eps)         # EF near-low close
    yang = c > o; yin = c < o
    l13 = pd.Series(l).rolling(13).min().values                      # LLV(LOW,13) ending day e
    c13 = pd.Series(c).rolling(13).min().values
    h30 = pd.Series(h).rolling(30).max().values                       # HHV(HIGH,30) ending day d
    c5ago = np.concatenate([np.full(6, np.nan), c[:-6]])             # c[d-6]
    l1 = np.concatenate([np.full(1, np.nan), l[:-1]])                # REF(LOW,1)
    c1 = np.concatenate([np.full(1, np.nan), c[:-1]])
    body_frac_ok = body >= YANG_BODY_FRAC * np.maximum(rng, eps)    # EF changyang body>=50% range

    fires = {}
    # MS: signal day d = e+1 (recovery yang); doji day e = d-1
    ms = np.zeros(n, dtype=bool)
    for d in range(14, n - 1):                                        # need e-1..d+1 windows
        e = d - 1
        if not (yang[d] and body_frac_ok[d] and c[d] > c[e - 1]):
            continue
        if not (yin[e - 1] and a1[e] and (int(a1[e - 1]) + int(a1[e])) == 1):
            continue
        if not (o[e] < c[e - 1]):                                     # gap-down open
            continue
        if not (np.isfinite(l13[e]) and l[e - 1] == l13[e] and c1[e] == c13[e]):
            continue
        ms[d] = True
    fires["MS"] = ms
    # TWS: signal day d = 3rd soldier
    tws = np.zeros(n, dtype=bool)
    for d in range(4, n):
        i, j, k = d - 2, d - 1, d
        if not (yin[i - 1] and yang[i] and yang[j] and yang[k]):
            continue
        if not (o[i] < o[j] < o[k] and c[i] < c[j] < c[k]):
            continue
        if not (head_ok[i] and head_ok[j] and head_ok[k]):
            continue
        b3 = [body[i], body[j], body[k]]
        if min(b3) <= 0 or max(b3) / min(b3) > BODY_RATIO:
            continue
        tws[d] = True
    fires["TWS"] = tws
    # DCC: signal day d (2-bar bearish reversal)
    dcc = np.zeros(n, dtype=bool)
    for d in range(7, n):
        if not (yang[d - 1] and yin[d]):
            continue
        if not (o[d] > h[d - 1]):
            continue
        if not (c[d] < (o[d - 1] + c[d - 1]) / 2.0):
            continue
        if not (np.isfinite(c5ago[d - 1]) and c[d - 1] >= RISE_5D * c5ago[d - 1]):
            continue
        dcc[d] = True
    fires["DCC"] = dcc
    # TBC: signal day d = 3rd crow; AA = h[d-2]==HHV(HIGH,30) ending d; A2 truncated in source (not encoded, honest)
    tbc = np.zeros(n, dtype=bool)
    for d in range(33, n):
        if not (yin[d - 2] and yin[d - 1] and yin[d]):
            continue
        if not (h[d - 2] == h30[d]):
            continue
        if not (c[d - 2] < l[d - 3] and c[d - 1] < l[d - 2] and c[d] < l[d - 1]):
            continue
        okb = all(min(o[i - 1], c[i - 1]) < o[i] < max(o[i - 1], c[i - 1])
                  for i in (d - 2, d - 1, d) if i - 1 >= 0)
        if not okb:
            continue
        if not (crow_ok[d - 2] and crow_ok[d - 1] and crow_ok[d]):
            continue
        tbc[d] = True
    fires["TBC"] = tbc

    dts = df["date"].values
    for k, arr in fires.items():
        idx = np.flatnonzero(arr)
        if len(idx) == 0:
            continue
        stocks_with_event[k].add(code)
        ycounts = {}
        for t in idx:
            y = str(dts[t])[:4]
            ycounts[y] = ycounts.get(y, 0) + 1
            dkey = str(dts[t])[:10]
            day_cross[k][dkey] = day_cross[k].get(dkey, 0) + 1
        stats[k]["n"] += int(len(idx))
        for y, ct in ycounts.items():
            stats[k]["per_year"][y] = stats[k]["per_year"].get(y, 0) + ct
        if len(idx) == 0:
            continue
        stocks_with_event[k].add(code)
        fday, lday = str(dts[idx[0]])[:10], str(dts[idx[-1]])[:10]
        if stats[k]["first"] is None or fday < stats[k]["first"]:
            stats[k]["first"] = fday
        if stats[k]["last"] is None or lday > stats[k]["last"]:
            stats[k]["last"] = lday
    if (pi + 1) % 1000 == 0:
        print(f"  {pi+1}/{len(files)} scanned, {time.time()-t0:.0f}s", flush=True)

for k in stats:
    stats[k]["stocks_with_event"] = len(stocks_with_event[k])
    stats[k]["per_year"] = dict(sorted(stats[k]["per_year"].items()))
    dc = day_cross[k]
    if dc:
        cts = sorted(dc.values(), reverse=True)
        stats[k]["cross_day"] = {
            "distinct_days": len(dc), "max_events_one_day": cts[0],
            "max_day_date": max(dc.items(), key=lambda kv: kv[1])[0],
            "p99_events_one_day": cts[min(len(cts) - 1, max(0, int(round(0.99 * len(cts))) - 1))],
        }

probe = {
    "batch": "CN_KLINE_PATTERN_P1",
    "kind": "pre-freeze probe, FACTS ONLY (R99: zero strategy runs)",
    "machine": "bm-a", "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    "panel": {"source": "Money02/data/bars (read-only, WILD-S1 precedent)",
              "files": len(files), "cutoff": CUTOFF},
    "universe_filter": {"b_layer_ok_static": True, "rows_ge": MIN_ROWS,
                        "last_eq_cutoff": True, "med_amount20_last20_ge_cny": MIN_AMT20},
    "universe": {"n": uni_n, "boards": board_n, "skipped": skip},
    "encodings": {"EF_params": {"head_top": HEAD_TOP, "body_ratio": BODY_RATIO,
                                "rise_5d": RISE_5D, "crow_top": CROW_TOP,
                                "yang_body_frac": YANG_BODY_FRAC},
                  "notes": ["MS: doji-day a1/a2/a3 per THS builtin formula + gap-down + "
                            "yin-before + recovery changyang (body>=50% range) on day d=e+1; "
                            "signal at close[d]",
                            "TWS: 3 yang, opens+closes strictly rising, guangtou (EF 0.3), "
                            "bodies dengchang (EF max/min<=2.0), prior-bar-yin bottom context (EF)",
                            "DCC: yang then open>prev-high yin closing below prior-body midpoint, "
                            "shengshi context EF c[d-1]>=1.05*c[d-6]; volume-expansion factor NOT "
                            "encoded (folklore strengthening note, not definition)",
                            "TBC: 3 yin, AA h[d-2]==HHV30, closes below prior lows, opens inside "
                            "prior bodies, closes near day-low (EF 0.3); source A2 formula "
                            "truncated on page (honest: not encoded)"]},
    "census": stats,
    "elapsed_sec": round(time.time() - t0, 1),
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(probe, f, ensure_ascii=False, indent=1)
print(json.dumps({"universe": uni_n, "skip": skip,
                  "census": {k: {"n": v["n"], "stocks": v["stocks_with_event"],
                                 "cross_day": v.get("cross_day"),
                                 "first": v["first"], "last": v["last"]} for k, v in stats.items()},
                  "elapsed": probe["elapsed_sec"]}, ensure_ascii=False, indent=1))
