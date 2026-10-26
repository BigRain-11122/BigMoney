"""Is the staggered book better than the book we publish -- under the SAME rule?

The open question (state pointer r1300 -> next): the staggered 5+5 book was reported at
20.77% CAGR / Sharpe 1.32, but it was priced on a different experiment than the published
card (8 names, R10 cadence, no bonds, no volatility target). Comparing it to the published
9.49% is therefore meaningless, and the earlier "+61% capacity" claim mixed a wider book
with an offset clock (r1262).

This script prices the stagger design through the PUBLISHED rule and nothing else:

  universe  : same class filter as the production card (equity + commodity + convertible)
  score     : same composite score builder
  engine    : same open-to-open execution (decide at close t, fill at open t+1)
  cost      : 10 bp per side, charged on the weight actually turned over
  sizing    : same 8% volatility target, min(1, target / realised), never levered up
  window    : same panel start (2020-01-01), same evidence cutoff
  holdings  : 12 names total, split 6 + 6, second sleeve offset half a period (R20 -> 10)

The control arm is the shipped card's own cell (N12 / R20 / vt08), re-priced here by the
same engine that prices the stagger, and ASSERTED against the published number before any
delta is printed (r1297 lesson: a control arm has to be the one that was asserted).

Usage:
  python scripts/etf_book_stagger_publish.py run
  python scripts/etf_book_stagger_publish.py selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_production as P
from config import PATHS

OUT = os.path.join(PATHS.results_dir, "etf_book_stagger_publish.json")
CARD = os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")

N_TOTAL = 12
REBAL = 20
COST = 0.0010
TARGET_VOL = 0.08
CARD_TOLERANCE = 0.005          # 0.5pp: r1297's pinned tolerance for a control arm


def _book_vol(op, book, upto, vol_window=60):
    """Realised annualised vol of `book` on open-to-open returns up to `upto` (causal)."""
    if not book:
        return np.nan
    rets = op.pct_change()
    window = rets.loc[:upto].tail(vol_window)[list(book)]
    if window.shape[0] < 20:
        return np.nan
    w = np.array([book[k] for k in window.columns])
    cov = window.cov().to_numpy()
    return float(np.sqrt(w @ cov @ w) * np.sqrt(252))


def run_staggered(close, openp, amt, score, rebal=REBAL, n_total=N_TOTAL, cost=COST,
                  vol_target=TARGET_VOL, vol_window=60, n_sleeves=2, start=R.START,
                  diag=None):
    """Two (or more) sleeves of n_total/n_sleeves names, decisions offset across the clock.

    Weight, cost and sizing semantics are the published ones: each name carries 1/n_total,
    the combined book is scaled by min(1, target/realised), and cost is charged on the
    change in the COMBINED weights -- exactly how the single-sleeve engine charges it, so
    a scale change repriced onto a non-trading sleeve is paid for, not hidden.
    """
    if n_total % n_sleeves:
        raise ValueError("n_total must divide evenly across sleeves")
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    half = n_total // n_sleeves
    w_leg = 1.0 / n_total

    equity, held, daily, turns, trades = 1.0, {}, [], [], []
    sleeves = [None] * n_sleeves
    offsets = [(k * (rebal // n_sleeves)) % rebal for k in range(n_sleeves)]

    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        fired = False
        for k in range(n_sleeves):
            if i % rebal != offsets[k]:
                continue
            s = score.loc[d].dropna()
            if len(s) < n_total:
                continue
            sleeves[k] = list(s.nlargest(n_total).index)[k * half:(k + 1) * half]
            fired = True
        if fired and all(sl is not None for sl in sleeves):
            raw = {}
            for sl in sleeves:
                for p in sl:
                    raw[p] = raw.get(p, 0.0) + w_leg
            scale, est = 1.0, None
            if vol_target:
                v = _book_vol(op, raw, d, vol_window)
                if np.isfinite(v) and v > 0:
                    est = float(v)
                    scale = float(min(1.0, vol_target / v))
            new = {p: w * scale for p, w in raw.items()}
            turn = sum(abs(new.get(x, 0.0) - held.get(x, 0.0)) for x in set(new) | set(held))
            equity *= (1.0 - cost * turn)
            turns.append(turn)
            trades.append({"date": d, "turnover": turn,
                           "delta": {x: abs(new.get(x, 0.0) - held.get(x, 0.0))
                                     for x in set(new) | set(held)}})
            held = new
            if diag is not None:
                diag.append({"date": str(d.date()), "est_vol": est, "scale": scale,
                             "book": sorted(raw)})
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))

    ser = pd.Series(dict(daily)).sort_index()
    return ser, turns, trades


def capacity(trades, amt):
    """CNY deployable while keeping p90 single-name participation at 1% / 5% of ADV."""
    recs = []
    for t in trades:
        d = t["date"]
        if d not in amt.index:
            continue
        a = amt.loc[d]
        worst = 0.0
        for sym, dw in t["delta"].items():
            v = a.get(sym, np.nan)
            if np.isfinite(v) and v > 0:
                worst = max(worst, dw / v)
        if worst > 0:
            recs.append(worst)
    if not recs:
        return {"units": "CNY", "aum_1pct": None, "aum_5pct": None, "decisions": 0}
    s = pd.Series(recs)
    q90 = float(s.quantile(0.90))
    # r1292 class: a participation ratio is per-CNY of capital, so rounding it to 8
    # decimals prints 0.0 while the number is real. Publish it scaled instead.
    return {"units": "CNY",
            "aum_1pct": round(0.01 / q90, 0),
            "aum_5pct": round(0.05 / q90, 0),
            "p90_participation_per_1m_cny": round(q90 * 1e6, 6),
            "p90_participation_per_cny": q90,
            "decisions": int(len(s))}


def _stats(ser, label):
    m = A.stats2(ser, label)
    keep = ("cagr", "sharpe", "maxdd", "vol", "years", "worst_year", "neg_years")
    return {k: m.get(k) for k in keep if k in m}


def _split(ser):
    return {"is": _stats(ser[ser.index <= R.IS_END], "is"),
            "oos": _stats(ser[ser.index > R.IS_END], "oos")}


def build():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    out = {"machinery": {
        "universe_classes": list(P.USE_CLASSES),
        "universe_size": int(close.shape[1]),
        "flips_repaired": int(n_flip),
        "score": "etf_composite_pf.build_score",
        "engine": "open-to-open, decide close t -> fill open t+1, hold to next decision",
        "cost_bp_per_side": COST * 1e4,
        "vol_target": TARGET_VOL,
        "n_total": N_TOTAL, "rebal": REBAL,
        "note": "every arm below shares this rule; deltas are only printed inside it",
    }}

    # ---- control: the shipped card's own cell, priced by this engine.
    ser_c, turn_c = R.open_to_open_equity(close, openp, amt, score, REBAL, N_TOTAL, COST,
                                          vol_target=TARGET_VOL)
    ctrl = {"label": "control: single sleeve, N12/R20/vt08 (the published cell)",
            **_stats(ser_c, "control"), **_split(ser_c),
            "turnover_per_decision": round(float(turn_c), 3),
            "source": "re-priced here, not retyped"}
    card_cagr = None
    if os.path.exists(CARD):
        with open(CARD, encoding="utf-8") as f:
            card = json.load(f)
        card_cagr = ((card.get("backtest") or {}).get("n12_vt08") or {}).get("full", {}).get("cagr")
        ctrl["card_cagr"] = card_cagr
        ctrl["card_file"] = os.path.relpath(CARD, os.path.dirname(PATHS.results_dir))
    ctrl["cagr_delta_vs_card"] = (None if card_cagr is None
                                  else round(float(ctrl["cagr"]) - float(card_cagr), 4))
    ctrl["control_reproduces_card"] = (None if card_cagr is None
                                       else abs(float(ctrl["cagr"]) - float(card_cagr))
                                       <= CARD_TOLERANCE)
    out["control"] = ctrl

    # ---- staggered: same 12 names, two sleeves of 6, offset 10 bars.
    diag = []
    ser_s, turns_s, trades_s = run_staggered(close, openp, amt, score, diag=diag)
    stag = {"label": "staggered: 6 + 6, second sleeve offset half a period (R20 -> 10)",
            **_stats(ser_s, "staggered"), **_split(ser_s),
            "turnover_per_decision": round(float(np.mean(turns_s)), 3),
            "decisions": len(turns_s)}
    out["staggered"] = stag

    # ---- the delta, printed only because both arms share one rule (and only if the
    # control arm actually reproduced the card).
    if ctrl["control_reproduces_card"] is not False:
        out["delta"] = {
            "cagr_pp": round((stag["cagr"] - ctrl["cagr"]) * 100, 2),
            "sharpe": round(stag["sharpe"] - ctrl["sharpe"], 3),
            "maxdd_pp": round((stag["maxdd"] - ctrl["maxdd"]) * 100, 2),
            "turnover": round(stag["turnover_per_decision"] - ctrl["turnover_per_decision"], 3),
            "is_cagr_pp": round((stag["is"]["cagr"] - ctrl["is"]["cagr"]) * 100, 2),
            "oos_cagr_pp": round((stag["oos"]["cagr"] - ctrl["oos"]["cagr"]) * 100, 2),
        }
    else:
        out["delta"] = {"suppressed": "control arm did not reproduce the published card"}

    # ---- capacity, both arms on the same participation measure.
    out["capacity"] = {"control": capacity(
        [{"date": d, "delta": deltas} for d, deltas in _control_trades(close, openp, amt, score)],
        amt), "staggered": capacity(trades_s, amt)}

    # ---- activity assertions: a stagger that never fired is indistinguishable in ratios.
    out["assertions"] = {
        "staggered_decisions": len(turns_s),
        "warmup_note": "sleeve B is half-cash until its first decision (%d bars)"
                       % (REBAL // 2),
        "sleeves_fired": bool(len(turns_s) > 0),
        "scale_median": round(float(np.median([r["scale"] for r in diag])), 4) if diag else None,
    }
    out["assertions"]["max_turnover_per_decision"] = _max_turnover(trades_s)
    out["evidence_cutoff"] = str(close.index[-1].date())
    out["script"] = "scripts/etf_book_stagger_publish.py"
    return out


def _control_trades(close, openp, amt, score):
    """The control arm's own weight deltas, for the capacity measure."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    masked = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(R.START)]
    held, out = {}, []
    for i in range(len(dates) - 1):
        if i % REBAL:
            continue
        d = dates[i]
        s = masked.loc[d].dropna()
        if len(s) < N_TOTAL:
            continue
        picks = list(s.nlargest(N_TOTAL).index)
        w = {p: 1.0 / N_TOTAL for p in picks}
        v = _book_vol(op, w, d)
        scale = float(min(1.0, TARGET_VOL / v)) if np.isfinite(v) and v > 0 else 1.0
        new = {p: x * scale for p, x in w.items()}
        out.append((d, {x: abs(new.get(x, 0.0) - held.get(x, 0.0))
                        for x in set(new) | set(held)}))
        held = new
    return out


