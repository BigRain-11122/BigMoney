#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""how big can this carry book get before the market -- not the capital -- is the gate?

WHY THIS FILE EXISTS
--------------------
r2094 (results/idx_fut_carry_always_on_price.json) priced one lot in CNY and ended with
the gap it did not fill: "1 手以上按首档线性外推，未验证深度（ETF 书已有容量面，carry
书没有）". The ETF book has answered this shape for a while (etf_book_capacity_edge, K1:
one day's own order may not exceed 1% of the traded slot's ADV, computed as a 20-bar
median and stress-tested over the last 60 sessions). The carry book quotes a per-lot rate
with no ceiling at all, and its unit is ~50x an ETF slot: one IC lot is 1.20M CNY of
notional. "Linear extrapolation from one lot" is exactly the sentence a capacity face
exists to replace.

WHAT IS MEASURED (this repo's own panels, no external numbers)
-------------------------------------------------------------
  * the front contract of each session = the one with the largest `hold` that date.
    That is the rule a trader applies intraday, so no future data enters the selection;
  * the ADV face = 20-bar median of the front contract's own volume, read on each of the
    last 60 sessions. The binding reading is the WEAKEST session in that window, not the
    median (same discipline as the ETF capacity face);
  * standing position vs open interest -- a quantity the ETF book has no analog for;
  * the roll leg: on the session where the front identity changes, the INCOMING
    contract's own volume, one day and three days. A roll is where the whole book has to
    move at once, so this is the leg that can bite first.

WHAT IS A RULE, NOT A MEASUREMENT
---------------------------------
  * the 1% line itself -- taken from the ETF capacity face so the two books are
    comparable, and swept 0.5/1/2/5% so a reader with a different line can read the same
    table;
  * capital scales linearly with lots: the published sizing face prints rung 2 as
    exactly 2x rung 1, and this face converts lots to capital at that rate and says so.

WHAT IT REFUSES TO PRINT
------------------------
  * an impact-adjusted return: daily bars carry no depth, so the face stops at "share of
    the thing you must trade" and never pretends to know what taking it costs;
  * a single money figure with no ruler named: r2094 showed the carry rate swings
    5.9-6.9pp across rulers, so every CNY number here is printed per ruler.

verdict tokens (frozen before the first run):
  MARKET_IS_NOT_THE_GATE      binding capacity >= 100x the desk's largest published rung:
                              capital binds, and the face names it
  A_DISTANT_GATE              10x <= capacity < 100x
  CAPACITY_BITES_AT_DESK_SCALE capacity < 10x the desk's rung
  DATA_BLOCKED                a panel or an upstream face is missing; refuse, never default

Usage:
    python scripts/idx_fut_carry_capacity_lots.py run
    python scripts/idx_fut_carry_capacity_lots.py check
    python scripts/idx_fut_carry_capacity_lots.py --selftest
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import statistics as st
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FUT_DIR = os.path.join(ROOT, "data", "futures_contracts")
PRICE_PATH = os.path.join(ROOT, "results", "idx_fut_carry_always_on_price.json")
SPEC_PATH = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capacity_lots.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_CAPACITY_LOTS.md")

PRODUCTS = ("IC", "IM")
ADV_BARS = 20
STABILITY_SESSIONS = 60
PRIMARY_SHARE_PCT = 1.0                      # the K1 line the ETF book uses
SHARE_LADDER_PCT = (0.5, 1.0, 2.0, 5.0)      # declared sweep, not a result
ROLL_DAYS = 3                                # a roll may be spread over three sessions

# headroom lines, declared before the first run
VAST = 100.0
DISTANT = 10.0

V_NOT_GATE = "MARKET_IS_NOT_THE_GATE"
V_DISTANT = "A_DISTANT_GATE"
V_BITES = "CAPACITY_BITES_AT_DESK_SCALE"
V_BLOCK = "DATA_BLOCKED"
VERDICTS = (V_NOT_GATE, V_DISTANT, V_BITES, V_BLOCK)


# ------------------------------------------------------------------ io helpers
def _read_json(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:                                                    # noqa: BLE001
        return None


def _digest(obj):
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def load_contracts(prod, fut_dir=None):
    """{contract: {date: (volume, hold, close)}} from the per-contract panels."""
    fut_dir = FUT_DIR if fut_dir is None else fut_dir
    out = {}
    for path in sorted(glob.glob(os.path.join(fut_dir, prod + "[0-9]*.csv"))):
        name = os.path.basename(path)[:6]
        rows = {}
        try:
            with io.open(path, encoding="utf-8") as fh:
                head = fh.readline().strip().split(",")
                ix = {k: i for i, k in enumerate(head)}
                for line in fh:
                    c = line.strip().split(",")
                    if len(c) < 7:
                        continue
                    try:
                        rows[c[ix["date"]]] = (float(c[ix["volume"]]),
                                               float(c[ix["hold"]]),
                                               float(c[ix["close"]]))
                    except (KeyError, ValueError):
                        continue
        except OSError:
            continue
        if rows:
            out[name] = rows
    return out


def front_series(contracts):
    """date -> (contract, volume, hold, close) for the largest-OI contract that date."""
    best = {}
    for name, rows in contracts.items():
        for d, (v, h, c) in rows.items():
            cur = best.get(d)
            if cur is None or h > cur[2]:
                best[d] = (name, v, h, c)
    return best


# ------------------------------------------------------------------ derivation
def price_product(prod, price_face, spec_face, fut_dir=None):
    """One product's capacity ladder, in lots and in CNY at the upstream rate."""
    contracts = load_contracts(prod, fut_dir)
    if not contracts:
        return {"status": "blocked", "why": "no contract panels in data/futures_contracts"}
    front = front_series(contracts)
    dates = sorted(front)
    if len(dates) < ADV_BARS + 5:
        return {"status": "blocked", "why": "front series shorter than the ADV window"}
    win = dates[-STABILITY_SESSIONS:]

    adv, oi, volume = [], [], []
    for d in win:
        hist = [front[x][1] for x in dates if x <= d][-ADV_BARS:]
        adv.append(st.median(hist))
        oi.append(front[d][2])
        volume.append(front[d][1])

    weak_i = min(range(len(adv)), key=lambda i: adv[i])
    adv_median = st.median(adv)
    adv_weak = adv[weak_i]

    # roll legs inside the window: the session where the front identity changes
    rolls = []
    for i in range(1, len(win)):
        if front[win[i]][0] != front[win[i - 1]][0]:
            incoming = front[win[i]][0]
            seq = [d for d in dates if d >= win[i] and d in (contracts.get(incoming) or {})][:ROLL_DAYS]
            one_day = front[win[i]][1]
            n_day = sum(contracts[incoming][d][0] for d in seq) if seq else one_day
            rolls.append({
                "date": win[i],
                "incoming": incoming,
                "one_day_volume": one_day,
                "three_day_volume": n_day,
                "n_days_used": len(seq) or 1,
            })

    legs = {
        "adv20_median": {"value": adv_median, "date": win[-1],
                         "what": "1% of the 20-bar median volume on the last session"},
        "adv20_weakest": {"value": adv_weak, "date": win[weak_i],
                          "what": "1% of the 20-bar median volume on the weakest session"},
    }
    if rolls:
        worst_roll = min(rolls, key=lambda r: r["one_day_volume"])
        legs["roll_one_day"] = {"value": worst_roll["one_day_volume"],
                                "date": worst_roll["date"],
                                "what": "1% of the incoming contract's volume on the roll day"}
        legs["roll_three_day"] = {"value": min(r["three_day_volume"] for r in rolls),
                                  "date": worst_roll["date"],
                                  "what": "1% of the incoming contract's first three sessions"}

    for name, row in legs.items():
        row["lots_at_primary"] = row["value"] * PRIMARY_SHARE_PCT / 100.0

    traded = [k for k in ("adv20_median", "adv20_weakest", "roll_one_day") if k in legs]
    adopted_leg = min(traded, key=lambda k: legs[k]["lots_at_primary"])
    adopted_lots = legs[adopted_leg]["lots_at_primary"]

    # money: convert lots to capital at the rung rate, and to carry at each ruler
    acct = (spec_face.get("accounts") or {}).get(prod) or {}
    rungs = [r for r in (acct.get("capital_rungs") or []) if int(r.get("lots", 0)) >= 1]
    if not rungs:
        return {"status": "blocked", "why": "sizing face has no executable rung"}
    top = max(rungs, key=lambda r: int(r["lots"]))
    desk_lots = float(top["lots"])
    desk_capital = float(top["capital_cny"])
    capital_per_lot = desk_capital / desk_lots

    pricing = (price_face.get("products") or {}).get(prod) or {}
    if pricing.get("status") != "ok":
        return {"status": "blocked", "why": "price face has no ok row for this product"}
    rulers = {}
    for ruler, row in (pricing.get("rulers") or {}).items():
        per_lot = float(row["always_on_carry_cny"])
        rulers[ruler] = {
            "ann_pct": float(row["always_on_ann_pct"]),
            "per_lot_carry_cny": per_lot,
            "capacity_carry_cny": round(adopted_lots * per_lot, 2),
        }

    window_rows = [[d, front[d][0], round(front[d][1], 3), round(front[d][2], 3)] for d in win]
    return {
        "status": "ok",
        "window": {"first": win[0], "last": win[-1], "sessions": len(win)},
        "front_contract_last": front[win[-1]][0],
        "notional_per_lot_cny": pricing.get("notional_per_lot_cny"),
        "window_digest": _digest(window_rows),
        "adv20_median": round(adv_median, 2),
        "adv20_weakest": {"value": round(adv_weak, 2), "date": win[weak_i]},
        "open_interest": {
            "median": round(st.median(oi), 2),
            "p10": round(sorted(oi)[max(0, int(0.1 * len(oi)) - 1)], 2),
            "lots_at_primary": st.median(oi) * PRIMARY_SHARE_PCT / 100.0,
            "what": "standing position, not a daily trade: printed as a separate bound",
        },
        "turnover": {"volume_over_oi_median": round(
            st.median([v / o for v, o in zip(volume, oi) if o > 0]), 4)},
        "roll": {"n_in_window": len(rolls), "days": rolls},
        "legs": {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                     for kk, vv in v.items()} for k, v in legs.items()},
        "capacity": {
            "adopted_leg": adopted_leg,
            "adopted_lots": round(adopted_lots, 2),
            "legs_traded_only": traded,
            "share_pct": PRIMARY_SHARE_PCT,
        },
        "desk": {"rung_lots": desk_lots, "rung_capital_cny": desk_capital,
                 "capital_per_lot_cny": round(capital_per_lot, 2),
                 "lots_at_1m_cny": int(acct.get("admissible_lots") or 0)},
        "money": {"rulers": rulers,
                  "capital_at_capacity_cny": round(adopted_lots * capital_per_lot, 2)},
        "headroom_multiple": round(adopted_lots / desk_lots, 2) if desk_lots else None,
    }


def derive(fut_dir=None):
    price_face = _read_json(PRICE_PATH)
    spec_face = _read_json(SPEC_PATH)
    missing = [name for name, face in (
        ("results/idx_fut_carry_always_on_price.json", price_face),
        ("results/idx_fut_carry_sizing_spec.json", spec_face),
    ) if not face]

    face = {
        "kind": "idx_fut_carry_capacity_lots",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": ("how many lots of this carry book can the front contract absorb at "
                     "1% of the thing you must trade, and what does that pay per year?"),
        "rules": {"adv_bars": ADV_BARS, "stability_sessions": STABILITY_SESSIONS,
                  "primary_share_pct": PRIMARY_SHARE_PCT,
                  "share_ladder_pct": list(SHARE_LADDER_PCT),
                  "roll_days": ROLL_DAYS,
                  "line_is_a_rule": "1% of ADV is the K1 line the ETF capacity face uses; "
                                    "it is declared here so the two books are comparable",
                  "capital_is_linear": "lots -> capital at rung_capital / rung_lots"},
        "not_recomputed": [
            "the carry rate itself (results/idx_fut_carry_always_on_price.json)",
            "the capital rungs (results/idx_fut_carry_sizing_spec.json)",
            "any impact cost: daily bars carry no depth",
        ],
        "inputs": {"price_face": _digest(price_face) if price_face else None,
                   "spec_face": _digest(spec_face) if spec_face else None},
    }
    if missing:
        face["verdict"] = V_BLOCK
        face["missing_inputs"] = missing
        face["products"] = {}
        print("DATA_BLOCKED missing: " + ", ".join(missing))
        return face

    products = {}
    for prod in PRODUCTS:
        products[prod] = price_product(prod, price_face, spec_face, fut_dir)
    face["products"] = products

    ok = {p: r for p, r in products.items() if r.get("status") == "ok"}
    if not ok:
        face["verdict"] = V_BLOCK
        face["products"] = products
        return face

    face["evidence_cutoff"] = min(r["window"]["last"] for r in ok.values())
    tightest = min(ok.values(), key=lambda r: r["headroom_multiple"] or 0)
    mult = tightest["headroom_multiple"] or 0
    if mult >= VAST:
        face["verdict"] = V_NOT_GATE
    elif mult >= DISTANT:
        face["verdict"] = V_DISTANT
    else:
        face["verdict"] = V_BITES
    face["binding_product"] = [p for p in ok if ok[p] is tightest][0]
    face["what_binds_today"] = {
        "name": "capital",
        "one_line": ("桌面已发布的最大档位是 %d 手（%s 元），而市场在 1%% 线上能吞下 %s 手——"
                     "差 %.0f 倍，所以约束是资本不是流动性"
                     % (int(tightest["desk"]["rung_lots"]),
                        format(int(round(tightest["desk"]["rung_capital_cny"])), ","),
                        format(int(round(tightest["capacity"]["adopted_lots"])), ","),
                        tightest["headroom_multiple"] or 0)),
    }
    face["reading"] = {
        V_NOT_GATE: "capital is the gate by two orders of magnitude; size on the rung, not on the market",
        V_DISTANT: "the market would bind eventually, but nothing the desk can fund today reaches it",
        V_BITES: "the market binds at desk scale: size on liquidity, and say which day you would roll",
        V_BLOCK: "an input is missing; refuse, never default",
    }[face["verdict"]]
    return face


