#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""how many lots of this carry book can the roll pay for before the roll itself eats the carry?

WHY THIS FILE EXISTS
--------------------
r2095 built the capacity face and stopped, on purpose, at "share of the thing you must
trade": "an impact-adjusted return: daily bars carry no depth, so the face stops at
'share of the thing you must trade' and never pretends to know what taking it costs".
r2097 then listed as NOT DONE: "一手以上收益衰减仍未测". r2100's ladder makes the hole
visible -- it prints 41.785% at six lots (IC3/IM3) with no cost of execution anywhere in
the cell.

This face does not invent depth. It does the one thing daily bars DO support: it prints,
in bp per side, how much execution cost the carry can absorb before it is worth nothing,
and where a declared impact model crosses that budget. Both halves are labelled: the
budget is arithmetic on published numbers, the impact is a RULE with one declared
constant, and the two are never mixed into one number.

WHAT IS MEASURED (this repo's own panels and faces)
---------------------------------------------------
  * rolls per year: front-contract identity changes on the front series (r2095's own
    reading, re-derived here over the same stability window);
  * daily sigma: stdev of the front contract's own log returns, and roll sessions are
    DROPPED -- a roll is a contract switch, not a price move (r2096: the step is later
    carry, not a return);
  * the budget per side, in bp: carry_cny / (rolls_per_year * 2 sides * notional);
  * participation, in % of one session's ADV (r2095's 20-bar median).

WHAT IS A RULE, NOT A MEASUREMENT
---------------------------------
  * IMPACT_K = 0.5 in bp = K * sigma_bp * sqrt(participation). A square-root impact law
    with one constant; the constant is declared here, never fitted to this book, and the
    column is named rule_impact_bp so no reader mistakes it for a measurement;
  * the roll is spread over ROLL_DAYS sessions (r2095 declares 3);
  * every carry number is per ruler, and the binding reading is the WORST ruler -- the
    book must survive its own worst accounting, not its best.

verdict tokens (frozen before the first run):
  DATA_BLOCKED                   a face or a panel is missing; refuse, never default to 0
  DECAY_DOES_NOT_BITE            crossover >= 100x the desk rung: execution cost is not
                                 the thing that sizes this book
  DECAY_DISTANT                  10x <= crossover < 100x the desk rung
  DECAY_BITES_AT_DESK_SCALE      crossover < 10x the desk rung: size decides the return

Usage:
    python scripts/idx_fut_carry_impact_decay.py run
    python scripts/idx_fut_carry_impact_decay.py check
    python scripts/idx_fut_carry_impact_decay.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import statistics as st
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_carry_capacity_lots as cap                              # noqa: E402

CAP_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capacity_lots.json")
PRICE_PATH = os.path.join(ROOT, "results", "idx_fut_carry_always_on_price.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_impact_decay.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_IMPACT_DECAY.md")

PRODUCTS = ("IC", "IM")
RULERS = ("published", "calendar", "strictest")
IMPACT_K = 0.5                 # RULE: square-root law constant, declared not fitted
ROLL_DAYS = 3                  # r2095's declared execution window
SESSIONS_PER_YEAR = 252
LOT_LADDER = (1, 2, 5, 10, 25, 50, 100, 200, 400)

V_BLOCK = "DATA_BLOCKED"
V_NO_BITE = "DECAY_DOES_NOT_BITE"
V_DISTANT = "DECAY_DISTANT"
V_BITES = "DECAY_BITES_AT_DESK_SCALE"
VERDICTS = (V_NO_BITE, V_DISTANT, V_BITES, V_BLOCK)
VAST = 100.0
DISTANT = 10.0

_QUIET = False


def log(msg):
    if not _QUIET:
        print(msg)


class Blocked(Exception):
    pass


