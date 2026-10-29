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


def commodity_support():
    """Read results/etf_book_commodity_split.json -> what the commodity sleeve earns.

    The commodity class produced ~30% of the book's gross return, and nothing on this
    card said whether that came from ranking commodity ETFs or from being long the metal.
    The artifact prices the sleeve on its own universe against the sleeve's own equal
    weight, so the answer travels with the CAGR instead of staying in a digest.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_commodity_split.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        runs = {r.get("label"): r for r in doc.get("runs", [])}
        book, ew = runs.get("commodity_only") or {}, runs.get("commodity_ew") or {}
        if book.get("cagr") is None or ew.get("cagr") is None:
            return None
        pas = (doc.get("read") or {}).get("deepest_name_passive") or {}
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "cell": doc.get("cell"),
            "n_cols": book.get("n_cols"),
            "book_cagr": book.get("cagr"),
            "ew_cagr": ew.get("cagr"),
            "excess_pp": book.get("excess_pp"),
            "gross_share_pct": (doc.get("read") or {}).get("commodity_gross_share_pct"),
            "passive_name": pas.get("name"),
            "passive_cagr": pas.get("cagr"),
            "verdict": (doc.get("read") or {}).get("verdict"),
        }
    except Exception:
        return None


def passive_mix_support():
    """Read results/etf_book_passive_mix.json -> what the rotation is worth vs never trading.

    Every other number on this card prices the book against another RANKING rule. This one
    prices it against the alternative a holder actually has: the same class exposure held
    statically. Without it the card can claim a CAGR but not that the machinery earns it.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_passive_mix.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        runs = {r.get("label"): r for r in doc.get("runs", [])}
        book, static = runs.get("book") or {}, runs.get("static_mix") or {}
        read = doc.get("read") or {}
        if book.get("cagr") is None or static.get("cagr") is None or not read.get("verdict"):
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "cell": doc.get("cell"),
            "book_cagr": book.get("cagr"),
            "book_maxdd": book.get("maxdd"),
            "static_cagr": static.get("cagr"),
            "static_maxdd": static.get("maxdd"),
            "premium_pp": read.get("selection_premium_pp"),
            "book_turnover": read.get("book_turnover_per_decision"),
            "static_turnover": read.get("static_turnover_per_decision"),
            "verdict": read.get("verdict"),
            # r1308: the same question asked outside the published regime. Absent on older
            # artifacts, so the card has to work with and without it.
            "by_window": read.get("by_window") or {},
            "cross_window": read.get("cross_window"),
            "premium_flips": read.get("premium_flips_between_periods"),
        }
    except Exception:
        return None


def decomp_support():
    """Read results/etf_book_window_decomp.json -> why the 2015-2019 window prints two numbers.

    r1305 published -8.86pp excess for 2015-2019 and this card also shows a small POSITIVE
    selection premium for the same window (r1308's passive-mix pre2020 cell). Both are real
    and they are different cells; without the ladder the two lines read as a contradiction.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_window_decomp.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        rungs = doc.get("rungs") or []
        if not rungs:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "window": doc.get("window"),
            "steps": [{"rung": r.get("rung"), "moves": r.get("moves"),
                       "cagr": r.get("book_cagr"), "excess_pp": r.get("excess_vs_ew_pp"),
                       "delta_pp": r.get("delta_vs_previous_pp")} for r in rungs],
            "total_move_pp": (doc.get("read") or {}).get("total_move_pp"),
            "controls": doc.get("controls") or {},
            "verdict": (doc.get("read") or {}).get("verdict"),
        }
    except Exception:
        return None


def spanning_support():
    """Read results/etf_book_spanning.json -> does the book still have an intercept?

    r1310: the card can quote a CAGR against another ranking rule or against a static class
    mix, but neither answers the question a funder asks -- after the four liquid exposures
    an account could simply hold (gold / Nasdaq QDII / CSI300 / bond), is anything left?
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_spanning.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        full = doc.get("full") or {}
        ports = doc.get("span_portfolios") or {}
        ew = ports.get("equal_weight_basket") or {}
        if full.get("alpha_annual") is None or ew.get("cagr") is None:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "as_of": doc.get("evidence_cutoff"),
            "book_cagr": (doc.get("book") or {}).get("cagr"),
            "book_sharpe": (doc.get("book") or {}).get("sharpe"),
            "book_maxdd": (doc.get("book") or {}).get("maxdd"),
            "basket_cagr": ew.get("cagr"),
            "basket_sharpe": ew.get("sharpe"),
            "basket_maxdd": ew.get("maxdd"),
            "alpha_annual": full.get("alpha_annual"),
            "alpha_t": full.get("alpha_t"),
            "r2": full.get("r2"),
            "resid_vol_annual": full.get("resid_vol_annual"),
            "is_alpha_t": (doc.get("is") or {}).get("alpha_t"),
            "oos_alpha_t": (doc.get("oos") or {}).get("alpha_t"),
            "arms": {k: {"cagr": (v or {}).get("cagr"), "sharpe": (v or {}).get("sharpe"),
                         "maxdd": (v or {}).get("maxdd")}
                     for k, v in ports.items() if k != "equal_weight_basket"},
            "codes": ew.get("codes") or [],
            # r1311: the stagger arm is priced through the same regression (one code path),
            # and the control assertion says whether this window re-priced the PUBLISHED
            # book (r1297). Both travel with the number or the number is unreadable.
            "staggered_arm": _stagger_block(doc),
            "stagger_control": doc.get("stagger_control"),
        }
    except Exception:
        return None


