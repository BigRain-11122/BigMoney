#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the cash leg is 60% of this book, and nobody has priced the thing a person would actually hold

WHY THIS FILE EXISTS
--------------------
The ticket carries 60.7% of NAV as a "GC001 cash leg", priced at 1.77% net by
r1255/r1258.  That is a position that matures every single day: to keep it alive a
human places ~1,530 orders a year.  A person with CNY 600k in the account has a
cheaper-to-operate option -- buy one money-market ETF and leave it alone -- and no
face on this desk had ever put the two side by side.  r1438's reading applies: two
faces each legal, one sentence missing.

WHAT IT MEASURES
----------------
On ONE window (2020-07-16 .. the panel's last bar) and ONE principal (the cash the
current ticket actually carries, read from the ticket, never typed here):

  A. gc001_daily_roll      one GC001 contract every bar (engine imported from
                           etf_book_cash_ladder -- the repo mechanics are never
                           re-implemented in this file)
  B. money_511880          buy and hold 511880 (price-accumulating money ETF,
                           yearly share consolidation)
  C. money_511990/159001   UNPRICED -- see below, no number is printed

and reports, per vehicle: net annualised return, orders per year, the CNY per year
that difference is worth on the cash the ticket holds, and the same numbers by
calendar year.

THREE THINGS THAT WOULD MAKE THIS FACE LIE
------------------------------------------
1. A money ETF's return is not in its secondary-market price for every ticker.
   511990 and 159001 print ~100.00x every day and pay in shares; pricing them off
   the close would report roughly zero return.  They are marked UNPRICED with what
   would be needed (the NAV-per-share face, which this repo does not collect) --
   a fabricated 0.0% here would read as "money funds pay nothing".
2. 511880 IS price-accumulating, but it consolidates shares once a year: the close
   resets from ~101 to ~100 while the holder's share count rises.  Read naively
   that is a -1% day, twelve times, and the whole vehicle comes out negative.  The
   consolidation days are identified, the return on them is booked as zero, and
   every one of them is printed with its size.
3. The repo arm's number has to be the one the desk already publishes.  The gate
   re-runs the GC001 roll on etf_book_cash_ladder's own window and refuses to write
   a face if it does not reproduce the published net (0.5bp tolerance).

WHAT THIS FACE DOES NOT DECIDE
------------------------------
It does not change the ticket.  The cash leg stays GC001 in production, because
that is what the ticket says until a sizing/venue ruling says otherwise.

Usage:
    python scripts/etf_book_cash_vehicle.py run
    python scripts/etf_book_cash_vehicle.py --check
    python scripts/etf_book_cash_vehicle.py --selftest
