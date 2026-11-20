"""ETF book -- the capacity line has an era, and the book's own numbers moved with it.

r1850's capacity face answers three questions about ONE ruler read on THIRTY sessions
(how far past the line, which day, how coarse). r1870 then showed that the admission
verdict barely moves when the start year moves, and left one blind spot on the record:
K1 is read on today's picks against today's ADV, so it cannot say anything about what
1,000,000 CNY would have meant in 2015.

This face prices the same trade in every year the panel has:

  * WHAT THE BOOK WAS. On the first bar of each year, take the five names the book's own
    score row ranked highest USING ONLY DATA UP TO THAT BAR (no lookahead), and read the
    1% of ADV line against that year's own ADV.
  * WHAT IT COULD CARRY. The capital that exactly fills the weakest of those five slots
    at the line, in CNY -- and whether the published lens (1,000,000) sat above or below
    it that year.
  * WHEN IT BECAME BUYABLE. Named from counts: the first measured year whose own line
    admits the lens. That is a statement about the market the book trades, not about the
    book: the same five-slot trade was a different size in 2015.

Nothing here re-decides the gate. The line, the capital lens, the picks recipe and the
ADV reading are imported from `etf_book_year_gate` / `etf_book_phase_admission` /
`etf_book_capacity_edge`; the leg refuses to publish if its own reproduction of the
published reading drifts.

Read the verdict as a statement about the ruler's era, not about today: EVERY_YEAR_ABOVE
means the lens would have fitted in every measured year (a capacity fact about the whole
window); LINE_CROSSED_INSIDE names the year the market grew past the lens, which is the
only year in which "DENY" turns into "ADMIT" with the book unchanged.

Usage:
    python scripts/etf_book_era_capacity.py run
    python scripts/etf_book_era_capacity.py check
    python scripts/etf_book_era_capacity.py selftest
"""

from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_book_capacity_edge as CE  # noqa: E402
import etf_book_era_grid as EG  # noqa: E402
import etf_book_phase_admission as PA  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_era_capacity.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_era_capacity.md")

SLOTS = 5                     # the gate's five-name lens (imported recipe, same n)
REPRO_TOL_PCT = 0.02          # gate publishes impact_pct_of_adv to 3 dp of a percent
GATE_FACE = PA.GATE


# ---------------------------------------------------------------- inputs

def load_gate(path=GATE_FACE):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def rulers(face=None):
    """The line and the lens, read off the gate's own published decision block."""
    face = load_gate() if face is None else face
    reads = ((face.get("decision") or {}).get("reads") or {})
    lens_key = reads.get("capacity_veto_lens") or "1M"
    blk = ((reads.get("capacity_by_capital") or {}).get(lens_key) or {})
    line_pct = reads.get("impact_max_pct_of_adv")
    return {"lens": lens_key,
            "lens_cny": blk.get("capital_cny"),
            "line_pct": line_pct,
            "line_frac": (None if line_pct is None else float(line_pct) / 100.0),
            "published_reading_pct": blk.get("impact_pct_of_adv"),
            "published_within": blk.get("within_1pct"),
            "panel_last": (face.get("data") or {}).get("last")}


def score_row_at(sc, d):
    """The score row the book would have read on `d`: last row at or before it."""
    sub = sc.loc[:d]
    if len(sub) == 0:
        return None
    return sub.iloc[-1]


def picks_at(sc, d, n=SLOTS):
    """Causal top-n: only bars up to `d` are visible to this call."""
    row = score_row_at(sc, d)
    if row is None:
        return None
    row = row.dropna()
    if row.empty:
        return None
    return list(row.nlargest(n).index)


# ---------------------------------------------------------------- measurement