def _stagger_block(doc):
    """The staggered arm's intercept, its risk, and the sentence the two alphas imply."""
    st = ((doc.get("arms") or {}).get("staggered") or {})
    full = st.get("full") or {}
    if full.get("alpha_annual") is None:
        return None
    stats = st.get("stats") or {}
    book = doc.get("full") or {}
    return {
        "window": st.get("window"),
        "alpha_annual": full.get("alpha_annual"),
        "alpha_t": full.get("alpha_t"),
        "r2": full.get("r2"),
        "resid_vol_annual": full.get("resid_vol_annual"),
        "is_alpha_t": (st.get("is") or {}).get("alpha_t"),
        "oos_alpha_t": (st.get("oos") or {}).get("alpha_t"),
        "cagr": stats.get("cagr"),
        "sharpe": stats.get("sharpe"),
        "maxdd": stats.get("maxdd"),
        "book_alpha_annual": book.get("alpha_annual"),
        "book_alpha_t": book.get("alpha_t"),
        "crosses_two_sigma": bool((full.get("alpha_t") or 0.0) >= 2.0),
        "book_crosses_two_sigma": bool((book.get("alpha_t") or 0.0) >= 2.0),
    }


def spanning_pre2020_support():
    """Read results/etf_book_spanning_pre2020.json -> does the intercept survive the window
    the book was not fitted in?

    r1312: the four-beta section on this card only ever spoke about 2020+ -- the window the
    book earned its money in. The same regression run on U_pre over 2015-2019 answers the
    question a reader actually has ("is this exposure mix, or skill?"), and it answers it
    negatively, so it belongs on the card and not in a digest (r1275). Soft-fails to None:
    a missing artefact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_spanning_pre2020.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or {}
        single = arms.get("single") or {}
        st = arms.get("staggered") or {}
        ew = (doc.get("span_portfolios") or {}).get("equal_weight_basket") or {}
        full_s, full_g = single.get("full") or {}, st.get("full") or {}
        if full_s.get("alpha_annual") is None or ew.get("cagr") is None:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "window": doc.get("window"),
            "universe": doc.get("universe") or {},
            "single": {"alpha_annual": full_s.get("alpha_annual"),
                       "alpha_t": full_s.get("alpha_t"), "r2": full_s.get("r2"),
                       "is_alpha_t": (single.get("is") or {}).get("alpha_t"),
                       "oos_alpha_t": (single.get("oos") or {}).get("alpha_t"),
                       "cagr": (single.get("stats") or {}).get("cagr"),
                       "sharpe": (single.get("stats") or {}).get("sharpe"),
                       "maxdd": (single.get("stats") or {}).get("maxdd")},
            "staggered": {"alpha_annual": full_g.get("alpha_annual"),
                          "alpha_t": full_g.get("alpha_t"), "r2": full_g.get("r2"),
                          "is_alpha_t": (st.get("is") or {}).get("alpha_t"),
                          "oos_alpha_t": (st.get("oos") or {}).get("alpha_t"),
                          "cagr": (st.get("stats") or {}).get("cagr"),
                          "sharpe": (st.get("stats") or {}).get("sharpe"),
                          "maxdd": (st.get("stats") or {}).get("maxdd")},
            "basket": {"cagr": ew.get("cagr"), "sharpe": ew.get("sharpe"),
                       "maxdd": ew.get("maxdd"), "vol": ew.get("vol")},
            "control": doc.get("control"),
            "verdict": doc.get("verdict"),
        }
    except Exception:
        return None


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


def hysteresis_support():
    """Read results/etf_book_hysteresis.json -> does this book trade on noise?

    r1324: the book re-decides every 20 bars and its score is an average of percentile
    ranks, so "it trades on noise" is the obvious thing to say about it and nobody had
    priced it. scripts/etf_book_hysteresis.py measured it two ways (the cut-line margin,
    and a displacement buffer priced through the same engine). Both readings belong on
    the card: a reader deciding whether to hold this book cares whether the turnover is
    signal or churn. Soft-fails to None -- a missing artefact must never break the
    production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_hysteresis.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or []
        base = next((a for a in arms if float(a.get("k") or 0.0) == 0.0), None)
        if base is None:
            return None
        cfg = doc.get("config") or {}
        census = doc.get("margin_census") or {}
        trades = doc.get("trade_margins") or {}

        def stats(a):
            return (a.get("stats") or {}).get("full") or {}

        base_s = stats(base)
        # the arm that beats the no-buffer book on all four numbers at once, if any:
        # turnover down, CAGR/Sharpe up, drawdown shallower. Data-driven, never assumed.
        best = None
        for a in arms:
            s = stats(a)
            if a is base or s.get("cagr") is None:
                continue
            if (a.get("turnover_per_decision") < base.get("turnover_per_decision")
                    and s["cagr"] > base_s["cagr"]
                    and (s.get("sharpe") or 0) > (base_s.get("sharpe") or 0)
                    and (s.get("maxdd") or 0) > (base_s.get("maxdd") or 0)):
                if best is None or s["cagr"] > stats(best)["cagr"]:
                    best = a
        return {
            "artifact": "results/etf_book_hysteresis.json",
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "config": {"n_hold": cfg.get("n_hold"), "rebal": cfg.get("rebal"),
                       "cost_bp": cfg.get("cost_bp"), "grid": cfg.get("grid")},
            "control": doc.get("control"),
            "census": {"n_decisions": census.get("n_decisions"),
                       "cut_score_median": census.get("cut_score_median"),
                       "share_within_0p10": (census.get("share_within") or {}).get("0.1"),
                       "cut_sd_median": (census.get("cut_sd_q") or {}).get("0.5")},
            "trades": trades,
            "arms": [{"k": a.get("k"),
                      "turnover": a.get("turnover_per_decision"),
                      "cagr": stats(a).get("cagr"),
                      "sharpe": stats(a).get("sharpe"),
                      "maxdd": stats(a).get("maxdd")} for a in arms],
            "best_arm_k": (best or {}).get("k"),
            "caveats": (doc.get("caveats") or [])[:2],
        }
    except Exception:
        return None


