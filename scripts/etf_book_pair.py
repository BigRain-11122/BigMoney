"""Second book: a short-horizon reversal book paired with the trend book.

Why: the trend book's own capacity study (r1280/r1295) says scale is capped by
participation in the names it trades, and the only remaining lever named there was
"a second, low-correlated book". This script measures exactly that: same panel, same
open-to-open execution, same vol target, but a different factor family (5d reversal
instead of 12-1 trend), then reports the correlation of the two daily return streams
and what the blend does vs either alone.

Everything here is exploratory measurement, not a new live face: no registry entry,
no capital claim. The honest question it answers is "does a second book actually
diversify, or is it the same trade wearing a different name?"
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
from config import PATHS

IS_END = "2023-12-31"
TARGET_VOL = 0.08
COST = 0.0010

# book A = the shipped configuration (12 names, 20d cadence, vol targeted)
A = {"label": "trend_12_R20", "n_hold": 12, "rebal": 20}
# book B = reversal family: rank on -5d return, 10 names, 10d cadence
B = {"label": "rev5_10_R10", "n_hold": 10, "rebal": 10}


def reversal_score(close, amt, min_amt=None, min_hist=None):
    """Cross-sectional rank of the negative 5d return, mapped to [-1, 1] and masked to
    the same eligibility the trend book uses. Only uses data up to the row's own date."""
    min_amt = E.MIN_AMT if min_amt is None else min_amt
    min_hist = E.MIN_HIST if min_hist is None else min_hist
    hist = close.notna().cumsum()
    elig = (amt.reindex_like(close) >= min_amt) & (hist >= min_hist)
    raw = -close.pct_change(5)
    score = (raw.rank(axis=1, pct=True) - 0.5) * 2.0
    score = score.where(elig)
    score.index = pd.to_datetime(score.index)
    return score


def daily_returns(ser):
    return ser.sort_index().pct_change().dropna()


def blend(series_list, weights):
    """Fixed-weight daily rebalanced blend of equity curves -> a new equity curve.
    No extra cost is charged: each leg already pays its own turnover cost, and the
    blend is a paper composition, not a traded overlay."""
    rets = [daily_returns(s) for s in series_list]
    idx = rets[0].index
    for r in rets[1:]:
        idx = idx.intersection(r.index)
    acc = None
    for w, r in zip(weights, rets):
        part = r.reindex(idx).fillna(0.0) * w
        acc = part if acc is None else acc + part
    eq = (1.0 + acc).cumprod()
    eq.index = idx
    return eq


def pair_corr(a, b):
    ra, rb = daily_returns(a), daily_returns(b)
    idx = ra.index.intersection(rb.index)
    if len(idx) < 20:
        return None
    return float(np.corrcoef(ra.reindex(idx).fillna(0.0), rb.reindex(idx).fillna(0.0))[0, 1])


