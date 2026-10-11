#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lu_prem_census.py -- limit-up next-day premium cheap census (E14 probe face).

Catalog anchor: research/EXTERNAL_IDEAS_CATALOG_R1-20261006.md #2 (first tier,
"cheap limit-up census FIRST, only then full batch"). bm-b lane (astock_daily
panel owner per T-87). Consumer named: SLOT berth draft window.

Laws honored:
  - E30 T+1 open-reality decomposition (DIGEST-20261004-lhb-seat-axis-census):
      gap        = open(T+1)/close(T) - 1   (uncapturable leg for open-entry)
      ret1_open  = close(T+1)/open(T+1) - 1  (capturable: T+1 open -> T+1 close)
      ret5_open  = close(T+5)/open(T+1) - 1  (capturable: T+1 open -> T+5 close)
      prem1      = close(T+1)/close(T) - 1    (filled-at-limit buyer face)
    cost = ce_transfer.COST_X1_RATE single-source import (13.041 bp/side,
    Face A canonical), round trip = 2x, applied to capturable legs.
  - LHB follow-family closure r680/r681 != this axis (list-following vs
    limit-up event) per catalog M2 adjudication: no collision.
  - Zero judged claims, zero panel writes, zero network: descriptive census
    (probe face; judged face requires separate PREREG_TEMPLATE gate).

Identification (qfq close-to-close, honest noise disclosure):
  main  (60xxxx/00xxxx incl 001/002/003): pct >= 9.9%
  chinext (30xxxx): pct >= 9.9% before 2020-08-24, >= 19.9% on/after
  star  (688xxx/689xxx): pct >= 19.9%
  ST 5% band not identifiable from code prefix alone -> implicit undercount,
  disclosed. Intraday zha-ban (high touched, close below) NOT identifiable
  from qfq closes -> disclosed. Exchange rounding gives true limit days at
  ~10.00%+/-0.05%; 9.9% threshold captures them; rare 9.9-10% non-limit
  closes = accepted noise, disclosed. qfq adjustment smears ex-div day
  returns = accepted noise, disclosed.

Usage:
  python scripts/lu_prem_census.py run          # full panel census
  python scripts/lu_prem_census.py selftest      # hermetic fixture legs

Exit contract: 0 = ok, 2 = mechanism failure. Evidence ->
results/lu_prem_census/face.json (+ by_board_rung.csv). Read-only on panel.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from ce_transfer import COST_X1_RATE  # x1 = 13.041bp/side (Face A canonical)

ROOT = os.path.dirname(HERE)
PANEL_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
OUT_DIR = os.path.join(ROOT, "results", "lu_prem_census")

# frozen thresholds (close-to-close, qfq noise tolerated)
TH_MAIN = 0.099
TH_CHINEXT_OLD = 0.099     # before 2020-08-24 registration reform
TH_CHINEXT_NEW = 0.199      # on/after 2020-08-24
TH_STAR = 0.199
CHINEXT_REFORM = pd.Timestamp("2020-08-24")
LONG_GAP_DAYS = 10          # calendar-day suspension face

RUNG_BANDS = [(1, "r1"), (2, "r2"), (3, "r3"), (10 ** 6, "r4+")]


def board_of(code: str) -> str:
    if code.startswith(("688", "689")):
        return "star"
    if code.startswith("30"):
        return "chinext"
    if code.startswith(("60", "00")):
        return "main"
    return "other"


def threshold_for(code: str, ts) -> float:
    b = board_of(code)
    if b == "star":
        return TH_STAR
    if b == "chinext":
        return TH_CHINEXT_NEW if ts >= CHINEXT_REFORM else TH_CHINEXT_OLD
    return TH_MAIN


def rung_band(k: int) -> str:
    for cap, name in RUNG_BANDS:
        if k <= cap:
            return name
    return "r4+"


def era_of(year: int) -> str:
    if year < 2017:
        return "pre2017"
    if year <= 2020:
        return "2017-2020"
    if year <= 2023:
        return "2021-2023"
    return "2024-2026"


def _bucket(agg: dict, key) -> dict:
    b = agg.get(key)
    if b is None:
        b = {"n": 0, "gap": [], "ret1": [], "prem1": [], "ret5": [],
             "promo": [], "long_gap": []}
        agg[key] = b
    return b


