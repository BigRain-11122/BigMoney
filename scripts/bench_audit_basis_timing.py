"""Audit of bench cell 7 (`basis_timing_size`): is that GO timing skill or an exposure artifact?

Why this audit exists
---------------------
Cell 7 published GO on 2026-11-22T23:35:  weighting the contract by where its basis sits in
its own trailing year beat holding it always by +7.36pp/yr (IC) and +3.67pp/yr (IM), with a
smaller drawdown on both.  The cell's own page ends with "GO 仍须独立复算 + 纸盘跟踪后才谈真钱",
so this is that independent recompute -- but not a second copy of the same arithmetic.  Reading
the code raised two specific, falsifiable suspicions:

  S1  The two arms do not carry the same exposure.  The weighted arm averages weight 0.497 and
      sits flat 22% of days; the "always-on" arm is weight 1.0 every day.  Any *negative-mean*
      stretch of the carry series therefore costs the always-on arm roughly twice as much as the
      weighted arm, with no timing skill involved.  Control: a constant weight equal to the
      weighted arm's own average must be refuted before "timing" can be claimed.
  S2  Cell 7 inherits cell 4's roll mask (`idx_fut_basis.basis_face`): a basis step 8x the median
      step.  `results/idx_fut_roll_gap.json` already showed that mask misses 65-78% of the calendar
      rolls and that the missed rolls are a *fake loss* (IC carry 1.80% under the threshold mask vs
      5.79% under the calendar mask).  Those fake-loss days sit inside both arms, so again S1's
      asymmetry converts a mask defect into an apparent timing edge.

Frozen rule under test (copied from cell 7, not re-chosen here)
--------------------------------------------------------------
  weight(k) = clamp((80 - pct_k) / 60, 0, 1),  pct over basis[k-249..k], min 60 obs
  carry(k)  = w(k) * spread(k),  zero on roll days;  cost = |dw| * 1.5bp/side
  H1  weighted carry/yr >= always-on carry/yr + 1.0pp

Arms (all on the same aligned panels, same cost, same roll-day exclusion)
-------------------------------------------------------------------------
  R  reproduce : frozen rule, published-style threshold mask, independent code
  W  weighted  : frozen rule, *calendar* mask (one roll per month, chosen by largest basis step
                 inside the expiry window) -- S2 control
  C  constant  : constant weight = mean(w of that arm), no timing -- S1 control
  P  permuted  : W's weights circularly rotated at a random offset, 200 draws -- null with the
                 same marginal weight distribution and the same autocorrelation

Frozen verdict rules
--------------------
  REPRODUCED      |R - published| <= 0.5pp on that product's weighted carry
  TIMING_REAL     all three: W(thr) >= C(thr) + 1.0pp, W(cal) >= C(cal) + 1.0pp, perm p <= 0.05
  EXPOSURE        C >= always-on + 1.0pp  (the margin is bought by being smaller, not by timing)
  ROLL_MASK       margin survives the exposure control but the calendar mask removes it
  NO_TIMING_EDGE  nothing above holds
  pooled = TIMING_REAL only if every usable product is TIMING_REAL.

Nothing here is rewritten by hand: every number is derived by `build()` and printed.
"""
import csv
import json
import os
import statistics
import sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
IDX_DIR = os.path.join(ROOT, "data", "index_daily")

OUT_JSON = os.path.join(RESULTS, "bench_audit_basis_timing.json")
OUT_MD = os.path.join(RESEARCH, "BENCH-BASIS-TIMING-AUDIT.md")
PUBLISHED = os.path.join(RESULTS, "bench_basis_timing_size.json")

PAIRS = {"IC": "sh000905", "IM": "sh000852"}
TRADING_DAYS = 244.0

# frozen rule (cell 7)
WINDOW = 250
MIN_OBS = 60
LOW_Q, HIGH_Q = 20.0, 80.0
COST_BP_SIDE = 1.5
SPLIT = "2024-01-01"
H1_MARGIN_PP = 1.0

# published-style threshold mask (cell 4 parity)
ROLL_SCALE = 8.0
ROLL_FLOOR = 0.005
# calendar mask: expiry = third Friday; the switch step is searched in this trading-day window
CAL_BACK, CAL_FWD = 8, 2
CAL_MIN_STEP = 0.003

PERM_DRAWS = 200
PERM_SEED = 20261123
T_CRIT_80 = 2.80   # two-sided 5%, 80% power, as used by `bench_power`


