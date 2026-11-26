#!/usr/bin/env python3
"""How much does the concentration check (Y4) actually weigh?  A census of published books.

The gate publishes two different things for the same year axis and they are easy to
confuse: a *check* (`Y4_top2_share`) and a *word* (`ADMIT` / `CONDITIONAL` / ...).  A book
whose top-2 share is over the line currently loses its `ADMIT` but still keeps its place
on the sheet; whether that is the right weight is a specification question (who holds the
veto), not a reporting question.  This face does not answer it -- it prices it.

Three rules are applied to every book-reading already published by an earlier receipt:

    R0  status quo   the word the producing face printed (Y4 downgrades, it does not veto)
    R1  veto         any book with checks.Y4_top2_share == False loses its place (REFUSE)
    R2  advisory     Y4 is printed and not counted: a book fails only on the checks that
                     are not Y4

Nothing is re-priced or re-run: every input is a number or a word an earlier face already
published, so a difference here is a difference in the rule and in nothing else.

Rules learned the hard way and enforced below:
  * a check whose value is `null` is UNKNOWN, never a pass -- a book with unmeasured
    capacity cannot read as ADMIT under any of the three rules (r98 / E-rest-paid);
  * a book with no `cagr_pct` is named, not summed into a zero (r1772: a missing number is
    not a small one);
  * the count of readings is not the count of books: the same book is published by several
    faces, so both numbers are printed with their denominators.

Usage: python scripts/etf_book_year_gate_vote.py [run|--check|selftest]
  run       census the published faces and publish results/etf_book_year_gate_vote.json
  --check   re-derive from the same faces and compare with the published census
  selftest  offline legs on fixtures, no receipt files needed
"""

from __future__ import annotations

import glob
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

CST = timezone(timedelta(hours=8))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_book_year_gate_vote.json")

Y4 = "Y4_top2_share"

# Canonical faces only.  `_r<round>...json` are per-round chain transcripts (the same book
# counted a hundred times) and `compute_audit*` quotes the check inside a log, so neither
# goes in the census.  The list is explicit so a new face has to be added on purpose.
FACES = [
    "results/etf_book_year_gate/YEAR-GATE.json",
    "results/etf_book_year_gate/WRAPPER-GATE.json",
    "results/etf_book_vt_ladder/VT-LADDER.json",
    "results/etf_book_vt_phases/VT-PHASES.json",
    "results/etf_book_phase_gate.json",
    "results/etf_book_gate_forward/GATE-FORWARD.json",
    "results/etf_book_derisk_rule/DERISK-RULE.json",
    "results/etf_book_sleeve_cap_phases.json",
    "results/etf_book_vol_target_gate.json",
    "results/etf_book_concentration_levers.json",
    "results/etf_book_gate_knobs.json",
    "results/etf_book_scale_floor.json",
    "results/etf_book_gate_causal.json",
    "results/etf_book_admission_eta.json",
    "results/etf_book_year_gate_idlecarry.json",
    "results/etf_book_partial_year_caliber/CALIBER.json",
    "results/etf_book_cut_gate_pass/CUT-GATE-PASS.json",
    "results/etf_book_supply_gate_decision/DECISION.json",
    "results/supply_candidates.json",
    "results/admission/CANDIDATES.json",
]

RULES = ("R0_status_quo", "R1_veto", "R2_advisory")