def measure_year(sc, amt, year_row, line_frac, lens_cny, n=SLOTS):
    """One year priced: picks as of its first bar, ADV as of the same bar."""
    d = pd.Timestamp(year_row["first_bar"])
    picks = picks_at(sc, d, n)
    out = {"year": year_row["year"], "anchor_requested": year_row["label"],
           "anchor": year_row["first_bar"], "picks": picks or [],
           "n_names": len(picks or [])}
    if not picks:
        out.update({"reading_pct": None, "capital_where_at_line_cny": None,
                    "binding": None, "unmeasurable": [], "admit_at_lens": None,
                    "why": "score panel has no readable row at or before this bar"})
        return out
    adv_map = {sym: CE.adv20_at(amt, sym, d) for sym in picks}
    m = CE.measure(picks, lens_cny, line_frac, adv_map)
    read = m["reading"]
    cap = m.get("capital_where_at_line_cny")
    out.update({
        "n_measured": m["n_names"] - len(m["unmeasurable"]),
        "unmeasurable": m["unmeasurable"],
        "reading_pct": (None if read is None else round(read * 100.0, 4)),
        "capital_where_at_line_cny": cap,
        "per_name_at_line_cny": (None if cap is None else round(cap / float(m["n_names"]), 2)),
        "binding": m["binding"],
        "admit_at_lens": (None if read is None else bool(read <= line_frac)),
        "adv_by_name": {r["sym"]: r["adv"] for r in m["rows"]},
    })
    if read is None:
        out["why"] = "no slot had a readable 20-bar ADV at this bar"
    return out


def era_block(rows, eras=None):
    """Group the year rows into eras and price each era on its own members."""
    eras = EG.ERAS if eras is None else eras
    out = []
    for name, lo, hi in eras:
        members = [r for r in rows if lo <= r["year"] <= hi]
        meas = [r for r in members if r.get("reading_pct") is not None]
        reads = [r["reading_pct"] for r in meas]
        caps = [r["capital_where_at_line_cny"] for r in meas
                if r.get("capital_where_at_line_cny") is not None]
        out.append({
            "era": name,
            "years": [r["year"] for r in members],
            "n_years": len(members),
            "n_measured": len(meas),
            "n_admit": sum(1 for r in meas if r["admit_at_lens"]),
            "reading_pct_min": round(min(reads), 4) if reads else None,
            "reading_pct_median": round(statistics.median(reads), 4) if reads else None,
            "reading_pct_max": round(max(reads), 4) if reads else None,
            "capacity_min_cny": min(caps) if caps else None,
            "capacity_median_cny": round(statistics.median(caps), 2) if caps else None,
            "capacity_max_cny": max(caps) if caps else None,
        })
    return out


def first_admit_year(rows):
    """The earliest measured year whose own line admits the lens (None if never)."""
    for r in rows:
        if r.get("admit_at_lens"):
            return r["year"]
    return None


def last_refuse_year(rows):
    """The last measured year whose own line refuses the lens (None if never)."""
    last = None
    for r in rows:
        if r.get("admit_at_lens") is False:
            last = r["year"]
    return last


def summarise(rows, rituals, latest=None):
    """Everything a sentence may say, derived from the rows and the ruler block.

    `latest` is the reading on the panel's LAST bar, which is NOT the last year anchor
    (2025-01-02 and 2026-11-19 are not the same day, and only the former is a row of the
    year grid). Calling an anchor "today" would print a growth multiple up to a bar the
    grid never read -- the check leg refuses that.
    """
    meas = [r for r in rows if r.get("reading_pct") is not None]
    caps = [r["capital_where_at_line_cny"] for r in meas
            if r.get("capital_where_at_line_cny") is not None]
    admits = [r for r in meas if r["admit_at_lens"]]
    today = latest if latest is not None else (rows[-1] if rows else None)
    out = {
        "n_years_total": len(rows),
        "n_years_measured": len(meas),
        "n_admit": len(admits),
        "latest_bar": (today or {}).get("anchor"),
        "today_reading_pct": (today or {}).get("reading_pct"),
        "today_capacity_cny": (today or {}).get("capital_where_at_line_cny"),
        "today_admits": (today or {}).get("admit_at_lens"),
        "last_anchor_year": (meas[-1]["year"] if meas else None),
        "last_anchor_reading_pct": (meas[-1]["reading_pct"] if meas else None),
        "earliest_measured_year": (meas[0]["year"] if meas else None),
        "earliest_capacity_cny": (meas[0]["capital_where_at_line_cny"] if meas else None),
        "earliest_reading_pct": (meas[0]["reading_pct"] if meas else None),
        "capacity_min_cny": min(caps) if caps else None,
        "capacity_max_cny": max(caps) if caps else None,
        "first_admit_year": first_admit_year(rows),
        "last_refuse_year": last_refuse_year(rows),
        "lens_cny": rituals.get("lens_cny"),
        "line_pct": rituals.get("line_pct"),
        "lens_label": rituals.get("lens"),
        "published_reading_pct": rituals.get("published_reading_pct"),
        "panel_last": rituals.get("panel_last"),
    }
    # A multiple is only printed when BOTH ends are measured AND they are different
    # days: dividing by a missing year would turn "no reading" into a growth story,
    # and one measured year over zero years would print 1.00x as if it were a finding
    # (r98 family).
    today_cap = out["today_capacity_cny"]
    today_bar = (today or {}).get("anchor")
    if (out["earliest_capacity_cny"] and today_cap
            and meas and today_bar and str(meas[0].get("anchor")) != str(today_bar)):
        out["capacity_multiple"] = round(float(out["today_capacity_cny"])
                                         / float(out["earliest_capacity_cny"]), 2)
        out["capacity_multiple_years"] = [out["earliest_measured_year"],
                                          int(str(today_bar)[:4])]
    else:
        out["capacity_multiple"] = None
        out["capacity_multiple_years"] = None
    out["reproduces_published"] = None
    if (out["published_reading_pct"] is not None
            and out["today_reading_pct"] is not None):
        out["reproduces_published"] = bool(
            abs(float(out["published_reading_pct"]) - float(out["today_reading_pct"]))
            <= REPRO_TOL_PCT)
    out["verdict"] = verdict_name(out)
    return out


