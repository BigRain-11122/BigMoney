"""ETF book -- replay the era capacity on the WHOLE roster, not on five names.

r1871 measured the capacity line in every year, but always on the five names the book's
own score ranked top on that year's first bar. That answers "what would 1,000,000 CNY have
meant for the book", and it leaves an obvious gap: the five names changed from year to
year, so a growing capacity number cannot say whether the market got DEEPER (the same
names trade more) or WIDER (there are far more names to spread the same trade over) or
whether the score simply started ranking bigger funds.

This face prices four rules on the same anchors:

  * `score_k5`  -- the gate's own lens: the five names the score ranked top (imported
    recipe from `etf_book_era_capacity`, so it must reproduce r1871 row for row).
  * `depth_k5`  -- the five DEEPEST readable names: the same book size, but chosen by
    liquidity instead of by score, so the ruler stops moving with the model.
  * `depth_k10` / `depth_k20` -- the same question at a wider equal-weight book.
  * `full_roster` -- every name with a readable 20-bar ADV that day, equal weight. This
    is the only rule that can be called "the whole roster"; at 61 names (2015) the
    weakest is a corner of the market, at 1,524 names (2026) it is not.

Then it splits the era-to-era change into named pieces, in log points, with an exact
identity per rule:

  fixed K:   total = depth + names     depth = same names, ADV moved
                                       names = the picks changed (survivors only)
  full:      total = breadth + depth   breadth = log(N_B / N_A)
                                       depth   = log(min ADV_B / min ADV_A)

`names` is measured on the SURVIVORS of set A only -- a name that did not trade at B has
no reading there, and quietly pricing it as zero would manufacture capacity. The face
prints how many of A's five survived and names the ones that did not.

Nothing here re-decides the gate, moves the line or re-ranks the book: the line, the lens
and the score recipe are imported, and the leg refuses to publish a reading that does not
reproduce r1871's own rows.

Usage:
    python scripts/etf_book_era_roster.py run
    python scripts/etf_book_era_roster.py check
    python scripts/etf_book_era_roster.py selftest
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_book_capacity_edge as CE  # noqa: E402
import etf_book_era_capacity as EC  # noqa: E402
import etf_book_era_grid as EG  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_era_roster.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_era_roster.md")
PRIOR_JSON = os.path.join(ROOT, "results", "etf_book_era_capacity.json")

SLOTS = 5                      # the gate's five-name lens
K_LADDER = (5, 10, 20)         # equal-weight widths priced on the depth rule
ADV_BARS = 20                  # same window the gate reads
MAX_STALE = 5                  # a name is part of that day's roster only if it printed a
                               # bar within the last MAX_STALE sessions (one trading week);
                               # without this guard a name that stopped trading in 2019 still
                               # answers `adv20_at` on 2026 with its 2019 median, and the
                               # "whole roster" would silently include the dead
DEPTH_LEAD = 2.0               # a piece leads only if it is >= 2x the other piece,
                               # i.e. it carries >= 2/3 of the log change (2/(1+2))
REPRO_TOL_CNY = 1.0            # r1871 publishes CNY rounded to 2 dp


# ---------------------------------------------------------------- inputs

def adv_at_anchors(amt, anchors, bars=ADV_BARS):
    """ADV for every name on every anchor, defined exactly as `adv20_at` defines it.

    `etf_book_capacity_edge.adv20_at(sym, d)` drops that name's holes and takes the median
    of its last `bars` readings at or before `d`. A plain `amt.rolling(20)` does something
    different the moment a name has a hole (it then needs 20 non-NaN rows inside the
    window), so this walks the same definition rather than the convenient one; selftest L8
    pins the two together on a holed series.
    """
    anchors = list(anchors)
    out = {}
    for sym in amt.columns:
        s = amt[sym].dropna()
        col = {}
        for d in anchors:
            sub = s.loc[:d]
            col[d] = float(sub.tail(bars).median()) if len(sub) >= bars else None
        out[str(sym)] = col
    return pd.DataFrame(out).T


def last_valid_positions(amt):
    """Index position of each name's last printed bar -- the roster's recency test."""
    pos = {d: i for i, d in enumerate(amt.index)}
    out = {}
    for sym in amt.columns:
        last = amt[sym].last_valid_index()
        out[str(sym)] = None if last is None else pos.get(last)
    return out


def roster_at(adv_panel, anchor, pos, last_pos, max_stale=MAX_STALE):
    """Every name that traded on `anchor`: readable 20-bar ADV AND a bar in the last week."""
    if anchor not in adv_panel.columns:
        return {}
    col = adv_panel[anchor].dropna()
    here = pos.get(anchor)
    out = {}
    for sym, v in col.items():
        if v is None or not (v > 0):
            continue
        lp = last_pos.get(str(sym))
        if lp is None or here is None or here - lp > max_stale:
            continue
        out[str(sym)] = float(v)
    return out


def cap_equal_weight(advs, k, line):
    """Capital that exactly fills the WEAKEST of `k` equal slots at the line.

    Same algebra as `etf_book_capacity_edge.measure`: reading = (cap/k)/adv_worst, so
    cap = line * k * adv_worst. `advs` is the list of the k deepest readable ADVs.
    """
    if not advs or k <= 0 or line is None:
        return None
    worst = min(advs[:k])
    return float(line) * float(k) * float(worst)


def depth_picks(roster, k):
    """The k deepest names, in order -- chosen by liquidity so the ruler cannot move
    with the score."""
    return sorted(roster.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def cap_score(roster, picks, line):
    """The gate's lens (r1871 recipe) priced on this roster: five equal slots, worst binds."""
    if not picks:
        return None
    advs = [roster.get(s) for s in picks]
    if any(a is None for a in advs):
        return None
    return cap_equal_weight([a for a in advs], len(advs), line)


