#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SUPPLY CALENDAR FACE -- is the empty pool "no topic", or "no topic survives
its own calendar"?

r1415/r1418/r1420 built a yearly gate that judges a candidate book by its
calendar-year shape, and a phase layer that lets the same gate answer "cannot
tell". Their readings left the supply floor red for a third reason, and that
reason was invisible in every supply face:

  pool        status=ready entries                    -> 0
  tickets     open unclaimed tickets                  -> 0
  queue       live drafts (need a prereg freeze)      -> 0
  backlog     cross-company rows                      -> not ours

So supply_candidate_face prints AGENDA_DEBT, whose reading says "generate a
topic". But this desk HAS candidates: the adopted ETF book, its un-overlaid
sibling, the floor arm, the smallcap and breadth books. They were judged, and
the judgement was a refusal -- `r1415`: CONDITIONAL on a partial year;
`r1418`: CONDITIONAL, top-2 share 71.08% against a 70% line; `r1420`: the
sibling cannot be judged at all across phases. "Nobody wrote a topic" and
"every topic we have fails its own calendar" need opposite responses (write a
new topic vs. wait for another year of evidence / re-cut the book), and they
were printing the same word -- the exact defect class r1199 fixed for the pool
and r98 fixed for unreadable files, one layer up.

THIS FACE ONLY READS PUBLISHED RECEIPTS. It computes no returns, re-prices
nothing, and imports no engines; every number it prints is copied from a
receipt that already exists and is re-derived in --check.

Verdict (frozen before any receipt was read):
  ADMITTED_CANDIDATE_EXISTS    at least one candidate reads ADMIT
  NO_CANDIDATE_PASSES_CALENDAR at least one candidate was judged and none
                               reads ADMIT (each carries its failing checks)
  NO_CANDIDATES                no receipt declares any candidate
  UNKNOWN                      declared receipts were unreadable and no
                               candidate could be read (unknown is not empty)

Only the literal word `ADMIT` is a pass. CONDITIONAL / REFUSE /
REFUSE_AS_CANDIDATE / UNADJUDICABLE_PHASE are all refusals here on purpose: a
candidate the gate will not admit cannot be offered to the supply floor as
"startable today".

  python scripts/supply_calendar_face.py run
  python scripts/supply_calendar_face.py --selftest
  python scripts/supply_calendar_face.py --check
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
OUT_JSON = os.path.join(ROOT, "results", "supply_calendar.json")
OUT_MD = os.path.join(ROOT, "results", "supply_calendar.md")

PASS_WORD = "ADMIT"

# "the caller said nothing about the ruler" -- distinct from "the caller proved
# there is no elected ruler" (r1432 selftest leg: no_election must be reachable).
_AUTO = object()

# Declared receipts, in preference order. The phase-aware reading supersedes a
# single-phase one for the same book, so it is listed first and wins the merge.
RECEIPTS = (
    ("results/etf_book_phase_gate.json", "phase_gate"),
    ("results/etf_book_year_gate/YEAR-GATE.json", "year_gate"),
)


def elected_ruler():
    """The ruler the desk elected on fixtures (r1429), imported -- never retyped.

    r1431 adopted it as the calendar's refusal reason; this face therefore names
    the reason with the same ruler instead of with the one r1426 disqualified.
    Returns (name_or_None, error)."""
    try:
        from scripts import etf_book_admission_ruler_election as E
        return (E.elect() or {}).get("elected"), ""
    except Exception as exc:                      # noqa: BLE001 - reported, not swallowed
        return None, "election unreadable: %s" % exc


def _rel(path, root):
    """Repo-relative label, safe across drives (a temp fixture on C: under a
    repo on K: makes os.path.relpath raise -- r1371 family)."""
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def _load(path):
    """(obj, error). Missing/corrupt is an ERROR, never an empty candidate
    list -- r98: unknown is not empty."""
    if not os.path.exists(path):
        return None, "absent"
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f), ""
    except Exception as exc:                      # noqa: BLE001 - reported
        return None, "unreadable: %s" % exc


def _phase_state(obj, book):
    """Phase verdict from the receipt's own summary block, or re-derived from
    its phase rows with the receipt's stated rule. Never guessed."""
    summ = (obj.get("summary") or {}).get(book)
    if isinstance(summ, dict) and summ.get("state"):
        return summ["state"], summ
    return None, summ if isinstance(summ, dict) else {}


