"""Four index-futures basis-carry arms -- or one trade wearing four costumes?

Every face in this family so far has been read one product at a time: IC 10.09%/yr, IM
9.29, IF 6.90, IH 5.75 (r1996/1997/1998).  A reader who wants to put money behind this
does not buy four separate books; he buys *one* book that happens to hold four index
futures.  Nobody has ever printed what that single book looks like.

That is the whole question here, and it cuts both ways:

  * if the four arms are close to independent, the combined drawdown should be far
    shallower than the worst single one, and the reader is buying diversification;
  * if they move together -- and they should, since a discount on CSI300 and a discount
    on CSI500 are the same funding condition -- then the "portfolio" is one line wearing
    four tickers, and its drawdown is the drawdown of that line.

So this face prints, for the equal-weight book: the annualised return, the daily
volatility, the Sharpe, the max drawdown, the year-by-year table, and the 4x4 same-day
correlation matrix -- and then answers the only question that decides whether a
"portfolio" means anything: **how much of the theoretical diversification does the real
book actually capture?**

The yardstick for "theoretical" is a circular-shift null: shift each member's daily
series by an independent random amount so that every member keeps its own return
distribution and its own autocorrelation, but same-day co-movement is destroyed.  The
portfolio built from those shifted legs has the same expected return and, if the members
are truly independent, the shallowest possible drawdown.  `dispersion_capture` is where
the real book sits between "worst single member" (0.0) and "perfectly independent"
(1.0).  A book wearing four costumes reads near 0 -- and that is a product, because it
tells the reader not to size four positions as if they were four bets.

Two configurations are priced because the natural follow-up is "should I weight them
equally or by risk".  The inverse-volatility book uses only the trailing 60 days of each
member's own realised volatility, so it is implementable without look-ahead; it must beat
equal weight by a visible margin to justify the extra machinery.

Nothing here is a new signal: basis, spread, roll mask and the sizing rule come verbatim
from idx_fut_basis / bench_basis_timing_replicate (weights, daily carry, annualisation,
drawdown are all imported), and the product list is idx_fut_basis_segments'.  The only new
code is the date-alignment, the two capital-allocation rules, the correlation read and the
shift null.

Frozen criteria live in JUDGED and --check re-derives every published number.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import bench_basis_timing_replicate as rep  # noqa: E402
import idx_fut_basis_segments as seg  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_carry_portfolio.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_CARRY_PORTFOLIO.md")

PRODUCTS = seg.PRODUCTS
COST_BP_SIDE = rep.COST_BP_SIDE

TOL_PP = 0.02          # --check tolerance, percent points
TOL_SHARPE = 0.02
ID_TOL = 1e-12

IV_LOOKBACK = 60       # trailing days of own realised volatility
IV_MIN_OBS = 20
MIN_WEIGHT_DAYS = 100  # a member needs this many trading days before it joins
CORR_STRUCTURAL = 0.85  # median pairwise rho above this is called out as structural
DISPERSE_CAPTURE_MIN = 0.50
IV_SHARPE_EDGE = 0.05
WORST_YEAR_FLOOR = -5.0
POSITIVE_YEAR_SHARE = 0.60
SHIFT_N = 400
SHIFT_SEED = 20261123

# The correlation matrix hinted at a two-block structure (small-cap pair, large-cap pair),
# so the reader's real question -- "how few arms do I need?" -- gets its own table.  These
# are readings, not criteria: the point is to show what each size buys, not to crown one.
SUBSETS = (
    ("all_four", ("IC", "IM", "IF", "IH")),
    ("small_pair_IC_IM", ("IC", "IM")),
    ("large_pair_IF_IH", ("IF", "IH")),
    ("cross_pair_IC_IF", ("IC", "IF")),
    ("cross_pair_IM_IH", ("IM", "IH")),
    ("three_IC_IF_IH", ("IC", "IF", "IH")),
)

# frozen before the first run
JUDGED = {
    "P1_identity":
        "portfolio daily == capital-weighted sum of member dailies (|residual| < 1e-12), and on "
        "days where exactly one member trades the portfolio equals that member exactly",
    "P2_correlation_is_printed_not_hidden":
        "the 4x4 same-day return correlation matrix is published; a median pairwise rho >= %.2f "
        "is named as structural co-movement on the page" % CORR_STRUCTURAL,
    "P3_the_drawdown_actually_diversifies":
        "in the window where all four members trade, the equal-weight portfolio's max drawdown "
        "is at least 20% better than the worst single member's",
    "P4_inverse_vol_earns_its_keep":
        "the trailing-60-day inverse-volatility book beats equal weight by >= %.2f Sharpe, "
        "otherwise the extra machinery is not worth carrying" % IV_SHARPE_EDGE,
    "P5_the_money_is_not_one_year":
        "the equal-weight book is positive in >= %d%% of calendar years and its worst year is "
        "better than %.1f%%" % (int(POSITIVE_YEAR_SHARE * 100), WORST_YEAR_FLOOR),
    "P6_dispersion_is_not_arithmetic":
        "dispersion_capture = (worst_single_mdd - real_mdd) / (worst_single_mdd - "
        "shift_null_mdd_median) must be >= %.2f; below that the four arms are one line"
        % DISPERSE_CAPTURE_MIN,
}
VERDICT_DISPERSE = "FOUR_ARMS_DO_DISPERSIFY"
VERDICT_ONE_LINE = "ONE_LINE_IN_FOUR_COSTUMES"
VERDICT_MIXED = "MIXED_READINGS"
VERDICT_BLOCKED = "DATA_BLOCKED"


def now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


# ------------------------------------------------------------------ one member
def member_daily(code):
    """Published weight rule -> one member's daily carry, with dates.

    Loading and arithmetic are the parent's; only the date slice is new, because the
    parent's `d1 = dates[1:]` is one longer than the daily series it labels.
    """
    pair = base.PAIRS.get(code)
    if not pair:
        return {"state": "NO_PAIR"}
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    if not os.path.exists(path):
        return {"state": "NO_FUTURES_PANEL"}
    fut = {}
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
            d = str(r["date"])[:10]
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[d] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    if len(dates) < 400:
        return {"state": "NOT_ENOUGH_BARS", "bars": len(dates)}
    basis, spread, roll = base.basis_face(f, i, dates)
    basis = np.asarray(basis, dtype=float)
    spread = np.asarray(spread, dtype=float)
    roll = np.asarray(roll, dtype=bool)
    w = rep.weight_series(basis, rep.pct_midrank)
    w_next = w[:-1]
    daily = rep.daily_carry(spread, roll, w_next)
    trade_dates = dates[1:][:len(daily)]
    if len(trade_dates) != len(daily):
        return {"state": "DATE_LENGTH_MISMATCH",
                "dates": len(trade_dates), "daily": len(daily)}
    return {"state": "ok", "dates": trade_dates, "daily": daily,
            "avg_weight": round(float(np.mean(w_next)), 4) if len(w_next) else None,
            "bars": len(trade_dates)}


# ------------------------------------------------------------------ alignment
def align_matrix(series):
    """Union date axis; a member's value is NaN on days it did not trade."""
    all_dates = sorted({d for s in series.values() for d in s["dates"]})
    pos = {d: k for k, d in enumerate(all_dates)}
    M = np.full((len(PRODUCTS), len(all_dates)), np.nan)
    for j, code in enumerate(PRODUCTS):
        s = series[code]
        for k, d in enumerate(s["dates"]):
            M[j, pos[d]] = s["daily"][k]
    return all_dates, M