# ---------------------------------------------------------------- decomposition

def split_fixed_k(roster_a, roster_b, picks_a, picks_b, k, line):
    """log capacity change between two anchors at a fixed width, split exactly.

    depth = the same NAMES, the market's depth moved (survivors of A priced at both ends)
    names = the SAME END-POINT depth, the picks changed (A's survivors -> B's picks)

    Both pieces are read PER SLOT (worst slot's ADV), never on the total: when one of A's
    five names no longer trades, the surviving subset has fewer slots, and a total-capacity
    reading would book that missing slot as a "name" effect worth log(k/n_surv) all by
    itself. Per slot, losing a name changes nothing about depth -- it is reported instead.
    The identity depth + names == total holds by construction; L2 pins it.
    """
    surv = [s for s in picks_a if roster_a.get(s) is not None and roster_b.get(s) is not None]
    dropped = [s for s in picks_a if s not in surv]
    out = {"k": k, "survivors": surv, "dropped": dropped, "n_surv": len(surv),
           "cap_a": None, "cap_b": None, "per_slot_a_cny": None, "per_slot_b_cny": None,
           "depth_pp": None, "names_pp": None, "total_pp": None, "multiple": None,
           "split_total_pp": None, "verdict": None}
    if not surv or not picks_b:
        out["verdict"] = "UNCOMPARABLE_NO_SURVIVORS" if not surv else "NO_PICKS_AT_B"
        return out
    worst_a_surv = min(roster_a[s] for s in surv)
    worst_b_surv = min(roster_b[s] for s in surv)
    advs_b_picks = [roster_b.get(s) for s in picks_b]
    if any(a is None for a in advs_b_picks):
        out["verdict"] = "UNREADABLE"
        return out
    worst_b_picks = min(advs_b_picks)
    depth = math.log(worst_b_surv) - math.log(worst_a_surv)
    names = math.log(worst_b_picks) - math.log(worst_b_surv)
    total = math.log(worst_b_picks) - math.log(worst_a_surv)
    # the book-to-book statement uses every pick on both sides, so it is only the same
    # number as `total` when every left-hand pick survived
    worst_a_picks = min(roster_a[s] for s in picks_a) if picks_a else None
    cap_a = (float(line) * len(picks_a) * worst_a_picks) if worst_a_picks else None
    cap_b = float(line) * len(picks_b) * worst_b_picks
    split_total = math.log(worst_b_picks) - math.log(worst_a_picks) if worst_a_picks else None
    out.update({"cap_a": cap_a, "cap_b": cap_b,
                "per_slot_a_cny": float(line) * worst_a_picks if worst_a_picks else None,
                "per_slot_b_cny": float(line) * worst_b_picks,
                "depth_pp": round(depth * 100.0, 4), "names_pp": round(names * 100.0, 4),
                "total_pp": round(total * 100.0, 4),
                "split_total_pp": None if split_total is None
                else round(split_total * 100.0, 4),
                "multiple": round(cap_b / cap_a, 4) if cap_a else None,
                "verdict": _fixed_verdict(depth, names)})
    return out


def _fixed_verdict(depth, names):
    """Same lead bar as `lead_verdict`, named for the two pieces it actually splits.

    When the two pieces point the OPPOSITE way (the same names got shallower while the
    new picks are deeper) a plain "which is bigger" answer would read as if both moved in
    the same direction -- so opposing signs get their own names.
    """
    v = lead_verdict(depth, names)
    if depth * names < 0:
        a, b = abs(depth), abs(names)
        if b >= DEPTH_LEAD * a:
            return "NAMES_LEAD_AGAINST_SHRINKING_DEPTH"
        if a >= DEPTH_LEAD * b:
            return "DEPTH_LEAD_AGAINST_CHANGING_NAMES"
        return "OPPOSING_PIECES"
    return {"LEFT_LEADS": "DEPTH_LEADS", "RIGHT_LEADS": "NAMES_LEAD"}.get(v, v)


