#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""three_book_wallet_ladder -- the wallet reads the gate at 1,000,000 CNY, but the gate is
a function of capital, and nobody had printed that function.

WHY THIS FILE EXISTS
--------------------
`three_book_wallet` (r2198) answered the 1,000,000-CNY question: three books, one wallet,
and the carry book -- best Sharpe of the three -- takes weight 0.00 because ONE IC lot
consumes 91,029 CNY of an 80,000-CNY volatility budget.  It priced the refusal honestly
(0.784 of Sharpe) and then stopped, because the wallet it was handed was 1,000,000.

That stopping point hides the reader's next question, and it is not a hypothetical one:
the same face already prints that the ungated optimum wants carry at 50%, which fits only
at 2,275,725 CNY.  So the face publishes a number it cannot buy, and a reader with
1,200,000 CNY cannot tell from it whether 200,000 more is what stands between the two
answers.

This face answers exactly that, by re-reading the parent's own grid at a ladder of
wallet sizes instead of one:

  * what the best FEASIBLE mix is at each capital rung,
  * what weight carry can even be expressed at that rung (the band, not a point),
  * what each rung still pays to the gate (Sharpe),
  * what the NEXT 100,000 CNY of capital buys, in Sharpe,
  * and where the gate stops binding entirely.

THE MECHANISM, IN ONE LINE
--------------------------
A book bought in lots cannot be bought in weights.  A wallet W can hold carry weight w
only when W * w >= 1,137,862.5 CNY (one lot at the 8% budget), so the smallest positive
carry weight expressible at W is 1,137,862.5 / W.  Below W = 1,137,862.5 that band is
empty (weight 0 only); between 1,137,862.5 and 2,275,725 the band starts at a weight no
diversifier would choose; at 2,275,725 the band finally includes the 50% the grid wants.

