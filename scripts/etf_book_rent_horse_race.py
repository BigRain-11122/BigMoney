#!/usr/bin/env python
"""etf_book_rent_horse_race -- does the tuning pay for its own search rent?

Why this face exists
--------------------
r1960 priced the production book's search rent (N* ~ 5 tries at DSR 0.95) and r1962/r1963
turned that into money: 1.80%/yr after 58 audited tries, 237 CNY/yr over parking, against a
19.1% one-year tail. Every one of those faces compares the *tuned* book against cash. None
of them compares it against a book that costs almost nothing to find. That is the question a
desk actually has to answer before it keeps tuning: if a rule with one or six tries earns
more after its own much smaller rent, the extra factors were not discovery -- they were the
rent.

What this face publishes
------------------------
1. **Four arms priced in the same frame** (1,000,000 CNY, same panel repair, same
   liquidity/history screen, same 20-bar rebalance, 5 names, 10bp/side, 8% vol cap):
   the tuned six-factor composite, `mom_12_1` alone, `vol_60` alone (low-vol), and the
   whole eligible pool equal-weight (no sort at all).
2. **Each arm charged its own trial count** -- the tuned book 58 (the audited
   prereg-file count r1960 already publishes), each single factor 6 (the six factors in
   `SIGNS` were all examined; taking one is one of six tries), equal weight 1 (no sort,
   no choice, the universe rule is fixed by liquidity).
3. **Deflated Sharpe -> money** through `book_deflated_expectation._haircut_row`, so the
   haircut and the tail arithmetic have exactly one implementation in this repo.
4. **N_max**: the largest trial count at which the tuned book would still beat the best
   low-rent arm. If our audited count is above it, tuning destroyed value.

Frozen before the first run (check() refuses a face whose echoed criteria differ):
    ARM_TRIALS, CAPITAL, ABANDON_P, DSR_LINE, MIN_BARS, REBAL, N_HOLD, COST, VOL_TARGET,
    ALIGN_TOL_PP, SR_TOL, CONTROL_PARENT.

Usage:
    python scripts/etf_book_rent_horse_race.py run
    python scripts/etf_book_rent_horse_race.py check
    python scripts/etf_book_rent_horse_race.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (HERE, ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

OUT_JSON = ROOT / "results" / "etf_book_rent_horse_race.json"
OUT_MD = ROOT / "research" / "ETF-BOOK-RENT-HORSE-RACE.md"
FACE = "results/etf_book_rent_horse_race.json"
SCRIPT = "scripts/etf_book_rent_horse_race.py"
CONTROL_PARENT = "results/etf_book_production/PRODUCTION-2026-11-20.json"

REBAL = 20
N_HOLD = 5
COST = 0.0010
VOL_TARGET = 0.08
CAPITAL = 1_000_000.0
ABANDON_P = 0.05
DSR_LINE = 0.95
MIN_BARS = 250
ALIGN_TOL_PP = 0.05      # our control arm's CAGR vs the published parent, percentage points
SR_TOL = 0.02            # our control arm's Sharpe vs the published parent

# n_trials charged per arm -- the whole point of the face. Written before the first run.
ARM_TRIALS = {
    "tuned_composite_6": 58,   # audited prereg-file count (r1960 definition), conservative
    "single_mom_12_1": 6,      # one of the six factors in SIGNS
    "single_vol_60_low": 6,    # one of the six factors in SIGNS
    "random_pick_5": 1,        # a coin: nothing was searched, so there is nothing to charge
}
RANDOM_DRAWS = 8               # coin tosses averaged; averaging is not a search, N stays 1

CRITERIA = {
    "capital_cny": CAPITAL,
    "abandon_p": ABANDON_P,
    "dsr_line": DSR_LINE,
    "min_bars": MIN_BARS,
    "rebal_bars": REBAL,
    "n_hold": N_HOLD,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": VOL_TARGET,
    "arm_trials": ARM_TRIALS,
    "align_tol_pp": ALIGN_TOL_PP,
    "sr_tol": SR_TOL,
    "control_parent": CONTROL_PARENT,
    "haircut": "book_deflated_expectation._haircut_row (single implementation)",
    "frozen": "constants above were written before the first run",
}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def _load(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ arithmetic (pure)
def small_stats(series):
    """Stats straight from `etf_equity_alpha.stats2` -- the repo's own annualisation.

    CAGR has to be day-based: a 1,666-bar curve spans 6.88 calendar years, not 6.61, so
    `252/bars` inflates the number by ~0.5pp. That is a second implementation of the same
    arithmetic, which is exactly how two faces end up disagreeing -- so the production
    helper is called instead, and the manual path survives only for a flat synthetic curve
    that stats2 refuses (<40 rows).
    """
    import etf_equity_alpha as A

    s = pd.Series(series, dtype="float64").dropna()
    if len(s) >= 40 and isinstance(s.index, pd.DatetimeIndex):
        m = A.stats2(s, "arm")
        return {"cagr": float(m["cagr"]), "vol": float(m["vol"]),
                "sharpe": float(m["sharpe"]), "maxdd": float(m["maxdd"]),
                "bars": len(s) - 1}
    if len(s) < 3:
        raise ValueError("series too short")
    rets = s.pct_change().dropna()
    vol = float(rets.std(ddof=1)) * math.sqrt(252.0) if len(rets) > 1 else 0.0
    sharpe = (float(rets.mean()) / float(rets.std(ddof=1)) * math.sqrt(252.0)
              if len(rets) > 1 and rets.std(ddof=1) else 0.0)
    return {"cagr": 0.0, "vol": vol, "sharpe": sharpe,
            "maxdd": float((s / s.cummax() - 1.0).min()), "bars": len(rets)}


def credible(arm, capital=CAPITAL, abandon_p=ABANDON_P):
    """Deflated Sharpe -> budgetable money, reusing the r1962 implementation verbatim."""
    import book_deflated_expectation as B
    import science_gates as SG

    rets = pd.Series(arm["returns"], dtype="float64").dropna()
    d = SG.deflated_sharpe_ratio(rets.tolist(), int(arm["n_trials"]))
    row = B._haircut_row(arm["sharpe"], arm["vol"], d["sigma_sr"], int(arm["n_trials"]),
                         capital, 1.0, abandon_p)
    row["dsr_raw"] = round(float(d["dsr"]), 6)
    row["sr_star_ann_from_returns"] = round(float(d["sr_star"]) * math.sqrt(252.0), 4)
    return row


def verdict(rows):
    """Frozen decision rule; rows are the printed haircut rows of every arm."""
    tuned = [r for r in rows if r["arm"] == "tuned_composite_6"]
    others = [r for r in rows if r["arm"] != "tuned_composite_6"]
    if not tuned:
        return {"verdict": "NO_TUNED_ARM", "why": "the tuned arm is the one being defended"}
    t = tuned[0]
    best = max(others, key=lambda r: r["money_on_capital"]) if others else None
    if best is None:
        return {"verdict": "NO_RIVAL_ARM", "why": "nothing to race"}
    if t["money_on_capital"] <= 0 and all(r["money_on_capital"] <= 0 for r in others):
        return {"verdict": "NOTHING_SURVIVES_THE_RENT", "why": "every arm deflates to zero",
                "tuned_money": t["money_on_capital"], "best_rival": best["arm"],
                "rival_money": best["money_on_capital"]}
    if t["money_on_capital"] > best["money_on_capital"]:
        return {"verdict": "TUNING_PAYS_FOR_ITS_RENT",
                "why": "the tuned book keeps the most money after each arm's own rent",
                "tuned_money": t["money_on_capital"], "best_rival": best["arm"],
                "rival_money": best["money_on_capital"]}
    if t["money_on_capital"] == best["money_on_capital"]:
        # a tie is not a win: the simpler arm is the default when both keep the same money
        return {"verdict": "TUNING_TIES_A_SIMPLER_ARM",
                "why": "%s keeps the same money for a fraction of the rent" % best["arm"],
                "tuned_money": t["money_on_capital"], "best_rival": best["arm"],
                "rival_money": best["money_on_capital"], "gap_cny": 0.0}
    return {"verdict": "THE_RENT_EATS_THE_TUNING",
            "why": "%s keeps more money after a much smaller rent" % best["arm"],
            "tuned_money": t["money_on_capital"], "best_rival": best["arm"],
            "rival_money": best["money_on_capital"],
            "gap_cny": round(t["money_on_capital"] - best["money_on_capital"], 2)}


def n_max_beats(tuned_arm, target_money, capital=CAPITAL, abandon_p=ABANDON_P, hi=400):
    """Largest N at which the tuned book still beats target_money; None if none does."""
    last = None
    for n in range(1, hi + 1):
        arm = dict(tuned_arm)
        arm["n_trials"] = n
        row = credible(arm, capital, abandon_p)
        if row["money_on_capital"] > target_money:
            last = n
        elif last is not None:
            break
    return last


# ------------------------------------------------------------------------ panel arms
def _scores(close, amt, feats):
    """Every arm's score matrix on the production universe (one eligibility mask)."""
    import etf_composite_pf as E

    cols = close.columns
    idx = close.index
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    out = {}
    out["tuned_composite_6"] = E.build_score(close, amt, feats)

    def one(name, sign):
        f = feats.get(name)
        if f is None:
            raise RuntimeError("factor %s missing from compute_all" % name)
        f = f.reindex(index=idx, columns=cols)
        z = (f.rank(axis=1, pct=True) - 0.5) * 2.0
        return (sign * z).where(elig)

    out["single_mom_12_1"] = one("mom_12_1", +1.0)
    out["single_vol_60_low"] = one("vol_60", -1.0)
    return out, elig


