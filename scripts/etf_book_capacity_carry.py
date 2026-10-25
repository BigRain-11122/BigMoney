"""Re-price the r1260 capacity ladder with the cash leg switched ON.

r1260 measured how much money the 5-name book can carry at a flat 8bp/side plus a
square-root impact term, and found break-even against the pool at ~50M. That ladder
priced an ALWAYS-FULLY-INVESTED book: every yuan not in a name sat at zero. The
production book (r1268) de-levers to an 8% vol target and keeps ~29% in cash, and that
cash now earns the repo ladder. So the honest capacity question is not "how big can the
unlevered book get" but "where does break-even move once the idle cash pays".

This script answers exactly that, with the same decision grid, the same ImpactCost
model and the same next-open execution as r1260 -- only the cash leg differs.

  python scripts/etf_book_capacity_carry.py run
  python scripts/etf_book_capacity_carry.py --selftest

Outputs results/etf_book_capacity_carry.json.
Exploratory: no preregistration, no verdict, no ledger booking.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F
from scripts import etf_book_forward as FWD
from scripts import etf_book_production as P
from scripts.etf_book_capacity import (ImpactCost, NAV_GRID, IMPACT_BP_PER_PCT,
                                       REBAL, START, REF_NAV)

K_BP = IMPACT_BP_PER_PCT
GRID = (1e6, 1e7, 5e7, 1e8, 5e8)


def _inputs():
    close, openp, amt, feats = F.build_panel()
    px = close.reindex(columns=close.columns).ffill()
    score = F.build_score(close, amt, feats)
    dates, rebal_days = FWD.date_grid(px, REBAL)
    return px, openp, amt, score, dates, rebal_days


def _ladder(px, openp, amt, score, dates, rebal_days, vol_target, carry, k_bp, grid,
            n_hold=None):
    """One capacity ladder. vol_target=None = always invested (r1260's book)."""
    rows = []
    for nav in grid:
        cm = ImpactCost(amt, nav, k_bp=k_bp, trace=False)
        fwd = FWD.Forward(px, openp, score, n_hold or F.N_HOLD, REBAL, cm,
                          vol_target=vol_target, carry=carry)
        marks = fwd.run(dates, rebal_days)
        ser = pd.Series([m["nav"] for _, m in marks], index=dates)
        ser = ser[ser.index >= pd.Timestamp(START)]
        m = F.metrics(ser, "nav=%.0e" % nav)
        cash = pd.Series([m_["cash"] for _, m_ in marks])
        rows.append({
            "nav": nav,
            "cagr": m.get("cagr"), "sharpe": m.get("sharpe"),
            "maxdd": m.get("maxdd"), "bars": m.get("bars"),
            "turnover": round(fwd.mean_turnover, 4),
            "n_fill": fwd.n_fill,
            "avg_cash": round(float(cash.iloc[1:].mean()), 6),
            "carry_bars": int(sum(1 for _, m_ in marks if m_.get("carry", 0.0) > 0)),
        })
    return rows


def _breakeven(rows, ref_cagr):
    ok = [r for r in rows if r.get("cagr") is not None and r["cagr"] > ref_cagr]
    return max([r["nav"] for r in ok]) if ok else None


def run(k_bp=K_BP, n_hold=None):
    px, openp, amt, score, dates, rebal_days = _inputs()
    carry, carry_note = FWD.build_carry(dates)
    if carry is None:
        raise SystemExit("repo panel absent: %s" % carry_note)

    ew = F.metrics(F.run_ew(px, amt, REBAL, start=START), "pool equal weight")
    out = {
        "evidence_cutoff": str(pd.Timestamp(dates[-1]).date()),
        "k_bp_per_pct": k_bp,
        "rebal": REBAL,
        "n_hold": n_hold or F.N_HOLD,
        "vol_target": P.TARGET_VOL,
        "frozen": {"pool_ew_cagr": ew.get("cagr"), "pool_ew_sharpe": ew.get("sharpe")},
        "carry_note": carry_note,
        "carry_mean_pct_per_yr": round(100.0 * float(np.nanmean(carry.values)) * 244.0, 4),
        "ladders": {},
    }

    # A: the r1260 book (always invested) -- carry can only touch gap cash
    a_off = _ladder(px, openp, amt, score, dates, rebal_days, None, None, k_bp, GRID, n_hold)
    a_on = _ladder(px, openp, amt, score, dates, rebal_days, None, carry, k_bp, GRID, n_hold)
    # B: the production book (8% vol target, ~29% cash)
    b_off = _ladder(px, openp, amt, score, dates, rebal_days, P.TARGET_VOL, None, k_bp, GRID, n_hold)
    b_on = _ladder(px, openp, amt, score, dates, rebal_days, P.TARGET_VOL, carry, k_bp, GRID, n_hold)

    for name, rows in (("invested_carry_off", a_off), ("invested_carry_on", a_on),
                       ("vt08_carry_off", b_off), ("vt08_carry_on", b_on)):
        out["ladders"][name] = rows
        out["ladders"][name + "_breakeven_nav_vs_pool_ew"] = _breakeven(rows, ew.get("cagr"))

    # the headline: what the cash leg is worth at each scale, and where break-even moves
    def _map(off, on, key):
        return [{"nav": o["nav"],
                 "cagr_carry_off": o["cagr"], "cagr_carry_on": n["cagr"],
                 "uplift_pp": (None if (o["cagr"] is None or n["cagr"] is None)
                               else round(100.0 * (n["cagr"] - o["cagr"]), 3))}
                for o, n in zip(off, on)]
    out["carry_value"] = {"invested": _map(a_off, a_on, "cagr"),
                          "vt08": _map(b_off, b_on, "cagr")}
    return out


def selftest():
    fails = []

    def chk(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
        if not ok:
            fails.append(name)

    px, openp, amt, score, dates, rebal_days = _inputs()
    flat = F.N_HOLD

    # L1 a callable that returns a constant must behave EXACTLY like that scalar --
    # this is the leg that lets the capacity ladder ride the forward state machine
    def _eq(cost, label):
        m = FWD.Forward(px, openp, score, flat, REBAL, cost)
        return pd.Series([mm["nav"] for _, mm in m.run(dates, rebal_days)], index=dates)
    s_scalar = _eq(F.COST, "scalar")
    s_call = _eq(lambda prev, new, d: F.COST, "callable")
    chk("callable cost == scalar cost", float(np.max(np.abs(s_scalar - s_call))) == 0.0,
        "maxdiff=%.2e" % float(np.max(np.abs(s_scalar - s_call))))

    # L2 the forward machine with a scalar cost reproduces the research engine exactly
    ser, _t, _g = F.run_next_open(px, openp, amt, None, REBAL, cost=F.COST,
                                  start=START, score=score)
    ser = ser[ser.index >= pd.Timestamp(START)]
    d = float(np.max(np.abs(s_scalar.reindex(ser.index) - ser)))
    chk("forward(scalar) == run_next_open engine", d < 1e-12, "maxdiff=%.2e" % d)

    # L3 activity: the vt08 book really does hold cash, and the ladder really pays
    carry, note = FWD.build_carry(dates)
    chk("repo carry panel present", carry is not None, str(note))
    if carry is not None:
        cm = ImpactCost(amt, REF_NAV, k_bp=K_BP, trace=False)
        off = FWD.Forward(px, openp, score, flat, REBAL, cm, vol_target=P.TARGET_VOL)
        mo = off.run(dates, rebal_days)
        cash = np.mean([m["cash"] for _, m in mo])
        chk("vt08 book holds cash (mechanism live)", cash > 0.05, "avg cash=%.3f" % cash)
        on = FWD.Forward(px, openp, score, flat, REBAL, ImpactCost(amt, REF_NAV, k_bp=K_BP, trace=False),
                         vol_target=P.TARGET_VOL, carry=carry)
        mk = on.run(dates, rebal_days)
        cb = sum(1 for _, m in mk if m.get("carry", 0.0) > 0)
        chk("carry accrues on some bars", cb > 0, "carry bars=%d" % cb)
        so = pd.Series([m["nav"] for _, m in mo], index=dates).iloc[-1]
        sn = pd.Series([m["nav"] for _, m in mk], index=dates).iloc[-1]
        chk("carry lifts the vt08 book at 10M", sn > so, "final %.4f -> %.4f" % (so, sn))

    # L4 zero-carry identity: carry=None and carry=(zeros) are the same book
    z = pd.Series(0.0, index=pd.DatetimeIndex(dates))
    a = FWD.Forward(px, openp, score, flat, REBAL, F.COST, carry=z).run(dates, rebal_days)
    b = FWD.Forward(px, openp, score, flat, REBAL, F.COST, carry=None).run(dates, rebal_days)
    d2 = max(abs(x["nav"] - y["nav"]) for (_, x), (_, y) in zip(a, b))
    chk("zero carry is an exact identity", d2 == 0.0, "maxabs=%.2e" % d2)

    print("SELFTEST %s (%d legs)" % ("OK" if not fails else "FAILED", 8))
    return 0 if not fails else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--k", type=float, default=K_BP)
    ap.add_argument("--n-hold", type=int, default=F.N_HOLD)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=os.path.join(PATHS.results_dir,
                                                  "etf_book_capacity_carry.json"))
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()

    out = run(k_bp=args.k, n_hold=args.n_hold)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("evidence_cutoff=%s  k=%.1fbp/1%%  carry=%.2f%%/yr (%s)"
          % (out["evidence_cutoff"], args.k, out["carry_mean_pct_per_yr"], out["carry_note"]))
    print("pool EW CAGR %.2f%%" % (100.0 * out["frozen"]["pool_ew_cagr"]))
    print("%-22s %10s %10s %10s" % ("ladder", "beNAV", "10M CAGR", "50M CAGR"))
    for k in ("invested_carry_off", "invested_carry_on", "vt08_carry_off", "vt08_carry_on"):
        rows = out["ladders"][k]
        def _c(nav):
            for r in rows:
                if abs(r["nav"] - nav) < 1:
                    return "%.2f%%" % (100.0 * r["cagr"]) if r["cagr"] else "n/a"
            return "n/a"
        be = out["ladders"].get(k + "_breakeven_nav_vs_pool_ew")
        print("%-22s %10s %10s %10s" % (k, ("%.0e" % be) if be else "-", _c(1e7), _c(5e7)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))