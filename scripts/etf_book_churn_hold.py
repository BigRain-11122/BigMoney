#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is this book's money made by the names it just bought, or by the names it kept? (r1768)

r1763 put the book's annual return into four legs (select 59% / rotate 30% / cost -10.4pp
cumulative / size). r1766-r1767 then closed the timing axes: the select leg's money is a
monthly event profile and those months share no condition you could have seen beforehand.
Both of those answers are about *when*. This face asks *which names*, on the same book, the
same engine, the same panel.

Every rebalance replaces some of the five seats. Each bar the book earns, per name,

    pp_i = w_i * (r_i - r_bench)

(exactly the engine's own `select` leg, equity names only), so the contributions are
additive: sum over names and bars == the annualised select leg. Two readings come out of
that, and they answer different questions:

  1. **share** -- of the money the selection leg earned, how much sits on names bought at the
     last decision ("fresh") vs names the book already held ("incumbent")? This is where the
     money is.
  2. **per-name gap** -- is one fresh name worth more than one held name? This is the only
     one of the two that can be tested, because the shares are mechanically tied to how many
     seats turned over.

The test is a within-period label permutation: in each period keep the same names, the same
contributions and the same count of fresh seats, and only shuffle *which* of them were new.
That is exactly the null this data can speak to -- it holds both the number of seats and the
period's own luck fixed.

Two secondary axes are reported on the same periods, both read against their own shuffle
null: turnover at the decision (median split) and the book's 60-bar correlation with the
index at the decision (median split, causal). A 2x2 of those two carries the r1767 lesson --
with four cells one is always the best, so its verdict is read off a label-shuffle null with
a minimum cell size, never off the table.

The control arm must reproduce the published book (9.13% CAGR, select 7.4451pp) and the
replay must rebuild the engine's equity curve before anything is published.

Usage:
    python scripts/etf_book_churn_hold.py run
    python scripts/etf_book_churn_hold.py --check
    python scripts/etf_book_churn_hold.py --selftest
    python scripts/etf_book_churn_hold.py --md
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_equity_alpha as A                  # noqa: E402  (classify)
import etf_book_corr_select as CS             # noqa: E402  (the base arm's rule)
import etf_book_period_slice as PS            # noqa: E402  (ann_pp)
import etf_book_money_mde as MM               # noqa: E402  (replay)
import etf_book_gate_raise_noise as N         # noqa: E402  (arm_stats)
import etf_robust_pf as R                     # noqa: E402  (the engine)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_churn_hold.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CHURN_HOLD.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_SLICE = os.path.join(ROOT, "results", "etf_book_period_slice.json")

BENCH = CS.BENCH
GATE = CS.GATE
SEATS = CS.BASE_SEATS
PER_YEAR = 252.0
CONTROL_TOL_PP = 0.25        # book CAGR must reproduce the published cell
SELECT_TOL_PP = 0.05         # select leg must reproduce the r1762..r1767 cell
REPLAY_TOL = 1e-9

DRAWS = 2000                 # permutation draws; seeds frozen below
SEED = 20261116
P_SEP = 0.10                 # a split counts as separating at this level
MIN_CELL_PERIODS = 8         # a 2x2 cell needs real periods, not two lucky ones
CORR_WIN = 60                # the same window r1764/r1765 used
AGE_EDGES = (1, 21, 41, 81)  # holding-age buckets, in bars since the name was bought
ERA_CUT = "2024-01-01"       # the repo's own OOS convention: 2024+ is out of sample
IDENTITY_TOL = 1e-4          # the table stores 6 decimals; ~290 observations sum can drift


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- per-name attribution

def build_bars(close, openp, diag, rebal, n_hold, start, cls, bench=BENCH):
    """One row per engine bar, with the bar's excess attributable to each held name.

    Mirrors `etf_book_money_mde.replay` exactly (same decision map, same scale, same
    skip when the benchmark return is missing) so that summing these legs reproduces the
    engine's select/rotate legs to rounding. `fresh` is decided at the decision bar: a name
    in the new book that was not in the book before it.
    """
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    by_date = {str(r["date"]): r for r in diag if r.get("book")}
    held, age = {}, {}
    bars, periods, cur = [], [], None
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            row = by_date.get(str(pd.Timestamp(d).date()))
            cur = {"decision": str(pd.Timestamp(d).date()), "bars": 0, "turn": 0.0,
                   "legs": {}, "r_bench_sum": 0.0, "no_decision": row is None}
            periods.append(cur)
            if row is not None:
                scale = float(row.get("scale") or 0.0)
                new = {p: scale / float(n_hold) for p in row["book"]}
                cur["turn"] = float(sum(abs(new.get(k, 0.0) - held.get(k, 0.0))
                                        for k in set(new) | set(held)))
                fresh = set(new) - set(held)
                cur["fresh"] = sorted(fresh)
                age = {k: (0 if k in fresh else age.get(k, 0)) for k in new}
                held = new
        if cur is None:          # bars before the first decision belong to no period
            continue
        for k in held:
            age[k] = age.get(k, 0) + 1
        r_b = np.nan
        if bench in op.columns:
            a, b = op.at[d, bench], op.at[nxt, bench]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r_b = float(b / a - 1.0)
        if not np.isfinite(r_b):
            continue             # replay skips these bars too (identity depends on it)
        row_legs = {}
        for k, w in held.items():
            if k not in op.columns:
                continue
            a, b = op.at[d, k], op.at[nxt, k]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                row_legs[k] = float(w) * float(b / a - 1.0 - r_b)
        bars.append({"date": str(pd.Timestamp(nxt).date()), "r_bench": r_b,
                     "corr": {}, "turn": cur["turn"], "legs": row_legs,
                     "age": {k: int(age.get(k, 0)) for k in row_legs}})
        cur["bars"] += 1
        cur["r_bench_sum"] += r_b
        for k, v in row_legs.items():
            rec = cur["legs"].setdefault(k, {"sum": 0.0,
                                             "fresh": k in (cur.get("fresh") or ()),
                                             "eq": cls.get(k) == "equity"})
            rec["sum"] += v
            rec["age"] = int(age.get(k, 0))
    return bars, periods


def scale_periods(periods, n_bars):
    """Turn the raw per-name sums into annualised pp, so every cut stays additive.

    Only the four fields a reader or `--check` needs survive (pp / fresh / eq / age):
    the evidence file is the published table, not a dump of the attribution loop.
    """
    f = PER_YEAR * 100.0 / float(max(1, n_bars))
    for p in periods:
        for rec in p["legs"].values():
            rec["pp"] = rec["sum"] * f
        p["select_pp"] = float(sum(r["pp"] for r in p["legs"].values() if r["eq"]))
        p["rotate_pp"] = float(sum(r["pp"] for r in p["legs"].values() if not r["eq"]))
        p["r_bench_pp"] = p["r_bench_sum"] * f
        for k in ("turn", "select_pp", "rotate_pp", "r_bench_pp"):
            p[k] = round(float(p[k]), 6)
        p["legs"] = {k: {"pp": round(float(r["pp"]), 6), "fresh": bool(r["fresh"]),
                         "eq": bool(r["eq"]), "age": int(r.get("age") or 0)}
                     for k, r in p["legs"].items()}
    return periods


def equity_obs(periods):
    """One observation per (period, equity name): its pp contribution and its flags."""
    out = []
    for p in periods:
        for k, rec in p["legs"].items():
            if not rec["eq"]:
                continue
            out.append({"period": p["decision"], "name": k, "pp": float(rec["pp"]),
                        "fresh": bool(rec["fresh"]), "age": int(rec.get("age") or 0)})
    return out


def fresh_split(periods):
    """Money share (what you read) and per-name gap (what can be tested)."""
    f_sum = f_n = i_sum = i_n = 0.0
    f_pp = i_pp = 0.0
    all_fresh = none_fresh = 0
    for p in periods:
        eq = [r for r in p["legs"].values() if r["eq"]]
        if not eq:
            continue
        nf = sum(1 for r in eq if r["fresh"])
        if nf == len(eq):
            all_fresh += 1
        if nf == 0:
            none_fresh += 1
        for r in eq:
            if r["fresh"]:
                f_sum += float(r["pp"]); f_n += 1; f_pp += float(r["pp"])
            else:
                i_sum += float(r["pp"]); i_n += 1; i_pp += float(r["pp"])
    if f_n == 0 or i_n == 0:
        return {"n_obs_fresh": int(f_n), "n_obs_incumbent": int(i_n),
                "sum_fresh_pp": round(f_pp, 4), "sum_incumbent_pp": round(i_pp, 4),
                "share_fresh": None, "mean_fresh_pp": None, "mean_incumbent_pp": None,
                "gap_pp": None, "periods_all_fresh": all_fresh,
                "periods_none_fresh": none_fresh}
    tot = f_pp + i_pp
    return {"n_obs_fresh": int(f_n), "n_obs_incumbent": int(i_n),
            "sum_fresh_pp": round(f_pp, 4), "sum_incumbent_pp": round(i_pp, 4),
            "share_fresh": (round(f_pp / tot, 4) if abs(tot) > 1e-12 else None),
            "mean_fresh_pp": round(f_pp / f_n, 6),
            "mean_incumbent_pp": round(i_pp / i_n, 6),
            "gap_pp": round(f_pp / f_n - i_pp / i_n, 6),
            "per_name_ratio": (round((f_pp / f_n) / (i_pp / i_n), 4)
                               if abs(i_pp / i_n) > 1e-12 else None),
            "periods_all_fresh": all_fresh, "periods_none_fresh": none_fresh}


def fresh_perm(periods, draws=DRAWS, seed=SEED):
    """Within-period label permutation: same names, same pp, same number of fresh seats."""
    obs = fresh_split(periods)
    if obs.get("gap_pp") is None:
        return {"gap_pp": None, "p_two_sided": None, "draws": draws, "seed": seed,
                "note": "no period splits its seats both ways; the null is empty"}
    plans = []
    for p in periods:
        eq = [r for r in p["legs"].values() if r["eq"]]
        if not eq:
            continue
        vals = [float(r["pp"]) for r in eq]
        nf = sum(1 for r in eq if r["fresh"])
        plans.append((vals, nf))
    base = abs(float(obs["gap_pp"]))
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(draws):
        f_sum = f_n = i_sum = i_n = 0.0
        for vals, nf in plans:
            tot = sum(vals)
            if nf == 0:
                i_sum += tot; i_n += len(vals); continue
            if nf == len(vals):
                f_sum += tot; f_n += len(vals); continue
            take = rng.choice(len(vals), size=nf, replace=False)
            s = sum(vals[j] for j in take)
            f_sum += s; f_n += nf
            i_sum += tot - s; i_n += len(vals) - nf
        if f_n == 0 or i_n == 0:
            continue
        if abs(f_sum / f_n - i_sum / i_n) >= base - 1e-12:
            hits += 1
    return {"gap_pp": round(float(obs["gap_pp"]), 6),
            "p_two_sided": round((hits + 1.0) / (draws + 1.0), 4),
            "draws": draws, "seed": seed, "statistic": "mean pp per fresh name - per incumbent name",
            "null": "which of a period's held names were new, counts held fixed"}


def median_split(periods, field, draws=DRAWS, seed=SEED):
    """Median split of a period-level, decision-time state; null = shuffle the period pp."""
    pairs = [(p.get(field), float(p["select_pp"])) for p in periods
             if p.get(field) is not None]
    if len(pairs) < 2 * MIN_CELL_PERIODS:
        return {"field": field, "note": "too few readable periods", "n_periods": len(pairs)}
    thr = float(np.median([v for v, _ in pairs]))
    hi = [c for v, c in pairs if v > thr]
    lo = [c for v, c in pairs if v <= thr]
    if not hi or not lo:
        return {"field": field, "note": "one side is empty", "n_periods": len(pairs)}
    gap = float(np.mean(hi) - np.mean(lo))
    rng = np.random.default_rng(seed)
    allv = np.array([c for _, c in pairs], float)
    n_hi = len(hi)
    base = abs(gap)
    hits = 0
    for _ in range(draws):
        perm = rng.permutation(allv)
        g = float(perm[:n_hi].mean() - perm[n_hi:].mean())
        if abs(g) >= base - 1e-12:
            hits += 1
    return {"field": field, "threshold": round(thr, 6), "n_periods": len(pairs),
            "n_high": len(hi), "n_low": len(lo),
            "mean_high_pp": round(float(np.mean(hi)), 4),
            "mean_low_pp": round(float(np.mean(lo)), 4),
            "gap_pp": round(gap, 4),
            "p_two_sided": round((hits + 1.0) / (draws + 1.0), 4),
            "draws": draws, "seed": seed,
            "null": "period pp shuffled across periods, split sizes held fixed"}


def joint_cells(periods, draws=DRAWS, seed=SEED):
    """2x2 of turnover and index correlation, with the r1767 best-cell null."""
    pairs = [(p.get("turn"), p.get("corr60"), float(p["select_pp"]), p.get("decision"))
             for p in periods
             if p.get("turn") is not None and p.get("corr60") is not None]
    if len(pairs) < 4 * MIN_CELL_PERIODS:
        return {"cells": [], "best_cell": {"note": "too few readable periods"}}
    t_thr = float(np.median([t for t, _, _, _ in pairs]))
    c_thr = float(np.median([c for _, c, _, _ in pairs]))
    groups = {}
    for t, c, v, d in pairs:
        key = "T%s_C%s" % ("+" if t > t_thr else "-", "+" if c > c_thr else "-")
        groups.setdefault(key, []).append((v, str(d)))
    cells = []
    for key in sorted(groups):
        v = np.array([x[0] for x in groups[key]], float)
        cells.append({"cell": key, "n_periods": int(len(v)),
                      "mean_pp": round(float(v.mean()), 4),
                      "sum_pp": round(float(v.sum()), 4),
                      "positive_share": round(float((v > 0).mean()), 4)})

    def best_gap(v):
        overall = float(v.mean())
        best, best_cell = -1e9, None
        pos = 0
        for key in sorted(groups):
            n = len(groups[key])
            if n < MIN_CELL_PERIODS:
                pos += n
                continue
            g = float(v[pos:pos + n].mean()) - overall
            if g > best:
                best, best_cell = g, key
            pos += n
        return best, best_cell

    vals = np.concatenate([np.array([x[0] for x in groups[k]], float) for k in sorted(groups)])
    obs_gap, obs_cell = best_gap(vals)
    if obs_cell is None:
        return {"cells": cells, "turn_threshold": round(t_thr, 6),
                "corr_threshold": round(c_thr, 6),
                "best_cell": {"note": "no cell holds MIN_CELL_PERIODS periods"}}
    rng = np.random.default_rng(seed + 3)
    hits = 0
    for _ in range(draws):
        g, _c = best_gap(rng.permutation(vals))
        if g >= obs_gap - 1e-12:
            hits += 1
    era_is = [x[0] for x in groups[obs_cell] if x[1] < ERA_CUT]
    era_oos = [x[0] for x in groups[obs_cell] if x[1] >= ERA_CUT]
    return {"cells": cells, "turn_threshold": round(t_thr, 6),
            "corr_threshold": round(c_thr, 6),
            "best_cell": {"cell": obs_cell,
                          "n_periods": int(len(groups[obs_cell])),
                          "gap_pp": round(float(obs_gap), 4),
                          "p_shuffle": round((hits + 1.0) / (draws + 1.0), 4),
                          "draws": draws, "seed": seed + 3,
                          "min_cell_periods": MIN_CELL_PERIODS,
                          "overall_mean_pp": round(float(vals.mean()), 4),
                          "era": {"cut": ERA_CUT,
                                  "is_n": len(era_is),
                                  "is_mean_pp": (round(float(np.mean(era_is)), 4)
                                                 if era_is else None),
                                  "oos_n": len(era_oos),
                                  "oos_mean_pp": (round(float(np.mean(era_oos)), 4)
                                                  if era_oos else None),
                                  "same_side": (None if not era_is or not era_oos
                                                else bool((float(np.mean(era_is)) > 0)
                                                          == (float(np.mean(era_oos)) > 0))),
                                  "note": "one cell passing the null is a lead; an edge that "
                                          "changes sign between eras is a period pileup"}}}


def jc_cell_mean(jc, cell):
    for c in jc.get("cells") or []:
        if c["cell"] == cell:
            return c["mean_pp"]
    return None


def age_table(obs):
    """Where in a name's life does the money arrive? Buckets are frozen above."""
    edges = list(AGE_EDGES) + [10 ** 9]
    out = []
    total = sum(o["pp"] for o in obs)
    for lo, hi in zip(edges[:-1], edges[1:]):
        sub = [o for o in obs if lo <= o["age"] < hi]
        if not sub:
            continue
        s = float(sum(o["pp"] for o in sub))
        out.append({"age_from": lo, "age_to": (None if hi >= 10 ** 9 else hi - 1),
                    "n_obs": len(sub), "sum_pp": round(s, 4),
                    "share": (round(s / total, 4) if abs(total) > 1e-12 else None),
                    "mean_pp": round(s / len(sub), 6)})
    return out


def top_names(obs, n=6):
    """Aggregate each name over the whole window before ranking -- one big period is not a name."""
    def key(flag):
        agg = {}
        for o in obs:
            if o["fresh"] is not flag:
                continue
            rec = agg.setdefault(o["name"], {"pp": 0.0, "periods": 0})
            rec["pp"] += float(o["pp"])
            rec["periods"] += 1
        rows = sorted(agg.items(), key=lambda kv: -kv[1]["pp"])[:n]
        return [{"name": k, "pp": round(v["pp"], 4), "periods": int(v["periods"])}
                for k, v in rows]
    return {"fresh_top": key(True), "incumbent_top": key(False)}


def beta_summary(df):
    """Book vs index, bar level: how much of the return is the index's own move."""
    x = df["r_bench"].to_numpy(float)
    y = df["net"].to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 20 or float(np.var(x, ddof=1)) <= 0:
        return {"note": "too few bars"}
    cov = float(np.cov(y, x, ddof=1)[0, 1])
    var = float(np.var(x, ddof=1))
    beta = cov / var
    alpha_d = float(y.mean()) - beta * float(x.mean())
    corr = cov / float(np.sqrt(var * float(np.var(y, ddof=1))))
    net_ann = float(y.mean()) * PER_YEAR * 100.0
    beta_part = beta * float(x.mean()) * PER_YEAR * 100.0
    share = (beta_part / net_ann) if abs(net_ann) > 1e-12 else None
    return {"beta": round(beta, 4), "corr": round(corr, 4), "r2": round(corr ** 2, 4),
            "alpha_ann_pp": round(alpha_d * PER_YEAR * 100.0, 4),
            "net_ann_pp": round(net_ann, 4),
            "bench_ann_pp": round(float(x.mean()) * PER_YEAR * 100.0, 4),
            "beta_leg_pp": round(beta_part, 4),
            "beta_share_of_net": (round(share, 4) if share is not None else None),
            "bars": int(len(x)),
            "read": "指数自己的涨跌贡献 %.2fpp，占全书 %.2fpp/年 的 %.1f%%——剩下的都不是 beta。"
                    "相关系数回答的是另一个问题：指数下跌时这本书会不会跟着跌（相关 %.2f，R² %.2f）。"
                    "（这里的年化是 bar 算术均值的年化，指数几何年化约 0.1%%，两个口径不要混读。）"
                    % (beta_part, net_ann, (share or 0.0) * 100.0, corr, corr ** 2)}


def touch_corr(periods, df):
    """Causal 60-bar correlation/beta of the book vs the index at each decision bar."""
    d = df[["net", "r_bench"]].dropna()
    for p in periods:
        sub = d[d.index <= pd.Timestamp(p["decision"])].tail(CORR_WIN)
        p["corr_n"] = int(len(sub))
        if len(sub) < CORR_WIN // 2:
            p["corr60"] = None
            p["beta60"] = None
            continue
        x = sub["r_bench"].to_numpy(float)
        y = sub["net"].to_numpy(float)
        v = float(np.var(x, ddof=1))
        if v <= 0:
            p["corr60"] = None
            p["beta60"] = None
            continue
        p["corr60"] = round(float(np.corrcoef(x, y)[0, 1]), 6)
        p["beta60"] = round(float(np.cov(y, x, ddof=1)[0, 1] / v), 6)
    return periods


def classify(control, fresh, perm):
    if not control.get("ok"):
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与在印的书对不上（年化差 %s pp / 选股腿差 %s pp），"
                            "这不是同一本书，本面不判。"
                            % (control.get("delta_pp"), control.get("select_delta_pp"))}
    if not control.get("replay_ok"):
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "重放重建不出引擎净值，按名字拆的腿不是这台引擎的，本面不判。"}
    if fresh.get("gap_pp") is None or perm.get("p_two_sided") is None:
        return {"verdict": "CANNOT_JUDGE_NO_SPLIT",
                "sentence": "这本书的席位在样本里没有同时出现「新买的」和「留着的」，"
                            "换手轴无对照，本面不判。"}
    p = float(perm["p_two_sided"])
    gap = float(fresh["gap_pp"])
    if p <= P_SEP and gap > 0:
        return {"verdict": "FRESH_CARRIES_ALPHA",
                "sentence": "钱在刚买进来的名字上：一只新名字平均 %+.3fpp，一只留着的名字 "
                            "%+.3fpp，差 %+.3fpp（同周期内打乱「哪几只是新的」%d 次，只有 %.1f%% "
                            "造得出这么大的差）——这本书是靠换名字赚钱的，换手不是它的敌人，"
                            "是它的引擎。"
                            % (fresh["mean_fresh_pp"], fresh["mean_incumbent_pp"], gap,
                               perm.get("draws") or DRAWS, p * 100.0)}
    if p <= P_SEP and gap < 0:
        return {"verdict": "INCUMBENT_CARRIES_ALPHA",
                "sentence": "钱在留着的名字上：一只留着的名字平均 %+.3fpp，一只新名字 %+.3fpp，"
                            "差 %+.3fpp（打乱 %d 次只有 %.1f%% 造得出这么大的差）——这本书的"
                            "超额是坐出来的，换手主要在付出成本。"
                            % (fresh["mean_incumbent_pp"], fresh["mean_fresh_pp"], gap,
                               perm.get("draws") or DRAWS, p * 100.0)}
    return {"verdict": "CHURN_AND_HOLD_TIE",
            "sentence": "新名字与老名字单车贡献分不开：新 %+.3fpp vs 留 %+.3fpp，差 %+.3fpp，"
                        "同周期打乱「哪几只是新的」%d 次里 %.0f%% 能造出一样大的差——"
                        "这本书的钱既不是换名字买来的，也不是坐着拿来的。"
                        % (fresh["mean_fresh_pp"], fresh["mean_incumbent_pp"], gap,
                           perm.get("draws") or DRAWS, p * 100.0)}


