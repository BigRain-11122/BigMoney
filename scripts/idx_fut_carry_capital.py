"""IDX_FUT_CARRY_CAPITAL — translate the index-futures carry into money per unit of capital.

Parent face: results/idx_fut_basis.json (r1685) measured the discount premium as a
percent of *contract notional*: IC +4.16%/yr, IM +6.01%/yr, IF +0.80%, IH +1.74%.
Notional percent is not money. One contract is 0.8-1.3 million CNY of index; a
1,000,000 CNY account cannot buy that with cash -- it posts margin and carries the
index's own risk. This face answers the only question a capital allocator asks:
how much per year does 100万 / 300万 / 1000万 actually earn, and how far is it from
a margin call.

What this face does NOT do: it never re-derives the carry (reads the parent JSON),
never claims a Sharpe from a risk premium, and never pretends to know a fee
schedule it cannot cite -- roll cost is a sensitivity band, not a number.

Frozen reading rules (written before the numbers were read):
  R1  size is set by risk, not by the margin box. lots = floor(capital * vol_target /
      (multiplier * price * index_vol)); the margin constraint is a ceiling, never
      the target. A book that fills its margin is not sized, it is levered.
  R2  a lot you cannot afford at the vol target is not small, it is absent: when
      lots == 0, print the capital that one lot would need, not a fractional position.
  R3  margin-call distance is printed as "the index must fall X% before the account
      is wiped", per position, never annualised and never blended into a return.

Subcommands:
  run      — deterministic, local-only; writes results/idx_fut_carry_capital.json.
  selftest — hermetic synthetic checks of R1/R2/R3 and the arithmetic.
"""
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from idx_fut_basis import (PAIRS, TRADING_DAYS, mask_sentence,  # noqa: E402
                           read_csv_rows, roll_mask_block)

PARENT = os.path.join(ROOT, "results", "idx_fut_basis.json")
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
IDX_DIR = os.path.join(ROOT, "data", "index_daily")
REPO_PATH = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
OUT = os.path.join(ROOT, "results", "idx_fut_carry_capital.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_BASIS_VERDICT.md")
DOC_BEGIN = ("<!-- CARRY-CAPITAL-BLOCK:BEGIN rendered by scripts/idx_fut_carry_capital.py "
             "docblock -- do not hand-edit -->")
DOC_END = "<!-- CARRY-CAPITAL-BLOCK:END -->"

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
MARGIN_RATE = 0.15          # declared: exchange standard 12% + broker buffer; see notes
MARGIN_USE = 0.60           # never post more than 60% of capital as margin
VOL_TARGET = 0.08           # same target the adopted ETF book runs
ROLLS_PER_YEAR = 4          # quarterly contracts
ROLL_COST_BPS = (0, 10, 25, 50)   # per roll, round-trip fees + slippage sensitivity
CAPITAL_TIERS = (1_000_000, 3_000_000, 5_000_000, 10_000_000)
VOL_LOOKBACK = 1240         # ~5 years of index daily returns
CARRY_MIN_PCT = 3.0         # V1: net per capital must clear 3%/yr
# The parent quotes three central tendencies of the same basis series. Which one is
# fed in decides the money, so all three are priced and the declared one is named.
CARRY_READINGS = ("median_ann_pct", "trimmed_mean_ann_pct", "mean_ann_pct")
DECLARED_READING = "median_ann_pct"   # what parent verdict.carries[].net_carry_pct uses
LEV_CAP = 3.0               # V2: notional may not exceed 3x capital
STRESS_MAX_PCT = 30.0       # V3: the index's own worst drawdown may not cost 30% of capital


def index_vol(index_code, lookback=VOL_LOOKBACK):
    """Annualised stdev of daily log returns over the last `lookback` rows."""
    path = os.path.join(IDX_DIR, index_code + ".csv")
    rows = read_csv_rows(path)
    closes = [float(r["close"]) for r in rows if r.get("close")]
    closes = closes[-(lookback + 1):]
    rets = [math.log(closes[k] / closes[k - 1]) for k in range(1, len(closes)) if closes[k - 1] > 0]
    if len(rets) < 60:
        return None
    return statistics.stdev(rets) * math.sqrt(TRADING_DAYS)


def last_close(fut):
    rows = read_csv_rows(os.path.join(FUT_DIR, fut + ".csv"))
    for r in reversed(rows):
        try:
            return str(r["date"])[:10], float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return None, None


def cash_rate():
    """GC001 mean over the current year -- the honest yield on idle margin cash."""
    rows = read_csv_rows(REPO_PATH)
    if not rows:
        return None, None
    year = str(rows[-1]["date"])[:4]
    vals = [float(r["close"]) for r in rows if str(r["date"])[:4] == year and r.get("close")]
    if not vals:
        return None, year
    return statistics.fmean(vals) / 100.0, year


