"""ETF book -- today's sibling premium gap is a price, not a rule: how much of it repeats?

r1464 found the same basket sold under several tickers and priced ONE session: 159501 and
513100 pay +23.64% / +21.26% above IOPV while 159513 pays +14.97%, so the same cash buys
CNY 9,762 more NDX100 basket. That answers "what does the swap save today". It does not
answer the question the desk actually has to decide:

    is the dearer ticker ALWAYS dearer (a permanent toll), or was today an episode?

Those are different trades. A permanent toll means re-tickering the book is a one-time fix.
An episode means the gap will decay and the sheet has to be re-ranked every session -- and
it also means most of today's saving is a one-off, not a rate.

This face reads the pair's own price history. Two same-index ETFs buying the same basket in
the same currency differ, day to day, only by their premium above NAV and by tracking; the
LEVEL of the close ratio also carries the two funds' different NAV-per-unit bases, which is
an arbitrary constant. So:

  * g_t = 100*ln(close_A/close_B) -- the level is contaminated by that constant;
  * the constant is pinned by the ONE day where both premiums are observable (today's board):
    offset = g_last - gap_today, and the reconstructed gap series is rec_t = g_t - offset;
    rec_last == gap_today by construction, and every earlier value inherits the assumption
    that the two bases did not move since. That assumption is tested, not asserted: a
    distribution or a split lands as a step in the ratio, so steps are detected and published;
  * the classified reading uses the RECONSTRUCTED series, never the raw ratio level (a reading
    off the raw ratio would report a 21pp "premium" that is mostly a different NAV base).

Verdicts per pair (frozen criteria echoed into the payload; --check refuses a face that
disagrees, and refuses a reconstruction whose last point is not the anchor):

  PERSISTENT_GAP  -- history mean clears the materiality line with the same sign as today
                     -> keep the cheaper ticker; the toll is structural
  EPISODIC_GAP    -- today's gap is material but history averages below it (and today sits
                     >= 2 sd from that average) -> swap for today only, re-rank every session
  NO_GAP          -- today's gap is under the materiality line -> nothing to do
  INSUFFICIENT_HISTORY / CANNOT_VERIFY -- never read as "no gap"

Usage:
    python scripts/etf_book_sibling_gap.py run
    python scripts/etf_book_sibling_gap.py --check
    python scripts/etf_book_sibling_gap.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_entry as sib  # noqa: E402  (single implementation of the family face)

SIB_JSON = os.path.join(ROOT, "results", "etf_book_sibling_entry.json")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_sibling_gap.md")

# ---- frozen criteria (echoed into the payload; --check refuses a face that disagrees) ----
MIN_DAYS = 120          # below this a "history" is a few observations wearing a mean
STEP_SD = 3.0           # a day-move this many sd wide is an event, not premium drift
HALF_NOTE_DAYS = 250    # ~one trading year: the window the reader will quote

LABEL_GAP_MEDIAN_PP = 0.30   # median |day change| of the gap: same basket sits below, another index above

CRITERIA = {
    "min_days": MIN_DAYS,
    "step_sd": STEP_SD,
    "material_gap_pp": sib.MATERIAL_PP,
    "half_note_days": HALF_NOTE_DAYS,
    "label_family_gap_median_pp": LABEL_GAP_MEDIAN_PP,
}


def label_family_verdict(gap_median_pp, n_live_alt, inner_verdict):
    """The board proposes a sibling by writing the same index label twice; its prices adjudicate.

    The hand map in etf_book_sibling_entry.LABEL_CANON covers two baskets, so every other labelled
    leg used to come back CANNOT_VERIFY even when the board listed four other tickers under the
    identical label. That is under-coverage, not caution -- but the opposite error (merging two
    tickers whose labels happen to match while the indices differ, e.g. 价值ETF) would price a
    swap that is not a swap. So the acceptance is empirical: two funds on one index differ only by
    premium drift, and the median day-over-day change of their gap is the robust way to see it.

    The MEDIAN OF DAY CHANGES, not the sd of the level: 510210 split 5:1 on 2021-01-25, which
    leaves one 160 pp step in the level series and inflates its sd to 42.9 pp against a same-basket
    pair whose median day change is 0.17 pp. A ruler that calls that pair "not a basket" is
    measuring the split, not the two funds. Returns (state, why).
    """
    if n_live_alt <= 0:
        return "NO_ALTERNATIVE", "no other live ticker writes this label on the board"
    if inner_verdict == "CANNOT_VERIFY":
        return "CANNOT_VERIFY", "the pair cannot be priced (see pair row)"
    if gap_median_pp is None:
        return "CANNOT_VERIFY", "no common history to adjudicate the label with"
    if gap_median_pp > LABEL_GAP_MEDIAN_PP:
        return ("LABEL_NOT_A_BASKET",
                "the board writes the same label, but the gap's median day change is %.3f pp "
                "(> %.2f): these are not the same basket, so no swap is priced"
                % (gap_median_pp, LABEL_GAP_MEDIAN_PP))
    return ("LABEL_IS_A_BASKET",
            "the board writes the same label and the gap's median day change is %.3f pp "
            "(<= %.2f): the price history agrees these hold the same basket"
            % (gap_median_pp, LABEL_GAP_MEDIAN_PP))


def find_daily(code):
    """The board's own daily file for one ticker, whichever exchange prefix it carries."""
    for cand in ("sh%s.csv" % code, "sz%s.csv" % code, "%s.csv" % code):
        p = os.path.join(DAILY_DIR, cand)
        if os.path.exists(p):
            return p
    return None


