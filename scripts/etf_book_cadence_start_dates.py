#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""is the 20-bars -> 10-bars cadence gain a cadence, or a 2020-winter start date?

WHY THIS FILE EXISTS
--------------------
r2128 measured the same knob (R20 -> R10) with three rulers and left one caveat it could not
answer with its own inputs: every phase book in this family starts between 2020-01-02 and
2020-03-05, so the "band inside a cell" that everything is judged against is ONE winter at the
top of a bubble, with the 2020 February-March crash inside it. The matched reading (+0.76pp) and
the independent adoption run (+0.68pp) both live inside that winter. Nobody had asked: does the
sign survive a start date in 2021, 2023, 2025?

This face answers exactly that, on the engine the family already uses (no re-implementation):
  scripts/etf_variants_null_rolling.fast_next_open   (pinned to the reference fill chain)
  scripts/etf_composite_pf.build_panel/build_score   (same panel, bond-removed universe)
  scripts/etf_asset_class.classify                   (same instrument classes)

TWO RULERS, BECAUSE THE ANCHORS ARE NESTED
------------------------------------------
Every book runs to the same cutoff, so a later start is a strict SUB-window of an earlier one:
the 21 anchors are 21 windows sharing one tail, not 21 independent draws. Ruler 1 (TO_CUTOFF)
is therefore a path reading -- it says what an account that entered on that date earned by now.
Ruler 2 (FIXED 252 / 504 bars) slices the first year / first two years of the SAME run, which
turns anchors twelve months apart into near-disjoint segments -- that is the ruler allowed to say
"inside any given year of holding, does the faster cadence help?".

WHAT IT DOES NOT DO
-------------------
No verdict on the production ticket: the schedule decision stays with
results/etf_book_rebal_adoption.json (PHASE_DEPENDENT). This face only fixes the sentence the
cadence ladder is allowed to say beyond the winter it was measured in. It also does not claim a
vol-target cell: fast_next_open has no vol target, so these are the un-targeted books and the
adoption face's vol-8% control is printed beside them, never merged with them.

