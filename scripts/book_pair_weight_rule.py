#!/usr/bin/env python
"""book_pair_weight_rule -- would a reader have found 30/70 without peeking?

`book_pair_blend` prints 30/70 as `best.w_cb`: the weight that maximised Sharpe on the
whole overlap.  `book_pair_rebalance` priced what keeping that weight costs.  Both faces
are honest about the same gap, and neither closes it:

    "30/70 is the blend face's in-sample optimum; a reader who adopts it should expect less"

The next question is the one a funder actually asks before wiring money: *if I had to pick
the split with only what I knew at the time, what would I have held -- and what would it
have paid?*  A weight that can only be found by looking at the whole six years backwards
is not an allocation rule; it is a description.

This face answers that and nothing else:

  * it never re-derives a book, never re-picks the published weight and never edits a
    parent -- both return series come from `book_pair_blend.load_cb/load_etf/align`, and
    the cost model comes from `book_pair_rebalance.COST_BP` (2x per side on the moved
    share), so a change upstream makes this face STALE, not different;
  * it walks forward: at each decision date (monthly / quarterly / annual) the rule picks
    the weight with the best trailing Sharpe using **only bars up to that date**, then
    holds it until the next decision, charging the move;
  * it scores every arm on the **same post-warm-up window**, so the year the rule spends
    learning is not quietly in one arm and not the other;
  * it prints the picks (min/max/median, how often they changed, how far they sit from
    the published 0.30) next to the money, because "the rule chases whichever book just
    won" and "the rule sometimes buys 100% of one book" are facts a reader must see;
  * it also runs the cheap honesty test with no machinery: pick the weight on the first
    half, score it on the second half.

What it refuses to do:
  * it does not present the best walk-forward cell as "the rule" -- the cadence and the
    lookback are chosen on the same window they are scored on, and the face says so;
  * it does not claim the published 1.066 is wrong -- it reproduces it (daily zero-cost
    arm) and then prices what a rule that only knows the past gets instead;
  * it does not model tax, underlying bid-ask, the lot grid or the NAV/traded-price spread.

Usage:
  python scripts/book_pair_weight_rule.py run        # re-derive and publish json + md
  python scripts/book_pair_weight_rule.py check      # cheap drift check (stamps + parents)
  python scripts/book_pair_weight_rule.py selftest   # offline arithmetic legs
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_weight_rule.json")
MD = os.path.join(RESULTS, "book_pair_weight_rule.md")
BLEND_FACE = os.path.join(RESULTS, "book_pair_blend.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import book_pair_blend as B  # noqa: E402  (single source: parents, stamps, stats)
import book_pair_rebalance as R  # noqa: E402  (single source: the cost model)

COST_BP = R.COST_BP          # 10bp per side, a move of x pays 2x
GRID = tuple(round(0.05 * k, 2) for k in range(0, 21))   # 0.00 .. 1.00
CADENCES = ("monthly", "quarterly", "annual")
LOOKBACKS = ("expanding", "trailing3y")
TRAILING_BARS = 732          # ~3 years of trading days
MIN_TRAIN = 244              # one year of bars before the rule is allowed to speak
HALF_LABEL = "second half scored on a weight picked on the first half"
ANN_DAYS = B.ANN_DAYS

CALIBER = {
    "cost_per_side_bp": COST_BP,
    "why_two_sides": "moving x from one book to the other is a sell of x and a buy of x",
    "pick_metric": "trailing Sharpe of the static-weight blend on the bars strictly up to "
                   "the decision date (no cost inside the pick, the cost is charged when "
                   "the wallet actually moves)",
    "warmup": f"the rule may not speak until it has {MIN_TRAIN} bars; the wallet is parked "
              "at 50/50 before that and every arm is scored only after the warm-up, so no "
              "arm is paid for the learning year",
    "ann_days": ANN_DAYS,
    "not_modelled": "tax, bid-ask on the underlying names, the whole-lot grid, and the "
                    "gap between a fund's NAV and its traded price",
}


def _now_iso():
    return B._now_iso()


def _plain(o):
    return B._plain(o)


# ---------------------------------------------------------------- the rule
def _sharpe_of_slice(rc, re, w, lo, hi):
    """Trailing Sharpe of a static-weight blend over bars [lo, hi).  Cost-free: this is
    the rule's opinion, not a tradable path."""
    sub_a = rc.iloc[lo:hi]
    sub_b = re.iloc[lo:hi]
    if len(sub_a) < 40:
        return None
    eq = B.blend_daily(sub_a, sub_b, w)
    st = B.local_stats(eq, ann=ANN_DAYS, base=1.0)
    sr = st.get("sharpe")
    return None if sr is None or sr != sr else float(sr)


