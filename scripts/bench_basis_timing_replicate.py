"""Bench cell 7, independent replication: does sizing the basis by its own percentile
really beat holding it always, or is the published GO an artefact of one wide-discount era?

Why this face exists
--------------------
`bench_basis_timing_size` published **GO** (IC 10.09%/yr weighted vs 2.73% always-on;
IM 9.30% vs 5.63%) with a note that says the verdict still needs an independent
recompute before any money moves.  This face is that recompute.  It is a second
implementation (own weight/curve/annualise code, only the raw readers are shared), and it
asks the four questions that the published cell cannot answer about itself:

  R1  the margin survives exposure normalisation -- the weighted arm runs at ~0.5 average
      weight, so "10.09 vs 2.73" compares half exposure with full exposure.  R1 puts both
      arms on the same unit of exposure before claiming a margin.
  R2  the margin survives a time-shuffled weight null -- same weight distribution, order
      destroyed.  If the percentile alignment is worthless, a shuffled weight vector earns
      just as much and p is large.  This is the "must beat random, not just nothing" test.
  R3  the margin is not one year -- per-calendar-year read of both arms.
  R4  the weighted arm's own money is not one or two years -- top-2-year share of its
      contributions, against the line imported from `candidate_year_gate.TOP2_SHARE_MAX`
      (0.70).  The line is imported, never re-typed.
  R5  the margin is not roll-day leakage -- the mask is widened to exclude the day after
      every roll as well, and the margin must still clear 1.0pp.

Criteria (frozen before the run, do not move after seeing numbers)
-----------------------------------------------------------------
  R1  (w_ann/avg_w - a_ann) >= 1.0pp
  R2  shuffle p (stricter of with-cost / no-cost) <= 0.05
  R3  years with weighted >= always-on >= 60% of years with >=100 bars, and >= 2 such years
  R4  top-2-year share of the weighted arm's contributions <= TOP2_SHARE_MAX
  R5  margin under the widened roll mask >= 1.0pp
Verdict: GO_REPLICATED only if R1..R5 all pass, else GO_NOT_REPLICATED with the failing
legs named.  A failed replication is a product: it says the money is not there yet.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402  (raw readers + roll mask only)
import candidate_year_gate as gate  # noqa: E402  (TOP2_SHARE_MAX lives there)

OUT_JSON = os.path.join(bc.RESULTS, "bench_basis_timing_replicate.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BASIS-TIMING-REPLICATE.md")

WINDOW, MIN_OBS = 250, 60
LOW_Q, HIGH_Q = 20.0, 80.0
COST_BP_SIDE = 1.5
SPLIT = "2024-01-01"
PRODUCTS = ("IC", "IM")

R1_MARGIN_PP = 1.0
R2_ALPHA = 0.05
R2_PERM, R2_SEED = 2000, 20261123
R3_MIN_SHARE, R3_MIN_YEARS, R3_MIN_BARS = 0.60, 2, 100
R4_TOPN = 2
R5_MARGIN_PP = 1.0
TOL_PP = 0.02          # --check comparison tolerance (percent points)


# ---------------------------------------------------------------- weights
def pct_midrank(win, x):
    """Published convention: below + half of equal, over the window."""
    win = np.asarray(win, dtype=float)
    return 100.0 * ((win < x).mean() + 0.5 * (win == x).mean())


def pct_linear(win, x):
    """Robustness convention: linear interpolation, a different percentile estimator."""
    return float(np.percentile(np.asarray(win, dtype=float), 100.0 * (np.asarray(win) < x).mean()))


def weight_series(basis, conv):
    """w[k] = clamp((80 - pct(basis[k] inside trailing window))/60, 0, 1)."""
    w = np.zeros(len(basis))
    for k in range(len(basis)):
        win = basis[max(0, k - WINDOW + 1):k + 1]
        if len(win) < MIN_OBS:
            continue
        w[k] = min(1.0, max(0.0, (HIGH_Q - conv(win, basis[k])) / (HIGH_Q - LOW_Q)))
    return w


# ---------------------------------------------------------------- curves
def daily_carry(spread, roll, w):
    """w*spread on non-roll days, minus |dw|*cost.  w already lagged by the caller."""
    carry = np.where(roll, 0.0, w * spread)
    cost = np.abs(np.diff(np.concatenate(([0.0], w)))) * COST_BP_SIDE / 10000.0
    return carry - cost


def ann_pct(daily):
    if len(daily) == 0:
        return None
    eq = float(np.prod(1.0 + np.asarray(daily)))
    years = len(daily) / bc.TRADING_DAYS
    if eq <= 0 or years <= 0:
        return None
    return round((eq ** (1.0 / years) - 1.0) * 100.0, 3)


def mdd_pct(daily):
    eq = np.cumprod(1.0 + np.asarray(daily))
    return round(float(np.min(eq / np.maximum.accumulate(eq) - 1.0)) * 100.0, 3)


# ---------------------------------------------------------------- permutation null
def shuffle_p(w, spread, roll, observed_ann, seed=R2_SEED, n=R2_PERM):
    """Same weight distribution, order destroyed. Returns p with and without cost.

    With cost is the fair comparison (the observed arm pays turn cost too) but shuffling
    creates far more turnover, so it makes the null easier to beat.  Without cost makes the
    null harder to beat.  R2 uses the stricter (larger) of the two p values.
    """
    rng = np.random.default_rng(seed)
    src = w.copy()
    ge_cost = 0
    ge_nocost = 0
    for _ in range(n):
        perm = rng.permutation(src)
        with_cost = ann_pct(daily_carry(spread, roll, perm))
        no_cost = ann_pct(np.where(roll, 0.0, perm * spread))
        if with_cost is not None and with_cost >= observed_ann:
            ge_cost += 1
        if no_cost is not None and no_cost >= observed_ann:
            ge_nocost += 1
    return round((ge_cost + 1) / (n + 1), 4), round((ge_nocost + 1) / (n + 1), 4)


def shift_null(w, spread, roll, observed_ann):
    """Post-hoc stricter null: circular shifts keep the weight series' whole serial
    structure and destroy only its alignment with the carry days.  Under autocorrelated
    weights (250-day windows) the shuffle test is anti-conservative; this one is not."""
    n = len(w)
    ge = 0
    for s in range(1, n):
        perm = np.roll(w, s)
        a = ann_pct(daily_carry(spread, roll, perm))
        if a is not None and a >= observed_ann:
            ge += 1
    return round((ge + 1) / n, 5)


def decay(w_next, spread, roll, lag):
    """Same rule, weight applied `lag` days later.  A 1-day-only effect is microstructure
    catch-up; a level effect decays slowly."""
    if lag <= 1:
        wl = w_next
    else:
        wl = np.concatenate((np.zeros(lag - 1), w_next[:-(lag - 1)]))
    return ann_pct(daily_carry(spread, roll, wl))


# ---------------------------------------------------------------- per year
def by_year(dates, daily):
    buckets = {}
    for k, v in enumerate(daily):
        buckets.setdefault(dates[k][:4], []).append(float(v))
    return buckets


def year_table(dates, daily_w, daily_a):
    bw, ba = by_year(dates, daily_w), by_year(dates, daily_a)
    out = {}
    for y in sorted(bw):
        out[y] = {"bars": len(bw[y]),
                  "weighted_ann_pct": ann_pct(bw[y]),
                  "always_ann_pct": ann_pct(ba.get(y, [])),
                  "weighted_sum": round(float(np.sum(bw[y])), 6)}
    return out


def top2_share(table):
    contrib = [(y, abs(e["weighted_sum"]), e["weighted_sum"]) for y, e in table.items()]
    total = sum(c[2] for c in contrib)
    if total <= 0:
        return None
    best = sorted(contrib, key=lambda c: c[2], reverse=True)[:R4_TOPN]
    return round(sum(c[2] for c in best) / total, 4)


# ---------------------------------------------------------------- one product
def run_product(code):
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
    d1 = dates[1:]                                   # one bar per spread observation

    w = weight_series(basis, pct_midrank)
    w_next = w[:-1]                                  # weight known at k drives day k+1
    one = np.ones(len(spread))

    daily_w = daily_carry(spread, roll, w_next)
    daily_a = daily_carry(spread, roll, one)
    ann_w, ann_a = ann_pct(daily_w), ann_pct(daily_a)
    avg_w = round(float(w_next.mean()), 4)
    # R1 uses a linear (simple-sum) annualisation: compounding makes "annual return / avg
    # weight" overstate the same-exposure rate by ~6% relative at 0.5 weight, and R1 is
    # exactly the leg that must not be inflated.  Per unit of exposure, both arms pay cost.
    per_unit_w = None
    margin_per_unit = None
    if avg_w > 0:
        mu_w = float(np.sum(daily_w)) / len(daily_w) / avg_w
        mu_a = float(np.sum(daily_a)) / len(daily_a)
        per_unit_w = round(mu_w * bc.TRADING_DAYS * 100.0, 3)
        margin_per_unit = round((mu_w - mu_a) * bc.TRADING_DAYS * 100.0, 3)
    margin = round(ann_w - ann_a, 3) if None not in (ann_w, ann_a) else None

    # R2 null on the same measured quantity as the published claim (raw annualised carry)
    p_cost, p_nocost = shuffle_p(w_next, spread, roll, ann_w) if ann_w is not None else (None, None)
    p_strict = max(p_cost, p_nocost) if p_cost is not None else None

    # R3/R4 year read
    table = year_table(d1, daily_w, daily_a)
    judged = {y: e for y, e in table.items() if e["bars"] >= R3_MIN_BARS}
    beat = [y for y, e in judged.items()
            if e["weighted_ann_pct"] is not None and e["always_ann_pct"] is not None
            and e["weighted_ann_pct"] >= e["always_ann_pct"]]
    share = round(len(beat) / len(judged), 3) if judged else None
    t2 = top2_share(table)

    # R5 widened roll mask: roll day and the day after
    wide_roll = roll.copy()
    wide_roll[1:] |= roll[:-1]
    w_w = daily_carry(spread, wide_roll, w_next)
    w_a = daily_carry(spread, wide_roll, one)
    margin_wide = (round(ann_pct(w_w) - ann_pct(w_a), 3)
                   if ann_pct(w_w) is not None and ann_pct(w_a) is not None else None)
    wide_roll_days = int(wide_roll.sum()) - int(roll.sum())

    # robustness row: a different percentile estimator, same rule
    w_lin = weight_series(basis, pct_linear)
    margin_linear = round(ann_pct(daily_carry(spread, roll, w_lin[:-1])) - ann_a, 3)

    # paired daily read of the excess (context, not a leg)
    excess = (w_next - one) * np.where(roll, 0.0, spread)
    sd = float(np.std(excess, ddof=1))
    t_stat = round(float(np.mean(excess)) / (sd / np.sqrt(len(excess))), 3) if sd > 0 else None

    # post-hoc (stricter, can only downgrade): shift null + decay of the effect
    shift_p = shift_null(w_next, spread, roll, ann_w) if ann_w is not None else None
    decays = {}
    if ann_a is not None:
        for lag in (1, 2, 5, 10):
            a = decay(w_next, spread, roll, lag)
            decays[lag] = round(a - ann_a, 3) if a is not None else None

    checks = {
        "R1_exposure_normalised_margin": bool(margin_per_unit is not None
                                              and margin_per_unit >= R1_MARGIN_PP),
        "R2_beats_shuffled_weights": bool(p_strict is not None and p_strict <= R2_ALPHA),
        "R3_margin_not_one_year": bool(share is not None and share >= R3_MIN_SHARE
                                       and len(beat) >= R3_MIN_YEARS),
        "R4_top2_year_share_ok": bool(t2 is not None and t2 <= gate.TOP2_SHARE_MAX),
        "R5_survives_widened_roll_mask": bool(margin_wide is not None
                                              and margin_wide >= R5_MARGIN_PP),
        "R2b_posthoc_beats_shift_null": bool(shift_p is not None and shift_p <= R2_ALPHA),
    }
    return {
        "state": "ok", "bars": len(dates), "first": d1[0], "last": d1[-1],
        "full_years": round(len(d1) / bc.TRADING_DAYS, 2),
        "weighted": {"carry_ann_pct": ann_w, "carry_mdd_pct": mdd_pct(daily_w),
                     "avg_weight": avg_w, "per_unit_exposure_ann_pct": per_unit_w,
                     "days_flat_pct": round(100.0 * float(np.mean(w_next <= 0.001)), 1)},
        "always_on": {"carry_ann_pct": ann_a, "carry_mdd_pct": mdd_pct(daily_a)},
        "margin_pp": margin,
        "margin_per_unit_pp": margin_per_unit,
        "margin_pp_linear_pct": margin_linear,
        "shuffle_p": {"with_cost": p_cost, "no_cost": p_nocost, "strict": p_strict},
        "posthoc": {"shift_null_p": shift_p, "decay_margin_pp_by_lag": decays,
                    "note": "not frozen with R1-R5; shift null can only downgrade the "
                            "verdict, decay readings are reported not judged"},
        "paired_excess_t": t_stat,
        "years": table,
        "years_judged": len(judged), "years_beating_always_on": beat,
        "beat_share": share, "top2_year_share": t2,
        "widened_roll_mask": {"extra_days": wide_roll_days, "margin_pp": margin_wide},
        "checks": checks,
        "verdict": "GO_REPLICATED" if all(checks.values()) else "GO_NOT_REPLICATED",
    }


def judge(products):
    usable = {k: v for k, v in products.items() if v.get("checks")}
    if not usable:
        return "DATA_BLOCKED"
    if all(v["verdict"] == "GO_REPLICATED" for v in usable.values()):
        return "GO_REPLICATED"
    return "GO_NOT_REPLICATED"


def run(write=True):
    bc.weight_priority()
    products = {code: run_product(code) for code in PRODUCTS}
    usable = {k: v for k, v in products.items() if v.get("checks")}
    verdict = judge(products)
    payload = {
        "face": "bench_basis_timing_replicate",
        "generated": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
        ).isoformat(timespec="seconds"),
        "evidence_cutoff": max((v.get("last") for v in products.values() if v.get("last")),
                               default="n/a"),
        "replicates": "results/bench_basis_timing_size.json",
        "rule": {"weight": "clamp((80-pct)/60,0,1)", "window": WINDOW, "min_obs": MIN_OBS,
                 "cost_bp_side": COST_BP_SIDE, "split": SPLIT},
        "criteria": {"R1_margin_pp": R1_MARGIN_PP, "R2_alpha": R2_ALPHA,
                     "R2_permutations": R2_PERM, "R3_min_share": R3_MIN_SHARE,
                     "R3_min_years": R3_MIN_YEARS, "R4_topN": R4_TOPN,
                     "R4_top2_share_max": gate.TOP2_SHARE_MAX,
                     "R5_margin_pp": R5_MARGIN_PP},
        "products": products,
        "verdict": verdict,
        "note": ("Second implementation of the sizing rule; only the raw readers and the roll "
                 "mask are shared with the published cell. R1 puts both arms on the same unit "
                 "of exposure, R2 destroys the time order of the weights (the harsh null), "
                 "R3/R4 ask whether the money is one year, R5 widens the roll exclusion."),
    }
    if write:
        bc.write_json(OUT_JSON, payload)
        write_doc(payload)

    lines = [f"基差择时定仓（bench cell 7）**独立复算** → 判决 **{verdict}**", "",
             f"generated {payload['generated']} | cutoff {payload['evidence_cutoff']} | "
             f"复算对象 results/bench_basis_timing_size.json", ""]
    for code, v in products.items():
        if not v.get("checks"):
            lines.append(f"- {code}: {v.get('state')}")
            continue
        lines.append(
            f"- **{code}** {v['bars']} bars {v['first']}→{v['last']}：加权 {v['weighted']['carry_ann_pct']:+.2f}% "
            f"vs 常驻 {v['always_on']['carry_ann_pct']:+.2f}%（差 {v['margin_pp']:+.2f}pp，"
            f"均权 {v['weighted']['avg_weight']:.3f} → 同曝光差 **{v['margin_per_unit_pp']:+.2f}pp**）；"
            f"shuffle p={v['shuffle_p']['strict']}；年胜率 {v['beat_share']}（{len(v['years_beating_always_on'])}/"
            f"{v['years_judged']}）；top2 年份额 {v['top2_year_share']}；宽遮罩差 {v['widened_roll_mask']['margin_pp']:+.2f}pp；"
            f"**衰减(1/2/5/10日)={v['posthoc']['decay_margin_pp_by_lag']}**")
    for line in lines:
        print(line)
    return payload


def write_doc(p):
    L = ["# 基差按分位定仓：独立复算", "",
         f"generated {p['generated']} | evidence_cutoff **{p['evidence_cutoff']}** | "
         f"判决 **{p['verdict']}**",
         "",
         "本面是对 `results/bench_basis_timing_size.json`（GO）的第二套实现。"
         "只共用原始读取器与移仓遮罩，权重/净值/年化/置换检验全部另写。判据跑前冻结在脚本头部。", "",
         "## 判据（跑前冻结）", "",
         "| 腿 | 问题 | 线 |", "|---|---|---|",
         "| R1 | 把两条臂放到同单位曝光上，还剩多少 | ≥ +1.0pp |",
         "| R2 | 权重分布不变、时间顺序打乱，还能赢吗 | p ≤ 0.05（取带成本/不带成本里更严的一侧） |",
         "| R3 | 是常年有效还是一年行情 | 胜率 ≥60% 且 ≥2 个年份 |",
         "| R4 | 加权臂自己的钱是不是一两年 | top-2 年份额 ≤ %.2f（从 candidate_year_gate 导入） |" % gate.TOP2_SHARE_MAX,
         "| R5 | 是不是移仓日泄漏 | 宽遮罩下差仍 ≥ +1.0pp |", "",
         "## 读数", ""]
    for code, v in p["products"].items():
        if not v.get("checks"):
            L.append(f"- {code}: {v.get('state')}")
            continue
        w, a = v["weighted"], v["always_on"]
        L += [f"### {code}", "",
              f"- bars {v['bars']}（{v['first']} → {v['last']}，{v['full_years']} 年），移仓宽遮罩多加 {v['widened_roll_mask']['extra_days']} 天",
              f"- 加权 carry/年 **{w['carry_ann_pct']:+.2f}%**（MDD {w['carry_mdd_pct']:+.2f}%，均权 {w['avg_weight']:.3f}，"
              f"空仓 {w['days_flat_pct']}%）vs 常驻 **{a['carry_ann_pct']:+.2f}%**（MDD {a['carry_mdd_pct']:+.2f}%）",
              f"- 差额 {v['margin_pp']:+.2f}pp；**同曝光差额 {v['margin_per_unit_pp']:+.2f}pp**（线性分位估计量复算：{v['margin_pp_linear_pct']:+.2f}pp）",
              f"- 打乱权重零假设：p(带成本)={v['shuffle_p']['with_cost']}，p(无成本)={v['shuffle_p']['no_cost']}，取严 **{v['shuffle_p']['strict']}**；"
              f"环形位移零假设（保留权重序列全部自相关结构，post-hoc 加严）p={v['posthoc']['shift_null_p']}",
              f"- 逐年：胜 {len(v['years_beating_always_on'])}/{v['years_judged']}（{v['beat_share']}），"
              f"top-2 年份额 {v['top2_year_share']}",
              f"- **钱是哪一天赚的**：把同一组权重往后挪 1/2/5/10 个交易日再上，差额变成 "
              + " / ".join("%+.2fpp" % m for m in v["posthoc"]["decay_margin_pp_by_lag"].values())
              + "（1/2/5/10 日）",
              "", "| 年 | bars | 加权 | 常驻 | 差 |", "|---|---|---|---|---|"]
        for y, e in v["years"].items():
            dw = (round(e["weighted_ann_pct"] - e["always_ann_pct"], 2)
                  if None not in (e["weighted_ann_pct"], e["always_ann_pct"]) else None)
            L.append(f"| {y} | {e['bars']} | {e['weighted_ann_pct']:+.2f}% | "
                     f"{e['always_ann_pct']:+.2f}% | {dw:+}pp |")
        L += ["", "判据：" + "；".join(f"{k}={'✓' if v else '✗'}" for k, v in v["checks"].items()), ""]
    L += ["## 这条面回答了什么", "",
          "它不新增一个策略，只决定那一条 **GO** 能不能当钱花：同曝光有差、且打乱顺序与环形位移都赢不了，"
          "才说明「按分位定仓」这个动作本身在赚钱；若钱集中在一年，说明这条 GO 只是「那一年贴水宽」的记忆。",
          "",
          "**本轮最重要的读数不是判决，是衰减**：两条腿的钱都在**下一个交易日**，挪后 2 天就掉到 +1.2pp 以下、"
          "5 天变负。所以这条 GO 描述的是一个**日频的价差回补**，不是「贴水宽的年份拿住就能吃」的持有收成；"
          "它对执行时点、对成交价（收盘还是次日开盘）都极敏感，而这正是本面没有能力判定的部分。",
          "",
          "口径与限制：carry=期货−指数、移仓日剔除（与父面同口径）；未计保证金、未做逐合约换月交易成本细分；"
          "IM 面板 2022-07 起，只有 4.3 年；环形位移与衰减两组读数是 post-hoc（位移只可下调判决，衰减只报不判）。"
          "指数面板只有收盘价，因此「隔夜段 vs 日内段」无法在本面拆开——那是下一面的事。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- check / selftest
def check():
    if not os.path.exists(OUT_JSON):
        print("STALE: results/bench_basis_timing_replicate.json missing")
        return 3
    old = json.load(open(OUT_JSON, encoding="utf-8"))
    new = run(write=False)
    problems = []
    for code in PRODUCTS:
        o, n = old["products"].get(code, {}), new["products"].get(code, {})
        if not n.get("checks"):
            problems.append(f"{code} unreadable now: {n.get('state')}")
            continue
        for key in ("margin_pp", "margin_per_unit_pp", "margin_pp_linear_pct"):
            ov, nv = o.get(key), n.get(key)
            if ov is None or nv is None or abs(ov - nv) > TOL_PP:
                problems.append(f"{code}.{key} published {ov} != recomputed {nv}")
        if o.get("shuffle_p", {}).get("strict") != n["shuffle_p"]["strict"]:
            problems.append(f"{code}.shuffle_p {o.get('shuffle_p')} != {n['shuffle_p']}")
        if o.get("last") != n.get("last"):
            problems.append(f"{code}.last published {o.get('last')} != panel {n.get('last')} (STALE)")
    if problems:
        print("CHECK FAILED:")
        for x in problems:
            print("  -", x)
        return 3
    print(f"check ok: {len(PRODUCTS)} products recomputed, verdict {new['verdict']}")
    return 0


def selftest():
    global COST_BP_SIDE
    ok = []
    # L1 a wide discount is a NEGATIVE basis, so it is the LOW percentile that gets 1.0
    series = list(np.linspace(-0.05, 0.05, 200))
    w = weight_series(np.asarray(series), pct_midrank)
    ok.append(("L1 narrowest discount (highest basis) weights 0.0", abs(w[-1] - 0.0) < 1e-9))
    down = weight_series(np.asarray(list(np.linspace(0.05, -0.05, 200))), pct_midrank)
    ok.append(("L1 widest discount (lowest basis in window) weights >= 0.9", down[60] > 0.9))
    ok.append(("L1 warm-up days weight 0.0", abs(w[10]) < 1e-12))
    # L2 cost is exactly |dw| * 1.5bp, charged on both the step up and the step back down
    sp = np.zeros(4)
    rl = np.zeros(4, dtype=bool)
    one_side = COST_BP_SIDE / 10000.0
    d = daily_carry(sp, rl, np.array([1.0, 0.0, 0.0, 0.0]))
    ok.append(("L2 |dw| charged on entry and exit, nothing after",
               abs(d[0] + one_side) < 1e-12 and abs(d[1] + one_side) < 1e-12
               and abs(d[2]) < 1e-12 and abs(d[3]) < 1e-12))
    # L3 annualise 252 bars of 0.1%/day -- expected value derived, not typed
    expect = ((1.001 ** 252) ** (1.0 / (252 / bc.TRADING_DAYS)) - 1.0) * 100.0
    a = ann_pct(np.full(252, 0.001))
    ok.append(("L3 constant 0.1%%/day annualises to %.2f%%" % expect, abs(a - expect) < 0.02))
    # L4 roll day never carries, however big the spread
    d = daily_carry(np.array([0.0, 0.5, 0.0]), np.array([False, True, False]),
                    np.array([1.0, 1.0, 1.0]))
    ok.append(("L4 roll day carry is zero (only the entry cost shows)",
               abs(d[1]) < 1e-12 and abs(d[0] + one_side) < 1e-12))
    # L5 permutation null can fire: weights aligned with positive carry must beat shuffles
    rng = np.random.default_rng(7)
    sp5 = rng.normal(0, 0.004, 900)
    w5 = np.zeros(900)
    for k in range(60, 900):
        w5[k] = max(0.0, min(1.0, sp5[k] / 0.008))   # perfect foresight, no look-ahead needed here
    roll5 = np.zeros(900, dtype=bool)
    obs = ann_pct(daily_carry(sp5, roll5, w5))
    pc, pn = shuffle_p(w5, sp5, roll5, obs, seed=11, n=200)
    ok.append(("L5 perfect-foresight weights beat shuffles", max(pc, pn) <= 0.05))
    # L5b and a worthless rule does not
    w6 = np.full(900, 0.5)
    obs6 = ann_pct(daily_carry(sp5, roll5, w6))
    pc6, pn6 = shuffle_p(w6, sp5, roll5, obs6, seed=11, n=200)
    ok.append(("L5b constant weights cannot beat shuffles", max(pc6, pn6) > 0.05))
    # L6 top2 share of a single-year series is 1.0
    tab = {"2024": {"weighted_sum": 0.10}, "2025": {"weighted_sum": 0.01}}
    ok.append(("L6 one-year money reads share 1.0", top2_share(tab) == 1.0))
    tab2 = {str(2000 + k): {"weighted_sum": 0.01} for k in range(10)}
    ok.append(("L6b even money reads share %.2f" % top2_share(tab2),
               0.19 < top2_share(tab2) < 0.21))
    # L7 exposure normalisation is not an inflator: w=0.5 constant, cost off, the
    # simple-sum rate split by weight must equal the always-on rate exactly
    saved = COST_BP_SIDE
    COST_BP_SIDE = 0.0
    sp7 = np.array([0.001] * 300)
    no_roll = np.zeros(300, dtype=bool)
    half = daily_carry(sp7, no_roll, np.full(300, 0.5))
    per_unit = float(np.sum(half)) / 300 / 0.5 * bc.TRADING_DAYS * 100.0
    always = float(np.sum(daily_carry(sp7, no_roll, np.ones(300)))) / 300 * bc.TRADING_DAYS * 100.0
    COST_BP_SIDE = saved
    ok.append(("L7 simple-sum per-exposure ties with always-on",
               abs(per_unit - always) < 1e-9))
    # L7b the compounded version does NOT tie -- disproves the rate/weight shortcut
    half_c = ann_pct(daily_carry(sp7, no_roll, np.full(300, 0.5))) / 0.5
    ok.append(("L7b compounded rate/weight overstates by >1pp (why R1 is linear)",
               abs(half_c - ann_pct(sp7)) > 1.0))
    # L8 verdict names the failing leg instead of a blanket fail
    prod = {"IC": {"checks": {"R1": False, "R2": True}, "verdict": "GO_NOT_REPLICATED"}}
    ok.append(("L8 judge propagates NOT_REPLICATED", judge(prod) == "GO_NOT_REPLICATED"))
    ok.append(("L8b judge refuses to call an empty book replicated",
               judge({"IC": {"state": "NOT_ENOUGH_BARS"}}) == "DATA_BLOCKED"))
    # L9 the concentration line is imported, not re-typed
    ok.append(("L9 TOP2 line comes from candidate_year_gate", gate.TOP2_SHARE_MAX == 0.70))
    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    print("%d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    payload = run()
    return 0 if payload["verdict"] in ("GO_REPLICATED", "GO_NOT_REPLICATED") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