def read_phase_gate(path, obj, err, root=ROOT):
    """Books + phases. A book is a candidate only if it carries phase rows."""
    rows = []
    if obj is None:
        return rows, err
    for b in obj.get("books") or []:
        name = b.get("book")
        if not name:
            continue
        phases = b.get("phase_rows") or []
        state, summ = _phase_state(obj, name)
        failing = []
        for p in phases:
            for c in p.get("failing_checks") or []:
                if c not in failing:
                    failing.append(c)
        rows.append({
            "candidate": name,
            "receipt": _rel(path, root),
            "receipt_asof": obj.get("asof"),
            "reading": "phase",
            "phases": len(phases),
            "state": state,
            "pass": state == PASS_WORD,
            "failing_checks": failing,
            "median_top2_share": summ.get("median_top2_share"),
            "spread_pp": summ.get("spread_pp"),
            "margin_pp": summ.get("margin_pp"),
            "single_phase_verdict": summ.get("single_phase_verdict"),
            # r1427: a refusal is only as good as the ruler that produced it. The
            # phase receipt now re-reads every book through the calibers r1426 proved
            # self-adjudicable, so carry its word here instead of leaving the reader
            # with a number nobody can trust (r1426: net_top2_share cannot adjudicate
            # three of its own four arms).
            "refusal_survival": (b.get("refusal_survival") or {}).get("word"),
            "trusted_states": {
                c: (b.get("caliber_adjudication") or {}).get(c, {}).get("state")
                for c in ((b.get("refusal_survival") or {}).get("trusted") or [])},
            # r1432: the WORD above says a trusted ruler also refuses; the operator
            # still had to open the receipt to learn with what number. Carry the
            # adjudicated reading (median against its own line) for every trusted
            # caliber so the refusal sentence can be printed from a ruler we trust.
            "trusted_readings": {
                c: _reading_of((b.get("caliber_adjudication") or {}).get(c))
                for c in ((b.get("refusal_survival") or {}).get("trusted") or [])},
            # A5 input, from the receipt's own published sums (never re-derived
            # from returns): how many phases would make "half" a rounding artefact.
            "degenerate_phases": _degenerate_phases(phases),
        })
    return rows, ""


def _reading_of(adj):
    """Compact copy of one caliber adjudication block (median vs its own line)."""
    if not isinstance(adj, dict):
        return None
    return {k: adj.get(k) for k in ("state", "median", "line", "spread", "margin", "unit")
            if adj.get(k) is not None} or None


def _degenerate_phases(phases):
    """Count phases where |net|/gross <= 0.5 -- the A5 printing rule's input."""
    from scripts import etf_book_admission_refusal_caliber_adoption as A
    n = 0
    for p in phases:
        cal = p.get("calibers") or {}
        ratio = A.net_over_gross(cal.get("net_sum_pct"), cal.get("gross_sum_pct"))
        if A.is_degenerate(ratio):
            n += 1
    return n


def _fmt(value):
    if value is None:
        return "?"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    return ("%d" % f) if abs(f - round(f)) < 1e-9 else ("%.3f" % f)


def elected_reason(row, elected):
    """The refusal sentence under the ruler r1431 adopted, or an honest 'cannot'.

    Pure given `elected` (which the caller takes from the election, never from a
    constant here). Words:
      refuse         the elected ruler refuses this book, reading carried here
      admitted       the elected ruler admits it -- r1431 A2 says this cannot
                     happen for a cell refused today; printed, never hidden
      indeterminate  every phase is flat (A5): 'half' is a rounding artefact
      not_on_record  the receipt carries no reading for the elected ruler
      no_election    the election could not be read
    """
    if row.get("pass"):
        return None
    if not elected:
        return {"ruler": None, "word": "no_election"}
    readings = row.get("trusted_readings") or {}
    got = readings.get(elected)
    if not got:
        return {"ruler": elected, "word": "not_on_record"}
    state = got.get("state")
    if state and "UNADJUDICABLE" in str(state):
        return {"ruler": elected, "word": "cannot_adjudicate", "state": state,
                "reading": got}
    if row.get("phases") and row.get("degenerate_phases") == row.get("phases"):
        return {"ruler": elected, "word": "indeterminate", "state": state,
                "reading": got}
    word = "refuse" if state != PASS_WORD else "admitted"
    return {"ruler": elected, "word": word, "state": state, "reading": got,
            "sentence": "%s median %s vs line %s (%s)" % (
                elected, _fmt(got.get("median")), _fmt(got.get("line")), state)}


