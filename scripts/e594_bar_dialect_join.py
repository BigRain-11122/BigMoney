# -*- coding: utf-8 -*-
"""E594 -- can the bar be joined across the dialects E586 counted, without a hand map?

E586 (r1621) closed the consumer-side question -- zero silent readers, zero money-carrying surfaces
that omit the bar -- and left one residue: the bar is spelled ``pricing_bar`` on some surfaces,
``ticket_bar``/``evidence_cutoff`` on others, ``as_of`` on the pointer face a follow-up page reads,
and in prose on the human ORDER page.  A reader that asks for a spelling the face it reads does not
carry gets ``None`` and looks exactly like a reader that read a bar and found nothing there.

This study takes E586's reader population (imported, not re-typed) and answers, per reader:

  spellings   which dialect(s) the reader's own string literals use to obtain the bar, grouped
              into families (pricing / decision / evidence_cutoff / as_of);
  targets     which published face(s) the reader names -- resolved from its literals to files that
              exist on disk, so a reader whose literals are only name fragments is published as
              unresolved rather than counted as a silent join;
  joins       for each (reader, spelling, target) the study asks the target's own payload whether
              it carries that spelling, and publishes the pair as carried / not carried / unknown
              (a target that is not JSON, or a spelling the reader never spells).

The verdict is about the class, not one reader: if every reader's spelling is carried by the face
it reads, a consumer needs no hand map; if some reader asks for a spelling that face does not carry,
that join silently returns nothing.

Read-only: no ticket, ledger, panel or face is written except this study's own output.

Honest limits (published in the face, not in a footnote):

  * name matching cannot prove a reader's join *runs* -- a literal may be used to build a path, to
    log, or in a docstring; the pair is published with the literal that produced it;
  * a reader that names several faces has several targets and the join is per pair, so "carried" is
    never a statement about the reader as a whole;
  * a spelling used by a reader with no resolved target is ``unresolved``, which is not evidence of
    a broken join -- it is evidence that this instrument cannot see the join.

  python scripts/e594_bar_dialect_join.py build
  python scripts/e594_bar_dialect_join.py check
  python scripts/e594_bar_dialect_join.py verify
  python scripts/e594_bar_dialect_join.py selftest

Output: results/state_tilt/BARDIALECTJOIN.json (+ BARDIALECTJOIN-latest.json)
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e586_ticket_reader_bar as e586                                    # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "BARDIALECTJOIN.json")
SELF_NAME = "e594_bar_dialect_join.py"

# spelling families: a reader in one family asks the payload for one of these names
SPELLINGS = {
    "pricing": sorted(e586.PRICING_BAR_FIELDS),
    "decision": sorted(e586.DECISION_BAR_FIELDS),
    "evidence_cutoff": sorted(e586.CUTOFF_FIELDS),
    "as_of": ["as_of", "asof", "as_of_date", "bar_date", "ticket_bar"],
}

CANDIDATE_GLOBS = [
    "results/etf_book_order/*.json",
    "results/etf_book_order/*.md",
    "results/dashboard_status.json",
    "results/paper_export/latest.json",
    "docs/live_usage/LIVE-latest.json",
    "results/state_tilt/*TICKET*.json",
]

V_SOME_SILENT = "some_reader_asks_for_a_spelling_the_face_it_reads_does_not_carry"
V_ALL_CARRIED = "every_reader_spelling_is_carried_by_at_least_one_face_it_reads"
V_NO_JOIN_SEEN = "no_reader_resolves_to_a_published_face"
V_NO_READER = "no_in_repo_reader_addresses_a_ticket"


# --------------------------------------------------------------------------- pure helpers
def spelling_families(literals):
    """Which dialect families this module's literals spell, and with which names."""
    lits = set(literals)
    out = {}
    for fam, names in SPELLINGS.items():
        hit = sorted(lits & set(names))
        if hit:
            out[fam] = hit
    return out


def basename_of(literal):
    """The file part of a literal, whichever separator (and quoting) it carries."""
    if not isinstance(literal, str):
        return ""
    return literal.replace("\\", "/").rstrip("/").split("/")[-1]


