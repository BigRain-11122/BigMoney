#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the risk budget is a percentage; a position is a whole block -- how many blocks?

WHY THIS FILE EXISTS
--------------------
`results/policy_return_lattice.json` prices the 1-lot-IC + 1-lot-IM rung, and
`results/idx_fut_carry_sizing_spec.json` turns an 8 % budget into "one lot needs 1,132,145
CNY of capital".  Both divide by a **declared** volatility.  r2109 measured that
declaration on the legs' own spreads: the block runs 13.636 % over the full sample and its
120-day rolling p95 is 24.546 %.  A budget divided by an average is a position that is too
large exactly in the windows that hurt, so this face answers the only question a holder has
after reading r2109:

    at an 8 % budget, how much capital does one price-spread block need, and how many
    blocks does a 1,000,000 CNY book actually fund?

under five rulers (declaration / full sample / 120-day median / p95 / max), plus the
historical block count a holder would have carried in every 120-day window.

WHAT IS OUT OF SCOPE (printed, not implied)
-------------------------------------------
the equity sleeve, financing, margin and transaction costs.  The per-account hedged residual
that the sizing face prices (one IC lot hedged with IF) is a **different book** from the
IC+IM spread block this face sizes; the two are named side by side on the page and never
averaged.

verdict tokens (frozen before the first run):
  DECLARATION_UNDERSTATES_RISK / DECLARATION_COVERS_RISK
       full-sample block vol is above / at-or-below the declaration (tolerance = the
       publishing precision of the stability face, half an ulp of 3 dp)
  PRESSURE_BENCHES_THE_BOOK / PRESSURE_FUNDS_ONE_BLOCK
       the 120-day p95 window funds fewer than one whole block / at least one
  TICKET_EXCEEDS_BUDGET_AT_EVERY_RULER / TICKET_FITS_SOME_RULER
       the desk's recommended ticket spends more than the budget under every ruler / at
       least one ruler funds it
  DATA_BLOCKED
       an input is missing or unreadable; refuse, never default

Usage:
    python scripts/idx_fut_carry_vol_sized_lots.py run
    python scripts/idx_fut_carry_vol_sized_lots.py check
    python scripts/idx_fut_carry_vol_sized_lots.py --selftest
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import idx_fut_carry_ladder_stability as S  # pure arithmetic + the legs' spread authority

SCHEMA = "idx-fut-carry-vol-sized-lots/v1"
KIND = "carry_vol_sized_lots"
STABILITY = os.path.join(ROOT, "results", "idx_fut_carry_ladder_stability.json")
SIZING = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
OUT = os.path.join(ROOT, "results", "idx_fut_carry_vol_sized_lots.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_VOL_SIZED_LOTS.md")

WINDOW = 120
VOL_TOL = 0.002      # the stability face publishes 3 dp; half an ulp is 0.0005
LOT_TOL = 1e-4
MONEY_TOL = 0.05

V_DECL_LOW = "DECLARATION_UNDERSTATES_RISK"
V_DECL_OK = "DECLARATION_COVERS_RISK"
V_PRESS_BENCH = "PRESSURE_BENCHES_THE_BOOK"
V_PRESS_ONE = "PRESSURE_FUNDS_ONE_BLOCK"
V_TICKET_EVERY = "TICKET_EXCEEDS_BUDGET_AT_EVERY_RULER"
V_TICKET_SOME = "TICKET_FITS_SOME_RULER"
V_BLOCK = "DATA_BLOCKED"

RULER_ORDER = ("declared", "full_sample", "rolling_120_median", "rolling_120_p95",
               "rolling_120_max")
RULER_LABEL = {
    "declared": "declaration (ladder's own 4 % per unit notional)",
    "full_sample": "full sample (2022-07 -> 2026-11)",
    "rolling_120_median": "120-day rolling median",
    "rolling_120_p95": "120-day rolling p95",
    "rolling_120_max": "120-day rolling max",
}