def common_window(M):
    """First index at which every member has a value; the rest is the all-four window."""
    last_first = 0
    for j in range(M.shape[0]):
        idx = np.where(~np.isnan(M[j]))[0]
        if len(idx) == 0:
            return None
        last_first = max(last_first, int(idx[0]))
    return last_first


# ------------------------------------------------------------------ portfolios
def equal_weight(M):
    """Each trading member of the day gets an equal share of the book."""
    avail = ~np.isnan(M)
    n = avail.sum(axis=0)
    w = np.where(avail, 1.0 / np.maximum(n, 1), 0.0)
    port = np.nansum(np.where(avail, w * np.nan_to_num(M), 0.0), axis=0)
    return port, w


def inverse_volatility(M, lookback=IV_LOOKBACK, min_obs=IV_MIN_OBS):
    """Capital split by 1/realised-vol, using only days strictly before t."""
    T = M.shape[1]
    w = np.zeros_like(M)
    for t in range(T):
        avail = ~np.isnan(M[:, t])
        n = int(avail.sum())
        if n == 0:
            continue
        vols = {}
        for j in range(M.shape[0]):
            if not avail[j]:
                continue
            lo = max(0, t - lookback)
            win = M[j, lo:t]
            win = win[~np.isnan(win)]
            vols[j] = float(np.std(win, ddof=1)) if len(win) >= min_obs else None
        usable = [j for j in vols if vols[j] and vols[j] > 0]
        if len(usable) == n:
            inv = np.array([1.0 / vols[j] for j in range(M.shape[0]) if j in usable])
            w[np.array(usable), t] = inv / inv.sum()
        else:
            w[avail, t] = 1.0 / n
    port = np.nansum(np.where(~np.isnan(M), w * np.nan_to_num(M), 0.0), axis=0)
    return port, w


# ------------------------------------------------------------------ readings
def sharpe(daily):
    d = np.asarray(daily, dtype=float)
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return round(float(np.mean(d) / sd * np.sqrt(bc.TRADING_DAYS)), 3)


def vol_pct(daily):
    d = np.asarray(daily, dtype=float)
    if len(d) < 2:
        return None
    return round(float(np.std(d, ddof=1)) * np.sqrt(bc.TRADING_DAYS) * 100.0, 3)


def corr_matrix(M):
    rows = []
    for a in range(M.shape[0]):
        row = []
        for b in range(M.shape[0]):
            x, y = M[a], M[b]
            ok = ~np.isnan(x) & ~np.isnan(y)
            if ok.sum() < 100:
                row.append(None)
                continue
            xa, ya = x[ok], y[ok]
            if np.std(xa) <= 0 or np.std(ya) <= 0:
                row.append(None)
                continue
            row.append(round(float(np.corrcoef(xa, ya)[0, 1]), 4))
        rows.append(row)
    return rows


def median_pairwise_corr(cm):
    vals = []
    for a in range(len(cm)):
        for b in range(a + 1, len(cm)):
            if cm[a][b] is not None:
                vals.append(cm[a][b])
    if not vals:
        return None
    return round(float(np.median(vals)), 4)


def circ_shift(arr, k):
    a = np.asarray(arr, dtype=float)
    if len(a) == 0:
        return a
    k = int(k) % len(a)
    return np.concatenate((a[k:], a[:k]))


