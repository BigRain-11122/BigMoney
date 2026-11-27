#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Can the convertible-bond book actually be bought, and with how much money?

Why this face exists
--------------------
r2171 gave the dual-low book its first driver, so the desk can now read a fresh
CAGR (7.35% / SR 0.758 at 20 names, 20-day rebalance, 10bp/side) off
`results/cb_dual_low.json`.  That number answers "is the rule worth following".
It does not answer the question the person holding the money asks next:

    at my capital, can I hold the twenty names the rule names, or does the
    one-lot floor eat the book?

The same gap was already paid for once on the futures book (r1780: "the correct
zero is not a ticket" -- 8% cap at 1,000,000 buys 0 lots, and nobody had printed
how much money would change that).  A convertible bond is quoted per 100 CNY of
face value and trades in lots of 10 bonds, so one lot costs `close * 10` CNY.
With 20 equal-weight names, a name whose lot costs 1,500 CNY needs
`1500 * 20 = 30,000` CNY of book before it can hold a single lot -- and below that
the weight is silently *not* 1/20, it is zero.

This script is the ticket, not a new strategy: it reads the published panel,
applies the book's own frozen screen (the same `_eligible` + `close+premium`
ranking that `scripts/cb_dual_low.py` backtests, imported, not re-implemented),
and prints for a ladder of capitals:

  * `rung` -- the smallest book where every picked name clears one lot;
  * per name -- one-lot cost, the weight floor `one_lot / (1/n)`, and the lots
    actually bought at each capital;
  * stranded cash at each capital, i.e. what the lot grid, not the design,
    leaves uninvested.

Verdict (frozen before the first run):

    BUYABLE            at the reference capital every picked name holds >= 1 lot
                       and stranded cash <= STRAND_CAP of the book
    BUYABLE_WITH_STRAND  every name holds a lot but the lot grid strands more
                       than STRAND_CAP (that stray cash is a real cost, print it)
    PARTIAL            some names cannot be held at that capital (the book is
                       not the book that was backtested)
    NOT_BUYABLE        fewer than half the names clear one lot