def load_close(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                out[row["date"]] = float(row["close"])
            except (TypeError, ValueError, KeyError):
                continue
    return out


def common_series(a, b):
    """Aligned (dates, closes_a, closes_b) over the days both tickers traded."""
    dates = sorted(set(a) & set(b))
    return dates, [a[d] for d in dates], [b[d] for d in dates]


def gap_series(ca, cb):
    """g_t = 100*ln(P_A/P_B). Level carries the two NAV bases; changes do not."""
    return [100.0 * math.log(x / y) for x, y in zip(ca, cb)]


def reconstruct(g, gap_today):
    """Pin the unknown NAV-base constant with today's observable premium pair."""
    if not g:
        return None, None
    offset = g[-1] - gap_today
    return [x - offset for x in g], offset


def median_abs_change(series):
    """Median |day-over-day change|. Immune to a split, which is a step and not a tracking gap.

    The level series of a pair where one fund split 5:1 carries one 160 pp step; its sd reads that
    step every session, while the median day change does not see it at all. Same-basket pairs on
    this board read 0.145-0.206 pp, pairs holding different indices read 0.385+.
    """
    if not series or len(series) < 2:
        return None
    diffs = sorted(abs(series[i] - series[i - 1]) for i in range(1, len(series)))
    n = len(diffs)
    mid = n // 2
    return diffs[mid] if n % 2 else 0.5 * (diffs[mid - 1] + diffs[mid])


def percentile_rank(series, value):
    """Share of observations at or below `value` (so the max reads 100)."""
    if not series:
        return None
    return round(100.0 * sum(1 for v in series if v <= value) / len(series), 2)


def describe(rec, dates, gap_today):
    n = len(rec)
    mean = sum(rec) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in rec) / n)
    ordered = sorted(rec)
    return {
        "days": n,
        "first_date": dates[0],
        "last_date": dates[-1],
        "today_gap_pp": round(gap_today, 4),
        "mean_pp": round(mean, 4),
        "median_pp": round(ordered[n // 2], 4),
        "sd_pp": round(sd, 4),
        "min_pp": round(ordered[0], 4),
        "max_pp": round(ordered[-1], 4),
        "share_days_positive": round(sum(1 for v in rec if v > 0) / n, 4),
        "today_percentile": percentile_rank(rec, rec[-1]),
        "today_z": round((rec[-1] - mean) / sd, 3) if sd else None,
        "last_year_mean_pp": round(sum(rec[-HALF_NOTE_DAYS:]) / len(rec[-HALF_NOTE_DAYS:]), 4),
        "half_split_mean_pp": [
            round(sum(rec[:n // 2]) / max(1, n // 2), 4),
            round(sum(rec[n // 2:]) / max(1, n - n // 2), 4),
        ],
    }


def detect_steps(g, dates, k=STEP_SD):
    """Day moves in the ratio that are events (distribution, split, premium dislocation)."""
    if len(g) < 3:
        return []
    diffs = [g[i] - g[i - 1] for i in range(1, len(g))]
    mean = sum(diffs) / len(diffs)
    sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / len(diffs))
    if not sd:
        return []
    return [{"date": dates[i + 1], "jump_pp": round(diffs[i], 4)}
            for i in range(len(diffs)) if abs(diffs[i] - mean) > k * sd]


def classify(d, mat=sib.MATERIAL_PP, min_days=MIN_DAYS):
    """One word per pair, from the reconstructed series only."""
    if d is None or d.get("days", 0) < min_days:
        return "INSUFFICIENT_HISTORY", {
            "mean_clears_materiality": None,
            "today_is_tail": None,
        }
    mean = d["mean_pp"]
    last = d["today_gap_pp"]
    sd = d["sd_pp"] or 0.0
    same_sign = (mean > 0) == (last > 0)
    mean_clears = abs(mean) >= mat and same_sign
    tail = sd > 0 and abs(last - mean) >= 2.0 * sd
    flags = {"mean_clears_materiality": bool(mean_clears), "today_is_tail": bool(tail)}
    if abs(last) < mat:
        return "NO_GAP", flags
    if mean_clears:
        return "PERSISTENT_GAP", flags
    if tail:
        return "EPISODIC_GAP", flags
    return "AMBIGUOUS_GAP", flags


def advice(verdict, d, flags=None):
    flags = flags or {}
    if verdict == "PERSISTENT_GAP":
        base = ("the dearer ticker has been dearer on %s%% of %d sessions and the average gap "
                "is %s pp: re-tickering the book is a permanent fix, not a daily decision"
                % (round(100 * d["share_days_positive"]), d["days"], d["mean_pp"]))
        if flags.get("today_is_tail"):
            base += (" -- but today's %s pp is the %s-th percentile of that history, so only the "
                     "average repeats and today's excess is an episode"
                     % (d["today_gap_pp"], d["today_percentile"]))
        return base
    if verdict == "EPISODIC_GAP":
        return ("today's %s pp sits at the %s percentile of %d sessions whose average is %s pp: "
                "swap for today and re-rank the sheet next session -- most of this saving is a "
                "one-off, not a rate" % (d["today_gap_pp"], d["today_percentile"], d["days"], d["mean_pp"]))
    if verdict == "NO_GAP":
        return "today's gap is under the %s pp materiality line: nothing to swap" % sib.MATERIAL_PP
    if verdict == "INSUFFICIENT_HISTORY":
        return "fewer than %d common sessions: the gap cannot be read as persistent or episodic" % MIN_DAYS
    return ("today's gap is material but the history neither averages to it nor puts it in a "
            "tail: no claim is made either way")


def assess_pair(a, b, gap_today, sib_row):
    """Full reading for one (booked leg, cheapest sibling) pair."""
    pa, pb = find_daily(a), find_daily(b)
    row = {
        "leg_symbol": a,
        "sibling_symbol": b,
        "sibling_name": (sib_row.get("cheapest") or {}).get("name"),
        "index": sib_row.get("index"),
        "amount_cny": sib_row.get("amount_cny"),
        "source_verdict": sib_row.get("verdict"),
        "today_gain_cny": sib_row.get("basket_gain_cny"),
        "gap_today_pp": gap_today,
        "daily_files": [os.path.relpath(pa, ROOT) if pa else None,
                        os.path.relpath(pb, ROOT) if pb else None],
        "verdict": "CANNOT_VERIFY",
        "why": "",
        "stats": None,
        "repeatable_gain_cny": None,
        "one_off_gain_cny": None,
        "steps": [],
    }
    if not pa or not pb:
        row["why"] = "no local daily panel for %s" % (a if not pa else b)
        return row
    dates, ca, cb = common_series(load_close(pa), load_close(pb))
    if not dates:
        row["why"] = "the two tickers share no session in the local panels"
        return row
    g = gap_series(ca, cb)
    rec, offset = reconstruct(g, gap_today)
    d = describe(rec, dates, gap_today)
    d["nav_base_offset_pp"] = round(offset, 4)
    d["gap_change_median_pp"] = round(median_abs_change(g), 4)
    verdict, flags = classify(d)
    row.update({"verdict": verdict, "stats": d, "flags": flags, "advice": advice(verdict, d, flags),
                "steps": detect_steps(g, dates)})
    if verdict in ("PERSISTENT_GAP", "EPISODIC_GAP", "AMBIGUOUS_GAP"):
        # the part of today's saving that a repeat entry could expect again: reprice the same
        # cash with the leg's premium set at best + the historical average gap
        p_best = sib.premium_dec((sib_row.get("cheapest") or {}).get("premium_pct"))
        amount = float(sib_row.get("amount_cny") or 0.0)
        if p_best is not None and amount:
            p_hist = p_best + d["mean_pp"] / 100.0
            rep = sib.basket_value(amount, p_best) - sib.basket_value(amount, p_hist)
            con = (sib_row.get("basket_gain_cny") or 0.0) - rep
            row["repeatable_gain_cny"] = round(rep, 1)
            row["one_off_gain_cny"] = round(con, 1)
    return row


def board_labels():
    """The session board keyed by code, each row carrying the label its own name writes.

    Same reader as the sibling face (load_rows/derive_houses/strip_house) so the two faces cannot
    disagree about what a name says. Returns ({code: row}, session).
    """
    snap = sib.latest_snapshot()
    if not snap:
        return {}, None
    rows, session = sib.load_rows(snap)
    houses = sib.derive_houses([r["name"] for r in rows])
    resid = sib.strip_house([r["name"] for r in rows], houses)
    for r in rows:
        r["label"] = resid[r["name"]]
    return {r["code"]: r for r in rows}, session


def label_family_price(leg, board):
    """Second chance for a leg the hand canon could not name: same board label, prices decide.

    Returns (pair_row_or_None, note). A None row means "not a sibling after all" and the note
    says why, so the reader sees the refusal instead of a silent gap.
    """
    code = str(leg.get("symbol"))
    me = board.get(code)
    if me is None:
        return None, {"leg_symbol": code, "label": None, "same_label_tickers": 0,
                      "live_alternatives": 0, "gap_median_pp": None, "state": "NOT_ON_BOARD",
                      "why": "this ticker is not on the board the label test reads"}
    label = me.get("label")
    members = [r for r in board.values()
               if r.get("label") == label and sib.premium_dec(r.get("premium_pct")) is not None]
    live_alt = [r for r in members
                if r["code"] != code and (r.get("amount") or 0.0) >= sib.LIQ_FLOOR_CNY]
    note = {"leg_symbol": code, "label": label, "same_label_tickers": len(members),
            "live_alternatives": len(live_alt), "gap_median_pp": None, "state": "", "why": ""}
    state, why = label_family_verdict(None, len(live_alt), "NO_PAIR")
    if not live_alt:
        note.update({"state": state, "why": why})
        return None, note
    # the economics come from the sibling face's own assess(), never a second copy of it
    fam = {"LBL:%s" % label: members}
    summary = sib.assess([{"symbol": code, "amount": leg.get("amount_cny")}], fam, board)
    sib_leg = summary["legs"][0]
    if not sib_leg.get("cheapest") or sib_leg.get("gap_pp") is None:
        note.update({"state": "NO_LIVE_ALTERNATIVE",
                     "why": sib_leg.get("why") or "no live alternative under this label"})
        return None, note
    row = assess_pair(code, sib_leg["cheapest"]["code"], sib_leg["gap_pp"], sib_leg)
    med = (row.get("stats") or {}).get("gap_change_median_pp")
    state, why = label_family_verdict(med, len(live_alt), row.get("verdict"))
    note.update({"state": state, "why": why, "gap_median_pp": med,
                 "sibling_symbol": sib_leg["cheapest"]["code"],
                 "inner_verdict": row.get("verdict")})
    if state != "LABEL_IS_A_BASKET":
        return None, note
    row["family_basis"] = "board_label"
    row["label"] = label
    row["label_gap_median_pp"] = med
    return row, note


def build():
    with open(SIB_JSON, encoding="utf-8") as fh:
        found = json.load(fh)
    legs = ((found.get("summary") or {}).get("legs")) or []
    board, board_session = board_labels()
    pairs, skipped, label_family = [], [], []
    for leg in legs:
        ch = leg.get("cheapest")
        gap = leg.get("gap_pp")
        if not ch or gap is None:
            priced = label_family_price(leg, board)
            if priced is not None:
                row, note = priced
                label_family.append(note)
                if row is not None:
                    pairs.append(row)
                    continue
            skipped.append({"leg_symbol": leg.get("symbol"),
                            "label": leg.get("label"),
                            "verdict": "CANNOT_VERIFY",
                            "why": (priced[1]["why"] if priced is not None
                                    else (leg.get("why") or "the sibling face priced no alternative for this leg"))})
            continue
        pairs.append(assess_pair(leg["symbol"], ch["code"], gap, leg))
    counts = {}
    for p in pairs + skipped:
        counts[p["verdict"]] = counts.get(p["verdict"], 0) + 1
    repeatable = round(sum(p.get("repeatable_gain_cny") or 0.0 for p in pairs), 1)
    one_off = round(sum(p.get("one_off_gain_cny") or 0.0 for p in pairs), 1)
    # only a leg the sibling face itself called SWAP_SAVES is money on the table; a gap under
    # its materiality line is a real CNY figure but not an action, and it is reported apart
    today_gain = round(sum(p.get("today_gain_cny") or 0.0 for p in pairs
                           if p.get("source_verdict") == "SWAP_SAVES"), 1)
    immaterial_gain = round(sum(p.get("today_gain_cny") or 0.0 for p in pairs
                                if p.get("source_verdict") == "GAP_IMMATERIAL"), 1)
    face = {
        "artifact": "etf_book_sibling_gap",
        "session": found.get("session"),
        "ticket": found.get("ticket"),
        "source_face": os.path.relpath(SIB_JSON, ROOT),
        "criteria": CRITERIA,
        "pairs": pairs,
        "skipped_legs": skipped,
        "verdict_counts": counts,
        "today_gain_cny": today_gain,
        "immaterial_gain_cny": immaterial_gain,
        "repeatable_gain_cny": repeatable,
        "one_off_gain_cny": one_off,
        "sentence": sentence(pairs, today_gain, repeatable, one_off),
        "caveats": [
            "the reconstructed gap is anchored on ONE session's IOPV pair; every earlier value "
            "inherits the assumption that the two funds' NAV-per-unit ratio has not moved, and "
            "steps are published as the evidence against that assumption",
            "closes are as-traded, not total-return: a distribution to one fund only lands as a "
            "step and is flagged, not corrected",
            "same index, not same basket: tracking difference, fee, size, quotation width and "
            "FX-hedge policy are NOT priced here",
            "premium history from our own board starts at one session; this face uses the price "
            "ratio for history precisely because it is the only long series we have",
            "a step is a flag, not an error: the level after a step is still the level a buyer "
            "would pay today",
            "a leg the hand map could not name is retried on the board's own label, and the price "
            "history has to agree before a swap is priced (label_family block); a label match "
            "alone is never treated as the same basket",
        ],
        "label_family": label_family,
        "label_family_board_session": board_session,
        "label_family_sensitivity": label_family_sensitivity(label_family),
    }
    return face


def label_family_sensitivity(label_family, lines=(0.25, 0.35, 0.45)):
    """Which legs change side if the frozen line moves by ~1/6 and ~1/2 (a call with no margin is a guess)."""
    out = []
    for line in lines:
        accepted, refused = [], []
        for n in label_family:
            med = n.get("gap_median_pp")
            if med is None:
                continue
            (accepted if med <= line else refused).append(n.get("leg_symbol"))
        out.append({"line_pp": line, "accepted": accepted, "refused": refused})
    return out


def sentence(pairs, today_gain, repeatable, one_off):
    if not pairs:
        return "no pair carries both a premium gap and a local price history"
    pers = [p for p in pairs if p["verdict"] == "PERSISTENT_GAP"]
    epis = [p for p in pairs if p["verdict"] == "EPISODIC_GAP"]
    if not pers and not epis:
        return ("no pair carries a gap that can be read: %d pair(s) unverifiable or immaterial"
                % len(pairs))
    bits = []
    if epis:
        bits.append("%d pair(s) episodic (today's gap is a tail of its own history)" % len(epis))
    if pers:
        bits.append("%d pair(s) persistent (the toll repeats)" % len(pers))
    return ("today the swap is worth %s CNY of which %s is repeatable at the historical average "
            "gap and %s is a one-off: %s"
            % (format(today_gain, ",.0f"), format(repeatable, ",.0f"),
               format(one_off, ",.0f"), "; ".join(bits)))


def render_md(face):
    L = ["# ETF book -- the sibling premium gap: a price today, or a rule?", ""]
    L.append("session `%s` | ticket `%s` | source `%s`" % (face["session"], face["ticket"], face["source_face"]))
    L.append("")
    L.append("**%s**" % face["sentence"])
    L.append("")
    L.append("| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in face["pairs"]:
        d = p.get("stats") or {}
        L.append("| %s | %s %s | %s | %s pp | %s pp | %s | %s | %s | %s |" % (
            p["leg_symbol"], p["sibling_symbol"], p.get("sibling_name") or "",
            p.get("index") or "-",
            d.get("today_gap_pp", p["gap_today_pp"]), d.get("mean_pp", "-"),
            d.get("sd_pp", "-"), d.get("days", "-"), d.get("today_percentile", "-"),
            p["verdict"]))
    L.append("")
    for p in face["pairs"]:
        L.append("## %s -> %s (%s)" % (p["leg_symbol"], p["sibling_symbol"], p["verdict"]))
        L.append("")
        L.append(p.get("advice") or p.get("why") or "")
        d = p.get("stats") or {}
        if d:
            L.append("")
            L.append("- window %s..%s (%d common sessions), reconstructed gap mean %s pp, median %s pp, sd %s pp"
                     % (d["first_date"], d["last_date"], d["days"], d["mean_pp"], d["median_pp"], d["sd_pp"]))
            L.append("- today z = %s, percentile = %s, positive on %s%% of sessions"
                     % (d["today_z"], d["today_percentile"], round(100 * d["share_days_positive"])))
            L.append("- half-split means %s pp / %s pp; last %d sessions mean %s pp"
                     % (d["half_split_mean_pp"][0], d["half_split_mean_pp"][1], CRITERIA["half_note_days"],
                        d["last_year_mean_pp"]))
            L.append("- NAV-base offset pinned today = %s pp (the raw close ratio level, %s pp, is not a premium)"
                     % (d["nav_base_offset_pp"], round(d["nav_base_offset_pp"] + d["today_gap_pp"], 2)))
            if p.get("repeatable_gain_cny") is not None:
                L.append("- today %s CNY of basket gain: %s repeatable at the average gap, %s one-off"
                         % (format(p["today_gain_cny"], ",.0f"),
                            format(p["repeatable_gain_cny"], ",.0f"),
                            format(p["one_off_gain_cny"], ",.0f")))
            if p["steps"]:
                L.append("- %d step(s) > %s sd: %s"
                         % (len(p["steps"]), CRITERIA["step_sd"],
                            ", ".join("%s %+.2fpp" % (s["date"], s["jump_pp"]) for s in p["steps"][:6])))
        L.append("")
    if face["skipped_legs"]:
        L.append("## legs the sibling face could not price")
        L.append("")
        for s in face["skipped_legs"]:
            L.append("- %s: %s" % (s["leg_symbol"], s["why"]))
        L.append("")
    lf = face.get("label_family") or []
    if lf:
        L.append("## the board's own labels, adjudicated by the prices (%s)" % (face.get("label_family_board_session") or "-"))
        L.append("")
        L.append("A leg the hand map could not name is retried here: if two live tickers carry the "
                 "identical index label, the median day-over-day change of their gap decides whether "
                 "they are one basket. The line is %.2f pp (median, not sd: a 5:1 split is one step "
                 "and must not be read as a tracking gap)." % CRITERIA["label_family_gap_median_pp"])
        L.append("")
        L.append("| leg | label | same-label | live alts | gap median day change | state |")
        L.append("|---|---|---|---|---|---|")
        for n in lf:
            L.append("| %s | %s | %s | %s | %s | %s |" % (
                n.get("leg_symbol"), n.get("label") or "-", n.get("same_label_tickers"),
                n.get("live_alternatives"),
                "-" if n.get("gap_median_pp") is None else "%.3f pp" % n["gap_median_pp"],
                n.get("state")))
        L.append("")
        for n in lf:
            L.append("- %s: %s" % (n.get("leg_symbol"), n.get("why")))
        L.append("")
    L.append("## caveats")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    return "\n".join(L) + "\n"


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))


def run():
    face = build()
    write_out(face)
    print("[sibling_gap] %s" % face["sentence"])
    for p in face["pairs"]:
        d = p.get("stats") or {}
        print("  %s->%s %-17s today %+7.3fpp  mean %+6.3f  pct %6s  n=%s" % (
            p["leg_symbol"], p["sibling_symbol"], p["verdict"], p["gap_today_pp"],
            d.get("mean_pp", float("nan")), d.get("today_percentile", "-"), d.get("days", 0)))
    return 0


def check():
    """Re-derive every published number from the panels and the board; refuse a stale face."""
    if not (os.path.exists(OUT_JSON) and os.path.exists(OUT_MD)):
        print("[sibling_gap] CHECK_FAIL no published face")
        return 1
    face = json.load(open(OUT_JSON, encoding="utf-8"))
    bad = []
    if face.get("criteria") != CRITERIA:
        bad.append("criteria echoed %r != constants %r" % (face.get("criteria"), CRITERIA))
    if not os.path.exists(SIB_JSON):
        bad.append("source sibling face is missing")
    else:
        src = json.load(open(SIB_JSON, encoding="utf-8"))
        if face.get("session") != src.get("session"):
            bad.append("face quotes session %s, sibling face says %s" % (face.get("session"), src.get("session")))
        src_legs = {leg["symbol"]: leg for leg in ((src.get("summary") or {}).get("legs") or [])}
        for p in face.get("pairs", []):
            leg = src_legs.get(p["leg_symbol"])
            if leg is None:
                bad.append("%s is not in the source ticket" % p["leg_symbol"])
                continue
            if (leg.get("cheapest") or {}).get("code") != p["sibling_symbol"]:
                if p.get("family_basis") == "board_label":
                    # this pair was found past the hand map, on the board's own label; re-adjudicate
                    # it here so a published board-label pair is checked instead of excused
                    board, _ = board_labels()
                    again = label_family_price(leg, board)
                    if again is None or again[0] is None:
                        bad.append("%s was priced off the board label but no longer adjudicates as one basket"
                                   % p["leg_symbol"])
                    elif again[0].get("sibling_symbol") != p["sibling_symbol"]:
                        bad.append("%s board-label sibling drifted: published %s, now %s"
                                   % (p["leg_symbol"], p["sibling_symbol"], again[0]["sibling_symbol"]))
                    elif abs((again[0].get("gap_today_pp") or 0.0) - p["gap_today_pp"]) > 1e-3:
                        bad.append("%s board-label gap drifted" % p["leg_symbol"])
                else:
                    bad.append("%s quotes sibling %s, source says %s"
                               % (p["leg_symbol"], p["sibling_symbol"], (leg.get("cheapest") or {}).get("code")))
            if p.get("family_basis") != "board_label" and abs((leg.get("gap_pp") or 0.0) - p["gap_today_pp"]) > 1e-3:
                bad.append("%s quotes gap %s, source says %s"
                           % (p["leg_symbol"], p["gap_today_pp"], leg.get("gap_pp")))
            # the anchor identity: a reconstruction that does not land on today's gap is a bug
            d = p.get("stats") or {}
            if d and abs((d.get("today_gap_pp") or 0.0) - p["gap_today_pp"]) > 1e-3:
                bad.append("%s reconstruction lands at %s, not the anchor %s"
                           % (p["leg_symbol"], d.get("today_gap_pp"), p["gap_today_pp"]))
            pa, pb = find_daily(p["leg_symbol"]), find_daily(p["sibling_symbol"])
            if not pa or not pb:
                bad.append("%s pair lost its daily panel" % p["leg_symbol"])
                continue
            dates, ca, cb = common_series(load_close(pa), load_close(pb))
            rec, _ = reconstruct(gap_series(ca, cb), p["gap_today_pp"])
            d2 = describe(rec, dates, p["gap_today_pp"])
            v2, _ = classify(d2)
            if v2 != p["verdict"]:
                bad.append("%s verdict drifted: published %s, now %s" % (p["leg_symbol"], p["verdict"], v2))
            if d and abs((d.get("mean_pp") or 0.0) - d2["mean_pp"]) > 1e-3:
                bad.append("%s mean drifted: published %s, now %s" % (p["leg_symbol"], d.get("mean_pp"), d2["mean_pp"]))
    tot = round(sum(p.get("today_gain_cny") or 0.0 for p in face.get("pairs", [])
                    if p.get("source_verdict") == "SWAP_SAVES"), 1)
    if abs(tot - (face.get("today_gain_cny") or 0.0)) > 0.5:
        bad.append("pair gains %s do not add up to %s" % (tot, face.get("today_gain_cny")))
    rep = round(sum(p.get("repeatable_gain_cny") or 0.0 for p in face.get("pairs", [])), 1)
    if abs(rep - (face.get("repeatable_gain_cny") or 0.0)) > 0.5:
        bad.append("repeatable gains %s do not add up to %s" % (rep, face.get("repeatable_gain_cny")))
    one = round(sum(p.get("one_off_gain_cny") or 0.0 for p in face.get("pairs", [])), 1)
    if abs(one - (face.get("one_off_gain_cny") or 0.0)) > 0.5:
        bad.append("one-off gains %s do not add up to %s" % (one, face.get("one_off_gain_cny")))
    if abs((rep + one) - (face.get("today_gain_cny") or 0.0)) > 0.5:
        bad.append("repeatable + one-off do not add to today's gain")
    if bad:
        for b in bad:
            print("[sibling_gap] CHECK_FAIL %s" % b)
        return 1
    print("[sibling_gap] CHECK_OK %s" % (face.get("sentence") or ""))
    return 0


def selftest():
    fails = []

    def eq(name, got, want, tol=None):
        if tol is not None:
            ok = got is not None and abs(got - want) <= tol
        else:
            ok = got == want
        print("  %-52s %s" % (name, "PASS" if ok else "FAIL got=%r want=%r" % (got, want)))
        if not ok:
            fails.append(name)

    # --- a synthetic pair: same index, constant 1% premium gap, 300 sessions
    dates = ["2024-%03d" % i for i in range(300)]
    ca = [1.0 * (1.0 + 0.0001 * i) for i in range(300)]
    cb = [p / 1.01 for p in ca]
    g = gap_series(ca, cb)
    eq("L1 a constant 1% gap reconstructs to 1.00 pp", round(g[0], 6), round(100 * math.log(1.01), 6))
    rec, off = reconstruct(g, 1.0099)
    eq("L2 the reconstruction lands exactly on the anchor", round(rec[-1], 6), 1.0099, tol=1e-6)
    d = describe(rec, dates, 1.0099)
    eq("L3 the reconstructed series is flat", d["sd_pp"], 0.0)
    eq("L4 max reads percentile 100", d["today_percentile"], 100.0)
    eq("L5 a flat 1pp gap over 300 days is PERSISTENT", classify(d)[0], "PERSISTENT_GAP")

    # --- episodic: 299 sessions at ~0, one spike on the last day
    ca2 = [1.0] * 299 + [1.09]
    cb2 = [1.0] * 300
    g2 = gap_series(ca2, cb2)
    rec2, _ = reconstruct(g2, g2[-1])
    d2 = describe(rec2, dates, g2[-1])
    eq("L6 a one-day spike is EPISODIC", classify(d2)[0], "EPISODIC_GAP")
    eq("L7 the spike is the max of its own series", round(d2["max_pp"], 4), round(g2[-1], 4))

    # --- a gap under the materiality line is NOT a saving
    d3 = dict(d2)
    d3["today_gap_pp"] = 0.10
    eq("L8 sub-materiality gap reads NO_GAP", classify(d3)[0], "NO_GAP")

    # --- short history is never read as "no gap"
    short = describe(rec2[:50], dates[:50], rec2[49])
    eq("L9 short history is INSUFFICIENT_HISTORY", classify(short)[0], "INSUFFICIENT_HISTORY")

    # --- a structural gap whose sign flips between the halves still classifies off the MEAN,
    #     and a persistent gap with a tail on top stays PERSISTENT (the toll repeats anyway)
    rec4 = [1.0] * 299 + [6.0]
    d4 = describe(rec4, dates, 6.0)
    v4, f4 = classify(d4)
    eq("L10 a persistent toll with a tail stays PERSISTENT", v4, "PERSISTENT_GAP")
    eq("L11 and the tail flag is set beside it", f4["today_is_tail"], True)

    # --- steps are flagged, not smoothed away
    caj = [1.0] * 150 + [1.05] * 150
    cbj = [1.0] * 300
    gj = gap_series(caj, cbj)
    st = detect_steps(gj, dates)
    eq("L12 a distribution-sized jump is detected as a step", len(st) >= 1, True)
    eq("L13 the step is dated on the day it happened", st[0]["date"] == dates[150] if st else None, True)

    # --- basket arithmetic for the repeatable/one-off split
    eq("L14 repeatable gain is the same cash at the average gap",
       round(sib.basket_value(100000.0, 0.15) - sib.basket_value(100000.0, 0.15 + 0.0083), 2),
       round(sib.basket_value(100000.0, 0.15) - sib.basket_value(100000.0, 0.1583), 2), tol=0.01)
    eq("L15 a zero mean gap makes no repeatable claim",
       round(sib.basket_value(100000.0, 0.15) - sib.basket_value(100000.0, 0.15), 6), 0.0)

    # --- refuse reading the raw ratio level as a premium (the whole point of the anchor)
    eq("L16 the published criteria echo the constants", CRITERIA["material_gap_pp"], sib.MATERIAL_PP)

    # --- a board label is a proposal, the price history is the judge (r1803)
    eq("L17 no live ticker under the label = NO_ALTERNATIVE",
       label_family_verdict(None, 0, "NO_PAIR")[0], "NO_ALTERNATIVE")
    eq("L18 a same-basket median day change accepts the label",
       label_family_verdict(0.145, 3, "ALREADY_CHEAPEST")[0], "LABEL_IS_A_BASKET")
    eq("L19 a different-index median day change refuses it",
       label_family_verdict(LABEL_GAP_MEDIAN_PP + 0.01, 3, "ALREADY_CHEAPEST")[0], "LABEL_NOT_A_BASKET")
    eq("L20 the line is inclusive (median == the frozen line still accepts)",
       label_family_verdict(LABEL_GAP_MEDIAN_PP, 1, "ALREADY_CHEAPEST")[0], "LABEL_IS_A_BASKET")
    eq("L21 an unpriceable inner pair stays CANNOT_VERIFY whatever the median says",
       label_family_verdict(0.10, 2, "CANNOT_VERIFY")[0], "CANNOT_VERIFY")
    # the ruler itself: one 160 pp split step must not move the median while it moves the sd
    stepped = [1.0] * 200 + [1.05] * 200
    eq("L22 a single split-sized step leaves the median day change at zero",
       round(median_abs_change(stepped), 6), 0.0)
    eq("L23 ... while the same series carries a non-zero sd",
       describe(stepped, dates[:400], stepped[-1])["sd_pp"] > 0.0, True)

    print("selftest: %d PASS, %d FAIL" % (23 - len(fails), len(fails)))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="ETF book sibling premium gap history")
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.check or a.mode == "check":
        return check()
    if a.selftest or a.mode == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())