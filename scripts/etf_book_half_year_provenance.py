"""Which years are in the half? -- the refusal sentence nobody ever decomposed.

The supply ladder has been red for thirty-nine rounds on one sentence: the desk's books are
refused by `years_for_half` at a median of 2 years against a line of 3.  Both the ladder board
and the supply face print it, and both the desk's own research notes read it as *front-loading*
-- "the money was already earned, it has been spent".  r1433 asked whether the window caused
it and r1428 asked how many years of new data would heal it.  Neither asked the plainest
question of all: **which years are actually in the half?**

`etf_book_year_caliber.calibers` sorts the year nets descending and counts how many of the
BEST years add up to half the calendar sum.  That number is order-free: it says "the return is
concentrated in k years", and says nothing about whether those k years are at the start or at
the end of the window.  Reading it as front-loading is an interpretation the ruler never made.
This file measures the interpretation.

What it publishes, per book and per phase (the same 3 books x 5 phases r1425/r1426 published,
repriced through the same wrapper -- `candidate_year_gate_phases.arm`, imported):

  members          the years that make up the half, in calendar order, with each year's net
  first / last     calendar position of the earliest and latest member
  mean_position    mean calendar index of the members (0 = first year of the table)
  direction        one_year | early | late | interleaved   (rule frozen in RULE)
  dominant_year    the single best year, its net and its share of the whole calendar sum
  half_from_partial whether any member is a partial year (a partial year can only be dragged,
                   never a best year -- but the flag travels with the sentence either way)

RULE is frozen BEFORE any read, and the thresholds are structural (a position, not a return
level): the direction word is a property of where the members sit, never of a gate line.  This
receipt carries no verdict, no prerereg and no ledger entry: it decides nothing and admits
nothing.  Its only claim is about the SENTENCE -- an operator told "front-loading" while the
half sits in the newest year has been given the wrong reason to change the book.

    python scripts/etf_book_half_year_provenance.py run
    python scripts/etf_book_half_year_provenance.py check
    python scripts/etf_book_half_year_provenance.py selftest
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as CP  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_caliber as K  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_half_year_provenance.json")
PHASE_RECEIPT = os.path.join(ROOT, "results", "etf_book_phase_gate.json")

RULE = {
    "kind": "exploratory",
    "prereg": None,
    "verdict": None,
    "ledger": None,
    "why": ("decomposes an already-published ruler value into the years it is made of; it "
            "admits nothing and refuses nothing -- it only says whether the sentence the "
            "operator reads next to the refusal ('front-loaded') is the ruler's own claim"),
    "frozen": {
        "half_rule": "the best years (descending) that reach HALF of the calendar net sum, "
                     ">= inclusive, exactly as etf_book_year_caliber.calibers counts them",
        "member_order": "members are reported in CALENDAR order, not in ranking order, "
                        "because the direction word is about calendar position",
        "direction_rule": (
            "mid = (n - 1) / 2 over the table's own years; k = 1 -> one_year; "
            "mean calendar index of the members < mid - 0.5 -> early; "
            "> mid + 0.5 -> late; otherwise interleaved"),
        "no_half": ("net <= 0 publishes no_half -- 'this book has no half to explain' is a "
                    "different statement from 'one year explains it' (r1426 family)"),
        "partial_years": ("partial years stay in the table (that is how the ruler counts "
                          "them) and are named in partial_years / half_from_partial"),
        "engine": "candidate_year_gate_phases.arm (imported, never retyped)",
        "annual_rows": "etf_book_year_gate.yearly_returns + candidate_year_gate._year_rows "
                       "(imported, never retyped)",
        "calibers": "etf_book_year_caliber.calibers (imported, never retyped)",
    },
    "frozen_before_read": True,
}

DIRECTION_WORDS = {
    "one_year": "one year supplies the half",
    "early": "the half sits in the early years",
    "late": "the half sits in the late years",
    "interleaved": "the half's years alternate through the window",
    "no_half": "the calendar sum is not positive, so it has no half to explain",
}


# ------------------------------------------------------------------ provenance
def provenance(rows: list[dict]) -> dict:
    """Decompose `years_for_half` into the years it is made of.  No gate lines, no verdicts."""
    years = [str(r["year"]) for r in rows]
    vals = [float(r["net_pct"]) for r in rows]
    partial = {str(r["year"]) for r in rows if r.get("partial")}
    n = len(vals)
    net = sum(vals)
    out = {
        "years": n,
        "net_sum_pct": round(net, 6),
        "years_for_half": None,
        "members": [],
        "first_year": None,
        "last_year": None,
        "mean_position": None,
        "direction": "no_half" if net <= 0 else None,
        "dominant_year": None,
        "dominant_net_pct": None,
        "dominant_share": None,
        "early_half_share": None,
        "late_half_share": None,
        "partial_years": sorted(partial),
        "half_from_partial": None,
    }
    if n == 0:
        return out
    if net > 0:
        half = 0.5 * net
        rank = sorted(range(n), key=lambda i: vals[i], reverse=True)
        members_idx, run = [], 0.0
        for i in rank:
            if run >= half:
                break
            run += vals[i]
            members_idx.append(i)
        members = sorted(members_idx)                     # calendar order
        out["years_for_half"] = len(members_idx)
        out["members"] = [{"year": years[i], "net_pct": round(vals[i], 6),
                           "share": round(vals[i] / net, 6),
                           "position": i, "partial": years[i] in partial}
                          for i in members]
        out["first_year"] = years[members[0]]
        out["last_year"] = years[members[-1]]
        mid = (n - 1) / 2.0
        mean_pos = sum(members) / float(len(members))
        out["mean_position"] = round(mean_pos, 6)
        if len(members) == 1:
            out["direction"] = "one_year"
        elif mean_pos < mid - 0.5:
            out["direction"] = "early"
        elif mean_pos > mid + 0.5:
            out["direction"] = "late"
        else:
            out["direction"] = "interleaved"
        out["half_from_partial"] = any(years[i] in partial for i in members)
        best = rank[0]
        out["dominant_year"] = years[best]
        out["dominant_net_pct"] = round(vals[best], 6)
        out["dominant_share"] = round(vals[best] / net, 6)
        cut = n // 2
        out["early_half_share"] = round(sum(vals[:cut]) / net, 6)
        out["late_half_share"] = round(sum(vals[cut:]) / net, 6)
    return out


def sentence(book: str, prov: dict) -> str:
    """One reader-facing line.  Pure given the provenance block."""
    if prov.get("direction") == "no_half" or prov.get("years_for_half") is None:
        return "%s: no positive calendar sum, so there is no half to explain" % book
    members = prov.get("members") or []
    names = ", ".join("%s %+.2fpp" % (m["year"], m["net_pct"]) for m in members)
    dom = prov.get("dominant_year")
    pos = next((m["position"] for m in members if m["year"] == dom), None)
    tail = ""
    if pos is not None:
        last = prov["years"] - 1
        partial_tail = prov.get("partial_years") or []
        is_newest_full = pos == last - 1 and len(partial_tail) == 1
        tail = (", which is the newest year of the table" if pos == last else
                ", which is the newest FULL year (the last row is a partial year)" if is_newest_full else
                ", which is the first year of the table" if pos == 0 else
                ", which is year %d of %d" % (pos + 1, prov["years"]))
    return ("%s: half of its %d-year net (%+.2fpp) is supplied by %s%s "
            "(dominant year %s = %+.2fpp = %.1f%% of net) -> %s" % (
                book, prov["years"], prov["net_sum_pct"], names, tail, dom,
                prov.get("dominant_net_pct") or 0.0,
                100.0 * (prov.get("dominant_share") or 0.0),
                DIRECTION_WORDS.get(prov["direction"], prov["direction"])))


def aggregate(per_phase: list[dict]) -> dict:
    """Word across a book's phase set: the modal direction, with the counts printed."""
    words = [p["provenance"]["direction"] for p in per_phase]
    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    word = max(counts, key=lambda w: (counts[w], w)) if counts else None
    dom = [p["provenance"].get("dominant_year") for p in per_phase
           if p["provenance"].get("dominant_year")]
    yfh = [p["provenance"].get("years_for_half") for p in per_phase
           if p["provenance"].get("years_for_half") is not None]
    return {
        "phases": len(per_phase),
        "direction_counts": counts,
        "direction": word,
        "dominant_years": sorted(set(dom)),
        "years_for_half_median": (statistics.median(yfh) if yfh else None),
        "any_half_from_partial": any(p["provenance"].get("half_from_partial")
                                     for p in per_phase),
    }