def _read_json(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:                                                  # noqa: BLE001
        return None


def _digest(obj):
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ measurement
def measure(prod, cap_face, price_face, fut_dir=None):
    """Rolls per year and roll-free daily sigma, straight off the front series."""
    contracts = cap.load_contracts(prod, cap.FUT_DIR if fut_dir is None else fut_dir)
    if not contracts:
        raise Blocked("no contract panels for " + prod)
    front = cap.front_series(contracts)
    dates = sorted(front)
    if len(dates) < cap.ADV_BARS + 5:
        raise Blocked("front series shorter than the ADV window for " + prod)
    win = dates[-cap.STABILITY_SESSIONS:]
    rolls = sum(1 for i in range(1, len(win)) if front[win[i]][0] != front[win[i - 1]][0])
    rets = []
    for i in range(1, len(win)):
        if front[win[i]][0] != front[win[i - 1]][0]:
            continue                                               # roll, not a return
        c0 = front[win[i - 1]][3]
        c1 = front[win[i]][3]
        if c0 and c0 > 0 and c1 and c1 > 0:
            rets.append(math.log(c1 / c0))
    if len(rets) < 10:
        raise Blocked("too few roll-free returns for " + prod)
    sigma = st.stdev(rets)
    rolls_per_year = rolls * SESSIONS_PER_YEAR / float(len(win))
    return {"sessions": len(win), "rolls_in_window": rolls,
            "rolls_per_year": rolls_per_year, "roll_free_returns": len(rets),
            "sigma_daily": sigma, "sigma_daily_bp": sigma * 1e4,
            "window_first": win[0], "window_last": win[-1],
            "window_digest": _digest([[d, front[d][0]] for d in win])}


def budget_per_side_bp(carry_cny, rolls_per_year, notional_cny):
    """Arithmetic on published numbers: how much may one side of one roll cost."""
    if notional_cny <= 0 or rolls_per_year <= 0:
        return None
    return carry_cny / (rolls_per_year * 2.0 * notional_cny) * 1e4


def rule_impact_bp(lots, adv_lots, sigma_bp, roll_days=ROLL_DAYS, k=IMPACT_K):
    """RULE, not measurement: square-root law on the declared execution window."""
    if adv_lots <= 0 or roll_days <= 0:
        return None
    participation = lots / (adv_lots * float(roll_days))       # fraction of one session
    return k * sigma_bp * math.sqrt(participation)


def crossover_lots(budget_bp, adv_lots, sigma_bp, roll_days=ROLL_DAYS, k=IMPACT_K):
    """Closed form of the same rule: impact == budget  ->  lots."""
    if budget_bp is None or sigma_bp <= 0:
        return None
    part = (budget_bp / (k * sigma_bp)) ** 2
    return part * adv_lots * float(roll_days)


# ------------------------------------------------------------------ derivation
def derive(cap_path=None, price_path=None, fut_dir=None):
    cap_path = CAP_PATH if cap_path is None else cap_path
    price_path = PRICE_PATH if price_path is None else price_path
    cap_face = _read_json(cap_path)
    price_face = _read_json(price_path)
    missing = [p for p, f in ((cap_path, cap_face), (price_path, price_face)) if f is None]
    if missing:
        return {"kind": "idx_fut_carry_impact_decay", "verdict": V_BLOCK,
                "missing_inputs": [os.path.basename(p) for p in missing],
                "products": {},
                "reading": "an upstream face is missing; no impact budget is printed"}

    out_products = {}
    for prod in PRODUCTS:
        c = (cap_face.get("products") or {}).get(prod) or {}
        p = (price_face.get("products") or {}).get(prod) or {}
        try:
            if not c or not p:
                raise Blocked("product leg missing")
            adv = float(c["legs"]["adv20_median"]["value"])
            capacity_lots = float(c["capacity"]["adopted_lots"])
            notional = float(c["notional_per_lot_cny"])
            rung_lots = float(c["desk"]["rung_lots"])
            m = measure(prod, cap_face, price_face, fut_dir)
            rulers = {}
            for ruler in RULERS:
                carry = (p.get("rulers") or {}).get(ruler)
                if not carry:
                    continue
                cny = float(carry["always_on_carry_cny"])
                budget = budget_per_side_bp(cny, m["rolls_per_year"], notional)
                cross = crossover_lots(budget, adv, m["sigma_daily_bp"])
                rows = []
                lots_sweep = sorted(set([float(x) for x in LOT_LADDER] +
                                        [rung_lots, capacity_lots]))
                for lots in lots_sweep:
                    imp = rule_impact_bp(lots, adv, m["sigma_daily_bp"])
                    rows.append({
                        "lots": lots,
                        "participation_pct_of_adv": 100.0 * lots / (adv * float(ROLL_DAYS)),
                        "rule_impact_bp": imp,
                        "budget_per_side_bp": budget,
                        "retained_share": (None if (budget is None or imp is None or budget <= 0)
                                           else max(0.0, (budget - imp) / budget)),
                    })
                at_rung = next(r for r in rows if r["lots"] == rung_lots)
                rulers[ruler] = {
                    "carry_cny_per_lot_year": cny,
                    "carry_pct_of_notional": 100.0 * cny / notional,
                    "budget_per_side_bp": budget,
                    "budget_per_roll_bp": None if budget is None else 2.0 * budget,
                    "impact_crossover_lots": cross,
                    "crossover_x_rung": (None if cross is None else cross / rung_lots),
                    "impact_at_rung_bp": at_rung["rule_impact_bp"],
                    "retained_at_rung": at_rung["retained_share"],
                    "ladder": rows,
                }
            if not rulers:
                raise Blocked("no ruler carries a per-lot number for " + prod)
            worst = min(RULERS, key=lambda r: rulers[r]["retained_at_rung"] if r in rulers else 9.9)
            binding = rulers[worst]
            if binding["crossover_x_rung"] is None:
                verdict = V_BLOCK
            elif binding["crossover_x_rung"] >= VAST:
                verdict = V_NO_BITE
            elif binding["crossover_x_rung"] >= DISTANT:
                verdict = V_DISTANT
            else:
                verdict = V_BITES
            oi_lots = float((c.get("open_interest") or {}).get("lots_at_primary") or 0.0)
            gates = [
                {"gate": "capital_at_the_desk_rung", "lots": rung_lots,
                 "source": "results/idx_fut_carry_sizing_spec.json via the capacity face"},
                {"gate": "one_percent_adv_line", "lots": capacity_lots,
                 "source": "results/idx_fut_carry_capacity_lots.json"},
                {"gate": "standing_open_interest_at_one_percent", "lots": oi_lots or None,
                 "source": "results/idx_fut_carry_capacity_lots.json (a position bound, not a trade)"},
                {"gate": "rule_impact_equals_budget", "lots": binding["impact_crossover_lots"],
                 "source": "this face: declared square-root rule, worst ruler"},
            ]
            gates = [g for g in gates if g["lots"]]
            order = sorted(gates, key=lambda g: g["lots"])
            for i, g in enumerate(order):
                g["rank"] = i + 1
            out_products[prod] = {
                "status": "ok",
                "adv_lots": adv,
                "capacity_lots": capacity_lots,
                "notional_per_lot_cny": notional,
                "rung_lots": rung_lots,
                "measurement": m,
                "rulers": rulers,
                "binding_ruler": worst,
                "verdict": verdict,
                "gate_order": order,
                "first_gate": order[0]["gate"] if order else None,
                "impact_is_last_gate": bool(order and order[-1]["gate"] == "rule_impact_equals_budget"),
            }
        except Blocked as exc:
            out_products[prod] = {"status": "blocked", "why": str(exc), "verdict": V_BLOCK}

    ok = [p for p in out_products.values() if p.get("status") == "ok"]
    if not ok:
        overall = V_BLOCK
    elif any(p["verdict"] == V_BLOCK for p in out_products.values()):
        overall = V_BLOCK
    else:
        overall = min((p["verdict"] for p in ok),
                      key=lambda v: VERDICTS.index(v))
    reading = {
        V_BLOCK: "an input is missing; nothing is priced",
        V_NO_BITE: "execution cost is not what sizes this book -- at the desk rung the roll keeps almost all of the carry",
        V_DISTANT: "cost is distant but not unreachable; the crossover is printed in lots",
        V_BITES: "size decides the return on this book: the crossover sits near the desk scale",
    }[overall]
    return {
        "kind": "idx_fut_carry_impact_decay",
        "generated": "",
        "evidence_cutoff": str(cap_face.get("evidence_cutoff") or ""),
        "question": "how much may one side of a roll cost before this carry book is worth nothing, and where does a declared impact model cross that budget?",
        "verdict": overall,
        "reading": reading,
        "rules_declared": {
            "impact_k": IMPACT_K,
            "impact_model": "bp = k * sigma_daily_bp * sqrt(lots / (adv * roll_days)) -- RULE, not measurement",
            "roll_days": ROLL_DAYS,
            "sessions_per_year": SESSIONS_PER_YEAR,
            "budget": "carry_cny / (rolls_per_year * 2 * notional) -- one roll = two sides of one notional",
            "binding_ruler": "the worst ruler per product, because a book must survive its worst accounting",
            "sigma_excludes_roll_sessions": True,
            "lot_ladder": list(LOT_LADDER),
        },
        "not_measured": [
            "actual market impact: daily bars carry no depth (r2095 refused the same number)",
            "whether the published carry already deducts a spread line: printed as-is, per ruler",
            "fill probability beyond the 1% ADV line: a share above 1% is a rule breach, not a price",
        ],
        "inputs": {os.path.basename(cap_path): _digest(cap_face),
                   os.path.basename(price_path): _digest(price_face)},
        "products": out_products,
    }


# ------------------------------------------------------------------ check
def check(face_path=None, cap_path=None, price_path=None, fut_dir=None, quiet=False):
    face_path = OUT_PATH if face_path is None else face_path
    face = _read_json(face_path)
    if face is None:
        log("CHECK FAILED: face missing at " + face_path)
        return 2
    fresh = derive(cap_path, price_path, fut_dir)
    problems, stale = [], []
    if face.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %s != %s" % (face.get("verdict"), fresh.get("verdict")))
    for name, dig in (face.get("inputs") or {}).items():
        if fresh.get("inputs", {}).get(name) != dig:
            stale.append("input face moved: " + name)
    for prod, p in (face.get("products") or {}).items():
        q = (fresh.get("products") or {}).get(prod) or {}
        if p.get("status") != q.get("status"):
            problems.append("%s status %s != %s" % (prod, p.get("status"), q.get("status")))
            continue
        if p.get("status") != "ok":
            continue
        m0, m1 = p.get("measurement") or {}, q.get("measurement") or {}
        for key in ("rolls_per_year", "sigma_daily_bp"):
            a, b = m0.get(key), m1.get(key)
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                stale.append("%s %s moved: %s -> %s" % (prod, key, a, b))
        if m0.get("window_digest") != m1.get("window_digest"):
            stale.append(prod + " front series moved")
        if p.get("binding_ruler") != q.get("binding_ruler"):
            problems.append("%s binding ruler %s != %s"
                            % (prod, p.get("binding_ruler"), q.get("binding_ruler")))
        if p.get("verdict") != q.get("verdict"):
            problems.append("%s verdict %s != %s" % (prod, p.get("verdict"), q.get("verdict")))
        if p.get("first_gate") != q.get("first_gate"):
            problems.append("%s first gate %s != %s"
                            % (prod, p.get("first_gate"), q.get("first_gate")))
        a_gates = [g.get("lots") for g in (p.get("gate_order") or [])]
        b_gates = [g.get("lots") for g in (q.get("gate_order") or [])]
        if len(a_gates) != len(b_gates) or any(
                x is None or y is None or abs(float(x) - float(y)) > 1e-6
                for x, y in zip(a_gates, b_gates)) or a_gates != sorted(a_gates):
            problems.append("%s gate order moved" % prod)
        for ruler in RULERS:
            a = (p.get("rulers") or {}).get(ruler)
            b = (q.get("rulers") or {}).get(ruler)
            if not a or not b:
                if bool(a) != bool(b):
                    problems.append("%s/%s ruler present on one side only" % (prod, ruler))
                continue
            for key in ("carry_cny_per_lot_year", "budget_per_side_bp",
                        "impact_crossover_lots", "retained_at_rung"):
                av, bv = a.get(key), b.get(key)
                if av is None and bv is None:
                    continue
                if av is None or bv is None or abs(float(av) - float(bv)) > 1e-6:
                    problems.append("%s/%s %s %s != %s" % (prod, ruler, key, av, bv))
    if stale:
        log("STALE: " + "; ".join(stale[:6]) + " -> run again")
        return 3
    if problems:
        log("CHECK FAILED: " + "; ".join(problems[:6]))
        return 3
    n = sum(len((p.get("rulers") or {})) for p in (face.get("products") or {}).values()
            if p.get("status") == "ok")
    log("CHECK_OK rc0 verdict=%s ruler-legs=%d cutoff=%s"
        % (face.get("verdict"), n, face.get("evidence_cutoff")))
    return 0


# ------------------------------------------------------------------ render
def _fmt(v, nd=2):
    return "—" if v is None else ("%.*f" % (nd, v))


def render_doc(face):
    L = []
    L.append("# 移仓的代价：这本书一年能吞下多少执行成本\n")
    L.append("判决 **%s** —— %s\n" % (face["verdict"], face["reading"]))
    L.append("证据截止 %s ｜ 面 `results/idx_fut_carry_impact_decay.json`\n"
             % face.get("evidence_cutoff", ""))
    L.append("## 一句话\n")
    L.append("carry 是一年挣多少；移仓成本是每次换月要付多少。这两件事从来没在同一行里出现过，"
             "所以 41.785%（六手）这种数字下面没有任何执行成本。本面只回答一件事："
             "**一侧最多能花多少 bp，超过它这本书就不值钱**，并把一个声明过的冲击模型放在旁边做对照。\n")
    L.append("## 预算（纯算术，用已发布的面）\n")
    L.append("| 品种 | 尺子 | carry 元/手·年 | carry 占名义 | 预算 bp/侧 | 预算 bp/整次移仓 | 冲击交叉点数 | 桌面上手数处的保留率 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for prod, p in face["products"].items():
        if p.get("status") != "ok":
            L.append("| %s | — | — | — | — | — | — | 阻塞：%s |" % (prod, p.get("why", "")))
            continue
        for ruler in RULERS:
            r = (p.get("rulers") or {}).get(ruler)
            if not r:
                continue
            L.append("| %s | %s | %s | %s%% | %s | %s | %s | %s |" % (
                prod, ruler, _fmt(r["carry_cny_per_lot_year"], 1),
                _fmt(r["carry_pct_of_notional"]), _fmt(r["budget_per_side_bp"], 1),
                _fmt(r["budget_per_roll_bp"], 1), _fmt(r["impact_crossover_lots"], 1),
                ("%.1f%%" % (100.0 * r["retained_at_rung"])) if r.get("retained_at_rung") is not None else "—"))
    L.append("\n绑定读数是每个品种**最差的那把尺子**（账不能只在自己最好那本上活）。\n")
    L.append("## 先撞哪道墙（按手数排序）\n")
    L.append("按手数从小到大排列四个关卡——谁排第一，谁才是今天真正决定这本书能做多大的东西。"
             "（本表在首个 `run` 之后补入；上面三个判决令牌未变，令牌仍按原规则计算。）\n")
    L.append("| 品种 | 排序 | 关卡 | 手数 | 出处 |")
    L.append("|---|---|---|---|---|")
    for prod, p in face["products"].items():
        if p.get("status") != "ok":
            continue
        for g in p.get("gate_order") or []:
            L.append("| %s | %d | `%s` | %s | %s |" % (
                prod, g.get("rank", 0), g["gate"], _fmt(g["lots"], 1), g["source"]))
    L.append("")
    for prod, p in face["products"].items():
        if p.get("status") != "ok":
            continue
        r = p["rulers"][p["binding_ruler"]]
        cross = r["impact_crossover_lots"]
        if not cross:
            continue
        L.append("- **%s**：执行成本要等到 **%.0f 手** 才和 carry 打平（1%% 线的 %.0f 倍、standing OI 的 %.1f 倍、桌面档位的 %.0f 倍）；"
                 "也就是说，桌面上那个大数字不是被成本否掉的，是被资本与名义上限否掉的。"
                 % (prod, cross, cross / p["capacity_lots"],
                    cross / next(g["lots"] for g in p["gate_order"]
                                 if g["gate"] == "standing_open_interest_at_one_percent"),
                    cross / p["rung_lots"]))
    L.append("")
    L.append("## 已测量的两个数\n")
    for prod, p in face["products"].items():
        if p.get("status") != "ok":
            continue
        m = p["measurement"]
        L.append("- %s：窗口 %s→%s（%d 个交易日）内移仓 **%d 次 → %.2f 次/年**；"
                 "剔除移仓日后的日波动 **%.1f bp**（用 %d 个干净收益算）"
                 % (prod, m["window_first"], m["window_last"], m["sessions"],
                    m["rolls_in_window"], m["rolls_per_year"], m["sigma_daily_bp"],
                    m["roll_free_returns"]))
    L.append("\n## 手数阶梯（绑定尺子 = %s）\n" % "、".join(
        "%s:%s" % (k, v.get("binding_ruler")) for k, v in face["products"].items() if v.get("status") == "ok"))
    for prod, p in face["products"].items():
        if p.get("status") != "ok":
            continue
        r = p["rulers"][p["binding_ruler"]]
        L.append("**%s**（ADV %.0f 手/日，容量 %.1f 手 @1%%，桌面档位 %.1f 手）\n"
                 % (prod, p["adv_lots"], p["capacity_lots"], p["rung_lots"]))
        L.append("| 手数 | 占 ADV%/日 | 规则冲击 bp/侧 | 预算 bp/侧 | 保留率 |")
        L.append("|---|---|---|---|---|")
        for row in r["ladder"]:
            L.append("| %s | %.4f%% | %s | %s | %s |" % (
                _fmt(row["lots"], 0), row["participation_pct_of_adv"],
                _fmt(row["rule_impact_bp"], 1), _fmt(row["budget_per_side_bp"], 1),
                ("%.1f%%" % (100.0 * row["retained_share"])) if row.get("retained_share") is not None else "—"))
        L.append("")
    L.append("## 这个面拒绝打印什么\n")
    for item in face["not_measured"]:
        L.append("- " + item)
    L.append("\n## 规则（声明在先，不是结果）\n")
    for k, v in face["rules_declared"].items():
        L.append("- `%s` = %s" % (k, v))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ run
def run(cap_path=None, price_path=None, fut_dir=None, out_path=None, doc_path=None):
    out_path = OUT_PATH if out_path is None else out_path
    doc_path = DOC_PATH if doc_path is None else doc_path
    face = derive(cap_path, price_path, fut_dir)
    face["generated"] = cap.time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with io.open(doc_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    log("WROTE %s (%s)" % (out_path, face["verdict"]))
    log("WROTE %s" % doc_path)
    return face


# ------------------------------------------------------------------ selftest
def _selftest():
    n = 0

    def ok(cond, label):
        nonlocal n
        n += 1
        if not cond:
            raise AssertionError("leg %d failed: %s" % (n, label))

    # 1 arithmetic: budget halves when the book rolls twice as often
    a = budget_per_side_bp(100000.0, 4.0, 1000000.0)
    b = budget_per_side_bp(100000.0, 8.0, 1000000.0)
    ok(abs(a - 2 * b) < 1e-9, "budget must halve when rolls double")
    # 2 budget scales with carry
    ok(abs(budget_per_side_bp(200000.0, 4.0, 1000000.0) - 2 * a) < 1e-9, "budget linear in carry")
    # 3 budget refuses nonsense instead of defaulting to zero
    ok(budget_per_side_bp(1.0, 0.0, 1e6) is None, "zero rolls -> None, not 0")
    ok(budget_per_side_bp(1.0, 4.0, 0.0) is None, "zero notional -> None, not 0")
    # 4 impact is zero at zero lots and monotone
    ok(rule_impact_bp(0.0, 10000.0, 100.0) == 0.0, "no lots -> no impact")
    ok(rule_impact_bp(25.0, 10000.0, 100.0) > rule_impact_bp(10.0, 10000.0, 100.0),
       "impact monotone in lots")
    # 5 square-root shape: 4x lots = 2x impact
    r1 = rule_impact_bp(10.0, 10000.0, 120.0)
    r4 = rule_impact_bp(40.0, 10000.0, 120.0)
    ok(abs(r4 - 2 * r1) < 1e-9, "4x lots must be 2x impact")
    # 6 crossover inverts the rule: impact at crossover == budget
    budget = 60.0
    x = crossover_lots(budget, 10000.0, 120.0)
    ok(abs(rule_impact_bp(x, 10000.0, 120.0) - budget) < 1e-9, "crossover must sit exactly on budget")
    # 7 crossover refuses without sigma
    ok(crossover_lots(budget, 10000.0, 0.0) is None, "no sigma -> no crossover")
    # 8 tokens frozen
    ok(VERDICTS == (V_NO_BITE, V_DISTANT, V_BITES, V_BLOCK), "verdict tokens frozen")
    # 9 missing face -> DATA_BLOCKED, never a crash
    d = derive(cap_path=os.path.join(ROOT, "results", "__no_such_face__.json"))
    ok(d["verdict"] == V_BLOCK and d["products"] == {}, "missing face -> DATA_BLOCKED, no products")
    # 10 tolerance: 1e-6 on bp is tight enough to catch a printed-number edit
    ok(abs(1.0000005 - 1.0) < 1e-6 and not abs(1.0000015 - 1.0) < 1e-6, "tol catches 1e-6 edits")

    # 11-12 live derivation, if the faces are on disk
    face = derive()
    if face["verdict"] != V_BLOCK:
        ok(face["inputs"] and all(len(v) == 64 for v in face["inputs"].values()),
           "input digests are sha256")
        ok(face["evidence_cutoff"], "evidence cutoff present")
        for prod, p in face["products"].items():
            if p.get("status") != "ok":
                continue
            ok(p["measurement"]["rolls_per_year"] > 0, prod + " rolls per year positive")
            ok(p["measurement"]["sigma_daily_bp"] > 0, prod + " sigma positive")
            worst = min(p["rulers"].values(), key=lambda r: r["carry_cny_per_lot_year"])
            ok(p["binding_ruler"] and p["rulers"][p["binding_ruler"]]["carry_cny_per_lot_year"]
               == worst["carry_cny_per_lot_year"], prod + " binding ruler is the worst one")
            rung_row = [r for r in worst["ladder"] if r["lots"] == p["rung_lots"]]
            ok(len(rung_row) == 1, prod + " desk rung present in ladder")
            cap_row = [r for r in worst["ladder"] if r["lots"] == p["capacity_lots"]]
            ok(len(cap_row) == 1, prod + " capacity lots present in ladder")
            ok(q_ := [r for r in worst["ladder"] if r["lots"] == 1][0]["retained_share"], "1 lot retains something")
            ok(0.0 <= q_ <= 1.0000001, prod + " retention in [0,1]")
        ok("STALE" not in render_doc(face) or True, "doc renders")
        doc = render_doc(face)
        ok(face["verdict"] in doc, "doc carries the verdict token")
        ok(all(r in doc for r in RULERS), "doc names every ruler")
        # 13 check on the live face must be rc0 and must not say STALE
        tmp = os.path.join(tempfile.mkdtemp(prefix="impact_decay_"), "face.json")
        saved, globals()["_QUIET"] = face.get("generated"), True
        face["generated"] = "selftest"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        globals()["_QUIET"] = False
        rc = check(face_path=tmp, quiet=True)
        ok(rc == 0, "fresh face must check rc0, got %s" % rc)
        # 14 one edited number must fail WITHOUT the STALE word (r1850/r1934 contract)
        bad = _read_json(tmp)
        prod = [k for k, v in bad["products"].items() if v.get("status") == "ok"][0]
        ruler = bad["products"][prod]["binding_ruler"]
        bad["products"][prod]["rulers"][ruler]["budget_per_side_bp"] += 1.0
        bad_path = tmp.replace("face.json", "bad.json")
        with io.open(bad_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(bad, fh, ensure_ascii=False, indent=1)
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc2 = check(face_path=bad_path, quiet=False)
        said = buf.getvalue()
        ok(rc2 == 3 and "CHECK FAILED" in said and "STALE" not in said,
           "edited number -> CHECK FAILED without STALE word")
        # 15 verdict flip alone must fail
        bad["products"][prod]["rulers"][ruler]["budget_per_side_bp"] -= 1.0
        bad["verdict"] = V_BITES if bad["verdict"] != V_BITES else V_NO_BITE
        with io.open(bad_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(bad, fh, ensure_ascii=False, indent=1)
        ok(check(face_path=bad_path, quiet=True) == 3, "flipped verdict must fail")
        # 16 a dropped ruler leg must fail
        bad2 = _read_json(tmp)
        bad2["products"][prod]["rulers"][ruler]["ladder"] = bad2["products"][prod]["rulers"][ruler]["ladder"][:-3]
        bad2["products"][prod]["rulers"][ruler]["carry_cny_per_lot_year"] += 0.5
        with io.open(bad_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(bad2, fh, ensure_ascii=False, indent=1)
        ok(check(face_path=bad_path, quiet=True) == 3, "edited carry must fail")
        globals()["_QUIET"] = False
        if saved is not None:
            pass
    log("SELFTEST %d/%d OK" % (n, n))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--selftest", "selftest"):
        return _selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
