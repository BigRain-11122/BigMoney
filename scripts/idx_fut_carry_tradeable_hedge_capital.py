#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""What the four-arm book costs to open when the hedge is something you can actually buy

WHY THIS FILE EXISTS
--------------------
results/idx_fut_carry_portfolio_capital.json published a floor and then named this file's
job in its own `next_work` field:

    "Give IF and IH the same capital line the hedged arms have (per-lot vol at the 8%
     target): only then can the four-arm opening cost be stated instead of floored."

Filling in two numbers is not the interesting half.  The capital line the whole sleeve is
sized on is `ann_vol_per_lot_hedged`, and that arm's residual is measured against the arm's
**own index** (idx_fut_carry_paper.per_lot_daily: futures points minus index points on the
same notional).  In an A-share account you cannot short an index.  What you can do is

    (a) short another index's future  -> tradable today, leaves the index spread standing,
    (b) 融券 borrow the tracking ETF   -> exists, financing fee not modelled anywhere in
                                          this repo, so this face names it and does not price it.

So there are three opening costs for the same four arms, and only two of them are buyable:

    reference   hedge = own index        -> the published ruler, not tradable
    executable  hedge = another future   -> tradable, priced here from measured prices
    borrowed    hedge = 融券 the ETF      -> named, unpriced (no in-house fee series)

This file prices the first two for all four arms, with the reference arms of IC/IM required
to reproduce the published per-lot vol and capital line before any number is printed.

WHY IT IS NOT JUST A WIDER TABLE
--------------------------------
The two rulers that pick a hedge disagree.  The published ruler picks the **cheapest carry**
short leg; the capital line picks the **smallest residual vol**.  For IC those are different
contracts, and the disagreement has a price on both sides.  A reader who is told only
"net carry after the cheapest hedge" is being told about a hedge whose residual is 2.0x the
reference vol; a reader told only the vol-cheapest is being told about a hedge whose carry
cost is 7.0pp instead of 0.6pp.  Both are printed here, side by side, per arm.

WHAT THIS FILE DOES NOT DO
--------------------------
  * no return series is rebuilt: per-lot vol comes from the parent's own `per_lot_daily`,
    and the reference arms of IC/IM must reproduce results/idx_fut_carry_paper/SIZING.json
    to the cent before this file publishes anything (`REFUSE` otherwise);
  * no financing fee, no 融券 availability, no margin: the capital line is the same
    vol-budget ruler the published face uses (capital = per-lot vol / 8%), not an account
    funding requirement; the hedge leg's margin is named as excluded;
  * the residual of a cross-index hedge is a *position* (the index spread), not noise: its
    measured one-year P&L is printed so nobody mistakes "hedged" for "flat".