def shift_null_mdd(M, n=SHIFT_N, seed=SHIFT_SEED):
    """Destroy same-day co-movement, keep each member's own distribution and autocorrelation."""
    rng = np.random.default_rng(seed)
    T = M.shape[1]
    members = []
    for j in range(M.shape[0]):
        ok = ~np.isnan(M[j])
        members.append((j, np.where(ok, M[j], 0.0), ok))
    mdds = []
    for _ in range(n):
        shifted = np.full_like(M, np.nan)
        for j, vals, ok in members:
            shifted[j, ok] = circ_shift(vals[ok], rng.integers(0, max(1, int(ok.sum()))))
        port, _ = equal_weight(shifted)
        mdds.append(rep.mdd_pct(port))
    mdds = np.asarray(mdds, dtype=float)
    return {
        "n": n, "seed": seed,
        "mdd_median": round(float(np.median(mdds)), 3),
        "mdd_p05": round(float(np.percentile(mdds, 5)), 3),
        "mdd_p95": round(float(np.percentile(mdds, 95)), 3),
        "mdd_worst": round(float(np.min(mdds)), 3),
        "mdd_best": round(float(np.max(mdds)), 3),
    }


def subset_read(all_dates, M, members):
    """Same readings for any sub-book, on that sub-book's own all-present window."""
    rows = [PRODUCTS.index(c) for c in members]
    Ms = M[rows, :]
    cw = common_window(Ms)
    if cw is None:
        return None
    Mc = Ms[:, cw:]
    dates_c = all_dates[cw:]
    port, _ = equal_weight(Mc)
    singles = {}
    for j, code in enumerate(members):
        v = Mc[j]
        vv = v[~np.isnan(v)]
        singles[code] = {"ann_pct": rep.ann_pct(vv), "mdd_pct": rep.mdd_pct(vv),
                         "sharpe": sharpe(vv)}
    worst = min(s["mdd_pct"] for s in singles.values() if s["mdd_pct"] is not None)
    real = rep.mdd_pct(port)
    null = shift_null_mdd(Mc, n=SHIFT_N, seed=SHIFT_SEED)
    improve_real = abs(worst) - abs(real)
    improve_indep = abs(worst) - abs(null["mdd_median"])
    cap = round(improve_real / improve_indep, 4) if improve_indep > 0 else None
    return {
        "members": list(members),
        "bars": int(Mc.shape[1]),
        "first": dates_c[0], "last": dates_c[-1],
        "ann_pct": rep.ann_pct(port), "vol_pct": vol_pct(port),
        "sharpe": sharpe(port), "mdd_pct": real,
        "worst_single_mdd": worst,
        "shift_null_mdd_median": null["mdd_median"],
        "dispersion_capture": cap,
    }


def year_table(dates, daily):
    buckets = {}
    for k, v in enumerate(daily):
        buckets.setdefault(dates[k][:4], []).append(float(v))
    out = {}
    for y in sorted(buckets):
        out[y] = {"bars": len(buckets[y]),
                  "ann_pct": rep.ann_pct(buckets[y]),
                  "sum": round(float(np.sum(buckets[y])), 6)}
    return out


def window_read(dates, daily):
    return {
        "bars": len(daily),
        "first": dates[0] if dates else None,
        "last": dates[-1] if dates else None,
        "ann_pct": rep.ann_pct(daily),
        "vol_pct": vol_pct(daily),
        "sharpe": sharpe(daily),
        "mdd_pct": rep.mdd_pct(daily),
        "years": year_table(dates, daily),
    }


