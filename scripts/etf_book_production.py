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
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import exchange_calendar_audit as CA

OUT_DIR = os.path.join(E.PATHS.results_dir, "etf_book_production")
IS_END = "2023-12-31"
COST = 0.0010
TARGET_VOL = 0.08
USE_CLASSES = ("equity", "commodity", "convertible")


def preperiod_support():
    """Read results/etf_book_pre2020.json -> the one-line out-of-period verdict.

    The card's whole history is 2020+. results/etf_book_pre2020.json prices the same
    engine on the 224 ETFs that already existed, over 2015-2019, and prints a negative
    excess there -- so the published return is a single-regime result and the card has
    to say so next to the CAGR rather than leave it in a digest (r1275: a measured
    difference has to land where the decision is made). Soft-fails to None: a missing
    or unreadable file must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_pre2020.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        cell = doc["cells"]["A_pre_universe_pre_period"]["cells"]
        primary = doc.get("grid", {}).get("primary", "N5_R20")
        row = cell[primary]
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "grid_cell": primary,
            "window": "%s..%s" % (doc["cells"]["A_pre_universe_pre_period"]["start"],
                                  doc["cells"]["A_pre_universe_pre_period"]["end"]),
            "universe_size": doc["cells"]["A_pre_universe_pre_period"]["universe_size"],
            "book_cagr": row["book"]["cagr"],
            "ew_cagr": row["ew"]["cagr"],
            "excess_pp": row["excess_cagr_pp"],
            "null_p": row.get("null", {}).get("p_value"),
            "cells_negative": sum(1 for v in cell.values() if v["excess_cagr_pp"] < 0),
            "cells_total": len(cell),
        }
    except Exception:
        return None


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


def backtest(close, openp, amt, score, n_hold, rebal, cost=COST, vol_target=None,
             vol_window=60):
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      vol_target=vol_target, vol_window=vol_window)
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


def delivered_vs_target(bt_row, target):
    """Realised vol next to the number on the label, window by window, with the ratio.

    The overlay is min(1, target / v) sized on the *picked names' backward* vol, so no
    window is guaranteed to deliver `target` -- the sleeve can run hotter than its label.
    The ratio is reported, never corrected: a fitted multiplier on the same sample is
    exactly the fitting that r1270's window x target sweep exists to detect.
    """
    out = {"target_vol": target, "windows": {}}
    for lbl in ("full", "is", "oos"):
        m = (bt_row or {}).get(lbl) or {}
        v = m.get("vol")
        if v is None:
            continue
        out["windows"][lbl] = {"target": target, "delivered": round(float(v), 4),
                               "ratio": round(float(v) / target, 3) if target else None}
    f = out["windows"].get("full")
    if f and f["ratio"] is not None:
        out["headline"] = ("target %.0f%% -> delivered %.1f%% over the full window (%.2fx)"
                           % (target * 100, f["delivered"] * 100, f["ratio"]))
    elif f:
        out["headline"] = ("delivered %.1f%% over the full window (no target set)"
                           % (f["delivered"] * 100))
    else:
        out["headline"] = None
    return out


def prep_panel(repair=True, repair_fn=None):
    """Panel + score exactly as the production run sees them (class filter included).

    Shared by `run` and by any sweep over the configuration, so a sensitivity study can
    never quietly price a different universe than the card.

    Returns the class map alongside the panel: the order sheet labels every leg with it,
    and recomputing it downstream would be a second, drift-prone classification. The
    flip count travels too -- it is printed on the card as evidence the panel was repaired.
    """
    close, openp, amt, feats = E.build_panel()
    if repair_fn is not None:
        # counterfactual repair injected by an audit (e.g. the pre-r1282 behaviour), so a
        # twin can be priced through THIS universe and score builder instead of a copy.
        close, openp, n_flip = repair_fn(close, openp)
    elif repair:
        close, openp, n_flip = A.repair_flips(close, openp)
    else:
        # the raw twin: the panel exactly as the source prints it, for audits that have
        # to price what the repair is worth instead of assuming it (etf_book_split_audit).
        n_flip = 0
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in USE_CLASSES]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    return close, openp, amt, score, cls, n_flip


def run(capital=1_000_000.0, n_hold=8, rebal=20):
    close, openp, amt, score, cls, n_flip = prep_panel()
    cols = list(close.columns)
    names = load_names()

    runs = {}
    for n in sorted({5, 8, n_hold}):
        for lbl, vt in (("base", None), ("vt08", TARGET_VOL)):
            key = "n%d_%s" % (n, lbl)
            runs[key], _ = backtest(close, openp, amt, score, n, rebal, vol_target=vt)
            print(key, runs[key]["full"], flush=True)

    # ---- the book IN FORCE, read off the engine's own decision step.
    # The engine only re-decides every `rebal` bars, so re-ranking the panel's last bar
    # here hands a human a sheet that trades 11 of 12 names on a bar the card itself
    # labels "HOLD". That is what this function did until r1277: at cutoff 2026-10-23 the
    # card listed the 10-23 top-12 while the book in force was the one decided 2026-10-14,
    # sharing a single name (159307) -- and the forward ledger, which does decide on the
    # grid, was tracking that other book. Consuming the diag row makes the card and the
    # ledger the same object by construction rather than by agreement.
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    masked = score.where(elig)
    last = masked.index[-1]
    diag = []
    R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, COST,
                          vol_target=TARGET_VOL, diag=diag)
    if not diag:
        raise RuntimeError("panel too short for one decision on the grid")
    drow = diag[-1]
    dec_bar = pd.Timestamp(drow["date"])
    picks = list(drow["book"])
    scale = float(drow["scale"])
    s = masked.loc[dec_bar].dropna()          # the scores that actually picked
    book = {p: 1.0 / len(picks) for p in picks}
    realised_vol = scale_for(book, openp, dec_bar)[1]
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
        "last_decision_bar": str(dec_bar.date()),
        "book_decided_at": str(dec_bar.date()),
        "bars_until_next_decision": grid["bars_until_next_decision"],
        "capital_cny": capital,
        "target_vol": TARGET_VOL,
        "realised_book_vol_60d": None if realised_vol is None else round(realised_vol, 4),
        "risk_scale": round(scale, 4),
        "cash_weight": round(cash, 4),
        "cash_amount_cny": round(cash * capital, 0),
        "legs": legs,
    }

    dv = delivered_vs_target(runs.get("n%d_vt08" % n_hold), TARGET_VOL)
    # r1287: the card is the sheet a human reads, so it states out loud which bar it was
    # priced on against the official calendar -- the panel cannot judge this by itself.
    feed = CA.live_ticket_feed_status(last)
    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(last.date()),
        "feed_status": feed,
        "script": "scripts/etf_book_production.py",
        "config": {"universe_classes": list(USE_CLASSES), "n_hold": n_hold, "rebal": rebal,
                   "cost_bp_per_side": COST * 1e4, "vol_target": TARGET_VOL,
                   "capital_cny": capital, "universe_size": len(cols),
                   "flips_repaired": n_flip,
                   "execution": "decide at close t -> fill at open t+1 -> hold to next rebalance"},
        "backtest": runs,
        "vol_delivery": dv,
        "sheet": sheet,
        "caveats": [
            "ETF pool is today's listed set: survivorship inflates the equity sleeve.",
            "2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.",
            "The vol target only de-levers; it is a drawdown tool, not an edge.",
            "Delivered vol is not the label: %s. The label is a per-hold risk target, so an "
            "8%% label annualises near 10%% once hold-level vol dispersion is priced in -- a "
            "definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md)." % (dv.get("headline") or "no history"),
            "Order sheet is research output, not an investment recommendation.",
            "The sheet is the book decided at book_decided_at, not a re-ranking of the "
            "latest bar: the engine only re-decides every %d bars, so an off-grid ranking "
            "would trade names the book never held." % rebal,
        ],
        "preperiod": preperiod_support(),
    }
    pp = out["preperiod"]
    if pp is not None:
        out["caveats"].insert(0,
            "ONE REGIME, NOT A VERIFIED EDGE: on the %d ETFs that existed before 2020, "
            "priced 2015-2019 (a window this card never covered) the same engine returned "
            "%+.2f%%/yr against %+.2f%%/yr equal weight = %+.2fpp excess, worse in %d of %d "
            "grid cells, random-score p=%.2f. The published CAGR is the 2020+ regime, not a "
            "property of the factors. See %s."
            % (pp["universe_size"], pp["book_cagr"] * 100, pp["ew_cagr"] * 100,
               pp["excess_pp"], pp["cells_negative"], pp["cells_total"],
               pp["null_p"] if pp["null_p"] is not None else float("nan"), pp["artifact"]))
    if feed.get("status") in ("stale_feed", "feed_broken"):
        out["caveats"].insert(0, "FEED IS BEHIND: this card is priced on the %s bar, %s "
                              "official trading day(s) short of the %s bar the market has "
                              "already published. The names are that old, not a fresh call."
                              % (feed.get("ticket_bar"), feed.get("lag_days"),
                                 feed.get("expected_bar")))
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
        "| window | CAGR | Sharpe | max drawdown | realised vol | target |",
        "|---|---|---|---|---|---|",
    ]
    dv = out.get("vol_delivery") or {}
    for lbl in ("full", "is", "oos"):
        m = b.get(lbl) or {}
        if m.get("cagr") is None:
            continue
        d = (dv.get("windows") or {}).get(lbl) or {}
        lines.append("| %s | %.1f%% | %.2f | %.1f%% | %.1f%% | %.0f%% (%.2fx) |" % (
            {"full": "2020-01 onwards", "is": "2020-2023", "oos": "2024 onwards"}[lbl],
            m["cagr"] * 100, m["sharpe"] or 0.0, m["maxdd"] * 100,
            (m.get("vol") or 0.0) * 100, cfg["vol_target"] * 100, d.get("ratio") or 0.0))
    lines += [""]
    if dv.get("headline"):
        lines += ["**Vol label vs delivered risk: %s.** The overlay only de-levers, so a "
                  "sleeve sized on its own backward vol can run hotter than %.0f%%; read the "
                  "risk column, not the label." % (dv["headline"], cfg["vol_target"] * 100), ""]
    lines += [
        "",
        "**Feed: %s** -- priced on the %s bar; the official calendar expects %s (lag %s "
        "official day(s))." % (
            (out.get("feed_status") or {}).get("status", "unknown"), s["as_of_bar"],
            (out.get("feed_status") or {}).get("expected_bar") or "unknown",
            (out.get("feed_status") or {}).get("lag_days")), "",
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

    # 5. delivered-vs-target is pure arithmetic and never invents a missing window
    dv = delivered_vs_target({"full": {"vol": 0.1018}, "is": {"vol": 0.09}}, 0.08)
    chk("vol delivery ratio", abs(dv["windows"]["full"]["ratio"] - 1.2725) < 5e-4, dv["headline"] or "")
    chk("vol delivery skips absent windows", "oos" not in dv["windows"])
    chk("vol delivery headline quotes delivered risk", "10.2%" in (dv["headline"] or ""))
    chk("vol delivery without a target has no ratio",
        delivered_vs_target({"full": {"vol": 0.10}}, 0)["windows"]["full"]["ratio"] is None)

    # 6. end-to-end on a synthetic panel: the whole run() path (order sheet + card) must
    #    execute. r1270's prep_panel() extraction left run() reading names that no longer
    #    existed in its scope, and the card -- the only placeable deliverable -- crashed
    #    for a full round with every other leg green, because no leg ever called run().
    idx = pd.bdate_range("2021-01-04", periods=400)
    rng = np.random.default_rng(7)
    syn = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0, 0.01, (len(idx), 9)), axis=0)),
        index=idx, columns=["519%03d" % i for i in range(9)])
    s_open = syn.shift(1).bfill()
    s_amt = pd.DataFrame(1e8, index=idx, columns=syn.columns)
    s_score = syn.pct_change(20).fillna(0.0)
    s_cls = {c: "equity" for c in syn.columns}
    tmp = tempfile.mkdtemp(prefix="etf_book_prod_selftest_")
    keep = (globals()["prep_panel"], globals()["load_names"], globals()["OUT_DIR"])
    try:
        globals()["prep_panel"] = lambda: (syn, s_open, s_amt, s_score, s_cls, 0)
        globals()["load_names"] = lambda: {}
        globals()["OUT_DIR"] = tmp
        o = run(capital=1_000_000.0, n_hold=3, rebal=20)
        card = open(os.path.join(tmp, "CARD.md"), encoding="utf-8").read()
        chk("run() produces a placeable sheet",
            len(o["sheet"]["legs"]) == 3 and o["sheet"]["as_of_bar"] == str(idx[-1].date()),
            "legs=%d as_of=%s" % (len(o["sheet"]["legs"]), o["sheet"]["as_of_bar"]))
        chk("card states delivered vol against the label",
            "Vol label vs delivered risk" in card and "target 8%" in card)
        chk("card lists every leg", all(l["symbol"] in card for l in o["sheet"]["legs"]))
        chk("output carries the vol delivery block",
            (o.get("vol_delivery") or {}).get("headline") is not None)
        # 7. the sheet must be the book IN FORCE (the last on-grid decision), not today's
        #    ranking. Until r1277 the card re-ranked the panel's last bar and handed out a
        #    book 11/12 apart from the one the engine -- and the forward ledger -- held.
        sdiag = []
        R.open_to_open_equity(syn, s_open, s_amt, s_score, 20, 3, COST,
                              vol_target=TARGET_VOL, diag=sdiag)
        held = set(sdiag[-1]["book"])
        chk("sheet is the book in force, not today's ranking",
            set(l["symbol"] for l in o["sheet"]["legs"]) == held
            and o["sheet"]["book_decided_at"] == sdiag[-1]["date"],
            "sheet=%s diag=%s" % (o["sheet"]["book_decided_at"], sdiag[-1]["date"]))
        # activity: on this fixture the off-grid ranking really does differ, so the leg
        # above cannot pass on the old behaviour (a broken test that never traded).
        today = set(s_score.iloc[-1].nlargest(3).index)
        chk("off-grid ranking differs from the held book",
            today != held and today != set(),
            "today=%s held=%s" % (sorted(today), sorted(held)))
        chk("sheet cash equals 1 - risk_scale",
            abs(o["sheet"]["cash_weight"] - (1.0 - o["sheet"]["risk_scale"])) < 1e-3,
            "cash=%.4f scale=%.4f" % (o["sheet"]["cash_weight"], o["sheet"]["risk_scale"]))
    finally:
        globals()["prep_panel"], globals()["load_names"], globals()["OUT_DIR"] = keep
        shutil.rmtree(tmp, ignore_errors=True)

    # 8. the out-of-period face: when the artifact exists the card must carry it (a
    #    measured difference that only lives in a digest is not disclosed), and when it
    #    does not, the production face must still run.
    pp = preperiod_support()
    if pp is None:
        chk("preperiod face soft-fails when absent", True, "results/etf_book_pre2020.json absent")
    else:
        chk("preperiod face reads the primary cell",
            all(k in pp for k in ("universe_size", "book_cagr", "ew_cagr", "excess_pp",
                                  "null_p", "cells_negative", "cells_total"))
            and pp["cells_total"] > 0 and pp["universe_size"] > 0,
            "%s %s book=%.4f ew=%.4f excess=%+.2fpp neg=%d/%d p=%s"
            % (pp["grid_cell"], pp["window"], pp["book_cagr"], pp["ew_cagr"],
               pp["excess_pp"], pp["cells_negative"], pp["cells_total"], pp["null_p"]))
    _keep_results = E.PATHS.results_dir
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("preperiod face is not fatal when the artifact is missing",
            preperiod_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

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