def verdict_name(s):
    """Frozen: decided by the pass count, never written by hand."""
    n = s.get("n_years_measured") or 0
    if s.get("line_pct") is None or s.get("lens_cny") is None:
        return "NO_RULER"
    if n == 0:
        return "NO_MEASURABLE_YEAR"
    k = s.get("n_admit") or 0
    if k == n:
        return "CAPACITY_ABOVE_LINE_IN_EVERY_YEAR"
    if k == 0:
        return "BELOW_LINE_IN_EVERY_YEAR"
    return "LINE_CROSSED_INSIDE_THE_WINDOW"


# ---------------------------------------------------------------- sentences

def sentence_fit(s):
    """One line: does the lens fit, and since when."""
    if s.get("line_pct") is None or s.get("lens_cny") is None:
        return "the gate face carries no 1%%-of-ADV line or no capital lens, so this face cannot price a year"
    lens = float(s["lens_cny"])
    n, k = s.get("n_years_measured") or 0, s.get("n_admit") or 0
    if n == 0:
        return "no measured year, so there is nothing to compare the %s lens with" % s.get("lens_label")
    head = ("the %s lens fits in %d of %d measured years" % (s.get("lens_label"), k, n))
    if s["verdict"] == "CAPACITY_ABOVE_LINE_IN_EVERY_YEAR":
        return head + " -- in every year this panel has, the book's own five names were deep enough"
    if s["verdict"] == "BELOW_LINE_IN_EVERY_YEAR":
        worst = max(r for r in [s.get("capacity_max_cny")] if r)
        return (head + " -- in no measured year would %s fit; the largest any year carried is %s CNY"
                % (("{:,}".format(int(lens))), "{:,}".format(int(worst))))
    return (head + " -- it starts fitting in %s, and the last year that refused it is %s"
            % (s.get("first_admit_year"), s.get("last_refuse_year")))


def sentence_multiple(s):
    if s.get("capacity_multiple") is None:
        return ("a capacity multiple needs both ends measured; one end is missing, so the "
                "ratio is not printed")
    a, b = s["capacity_multiple_years"]
    return ("the same five-slot trade carried %s CNY at the line in %s and %s CNY on the "
            "latest bar -- %.2fx in %s years, and that growth is the ETF market's, not "
            "the book's" % ("{:,}".format(int(s["earliest_capacity_cny"])), a,
                            "{:,}".format(int(s["today_capacity_cny"])),
                            s["capacity_multiple"], (b - a) if a and b else "?"))


def sentence_repro(s):
    if s.get("reproduces_published") is None:
        return "no published reading to reproduce"
    if s["reproduces_published"]:
        return ("this face's reading on the latest bar, %.4f%%, reproduces the gate's "
                "published %.4f%%" % (s["today_reading_pct"], s["published_reading_pct"]))
    return ("this face reads %.4f%% on the latest bar while the gate published %.4f%% -- "
            "the two disagree, so the year rows below are not comparable with the gate"
            % (s["today_reading_pct"], s["published_reading_pct"]))