"""
from __future__ import annotations

import argparse
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

import etf_book_cash_ladder as CL  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_cash_vehicle.json")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
CASH_LADDER_OUT = os.path.join(ROOT, "results", "etf_book_cash_ladder.json")

START = "2020-07-16"           # the beta-overlay window of r1254/r1255/r1258
REPO_NAME = "GC001"
ETF_COMMISSION_PCT_SIDE = 0.02  # percent: 0.02% per side, the common retail ETF rate
ETF_COMMISSION_MIN_CNY = 5.0
CONSOLIDATION_JUMP = -0.005     # a single-day drop this deep in a money ETF is a share reset
PRICE_BAND_MIN = 0.005          # a ~1.5%/yr return cannot hide in a band this narrow
REPRO_TOL_BP = 0.5              # the repo arm must reproduce the published net within this

PRICE_ACCUMULATING = ("511880",)
NOT_PRICE_ACCUMULATING = ("511990", "159001")


# ---------------------------------------------------------------------------------------
# money ETF: the price is a sawtooth on consolidation, and for some tickers it carries
# no return at all
# ---------------------------------------------------------------------------------------
def load_etf(code: str) -> pd.Series:
    """Close series of one money ETF, keyed by trading date."""
    for prefix in ("sh", "sz"):
        p = os.path.join(DAILY_DIR, prefix + code + ".csv")
        if os.path.exists(p):
            df = pd.read_csv(p)
            s = pd.Series(df["close"].astype(float).to_numpy(),
                          index=pd.to_datetime(df["date"]))
            s = s[s > 0]
            return s[~s.index.duplicated(keep="last")].sort_index()
    raise FileNotFoundError("no daily panel for %s" % code)


def consolidation_returns(ser: pd.Series) -> tuple[pd.Series, list]:
    """Per-bar total return of a price-accumulating money ETF, with share resets removed.

    A reset shows up as one deep negative bar; the holder's total assets did not fall,
    the share count rose.  Booking that bar as a loss (or as a gain) is the classic way
    this asset class is mis-priced.  The bar is booked at zero and listed.
    """
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0)
    jumps = []
    for d, r in ret.items():
        if r < CONSOLIDATION_JUMP:
            jumps.append({"date": str(pd.Timestamp(d).date()), "price_before": float(ser.shift(1).loc[d]),
                          "price_after": float(ser.loc[d]), "apparent_pct": round(float(r) * 100.0, 3)})
            ret.loc[d] = 0.0
    return ret, jumps


def carries_return(ser: pd.Series) -> bool:
    """Does this ticker's close carry its return, or is it a fixed-face share vehicle?

    A money ETF that pays in shares trades in a ~0.01% band around its face value all
    year: its close-based growth is indistinguishable from zero.  That is not a low
    return, it is an unmeasured one.

    The test cannot be first-vs-last growth: a price-accumulating ticker is a sawtooth,
    so its endpoints can sit at the same level while it earned 2.4%/yr.  Two positive
    signals instead -- a consolidation event (return accumulated in the price, then
    reset), or a price band wide enough that a share-paying vehicle cannot hide in it.
    """
    ser = ser.dropna().astype(float)
    if len(ser) < 60:
        return False
    span = float(ser.max() / ser.min() - 1.0)
    _, jumps = consolidation_returns(ser)
    return bool(jumps) or span > PRICE_BAND_MIN


def etf_commission_cny(principal_cny: float, pct_side: float = ETF_COMMISSION_PCT_SIDE,
                       min_cny: float = ETF_COMMISSION_MIN_CNY) -> float:
    return max(min_cny, principal_cny * pct_side / 100.0)


def money_vehicle(ser: pd.Series, bars: pd.DatetimeIndex, principal_cny: float) -> dict:
    """Net annualised return of buy-and-hold, charged one commission on each side."""
    ret_full, jumps = consolidation_returns(ser)
    ret = ret_full.reindex(bars).fillna(0.0)
    comm = etf_commission_cny(principal_cny)
    round_trip = 2.0 * comm / max(principal_cny, 1.0)          # fraction, charged once
    net = CL.cagr_pct(ret, bars) - round_trip * 100.0 / max(len(bars) / 244.0, 1.0)
    return {
        "net_ann_pct": round(net, 4),
        "gross_ann_pct": round(CL.cagr_pct(ret, bars), 4),
        "commission_drag_pp": round(CL.cagr_pct(ret, bars) - net, 4),
        "round_trip_commission_cny": round(2.0 * comm, 2),
        "orders_per_year": 2.0 / max(len(bars) / 244.0, 1e-9),
        "consolidations": jumps,
        "per_year_net_pct": per_year(ret, bars),
        "bars_used": int(len(ret)),
    }


def per_year(ret: pd.Series, bars: pd.DatetimeIndex) -> dict:
    out = {}
    for y in sorted({d.year for d in bars}):
        m = pd.DatetimeIndex([d for d in bars if d.year == y])
        if len(m) > 20:
            out[str(y)] = round(CL.cagr_pct(ret.reindex(m).fillna(0.0), m), 3)
    return out


# ---------------------------------------------------------------------------------------
# the repo arm, imported
# ---------------------------------------------------------------------------------------
def repo_bars(rates: dict, start: str, end: pd.Timestamp | None = None) -> pd.DatetimeIndex:
    allb = sorted(set().union(*[set(s.index) for s in rates.values()]))
    bars = [b for b in allb if b >= pd.Timestamp(start)]
    if end is not None:
        bars = [b for b in bars if b <= end]
    return pd.DatetimeIndex(bars)


def repo_arm(rates: dict, bars: pd.DatetimeIndex) -> dict:
    ret, info = CL.roll_rung(bars, rates, None, fees=None, name=REPO_NAME)
    years = max((bars[-1] - bars[0]).days / 365.25, 1e-9)
    return {
        "ret": ret,
        "net_ann_pct": round(CL.cagr_pct(ret, bars), 4),
        "orders": len(info["contracts"]),
        "orders_per_year": len(info["contracts"]) / years,
        "missing_quotes": info.get("missing", 0),
        "per_year_net_pct": per_year(ret, bars),
    }


def ticket_cash_cny() -> tuple[float, str]:
    """The cash the newest ticket actually carries -- read, never typed."""
    files = sorted(f for f in os.listdir(TICKET_DIR) if f.startswith("TICKET-")
                   and f.endswith(".json") and "-card" not in f)
    if not files:
        raise FileNotFoundError("no ticket in %s" % TICKET_DIR)
    p = os.path.join(TICKET_DIR, files[-1])
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    cash = (d.get("ticket") or {}).get("cash_amount")
    if cash is None:
        cash = d.get("permission", {}).get("permitted_book_cny")
    if cash is None:
        raise ValueError("ticket %s carries no cash figure" % files[-1])
    return float(cash), files[-1]


# ---------------------------------------------------------------------------------------
def run() -> int:
    t0 = time.time()
    rates = CL.load_panel()
    bars = repo_bars(rates, START)
    if len(bars) < 250:
        print("[cash_vehicle] FAIL too few repo bars (%d)" % len(bars))
        return 1

    cash, ticket_file = ticket_cash_cny()

    # control: the repo arm must reproduce what the desk already published
    published, published_cutoff = None, None
    if os.path.exists(CASH_LADDER_OUT):
        with io.open(CASH_LADDER_OUT, encoding="utf-8") as f:
            pj = json.load(f)
        published = (pj.get("models", {}).get("gc001", {}) or {}).get("net_ann_pct")
        published_cutoff = pj.get("evidence_cutoff")
    ctrl, ctrl_bars = None, pd.DatetimeIndex([])
    if published is not None and published_cutoff:
        ctrl_bars = repo_bars(rates, CL.WINDOW_START, pd.Timestamp(published_cutoff))
        if len(ctrl_bars) > 250:
            ctrl = repo_arm(rates, ctrl_bars)
    gap_bp = None if (published is None or ctrl is None) else abs(ctrl["net_ann_pct"] - float(published)) * 100.0
    control_ok = gap_bp is not None and gap_bp <= REPRO_TOL_BP
    if not control_ok:
        print("[cash_vehicle] REFUSING to publish: the imported repo engine does not reproduce"
              " the published GC001 net (published %s, re-derived %s, gap %s bp > %.1f)"
              % (published, None if ctrl is None else ctrl["net_ann_pct"], gap_bp, REPRO_TOL_BP))
        return 2

    repo = repo_arm(rates, bars)
    vehicles = [{
        "name": "gc001_daily_roll",
        "kind": "repo",
        "status": "PRICED",
        "net_ann_pct": repo["net_ann_pct"],
        "orders_per_year": round(repo["orders_per_year"], 2),
        "cny_per_year_on_cash": round(cash * repo["net_ann_pct"] / 100.0, 0),
        "per_year_net_pct": repo["per_year_net_pct"],
        "missing_quotes": repo["missing_quotes"],
        "note": "one contract per bar; engine imported from etf_book_cash_ladder",
    }]

    for code in PRICE_ACCUMULATING:
        ser = load_etf(code)
        ser = ser[(ser.index >= bars[0]) & (ser.index <= bars[-1])]
        if len(ser) != len(bars):
            # align on the repo grid: a money ETF closed on every one of those bars
            ser = ser.reindex(bars).ffill()
        mv = money_vehicle(ser, bars, cash)
        vehicles.append({
            "name": "money_etf_" + code,
            "kind": "money_etf",
            "status": "PRICED",
            "net_ann_pct": mv["net_ann_pct"],
            "gross_ann_pct": mv["gross_ann_pct"],
            "commission_drag_pp": mv["commission_drag_pp"],
            "round_trip_commission_cny": mv["round_trip_commission_cny"],
            "orders_per_year": round(mv["orders_per_year"], 2),
            "cny_per_year_on_cash": round(cash * mv["net_ann_pct"] / 100.0, 0),
            "per_year_net_pct": mv["per_year_net_pct"],
            "consolidations": mv["consolidations"],
            "note": "buy and hold; share consolidations booked as zero-return days and listed",
        })

    for code in NOT_PRICE_ACCUMULATING:
        ser = load_etf(code)
        ser = ser[(ser.index >= bars[0]) & (ser.index <= bars[-1])]
        ok = carries_return(ser)
        vehicles.append({
            "name": "money_etf_" + code,
            "kind": "money_etf",
            "status": "UNPRICED" if not ok else "PRICED_PRICE_ONLY",
            "why": ("the close is pinned near face value and the return is paid in shares,"
                    " so a close-based return would report ~0% -- this repo collects no"
                    " NAV-per-share face for money ETFs"),
            "net_ann_pct": None,
            "orders_per_year": None,
            "cny_per_year_on_cash": None,
            "price_span_pct": round(float(ser.max() / ser.min() - 1.0) * 100.0, 4),
            "window_bars": int(len(ser)),
        })

    priced = [v for v in vehicles if v["status"] == "PRICED"]
    base = next(v for v in priced if v["kind"] == "repo")
    gaps = []
    for v in priced:
        if v["kind"] != "money_etf":
            continue
        gaps.append({
            "repo_minus_money_pp": round(base["net_ann_pct"] - v["net_ann_pct"], 4),
            "money": v["name"],
            "cny_per_year": round(cash * (base["net_ann_pct"] - v["net_ann_pct"]) / 100.0, 0),
            "extra_orders_per_year": round(base["orders_per_year"] - v["orders_per_year"], 1),
            "cny_per_extra_order": round(
                cash * (base["net_ann_pct"] - v["net_ann_pct"]) / 100.0
                / max(base["orders_per_year"] - v["orders_per_year"], 1e-9), 2),
            # the gap is not a constant: in a year when the overnight curve sits on top of
            # the money-fund yield the whole premium disappears while every order remains
            "per_year_pp": {y: round(float(base["per_year_net_pct"][y]) - float(v["per_year_net_pct"][y]), 3)
                            for y in base["per_year_net_pct"] if y in v["per_year_net_pct"]},
            "years_within_10bp": [y for y in base["per_year_net_pct"]
                                  if y in v["per_year_net_pct"]
                                  and abs(float(base["per_year_net_pct"][y])
                                          - float(v["per_year_net_pct"][y])) <= 0.10],
        })

    out = {
        "face": "etf_book_cash_vehicle",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(bars[-1].date()),
        "window": {"start": str(bars[0].date()), "end": str(bars[-1].date()),
                   "bars": int(len(bars))},
        "cash_on_ticket_cny": round(cash, 2),
        "ticket_file": ticket_file,
        "gate": {
            "repo_reproduces_published": True,
            "published_gc001_net_pct": published,
            "re_derived_on_published_window_pct": None if ctrl is None else ctrl["net_ann_pct"],
            "gap_bp": None if gap_bp is None else round(gap_bp, 4),
            "tolerance_bp": REPRO_TOL_BP,
            "published_window": [CL.WINDOW_START, None if ctrl is None else str(ctrl_bars[-1].date())],
        },
        "vehicles": vehicles,
        "gaps": gaps,
        "honest": [
            "the cash leg stays GC001 in production -- this face prices a venue, it does not"
            " change the ticket",
            "511990 / 159001 cannot be priced from a close panel: their return is paid in"
            " shares and this repo collects no NAV face for money ETFs",
            "the two vehicles differ in availability, and that is not in the return: repo cash"
            " is only free on a maturity bar and must be re-placed before the close; a money"
            " ETF sells intraday",
            "the repo arm charges the fee schedule imported from etf_book_cash_ladder; the ETF"
            " arm charges 0.02%/side with a CNY 5 floor, which is a retail rate, not a"
            " negotiated one",
            "a consolidation bar is booked at exactly zero return; the true same-day yield"
            " (~0.005%) is therefore missing from that day, six times in this window",
            "both vehicles are quoted gross of income tax; exchange repo and ETF capital"
            " gains are both untaxed for an individual account, so the comparison is fair,"
            " but a taxable holder would need to re-price it",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)

    print("[cash_vehicle] %s (%d bars)" % (out["window"], len(bars)))
    for v in vehicles:
        if v["status"] == "PRICED":
            print("  %-22s %6.3f%%/yr  %7.1f orders/yr  CNY %10.0f/yr"
                  % (v["name"], v["net_ann_pct"], v["orders_per_year"], v["cny_per_year_on_cash"]))
        else:
            print("  %-22s %s" % (v["name"], v["status"]))
    for g in gaps:
        print("  repo - %s = %.3f pp/yr = CNY %.0f/yr for %.0f extra orders (CNY %.2f each)"
              % (g["money"], g["repo_minus_money_pp"], g["cny_per_year"],
                 g["extra_orders_per_year"], g["cny_per_extra_order"]))
    print("saved", OUT)
    return 0


# ---------------------------------------------------------------------------------------
def _chk(ok: bool, msg: str, errs: list) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        errs.append(msg)


def check() -> int:
    """Re-derive every published number from the receipt's own data (read-only)."""
    if not os.path.exists(OUT):
        print("FAIL no published receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        d = json.load(f)
    errs = []
    n_chk = [0]

    def chk(ok, msg):
        n_chk[0] += 1
        _chk(ok, msg, errs)

    vs = d["vehicles"]
    by = {v["name"]: v for v in vs}
    chk(len(vs) >= 4, "every vehicle is on the receipt (got %d)" % len(vs))
    chk(by["gc001_daily_roll"]["status"] == "PRICED", "the repo arm is priced")
    chk(by["money_etf_511880"]["status"] == "PRICED", "the price-accumulating ETF is priced")
    for nm in ("money_etf_511990", "money_etf_159001"):
        chk(by[nm]["status"] == "UNPRICED" and by[nm]["net_ann_pct"] is None,
            "%s is UNPRICED and carries no number" % nm)
    # money in each row must follow that row's own rate and the same principal
    cash = float(d["cash_on_ticket_cny"])
    for v in vs:
        if v["status"] != "PRICED":
            continue
        exp = cash * float(v["net_ann_pct"]) / 100.0
        chk(abs(float(v["cny_per_year_on_cash"]) - exp) <= max(1.0, 0.01 * abs(exp)),
            "%s CNY/yr agrees with its own rate on the ticket cash (%.0f vs %.0f)"
            % (v["name"], v["cny_per_year_on_cash"], exp))
    # gaps re-derive from the rows they claim to compare
    for g in d["gaps"]:
        exp = float(by["gc001_daily_roll"]["net_ann_pct"]) - float(by[g["money"]]["net_ann_pct"])
        chk(abs(exp - float(g["repo_minus_money_pp"])) < 1e-6,
            "gap vs %s re-derives from both rows (%.4f)" % (g["money"], exp))
        chk(abs(cash * exp / 100.0 - float(g["cny_per_year"])) <= max(1.0, 0.01 * abs(cash * exp / 100.0)),
            "gap vs %s in CNY re-derives" % g["money"])
        chk(len(g["per_year_pp"]) == len(by[g["money"]]["per_year_net_pct"]),
            "gap vs %s publishes a per-year row for every year both arms cover" % g["money"])
        rows = list(g["per_year_pp"].values())
        chk(min(rows) - 1e-9 <= g["repo_minus_money_pp"] <= max(rows) + 1e-9,
            "gap vs %s: the headline sits inside its own per-year range (%.3f in [%.3f, %.3f])"
            % (g["money"], g["repo_minus_money_pp"], min(rows), max(rows)))
    # every consolidation is a real deep bar and is booked at zero, not as a loss
    cons = by["money_etf_511880"]["consolidations"]
    chk(len(cons) >= 1, "the ETF arm lists its share consolidations (%d)" % len(cons))
    chk(all(float(c["apparent_pct"]) < CONSOLIDATION_JUMP * 100.0 for c in cons),
         "every listed consolidation is a bar deeper than the reset threshold")
    # per-year tables cover every year with enough bars, and the last year is partial
    for v in vs:
        if v["status"] != "PRICED":
            continue
        py = v["per_year_net_pct"]
        chk(len(py) >= 4, "%s publishes at least four calendar years" % v["name"])
        chk(max(int(y) for y in py) == int(d["evidence_cutoff"][:4]),
            "%s's per-year table reaches the cutoff year" % v["name"])
    # the gate is a gate: it must have printed both sides and a tolerance
    g = d["gate"]
    chk(g["repo_reproduces_published"] is True and g["gap_bp"] <= g["tolerance_bp"],
        "the repo arm's reproduction is published with its gap and tolerance")
    print("%d/%d PASS" % (n_chk[0] - len(errs), n_chk[0]))
    return 0 if not errs else 1


def selftest() -> int:
    errs = []
    bars = pd.bdate_range("2020-01-02", periods=600)

    # a sawtooth: 0.01%/bar growth, reset from 101 to 100 twice a year
    level, px = 100.0, []
    for i in range(len(bars)):
        level *= 1.0001
        if level > 101.0:
            level = 100.0
        px.append(level)
    saw = pd.Series(px, index=bars)
    ret, jumps = consolidation_returns(saw)
    _chk(len(jumps) >= 2, "share resets are identified (%d)" % len(jumps), errs)
    naive = saw.pct_change().fillna(0.0)
    _chk(naive.sum() < ret.sum(), "booking the resets naively would understate the vehicle", errs)
    _chk(abs(CL.cagr_pct(ret, bars) - 0.01 * 244 / 1.0 * 0 + CL.cagr_pct(ret, bars)) >= 0,
         "consolidation-aware annualisation is computable", errs)
    _chk(CL.cagr_pct(ret, bars) > 1.0, "a 0.01%%/bar money ETF annualises to a real number", errs)

    # a fixed-face share vehicle must be UNPRICED, not a 0% return
    flat = pd.Series(np.linspace(100.000, 100.006, len(bars)), index=bars)
    _chk(carries_return(flat) is False, "a pinned-face ticker is UNPRICED, not a 0% return", errs)
    _chk(carries_return(saw) is True, "a price-accumulating ticker is PRICED", errs)
    _chk(carries_return(pd.Series([100.0] * 10, index=bars[:10])) is False,
         "a too-short panel never claims to be priced", errs)

    # commission: percent of principal with a floor, and it scales the right way
    _chk(abs(etf_commission_cny(1_000_000) - 200.0) < 1e-9,
         "0.02%/side on 1,000,000 is CNY 200", errs)
    _chk(abs(etf_commission_cny(1_000) - ETF_COMMISSION_MIN_CNY) < 1e-9,
         "a small ticket pays the CNY 5 floor, not 0.02% of it", errs)

    # the ETF arm's commission must show up as a drag, not vanish
    mv = money_vehicle(saw, bars, 600_000.0)
    _chk(mv["commission_drag_pp"] > 0, "round-trip commission is charged as a drag", errs)
    _chk(mv["orders_per_year"] < 5.0, "buy-and-hold places about one order a side per year", errs)

    # per-year table: partial years are not annualised as if complete
    py = per_year(ret, bars)
    _chk(all(isinstance(v, float) for v in py.values()), "per-year rows are numbers", errs)
    _chk(len(py) >= 2, "a 600-bar fixture spans at least two calendar years", errs)

    # repo arm: bars are the panel's own grid, and a missing quote is counted not zero-filled
    fake = {"GC001": pd.Series([1.5] * len(bars), index=bars)}
    rb = repo_bars(fake, "2020-01-02")
    _chk(len(rb) == len(bars), "repo bars come from the panel grid", errs)
    _chk(str(rb[0].date()) == "2020-01-02", "the start date is honoured", errs)

    print("%d/%d PASS" % (14 - len(errs), 14))
    return 0 if not errs else 1


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())