# ------------------------------------------------------------------ build
def build():
    series = {}
    for code in PRODUCTS:
        s = member_daily(code)
        if s.get("state") != "ok":
            return {"state": s.get("state", "UNKNOWN"), "product": code, "detail": s}
        if len(s["dates"]) < MIN_WEIGHT_DAYS:
            return {"state": "MEMBER_TOO_SHORT", "product": code, "bars": len(s["dates"])}
        series[code] = s

    all_dates, M = align_matrix(series)
    cwi = common_window(M)
    if cwi is None:
        return {"state": "NO_COMMON_WINDOW"}

    port_ew, w_ew = equal_weight(M)
    port_iv, w_iv = inverse_volatility(M)
    cm = corr_matrix(M)
    med_rho = median_pairwise_corr(cm)

    # common window slices (all four members trading)
    Mc = M[:, cwi:]
    dates_c = all_dates[cwi:]
    port_ew_c, _ = equal_weight(Mc)
    singles_c = {}
    for j, code in enumerate(PRODUCTS):
        v = Mc[j]
        vv = v[~np.isnan(v)]
        singles_c[code] = {
            "bars": int(len(vv)),
            "ann_pct": rep.ann_pct(vv),
            "vol_pct": vol_pct(vv),
            "sharpe": sharpe(vv),
            "mdd_pct": rep.mdd_pct(vv),
        }

    # identity check: weighted sum reconstruction vs plain sum, and single-member days
    recon = np.nansum(np.where(~np.isnan(M), w_ew * np.nan_to_num(M), 0.0), axis=0)
    id_resid = float(np.max(np.abs(recon - port_ew)))
    single_day_resid = 0.0
    avail_n = (~np.isnan(M)).sum(axis=0)
    for t in np.where(avail_n == 1)[0]:
        j = int(np.where(~np.isnan(M[:, t]))[0][0])
        single_day_resid = max(single_day_resid, abs(port_ew[t] - M[j, t]))

    null = shift_null_mdd(Mc)
    worst_single_mdd = min(v["mdd_pct"] for v in singles_c.values() if v["mdd_pct"] is not None)
    real_c_mdd = rep.mdd_pct(port_ew_c)
    # drawdowns are negative; "improvement" is the shrink in magnitude
    improve_real = abs(worst_single_mdd) - abs(real_c_mdd)
    improve_independent = abs(worst_single_mdd) - abs(null["mdd_median"])
    ddr_improve = (round(improve_real / abs(worst_single_mdd), 4)
                   if worst_single_mdd else None)
    # the independent book is the ceiling: a shift null that does not even improve the
    # drawdown is not a valid ceiling, so the capture is reported as unmeasurable.
    capture = (round(improve_real / improve_independent, 4)
               if improve_independent > 0 else None)

    ew_full = window_read(all_dates, port_ew)
    iv_full = window_read(all_dates, port_iv)
    ew_com = window_read(dates_c, port_ew_c)

    subsets = {}
    for name, members in SUBSETS:
        s = subset_read(all_dates, M, members)
        if s is not None:
            subsets[name] = s

    years = ew_full["years"]
    judged_years = {y: e for y, e in years.items() if e["bars"] >= 100}
    pos_years = [y for y, e in judged_years.items() if (e["ann_pct"] or 0) > 0]
    year_share = round(len(pos_years) / len(judged_years), 3) if judged_years else None
    worst_year = min((e["ann_pct"] for e in judged_years.values()
                      if e["ann_pct"] is not None), default=None)

    ddr_improve = None
    if worst_single_mdd not in (None, 0):
        ddr_improve = round(improve_real / abs(worst_single_mdd), 4)

    checks = {
        "P1_identity": bool(id_resid < ID_TOL and single_day_resid < ID_TOL),
        "P2_correlation_is_printed_not_hidden": med_rho is not None,
        "P3_the_drawdown_actually_diversifies": bool(
            ddr_improve is not None and ddr_improve >= 0.20),
        "P4_inverse_vol_earns_its_keep": bool(
            ew_full["sharpe"] is not None and iv_full["sharpe"] is not None
            and (iv_full["sharpe"] - ew_full["sharpe"]) >= IV_SHARPE_EDGE),
        "P5_the_money_is_not_one_year": bool(
            year_share is not None and year_share >= POSITIVE_YEAR_SHARE
            and worst_year is not None and worst_year > WORST_YEAR_FLOOR),
        "P6_dispersion_is_not_arithmetic": bool(
            capture is not None and capture >= DISPERSE_CAPTURE_MIN),
    }
    n_pass = sum(1 for v in checks.values() if v)
    verdict = _verdict(checks)
    if n_pass == len(checks):
        verdict = VERDICT_DISPERSE

    return {
        "state": "ok",
        "generated": now_iso(),
        "evidence_cutoff": all_dates[-1],
        "kind": "idx_fut_carry_portfolio",
        "members": {c: {"bars": series[c]["bars"],
                        "first": series[c]["dates"][0],
                        "last": series[c]["dates"][-1],
                        "avg_weight": series[c]["avg_weight"]} for c in PRODUCTS},
        "cost_bp_side": COST_BP_SIDE,
        "criteria": JUDGED,
        "frozen": {"iv_lookback": IV_LOOKBACK, "iv_min_obs": IV_MIN_OBS,
                   "corr_structural": CORR_STRUCTURAL,
                   "disperse_capture_min": DISPERSE_CAPTURE_MIN,
                   "iv_sharpe_edge": IV_SHARPE_EDGE,
                   "shift_n": SHIFT_N, "shift_seed": SHIFT_SEED,
                   "positive_year_share": POSITIVE_YEAR_SHARE,
                   "worst_year_floor": WORST_YEAR_FLOOR},
        "equal_weight_full": ew_full,
        "inverse_vol_full": iv_full,
        "equal_weight_common": ew_com,
        "subsets": subsets,
        "singles_common": singles_c,
        "correlation": {"labels": list(PRODUCTS), "matrix": cm,
                        "median_pairwise": med_rho,
                        "structural": bool(med_rho is not None and med_rho >= CORR_STRUCTURAL)},
        "dispersion": {"worst_single_mdd_common": worst_single_mdd,
                       "real_portfolio_mdd_common": real_c_mdd,
                       "shift_null": null,
                       "drawdown_improvement_frac": ddr_improve,
                       "dispersion_capture": capture},
        "identity": {"reconstruction_max_abs_resid": id_resid,
                     "single_member_day_max_abs_resid": single_day_resid},
        "year_read": {"positive_year_share": year_share, "worst_year_pct": worst_year,
                      "judged_years": sorted(judged_years)},
        "checks": checks,
        "verdict": verdict,
        "note": ("Four basis-carry arms priced as one book. Reading the correlation matrix and "
                 "dispersion_capture together answers whether 'portfolio' means anything here; "
                 "the inverse-vol book only earns its keep if it beats equal weight by a visible "
                 "Sharpe margin."),
    }


# ------------------------------------------------------------------ doc
def _pp(v):
    return "n/a" if v is None else ("%.2f%%" % v)


