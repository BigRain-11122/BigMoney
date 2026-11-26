#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""is the "cadence ladder" a cadence, or is it which phase set each cell averaged?

WHY THIS FILE EXISTS
--------------------
r2127 published CADENCE_LADDER_IS_K_ROBUST from the phase atlas: within every buffer
rung, R10's worst cell median beat R20's best cell median (5/5). That comparison uses the
per-cell median the atlas prints, and those medians average DIFFERENT phase sets:
a cadence-R cell averages its own R offsets, so the R10 column is a median over 10 books,
the R20 column over 20 and the R40 column over 40 -- and the extra offsets R20/R40 add are
start dates the R10 column never covers (bars 10..19 and 20..39). So the ladder may be
part cadence and part "which start dates got averaged in".

Three measurements of the same knob (20 bars -> 10 bars), on the atlas's own rows:
  CROSS_SET   what the atlas prints: median over each cell's own phase set (r2127's ruler)
  MATCHED     paired on the offsets every cadence shares (0..match_n-1), same start date,
              same width, same rung -> the only way to ask "is faster better, holding the
              start date fixed"
  PAIRED_RUN  the independent adoption run (results/etf_book_rebal_adoption.json) which
              re-ran the engine on paired calendars -- read, never recomputed here

WHAT IT ALSO PUBLISHES
----------------------
Every phase book in this family starts between 2020-01-02 and 2020-03-05, i.e. the "band"
that everything is judged against is one winter at the top of a bubble, and the 2020
February-March crash is inside it. The face measures how much of the spread inside a single
cadence is that calendar: it splits each cell's own offsets in half and reports the level
step between halves. That step is compared against the whole cadence gap.

WHAT IT DOES NOT DO
-------------------
It does not change the production cell and does not re-open the schedule decision: that is
results/etf_book_rebal_adoption.json (PHASE_DEPENDENT, "do not change the ticket"). This
surface only fixes the sentence the ladder is allowed to say.

