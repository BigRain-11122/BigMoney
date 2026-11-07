"""Does the volume state machine have a claim on the BOOK, not on a 510300 proxy?

The supply line burned zoo #96 (`zoo96_volume_regime_probe`) and refused it standalone:
as a timing rule on 510300 it lost 0.67pp/yr to buy-and-hold with a phase null at p=0.09,
and its two honest volume proxies disagreed in sign. That verdict answers "can the state
machine trade the index". It does not answer the question the money line actually asks,
because the book is not the index: it is an equity/commodity/convertible rotation that
already sits flat 43% of the time and whose drawdowns are made inside two or three
sleeves, not in one index. A gate can be worthless standalone and still be worth
something as a risk switch on a book (and the reverse is the trap that burned E224).

So this face keeps the frozen rule (HMA(volume,5)/HMA(volume,100) against 1.15 and
1.15**-1.5, either band = risk-on) and changes only what it is applied to: the book the
production card publishes (N5, R20, 8% volatility target, 10bp per side), gated at each
close, paid one side per unit of weight change, marked on the book's own open-to-open
equity.

Frozen before reading any number:

  * book: `etf_book_production.prep_panel()` (repaired panel, class filter, one score
    builder) + `backtest(n_hold=5, rebal=20, vol_target=0.08)` -- i.e. the production
    cell, produced by the same engine as the card. The base cell (no vol target) is
    carried as a robustness arm, never as the headline.
  * gate: state known at the close of bar t, weight applies to bar t+1's book return;
    an unread state (no volume history yet, or a bar the archive does not cover) HOLDS
    the previous weight rather than being read as "off".
  * arms (6):
      control      w = 1 always, no gate cost -- must reproduce the book to 1e-12
      gate_long    w = 1 inside either band (the berth's own shape), else 0
      gate_mid     w = 0 inside either band, else 1 (the MIRROR: a direction check --
                   if both directions read positive the gate is a regime premium, not a signal)
      gate_half    w = 1 inside either band, 0.5 in the middle
      gate_long_x   gate_long charged 13.041bp per side instead of 10bp
      gate_long_base  gate_long applied to the no-vol-target book
  * cost: one side per unit |delta weight| at the book's own per-side rate; entering
    from flat pays a full side, so a full 0->1->0 round trip pays two.
  * null: 200 circular shifts of the gate state against the same book curve; p = share
    of draws whose excess CAGR matches or beats the observed one.

Declared conservatisms, stated on the face rather than hidden:

  * the gated arm still pays the book's internal turnover while it is flat, because the
    engine's curve already carries it -- a real flat book would not rebalance. This makes
    the gate look WORSE than it could be, never better.
  * the state is market-wide traded value (summed `amount` over the A-share archive),
    the same proxy zoo #96 chose, and the same axis caveat travels with it here.

Usage:
  python scripts/etf_book_volgate.py                 # run + publish
  python scripts/etf_book_volgate.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import etf_book_production as P          # noqa: E402
import etf_equity_alpha as A             # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_volgate")

COST_SIDE = P.COST                       # 10bp, the rate the production card pays
COST_X = 0.0013041                       # COST_X1_RATE, the constant the book cards also pay
UP = 1.15
A_EXP = 1.5
DOWN = UP ** (-A_EXP)
FAST, SLOW = 5, 100
DRAWS = 200
SEED = 0
N_HOLD, REBAL, VOL_TARGET = 5, 20, P.TARGET_VOL

CRITERIA = {
    "call": "does the volume state machine improve the production book it is gated on?",
    "passes": {
        "net_excess": "gated CAGR minus the ungated book's > 0",
        "beats_null": "circular-shift p < 0.05",
        "drawdown": "gated max drawdown not worse than the book's",
        "cost": "the 13.041bp-per-side leg keeps a positive excess",
        "direction": "the mirror arm's excess is negative (otherwise it is a regime "
                     "premium, not a signal)",
    },
    "verdicts": ["ADOPT_AS_OVERLAY", "REFUSE_AS_OVERLAY",
                 "UNDECIDABLE_NULL_THIN", "INSUFFICIENT_BARS"],
    "thresholds": {"up": UP, "down": round(DOWN, 6), "fast": FAST, "slow": SLOW,
                   "n_hold": N_HOLD, "rebal": REBAL, "vol_target": VOL_TARGET},
    "cost": {"per_side": COST_SIDE, "robustness_per_side": COST_X},
}


# --------------------------------------------------------------------------- #
# the volume state (zoo #96's frozen rule, reused, not re-implemented)
# --------------------------------------------------------------------------- #
def volume_state(panel: dict | None = None):
    """Market-wide volume index -> 1 (either band) / 0 (middle) / NaN (no reading)."""
    import zoo96_volume_regime_probe as Z96

    if panel is None:
        import zoo93_disposition_cgo_probe as Z93
        panel = Z93.load_panel()
    tot, cov = Z96.market_totals(panel, "amount")
    vi = Z96.volume_index(tot)
    st = Z96.state_of(vi)
    ser = pd.Series(st, index=pd.to_datetime(pd.Series(panel["dates"])))
    return ser[~ser.index.duplicated(keep="last")].sort_index(), vi, cov, panel


# --------------------------------------------------------------------------- #
# the gate
# --------------------------------------------------------------------------- #
def gate_book(book: pd.Series, state: pd.Series, cost: float = COST_SIDE,
              mode: str = "binary", start_weight: float = 0.0,
              mid_weight: float = 0.5):
    """Weight the book's own returns by a state decided one bar earlier.

    `book` is an equity curve, so its per-bar return already carries the engine's own
    turnover cost. Gating multiplies that return by the weight the gate carried INTO the
    bar and charges the gate's own |delta weight| at that bar. An unread state holds the
    previous weight (never silently reads as flat).
    """
    ser = book.dropna()
    if len(ser) < 3:
        return ser.copy()
    r = ser.pct_change().fillna(0.0)
    st = state.reindex(ser.index)
    if mode == "binary_in":
        target = st.apply(lambda v: 1.0 if (np.isfinite(v) and v == 1.0) else
                          (0.0 if np.isfinite(v) else np.nan))
    elif mode == "binary_out":          # the mirror: 1 where the state is 0
        target = st.apply(lambda v: 0.0 if (np.isfinite(v) and v == 1.0) else
                          (1.0 if np.isfinite(v) else np.nan))
    elif mode == "half":
        target = st.apply(lambda v: 1.0 if (np.isfinite(v) and v == 1.0) else
                          (mid_weight if np.isfinite(v) else np.nan))
    else:
        raise ValueError("unknown gate mode: %s" % mode)
    target = target.ffill()
    w_prev = float(start_weight) if np.isfinite(start_weight) else 0.0
    eq = float(ser.iloc[0])
    out = [eq]
    for i in range(1, len(ser)):
        # the state known at the close of bar i-1 weights bar i's return: one bar of lag,
        # never the same bar that produced the reading
        w = target.iloc[i - 1]
        if not np.isfinite(w):
            w = w_prev
        if w != w_prev:
            eq *= (1.0 - cost * abs(w - w_prev))
        eq *= (1.0 + w * float(r.iloc[i]))
        w_prev = w
        out.append(eq)
    return pd.Series(out, index=ser.index)


def excess_of(book: pd.Series, gated: pd.Series) -> float:
    b = A.stats2(book, "book")
    g = A.stats2(gated, "gated")
    if "cagr" not in b or "cagr" not in g:
        return float("nan")
    return float(g["cagr"] - b["cagr"])


def null_test(book: pd.Series, state: pd.Series, observed: float, mode: str = "binary_in",
              draws: int = DRAWS, seed: int = SEED, cost: float = COST_SIDE) -> dict:
    """Circular shifts of the state: is the gate better than the same gate at a random phase?"""
    st = state.reindex(book.index).ffill()
    ok = np.where(np.isfinite(st.to_numpy(dtype=np.float64)))[0]
    if len(ok) < 3 or draws <= 0:
        return {"draws": 0, "note": "no state to shift"}
    vals = st.to_numpy(dtype=np.float64)
    rng = np.random.default_rng(seed)
    ex = []
    for _ in range(int(draws)):
        shift = int(rng.integers(1, len(ok)))
        moved = vals.copy()
        moved[ok] = vals[np.roll(ok, shift)]
        s2 = pd.Series(moved, index=book.index)
        g = gate_book(book, s2, cost=cost, mode=mode)
        e = excess_of(book, g)
        if np.isfinite(e):
            ex.append(e)
    if not ex:
        return {"draws": 0, "note": "null produced no reading"}
    arr = np.array(ex, dtype=np.float64)
    return {"draws": int(len(arr)), "mean_pp": round(100 * float(arr.mean()), 3),
            "p95_pp": round(100 * float(np.percentile(arr, 95)), 3),
            "p_value": round(float((arr >= observed).mean()), 4)}


def _row(book: pd.Series, gated: pd.Series, state: pd.Series) -> dict:
    row = {}
    for lbl, sl in (("full", gated), ("is", gated[gated.index <= P.IS_END]),
                    ("oos", gated[gated.index > P.IS_END])):
        m = A.stats2(sl, lbl)
        row[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    w = state.reindex(gated.index).ffill()
    row["exposure_share"] = round(float(w.dropna().mean()), 4) if w.notna().any() else None
    finite = np.where(np.isfinite(w.to_numpy(dtype=np.float64)))[0]
    sw = int(np.sum(np.diff(w.to_numpy(dtype=np.float64)[finite]) != 0)) if len(finite) > 1 else 0
    yrs = row["full"].get("years") or 1e-9
    row["switches"] = sw
    row["switches_per_year"] = round(sw / yrs, 2)
    return row


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def run() -> dict:
    t0 = time.time()
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    book_row, book_ser = P.backtest(close, openp, amt, score, N_HOLD, REBAL,
                                    cost=COST_SIDE, vol_target=VOL_TARGET)
    base_row, base_ser = P.backtest(close, openp, amt, score, N_HOLD, REBAL, cost=COST_SIDE)
    state, vi, cov, panel = volume_state()

    arms = {}
    ones = pd.Series(1.0, index=book_ser.index)
    control = gate_book(book_ser, ones, cost=0.0, mode="binary_in", start_weight=1.0)
    arms["control"] = _row(book_ser, control, ones)
    arms["control"]["identity_max_abs_diff"] = float((control - book_ser).abs().max())
    # r1402 pitfall, caught by the control itself: the first draft handed the CONTROL the
    # volume state instead of an all-ones series, so the arm that exists to prove the gate
    # changes nothing was quietly a gated arm -- and it published a 5.88% "control" beside an
    # 11.46% book. A control that does not reproduce the published cell makes every other
    # reading on this page unreadable, so it refuses to publish rather than printing a diff.
    if arms["control"]["identity_max_abs_diff"] > 1e-9:
        raise RuntimeError("control arm does not reproduce the book (max abs diff %.6e)"
                           % arms["control"]["identity_max_abs_diff"])

    gate = gate_book(book_ser, state, cost=COST_SIDE, mode="binary_in")
    arms["gate_long"] = _row(book_ser, gate, state)
    mirror = gate_book(book_ser, state, cost=COST_SIDE, mode="binary_out")
    arms["gate_mid"] = _row(book_ser, mirror, state)
    half = gate_book(book_ser, state, cost=COST_SIDE, mode="half")
    arms["gate_half"] = _row(book_ser, half, state)
    gx = gate_book(book_ser, state, cost=COST_X, mode="binary_in")
    arms["gate_long_x"] = _row(book_ser, gx, state)
    gb = gate_book(base_ser, state, cost=COST_SIDE, mode="binary_in")
    arms["gate_long_base"] = _row(base_ser, gb, state)

    ex = {k: round(100 * excess_of(book_ser, v if k != "gate_long_base" else gb), 3)
          for k, v in (("gate_long", gate), ("gate_mid", mirror), ("gate_half", half),
                       ("gate_long_x", gx), ("gate_long_base", gb))}
    ex["gate_long_x"] = round(100 * (A.stats2(gx, "x")["cagr"] - A.stats2(book_ser, "b")["cagr"]), 3)
    null = null_test(book_ser, state, ex["gate_long"] / 100.0)
    null_mirror = null_test(book_ser, state, ex["gate_mid"] / 100.0, mode="binary_out")

    reasons = []
    bars = arms["gate_long"]["full"].get("years") or 0
    if (arms["control"]["full"].get("years") or 0) < 1.0:
        verdict = "INSUFFICIENT_BARS"
        reasons.append("the book curve is shorter than one year")
    else:
        if not (ex["gate_long"] > 0):
            reasons.append("gated CAGR %+.2fpp/yr is not above the book"
                           % ex["gate_long"])
        if null.get("p_value") is None or null.get("p_value") >= 0.05:
            reasons.append("phase null p=%s does not beat 5%%" % null.get("p_value"))
        if (arms["gate_long"]["full"].get("maxdd") or 0) < (arms["control"]["full"].get("maxdd") or 0):
            reasons.append("gated max drawdown %.2f%% is worse than the book's %.2f%%"
                           % (100 * arms["gate_long"]["full"]["maxdd"],
                              100 * arms["control"]["full"]["maxdd"]))
        if not (ex["gate_long_x"] > 0):
            reasons.append("at 13.041bp per side the gate gives the excess back (%+.2fpp/yr)"
                           % ex["gate_long_x"])
        if not (ex["gate_mid"] < 0):
            reasons.append("the mirror arm also earns %+.2fpp/yr, so the reading is a "
                           "regime premium rather than a signal" % ex["gate_mid"])
        verdict = "REFUSE_AS_OVERLAY" if reasons else "ADOPT_AS_OVERLAY"
        if null.get("p_value") is None or null.get("draws", 0) < 50:
            verdict = "UNDECIDABLE_NULL_THIN"
            reasons.append("the null produced %s usable draws" % null.get("draws", 0))

    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": "scripts/etf_book_volgate.py",
        "question": "does zoo #96's volume state machine improve the production book?",
        "evidence_cutoff": str(book_ser.index[-1].date()),
        "criteria": CRITERIA,
        "book": {
            "cell": "n%d_rebal%d_vt%s" % (N_HOLD, REBAL, VOL_TARGET),
            "panel_digest": (P.PANEL_DIGEST or {}).get("digest"),
            "flips_repaired": int(n_flip),
            "series_first": str(book_ser.index[0].date()),
            "series_last": str(book_ser.index[-1].date()),
            "published_cell": {k: book_row[k] for k in ("full", "is", "oos",
                                                        "turnover_per_decision")},
            "base_cell": {k: base_row[k] for k in ("full", "is", "oos",
                                                   "turnover_per_decision")},
        },
        "state": {
            "rule": "HMA(amount_sum,5)/HMA(amount_sum,100) vs %.3f / %.6f" % (UP, DOWN),
            "bars": int(len(state)),
            "coverage": {"min": int(cov.min()), "median": int(np.median(cov))},
            "risk_on_share": round(float(state.dropna().mean()), 4),
            "last_bar": str(state.index[-1].date()),
            "last_state": None if not np.isfinite(state.iloc[-1]) else int(state.iloc[-1]),
            "last_volume_index": round(float(vi[np.isfinite(vi)][-1]), 4)
            if np.isfinite(vi).any() else None,
        },
        "arms": arms,
        "excess_pp": ex,
        "null": null,
        "null_mirror": null_mirror,
        "deviations": [
            "the gated arm keeps paying the book's internal turnover while flat (the "
            "engine's curve already carries it), so every gated reading here is a floor",
            "the volume axis is summed traded VALUE over the A-share archive; zoo #96 "
            "showed the share-count proxy disagrees in sign, and that caveat travels here",
            "one bar of alignment: state at close t weights the book's t+1 return",
        ],
        "verdict": verdict,
        "verdict_reasons": reasons,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    return doc


def write(doc: dict) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    cutoff = doc["evidence_cutoff"]
    path = os.path.join(OUT_DIR, "VOLGATE-%s.json" % cutoff)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    latest = os.path.join(OUT_DIR, "latest.json")
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return path


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _curve(n=300, drift=0.0004, seed=5):
    rng = np.random.default_rng(seed)
    r = drift + rng.normal(0, 0.008, n)
    idx = pd.bdate_range("2021-01-04", periods=n)
    return pd.Series(np.cumprod(1.0 + r), index=idx)


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"name": name, "pass": bool(ok), "detail": str(detail)[:160]})

    book = _curve()
    st = pd.Series(1.0, index=book.index)
    c = gate_book(book, st, cost=0.01, mode="binary_in", start_weight=1.0)
    leg("control reproduces the book exactly", float((c - book).abs().max()) < 1e-12,
        (c - book).abs().max())

    # a gate that never turns on must equal cash: flat line, one entry side then nothing
    off = pd.Series(0.0, index=book.index)
    g0 = gate_book(book, off, cost=0.01, mode="binary_in")
    leg("gate off is a flat line", abs(g0.iloc[-1] - g0.iloc[0]) < 1e-12, g0.iloc[-1])

    # a gate that is off from the start charges nothing at all: the level never moves
    g0b = gate_book(book, off, cost=0.01, mode="binary_in", start_weight=0.0)
    leg("never entering costs nothing", abs(g0b.iloc[-1] - g0b.iloc[0]) < 1e-12, g0b.iloc[-1])

    # one switch in, one out: exactly two sides are charged on a flat book
    flat = pd.Series(1.0, index=book.index)
    st2 = pd.Series(0.0, index=book.index)
    st2.iloc[50:150] = 1.0
    g2 = gate_book(flat, st2, cost=0.01, mode="binary_in")
    leg("in-and-out charges two sides", abs(g2.iloc[-1] - (0.99 * 0.99)) < 1e-12, g2.iloc[-1])

    # the weight applies one bar later than the state: a state that turns on at the last
    # bar cannot capture that bar's return
    r = book.pct_change().fillna(0.0)
    st3 = pd.Series(0.0, index=book.index)
    st3.iloc[-1] = 1.0
    g3 = gate_book(book, st3, cost=0.0, mode="binary_in")
    leg("last-bar state does not trade that bar", abs(g3.iloc[-1] - g3.iloc[-2]) < 1e-12,
        g3.iloc[-1] - g3.iloc[-2])

    # an unread state holds the previous weight instead of reading as flat
    st4 = pd.Series(1.0, index=book.index)
    st4.iloc[100:150] = np.nan
    g4 = gate_book(book, st4, cost=0.0, mode="binary_in", start_weight=1.0)
    leg("NaN state holds the weight", float((g4 - book).abs().max()) < 1e-12,
        (g4 - book).abs().max())

    # the mirror is the same function on the flipped state, not a lookalike: this is the
    # invariant that keeps 'gate_mid' from ever becoming its own implementation
    st5 = pd.Series(np.where(np.arange(len(book)) % 40 < 20, 1.0, 0.0), index=book.index)
    a_out = gate_book(book, st5, cost=0.01, mode="binary_out")
    flipped = pd.Series(1.0 - st5.to_numpy(), index=book.index)
    a_flip = gate_book(book, flipped, cost=0.01, mode="binary_in")
    leg("mirror equals the flipped-state in-gate",
        np.allclose(a_out.to_numpy(), a_flip.to_numpy()), float(np.abs(a_out - a_flip).max()))

    # half keeps half of the book's per-bar return, so a drifting book must land strictly
    # between the flat gate and the full gate
    st6 = pd.Series(0.0, index=book.index)
    gh = gate_book(book, st6, cost=0.0, mode="half", mid_weight=0.5)
    g_all = gate_book(book, pd.Series(1.0, index=book.index), cost=0.0, mode="binary_in")
    leg("half-weight middle band sits between flat and full",
        bool(gh.iloc[0] < gh.iloc[-1] < g_all.iloc[-1]),
        (gh.iloc[-1], g_all.iloc[-1]))

    # excess_of is signed and finite
    e = excess_of(book, book)
    leg("excess of a series against itself is zero", abs(e) < 1e-12, e)

    # the null never claims a win for a constant state it cannot shift into different shapes
    n = null_test(book, st, 0.0, draws=10, seed=1)
    leg("null runs and returns draws", n.get("draws") == 10, n.get("p_value"))

    # determinism
    x = gate_book(book, st5, cost=0.01, mode="binary_in")
    y = gate_book(book, st5, cost=0.01, mode="binary_in")
    leg("determinism", np.array_equal(x.to_numpy(), y.to_numpy()))

    # stats refuse a short slice rather than inventing a CAGR
    leg("short slice refused", "cagr" not in A.stats2(book.iloc[:10], "short"))

    ok = sum(1 for l in legs if l["pass"])
    print(json.dumps({"selftest": "etf_book_volgate", "pass": ok,
                      "fail": len(legs) - ok, "legs": legs}, ensure_ascii=False, indent=1))
    return 0 if ok == len(legs) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    doc = run()
    path = write(doc)
    print(json.dumps({k: doc[k] for k in ("verdict", "excess_pp", "null", "elapsed_sec")},
                     ensure_ascii=False))
    print(json.dumps({k: doc["arms"][k]["full"] for k in doc["arms"]}, ensure_ascii=False, indent=1))
    print("state", json.dumps(doc["state"], ensure_ascii=False))
    print("wrote", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())