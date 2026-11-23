"""Bench addendum r1981: is cell 7's GO an edge in *sizing*, or a reading of the roll mask?

The question
------------
`bench_basis_timing_size` (cell 7)判 GO：把基差按自身分位定仓（weight = clamp((80-pct)/60,0,1)）
比常驻持有 IC 多 +7.36pp/年（10.09% vs 2.73%）、IM 多 +3.67pp/年（9.30% vs 5.63%）。
但同一个产品的"常驻持有"读数在另一张面上是 9.84%（IC）——`idx_fut_roll_gap` 的
strictest 掩码（两把尺子取并集，即"任一尺子说这天是移仓日就算"）。也就是说：
cell 7 的 always-on 臂只有 2.73%，很可能不是"常驻持有很弱"，而是它用的默认移仓掩码
漏掉了 106 个真实移仓日、把这些日的基差台阶当成日常 carry 记进了收益。

那么 cell 7 的 GO 到底在测什么？本面只问一个问题：
**同一套定仓规则、同一笔成本、同一个价格面板，换成正确的移仓掩码之后，
定仓还比常驻多赚 1pp 以上吗？**

Rule (frozen before the run)
----------------------------
- 定仓规则**原件导入**（`bench_basis_timing_size.weights`）——不重写、不看结果改；
- 收益曲线**原件导入**（`bench_basis_timing_size.curve`）——同为 1.5bp/边、|Δw| 计费、掩码日 carry 记 0；
- 三张掩码逐产品各算一遍两臂：published（basis_face 默认阈值尺）/ calendar（第三周五到期窗，
  原件 `idx_fut_roll_gap.calendar_rolls`）/ strictest（二者并集）；
- 复现门：published 掩码下两臂必须复现已发布读数（IC 10.09/2.73、IM 9.30/5.63，容差 0.06pp），
  否则本面拒绝发布（算术/面板漂移先修，不解释）。

Criteria (H-alt, frozen now)
----------------------------
  H-alt  strictest 掩码下 weighted - always_on >= 1.0pp/年 **且** 逐日配对差 t >= 2.0
  verdict:
    SIZING_EDGE_SURVIVES_ALL_MASKS       H-alt 过
    SIZING_EDGE_IS_A_MASK_ARTIFACT       published 差 >= 1.0pp 但 H-alt 不过（cell 7 的 GO 降级）
    SIZING_ADDS_NOTHING_ANYWHERE         三张掩码都过不了 1.0pp
    DATA_BLOCKED                         无可用产品

Money line: 差 1pp/年 在 1 手合约上是多少钱（最新收盘 x 乘数，乘数原件导入 idx_fut_desk_sheet）。
"""
import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import bench_basis_timing_size as cell7  # noqa: E402  (weights / curve / stats: 原件)
import idx_fut_roll_gap as gap  # noqa: E402  (calendar rolls: 原件)

OUT_JSON = os.path.join(bc.RESULTS, "bench_basis_timing_size_masks.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BASIS-TIMING-SIZE-MASKS.md")
PRODUCTS = ("IC", "IM")
MASKS = ("published", "calendar", "strictest")
H_MARGIN_PP = 1.0
T_MIN = 2.0
REPRO_TOL_PP = 0.06
SPLIT = "2024-01-01"

# 已发布 cell 7 读数（复现门用；只做对账，绝不参与计算）
PUBLISHED_CELL7 = {
    "IC": {"weighted": 10.09, "always_on": 2.73, "bars": 2388},
    "IM": {"weighted": 9.30, "always_on": 5.63, "bars": 1050},
}


# ------------------------------------------------------------------ masks
def mask_arrays(dates, basis, roll):
    """三张掩码，全部对齐到 spread 的下标（k -> dates[k+1]，与 basis_face 同约定）。"""
    cal_rolls, cal_info = gap.calendar_rolls(dates, basis)
    cal = [bool(dates[k + 1] in cal_rolls) for k in range(len(roll))]
    strictest = [bool(a or b) for a, b in zip(roll, cal)]
    return {
        "published": list(roll),
        "calendar": cal,
        "strictest": strictest,
    }, cal_info


