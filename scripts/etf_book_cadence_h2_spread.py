# -*- coding: utf-8 -*-
"""why did the cross-book spread inside one quarter blow up in 2025H2 -- and is it chance?

WHY THIS FILE EXISTS
--------------------
r2130 (scripts/etf_book_cadence_regime_split.py) measured, per calendar quarter, how far apart
six start-date books sit when they are handed the SAME quarter and the SAME rule (only the entry
date differs). It published the widening and then named the one thing it could not answer, in its
own honest block:

    2025Q3/Q4 segment cross-book range rose to 5.21 / 10.28 pp, an order of magnitude above the
    full-year median -- "later quarters where books are shorter and ordering more dispersed, the
    entry date starts to bite again"

That sentence contains three different claims that point at three different remedies, and nothing
in r2130 separated them:

  A window length   -- a quarter with fewer bars is noisier, so any spread measured on it is bigger
  B market breadth  -- if single names moved far apart in that quarter, books holding different
                       names MUST disagree, with no strategy involved
  C real phase risk -- books disagree because the rule's text at different phases points at
                       genuinely different names, and that is a risk the risk dial must carry

This face answers which. It reads the same panel, the same engine, the same start dates as r2130
(zero reimplementation: RS.build_inputs / RS.slice_ret / RS.spread / RS.quartiles imported), and
adds four readings r2130 never took:

  1 bars per quarter slice -- measured, not assumed (kills or confirms channel A)
  2 breadth: cross-sectional IQR of single-name quarterly returns over the whole tradable universe
  3 holdings: for each book, the union of names it actually picks inside that quarter (the pick is
    "top n_hold by score at a rebalance bar", recomputed from the same score panel), then the mean
    pairwise Jaccard across books -- if books hold the same names they cannot disagree much
  4 chance: NULL_DRAWS permutation-score books (per-bar shuffle of the finite score row, same
    starts, same cadences), each giving its own per-quarter cross-book spread. If the random books
    widen in 2025H2 too, the widening is not a property of the signal.

It also extends the grid to 2026Q1..Q4, which r2130's segment list stopped short of, so the
reader can see whether 2025H2 was a one-off or the new normal.

WHAT IT IS NOT
--------------
No verdict on the production ticket (results/etf_book_rebal_adoption.json stays PHASE_DEPENDENT).
No new engine, no re-fitted thresholds: every word below is recomputed by `check` from the numbers
this face prints.

self  python scripts/etf_book_cadence_h2_spread.py selftest
run   python scripts/etf_book_cadence_h2_spread.py run
check python scripts/etf_book_cadence_h2_spread.py check
"""

import hashlib
import json
import os
import statistics as st
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_h2_spread.json")
FACE = "results/etf_book_cadence_h2_spread.json"
SCHEMA = "etf-book-cadence-h2-spread/v1"

BASE_MONEY = 1_000_000.0
N_HOLD = 5
CADENCES = (10, 20)
COST_KEY, COST = "8bp", 0.0008
MIN_BARS = 30              # a quarter slice shorter than this is a named hole, never a zero
NULL_DRAWS = 4             # permutation-score books; each is a full 12-book family
NULL_SEED = 20261126

# identical to r2130 so the two faces read the same books
STARTS = ["2021-09-01", "2022-03-01", "2022-09-01", "2023-03-01", "2023-09-01", "2024-03-01"]
LEGACY_SEGMENTS = 2022, 2025     # r2130's grid, kept so the overlap can be cross-checked
EXTENDED_SEGMENTS = 2022, 2026   # this face's grid: adds 2026Q1..Q4

H2_2025 = ["2025Q3", "2025Q4"]

# frozen before the first run of this round
RATIO_EXCEEDS = 1.8        # actual H2 spread >= 1.8x the null's -> widening is not chance
RATIO_CHANCE = 1.25        # at or below 1.25x -> chance (plus window/breadth) explains it
BARS_FLAT_BAND = 0.15      # all quarters within +-15% of the median bar count -> length is flat
TRACK_CORR = 0.50          # rank correlation that counts as "this channel tracks the spread"

RULE = {
    "R1_same_books": "same six start dates, same cadences 10/20, same n_hold=5, same 8bp cost and "
                     "same next-open fill as r2130 -- only the segment list is extended",
    "R2_bars_measured": "the bar count of every quarter slice is printed from the same slice call "
                        "that produced the return; channel A is judged on the measured numbers, "
                        "not on a belief about short windows",
    "R3_breadth": "breadth = interquartile range of single-name quarterly returns over every column "
                  "of the tradable panel that has both endpoints finite; this is a property of "
                  "the market, not of any book",
    "R4_overlap": "for each book, the union of names picked at its rebalance bars inside the "
                  "quarter (top n_hold by that bar's score, the same rule fast_next_open applies); "
                  "overlap = mean pairwise Jaccard across the books live in that quarter",
    "R5_null": "%d permutation-score families (per-bar shuffle of the finite entries, seed %d). "
               "Each null family gets the same per-quarter cross-book spread treatment; the "
               "widening is called chance when the actual spread does not clear the largest null"
               % (NULL_DRAWS, NULL_SEED),
    "R6_words": "every verdict word is computed from this face's own printed numbers; check "
                "recomputes them and fails on any disagreement",
    "R7_thin": "a quarter needs >= 2 live books to have a cross-book spread at all; thin cells and "
               "partial quarters are named, never zeroed",
    "R8_money": "money lines use a %d reference account and quarter total returns, not annualised"
                % BASE_MONEY,
}