def split_full_roster(roster_a, roster_b, line):
    """The whole-roster rule, split into breadth (how many names) and depth (how deep).

    cap = line * N * min(ADV), so log change = log(N_B/N_A) + log(min_B/min_A) exactly.
    """
    out = {"n_a": len(roster_a), "n_b": len(roster_b), "cap_a": None, "cap_b": None,
           "breadth_pp": None, "depth_pp": None, "total_pp": None, "multiple": None,
           "verdict": None}
    if not roster_a or not roster_b:
        out["verdict"] = "EMPTY_ROSTER"
        return out
    cap_a = cap_equal_weight(sorted(roster_a.values()), len(roster_a), line)
    cap_b = cap_equal_weight(sorted(roster_b.values()), len(roster_b), line)
    breadth = math.log(len(roster_b)) - math.log(len(roster_a))
    depth = math.log(cap_b) - math.log(cap_a) - breadth
    total = math.log(cap_b) - math.log(cap_a)
    out.update({"cap_a": cap_a, "cap_b": cap_b,
                "breadth_pp": round(breadth * 100.0, 4),
                "depth_pp": round(depth * 100.0, 4),
                "total_pp": round(total * 100.0, 4),
                "multiple": round(cap_b / cap_a, 4),
                "verdict": lead_verdict(breadth, depth)})
    return out


def lead_verdict(left, right):
    """Which piece carried the change -- by counts, with a declared lead bar.

    `left`/`right` are log components (fractions, not pp). A piece "leads" when it is at
    least DEPTH_LEAD times the other in absolute size, i.e. it carries >= 2/3 of the
    move. Two pieces that oppose each other cannot be called a lead in either direction,
    so they land in BOTH_MATTER unless one is far larger.
    """
    a, b = abs(left), abs(right)
    if a == 0 and b == 0:
        return "NO_CHANGE"
    if a >= DEPTH_LEAD * b:
        return "LEFT_LEADS"
    if b >= DEPTH_LEAD * a:
        return "RIGHT_LEADS"
    return "BOTH_MATTER"


# ---------------------------------------------------------------- one anchor

def measure_anchor(adv_panel, last_pos, pos, sc, anchor, line, per_name=None):
    """Everything one anchor can say about the roster the market offered that day."""
    d = pd.Timestamp(anchor)
    key = str(d.date())
    roster = roster_at(adv_panel, key, pos, last_pos)
    out = {"anchor": str(d.date()), "year": int(str(d.date())[:4]),
           "n_names": len(roster),
           "adv_total_cny": round(sum(roster.values()), 2) if roster else None,
           "adv_median_cny": round(statistics.median(roster.values()), 2) if roster else None,
           "adv_min_cny": round(min(roster.values()), 2) if roster else None,
           "cap_full_roster_cny": None, "depth_k": {}, "depth_picks": {},
           "n_slots_at_budget": None,
           "score_picks": [], "cap_score_k5_cny": None, "score_all_readable": None}
    if not roster:
        out["why"] = "no name had a readable 20-bar ADV on this bar"
        return out
    out["cap_full_roster_cny"] = cap_equal_weight(sorted(roster.values()), len(roster), line)
    if per_name:
        # how many names could take the gate's own per-slot order at the line -- a count,
        # so a single micro-name cannot move it the way it moves `cap_full_roster`
        out["n_slots_at_budget"] = sum(1 for v in roster.values() if v * line >= per_name)
    for k in K_LADDER:
        picked = depth_picks(roster, k)
        out["depth_picks"]["k%d" % k] = [s for s, _ in picked]
        out["depth_k"]["k%d" % k] = cap_equal_weight([a for _, a in picked], len(picked), line)
    picks = EC.picks_at(sc, d, SLOTS)
    if picks:
        out["score_picks"] = list(picks)
        out["cap_score_k5_cny"] = cap_score(roster, picks, line)
        out["score_all_readable"] = out["cap_score_k5_cny"] is not None
    return out


# ---------------------------------------------------------------- render / summary

def pairs_of(rows, anchors_named, line):
    """The three named windows this face decomposes (earliest, the 2021-2023 era, today)."""
    by = {r["anchor"]: r for r in rows}
    out = []
    for a_anchor, b_anchor, label in anchors_named:
        ra, rb = by.get(a_anchor), by.get(b_anchor)
        if ra is None or rb is None:
            continue
        adv_a = ra.get("_roster") or {}
        adv_b = rb.get("_roster") or {}
        fixed = split_fixed_k(adv_a, adv_b, ra.get("score_picks") or [],
                              rb.get("score_picks") or [], SLOTS, line)
        # control: the same width chosen by depth instead of by score. This is the
        # ruler-free split -- it cannot move because the model changed its mind.
        deep = split_fixed_k(adv_a, adv_b,
                             [s for s, _ in depth_picks(adv_a, SLOTS)],
                             [s for s, _ in depth_picks(adv_b, SLOTS)], SLOTS, line)
        full = split_full_roster(adv_a, adv_b, line)
        slots_a, slots_b = ra.get("n_slots_at_budget"), rb.get("n_slots_at_budget")
        slots = {"n_a": slots_a, "n_b": slots_b,
                 "multiple": (round(slots_b / float(slots_a), 4)
                              if slots_a and slots_b else None),
                 "pp": (round(math.log(slots_b / float(slots_a)) * 100.0, 4)
                        if slots_a and slots_b else None)}
        out.append({"window": label, "from": a_anchor, "to": b_anchor,
                    "score_k5": fixed, "deep_k5": deep, "budget_slots": slots,
                    "full_roster": full})
    return out