# ------------------------------------------------------------------ io
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


# ------------------------------------------------------------------ arithmetic (pure)
def blocks_at(target_pct, block_vol_pct):
    """blocks = target / vol -- the sizing face's rule with the same percentage numerator."""
    if target_pct is None or block_vol_pct is None:
        return None
    target_pct, block_vol_pct = float(target_pct), float(block_vol_pct)
    if block_vol_pct <= 0:
        return None
    return target_pct / block_vol_pct


def ruler(name, block_vol_pct, nav, target_pct, ticket_blocks):
    """One ruler's whole answer: what one block costs and what the book funds."""
    b = blocks_at(target_pct, block_vol_pct)
    if b is None:
        return None
    per_block_cny = float(block_vol_pct) / 100.0 * float(nav)
    capital_one = per_block_cny / (float(target_pct) / 100.0)
    return {
        "ruler": name,
        "block_vol_pct": round(float(block_vol_pct), 3),
        "per_block_vol_cny": round(per_block_cny, 2),
        "capital_one_block_cny": round(capital_one, 2),
        "blocks_float_at_book": round(b, 4),
        "blocks_whole_at_book": int(math.floor(b)),
        "ticket_blocks": int(ticket_blocks),
        "ticket_vol_cny": round(ticket_blocks * per_block_cny, 2),
        "ticket_multiple_of_budget": round(ticket_blocks * float(block_vol_pct) / float(target_pct), 4),
        "capital_for_ticket_cny": round(ticket_blocks * capital_one, 2),
    }


def judge(rulers, history, target_pct):
    """Frozen tokens; derived from the ruler table and the window history only."""
    by = {r["ruler"]: r for r in rulers if r}
    declared = by["declared"]["block_vol_pct"]
    full = by["full_sample"]["block_vol_pct"]
    p95 = by["rolling_120_p95"]["block_vol_pct"]
    multiples = {r["ruler"]: r["ticket_multiple_of_budget"] for r in rulers if r}
    return {
        "declaration": V_DECL_LOW if (full - declared) > VOL_TOL else V_DECL_OK,
        "understatement_pp": round(full - declared, 3),
        "understatement_ratio": round(full / declared, 4) if declared else None,
        "pressure": V_PRESS_BENCH if p95 > float(target_pct) else V_PRESS_ONE,
        "pressure_blocks_float": by["rolling_120_p95"]["blocks_float_at_book"],
        "pressure_capital_one_block_cny": by["rolling_120_p95"]["capital_one_block_cny"],
        "ticket": V_TICKET_EVERY if all(m > 1.0 for m in multiples.values()) else V_TICKET_SOME,
        "ticket_multiples": multiples,
        "share_windows_funding_one_block": history["share_windows_funding_one_block"],
        "share_windows_funding_two_blocks": history["share_windows_funding_two_blocks"],
        "whole_block_max": history["whole_block_max"],
    }