def edge_share(cal_info):
    """落窗口边缘（-before / +after 天）的移仓占比：边缘=可能被窗口截断，要如实印出来。"""
    offs = (cal_info or {}).get("offsets_from_expiry") or {}
    before, after = gap.CRITERIA["expiry_window_before_days"], gap.CRITERIA["expiry_window_after_days"]
    total = sum(offs.values())
    edge = sum(v for k, v in offs.items() if int(k) in (-before, after))
    return round(100.0 * edge / total, 1) if total else None


# ------------------------------------------------------------------ readings
def arm_stats(spread, mask, w, d1):
    """一臂一掩码：returns 原件 curve；returns/净额、回撤、分段、样本外、换手。"""
    carry, net, turnover = cell7.curve(spread, mask, w)
    split_i = next((k for k, d in enumerate(d1) if d >= SPLIT), len(d1))
    return {
        "carry_ann_pct": cell7.annualise(carry),
        "net_ann_pct": cell7.annualise(net),
        "carry_mdd_pct": cell7.mdd(carry),
        "halves_pct": [None if x is None else round(x, 2) for x in cell7.halves(carry)],
        "oos_carry_ann_pct": cell7.annualise(carry[split_i:]),
        "turnover_per_year": round(turnover * bc.TRADING_DAYS / max(len(d1), 1), 2),
        "avg_weight": round(float(np.mean(w)), 3),
        "days_in_market_pct": round(
            100.0 * float(np.mean([1.0 if x > 0.001 else 0.0 for x in w])), 1),
        "_carry_series": carry,
    }


def paired_t(diff):
    """逐日配对差的 t（自相关会抬高 t，页内如实声明）。"""
    arr = np.asarray(diff, dtype=float)
    if arr.size < 30:
        return None
    sd = float(arr.std(ddof=1))
    if sd <= 0:
        return None
    return round(float(arr.mean()) / (sd / np.sqrt(arr.size)), 2)


def verdict_for(published_delta, strictest_delta, strictest_t):
    """纯函数（selftest 直接打）：H-alt 是唯一判据。"""
    if published_delta is None or strictest_delta is None:
        return "DATA_BLOCKED"
    ok = strictest_delta >= H_MARGIN_PP and (strictest_t is not None and strictest_t >= T_MIN)
    if ok:
        return "SIZING_EDGE_SURVIVES_ALL_MASKS"
    if published_delta >= H_MARGIN_PP:
        return "SIZING_EDGE_IS_A_MASK_ARTIFACT"
    return "SIZING_ADDS_NOTHING_ANYWHERE"


def reproblems(code, products):
    """复现门：published 掩码下两臂必须与已发布 cell 7 读数一致。"""
    want = PUBLISHED_CELL7.get(code)
    got = (products.get(code) or {}).get("masks", {}).get("published")
    if not want or not got:
        return []
    out = []
    for arm in ("weighted", "always_on"):
        g = got[arm]["carry_ann_pct"]
        w = want[arm]
        if g is None or abs(g - w) > REPRO_TOL_PP:
            out.append("%s/%s published=%s != cell7=%s" % (code, arm, g, w))
    if products[code].get("bars") + 1 != want["bars"]:
        # cell 7 记的是 len(dates)，本面记的是逐日收益的条数 len(dates)-1
        out.append("%s/bars %s(+1) != cell7=%s"
                   % (code, products[code].get("bars"), want["bars"]))
    return out


# ------------------------------------------------------------------ run
def lot_notional(code, last_close):
    """1 手合约的名义金额：乘数单源 = idx_fut_desk_sheet.MULTIPLIER。"""
    try:
        import idx_fut_desk_sheet as desk
        mult = desk.MULTIPLIER.get(code)
    except Exception:  # noqa: BLE001 - 乘数缺失就必须如实说不知道
        mult = None
    if not mult or not last_close:
        return {"multiplier": mult, "cny_per_lot": None}
    return {"multiplier": mult, "cny_per_lot": round(mult * last_close)}


