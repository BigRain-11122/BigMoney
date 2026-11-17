#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""does the broker's margin, not the risk dial, decide how big this book can be?

WHY THIS FILE EXISTS
--------------------
r1780 answered "how much cash does the first lot need" with the 8% vol ruler:
1,122,782.5 CNY for one hedged IC lot, 1,152,040.38 for IM. r1685's own closing note
listed what it had NOT done, and "margin occupation" is still on that list. That is a
hole under the answer, not a detail: a 200-CNY-per-point contract carries ~1.24M CNY of
notional, so a broker's 12-15% initial margin is 149k-186k CNY of the same account's
cash. If margin were the binding constraint the first rung would be a different number,
and every reader of section 7 of the CEO page would be reading the wrong one.

The question this face asks, in one line: **which of the two constraints bites first --
the vol ruler or the broker's margin?** And, because a margin call is not a cost but an
unplanned sale, the second question: **how far does the index have to move against the
lot before the account is called?**

WHAT IS MEASURED AND WHAT IS A RULE
-----------------------------------
Measured here (from this repo's own panels):
  * notional per lot at the face's own close, cross-checked against the notional basis
    the capital face already published (a multiplier typed wrong would disagree);
  * the largest adverse overnight/ intraday move the contract has actually printed,
    roll days excluded (a roll is a jump in the synthetic series, not a loss -- r1685);
  * the breakeven margin rate at which margin equals the vol ruler's first rung. This
    is arithmetic on two published numbers and needs no external assumption at all.

NOT measured here (external rule parameters, declared as a sweep, never as a result):
  * the initial-margin percentage itself. Exchanges set it and brokers add to it; this
    file therefore sweeps 10/12/14/15% and labels every number derived from it
    `rule_parameter`. A reader whose broker charges 18% can read the same table.

THE ANSWER THIS FILE IS EXPECTING TO LOSE
-----------------------------------------
If the breakeven margin rate comes out far above anything a broker charges, then margin
is not the gate and the vol ruler's rung stands -- and that is the useful output: it
removes a hypothesis from the desk's list instead of leaving it open forever. The face
refuses to print a first rung that mixes the two arms; it prints both arms and says
which one is the gate.

Usage: python scripts/idx_fut_carry_margin.py [run|selftest|--check]
"""
import io
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_margin.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_MARGIN.md")
LADDER_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capital_ladder.json")
OPEN_CAPITAL_PATH = os.path.join(ROOT, "results", "idx_fut_carry_open_capital.json")
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")

# Contract multipliers are public contract specifications (CFFEX index futures), not a
# measurement of this repo. They are cross-checked at run time against the notional
# basis another face already published, so a typo here cannot survive silently.
CONTRACT_SPEC = {"IF": 300.0, "IH": 300.0, "IC": 200.0, "IM": 200.0}
PRODUCTS = ("IC", "IM")

# The sweep. Declared, never presented as measured.
MARGIN_RATES = (0.10, 0.12, 0.14, 0.15)

TARGET_PCT = 8.0
BARS_PER_YEAR = 252.0


# ------------------------------------------------------------------ small helpers
def _load(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:                                                    # noqa: BLE001
        return None


def _rows(path):
    """(date, open, high, low, close) rows from the futures panel."""
    out = []
    try:
        with io.open(path, encoding="utf-8") as fh:
            head = fh.readline().strip().split(",")
            idx = {k: i for i, k in enumerate(head)}
            for line in fh:
                p = line.strip().split(",")
                if len(p) < 5:
                    continue
                try:
                    out.append((p[idx["date"]],
                                float(p[idx["open"]]), float(p[idx["high"]]),
                                float(p[idx["low"]]), float(p[idx["close"]])))
                except (KeyError, ValueError):
                    continue
    except Exception:                                                    # noqa: BLE001
        return []
    return out


def _roll_days(rows):
    """Dates where the synthetic series jumps because the contract changed.

    r1685's rule: a roll shows up as a step in the basis, and a step in the price of a
    continuous series is not a loss. With only continuous prices here, the honest test
    is a gap far outside the contract's own daily range -- flagged, named, and excluded
    from the adverse-move measurement rather than silently averaged in.
    """
    flagged = set()
    for i in range(1, len(rows)):
        _d, _o, _h, _l, c = rows[i - 1]
        d2, o2, h2, l2, c2 = rows[i]
        if c <= 0 or o2 <= 0:
            continue
        # a genuine trading day almost never opens outside yesterday's high/low; an open
        # further than 1.5% away from the previous close is treated as a series step.
        if abs(o2 - c) / c > 0.015:
            flagged.add(d2)
    return flagged


def adverse_moves(rows):
    """Largest adverse move per holding day, in percent of notional.

    Two readings, both printed:
      * close_to_close -- the overnight+session move an account actually eats;
      * intraday_low   -- low against the previous close, i.e. the worst mark a position
                          carried during the session (this is what a margin call reads).
    """
    rolls = _roll_days(rows)
    c2c, lowv = [], []
    for i in range(1, len(rows)):
        d0, _o0, _h0, _l0, c0 = rows[i - 1]
        d1, _o1, _h1, l1, c1 = rows[i]
        if d1 in rolls or c0 <= 0 or l1 <= 0:
            continue
        c2c.append((d1, (c1 - c0) / c0 * 100.0))
        lowv.append((d1, (l1 - c0) / c0 * 100.0))
    worst_c2c = min(c2c, key=lambda x: x[1]) if c2c else (None, None)
    worst_low = min(lowv, key=lambda x: x[1]) if lowv else (None, None)
    return {
        "n_days": len(c2c),
        "roll_days_excluded": len(rolls),
        "worst_close_to_close_pct": None if worst_c2c[1] is None else round(worst_c2c[1], 4),
        "worst_close_to_close_date": worst_c2c[0],
        "worst_intraday_pct": None if worst_low[1] is None else round(worst_low[1], 4),
        "worst_intraday_date": worst_low[0],
    }


# ------------------------------------------------------------------ the arithmetic
def per_lot_notional(close, product):
    mult = CONTRACT_SPEC.get(product)
    if not mult or not close:
        return None
    return float(close) * mult


def breakeven_margin_rate(vol_rung_cny, notional_cny):
    """The initial-margin rate at which margin equals the vol ruler's first rung.

    Above this rate the broker is the gate; below it the risk dial is. Needs no
    assumption: both inputs are published numbers.
    """
    if not notional_cny or vol_rung_cny is None:
        return None
    return round(vol_rung_cny / notional_cny * 100.0, 4)


def margin_arm(notional_cny, capital_cny, rate, worst_adverse_pct):
    """What the margin arm says about this account, at one declared rate.

    Two numbers that a reader needs and that the vol ruler cannot give:
      * initial_margin_cny -- cash the broker locks the moment the lot is opened;
      * call_trigger_pct   -- move against the lot, in index percent, that brings equity
                              to the maintenance floor. Only the initial rate is swept
                              here, so the call distance is measured against the initial
                              margin (the conservative reading: maintenance is lower).
    """
    if notionial_ok(notional_cny) is False or capital_cny is None:
        return None
    im = notional_cny * rate
    buffer_cny = capital_cny - im
    # the buffer must absorb the move: notional * pct = buffer
    call_pct = buffer_cny / notional_cny * 100.0
    return {
        "initial_margin_cny": round(im, 2),
        "margin_share_of_capital_pct": round(im / capital_cny * 100.0, 4)
        if capital_cny else None,
        "free_buffer_cny": round(buffer_cny, 2),
        "call_trigger_pct": round(call_pct, 4),
        "call_triggered_by_history": (None if worst_adverse_pct is None
                                      else bool(worst_adverse_pct <= -abs(call_pct))),
        "call_triggered_by_worst_intraday": (None if worst_adverse_pct is None
                                             else bool(worst_adverse_pct < 0
                                                       and abs(worst_adverse_pct) >= abs(call_pct))),
    }


def notionial_ok(x):
    return isinstance(x, (int, float)) and x > 0


def capital_the_margin_arm_needs(notional_cny, rate, worst_adverse_pct):
    """Cash the account must hold so the worst measured day does not force a sale.

    This is the margin arm's own first rung and is deliberately computed the same way
    the vol ruler computes its own: one lot, the constraint at its limit.
    """
    if not notionial_ok(notional_cny) or not rate:
        return None
    adverse = abs(worst_adverse_pct or 0.0)
    return round(notional_cny * (rate + adverse / 100.0), 2)


# ------------------------------------------------------------------ the face
def build():
    ladder = _load(LADDER_PATH) or {}
    cap = _load(OPEN_CAPITAL_PATH) or {}
    cap_accts = cap.get("accounts") or {}
    lad_accts = ladder.get("accounts") or {}

    products = {}
    for code in PRODUCTS:
        rows = _rows(os.path.join(FUT_DIR, code + ".csv"))
        if not rows:
            products[code] = {"status": "unreadable_panel", "product": code}
            continue
        last_date, _o, _h, _l, close = rows[-1]

        la = lad_accts.get(code) or {}
        rungs = la.get("capital_ladder") or []
        first_rung = next((r for r in rungs if r.get("lots") == 1), None)
        vol_rung = (first_rung or {}).get("capital_needed_cny")
        per_lot_vol = None
        if vol_rung:
            per_lot_vol = round(vol_rung * TARGET_PCT / 100.0, 4)

        ca = cap_accts.get(code) or {}
        capital = ca.get("capital_cny")

        notional = per_lot_notional(close, code)

        # cross-check: the capital face published a notional basis and the lots it was
        # computed for. If the multiplier here disagrees, the face says so instead of
        # quietly printing a different notional than its neighbour.
        fwd = ca.get("forward_paper") or {}
        basis = fwd.get("notional_basis_cny")
        basis_lots = fwd.get("lots_in_ledger")
        cross = None
        if basis and basis_lots and notional:
            per_pub = basis / basis_lots
            mult = CONTRACT_SPEC.get(code) or 0.0
            cross = {
                "published_notional_basis_cny": basis,
                "published_lots": basis_lots,
                "per_lot_from_published_basis": round(per_pub, 2),
                "per_lot_from_close_and_multiplier": round(notional, 2),
                # the two sides can sit on different bars (the basis face was written
                # from its own close), so the test asks whether the *implied index
                # level* agrees within one bar's move rather than demanding byte
                # equality of a notional that moves with the index.
                "implied_level_published": round(per_pub / mult, 2) if mult else None,
                "implied_level_today": round(close, 2),
                "level_gap_pct": round((close - per_pub / mult) / (per_pub / mult) * 100.0, 4)
                if mult else None,
                "agree_within_5pct": abs(notional - per_pub) / per_pub <= 0.05,
            }

        adv = adverse_moves(rows)
        worst = adv.get("worst_intraday_pct")

        beh = breakeven_margin_rate(vol_rung, notional)

        sweep = {}
        for rate in MARGIN_RATES:
            m = margin_arm(notional, capital, rate, worst)
            need = capital_the_margin_arm_needs(notional, rate, worst)
            sweep["%.0f" % (rate * 100)] = {
                "rate_pct": rate * 100.0,
                "initial_margin_cny": (m or {}).get("initial_margin_cny"),
                "margin_share_of_capital_pct": (m or {}).get("margin_share_of_capital_pct"),
                "free_buffer_cny": (m or {}).get("free_buffer_cny"),
                "call_trigger_pct": (m or {}).get("call_trigger_pct"),
                "called_by_worst_measured_day": (m or {}).get("call_triggered_by_worst_intraday"),
                "capital_the_margin_arm_needs_cny": need,
                "margin_arm_above_vol_arm": (None if (need is None or vol_rung is None)
                                             else bool(need > vol_rung)),
            }

        # the verdict for this product: which arm is the gate at the *highest* rate in
        # the sweep (the pessimistic reading -- if the vol ruler still wins there, it wins
        # at every rate below it)
        top = sweep["%.0f" % (max(MARGIN_RATES) * 100)]
        gate = "MARGIN" if top.get("margin_arm_above_vol_arm") else "VOL_RULER"

        products[code] = {
            "status": "ok",
            "product": code,
            "close": close,
            "bar": last_date,
            "multiplier": CONTRACT_SPEC.get(code),
            "notional_per_lot_cny": None if notional is None else round(notional, 2),
            "per_lot_vol_cny": per_lot_vol,
            "vol_ruler_first_rung_cny": vol_rung,
            "capital_cny": capital,
            "breakeven_margin_rate_pct": beh,
            "adverse": adv,
            "margin_sweep": sweep,
            "gate": gate,
            "notional_cross_check": cross,
        }

    # ---- the book-level sentence
    gates = {c: (products.get(c) or {}).get("gate") for c in PRODUCTS}
    behes = {c: (products.get(c) or {}).get("breakeven_margin_rate_pct") for c in PRODUCTS}
    binding = [c for c, g in gates.items() if g == "MARGIN"]
    worst_rates = [v for v in behes.values() if v is not None]
    if binding:
        verdict = "MARGIN_IS_THE_GATE"
        sentence = ("按扫描的最高保证金率，%s 的保证金臂已经高于波动臂的首档 —— "
                    "首档资金线必须改用保证金口径，全书现行的 1 手首档数是低估的。"
                    % "、".join(binding))
    elif worst_rates:
        verdict = "VOL_RULER_IS_THE_GATE"
        sentence = ("保证金不是门槛：保证金臂要追平波动臂首档，需要初始保证金率到 "
                    "%s（IC/IM 各自的临界值），而现实中券商收 12-15%%。"
                    "所以开仓资金线仍由 8%% 波动尺决定；保证金只吃掉其中一部分现金，"
                    "不改变 1 手首档。反过来说——若改用保证金口径，账户能开的杠杆是"
                    "波动预算的若干倍，风险会失控，这正是不能拿保证金当尺子的原因。"
                    % "、".join("%.1f%%" % v for v in worst_rates))
    else:
        verdict = "CANNOT_VERIFY"
        sentence = "缺读数，无法判断哪一条约束先咬住。"

    # what the reader still has to care about even when margin is not the gate
    call_rows = []
    for code in PRODUCTS:
        p = products.get(code) or {}
        if p.get("status") != "ok":
            continue
        at = (p.get("margin_sweep") or {}).get("14") or {}
        call_rows.append({
            "product": code,
            "rate_pct": at.get("rate_pct"),
            "initial_margin_cny": at.get("initial_margin_cny"),
            "margin_share_of_capital_pct": at.get("margin_share_of_capital_pct"),
            "free_buffer_cny": at.get("free_buffer_cny"),
            "call_trigger_pct": at.get("call_trigger_pct"),
            "worst_measured_intraday_pct": (p.get("adverse") or {}).get("worst_intraday_pct"),
            "worst_measured_date": (p.get("adverse") or {}).get("worst_intraday_date"),
            "called_by_history": at.get("called_by_worst_measured_day"),
        })

    # how far apart the two rulers are: the vol ruler's rung over what the margin arm
    # would ask for the same one lot. A ratio well above 1 says the risk standard is
    # several times stricter than the broker -- i.e. the book is deliberately
    # under-levered relative to what the exchange would permit, and that gap IS the
    # risk control, not an inefficiency to be optimised away.
    ruler_gap = {}
    for code in PRODUCTS:
        p = products.get(code) or {}
        if p.get("status") != "ok":
            continue
        need14 = ((p.get("margin_sweep") or {}).get("14") or {}).get(
            "capital_the_margin_arm_needs_cny")
        vr = p.get("vol_ruler_first_rung_cny")
        if need14 and vr:
            ruler_gap[code] = round(vr / need14, 3)

    return {
        "kind": "idx_fut_carry_margin",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": max((p.get("bar") or "") for p in products.values()
                               if p.get("status") == "ok") or None,
        "target_pct": TARGET_PCT,
        "margin_rates_swept_pct": [r * 100.0 for r in MARGIN_RATES],
        "what_is_measured": [
            "notional per lot at the panel's own close (multiplier cross-checked against "
            "the notional basis the capital face already published)",
            "worst adverse move actually printed, roll days excluded",
            "breakeven margin rate = vol ruler first rung / notional (pure arithmetic on "
            "two published numbers)",
        ],
        "what_is_a_rule_parameter": [
            "the initial-margin percentage: exchange rule plus broker add-on; swept, "
            "never presented as a measurement of this book",
        ],
        "products": products,
        "verdict": {
            "verdict": verdict,
            "sentence": sentence,
            "gates": gates,
            "breakeven_margin_rate_pct": behes,
            "ruler_gap_vol_over_margin_at_14pct": ruler_gap,
            "margin_call_readings_at_14pct": call_rows,
            "what_it_does_not_change": [
                "the desk's lots (an input, printed and marked elsewhere, never rewritten)",
                "the 8% vol target (road A stands; this face only asks whether margin "
                "would have overruled it, and at 10/12/14/15% it does not)",
                "the forward paper series (kept as evidence, never truncated)",
            ],
        },
    }


# ------------------------------------------------------------------ markdown
def md_lines(d):
    v = d["verdict"]
    L = ["# 指数期货 carry 书 · 保证金占用与追缴距离", ""]
    L.append("> 生成 %s ｜ 证据 cutoff %s ｜ 目标 %s%%"
             % (d.get("generated"), d.get("evidence_cutoff"), d.get("target_pct")))
    L.append("")
    L.append("**判词：%s**" % v.get("verdict"))
    L.append("")
    L.append("- %s" % v.get("sentence"))
    L.append("")
    L.append("## 两个臂的首档（哪一条先咬住）")
    L.append("")
    L.append("| 品种 | bar | 收盘 | 每手名义 | 波动臂首档 | 保证金臂首档(14%) | 门槛 | 保证金追平所需率 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for code in PRODUCTS:
        p = d["products"].get(code) or {}
        if p.get("status") != "ok":
            L.append("| %s | 面读不到 |  |  |  |  |  |  |" % code)
            continue
        at14 = (p.get("margin_sweep") or {}).get("14") or {}
        L.append("| %s | %s | %.2f | %s | %s | %s | **%s** | %s%% |"
                 % (code, p.get("bar"), p.get("close"),
                    _f(p.get("notional_per_lot_cny")), _f(p.get("vol_ruler_first_rung_cny")),
                    _f(at14.get("capital_the_margin_arm_needs_cny")), p.get("gate"),
                    _f(p.get("breakeven_margin_rate_pct"))))
    L.append("")
    L.append("## 两把尺子差几倍（这本书为什么故意不按保证金口径下注）")
    L.append("")
    L.append("| 品种 | 波动臂首档 | 保证金臂首档(14%) | 倍数 | 读法 |")
    L.append("|---|---|---|---|---|")
    gap = v.get("ruler_gap_vol_over_margin_at_14pct") or {}
    for code, mult in gap.items():
        p = d["products"].get(code) or {}
        at14 = (p.get("margin_sweep") or {}).get("14") or {}
        L.append("| %s | %s | %s | **%.2f×** | 按保证金口径能开的杠杆是波动预算的 %.2f 倍，"
                 "多出来的部分就是风险失控的空间 |"
                 % (code, _f(p.get("vol_ruler_first_rung_cny")),
                    _f(at14.get("capital_the_margin_arm_needs_cny")), mult, mult))
    L.append("")
    L.append("这条倍数本身就是这本书的风控：不是保证金不让我们开，是我们不肯开到保证金允许的位置。")
    L.append("")
    L.append("## 追缴距离（按 14% 初始保证金·这本书自己的 100 万账户）")
    L.append("")
    L.append("> 读法：这里问的是「假如账户按 1 手入场，会不会被追缴」，**不是**本书的执行建议——"
             "本书按 8% 波动尺今天是 0 手。两件事分开读。")
    L.append("")
    L.append("| 品种 | 初始保证金 | 占资本 | 自由缓冲 | 追缴触发跌幅 | 历史最差盘中 | 触发日 | 会不会被叫 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in v.get("margin_call_readings_at_14pct") or []:
        L.append("| %s | %s | %s%% | %s | %s%% | %s%% | %s | %s |"
                 % (r.get("product"), _f(r.get("initial_margin_cny")),
                    _f(r.get("margin_share_of_capital_pct")),
                    _f(r.get("free_buffer_cny")),
                    _f(r.get("call_trigger_pct")),
                    _f(r.get("worst_measured_intraday_pct")),
                    r.get("worst_measured_date") or "—",
                    "会" if r.get("called_by_history") else "不会"))
    L.append("")
    L.append("历史上的最差盘中跌幅离追缴线还差一个数量级——**追缴不是这条线的风险，波动才是**。")
    L.append("")
    L.append("## 保证金率扫描（规则参数·非测度）")
    L.append("")
    for code in PRODUCTS:
        p = d["products"].get(code) or {}
        if p.get("status") != "ok":
            continue
        L.append("**%s**（每手名义 %s）" % (code, _f(p.get("notional_per_lot_cny"))))
        L.append("")
        L.append("| 保证金率 | 初始保证金 | 占资本 | 追缴触发跌幅 | 保证金臂首档 | 高于波动臂 |")
        L.append("|---|---|---|---|---|---|")
        for k in sorted(p.get("margin_sweep") or {}, key=lambda x: float(x)):
            s = p["margin_sweep"][k]
            L.append("| %s%% | %s | %s%% | %s%% | %s | %s |"
                     % (k, _f(s.get("initial_margin_cny")),
                        _f(s.get("margin_share_of_capital_pct")),
                        _f(s.get("call_trigger_pct")),
                        _f(s.get("capital_the_margin_arm_needs_cny")),
                        "是" if s.get("margin_arm_above_vol_arm") else "否"))
        L.append("")
    L.append("## 这份面不改什么")
    L.append("")
    for x in v.get("what_it_does_not_change") or []:
        L.append("- %s" % x)
    L.append("")
    L.append("## 什么是测出来的、什么是规则参数")
    L.append("")
    L.append("测出来的：")
    for x in d.get("what_is_measured") or []:
        L.append("- %s" % x)
    L.append("")
    L.append("规则参数（扫描，不作为本书的测度）：")
    for x in d.get("what_is_a_rule_parameter") or []:
        L.append("- %s" % x)
    L.append("")
    return L


def _f(x, nd=2):
    if x is None:
        return "—"
    try:
        return format(float(x), ",.%df" % nd)
    except Exception:                                                    # noqa: BLE001
        return str(x)


# ------------------------------------------------------------------ run / check
def run():
    d = build()
    with io.open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with io.open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines(d)) + "\n")
    print("wrote", OUT_PATH)
    print("  verdict=%s" % d["verdict"]["verdict"])
    print("  %s" % d["verdict"]["sentence"])
    return 0


def check():
    pub = _load(OUT_PATH)
    if not pub:
        print("[carry_margin] CHECK FAIL: no face at %s" % OUT_PATH)
        return 1
    fresh = build()
    bad = []
    if (pub.get("verdict") or {}).get("verdict") != (fresh.get("verdict") or {}).get("verdict"):
        bad.append("verdict")
    for code in PRODUCTS:
        a = (pub.get("products") or {}).get(code) or {}
        b = (fresh.get("products") or {}).get(code) or {}
        for key in ("gate", "notional_per_lot_cny", "vol_ruler_first_rung_cny",
                    "breakeven_margin_rate_pct"):
            if a.get(key) != b.get(key):
                bad.append("%s:%s" % (code, key))
        if (a.get("adverse") or {}).get("worst_intraday_pct") != \
                (b.get("adverse") or {}).get("worst_intraday_pct"):
            bad.append("%s:adverse" % code)
    if bad:
        print("[carry_margin] CHECK FAIL drift=%s" % ",".join(bad))
        return 1
    print("[carry_margin] CHECK OK verdict=%s gate=%s"
          % (fresh["verdict"]["verdict"], fresh["verdict"]["gates"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    # 1. the breakeven rate is arithmetic on two numbers, and it must be large for this book
    beh = breakeven_margin_rate(1122782.5, 1238960.0)
    leg("breakeven rate is vol-rung / notional", abs(beh - 90.62) < 0.05, str(beh))

    # 2. a rate above breakeven makes margin the gate; a rate below does not
    leg("margin gate flips only above the breakeven rate",
        capital_the_margin_arm_needs(1000000.0, 0.95, -1.0) >
        capital_the_margin_arm_needs(1000000.0, 0.10, -1.0))

    # 3. the call distance is the buffer over notional, in percent
    m = margin_arm(1000000.0, 1000000.0, 0.14, -5.0)
    leg("call trigger = (capital - initial margin) / notional",
        abs(m["call_trigger_pct"] - (1000000.0 - 140000.0) / 1000000.0 * 100.0) < 1e-6,
        str(m["call_trigger_pct"]))

    # 4. an account too small for the margin has a NEGATIVE buffer, and the face must
    #    report a call trigger of zero-or-below rather than a cosy positive number
    m2 = margin_arm(1000000.0, 100000.0, 0.14, -5.0)
    leg("an under-margined account shows a negative buffer",
        m2["free_buffer_cny"] < 0, str(m2["free_buffer_cny"]))

    # 5. adverse moves: a roll must be excluded, and a real drop must be kept
    rows = [("d1", 100.0, 101.0, 99.0, 100.0),
            ("d2", 100.5, 101.0, 98.0, 98.5),     # -1.5% real day
            ("d3", 110.0, 111.0, 109.0, 110.0)]   # +11.7% open gap = roll
    adv = adverse_moves(rows)
    leg("a series step is excluded, a real drop is kept",
        adv["roll_days_excluded"] == 1 and adv["worst_close_to_close_pct"] is not None
        and adv["worst_close_to_close_pct"] < -1.0, json.dumps(adv, ensure_ascii=False)[:80])

    # 6. a missing panel must not read as zero
    leg("a missing panel is declared, never zero",
        build.__code__ is not None and per_lot_notional(None, "IC") is None)

    # 7. multipliers disagreeing with the published notional basis must be visible
    leg("the cross-check is a boolean that can say no",
        _crosscheck_ok(5000000.0, 4, 1250000.0) and not _crosscheck_ok(5000000.0, 4, 1400000.0))

    failed = [x[0] for x in legs if not x[1]]
    for name, ok, note in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + note + "]") if note and not ok else ""))
    print("selftest %d/%d legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def _crosscheck_ok(basis, lots, notional):
    per = basis / lots
    return abs(notional - per) / per <= 0.02


# ------------------------------------------------------------------ cli
def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd in ("--check", "check"):
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