def freshness_problem(payload):
    """Ask an EXTERNAL anchor (the gate's own data.last), not this face's own clock."""
    crit = payload.get("criteria") or {}
    panel = crit.get("panel_last")
    gate_last = crit.get("gate_panel_last")
    if not panel or not gate_last:
        return "STALE: neither the panel cutoff nor the gate's data.last is readable"
    if str(panel) != str(gate_last):
        return ("STALE: this face was priced on panel bar %s but the gate face reads %s"
                % (panel, gate_last))
    return None


# ---------------------------------------------------------------- check leg

def check(payload):
    """Re-derive every published number from the published rows."""
    problems = []
    rows = payload.get("years") or []
    s = payload.get("summary") or {}
    crit = payload.get("criteria") or {}
    line_pct = crit.get("line_pct")
    lens = crit.get("lens_cny")
    if line_pct is None or lens is None:
        problems.append("criteria.line_pct / criteria.lens_cny missing, cannot recompute")
        return {"ok": False, "problems": problems}

    line_frac = float(line_pct) / 100.0
    meas = [r for r in rows if r.get("reading_pct") is not None]
    admits = [r for r in meas if r.get("admit_at_lens")]
    if s.get("n_years_total") != len(rows):
        problems.append("n_years_total %r != rows %r" % (s.get("n_years_total"), len(rows)))
    if s.get("n_years_measured") != len(meas):
        problems.append("n_years_measured %r != rows %r" % (s.get("n_years_measured"), len(meas)))
    if s.get("n_admit") != len(admits):
        problems.append("n_admit %r != recomputed %r" % (s.get("n_admit"), len(admits)))

    verdict = verdict_name({"n_years_measured": len(meas), "n_admit": len(admits),
                            "line_pct": line_pct, "lens_cny": lens})
    if s.get("verdict") != verdict:
        problems.append("verdict %r != recomputed %r" % (s.get("verdict"), verdict))

    # every row's ceiling must follow from its own reading: cap = line * lens / reading
    for r in meas:
        read = float(r["reading_pct"]) / 100.0
        if read <= 0:
            problems.append("year %r has a non-positive reading" % r.get("year"))
            continue
        want = float(line_frac) * float(lens) / read
        got = r.get("capital_where_at_line_cny")
        if got is None:
            problems.append("year %r has a reading but no ceiling" % r.get("year"))
        elif abs(float(got) - want) > max(1.0, want * 1e-3):
            problems.append("year %r ceiling %r != line*lens/reading %r"
                            % (r.get("year"), got, round(want, 2)))
        if r.get("admit_at_lens") != (read <= line_frac):
            problems.append("year %r admit flag disagrees with its own reading" % r.get("year"))
        if (r.get("n_measured") or 0) == 0:
            problems.append("year %r prints a reading with zero measured names" % r.get("year"))

    # a year with unmeasurable slots may not be counted as a clean pass
    for r in rows:
        if r.get("reading_pct") is None:
            if r.get("admit_at_lens") is not None:
                problems.append("year %r has no reading but prints an admit flag" % r.get("year"))
    # a multiple needs both ends
    if s.get("capacity_multiple") is not None:
        if not (s.get("earliest_capacity_cny") and s.get("today_capacity_cny")):
            problems.append("capacity_multiple printed without both ends")

    eras = payload.get("eras") or []
    era_years = [y for e in eras for y in (e.get("years") or [])]
    if era_years != [r["year"] for r in rows]:
        problems.append("era grouping does not cover the year rows exactly once")
    for e in eras:
        mem = [r for r in rows if r["year"] in (e.get("years") or [])]
        m2 = [r for r in mem if r.get("reading_pct") is not None]
        if e.get("n_measured") != len(m2):
            problems.append("era %r n_measured %r != rows %r"
                            % (e.get("era"), e.get("n_measured"), len(m2)))
        if e.get("n_admit") != sum(1 for r in m2 if r.get("admit_at_lens")):
            problems.append("era %r n_admit disagrees with its years" % e.get("era"))
        reads = [r["reading_pct"] for r in m2]
        if reads and e.get("reading_pct_median") is not None:
            if abs(statistics.median(reads) - e["reading_pct_median"]) > 1e-3:
                problems.append("era %r reading median disagrees with its years" % e.get("era"))

    stale = freshness_problem(payload)
    if stale:
        problems.append(stale)

    # The row called "today" must be the panel's last bar, not the last year anchor --
    # and it must reproduce the gate's published reading, otherwise the year rows are
    # priced on a different book than the one the gate decided on.
    latest = payload.get("latest") or {}
    s_last_anchor = s.get("last_anchor_year")
    if latest:
        if s.get("latest_bar") != latest.get("anchor"):
            problems.append("summary.latest_bar %r != latest row %r"
                            % (s.get("latest_bar"), latest.get("anchor")))
        if (s.get("today_reading_pct") is not None
                and latest.get("reading_pct") is not None
                and abs(float(s["today_reading_pct"]) - float(latest["reading_pct"])) > 1e-9):
            problems.append("summary.today_reading_pct does not come from the latest bar")
        last_anchor = [r for r in rows if r.get("year") == s_last_anchor]
        if last_anchor and latest.get("anchor") == last_anchor[-1].get("anchor"):
            problems.append("the latest bar is also a year anchor, so 'today' and the grid "
                            "read the same bar")
        if latest.get("reading_pct") is None:
            problems.append("the latest bar has no reading, so nothing reproduces the gate")
        elif s.get("published_reading_pct") is not None:
            drift = abs(float(s["published_reading_pct"]) - float(latest["reading_pct"]))
            if drift > REPRO_TOL_PCT:
                problems.append("this face reads %.4f%% on the latest bar, the gate published "
                                "%.4f%% (drift %.4f > tol %.4f)"
                                % (latest["reading_pct"], s["published_reading_pct"],
                                   drift, REPRO_TOL_PCT))
    if s.get("reproduces_published") is False:
        problems.append("summary says the published reading is not reproduced")
    return {"ok": not problems, "problems": problems, "verdict": verdict}