def _reason_clause(row):
    """(name, phrase) for the summary, or None when nothing may be printed."""
    reason = row.get("elected_reason") or {}
    word = reason.get("word")
    if word == "refuse":
        return "%s refused at %s" % (row["candidate"], reason["sentence"])
    if word == "admitted":
        return ("%s is ADMITTED by %s -- not a refusal any more"
                % (row["candidate"], reason["ruler"]))
    if word == "indeterminate":
        return "%s indeterminate under %s (flat years, no sentence)" % (
            row["candidate"], reason["ruler"])
    if word == "cannot_adjudicate":
        return "%s cannot be judged by %s (phase spread)" % (row["candidate"], reason["ruler"])
    if word == "not_on_record":
        return "%s has no %s reading on record" % (row["candidate"], reason["ruler"])
    return None


def read_year_gate(path, obj, err, root=ROOT):
    """One verdict per book, with the failing check names the receipt printed."""
    rows = []
    if obj is None:
        return rows, err
    for b in obj.get("books") or []:
        name = b.get("book")
        if not name:
            continue
        failing = [k for k, v in (b.get("checks") or {}).items() if v is False]
        vm = b.get("year_metrics") or {}
        rows.append({
            "candidate": name,
            "receipt": _rel(path, root),
            "receipt_asof": obj.get("asof"),
            "reading": "single_phase",
            "phases": 1,
            "state": b.get("verdict"),
            "pass": b.get("verdict") == PASS_WORD,
            "failing_checks": failing,
            "top2_share": vm.get("top2_share"),
            "positive_years": vm.get("positive_years"),
            "years": vm.get("years"),
            "worst_year_pp": vm.get("worst"),
        })
    return rows, ""


ADAPTERS = {"phase_gate": read_phase_gate, "year_gate": read_year_gate}


def verdict_of(rows, unreadable):
    """Pure. Refusals need a candidate to refuse; an unreadable receipt with
    nothing readable is UNKNOWN, never 'nobody passes'."""
    if not rows:
        return "UNKNOWN" if unreadable else "NO_CANDIDATES"
    if any(r["pass"] for r in rows):
        return "ADMITTED_CANDIDATE_EXISTS"
    return "NO_CANDIDATE_PASSES_CALENDAR"


READING = {
    "ADMITTED_CANDIDATE_EXISTS":
        "a candidate reads ADMIT on its own calendar: it may be offered to "
        "the supply floor",
    "NO_CANDIDATE_PASSES_CALENDAR":
        "every candidate the desk has judged was refused by its own "
        "calendar: the empty pool is not a missing topic, it is a missing "
        "year of evidence",
    "NO_CANDIDATES":
        "no receipt declares a candidate -- the empty pool is genuine agenda "
        "debt (write a topic)",
    "UNKNOWN":
        "declared receipts were unreadable -- unknown is not empty (r98)",
}


