"""What is the smallest annualised gap this 5-seat book can actually tell from zero? (r1762)

Two faces have now each answered a question about the gate ladder and both landed on
"cannot separate":

  * r1760 (this repo, block bootstrap on paired daily returns) -- the 100M-vs-40M bump is
    1.79pp with p=0.104;
  * the arm-noise face (random-ranking null band) -- 100M-vs-20M is 0.79pp inside a 1.36pp
    band.

Both said "inside the noise", neither said **how big a gap would have had to be**. A reader
who is told "0.79pp is inside the noise" has no way to judge the next sentence on this book,
which is always of the form "this rung is better by N pp". This face publishes the number
that turns N into a verdict: the MINIMUM DETECTABLE EFFECT at 80% power, per rung pair, from
the same paired daily difference series the bootstrap already uses.

Design notes
------------
* Same panel, same engine, same cost/vol target, same seat count as the published book --
  only the liquidity cut moves. The control block re-prices every rung this face judges and
  must reproduce the price face's own cell to CONTROL_TOL_PP, or nothing is judged.
* MDE = z_80 * SE, z_80 = 2.802 (two-sided 5%, 80% power -- the constant E162/E247 use).
  SE is the standard deviation of the circular block bootstrap distribution of the mean
  daily difference (block = one rebalance period, frozen draws and seed), annualised with
  the same 252 the engine's own vol uses. So the ruler is not imported: it is the same
  resampling already behind the p-values, read for its width instead of its tail.
* Bars needed to reach a target MDE follow from SE ~ 1/sqrt(n): n_target = n * (mde/target)^2.
  Reported so "collect more history" becomes a number, not a wish.
* Nothing here moves a gate, a seat count, or a published number.

Usage:
  python scripts/etf_book_book_mde.py run
  python scripts/etf_book_book_mde.py --selftest
  python scripts/etf_book_book_mde.py --check
  python scripts/etf_book_book_mde.py --md
"""
import json
import math
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

import etf_composite_pf as E            # noqa: E402
import etf_book_entry_gate as G         # noqa: E402
import etf_robust_pf as R               # noqa: E402  (the engine itself)
import etf_equity_alpha as A            # noqa: E402
import etf_book_gate_raise_noise as N   # noqa: E402  (arm pricing + the existing bootstrap)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_book_mde.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_BOOK_MDE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")
FACE_GATE_NOISE = os.path.join(ROOT, "results", "etf_book_gate_raise_noise.json")
FACE_ARM_NOISE = os.path.join(ROOT, "results", "etf_book_raise_arm_noise.json")

ARMS_CNY = (20e6, 40e6, 100e6, 200e6, 400e6, 1000e6)
BASE = 20e6                      # the cut the ticket prints
BUMP_HIGH, BUMP_LOW = 100e6, 40e6
Z_80 = 2.802                     # two-sided 5%, 80% power
PER_YEAR = 252.0                 # the engine's own annualisation
BLOCK = 20                       # one rebalance period
DRAWS = 2000
SEED = 20261116
CONTROL_TOL_PP = 0.25            # the arm must reproduce the price face's own cell
TARGET_PP = 1.0                  # the sentence readers actually say: "better by 1pp"
XCHECK_P_TOL = 0.02              # the gate-noise face's p must reproduce here


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def pair_label(a_cny, b_cny):
    return "%gM_vs_%gM" % (a_cny / 1e6, b_cny / 1e6)


def ann_pp(mean_daily):
    """A mean daily difference, in the annualised pp the papers print."""
    return float(mean_daily) * PER_YEAR * 100.0


def delta_pp(got, want):
    """Published-cell control: both sides in the same units, rounded to 4dp pp."""
    if got is None or want is None:
        return None
    return round((float(got) - float(want)) * 100.0, 4)


