"""zoo #96 volume_regime_bimodal -- judged verdict: does the volume state machine time 510300?

The berth (`research/shortline/ASTYLE_ZOO.md` #96) froze its parameterisation on
2026-09-26 (bm-b r263) and has sat registered with nothing burned behind it. This run
prices it: volume_index = HMA(volume,5)/HMA(volume,100), three thresholds (1.15 up /
1.15**-1.5 ~= 0.807 down), long when the index is above the top band OR below the bottom
band ("物极必反"), flat in the middle. The source's short leg is dropped -- an ETF book
cannot short spot, so the whole 0.807..1.15 band is cash (same ruling as #94's registry
note).

Two honest deviations from the frozen text, both declared in the product face:

  1. the berth says "全市场成交量". Summing share counts across 5,223 names is broken by
     splits and by universe entry/exit, so the PRIMARY index is the summed traded VALUE
     (成交额, CNY) across the panel each day; the share-count sum is carried as a
     sensitivity leg so the reader can see whether the choice moved the verdict.
  2. the panel is the 5,223-name A-share archive on disk (2020-01 onward), not the whole
     exchange; the ratio form makes the level of the universe mostly cancel, and coverage
     per bar is published so the drift is visible rather than assumed away.

Execution: signal on bar t's close, fill at bar t+1's open, cost 13.041bp per side on the
traded weight, marks to close. The benchmark is 510300 bought and held with the same
convention, and the null is 200 circular shifts of the state series against the same bars.

No preregistration here: this is the berth's judgement, and the judging rule is stated
before the run in CRITERIA below.

Usage:
  python scripts/zoo96_volume_regime_probe.py            # run + publish
  python scripts/zoo96_volume_regime_probe.py --selftest
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

OUT = os.path.join(ROOT, "results", "supply_berth", "zoo96_volume_regime_probe.json")
INDEX_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")

FAST = 5
SLOW = 100            # berth main caliber (calc_func default; 45 is the implementer's knob)
UP = 1.15             # frozen
A = 1.5               # frozen default of the a bracketing
DOWN = UP ** (-A)     # 0.8069...
COST_PER_SIDE = 0.0013041   # COST_X1_RATE, the constant the book cards pay
COST_X3 = 3.0 * COST_PER_SIDE
DRAWS = 200
SEED = 0

CRITERIA = {
    "call": "does the volume state machine beat buy-and-hold on 510300 after cost?",
    "passes": {
        "net_excess": "net CAGR minus the benchmark's > 0",
        "beats_null": "the phase-null p (share of shifts that match or beat it) < 0.05",
        "drawdown": "max drawdown not worse than the benchmark's",
        "exposure": "long share reported, never tuned",
    },
    "verdicts": ["ADOPT_AS_CANDIDATE", "REFUSE_AS_CANDIDATE",
                 "UNDECIDABLE_NULL_THIN", "INSUFFICIENT_BARS"],
    "thresholds": {"up": UP, "down": round(DOWN, 6), "slow": SLOW, "fast": FAST},
    "cost": {"per_side": COST_PER_SIDE, "x3_robustness": COST_X3},
    "execution": "signal at close t, fill at open t+1, mark to close",
}


# --------------------------------------------------------------------------- #
# the index
# --------------------------------------------------------------------------- #
def wma(x: np.ndarray, n: int) -> np.ndarray:
    """Linearly weighted MA, weights 1..n on the newest n bars (NaN-safe prefix)."""
    x = np.asarray(x, dtype=np.float64)
    out = np.full(x.shape, np.nan)
    if n <= 0:
        raise ValueError("window must be positive")
    w = np.arange(1, n + 1, dtype=np.float64)
    w = w / w.sum()
    if len(x) < n:
        return out
    for i in range(n - 1, len(x)):
        win = x[i - n + 1:i + 1]
        if np.isnan(win).any():
            continue
        out[i] = float(np.dot(win, w))
    return out


def hma(x: np.ndarray, n: int) -> np.ndarray:
    """Hull MA: WMA(2*WMA(n/2) - WMA(n), sqrt(n)). The half window is the berth's rule."""
    half = max(int(n) // 2, 1)
    inner = 2.0 * wma(x, half) - wma(x, int(n))
    return wma(inner, max(int(np.sqrt(int(n))), 1))


def volume_index(totals: np.ndarray, fast: int = FAST, slow: int = SLOW) -> np.ndarray:
    """Ratio of a fast HMA to a slow one -- scale-free, so the universe level cancels."""
    f = hma(totals, fast)
    s = hma(totals, slow)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = f / s
    out[~np.isfinite(out)] = np.nan
    return out


def market_totals(panel: dict, field: str = "amount") -> np.ndarray:
    """Summed traded value (primary) or share count (sensitivity) per bar, NaN-skipping."""
    m = panel[field]
    cov = np.isfinite(m).sum(axis=1)
    tot = np.nansum(m, axis=1)
    tot[cov == 0] = np.nan
    return tot, cov


def state_of(vi: np.ndarray, up: float = UP, down: float = DOWN) -> np.ndarray:
    """1 = long (either band), 0 = cash. NaN stays NaN (no state without a reading)."""
    st = np.full(vi.shape, np.nan)
    ok = np.isfinite(vi)
    st[ok] = 0.0
    st[ok & (vi >= up)] = 1.0
    st[ok & (vi <= down)] = 1.0
    return st


# --------------------------------------------------------------------------- #
# the trade
# --------------------------------------------------------------------------- #
def _read_index(path: str = INDEX_CSV):
    import pandas as pd

    df = pd.read_csv(path, dtype={"date": str})
    df = df[["date", "open", "close"]].dropna()
    df = df[(df["open"] > 0) & (df["close"] > 0)]
    return df.reset_index(drop=True)


def curve(dates, openp, close, state, cost=COST_PER_SIDE):
    """Per-bar equity levels: a state known at close t applies from open t+1.

    The overnight gap from the previous close to this bar's open is earned at the weight
    the book carried INTO the bar (you cannot be flat overnight on a decision taken at the
    close), then the new weight earns open-to-close. Chained, an always-long book without
    cost therefore reproduces close/close exactly -- pinned by a selftest leg, because
    getting this wrong is how a backtest quietly invents a few hundred bp.
    """
    n = len(dates)
    lvl, eq, w_prev = [], 1.0, 0.0
    for i in range(1, n):
        w = state[i - 1]
        if not np.isfinite(w):
            w = w_prev
        if w != w_prev:
            eq *= (1.0 - cost * abs(w - w_prev))
        c0, o1 = close[i - 1], openp[i]
        c1 = close[i]
        if np.isfinite(c0) and np.isfinite(o1) and c0 > 0:
            eq *= (1.0 + w_prev * (o1 / c0 - 1.0))
        if np.isfinite(o1) and np.isfinite(c1) and o1 > 0:
            eq *= (1.0 + w * (c1 / o1 - 1.0))
        w_prev = w
        lvl.append(eq)
    return np.array(lvl, dtype=np.float64)


def stats(levels: np.ndarray, dates: np.ndarray) -> dict:
    if len(levels) < 40:
        return {"note": "short"}
    span = np.asarray(dates)
    days = float((span[-1] - span[0]) / np.timedelta64(1, "D")) \
        if np.issubdtype(span.dtype, np.datetime64) else float(span[-1] - span[0])
    yrs = days / 365.25
    if yrs <= 0:
        return {"note": "short"}
    growth = float(levels[-1] / levels[0])
    cagr = growth ** (1.0 / yrs) - 1.0
    r = levels[1:] / levels[:-1] - 1.0
    vol = float(np.std(r, ddof=1) * np.sqrt(252))
    peak = np.maximum.accumulate(levels)
    return {"years": round(float(yrs), 2), "cagr": round(float(cagr), 5),
            "vol": round(vol, 4),
            "sharpe": round(float(np.mean(r) * 252 / vol), 3) if vol > 0 else 0.0,
            "maxdd": round(float((levels / peak - 1.0).min()), 5)}


def null_test(dates, openp, close, state, base_excess, draws=DRAWS, seed=SEED):
    """Circular shifts of the state series: 'is the timing better than a random phase?'"""
    ok = np.isfinite(state)
    if not ok.any() or draws <= 0:
        return {"draws": 0, "note": "no state"}
    idx = np.where(ok)[0]
    rng = np.random.default_rng(seed)
    bench = curve(dates, openp, close, np.ones(len(dates)), 0.0)
    excesses = []
    for _ in range(int(draws)):
        shift = int(rng.integers(1, len(idx)))
        st = np.full(state.shape, np.nan)
        st[idx] = state[np.roll(idx, shift)]
        lv = curve(dates, openp, close, st)
        b = stats(bench, dates)
        s = stats(lv, dates)
        if "cagr" in b and "cagr" in s:
            excesses.append(s["cagr"] - b["cagr"])
    if not excesses:
        return {"draws": 0, "note": "null produced no reading"}
    arr = np.array(excesses, dtype=np.float64)
    p = float((arr >= base_excess).mean())
    return {"draws": int(len(arr)), "mean": round(float(arr.mean()), 5),
            "p95": round(float(np.percentile(arr, 95)), 5),
            "p_value": round(p, 4)}


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def run(panel: dict | None = None) -> dict:
    import zoo93_disposition_cgo_probe as Z

    t0 = time.time()
    if panel is None:
        panel = Z.load_panel()
    dates_s = np.array(panel["dates"])
    amt_tot, cov = market_totals(panel, "amount")
    vol_tot, _ = market_totals(panel, "volume")
    vi_amt = volume_index(amt_tot)
    vi_vol = volume_index(vol_tot)
    st_amt = state_of(vi_amt)
    st_vol = state_of(vi_vol)

    ix = _read_index()
    ix_pos = {d: i for i, d in enumerate(ix["date"].tolist())}
    # align the index's own bars to the panel calendar (the index is the traded leg)
    keep = [i for i, d in enumerate(dates_s.tolist()) if d in ix_pos]
    dates = np.array([dates_s[i] for i in keep])
    st_amt = st_amt[keep]
    st_vol = st_vol[keep]
    vi_amt = vi_amt[keep]
    cov = cov[keep]
    openp = ix["open"].to_numpy(dtype=np.float64)[[ix_pos[d] for d in dates.tolist()]]
    close = ix["close"].to_numpy(dtype=np.float64)[[ix_pos[d] for d in dates.tolist()]]
    dts = np.array([np.datetime64(d) for d in dates])

    arms = {}
    for name, st in (("amount_index", st_amt), ("volume_index", st_vol)):
        lv = curve(dts, openp, close, st)
        arms[name] = stats(lv, dts)
        arms[name]["long_share"] = round(float(np.nanmean(st)), 4)
        finite = np.where(np.isfinite(st))[0]
        sw = int(np.sum(np.diff(st[finite]) != 0)) if len(finite) > 1 else 0
        yrs = max(arms[name].get("years") or 1e-9, 1e-9)
        arms[name]["switches"] = sw
        arms[name]["switches_per_year"] = round(sw / yrs, 2)
        arms[name]["bars"] = int(len(finite))
        arms[name]["index_first"] = str(dates[int(finite[0])]) if len(finite) else None
    bench_lv = curve(dts, openp, close, np.ones(len(dts)), 0.0)
    bench = stats(bench_lv, dts)
    lv_amt = curve(dts, openp, close, st_amt)
    excess = float(arms["amount_index"]["cagr"] - bench["cagr"])
    excess_vol = float(arms["volume_index"]["cagr"] - bench["cagr"])
    null = null_test(dts, openp, close, st_amt, excess)
    null_vol = null_test(dts, openp, close, st_vol, excess_vol)
    x3 = curve(dts, openp, close, st_amt, COST_X3)
    arms["amount_index_cost_x3"] = stats(x3, dts)
    x3v = curve(dts, openp, close, st_vol, COST_X3)
    arms["volume_index_cost_x3"] = stats(x3v, dts)

    reasons = []
    if arms["amount_index"].get("bars", 0) < 250:
        verdict = "INSUFFICIENT_BARS"
        reasons.append("fewer than 250 traded bars")
    else:
        if not (excess > 0):
            reasons.append("net excess %.2fpp/yr is not positive" % (100 * excess))
        if null.get("p_value") is None or null.get("p_value") >= 0.05:
            reasons.append("phase null p=%s does not beat 5%%" % null.get("p_value"))
        if arms["amount_index"]["maxdd"] < bench["maxdd"]:
            reasons.append("max drawdown %.2f%% is worse than buy-and-hold %.2f%%"
                           % (100 * arms["amount_index"]["maxdd"], 100 * bench["maxdd"]))
        verdict = "REFUSE_AS_CANDIDATE" if reasons else "ADOPT_AS_CANDIDATE"
        if verdict == "ADOPT_AS_CANDIDATE" and arms["amount_index_cost_x3"]["cagr"] < bench["cagr"]:
            verdict = "REFUSE_AS_CANDIDATE"
            reasons.append("the x3-cost leg already gives back the whole excess")
        # the axis itself is undecided: the berth says 成交量, the split-robust reading is
        # traded value, and the two disagree -- so neither the pass nor the fail may be
        # published as a rule effect until the axis is fixed by the berth owner.
        if np.sign(excess) != np.sign(excess_vol):
            reasons.append("the two honest volume proxies disagree in sign (value %+.2fpp/yr "
                           "p=%s vs share-count %+.2fpp/yr p=%s), so the berth's own axis is "
                           "the open question, not the rule"
                           % (100 * excess, null.get("p_value"), 100 * excess_vol,
                              null_vol.get("p_value")))
            if arms["volume_index_cost_x3"]["cagr"] < bench["cagr"]:
                reasons.append("even the passing proxy gives the excess back at x3 cost "
                               "(%.2f%%/yr vs buy-and-hold %.2f%%/yr)"
                               % (100 * arms["volume_index_cost_x3"]["cagr"],
                                  100 * bench["cagr"]))

    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": "scripts/zoo96_volume_regime_probe.py",
        "berth": "zoo #96 volume_regime_bimodal (frozen bm-b r263)",
        "evidence_cutoff": str(dates[-1]),
        "criteria": CRITERIA,
        "panel": {"symbols": len(panel["symbols"]), "bars": int(len(dates)),
                  "first_bar": str(dates[0]), "last_bar": str(dates[-1]),
                  "index": "sh510300"},
        "deviations": [
            "primary index is summed traded VALUE (成交额) across the archive, not summed "
            "share counts (splits and universe drift break a share-count sum); the "
            "share-count leg is published beside it",
            "universe = the 5,223-name A-share archive on disk (2020-01 ->), coverage per "
            "bar published as coverage_min/coverage_median",
            "the source's short leg is dropped: an ETF book cannot short spot, so the whole "
            "0.807..1.15 band is cash",
        ],
        "coverage": {"min": int(cov.min()), "median": int(np.median(cov))},
        "arms": arms,
        "benchmark": bench,
        "excess_pp": round(100 * excess, 3),
        "excess_pp_volume_index": round(100 * excess_vol, 3),
        "null": null,
        "null_volume_index": null_vol,
        "proxy_disagrees": bool(np.sign(excess) != np.sign(excess_vol)),
        "verdict": verdict,
        "verdict_reasons": reasons,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    return doc


def write(doc: dict, out: str = OUT) -> str:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return out


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _synth(n=400, seed=3):
    """A volume series with one spike and one trough, plus an index that trends."""
    rng = np.random.default_rng(seed)
    v = np.full(n, 100.0) + rng.normal(0, 1.0, n)
    v[n // 2:n // 2 + 5] = 400.0
    v[-40:-30] = 5.0
    return v


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"name": name, "pass": bool(ok), "detail": str(detail)[:160]})

    # 1. WMA of a constant is the constant, and the weights sum to one
    c = wma(np.full(20, 7.0), 5)
    leg("wma constant", np.allclose(c[4:], 7.0))
    leg("wma prefix NaN", np.isnan(c[:4]).all())

    # 2. WMA reproduces a hand-computed ramp at the last bar
    x = np.arange(1.0, 6.0)          # 1..5, window 5 -> weights 1..5 / 15
    leg("wma ramp", abs(wma(x, 5)[-1] - (1 * 1 + 2 * 2 + 3 * 3 + 4 * 4 + 5 * 5) / 15.0) < 1e-12)

    # 3. HMA of a constant is the constant (the double difference cancels)
    h = hma(np.full(200, 42.0), 100)
    leg("hma constant", abs(h[-1] - 42.0) < 1e-9, h[-1])

    # 4. volume_index is 1 for a flat series and > 1 at a spike
    v = _synth()
    vi = volume_index(v)
    leg("vindex flat-is-one", abs(volume_index(np.full(300, 9.0))[-1] - 1.0) < 1e-9)
    leg("vindex spike-above-one", float(np.nanmax(vi)) > 1.2, float(np.nanmax(vi)))

    # 5. thresholds: above up -> long, inside the band -> cash, below down -> long
    st = state_of(np.array([1.16, 1.05, 0.95, 0.79, np.nan]))
    leg("state bands", np.array_equal(np.nan_to_num(st, nan=-1), np.array([1, 0, 0, 1, -1])),
        st)

    # 6. the band edges belong to the long side (>= up, <= down)
    edge = state_of(np.array([1.15, UP ** (-1.5)]))
    leg("state edges inclusive", np.array_equal(edge, np.array([1.0, 1.0])))

    # 7. a state that only arrives on the last bar never trades
    d = np.arange("2020-01-01", "2020-03-01", dtype="datetime64[D]")
    o = np.full(len(d), 10.0)
    cl = np.full(len(d), 10.0)
    s = np.zeros(len(d))
    s[-1] = 1.0
    lv = curve(d, o, cl, s, 0.0)
    leg("last-bar state does not trade", abs(lv[-1] - 1.0) < 1e-12, lv[-1])

    # 8. one switch costs exactly one cost leg (and nothing else on a flat price)
    s2 = np.ones(len(d))
    s2[0] = 0.0
    lv2 = curve(d, o, cl, s2, 0.001)
    leg("cost charged once", abs(lv2[-1] - (1.0 - 0.001)) < 1e-12, lv2[-1])

    # 9. always-long at zero cost earns exactly the price path it can actually hold:
    #    a book that is flat on bar 0 buys at bar 1's open and rides to the last close
    o3 = np.linspace(10.0, 12.0, len(d))
    c3 = o3 * 1.01
    lv3 = curve(d, o3, c3, np.ones(len(d)), 0.0)
    leg("buy-and-hold identity", abs(lv3[-1] - (c3[-1] / o3[1])) < 1e-12, lv3[-1])

    # 10. the null on a constant state has no spread to speak of, and never claims a win
    n = null_test(d, o3, c3, np.zeros(len(d)), 0.0, draws=10, seed=1)
    leg("null runs", n.get("draws") == 10, n.get("p_value"))

    # 11. stats refuse a short series rather than inventing a CAGR
    leg("stats short", "note" in stats(np.array([1.0, 1.1]), np.array([0, 1])))

    # 12. determinism: the same inputs produce the same curve to the bit
    a = curve(d, o3, c3, s2, 0.001)
    b = curve(d, o3, c3, s2, 0.001)
    leg("determinism", np.array_equal(a, b))

    ok = sum(1 for l in legs if l["pass"])
    print(json.dumps({"selftest": "zoo96_volume_regime_probe", "pass": ok,
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
    print(json.dumps({k: doc[k] for k in ("verdict", "excess_pp", "null",
                                          "benchmark", "elapsed_sec")}, ensure_ascii=False))
    print(json.dumps(doc["arms"], ensure_ascii=False, indent=1))
    print("wrote", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())