"""
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_basis as BASE  # noqa: E402  product->index map, index panel reader
import idx_fut_carry_paper as PAP  # noqa: E402  roll path + per-lot residual, imported

OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_tradeable_hedge_capital.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_TRADEABLE_HEDGE_CAPITAL.md")

SIZING_PATH = os.path.join(ROOT, "results", "idx_fut_carry_paper", "SIZING.json")
FLOOR_PATH = os.path.join(ROOT, "results", "idx_fut_carry_portfolio_capital.json")
DESK_PATH = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
PRODUCTS = ("IF", "IH", "IC", "IM")
TARGET_PCT = 8.0         # the book's risk dial, read from the published sizing face
WINDOW_YEARS = 1.0       # the parent's REPLAY_YEARS: the published per-lot vol window
RATIO_TOL = 1e-6
DOC_BEGIN = "<!-- BEGIN:TRADEABLE-HEDGE-CAPITAL -->"
DOC_END = "<!-- END:TRADEABLE-HEDGE-CAPITAL -->"


# ------------------------------------------------------------------ io helpers
def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_paths():
    paths = [SIZING_PATH, FLOOR_PATH, DESK_PATH]
    for p in PRODUCTS:
        paths.append(os.path.join(BASE.FUT_DIR, p + ".csv"))
        pair = BASE.PAIRS.get(p)
        if pair:
            paths.append(os.path.join(BASE.IDX_DIR, pair[0] + ".csv"))
    return paths


def input_digests():
    out = {}
    for p in input_paths():
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        out[rel] = sha256_file(p)
    return out


# --------------------------------------------------------------- arithmetic
def ann_vol_cny(points, mult):
    """Annualised P&L vol of one lot, in CNY.  A short series is absent, not small."""
    if not points or len(points) < 20:
        return None
    return statistics.stdev(points) * float(mult) * math.sqrt(252.0)


def capital_for_one_lot(sigma_cny, target_pct=TARGET_PCT):
    if not sigma_cny or sigma_cny <= 0 or not target_pct:
        return None
    return sigma_cny / (target_pct / 100.0)


def beta_no_intercept(xs, ys):
    """Hedge lots of the short leg per one long lot.

    No intercept: this is a scaling choice, not a forecast.  An intercept would absorb the
    average carry into the hedge and report a residual whose mean is zero by construction --
    that would hide exactly the number a reader needs (what the carry becomes).
    """
    sxx = sum(x * x for x in xs)
    if sxx <= 0:
        return None
    return sum(x * y for x, y in zip(xs, ys)) / sxx


def residual(xs, ys, beta):
    return [y - beta * x for x, y in zip(xs, ys)]


# ------------------------------------------------------------ arm series
def dated_pnl(prod, years=WINDOW_YEARS):
    """[(date, pnl_cny, notional_cny)] for one lot of `prod`, the parent's seam rule.

    The roll logic itself is the parent's (`position_series`); only the date label is new,
    because `per_lot_daily` returns points without days.  `verify_against_parent` below
    asserts this walk reproduces the parent's own point series element by element -- a
    second implementation that drifts is worse than no second implementation.
    """
    rows, _rolls = PAP.position_series(prod)
    if not rows:
        return None, "NO_FUTURES_PANEL"
    cutoff = rows[-1][0]
    want = str(int(cutoff[:4]) - int(years)) + cutoff[4:]
    start = next((k for k, r in enumerate(rows) if r[0] >= want), 0)
    held = rows[start][1]
    prev = rows[start][2]
    mult = MULTIPLIER[prod]
    out = []
    for d, sym, px, old_px in rows[start + 1:]:
        if px is None:
            continue
        if sym != held:
            if old_px is None:
                fut = 0.0
                notional = prev if prev is not None else px
            else:
                fut = (old_px - prev) if prev is not None else 0.0
                notional = old_px
            held, prev = sym, px
        else:
            fut = (px - prev) if prev is not None else 0.0
            notional = prev if prev is not None else px
            prev = px
        out.append((d, fut * mult, notional * mult))
    return out, "ok"


def verify_against_parent(prod, dated):
    """The dated walk must reproduce the parent's undated point series exactly."""
    rows, _ = PAP.position_series(prod)
    idx = BASE.load_index(BASE.PAIRS[prod][0])
    parent = PAP.per_lot_daily(rows, idx, years=WINDOW_YEARS)
    if not parent:
        return False, "parent returned nothing"
    pts = parent.get("fut_points") or []
    mine = [round(p[1] / MULTIPLIER[prod], 10) for p in dated]
    if len(mine) != len(pts):
        return False, "length %d vs parent %d" % (len(mine), len(pts))
    worst = max((abs(a - b) for a, b in zip(mine, pts)), default=0.0)
    return worst <= 1e-8, "max |diff| = %.3e" % worst


def reference_arm(prod):
    """The published arm: one lot hedged with its own index (parent's definition, reused)."""
    rows, _ = PAP.position_series(prod)
    if not rows:
        return {"state": "NO_FUTURES_PANEL"}
    idx = BASE.load_index(BASE.PAIRS[prod][0])
    d = PAP.per_lot_daily(rows, idx, years=WINDOW_YEARS)
    if not d:
        return {"state": "NO_PANEL"}
    sigma = ann_vol_cny(d["excess_points"], MULTIPLIER[prod])
    if sigma is None:
        return {"state": "NOT_ENOUGH_BARS", "days": d.get("days")}
    return {
        "state": "ok",
        "window": d["window"],
        "days": d["days"],
        "forced_rolls": d["forced_rolls"],
        "sigma_cny": round(sigma, 2),
        "capital_cny": round(capital_for_one_lot(sigma), 2),
        "hedge": "own index %s (not tradable: no short exists for an index itself)" % BASE.PAIRS[prod][0],
    }


