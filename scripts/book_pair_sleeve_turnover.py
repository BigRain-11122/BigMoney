#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""How much of the sleeve's premium reading is the market, and how much is which bonds we hold?

r2185 left this on its own `unverified` list: the sleeve's own premium is the median
premium of the 20 bonds the dual-low rule holds, and a re-pick turns over about half of
them -- so part of every reading is membership, not expensiveness.  This face measures
that part instead of mentioning it.

On each rebalance it prices the same day twice, with the same panel and the same date:

    level_before  = median premium of the bonds held *before* the swap, on date d
    level_after   = median premium of the bonds held *after*  the swap, on date d
    churn_pp      = level_after - level_before        (membership only, no market in it)

`churn_pp` cannot be caused by anything the market did: both sides read the same day.
It is therefore the size of the step a re-pick can put into the ruler without any
information arriving.  Two things follow and both are published:

  (1) how big that step is against the ordinary day-to-day move of the same series;
  (2) whether the step is big enough to move a month-end label across one of the
      tertile edges -- measured with the *actual* edges held fixed, so only the
      reading changes and the ruler cannot drift between the two arms.

The parent face is imported, not re-derived: `book_pair_sleeve_premium.sleeve_premium`
publishes the levels, and this face rebuilds membership with the parent's own eligibility
filter and pick formula and reconciles against those levels (1e-9) before it says
anything.  No weights, no arms, no rules are priced here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACE = "results/book_pair_sleeve_turnover.json"
MD = "results/book_pair_sleeve_turnover.md"
RESEARCH = "research/BOOK_PAIR_SLEEVE_TURNOVER.md"

N_HOLD = 20
REBAL = 20
PHASE = 0
MIN_PRICE = 80.0
MAX_PRICE = 200.0
ITM_PRICE = 130.0
ITM_PREMIUM = 1.0
MIN_COVER = 0.80          # a side whose held bonds lack a premium is not measured
FRESH_BARS = 10           # bars after a swap in which the reading is still "the new bonds"
MIN_HIST = 250            # premium readings before a tertile may be issued
RECON_TOL = 1e-9


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


def _median(vals):
    import numpy as np
    good = [v for v in vals if v is not None and v == v]
    return (float(np.median(good)) if good else None), (len(good) / float(len(vals)) if vals else 0.0)