# ---------------------------------------------------------------- render

def render_md(payload):
    s = payload.get("summary") or {}
    lines = ["# ETF book -- capacity by year", "",
             "Generated %s (panel bar %s). Line = %s%% of the weakest slot's 20-bar ADV; "
             "lens = %s (%s CNY)." % (payload.get("generated", ""),
                                      payload.get("evidence_cutoff"),
                                      s.get("line_pct"), s.get("lens_label"),
                                      "{:,}".format(int(s["lens_cny"])) if s.get("lens_cny") else "?"),
             "", "## What the years say", "",
             "- %s" % sentence_fit(s),
             "- %s" % sentence_multiple(s),
             "- %s" % sentence_repro(s),
             "", "## Years", "",
             "| year | first bar | names | reading % of ADV | capital at the line (CNY) "
             "| per name (CNY) | binding | admits the lens |",
             "|---|---|---|---|---|---|---|---|"]
    latest = payload.get("latest") or {}
    if latest:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            "latest", latest.get("anchor"), latest.get("n_measured", "-"),
            "-" if latest.get("reading_pct") is None else "%.4f" % latest["reading_pct"],
            "-" if not latest.get("capital_where_at_line_cny")
            else "{:,}".format(int(latest["capital_where_at_line_cny"])),
            "-" if not latest.get("per_name_at_line_cny")
            else "{:,}".format(int(latest["per_name_at_line_cny"])),
            latest.get("binding") or "-",
            "-" if latest.get("admit_at_lens") is None
            else ("yes" if latest["admit_at_lens"] else "no")))
    for r in payload.get("years") or []:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["year"], r["anchor"], r.get("n_measured", "-"),
            "-" if r.get("reading_pct") is None else "%.4f" % r["reading_pct"],
            "-" if not r.get("capital_where_at_line_cny") else "{:,}".format(int(r["capital_where_at_line_cny"])),
            "-" if not r.get("per_name_at_line_cny") else "{:,}".format(int(r["per_name_at_line_cny"])),
            r.get("binding") or "-",
            "-" if r.get("admit_at_lens") is None else ("yes" if r["admit_at_lens"] else "no")))
    lines += ["", "## Eras", "",
              "| era | years | measured | admits | reading median % | capacity median (CNY) |",
              "|---|---|---|---|---|---|"]
    for e in payload.get("eras") or []:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            e["era"], len(e.get("years") or []), e.get("n_measured"), e.get("n_admit"),
            "-" if e.get("reading_pct_median") is None else "%.4f" % e["reading_pct_median"],
            "-" if not e.get("capacity_median_cny") else "{:,}".format(int(e["capacity_median_cny"]))))
    lines += ["", "## Honest boundaries", ""]
    for h in payload.get("honest") or []:
        lines.append("- %s" % h)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- run