Freshness: `--check` compares the panel's (size, mtime) and bar against what this
face recorded when it priced, and says STALE when they moved (cheap, no panel
load); `face missing` when there is nothing to compare.  A panel that lags the
official calendar is reported as `panel_lags_calendar`, which is *upstream*
(cb_dual_low's update leg refreshes it) and deliberately not called STALE here.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

PANEL_PATH = os.path.join(ROOT, "data", "cb_panel.csv.gz")
RESULT_JSON = os.path.join(ROOT, "results", "cb_book_ticket_floor.json")

# Frozen with the book it prices (results/cb_dual_low.json main config).
N_HOLD = 20
REBAL = 20
MIN_PRICE = 80.0
MAX_PRICE = 200.0
ITM_PRICE = 130.0
ITM_PREMIUM = 1.0
FACE_PER_BOND = 100.0     # quoted per 100 CNY of face
BONDS_PER_LOT = 10        # SH/SZ convertible minimum board lot
REFERENCE_CAPITALS = (50_000, 100_000, 200_000, 500_000, 1_000_000)
STRAND_CAP = 0.02         # stranded cash above 2% of the book is a printed cost


# ------------------------------------------------------------------ pure parts
def lot_cost(close: float) -> float:
    """One board lot in CNY: 10 bonds, price quoted per 100 CNY of face."""
    return float(close) * BONDS_PER_LOT * FACE_PER_BOND / 100.0


def weight_floor(one_lot: float, n: int) -> float:
    """Smallest book at which a 1/n weight buys one lot."""
    return float(one_lot) * float(n)


def ticket_math(one_lots: list[float], capital: float) -> dict:
    """Whole-lot purchase at equal weight; everything else is stranded cash."""
    n = len(one_lots)
    if n == 0:
        return {"capital": capital, "n": 0, "names_held": 0,
                "invested": 0.0, "stranded": capital,
                "stranded_pct": 1.0, "lots": [],
                "max_weight_dev_pp": None, "top_weight": 0.0}
    target = float(capital) / n
    lots, invested = [], 0.0
    for c in one_lots:
        k = int(math.floor(target / c)) if c > 0 else 0
        lots.append(k)
        invested += k * c
    # realised weights after the lot grid -- this is what the book really holds,
    # and cheap bonds carry more of it than the backtest's 1/n assumed.
    w = [(k * c) / float(capital) for k, c in zip(lots, one_lots)]
    dev = [abs(x - 1.0 / n) for x in w]
    return {
        "capital": float(capital),
        "n": n,
        "names_held": int(sum(1 for k in lots if k > 0)),
        "invested": round(invested, 2),
        "stranded": round(float(capital) - invested, 2),
        "stranded_pct": round((float(capital) - invested) / float(capital), 6),
        "lots": lots,
        "max_weight_dev_pp": round(100.0 * max(dev), 3),
        "top_weight": round(max(w), 6),
    }


def verdict_of(n_names: int, n_held: int, stranded_pct: float) -> str:
    if n_names == 0:
        return "NO_NAMES"
    if n_held < 0.5 * n_names:
        return "NOT_BUYABLE"
    if n_held < n_names:
        return "PARTIAL"
    if stranded_pct > STRAND_CAP:
        return "BUYABLE_WITH_STRAND"
    return "BUYABLE"


# ------------------------------------------------------------------ book screen
def book_on(day_df, n_hold: int = N_HOLD):
    """The book's own frozen screen, imported so the rule cannot drift."""
    import cb_dual_low as cb
    pool = cb._eligible(day_df, MIN_PRICE, MAX_PRICE, None, ITM_PRICE, ITM_PREMIUM)
    if len(pool) < n_hold:
        return pool.iloc[0:0]
    pool = pool.assign(score=pool["close"] + pool["conv_premium"].fillna(50.0))
    return pool.nsmallest(n_hold, "score")


def panel_stamp() -> dict | None:
    try:
        st = os.stat(PANEL_PATH)
    except OSError:
        return None
    return {"bytes": int(st.st_size), "mtime": int(st.st_mtime)}


# ------------------------------------------------------------------ build
def build() -> dict:
    import cb_dual_low as cb

    stamp = panel_stamp()
    if stamp is None:
        return {"face": "cb_book_ticket_floor", "status": "face missing",
                "why": PANEL_PATH + " does not exist"}

    panel = cb._load_panel()
    last = panel["date"].max()
    day = panel[panel["date"] == last]
    picks = book_on(day)
    if len(picks) == 0:
        return {"face": "cb_book_ticket_floor", "status": "NO_NAMES",
                "evidence_cutoff": last.strftime("%Y-%m-%d"),
                "why": "the frozen screen returned fewer names than n_hold on the last bar"}

    names = []
    for _, r in picks.iterrows():
        one = round(lot_cost(r["close"]), 2)
        names.append({
            "code": str(r["code"]),
            "name": (r.get("name") or ""),
            "close": round(float(r["close"]), 3),
            "conv_premium": None if r["conv_premium"] != r["conv_premium"] else round(float(r["conv_premium"]), 3),
            "score": round(float(r["score"]), 3),
            "one_lot_cny": one,
            "weight_floor_cny": round(weight_floor(one, len(picks)), 2),
        })
    one_lots = [x["one_lot_cny"] for x in names]
    rung = round(weight_floor(max(one_lots), len(names)), 2)

    ladder = []
    for cap in REFERENCE_CAPITALS:
        m = ticket_math(one_lots, cap)
        m["verdict"] = verdict_of(len(names), m["names_held"], m["stranded_pct"])
        ladder.append(m)

    at_rung = ticket_math(one_lots, rung)
    # smallest book where the lot grid strands no more than STRAND_CAP: the lot
    # grid thins out as the book grows, so this is a monotone bisection on money.
    lo, hi = rung, max(REFERENCE_CAPITALS)
    while ticket_math(one_lots, hi)["stranded_pct"] > STRAND_CAP and hi < 50_000_000:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ticket_math(one_lots, mid)["stranded_pct"] <= STRAND_CAP:
            hi = mid
        else:
            lo = mid
    clean_capital = round(hi)
    # the rung is the first capital where every name clears one lot; the grid
    # there still strands the remainder of the 10-bond ladder.
    expected = cb.expected_bar_day()
    lag = bool(expected and last.strftime("%Y-%m-%d") < expected)

    out = {
        "face": "cb_book_ticket_floor",
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": last.strftime("%Y-%m-%d"),
        "question": ("at a given capital, can the twenty names the dual-low book "
                     "names actually be held, or does the one-lot floor eat the book?"),
        "rules_frozen": {
            "n_hold": N_HOLD, "rebal": REBAL,
            "screen": f"{MIN_PRICE} <= close <= {MAX_PRICE}, exclude deep-ITM "
                      f"(close>={ITM_PRICE} and conv_premium<={ITM_PREMIUM})",
            "rank": "close + conv_premium (fillna 50), smallest wins",
            "lot": f"{BONDS_PER_LOT} bonds x {FACE_PER_BOND:.0f} face = close*{BONDS_PER_LOT} CNY",
            "strand_cap": STRAND_CAP,
            "imported_from": "scripts/cb_dual_low.py (_eligible / _load_panel)",
            "rule_frozen_before_run": True,
        },
        "panel": {"stamp": stamp, "last_bar": last.strftime("%Y-%m-%d"),
                  "names_on_last_bar": int(len(day)),
                  "expected_bar_official_calendar": expected,
                  "panel_lags_calendar": lag},
        "picks": names,
        "one_lot_floor": {"rung_cny": rung,
                          "why": "max(one_lot) * n_hold: below this the dearest name gets zero weight",
                          "clean_capital_cny": clean_capital,
                          "clean_capital_why": f"smallest book where the lot grid strands <= {STRAND_CAP:.0%}",
                          "at_rung": at_rung,
                          "at_rung_verdict": verdict_of(len(names), at_rung["names_held"],
                                                        at_rung["stranded_pct"])},
        "ladder": ladder,
        "verdict_at_reference": {str(m["capital"]): m["verdict"] for m in ladder},
        "honest_limits": [
            "prices are the last bar's close; a real order pays the next open plus impact",
            "the rung assumes equal weight and whole lots; a broker's minimum commission "
            "per ticket is not in this face (the backtest charges 10bp/side)",
            "the screen reads one bar: names that leave the pool before the next rebalance "
            "are the book's problem, not the floor's",
            "panel_lags_calendar=true means this is yesterday's screen: the write-up is "
            "still correct arithmetic, the pool is not today's",
        ],
    }
    return out


# ------------------------------------------------------------------ check
def check() -> int:
    if not os.path.exists(RESULT_JSON):
        print("CHECK face missing: %s does not exist" % os.path.relpath(RESULT_JSON, ROOT))
        return 3
    try:
        with open(RESULT_JSON, encoding="utf-8") as f:
            face = json.load(f)
    except Exception as e:  # noqa: BLE001
        print("CHECK unreadable: %s" % e)
        return 2
    if face.get("status") == "face missing":
        print("CHECK face missing: the published face says the panel was absent")
        return 3
    cur = panel_stamp()
    old = (face.get("panel") or {}).get("stamp") or {}
    if cur is None:
        print("STALE: the panel is gone since this face priced it")
        return 3
    if cur.get("bytes") != old.get("bytes") or cur.get("mtime") != old.get("mtime"):
        print("STALE: the built panel changed since this face was written "
              "(bytes %s->%s, mtime %s->%s)"
              % (old.get("bytes"), cur.get("bytes"), old.get("mtime"), cur.get("mtime")))
        return 3
    print("CHECK OK: priced on panel bar %s (%d names), stamp matches"
          % (face.get("evidence_cutoff"), len(face.get("picks") or [])))
    return 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    ok = fail = 0

    def want(cond, msg):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("  FAIL:", msg)

    # leg 1-2: lot arithmetic (a 120-price bond is 1,200 CNY a lot)
    want(abs(lot_cost(120.0) - 1200.0) < 1e-9, "lot_cost(120) != 1200")
    want(abs(lot_cost(83.858) - 838.58) < 1e-6, "lot_cost(83.858) != 838.58")

    # leg 3: the weight floor is one_lot * n, not one_lot
    want(abs(weight_floor(1500.0, 20) - 30000.0) < 1e-9, "weight_floor wrong")

    # leg 4-5: whole lots at equal weight, and the remainder is named as stranded
    m = ticket_math([1000.0, 1500.0], 40_000.0)
    want(m["lots"] == [20, 13], "lots %r != [20, 13]" % (m["lots"],))
    want(abs(m["stranded"] - (40_000 - (20 * 1000 + 13 * 1500))) < 1e-6, "stranded wrong")

    # leg 6: a cheap bond takes more of the book than 1/n -- the grid is a tilt
    m_dev = ticket_math([1000.0, 2000.0], 100_000.0)   # targets 50k each: 50 vs 25 lots
    want(m_dev["lots"] == [50, 25], "dev lots %r != [50, 25]" % (m_dev["lots"],))
    want(abs(m_dev["top_weight"] - 0.50) < 1e-9, "top_weight %r != 0.50" % (m_dev["top_weight"],))
    want(abs(m_dev["max_weight_dev_pp"] - 0.0) < 1e-9, "perfect grid should deviate 0pp")

    # leg 7: below the floor the dearest name is bought with zero lots -> PARTIAL
    m_low = ticket_math([1000.0, 40_000.0], 40_000.0)
    want(m_low["names_held"] == 1, "names_held %r != 1" % (m_low["names_held"],))
    want(verdict_of(2, 1, 0.05) == "PARTIAL", "PARTIAL not returned")

    # leg 7: verdict ladder - only held names and stranded cash decide
    want(verdict_of(20, 20, 0.01) == "BUYABLE", "BUYABLE not returned")
    want(verdict_of(20, 20, 0.05) == "BUYABLE_WITH_STRAND", "strand verdict not returned")
    want(verdict_of(20, 5, 0.01) == "NOT_BUYABLE", "NOT_BUYABLE not returned")

    # leg 8: empty book is its own verdict, not a divide-by-zero
    want(verdict_of(0, 0, 1.0) == "NO_NAMES", "NO_NAMES not returned")
    want(ticket_math([], 100_000.0)["stranded"] == 100_000.0, "empty book stranded wrong")

    # leg 9-10: the screen is the book's own, imported (rank = close + premium)
    import pandas as pd

    day = pd.DataFrame({
        "code": ["A", "B", "C", "D"],
        "name": ["a", "b", "c", "d"],
        "close": [100.0, 101.0, 150.0, 60.0],      # D is below MIN_PRICE
        "conv_premium": [5.0, 1.0, 1.0, 1.0],
    })
    picks = book_on(day, n_hold=2)
    want(list(picks["code"]) == ["B", "A"],
         "screen picks %r != ['B','A'] (close+premium; C is dear, D out of the price band)"
         % (list(picks["code"]),))
    itm = pd.DataFrame({
        "code": ["X", "Y"], "name": ["x", "y"],
        "close": [140.0, 100.0], "conv_premium": [0.5, 20.0],
    })
    want(len(book_on(itm, n_hold=1)) == 1 and book_on(itm, n_hold=1).iloc[0]["code"] == "Y",
         "deep-ITM exclusion broke")

    print(f"cb_book_ticket_floor selftest {ok}/{ok + fail}", flush=True)
    return 0 if fail == 0 else 1


# ------------------------------------------------------------------ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="cheap drift check against the published face")
    ap.add_argument("--selftest", action="store_true", help="offline assertions, no data read")
    ap.add_argument("--quiet", action="store_true", help="write the face, print one line")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check()

    out = build()
    if out.get("status") in ("face missing", "NO_NAMES"):
        print("%s: %s" % (out["status"], out.get("why", "")))
        return 3
    os.makedirs(os.path.dirname(RESULT_JSON), exist_ok=True)
    tmp = RESULT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, RESULT_JSON)

    ladder = out["ladder"]
    worst = max(ladder, key=lambda m: m["stranded_pct"])
    cheap = min(ladder, key=lambda m: m["capital"])
    print("bar %s | picks %d | rung %.0f CNY (dearest lot %.0f x %d)"
          % (out["evidence_cutoff"], len(out["picks"]), out["one_lot_floor"]["rung_cny"],
             max(x["one_lot_cny"] for x in out["picks"]), len(out["picks"])))
    print("at %d CNY: %s, %d/%d names hold a lot, stranded %.1f%%, top weight %.2f%% (vs %.2f%% at 1/n)"
          % (cheap["capital"], cheap["verdict"], cheap["names_held"], cheap["n"],
             100 * cheap["stranded_pct"], 100 * cheap["top_weight"], 100.0 / cheap["n"]))
    print("worst strand on the ladder: %d CNY -> %.2f%% uninvested"
          % (worst["capital"], 100 * worst["stranded_pct"]))
    if out["panel"]["panel_lags_calendar"]:
        print("note: panel bar %s lags the official calendar (%s) -- screen is stale upstream"
              % (out["panel"]["last_bar"], out["panel"]["expected_bar_official_calendar"]))
    print("wrote %s" % os.path.relpath(RESULT_JSON, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