def size_position(capital, cv, vol, vol_target=VOL_TARGET, margin_rate=MARGIN_RATE,
                  margin_use=MARGIN_USE):
    """R1/R2: risk sets the size; margin is only a ceiling."""
    lots_risk = int(capital * vol_target / (cv * vol)) if vol > 0 else 0
    lots_margin = int(capital * margin_use / (cv * margin_rate)) if cv > 0 else 0
    lots = max(0, min(lots_risk, lots_margin))
    needed = (cv * vol / vol_target) if vol > 0 else None   # capital for exactly one lot
    return {"lots_risk": lots_risk, "lots_margin": lots_margin, "lots": lots,
            "one_lot_capital_needed": needed}


def build_tier(capital, cv, vol, carry_pct, cash, roll_bps_list, mdd_pct=0.0,
               carry_by_reading=None, carry_by_mask=None):
    s = size_position(capital, cv, vol)
    lots = s["lots"]
    row = {"capital_cny": capital, "lots": lots, "lots_by_risk": s["lots_risk"],
           "lots_by_margin": s["lots_margin"],
           "one_lot_capital_needed_cny": (round(s["one_lot_capital_needed"])
                                          if s["one_lot_capital_needed"] else None)}
    if lots <= 0:
        # R2: absent, and say what it would take
        return row
    notional = lots * cv
    margin = notional * MARGIN_RATE
    carry_cny = notional * carry_pct / 100.0
    cash_cny = (capital - margin) * cash
    roll = {bps: notional * bps / 10000.0 * ROLLS_PER_YEAR for bps in roll_bps_list}
    row.update({
        "notional_cny": round(notional),
        "notional_x_capital": round(notional / capital, 2),
        "margin_cny": round(margin),
        "margin_pct_of_capital": round(margin / capital * 100, 1),
        "carry_cny": round(carry_cny),
        "roll_cost_cny_by_bps": {str(k): round(v) for k, v in roll.items()},
        "cash_cny": round(cash_cny),
        "net_pct_of_capital": {str(k): round((carry_cny - v + cash_cny) / capital * 100, 2)
                               for k, v in roll.items()},
        # Same money under each parent reading. All three are printed because the
        # median is the most flattering of them and V1 sits close to the bar.
        "net_pct_of_capital_by_reading": {
            name: (None if c is None else
                   round((notional * c / 100.0 + cash_cny - roll[10]) / capital * 100, 2))
            for name, c in (carry_by_reading or {}).items()},
        # r1695: the same money under each roll mask, reading by reading. The published
        # column prices the series with the size-rule mask; the calendar column prices
        # the same days minus the splices that mask misses. Both are printed because a
        # reader who sees only one of them sizes the position off an unfinished series.
        "net_pct_of_capital_by_mask": {
            mask: {name: (None if c is None else
                          round((notional * c / 100.0 + cash_cny - roll[10]) / capital * 100, 2))
                   for name, c in (readings or {}).items()}
            for mask, readings in (carry_by_mask or {}).items()},
        # R3: two distances, printed separately. A margin call is a fixed 15% fall
        # (the posted margin is gone); the account is wiped only if the loss outruns
        # ALL the capital, which for a small position can be more than the index can
        # ever fall in one move -- so that one is allowed to read "never".
        "margin_call_fall_pct": round(MARGIN_RATE * 100, 1),
        "account_wipe_fall_pct": (round(capital / notional * 100, 1)
                                  if capital / notional <= 1.0 else None),
        "account_wipe_note": (None if capital / notional <= 1.0 else
                              "notional is %.0f%% of capital: no single index fall wipes it"
                              % (notional / capital * 100)),
        "vol_contrib_pct": round(notional * vol / capital * 100, 1),
        # V3's input: replay the index's own worst drawdown on this position.
        # A carry premium is paid for holding the index; this is the bill.
        "stress_loss_pct_of_capital": round(abs(mdd_pct) / 100.0 * notional / capital * 100, 1),
    })
    return row