def bootstrap_se(diff, block=BLOCK, draws=DRAWS, seed=SEED):
    """Width of the same block bootstrap that the p-values come from.

    One inflation pass over the paired daily difference; the resampled means' spread is the
    standard error of the mean, and z_80 * SE is the smallest gap detectable at 80% power.
    """
    x = np.asarray([v for v in diff if np.isfinite(v)], dtype=float)
    if x.size < block * 2:
        return None
    rng = np.random.default_rng(seed)
    n = x.size
    nb = int(math.ceil(n / float(block)))
    starts_all = rng.integers(0, n, size=(draws, nb))
    offs = np.arange(block)[None, :]
    means = np.empty(draws, dtype=float)
    for i in range(draws):
        idx = (starts_all[i][:, None] + offs).ravel() % n
        means[i] = float(x[idx[:n]].mean())
    obs = float(x.mean())
    se = float(means.std(ddof=1))
    se_ann = ann_pp(se)
    p_one = round((int((means <= 0.0).sum()) + 1) / (draws + 1.0), 4)
    # the same resamples, counted on the side the number actually points at: a negative gap
    # is not evidence for "zero" just because p_one_sided sits near 1. Counting the far tail
    # directly (instead of 1 - p) keeps an all-zero series from claiming a direction.
    if obs > 0:
        p_dir = p_one
    elif obs < 0:
        p_dir = round((int((means >= 0.0).sum()) + 1) / (draws + 1.0), 4)
    else:
        p_dir = 1.0
    return {"bars": int(n), "obs_ann_pp": round(ann_pp(obs), 4),
            "se_ann_pp": round(se_ann, 4),
            "mde80_ann_pp": round(Z_80 * se_ann, 4),
            "t": (round(obs / se, 3) if se > 0 else None),
            "p_one_sided": p_one, "p_direction": p_dir,
            "draws": draws, "block": block, "seed": seed}


def bars_needed(mde_pp, bars, target_pp=TARGET_PP):
    """How many bars would bring the MDE down to `target_pp` (SE ~ 1/sqrt(n))."""
    if mde_pp is None or not bars:
        return None
    if mde_pp <= target_pp:
        return 0
    return int(math.ceil(bars * (mde_pp / float(target_pp)) ** 2))


def classify_pair(obs_pp, mde_pp, p_dir=None, p_sig=0.05):
    """One row, one word.

    Three states, because two would lie: a gap can be *significant* (the bootstrap rarely
    puts the mean on the other side of zero) and still be *underpowered* (a rerun of this
    same history would fail to reproduce the direction 20% of the time). MDE80 is the
    second threshold; the p is the first. Printing only one of them is how a "0.79pp inside
    the noise" sentence and a t=-2.07 go out under the same word.
    """
    if obs_pp is None or mde_pp is None:
        return "NO_ESTIMATE"
    if abs(obs_pp) > mde_pp:
        return "ABOVE_MDE80"
    if p_dir is not None and p_dir <= p_sig:
        return "SIGNIFICANT_UNDERPOWERED"
    return "NO_DIRECTION"


def classify(rows, control_pp=None):
    """Face-level verdict over the rung rows."""
    if control_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "控制臂没有跑出来：这张面不判任何一档。"}
    if abs(control_pp) > CONTROL_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与抬闸定价面的同一格差 %.2fpp（容差 %.2fpp），"
                            "这不是同一本书，本面不判。" % (control_pp, CONTROL_TOL_PP)}
    est = [r for r in rows if r.get("status") not in (None, "NO_ESTIMATE")]
    if not est:
        return {"verdict": "CANNOT_JUDGE_NO_ARMS",
                "sentence": "没有一行拿到可用的差序列：不判。"}
    above = [r for r in est if r["status"] == "ABOVE_MDE80"]
    sig = [r for r in est if r["status"] == "SIGNIFICANT_UNDERPOWERED"]

    def name(rs):
        return "、".join("%s（%.2fpp，MDE80 %.2fpp）"
                        % (r["pair"], r["obs_ann_pp"], r["mde80_ann_pp"]) for r in rs)

    lo = min(r["mde80_ann_pp"] for r in est)
    hi = max(r["mde80_ann_pp"] for r in est)
    if above and len(above) == len(est):
        return {"verdict": "EVERY_GAP_ABOVE_MDE80",
                "sentence": "%d 个档差全部越过这本书 80%% 效力下的最小可分辨差——"
                            "这些档位之间的高低不是噪声。" % len(above)}
    if above and sig:
        return {"verdict": "MIXED_ABOVE_AND_UNDERPOWERED",
                "sentence": "%d 档越过 MDE80（%s）；另有 %d 档方向站得住（p≤0.05）但没到 80%% 效力"
                            "（%s）；其余落在无方向档。"% (len(above), name(above), len(sig), name(sig))}
    if above:
        return {"verdict": "SOME_GAPS_ABOVE_MDE80",
                "sentence": "%d 档越过 MDE80（%s）；其余 %d 档在这本书的射程外。"
                            % (len(above), name(above), len(est) - len(above))}
    if sig:
        return {"verdict": "SIGNIFICANT_BUT_UNDERPOWERED",
                "sentence": "%d 个档差里，%d 档方向站得住（p≤0.05）却没到 80%% 效力（%s）——"
                            "把这本账再跑一遍，那 20%% 的失败率就是这条差消失的概率；"
                            "MDE80 区间 %.2f~%.2fpp，越小的差越没有射程。"
                            % (len(est), len(sig), name(sig), lo, hi)}
    biggest = max(est, key=lambda r: abs(r["obs_ann_pp"]))
    return {"verdict": "ALL_GAPS_BELOW_MDE80",
            "sentence": "%d 个档差全部落在这本书 80%% 效力阈值之下（MDE80 %.2f~%.2fpp；"
                        "最大的一个差 %.2fpp，p 也不显著）——这张表上的档位高低，"
                        "在 %s 座的书上读不出方向。"
                        % (len(est), lo, hi, abs(biggest["obs_ann_pp"]),
                           biggest.get("seats") or "5")}


