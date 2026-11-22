"""Shared machinery for the multi-asset strategy bench (O-20261122 continuous testing).

Why this module exists
----------------------
The book we have is one strategy on one asset class (ETF rotation). The CEO's
standing instruction (2026-11-22) is: test continuously, on real bars, across
strategies, styles and instruments -- and the four-gate rule (O-20261114-2325)
still says a test only counts if it changes a decision. So the bench is not a
research diary: every cell ends in GO / NO_EDGE / DATA-BLOCKED on a concrete
question -- "do we add this line to the book, and at what weight".

Protocol frozen before any number is read (applies to every cell)
-----------------------------------------------------------------
1. Signals at bar t use data through t's close; the position is held over
   t+1's return. No same-bar fill.
2. Roll gaps are excluded from returns. The main-continuous series is raw
   (never back-adjusted), so at a roll the price jumps to a more discounted
   contract. A holder does not lose that jump (they roll the position), so the
   jump is removed from the return series and the actual roll cost is charged
   through turnover instead. Ignoring this is how naive futures backtests
   manufacture trend profits out of roll jumps.
3. Costs are charged on notional turnover at a printed bp-per-side rate; every
   result is printed net. A gross-only number is never reported.
4. Three robustness tests are mandatory before a GO: both-halves, drop the
   best calendar year, and a random-sign control arm (same weights, same
   turnover, signs shuffled). The control is what tells a trend from a
   vol-harvest or a data artefact.
5. Equal-weight buy-and-hold of the same universe is printed next to the
   strategy, because "beats zero" is not the question; "beats holding" is.

Nothing here reads the network. Universe files are the ones the data lanes
already maintain under data/.
"""
import json
import math
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
BENCH_OUT = os.path.join(RESULTS, "bench")

TRADING_DAYS = 244.0
ROLL_SCALE = 8.0        # a bar move this many times the median |move| is a roll
ROLL_FLOOR = 0.005      # ...and it must be visible (0.5%) to count
VOL_WINDOW = 60         # realized-vol window for risk sizing
REBALANCE_BARS = 5      # weights are re-struck weekly, not every close
COST_BP_SIDE = 3.0      # per side of notional traded; printed on every face

