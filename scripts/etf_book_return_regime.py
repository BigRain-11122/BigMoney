"""How much of the published return is cash carry, and what is left if the repo rate falls.

The executable book keeps roughly half its NAV in 1-day repo, and every year it quotes was
earned while GC001 paid about 2.1%/yr on that half. The quote the page shows today is near
1.1%. Nothing on the page separates the two sources, so a cheaper cash leg reads like a bad
month rather than a smaller book -- and the reader cannot tell whether the selection
machinery still pays when parking money stops paying.

This script re-prices the SAME book under three cash regimes and across the beta ladder the
reader can actually choose:

  observed   the GC001 close quoted on each bar (what the ticket already uses)
  flat       today's latest quote held constant over the whole window
  zero       no cash return at all -- what the five names alone pay

Nothing is re-implemented: the leg chain is etf_composite_pf.run_next_open, the overlay is
etf_book_order.k_schedule + etf_phase_beta_target.apply_overlay, the accrual is
etf_phase_beta_window.repo_daily_cash (calendar-gap convention, so "flat" uses the identical
convention with a constant rate), and the statistics are etf_book_order.metrics. Selftest
leg 1 is the identity that makes every other number readable: the base cell must reproduce
the ticket's OWN published headline, not a look-alike.

  python scripts/etf_book_return_regime.py run
  python scripts/etf_book_return_regime.py --selftest

Outputs results/etf_book_return_regime.json.
Exploratory: no preregistration, no verdict on the book, no ledger booking.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS                                        # noqa: E402
from scripts import etf_book_order as O                        # noqa: E402
from scripts import etf_composite_pf as F                      # noqa: E402
from scripts import etf_phase_beta_target as BT                # noqa: E402
from scripts import etf_phase_beta_window as BW                # noqa: E402
from scripts import etf_variants_null_rolling as V             # noqa: E402
from scripts.etf_asset_class import classify                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PATHS.results_dir, "etf_book_return_regime.json")
TICKET_PTR = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")

REBAL = O.REBAL
N_HOLD = O.N_HOLD
COST_BP = O.COST_BP
START = O.DEFAULT_INCEPTION
BASE_BETA = O.DEFAULT_BETA
BETAS = (0.10, 0.20, 0.30, 0.50)
REGIMES = ("observed", "flat_today", "zero")
# a rebuilt cell must land this close to the ticket's own rounded headline (4 decimals)
REPRO_TOL = 5e-4


# ---------------------------------------------------------------- pure helpers
def flat_rf(idx, rate_pct):
    """Constant-rate cash accrual under the SAME calendar-gap convention as the repo leg.

    repo_daily_cash pays rate(prior bar) * gap_days / 365, so a "flat rate" arm is only
    comparable when it uses that convention rather than rate/252 per bar.
    """
    idx = pd.DatetimeIndex(idx)
    out = pd.Series(0.0, index=idx, dtype=float)
    for i in range(1, len(idx)):
        gap = max(int((idx[i] - idx[i - 1]).days), 1)
        out.iloc[i] = float(rate_pct) / 100.0 * gap / 365.0
    return out


def carry_gate(cells, base_beta=BASE_BETA):
    """Read the carry answer off the cells. Pure, so the selftest can pin it.

    `cells` is a list of {beta, regime, cagr_pct, sharpe, maxdd_pct, vol_pct, cash_share}.
    Returns per-beta carry_pp (observed - zero), the flat-rate cost (observed - flat_today),
    a sensitivity in pp per 100bp, and the flags the page is allowed to quote.
    """
    by = {}
    for c in cells:
        by[(round(float(c["beta"]), 4), c["regime"])] = c
    out = {"betas": {}, "flags": {}}
    for (beta, _regime) in sorted(by):
        if beta in out["betas"]:
            continue
        o = by.get((beta, "observed"))
        f = by.get((beta, "flat_today"))
        z = by.get((beta, "zero"))
        if o is None or f is None or z is None:
            out["betas"][beta] = None
            continue
        row = {"observed_pct": o["cagr_pct"], "flat_today_pct": f["cagr_pct"],
               "zero_pct": z["cagr_pct"],
               "carry_pp": round(o["cagr_pct"] - z["cagr_pct"], 3),
               "carry_share_of_headline_pct":
                   (round(100.0 * (o["cagr_pct"] - z["cagr_pct"]) / o["cagr_pct"], 1)
                    if o["cagr_pct"] else None),
               "flat_rate_cost_pp": round(o["cagr_pct"] - f["cagr_pct"], 3),
               "cash_share": o.get("cash_share")}
        if o.get("rate_observed_pct") is not None and o.get("rate_today_pct") is not None:
            d_rate = float(o["rate_observed_pct"]) - float(o["rate_today_pct"])
            if abs(d_rate) > 1e-9:
                # d_rate is already in percentage points, and 1pp of rate = 100bp
                row["pp_per_100bp"] = round(
                    (o["cagr_pct"] - f["cagr_pct"]) / d_rate, 3)
        out["betas"][beta] = row
    base = out["betas"].get(round(float(base_beta), 4))
    # the ordering that makes the three arms readable: paying more on cash cannot pay less
    out["flags"]["observed_ge_flat_ge_zero"] = (
        base is not None
        and base["observed_pct"] >= base["flat_today_pct"] >= base["zero_pct"] - 1e-9)
    out["flags"]["carry_positive"] = base is not None and base["carry_pp"] > 0
    out["flags"]["selection_survives_zero_cash"] = base is not None and base["zero_pct"] > 0
    out["base_beta"] = round(float(base_beta), 4)
    return out


# ---------------------------------------------------------------- live run
def _published():
    if not os.path.exists(TICKET_PTR):
        return None
    with open(TICKET_PTR, encoding="utf-8") as fh:
        ptr = json.load(fh)
    name = ptr.get("file")
    if not name:
        return None
    path = os.path.join(os.path.dirname(TICKET_PTR), os.path.basename(name))
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        tk = json.load(fh)
    book = ((tk.get("metrics") or {}).get("book") or {})
    if book.get("cagr") is None:
        return None
    return {"file": os.path.relpath(path, ROOT), "beta": tk.get("beta_target"),
            "n_hold": tk.get("n_hold"), "cost_bp": tk.get("cost_bp_per_side"),
            "cagr": book.get("cagr"), "sharpe": book.get("sharpe"),
            "maxdd": book.get("maxdd"), "bars": book.get("bars")}


def build():
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ser, turnover, _gapfill = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                              REBAL, n_hold=N_HOLD, cost=F.COST, score=score)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    idx = ser.index.intersection(close[mkt_col].index)
    rp = BT.rets(ser.reindex(idx))
    rm = BT.rets(close[mkt_col].reindex(idx))

    rates = BW.load_repo_rates()
    cash_rf, missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)
    in_win = rates.reindex(idx).dropna() if len(rates) else rates
    rate_observed_pct = (round(float(in_win.mean()), 4) if len(in_win) else None)
    rate_today_pct = (round(float(rates.iloc[-1]), 4) if len(rates) else None)
    rate_today_date = (str(rates.index[-1].date()) if len(rates) else None)

    rfs = {"observed": cash_rf, "zero": pd.Series(0.0, index=idx, dtype=float)}
    if rate_today_pct is None:
        rfs["flat_today"] = pd.Series(0.0, index=idx, dtype=float)
    else:
        rfs["flat_today"] = flat_rf(idx, rate_today_pct)

    start = pd.Timestamp(START)
    cells = []
    for beta in BETAS:
        sched = O.k_schedule(rp, rm, beta)
        k_ser = O.in_force(sched, idx)
        live_k = k_ser.dropna()
        for regime in REGIMES:
            strat, bench, _kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=rfs[regime])
            cell = {"beta": round(float(beta), 4), "regime": regime}
            if strat is None or not len(live_k):
                cell["cagr_pct"] = None
                cells.append(cell)
                continue
            slip = strat[strat.index >= start]
            slip = slip[slip.index >= live_k.index[0]]
            mk = O.metrics(slip, None)["book"]
            if mk is None:
                cell["cagr_pct"] = None
                cells.append(cell)
                continue
            win_k = live_k[live_k.index >= slip.index[0]]
            cell.update({
                "cagr_pct": round(mk["cagr"] * 100, 3),
                "sharpe": mk["sharpe"], "maxdd_pct": round(mk["maxdd"] * 100, 3),
                "vol_pct": round(mk["vol"] * 100, 3), "bars": mk["bars"],
                "first_bar": str(slip.index[0].date()), "last_bar": str(slip.index[-1].date()),
                "cash_share": (round(float((1.0 - win_k).mean()), 4) if len(win_k) else None),
                "rate_observed_pct": rate_observed_pct, "rate_today_pct": rate_today_pct,
            })
            cells.append(cell)

    out = {
        "script": "scripts/etf_book_return_regime.py",
        "evidence_cutoff": str(idx[-1].date()),
        "config": {"rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
                   "start": START, "betas": list(BETAS), "regimes": list(REGIMES),
                   "engine": ("etf_composite_pf.run_next_open + etf_book_order.k_schedule + "
                              "etf_phase_beta_target.apply_overlay + "
                              "etf_phase_beta_window.repo_daily_cash + etf_book_order.metrics")},
        "cash_rates": {"observed_mean_pct": rate_observed_pct,
                       "today_pct": rate_today_pct, "today_date": rate_today_date,
                       "missing_bar_steps": int(missing),
                       "convention": "rate(prior bar) * calendar_gap / 365, identical in all arms"},
        "cells": cells,
        "rate_pp": (round(rate_observed_pct - rate_today_pct, 4)
                    if rate_observed_pct is not None and rate_today_pct is not None else None),
    }
    out["gate"] = carry_gate([c for c in cells if c.get("cagr_pct") is not None])
    pub = _published()
    base = next((c for c in cells
                 if c["beta"] == round(float(BASE_BETA), 4) and c["regime"] == "observed"), None)
    if pub is not None and base is not None and base.get("cagr_pct") is not None:
        recon = round(base["cagr_pct"] / 100.0, 6)
        out["identity"] = {
            "published_file": pub["file"], "published_cagr": pub["cagr"],
            "published_bars": pub["bars"], "rebuilt_cagr": recon,
            "rebuilt_bars": base.get("bars"),
            "matched": bool(abs(recon - float(pub["cagr"])) <= REPRO_TOL
                            and (pub.get("bars") in (None, base.get("bars")))),
            "basis": "base cell (beta 0.20, observed repo) must equal the ticket's own headline",
        }
    else:
        out["identity"] = {"published_file": None, "matched": None,
                           "basis": "no published ticket on disk -- identity leg not evaluated"}
    out["caveats"] = [
        "cash-share is the mean of (1-k) over the printed window, so it moves with the beta ladder",
        "flat_today holds one quote constant for years; the observed arm is what actually happened",
        "survivorship: the panel holds ETFs that still exist",
        "exploratory: no preregistration, no verdict, no ledger booking",
    ]
    return out


def write(obj):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def run():
    obj = build()
    write(obj)
    g = obj["gate"]["betas"].get(obj["gate"]["base_beta"]) or {}
    print("cutoff %s | cash rate observed %.3f%% -> today %.3f%% (%s)"
          % (obj["evidence_cutoff"], obj["cash_rates"]["observed_mean_pct"] or 0.0,
             obj["cash_rates"]["today_pct"] or 0.0, obj["cash_rates"]["today_date"]))
    for beta in sorted(obj["gate"]["betas"], key=float):
        r = obj["gate"]["betas"][beta]
        if not r:
            print("  beta %.2f: incomplete cells" % beta)
            continue
        print("  beta %.2f | observed %.2f%% | today-flat %.2f%% | zero %.2f%% "
              "| carry %.2fpp (%.0f%% of headline) | cash %.0f%%"
              % (beta, r["observed_pct"], r["flat_today_pct"], r["zero_pct"],
                 r["carry_pp"], r["carry_share_of_headline_pct"] or 0.0,
                 100.0 * (r["cash_share"] or 0.0)))
    idy = obj.get("identity") or {}
    print("identity: rebuilt %.4f vs published %s | matched=%s"
          % (idy.get("rebuilt_cagr") or float("nan"), idy.get("published_cagr"),
             idy.get("matched")))
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    if idy.get("matched") is False:
        print("FATAL: rebuilt base cell does not reproduce the published headline", flush=True)
        return 2
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = tot = 0

    def chk(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        print("  [%d/%d] %s" % (ok, tot, name))

    idx = pd.DatetimeIndex(["2026-01-02", "2026-01-05", "2026-01-06"])  # Fri -> Mon -> Tue
    s = flat_rf(idx, 2.0)
    chk("L1 flat accrual uses the calendar-gap convention (2% over a 3-day weekend)",
        s.iloc[0] == 0.0 and abs(s.iloc[1] - 0.02 * 3 / 365.0) < 1e-12
        and abs(s.iloc[2] - 0.02 * 1 / 365.0) < 1e-12)
    chk("L2 a zero rate accrues exactly nothing", float(flat_rf(idx, 0.0).abs().sum()) == 0.0)
    chk("L3 the accrual series is indexed by the same dates it was handed",
        list(flat_rf(idx, 3.0).index) == list(idx))

    def cell(beta, regime, cagr, cash=0.5):
        return {"beta": beta, "regime": regime, "cagr_pct": cagr, "sharpe": 1.0,
                "maxdd_pct": -5.0, "vol_pct": 8.0, "cash_share": cash,
                "rate_observed_pct": 2.09, "rate_today_pct": 1.09}

    good = [cell(0.2, "observed", 11.33), cell(0.2, "flat_today", 10.85),
            cell(0.2, "zero", 10.33)]
    g = carry_gate(good)
    b = g["betas"][0.2]
    chk("L4 carry = observed - zero in pp", abs(b["carry_pp"] - 1.0) < 1e-9)
    chk("L5 flat-rate cost = observed - today-flat in pp",
        abs(b["flat_rate_cost_pp"] - 0.48) < 1e-9)
    chk("L6 sensitivity is pp per 100bp of the rate difference",
        abs(b["pp_per_100bp"] - 0.48) < 1e-9)
    chk("L7 carry share of the headline is reported, not assumed",
        abs(b["carry_share_of_headline_pct"] - 8.8) < 0.06)
    chk("L8 monotone arms pass the gate", g["flags"]["observed_ge_flat_ge_zero"] is True)
    chk("L9 carry is positive and selection survives zero cash",
        g["flags"]["carry_positive"] and g["flags"]["selection_survives_zero_cash"])

    bad = [cell(0.2, "observed", 10.0), cell(0.2, "flat_today", 10.5),
           cell(0.2, "zero", 9.0)]
    gb = carry_gate(bad)
    chk("L10 a higher rate that pays LESS is caught, not published",
        gb["flags"]["observed_ge_flat_ge_zero"] is False)
    neg = [cell(0.2, "observed", -1.0), cell(0.2, "flat_today", -2.0),
           cell(0.2, "zero", -3.0)]
    chk("L11 a book that needs cash carry to break even is flagged",
        carry_gate(neg)["flags"]["selection_survives_zero_cash"] is False)
    missing = [cell(0.2, "observed", 11.0), cell(0.2, "zero", 10.0)]
    chk("L12 missing arm -> None, never a number (no silent substitution)",
        carry_gate(missing)["betas"][0.2] is None)
    no_rate = [{"beta": 0.2, "regime": r, "cagr_pct": 10.0, "sharpe": 1.0,
                "maxdd_pct": -5.0, "vol_pct": 8.0, "cash_share": 0.5}
               for r in ("observed", "flat_today", "zero")]
    chk("L13 without rate quotes no sensitivity is invented",
        "pp_per_100bp" not in (carry_gate(no_rate)["betas"][0.2] or {}))

    print("selftest %d/%d" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))