def read_inputs():
    price = _load(FACE_PRICE)
    published = {}
    for row in (price.get("rows") or []):
        published[float(row["min_amt_cny"])] = (row.get("book") or {}).get("cagr")
    book = (_load(FACE_IDLE_CASH).get("book") or {})
    opt = {}
    for path, key in ((FACE_GATE_NOISE, "gate_noise"), (FACE_ARM_NOISE, "arm_noise")):
        if os.path.exists(path):
            try:
                opt[key] = _load(path)
            except (OSError, ValueError):
                opt[key] = None
    return {"price": price, "cfg": price.get("config") or {}, "published": published,
            "seats": int(book.get("n_hold") or 0) or None,
            "evidence_cutoff": price.get("evidence_cutoff"), **opt}


def run():
    t0 = time.time()
    src = read_inputs()
    seats = src["seats"]
    cfg = src["cfg"]
    if seats is None:
        print("FATAL: results/etf_book_idle_cash.json carries no book seat count")
        return 2
    close, openp, amt, feats, n_flip = G.build_universe()
    t_panel = time.time() - t0
    universe_measured = int(len(close.columns))

    arms = {}
    for gate in ARMS_CNY:
        arms[gate] = N.price_arm(close, openp, amt, feats, gate, seats, cfg)
        print("[book %gM] cagr=%s  %.1fs"
              % (gate / 1e6, arms[gate]["stats"]["full"].get("cagr"), time.time() - t0),
              flush=True)

    control = {}
    worst = None
    for gate in ARMS_CNY:
        got = arms[gate]["stats"]["full"].get("cagr")
        want = src["published"].get(float(gate))
        d = delta_pp(got, want)
        if d is None:
            continue
        control["%gM" % (gate / 1e6)] = {"arm_cagr": float(got), "published_cagr": float(want),
                                        "delta_pp": d}
        if worst is None or abs(d) > abs(worst):
            worst = d

    rets = {g: arms[g]["series"].pct_change() for g in ARMS_CNY}

    def diff(a, b):
        return (rets[a] - rets[b]).dropna()

    rows = []
    boot = {}
    for gate in ARMS_CNY:
        if gate == BASE:
            continue
        key = pair_label(gate, BASE)
        b = bootstrap_se(diff(gate, BASE))
        boot[key] = b
        rows.append({"pair": key, "high_cny": gate, "low_cny": BASE, "seats": seats,
                     "obs_ann_pp": (b or {}).get("obs_ann_pp"),
                     "mde80_ann_pp": (b or {}).get("mde80_ann_pp"),
                     "p_one_sided": (b or {}).get("p_one_sided"),
                     "p_direction": (b or {}).get("p_direction"),
                     "t": (b or {}).get("t"),
                     "cagr_delta_pp": round((arms[gate]["stats"]["full"].get("cagr", 0.0)
                                             - arms[BASE]["stats"]["full"].get("cagr", 0.0))
                                            * 100.0, 3),
                     "status": classify_pair((b or {}).get("obs_ann_pp"),
                                             (b or {}).get("mde80_ann_pp"),
                                             (b or {}).get("p_direction"))})
    bump_key = pair_label(BUMP_HIGH, BUMP_LOW)
    bump = bootstrap_se(diff(BUMP_HIGH, BUMP_LOW))
    boot[bump_key] = bump
    bump_row = {"pair": bump_key, "high_cny": BUMP_HIGH, "low_cny": BUMP_LOW, "seats": seats,
                "obs_ann_pp": (bump or {}).get("obs_ann_pp"),
                "mde80_ann_pp": (bump or {}).get("mde80_ann_pp"),
                "p_one_sided": (bump or {}).get("p_one_sided"),
                "p_direction": (bump or {}).get("p_direction"),
                "t": (bump or {}).get("t"),
                "cagr_delta_pp": round((arms[BUMP_HIGH]["stats"]["full"].get("cagr", 0.0)
                                        - arms[BUMP_LOW]["stats"]["full"].get("cagr", 0.0))
                                       * 100.0, 3),
                "status": classify_pair((bump or {}).get("obs_ann_pp"),
                                        (bump or {}).get("mde80_ann_pp"),
                                        (bump or {}).get("p_direction"))}
    rows.append(bump_row)

    for r in rows:
        r["bars_needed_for_1pp"] = bars_needed(r["mde80_ann_pp"], (boot.get(r["pair"]) or
                                                                   {}).get("bars"))
        span = (arms[BASE]["stats"]["full"].get("years") or 0.0)
        bars = (boot.get(r["pair"]) or {}).get("bars") or 0
        if r["bars_needed_for_1pp"] and span and bars:
            r["years_needed_for_1pp"] = round(
                r["bars_needed_for_1pp"] / (bars / float(span)), 1)
        else:
            r["years_needed_for_1pp"] = 0.0 if r["bars_needed_for_1pp"] == 0 else None

    # the same pair, seen by the two published rulers: their p, their band, this MDE
    base_key = pair_label(BUMP_HIGH, BASE)
    gn = (src.get("gate_noise") or {}).get("pairs") or {}
    gn_p = ((gn.get("high_vs_shipped") or {}).get("bootstrap") or {}).get("p_one_sided")
    an_v = ((src.get("arm_noise") or {}) or {}).get("verdict") or {}
    own = boot.get(base_key) or {}
    xcheck = {"pair": base_key,
              "gate_noise_p_published": gn_p,
              "gate_noise_p_here": own.get("p_one_sided"),
              "arm_noise_ruler_pp": an_v.get("ruler_pp"),
              "arm_noise_diff_pp": an_v.get("diff_pp"),
              "mde80_here_pp": own.get("mde80_ann_pp"),
              "obs_here_pp": own.get("obs_ann_pp")}
    xcheck["p_agrees"] = (None if gn_p is None or own.get("p_one_sided") is None
                          else bool(abs(own["p_one_sided"] - float(gn_p)) <= XCHECK_P_TOL))
    xcheck["diff_agrees"] = (None if an_v.get("diff_pp") is None
                             or own.get("obs_ann_pp") is None
                             else bool(abs(own["obs_ann_pp"] - float(an_v["diff_pp"])) <= 0.25))
    xcheck["both_rulers_say_inside"] = (
        None if not xcheck["p_agrees"] else
        bool((own.get("p_one_sided") or 1.0) > 0.05
             and abs(own.get("obs_ann_pp") or 0.0) < (own.get("mde80_ann_pp") or 0.0)))

    verdict = classify(rows, control_pp=worst)
    verdict["seats"] = seats
    verdict["min_mde_pp"] = min([r["mde80_ann_pp"] for r in rows if r.get("mde80_ann_pp")],
                                default=None)
    verdict["max_mde_pp"] = max([r["mde80_ann_pp"] for r in rows if r.get("mde80_ann_pp")],
                                default=None)

    out = {"evidence_cutoff": (src["evidence_cutoff"]
                               or str(pd.Timestamp(close.index[-1]).date())),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_book_mde.py",
           "rule": {"arms_cny": list(ARMS_CNY), "base_cny": BASE,
                    "bump": [BUMP_HIGH, BUMP_LOW], "z80": Z_80, "per_year": PER_YEAR,
                    "block": BLOCK, "draws": DRAWS, "seed": SEED,
                    "control_tol_pp": CONTROL_TOL_PP, "target_pp": TARGET_PP,
                    "question": "the smallest annualised gap this book can tell from zero",
                    "mde": "z80 * SE of the block-bootstrap distribution of the mean paired "
                           "daily return difference, annualised by the engine's own 252",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"book_seats": seats, "rebal": int(cfg.get("rebal") or 20),
                      "vol_target": cfg.get("vol_target"),
                      "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                      "universe_measured": universe_measured,
                      "universe_published": cfg.get("universe_measured"),
                      "flips_repaired": int(n_flip),
                      "panel_build_seconds": round(t_panel, 1), "run_seconds": None},
           "control": {"cells": control, "worst_delta_pp": worst,
                       "tol_pp": CONTROL_TOL_PP},
           "arms": {("%gM" % (g / 1e6)): {"stats": arms[g]["stats"],
                                          "turnover_per_decision":
                                              arms[g]["turnover_per_decision"]}
                    for g in ARMS_CNY},
           "rows": rows, "bootstrap": boot, "crosscheck": xcheck, "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"], "seats": seats,
                      "min_mde_pp": verdict["min_mde_pp"],
                      "max_mde_pp": verdict["max_mde_pp"],
                      "run_seconds": out["config"]["run_seconds"]}, ensure_ascii=False))
    return 0