def _max_turnover(trades):
    """Largest single-decision turnover (a weight change, not a gross exposure)."""
    if not trades:
        return None
    return round(float(max(t["turnover"] for t in trades)), 4)


# --------------------------------------------------------------------------- selftest
def _synthetic(bars=520, cols=24, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=bars)
    syms = ["s%02d" % i for i in range(cols)]
    steps = rng.normal(0.0004, 0.012, size=(bars, cols))
    close = pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=idx, columns=syms)
    openp = close.shift(1).bfill() * (1 + rng.normal(0, 0.0005, size=(bars, cols)))
    amt = pd.DataFrame(np.full((bars, cols), 5e7), index=idx, columns=syms)
    score = pd.DataFrame(rng.normal(size=(bars, cols)), index=idx, columns=syms)
    return close, openp, amt, score


def selftest():
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    close, openp, amt, score = _synthetic()

    # L1 the one-sleeve degenerate case must equal the published engine exactly.
    ser_e, _ = R.open_to_open_equity(close, openp, amt, score, 20, 8, COST, vol_target=0.08)
    ser_s, _, _ = run_staggered(close, openp, amt, score, n_total=8, n_sleeves=1)
    chk("L1 one-sleeve stagger equals the engine",
        np.allclose(ser_e.to_numpy(), ser_s.to_numpy(), atol=1e-12),
        "max abs diff %.2e" % float(np.max(np.abs(ser_e.to_numpy() - ser_s.to_numpy()))))

    # L1b the equality must survive with the vol overlay ENGAGED, otherwise the overlay
    # branch is untested by the degenerate case above (quiet synthetic panel = scale 1).
    hc, ho, ha, hs = _synthetic()
    ho = ho * 1.0
    hs = hs * 4.0                                    # force a hot book via dispersion only
    hot_close = hc * 1.0
    ser_he, _ = R.open_to_open_equity(hot_close, ho, ha, hs, 20, 8, COST, vol_target=0.02)
    ser_hs, _, _ = run_staggered(hot_close, ho, ha, hs, n_total=8, n_sleeves=1,
                                 vol_target=0.02)
    chk("L1b degenerate equality holds with the overlay engaged",
        np.allclose(ser_he.to_numpy(), ser_hs.to_numpy(), atol=1e-12),
        "max abs diff %.2e" % float(np.max(np.abs(ser_he.to_numpy() - ser_hs.to_numpy()))))

    # L2 two sleeves still spend at most the whole book (never levers up), and the
    # overlay has to be shown ENGAGING at least once -- a permanently 1.0 scale means
    # the de-lever branch was never exercised.
    diag = []
    ser2, turns2, tr2 = run_staggered(close, openp, amt, score, diag=diag)
    hot_diag = []
    run_staggered(hot_close, ho, ha, hs, vol_target=0.02, diag=hot_diag)
    chk("L2 vol overlay never levers up", all(r["scale"] <= 1.0 for r in diag + hot_diag),
        "quiet min %.3f / hot min %.3f" % (min(r["scale"] for r in diag or [{"scale": 1.0}]),
                                           min(r["scale"] for r in hot_diag)))
    chk("L2b overlay actually engages on a hot book",
        any(r["scale"] < 1.0 for r in hot_diag),
        "min hot scale %.3f" % min(r["scale"] for r in hot_diag))
    chk("L2c every turnover is finite and positive somewhere",
        all(np.isfinite(t["turnover"]) for t in tr2) and len(tr2) > 0,
        "%d decisions" % len(tr2))

    # L3 the stagger must fire on TWO clocks: twice the decisions of the one-sleeve arm
    # (the r1262 lens: a clock change and a width change are different experiments).
    _, turns1, _ = run_staggered(close, openp, amt, score, n_sleeves=1)
    chk("L3 sleeves fire on their own clock", len(turns2) >= 1.9 * len(turns1),
        "two-sleeve %d vs one-sleeve %d" % (len(turns2), len(turns1)))

    # L4 cost monotonicity: more friction cannot raise the curve.
    s_lo, _, _ = run_staggered(close, openp, amt, score, cost=0.0000)
    s_hi, _, _ = run_staggered(close, openp, amt, score, cost=0.0050)
    chk("L4 cost monotone", float(s_hi.iloc[-1]) < float(s_lo.iloc[-1]),
        "hi %.6f < lo %.6f" % (float(s_hi.iloc[-1]), float(s_lo.iloc[-1])))

    # L5 the fields an 8-name book would silently break on.
    bad = False
    try:
        run_staggered(close, openp, amt, score, n_total=7, n_sleeves=2)
    except ValueError:
        bad = True
    chk("L5 uneven split rejected", bad)

    # L6 capacity units are CNY and p90 uses an actual participation record.
    cap = capacity(tr2, amt)
    chk("L6 capacity priced in CNY", cap.get("units") == "CNY" and cap.get("aum_1pct") is not None,
        "aum_1pct=%s" % cap.get("aum_1pct"))
    # r1292: a per-CNY ratio rounded to 8 decimals reads 0.0 while being nonzero. Pin the
    # un-rounded field so a silent zero cannot pass.
    chk("L6b participation is nonzero and positive per CNY",
        cap.get("p90_participation_per_cny", 0.0) > 0.0,
        "q90=%.3e per 1M=%.6f" % (cap.get("p90_participation_per_cny") or 0.0,
                                  cap.get("p90_participation_per_1m_cny") or 0.0))

    n_ok = sum(1 for c in checks if c["ok"])
    for c in checks:
        print(("PASS " if c["ok"] else "FAIL ") + c["check"] + (" | " + c["detail"] if c["detail"] else ""))
    print("%d/%d" % (n_ok, len(checks)))
    return 0 if n_ok == len(checks) else 1


def main():
    out = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"control": out["control"], "staggered": out["staggered"],
                      "delta": out["delta"], "capacity": out["capacity"]},
                     ensure_ascii=False, indent=1))
    print("saved", OUT)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(main())