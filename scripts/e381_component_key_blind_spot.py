"""E381 -- why the upstream reader census misses a literal read, and whether that is one defect.

The card: ``scripts/etf_book_bridge.py:369`` reads ``results/etf_book_production/latest.json``
through ``json.load(open(os.path.join(OUT_DIR, "etf_book_production", "latest.json")))``, and every
operand of that join folds to a string (``OUT_DIR`` is ``results``), so by E377's own vocabulary the
site is inside the census universe (literal / bound_constant / joined_constants).  Yet E377 published
that face among the faces "no resolved sink keys".  One of the two is wrong.

It is the census, and not where the card guessed.  The operands DO fold; the loss happens one step
later:

  * ``e347.values_in`` on a ``join`` call returns the operands as SEPARATE values (``results``,
    ``etf_book_production``, ``latest.json``) -- the shape an enumeration scope wants, because only
    the trailing components name a directory (E344);
  * ``e350._face_bindings`` then keeps the values that end in ``.json`` and runs ``_face_key`` on
    each one ALONE, so a three-component path is keyed as ``latest.json``;
  * ``_face_key`` falls back to the basename when no top-level root survives (it says so: "the
    unsafe direction"), and ``latest.json`` merges with any other bare ``latest.json`` read.

So the face is not unread; it is keyed under a name that is not its path.  This face measures the
bill: re-key one joined path from its own operands and ask which published faces stop being unkeyed.

The E377 face is read as published, never rebuilt; nothing here rewrites E350/E353/E368/E377.

Usage:
  python scripts/e381_component_key_blind_spot.py run       # build the face
  python scripts/e381_component_key_blind_spot.py verify    # re-derive the arithmetic
  python scripts/e381_component_key_blind_spot.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "COMPONENTKEY-%s.json" % TODAY
LATEST = "componentkey_latest.json"
UPSTREAM = "unresolveddest_latest.json"
STUDY = "E381_component_key_blind_spot"
SELF_REL = "scripts/e381_component_key_blind_spot.py"
CARD_SOURCE = "scripts/etf_book_bridge.py"
CARD_FACE = "results/etf_book_production/latest.json"
MAX_ROWS = 400

STATUS_MOVED = "unkeyed_only_because_the_join_was_keyed_by_its_operands"
STATUS_STANDS = "keyed_by_no_resolved_site_under_either_keying"

REASON_BASENAME = "the_published_keying_names_it_by_its_basename_only"
REASON_SUFFIX = "the_published_keying_never_names_it_because_both_helpers_accept_only_._json"
REASON_NO_SITE = "the_published_keying_never_names_it_and_no_suffix_rule_explains_that"

V_COMPONENT = ("the_census_keys_a_join_by_its_operands_so_a_read_through_os_path_join_lands_under_a_"
               "bare_basename_and_a_face_that_is_read_is_reported_as_having_no_reader")
V_NO_DEFECT = ("every_face_the_census_reports_unkeyed_is_keyed_by_no_resolved_site_under_either_"
               "keying_so_that_report_stands")
V_UNCOUNTED = ("the_joined_keying_names_faces_the_published_one_misses_but_none_of_them_is_on_the_"
               "published_blind_spot_list_so_the_defect_costs_no_published_number")
V_EMPTY = "the_corpus_named_no_face_under_a_joined_key_so_no_claim_is_made"

# Tokens that travel in a join call's value list but are not path segments: the encoding keyword of
# ``open(p, encoding="utf-8")`` and a bare open mode.  Dropping them is not cosmetic -- leaving
# "utf-8" in the tail would make the joined key end in a non-face component.
NOT_PATH = frozenset(("utf-8", "utf8", "utf_8", "gbk", "gb2312", "latin-1", "ascii",
                      "r", "w", "rb", "wb", "a", "ab", "r+", "w+", "a+"))


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ the key, both ways

def _is_path_component(value):
    """A join operand that is part of a path, as opposed to an encoding or a file mode."""
    if not isinstance(value, str) or not value.strip():
        return False
    if value.lower() in NOT_PATH or value in NOT_PATH:
        return False
    if value.endswith((".json", ".jsonl")):
        return True
    # A directory component: no extension, no separator, no whitespace.  Deliberately narrow --
    # a component this refuses costs a face its joined key, which under-reports the defect rather
    # than inventing one.
    return "." not in value and "/" not in value and " " not in value


def joined_key(values):
    """The face key of one load call's value list, when its operands are joined into one path.

    Returns ``None`` when the list carries no face component at all, so a bare
    ``json.load(open("flags.json"))`` is not credited with a path it never had.
    """
    parts = [v for v in values if _is_path_component(v)]
    if not any(p.endswith((".json", ".jsonl")) for p in parts):
        return None
    return e350._face_key("/".join(p.strip("/") for p in parts))


def published_keying(tree, consts):
    """The E377 keying, reproduced exactly: face keys from resolved dump sinks and load bindings."""
    keys = set()
    try:
        sinks = e350._dump_sinks(tree, consts)
    except Exception:  # noqa: BLE001 -- a helper that fails on one source names no key for it
        sinks = {}
    try:
        bindings, _unresolved = e350._face_bindings(tree, consts)
    except Exception:  # noqa: BLE001
        bindings = {}
    for faces in list(sinks.values()) + list(bindings.values()):
        keys |= set(faces)
    return keys


def scan(sources):
    """One pass: the published key set, the joined key set, and the per-row evidence."""
    published, joined = set(), set()
    sites = {}
    parsed = 0
    load_rows = 0
    for rel, text in sources:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        parsed += 1
        consts = e347.constants(tree)
        published |= published_keying(tree, consts)
        for row in e347.load_bindings(tree, consts):
            key = joined_key(row["values"])
            if key:
                joined.add(key)
                # The site is published beside the key: a face list without the line that named
                # it is a decree, and this study's whole complaint is about keys standing in for
                # the thing they key.
                sites.setdefault(key, []).append("%s:%d %s" % (rel, row["line"], row["values"]))
            load_rows += 1
    return {"published": published, "joined": joined, "sites": sites,
            "parsed": parsed, "load_rows": load_rows}


def _is_face(path):
    return path.endswith((".json", ".jsonl"))


def _exists(key):
    return os.path.exists(os.path.join(ROOT, key))


def classify_targets(targets, published, joined):
    """One row per published blind-spot face: which keying names it, if any, and why not."""
    rows = []
    for face in targets:
        reason = None
        if face in published:
            status = "contradiction_published_keying_names_it_after_all"
        elif face in joined:
            status = STATUS_MOVED
            reason = why_not_published(face, published)
        else:
            status = STATUS_STANDS
        rows.append({"face": face, "status": status, "reason": reason,
                     "published_keying": face in published,
                     "joined_keying": face in joined})
    return rows


def why_not_published(face, published):
    """Why the published keying does not name a face the joined keying does.

    Two causes, and they are different repairs: a basename-only key means the key projection threw
    the path away, while a total absence on a ``.jsonl`` face means the suffix filter never let the
    value in.  Rolling them into one count would have said "component keying hides 12 faces".
    """
    if face.rsplit("/", 1)[-1] in published:
        return REASON_BASENAME
    if face.endswith(".jsonl"):
        return REASON_SUFFIX
    return REASON_NO_SITE


# ------------------------------------------------------------------ evidence for the card's site

def bridge_evidence():
    """The named site: which binding, which values, which key under each keying."""
    path = os.path.join(ROOT, CARD_SOURCE)
    if not os.path.exists(path):
        return {"source": CARD_SOURCE, "present": False}
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    tree = ast.parse(text)
    consts = e347.constants(tree)
    rows = []
    for row in e347.load_bindings(tree, consts):
        key = joined_key(row["values"])
        if not key:
            continue
        one = {"line": row["line"], "binding": row["binding"],
               "values": row["values"], "joined_key": key,
               "published_keys": sorted({e350._face_key(v) for v in row["values"]
                                         if str(v).endswith(".json")})}
        rows.append(one)
    card = next((r for r in rows if r["joined_key"] == CARD_FACE), None)
    return {"source": CARD_SOURCE, "present": True,
            "literal_in_source": CARD_FACE.rsplit("/", 1)[-1] in text,
            "face_exists_on_disk": os.path.exists(os.path.join(ROOT, CARD_FACE)),
            "load_rows": rows[:20],
            "card_row": card,
            "card_crosses_the_two_keyings": bool(card) and CARD_FACE not in card["published_keys"]}


# ------------------------------------------------------------------ build

def decide(summary):
    if not summary.get("joined_keys"):
        return V_EMPTY
    moved = summary.get("upstream_targets_moved") or 0
    if moved:
        return V_COMPONENT
    if summary.get("joined_only_faces"):
        return V_UNCOUNTED
    return V_NO_DEFECT


def build(write_face=True):
    srcs = [(rel, text) for rel, text in e350._sources() if rel != SELF_REL]
    say("corpus: %d sources" % len(srcs))
    result = scan(srcs)
    published, joined = result["published"], result["joined"]
    say("published keys %d | joined keys %d | load rows %d"
        % (len(published), len(joined), result["load_rows"]))

    up_path = os.path.join(OUTDIR, UPSTREAM)
    upstream = {}
    if os.path.exists(up_path):
        with io.open(up_path, encoding="utf-8") as fh:
            upstream = json.load(fh)
    targets = upstream.get("faces_no_census_keys") or []
    rows = classify_targets(targets, published, joined)
    moved = [r for r in rows if r["status"] == STATUS_MOVED]
    say("E377 blind-spot faces: %d | moved under a joined key: %d" % (len(rows), len(moved)))

    joined_only = sorted(k for k in joined - published if _is_face(k) and _exists(k))
    by_reason = {}
    for k in joined_only:
        by_reason.setdefault(why_not_published(k, published), []).append(k)
    say("faces named only by the joined keying and present on disk: %d (%s)"
        % (len(joined_only), ", ".join("%s=%d" % (r, len(v)) for r, v in sorted(by_reason.items()))))

    evidence = bridge_evidence()
    card = evidence.get("card_row") or {}
    say("card site %s:%s -> published %s vs joined %s"
        % (CARD_SOURCE, card.get("line"), card.get("published_keys"), card.get("joined_key")))

    summary = {
        "corpus_sources": len(srcs),
        "sources_parsed": result["parsed"],
        "load_bindings_walked": result["load_rows"],
        "published_keys": len(published),
        "joined_keys": len(joined),
        "upstream_face": "results/state_tilt/" + UPSTREAM,
        "upstream_targets": len(rows),
        "upstream_targets_moved": len(moved),
        "upstream_targets_unchanged": len(rows) - len(moved),
        "joined_only_faces": len(joined_only),
        "joined_only_by_basename": len(by_reason.get(REASON_BASENAME) or []),
        "joined_only_by_jsonl_suffix": len(by_reason.get(REASON_SUFFIX) or []),
        "joined_only_unexplained": len(by_reason.get(REASON_NO_SITE) or []),
        "keying_scope": ("published_keys counts dump sinks AND load bindings (E377's union); "
                         "joined_keys counts load bindings only, so the two totals are not a "
                         "subset relation and a face a writer alone keys is correctly absent "
                         "from the joined set"),
        "card_face": CARD_FACE,
        "card_face_keyed_by_the_published_keying": CARD_FACE in published,
        "card_face_keyed_by_the_joined_keying": CARD_FACE in joined,
        "card_site_crosses_the_two_keyings": evidence.get("card_crosses_the_two_keyings", False),
    }
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "summary": summary,
        "upstream_rows": rows[:MAX_ROWS],
        "upstream_rows_truncated": max(0, len(rows) - MAX_ROWS),
        "moved_faces": [
            {"face": r["face"], "reason": r["reason"],
             "why": ("the loading site keys the join by its operands, so _face_key falls back to "
                     "the basename and the path never enters the keyed set"
                     if r["reason"] == REASON_BASENAME else
                     "both face helpers accept only paths ending in .json, so a .jsonl read is "
                     "never keyed however well its path resolves")}
            for r in moved],
        "joined_only_faces": [{"face": k, "reason": why_not_published(k, published),
                               "sites": (result["sites"].get(k) or [])[:3]}
                              for k in joined_only[:MAX_ROWS]],
        "joined_only_faces_truncated": max(0, len(joined_only) - MAX_ROWS),
        "bridge_evidence": evidence,
        "verdict": decide(summary),
        "bound": ("the joined keying is a SECOND reading of the same load rows, not a repair of the "
                  "published one: it is asserted here only where every operand survives the fold, "
                  "and it is published beside the published keying so a reader can see both.  A "
                  "component this study refuses to treat as a path under-reports the defect; it "
                  "cannot invent a face, because a joined key with no .json component is dropped.  "
                  "E377's face is read as published and is never rebuilt, so 'moved' means the two "
                  "keyings disagree, not that E377 was re-run."),
    }
    if write_face:
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(OUTDIR, FACE))
    return face


def verify():
    """Re-derive what needs no corpus scan: the row arithmetic, the lists, the verdict."""
    path = os.path.join(OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    summary = face.get("summary") or {}
    rows = face.get("upstream_rows") or []
    if len(rows) + (face.get("upstream_rows_truncated") or 0) != summary.get("upstream_targets"):
        problems.append("upstream row count does not equal the published target count")
    moved = [r for r in rows if r.get("status") == STATUS_MOVED]
    if len(moved) != summary.get("upstream_targets_moved"):
        problems.append("moved count does not re-add from the rows")
    if len(moved) != len(face.get("moved_faces") or []):
        problems.append("the moved-face list does not match the moved rows")
    for row in rows:
        if row.get("status") not in (STATUS_MOVED, STATUS_STANDS,
                                     "contradiction_published_keying_names_it_after_all"):
            problems.append("row carries an unknown status: %s" % row.get("face"))
            break
        if row.get("status") == STATUS_MOVED and (row.get("published_keying") or False):
            problems.append("a row is both moved and published-keyed: %s" % row.get("face"))
            break
        if row.get("status") == STATUS_STANDS and row.get("joined_keying"):
            problems.append("a standing row is named by the joined keying: %s" % row.get("face"))
            break
    if len(face.get("joined_only_faces") or []) + (face.get("joined_only_faces_truncated") or 0) \
            != summary.get("joined_only_faces"):
        problems.append("the joined-only list does not match its published count")
    split = sum(summary.get(k) or 0 for k in ("joined_only_by_basename",
                                              "joined_only_by_jsonl_suffix",
                                              "joined_only_unexplained"))
    if split != summary.get("joined_only_faces"):
        problems.append("the three named causes do not re-add to the joined-only count")
    for row in (face.get("joined_only_faces") or []):
        if row.get("reason") not in (REASON_BASENAME, REASON_SUFFIX, REASON_NO_SITE):
            problems.append("a joined-only row carries no named cause: %s" % row.get("face"))
            break
        if not row.get("sites"):
            problems.append("a joined-only row names no line: %s" % row.get("face"))
            break
    if summary.get("published_keys") and summary.get("joined_keys") is not None \
            and summary["joined_keys"] > summary["load_bindings_walked"]:
        problems.append("more joined keys than load rows, which cannot happen")
    ev = face.get("bridge_evidence") or {}
    if ev.get("present"):
        if not ev.get("card_row"):
            problems.append("the card's site is not among the source's load rows")
        else:
            if CARD_FACE == (ev["card_row"].get("joined_key") or ""):
                if CARD_FACE in (ev["card_row"].get("published_keys") or []):
                    problems.append("the card's keys agree, so there is nothing to explain")
    if face.get("verdict") != decide(summary):
        problems.append("the verdict does not re-derive from the summary")
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ------------------------------------------------------------------ selftest

FIXT_JOIN = '''
import json, os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
def main():
    card = json.load(open(os.path.join(OUT_DIR, "etf_book_production", "latest.json"),
                          encoding="utf-8"))
    return card
'''

FIXT_LITERAL = '''
import json
def main():
    card = json.load(open("results/etf_book_production/latest.json", encoding="utf-8"))
    return card
'''

FIXT_NOFACE = '''
import json
def main(p):
    flags = json.load(open(p, encoding="utf-8"))
    return flags
'''


def _row(text, face_like):
    tree = ast.parse(text)
    consts = e347.constants(tree)
    for row in e347.load_bindings(tree, consts):
        key = joined_key(row["values"])
        if key and key.endswith(face_like):
            return row, key, published_keying(tree, consts)
    return None, None, set()


FIXT_JSONL = '''
import json, os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
def main():
    rows = json.load(open(os.path.join(OUT_DIR, "runs.jsonl"), encoding="utf-8"))
    return rows
'''


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    row, key, published = _row(FIXT_JOIN, "latest.json")
    leg("a join of folded operands re-keys to its path",
        key == CARD_FACE, "%s -> %s" % (row and row["values"], key))
    leg("the published keying of that same site is a bare basename, which is the defect",
        "latest.json" in published and CARD_FACE not in published, str(sorted(published)))
    leg("the two keyings disagree on exactly the face the card names",
        key == CARD_FACE and key not in published)

    _row_l, key_l, published_l = _row(FIXT_LITERAL, "latest.json")
    leg("a literal path is keyed identically by both readings, so the repair cannot move it",
        key_l == CARD_FACE and CARD_FACE in published_l, "%s / %s" % (key_l, sorted(published_l)))

    _row_n, key_n, _published_n = _row(FIXT_NOFACE, "flags.json")
    leg("a caller-supplied destination yields no joined key", key_n is None, str(key_n))

    leg("an encoding token is not a path component",
        not _is_path_component("utf-8") and not _is_path_component("rb")
        and _is_path_component("results") and _is_path_component("latest.json"))
    leg("a key with no face component is refused rather than invented",
        joined_key(["results", "state_tilt"]) is None
        and joined_key([]) is None)

    base = {"joined_keys": 3, "upstream_targets_moved": 1, "joined_only_faces": 1}
    leg("a moved target is the component-key defect", decide(base) == V_COMPONENT)
    leg("no moved target but a joined-only face costs no published number",
        decide({"joined_keys": 3, "upstream_targets_moved": 0, "joined_only_faces": 2})
        == V_UNCOUNTED)
    leg("nothing joined-only means the published report stands",
        decide({"joined_keys": 3, "upstream_targets_moved": 0, "joined_only_faces": 0})
        == V_NO_DEFECT)
    leg("no joined key is no claim", decide({"joined_keys": 0}) == V_EMPTY)

    rows = classify_targets(["results/a/latest.json", "results/b/other.json"],
                            set(), {"results/a/latest.json"})
    leg("classification names the moved face and leaves the other standing",
        rows[0]["status"] == STATUS_MOVED and rows[1]["status"] == STATUS_STANDS)

    _row_j, key_j, published_j = _row(FIXT_JSONL, "runs.jsonl")
    leg("a .jsonl read resolves as a joined key but neither helper keys it (suffix filter)",
        key_j == "results/runs.jsonl" and not published_j
        and why_not_published("results/runs.jsonl", published_j) == REASON_SUFFIX,
        "%s / %s" % (key_j, sorted(published_j)))

    leg("a basename already in the key set is called a basename, not a suffix case",
        why_not_published(CARD_FACE, {"latest.json"}) == REASON_BASENAME)
    leg("a face nobody names and no suffix rule explains is not explained away",
        why_not_published("results/ghost.json", set()) == REASON_NO_SITE)

    total = len(legs)
    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if not ok else ""))
    say("selftest: %d/%d" % (total - len(bad), total))
    return 1 if bad else 0


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    build(write_face=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))