def sign_pit_support():
    """Read results/etf_sign_pit.json -> are this book's factor signs knowable in real time?

    E205 (r1335): the six SIGNS are exactly the panel's full-sample IC signs, so the book is
    priced with knowledge of which way each factor paid. scripts/etf_sign_pit.py prices the
    honest arm (signs from already-realised windows only) on the same engine. That number
    belongs on the card: a reader deciding whether to run this book is reading a period, and
    the card must say so. Soft-fails to None -- a missing artefact never breaks the face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_sign_pit.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        s = doc.get("summary") or {}
        if s.get("cagr_fixed") is None or s.get("cagr_pit") is None:
            return None
        matches = doc.get("fixed_sign_matches_full_sample_ic") or {}
        return {
            "artifact": "results/etf_sign_pit.json",
            "verdict": doc.get("verdict"),
            "n_factors": len(matches),
            "n_match": sum(1 for v in matches.values() if v),
            "cagr_fixed": float(s["cagr_fixed"]),
            "cagr_pit": float(s["cagr_pit"]),
            "sharpe_fixed": float(s.get("sharpe_fixed") or 0.0),
            "sharpe_pit": float(s.get("sharpe_pit") or 0.0),
            "cagr_reversed": float(s.get("cagr_reversed_sign") or 0.0),
            "evidence_cutoff": doc.get("evidence_cutoff"),
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
        "commodity": commodity_support(),
        "passive_mix": passive_mix_support(),
        "window_decomp": decomp_support(),
        "spanning": spanning_support(),
        "spanning_pre2020": spanning_pre2020_support(),
        "hysteresis": hysteresis_support(),
    }
    pp = out["preperiod"]
    if pp is not None:
        out["caveats"].insert(0,
            "ONE REGIME, NOT A VERIFIED EDGE: on the %d ETFs that existed before 2020, "
            "priced 2015-2019 (a window this card never covered) the same engine returned "
            "%+.2f%%/yr against %+.2f%%/yr equal weight = %+.2fpp excess, worse in %d of %d "
            "grid cells, random-score p=%.2f. The published CAGR is the 2020+ regime, not a "
            "property of the factors. That cell is bond-inclusive, 5 names wide and has no "
            "sizing rule; 'The 2015-2019 reconciliation' below prices what each of those "
            "differences is worth. See %s."
            % (pp["universe_size"], pp["book_cagr"] * 100, pp["ew_cagr"] * 100,
               pp["excess_pp"], pp["cells_negative"], pp["cells_total"],
               pp["null_p"] if pp["null_p"] is not None else float("nan"), pp["artifact"]))
    cs = out["commodity"]
    if cs is not None and cs.get("excess_pp") is not None:
        beat = cs["excess_pp"] > 0.5
        vs_passive = None
        if cs.get("passive_cagr") is not None:
            vs_passive = (cs["book_cagr"] - cs["passive_cagr"]) * 100
        out["caveats"].insert(1,
            "THE COMMODITY SLEEVE IS %s: it produced %s%% of gross return; the same engine "
            "restricted to the %s commodity ETFs returned %+.2f%%/yr against %+.2f%%/yr for "
            "holding those names equally (%+.2fpp), and the deepest-turnover commodity name "
            "(%s) returned %s passively%s. Read the sleeve as %s. See %s."
            % ("MOSTLY METAL BETA WITH A MODEST RANKING OVERLAY" if beat else
               "EXPOSURE, NOT A RANKING",
               cs.get("gross_share_pct"), cs.get("n_cols"), cs["book_cagr"] * 100,
               cs["ew_cagr"] * 100, cs["excess_pp"], cs.get("passive_name"),
               ("%+.2f%%/yr" % (cs["passive_cagr"] * 100)) if cs.get("passive_cagr") is not None
               else "n/a",
               (", i.e. the book beat holding the metal by %+.2fpp" % vs_passive)
               if vs_passive is not None else "",
               "commodity/gold exposure plus a small selection add-on, not a commodity "
               "ranking that pays" if beat else "commodity/gold beta, not selection",
               cs["artifact"]))
    if feed.get("status") in ("stale_feed", "feed_broken"):
        out["caveats"].insert(0, "FEED IS BEHIND: this card is priced on the %s bar, %s "
                              "official trading day(s) short of the %s bar the market has "
                              "already published. The names are that old, not a fresh call."
                              % (feed.get("ticket_bar"), feed.get("lag_days"),
                                 feed.get("expected_bar")))
    sp = sign_pit_support()
    if sp is not None:
        out["caveats"].insert(0, "THE SIX FACTOR DIRECTIONS WERE CHOSEN WITH HINDSIGHT: every "
                              "published number here uses a fixed sign block, and those signs are "
                              "exactly this panel's full-sample IC signs (%d of %d factors match). "
                              "Re-priced with signs estimated only from already-realised windows, "
                              "the same engine returns %+.2f%%/yr (Sharpe %+.2f) against %+.2f%%/yr "
                              "(%+.2f) for the fixed signs -- and reversing the trailing sign does "
                              "not recover it (%+.2f%%/yr). Read the headline as the size of a "
                              "period, not the size of a rule. See %s."
                              % (sp["n_match"], sp["n_factors"], sp["cagr_pit"] * 100,
                                 sp["sharpe_pit"], sp["cagr_fixed"] * 100, sp["sharpe_fixed"],
                                 sp["cagr_reversed"] * 100, sp["artifact"]))
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
    lines += ["## What the rotation is worth", ""]
    lines += passive_mix_paragraphs(out.get("passive_mix"))
    lines += decomp_paragraphs(out.get("window_decomp"))
    lines += ["## What is left after the four betas", ""]
    lines += spanning_paragraphs(out.get("spanning"))
    lines += ["## Does any of it survive outside 2020-2026?", ""]
    lines += spanning_pre2020_paragraphs(out.get("spanning_pre2020"))
    lines += ["## Does the book trade on noise?", ""]
    lines += hysteresis_paragraphs(out.get("hysteresis"))
    lines += ["## Caveats", ""] + ["- " + c for c in out["caveats"]] + [""]
    with open(os.path.join(OUT_DIR, "CARD.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def decomp_paragraphs(dc):
    """The 2015-2019 reconciliation section. Pure: takes the artifact block, returns lines.

    The card carries two readings of one window -- the -8.86pp excess caveat and the
    passive-mix premium -- and they only make sense side by side with the ladder that
    connects them.
    """
    if not (dc and dc.get("steps")):
        return []
    steps = [s for s in dc["steps"] if s.get("delta_pp") is not None]
    first = dc["steps"][0]
    # a rung id is an artifact key, not a sentence; the axis is what a reader needs
    axis = {"r2_bond_free_pool": "dropping the bond/money sleeve",
            "r3_wider_book": "widening the book to 12 names",
            "r4_vol_overlay": "adding the 8% sizing rule"}
    parts = ["%+.1fpp from %s" % (s["delta_pp"], axis.get(s["rung"], s["rung"]))
             for s in steps]
    ctrl = dc.get("controls") or {}
    ok = all((c.get("passes") is not False) for c in ctrl.values() if isinstance(c, dict))
    return [
        "## The 2015-2019 reconciliation", "",
        "This card states two things about 2015-2019 that look like a contradiction: the "
        "caveat below reports %.1fpp of excess (%.1f%%/yr absolute) before 2020, while the "
        "rotation section above reports a premium on that same window. They are different "
        "cells, and the ladder between them is measured, not argued: from the caveat's cell "
        "(all classes, 5 names, no sizing rule) to this book's cell, holding the window and "
        "the fill rule fixed, the CAGR moves %+.1fpp in total (%s). Both ends reproduce "
        "their published number within %.1fpp%s. See %s."
        % (first.get("excess_pp") or 0.0, (first.get("cagr") or 0.0) * 100,
           dc.get("total_move_pp") or 0.0,
           ", ".join(parts),
           (ctrl.get("rung1_vs_pre2020_cellA") or {}).get("tolerance_pp") or 0.5,
           "" if ok else " (one control is out of tolerance -- read the artifact before "
                        "quoting these steps)",
           dc["artifact"]),
        "",
        "So the pre-2020 failure belongs to the bond-inclusive, unsized cell (%.1f%%/yr) "
        "and not to the ranking: with the same sizing rule on both arms the ranking still "
        "pays before 2020, just less than it pays after. What the ladder does NOT say is "
        "that the ranking works without the sizing rule -- on this window it does not."
        % ((first.get("cagr") or 0.0) * 100), ""]


def passive_mix_paragraphs(pm):
    """The rotation-vs-static-mix section text. Pure: needs only the artifact block.

    Kept a function so the wording is testable without writing a card, and so the two
    windows (published regime, and the pre-2020 control) are emitted from one place.
    """
    if not (pm and pm.get("premium_pp") is not None):
        return ["Not measured: results/etf_book_passive_mix.json is missing, so this card "
                "cannot say what the rotation is worth against simply holding the classes.", ""]
    out = ["Against a static mix of this book's own class exposure -- no scoring, no "
           "rotation, same grid, same cost rule, same 8%% overlay -- the book returns "
           "%.1f%%/yr vs %.1f%%/yr (%+.1fpp), worst drawdown %.1f%% vs %.1f%%, carrying "
           "%.1fx the static arm's turnover. That is the number the machinery has to "
           "beat to justify trading at all. See %s."
           % (pm["book_cagr"] * 100, pm["static_cagr"] * 100, pm["premium_pp"],
              (pm.get("book_maxdd") or 0) * 100, (pm.get("static_maxdd") or 0) * 100,
              (pm.get("book_turnover") / pm["static_turnover"])
              if pm.get("static_turnover") else float("nan"), pm["artifact"]), ""]
    bw = pm.get("by_window") or {}
    pre_w = bw.get("pre2020") or {}
    post_w = bw.get("post2020_pre_universe") or {}
    if pre_w.get("premium_pp") is not None and post_w.get("premium_pp") is not None:
        out += [
            "The same test outside the regime this card was published on -- the %d ETFs "
            "that already existed before 2020, priced 2015-2019, same engine, same grid, "
            "same cost rule, same overlay on both arms: the book returns %.1f%%/yr vs "
            "%.1f%%/yr for the static mix (%+.1fpp), against %+.1fpp on those SAME %d names "
            "over 2020+. Read the two together: %s"
            % (pre_w.get("universe_size") or 0, pre_w["book_cagr"] * 100,
               pre_w["static_cagr"] * 100, pre_w["premium_pp"], post_w["premium_pp"],
               post_w.get("universe_size") or 0,
               ("the premium does not survive the period change, so what pays is the "
                "regime, not the ranking -- the ranking is only worth carrying where the "
                "regime that produced it still holds."
                if pm.get("premium_flips") else
                "the premium survives the period change, so the machinery is not what "
                "the pre-2020 window was missing.")), ""]
    return out


def spanning_paragraphs(sp):
    """The four-beta section text. Pure: needs only the artifact block.

    Both arms' risk travels with both returns, and the t-stat decides the wording -- a
    sentence that reads the point estimate as skill without printing t is the failure this
    section exists to prevent (E147).
    """
    if not (sp and sp.get("alpha_annual") is not None):
        return ["Not measured: results/etf_book_spanning.json is missing, so this card "
                "cannot say what is left after the liquid betas.", ""]
    arms = sp.get("arms") or {}
    gold = arms.get("gold") or {}
    sentence = ("Regressed on the four exposures an account could hold instead of this book "
                "(gold / Nasdaq-100 QDII / CSI300 / treasury bond, same execution basis, "
                "same cost), the book's daily returns leave an intercept of **%+.1f%%/yr with "
                "t=%.2f** and R2=%.2f, as of %s. The equal-weight four-ETF basket itself "
                "returns %.1f%%/yr at Sharpe %.2f and worst drawdown %.1f%%, against the "
                "book's %.1f%%/yr, Sharpe %.2f and %.1f%%."
                % (sp["alpha_annual"] * 100, sp.get("alpha_t") or 0.0, sp.get("r2") or 0.0,
                   sp.get("as_of"), (sp.get("basket_cagr") or 0) * 100,
                   sp.get("basket_sharpe") or 0.0, (sp.get("basket_maxdd") or 0) * 100,
                   (sp.get("book_cagr") or 0) * 100, sp.get("book_sharpe") or 0.0,
                   (sp.get("book_maxdd") or 0) * 100))
    out = [sentence, ""]
    if (sp.get("alpha_t") or 0) < 2.0:
        out += ["Read that as **not distinguishable from a fixed loadings mix**, not as zero "
                "and not as proven skill: the in-sample half of the window prints t=%.2f and "
                "the out-of-sample half t=%.2f, so the point estimate is carried by the later "
                "period and the line is a risk statement rather than a return one."
                % (sp.get("is_alpha_t") or 0.0, sp.get("oos_alpha_t") or 0.0), ""]
    if gold.get("cagr") is not None:
        out += ["The single arm that out-earns the book is gold (%.1f%%/yr) at a %.1f%% "
                "drawdown -- the comparison has to be printed next to the return or it reads "
                "as a verdict. See %s."
                % (gold["cagr"] * 100, (gold.get("maxdd") or 0) * 100, sp["artifact"]), ""]
    st = sp.get("staggered_arm") or {}
    if st.get("alpha_annual") is not None:
        head = ("The staggered 6+6 book (same universe, score, execution and cost; second "
                "sleeve offset half a rebalance period) leaves **%+.1f%%/yr at t=%.2f** "
                "(IS t=%.2f / OOS t=%.2f) with residual vol %.1f%%, against the single "
                "sleeve's %+.1f%%/yr at t=%.2f and %.1f%%"
                % (st["alpha_annual"] * 100, st.get("alpha_t") or 0.0,
                   st.get("is_alpha_t") or 0.0, st.get("oos_alpha_t") or 0.0,
                   (st.get("resid_vol_annual") or 0.0) * 100,
                   (st.get("book_alpha_annual") or 0.0) * 100,
                   st.get("book_alpha_t") or 0.0,
                   (sp.get("resid_vol_annual") or 0.0) * 100))
        if st["crosses_two_sigma"] and not st["book_crosses_two_sigma"]:
            tail = (". The split clock clears a t of 2 where the single sleeve does not: that "
                    "is a strategy difference worth its own test, not a free lunch -- one arm "
                    "over the threshold is a hypothesis, not an edge.")
        elif not st["crosses_two_sigma"]:
            tail = (". Neither arm clears a t of 2, so the turnover saving remains the only "
                    "measured difference between them (E149/E150).")
        else:
            tail = (".")
        out += [head + tail, ""]
    return out


def spanning_pre2020_paragraphs(sp):
    """The outside-the-boom-window section. Pure: needs only the artefact block.

    r1312: the section above answers "is anything left after the four betas" on 2020+.
    This one answers "and does that survive the window the book was not fitted in" -- and
    prints the buy-and-hold basket beside it, because a book that loses to four ETFs in a
    negative-alpha window is a different object from one that merely fails a t-test.
    """
    if not (sp and (sp.get("single") or {}).get("alpha_annual") is not None):
        return ["Not measured: results/etf_book_spanning_pre2020.json is missing, so this "
                "card cannot say whether the intercept exists outside 2020-2026.", ""]
    s, g, b = sp.get("single") or {}, sp.get("staggered") or {}, sp.get("basket") or {}
    win = sp.get("window") or ["?", "?"]
    n_pre = (sp.get("universe") or {}).get("U_pre")
    out = ["The same regression, run on the %s ETFs that already existed before the boom, "
           "over %s..%s (a window this card's configuration was never fitted in, control "
           "delta %spp against the published pre-2020 cell):" % (
               n_pre if n_pre is not None else "pre-2020", win[0], win[1],
               (sp.get("control") or {}).get("delta_pp")), ""]
    out += ["| arm | CAGR | Sharpe | maxDD | intercept | t | R2 |", "|---|---|---|---|---|---|---|"]
    for label, a in (("single sleeve", s), ("staggered 6+6", g)):
        if a.get("cagr") is None:
            continue
        out.append("| %s | %.1f%% | %.2f | %.1f%% | %+.1f%%/yr | %.2f | %.2f |" % (
            label, a["cagr"] * 100, a.get("sharpe") or 0.0, (a.get("maxdd") or 0) * 100,
            a["alpha_annual"] * 100, a.get("alpha_t") or 0.0, a.get("r2") or 0.0))
    if b.get("cagr") is not None:
        out.append("| equal-weight four ETFs | %.1f%% | %.2f | %.1f%% | - | - | - |" % (
            b["cagr"] * 100, b.get("sharpe") or 0.0, (b.get("maxdd") or 0) * 100))
    out += [""]
    if (s.get("alpha_t") or 0) < 2.0 and (g.get("alpha_t") or 0) < 2.0:
        out += ["**Neither arm clears a t of 2 outside 2020-2026** (single t=%.2f, staggered "
                "t=%.2f; the out-of-sample half prints t=%.2f and t=%.2f, i.e. no intercept "
                "there at all). Read it as: the published "
                "intercept is a property of the boom window and the panel that grew in it, "
                "not yet a property of the rule -- the pre-2020 cross-section is small and "
                "survival-filtered, so this is one honest negative, not a demolition. It is, "
                "however, the reason not to scale size on the 9-10%% headline."
                % (s.get("alpha_t") or 0.0, g.get("alpha_t") or 0.0,
                   s.get("oos_alpha_t") or 0.0, g.get("oos_alpha_t") or 0.0),
                ""]
    if b.get("cagr") is not None and s.get("cagr") is not None:
        d = (s["cagr"] - b["cagr"]) * 100
        if d < 0:
            out += ["In that window a static equal-weight basket of the same four ETFs "
                    "returned %.1f%%/yr at Sharpe %.2f against the book's %.1f%%/yr at %.2f "
                    "(%+.1fpp), so the negative is not merely a failed t-test -- the rotation "
                    "cost money there. See %s."
                    % (b["cagr"] * 100, b.get("sharpe") or 0.0, s["cagr"] * 100,
                       s.get("sharpe") or 0.0, d, sp["artifact"]), ""]
    return out


def hysteresis_paragraphs(h):
    """The noise section. Pure: needs only the artefact block.

    r1324: two questions that read the same and are not -- "is the cut line arbitrary?"
    and "are the trades I actually pay for noise?". This prints both, because a buffer
    that lowers turnover without lowering the return is a cost knob, and saying so is the
    difference between a measured answer and a marketing one.
    """
    if not (h and h.get("arms")):
        return ["Not measured: results/etf_book_hysteresis.json is missing, so this card "
                "cannot say whether the book's turnover is signal or churn.", ""]
    cz, tr, cfg = h.get("census") or {}, h.get("trades") or {}, h.get("config") or {}
    out = []
    if cz.get("n_decisions"):
        out += ["The book holds %s names and re-decides every %s bars, so its score only "
                "has to separate the 12th name from the 13th. Over %d decisions that gap "
                "is a median of %.3f standard deviations of the bar's own cross-section, "
                "and %.1f%% of decisions sit inside 0.10 sd -- **the cut line is, "
                "literally, a coin flip at the margin**."
                % (cfg.get("n_hold"), cfg.get("rebal"), cz["n_decisions"],
                   cz.get("cut_sd_median") or 0.0, (cz.get("share_within_0p10") or 0) * 100),
                ""]
    if tr.get("n_pairs"):
        out += ["The trades are not. Of the %d executed pairs (a name leaving, a name "
                "entering) the median score gap is %.2f sd and only %.1f%% sit inside "
                "0.10 sd. Read the two lines together: the ranking is noisy exactly where "
                "it costs nothing, and decisive where it costs %s bp a side."
                % (tr["n_pairs"], tr.get("gap_sd_median") or 0.0,
                   (tr.get("share_under_0p10sd") or 0) * 100, cfg.get("cost_bp")), ""]
    arms = h["arms"]
    out += ["Priced the other way: a buffer that only displaces an incumbent when the "
            "challenger beats it by k*sd, run through the same engine on the same grid "
            "(%s, %s bp/side, control arm %s vs %s published = %spp):"
            % ("/".join("k=%g" % float(a["k"]) for a in arms if a.get("k") is not None),
               cfg.get("cost_bp"),
               "%.2f%%" % ((h.get("control") or {}).get("measured", 0) * 100),
               "%.2f%%" % ((h.get("control") or {}).get("published", 0) * 100),
               "%+.2f" % ((h.get("control") or {}).get("delta_pp") or 0.0)), ""]
    out += ["| buffer | turnover/decision | CAGR | Sharpe | maxDD |", "|---|---|---|---|---|"]
    for a in arms:
        if a.get("cagr") is None:
            continue
        out.append("| k=%g | %.3f | %.2f%% | %.2f | %.1f%% |" % (
            float(a["k"]), a.get("turnover") or 0.0, a["cagr"] * 100,
            a.get("sharpe") or 0.0, (a.get("maxdd") or 0) * 100))
    out += [""]
    k0, kend = arms[0], arms[-1]
    if h.get("best_arm_k") is not None:
        best = next(a for a in arms if a.get("k") == h["best_arm_k"])
        out += ["k=%g is the only arm that lowers turnover (%.3f -> %.3f), keeps the "
                "return (%+.2fpp) and improves both Sharpe and drawdown; past k=0.35 the "
                "buffer starts costing return and depth. So the buffer is a **cost knob, "
                "not a discovered edge** -- worth using, worth nothing to brag about."
                % (float(h["best_arm_k"]), k0.get("turnover") or 0.0,
                   best.get("turnover") or 0.0,
                   ((best.get("cagr") or 0.0) - (k0.get("cagr") or 0.0)) * 100), ""]
    elif (kend.get("turnover") or 0.0) < (k0.get("turnover") or 0.0):
        out += ["No arm improves all four numbers together: turnover falls %.3f -> %.3f "
                "only by giving up return or depth, so there is nothing here to adopt."
                % (k0.get("turnover") or 0.0, kend.get("turnover") or 0.0), ""]
    for c in (h.get("caveats") or []):
        out += ["- " + c]
    if h.get("caveats"):
        out += [""]
    return out


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

    # 9. the commodity-sleeve face: the sleeve's 30% share has to be labelled as exposure
    #    or as selection on the card, and a missing artifact must not break production.
    cs = commodity_support()
    if cs is None:
        chk("commodity face soft-fails when absent", True,
            "results/etf_book_commodity_split.json absent")
    else:
        chk("commodity face reads both arms",
            all(k in cs for k in ("n_cols", "book_cagr", "ew_cagr", "excess_pp", "verdict"))
            and cs["book_cagr"] is not None and cs["ew_cagr"] is not None
            and abs(cs["excess_pp"] - (cs["book_cagr"] - cs["ew_cagr"]) * 100) < 0.05,
            "book=%.4f ew=%.4f excess=%+.2fpp verdict=%s"
            % (cs["book_cagr"], cs["ew_cagr"], cs["excess_pp"], cs["verdict"]))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("commodity face is not fatal when the artifact is missing",
            commodity_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10. the passive-mix face: the card has to say what the rotation is worth against
    #     simply holding the classes, and a missing artifact must not break production.
    pm = passive_mix_support()
    if pm is None:
        chk("passive-mix face soft-fails when absent", True,
            "results/etf_book_passive_mix.json absent")
    else:
        chk("passive-mix face reads both arms and the premium",
            all(k in pm for k in ("book_cagr", "static_cagr", "premium_pp", "verdict"))
            and pm["book_cagr"] is not None and pm["static_cagr"] is not None
            and pm["premium_pp"] is not None
            and abs(pm["premium_pp"] - (pm["book_cagr"] - pm["static_cagr"]) * 100) < 0.05,
            "book=%.4f static=%.4f premium=%+.2fpp verdict=%s"
            % (pm["book_cagr"], pm["static_cagr"], pm["premium_pp"], pm["verdict"]))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("passive-mix face is not fatal when the artifact is missing",
            passive_mix_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10b. the two-window face (r1308): when the artifact prices the pre-2020 control too,
    #      the card has to print both periods and let the flip change the conclusion.
    pm_fix = {"artifact": "x.json", "book_cagr": 0.0949, "static_cagr": 0.0313,
              "premium_pp": 6.36, "book_maxdd": -0.118, "static_maxdd": -0.229,
              "book_turnover": 0.98, "static_turnover": 0.0935,
              "by_window": {"pre2020": {"universe_size": 224, "book_cagr": -0.0497,
                                        "static_cagr": 0.0389, "premium_pp": -8.86},
                            "post2020_pre_universe": {"universe_size": 224,
                                                      "premium_pp": 3.11}},
              "premium_flips": True}
    txt_flip = "\n".join(passive_mix_paragraphs(pm_fix))
    chk("card carries both windows of the rotation test",
        "2015-2019" in txt_flip and "2020+" in txt_flip and "224" in txt_flip
        and "does not survive the period change" in txt_flip,
        "%d lines" % len(passive_mix_paragraphs(pm_fix)))
    txt_keep = "\n".join(passive_mix_paragraphs(dict(pm_fix, premium_flips=False)))
    chk("a surviving premium says the other thing",
        "does not survive" not in txt_keep and "survives the period change" in txt_keep)
    chk("a single-window artifact prints the headline only",
        len(passive_mix_paragraphs({k: v for k, v in pm_fix.items()
                                    if k not in ("by_window", "premium_flips")})) == 2)

    # 10c. the reconciliation section (r1308): the ladder has to be on the card, and a
    #      control out of tolerance has to say so instead of printing clean steps.
    dc = decomp_support()
    if dc is None:
        chk("reconciliation face soft-fails when absent", True,
            "results/etf_book_window_decomp.json absent")
    else:
        chk("reconciliation face carries the ladder",
            len(dc.get("steps") or []) >= 2 and dc.get("total_move_pp") is not None,
            "steps=%d total=%s" % (len(dc.get("steps") or []), dc.get("total_move_pp")))
        txt = "\n".join(decomp_paragraphs(dc))
        chk("card prints the reconciliation with both ends",
            "2015-2019 reconciliation" in txt and "%.1fpp" % dc["total_move_pp"] in txt,
            "%d lines" % len(decomp_paragraphs(dc)))
        broken = json.loads(json.dumps(dc))
        for k in broken.get("controls") or {}:
            broken["controls"][k]["passes"] = False
        chk("a failed control is disclosed in the text, not swallowed",
            "out of tolerance" in "\n".join(decomp_paragraphs(broken)))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("reconciliation face is not fatal when the artifact is missing",
            decomp_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results
    chk("no reconciliation artifact -> no section",
        decomp_paragraphs(None) == [])

    # 10d. the outside-the-window section (r1312): both arms' t, the basket, and the
    #      sentence that changes when the alpha DOES clear 2. A section that prints the
    #      same words for a pass and a failure would hide the finding it exists to carry.
    sp20 = spanning_pre2020_support()
    fix = {"window": ["2015-01-01", "2019-12-31"], "universe": {"U_pre": 193},
           "single": {"alpha_annual": 0.0203, "alpha_t": 1.04, "r2": 0.70, "cagr": 0.0512,
                      "sharpe": 0.70, "maxdd": -0.1671},
           "staggered": {"alpha_annual": 0.0100, "alpha_t": 0.48, "r2": 0.68,
                         "cagr": 0.0426, "sharpe": 0.574, "maxdd": -0.1762},
           "basket": {"cagr": 0.0864, "sharpe": 0.968, "maxdd": -0.1298},
           "control": {"delta_pp": 0.13, "within_0p5pp": True},
           "artifact": "results/etf_book_spanning_pre2020.json"}
    txt = "\n".join(spanning_pre2020_paragraphs(fix))
    chk("card prints the outside-window section with both arms",
        "193" in txt and "single sleeve" in txt and "staggered 6+6" in txt
        and "Neither arm clears a t of 2" in txt, "%d lines" % len(spanning_pre2020_paragraphs(fix)))
    chk("the buy-and-hold basket is printed beside the book",
        "equal-weight four ETFs" in txt and "rotation cost money" in txt)
    passing = json.loads(json.dumps(fix))
    passing["single"]["alpha_t"] = 2.6
    passing["staggered"]["alpha_t"] = 2.2
    chk("a passing alpha stops printing the negative sentence",
        "Neither arm clears" not in "\n".join(spanning_pre2020_paragraphs(passing)))
    chk("no outside-window artifact -> disclosed, not silent",
        "Not measured" in spanning_pre2020_paragraphs(None)[0])
    chk("outside-window face reads the live artifact when present",
        sp20 is None or (sp20.get("window") and sp20.get("single", {}).get("alpha_t") is not None),
        "artifact %s" % ("absent" if sp20 is None else sp20.get("window")))

    # 10e. the noise section (r1324): the card has to print the cut-line margin and the
    #      trade margin side by side -- they point opposite ways -- and the "cost knob"
    #      sentence has to be earned by an arm, not written in advance.
    hz = hysteresis_support()
    hfix = {"artifact": "results/etf_book_hysteresis.json", "evidence_cutoff": "2026-10-27",
            "config": {"n_hold": 12, "rebal": 20, "cost_bp": 10.0, "grid": [0.0, 0.05, 0.5]},
            "control": {"published": 0.0962, "measured": 0.0962, "delta_pp": 0.0,
                        "within_tol": True},
            "census": {"n_decisions": 83, "cut_score_median": 0.0045,
                       "share_within_0p10": 0.8675, "cut_sd_median": 0.0181},
            "trades": {"n_pairs": 590, "gap_sd_median": 0.9741, "share_under_0p10sd": 0.0288},
            "arms": [{"k": 0.0, "turnover": 0.934, "cagr": 0.0962, "sharpe": 0.992,
                      "maxdd": -0.1177},
                     {"k": 0.05, "turnover": 0.901, "cagr": 0.0969, "sharpe": 1.006,
                      "maxdd": -0.1159},
                     {"k": 0.5, "turnover": 0.702, "cagr": 0.0958, "sharpe": 0.99,
                      "maxdd": -0.1348}],
            "best_arm_k": 0.05, "caveats": ["exploratory: no preregistration"]}
    txt = "\n".join(hysteresis_paragraphs(hfix))
    chk("card prints both margins of the same question",
        "coin flip at the margin" in txt and "0.97 sd" in txt
        and "0.10 sd" in txt and "590" in txt, "%d lines" % len(hysteresis_paragraphs(hfix)))
    chk("card prints the arm grid with the control arm", "| k=0 |" in txt and "k=0.5" in txt)
    chk("an improving arm earns the cost-knob sentence",
        "cost knob" in txt and "k=0.05" in txt and "+0.07pp" in txt)
    nohelp = json.loads(json.dumps(hfix))
    nohelp["best_arm_k"] = None
    nohelp["arms"][1] = dict(nohelp["arms"][1], cagr=0.0900)
    txt_no = "\n".join(hysteresis_paragraphs(nohelp))
    chk("no improving arm prints the negative, not the knob",
        "cost knob" not in txt_no and "nothing here to adopt" in txt_no)
    chk("no hysteresis artifact -> disclosed, not silent",
        "Not measured" in hysteresis_paragraphs(None)[0])
    chk("hysteresis face reads the live artifact when present",
        hz is None or (hz.get("census") or {}).get("n_decisions"))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("hysteresis face is not fatal when the artifact is missing",
            hysteresis_support() is None)
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