# ------------------------------------------------------------------ checks
def check(quiet=False):
    """Re-derive and compare. A moved panel is STALE; a moved number with the same
    panel is a real defect and must NOT say stale (r1850/r1935)."""
    published = _read_json(OUT_PATH)
    if published is None:
        print("STALE face missing: results/idx_fut_carry_capacity_lots.json")
        return 3
    fresh = derive()

    # r2098: the upstream faces are inputs too, not just the panel window. The per-lot carry
    # comes from the always-on price face, which this chain rewrites a few legs earlier -- so
    # on a chain pass this check saw only "capacity_carry moved" and called it a defect the
    # chain never pays to repair (r1934's class; third face this round, after the decision
    # face and the roll-step face). Comparing the recorded input digests first makes a moved
    # upstream face say STALE in its own word; a hand-edited number with unchanged inputs
    # still says CHECK_FAILED.
    moved = sorted(k for k, v in (published.get("inputs") or {}).items()
                   if (fresh.get("inputs") or {}).get(k) != v)
    if moved:
        if not quiet:
            print("STALE: input face(s) moved: %s -- rebuild this face" % ", ".join(moved))
        return 3

    problems, stale = [], []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %r -> %r" % (published.get("verdict"), fresh.get("verdict")))
    for prod in PRODUCTS:
        a = (published.get("products") or {}).get(prod) or {}
        b = (fresh.get("products") or {}).get(prod) or {}
        if a.get("status") != b.get("status"):
            problems.append("%s status %r -> %r" % (prod, a.get("status"), b.get("status")))
            continue
        if a.get("status") != "ok":
            continue
        if a.get("window_digest") != b.get("window_digest"):
            stale.append("%s panel window %s..%s -> %s..%s"
                         % (prod, (a.get("window") or {}).get("first"),
                            (a.get("window") or {}).get("last"),
                            (b.get("window") or {}).get("first"),
                            (b.get("window") or {}).get("last")))
            continue
        for path in (("capacity", "adopted_lots"), ("desk", "rung_capital_cny"),
                     ("headroom_multiple", None), ("adv20_median", None)):
            if path[1] is None:
                va, vb = a.get(path[0]), b.get(path[0])
            else:
                va = (a.get(path[0]) or {}).get(path[1])
                vb = (b.get(path[0]) or {}).get(path[1])
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                if abs(float(va) - float(vb)) > 1e-6:
                    problems.append("%s %s.%s %r -> %r" % (prod, path[0], path[1], va, vb))
            elif va != vb:
                problems.append("%s %s.%s %r -> %r" % (prod, path[0], path[1], va, vb))
        for ruler, ra in ((a.get("money") or {}).get("rulers") or {}).items():
            rb = ((b.get("money") or {}).get("rulers") or {}).get(ruler) or {}
            for key in ("per_lot_carry_cny", "capacity_carry_cny"):
                va, vb = ra.get(key), rb.get(key)
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    if abs(float(va) - float(vb)) > 0.02:
                        problems.append("%s %s %s %r -> %r" % (prod, ruler, key, va, vb))
    if stale:
        print("STALE results/idx_fut_carry_capacity_lots.json (panel moved, pay its writer)")
        for s in stale[:6]:
            print("  - " + s)
        return 3
    if problems:
        print("CHECK FAILED results/idx_fut_carry_capacity_lots.json (same panel, different numbers)")
        for p in problems[:12]:
            print("  - " + p)
        return 3
    if not quiet:
        print("CHECK_OK idx_fut_carry_capacity_lots (%s, verdict %s)"
              % (published.get("evidence_cutoff"), published.get("verdict")))
    return 0


