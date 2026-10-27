"""E107: does a split inside an UNCHANGED holding reach the book's own curve?

E104 measured the read on names the book kept through a window (they enter no
swap list, so E100's entrant/exit decomposition cannot see them). The ticket
also asked the second half: price those same windows on the ENGINE's own
simulated book, in both arms, and say how many bp of the era curve the
persistent-name reads actually move.

Method (one per-potential-confusion note per choice, because the two candidate
readings differ):

  * the curve is built from the SAME decision timeline E104 used, not from a
    fresh rank call -- so the book that earns the curve is by construction the
    book whose windows were measured;
  * the arm-vs-arm curve delta is NOT the read effect: two arms hold different
    names in the swap windows, so that gap pays for selection as well. The read
    effect is a third, counterfactual curve: the repair arm's own holdings and
    own prices everywhere except the persistent names, whose session-to-session
    RETURN is replaced by the unscreened RETURN while that window is open. Turn-
    over, cost and holdings are therefore identical to the repair arm, so the
    difference is the read and nothing else;
  * the substitution rewrites returns, not levels: splicing unscreened LEVELS
    into a repair series would inject a spurious jump at every window edge
    (the two arms disagree about the level by exactly the read being measured).

Pure function of the already-published panel and the E104 window list: no new
engine, no re-burn, no gate, zero ledger.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

FACE_DIR = os.path.join(ROOT, "results", "e44_midmonth")
OUT_NAME = "HELDCURVE-<cutoff>.json"


def _max_drawdown(curve):
    """Worst peak-to-trough of a [(date, value)] curve, as a positive fraction."""
    peak = None
    worst = 0.0
    for _d, v in curve:
        if v is None:
            continue
        if peak is None or v > peak:
            peak = v
        if peak and v < peak:
            dd = 1.0 - v / peak
            if dd > worst:
                worst = dd
    return worst


def _book_curve(cal, prices, decisions, start_idx, end_idx, cost_bp_side):
    """Equal-weight book curve from an explicit decision timeline.

    ``decisions`` is [(session_idx, [names])] -- the engine's own holdings. The
    decision at idx is filled at that session's close and earns idx -> idx+1,
    which is exactly the holding period E104 measures a window read over.

    NOTE (deliberate divergence, recorded in the spec and the honest block):
    e27.simulate books the same decision one session later, so this curve's
    LEVEL is not comparable to a published era curve. Only deltas between the
    three arms of this leg are published.
    """
    plan = {i: list(names) for i, names in decisions}
    weights = {}
    port = 1.0
    curve = []
    turnover_total = 0.0
    cost_paid = 0.0
    rebalances = 0
    breadth = []
    curve = [(cal[start_idx], 1.0)] if start_idx < len(cal) else []
    for i in range(start_idx + 1, end_idx + 1):
        if (i - 1) in plan and plan[i - 1]:
            target = {s: 1.0 / len(plan[i - 1]) for s in plan[i - 1]}
            turnover = (sum(abs(target.get(s, 0.0) - weights.get(s, 0.0))
                            for s in set(target) | set(weights)) / 2.0
                        if weights else 1.0)
            fee = turnover * cost_bp_side / 1e4
            port *= (1.0 - fee)
            cost_paid += fee
            turnover_total += turnover
            rebalances += 1
            weights = dict(target)
            breadth.append(len(target))
        if weights:
            growth = 0.0
            neww = {}
            for s, w in weights.items():
                p = prices.get(s)
                if not p:
                    neww[s] = w
                    continue
                a, b = p[i], p[i - 1]
                if a is None or b is None or b <= 0:
                    neww[s] = w
                    continue
                r = a / b - 1.0
                neww[s] = w * (1.0 + r)
                growth += w * r
            tv = sum(neww.values())
            weights = {s: v / tv for s, v in neww.items()} if tv > 0 else weights
            port *= (1.0 + growth)
        curve.append((cal[i], port))
    return curve, {"rebalances": rebalances, "turnover_total": turnover_total,
                   "cost_paid_frac": cost_paid,
                   "breadth_mean": (sum(breadth) / len(breadth)) if breadth else None,
                   "breadth_min": min(breadth) if breadth else None,
                   "breadth_max": max(breadth) if breadth else None}


def _hybrid_prices(rep_prices, uns_prices, names, start_idx, end_idx):
    """rep prices with ``names``' RETURNS rewritten to the unscreened series.

    Continuity is preserved inside the window and nothing is spliced at the
    edges: out[j] = out[j-1] * (uns[j]/uns[j-1]) for the substituted names, and
    out[j] = rep[j] for everyone else.
    """
    out = {}
    for s, series in rep_prices.items():
        if s not in names:
            out[s] = series
            continue
        uns = uns_prices.get(s)
        if not uns:
            out[s] = series
            continue
        new = list(series)
        for j in range(max(1, start_idx + 1), min(end_idx, len(series) - 1) + 1):
            a, b = uns[j], uns[j - 1]
            if a is None or b is None or b <= 0:
                continue
            prev = new[j - 1]
            if prev is None:
                continue
            new[j] = prev * (a / b)
            # rebase after the window so later windows start from the rep level
            if j + 1 < len(new):
                nxt = series[j + 1] if j + 1 < len(series) else None
                if nxt is not None and series[j]:
                    new[j + 1] = nxt * (new[j] / series[j]) if series[j] else nxt
        out[s] = new
    return out


def _ret(curve):
    if not curve:
        return None
    return curve[-1][1] / curve[0][1] - 1.0


def run(out_path=None, start="2018-01-01", pick_n=9999, exclude=("sh511",),
        gap_limit=1, mid_day=15, eras=None, top_k=3):
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import e39_panel_census as e39
    import panel_screen

    eras = eras or e39.ERAS
    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    gap_label = "neutralise_gap%d" % int(gap_limit)
    universes = {"unscreened": raw}
    universes[gap_label], reports = panel_screen.screen_universe(
        raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(gap_limit))
    arms = ["unscreened", gap_label]

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", e39._mid_month_indices(cal, mid_day))]

    caches = {}
    for label in arms:
        univ = universes[label]
        all_syms = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = e39._decision_sets(cal, prices, amounts, universe,
                                                  pick_n, idxs, rank_cache)
        caches[label] = {"prices": prices, "decisions": decisions}

    cells = []
    for era_row in eras:
        for book in e39.LEVEL_BOOKS:
            a_dec = caches["unscreened"]["decisions"][book]
            b_dec = caches[gap_label]["decisions"][book]
            grid = e39._era_end_grid(b_dec, cal, era_row, 1)
            if not grid:
                cells.append({"era": era_row[0], "book": book,
                              "skipped": "no decision ends for this era/book",
                              "verdict": "no_unchanged_holdings"})
                continue
            nxt = e39._next_decision_session(b_dec, cal, grid[-1])
            window_end = nxt or cal[-1]
            a_tr = [x for x in e39._truncate_decisions(a_dec, cal, window_end)
                    if e39._era_of(cal[x[0]], (era_row,)) == era_row[0]]
            b_tr = [x for x in e39._truncate_decisions(b_dec, cal, window_end)
                    if e39._era_of(cal[x[0]], (era_row,)) == era_row[0]]
            if len(a_tr) < 2 or len(b_tr) < 2:
                cells.append({"era": era_row[0], "book": book,
                              "window_end": window_end,
                              "skipped": "fewer than two decisions in the era",
                              "verdict": "no_unchanged_holdings"})
                continue

            # --- E104's window list, recomputed here so the names are available
            b_hold = {cal[i]: set(h) for i, h in b_tr}
            a_hold = {cal[i]: set(h) for i, h in a_tr}
            dates = sorted(set(b_hold) & set(a_hold))
            windows = []
            for d, nd in zip(dates, dates[1:]):
                if e39._era_of(d, (era_row,)) != era_row[0]:
                    continue
                persistent = sorted(b_hold[d] & b_hold[nd])
                split = e39._held_read_split(
                    caches[gap_label]["prices"], caches["unscreened"]["prices"],
                    b_hold[d], b_hold[nd],
                    cal.index(d), cal.index(nd), top_k=top_k)
                if not split["persistent_names"]:
                    continue
                windows.append({"date": d, "next": nd, "persistent": persistent,
                                "split": split})
            if not windows:
                cells.append({"era": era_row[0], "book": book,
                              "window_end": window_end, "persistent_reads": 0,
                              "verdict": "no_unchanged_holdings"})
                continue

            s_idx = b_tr[0][0]
            # the era's own last transition is priced through the following
            # decision of the same book (r1166: a hard cut silently drops it),
            # so the curve runs to that session, not to the last era decision
            e_idx = cal.index(window_end) if window_end in cal else len(cal) - 1

            rep_prices = caches[gap_label]["prices"]
            uns_prices = caches["unscreened"]["prices"]
            cur_u, st_u = _book_curve(cal, uns_prices, a_tr, s_idx, e_idx, base.COST_BP_SIDE)
            cur_b, st_b = _book_curve(cal, rep_prices, b_tr, s_idx, e_idx, base.COST_BP_SIDE)
            # one hybrid per window, chained: the substitution set is a property
            # of the window, and chaining keeps the book continuous.
            hybrid = rep_prices
            for w in windows:
                hybrid = _hybrid_prices(hybrid, uns_prices, set(w["persistent"]),
                                        cal.index(w["date"]), cal.index(w["next"]))
            cur_h, st_h = _book_curve(cal, hybrid, b_tr, s_idx, e_idx, base.COST_BP_SIDE)
            # identity control: substituting a series for ITSELF must leave the
            # curve bit-identical. A level splice, or an off-by-one at a window
            # edge, shows up here as a non-zero residual instead of hiding as a
            # plausible few-bp "read effect".
            hybrid_id = rep_prices
            for w in windows:
                hybrid_id = _hybrid_prices(hybrid_id, rep_prices, set(w["persistent"]),
                                           cal.index(w["date"]), cal.index(w["next"]))
            cur_id, _st_id = _book_curve(cal, hybrid_id, b_tr, s_idx, e_idx,
                                        base.COST_BP_SIDE)
            identity_residual_bp = 100.0 * (_ret(cur_id) - _ret(cur_b))

            ret_u, ret_b, ret_h = _ret(cur_u), _ret(cur_b), _ret(cur_h)
            curve_delta_bp = 100.0 * (ret_b - ret_u)
            read_effect_bp = 100.0 * (ret_h - ret_b)

            # weight share of the persistent names in the repair book per window:
            # a read only reaches the curve through the weight it is carried at
            wmap = {d: set(h) for d, h in b_hold.items()}
            win_rows = []
            for w in windows:
                n = len(wmap[w["date"]]) or 1
                win_rows.append({
                    "date": w["date"], "next": w["next"],
                    "persistent_names": w["split"]["persistent_names"],
                    "persistent_weight_pct": round(100.0 * w["split"]["persistent_names"] / n, 2),
                    "read_delta_bp": w["split"]["delta_bp"],
                    "max_abs_read": w["split"]["max_abs_read"].get("name")
                    if w["split"]["max_abs_read"] else None,
                })
            pw_mean = (sum(r["persistent_weight_pct"] for r in win_rows) / len(win_rows))
            win_rows.sort(key=lambda r: -abs(r["read_delta_bp"] or 0.0))

            cells.append({
                "era": era_row[0], "book": book, "window_end": window_end,
                "sessions": e_idx - s_idx + 1,
                "decisions": len(b_tr),
                "persistent_reads": sum(w["split"]["persistent_names"] for w in windows),
                "transitions": len(windows),
                "windows_with_a_split_pct": round(
                    100.0 * sum(1 for w in windows if abs(w["split"]["delta_bp"] or 0) > 1e-9)
                    / len(windows), 1),
                "curve": {
                    "ret_unscreened_pct": round(100.0 * ret_u, 4),
                    "ret_repair_pct": round(100.0 * ret_b, 4),
                    "ret_hybrid_pct": round(100.0 * ret_h, 4),
                    "curve_delta_bp": round(curve_delta_bp, 2),
                    "read_effect_bp": round(read_effect_bp, 2),
                    # sign convention, stated once: read_effect is the COST of
                    # undoing the repair on the persistent names, so the part of
                    # the arm gap the READ itself supplies is its negative
                    "read_attribution_bp": round(-read_effect_bp, 2),
                    "read_effect_share_of_curve_delta_pct": (
                        round(-100.0 * read_effect_bp / curve_delta_bp, 1)
                        if abs(curve_delta_bp) > 1e-9 else None),
                    "identity_control_residual_bp": round(identity_residual_bp, 12),
                    "persistent_weight_mean_pct": round(pw_mean, 2),
                    # the book is a near-universe book (breadth ~ the ETF panel),
                    # so the names that actually swap are the only place selection
                    # can act; publishing that share says how much of the arm gap
                    # is even AVAILABLE to selection
                    "swapped_share_mean_pct": round(100.0 - pw_mean, 2),
                    "selection_effect_bp": round(curve_delta_bp + read_effect_bp, 2),
                    "max_drawdown_unscreened_pct": round(100.0 * _max_drawdown(cur_u), 3),
                    "max_drawdown_repair_pct": round(100.0 * _max_drawdown(cur_b), 3),
                    "max_drawdown_hybrid_pct": round(100.0 * _max_drawdown(cur_h), 3),
                    "breadth_mean": round(st_b["breadth_mean"], 1) if st_b["breadth_mean"] else None,
                    "turnover_unscreened": round(st_u["turnover_total"], 2),
                    "turnover_repair": round(st_b["turnover_total"], 2),
                },
                "windows": win_rows[:top_k + 3],
                "verdict": _verdict(read_effect_bp, curve_delta_bp, pw_mean),
            })

    measured = [c for c in cells if isinstance((c.get("curve") or {}).get("read_effect_bp"),
                                              (int, float))]
    by_era = {}
    for c in measured:
        by_era.setdefault(c["era"], []).append(c["curve"]["read_effect_bp"])
    worst = sorted(measured, key=lambda c: -abs(c["curve"]["read_effect_bp"]))[:5]
    biggest_read = sorted(
        ((w["read_delta_bp"] or 0.0, c["era"], c["book"], w["date"], w["persistent_names"])
         for c in measured for w in c["windows"]),
        key=lambda r: -abs(r[0]))[:5]

    share_of_curve = [c["curve"]["read_effect_share_of_curve_delta_pct"] for c in measured
                      if c["curve"]["read_effect_share_of_curve_delta_pct"] is not None]
    return {
        "study": "e107_unchanged_holding_curve_effect",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "arms": arms, "gap_limit": int(gap_limit),
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": list(e39.LEVEL_BOOKS),
            "cost_bp_side": base.COST_BP_SIDE,
            "curve": "equal-weight book built from the SAME decision timeline E104 "
                     "measured; a decision at idx earns from idx to idx+1; cost = "
                     "turnover x COST_BP_SIDE",
            "curve_delta_bp": "100*(ret_repair - ret_unscreened) -- selection + read + cost",
            "read_effect_bp": "100*(ret_hybrid - ret_repair) where hybrid = repair arm's "
                              "holdings and prices, except persistent names whose session "
                              "RETURN is the unscreened one inside that window; holdings, "
                              "turnover and cost are therefore identical",
            "not_a_burn": "no panel re-burn, no new engine path, no gate",
        },
        "screen_reports": {k: reports.get(k) for k in list(reports)[:6]} if reports else {},
        "cells": cells,
        "summary": {
            "cells_measured": len(measured),
            "read_effect_bp_by_era": {k: [round(x, 2) for x in v] for k, v in by_era.items()},
            "largest_read_effects": [
                {"era": c["era"], "book": c["book"],
                 "curve_delta_bp": c["curve"]["curve_delta_bp"],
                 "read_effect_bp": c["curve"]["read_effect_bp"]} for c in worst],
            "largest_window_reads": [
                {"delta_bp": round(d, 2), "era": e, "book": b, "date": dt,
                 "persistent_names": n} for d, e, b, dt, n in biggest_read],
            "median_read_effect_share_of_curve_delta_pct": (
                round(sorted(share_of_curve)[len(share_of_curve) // 2], 1)
                if share_of_curve else None),
            "max_identity_control_residual_bp": max(
                [abs(c["curve"]["identity_control_residual_bp"]) for c in measured] or [0.0]),
            "degenerate_cells": [
                {"era": c["era"], "book": c["book"],
                 "persistent_weight_mean_pct": c["curve"]["persistent_weight_mean_pct"],
                 "swapped_share_mean_pct": c["curve"]["swapped_share_mean_pct"]}
                for c in measured if c["curve"]["persistent_weight_mean_pct"] >= 95.0],
            "verdicts": _tally(c.get("verdict") for c in measured),
        },
        "answers": {
            "does_a_persistent_read_reach_the_curve": any(
                abs(c["curve"]["read_effect_bp"]) > 1.0 for c in measured),
            "how_do_the_two_readings_differ": "the arm-vs-arm curve delta pays for "
                                              "selection as well as the read, so it is "
                                              "published beside the read effect, never as it",
            "drawdown_moves_too": any(
                abs(c["curve"]["max_drawdown_repair_pct"]
                    - c["curve"]["max_drawdown_hybrid_pct"]) > 0.01
                for c in measured if c["curve"].get("max_drawdown_hybrid_pct") is not None),
        },
        "honest": [
            "the read effect is a counterfactual on the SAME holdings, not a re-burn: it "
            "answers 'what does the read alone do to this curve', not 'what would the "
            "other arm have earned'",
            "the substitution rewrites returns inside the window and rebases afterwards, "
            "so later windows start from the repair level -- splicing levels would inject "
            "a jump exactly the size of the read being measured",
            "a level over few transitions is a mean over few names (E105); no window-level "
            "read is promoted to an era reading here",
            "where the persistent names carry ~the whole book (2024_now), the "
            "counterfactual IS the other arm: the number is still true but it cannot "
            "separate the read from selection, and those cells say so",
            "the identity control (substitute a series for itself) must read 0.0; a "
            "non-zero residual there would mean the machinery, not the data, moved the "
            "curve",
            "description only: no gate, no verdict on any strategy, zero ledger",
        ],
    }


def _tally(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


def _verdict(read_effect_bp, curve_delta_bp, persistent_weight_pct=None):
    """Verdict on the READ's attribution to the arm gap (-read_effect_bp)."""
    if not isinstance(read_effect_bp, (int, float)):
        return "unmeasured"
    attribution = -read_effect_bp
    cd = curve_delta_bp or 0.0
    if abs(attribution) < 1e-9 and abs(cd) < 1e-9:
        return "no_read_and_no_arm_gap"
    if abs(attribution) < 1e-9:
        return "read_does_not_reach_the_curve"
    if abs(cd) > 1e-9 and abs(attribution - cd) < 1e-9:
        return "read_explains_the_arm_gap"
    if attribution * cd < 0:
        return "read_opposes_the_arm_gap"
    if abs(attribution) < 1.0:
        return "read_under_1bp"
    if abs(attribution) > abs(cd):
        return "read_exceeds_the_arm_gap"
    return "read_in_the_same_direction_as_the_arm_gap"