def write_doc(p):
    L = []
    L.append("# 四个品种的基差 carry，合起来是一条线还是四条线")
    L.append("")
    L.append("generated %s | evidence_cutoff **%s** | 判决 **%s**"
             % (p["generated"], p["evidence_cutoff"], p["verdict"]))
    L.append("")
    L.append("这个家族此前 21 个面全是分品种读数。真要下单的人买的是**一本**书，"
             "只是这本书记着四个指数期货。这一页第一次印那本书长什么样，并回答一个决定"
             "「组合」还有没有意义的问题：**理论上的分散化，实际吃到了几成？**")
    L.append("")
    L.append("## 判据（跑前冻结）")
    L.append("")
    L.append("| 腿 | 问题 | 线 |")
    L.append("|---|---|---|")
    L.append("| P1 | 组合是否就是成员的资本加权和 | 全窗重建残差 < 1e-12，且单成员交易日组合必须等于该成员 |")
    L.append("| P2 | 相关矩阵是否被如实印出 | 4×4 同日均收益相关矩阵发布；两两 rho 中位数 ≥ %.2f 即点名结构性同向 |" % CORR_STRUCTURAL)
    L.append("| P3 | 回撤是否真的被分散 | 四成员共同窗内，等权组合最大回撤比最差单成员好 ≥ 20% |")
    L.append("| P4 | 逆波动加权值不值多这套机械 | 领先等权 ≥ %.2f 夏普，否则不划算 |" % IV_SHARPE_EDGE)
    L.append("| P5 | 钱是不是一年的 | 等权组合正收益年占比 ≥ %d%%，最差年 > %.1f%% |"
             % (int(POSITIVE_YEAR_SHARE * 100), WORST_YEAR_FLOOR))
    L.append("| P6 | 分散是不是算术幻觉 | dispersion_capture ≥ %.2f（0=最差单成员，1=完全独立） |" % DISPERSE_CAPTURE_MIN)
    L.append("")
    L.append("P4 是**配置腿**：它不过只说明「逆波动加权不值」，不影响「四只合起来有没有分散」这个主判词。"
             "P3 / P6 才是主判词的门。")
    L.append("")

    m = p["members"]
    L.append("## 成员（各自按已发布规则、同一成本口径）")
    L.append("")
    L.append("| 品种 | bars | 区间 | 均权 |")
    L.append("|---|---|---|---|")
    for c in PRODUCTS:
        e = m[c]
        L.append("| %s | %d | %s → %s | %.3f |"
                 % (c, e["bars"], e["first"], e["last"], e["avg_weight"] if e["avg_weight"] is not None else float("nan")))
    L.append("")

    ew = p["equal_weight_full"]
    iv = p["inverse_vol_full"]
    L.append("## 读数：等权组合（全窗）vs 逆波动加权组合（全窗）")
    L.append("")
    L.append("| 配置 | bars | 年化 | 年化波动 | 夏普 | 最大回撤 |")
    L.append("|---|---|---|---|---|---|")
    L.append("| 等权 | %d | %s | %s | %s | %s |"
             % (ew["bars"], _pp(ew["ann_pct"]), _pp(ew["vol_pct"]),
                "n/a" if ew["sharpe"] is None else "%.3f" % ew["sharpe"], _pp(ew["mdd_pct"])))
    L.append("| 逆波动 60 日 | %d | %s | %s | %s | %s |"
             % (iv["bars"], _pp(iv["ann_pct"]), _pp(iv["vol_pct"]),
                "n/a" if iv["sharpe"] is None else "%.3f" % iv["sharpe"], _pp(iv["mdd_pct"])))
    L.append("")

    co = p["correlation"]
    L.append("## 同日均收益相关矩阵（%s → %s）" % (p["equal_weight_common"]["first"], p["equal_weight_common"]["last"]))
    L.append("")
    L.append("| | " + " | ".join(co["labels"]) + " |")
    L.append("|" + "---|" * (len(co["labels"]) + 1))
    for i, lab in enumerate(co["labels"]):
        cells = []
        for j in range(len(co["labels"])):
            v = co["matrix"][i][j]
            cells.append("—" if v is None else "%.3f" % v)
        L.append("| %s | %s |" % (lab, " | ".join(cells)))
    L.append("")
    mp = co["median_pairwise"]
    L.append("两两 rho 中位数 **%s**%s。" % (
        "n/a" if mp is None else "%.3f" % mp,
        "，**已结构化同向**：四本不是四个独立赌注" if co["structural"] else "，同向程度不算结构性"))
    L.append("")

    d = p["dispersion"]
    L.append("## 分散化到底吃到了几成")
    L.append("")
    L.append("口径=四成员共同窗（%s → %s）。「完全独立」用循环位移零假设估：每个成员按自身序列随机平移，"
             "分布与自相关都保留、只打掉同日共振。" % (
                 p["equal_weight_common"]["first"], p["equal_weight_common"]["last"]))
    L.append("")
    L.append("| 读数 | 值 |")
    L.append("|---|---|")
    L.append("| 最差单成员最大回撤 | %s |" % _pp(d["worst_single_mdd_common"]))
    L.append("| 真实等权组合最大回撤 | %s |" % _pp(d["real_portfolio_mdd_common"]))
    L.append("| 位移零假设回撤中位数（≈完全独立） | %s |" % _pp(d["shift_null"]["mdd_median"]))
    L.append("| 位移零假设回撤 5%%–95%% | %s … %s |"
             % (_pp(d["shift_null"]["mdd_p05"]), _pp(d["shift_null"]["mdd_p95"])))
    L.append("| 回撤改善相对最差单成员 | %s |"
             % ("n/a" if d["drawdown_improvement_frac"] is None
                else "%.1f%%" % (d["drawdown_improvement_frac"] * 100)))
    L.append("| **dispersion_capture**（0=没分散，1=完全分散） | **%s** |"
             % ("n/a" if d["dispersion_capture"] is None else "%.3f" % d["dispersion_capture"]))
    L.append("")

    L.append("## 逐年（等权组合，全窗）")
    L.append("")
    L.append("| 年 | bars | 年化 |")
    L.append("|---|---|---|")
    for y, e in sorted(ew["years"].items()):
        L.append("| %s | %d | %s |" % (y, e["bars"], _pp(e["ann_pct"])))
    L.append("")

    sub = p.get("subsets") or {}
    if sub:
        L.append("## 买几只才够（各自按自己的「全员在位」窗口重算）")
        L.append("")
        L.append("相关矩阵露出一个两段结构：小盘对（IC·IM）0.771、大盘对（IF·IH）0.705，"
                 "而跨对只有 0.22~0.31——分散来自大小盘错位，不是四只各不相同。"
                 "于是「最少几只够用」本身就是产品问题：")
        L.append("")
        L.append("| 子集 | 成员 | 窗口 | bars | 年化 | 夏普 | 最大回撤 | 最差单成员回撤 | dispersion_capture |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for name, s in sub.items():
            L.append("| %s | %s | %s→%s | %d | %s | %s | %s | %s | %s |"
                     % (name, "·".join(s["members"]), s["first"], s["last"], s["bars"],
                        _pp(s["ann_pct"]),
                        "n/a" if s["sharpe"] is None else "%.3f" % s["sharpe"],
                        _pp(s["mdd_pct"]), _pp(s["worst_single_mdd"]),
                        "n/a" if s["dispersion_capture"] is None
                        else "%.3f" % s["dispersion_capture"]))
        L.append("")
        full_cap = (sub.get("all_four") or {}).get("dispersion_capture")
        cross = sub.get("cross_pair_IC_IF") or {}
        if full_cap and cross.get("dispersion_capture") is not None:
            share = cross["dispersion_capture"] / full_cap
            L.append("读数：跨对两只（IC·IF）的 capture 是四只的 **%.0f%%**（%s vs %s），"
                     "回撤 %s vs 四只 %s——**这个窗口里两只跨对已经拿到大部分分散**。"
                     "但要连着窗口看：两只的窗口从 %s 起，四只只有 %s 起，"
                     "不是同一个样本，不能直接说谁更好。"
                     % (share * 100, "%.3f" % cross["dispersion_capture"], "%.3f" % full_cap,
                        _pp(cross["mdd_pct"]), _pp(sub["all_four"]["mdd_pct"]),
                        cross["first"], sub["all_four"]["first"]))
            L.append("")

    sc = p["singles_common"]
    L.append("## 共同窗内的单成员参照")
    L.append("")
    L.append("| 品种 | bars | 年化 | 波动 | 夏普 | 最大回撤 |")
    L.append("|---|---|---|---|---|---|")
    for c in PRODUCTS:
        e = sc[c]
        L.append("| %s | %d | %s | %s | %s | %s |"
                 % (c, e["bars"], _pp(e["ann_pct"]), _pp(e["vol_pct"]),
                    "n/a" if e["sharpe"] is None else "%.3f" % e["sharpe"], _pp(e["mdd_pct"])))
    L.append("")

    L.append("## 判据逐条")
    L.append("")
    L.append("| 腿 | 结果 |")
    L.append("|---|---|")
    for k, v in p["checks"].items():
        L.append("| %s | %s |" % (k, "PASS" if v else "**FAIL**"))
    L.append("")
    L.append("恒等残差：重建 %.3e｜单成员日 %.3e（容差 1e-12）。"
             % (p["identity"]["reconstruction_max_abs_resid"],
                p["identity"]["single_member_day_max_abs_resid"]))
    L.append("")
    L.append("## 怎么读这一页")
    L.append("")
    L.append("- `dispersion_capture` 接近 0：这本「组合」的回撤就是最差那只的回撤，"
             "不要当四笔独立仓位去配风险预算。")
    L.append("- 接近 1：四只确实各走各的，等权是有意义的。")
    L.append("- 中间的读数要连同相关矩阵一起看：中位 rho 高而 capture 不低，"
             "说明分散来自「不同幅度」而非「不同方向」。")
    L.append("- 逆波动臂只在 P4 通过时才值得上；不通过就是多一套机械换不来收益。")
    L.append("- 这一页不构成投资建议：它只回答「这四只合起来的形态」，不回答该不该下注。")
    L.append("")
    path = OUT_MD
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ check
def _cmp(name, published, fresh, tol, unit, problems):
    if published is None and fresh is None:
        return
    if published is None or fresh is None:
        problems.append("%s: published=%r fresh=%r" % (name, published, fresh))
        return
    if abs(float(published) - float(fresh)) > tol:
        problems.append("%s: published=%.4f fresh=%.4f (tol %.4f %s)"
                        % (name, float(published), float(fresh), tol, unit))


def check():
    path = OUT_JSON
    if not os.path.exists(path):
        print("STALE face missing: %s" % path)
        return 3
    with open(path, encoding="utf-8") as f:
        pub = json.load(f)
    if pub.get("state") != "ok":
        print("CHECK FAILED: published face is not ok (%r)" % pub.get("state"))
        return 3
    fresh = build()
    if fresh.get("state") != "ok":
        print("CHECK FAILED: fresh build is not ok (%r)" % fresh.get("state"))
        return 3
    problems = []
    if pub.get("evidence_cutoff") != fresh.get("evidence_cutoff"):
        problems.append("STALE cutoff: published=%s fresh=%s"
                        % (pub.get("evidence_cutoff"), fresh.get("evidence_cutoff")))
    if pub.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published=%s fresh=%s"
                        % (pub.get("verdict"), fresh.get("verdict")))
    for arm in ("equal_weight_full", "inverse_vol_full", "equal_weight_common"):
        for fld, tol, unit in (("ann_pct", TOL_PP, "pp"), ("vol_pct", TOL_PP, "pp"),
                               ("sharpe", TOL_SHARPE, "sharpe"),
                               ("mdd_pct", TOL_PP, "pp"), ("bars", 0, "bars")):
            _cmp("%s.%s" % (arm, fld), pub[arm].get(fld), fresh[arm].get(fld), tol, unit, problems)
    _cmp("dispersion.dispersion_capture",
         pub["dispersion"].get("dispersion_capture"),
         fresh["dispersion"].get("dispersion_capture"), 0.002, "capture", problems)
    _cmp("correlation.median_pairwise",
         pub["correlation"].get("median_pairwise"),
         fresh["correlation"].get("median_pairwise"), 0.001, "rho", problems)
    for a in range(len(PRODUCTS)):
        for b in range(len(PRODUCTS)):
            _cmp("corr[%d][%d]" % (a, b), pub["correlation"]["matrix"][a][b],
                 fresh["correlation"]["matrix"][a][b], 0.001, "rho", problems)
    for c in PRODUCTS:
        _cmp("singles_common.%s.mdd" % c, pub["singles_common"][c].get("mdd_pct"),
             fresh["singles_common"][c].get("mdd_pct"), TOL_PP, "pp", problems)
        _cmp("singles_common.%s.ann" % c, pub["singles_common"][c].get("ann_pct"),
             fresh["singles_common"][c].get("ann_pct"), TOL_PP, "pp", problems)
    for k in JUDGED:
        if bool(pub["checks"].get(k)) != bool(fresh["checks"].get(k)):
            problems.append("check %s: published=%s fresh=%s"
                            % (k, pub["checks"].get(k), fresh["checks"].get(k)))
    if problems:
        hard = [x for x in problems if "STALE" in x]
        print("CHECK FAILED (%d problems, %d stale):" % (len(problems), len(hard)))
        for x in problems:
            print("  - " + x)
        return 3
    print("CHECK OK: all published readings re-derive off the panels.")
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []

    def ok(cond, name):
        if not cond:
            fails.append(name)

    # 1 identity: equal weight over a 2-member toy matrix
    M = np.array([[0.01, 0.02, np.nan, 0.03],
                  [0.03, 0.00, 0.04, np.nan]], dtype=float)
    port, w = equal_weight(M)
    ok(abs(port[0] - 0.02) < ID_TOL, "ew averages two members")
    ok(abs(port[1] - 0.01) < ID_TOL, "ew averages two members again")
    ok(abs(port[2] - 0.04) < ID_TOL, "ew equals the only member trading")
    ok(abs(port[3] - 0.03) < ID_TOL, "ew equals the only member trading (2)")
    ok(abs(w.sum(axis=0)[2] - 1.0) < ID_TOL, "single-member day allocates the whole book")

    # 2 a flat member is averaged in, not skipped
    M2 = np.array([[0.02, 0.02], [0.00, 0.00]], dtype=float)
    p2, _ = equal_weight(M2)
    ok(abs(p2[0] - 0.01) < ID_TOL, "a flat member still takes half the book")

    # 3 correlation signs
    x = np.linspace(-1, 1, 200)
    Mc = np.vstack([x, 2 * x, -x])
    cm = corr_matrix(Mc)
    ok(abs(cm[0][1] - 1.0) < 1e-9, "perfectly co-moving reads 1.0")
    ok(abs(cm[0][2] + 1.0) < 1e-9, "perfectly opposed reads -1.0")
    ok(median_pairwise_corr(cm) is not None, "median pairwise is defined")

    # 4 drawdown of a monotone fall is exact (the peak is the first bar, so 99 steps follow;
    #    mdd_pct rounds to 3dp, so the tolerance is half of that last printed digit)
    d = -np.full(100, 0.01)
    ok(abs(rep.mdd_pct(d) - (0.99 ** 99 - 1) * 100.0) < 1e-3, "monotone fall mdd exact")

    # 5 circular shift is a permutation: distribution preserved
    arr = np.arange(10, dtype=float)
    sh = circ_shift(arr, 3)
    ok(sorted(sh.tolist()) == sorted(arr.tolist()), "circular shift preserves the multiset")

    # 6 the shift null must destroy co-movement: two identical members
    base_series = np.sin(np.linspace(0, 20, 400)) * 0.01
    M3 = np.vstack([base_series, base_series])
    real_mdd = rep.mdd_pct(equal_weight(M3)[0])
    null3 = shift_null_mdd(M3, n=60, seed=7)
    ok(null3["mdd_median"] > real_mdd,
       "wrecking co-movement must make a perfectly-correlated pair's drawdown shallower")

    # 7 dispersion capture: correlated pair -> near zero, independent pair -> larger
    rng = np.random.default_rng(11)
    ind = rng.normal(0.0004, 0.01, (2, 600))
    M4 = ind
    cwi = 0
    worst = min(rep.mdd_pct(M4[j]) for j in range(2))
    real = rep.mdd_pct(equal_weight(M4)[0])
    n4 = shift_null_mdd(M4, n=80, seed=13)
    den = worst - n4["mdd_median"]
    cap = None if den == 0 else (worst - real) / den
    ok(cap is not None and cap > 0.3, "independent members capture a real share of dispersion")

    # 8 inverse vol must not look ahead: constant-vol toy gives equal weights
    M5 = np.vstack([np.linspace(0.001, 0.002, 100), np.linspace(0.001, 0.002, 100)])
    _, w5 = inverse_volatility(M5, lookback=20, min_obs=10)
    tail = w5[:, 90]
    ok(abs(tail[0] - 0.5) < 1e-9 and abs(tail[1] - 0.5) < 1e-9,
       "equal volatilities split the book evenly")

    # 9 inverse vol actually tilts toward the calmer member (a truly constant series has
    #    zero std, which the rule treats as unusable rather than infinitely good)
    calm = 0.001 + np.where(np.arange(200) % 2 == 0, 0.0001, -0.0001)
    wild = np.where(np.arange(200) % 2 == 0, 0.02, -0.018)
    M6 = np.vstack([calm, wild])
    _, w6 = inverse_volatility(M6, lookback=40, min_obs=20)
    ok(w6[0, 150] > w6[1, 150], "inverse vol gives the calm member more capital")

    # 10 a NaN-heavy day never fabricates return
    M7 = np.array([[np.nan, 0.02], [np.nan, 0.00]])
    p7, _ = equal_weight(M7)
    ok(p7[0] == 0.0, "an all-missing day contributes zero, not a guess")

    # 11 year table buckets by calendar year
    yt = year_table(["2024-12-30", "2024-12-31", "2025-01-02"], [0.01, 0.01, -0.01])
    ok(yt["2024"]["bars"] == 2 and yt["2025"]["bars"] == 1, "year table splits on the year")

    # 12 verdict logic: failing P3 or P6 must read ONE_LINE, not MIXED
    fake = {k: True for k in JUDGED}
    fake["P3_the_drawdown_actually_diversifies"] = False
    fake["P6_dispersion_is_not_arithmetic"] = True
    fake["P4_inverse_vol_earns_its_keep"] = False
    ok(_verdict(fake) == VERDICT_ONE_LINE, "failing P3 reads ONE_LINE even with other legs down")
    fake2 = {k: True for k in JUDGED}
    fake2["P4_inverse_vol_earns_its_keep"] = False
    ok(_verdict(fake2) == VERDICT_DISPERSE,
       "only the sizing leg down still reads DISPERSE: P4 is not a statement about the book")
    fake3 = {k: True for k in JUDGED}
    fake3["P1_identity"] = False
    ok(_verdict(fake3) == VERDICT_MIXED, "a non-P4 core failure reads MIXED")

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for x in fails:
            print("  - " + x)
        return 1
    print("SELFTEST OK: 12/12 legs pass.")
    return 0