def window_lots(nav, target_pct):
    """Every 120-day window's block vol, turned into a block count at the budget."""
    lattice = read_json(LATTICE)
    legs = {}
    for p in ("IC", "IM"):
        leg = S.spread_leg(p)
        if "_refused" in leg:
            return None, "leg %s refused: %s" % (p, leg["_refused"])
        legs[p] = leg
    n_lot = S.per_lot_notional(lattice)
    if not n_lot.get("IC") or not n_lot.get("IM"):
        return None, "ladder does not publish per-lot notionals"
    w_ic = n_lot["IC"] / float(nav)
    w_im = n_lot["IM"] / float(nav)
    dates, a, b = S.align(legs["IC"]["dates"], legs["IC"]["spread"],
                          legs["IM"]["dates"], legs["IM"]["spread"])
    rows = S.with_block(S.rolling(dates, a, b, WINDOW), w_ic, w_im)
    if not rows:
        return None, "no rolling rows"
    volts = [r["block_vol_pct"] for r in rows]
    lots = [float(target_pct) / v for v in volts]
    flips, prev = 0, None
    for x in lots:
        k = int(math.floor(x))
        if prev is not None and k != prev:
            flips += 1
        prev = k
    return {
        "window": WINDOW,
        "windows": len(rows),
        "span": [rows[0]["end"], rows[-1]["end"]],
        "block_vol_min_pct": round(min(volts), 3),
        "block_vol_median_pct": round(S.pctl(volts, 0.5), 3),
        "block_vol_p95_pct": round(S.pctl(volts, 0.95), 3),
        "block_vol_max_pct": round(max(volts), 3),
        "blocks_float_min": round(min(lots), 4),
        "blocks_float_median": round(S.pctl(lots, 0.5), 4),
        "blocks_float_p95": round(S.pctl(lots, 0.95), 4),
        "blocks_float_max": round(max(lots), 4),
        "share_windows_funding_one_block": round(
            sum(1 for x in lots if x >= 1.0) / float(len(lots)), 4),
        "share_windows_funding_two_blocks": round(
            sum(1 for x in lots if x >= 2.0) / float(len(lots)), 4),
        "whole_block_switches": flips,
        "whole_block_max": int(math.floor(max(lots))),
    }, None