def judge(faces, vol_target=VOL_TARGET, mask="published"):
    """Frozen V1/V2/V3 on the first tier that can actually hold a lot.

    Reading the verdict off a fixed tier would print "no lot" for a book that is
    merely smaller than one contract; the gate that matters is the one applied to
    the smallest capital that can trade at all.

    r1695: `mask` picks which roll mask the carry is priced under. V2/V3 do not move
    with it (they are set by contract value and the index's own drawdown), so a face
    that reports the mask as if it changed the leverage gate would be inventing
    sensitivity. A mask with no reading is UNKNOWN, never False: an absent number is
    not a failed bar (r1371 family).
    """
    out = {}
    for fut, f in faces.items():
        mid = next((t for t in f["tiers"] if t["lots"] > 0), None)
        if not mid:
            # "cannot afford a lot" is a decided answer, not a missing measurement
            out[fut] = {"V1": False, "V2": None, "V3": None, "ADMIT": False,
                        "mask": mask,
                        "why": "no tier in the table can afford one lot at the vol target",
                        "first_affordable_tier_cny": None}
            continue
        if mask == "published":
            by = mid.get("net_pct_of_capital_by_reading") or {}
            net_declared = mid["net_pct_of_capital"]["10"]
        else:
            by = (mid.get("net_pct_of_capital_by_mask") or {}).get(mask) or {}
            net_declared = by.get(DECLARED_READING)
        v1 = None if net_declared is None else bool(net_declared >= CARRY_MIN_PCT)
        # V2 is a leverage cap, not a vol check: R1 already pins vol contribution to
        # the target by construction, so a "vol <= target" gate would be a tautology.
        # What R1 does NOT cap is the notional multiple, and that is what path risk
        # (consecutive limit-down days on the index) actually scales with.
        v2 = mid["notional_x_capital"] <= LEV_CAP
        # V3 replays the index's own worst drawdown on this position: the carry is
        # payment for holding the index, and this is what holding it has already cost.
        v3 = mid["stress_loss_pct_of_capital"] <= STRESS_MAX_PCT
        v1_by = {name: (None if by.get(name) is None else by[name] >= CARRY_MIN_PCT)
                 for name in CARRY_READINGS}
        admit_by = {name: (None if v1_by[name] is None else bool(v1_by[name] and v2 and v3))
                    for name in CARRY_READINGS}
        seen = {v for v in v1_by.values() if v is not None}
        admit = None if v1 is None else bool(v1 and v2 and v3)
        out[fut] = {"V1": v1, "V2": v2, "V3": v3, "ADMIT": admit, "mask": mask,
                    "V1_by_reading": v1_by,
                    "ADMIT_by_reading": admit_by,
                    "net_declared_pct": net_declared,
                    # a verdict that only one of the three readings supports is a
                    # verdict about the estimator, not about the trade
                    "ruler_stable": len(seen) <= 1,
                    "ADMIT_every_reading": (None if admit is None else
                                            bool(admit and all(v for v in admit_by.values()
                                                               if v is not None))),
                    "first_affordable_tier_cny": mid["capital_cny"],
                    "read_on_tier": mid["capital_cny"]}
    return out


def build():
    with open(PARENT, "r", encoding="utf-8") as f:
        parent = json.load(f)
    cash, cash_year = cash_rate()
    # The parent already subtracted the index's own appreciation (the ETF that would
    # otherwise be held accrues dividends the price index does not). Re-reading the
    # raw median here would hand the engine money the tracker already earns -- so the
    # parent's derived net_carry_pct is the input, and the raw readings are only a
    # disclosure band around it.
    parent_carries = {c.get("fut"): c for c in parent.get("verdict", {}).get("carries", [])}
    mask_block = roll_mask_block()
    mask_carry = mask_block.get("carry_pct") or {}
    faces = {}
    for fut, e in parent["pairs"].items():
        if e.get("status") != "ok":
            continue
        code = PAIRS[fut][0]
        vol = index_vol(code)
        day, price = last_close(fut)
        if not vol or not price:
            continue
        cv = float(price) * MULTIPLIER[fut]
        pc = parent_carries.get(fut) or {}
        drift = float(pc.get("drift_pct") or 0.0)
        carry = pc.get("net_carry_pct")
        if carry is None:
            carry = float(e["carry"][DECLARED_READING]) - drift   # named fallback
            carry_src = "fallback: parent carry[%s] - drift (parent verdict missing)" % DECLARED_READING
        else:
            carry_src = "parent verdict.carries[%s].net_carry_pct" % fut
        carry = float(carry)
        carry_by_reading = {}
        for name in CARRY_READINGS:
            g = (e.get("carry") or {}).get(name)
            carry_by_reading[name] = None if g is None else round(float(g) - drift, 3)
        carry_by_reading[DECLARED_READING] = round(carry, 3)
        # r1695: repricing under the complete (calendar-anchored) mask. Same estimator,
        # different set of days -- the calendar column is the parent's own three readings
        # recomputed on the series with the missed splices removed, minus the same drift.
        cal_stats = (mask_carry.get(fut) or {}).get("calendar_stats") or {}
        carry_by_mask = {"published": dict(carry_by_reading),
                         "calendar": {name: (None if cal_stats.get(name) is None else
                                             round(float(cal_stats[name]) - drift, 3))
                                      for name in CARRY_READINGS}}
        mdd = float(e.get("index_max_drawdown_pct") or 0.0)
        faces[fut] = {
            "index": code,
            "index_name": PAIRS[fut][1],
            "price_date": day,
            "price": price,
            "multiplier": MULTIPLIER[fut],
            "contract_value_cny": round(cv),
            "index_vol_pct": round(vol * 100, 2),
            "carry_net_ann_pct": carry,
            "carry_net_source": carry_src,
            "carry_net_by_reading": carry_by_reading,
            "carry_net_by_mask": carry_by_mask,
            "carry_per_unit_vol": round(carry / (vol * 100), 3),
            "index_max_drawdown_pct": mdd,
            "parent_last_2y_median_ann_pct": e.get("last_2y_median_ann_pct"),
            "tiers": [build_tier(c, cv, vol, carry, cash, ROLL_COST_BPS, mdd,
                                 carry_by_reading=carry_by_reading,
                                 carry_by_mask=carry_by_mask)
                      for c in CAPITAL_TIERS],
        }
    return {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": max(f["price_date"] for f in faces.values()) if faces else None,
        "inputs": {
            "parent_face": os.path.relpath(PARENT, ROOT).replace("\\", "/"),
            "parent_generated": parent.get("generated"),
            "cash_rate_pct": round(cash * 100, 3) if cash is not None else None,
            "cash_rate_year": cash_year,
            "cash_rate_source": "data/repo_daily/GC001.csv yearly mean close",
            "margin_rate": MARGIN_RATE,
            "margin_rate_note": "declared constant: exchange standard plus broker buffer; "
                                "not read from a source file, so every tier also reports "
                                "lots_by_margin so a different rate can be re-read",
            "margin_use": MARGIN_USE,
            "vol_target": VOL_TARGET,
            "rolls_per_year": ROLLS_PER_YEAR,
            "roll_cost_bps_sensitivity": list(ROLL_COST_BPS),
            "capital_tiers": list(CAPITAL_TIERS),
            "vol_lookback_days": VOL_LOOKBACK,
            "carry_readings": list(CARRY_READINGS),
            "declared_reading": DECLARED_READING,
        },
        "rules": {
            "R1": "lots = min(risk budget / (cv * index_vol), margin ceiling); risk sets the size",
            "R2": "lots == 0 -> report one_lot_capital_needed instead of a fractional position",
            "R3": "margin_call_fall_pct is a fixed 15% fall; account_wipe_fall_pct is "
                  "capital/notional and reads null when no single fall can wipe it",
            "R4": "carry input = parent net_carry_pct (median basis minus control drift); "
                  "median/trimmed/mean are all priced and a verdict that only one of "
                  "them supports is flagged ruler_stable=false",
        },
        "faces": faces,
        # every carry below is priced on this mask; r1694 makes the face say which one
        "roll_mask": mask_block,
        # `verdict` stays the published-mask read (what every older consumer expects);
        # r1695 adds the same gates re-priced under the complete mask, never merged.
        "verdict": judge(faces, mask="published"),
        "verdict_by_mask": {m: judge(faces, mask=m) for m in ("published", "calendar")},
        "admitted_by_mask": {m: sorted(fut for fut, v in judge(faces, mask=m).items()
                                       if v.get("ADMIT") is True)
                             for m in ("published", "calendar")},
    }