# ---------------------------------------------------------------------------------------
# pure helpers (fixture-tested, no panel)
# ---------------------------------------------------------------------------------------
def build_segments(lo_year, hi_year):
    segs = []
    for y in range(lo_year, hi_year + 1):
        for q, (m0, m1) in enumerate(((1, 4), (4, 7), (7, 10), (10, 13)), start=1):
            hi_y, hi_m = (y + 1, 1) if m1 > 12 else (y, m1)
            segs.append({"label": "%dQ%d" % (y, q),
                         "lo": "%04d-%02d-01" % (y, m0),
                         "hi": "%04d-%02d-01" % (hi_y, hi_m)})
    return segs


def quarter_stats(cells, qstats_quartiles):
    """per-segment spread of the delta, plus the book counts that make it readable."""
    out = {}
    for seg in sorted({c["segment"] for c in cells}):
        sub = [c for c in cells if c["segment"] == seg]
        v = [c["delta_pp"] for c in sub]
        q1, q3 = qstats_quartiles(v)
        out[seg] = {
            "n_books": len(sub),
            "bars": min(c["bars"] for c in sub),
            "median_pp": st.median(v),
            "iqr_pp": (q3 - q1) if q1 is not None else None,
            "range_pp": max(v) - min(v),
            "ret_fast_iqr_pp": None,   # filled below where the fast legs are readable
            "ret_slow_iqr_pp": None,
        }
        vf = [c["ret_fast_pct"] for c in sub]
        vs = [c["ret_slow_pct"] for c in sub]
        f1, f3 = qstats_quartiles(vf)
        s1, s3 = qstats_quartiles(vs)
        if f1 is not None:
            out[seg]["ret_fast_iqr_pp"] = f3 - f1
        if s1 is not None:
            out[seg]["ret_slow_iqr_pp"] = s3 - s1
    return out


def jaccard(a, b):
    if not a and not b:
        return None
    u = len(a | b)
    if u == 0:
        return None
    return len(a & b) / float(u)


def mean_pairwise_jaccard(sets):
    vals = []
    keys = sorted(sets)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            v = jaccard(sets[keys[i]], sets[keys[j]])
            if v is not None:
                vals.append(v)
    return (st.mean(vals) if vals else None), len(vals)


