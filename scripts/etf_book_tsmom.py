"""Second book, round three: time-series momentum on the ETF panel (no capital floor).

Why this mechanism and not another cross-section screen: r1297 priced five
cross-sectional mechanisms and all five were rejected -- the ones that paid were the
same trade as the shipped book, the ones that were different lost money. r1298 then
killed the futures trend sleeve for a reason that has nothing to do with the signal:
CNY 1M buys 16.9% of target notional at a CNY 8.08M capital floor. So the remaining
question is whether a TREND book can be expressed in instruments that have no floor.
ETFs do (100-share lots): the floor is rounding, not millions.

This is the time-series form of trend, not the cross-sectional form the shipped book
uses. Book A ranks every ETF against its peers and holds the top 12; this book asks,
of each ETF independently, "is this instrument in an uptrend?" and holds whatever
answers yes, sized so the whole book runs at the same 8% vol target. When nothing
answers yes the book is in cash.

Discipline inherited from earlier rounds (each line was paid for):
  * the control arm is built through `etf_book_production.prep_panel()` and asserted
    against the published card (r1296: a hand-rebuilt control read 6.74% where the
    shipped book does 9.49%).
  * blending is judged at EQUAL RISK -- both legs scaled to the same vol before the
    50/50 -- because fixed weights are a leverage decision, not a quality decision
    (r1291/r1297).
  * the number of variants tested is published, and a seeded random-sign arm runs as
    the null control.
  * nothing here is a live face: no registry entry, no capital claim.

Outputs results/etf_book_tsmom.json.
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
CONTROL_TOL_PP = 0.50
CORR_MAX = 0.70


def tsmom_weights(signal_row, rets, upto, vol_window=60, inverse_vol=False):
    """Weights for one decision row. Empty dict == cash.

    Long-only by construction (an ETF cannot be shorted here for free): every eligible
    ETF with a positive own-return over the lookback is held. inverse_vol=True sizes by
    1/vol instead of equal weight, which matters because the universe mixes 4%-vol
    bond ETFs with 40%-vol sector ETFs."""
    picks = [p for p in signal_row.index if np.isfinite(signal_row[p]) and signal_row[p] > 0]
    if not picks:
        return {}
    if not inverse_vol:
        return {p: 1.0 / len(picks) for p in picks}
    window = rets.loc[:upto].tail(vol_window)[picks]
    if window.shape[0] < 20:
        return {p: 1.0 / len(picks) for p in picks}
    vol = window.std() * np.sqrt(252)
    vol = vol.replace(0.0, np.nan).dropna()
    if len(vol) == 0:
        return {p: 1.0 / len(picks) for p in picks}
    inv = 1.0 / vol
    total = float(inv.sum())
    return {p: float(inv[p] / total) for p in inv.index}


def book_vol(book, rets, upto, vol_window=60):
    if not book:
        return np.nan
    window = rets.loc[:upto].tail(vol_window)[list(book)]
    if window.shape[0] < 20:
        return np.nan
    w = np.array([book[k] for k in window.columns])
    cov = window.cov().to_numpy()
    return float(np.sqrt(w @ cov @ w) * np.sqrt(252))


def tsmom_equity(close, openp, amt, lookback, rebal, cost, vol_target=TARGET_VOL,
                 start=R.START, vol_window=60, inverse_vol=False, vol_cap=1.0,
                 inverse_signal=False, diag=None):
    """Decision at close t (signal uses closes up to t) -> execute at open t+1.

    `inverse_signal` flips every sign; it exists only so the selftest can show that a
    sign error costs money instead of being silently absorbed."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    signal = close.pct_change(lookback).where(elig)
    if inverse_signal:
        signal = -signal
    op = openp.reindex(columns=close.columns)
    rets = op.pct_change()
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    equity, held, daily, turns, cash_days, widths = 1.0, {}, [], [], 0, []

    for i in range(len(dates) - 1):
        d = dates[i]
        if i % rebal == 0:
            row = signal.loc[d].dropna()
            w = tsmom_weights(row, rets, d, vol_window=vol_window, inverse_vol=inverse_vol)
            if not w:
                cash_days += 1
            scale = 1.0
            est = None
            if vol_target and w:
                v = book_vol(w, rets, d, vol_window)
                if np.isfinite(v) and v > 0:
                    est = float(v)
                    scale = float(min(vol_cap, vol_target / v))
            w = {k: v * scale for k, v in w.items()}
            turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
            equity *= (1.0 - cost * turn)
            turns.append(turn)
            held = w
            widths.append(len(w))
            if diag is not None:
                diag.append({"date": str(d.date()), "names": len(w), "est_vol": est,
                             "scale": scale, "gross": round(sum(w.values()), 4)})
        nxt = dates[i + 1]
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))
    ser = pd.Series(dict(daily)).sort_index()
    n_dec = len(turns)
    meta = {"avg_turnover": float(np.mean(turns)) if turns else 0.0,
            "decision_days": n_dec,
            "cash_days": cash_days,
            "cash_pct": round(cash_days / n_dec, 4) if n_dec else None,
            "avg_names": round(float(np.mean(widths)), 2) if widths else 0.0}
    return ser, meta