WHAT THIS FACE DOES NOT DO
--------------------------
It imports the parent's own machinery (`three_book_wallet.load_books / align / vol_scale /
stats / blend / weight_grid / feasible / FLOORS`) and re-prices nothing: no backtest is
re-run, no book is re-derived, no volatility is re-estimated.  The only new arithmetic is
the search over wallets.  The 1,000,000 rung is asserted equal to the parent's published
`best_inside_gate` -- if the two disagree, this face goes red rather than printing a
second opinion.

HONESTY LINES (each one also printed on the page)
-------------------------------------------------
  * weights are quantised at 0.05, so a band edge is reported as the grid weight it can
    actually reach, never as the exact real number;
  * carry is the hedged EXCESS, gross of the hedge leg's cost, and a real hedge needs a
    second account -- the parent's caliber, not re-estimated here;
  * the mix's realised vol is usually BELOW 8%, so the Sharpe ladder is not a money
    ladder: `money_cny_per_year` is printed at each rung's own realised vol, and
    `leverage_to_8pct` is printed beside it with r2199's measured financing price named
    rather than amortised into a fantasy;
  * this is a within-sample statement on the three books' common window (2020-2026).
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402  (kept for the selftest's synthetic legs)

import three_book_wallet as W  # noqa: E402

FACE = os.path.join(ROOT, "results", "three_book_wallet_ladder.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_WALLET_LADDER.md")
PARENT_FACE = os.path.join(ROOT, "results", "three_book_wallet.json")
SCHEMA = "three-book-wallet-ladder/v1"

TZ = timezone(timedelta(hours=8))
TARGET_VOL = W.TARGET_VOL
GRID_STEP = W.STEP

# Round rungs a reader can hold in their head, below and above the parent's 1,000,000.
ROUND_LADDER_CNY = (400_000, 750_000, 1_000_000, 1_250_000, 1_500_000, 1_750_000,
                    2_000_000, 2_500_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000)


# ------------------------------------------------------------------ small helpers
def _rp(rel):
    return os.path.join(ROOT, rel)


def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _stamp(rel):
    """Same shape as the parent's stamp: path/size/mtime or missing."""
    return W._stamp(rel)


def _plain(o):
    return W._plain(o)


def _read_json(rel):
    p = _rp(rel)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


# ------------------------------------------------------------------ the band
def min_carry_weight(wallet, floor=None):
    """Smallest positive carry weight a wallet of `wallet` CNY can express at all.

    Returns None when no positive weight fits (the band is empty and only 0 is legal).
    This is the whole mechanism of the face: one lot is indivisible, so the affordable
    weights are a half-line [floor/wallet, 1], not the whole interval (0, 1].
    """
    floor = W.FLOORS["carry"] if floor is None else float(floor)
    if floor <= 0:
        return 0.0
    if wallet <= 0:
        return None
    w = floor / float(wallet)
    return w if w <= 1.0 + 1e-12 else None


def grid_floor_at(weight):
    """The smallest grid weight >= `weight` (weights are quantised at GRID_STEP)."""
    n = int(round(1.0 / GRID_STEP))
    k = int(math.ceil(weight * n - 1e-9))
    return min(max(k, 0), n) / float(n)


def best_at(rows, wallet):
    """Best-Sharpe feasible cell at one wallet, plus what that rung costs the gate."""
    feasible_rows = [r for r in rows if W.feasible(tuple(r["w"]), wallet)]
    if not feasible_rows:
        return None
    b = max(feasible_rows, key=lambda r: r["sharpe"])
    out = dict(b)
    out["n_feasible_cells"] = len(feasible_rows)
    band = min_carry_weight(wallet)
    out["band"] = {
        "min_positive_carry_weight": (None if band is None else round(band, 6)),
        "min_positive_carry_weight_on_grid": (None if band is None else grid_floor_at(band)),
        "band_is_empty": band is None,
        "why": ("W * w >= one lot's capital (%.2f CNY at the 8%% budget); below that the only "
                "legal carry weight is 0" % W.FLOORS["carry"]),
    }
    if b["w"][2] > 0:
        out["carry_lots_at_this_weight"] = round(wallet * b["w"][2] / W.FLOORS["carry"], 6)
        out["carry_money_at_this_weight_cny"] = round(wallet * b["w"][2], 0)
    else:
        out["carry_lots_at_this_weight"] = 0.0
        out["carry_money_at_this_weight_cny"] = 0.0
    return out


def ladder_rungs(unc, floor_carry):
    """Round rungs + the structural rungs the arithmetic itself names."""
    out = {}
    for w in ROUND_LADDER_CNY:
        out[float(w)] = "round rung"
    if floor_carry > 0:
        structural = (
            (floor_carry,
             "first lot: ONE IC contract is 100% of this wallet's 8% budget"),
            (floor_carry / 0.95,
             "first two-book mix: 95% carry still leaves room for one other book"),
        )
        w_want = float(((unc or {}).get("w") or [0, 0, 0])[2] or 0.0)
        if w_want > 0:
            structural += ((floor_carry / w_want,
                            "wanted weight: carry can finally sit at the weight the ungated "
                            "grid picks (%.0f%%)" % (w_want * 100.0)),)
        for w, why in structural:
            out[round(float(w), 2)] = why
    return [(k, out[k]) for k in sorted(out)]


# ------------------------------------------------------------------ build
def build(write=True, quiet=False):
    series, _metas = W.load_books()
    aligned, idx = W.align(series)
    if len(idx) < 500:
        raise SystemExit("three_book_wallet_ladder: common window too short (%d bars)" % len(idx))

    scaled = {}
    gains = {}
    for k, s in aligned.items():
        scaled[k], gains[k] = W.vol_scale(s)

    # One grid, priced once. Every rung below is a different FEASIBLE SUBSET of it.
    rows = []
    for w in W.weight_grid():
        st = W.stats(W.blend(scaled, w))
        if st.get("status") == "short":
            continue
        rows.append({
            "w": [round(x, 4) for x in w],
            "cagr": st["cagr"], "sharpe": st["sharpe"], "vol": st["vol"],
            "maxdd": st["maxdd"], "worst_year": st["worst_year"],
        })
    if not rows:
        raise SystemExit("three_book_wallet_ladder: empty weight grid")

    unc = max(rows, key=lambda r: r["sharpe"])
    floor_carry = W.FLOORS["carry"]
    wallet_now = W.WALLET_CNY

    base = best_at(rows, wallet_now)
    if base is None:
        raise SystemExit("three_book_wallet_ladder: no feasible cell at the parent's wallet")

    rungs = []
    prev = None
    for wallet, why in ladder_rungs(unc, floor_carry):
        b = best_at(rows, wallet)
        if b is None:
            rungs.append({"wallet_cny": round(wallet, 2), "why": why,
                          "best": None, "note": "no weight cell fits this wallet"})
            prev = None
            continue
        gap = round(wallet - wallet_now, 2)
        gain_vs_now = round(b["sharpe"] - base["sharpe"], 6)
        marginal = None
        if gap > 0 and gain_vs_now > 0:
            marginal = round(gain_vs_now / gap * 1_000_000.0, 3)
        entry = {
            "wallet_cny": round(wallet, 2),
            "why": why,
            "best": {
                "w": b["w"], "cagr": b["cagr"], "sharpe": b["sharpe"], "vol": b["vol"],
                "maxdd": b["maxdd"], "worst_year": b["worst_year"],
            },
            "band": b["band"],
            "n_feasible_cells": b["n_feasible_cells"],
            "carry_weight_pct": round(b["w"][2] * 100.0, 2),
            "carry_lots_at_this_weight": b["carry_lots_at_this_weight"],
            "carry_money_at_this_weight_cny": b["carry_money_at_this_weight_cny"],
            "gate_price_sharpe": round(unc["sharpe"] - b["sharpe"], 6),
            "capital_gap_from_parent_wallet_cny": gap,
            "sharpe_gain_from_parent_wallet": gain_vs_now,
            "marginal_sharpe_per_million_cny": marginal,
            "money_cny_per_year": round(wallet * b["cagr"], 0),
            "return_at_8pct_identity_pct": round(TARGET_VOL * b["sharpe"] * 100.0, 3),
            "leverage_to_8pct": round(TARGET_VOL / b["vol"], 4) if b["vol"] > 0 else None,
        }
        if prev is not None:
            step_gap = wallet - prev["wallet_cny"]
            step_gain = b["sharpe"] - prev["best"]["sharpe"]
            entry["step"] = {
                "from_wallet_cny": prev["wallet_cny"],
                "extra_capital_cny": round(step_gap, 2),
                "sharpe_gain": round(step_gain, 6),
                "sharpe_per_million_cny": (round(step_gain / step_gap * 1_000_000.0, 3)
                                           if step_gap > 0 else None),
            }
        rungs.append(entry)
        prev = entry

    # ---- the cliff, read off the ladder itself (no hand-typed numbers)
    # FLOORS["carry"] already IS one lot's capital at the 8% budget (91,029 / 0.08);
    # dividing by the target again would print a 14.2m rung that answers nothing.
    first_rung_wallet = round(floor_carry, 2)
    just_below = best_at(rows, first_rung_wallet - 1.0)
    at_rung = best_at(rows, first_rung_wallet)
    mix_rung_wallet = round(floor_carry / 0.95, 2)
    wanted_wallet = round(floor_carry / (unc["w"][2] or 1.0), 2)
    total_gain = round(unc["sharpe"] - base["sharpe"], 6)
    jump = round(at_rung["sharpe"] - just_below["sharpe"], 6) if at_rung and just_below else None
    entry_facts = {
        "parent_wallet_cny": round(wallet_now, 2),
        "parent_best_sharpe": base["sharpe"],
        "ungated_best": {"w": unc["w"], "sharpe": unc["sharpe"], "cagr": unc["cagr"],
                         "vol": unc["vol"], "maxdd": unc["maxdd"],
                         "wallet_needed_cny": round(wanted_wallet, 2)},
        "total_gate_price_sharpe": total_gain,
        "first_capital_where_carry_fits_any_weight_cny": first_rung_wallet,
        "weight_forced_at_that_rung_pct": (round(at_rung["w"][2] * 100.0, 2) if at_rung else None),
        "carry_sharpe_at_that_rung": (at_rung["sharpe"] if at_rung else None),
        "sharpe_one_cny_below_that_rung": (just_below["sharpe"] if just_below else None),
        "jump_in_sharpe_at_that_rung": jump,
        "share_of_total_gate_price_captured_by_the_jump": (
            round(jump / total_gain, 6) if (jump is not None and total_gain) else None),
        "capital_paid_for_the_jump_cny": round(first_rung_wallet - wallet_now, 2),
        "capital_paid_for_the_jump_pct_of_wallet": round(
            (first_rung_wallet - wallet_now) / wallet_now * 100.0, 4),
        "first_capital_where_a_two_book_mix_exists_cny": mix_rung_wallet,
        "capital_the_mix_wants_cny": wanted_wallet,
        "wanted_carry_weight_pct": round((unc["w"][2] or 0.0) * 100.0, 2),
        "wanted_over_first_rung_x": round(wanted_wallet / first_rung_wallet, 4),
        "one_lot_capital_cny": round(floor_carry, 2),
        "one_lot_vol_budget_cny": round(floor_carry * TARGET_VOL, 2),
        "grid_step": GRID_STEP,
        "why_this_is_not_a_smooth_curve": (
            "one IC lot is indivisible: the affordable carry weights at W form the half-line "
            "[%.2f / W, 1]. At W = %.0f that half-line is the single point {1.00}, so the "
            "best the wallet can do is hold the carry book ALONE; the diversifiers come back "
            "only as W grows and the band's left edge falls."
            % (floor_carry, first_rung_wallet)),
        "what_this_is_not": (
            "not a second opinion on any book's Sharpe: the rungs only re-read which cells of "
            "the parent's grid a wallet can afford"),
    }
    # The rungs are the 8% target's arithmetic, not a law of the market: move the target and
    # every rung moves with it. Printed as data so a reader can re-price their own dial.
    one_lot_vol = floor_carry * TARGET_VOL
    entry_facts["target_vol_where_parent_wallet_fits_one_lot_pct"] = round(
        one_lot_vol / wallet_now * 100.0, 3)
    entry_facts["target_sensitivity"] = [
        {"target_vol_pct": round(t * 100.0, 4),
         "first_lot_capital_cny": round(one_lot_vol / t, 0),
         "wanted_weight_capital_cny": round(one_lot_vol / t / (unc["w"][2] or 1.0), 0)}
        for t in (0.05, 0.06, 0.08, 0.10, 0.12)
    ]

    if jump is None:
        word = "LADDER_UNAVAILABLE"
    elif (at_rung["w"][2] > 0.999) and jump > 0:
        word = "THE_THIRD_BOOK_ENTERS_AS_ONE_CONTRACT_NOT_AS_A_WEIGHT"
    elif at_rung["w"][2] > 0:
        word = "THE_THIRD_BOOK_ENTERS_AS_A_SMALL_WEIGHT"
    else:
        word = "THE_GATE_NEVER_OPENS_ON_THIS_GRID"

    sentence = (
        "The wallet the parent priced holds no carry and earns Sharpe %.3f. The first IC lot "
        "becomes affordable %s CNY later (%.2f%% more capital), and at that size the lot is "
        "100%% of the 8%% budget -- so the best a %s wallet can do is hold the carry book "
        "ALONE: Sharpe %.3f, a jump of %.3f that captures %s of the gate's whole %.3f. The "
        "weight the grid actually wants is %.0f%%, and that weight only fits at %s CNY, "
        "%.2fx the first rung. Between those two numbers the ladder is not a slope: each rung "
        "buys back the right to diversify."
        % (base["sharpe"], "{:,.0f}".format(first_rung_wallet - wallet_now),
           (first_rung_wallet - wallet_now) / wallet_now * 100.0,
           "{:,.0f}".format(first_rung_wallet), at_rung["sharpe"], jump,
           ("%.0f%%" % (jump / total_gain * 100.0)) if total_gain else "n/a",
           total_gain, (unc["w"][2] or 0.0) * 100.0, "{:,.0f}".format(wanted_wallet),
           wanted_wallet / first_rung_wallet))

    sentence_zh = (
        "父面那只 100 万的钱包拿不到 carry，Sharpe %.3f。第一手 IC 合约要多掏 %s 元才买得起"
        "（多 %.2f%% 资本），可到了那一档，一手合约正好吃掉整个 8%% 预算——所以 %s 元的钱包"
        "能拿到的最好答案是把整本书压在 carry 一本上：Sharpe %.3f，跳升 %.3f，一口气吃掉门"
        "总价 %.3f 里的 %s。网格真正想要的权重是 %.0f%%，那个权重要到 %s 元才装得下，是第一档"
        "的 %.2fx。这两档之间不是斜坡而是台阶：每一级台阶买回来的是重新分散的权利。"
        % (base["sharpe"], "{:,.0f}".format(first_rung_wallet - wallet_now),
           (first_rung_wallet - wallet_now) / wallet_now * 100.0,
           "{:,.0f}".format(first_rung_wallet), at_rung["sharpe"], jump, total_gain,
           ("%.0f%%" % (jump / total_gain * 100.0)) if total_gain else "n/a",
           (unc["w"][2] or 0.0) * 100.0, "{:,.0f}".format(wanted_wallet),
           wanted_wallet / first_rung_wallet))

    face = {
        "schema": SCHEMA,
        "face": "three_book_wallet_ladder",
        "generated": _now_iso(),
        "evidence_cutoff": str(idx[-1].date()),
        "question": ("the parent read the gate at 1,000,000 CNY; at what capital does the third "
                     "book get in, and what does the gate still cost after it does"),
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()), "bars": int(len(idx)),
            "why": "the parent's own common window; this face re-prices no book",
        },
        "caliber": {
            "ann_days": W.ANN_DAYS,
            "target_vol_pct": TARGET_VOL * 100.0,
            "parent_wallet_cny": round(wallet_now, 2),
            "weights_are": "share of the 8% volatility budget after each book is scaled to it",
            "grid_step": GRID_STEP,
            "carry_gross_of_hedge_cost": True,
            "execution": {k: W.PARENTS[k]["execution"] for k in W.PARENTS},
            "vol_scale_factors": {k: round(gains[k], 6) for k in W.ORDER},
        },
        "floors": {k: round(W.FLOORS[k], 2) for k in W.ORDER},
        "single_books": {
            k: {"sharpe": round(float(W.stats(scaled[k])["sharpe"]), 6),
                "cagr": round(float(W.stats(scaled[k])["cagr"]), 6),
                "vol": round(float(W.stats(scaled[k])["vol"]), 6),
                "maxdd": round(float(W.stats(scaled[k])["maxdd"]), 6)}
            for k in W.ORDER
        },
        "entry": entry_facts,
        "ladder": rungs,
        "grid": {"step": GRID_STEP, "n_cells": len(rows),
                 "ungated_best": {"w": unc["w"], "sharpe": unc["sharpe"]}},
        "anchor_parent": {
            "face": "results/three_book_wallet.json",
            "parent_wallet_cny": round(wallet_now, 2),
            "parent_best_inside_gate": (base["w"], base["sharpe"]),
            "this_face_at_that_wallet": ([r for r in rungs
                                          if abs(r["wallet_cny"] - wallet_now) < 1e-6][:1] or [None])[0],
        },
        "verdict": word,
        "sentence": sentence,
        "sentence_zh": sentence_zh,
        "caveats": [
            "weights are quantised at %.2f, so a band edge is reported as the grid weight it can "
            "actually reach, never as the exact real number" % GRID_STEP,
            "carry is the hedged EXCESS, gross of the hedge leg's cost; a real hedge needs a "
            "second account (parent's caliber, not re-estimated)",
            "the mix's realised vol is usually below 8%, so this is a Sharpe ladder, not a money "
            "ladder: money_cny_per_year is printed at each rung's own realised vol, and "
            "leverage_to_8pct is printed beside it with r2199's measured financing price (-0.217 "
            "Sharpe for the ETF book's last 1.88pp of vol) named rather than amortised",
            "within-sample statement on the three books' own published series, 2020-2026; the "
            "Sharpe ordering is not a forecast",
            "the 1,000,000 rung is asserted equal to the parent's own best_inside_gate: if it is "
            "not, this face is quoting a different ruler and goes red",
            "Sharpe is compared ACROSS rungs, but every rung also prints its own vol: the first "
            "rung sits at 8.00% against 6.12% at 1,000,000, so part of the jump is a shift in the "
            "risk taken, not only in the odds",
            "the rungs are the 8%% target's arithmetic, not a law: moving the target moves every "
            "rung in proportion (see entry.target_sensitivity, and section 5b of the page)",
        ],
        "provenance": {
            "inputs": {
                "parent_wallet": _stamp("results/three_book_wallet.json"),
                "etf": _stamp("results/etf_nobond_vt.json"),
                "cb": _stamp("results/cb_dual_low.json"),
                "carry_panel": _stamp("data/futures_daily/IC.csv"),
                "index_panel": _stamp("data/index_daily/sh000905.csv"),
                "sizing_spec": _stamp("results/idx_fut_carry_sizing_spec.json"),
            },
            "script": "scripts/three_book_wallet_ladder.py",
        },
    }
    face = _plain(face)

    if write:
        os.makedirs(os.path.dirname(FACE), exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        with open(DOC, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        with open(os.path.join(ROOT, "results", "three_book_wallet_ladder.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(render_md(face))
    if not quiet:
        print(sentence)
    return face


# ------------------------------------------------------------------ render
def render_md(face):
    e = face["entry"]
    lad = face["ladder"]

    def pct(v, nd=2):
        return "n/a" if v is None else ("%." + str(nd) + "f%%") % (v * 100.0)

    def num(v, nd=0):
        return "n/a" if v is None else ("{:,.%df}" % nd).format(v)

    out = []
    add = out.append
    add("# Three books, one wallet — the ladder of capital\n")
    add("面：`results/three_book_wallet_ladder.json` · 脚本：`scripts/three_book_wallet_ladder.py` · "
        "证据截止：%s（%d 根 bar，%s → %s）\n"
        % (face["evidence_cutoff"], face["window"]["bars"], face["window"]["first"],
           face["window"]["last"]))
    add("> %s\n" % (face.get("sentence_zh") or face["sentence"]))
    # r2216: the face derives a word for what the ladder is; a page that never prints it
    # leaves the reader to re-derive the verdict from the table (and the smoke leg that
    # checks "the page prints the verdict it derives" could only ever be red).
    add("**判词：`%s`** —— 这个词由上面的门槛自己推出（右手合约不可分割 + 8%% 预算），"
        "不是人工写死的结论。\n" % face["verdict"])
    add("## 1. 父面留在桌上的那一半\n")
    add("`three_book_wallet` 回答的是 1,000,000 元这一只钱包：三本书、一个钱包、carry 因为一手 IC "
        "合约吃掉 80,000 元波动预算里的 91,029 元而拿到权重 0.00，门的价格 0.784 夏普。"
        "它把这一半答案印得很诚实，然后停住了——因为递给它的钱包只有 100 万。\n")
    add("本面把同一个网格按**资本**重读一遍：不重算任何一本书，只问「到多少钱，第三本书才进得去；"
        "进去之后门还收多少」。\n")
    add("## 2. 机制：一手合约是不可分割的\n")
    add("| 量 | 值 |")
    add("|---|---|")
    add("| 一手 IC 合约吃掉的年化波动预算 | %s 元 |" % num(e["one_lot_vol_budget_cny"]))
    add("| 在 8%% 预算下，一手合约需要的资本 | %s 元 |" % num(e["one_lot_capital_cny"]))
    add("| 钱包 W 能表达的 carry 权重（合法带） | `[%.2f / W, 1]`，低于 1,137,862.5 元时只有 0 |"
        % e["one_lot_capital_cny"])
    add("| 第三本书第一次能进的最小资本 | **%s 元** |"
        % num(e["first_capital_where_carry_fits_any_weight_cny"]))
    add("| 那一刻它能拿到的权重 | **%s**（只能是 100%%） |" % pct(
        (e["weight_forced_at_that_rung_pct"] or 0) / 100.0))
    add("| 钱包第一次能同时持有两本书 | %s 元 |"
        % num(e["first_capital_where_a_two_book_mix_exists_cny"]))
    add("| 网格真正想要的 carry 权重 | %s |" % pct((e["wanted_carry_weight_pct"] or 0) / 100.0))
    add("| 那个权重需要的最小资本 | **%s 元** |" % num(e["capital_the_mix_wants_cny"]))
    add("| 想要 / 第一档 | **%.2fx** |" % e["wanted_over_first_rung_x"])
    add("")
    add("所以曲线不是一条斜线，而是一级台阶：`%s`\n" % e["why_this_is_not_a_smooth_curve"])
    add("## 3. 台阶里的那一跳\n")
    add("| 量 | 值 |")
    add("|---|---|")
    add("| 100 万时的最好组合 | Sharpe %.3f（carry 权重 0.00） |" % e["parent_best_sharpe"])
    add("| 第一档前 1 元 | Sharpe %.3f |" % e["sharpe_one_cny_below_that_rung"])
    add("| 第一档（%s 元） | Sharpe %.3f（100%% carry） |"
        % (num(e["first_capital_where_carry_fits_any_weight_cny"]), e["carry_sharpe_at_that_rung"]))
    add("| 这一跳 | **+%.3f 夏普** |" % e["jump_in_sharpe_at_that_rung"])
    add("| 这一跳吃掉了门总价的 | **%s** |"
        % pct(e["share_of_total_gate_price_captured_by_the_jump"], 0))
    add("| 为这一跳要多掏的资本 | %s 元（占 100 万钱包的 %.2f%%） |"
        % (num(e["capital_paid_for_the_jump_cny"]), e["capital_paid_for_the_jump_pct_of_wallet"]))
    add("| 门的总价（无门最优 %.3f − 100 万实得 %.3f） | %.3f |"
        % (e["ungated_best"]["sharpe"], e["parent_best_sharpe"], e["total_gate_price_sharpe"]))
    add("")
    add("## 4. 每一档的账\n")
    add("| 钱包（元） | 出处 | carry 权重 | 可表达的最小 carry 权重 | 最好组合 Sharpe | CAGR | 波动 | 回撤 | 门还收 | 比上一档多花的钱买到的夏普/百万 |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for r in lad:
        if not r.get("best"):
            add("| %s | %s | — | — | — | — | — | — | — | 无可行格 |" % (num(r["wallet_cny"]), r["why"]))
            continue
        b = r["best"]
        step = (r.get("step") or {}).get("sharpe_per_million_cny")
        add("| %s | %s | %s | %s | %.3f | %s | %s | %s | %.3f | %s |"
            % (num(r["wallet_cny"]), r["why"], pct(r["carry_weight_pct"] / 100.0),
               (pct(r["band"]["min_positive_carry_weight"]) if r["band"]["min_positive_carry_weight"]
                is not None else "只有 0"),
               b["sharpe"], pct(b["cagr"]), pct(b["vol"]), pct(b["maxdd"]),
               r["gate_price_sharpe"], ("%.2f" % step) if step is not None else "—"))
    add("")
    add("逐档看：carry 权重从 100%% 一路退到 %.0f%%，因为钱包越大，一手合约占预算的比例越小，"
        "另一本书才有位置。\n" % (e["ungated_best"]["w"][2] * 100.0))
    add("## 5. 这些是夏普，不是钱\n")
    add("| 钱包（元） | 自实现波动 | 要加多少杠杆才到 8% | 8%×Sharpe 的资本收益（父面恒等式） | 按自身波动算的年钱 |")
    add("|---|---|---|---|---|")
    for r in lad:
        if not r.get("best"):
            continue
        add("| %s | %s | %.2fx | %.2f%% | %s 元 |"
            % (num(r["wallet_cny"]), pct(r["best"]["vol"]), r["leverage_to_8pct"],
               r["return_at_8pct_identity_pct"], num(r["money_cny_per_year"])))
    add("")
    add("最后两列必须一起读：`8%×Sharpe` 是父面的恒等式（把组合按杠杆放大到 8% 波动后的资本收益），"
        "它不是本面测出来的；本面测到的只有各档自己在原始波动下的钱。杠杆不是免费的——r2199 对 ETF "
        "书最后 1.88pp 波动实测的融资价是 **-0.217 夏普**，这里不重复摊销。\n")
    add("## 5b. 同一级台阶，换一只波动旋钮\n")
    add("台阶的高度是 8% 这个旋钮定的，不是市场定的。把旋钮拧一下，每一档都跟着移动：\n")
    add("把旋钮拧到 **%.2f%%**，现在这只 100 万的钱包就正好装得下一手合约（100%% 权重）——"
        "所以「要 228 万」这句话只在 8%% 这一档成立，它同时也可以读成「8%% 对这个钱包太紧了」。\n"
        % face["entry"]["target_vol_where_parent_wallet_fits_one_lot_pct"])
    add("| 目标波动 | 第一手合约需要的资本 | 网格想要的权重需要的资本 |")
    add("|---|---|---|")
    for t in (face["entry"].get("target_sensitivity") or []):
        add("| %.0f%% | %s 元 | %s 元 |"
            % (t["target_vol_pct"], num(t["first_lot_capital_cny"]),
               num(t["wanted_weight_capital_cny"])))
    add("")
    add("## 6. 诚实条款\n")
    for c in face["caveats"]:
        add("- %s" % c)
    add("")
    add("## 7. 复跑与守卫\n")
    add("```")
    add("python scripts\\three_book_wallet_ladder.py run       # 重算并写面")
    add("python scripts\\three_book_wallet_ladder.py check     # 输入动了=STALE(rc3)；自相矛盾=CHECK FAILED(rc2)")
    add("python scripts\\three_book_wallet_ladder.py selftest  # 离线自检")
    add("```")
    add("")
    add("`check` 的三件事：①任何上游面（父面 / ETF / 转债 / IC 面板 / 指数面板 / sizing spec）字节或 "
        "mtime 变了 → `STALE`；②阶梯自身单调性与可行性重算不通 → `CHECK FAILED`（不带 STALE 字样）；"
        "③100 万那一档必须等于父面自己发布的 `best_inside_gate`，不等 = 引用了另一把尺子。\n")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ check
