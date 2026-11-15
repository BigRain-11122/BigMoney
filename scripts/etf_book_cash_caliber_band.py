"""Does the cash ticket's 1bp "same caliber" band ever fire, and what is the 50.81bp gap made of?

r1718 put the desk's already-published 1.77%/yr net roll beside one session's GC001 quote
(1.26% on 2026-11-13) and printed the -50.81bp difference, refusing to add them.  Its own
pointer said the remaining question was the band: "within 1bp the line reads 'same caliber'"
is a frozen constant, never measured -- if GC001 keeps trading far from the window mean, the
sentence is the standing answer and the reader is being told "two faces disagree" every day
whether or not anything is wrong.

Two measurements, both on the published face's own window (no new panel, no new estimator):

  A. REACHABILITY.  For every bar of the window, gap = (that bar's GC001 close - the window's
     own rate), in bp.  The share of bars inside the frozen 1bp band says whether the
     "same caliber" branch is a state the page can ever reach, or dead code.  The |gap|
     percentiles say what band would cover half / nine tenths of the days.

  B. COMPOSITION.  The printed -50.81bp is a GROSS quote against a NET roll.  The vehicle
     charges 0.1bp per contract per day (etf_book_cash_ladder.FEE_BP[1]), so part of that
     gap is the commission, not the market.  Split it: commission = net - gross on the same
     window; rate difference = today's quote - the window's gross.  Both printed, and the
     two are never added into one "the market pays less" story -- only the split is stated.

Frozen reading rule (written before the run, r1325 adoption discipline):

  * C0 control: the recomputed net on the published window must reproduce
    results/etf_book_idle_cash.json's own `cash_vehicle_net_pct_on_window` to 0.5bp.
    Failing that this face says REFUSE -- the composition, not the band, is what moved.
  * band_share (gross basis) >= REACH_SHARE -> `CALIBER_BAND_REACHABLE`,
    else `CALIBER_BAND_IS_DECORATIVE`.  The gross basis is the like-for-like one: the quote
    is gross, so a band meant to detect "the same caliber" must be read against gross.
  * commission share of the printed gap >= FEE_SHARE -> `PRINTED_GAP_IS_PARTLY_A_FEE`.
  * a missing quote or an unreadable face prints None and the word "cannot verify";
    it never prints 0 (a zero gap would read as "they agree").
"""

from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import etf_book_cash_ladder as CL  # noqa: E402
import etf_book_cash_vehicle as V  # noqa: E402

ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(RESULTS, "etf_book_cash_caliber_band.json")
IDLE_JSON = os.path.join(RESULTS, "etf_book_idle_cash.json")

BAND_BP = 1.0          # the frozen "same caliber" band the ticket already carries
REACH_SHARE = 0.05     # below this the branch is decorative, not a reading
FEE_SHARE = 0.20       # above this the printed gap is partly the commission
REPRO_TOL_BP = 0.5

CRITERIA = {
    "C0_control": "net recomputed on the published window reproduces "
                  "etf_book_idle_cash.cash_vehicle_net_pct_on_window to 0.5bp",
    "band_basis": "gross -- the quote is gross, so the band must be read on the same side",
    "band_reach_min_share": REACH_SHARE,
    "fee_share_of_printed_gap": FEE_SHARE,
    "unreadable": "missing quote or unreadable face prints None and 'cannot verify', never 0",
    "split_only": "commission and rate difference are printed side by side; they are never "
                  "added into a single 'the market pays less' number",
}