def face_index(root):
    """basename -> absolute path for the bounded published-face candidate set."""
    idx = {}
    for pat in CANDIDATE_GLOBS:
        for p in glob.glob(os.path.join(root, pat)):
            idx.setdefault(os.path.basename(p), os.path.abspath(p))
    return idx


def resolve_targets(literals, idx, self_names):
    """(targets, unresolved_literals) for one reader's literals."""
    targets, unresolved = {}, []
    for lit in sorted(set(literals)):
        if not isinstance(lit, str) or len(lit) > 300:
            continue
        b = basename_of(lit)
        if not b or b in self_names:
            continue
        if b.startswith(("TICKET-", "ORDER-")) or b.endswith((".json", ".md")):
            if b in idx:
                targets[idx[b]] = b
            elif e586.FAMILY_DIR_LITERAL in lit or "TICKET-" in lit or "ORDER-" in lit:
                unresolved.append(lit)
    return targets, unresolved


def face_keys(path):
    """(carrier key set, kind) for one published face; ({}, 'text') when not JSON."""
    if not path.lower().endswith(".json"):
        return set(), "text"
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            payload = json.load(f)
    except (ValueError, OSError):
        return set(), "unreadable"
    return e586.walk_keys(payload), "json"


def join_pairs(reader, targets, keys_by_path, text_by_path):
    """One row per (spelling family the reader uses, target it names)."""
    pairs = []
    for fam, names in sorted(reader["spellings"].items()):
        if not targets:
            pairs.append({"reader": reader["module"], "spelling": fam, "names": names,
                          "target": None, "outcome": "unresolved"})
            continue
        for path, base in sorted(targets.items()):
            keys, kind = keys_by_path[path]
            if kind == "json":
                carried = sorted(set(names) & keys)
                outcome = "carried" if carried else "not_carried"
            elif kind == "text":
                text = text_by_path.get(path, "")
                carried = [n for n in names if n in text]
                outcome = "carried_in_text" if carried else "not_carried_in_text"
            else:
                carried, outcome = [], "unknown"
            pairs.append({"reader": reader["module"], "spelling": fam, "names": names,
                          "target": base, "outcome": outcome,
                          "carried_names": carried})
    return pairs


def count_pairs(pairs, readers, n_faces=0):
    """Two arms: per PAIR (broad) and per READER (deciding).

    A module that names many faces -- the smoke suite names nearly every published file -- crosses
    each of its spellings with each of its targets, and most of those cross products were never a
    join.  A reader is therefore counted silent only when EVERY one of its (spelling, target) pairs
    fails: a reader that can obtain the bar from at least one face it names is not silent, however
    many of its combinations miss.  The pair-level count is published beside it so the breadth of
    the wiring is visible rather than hidden behind the deciding number.
    """
    by_outcome = {}
    for p in pairs:
        by_outcome[p["outcome"]] = by_outcome.get(p["outcome"], 0) + 1
    failing = sorted({p["reader"] for p in pairs
                      if p["outcome"] in ("not_carried", "not_carried_in_text")})
    carried = sorted({p["reader"] for p in pairs
                      if p["outcome"] in ("carried", "carried_in_text")})
    all_fail = sorted(set(failing) - set(carried))
    resolved = sorted({p["reader"] for p in pairs if p["target"]})
    by_spelling = {}
    for p in pairs:
        b = by_spelling.setdefault(p["spelling"], {})
        b[p["outcome"]] = b.get(p["outcome"], 0) + 1
    return {
        "readers": len(readers),
        "readers_with_a_resolved_target": len(resolved),
        "readers_with_no_resolved_target": len(readers) - len(resolved),
        "candidate_faces": n_faces,
        "pairs": len(pairs),
        "pairs_by_outcome": dict(sorted(by_outcome.items())),
        "pairs_by_spelling": {k: dict(sorted(v.items())) for k, v in sorted(by_spelling.items())},
        "readers_with_at_least_one_carried_pair": len(carried),
        "pairs_joining_a_spelling_the_face_lacks": sum(
            1 for p in pairs if p["outcome"] in ("not_carried", "not_carried_in_text")),
        "readers_joining_a_spelling_the_face_lacks": len(failing),
        "silent_join_readers": all_fail,
    }