FUTURES = ["IC", "IF", "IH", "IM", "AU", "RB", "SC", "T", "TF", "TS"]
EQUITY_FUT = {"IC", "IF", "IH", "IM"}
BOND_FUT = {"T", "TF", "TS"}
COMMODITY_FUT = {"AU", "RB", "SC"}


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def load_futures_products(products=None):
    """Return {code: DataFrame(index=date, open/high/low/close/volume)}."""
    products = products or FUTURES
    out = {}
    for code in products:
        path = os.path.join(DATA, "futures_daily", code + ".csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        if df.empty or "close" not in df:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates("date").set_index("date").sort_index()
        df = df[~df["close"].isna()]
        df = df[df["close"] > 0]
        if len(df) < 300:
            continue
        out[code] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return out


def load_index_close(code="sh000300"):
    path = os.path.join(DATA, "index_daily", code + ".csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.drop_duplicates("date").set_index("date").sort_index()["close"].astype(float)


def roll_adjusted_returns(close):
    """Daily returns with roll jumps set to zero, plus the roll mask.

    A roll is a move >= max(ROLL_SCALE * median |move|, ROLL_FLOOR). The mask is
    returned so the caller can disclose how many bars were touched instead of
    hiding the surgery.
    """
    close = np.asarray(close, dtype=float)
    r = np.zeros(len(close))
    if len(close) > 1:
        r[1:] = close[1:] / close[:-1] - 1.0
    finite = np.abs(r[np.isfinite(r)])
    med = float(np.median(finite)) if len(finite) else 0.0
    thr = max(ROLL_SCALE * med, ROLL_FLOOR)
    mask = np.abs(r) >= thr
    mask[0] = False
    r = np.where(mask, 0.0, r)
    r[~np.isfinite(r)] = 0.0
    return r, mask


def adjusted_price(close):
    """Price series rebuilt from roll-adjusted returns (signal input)."""
    r, _ = roll_adjusted_returns(close)
    return np.cumprod(1.0 + r)


# --------------------------------------------------------------------------
# performance
# --------------------------------------------------------------------------
def perf(ret, dates, rf=0.0):
    """Annualised return / vol / Sharpe / max drawdown / t-stat / yearly table."""
    r = np.asarray(ret, dtype=float)
    r = np.where(np.isfinite(r), r, 0.0)
    n = len(r)
    if n < 60:
        return {"n": n, "ann_pct": None, "sharpe": None, "mdd_pct": None,
                "t_stat": None, "years": {}}
    eq = np.cumprod(1.0 + r)
    years = n / TRADING_DAYS
    ann = eq[-1] ** (1.0 / years) - 1.0 if eq[-1] > 0 else -1.0
    vol = float(np.std(r, ddof=1)) * math.sqrt(TRADING_DAYS)
    sharpe = (float(np.mean(r)) * TRADING_DAYS - rf) / vol if vol > 0 else 0.0
    peak = np.maximum.accumulate(eq)
    mdd = float(np.min(eq / peak - 1.0))
    sd = float(np.std(r, ddof=1))
    t = float(np.mean(r)) / (sd / math.sqrt(n)) if sd > 0 else 0.0

    yearly = {}
    if dates is not None:
        yrs = pd.DatetimeIndex(dates).year
        logr = np.log1p(np.clip(r, -0.999999, None))
        for y in sorted(set(yrs)):
            sel = yrs == y
            if sel.sum() < 20:
                continue
            yearly[int(y)] = round(float(np.expm1(logr[sel].sum())) * 100.0, 2)

    drop_best = None
    if yearly:
        best = max(yearly, key=lambda k: yearly[k])
        # rebuild annualised from the other years using their day counts
        keep = [y for y in yearly if y != best]
        if keep:
            logr = np.log1p(np.clip(r, -0.999999, None))
            yrs = pd.DatetimeIndex(dates).year
            sel = np.isin(yrs, keep)
            days = int(sel.sum())
            if days > 60:
                drop_best = round(float(np.expm1(logr[sel].sum())) * 100.0
                                  * TRADING_DAYS / days, 2)
        else:
            drop_best = None

    return {
        "n": n,
        "ann_pct": round(ann * 100.0, 2),
        "vol_pct": round(vol * 100.0, 2),
        "sharpe": round(sharpe, 3),
        "mdd_pct": round(mdd * 100.0, 2),
        "t_stat": round(t, 2),
        "years": yearly,
        "best_year": max(yearly, key=lambda k: yearly[k]) if yearly else None,
        "drop_best_year_ann_pct": drop_best,
    }


def perf_periodic(ret, dates, periods_per_year):
    """Same readings as perf(), for returns sampled every k bars.

    perf() assumes one observation per trading day. A 20-bar rebalanced book
    handed to perf() is annualised as if each 20-day return were one day, which
    turns a 7%/yr bond book into +327%/yr (this cell's first run). Here the
    elapsed calendar time comes from the dates, and vol/Sharpe are scaled by the
    real sampling rate.
    """
    r = np.asarray(ret, dtype=float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 8 or dates is None:
        return {"n": n, "ann_pct": None, "vol_pct": None, "sharpe": None,
                "mdd_pct": None, "t_stat": None, "years": {}}
    dates = pd.DatetimeIndex(dates)
    span_years = max((dates[-1] - dates[0]).days / 365.25, 1e-9)
    eq = np.cumprod(1.0 + r)
    total = float(eq[-1])
    ann = total ** (1.0 / span_years) - 1.0 if total > 0 else -1.0
    vol = float(np.std(r, ddof=1)) * math.sqrt(periods_per_year)
    sharpe = (float(np.mean(r)) * periods_per_year) / vol if vol > 0 else 0.0
    peak = np.maximum.accumulate(eq)
    mdd = float(np.min(eq / peak - 1.0))
    sd = float(np.std(r, ddof=1))
    t = float(np.mean(r)) / (sd / math.sqrt(n)) if sd > 0 else 0.0

    yearly = {}
    yrs = dates.year
    for y in sorted(set(yrs)):
        sel = yrs == y
        if sel.sum() < 2:
            continue
        yearly[int(y)] = round(float(np.expm1(np.log1p(np.clip(r[sel], -0.999999, None)).sum())) * 100, 2)

    drop_best = None
    if len(yearly) >= 2:
        keep = sorted(yearly, key=lambda k: -yearly[k])[1:]
        sel = np.isin(yrs, keep)
        if sel.sum() >= 4:
            span_keep = max((dates[sel][-1] - dates[sel][0]).days / 365.25, 1e-9)
            g = float(np.prod(1.0 + r[sel]))
            if g > 0:
                drop_best = round((g ** (1.0 / span_keep) - 1.0) * 100, 2)

    return {"n": n, "ann_pct": round(ann * 100, 2), "vol_pct": round(vol * 100, 2),
            "sharpe": round(sharpe, 3), "mdd_pct": round(mdd * 100, 2),
            "t_stat": round(t, 2), "years": yearly,
            "best_year": max(yearly, key=lambda k: yearly[k]) if yearly else None,
            "drop_best_year_ann_pct": drop_best}


def split_perf_periodic(ret, dates, periods_per_year, split="2024-01-01"):
    dates = pd.DatetimeIndex(dates)
    cut = pd.Timestamp(split)
    arr = np.asarray(ret)
    full = perf_periodic(arr, dates, periods_per_year)
    ins = perf_periodic(arr[dates < cut], dates[dates < cut], periods_per_year)
    oos = perf_periodic(arr[dates >= cut], dates[dates >= cut], periods_per_year)
    halves = {}
    if len(arr) >= 8:
        mid = len(arr) // 2
        halves = {
            "first_half_ann_pct": perf_periodic(arr[:mid], dates[:mid], periods_per_year)["ann_pct"],
            "second_half_ann_pct": perf_periodic(arr[mid:], dates[mid:], periods_per_year)["ann_pct"],
        }
    return {"full": full, "is": ins, "oos": oos, **halves}


def split_perf(ret, dates, split="2024-01-01"):
    dates = pd.DatetimeIndex(dates)
    cut = pd.Timestamp(split)
    full = perf(ret, dates)
    ins = perf(np.asarray(ret)[dates < cut], dates[dates < cut])
    oos = perf(np.asarray(ret)[dates >= cut], dates[dates >= cut])
    halves = {}
    if len(ret) >= 240:
        mid = len(ret) // 2
        halves = {
            "first_half_ann_pct": perf(np.asarray(ret)[:mid], dates[:mid])["ann_pct"],
            "second_half_ann_pct": perf(np.asarray(ret)[mid:], dates[mid:])["ann_pct"],
        }
    return {"full": full, "is": ins, "oos": oos, **halves}


# --------------------------------------------------------------------------
# portfolio construction helpers
# --------------------------------------------------------------------------
def align_futures(panel):
    """Align products on a common daily index; returns (dates, {code: df}, rets)."""
    code_sets = [set(df.index) for df in panel.values()]
    dates = sorted(set.union(*code_sets)) if code_sets else []
    dates = pd.DatetimeIndex(dates)
    rets, vols, closes = {}, {}, {}
    for code, df in panel.items():
        c = df["close"].reindex(dates)
        r, mask = roll_adjusted_returns(c.values)
        r_s = pd.Series(r, index=dates)
        r_s[c.isna().values] = np.nan
        rets[code] = r_s
        adj = pd.Series(adjusted_price(c.ffill().values), index=dates)
        closes[code] = adj.where(c.notna())
        vols[code] = r_s.rolling(VOL_WINDOW, min_periods=30).std() * math.sqrt(TRADING_DAYS)
    return dates, closes, rets, vols


def vol_weighted_positions(signals, vols, target_vol=0.10, max_weight=2.0):
    """Equal risk budget across the instruments live *on that bar*.

    The budget must follow the live count: dividing by the eventual universe
    size while only two products have data leaves the early sample almost
    flat and quietly dilutes every full-sample reading. Live = signal present
    AND a usable 60d vol on that bar.
    """
    frame = pd.DataFrame(signals)
    v = pd.DataFrame(vols).reindex(frame.index)
    live = frame.notna() & v.notna() & (v > 0)
    n_live = live.sum(axis=1).replace(0, np.nan)
    # Equal risk contribution: each instrument's risk share is target/sqrt(N),
    # not target/N. With target/N the portfolio only reaches target/sqrt(N) when
    # the legs are uncorrelated (measured: 5.4% vol against a 10% target).
    budget = target_vol / np.sqrt(n_live)
    w = v.replace(0.0, np.nan).rdiv(budget, axis=0)
    pos = (frame * w).clip(-max_weight, max_weight)
    # Re-strike the weights weekly. Recomputing 1/vol every close trades the
    # vol estimate, not the signal -- on ten futures that alone is ~38x/yr of
    # notional turnover and pays for noise.
    if REBALANCE_BARS and REBALANCE_BARS > 1:
        keep = (np.arange(len(pos)) % REBALANCE_BARS) == 0
        pos = pos.where(pd.Series(keep, index=pos.index), np.nan).ffill()
    return pos, live.sum(axis=1)


def apply_costs(pos, rets, cost_bp_side=COST_BP_SIDE):
    """Hold pos[t-1] over ret[t]; charge |pos[t]-pos[t-1]| at cost_bp per side."""
    rframe = rets if isinstance(rets, pd.DataFrame) else pd.DataFrame(rets)
    rframe = rframe.reindex(pos.index)
    gross = (pos.shift(1) * rframe).sum(axis=1, min_count=1)
    turn = (pos - pos.shift(1)).abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    net = gross - turn * (cost_bp_side / 10000.0)
    return gross.fillna(0.0), net.fillna(0.0), turn.fillna(0.0)


def random_sign_control(pos, rets, draws=200, seed=20261122):
    """Same weights and turnover, signs shuffled -> the null distribution.

    If a real arm cannot beat this, what it found is the long/short vol
    asymmetry of the universe, not a trend.
    """
    rng = np.random.default_rng(seed)
    _, net, _ = apply_costs(pos, rets)
    real = float(np.mean(net.values) * TRADING_DAYS)
    base = pos.abs()
    signs = np.sign(pos).fillna(0.0).values
    sample = []
    for _ in range(draws):
        flip = rng.choice([-1.0, 1.0], size=signs.shape[1])
        p = base.mul(pd.Series(flip, index=base.columns), axis=1)
        _, n2, _ = apply_costs(p, rets)
        sample.append(float(np.mean(n2.values) * TRADING_DAYS))
    sample = np.array(sample)
    return {
        "real_ann_pct": round(real * 100.0, 2),
        "null_mean_ann_pct": round(float(sample.mean()) * 100.0, 2),
        "null_p95_ann_pct": round(float(np.percentile(sample, 95)) * 100.0, 2),
        "p_value": round(float((sample >= real).mean()), 4),
        "draws": draws,
    }


def weight_priority():
    """Best effort: run our own process below normal so the desktop stays fluid."""
    try:
        import psutil  # noqa: F401
        p = psutil.Process(os.getpid())
        if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS"):
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def available_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return None


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
        f.write("\n")
    os.replace(tmp, path)


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verdict_of(checks):
    """checks = {'H1': bool, ...}; None means not computable."""
    if not checks:
        return "NO_EDGE"
    vals = [None if v is None else bool(v) for v in checks.values()]
    if any(v is False for v in vals):
        return "NO_EDGE"
    if all(v is True for v in vals):
        return "GO"
    return "INCOMPLETE"


def fmt_pct(x):
    return "n/a" if x is None else f"{x:+.2f}%"


def fmt_num(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"