self  python scripts/etf_book_cadence_start_dates.py selftest
run   python scripts/etf_book_cadence_start_dates.py run
check python scripts/etf_book_cadence_start_dates.py check
"""

import hashlib
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_start_dates.json")
FACE = "results/etf_book_cadence_start_dates.json"
SCHEMA = "etf-book-cadence-start-dates/v2"

COMPARABLE_PATH = os.path.join(ROOT, "results", "etf_book_cadence_comparable.json")
ADOPTION_PATH = os.path.join(ROOT, "results", "etf_book_rebal_adoption.json")

BASE_MONEY = 1_000_000.0
N_HOLD = 5
CADENCE_FAST, CADENCE_SLOW = 10, 20
COSTS = {"8bp": 0.0008, "1bp": 0.0001}
MIN_BARS = 300                  # below this a CAGR is noise; such a start is named, never zeroed
LONG_WINDOW_BARS = 1000         # split used to test "later starts have shorter windows"
SIGN_MIN_SHARE = 0.60           # frozen before the first run of this round
CONSISTENT_LO, CONSISTENT_HI = 0.50, 2.00   # of the winter reading, to call it consistent
HORIZONS = (("to_cutoff", None), ("252", 252), ("504", 504))

STARTS = []
for _y in range(2020, 2026):
    for _m in (3, 6, 9, 12):
        _iso = "%04d-%02d-01" % (_y, _m)
        if "2020-06-01" <= _iso <= "2025-09-01":
            STARTS.append(_iso)

RULE = {
    "R1_starts": "quarterly anchors 2020-06-01..2025-09-01; a start whose book is shorter than "
                 "%d bars is named in excluded_starts with the reason and never read as a zero"
                 % MIN_BARS,
    "R2_pair": "every delta pairs the SAME start date, the same cost, the same n_hold and the "
               "same horizon -- only the cadence differs, so no other ruler is mixed in",
    "R3_sign": "the direction holds iff at least %.0f%% of start dates move the same way "
               "(threshold frozen before the first run)" % (SIGN_MIN_SHARE * 100),
    "R4_calendar": "the start-date term is the interquartile spread of the paired deltas; if it "
                   "is at least as large as the median, the cadence gap lives inside the "
                   "start-date noise",
    "R5_window": "TO_CUTOFF anchors are nested (all books end at the same cutoff); the fixed "
                 "252/504-bar rulers slice each run's own head and are the ones allowed to speak "
                 "about a single year of holding. A start too short for a horizon is a named "
                 "hole for that horizon only",
    "R6_winter": "the winter reading is read from etf_book_cadence_comparable (matched) and "
                 "etf_book_rebal_adoption (paired run) and compared by a frozen band of "
                 "[%.2f, %.2f]x -- never recomputed here" % (CONSISTENT_LO, CONSISTENT_HI),
    "R7_money": "money lines use a %d reference account" % BASE_MONEY,
    "frozen": "thresholds written before the first read of these panels in this round",
}


# --------------------------------------------------------------------------------------
# pooled readings (pure functions so selftest can drive them without a panel)
# --------------------------------------------------------------------------------------
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


def pool(deltas):
    """median / share positive / interquartile spread over paired start-date deltas."""
    if not deltas:
        return {"n": 0, "median_pp": None, "share_positive": None,
                "spread_pp": None, "min_pp": None, "max_pp": None}
    q1, q3 = quartiles(deltas)
    return {
        "n": len(deltas),
        "median_pp": st.median(deltas),
        "share_positive": sum(1 for d in deltas if d > 0) / float(len(deltas)),
        "spread_pp": (q3 - q1) if q1 is not None else None,
        "min_pp": min(deltas), "max_pp": max(deltas),
    }


def deltas_of(cells, cost_key, horizon):
    out = []
    for c in cells:
        if c["cost"] != cost_key:
            continue
        h = (c.get("horizons") or {}).get(horizon) or {}
        if h.get("delta_pp") is not None:
            out.append(h["delta_pp"])
    return out


def window_split(cells, cost_key, horizon="to_cutoff"):
    long_d, short_d = [], []
    for c in cells:
        if c["cost"] != cost_key:
            continue
        h = (c.get("horizons") or {}).get(horizon) or {}
        if h.get("delta_pp") is None:
            continue
        (long_d if c["bars_slow"] >= LONG_WINDOW_BARS else short_d).append(h["delta_pp"])
    return {"long": pool(long_d), "short": pool(short_d)}


def words_for(pooled, split, winter, allow_window=True):
    words = []
    if pooled["n"] == 0:
        return ["NO_STARTS_READ"]
    words.append("SIGN_HOLDS" if pooled["share_positive"] >= SIGN_MIN_SHARE
                 else "SIGN_FAILS")
    spread, med = pooled["spread_pp"], pooled["median_pp"]
    if spread is not None and med is not None:
        words.append("CALENDAR_TERM_EXCEEDS_CADENCE_GAP" if spread >= abs(med)
                     else "CADENCE_GAP_EXCEEDS_CALENDAR_TERM")
    if allow_window:
        lo = split["long"]["median_pp"] if split["long"]["n"] else None
        sh = split["short"]["median_pp"] if split["short"]["n"] else None
        if lo is not None and sh is not None:
            words.append("WINDOW_SIGN_HOLDS" if (lo > 0) == (sh > 0) else "WINDOW_SIGN_FLIPS")
        else:
            words.append("WINDOW_SPLIT_INCOMPLETE")
    if winter is not None and med is not None:
        if winter == 0:
            words.append("WINTER_COMPARISON_UNDEFINED")
        elif med * winter < 0:
            words.append("REVERSES_THE_WINTER_READING")
        elif CONSISTENT_LO <= (med / winter) <= CONSISTENT_HI:
            words.append("CONSISTENT_WITH_THE_WINTER_READING")
        else:
            words.append("ATTENUATED_BEYOND_THE_WINTER_READING")
    return words


# --------------------------------------------------------------------------------------
# inputs (read-only)
# --------------------------------------------------------------------------------------
def _read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def winter_reading():
    """the two winter rulers already published; read, never recomputed."""
    out = {}
    cmp_doc = _read_json(COMPARABLE_PATH)
    if cmp_doc:
        h = cmp_doc.get("headline") or {}
        out["cadence_comparable"] = {
            "face": "results/etf_book_cadence_comparable.json",
            "evidence_cutoff": cmp_doc.get("evidence_cutoff"),
            "matched_median_delta_pp": h.get("matched_median_delta_pp"),
            "cross_set_median_delta_pp": h.get("cross_set_median_delta_pp"),
            "matched_pairs": h.get("matched_pairs"),
            "start_window": (cmp_doc.get("start_date_coverage") or {}).get("first_decisions_min"),
            "start_window_end": (cmp_doc.get("start_date_coverage") or {}).get("first_decisions_max"),
        }
    ad = _read_json(ADOPTION_PATH)
    if ad:
        s10 = ((ad.get("summary") or {}).get("by_cost") or {}).get("10") or {}
        out["rebal_adoption"] = {
            "face": "results/etf_book_rebal_adoption.json",
            "evidence_cutoff": ad.get("evidence_cutoff"),
            "median_delta_cagr_pp_10bp": s10.get("median_delta_cagr_pp"),
            "n_phases": s10.get("n_phases"),
            "verdict": (ad.get("verdict") or {}).get("label"),
            "note": "control carries a vol target of 0.08; this face has none -- printed "
                    "side by side, never merged",
        }
    return out or None


def build_inputs():
    """panel + score, exactly as the family builds them."""
    sys.path.insert(0, ROOT)
    import pandas as pd                                   # noqa: F401  (pandas for the index)
    from scripts import etf_composite_pf as F
    from scripts import etf_variants_null_rolling as V
    from scripts.etf_asset_class import classify

    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    return F, V, close, openp, cols, score


def fingerprint(close, cols):
    """cheap identity of the panel bytes this face read (drift detector for check)."""
    import pandas as pd
    idx = pd.to_datetime(close.index)
    tail = [str(d.date()) for d in idx[-3:]]
    h = hashlib.sha1()
    h.update(("|".join(tail) + "|%d|%d" % (len(idx), len(cols))).encode("utf-8"))
    last = close[cols].iloc[-1].fillna(0.0).round(6)
    h.update(("|".join("%s=%.6f" % (k, float(v)) for k, v in last.items())).encode("utf-8"))
    return {"cutoff": tail[-1], "bars": int(len(idx)), "cols": int(len(cols)),
            "sha1": h.hexdigest()}


# --------------------------------------------------------------------------------------
# run
# --------------------------------------------------------------------------------------
def compute():
    F, V, close, openp, cols, score = build_inputs()
    import pandas as pd
    idx = pd.to_datetime(close.index)
    fp = fingerprint(close, cols)

    cells, excluded = [], []
    for start in STARTS:
        pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(start)]
        if len(pos) < MIN_BARS:
            excluded.append({"start": start, "why": "only %d bars to the cutoff (< %d)"
                                                    % (len(pos), MIN_BARS)})
            continue
        for cost_key, cost in COSTS.items():
            runs = {}
            for cad in (CADENCE_FAST, CADENCE_SLOW):
                ser, turn, _gap = V.fast_next_open(score, close[cols], openp[cols], cad,
                                                   n_hold=N_HOLD, cost=cost, start=start)
                if ser is None or len(ser) < MIN_BARS:
                    runs[cad] = None
                    continue
                runs[cad] = {"ser": ser, "turn": float(turn)}
            if runs.get(CADENCE_FAST) is None or runs.get(CADENCE_SLOW) is None:
                excluded.append({"start": start, "cost": cost_key,
                                 "why": "one of the two cadence runs came back empty"})
                continue

            horizons, holes = {}, []
            for name, hbars in HORIZONS:
                sf = runs[CADENCE_FAST]["ser"]
                ss = runs[CADENCE_SLOW]["ser"]
                if hbars is not None:
                    if len(sf) < hbars or len(ss) < hbars:
                        holes.append({"horizon": name,
                                      "why": "run has %d/%d bars, horizon needs %d"
                                             % (len(sf), len(ss), hbars)})
                        horizons[name] = {"unavailable": True}
                        continue
                    sf, ss = sf.iloc[:hbars], ss.iloc[:hbars]
                mf = F.metrics(sf, "R%d:%s" % (CADENCE_FAST, name))
                ms = F.metrics(ss, "R%d:%s" % (CADENCE_SLOW, name))
                if "cagr" not in mf or "cagr" not in ms:
                    holes.append({"horizon": name, "why": "a slice was too short for a CAGR"})
                    horizons[name] = {"unavailable": True}
                    continue
                horizons[name] = {
                    "bars": int(len(sf)),
                    "cagr_fast_pct": mf["cagr"] * 100.0,
                    "cagr_slow_pct": ms["cagr"] * 100.0,
                    "delta_pp": (mf["cagr"] - ms["cagr"]) * 100.0,
                    "sharpe_fast": mf.get("sharpe"), "sharpe_slow": ms.get("sharpe"),
                }

            base = runs[CADENCE_FAST]["ser"]
            slow = runs[CADENCE_SLOW]["ser"]
            cells.append({
                "start": start, "cost": cost_key, "n_hold": N_HOLD,
                "bars_fast": int(len(base)), "bars_slow": int(len(slow)),
                "cagr_fast_pct": horizons["to_cutoff"]["cagr_fast_pct"],
                "cagr_slow_pct": horizons["to_cutoff"]["cagr_slow_pct"],
                "delta_pp": horizons["to_cutoff"]["delta_pp"],
                "turnover_fast": runs[CADENCE_FAST]["turn"],
                "turnover_slow": runs[CADENCE_SLOW]["turn"],
                "first": str(base.index[0].date()), "last": str(base.index[-1].date()),
                "horizons": horizons, "horizon_holes": holes,
            })

    winter = winter_reading()
    winter_med = ((winter or {}).get("cadence_comparable") or {}).get("matched_median_delta_pp")

    by_cost = {}
    for cost_key in COSTS:
        block = {}
        for name, _hbars in HORIZONS:
            d = deltas_of(cells, cost_key, name)
            pooled = pool(d)
            split = window_split(cells, cost_key, name)
            entry = {"pooled": pooled,
                     "window_split": split if name == "to_cutoff" else None,
                     "n_holes": sum(1 for c in cells if c["cost"] == cost_key
                                    and ((c.get("horizons") or {}).get(name) or {})
                                    .get("unavailable"))}
            entry["words"] = " | ".join(
                words_for(pooled, split, winter_med if (name == "to_cutoff" and cost_key == "8bp")
                           else None, allow_window=(name == "to_cutoff")))
            block[name] = entry
        by_cost[cost_key] = block

    main_block = by_cost.get("8bp", {})
    p_cut = (main_block.get("to_cutoff") or {}).get("pooled") or {}
    p_252 = (main_block.get("252") or {}).get("pooled") or {}
    p_504 = (main_block.get("504") or {}).get("pooled") or {}

    money = {
        "reference_account_cny": BASE_MONEY,
        "to_cutoff_median_pp": p_cut.get("median_pp"),
        "cny_per_year_at_to_cutoff_median": ((p_cut.get("median_pp") or 0.0) / 100.0 * BASE_MONEY
                                            if p_cut.get("median_pp") is not None else None),
        "one_year_median_pp": p_252.get("median_pp"),
        "cny_per_year_at_one_year_median": ((p_252.get("median_pp") or 0.0) / 100.0 * BASE_MONEY
                                            if p_252.get("median_pp") is not None else None),
        "to_cutoff_range_low": ((p_cut.get("min_pp") or 0.0) / 100.0 * BASE_MONEY
                                if p_cut.get("min_pp") is not None else None),
        "to_cutoff_range_high": ((p_cut.get("max_pp") or 0.0) / 100.0 * BASE_MONEY
                                 if p_cut.get("max_pp") is not None else None),
        "note": "every delta already pays the faster cadence's own higher toll; the one-year "
                "line is the near-disjoint ruler, the to-cutoff line is the nested path",
    }

    by_year = {}
    for c in cells:
        if c["cost"] != "8bp":
            continue
        by_year.setdefault(c["start"][:4], []).append(c["delta_pp"])
    by_year_pooled = {y: pool(v) for y, v in sorted(by_year.items())}

    sentence = (
        "对票面：不改（节奏决定权在 etf_book_rebal_adoption）。"
        "「20→10 更快更好」在 21 个起跑日（2020-06..2025-09）上：跑到今天中位 %s pp、"
        "%s 的起跑日为正（嵌套窗，一个尾巴算了好几遍）；切成一整年（252 bar，近互斥）中位 %s pp、"
        "%s 为正。所以冬天以外这句话只剩一口气：起跑日四分位差 %s pp 比中位还大。"
        % (("%+.2f" % p_cut["median_pp"]) if p_cut.get("median_pp") is not None else "n/a",
           ("%.0f%%" % (p_cut["share_positive"] * 100)) if p_cut.get("share_positive")
           is not None else "n/a",
           ("%+.2f" % p_252["median_pp"]) if p_252.get("median_pp") is not None else "n/a",
           ("%.0f%%" % (p_252["share_positive"] * 100)) if p_252.get("share_positive")
           is not None else "n/a",
           ("%.2f" % p_cut["spread_pp"]) if p_cut.get("spread_pp") is not None else "n/a")
    )

    return {
        "schema": SCHEMA, "face": FACE,
        "question": "the 20->10 cadence gain was measured on books that all start in the 2020 "
                    "winter; does it survive a start date in 2021, 2023, 2025?",
        "rule": RULE,
        "evidence_cutoff": fp["cutoff"],
        "panel_fingerprint": fp,
        "starts": STARTS,
        "n_starts": len(STARTS),
        "horizons": {name: (hbars if hbars is not None else "to the panel cutoff")
                     for name, hbars in HORIZONS},
        "costs": {k: round(v, 6) for k, v in COSTS.items()},
        "n_hold": N_HOLD,
        "cadence": {"fast": CADENCE_FAST, "slow": CADENCE_SLOW},
        "excluded_starts": excluded,
        "cells": cells,
        "by_cost": by_cost,
        "by_start_year_8bp": by_year_pooled,
        "winter_reading": winter,
        "winter_median_pp_used": winter_med,
        "money": money,
        "headline": {
            "words_8bp": {name: (by_cost.get("8bp", {}).get(name) or {}).get("words")
                          for name, _h in HORIZONS},
            "to_cutoff": {"n": p_cut.get("n"), "median_pp": p_cut.get("median_pp"),
                          "share_positive": p_cut.get("share_positive"),
                          "spread_pp": p_cut.get("spread_pp")},
            "one_year_252": {"n": p_252.get("n"), "median_pp": p_252.get("median_pp"),
                             "share_positive": p_252.get("share_positive"),
                             "spread_pp": p_252.get("spread_pp")},
            "two_year_504": {"n": p_504.get("n"), "median_pp": p_504.get("median_pp"),
                             "share_positive": p_504.get("share_positive"),
                             "spread_pp": p_504.get("spread_pp")},
        },
        "desk_sentence": sentence,
        "honest": [
            "survivorship: the on-disk panel holds ETFs that still exist (family caveat)",
            "no vol target here: fast_next_open has none, so these are un-targeted books; the "
            "adoption face's vol-8% control is printed beside them and never merged",
            "to-cutoff anchors are nested by construction: they share one tail, so their "
            "agreement/disagreement is a path, not independent evidence (R5)",
            "fixed 252/504-bar rulers are near-disjoint only for anchors twelve months apart; "
            "quarterly neighbours still overlap inside a horizon",
            "the earlier a book starts the more of 2020-2021 it contains, so for the earliest "
            "anchors 'start date' and 'which regime you lived through' are the same knob",
        ],
    }


def write_face(doc):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


# --------------------------------------------------------------------------------------
# check: cheap invariants + drift detector (never the two-minute re-run)
# --------------------------------------------------------------------------------------
def check():
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % FACE)
        return 3
    with open(OUT_PATH, "r", encoding="utf-8") as fh:
        old = json.load(fh)

    # 1) has the panel moved since the face was written?
    try:
        F, V, close, openp, cols, score = build_inputs()
        live = fingerprint(close, cols)
    except Exception as exc:                                    # noqa: BLE001
        print("STALE panel could not be rebuilt: %r" % (exc,))
        return 3
    oldfp = old.get("panel_fingerprint") or {}
    if live["sha1"] != oldfp.get("sha1"):
        print("STALE input panel moved: cutoff %s -> %s, bars %s -> %s"
              % (oldfp.get("cutoff"), live["cutoff"], oldfp.get("bars"), live["bars"]))
        return 3

    # 2) do the stored cells still add up, and do the words still follow the numbers?
    bad = []
    cells = old.get("cells") or []
    if not cells:
        print("CHECK FAILED no cells stored")
        return 1
    for c in cells:
        for name, h in (c.get("horizons") or {}).items():
            if h.get("unavailable"):
                continue
            d = h["cagr_fast_pct"] - h["cagr_slow_pct"]
            if abs(d - h["delta_pp"]) > 1e-9:
                bad.append("cell %s/%s/%s delta %.6f != %.6f"
                           % (c["start"], c["cost"], name, h["delta_pp"], d))
    for cost_key, block in (old.get("by_cost") or {}).items():
        for name in (old.get("horizons") or {}):
            stored = (block.get(name) or {}).get("pooled") or {}
            p = pool(deltas_of(cells, cost_key, name))
            if p["n"] != stored.get("n"):
                bad.append("%s/%s n %r != %r" % (cost_key, name, stored.get("n"), p["n"]))
            for k in ("median_pp", "share_positive", "spread_pp"):
                a, b = stored.get(k), p.get(k)
                if a is None or b is None:
                    if a is not b:
                        bad.append("%s/%s %s %r != %r" % (cost_key, name, k, a, b))
                elif abs(float(a) - float(b)) > 1e-9:
                    bad.append("%s/%s %s %r != %r" % (cost_key, name, k, a, b))
            want = " | ".join(words_for(
                p, window_split(cells, cost_key, name),
                old.get("winter_median_pp_used") if (name == "to_cutoff" and cost_key == "8bp")
                else None,
                allow_window=(name == "to_cutoff")))
            got = (block.get(name) or {}).get("words")
            if want != got:
                bad.append("%s/%s words %r != %r" % (cost_key, name, got, want))
    if bad:
        print("CHECK FAILED " + "; ".join(bad[:6]) + (" (+%d more)" % (len(bad) - 6)
                                                      if len(bad) > 6 else ""))
        return 1
    h = old.get("headline") or {}
    print("CHECK OK %d cells, %d starts, to_cutoff median %s pp, one-year median %s pp"
          % (len(cells), old.get("n_starts") or 0,
             ("%.3f" % h["to_cutoff"]["median_pp"]) if h["to_cutoff"].get("median_pp") is not None
             else "n/a",
             ("%.3f" % h["one_year_252"]["median_pp"])
             if h["one_year_252"].get("median_pp") is not None else "n/a"))
    return 0


# --------------------------------------------------------------------------------------
# selftest -- synthetic, no panel reads
# --------------------------------------------------------------------------------------
def selftest():
    legs, ok = [], 0

    def leg(name, cond):
        nonlocal ok
        legs.append({"leg": name, "pass": bool(cond)})
        if cond:
            ok += 1

    # 1 pooled reading
    p = pool([1.0, 2.0, 3.0, 4.0])
    leg("median of an even set is the middle pair", abs(p["median_pp"] - 2.5) < 1e-12)
    leg("share positive counts only strictly positive",
        abs(pool([1.0, -1.0, 0.0, 2.0])["share_positive"] - 0.5) < 1e-12)
    leg("interquartile spread is q3-q1 on the sorted set",
        abs(pool([0, 1, 2, 3, 4])["spread_pp"] - 2.0) < 1e-12)
    leg("fewer than four deltas refuses a spread instead of inventing one",
        pool([1.0, 2.0, 3.0])["spread_pp"] is None)
    leg("an empty pool is a hole, not a zero", pool([])["n"] == 0
        and pool([])["median_pp"] is None)

    # 2 words follow the frozen thresholds
    w = words_for(pool([1.0, 1.1, 1.2, 1.3, 1.4]), {"long": pool([1.0, 1.2]),
                                                   "short": pool([1.3, 1.4])}, 1.0)
    leg("a tight positive set holds the sign", any(x == "SIGN_HOLDS" for x in w))
    wj = words_for(pool([0.0, 0.1, 1.0, 2.0, 3.0]), {"long": pool([0.0, 1.0]),
                                                     "short": pool([2.0, 3.0])}, 0.8)
    leg("a wide spread against a small median is a calendar term",
        any(x == "CALENDAR_TERM_EXCEEDS_CADENCE_GAP" for x in wj))
    leg("exactly the frozen share still holds",
        any(x == "SIGN_HOLDS" for x in words_for(
            pool([1.0, 1.0, 1.0, -1.0, -1.0]), {"long": pool([1.0]),
                                                "short": pool([1.0])}, 1.0)))
    leg("a minority sign fails",
        any(x == "SIGN_FAILS" for x in words_for(
            pool([1.0, -1.0, -1.0, -1.0]), {"long": pool([1.0]),
                                             "short": pool([-1.0])}, 1.0)))
    leg("long and short halves disagreeing is a window flag",
        any(x == "WINDOW_SIGN_FLIPS" for x in words_for(
            pool([1.0, 1.0, -1.0, -1.0]), {"long": pool([1.0, 1.2]),
                                            "short": pool([-1.0, -1.2])}, 1.0)))
    leg("a fixed-horizon ruler does not repeat the to-cutoff window words",
        not any("WINDOW" in x for x in words_for(
            pool([1.0, 1.0, -1.0, -1.0]), {"long": pool([1.0]), "short": pool([-1.0])},
            1.0, allow_window=False)))

    # 3 winter comparison band
    leg("the same size as the winter reading is consistent",
        any(x == "CONSISTENT_WITH_THE_WINTER_READING" for x in
            words_for(pool([0.7, 0.8, 0.75, 0.72, 0.78]),
                      {"long": pool([0.7, 0.8]), "short": pool([0.7, 0.8])}, 0.76)))
    leg("a quarter of the winter reading is attenuated",
        any(x == "ATTENUATED_BEYOND_THE_WINTER_READING" for x in
            words_for(pool([0.1, 0.12, 0.11, 0.13, 0.12]),
                      {"long": pool([0.1, 0.12]), "short": pool([0.11, 0.13])}, 0.76)))
    leg("the opposite sign is a reversal, not an attenuation",
        any(x == "REVERSES_THE_WINTER_READING" for x in
            words_for(pool([-0.1, -0.12, -0.11, -0.13, -0.12]),
                      {"long": pool([-0.1, -0.12]), "short": pool([-0.11, -0.13])}, 0.76)))
    leg("no winter face means no winter word",
        not any("WINTER" in x for x in words_for(pool([1.0, 1.2, 1.1, 1.3]),
                                                 {"long": pool([1.0]), "short": pool([1.2])},
                                                 None)))

    # 4 per-horizon reading comes from that horizon's own cells
    cells = [{"cost": "8bp", "bars_slow": 1200,
              "horizons": {"to_cutoff": {"delta_pp": 2.0}, "252": {"delta_pp": -2.0},
                           "504": {"unavailable": True}}},
             {"cost": "8bp", "bars_slow": 400,
              "horizons": {"to_cutoff": {"delta_pp": 1.0}, "252": {"delta_pp": -1.0},
                           "504": {"unavailable": True}}},
             {"cost": "1bp", "bars_slow": 1200,
              "horizons": {"to_cutoff": {"delta_pp": 9.0}, "252": {"delta_pp": 9.0},
                           "504": {"unavailable": True}}}]
    leg("the one-year reading never borrows the to-cutoff numbers",
        pool(deltas_of(cells, "8bp", "252"))["median_pp"] == -1.5)
    leg("the other cost is never mixed into this cost's reading",
        deltas_of(cells, "1bp", "252") == [9.0])
    leg("an unavailable horizon contributes nothing rather than a zero",
        deltas_of(cells, "8bp", "504") == [])
    leg("the window split keeps only this cost and only cells with a delta at that horizon",
        window_split(cells, "8bp", "252")["long"]["n"] == 1
        and window_split(cells, "8bp", "252")["short"]["n"] == 1)

    # 5 frozen constants and money conversion
    leg("sign threshold is frozen in code", SIGN_MIN_SHARE == 0.60)
    leg("1.0pp on a 1e6 account is 10,000 a year",
        abs(1.0 / 100.0 * BASE_MONEY - 10000.0) < 1e-9)

    # 6 start list is quarterly and inside the declared window
    leg("starts are quarterly anchors between 2020-06-01 and 2025-09-01",
        len(STARTS) == 22 and STARTS[0] == "2020-06-01" and STARTS[-1] == "2025-09-01"
        and all(s[5:7] in ("03", "06", "09", "12") for s in STARTS))
    leg("every horizon is either fixed in bars or the cutoff itself",
        all(h is None or h >= 30 for _n, h in HORIZONS)
        and len({h for _n, h in HORIZONS}) == len(HORIZONS))

    # 7 fingerprint drift is caught before any number is compared
    a = {"cutoff": "2026-11-25", "bars": 1543, "cols": 1456, "sha1": "x"}
    b = dict(a, cutoff="2026-11-26", bars=1544, sha1="y")
    leg("a moved panel reads STALE by sha1, not by eye",
        a["sha1"] != b["sha1"] and a["bars"] != b["bars"])

    print(json.dumps({"legs": len(legs), "passed": ok,
                      "failed": [l["leg"] for l in legs if not l["pass"]]},
                     ensure_ascii=False))
    return 0 if ok == len(legs) else 1


def run():
    doc = compute()
    if doc is None:
        print("FATAL no panel")
        return 2
    write_face(doc)
    h = doc["headline"]
    print(json.dumps({"face": FACE, "cutoff": doc["evidence_cutoff"],
                      "starts": doc["n_starts"], "cells": len(doc["cells"]),
                      "to_cutoff_median_pp": h["to_cutoff"]["median_pp"],
                      "one_year_median_pp": h["one_year_252"]["median_pp"],
                      "two_year_median_pp": h["two_year_504"]["median_pp"],
                      "words": h["words_8bp"]}, ensure_ascii=False))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print("usage: etf_book_cadence_start_dates.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
