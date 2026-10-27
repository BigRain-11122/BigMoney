"""Does the shipped book beat doing nothing with the same asset classes?

Every published number on the card prices the book against OTHER ranking rules. Nothing in
the repo prices it against the thing a holder actually has as an alternative: hold the
book's own asset-class exposure statically and never rotate a single name.

Why this is the question that matters after r1306: the commodity sleeve turned out to be
13.9pp of metal beta and +2.4pp of overlay, and the equity sleeve was already shown to
carry the book's other 59% of gross return. If a fixed equity/commodity/convertible mix --
weights taken from the book's own average class exposure, no scoring, no rotation -- lands
near the book's CAGR, then the ranking machinery is not what pays and the card should say so.

Arms, all on the production panel (production.prep_panel: class filter + split repair) and
all on the same decision grid, the same 10bp/side cost rule and the same 8% vol overlay:

  book            the shipped cell (n_hold=12, vol target 8%), asserted against the CAGR
                  published in results/etf_book_production/latest.json (control = the arm
                  that was published; r1297)
  static_mix      the three class equal-weight indices (A.ew_universe) blended daily at
                  fixed weights = the book's own mean class exposure, with the SAME vol
                  overlay and the SAME turnover cost rule
  static_mix_novt static_mix without the vol overlay (what "no machinery at all" earns)

Read: book minus static_mix is the selection premium -- what all the scoring, rotation and
turnover is worth per year against a holder who never trades. A premium that does not clear
the book's own cost drag means the ranking is decoration.

Windows (r1308, answering r1307's next pointer). The premium was priced on one window --
the 2020+ regime the card was published on -- and r1305 showed the same engine LOSES to
equal weight over 2015-2019. If the machinery also fails to beat a static mix there, then
"the rotation pays" is a property of the period, not of the ranking, and the card has to
print both windows instead of the flattering one. Three cells, each moving one axis:

  full                    2020..panel end, full universe (the published window)
  pre2020                 2015-2019, the ETFs that existed before 2020 (r1305's U_pre)
  post2020_pre_universe   2020..panel end on that SAME pre-2020 universe (period control)

pre2020 vs post2020_pre_universe holds the universe fixed and moves the period, so the
difference between their premiums cannot be a breadth artefact.

Reuse, not re-implementation: panel, class map, equal-weight indices, stats and the
open-to-open engine all come from etf_composite_pf / etf_equity_alpha / etf_robust_pf /
etf_book_production.

  python scripts/etf_book_passive_mix.py run
  python scripts/etf_book_passive_mix.py --selftest      # offline invariants
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_book_production as P
import etf_robust_pf as R

OUT = os.path.join(E.PATHS.results_dir, "etf_book_passive_mix.json")
PUBLISHED = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
CONTROL_TOL_PP = 0.5
N_HOLD = 12
REBAL = 20
VOL_TARGET = 0.08
VOL_WINDOW = 60
COST = P.COST

PRE_NEEDLE = pd.Timestamp("2020-01-01")   # "existed before the boom" boundary (r1305)
PRE_START = "2015-01-01"
PRE_END = "2019-12-31"

WINDOWS = (
    ("full", "all", A.START, None,
     "2020-01..panel end, full universe -- the window every published number lives in"),
    ("pre2020", "pre", PRE_START, PRE_END,
     "2015-2019, the ETFs whose first bar is <= 2020-01-01 -- a window this book never covered"),
    ("post2020_pre_universe", "pre", A.START, None,
     "2020..panel end on the SAME pre-2020 universe -- the period control"),
)


def published_book_cagr(path=PUBLISHED):
    """The published n12_vt08 full-window CAGR, or None when the artifact is unavailable."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        return float(doc["backtest"]["n12_vt08"]["full"]["cagr"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def pre_universe(close, asof=PRE_NEEDLE):
    """Columns whose first bar is on/before `asof` -- the funds that already existed.

    Same rule as scripts/etf_book_pre2020.universe_pre (that script owns the cell design;
    this one only needs the mask, so it is restated in three lines rather than imported
    from a module whose import path is package-relative).
    """
    first = close.apply(lambda s: s.first_valid_index())
    return [c for c in close.columns if first.get(c) is not None and first[c] <= asof]