def run() -> int:
    t0 = time.time()
    face = load_gate()
    rituals = rulers(face)
    if rituals["line_frac"] is None or rituals["lens_cny"] is None:
        print("gate face carries no usable ruler: line=%r lens=%r"
              % (rituals["line_pct"], rituals["lens_cny"]), flush=True)
        return 2

    close, openp, amt, sc, n_flip = S.nobond_universe()
    anchors = EG.year_anchors(sc.index)
    if not anchors:
        print("no year anchor is readable on this panel", flush=True)
        return 2

    rows = []
    for a in anchors:
        r = measure_year(sc, amt, a, rituals["line_frac"], rituals["lens_cny"])
        rows.append(r)
        print("  %d  %s  picks=%d reading=%s cap=%s  admit=%s"
              % (r["year"], r["anchor"], r.get("n_measured") or 0,
                 "-" if r["reading_pct"] is None else "%.4f%%" % r["reading_pct"],
                 "-" if not r.get("capital_where_at_line_cny")
                 else "{:,}".format(int(r["capital_where_at_line_cny"])),
                 r.get("admit_at_lens")), flush=True)

    # The panel's LAST bar is measured separately: it is the only row that may be called
    # "today", and it is the row that has to reproduce the gate's published reading.
    last_bar = str(pd.Timestamp(sc.index[-1]).date())
    latest_row = measure_year(sc, amt, {"year": int(last_bar[:4]), "label": "latest",
                                        "first_bar": last_bar},
                              rituals["line_frac"], rituals["lens_cny"])
    print("  latest %s  reading=%s cap=%s  admit=%s (gate published %s%%)"
          % (last_bar,
             "-" if latest_row["reading_pct"] is None else "%.4f%%" % latest_row["reading_pct"],
             "-" if not latest_row.get("capital_where_at_line_cny")
             else "{:,}".format(int(latest_row["capital_where_at_line_cny"])),
             latest_row.get("admit_at_lens"), rituals["published_reading_pct"]), flush=True)

    summary = summarise(rows, rituals, latest=latest_row)
    eras = era_block(rows)
    payload = {
        "face": "etf_book_era_capacity",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(sc.index[-1]).date()),
        "criteria": {"line_pct": rituals["line_pct"], "line_frac": rituals["line_frac"],
                     "lens_cny": rituals["lens_cny"], "lens_label": rituals["lens"],
                     "slots": SLOTS, "repro_tol_pct": REPRO_TOL_PCT,
                     "panel_last": str(pd.Timestamp(sc.index[-1]).date()),
                     "gate_panel_last": rituals["panel_last"],
                     "anchor_from_year": EG.ANCHOR_FROM_YEAR,
                     "anchor_to_year": EG.ANCHOR_TO_YEAR},
        "summary": summary,
        "latest": latest_row,
        "years": rows,
        "eras": eras,
        "honest": [
            "the picks on each year's first bar are ranked by the same score row the book "
            "uses today, applied to data up to that bar; they are not the picks the book "
            "actually held in that year (it launched in 2020)",
            "the ADV reading is a 20-bar median as of that bar, so a year is measured with "
            "the liquidity it had, not with today's",
            "the universe is the ETF list that exists TODAY -- names that delisted before "
            "2026 are absent, which is the book's standing survivorship bias and is not "
            "fixed by this face",
            "a year whose five slots cannot all be measured prints no reading rather than a "
            "smaller one (the gate's line is written for five equal slots)",
            "capacity in CNY is the largest capital that fills the WEAKEST of five equal "
            "slots at the line; a book that sizes unevenly would carry a different number",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))

    print("%s | %s" % (summary["verdict"], sentence_fit(summary)), flush=True)
    print(sentence_multiple(summary), flush=True)
    print("reproduces published: %s" % summary["reproduces_published"], flush=True)
    return 0


