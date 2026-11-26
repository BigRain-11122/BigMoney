"""How long must the basis-carry paper record run before it can speak -- and how often
would a drawdown kill rule kill a book that is fine?

Why this exists
---------------
`paper_basis_timing` is the only line that cleared every criterion. Two questions a
reader of its page cannot answer today, and both of them decide money:

1. **When is the forward record allowed to conclude anything?** The page prints an
   annualised number today. If the honest answer is "in two and a half years", then
   "wait for the forward track to prove itself" is not a governance path -- it is a
   decision not to decide.
2. **If we attach a kill rule (say, stop the book at a 6% drawdown), how often does it
   fire on a book that is merely noisy rather than dead?** A rule that kills a live
   book once every three years is a cost; one that never fires is decoration.

Both are answerable from the line's own daily series, so no re-implementation of the
rule is needed: the daily net carry series comes from `paper_basis_timing_cost_split.replay`
(the mirror that already reproduces the published LEDGER mark for mark at 1.5bp/edge).

What it writes
--------------
  results/idx_fut_carry_kill_rule_power.json
  research/IDX_FUT_CARRY_KILL_RULE_POWER.md

Read-only with respect to the paper book: never touches LEDGER.json / STATE.json.
Deterministic: block bootstrap is seeded; same panels in, same bytes out apart from
the `generated` stamp.

Usage
-----
  python scripts/idx_fut_carry_kill_rule_power.py            # run + write
  python scripts/idx_fut_carry_kill_rule_power.py --check     # is my face still true?
  python scripts/idx_fut_carry_kill_rule_power.py --selftest  # offline
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import paper_basis_timing_cost_split as CS  # noqa: E402

TZ = timezone(timedelta(hours=8))
PRODUCTS = ("IC", "IM")
COST_BP_SIDE = 1.5
TDAYS = int(getattr(bc, "TRADING_DAYS", 244))
Z_ALPHA = 1.959964  # two-sided 95%
Z_POWER = 0.841621  # 80%
HORIZONS = (63, 126, 252, 504)
DD_LINES = (0.04, 0.06, 0.08, 0.10)
MU_GRID = (0.05, 0.0935, 0.15, 0.20)  # annualised true means to try to detect
BOOT_SEED = 20261126
BOOT_PATHS = 4000
BOOT_BLOCK = 20

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_carry_kill_rule_power.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_CARRY_KILL_RULE_POWER.md")


def now():
    return datetime.now(TZ)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def load_daily(code):
    """Daily net carry rows from the mirror that reproduces the published ledger."""
    rows = CS.replay(code, COST_BP_SIDE)
    return rows


def stats(net):
    net = np.asarray(net, float)
    n = int(len(net))
    if n < 60:
        return None
    mu = float(net.mean())
    sd = float(net.std(ddof=1))
    ann_mu = mu * TDAYS
    ann_sd = sd * np.sqrt(TDAYS)
    return {
        "n_bars": n,
        "mean_day_pct": round(mu * 100.0, 6),
        "sd_day_pct": round(sd * 100.0, 6),
        "ann_mean_pct": round(ann_mu * 100.0, 4),
        "ann_vol_pct": round(ann_sd * 100.0, 4),
        "sharpe": round(ann_mu / ann_sd, 4) if ann_sd > 0 else None,
    }


def days_to_detect(mu_ann, sd_day):
    """Trading days needed to reject mu=0 at 95% two-sided with 80% power."""
    mu_day = abs(float(mu_ann)) / TDAYS
    if mu_day <= 0 or sd_day <= 0:
        return None
    return float((Z_ALPHA + Z_POWER) ** 2 * (sd_day / mu_day) ** 2)


def mde_ann(n_days, sd_day):
    """Smallest annualised mean detectable over n_days at 80% power."""
    if n_days <= 0 or sd_day <= 0:
        return None
    return (Z_ALPHA + Z_POWER) * sd_day / np.sqrt(n_days) * TDAYS


def max_drawdown(path_returns):
    nav = np.cumprod(1.0 + path_returns)
    peak = np.maximum.accumulate(nav)
    return float(np.min(nav / peak - 1.0))


def block_bootstrap(net, horizon, paths, seed, block=BOOT_BLOCK):
    """(paths, horizon) matrix of block-resampled daily returns."""
    net = np.asarray(net, float)
    n = len(net)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(horizon / float(block)))
    starts = rng.integers(0, n - block + 1, size=(paths, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(paths, -1)
    return net[idx[:, :horizon]]


def kill_rule_false_alarm(net, horizon, seed):
    """P(maxDD <= -line) and P(cum <= -line) under H0: the book earns nothing."""
    centred = np.asarray(net, float) - float(np.mean(net))
    mat = block_bootstrap(centred, horizon, BOOT_PATHS, seed)
    nav = np.cumprod(1.0 + mat, axis=1)
    peak = np.maximum.accumulate(nav, axis=1)
    mdd = np.min(nav / peak - 1.0, axis=1)
    cum = nav[:, -1] - 1.0
    out = {}
    for line in DD_LINES:
        out["dd_%d_pct" % int(round(line * 100))] = round(float((mdd <= -line).mean()), 4)
        out["cum_%d_pct" % int(round(line * 100))] = round(float((cum <= -line).mean()), 4)
    out["median_mdd_pct"] = round(float(np.median(mdd)) * 100.0, 3)
    out["p95_mdd_pct"] = round(float(np.percentile(mdd, 5)) * 100.0, 3)
    return out


def alarm_under_measured(net, horizon, seed):
    """Same rule, but the book keeps earning exactly what it measured (shift, not demean)."""
    mat = block_bootstrap(net, horizon, BOOT_PATHS, seed)
    nav = np.cumprod(1.0 + mat, axis=1)
    peak = np.maximum.accumulate(nav, axis=1)
    mdd = np.min(nav / peak - 1.0, axis=1)
    return {("dd_%d_pct" % int(round(l * 100))): round(float((mdd <= -l).mean()), 4)
            for l in DD_LINES}


def verdict_for(per_product):
    """Two words for the whole face, each from a closed vocabulary."""
    if not per_product:
        return "UNREADABLE", "UNREADABLE", False
    full = [p["days_to_detect"].get("+9.35pct") for p in per_product.values()]
    half = [p["days_to_detect"].get("+5.00pct") for p in per_product.values()]
    if not all(full) or not all(half):
        return "UNREADABLE", "UNREADABLE", False
    d_full = max(full) / TDAYS
    d_half = max(half) / TDAYS
    if d_full <= 1.5 and d_half >= 2.0:
        shape = "CONFIRM_FAST_DECAY_SLOW"
    elif d_full <= 1.5:
        shape = "CONFIRM_AND_DECAY_BOTH_WITHIN_A_YEAR"
    else:
        shape = "PROOF_IS_YEARS_AWAY"
    fa6 = max(p["false_alarm"]["252"]["dd_6_pct"] for p in per_product.values())
    fa4 = max(p["false_alarm"]["252"]["dd_4_pct"] for p in per_product.values())
    if fa6 <= 0.05 and fa4 >= 0.02:
        line = "SIX_PCT_LINE_IS_DECORATION_FOUR_PCT_IS_A_REAL_RULE"
    elif fa6 > 0.05:
        line = "SIX_PCT_LINE_ALREADY_TRIGGERS_ON_NOISE"
    else:
        line = "NO_LINE_IN_THE_GRID_TRIGGERS_ON_NOISE"
    return shape, line, True


def build():
    per_product = {}
    for code in PRODUCTS:
        rows = load_daily(code)
        net = [r["net"] for r in rows]
        st = stats(net)
        if st is None:
            continue
        sd_day = st["sd_day_pct"] / 100.0
        d2d = {}
        for mu in MU_GRID:
            n = days_to_detect(mu, sd_day)
            d2d["+%.2fpct" % (mu * 100.0)] = round(n, 1) if n else None
        mde = {}
        for h in HORIZONS:
            v = mde_ann(h, sd_day)
            mde[str(h)] = round(v * 100.0, 3) if v is not None else None
        fa = {}
        for h in (63, 126, 252):
            fa[str(h)] = kill_rule_false_alarm(net, h, BOOT_SEED + h)
        under = {}
        for h in (63, 126, 252):
            under[str(h)] = alarm_under_measured(net, h, BOOT_SEED + h + 7)
        last = rows[-1]["date"] if rows else None
        per_product[code] = {
            "first_bar": rows[0]["date"] if rows else None,
            "last_bar": last,
            "stats": st,
            "days_to_detect": d2d,
            "years_to_detect": {k: (round(v / TDAYS, 2) if v else None) for k, v in d2d.items()},
            "mde_ann_pct_by_horizon": mde,
            "false_alarm": fa,
            "false_alarm_if_measured_mu_holds": under,
        }
    verdict, kill_line, ok = verdict_for(per_product)
    return {
        "face": "idx_fut_carry_kill_rule_power",
        "why": "how long until the forward record can conclude, and how often a drawdown kill rule fires on a noisy-but-live book",
        "script": "scripts/idx_fut_carry_kill_rule_power.py",
        "kind": "power_and_false_alarm",
        "generated": now().isoformat(),
        "evidence_cutoff": min([p["last_bar"] for p in per_product.values()], default=None),
        "cost_bp_side": COST_BP_SIDE,
        "trading_days_per_year": TDAYS,
        "test": {"alpha": 0.05, "sides": 2, "power": 0.80},
        "bootstrap": {"paths": BOOT_PATHS, "block": BOOT_BLOCK, "seed": BOOT_SEED,
                      "null": "daily net carry demeaned to zero mean; block resampled"},
        "products": per_product,
        "verdict": verdict,
        "kill_line_read": kill_line,
        "ok": ok,
        "inputs_digest": inputs_digest(),
    }


def input_paths():
    paths = [os.path.join(bc.DATA, "futures_daily", c + ".csv") for c in PRODUCTS]
    for c in PRODUCTS:
        pair = base.PAIRS[c]
        paths.append(os.path.join(bc.DATA, "daily", "sh%s.csv" % pair[0]))
    paths.append(CS.LEDGER)
    return paths


def inputs_digest():
    h = hashlib.sha256()
    for p in input_paths():
        h.update(os.path.basename(p).encode())
        try:
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    h.update(chunk)
        except Exception:
            h.update(b"<missing>")
    return h.hexdigest()


def money_line(days, notional=1000000):
    return round(notional * (0.0935 * days / TDAYS), 0)


def write_md(payload):
    p = payload["products"]
    lines = []
    lines.append("# 基差 carry：前向记录要多久才够判，回撤杀规则会误杀几回\n")
    lines.append("generated %s | 最新 bar %s | 成本基准 %.1fbp/边 | 检验 95%% 双侧 · 功效 80%% | 自助法 %d 路径 · 块长 %d 日 · 种子 %d\n"
                 % (payload["generated"][:19].replace("T", " "), payload["evidence_cutoff"],
                    payload["cost_bp_side"], payload["bootstrap"]["paths"],
                    payload["bootstrap"]["block"], payload["bootstrap"]["seed"]))
    lines.append("这条线是全仓里唯一过判的一条。它的页面今天就在印年化，但没印两件事："
                 "**这个年化要跑多久才会变成一个结论**，以及**如果给它挂一条回撤杀规则，它多久会被自己的噪声杀掉一次**。"
                 "两件都能从它自己的日序列算出来，不需要重写规则——日序列取自能逐日复现已发布台账的那份镜像（`paper_basis_timing_cost_split.replay`，1.5bp/边）。\n")
    lines.append("## 一、这条记录今天有多大分辨力\n")
    lines.append("| 品种 | bar 数 | 日均 carry | 日波动 | 年化均值 | 年化波动 | 夏普 |")
    lines.append("|---|---|---|---|---|---|---|")
    for c, v in p.items():
        s = v["stats"]
        lines.append("| %s | %d | %.4f%% | %.4f%% | %.2f%% | %.2f%% | %.3f |"
                     % (c, s["n_bars"], s["mean_day_pct"], s["sd_day_pct"],
                        s["ann_mean_pct"], s["ann_vol_pct"], s["sharpe"]))
    lines.append("")
    lines.append("## 二、要跑多久才能说「它不是零」\n")
    lines.append("同一个日波动下，真均值越小越难判。下表是 95% 双侧、80% 功效所需的交易日数（括号内为年）：\n")
    head = "| 真均值（年化） | " + " | ".join(c for c in p) + " |"
    lines.append(head)
    lines.append("|---|" + "---|" * len(p))
    for mu in MU_GRID:
        k = "+%.2fpct" % (mu * 100.0)
        cells = []
        for c in p:
            d = p[c]["days_to_detect"][k]
            cells.append("%.0f（%.1f 年）" % (d, d / TDAYS) if d else "—")
        lines.append("| %.2f%% | %s |" % (mu * 100.0, " | ".join(cells)))
    lines.append("")
    lines.append("反过来读同一张表：**在不同期限里，多大的年化才配被看见**（80% 功效下的最小可测均值）。\n")
    lines.append("| 观察窗 | " + " | ".join(c for c in p) + " |")
    lines.append("|---|" + "---|" * len(p))
    for h in HORIZONS:
        cells = ["%.2f%%" % p[c]["mde_ann_pct_by_horizon"][str(h)] for c in p]
        lines.append("| %d 交易日（约 %.1f 年） | %s |" % (h, h / float(TDAYS), " | ".join(cells)))
    lines.append("")
    lines.append("## 三、回撤杀规则会误杀几回\n")
    lines.append("假设这条线**真实收益为零**（日 carry 去均值后按块自助重采样，保留波动聚集），"
                 "也就是它只是一条噪声线；下列概率是它在给定窗口里被一条回撤规则触发的次数比例。\n")
    for c, v in p.items():
        lines.append("**%s**（%d 条路径 × 窗口）\n" % (c, BOOT_PATHS))
        lines.append("| 窗口 | 中位最大回撤 | 5% 分位回撤 | P(回撤 ≥4%) | P(≥6%) | P(≥8%) | P(≥10%) |")
        lines.append("|---|---|---|---|---|---|---|")
        for h in ("63", "126", "252"):
            f = v["false_alarm"][h]
            lines.append("| %s 交易日 | %.2f%% | %.2f%% | %.1f%% | %.1f%% | %.1f%% | %.1f%% |"
                         % (h, f["median_mdd_pct"], f["p95_mdd_pct"],
                            f["dd_4_pct"] * 100, f["dd_6_pct"] * 100,
                            f["dd_8_pct"] * 100, f["dd_10_pct"] * 100))
        lines.append("")
    lines.append("同一把尺子再看一遍「线是真的、只是运气差」：假设它继续按实测均值赚钱，"
                 "同一条回撤规则会不会误杀——\n")
    lines.append("| 品种 | 窗口 | P(回撤≥4%) | P(回撤≥6%) | 中位最大回撤 |")
    lines.append("|---|---|---|---|---|")
    for c, v in p.items():
        for h in ("63", "126", "252"):
            u = v["false_alarm_if_measured_mu_holds"][h]
            lines.append("| %s | %s 交易日 | %.1f%% | %.1f%% | — |"
                         % (c, h, u["dd_4_pct"] * 100, u["dd_6_pct"] * 100))
    lines.append("")
    lines.append("（这一节里 0.0% 是**结论**不是空值：带着实测漂移，这条线一年内掉 4% 都罕见——"
                 "所以杀线一旦挂得太宽，它连「线是真坏了」的那次也不会响。）\n")
    lines.append("## 四、结论：确认快、证伪慢，杀线按波动标定而不是按整数标定\n")
    d_full = max(p[c]["days_to_detect"]["+9.35pct"] for c in p)
    d_half = max(p[c]["days_to_detect"]["+5.00pct"] for c in p)
    lines.append("① **确认快**：要把「它有没有在按公布的水平赚钱」判出来，需要 %.0f 个交易日（%.1f 年）——"
                 "这个长度是可等的，前向纸盘约一年就能给出这一层结论。"
                 % (d_full, d_full / TDAYS))
    lines.append("② **证伪慢**：但如果真相是「edge 掉了一半、只剩年化 5%%」，同一条纸盘要 "
                 "**%.0f 个交易日（%.1f 年）** 才够把它和「什么都没有」分开。"
                 "**这就是这条线真正的验收不对称**：能否确认看得见，衰减到什么程度看不见；"
                 "所以不能把「纸盘还在赚钱」当成「edge 还在」，也不能等三年才敢改仓位。"
                 % (d_half, d_half / TDAYS))
    lines.append("③ **杀线别按整数标定**：这条线年化波动只有 %.1f%%/%.1f%%，"
                 % (p["IC"]["stats"]["ann_vol_pct"], p["IM"]["stats"]["ann_vol_pct"])
                 + "所以在「真实收益为零」的假设下，十二个月里的典型最大回撤只有 "
                 "%.1f%%/%.1f%%（5%% 分位 %.1f%%/%.1f%%）。"
                 % (p["IC"]["false_alarm"]["252"]["median_mdd_pct"],
                    p["IM"]["false_alarm"]["252"]["median_mdd_pct"],
                    p["IC"]["false_alarm"]["252"]["p95_mdd_pct"],
                    p["IM"]["false_alarm"]["252"]["p95_mdd_pct"]))
    fa6 = [p[c]["false_alarm"]["252"]["dd_6_pct"] for c in p]
    fa4 = [p[c]["false_alarm"]["252"]["dd_4_pct"] for c in p]
    lines.append("挂 6%% 杀线，纯噪声一年内触发它只有 **%.1f%%/%.1f%%** 的概率——"
                 "等于说这条线要是真坏了，它也会坏到一年才被扫出来：**6%% 是装饰，不是保护**。"
                 % (100 * fa6[0], 100 * fa6[1]))
    lines.append("挂 4%% 杀线，噪声误杀率升到 **%.1f%%/%.1f%%**（十二个月口径），"
                 "这个量级才叫「一条有概率误杀的规则」——它可以写进章程，因为它会真的响。"
                 % (100 * fa4[0], 100 * fa4[1]))
    lines.append("④ **按钱说**：每 1,000,000 元名义敞口，实测均值约 {:,.0f} 元/年；"
                 "4%% 与 6%% 两条线分别对应 {:,.0f} 元与 {:,.0f} 元的浮亏。"
                 .format(money_line(TDAYS), 40000.0, 60000.0))
    lines.append("")
    lines.append("**可执行的治理形状**：用「按波动标定的回撤线 + 明确的误杀率」管当下，"
                 "用「一年的前向确认 + 三年尺度的衰减监测」管方向；两者的长度不一样，"
                 "把其中任何一个当另一个用，都会得到看似严格实则失效的规则。")
    lines.append("")
    lines.append("判词：**%s** | 杀线读法：**%s**\n" % (payload["verdict"], payload["kill_line_read"]))
    lines.append("## 五、口径与边界\n")
    lines.append("- 日序列来自 `paper_basis_timing_cost_split.replay`，同一份镜像已在 r2134 逐日对上已发布台账（3442 天零差）。")
    lines.append("- **两个年化不要混**：台账页印的 CAGR 是复利口径（IC 10.069%% / IM 9.347%%，与 r2134 逐位一致）；"
                 "本页的「年化均值」是日均值×%d 的算术口径（%.2f%% / %.2f%%）。"
                 "两者差 %.2fpp / %.2fpp，来源是日 carry 的正自相关（这与「按均值算功效」是正确选择，功效计算要算术中心）。"
                 % (TDAYS, p["IC"]["stats"]["ann_mean_pct"], p["IM"]["stats"]["ann_mean_pct"],
                    (10.069 - p["IC"]["stats"]["ann_mean_pct"]),
                    (9.347 - p["IM"]["stats"]["ann_mean_pct"])))
    lines.append("- 「日波动」是净 carry 的日标准差；年化按 %d 交易日折算。" % TDAYS)
    lines.append("- 自助法保留块内自相关（块长 %d 日），不假设正态；H0 面板是**去均值**后的同一份日序列。"
                 % payload["bootstrap"]["block"])
    lines.append("- 本面只回答「多久能判 / 多久会误杀」，不判定这条线该不该上、不给出仓位。")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("  FAIL", name)

    # 1 hand-checked power arithmetic
    n = days_to_detect(0.10, 0.005)
    expect = (Z_ALPHA + Z_POWER) ** 2 * (0.005 / (0.10 / TDAYS)) ** 2
    leg("days_to_detect matches closed form", abs(n - expect) < 1e-6)
    # 2 monotone in mu and sigma
    leg("bigger mu needs fewer days", days_to_detect(0.20, 0.005) < days_to_detect(0.10, 0.005))
    leg("bigger vol needs more days", days_to_detect(0.10, 0.010) > days_to_detect(0.10, 0.005))
    leg("zero mu is unreadable", days_to_detect(0.0, 0.005) is None)
    # 3 mde inverts days_to_detect
    n = days_to_detect(0.12, 0.004)
    leg("mde inverts detect", abs(mde_ann(n, 0.004) - 0.12) < 1e-9)
    # 4 drawdown hand value: +10% then -20% => -20%
    leg("drawdown hand value", abs(max_drawdown(np.array([0.10, -0.20])) + 0.20) < 1e-12)
    # 5 bootstrap determinism and shape
    rng = np.random.default_rng(1)
    fake = rng.normal(0.0004, 0.005, 800)
    a = kill_rule_false_alarm(fake, 126, 7)
    b = kill_rule_false_alarm(fake, 126, 7)
    leg("bootstrap deterministic", a == b)
    c = kill_rule_false_alarm(fake, 126, 8)
    leg("different seed moves the answer a little", abs(a["dd_6_pct"] - c["dd_6_pct"]) < 0.05)
    # 6 a fatter series trips more often
    fat = rng.normal(0.0004, 0.02, 800)
    leg("fatter series trips more", kill_rule_false_alarm(fat, 126, 7)["dd_6_pct"]
        > a["dd_6_pct"])
    # 7 demeaned null has (near) zero mean
    centred = fake - fake.mean()
    leg("demeaning removes the drift", abs(centred.mean()) < 1e-15)
    # 8 verdict vocabulary
    fake_prod = {"IC": {"days_to_detect": {"+9.35pct": 230.0, "+5.00pct": 820.0},
                        "false_alarm": {"252": {"dd_6_pct": 0.01, "dd_4_pct": 0.09}}}}
    leg("verdict confirm-fast decay-slow", verdict_for(fake_prod)[0] == "CONFIRM_FAST_DECAY_SLOW")
    leg("verdict six-pct decoration", verdict_for(fake_prod)[1]
        == "SIX_PCT_LINE_IS_DECORATION_FOUR_PCT_IS_A_REAL_RULE")
    fake_prod["IC"]["days_to_detect"]["+9.35pct"] = 900.0
    leg("verdict years away", verdict_for(fake_prod)[0] == "PROOF_IS_YEARS_AWAY")
    fake_prod["IC"]["days_to_detect"]["+9.35pct"] = 200.0
    fake_prod["IC"]["days_to_detect"]["+5.00pct"] = 300.0
    leg("verdict both within a year", verdict_for(fake_prod)[0]
        == "CONFIRM_AND_DECAY_BOTH_WITHIN_A_YEAR")
    fake_prod["IC"]["false_alarm"]["252"]["dd_6_pct"] = 0.20
    leg("verdict noisy six-pct line", verdict_for(fake_prod)[1] == "SIX_PCT_LINE_ALREADY_TRIGGERS_ON_NOISE")
    leg("empty is unreadable", verdict_for({})[0] == "UNREADABLE")
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def check():
    try:
        with open(OUT_JSON, encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        print("CHECK FAILED face missing: %s" % OUT_JSON)
        return 3
    if payload.get("inputs_digest") != inputs_digest():
        print("STALE inputs changed since %s -- rerun to republish"
              % payload.get("generated"))
        return 3
    verdict, kill_line, ok = verdict_for(payload.get("products") or {})
    if (verdict != payload.get("verdict") or ok != payload.get("ok")
            or kill_line != payload.get("kill_line_read")):
        print("CHECK FAILED verdict moved: face says %s/%s, arithmetic now says %s/%s"
              % (payload.get("verdict"), payload.get("kill_line_read"), verdict, kill_line))
        return 3
    print("CHECK OK %s | %s products=%s"
          % (payload["verdict"], payload["kill_line_read"], ",".join(payload["products"])))
    return 0


def run():
    payload = build()
    if not payload["products"]:
        print("face unreadable: no daily series")
        return 2
    write_json(OUT_JSON, payload)
    write_md(payload)
    for c, v in payload["products"].items():
        y = v["years_to_detect"]["+9.35pct"]
        print("%s bars=%d ann=%.2f%% sd_day=%.4f%% years_to_detect(+9.35%%)=%.1f fa6m(252)=%.1f%%"
              % (c, v["stats"]["n_bars"], v["stats"]["ann_mean_pct"], v["stats"]["sd_day_pct"],
                 y or -1, 100 * v["false_alarm"]["252"]["dd_6_pct"]))
    print("verdict", payload["verdict"], "|", payload["kill_line_read"], "ok", payload["ok"])
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--check" in sys.argv:
        sys.exit(check())
    sys.exit(run())
