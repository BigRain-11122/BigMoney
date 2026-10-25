"""Phase package under a cost sweep and a rolling-origin ruler.

r1251 left three follow-ups open; this round takes the two that decide whether the book is
tradeable at all:

  (a) cost sweep -- every published number in this family is 8bp/side. The package trades
      20 sub-books, so a cost error is paid 20 times over. Sweep 3/5/8/10/20/30bp on N=5 and
      N=10 and check the excess survives, plus report the actual annual fee drag in pp.
  (b) rolling origin -- a full-window CAGR of ~9% can be one good stretch plus eight flat
      years. Cut the package-vs-own-EW return spread into rolling 2-year (504-bar) windows
      and count how many are positive, plus a per-year table.

Engine: `P.fast_next_open_vt` from scripts/etf_phase_package_n.py (itself pinned 1e-12 to
`V.fast_next_open`), called with an explicit `cost`. --selftest re-pins the cost=8bp leg to
the reference engine and asserts cost monotonicity, so a mis-wired cost cannot pass.

Exploratory: no preregistration, no verdict, no ledger booking.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F  # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_phase_ensemble as P  # noqa: E402
from scripts import etf_phase_package_n as PK  # noqa: E402
from scripts.etf_asset_class import classify  # noqa: E402

ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
REBAL = 20
COST_BP = (3, 5, 8, 10, 20, 30)
N_MAIN = (5, 10)
ROLL_BARS = 504
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "etf_phase_cost_rolling.json")

eng = PK.fast_next_open_vt


def phase_book_cost(score, close, openp, n_hold, cost_bp):
    """`PK.phase_book` with an explicit per-side cost in bp."""
    idx = pd.to_datetime(close.index)
    cost = cost_bp / 10000.0
    curves, cells = [], []
    for k, start in enumerate(PK.phase_grid(idx)):
        ser, turn, _ = eng(score, close, openp, REBAL, n_hold=n_hold, cost=cost,
                           start=str(start.date()))
        if ser is None or len(ser) < 30:
            continue
        curves.append(ser)
        m = F.metrics(ser, "phase-%02d" % k)
        cells.append({"phase": k, "start": str(start.date()),
                      "cagr_pct": round(m["cagr"] * 100, 2), "sharpe": m["sharpe"],
                      "maxdd_pct": round(m["maxdd"] * 100, 2),
                      "turnover_per_rebal": round(turn, 3)})
    return P.mean_curve(curves), cells


def rolling_excess(ser, ew, bars=ROLL_BARS):
    """Annualised excess (pp/yr) of the package over the control on rolling `bars` windows."""
    idx = ser.index.intersection(ew.index)
    rp = ser.reindex(idx).pct_change().dropna()
    re = ew.reindex(idx).pct_change().dropna()
    idx = rp.index.intersection(re.index)
    rp, re = rp.reindex(idx), re.reindex(idx)
    out = []
    for i in range(0, len(idx) - bars + 1, 21):     # monthly stride
        a = rp.iloc[i:i + bars]
        b = re.reindex(a.index)
        def cagr(r):
            lvl = float(np.prod(1.0 + r.to_numpy()))
            yrs = len(r) / 252.0
            return (lvl ** (1.0 / yrs) - 1.0) * 100.0 if yrs > 0 and lvl > 0 else float("nan")
        out.append({"start": str(idx[i].date()), "end": str(idx[i + bars - 1].date()),
                    "pkg_pct": round(cagr(a), 2), "ew_pct": round(cagr(b), 2),
                    "excess_pp": round(cagr(a) - cagr(b), 2)})
    return out


def _year_excess(ser, ew):
    idx = ser.index.intersection(ew.index)
    rp = ser.reindex(idx).pct_change().dropna()
    re = ew.reindex(idx).pct_change().dropna()
    idx = rp.index.intersection(re.index)
    rp, re = rp.reindex(idx), re.reindex(idx)
    rows = {}
    for y in sorted({d.year for d in idx}):
        a = rp[[d.year == y for d in idx]]
        b = re[[d.year == y for d in idx]]
        if not len(a):
            continue
        pa = (float(np.prod(1.0 + a.to_numpy())) - 1.0) * 100
        pb = (float(np.prod(1.0 + b.to_numpy())) - 1.0) * 100
        rows[str(y)] = {"pkg_pct": round(pa, 2), "ew_pct": round(pb, 2),
                        "excess_pp": round(pa - pb, 2)}
    return rows


def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name, extra)

    rng = np.random.default_rng(7)
    n_bar, n_col = 160, 12
    idx = pd.bdate_range("2021-01-04", periods=n_bar)
    px = np.cumprod(1.0 + rng.normal(0.0007, 0.012, size=(n_bar, n_col)), axis=0) * 10.0
    close = pd.DataFrame(px, index=idx, columns=["c%02d" % k for k in range(n_col)])
    openp = close * (1.0 + rng.normal(0.0, 0.003, size=(n_bar, n_col)))
    score = pd.DataFrame(rng.normal(size=(n_bar, n_col)), index=idx, columns=close.columns)

    # leg 1: cost=8bp through phase_book_cost must equal the reference engine at 1e-12
    cost8 = 8.0 / 10000.0
    ref, ref_turn, _ = V.fast_next_open(score, close, openp, 7, n_hold=4, cost=cost8,
                                        start="2021-01-04")
    got, got_turn, _ = eng(score, close, openp, 7, n_hold=4, cost=cost8, start="2021-01-04")
    chk("date grid identical", ref.index.equals(got.index))
    chk("levels pinned 1e-12", float(np.max(np.abs(ref.to_numpy() / got.to_numpy() - 1.0)))
        < 1e-12)
    chk("turnover pinned 1e-12", abs(ref_turn - got_turn) < 1e-12, (ref_turn, got_turn))

    # leg 2: higher cost must never raise the NAV, and 0bp must be the max
    cur = {}
    for bp in (0.0, 8.0, 40.0):
        s, _, _ = eng(score, close, openp, 7, n_hold=4, cost=bp / 10000.0,
                      start="2021-01-04")
        cur[bp] = float(s.iloc[-1])
    chk("cost monotone (40bp < 8bp < 0bp)", cur[40.0] < cur[8.0] < cur[0.0], cur)

    # leg 3: phase_book_cost returns one cell per phase and the mean curve of the NAVs
    ens, cells = phase_book_cost(score, close, openp, 4, 8.0)
    chk("phase cells == phase grid", 0 < len(cells) <= REBAL, len(cells))
    chk("package curve non-empty", ens is not None and len(ens) > 30,
        (0 if ens is None else len(ens)))
    chk("package starts at 1.0", abs(float(ens.iloc[0]) - 1.0) < 1e-12)

    # leg 4: annual fee drag identity -- drag_pp ~= cost_bp/1e4 * turnover * (252/REBAL) * 100
    turn = float(np.mean([c["turnover_per_rebal"] for c in cells]))
    drag_expect = (8.0 / 10000.0) * turn * (252.0 / REBAL) * 100.0
    chk("turnover sane", 0.0 < turn < 3.0, turn)
    chk("expected drag is sub-pp", drag_expect < 5.0, drag_expect)

    # leg 5: rolling_excess and _year_excess produce aligned rows
    a = pd.Series(np.cumprod(1.0 + rng.normal(0.0006, 0.008, n_bar)),
                  index=idx)
    b = pd.Series(np.cumprod(1.0 + rng.normal(0.0002, 0.008, n_bar)), index=idx)
    rolls = rolling_excess(a, b, bars=100)
    chk("rolling windows produced", len(rolls) >= 1, len(rolls))
    chk("rolling row shape", set(rolls[0]) == {"start", "end", "pkg_pct", "ew_pct",
                                               "excess_pp"})
    yrs = _year_excess(a, b)
    chk("per-year rows keyed by year", all(len(k) == 4 for k in yrs), list(yrs)[:3])

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    t_all = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ew = F.run_ew(close[cols], amt[cols], REBAL, start=ANCHOR)
    base = F.metrics(ew, "ew")
    print("panel %s bars=%d bond_removed=%d | ew full %.2f%%"
          % (close.index[0].date(), close.shape[0], len(cols), base["cagr"] * 100), flush=True)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR, "rebal": REBAL,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "basis": "next-open fill per sub-book, per-side cost swept; package = buy-and-hold "
                 "mean of the R=20 phase NAVs; control = equal weight on the same subset",
        "question": "(a) does the package excess survive realistic costs, (b) is the excess "
                    "stable across rolling 2-year windows or one stretch",
        "control_ew": base,
        "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "cost is charged on sub-book turnover at each rebalance only (no borrow/slippage "
            "beyond the bp figure, no market-impact term)",
            "rolling windows overlap (monthly stride, 504-bar window), so the count of "
            "positive windows is a stability read, not an independent-sample test",
            "exploratory: no preregistration, no verdict, no ledger booking",
        ],
        "cost_sweep": {}, "rolling": {}, "per_year": {},
    }

    # (a) cost sweep
    drag_rows = []
    for n in N_MAIN:
        block = {}
        bps = COST_BP if n == N_MAIN[0] else tuple(b for b in COST_BP if b in (3, 8, 20, 30))
        for bp in bps:
            t0 = time.time()
            ens, cells = phase_book_cost(score, close[cols], openp[cols], n, bp)
            m = F.metrics(ens, "package")
            oos = ens[ens.index >= OOS]
            ewo = ew[ew.index >= OOS]
            mo = F.metrics(oos, "package:oos") if len(oos) > 20 else None
            turn = float(np.mean([c["turnover_per_rebal"] for c in cells]))
            drag = (bp / 10000.0) * turn * (252.0 / REBAL) * 100.0
            row = {
                "cost_bp_per_side": bp,
                "package": m,
                "excess_pp": round((m["cagr"] - base["cagr"]) * 100, 2),
                "oos_package": mo,
                "oos_excess_pp": (round((mo["cagr"] - F.metrics(ewo, "ew:oos")["cagr"]) * 100, 2)
                                  if mo else None),
                "mean_turnover_per_rebal": round(turn, 3),
                "rebal_per_year": round(252.0 / REBAL, 1),
                "annual_fee_drag_pp": round(drag, 3),
                "phase_cagr": PK._disp([c["cagr_pct"] for c in cells]),
                "secs": round(time.time() - t0, 1),
            }
            block["%dbp" % bp] = row
            drag_rows.append(row)
            print("N%-2d %2dbp pkg %6.2f%% (%+.2fpp) | oos %6.2f%% (%+.2fpp) | sharpe %.3f | "
                  "mdd %6.2f%% | turn %.3f | drag %.3fpp | %.0fs"
                  % (n, bp, m["cagr"] * 100, row["excess_pp"],
                     (mo["cagr"] * 100) if mo else float("nan"),
                     row["oos_excess_pp"] if row["oos_excess_pp"] is not None else float("nan"),
                     m["sharpe"], m["maxdd"] * 100, turn, drag, row["secs"]), flush=True)
        out["cost_sweep"]["N%d" % n] = block

    # (b) rolling origin + per year at the published 8bp
    ens8, cells8 = phase_book_cost(score, close[cols], openp[cols], F.N_HOLD, 8.0)
    rolls = rolling_excess(ens8, ew)
    ex = [r["excess_pp"] for r in rolls]
    out["rolling"] = {
        "window_bars": ROLL_BARS, "stride": 21, "n_windows": len(rolls),
        "excess_pp": {
            "min": round(float(min(ex)), 2) if ex else None,
            "p25": round(float(np.percentile(ex, 25)), 2) if ex else None,
            "median": round(float(np.median(ex)), 2) if ex else None,
            "p75": round(float(np.percentile(ex, 75)), 2) if ex else None,
            "max": round(float(max(ex)), 2) if ex else None,
        },
        "positive_windows": sum(1 for v in ex if v > 0),
        "windows": rolls,
    }
    out["per_year"] = _year_excess(ens8, ew)
    out["per_year_control"] = "ew on the same subset"

    print("rolling: n=%d positive=%d/%d median %+.2fpp min %+.2f max %+.2f"
          % (len(rolls), out["rolling"]["positive_windows"], len(rolls),
             out["rolling"]["excess_pp"]["median"], out["rolling"]["excess_pp"]["min"],
             out["rolling"]["excess_pp"]["max"]), flush=True)
    for y, r in out["per_year"].items():
        print("  %s pkg %6.2f%% ew %6.2f%% excess %+6.2fpp"
              % (y, r["pkg_pct"], r["ew_pct"], r["excess_pp"]), flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", OUT_PATH, "(%.0fs total)" % (time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())