# ----------------------------------------------------------------------- build
def build(cells: list[dict], published: dict | None) -> dict:
    """Assemble the receipt from per-cell provenance.  Identity results travel with it."""
    books: dict[str, list[dict]] = {}
    for c in cells:
        books.setdefault(c["book"], []).append(c)
    out_books = []
    for label in [b for b, _, _ in CP.ARMS] + sorted(k for k in books if k not in
                                                     [b for b, _, _ in CP.ARMS]):
        rows = books.get(label) or []
        if not rows:
            continue
        agg = aggregate(rows)
        out_books.append({
            "book": label,
            "aggregate": agg,
            "sentence": sentence(label, rows[0]["provenance"]) if len(rows) == 1 else (
                sentence(label, rows[0]["provenance"]) +
                " [phase set: %s %d/%d phases]" % (
                    agg["direction"], agg["direction_counts"].get(agg["direction"], 0),
                    agg["phases"])),
            "phase_cells": rows,
        })
    identity = {"checked": published is not None, "cells_compared": 0,
                "max_abs_dev_years_for_half": 0, "max_abs_dev_net_top2_share": 0.0,
                "mismatches": []}
    if published is not None:
        pub = {(b["book"], r["start"]): r for b in published.get("books") or []
               for r in b.get("phase_rows") or []}
        for c in cells:
            key = (c["book"], c["start"])
            ref = pub.get(key)
            if ref is None:
                identity["mismatches"].append("%s/%s not in the published phase receipt"
                                              % key)
                continue
            identity["cells_compared"] += 1
            want = (ref.get("calibers") or {}).get("years_for_half")
            got = c["calibers"].get("years_for_half")
            if want != got:
                identity["mismatches"].append(
                    "%s/%s years_for_half %r != published %r" % (key[0], key[1], got, want))
            w2 = (ref.get("calibers") or {}).get("net_top2_share")
            g2 = c["calibers"].get("net_top2_share")
            if w2 is not None and g2 is not None:
                identity["max_abs_dev_net_top2_share"] = round(max(
                    identity["max_abs_dev_net_top2_share"], abs(g2 - w2)), 8)
                if abs(g2 - w2) > 5e-6:
                    identity["mismatches"].append(
                        "%s/%s net_top2_share %r != published %r"
                        % (key[0], key[1], g2, w2))
    face = {
        "tool": "etf_book_half_year_provenance",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": None,
        "question": ("when a book is refused by years_for_half, WHICH years make up the "
                     "half -- and is the operator's word for that refusal ('front-loaded') "
                     "the ruler's own claim or the desk's reading of it?"),
        "rule": RULE,
        "direction_words": DIRECTION_WORDS,
        "books": out_books,
        "identity": identity,
        "reading": "every refusal sentence on the supply ladder names a concentration, not a "
                   "start date; this receipt prints the start date",
        "elapsed_sec": None,
    }
    face["summary"] = summarize(face)
    return face


