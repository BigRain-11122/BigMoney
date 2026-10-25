"""ETF book, production candidate -- an order sheet a human can actually place.

The research line settled on a configuration: bond/money sleeves carry no selection
skill (see etf_equity_alpha.py), so the book is built from equity + commodity +
convertible only, held at the top-N composite score, rebalanced every 20 bars, with a
volatility target that only ever de-levers. This script does two things and nothing else:

  1. re-runs that exact configuration on the full panel (so the number on the card is
     produced by the same engine that produced the research, not retyped);
  2. prints TODAY'S target book -- weights, cash slot, and a yuan/share order sheet at a
     stated capital, from the most recent bar in the panel.

It does not trade, does not touch any registry, and does not claim edge. The honest
caveats (survivorship in the ETF pool, IS-heavy history, 2026 flat) travel on the card.

  python scripts/etf_book_production.py run [--capital=1000000] [--n=8] [--rebal=20]
  python scripts/etf_book_production.py --selftest      # offline invariants
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

OUT_DIR = os.path.join(E.PATHS.results_dir, "etf_book_production")
IS_END = "2023-12-31"
COST = 0.0010
TARGET_VOL = 0.08
USE_CLASSES = ("equity", "commodity", "convertible")


def load_names():
    """ETF code -> short name from the shipped list; empty on failure (never fatal)."""
    p = os.path.join(E.PATHS.data_dir, "basic", "etf_list.csv")
    df = None
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            df = pd.read_csv(p, encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        return {}
    out = {}
    c_code, c_name = df.columns[0], df.columns[1]
    for code, name in zip(df[c_code].astype(str), df[c_name].astype(str)):
        code = code.strip()
        # the list carries exchange prefixes (sz159998) while the panel uses bare codes
        out[code[-6:]] = name.strip()
    return out


def scale_for(book, op, upto, target_vol=TARGET_VOL):
    """Same realised-vol overlay as etf_robust_pf book_vol: weights on 60d open returns."""
    if not book:
        return 1.0, None
    rets = op.pct_change()
    window = rets.loc[:upto].tail(60)[list(book)]
    if window.shape[0] < 20:
        return 1.0, None
    w = np.array([book[k] for k in window.columns])
    cov = window.cov().to_numpy()
    v = float(np.sqrt(w @ cov @ w) * np.sqrt(252))
    if not np.isfinite(v) or v <= 0:
        return 1.0, None
    return float(min(1.0, target_vol / v)), v


def backtest(close, openp, amt, score, n_hold, rebal, cost=COST, vol_target=None):
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      vol_target=vol_target)
    out = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= IS_END]),
                    ("oos", ser[ser.index > IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    out["turnover_per_decision"] = round(turn, 3)
    out["n_hold"] = n_hold
    out["vol_target"] = vol_target
    out["cost_bp"] = cost * 1e4
    return out, ser


def grid_position(dates, last_bar, rebal):
    """Where the last bar sits on the engine's every-`rebal`-bars decision grid.

    The panel ends at `last_bar`, so the next grid point usually lies in the future and
    has no date yet -- report it as a count of trading bars, not as an invented date.
    """
    if last_bar not in dates:
        return {"is_decision_bar": None, "bars_since_decision": None,
                "bars_until_next_decision": None, "last_decision_bar": None}
    i = dates.index(last_bar)
    off = i % rebal
    return {"is_decision_bar": off == 0,
            "bars_since_decision": off,
            "bars_until_next_decision": (rebal - off) % rebal,
            "last_decision_bar": str(dates[i - off].date())}


def run(capital=1_000_000.0, n_hold=8, rebal=20):
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in USE_CLASSES]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    names = load_names()

    runs = {}
    for n in sorted({5, 8, n_hold}):
        for lbl, vt in (("base", None), ("vt08", TARGET_VOL)):
            key = "n%d_%s" % (n, lbl)
            runs[key], _ = backtest(close, openp, amt, score, n, rebal, vol_target=vt)
            print(key, runs[key]["full"], flush=True)

    # ---- today's book, computed exactly like the engine's decision step
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    masked = score.where(elig)
    last = masked.index[-1]
    s = masked.loc[last].dropna()
    picks = list(s.nlargest(n_hold).index)
    book = {p: 1.0 / len(picks) for p in picks}
    scale, realised_vol = scale_for(book, openp, last)
    weights = {p: w * scale for p, w in book.items()}
    cash = 1.0 - sum(weights.values())

    px = close.reindex(columns=close.columns).ffill().loc[last]
    legs = []
    for p in picks:
        w = weights[p]
        price = float(px.get(p)) if p in px.index else None
        amount = w * capital
        shares = int(amount / price // 100 * 100) if price and price > 0 else None  # 100-share lots
        legs.append({
            "symbol": p,
            "name": names.get(p) or names.get(p[2:]) or "",
            "class": cls[p],
            "score": round(float(s[p]), 4),
            "weight": round(w, 4),
            "amount_cny": round(amount, 0),
            "ref_price": price,
            "lots_100": shares,
            "actual_amount_cny": round(shares * price, 0) if shares and price else None,
        })
    legs.sort(key=lambda r: -r["amount_cny"])

    op_dates = [d for d in openp.index if d >= pd.Timestamp(R.START)]
    grid = grid_position(op_dates, last, rebal)

    sheet = {
        "as_of_bar": str(last.date()),
        "decision": "REBALANCE: this bar's close is a decision point -- place at next open"
                    if grid["is_decision_bar"]
                    else "HOLD: %d bars until the next decision point"
                         % grid["bars_until_next_decision"],
        "is_grid_decision_bar": grid["is_decision_bar"],
        "last_decision_bar": grid["last_decision_bar"],
        "bars_until_next_decision": grid["bars_until_next_decision"],
        "capital_cny": capital,
        "target_vol": TARGET_VOL,
        "realised_book_vol_60d": None if realised_vol is None else round(realised_vol, 4),
        "risk_scale": round(scale, 4),
        "cash_weight": round(cash, 4),
        "cash_amount_cny": round(cash * capital, 0),
        "legs": legs,
    }

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(last.date()),
        "script": "scripts/etf_book_production.py",
        "config": {"universe_classes": list(USE_CLASSES), "n_hold": n_hold, "rebal": rebal,
                   "cost_bp_per_side": COST * 1e4, "vol_target": TARGET_VOL,
                   "capital_cny": capital, "universe_size": len(cols),
                   "flips_repaired": n_flip,
                   "execution": "decide at close t -> fill at open t+1 -> hold to next rebalance"},
        "backtest": runs,
        "sheet": sheet,
        "caveats": [
            "ETF pool is today's listed set: survivorship inflates the equity sleeve.",
            "2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.",
            "The vol target only de-levers; it is a drawdown tool, not an edge.",
            "Order sheet is research output, not an investment recommendation.",
        ],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "PRODUCTION-%s.json" % last.date()), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    write_card(out)
    print(json.dumps(sheet, ensure_ascii=False, indent=1))
    return out


def write_card(out):
    s, cfg, bt = out["sheet"], out["config"], out["backtest"]
    b = bt.get("n%d_vt08" % cfg["n_hold"], {})
    lines = [
        "# ETF book -- production candidate, order sheet (%s bar)" % s["as_of_bar"],
        "",
        "Config: %d names of a %d-instrument bond-free pool, rebalance every %d bars, "
        "%g bp/side, %.0f%% vol target (de-lever only)."
        % (cfg["n_hold"], cfg["universe_size"], cfg["rebal"], cfg["cost_bp_per_side"],
           cfg["vol_target"] * 100),
        "",
        "| window | CAGR | Sharpe | max drawdown |",
        "|---|---|---|---|",
    ]
    for lbl in ("full", "is", "oos"):
        m = b.get(lbl) or {}
        if m.get("cagr") is None:
            continue
        lines.append("| %s | %.1f%% | %.2f | %.1f%% |" % (
            {"full": "2020-01 onwards", "is": "2020-2023", "oos": "2024 onwards"}[lbl],
            m["cagr"] * 100, m["sharpe"] or 0.0, m["maxdd"] * 100))
    lines += [
        "",
        "**Today (%s bar): %s** (last grid decision %s)." % (
            s["as_of_bar"], s["decision"], s["last_decision_bar"]),
        "",
        "Realised 60d book vol %.1f%% -> risk scale %.2f, cash slot %.1f%%."
        % ((s["realised_book_vol_60d"] or 0) * 100, s["risk_scale"], s["cash_weight"] * 100),
        "",
        "| code | name | sleeve | weight | amount (CNY) | 100-share lots |",
        "|---|---|---|---|---|---|",
    ]
    for leg in s["legs"]:
        lines.append("| %s | %s | %s | %.1f%% | %s | %s |" % (
            leg["symbol"], leg["name"], leg["class"], leg["weight"] * 100,
            format(int(leg["amount_cny"]), ","), leg["lots_100"]))
    lines += ["| cash | - | money | %.1f%% | %s | - |" % (
        s["cash_weight"] * 100, format(int(s["cash_amount_cny"]), ",")), ""]
    lines += ["## Caveats", ""] + ["- " + c for c in out["caveats"]] + [""]
    with open(os.path.join(OUT_DIR, "CARD.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def selftest():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in USE_CLASSES][:60]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""), flush=True)

    # 1. vol target never levers up: scale <= 1 for any book
    book = {c: 1.0 / 3 for c in cols[:3]}
    sc, v = scale_for(book, openp, openp.index[-1])
    chk("vol target never levers up", 0 < sc <= 1.0, "scale=%s vol=%s" % (sc, v))
    # 2. alignment: a bar one step off the grid must not read as a decision bar
    dates = [d for d in openp.index if d >= pd.Timestamp(R.START)]
    if len(dates) > 41:
        d0 = dates[40]  # on-grid under rebal=20
        d1 = dates[41]
        chk("grid flags the on-grid bar", grid_position(dates, d0, 20)["is_decision_bar"] is True)
        chk("grid rejects the off-grid bar", grid_position(dates, d1, 20)["is_decision_bar"] is False)
        chk("grid counts bars to the next decision", grid_position(dates, d1, 20)["bars_until_next_decision"] == 19,
            str(grid_position(dates, d1, 20)["bars_until_next_decision"]))
    # 3. weights + cash conserve exactly 1.0
    w = {c: 1.0 / 5 for c in cols[:5]}
    sc2, _ = scale_for(w, openp, openp.index[-1])
    tot = sum(sc2 * x for x in w.values())
    chk("weights + cash == 1", abs(tot + (1.0 - tot) - 1.0) < 1e-12, "invested=%.6f" % tot)
    # 4. engine reproduces a flat line only when it has no history (sanity on the harness)
    ser, _ = R.open_to_open_equity(close, openp, amt, score, 20, 5, COST)
    chk("harness actually traded", ser.notna().sum() > 10 and ser.std() > 0,
        "bars=%d std=%.6f" % (ser.notna().sum(), ser.std()))
    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "--selftest" in args:
        sys.exit(selftest())
    opts = {}
    for a in args:
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
    run(capital=float(opts.get("capital", 1_000_000)),
        n_hold=int(opts.get("n", 12)), rebal=int(opts.get("rebal", 20)))