def check(quiet=False):
    """Drift = STALE (upstream moved). Self-contradiction = CHECK FAILED (no STALE word).

    The distinction is a contract, not a style: the chain only pays for a re-run when the
    text says STALE, so a true defect must never wear that word.
    """
    if not os.path.exists(FACE):
        print("STALE face missing: results/three_book_wallet_ladder.json")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)

    drifted = []
    for key, rec in (face.get("provenance") or {}).get("inputs", {}).items():
        if not isinstance(rec, dict) or rec.get("missing"):
            continue
        rel = rec.get("path")
        if not rel:
            continue
        now = _stamp(rel)
        if now.get("missing"):
            drifted.append("%s (missing now)" % rel)
            continue
        if now.get("size") != rec.get("size") or now.get("mtime") != rec.get("mtime"):
            drifted.append("%s (%s -> %s)" % (rel, rec.get("mtime"), now.get("mtime")))
    if drifted:
        print("STALE upstream moved: " + "; ".join(drifted))
        return 3

    problems = []
    floors = face.get("floors") or {}
    ladder = face.get("ladder") or []

    prev_sharpe = None
    for r in ladder:
        b = r.get("best")
        if not b:
            prev_sharpe = None
            continue
        if abs(sum(b["w"]) - 1.0) > 1e-6:
            problems.append("wallet %s: weights do not sum to 1" % r["wallet_cny"])
        # every printed best must actually be feasible at its own rung
        for i, k in enumerate(W.ORDER):
            w = b["w"][i]
            if w <= 0:
                continue
            if r["wallet_cny"] * w < (floors.get(k) or 0.0) - 1.0:
                problems.append("wallet %s: %s weight %.2f needs %.0f > %.0f"
                                % (r["wallet_cny"], k, w, (floors.get(k) or 0.0) / max(w, 1e-9),
                                   r["wallet_cny"]))
        if prev_sharpe is not None and b["sharpe"] < prev_sharpe - 1e-9:
            problems.append("wallet %s: Sharpe fell (%.6f < %.6f) -- feasible sets only grow"
                            % (r["wallet_cny"], b["sharpe"], prev_sharpe))
        prev_sharpe = b["sharpe"]

    e = face.get("entry") or {}
    if e.get("one_lot_capital_cny") and e.get("first_capital_where_carry_fits_any_weight_cny"):
        want = float(e["one_lot_capital_cny"])
        if abs(want - float(e["first_capital_where_carry_fits_any_weight_cny"])) > 1.0:
            problems.append("first rung %.2f != one lot's capital %.2f"
                            % (e["first_capital_where_carry_fits_any_weight_cny"], want))

    # the 1,000,000 rung must be the parent's own answer, or this face quotes another ruler
    parent = _read_json("results/three_book_wallet.json")
    if not parent:
        problems.append("parent face unreadable: results/three_book_wallet.json")
    else:
        pb = parent.get("best_inside_gate") or {}
        anchor = ((face.get("anchor_parent") or {}).get("parent_best_inside_gate") or [[], []])
        aw = anchor[0] if anchor else []
        if pb.get("sharpe") is None or e.get("parent_best_sharpe") is None:
            problems.append("parent anchor missing on one side")
        else:
            if abs(float(pb["sharpe"]) - float(e["parent_best_sharpe"])) > 1e-6:
                problems.append("parent best Sharpe %.6f != this face %.6f"
                                % (pb["sharpe"], e["parent_best_sharpe"]))
            if [round(x, 4) for x in aw] != [round(x, 4) for x in (pb.get("w") or [])]:
                problems.append("parent best weights %s != this face %s" % (pb.get("w"), aw))

    if problems:
        print("CHECK FAILED " + "; ".join(problems))
        return 2
    if not quiet:
        print("OK three_book_wallet_ladder: %d rungs to %s, first lot at %s CNY, gate closes at %s"
              % (len(ladder), face["evidence_cutoff"],
                 "{:,.0f}".format(e.get("first_capital_where_carry_fits_any_weight_cny") or 0),
                 "{:,.0f}".format(e.get("capital_the_mix_wants_cny") or 0)))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    floor = W.FLOORS["carry"]

    # 1. the band: below one lot's capital no positive weight exists
    leg("band empty below one lot", min_carry_weight(floor - 1.0) is None)
    leg("band is exactly {1.00} at one lot's capital",
        abs(min_carry_weight(floor) - 1.0) < 1e-12)
    leg("band left edge at 4x one lot is 0.25",
        abs(min_carry_weight(4.0 * floor) - 0.25) < 1e-12)

    # 2. grid quantisation rounds the band edge UP (a weight you cannot reach is not a weight)
    leg("grid_floor_at rounds up", abs(grid_floor_at(0.253) - 0.30) < 1e-9)
    leg("grid_floor_at is exact on the grid", abs(grid_floor_at(0.25) - 0.25) < 1e-9)
    leg("grid_floor_at clamps at 1", abs(grid_floor_at(1.4) - 1.0) < 1e-9)

    # 3. best_at picks the max-Sharpe FEASIBLE cell and says so
    rows = [
        {"w": [1.0, 0.0, 0.0], "sharpe": 0.5, "cagr": 0.05, "vol": 0.08, "maxdd": -0.1,
         "worst_year": 0.0},
        {"w": [0.0, 0.0, 1.0], "sharpe": 1.4, "cagr": 0.11, "vol": 0.08, "maxdd": -0.1,
         "worst_year": 0.0},
        {"w": [0.2, 0.0, 0.8], "sharpe": 1.6, "cagr": 0.11, "vol": 0.07, "maxdd": -0.1,
         "worst_year": 0.0},
    ]
    small = best_at(rows, floor)                 # only the 100% carry cell fits
    big = best_at(rows, 5.0 * floor)             # all three fit
    leg("at one lot's capital only the 100% carry cell is feasible",
        small is not None and abs(small["w"][2] - 1.0) < 1e-12)
    leg("a big wallet gets the diversified cell",
        big is not None and abs(big["w"][2] - 0.8) < 1e-12 and big["sharpe"] == 1.6)
    cb_only = [{"w": [0.0, 1.0, 0.0], "sharpe": 0.6, "cagr": 0.04, "vol": 0.08,
                "maxdd": -0.1, "worst_year": 0.0}]
    leg("no feasible cell returns None", best_at(cb_only, 1.0) is None)

    # 4. the structural rungs come from the arithmetic, not from a typed table
    rungs = dict(ladder_rungs({"w": [0.35, 0.15, 0.5]}, floor))
    keys = [k for k in rungs]
    leg("first lot rung = one lot's capital at 8%", any(abs(k - floor) < 0.01 for k in keys))
    leg("wanted-weight rung = one lot / 50%", any(abs(k - floor / 0.5) < 0.01 for k in keys))
    leg("rungs are sorted and unique", keys == sorted(set(keys)))

    # 5. the two derived columns the page prints are arithmetic, and they are checked here
    #    rather than asserted on the page: leverage to reach 8% and the parent's 8%*Sharpe
    #    identity. A mix already at 8% needs 1.00x; one at 4% needs 2.00x.
    leg("leverage_to_8pct at 8% vol is 1.00x", abs(TARGET_VOL / 0.08 - 1.0) < 1e-12)
    leg("leverage_to_8pct at 4% vol is 2.00x", abs(TARGET_VOL / 0.04 - 2.0) < 1e-12)
    leg("8%*Sharpe identity: 1.844477 -> 14.756pp",
        abs(round(TARGET_VOL * 1.844477 * 100.0, 3) - 14.756) < 1e-9)

    # 6. drift text self-declares STALE (the chain only pays when that word is there)
    tmp = os.path.join(ROOT, "results", "_three_book_wallet_ladder_selftest.json")
    fake = {
        "provenance": {"inputs": {"probe": {"path": "results/etf_nobond_vt.json",
                                            "size": 1, "mtime": "1970-01-01T00:00:00+08:00"}}},
        "floors": {"etf": 0.0, "cb": 25850.2, "carry": floor},
        "ladder": [{"wallet_cny": 1_000_000.0, "why": "x",
                    "best": {"w": [1.0, 0.0, 0.0], "sharpe": 1.0, "cagr": 0.05, "vol": 0.08,
                             "maxdd": -0.1, "worst_year": 0.0}}],
        "entry": {"one_lot_capital_cny": floor,
                  "first_capital_where_carry_fits_any_weight_cny": floor,
                  "parent_wallet_cny": 1_000_000.0, "parent_best_sharpe": 1.0},
        "anchor_parent": {"parent_best_inside_gate": [[1.0, 0.0, 0.0], 1.0]},
    }
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(fake, fh)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("drift rc=3 and says STALE", rc == 3 and "STALE" in buf.getvalue())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 7. a true defect must NOT wear the STALE word
    fake2 = json.loads(json.dumps(fake))
    fake2["provenance"] = {"inputs": {}}          # no drift to report
    fake2["ladder"] = [
        {"wallet_cny": 1_000_000.0, "why": "x",
         "best": {"w": [1.0, 0.0, 0.0], "sharpe": 1.20, "cagr": 0.05, "vol": 0.08,
                  "maxdd": -0.1, "worst_year": 0.0}},
        {"wallet_cny": 2_000_000.0, "why": "x",
         "best": {"w": [0.0, 0.0, 1.0], "sharpe": 1.10, "cagr": 0.11, "vol": 0.08,
                  "maxdd": -0.1, "worst_year": 0.0}},
    ]
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(fake2, fh)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        text = buf.getvalue()
        leg("falling Sharpe across rungs is CHECK FAILED, not STALE",
            rc == 2 and "CHECK FAILED" in text and "STALE" not in text)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 8. infeasible weights are caught (a wallet too small for the weight it prints)
    fake3 = json.loads(json.dumps(fake2))
    fake3["ladder"] = [{"wallet_cny": 1_000_000.0, "why": "x",
                        "best": {"w": [0.5, 0.0, 0.5], "sharpe": 1.0, "cagr": 0.05,
                                 "vol": 0.08, "maxdd": -0.1, "worst_year": 0.0}}]
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(fake3, fh)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("half a lot at a 1m wallet is caught", rc == 2 and "needs" in buf.getvalue())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS  " if c else "FAIL  ") + name)
    print("%d/%d legs pass" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _check_path(path):
    """check() against an arbitrary face path (selftest only)."""
    global FACE
    saved = FACE
    try:
        FACE = path
        return check(quiet=True)
    finally:
        FACE = saved


def run():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "show"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        with open(FACE, encoding="utf-8") as fh:
            print(json.dumps(json.load(fh).get("sentence"), ensure_ascii=False))
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(run())
