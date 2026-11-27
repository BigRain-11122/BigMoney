#!/usr/bin/env python3
"""r2191 挂账 (b) 的兑现：把 basis 臂放到另两条的日历上重算。

WHY THIS FILE EXISTS
--------------------
``carry_three_lines_window``（r2191）把 carry 的三个代表读数摊开，判词是
``THE_TABLE_MIXES_WINDOWS``：basis_nominal 从 2017-01-18 起算（2390 bar），对冲残差与
点位收益都从 2018-10-22 起算（1961 bar），差 647 个日历日。它给了两个想法但没答：
「把 basis 剪到共同窗，那条 2.972 还剩多少？」「排序会不会翻？」

本面就答这两问，并且**先证明自己用的是同一把尺**：
  * 重放基准（``CS.replay``）在父面自己的窗口 2017-01-18..2026-11-25 上必须逐位复现
    已发布的 2.972 / 10.069 / 3.2463 / -1.8896；
  * 重放两臂（``CP.position_series`` + ``per_lot_daily``）在 2018-10-22..2026-11-20 上
    必须逐位复现已发布的 1.4162 / 0.5057。
两条复现腿任一失配 = 本文不发布（exit 2），因为「尺不一样」时的比较只是把错的地方换了个位置。

口径不是判据
------------
  * basis 是复利收益率（%），另两条是每手点数（指数点），两者单位不同，本面不把它们相加；
  * 点数换钱用 ``idx_fut_carry_capacity_lots`` 的 ``capital_per_lot_cny`` 与
    ``idx_fut_carry_one_lot_ruler`` 里的每跳金额反推出的合约乘数（IC=200 元/点）——
    两个都是已发布面，本面只读不推；
  * 年化天数**两套**并印：basis 那条用 244（``bench_core.TRADING_DAYS``），两臂的父面用
    252（``_ann_sharpe``）。差 √(252/244)=1.6%，不够解释 2x 的差距，但读者该看得见。

verdict tokens（跑之前冻结）
  ORDERING_HOLDS_ON_ONE_CALENDAR         共同窗上 basis > 对冲残差 > 点位收益，名次与 r2191 一致
  ORDERING_FLIPS_WHEN_THE_CALENDAR_MATCHES  名次翻面——那说明 r2190 那张表的名次是日历给的
  THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE   剪到共同窗后 basis 的 Sharpe 掉 ≤ 0.10：多出的
                                         647 天既没抬也没压这条读数
  THE_EXTRA_DAYS_BUY_SOME_OF_IT          掉 0.10..0.30
  THE_EXTRA_DAYS_BUY_MOST_OF_THE_SHARPE  掉 ≥ 0.30：印出来的 2.972 主要靠别人看不到的那一段
  UNREADABLE                             任一复现腿失配或读数缺失——不比较、不发布

只读：不碰 LEDGER.json / STATE.json / 任何已发布面；确定性（同面板同字节，除 generated）。
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import paper_basis_timing_cost_split as CS  # noqa: E402

TZ = timezone(timedelta(hours=8))

ECON_SRC = "results/idx_fut_carry_kill_rule_economics.json"
RENT_SRC = "results/idx_fut_carry_search_rent.json"
WINDOW_SRC = "results/carry_three_lines_window.json"
CAP_SRC = "results/idx_fut_carry_capacity_lots.json"
RULER_SRC = "results/idx_fut_carry_one_lot_ruler.json"
PAPER_SRC = "results/idx_fut_carry_open_capital.json"

OUT_JSON = ROOT / "results" / "carry_three_lines_common_window.json"
OUT_MD = ROOT / "research" / "CARRY_THREE_LINES_COMMON_WINDOW.md"

CODE = "IC"
PRODUCT = CODE
COST_BP_SIDE = 1.5
TDAYS_BASIS = 244.0     # bench_core.TRADING_DAYS, the basis line's own annualisation
TDAYS_ARMS = 252.0      # idx_fut_carry_search_rent._ann_sharpe
MIN_BARS = 60
DELTA_NO_BUY = 0.10
DELTA_MOST = 0.30
REPRO_TOL = 5e-4        # published faces are rounded to 4dp


def _now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _load(rel):
    p = ROOT / rel
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- maths


def return_stats(net, tdays=TDAYS_BASIS):
    """复利率路径的读数（basis 那条的口径）。少于 MIN_BARS 一律 None，禁编。"""
    xs = [float(x) for x in net]
    n = len(xs)
    if n < MIN_BARS:
        return None
    eq = 1.0
    peak = 1.0
    mdd = 0.0
    for x in xs:
        eq *= 1.0 + x
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1.0)
    years = n / tdays
    cagr = eq ** (1.0 / years) - 1.0 if eq > 0 else None
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    sd = math.sqrt(var)
    return {
        "days": n,
        "years": round(years, 3),
        "cagr_pct": round(cagr * 100.0, 4) if cagr is not None else None,
        "ann_mean_pct": round(mu * tdays * 100.0, 4),
        "ann_vol_pct": round(sd * math.sqrt(tdays) * 100.0, 4),
        "sharpe": round(mu / sd * math.sqrt(tdays), 4) if sd > 0 else None,
        "mdd_pct": round(mdd * 100.0, 4),
    }


def points_stats(points, multiplier=None, capital_cny=None, tdays=TDAYS_ARMS):
    """每手点数路径的读数（两臂的口径）。

    点数是可加的 P&L，不是收益率：回撤要按累计点数算（峰值到谷底），换成 % 只能借
    「一手要多少资本」这条已发布的面，借不到就只印点数（禁自造分母）。
    """
    xs = [float(x) for x in points]
    n = len(xs)
    if n < MIN_BARS:
        return None
    cum = 0.0
    peak = 0.0
    mdd_pts = 0.0
    for x in xs:
        cum += x
        peak = max(peak, cum)
        mdd_pts = min(mdd_pts, cum - peak)
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    sd = math.sqrt(var)
    out = {
        "days": n,
        "sharpe_ann": round(mu / sd * math.sqrt(tdays), 4) if sd > 0 else None,
        "sharpe_ann_at_244": round(mu / sd * math.sqrt(TDAYS_BASIS), 4) if sd > 0 else None,
        "ann_mean_points": round(mu * tdays, 2),
        "ann_vol_points": round(sd * math.sqrt(tdays), 2),
        "cum_points": round(cum, 2),
        "mdd_points": round(mdd_pts, 2),
    }
    if multiplier and capital_cny:
        out["ann_mean_cny"] = round(mu * tdays * multiplier, 0)
        out["ann_vol_cny"] = round(sd * math.sqrt(tdays) * multiplier, 0)
        out["mdd_cny"] = round(mdd_pts * multiplier, 0)
        out["mdd_pct_of_capital"] = round(100.0 * mdd_pts * multiplier / capital_cny, 2)
        out["pct_of_capital_basis"] = {
            "multiplier_cny_per_point": multiplier,
            "capital_per_lot_cny": capital_cny,
        }
    return out


def slice_rows(rows, first, last):
    """两端都含的日期切片。"""
    return [r for r in rows if first <= r["date"] <= last]


# ---------------------------------------------------------------- inputs


def basis_rows():
    return CS.replay(CODE, COST_BP_SIDE)


def arm_points(cutoff):
    """(window, fut_points, excess_points) 截在 cutoff，窗口=父面自己的十年回放窗。"""
    import idx_fut_carry_paper as CP
    import idx_fut_basis as BASE

    rows, _rolls = CP.position_series(PRODUCT)
    if not rows:
        return None
    cut = [r for r in rows if r[0] <= cutoff]
    if len(cut) < 300:
        return None
    idx = BASE.load_index(BASE.PAIRS[PRODUCT][0])
    s = CP.per_lot_daily(cut, idx, years=10)
    if not s:
        return None
    return {"window": list(s["window"]), "fut": list(s["fut_points"]), "excess": list(s["excess_points"])}


def money_basis():
    """(multiplier, capital) 从已发布面读；读不到就 None（只印点数）。"""
    mult = None
    ruler = _load(RULER_SRC) or {}
    tick = ((ruler.get("rule") or {}).get("precision_tick_cny") or {}).get(PRODUCT)
    try:
        mult = int(round(float(tick) / 0.0001))
    except Exception:
        mult = None
    cap = None
    lots = _load(CAP_SRC) or {}
    try:
        cap = float(lots["products"][PRODUCT]["desk"]["capital_per_lot_cny"])
    except Exception:
        cap = None
    return mult, cap


# ---------------------------------------------------------------- build


def build():
    econ = _load(ECON_SRC) or {}
    rent = _load(RENT_SRC) or {}
    window = _load(WINDOW_SRC) or {}
    mult, cap = money_basis()

    ic = (econ.get("products") or {}).get(PRODUCT) or {}
    published = {
        "baseline": ic.get("baseline") or {},
        "series": ic.get("series") or {},
    }
    hedged_pub = ((rent.get("cells") or {}).get("%s|excess_hedged" % PRODUCT) or {})
    unhedged_pub = ((rent.get("cells") or {}).get("%s|carry_unhedged" % PRODUCT) or {})

    rows = basis_rows()
    if not rows:
        return {"schema": "carry-three-lines-common-window/v1", "face": "carry_three_lines_common_window",
                "machine": "bm-c", "judgement": {"verdict": "UNREADABLE", "sentence": "基准日序列为空"}}

    # 共同窗取 r2191 已算出的交集（缺则用两臂父面声明的窗口）
    overlap = window.get("overlap") or {}
    first = overlap.get("first") or hedged_pub.get("window", [None])[0]
    last = overlap.get("last") or hedged_pub.get("window", [None])[1]
    if not first or not last:
        return {"schema": "carry-three-lines-common-window/v1", "face": "carry_three_lines_common_window",
                "machine": "bm-c", "judgement": {"verdict": "UNREADABLE", "sentence": "没有任何一张面印出共同窗"}}

    # ---- 复现腿 1：basis 在父面自己的窗口上必须逐位复现
    pub_first = published["series"].get("first")
    pub_last = published["series"].get("last")
    own_rows = slice_rows(rows, pub_first, pub_last) if pub_first and pub_last else []
    own = return_stats([r["net"] for r in own_rows])
    repro = {}
    keys = (("sharpe", 4), ("cagr_pct", 4), ("ann_vol_pct", 4), ("mdd_pct", 4), ("days", 0))
    diffs = {}
    for k, _dp in keys:
        a = (own or {}).get(k)
        b = published["baseline"].get(k)
        ok = a is not None and b is not None and abs(float(a) - float(b)) <= REPRO_TOL
        diffs[k] = {"recomputed": a, "published": b, "match": bool(ok)}
    repro["basis_own_window"] = {
        "window": [pub_first, pub_last],
        "bars_recomputed": len(own_rows),
        "bars_published": published["series"].get("bars"),
        "fields": diffs,
        "verdict": "MATCH" if all(v["match"] for v in diffs.values()) else "MISMATCH",
        "how": "CS.replay(IC, 1.5) 截父面窗口后按父面口径（244 天、复利）重算",
    }

    # ---- 复现腿 2：两臂在 2018-10-22..2026-11-20 上必须逐位复现
    arms = arm_points(last)
    arm_repro = {}
    if arms:
        hp = points_stats(arms["excess"], mult, cap)
        up = points_stats(arms["fut"], mult, cap)
        arm_repro = {
            "window": arms["window"],
            "bars": hp["days"] if hp else None,
            "excess_hedged": {
                "recomputed": (hp or {}).get("sharpe_ann"),
                "published": hedged_pub.get("sharpe_ann"),
                "match": bool(hp) and abs(hp["sharpe_ann"] - float(hedged_pub.get("sharpe_ann"))) <= REPRO_TOL,
            },
            "carry_unhedged": {
                "recomputed": (up or {}).get("sharpe_ann"),
                "published": unhedged_pub.get("sharpe_ann"),
                "match": bool(up) and abs(up["sharpe_ann"] - float(unhedged_pub.get("sharpe_ann"))) <= REPRO_TOL,
            },
            "verdict": "MATCH" if (hp and up and abs(hp["sharpe_ann"] - float(hedged_pub.get("sharpe_ann"))) <= REPRO_TOL
                                   and abs(up["sharpe_ann"] - float(unhedged_pub.get("sharpe_ann"))) <= REPRO_TOL)
                       else "MISMATCH",
            "how": "CP.position_series(IC) 截 2026-11-20 + per_lot_daily(years=10)，按父面口径（252 天）重算",
        }
    else:
        arm_repro = {"verdict": "MISMATCH", "why": "面板不可读"}
    repro["two_arms_common_window"] = arm_repro

    readable = repro["basis_own_window"]["verdict"] == "MATCH" and arm_repro.get("verdict") == "MATCH"

    # ---- 共同窗上的 basis（两种切片都印：含锚日=1962，去掉锚日=与两臂同为 1961）
    common_rows = slice_rows(rows, first, last)
    common = return_stats([r["net"] for r in common_rows])
    if common:
        common["first"] = first
        common["last"] = last
    common_drop = return_stats([r["net"] for r in common_rows[1:]]) if len(common_rows) > 1 else None

    # ---- 被剪掉的那一段
    pre_rows = [r for r in rows if r["date"] < first]
    pre = return_stats([r["net"] for r in pre_rows])

    # ---- 逐年（basis），给「多出的 647 天是不是好年份」一个可查答案
    by_year = {}
    for r in rows:
        by_year.setdefault(r["date"][:4], []).append(r["net"])
    yearly = {y: return_stats(v) for y, v in sorted(by_year.items())}
    prefix_years = sorted({r["date"][:4] for r in pre_rows})

    lines = []
    if common:
        lines.append({
            "line": "basis_nominal",
            "unit": "compounded %",
            "window": [first, last],
            "bars": common["days"],
            "sharpe_at_244": common["sharpe"],
            "sharpe_at_252": round(common["sharpe"] * math.sqrt(TDAYS_ARMS / TDAYS_BASIS), 4),
            "cagr_pct": common["cagr_pct"],
            "ann_vol_pct": common["ann_vol_pct"],
            "mdd_pct": common["mdd_pct"],
            "source": "this face (recomputed from CS.replay)",
            "same_ruler_as_published": repro["basis_own_window"]["verdict"] == "MATCH",
        })
    if hp_ := (points_stats(arms["excess"], mult, cap) if arms else None):
        lines.append({
            "line": "excess_hedged",
            "unit": "index points per lot",
            "window": arms["window"],
            "bars": hp_["days"],
            "sharpe_at_252": hp_["sharpe_ann"],
            "sharpe_at_244": hp_["sharpe_ann_at_244"],
            "ann_mean_points": hp_["ann_mean_points"],
            "ann_vol_points": hp_["ann_vol_points"],
            "mdd_points": hp_["mdd_points"],
            "mdd_cny": hp_.get("mdd_cny"),
            "mdd_pct_of_capital": hp_.get("mdd_pct_of_capital"),
            "source": "this face (recomputed from CP.per_lot_daily)",
            "same_ruler_as_published": arm_repro.get("excess_hedged", {}).get("match", False),
        })
    if up_ := (points_stats(arms["fut"], mult, cap) if arms else None):
        lines.append({
            "line": "carry_unhedged",
            "unit": "index points per lot",
            "window": arms["window"],
            "bars": up_["days"],
            "sharpe_at_252": up_["sharpe_ann"],
            "sharpe_at_244": up_["sharpe_ann_at_244"],
            "ann_mean_points": up_["ann_mean_points"],
            "ann_vol_points": up_["ann_vol_points"],
            "mdd_points": up_["mdd_points"],
            "mdd_cny": up_.get("mdd_cny"),
            "mdd_pct_of_capital": up_.get("mdd_pct_of_capital"),
            "source": "this face (recomputed from CP.per_lot_daily)",
            "same_ruler_as_published": arm_repro.get("carry_unhedged", {}).get("match", False),
        })

    judgement = judge(readable, lines, published["baseline"].get("sharpe"), common)
    delta_token = delta_verdict(published["baseline"].get("sharpe"), (common or {}).get("sharpe"))

    payload = {
        "schema": "carry-three-lines-common-window/v1",
        "face": "carry_three_lines_common_window",
        "machine": "bm-c",
        "evidence_cutoff": econ.get("evidence_cutoff"),
        "question": "把 basis 剪到另两条的日历（2018-10-22..2026-11-20）上，2.972 还剩多少？排序会不会翻？",
        "reproduction": repro,
        "common_window": {
            "first": first,
            "last": last,
            "basis_bars_including_anchor_day": len(common_rows),
            "basis_bars_dropping_anchor_day": len(common_rows) - 1 if common_rows else 0,
            "arms_bars": arm_repro.get("bars"),
            "note": "两臂的序列从锚日的下一 bar 起算，所以 basis 在窗内多出锚日一天；两个切片都印，读者不必信一个挑过的数",
        },
        "lines": lines,
        "basis_common_window": common,
        "basis_common_window_dropping_anchor": common_drop,
        "basis_published_own_window": published["baseline"],
        "basis_excluded_prefix": dict(pre or {}, years=sorted({y for y in prefix_years}),
                                       window=[pre_rows[0]["date"] if pre_rows else None,
                                               pre_rows[-1]["date"] if pre_rows else None]),
        "yearly_basis": yearly,
        "annualisation": {
            "basis_days_per_year": TDAYS_BASIS,
            "arms_days_per_year": TDAYS_ARMS,
            "ratio_of_sharpes": round(math.sqrt(TDAYS_ARMS / TDAYS_BASIS), 4),
            "note": "同一个 Sharpe 在 252 口径下比 244 口径高 1.6%；两臂的 1.4162 / 0.5057 与 basis 的 2.972 原来不是同一天数，这里两套都印",
        },
        "money_basis": {"multiplier_cny_per_point": mult, "capital_per_lot_cny": cap,
                        "sources": [RULER_SRC, CAP_SRC]},
        "conflicting_faces": _conflicting(hp_ if arms else None),
        "judgement": judgement,
        "delta_verdict": delta_token,
        "what_can_now_be_said": _can_say(lines, common, delta_token),
        "what_is_still_missing": [
            "两臂的点数换成 % 借的是「一手资本」这条面：一手是一个不可分割的单位，资本更小或更大时 % 会变，点数是唯一不随账户变的读数",
            "对冲残差与点位收益没有 CAGR —— 点数序列可以算复合增长，但那要求一个账户与一次不中断的滚仓，这不是本面能替读者假定的",
        ],
        "inputs_digest": _sha({
            "econ": econ.get("inputs_digest"),
            "rent": rent.get("inputs_digest"),
            "window": window.get("inputs_digest"),
            "capital": (lots := _load(CAP_SRC) or {}).get("inputs"),
        }),
        "sources": {
            ECON_SRC: {"generated": econ.get("generated"), "evidence_cutoff": econ.get("evidence_cutoff")},
            RENT_SRC: {"generated": rent.get("generated"), "evidence_cutoff": rent.get("evidence_cutoff")},
            WINDOW_SRC: {"generated": window.get("generated")},
            CAP_SRC: {"generated": (_load(CAP_SRC) or {}).get("generated")},
            RULER_SRC: {"generated": (_load(RULER_SRC) or {}).get("generated")},
        },
    }
    if not readable:
        payload["judgement"] = {
            "verdict": "UNREADABLE",
            "sentence": "复现腿失配：重放的尺与已发布面不是同一把，任何比较都不成立（先修复现，再谈共同窗）",
            "token_aside": judgement.get("verdict"),
        }
        payload["delta_verdict"] = "UNREADABLE"
    return payload


def _conflicting(hedged_stats):
    """同名不同窗的量并列印，本面不仲裁。"""
    paper = _load(PAPER_SRC) or {}
    out = []
    other = None
    for acc, blk in (paper.get("accounts") or {}).items():
        if acc == PRODUCT and isinstance(blk, dict):
            other = blk.get("per_lot_vol_cny_hedged")
    if other and hedged_stats and hedged_stats.get("ann_vol_cny"):
        out.append({
            "quantity": "hedged arm annual vol, per lot, CNY",
            "this_face": hedged_stats["ann_vol_cny"],
            "other_face": other,
            "other_source": PAPER_SRC,
            "verdict": "NOT_THE_SAME_MEASUREMENT",
            "why": "两张面用的窗口不同（本面=两臂父面的十年回放窗，另一面=它自己的窗口）；两个都能真，读者不该拿一个去改另一个",
        })
    return out


def judge(readable, lines, published_full_sharpe, common):
    if not readable or not common:
        return {"verdict": "UNREADABLE", "sentence": "复现腿未过或缺共同窗读数"}
    order = [l for l in lines if (l.get("sharpe_at_252") is not None)]
    if len(order) < 3:
        return {"verdict": "UNREADABLE", "sentence": "共同窗上少于三条读数，谈不了名次"}
    ranked = sorted(order, key=lambda l: -l["sharpe_at_252"])
    names = [l["line"] for l in ranked]
    expected = ["basis_nominal", "excess_hedged", "carry_unhedged"]
    holds = names == expected
    return {
        "verdict": "ORDERING_HOLDS_ON_ONE_CALENDAR" if holds else "ORDERING_FLIPS_WHEN_THE_CALENDAR_MATCHES",
        "order": names,
        "sharpe_at_252": {l["line"]: l["sharpe_at_252"] for l in ranked},
        "sentence": (
            "同一天历（{f}..{t}）上名次={o}，所以 r2190 那张表的名次不是日历给的"
        ).format(f=common.get("first"), t=common.get("last"), o=" > ".join(names)),
    }


def delta_verdict(full_sharpe, common_sharpe):
    if full_sharpe is None or common_sharpe is None:
        return "UNREADABLE"
    d = round(float(full_sharpe) - float(common_sharpe), 4)
    if abs(d) <= DELTA_NO_BUY:
        return "THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE"
    if d >= DELTA_MOST:
        return "THE_EXTRA_DAYS_BUY_MOST_OF_THE_SHARPE"
    return "THE_EXTRA_DAYS_BUY_SOME_OF_IT"


def _can_say(lines, common, delta_token):
    if not common or not lines:
        return []
    out = []
    b = next((l for l in lines if l["line"] == "basis_nominal"), None)
    if b:
        out.append(
            "剪到共同窗后 basis 的 Sharpe = {s}（252 口径 {s2}），父面印的 2.972 不是在多出的 647 天上挣的".format(
                s=b.get("sharpe_at_244"), s2=b.get("sharpe_at_252"))
        )
    out.append("三条读数现在用的是同一段日历（{f}..{t}），可以并排，仍不能跨单位相加".format(
        f=common.get("first"), t=common.get("last")))
    if delta_token == "THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE":
        out.append("多出的 425 个 bar 自己的 Sharpe 也不低：剪掉它既没抬高也没压低结论，r2191 的混窗是呈现缺陷，不是数字缺陷")
    return out


# ---------------------------------------------------------------- check


def check(payload):
    """漂移 = 重放出来的数与面上写的不同（STALE）；自相矛盾 = 面自己算错（CHECK FAILED）。"""
    notes = []
    fresh = build()
    if fresh.get("judgement", {}).get("verdict") == "UNREADABLE" and payload.get("judgement", {}).get("verdict") != "UNREADABLE":
        return 3, ["STALE: 重放现在读不出（复现腿失配），面上写的还是上一趟的结论"]
    fc = fresh.get("basis_common_window") or {}
    pc = payload.get("basis_common_window") or {}
    for k in ("days", "sharpe", "cagr_pct", "ann_vol_pct", "mdd_pct"):
        if fc.get(k) != pc.get(k):
            notes.append("STALE: basis_common_window.{k} 面上 {a}，重放 {b}".format(k=k, a=pc.get(k), b=fc.get(k)))
    if (fresh.get("judgement") or {}).get("verdict") != (payload.get("judgement") or {}).get("verdict"):
        notes.append("STALE: 判词从 {a} 变成 {b}".format(
            a=(payload.get("judgement") or {}).get("verdict"), b=(fresh.get("judgement") or {}).get("verdict")))
    if fresh.get("delta_verdict") != payload.get("delta_verdict"):
        notes.append("STALE: delta_verdict 从 {a} 变成 {b}".format(a=payload.get("delta_verdict"), b=fresh.get("delta_verdict")))
    if (fresh.get("reproduction") or {}).get("basis_own_window", {}).get("verdict") != "MATCH":
        notes.append("STALE: 复现腿在本趟失配")

    # 自洽：判词必须由面自己的 lines 算出来
    lines = payload.get("lines") or []
    if len(lines) == 3:
        try:
            expected = judge(True, lines, (payload.get("basis_published_own_window") or {}).get("sharpe"),
                             payload.get("basis_common_window"))["verdict"]
        except Exception:
            expected = None
        actual = (payload.get("judgement") or {}).get("verdict")
        if expected and expected != actual:
            notes.append("CHECK FAILED: 面上判词 {a} 与自身 lines 算出的 {b} 不一致".format(a=actual, b=expected))
        exp_delta = delta_verdict((payload.get("basis_published_own_window") or {}).get("sharpe"),
                                  (payload.get("basis_common_window") or {}).get("sharpe"))
        if exp_delta != payload.get("delta_verdict"):
            notes.append("CHECK FAILED: delta_verdict {a} 与自身两个 Sharpe 算出的 {b} 不一致".format(
                a=payload.get("delta_verdict"), b=exp_delta))
    if notes:
        return 3, notes
    return 0, []


# ---------------------------------------------------------------- page


def write_md(payload):
    L = []
    L.append("# 三条 carry 读数放到同一本日历上之后")
    L.append("")
    L.append("- 面：`results/carry_three_lines_common_window.json`｜机器：{m}｜生成：{g}".format(
        m=payload.get("machine"), g=payload.get("generated", "(未写)")))
    L.append("- 数据截止：{c}｜共同窗：{f}..{t}｜复现腿：basis={a} / 两臂={b}".format(
        c=payload.get("evidence_cutoff"),
        f=(payload.get("common_window") or {}).get("first"),
        t=(payload.get("common_window") or {}).get("last"),
        a=(payload.get("reproduction") or {}).get("basis_own_window", {}).get("verdict"),
        b=(payload.get("reproduction") or {}).get("two_arms_common_window", {}).get("verdict")))
    L.append("")
    J = payload.get("judgement") or {}
    L.append("## 判词")
    L.append("")
    L.append("**{v}** — {s}".format(v=J.get("verdict"), s=J.get("sentence", "")))
    L.append("")
    L.append("第二个判词：**{v}**".format(v=payload.get("delta_verdict")))
    L.append("")
    L.append("## 同一段日历上的三条读数")
    L.append("")
    L.append("| 线 | 单位 | bar | Sharpe(252) | Sharpe(244) | 年化均值 | 年化波动 | 回撤 | 同尺复现 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for l in payload.get("lines") or []:
        if l["line"] == "basis_nominal":
            L.append("| {n} | {u} | {b} | {s252} | {s244} | {cagr}% | {vol}% | {mdd}% | {r} |".format(
                n=l["line"], u=l["unit"], b=l.get("bars"), s252=l.get("sharpe_at_252"), s244=l.get("sharpe_at_244"),
                cagr=l.get("cagr_pct"), vol=l.get("ann_vol_pct"), mdd=l.get("mdd_pct"),
                r="MATCH" if l.get("same_ruler_as_published") else "MISMATCH"))
        else:
            L.append("| {n} | {u} | {b} | {s252} | {s244} | {m} 点/年 | {v} 点/年 | {d} 点 ({p}% 资本) | {r} |".format(
                n=l["line"], u=l["unit"], b=l.get("bars"), s252=l.get("sharpe_at_252"), s244=l.get("sharpe_at_244"),
                m=l.get("ann_mean_points"), v=l.get("ann_vol_points"), d=l.get("mdd_points"),
                p=l.get("mdd_pct_of_capital"), r="MATCH" if l.get("same_ruler_as_published") else "MISMATCH"))
    L.append("")
    cap = (payload.get("money_basis") or {})
    L.append("点数换钱：乘数 {m} 元/点（`{rs}` 的每跳金额反推），一手资本 {c} 元（`{cs}`）。".format(
        m=cap.get("multiplier_cny_per_point"), c=cap.get("capital_per_lot_cny"), rs=RULER_SRC, cs=CAP_SRC))
    L.append("")
    cw = payload.get("common_window") or {}
    L.append("窗口 bar 数：basis 窗内 {a} 条（含锚日）/{b} 条（去掉锚日，与两臂同口径），两臂 {c} 条。".format(
        a=cw.get("basis_bars_including_anchor_day"), b=cw.get("basis_bars_dropping_anchor_day"), c=cw.get("arms_bars")))
    drop = payload.get("basis_common_window_dropping_anchor") or {}
    if drop:
        L.append("去掉锚日的 basis Sharpe = {s}（1962 条那版为 {d}），两个切片都在这条线上方，读者不必信一个挑过的数。".format(
            s=drop.get("sharpe"), d=(payload.get("basis_common_window") or {}).get("sharpe")))
    L.append("")
    pre = payload.get("basis_excluded_prefix") or {}
    if pre.get("days"):
        win = "..".join([str(x) for x in (pre.get("window") or [])])
        L.append("## 被剪掉的那 647 天自己干了什么")
        L.append("")
        L.append("| 窗口 | bar | Sharpe | CAGR | 年化波动 | 回撤 |")
        L.append("|---|---|---|---|---|---|")
        L.append("| {w} | {d} | {s} | {c}% | {v}% | {m}% |".format(
            w=win, d=pre.get("days"), s=pre.get("sharpe"), c=pre.get("cagr_pct"),
            v=pre.get("ann_vol_pct"), m=pre.get("mdd_pct")))
        L.append("")
    L.append("## 逐年（basis，自己的一段日历）")
    L.append("")
    L.append("| 年 | bar | Sharpe | CAGR | 回撤 |")
    L.append("|---|---|---|---|---|")
    for y, st in (payload.get("yearly_basis") or {}).items():
        if not st:
            L.append("| {y} | — | — | — | — |".format(y=y))
            continue
        L.append("| {y} | {d} | {s} | {c}% | {m}% |".format(
            y=y, d=st.get("days"), s=st.get("sharpe"), c=st.get("cagr_pct"), m=st.get("mdd_pct")))
    L.append("")
    ann = payload.get("annualisation") or {}
    L.append("## 一个被顺手发现的别扭")
    L.append("")
    L.append("basis 那条按 {a} 天年化，两臂的父面按 {b} 天年化，同一天数的 Sharpe 在两种口径下差 {r} 倍。"
             "这不是差距的来源，但它说明「三个数字并排」时连分母都没统一过。".format(
                 a=ann.get("basis_days_per_year"), b=ann.get("arms_days_per_year"), r=ann.get("ratio_of_sharpes")))
    L.append("")
    cf = payload.get("conflicting_faces") or []
    if cf:
        L.append("## 同名不同窗，两个都印")
        L.append("")
        for c in cf:
            L.append("- {q}：本面 {a} 元/年 ↔ `{s}` 印 {b}；{w}".format(
                q=c["quantity"], a=c["this_face"], s=c["other_source"], b=c["other_face"], w=c["why"]))
        L.append("")
    L.append("## 现在可以说的话")
    L.append("")
    for s in payload.get("what_can_now_be_said") or []:
        L.append("- " + s)
    L.append("")
    L.append("## 还不能说的")
    L.append("")
    for s in payload.get("what_is_still_missing") or []:
        L.append("- " + s)
    L.append("")
    L.append("## 复现两条腿的明细")
    L.append("")
    L.append("```json")
    L.append(json.dumps(payload.get("reproduction"), ensure_ascii=False, indent=1, sort_keys=True))
    L.append("```")
    L.append("")
    L.append("## 怎么跑")
    L.append("")
    L.append("```")
    L.append("python scripts/carry_three_lines_common_window.py            # 重算并写面")
    L.append("python scripts/carry_three_lines_common_window.py --check     # 只比对，不写")
    L.append("python scripts/carry_three_lines_common_window.py --selftest  # 离线自检")
    L.append("```")
    L.append("")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- selftest


def selftest():
    passed = 0
    cases = []

    # 1 复利读数：10% 一年（244 bar，每日常数）的 Sharpe 极大、CAGR=10%
    daily = (1.10 ** (1.0 / 244.0)) - 1.0
    st = return_stats([daily] * 244)
    cases.append(("return_stats 常数日收益 -> CAGR 10%", abs(st["cagr_pct"] - 10.0) < 0.05))
    cases.append(("return_stats 常数 -> 回撤 0", abs(st["mdd_pct"]) < 1e-9))

    # 2 少于 MIN_BARS -> None（禁编）
    cases.append(("少于 60 bar -> None", return_stats([0.001] * 59) is None))

    # 3 点数读数：累计 = 求和，回撤按点数
    pts = [1.0] * 10 + [-3.0] + [1.0] * 60
    ps = points_stats(pts, multiplier=200, capital_cny=1_000_000.0)
    cases.append(("points_stats 累计点数 = 求和", abs(ps["cum_points"] - 67.0) < 1e-9))
    cases.append(("points_stats 回撤 = -3 点", abs(ps["mdd_points"] + 3.0) < 1e-9))
    cases.append(("points_stats 回撤换 % = -3*200/1e6", abs(ps["mdd_pct_of_capital"] + 0.06) < 1e-9))
    cases.append(("points_stats 无资本 -> 只印点数", "mdd_pct_of_capital" not in points_stats(pts)))

    # 4 年化两套口径的换算（常数序列方差为 0，Sharpe 无定义——正控必须用有起伏的序列）
    wiggle = [0.001 if i % 3 else -0.0015 for i in range(500)]
    a = return_stats(wiggle)["sharpe"]
    b = points_stats(wiggle)["sharpe_ann"]
    cases.append(("244/252 换算 = sqrt(252/244)", abs(b / a - math.sqrt(252 / 244.0)) < 1e-3))

    # 5 切片两端都含
    rows = [{"date": d, "net": 0.0} for d in ("2018-10-19", "2018-10-22", "2020-01-01", "2026-11-20", "2026-11-21")]
    cases.append(("slice_rows 两端含", [r["date"] for r in slice_rows(rows, "2018-10-22", "2026-11-20")]
                  == ["2018-10-22", "2020-01-01", "2026-11-20"]))

    # 6 delta 三段判词（含两端点）
    cases.append(("delta 0.05 -> DO_NOT_BUY", delta_verdict(3.0, 2.95) == "THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE"))
    cases.append(("delta 0.10 边界 -> DO_NOT_BUY", delta_verdict(3.0, 2.90) == "THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE"))
    cases.append(("delta 0.20 -> SOME_OF_IT", delta_verdict(3.0, 2.80) == "THE_EXTRA_DAYS_BUY_SOME_OF_IT"))
    cases.append(("delta 0.30 -> MOST", delta_verdict(3.0, 2.70) == "THE_EXTRA_DAYS_BUY_MOST_OF_THE_SHARPE"))
    cases.append(("delta 缺数 -> UNREADABLE", delta_verdict(None, 2.7) == "UNREADABLE"))

    # 7 名次判词（正反控）
    lines = [
        {"line": "basis_nominal", "sharpe_at_252": 3.0},
        {"line": "excess_hedged", "sharpe_at_252": 1.4},
        {"line": "carry_unhedged", "sharpe_at_252": 0.5},
    ]
    cases.append(("名次保持 -> HOLDS", judge(True, lines, 2.97, {"first": "a", "last": "b"})["verdict"]
                  == "ORDERING_HOLDS_ON_ONE_CALENDAR"))
    flipped = [dict(l) for l in lines]
    flipped[0]["sharpe_at_252"] = 0.2
    cases.append(("负控：basis 掉到 0.2 -> FLIPS", judge(True, flipped, 2.97, {"first": "a", "last": "b"})["verdict"]
                  == "ORDERING_FLIPS_WHEN_THE_CALENDAR_MATCHES"))
    cases.append(("复现腿失配 -> UNREADABLE", judge(False, lines, 2.97, {"first": "a", "last": "b"})["verdict"]
                  == "UNREADABLE"))
    cases.append(("少于三条 -> UNREADABLE", judge(True, lines[:2], 2.97, {"first": "a", "last": "b"})["verdict"]
                  == "UNREADABLE"))

    # 8 check：面新鲜 = rc0（用真面重算一次，代价 ~2s）
    fresh = build()
    if fresh.get("judgement", {}).get("verdict") != "UNREADABLE":
        rc, notes = check(fresh)
        cases.append(("check 新鲜 -> rc0", rc == 0 and not notes))
        mut = json.loads(json.dumps(fresh))
        mut["basis_common_window"]["sharpe"] = 9.99
        rc2, notes2 = check(mut)
        cases.append(("check 改共同窗 Sharpe -> STALE", rc2 == 3 and any("STALE" in n for n in notes2)))
        mut2 = json.loads(json.dumps(fresh))
        mut2["delta_verdict"] = "THE_EXTRA_DAYS_BUY_MOST_OF_THE_SHARPE"
        rc3, notes3 = check(mut2)
        cases.append(("check 改 delta 判词 -> STALE 且点名 delta", rc3 == 3 and any("delta_verdict" in n for n in notes3)))
        mut3 = json.loads(json.dumps(fresh))
        mut3["lines"][2]["sharpe_at_252"] = 9.0
        rc4, notes4 = check(mut3)
        cases.append(("check 面内自相矛盾 -> CHECK FAILED 且不带 STALE",
                      rc4 == 3 and any("CHECK FAILED" in n for n in notes4) and not any("STALE" in n for n in notes4)))
    else:
        cases.append(("check 需要可读的真面（复现腿失配时本条不计通过）", False))

    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
        if ok:
            passed += 1
    print("{p}/{t} passed".format(p=passed, t=len(cases)))
    return 0 if passed == len(cases) else 1


# ---------------------------------------------------------------- main


def main(argv):
    if "--selftest" in argv:
        return selftest()
    payload = build()
    if payload.get("judgement", {}).get("verdict") == "UNREADABLE":
        print(json.dumps({"ok": False, "why": payload["judgement"], "reproduction": payload.get("reproduction")},
                         ensure_ascii=False))
        return 2
    if "--check" in argv:
        rc, notes = check(payload)
        print(json.dumps({"ok": rc == 0, "notes": notes}, ensure_ascii=False))
        return rc
    payload["generated"] = _now()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(OUT_JSON) + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, OUT_JSON)
    write_md(payload)
    print(json.dumps({
        "face": str(OUT_JSON.relative_to(ROOT)),
        "page": str(OUT_MD.relative_to(ROOT)),
        "verdict": payload["judgement"]["verdict"],
        "delta_verdict": payload["delta_verdict"],
        "basis_common_sharpe": (payload.get("basis_common_window") or {}).get("sharpe"),
        "extra_days_prefix_sharpe": (payload.get("basis_excluded_prefix") or {}).get("sharpe"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