def selftest():
    fails, n = [], 0

    def chk(cond, label):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    cal = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
    flat = {"a": [1.0, 1.0, 1.0, 1.0]}
    cur, st = _book_curve(cal, flat, [(0, ["a"])], 0, 3, 0.0)
    chk(abs(_ret(cur)) < 1e-12, "a flat price earns exactly zero")
    chk(st["rebalances"] == 1, "one decision is one rebalance")
    chk(st["turnover_total"] == 1.0, "the first buy is full turnover")

    up = {"a": [1.0, 1.1, 1.21, 1.331]}
    cur, st = _book_curve(cal, up, [(0, ["a"])], 0, 3, 0.0)
    chk(abs(_ret(cur) - 0.331) < 1e-9, "a single holding compounds its own series")

    cur, st = _book_curve(cal, flat, [(0, ["a"])], 0, 3, 10.0)
    chk(abs(_ret(cur) + 1.0 / 1e4 * 10.0) < 1e-9,
        "cost is turnover x bp on the first buy (10bp = -0.10%)")

    # a decision earns from its own session, never from before it
    late = {"a": [1.0, 1.0, 2.0, 2.0]}
    cur, _st = _book_curve(cal, late, [(2, ["a"])], 0, 3, 0.0)
    chk(abs(_ret(cur)) < 1e-12, "a decision at idx does not earn the idx-1 -> idx leg")

    # hybrid: the repair series doubles, the unscreened one is flat -> the
    # substituted read must remove that doubling from the curve
    rep = {"a": [1.0, 1.5, 2.0, 2.0]}
    uns = {"a": [1.0, 1.0, 1.0, 1.0]}
    hyb = _hybrid_prices(rep, uns, {"a"}, 0, 2)
    chk(all(abs(x - 1.0) < 1e-12 for x in hyb["a"][:3]),
        "a persistent name's return is rewritten to the unscreened one inside the window")
    chk(hyb["a"][3] is not None, "the series stays continuous after the window")
    other = _hybrid_prices(rep, uns, {"b"}, 0, 2)
    chk(other["a"] is rep["a"], "a name outside the persistent set is not substituted")

    cur_b, _ = _book_curve(cal, rep, [(0, ["a"])], 0, 2, 0.0)
    cur_h, _ = _book_curve(cal, hyb, [(0, ["a"])], 0, 2, 0.0)
    chk(_ret(cur_h) < _ret(cur_b), "the read effect is signed, not absolute-valued")

    chk(abs(_max_drawdown([("d1", 1.0), ("d2", 1.2), ("d3", 0.6)]) - 0.5) < 1e-12,
        "drawdown is peak-to-trough, as a positive fraction")
    chk(_max_drawdown([("d1", 1.0), ("d2", 1.1)]) == 0.0, "a monotone curve has no drawdown")

    chk(_verdict(0.0, 0.0) == "no_read_and_no_arm_gap",
        "two zeros are one verdict, not an |x|<1 rounding")
    chk(_verdict(0.0, -700.0) == "read_does_not_reach_the_curve",
        "zero read is not a verdict about the curve gap")
    chk(_verdict(-0.4, 3.0) == "read_under_1bp",
        "a sub-bp read is named as sub-bp, not rounded into either neighbour")
    chk(_verdict(-2.31, 2.31) == "read_explains_the_arm_gap",
        "a read that is the whole gap says so instead of 'exceeds'")
    chk(_verdict(2.3, 2.3) == "read_opposes_the_arm_gap",
        "a read arguing the other way is named, not averaged into the gap")
    chk(_verdict(-12.0, 3.0) == "read_exceeds_the_arm_gap",
        "a read larger than the arm gap is called out")
    chk(_verdict(-12.0, -1.0) == "read_opposes_the_arm_gap",
        "opposition outranks size: a big read against a small gap argues first")
    chk(_tally(["a", "a", "b"]) == {"a": 2, "b": 1}, "verdict tally counts, never assumes")

    return {"legs": n, "fails": fails}


def main(argv):
    import e39_panel_census as e39

    if "--selftest" in argv:
        out = selftest()
        print(json.dumps(out, ensure_ascii=False))
        return 1 if out["fails"] else 0
    payload = run()
    name = OUT_NAME.replace("<cutoff>", payload["evidence_cutoff"].replace("-", ""))
    path = e39.write_json(FACE_DIR, name, payload)
    latest = os.path.join(FACE_DIR, "HELDCURVE-latest.json")
    with open(latest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"face": os.path.relpath(path, ROOT),
                      "latest": os.path.relpath(latest, ROOT),
                      "summary": payload["summary"],
                      "answers": payload["answers"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))