def rank_corr(xs, ys):
    """Spearman on the pairs where both sides are numbers; None when fewer than 4 pairs."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 4:
        return None

    def ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx = ranks([p[0] for p in pairs])
    ry = ranks([p[1] for p in pairs])
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return (num / den) if den > 0 else None


def verdict_words(qstats, nullq, breadth, overlap, segments, partial=()):
    """every word here is a pure function of the numbers this face prints.

    Partial quarters are printed but kept out of every statistic: a 35-bar stub is not a quarter,
    and judging 'short windows are noisier' on a stub would be judging the stub.
    """
    partial = set(partial or ())
    reads = [s for s in segments
             if qstats.get(s) and qstats[s]["n_books"] >= 2 and s not in partial]
    words = []
    bars = [qstats[s]["bars"] for s in reads]
    med_bars = st.median(bars) if bars else None
    flat = (med_bars is not None and
            all(abs(b / float(med_bars) - 1.0) <= BARS_FLAT_BAND for b in bars))
    words.append("WINDOW_LENGTH_NOT_THE_ANSWER" if flat else "WINDOW_LENGTH_MIGHT_EXPLAIN_IT")

    h2 = [s for s in H2_2025 if qstats.get(s) and qstats[s]["iqr_pp"] is not None
          and (nullq.get(s) or {}).get("iqr_pp_max") is not None]
    act = st.median([qstats[s]["iqr_pp"] for s in h2]) if h2 else None
    null_vals = [nullq[s]["iqr_pp_max"] for s in h2]
    nv = st.median(null_vals) if null_vals else None
    ratio = (act / nv) if (act is not None and nv not in (None, 0.0)) else None

    # per-quarter ratio: two quarters can disagree, and a median would hide exactly that
    per_q = {}
    for s in reads:
        nm = (nullq.get(s) or {}).get("iqr_pp_max")
        iqr = qstats[s]["iqr_pp"]
        per_q[s] = {"iqr_pp": iqr, "null_iqr_pp_max": nm,
                    "ratio": (iqr / nm) if (iqr is not None and nm not in (None, 0.0)) else None}
    h2_ratios = [per_q[s]["ratio"] for s in h2 if per_q.get(s, {}).get("ratio") is not None]
    n_above = sum(1 for r in h2_ratios if r >= RATIO_EXCEEDS)
    n_below = sum(1 for r in h2_ratios if r <= RATIO_CHANCE)
    if not h2_ratios:
        words.append("CHANCE_UNTESTABLE")
    elif n_above == len(h2_ratios):
        words.append("WIDENING_EXCEEDS_CHANCE")
    elif n_below == len(h2_ratios):
        words.append("CHANCE_EXPLAINS_THE_WIDENING")
    elif n_above == 0:
        words.append("H2_QUARTERS_DISAGREE_NOTHING_ABOVE_CHANCE")
    else:
        words.append("H2_QUARTERS_DISAGREE")

    # how systematic is "the rule pulls the books together"? counted over every readable quarter
    with_ratio = [s for s in reads if per_q[s]["ratio"] is not None]
    # an exact tie (ratio == 1.0) is not evidence either way, so it is counted in neither side
    decisive = [s for s in with_ratio if abs(per_q[s]["ratio"] - 1.0) > 1e-12]
    tighter = [s for s in decisive if per_q[s]["ratio"] < 1.0]
    if len(decisive) < 4:
        words.append("TIGHTNESS_UNREADABLE")
    elif len(tighter) >= 0.7 * len(decisive):
        words.append("BOOKS_TIGHTER_THAN_RANDOM_IN_MOST_QUARTERS")
    else:
        words.append("BOOKS_ARE_NOT_SYSTEMATICALLY_TIGHTER")

    bc = rank_corr([qstats[s]["iqr_pp"] for s in reads], [breadth.get(s) for s in reads])
    if bc is None:
        words.append("BREADTH_UNREADABLE")
    elif bc >= TRACK_CORR:
        words.append("BREADTH_TRACKS_THE_SPREAD")
    else:
        words.append("BREADTH_DOES_NOT_TRACK_THE_SPREAD")

    oc = rank_corr([qstats[s]["iqr_pp"] for s in reads], [overlap.get(s) for s in reads])
    if oc is None:
        words.append("OVERLAP_UNREADABLE")
    elif oc <= -TRACK_CORR:
        words.append("LOW_OVERLAP_COINCIDES_WITH_WIDE_SPREAD")
    else:
        words.append("OVERLAP_DOES_NOT_COINCIDE_WITH_SPREAD")

    # does the widening persist into 2026, the quarters r2130 never covered?
    base = [qstats[s]["iqr_pp"] for s in reads
            if s not in H2_2025 and not s.startswith("2026")
            and qstats[s]["iqr_pp"] is not None]
    y26 = [qstats[s]["iqr_pp"] for s in reads
           if s.startswith("2026") and qstats[s]["iqr_pp"] is not None]
    if not y26 or not base:
        words.append("PERSISTENCE_UNREADABLE")
    elif max(y26) >= 1.5 * st.median(base):
        words.append("WIDENING_PERSISTS_INTO_2026")
    else:
        words.append("WIDENING_WAS_LOCAL_TO_2025H2")

    return {"words": words,
            "bars_flat": flat, "median_bars": med_bars,
            "h2_actual_iqr_pp": act, "h2_null_iqr_pp": nv, "actual_over_null": ratio,
            "per_quarter": per_q,
            "h2_ratios": h2_ratios,
            "quarters_tighter_than_null": sorted(tighter),
            "quarters_wider_than_null": sorted(s for s in decisive if per_q[s]["ratio"] > 1.0),
            "n_quarters_with_ratio": len(with_ratio),
            "n_quarters_decisive": len(decisive),
            "breadth_rank_corr": bc, "overlap_rank_corr": oc}


# ---------------------------------------------------------------------------------------
# panel-side readings
# ---------------------------------------------------------------------------------------
def build_inputs():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_regime_split as RS
    return RS, RS.build_inputs()


def fingerprint(close, cols):
    idx = pd.to_datetime(close.index)
    tail = [str(d.date()) for d in idx[-3:]]
    h = hashlib.sha1()
    h.update(("|".join(tail) + "|%d|%d" % (len(idx), len(cols))).encode("utf-8"))
    last = close[cols].iloc[-1].fillna(0.0).round(6)
    h.update(("|".join("%s=%.6f" % (k, float(v)) for k, v in last.items())).encode("utf-8"))
    return {"cutoff": tail[-1], "bars": int(len(idx)), "cols": int(len(cols)),
            "sha1": h.hexdigest()}


def permute_score(score, seed):
    """per-bar shuffle of the finite entries: kills cross-sectional information, keeps eligibility."""
    rng = np.random.default_rng(seed)
    S = score.to_numpy(dtype=float).copy()
    for i in range(S.shape[0]):
        m = np.isfinite(S[i])
        k = int(m.sum())
        if k > 1:
            S[i, m] = rng.permutation(S[i, m])
    return pd.DataFrame(S, index=score.index, columns=score.columns)


def breadth_of_quarter(close, cols, seg):
    """IQR / p90-p10 of single-name returns inside one quarter -- a market property, no book."""
    lo, hi = pd.Timestamp(seg["lo"]), pd.Timestamp(seg["hi"])
    idx = pd.to_datetime(close.index)
    sel = (idx >= lo) & (idx < hi)
    if int(sel.sum()) < 5:
        return None
    block = close[cols].ffill().iloc[np.flatnonzero(sel)]
    first = block.iloc[0].to_numpy(dtype=float)
    last = block.iloc[-1].to_numpy(dtype=float)
    m = np.isfinite(first) & np.isfinite(last) & (first > 0)
    if int(m.sum()) < 50:
        return None
    r = (last[m] / first[m] - 1.0) * 100.0
    q1, q3 = np.percentile(r, [25, 75])
    p10, p90 = np.percentile(r, [10, 90])
    return {"names": int(m.sum()), "iqr_pp": float(q3 - q1), "p90_p10_pp": float(p90 - p10),
            "median_pp": float(np.median(r))}


def book_holdings(score, idx, cols, start, cadence, seg):
    """names a book picks at its rebalance bars inside one quarter, and how many events it had."""
    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(start)]
    if len(pos) < 3:
        return set(), 0
    rebal = set(pos[::cadence])
    lo, hi = pd.Timestamp(seg["lo"]), pd.Timestamp(seg["hi"])
    S = score.reindex(index=idx, columns=cols).to_numpy(dtype=float)
    names, n_events = set(), 0
    for i in pos:
        d = idx[i]
        if d < lo or d >= hi:
            continue
        if i in rebal:
            row = S[i]
            m = np.isfinite(row)
            if int(m.sum()) >= N_HOLD:
                cand = np.flatnonzero(m)
                picks = cand[np.argsort(-row[cand], kind="stable")][:N_HOLD]
                names |= set(int(p) for p in picks)
                n_events += 1
    return names, n_events


def run_family(V, score, close, openp, cols, segments):
    """one 12-book family -> per-quarter cross-book spread of the cadence delta."""
    runs = {}
    for start in STARTS:
        for cad in CADENCES:
            ser, _turn, _gap = V.fast_next_open(score, close[cols], openp[cols], cad,
                                                n_hold=N_HOLD, cost=COST, start=start)
            runs[(start, cad)] = ser
    cells = []
    for start in STARTS:
        for seg in segments:
            rf = rs_slice(runs[(start, CADENCES[0])], seg)
            rs = rs_slice(runs[(start, CADENCES[1])], seg)
            if rf is None or rs is None or rf[0] is None or rs[0] is None:
                continue
            cells.append({"start": start, "segment": seg["label"], "bars": min(rf[1], rs[1]),
                          "ret_fast_pct": rf[0] * 100.0, "ret_slow_pct": rs[0] * 100.0,
                          "delta_pp": (rf[0] - rs[0]) * 100.0})
    return cells


_RS = None


def rs_slice(ser, seg):
    if ser is None or len(ser) == 0:
        return None
    return _RS.slice_ret(ser, seg["lo"], seg["hi"], min_bars=MIN_BARS)


def mark_partial(segments, cutoff):
    """a quarter whose right bound is past the cutoff is partial: readable, but named as such."""
    cut = pd.Timestamp(cutoff)
    out = []
    for s in segments:
        s2 = dict(s)
        s2["partial"] = bool(pd.Timestamp(s2["hi"]) > cut + pd.Timedelta(days=1))
        out.append(s2)
    return out


# ---------------------------------------------------------------------------------------
# run / check
# ---------------------------------------------------------------------------------------
def compute():
    global _RS
    RS, inputs = build_inputs()
    _RS = RS
    F, V, close, openp, cols, score = inputs
    idx = pd.to_datetime(close.index)
    fp = fingerprint(close, cols)

    segments = mark_partial(build_segments(*EXTENDED_SEGMENTS), fp["cutoff"])
    legacy = [s for s in segments if LEGACY_SEGMENTS[0] <= int(s["label"][:4]) <= LEGACY_SEGMENTS[1]]

    cells = run_family(V, score, close, openp, cols, segments)
    qstats = quarter_stats(cells, RS.quartiles)
    holes = [s["label"] for s in segments if s["label"] not in qstats]

    breadth = {}
    for seg in segments:
        b = breadth_of_quarter(close, cols, seg)
        if b is not None:
            breadth[seg["label"]] = b

    overlap, events = {}, {}
    for seg in segments:
        sets = {}
        for start in STARTS:
            for cad in CADENCES:
                nm, ev = book_holdings(score, idx, cols, start, cad, seg)
                if nm:
                    sets[(start, cad)] = nm
                    events.setdefault(seg["label"], {})
        mj, npairs = mean_pairwise_jaccard(sets)
        overlap[seg["label"]] = mj
        events[seg["label"]] = {"books_with_holds": len(sets), "pairs": npairs,
                                "rebalance_events": int(sum(
                                    book_holdings(score, idx, cols, s_, c_, seg)[1]
                                    for s_, c_ in sets))}

    nullq = {}
    null_runs = []
    for d in range(NULL_DRAWS):
        sc = permute_score(score, NULL_SEED + d)
        ncells = run_family(V, sc, close, openp, cols, segments)
        nq = quarter_stats(ncells, RS.quartiles)
        null_runs.append({"draw": d, "cells": len(ncells),
                          "iqr_pp": {k: v["iqr_pp"] for k, v in nq.items()}})
        for k, v in nq.items():
            slot = nullq.setdefault(k, {"iqr_pp": [], "range_pp": []})
            if v["iqr_pp"] is not None:
                slot["iqr_pp"].append(v["iqr_pp"])
            slot["range_pp"].append(v["range_pp"])
    for k, slot in nullq.items():
        slot["iqr_pp_mean"] = st.mean(slot["iqr_pp"]) if slot["iqr_pp"] else None
        slot["iqr_pp_max"] = max(slot["iqr_pp"]) if slot["iqr_pp"] else None
        slot["range_pp_mean"] = st.mean(slot["range_pp"]) if slot["range_pp"] else None

    br = {k: (v["iqr_pp"] if isinstance(v, dict) else v) for k, v in breadth.items()}
    partial_labels = [s["label"] for s in segments if s["partial"]]
    v = verdict_words(qstats, nullq, br, overlap, [s["label"] for s in segments],
                      partial=partial_labels)

    h2_act = v["h2_actual_iqr_pp"]
    money = {
        "reference_account_cny": BASE_MONEY,
        "h2_iqr_cny": (h2_act / 100.0 * BASE_MONEY) if h2_act is not None else None,
        "h2_range_cny": (max(qstats[s]["range_pp"] for s in H2_2025 if s in qstats) / 100.0
                         * BASE_MONEY) if all(s in qstats for s in H2_2025) else None,
        "note": "quarter total-return spread on a %d account; the middle half of the six books "
                "differed by this much inside one quarter. Not annualised, not additive."
                % BASE_MONEY,
    }

    sentence = (
        "六本起跑日不同的书放进同一个季度：2025Q3/Q4 里中间一半的书相差 %s pp（%s pp 横扫极差），"
        "而四档随机打分书在同两季的极差中位只有 %s pp（倍数 %s）；"
        "同期名字宽度（个股季度收益四分位差）%s pp、持仓重叠（平均 Jaccard）%s → %s。"
        % (_p(h2_act), _p(money["h2_range_cny"], div=BASE_MONEY, scale=100.0),
           _p(v["h2_null_iqr_pp"]), _p(v["actual_over_null"], nd=2),
           _p(br.get("2025Q3")), _p(overlap.get("2025Q3")), " | ".join(v["words"]))
    )

    return {
        "schema": SCHEMA, "face": FACE,
        "question": "r2130 found the within-quarter cross-book spread of the cadence delta jump in "
                    "2025H2 and could not say whether that was a short window, a wide market, or "
                    "real phase risk from the rule",
        "rule": RULE,
        "evidence_cutoff": fp["cutoff"],
        "panel_fingerprint": fp,
        "starts": STARTS, "cadences": list(CADENCES), "n_hold": N_HOLD,
        "cost": {"key": COST_KEY, "per_side": COST},
        "segments": {s["label"]: {"lo": s["lo"], "hi": s["hi"], "partial": s["partial"]}
                     for s in segments},
        "legacy_segments": [s["label"] for s in legacy],
        "cells": cells,
        "quarter_stats": qstats,
        "breadth": breadth,
        "holdings_overlap": overlap,
        "holdings_events": events,
        "null": {"draws": NULL_DRAWS, "seed": NULL_SEED, "by_quarter": nullq,
                 "runs": null_runs},
        "verdict": v,
        "money": money,
        "headline": {
            "words": v["words"],
            "h2_actual_iqr_pp": h2_act,
            "h2_null_iqr_pp": v["h2_null_iqr_pp"],
            "actual_over_null": v["actual_over_null"],
            "bars_by_quarter": {k: qstats[k]["bars"] for k in qstats},
            "breadth_rank_corr": v["breadth_rank_corr"],
            "overlap_rank_corr": v["overlap_rank_corr"],
            "h2_iqr_cny": money["h2_iqr_cny"],
        },
        "desk_sentence": sentence,
        "holes": holes,
        "partial_excluded": partial_labels,
        "honest": [
            "survivorship: the on-disk panel holds ETFs that still exist (family caveat)",
            "no vol target: fast_next_open has none, so these are un-targeted books",
            "the null is a permutation of the score row, so it keeps eligibility and the score's "
            "marginal distribution but destroys which name is better than which; it measures what "
            "random picking inside this market would disperse, not what a different signal would",
            "holdings are the names picked at rebalance bars inside the quarter, a union across the "
            "quarter's rebalances; they are the rule's text read off the same score panel, not the "
            "engine's internal state",
            "a quarter with fewer than two live books has no cross-book spread; thin cells and "
            "partial quarters (2026Q4) are named in holes or flagged partial, never zeroed",
            "quarter returns are total returns inside a quarter, not annualised",
        ],
    }


def _p(x, nd=2, div=None, scale=1.0):
    if x is None:
        return "n/a"
    if div is not None:
        x = x / div * scale
    return ("%." + str(nd) + "f") % x


def write_face(doc):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(body + "\n")
    return hashlib.sha1(body.encode("utf-8")).hexdigest()


def check():
    if not os.path.exists(OUT_PATH):
        print("STALE FACE_MISSING %s" % FACE)
        return 3
    with open(OUT_PATH, encoding="utf-8") as f:
        doc = json.load(f)
    problems = []

    RS, inputs = build_inputs()
    global _RS
    _RS = RS
    _F, _V, close, openp, cols, score = inputs
    fp_now = fingerprint(close, cols)
    fp_face = doc.get("panel_fingerprint") or {}
    if fp_now != fp_face:
        problems.append("STALE panel moved: face %s -> disk %s"
                        % (fp_face.get("cutoff"), fp_now.get("cutoff")))

    # every published spread must be recomputable from the published cells
    cells = doc.get("cells") or []
    recomputed = quarter_stats(cells, RS.quartiles)
    for seg, stt in (doc.get("quarter_stats") or {}).items():
        rc = recomputed.get(seg)
        if rc is None:
            problems.append("CHECK FAILED %s printed but no cells support it" % seg)
            continue
        for key in ("n_books", "iqr_pp", "range_pp", "median_pp", "bars"):
            a, b = stt.get(key), rc.get(key)
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                problems.append("CHECK FAILED %s.%s printed %r recomputed %r" % (seg, key, a, b))

    # the verdict must follow from the face's own numbers
    br = {k: v["iqr_pp"] for k, v in (doc.get("breadth") or {}).items()}
    vv = verdict_words(doc.get("quarter_stats") or {}, doc.get("null", {}).get("by_quarter") or {},
                       br, doc.get("holdings_overlap") or {},
                       list((doc.get("segments") or {}).keys()),
                       partial=doc.get("partial_excluded") or [])
    face_words = (doc.get("verdict") or {}).get("words") or []
    if vv["words"] != face_words:
        problems.append("CHECK FAILED verdict words printed %r recomputed %r"
                        % (face_words, vv["words"]))
    for key in ("h2_actual_iqr_pp", "h2_null_iqr_pp", "actual_over_null",
                "breadth_rank_corr", "overlap_rank_corr"):
        a = (doc.get("verdict") or {}).get(key)
        b = vv.get(key)
        if a is None and b is None:
            continue
        if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
            problems.append("CHECK FAILED verdict.%s printed %r recomputed %r" % (key, a, b))

    if problems:
        for p in problems:
            print(p)
        return 3
    print("CHECK OK quarters=%d readings=%d cells=%d words=%s"
          % (len(doc.get("quarter_stats") or {}), len(br), len(cells),
             ",".join(face_words)))
    return 0


# ---------------------------------------------------------------------------------------
# selftest (offline, no panel)
# ---------------------------------------------------------------------------------------
def selftest():
    legs, bad = 0, []

    def ok(name, cond):
        nonlocal legs
        legs += 1
        if not cond:
            bad.append(name)
        print("%-62s %s" % (name, "OK" if cond else "FAIL"))

    def quartiles(vals):
        v = sorted(vals)
        if len(v) < 4:
            return None, None
        n = len(v)

        def at(p):
            pos = p * (n - 1)
            lo = int(pos)
            hi = min(lo + 1, n - 1)
            return v[lo] + (v[hi] - v[lo]) * (pos - lo)

        return at(0.25), at(0.75)

    # 1 spread needs four books
    q1, q3 = quartiles([1.0, 2.0, 3.0])
    ok("spread of three books is unreadable, not zero", q1 is None and q3 is None)

    # 2 quarter_stats keeps the thin cell named and computes the IQR from the cells alone
    cells = [{"segment": "S1", "start": str(i), "bars": 60, "ret_fast_pct": 1.0 + i,
              "ret_slow_pct": 0.5, "delta_pp": float(i)} for i in range(6)]
    cells.append({"segment": "S2", "start": "x", "bars": 60, "ret_fast_pct": 1.0,
                  "ret_slow_pct": 1.0, "delta_pp": 0.0})
    qs = quarter_stats(cells, quartiles)
    ok("six books give a readable IQR", qs["S1"]["iqr_pp"] is not None and
       abs(qs["S1"]["iqr_pp"] - 2.5) < 1e-12)
    ok("a one-book quarter is printed with a null IQR, never zero",
       qs["S2"]["n_books"] == 1 and qs["S2"]["iqr_pp"] is None)

    # 3 jaccard + pairwise overlap
    ok("jaccard of identical sets is 1", jaccard({1, 2}, {1, 2}) == 1.0)
    ok("jaccard of disjoint sets is 0", jaccard({1, 2}, {3, 4}) == 0.0)
    ok("jaccard of two empty sets is unreadable", jaccard(set(), set()) is None)
    mj, npairs = mean_pairwise_jaccard({"a": {1, 2}, "b": {1, 2}, "c": {3, 4}})
    # pairs: a-b identical (1.0), a-c and b-c disjoint (0.0) -> mean 1/3
    ok("mean pairwise jaccard over three books has three pairs",
       npairs == 3 and abs(mj - 1.0 / 3.0) < 1e-12)

    # 4 rank correlation is exact on a monotone relation and refuses thin input
    ok("rank corr of a monotone pair is 1", abs(rank_corr([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-12)
    ok("rank corr of an inverted pair is -1", abs(rank_corr([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-12)
    ok("rank corr with three pairs is unreadable", rank_corr([1, 2, 3], [1, 2, 3]) is None)
    ok("rank corr tolerates a null on either side",
       rank_corr([1, 2, 3, 4], [1, None, 3, 4]) is None)

    # 5 verdict: chance explains a widening that the null also shows
    segs = ["2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1"]
    q_flat = {s: {"n_books": 6, "bars": 60, "iqr_pp": (13.0 if s in H2_2025 else 2.0),
                  "range_pp": 20.0, "median_pp": 0.0} for s in segs}
    null_same = {s: {"iqr_pp_max": (12.0 if s in H2_2025 else 1.8)} for s in segs}
    v1 = verdict_words(q_flat, null_same, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("null as wide as the books -> chance explains the widening",
       "CHANCE_EXPLAINS_THE_WIDENING" in v1["words"])
    ok("flat bar counts -> window length is not the answer",
       "WINDOW_LENGTH_NOT_THE_ANSWER" in v1["words"])

    # 6 verdict: widening far above the null and above every other quarter
    null_small = {s: {"iqr_pp_max": (3.0 if s in H2_2025 else 2.0)} for s in segs}
    v2 = verdict_words(q_flat, null_small, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("actual four times the null -> exceeds chance",
       "WIDENING_EXCEEDS_CHANCE" in v2["words"])
    ok("2026 does not repeat the 2025H2 widening -> local, not persistent",
       "WIDENING_WAS_LOCAL_TO_2025H2" in v2["words"])

    # 7 verdict: a 2026 quarter just as wide as 2025H2 makes it persistent
    q_persist = {s: dict(v) for s, v in q_flat.items()}
    q_persist["2026Q1"]["iqr_pp"] = 12.0
    v3 = verdict_words(q_persist, null_small, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("2026 repeats it -> persists into 2026", "WIDENING_PERSISTS_INTO_2026" in v3["words"])

    # 8 verdict: breadth and overlap must earn their words
    br_track = {"2025Q1": 1.0, "2025Q2": 2.0, "2025Q3": 3.0, "2025Q4": 4.0, "2026Q1": 5.0}
    q_track = {"2025Q1": {"n_books": 6, "bars": 60, "iqr_pp": 1.0, "range_pp": 2.0, "median_pp": 0},
               "2025Q2": {"n_books": 6, "bars": 60, "iqr_pp": 2.0, "range_pp": 2.0, "median_pp": 0},
               "2025Q3": {"n_books": 6, "bars": 60, "iqr_pp": 3.0, "range_pp": 2.0, "median_pp": 0},
               "2025Q4": {"n_books": 6, "bars": 60, "iqr_pp": 4.0, "range_pp": 2.0, "median_pp": 0},
               "2026Q1": {"n_books": 6, "bars": 60, "iqr_pp": 5.0, "range_pp": 2.0, "median_pp": 0}}
    v4 = verdict_words(q_track, null_small, br_track, {s: 0.3 for s in segs}, segs)
    ok("breadth rising with the spread -> breadth tracks it",
       "BREADTH_TRACKS_THE_SPREAD" in v4["words"])
    ov_inv = {"2025Q1": 0.9, "2025Q2": 0.8, "2025Q3": 0.7, "2025Q4": 0.6, "2026Q1": 0.5}
    v5 = verdict_words(q_track, null_small, br_track, ov_inv, segs)
    ok("overlap falling as the spread rises -> low overlap coincides",
       "LOW_OVERLAP_COINCIDES_WITH_WIDE_SPREAD" in v5["words"])
    v6 = verdict_words(q_track, null_small, br_track, {s: 0.5 for s in segs}, segs)
    ok("a constant overlap cannot be correlated -> unreadable, not 'does not coincide'",
       "OVERLAP_UNREADABLE" in v6["words"])
    ov_flat = {"2025Q1": 0.50, "2025Q2": 0.62, "2025Q3": 0.41, "2025Q4": 0.58, "2026Q1": 0.47}
    v6b = verdict_words(q_track, null_small, br_track, ov_flat, segs)
    ok("varying but uncorrelated overlap -> overlap does not coincide",
       "OVERLAP_DOES_NOT_COINCIDE_WITH_SPREAD" in v6b["words"])

    # 9 bars that really do differ are not called flat
    q_bars = {s: dict(v) for s, v in q_flat.items()}
    q_bars["2025Q4"]["bars"] = 25
    v7 = verdict_words(q_bars, null_small, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("one quarter with a quarter of the bars -> length might explain it",
       "WINDOW_LENGTH_MIGHT_EXPLAIN_IT" in v7["words"])
    v7b = verdict_words(q_bars, null_small, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs,
                        partial=["2025Q4"])
    ok("the same short quarter, flagged partial, is kept out of the length verdict",
       "WINDOW_LENGTH_NOT_THE_ANSWER" in v7b["words"])

    # 9b a widening narrower than the null in EVERY quarter: the books are systematically tighter
    null_wide = {s: {"iqr_pp_max": 30.0} for s in segs}
    v8 = verdict_words(q_flat, null_wide, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("every quarter narrower than its null -> tighter than random in most quarters",
       "CHANCE_EXPLAINS_THE_WIDENING" in v8["words"] and
       "BOOKS_TIGHTER_THAN_RANDOM_IN_MOST_QUARTERS" in v8["words"])

    # 9c the shape this round actually met: one H2 quarter above chance, the other below
    null_split = {"2025Q1": {"iqr_pp_max": 2.0}, "2025Q2": {"iqr_pp_max": 2.0},
                  "2025Q3": {"iqr_pp_max": 30.0}, "2025Q4": {"iqr_pp_max": 3.0},
                  "2026Q1": {"iqr_pp_max": 2.0}}
    v9 = verdict_words(q_flat, null_split, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("one quarter above chance and one below -> quarters disagree, never averaged into a word",
       "H2_QUARTERS_DISAGREE" in v9["words"])
    ok("the split names which quarters were wider than their null",
       v9["quarters_wider_than_null"] == ["2025Q4"])
    # 9d neither H2 quarter clears the exceed line: the sharper, quieter word
    null_mid = {"2025Q1": {"iqr_pp_max": 2.0}, "2025Q2": {"iqr_pp_max": 2.0},
                "2025Q3": {"iqr_pp_max": 30.0}, "2025Q4": {"iqr_pp_max": 9.0},
                "2026Q1": {"iqr_pp_max": 2.0}}
    v10 = verdict_words(q_flat, null_mid, {s: 5.0 for s in segs}, {s: 0.3 for s in segs}, segs)
    ok("nothing in H2 clears the exceed line -> says so instead of 'disagree'",
       "H2_QUARTERS_DISAGREE_NOTHING_ABOVE_CHANCE" in v10["words"])

    # 10 partial-quarter flagging follows the cutoff
    segs_p = mark_partial(build_segments(2026, 2026), "2026-11-25")
    ok("2026Q4 is partial and 2026Q1 is not",
       [s["partial"] for s in segs_p] == [False, False, False, True])

    # 11 check() on a face whose fingerprint moved must say STALE and return 3
    doc = {"panel_fingerprint": {"cutoff": "1999-01-01", "bars": 1, "cols": 1, "sha1": "dead"},
           "cells": [], "quarter_stats": {}, "verdict": {"words": []}}
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "face.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        global OUT_PATH
        keep = OUT_PATH
        OUT_PATH = p
        try:
            rc = check()   # builds the real panel; the face fingerprint is fake
        finally:
            OUT_PATH = keep
    ok("check on a moved panel says STALE and returns 3", rc == 3)

    # 12 permutation null really destroys the ordering inside a row
    sc = pd.DataFrame(np.array([[1.0, 2.0, 3.0, 4.0], [np.nan, 5.0, 6.0, 7.0]]),
                      columns=["a", "b", "c", "d"], index=pd.to_datetime(["2024-01-02",
                                                                         "2024-01-03"]))
    perm = permute_score(sc, 7)
    ok("permutation keeps the NaN pattern", np.isnan(perm.iloc[1, 0]))
    ok("permutation keeps each row's multiset",
       sorted(perm.iloc[0].tolist()) == [1.0, 2.0, 3.0, 4.0])
    ok("permutation is reproducible for one seed",
       perm.equals(permute_score(sc, 7)))

    print("\nSELFTEST %d/%d %s" % (legs - len(bad), legs, "OK" if not bad else "FAILED: " + ", ".join(bad)))
    return 0 if not bad else 1


def run():
    doc = compute()
    sha = write_face(doc)
    print("WROTE %s sha1(face)=%s" % (FACE, sha[:12]))
    print("cutoff=%s" % doc["evidence_cutoff"])
    print("words: %s" % " | ".join(doc["verdict"]["words"]))
    print(doc["desk_sentence"])
    qs = doc["quarter_stats"]
    print("\n%-8s %3s %4s %8s %8s %8s %7s %7s" %
          ("quarter", "n", "bars", "median", "iqr", "range", "breadth", "jaccard"))
    for seg in doc["segments"]:
        s = qs.get(seg)
        if not s:
            print("%-8s  -- named hole (fewer than 2 live books)" % seg)
            continue
        b = (doc["breadth"].get(seg) or {}).get("iqr_pp")
        o = doc["holdings_overlap"].get(seg)
        nq = doc["null"]["by_quarter"].get(seg) or {}
        print("%-8s %3d %4d %8.2f %8s %8.2f %7s %7s  null_iqr_max=%s" %
              (seg, s["n_books"], s["bars"], s["median_pp"],
               ("%.2f" % s["iqr_pp"]) if s["iqr_pp"] is not None else "n/a",
               s["range_pp"],
               ("%.2f" % b) if b is not None else "n/a",
               ("%.2f" % o) if o is not None else "n/a",
               ("%.2f" % nq.get("iqr_pp_max")) if nq.get("iqr_pp_max") is not None else "n/a"))
    print("\nholes: %s" % (doc["holes"] or "none"))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "").strip().lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