def build(receipts=None, root=None, elected=_AUTO):
    """Assemble the face. Injection exists for hermetic selftests."""
    root = root or ROOT
    receipts = RECEIPTS if receipts is None else receipts
    if elected is _AUTO:
        elected, election_err = elected_ruler()
    else:
        election_err = ""
    rows, by_name, unreadable, seen = [], {}, [], []
    for rel, kind in receipts:
        path = rel if os.path.isabs(rel) else os.path.join(root, rel)
        obj, err = _load(path)
        adapter = ADAPTERS[kind]
        got, err2 = adapter(path, obj, err, root)
        if err or err2:
            unreadable.append({"receipt": rel, "reason": err or err2})
            continue
        seen.append(rel)
        for r in got:
            # first declaration wins for a given candidate (phase beats
            # single-phase because it is listed first); the loser is recorded
            if r["candidate"] in by_name:
                by_name[r["candidate"]]["superseded_receipts"].append(r["receipt"])
                continue
            r["superseded_receipts"] = []
            by_name[r["candidate"]] = r
            rows.append(r)
    verdict = verdict_of(rows, unreadable)
    # The refusal reason is printed with the ruler r1431 adopted, not with the
    # one r1426 disqualified; the verdict words above are untouched (A2: a
    # reporting change may only ever refuse more, never fewer).
    for r in rows:
        r["elected_reason"] = elected_reason(r, elected)
    # The summary carries only reasons that say something about the book; "the
    # receipt has no reading for this ruler" is a note for the md page (the ruler
    # split line already says when a book was not re-read).
    active = ("refuse", "admitted", "indeterminate", "cannot_adjudicate")
    sentences, notes = [], []
    for r in rows:
        clause = _reason_clause(r)
        if not clause:
            continue
        (sentences if (r.get("elected_reason") or {}).get("word") in active
         else notes).append(clause)
    return {
        "tool": "supply_calendar_face",
        "pass_word": PASS_WORD,
        "receipts_declared": [r[0] for r in receipts],
        "receipts_read": seen,
        "receipts_unreadable": unreadable,
        "candidates": rows,
        "n_candidates": len(rows),
        "n_refused": sum(1 for r in rows if not r["pass"]),
        "n_admitted": sum(1 for r in rows if r["pass"]),
        "ruler_split": ruler_split(rows),
        "elected_ruler": elected,
        "election_error": election_err,
        "elected_reasons": sentences,
        "elected_notes": notes,
        "verdict": verdict,
        "reading": READING[verdict],
    }


RULER_WORDS = {
    "REFUSAL_SURVIVES_TRUSTED_RULER": "survives",
    "REFUSAL_WAS_RULER_ARTIFACT": "artifact",
    "PARTIAL_TRUSTED_READ": "partial",
    "UNCERTIFIED": "uncertified",
}


def ruler_split(rows):
    """Split the refusals by whether a self-adjudicable ruler also refuses them --
    a refusal carried only by a ruler that cannot judge itself is an artifact and
    must not be read as evidence about the book (r1426/r1427)."""
    out = {"survives": [], "artifact": [], "partial": [], "uncertified": [],
           "no_phase_set": []}
    for r in rows:
        if r.get("pass"):
            continue
        word = r.get("refusal_survival")
        if word is None:
            out["no_phase_set"].append(r["candidate"])
            continue
        key = RULER_WORDS.get(word)
        if key is None:
            out["uncertified"].append(r["candidate"])
        else:
            out[key].append(r["candidate"])
    return out


def _one_line(row):
    """Name the failing check, not just the word CONDITIONAL."""
    checks = ", ".join(row.get("failing_checks") or []) or "no named check"
    extra = ""
    if row.get("state") == "UNADJUDICABLE_PHASE" and row.get("spread_pp") is not None:
        extra = " (phase spread %.2fpp vs margin %spp)" % (
            row["spread_pp"], row.get("margin_pp"))
    return "%s: %s via %s%s" % (row["candidate"], row.get("state"), checks, extra)


def summary_line(face):
    """The sentence an operator needs: why the pool is empty."""
    if face["verdict"] == "NO_CANDIDATE_PASSES_CALENDAR":
        names = "; ".join(_one_line(r) for r in face["candidates"])
        line = "no candidate passes its calendar (%d refused): %s" % (
            face["n_refused"], names)
        rs = face.get("ruler_split") or {}
        if rs.get("survives"):
            line += (" | ruler: %d refusal(s) survive a self-adjudicable caliber (%s)"
                     % (len(rs["survives"]), ", ".join(rs["survives"])))
        if rs.get("artifact"):
            line += (" | WARNING %d refusal(s) only from an untrustworthy ruler (%s)"
                     % (len(rs["artifact"]), ", ".join(rs["artifact"])))
        if rs.get("no_phase_set") and (rs.get("survives") or rs.get("artifact")
                                       or rs.get("partial") or rs.get("uncertified")):
            line += (" | no phase set, ruler not re-read (%s)"
                     % ", ".join(rs["no_phase_set"]))
        if face.get("elected_reasons"):
            line += " | reason: " + "; ".join(face["elected_reasons"])
        return line
    return face["reading"]