def spelling_carriers(keys_by_path, text_by_path):
    """Per spelling family, which published faces carry at least one of its names."""
    out = {}
    for fam, names in SPELLINGS.items():
        carriers, dater_only = [], []
        for path in sorted(keys_by_path):
            keys, kind = keys_by_path[path]
            base = os.path.basename(path)
            if kind == "json" and set(names) & keys:
                carriers.append(base)
            elif kind == "text" and any(n in text_by_path.get(path, "") for n in names):
                carriers.append(base)
        out[fam] = {"names": names, "carried_by": carriers, "carrier_count": len(carriers)}
    universals = [fam for fam, v in out.items() if v["carrier_count"] == len(keys_by_path)]
    return out, sorted(universals)


def verdict_from(counts):
    if not counts.get("readers"):
        return V_NO_READER
    if not counts.get("readers_with_a_resolved_target"):
        return V_NO_JOIN_SEEN
    if counts.get("silent_join_readers"):
        return V_SOME_SILENT
    return V_ALL_CARRIED


def answer_sentence(counts, carriers, universals):
    return (
        "Of %d readers that address a ticket, %d name a published face this census can resolve and "
        "%d name only fragments. They spell the bar in %d dialect(s): %s. Across the %d candidate "
        "faces no single spelling is carried by all of them%s, so a consumer cannot join on one "
        "name. %d of %d graded (reader, spelling, face) pairs miss -- and %d reader(s) miss on EVERY "
        "pair they can make, which is the class where the join silently returns nothing: %s. %d "
        "reader(s) can obtain the bar from at least one face they name."
        % (counts["readers"], counts["readers_with_a_resolved_target"],
           counts["readers_with_no_resolved_target"], len(carriers),
           ", ".join("%s(%d)" % (k, v["carrier_count"]) for k, v in carriers.items()),
           counts["candidate_faces"],
           "" if universals else " (no universal spelling)",
           counts["pairs_joining_a_spelling_the_face_lacks"], counts["pairs"],
           len(counts["silent_join_readers"]),
           ", ".join(counts["silent_join_readers"]) or "none",
           counts["readers_with_at_least_one_carried_pair"]))


# --------------------------------------------------------------------------- build
def reader_rows():
    paths = sorted(glob.glob(e586.TICKET_GLOB))
    bar, ticket = e586.newest_ticket(paths)
    if ticket is None:
        return None, None, []
    keys = e586.walk_keys(ticket)
    base_rows = e586.reader_rows(keys)[0]
    idx = face_index(ROOT)
    self_names = {os.path.basename(OUT_PATH), "BARDIALECTJOIN-latest.json", SELF_NAME}
    facts = {}
    rows = []
    for r in base_rows:
        mod = r["module"]
        if mod.endswith(SELF_NAME):
            continue        # this study's own literals are the spelling table, not a join
        if mod not in facts:
            path = os.path.join(ROOT, mod)
            try:
                src = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                src = ""
            facts[mod] = e586.module_facts(src)[0] if src else set()
        lits = facts[mod]
        targets, unresolved = resolve_targets(lits, idx, self_names)
        row = dict(r)
        row["spellings"] = spelling_families(lits)
        row["targets"] = sorted(set(targets.values()))
        row["unresolved_ticket_literals"] = unresolved[:5]
        rows.append(row)
    return bar, ticket, rows


