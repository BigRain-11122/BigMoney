#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cb_parking_shelf_at_size -- the class pays; can the shelf hold our money?

WHY THIS FACE EXISTS
--------------------
`cb_parking_bakeoff` (r2040) answered the CEO's question ("convertibles may supplement
the idle periods") at the *class* level: the two convertible ETFs pay 1.83%/yr against the
repo leg's 1.77%, and they fall 0.665% on the days the book defends (beta 0.36).  It stopped
there.  A treasurer cannot buy a class -- he buys a shelf: 100 份 at a time, on a day when
somebody is on the other side, with a cash leg of a fixed size.

`repo_capacity_at_size` already put the repo tenors on that ruler (p10 of the bad day, 1%/10%
participation bands, minimum ticket).  The convertible shelf has never been measured on it.
So the two published readings -- "the class pays 0.067pp more" and "the shelf is what we can
actually buy" -- were never put on the same axis.  This face does exactly that.

THE QUESTION (frozen before the first run)
------------------------------------------
At the sizes we actually run, can the convertible shelf absorb the cash leg, what does a lot
leave stranded, and what does one defence day cost at that size?

MODEL
-----
* **Ruler** = p10 of the daily turnover series (the bad day), the same convention
  `repo_capacity_at_size` froze.  The bands are imported from that face rather than retyped,
  and a selftest leg asserts the two faces still agree (1% / 10%).
* **Bands** = OPEN <= 1% of the bad day, THIN <= 10%, BLOCKED above.  A participation band is
  a market-impact convention, not a measured impact: our orders are small enough that no
  impact model exists, and the band keeps us away from days where we *are* the tape.
* **Lot** = 100 份, the exchange minimum for an ETF.  It is not asserted: the face prints the
  lot's value in yuan so the reader can check it against the screen.
* **Effective yield at size** = (full lots x the instrument's own net CAGR + the residue x
  the repo net rate) / size.  The residue cannot buy convertibles; it sits in the repo leg.
  That is the only place lot friction becomes money, so it is printed in bp of the sleeve.
