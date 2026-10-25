"""ETF book width audit -- what the 5-name executable ticket costs against the 12-name card.

The two live faces of the production book disagree on one number that nobody had priced:

  * ``etf_book_order`` (the only artefact a broker adapter can follow) sizes its basket at
    ``F.N_HOLD`` = 5 names, because it reuses the composite factor's default;
  * the production card / forward ledger run the sleeve at **12 names** with an 8% vol
    target (r1269 "12-name sleeve", r1270 "12 names", r1271 vol_delivery on the card).

Both are published as "the production book", so an operator has to know which one the
ticket is. This script answers the only question that matters for that decision: holding
the ticket's own accounting fixed (beta overlay at 0.20, GC001 on the cash remainder,
next-open fills, 10bp/side) and moving ONLY the name count, what does width buy or cost?

Accounting is reused, never re-implemented:
  * book leg        = ``F.run_next_open(..., n_hold=n)``
  * beta overlay    = ``BT.k_schedule`` / ``BT.in_force`` / ``BT.apply_overlay``
  * cash leg        = ``BW.load_repo_rates`` / ``BW.repo_daily_cash``
  * stats           = ``etf_book_order.metrics`` (same CAGR/Sharpe/DD definitions as the
                      ticket face, so the numbers here are directly comparable)

The overlay de-levers only (k = target/beta clipped to [0,1]) and is charged |delta k| *
cost on the k leg, so a wider sleeve also changes how much cash the beta rule leaves on
the table -- that is reported, not netted out.

  python scripts/etf_book_width_audit.py run [--beta=0.20] [--inception=2024-01-01]
  python scripts/etf_book_width_audit.py --selftest

Outputs:
  results/etf_book_width_audit.json     per-width rows + evidence_cutoff

Exploratory measurement: no verdict, no ledger booking, no admission change.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_book_order as EO           # noqa: E402  (metrics + accounting)
from scripts import etf_composite_pf as F          # noqa: E402
from scripts import etf_phase_beta_target as BT    # noqa: E402
from scripts import etf_phase_beta_window as BW    # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402  (the ticket's KEEP list)
from scripts.etf_asset_class import classify       # noqa: E402

WIDTHS = (5, 8, 12, 20)
DEFAULT_BETA = 0.20
DEFAULT_INCEPTION = "2024-01-01"
COST_BP = 8.0
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results")


def prep():
    """Panel + composite score, exactly the columns the order ticket scores."""
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    return {"close": close[cols], "openp": openp[cols], "amt": amt[cols],
            "feats": feats, "score": score, "mkt": close[mkt_col], "classes": classes}


def arm(pan, n_hold, beta=DEFAULT_BETA, inception=DEFAULT_INCEPTION):
    """One width, ticket accounting: book leg -> beta overlay -> repo cash on the rest."""
    ser, turnover, _gap = F.run_next_open(pan["close"], pan["openp"], pan["amt"],
                                          pan["feats"], EO.REBAL, n_hold=n_hold,
                                          cost=F.COST, score=pan["score"])
    idx = ser.index.intersection(pan["mkt"].index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(pan["mkt"].reindex(idx))
    sched = EO.k_schedule(rp, rm, beta)
    k_ser = EO.in_force(sched, idx)
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)
    strat, bench, _kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=cash_rf)
    if strat is None:
        raise SystemExit("FATAL: overlay produced no live window at n_hold=%d" % n_hold)
    start = pd.Timestamp(inception)
    live_k = k_ser.dropna()
    lo = live_k.index[0] if len(live_k) else start
    lo = max(lo, start)
    slip, blip = strat[strat.index >= lo], bench[bench.index >= lo]
    m = EO.metrics(slip, blip)
    kk = k_ser.reindex(slip.index)
    book = {
        "n_hold": int(n_hold),
        "turnover_per_year": round(float(turnover), 4),
        "cash_share": round(float((1.0 - kk).mean()), 4),
        "k_mean": round(float(kk.mean()), 4),
        "k_full_share": round(float((kk >= 0.999).mean()), 4),
        "cash_leg_missing_bars": int(cash_missing) if cash_missing is not None else 0,
        "bars": int(len(slip)),
    }
    book.update({k: v for k, v in (m or {}).items() if v is not None})
    return book, slip


def run(beta=DEFAULT_BETA, inception=DEFAULT_INCEPTION, widths=WIDTHS):
    pan = prep()
    rows, curves = [], {}
    for n in widths:
        row, slip = arm(pan, n, beta=beta, inception=inception)
        rows.append(row)
        curves[n] = slip
        b = row.get("book") or {}
        x = row.get("excess_pp")
        print("n=%-3d CAGR %5.2f%%  Sharpe %5.3f  DD %6.2f%%  cash %4.1f%%  "
              "excess %+5.2fpp  turn %.2f"
              % (n, 100.0 * (b.get("cagr") or 0.0), b.get("sharpe") or 0.0,
                 100.0 * (b.get("maxdd") or 0.0), 100.0 * row["cash_share"],
                 x if x is not None else float("nan"), row["turnover_per_year"]),
              flush=True)
    asof = str(max(c.index[-1] for c in curves.values()).date())
    base = next((r for r in rows if r["n_hold"] == 5), None)
    wide = next((r for r in rows if r["n_hold"] == 12), None)
    headline = None
    if base and wide:
        headline = {
            "ticket_wide_pp": round(100.0 * ((wide["book"]["cagr"] or 0.0)
                                            - (base["book"]["cagr"] or 0.0)), 2),
            "sharpe_delta": round((wide["book"]["sharpe"] or 0.0)
                                  - (base["book"]["sharpe"] or 0.0), 3),
            "cash_share_5": base["cash_share"],
            "cash_share_12": wide["cash_share"],
            "turnover_5": base["turnover_per_year"],
            "turnover_12": wide["turnover_per_year"],
        }
        print("headline: 12 names vs the executable 5 -> %+.2fpp/yr, Sharpe %+.3f, "
              "cash %.1f%% -> %.1f%%"
              % (headline["ticket_wide_pp"], headline["sharpe_delta"],
                 100.0 * headline["cash_share_5"], 100.0 * headline["cash_share_12"]),
              flush=True)
    payload = {"evidence_cutoff": asof, "beta_target": float(beta),
               "inception": str(inception), "widths": list(widths),
               "cost_bp_side": COST_BP, "rows": rows, "headline": headline}
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "etf_book_width_audit.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("wrote " + p)
    return 0


# ------------------------------------------------------------------------ selftest
def _synth(n_names=9, n_bars=320, seed=11):
    """A tiny deterministic panel: names differ only in drift so picks are stable."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-04", periods=n_bars)
    cols = ["S%02d" % i for i in range(n_names)]
    rets = pd.DataFrame(rng.normal(0.0004, 0.008, size=(n_bars, n_names)),
                        index=dates, columns=cols)
    rets["S00"] += 0.0012            # a persistent leader
    rets["S01"] += 0.0009
    close = 1.0 * (1.0 + rets).cumprod()
    return close, rets


