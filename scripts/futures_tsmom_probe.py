"""Second book, round three: time-series momentum on the FUTURES panel.

Why: r1297's bake-off tested five cross-sectional mechanisms on the ETF panel and all
five were rejected -- the two that were genuinely different (5d reversal: 7% name
overlap; random: 46%) both lost money, and the two that made money were the same trade
as the shipped book (corr 0.62-0.75, 88% name overlap). The conclusion is not "no second
book exists", it is "the ETF cross-section does not contain one". A sleeve in a different
UNIVERSE cannot queue behind the shipped book's ADV, which was the whole point of looking
for a second book (r1280/r1295 capacity cap ~1.5M CNY at 1% ADV).

This script measures the cheapest genuinely-different candidate already on disk: the
10-variety main-continuous futures panel (`data/futures_daily/`), traded with classic
time-series momentum (long when the trailing return is positive, short when negative,
equal risk per variety). Nothing about it touches ETF ADV.

Modelling choices, all disclosed in the output:
  * weights are RISK-based: w_i = sign_i * (target_vol / sqrt(N)) / vol_i, so contract
    multipliers cancel out and no lot rounding is pretended. |w_i| capped at 2.0 and
    gross capped at 3.0 -- TSMOM at 8% vol target levers low-vol bond futures if left
    uncapped, and an uncapped backtest is a fiction.
  * cost is charged on |delta weight| at COST_PER_SIDE of notional (1bp). Real futures
    commissions on these varieties are ~0.2-1bp; margin/roll financing are NOT modelled
    and are called out as caveats.
  * main-continuous series splice contracts, so roll gaps live inside the return series.
    This is a known optimism/pessimism source and is stated, not smoothed away.
  * the sign-selection arm is compared against a seeded random-sign arm: with 10 series
    a "the sign worked" claim is cheap unless the null is beside it.

Exploratory measurement: no live face, no registry entry, no capital claim.
Outputs results/futures_tsmom_probe.json.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

from config import PATHS

DATA_DIR = os.path.join(ROOT, "data", "futures_daily")
IS_END = "2023-12-31"
TARGET_VOL = 0.08
COST_PER_SIDE = 0.0001
W_CAP = 2.0
GROSS_CAP = 3.0


def load_panel(data_dir=None):
    """close matrix over the futures varieties; index = union of trading dates."""
    data_dir = data_dir or DATA_DIR
    cols = {}
    for p in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
        v = os.path.splitext(os.path.basename(p))[0]
        d = pd.read_csv(p)
        if "date" not in d.columns or "close" not in d.columns:
            continue
        s = pd.Series(pd.to_numeric(d["close"], errors="coerce").values,
                      index=pd.to_datetime(d["date"]), name=v)
        s = s[~s.index.duplicated(keep="last")].dropna()
        if len(s) > 200:
            cols[v] = s
    close = pd.DataFrame(cols).sort_index()
    return close


def tsmom_weights(close, lookback=60, target_vol=TARGET_VOL, vol_window=60,
                  w_cap=W_CAP, gross_cap=GROSS_CAP, signs=None):
    """Risk-parity time-series momentum weights, all computed from data <= each row.

    signs (DataFrame) overrides the momentum sign -- used only by the random-sign null.
    Rows where any input is missing are left NaN, and the runner treats NaN as flat.
    """
    rets = close.pct_change()
    vol = rets.rolling(vol_window).std() * np.sqrt(252)
    mom = close.pct_change(lookback)
    sgn = np.sign(mom) if signs is None else signs
    n = close.shape[1]
    raw = sgn * ((target_vol / np.sqrt(n)) / vol)
    raw = raw.clip(-w_cap, w_cap)
    gross = raw.abs().sum(axis=1)
    # scale the whole book down only when gross breaches the cap (never levers up)
    scale = (gross_cap / gross).where(gross > gross_cap, 1.0)
    w = raw.mul(scale, axis=0)
    return w


def random_signs(close, seed=20261027):
    rs = np.random.RandomState(seed)
    vals = rs.choice([-1.0, 0.0, 1.0], size=close.shape, p=[0.45, 0.10, 0.45])
    return pd.DataFrame(vals, index=close.index, columns=close.columns)


def run_weights(close, w, cost=COST_PER_SIDE):
    """Weights decided at close t are held over t -> t+1 (one-bar execution lag)."""
    rets = close.pct_change().fillna(0.0)
    held = w.shift(1).fillna(0.0)
    gross_ret = (held * rets).sum(axis=1)
    turn = (held - held.shift(1).fillna(0.0)).abs().sum(axis=1)
    net = gross_ret - turn * cost
    eq = (1.0 + net).cumprod()
    return eq, float(turn.sum()), float(gross_ret.sum())


def stats(ser, label):
    ser = ser.dropna()
    if len(ser) < 60:
        return {"label": label, "note": "short"}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    r = ser.pct_change().dropna()
    vol = float(r.std() * np.sqrt(252))
    dd = ser / ser.cummax() - 1
    yearly = ser.groupby(ser.index.year).apply(lambda x: x.iloc[-1] / x.iloc[0] - 1)
    cagr = growth ** (1 / yrs) - 1
    return {"label": label, "years": round(yrs, 2), "cagr": round(float(cagr), 4),
            "vol": round(vol, 4),
            "sharpe": round(float(r.mean() * 252 / vol), 3) if vol > 0 else 0.0,
            "maxdd": round(float(dd.min()), 4),
            "worst_year": round(float(yearly.min()), 4),
            "neg_years": int((yearly < 0).sum())}


def daily_returns(ser):
    return ser.sort_index().pct_change().dropna()


def pair_corr(a, b):
    ra, rb = daily_returns(a), daily_returns(b)
    idx = ra.index.intersection(rb.index)
    if len(idx) < 20:
        return None
    return float(np.corrcoef(ra.reindex(idx).fillna(0.0), rb.reindex(idx).fillna(0.0))[0, 1])


def blend(series_list, weights):
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


def vol_normalize(ser, target_vol):
    """Scale a daily return stream to a given realised vol, so two books can be compared
    at the SAME risk. Fixed 50/50 weights de-lever the higher-vol leg, so a plain blend's
    lower CAGR is a leverage artefact, not a quality statement (r1291 lesson). This is an
    analytical normalisation, not a trading rule."""
    r = ser.pct_change().dropna()
    v = float(r.std() * np.sqrt(252))
    if v <= 0:
        return ser
    k = target_vol / v
    eq = (1.0 + r * k).cumprod()
    eq.index = r.index
    return eq


def sell_side_flip(w):
    """How often the sign of the book actually changes -- a TSMOM book that never flips
    is a buy-and-hold in disguise."""
    s = np.sign(w.fillna(0.0))
    chg = (s - s.shift(1)).abs().sum(axis=1)
    return int((chg > 0).sum())


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

    idx = pd.bdate_range("2021-01-01", periods=200)
    cols = ["AU", "IC", "T"]
    up = pd.DataFrame({c: 1.0 + 0.001 * np.arange(len(idx)) for c in cols}, index=idx, columns=cols)
    up["T"] = 1.0 - 0.0008 * np.arange(len(idx))     # one variety trends down

    w = tsmom_weights(up, lookback=60, vol_window=20, target_vol=0.08)
    last = w.dropna().iloc[-1]
    chk("L1 sign follows momentum", last["AU"] > 0 and last["IC"] > 0 and last["T"] < 0,
        "up=%.2f,%.2f down=%.2f" % (last["AU"], last["IC"], last["T"]))

    # L2 causality: weight at row t must not change when later rows are appended
    w1 = tsmom_weights(up.iloc[:150], lookback=60, vol_window=20)
    t = up.index[139]
    same = np.allclose(w.iloc[139].dropna().values, w1.loc[t].dropna().values)
    chk("L2 weights are causal", same, "row t identical when the panel is truncated after t")

    # L3 the one-bar execution lag is real. A constant weight of 1 must earn nothing on
    # the first bar (the position cannot exist before it is decided) and must then track
    # the holding-period return exactly -- a leaked (same-bar) book would put P&L on bar 0.
    one = pd.DataFrame(1.0, index=idx, columns=cols)
    eqc, _, _ = run_weights(up, one)
    r = up.pct_change().fillna(0.0)
    held = one.shift(1).fillna(0.0)
    turn = (held - held.shift(1).fillna(0.0)).abs().sum(axis=1)
    expect = (1.0 + (held * r).sum(axis=1) - turn * COST_PER_SIDE).cumprod()
    chk("L3 execution lag is applied",
        abs(float(eqc.iloc[0]) - 1.0) < 1e-12 and np.allclose(eqc.values, expect.values),
        "bar0 nav %.6f, path identical to a one-bar-shifted book" % eqc.iloc[0])

    # L4 the gross cap binds: a low-vol book must never exceed the cap
    quiet = up.pct_change().mul(0.05).add(1).cumprod() * 100
    wq = tsmom_weights(quiet, lookback=60, vol_window=20)
    g = wq.abs().sum(axis=1).max()
    chk("L4 gross cap binds", g <= GROSS_CAP + 1e-9, "max gross %.3f" % g)

    # L5 cost is charged on turnover (a zero-turnover book pays nothing)
    flat = pd.DataFrame(1.0, index=idx, columns=cols)
    eq0, turn0, _ = run_weights(flat, pd.DataFrame(0.0, index=idx, columns=cols))
    chk("L5 flat book pays nothing", abs(float(eq0.iloc[-1]) - 1.0) < 1e-12 and turn0 == 0.0,
        "nav %.6f turn %.3f" % (eq0.iloc[-1], turn0))

    # L6 the null arm is reproducible
    a, b = random_signs(up), random_signs(up)
    chk("L6 random-sign control deterministic", a.equals(b), "same seed -> identical signs")

    print("\nselftest %d/%d" % (ok, total), flush=True)
    return 0 if ok == total else 1


def etf_book_series():
    """The shipped ETF book's daily equity curve, built the way the card prices it."""
    import etf_book_production as P
    import etf_robust_pf as R
    import etf_composite_pf as E
    close, openp, amt, score_a, cls, n_flip = P.prep_panel()
    ser, turn = R.open_to_open_equity(close, openp, amt, score_a, 20, 12, 0.0010,
                                      vol_target=TARGET_VOL)
    return ser, {"names": int(close.shape[1]), "flips_repaired": int(n_flip),
                 "cutoff": str(close.index[-1].date())}