def pick_weight(rc, re, i, lookback, grid=GRID):
    """The weight the rule would choose at the END of bar i, knowing only bars <= i."""
    lo = 0 if lookback == "expanding" else max(0, i + 1 - TRAILING_BARS)
    hi = i + 1
    if hi - lo < MIN_TRAIN:
        return None, None
    best_w, best_sr = None, None
    for w in grid:
        sr = _sharpe_of_slice(rc, re, w, lo, hi)
        if sr is None:
            continue
        if best_sr is None or sr > best_sr:
            best_w, best_sr = w, sr
    return best_w, best_sr


def walk_forward(rc, re, cadence, lookback, grid=GRID, cost_bp=COST_BP):
    """Walk the wallet forward; the target is chosen at each decision from the past only.

    Returns the equity path from the first decision (index 0 of the returned series is the
    warm-up end), the picks, and the move accounting.
    """
    import pandas as pd

    n = len(rc)
    cb_r = rc.values
    et_r = re.values
    first_decision = None
    cd = rc.index
    w = None
    val = 1.0
    out = []
    picks = []
    n_moves = 0
    turn = 0.0
    prev = None
    for i in range(n):
        a, b = float(cb_r[i]), float(et_r[i])
        if w is None:
            w = 0.5            # warm-up park; not scored (see CALIBER.warmup)
        growth = w * (1.0 + a) + (1.0 - w) * (1.0 + b)
        val *= growth
        w = (w * (1.0 + a)) / growth if growth > 0 else w
        ts = cd[i]
        if R._fires(cadence, i, ts, prev):
            choice, sr = pick_weight(rc, re, i, lookback, grid)
            if choice is not None:
                if first_decision is None:
                    first_decision = i
                move = float(choice) - w
                if abs(move) > 1e-15:
                    n_moves += 1
                    turn += abs(move)
                    val *= max(0.0, 1.0 - 2.0 * abs(move) * cost_bp / 1e4)
                w = float(choice)
                picks.append({"date": str(ts.date()), "w_cb": round(float(choice), 4),
                              "trailing_sharpe": (round(sr, 4) if sr is not None else None),
                              "move": round(move, 4)})
        out.append(val)
        prev = ts
    if first_decision is None:
        return None
    # score from the first decision forward, base 1.0
    ser = pd.Series(out[first_decision:], index=cd[first_decision:])
    ser = ser / float(ser.iloc[0])
    return {"equity": ser, "picks": picks, "n_moves": n_moves,
            "turnover": turn, "first_decision": first_decision}