self  python scripts/etf_book_cadence_comparable.py selftest
run   python scripts/etf_book_cadence_comparable.py run
check python scripts/etf_book_cadence_comparable.py check
"""

import glob
import hashlib
import json
import math
import os
import re
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_comparable.json")
ADOPTION_PATH = os.path.join(ROOT, "results", "etf_book_rebal_adoption.json")
FACE = "results/etf_book_cadence_comparable.json"
SCHEMA = "etf-book-cadence-comparable/v1"
BASE_MONEY = 1_000_000.0
MODEL_COST = 0.001          # the atlas's own 10bp/side
REAL_COST = 0.0001          # 1bp/side: A-share ETFs, no stamp duty (assumption, printed)
PAIR_MIN_SHARE = 0.60       # sign rule, frozen before the first read
MATCH_MIN = 3               # a paired comparison over fewer than 3 calendars says nothing

RULE = {
    "R1_rungs": "a panel joins only if its evidence_cutoff equals the modal cutoff; every "
                "excluded panel is named with the reason, never silently dropped",
    "R2_match_prefix": "MATCHED pairs each width on the offsets every cadence shares "
                       "(0..min(offsets)-1) -- never a median of a different-sized set",
    "R3_cross_set": "CROSS_SET reproduces the atlas's own reading (median over a cell's own "
                    "phase set) so the two rulers are printed side by side",
    "R4_sign": "the paired direction holds iff at least %.0f%% of pairs move the same way; "
               "the separation word holds iff the worst of one cadence still beats the best "
               "of the other on matched calendars" % (PAIR_MIN_SHARE * 100),
    "R5_calendar": "the calendar term for a cell is the level step between the first and the "
                   "second half of that cell's own offsets; if it is the same size as the "
                   "cadence gap, the gap is not attributable to cadence alone",
    "R6_money": "money lines use a %d reference account and the panel's own cost step" % BASE_MONEY,
    "R7_no_invented": "a missing panel or a missing width is a named hole, never a zero",
    "frozen": "threshold words written before the first read of these panels in this round",
}


# --------------------------------------------------------------------------------------
# small statistics
# --------------------------------------------------------------------------------------
def binom_two_sided(k, n, p=0.5):
    """exact two-sided binomial p-value for k successes out of n."""
    if n <= 0:
        return 1.0
    def pmf(i):
        return math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    obs = pmf(k)
    total = 0.0
    for i in range(n + 1):
        v = pmf(i)
        if v <= obs * (1 + 1e-12):
            total += v
    return min(1.0, total)


def sci(x, nd=6):
    return abs(x) < 1e-12


# --------------------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------------------
def discover_panels(results_dir):
    """k from the fixed atlas filename, so a stray file cannot be read as a rung."""
    out, rejected = [], []
    for path in sorted(glob.glob(os.path.join(results_dir, "etf_book_phase_atlas_buffer_k*.json"))):
        m = re.match(r"^etf_book_phase_atlas_buffer_k(\d+)\.json$", os.path.basename(path))
        if not m:
            rejected.append({"panel": os.path.basename(path), "why": "filename is not a buffer rung"})
            continue
        out.append({"k": int(m.group(1)) / 100.0, "name": os.path.basename(path), "path": path})
    return out, rejected


def load_panels(results_dir):
    found, rejected = discover_panels(results_dir)
    loaded = []
    for f in found:
        with open(f["path"], "rb") as fh:
            raw = fh.read()
        doc = json.loads(raw.decode("utf-8"))
        rows = doc.get("rows") or []
        if not rows:
            rejected.append({"panel": f["name"], "why": "no rows"})
            continue
        loaded.append({
            "k": f["k"], "panel": f["name"], "sha1": hashlib.sha1(raw).hexdigest(),
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "cost": (doc.get("audit") or {}).get("cost"),
            "target_vol": (doc.get("audit") or {}).get("target_vol"),
            "start": (doc.get("audit") or {}).get("start"),
            "rows": rows,
        })
    if not loaded:
        return [], rejected
    cut = st.mode([p["evidence_cutoff"] for p in loaded])
    keep = [p for p in loaded if p["evidence_cutoff"] == cut]
    for p in loaded:
        if p["evidence_cutoff"] != cut:
            rejected.append({"panel": p["panel"],
                             "why": "evidence_cutoff %r is not the rung cutoff %r"
                                    % (p["evidence_cutoff"], cut)})
    return keep, rejected


def cell_map(panel):
    """{(n_hold, rebal): {offset: row}} -- offsets are the books of that cell."""
    out = {}
    for r in panel["rows"]:
        out.setdefault((r["n_hold"], r["rebal"]), {})[r["phase_offset"]] = r
    return out


def years_between(start_iso, cutoff_iso):
    import datetime as dt
    a = dt.date.fromisoformat(start_iso)
    b = dt.date.fromisoformat(cutoff_iso)
    return max(1e-9, (b - a).days / 365.25)


# --------------------------------------------------------------------------------------
# the three measurements
# --------------------------------------------------------------------------------------
def cross_set(panel):
    """the atlas's own reading: median over each cell's own phase set."""
    cells = cell_map(panel)
    out = {}
    for (nh, rb), offs in cells.items():
        vals = sorted(v["cagr"] for v in offs.values())
        out[(nh, rb)] = {
            "median_pct": st.median(vals) * 100.0,
            "mean_pct": st.mean(vals) * 100.0,
            "n_offsets": len(vals),
            "min_pct": min(vals) * 100.0,
            "max_pct": max(vals) * 100.0,
        }
    return out


def matched(panel, cadences, widths, match_n):
    """paired on shared offsets; returns per-width deltas for the (10,20) and (20,40) steps."""
    cells = cell_map(panel)
    out = {}
    for a, b in ((10, 20), (20, 40)):
        per_width = []
        for nh in widths:
            ra, rb = cells.get((nh, a)), cells.get((nh, b))
            if not ra or not rb:
                continue
            offs = [o for o in range(match_n) if o in ra and o in rb]
            if len(offs) < MATCH_MIN:
                continue
            va = [ra[o]["cagr"] * 100.0 for o in offs]
            vb = [rb[o]["cagr"] * 100.0 for o in offs]
            d = [x - y for x, y in zip(va, vb)]
            per_width.append({
                "n_hold": nh, "offsets": len(offs),
                "a": a, "b": b,
                "a_median_pct": st.median(va), "b_median_pct": st.median(vb),
                "delta_median_pp": st.median(d), "delta_mean_pp": st.mean(d),
                "a_min_pct": min(va), "a_max_pct": max(va),
                "b_min_pct": min(vb), "b_max_pct": max(vb),
                "separated": bool(min(va) > max(vb)),
                "pairs_a_wins": sum(1 for x in d if x > 0),
                "pairs": len(d),
            })
        out[(a, b)] = {
            "per_width": per_width,
            "pairs_total": sum(w["pairs"] for w in per_width),
            "pairs_a_wins": sum(w["pairs_a_wins"] for w in per_width),
            "separated_widths": sum(1 for w in per_width if w["separated"]),
            "widths": len(per_width),
            "delta_median_of_widths_pp": (st.median([w["delta_median_pp"] for w in per_width])
                                          if per_width else None),
        }
        if out[(a, b)]["pairs_total"]:
            out[(a, b)]["sign_p"] = binom_two_sided(out[(a, b)]["pairs_a_wins"],
                                                    out[(a, b)]["pairs_total"])
            out[(a, b)]["a_win_share"] = (out[(a, b)]["pairs_a_wins"]
                                          / out[(a, b)]["pairs_total"])
        else:
            out[(a, b)]["sign_p"] = None
            out[(a, b)]["a_win_share"] = None
    return out


def calendar_term(panel, widths, cadences):
    """how much of a cell's own spread is 'which half of the cycle you start in'."""
    cells = cell_map(panel)
    out = []
    for rb in cadences:
        steps = []
        for nh in widths:
            offs = cells.get((nh, rb))
            if not offs:
                continue
            ks = sorted(offs)
            half = len(ks) // 2
            if half < 2:
                continue
            first = [offs[k]["cagr"] * 100.0 for k in ks[:half]]
            second = [offs[k]["cagr"] * 100.0 for k in ks[half:]]
            steps.append({
                "n_hold": nh, "rebal": rb,
                "first_half_mean_pct": st.mean(first),
                "second_half_mean_pct": st.mean(second),
                "step_pp": st.mean(second) - st.mean(first),
                "offsets": len(ks),
            })
        if steps:
            out.append({"rebal": rb,
                        "step_median_pp": st.median([s["step_pp"] for s in steps]),
                        "step_max_abs_pp": max(abs(s["step_pp"]) for s in steps),
                        "per_width": steps})
    return out