def _scan_file(path: str, code: str, agg: dict, meta: dict) -> None:
    try:
        df = pd.read_csv(path, usecols=["date", "open", "close"])
    except Exception as e:  # unreadable file: count, do not crash census
        meta["unreadable"] += 1
        meta["unreadable_head"].append({"code": code, "err": str(e)[:80]})
        return
    n = len(df)
    if n < 3:
        return
    close = df["close"].to_numpy(dtype=float)
    open_ = df["open"].to_numpy(dtype=float)
    dates = pd.to_datetime(df["date"].to_numpy())
    prev = close[:-1]
    cur = close[1:]
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = cur / prev - 1.0
    # pct[i-1] is the return of day i (i from 1..n-1)
    ev_flags = [False] * n
    any_ev = False
    for i in range(1, n):
        v = pct[i - 1]
        if pd.notna(v) and v >= threshold_for(code, dates[i]):
            ev_flags[i] = True
            any_ev = True
    if not any_ev:
        return
    meta["stocks_with_events"] += 1
    meta["bars_total"] += n
    # ladder rung ending at each day (consecutive event days)
    rungs = [0] * n
    streak = 0
    for i in range(1, n):
        if ev_flags[i]:
            streak += 1
        else:
            streak = 0
        rungs[i] = streak
    for i in range(1, n):
        if not ev_flags[i]:
            continue
        if i + 1 >= n:
            meta["tail_events"] += 1   # no next bar: excluded from legs
            continue
        o1 = open_[i + 1]
        c0 = close[i]
        c1 = close[i + 1]
        if not (o1 > 0 and c0 > 0 and c1 > 0):
            meta["bad_px_events"] += 1
            continue
        gap = o1 / c0 - 1.0
        ret1 = c1 / o1 - 1.0
        prem1 = c1 / c0 - 1.0
        ret5 = float("nan")
        if i + 5 < n and close[i + 5] > 0:
            ret5 = close[i + 5] / o1 - 1.0
        gap_days = (dates[i + 1] - dates[i]).days
        # next-day promotion (day i+1 limit-up too)
        promo = False
        if pd.notna(pct[i]):
            promo = bool(pct[i] >= threshold_for(code, dates[i + 1]))
        year = int(dates[i].year)
        b = board_of(code)
        rb = rung_band(rungs[i])
        a = _bucket(agg, (b, rb))
        a["n"] += 1
        a["gap"].append(gap)
        a["ret1"].append(ret1)
        a["prem1"].append(prem1)
        a["promo"].append(1 if promo else 0)
        a["long_gap"].append(1 if gap_days > LONG_GAP_DAYS else 0)
        if ret5 == ret5:
            a["ret5"].append(ret5)
        ya = _bucket(agg, ("year", year))
        ya["n"] += 1
        ya["gap"].append(gap)
        ya["ret1"].append(ret1)
        ya["promo"].append(1 if promo else 0)
        if ret5 == ret5:
            ya["ret5"].append(ret5)
        ea = _bucket(agg, ("era", era_of(year)))
        ea["n"] += 1
        ea["gap"].append(gap)
        ea["ret1"].append(ret1)
        ea["promo"].append(1 if promo else 0)
        if ret5 == ret5:
            ea["ret5"].append(ret5)


def _stat(xs: list) -> dict:
    if not xs:
        return {"n": 0}
    s = pd.Series(xs)
    return {
        "n": int(len(xs)),
        "mean": round(float(s.mean()), 6),
        "median": round(float(s.median()), 6),
        "win": round(float((s > 0).mean()), 4),
    }


def _agg_out(agg: dict, cost_rt: float) -> dict:
    out = {}
    for key in sorted(agg.keys(), key=str):
        a = agg[key]
        entry = {
            "n": a["n"],
            "gap": _stat(a["gap"]),
            "ret1_open": _stat(a["ret1"]),
            "prem1": _stat(a.get("prem1", [])),
            "ret5_open": _stat(a.get("ret5", [])),
            "promo_rate": round(sum(a["promo"]) / max(1, len(a["promo"])), 4),
            "long_gap_share": round(sum(a["long_gap"]) / max(1, len(a["long_gap"])), 4),
        }
        if a.get("ret1"):
            entry["ret1_net_mean"] = round(
                float(pd.Series(a["ret1"]).mean()) - cost_rt, 6)
        if a.get("ret5"):
            entry["ret5_net_mean"] = round(
                float(pd.Series(a["ret5"]).mean()) - cost_rt, 6)
        if a.get("prem1"):
            entry["prem1_net_mean"] = round(
                float(pd.Series(a["prem1"]).mean()) - cost_rt, 6)
        if key[0] in ("year", "era"):
            out.setdefault(key[0], {})[str(key[1])] = entry
        else:
            out["%s|%s" % key] = entry
    return out