def doc_block(face):
    """Render the reader-facing table from the published face -- never hand-copied.

    The parent page headlines OPEN ("the discount exists"), which is measured per
    *notional*. This block is the same trade measured per *committed capital*.
    A reader holding only one of the two numbers sizes the position by the wrong
    one, so the block states the relationship before it prints any row.
    """
    lines = [DOC_BEGIN, ""]
    lines.append("**这不是同一问题的两个答案。** §二的 OPEN 回答「贴水存不存在」，"
                 "分母是**合约名义额**；这张表回答「在你的资金上划不划算」，"
                 "分母是**必须压上的本金**，且仓位按 %.0f%% 波动目标定尺 —— "
                 "名义百分比不是钱。" % (VOL_TARGET * 100))
    lines.append("")
    lines.append(mask_sentence(face.get("roll_mask"), "carry"))
    lines.append("")
    lines.append("| 品种 | 名义 carry %/yr | 单张合约价值(万) | 一手所需本金(万) | "
                 "首个买得起档(万) | 该档名义×本金 | 该档本金净收益 %/yr (10bp) | "
                 "历史最大回撤占本金 % | 资金口径判词 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for fut in ("IF", "IC", "IH", "IM"):
        f = (face.get("faces") or {}).get(fut)
        v = (face.get("verdict") or {}).get(fut) or {}
        if not f:
            lines.append("| %s | 面缺失 | - | - | - | - | - | - | - |" % fut)
            continue
        tiers = {t["capital_cny"]: t for t in f.get("tiers") or []}
        held = tiers.get(v.get("read_on_tier")) or {}
        need = f.get("contract_value_cny", 0) * f.get("index_vol_pct", 0) / 100.0 / VOL_TARGET
        def num(x, fmt="%+.2f"):
            return "-" if x is None else fmt % x
        lines.append("| %s | %s | %.0f | %.0f | %s | %s | %s | %s | %s |" % (
            fut,
            num(f.get("carry_net_ann_pct")),
            (f.get("contract_value_cny") or 0) / 10000.0,
            need / 10000.0,
            "-" if not v.get("read_on_tier") else "%.0f" % (v["read_on_tier"] / 10000.0),
            "-" if not held.get("notional_x_capital") else "%.2f×" % held["notional_x_capital"],
            num((held.get("net_pct_of_capital") or {}).get("10")),
            num(held.get("stress_loss_pct_of_capital"), "%.1f"),
            "ADMIT" if v.get("ADMIT") else ("REJECT (V1 资金收益率 < %.1f%%)" % CARRY_MIN_PCT
                                            if v.get("V1") is False else "REJECT"),
        ))
    lines.append("")
    # r1695: the same gates, priced on the days the published mask leaves in the series.
    # Both columns print because the verdict flips between them -- and a flip that is
    # only visible in one column would read as "the bar was always this way".
    vb = face.get("verdict_by_mask") or {}
    pub_v, cal_v = vb.get("published") or {}, vb.get("calendar") or {}
    lines.append("**按完整掩码重定价（r1695）**。上表的 carry 是在**已发布尺寸式掩码**下量的，"
                 "而 r1692 量出那套掩码漏遮 64-81%% 的日历换月。把同一批日子换成日历锚定的"
                 "完整掩码重算（同一批读数口径：median/trimmed/mean，同一个 drift），"
                 "同一个 %.1f%% 线给出不同的判词 —— 两个都印，读者自己看口径：" % CARRY_MIN_PCT)
    lines.append("")
    lines.append("| 品种 | 已发布掩码 净 %%/yr | 完整掩码 净 %%/yr | 差 pp | 完整掩码 V1（≥%.1f%%） | 完整掩码判词 |"
                 % CARRY_MIN_PCT)
    lines.append("|---|---|---|---|---|---|")
    for fut in ("IF", "IC", "IH", "IM"):
        pv = pub_v.get(fut) or {}
        cv_ = cal_v.get(fut) or {}
        pn, cn = pv.get("net_declared_pct"), cv_.get("net_declared_pct")
        gap = "-" if (pn is None or cn is None) else "%+.2f" % (cn - pn)
        v1 = cv_.get("V1")
        v1_s = "-" if v1 is None else ("是" if v1 else "否")
        admit = cv_.get("ADMIT")
        word = "口径未知" if admit is None else ("ADMIT" if admit else "REJECT")
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            fut,
            "-" if pn is None else "%+.2f" % pn,
            "-" if cn is None else "%+.2f" % cn,
            gap, v1_s, word))
    lines.append("")
    adm = face.get("admitted_by_mask") or {}
    cal_list = adm.get("calendar")
    pub_list = adm.get("published")
    ic_net = (cal_v.get("IC") or {}).get("net_declared_pct")
    im_net = (cal_v.get("IM") or {}).get("net_declared_pct")
    lines.append("完整掩码下过线的品种：%s（已发布掩码下：%s）。**这不是「多赚了」，是同一批日子"
                 "少扣了「%s」档漏遮的换月跳变** —— 判词翻面本身说明这条线对掩码敏感；"
                 "过线的两个净收益只有 %s/%s %%/yr（高出线 %s/%s pp），IF/IH 仍未过。"
                 % ("、".join(cal_list) if cal_list else "无",
                    "、".join(pub_list) if pub_list else "无",
                    (face.get("roll_mask") or {}).get("published_rule") or "尺寸式",
                    "-" if ic_net is None else "%.2f" % ic_net,
                    "-" if im_net is None else "%.2f" % im_net,
                    "-" if ic_net is None else "%.2f" % (ic_net - CARRY_MIN_PCT),
                    "-" if im_net is None else "%.2f" % (im_net - CARRY_MIN_PCT)))
    lines.append("")
    lines.append("**这张表不下采纳判决**。过线只说明「按完整掩码，这两笔的资金收益率过了 %.1f%% 线」；"
                 "日历掩码也不是终点 —— 它按到期日历抓换月，但换月幅度本身还没用合约级数据重建"
                 "（r1692 遗留），所以 IC/IM 记为**候选**而不是采纳。" % CARRY_MIN_PCT)
    lines.append("")
    # the actionable half: what would have to change for the bar to be cleared
    lines.append("过 %.1f%% 线的两种走法，各自代价写在这里：**①同样的风险预算下提高名义 "
                 "= 提高波动目标**（carry 不变，风险变大）；**②增加本金**（一手所需本金以上，"
                 "每多一张就多一份 carry）。下表末列给出「如果只靠加杠杆过线」需要名义达到本金的多少倍，"
                 "以及它同时放大的历史回撤。" % CARRY_MIN_PCT)
    lines.append("")
    lines.append("| 品种 | 靠杠杆过线所需名义×本金 | 该倍数下的历史最大回撤占本金 % |")
    lines.append("|---|---|---|")
    for fut in ("IF", "IC", "IH", "IM"):
        f = (face.get("faces") or {}).get(fut) or {}
        carry = f.get("carry_net_ann_pct")
        mdd = f.get("index_max_drawdown_pct")
        if not carry or carry <= 0:
            lines.append("| %s | 不适用（carry ≤ 0） | - |" % fut)
            continue
        need_x = CARRY_MIN_PCT / carry
        lines.append("| %s | %.2f× | %.1f |" % (
            fut, need_x, abs(mdd or 0) * need_x))
    lines.append("")
    lines.append("读法：IC 需要 %.2f× 名义才能过线，而 %.0f%% 波动目标只给 0.26× —— "
                 "把杠杆拉到 0.72× 等于把指数回撤按 0.72 倍压到本金上，这正是 V3 要挡的东西。"
                 % (CARRY_MIN_PCT / ((face["faces"]["IC"]["carry_net_ann_pct"]) or 1),
                    VOL_TARGET * 100))
    lines.append(DOC_END)
    return "\n".join(lines)