def toll(cells, rebal, nh, cost, years):
    offs = cells.get((nh, rebal))
    if not offs:
        return None
    dec = st.mean([o["decisions"] for o in offs.values()])
    turn = st.mean([o["turnover_per_decision"] for o in offs.values()])
    per_year = dec * turn * cost / years * 100.0
    return {"decisions": dec, "turnover_per_decision": turn,
            "edges": dec * turn, "toll_pct_per_year": per_year}


# --------------------------------------------------------------------------------------
# run / check
# --------------------------------------------------------------------------------------
def compute():
    panels, rejected = load_panels(os.path.join(ROOT, "results"))
    if not panels:
        return None
    cut = panels[0]["evidence_cutoff"]
    start = panels[0]["start"] or "2020-01-01"
    years = years_between(start, cut)
    cadences = sorted({r["rebal"] for p in panels for r in p["rows"]})
    widths = sorted({r["n_hold"] for p in panels for r in p["rows"]})
    counts = {c: sorted({r["phase_offset"] for p in panels for r in p["rows"]
                         if r["rebal"] == c}) for c in cadences}
    match_n = min(len(v) for v in counts.values() if v)
    first_decisions = sorted({r["first_decision"] for p in panels for r in p["rows"]})

    rungs = []
    for p in sorted(panels, key=lambda z: z["k"]):
        cs = cross_set(p)
        mt = matched(p, cadences, widths, match_n)
        rungs.append({
            "buffer_k": p["k"], "panel": p["panel"], "sha1": p["sha1"],
            "evidence_cutoff": p["evidence_cutoff"],
            "offsets_per_cadence": {str(c): len(counts[c]) for c in cadences},
            "cross_set": [{"n_hold": nh, "rebal": rb, **v} for (nh, rb), v in sorted(cs.items())],
            "matched": {("%d>%d" % k): v for k, v in mt.items()},
        })

    # the headline: the (10,20) step under both rulers, pooled over rungs and widths
    cross_delta, match_delta, sep_widths, tot_widths, wins, pairs = [], [], 0, 0, 0, 0
    pvals = []
    for r in rungs:
        cs = {(c["n_hold"], c["rebal"]): c for c in r["cross_set"]}
        for nh in widths:
            a, b = cs.get((nh, 10)), cs.get((nh, 20))
            if a and b:
                cross_delta.append(a["median_pct"] - b["median_pct"])
        m = r["matched"].get("10>20")
        if m:
            sep_widths += m["separated_widths"]
            tot_widths += m["widths"]
            wins += m["pairs_a_wins"]
            pairs += m["pairs_total"]
            if m["sign_p"] is not None:
                pvals.append(m["sign_p"])
            match_delta.extend(w["delta_median_pp"] for w in m["per_width"])

    adoption = None
    if os.path.exists(ADOPTION_PATH):
        with open(ADOPTION_PATH, "r", encoding="utf-8") as fh:
            ad = json.load(fh)
        s10 = (ad.get("summary") or {}).get("by_cost", {}).get("10") or {}
        s20 = (ad.get("summary") or {}).get("by_cost", {}).get("20") or {}
        adoption = {
            "face": ADOPTION_PATH.replace(ROOT + os.sep, "").replace("\\", "/"),
            "asof": ad.get("asof"), "evidence_cutoff": ad.get("evidence_cutoff"),
            "verdict": (ad.get("verdict") or {}).get("label"),
            "desk_sentence": ad.get("desk_sentence"),
            "median_delta_cagr_pp_10bp": s10.get("median_delta_cagr_pp"),
            "median_delta_cagr_pp_20bp": s20.get("median_delta_cagr_pp"),
            "share_cagr_up_10bp": s10.get("share_cagr_up"),
            "delta_turnover_per_year_10bp": s10.get("median_delta_turnover_per_year"),
            "n_phases": s10.get("n_phases"),
            "rule_note": "n_hold=5, vol_target 0.08, paired on 5 calendars, own engine run",
        }

    cal = calendar_term(panels[0], widths, cadences)
    cells0 = cell_map(panels[0])
    tol = {}
    for rb in (10, 20, 40):
        tol[rb] = {"model_10bp": toll(cells0, rb, 5, MODEL_COST, years),
                   "real_1bp": toll(cells0, rb, 5, REAL_COST, years)}

    cross_med = st.median(cross_delta) if cross_delta else None
    match_med = st.median(match_delta) if match_delta else None
    win_share = (wins / pairs) if pairs else None

    words = []
    if win_share is not None:
        words.append("MATCHED_SIGN_HOLDS" if win_share >= PAIR_MIN_SHARE
                     else "MATCHED_SIGN_FAILS")
    words.append("MATCHED_SEPARATION_FAILS" if sep_widths == 0 else
                 "MATCHED_SEPARATION_HOLDS_ON_%d_OF_%d" % (sep_widths, tot_widths))
    if cross_med is not None and match_med is not None and match_med > 0:
        ratio = cross_med / match_med
        words.append("CROSS_SET_OVERSTATES_BY_%.2fx" % ratio)

    cal_step = max((abs(c["step_median_pp"]) for c in cal), default=0.0)
    if match_med is not None and cal_step >= abs(match_med):
        words.append("CALENDAR_TERM_EXCEEDS_CADENCE_GAP")

    # money
    money = {}
    d_matched = None
    if match_delta:
        d_matched = match_med
    if d_matched is not None:
        widen = None
        if tol[10]["model_10bp"] and tol[20]["model_10bp"]:
            widen = (tol[10]["model_10bp"]["toll_pct_per_year"]
                     - tol[20]["model_10bp"]["toll_pct_per_year"]) * (1 - REAL_COST / MODEL_COST)
        money = {
            "reference_account_cny": BASE_MONEY,
            "delta_pp_matched_median": d_matched,
            "cny_per_year_if_matched": d_matched / 100.0 * BASE_MONEY,
            "cny_per_year_if_cross_set": (cross_med / 100.0 * BASE_MONEY) if cross_med else None,
            "extra_toll_pp_per_year_at_10bp": widen,
            "cny_extra_if_only_real_commission": (widen / 100.0 * BASE_MONEY) if widen else None,
            "note": "the matched number already pays R10's higher toll; the second line is what "
                    "the gap would widen by if the account pays 1bp/side instead of 10bp",
        }

    return {
        "schema": SCHEMA, "face": FACE,
        "question": "the phase atlas compares R10/R20/R40 cells by the median of each cell's own "
                    "phase set, which averages a different set of start dates per cadence -- is "
                    "the ladder a cadence or a phase-set difference?",
        "rule": RULE,
        "evidence_cutoff": cut, "panel_start": start, "years": years,
        "panel_sha1": {p["panel"]: p["sha1"] for p in panels},
        "excluded_panels": rejected,
        "cadences": cadences, "widths": widths,
        "offsets_per_cadence": {str(c): counts[c] for c in cadences},
        "match_n": match_n,
        "start_date_coverage": {"first_decisions_min": first_decisions[0],
                                "first_decisions_max": first_decisions[-1],
                                "distinct": len(first_decisions),
                                "note": "every phase book in this family starts in this window"},
        "rungs": rungs,
        "headline": {
            "cross_set_median_delta_pp": cross_med,
            "matched_median_delta_pp": match_med,
            "matched_pairs": pairs,
            "matched_pairs_a_wins": wins,
            "matched_a_win_share": win_share,
            "matched_sign_p_min": min(pvals) if pvals else None,
            "matched_separated_widths": sep_widths,
            "matched_widths": tot_widths,
            "verdict_word": " | ".join(words),
        },
        "calendar_term": cal,
        "toll": {str(k): v for k, v in tol.items()},
        "independent_paired_run": adoption,
        "money": money,
        "desk_sentence": (
            "对票面：不改（节奏决定权在 etf_book_rebal_adoption = %s）。"
            "「节奏阶梯 5/5 稳」这句话只能说到「配对同日历上方向仍为正」，"
            "不能说幅度：换一把对齐日历的尺子，20→10 的中位增益从 %s 缩到 %s pp。"
            % (adoption.get("verdict") if adoption else "MISSING",
               ("%.2f" % cross_med) if cross_med is not None else "n/a",
               ("%.2f" % match_med) if match_med is not None else "n/a")
        ),
    }