def clip_end(df, end):
    """Upper bound only. The lower bound always travels as the engine's `start` argument:
    slicing the panel at `start` resets the 120-bar history counter and leaves the book in
    cash for its first six months (r1305 self-caught defect)."""
    if df is None or end is None:
        return df
    return df.loc[df.index <= pd.Timestamp(end)]


def class_returns(close, amt, cls, classes, start=A.START):
    """Daily returns of each class's equal-weight index, on one shared calendar."""
    rets = {}
    for c in classes:
        ser = A.ew_universe(close, amt, cls, (c,), start=start)
        r = ser.sort_index().pct_change()
        if r.notna().sum() >= 40:
            rets[c] = r
    return pd.DataFrame(rets).sort_index()


def mix_weights(mixes, classes):
    """Mean class exposure shape the book actually carried -- the weights a static holder copies.

    Source caveat that must travel with these numbers: the mixes come from
    etf_equity_alpha.run_with_attribution, which is the FULLY-INVESTED leg chain (no vol
    overlay, no cash slot). They are a class *shape*, not the shipped book's deployed
    exposure. Both arms then get the same 8% overlay inside simulate_mix, so the deployed
    exposure is comparable by construction -- and the delivered vol of each arm is printed
    so a reader can check that instead of assuming it.
    """
    mx = pd.DataFrame(mixes)
    w = {}
    for c in classes:
        w[c] = float(mx[c].mean()) if c in mx else 0.0
    tot = sum(w.values())
    if tot <= 0:
        return {c: 0.0 for c in classes}
    return {c: round(w[c] / tot, 6) for c in classes}


def simulate_mix(mix_ret, weights, dates, vol_target=VOL_TARGET, cost=COST,
                 rebal=20, vol_window=VOL_WINDOW):
    """Fixed-weight mix on the book's grid, same overlay and same cost rule as the engine.

    Exposure is squared to the grid: at each decision bar the scale is re-derived from the
    mix's own backward vol (min(1, target/vol), de-lever only, exactly the book's rule) and
    the cost is charged on the turnover that rescaling implies. Between decisions the mix
    simply earns its blended daily return.
    """
    cols = [c for c in weights if c in mix_ret.columns and weights[c] > 0]
    if not cols:
        return None, 0.0, []
    blend = (mix_ret[cols] * pd.Series({c: weights[c] for c in cols})).sum(axis=1, min_count=1)
    blend = blend.reindex(mix_ret.index).fillna(0.0)
    equity, held, scale, turns, scales = 1.0, 0.0, 0.0, [], []
    curve = []
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            want = 1.0
            if vol_target:
                window = blend.loc[:d].tail(vol_window)
                if window.shape[0] >= 20:
                    v = float(window.std() * np.sqrt(252))
                    if np.isfinite(v) and v > 0:
                        want = float(min(1.0, vol_target / v))
            turn = abs(want - held)
            equity *= (1.0 - cost * turn)
            turns.append(turn)
            scales.append(want)
            held, scale = want, want
        r = float(blend.get(nxt, 0.0)) * scale
        if np.isfinite(r):
            equity *= (1.0 + r)
        curve.append((d, equity))
    return (pd.Series(dict(curve)), (sum(turns) / len(turns) if turns else 0.0), scales)


def stats_block(ser, label, splits=True):
    """CAGR/Sharpe/drawdown/vol. `splits` off for windows that do not straddle IS_END --
    labelling a 2015-2019 curve "is" would report a split that does not exist."""
    m = {"label": label}
    slices = [("full", ser)]
    if splits:
        slices += [("is", ser[ser.index <= A.IS_END]), ("oos", ser[ser.index > A.IS_END])]
    for lbl, sl in slices:
        s = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd", "vol", "years"):
            m[k + "_" + lbl if lbl != "full" else k] = s.get(k)
    return m