def swap_measurable(n_before, n_hold=N_HOLD):
    """A rebalance out of a collapsed basket is a restart, not a swap.

    When the sleeve is holding one or two surviving bonds and the rule refills to 20,
    the "churn" is the size difference talking, not the basket changing.  Those bars are
    recorded and excluded by name, so the exclusion is visible in the face.
    """
    return n_before >= max(2, n_hold // 2)


# ---------------------------------------------------------------- the run
def membership_run(panel, n_hold=N_HOLD, rebal=REBAL, phase=PHASE):
    """Rebuild the sleeve's membership and price every swap twice on its own day.

    Mirrors `book_pair_sleeve_premium.sleeve_premium` bar for bar (same eligibility,
    same `close + conv_premium.fillna(50)` pick, same `dates[i-1]` signal / `dates[i]`
    trade grid) and adds what that face does not keep: the holdings either side of
    each swap, and the pre-swap reading for the bars that follow it.
    """
    import numpy as np
    import cb_dual_low as C

    dates = list(panel["date"].drop_duplicates().sort_values())
    by_date = {d: g for d, g in panel.groupby("date")}
    last_seen = panel.groupby("code")["date"].max().to_dict()
    prem_of = {d: dict(zip(g["code"], g["conv_premium"])) for d, g in by_date.items()}

    holds = set()
    levels, cover, naive = [], [], []
    events = []
    pending = []           # (expiry_bar_index, before_set) for the fresh-window readings
    rebalances = 0
    short_pool_skips = 0
    for i, d in enumerate(dates):
        if holds:
            holds = {c for c in holds if last_seen.get(c, d) >= d}
        before = None
        if i > 0 and ((i - 1 - phase) % rebal == 0):
            sig = by_date.get(dates[i - 1])
            if sig is not None and not sig.empty:
                pool = C._eligible(sig, MIN_PRICE, MAX_PRICE, None, ITM_PRICE, ITM_PREMIUM)
                if len(pool) < n_hold:
                    short_pool_skips += 1
                else:
                    pool = pool.assign(score=pool["close"] + pool["conv_premium"].fillna(50.0))
                    before = set(holds)
                    holds = set(pool.nsmallest(n_hold, "score")["code"])
                    rebalances += 1
        today = prem_of.get(d, {})

        def _level(codes):
            vals = [today.get(c) for c in codes] if codes else []
            med, cov = _median(vals)
            return med, cov

        lvl, cv = _level(holds)
        levels.append(lvl if lvl is not None else np.nan)
        cover.append(cv)

        if before:                       # the first pick is not a swap: nothing to leave
            b_lvl, b_cov = _level(before)
            a_lvl, a_cov = _level(holds)
            turnover = (len(before - holds) / float(max(1, len(holds)))) if holds else None
            thin = not (a_lvl is not None and b_lvl is not None
                        and b_cov >= MIN_COVER and a_cov >= MIN_COVER)
            restart = not swap_measurable(len(before), len(holds) or n_hold)
            events.append({
                "bar": int(i),
                "date": str(d.date()),
                "turnover": (round(turnover, 4) if turnover is not None else None),
                "n_before": len(before),
                "n_after": len(holds),
                "level_before_same_day_pct": (round(b_lvl, 4) if b_lvl is not None else None),
                "level_after_same_day_pct": (round(a_lvl, 4) if a_lvl is not None else None),
                "churn_pp": (None if (thin or restart) else round(a_lvl - b_lvl, 4)),
                "why_skipped": ("thin coverage on one side" if thin else
                                ("pre-swap basket had only %d of %d bonds (restart, not a swap)"
                                 % (len(before), n_hold) if restart else None)),
            })
            pending = [(i + FRESH_BARS, set(before))]

        # the counterfactual reading: what the ruler would say if this re-pick had not
        # happened, for the bars that are still close enough to the swap
        alive = [(exp, bset) for exp, bset in pending if i <= exp]
        pending = alive
        if alive and holds:
            _, bset = alive[-1]
            bset = {c for c in bset if last_seen.get(c, d) >= d}
            n_lvl, n_cov = _level(bset)
            naive.append(n_lvl if (n_lvl is not None and n_cov >= MIN_COVER) else np.nan)
        else:
            naive.append(np.nan)

    import pandas as pd
    idx = pd.DatetimeIndex(dates)
    meta = {
        "arm": "n_hold=%d rebal=%d phase=%d" % (n_hold, rebal, phase),
        "filters": "close %g..%g, drop deep-ITM (close>=%g and premium<=%g%%)"
                   % (MIN_PRICE, MAX_PRICE, ITM_PRICE, ITM_PREMIUM),
        "rebalances": rebalances,
        "short_pool_skips": short_pool_skips,
        "first": str(idx[0].date()) if len(idx) else None,
        "last": str(idx[-1].date()) if len(idx) else None,
        "days_with_a_level": int(pd.Series(levels).notna().sum()),
    }
    return (pd.Series(levels, index=idx, dtype=float),
            pd.Series(cover, index=idx, dtype=float),
            pd.Series(naive, index=idx, dtype=float),
            events, meta)


def jump_stats(levels, events):
    """The membership step vs the ordinary step of the same series."""
    import numpy as np

    churn = [e["churn_pp"] for e in events if e.get("churn_pp") is not None]
    measured = [e for e in events if e.get("churn_pp") is not None]
    swap_bars = {e["bar"] for e in measured}
    diffs = levels.diff().abs().dropna()
    quiet = [float(v) for i, v in enumerate(diffs.values)
             if (i + 1) not in swap_bars and v == v]
    turnover = [e["turnover"] for e in measured if e.get("turnover") is not None]
    abs_churn = [abs(v) for v in churn]
    out = {
        "swaps": len(events),
        "swaps_measured": len(churn),
        "swaps_skipped": len(events) - len(churn),
        "turnover_median": (round(float(np.median(turnover)), 4) if turnover else None),
        "churn_abs_median_pp": (round(float(np.median(abs_churn)), 4) if abs_churn else None),
        "churn_abs_p90_pp": (round(float(np.quantile(abs_churn, 0.90)), 4) if abs_churn else None),
        "churn_abs_max_pp": (round(float(max(abs_churn)), 4) if abs_churn else None),
        "churn_signed_median_pp": (round(float(np.median(churn)), 4) if churn else None),
        "churn_direction_up_share": (round(sum(1 for v in churn if v > 0) / float(len(churn)), 4)
                                     if churn else None),
        "quiet_days": len(quiet),
        "quiet_abs_change_median_pp": (round(float(np.median([abs(v) for v in quiet])), 4)
                                       if quiet else None),
        "quiet_abs_change_p90_pp": (round(float(np.quantile([abs(v) for v in quiet], 0.90)), 4)
                                    if quiet else None),
    }
    q = out["quiet_abs_change_median_pp"]
    c = out["churn_abs_median_pp"]
    if q in (None, 0) or c is None:
        out["churn_over_quiet_ratio"] = None
    else:
        out["churn_over_quiet_ratio"] = round(c / q, 3)
    # the largest single swap, in units of an ordinary day
    pq = out["quiet_abs_change_p90_pp"]
    out["biggest_swap_over_quiet_p90"] = (round(out["churn_abs_max_pp"] / pq, 2)
                                          if (pq not in (None, 0) and out["churn_abs_max_pp"] is not None)
                                          else None)
    return out, measured


def _edges(hist):
    import numpy as np
    vals = [v for v in hist if v is not None and v == v]
    if len(vals) < MIN_HIST:
        return None
    return (float(np.quantile(vals, 1.0 / 3.0)), float(np.quantile(vals, 2.0 / 3.0)))


def _bucket(value, edges):
    if edges is None or value is None or value != value:
        return None
    e1, e2 = edges
    return 2 if value >= e2 else (0 if value <= e1 else 1)


def bucket_flip_test(levels, naive, month_ends, fresh_bars=FRESH_BARS):
    """Would the label be the same if the last re-pick had not happened?

    The edges come from the actual series every time (`_edges` on the history up to the
    previous month end), so the ruler is held fixed and only the reading changes --
    otherwise a label difference could be a threshold drift dressed up as churn.
    """
    import numpy as np

    names = {0: "cheap", 1: "mid", 2: "rich"}
    idx = levels.index
    vals = levels.values.astype(float)
    nvals = naive.reindex(idx).values.astype(float)
    rows, exposed, flipped = [], 0, 0
    for k in range(1, len(month_ends)):
        cut = int(idx.searchsorted(month_ends[k - 1], side="right"))
        if cut < 1:
            continue
        edges = _edges(list(vals[:cut]))
        if edges is None:
            continue
        lab = _bucket(vals[cut - 1], edges)
        alt_val = nvals[cut - 1]
        alt = _bucket(alt_val, edges)
        if lab is None:
            continue
        is_fresh = alt is not None
        if is_fresh:
            exposed += 1
        if is_fresh and alt != lab:
            flipped += 1
        rows.append({
            "month_ending": str(month_ends[k].date()),
            "reading_pct": round(float(vals[cut - 1]), 4),
            "label": names[lab],
            "counterfactual_reading_pct": (round(float(alt_val), 4) if is_fresh else None),
            "counterfactual_label": (names[alt] if is_fresh else None),
            "near_a_swap": bool(is_fresh),
            "bucket_changed_by_the_swap": bool(is_fresh and alt != lab),
        })
    return {
        "month_ends_examined": len(rows),
        "month_ends_near_a_swap": exposed,
        "month_ends_with_changed_bucket": flipped,
        "fresh_bars": int(fresh_bars),
        "rows": rows,
    }


def verdict_of(jumps, flips, today_blk):
    """Ordered by what a reader would have to act on first."""
    if not jumps.get("swaps_measured"):
        return "NOT_MEASURABLE_NO_SWAP_PRICED_BOTH_SIDES"
    if flips.get("month_ends_with_changed_bucket"):
        return "THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET"
    margin = (today_blk or {}).get("margin_to_nearest_edge_pp")
    p90 = jumps.get("churn_abs_p90_pp")
    if margin is not None and p90 is not None and margin < p90:
        return "TODAY_SITS_INSIDE_THE_SWAP_NOISE"
    ratio = jumps.get("churn_over_quiet_ratio")
    if ratio is not None and ratio < 1.0:
        return "MEMBERSHIP_CHURN_IS_THE_SMALLER_PART_OF_THE_READING"
    return "CHURN_IS_LARGE_BUT_NO_BUCKET_MOVED"


# ---------------------------------------------------------------- today
def today_block(levels, jumps, parent_current=None):
    """The live reading, its distance to each edge, and the churn step it carries."""
    import numpy as np

    vals = levels.values.astype(float)
    good = vals[~np.isnan(vals)]
    if not len(good):
        return {"missing": True}
    p = float(good[-1])
    edges = _edges(list(good))
    blk = {
        "asof": str(levels.index[levels.notna().values].max().date()),
        "reading_pct": round(p, 3),
        "cheap_below_pct": (round(edges[0], 3) if edges else None),
        "rich_above_pct": (round(edges[1], 3) if edges else None),
        "label_spot": (_bucket(p, edges) if edges else None),
        "churn_abs_median_pp": jumps.get("churn_abs_median_pp"),
        "churn_abs_p90_pp": jumps.get("churn_abs_p90_pp"),
    }
    if edges:
        blk["margin_to_cheap_edge_pp"] = round(p - edges[0], 3)
        blk["margin_to_rich_edge_pp"] = round(edges[1] - p, 3)
        blk["margin_to_nearest_edge_pp"] = round(min(abs(p - edges[0]), abs(edges[1] - p)), 3)
        p90 = jumps.get("churn_abs_p90_pp")
        blk["inside_the_swap_noise"] = (bool(p90 is not None
                                            and blk["margin_to_nearest_edge_pp"] < p90))
    blk["label_names"] = {0: "cheap", 1: "mid", 2: "rich"}.get(blk.get("label_spot"))
    if parent_current:
        blk["parent_label_in_force"] = parent_current.get("label_in_force")
        blk["parent_read_at_month_end"] = parent_current.get("read_at_month_end")
    return blk


# ---------------------------------------------------------------- verify / check
def _verify(face, stamps=None):
    problems = []
    if face.get("face") != FACE:
        problems.append("face pointer %r" % face.get("face"))
    if not face.get("evidence_cutoff"):
        problems.append("no evidence_cutoff")
    j = face.get("jumps") or {}
    if j.get("swaps_measured", 0) > j.get("swaps", 0):
        problems.append("more swaps measured than swaps seen")
    if j.get("swaps", 0) and not j.get("swaps_measured"):
        problems.append("no swap priced on both sides despite %s swaps" % j.get("swaps"))
    t = face.get("timing") or {}
    if not t.get("rebalances"):
        problems.append("timing block empty")
    rec = face.get("reconciliation") or {}
    if rec.get("ok") is not True:
        problems.append("parent levels not reconciled: max_abs_diff=%r"
                        % rec.get("max_abs_diff"))
    f = face.get("labels") or {}
    if f.get("month_ends_with_changed_bucket", 0) > f.get("month_ends_near_a_swap", 0):
        problems.append("more bucket changes than months near a swap")
    v = face.get("verdict")
    again = verdict_of(j, f, face.get("today") or {})
    if v != again:
        problems.append("verdict %r does not recompute (%r)" % (v, again))
    drift = []
    if stamps:
        for key, want in stamps.items():
            got = (face.get("inputs") or {}).get(key) or {}
            if key == "cb":
                got = got.get("panel") or {}
            got = got.get("stamp") or got
            if want.get("missing"):
                drift.append("%s missing on disk" % key)
            elif got.get("size") != want.get("size") or got.get("mtime") != want.get("mtime"):
                drift.append("%s moved (face %s/%s, disk %s/%s)"
                             % (key, got.get("size"), got.get("mtime"),
                                want.get("size"), want.get("mtime")))
    if drift:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "drift": drift, "kind": "CHECK STALE FACE_DRIFT"}
    if problems:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "kind": "CHECK FAILED"}
    return {"ok": True, "verdict": face.get("verdict"), "problems": [], "kind": "CHECK OK"}