def write_face(doc):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check():
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % FACE)
        return 3
    with open(OUT_PATH, "r", encoding="utf-8") as fh:
        old = json.load(fh)
    live, _ = load_panels(os.path.join(ROOT, "results"))
    live_sha = {p["panel"]: p["sha1"] for p in live}
    if live_sha != old.get("panel_sha1"):
        moved = [k for k in live_sha if live_sha.get(k) != (old.get("panel_sha1") or {}).get(k)]
        print("STALE input panel bytes moved: %s" % (", ".join(moved) or "set changed"))
        return 3
    new = compute()
    if new is None:
        print("CHECK FAILED no panels")
        return 1
    bad = []
    for field, path in (("cross_set_median_delta_pp", ("headline", "cross_set_median_delta_pp")),
                        ("matched_median_delta_pp", ("headline", "matched_median_delta_pp")),
                        ("matched_pairs", ("headline", "matched_pairs")),
                        ("matched_pairs_a_wins", ("headline", "matched_pairs_a_wins")),
                        ("verdict_word", ("headline", "verdict_word"))):
        a = old.get(path[0], {}).get(path[1])
        b = new.get(path[0], {}).get(path[1])
        if isinstance(a, float) or isinstance(b, float):
            if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
                bad.append("%s %r != %r" % (field, a, b))
        elif a != b:
            bad.append("%s %r != %r" % (field, a, b))
    if bad:
        print("CHECK FAILED " + "; ".join(bad))
        return 1
    print("CHECK OK %d rungs, %d matched pairs, word=%s"
          % (len(old.get("rungs") or []), old["headline"]["matched_pairs"],
             old["headline"]["verdict_word"]))
    return 0