def cross_arm(prod, hedge, series, desk):
    """One tradable hedge: beta, residual vol, capital line, and what the carry becomes."""
    a = series.get(prod)
    b = series.get(hedge)
    if not a or not b:
        return {"state": "NO_SERIES"}
    da = {x[0]: x for x in a}
    db = {x[0]: x for x in b}
    common = sorted(set(da) & set(db))
    if len(common) < 60:
        return {"state": "NOT_ENOUGH_OVERLAP", "days": len(common)}
    xs = [db[d][1] for d in common]   # short leg P&L, one lot of hedge
    ys = [da[d][1] for d in common]   # long leg P&L, one lot of the arm
    beta = beta_no_intercept(xs, ys)
    if beta is None:
        return {"state": "ZERO_VARIANCE_HEDGE"}
    res = residual(xs, ys, beta)
    sigma = ann_vol_cny([r / MULTIPLIER[prod] for r in res], MULTIPLIER[prod])
    if sigma is None:
        return {"state": "NOT_ENOUGH_BARS"}
    h_int = int(round(beta)) or 1
    res_int = residual(xs, ys, h_int)
    sigma_int = ann_vol_cny([r / MULTIPLIER[prod] for r in res_int], MULTIPLIER[prod])
    carry = (desk.get(hedge) or {}).get("gap_after_roll_cost_pp") or {}
    cost = carry.get("measured_median")
    own = (desk.get(prod) or {}).get("gap_after_roll_cost_pp") or {}
    own_carry = own.get("measured_median")
    net = None if (cost is None or own_carry is None) else float(own_carry) - float(cost)
    notional = statistics.median([x[2] for x in a])
    return {
        "state": "ok",
        "days": len(common),
        "beta_lots_per_long_lot": round(beta, 4),
        "sigma_cny": round(sigma, 2),
        "capital_cny": round(capital_for_one_lot(sigma), 2),
        "integer_hedge": {
            "lots": h_int,
            "sigma_cny": None if sigma_int is None else round(sigma_int, 2),
            "capital_cny": None if sigma_int is None else round(capital_for_one_lot(sigma_int), 2),
        },
        "hedge_carry_pp": None if cost is None else round(float(cost), 3),
        "long_carry_pp": None if own_carry is None else round(float(own_carry), 3),
        "net_carry_pp": None if net is None else round(net, 3),
        "residual_pnl_one_year_cny": round(sum(res) / (WINDOW_YEARS or 1.0), 2),
        "residual_pnl_pct_of_notional": round(sum(res) / (WINDOW_YEARS or 1.0) / notional * 100.0, 3)
        if notional else None,
    }


def carry_verdict(row):
    if row.get("state") != "ok":
        return row.get("state")
    if row.get("net_carry_pp") is None:
        return "HEDGE_CARRY_UNPRICED"
    if row["net_carry_pp"] <= 0:
        return "HEDGE_GIVES_THE_SLEEVE_AWAY"
    return "HEDGE_KEEPS_THE_CARRY"


def pick(pairs, key, keep_carry_only=False):
    usable = [(k, v) for k, v in pairs.items() if v.get("state") == "ok"]
    if key == "capital":
        usable = [(k, v) for k, v in usable if v.get("capital_cny")]
        if keep_carry_only:
            usable = [(k, v) for k, v in usable
                      if v.get("net_carry_pp") is not None and v["net_carry_pp"] > 0]
        if not usable:
            return None
        return min(usable, key=lambda kv: (kv[1]["capital_cny"], kv[0]))[0]
    usable = [(k, v) for k, v in usable if v.get("hedge_carry_pp") is not None]
    if not usable:
        return None
    return min(usable, key=lambda kv: (kv[1]["hedge_carry_pp"], kv[0]))[0]


def arm_status(pairs):
    """Whether this arm still is a carry arm once the hedge is something you can buy."""
    ok = [v for v in pairs.values() if v.get("state") == "ok"]
    if not ok:
        return "ARM_NOT_MEASURABLE"
    priced = [v for v in ok if v.get("net_carry_pp") is not None]
    if not priced:
        return "HEDGE_CARRY_UNPRICED"
    if not any(v["net_carry_pp"] > 0 for v in priced):
        return "HEDGE_GIVES_THE_SLEEVE_AWAY"
    return "HEDGE_KEEPS_THE_CARRY"