def summarize(face: dict) -> dict:
    rows = []
    for b in face.get("books") or []:
        agg = b.get("aggregate") or {}
        rows.append({"book": b["book"], "direction": agg.get("direction"),
                     "years_for_half_median": agg.get("years_for_half_median"),
                     "dominant_years": agg.get("dominant_years")})
    words = sorted({r["direction"] for r in rows if r["direction"]})
    return {"books": len(rows), "directions": words, "per_book": rows,
            "any_early": "early" in words, "any_late": "late" in words}


# ------------------------------------------------------------------------- run
def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, _nflip = S.nobond_universe()
    cells = []
    for label, vt, floor in CP.ARMS:
        for start in CP.PHASE_STARTS:
            ser, _turn = CP.arm(close, openp, amt, sc, vt, floor, start)
            rows = G._year_rows(Y.yearly_returns(ser))
            # the provenance is computed FROM the published year table, not from the
            # unrounded rows: otherwise `check` re-derives from the table and disagrees
            # in the sixth decimal, and a receipt that cannot reproduce itself is a
            # receipt nobody can audit (r1317 family).
            table = [{"year": str(r["year"]), "net_pct": round(r["net_pct"], 6),
                      "partial": bool(r.get("partial"))} for r in rows]
            cells.append({
                "book": label,
                "start": start,
                "calibers": K.calibers(rows),
                "year_table": table,
                "provenance": provenance(table),
            })
    published = None
    if os.path.exists(PHASE_RECEIPT):
        with open(PHASE_RECEIPT, encoding="utf-8") as f:
            published = json.load(f)
    face = build(cells, published)
    last = (cells[0]["year_table"][-1]["year"] if cells else None)
    face["evidence_cutoff"] = _last_bar(close)
    face["last_year_in_tables"] = last
    face["elapsed_sec"] = round(time.time() - t0, 1)
    if (face["identity"]["mismatches"]):
        print("REFUSED: calibers do not reproduce the published phase receipt: %s"
              % face["identity"]["mismatches"][:3], flush=True)
        return 3
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    for b in face["books"]:
        print(b["sentence"], flush=True)
    print("identity cells=%d dev_top2=%s ok" %
          (face["identity"]["cells_compared"],
           face["identity"]["max_abs_dev_net_top2_share"]), flush=True)
    print("wrote", os.path.relpath(OUT, ROOT), "in %.1fs" % face["elapsed_sec"], flush=True)
    return 0