def _load(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# every face names its rows differently; a row without any of these is published as
# "unnamed" rather than inheriting the previous row's name
NAME_KEYS = ("name", "label", "book", "rung", "candidate", "arm", "window", "id", "key")


def _name_of(node):
    for k in NAME_KEYS:
        v = node.get(k)
        if isinstance(v, str) and v:
            return v
    return None


def collect_readings(face_paths=None, cutoffs=None):
    """Every published dict that carries a Y4 check and a word, with its own path."""
    out = []
    for rel in (face_paths if face_paths is not None else FACES):
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        doc = _load(path)
        if doc is None:
            continue
        if cutoffs is not None and isinstance(doc, dict) and doc.get("evidence_cutoff"):
            cutoffs.append(str(doc["evidence_cutoff"]))
        stack = [(rel, "", doc)]
        while stack:
            where, sub, node = stack.pop()
            if isinstance(node, dict):
                checks = node.get("checks")
                word = node.get("verdict")
                if isinstance(checks, dict) and Y4 in checks and isinstance(word, str):
                    ym = node.get("year_metrics") or {}
                    out.append({
                        "face": where,
                        "at": sub or "/",
                        "book": _name_of(node),
                        "verdict": word,
                        "checks": dict(checks),
                        "cagr_pct": node.get("cagr_pct"),
                        "top2_share": ym.get("top2_share"),
                        "top2_max": node.get("line_top2_share"),
                    })
                for k, v in node.items():
                    if isinstance(v, (dict, list)):
                        stack.append((where, "%s/%s" % (sub, k), v))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    if isinstance(v, (dict, list)):
                        stack.append((where, "%s/%d" % (sub, i), v))
    return out


def other_checks(checks):
    return {k: v for k, v in checks.items() if k != Y4}


def all_true(d):
    """`all(d.values())` is a trap: a null check is not True and not False, it is unknown."""
    return bool(d) and all(v is True for v in d.values())


def words_under(r):
    """The three rules, applied to one published reading."""
    checks = r["checks"]
    y4 = checks.get(Y4)
    others = other_checks(checks)
    pub = r["verdict"]

    r1 = pub
    if y4 is False:
        r1 = "REFUSE"

    r2 = pub
    if y4 is False:
        # only the concentration check objected: with it printed and not counted the book
        # keeps its word -- but never past an unmeasured or failed non-Y4 check
        r2 = "ADMIT" if all_true(others) else pub

    return {"R0_status_quo": pub, "R1_veto": r1, "R2_advisory": r2}


def summarise(readings):
    """Counts and names per rule; the money column is a reading, not a portfolio return."""
    rows = []
    for r in readings:
        w = words_under(r)
        rows.append({
            "face": r["face"],
            "at": r["at"],
            "book": r["book"],
            "published": r["verdict"],
            "checks": r["checks"],
            "top2_share": r["top2_share"],
            "cagr_pct": r["cagr_pct"],
            "words": w,
            "y4_is_the_only_false_check": (r["checks"].get(Y4) is False
                                           and all_true(other_checks(r["checks"]))),
            "y4_unknown": r["checks"].get(Y4) is None,
        })

    rules = {}
    for rule in RULES:
        admitted = [x for x in rows if x["words"][rule] == "ADMIT"]
        changed = [x for x in rows if x["words"][rule] != x["published"]]
        # cagr is quoted per face, never pooled: two faces can print the same number in
        # percent and in fraction (r1775), and pooling them invents a distribution
        by_face = {}
        for x in admitted:
            slot = by_face.setdefault(x["face"], {"n_quoted": 0, "n_missing": 0, "values": []})
            if isinstance(x["cagr_pct"], (int, float)):
                slot["n_quoted"] += 1
                slot["values"].append(float(x["cagr_pct"]))
            else:
                slot["n_missing"] += 1
        for slot in by_face.values():
            vals = sorted(slot.pop("values"))
            slot["min"] = round(vals[0], 4) if vals else None
            slot["median"] = round(vals[len(vals) // 2], 4) if vals else None
            slot["max"] = round(vals[-1], 4) if vals else None
        rules[rule] = {
            "n_admit": len(admitted),
            "n_not_admit": len(rows) - len(admitted),
            "n_changed_vs_published": len(changed),
            "changed": [{"face": x["face"], "at": x["at"], "book": x["book"],
                         "from": x["published"], "to": x["words"][rule],
                         "top2_share": x["top2_share"], "cagr_pct": x["cagr_pct"]}
                        for x in changed],
            "admitted_cagr_by_face": by_face,
        }

    n_y4_false = sum(1 for x in rows if x["checks"].get(Y4) is False)
    n_only = sum(1 for x in rows if x["y4_is_the_only_false_check"])
    names = sorted({x["book"] for x in rows if x["book"]})
    return {
        "n_readings": len(rows),
        "n_distinct_names": len(names),
        "names": names,
        "n_y4_false": n_y4_false,
        "n_y4_unknown": sum(1 for x in rows if x["y4_unknown"]),
        "n_y4_is_the_only_false_check": n_only,
        "n_y4_only_and_published_admit": sum(
            1 for x in rows if x["y4_is_the_only_false_check"] and x["published"] == "ADMIT"),
        "rules": rules,
        "rows": rows,
    }


def build(readings=None):
    cutoffs = []
    readings = collect_readings(cutoffs=cutoffs) if readings is None else readings
    s = summarise(readings)
    now = datetime.now(CST)
    s.update({
        "face": "etf_book_year_gate_vote",
        "question": ("the concentration check downgrades a book instead of refusing it -- "
                     "how many books does the weight of that one vote actually move?"),
        "generated": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": (sorted(cutoffs)[-1] if cutoffs else None),
        "evidence_cutoff_note": ("the newest cutoff among the faces read; the books inside "
                                 "keep their own cutoff, printed in their producing face"),
        "rules_note": {
            "R0_status_quo": "the word the producing face printed",
            "R1_veto": "Y4 False -> REFUSE, whatever the other checks say",
            "R2_advisory": "Y4 printed and not counted; only non-Y4 checks can fail a book",
        },
        "honest": [
            "no engine call and no repricing: every word below is a word an earlier face "
            "already printed, so a difference is a difference in the rule",
            "R2 can only ever promote a book whose every non-Y4 check is True; a book with "
            "an unmeasured (null) check stays where it was, because unknown is not a pass",
            "the cagr column is a reading of the books that would reach ADMIT, not a "
            "portfolio return: they are different books read on different panels",
            "the same book is published by several faces (n_readings > n_distinct_names); "
            "both denominators are printed rather than picking one",
            "no adoption: which rule should hold is a specification question (the weights "
            "and who holds the veto); this page prices the three and ranks none",
        ],
        "sources": [p for p in FACES
                    if os.path.exists(os.path.join(ROOT, p.replace('/', os.sep)))],
    })
    return s


def write(face):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, OUT)
    return face


def check():
    pub = _load(OUT)
    if pub is None:
        print("CHECK_FAIL no published face at %s" % _rel(OUT))
        return 2
    now = build()
    drift = []
    for rule in RULES:
        a, b = pub["rules"][rule], now["rules"][rule]
        for k in ("n_admit", "n_not_admit", "n_changed_vs_published"):
            if a.get(k) != b.get(k):
                drift.append("rules.%s.%s: published=%r re-derived=%r" % (rule, k, a.get(k), b.get(k)))
        if [c["face"] + c["at"] for c in a.get("changed") or []] != \
                [c["face"] + c["at"] for c in b.get("changed") or []]:
            drift.append("rules.%s.changed: the list of books this rule moves differs" % rule)
    for k in ("n_readings", "n_distinct_names", "n_y4_false", "n_y4_is_the_only_false_check"):
        if pub.get(k) != now.get(k):
            drift.append("%s: published=%r re-derived=%r" % (k, pub.get(k), now.get(k)))
    if drift:
        # r2159: the census is only as new as the book faces it reads.  When they moved,
        # these numbers were right for the cut they were taken at -- say STALE, the one word
        # the chain pays a rebuild for, or this face freezes until a human runs it.
        moved = []
        pc, nc = pub.get("evidence_cutoff"), now.get("evidence_cutoff")
        if pc and nc and str(pc) < str(nc):
            moved.append("the faces this census reads moved to %s (this publication was "
                         "cut at %s)" % (nc, pc))
        for m in moved:
            print("STALE " + m)
        for d in drift:
            print("DRIFT " + d)
        if moved:
            print("STALE %d field(s) moved with the upstream -- rerun "
                  "`python scripts/etf_book_year_gate_vote.py`" % len(drift))
        else:
            print("CHECK_FAIL %d field(s) drifted -- rerun "
                  "`python scripts/etf_book_year_gate_vote.py`" % len(drift))
        return 1
    r = now["rules"]
    print("CHECK_OK readings=%d books=%d y4_false=%d y4_only=%d | admit R0=%d R1=%d R2=%d"
          % (now["n_readings"], now["n_distinct_names"], now["n_y4_false"],
             now["n_y4_is_the_only_false_check"], r["R0_status_quo"]["n_admit"],
             r["R1_veto"]["n_admit"], r["R2_advisory"]["n_admit"]))
    return 0


# ------------------------------------------------------------------------- selftest
def _leg(name, cond, ok, tot):
    print("  %s %s" % ("PASS" if cond else "FAIL", name))
    return ok + (1 if cond else 0), tot + 1


def selftest():
    ok = tot = 0

    def R(verdict, checks, cagr=None, name="b"):
        return {"face": "fixture", "at": "/" + name, "book": name, "verdict": verdict,
                "checks": checks, "cagr_pct": cagr, "top2_share": None, "top2_max": None}

    # L1  a book whose only objection is Y4: veto kills it, advisory promotes it
    s = summarise([R("CONDITIONAL", {"Y1": True, "Y4_top2_share": False})])
    w = s["rows"][0]["words"]
    ok, tot = _leg("L1 Y4-only book: R0 conditional / R1 refuse / R2 admit",
                   (w["R0_status_quo"], w["R1_veto"], w["R2_advisory"])
                   == ("CONDITIONAL", "REFUSE", "ADMIT"), ok, tot)

    # L2  a book that already passes everything is untouched by every rule
    s = summarise([R("ADMIT", {"Y1": True, "Y4_top2_share": True})])
    w = s["rows"][0]["words"]
    ok, tot = _leg("L2 clean book: all three rules agree with the printed word",
                   set(w.values()) == {"ADMIT"}, ok, tot)

    # L3  an unmeasured check is not a pass: capacity unknown keeps the book where it is
    s = summarise([R("CONDITIONAL", {"Y1": True, "Y4_top2_share": False, "C1": None})])
    w = s["rows"][0]["words"]
    ok, tot = _leg("L3 unmeasured capacity: R2 does not promote it",
                   w["R2_advisory"] == "CONDITIONAL", ok, tot)

    # L4  a second failing non-Y4 check: the vote is not the decider, and we say so
    s = summarise([R("CONDITIONAL", {"Y1": False, "Y4_top2_share": False})])
    ok, tot = _leg("L4 not alone: y4_is_the_only_false_check is False",
                   s["rows"][0]["y4_is_the_only_false_check"] is False
                   and s["n_y4_is_the_only_false_check"] == 0, ok, tot)

    # L5  the census conserves its own denominator
    s = summarise([R("ADMIT", {"Y4_top2_share": True}, name="a"),
                   R("CONDITIONAL", {"Y4_top2_share": False}, name="b"),
                   R("CONDITIONAL", {"Y4_top2_share": False}, name="c")])
    ok, tot = _leg("L5 counts add up: n_admit + n_not_admit == n_readings for every rule",
                   all(v["n_admit"] + v["n_not_admit"] == s["n_readings"]
                       for v in s["rules"].values()), ok, tot)

    # L6  a missing cagr is named, never summed as zero
    s = summarise([R("ADMIT", {"Y4_top2_share": True}, cagr=9.0, name="a"),
                   R("ADMIT", {"Y4_top2_share": True}, cagr=None, name="b")])
    c = s["rules"]["R0_status_quo"]["admitted_cagr_by_face"]["fixture"]
    ok, tot = _leg("L6 money column: n_quoted 1 / n_missing 1, median from the quoted one",
                   (c["n_quoted"], c["n_missing"], c["median"]) == (1, 1, 9.0), ok, tot)

    # L6b two faces printing the same statistic in percent and in fraction are never pooled
    s = summarise([R("ADMIT", {"Y4_top2_share": True}, cagr=15.51, name="a"),
                   dict(R("ADMIT", {"Y4_top2_share": True}, cagr=0.155, name="b"), face="other")])
    bf = s["rules"]["R0_status_quo"]["admitted_cagr_by_face"]
    ok, tot = _leg("L6b no pooling across faces: two faces, two medians (15.51 and 0.155)",
                   sorted((bf["fixture"]["median"], bf["other"]["median"])) == [0.155, 15.51],
                   ok, tot)

    # L7  the same book read by two faces counts twice in readings, once in names
    s = summarise([R("ADMIT", {"Y4_top2_share": True}, name="a"),
                   dict(R("ADMIT", {"Y4_top2_share": True}, name="a"), face="other")])
    ok, tot = _leg("L7 two denominators: n_readings 2, n_distinct_names 1",
                   (s["n_readings"], s["n_distinct_names"]) == (2, 1), ok, tot)

    # L8  a changed list is not a changed count: R1 names the book it moves
    s = summarise([R("CONDITIONAL", {"Y4_top2_share": False}, name="x")])
    ch = s["rules"]["R1_veto"]["changed"]
    ok, tot = _leg("L8 change list: R1 moves x from CONDITIONAL to REFUSE",
                   len(ch) == 1 and ch[0]["book"] == "x" and ch[0]["to"] == "REFUSE", ok, tot)

    # L9  no faces on disk is not a pass -- the census says it read nothing
    s = summarise([])
    ok, tot = _leg("L9 empty census: zero readings, every rule zero, no invented book",
                   s["n_readings"] == 0 and all(v["n_admit"] == 0 for v in s["rules"].values()),
                   ok, tot)

    print("selftest %d/%d %s" % (ok, tot, "ALL PASS" if ok == tot else "FAILED"))
    return 0 if ok == tot else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    mode = argv[0] if argv else "run"
    if mode == "selftest":
        return selftest()
    if mode == "--check":
        return check()
    if mode in ("run", "refresh"):
        face = write(build())
        r = face["rules"]
        print("PUBLISHED readings=%d books=%d y4_false=%d y4_only=%d | admit R0=%d R1=%d R2=%d -> %s"
              % (face["n_readings"], face["n_distinct_names"], face["n_y4_false"],
                 face["n_y4_is_the_only_false_check"], r["R0_status_quo"]["n_admit"],
                 r["R1_veto"]["n_admit"], r["R2_advisory"]["n_admit"], _rel(OUT)))
        return 0
    print("usage: python scripts/etf_book_year_gate_vote.py [run|--check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