def cmd_run() -> int:
    t0 = time.time()
    files = sorted(f for f in os.listdir(PANEL_DIR) if f.endswith(".csv"))
    agg = defaultdict(lambda: defaultdict(list))
    meta = {
        "unreadable": 0, "unreadable_head": [], "stocks_with_events": 0,
        "bars_total": 0, "tail_events": 0, "bad_px_events": 0,
    }
    for f in files:
        code = f[:-4]
        _scan_file(os.path.join(PANEL_DIR, f), code, agg, meta)
    cost_rt = 2 * COST_X1_RATE
    face = {
        "probe": "lu_prem_census",
        "version": "v1.0",
        "law_ref": "E30 T+1 open-reality decomposition (lhb-seat-axis census "
                   "precedent) + EXTERNAL_IDEAS_CATALOG_R1-20261006 #2 "
                   "cheap-census-first",
        "cost_face": "ce_transfer.COST_X1_RATE imported (%.4f bp/side); "
                     "round trip x2 applied to capturable/prem legs"
                     % (COST_X1_RATE * 1e4),
        "identification": {
            "main": "pct >= 9.9% (10% band)",
            "chinext": "pct >= 9.9% before 2020-08-24, >= 19.9% on/after",
            "star": "pct >= 19.9%",
            "disclosures": [
                "ST 5% band not identifiable -> implicit undercount",
                "intraday zha-ban (touched, closed below) not identifiable from qfq closes",
                "exchange rounding: true limit days at ~10.00%; 9.9% threshold "
                "may include rare non-limit 9.9-10% closes",
                "qfq adjustment smears ex-div day returns (identification noise)",
                "next bar = next available bar; suspensions fold into gap legs "
                "(long_gap_share = calendar gap > %d days)" % LONG_GAP_DAYS,
            ],
        },
        "panel": {"files_scanned": len(files), "cutoff": None},
        "meta": meta,
        "elapsed_sec": 0.0,
    }
    maxd = ""
    for f in files[-50:] + files[:50]:
        try:
            tail = pd.read_csv(os.path.join(PANEL_DIR, f), usecols=["date"])
            d = str(tail["date"].iloc[-1])
            if d > maxd:
                maxd = d
        except Exception:
            pass
    face["panel"]["cutoff"] = maxd or "unknown"
    face["segments"] = _agg_out(agg, cost_rt)
    face["elapsed_sec"] = round(time.time() - t0, 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    for key, entry in sorted(face["segments"].items()):
        if key.startswith(("year", "era")):
            continue
        b, rb = key.split("|")
        rows.append({
            "board": b, "rung": rb, "n": entry["n"],
            "gap_mean": entry["gap"].get("mean"),
            "gap_median": entry["gap"].get("median"),
            "gap_win": entry["gap"].get("win"),
            "ret1_mean": entry["ret1_open"].get("mean"),
            "ret1_net_mean": entry.get("ret1_net_mean"),
            "ret5_mean": entry["ret5_open"].get("mean"),
            "ret5_net_mean": entry.get("ret5_net_mean"),
            "prem1_mean": entry["prem1"].get("mean"),
            "prem1_net_mean": entry.get("prem1_net_mean"),
            "promo_rate": entry["promo_rate"],
            "long_gap_share": entry["long_gap_share"],
        })
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "by_board_rung.csv"),
                              index=False)
    with open(os.path.join(OUT_DIR, "face.json"), "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, default=str)
    tot = sum(v["n"] for k, v in face["segments"].items()
              if not k.startswith(("year", "era")))
    print("census done: files=%d events=%d stocks_with_events=%d "
          "cutoff=%s elapsed=%.1fs"
          % (len(files), tot, meta["stocks_with_events"],
             face["panel"]["cutoff"], face["elapsed_sec"]))
    return 0


def _write_fixture(tmp: str) -> str:
    pdir = os.path.join(tmp, "per")
    os.makedirs(pdir, exist_ok=True)
    rows = [
        ("2021-01-04", 10.0, 10.0),
        ("2021-01-05", 10.9, 11.0),   # +10.0% event (rung1)
        ("2021-01-06", 11.55, 11.6),  # +5.45% no event
        ("2021-01-07", 11.6, 11.7),
        ("2021-01-08", 11.7, 11.8),
        ("2021-01-11", 12.88, 12.98),  # +10.0% event (rung1)
        ("2021-01-12", 14.10, 14.28),  # +10.0% event (rung2)
        ("2021-01-13", 13.90, 13.85),  # -3.0%
    ]
    with open(os.path.join(pdir, "600001.csv"), "w", encoding="utf-8") as fh:
        fh.write("date,open,close\n")
        for d, o, c in rows:
            fh.write("%s,%.2f,%.2f\n" % (d, o, c))
    rows2 = [
        ("2019-06-03", 20.0, 20.0),
        ("2019-06-04", 21.8, 22.0),   # +10% event (pre-reform band)
        ("2019-06-05", 22.5, 22.4),   # +1.8% no event
    ]
    with open(os.path.join(pdir, "300002.csv"), "w", encoding="utf-8") as fh:
        fh.write("date,open,close\n")
        for d, o, c in rows2:
            fh.write("%s,%.2f,%.2f\n" % (d, o, c))
    rows3 = [
        ("2022-03-01", 50.0, 50.0),
        ("2022-03-02", 60.0, 60.0),   # +20% event (star band)
        ("2022-03-21", 63.0, 62.0),   # next bar 19 calendar days later (long gap)
    ]
    with open(os.path.join(pdir, "688003.csv"), "w", encoding="utf-8") as fh:
        fh.write("date,open,close\n")
        for d, o, c in rows3:
            fh.write("%s,%.2f,%.2f\n" % (d, o, c))
    return pdir


def cmd_selftest() -> int:
    global PANEL_DIR
    tmp = tempfile.mkdtemp(prefix="lu_prem_st_")
    PANEL_DIR = _write_fixture(tmp)
    agg = defaultdict(lambda: defaultdict(list))
    meta = {"unreadable": 0, "unreadable_head": [], "stocks_with_events": 0,
            "bars_total": 0, "tail_events": 0, "bad_px_events": 0}
    for f in sorted(os.listdir(PANEL_DIR)):
        _scan_file(os.path.join(PANEL_DIR, f), f[:-4], agg, meta)
    fails = []

    def eq(name, a, b, tol=1e-9):
        ok = abs(a - b) <= tol if isinstance(a, float) else a == b
        if not ok:
            fails.append("%s: got %r want %r" % (name, a, b))

    eq("main_r1_n", agg[("main", "r1")]["n"], 2)
    eq("main_r2_n", agg[("main", "r2")]["n"], 1)
    eq("chinext_r1_n", agg[("chinext", "r1")]["n"], 1)
    eq("star_r1_n", agg[("star", "r1")]["n"], 1)
    eq("stocks_with_events", meta["stocks_with_events"], 3)
    # event day2 (close 11.0): T+1 = day3 (open 11.55, close 11.6)
    eq("main_r1_gap0", agg[("main", "r1")]["gap"][0], 11.55 / 11.0 - 1.0)
    eq("main_r1_ret10", agg[("main", "r1")]["ret1"][0], 11.6 / 11.55 - 1.0)
    eq("main_r1_prem10", agg[("main", "r1")]["prem1"][0], 11.6 / 11.0 - 1.0)
    # event day7 (close 14.28, rung2): T+1 = day8 (open 13.90, close 13.85)
    eq("main_r2_gap", agg[("main", "r2")]["gap"][0], 13.90 / 14.28 - 1.0)
    eq("main_r2_ret1", agg[("main", "r2")]["ret1"][0], 13.85 / 13.90 - 1.0)
    eq("main_r1_promo", sum(agg[("main", "r1")]["promo"]), 1)
    eq("star_r1_long_gap", sum(agg[("star", "r1")]["long_gap"]), 1)
    eq("star_r1_gap", agg[("star", "r1")]["gap"][0], 0.05)
    eq("star_r1_ret1", agg[("star", "r1")]["ret1"][0], 62.0 / 63.0 - 1.0)
    eq("era_2021_n", agg[("era", "2021-2023")]["n"], 4)  # main 3 + star 2022
    eq("era_2017_n", agg[("era", "2017-2020")]["n"], 1)
    eq("year_2021_n", agg[("year", 2021)]["n"], 3)
    # ret5: day2 event has i+5 in range; day6 event does not
    eq("main_r1_ret5_n", len(agg[("main", "r1")]["ret5"]), 1)
    if fails:
        print("SELFTEST FAIL (%d):" % len(fails))
        for f in fails:
            print("  " + f)
        return 2
    print("SELFTEST PASS (18 legs)")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        return cmd_run()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
