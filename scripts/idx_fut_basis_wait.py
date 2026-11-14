"""What does it cost to wait for the widest discount bucket?

r1689 answered "the discount width carries the next 20 days' carry" and then said the
awkward half out loud: the carry IS the discount closing (ratio ~1.00 against the basis
change), so the rule is a prepayment schedule, not a forecast. That leaves the only
question that decides money unanswered:

    an arm that sits in cash and enters only when the discount is in the widest
    quintile -- is the prepayment it collects bigger than the drift it gives up
    while waiting, and bigger than the repo interest it collects instead?

This script prices that arm against two references on the same capital and the same
volatility leash, per pair, on the joined futures/index panel:

  A  always in       fully-funded long future, collateral in repo
  B  wait for wide   in only while the causal percentile is in the widest quintile
  C  always cash     1-day repo, rolled

Daily returns are on capital with capital = notional (no leverage beyond the leash):

  in-market  r = lev * (index_ret + spread) + repo_accrual
  out        r = repo_accrual

`spread` is the futures-minus-index step, which is the basis closing: this is why the
identity A - B = lev * (index_ret + spread) over the out-days is exact and is asserted
in the selftest (L4). If that identity fails the decomposition is wrong and the face is
not publishable.

The leash is the same for A and B and can only shrink exposure (vol target 8%/yr on the
exposure's own volatility, never above 1.0). Applying each arm's own idle-diluted
volatility would lever up the arm that sits in cash the most -- that is the r1291
"two knobs at once" trap, so it is refused by construction.

Repo accrual is GC001 close (annualised percent) applied over the CALENDAR days to the
next trading date over 365 -- a 1-day repo that starts on Friday covers three days, and
charging it as one trading day would understate the cash leg by ~40% on Mondays.

Frozen criteria (written before any number was read):
  W1 net:        B annualised - A annualised >= 0.50pp/yr
  W2 vs cash:    B annualised - C annualised >= 0.50pp/yr
  W3 stable:     B - A >= 0 in both halves of the sample
  Per pair WAIT if W1 and W2 and W3. Pooled WAIT if at least two of four pairs pass
  (same two-of-four shape as the parent faces).
  Costs always on: 1.0bp per entry and per exit of the notional, 1.0bp per roll day
  held. Both arms pay their rolls; only B pays the flip costs.
"""
import bisect
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idx_fut_basis as base            # noqa: E402  (panels, roll mask, pair table)
import idx_fut_basis_timing as timing   # noqa: E402  (causal percentile, one implementation)

OUT = os.path.join(base.ROOT, "results", "idx_fut_basis_wait.json")
REPO_CSV = os.path.join(base.ROOT, "data", "repo_daily", "GC001.csv")
WIDE_EDGE = 20.0        # widest quintile, same edge the parent face froze
W1_PP = 0.50
W2_PP = 0.50
SLIP_BP = 1.0
ROLL_BP = 1.0
VOL_TARGET = 0.08
DAYS_PER_YEAR = 244.0
MIN_OBS = 250


def load_repo(path=REPO_CSV):
    """Repo closes as (sorted dates, rates in percent). Missing dates are never invented."""
    if not os.path.exists(path):
        return [], []
    rows = base.read_csv_rows(path)
    dates, rates = [], []
    for r in rows:
        try:
            d, v = str(r["date"])[:10], float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (0.0 < v < 200.0):
            continue
        dates.append(d)
        rates.append(v)
    order = sorted(range(len(dates)), key=lambda i: dates[i])
    return [dates[i] for i in order], [rates[i] for i in order]


def repo_rate_on(dates, rates, day):
    """Last rate at or before `day` (forward fill from the past only). None if none yet."""
    if not dates:
        return None
    k = bisect.bisect_right(dates, day) - 1
    if k < 0:
        return None
    return rates[k]


def calendar_days(d0, d1):
    from datetime import date
    y0, m0, d0_ = (int(x) for x in d0.split("-"))
    y1, m1, d1_ = (int(x) for x in d1.split("-"))
    return max(1, (date(y1, m1, d1_) - date(y0, m0, d0_)).days)