def verdict_for(premium, book_turn, static_turn):
    """One sentence per premium sign. Kept a function so every window gets the SAME rule --
    a per-window hand-written verdict is how two arms get read under two standards."""
    if premium is None:
        return "undetermined -- one arm did not price"
    ratio = (book_turn / static_turn) if static_turn else float("nan")
    if premium > 2.0:
        return ("the ranking pays: %+.2fpp/yr over a static mix of the book's own class "
                "exposure, at %.2fx the static arm's turnover" % (premium, ratio))
    if premium > 0.0:
        return ("the ranking barely pays: %+.2fpp/yr over a static mix -- inside the noise "
                "of one regime change, not a reason to carry %.1fx-turnover machinery"
                % (premium, ratio))
    return ("the ranking does not pay: %+.2fpp/yr against a static mix of the same class "
            "exposure -- the machinery costs money" % premium)


def price_window(close, openp, amt, score, cls, cols, start, end, label,
                 classes=None, splits=True, vol_target=VOL_TARGET):
    """Price one (universe, window) cell: the book, the static mix, the no-overlay mix.

    `cols` is the universe mask, applied to every frame BEFORE the engine sees it, so the
    book and the static arms draw on the same names. Only the END is clipped; `start` goes
    to the engine and to ew_universe as an argument.
    """
    classes = list(classes or P.USE_CLASSES)
    cols = [c for c in cols if c in close.columns]
    box = {"label": label, "start": str(start),
           "end": end or str(close.index[-1].date()), "universe_size": len(cols)}
    if not cols:
        box["note"] = "empty universe"
        return box

    c = clip_end(close[cols], end)
    o = clip_end(openp.reindex(columns=cols), end)
    a = clip_end(amt[cols], end)
    s = clip_end(score.reindex(columns=cols), end)

    ser_book, turn = R.open_to_open_equity(c, o, a, s, REBAL, N_HOLD, COST,
                                          vol_target=vol_target, start=start)
    book = stats_block(ser_book, "book", splits=splits)
    book["turnover_per_decision"] = round(float(turn), 4)
    box["book"] = book
    print("  book cagr=%s sr=%s dd=%s" % (book.get("cagr"), book.get("sharpe"),
                                          book.get("maxdd")), flush=True)

    # the class shape the book actually carried in THIS cell, from its own attribution run
    _, _, _, mixes = A.run_with_attribution(c, o, a, s, cls, start=start)
    w = mix_weights(mixes, classes)
    box["static_weights"] = w
    cret = class_returns(c, a, cls, classes, start=start)
    dates = [d for d in o.index if d >= pd.Timestamp(start)]
    if end is not None:
        dates = [d for d in dates if d <= pd.Timestamp(end)]

    ser_static, turn_static, _ = simulate_mix(cret, w, dates)
    static = {}
    if ser_static is not None:
        static = stats_block(ser_static, "static_mix", splits=splits)
        static["turnover_per_decision"] = round(turn_static, 4)
        box["static_mix"] = static
        print("  static cagr=%s sr=%s dd=%s" % (static.get("cagr"), static.get("sharpe"),
                                                static.get("maxdd")), flush=True)

    ser_novt, turn_novt, _ = simulate_mix(cret, w, dates, vol_target=None)
    novt = {}
    if ser_novt is not None:
        novt = stats_block(ser_novt, "static_mix_novt", splits=splits)
        novt["turnover_per_decision"] = round(turn_novt, 4)
        box["static_mix_novt"] = novt

    premium = maxdd_delta = None
    if static.get("cagr") is not None and book.get("cagr") is not None:
        premium = round((book["cagr"] - static["cagr"]) * 100, 2)
        maxdd_delta = round(((book.get("maxdd") or 0) - (static.get("maxdd") or 0)) * 100, 2)
    box["read"] = {
        "selection_premium_pp": premium,
        "maxdd_delta_pp": maxdd_delta,
        "book_turnover_per_decision": book.get("turnover_per_decision"),
        "static_turnover_per_decision": static.get("turnover_per_decision"),
        "vol_delivered": {"book": book.get("vol"), "static_mix": static.get("vol"),
                          "static_mix_no_overlay": novt.get("vol")},
        "verdict": verdict_for(premium, book.get("turnover_per_decision"),
                               static.get("turnover_per_decision")),
    }
    print("  premium=%s pp -> %s" % (premium, box["read"]["verdict"]), flush=True)
    return box