# ------------------------------------------------------------------- build
def build():
    sizing = load_json(SIZING_PATH) or {}
    floor = load_json(FLOOR_PATH) or {}
    desk = (load_json(DESK_PATH) or {}).get("rows") or {}

    series, series_state = {}, {}
    for p in PRODUCTS:
        dated, state = dated_pnl(p)
        series_state[p] = state
        if state == "ok":
            series[p] = dated
            ok, why = verify_against_parent(p, dated)
            series_state[p] = ("ok" if ok else "PARENT_MISMATCH:" + why)

    accounts = {}
    for p in PRODUCTS:
        ref = reference_arm(p)
        pairs = {}
        if ref.get("state") == "ok":
            for q in PRODUCTS:
                if q == p:
                    continue
                row = cross_arm(p, q, series, desk)
                pairs[q] = row
        by_carry = pick(pairs, "carry")
        by_capital = pick(pairs, "capital")
        by_capital_keep = pick(pairs, "capital", keep_carry_only=True)
        acct = {
            "reference": ref,
            "tradeable": pairs,
            "pick_by_carry": by_carry,
            "pick_by_capital": by_capital,
            "pick_by_capital_keeping_carry": by_capital_keep,
            "series_state": series_state.get(p),
        }
        if ref.get("state") != "ok":
            acct["verdict"] = "ARM_NOT_MEASURABLE"
        else:
            acct["verdict"] = arm_status(pairs)
            acct["rulers_disagree"] = bool(by_carry and by_capital and by_carry != by_capital)
        accounts[p] = acct

    # ---- reference gate: IC/IM must reproduce the published per-lot vol and capital line
    pubs = (sizing.get("accounts") or {})
    gates, problems = {}, []
    for p in PRODUCTS:
        ref = accounts[p]["reference"]
        pub = (pubs.get(p) or {}).get("hedged") or {}
        if pub and ref.get("state") == "ok":
            d_sig = abs(ref["sigma_cny"] - float(pub["ann_vol_per_lot_cny"]))
            d_cap = abs(ref["capital_cny"] - float(pub["capital_for_one_lot_at_target"]))
            gates["%s_reference_sigma_matches_published" % p] = d_sig <= 0.5
            gates["%s_reference_capital_matches_published" % p] = d_cap <= 0.5
            if d_sig > 0.5 or d_cap > 0.5:
                problems.append("%s reference arm differs from published: d_sigma=%.2f d_capital=%.2f"
                                % (p, d_sig, d_cap))
    two_arm = sum(accounts[p]["reference"].get("capital_cny") or 0 for p in ("IC", "IM"))
    pub_floor = floor.get("floor_to_open_measured_arms_cny")
    gates["published_two_arm_floor_reproduced"] = bool(
        pub_floor and abs(two_arm - float(pub_floor)) <= 1.0)
    if not gates["published_two_arm_floor_reproduced"]:
        problems.append("two-arm floor %.2f vs published %.2f" % (two_arm, float(pub_floor or 0)))

    four_ref = sum(accounts[p]["reference"].get("capital_cny") or 0 for p in PRODUCTS
                   if accounts[p]["reference"].get("state") == "ok")

    # ---- the three opening costs
    pick_cap_total, pick_cap_rows = 0.0, {}
    for p in PRODUCTS:
        acct = accounts[p]
        q = acct.get("pick_by_capital")
        if not q:
            continue
        row = acct["tradeable"][q]
        pick_cap_total += row["capital_cny"] or 0
        pick_cap_rows[p] = {"hedge": q, "capital_cny": row["capital_cny"],
                            "verdict": carry_verdict(row)}

    keep_rows, keep_total, not_openable = {}, 0.0, []
    for p in PRODUCTS:
        acct = accounts[p]
        q = acct.get("pick_by_capital_keeping_carry")
        if not q:
            not_openable.append(p)
            continue
        row = acct["tradeable"][q]
        keep_total += row["capital_cny"] or 0
        keep_rows[p] = {"hedge": q, "capital_cny": row["capital_cny"],
                        "net_carry_pp": row.get("net_carry_pp"),
                        "sigma_cny": row.get("sigma_cny")}

    ref_all_ok = all(accounts[p]["reference"].get("state") == "ok" for p in PRODUCTS)
    verdict = "REFERENCE_CAPITAL_ASSUMES_A_HEDGE_YOU_CANNOT_BUY"
    if problems:
        verdict = "REFUSE_REFERENCE_GATES_FAILED"

    face = {
        "kind": "idx_fut_carry_tradeable_hedge_capital",
        "generated": now_iso(),
        "evidence_cutoff": self_cutoff(accounts),
        "target_pct": TARGET_PCT,
        "window_years": WINDOW_YEARS,
        "book_capital_cny": 1000000.0,
        "accounts": accounts,
        "totals": {
            "reference_four_arm_cny": round(four_ref, 2),
            "published_two_arm_floor_cny": pub_floor,
            "capital_cheapest_four_arm_cny": round(pick_cap_total, 2),
            "capital_cheapest_rows": pick_cap_rows,
            "carry_keeping_rows": keep_rows,
            "arms_not_openable_as_carry": not_openable,
            "carry_keeping_opening_cost_cny": round(keep_total, 2),
            "reference_multiple_of_book": round(four_ref / 1000000.0, 3),
            "capital_cheapest_multiple_of_book": round(pick_cap_total / 1000000.0, 3),
            "carry_keeping_multiple_of_book": round(keep_total / 1000000.0, 3),
        },
        "gates": gates,
        "problems": problems,
        "inputs": input_digests(),
        "sources": {
            "sizing_face": "results/idx_fut_carry_paper/SIZING.json",
            "floor_face": "results/idx_fut_carry_portfolio_capital.json",
            "desk_face": "results/idx_fut_desk_sheet.json",
            "parent_module": "scripts/idx_fut_carry_paper.py (position_series, per_lot_daily)",
        },
        "unpriced_road": {
            "method": "borrow the tracking ETF (融券) and short it",
            "why_unpriced": "no in-house financing-fee series; naming it keeps the reader "
                            "from reading 'unpriced' as 'free' or as 'does not exist'",
            "etf_for_arm": {p: (BASE.PAIRS.get(p) or [None, None, None])[2] for p in PRODUCTS},
        },
        "verdict": verdict,
        "checks": {
            "G1_reference_arms_reproduce_published": all(
                v for k, v in gates.items() if k.endswith("matches_published")) if any(
                k.endswith("matches_published") for k in gates) else False,
            "G2_two_arm_floor_reproduced": gates.get("published_two_arm_floor_reproduced", False),
            "G3_all_four_reference_arms_measured": ref_all_ok,
            "G4_every_arm_has_a_tradeable_pair": all(
                accounts[p].get("pick_by_capital") for p in PRODUCTS),
            "G5_no_refusal": not problems,
        },
    }
    return face