# ---------------------------------------------------------------------------------------
# pure pieces (the selftest holds these)
# ---------------------------------------------------------------------------------------
def band_stats(gaps_bp, band_bp=BAND_BP):
    """How often |gap| sits inside `band_bp`, and what band would cover half / nine tenths.

    An empty or all-NaN series returns None fields -- an unread sample is not a narrow band.
    """
    g = pd.Series(list(gaps_bp), dtype="float64")
    g = g.replace([np.inf, -np.inf], np.nan).dropna()
    if not len(g):
        return {"bars": 0, "share_within_band_pct": None, "median_abs_gap_bp": None,
                "p10_abs_gap_bp": None, "p90_abs_gap_bp": None,
                "band_covering_50pct_bp": None, "band_covering_90pct_bp": None,
                "share_within_band_pct_basis": None}
    a = g.abs()
    return {
        "bars": int(len(a)),
        "share_within_band_pct": round(float((a <= band_bp).mean()) * 100.0, 3),
        "median_abs_gap_bp": round(float(a.median()), 3),
        "p10_abs_gap_bp": round(float(a.quantile(0.10)), 3),
        "p90_abs_gap_bp": round(float(a.quantile(0.90)), 3),
        "band_covering_50pct_bp": round(float(a.quantile(0.50)), 3),
        "band_covering_90pct_bp": round(float(a.quantile(0.90)), 3),
        "mean_signed_gap_bp": round(float(g.mean()), 3),
    }


def split_gap(quote_pct, gross_pct, net_pct):
    """Break the printed gap into a rate part and a commission part, never a merged total.

    quote_pct = one session's quoted close (gross).
    gross_pct / net_pct = the same window's annualised roll before / after commission.
    Returns parts in bp plus `merged: False` -- adding the two produces one number whose
    cause is unattributable, which is exactly the reading this face refuses to publish.
    """
    if quote_pct is None or gross_pct is None or net_pct is None:
        return {"readable": False, "why": "a side is missing -- cannot verify"}
    total = (float(quote_pct) - float(net_pct)) * 100.0
    fee = (float(gross_pct) - float(net_pct)) * 100.0
    rate = (float(quote_pct) - float(gross_pct)) * 100.0
    return {
        "readable": True,
        "total_vs_net_bp": round(total, 3),
        "commission_bp": round(fee, 3),
        "rate_difference_vs_gross_bp": round(rate, 3),
        "recombines": bool(abs((fee + rate) - total) <= 1e-6),
        "commission_share_of_total_pct": None if abs(total) < 1e-9
        else round(abs(fee) / abs(total) * 100.0, 2),
        "merged": False,
        "rule": "两个部分分别印，不相加：一个是车辆成本，一个是利率差",
    }


def verdict_of(readings, criteria=None):
    """Derived from the readings, never typed."""
    c = dict(CRITERIA if criteria is None else criteria)
    c0 = readings.get("control_error_bp")
    c0_ok = bool(c0 is not None and float(c0) <= REPRO_TOL_BP)
    share = readings.get("band", {}).get("share_within_band_pct")
    fee_share = (readings.get("split") or {}).get("commission_share_of_total_pct")
    band_verdict = "UNREADABLE" if share is None else (
        "CALIBER_BAND_REACHABLE" if float(share) / 100.0 >= c["band_reach_min_share"]
        else "CALIBER_BAND_IS_DECORATIVE")
    fee_verdict = "UNREADABLE" if fee_share is None else (
        "PRINTED_GAP_IS_PARTLY_A_FEE" if float(fee_share) / 100.0 >= c["fee_share_of_printed_gap"]
        else "PRINTED_GAP_IS_A_RATE_DIFFERENCE")
    gates = {"C0_control": c0_ok, "band_basis_gross_available": share is not None,
             "split_readable": bool((readings.get("split") or {}).get("readable"))}
    if not gates["C0_control"]:
        return "REFUSE", band_verdict, fee_verdict, gates
    return band_verdict, band_verdict, fee_verdict, gates


# ---------------------------------------------------------------------------------------
def published_window(path=IDLE_JSON):
    """(start, end, published net) off the face that already prices this cash."""
    if not os.path.exists(path):
        return None, None, None
    with io.open(path, encoding="utf-8") as f:
        p = json.load(f)
    w = p.get("window") or {}
    return w.get("start"), w.get("end"), (p.get("readings") or {}).get(
        "cash_vehicle_net_pct_on_window")


