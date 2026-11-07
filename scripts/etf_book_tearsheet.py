"""ETF book tearsheet: one picture of the production book, rebuilt from the same engine.

Everything printed here is a *re-derivation* of an already published cell
(`results/etf_book_production/PRODUCTION-<bar>.json` -> backtest.n5_vt08), so the
control arm rule of E346 applies: if the rebuilt CAGR / Sharpe / max-DD do not
reproduce the published numbers inside 5e-5, the picture is of a different book and
this script refuses to emit it.

Outputs
    results/etf_book_tearsheet.png   four panels: log NAV vs benchmarks, drawdown,
                                     calendar-year bars, the executable ticket
    results/etf_book_tearsheet.json  the numbers behind the picture + the control arm

Usage
    python scripts/etf_book_tearsheet.py            # rebuild + render
    python scripts/etf_book_tearsheet.py --selftest # offline checks, no panel load
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

REBAL = 20
N_HOLD = 5
COST = 0.0010
VOL_TARGET = 0.08
CTRL_TOL = 5e-5


# ---------------------------------------------------------------- pure helpers
def drawdown(ser: pd.Series) -> pd.Series:
    """Running peak-to-trough, negative. A curve that only rises is all zeros."""
    peak = ser.cummax()
    return ser / peak - 1.0


def calendar_years(ser: pd.Series) -> dict:
    """Year -> return, each year renormalised against its own first level.

    The first year is measured from the series' own start (that is what the curve
    begins at), later years from the previous year's last level.
    """
    out = {}
    if ser.empty:
        return out
    prev_last = None
    for year, chunk in ser.groupby(ser.index.year):
        base = prev_last if prev_last is not None else float(chunk.iloc[0])
        out[int(year)] = float(chunk.iloc[-1]) / float(base) - 1.0
        prev_last = float(chunk.iloc[-1])
    return out


def full_block(block: dict) -> dict:
    """Production cells nest full/is/oos; a whole-history rebuild compares with `full`.

    Reading the outer block directly yields three Nones, which the control arm reports
    as 'does not reproduce' -- a refusal that names the wrong cause (r1292 family: a
    field whose name promises a number and hands back a container).
    """
    if not isinstance(block, dict):
        return {}
    inner = block.get("full")
    return inner if isinstance(inner, dict) else block


def same_object(a: dict, b: dict, tol: float = CTRL_TOL) -> dict:
    """Control-arm comparison of three numbers; also says which key drifted."""
    diffs = {}
    for k in ("cagr", "sharpe", "maxdd"):
        va, vb = a.get(k), b.get(k)
        if va is None or vb is None:
            diffs[k] = None
            continue
        diffs[k] = round(float(va) - float(vb), 9)
    ok = all(v is not None and abs(v) <= tol for v in diffs.values())
    return {"ok": ok, "tolerance": tol, "delta": diffs}


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
        print(("PASS " if cond else "FAIL ") + name)

    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    ser = pd.Series([1.0, 1.1, 0.99, 1.2, 1.32], index=idx)
    dd = drawdown(ser)
    check("drawdown is zero at a new high", abs(dd.iloc[1]) < 1e-12)
    check("drawdown measures from the running peak", abs(dd.iloc[2] - (0.99 / 1.1 - 1)) < 1e-12)
    check("drawdown ends flat on the last high", abs(dd.iloc[4]) < 1e-12)

    yrs = calendar_years(pd.Series([1.0, 2.0, 1.0, 1.5],
                                   index=pd.to_datetime(["2020-06-30", "2020-12-31",
                                                         "2021-06-30", "2021-12-31"])))
    check("calendar year 1 is measured from the series start", abs(yrs[2020] - 1.0) < 1e-12)
    check("later years start from the previous year's last level",
          abs(yrs[2021] - (1.5 / 2.0 - 1.0)) < 1e-12)
    check("the first year is measured from its own opening level, not 1.0",
          abs(yrs[2020] - (2.0 / 1.0 - 1.0)) < 1e-12)

    same = same_object({"cagr": 0.1146, "sharpe": 1.128, "maxdd": -0.1056},
                       {"cagr": 0.1146, "sharpe": 1.128, "maxdd": -0.1056})
    check("a control arm that repeats itself passes", same["ok"])
    diff = same_object({"cagr": 0.1146, "sharpe": 1.128, "maxdd": -0.1056},
                       {"cagr": 0.1146, "sharpe": 1.128, "maxdd": -0.1500})
    check("a control arm that drifts is refused", not diff["ok"])
    check("the refusal names the column that moved", abs(diff["delta"]["maxdd"] - 0.0444) < 1e-9)

    nested = {"full": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1},
              "is": {"cagr": 0.05, "sharpe": 0.5, "maxdd": -0.1}}
    check("a nested production cell is read through its whole-sample block",
          full_block(nested).get("cagr") == 0.1)
    check("a flat cell is read as itself", full_block({"cagr": 0.2}).get("cagr") == 0.2)

    empty = calendar_years(pd.Series(dtype=float))
    check("an empty curve yields no years", empty == {})

    print("SELFTEST %s (%d failed)" % ("OK" if not fails else "FAILED", len(fails)))
    return 0 if not fails else 1


# ---------------------------------------------------------------- main
def published_cell() -> dict | None:
    """The newest published production cell, read off disk rather than hard-coded."""
    d = os.path.join(E.PATHS.results_dir, "etf_book_production")
    try:
        latest = json.load(open(os.path.join(d, "latest.json"), encoding="utf-8"))
    except Exception:
        return None
    bar = latest.get("evidence_cutoff") or latest.get("ts")
    for name in (f"PRODUCTION-{bar}.json", "PRODUCTION-latest.json"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            cell = json.load(open(p, encoding="utf-8"))
            # the production cell nests full / is / oos; the whole-sample block is the
            # one a full-history rebuild must reproduce
            block = cell.get("backtest", {}).get("n5_vt08", {}) or {}
            return {"path": os.path.relpath(p, ROOT), "bar": bar,
                    "n5_vt08": full_block(block)}
    return None


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)

    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                      REBAL, N_HOLD, COST, vol_target=VOL_TARGET)
    ser = ser.dropna()
    book = A.stats2(ser, "book")

    # benchmarks: the index itself, and the whole ETF panel equal-weighted
    px = close[cols].reindex(ser.index).ffill()
    rets = px.pct_change().fillna(0.0)
    ew = (1.0 + rets.mean(axis=1)).cumprod()
    hs300_col = "510300" if "510300" in px.columns else None
    hs300 = (px[hs300_col] / px[hs300_col].iloc[0]) if hs300_col else None

    ref = {"equal_weight_etf": A.stats2(ew, "ew")}
    if hs300 is not None:
        ref["hs300"] = A.stats2(hs300.dropna(), "hs300")

    ctrl = published_cell()
    ctrl_check = None
    if ctrl and ctrl["n5_vt08"]:
        ctrl_check = same_object(book, ctrl["n5_vt08"])
        if not ctrl_check["ok"]:
            print("REFUSED: the rebuilt curve does not reproduce %s (%s)"
                  % (ctrl["path"], ctrl_check["delta"]), file=sys.stderr)
            return 2

    # the executable ticket, if the order face is on the same bar
    ticket = None
    try:
        latest = json.load(open(os.path.join(E.PATHS.results_dir, "etf_book_order",
                                             "TICKET-2026-11-06.json"), encoding="utf-8"))
        ticket = latest.get("ticket", {})
    except Exception:
        pass

    years = calendar_years(ser)
    years_ew = calendar_years(ew)
    years_h = calendar_years(hs300.dropna()) if hs300 is not None else {}

    # ---------------- render
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), facecolor="white")
    ax = axes[0][0]
    ax.plot(ser.index, ser.values, lw=1.6, color="#1f4e79", label="ETF book (bond-free, 8%% vol target)")
    ax.plot(ew.index, ew.values, lw=1.0, color="#999999", label="whole ETF panel, equal weight")
    if hs300 is not None:
        ax.plot(hs300.index, hs300.values, lw=1.0, color="#c0504d", label="510300 buy & hold")
    ax.set_yscale("log")
    ax.set_title("NAV, rebased to 1.0 (log scale)", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.25)

    ax = axes[0][1]
    ax.fill_between(ser.index, drawdown(ser).values * 100, 0, color="#1f4e79", alpha=0.35)
    if hs300 is not None:
        ax.plot(hs300.index, drawdown(hs300.dropna()).values * 100, lw=0.9, color="#c0504d",
                label="510300")
    ax.set_title("Drawdown from running high (%)", fontsize=11)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25)

    ax = axes[1][0]
    ys = sorted(years)
    x = np.arange(len(ys))
    ax.bar(x - 0.2, [years[y] * 100 for y in ys], 0.38, label="ETF book", color="#1f4e79")
    ax.bar(x + 0.2, [(years_ew.get(y) or 0.0) * 100 for y in ys], 0.38,
           label="ETF panel EW", color="#999999")
    if years_h:
        ax.plot(x, [(years_h.get(y) or 0.0) * 100 for y in ys], "o-", ms=3, lw=0.9,
                color="#c0504d", label="510300")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in ys], fontsize=8)
    ax.set_title("Calendar-year return (%)", fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25, axis="y")

    ax = axes[1][1]
    if ticket and ticket.get("order"):
        names = [o["symbol"] for o in ticket["order"]]
        wts = [o["weight"] * 100 for o in ticket["order"]]
        ax.barh(range(len(names)), wts, color="#1f4e79")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=8)
        ax.invert_yaxis()
        ax.set_title("Executable ticket weights (%%, cash %.1f%%)"
                     % (ticket.get("cash_weight", 0) * 100), fontsize=11)
        ax.grid(alpha=0.25, axis="x")
    else:
        ax.text(0.5, 0.5, "no executable ticket on disk", ha="center", va="center")
        ax.set_axis_off()

    fig.suptitle("BigMoney ETF book — tearsheet, evidence cutoff %s" % str(ser.index[-1].date()),
                 fontsize=13, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    png = os.path.join(E.PATHS.results_dir, "etf_book_tearsheet.png")
    fig.savefig(png, dpi=130)
    plt.close(fig)

    out = {
        "tool": "etf_book_tearsheet",
        "evidence_cutoff": str(ser.index[-1].date()),
        "first_bar": str(ser.index[0].date()),
        "bars": int(len(ser)),
        "config": {"rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST * 1e4,
                   "vol_target": VOL_TARGET, "universe": len(cols),
                   "flips_repaired": int(n_flip)},
        "book": book,
        "turnover_per_decision": round(turn, 3),
        "benchmarks": ref,
        "calendar_years": {str(k): round(v, 6) for k, v in years.items()},
        "calendar_years_ew": {str(k): round(v, 6) for k, v in years_ew.items()},
        "drawdown_now": round(float(drawdown(ser).iloc[-1]), 6),
        "control_arm": ctrl_check,
        "control_arm_source": ctrl["path"] if ctrl else None,
        "png": os.path.relpath(png, ROOT),
        "ticket": {"bar": "2026-11-06",
                   "order": ticket.get("order") if ticket else None,
                   "cash_weight": ticket.get("cash_weight") if ticket else None},
    }
    jp = os.path.join(E.PATHS.results_dir, "etf_book_tearsheet.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("book", book, flush=True)
    print("control arm", ctrl_check, flush=True)
    print("wrote", os.path.relpath(png, ROOT), os.path.relpath(jp, ROOT), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return build()


if __name__ == "__main__":
    sys.exit(main())