def build(write=True):
    bar, ticket, rows = reader_rows()
    if ticket is None:
        face = {"study": "E594_bar_dialect_join", "verdict": V_NO_JOIN_SEEN,
                "answer": "no ticket on disk; nothing to measure", "evidence_cutoff": None}
        if write:
            write_face(face)
        return face

    idx = face_index(ROOT)
    keys_by_path, text_by_path = {}, {}
    for base, path in sorted(idx.items()):
        k, kind = face_keys(path)
        keys_by_path[path] = (k, kind)
        if kind == "text":
            try:
                text_by_path[path] = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                text_by_path[path] = ""

    pairs = []
    for r in rows:
        targets = {idx[b]: b for b in r["targets"] if b in idx}
        pairs.extend(join_pairs(r, targets, keys_by_path, text_by_path))
    counts = count_pairs(pairs, rows, len(keys_by_path))
    carriers, universals = spelling_carriers(keys_by_path, text_by_path)

    face = {
        "study": "E594_bar_dialect_join",
        "evidence_cutoff": ticket.get("evidence_cutoff") or bar,
        "ticket": {"bar": bar,
                   "path": "results/etf_book_order/TICKET-%s.json" % bar,
                   "pricing_bar": ticket.get("pricing_bar"),
                   "book_decided_at": ticket.get("book_decided_at")},
        "spelling_families": {k: v for k, v in SPELLINGS.items()},
        "candidate_faces": sorted(os.path.relpath(p, ROOT).replace(os.sep, "/")
                                  for p in keys_by_path),
        "spelling_carrier_census": carriers,
        "spellings_carried_by_every_candidate": universals,
        "readers": rows,
        "joins": pairs,
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, carriers, universals),
        "limits": [
            "a name match cannot prove the join runs; each pair carries the literal family that "
            "produced it",
            "a reader with no resolved target is 'unresolved', which is not evidence of a broken "
            "join but of an instrument that cannot see it",
            "text faces are graded by name occurrence, so prose that never names the field is "
            "counted as not carrying it",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, "BARDIALECTJOIN-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


# --------------------------------------------------------------------------- guard
REQUIRED_READER_KEYS = ("module", "addressing", "spellings", "targets",
                        "unresolved_ticket_literals", "strict_notional_fields")
REQUIRED_PAIR_KEYS = ("reader", "spelling", "names", "target", "outcome")


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    rows = face.get("readers") or []
    pairs = face.get("joins") or []
    counts = face.get("counts") or {}
    if not rows:
        p.append("no reader rows are published")
    if not pairs:
        p.append("no join pairs are published")
    for r in rows:
        missing = [k for k in REQUIRED_READER_KEYS if k not in r]
        if missing:
            p.append("reader row %s lacks %s" % (r.get("module"), ",".join(missing)))
            break
        if not r.get("addressing"):
            p.append("reader row %s does not say how it addresses a ticket" % r.get("module"))
            break
    for q in pairs:
        missing = [k for k in REQUIRED_PAIR_KEYS if k not in q]
        if missing:
            p.append("join pair %s/%s lacks %s" % (q.get("reader"), q.get("spelling"),
                                                   ",".join(missing)))
            break
        if q["outcome"] in ("carried", "not_carried") and not q.get("target"):
            p.append("join pair %s/%s grades a face it does not name"
                     % (q["reader"], q["spelling"]))
            break
    want = count_pairs(pairs, rows, len(face.get("candidate_faces") or []))
    for k, v in want.items():
        if counts.get(k) != v:
            p.append("count %s is %r but re-derives to %r" % (k, counts.get(k), v))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    cur = face.get("spelling_carrier_census") or {}
    for fam in SPELLINGS:
        if fam not in cur:
            p.append("the carrier census omits the %s dialect" % fam)
            break
        if cur[fam].get("carrier_count") != len(cur[fam].get("carried_by") or []):
            p.append("carrier count for %s does not equal its carrier list" % fam)
            break
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # leg1 dialect families split by name, not by one hand map
    fam = spelling_families({"pricing_bar", "evidence_cutoff", "as_of", "nav"})
    chk("leg1 three dialects are read off the literals and 'nav' is not a bar",
        set(fam) == {"pricing", "evidence_cutoff", "as_of"} and "nav" not in json.dumps(fam), fam)
    chk("leg1b a ticket_bar literal lands in the as_of family, not pricing",
        "ticket_bar" in spelling_families({"ticket_bar"})["as_of"])
    chk("leg1c a pricing_bar literal does not land in as_of",
        "as_of" not in spelling_families({"pricing_bar"}))

    # leg2 target resolution
    idx = {"latest.json": "/x/results/etf_book_order/latest.json"}
    tg, un = resolve_targets({"results/etf_book_order/latest.json", "TICKET-2026-11-06.json",
                              "results/etf_book_order/"}, idx, {"BARDIALECTJOIN.json"})
    chk("leg2 a named file that exists resolves as a target",
        "/x/results/etf_book_order/latest.json" in tg, tg)
    chk("leg2b a file literal that does not exist is not invented as a target",
        "TICKET-2026-11-06.json" not in tg.values(), tg)
    chk("leg2c a ticket-named literal with no file is published as unresolved",
        "TICKET-2026-11-06.json" in un, un)

    # leg3 the join grades a payload by the keys it carries
    keys = {"pricing_bar", "nav", "as_of"}
    r = {"module": "a.py", "spellings": {"pricing": ["pricing_bar"], "as_of": ["as_of"]}}
    pairs = join_pairs(r, {"/x/f.json": "f.json"},
                       {"/x/f.json": (keys, "json")}, {})
    chk("leg3 a spelling the face carries is 'carried'",
        any(p["outcome"] == "carried" and p["spelling"] == "pricing" for p in pairs), pairs)

    # leg4 the silent case: spelling the face does not carry
    r2 = {"module": "b.py", "spellings": {"evidence_cutoff": ["evidence_cutoff"]}}
    pairs2 = join_pairs(r2, {"/x/f.json": "f.json"}, {"/x/f.json": (keys, "json")}, {})
    cnt2 = count_pairs(pairs2, [r2])
    chk("leg4 asking for evidence_cutoff of a face that carries as_of is not_carried",
        pairs2[0]["outcome"] == "not_carried", pairs2)
    chk("leg4b that reader is counted as a silent join",
        cnt2["readers_joining_a_spelling_the_face_lacks"] == 1
        and cnt2["silent_join_readers"] == ["b.py"], cnt2)
    chk("leg4c the verdict follows those counts",
        verdict_from(cnt2) == V_SOME_SILENT, cnt2)
    chk("leg4d both arms are published: the failing pair and the all-failing reader",
        cnt2["pairs_joining_a_spelling_the_face_lacks"] == 1
        and cnt2["readers_joining_a_spelling_the_face_lacks"] == 1, cnt2)

    # leg4e the deciding arm: a wide reader that misses on one pair but hits on another is NOT silent
    wide = {"module": "wide.py", "spellings": {"pricing": ["pricing_bar"],
                                               "evidence_cutoff": ["evidence_cutoff"]}}
    wpairs = join_pairs(wide, {"/x/f.json": "f.json"}, {"/x/f.json": (keys, "json")}, {})
    wcnt = count_pairs(wpairs, [wide])
    chk("leg4e a reader that can obtain the bar from one face is not a silent joiner",
        wcnt["pairs_joining_a_spelling_the_face_lacks"] == 1
        and wcnt["silent_join_readers"] == []
        and wcnt["readers_with_at_least_one_carried_pair"] == 1, wcnt)
    chk("leg4f and that population grades ALL_CARRIED, not silent",
        verdict_from(wcnt) == V_ALL_CARRIED, wcnt)

    # leg5 unresolved is a distinct outcome, never a silent join
    r3 = {"module": "c.py", "spellings": {"pricing": ["pricing_bar"]}}
    pairs3 = join_pairs(r3, {}, {}, {})
    cnt3 = count_pairs(pairs3, [r3])
    chk("leg5 a reader with no resolved target is 'unresolved'",
        pairs3[0]["outcome"] == "unresolved" and pairs3[0]["target"] is None, pairs3)
    chk("leg5b unresolved does not count as a silent join",
        cnt3["readers_joining_a_spelling_the_face_lacks"] == 0, cnt3)
    chk("leg5c a population with no resolved target has its own verdict",
        verdict_from(cnt3) == V_NO_JOIN_SEEN, cnt3)

    # leg6 carried-in-text and the universal test
    text = "priced on 2026-11-06 and decided 2026-10-14 evidence_cutoff 2026-11-06"
    r4 = {"module": "d.py", "spellings": {"evidence_cutoff": ["evidence_cutoff"]}}
    pairs4 = join_pairs(r4, {"/x/ORDER.md": "ORDER.md"}, {"/x/ORDER.md": (set(), "text")},
                        {"/x/ORDER.md": text})
    chk("leg6 a text face carries a spelling by name occurrence",
        pairs4[0]["outcome"] == "carried_in_text", pairs4)
    carriers, uni = spelling_carriers({"/x/f.json": (keys, "json")}, {})
    chk("leg6b a spelling no face carries has an empty carrier list",
        carriers["decision"]["carrier_count"] == 0, carriers["decision"])
    chk("leg6c on one face the dialects it carries are universal and the ones it lacks are not",
        uni == ["as_of", "pricing"] and "evidence_cutoff" not in uni, uni)
    carriers2, uni2 = spelling_carriers(
        {"/x/f.json": ({"as_of"}, "json"), "/x/g.json": ({"pricing_bar"}, "json")}, {})
    chk("leg6d with two faces carrying different dialects there is no universal spelling",
        uni2 == [], (carriers2, uni2))

    # leg7 the guard refuses hand-written counts, a verdict that contradicts them, and a pair
    #      that grades a face it never names
    rows = [{"module": "a.py", "addressing": ["ticket_literal"],
             "spellings": {"pricing": ["pricing_bar"]}, "targets": ["f.json"],
             "unresolved_ticket_literals": [], "strict_notional_fields": ["nav"]},
            {"module": "b.py", "addressing": ["family_dir"],
             "spellings": {"evidence_cutoff": ["evidence_cutoff"]}, "targets": ["f.json"],
             "unresolved_ticket_literals": [], "strict_notional_fields": ["cash_amount"]}]
    prs = join_pairs({"module": "a.py", "spellings": {"pricing": ["pricing_bar"]}},
                     {"/x/f.json": "f.json"}, {"/x/f.json": (keys, "json")}, {})
    prs += join_pairs({"module": "b.py", "spellings": {"evidence_cutoff": ["evidence_cutoff"]}},
                      {"/x/f.json": "f.json"}, {"/x/f.json": (keys, "json")}, {})
    cnts = count_pairs(prs, rows)
    car, uni3 = spelling_carriers({"/x/f.json": (keys, "json")}, {})
    face = {"readers": rows, "joins": prs, "counts": dict(cnts),
            "verdict": verdict_from(cnts), "answer": "x",
            "spelling_carrier_census": car}
    chk("leg7 the guard accepts a face whose counts re-derive", face_problems(face) == [],
        face_problems(face))
    bad = json.loads(json.dumps(face))
    bad["counts"]["readers_joining_a_spelling_the_face_lacks"] = 0
    chk("leg7b the guard refuses a silent count that does not re-derive",
        any("readers_joining" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(face))
    bad2["verdict"] = V_ALL_CARRIED
    chk("leg7c the guard refuses a verdict that contradicts the pairs",
        any("verdict does not follow" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(face))
    bad3["joins"][0]["target"] = None
    chk("leg7d the guard refuses a graded pair with no face named",
        any("grades a face it does not name" in s for s in face_problems(bad3)),
        face_problems(bad3))
    bad4 = json.loads(json.dumps(face))
    bad4["spelling_carrier_census"]["pricing"]["carrier_count"] = 99
    chk("leg7e the guard refuses a carrier count that disagrees with its list",
        any("carrier count" in s for s in face_problems(bad4)), face_problems(bad4))

    # leg8 basename handling of both separators, and the answer sentence carries its numbers
    chk("leg8 a windows-separated literal yields the same basename",
        basename_of("results\\etf_book_order\\latest.json") == "latest.json"
        and basename_of("results/etf_book_order/latest.json") == "latest.json")
    ans = answer_sentence(cnts, car, uni3)
    chk("leg8b the answer names the silent readers it counted",
        "b.py" in ans and "2" in ans, ans[:160])

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face = build(write=True)
        pr = face_problems(face)
        print("built %s | verdict=%s"
              % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        face = build(write=False)
        pr = face_problems(face)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh = build(write=False)
        keys = ("ticket", "readers", "joins", "counts", "verdict",
                "spelling_carrier_census", "spellings_carried_by_every_candidate")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))