def run():
    import time
    t0 = time.time()
    start, end, published_net = published_window()
    if not (start and end and published_net is not None):
        payload = {"face": "etf_book_cash_caliber_band", "verdict": "REFUSE",
                   "why": "results/etf_book_idle_cash.json missing window or published net"}
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print(json.dumps(payload, ensure_ascii=False), flush=True)
        return 2

    rates = CL.load_panel()
    bars = V.repo_bars(rates, start, pd.Timestamp(end))
    print("repo bars %s..%s n=%d" % (bars[0].date(), bars[-1].date(), len(bars)), flush=True)

    ret_net, info = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
    net_pct = CL.cagr_pct(ret_net, bars)
    ret_gross, _ = CL.roll_rung(bars, rates, None, fees={}, name="GC001")
    gross_pct = CL.cagr_pct(ret_gross, bars)
    ctrl_err = abs(net_pct - float(published_net)) * 100.0
    print("net %.4f%% (published %.4f%%, err %.3fbp) gross %.4f%% fee drag %.3fbp"
          % (net_pct, float(published_net), ctrl_err, gross_pct, (gross_pct - net_pct) * 100.0),
          flush=True)

    quotes = rates["GC001"].reindex(bars).ffill()
    live = quotes.dropna()
    gap_gross = (live - gross_pct) * 100.0
    gap_net = (live - net_pct) * 100.0

    band_gross = band_stats(gap_gross)
    band_net = band_stats(gap_net)
    tail = gap_gross.tail(60)
    band_tail = band_stats(tail)

    # the ticket's own session: the last bar of the window
    quote_date = str(live.index[-1].date())
    quote_pct = float(live.iloc[-1])
    split = split_gap(quote_pct, gross_pct, net_pct)

    readings = {
        "window_net_pct": round(net_pct, 4),
        "published_net_pct": float(published_net),
        "control_error_bp": round(ctrl_err, 4),
        "window_gross_pct": round(gross_pct, 4),
        "commission_drag_pp": round(gross_pct - net_pct, 4),
        "quote_pct": round(quote_pct, 4),
        "quote_date": quote_date,
        "band": band_gross,
        "band_net_basis": band_net,
        "band_last_60_bars": band_tail,
        "split": split,
    }
    band_verdict, _, fee_verdict, gates = verdict_of(readings)
    verdict = band_verdict if band_verdict != "REFUSE" else "REFUSE"

    payload = {
        "face": "etf_book_cash_caliber_band",
        "asof": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(bars[-1].date()),
        "window": {"start": str(bars[0].date()), "end": str(bars[-1].date()),
                   "bars": int(len(bars))},
        "question": "the ticket prints -50.81bp between one session's quote and a net window "
                    "roll, and calls them 'same caliber' within 1bp -- is that band a state "
                    "the page can reach, and what is the gap made of?",
        "criteria_frozen": CRITERIA,
        "readings": readings,
        "gates": gates,
        "verdict": verdict,
        "fee_verdict": fee_verdict,
        "band_bp": BAND_BP,
        "honest": [
            "the band is measured against a FIXED reference (the window's own rate); a real "
            "forward ticket would compare against a trailing window that moves, which would "
            "narrow the daily gap for a drifting rate regime and is not measured here",
            "the quote is one session's close, gross; the reference is the same window's roll, "
            "so the rate part is like-for-like and the commission part is the vehicle's own "
            "fee schedule, not a broker bill",
            "the 1bp band is a frozen constant in the ticket; this face measures how often the "
            "asset reaches it, it does not change the ticket",
            "%d repo bars, %d missing quotes on the window" % (len(bars), info.get("missing", 0)),
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": verdict, "fee_verdict": fee_verdict,
                      "share_in_band_pct": band_gross["share_within_band_pct"],
                      "median_abs_bp": band_gross["median_abs_gap_bp"],
                      "band_50": band_gross["band_covering_50pct_bp"],
                      "band_90": band_gross["band_covering_90pct_bp"],
                      "split": split}, ensure_ascii=False), flush=True)
    print("saved", OUT, flush=True)
    return 0 if verdict in ("CALIBER_BAND_REACHABLE", "CALIBER_BAND_IS_DECORATIVE") else 2