def _last_bar(close) -> str | None:
    try:
        return str(close.index.max().date())
    except Exception:                                   # noqa: BLE001 - face only
        return None


# ------------------------------------------------------------------------ check
def check(path: str | None = None) -> int:
    """Every published sentence must be re-derivable from that book's own year table."""
    p = path or OUT
    if not os.path.exists(p):
        print("absent: %s" % p)
        return 2
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    problems = []
    for b in face.get("books") or []:
        for c in b.get("phase_cells") or []:
            want = provenance(c["year_table"])
            got = c.get("provenance")
            if want != got:
                problems.append("%s/%s provenance does not re-derive" % (b["book"], c["start"]))
            if c.get("calibers", {}).get("years_for_half") != want["years_for_half"]:
                problems.append("%s/%s years_for_half disagrees with its own year table"
                                % (b["book"], c["start"]))
        want_sentence = sentence(b["book"], (b["phase_cells"] or [{}])[0]["provenance"])
        if b.get("sentence") and not b["sentence"].startswith(want_sentence.split(" [phase set")[0]):
            problems.append("%s sentence does not re-derive" % b["book"])
    if (face.get("summary") or {}) != summarize(face):
        problems.append("summary does not re-derive from the books")
    for pr in problems:
        print("PROBLEM:", pr)
    print("check %s: %d book(s), %d problem(s)" %
          ("PASS" if not problems else "FAIL", len(face.get("books") or []), len(problems)))
    return 0 if not problems else 1


