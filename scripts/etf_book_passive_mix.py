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

OUT = os.path.join(E.PATHS.results_dir, "etf_book_passive_mix.json")
PUBLISHED = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
CONTROL_TOL_PP = 0.5
N_HOLD = 12
VOL_TARGET = 0.08
VOL_WINDOW = 60
COST = P.COST


def published_book_cagr(path=PUBLISHED):
    """The published n12_vt08 full-window CAGR, or None when the artifact is unavailable."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        return float(doc["backtest"]["n12_vt08"]["full"]["cagr"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def class_returns(close, amt, cls, classes):
    """Daily returns of each class's equal-weight index, on one shared calendar."""
    rets = {}
    for c in classes:
        ser = A.ew_universe(close, amt, cls, (c,))
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


def stats_block(ser, label):
    m = {"label": label}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= A.IS_END]),
                    ("oos", ser[ser.index > A.IS_END])):
        s = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd", "vol"):
            m[k + "_" + lbl if lbl != "full" else k] = s.get(k)
    return m


def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    classes = list(P.USE_CLASSES)
    print("panel %s flips=%d classes=%s" % (close.shape, n_flip, cls.value_counts().to_dict()),
          flush=True)

    dates = [d for d in openp.index if d >= pd.Timestamp(A.START)]
    out = {
        "schema": "etf_book_passive_mix/v1",
        "question": ("does the shipped book beat holding its own class exposure statically, "
                     "with no scoring and no rotation?"),
        "engine": ("etf_book_production.prep_panel + etf_robust_pf.open_to_open_equity "
                   "(control) / etf_equity_alpha.ew_universe (static arms); no re-implementation"),
        "cell": "N%d_R20_10bp" % N_HOLD,
        "basis": "close decision -> next open fill, 10bp per side, top-N equal weight",
        "vol_overlay": "scale = min(1, %.2f / backward %dd realised vol) at each decision"
                       % (VOL_TARGET, VOL_WINDOW),
        "window": "%s..panel end" % A.START,
        "runs": [],
        "control": {},
    }

    # 1) control: the shipped book
    bt, ser_book = P.backtest(close, openp, amt, score, N_HOLD, 20, vol_target=VOL_TARGET)
    row = stats_block(ser_book, "book")
    row["turnover_per_decision"] = bt.get("turnover_per_decision")
    out["runs"].append(row)
    pub = published_book_cagr()
    delta = (round((bt["full"]["cagr"] - pub) * 100, 2)
             if pub is not None and bt["full"].get("cagr") is not None else None)
    out["control"] = {
        "arm": "book",
        "published_cagr": pub,
        "recomputed_cagr": bt["full"].get("cagr"),
        "delta_pp": delta,
        "tolerance_pp": CONTROL_TOL_PP,
        "passes": (None if delta is None else abs(delta) <= CONTROL_TOL_PP),
        "note": ("not asserted: published artifact unavailable" if delta is None else
                 "the compared arm is the arm that was published"),
    }
    print({k: row.get(k) for k in ("label", "cagr", "sharpe", "maxdd", "vol")}, flush=True)

    # 2) what class exposure the book actually carried (from its own attribution run)
    _, contrib, turn, mixes = A.run_with_attribution(close, openp, amt, score, cls)
    w = mix_weights(mixes, classes)
    out["static_weights"] = w
    out["static_weight_source"] = ("mean class shape of etf_equity_alpha.run_with_attribution "
                                   "(fully-invested chain); both arms carry the same 8% "
                                   "overlay, delivered vol per arm is in read.vol_delivered")

    # 3) static mix: same exposure, no scoring, same overlay and cost rule
    cret = class_returns(close, amt, cls, classes)
    ser_static, turn_static, _ = simulate_mix(cret, w, dates)
    static_row = {}
    if ser_static is not None:
        static_row = stats_block(ser_static, "static_mix")
        static_row["turnover_per_decision"] = round(turn_static, 4)
        out["runs"].append(static_row)
        print({k: static_row.get(k) for k in ("label", "cagr", "sharpe", "maxdd", "vol")},
              flush=True)

    # 5) the same mix without any overlay: "no machinery at all"
    ser_novt, turn_novt, _ = simulate_mix(cret, w, dates, vol_target=None)
    novt_row = {}
    if ser_novt is not None:
        novt_row = stats_block(ser_novt, "static_mix_novt")
        novt_row["turnover_per_decision"] = round(turn_novt, 4)
        out["runs"].append(novt_row)
        print({k: novt_row.get(k) for k in ("label", "cagr", "sharpe", "maxdd", "vol")},
              flush=True)

    # 6) read: what all the rotation is worth against a holder who never trades
    premium = bad = None
    if static_row.get("cagr") is not None and row.get("cagr") is not None:
        premium = round((row["cagr"] - static_row["cagr"]) * 100, 2)
        bad = round(((row.get("maxdd") or 0) - (static_row.get("maxdd") or 0)) * 100, 2)
    book_turn = bt.get("turnover_per_decision")
    out["read"] = {
        "selection_premium_pp": premium,
        "maxdd_delta_pp": bad,
        "book_turnover_per_decision": book_turn,
        "static_turnover_per_decision": static_row.get("turnover_per_decision"),
        "vol_delivered": {"book": row.get("vol"), "static_mix": static_row.get("vol"),
                          "static_mix_no_overlay": novt_row.get("vol")},
        "verdict": None,
    }
    if premium is None:
        verdict = "undetermined -- one arm did not price"
    elif premium > 2.0:
        verdict = ("the ranking pays: %+.2fpp/yr over a static mix of the book's own class "
                   "exposure, at %.2fx the static arm's turnover"
                   % (premium, (book_turn / static_row["turnover_per_decision"])
                      if static_row.get("turnover_per_decision") else float("nan")))
    elif premium > 0.0:
        verdict = ("the ranking barely pays: %+.2fpp/yr over a static mix -- inside the noise "
                   "of one regime change, not a reason to carry %.1f-turnover machinery"
                   % (premium, book_turn if book_turn is not None else float("nan")))
    else:
        verdict = ("the ranking does not pay: %+.2fpp/yr against a static mix of the same "
                   "class exposure -- the machinery costs money" % premium)
    out["read"]["verdict"] = verdict
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
        ("one regime: the premium is measured on the 2020+ window the book was published on; "
         "r1305 showed the same engine loses to equal weight before 2020, and this script "
         "does not re-price the static mix on that window"),
    ]
    print("READ", verdict, flush=True)

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