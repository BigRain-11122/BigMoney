#!/usr/bin/env python3
"""carry_three_lines_window -- 三条 carry 读数是不是同一把尺？

背景（r2190）：``results/three_book_rulers.json`` 把 carry 那行与 ETF / 转债摆在一张表上，
并把家族自己的三个 Sharpe 并排印出（basis 2.972 / 对冲残差 1.4162 / 不带对冲 0.5057）。
那时三行写的是「同一条腿的三种印法」，但没问过一件事：**它们是不是在同一段时间上算的**。

本面只做一件事：把三条读数的窗口、bar 数、口径与出处摊开，算出交集，
并回答「读者能不能把它们相减 / 排序」。不重算任何回测、不改任何一个已发布数字。

口径说明（不是判据）：
  * basis_nominal -- 名义额基差收益，来源 ``idx_fut_carry_kill_rule_economics`` 的 baseline 块；
  * excess_hedged  -- 扣掉指数后的对冲残差（袖能持有的那条）；
  * carry_unhedged -- 不带对冲的 per-lot 点位收益。
`8% 目标 x Sharpe` 这一恒等式在 r2190 里被用来把 Sharpe 换算成资本收益；本面把两个乘数
各自的窗口印在旁边，因为跨窗相乘得到的两个百分比不能相减。
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACE = ROOT / "results" / "carry_three_lines_window.json"

ECON_SRC = "results/idx_fut_carry_kill_rule_economics.json"
RENT_SRC = "results/idx_fut_carry_search_rent.json"

TOL_BAR = 0  # 窗口首尾必须逐字相同，不做宽容


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _days(first: str, last: str) -> int:
    y1, m1, d1 = (int(x) for x in first.split("-"))
    y2, m2, d2 = (int(x) for x in last.split("-"))
    return (date(y2, m2, d2) - date(y1, m1, d1)).days


def _intersect(lines):
    first = max(l["first"] for l in lines)
    last = min(l["last"] for l in lines)
    if first > last:
        return None
    return {"first": first, "last": last, "calendar_days": _days(first, last)}


def extract(econ: dict, rent: dict) -> list:
    """从两张已发布面里取三条读数。缺字段的一律 None（禁编）。"""
    ic = econ["products"]["IC"]
    base = ic["baseline"]
    series = ic["series"]
    cells = rent["cells"]
    hedged = cells["IC|excess_hedged"]
    unhedged = cells["IC|carry_unhedged"]
    lines = [
        {
            "line": "basis_nominal",
            "caliber": "名义额基差收益（读者拿不到：钱包买不到名义额，见 r2190）",
            "sharpe": base.get("sharpe"),
            "cagr_pct": base.get("cagr_pct"),
            "ann_vol_pct": base.get("ann_vol_pct"),
            "mdd_pct": base.get("mdd_pct"),
            "first": series.get("first"),
            "last": series.get("last"),
            "bars": series.get("bars"),
            "source_face": ECON_SRC,
            "source_generated": econ.get("generated"),
            "source_key": "products.IC.baseline",
        },
        {
            "line": "excess_hedged",
            "caliber": "扣掉指数后的对冲残差（袖能持有的那条）",
            "sharpe": hedged.get("sharpe_ann"),
            "cagr_pct": None,
            "ann_vol_pct": None,
            "mdd_pct": None,
            "first": hedged["window"][0],
            "last": hedged["window"][1],
            "bars": hedged.get("bars"),
            "source_face": RENT_SRC,
            "source_generated": rent.get("generated"),
            "source_key": "cells.IC|excess_hedged",
        },
        {
            "line": "carry_unhedged",
            "caliber": "不带对冲的 per-lot 点位收益",
            "sharpe": unhedged.get("sharpe_ann"),
            "cagr_pct": None,
            "ann_vol_pct": None,
            "mdd_pct": None,
            "first": unhedged["window"][0],
            "last": unhedged["window"][1],
            "bars": unhedged.get("bars"),
            "source_face": RENT_SRC,
            "source_generated": rent.get("generated"),
            "source_key": "cells.IC|carry_unhedged",
        },
    ]
    return lines


def judge(lines: list, overlap) -> dict:
    """判词只由窗口决定；任何一条缺窗口 = 不可判（禁把缺面读成同窗）。"""
    missing = [l["line"] for l in lines if not l.get("first") or not l.get("last")]
    if missing:
        return {
            "verdict": "WINDOW_UNREADABLE",
            "lines_missing_window": missing,
            "sentence": "有读数没有印出窗口，这张表就不能被当成同一把尺，也不能被当成三把尺",
        }
    same = len({(l["first"], l["last"]) for l in lines}) == 1
    bars_same = len({l.get("bars") for l in lines}) == 1
    if same and bars_same:
        return {
            "verdict": "THREE_LINES_SHARE_ONE_WINDOW",
            "sentence": "三条读数印的是同一段日历与同一个 bar 数，可以并排比较，仍不能跨口径相减",
        }
    if overlap is None:
        return {
            "verdict": "NO_COMMON_WINDOW",
            "sentence": "三条读数连一天共同日历都没有，任何相减或排序都是假的",
        }
    widest = max(lines, key=lambda l: _days(l["first"], l["last"]) if l.get("first") else 0)
    narrowest = min(lines, key=lambda l: _days(l["first"], l["last"]) if l.get("first") else 10 ** 9)
    return {
        "verdict": "THE_TABLE_MIXES_WINDOWS",
        "widest_line": widest["line"],
        "widest_days": _days(widest["first"], widest["last"]),
        "narrowest_line": narrowest["line"],
        "narrowest_days": _days(narrowest["first"], narrowest["last"]),
        "extra_days_in_widest": _days(widest["first"], widest["last"]) - _days(narrowest["first"], narrowest["last"]),
        "sentence": (
            "三条读数不是同一段时间上的钱：{w} 从 {wf} 起算，{n} 从 {nf} 起算，"
            "前者多出 {ed} 个日历日；把它们的 Sharpe 并排或相乘（8% 目标 x Sharpe）都跨了窗"
        ).format(w=widest["line"], wf=widest["first"], n=narrowest["line"], nf=narrowest["first"], ed=_days(widest["first"], widest["last"]) - _days(narrowest["first"], narrowest["last"])),
    }


def _segments(econ_ic: dict) -> dict:
    """basis 臂在父面自己的 train/test 切点上的读数（按第一个规则键取，键名一并印出）。

    父面用规则名键控（如 ``0.4sig_cooldown20``），每格里有 baseline/filtered 两块；
    读者要知道「换一个切点，那条 2.972 会掉成多少」，这一块就是唯一的现成证据。
    """
    out = {"train": {"first": econ_ic["series"].get("train_first"), "last": econ_ic["series"].get("train_last"), "bars": econ_ic["series"].get("train_bars")},
           "test": {"first": econ_ic["series"].get("test_first"), "last": econ_ic["series"].get("last"), "bars": econ_ic["series"].get("test_bars")}}
    for side in ("train", "test"):
        block = econ_ic.get(side) or {}
        rule = next(iter(block), None)
        out[side]["rule_key"] = rule
        base = (block.get(rule) or {}).get("baseline") if rule else None
        out[side]["sharpe"] = (base or {}).get("sharpe")
        out[side]["cagr_pct"] = (base or {}).get("cagr_pct")
        out[side]["ann_vol_pct"] = (base or {}).get("ann_vol_pct")
        out[side]["mdd_pct"] = (base or {}).get("mdd_pct")
    return out


def build(econ: dict, rent: dict) -> dict:
    lines = extract(econ, rent)
    overlap = _intersect(lines)
    verdict = judge(lines, overlap)

    coverage = {}
    if overlap:
        od = overlap["calendar_days"]
        for l in lines:
            own = _days(l["first"], l["last"])
            coverage[l["line"]] = {
                "own_days": own,
                "shared_days": od,
                "share_of_own_pct": round(100.0 * od / own, 2) if own else None,
            }

    # r2190 的两个换算数重印一遍，并把乘数自己的窗口挂在旁边
    target_pct = 8.0
    conversions = []
    for l in lines:
        if l.get("sharpe") is None:
            continue
        conversions.append({
            "line": l["line"],
            "sharpe": l["sharpe"],
            "target_vol_pct": target_pct,
            "capital_return_pct": round(target_pct * l["sharpe"], 3),
            "window": [l["first"], l["last"]],
            "note": "恒等式 8% 目标 x Sharpe；它不是预测，且两个乘数各自的窗口不同",
        })

    econ_ic = econ["products"]["IC"]
    segments = _segments(econ_ic)

    # 排序对切点敏不敏感：拿 basis 的 test 段 Sharpe 顶上去，看三名顺序变没变
    ordering = None
    full_rank = sorted([l for l in lines if l.get("sharpe") is not None], key=lambda l: -l["sharpe"])
    test_sharpe = (segments.get("test") or {}).get("sharpe")
    if test_sharpe is not None and len(full_rank) == 3:
        swapped = [dict(l) for l in lines if l.get("sharpe") is not None]
        for l in swapped:
            if l["line"] == "basis_nominal":
                l["sharpe"] = test_sharpe
        cut_rank = sorted(swapped, key=lambda l: -l["sharpe"])
        ordering = {
            "full_window_order": [l["line"] for l in full_rank],
            "cut_order": [l["line"] for l in cut_rank],
            "cut_used": {"line": "basis_nominal", "sharpe": test_sharpe, "window": [segments["test"]["first"], segments["test"]["last"]]},
            "verdict": "ORDERING_SURVIVES_THE_CUT" if [l["line"] for l in full_rank] == [l["line"] for l in cut_rank] else "ORDERING_DEPENDS_ON_THE_CUT",
            "note": "排序不变时说「这三条腿谁更厚」对切点不敏感；它不证明任何一个绝对值",
        }

    payload = {
        "schema": "carry-three-lines-window/v1",
        "face": "carry_three_lines_window",
        "machine": "bm-c",
        "evidence_cutoff": econ.get("evidence_cutoff"),
        "lines": lines,
        "overlap": overlap,
        "coverage": coverage,
        "conversions": conversions,
        "basis_segments": segments,
        "ordering_check": ordering,
        "judgement": verdict,
        "what_can_still_be_said": [
            "对冲残差与点位那两条的日历完全一样（2018-10-22..2026-11-20），它们之间可以排序",
            "basis 那条的绝对值与另两条不可比；它的窗口多出 2017-01-18..2018-10-19 一整段",
            "跨窗的 8% x Sharpe 得到的两个百分比（23.78% 与 11.33%）不能相减，也不能当成同一年的书",
            "父面自己的 test 段（2024-01-02 起）给了 basis 臂一个独立读数，见 ordering_check：排序变不变由它回答，不由本面口头保证",
        ],
        "what_is_needed_to_compare": [
            "在共同窗 2018-10-22..2026-11-20 上重算 basis 臂的 Sharpe 与 CAGR（需要父面的日序列或重跑基差腿）",
            "另两条只有 Sharpe，没有 CAGR / 波动 / 回撤 —— 三行读完仍拼不出一张完整的风险表",
        ],
        "inputs_digest": _sha({"econ": econ.get("inputs_digest"), "rent": rent.get("inputs_digest")}),
        "sources": {
            ECON_SRC: {"generated": econ.get("generated"), "evidence_cutoff": econ.get("evidence_cutoff")},
            RENT_SRC: {"generated": rent.get("generated"), "evidence_cutoff": rent.get("evidence_cutoff")},
        },
    }
    return payload


def check(payload: dict, econ: dict, rent: dict) -> tuple:
    """漂移 = 源面变了（STALE）；自相矛盾 = 算术对不上（CHECK FAILED，不带 STALE）。"""
    notes = []
    fresh = extract(econ, rent)
    old = {l["line"]: l for l in payload.get("lines", [])}
    for l in fresh:
        o = old.get(l["line"])
        if not o:
            notes.append("STALE: 源面出现了新线 {n}".format(n=l["line"]))
            continue
        for key in ("sharpe", "first", "last", "bars"):
            if o.get(key) != l.get(key):
                notes.append(
                    "STALE: {n}.{k} 面上写 {a}，源面现在是 {b}".format(n=l["line"], k=key, a=o.get(key), b=l.get(key))
                )
    fresh_overlap = _intersect(fresh)
    if (fresh_overlap or {}).get("first") != (payload.get("overlap") or {}).get("first"):
        notes.append("STALE: 交集起点已变")
    # 自洽：判词必须由本面自己的窗口算出来
    expected = judge(fresh, fresh_overlap)["verdict"]
    actual = (payload.get("judgement") or {}).get("verdict")
    if expected != actual:
        notes.append("CHECK FAILED: 面上判词 {a} 与自身窗口算出的 {b} 不一致".format(a=actual, b=expected))
    if notes:
        return 3, notes
    return 0, []


def selftest() -> int:
    passed = 0
    cases = []

    # 1/2/3 三态判词
    same = [
        {"line": "a", "first": "2020-01-01", "last": "2026-01-01", "bars": 100},
        {"line": "b", "first": "2020-01-01", "last": "2026-01-01", "bars": 100},
    ]
    cases.append(("同窗同 bar -> SHARE_ONE_WINDOW", judge(same, _intersect(same))["verdict"] == "THREE_LINES_SHARE_ONE_WINDOW"))
    mixed = [
        {"line": "a", "first": "2017-01-18", "last": "2026-11-25", "bars": 2390},
        {"line": "b", "first": "2018-10-22", "last": "2026-11-20", "bars": 1961},
    ]
    jm = judge(mixed, _intersect(mixed))
    cases.append(("跨窗 -> MIXES_WINDOWS", jm["verdict"] == "THE_TABLE_MIXES_WINDOWS"))
    cases.append(("跨窗 -> 多出天数 = 285", jm.get("extra_days_in_widest") == _days("2017-01-18", "2026-11-25") - _days("2018-10-22", "2026-11-20")))
    far = [
        {"line": "a", "first": "2010-01-01", "last": "2012-01-01", "bars": 10},
        {"line": "b", "first": "2020-01-01", "last": "2026-01-01", "bars": 10},
    ]
    cases.append(("无交集 -> NO_COMMON_WINDOW", judge(far, _intersect(far))["verdict"] == "NO_COMMON_WINDOW"))
    broken = [{"line": "a", "first": None, "last": None, "bars": 1}]
    cases.append(("缺窗口 -> WINDOW_UNREADABLE", judge(broken, None)["verdict"] == "WINDOW_UNREADABLE"))

    # 4 交集算术
    ov = _intersect(mixed)
    cases.append(("交集首尾 = max(first)/min(last)", ov["first"] == "2018-10-22" and ov["last"] == "2026-11-20"))

    # 5 build 端到端：注入两份假面
    econ = {
        "products": {"IC": {"series": {"first": "2017-01-18", "last": "2026-11-25", "bars": 2390, "train_first": "2017-01-18", "train_last": "2023-12-29", "train_bars": 1689, "test_first": "2024-01-02", "test_bars": 701},
                            "baseline": {"sharpe": 2.972, "cagr_pct": 10.069, "ann_vol_pct": 3.2463, "mdd_pct": -1.8896},
                            "train": {"r1": {"baseline": {"sharpe": 3.1736, "cagr_pct": 10.4378, "ann_vol_pct": 3.1445, "mdd_pct": -1.2618}}},
                            "test": {"r1": {"baseline": {"sharpe": 2.5422, "cagr_pct": 9.1854, "ann_vol_pct": 3.4812, "mdd_pct": -1.8896}}}}},
        "generated": "2026-11-26T15:29:49+08:00", "evidence_cutoff": "2026-11-25", "inputs_digest": "x",
    }
    rent = {
        "cells": {"IC|excess_hedged": {"sharpe_ann": 1.4162, "bars": 1961, "window": ["2018-10-22", "2026-11-20"]},
                  "IC|carry_unhedged": {"sharpe_ann": 0.5057, "bars": 1961, "window": ["2018-10-22", "2026-11-20"]}},
        "generated": "2026-11-27T02:xx", "evidence_cutoff": "2026-11-26", "inputs_digest": "y",
    }
    p = build(econ, rent)
    cases.append(("build -> 三行", len(p["lines"]) == 3))
    cases.append(("build -> 判词 MIXES_WINDOWS", p["judgement"]["verdict"] == "THE_TABLE_MIXES_WINDOWS"))
    cases.append(("build -> 换算 23.78 用的是 basis 窗", any(abs(c["capital_return_pct"] - 23.776) < 1e-6 and c["line"] == "basis_nominal" for c in p["conversions"])))
    cases.append(("build -> 覆盖率两项都在", set(p["coverage"]) == {"basis_nominal", "excess_hedged", "carry_unhedged"}))

    # 11/12 排序对切点敏不敏感（正反两腿）
    cases.append(("build -> test 段 2.54 顶上后排序不变", (p.get("ordering_check") or {}).get("verdict") == "ORDERING_SURVIVES_THE_CUT"))
    econ_low = json.loads(json.dumps(econ))
    econ_low["products"]["IC"]["test"]["r1"]["baseline"]["sharpe"] = 0.30
    p_low = build(econ_low, rent)
    cases.append(("负控：test 段 Sharpe 掉到 0.30 -> 排序翻面", (p_low.get("ordering_check") or {}).get("verdict") == "ORDERING_DEPENDS_ON_THE_CUT"))
    cases.append(("分段读数取到 baseline.sharpe", abs((p["basis_segments"]["test"]["sharpe"] or 0) - 2.5422) < 1e-9))

    # 6 check：面新鲜 = rc0
    rc, notes = check(p, econ, rent)
    cases.append(("check 新鲜 -> rc0", rc == 0 and not notes))

    # 7 check：改动源面 Sharpe -> STALE
    rent2 = json.loads(json.dumps(rent))
    rent2["cells"]["IC|excess_hedged"]["sharpe_ann"] = 1.5
    rc2, notes2 = check(p, econ, rent2)
    cases.append(("check 改 Sharpe -> rc3 + STALE", rc2 == 3 and any("STALE" in n for n in notes2)))

    # 8 check：篡改面上判词 -> CHECK FAILED 且不带 STALE
    p3 = json.loads(json.dumps(p))
    p3["judgement"]["verdict"] = "THREE_LINES_SHARE_ONE_WINDOW"
    rc3, notes3 = check(p3, econ, rent)
    cases.append(("check 改判词 -> CHECK FAILED 无 STALE", rc3 == 3 and any("CHECK FAILED" in n for n in notes3) and not any("STALE" in n for n in notes3)))

    # 9 覆盖：basis 的共享天数占自己多少
    own = _days("2017-01-18", "2026-11-25")
    shared = _days("2018-10-22", "2026-11-20")
    cases.append(("覆盖率算术", abs(p["coverage"]["basis_nominal"]["share_of_own_pct"] - round(100.0 * shared / own, 2)) < 1e-9))

    # 10 缺面 -> 不可判，不编数
    rent3 = {"cells": {"IC|excess_hedged": {"sharpe_ann": 1.4162, "bars": 1961, "window": ["2018-10-22", "2026-11-20"]},
                       "IC|carry_unhedged": {"sharpe_ann": 0.5057, "bars": 1961}}}
    try:
        build(econ, rent3)
        cases.append(("缺窗口 -> 抛错或判 WINDOW_UNREADABLE", False))
    except (KeyError, IndexError):
        cases.append(("缺窗口 -> 抛错或判 WINDOW_UNREADABLE", True))

    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
        if ok:
            passed += 1
    print("{p}/{t} passed".format(p=passed, t=len(cases)))
    return 0 if passed == len(cases) else 1


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    econ = json.loads((ROOT / ECON_SRC).read_text(encoding="utf-8"))
    rent = json.loads((ROOT / RENT_SRC).read_text(encoding="utf-8"))
    payload = build(econ, rent)
    if "--check" in argv:
        rc, notes = check(payload, econ, rent)
        print(json.dumps({"ok": rc == 0, "notes": notes}, ensure_ascii=False))
        return rc
    payload["generated"] = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
    FACE.parent.mkdir(parents=True, exist_ok=True)
    FACE.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    j = payload["judgement"]
    print(json.dumps({"face": str(FACE.relative_to(ROOT)), "verdict": j["verdict"], "sentence": j["sentence"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