* **Round trip** = 2bp/side (r2040's ETF caliber), printed next to the annual extra so the
  payback time is on the page and not left to the reader's mental arithmetic.
* **Defence day** = the equity yardstick's own <= -1% days, rebuilt here with r2040's own
  yard construction (equal-weight equity ETFs, monthly, 2bp/side), then cross-checked against
  the published defence reading of the convertible blend.  Two faces that drift apart are two
  claims, so the delta is printed and a leg re-derives it.

VERDICTS (mechanical, no taste)
-------------------------------
* SHELF_ABSORBS_THE_WHOLE_CASH_LEG   -- both convertible rows are OPEN at the ticket's cash.
* SHELF_ABSORBS_ONLY_A_SLICE         -- some convertible row is OPEN at the quarter-cash tier
                                        but not at the ticket's cash.
* SHELF_IS_SHUT_AT_OUR_SIZE          -- no convertible row is OPEN even at the smallest tier.
* THE_LOT_COSTS_UNDER_ONE_BP         -- the residue-driven yield drag at the ticket tier is
                                        below 1bp of the sleeve on every convertible row.
* ONE_DEFENCE_DAY_OUTWEIGHS_THE_YEAR -- one bad day at the parked size costs more than a full
                                        year of the extra the shelf pays over the repo leg.
* THE_COMPARATORS_PAY_LESS_THAN_THE_REPO -- the money/bond rows underperform the repo leg even
                                        before their own defence days.
* UNIT_SUSPECT                       -- a turnover magnitude outside the exchange's published
                                        range; no capacity number is printed.

Usage:
    python scripts/cb_parking_shelf_at_size.py run
    python scripts/cb_parking_shelf_at_size.py --check
    python scripts/cb_parking_shelf_at_size.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_parking_bakeoff as B  # noqa: E402  (r2040 construction: yard, defence, cagr)
import etf_book_cash_vehicle as CV  # noqa: E402  (money ETF share-reset consolidation)
import etf_composite_pf as E  # noqa: E402  (ETF panel with close/open/amount)
import etf_equity_alpha as A  # noqa: E402  (flip repair + class map)
import repo_capacity_at_size as RC  # noqa: E402  (the frozen capacity bands)

OUT_JSON = os.path.join(ROOT, "results", "cb_parking_shelf_at_size.json")
OUT_MD = os.path.join(ROOT, "research", "CB_PARKING_SHELF_AT_SIZE.md")
R2040_JSON = os.path.join(ROOT, "results", "cb_parking_bakeoff.json")

START = "2020-07-16"          # the window every cash-leg face already uses
LOT_UNITS = 100               # exchange ETF minimum, printed as money below
COST_BP_SIDE = 2.0            # r2040's ETF caliber: 0.02%/side, charged once each way
PRICE_DEC = 4
TIERS = (250_000, 565_246, 1_000_000, 2_000_000, 5_000_000)
TIER_LABELS = {250_000: "quarter", 565_246: "ticket", 1_000_000: "1M",
               2_000_000: "2M", 5_000_000: "5M"}
SHELF = (
    ("511380", "cb_etf_sh", "convertible", "SSE convertible ETF (the larger of the two)"),
    ("511180", "cb_etf_sz", "convertible", "the second convertible ETF"),
    ("511880", "money_etf", "money", "price-accumulating money ETF"),
    ("511360", "short_fin_etf", "money", "short-term financing ETF"),
    ("511010", "bond_etf", "bond", "treasury bond ETF"),
)
UNIT_RANGES = {  # median daily turnover must land where the exchange's own magnitude is
    "511380": (1e8, 3e10),
    "511180": (5e7, 3e10),
    "511880": (1e8, 1e11),
    "511360": (5e7, 1e11),
    "511010": (1e7, 1e10),
}
SCHEMA = "cb-parking-shelf-at-size/v1"


# --------------------------------------------------------------------------- helpers
def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _content_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _now():
    return dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def lot_split(size, lot_value):
    """How many whole lots fit, and what is stranded in the repo leg."""
    if size is None or lot_value is None or not np.isfinite(lot_value) or lot_value <= 0:
        return 0, float(size or 0.0), float("nan")
    lots = int(size // lot_value)
    filled = lots * float(lot_value)
    residue = float(size) - filled
    residue_bp = residue / float(size) * 1e4 if size else float("nan")
    return lots, residue, residue_bp


def effective_yield_pct(size, lot_value, own_pct, repo_pct):
    """What the sleeve actually earns once the residue has to sit in the repo leg."""
    lot_value = float(lot_value)
    if size <= 0 or not np.isfinite(lot_value) or lot_value <= 0:
        return float("nan")
    lots, residue, _bp = lot_split(size, lot_value)
    filled = lots * lot_value
    if filled <= 0:
        return float(repo_pct)
    return (filled * float(own_pct) + residue * float(repo_pct)) / float(size)


def round_trip_bp(cost_bp_side=COST_BP_SIDE):
    return 2.0 * float(cost_bp_side)


def payback_years(extra_pp, cost_bp=COST_BP_SIDE):
    """How long the shelf's own round trip takes to be repaid by its extra yield."""
    rt_pp = round_trip_bp(cost_bp) / 100.0     # bp -> pp
    if extra_pp is None or not np.isfinite(extra_pp) or extra_pp <= 0:
        return None
    return rt_pp / float(extra_pp)


def years_per_defence_day(defence_mean_pct, extra_pp):
    """One defence day measured in years of the extra the shelf pays over the repo leg."""
    if extra_pp is None or not np.isfinite(extra_pp) or extra_pp <= 0:
        return None
    if defence_mean_pct is None or not np.isfinite(defence_mean_pct):
        return None
    return abs(float(defence_mean_pct)) / float(extra_pp)


def buy_hold_rets(px, start, end, cost_bp_side=COST_BP_SIDE):
    """Buy and hold the instrument, one round trip charged on the entry bar."""
    s = px.dropna()
    s = s[(s.index >= pd.Timestamp(start)) & (s.index <= pd.Timestamp(end))]
    if len(s) < 40:
        return None
    r = s.pct_change().dropna()
    r.iloc[0] -= round_trip_bp(cost_bp_side) / 1e4
    return r


def capacity_row(code, label, klass, amount, price, own_pct, repo_pct, defence):
    vol = amount.dropna()
    vol = vol[vol.index >= pd.Timestamp(START)]
    med = float(vol.median()) if len(vol) else float("nan")
    bad = float(vol.quantile(0.10)) if len(vol) else float("nan")
    lot_value = float(price) * LOT_UNITS
    dm = float(defence["mean_pct"]) if defence and defence.get("mean_pct") is not None else None
    capped = {}
    for tier in TIERS:
        cls, part = RC.part_class(float(tier), bad)
        lots, residue, residue_bp = lot_split(float(tier), lot_value)
        eff = effective_yield_pct(tier, lot_value, own_pct, repo_pct)
        capped[str(tier)] = {
            "participation_pct_of_bad_day": round(part * 100.0, 4),
            "class": cls,
            "lots": lots,
            "residue_cny": round(residue, 2),
            "residue_bp": round(residue_bp, 3) if np.isfinite(residue_bp) else None,
            "effective_yield_pct": round(eff, 6) if np.isfinite(eff) else None,
            "yield_drag_bp": round((float(own_pct) - eff) * 100.0, 4) if np.isfinite(eff) else None,
            "extra_vs_repo_pp": round(eff - float(repo_pct), 4) if np.isfinite(eff) else None,
            "cny_per_year_vs_repo": round((eff - float(repo_pct)) / 100.0 * float(tier), 2)
            if np.isfinite(eff) else None,
            "one_defence_day_cny": round(float(tier) * dm / 100.0, 2)
            if dm is not None and np.isfinite(dm) else None,
            "years_of_extra_per_defence_day": (
                round(y, 3) if (y := years_per_defence_day(dm, eff - float(repo_pct))) is not None
                else None),
        }
    max_open_yuan = RC.PART_OK * bad if np.isfinite(bad) else float("nan")
    return {
        "code": code,
        "label": label,
        "class": klass,
        "price": round(float(price), PRICE_DEC),
        "lot_units": LOT_UNITS,
        "lot_value_cny": round(lot_value, 2),
        "bars": int(len(vol)),
        "turnover_median_yuan": round(med, 0),
        "turnover_bad_day_yuan": round(bad, 0),
        "max_open_order_cny": round(max_open_yuan, 0) if np.isfinite(max_open_yuan) else None,
        "max_open_lots": (int(max_open_yuan // lot_value)
                          if np.isfinite(max_open_yuan) and lot_value > 0 else None),
        "own_net_cagr_pct": round(float(own_pct), 4),
        "defence": defence,
        "capacity": capped,
    }


# --------------------------------------------------------------------------- build
def build(write=True, verbose=True):
    t0 = time.time()
    log = (lambda *a: print(*a, flush=True)) if verbose else (lambda *a: None)

    if not os.path.exists(R2040_JSON):
        print("MISSING FACE: %s (r2040's parking face is the repo comparator)" % R2040_JSON)
        return 2
    with io.open(R2040_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    repo_pct = float(pub["headline"]["repo_net_pct"])
    ticket_cash = float(pub["ticket"]["cash_cny"])

    close_all, open_all, amt_all, _feats = E.build_panel()
    close_all, _open2, n_flip = A.repair_flips(close_all, open_all)
    log("  ETF panel: %d columns, %d flips repaired" % (close_all.shape[1], n_flip))
    cmap = A.load_class_map()
    cls = A.classify(close_all.columns, cmap, close_all)
    eq_cols = [c for c in close_all.columns if cls[c] == "equity"]
    log("  equity yardstick columns: %d" % len(eq_cols))

    end = close_all.index[-1]
    yard, _yinfo = B.ew_arm(close_all[eq_cols], START, str(end.date()), COST_BP_SIDE)
    log("  yard: %s..%s bars=%d" % (yard.index[0].date(), yard.index[-1].date(), len(yard)))

    rows = []
    for code, label, klass, note in SHELF:
        if code not in close_all.columns:
            print("MISSING INSTRUMENT: %s on the panel" % code)
            return 2
        px = close_all[code]
        resets = 0
        rets = None
        if klass == "money":
            # a price-accumulating money ETF resets its share count; the raw pct_change of the
            # traded line is not a return (r2040 removed 13 such jumps on 511880 alone)
            try:
                rets, jumps = CV.consolidation_returns(CV.load_etf(code))
                resets = len(jumps)
                rets = rets[(rets.index >= pd.Timestamp(START)) & (rets.index <= pd.Timestamp(end))]
                if len(rets) < 40:
                    rets = None
            except Exception as exc:  # noqa: BLE001 -- fall back and say so
                log("  %s: consolidation unavailable (%s) -> raw buy and hold" % (code, exc))
                rets = None
        if rets is None:
            rets = buy_hold_rets(px, START, str(end.date()))
        if rets is None:
            print("MISSING WINDOW: %s has too few bars" % code)
            return 2
        own = B.cagr(rets)
        defence = B.defence_stats(rets, yard)
        med = float(amt_all[code].dropna().median()) if code in amt_all.columns else float("nan")
        lo, hi = UNIT_RANGES[code]
        unit_ok = bool(np.isfinite(med) and lo <= med <= hi)
        row = capacity_row(code, label, klass,
                           amt_all[code] if code in amt_all.columns else pd.Series(dtype=float),
                           float(px.dropna().iloc[-1]), own, repo_pct, defence)
        row["note"] = note
        if resets:
            row["share_resets_removed"] = resets
        row["beta_to_equity"] = round(float(B.beta_corr(rets, yard)[0]), 3) \
            if np.isfinite(B.beta_corr(rets, yard)[0]) else None
        row["unit_check"] = {"median_yuan": round(med, 0) if np.isfinite(med) else None,
                             "range": [lo, hi], "ok": unit_ok}
        rows.append(row)
        log("  %s %-14s px=%.3f lot=%.0f cagr=%.3f%% bad_day=%.0fwan open_order=%.0fwan"
            % (code, label, row["price"], row["lot_value_cny"], row["own_net_cagr_pct"],
               row["turnover_bad_day_yuan"] / 1e4, (row["max_open_order_cny"] or 0) / 1e4))

    # cross-check: the same blend r2040 published, rebuilt here
    cb_codes = [c for c, _l, k, _n in SHELF if k == "convertible" and c in close_all.columns]
    blend, _binfo = B.ew_arm(close_all[cb_codes], START, str(end.date()), COST_BP_SIDE)
    blend_cagr = round(float(B.cagr(blend)), 4)
    blend_def = B.defence_stats(blend, yard)
    agreement = {
        "source": os.path.basename(R2040_JSON),
        "published_cb_etf_net_pct": pub["headline"]["cb_etf_net_pct"],
        "rebuilt_cb_etf_net_pct": blend_cagr,
        "delta_net_pp": round(blend_cagr - float(pub["headline"]["cb_etf_net_pct"]), 4),
        "published_defence_mean_pct": pub["headline"]["cb_etf_defence_mean_pct"],
        "rebuilt_defence_mean_pct": blend_def["mean_pct"],
        "delta_defence_pp": round(blend_def["mean_pct"] - float(pub["headline"]["cb_etf_defence_mean_pct"]), 4),
        "published_defence_days": [a for a in pub["arms"] if a["label"] == "cb_etf_ew"][0]["defence_days"]["days"],
        "rebuilt_defence_days": blend_def["days"],
        "agree_net_within_0_01pp": abs(blend_cagr - float(pub["headline"]["cb_etf_net_pct"])) <= 0.01,
        "agree_defence_within_0_02pp": abs(blend_def["mean_pct"] - float(pub["headline"]["cb_etf_defence_mean_pct"])) <= 0.02,
    }
    pub_money = [a for a in pub["arms"] if a["label"] == "money_511880"]
    mine_money = [r for r in rows if r["label"] == "money_etf"]
    if pub_money and mine_money:
        agreement["published_money_net_pct"] = pub_money[0]["net_cagr_pct"]
        agreement["rebuilt_money_net_pct"] = mine_money[0]["own_net_cagr_pct"]
        agreement["delta_money_pp"] = round(mine_money[0]["own_net_cagr_pct"] - float(pub_money[0]["net_cagr_pct"]), 4)
    log("  agreement with r2040: net %+.4fpp / defence %+.4fpp / days %d vs %d"
        % (agreement["delta_net_pp"], agreement["delta_defence_pp"],
           agreement["rebuilt_defence_days"], agreement["published_defence_days"]))

    tickets = [r for r in rows if r["class"] == "convertible"]
    small_tier, ticket_tier = str(TIERS[0]), str(TIERS[1])
    verdict = []
    if not all(r["unit_check"]["ok"] for r in rows):
        verdict = ["UNIT_SUSPECT"]
    else:
        if all(r["capacity"][ticket_tier]["class"] == "OPEN" for r in tickets):
            verdict.append("SHELF_ABSORBS_THE_WHOLE_CASH_LEG")
        elif sum((r["max_open_order_cny"] or 0.0) for r in tickets) >= ticket_cash \
                and all((r["max_open_order_cny"] or 0.0) > 0 for r in tickets):
            verdict.append("SHELF_ABSORBS_THE_CASH_LEG_IN_TWO_ORDERS")
        elif any(r["capacity"][small_tier]["class"] == "OPEN" for r in tickets):
            verdict.append("SHELF_ABSORBS_ONLY_A_SLICE")
        else:
            verdict.append("SHELF_IS_SHUT_AT_OUR_SIZE")
        drags = [r["capacity"][ticket_tier]["yield_drag_bp"] for r in tickets]
        if all(d is not None and abs(d) < 1.0 for d in drags):
            verdict.append("THE_LOT_COSTS_UNDER_ONE_BP")
        best = max(tickets, key=lambda r: r["capacity"][ticket_tier]["extra_vs_repo_pp"] or -9e9)
        yrs = best["capacity"][ticket_tier]["years_of_extra_per_defence_day"]
        if yrs is not None and yrs >= 1.0:
            verdict.append("ONE_DEFENCE_DAY_OUTWEIGHS_THE_YEAR")
        comps = [r for r in rows if r["class"] in ("money", "bond")]
        if comps and all(r["own_net_cagr_pct"] < repo_pct for r in comps):
            verdict.append("THE_COMPARATORS_PAY_LESS_THAN_THE_REPO")

    face = {
        "schema": SCHEMA,
        "artifact": "cb_parking_shelf_at_size",
        "generated": _now(),
        "evidence_cutoff": str(end.date()),
        "window": {"start": START, "end": str(end.date())},
        "question": ("at the sizes we actually run, can the convertible shelf absorb the cash leg, "
                     "what does a lot leave stranded, and what does one defence day cost at that size?"),
        "order_ref": pub.get("order_ref"),
        "comparator": {"repo_net_pct": repo_pct, "provenance": "%s::headline.repo_net_pct" % os.path.basename(R2040_JSON)},
        "ruler": {"bad_day": "p10 of the daily turnover series",
                  "open_max_participation": RC.PART_OK,
                  "thin_max_participation": RC.PART_THIN,
                  "bands_imported_from": "scripts/repo_capacity_at_size.py"},
        "lot": {"units": LOT_UNITS, "cost_bp_per_side": COST_BP_SIDE,
                "round_trip_bp": round_trip_bp()},
        "tiers_cny": list(TIERS),
        "ticket_cash_cny": ticket_cash,
        "rows": rows,
        "agreement_with_r2040": agreement,
        "verdict": verdict,
        "headline": {
            "best_shelf": max(tickets, key=lambda r: r["capacity"][ticket_tier]["effective_yield_pct"])["label"],
            "best_shelf_open_order_cny": max(tickets, key=lambda r: r["max_open_order_cny"] or 0)["max_open_order_cny"],
            "best_shelf_bad_day_m": round(max(r["turnover_bad_day_yuan"] for r in tickets) / 1e6, 1),
            "combinable_open_order_cny": round(sum((r["max_open_order_cny"] or 0) for r in tickets), 0),
            "ticket_participation_pct": max(tickets, key=lambda r: r["turnover_bad_day_yuan"] or 0)
            ["capacity"][ticket_tier]["participation_pct_of_bad_day"],
            "one_defence_day_cny_at_ticket": max((r["capacity"][ticket_tier]["one_defence_day_cny"] or 0)
                                                 for r in tickets),
            "year_extra_cny_at_ticket": max((r["capacity"][ticket_tier]["cny_per_year_vs_repo"] or 0)
                                            for r in tickets),
            "years_of_extra_per_defence_day": yrs,
            "payback_years_best_shelf": (round(payback_years(max(r["capacity"][ticket_tier]["extra_vs_repo_pp"] or -9e9
                                                               for r in tickets)), 3)
                                         if max(r["capacity"][ticket_tier]["extra_vs_repo_pp"] or -9e9
                                                for r in tickets) > 0 else None),
            "lot_value_money_etf_cny": [r["lot_value_cny"] for r in rows if r["label"] == "money_etf"][0],
            "lot_value_cb_cny": [r["lot_value_cny"] for r in tickets][0],
        },
        "data_sha": {"r2040_face": _sha(R2040_JSON)},
        "notes": ("Participation is measured against the p10 day, so 'OPEN at the ticket tier' means "
                  "our order is no more than 1% of a bad day's tape. The residue is priced at the repo "
                  "net rate; the effective yield therefore never flatters the shelf. Defence days are "
                  "the equity yardstick's own <= -1% bars, rebuilt with r2040's construction."),
        "not_measured": [
            "intraday execution shape (the face prices turnover, not our fill)",
            "IOPV / premium at the trade timestamp",
            "conversion-bond ETF lending or fee differences between the two listings",
            "the class-vs-shelf gap (equal weight vs issuance weight) -- r2040 already prints it",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items()
                                           if k not in ("content_sha256", "elapsed_sec", "generated")})
    if write:
        with io.open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
        with io.open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(render_md(face))
    log("  verdict: %s | route: %s" % (" ".join(face["verdict"]), OUT_JSON))
    return 0


# --------------------------------------------------------------------------- render
def _m(x):
    return "{:,.0f}".format(x) if isinstance(x, (int, float)) and np.isfinite(x) else "-"


def render_md(face):
    h = face["headline"]
    tickets = [r for r in face["rows"] if r["class"] == "convertible"]
    big = max(tickets, key=lambda r: r["max_open_order_cny"] or 0)
    small = min(tickets, key=lambda r: r["max_open_order_cny"] or 0)
    money = [r for r in face["rows"] if r["label"] == "money_etf"][0]
    t_ticket = str(face["tiers_cny"][1])
    t_small = str(face["tiers_cny"][0])
    cb_cap = big["capacity"][t_ticket]
    L = []
    L.append("# 转债停泊货架：这一类能付钱，这副货架能不能装下钱？")
    L.append("")
    L.append("r2040 的判词是「这一类付得比回购多，但在书防守的那些日子跟着跌」。这张面接着问"
             "下一个问题——**我们真的下得进去吗**：一手 100 份、现金腿 %s 元、坏日子的成交只有 p10。"
             % _m(face["ticket_cash_cny"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append("货架装得下，但要用两张单：%s 在坏日子（p10 成交 %s 元）上一张 1%% 的单最多 %s 元，"
             "%s 再给 %s 元，两张合起来 %s 元 > 票面的 %s 元；单靠 %s 一张，票面的现金腿是它坏日子的 "
             "%s%%（%s 档）。整手不是障碍：转债 ETF 一手只要 %s 元，货币 ETF 一手 %s 元——"
             "%s 元停在货币 ETF 上留 %s%% 的零头，停在转债上只留 %s%%。"
             "代价不在容量上：票面规模下 %s 一个防守日亏 %s 元，而它一年比回购只多赚 %s 元，"
             "**一个防守日 = %s 年的超额**。"
             % (big["code"], _m(big["turnover_bad_day_yuan"]),
                _m(big["max_open_order_cny"]), small["code"], _m(small["max_open_order_cny"]),
                _m(h["combinable_open_order_cny"]), _m(face["ticket_cash_cny"]), big["code"],
                _fmt(cb_cap["participation_pct_of_bad_day"], 2), cb_cap["class"],
                _m(big["lot_value_cny"]), _m(money["lot_value_cny"]),
                _m(face["tiers_cny"][0]), _fmt(money["capacity"][t_small]["residue_bp"] / 100.0, 2),
                _fmt(big["capacity"][t_small]["residue_bp"] / 100.0, 2),
                big["code"], _m(abs(cb_cap["one_defence_day_cny"] or 0.0)),
                _m(cb_cap["cny_per_year_vs_repo"]), _fmt(h["years_of_extra_per_defence_day"], 1)))
    L.append("")
    L.append("判词：**%s**" % " + ".join(face["verdict"]))
    L.append("")
    L.append("## 尺子（先冻结，再看数）")
    L.append("")
    L.append("- 窗口 %s .. %s（与所有现金腿面同一窗口）。" % (face["window"]["start"], face["window"]["end"]))
    L.append("- 坏日子 = 日成交额的 p10；参与带 = OPEN ≤1% / THIN ≤10% / BLOCKED 更高"
             "（常量直接 import 自 `scripts/repo_capacity_at_size.py`，同一个尺子）。")
    L.append("- 一手 = %d 份（交易所 ETF 最小单位）；一手的钱直接印出来，读者可以对着行情软件核。"
             % face["lot"]["units"])
    L.append("- 有效收益 = (整手 × 该标的自身净年化 + 零头 × 回购净利率) / 规模。零头买不了转债，"
             "只能停在回购腿，所以整手摩擦只在这里变成钱。")
    L.append("- 来回成本 = %d bp（r2040 的 ETF 口径，2bp/边）。" % face["lot"]["round_trip_bp"])
    L.append("")
    L.append("## 货架（按规模）")
    L.append("")
    for r in face["rows"]:
        L.append("### %s · %s（%s）" % (r["code"], r["label"], r["class"]))
        L.append("")
        L.append("价格 ¥%.3f · 一手 ¥%s · 自身净年化 %.3f%% · 坏日子成交 ¥%s 万 · "
                 "p10 的 1%% 最大单 ¥%s 万（%s 手）· 防守日均值 %s%%"
                 % (r["price"], _m(r["lot_value_cny"]), r["own_net_cagr_pct"],
                    _m(r["turnover_bad_day_yuan"] / 1e4), _m((r["max_open_order_cny"] or 0) / 1e4),
                    _m(r["max_open_lots"]), _fmt(r["defence"]["mean_pct"] if r["defence"] else None, 3)))
        L.append("")
        L.append("| 规模 | 占坏日子 | 档 | 整手 | 零头 ¥ | 零头 bp | 有效收益 % | 比回购 pp | 一年 ¥ | 一个防守日 ¥ | 一个防守日 = 几年的超额 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for tier in face["tiers_cny"]:
            c = r["capacity"][str(tier)]
            L.append("| ¥%s | %s%% | %s | %d | %s | %s | %s | %s | %s | %s | %s |"
                     % (_m(tier), _fmt(c["participation_pct_of_bad_day"], 3), c["class"], c["lots"],
                        _m(c["residue_cny"]), _fmt(c["residue_bp"], 2),
                        _fmt(c["effective_yield_pct"], 4), _fmt(c["extra_vs_repo_pp"], 4),
                        _m(c["cny_per_year_vs_repo"]), _m(c["one_defence_day_cny"]),
                        _fmt(c["years_of_extra_per_defence_day"], 2)))
        L.append("")
    L.append("## 与 r2040 的对照（两张面不许各说各的）")
    L.append("")
    a = face["agreement_with_r2040"]
    L.append("- 转债 ETF 等权净年化：r2040 印 %.4f%%，本面重建 %.4f%%（差 %+.4f pp）。"
             % (a["published_cb_etf_net_pct"], a["rebuilt_cb_etf_net_pct"], a["delta_net_pp"]))
    L.append("- 防守日均值：r2040 印 %.3f%%，本面重建 %.3f%%（差 %+.3f pp）；防守日天数 %d 对 %d。"
             % (a["published_defence_mean_pct"], a["rebuilt_defence_mean_pct"], a["delta_defence_pp"],
                a["rebuilt_defence_days"], a["published_defence_days"]))
    if "rebuilt_money_net_pct" in a:
        L.append("- 货币 ETF 净年化：r2040 印 %.4f%%，本面重建 %.4f%%（差 %+.4f pp）——"
                 "这条腿同时证明份额复位已经修掉，否则货币 ETF 会读成一个负数。"
                 % (a["published_money_net_pct"], a["rebuilt_money_net_pct"], a["delta_money_pp"]))
    L.append("")
    L.append("## 这张面没测的")
    L.append("")
    for n in face["not_measured"]:
        L.append("- %s" % n)
    L.append("")
    L.append("数据：ETF 面板（close/open/amount，含翻转修复）× %d 列 · 回购对照 `%s::headline.repo_net_pct`"
             " · 票面 `%s`。生成 %s，用时 %ss。"
             % (len(face["rows"]), a["source"], "TICKET-2026-11-20.json", face["generated"], face["elapsed_sec"]))
    L.append("")
    return "\n".join(L)


def _fmt(x, nd=2):
    return "{:,.{nd}f}".format(x, nd=nd) if isinstance(x, (int, float)) and np.isfinite(x) else "-"


# --------------------------------------------------------------------------- check
def check(json_path=None, md_path=None):
    json_path, md_path = json_path or OUT_JSON, md_path or OUT_MD
    problems = []
    if not os.path.exists(json_path):
        print("STALE face missing:", json_path)
        return 3
    if not os.path.exists(md_path):
        print("STALE page missing:", md_path)
        return 3
    with io.open(json_path, encoding="utf-8") as f:
        face = json.load(f)
    md = io.open(md_path, encoding="utf-8").read()

    if os.path.exists(R2040_JSON) and _sha(R2040_JSON) != face["data_sha"]["r2040_face"]:
        print("STALE input moved: r2040 face")
        return 3

    def near(a, b, tol, what):
        if a is None or b is None:
            problems.append("%s: missing (%r vs %r)" % (what, a, b))
            return
        if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) \
                or not isinstance(b, (int, float)):
            problems.append("%s: not a number (%r vs %r)" % (what, a, b))
            return
        if abs(a - b) > tol:
            problems.append("%s: %r vs %r" % (what, a, b))

    # every printed tier row must be re-derivable from the row's own published inputs
    repo = face["comparator"]["repo_net_pct"]
    for r in face["rows"]:
        lot_value = r["price"] * r["lot_units"]
        near(lot_value, r["lot_value_cny"], 0.01 + 1e-9, "%s lot value" % r["code"])
        bad = r["turnover_bad_day_yuan"]
        near(RC.PART_OK * bad, r["max_open_order_cny"], 1.0, "%s max open" % r["code"])
        for tier in face["tiers_cny"]:
            c = r["capacity"][str(tier)]
            cls, part = RC.part_class(float(tier), bad)
            if cls != c["class"]:
                problems.append("%s@%s: class %s vs %s" % (r["code"], tier, cls, c["class"]))
            near(part * 100.0, c["participation_pct_of_bad_day"], 5e-4, "%s@%s part" % (r["code"], tier))
            lots, residue, residue_bp = lot_split(float(tier), lot_value)
            if lots != c["lots"]:
                problems.append("%s@%s: lots %d vs %d" % (r["code"], tier, lots, c["lots"]))
            near(residue, c["residue_cny"], 0.02, "%s@%s residue" % (r["code"], tier))
            # the face prints own_net_cagr_pct at 4dp, so a re-derivation from the printed
            # inputs can only agree to 5e-5 pp * the filled share; 2e-4 is that bound with room
            near(effective_yield_pct(float(tier), lot_value, r["own_net_cagr_pct"], repo),
                 c["effective_yield_pct"], 2e-4, "%s@%s eff" % (r["code"], tier))
            near(float(tier) * (r["defence"]["mean_pct"] if r["defence"] else float("nan")) / 100.0,
                 c["one_defence_day_cny"], 0.02, "%s@%s defence money" % (r["code"], tier))

    # the bands are imported, not retyped: if the other face changes its ruler, we are stale
    if not (abs(RC.PART_OK - face["ruler"]["open_max_participation"]) < 1e-12
            and abs(RC.PART_THIN - face["ruler"]["thin_max_participation"]) < 1e-12):
        problems.append("ruler bands drifted from repo_capacity_at_size")

    # agreement block must be internally consistent with its own two columns
    a = face["agreement_with_r2040"]
    near(a["rebuilt_cb_etf_net_pct"] - a["published_cb_etf_net_pct"], a["delta_net_pp"], 1e-4, "agreement net delta")
    near(a["rebuilt_defence_mean_pct"] - a["published_defence_mean_pct"], a["delta_defence_pp"], 1e-4,
         "agreement defence delta")
    if "rebuilt_money_net_pct" in a and "published_money_net_pct" in a:
        near(a["rebuilt_money_net_pct"] - a["published_money_net_pct"], a["delta_money_pp"], 1e-4,
             "agreement money delta")

    # verdict must follow from the published rows (not from whatever was typed)
    tickets = [r for r in face["rows"] if r["class"] == "convertible"]
    t_small, t_ticket = str(face["tiers_cny"][0]), str(face["tiers_cny"][1])
    want = []
    if not all(r["unit_check"]["ok"] for r in face["rows"]):
        want = ["UNIT_SUSPECT"]
    else:
        if all(r["capacity"][t_ticket]["class"] == "OPEN" for r in tickets):
            want.append("SHELF_ABSORBS_THE_WHOLE_CASH_LEG")
        elif sum((r["max_open_order_cny"] or 0.0) for r in tickets) >= face["ticket_cash_cny"] \
                and all((r["max_open_order_cny"] or 0.0) > 0 for r in tickets):
            want.append("SHELF_ABSORBS_THE_CASH_LEG_IN_TWO_ORDERS")
        elif any(r["capacity"][t_small]["class"] == "OPEN" for r in tickets):
            want.append("SHELF_ABSORBS_ONLY_A_SLICE")
        else:
            want.append("SHELF_IS_SHUT_AT_OUR_SIZE")
        if all(abs(r["capacity"][t_ticket]["yield_drag_bp"]) < 1.0 for r in tickets):
            want.append("THE_LOT_COSTS_UNDER_ONE_BP")
        best = max(tickets, key=lambda r: r["capacity"][t_ticket]["extra_vs_repo_pp"] or -9e9)
        yrs = best["capacity"][t_ticket]["years_of_extra_per_defence_day"]
        if yrs is not None and yrs >= 1.0:
            want.append("ONE_DEFENCE_DAY_OUTWEIGHS_THE_YEAR")
        comps = [r for r in face["rows"] if r["class"] in ("money", "bond")]
        if comps and all(r["own_net_cagr_pct"] < repo for r in comps):
            want.append("THE_COMPARATORS_PAY_LESS_THAN_THE_REPO")
    if want != face["verdict"]:
        problems.append("verdict does not follow from the rows: %s vs %s" % (want, face["verdict"]))

    for v in face["verdict"]:
        if v not in md:
            problems.append("page missing verdict token: %s" % v)
    if "坏日子" not in md or "一手" not in md:
        problems.append("page missing the ruler / lot sentence")
    # two numbers that belong in one sentence must not swap slots (E-20261122 class)
    money_row = [r for r in face["rows"] if r["label"] == "money_etf"][0]
    cb_row = max([r for r in face["rows"] if r["class"] == "convertible"],
                 key=lambda r: r["max_open_order_cny"] or 0)
    want_sentence = ("停在货币 ETF 上留 %s%% 的零头，停在转债上只留 %s%%"
                     % (_fmt(money_row["capacity"][t_small]["residue_bp"] / 100.0, 2),
                        _fmt(cb_row["capacity"][t_small]["residue_bp"] / 100.0, 2)))
    if want_sentence not in md:
        problems.append("page swaps or drops the two residue percentages: %s" % want_sentence)

    want_sha = _content_sha({k: v for k, v in face.items()
                             if k not in ("content_sha256", "elapsed_sec", "generated")})
    if want_sha != face.get("content_sha256"):
        problems.append("content_sha256 mismatch")

    if problems:
        for p in problems:
            print("CHECK FAILED:", p)
        return 3
    print("CHECK OK", face["artifact"], face["evidence_cutoff"], "|", " ".join(face["verdict"]))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    errs = []
    legs = [0]

    def chk(cond, msg):
        legs[0] += 1
        if not cond:
            errs.append(msg)

    # 1. the two faces must use one ruler
    chk(abs(RC.PART_OK - 0.01) < 1e-12, "repo capacity face changed its OPEN band")
    chk(abs(RC.PART_THIN - 0.10) < 1e-12, "repo capacity face changed its THIN band")
    chk(RC.part_class(1e5, 1e7)[0] == "OPEN", "imported bands must still call 1% OPEN")

    # 2. lot arithmetic
    lots, residue, bp = lot_split(250_000.0, 1_158.9)
    chk(lots == 215, "250k / 1158.9 must fit 215 lots, got %d" % lots)
    chk(abs(residue - (250_000.0 - 215 * 1_158.9)) < 1e-6, "residue must be size - lots*lot")
    chk(abs(residue + lots * 1_158.9 - 250_000.0) < 1e-6, "lots*lot + residue must reconstruct size")
    chk(abs(bp - residue / 250_000.0 * 1e4) < 1e-9, "residue bp must be residue/size")
    chk(lot_split(500.0, 1_158.9)[0] == 0, "a sleeve smaller than one lot buys zero lots")
    chk(lot_split(999.0, 1_158.9)[1] == 999.0, "an unfillable sleeve leaves all of it stranded")

    # 3. effective yield: residue priced at repo, never at the shelf's own rate
    eff = effective_yield_pct(250_000.0, 1_158.9, 5.0, 1.0)
    chk(eff < 5.0, "the residue must drag the effective yield below the shelf's own")
    chk(eff > 1.0, "the filled part must lift it above the repo leg")
    chk(abs(effective_yield_pct(1_158.9, 1_158.9, 5.0, 1.0) - 5.0) < 1e-9,
        "exactly one lot with no residue must earn the shelf's own yield")
    chk(abs(effective_yield_pct(100.0, 1_158.9, 5.0, 1.0) - 1.0) < 1e-9,
        "too small to buy a lot must earn the repo rate")

    # 4. round trip and payback
    chk(abs(round_trip_bp() - 4.0) < 1e-12, "round trip must be 2bp/side")
    chk(abs(payback_years(0.1) - 0.4) < 1e-9, "4bp cost against 0.1pp extra must pay back in 0.4y")
    chk(payback_years(-0.1) is None, "a shelf that pays nothing cannot pay back a round trip")

    # 5. years per defence day
    chk(abs(years_per_defence_day(-0.665, 0.067) - 9.925) < 0.01, "0.665 / 0.067 is ~9.9 years")
    chk(years_per_defence_day(-0.665, 0.0) is None, "no extra means no ratio to print")
    chk(years_per_defence_day(0.5, 0.067) == abs(0.5 / 0.067), "a positive defence mean is still a size")

    # 6. buy-and-hold charges one round trip and nothing else
    idx = pd.bdate_range("2021-01-01", periods=120)
    px = pd.Series(10.0 * 1.001 ** np.arange(120), index=idx)
    r = buy_hold_rets(px, "2021-01-01", "2099-01-01")
    chk(abs(float((1 + r).prod()) - (1.0 + 0.001 - 0.0004) * (1.001 ** 118)) < 1e-9,
        "buy and hold must charge exactly one round trip on the entry bar")
    chk(len(r) == 119, "returns length must be bars-1")

    # 7. verdict rules, positive and negative (a rule that cannot fail is not a rule)
    def row(label, klass, cls_at, drag, extra, yrs, cagr=2.0, unit=True):
        cap = {}
        for tier in TIERS:
            cap[str(tier)] = {"class": cls_at.get(str(tier), "THIN"), "yield_drag_bp": drag,
                              "extra_vs_repo_pp": extra, "years_of_extra_per_defence_day": yrs}
        return {"code": label, "label": label, "class": klass, "capacity": cap,
                "own_net_cagr_pct": cagr, "unit_check": {"ok": unit}}

    def verdict_of(rows):
        out = []
        if not all(r["unit_check"]["ok"] for r in rows):
            return ["UNIT_SUSPECT"]
        tk = [r for r in rows if r["class"] == "convertible"]
        if all(r["capacity"][str(TIERS[1])]["class"] == "OPEN" for r in tk):
            out.append("SHELF_ABSORBS_THE_WHOLE_CASH_LEG")
        elif sum((r.get("max_open_order_cny") or 0.0) for r in tk) >= 565_246 \
                and all((r.get("max_open_order_cny") or 0.0) > 0 for r in tk):
            out.append("SHELF_ABSORBS_THE_CASH_LEG_IN_TWO_ORDERS")
        elif any(r["capacity"][str(TIERS[0])]["class"] == "OPEN" for r in tk):
            out.append("SHELF_ABSORBS_ONLY_A_SLICE")
        else:
            out.append("SHELF_IS_SHUT_AT_OUR_SIZE")
        if all(abs(r["capacity"][str(TIERS[1])]["yield_drag_bp"]) < 1.0 for r in tk):
            out.append("THE_LOT_COSTS_UNDER_ONE_BP")
        yrs = max((r["capacity"][str(TIERS[1])]["years_of_extra_per_defence_day"] or -9e9) for r in tk)
        if yrs >= 1.0:
            out.append("ONE_DEFENCE_DAY_OUTWEIGHS_THE_YEAR")
        comps = [r for r in rows if r["class"] in ("money", "bond")]
        if comps and all(r["own_net_cagr_pct"] < 1.77 for r in comps):
            out.append("THE_COMPARATORS_PAY_LESS_THAN_THE_REPO")
        return out

    allopen = row("A", "convertible", {str(TIERS[0]): "OPEN", str(TIERS[1]): "OPEN"}, 0.2, 0.067, 9.9)
    chk(verdict_of([allopen]) == ["SHELF_ABSORBS_THE_WHOLE_CASH_LEG", "THE_LOT_COSTS_UNDER_ONE_BP",
                                 "ONE_DEFENCE_DAY_OUTWEIGHS_THE_YEAR"],
        "all-OPEN shelf must be named as absorbing the cash leg")
    slice_open = row("A", "convertible", {str(TIERS[0]): "OPEN", str(TIERS[1]): "THIN"}, 3.0, 0.067, 0.5)
    chk(verdict_of([slice_open]) == ["SHELF_ABSORBS_ONLY_A_SLICE"],
        "OPEN only at the small tier must be a slice, and a 3bp drag must not be called under one")
    shut = row("A", "convertible", {}, 3.0, -0.5, None)
    chk(verdict_of([shut]) == ["SHELF_IS_SHUT_AT_OUR_SIZE"], "no OPEN tier must be shut")
    two_a = row("A", "convertible", {str(TIERS[0]): "OPEN"}, 0.2, 0.067, 9.9)
    two_a["max_open_order_cny"] = 300_000.0
    two_b = row("B", "convertible", {str(TIERS[0]): "OPEN"}, 0.2, 0.067, 9.9)
    two_b["max_open_order_cny"] = 300_000.0
    chk(verdict_of([two_a, two_b])[0] == "SHELF_ABSORBS_THE_CASH_LEG_IN_TWO_ORDERS",
        "two orders that add up to the ticket must be named as such")
    two_b["max_open_order_cny"] = 200_000.0
    chk(verdict_of([two_a, two_b])[0] == "SHELF_ABSORBS_ONLY_A_SLICE",
        "two orders short of the ticket must fall back to a slice")
    susp = row("A", "convertible", {}, 0.0, 1.0, 0.1, unit=False)
    chk(verdict_of([susp]) == ["UNIT_SUSPECT"], "a bad unit check must stop every capacity claim")
    comp_bad = row("M", "money", {}, 0.0, -0.2, None, cagr=1.5)
    chk("THE_COMPARATORS_PAY_LESS_THAN_THE_REPO" in verdict_of([allopen, comp_bad]),
        "a comparator below the repo must be named")
    comp_ok = row("M", "money", {}, 0.0, 0.3, None, cagr=2.2)
    chk("THE_COMPARATORS_PAY_LESS_THAN_THE_REPO" not in verdict_of([allopen, comp_ok]),
        "a comparator above the repo must not be named")

    if errs:
        for e in errs:
            print("SELFTEST FAIL:", e)
        print("SELFTEST %d/%d FAILED" % (legs[0] - len(errs), legs[0]))
        return 1
    print("SELFTEST OK %d/%d PASS" % (legs[0], legs[0]))
    return 0


# --------------------------------------------------------------------------- main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        return build(write=True)
    if cmd in ("--check", "check"):
        return check()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