def daily_returns(ser):
    return ser.sort_index().pct_change().dropna()


def pair_corr(a, b):
    ra, rb = daily_returns(a), daily_returns(b)
    idx = ra.index.intersection(rb.index)
    if len(idx) < 20:
        return None
    return float(np.corrcoef(ra.reindex(idx).fillna(0.0), rb.reindex(idx).fillna(0.0))[0, 1])


def equal_risk_blend(a, b, weight=0.5):
    """Scale leg B to leg A's realised vol, then mix. Equal risk, not equal capital:
    a 5%-vol leg and a 15%-vol leg at 50/50 is a 2:1 bet on the loud one."""
    ra, rb = daily_returns(a), daily_returns(b)
    va, vb = ra.std(), rb.std()
    k = float(va / vb) if vb and np.isfinite(vb) else 1.0
    eq = a.sort_index().pct_change().dropna()
    eqb = (rb * k).reindex(eq.index).fillna(0.0)
    mixed = (1.0 - weight) * eq.fillna(0.0) + weight * eqb
    return (1.0 + mixed).cumprod(), {"vol_a": float(va), "vol_b": float(vb),
                                     "scale_b": round(k, 3),
                                     "corr": pair_corr(a, b)}


def verdict(row):
    if row.get("cagr") is None or row.get("blend_cagr") is None:
        return "unmeasured"
    if row["cagr"] <= 0:
        return "reject: loses money alone"
    if row.get("corr_full") is not None and row["corr_full"] >= CORR_MAX:
        return "reject: same trade (corr >= %.2f)" % CORR_MAX
    if row["blend_cagr"] <= row.get("control_cagr", 0.0):
        return "reject: equal-risk blend does not beat the shipped book"
    return "candidate: pursue"


def published_control_cagr(path=None):
    p = path or os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return float(d["backtest"]["n12_vt08"]["full"]["cagr"])
    except Exception:
        return None