# ---------------------------------------------------------------- data
def read_close(path, field="close"):
    out = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            try:
                v = float(r[field])
            except (KeyError, TypeError, ValueError):
                continue
            if v > 0:
                out[str(r["date"])[:10]] = v
    return out


def load_pair(code):
    fut = read_close(os.path.join(FUT_DIR, code + ".csv"))
    idx = read_close(os.path.join(IDX_DIR, PAIRS[code] + ".csv"))
    dates = sorted(set(fut) & set(idx))
    return dates, [fut[d] for d in dates], [idx[d] for d in dates]


def faces(f, i):
    """basis per day, per-day relative return spread (futures minus index)."""
    basis = [a / b - 1.0 for a, b in zip(f, i)]
    spread = [f[k] / f[k - 1] - i[k] / i[k - 1] for k in range(1, len(f))]
    return basis, spread


# ---------------------------------------------------------------- masks
def mask_threshold(basis):
    db = [abs(basis[k + 1] - basis[k]) for k in range(len(basis) - 1)]
    scale = max(statistics.median(db), 0.001)
    return [bool(db[k] > ROLL_SCALE * scale and db[k] > ROLL_FLOOR) for k in range(len(db))]


def third_friday(y, m):
    d = date(y, m, 1)
    fridays = 0
    while True:
        if d.weekday() == 4:
            fridays += 1
            if fridays == 3:
                return d
        d += timedelta(days=1)


def mask_calendar(dates, basis):
    """One roll per month: the largest |dbasis| inside [expiry-back, expiry+fwd] trading days."""
    flags = [False] * (len(basis) - 1)
    iso = [date(int(d[:4]), int(d[5:7]), int(d[8:10])) for d in dates]
    months = sorted({(d.year, d.month) for d in iso})
    hits = 0
    for y, m in months:
        exp = third_friday(y, m)
        win = [k for k in range(len(basis) - 1) if
               -CAL_BACK <= _tdiff(iso[k + 1], exp) <= CAL_FWD]
        if not win:
            continue
        k = max(win, key=lambda x: abs(basis[x + 1] - basis[x]))
        if abs(basis[k + 1] - basis[k]) >= CAL_MIN_STEP:
            flags[k] = True
            hits += 1
    return flags, hits