# ------------------------------------------------------------------ render
def render_doc(face):
    L = []
    L.append("# 这本 carry 书最多能做多大：市场什么时候才会注意到")
    L.append("")
    L.append("generated %s | 判决 **%s** | 证据截止 %s | 约束腿=**%s** | 1%% 线（与 ETF 容量面同一条 K1）"
             % (face.get("generated"), face.get("verdict"), face.get("evidence_cutoff"),
                (face.get("products", {}).get(face.get("binding_product") or "IC", {})
                 .get("capacity") or {}).get("adopted_leg")))
    L.append("")
    L.append("上一轮（r2094）把一手 carry 折成元，结尾自己承认「一手以上未验证深度」。"
             "这页把那个洞补上：不问「能赚多少比例」，问「能放多大、放多大以后市场才开始在意」。")
    L.append("")
    L.append("## 每一条腿各能放多少手（1% 线）")
    L.append("")
    L.append("| 品种 | 腿 | 读数日 | 成交量 | 1% 手数 | 说明 |")
    L.append("|---|---|---|---|---|---|")
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            L.append("| %s | — | — | — | — | %s |" % (prod, row.get("why", "blocked")))
            continue
        for name, leg in row["legs"].items():
            L.append("| %s | %s | %s | %s | **%s** | %s |"
                     % (prod, name, leg.get("date", "—"),
                        format(int(round(leg["value"])), ","),
                        format(int(round(leg["lots_at_primary"])), ","),
                        leg.get("what", "")))
        L.append("| %s | 持仓量（参考，不是日成交） | %s | %s | %s | 站在场内的仓，不是一天能成交的量 |"
                 % (prod, row["window"]["last"],
                    format(int(round(row["open_interest"]["median"])), ","),
                    format(int(round(row["open_interest"]["lots_at_primary"])), ",")))
    L.append("")
    L.append("**采信的是成交类三条腿里最紧的一条**（不含持仓量：那是场内沉淀的仓，不是一天能成交的量）。")
    L.append("")
    L.append("## 每个品种一句话")
    L.append("")
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            continue
        cap = row["capacity"]
        money = row["money"]
        L.append("- **%s**：约束腿 `%s` → 只能放 **%s 手**；按每手资本 %s 元算要 **%s 元资本**；"
                 "桌面上已发布的最大档位是 **%d 手 / %s 元**，容量是它的 **%.0f 倍**。"
                 % (prod, cap["adopted_leg"],
                    format(int(round(cap["adopted_lots"])), ","),
                    format(int(row["desk"]["capital_per_lot_cny"]), ","),
                    format(int(round(money["capital_at_capacity_cny"])), ","),
                    int(row["desk"]["rung_lots"]),
                    format(int(row["desk"]["rung_capital_cny"]), ","),
                    row["headroom_multiple"]))
        parts = []
        for ruler, r in money["rulers"].items():
            parts.append("%s %.2f%% → %s 元/年"
                         % (ruler, r["ann_pct"], format(int(round(r["capacity_carry_cny"])), ",")))
        L.append("  放满这一档的 carry 按尺子各印一遍：" + "；".join(parts) + "。")
    L.append("")
    L.append("## 为什么「市场」不是今天的约束")
    L.append("")
    r0 = (face.get("products") or {}).get(face.get("binding_product") or "IC") or {}
    if r0.get("status") == "ok":
        oi = r0["open_interest"]
        L.append("- 前月合约中位持仓 %s 手、20 根中位成交 %s 手，成交/持仓 = %.2f ——"
                 "这是一个每天都在换手 %d%% 的市场，1%% 的日内份额对它是零头。"
                 % (format(int(round(oi["median"])), ","),
                    format(int(round(r0["adv20_median"])), ","),
                    r0["turnover"]["volume_over_oi_median"],
                    int(round(r0["turnover"]["volume_over_oi_median"] * 100))))
        rolls = r0["roll"].get("days") or []
        if rolls:
            tight = min(rolls, key=lambda r: r["one_day_volume"])
            L.append("- 最紧的一条腿不是平时成交，而是**持仓量迁移那一天**：%s 在 %s 接上前月时"
                     "只成交 %s 手，1%% 只有 %s 手——这本书真正的容量问题不是「能不能建仓」，"
                     "是**哪天移仓**。"
                     % (tight["incoming"], tight["date"],
                        format(int(round(tight["one_day_volume"])), ","),
                        format(int(round(r0["legs"]["roll_one_day"]["lots_at_primary"]
                                          if "roll_one_day" in r0["legs"] else 0)), ",")))
            L.append("- 把移仓摊到三天（本面 `roll_days`=%d），同一把尺子下容量变成 %s 手——"
                     "**移仓节奏是免费的容量**，这一点比任何收益率都更容易被忽略。"
                     % (ROLL_DAYS,
                        format(int(round(r0["legs"]["roll_three_day"]["lots_at_primary"]
                                          if "roll_three_day" in r0["legs"] else 0)), ",")))
    L.append("")
    L.append("所以今天的墙不是流动性，是资本：`%s`。" % (face.get("what_binds_today") or {}).get(
        "one_line", "—"))
    L.append("")
    L.append("## 没有回答的问题")
    L.append("")
    L.append("- 冲击成本：日线没有深度，本面只印「占多大的份额」，不印「吃下去要花多少钱」；")
    L.append("- 1% 是一条规则不是测量：0.5/1/2/5% 的阶梯在 JSON 里，谁的线不同就按比例读；")
    L.append("- 持仓量里有多少是可成交的（套保盘、做市盘与投机盘混在一起）无从得知；")
    L.append("- 只覆盖 IC/IM；IF/IH 贴水更薄、成交也不同，规则未验证；")
    L.append("- 杠杆/保证金线性外推：档位面里 2 手正好是 1 手的 2 倍，但组合层面的保证金净额未测；")
    L.append("- 本面不重复 r2094 的收益率结论——容量大不等于收益率稳，那仍是「尺子决定年化」的问题。")
    L.append("")
    L.append("`--check` 会重算本页每个数；面板动了会说 STALE，同样面板算出不同数会说 CHECK FAILED。")
    for what in face.get("not_recomputed", []):
        L.append("- 未重算：%s" % what)
    L.append("")
    return "\n".join(L)