# ------------------------------------------------------------------ build
def build():
    for p in (STABILITY, SIZING, LATTICE):
        if not os.path.exists(p):
            return None, {"verdict": V_BLOCK, "why": "input missing: %s" % p}
    stab = read_json(STABILITY)
    sizing = read_json(SIZING)
    lattice = read_json(LATTICE)

    nav = float(lattice.get("nav_cny") or 0.0)
    if nav <= 0:
        return None, {"verdict": V_BLOCK, "why": "lattice publishes no nav_cny"}
    adoption = sizing.get("adoption") or {}
    if adoption.get("target_pct") is None:
        return None, {"verdict": V_BLOCK, "why": "sizing face publishes no adoption.target_pct"}
    target_pct = float(adoption["target_pct"])
    ticket = ((sizing.get("accounts") or {}).get("IC") or {}).get("ticket") or {}
    if ticket.get("lots") is None:
        return None, {"verdict": V_BLOCK, "why": "sizing face publishes no IC ticket lots"}
    ticket_blocks = int(ticket["lots"])

    h = stab.get("headline") or {}
    r120 = (stab.get("rolling") or {}).get("120") or {}
    for k in ("declared_block_vol_pct", "block_vol_full_pct"):
        if h.get(k) is None:
            return None, {"verdict": V_BLOCK, "why": "stability headline missing %s" % k}
    for k in ("block_vol_median_pct", "block_vol_p95_pct", "block_vol_max_pct"):
        if r120.get(k) is None:
            return None, {"verdict": V_BLOCK, "why": "stability rolling/120 missing %s" % k}

    rulers = [
        ruler("declared", float(h["declared_block_vol_pct"]), nav, target_pct, ticket_blocks),
        ruler("full_sample", float(h["block_vol_full_pct"]), nav, target_pct, ticket_blocks),
        ruler("rolling_120_median", float(r120["block_vol_median_pct"]), nav, target_pct,
              ticket_blocks),
        ruler("rolling_120_p95", float(r120["block_vol_p95_pct"]), nav, target_pct,
              ticket_blocks),
        ruler("rolling_120_max", float(r120["block_vol_max_pct"]), nav, target_pct,
              ticket_blocks),
    ]
    if any(r is None for r in rulers):
        return None, {"verdict": V_BLOCK, "why": "a ruler produced no block count"}

    history, why = window_lots(nav, target_pct)
    if history is None:
        return None, {"verdict": V_BLOCK, "why": why}

    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": history["span"][1],
        "generated": None,
        "inputs": {
            "stability": {"path": "results/idx_fut_carry_ladder_stability.json",
                          "sha256": digest(STABILITY)},
            "sizing": {"path": "results/idx_fut_carry_sizing_spec.json",
                       "sha256": digest(SIZING)},
            "lattice": {"path": "results/policy_return_lattice.json",
                        "sha256": digest(LATTICE)},
        },
        "question": ("at an 8 % risk budget, how much capital does one IC+IM price-spread "
                     "block need, and how many blocks does a 1,000,000 CNY book fund?"),
        "rule": ("blocks = target_pct / block_vol_pct; one block needs "
                 "block_vol_pct/100 * nav / (target_pct/100) CNY of capital"),
        "nav_cny": nav,
        "target_pct": target_pct,
        "ticket_blocks": ticket_blocks,
        "rulers": rulers,
        "history": history,
        "judgment": judge(rulers, history, target_pct),
        "scope_limits": [
            "futures block only (1 lot IC + 1 lot IM); the equity sleeve, financing,",
            "margin and transaction costs stay in results/idx_fut_carry_ladder_risk.json",
            "the sizing face prices one IC lot hedged with IF, a different book; the two",
            "are named side by side on the page and never averaged",
        ],
        "not_recomputed": [
            "the volatility series itself (imported from idx_fut_carry_ladder_stability)",
            "the 8 % target and the desk's ticket (read from the sizing face, printed, "
            "never rewritten)",
            "any income, Sharpe or drawdown: this face only sizes a position",
        ],
    }
    import datetime
    face["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    face["cross_face"] = cross_face(face)
    return face, None


def cross_face(face):
    """The two faces a reader will put side by side, reconciled in words not averages."""
    out = {}
    by = {r["ruler"]: r for r in face["rulers"]}
    try:
        stab = read_json(STABILITY)
        theirs = float(stab["headline"]["block_vol_full_pct"])
        mine = float(by["full_sample"]["block_vol_pct"])
        out["stability"] = {
            "status": "CROSS_FACE_MATCHES" if abs(mine - theirs) <= VOL_TOL
            else "CROSS_FACE_DIVERGES",
            "sibling_face": "results/idx_fut_carry_ladder_stability.json",
            "sibling_full_sample_pct": round(theirs, 3),
            "this_face_full_sample_pct": round(mine, 3),
            "delta_pp": round(mine - theirs, 3),
        }
    except Exception as exc:  # a missing sibling is named, never scored 0
        out["stability"] = {"status": "SIBLING_UNREADABLE", "why": str(exc)}
    try:
        sz = read_json(SIZING)
        ic = ((sz.get("accounts") or {}).get("IC") or {})
        out["sizing"] = {
            "status": "DIFFERENT_BOOK_NAMED",
            "sibling_face": "results/idx_fut_carry_sizing_spec.json",
            "sibling_one_lot_capital_cny": ic.get("first_executable_capital_cny"),
            "sibling_basis": ("one IC lot hedged with IF (per-account residual), not the "
                              "IC+IM spread block"),
            "this_face_one_block_capital_cny": by["full_sample"]["capital_one_block_cny"],
            "why_not_an_average": ("the two faces size different books; the spread block is "
                                   "the one a holder of the lattice's 1/1 rung carries"),
        }
    except Exception as exc:
        out["sizing"] = {"status": "SIBLING_UNREADABLE", "why": str(exc)}
    return out


# ------------------------------------------------------------------ page
def _money(v):
    return "{:,.0f}".format(v)


def write_doc(face):
    j = face["judgment"]
    by = {r["ruler"]: r for r in face["rulers"]}
    hi = face["history"]
    lines = []
    A = lines.append
    A("# 8 % 的风险预算，摊到实测波动上：一个价差块要多少钱")
    A("")
    A("generated %s | evidence cutoff %s | nav %s 元 | 目标波动 %.2f %%"
      % (face["generated"], face["evidence_cutoff"], _money(face["nav_cny"]),
         face["target_pct"]))
    A("")
    A("> 一句话：**1 个 IC+IM 价差块的实测波动是 %.3f %%，不是声明里那个 %.3f %%**。"
      "按 8 %% 预算，1 块要 **%s 元**资本，100 万的书**只能开 %.2f 块**；"
      "而桌面推荐的那张 %d 块票，在最乐观的尺子上也要花掉 **%.2f 倍**预算，"
      "在压力窗（120 日 p95）下要 **%.2f 倍**。"
      % (by["full_sample"]["block_vol_pct"], by["declared"]["block_vol_pct"],
         _money(by["full_sample"]["capital_one_block_cny"]),
         by["full_sample"]["blocks_float_at_book"], face["ticket_blocks"],
         by["declared"]["ticket_multiple_of_budget"],
         by["rolling_120_p95"]["ticket_multiple_of_budget"]))
    A("")
    A("## 1. 每把尺子下的账")
    A("")
    A("| 尺子 | 块波动 %% | 1 块波动（元） | 1 块需要资本（元） | 100 万能开（块） | 整块 | %d 块票占用预算倍数 |"
      % face["ticket_blocks"])
    A("|---|---|---|---|---|---|---|")
    for name in RULER_ORDER:
        r = by[name]
        A("| %s | %.3f | %s | %s | %.4f | %d | %.4f |"
          % (RULER_LABEL[name], r["block_vol_pct"], _money(r["per_block_vol_cny"]),
             _money(r["capital_one_block_cny"]), r["blocks_float_at_book"],
             r["blocks_whole_at_book"], r["ticket_multiple_of_budget"]))
    A("")
    A("- 声明与实测的差：**%.3f pp**（实测是声明的 **%.2f 倍**）"
      % (j["understatement_pp"], j["understatement_ratio"]))
    A("- 压力窗（120 日 p95）：1 块要 **%s 元**资本，100 万只能开 **%.4f 块**"
      % (_money(j["pressure_capital_one_block_cny"]), j["pressure_blocks_float"]))
    A("- 判词：`%s` / `%s` / `%s`"
      % (j["declaration"], j["pressure"], j["ticket"]))
    A("")
    A("## 2. 历史上每 %d 个交易日一个窗，能开几块" % hi["window"])
    A("")
    A("- 窗数 **%d**（%s → %s）" % (hi["windows"], hi["span"][0], hi["span"][1]))
    A("- 块波动：min **%.3f %%** / 中位 **%.3f %%** / p95 **%.3f %%** / max **%.3f %%**"
      % (hi["block_vol_min_pct"], hi["block_vol_median_pct"], hi["block_vol_p95_pct"],
         hi["block_vol_max_pct"]))
    A("- 100 万能开：min **%.4f 块** / 中位 **%.4f 块** / p95 **%.4f 块** / max **%.4f 块**"
      % (hi["blocks_float_min"], hi["blocks_float_median"], hi["blocks_float_p95"],
         hi["blocks_float_max"]))
    A("- 开得起整 1 块的窗：**%.2f %%**；开得起整 2 块的窗：**%.2f %%**"
      % (hi["share_windows_funding_one_block"] * 100.0,
         hi["share_windows_funding_two_blocks"] * 100.0))
    A("- 整块数在历史窗里切换 **%d 次**，最多 **%d 块**"
      % (hi["whole_block_switches"], hi["whole_block_max"]))
    A("")
    A("读法：**这本书在任何历史窗里都没有开满 2 块**，"
      "而且只有在块波动最低的那 %.0f %% 的窗里才开得起 1 块。"
      % (hi["share_windows_funding_one_block"] * 100.0))
    A("")
    A("## 3. 与相邻面不是同一个量（不许平均）")
    A("")
    cf = face["cross_face"]
    st = cf.get("stability") or {}
    sz = cf.get("sizing") or {}
    A("- `idx_fut_carry_ladder_stability`：**%s**（兄弟面 %.3f %% vs 本面 %.3f %%，差 %.3f pp）"
      % (st.get("status"), st.get("sibling_full_sample_pct", float("nan")),
         st.get("this_face_full_sample_pct", float("nan")), st.get("delta_pp", float("nan"))))
    A("- `idx_fut_carry_sizing_spec`：**%s** —— 它按「1 手 IC 用 IF 对冲后的残差」定价"
      "（1 手 **%s 元**），本面按「IC+IM 价差块」定价（1 块 **%s 元**）。"
      "两本书不同，数字不该相等，也不该取平均。"
      % (sz.get("status"), _money(sz.get("sibling_one_lot_capital_cny") or 0.0),
         _money(sz.get("this_face_one_block_capital_cny") or 0.0)))
    A("")
    A("## 4. 口径边界")
    A("")
    for s in face["scope_limits"]:
        A("- " + s)
    A("")
    A("## 5. 复算")
    A("")
    A("```")
    A("python scripts/idx_fut_carry_vol_sized_lots.py run")
    A("python scripts/idx_fut_carry_vol_sized_lots.py check     # 漂移说 STALE，同输入不符说 CHECK FAILED")
    A("python scripts/idx_fut_carry_vol_sized_lots.py --selftest")
    A("```")
    A("")
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------------ check
def _flat(face):
    """Everything a reader can act on, without provenance/timestamps."""
    out = []
    for r in face["rulers"]:
        out.append({k: v for k, v in r.items()})
    out.append(dict(face["history"]))
    out.append(dict(face["judgment"]))
    return out


def _diff(a, b):
    bad = []
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            for k in x:
                xv, yv = x.get(k), y.get(k)
                if xv == yv:
                    continue
                tol = MONEY_TOL if "cny" in k else (VOL_TOL if k.endswith("_pct") else LOT_TOL)
                if isinstance(xv, (int, float)) and isinstance(yv, (int, float)):
                    if abs(float(xv) - float(yv)) <= tol:
                        continue
                bad.append("row %d field %s: face %r != recomputed %r" % (i, k, xv, yv))
    return bad


def check():
    if not os.path.exists(OUT):
        return 3, ["face missing: %s (STALE, rebuild)" % OUT]
    face = read_json(OUT)
    stale = []
    for key, path in (("stability", STABILITY), ("sizing", SIZING), ("lattice", LATTICE)):
        rec = (face.get("inputs") or {}).get(key) or {}
        if not os.path.exists(path):
            stale.append("input missing: %s (STALE, rebuild)" % path)
            continue
        if rec.get("sha256") != digest(path):
            stale.append("input drifted: %s (STALE, rebuild)" % path)
    if stale:
        return 3, stale
    fresh, refusal = build()
    if refusal is not None:
        return 3, ["build refused: %s" % refusal]
    bad = _diff(_flat(face), _flat(fresh))
    if bad:
        return 3, ["CHECK FAILED"] + bad
    return 0, ["CHECK_OK %d rulers / %d windows" % (len(fresh["rulers"]),
                                                    fresh["history"]["windows"])]


# ------------------------------------------------------------------ selftest
def _selftest():
    fails = []
    state = {"legs": 0}

    def pin(name, got, want, tol=LOT_TOL):
        state["legs"] += 1
        ok = (abs(float(got) - float(want)) <= tol) if isinstance(want, (int, float)) else (got == want)
        if not ok:
            fails.append("%s: %r != %r" % (name, got, want))

    # 1. the rule itself
    pin("blocks_at(8,13.636)", blocks_at(8.0, 13.636), 8.0 / 13.636)
    pin("blocks_at(8,0) refuses", blocks_at(8.0, 0.0), None)
    pin("blocks_at(None,10) refuses", blocks_at(None, 10.0), None)
    # 2. monotonic: more vol -> fewer blocks
    state["legs"] += 1
    if not (blocks_at(8.0, 5.0) > blocks_at(8.0, 20.0)):
        fails.append("monotonicity: vol up must cut blocks")
    # 3. one ruler's identity: capital_one * target/100 == per_block_vol
    r = ruler("t", 13.636, 1000000.0, 8.0, 4)
    pin("identity capital", r["capital_one_block_cny"] * 0.08, r["per_block_vol_cny"], 0.05)
    pin("identity blocks", r["blocks_float_at_book"], 8.0 / 13.636)
    pin("ticket multiple", r["ticket_multiple_of_budget"], 4 * 13.636 / 8.0, 1e-4)
    pin("ticket capital", r["capital_for_ticket_cny"], 4 * 136360.0 / 0.08, 1.0)
    # 4. judgment tokens, both directions
    hist = {"share_windows_funding_one_block": 0.29, "share_windows_funding_two_blocks": 0.0,
            "whole_block_max": 1}
    rs = [ruler("declared", 8.963, 1e6, 8.0, 4), ruler("full_sample", 13.636, 1e6, 8.0, 4),
          ruler("rolling_120_median", 11.691, 1e6, 8.0, 4),
          ruler("rolling_120_p95", 24.546, 1e6, 8.0, 4),
          ruler("rolling_120_max", 24.704, 1e6, 8.0, 4)]
    j = judge(rs, hist, 8.0)
    pin("judge decl low", j["declaration"], V_DECL_LOW)
    pin("judge pressure", j["pressure"], V_PRESS_BENCH)
    pin("judge ticket", j["ticket"], V_TICKET_EVERY)
    # 5. reverse: a declaration above the sample flips both tokens
    rs2 = [ruler("declared", 30.0, 1e6, 8.0, 1), ruler("full_sample", 13.636, 1e6, 8.0, 1),
           ruler("rolling_120_median", 11.691, 1e6, 8.0, 1),
           ruler("rolling_120_p95", 7.0, 1e6, 8.0, 1), ruler("rolling_120_max", 7.5, 1e6, 8.0, 1)]
    j2 = judge(rs2, hist, 8.0)
    pin("judge decl ok", j2["declaration"], V_DECL_OK)
    pin("judge pressure one", j2["pressure"], V_PRESS_ONE)
    pin("judge ticket some", j2["ticket"], V_TICKET_SOME)
    # 6. the published face is consistent with its own rule
    if os.path.exists(OUT):
        face = read_json(OUT)
        for x in face["rulers"]:
            pin("face %s blocks" % x["ruler"],
                x["blocks_float_at_book"], 8.0 / x["block_vol_pct"], 1e-3)
            pin("face %s whole" % x["ruler"],
                x["blocks_whole_at_book"], int(math.floor(8.0 / x["block_vol_pct"])))
    # 7. percentiles are monotone in q (the page quotes them)
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    state["legs"] += 1
    if not (S.pctl(xs, 0.0) <= S.pctl(xs, 0.5) <= S.pctl(xs, 1.0)):
        fails.append("pctl not monotone")
    print("SELFTEST %d/%d %s" % (state["legs"] - len(fails), state["legs"],
                                  "ALL_PASS" if not fails else "FAILED"))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.mode == "check":
        rc, msgs = check()
        for m in msgs:
            print(m)
        return rc
    face, refusal = build()
    if refusal is not None:
        print(json.dumps(refusal, ensure_ascii=False))
        return 2
    write_json(OUT, face)
    write_doc(face)
    j = face["judgment"]
    print("VERDICT %s / %s / %s" % (j["declaration"], j["pressure"], j["ticket"]))
    print("blocks at book capital: " + " | ".join(
        "%s=%.4f" % (r["ruler"], r["blocks_float_at_book"]) for r in face["rulers"]))
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("wrote %s" % os.path.relpath(DOC, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