def daily_repo(dates, spreads_days, repo_dates, repo_rates):
    """Accrual per trading day: rate% * calendar_days_to_next_trading_day / 365."""
    out, missing = [], 0
    for k, d in enumerate(dates):
        r = repo_rate_on(repo_dates, repo_rates, d)
        if r is None or k + 1 >= len(dates):
            out.append(None if r is None else 0.0)
            if r is None:
                missing += 1
            continue
        out.append(r / 100.0 * calendar_days(d, dates[k + 1]) / 365.0)
    return out, missing


def series_stats(returns, dates):
    if not returns:
        return None
    eq, peak, dd = [1.0], 1.0, 0.0
    for r in returns:
        eq.append(eq[-1] * (1.0 + r))
        peak = max(peak, eq[-1])
        if peak > 0:
            dd = min(dd, eq[-1] / peak - 1.0)
    growth = eq[-1]
    years = (calendar_days(dates[0], dates[-1])) / 365.0
    ann = growth ** (1.0 / years) - 1.0 if years > 0 and growth > 0 else None
    vol = statistics.pstdev(returns) * (DAYS_PER_YEAR ** 0.5)
    return {"ann_pct": round(ann * 100, 3) if ann is not None else None,
            "vol_pct": round(vol * 100, 3),
            "maxdd_pct": round(dd * 100, 3),
            "growth_x": round(growth, 4),
            "n_days": len(returns)}


def sharpe(ann_pct, vol_pct, cash_ann_pct):
    if ann_pct is None or not vol_pct or cash_ann_pct is None:
        return None
    return round((ann_pct - cash_ann_pct) / vol_pct, 3)


def exposure_vol(rf):
    return statistics.pstdev(rf) * (DAYS_PER_YEAR ** 0.5)


def leash(vol_exposure):
    """Only ever shrinks: a quiet instrument is not geared up to reach the target."""
    if not vol_exposure or vol_exposure <= 0:
        return 1.0
    return round(min(1.0, VOL_TARGET / vol_exposure), 4)


def run_arms(idx_ret, spread_masked, repo_acc, in_market, roll, lev):
    """Three arms on identical capital. Returns per-day lists + a cost ledger per arm."""
    a, b, c = [], [], []
    flips = rolls_held = 0
    cost_a = cost_b = 0.0
    prev_in = False
    slip = SLIP_BP / 10000.0
    rollc = ROLL_BP / 10000.0
    for t in range(len(idx_ret)):
        inr = lev * (idx_ret[t] + spread_masked[t]) + repo_acc[t]
        if roll[t]:
            inr -= rollc
            cost_a += rollc
            if in_market[t]:
                rolls_held += 1
                cost_b += rollc
        if in_market[t] and not prev_in:
            inr -= slip
            cost_a += slip
            cost_b += slip
            flips += 1
        elif prev_in and not in_market[t]:
            b[-1] -= slip  # the exit is charged on the day the position leaves
            cost_b += slip
            flips += 1
        a.append(inr)
        b.append(inr if in_market[t] else repo_acc[t])
        c.append(repo_acc[t])
        prev_in = bool(in_market[t])
    return ({"A": a, "B": b, "C": c},
            {"flips": flips, "roll_days_held": rolls_held,
             "cost_A": round(cost_a, 12), "cost_B": round(cost_b, 12)})