# --------------------------------------------------------------------- selftest
def selftest() -> int:
    fails = []

    def chk(ok, msg):
        if not ok:
            fails.append(msg)

    def tbl(spec):
        return [{"year": str(y), "net_pct": v, "partial": False} for y, v in spec]

    # L1 one dominant year -> one_year, and it is the LAST year of the table
    p = provenance(tbl([(2020, 5.0), (2021, 6.0), (2022, 4.0), (2023, 43.0)]))
    chk(p["years_for_half"] == 1, "L1 one dominant year should need one year")
    chk(p["direction"] == "one_year", "L1 direction should be one_year, got %r" % p["direction"])
    chk(p["dominant_year"] == "2023", "L1 dominant year")
    chk(p["first_year"] == p["last_year"] == "2023", "L1 the single member is 2023")

    # L2 front-loaded: members are the first two years -> early
    p = provenance(tbl([(2020, 40.0), (2021, 30.0), (2022, 5.0), (2023, 5.0), (2024, 5.0)]))
    chk(p["members"][0]["year"] == "2020", "L2 first member is the earliest year")
    chk(p["direction"] == "early", "L2 direction early, got %r" % p["direction"])

    # L3 back-loaded: members are the last two years -> late
    p = provenance(tbl([(2020, 5.0), (2021, 5.0), (2022, 5.0), (2023, 30.0), (2024, 40.0)]))
    chk(p["direction"] == "late", "L3 direction late, got %r" % p["direction"])
    chk(p["last_year"] == "2024", "L3 last member is the newest year")

    # L4 members straddling the middle are interleaved, not early or late
    # (members are positions 1 and 3 of five -> mean 2.0 = mid)
    p = provenance(tbl([(2020, 1.0), (2021, 25.0), (2022, 1.0), (2023, 25.0), (2024, 1.0)]))
    chk(p["direction"] == "interleaved", "L4 direction interleaved, got %r" % p["direction"])

    # L5 the direction word uses the MEMBERS, not every year: the mean position of all years
    # would be the middle here, and a ruler that ignored membership would call it interleaved
    p = provenance(tbl([(2020, 1.0), (2021, 1.0), (2022, 1.0), (2023, 1.0), (2024, 50.0)]))
    chk(p["direction"] == "one_year" and p["dominant_year"] == "2024",
        "L5 a single newest year must read one_year, got %r/%r"
        % (p["direction"], p["dominant_year"]))

    # L6 non-positive calendar sum publishes no_half and never a pass
    p = provenance(tbl([(2020, -5.0), (2021, 3.0)]))
    chk(p["years_for_half"] is None and p["direction"] == "no_half",
        "L6 negative net must read no_half, got %r" % p["direction"])
    chk("does not explain" not in sentence("x", p), "L6b the sentence must not claim a half")

    # L7 the half boundary is >= inclusive, exactly like the ruler
    # 1.0 + 2.0 = 3.0 = half of 6.0 -> two members, not three
    p = provenance(tbl([(2020, 1.0), (2021, 2.0), (2022, 1.0), (2023, 2.0)]))
    chk(p["years_for_half"] == 2, "L7 half boundary must be >= inclusive, got %r"
        % p["years_for_half"])

    # L8 partial years travel with the sentence
    rows = [{"year": "2025", "net_pct": 10.0, "partial": False},
            {"year": "2026", "net_pct": 1.0, "partial": True}]
    p = provenance(rows)
    chk(p["partial_years"] == ["2026"], "L8 partial year must be named")
    chk(p["half_from_partial"] is False, "L8 the best year is the full one")

    # L9 early+late shares are a partition of the net sum
    p = provenance(tbl([(2020, 5.0), (2021, -2.0), (2022, 3.0), (2023, 4.0)]))
    chk(abs((p["early_half_share"] + p["late_half_share"]) - 1.0) < 1e-9,
        "L9 early+late shares must sum to 1")

    # L10 the provenance is order-free in the values but order-aware in the members:
    # shuffling the rows must NOT change the members' calendar positions
    a = provenance(tbl([(2020, 4.0), (2021, 9.0), (2022, 5.0)]))
    b = provenance(tbl([(2022, 5.0), (2020, 4.0), (2021, 9.0)]))
    chk(a["years_for_half"] == b["years_for_half"], "L10 ranking must be order-free")
    chk(a["direction"] == b["direction"], "L10 direction must be stable under row order")

    # L11 the sentence names every member and the dominant year
    p = provenance(tbl([(2020, 40.0), (2021, 30.0), (2022, 5.0), (2023, 5.0), (2024, 5.0)]))
    s = sentence("book_x", p)
    for frag in ("2020", "2021", "book_x", "half"):
        chk(frag in s, "L11 sentence must mention %r: %s" % (frag, s))

    # L12 the rule block carries no gate line: this receipt cannot refuse or admit
    keys = json.dumps(RULE["frozen"]).lower()
    for bad in ("top2_share_max", "worst_year_floor_pp", "line_", "admit_word"):
        chk(bad not in keys, "L12 the frozen rule must not carry an admission line (%s)" % bad)

    # L13 aggregate picks the modal direction and prints the counts
    cells = [{"book": "b", "provenance": {"direction": w, "years_for_half": 2,
                                          "dominant_year": "2025", "half_from_partial": False}}
             for w in ("late", "late", "early")]
    agg = aggregate(cells)
    chk(agg["direction"] == "late" and agg["direction_counts"] == {"late": 2, "early": 1},
        "L13 modal direction, got %r" % (agg["direction"],))

    # L14 magnitude: a real (heavy) row count must still finish this function
    big = tbl([(2000 + i, float((i * 7) % 13)) for i in range(40)])
    p = provenance(big)
    chk(p["years_for_half"] is not None, "L14 a 40-year table must produce a half")

    # L15 a dominant year that is the last FULL one must be named as such -- the sentence may
    # not call a book with a stub tail "year 6 of 7" and leave the reader to guess
    rows = [{"year": str(2020 + i), "net_pct": (43.0 if i == 4 else 5.0),
             "partial": (i == 5)} for i in range(6)]
    p = provenance(rows)
    chk(p["dominant_year"] == "2024" and p["direction"] == "one_year",
        "L15 fixture: the dominant year is the newest full one")
    chk("newest FULL year" in sentence("book_x", p),
        "L15 sentence must say it is the newest full year: %s" % sentence("book_x", p))

    print("%d/%d PASS" % (15 - len(fails), 15))
    for f in fails:
        print("FAIL:", f)
    return 0 if not fails else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check(argv[2] if len(argv) > 2 else None)
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))