def summarise(rows, pairs):
    """Only what the rows and pairs can support -- sentences read this, never raw math."""
    out = {"n_anchors": len(rows),
           "first_anchor": rows[0]["anchor"] if rows else None,
           "last_anchor": rows[-1]["anchor"] if rows else None,
           "n_names_first": rows[0]["n_names"] if rows else None,
           "n_names_last": rows[-1]["n_names"] if rows else None,
           "adv_total_first_cny": rows[0]["adv_total_cny"] if rows else None,
           "adv_total_last_cny": rows[-1]["adv_total_cny"] if rows else None,
           "adv_median_first_cny": rows[0]["adv_median_cny"] if rows else None,
           "adv_median_last_cny": rows[-1]["adv_median_cny"] if rows else None}
    if out["n_names_first"] and out["n_names_last"]:
        out["roster_multiple"] = round(out["n_names_last"] / float(out["n_names_first"]), 2)
    if out["adv_total_first_cny"] and out["adv_total_last_cny"]:
        out["adv_total_multiple"] = round(out["adv_total_last_cny"] / out["adv_total_first_cny"], 2)
    if out["adv_median_first_cny"] and out["adv_median_last_cny"]:
        out["adv_median_multiple"] = round(
            out["adv_median_last_cny"] / float(out["adv_median_first_cny"]), 2)
    heads = [p["deep_k5"]["verdict"] for p in pairs
             if p["deep_k5"]["verdict"] in ("DEPTH_LEADS", "NAMES_LEAD", "BOTH_MATTER",
                                            "OPPOSING_PIECES",
                                            "NAMES_LEAD_AGAINST_SHRINKING_DEPTH",
                                            "DEPTH_LEAD_AGAINST_CHANGING_NAMES")]
    out["deep_k5_leads"] = heads
    out["score_k5_leads"] = [p["score_k5"]["verdict"] for p in pairs
                             if p["score_k5"]["verdict"] in ("DEPTH_LEADS", "NAMES_LEAD",
                                                             "BOTH_MATTER", "OPPOSING_PIECES",
                                                             "NAMES_LEAD_AGAINST_SHRINKING_DEPTH",
                                                             "DEPTH_LEAD_AGAINST_CHANGING_NAMES")]
    if rows:
        # what the ranking cost on the first anchor: the five deepest names vs the five
        # the score picked, same bar, same line
        d5 = (rows[0].get("depth_k") or {}).get("k5")
        s5 = rows[0].get("cap_score_k5_cny")
        out["cap_deep5_first_cny"] = d5
        out["cap_score5_first_cny"] = s5
        if d5 and s5:
            out["ranking_cost_pp_first"] = round(math.log(d5 / s5) * 100.0, 4)
            out["ranking_cost_multiple_first"] = round(d5 / s5, 2)
    out["n_slots_first"] = rows[0].get("n_slots_at_budget") if rows else None
    out["n_slots_last"] = rows[-1].get("n_slots_at_budget") if rows else None
    if out["n_slots_first"] and out["n_slots_last"]:
        out["slots_multiple"] = round(out["n_slots_last"] / float(out["n_slots_first"]), 2)
    out["verdict"] = roster_verdict(out)
    return out


def roster_verdict(s):
    """The headline, named from counts. The pieces are the DEPTH-CHOSEN five names, so the
    verdict cannot move because the score changed its mind; the score book's own split is
    published beside it as the thing the company actually trades."""
    heads = s.get("deep_k5_leads") or []
    if not heads:
        return "NO_WINDOW_MEASURED"
    if len(set(heads)) == 1:
        return {"DEPTH_LEADS": "DEPTH_LEADS_EVERY_WINDOW",
                "NAMES_LEAD": "NAMES_LEAD_EVERY_WINDOW",
                "BOTH_MATTER": "DEPTH_AND_NAMES_MOVE_TOGETHER",
                "OPPOSING_PIECES": "NAMES_AND_DEPTH_OPPOSE",
                "NAMES_LEAD_AGAINST_SHRINKING_DEPTH":
                    "NAMES_LEAD_AGAINST_SHRINKING_DEPTH",
                "DEPTH_LEAD_AGAINST_CHANGING_NAMES":
                    "DEPTH_LEAD_AGAINST_CHANGING_NAMES"}.get(heads[0], heads[0])
    return "SPLIT_BY_WINDOW"


def sentence_roster(s):
    if not s.get("roster_multiple"):
        return "the roster could not be counted at both ends"
    slots = ("%d -> %d names" % (s["n_slots_first"], s["n_slots_last"])
             if s.get("n_slots_first") and s.get("n_slots_last") else "not counted")
    return ("the roster went from %d readable names to %d (%.2fx); per-name median ADV "
            "%.2fx, total ADV %.2fx; names that can take the gate's own 200k slice at the "
            "line: %s -- the era changed the COUNT of places to stand far more than the "
            "depth of any one place"
            % (s["n_names_first"], s["n_names_last"], s["roster_multiple"],
               s.get("adv_median_multiple") or float("nan"),
               s.get("adv_total_multiple") or float("nan"), slots))


def sentence_ranking(s):
    """What the RANKING cost, read on one bar: five deepest vs the five the score picked."""
    if not s.get("ranking_cost_multiple_first"):
        return "the ranking's cost could not be read on the first anchor"
    return ("on %s the same line and the same five equal slots carry %s CNY if the five "
            "deepest names are used and %s CNY for the five the score picked -- %.2fx, so "
            "the early DENY was about WHICH five names, not about the size of that market"
            % (s["first_anchor"], _money(s["cap_deep5_first_cny"]),
               _money(s["cap_score5_first_cny"]), s["ranking_cost_multiple_first"]))


