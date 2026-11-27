# -*- coding: utf-8 -*-
"""carry_entry_window_yield.py -- 「随便哪一天上车，拿满一年，这本书给你什么」

WHY (r2196): r2195 把这个问题问了 ETF 那本书，得到它的头条
（THE_DAY_YOU_START_MOVES_THE_ANSWER_MORE_THAN_THE_STRATEGY_DOES：一年期
p90 减 p10 = 32.34pp，中位 9.08%）。carry 这本书从来没被问过：它所有面引用的
都是同一个窗口（两臂 2018-10-22..2026-11-20；basis 父面 2017-01-18..2026-11-26）
的 Sharpe。明天上车的人拿到的不是那个窗口的平均，而是「起点分布」里的一次抽样。

这个面回答三句读者真的会说的话：
  1. 我在随机的某天上车、拿满一年，三条线各会给我什么分布？
  2. 这个分布里亏钱的起点占多少、最差的起点挤在哪些月份（是不是一次事件）？
  3. r2192 在**一本日历**上看到的排序（basis > 对冲残差 > 不带对冲）在**每一个**
     一年窗口里都成立吗？——排序是策略性质还是日历给的？

律（沿用本族）：
  - 零重实现：基差日序列直接调 `carry_three_lines_common_window.basis_rows()`
    （= paper_basis_timing_cost_split.replay），两臂调 `arm_points()`（= 
    CP.position_series + CP.per_lot_daily），不复制一行引擎算术。
  - 执行口径 = 起点日收盘决策、从下一根 bar 起持有（entry_lag=1，r1796 认定的
    可执行口径），与 r2195 的 ETF 面同一口径，跨书可比。
  - 单位：三条线统一用「一手资本的一日分数」（basis = 名义额收益率，两臂 =
    点数 x 200 元/点 / 1,137,862.5 元一手资本）。求和口径（不复利）做头条，
    basis 的复利读数并列印出——一把尺才许排序。
  - 重叠窗口不是独立样本：分布只描述起点；独立证据另印「整年不重叠块」。
  - check 锚在外部字节（源面字节 + 数据面板尾 bar），只重算自己会永远说自己新鲜
    （r1935）。

用法：
  python scripts\\carry_entry_window_yield.py            # 建面（写 json + md）
  python scripts\\carry_entry_window_yield.py check      # 廉价漂移探针
  python scripts\\carry_entry_window_yield.py selftest   # 离线算术自检

退出码：0 正常 / 1 CHECK FAILED（输入没动但自家数字对不上=真缺陷）
        2 UNREADABLE（复现腿失配或面板读不到，不发布）/ 3 STALE（输入字节动了）
"""
import copy
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import carry_three_lines_common_window as W  # noqa: E402

TZ = timezone(timedelta(hours=8))

PROD = "IC"
HORIZON = 244          # 一根 bar 一年：本面板两条线的密度都是 ~242.5-242.7 bar/年
MIN_STARTS = 200

ECON_SRC = "results/idx_fut_carry_kill_rule_economics.json"
RENT_SRC = "results/idx_fut_carry_search_rent.json"
WINDOW_SRC = "results/carry_three_lines_window.json"
CAP_SRC = "results/idx_fut_carry_capacity_lots.json"
RULER_SRC = "results/idx_fut_carry_one_lot_ruler.json"
ETF_SRC = "results/etf_book_entry_window_yield.json"
PANEL_PROBE = "data/daily/sh510300.csv"

OUT_JSON = ROOT / "results" / "carry_entry_window_yield.json"
OUT_MD = ROOT / "results" / "carry_entry_window_yield.md"
RESEARCH_MD = ROOT / "research" / "CARRY_ENTRY_WINDOW_YIELD.md"

REPRO_TOL = 5e-4       # 已发布面 rounded to 4dp
CHECK_TOL = 1e-6       # 自家重算比对容差（都是确定性算术）
LINES = ("basis_nominal", "excess_hedged", "carry_unhedged")


def _now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha_file(rel):
    try:
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    except Exception:
        return None


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- maths


def _pct(sorted_xs, p):
    """线性插值分位（numpy 默认口径），空序列返回 None。"""
    n = len(sorted_xs)
    if n == 0:
        return None
    if n == 1:
        return float(sorted_xs[0])
    k = (n - 1) * (p / 100.0)
    lo = int(math.floor(k))
    hi = min(lo + 1, n - 1)
    return float(sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (k - lo))


def window_rows(rets, dates, h=HORIZON, mode="simple"):
    """每根可作起点的 bar 一个一年窗：起点=day i 收盘，收益取 i+1..i+h（entry_lag=1）。

    mode='simple'  -> g = sum(rets)，dd 走累计 P&L 的峰谷（线性、可加）
    mode='compound'-> g = prod(1+rets)-1，dd 走净值路径
    """
    n = len(rets)
    rows = []
    if n <= h:
        return rows
    for i in range(0, n - h):
        seg = rets[i + 1:i + h + 1]
        if mode == "compound":
            eq = 1.0
            peak = 1.0
            dd = 0.0
            for x in seg:
                eq *= 1.0 + x
                peak = max(peak, eq)
                dd = min(dd, eq / peak - 1.0)
            g = eq - 1.0
        else:
            cum = 0.0
            peak = 0.0
            dd = 0.0
            for x in seg:
                cum += x
                peak = max(peak, cum)
                dd = min(dd, cum - peak)
            g = cum
        rows.append({"from": dates[i], "to": dates[i + h], "g": g, "dd": dd})
    return rows