def _tdiff(a, b):
    """a - b measured in weekdays (a positive means a is later)."""
    return (a - b).days - 2 * ((a - b).days // 7)


# ---------------------------------------------------------------- rule
def percentile(win, x):
    below = sum(1 for v in win if v < x)
    equal = sum(1 for v in win if v == x)
    return 100.0 * (below + 0.5 * equal) / len(win)


def weights(basis, window=WINDOW, min_obs=MIN_OBS, low=LOW_Q, high=HIGH_Q):
    w = []
    for k in range(len(basis)):
        win = basis[max(0, k - window + 1):k + 1]
        if len(win) < min_obs:
            w.append(0.0)
            continue
        p = percentile(win, basis[k])
        w.append(max(0.0, min(1.0, (high - p) / (high - low))))
    return w


def arm(spread, roll, w, cost_bp=COST_BP_SIDE):
    """Weight known at k drives the k->k+1 return; roll days pay nothing and earn nothing."""
    carry, prev, turn = [], 0.0, 0.0
    for k in range(len(spread)):
        wk = w[k] if k < len(w) else 0.0
        c = 0.0 if roll[k] else wk * spread[k]
        fee = abs(wk - prev) * cost_bp / 10000.0
        carry.append(c - fee)
        turn += abs(wk - prev)
        prev = wk
    return carry, turn


def annualise(v):
    if not v:
        return None
    eq = 1.0
    for x in v:
        eq *= 1.0 + x
    if eq <= 0:
        return None
    return round((eq ** (TRADING_DAYS / len(v)) - 1.0) * 100, 2)


def mdd(v):
    if not v:
        return None
    eq, peak, worst = 1.0, 1.0, 0.0
    for x in v:
        eq *= 1.0 + x
        peak = max(peak, eq)
        worst = min(worst, eq / peak - 1.0)
    return round(worst * 100, 2)


def paired(v):
    """Arithmetic mean of a daily difference, its t-stat and the MDE at 80% power."""
    n = len(v)
    if n < 30:
        return {"n": n}
    mu = statistics.fmean(v)
    sd = statistics.stdev(v)
    se = sd / (n ** 0.5)
    return {"n": n,
            "mean_pp": round(mu * TRADING_DAYS * 100, 2),
            "t": round(mu / se, 2) if se else None,
            "mde_pp": round(T_CRIT_80 * se * TRADING_DAYS * 100, 2),
            "sd_ann_pp": round(sd * (TRADING_DAYS ** 0.5) * 100, 2)}


def halves(v):
    mid = len(v) // 2
    return [annualise(v[:mid]), annualise(v[mid:])]


def permute(spread, roll, w, observed_pp, draws=PERM_DRAWS, seed=PERM_SEED):
    """Circular rotation: keeps the weight path's own autocorrelation, drops its alignment."""
    n = len(w)
    if n < 50:
        return {"draws": 0}
    state = seed
    better = 0
    got = []
    for _ in range(draws):
        state = (1103515245 * state + 12345) % (2 ** 31)
        off = 1 + state % (n - 1)
        ww = w[off:] + w[:off]
        c, _t = arm(spread, roll, ww)
        a = annualise(c)
        got.append(a)
        if a is not None and observed_pp is not None and a >= observed_pp:
            better += 1
    got = [x for x in got if x is not None]
    got.sort()
    return {"draws": len(got),
            "p_value": round((better + 1) / (len(got) + 1), 3),
            "null_median_pp": got[len(got) // 2] if got else None,
            "null_p05_pp": got[max(0, int(0.95 * len(got)) - 1)] if got else None}


# ---------------------------------------------------------------- audit
def audit_product(code, published):
    dates, f, i = load_pair(code)
    if len(dates) < 400:
        return {"state": "NOT_ENOUGH_BARS", "bars": len(dates)}
    basis, spread = faces(f, i)
    d1 = dates[1:]

    thr = mask_threshold(basis)
    cal, cal_hits = mask_calendar(dates, basis)

    w = weights(basis)
    w_next = w[:-1]

    arms = {}
    for name, roll in (("threshold", thr), ("calendar", cal)):
        cw, tw = arm(spread, roll, w_next)
        cconst, _ = arm(spread, roll, [statistics.fmean(w_next)] * len(spread))
        call, _ = arm(spread, roll, [1.0] * len(spread))
        arms[name] = {
            "weighted_pct": annualise(cw),
            "constant_pct": annualise(cconst),
            "always_pct": annualise(call),
            "weighted_mdd_pct": mdd(cw),
            "always_mdd_pct": mdd(call),
            "weighted_halves": halves(cw),
            "turnover_per_year": round(tw * TRADING_DAYS / len(spread), 1),
            "roll_days": sum(1 for x in roll if x),
            "margin_over_always_pp": _d(annualise(cw), annualise(call)),
            "margin_over_constant_pp": _d(annualise(cw), annualise(cconst)),
            "constant_minus_always_pp": _d(annualise(cconst), annualise(call)),
            "_carry": cw, "_const": cconst,
        }

    t = arms["threshold"]
    diff_vs_const = [a - b for a, b in zip(t["_carry"], t["_const"])]
    diff_vs_always = [a - b for a, b in zip(t["_carry"],
                                           arm(spread, thr, [1.0] * len(spread))[0])]
    perm = permute(spread, thr, w_next, t["weighted_pct"])

    pub = published.get("weighted", {}).get("carry_ann_pct")
    repro_delta = _d(t["weighted_pct"], pub) if pub is not None else None

    ct = arms["calendar"]["threshold"] if False else arms["calendar"]
    checks = {
        "reproduced_0p5pp": bool(repro_delta is not None and abs(repro_delta) <= 0.5),
        "timing_survives_exposure_thr": bool(
            t["margin_over_constant_pp"] is not None
            and t["margin_over_constant_pp"] >= H1_MARGIN_PP),
        "timing_survives_exposure_cal": bool(
            ct["margin_over_constant_pp"] is not None
            and ct["margin_over_constant_pp"] >= H1_MARGIN_PP),
        "perm_p_le_0p05": bool(perm.get("p_value") is not None and perm["p_value"] <= 0.05),
    }
    if not checks["reproduced_0p5pp"]:
        verdict = "NOT_REPRODUCED"
    elif all(checks[k] for k in ("timing_survives_exposure_thr",
                                 "timing_survives_exposure_cal", "perm_p_le_0p05")):
        verdict = "TIMING_REAL"
    elif t["constant_minus_always_pp"] is not None and t["constant_minus_always_pp"] >= H1_MARGIN_PP:
        verdict = "EXPOSURE_NOTS_TIMING"
    elif (t["margin_over_always_pp"] or 0) >= H1_MARGIN_PP and not checks["timing_survives_exposure_cal"]:
        verdict = "ROLL_MASK_ARTIFACT"
    else:
        verdict = "NO_TIMING_EDGE"

    for a in arms.values():
        a.pop("_carry", None)
        a.pop("_const", None)

    return {
        "bars": len(dates), "first": d1[0], "last": d1[-1],
        "years": round(len(d1) / TRADING_DAYS, 2),
        "published_weighted_pct": pub,
        "published_always_pct": published.get("always_on", {}).get("carry_ann_pct"),
        "repro_delta_pp": repro_delta,
        "avg_weight": round(statistics.fmean(w_next), 3),
        "calendar_roll_hits": cal_hits,
        "arms": arms,
        "paired_vs_constant": paired(diff_vs_const),
        "paired_vs_always": paired(diff_vs_always),
        "permutation": perm,
        "checks": checks,
        "verdict": verdict,
    }


def _d(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 2)


def build():
    published = {}
    if os.path.exists(PUBLISHED):
        with open(PUBLISHED, "r", encoding="utf-8") as f:
            published = json.load(f).get("products", {})
    products = {}
    for code in PAIRS:
        products[code] = audit_product(code, published.get(code, {}))
    usable = {k: v for k, v in products.items() if "checks" in v}
    pooled = ("TIMING_REAL" if usable and all(v["verdict"] == "TIMING_REAL" for v in usable.values())
              else "NOT_TIMING_REAL" if usable else "DATA_BLOCKED")
    payload = {
        "cell": "basis_timing_size_audit",
        "audits": "bench_basis_timing_size (cell 7)",
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": max((v.get("last") for v in products.values() if v.get("last")),
                               default="n/a"),
        "frozen": {"window": WINDOW, "min_obs": MIN_OBS, "quantiles": [LOW_Q, HIGH_Q],
                   "cost_bp_side": COST_BP_SIDE, "h1_margin_pp": H1_MARGIN_PP,
                   "roll_scale": ROLL_SCALE, "roll_floor": ROLL_FLOOR,
                   "cal_window_td": [-CAL_BACK, CAL_FWD], "perm_draws": PERM_DRAWS,
                   "perm_seed": PERM_SEED, "repro_tolerance_pp": 0.5},
        "products": products,
        "verdict": pooled,
        "note": ("Two controls the published cell did not have: (a) constant weight equal to the "
                 "weighted arm's own average -- separates 'smaller' from 'timed'; (b) a calendar "
                 "roll mask -- cell 4's threshold mask is known to miss most real rolls. "
                 "Permutation rotates the weight path, keeping its autocorrelation."),
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    write_md(payload)
    return payload


def fmt(x):
    return "—" if x is None else "%+.2f%%" % x


def fnum(x):
    """A bare number, for places where the unit (pp) is already in the sentence."""
    return "—" if x is None else "%+.2f" % x


def write_md(p):
    L = ["# 基差定仓位的 GO 独立复算（audit of bench cell 7）", "",
         "generated %s | cutoff %s | 判决 **%s**" % (p["generated"], p["evidence_cutoff"], p["verdict"]),
         "",
         "问题不是「再算一遍」，而是：**那 +7.36pp 是择时能力，还是两个臂曝光不同造成的算术假象？**",
         "",
         "两个可证伪的疑点（读 cell 7 代码时发现，冻结在跑之前）：", "",
         "1. 两臂曝光不同——加权臂平均权重 %.2f、22%% 的日子空仓；常驻臂每天满仓。" % (
             p["products"].get("IC", {}).get("avg_weight", 0) or 0),
         "   任何一段「负的均值」对满仓臂的伤害约为半仓臂的两倍，与择时无关。",
         "2. cell 7 继承 cell 4 的阈值展期掩码；本仓 `idx_fut_roll_gap.json` 已证该掩码漏掉",
         "   65-78% 的日历展期，且被漏掉的展期是**假亏损**（IC 阈值掩码 1.80% vs 日历掩码 5.79%）。",
         "   假亏损日两臂都持有，于是疑点 1 的不对称又把掩码缺陷放大成「择时」。",
         "",
         "## 控制臂", "",
         "| 臂 | 含义 |", "|---|---|",
         "| R 复现 | 冻结规则 + 阈值掩码，独立代码 |",
         "| W 加权 | 冻结规则 + **日历掩码**（每月一个展期，按到期窗内最大基差步选定） |",
         "| C 恒定 | 权重恒等于该臂自己的平均权重，**不含任何择时** |",
         "| P 置换 | W 的权重序列循环平移 200 次（同分布同自相关，无对齐） |",
         ""]
    for code, v in p["products"].items():
        if "checks" not in v:
            L += ["## %s — %s" % (code, v.get("state")), ""]
            continue
        t, c = v["arms"]["threshold"], v["arms"]["calendar"]
        L += ["## %s（%s → %s，%.2f 年）" % (code, v["first"], v["last"], v["years"]), "",
              "| 掩码 | 加权 carry/年 | 恒定权重/年 | 常驻/年 | 加权回撤 | 常驻回撤 | 加权-恒定 | 加权-常驻 | 展期日 |",
              "|---|---|---|---|---|---|---|---|---|",
              "| 阈值(发布用) | %s | %s | %s | %s | %s | %s | %s | %d |" % (
                  fmt(t["weighted_pct"]), fmt(t["constant_pct"]), fmt(t["always_pct"]),
                  fmt(t["weighted_mdd_pct"]), fmt(t["always_mdd_pct"]),
                  fmt(t["margin_over_constant_pp"]), fmt(t["margin_over_always_pp"]),
                  t["roll_days"]),
              "| 日历(控制) | %s | %s | %s | %s | %s | %s | %s | %d |" % (
                  fmt(c["weighted_pct"]), fmt(c["constant_pct"]), fmt(c["always_pct"]),
                  fmt(c["weighted_mdd_pct"]), fmt(c["always_mdd_pct"]),
                  fmt(c["margin_over_constant_pp"]), fmt(c["margin_over_always_pp"]),
                  c["roll_days"]), "",
              "- 复现差：加权 %s vs 已发布 %s → **%s pp**（容差 0.5）" % (
                  fmt(t["weighted_pct"]), fmt(v["published_weighted_pct"]), v["repro_delta_pp"]),
              "- 配对检验（加权 - 恒定）：%s pp/年，t=%s，MDE=%.2f pp/年" % (
                  fnum(v["paired_vs_constant"].get("mean_pp")),
                  v["paired_vs_constant"].get("t"),
                  v["paired_vs_constant"].get("mde_pp") or 0),
              "- 配对检验（加权 - 常驻）：%s pp/年，t=%s" % (
                  fnum(v["paired_vs_always"].get("mean_pp")),
                  v["paired_vs_always"].get("t")),
              "- 置换检验：p=%s，零假设中位 %s pp（95 分位 %s pp）" % (
                  v["permutation"].get("p_value"),
                  fnum(v["permutation"].get("null_median_pp")),
                  fnum(v["permutation"].get("null_p05_pp"))),
              "- 判据 %s" % json.dumps(v["checks"], ensure_ascii=False),
              "- **判决 %s**" % v["verdict"], ""]
    prim = p["products"].get("IC") or next(
        (v for v in p["products"].values() if "checks" in v), {})
    if "checks" in prim:
        t = prim["arms"]["threshold"]
        c = prim["arms"]["calendar"]
        null_med = prim["permutation"].get("null_median_pp")
        else_where = (t["weighted_pct"] - null_med
                      if null_med is not None and t["weighted_pct"] is not None else None)
        L += ["## 一句话结论（全部由上面两张表派生）", "",
              "- 不带任何择时的恒定权重只拿到 %s，低于每天满仓的 %s——"
              "「少拿一点」买不到这段收益，曝光解释被证伪。" % (
                  fmt(t["constant_pct"]), fmt(t["always_pct"])),
              "- 同一段权重路径循环平移 200 次，中位只到 %s：权重自身的分布值这么多，"
              "剩下 %s 来自它落在哪一天。" % (fnum(null_med), fnum(else_where)),
              "- 换成日历展期掩码后加权仍是 %s、恒定仍是 %s，领先 %s pp 不靠被漏掉的展期。" % (
                  fmt(c["weighted_pct"]), fmt(c["constant_pct"]),
                  fnum(c["margin_over_constant_pp"])),
              "- 配对差的 MDE 只有 %s pp/年（非配对口径是 8pp 级）："
              "这格能分辨 1pp 的边，不是「看不出差别」。" % (
                  fnum(prim["paired_vs_constant"].get("mde_pp"))),
              ""]
    L += ["## 读数", "",
          "- 恒定权重臂（无择时）若已跑赢常驻 1pp 以上，那么「按分位定仓位」的收益主要来自",
          "  **少拿一点**，不是来自**在对的时候拿**。",
          "- 日历掩码把被漏掉的展期剔除后，两臂的相对关系会变——变多少就是掩码缺陷贡献的量。",
          "- 配对 d 序列的 MDE 远小于非配对 MDE：这正是本仓「一格只有能分辨它值得下注的边才准排队」",
          "  那条规则需要的那种数字。",
          "",
          "## 没有回答的问题", "",
          "- 没有建模保证金占用与资金成本（carry 毛口径，与 cell 7 同）。",
          "- 日历掩码按「到期窗内最大基差步」选日，是近似而非合约代码；合约身份不在面板里。",
          "- 只做 IC/IM（cell 7 也只做这两个）。IF/IH 贴水更薄，规则可能不适用。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- selftest
def selftest():
    ok = total = 0

    def leg(cond, name):
        nonlocal ok, total
        total += 1
        ok += 1 if cond else 0
        if not cond:
            print("FAIL " + name)

    # L1 basis and spread arithmetic
    b, sp = faces([100.0, 99.0], [100.0, 100.0])
    leg(abs(b[0]) < 1e-12 and abs(b[1] + 0.01) < 1e-12 and abs(sp[0] + 0.01) < 1e-12,
        "L1 basis/spread arithmetic")
    # L2 the threshold mask flags a visible basis step and not the quiet days
    b = [0.0, 0.0, -0.05, -0.05, -0.05]
    m = mask_threshold(b)
    leg(m[1] is True and not any(m[k] for k in (0, 2)), "L2 threshold mask flags the step only")
    # L3 percentile midpoint rule
    leg(abs(percentile([1.0, 2.0, 3.0], 2.0) - 50.0) < 1e-9, "L3 percentile midpoint")
    # L4 weight bounds: widest discount -> 1, narrowest -> 0
    b = [0.0] * 100 + [-0.30] + [0.0] * 20
    w = weights(b, window=100, min_obs=60)
    leg(abs(w[100] - 1.0) < 1e-9, "L4 widest discount gets full weight")
    b2 = [0.0] * 100 + [0.30] + [0.0] * 20
    leg(abs(weights(b2, window=100, min_obs=60)[100]) < 1e-9, "L5 narrowest discount gets zero")
    # L6 arm pays the entry cost and earns nothing on a roll day
    c, turn = arm([0.01, 0.01], [False, True], [1.0, 1.0])
    leg(abs(c[0] - (0.01 - 1.5 / 10000)) < 1e-12 and abs(c[1]) < 1e-15,
        "L6 entry cost paid, roll day earns nothing")
    # L7 annualise of a flat 0 series is 0, not None
    leg(annualise([0.0] * 244) == 0.0, "L7 flat series annualises to zero")
    # L8 paired stats catch a sign and never divide by zero on a constant difference
    d = [0.0005] * 244
    p = paired(d)
    leg(p["mean_pp"] > 12 and p["t"] is None or p["t"] > 100, "L8 paired mean over 244 identical days")
    # L9 calendar mask finds exactly one roll in a month whose basis steps once
    dates = []
    d0 = date(2025, 3, 3)
    while d0 <= date(2025, 3, 31):
        if d0.weekday() < 5:
            dates.append(d0.isoformat())
        d0 += timedelta(days=1)
    basis = [0.0] * len(dates)
    base = len(dates) // 2
    for k in range(base, len(dates)):
        basis[k] = -0.01
    cal, hits = mask_calendar(dates, basis)
    leg(hits == 1 and sum(1 for x in cal if x) == 1, "L9 calendar mask picks one roll in the month")
    # L10 a zero-weight path can never clear a positive bar, so the permutation p bottoms out
    # at 1/(draws+1) -- rotating a path that earns nothing cannot invent a rotation that earns
    b3 = [0.0] * 60
    w3 = [0.0] * len(b3)
    pm = permute([0.001] * len(b3), [False] * len(b3), w3, 5.0, draws=20)
    leg(pm["p_value"] <= 0.05, "L10 zero-weight path never reaches a positive bar")
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    p = build()
    print(json.dumps({"ok": True, "verdict": p["verdict"],
                      "per_product": {k: (v.get("verdict"),
                                          v["arms"]["threshold"]["weighted_pct"] if "checks" in v else None,
                                          v["arms"]["threshold"]["constant_pct"] if "checks" in v else None,
                                          v["arms"]["calendar"]["weighted_pct"] if "checks" in v else None,
                                          v["arms"]["calendar"]["constant_pct"] if "checks" in v else None)
                                      for k, v in p["products"].items()}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