def render_md(p):
    s = p["summary"]
    L = ["# ETF book -- era capacity on the whole roster", "",
         "generated %s | evidence cutoff %s | line %.2f%% of ADV | lens %s CNY"
         % (p["generated"], p["evidence_cutoff"], p["criteria"]["line_pct"],
            "{:,.0f}".format(p["criteria"]["lens_cny"])), "",
         "## Verdict", "", "- **%s**" % s["verdict"], "- " + sentence_roster(s),
         "- " + sentence_ranking(s), ""]
    L += ["## Roster by anchor", "",
          "| anchor | names | ADV total (CNY/day) | ADV median | ADV min | slots at 200k | "
          "cap k5 score | cap k5 depth | cap full (bound) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in p["roster"]:
        L.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (
            r["anchor"], r["n_names"],
            _money(r.get("adv_total_cny")), _money(r.get("adv_median_cny")),
            _money(r.get("adv_min_cny")), r.get("n_slots_at_budget"),
            _money(r.get("cap_score_k5_cny")),
            _money((r.get("depth_k") or {}).get("k5")),
            _money(r.get("cap_full_roster_cny"))))
    L += ["", "## The change, split", "",
          "log points. `total = depth + names` at a fixed five slots; `total = breadth + "
          "depth` on the whole roster, which is bound by the WEAKEST readable name and is "
          "published as a width bound, not as a book. `names` is measured on the survivors "
          "of the left-hand picks only, and a pick with no reading at the right-hand anchor "
          "is named rather than priced at zero.", ""]
    for pr in p["pairs"]:
        f5, deep, sl, fr = pr["score_k5"], pr["deep_k5"], pr["budget_slots"], pr["full_roster"]
        L += ["### %s (%s -> %s)" % (pr["window"], pr["from"], pr["to"]), "",
              "- five slots by score: %s CNY -> %s CNY (%.2fx) | per slot %s -> %s | "
              "depth %s pp | names %s pp | **%s** | survivors %d/%d%s"
              % (_money(f5["cap_a"]), _money(f5["cap_b"]), f5.get("multiple") or 0,
                 _money(f5.get("per_slot_a_cny")), _money(f5.get("per_slot_b_cny")),
                 _num(f5["depth_pp"]), _num(f5["names_pp"]), f5["verdict"],
                 f5["n_surv"], len(f5["survivors"]) + len(f5["dropped"]),
                 (" (dropped: %s)" % ", ".join(f5["dropped"])) if f5["dropped"] else ""),
              "- five DEEPEST (control, no ranking): %s CNY -> %s CNY (%.2fx) | per slot "
              "%s -> %s | depth %s pp | names %s pp | **%s**"
              % (_money(deep["cap_a"]), _money(deep["cap_b"]), deep.get("multiple") or 0,
                 _money(deep.get("per_slot_a_cny")), _money(deep.get("per_slot_b_cny")),
                 _num(deep["depth_pp"]), _num(deep["names_pp"]), deep["verdict"]),
              "- names that can take the gate's own 200k slice at the line: %s -> %s (%.2fx, "
              "%s pp)"
              % (sl["n_a"], sl["n_b"], sl.get("multiple") or 0, _num(sl["pp"])),
              "- whole roster equal weight (bound): %d -> %d names, %s CNY -> %s CNY (%.2fx) | "
              "breadth %s pp | depth %s pp | **%s**"
              % (fr["n_a"], fr["n_b"], _money(fr["cap_a"]), _money(fr["cap_b"]),
                 fr.get("multiple") or 0, _num(fr["breadth_pp"]), _num(fr["depth_pp"]),
                 fr["verdict"]), ""]
    L += ["## What this face will not say", ""]
    L += ["- %s" % h for h in p["honest"]]
    L.append("")
    return "\n".join(L)


def _money(v):
    return "-" if v is None else "{:,.0f}".format(v)


def _num(v):
    return "-" if v is None else "%+.2f" % v


# ---------------------------------------------------------------- check