# ---------------------------------------------------------------- run

def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    cut = price.get("evidence_cutoff")
    slice_face = _load(FACE_SLICE) if os.path.exists(FACE_SLICE) else {}
    r1767_select_pp = (slice_face.get("months") or {}).get("total_pp")
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")

    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)

    diag = []
    ser, mean_turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, SEATS,
                                          cost, vol_target=vol_target, vol_window=60,
                                          diag=diag)
    stats = N.arm_stats(ser)
    df = MM.replay(close, openp, diag, rebal, SEATS, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    replay_max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                            / joined["engine"].iloc[-1]) if len(joined) else None)
    select_ann_pp = PS.ann_pp(df["select"].dropna().mean())
    print("[base] cagr=%6.3f%% select=%+6.3fpp replay_rel=%.2e"
          % (float(stats["full"]["cagr"]) * 100.0, select_ann_pp, replay_max_rel or 0.0),
          flush=True)

    bars, periods = build_bars(close, openp, diag, rebal, SEATS, R.START, cls)
    periods = scale_periods(periods, len(bars))
    periods = touch_corr(periods, df)
    obs = equity_obs(periods)
    fresh = fresh_split(periods)
    perm = fresh_perm(periods)
    turn_split = median_split(periods, "turn")
    corr_split = median_split(periods, "corr60")
    cells = joint_cells(periods)
    ages = age_table(obs)

    sel_sum = float(sum(o["pp"] for o in obs))
    rot_sum = float(sum(p["rotate_pp"] for p in periods))
    cagr_pct = round(float(stats["full"]["cagr"]) * 100.0, 3)
    published_cagr = (None if published.get("cagr") is None
                      else round(float(published["cagr"]) * 100.0, 3))
    delta_pp = (None if published_cagr is None else round(cagr_pct - published_cagr, 3))
    select_delta = (None if r1767_select_pp is None
                    else round(select_ann_pp - float(r1767_select_pp), 4))
    control = {
        "cagr_pct": cagr_pct, "published_cagr_pct": published_cagr,
        "delta_pp": delta_pp, "tol_pp": CONTROL_TOL_PP,
        "select_ann_pp": round(select_ann_pp, 4), "r1767_select_pp": r1767_select_pp,
        "select_delta_pp": select_delta, "select_tol_pp": SELECT_TOL_PP,
        "replay_max_rel": replay_max_rel, "replay_tol": REPLAY_TOL,
        "replay_ok": bool(replay_max_rel is not None and replay_max_rel <= REPLAY_TOL),
        "mean_turnover": round(float(mean_turn), 4),
    }
    control["ok"] = bool(delta_pp is not None and abs(delta_pp) <= CONTROL_TOL_PP
                         and select_delta is not None and abs(select_delta) <= SELECT_TOL_PP)
    v = classify(control, fresh, perm)

    out = {
        "evidence_cutoff": cut or str(pd.Timestamp(close.index[-1]).date()),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_churn_hold.py",
        "rule": {
            "benchmark": BENCH, "gate_cny": GATE, "seats": SEATS, "rebal": rebal,
            "cost_bp_per_side": cfg.get("cost_bp_per_side"), "vol_target": vol_target,
            "question": "does the select leg's money sit on names bought at the last "
                        "decision or on names the book already held",
            "attribution": "pp_i = w_i * (r_i - r_bench), summed over bars and annualised; "
                           "sum over equity names == the select leg, sum over the rest == the "
                           "rotate leg",
            "fresh": "a name in the new book that was not in the book at the previous decision",
            "primary_test": "within-period label permutation of which held names were new, "
                            "counts held fixed, statistic = mean pp per fresh name minus mean "
                            "pp per incumbent name",
            "secondary": ["turnover at the decision (median split)",
                          "book-vs-index 60-bar correlation at the decision (median split)",
                          "2x2 of those two with a label-shuffle best-cell null"],
            "draws": DRAWS, "seed": SEED, "p_sep": P_SEP,
            "min_cell_periods": MIN_CELL_PERIODS, "corr_window": CORR_WIN,
            "age_buckets_from": list(AGE_EDGES),
            "frozen": "criteria written before the run; --check re-derives them off the "
                      "period table on disk",
        },
        "config": {"universe_measured": len(close.columns), "flips_repaired": int(n_flip),
                   "bars": len(bars), "periods": len(periods),
                   "mean_turnover": round(float(mean_turn), 4)},
        "control": control,
        "totals": {
            "select_ann_pp": round(select_ann_pp, 4),
            "rotate_ann_pp": round(rot_sum, 4),
            "net_ann_pp": round(PS.ann_pp(df["net"].dropna().mean()), 4),
            "cost_ann_pp": round(PS.ann_pp(df["cost"].dropna().mean()), 4),
            "bench_ann_pp": round(PS.ann_pp(df["r_bench"].dropna().mean()), 4),
            "identity_select_sum_pp": round(sel_sum, 4),
            "identity_select_abs_error": abs(sel_sum - select_ann_pp),
            "identity_ok": bool(abs(sel_sum - select_ann_pp) <= IDENTITY_TOL),
        },
        "beta": beta_summary(df),
        "fresh": fresh,
        "fresh_perm": perm,
        "turn_split": turn_split,
        "corr_split": corr_split,
        "joint_cells": cells,
        "ages": ages,
        "names": top_names(obs),
        "periods": [{k: p[k] for k in ("decision", "turn", "corr60", "beta60", "corr_n",
                                       "bars", "select_pp", "rotate_pp", "r_bench_pp",
                                       "legs") if k in p} for p in periods],
        **v,
        "run_seconds": round(time.time() - t0, 1),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[fresh] share=%s gap=%+.4fpp p=%s (n_fresh=%d n_inc=%d)"
          % (fresh.get("share_fresh"), fresh.get("gap_pp") or 0.0,
             perm.get("p_two_sided"), fresh["n_obs_fresh"], fresh["n_obs_incumbent"]),
          flush=True)
    for s in (turn_split, corr_split):
        if s.get("gap_pp") is not None:
            print("[split] %-8s thr=%.4f hi=%+.4f lo=%+.4f gap=%+.4f p=%s"
                  % (s["field"], s["threshold"], s["mean_high_pp"], s["mean_low_pp"],
                     s["gap_pp"], s["p_two_sided"]), flush=True)
    bc = cells.get("best_cell") or {}
    if bc.get("cell"):
        print("[joint] best %s n=%d gap=%+.4f p=%s"
              % (bc["cell"], bc["n_periods"], bc["gap_pp"], bc["p_shuffle"]), flush=True)
    print("[verdict] %s" % v["verdict"], flush=True)
    print("[write] %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


# ---------------------------------------------------------------- write-up

def write_md():
    d = _load(OUT_JSON)
    L = []
    L.append("# 钱在刚买进来的名字上，还是在留着的名字上（r1768）\n")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_churn_hold.py`；"
             "证据 `results/etf_book_churn_hold.json`。\n"
             "> 同一台引擎、同一张面板、同一把尺（窗 %d 期；%d 次打乱；种子 %d）。\n"
             % (d.get("evidence_cutoff"), d.get("panel_last_bar"),
                d.get("config", {}).get("periods") or 0, d["rule"]["draws"], d["rule"]["seed"]))
    L.append("## 问的问题\n")
    L.append("r1766/r1767 把「什么时候赚钱」问完了（月度事件、天气不可预告）。本轮问**哪几只名字**："
             "每次调仓会换掉五个座位里的几个，钱是落在刚换进来的名字上，还是落在已经拿着的名字上。\n")
    L.append("拆法：每一根 bar、每一只名字的贡献就是引擎自己的选股腿\n\n")
    L.append("    pp_i = w_i * (r_i - r_bench)\n\n")
    L.append("按名字和按 bar 加总是精确的：权益名字的贡献加起来 == 选股腿，其余 == 轮动腿。"
             "「新名字」= 这次决策买进来、上次决策不在书里的名字。\n")
    L.append("## 两个读数，别混着读\n")
    f = d["fresh"]
    L.append("- **份额（钱在哪）**：新名字贡献 %+.3fpp（占 %s%%），留着的名字 %+.3fpp。\n"
             % (f["sum_fresh_pp"],
                ("%.1f" % (f["share_fresh"] * 100.0)) if f.get("share_fresh") is not None else "?",
                f["sum_incumbent_pp"]))
    L.append("- **单车（能不能测）**：一只新名字平均 %+.4fpp，一只留着的名字平均 %+.4fpp，"
             "差 **%+.4fpp**（同周期内打乱「哪几只是新的」%d 次，双侧 p=**%s**）。\n"
             % (f["mean_fresh_pp"] or 0.0, f["mean_incumbent_pp"] or 0.0, f["gap_pp"] or 0.0,
                d["fresh_perm"]["draws"], d["fresh_perm"].get("p_two_sided")))
    L.append("- 份额天然被「换了几座」牵着走（换得多，新名字的名字-期就多），所以判词读单车差、"
             "份额只当钱的分布看。两读同向才算同一件事。\n")
    L.append("- 期数分布：%d 个周期全是新名字（整本换掉）、%d 个周期一个都没换，"
             "其余周期两侧都有，才进得了打乱。\n"
             % (f["periods_all_fresh"], f["periods_none_fresh"]))
    L.append("- **这本书几乎不持有**：%d 只名字-期里 %d 只是刚买的（%.0f%%），只有 %d 只是留着的。"
             "所以「换手 vs 持有」在这个规则下不是一个可以观察的选择，而是它的构造——"
             "五座的书每次调仓后基本换了个遍。这条比上面的 p 值重要：它说明本面测的是一个"
             "没有对照臂的书，而「强制留几座」是要另开一条臂去问的事。\n"
             % (f["n_obs_fresh"] + f["n_obs_incumbent"], f["n_obs_fresh"],
                100.0 * f["n_obs_fresh"] / max(1, f["n_obs_fresh"] + f["n_obs_incumbent"]),
                f["n_obs_incumbent"]))
    L.append("\n## 判词\n")
    L.append("**%s** — %s\n" % (d.get("verdict"), d.get("sentence")))
    L.append("\n## 这本书和指数的关系（顺手量清楚）\n")
    b = d["beta"]
    L.append("| | 值 |\n|---|---|\n")
    L.append("| 全书 vs 510300 beta | %s |\n" % b.get("beta"))
    L.append("| 相关系数 / R² | %s / %s |\n" % (b.get("corr"), b.get("r2")))
    L.append("| 年化 alpha | %s pp |\n" % b.get("alpha_ann_pp"))
    L.append("| 年化 net / 指数 | %s pp / %s pp |\n" % (b.get("net_ann_pp"), b.get("bench_ann_pp")))
    L.append("| beta 腿占净收益 | %s |\n" % b.get("beta_share_of_net"))
    L.append("\n%s\n"
             "四个腿的年度账：选股 %+.2fpp / 轮动 %+.2fpp / 成本 %+.2fpp / 合计 net %+.2fpp，"
             "选股腿加总恒等误差 %.1e（pp 表存 6 位小数，%d 个观测加总会有这点漂移）。\n"
             % (b.get("read", ""),
                d["totals"]["select_ann_pp"], d["totals"]["rotate_ann_pp"],
                d["totals"]["cost_ann_pp"], d["totals"]["net_ann_pp"],
                d["totals"]["identity_select_abs_error"],
                f["n_obs_fresh"] + f["n_obs_incumbent"]))
    L.append("\n## 两条副轴（同一批周期）\n")
    for key, label in (("turn_split", "换手（决策时的换手率中位切）"),
                       ("corr_split", "与指数 60 日相关（决策时中位切）")):
        s = d.get(key) or {}
        if s.get("gap_pp") is None:
            L.append("- %s：%s\n" % (label, s.get("note", "不可判")))
            continue
        L.append("- %s：高侧 %.4fpp/期 vs 低侧 %.4fpp/期，差 %+.4fpp（打乱 p=%s，"
                 "阈值 %.4f，%d 期）\n"
                 % (label, s["mean_high_pp"], s["mean_low_pp"], s["gap_pp"],
                    s["p_two_sided"], s["threshold"], s["n_periods"]))
    jc = d.get("joint_cells") or {}
    if jc.get("cells"):
        L.append("\n### 换手 × 相关 2×2（四格里总有一格最好，所以判词读打乱空分布）\n")
        L.append("| 格 | 周期数 | 平均 pp/期 | 正贡献期占比 |\n|---|---|---|---|\n")
        for c in jc["cells"]:
            L.append("| %s | %d | %+.4f | %.0f%% |\n"
                     % (c["cell"], c["n_periods"], c["mean_pp"], c["positive_share"] * 100.0))
        bc = jc.get("best_cell") or {}
        if bc.get("cell"):
            era = bc.get("era") or {}
            L.append("\n最好的一格 %s（%d 期，全表均值 %+.4fpp/期）平均 %+.4fpp/期，打乱 %d 次里 "
                     "%.1f%% 也能造出一样好或更好的一格。\n"
                     % (bc["cell"], bc["n_periods"], bc.get("overall_mean_pp") or 0.0,
                        (jc_cell_mean(jc, bc["cell"])), bc["draws"], bc["p_shuffle"] * 100.0))
            if era.get("is_mean_pp") is not None and era.get("oos_mean_pp") is not None:
                L.append("分代复核（%s 切）：样本内 %d 期 %+.4fpp/期，样本外 %d 期 %+.4fpp/期，"
                         "同号=%s。\n"
                         % (era["cut"], era["is_n"], era["is_mean_pp"], era["oos_n"],
                            era["oos_mean_pp"], "是" if era["same_side"] else "**否**"))
                if era["oos_n"] and era["oos_mean_pp"] <= (bc.get("overall_mean_pp") or 0.0):
                    L.append("**样本外这一格 %+.4fpp/期，与全表均值 %+.4fpp/期分不开**——"
                             "也就是说，这个「最好的一格」在 2024 年之后不再最好。"
                             "按定格判据它过线，按这笔钱该怎么用它是零。\n"
                             % (era["oos_mean_pp"], bc.get("overall_mean_pp") or 0.0))
            L.append("\n这条要按线索读，不能按发现读：两把边缘刀（换手 %s、相关 %s）单看都不过线，"
                     "过线的只是它们交叉出来的一格；%d 期、%d 个格子里挑最好的一格，"
                     "本身就是在噪声里找形状。\n"
                     % (d["turn_split"].get("p_two_sided"), d["corr_split"].get("p_two_sided"),
                        bc["n_periods"], len(jc["cells"])))
    L.append("\n## 持有时间轮廓\n")
    L.append("> 注意：一个周期就是 20 根 bar，所以「买入后 1-20 根」与上一节的「新名字」是同一批"
             "观测（%d 个）——这张表不是独立证据，它是同一件事的另一种写法，摆出来只为看"
             "「钱会不会在名字变老之后回来」。\n\n" % (d["fresh"]["n_obs_fresh"]))
    L.append("| 买入后第几根 bar | 观测数 | 合计 pp | 份额 | 单车 pp |\n|---|---|---|---|---|\n")
    for a in d["ages"]:
        L.append("| %d-%s | %d | %+.3f | %s%% | %+.4f |\n"
                 % (a["age_from"], a["age_to"] if a["age_to"] else "+", a["n_obs"],
                    a["sum_pp"],
                    ("%.0f" % (a["share"] * 100.0)) if a.get("share") is not None else "?",
                    a["mean_pp"]))
    L.append("\n## 控制臂\n")
    c = d["control"]
    L.append("年化 %.3f%% vs 在印 %.3f%%（差 %s pp，容差 %.2f）；选股腿 %.4fpp vs r1767 在印 %s"
             "（差 %s pp，容差 %.2f）；重放最大相对偏差 %.2e（容差 %.0e）。\n"
             % (c["cagr_pct"], c["published_cagr_pct"], c["delta_pp"], c["tol_pp"],
                c["select_ann_pp"], c["r1767_select_pp"], c["select_delta_pp"],
                c["select_tol_pp"], c["replay_max_rel"], c["replay_tol"]))
    L.append("\n## 这张面不说什么\n")
    L.append("- 它是**事后**的拆法：你没法事前选「哪一只能赚钱的新名字」。所以它不给杠杆，"
             "只给一句话——若判「钱在新名字上」，那么降低调仓频率会伤到这本书（换手就是引擎）；"
             "若判「钱在留着的名字上」，那么拉长持有是安全的，换手主要是成本。\n")
    L.append("- 单车差是**同周期内**的比较，控制了当期的市场天气；但它不控制「新名字恰好是当期"
             "分数更高的那些」，所以它仍然只是描述，不是因果。\n")
    L.append("- 成本只按 10bp/边实收，滑点未建模；换手越高，这个缺口越大。\n")
    L.append("- ETF 票池为现存标的（幸存者偏差照旧）；2020-2023 段收益薄。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("".join(L))
    print("[write] %s" % OUT_MD, flush=True)
    return 0


# ---------------------------------------------------------------- checks

def _check():
    d = _load(OUT_JSON)
    problems = []
    periods = d["periods"]
    obs = equity_obs(periods)
    sel_sum = float(sum(o["pp"] for o in obs))
    if abs(sel_sum - d["control"]["select_ann_pp"]) > IDENTITY_TOL:
        problems.append("per-name select sum %.6f != control %.6f"
                        % (sel_sum, d["control"]["select_ann_pp"]))
    fresh = fresh_split(periods)
    for k in ("sum_fresh_pp", "sum_incumbent_pp", "mean_fresh_pp", "mean_incumbent_pp",
              "gap_pp", "n_obs_fresh", "n_obs_incumbent"):
        if d["fresh"].get(k) != fresh.get(k):
            problems.append("fresh.%s re-derives to %s, face says %s"
                            % (k, fresh.get(k), d["fresh"].get(k)))
    perm = fresh_perm(periods)
    if perm.get("p_two_sided") != d["fresh_perm"].get("p_two_sided"):
        problems.append("permutation p re-derives to %s, face says %s"
                        % (perm.get("p_two_sided"), d["fresh_perm"].get("p_two_sided")))
    v = classify(d["control"], fresh, perm)
    if v["verdict"] != d["verdict"]:
        problems.append("verdict re-derives to %s, face says %s" % (v["verdict"], d["verdict"]))
    for key in ("turn_split", "corr_split"):
        s = median_split(periods, "turn" if key == "turn_split" else "corr60")
        old = d.get(key) or {}
        if s.get("gap_pp") != old.get("gap_pp") or s.get("p_two_sided") != old.get("p_two_sided"):
            problems.append("%s re-derives to gap=%s p=%s, face says gap=%s p=%s"
                            % (key, s.get("gap_pp"), s.get("p_two_sided"),
                               old.get("gap_pp"), old.get("p_two_sided")))
    bc = joint_cells(periods).get("best_cell") or {}
    obc = (d.get("joint_cells") or {}).get("best_cell") or {}
    if bc.get("cell") != obc.get("cell") or bc.get("p_shuffle") != obc.get("p_shuffle"):
        problems.append("joint best cell re-derives to %s/%s, face says %s/%s"
                        % (bc.get("cell"), bc.get("p_shuffle"), obc.get("cell"),
                           obc.get("p_shuffle")))
    ages = age_table(obs)
    if [a["sum_pp"] for a in ages] != [a["sum_pp"] for a in d["ages"]]:
        problems.append("age table re-derives to a different profile")
    if not d["totals"]["identity_ok"]:
        problems.append("the face itself says the per-name identity does not hold")
    ok = not problems
    print(json.dumps({"ok": ok, "problems": problems, "verdict": v["verdict"],
                      "gap_pp": fresh.get("gap_pp"),
                      "p_two_sided": perm.get("p_two_sided"),
                      "share_fresh": fresh.get("share_fresh")}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    def period(decision, turn, corr, legs_map):
        return {"decision": decision, "turn": turn, "corr60": corr, "bars": 20,
                "select_pp": 0.0, "rotate_pp": 0.0,
                "legs": {k: {"pp": v, "eq": eq, "fresh": fr, "sum": v, "bars": 20}
                         for k, (v, fr, eq) in legs_map.items()}}

    # L1 fresh split sums to the period total and the share is the money reading
    p1 = [period("d1", 1.0, 0.1, {"A": (10.0, True, True), "B": (1.0, False, True),
                                  "C": (1.0, False, True), "D": (1.0, False, True),
                                  "E": (1.0, False, True)})]
    f1 = fresh_split(p1)
    leg("L1 fresh+incumbent sums to the period", abs(f1["sum_fresh_pp"] - 10.0) < 1e-9
        and abs(f1["sum_incumbent_pp"] - 4.0) < 1e-9)
    leg("L2 share reads the money, gap reads the per-name", f1["share_fresh"] > 0.7
        and f1["gap_pp"] > 0)

    # L3 the two readings can disagree -- that is the trap this face pins
    p2 = [period("d2", 1.0, 0.1, {"A": (0.5, True, True), "B": (0.5, True, True),
                                  "C": (0.5, True, True), "D": (0.5, True, True),
                                  "E": (1.0, False, True)})]
    f2 = fresh_split(p2)
    leg("L3 share says 'fresh' while per-name says 'incumbent'",
        f2["share_fresh"] > 0.6 and f2["gap_pp"] < 0)

    # L4 non-equity names stay out of the select split
    p3 = [period("d3", 1.0, 0.1, {"A": (1.0, True, True), "B": (9.0, False, False),
                                  "C": (1.0, False, True)})]
    f3 = fresh_split(p3)
    leg("L4 rotation names never enter the select split",
        f3["n_obs_fresh"] == 1 and f3["n_obs_incumbent"] == 1)

    # L5 nothing to compare -> no gap, not a fake zero
    p4 = [period("d4", 1.0, 0.1, {"A": (1.0, True, True), "B": (1.0, True, True)})]
    f4 = fresh_split(p4)
    leg("L5 a period with no incumbents yields no gap", f4["gap_pp"] is None)
    leg("L6 the null is reported empty, not p=1", fresh_perm(p4)["p_two_sided"] is None)

    # L7 a planted per-name gap clears the within-period permutation
    rng = np.random.default_rng(4)
    planted = []
    for i in range(30):
        legs_map = {}
        for j in range(5):
            fresh = j < 2
            val = (1.0 if fresh else 0.0) + float(rng.normal(0, 0.05))
            legs_map["n%02d_%d" % (i, j)] = (val, fresh, True)
        planted.append(period("p%02d" % i, 1.0, 0.1, legs_map))
    pp = fresh_perm(planted, draws=400, seed=9)
    leg("L7 planted fresh advantage is separated", pp["p_two_sided"] <= 0.01)

    # L8 no advantage -> the null is broad
    flat_rows = []
    for i in range(30):
        legs_map = {}
        for j in range(5):
            legs_map["m%02d_%d" % (i, j)] = (float(rng.normal(0, 1.0)), j < 2, True)
        flat_rows.append(period("q%02d" % i, 1.0, 0.1, legs_map))
    pf = fresh_perm(flat_rows, draws=400, seed=9)
    leg("L8 an unplanted gap is not separated", pf["p_two_sided"] > 0.10)

    # L9 median split finds a planted turnover difference, ignores a flat one
    hi_rows = [period("h%02d" % i, 1.0, 0.1, {"A": (1.0, True, True)}) for i in range(20)]
    lo_rows = [period("l%02d" % i, 0.1, 0.1, {"A": (0.0, True, True)}) for i in range(20)]
    for p in hi_rows:
        p["select_pp"] = sum(r["pp"] for r in p["legs"].values())
    for p in lo_rows:
        p["select_pp"] = sum(r["pp"] for r in p["legs"].values())
    sp = median_split(hi_rows + lo_rows, "turn", draws=400, seed=3)
    leg("L9 median split finds a planted turnover gap",
        sp["gap_pp"] > 0.5 and sp["p_two_sided"] <= 0.01)
    for i, p in enumerate(hi_rows + lo_rows):
        p["select_pp"] = float(rng.normal(0, 1.0))
    sf = median_split(hi_rows + lo_rows, "turn", draws=400, seed=3)
    leg("L10 a flat split is not separated", sf["p_two_sided"] > 0.10)

    # L11 the 2x2 does not hand out a verdict for an eight-of-four search
    cells_rows = []
    for i in range(80):
        v = float(rng.normal(0, 1.0))
        cells_rows.append({"decision": "c%02d" % i, "turn": 1.0 if i % 2 else 0.0,
                           "corr60": 0.2 if i % 4 < 2 else 0.9, "select_pp": v, "legs": {}})
    jc = joint_cells(cells_rows, draws=300, seed=2)
    leg("L11 four cells on noise do not clear the null",
        (jc.get("best_cell") or {}).get("p_shuffle", 1.0) > P_SEP)

    # L12 age buckets are additive and keep the last bucket open
    obs = [{"pp": 1.0, "age": 5}, {"pp": 2.0, "age": 25}, {"pp": 3.0, "age": 45},
           {"pp": 4.0, "age": 500}]
    at = age_table(obs)
    leg("L12 age table is additive", abs(sum(a["sum_pp"] for a in at) - 10.0) < 1e-9)
    leg("L13 the oldest bucket is open ended", at[-1]["age_to"] is None)

    # L14 verdict states
    ctrl_ok = {"ok": True, "replay_ok": True}
    good = {"gap_pp": 1.0, "mean_fresh_pp": 1.5, "mean_incumbent_pp": 0.5,
            "n_obs_fresh": 10, "n_obs_incumbent": 10}
    leg("L14 fresh carries", classify(ctrl_ok, good, {"p_two_sided": 0.01})["verdict"]
        == "FRESH_CARRIES_ALPHA")
    bad = dict(good, gap_pp=-1.0, mean_fresh_pp=0.5, mean_incumbent_pp=1.5)
    leg("L15 incumbents carry", classify(ctrl_ok, bad, {"p_two_sided": 0.01})["verdict"]
        == "INCUMBENT_CARRIES_ALPHA")
    leg("L16 a wide p is a tie", classify(ctrl_ok, good, {"p_two_sided": 0.5})["verdict"]
        == "CHURN_AND_HOLD_TIE")
    leg("L17 control refuses",
        classify({"ok": False, "replay_ok": True}, good, {"p_two_sided": 0.01})["verdict"]
        == "CANNOT_JUDGE_CONTROL")
    leg("L18 replay refuses",
        classify({"ok": True, "replay_ok": False}, good, {"p_two_sided": 0.01})["verdict"]
        == "CANNOT_JUDGE_REPLAY")
    leg("L19 no split refuses",
        classify(ctrl_ok, {"gap_pp": None}, {"p_two_sided": None})["verdict"]
        == "CANNOT_JUDGE_NO_SPLIT")

    # L20 beta summary: a book that is exactly 1x the index reads beta 1, alpha 0
    idx = pd.date_range("2024-01-01", periods=120, freq="B")
    x = pd.Series(rng.normal(0.0004, 0.01, len(idx)), index=idx)
    df = pd.DataFrame({"r_bench": x, "net": x})
    bs = beta_summary(df)
    leg("L20 beta/alpha banner is exact", abs(bs["beta"] - 1.0) < 1e-6
        and abs(bs["alpha_ann_pp"]) < 1e-9 and abs(bs["r2"] - 1.0) < 1e-6)
    half = pd.DataFrame({"r_bench": x, "net": 0.5 * x})
    leg("L21 half the index reads beta 0.5", abs(beta_summary(half)["beta"] - 0.5) < 1e-6)

    total = len(legs)
    bad_legs = [n for n, okk in legs if not okk]
    print("selftest %d/%d PASS" % (total - len(bad_legs), total))
    for b in bad_legs:
        print("  FAIL", b)
    return 1 if bad_legs else 0


def main(argv):
    args = [a.lstrip("-") for a in argv]
    if "selftest" in args:
        return selftest()
    if "check" in args:
        return _check()
    if "md" in args:
        return write_md()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