def splice_doc(text, block):
    """Replace (or append) the rendered block; idempotent, never duplicates it."""
    if DOC_BEGIN in text and DOC_END in text:
        head = text[:text.index(DOC_BEGIN)]
        tail = text[text.index(DOC_END) + len(DOC_END):]
        return head + block + tail, "replaced"
    return text.rstrip("\n") + "\n\n" + block + "\n", "appended"


def checkdoc():
    """rc0 = the research page still carries this face's numbers; rc2 = drifted."""
    if not os.path.exists(OUT):
        print("no face at %s -- run `run` first" % os.path.relpath(OUT, ROOT))
        return 2
    if not os.path.exists(DOC):
        print("no page at %s" % os.path.relpath(DOC, ROOT))
        return 2
    face = json.load(open(OUT, encoding="utf-8"))
    block = doc_block(face)
    text = open(DOC, encoding="utf-8").read()
    if DOC_BEGIN not in text or DOC_END not in text:
        print("page carries no rendered block -- run `write-doc`")
        return 2
    have = text[text.index(DOC_BEGIN):text.index(DOC_END) + len(DOC_END)]
    if have.strip() != block.strip():
        print("page block differs from the face (face %s)" % face.get("generated"))
        return 2
    print("page block matches the face (%d rows, face %s)"
          % (len(face.get("faces") or {}), face.get("generated")))
    return 0