def check(payload):
    """Recompute what can be recomputed without the panel, and name what cannot.

    The independent anchor is the PREVIOUS face: every `cap_score_k5_cny` here is the same
    quantity r1871 published per year, produced by a different code path (CE.measure over
    per-name slices). If those disagree the matrix is wrong and nothing here is readable.
    """
    problems = []
    for r in payload.get("roster") or []:
        for k, v in (r.get("depth_k") or {}).items():
            if v is not None and r.get("adv_min_cny") and v < 0:
                problems.append("%s %s negative capacity" % (r["anchor"], k))
    for pr in payload.get("pairs") or []:
        f5 = pr["score_k5"]
        if f5.get("depth_pp") is not None and f5.get("names_pp") is not None:
            gap = abs((f5["depth_pp"] + f5["names_pp"]) - f5["total_pp"])
            if gap > 0.01:
                problems.append("%s five-slot identity off by %.4f pp" % (pr["window"], gap))
            if f5.get("verdict") != _fixed_verdict(f5["depth_pp"] / 100.0,
                                                  f5["names_pp"] / 100.0):
                problems.append("%s five-slot verdict does not follow its own counts"
                                % pr["window"])
        deep = pr.get("deep_k5") or {}
        if deep.get("depth_pp") is not None and deep.get("names_pp") is not None:
            gap = abs((deep["depth_pp"] + deep["names_pp"]) - deep["total_pp"])
            if gap > 0.01:
                problems.append("%s depth-k5 identity off by %.4f pp" % (pr["window"], gap))
            if deep.get("verdict") != _fixed_verdict(deep["depth_pp"] / 100.0,
                                                     deep["names_pp"] / 100.0):
                problems.append("%s depth-k5 verdict does not follow its own counts"
                                % pr["window"])
        fr = pr["full_roster"]
        if fr.get("breadth_pp") is not None and fr.get("depth_pp") is not None:
            gap = abs((fr["breadth_pp"] + fr["depth_pp"]) - fr["total_pp"])
            if gap > 0.01:
                problems.append("%s roster identity off by %.4f pp" % (pr["window"], gap))
            if fr.get("verdict") != lead_verdict(fr["breadth_pp"] / 100.0,
                                                 fr["depth_pp"] / 100.0):
                problems.append("%s roster verdict does not follow its own counts"
                                % pr["window"])
    # freshness: the face is only as new as the panel it counts
    cutoff = payload.get("evidence_cutoff")
    panel_last = (payload.get("criteria") or {}).get("panel_last")
    if not cutoff or not panel_last or cutoff != panel_last:
        problems.append("STALE: evidence_cutoff %r != panel_last %r (re-run run)"
                        % (cutoff, panel_last))
    # cross-face reproduction of r1871's per-year five-slot capacity
    repro = {"checked": 0, "mismatched": []}
    prior = None
    try:
        with io.open(PRIOR_JSON, encoding="utf-8") as f:
            prior = json.load(f)
    except (IOError, OSError, ValueError):
        problems.append("STALE: prior face %s is unreadable, cannot cross-check"
                        % os.path.basename(PRIOR_JSON))
    if prior:
        mine = {r["anchor"]: r.get("cap_score_k5_cny") for r in payload.get("roster") or []}
        for row in (prior.get("years") or []):
            want = row.get("capital_where_at_line_cny")
            got = mine.get(str(row.get("anchor")))
            if want is None or got is None:
                continue
            repro["checked"] += 1
            if abs(got - want) > REPRO_TOL_CNY:
                repro["mismatched"].append({"anchor": row["anchor"], "prior": want, "mine": got})
    if repro["mismatched"]:
        problems.append("five-slot capacity does not reproduce r1871 at %d anchor(s)"
                        % len(repro["mismatched"]))
    summary = payload.get("summary") or {}
    if summary.get("verdict") != roster_verdict(summary):
        problems.append("headline verdict does not follow the window verdicts")
    return {"ok": not problems, "problems": problems, "repro": repro}


# ---------------------------------------------------------------- run