# --------------------------------------------------------------------------------------
# selftest -- synthetic, no panel reads
# --------------------------------------------------------------------------------------
def _mk_offsets(vals):
    return {i: {"phase_offset": i, "phase": "2020-01-%02d" % (i + 2), "cagr": v,
                "sharpe": 1.0, "maxdd": -0.1, "oos_cagr": v, "turnover_per_decision": 1.0,
                "decisions": 84, "first_decision": "2020-01-%02d" % (i + 2),
                "last_decision": "2026-11-01"} for i, v in enumerate(vals)}


def selftest():
    legs, ok = [], 0

    def leg(name, cond):
        nonlocal ok
        legs.append({"leg": name, "pass": bool(cond)})
        if cond:
            ok += 1

    # 1 paired prefix stops at the shared length
    panel = {"k": 0.02, "panel": "x", "sha1": "0", "evidence_cutoff": "2026-11-25",
             "cost": 0.001, "target_vol": 0.08, "start": "2020-01-01",
             "rows": []}
    for nh in (5,):
        for off, v in _mk_offsets([0.11, 0.12, 0.10, 0.13, 0.09, 0.1, 0.11, 0.12, 0.1, 0.105]).items():
            panel["rows"].append(dict(v, n_hold=nh, rebal=10))
        for off, v in _mk_offsets([0.09, 0.10, 0.08, 0.11, 0.07, 0.08, 0.09, 0.10, 0.08,
                                   0.085, 0.01, 0.02, 0.03, 0.04, 0.0]).items():
            panel["rows"].append(dict(v, n_hold=nh, rebal=20))
    mt = matched(panel, [10, 20], [5], 10)
    leg("matched uses only the shared 10 offsets", mt[(10, 20)]["per_width"][0]["pairs"] == 10)
    leg("matched delta is paired, not a median of a bigger set",
        abs(mt[(10, 20)]["per_width"][0]["delta_median_pp"] - 2.0) < 1e-9)
    cs = cross_set(panel)
    leg("cross_set reads the whole 20-offset set (this is the overstating ruler)",
        abs(cs[(5, 20)]["median_pct"] - 8.0) < 1e-9)

    # 2 separation word fails when ranges overlap
    leg("separation is refused on overlapping ranges", mt[(10, 20)]["separated_widths"] == 0)
    sep_panel = {"k": 0.02, "panel": "y", "sha1": "1", "evidence_cutoff": "2026-11-25",
                 "cost": 0.001, "target_vol": 0.08, "start": "2020-01-01", "rows": []}
    for off, v in _mk_offsets([0.2, 0.21, 0.22]).items():
        sep_panel["rows"].append(dict(v, n_hold=5, rebal=10))
    for off, v in _mk_offsets([0.01, 0.02, 0.03]).items():
        sep_panel["rows"].append(dict(v, n_hold=5, rebal=20))
    leg("separation holds when every A beats every B",
        matched(sep_panel, [10, 20], [5], 3)[(10, 20)]["separated_widths"] == 1)

    # 3 sign test
    leg("sign test p is small for 18/20", binom_two_sided(18, 20) < 0.01)
    leg("sign test p is ~1 for 10/20", 0.9 < binom_two_sided(10, 20) <= 1.0)

    # 4 calendar term splits the cell's own offsets
    cal = calendar_term(panel, [5], [20])
    leg("calendar term compares halves of one cell's offsets",
        len(cal) == 1 and cal[0]["rebal"] == 20 and cal[0]["step_median_pp"] < -3.0)

    # 5 toll grows with cadence and scales with cost
    cells = cell_map(panel)
    for off in cells[(5, 10)].values():
        off["decisions"], off["turnover_per_decision"] = 167, 0.82
    t10 = toll(cells, 10, 5, MODEL_COST, 6.9)
    t20 = toll(cells, 20, 5, MODEL_COST, 6.9)
    leg("R10 pays a bigger toll than R20", t10["toll_pct_per_year"] > t20["toll_pct_per_year"])
    leg("toll is linear in the cost step",
        abs(toll(cells, 10, 5, REAL_COST, 6.9)["toll_pct_per_year"]
            - t10["toll_pct_per_year"] / 10.0) < 1e-12)

    # 6 money conversion
    leg("2.0pp on a 1e6 account is 20,000 a year", abs(2.0 / 100.0 * BASE_MONEY - 20000.0) < 1e-9)

    # 7 exclusion of a non-modal cutoff panel
    ok_doc = {"evidence_cutoff": "2026-11-25", "audit": {"cost": 0.001, "target_vol": 0.08,
                                                        "start": "2020-01-01"},
              "rows": [{"n_hold": 5, "rebal": 10, "phase_offset": 0, "phase": "2020-01-02",
                        "cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1, "oos_cagr": 0.1,
                        "turnover_per_decision": 1.0, "decisions": 84,
                        "first_decision": "2020-01-02", "last_decision": "2026-11-01"}]}
    olds = {"evidence_cutoff": "2026-10-29", "audit": {}, "rows": ok_doc["rows"]}
    tmp = os.path.join(ROOT, "results", "_selftest_cadcmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with open(os.path.join(tmp, "etf_book_phase_atlas_buffer_k02.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(ok_doc, fh)
        with open(os.path.join(tmp, "etf_book_phase_atlas_buffer_k30.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(olds, fh)
        kept, rej = load_panels(tmp)
        leg("only the modal cutoff keeps a panel", [p["panel"] for p in kept]
            == ["etf_book_phase_atlas_buffer_k02.json"])
        leg("the excluded panel is named with a reason",
            any("2026-10-29" in r["why"] for r in rej))
        with open(os.path.join(tmp, "etf_book_phase_atlas_buffer_kxx.json"), "w",
                  encoding="utf-8") as fh:
            fh.write("{}")
        kept2, rej2 = load_panels(tmp)
        leg("a non-rung filename is refused, not parsed",
            any("not a buffer rung" in r["why"] for r in rej2) and len(kept2) == 1)
    finally:
        for f in glob.glob(os.path.join(tmp, "*.json")):
            os.remove(f)
        if os.path.isdir(tmp):
            os.rmdir(tmp)

    # 8 rule words are frozen before the read
    leg("thresholds are constants in code", PAIR_MIN_SHARE == 0.60 and MATCH_MIN == 3)
    leg("money base is the reference account", BASE_MONEY == 1_000_000.0)
    leg("sci treats a tiny number as zero", sci(0.0) and not sci(1e-6))

    print(json.dumps({"legs": len(legs), "passed": ok,
                      "failed": [l["leg"] for l in legs if not l["pass"]]},
                     ensure_ascii=False))
    return 0 if ok == len(legs) else 1


def run():
    doc = compute()
    if doc is None:
        print("FATAL no panels")
        return 2
    write_face(doc)
    h = doc["headline"]
    print(json.dumps({"face": FACE, "cutoff": doc["evidence_cutoff"],
                      "cross_set_pp": h["cross_set_median_delta_pp"],
                      "matched_pp": h["matched_median_delta_pp"],
                      "pairs": h["matched_pairs"], "wins": h["matched_pairs_a_wins"],
                      "word": h["verdict_word"]}, ensure_ascii=False))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print("usage: etf_book_cadence_comparable.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