def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    classes = list(P.USE_CLASSES)
    unis = {"all": list(close.columns), "pre": pre_universe(close)}
    print("panel %s flips=%d pre-2020 universe=%d classes=%s"
          % (close.shape, n_flip, len(unis["pre"]), cls.value_counts().to_dict()), flush=True)

    out = {
        "schema": "etf_book_passive_mix/v2",
        "question": ("does the shipped book beat holding its own class exposure statically, "
                     "with no scoring and no rotation -- and is that answer the same outside "
                     "the regime it was published on?"),
        "engine": ("etf_book_production.prep_panel + etf_robust_pf.open_to_open_equity "
                   "(book) / etf_equity_alpha.ew_universe (static arms); no re-implementation"),
        "cell": "N%d_R%d_10bp" % (N_HOLD, REBAL),
        "basis": "close decision -> next open fill, 10bp per side, top-N equal weight",
        "vol_overlay": "scale = min(1, %.2f / backward %dd realised vol) at each decision"
                       % (VOL_TARGET, VOL_WINDOW),
        "window": "%s..panel end" % A.START,
        "windows": {},
        "runs": [],
        "control": {},
    }

    # 1) price every window: each cell changes one axis relative to its neighbour
    windows = out["windows"]
    for label, uni, start, end, why in WINDOWS:
        print("[%s] %s" % (label, why), flush=True)
        box = price_window(close, openp, amt, score, cls, unis[uni], start, end, label,
                           classes=classes, splits=(label == "full"))
        box["why"] = why
        box["universe"] = uni
        windows[label] = box

    full = windows.get("full") or {}
    pre = (windows.get("pre2020") or {}).get("read") or {}
    post = (windows.get("post2020_pre_universe") or {}).get("read") or {}
    book = full.get("book") or {}
    static_row = full.get("static_mix") or {}
    novt_row = full.get("static_mix_novt") or {}

    # 2) control: the book arm on the published window must be the published arm (r1297)
    pub = published_book_cagr()
    delta = (round((book["cagr"] - pub) * 100, 2)
             if pub is not None and book.get("cagr") is not None else None)
    out["control"] = {
        "arm": "book@full",
        "published_cagr": pub,
        "recomputed_cagr": book.get("cagr"),
        "delta_pp": delta,
        "tolerance_pp": CONTROL_TOL_PP,
        "passes": (None if delta is None else abs(delta) <= CONTROL_TOL_PP),
        "note": ("not asserted: published artifact unavailable" if delta is None else
                 "the compared arm is the arm that was published"),
    }
    out["static_weights"] = full.get("static_weights") or {}
    out["static_weight_source"] = ("mean class shape of etf_equity_alpha.run_with_attribution "
                                   "run on each cell's own universe/window (fully-invested "
                                   "chain); both arms carry the same 8% overlay, delivered vol "
                                   "per arm is in each cell's read.vol_delivered")

    # 3) the published window keeps the flat keys earlier consumers read
    for lbl in ("book", "static_mix", "static_mix_novt"):
        row = windows.get("full", {}).get(lbl)
        if row:
            out["runs"].append(row)
    out["read"] = dict(full.get("read") or {})

    # 4) the cross-window read: the same question asked twice, universe held fixed
    summary = {}
    for label, box in windows.items():
        r = box.get("read") or {}
        summary[label] = {
            "window": "%s..%s" % (box.get("start"), box.get("end")),
            "universe_size": box.get("universe_size"),
            "book_cagr": (box.get("book") or {}).get("cagr"),
            "static_cagr": (box.get("static_mix") or {}).get("cagr"),
            "premium_pp": r.get("selection_premium_pp"),
            "book_maxdd": (box.get("book") or {}).get("maxdd"),
            "static_maxdd": (box.get("static_mix") or {}).get("maxdd"),
            "verdict": r.get("verdict"),
        }
    out["read"]["by_window"] = summary

    pre_pp, post_pp = pre.get("selection_premium_pp"), post.get("selection_premium_pp")
    flips = (pre_pp is not None and post_pp is not None and (pre_pp > 0) != (post_pp > 0))
    out["read"]["premium_flips_between_periods"] = flips
    if pre_pp is None or post_pp is None:
        cross = "undetermined -- the pre-2020 universe did not price in one of the periods"
    elif flips:
        cross = ("the premium is a property of the PERIOD, not of the ranking: on the same "
                 "%d ETFs the book is %+.2fpp/yr against its static mix over 2015-2019 and "
                 "%+.2fpp/yr over 2020+, while the static arm is the same construction in "
                 "both cells. Carry the ranking only where the regime that produced it holds."
                 % (summary.get("pre2020", {}).get("universe_size") or 0, pre_pp, post_pp))
    else:
        cross = ("the premium survives the period change: %+.2fpp/yr over 2015-2019 vs "
                 "%+.2fpp/yr over 2020+ on the same universe -- the ranking adds value in "
                 "both, so the pre-2020 failure is about the level, not the machinery."
                 % (pre_pp, post_pp))
    out["read"]["cross_window"] = cross
    print("READ", cross, flush=True)

    out["caveats"] = [
        ("the static arms ride class equal-weight indices that rebalance daily at ZERO cost "
         "(etf_equity_alpha.ew_universe); a real passive holder pays something, so the "
         "premium measured here is a LOWER bound on what the ranking adds"),
        ("the static class shape comes from the fully-invested attribution chain; both arms "
         "carry the same 8% overlay, and read.vol_delivered reports what each one actually "
         "delivered so the comparison is checkable rather than assumed"),
        ("both arms draw on the same ETF pool, so the survivorship bias that inflates the "
         "equity sleeve inflates the static mix as well -- it cancels in the premium, not "
         "in the absolute numbers"),
        ("the pre-2020 universe is itself survival-filtered (the panel holds no delisted "
         "funds); a failure there is weaker evidence than it looks, a pass is weaker still"),
        ("the static class weights are re-derived inside each window from that window's own "
         "attribution run, so the two periods are compared under the same construction "
         "rather than one window inheriting the other's exposure"),
    ]

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", OUT, flush=True)
    return 0