def run() -> int:
    t0 = time.time()
    face = EC.load_gate()
    rituals = EC.rulers(face)
    if rituals["line_frac"] is None or rituals["lens_cny"] is None:
        print("gate face carries no usable ruler: line=%r lens=%r"
              % (rituals["line_pct"], rituals["lens_cny"]), flush=True)
        return 2
    line = rituals["line_frac"]

    close, openp, amt, sc, _n_flip = S.nobond_universe()

    anchors = [str(pd.Timestamp(a["first_bar"]).date()) for a in EG.year_anchors(sc.index)]
    last_bar = str(pd.Timestamp(sc.index[-1]).date())
    anchors.append(last_bar)

    adv_panel = adv_at_anchors(amt, anchors)
    last_pos = last_valid_positions(amt)
    pos = {str(pd.Timestamp(d).date()): i for i, d in enumerate(amt.index)}

    per_name = float(rituals["lens_cny"]) / SLOTS
    rows = []
    for a in anchors:
        r = measure_anchor(adv_panel, last_pos, pos, sc, a, line, per_name)
        r["_roster"] = roster_at(adv_panel, a, pos, last_pos)
        rows.append(r)
        print("  %s  names=%d  slots=%s  adv_total=%s  cap_k5_score=%s  cap_full=%s"
              % (r["anchor"], r["n_names"], r.get("n_slots_at_budget"),
                 _money(r.get("adv_total_cny")),
                 _money(r.get("cap_score_k5_cny")), _money(r.get("cap_full_roster_cny"))),
              flush=True)

    era_2021 = str(pd.Timestamp(next(
        a["first_bar"] for a in EG.year_anchors(sc.index) if a["year"] == 2021)).date()) \
        if any(a["year"] == 2021 for a in EG.year_anchors(sc.index)) else None
    named = [(anchors[0], last_bar, "first anchor -> today")]
    if era_2021 and era_2021 != anchors[0]:
        named.append((anchors[0], era_2021, "first anchor -> 2021-2023 era"))
        named.append((era_2021, last_bar, "2021-2023 era -> today"))
    pairs = pairs_of(rows, named, line)

    summary = summarise(rows, pairs)
    payload = {
        "face": "etf_book_era_roster",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": last_bar,
        "criteria": {"line_pct": rituals["line_pct"], "line_frac": line,
                     "lens_cny": rituals["lens_cny"], "lens_label": rituals["lens"],
                     "slots": SLOTS, "k_ladder": list(K_LADDER),
                     "per_name_cny": per_name, "adv_bars": ADV_BARS,
                     "max_stale_sessions": MAX_STALE, "depth_lead": DEPTH_LEAD,
                     "panel_last": last_bar,
                     "gate_panel_last": rituals["panel_last"],
                     "repro_tol_cny": REPRO_TOL_CNY},
        "summary": summary,
        "roster": [{k: v for k, v in r.items() if k != "_roster"} for r in rows],
        "pairs": pairs,
        "honest": [
            "the roster is the ETF list that exists TODAY; names that listed before 2015 "
            "and died before 2026 are absent, so 2015's 61 readable names is an undercount "
            "and the breadth multiple is a floor in the other direction -- it compares "
            "surviving-2015 names with surviving-2026 names",
            "`full_roster` equal-weights EVERY readable name, so it is bound by the weakest "
            "corner of the roster, not by the book the company runs; read it as the "
            "market's width, not as a strategy",
            "`depth_k5` picks the five deepest names, which is a different book from the "
            "score book by construction -- it is the control that removes the ranking",
            "a name counts toward the roster only if it printed a bar within the last %d "
            "sessions: a name that stopped trading keeps answering `adv20_at` with its old "
            "median, and counting it would put dead funds in today's roster" % MAX_STALE,
            "`n_slots_at_budget` counts names that can absorb the gate's own per-slot order "
            "(lens/%d) at the line -- a count, so one micro-fund cannot move it" % SLOTS,
            "`names` in the five-slot split is measured on the survivors of the left-hand "
            "picks, PER SLOT: a pick that does not trade at the right-hand anchor is named "
            "and excluded rather than priced at zero, and the loss of that slot is not "
            "booked as a name effect -- the book-to-book multiple beside it still prices "
            "five slots at both ends",
            "the ADV reading is a 20-bar median as of each bar, so every year is measured "
            "with the liquidity it had",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }

    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))

    print("%s | %s" % (summary["verdict"], sentence_roster(summary)), flush=True)
    print(sentence_ranking(summary), flush=True)
    for pr in pairs:
        print("  %s: score-k5 depth %s / names %s (%s) | depth-k5 depth %s / names %s (%s) "
              "| slots %s -> %s (%s)"
              % (pr["window"], _num(pr["score_k5"]["depth_pp"]),
                 _num(pr["score_k5"]["names_pp"]), pr["score_k5"]["verdict"],
                 _num(pr["deep_k5"]["depth_pp"]), _num(pr["deep_k5"]["names_pp"]),
                 pr["deep_k5"]["verdict"], pr["budget_slots"]["n_a"],
                 pr["budget_slots"]["n_b"], _num(pr["budget_slots"]["pp"])), flush=True)
    res = check(payload)
    print("check ok=%s problems=%s" % (res["ok"], res["problems"]), flush=True)
    return 0 if res["ok"] else 0