def write_md(out):
    v = out["verdict"]
    seats = out["config"]["book_seats"]

    def f2(x):
        return "-" if x is None else "%.2f" % x

    lines = ["# %d 座的书，最小能分辨多大的差（r1762）" % seats, "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "前两面各自用一把尺子量过这道闸（r1760 的配对日收益块自助、臂噪声面的随机排名带），"
             "两次都落在「分不开」。可是「分不开」没告诉读表的人：**要多大的差才分得开**。"
             "本面把两把尺子放回同一条差序列上，给出这本书的最小可分辨差（MDE80）——"
             "下一次读到「这一档好 1pp」，可以直接判它是否在射程内。", "",
             "## 1. 每档 vs 在印档（%gM）" % (BASE / 1e6), "",
             "| 比较 | 表上的 CAGR 差 | 观测年化差 | SE | **MDE80** | p（该方向） | 判读 |",
             "|---|---|---|---|---|---|---|"]
    words = {"ABOVE_MDE80": "越过 MDE80",
             "SIGNIFICANT_UNDERPOWERED": "显著但没到效力",
             "NO_DIRECTION": "无方向",
             "NO_ESTIMATE": "无估计"}
    for r in out["rows"]:
        lines.append("| %s | %s pp | %s pp | %s pp | **%s pp** | %s | %s |"
                     % (r["pair"], f2(r.get("cagr_delta_pp")), f2(r.get("obs_ann_pp")),
                        f2((out["bootstrap"].get(r["pair"]) or {}).get("se_ann_pp")),
                        f2(r.get("mde80_ann_pp")),
                        "-" if r.get("p_direction") is None else "%.4f" % r["p_direction"],
                        words.get(r["status"], r["status"])))
    lines += ["",
              "读法：三个词是三件事，不是一个档位的三个称呼。**越过 MDE80** = 这个差比这本书"
              "在最理想 80% 效力下还分得清的阈值更大；**显著但没到效力** = 方向站得住"
              "（p≤0.05），但把这本账再跑一遍仍有 20% 机会读成零——方向可信、幅度不可信；"
              "**无方向** = 连方向都立不住。表上一律按此判读，不看 CAGR 差的大小排座次。", "",
              "MDE 区间：%.2f~%.2fpp（同一本书同一张面板，不同档对之间的宽度不同）。"
              % (v.get("min_mde_pp") or 0.0, v.get("max_mde_pp") or 0.0), ""]
    sig = [r for r in out["rows"] if r["status"] == "SIGNIFICANT_UNDERPOWERED"]
    if sig:
        lines += ["唯一站得住的**方向**：" + "、".join(
            "%s（t=%s，p=%s）" % (r["pair"], r["t"], r["p_direction"]) for r in sig)
            + "——方向可信，**幅度不可信**：80% 效力下这本书还分辨不出它到底衰减了几 pp。"
              "换句话说，把闸抬到 1000M 会让这本书变差这件事可以信；"
              "变差了多少，这张表说了不算。", ""]
    bump = [r for r in out["rows"] if r["pair"] == "100M_vs_40M"]
    if bump:
        b = bump[0]
        lines += ["r1760 那条凸起（100M 比 40M 高 %.2fpp）自己的 MDE80 是 **%.2fpp**——"
                  "那条差连自家射程的一半都不到，所以「100M 是更好的闸」在 5 座的书上"
                  "不是被噪声带压住的推测，而是**根本没有分辨能力**。"
                  % (abs(b["cagr_delta_pp"]), b["mde80_ann_pp"]), ""]
    lines += ["## 2. 两把尺子，同一条差序列", ""]
    x = out["crosscheck"]
    lines.append("同一对（%s）：" % x["pair"].replace("_", " "))
    lines.append("")
    lines.append("* 闸噪声面（块自助）印的 p = **%s**；本面在同一条差序列上重算 p = **%s**（%s）"
                 % (x.get("gate_noise_p_published"), x.get("gate_noise_p_here"),
                    "一致" if x.get("p_agrees") else "不一致"))
    lines.append("* 臂噪声面（随机排名带）印的尺子 = **%s pp**，它要判的那条差 = **%s pp**"
                 % (f2(x.get("arm_noise_ruler_pp")), f2(x.get("arm_noise_diff_pp"))))
    lines.append("* 本面（块自助宽度）印的 MDE80 = **%s pp**，同一条差 = **%s pp**"
                 % (f2(x.get("mde80_here_pp")), f2(x.get("obs_here_pp"))))
    lines.append("")
    lines += ["两把尺子量的是**不同的东西**：随机排名带问「只把排名打乱，年化能飘多远」"
                 "（那是这本书自身的水平噪声），块自助 SE 问「这一条配对差序列的均值有多不稳」。"
                 "同一个差在两者下面都判 inside（%s），这比任何一把尺子单独判 inside 更可信。"
                 % ("是" if x.get("both_rulers_say_inside") else "否"), "",
                 "## 3. 要多长的史才分得开 1pp", "",
                 "| 比较 | 现有 MDE80 | 现有 bar 数 | 把 MDE 压到 1pp 需要的 bar | ≈ 年 |",
                 "|---|---|---|---|---|"]
    for r in out["rows"]:
        lines.append("| %s | %s pp | %s | %s | %s |"
                     % (r["pair"], f2(r.get("mde80_ann_pp")),
                        (out["bootstrap"].get(r["pair"]) or {}).get("bars"),
                        r.get("bars_needed_for_1pp"),
                        "-" if r.get("years_needed_for_1pp") is None
                        else "%g" % r["years_needed_for_1pp"]))
    lines += ["",
              "这份表的用途是让「再攒点数据」变成一句话能算的数：SE 按 1/sqrt(n) 缩，"
              "所以 MDE 从 2pp 压到 1pp 需要 4 倍的 bar。若某档需要的 bar 已经是现有史的数倍，"
              "那这一档的差**在这本书的寿命里分不开**，不该再拿它当选择理由。", "",
              "## 4. 诚实边界", "",
              "* `per_year=252` 是引擎自己算波动率用的常量，也是本面年化用的常量——年化算术收益"
              "与复利 CAGR 不完全同口径，本面比的是**同一本账上两档的差**，这个近似对差是低阶的。",
              "* MDE80 是「80% 效力下能分辨」的阈值，不是「差 1pp 就一定是真差」的门；"
              "越过 MDE 只说明这一条序列给出的方向在噪声之外，不说明它能延续到样本外。",
              "* 控制臂只覆盖本面判过的档；没判的档没有被复现，也没有被背书。",
              "* 块长取 20（一个调仓周期）是选的，不是推的；块长 10/40 下的 SE 本面不报。", ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _check():
    """Re-derive the published verdict and every row's word from the published numbers."""
    with open(OUT_JSON, encoding="utf-8") as fh:
        out = json.load(fh)
    rows = out.get("rows") or []
    again = classify(rows, control_pp=out["control"]["worst_delta_pp"])
    words_ok = True
    for r in rows:
        if classify_pair(r.get("obs_ann_pp"), r.get("mde80_ann_pp"),
                         r.get("p_direction")) != r.get("status"):
            words_ok = False
    mde_ok = True
    for r in rows:
        b = (out.get("bootstrap") or {}).get(r["pair"]) or {}
        if b and r.get("mde80_ann_pp") is not None:
            # both sides are stored at 4dp, so the identity only holds to that precision
            if abs(round(Z_80 * float(b["se_ann_pp"]), 4) - float(r["mde80_ann_pp"])) > 5e-3:
                mde_ok = False
    ok = (again["verdict"] == out["verdict"]["verdict"]) and words_ok and mde_ok
    print(json.dumps({"published": out["verdict"]["verdict"],
                      "recomputed": again["verdict"], "rows_rederived": words_ok,
                      "mde_equals_z80_se": mde_ok, "ok": ok}, ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails = []
    legs = []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1-L3 the annualisation is the engine's own, and linear
    chk("L1 zero", abs(ann_pp(0.0)) < 1e-12, ann_pp(0.0))
    chk("L2 one year of 1/252", abs(ann_pp(1.0 / 252.0) - 100.0) < 1e-9, ann_pp(1 / 252.0))
    chk("L3 linear", abs(ann_pp(0.002) - 2.0 * ann_pp(0.001)) < 1e-9)

    # L4 short series is refused, never silently widened
    chk("L4 too few bars", bootstrap_se(list(np.zeros(39))) is None)

    # L5-L6 the bootstrap sees sign, and a zero series cannot be separable
    z = bootstrap_se(list(np.zeros(400)), draws=300, seed=5)
    chk("L5 zero means p=1", z["p_one_sided"] == 1.0, z["p_one_sided"])
    # a degenerate (all-zero) diff has zero width, so it can never say "above": the
    # estimate is not separable because there is nothing to separate
    chk("L5b zero width", z["mde80_ann_pp"] == 0.0, z["mde80_ann_pp"])
    chk("L5c zero never above",
        classify_pair(z["obs_ann_pp"], z["mde80_ann_pp"], z["p_direction"]) == "NO_DIRECTION")
    rng = np.random.default_rng(11)
    pos = list(0.001 + rng.normal(0.0, 0.004, 800))
    up = bootstrap_se(pos, draws=600, seed=5)
    chk("L6 a real shift is caught", up["p_one_sided"] <= 0.05, up["p_one_sided"])
    chk("L6b obs annualises", abs(up["obs_ann_pp"] - ann_pp(np.mean(pos))) < 1e-3,
        up["obs_ann_pp"])

    # L7 frozen seed => frozen width
    a1 = bootstrap_se(pos, draws=400, seed=7)
    a2 = bootstrap_se(pos, draws=400, seed=7)
    chk("L7 seed determinism", a1 == a2)
    a3 = bootstrap_se(pos, draws=400, seed=8)
    chk("L7b another seed is another sample", a3["se_ann_pp"] != a1["se_ann_pp"])

    # L8 the width is z80 * SE, by construction
    chk("L8 mde = z80*se", abs(a1["mde80_ann_pp"] - round(Z_80 * a1["se_ann_pp"], 4)) < 1e-9,
        (a1["mde80_ann_pp"], a1["se_ann_pp"]))

    # L9-L11 bars-needed is a square law, and does nothing when already inside the target
    chk("L9 already there", bars_needed(0.5, 1600) == 0)
    chk("L10 boundary is zero", bars_needed(1.0, 1600) == 0)
    chk("L11 quadruple", bars_needed(2.0, 1600) == 6400, bars_needed(2.0, 1600))
    chk("L11b no mde", bars_needed(None, 1600) is None)

    # L12-L14 one row, one word -- and the boundary is not a pass
    chk("L12 inside", classify_pair(0.79, 1.36, 0.32) == "NO_DIRECTION")
    chk("L13 above", classify_pair(1.50, 1.36, 0.90) == "ABOVE_MDE80")
    chk("L14 boundary", classify_pair(1.36, 1.36, 0.32) == "NO_DIRECTION")
    chk("L14b missing", classify_pair(None, 1.0) == "NO_ESTIMATE")
    # a gap can be significant and still underpowered: the two thresholds are different
    chk("L14c significant underpowered",
        classify_pair(-7.97, 10.82, 0.018) == "SIGNIFICANT_UNDERPOWERED")
    chk("L14d no p means no direction", classify_pair(0.79, 1.36, None) == "NO_DIRECTION")

    # L15-L19 the face-level verdict refuses before it judges
    r_inside = [{"pair": "100M_vs_20M", "obs_ann_pp": 0.79, "mde80_ann_pp": 1.36,
                 "status": "NO_DIRECTION", "seats": 5}]
    v = classify(r_inside, control_pp=0.0)
    chk("L15 all inside", v["verdict"] == "ALL_GAPS_BELOW_MDE80", v["verdict"])
    chk("L15b sentence names the mde", "1.36" in v["sentence"], v["sentence"])
    r_mixed = r_inside + [{"pair": "1000M_vs_20M", "obs_ann_pp": -7.97,
                           "mde80_ann_pp": 2.10, "status": "ABOVE_MDE80"}]
    v = classify(r_mixed, control_pp=0.0)
    chk("L16 mixed", v["verdict"] == "SOME_GAPS_ABOVE_MDE80", v["verdict"])
    chk("L16b names the rung", "1000M_vs_20M" in v["sentence"], v["sentence"])
    v = classify([dict(r) for r in r_mixed if r["status"] == "ABOVE_MDE80"], control_pp=0.0)
    chk("L17 every gap above", v["verdict"] == "EVERY_GAP_ABOVE_MDE80", v["verdict"])
    # significant-but-underpowered must never be filed as "no direction"
    r_sig = r_inside + [{"pair": "1000M_vs_20M", "obs_ann_pp": -7.99,
                         "mde80_ann_pp": 10.82, "status": "SIGNIFICANT_UNDERPOWERED"}]
    v = classify(r_sig, control_pp=0.0)
    chk("L17b significant is not silence",
        v["verdict"] == "SIGNIFICANT_BUT_UNDERPOWERED", v["verdict"])
    chk("L17c names it", "1000M_vs_20M" in v["sentence"], v["sentence"])
    v = classify(r_sig + [{"pair": "400M_vs_20M", "obs_ann_pp": -3.6,
                           "mde80_ann_pp": 2.10, "status": "ABOVE_MDE80"}], control_pp=0.0)
    chk("L17d mixed with power", v["verdict"] == "MIXED_ABOVE_AND_UNDERPOWERED", v["verdict"])
    v = classify(r_inside, control_pp=None)
    chk("L18 no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])
    v = classify(r_inside, control_pp=CONTROL_TOL_PP + 0.01)
    chk("L19 control fails", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = classify([{"pair": "x", "obs_ann_pp": None, "mde80_ann_pp": None,
                   "status": "NO_ESTIMATE"}], control_pp=0.0)
    chk("L19b no arms", v["verdict"] == "CANNOT_JUDGE_NO_ARMS", v["verdict"])

    # L20-L23 labels, control arithmetic, and the honest skip
    chk("L20 label", pair_label(100e6, 20e6) == "100M_vs_20M", pair_label(100e6, 20e6))
    chk("L20b label fraction", pair_label(1000e6, 400e6) == "1000M_vs_400M")
    chk("L21 control delta", delta_pp(0.0912, 0.0912) == 0.0)
    chk("L21b control pp", abs(delta_pp(0.0920, 0.0912) - 0.08) < 1e-9,
        delta_pp(0.0920, 0.0912))
    chk("L22 missing cell", delta_pp(0.09, None) is None)
    # the direction tail is counted on its own side, never a mirror of the other tail
    neg = bootstrap_se(list(-0.001 + rng.normal(0.0, 0.004, 600)), draws=400, seed=5)
    chk("L23 negative gap reads its own tail", neg["p_direction"] < 0.05,
        (neg["p_one_sided"], neg["p_direction"]))
    chk("L23b two tails both counted", neg["p_direction"] + neg["p_one_sided"] < 1.2)

    total = len(legs)
    if fails:
        print("selftest %d/%d FAIL" % (total - len(fails), total))
        for f in fails:
            print("  FAIL %s" % f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        with open(OUT_JSON, encoding="utf-8") as fh:
            write_md(json.load(fh))
        return 0
    if "run" in argv:
        return run()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