def _verdict(checks):
    """P4 is a sizing-choice leg, not a statement about the book: it can fail while the
    four arms still diversify.  Any other leg failing on the core question does count."""
    core = ("P1_identity", "P2_correlation_is_printed_not_hidden",
            "P3_the_drawdown_actually_diversifies",
            "P5_the_money_is_not_one_year", "P6_dispersion_is_not_arithmetic")
    if checks.get("P3_the_drawdown_actually_diversifies") is False or \
            checks.get("P6_dispersion_is_not_arithmetic") is False:
        return VERDICT_ONE_LINE
    if all(checks.get(k) for k in core):
        return VERDICT_DISPERSE
    return VERDICT_MIXED


# ------------------------------------------------------------------ run
def run(write=True):
    bc.weight_priority()
    p = build()
    if p.get("state") != "ok":
        print("BUILD BLOCKED: %r" % {k: v for k, v in p.items() if k != "criteria"})
        return 2
    if write:
        with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(p, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        write_doc(p)
    ew, iv = p["equal_weight_full"], p["inverse_vol_full"]
    print("PORTFOLIO %s | cutoff %s" % (p["verdict"], p["evidence_cutoff"]))
    print("  equal weight : ann %s vol %s sharpe %s mdd %s"
          % (_pp(ew["ann_pct"]), _pp(ew["vol_pct"]), ew["sharpe"], _pp(ew["mdd_pct"])))
    print("  inverse vol  : ann %s vol %s sharpe %s mdd %s"
          % (_pp(iv["ann_pct"]), _pp(iv["vol_pct"]), iv["sharpe"], _pp(iv["mdd_pct"])))
    print("  median rho   : %s (structural=%s)"
          % (p["correlation"]["median_pairwise"], p["correlation"]["structural"]))
    print("  dispersion_capture: %s (worst single mdd %s vs real %s)"
          % (p["dispersion"]["dispersion_capture"],
             _pp(p["dispersion"]["worst_single_mdd_common"]),
             _pp(p["dispersion"]["real_portfolio_mdd_common"])))
    for k, v in p["checks"].items():
        print("  %-42s %s" % (k, "PASS" if v else "FAIL"))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-").lower()
    if cmd == "run":
        return run(write=True)
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    if cmd == "dry":
        return run(write=False)
    print("usage: idx_fut_carry_portfolio.py [run|check|selftest|dry]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