def check():
    p = _rp(FACE)
    if not os.path.exists(p):
        print(json.dumps({"ok": False, "kind": "CHECK STALE face missing", "path": p},
                         ensure_ascii=False))
        return 2
    with open(p, encoding="utf-8") as fh:
        face = json.load(fh)
    stamps = {
        "cb": _stamp(_rp("data/cb_panel.csv.gz")),
        "parent": _stamp(_rp("results/book_pair_sleeve_premium.json")),
    }
    res = _verify(face, stamps)
    print(json.dumps(res, ensure_ascii=False))
    if res["ok"]:
        return 0
    return 3 if res.get("kind", "").startswith("CHECK FAILED") else 2


# ---------------------------------------------------------------- build
def build(write=True, quiet=False):
    from_shell = not quiet

    def say(msg):
        if from_shell:
            sys.stdout.write(msg + "\n")

    import book_pair_cushion_regime as Cu
    import book_pair_sleeve_premium as P
    import cb_dual_low as C

    say("[1/4] loading the cb panel once ...")
    panel = C._load_panel()
    inp = Cu.load_inputs()
    cb, etf = inp["cb"], inp["etf"]
    say("      cb bars=%d  etf bars=%d  panel rows=%d" % (len(cb), len(etf), len(panel)))

    say("[2/4] rebuilding membership and pricing every swap on its own day ...")
    levels, cover, naive, events, meta = membership_run(panel)
    say("      rebalances=%d  swaps both sides priced=%d  days=%d"
        % (meta["rebalances"],
           sum(1 for e in events if e.get("churn_pp") is not None),
           meta["days_with_a_level"]))

    say("[3/4] reconciling against the parent face's published levels ...")
    parent_levels, parent_cover, parent_meta = P.sleeve_premium(panel)
    j = levels.index.intersection(parent_levels.index)
    a = levels.reindex(j).values.astype(float)
    b = parent_levels.reindex(j).values.astype(float)
    both = [(x, y) for x, y in zip(a, b) if x == x and y == y]
    max_diff = max((abs(x - y) for x, y in both), default=None)
    recon = {
        "parent_rebalances": parent_meta.get("rebalances"),
        "my_rebalances": meta.get("rebalances"),
        "days_compared": len(both),
        "max_abs_diff": (round(float(max_diff), 12) if max_diff is not None else None),
        "tol": RECON_TOL,
        "ok": bool(max_diff is not None and max_diff <= RECON_TOL),
    }
    say("      reconciled=%s max_abs_diff=%s over %d days"
        % (recon["ok"], recon["max_abs_diff"], recon["days_compared"]))

    say("[4/4] the step, the ordinary day, and the month-end labels ...")
    jumps, measured = jump_stats(levels, events)
    mi, mc, me, mb = Cu.monthly_frame(cb, etf, inp["w"])
    month_ends = list(mi)
    flips = bucket_flip_test(levels, naive, month_ends)
    parent_face = {}
    pp = _rp(P.FACE)
    if os.path.exists(pp):
        try:
            with open(pp, encoding="utf-8") as fh:
                parent_face = (json.load(fh).get("current") or {}).get("sleeve_ruler") or {}
        except Exception:
            parent_face = {}
    today = today_block(levels, jumps, parent_current=parent_face)
    verd = verdict_of(jumps, flips, today)
    # the swaps that moved the ruler hardest, for the reader who wants the episodes
    big = sorted([e for e in measured if e.get("churn_pp") is not None],
                 key=lambda e: -abs(e["churn_pp"]))[:8]

    face = {
        "face": FACE,
        "generated_at": _now_iso(),
        "evidence_cutoff": min(str(etf.index[-1].date()),
                               str(cb.index[-1].date()),
                               (meta.get("last") or "9999-12-31")),
        "panels": {
            "etf": str(etf.index[-1].date()),
            "cb_arm": str(cb.index[-1].date()),
            "sleeve_premium": meta.get("last"),
        },
        "question": ("How much of the sleeve's own premium reading is which 20 bonds the "
                     "rule happens to hold, rather than how expensive they are?"),
        "caliber": {
            "membership": ("rebuilt with `cb_dual_low._eligible` and the parent's "
                           "`close + conv_premium.fillna(50)` pick on the parent's "
                           "rebal=%d / phase=%d grid" % (REBAL, PHASE)),
            "churn_pp": ("median premium of the post-swap 20 minus median premium of the "
                         "pre-swap 20, both read on the swap date itself -- the market "
                         "cannot move between the two sides"),
            "coverage_gate": ("a side is priced only when at least %.0f%% of its bonds "
                              "carry a premium that day" % (100.0 * MIN_COVER)),
            "quiet_days": "days that are not a swap day, |level - previous level|",
            "labels": ("tertiles of the *actual* series up to the previous month end, held "
                       "fixed for both readings; the counterfactual reading uses the "
                       "pre-swap holdings for the first %d bars after a swap" % FRESH_BARS),
            "parent_reconciliation": "levels compared bar for bar at 1e-9",
        },
        "window": {
            "first": meta.get("first"),
            "last": meta.get("last"),
            "last_bar": str(etf.index[-1].date()),
            "month_ends": len(month_ends),
        },
        "inputs": {
            "cb": {"panel": _stamp(_rp("data/cb_panel.csv.gz")), "meta": meta},
            "parent": _stamp(pp),
        },
        "timing": {
            "rebalances": meta.get("rebalances"),
            "short_pool_skips": meta.get("short_pool_skips"),
            "rebal_bars": REBAL,
            "fresh_bars": FRESH_BARS,
        },
        "reconciliation": recon,
        "jumps": jumps,
        "biggest_swaps": big,
        "labels": {k: v for k, v in flips.items() if k != "rows"},
        "label_rows": flips["rows"],
        "today": today,
        "verdict": verd,
        "unverified": [
            "membership is rebuilt from the parent's pick formula because neither parent "
            "publishes its holdings; the 1e-9 reconciliation only proves the two "
            "implementations agree, not that either equals the traded book",
            "the counterfactual reading drops bonds that delisted since the swap, so a "
            "swap that saved a defaulted name flatters the pre-swap side in those months",
            "a tertile label is a coarse ruler: a reading that moves 3pp inside the mid "
            "bucket is invisible to this face even though it is the same 3pp the desk sees",
            "churn_pp is a median-of-medians: two sets of 20 with the same median can "
            "differ in every bond, so this is a lower bound on membership noise",
        ],
    }
    if write:
        with open(_rp(FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(_rp(MD), "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        with open(_rp(RESEARCH), "w", encoding="utf-8") as fh:
            fh.write(render_research(face))
    say("      verdict=%s  churn median=%spp  p90=%spp  quiet day median=%spp"
        % (verd, jumps.get("churn_abs_median_pp"), jumps.get("churn_abs_p90_pp"),
           jumps.get("quiet_abs_change_median_pp")))
    return face


# ---------------------------------------------------------------- rendering
def _n(v, dash="n/a", nd=2):
    return dash if v is None else ("%.*f" % (nd, v))


def render_md(face):
    j = face["jumps"]
    t = face["today"]
    f = face["labels"]
    rec = face["reconciliation"]
    L = []
    L.append("# The sleeve's premium reading: how much of it is which bonds we hold?\n")
    L.append("generated %s · evidence cutoff %s · bar %s\n"
             % (face["generated_at"], face["evidence_cutoff"], face["window"]["last_bar"]))
    L.append("**%s**\n" % face["verdict"])
    L.append("\n| what | value |\n|---|---|")
    L.append("| swaps seen / priced on both sides | %s / %s |"
             % (j.get("swaps"), j.get("swaps_measured")))
    L.append("| median turnover per swap | %s |"
             % (_n((j.get("turnover_median") or 0) * 100.0, nd=1) + "%"
                if j.get("turnover_median") is not None else "n/a"))
    L.append("| membership step: median |churn| | %s pp |" % _n(j.get("churn_abs_median_pp")))
    L.append("| membership step: p90 |churn| | %s pp |" % _n(j.get("churn_abs_p90_pp")))
    L.append("| membership step: largest |churn| | %s pp |" % _n(j.get("churn_abs_max_pp")))
    L.append("| ordinary day (not a swap): median |change| | %s pp |"
             % _n(j.get("quiet_abs_change_median_pp")))
    L.append("| ordinary day: p90 |change| | %s pp |" % _n(j.get("quiet_abs_change_p90_pp")))
    L.append("| churn median ÷ ordinary-day median | %s |" % _n(j.get("churn_over_quiet_ratio")))
    L.append("| biggest swap ÷ ordinary-day p90 | %s |"
             % _n(j.get("biggest_swap_over_quiet_p90")))
    L.append("\n## Does a swap alone move a label?\n")
    L.append("- month ends examined: **%s**; within %s bars of a swap: **%s**; "
             "bucket changed by the swap alone: **%s**."
             % (f.get("month_ends_examined"), f.get("fresh_bars"),
                f.get("month_ends_near_a_swap"), f.get("month_ends_with_changed_bucket")))
    L.append("- the edges are the *actual* series' own tertiles, held fixed for both "
             "readings, so a change here is the reading moving, not the ruler drifting.\n")
    L.append("\n## Today\n")
    L.append("| what | value |\n|---|---|")
    L.append("| reading (%s) | %s%% |" % (t.get("asof"), _n(t.get("reading_pct"), nd=3)))
    L.append("| cheap below / rich above | %s%% / %s%% |"
             % (_n(t.get("cheap_below_pct"), nd=3), _n(t.get("rich_above_pct"), nd=3)))
    L.append("| distance to nearest edge | %s pp |" % _n(t.get("margin_to_nearest_edge_pp")))
    L.append("| swap step p90 | %s pp |" % _n(t.get("churn_abs_p90_pp")))
    L.append("| reading sits inside the swap step | %s |"
             % ("yes" if t.get("inside_the_swap_noise") else "no"))
    if t.get("parent_label_in_force"):
        L.append("| label in force (parent face, read %s) | %s |"
                 % (t.get("parent_read_at_month_end"), t.get("parent_label_in_force")))
    L.append("\n## Reconciliation with the parent face\n")
    L.append("`%s` — %s days compared, max |diff| **%s** (tolerance %s).\n"
             % ("book_pair_sleeve_premium.sleeve_premium", rec.get("days_compared"),
                rec.get("max_abs_diff"), rec.get("tol")))
    if face.get("biggest_swaps"):
        L.append("\n## The swaps that moved it most\n")
        L.append("| date | turnover | before | after | churn (pp) |\n|---|---|---|---|---|")
        for e in face["biggest_swaps"]:
            L.append("| %s | %s | %s | %s | %s |"
                     % (e["date"],
                        (_n(e["turnover"] * 100.0, nd=0) + "%") if e.get("turnover") is not None else "n/a",
                        _n(e.get("level_before_same_day_pct")),
                        _n(e.get("level_after_same_day_pct")),
                        _n(e.get("churn_pp"))))
    L.append("\n## What this face does not claim\n")
    for u in face.get("unverified") or []:
        L.append("- %s" % u)
    L.append("")
    return "\n".join(L)


def render_research(face):
    j = face["jumps"]
    f = face["labels"]
    t = face["today"]
    L = []
    L.append("# BOOK_PAIR_SLEEVE_TURNOVER\n")
    L.append("Q: %s\n" % face["question"])
    L.append("Verdict: **%s**\n" % face["verdict"])
    L.append("## Mechanism\n")
    L.append("The sleeve ruler is a median over 20 bonds. A re-pick holds on to roughly ")
    L.append("%s of them and swaps the rest, so the ruler's next reading is taken over a ")
    L.append("partly different basket. This face prices that basket change on one date: ")
    L.append("the same 20 before the swap and the same 20 after, both read on the swap ")
    L.append("date. Anything the market did cancels out, so what is left is membership.\n")
    L.append("\n## Numbers\n")
    L.append("- median |churn| **%s pp**, p90 **%s pp**, max **%s pp**"
             % (_n(j.get("churn_abs_median_pp")), _n(j.get("churn_abs_p90_pp")),
                _n(j.get("churn_abs_max_pp"))))
    L.append("- ordinary (non-swap) day: median **%s pp**, p90 **%s pp**"
             % (_n(j.get("quiet_abs_change_median_pp")), _n(j.get("quiet_abs_change_p90_pp"))))
    L.append("- ratio churn/ordinary **%s**; biggest swap is **%sx** an ordinary p90 day"
             % (_n(j.get("churn_over_quiet_ratio")), _n(j.get("biggest_swap_over_quiet_p90"))))
    L.append("- month ends within %s bars of a swap: **%s**, of which a bucket changed: **%s**"
             % (f.get("fresh_bars"), f.get("month_ends_near_a_swap"),
                f.get("month_ends_with_changed_bucket")))
    L.append("- today: reading **%s%%**, nearest edge **%s pp** away, swap p90 **%s pp** "
             "→ inside the swap step: **%s**"
             % (_n(t.get("reading_pct"), nd=3), _n(t.get("margin_to_nearest_edge_pp")),
                _n(t.get("churn_abs_p90_pp")),
                "yes" if t.get("inside_the_swap_noise") else "no"))
    L.append("\n## How to use it\n")
    L.append("Two sentences a reader can act on. First: when a label is decided within a ")
    L.append("couple of weeks of a re-pick, the reading it is decided on carries a step ")
    L.append("that no market event produced — the table above says how big that step is ")
    L.append("in the units the reader already knows (pp of premium). Second: if the reading ")
    L.append("sits closer to an edge than that step, the label could have gone the other ")
    L.append("way for reasons that are not about expensiveness at all.\n")
    L.append("\n## What is not measured\n")
    for u in face.get("unverified") or []:
        L.append("- %s" % u)
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- selftest
def selftest():
    import numpy as np
    import pandas as pd

    legs = []

    def leg(name):
        def deco(fn):
            try:
                fn()
                legs.append((name, "PASS", ""))
            except AssertionError as exc:
                legs.append((name, "FAIL", str(exc)))
            except Exception as exc:                     # noqa: BLE001
                legs.append((name, "ERROR", "%s: %s" % (type(exc).__name__, exc)))
            return fn
        return deco

    def _panel(rows):
        df = pd.DataFrame(rows, columns=["date", "code", "close", "conv_premium",
                                         "conv_value", "pure_bond_value"])
        df["date"] = pd.to_datetime(df["date"])
        df["pure_bond_premium"] = 10.0
        df["swap_price"] = np.nan
        df["name"] = df["code"]
        return df

    @leg("a swap is priced on its own day, both sides on the same date")
    def t_swap_is_same_day():
        # the basket is renamed wholesale on bar 3, and both baskets happen to have the
        # same median premium -- so a correctly priced swap must read exactly zero
        rows = []
        for i in range(8):
            for c in ["A", "B", "C", "D"]:
                p = {"A": 10.0, "B": 20.0, "C": 30.0, "D": 40.0}[c]
                if i >= 2:            # one bar before the trade, so the lagged signal sees it
                    p = {"A": 55.0, "B": 65.0, "C": 15.0, "D": 25.0}[c]
                rows.append((pd.Timestamp("2024-01-01") + pd.Timedelta(days=i), c,
                             90.0, p, 100.0, 100.0))
        panel = _panel(rows)
        levels, cover, naive, events, meta = membership_run(panel, n_hold=2, rebal=2, phase=0)
        got = [e for e in events if e.get("churn_pp") is not None]
        assert got, events
        d = pd.Timestamp(got[0]["date"])
        day = panel[panel["date"] == d].set_index("code")["conv_premium"]
        # the two baskets are read off the same date, so both sides are that day's prices
        assert abs(got[0]["level_before_same_day_pct"] - float(day[["A", "B"]].median())) < 1e-6, got[0]
        assert abs(got[0]["level_after_same_day_pct"] - float(day[["C", "D"]].median())) < 1e-6, got[0]
        assert got[0]["turnover"] > 0.0, got[0]   # the baskets did change

    @leg("churn is membership only: the step equals the two medians on that date")
    def t_churn_is_membership():
        rows = []
        for i in range(8):
            for c in ["A", "B", "C", "D"]:
                p = {"A": 20.0, "B": 30.0, "C": 45.0, "D": 55.0}[c]
                if i >= 2:            # A,B become the expensive pair and get dropped
                    p = {"A": 70.0, "B": 80.0, "C": 45.0, "D": 55.0}[c]
                rows.append((pd.Timestamp("2024-01-01") + pd.Timedelta(days=i), c,
                             90.0, p, 100.0, 100.0))
        panel = _panel(rows)
        levels, cover, naive, events, meta = membership_run(panel, n_hold=2, rebal=2, phase=0)
        got = [e for e in events if e.get("churn_pp") is not None]
        assert got, events
        e = got[0]
        assert abs(e["churn_pp"] - (e["level_after_same_day_pct"]
                                    - e["level_before_same_day_pct"])) < 1e-6, e
        assert e["churn_pp"] < -1.0, e      # swapping into a cheaper pair moves it down
        # and the day's own level is the post-swap basket, not the pre-swap one
        assert levels.loc[pd.Timestamp(e["date"])] == e["level_after_same_day_pct"]

    @leg("the counterfactual reading uses the pre-swap basket for a bounded window")
    def t_counterfactual_window():
        rows = []
        base = pd.Timestamp("2024-02-01")
        for i in range(30):
            for c in ["A", "B", "C", "D"]:
                p = {"A": 10.0, "B": 12.0, "C": 30.0, "D": 40.0}[c] + (3.0 if i >= 3 else 0.0)
                rows.append((base + pd.Timedelta(days=i), c, 90.0, p, 100.0, 100.0))
        panel = _panel(rows)
        levels, cover, naive, events, meta = membership_run(panel, n_hold=2, rebal=4, phase=0)
        got = naive.notna().sum()
        assert got > 0, "counterfactual never produced a reading"
        assert got <= FRESH_BARS * max(1, meta["rebalances"]) + 2, (got, meta)

    @leg("thin coverage is skipped, not guessed")
    def t_thin_coverage_skipped():
        rows = []
        for i in range(6):
            for c in ["A", "B"]:
                rows.append(("2024-03-0%d" % (i + 1), c, 90.0, 10.0, 100.0, 100.0))
            rows.append(("2024-03-0%d" % (i + 1), "C", 90.0, np.nan, 100.0, 100.0))
        panel = _panel(rows)
        levels, cover, naive, events, meta = membership_run(panel, n_hold=3, rebal=2, phase=0)
        # with 3 names one of which has no premium, the median is still quoted but the
        # coverage gate is what decides whether a swap may be priced
        assert meta["rebalances"] >= 1
        assert all(e["churn_pp"] is None or cover.min() <= 1.0 for e in events)

    @leg("jump stats separate swap days from ordinary days")
    def t_jump_stats():
        idx = pd.date_range("2024-01-01", periods=6, freq="D")
        levels = pd.Series([10.0, 12.0, 12.0, 20.0, 20.0, 20.0], index=idx)
        events = [{"bar": 3, "churn_pp": 5.0}, {"bar": 2, "churn_pp": -2.0}]
        j, measured = jump_stats(levels, events)
        assert j["swaps_measured"] == 2
        assert abs(j["churn_abs_median_pp"] - 3.5) < 1e-9, j
        # quiet days are every day except the swap bars: 2.0, 0.0, 0.0
        assert abs(j["quiet_abs_change_median_pp"] - 0.0) < 1e-9, j
        assert len(measured) == 2

    @leg("the flip test holds the edges fixed and only moves the reading")
    def t_flip_uses_actual_edges():
        idx = pd.date_range("2020-01-01", periods=900, freq="D")
        base = 5.0 + 0.02 * np.arange(900) + np.sin(np.arange(900) / 9.0)
        levels = pd.Series(base, index=idx)
        naive = levels.copy()
        me = pd.date_range("2021-06-30", periods=6, freq="ME")
        a = bucket_flip_test(levels, naive, list(me))
        assert a["month_ends_examined"] >= 4, a
        assert a["month_ends_with_changed_bucket"] == 0, a
        # nudge one month-end reading far enough to cross an edge; the ruler is the same
        # series' own edges, so this isolates the reading
        cut = int(idx.searchsorted(me[2], side="right")) - 1
        naive.iloc[cut] = base[cut] - 40.0
        b = bucket_flip_test(levels, naive, list(me))
        assert b["month_ends_with_changed_bucket"] >= 1, b
        row = [r for r in b["rows"] if r["month_ending"] == str(me[3].date())][0]
        assert row["bucket_changed_by_the_swap"] is True, row

    @leg("a reading nobody could measure yields zero flips, not a clean bill")
    def t_no_measure_no_flip():
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        levels = pd.Series(np.nan, index=idx)
        naive = levels.copy()
        me = pd.date_range("2020-02-29", periods=4, freq="ME")
        b = bucket_flip_test(levels, naive, list(me))
        assert b["month_ends_with_changed_bucket"] == 0
        assert b["month_ends_near_a_swap"] == 0

    @leg("verdict order: a bucket that moved outranks a big step")
    def t_verdict_order():
        jumps = {"swaps_measured": 5, "churn_abs_p90_pp": 1.0,
                 "churn_over_quiet_ratio": 0.5}
        assert verdict_of(jumps, {"month_ends_with_changed_bucket": 1},
                          {"margin_to_nearest_edge_pp": 9.0}) == \
            "THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET"
        assert verdict_of(jumps, {"month_ends_with_changed_bucket": 0},
                          {"margin_to_nearest_edge_pp": 0.5}) == \
            "TODAY_SITS_INSIDE_THE_SWAP_NOISE"
        assert verdict_of(jumps, {"month_ends_with_changed_bucket": 0},
                          {"margin_to_nearest_edge_pp": 9.0}) == \
            "MEMBERSHIP_CHURN_IS_THE_SMALLER_PART_OF_THE_READING"
        assert verdict_of({"swaps_measured": 0}, {}, {}) == \
            "NOT_MEASURABLE_NO_SWAP_PRICED_BOTH_SIDES"

    @leg("today's block reports the margin in the same units as the step")
    def t_today_block():
        idx = pd.date_range("2020-01-01", periods=500, freq="D")
        levels = pd.Series(np.linspace(5.0, 20.0, 500), index=idx)
        blk = today_block(levels, {"churn_abs_median_pp": 0.5, "churn_abs_p90_pp": 1.0})
        assert blk["reading_pct"] is not None
        assert blk["margin_to_nearest_edge_pp"] is not None
        assert isinstance(blk["inside_the_swap_noise"], bool)

    @leg("_verify refuses a verdict that does not recompute")
    def t_verify_verdict():
        face = {"face": FACE, "evidence_cutoff": "2026-11-26",
                "jumps": {"swaps": 1, "swaps_measured": 1, "churn_abs_median_pp": 0.2,
                          "churn_abs_p90_pp": 0.3, "churn_over_quiet_ratio": 0.4},
                "timing": {"rebalances": 1},
                "reconciliation": {"ok": True, "max_abs_diff": 0.0},
                "labels": {"month_ends_with_changed_bucket": 0, "month_ends_near_a_swap": 0},
                "today": {"margin_to_nearest_edge_pp": 9.0},
                "verdict": "THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET"}
        res = _verify(face)
        assert res["ok"] is False and any("recompute" in p for p in res["problems"]), res
        face["verdict"] = "MEMBERSHIP_CHURN_IS_THE_SMALLER_PART_OF_THE_READING"
        assert _verify(face)["ok"] is True, _verify(face)

    @leg("_verify refuses reconciliation that did not happen")
    def t_verify_recon():
        face = {"face": FACE, "evidence_cutoff": "2026-11-26",
                "jumps": {"swaps": 1, "swaps_measured": 1, "churn_abs_median_pp": 0.2,
                          "churn_abs_p90_pp": 0.3, "churn_over_quiet_ratio": 0.4},
                "timing": {"rebalances": 1},
                "reconciliation": {"ok": False, "max_abs_diff": 0.5},
                "labels": {"month_ends_with_changed_bucket": 0, "month_ends_near_a_swap": 0},
                "today": {"margin_to_nearest_edge_pp": 9.0},
                "verdict": "MEMBERSHIP_CHURN_IS_THE_SMALLER_PART_OF_THE_READING"}
        res = _verify(face)
        assert res["ok"] is False and any("reconcil" in p for p in res["problems"]), res

    @leg("an input that moved is called STALE, not failed")
    def t_verify_stale_word():
        face = {"face": FACE, "evidence_cutoff": "2026-11-26",
                "jumps": {"swaps": 1, "swaps_measured": 1, "churn_abs_median_pp": 0.2,
                          "churn_abs_p90_pp": 0.3, "churn_over_quiet_ratio": 0.4},
                "timing": {"rebalances": 1},
                "reconciliation": {"ok": True, "max_abs_diff": 0.0},
                "labels": {"month_ends_with_changed_bucket": 0, "month_ends_near_a_swap": 0},
                "today": {"margin_to_nearest_edge_pp": 9.0},
                "inputs": {"cb": {"panel": {"size": 1, "mtime": "2026-11-26T00:00:00"}}},
                "verdict": "MEMBERSHIP_CHURN_IS_THE_SMALLER_PART_OF_THE_READING"}
        res = _verify(face, {"cb": {"size": 2, "mtime": "2026-11-27T00:00:00"}})
        assert res["ok"] is False and "STALE" in res["kind"], res

    @leg("a refill out of a collapsed basket is a restart, not a swap")
    def t_restart_not_a_swap():
        assert swap_measurable(20, 20) is True
        assert swap_measurable(10, 20) is True
        assert swap_measurable(9, 20) is False
        assert swap_measurable(1, 20) is False
        # and the run never prices a churn for one of them
        rows = []
        base = pd.Timestamp("2024-05-01")
        for i in range(40):
            for c in ["A", "B"]:
                rows.append((base + pd.Timedelta(days=i), c, 90.0, 20.0, 100.0, 100.0))
            if i < 2:
                rows.append((base + pd.Timedelta(days=i), "C", 90.0, 5.0, 100.0, 100.0))
        panel = _panel(rows)
        levels, cover, naive, events, meta = membership_run(panel, n_hold=2, rebal=2, phase=0)
        assert all(e["churn_pp"] is None for e in events if e["n_before"] < 1), events
        assert all("restart" in (e["why_skipped"] or "") for e in events if e["n_before"] == 1), events

    @leg("markdown prints the step and the margin it is compared against")
    def t_md_prints_both():
        face = {"face": FACE, "generated_at": "2026-11-27T00:00:00", "evidence_cutoff": "2026-11-26",
                "question": "q",
                "window": {"last_bar": "2026-11-27", "month_ends": 80},
                "jumps": {"swaps": 10, "swaps_measured": 9, "turnover_median": 0.5,
                          "churn_abs_median_pp": 0.4, "churn_abs_p90_pp": 1.2,
                          "churn_abs_max_pp": 3.0, "quiet_abs_change_median_pp": 0.3,
                          "quiet_abs_change_p90_pp": 0.9, "churn_over_quiet_ratio": 1.3,
                          "biggest_swap_over_quiet_p90": 3.3},
                "labels": {"month_ends_examined": 80, "month_ends_near_a_swap": 4,
                           "month_ends_with_changed_bucket": 0, "fresh_bars": 10},
                "today": {"asof": "2026-11-26", "reading_pct": 8.769,
                          "cheap_below_pct": 9.246, "rich_above_pct": 15.233,
                          "margin_to_nearest_edge_pp": 0.477, "churn_abs_p90_pp": 1.2,
                          "inside_the_swap_noise": True},
                "reconciliation": {"days_compared": 4700, "max_abs_diff": 0.0, "tol": 1e-9},
                "biggest_swaps": [], "unverified": ["x"], "verdict": "TODAY_SITS_INSIDE_THE_SWAP_NOISE"}
        md = render_md(face)
        assert "TODAY_SITS_INSIDE_THE_SWAP_NOISE" in md
        assert "0.48" in md and "1.20" in md, md
        assert "inside the swap step" in md
        rs = render_research(face)
        assert "TODAY_SITS_INSIDE_THE_SWAP_NOISE" in rs

    for name, status, why in legs:
        sys.stdout.write("%-5s %s%s\n" % (status, name, ("" if status == "PASS" else "  <- " + why)))
    bad = [l for l in legs if l[1] != "PASS"]
    sys.stdout.write("%d/%d legs pass\n" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="build",
                    choices=["build", "check", "show", "selftest"])
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "show":
        with open(_rp(FACE), encoding="utf-8") as fh:
            print(json.dumps(json.load(fh), ensure_ascii=False, indent=1))
        return 0
    face = build(write=not args.no_write)
    if not args.no_write:
        res = _verify(face, {"cb": _stamp(_rp("data/cb_panel.csv.gz")),
                             "parent": _stamp(_rp("results/book_pair_sleeve_premium.json"))})
        print(json.dumps({"kind": res["kind"], "verdict": res["verdict"],
                          "problems": res["problems"]}, ensure_ascii=False))
        return 0 if res["ok"] else 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