def name_overlap(close, openp, amt, score_a, score_b, n_a, n_b, rebal, start=R.START):
    """Fraction of decision days where the two books hold at least one common name.
    This is the cheap proxy for "capacity adds or not": books that trade disjoint
    universes do not queue behind each other's ADV."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    sa, sb = score_a.where(elig), score_b.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    shared = 0
    days = 0
    for i in range(0, len(dates) - 1, rebal):
        d = dates[i]
        x, y = sa.loc[d].dropna(), sb.loc[d].dropna()
        if len(x) < n_a or len(y) < n_b:
            continue
        days += 1
        if set(x.nlargest(n_a).index) & set(y.nlargest(n_b).index):
            shared += 1
    return {"decision_days": days, "days_with_shared_name": shared,
            "shared_pct": round(shared / days, 4) if days else None}


def selftest():
    ok = 0
    total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS]", label, "|", detail, flush=True)
        else:
            print("[FAIL]", label, "|", detail, flush=True)

    idx = pd.bdate_range("2021-01-01", periods=160)
    cols = ["sh510300", "sh510500", "sz159915", "sh518880"]

    # synthetic: one name falls steadily, one rises -> reversal must prefer the faller
    close = pd.DataFrame({c: 1.0 + np.linspace(0, 0.2, len(idx)) for c in cols}, index=idx)
    close["sh510300"] = 1.0 + np.linspace(0.3, -0.1, len(idx))
    amt = pd.DataFrame(30e6, index=idx, columns=cols)
    sc = reversal_score(close, amt)
    last = sc.iloc[-1].dropna()
    chk("L1 reversal prefers the falling name", last.idxmax() == "sh510300",
        "%s=%.3f vs best other %.3f" % (last.idxmax(), last.max(), last.drop("sh510300").max()))

    # causality: mutating future prices must not change an earlier score
    close2 = close.copy()
    close2.iloc[-1] = close2.iloc[-1] * 3.0
    sc2 = reversal_score(close2, amt)
    same = sc.iloc[-3].fillna(0).round(10).equals(sc2.iloc[-3].fillna(0).round(10))
    chk("L2 score at t does not see t+1", same, "ip[-3] unchanged after mutating last bar")

    # identical series -> correlation exactly 1 and blend equals the leg itself
    s = pd.Series(np.cumprod(1 + np.random.RandomState(0).normal(0, 0.002, len(idx))), index=idx)
    chk("L3 corr of identical series is 1", abs(pair_corr(s, s) - 1.0) < 1e-12, "corr=%.12f" % pair_corr(s, s))
    bl = blend([s, s], [0.5, 0.5])
    leg = s.reindex(bl.index)
    # levels are compared after normalising to each series' own first value: the blend
    # restarts at 1.0 on its first common return day, the leg does not.
    diff = float(np.nanmax(np.abs((bl.values / bl.iloc[0]) / (leg.values / leg.iloc[0]) - 1.0)))
    chk("L4 50/50 blend of identical legs is the leg", diff < 1e-9, "max rel diff=%.2e" % diff)

    # a real blend must be strictly less volatile than either leg when the legs are
    # negatively correlated -- guards against the blend silently being a no-op
    rng = np.random.RandomState(1)
    x = pd.Series(np.cumprod(1 + rng.normal(0.0004, 0.01, len(idx))), index=idx)
    y = pd.Series(np.cumprod(1 - rng.normal(0.0004, 0.01, len(idx))), index=idx)
    c = pair_corr(x, y)
    blvol = daily_returns(blend([x, y], [0.5, 0.5])).std()
    legvol = min(daily_returns(x).std(), daily_returns(y).std())
    chk("L5 uncorrelated blend cuts vol", c < 0.2 and blvol < legvol,
        "corr=%.3f blendvol=%.5f minleg=%.5f" % (c, blvol, legvol))

    print("selftest %d/%d %s" % (ok, total, "PASS" if ok == total else "FAIL"), flush=True)
    return 0 if ok == total else 1


def main():
    # The same panel the production card prices: class-restricted (equity / commodity /
    # convertible) and split-print repaired. Book A must be *the shipped book*, otherwise
    # "what does a second book add" is measured against a book nobody runs -- the first
    # cut of this script used the full universe (bonds included) and priced A at 6.7%
    # against the card's ~11.5%.
    import etf_book_production as P
    close, openp, amt, score_a, cls, n_flip = P.prep_panel()
    score_b = reversal_score(close, amt)
    print("universe", close.shape[1], "bars", close.shape[0], "flips repaired", n_flip, flush=True)

    ser_a, turn_a = R.open_to_open_equity(close, openp, amt, score_a, A["rebal"], A["n_hold"],
                                          COST, vol_target=TARGET_VOL)
    ser_b, turn_b = R.open_to_open_equity(close, openp, amt, score_b, B["rebal"], B["n_hold"],
                                          COST, vol_target=TARGET_VOL)
    print("book A done, book B done", flush=True)

    blend_eq = blend([ser_a, ser_b], [0.5, 0.5])

    out = {"evidence_cutoff": str(close.index[-1].date()),
           "execution": "decision at close t, execute at open t+1, vol target 8%, cost 10bp/side",
           "panel": {"universe_classes": list(P.USE_CLASSES), "names": int(close.shape[1]),
                     "flips_repaired": int(n_flip),
                     "why": "same panel the production card prices, so book A is the shipped book"},
           "note": "exploratory; not a live face, not registered, no capital claim",
           "books": {}, "correlation": {}, "blend_50_50": {}, "yearly": {},
           "overlap": name_overlap(close, openp, amt, score_a, score_b,
                                   A["n_hold"], B["n_hold"], A["rebal"])}

    for tag, ser, turn, cfg in (("A_trend", ser_a, turn_a, A), ("B_reversal", ser_b, turn_b, B)):
        full = R.stats(ser, cfg["label"])
        full["turnover"] = round(turn, 2)
        full["vol_target"] = TARGET_VOL
        is_s = R.stats(ser[ser.index <= IS_END], cfg["label"] + "_is")
        oos = R.stats(ser[ser.index > IS_END], cfg["label"] + "_oos")
        for k in ("cagr", "sharpe", "maxdd"):
            full[k + "_is"] = is_s.get(k)
            full[k + "_oos"] = oos.get(k)
        out["books"][tag] = full
        out["yearly"][tag] = {int(y): round(float(v), 4) for y, v in
                              ser.groupby(ser.index.year).apply(lambda x: x.iloc[-1] / x.iloc[0] - 1).items()}

    for tag, sl in (("full", slice(None)), ("is", None), ("oos", None)):
        if tag == "full":
            a, b = ser_a, ser_b
        elif tag == "is":
            a, b = ser_a[ser_a.index <= IS_END], ser_b[ser_b.index <= IS_END]
        else:
            a, b = ser_a[ser_a.index > IS_END], ser_b[ser_b.index > IS_END]
        out["correlation"][tag] = (round(pair_corr(a, b), 3) if pair_corr(a, b) is not None else None)

    bl = R.stats(blend_eq, "blend_50_50")
    bl_is = R.stats(blend_eq[blend_eq.index <= IS_END], "blend_50_50_is")
    bl_oos = R.stats(blend_eq[blend_eq.index > IS_END], "blend_50_50_oos")
    for k in ("cagr", "sharpe", "maxdd"):
        bl[k + "_is"] = bl_is.get(k)
        bl[k + "_oos"] = bl_oos.get(k)
    # The blend's realised vol should sit below the average of the legs when the
    # correlation is under 1 -- if it does not, the two books are the same trade.
    bl["diversification_note"] = ("blend vol %.4f vs leg vols %.4f / %.4f at corr %s"
                                 % (bl.get("vol", 0), out["books"]["A_trend"].get("vol", 0),
                                    out["books"]["B_reversal"].get("vol", 0),
                                    out["correlation"].get("full")))
    out["blend_50_50"] = bl
    out["yearly"]["blend_50_50"] = {int(y): round(float(v), 4) for y, v in
                                    blend_eq.groupby(blend_eq.index.year)
                                    .apply(lambda x: x.iloc[-1] / x.iloc[0] - 1).items()}

    p = os.path.join(PATHS.results_dir, "etf_book_pair.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("correlation", "overlap")}, ensure_ascii=False), flush=True)
    for tag in ("A_trend", "B_reversal"):
        b = out["books"][tag]
        print("%-11s cagr %6.2f%% sharpe %5.3f maxdd %6.2f%% oos_cagr %6.2f%% turn %.2f"
              % (tag, b["cagr"] * 100, b["sharpe"], b["maxdd"] * 100,
                 (b.get("cagr_oos") or 0) * 100, b["turnover"]), flush=True)
    print("%-11s cagr %6.2f%% sharpe %5.3f maxdd %6.2f%% oos_cagr %6.2f%%"
          % ("blend_50_50", bl["cagr"] * 100, bl["sharpe"], bl["maxdd"] * 100,
             (bl.get("cagr_oos") or 0) * 100), flush=True)
    print("saved", p, flush=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    main()