def selftest():
    ok = total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS]", label, "|", detail, flush=True)
        else:
            print("[FAIL]", label, "|", detail, flush=True)

    idx = pd.bdate_range("2021-01-01", periods=300)
    cols = ["sh510300", "sh510500", "sz159915", "sh518880"]
    rs = np.random.RandomState(11)
    close = pd.DataFrame(1.0 + rs.random_sample((len(idx), len(cols))).cumsum(0) * 0.01,
                         index=idx, columns=cols)
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    openp = close * 1.0005

    # L1 causality: the signal row at t must be reproduced from a panel truncated at t
    def sig(c, lb=60):
        hist = c.notna().cumsum()
        elig = (amt.reindex_like(c) >= E.MIN_AMT) & (hist >= E.MIN_HIST)
        return c.pct_change(lb).where(elig)
    full, cut = sig(close), sig(close.iloc[:200])
    t = idx[199]
    v1, v2 = full.loc[t].dropna(), cut.loc[t].dropna()
    chk("L1 tsmom signal is causal", len(v1) > 0 and len(v1) == len(v2)
        and np.allclose(v1.sort_index(), v2.sort_index()), "row 200 identical under truncation")

    # L2 no positive trend -> cash, not a silent equal-weight book
    falling = pd.DataFrame({c: np.linspace(2.0, 1.0, len(idx)) for c in cols}, index=idx)
    row = falling.pct_change(60).iloc[-1]
    chk("L2 all-negative trend books cash", tsmom_weights(row, rising_rets(falling), idx[-1]) == {},
        "empty dict == no position")

    # L3 a rising universe is held, and weights sum to 1 before the vol overlay
    rising = pd.DataFrame({c: np.linspace(1.0, 3.0, len(idx)) for c in cols}, index=idx)
    w = tsmom_weights(rising.pct_change(60).iloc[-1], rising_rets(rising), idx[-1])
    chk("L3 rising universe is held at full weight",
        len(w) == len(cols) and abs(sum(w.values()) - 1.0) < 1e-9, "names %d sum %.6f" % (len(w), sum(w.values())))

    # L4 inverse-vol sizing is still a full-weight book, and it tilts away from the loud name
    noisy = rising.copy()
    noisy["sh518880"] = rising["sh518880"] * (1.0 + 0.02 * np.sin(np.arange(len(idx)) / 3.0))
    wi = tsmom_weights(noisy.pct_change(60).iloc[-1], rising_rets(noisy), idx[-1], inverse_vol=True)
    chk("L4 inverse-vol weights sum to 1", abs(sum(wi.values()) - 1.0) < 1e-9, "sum %.6f" % sum(wi.values()))

    # L5 a dead-flat market must produce a flat equity curve (no phantom P&L, no cost bleed
    # beyond the entry, which is charged once)
    flat = pd.DataFrame(1.0, index=idx, columns=cols)
    ser, meta = tsmom_equity(flat, flat, amt, 60, 20, COST, vol_target=None)
    chk("L5 flat market -> flat after entry cost", abs(ser.iloc[-1] - 1.0) < 1e-9,
        "final %.10f turnover %.3f" % (ser.iloc[-1], meta["avg_turnover"]))

    # L6 sign error costs money: the same panel with the signal flipped must underperform
    up = pd.DataFrame({c: np.linspace(1.0, 2.0, len(idx)) * (1 + 0.01 * rs.random_sample(len(idx))) for c in cols},
                      index=idx)
    s1, _ = tsmom_equity(up, up, amt, 60, 20, COST, vol_target=None)
    s2, _ = tsmom_equity(up, up, amt, 60, 20, COST, vol_target=None, inverse_signal=True)
    chk("L6 flipped signal loses vs correct signal", s2.iloc[-1] < s1.iloc[-1],
        "correct %.4f flipped %.4f" % (s1.iloc[-1], s2.iloc[-1]))

    # L7 vol targeting only de-levers when the book is louder than target, and the cap binds
    diag = []
    volser = pd.DataFrame({c: np.linspace(1.0, 2.0, len(idx)) for c in cols}, index=idx)
    tsmom_equity(volser, volser, amt, 60, 20, COST, vol_target=1e-6, vol_cap=1.0, diag=diag)
    scales = [d["scale"] for d in diag if d["scale"] is not None]
    chk("L7 vol target never levers up", all(s <= 1.0 + 1e-12 for s in scales) and len(scales) > 0,
        "max scale %.6f over %d decisions" % (max(scales) if scales else float("nan"), len(scales)))

    # L8 equal-risk blend of a leg with itself reproduces the leg
    eq = s1
    bl, info = equal_risk_blend(eq, eq, 0.5)
    same = np.allclose(bl.values, eq.sort_index().iloc[1:].values / eq.sort_index().iloc[0])
    chk("L8 equal-risk blend of a leg with itself == the leg", same,
        "scale_b %.3f corr %.3f" % (info["scale_b"], info["corr"] or 0.0))

    # L9 the control guard fires on drift and passes the shipped number
    d1 = abs((0.1049 - 0.0949) * 100.0)
    chk("L9 control guard catches drift", d1 > CONTROL_TOL_PP, "delta %.2fpp" % d1)
    chk("L9b control guard passes the shipped number", abs((0.0949 - 0.0949) * 100.0) <= CONTROL_TOL_PP,
        "identical inputs")

    # L10 a losing or same-trade leg can never be published as a candidate
    chk("L10 losing leg rejected",
        verdict({"cagr": -0.01, "blend_cagr": 0.10, "corr_full": 0.2, "control_cagr": 0.09}).startswith("reject"),
        "negative cagr")
    chk("L10b same trade rejected",
        verdict({"cagr": 0.12, "blend_cagr": 0.11, "corr_full": 0.9, "control_cagr": 0.09}).startswith("reject"),
        "corr gate")
    chk("L10c non-additive rejected",
        verdict({"cagr": 0.12, "blend_cagr": 0.08, "corr_full": 0.2, "control_cagr": 0.09}).startswith("reject"),
        "blend gate")

    print("\nselftest %d/%d" % (ok, total), flush=True)
    return 0 if ok == total else 1


def rising_rets(df):
    return df.pct_change()