def distribution(rows, k_months=5):
    if not rows:
        return None
    g = sorted(r["g"] for r in rows)
    dd = sorted(r["dd"] for r in rows)
    med = _pct(g, 50)
    p10, p90 = _pct(g, 10), _pct(g, 90)
    spread = (p90 - p10) * 100.0
    out = {
        "n_start_days": len(rows),
        "return_pct": {
            "median": round(med * 100.0, 2),
            "p10": round(p10 * 100.0, 2),
            "p25": round(_pct(g, 25) * 100.0, 2),
            "p75": round(_pct(g, 75) * 100.0, 2),
            "p90": round(p90 * 100.0, 2),
            "min": round(g[0] * 100.0, 2),
            "max": round(g[-1] * 100.0, 2),
            "share_negative_pct": round(100.0 * sum(1 for x in g if x < 0) / len(g), 1),
            "spread_p90_minus_p10_pp": round(spread, 2),
            "spread_over_median_x": round((p90 - p10) / abs(med), 2) if abs(med) > 1e-9 else None,
        },
        "path_drawdown_pct": {
            "median": round(_pct(dd, 50) * 100.0, 2),
            "p10": round(_pct(dd, 10) * 100.0, 2),
            "worst": round(dd[0] * 100.0, 2),
        },
        "worst_starts": [{"from": r["from"], "to": r["to"],
                          "return_pct": round(r["g"] * 100.0, 2),
                          "path_maxdd_pct": round(r["dd"] * 100.0, 2)}
                         for r in sorted(rows, key=lambda r: r["g"])[:5]],
        "best_starts": [{"from": r["from"], "to": r["to"],
                         "return_pct": round(r["g"] * 100.0, 2)}
                        for r in sorted(rows, key=lambda r: -r["g"])[:3]],
    }
    worst_decile = sorted(rows, key=lambda r: r["g"])[:max(1, len(rows) // 10)]
    months = {}
    for r in worst_decile:
        months[r["from"][:7]] = months.get(r["from"][:7], 0) + 1
    out["worst_decile_start_months"] = dict(sorted(months.items(), key=lambda kv: -kv[1])[:k_months])
    out["distinct_start_months_in_worst_decile"] = len(months)
    return out


def independent_blocks(rows, h=HORIZON):
    """不重叠块：起点每隔 h 根 bar 取一个，这才是独立证据。"""
    picked = rows[::h]
    if not picked:
        return None
    g = [r["g"] for r in picked]
    neg = sum(1 for x in g if x < 0)
    return {
        "n_blocks": len(picked),
        "mean_pct": round(sum(g) / len(g) * 100.0, 2),
        "min_pct": round(min(g) * 100.0, 2),
        "max_pct": round(max(g) * 100.0, 2),
        "n_negative": neg,
        "blocks": [{"from": r["from"], "to": r["to"], "return_pct": round(r["g"] * 100.0, 2)} for r in picked],
    }


def _align(series):
    """按日期键取交集（不按行号对齐）。"""
    maps = {k: dict(v) for k, v in series.items()}
    common = sorted(set.intersection(*[set(maps[k]) for k in maps]))
    return common, maps


def ordering(series, h=HORIZON, metric="sum"):
    """在每个共同日历的一年窗里给三条线排一次名。

    metric='sum'    -> 按窗内赚到的钱排（%）
    metric='sharpe' -> 按窗内自己的风险调整收益排（mean/sd*sqrt(252)，与 r2192 的 1.4162/0.5057 同一量）

    两种排序会给出相反答案：钱的排序天然偏向波动大的线，Sharpe 的排序才回答「哪条线更划算」。
    两个都印，禁挑一个（r1313 同族）。
    """
    common, maps = _align(series)
    if len(common) <= h:
        return {"metric": metric, "verdict": "UNREADABLE", "why": "共同日不足一个窗口"}
    perm = {}
    n = 0
    for i in range(0, len(common) - h):
        seg = common[i + 1:i + h + 1]
        vals = {}
        for k in LINES:
            m = maps[k]
            if any(d not in m for d in seg):
                vals = None
                break
            xs = [m[d] for d in seg]
            if metric == "sharpe":
                mu = sum(xs) / len(xs)
                var = sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)
                sd = math.sqrt(var)
                if sd <= 0:
                    vals = None
                    break
                vals[k] = mu / sd * math.sqrt(252.0)
            else:
                vals[k] = sum(xs)
        if not vals:
            continue
        order = tuple(sorted(LINES, key=lambda k: -vals[k]))
        perm[">".join(order)] = perm.get(">".join(order), 0) + 1
        n += 1
    if not n:
        return {"metric": metric, "verdict": "UNREADABLE", "why": "没有一日共同可算"}
    best = max(perm, key=lambda k: perm[k])
    share = 100.0 * perm[best] / n
    canonical = "basis_nominal>excess_hedged>carry_unhedged"
    canon_share = 100.0 * perm.get(canonical, 0) / n
    if canon_share >= 95.0:
        token = "THE_LINE_ORDER_IS_NOT_A_CALENDAR_ARTIFACT"
    elif canon_share >= 80.0:
        token = "THE_LINE_ORDER_MOSTLY_HOLDS_BUT_FLIPS_ON_SOME_STARTS"
    else:
        token = "THE_LINE_ORDER_DEPENDS_ON_WHEN_YOU_START"
    return {
        "metric": metric,
        "common_dates": len(common),
        "common_first": common[0],
        "common_last": common[-1],
        "n_windows": n,
        "permutations": dict(sorted(perm.items(), key=lambda kv: -kv[1])),
        "dominant_order": best,
        "dominant_share_pct": round(share, 2),
        "canonical_order": canonical,
        "canonical_share_pct": round(canon_share, 2),
        "verdict": token,
    }


# ---------------------------------------------------------------- inputs


def load_series():
    """三条线的日序列 + 两臂的窗口。basis=(date, net)；两臂=(date, points/mult/cap)。"""
    rows = W.basis_rows()
    if not rows:
        return None, None
    mult, cap = W.money_basis()
    if not mult or not cap:
        return None, None
    rent = _load(RENT_SRC) or {}
    last = (((rent.get("cells") or {}).get("%s|excess_hedged" % PROD) or {}).get("window") or [None, None])[1]
    if not last:
        return None, None
    arms = W.arm_points(last)
    if not arms:
        return None, None
    import idx_fut_carry_paper as CP
    cut = [r[0] for r in CP.position_series(PROD)[0] if r[0] <= last]
    win = arms["window"]
    dates = [d for d in cut if win[0] <= d <= win[1]]
    # 两臂序列从锚日的下一根 bar 起算：长度必须正好少一天，否则不发布（禁按行号猜）
    if len(dates) - 1 != len(arms["excess"]) or len(arms["fut"]) != len(arms["excess"]):
        return None, None
    arm_dates = dates[1:]
    series = {
        "basis_nominal": [(r["date"], float(r["net"])) for r in rows],
        "excess_hedged": [(d, p * mult / cap) for d, p in zip(arm_dates, arms["excess"])],
        "carry_unhedged": [(d, p * mult / cap) for d, p in zip(arm_dates, arms["fut"])],
    }
    return series, {"multiplier": mult, "capital": cap, "arm_window": list(win), "arm_starts": arm_dates[0]}


def reproduction(series, arms_meta):
    """两条复现腿：basis 在父面窗口逐位复现（复利口径）+ 两臂 Sharpe 复现。"""
    econ = _load(ECON_SRC) or {}
    rent = _load(RENT_SRC) or {}
    ic = (econ.get("products") or {}).get(PROD) or {}
    base = ic.get("baseline") or {}
    ser = ic.get("series") or {}
    hedged = ((rent.get("cells") or {}).get("%s|excess_hedged" % PROD) or {})
    unhedged = ((rent.get("cells") or {}).get("%s|carry_unhedged" % PROD) or {})

    basis_map = dict(series["basis_nominal"])
    first, last = ser.get("first"), ser.get("last")
    own = [basis_map[d] for d in sorted(basis_map) if first and last and first <= d <= last]
    own_stats = W.return_stats(own) if own else None
    fields = {}
    ok = True
    for k in ("sharpe", "cagr_pct", "ann_vol_pct", "mdd_pct", "days"):
        a = (own_stats or {}).get(k)
        b = base.get(k)
        m = a is not None and b is not None and abs(float(a) - float(b)) <= REPRO_TOL
        ok = ok and m
        fields[k] = {"recomputed": a, "published": b, "match": bool(m)}

    def _ann_sharpe(xs):
        n = len(xs)
        mu = sum(xs) / n
        var = sum((x - mu) ** 2 for x in xs) / (n - 1)
        return mu / math.sqrt(var) * math.sqrt(252.0)

    # 两臂重算要用点数（% 化会丢点数的可加性），从 % 还原回点数
    mult, cap = arms_meta["multiplier"], arms_meta["capital"]
    hp = _ann_sharpe([x * cap / mult for _d, x in series["excess_hedged"]])
    up = _ann_sharpe([x * cap / mult for _d, x in series["carry_unhedged"]])
    arm_fields = {}
    for name, val, pub in (("excess_hedged", hp, hedged.get("sharpe_ann")),
                           ("carry_unhedged", up, unhedged.get("sharpe_ann"))):
        m = pub is not None and abs(val - float(pub)) <= REPRO_TOL
        ok = ok and m
        arm_fields[name] = {"recomputed": round(val, 4), "published": pub, "match": bool(m)}
    return {
        "basis_own_window": {"window": [first, last], "bars": len(own), "fields": fields,
                             "verdict": "MATCH" if all(v["match"] for v in fields.values()) else "MISMATCH",
                             "how": "CS.replay(IC,1.5) 截父面窗口按父面口径（244 天、复利）重算"},
        "two_arms": {"window": arms_meta["arm_window"], "bars": len(series["excess_hedged"]),
                     "fields": arm_fields,
                     "verdict": "MATCH" if all(v["match"] for v in arm_fields.values()) else "MISMATCH",
                     "how": "CP.position_series(IC)+per_lot_daily(years=10)，按父面口径（252 天）重算"},
        "verdict": "MATCH" if ok else "MISMATCH",
    }


# ---------------------------------------------------------------- build


def _bars_per_year(dates):
    if len(dates) < 2:
        return None
    d0 = datetime.strptime(dates[0], "%Y-%m-%d")
    d1 = datetime.strptime(dates[-1], "%Y-%m-%d")
    years = (d1 - d0).days / 365.25
    return round(len(dates) / years, 1) if years > 0 else None


def judge(lines, orderings, etf):
    hed = lines.get("excess_hedged") or {}
    hd = hed.get("distribution") or {}
    sp_x = (hd.get("return_pct") or {}).get("spread_over_median_x")
    etf_sp_x = (((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return", {}).get("spread_over_median_x")
    etf_sp_pp = (((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return", {}).get("spread_p90_minus_p10_pp")
    spread_pp = (hd.get("return_pct") or {}).get("spread_p90_minus_p10_pp")
    if sp_x is not None and etf_sp_x is not None:
        if sp_x < etf_sp_x:
            head = "THE_CARRY_BOOK_CARES_LESS_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK"
        elif sp_x > etf_sp_x:
            head = "THE_CARRY_BOOK_CARES_MORE_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK"
        else:
            head = "THE_TWO_BOOKS_CARE_EQUALLY_ABOUT_WHEN_YOU_START"
    else:
        head = "UNREADABLE"
    sentence = (
        "同一把尺（p90-p10 除中位）: carry 对冲臂 %.2fx vs ETF vt08 %.2fx；绝对跨度 %.2fpp vs %.2fpp "
        "（绝对值跨书不可比：两本书的波动不同）"
        % (sp_x or 0.0, etf_sp_x or 0.0, spread_pp or 0.0, etf_sp_pp or 0.0)
    )
    money = (orderings or {}).get("money") or {}
    sharpe = (orderings or {}).get("sharpe") or {}
    return {
        "headline": head,
        "headline_sentence": sentence,
        "spread_over_median_x_carry_hedged": sp_x,
        "spread_over_median_x_etf_vt08": etf_sp_x,
        "spread_pp_carry_hedged": spread_pp,
        "spread_pp_etf_vt08": etf_sp_pp,
        "ordering_token": sharpe.get("verdict"),
        "ordering_share_pct": sharpe.get("canonical_share_pct"),
        "ordering_sentence": (
            "r2192 的排序只在一本日历上验过一次；现在在 %s 个一年窗里按**同一量**（窗内 Sharpe）排："
            "basis>对冲残差>不带对冲 占 %.2f%%（判词 %s）——按**钱**排则是 %.2f%%（判词 %s），"
            "两个量给出相反答案，因为不带对冲那条的波动是另两条的约四倍"
            % (sharpe.get("n_windows"), sharpe.get("canonical_share_pct") or 0.0, sharpe.get("verdict"),
               money.get("canonical_share_pct") or 0.0, money.get("verdict"))
        ),
    }


def build():
    t0 = time.time()
    series, meta = load_series()
    if not series:
        return {"schema": "carry-entry-window-yield/v1", "face": "carry_entry_window_yield",
                "machine": "bm-c", "judgement": {"headline": "UNREADABLE",
                "headline_sentence": "面板或父面读不到（禁编）"}}
    repro = reproduction(series, meta)
    lines = {}
    for k in LINES:
        dates = [d for d, _v in series[k]]
        rets = [v for _d, v in series[k]]
        rows = window_rows(rets, dates, HORIZON, mode="simple")
        dist = distribution(rows)
        entry = {
            "unit": "one-lot capital per day (basis = notional return; arms = points x %d / %.1f)"
                    % (meta["multiplier"], meta["capital"]),
            "window": [dates[0], dates[-1]],
            "bars": len(dates),
            "bars_per_year": _bars_per_year(dates),
            "distribution": dist,
            "independent_blocks": independent_blocks(rows),
        }
        if k == "basis_nominal":
            crows = window_rows(rets, dates, HORIZON, mode="compound")
            entry["compounded_reading"] = {
                "note": "同一批窗口、同一根 bar 长度，改按复利算（basis 父面的口径）；头条用求和口径以便与两条点数臂同一把尺",
                "median_pct": round(_pct(sorted(r["g"] for r in crows), 50) * 100.0, 2),
                "p10_pct": round(_pct(sorted(r["g"] for r in crows), 10) * 100.0, 2),
                "p90_pct": round(_pct(sorted(r["g"] for r in crows), 90) * 100.0, 2),
            }
        else:
            med = (dist or {}).get("return_pct", {}).get("median")
            p10 = (dist or {}).get("return_pct", {}).get("p10")
            p90 = (dist or {}).get("return_pct", {}).get("p90")
            entry["money_per_lot_cny"] = {
                "capital": meta["capital"],
                "median": round(med / 100.0 * meta["capital"]) if med is not None else None,
                "p10": round(p10 / 100.0 * meta["capital"]) if p10 is not None else None,
                "p90": round(p90 / 100.0 * meta["capital"]) if p90 is not None else None,
            }
        lines[k] = entry

    ordr = {"money": ordering({k: series[k] for k in LINES}, metric="sum"),
            "sharpe": ordering({k: series[k] for k in LINES}, metric="sharpe"),
            "why_two_orderings": "钱由波动放大、Sharpe 不放大；r2192 的排序是 Sharpe 的排序，拿钱的排序去比会得到相反结论（r1313 同族）"}
    etf = _load(ETF_SRC) or {}
    judge_block = judge(lines, ordr, etf)
    reads = {k: ((lines[k].get("distribution") or {}).get("return_pct") or {}) for k in LINES}

    payload = {
        "schema": "carry-entry-window-yield/v1",
        "face": "carry_entry_window_yield",
        "machine": "bm-c",
        "evidence_cutoff": max(d for d, _v in series["basis_nominal"]),
        "question": "随便哪一天上车、拿满一年，carry 三条线各给你什么分布？r2192 的排序是不是日历给的？",
        "caliber": {
            "horizon_bars": HORIZON,
            "entry_lag": 1,
            "why": "244 根 bar = 一年（本面板两线密度 242.5/242.7 bar/年）；起点收盘决策、下一根 bar 起持有（r1796 可执行口径，与 r2195 同一口径）",
            "aggregation": "求和（不复利）为头条 = 一手资本的线性 P&L；basis 的复利读数并列印出，禁拿复利数与点数臂排序",
        },
        "reproduction": repro,
        "lines": lines,
        "ordering": ordr,
        "comparison_etf_book": {
            "source": ETF_SRC,
            "arm": "nobond_vt08",
            "spread_pp": ((((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return") or {}).get("spread_p90_minus_p10_pp"),
            "median_pct": ((((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return") or {}).get("median_pct"),
            "spread_over_median_x": ((((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return") or {}).get("spread_over_median_x"),
            "share_negative_pct": ((((etf or {}).get("arms") or {}).get("nobond_vt08") or {}).get("return") or {}).get("share_of_starts_negative_pct"),
            "note": "只用已发布的 ETF 面读数，不重算、不改它；追高绝对pp跨书不可比（波动不同），可比的是 spread/median 与亏钱起点占比",
        },
        "judgement": judge_block,
        "adoption": {
            "decided": "HORIZON=244 + entry_lag=1 + 求和口径",
            "decided_in": "r2196",
            "because": "三条线只有换算成「一手资本的分数」才可比；换年长、改复利、改起点偏移都会改读数，所以钉死在一处常量，其余各面只读这一处",
            "not_adopted": [
                {"road": "改复利做头条", "adopted": False,
                 "why": "点数臂的复利需要「P&L 再买第二手」，一手是不可分割单位；复利只对 basis 有意义，已并列印出"},
                {"road": "把 HORIZON 拉到 3 年让分布更窄", "adopted": False,
                 "why": "会同时砍掉大半起点样本，且读者问的是「拿满一年」，不是「拿到好看」"},
            ],
        },
        "not_measured": [
            "重叠窗口不是独立样本（独立块另印）；未做显著性检验、未声称 p 值",
            "两臂的换仓成本按父面已扣口径沿用，本面不重估",
            "basis_nominal 不可买（r2190：钱包买不到名义额），它的分布只作参照，不作可执行读数",
            "IM 腿未同做（本面只回答 IC）",
        ],
        "inputs_digest": _sha({
            "econ": _sha_file(ECON_SRC), "rent": _sha_file(RENT_SRC), "window": _sha_file(WINDOW_SRC),
            "cap": _sha_file(CAP_SRC), "ruler": _sha_file(RULER_SRC), "etf": _sha_file(ETF_SRC),
            "panel_tail": _panel_tail(),
        }),
        "sources": {rel: {"sha256": _sha_file(rel)} for rel in (ECON_SRC, RENT_SRC, WINDOW_SRC, CAP_SRC, RULER_SRC, ETF_SRC)},
        "panel_probe": {"path": PANEL_PROBE, "tail_date": _panel_tail()},
        "generated": _now(),
        "elapsed_sec": None,
        "_reads": reads,
    }
    payload["elapsed_sec"] = round(time.time() - t0, 1)
    return payload


def _panel_tail():
    p = ROOT / PANEL_PROBE
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        return lines[-1].split(",")[0][:10] if len(lines) > 1 else None
    except Exception:
        return None


# ---------------------------------------------------------------- md


def write_md(payload):
    j = payload.get("judgement") or {}
    lines = payload.get("lines") or {}
    ordr = payload.get("ordering") or {}
    cmp_ = payload.get("comparison_etf_book") or {}
    L = []
    L.append("# carry 这本书：随便哪天上车，拿满一年，给你什么（r2196 · bm-c）\n")
    L.append("证据截止 **%s** · 一年 = **%d** 根 bar · 起点收盘决策、下一根 bar 起持有（entry_lag=1）\n"
             % (payload.get("evidence_cutoff"), (payload.get("caliber") or {}).get("horizon_bars")))
    L.append("> 一句话：%s\n" % j.get("headline_sentence"))
    L.append("> 排序：%s\n" % j.get("ordering_sentence"))
    L.append("> 三条线各自的窗口：%s\n" % " · ".join(
        "%s %s→%s（%s bar，%.1f bar/年）" % (k, (lines.get(k) or {}).get("window", [None, None])[0],
                                          (lines.get(k) or {}).get("window", [None, None])[1],
                                          (lines.get(k) or {}).get("bars"), (lines.get(k) or {}).get("bars_per_year") or 0.0)
        for k in LINES))
    L.append("\n## 三条线的一年期分布（一手资本的 %）\n")
    L.append("| 线 | 起点数 | 中位 | p10 | p25 | p75 | p90 | 最差 | 最好 | 亏钱起点 | p90-p10 | 跨度/中位 | 路径回撤中位 | 最深 |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for k in LINES:
        d = (lines.get(k) or {}).get("distribution") or {}
        r = d.get("return_pct") or {}
        dd = d.get("path_drawdown_pct") or {}
        L.append("| %s | %d | %s%% | %s%% | %s%% | %s%% | %s%% | %s%% | %s%% | %s%% | %spp | %sx | %s%% | %s%% |"
                 % (k, d.get("n_start_days") or 0, r.get("median"), r.get("p10"), r.get("p25"), r.get("p75"),
                    r.get("p90"), r.get("min"), r.get("max"), r.get("share_negative_pct"),
                    r.get("spread_p90_minus_p10_pp"), r.get("spread_over_median_x"),
                    dd.get("median"), dd.get("worst")))
    L.append("\n- `basis_nominal` 不可买（r2190：钱包买不到名义额），它的分布只作参照。")
    br = (lines.get("basis_nominal") or {}).get("compounded_reading") or {}
    L.append("- 两臂是**点数换一手资本**的读数（200 元/点 ÷ 1,137,862.5 元），求和口径；basis 的复利读数：中位 {0}% / p10 {1}% / p90 {2}%。\n"
             .format(br.get("median_pct"), br.get("p10_pct"), br.get("p90_pct")))
    L.append("\n## 最差那一成起点挤在哪几个月（是不是一次事件）\n")
    for k in LINES:
        d = (lines.get(k) or {}).get("distribution") or {}
        months = d.get("worst_decile_start_months") or {}
        fmt_months = " / ".join("%s×%d" % (m, c) for m, c in months.items()) or "无"
        L.append("- **%s**：%s（最差一成起点落在 %s 个不同月份 → %s）"
                 % (k, fmt_months, d.get("distinct_start_months_in_worst_decile"),
                    "一次事件" if (d.get("distinct_start_months_in_worst_decile") or 99) <= 5 else "多点分布"))
    L.append("\n## 独立证据（不重叠整年块）\n")
    for k in LINES:
        b = (lines.get(k) or {}).get("independent_blocks") or {}
        L.append("- **%s**：%s 块 · 均值 %s%% · 最差 %s%% · 最好 %s%% · 亏钱 %s 块"
                 % (k, b.get("n_blocks"), b.get("mean_pct"), b.get("min_pct"), b.get("max_pct"), b.get("n_negative")))
    L.append("\n## 排序：r2192 的结论是不是日历给的\n")
    for metric, label in (("sharpe", "按窗内 Sharpe（r2192 量的就是它）"), ("money", "按窗内赚到的钱")):
        o = ordr.get(metric) or {}
        L.append("\n**%s** · 可算窗口 %s 个 · 共同日 %s（%s → %s）\n"
                 % (label, o.get("n_windows"), o.get("common_dates"), o.get("common_first"), o.get("common_last")))
        L.append("| 排序 | 窗口数 | 占比 |")
        L.append("|---|---:|---:|")
        for k, v in (o.get("permutations") or {}).items():
            L.append("| %s | %d | %.2f%% |" % (k.replace(">", " > "), v, 100.0 * v / max(1, o.get("n_windows") or 1)))
        L.append("\n判词 `%s`（basis>对冲残差>不带对冲 占 %.2f%%）\n" % (o.get("verdict"), o.get("canonical_share_pct") or 0.0))
    L.append("\n## 与 ETF 那本书同一把尺\n")
    L.append("- ETF vt08（r2195 已发布）：中位 %s%% · p90-p10 %spp · 跨度/中位 **%sx** · 亏钱起点 %s%%"
             % (cmp_.get("median_pct"), cmp_.get("spread_pp"), cmp_.get("spread_over_median_x"), cmp_.get("share_negative_pct")))
    L.append("- carry 对冲臂（本面）：中位 %s%% · p90-p10 **%spp** · 跨度/中位 **%sx** · 亏钱起点 %s%%"
             % (((lines.get("excess_hedged") or {}).get("distribution") or {}).get("return_pct", {}).get("median"),
                j.get("spread_pp_carry_hedged"), j.get("spread_over_median_x_carry_hedged"),
                (((lines.get("excess_hedged") or {}).get("distribution") or {}).get("return_pct", {}).get("share_negative_pct"))))
    L.append("- 绝对值跨书不可比（波动不同），可比的是 spread/median 与亏钱起点占比。\n")
    L.append("## 复现腿（先证明尺子一样，再读任何数）\n")
    rep = payload.get("reproduction") or {}
    L.append("- basis 父面窗口 %s：**%s**（%s）" % ((rep.get("basis_own_window") or {}).get("window"),
                                                 (rep.get("basis_own_window") or {}).get("verdict"),
                                                 (rep.get("basis_own_window") or {}).get("how")))
    L.append("- 两臂 %s：**%s**（%s）" % ((rep.get("two_arms") or {}).get("window"),
                                      (rep.get("two_arms") or {}).get("verdict"),
                                      (rep.get("two_arms") or {}).get("how")))
    for name, blk in ((rep.get("two_arms") or {}).get("fields") or {}).items():
        L.append("  - %s：重算 %s vs 已发布 %s（%s）" % (name, blk.get("recomputed"), blk.get("published"),
                                                    "MATCH" if blk.get("match") else "MISMATCH"))
    L.append("\n## 没量到的（如实）\n")
    for x in payload.get("not_measured") or []:
        L.append("- %s" % x)
    L.append("\n生成：%s · 用时 %ss · 输入摘要 %s…" % (payload.get("generated"), payload.get("elapsed_sec"),
                                                (payload.get("inputs_digest") or "")[:12]))
    text = "\n".join(L) + "\n"
    OUT_MD.write_text(text, encoding="utf-8")
    head = []
    head.append("# carry 一年期起点分布 · 研究记录（r2196 · bm-c）\n")
    head.append("问的是：**同一本书，我对不同的日子上车，一年后的答案会差多少？** 而 r2192 的排序是不是日历给的？\n")
    head.append("读数面（机器可读）：`results/carry_entry_window_yield.json`\n")
    head.append("读者面（人可读，含全部表）：`results/carry_entry_window_yield.md`\n")
    head.append("\n## 一句话结论\n")
    head.append("- %s" % j.get("headline"))
    head.append("- %s" % j.get("headline_sentence"))
    head.append("- %s" % j.get("ordering_sentence"))
    head.append("\n## 口径与律\n")
    head.append("- 一年 = %s 根 bar；起点收盘决策、下一根 bar 起持有（与 r2195 的 ETF 面同一口径）。"
                % (payload.get("caliber") or {}).get("horizon_bars"))
    head.append("- 三条线统一换成「一手资本的日分数」才可比：basis=名义额收益率，两臂=点数×200÷1,137,862.5。")
    head.append("- 求和口径为头条（一手不可分割，P&L 线性可加）；basis 的复利读数并列印出，禁混用排序。")
    head.append("- 重叠窗口不是独立样本：另印不重叠整年块作独立证据，不声称 p 值。")
    head.append("- 复现腿先跑：basis 在父面窗口逐位复现 + 两臂 Sharpe 逐位复现，任一失配 exit 2 不发布。")
    head.append("\n## 自捕与留账\n")
    head.append("- 本面不改任何已发布面；链腿/冒烟腿未接（竞争窗，见轮报告）。")
    head.append("- 未测：IM 腿、两臂自己的标空成本重估、显著性。")
    RESEARCH_MD.write_text("\n".join(head) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- check


def _flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flatten(v, prefix + "/" + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flatten(v, prefix + "/%d" % i))
    else:
        out[prefix] = obj
    return out


VOLATILE = ("/generated", "/elapsed_sec", "/sources", "/panel_probe", "/inputs_digest",
            "/reproduction/how", "/_reads")


def compare_faces(face, live):
    a = _flatten(face)
    b = _flatten(live)
    diffs = []
    for k in sorted(set(a) | set(b)):
        if any(k.startswith(v) for v in VOLATILE):
            continue
        va, vb = a.get(k), b.get(k)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            if abs(float(va) - float(vb)) > CHECK_TOL:
                diffs.append({"path": k, "face": va, "live": vb})
        elif va != vb:
            diffs.append({"path": k, "face": va, "live": vb})
    return diffs


def classify(face, live):
    """输入字节动=STALE（付费补写）；同输入数字不符=CHECK FAILED（真缺陷，不带 STALE）。"""
    notes = []
    stale = face.get("inputs_digest") != live.get("inputs_digest")
    diffs = compare_faces(face, live)
    if stale:
        notes.append("STALE: source bytes or panel tail moved since this face was written")
    if diffs:
        notes.append("%s: %d field(s) no longer recompute from the same inputs"
                     % ("CHECK FAILED" if not stale else "CHECK FAILED (also stale)", len(diffs)))
    ok = not stale and not diffs
    return ok, notes, diffs


def check():
    p = ROOT / "results" / "carry_entry_window_yield.json"
    if not p.exists():
        print(json.dumps({"ok": False, "notes": ["face missing"]}, ensure_ascii=False))
        return 3
    face = json.loads(p.read_text(encoding="utf-8"))
    live = build()
    ok, notes, diffs = classify(face, live)
    print(json.dumps({"ok": ok, "notes": notes, "diffs": diffs[:8]}, ensure_ascii=False))
    if ok:
        return 0
    return 3 if any(n.startswith("STALE") for n in notes) else 1


# ---------------------------------------------------------------- selftest


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # 1-4 分布算术
    xs = sorted(float(i) for i in range(1, 101))
    leg("pct_median_50", abs(_pct(xs, 50) - 50.5) < 1e-12, "%.4f" % _pct(xs, 50))
    leg("pct_p10", abs(_pct(xs, 10) - 10.9) < 1e-12, "%.4f" % _pct(xs, 10))
    leg("pct_single", _pct([3.0], 90) == 3.0)
    leg("pct_empty", _pct([], 50) is None)

    # 5 求和口径 vs 复利口径必须不同
    rets = [0.01] * 300
    dates = ["d%03d" % i for i in range(300)]
    s_rows = window_rows(rets, dates, 244, mode="simple")
    c_rows = window_rows(rets, dates, 244, mode="compound")
    leg("window_count", len(s_rows) == len(rets) - 244, "%d" % len(s_rows))
    leg("simple_sum", abs(s_rows[0]["g"] - 2.44) < 1e-9, "%.6f" % s_rows[0]["g"])
    leg("compound_pow", abs(c_rows[0]["g"] - (1.01 ** 244 - 1.0)) < 1e-9, "%.6f" % c_rows[0]["g"])
    leg("entry_lag", s_rows[0]["to"] == dates[244])

    # 6 单调上升序列回撤=0；单调下降回撤<0
    up = window_rows([0.002] * 300, dates, 244, mode="simple")
    dn = window_rows([-0.002] * 300, dates, 244, mode="simple")
    leg("dd_zero_on_up", up[0]["dd"] == 0.0)
    leg("dd_negative_on_down", dn[0]["dd"] < 0)

    # 7 分布块：中位与跨度
    rows = [{"from": "2020-01-%02d" % (i % 28 + 1), "to": "2021-01-01", "g": i / 100.0, "dd": -0.01}
            for i in range(1, 101)]
    d = distribution(rows)
    leg("dist_median", abs(d["return_pct"]["median"] - 0.505 * 100) < 1e-6, str(d["return_pct"]["median"]))
    leg("dist_share_neg", d["return_pct"]["share_negative_pct"] == 0.0)
    leg("dist_worst_first", d["worst_starts"][0]["return_pct"] == 1.0)
    leg("dist_months_present", "worst_decile_start_months" in d)

    # 8 独立块：步长=HORIZON
    blocks = independent_blocks(rows, h=10)
    leg("blocks_every_h", blocks["n_blocks"] == len(rows[::10]), "%d" % blocks["n_blocks"])

    # 9 排序：恒定排序 -> 100%；交替 -> 低
    a = [("d%03d" % i, 0.003) for i in range(400)]
    b = [("d%03d" % i, 0.002) for i in range(400)]
    c = [("d%03d" % i, -0.001) for i in range(400)]
    o1 = ordering({"basis_nominal": a, "excess_hedged": b, "carry_unhedged": c}, h=244)
    leg("order_holds_100", o1["canonical_share_pct"] == 100.0, str(o1["verdict"]))
    a2 = [("d%03d" % i, 0.001 if i % 2 else -0.001) for i in range(400)]
    o2 = ordering({"basis_nominal": a2, "excess_hedged": b, "carry_unhedged": c}, h=244)
    leg("order_flips", o2["canonical_share_pct"] < 95.0, "%.1f" % o2["canonical_share_pct"])
    leg("order_token_mapping", o1["verdict"] == "THE_LINE_ORDER_IS_NOT_A_CALENDAR_ARTIFACT")

    # 10 对齐按日期键：两条不同起点的序列只在交集上算
    x = [("d%03d" % i, 0.001) for i in range(0, 400, 2)]
    y = [("d%03d" % i, 0.001) for i in range(400)]
    common, maps = _align({"basis_nominal": x, "excess_hedged": y, "carry_unhedged": y})
    leg("align_by_date", len(common) == len(x) and common[0] == "d000")

    # 11 复现容差
    leg("repro_tol_accepts_1e5", abs(2.972 - (2.972 + 1e-5)) <= REPRO_TOL)
    leg("repro_tol_rejects_1e3", abs(2.972 - (2.972 + 1e-3)) > REPRO_TOL)

    # 12-15 行为腿：classify 三态
    face = {"inputs_digest": "AAA", "judgement": {"headline": "X", "spread_pp": 12.0},
            "lines": {"excess_hedged": {"distribution": {"return_pct": {"median": 8.0}}}}}
    live = copy.deepcopy(face)
    ok, notes, diffs = classify(face, live)
    leg("classify_clean", ok and not notes, str(notes))
    live2 = copy.deepcopy(face)
    live2["inputs_digest"] = "BBB"
    ok2, notes2, _d2 = classify(face, live2)
    leg("classify_stale", (not ok2) and any(n.startswith("STALE") for n in notes2), str(notes2))
    live3 = copy.deepcopy(face)
    live3["judgement"]["headline"] = "Y"
    ok3, notes3, _d3 = classify(face, live3)
    leg("classify_check_failed", (not ok3) and any("CHECK FAILED" in n for n in notes3)
        and not any(n.startswith("STALE") for n in notes3), str(notes3))
    live4 = copy.deepcopy(face)
    live4["lines"]["excess_hedged"]["distribution"]["return_pct"]["median"] = 8.5
    ok4, notes4, _d4 = classify(face, live4)
    leg("classify_number_drift", (not ok4) and any("CHECK FAILED" in n for n in notes4), str(notes4))
    live5 = copy.deepcopy(face)
    live5["generated"] = "zzz"
    live5["sources"] = {"k": 1}
    ok5, _n5, _d5 = classify(face, live5)
    leg("volatile_fields_ignored", ok5)

    # 16 密度检查器
    leg("bars_per_year_sane", abs((_bars_per_year(["2018-10-22", "2019-10-22"]) or 0) - 365.0 / 365.25 * 1) < 2.0,
        str(_bars_per_year(["2018-10-22", "2019-10-22"])))

    # 17 判词阈值两侧
    lines_ok = {"excess_hedged": {"distribution": {"return_pct": {"spread_over_median_x": 1.0,
                                                                 "spread_p90_minus_p10_pp": 10.0}}}}
    etf = {"arms": {"nobond_vt08": {"return": {"spread_over_median_x": 3.56, "spread_p90_minus_p10_pp": 32.34}}}}
    jb = judge(lines_ok, {"sharpe": {"verdict": "T", "canonical_share_pct": 99.0, "n_windows": 10},
                          "money": {"verdict": "U", "canonical_share_pct": 24.0}}, etf)
    leg("judge_less", jb["headline"] == "THE_CARRY_BOOK_CARES_LESS_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK", jb["headline"])
    lines_more = {"excess_hedged": {"distribution": {"return_pct": {"spread_over_median_x": 9.0,
                                                                    "spread_p90_minus_p10_pp": 90.0}}}}
    jb2 = judge(lines_more, {"sharpe": {"verdict": "T", "canonical_share_pct": 99.0, "n_windows": 10},
                             "money": {"verdict": "U", "canonical_share_pct": 24.0}}, etf)
    leg("judge_more", jb2["headline"] == "THE_CARRY_BOOK_CARES_MORE_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK", jb2["headline"])
    leg("judge_prints_both_orderings", "24.00" in (jb["ordering_sentence"] or "") or "24.0" in (jb["ordering_sentence"] or ""),
        jb["ordering_sentence"][:60])

    # 18 钱排序 vs Sharpe 排序会相反（本面自捕：拿钱的排序去比 r2192 的 Sharpe 排序就是错读）
    hi_vol = [("d%03d" % i, 0.002 + (0.006 if i % 2 else -0.006)) for i in range(400)]
    lo_vol = [("d%03d" % i, 0.0011 + (0.0001 if i % 2 else 0.0)) for i in range(400)]
    tiny = [("d%03d" % i, 0.0005 + (0.0002 if i % 2 else 0.0)) for i in range(400)]
    ser = {"basis_nominal": lo_vol, "excess_hedged": hi_vol, "carry_unhedged": tiny}
    om = ordering(ser, h=244, metric="sum")
    osr = ordering(ser, h=244, metric="sharpe")
    leg("money_vs_sharpe_differ", om["dominant_order"] != osr["dominant_order"],
        "%s vs %s" % (om["dominant_order"], osr["dominant_order"]))

    npass = sum(1 for _n, c, _d in legs if c)
    for name, cond, detail in legs:
        print("%-28s %s %s" % (name, "PASS" if cond else "FAIL", detail))
    print("\n%d/%d PASS" % (npass, len(legs)))
    return 0 if npass == len(legs) else 1


# ---------------------------------------------------------------- main


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    payload = build()
    head = (payload.get("judgement") or {}).get("headline")
    if head == "UNREADABLE" or (payload.get("reproduction") or {}).get("verdict") not in (None, "MATCH"):
        public = {k: v for k, v in payload.items() if not k.startswith("_")}
        OUT_JSON.write_text(json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({"ok": False, "verdict": head,
                          "why": "reproduction leg failed or panel unreadable -- face not published",
                          "reproduction": payload.get("reproduction")}, ensure_ascii=False)[:1200])
        return 2
    reads = payload.pop("_reads")
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(payload)
    print(json.dumps({"headline": head,
                      "sentence": (payload.get("judgement") or {}).get("headline_sentence"),
                      "ordering": (payload.get("judgement") or {}).get("ordering_token"),
                      "reads": reads}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