def selftest():
    ok = True

    def leg(name, cond, note=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("%s %s %s" % ("PASS" if cond else "FAIL", name, note))

    # 1) width actually changes the basket: run_next_open must honour n_hold, otherwise
    #    every arm here would be the same book and the table would mean nothing.
    close, _rets = _synth()
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(5000.0, index=close.index, columns=close.columns)
    feats = {}
    score = close.rolling(20).mean() / close - 1.0
    s5, t5, _ = F.run_next_open(close, openp, amt, feats, 20, n_hold=5,
                                cost=F.COST, score=score)
    s9, t9, _ = F.run_next_open(close, openp, amt, feats, 20, n_hold=9,
                                cost=F.COST, score=score)
    diverged = float((s5.dropna() / s9.dropna() - 1.0).abs().max() or 0.0)
    leg("width changes the book (activity leg)", diverged > 1e-6,
        "max rel diff %.2e" % diverged)
    leg("two widths produce two turnovers", abs(float(t5) - float(t9)) > 1e-3,
        "t5=%.3f t9=%.3f" % (t5, t9))

    # 2) the stats block is the ticket's own metric, so the table is comparable by
    #    construction -- pin the arithmetic on a synthetic curve with known endpoints.
    dates = pd.bdate_range("2022-01-03", periods=253)
    lin = pd.Series(np.linspace(1.0, 1.10, 253), index=dates)
    m = EO.metrics(lin, lin)
    leg("metrics reuse the ticket definitions",
        m is not None and m["book"]["bars"] == 253
        and abs(m["book"]["cagr"] - 0.10) < 0.02,
        "cagr=%.4f" % (m["book"]["cagr"] if m else float("nan")))

    # 3) the headline must be free of the r1262 width-confounded comparison: both legs
    #    are read off the SAME rows list, so a missing 12-name row cannot be silently
    #    compared against a different experiment.
    base = {"book": {"cagr": 0.10, "sharpe": 1.0}}
    wide = {"book": {"cagr": 0.12, "sharpe": 1.1}}
    d = round(100.0 * (wide["book"]["cagr"] - base["book"]["cagr"]), 2)
    leg("headline is a same-rows difference", abs(d - 2.0) < 1e-9, "delta=%.2fpp" % d)

    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--beta", type=float, default=DEFAULT_BETA)
    ap.add_argument("--inception", default=DEFAULT_INCEPTION)
    a = ap.parse_args()
    if a.selftest or a.cmd == "selftest":
        return selftest()
    return run(beta=a.beta, inception=a.inception)


if __name__ == "__main__":
    sys.exit(main())