# ---------------------------------------------------------------------------------------
def selftest():
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)
            print("FAIL", msg, flush=True)

    # L1 a quote series that sits exactly on the reference is inside the band every day
    flat = band_stats([0.0] * 250)
    chk(flat["share_within_band_pct"] == 100.0 and flat["band_covering_50pct_bp"] == 0.0,
        "L1 a quote on the reference is inside the band every day")

    # L2 a constant 10bp offset never enters a 1bp band, and the band that covers half is 10
    off = band_stats([10.0] * 250)
    chk(off["share_within_band_pct"] == 0.0 and abs(off["band_covering_50pct_bp"] - 10.0) < 1e-9,
        "L2 a 10bp offset never enters the 1bp band")

    # L3 the percentiles are ordered: the 90% band cannot be narrower than the 50% band
    mixed = band_stats(np.linspace(-40.0, 40.0, 401))
    chk(mixed["band_covering_90pct_bp"] >= mixed["band_covering_50pct_bp"],
        "L3 the 90% band is not narrower than the 50% band")

    # L4 an unread sample is None, not a narrow band
    empty = band_stats([])
    nan = band_stats([np.nan, np.inf, -np.inf])
    chk(empty["share_within_band_pct"] is None and empty["bars"] == 0,
        "L4a an empty sample does not read as a narrow band")
    chk(nan["share_within_band_pct"] is None, "L4b a NaN/inf sample does not read as agreement")

    # L5 the split recombines exactly and refuses to merge
    s = split_gap(1.265, 2.017, 1.7731)
    chk(s["readable"] and s["recombines"], "L5a the split recombines to the printed gap")
    chk(s["merged"] is False and s["commission_bp"] > 0,
        "L5b commission is a positive part and the two are not merged")
    chk(abs(s["total_vs_net_bp"] - (-50.81)) < 0.02,
        "L5c the published -50.81bp is reproduced from its parts")

    # L6 a missing side prints cannot-verify, never zero
    miss = split_gap(None, 2.0, 1.7)
    chk(miss["readable"] is False and "cannot verify" in miss["why"],
        "L6 a missing side says cannot verify instead of 0bp")

    # L7 the verdict is derived: the share moves the band verdict, the fee share moves the other
    r = {"control_error_bp": 0.1, "band": {"share_within_band_pct": 1.0},
         "split": {"readable": True, "commission_share_of_total_pct": 48.0}}
    v, _, f, _ = verdict_of(r)
    chk(v == "CALIBER_BAND_IS_DECORATIVE", "L7a a 1% in-band share is decorative")
    chk(f == "PRINTED_GAP_IS_PARTLY_A_FEE", "L7b a 48% commission share names the fee")
    r2 = dict(r, band={"share_within_band_pct": 40.0},
              split={"readable": True, "commission_share_of_total_pct": 2.0})
    v2, _, f2, _ = verdict_of(r2)
    chk(v2 == "CALIBER_BAND_REACHABLE" and f2 == "PRINTED_GAP_IS_A_RATE_DIFFERENCE",
        "L7c the opposite readings name the opposite branches")

    # L8 a broken control refuses the whole face before any verdict is read
    r3 = dict(r, control_error_bp=5.0)
    v3, _, _, g3 = verdict_of(r3)
    chk(v3 == "REFUSE" and g3["C0_control"] is False,
        "L8 a control that misses the published net refuses the face")

    # L9 fees={} must actually switch the fee path off (the gross side is a real control)
    f = pd.DatetimeIndex(pd.date_range("2025-01-01", periods=40, freq="B"))
    rf = {"GC001": pd.Series(2.0, index=f)}
    b = V.repo_bars(rf, str(f[0].date()), f[-1])
    r_on, _ = CL.roll_rung(b, rf, None, fees=None, name="GC001")
    r_off, _ = CL.roll_rung(b, rf, None, fees={}, name="GC001")
    chk(float((1.0 + r_off).cumprod().iloc[-1]) > float((1.0 + r_on).cumprod().iloc[-1]),
        "L9 switching the fee off earns strictly more (the gross side is a real control)")

    print("selftest %s" % ("PASS" if not errs else "FAIL %d" % len(errs)), flush=True)
    return 0 if not errs else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run())
