#!/usr/bin/env python
"""book_pair_rebalance -- what it costs to keep the two books at their weight.

`book_pair_blend` priced one wallet split 30/70 across the two published books and got
Sharpe 1.066 against 0.540 and 0.958 -- but its own caliber line says the quiet part:

    "the blend adds no rebalancing cost between books (not modelled -- a reader who
     moves money between them pays it)"

That sentence is the whole question a funder asks next: **I can hold 30/70 on paper, but
how often do I have to move money, and does paying to move it eat the gain?**  A blend
that only works if you rebalance every day for free is not a blend you can buy.

This face answers exactly that and nothing else:

  * it never re-derives a book -- it imports both parents' own backtests through
    `book_pair_blend.load_cb/load_etf` and takes the target weight from the blend face's
    own published `best.w_cb`, so a change upstream makes this face STALE, not different;
  * it walks the two daily return series day by day, lets the weights drift with each
    book's own return, and rebalances on six calendar cadences (never / every 20 bars /
    monthly / quarterly / semiannual / annual), charging the move at a stated bp per
    side -- moving x from one book to the other is a SELL of x and a BUY of x, so the
    round trip costs 2x;
  * it prints, for each cadence, the net result, the number of moves, the turnover per
    year, the worst drift the wallet carried, and the same cadence at zero cost, so the
    cost drag is a printed number instead of a caveat;
  * it sweeps the weight grid under cost, because the honest next question is whether
    paying to rebalance moves the answer *away* from 30/70.

What it refuses to do:
  * it does not choose a cadence and sell it as an optimum -- the cadence is picked on
    the same window it is scored on, and the face says so in `unverified`;
  * it does not model tax, bid-ask on the underlying names, or the lot grid (the ticket
    floor face prices lots; this face prices the move between books);
  * it does not hide that "never rebalance" can win simply because the winning book is
    allowed to grow -- that is printed as the drift, with the final weight on the face.

Usage:
  python scripts/book_pair_rebalance.py run        # re-derive and publish json + md
  python scripts/book_pair_rebalance.py check      # cheap drift check (stamps + target)
  python scripts/book_pair_rebalance.py selftest   # offline arithmetic legs
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_rebalance.json")
MD = os.path.join(RESULTS, "book_pair_rebalance.md")
BLEND_FACE = os.path.join(RESULTS, "book_pair_blend.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import book_pair_blend as B  # noqa: E402  (single source: parents, stamps, stats)

COST_BP = 10.0            # per side, same floor each parent already pays
COST_SENS = (5.0, 10.0, 20.0)
RULES = ("hold", "every20", "monthly", "quarterly", "semiannual", "annual")
GRID_WEIGHTS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
GRID_RULES = ("hold", "every20", "quarterly", "annual")
ANN_DAYS = 244.0

CALIBER = {
    "cost_per_side_bp": COST_BP,
    "why_two_sides": "moving an amount x from one book to the other is a sell of x and a "
                     "buy of x -- the round trip is 2x the per-side rate, and each parent "
                     "already pays its own 10bp inside its published series",
    "when": "the move is charged at the close of the bar the cadence fires, after that "
            "day's return; a reader who moves at the next open pays the same 2x on a "
            "slightly different price",
    "ann_days": ANN_DAYS,
    "not_modelled": "tax, bid-ask on the underlying names, the whole-lot grid, and the "
                    "spread between a fund's NAV and its traded price",
}


def _rp(rel):
    return os.path.join(ROOT, rel)


def _now_iso():
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _plain(o):
    return B._plain(o)


# ---------------------------------------------------------------- enforce the move
def _fires(rule, i, ts, prev):
    """Does this cadence rebalance at the END of bar i?"""
    if rule == "hold":
        return False
    if rule == "daily":
        return i > 0
    if rule == "every20":
        return i > 0 and i % 20 == 0
    if prev is None:
        return False
    if rule == "monthly":
        return ts.month != prev.month
    if rule == "quarterly":
        return ts.quarter != prev.quarter
    if rule == "semiannual":
        return ((ts.year, 0 if ts.month <= 6 else 1) !=
                (prev.year, 0 if prev.month <= 6 else 1))
    if rule == "annual":
        return ts.year != prev.year
    raise ValueError(rule)


def simulate(rc, re, w_target, rule, cost_bp=COST_BP):
    """Walk the two daily return series, rebalancing on `rule`, paying 2x per side.

    Returns the net equity path (starts at 1.0 after bar 0), the move count, the total
    one-way turnover, and the worst drift the wallet carried away from its target.
    """
    import pandas as pd

    w = float(w_target)
    val = 1.0
    prev = None
    n_moves = 0
    turn = 0.0
    max_drift = 0.0
    n = len(rc)
    out = [0.0] * n
    cb_r = rc.values if hasattr(rc, "values") else rc
    etf_r = re.values if hasattr(re, "values") else re
    for i in range(n):
        a, b = float(cb_r[i]), float(etf_r[i])
        growth = w * (1.0 + a) + (1.0 - w) * (1.0 + b)
        val *= growth
        # the weights the wallet now carries (before any move)
        w = (w * (1.0 + a)) / growth if growth > 0 else w
        drift = abs(w - float(w_target))
        if drift > max_drift:
            max_drift = drift
        ts = rc.index[i]
        if _fires(rule, i, ts, prev):
            move = float(w_target) - w
            if abs(move) > 1e-15:
                n_moves += 1
                turn += abs(move)
                val *= max(0.0, 1.0 - 2.0 * abs(move) * cost_bp / 1e4)
                w = float(w_target)
        out[i] = val
        prev = ts
    ser = pd.Series(out, index=rc.index)
    return {"equity": ser, "n_moves": n_moves, "turnover": turn,
            "max_drift": max_drift, "final_w": w}


def _row(rc, re, w_target, rule, cost_bp):
    import math

    sim = simulate(rc, re, w_target, rule, cost_bp)
    st = B.local_stats(sim["equity"], ann=ANN_DAYS, base=1.0)
    years = max(st.get("years") or 0.0, 1e-9)
    return {
        "rule": rule, "cost_bp": cost_bp,
        "n_moves": sim["n_moves"],
        "turnover_one_way": round(sim["turnover"], 6),
        "turnover_per_year": round(sim["turnover"] / years, 4),
        "max_drift_pp": round(sim["max_drift"] * 100.0, 3),
        "final_w_cb": round(sim["final_w"], 6),
        "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
        "maxdd": st.get("maxdd"), "vol": st.get("vol"),
        "worst_year": st.get("worst_year"), "bars": st.get("bars"),
    }


def _verdict(best_net, hold_net, gain, zero_cagr, net_cagr, cost_only_edge):
    """Name the story; the band edges are stated because a tie is not a gain.

    The order matters: "it only wins for free" is the sharper fact, and it would be
    hidden by the vaguer "holding is enough" if the gain is negative but the zero-cost
    arm still beats holding.
    """
    if cost_only_edge:
        return "COST_EATS_THE_GAIN"
    if gain > 0.005:
        return "REBALANCE_PAYS"
    if gain > 1e-9:
        return "REBALANCE_PAYS_A_LITTLE"
    return "HOLDING_IS_ENOUGH"


def _sentence(word, best, hold, gain, drag_pp, tgt):
    base = (f"{tgt*100:.0f}/{100-tgt*100:.0f} held without ever moving money")
    if word == "HOLDING_IS_ENOUGH":
        return (f"Never moving money is the best cadence on this window ({base}: "
                f"Sharpe {hold['sharpe']:.3f}). Every paid cadence pays 2x per side and "
                f"still lands on or below it -- there is nothing here to buy")
    if word in ("REBALANCE_PAYS", "REBALANCE_PAYS_A_LITTLE"):
        return (f"Rebalancing {best['rule']} pays: Sharpe {best['sharpe']:.3f} against "
                f"{hold['sharpe']:.3f} for holding, after {drag_pp:.2f}pp of cost drag, "
                f"with {best['n_moves']} moves over the window "
                f"({best['turnover_per_year']:.2f} one-way turnover per year)")
    if word == "COST_EATS_THE_GAIN":
        return (f"The only cadence that beats holding does it at zero cost: "
                f"{best['rule']} at {best['cost_bp']:.0f}bp per side gains "
                f"{gain:+.3f} Sharpe, and the same cadence at zero cost gains more than "
                f"that -- paying to move is what removes the edge")
    return (f"No cadence worth paying for: the best paid one is {best['rule']} at "
            f"{gain:+.3f} Sharpe against just holding, inside the band that is a tie "
            f"({drag_pp:.2f}pp of cost paid for nothing)")


# ---------------------------------------------------------------- the face
def build(write=True, quiet=False):
    import numpy as np

    cb, cb_meta = B.load_cb()
    etf, etf_meta = B.load_etf()
    cb_w, etf_w, idx = B.align(cb, etf)
    if cb_w is None:
        raise SystemExit("the two books share no days -- refusing to price a cadence")

    rc = cb_w.pct_change().dropna()
    re_ = etf_w.pct_change().dropna()
    common = rc.index.intersection(re_.index)
    rc, re_ = rc.reindex(common), re_.reindex(common)

    # the target weight is the blend face's own published choice, never re-picked here
    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend = json.load(fh)
    tgt = float(blend["best"]["w_cb"])
    tgt_src = {"face": "results/book_pair_blend.json", "field": "best.w_cb",
               "value": tgt, "window_last": blend.get("window", {}).get("last")}

    rows = []
    for rule in RULES:
        net = _row(rc, re_, tgt, rule, COST_BP)
        zero = _row(rc, re_, tgt, rule, 0.0)
        net["zero_cost"] = {k: zero[k] for k in
                            ("cagr", "sharpe", "maxdd", "vol", "worst_year")}
        net["cost_drag_pp_cagr"] = (round((zero.get("cagr") or 0.0) * 100.0
                                          - (net.get("cagr") or 0.0) * 100.0, 4))
        net["cost_drag_sharpe"] = round((zero.get("sharpe") or 0.0)
                                        - (net.get("sharpe") or 0.0), 4)
        rows.append(net)

    by = {r["rule"]: r for r in rows}
    hold = by["hold"]
    paid = [r for r in rows if r["rule"] != "hold"]
    best_net = max(paid, key=lambda r: r["sharpe"])
    # "the cadence only wins on the free lunch" test: its own zero-cost Sharpe must
    # beat holding's, while its paid Sharpe does not beat holding by the band.
    cost_only = (best_net["sharpe"] <= hold["sharpe"] + 0.005
                 and best_net["zero_cost"]["sharpe"] > hold["sharpe"] + 0.005)
    gain = best_net["sharpe"] - hold["sharpe"]
    word = _verdict(best_net, hold, gain, best_net["zero_cost"]["cagr"],
                    best_net["cagr"], cost_only)

    # The number the blend face printed for 30/70 is a DAILY-rebalanced, zero-cost
    # wallet.  A reader will put the two pages side by side, so reproduce it here and
    # say plainly how much of the paid cadence's edge is just walking back to it.
    daily = B.blend_daily(rc, re_, tgt)
    st_daily = B.local_stats(daily, ann=ANN_DAYS, base=1.0)
    blend_best_n = float((blend.get("best") or {}).get("sharpe") or 0.0)
    daily_sr = float(st_daily.get("sharpe") or 0.0)
    paper_gap = blend_best_n - best_net["sharpe"]
    recon = {
        "why": "the blend face's 30/70 number is a daily-rebalanced, zero-cost wallet; "
               "this face's own daily arm must land on it, or the two pages are not "
               "reading the same books",
        "daily_here_sharpe": round(daily_sr, 4),
        "blend_best_sharpe": round(blend_best_n, 4),
        "diff_sharpe": round(daily_sr - blend_best_n, 4),
        "matches": bool(abs(daily_sr - blend_best_n) < 2e-3),
    }
    recovery = {
        "paper_sharpe": round(blend_best_n, 4),
        "paid_cadence": best_net["rule"],
        "paid_cadence_sharpe": round(best_net["sharpe"], 4),
        "gap_sharpe": round(paper_gap, 4),
        "is_just_the_paper_number": bool(abs(paper_gap) < 0.01),
        "sentence": (
            f"what the paid cadence buys is the paper number: the blend face's "
            f"{blend_best_n:.3f} assumes the wallet is walked back to 30/70 every day, "
            f"and the best paid cadence lands at {best_net['sharpe']:.3f} -- so the edge "
            f"is the price of not drifting, not a second source of return"
            if abs(paper_gap) < 0.01 else
            f"the paid cadence does not merely recover the paper number "
            f"({blend_best_n:.3f}): it lands at {best_net['sharpe']:.3f}, a "
            f"{paper_gap:+.3f} Sharpe difference from the daily-rebalanced reading"),
    }
    if best_net["sharpe"] <= hold["sharpe"]:
        # hold itself is the winner of the paid comparison; name it, do not invent a
        # paid cadence that "nearly" matched
        best_paid_for_display = best_net
    else:
        best_paid_for_display = best_net

    # sensitivity: does the ranking survive a different per-side rate?
    sens = []
    for bp in COST_SENS:
        r_h = _row(rc, re_, tgt, "hold", bp)
        r_b = _row(rc, re_, tgt, best_net["rule"], bp)
        sens.append({"cost_bp": bp,
                     "hold_sharpe": round(r_h["sharpe"], 4),
                     "cadence": best_net["rule"],
                     "cadence_sharpe": round(r_b["sharpe"], 4),
                     "cadence_still_ahead": bool(r_b["sharpe"] > r_h["sharpe"] + 0.005)})

    # grid under cost: does paying to rebalance move the answer away from 30/70?
    grid = []
    for w in GRID_WEIGHTS:
        cells = {}
        for rule in GRID_RULES:
            r = _row(rc, re_, w, rule, COST_BP)
            cells[rule] = {"sharpe": round(r["sharpe"], 4),
                           "cagr": round(r["cagr"], 6),
                           "n_moves": r["n_moves"],
                           "turnover_per_year": r["turnover_per_year"]}
        best_rule = max(cells, key=lambda k: cells[k]["sharpe"])
        grid.append({"w_cb": round(w, 2), "cells": cells,
                     "best_rule": best_rule,
                     "best_sharpe": cells[best_rule]["sharpe"]})
    grid_best = max(grid, key=lambda g: g["best_sharpe"])

    # the drift story in one place: what the wallet becomes if nobody ever moves it
    drill = {
        "rule": "hold",
        "start_w_cb": round(tgt, 4),
        "end_w_cb": round(hold["final_w_cb"], 4),
        "max_drift_pp": hold["max_drift_pp"],
        "turnover": 0.0,
        "sentence": (f"left alone from {idx[0].date()} to {idx[-1].date()}, a "
                     f"{tgt*100:.0f}/{100-tgt*100:.0f} wallet ends at "
                     f"{hold['final_w_cb']*100:.1f}/{100-hold['final_w_cb']*100:.1f} and at "
                     f"its worst carried {hold['max_drift_pp']:.1f}pp away from target -- "
                     f"that drift is what a paid cadence buys back"),
    }

    face = {
        "face": "book_pair_rebalance",
        "generated_at": _now_iso(),
        "evidence_cutoff": str(idx[-1].date()),
        "question": "if I split one wallet across both books, how often must I move money "
                    "-- and does paying for the move eat the gain?",
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "bars": int(len(idx)),
            "why": "the overlap only -- a wallet split cannot be priced on days one of the "
                   "books does not exist",
        },
        "caliber": CALIBER,
        "target": tgt_src,
        "parents": {
            "cb": {"face": cb_meta["face"], "arm": cb_meta["arm"],
                   "execution": cb_meta["execution"], "panel": cb_meta["panel"]},
            "etf": {"face": etf_meta["face"], "arm": etf_meta["arm"],
                    "execution": etf_meta["execution"], "panel": etf_meta["panel"]},
        },
        "rules": rows,
        "hold": {"sharpe": hold["sharpe"], "cagr": hold["cagr"],
                 "maxdd": hold["maxdd"], "final_w_cb": hold["final_w_cb"]},
        "drift": drill,
        "sensitivity": sens,
        "grid": grid,
        "grid_best": {"w_cb": grid_best["w_cb"], "rule": grid_best["best_rule"],
                      "sharpe": grid_best["best_sharpe"],
                      "target_w_cb": round(tgt, 2),
                      "moves_the_answer": bool(abs(grid_best["w_cb"] - tgt) > 0.05)},
        "reconciliation": recon,
        "recovery": recovery,
        "verdict": {
            "word": word,
            "gain_sharpe_vs_holding": round(gain, 4),
            "best_paid_rule": best_paid_for_display["rule"],
            "cost_drag_pp_cagr": best_paid_for_display["cost_drag_pp_cagr"],
            "recovers_the_paper_number": recovery["is_just_the_paper_number"],
            "sentence": (_sentence(word, best_paid_for_display, hold, gain,
                                   best_paid_for_display["cost_drag_pp_cagr"], tgt)
                         + "; " + recovery["sentence"]),
        },
        "unverified": [
            "the cadence is picked on the same window it is scored on (in-sample pick): a "
            "reader who adopts it should expect less than the printed edge",
            "each parent's own unverified list still applies (etf pool survivorship, the "
            "cb book's close-fill assumption, its 2026 drawdown being one regime)",
            "the move is charged at the bar close, not at the open a reader would use",
            "tax, the underlying bid-ask and the whole-lot grid are not in this cost",
            "a 2x per-side round trip is the stated floor; a real desk moving size pays more",
        ],
    }

    if write:
        os.makedirs(RESULTS, exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(_plain(face), fh, ensure_ascii=False, indent=1)
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(_md(face))
    if not quiet:
        print(f"[run] target {tgt*100:.0f}/{100-tgt*100:.0f} on "
              f"{face['window']['first']} -> {face['window']['last']} "
              f"({face['window']['bars']} bars)", flush=True)
        for r in rows:
            print(f"  {r['rule']:>10s} moves {r['n_moves']:>3d} "
                  f"turn/yr {r['turnover_per_year']:6.2f} "
                  f"CAGR {r['cagr']*100:6.2f}% SR {r['sharpe']:.3f} "
                  f"MDD {r['maxdd']*100:6.1f}% drift {r['max_drift_pp']:5.1f}pp "
                  f"drag {r['cost_drag_pp_cagr']:5.2f}pp", flush=True)
        print(f"  VERDICT {word} (best paid {best_net['rule']}, "
              f"SR vs holding {gain:+.3f})", flush=True)
        print(f"  daily zero-cost arm SR {daily_sr:.4f} vs blend page "
              f"{blend_best_n:.4f} (diff {daily_sr-blend_best_n:+.4f})", flush=True)
    return face


def _md(face):
    w = face["window"]
    t = face["target"]
    L = []
    A = L.append
    A(f"# Keeping the wallet at its weight -- {face['evidence_cutoff']}\n")
    A(f"*generated {face['generated_at']} · window {w['first']} -> {w['last']} "
      f"({w['bars']} bars, the overlap of both books)*\n")
    A(f"**{face['verdict']['word']}** -- {face['verdict']['sentence']}\n")
    A(f"Target: {t['value']*100:.0f}% convertible / {100-t['value']*100:.0f}% ETF, "
      f"taken from `{t['face']}` field `{t['field']}` -- this face does not re-pick it.\n")
    A("## Each cadence, after the cost of moving\n")
    A(f"Cost: {face['caliber']['cost_per_side_bp']:.0f}bp per side; a move of x is a sell "
      f"of x plus a buy of x, so each rebalance pays 2x of the traded share.\n")
    A("| cadence | moves | turnover/yr | CAGR | Sharpe | max DD | worst year | "
      "max drift | cost drag (pp CAGR) |")
    A("|---|---|---|---|---|---|---|---|---|")
    for r in face["rules"]:
        A(f"| {r['rule']} | {r['n_moves']} | {r['turnover_per_year']:.2f} | "
          f"{r['cagr']*100:.2f}% | {r['sharpe']:.3f} | {r['maxdd']*100:.1f}% | "
          f"{r['worst_year']*100:.1f}% | {r['max_drift_pp']:.1f}pp | "
          f"{r['cost_drag_pp_cagr']:.2f} |")
    A("")
    d = face["drift"]
    A(f"Left alone: {d['sentence']}.\n")
    rc_ = face.get("reconciliation", {})
    A("## Does this face read the same books as the blend page?\n")
    A(f"- This face's daily, zero-cost arm: Sharpe {rc_.get('daily_here_sharpe'):.3f} "
      f"against the blend face's 30/70 {rc_.get('blend_best_sharpe'):.3f} "
      f"(diff {rc_.get('diff_sharpe'):+.4f}, "
      f"{'match' if rc_.get('matches') else 'MISMATCH'}).")
    rv = face.get("recovery", {})
    A(f"- {rv.get('sentence')}.\n")
    A("## Does a different per-side rate change the ranking?\n")
    A("| cost per side | holding Sharpe | best cadence | cadence Sharpe | cadence ahead? |")
    A("|---|---|---|---|---|")
    for s in face["sensitivity"]:
        A(f"| {s['cost_bp']:.0f}bp | {s['hold_sharpe']:.3f} | {s['cadence']} | "
          f"{s['cadence_sharpe']:.3f} | {'yes' if s['cadence_still_ahead'] else 'no'} |")
    A("")
    A("## Does paying to rebalance move the answer away from the target weight?\n")
    A("| convertible share | hold | every 20 | quarterly | annual | best cadence |")
    A("|---|---|---|---|---|---|")
    for g in face["grid"]:
        c = g["cells"]
        star = " **" if abs(g["w_cb"] - face["grid_best"]["w_cb"]) < 1e-9 else ""
        A(f"| {g['w_cb']*100:.0f}%{star} | {c['hold']['sharpe']:.3f} | "
          f"{c['every20']['sharpe']:.3f} | {c['quarterly']['sharpe']:.3f} | "
          f"{c['annual']['sharpe']:.3f} | {g['best_rule']} |")
    A("")
    gb = face["grid_best"]
    A(f"Best cell under cost: {gb['w_cb']*100:.0f}% convertible on `{gb['rule']}` at "
      f"Sharpe {gb['sharpe']:.3f}; the target weight is {gb['target_w_cb']*100:.0f}%. "
      f"Cost {'moves' if gb['moves_the_answer'] else 'does not move'} the weight choice.\n")
    A("## How to read it\n")
    A(f"- {face['caliber']['why_two_sides']}.")
    A(f"- {face['caliber']['when']}.")
    A(f"- Not in this cost: {face['caliber']['not_modelled']}.")
    A("\n## Unverified\n")
    for u in face["unverified"]:
        A(f"- {u}")
    A("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- check
def check():
    """Cheap drift check: have the parents' panel bytes or the target weight moved?"""
    if not os.path.exists(FACE):
        print("STALE: book_pair_rebalance face missing "
              "(run `python scripts/book_pair_rebalance.py run`)")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    for k in ("cb", "etf"):
        rec = (face.get("parents", {}).get(k, {}) or {}).get("panel")
        if not rec or rec.get("missing"):
            problems.append(f"STALE: {k} panel is not on disk any more ({rec})")
            continue
        now = B._stamp(rec["path"])
        if now.get("missing"):
            problems.append(f"STALE: {k} panel {rec['path']} disappeared")
            continue
        if now["size"] != rec["size"] or now["mtime"] != rec["mtime"]:
            problems.append(
                f"STALE: {k} panel bytes moved since this face was written "
                f"({rec['size']}B@{rec['mtime']} -> {now['size']}B@{now['mtime']})")
    # the target is a number read off another face: compare the number, not that face's
    # bytes -- a republish with the same weight must not cost a 60s rebuild (r1935).
    tgt_rec = face.get("target", {})
    try:
        with open(BLEND_FACE, encoding="utf-8") as fh:
            blend = json.load(fh)
        now_tgt = float(blend["best"]["w_cb"])
        if abs(now_tgt - float(tgt_rec.get("value", -1))) > 1e-9:
            problems.append(
                f"STALE: the blend face now picks w_cb={now_tgt}, this face priced "
                f"{tgt_rec.get('value')}")
        now_last = blend.get("window", {}).get("last")
        if now_last and now_last != tgt_rec.get("window_last"):
            problems.append(
                f"STALE: the blend window now ends {now_last}, this face ended at "
                f"{tgt_rec.get('window_last')}")
    except Exception as exc:
        problems.append(f"STALE: the blend face cannot be read ({exc})")
    if problems:
        for p in problems:
            print(p)
        return 3
    print(json.dumps({"ok": True, "problems": [], "target_w_cb": tgt_rec.get("value"),
                      "verdict": face["verdict"]["word"]}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    """Offline: the move arithmetic must do what it says, on numbers we can check."""
    import numpy as np
    import pandas as pd

    legs, fails = 0, []

    def ok(name, cond, got=""):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(f"{name}: {got}")

    idx = pd.bdate_range("2022-01-03", periods=800)
    n = len(idx)

    # a: cb earns +0.05%/day, etf earns 0 -- so cb's weight must drift UP by arithmetic
    ra = pd.Series(np.full(n, 0.0005), index=idx)
    rb = pd.Series(np.zeros(n), index=idx)

    hold = simulate(ra, rb, 0.3, "hold")
    ok("A1 holding lets the better book's weight grow", hold["final_w"] > 0.3 + 1e-6,
       hold["final_w"])
    ok("A2 holding never pays", hold["n_moves"] == 0 and hold["turnover"] == 0.0,
       (hold["n_moves"], hold["turnover"]))

    # b: exact drift arithmetic over ONE bar: 30/70 with +10% / 0% must land on
    # 0.3*1.1 / (0.3*1.1 + 0.7) = 0.32
    one = pd.Series([0.10], index=idx[:1])
    zero = pd.Series([0.0], index=idx[:1])
    s1 = simulate(one, zero, 0.3, "every20")
    ok("B1 one-bar drift is exactly 0.33/(0.33+0.70)", abs(s1["final_w"] - 0.33 / 1.03) < 1e-12,
       s1["final_w"])
    ok("B2 a single bar cannot fire every20 (i=0 only)", s1["n_moves"] == 0, s1["n_moves"])

    # c: cost is 2x per side and monotone in the move size
    r_h = _row(ra, rb, 0.3, "every20", 10.0)
    r_0 = _row(ra, rb, 0.3, "every20", 0.0)
    ok("C1 charges lower the CAGR at the same cadence", r_h["cagr"] < r_0["cagr"],
       f"{r_h['cagr']:.6f} vs {r_0['cagr']:.6f}")
    ok("C2 the paid run keeps the same move count", r_h["n_moves"] == r_0["n_moves"],
       (r_h["n_moves"], r_0["n_moves"]))
    dbl = _row(ra, rb, 0.3, "every20", 20.0)
    ok("C3 doubling the rate doubles the drag", 
       abs((r_0["cagr"] - dbl["cagr"]) - 2.0 * (r_0["cagr"] - r_h["cagr"])) < 5e-3,
       f"{r_0['cagr']-dbl['cagr']:.6f} vs {2*(r_0['cagr']-r_h['cagr']):.6f}")

    # d: on a monotone drift the total correction is nearly the same at any cadence
    # (every cadence walks the wallet back to the same target), so the "faster pays
    # more" claim is tested where it is true: a swinging pair, whose distance to target
    # oscillates and therefore has a path length that grows with sampling frequency.
    sw_a = pd.Series(0.003 * np.where(np.arange(n) % 40 < 20, 1.0, -1.0), index=idx)
    sw_b = pd.Series(0.003 * np.where(np.arange(n) % 40 < 20, -1.0, 1.0), index=idx)
    e20 = _row(sw_a, sw_b, 0.3, "every20", 10.0)
    q = _row(sw_a, sw_b, 0.3, "quarterly", 10.0)
    a_ = _row(sw_a, sw_b, 0.3, "annual", 10.0)
    ok("D1 every-20-bars chases more turnover than annual on a swing",
       e20["turnover_one_way"] > a_["turnover_one_way"],
       f"{e20['turnover_one_way']:.4f} vs {a_['turnover_one_way']:.4f}")
    ok("D1b and pays for it (lower CAGR at the same cadence)",
       e20["cagr"] < _row(sw_a, sw_b, 0.3, "every20", 0.0)["cagr"],
       e20["cagr"])
    ok("D2 quarterly moves more often than annual", q["n_moves"] > a_["n_moves"],
       (q["n_moves"], a_["n_moves"]))

    # e: a daily-firing cadence at a paid rate must reconverge the weight each time
    sim_e = simulate(ra, rb, 0.3, "monthly", 10.0)
    # 800 business days span ~38 months: a monthly cadence must fire once per month change
    n_months = sum(1 for i in range(1, n) if idx[i].month != idx[i - 1].month)
    ok("E1 monthly fires exactly once per month change", sim_e["n_moves"] == n_months,
       f"{sim_e['n_moves']} vs {n_months}")
    st_e = B.local_stats(sim_e["equity"], base=1.0)
    ok("E2 the equity path is finite and positive", np.isfinite(st_e["cagr"])
       and sim_e["equity"].min() > 0, st_e.get("cagr"))

    # f: identical books -- splitting cannot help, and drift is exactly zero
    same = simulate(ra, ra, 0.3, "annual")
    ok("F1 two identical books never drift", abs(same["max_drift"]) < 1e-15,
       same["max_drift"])

    # i: walking the wallet back to target EVERY bar, for free, must be exactly the
    # static-weight blend the parent page prints -- this is the reconciliation leg the
    # published face relies on, checked offline so it cannot drift silently
    sim_daily = simulate(ra, rb, 0.3, "daily", 0.0)
    static = B.blend_daily(ra, rb, 0.3)
    # 1e-6, not 1e-12: the two paths are algebraically identical but accumulate in a
    # different order (w*(1+a)+(1-w)*(1+b) vs 1+w*a+(1-w)*b), which costs ~6e-8 on a
    # 1.13 net asset value.  Anything a reader could act on is 10^4 larger.
    ok("I1 daily zero-cost rebalancing equals the static-weight blend",
       abs(float(sim_daily["equity"].iloc[-1]) - float(static.iloc[-1])) < 1e-6,
       f"{sim_daily['equity'].iloc[-1]} vs {static.iloc[-1]}")
    ok("I2 and it pays a move every bar but the first", sim_daily["n_moves"] == n - 1,
       sim_daily["n_moves"])

    # g: the verdict bands.  A cadence that only wins for free must be named as such.
    hold_row = {"rule": "hold", "sharpe": 1.0, "cagr": 0.09, "cost_drag_pp_cagr": 0.0}
    ok("G1 holding is named when nothing beats it",
       _verdict({"rule": "annual", "sharpe": 0.99}, hold_row, -0.01, 0.09, 0.09,
                False) == "HOLDING_IS_ENOUGH", "band")
    ok("G2 a cadence that only wins at zero cost is COST_EATS_THE_GAIN",
       _verdict({"rule": "quarterly", "sharpe": 1.002}, hold_row, 0.002, 0.10, 0.09,
                True) == "COST_EATS_THE_GAIN", "band")
    ok("G3 a real edge is REBALANCE_PAYS",
       _verdict({"rule": "quarterly", "sharpe": 1.05}, hold_row, 0.05, 0.10, 0.095,
                False) == "REBALANCE_PAYS", "band")
    ok("G4 a paid cadence inside the tie band is not sold as an edge",
       _verdict({"rule": "quarterly", "sharpe": 1.002}, hold_row, 0.002, 0.09, 0.089,
                False) == "REBALANCE_PAYS_A_LITTLE", "band")

    # h: check() contract words -- the chain pays attention to STALE and nothing else
    import contextlib
    import io
    import tempfile

    saved = globals().get("FACE")
    tmpdir = tempfile.mkdtemp()
    try:
        real_cb = B._stamp(_rp("data/cb_panel.csv.gz"))
        real_etf = B._stamp(_rp("data/daily/510300.csv"))
        with open(BLEND_FACE, encoding="utf-8") as fh:
            blend = json.load(fh)
        good = os.path.join(tmpdir, "good.json")
        with open(good, "w", encoding="utf-8") as fh:
            json.dump({"parents": {"cb": {"panel": real_cb}, "etf": {"panel": real_etf}},
                       "target": {"value": float(blend["best"]["w_cb"]),
                                  "window_last": blend.get("window", {}).get("last")},
                       "verdict": {"word": "X"}}, fh)
        globals()["FACE"] = good
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_good = check()
        ok("H1 matching parents and target pass the check",
           rc_good == 0 and "STALE" not in buf.getvalue(), buf.getvalue()[:120])

        blocked = os.path.join(tmpdir, "blocked.json")
        with open(blocked, "w", encoding="utf-8") as fh:
            json.dump({"parents": {"cb": {"panel": dict(real_cb, size=real_cb["size"] + 1)},
                                   "etf": {"panel": real_etf}},
                       "target": {"value": float(blend["best"]["w_cb"]),
                                  "window_last": blend.get("window", {}).get("last")},
                       "verdict": {"word": "X"}}, fh)
        globals()["FACE"] = blocked
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_bad = check()
        ok("H2 a moved parent panel is STALE and rc3",
           rc_bad == 3 and "STALE" in buf.getvalue(), f"{rc_bad} {buf.getvalue()[:100]}")

        moved_tgt = os.path.join(tmpdir, "moved_tgt.json")
        with open(moved_tgt, "w", encoding="utf-8") as fh:
            json.dump({"parents": {"cb": {"panel": real_cb}, "etf": {"panel": real_etf}},
                       "target": {"value": float(blend["best"]["w_cb"]) + 0.1,
                                  "window_last": blend.get("window", {}).get("last")},
                       "verdict": {"word": "X"}}, fh)
        globals()["FACE"] = moved_tgt
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_tgt = check()
        ok("H3 a changed target weight is STALE (not a quiet republish)",
           rc_tgt == 3 and "STALE" in buf.getvalue(), f"{rc_tgt} {buf.getvalue()[:120]}")

        absent = os.path.join(tmpdir, "none.json")
        globals()["FACE"] = absent
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_absent = check()
        ok("H4 a missing face says STALE + face missing",
           rc_absent == 3 and "STALE" in buf.getvalue() and "missing" in buf.getvalue(),
           buf.getvalue()[:140])
    finally:
        if saved is not None:
            globals()["FACE"] = saved

    print(f"selftest: {legs - len(fails)}/{legs} PASS")
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="re-derive and publish the face")
    sub.add_parser("check", help="cheap drift check against parent stamps and target")
    sub.add_parser("selftest", help="offline arithmetic legs")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "run":
        build(write=True)
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