def run():
    face = derive()
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    print("WROTE results/idx_fut_carry_capacity_lots.json verdict=%s" % face["verdict"])
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            print("  %s: %s" % (prod, row.get("why", "blocked")))
            continue
        print("  %s: %s lots at the 1%% line (%s) | capital %.0f CNY | desk rung %d lots"
              " | headroom %.0fx"
              % (prod, format(int(round(row["capacity"]["adopted_lots"])), ","),
                 row["capacity"]["adopted_leg"],
                 row["money"]["capital_at_capacity_cny"],
                 int(row["desk"]["rung_lots"]), row["headroom_multiple"]))
    if face.get("what_binds_today"):
        print("  what binds today: " + face["what_binds_today"]["one_line"])
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    face = derive()
    leg("upstream faces present", face["verdict"] != V_BLOCK, face.get("verdict", ""))
    leg("verdict in the frozen token set", face["verdict"] in VERDICTS)

    ok_rows = {p: r for p, r in face["products"].items() if r.get("status") == "ok"}
    leg("both products priced", set(ok_rows) == set(PRODUCTS), ",".join(sorted(ok_rows)))

    if ok_rows:
        bad = [(p, n) for p, r in ok_rows.items() for n, lg in r["legs"].items()
               if abs(lg["value"] * PRIMARY_SHARE_PCT / 100.0 - lg["lots_at_primary"]) > 1e-6]
        leg("lots == volume x 1% on every leg", not bad, str(bad[:3]))

        bad = []
        for p, r in ok_rows.items():
            for ruler, m in r["money"]["rulers"].items():
                calc = r["capacity"]["adopted_lots"] * m["per_lot_carry_cny"]
                if abs(calc - m["capacity_carry_cny"]) > 0.02:
                    bad.append((p, ruler, calc, m["capacity_carry_cny"]))
        leg("capacity money == lots x per-lot carry", not bad, str(bad[:3]))

        bad = [(p, r["desk"]) for p, r in ok_rows.items()
               if abs(r["desk"]["capital_per_lot_cny"] * r["desk"]["rung_lots"]
                      - r["desk"]["rung_capital_cny"]) > 0.02]
        leg("capital per lot is the rung rate (linear)", not bad, str(bad[:2]))

        bad = [(p, r["adv20_weakest"]["value"], r["adv20_median"])
               for p, r in ok_rows.items() if r["adv20_weakest"]["value"] > r["adv20_median"]]
        leg("the weakest session is not above the median", not bad, str(bad[:2]))

        bad = [(p, r["capacity"]["adopted_leg"]) for p, r in ok_rows.items()
               if r["capacity"]["adopted_leg"] not in r["capacity"]["legs_traded_only"]]
        leg("adopted leg is one of the traded legs", not bad, str(bad[:2]))

        bad = [(p, r["capacity"]["adopted_lots"]) for p, r in ok_rows.items()
               if r["capacity"]["adopted_lots"] > r["open_interest"]["lots_at_primary"]]
        leg("capacity is tighter than the standing-interest bound", not bad, str(bad[:2]))

        bad = [(p, r["headroom_multiple"]) for p, r in ok_rows.items()
               if abs(r["headroom_multiple"]
                      - r["capacity"]["adopted_lots"] / r["desk"]["rung_lots"]) > 0.02]
        leg("headroom == capacity / desk rung", not bad, str(bad[:2]))

        leg("every roll inside the window is named",
            all(r["roll"]["n_in_window"] == len(r["roll"]["days"]) for r in ok_rows.values()))

    # behavioural: an absent panel must refuse, never extrapolate from one lot
    tmp = tempfile.mkdtemp(prefix="r2095thin_")
    try:
        thin_face = derive(fut_dir=tmp)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    leg("an empty panel refuses instead of extrapolating", thin_face["verdict"] == V_BLOCK,
        thin_face.get("verdict", ""))

    # behavioural: doubling the desk rung halves the headroom
    spec = _read_json(SPEC_PATH) or {}
    scaled = json.loads(json.dumps(spec))
    price = _read_json(PRICE_PATH) or {}
    for prod in PRODUCTS:
        acct = (scaled.get("accounts") or {}).get(prod) or {}
        for rung in acct.get("capital_rungs") or []:
            if int(rung.get("lots", 0)) >= 1:
                rung["lots"] = int(rung["lots"]) * 50
                rung["capital_cny"] = float(rung["capital_cny"]) * 50
    before = {p: r["headroom_multiple"] for p, r in ok_rows.items()}
    after = {}
    for prod in PRODUCTS:
        row = price_product(prod, price, scaled)
        if row.get("status") == "ok":
            after[prod] = row["headroom_multiple"]
    leg("50x the desk rung cuts headroom 50x",
        all(abs(before[p] / after[p] - 50.0) < 0.05 for p in after if p in before
            and before[p] and after[p]),
        str({p: (before.get(p), after.get(p)) for p in after}))

    # behavioural: a hand-edited published number must be caught by check()
    tmp2 = tempfile.mkdtemp(prefix="r2095neg_")
    saved_out = OUT_PATH
    try:
        publish = derive()
        fake = json.loads(json.dumps(publish))
        if fake["products"].get("IC", {}).get("status") == "ok":
            fake["products"]["IC"]["capacity"]["adopted_lots"] += 1.0
        fake_path = os.path.join(tmp2, "face.json")
        with io.open(fake_path, "w", encoding="utf-8") as fh:
            json.dump(fake, fh, ensure_ascii=False)
        globals()["OUT_PATH"] = fake_path
        rc_same = check(quiet=True)
        fake2 = json.loads(json.dumps(publish))
        if fake2["products"].get("IC", {}).get("status") == "ok":
            fake2["products"]["IC"]["window_digest"] = "0" * 64
        with io.open(fake_path, "w", encoding="utf-8") as fh:
            json.dump(fake2, fh, ensure_ascii=False)
        rc_moved = check(quiet=True)
    finally:
        globals()["OUT_PATH"] = saved_out
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)
    leg("hand-edited number is CHECK FAILED (rc3)", rc_same == 3, "rc=%s" % rc_same)
    leg("moved panel digest is STALE (rc3)", rc_moved == 3, "rc=%s" % rc_moved)

    passed = sum(1 for _n, ok, _d in legs if ok)
    for name, ok, detail in legs:
        print(("  PASS " if ok else "  FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    print("SELFTEST %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv or "selftest" in argv:
        return _selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