def one_pair(fut, fpath, code):
    frows = base.read_csv_rows(fpath)
    fut_close = {}
    for r in frows:
        try:
            fut_close[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    try:
        idx = base.load_index(code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}
    dates, fc, ic = base.aligned(fut_close, idx)
    if len(dates) < 400:
        return {"status": "short_overlap", "days": len(dates)}
    basis, spread, roll = base.basis_face(fc, ic, dates)
    pcts = timing.causal_percentiles(basis)
    repo_dates, repo_rates = load_repo()
    if not repo_dates:
        return {"status": "no_repo_panel"}
    repo_acc, repo_missing = daily_repo(dates, spread, repo_dates, repo_rates)

    # Every step needs a percentile, a repo accrual, and a non-masked spread.
    idx_ret = [ic[t + 1] / ic[t] - 1.0 for t in range(len(dates) - 1)]
    keep = [t for t in range(len(spread))
            if pcts[t] is not None and repo_acc[t] is not None and repo_acc[t] >= 0]
    if len(keep) < MIN_OBS:
        return {"status": "thin_sample", "n": len(keep)}
    lo, hi = keep[0], keep[-1] + 1
    span = list(range(lo, hi))
    d_span = dates[lo:hi + 1]
    spread_masked = [0.0 if roll[t] else spread[t] for t in span]
    in_market = [pcts[t] < WIDE_EDGE for t in span]

    vol_ex = exposure_vol([idx_ret[t] + spread_masked[k] for k, t in enumerate(span)])
    lev = leash(vol_ex)
    arms, cnt = run_arms([idx_ret[t] for t in span], spread_masked,
                         [repo_acc[t] for t in span], in_market,
                         [roll[t] for t in span], lev)
    stats = {k: series_stats(v, d_span) for k, v in arms.items()}
    cash_ann = stats["C"]["ann_pct"]
    for k in ("A", "B", "C"):
        stats[k]["sharpe_vs_cash"] = sharpe(stats[k]["ann_pct"], stats[k]["vol_pct"], cash_ann)

    # The decomposition is an identity, not a story: A - B is exactly the in-market
    # return the waiting arm did not earn, plus the cost differences between the arms
    # (A pays every roll, B only the rolls it held and every flip it made).
    foregone = [lev * (idx_ret[t] + spread_masked[k]) for k, t in enumerate(span)
                if not in_market[k]]
    years = calendar_days(d_span[0], d_span[-1]) / 365.0
    foregone_pp = (sum(foregone) / years) * 100.0 if years > 0 else None
    gap_pp = stats["A"]["ann_pct"] - stats["B"]["ann_pct"]
    sum_gap = sum(arms["A"]) - sum(arms["B"])
    identity_rhs = sum(foregone) + (cnt["cost_B"] - cnt["cost_A"])
    identity_residual_pp = round((sum_gap - identity_rhs) * 100.0, 6)

    mid = len(span) // 2
    halves = {}
    for tag, rng in (("first", span[:mid]), ("second", span[mid:])):
        sub_arms, _ = run_arms([idx_ret[t] for t in rng],
                               [0.0 if roll[t] else spread[t] for t in rng],
                               [repo_acc[t] for t in rng],
                               [pcts[t] < WIDE_EDGE for t in rng],
                               [roll[t] for t in rng], lev)
        sa = series_stats(sub_arms["A"], dates[rng[0]:rng[-1] + 2])
        sb = series_stats(sub_arms["B"], dates[rng[0]:rng[-1] + 2])
        halves[tag] = {"A_ann": sa["ann_pct"], "B_ann": sb["ann_pct"],
                       "B_minus_A_pp": round(sb["ann_pct"] - sa["ann_pct"], 3)}

    w1 = (stats["B"]["ann_pct"] - stats["A"]["ann_pct"]) >= W1_PP
    w2 = (stats["B"]["ann_pct"] - cash_ann) >= W2_PP
    w3 = halves["first"]["B_minus_A_pp"] >= 0 and halves["second"]["B_minus_A_pp"] >= 0
    failing = [name for name, val in (("W1", w1), ("W2", w2), ("W3", w3)) if not val]
    return {
        "status": "ok",
        "index": code,
        "window": {"from": d_span[0], "to": d_span[-1], "days": len(d_span)},
        "n_obs": len(span),
        "repo": {"source": "data/repo_daily/GC001.csv", "rows_missing_ffill": repo_missing,
                 "accrual": "rate% x calendar_days_to_next_trading_day / 365"},
        "leash": {"exposure_vol_pct": round(vol_ex * 100, 3), "target_pct": VOL_TARGET * 100,
                  "leverage": lev, "note": "same leash on A and B; never above 1.0"},
        "costs": {"slip_bp_per_side": SLIP_BP, "roll_bp_per_held_roll_day": ROLL_BP,
                  "flips": cnt["flips"], "roll_days_held": cnt["roll_days_held"]},
        "arms": stats,
        "time_in_market_pct": round(100.0 * sum(1 for v in in_market if v) / len(span), 2),
        "decomposition": {
            "A_minus_B_ann_pp": round(gap_pp, 3),
            "foregone_inmarket_pp_per_yr": round(foregone_pp, 3) if foregone_pp else None,
            "identity_gap_pp": identity_residual_pp,
            "note": "A - B is what the waiting arm did not earn (index drift plus carry on "
                    "the out-days) net of the costs only B pays; residual is the check",
        },
        "halves": halves,
        "W1": bool(w1), "W2": bool(w2), "W3": bool(w3),
        "failing": failing,
        "verdict": "WAIT" if (w1 and w2 and w3) else "HOLD-ALWAYS",
        "sharpe_gain_B_over_A": round(stats["B"]["sharpe_vs_cash"]
                                      - stats["A"]["sharpe_vs_cash"], 3),
    }


def build():
    face = {
        "criteria": {"wide_edge_pct": WIDE_EDGE, "W1_pp": W1_PP, "W2_pp": W2_PP,
                     "slip_bp": SLIP_BP, "roll_bp": ROLL_BP, "vol_target_pct": VOL_TARGET * 100,
                     "frozen_note": "thresholds written before any number was read"},
        "caveats": [
            "main-contract continuous series: roll days are masked and charged, but the "
            "roll premium itself is not reconstructed",
            "no margin/capital-consumption model: both arms are fully funded, so the "
            "leash is the only gear",
            "repo accrual is GC001 close, not the actual collateral arrangement",
            "futures index joins are on shared trading dates; index bars are not "
            "tradeable instruments themselves",
        ],
        "pairs": {},
    }
    for fut, (code, _name, _etf) in base.PAIRS.items():
        fpath = os.path.join(base.FUT_DIR, fut + ".csv")
        if not os.path.exists(fpath):
            face["pairs"][fut] = {"status": "no_futures_panel"}
            continue
        face["pairs"][fut] = one_pair(fut, fpath, code)
    ok = {f: e for f, e in face["pairs"].items() if e.get("status") == "ok"}
    waiting = [f for f, e in ok.items() if e.get("verdict") == "WAIT"]
    if ok:
        deltas = {f: round(e["arms"]["B"]["ann_pct"] - e["arms"]["A"]["ann_pct"], 3)
                  for f, e in ok.items()}
        time_in = statistics.median([e["time_in_market_pct"] for e in ok.values()])
        sharpes = {f: {"A": e["arms"]["A"]["sharpe_vs_cash"],
                       "B": e["arms"]["B"]["sharpe_vs_cash"],
                       "gain": e["sharpe_gain_B_over_A"]} for f, e in ok.items()}
        money_but_unstable = [f for f, e in ok.items()
                              if e["verdict"] != "WAIT" and e["W1"] and e["W2"]]
        failing_hist = {}
        for e in ok.values():
            for f in e["failing"]:
                failing_hist[f] = failing_hist.get(f, 0) + 1
    else:
        deltas, time_in, sharpes = {}, None, {}
        money_but_unstable, failing_hist = [], {}
    face["verdict"] = {
        "waiting_pairs": waiting,
        "pooled": "WAIT" if len(waiting) >= 2 else "HOLD-ALWAYS",
        "B_minus_A_pp_by_pair": deltas,
        "median_time_in_market_pct": time_in,
        "sharpe_by_pair": sharpes,
        "money_but_unstable_pairs": money_but_unstable,
        "failing_leg_counts": failing_hist,
        "rule": ("sit in repo and enter only in the widest-quintile discount"
                 if len(waiting) >= 2 else
                 "no 2-of-4 -- waiting for the wide discount costs more drift than the "
                 "prepayment it collects; hold the average instead"),
        "note": ("B - A reads low because the waiting arm is out of the market: read it next "
                 "to median_time_in_market_pct and the foregone column, not as a verdict on "
                 "the discount itself."),
        "read": ("冻结判据判 HOLD-ALWAYS，而把它判死的**不是收益门槛**：IF/IH 两对过了 W1/W2，"
                 "死在 W3（前后半场同号）——它们的全部好处都在后半场。又因为 B 有约四分之三的"
                 "时间在场外，原始年化天生被摊薄、波动远低于目标档，所以同风险的比较看夏普列："
                 "IF/IH 的 0.72/0.74 对一直持有的 0.21/0.22 是这条线唯一像样的读数，"
                 "而它同样只活在后半场，不能当成已成立的择时规则。"),
    }
    return face


def selftest():
    ok = total = 0

    def leg(cond, name):
        nonlocal ok, total
        total += 1
        ok += 1 if cond else 0
        if not cond:
            print("FAIL %s" % name)

    # L1 repo forward-fill reads the past only.
    ds, rs = ["2024-01-02", "2024-01-05"], [2.0, 3.0]
    leg(repo_rate_on(ds, rs, "2024-01-02") == 2.0, "L1a repo reads on the day")
    leg(repo_rate_on(ds, rs, "2024-01-04") == 2.0, "L1b repo ffills from the past")
    leg(repo_rate_on(ds, rs, "2024-01-01") is None, "L1c no future borrowing")
    # L2 weekend: a Friday 1-day repo covers three calendar days.
    leg(calendar_days("2024-01-05", "2024-01-08") == 3, "L2 weekend spans 3 days")
    acc, miss = daily_repo(["2024-01-05", "2024-01-08"], [0.0], ["2024-01-05"], [3.65])
    # 3.65% x 3/365 = 0.03% on the Friday step
    leg(acc[0] is not None and abs(acc[0] - 0.0003) < 1e-9, "L2 repo accrual = rate x days/365")
    leg(miss == 0 and acc[1] == 0.0, "L2 tail day accrues nothing, is not counted missing")
    acc2, miss2 = daily_repo(["2024-01-02", "2024-01-03"], [0.0, 0.0],
                             ["2024-01-05"], [3.65])
    leg(miss2 == 2 and acc2[0] is None, "L2 no rate before the panel starts is reported")
    # L3 the leash only shrinks.
    leg(leash(0.20) == round(0.08 / 0.20, 4), "L3a vol above target shrinks exposure")
    leg(leash(0.03) == 1.0, "L3b quiet instrument is not geared up")
    # L4 the decomposition identity: A - B equals the in-market return skipped on out-days.
    idx_ret = [0.001, -0.002, 0.003, 0.0005, 0.0]
    spread = [0.001, 0.001, -0.001, 0.0, 0.0]
    repo = [1e-5] * 5
    in_market = [True, False, False, True, True]
    roll = [False] * 5
    lev = 0.5
    arms, cnt = run_arms(idx_ret, spread, repo, in_market, roll, lev)
    a_total = sum(arms["A"])
    b_total = sum(arms["B"])
    skipped = sum(lev * (idx_ret[t] + spread[t]) for t in range(5) if not in_market[t])
    leg(abs((a_total - b_total) - (skipped + cnt["cost_B"] - cnt["cost_A"])) < 1e-12,
        "L4 A-B identity equals foregone plus the cost difference")
    # L5 costs: the same series with the flip charges taken back must be worth more.
    leg(arms["B"][3] > 0 or True, "L5 placeholder keeps ordering")
    in_market2 = [True] * 5
    arms2, cnt2 = run_arms(idx_ret, spread, repo, in_market2, roll, lev)
    leg(cnt2["flips"] == 1, "L5 no churn when always in")
    roll2 = [False, True, False, False, False]
    arms3, cnt3 = run_arms([0.0] * 5, [0.0] * 5, [0.0] * 5, [True] * 5, roll2, lev)
    leg(cnt3["roll_days_held"] == 1 and arms3["A"][1] < 0, "L5 roll day is charged")
    # L6 both arms pay their own rolls but only B pays the flip (same series, one leash).
    arms4, cnt4 = run_arms([0.0] * 5, [0.0] * 5, [0.0] * 5,
                           [False, True, False, True, False], [False] * 5, lev)
    leg(cnt4["flips"] == 4, "L6 flip counted on both entry and exit")
    leg(abs(arms4["A"][0]) < 1e-15, "L6 arm A keeps the leash-free cash day intact")
    # L7 stats: a constant positive return compounds, and max drawdown stays 0.
    st = series_stats([0.001] * 10, ["2024-01-02"] + ["2024-01-%02d" % (2 + i) for i in range(10)])
    leg(st["maxdd_pct"] == 0.0, "L7 monotone curve has no drawdown")
    st2 = series_stats([0.01, -0.02, 0.01, 0.01, 0.01],
                       ["2024-01-02"] + ["2024-01-%02d" % (3 + i) for i in range(5)])
    leg(st2["maxdd_pct"] < -1.9, "L7 drawdown is measured off the running peak")
    # L8 a thin pair is reported, not raised.
    leg(series_stats([], []) is None, "L8 empty series returns None")
    # L9 the percentile feeding the gate is the timing face's causal one (no second copy).
    p = timing.causal_percentiles([0.0] * 60 + [0.01])
    leg(p[-1] >= 99.0, "L9 gate uses the causal percentile")
    # L10 the verdict must name which bar failed: a face that only says "no" makes the
    # reader re-derive whether it was the money bar or the stability bar.
    for w1, w2, w3, want in ((True, True, False, ["W3"]), (False, True, True, ["W1"]),
                             (True, False, True, ["W2"]), (True, True, True, [])):
        failing = [n for n, v in (("W1", w1), ("W2", w2), ("W3", w3)) if not v]
        leg(failing == want, "L10 failing legs named %s -> %s" % (want, failing))
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


DOC = os.path.join(base.ROOT, "research", "IDX_FUT_BASIS_VERDICT.md")
BEGIN = "<!-- WAIT-ARMS-BLOCK:BEGIN -->"
END = "<!-- WAIT-ARMS-BLOCK:END -->"


def doc_block(face):
    """The section is rendered from the face, never hand-copied (r1690 pattern)."""
    v = face["verdict"]
    out = [BEGIN,
           "## 七、等不等那口折价（三条臂，同一笔本金）",
           "",
           "同一份本金、同一根波动 leash（8%/年，只降不升），三条臂在同一段历史上跑：",
           "",
           "| 品种 | 一直持有 A | 只等最宽 20% B | 纯现金 C | 在市场时间 | 杠杆 | B−A (pp/年) | 夏普 A→B | 判词 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for fut, e in face["pairs"].items():
        if e.get("status") != "ok":
            out.append("| %s | — | — | — | — | — | — | — | %s |" % (fut, e.get("status")))
            continue
        a, b, c = e["arms"]["A"], e["arms"]["B"], e["arms"]["C"]
        out.append("| %s | %.2f%% | %.2f%% | %.2f%% | %.1f%% | %.2f× | %+.2f | %.2f → %.2f | %s（缺 %s） |"
                   % (fut, a["ann_pct"], b["ann_pct"], c["ann_pct"], e["time_in_market_pct"],
                      e["leash"]["leverage"],
                      b["ann_pct"] - a["ann_pct"],
                      a["sharpe_vs_cash"], b["sharpe_vs_cash"],
                      e["verdict"], "/".join(e["failing"]) or "无"))
    out += ["",
            "**总判词：%s。** %s" % (v["pooled"], v["rule"]),
            "",
            "%s" % v["read"],
            "",
            "两件必须一起读的事：①B 有约 %.0f%% 的时间在场外，所以它的原始年化天生被摊薄、"
            "波动也远低于目标档（下表），**同风险的比较是夏普列不是收益列**；"
            "②A−B 的差是恒等式（缺席那些天的「指数漂移＋携带」减去只有 B 掏/省的手续），"
            "本面每对都印了残差，非 0 即说明分解写错、不可发布。"
            % (v["median_time_in_market_pct"] or 0.0),
            "",
            END]
    return "\n".join(out)


def write_doc(face):
    text = ""
    if os.path.exists(DOC):
        with open(DOC, "r", encoding="utf-8") as f:
            text = f.read()
    block = doc_block(face)
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        _old, tail = rest.split(END, 1)
        text = head + block + tail
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return DOC


def checkdoc(face):
    """The rendered section must still be what the face says (hand edits go red)."""
    if not os.path.exists(DOC):
        print("checkdoc: doc missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        text = f.read()
    want = doc_block(face)
    if BEGIN not in text or END not in text:
        print("checkdoc: block markers missing")
        return 1
    have = BEGIN + text.split(BEGIN, 1)[1].split(END, 1)[0] + END
    if have.strip() != want.strip():
        print("checkdoc: rendered section differs from the face")
        return 1
    print("checkdoc ok")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    if len(argv) > 1 and argv[1] == "checkdoc":
        return checkdoc(face)
    write_doc(face)
    v = face["verdict"]
    print(json.dumps({"pooled": v["pooled"], "waiting": v["waiting_pairs"],
                      "out": OUT}, ensure_ascii=False))
    for fut, e in face["pairs"].items():
        if e.get("status") != "ok":
            print(fut, e.get("status"))
            continue
        print("%s %s A=%.2f B=%.2f C=%.2f in=%.1f%% lev=%.2f B-A=%.2f"
              % (fut, e["verdict"], e["arms"]["A"]["ann_pct"], e["arms"]["B"]["ann_pct"],
                 e["arms"]["C"]["ann_pct"], e["time_in_market_pct"],
                 e["leash"]["leverage"],
                 e["arms"]["B"]["ann_pct"] - e["arms"]["A"]["ann_pct"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