def write_md(face, path):
    lines = [
        "# 供给日历面：池子空着，是没题，还是题都过不了自己的日历",
        "",
        "判词 **%s** —— %s" % (face["verdict"], face["reading"]),
        "",
        "| 候选 | 读数 | 判决 | 未过的检查 | 收据 |",
        "|---|---|---|---|---|",
    ]
    for r in face["candidates"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["candidate"], r["reading"], r.get("state"),
            ", ".join(r.get("failing_checks") or []) or "—", r["receipt"]))
    if face["receipts_unreadable"]:
        lines += ["", "读不到的收据（未知不是空）："]
        for u in face["receipts_unreadable"]:
            lines.append("- %s —— %s" % (u["receipt"], u["reason"]))
    rs = face.get("ruler_split") or {}
    if any(v for k, v in rs.items() if v):
        lines += ["", "## 拒的是书还是尺子（r1426 口径复读）", ""]
        if rs.get("survives"):
            lines.append("- 尺子可自判且同样拒：%s —— 拒是真的，处置是等证据或重切书"
                         % ", ".join(rs["survives"]))
        if rs.get("artifact"):
            lines.append("- **仅由不可自判的尺子拒**：%s —— 这是尺子的问题，不许当证据"
                         % ", ".join(rs["artifact"]))
        if rs.get("partial"):
            lines.append("- 可自判尺子在本组相位上读不出：%s" % ", ".join(rs["partial"]))
        if rs.get("uncertified"):
            lines.append("- 无在册可自判尺子：%s（不猜）" % ", ".join(rs["uncertified"]))
        if rs.get("no_phase_set"):
            lines.append("- 无相位集、尺子未复读：%s" % ", ".join(rs["no_phase_set"]))
    if face.get("elected_reasons") or face.get("elected_notes") or face.get("election_error"):
        lines += ["", "## 拒的理由用的是哪把尺子（r1431 采纳：%s）"
                  % (face.get("elected_ruler") or "选举读不出"), ""]
        if face.get("election_error"):
            lines.append("- 选举不可读：%s（不猜尺子）" % face["election_error"])
        for clause in face.get("elected_reasons") or []:
            lines.append("- %s" % clause)
        for clause in face.get("elected_notes") or []:
            lines.append("- %s" % clause)
        lines += ["", "选举来自 `scripts/etf_book_admission_ruler_election.py`（fixtures 上选出"
                  "，不在本书上挑）；每本候选的读数抄自相位闸收据的 caliber 裁定块，本面不重算。"
                  "判决词不变：换的只是「拒的理由」，不是「拒」本身。"]
    lines += [
        "",
        "读法：只有字面 `ADMIT` 算过。CONDITIONAL / REFUSE / UNADJUDICABLE_PHASE "
        "在本面一律是拒——日历闸不肯放行的候选，不能当作「今天就能点火」的供给。"
        "「没人写题」要开题，「题都过不了日历」要等证据或重切书，两件事的处置相反，"
        "把两种都印成 agenda debt 等于没说。",
        "",
    ]
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ----------------------------------------------------------------- selftest
def _selftest():
    ok = [0, 0]

    def check(name, got, want):
        ok[1] += 1
        if got == want:
            ok[0] += 1
            print("  PASS %s" % name)
        else:
            print("  FAIL %s -> %r != %r" % (name, got, want))

    import tempfile
    tmp = tempfile.mkdtemp(prefix="supplycal-")

    def write(name, obj):
        p = os.path.join(tmp, name)
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        return p

    # (1) the frozen word rule: only ADMIT passes
    check("ADMIT passes", verdict_of([{"pass": True}], []),
          "ADMITTED_CANDIDATE_EXISTS")
    check("CONDITIONAL alone is a refusal",
          verdict_of([{"pass": False}], []), "NO_CANDIDATE_PASSES_CALENDAR")
    check("UNADJUDICABLE alone is a refusal",
          verdict_of([{"pass": False}], []), "NO_CANDIDATE_PASSES_CALENDAR")
    check("no rows and no unreadable -> no candidates",
          verdict_of([], []), "NO_CANDIDATES")
    check("no rows but an unreadable receipt -> unknown, not empty",
          verdict_of([], [{"receipt": "x"}]), "UNKNOWN")

    # (2) year-gate adapter names the failing check (r1418's live shape)
    yg = write("year.json", {"asof": "2026-11-08T08:38:12+0800", "books": [
        {"book": "nobond_vt08_adopted", "verdict": "CONDITIONAL",
         "checks": {"Y1_positive_years_share": True, "Y4_top2_share": False},
         "year_metrics": {"top2_share": 0.7108, "positive_years": 7,
                          "years": 7, "worst": 1.898}},
        {"book": "nobond_base", "verdict": "ADMIT",
         "checks": {"Y1_positive_years_share": True}, "year_metrics": {}},
    ]})
    f = build(receipts=[(yg, "year_gate")], root=tmp)
    check("year receipt read", f["verdict"], "ADMITTED_CANDIDATE_EXISTS")
    by = {r["candidate"]: r for r in f["candidates"]}
    check("failing check carried verbatim",
          by["nobond_vt08_adopted"]["failing_checks"], ["Y4_top2_share"])
    check("named in the one-line reason",
          "Y4_top2_share" in _one_line(by["nobond_vt08_adopted"]), True)

    # (3) phase adapter: state from summary, spread printed for cannot-tell
    pg = write("phase.json", {
        "asof": "2026-11-08T09:25:05+08:00",
        "summary": {"a_book": {"state": "CONDITIONAL", "median_top2_share": 0.7958,
                               "spread_pp": 8.74, "margin_pp": 9.58},
                    "b_book": {"state": "UNADJUDICABLE_PHASE",
                               "median_top2_share": 0.8207, "spread_pp": 20.82,
                               "margin_pp": 12.07}},
        "books": [
            {"book": "a_book", "phase_rows": [
                {"start": "2020-01-01", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"]},
                {"start": "2020-01-08", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"]}]},
            {"book": "b_book", "phase_rows": [
                {"start": "2020-01-01", "verdict": "ADMIT", "failing_checks": []},
                {"start": "2020-01-08", "verdict": "REFUSE",
                 "failing_checks": ["Y4_top2_share", "Y3_worst_year"]}]},
        ]})
    f2 = build(receipts=[(pg, "phase_gate")], root=tmp)
    check("phase book kept", sorted(r["candidate"] for r in f2["candidates"]),
          ["a_book", "b_book"])
    b = {r["candidate"]: r for r in f2["candidates"]}
    check("phase count", b["a_book"]["phases"], 2)
    check("cannot-tell is a refusal",
          b["b_book"]["pass"], False)
    check("cannot-tell prints its phase spread",
          "phase spread 20.82pp" in _one_line(b["b_book"]), True)
    check("union of failing checks across phases",
          b["b_book"]["failing_checks"], ["Y4_top2_share", "Y3_worst_year"])

    # (4) the same book in both receipts: read order decides, loser recorded.
    #     Fixtures share one candidate name on purpose -- a merge test whose
    #     two sides never overlap proves nothing (caught by this very leg).
    same = "BOOK_X"
    pg_same = write("phase_same.json", {
        "asof": "p", "summary": {same: {"state": "UNADJUDICABLE_PHASE",
                                        "spread_pp": 20.8, "margin_pp": 12.0}},
        "books": [{"book": same, "phase_rows": [
            {"start": "p1", "verdict": "ADMIT", "failing_checks": []},
            {"start": "p2", "verdict": "REFUSE",
             "failing_checks": ["Y3_worst_year"]}]}]})
    yg_same = write("year_same.json", {"asof": "y", "books": [
        {"book": same, "verdict": "ADMIT", "checks": {}, "year_metrics": {}}]})
    f_phase = build(receipts=[(pg_same, "phase_gate"), (yg_same, "year_gate")],
                    root=tmp)
    f_year = build(receipts=[(yg_same, "year_gate"), (pg_same, "phase_gate")],
                   root=tmp)
    r_phase = {r["candidate"]: r for r in f_phase["candidates"]}
    r_year = {r["candidate"]: r for r in f_year["candidates"]}
    check("phase reading wins when listed first",
          r_phase[same]["reading"], "phase")
    check("single-phase reading wins when listed first",
          r_year[same]["reading"], "single_phase")
    check("the loser is recorded, not dropped",
          len(r_phase[same]["superseded_receipts"]), 1)
    check("one row per candidate after the merge",
          len(f_phase["candidates"]), 1)

    # (5) absent receipt is not "no candidates" and not a pass
    f5 = build(receipts=[(os.path.join(tmp, "__absent__.json"), "year_gate")],
               root=tmp)
    check("absent receipt -> UNKNOWN", f5["verdict"], "UNKNOWN")
    check("absent receipt named", f5["receipts_unreadable"][0]["reason"], "absent")

    # (6) all-refused fixture summarises as the calendar sentence, not silence
    only_refused = write("r.json", {"asof": "x", "books": [
        {"book": "only", "verdict": "CONDITIONAL",
         "checks": {"Y4_top2_share": False}, "year_metrics": {}}]})
    f6 = build(receipts=[(only_refused, "year_gate")], root=tmp)
    check("all-refused verdict", f6["verdict"], "NO_CANDIDATE_PASSES_CALENDAR")
    check("summary names the candidate and the check",
          summary_line(f6), "no candidate passes its calendar (1 refused): "
                            "only: CONDITIONAL via Y4_top2_share")

    # (7) determinism
    check("deterministic", json.dumps(f_phase, sort_keys=True),
          json.dumps(build(receipts=[(pg_same, "phase_gate"),
                                     (yg_same, "year_gate")],
                           root=tmp), sort_keys=True))

    # (8) r1427: the refusal is split by whether a self-adjudicable ruler agrees
    pg_ruler = write("phase_ruler.json", {
        "asof": "r", "summary": {"survives_book": {"state": "CONDITIONAL"},
                                 "artifact_book": {"state": "CONDITIONAL"},
                                 "unread_book": {"state": "CONDITIONAL"},
                                 "old_book": {"state": "CONDITIONAL"}},
        "books": [
            {"book": "survives_book", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"]}],
             "refusal_survival": {"word": "REFUSAL_SURVIVES_TRUSTED_RULER",
                                  "trusted": ["years_for_half"]},
             "caliber_adjudication": {"years_for_half": {"state": "FAIL"}}},
            {"book": "artifact_book", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"]}],
             "refusal_survival": {"word": "REFUSAL_WAS_RULER_ARTIFACT",
                                  "trusted": ["years_for_half"]},
             "caliber_adjudication": {"years_for_half": {"state": "PASS"}}},
            {"book": "unread_book", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL", "failing_checks": []}],
             "refusal_survival": {"word": "PARTIAL_TRUSTED_READ",
                                  "trusted": ["years_for_half"]},
             "caliber_adjudication": {"years_for_half": {"state": "UNADJUDICABLE_CALIBER"}}},
            {"book": "old_book", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL", "failing_checks": []}]},
        ]})
    f8 = build(receipts=[(pg_ruler, "phase_gate")], root=tmp)
    rs = f8["ruler_split"]
    check("survives named", rs["survives"], ["survives_book"])
    check("artifact named", rs["artifact"], ["artifact_book"])
    check("partial named", rs["partial"], ["unread_book"])
    check("no phase set is not called an artifact", rs["no_phase_set"], ["old_book"])
    check("the split does not change the verdict", f8["verdict"],
          "NO_CANDIDATE_PASSES_CALENDAR")
    check("summary warns on an artifact-only refusal",
          "WARNING 1 refusal(s) only from an untrustworthy ruler" in summary_line(f8), True)
    check("summary states the surviving refusal",
          "1 refusal(s) survive a self-adjudicable caliber" in summary_line(f8), True)
    check("trusted states carried per row",
          {r["candidate"]: r["trusted_states"] for r in f8["candidates"]}["artifact_book"],
          {"years_for_half": "PASS"})

    # (9) r1432: the refusal sentence must come from the ELECTED ruler, and a flat
    # book may not carry one at all (r1431's A5 printing rule).
    pg_elected = write("elected.json", {
        "asof": "r1432", "summary": {
            "book_a": {"state": "CONDITIONAL"},
            "book_flat": {"state": "CONDITIONAL"},
            "book_norec": {"state": "CONDITIONAL"},
        },
        "books": [
            {"book": "book_a", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"],
                 "calibers": {"net_sum_pct": 81.0, "gross_sum_pct": 81.0}},
                {"start": "p2", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"],
                 "calibers": {"net_sum_pct": 78.9, "gross_sum_pct": 91.9}}],
             "refusal_survival": {"word": "REFUSAL_SURVIVES_TRUSTED_RULER",
                                  "trusted": ["years_for_half", "effective_years"]},
             "caliber_adjudication": {
                 "years_for_half": {"state": "FAIL", "median": 2, "line": 3,
                                    "unit": "years"},
                 "effective_years": {"state": "PASS", "median": 4.98, "line": 3}}},
            {"book": "book_flat", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL",
                 "failing_checks": ["Y4_top2_share"],
                 "calibers": {"net_sum_pct": 10.0, "gross_sum_pct": 100.0}}],
             "refusal_survival": {"word": "REFUSAL_SURVIVES_TRUSTED_RULER",
                                  "trusted": ["years_for_half"]},
             "caliber_adjudication": {"years_for_half": {"state": "FAIL", "median": 1,
                                                         "line": 3}}},
            {"book": "book_norec", "phase_rows": [
                {"start": "p1", "verdict": "CONDITIONAL", "failing_checks": []}],
             "refusal_survival": {"word": "REFUSAL_SURVIVES_TRUSTED_RULER",
                                  "trusted": ["years_for_half"]},
             "caliber_adjudication": {}},
        ]})
    f9 = build(receipts=[(pg_elected, "phase_gate")], root=tmp, elected="years_for_half")
    rows9 = {r["candidate"]: r for r in f9["candidates"]}
    check("elected ruler reading carried",
          rows9["book_a"]["trusted_readings"]["years_for_half"],
          {"state": "FAIL", "median": 2, "line": 3, "unit": "years"})
    check("refusal sentence names the elected ruler and its own line",
          rows9["book_a"]["elected_reason"]["sentence"],
          "years_for_half median 2 vs line 3 (FAIL)")
    check("the sentence reaches the operator summary",
          "book_a refused at years_for_half median 2 vs line 3 (FAIL)"
          in summary_line(f9), True)
    check("a flat book prints indeterminate, not a refusal sentence",
          rows9["book_flat"]["elected_reason"]["word"], "indeterminate")
    check("flat book carries no sentence into the summary",
          "book_flat refused" in summary_line(f9), False)
    check("no reading for the elected ruler is named, never guessed",
          rows9["book_norec"]["elected_reason"]["word"], "not_on_record")
    check("the ruler is not pinned to the election's current answer",
          build(receipts=[(pg_elected, "phase_gate")], root=tmp,
                elected="effective_years")["candidates"][0]["elected_reason"]["ruler"],
          "effective_years")
    check("the new block cannot turn a refusal into a pass",
          (f9["verdict"], [r["pass"] for r in f9["candidates"]]),
          ("NO_CANDIDATE_PASSES_CALENDAR", [False, False, False]))
    check("no elected ruler prints no_election, never a sentence",
          build(receipts=[(pg_elected, "phase_gate")], root=tmp,
                elected=None)["candidates"][0]["elected_reason"]["word"], "no_election")

    print("selftest %d/%d PASS" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def check_published(path=None):
    """Re-derive the verdict from the published rows (falsifiability leg)."""
    path = path or OUT_JSON
    if not os.path.exists(path):
        print("supply_calendar_face: no published face at %s" % path)
        return 2
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    want = verdict_of(d.get("candidates") or [],
                      d.get("receipts_unreadable") or [])
    problems = []
    if d.get("verdict") != want:
        problems.append("verdict %r != recomputed %r" % (d.get("verdict"), want))
    for r in d.get("candidates") or []:
        if r.get("pass") != (r.get("state") == PASS_WORD):
            problems.append("%s: pass flag %r != state %r"
                            % (r.get("candidate"), r.get("pass"), r.get("state")))
        # r1432: the printed refusal reason must re-derive from the row itself and
        # the elected ruler the face published -- a hard-coded sentence is red.
        want_reason = elected_reason(r, d.get("elected_ruler")) or {}
        if (r.get("elected_reason") or {}) != want_reason:
            problems.append("%s: elected_reason %r != recomputed %r"
                            % (r.get("candidate"), r.get("elected_reason"), want_reason))
        if (r.get("elected_reason") or {}).get("word") == "refuse" and r.get("pass"):
            problems.append("%s: a refusal sentence on a passing candidate"
                            % r.get("candidate"))
    if problems:
        print("supply_calendar_face: FAIL " + "; ".join(problems))
        return 1
    print("supply_calendar_face: check OK (%s)" % want)
    return 0


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check_published()
    if "run" in argv or len(argv) <= 1:
        face = build()
        face["generated"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z")
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        write_md(face, OUT_MD)
        print("supply_calendar_face: %s" % summary_line(face))
        return 0
    print(__doc__.strip().splitlines()[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))