def self_cutoff(accounts):
    cuts = []
    for a in accounts.values():
        w = (a.get("reference") or {}).get("window")
        if w:
            cuts.append(w[1])
    return max(cuts) if cuts else None


# ------------------------------------------------------------------ markdown
def _money(v):
    return "--" if v is None else "{:,.0f}".format(v)


def _pp(v):
    return "UNPRICED" if v is None else "%+.3f" % v


def render_md(face):
    t = face["totals"]
    out = [DOC_BEGIN, ""]
    out.append("generated %s | evidence_cutoff **%s** | verdict **%s**"
               % (face["generated"], face["evidence_cutoff"], face["verdict"]))
    out.append("")
    out.append("## 三个开仓价，只有两个买得到")
    out.append("")
    out.append("| 口径 | 对冲腿 | 四臂开仓成本 | 倍于 100 万 | 买得到？ |")
    out.append("|---|---|---|---|---|")
    out.append("| 参考（已发布尺子） | 各自指数本身 | %s 元 | %.2fx | 否（指数不能做空） |"
               % (_money(t["reference_four_arm_cny"]), t["reference_multiple_of_book"]))
    out.append("| 可执行·按波动最省 | 另一个品种的期货 | %s 元 | %.2fx | 是（留下指数价差） |"
               % (_money(t["capital_cheapest_four_arm_cny"]),
                  t["capital_cheapest_multiple_of_book"]))
    out.append("| 可执行·且保住 carry | 另一个品种的期货 | %s 元（%s 臂） | %.2fx | 是 |"
               % (_money(t["carry_keeping_opening_cost_cny"]),
                  ",".join(sorted(t["carry_keeping_rows"])) or "无一臂",
                  t["carry_keeping_multiple_of_book"]))
    out.append("| 借券（融券 ETF） | 跟踪 ETF | 未定价 | -- | 有，费用本司无序列 |")
    out.append("")
    out.append("已发布的两臂地板 %s 元复现（IC+IM 参考臂）；四臂参考口径合计 %s 元。"
               % (_money(t["published_two_arm_floor_cny"]), _money(t["reference_four_arm_cny"])))
    out.append("")
    if t["arms_not_openable_as_carry"]:
        bits = []
        for p in t["arms_not_openable_as_carry"]:
            acct = face["accounts"][p]
            own = None
            nets = []
            for _q, row in sorted((acct.get("tradeable") or {}).items()):
                if row.get("state") != "ok":
                    continue
                own = row.get("long_carry_pp") if own is None else own
                if row.get("net_carry_pp") is not None:
                    nets.append("%s %+.3fpp" % (_q, row["net_carry_pp"]))
            bits.append("%s（自身 carry %s；有读数的对冲后净 carry：%s）"
                        % (p, _pp(own), "、".join(nets) if nets else "无一条有读数"))
        out.append("**买得到的对冲下不再是 carry 臂的：%s**——%s。"
                   "未定价不等于免费；这两只在票面上的真正角色是对冲腿，不是 carry 腿。"
                   % (",".join(t["arms_not_openable_as_carry"]), "；".join(bits)))
        out.append("")
    out.append("## 逐臂：参考 vs 可执行（每手年化波动 -> 8% 目标下的资金线）")
    out.append("")
    out.append("| 臂 | 参考波动 | 参考资金 | 对冲品种 | beta 手/手 | 可执行波动 | 可执行资金 | "
               "倍数 | 整手对冲 | 净 carry | 判词 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in PRODUCTS:
        acct = face["accounts"][p]
        ref = acct.get("reference") or {}
        if ref.get("state") != "ok":
            out.append("| %s | -- | -- | -- | -- | -- | -- | -- | -- | -- | %s |"
                       % (p, ref.get("state")))
            continue
        best = acct.get("pick_by_capital")
        if not best:
            out.append("| %s | %s | %s | -- | -- | -- | -- | -- | -- | -- | NO_PAIR |"
                       % (p, _money(ref.get("sigma_cny")), _money(ref.get("capital_cny"))))
            continue
        row = acct["tradeable"][best]
        ratio = (row["sigma_cny"] / ref["sigma_cny"]) if ref.get("sigma_cny") else None
        ih = row.get("integer_hedge") or {}
        out.append("| %s | %s | %s | %s | %.3f | %s | %s | %s | %s 手 -> %s | %s | %s |"
                   % (p, _money(ref.get("sigma_cny")), _money(ref.get("capital_cny")),
                      best, row["beta_lots_per_long_lot"], _money(row["sigma_cny"]),
                      _money(row["capital_cny"]),
                      "--" if ratio is None else "%.2fx" % ratio,
                      ih.get("lots"), _money(ih.get("capital_cny")),
                      _pp(row.get("net_carry_pp")), carry_verdict(row)))
    out.append("")
    out.append("## 两把尺子挑出两只合约")
    out.append("")
    out.append("| 臂 | 按 carry 最省 | 按资金最省 | 一致？ |")
    out.append("|---|---|---|---|")
    for p in PRODUCTS:
        acct = face["accounts"][p]
        out.append("| %s | %s | %s | %s |"
                   % (p, acct.get("pick_by_carry") or "--", acct.get("pick_by_capital") or "--",
                      "是" if not acct.get("rulers_disagree") else "**否**"))
    out.append("")
    out.append("## 全部可执行组合")
    out.append("")
    out.append("| 臂 | 对冲 | 交易日 | beta | 残差波动 | 资金线 | 净 carry | 残差一年盈亏 | 判词 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for p in PRODUCTS:
        for q, row in sorted((face["accounts"][p].get("tradeable") or {}).items()):
            if row.get("state") != "ok":
                out.append("| %s | %s | -- | -- | -- | -- | -- | -- | %s |"
                           % (p, q, row.get("state")))
                continue
            out.append("| %s | %s | %d | %.3f | %s | %s | %s | %s 元 (%s%%) | %s |"
                       % (p, q, row["days"], row["beta_lots_per_long_lot"],
                          _money(row["sigma_cny"]), _money(row["capital_cny"]),
                          _pp(row.get("net_carry_pp")),
                          _money(row.get("residual_pnl_one_year_cny")),
                          "--" if row.get("residual_pnl_pct_of_notional") is None
                          else "%+.2f" % row["residual_pnl_pct_of_notional"],
                          carry_verdict(row)))
    out.append("")
    out.append("## 读法")
    out.append("")
    out.append("1. 参考臂的残差是「期货减自己指数」，这是已发布面上 `ann_vol_per_lot_hedged` "
               "的定义；A 股没有做空指数的工具，所以这条资金线是一把尺子，不是一个订单。")
    out.append("2. 可执行臂的残差是「本品种期货减另一个品种期货」，它是可以真做出来的，"
               "但残差本身就是一笔指数价差仓位——表里最后一列印了它过去一年的盈亏，"
               "别把「hedged」读成「flat」。")
    out.append("3. 两把尺子会挑不同的合约：按 carry 最省挑的是贴水最浅的那只，"
               "按资金最省挑的是残差波动最小的那只；两者都要印，否则读者只拿到一半。")
    out.append("4. 资金线是波动预算线（每手波动 / 8%），不是开户入金线：对冲腿自己的保证金"
               "没有算进来，融券的费率也没有算进来（本司无序列，故不定价）。")
    out.append("")
    out.append(DOC_END)
    return "\n".join(out) + "\n"


def splice_doc(block):
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = ("# 四臂基差 carry：这本书要用什么样的对冲才开得起来\n\n"
                "> 本页读数块由 `scripts/idx_fut_carry_tradeable_hedge_capital.py` "
                "渲染（`--write` 重写、`--check` 逐字比对）。\n")
    if DOC_BEGIN in text and DOC_END in text:
        head, rest = text.split(DOC_BEGIN, 1)
        _mid, tail = rest.split(DOC_END, 1)
        new = head + block.rstrip("\n") + "\n" + tail
    else:
        new = text.rstrip("\n") + "\n\n" + block
    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)


# ------------------------------------------------------------------- check
def compare(pub, fresh, tol, path, problems):
    a, b = pub, fresh
    if a is None and b is None:
        return
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs(float(a) - float(b)) > tol:
            problems.append("%s: face %r vs fresh %r" % (path, a, b))
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            compare(a.get(k), b.get(k), tol, path + "." + str(k), problems)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            problems.append("%s: length %d vs %d" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, tol, "%s[%d]" % (path, i), problems)
        return
    if a != b:
        problems.append("%s: face %r vs fresh %r" % (path, a, b))


def check():
    pub = load_json(OUT_PATH)
    if not pub:
        return 2, "no published face at %s -- run first" % OUT_PATH

    # drift: any input changed since the face was built -> STALE (writer must re-run)
    drift = []
    for rel, sha in (pub.get("inputs") or {}).items():
        now = sha256_file(os.path.join(ROOT, rel))
        if now != sha:
            drift.append(rel)

    fresh = build()
    problems = []
    for key in ("accounts", "totals", "verdict", "target_pct", "window_years"):
        compare(pub.get(key), fresh.get(key), 0.02, key, problems)
    if drift:
        for rel in drift:
            problems.insert(0, "STALE: input changed since publish -> %s" % rel)
        # doc drift too
        if os.path.exists(DOC_PATH):
            with open(DOC_PATH, "r", encoding="utf-8") as fh:
                text = fh.read()
            if DOC_BEGIN in text and DOC_END in text:
                block = text.split(DOC_BEGIN, 1)[1].split(DOC_END, 1)[0]
                if block.strip() != render_md(fresh).split(DOC_BEGIN, 1)[1].split(DOC_END, 1)[0].strip():
                    problems.append("STALE: research page block differs from a fresh render")
        return 3, "\n".join(problems) if problems else "STALE"
    if problems:
        return 1, "\n".join(problems)
    return 0, "ok"


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(cond, name):
        legs.append((bool(cond), name))

    # 1. capital line arithmetic
    leg(abs(capital_for_one_lot(80000.0, 8.0) - 1000000.0) < 1e-6,
        "capital = sigma / target (80,000 at 8% -> 1,000,000)")
    leg(capital_for_one_lot(0.0) is None, "zero vol has no capital line (absent, not zero)")

    # 2. beta of a perfectly proportional pair
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0 * x for x in xs]
    b = beta_no_intercept(xs, ys)
    leg(abs(b - 2.0) < 1e-12, "beta of y=2x is 2")
    leg(max(abs(r) for r in residual(xs, ys, b)) < 1e-12, "residual of y=2x is zero")

    # 3. unrelated hedge cannot claim a small residual
    xs = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
    ys = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    b = beta_no_intercept(xs, ys)
    leg(abs(b) < 1e-12, "orthogonal legs give beta 0")
    leg(statistics.stdev(residual(xs, ys, b)) == 0.0,
        "orthogonal residual is the long leg itself (constant here)")

    # 4. residual vol falls as the hedge explains more
    xs = [1.0, 2.0, 1.5, 2.5, 2.0, 3.0, 2.2, 2.8]
    ys = [x + 0.5 * ((i % 2) - 0.5) for i, x in enumerate(xs)]
    b = beta_no_intercept(xs, ys)
    r_hedged = statistics.stdev(residual(xs, ys, b))
    r_raw = statistics.stdev(ys)
    leg(r_hedged < r_raw, "a fitted hedge lowers the residual vol")

    # 5. integer hedge cannot be better than the fractional one
    xs = [1.0, 2.0, 1.4, 2.2, 1.8, 2.6, 1.6, 2.4]
    ys = [1.6 * x for x in xs]
    b = beta_no_intercept(xs, ys)
    leg(abs(b - 1.6) < 1e-12, "beta 1.6 detected for an integerisation case")
    leg(int(round(b)) == 2, "1.6 hedge lots integerise to 2")

    # 6. missing panel is a state, not a zero
    leg(ann_vol_cny([], 300) is None, "empty series has no vol")
    leg(ann_vol_cny([1.0] * 5, 300) is None, "short series has no vol (absent, not small)")

    # 7. carry verdict matrix
    leg(carry_verdict({"state": "ok", "net_carry_pp": 1.0}) == "HEDGE_KEEPS_THE_CARRY",
        "positive net carry keeps the sleeve")
    leg(carry_verdict({"state": "ok", "net_carry_pp": 0.0}) == "HEDGE_GIVES_THE_SLEEVE_AWAY",
        "zero net carry gives the sleeve away")
    leg(carry_verdict({"state": "ok", "net_carry_pp": None}) == "HEDGE_CARRY_UNPRICED",
        "unpriced hedge is not read as free")

    # 8. picks: capital ruler and carry ruler can differ
    pairs = {
        "A": {"state": "ok", "capital_cny": 100.0, "hedge_carry_pp": 9.0},
        "B": {"state": "ok", "capital_cny": 200.0, "hedge_carry_pp": 1.0},
        "C": {"state": "ok", "capital_cny": 150.0, "hedge_carry_pp": None},
    }
    leg(pick(pairs, "capital") == "A", "capital ruler picks the smallest residual")
    leg(pick(pairs, "carry") == "B", "carry ruler skips the unpriced leg and picks the cheapest")
    leg(pick({"C": pairs["C"]}, "carry") is None, "a pool of unpriced legs has no carry pick")

    # 9. determinism of the arithmetic (no wall clock in the numbers)
    a = build()
    b2 = build()
    for f in (a, b2):
        f.pop("generated", None)
    leg(json.dumps(a, sort_keys=True) == json.dumps(b2, sort_keys=True),
        "two builds are byte-identical apart from the timestamp")

    # 10. check() distinguishes a doctored face from a moved input
    path_backup = None
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, "rb") as fh:
            path_backup = fh.read()
        pub = json.loads(path_backup.decode("utf-8"))
        poisoned = json.loads(json.dumps(pub))
        poisoned["totals"]["capital_cheapest_four_arm_cny"] = (
            (poisoned["totals"].get("capital_cheapest_four_arm_cny") or 0) + 12345.0)
        dump_json(OUT_PATH, poisoned)
        rc1, msg1 = check()
        leg(rc1 == 1 and "STALE" not in msg1, "a doctored number is CHECK FAILED, not STALE")
        drift = json.loads(json.dumps(pub))
        k = next(iter(drift.get("inputs") or {"x": None}))
        if k in (drift.get("inputs") or {}):
            drift["inputs"][k] = "0" * 64
            if drift["inputs"][k] == pub["inputs"][k]:
                drift["inputs"][k] = "1" * 64
        dump_json(OUT_PATH, drift)
        rc3, msg3 = check()
        leg(rc3 == 3 and "STALE" in msg3, "a moved input is STALE")
        with open(OUT_PATH, "wb") as fh:
            fh.write(path_backup)
    else:
        legs.append((False, "no published face on disk for the behaviour legs"))

    passed = sum(1 for ok_, _ in legs if ok_)
    for ok_, name in legs:
        print(("PASS  " if ok_ else "FAIL  ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# -------------------------------------------------------------------- main
def run(write=True):
    face = build()
    if face["verdict"].startswith("REFUSE"):
        print("REFUSE: " + "; ".join(face["problems"]))
        return 4
    if write:
        dump_json(OUT_PATH, face)
        splice_doc(render_md(face))
    t = face["totals"]
    print("verdict %s" % face["verdict"])
    for p in PRODUCTS:
        a = face["accounts"][p]
        ref = a.get("reference") or {}
        q = a.get("pick_by_capital")
        row = (a.get("tradeable") or {}).get(q) or {}
        print("%-3s ref %10s  cap %12s | tradeable %-3s cap %12s  %s"
              % (p, _money(ref.get("sigma_cny")), _money(ref.get("capital_cny")),
                 q or "--", _money(row.get("capital_cny")), a.get("verdict")))
    print("four-arm reference %s  |  capital-cheapest %s  |  carry-keeping %s (%s)  |  not openable as carry: %s"
          % (_money(t["reference_four_arm_cny"]), _money(t["capital_cheapest_four_arm_cny"]),
             _money(t["carry_keeping_opening_cost_cny"]),
             ",".join(sorted(t["carry_keeping_rows"])) or "none",
             ",".join(t["arms_not_openable_as_carry"]) or "none"))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("run", "--write"):
        return run(write=True)
    if cmd in ("dry", "--dry"):
        return run(write=False)
    if cmd == "--check":
        rc, msg = check()
        print(msg)
        return rc
    if cmd == "--selftest":
        return selftest()
    print("usage: python scripts/idx_fut_carry_tradeable_hedge_capital.py "
          "[run|dry|--check|--selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