def cross_face(code):
    """已发布掩码面（idx_fut_roll_gap）的 strictest 读数，用来对账本面的数字。

    只读已发布件、只做并列：两张面的估计量不同（那边以保留日的均值年化，
    这边把日序列复合后扣建仓成本），差额要印出来而不是抹平。
    """
    path = os.path.join(bc.RESULTS, "idx_fut_roll_gap.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            face = json.load(fh)
        d = (face.get("dilution") or {}).get("pairs", {}).get(code) or {}
    except (OSError, ValueError):
        return {"available": False}
    return {"available": True, "face": "idx_fut_roll_gap",
            "strictest_ann_pct": d.get("strictest_ann_pct"),
            "published_ann_pct": d.get("published_ann_pct"),
            "reading": d.get("reading")}


def decomposition(pub_mask, strict_mask):
    """把标题里的 7.36pp 拆成「常驻读数被掩码抬了多少」与「定仓自己抬了多少」。"""
    a_pub = pub_mask["always_on"]["carry_ann_pct"]
    a_str = strict_mask["always_on"]["carry_ann_pct"]
    w_pub = pub_mask["weighted"]["carry_ann_pct"]
    w_str = strict_mask["weighted"]["carry_ann_pct"]
    if None in (a_pub, a_str, w_pub, w_str):
        return {}
    return {
        "published_delta_pp": round(w_pub - a_pub, 2),
        "strictest_delta_pp": round(w_str - a_str, 2),
        "always_on_shift_pp": round(a_str - a_pub, 2),
        "weighted_shift_pp": round(w_str - w_pub, 2),
        "delta_shrunk_pp": round((w_pub - a_pub) - (w_str - a_str), 2),
    }


def funding_line(code):
    """开这一手要多少资本：只读已发布资金线面（idx_fut_carry_open_capital）。"""
    path = os.path.join(bc.RESULTS, "idx_fut_carry_open_capital.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            acct = (json.load(fh).get("accounts") or {}).get(code) or {}
    except (OSError, ValueError):
        return {"available": False}
    rung = (acct.get("funding") or {}).get("first_rung_cny")
    return {"available": rung is not None, "face": "idx_fut_carry_open_capital",
            "first_rung_cny": rung,
            "target_pct": acct.get("target_pct"),
            "per_lot_vol_cny_hedged": acct.get("per_lot_vol_cny_hedged")}


def run():
    bc.weight_priority()
    products = {}
    for code in PRODUCTS:
        pair = base.PAIRS.get(code)
        if not pair:
            continue
        path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
        fut, last_close = {}, None
        for r in base.read_csv_rows(path):
            try:
                v = float(r["close"])
            except (KeyError, TypeError, ValueError):
                continue
            if v > 0:
                fut[str(r["date"])[:10]] = v
        if fut:
            last_close = fut[max(fut)]
        idx = base.load_index(pair[0])
        dates, f, i = base.aligned(fut, idx)
        if len(dates) < 400:
            products[code] = {"state": "NOT_ENOUGH_BARS", "bars": len(dates)}
            continue
        basis, spread, roll = base.basis_face(f, i, dates)
        d1 = dates[1:]
        masks, cal_info = mask_arrays(dates, basis, roll)
        w_next = cell7.weights(basis)[:-1]
        w_always = [1.0] * len(spread)

        per_mask = {}
        for name in MASKS:
            m = masks[name]
            row = {"days_excluded": sum(1 for x in m if x)}
            row["weighted"] = arm_stats(spread, m, w_next, d1)
            row["always_on"] = arm_stats(spread, m, w_always, d1)
            diff = (np.asarray(row["weighted"]["_carry_series"])
                    - np.asarray(row["always_on"]["_carry_series"]))
            row["delta_pp"] = (round(row["weighted"]["carry_ann_pct"]
                                     - row["always_on"]["carry_ann_pct"], 2)
                               if row["weighted"]["carry_ann_pct"] is not None
                               and row["always_on"]["carry_ann_pct"] is not None else None)
            row["delta_t_paired"] = paired_t(diff)
            # 日序列只用于配对 t，落盘只留读数（面要能被读，不要塞 2 万行数组）
            row["weighted"].pop("_carry_series", None)
            row["always_on"].pop("_carry_series", None)
            per_mask[name] = row

        strict = per_mask["strictest"]
        fund = funding_line(code)
        lotc = lot_notional(code, last_close)["cny_per_lot"]
        carry_cny = (round(strict["always_on"]["carry_ann_pct"] / 100.0 * lotc)
                     if strict["always_on"]["carry_ann_pct"] is not None and lotc else None)
        delta_cny = (round(strict["delta_pp"] / 100.0 * lotc)
                     if strict["delta_pp"] is not None and lotc else None)
        rung = fund.get("first_rung_cny")
        products[code] = {
            "bars": len(d1),
            "first": d1[0],
            "last": d1[-1],
            "full_years": round(len(d1) / bc.TRADING_DAYS, 2),
            "calendar": {"months_hit": cal_info.get("months_hit"),
                         "months_total": cal_info.get("months_total"),
                         "offsets_from_expiry": cal_info.get("offsets_from_expiry"),
                         "edge_share_pct": edge_share(cal_info)},
            "masks": per_mask,
            "lot": lot_notional(code, last_close),
            "money": {
                "strictest_delta_pp": strict["delta_pp"],
                "cny_per_year_on_one_lot": delta_cny,
                "always_on_carry_cny_on_one_lot": carry_cny,
                "capital_first_rung_cny": rung,
                "capital_target_pct": fund.get("target_pct"),
                "carry_pct_of_capital": (round(100.0 * carry_cny / rung, 2)
                                         if carry_cny is not None and rung else None),
                "sizing_pp_of_capital": (round(100.0 * delta_cny / rung, 2)
                                         if delta_cny is not None and rung else None),
            },
            "verdict": verdict_for(per_mask["published"]["delta_pp"],
                                   strict["delta_pp"], strict["delta_t_paired"]),
            "decomposition": decomposition(per_mask["published"], strict),
            "cross_face": cross_face(code),
        }

    usable = {k: v for k, v in products.items() if v.get("verdict")}
    problems = []
    for code in usable:
        problems.extend(reproblems(code, products))
    if problems:
        payload = {"cell": "basis_timing_size_masks", "status": "REFUSED_REPRO_MISMATCH",
                   "problems": problems, "products": products,
                   "note": "published 掩码下复现不出 cell 7 的读数 = 面板或算术已漂移，本面不出判词。"}
        os.makedirs(bc.RESULTS, exist_ok=True)
        bc.write_json(OUT_JSON, payload)
        print("REFUSED_REPRO_MISMATCH: " + "; ".join(problems))
        return payload

    pooled = ("DATA_BLOCKED" if not usable else
              ("SIZING_EDGE_SURVIVES_ALL_MASKS"
               if all(v["verdict"] == "SIZING_EDGE_SURVIVES_ALL_MASKS" for v in usable.values())
               else ("SIZING_EDGE_IS_A_MASK_ARTIFACT"
                     if any(v["verdict"] == "SIZING_EDGE_IS_A_MASK_ARTIFACT"
                            for v in usable.values())
                     else "SIZING_ADDS_NOTHING_ANYWHERE")))
    payload = {
        "cell": "basis_timing_size_masks",
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": max((v.get("last") for v in usable.values() if v.get("last")),
                               default="n/a"),
        "criteria": {"H_alt_margin_pp": H_MARGIN_PP, "H_alt_t_min": T_MIN,
                     "repro_tolerance_pp": REPRO_TOL_PP, "split": SPLIT,
                     "cost_bp_side": cell7.COST_BP_SIDE,
                     "weight_rule": "clamp((80-pct)/60,0,1)",
                     "window": cell7.WINDOW,
                     "masks": "published / calendar(third-Friday window) / strictest(union)"},
        "reproduction": {"gate": "published arm readings must equal cell 7",
                         "cell7_published": PUBLISHED_CELL7, "problems": []},
        "products": products,
        "verdict": pooled,
        "note": ("Same rule, same cost, same bars; only the roll mask changes. "
                 "A GO that exists under one mask and not under the union of both roll rulers "
                 "is a reading about the mask, not about sizing."),
    }
    os.makedirs(bc.RESULTS, exist_ok=True)
    bc.write_json(OUT_JSON, payload)
    print("wrote %s verdict=%s cutoff=%s" % (OUT_JSON, pooled, payload["evidence_cutoff"]))
    return payload


# ------------------------------------------------------------------ page
def fmt(x):
    return "n/a" if x is None else ("%.2f" % x)


def write_md(payload):
    p = payload["products"]
    L = ["# 定仓的 GO 是掩码的读数吗（bench cell 7 追加面）", "",
         "generated %s | 判决 **%s** | 证据截止 %s"
         % (payload["generated"], payload["verdict"], payload["evidence_cutoff"]), "",
         "同一套定仓规则、同一笔成本、同一批 bar，只换移仓掩码。判据 H-alt 写在脚本头部、跑前冻结：",
         "strictest 掩码下定仓要比常驻多 ≥%.1fpp/年且逐日配对 t ≥ %.1f。" % (H_MARGIN_PP, T_MIN), "",
         "| 产品 | 掩码 | 剔除日 | 常驻 carry | 定仓 carry | 差(pp) | 配对t | 定仓回撤 |",
         "|---|---|---|---|---|---|---|---|"]
    for code in ("IC", "IM"):
        v = p.get(code) or {}
        if not v.get("masks"):
            continue
        for name in MASKS:
            m = v["masks"][name]
            L.append("| %s | %s | %d | %s%% | %s%% | %s | %s | %s%% |"
                     % (code, name, m["days_excluded"],
                        fmt(m["always_on"]["carry_ann_pct"]),
                        fmt(m["weighted"]["carry_ann_pct"]),
                        fmt(m["delta_pp"]),
                        "n/a" if m["delta_t_paired"] is None else "%.2f" % m["delta_t_paired"],
                        fmt(m["weighted"]["carry_mdd_pct"])))
        L.append("")
    L += ["## 读法", ""]
    for code in ("IC", "IM"):
        v = p.get(code) or {}
        if not v.get("masks"):
            continue
        pub = v["masks"]["published"]
        strict = v["masks"]["strictest"]
        L.append("- **%s**：默认掩码下定仓比常驻多 %spp（复现已发布 cell 7）；"
                 "两把尺子取并集后常驻升到 %s%%、定仓 %s%%，差缩到 %spp（t=%s）。"
                 % (code, fmt(pub["delta_pp"]), fmt(strict["always_on"]["carry_ann_pct"]),
                    fmt(strict["weighted"]["carry_ann_pct"]), fmt(strict["delta_pp"]),
                    "n/a" if strict["delta_t_paired"] is None
                    else "%.2f" % strict["delta_t_paired"]))
        lot = v.get("lot") or {}
        money = v.get("money") or {}
        dec = v.get("decomposition") or {}
        if dec:
            L.append("  拆账：标题里的 %spp 里，常驻那一臂被掩码抬了 **%spp**、定仓自己只抬了 %spp → "
                     "差缩了 %spp。"
                     % (fmt(dec.get("published_delta_pp")), fmt(dec.get("always_on_shift_pp")),
                        fmt(dec.get("weighted_shift_pp")), fmt(dec.get("delta_shrunk_pp"))))
        xf = v.get("cross_face") or {}
        if xf.get("available") and xf.get("strictest_ann_pct") is not None:
            mine = strict["always_on"]["carry_ann_pct"]
            gap_pp = None if mine is None else round(mine - xf["strictest_ann_pct"], 2)
            L.append("  对账：已发布掩码面 `idx_fut_roll_gap` 的 strictest 常驻读数是 %s%%（它把保留日均值年化），"
                     "本面复合日序列并扣建仓成本后读 %s%% → 差 %spp（估计量差，两个都印）。"
                     % (fmt(xf["strictest_ann_pct"]), fmt(mine), fmt(gap_pp)))
        if lot.get("cny_per_lot"):
            L.append("  钱：1 手 %s 名义 %s 元（乘数 %s）。strictest 下的差 %spp/年 ≈ **%s 元/年**；"
                     "同一手上的常驻 carry 本身 ≈ **%s 元/年**。"
                     % (code, format(int(lot["cny_per_lot"]), ","), lot["multiplier"],
                        fmt(money.get("strictest_delta_pp")),
                        format(int(money["cny_per_year_on_one_lot"]), ","),
                        format(int(money["always_on_carry_cny_on_one_lot"]), ",")))
            if money.get("capital_first_rung_cny"):
                L.append("  按已发布资金线（`idx_fut_carry_open_capital` 首档 %s 元、%s%% 波动目标）折算："
                         "这笔 carry = **资本的 %s%%/年**，定仓叠上去只值 **%spp/年**（且未过 t=2）。"
                         % (format(int(money["capital_first_rung_cny"]), ","),
                            fmt(money.get("capital_target_pct")),
                            fmt(money.get("carry_pct_of_capital")),
                            fmt(money.get("sizing_pp_of_capital"))))
    edge_bits = ["%s %s%%" % (c, fmt((p.get(c) or {}).get("calendar", {}).get("edge_share_pct")))
                 for c in ("IC", "IM")
                 if (p.get(c) or {}).get("calendar", {}).get("edge_share_pct") is not None]
    L += ["",
          "## 这张面没有回答的", "",
          "- 日历尺只在到期日窗口内找台阶：%s 的移仓落在窗口边缘（-6/+3 天），"
          "这些月的真实换月可能被窗口截断；边缘占比越高，calendar/strictest 两列的剔除日越可能"
          "多剔或少剔一天。两把尺子并列印出来正是为了让读者看见这个宽度。"
          % "、".join(edge_bits),
          "- 移仓当天的**实际成交成本**（旧约平仓 vs 新约开仓的价差、滑点、双边手续费）本面仍未计入："
          "两张掩码的面都只是把移仓日剔出收益序列，等于假设移仓免费。这与 `idx_fut_roll_gap` 同一条欠账。",
          "- 配对 t 按日频算，自相关会抬高 t：t≥2 只是必要条件，不是充分证据。",
          "- 本面不改 cell 7 的结论文件，也不改策略试验场登记簿（本轮另一宿主正在写共享面，按 r1907 只落新增文件）；"
          "降级生效须在无竞争的轮里把判词写进 BENCH-QUEUE 的 cells[].verdict。", ""]
    path = OUT_MD
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", path)
    return path


# ------------------------------------------------------------------ selftest
def selftest():
    ok = 0
    legs = 0

    def leg(cond, msg):
        nonlocal ok, legs
        legs += 1
        if cond:
            ok += 1
        else:
            print("FAIL", msg)

    # L1 掩码包含关系：strictest 必须 ⊇ published 与 ⊇ calendar
    dates = ["2026-01-%02d" % d for d in range(1, 29)]
    basis = [0.01 * k for k in range(len(dates))]
    roll = [k % 5 == 0 for k in range(len(dates) - 1)]
    masks, _info = mask_arrays(dates, basis, roll)
    # 包含 = 凡 published 说"是移仓日"的天，strictest 必须也是（反过来不要求）
    leg(all(s or not p for s, p in zip(masks["strictest"], masks["published"])),
        "L1 strictest ⊇ published")
    leg(all(s or not c for s, c in zip(masks["strictest"], masks["calendar"])),
        "L1 strictest ⊇ calendar")

    # L2 空掩码 + 常权：曲线必须逐等 spread，只有建仓那一天扣一次单边成本
    spread = [0.001 * ((k % 7) - 3) for k in range(50)]
    carry, _net, _turn = cell7.curve(spread, [False] * 50, [1.0] * 50)
    entry = cell7.COST_BP_SIDE / 10000.0
    leg(abs(carry[0] - (spread[0] - entry)) < 1e-15
        and all(abs(a - b) < 1e-15 for a, b in zip(carry[1:], spread[1:])),
        "L2 always-on = spread minus one entry cost")

    # L3 判词纯函数：三条分支各自可达
    leg(verdict_for(7.36, 0.25, 0.9) == "SIZING_EDGE_IS_A_MASK_ARTIFACT", "L3 artifact branch")
    leg(verdict_for(7.36, 1.40, 3.1) == "SIZING_EDGE_SURVIVES_ALL_MASKS", "L3 survives branch")
    leg(verdict_for(0.20, 0.10, 0.5) == "SIZING_ADDS_NOTHING_ANYWHERE", "L3 adds-nothing branch")
    leg(verdict_for(None, 1.0, 3.0) == "DATA_BLOCKED", "L3 blocked branch")

    # L4 复现门必须抓得住偏差（不能只看数字像不像）
    fake = {"IC": {"bars": PUBLISHED_CELL7["IC"]["bars"] - 1,
                   "masks": {"published": {
                       "weighted": {"carry_ann_pct": 10.09},
                       "always_on": {"carry_ann_pct": 2.80}}}}}
    prob = reproblems("IC", fake)
    leg(any("always_on" in x for x in prob), "L4 repro catches a 0.07pp drift")
    fake["IC"]["masks"]["published"]["always_on"]["carry_ann_pct"] = 2.73
    leg(reproblems("IC", fake) == [], "L4 repro passes on exact readings")

    print("selftest %d/%d" % (ok, legs))
    return 0 if ok == legs else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-page", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    payload = run()
    if payload.get("status") == "REFUSED_REPRO_MISMATCH":
        return 3
    if not args.no_page:
        write_md(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