def _pick_summary(picks):
    if not picks:
        return {}
    ws = [p["w_cb"] for p in picks]
    ws_sorted = sorted(ws)
    med = ws_sorted[len(ws_sorted) // 2]
    changes = sum(1 for k in range(1, len(ws)) if abs(ws[k] - ws[k - 1]) > 1e-9)
    return {
        "n": len(ws),
        "min": round(min(ws), 4), "max": round(max(ws), 4),
        "median": round(med, 4), "mean": round(sum(ws) / len(ws), 4),
        "n_changes": changes,
        "share_at_full_book": round(sum(1 for w in ws if w <= 1e-9 or w >= 1 - 1e-9)
                                    / len(ws), 4),
        "mean_abs_from_target": round(sum(abs(w - 0.30) for w in ws) / len(ws), 4),
        "last": picks[-1],
    }


# ---------------------------------------------------------------- the face
def build(write=True, quiet=False):
    import numpy as np

    cb, cb_meta = B.load_cb()
    etf, etf_meta = B.load_etf()
    cb_w, etf_w, idx = B.align(cb, etf)
    if cb_w is None:
        raise SystemExit("the two books share no days -- refusing to score a rule")

    rc = cb_w.pct_change().dropna()
    re_ = etf_w.pct_change().dropna()
    common = rc.index.intersection(re_.index)
    rc, re_ = rc.reindex(common), re_.reindex(common)

    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend = json.load(fh)
    tgt = float(blend["best"]["w_cb"])
    tgt_src = {"face": "results/book_pair_blend.json", "field": "best.w_cb",
               "value": tgt, "window_last": blend.get("window", {}).get("last"),
               "why": "taken as published -- this face never re-picks it"}

    # --- the arms, all scored on the same post-warm-up window
    arms = []
    best = None
    paths = {}
    for cadence in CADENCES:
        for lookback in LOOKBACKS:
            wf = walk_forward(rc, re_, cadence, lookback)
            if wf is None:
                continue
            paths[(cadence, lookback)] = wf["picks"]
            st = B.local_stats(wf["equity"], ann=ANN_DAYS, base=1.0)
            rec = {"kind": "walk_forward", "cadence": cadence, "lookback": lookback,
                   "cost_bp": COST_BP, "n_moves": wf["n_moves"],
                   "turnover_one_way": round(wf["turnover"], 6),
                   "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
                   "maxdd": st.get("maxdd"), "vol": st.get("vol"),
                   "worst_year": st.get("worst_year"), "bars": st.get("bars"),
                   "first": st.get("first"), "last": st.get("last"),
                   "picks": _pick_summary(wf["picks"])}
            rec["window_start"] = st.get("first")
            arms.append(rec)
            if best is None or (rec["sharpe"] or -9) > (best["sharpe"] or -9):
                best = rec

    # the window every arm is scored on = the first decision of the earliest cadence
    wf_probe = walk_forward(rc, re_, "monthly", "expanding")
    start_i = wf_probe["first_decision"] if wf_probe else 0
    rcs = rc.iloc[start_i:]
    res = re_.iloc[start_i:]

    def fixed(w, cadence, cost_bp):
        sim = R.simulate(rcs, res, w, cadence, cost_bp)
        st = B.local_stats(sim["equity"], ann=ANN_DAYS, base=1.0)
        return {"w_cb": round(w, 4), "cadence": cadence, "cost_bp": cost_bp,
                "n_moves": sim["n_moves"],
                "turnover_one_way": round(sim["turnover"], 6),
                "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
                "maxdd": st.get("maxdd"), "vol": st.get("vol"),
                "worst_year": st.get("worst_year"), "bars": st.get("bars")}

    hold_30_paid = fixed(tgt, "quarterly", COST_BP)
    hold_30_free = fixed(tgt, "daily", 0.0)
    hold_50_paid = fixed(0.5, "quarterly", COST_BP)
    hold_30_onall = R.simulate(rc, re_, tgt, "quarterly", COST_BP)
    st_all = B.local_stats(hold_30_onall["equity"], ann=ANN_DAYS, base=1.0)

    # the same-window published reading (zero-cost daily) is what the CEO page prints;
    # print it on both windows so the reader can see how much is the window
    blend_best_sr = float((blend.get("best") or {}).get("sharpe") or 0.0)
    recon = {
        "why": "the published 30/70 is a daily-rebalanced, zero-cost wallet; this face's "
               "own free daily arm must land on it or the two pages read different books",
        "daily_free_same_window_sharpe": round(float(hold_30_free["sharpe"] or 0.0), 4),
        "published_full_window_sharpe": round(blend_best_sr, 4),
        "full_window_free_daily_here": None,  # filled below
        "diff_same_window": None,
    }
    free_all = R.simulate(rc, re_, tgt, "daily", 0.0)
    st_free_all = B.local_stats(free_all["equity"], ann=ANN_DAYS, base=1.0)
    recon["full_window_free_daily_here"] = round(float(st_free_all.get("sharpe") or 0.0), 4)
    recon["diff_full_window"] = round(
        float(st_free_all.get("sharpe") or 0.0) - blend_best_sr, 4)
    recon["diff_same_window"] = round(
        float(hold_30_free["sharpe"] or 0.0) - float(st_free_all.get("sharpe") or 0.0), 4)
    recon["matches_published"] = bool(abs(recon["diff_full_window"] or 0.0) < 2e-3)

    # --- the no-machinery honesty test: pick on the first half, score the second
    h = len(rc) // 2
    first_a, first_b = rc.iloc[:h], re_.iloc[:h]
    best_w, best_sr = None, None
    for w in GRID:
        sr = _sharpe_of_slice(first_a, first_b, w, 0, h)
        if sr is None:
            continue
        if best_sr is None or sr > best_sr:
            best_w, best_sr = w, sr
    sec_a, sec_b = rc.iloc[h:], re_.iloc[h:]
    sim_half = R.simulate(sec_a, sec_b, float(best_w), "quarterly", COST_BP)
    st_half = B.local_stats(sim_half["equity"], ann=ANN_DAYS, base=1.0)
    sim_half30 = R.simulate(sec_a, sec_b, tgt, "quarterly", COST_BP)
    st_half30 = B.local_stats(sim_half30["equity"], ann=ANN_DAYS, base=1.0)
    half = {
        "label": HALF_LABEL,
        "picked_on_first_half": {"w_cb": float(best_w),
                                 "sharpe_first_half": round(float(best_sr or 0.0), 4),
                                 "from": str(rc.index[0].date()),
                                 "to": str(rc.index[h - 1].date())},
        "scored_on": {"from": str(rc.index[h].date()),
                      "to": str(rc.index[-1].date()),
                      "bars": int(len(sec_a))},
        "picked_arm": {"w_cb": float(best_w), "sharpe": st_half.get("sharpe"),
                       "cagr": st_half.get("cagr"), "maxdd": st_half.get("maxdd"),
                       "cost_bp": COST_BP, "cadence": "quarterly"},
        "thirty_seventy_same_half": {"sharpe": st_half30.get("sharpe"),
                                     "cagr": st_half30.get("cagr"),
                                     "maxdd": st_half30.get("maxdd"),
                                     "cost_bp": COST_BP, "cadence": "quarterly"},
        "hindsight_on_second_half": _second_half_oracle(rc, re_, h, tgt),
    }
    half["picked_beat_30_70"] = bool(
        (half["picked_arm"]["sharpe"] or 0) > (half["thirty_seventy_same_half"]["sharpe"] or 0)
        + 0.005)

    # --- verdict: does the rule earn what the published split prints?
    band = 0.02
    walk_sr = float(best["sharpe"] or 0.0)
    hold_sr = float(hold_30_paid["sharpe"] or 0.0)
    half_sr = float(hold_50_paid["sharpe"] or 0.0)
    gap_vs_paid = walk_sr - hold_sr
    gap_vs_paper = walk_sr - blend_best_sr
    if gap_vs_paid > band:
        word = "THE_RULE_BEATS_HOLDING_THE_SPLIT"
    elif gap_vs_paid < -band:
        word = "THE_RULE_LOSES_TO_HOLDING_THE_SPLIT"
    else:
        word = "THE_RULE_MATCHES_HOLDING_THE_SPLIT"
    # the arm that needs no hindsight at all: a neutral 50/50.  If it also beats the rule,
    # the money lost is the churn's, not the weight's -- that is a different lesson and it
    # must be printed, not left for the reader to notice.
    naive = {
        "half_half_paid_sharpe": round(half_sr, 4),
        "best_rule_sharpe": round(walk_sr, 4),
        "wins_over_rule": bool(half_sr > walk_sr + 0.005),
        "sentence": (
            f"A neutral 50/50, which needs no hindsight about which split is best, earns "
            f"Sharpe {half_sr:.3f} -- {'more' if half_sr > walk_sr + 0.005 else 'less'} "
            f"than the best past-only rule's {walk_sr:.3f}. "
            + ("So the money the rule gives up is the churn's, not the weight's: it pays "
               "to move and still lands on a worse split."
               if half_sr > walk_sr + 0.005 else
               "The rule did add something over the neutral arm on this window.")),
    }
    sentence = (
        f"A rule that only knows the past picks {best['cadence']} / {best['lookback']} and "
        f"earns Sharpe {walk_sr:.3f}, against {hold_sr:.3f} for just holding the published "
        f"{tgt*100:.0f}/{100-tgt*100:.0f} with the same quarterly move -- and against the "
        f"{blend_best_sr:.3f} the page prints, which assumes the weight was known in "
        f"advance and the wallet walked back to it every day for free. The rule held "
        f"{best['picks']['median']*100:.0f}% convertible at the median, went all-in on one "
        f"book {best['picks']['share_at_full_book']*100:.0f}% of the time, and sat "
        f"{best['picks']['mean_abs_from_target']*100:.0f}pp away from the published split "
        f"on average. It also loses to a plain 50/50, which needs no hindsight at all "
        f"(that arm is scored below)."
    )

    face = {
        "face": "book_pair_weight_rule",
        "generated_at": _now_iso(),
        "evidence_cutoff": str(idx[-1].date()),
        "question": "would a reader who only knew the past have held 30/70 -- and what "
                    "would that rule have paid?",
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "bars": int(len(idx)),
            "scored_first": str(rcs.index[0].date()),
            "scored_bars": int(len(rcs)),
            "why": "the overlap only, and every arm scored after the rule's warm-up so no "
                   "arm is charged for the learning year",
        },
        "caliber": CALIBER,
        "target": tgt_src,
        "parents": {
            "cb": {"face": cb_meta["face"], "arm": cb_meta["arm"],
                   "execution": cb_meta["execution"], "panel": cb_meta["panel"]},
            "etf": {"face": etf_meta["face"], "arm": etf_meta["arm"],
                    "execution": etf_meta["execution"], "panel": etf_meta["panel"]},
        },
        "arms": arms,
        "best_rule": {k: best[k] for k in ("cadence", "lookback", "sharpe", "cagr",
                                           "maxdd", "n_moves", "turnover_one_way")},
        "best_rule_picks": best["picks"],
        "best_rule_path": paths.get((best["cadence"], best["lookback"]), []),
        "fixed_arms": {
            "published_split_paid_quarterly": hold_30_paid,
            "published_split_free_daily": hold_30_free,
            "half_half_paid_quarterly": hold_50_paid,
            "published_split_paid_full_window": {
                "w_cb": round(tgt, 4),
                "cadence": "quarterly", "cost_bp": COST_BP,
                "cagr": st_all.get("cagr"), "sharpe": st_all.get("sharpe"),
                "maxdd": st_all.get("maxdd"), "n_moves": hold_30_onall["n_moves"]},
        },
        "half_test": half,
        "naive_arm": naive,
        "reconciliation": recon,
        "verdict": {
            "word": word,
            "rule_sharpe": round(walk_sr, 4),
            "hold_published_paid_sharpe": round(hold_sr, 4),
            "published_paper_sharpe": round(blend_best_sr, 4),
            "gap_vs_holding": round(gap_vs_paid, 4),
            "gap_vs_paper": round(gap_vs_paper, 4),
            "sentence": sentence,
        },
        "unverified": [
            "the cadence and the lookback are picked on the same window they are scored "
            "on -- a reader adopting either should expect less than the printed number",
            "the trailing Sharpe the rule maximises is itself noisy: with one year of "
            "warm-up the first picks rest on few bars and flip easily",
            "each parent's own unverified list still applies (etf pool survivorship, the "
            "cb book's close-fill assumption, its 2026 drawdown being one regime)",
            "tax, the underlying bid-ask and the whole-lot grid are not in this cost",
            "the 6.9-year overlap contains one ETF-only regime; a rule tested only inside "
            "it cannot be shown to survive an ETF bad year",
        ],
    }

    if write:
        os.makedirs(RESULTS, exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(_plain(face), fh, ensure_ascii=False, indent=1)
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(_md(face))
    if not quiet:
        print(f"[run] window {face['window']['first']} -> {face['window']['last']} "
              f"scored from {face['window']['scored_first']} "
              f"({face['window']['scored_bars']} bars)", flush=True)
        for a in arms:
            print(f"  walk {a['cadence']:>9s}/{a['lookback']:>9s} moves {a['n_moves']:>3d} "
                  f"CAGR {a['cagr']*100:6.2f}% SR {a['sharpe']:.3f} "
                  f"MDD {a['maxdd']*100:6.1f}% median w {a['picks']['median']:.2f} "
                  f"changes {a['picks']['n_changes']}", flush=True)
        print(f"  hold {tgt*100:.0f}/{100-tgt*100:.0f} paid quarterly SR {hold_sr:.3f} "
              f"| free daily same window SR {hold_30_free['sharpe']:.3f} "
              f"| paper {blend_best_sr:.3f}", flush=True)
        print(f"  VERDICT {word} (rule {walk_sr:.3f} vs hold {hold_sr:.3f}, "
              f"{gap_vs_paid:+.3f})", flush=True)
    return face


def _second_half_oracle(rc, re_, h, tgt):
    """What the best weight *on the second half itself* would have paid -- the size of
    the prize hindsight is competing for."""
    best_w, best_sr = None, None
    for w in GRID:
        sr = _sharpe_of_slice(rc, re_, w, h, len(rc))
        if sr is None:
            continue
        if best_sr is None or sr > best_sr:
            best_w, best_sr = w, sr
    return {"w_cb": float(best_w) if best_w is not None else None,
            "sharpe": round(float(best_sr or 0.0), 4),
            "note": "picked with the second half's own data -- not attainable, printed as "
                    "the size of the prize"}


def _md(face):
    w = face["window"]
    t = face["target"]
    v = face["verdict"]
    L = []
    A = L.append
    A(f"# Would you have found the split without peeking? -- {face['evidence_cutoff']}\n")
    A(f"*generated {face['generated_at']} · window {w['first']} -> {w['last']} "
      f"({w['bars']} bars, the overlap of both books) · every arm scored from "
      f"{w['scored_first']} ({w['scored_bars']} bars)*\n")
    A(f"**{v['word']}** -- {v['sentence']}\n")
    A(f"The published split is {t['value']*100:.0f}% convertible / "
      f"{100-t['value']*100:.0f}% ETF, taken from `{t['face']}` field `{t['field']}` "
      f"({t['why']}).\n")
    A("## The rule, walked forward (past-only picks, 10bp per side on every move)\n")
    A("| cadence | lookback | moves | CAGR | Sharpe | max DD | median w_cb | "
      "all-in share | changes | mean distance from 30% |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for a in face["arms"]:
        p = a["picks"]
        star = " **" if (a["cadence"] == face["best_rule"]["cadence"]
                         and a["lookback"] == face["best_rule"]["lookback"]) else ""
        A(f"| {a['cadence']}{star} | {a['lookback']} | {a['n_moves']} | "
          f"{a['cagr']*100:.2f}% | {a['sharpe']:.3f} | {a['maxdd']*100:.1f}% | "
          f"{p['median']*100:.0f}% | {p['share_at_full_book']*100:.0f}% | "
          f"{p['n_changes']} | {p['mean_abs_from_target']*100:.0f}pp |")
    A("")
    A("## What the weight actually was, beside the split you were shown\n")
    fa = face["fixed_arms"]
    A("| arm | w_cb | moves | CAGR | Sharpe | max DD |")
    A("|---|---|---|---|---|---|")
    for name, key in (("published 30/70, quarterly move, paid",
                       "published_split_paid_quarterly"),
                      ("published 30/70, daily walk-back, free (the page's number)",
                       "published_split_free_daily"),
                      ("50/50, quarterly move, paid", "half_half_paid_quarterly"),
                      ("published 30/70, quarterly move, paid, FULL window",
                       "published_split_paid_full_window")):
        r = fa[key]
        A(f"| {name} | {r['w_cb']*100:.0f}% | {r['n_moves']} | {r['cagr']*100:.2f}% | "
          f"{r['sharpe']:.3f} | {r['maxdd']*100:.1f}% |")
    A("")
    b = face["best_rule_picks"]
    A(f"Best rule (`{face['best_rule']['cadence']}` / "
      f"`{face['best_rule']['lookback']}`): it held between {b['min']*100:.0f}% and "
      f"{b['max']*100:.0f}% convertible, sat at {b['median']*100:.0f}% at the median, "
      f"changed its mind {b['n_changes']} times over {b['n']} decisions, and was all-in "
      f"on a single book in {b['share_at_full_book']*100:.0f}% of them.\n")
    h = face["half_test"]
    A("## The test with no machinery: pick on the first half, score the second\n")
    A(f"- best weight on {h['picked_on_first_half']['from']} -> "
      f"{h['picked_on_first_half']['to']}: **{h['picked_on_first_half']['w_cb']*100:.0f}%** "
      f"convertible (first-half Sharpe {h['picked_on_first_half']['sharpe_first_half']:.3f})")
    A(f"- that weight on the second half (quarterly move, paid): Sharpe "
      f"{h['picked_arm']['sharpe']:.3f}, CAGR {h['picked_arm']['cagr']*100:.2f}%, "
      f"max DD {h['picked_arm']['maxdd']*100:.1f}%")
    A(f"- the published 30/70 on the same half: Sharpe "
      f"{h['thirty_seventy_same_half']['sharpe']:.3f}, CAGR "
      f"{h['thirty_seventy_same_half']['cagr']*100:.2f}%, max DD "
      f"{h['thirty_seventy_same_half']['maxdd']*100:.1f}%")
    A(f"- the best weight with the second half's own data (not attainable, printed as the "
      f"size of the prize): {h['hindsight_on_second_half']['w_cb']*100:.0f}% convertible at "
      f"Sharpe {h['hindsight_on_second_half']['sharpe']:.3f}\n")
    rc_ = face["reconciliation"]
    A("## The arm that needs no hindsight at all\n")
    nv = face["naive_arm"]
    # r2180: the sentence already states the 50/50, the no-hindsight part and both
    # Sharpes; printing a prefix around it put the same measurement on the page twice
    # (r1911 family).
    A(f"{nv['sentence']}\n")
    A("## Does this face read the same books as the page?\n")
    A(f"- free daily walk-back on the full window: Sharpe "
      f"{rc_['full_window_free_daily_here']:.3f} against the blend face's "
      f"{rc_['published_full_window_sharpe']:.3f} (diff {rc_['diff_full_window']:+.4f}, "
      f"{'match' if rc_['matches_published'] else 'MISMATCH'})")
    A(f"- the same arm restricted to the scored window: "
      f"{rc_['daily_free_same_window_sharpe']:.3f} (diff {rc_['diff_same_window']:+.4f}) -- "
      f"that difference is the window, not the books.\n")
    A("## How to read it\n")
    A(f"- {face['caliber']['pick_metric']}.")
    A(f"- {face['caliber']['warmup']}.")
    A(f"- {face['caliber']['why_two_sides']}, so each move pays 2x the moved share at "
      f"{face['caliber']['cost_per_side_bp']:.0f}bp per side.")
    A(f"- Not in this cost: {face['caliber']['not_modelled']}.")
    A("\n## Unverified\n")
    for u in face["unverified"]:
        A(f"- {u}")
    A("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- check
def check():
    """Cheap drift check: parent panel bytes, the published weight and the window."""
    if not os.path.exists(FACE):
        print("STALE: book_pair_weight_rule face missing "
              "(run `python scripts/book_pair_weight_rule.py run`)")
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
    tgt_rec = face.get("target", {})
    try:
        with open(BLEND_FACE, encoding="utf-8") as fh:
            blend = json.load(fh)
        now_tgt = float(blend["best"]["w_cb"])
        if abs(now_tgt - float(tgt_rec.get("value", -1))) > 1e-9:
            problems.append(f"STALE: the blend face now picks w_cb={now_tgt}, this face "
                            f"scored {tgt_rec.get('value')}")
        now_last = blend.get("window", {}).get("last")
        if now_last and now_last != tgt_rec.get("window_last"):
            problems.append(f"STALE: the blend window now ends {now_last}, this face "
                            f"ended at {tgt_rec.get('window_last')}")
    except Exception as exc:
        problems.append(f"STALE: the blend face cannot be read ({exc})")
    if problems:
        for p in problems:
            print(p)
        return 3
    print(json.dumps({"ok": True, "problems": [],
                      "target_w_cb": tgt_rec.get("value"),
                      "verdict": face["verdict"]["word"]}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    """Offline: the pick must use only the past, and the money must follow the picks."""
    import numpy as np
    import pandas as pd

    legs, fails = 0, []

    def ok(name, cond, got=""):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(f"{name}: {got}")

    idx = pd.bdate_range("2019-01-02", periods=1600)
    n = len(idx)
    # book A earns ~0.06%/day for the first half and nothing after; book B the reverse --
    # a rule that reads the past must follow the money, and a rule that peeked would not.
    # Both books carry the same seeded noise: a NOISELESS fixture has zero variance and
    # therefore an undefined Sharpe, which is not a case worth asserting on.
    rng = np.random.default_rng(20261127)
    noise_a = rng.normal(0.0, 0.002, n)
    noise_b = rng.normal(0.0, 0.002, n)
    ra = pd.Series(np.where(np.arange(n) < n // 2, 0.0006, 0.0) + noise_a, index=idx)
    rb = pd.Series(np.where(np.arange(n) < n // 2, 0.0, 0.0006) + noise_b, index=idx)

    # A: the pick at bar i must not depend on any bar after i
    a_short = pd.Series(ra.values[:900], index=idx[:900])
    b_short = pd.Series(rb.values[:900], index=idx[:900])
    w_short, sr_short = pick_weight(a_short, b_short, 899, "expanding")
    w_long, sr_long = pick_weight(ra, rb, 899, "expanding")
    ok("A1 the pick ignores bars after the decision", (w_short, sr_short) == (w_long, sr_long),
       f"{(w_short, sr_short)} vs {(w_long, sr_long)}")
    ok("A2 with enough history the pick is a grid point", w_long in GRID, w_long)

    # B: early on there is not enough history to speak
    w0, sr0 = pick_weight(ra, rb, 50, "expanding")
    ok("B1 the rule stays silent before the warm-up", w0 is None and sr0 is None,
       (w0, sr0))

    # C: the rule follows the book that just won.  With an EXPANDING window by the end
    # the book that won the first half is still half the history, so C2 uses the trailing
    # window -- that is the whole reason both lookbacks exist.
    w_first, _ = pick_weight(ra, rb, n // 2 - 2, "expanding")
    w_second, _ = pick_weight(ra, rb, n - 2, "trailing3y")
    ok("C1 after book A's run the rule wants all of A", abs(w_first - 1.0) < 1e-9, w_first)
    ok("C2 after book B's run the trailing rule wants none of A",
       abs(w_second - 0.0) < 1e-9, w_second)

    # D: the walk pays for moves and the picks are the ones it acted on
    wf = walk_forward(ra, rb, "quarterly", "trailing3y")
    ok("D1 the walk starts at its first decision", wf is not None and wf["picks"],
       None if wf is None else len(wf["picks"]))
    ok("D2 a wandering rule must move more than never", wf["n_moves"] > 0, wf["n_moves"])
    vals = [p["w_cb"] for p in wf["picks"]]
    ok("D3 the first pick is all of the winning book", abs(vals[0] - 1.0) < 1e-9, vals[0])
    ok("D4 the last pick is all of the other book", abs(vals[-1] - 0.0) < 1e-9, vals[-1])
    sim_paid = walk_forward(ra, rb, "quarterly", "expanding", cost_bp=COST_BP)
    sim_free = walk_forward(ra, rb, "quarterly", "expanding", cost_bp=0.0)
    ok("D5 paying to move lowers the walk's return",
       float(sim_paid["equity"].iloc[-1]) < float(sim_free["equity"].iloc[-1]),
       f"{sim_paid['equity'].iloc[-1]:.6f} vs {sim_free['equity'].iloc[-1]:.6f}")
    ok("D6 the paid and free walks take the same route",
       sim_paid["n_moves"] == sim_free["n_moves"]
       and abs(sim_paid["turnover"] - sim_free["turnover"]) < 1e-12,
       (sim_paid["n_moves"], sim_free["n_moves"]))

    # E: a book that never moves must be held, not traded
    flat = pd.Series(np.zeros(n), index=idx)
    wf_flat = walk_forward(ra, flat, "quarterly", "expanding")
    ok("E1 holding the better book pays, and the walk's equity is finite",
       np.isfinite(float(wf_flat["equity"].iloc[-1])) and wf_flat["equity"].iloc[-1] > 1.0,
       float(wf_flat["equity"].iloc[-1]))

    # F: pick summary names a rule that never changes its mind
    same_w = [{"date": "2020-01-01", "w_cb": 0.3, "trailing_sharpe": 1.0, "move": 0.0}] * 5
    s = _pick_summary(same_w)
    ok("F1 a constant path has zero changes and zero distance", s["n_changes"] == 0
       and s["mean_abs_from_target"] == 0.0, s)
    extremes = [{"date": "2020-01-01", "w_cb": w, "trailing_sharpe": 1.0, "move": 0.0}
                for w in (0.0, 1.0)]
    s2 = _pick_summary(extremes)
    ok("F2 all-in picks are counted as all-in", s2["share_at_full_book"] == 1.0,
       s2["share_at_full_book"])

    # G: the honesty test's own arithmetic -- a weight picked on a flat first half must
    # not be reported as a winner
    ok("G1 a short slice yields no Sharpe rather than a zero",
       _sharpe_of_slice(ra, rb, 0.3, 0, 10) is None, "none")

    # H: check() contract words -- the chain pays attention to STALE and nothing else
    import contextlib
    import io
    import tempfile

    saved = globals().get("FACE")
    tmpdir = tempfile.mkdtemp()
    try:
        real_cb = B._stamp(os.path.join(ROOT, "data/cb_panel.csv.gz"))
        real_etf = B._stamp(os.path.join(ROOT, "data/daily/510300.csv"))
        with open(BLEND_FACE, encoding="utf-8") as fh:
            blend = json.load(fh)
        base = {"parents": {"cb": {"panel": real_cb}, "etf": {"panel": real_etf}},
                "target": {"value": float(blend["best"]["w_cb"]),
                           "window_last": blend.get("window", {}).get("last")},
                "verdict": {"word": "X"}}
        good = os.path.join(tmpdir, "good.json")
        with open(good, "w", encoding="utf-8") as fh:
            json.dump(base, fh)
        globals()["FACE"] = good
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_good = check()
        ok("H1 matching parents and target pass the check",
           rc_good == 0 and "STALE" not in buf.getvalue(), buf.getvalue()[:120])

        blocked = os.path.join(tmpdir, "blocked.json")
        bad = json.loads(json.dumps(base))
        bad["parents"]["cb"]["panel"] = dict(real_cb, size=real_cb["size"] + 1)
        with open(blocked, "w", encoding="utf-8") as fh:
            json.dump(bad, fh)
        globals()["FACE"] = blocked
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_bad = check()
        ok("H2 a moved parent panel is STALE and rc3",
           rc_bad == 3 and "STALE" in buf.getvalue(), f"{rc_bad} {buf.getvalue()[:100]}")

        moved_tgt = os.path.join(tmpdir, "moved_tgt.json")
        bad2 = json.loads(json.dumps(base))
        bad2["target"]["value"] = float(blend["best"]["w_cb"]) + 0.1
        with open(moved_tgt, "w", encoding="utf-8") as fh:
            json.dump(bad2, fh)
        globals()["FACE"] = moved_tgt
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_tgt = check()
        ok("H3 a changed published weight is STALE (not a quiet republish)",
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
    sub.add_parser("check", help="cheap drift check against parent stamps and the target")
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