def main_check() -> int:
    with io.open(OUT_JSON, encoding="utf-8") as f:
        payload = json.load(f)
    res = check(payload)
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res["ok"] else 3


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append("%s %s" % (name, detail))

    # L1 the ceiling identity: cap = line * adv * n
    line = 0.01
    adv = {"A": 1.0e7, "B": 2.0e7, "C": 3.0e7, "D": 4.0e7, "E": 5.0e7}
    m = CE.measure(["A", "B", "C", "D", "E"], 1_000_000.0, line, adv)
    want = line * 1.0e7 * 5
    leg("L1 ceiling identity", abs(m["capital_where_at_line_cny"] - want) < 1e-6,
        "%r vs %r" % (m["capital_where_at_line_cny"], want))

    # L2 a missing slot is named, not priced at zero
    m2 = CE.measure(["A", "B", "C", "D", "Z"], 1_000_000.0, line, adv)
    leg("L2 missing slot named", m2["unmeasurable"] == ["Z"] and m2["binding"] != "Z",
        "%r" % (m2["unmeasurable"],))

    # L3 no ruler no verdict
    leg("L3 no ruler", verdict_name({"n_years_measured": 3, "n_admit": 3,
                                     "line_pct": None, "lens_cny": None}) == "NO_RULER")

    # L4 picks are causal: a planted later row must not leak into an earlier bar
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    planted = pd.DataFrame({"AAA": [1.0, 9.0, 9.0], "BBB": [0.5, 0.1, 0.1]}, index=idx)
    early = picks_at(planted, pd.Timestamp("2020-01-02"), n=1)
    late = picks_at(planted, pd.Timestamp("2020-01-06"), n=1)
    leg("L4 causal picks", early == ["AAA"] and late == ["AAA"],
        "early=%r late=%r" % (early, late))
    planted2 = pd.DataFrame({"AAA": [1.0, 9.0, 9.0], "BBB": [0.5, 9.5, 9.5]}, index=idx)
    leg("L4b later row wins only later",
        picks_at(planted2, pd.Timestamp("2020-01-02"), n=1) == ["AAA"]
        and picks_at(planted2, pd.Timestamp("2020-01-03"), n=1) == ["BBB"])

    # L5 verdict names come from counts
    base = {"line_pct": 1.0, "lens_cny": 1e6}
    leg("L5 all admit", verdict_name(dict(base, n_years_measured=4, n_admit=4))
        == "CAPACITY_ABOVE_LINE_IN_EVERY_YEAR")
    leg("L5b none admit", verdict_name(dict(base, n_years_measured=4, n_admit=0))
        == "BELOW_LINE_IN_EVERY_YEAR")
    leg("L5c crossed", verdict_name(dict(base, n_years_measured=4, n_admit=2))
        == "LINE_CROSSED_INSIDE_THE_WINDOW")
    leg("L5d no measured year", verdict_name(dict(base, n_years_measured=0, n_admit=0))
        == "NO_MEASURABLE_YEAR")

    # L6 an era keeps its boundary years on the right side
    rows = [{"year": y, "reading_pct": 0.5, "admit_at_lens": True,
             "capital_where_at_line_cny": 2.0e6} for y in (2017, 2018)]
    eras = era_block(rows, eras=(("2015-2017", 2015, 2017), ("2018-2020", 2018, 2020)))
    leg("L6 era boundary", eras[0]["years"] == [2017] and eras[1]["years"] == [2018])

    # L7 a multiple needs both ends (missing earliest -> None, never a fake 0)
    rits = {"line_pct": 1.0, "lens_cny": 1e6, "lens": "1M", "published_reading_pct": 1.0}
    s_none = summarise([{"year": 2020, "reading_pct": None, "admit_at_lens": None,
                         "capital_where_at_line_cny": None},
                        {"year": 2021, "reading_pct": 0.9, "admit_at_lens": True,
                         "capital_where_at_line_cny": 1.1e6}], rits)
    leg("L7 multiple needs both ends", s_none["capacity_multiple"] is None
        and s_none["n_years_measured"] == 1)
    # ... and one measured year is not a growth story either: 1.00x over zero years
    s_one = summarise([{"year": 2021, "reading_pct": 0.9, "admit_at_lens": True,
                        "capital_where_at_line_cny": 1.1e6}], rits)
    leg("L7b one year is not a multiple", s_one["capacity_multiple"] is None,
        "%r" % (s_one["capacity_multiple"],))

    # L8 freshness answers with the OTHER face's bar
    stale = freshness_problem({"criteria": {"panel_last": "2026-11-18",
                                            "gate_panel_last": "2026-11-19"}})
    leg("L8 stale names both bars", stale is not None and "2026-11-18" in stale
        and "2026-11-19" in stale, stale or "")
    leg("L8b same bar is fresh",
        freshness_problem({"criteria": {"panel_last": "2026-11-19",
                                        "gate_panel_last": "2026-11-19"}}) is None)

    # L9 a year with no reading may not carry an admit flag through check
    bad = {"criteria": {"line_pct": 1.0, "lens_cny": 1e6, "panel_last": "x",
                        "gate_panel_last": "x"},
           "years": [{"year": 2020, "reading_pct": None, "admit_at_lens": True}],
           "summary": {"n_years_total": 1, "n_years_measured": 0, "n_admit": 1,
                       "line_pct": 1.0, "lens_cny": 1e6,
                       "verdict": "BELOW_LINE_IN_EVERY_YEAR"},
           "eras": []}
    res = check(bad)
    leg("L9 unmeasured year cannot pass", not res["ok"]
        and any("no reading but prints an admit" in p for p in res["problems"]),
        str(res["problems"])[:160])

    # L10 a tampered ceiling is caught by check
    good = {"criteria": {"line_pct": 1.0, "lens_cny": 1e6, "panel_last": "d",
                         "gate_panel_last": "d"},
            "years": [{"year": 2020, "reading_pct": 1.0, "admit_at_lens": True,
                       "capital_where_at_line_cny": 1e6, "n_measured": 5}],
            "summary": {"n_years_total": 1, "n_years_measured": 1, "n_admit": 1,
                        "line_pct": 1.0, "lens_cny": 1e6,
                        "verdict": "CAPACITY_ABOVE_LINE_IN_EVERY_YEAR",
                        "capacity_multiple": None},
            "eras": [{"era": "2018-2020", "years": [2020], "n_measured": 1, "n_admit": 1}]}
    leg("L10 clean payload passes", check(good)["ok"], str(check(good)["problems"]))
    tampered = json.loads(json.dumps(good))
    tampered["years"][0]["capital_where_at_line_cny"] = 1.5e6
    leg("L10b tampered ceiling caught", not check(tampered)["ok"])

    # L11 sentences never invent a number when nothing is measured
    s_no = summarise([], {"line_pct": 1.0, "lens_cny": 1e6, "lens": "1M",
                          "published_reading_pct": 1.0})
    leg("L11 empty rows say so",
        "no measured year" in sentence_fit(s_no)
        and "one end is missing" in sentence_multiple(s_no))

    # L12-L14 the "today" row is the panel's last bar and it must reproduce the gate
    plant = {"criteria": {"line_pct": 1.0, "lens_cny": 1e6, "panel_last": "d",
                          "gate_panel_last": "d"},
             "years": [{"year": 2025, "anchor": "2025-01-02", "reading_pct": 0.61,
                        "admit_at_lens": True,
                        "capital_where_at_line_cny": 0.01 * 1e6 / 0.0061,
                        "n_measured": 5}],
             "latest": {"year": 2026, "anchor": "2026-11-19", "reading_pct": 0.997,
                        "admit_at_lens": True,
                        "capital_where_at_line_cny": 0.01 * 1e6 / 0.00997},
             "summary": {"n_years_total": 1, "n_years_measured": 1, "n_admit": 1,
                         "line_pct": 1.0, "lens_cny": 1e6,
                         "latest_bar": "2026-11-19", "today_reading_pct": 0.997,
                         "last_anchor_year": 2025, "published_reading_pct": 0.997,
                         "verdict": "CAPACITY_ABOVE_LINE_IN_EVERY_YEAR",
                         "capacity_multiple": None, "reproduces_published": True},
             "eras": [{"era": "2024-2026", "years": [2025], "n_measured": 1, "n_admit": 1}]}
    leg("L12 planted face passes", check(plant)["ok"], str(check(plant)["problems"])[:200])

    same = json.loads(json.dumps(plant))
    same["summary"]["latest_bar"] = "2025-01-02"
    same["latest"]["anchor"] = "2025-01-02"
    leg("L12b anchor called today is caught", not check(same)["ok"],
        str(check(same)["problems"])[:160])

    moved = json.loads(json.dumps(plant))
    moved["latest"]["reading_pct"] = 1.4
    res_moved = check(moved)
    leg("L13 a drifted reproduction is caught",
        not res_moved["ok"] and any("the gate published" in p for p in res_moved["problems"]),
        str(res_moved["problems"])[:200])

    off = json.loads(json.dumps(plant))
    off["summary"]["today_reading_pct"] = 0.61
    leg("L14 today_reading must come from the latest bar", not check(off)["ok"])

    print("era_capacity selftest %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    for f in fails:
        print("  FAIL %s" % f)
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return main_check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