def _random_score(close, elig, draw):
    """A coin with no memory: every rebalance draws a fresh random rank for every symbol."""
    rng = np.random.default_rng(90210 + int(draw))
    mat = rng.random((len(close.index), len(close.columns)))
    return pd.DataFrame(mat, index=close.index, columns=close.columns).where(elig)


def _arm_series(close, openp, amt, score, n_hold):
    import etf_robust_pf as R

    diag = []
    ser, _turn = R.open_to_open_equity(
        close, openp, amt, score, REBAL, n_hold, COST, vol_target=VOL_TARGET, diag=diag)
    return ser


def build(write=True, verbose=True):
    import etf_composite_pf as E
    import etf_equity_alpha as A
    import etf_book_production as P

    t0 = time.time()
    # One panel build, then the production face's own repair + class filter, so this race
    # prices the universe the card prices (a raw unfiltered panel would read ~2.6pp low and
    # every arm here would be quoting a book nobody funds).
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols_keep = [c for c in close.columns if cls[c] in P.USE_CLASSES]
    close, openp, amt = close[cols_keep], openp[cols_keep], amt[cols_keep]
    feats = {k: v.reindex(columns=cols_keep) for k, v in feats.items()}

    scores, elig = _scores(close, amt, feats)
    scores["tuned_composite_6"] = E.build_score(close, amt, feats)
    n_pool = int(len(close.columns))

    arms = {}

    def _record(name, ser):
        st = small_stats(ser)
        rets = pd.Series(ser.values, dtype="float64").pct_change().dropna()
        arms[name] = {
            "arm": name,
            "n_trials": ARM_TRIALS[name],
            "n_hold": N_HOLD,
            "cagr": round(st["cagr"], 6),
            "vol": round(st["vol"], 6),
            "sharpe": round(st["sharpe"], 4),
            "maxdd": round(st["maxdd"], 6),
            "bars": st["bars"],
            "returns": [float(x) for x in rets.values],
        }
        if verbose:
            print("  %-20s cagr %.2f%% vol %.2f%% SR %.3f maxdd %.2f%% (N=%d)"
                  % (name, 100 * st["cagr"], 100 * st["vol"], st["sharpe"],
                     100 * st["maxdd"], ARM_TRIALS[name]), flush=True)

    for name in ("tuned_composite_6", "single_mom_12_1", "single_vol_60_low"):
        _record(name, _arm_series(close, openp, amt, scores[name], N_HOLD))

    # the coin: RANDOM_DRAWS books, each re-picking 5 names every rebalance, averaged
    curves = []
    for k in range(RANDOM_DRAWS):
        ser = _arm_series(close, openp, amt, _random_score(close, elig, k), N_HOLD)
        curves.append(ser.reindex(close.index).ffill())
    coin = pd.concat(curves, axis=1).mean(axis=1).dropna()
    _record("random_pick_5", coin)

    rows = []
    for name, arm in arms.items():
        row = credible(arm)
        row["arm"] = name
        row["n_hold"] = arm["n_hold"]
        row["cagr"] = arm["cagr"]
        row["vol"] = arm["vol"]
        row["sharpe"] = arm["sharpe"]
        row["maxdd"] = arm["maxdd"]
        rows.append(row)

    # Control A (construction): the production wrapper must price my arm identically. This
    # is the leg that proves the four arms ride the published engine and not a copy of it.
    control_twin = {"source": "etf_book_production.backtest (in-process)",
                    "parent_cagr": None, "parent_sharpe": None,
                    "delta_pp": None, "delta_sr": None, "aligned": None}
    try:
        twin, _ser_twin = P.backtest(close, openp, amt, scores["tuned_composite_6"],
                                     N_HOLD, REBAL, vol_target=VOL_TARGET)
        full = twin.get("full") or {}
        t = arms["tuned_composite_6"]
        control_twin.update({
            "parent_cagr": full.get("cagr"), "parent_sharpe": full.get("sharpe"),
            "delta_pp": round(100.0 * (t["cagr"] - float(full["cagr"])), 4),
            "delta_sr": round(t["sharpe"] - float(full["sharpe"]), 4),
        })
        control_twin["aligned"] = (abs(control_twin["delta_pp"]) <= ALIGN_TOL_PP
                                   and abs(control_twin["delta_sr"]) <= SR_TOL)
    except Exception as exc:                                        # noqa: BLE001
        control_twin["error"] = repr(exc)

    # Control B (vintage): the published tearsheet on the panel it was written on. It cannot
    # be a pass/fail line this panel can meet -- bars have been appended since -- so it is
    # printed with both cutoffs and the drift is named, not hidden (r1860 面代差 not 算法错).
    control = {"source": CONTROL_PARENT, "parent_cagr": None, "parent_sharpe": None,
               "delta_pp": None, "delta_sr": None, "aligned": None,
               "parent_cutoff": None, "panel_last_bar": str(close.index[-1].date()),
               "vintage_drift_note": None}
    rp = ROOT / CONTROL_PARENT
    if rp.exists():
        pj = _load(rp)
        full = (((pj.get("backtest") or {}).get("n5_vt08") or {}).get("full") or {})
        pc, ps = full.get("cagr"), full.get("sharpe")
        control["parent_cutoff"] = pj.get("evidence_cutoff")
        if pc is not None and ps is not None:
            t = arms["tuned_composite_6"]
            control.update({
                "parent_cagr": pc, "parent_sharpe": ps,
                "delta_pp": round(100.0 * (t["cagr"] - pc), 4),
                "delta_sr": round(t["sharpe"] - ps, 4),
            })
            same_vintage = (control["parent_cutoff"] == str(close.index[-1].date()))
            control["aligned"] = (abs(100.0 * (t["cagr"] - pc)) <= ALIGN_TOL_PP
                                  and abs(t["sharpe"] - ps) <= SR_TOL)
            control["same_vintage"] = same_vintage
            if not control["aligned"] and not same_vintage:
                control["vintage_drift_note"] = (
                    "parent was written on cutoff %s; this panel ends %s -- the drift is "
                    "attributable to bars added since, and control A is the leg that can "
                    "fail on today's panel" % (control["parent_cutoff"], control["panel_last_bar"]))

    v = verdict(rows)
    best_rival = v.get("best_rival")
    nmax = None
    if best_rival:
        rival_money = next(r["money_on_capital"] for r in rows if r["arm"] == best_rival)
        nmax = n_max_beats(arms["tuned_composite_6"], rival_money)

    face = {
        "kind": "etf-book-rent-horse-race/v1",
        "generated": _now(),
        "script": SCRIPT,
        "criteria": CRITERIA,
        "panel": {"symbols": n_pool, "bars": arms["tuned_composite_6"]["bars"],
                  "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date())},
        "evidence_cutoff": str(close.index[-1].date()),
        "control": control,
        "control_engine_twin": control_twin,
        "arms": [{k: v2 for k, v2 in r.items()} for r in rows],
        "verdict": v,
        "n_max_beats_best_rival": nmax,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if write:
        _dump(OUT_JSON, face)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text(_render_md(face), encoding="utf-8", newline="\n")
        if verbose:
            print("  -> %s" % FACE)
            print("  -> research/%s" % OUT_MD.name)
            print("  verdict %s | tuned %s CNY vs %s %s CNY | N_max=%s"
                  % (v["verdict"], v.get("tuned_money"), v.get("best_rival"),
                     v.get("rival_money"), nmax))
    return face


def _money(x):
    return "{:,.0f}".format(x)


def _render_md(face):
    v = face["verdict"]
    rows = face["arms"]
    c = face["control"]
    lines = []
    lines.append("# 调参付得起自己的搜索租金吗")
    lines.append("")
    lines.append("> 由 `%s` 渲染，数字不手抄。`generated %s`，`cutoff %s`。"
                 % (SCRIPT, face["generated"], face["evidence_cutoff"]))
    lines.append("")
    lines.append("## 一句话")
    tuned = next(r for r in rows if r["arm"] == "tuned_composite_6")
    rival = next((r for r in rows if r["arm"] == v.get("best_rival")), None)
    if v["verdict"] == "TUNING_PAYS_FOR_ITS_RENT":
        lines.append("按各自尝试次数扣完租金，六因子调参版一年还剩 **%s 元**，比第二名的 %s（%s 元）多 %s 元——调参在这里付得起自己的租金。"
                     % (_money(tuned["money_on_capital"]), rival["arm"],
                        _money(rival["money_on_capital"]),
                        _money(tuned["money_on_capital"] - rival["money_on_capital"])))
    elif v["verdict"] == "THE_RENT_EATS_THE_TUNING":
        lines.append("按各自尝试次数扣完租金，六因子调参版一年只剩 **%s 元**，而 %s 只花 %d 次尝试就剩 **%s 元**——多出来的四个因子不是发现，是租金。"
                     % (_money(tuned["money_on_capital"]), rival["arm"],
                        rival["n_trials"], _money(rival["money_on_capital"])))
    elif v["verdict"] == "TUNING_TIES_A_SIMPLER_ARM":
        lines.append("按各自尝试次数扣完租金，六因子调参版一年剩 **%s 元**，和 %s（%d 次尝试）打平——同样的钱，选便宜的那个。"
                     % (_money(tuned["money_on_capital"]), rival["arm"], rival["n_trials"]))
    else:
        lines.append("按各自尝试次数扣完租金，所有臂都归零（%s）——这本书的任何版本都不该用 100 万元去做。"
                     % v["why"])
    lines.append("")
    lines.append("## 四臂同框（同一块面板、同一道流动性门、同一套成本）")
    lines.append("")
    lines.append("| 臂 | 尝试次数 N | 年化 | 波动 | 夏普 | 最大回撤 | 扣租金夏普 | 可预算年化 | 100 万上一年 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append("| %s | %d | %.2f%% | %.2f%% | %.3f | %.2f%% | %.3f | %.2f%% | %s |"
                     % (r["arm"], r["n_trials"], 100 * r["cagr"], 100 * r["vol"],
                        r["sharpe"], 100 * r["maxdd"], r["credible_sharpe"],
                        100 * r["budgetable_cagr"], _money(r["money_on_capital"])))
    lines.append("")
    lines.append("## 调参必须多快才划算")
    if face["n_max_beats_best_rival"] is None:
        lines.append("* 在 N≤400 的任何尝试次数下，调参版都追不上 %s——不是「少试几次就好」，是这套因子本身不值这个租金。"
                     % v.get("best_rival"))
    else:
        lines.append("* 调参版只在**尝试次数 ≤ %d** 时才跑赢 %s；本司机械可数的审计尝试是 58 次。"
                     % (face["n_max_beats_best_rival"], v.get("best_rival")))
        lines.append("* 也就是说：这套六因子只有在「一眼就想到、从未试过别的组合」的世界里才值得买。")
    lines.append("")
    lines.append("## 每个 N 都从哪来")
    for name, n in ARM_TRIALS.items():
        lines.append("* `%s` → N=%d" % (name, n))
    lines.append("* 理由：调参版用 r1960 已发布的审计计数 58（prereg 文件数·取最保守的一档）；单因子 6 = SIGNS 里被一并考察过的六个因子，取其中一个是六选一；硬币 = 每条调仓日重抽 5 名，没有搜索可记，租金记 1（8 次抛币取均值只降噪，不算搜索）。")
    lines.append("")
    lines.append("## 控制腿")
    tw = face.get("control_engine_twin") or {}
    if tw.get("parent_cagr") is None:
        lines.append("* 构造腿：生产包装器读不到 → 未跑，本面数字不宣称可对账。")
    else:
        lines.append("* **构造腿**（`etf_book_production.backtest` 同进程重跑同一臂）：年化 %.2f%% / 夏普 %.3f，与本面 %.2f%% / %.3f 差 %.4fpp / %.4f → **%s**。这条腿证明四臂跑的是已发布的引擎，不是副本。"
                     % (100 * tw["parent_cagr"], tw["parent_sharpe"], 100 * tuned["cagr"],
                        tuned["sharpe"], tw["delta_pp"], tw["delta_sr"],
                        "ALIGNED" if tw["aligned"] else "MISALIGNED"))
    if c.get("parent_cagr") is None:
        lines.append("* 代差腿：父面读不到 → 未跑。")
    else:
        lines.append("* **代差腿**（发布件 `%s`，写在 cutoff %s 的面板上）：父面 年化 %.2f%% / 夏普 %.3f，本面差 %.4fpp / %.4f → %s。"
                     % (c["source"], c.get("parent_cutoff"), 100 * c["parent_cagr"],
                        c["parent_sharpe"], c["delta_pp"], c["delta_sr"],
                        "ALIGNED" if c.get("aligned") else "DIFFERS"))
        if c.get("vintage_drift_note"):
            lines.append("* 差额归因：%s。" % c["vintage_drift_note"])
    lines.append("")
    lines.append("## 不许只挑一边信")
    lines.append("* 租金是按 N 打的折，不是后验概率；本面把未扣租金的四行和扣租金的三列一起印，两面都能读。")
    lines.append("* 硬币臂（random_pick_5）=%d 次抛硬币的均值，每次调仓重抽 5 名；取均值只是降噪，不是搜索，所以 N 记 1。它测的是「这份打分有没有超过运气」，不是资产配置。")
    lines.append("* 单因子臂的 N=6 是上限估计：若这六个因子本来就来自更多次筛选，它们的租金还要更高，结论只会更偏。")
    lines.append("* 复利口径与父面一致（次日开盘成交、20 日调仓、单边 10bp）；面板修复与父面同一函数，翻价格共用。")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------- check
def check(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        print("CHECK FAILED: face missing -> %s" % p)
        return 2
    face = _load(p)
    problems = []
    if face.get("criteria") != CRITERIA:
        problems.append("criteria echo differs from this script's frozen block")
    rows = face.get("arms") or []
    if len(rows) != len(ARM_TRIALS):
        problems.append("arm count %d != %d" % (len(rows), len(ARM_TRIALS)))
    for r in rows:
        n_exp = ARM_TRIALS.get(r["arm"])
        if n_exp is None:
            problems.append("unknown arm on the face: %s" % r["arm"])
            continue
        if r["n_trials"] != n_exp:
            problems.append("%s charged N=%s, frozen N=%d" % (r["arm"], r["n_trials"], n_exp))
        # every money cell must re-derive from the printed credible Sharpe
        b_exp = max(0.0, r["sharpe"] - r["sr_star_ann"])
        if abs(b_exp - r["credible_sharpe"]) > 1e-3:
            problems.append("%s credible %.4f != max(0, %.4f-%.4f)"
                            % (r["arm"], r["credible_sharpe"], r["sharpe"], r["sr_star_ann"]))
        if abs(r["credible_sharpe"] * r["vol"] - r["budgetable_cagr"]) > 1e-4:
            problems.append("%s budgetable != credible*vol" % r["arm"])
        if abs(CAPITAL * r["budgetable_cagr"] - r["money_on_capital"]) > 1.0:
            problems.append("%s money != capital*budgetable" % r["arm"])
        if not (1 <= r["n_trials"]):
            problems.append("%s N must be >= 1" % r["arm"])
    # the verdict must be the one these printed rows imply
    want = verdict([dict(r, arm=r["arm"], money_on_capital=r["money_on_capital"]) for r in rows])
    if face.get("verdict", {}).get("verdict") != want["verdict"]:
        problems.append("verdict %s != re-derived %s"
                        % (face.get("verdict", {}).get("verdict"), want["verdict"]))
    twin = face.get("control_engine_twin") or {}
    if twin.get("parent_cagr") is None:
        problems.append("engine-twin control missing (production wrapper unreadable)")
    elif not twin.get("aligned"):
        problems.append("engine-twin control misaligned: delta %.4fpp / %.4f SR"
                        % (twin.get("delta_pp") or 0.0, twin.get("delta_sr") or 0.0))
    c = face.get("control") or {}
    if c.get("parent_cagr") is None:
        problems.append("vintage control missing (parent unreadable)")
    elif (not c.get("aligned")) and c.get("same_vintage"):
        problems.append("vintage control misaligned on its OWN vintage: delta %.4fpp"
                        % (c.get("delta_pp") or 0.0))
    if face.get("evidence_cutoff") is None:
        problems.append("evidence_cutoff missing")
    if problems:
        print("CHECK FAILED (%d)" % len(problems))
        for x in problems:
            print("  - " + x)
        return 1
    print("CHECK OK: %d arms, verdict %s, engine twin %s, vintage %s"
          % (len(rows), face["verdict"]["verdict"],
             "ALIGNED" if twin.get("aligned") else "UNALIGNED",
             "ALIGNED" if c.get("aligned") else
             ("DRIFT_NAMED" if c.get("vintage_drift_note") else "UNALIGNED")))
    return 0


# ------------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # 1. legitimate mapping arithmetic on a hand-built arm
    arm = {"arm": "x", "n_trials": 10, "sharpe": 1.10, "vol": 0.10,
           "returns": [0.001, -0.001, 0.002, -0.002, 0.0015, -0.0005] * 40}
    row = credible(arm)
    leg("budgetable == credible*vol", abs(row["credible_sharpe"] * 0.10 - row["budgetable_cagr"]) < 1e-4)
    leg("money == capital*budgetable", abs(CAPITAL * row["budgetable_cagr"] - row["money_on_capital"]) < 1.0)
    leg("credible floored at 0", row["credible_sharpe"] >= 0.0)

    # 2. rent is monotone: more tries can never raise the credible Sharpe
    a5, a50 = dict(arm, n_trials=5), dict(arm, n_trials=50)
    leg("N=50 <= N=5 credible", credible(a50)["credible_sharpe"] <= credible(a5)["credible_sharpe"] + 1e-12)

    # 3. verdicts
    def mk(name, money):
        return {"arm": name, "money_on_capital": money}
    r_tuned = mk("tuned_composite_6", 18000)
    leg("tuning wins -> TUNING_PAYS",
        verdict([r_tuned, mk("single_mom_12_1", 9000)])["verdict"] == "TUNING_PAYS_FOR_ITS_RENT")
    leg("rival wins -> RENT_EATS",
        verdict([r_tuned, mk("equal_weight_pool", 30000)])["verdict"] == "THE_RENT_EATS_THE_TUNING")
    leg("all zero -> NOTHING_SURVIVES",
        verdict([mk("tuned_composite_6", 0.0), mk("single_mom_12_1", 0.0)])["verdict"]
        == "NOTHING_SURVIVES_THE_RENT")
    leg("tie -> TUNING_TIES_A_SIMPLER_ARM (simplicity wins ties)",
        verdict([r_tuned, mk("equal_weight_pool", 18000)])["verdict"] == "TUNING_TIES_A_SIMPLER_ARM")
    v = verdict([r_tuned, mk("equal_weight_pool", 30000)])
    leg("gap_cny printed on a loss", v.get("gap_cny") == -12000.0)

    # 4. n_max_beats: at N=1 any positive target is reachable iff credible>0
    tuned_arm = {"arm": "tuned_composite_6", "sharpe": 1.10, "vol": 0.105,
                 "returns": arm["returns"]}
    nmax = n_max_beats(tuned_arm, target_money=0.0)
    leg("n_max is finite and >=1 when the book has a positive credible Sharpe", nmax is not None and nmax >= 1)
    nmax2 = n_max_beats(tuned_arm, target_money=1e12)
    leg("n_max is None when the target is unreachable", nmax2 is None)

    # 5. stats on a flat curve do not divide by zero
    st = small_stats([1.0, 1.0, 1.0, 1.0])
    leg("flat curve -> zero vol/sharpe, no crash", st["vol"] == 0.0 and st["sharpe"] == 0.0)

    # 6. renderer names the losing arm, not just the verdict token
    face = {"generated": "t", "evidence_cutoff": "c", "control": {"parent_cagr": None},
            "n_max_beats_best_rival": 3,
            "arms": [dict(row, arm="tuned_composite_6", cagr=0.1, vol=0.1, sharpe=1.1, maxdd=-0.1),
                     dict(row, arm="equal_weight_pool", cagr=0.2, vol=0.2, sharpe=0.9, maxdd=-0.2)],
            "verdict": verdict([r_tuned, mk("equal_weight_pool", 30000)])}
    md = _render_md(face)
    leg("md names the rival arm", "equal_weight_pool" in md)

    n_ok = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--face")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        build(write=True)
        return 0
    if a.cmd == "check":
        return check(a.face)
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