def main():
    close = load_panel()
    print("futures panel varieties %d bars %d %s..%s"
          % (close.shape[1], close.shape[0], close.index[0].date(), close.index[-1].date()),
          flush=True)

    arms = {
        "tsmom60": dict(lookback=60),
        "tsmom120": dict(lookback=120),
    }
    out = {"evidence_cutoff": str(close.index[-1].date()),
           "universe": {"varieties": list(close.columns), "bars": int(close.shape[0]),
                        "start": str(close.index[0].date()),
                        "source": "data/futures_daily main-continuous (sina), roll gaps live in the series"},
           "model": {"sizing": "risk parity w_i = sign_i*(target/sqrt(N))/vol_i, |w_i|<=%.1f, gross<=%.1f"
                               % (W_CAP, GROSS_CAP),
                     "execution": "weights decided at close t, held over t->t+1",
                     "cost_per_side": COST_PER_SIDE,
                     "target_vol": TARGET_VOL,
                     "not_modelled": "margin, financing/carry, roll cost, contract multipliers (cancel in risk sizing)"},
           "note": "exploratory; not a live face, not registered, no capital claim",
           "arms": {}}

    for tag, kw in arms.items():
        w = tsmom_weights(close, **kw)
        eq, turn, gross_ret = run_weights(close, w)
        full = stats(eq, tag)
        full["turnover_total"] = round(turn, 2)
        full["sum_gross_return"] = round(gross_ret, 4)
        full["sign_flip_days"] = sell_side_flip(w)
        full["is"] = stats(eq[eq.index <= IS_END], tag + "_is")
        full["oos"] = stats(eq[eq.index > IS_END], tag + "_oos")
        out["arms"][tag] = full

    # null control: same sizing, random signs (10 series, so a lucky sign set is cheap)
    wnull = tsmom_weights(close, signs=random_signs(close))
    eqn, turnn, _ = run_weights(close, wnull)
    out["arms"]["random_sign"] = stats(eqn, "random_sign")
    out["arms"]["random_sign"]["turnover_total"] = round(turnn, 2)

    # long-only reference: no sign selection at all
    wl = tsmom_weights(close, signs=pd.DataFrame(1.0, index=close.index, columns=close.columns))
    eql, _, _ = run_weights(close, wl)
    out["arms"]["long_only"] = stats(eql, "long_only")
    for tag in ("random_sign", "long_only"):
        eqx = {"random_sign": eqn, "long_only": eql}[tag]
        out["arms"][tag]["is"] = stats(eqx[eqx.index <= IS_END], tag + "_is")
        out["arms"][tag]["oos"] = stats(eqx[eqx.index > IS_END], tag + "_oos")

    # pair with the shipped ETF book over the common window
    try:
        ser_etf, etf_meta = etf_book_series()
        out["etf_book"] = etf_meta
        for tag in ("tsmom60", "tsmom120"):
            w = tsmom_weights(close, **arms[tag])
            eq, _, _ = run_weights(close, w)
            idx = eq.index.intersection(ser_etf.index)
            a, b = eq.reindex(idx).dropna(), ser_etf.reindex(idx).dropna()
            idx2 = a.index.intersection(b.index)
            a, b = a.reindex(idx2), b.reindex(idx2)
            out["arms"][tag]["vs_etf_book"] = {
                "corr_full": round(pair_corr(a, b), 3) if pair_corr(a, b) is not None else None,
                "corr_oos": round(pair_corr(a[a.index > IS_END], b[b.index > IS_END]), 3)
                if pair_corr(a[a.index > IS_END], b[b.index > IS_END]) is not None else None,
                "common_window": [str(idx2[0].date()), str(idx2[-1].date())],
                "blend_50_50": stats(blend([a, b], [0.5, 0.5]), tag + "_blend50"),
                "etf_alone": stats(b, "etf_alone"),
            }
            # Same-risk comparison: both books scaled to the ETF book's own realised vol,
            # plus the 50/50 blend scaled to it. Without this, "the blend earns less"
            # would just be reporting that a 50/50 mix halves the book that earns more.
            v_etf = float(daily_returns(b).std() * np.sqrt(252))
            bl = blend([a, b], [0.5, 0.5])
            out["arms"][tag]["vs_etf_book"]["at_equal_vol_%0.2f" % (v_etf * 100)] = {
                "target_vol": round(v_etf, 4),
                "etf_alone": stats(vol_normalize(b, v_etf), "etf_at_vol"),
                "sleeve": stats(vol_normalize(a, v_etf), "sleeve_at_vol"),
                "blend_50_50": stats(vol_normalize(bl, v_etf), "blend_at_vol"),
                "note": "all three scaled to the ETF book's realised vol; analytical, not a trading rule",
            }
    except Exception as exc:      # panel/prep failure must not invalidate the futures arms
        out["etf_book"] = {"error": "%s: %s" % (type(exc).__name__, exc)}

    p = os.path.join(PATHS.results_dir, "futures_tsmom_probe.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    for tag, a in out["arms"].items():
        extra = ""
        v = a.get("vs_etf_book")
        if v:
            extra = " | corr vs ETF %.3f blend %.2f%%" % (
                v["corr_full"] if v["corr_full"] is not None else float("nan"),
                (v["blend_50_50"].get("cagr") or 0) * 100)
        print("%-11s cagr %7.2f%% SR %5.3f dd %6.2f%% oos %7.2f%% flips %4d%s"
              % (tag, (a.get("cagr") or 0) * 100, a.get("sharpe") or 0,
                 (a.get("maxdd") or 0) * 100, (a.get("oos", {}) or {}).get("cagr", 0) * 100,
                 a.get("sign_flip_days") or 0, extra), flush=True)
    print("saved", p, flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main())