def selftest():
    ok = []

    def leg(cond, name):
        assert cond, name
        ok.append(name)

    cv, vol = 1_200_000.0, 0.22
    # R1: risk budget binds first at 100万 (not the margin box)
    s = size_position(1_000_000, cv, vol)
    leg(s["lots_risk"] == 0 and s["lots"] == 0, "R1 risk budget refuses a lot the margin box would allow")
    leg(s["lots_margin"] >= 0, "R1 margin ceiling computed")
    # 300万 is still short of one lot at the vol target; 400万 is not
    s3 = size_position(3_000_000, cv, vol)
    leg(s3["lots"] == 0, "R1 300万 still cannot hold a lot (0.91 lots at 8% target / 22% vol)")
    s4 = size_position(4_000_000, cv, vol)
    leg(s4["lots"] == 1, "R1 400万 holds exactly one lot at 8% target / 22% vol")
    # R2: the one-lot capital is the number a reader can act on
    leg(abs(s["one_lot_capital_needed"] - cv * vol / VOL_TARGET) < 1, "R2 one-lot capital = cv*vol/target")

    # arithmetic of a tier
    t = build_tier(4_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS)
    leg(t["lots"] == 1, "tier carries the size from R1")
    leg(t["carry_cny"] == round(cv * 0.04), "carry = notional * carry_pct")
    leg(t["net_pct_of_capital"]["0"] > t["net_pct_of_capital"]["50"], "higher roll cost lowers net")
    leg(t["margin_pct_of_capital"] <= MARGIN_USE * 100 + 0.5, "margin stays under the declared cap")

    # R3: wipe-out distance is capital/notional, monotone in size
    leg(abs(t["margin_call_fall_pct"] - 15.0) < 1e-9 and t["account_wipe_fall_pct"] is None,
        "R3 a 1-lot book on 400万 is called at -15% but a single fall never wipes it")
    mid5 = build_tier(5_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    t_mdd = build_tier(4_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    leg(mid5["lots"] == 1 and mid5["stress_loss_pct_of_capital"] < t_mdd["stress_loss_pct_of_capital"],
        "R3 same position, more capital -> the same index fall costs a smaller share of it")
    big = build_tier(10_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    leg(big["lots"] > t_mdd["lots"] and big["stress_loss_pct_of_capital"] > t_mdd["stress_loss_pct_of_capital"],
        "R3 more lots at the same target -> the index drawdown costs more, not less")

    # V-gates: a fat carry with an unaffordable lot is still not admitted
    faces = {"X": {"tiers": [{"capital_cny": 3_000_000, "lots": 0}]}}
    j = judge(faces)
    leg(j["X"]["ADMIT"] is False and j["X"]["why"].startswith("no tier"),
        "V: unaffordable is not small, it is absent")

    # V2 is a leverage cap: a 4x-notional book fails even with a fat carry
    hot = {"capital_cny": 4_000_000, "lots": 3, "notional_x_capital": 4.0,
           "net_pct_of_capital": {"10": 9.0}, "vol_contrib_pct": 22.0,
           "stress_loss_pct_of_capital": 10.0}
    j2 = judge({"X": {"tiers": [hot]}})
    leg(j2["X"]["V2"] is False and j2["X"]["V1"] is True,
        "V2 is the leverage cap, not a second vote on the carry")
    # and the same book at 2x is admitted on V2
    warm = dict(hot, notional_x_capital=2.0)
    leg(judge({"X": {"tiers": [warm]}})["X"]["V2"] is True, "V2 admits 2x notional")

    # R4: the same money under three readings of the same series
    band = {"median_ann_pct": 11.0, "trimmed_mean_ann_pct": 9.0, "mean_ann_pct": 6.0}
    t3 = build_tier(4_000_000, cv, vol, 11.0, 0.013, ROLL_COST_BPS, carry_by_reading=band)
    nets = t3["net_pct_of_capital_by_reading"]
    leg(nets["median_ann_pct"] > nets["trimmed_mean_ann_pct"] > nets["mean_ann_pct"],
        "R4 three readings of the same series price three different amounts of money")
    # a verdict only the median supports is not a stable verdict
    split = dict(t3, net_pct_of_capital_by_reading=nets, notional_x_capital=0.30,
                 stress_loss_pct_of_capital=12.0, vol_contrib_pct=8.0)
    j3 = judge({"X": {"tiers": [split]}})["X"]
    leg(j3["V1"] is True and j3["V1_by_reading"]["mean_ann_pct"] is False
        and j3["ruler_stable"] is False and j3["ADMIT_every_reading"] is False,
        "R4 a verdict that hangs on the median alone is flagged unstable")
    # missing reading is named, not silently filled with the median
    part = dict(t3, net_pct_of_capital_by_reading={"median_ann_pct": nets["median_ann_pct"],
                                                   "mean_ann_pct": None},
                notional_x_capital=0.30, stress_loss_pct_of_capital=12.0, vol_contrib_pct=8.0)
    j4 = judge({"X": {"tiers": [part]}})["X"]
    leg(j4["V1_by_reading"]["mean_ann_pct"] is None and j4["V1_by_reading"]["median_ann_pct"] is True,
        "R4 an absent reading stays absent instead of borrowing the median")

    # R5: the reader-facing block is rendered from the face, not copied by hand
    _f = {"faces": {"IC": {"carry_net_ann_pct": 4.159, "contract_value_cny": 1_275_000.0,
                           "index_vol_pct": 22.45, "index_max_drawdown_pct": -41.808,
                           "tiers": [{"capital_cny": 5_000_000, "lots": 1,
                                      "notional_x_capital": 0.26,
                                      "net_pct_of_capital": {"10": 2.24},
                                      "stress_loss_pct_of_capital": 10.9}]},
                    "IF": None, "IH": None, "IM": None},
          "verdict": {"IC": {"read_on_tier": 5_000_000, "V1": False, "ADMIT": False}}}
    b1 = doc_block(_f)
    leg("+4.16" in b1 and "| IC | +4.16 | 128 |" in b1 and "2.24" in b1 and "REJECT" in b1
        and DOC_BEGIN in b1 and DOC_END in b1,
        "R5 the block prints the face's numbers and names the rejected reading")
    _f2 = json.loads(json.dumps(_f))
    _f2["faces"]["IC"]["carry_net_ann_pct"] = 9.0
    _f2["verdict"]["IC"] = {"read_on_tier": 5_000_000, "V1": True, "ADMIT": True}
    b2 = doc_block(_f2)
    leg("+9.00" in b2 and "+4.16" not in b2 and "ADMIT" in b2
        and b1 != b2,
        "R5 a moved carry moves the block (two-sided: no stale copy survives)")
    # R6: the mask line travels with the face -- a moved mask face moves the page
    own = roll_mask_block()
    b3 = doc_block(dict(_f, roll_mask=own))
    leg(("遮罩口径" in b3) and (mask_sentence(own, "carry") in b3),
        "R6 the block prints the mask sentence the face carries")
    moved = json.loads(json.dumps(own))
    if moved.get("available"):
        first = sorted(moved["carry_pct"])[0]
        moved["carry_pct"][first]["published"] = 9.99
    leg(doc_block(dict(_f, roll_mask=moved)) != b3,
        "R6 a moved mask face moves the block (two-sided: no stale sentence survives)")
    leg("遮罩口径未知" in doc_block(_f),
        "R6 a face without a mask block says the mask is unknown instead of silence")
    # R7: repricing under the complete mask is a different column, never a relabelled one
    t4 = build_tier(4_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS,
                    carry_by_mask={"calendar": {"median_ann_pct": 8.0,
                                                "trimmed_mean_ann_pct": None}})
    leg(t4["net_pct_of_capital_by_mask"]["calendar"]["median_ann_pct"]
        > t4["net_pct_of_capital"]["10"],
        "R7 calendar mask prices more than the published one on the same tier")
    leg(t4["net_pct_of_capital_by_mask"]["calendar"]["trimmed_mean_ann_pct"] is None,
        "R7 an absent calendar reading stays absent instead of borrowing the median")
    masked = dict(hot, net_pct_of_capital={"10": 2.0}, notional_x_capital=0.30,
                  stress_loss_pct_of_capital=12.0, vol_contrib_pct=8.0,
                  net_pct_of_capital_by_mask={
                      "published": {"median_ann_pct": 2.0},
                      "calendar": {"median_ann_pct": 4.0}})
    jp = judge({"X": {"tiers": [masked]}}, mask="published")["X"]
    jc = judge({"X": {"tiers": [masked]}}, mask="calendar")["X"]
    leg(jp["V1"] is False and jc["V1"] is True and jc["mask"] == "calendar",
        "R7 the same book clears V1 only under the complete mask")
    leg(jc["V2"] is True and jc["V3"] is True,
        "R7 V2/V3 do not move with the mask (they are set by contract size and drawdown)")
    j5 = judge({"X": {"tiers": [dict(masked, net_pct_of_capital_by_mask=None)]}},
               mask="calendar")["X"]
    leg(j5["V1"] is None and j5["ADMIT"] is None,
        "R7 a mask with no reading is UNKNOWN, never a failed bar")
    _t1, _how1 = splice_doc("# page\n\ntext\n", b1)
    _t2, _how2 = splice_doc(_t1, b2)
    leg(_how1 == "appended" and _how2 == "replaced"
        and _t2.count(DOC_BEGIN) == 1 and "+9.00" in _t2,
        "R5 splicing is idempotent: one block, replaced in place")
    return ok


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        legs = selftest()
        print("selftest: %d legs PASS" % len(legs))
        for name in legs:
            print("  [PASS] " + name)
        return 0
    if cmd == "docblock":
        print(doc_block(json.load(open(OUT, encoding="utf-8"))))
        return 0
    if cmd == "write-doc":
        face = json.load(open(OUT, encoding="utf-8"))
        text = open(DOC, encoding="utf-8").read()
        new, how = splice_doc(text, doc_block(face))
        with open(DOC, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("page block %s (%s, face %s)"
              % (how, os.path.relpath(DOC, ROOT), face.get("generated")))
        return 0
    if cmd == "checkdoc":
        return checkdoc()
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("cash %.3f%% (%s)  evidence_cutoff %s"
          % (face["inputs"]["cash_rate_pct"] or 0, face["inputs"]["cash_rate_year"], face["evidence_cutoff"]))
    for fut, f in face["faces"].items():
        print("%s %-7s px %.1f cv %.0f万 vol %.1f%% carry %+.2f%%/yr"
              % (fut, f["index_name"], f["price"], f["contract_value_cny"] / 10000,
                 f["index_vol_pct"], f["carry_net_ann_pct"]))
        for t in f["tiers"]:
            if t["lots"] == 0:
                print("    %8.0f万: no lot (one lot needs %.0f万 at 8%% target)"
                      % (t["capital_cny"] / 10000, (t["one_lot_capital_needed_cny"] or 0) / 10000))
            else:
                print("    %8.0f万: %d lot(s) %.2fx notional  net %+.2f%% (10bp roll)  vol %.0f%%"
                      "  hist-drawdown costs %.1f%% of capital"
                      % (t["capital_cny"] / 10000, t["lots"], t["notional_x_capital"],
                         t["net_pct_of_capital"]["10"], t["vol_contrib_pct"],
                         t["stress_loss_pct_of_capital"]))
        v = face["verdict"][fut]
        band = f.get("carry_net_by_reading") or {}
        print("    net carry by reading: %s"
              % "  ".join("%s %+.2f%%" % (k.replace("_ann_pct", ""), band[k] or 0)
                          for k in CARRY_READINGS if band.get(k) is not None))
        print("    verdict ADMIT=%s (V1 %s / V2 %s / V3 %s)  ruler_stable=%s  every-reading=%s"
              % (v["ADMIT"], v["V1"], v["V2"], v["V3"], v["ruler_stable"],
                 v["ADMIT_every_reading"]))
    # r1695: the chain leg runs `run --write-doc` so the page cannot outlive the face it
    # renders -- the face and its block ship in the same step, and checkdoc is then a
    # drift alarm rather than the only producer of the page.
    if "--write-doc" in argv:
        text = open(DOC, encoding="utf-8").read()
        new, how = splice_doc(text, doc_block(face))
        with open(DOC, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("page block %s (%s, face %s)"
              % (how, os.path.relpath(DOC, ROOT), face["generated"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