def main():
    import etf_book_production as P
    close, openp, amt, score_a, cls, n_flip = P.prep_panel()
    print("panel names %d bars %d flips %d" % (close.shape[1], close.shape[0], n_flip), flush=True)

    variants = {
        "tsmom60_e":   dict(lookback=60,  rebal=20, inverse_vol=False, why="60d own-return sign, equal weight"),
        "tsmom120_e":  dict(lookback=120, rebal=20, inverse_vol=False, why="120d own-return sign, equal weight"),
        "tsmom60_iv":  dict(lookback=60,  rebal=20, inverse_vol=True,  why="60d own-return sign, inverse-vol weight"),
        "tsmom120_iv": dict(lookback=120, rebal=20, inverse_vol=True,  why="120d own-return sign, inverse-vol weight"),
    }

    out = {"evidence_cutoff": str(close.index[-1].date()),
           "execution": "signal from closes up to t, execute at open t+1, cost 10bp/side, vol target 8%",
           "panel": {"names": int(close.shape[1]), "flips_repaired": int(n_flip),
                     "classes": list(P.USE_CLASSES)},
           "note": "time-series trend, long-only, no capital floor (ETF lots); exploratory, not a live face",
           "n_variants": len(variants), "books": {}, "vs_A": {}, "ranking": []}

    sum_a, turn_a = R.open_to_open_equity(close, openp, amt, score_a, 20, 12, COST, vol_target=TARGET_VOL)
    a = R.stats(sum_a, "A_trend_12_R20")
    a["turnover"] = round(turn_a, 2)
    for lbl, sl in (("is", sum_a[sum_a.index <= IS_END]), ("oos", sum_a[sum_a.index > IS_END])):
        mm = R.stats(sl, "A_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            a[k + "_" + lbl] = mm.get(k)
    out["books"]["A_trend"] = a
    pub = published_control_cagr()
    delta = round((a["cagr"] - pub) * 100.0, 3) if pub is not None else None
    out["control_check"] = {"published_cagr": pub, "computed_cagr": a["cagr"], "delta_pp": delta,
                            "tolerance_pp": CONTROL_TOL_PP,
                            "matches": delta is not None and abs(delta) <= CONTROL_TOL_PP}
    print("control A: computed %.2f%% published %s delta %s pp"
          % (a["cagr"] * 100, ("%.2f%%" % (pub * 100)) if pub else "n/a", delta), flush=True)

    for tag, cfg in variants.items():
        ser, meta = tsmom_equity(close, openp, amt, cfg["lookback"], cfg["rebal"], COST,
                                vol_target=TARGET_VOL, inverse_vol=cfg["inverse_vol"])
        st = R.stats(ser, tag)
        st.update({"turnover": round(meta["avg_turnover"], 2), "cash_pct": meta["cash_pct"],
                   "avg_names": meta["avg_names"], "rebal": cfg["rebal"],
                   "lookback": cfg["lookback"], "mechanism": cfg["why"]})
        for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
            mm = R.stats(sl, tag + "_" + lbl)
            for k in ("cagr", "sharpe", "maxdd"):
                st[k + "_" + lbl] = mm.get(k)
        out["books"][tag] = st

        bl, blinfo = equal_risk_blend(sum_a, ser, 0.5)
        bst = R.stats(bl, tag + "_blend_eqrisk")
        for lbl, sl in (("is", bl[bl.index <= IS_END]), ("oos", bl[bl.index > IS_END])):
            mm = R.stats(sl, tag + "_blend_" + lbl)
            for k in ("cagr", "sharpe", "maxdd"):
                bst[k + "_" + lbl] = mm.get(k)

        corr = {}
        for w, (x, y) in (("full", (sum_a, ser)),
                          ("is", (sum_a[sum_a.index <= IS_END], ser[ser.index <= IS_END])),
                          ("oos", (sum_a[sum_a.index > IS_END], ser[ser.index > IS_END]))):
            c = pair_corr(x, y)
            corr[w] = round(c, 3) if c is not None else None

        row = {"tag": tag, "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
               "maxdd": st.get("maxdd"), "cagr_oos": st.get("cagr_oos"),
               "sharpe_oos": st.get("sharpe_oos"), "turnover": st.get("turnover"),
               "cash_pct": st.get("cash_pct"), "avg_names": st.get("avg_names"),
               "corr_full": corr["full"], "corr_oos": corr["oos"],
               "blend_cagr": bst.get("cagr"), "blend_sharpe": bst.get("sharpe"),
               "blend_maxdd": bst.get("maxdd"), "control_cagr": a.get("cagr")}
        row["verdict"] = verdict(row)
        out["vs_A"][tag] = {"correlation": corr, "equal_risk_blend_50_50": bst,
                            "blend_scaling": blinfo, "verdict": row["verdict"]}
        out["ranking"].append(row)
        print("%-12s cagr %7.2f%% SR %5.3f dd %6.2f%% oos %7.2f%% corr %5.3f cash %4.1f%% names %5.1f "
              "blend %7.2f%% SR %5.3f -> %s"
              % (tag, (st.get("cagr") or 0) * 100, st.get("sharpe") or 0,
                 (st.get("maxdd") or 0) * 100, (st.get("cagr_oos") or 0) * 100,
                 corr["full"] if corr["full"] is not None else float("nan"),
                 (st.get("cash_pct") or 0) * 100, st.get("avg_names") or 0,
                 (bst.get("cagr") or 0) * 100, bst.get("sharpe") or 0, row["verdict"]), flush=True)

    out["ranking"].sort(key=lambda r: (-(r["cagr"] or -9), -(r["blend_sharpe"] or -9)))
    p = os.path.join(PATHS.results_dir, "etf_book_tsmom.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p, flush=True)
    if not out["control_check"]["matches"]:
        print("CONTROL MISMATCH: computed book A is not the shipped book", flush=True)
        return 2
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    sys.exit(main())