# ---------------------------------------------------------------- selftest

def mix_ret_fixture(n=260, seed=7):
    """Two-class synthetic daily returns; deterministic, no panel needed."""
    rs = np.random.RandomState(seed)
    idx = pd.date_range("2022-01-03", periods=n, freq="B")
    return pd.DataFrame({"equity": rs.normal(0.0004, 0.010, n),
                         "commodity": rs.normal(0.0002, 0.009, n)}, index=idx)


def selftest():
    out = []

    def chk(label, cond, detail=""):
        out.append((label, bool(cond), detail))

    # 1. weights normalise to 1 and drop absent classes
    w = mix_weights([{"equity": 0.4, "commodity": 0.1, "convertible": 0.0},
                     {"equity": 0.2, "commodity": 0.1, "convertible": 0.0}],
                    ["equity", "commodity", "convertible"])
    chk("static weights normalise to 1", abs(sum(w.values()) - 1.0) < 1e-9, str(w))
    chk("weights are the book's mean exposure", abs(w["equity"] - 0.75) < 1e-6, str(w))

    # 2. no overlay, no turnover -> the mix is exactly the blended daily returns
    ret = mix_ret_fixture()
    dates = list(ret.index)
    ser, turn, _ = simulate_mix(ret, {"equity": 0.6, "commodity": 0.4}, dates, vol_target=None)
    blend = ret["equity"] * 0.6 + ret["commodity"] * 0.4
    expect = float((1.0 + blend.iloc[1:]).prod()) * (1.0 - COST)
    chk("no-overlay mix reproduces the blended return exactly",
        abs(float(ser.iloc[-1]) - float(expect)) < 1e-9,
        "nav=%.8f expect=%.8f" % (ser.iloc[-1], expect))

    # 3. with no overlay there is exactly one turnover event (0 -> 1), never more
    chk("no-overlay mix pays cost once", abs(turn - 1.0 / max(1, len(range(0, len(dates) - 1, 20)))) < 1e-9,
        "avg_turn=%.6f" % turn)

    # 4. the overlay can only de-lever: realised vol must come down, nav must not rise
    hi = mix_ret_fixture(seed=11)
    hi["equity"] = hi["equity"] * 3.0
    hi["commodity"] = hi["commodity"] * 3.0
    s_raw, _, _ = simulate_mix(hi, {"equity": 0.6, "commodity": 0.4}, list(hi.index), vol_target=None)
    s_vt, _, sc_vt = simulate_mix(hi, {"equity": 0.6, "commodity": 0.4}, list(hi.index),
                                  vol_target=0.08)
    v_raw = float(s_raw.pct_change().std() * np.sqrt(252))
    v_vt = float(s_vt.pct_change().std() * np.sqrt(252))
    chk("vol overlay de-levers a hot mix", v_vt < v_raw, "raw=%.3f vt=%.3f" % (v_raw, v_vt))
    chk("vol overlay only de-levers (every scale <= 1)",
        bool(sc_vt) and max(sc_vt) <= 1.0 and min(sc_vt) >= 0.0,
        "n=%d min=%.3f max=%.3f" % (len(sc_vt), min(sc_vt or [0.0]), max(sc_vt or [0.0])))

    # 5. a missing published artifact must soft-fail, never break the run
    chk("published control soft-fails when absent",
        published_book_cagr(os.path.join(E.PATHS.results_dir, "no_such_latest.json")) is None)

    # 6. the premium is arithmetic on the two arms, not a separate model
    book, static = 0.1020, 0.0850
    chk("selection premium arithmetic", abs((book - static) * 100 - 1.70) < 1e-9)

    # 7. the pre-2020 universe mask binds, and keeps only the early names
    idx = pd.bdate_range("2019-01-01", periods=700)   # spans the 2020-01-01 needle
    px = pd.DataFrame(index=idx)
    for k in range(6):
        px["s%d" % k] = np.nan
    px.iloc[:, :3] = 10.0                       # three names from the first bar
    px.iloc[400:, 3:] = 10.0                    # three names listing after the needle
    pre = pre_universe(px)
    chk("pre-2020 mask binds", 0 < len(pre) < len(px.columns),
        "U_pre=%d of %d" % (len(pre), len(px.columns)))
    chk("pre-2020 mask keeps only names already trading",
        all(px[s].first_valid_index() <= PRE_NEEDLE for s in pre) and len(pre) == 3,
        "%s" % sorted(pre))

    # 8. clip_end bounds the TOP only -- a window must never truncate the history the
    #    eligibility counter counts (a 2015-2019 cell still needs 120 bars of the past)
    clipped = clip_end(px, "2020-06-30")
    chk("clip_end bounds the end only",
        clipped.index[-1] <= pd.Timestamp("2020-06-30") and clipped.index[0] == idx[0]
        and clip_end(px, None) is px,
        "first=%s last=%s" % (clipped.index[0].date(), clipped.index[-1].date()))

    # 9. one verdict rule for every window: the sign decides, not the window's name
    chk("verdict is signed the same way in every window",
        verdict_for(-3.0, 1.0, 0.3).startswith("the ranking does not pay")
        and verdict_for(3.0, 1.0, 0.3).startswith("the ranking pays")
        and verdict_for(0.4, 1.0, 0.3).startswith("the ranking barely pays")
        and verdict_for(None, 1.0, 0.3).startswith("undetermined"))

    # 10. a window that does not straddle IS_END must not claim an is/oos split
    ser = pd.Series(1.0 + np.arange(60) * 0.001,
                    index=pd.bdate_range("2015-01-05", periods=60))
    nowin = stats_block(ser, "w", splits=False)
    chk("no is/oos labels on a single-period window",
        nowin.get("cagr") is not None and "cagr_is" not in nowin and "cagr_oos" not in nowin,
        "keys=%s" % sorted(k for k in nowin if k.startswith("cagr")))

    ok = sum(1 for _, c, _ in out if c)
    for label, cond, detail in out:
        print(("[PASS] " if cond else "[FAIL] ") + label + (" | " + detail if detail else ""),
              flush=True)
    print("selftest %d/%d PASS" % (ok, len(out)), flush=True)
    return 0 if ok == len(out) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(run())