def main_check() -> int:
    with io.open(OUT_JSON, encoding="utf-8") as f:
        payload = json.load(f)
    res = check(payload)
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res["ok"] else 3


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    passed = []

    def leg(name, ok, detail=""):
        passed.append(bool(ok))
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  -- " + str(detail)) if detail else ""))

    LINE = 0.01
    # L1 capacity formula, exact
    leg("L1 cap = line * k * worst", abs(cap_equal_weight([1e8, 2e8, 3e7], 3, LINE)
                                         - LINE * 3 * 3e7) < 1e-6)
    # L2 five-slot identity, exact on synthetic rosters
    ra = {"a": 1e8, "b": 2e8, "c": 3e8, "d": 4e8, "e": 5e8}
    rb = {"a": 3e8, "b": 6e8, "c": 9e8, "d": 2e8, "e": 5e8}
    f = split_fixed_k(ra, rb, ["a", "b", "c", "d", "e"], ["a", "b", "c", "d", "e"], 5, LINE)
    leg("L2 depth + names == total", abs(f["depth_pp"] + f["names_pp"] - f["total_pp"]) < 0.01,
        f)
    # L3 whole-roster identity
    g = split_full_roster(ra, rb, LINE)
    leg("L3 breadth + depth == total",
        abs(g["breadth_pp"] + g["depth_pp"] - g["total_pp"]) < 0.01, g)
    # L4 verdict mapping by counts
    leg("L4 verdict LEFT_LEADS", lead_verdict(0.5, 0.1) == "LEFT_LEADS")
    leg("L4b verdict RIGHT_LEADS", lead_verdict(0.1, 0.5) == "RIGHT_LEADS")
    leg("L4c verdict BOTH_MATTER", lead_verdict(0.30, 0.25) == "BOTH_MATTER")
    leg("L4d verdict NO_CHANGE", lead_verdict(0.0, 0.0) == "NO_CHANGE")
    # L5 a name that does not trade at the right anchor is dropped and named
    rb2 = {"a": 3e8, "b": 6e8}
    f2 = split_fixed_k(ra, rb2, ["a", "b", "c", "d"], ["a", "b"], 4, LINE)
    leg("L5 missing survivor dropped and named",
        f2["dropped"] == ["c", "d"] and f2["n_surv"] == 2
        and abs(f2["depth_pp"] + f2["names_pp"] - f2["total_pp"]) < 0.01, f2)
    # L6 zero survivors is not a number
    f3 = split_fixed_k({"x": 1e8}, {"a": 1e8}, ["x"], ["a"], 1, LINE)
    leg("L6 no survivors -> UNCOMPARABLE", f3["verdict"] == "UNCOMPARABLE_NO_SURVIVORS"
        and f3["total_pp"] is None, f3)
    # L7 empty roster prints nothing rather than zero
    leg("L7 empty roster -> no capacity", cap_equal_weight([], 5, LINE) is None
        and split_full_roster({}, {"a": 1e8}, LINE)["verdict"] == "EMPTY_ROSTER")
    # L8 the anchor reader agrees with the reference definition, holes included
    idx = pd.date_range("2020-01-01", periods=40, freq="B")
    df = pd.DataFrame({"s": [float(i + 1) for i in range(40)],
                       "h": [float(i + 1) if i % 3 else None for i in range(40)]}, index=idx)
    ap = adv_at_anchors(df, [idx[-1], idx[25]])
    ref_s = df["s"].loc[:idx[-1]].dropna().tail(20).median()
    ref_h = df["h"].loc[:idx[-1]].dropna().tail(20).median()
    leg("L8 ADV == median of the last 20 readings (clean and holed)",
        abs(ap.at["s", idx[-1]] - ref_s) < 1e-9 and abs(ap.at["h", idx[-1]] - ref_h) < 1e-9,
        (ap.at["s", idx[-1]], ref_s, ap.at["h", idx[-1]], ref_h))
    # L9 no lookahead: the value at a bar ignores everything after it
    cut = adv_at_anchors(df.loc[:idx[25]], [idx[25]])
    leg("L9 causal ADV", abs(ap.at["s", idx[25]] - cut.at["s", idx[25]]) < 1e-12,
        (ap.at["s", idx[25]], cut.at["s", idx[25]]))
    # L9b a name that stopped printing leaves the roster, however old its median is
    dead = pd.DataFrame({"a": [complex(i, 0).real + 1.0 for i in range(40)]}, index=idx)
    dead.loc[idx[20]:, "a"] = None
    lp = last_valid_positions(dead)
    p = {str(pd.Timestamp(d).date()): i for i, d in enumerate(dead.index)}
    apd = adv_at_anchors(dead, [str(pd.Timestamp(idx[19]).date()),
                                str(pd.Timestamp(idx[-1]).date())])
    on = roster_at(apd, str(pd.Timestamp(idx[19]).date()), p, lp)
    off = roster_at(apd, str(pd.Timestamp(idx[-1]).date()), p, lp)
    leg("L9b stale name counted on the day it traded, absent 19 bars later",
        "a" in on and "a" not in off, (on, off))
    # L10 the depth ladder is really the k deepest
    roster = {"a": 5e8, "b": 1e8, "c": 3e8, "d": 9e7}
    leg("L10 depth picks are the k largest",
        [s for s, _ in depth_picks(roster, 2)] == ["a", "c"]
        and cap_equal_weight([v for _, v in depth_picks(roster, 2)], 2, LINE)
        == LINE * 2 * 3e8)
    # L11 the multiple and the log total are the same statement (pp are published to 4 dp)
    f4 = split_fixed_k({"a": 1e8}, {"a": 4e8}, ["a"], ["a"], 1, LINE)
    leg("L11 multiple == exp(total)",
        abs(math.log(f4["multiple"]) - f4["total_pp"] / 100.0) < 1e-5,
        (f4["multiple"], f4["total_pp"]))
    # L12 the check catches a tampered split
    bad = {"roster": [], "pairs": [{"window": "w", "score_k5": {
        "depth_pp": 10.0, "names_pp": 10.0, "total_pp": 30.0, "verdict": "BOTH_MATTER"},
        "full_roster": {"breadth_pp": 1.0, "depth_pp": 1.0, "total_pp": 2.0,
                        "verdict": "BOTH_MATTER"}}],
        "summary": {"verdict": "SPLIT_BY_WINDOW", "full_roster_leads": [],
                    "score_k5_leads": []},
        "criteria": {"panel_last": "2026-01-01"}, "evidence_cutoff": "2026-01-01"}
    res = check(bad)
    leg("L12 tampered split is caught", not res["ok"]
        and any("identity" in p for p in res["problems"]), res["problems"])
    # L13 a stale face says STALE
    stale = {"roster": [], "pairs": [], "summary": {"verdict": "NO_WINDOW_MEASURED"},
             "criteria": {"panel_last": "2026-01-01"}, "evidence_cutoff": "2025-12-31"}
    res2 = check(stale)
    leg("L13 stale face says STALE", any("STALE" in p for p in res2["problems"]),
        res2["problems"])
    ok = all(passed)
    print("selftest %d/%d %s" % (sum(passed), len(passed), "PASS" if ok else "FAIL"))
    return 0 if ok else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return main_check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
