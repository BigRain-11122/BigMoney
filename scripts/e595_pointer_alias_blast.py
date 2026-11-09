# -*- coding: utf-8 -*-
"""E595 -- would aliasing the pointer face change any reader's answer?

E594 (r1622) published the join census: the bar is spelled in several dialects and three readers
were graded as asking ``evidence_cutoff`` of ``results/etf_book_order/latest.json``, a face that
carries only ``as_of``.  The obvious repair is one line in the writer -- publish the bar under every
spelling -- and E594's own note called that repair's blast radius unmeasured: an alias can also make
a reader that previously fell through to a default start reading a real value.

This study prices that repair two ways, because a repair that "fixes" readers who never read the
face is not a repair:

  addressing   for every graded pair against the pointer face, does the reader name THIS face
               (its directory plus the basename) or another face that merely shares the basename
               ``latest.json``?  A repo can hold many ``latest.json`` files, and E594's resolver
               keys targets by basename alone, so a reader of a different face is attributed to
               the pointer face by name collision.  The three classes are published always:
               names_this_face / names_another_face_of_the_same_basename /
               no_literal_naming_the_basename (the string appears in prose, a fixture or a test);
  aliasing     re-grade every pair against the shipped payload and against two alias arms --
               bar-valued names (evidence_cutoff/pricing_bar/priced_bar/ticket_bar/expected_bar/
               price_bar) set to the same bar, and decision-bar names (book_decided_at/
               decision_bar/card_decided_at/...) set to the same bar.  The second arm is the
               hazard: a decision bar is a different instant from a pricing bar (E586 measured the
               ticket printing both), so aliasing it fabricates an answer rather than supplying a
               missing one.  Both arms' flips are published, and only the bar arm is a candidate
               repair.

The verdict is about the repair, not one reader: if no reader that actually addresses this face
changes outcome, the one-line alias buys nothing and the silent readers were never silent readers
of this face.

Read-only: the shipped payload is never written; the aliased payloads exist only in memory.

  python scripts/e595_pointer_alias_blast.py build
  python scripts/e595_pointer_alias_blast.py check
  python scripts/e595_pointer_alias_blast.py verify
  python scripts/e595_pointer_alias_blast.py selftest

Output: results/state_tilt/BARALIAS.json (+ BARALIAS-latest.json)
"""
from __future__ import annotations

import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e594_bar_dialect_join as e594                                     # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "BARALIAS.json")
SELF_NAME = "e595_pointer_alias_blast.py"

POINTER_REL = "results/etf_book_order/latest.json"
POINTER = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
BASENAME = "latest.json"

# The bar arm: names whose value IS the bar the money was priced on.
BAR_ARM = ["evidence_cutoff", "pricing_bar", "priced_bar", "ticket_bar",
           "expected_bar", "price_bar"]
# The hazard arm: names that denote a DIFFERENT instant (when the book was decided).
DECISION_ARM = ["book_decided_at", "decision_bar", "card_decided_at", "card_priced_bar",
                "priced_on_decision_bar", "ticket_priced_bar"]

A_THIS = "names_this_face"
A_SIBLING = "names_another_face_of_the_same_basename"
A_PROSE = "no_literal_naming_the_basename"

V_ALIAS_NOOP = ("aliasing_this_face_moves_no_reader_that_addresses_it_because_the_silent_ones"
                "_name_a_different_face")
V_ALIAS_MOVES = "aliasing_this_face_moves_at_least_one_reader_that_addresses_it"
V_NO_PAIRS = "no_graded_pair_targets_the_pointer_face"


# --------------------------------------------------------------------------- pure helpers
def _join_parts(node):
    """Constant parts of an ``os.path.join(...)`` call, or None when a part is unreadable.

    A part that is a bare name (``ROOT``, ``HERE``, ``PATHS.results_dir``) is dropped instead of
    rejecting the whole join: the directory the caller spells as literals is what separates
    ``results/etf_book_order/latest.json`` from the twenty-six other ``latest.json`` faces, and
    throwing it away because the first segment is a constant would recreate the collision.
    """
    parts = []
    for a in node.args:
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            parts.append(a.value)
        elif isinstance(a, (ast.Name, ast.Attribute)):
            continue
        else:
            return None
    return parts


def _open_witnesses(src):
    """(line numbers where the file is opened, index of surrounding literals).

    A literal naming a face is not evidence the face is opened (E470: naming is not opening).  The
    witness published here is line-local and deliberately weak: a line carrying the pointer literal
    within a few lines of an ``open``/``json.load``/``read_text`` call.  It is a lower bound on
    "this module reads this face", and a module with no witness is published as such rather than
    as a reader.
    """
    lines = (src or "").splitlines()
    hits = []
    for i, ln in enumerate(lines):
        if BASENAME not in ln:
            continue
        lo, hi = max(0, i - 6), min(len(lines), i + 7)
        for j in range(lo, hi):
            if re.search(r"\b(open|read_text|json\.load|loads)\s*\(", lines[j]):
                hits.append({"literal_line": i + 1, "open_line": j + 1,
                             "snippet": lines[j].strip()[:120]})
                break
    return hits


def latest_literals(src):
    """Every path in a module whose basename is ``latest.json``, with its directory intact.

    ``os.path.join("results", "etf_book_order", "latest.json")`` spells three literals, so a scan
    that reads only the strings would see the basename and throw the directory away -- which is
    exactly the collision this study exists to price.  Joins are therefore folded when every part
    is a literal; f-strings and runtime-composed paths stay visible only through the literals they
    do spell, and that limit is published with the face.
    """
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        tree = None
    out = []
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "join":
                parts = _join_parts(node)
                if parts:
                    joined = "/".join(parts)
                    if joined.replace("\\", "/").rstrip("/").split("/")[-1] == BASENAME:
                        out.append(joined)
    for m in re.finditer(r"""["']([^"'\n]{0,300}latest\.json)["']""", src or ""):
        out.append(m.group(1))
    return sorted(set(out))


def addressing(literals, pointer_dir="etf_book_order"):
    """Which face a reader's own literals address, when the basename is shared by 27 faces."""
    if not literals:
        return A_PROSE
    for lit in literals:
        norm = lit.replace("\\", "/")
        if pointer_dir in norm.split("/")[-3:-1] or (pointer_dir + "/") in norm:
            return A_THIS
    return A_SIBLING


def alias_payload(shipped, names, bar_value):
    """A copy of the payload with each alias name added, pointing at the same bar.

    Names the payload already carries are left at their own value -- an alias never overwrites a
    field the writer already publishes, which is the whole point of "alias" rather than "rewrite".
    """
    out = dict(shipped)
    added = []
    for n in names:
        if n not in out:
            out[n] = bar_value
            added.append(n)
    return out, sorted(added)


def grade(payload_keys, names):
    """carried / not_carried for one (spelling names, payload)."""
    hit = sorted(set(names) & set(payload_keys))
    return ("carried" if hit else "not_carried"), hit


def _contains_pointer(node):
    """Does this expression spell a path whose basename is ``latest.json`` under the pointer dir?"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            norm = sub.value.replace("\\", "/")
            if norm.rstrip("/").split("/")[-1] == BASENAME and ("etf_book_order" in norm
                                                                or norm == BASENAME):
                if "etf_book_order" in norm:
                    return True
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                and sub.func.attr == "join":
            parts = _join_parts(sub)
            if parts:
                joined = "/".join(parts)
                if "etf_book_order" in joined and joined.endswith(BASENAME):
                    return True
    return False


def keys_requested(src):
    """Which keys a module actually asks OF this face, resolving the payload name up to 4 hops.

    A literal is not a read and an ``open`` is not a key fetch.  ``etf_book_ceo_page`` opens the
    pointer and asks it for ``ticket_file``/``file``/``path``; an alias of ``evidence_cutoff``
    changes nothing there, even though the module names the face and opens it.  So the deciding
    hop is the key fetch: names bound from a load of this face (directly or through a helper call
    or a module constant, up to four passes) are collected, then every ``x["k"]`` / ``x.get("k")``
    / ``"k" in x`` on those names.  A module whose payload binding cannot be resolved is published
    as unresolved rather than counted as asking for nothing.
    """
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        return {"keys": [], "resolved": False, "payload_names": []}
    ptr_names = set()
    for _ in range(4):
        before = len(ptr_names)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = node.value
            hit = _contains_pointer(value)
            if not hit and isinstance(value, ast.Call):
                hit = any(isinstance(a, ast.Name) and a.id in ptr_names for a in value.args) or \
                      any(isinstance(a, ast.Constant) and isinstance(a.value, str)
                          and a.value in ptr_names for a in value.args)
            if hit:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        ptr_names.add(t.id)
        if len(ptr_names) == before:
            break
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id in ptr_names:
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                keys.add(sl.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("get", "pop", "setdefault") \
                and isinstance(node.func.value, ast.Name) and node.func.value.id in ptr_names \
                and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            keys.add(node.args[0].value)
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Constant) \
                and isinstance(node.left.value, str):
            for comp in node.comparators:
                if isinstance(comp, ast.Name) and comp.id in ptr_names:
                    keys.add(node.left.value)
    return {"keys": sorted(keys), "resolved": bool(ptr_names), "payload_names": sorted(ptr_names)}


def fallback_sites(src, names):
    """Read sites that supply a DEFAULT for one of these names (`get("x", default)` / pop).

    An alias turning a missing key into a present one silently switches such a site from its
    default to the real value, which is the blast-radius case E594 named.  Publishing the count of
    these sites is the difference between "no reader moves" and "no reader moves because nobody has
    a default to be overridden".
    """
    hits = []
    for n in names:
        for m in re.finditer(r"""\.(?:get|pop)\(\s*["']%s["']\s*,(?!\s*\))\s*[^)]{0,80}\)""" % re.escape(n),
                             src or ""):
            hits.append({"name": n, "snippet": m.group(0)[:120]})
    return hits


def classify_pairs(pairs, facts, shipped_keys):
    """Re-grade every pair aimed at the pointer face under the shipped payload and both arms."""
    bar = {"added": [], "moved": []}
    dec = {"added": [], "moved": []}
    rows = []
    for p in pairs:
        if p.get("target") != BASENAME:
            continue
        mod = p.get("reader")
        f = facts.get(mod) or {}
        lits = f.get("literals", [])
        opens = f.get("opens", [])
        asked = f.get("keys") or {"keys": [], "resolved": False}
        cls = addressing(lits)
        names = list(p.get("names") or [])
        shipped_out, shipped_hit = grade(shipped_keys, names)
        row = {
            "reader": mod,
            "spelling": p.get("spelling"),
            "names": names,
            "addressing": cls,
            "reader_latest_literals": lits[:4],
            "reader_opens_this_face": bool(opens) and cls == A_THIS,
            "open_witnesses": opens[:2],
            "keys_the_reader_asks_of_this_face": sorted(asked.get("keys") or []),
            "payload_binding_resolved": bool(asked.get("resolved")),
            "shipped_outcome": shipped_out,
            "shipped_carried_names": shipped_hit,
            "bar_arm_outcome": shipped_out,
            "bar_arm_added": [],
            "decision_arm_outcome": shipped_out,
            "decision_arm_added": [],
            "flip_is_a_read_flip": False,
        }
        asked_keys = set(asked.get("keys") or [])
        bar_payload, bar_added = alias_payload({k: 1 for k in shipped_keys},
                                               [n for n in names if n in BAR_ARM], "BAR")
        bar_out, _ = grade(bar_payload, names)
        row["bar_arm_outcome"] = bar_out
        row["bar_arm_added"] = bar_added
        if bar_out == "carried" and shipped_out == "not_carried":
            is_read = bool(set(bar_added) & asked_keys)
            row["flip_is_a_read_flip"] = is_read
            bar["moved"].append({"reader": mod, "spelling": p.get("spelling"),
                                 "addressing": cls, "added": bar_added,
                                 "opens": row["reader_opens_this_face"],
                                 "read_flip": is_read})
            bar["added"].extend(bar_added)
        dec_payload, dec_added = alias_payload({k: 1 for k in shipped_keys},
                                               [n for n in names if n in DECISION_ARM], "BAR")
        dec_out, _ = grade(dec_payload, names)
        row["decision_arm_outcome"] = dec_out
        row["decision_arm_added"] = dec_added
        if dec_out == "carried" and shipped_out == "not_carried":
            dec["moved"].append({"reader": mod, "spelling": p.get("spelling"),
                                 "addressing": cls, "added": dec_added,
                                 "opens": row["reader_opens_this_face"],
                                 "read_flip": bool(set(dec_added) & asked_keys)})
            dec["added"].extend(dec_added)
        rows.append(row)
    return rows, bar, dec


def summarise(rows, bar_moved, dec_moved):
    """Two arms again: what flips at all, and what flips on a reader that addresses THIS face."""
    by_addr = {}
    for r in rows:
        b = by_addr.setdefault(r["addressing"], {"pairs": 0, "shipped_carried": 0,
                                                 "bar_arm_moves": 0, "decision_arm_moves": 0})
        b["pairs"] += 1
        if r["shipped_outcome"] == "carried":
            b["shipped_carried"] += 1
        if r["bar_arm_outcome"] == "carried" and r["shipped_outcome"] != "carried":
            b["bar_arm_moves"] += 1
        if r["decision_arm_outcome"] == "carried" and r["shipped_outcome"] != "carried":
            b["decision_arm_moves"] += 1
    return {
        "graded_pairs": len(rows),
        "readers": len({r["reader"] for r in rows}),
        "by_addressing": dict(sorted(by_addr.items())),
        "readers_addressing_this_face": sorted({r["reader"] for r in rows
                                                if r["addressing"] == A_THIS}),
        "readers_graded_silent_against_this_face": sorted({r["reader"] for r in rows
                                                           if r["shipped_outcome"] != "carried"}),
        "readers_that_address_and_open_this_face": sorted(
            {r["reader"] for r in rows if r["reader_opens_this_face"]}),
        "bar_arm_moved_pairs": len(bar_moved),
        "bar_arm_moved_readers": sorted({m["reader"] for m in bar_moved}),
        "bar_arm_moved_readers_that_address_this_face": sorted(
            {m["reader"] for m in bar_moved if m["addressing"] == A_THIS}),
        "bar_arm_moved_readers_that_open_this_face": sorted(
            {m["reader"] for m in bar_moved if m.get("opens")}),
        "pairs_whose_mover_opens_this_face": sum(
            1 for r in rows if r["reader_opens_this_face"]
            and r["bar_arm_outcome"] == "carried" and r["shipped_outcome"] != "carried"),
        "read_flipping_readers": sorted({m["reader"] for m in bar_moved if m.get("read_flip")}),
        "read_flipping_pairs": sum(1 for m in bar_moved if m.get("read_flip")),
        "readers_that_ask_for_at_least_one_key_of_this_face": sorted(
            {r["reader"] for r in rows if r["keys_the_reader_asks_of_this_face"]}),
        "decision_arm_moved_pairs": len(dec_moved),
        "decision_arm_moved_readers": sorted({m["reader"] for m in dec_moved}),
    }


def verdict_from(counts):
    """The deciding class is a reader that asks this face for the very key the alias would add.

    A flip on a reader that never spells this face is a basename collision (27 ``latest.json``
    faces); a flip on a reader that spells it but never opens it is a literal that is not a read
    (E470: naming is not opening); and a flip on a reader that opens it but never asks for that key
    is an open without a fetch -- ``etf_book_ceo_page`` opens the pointer and asks only for
    ``ticket_file``/``file``/``path``, which no bar alias touches.  Only the intersection is a
    reader whose ANSWER the alias can change, so only the intersection moves the verdict.
    """
    if not counts.get("graded_pairs"):
        return V_NO_PAIRS
    if counts.get("read_flipping_readers"):
        return V_ALIAS_MOVES
    return V_ALIAS_NOOP


def answer_sentence(counts, shipped_keys, n_faces):
    silent = counts.get("readers_graded_silent_against_this_face") or []
    openers = counts.get("bar_arm_moved_readers_that_open_this_face") or []
    read_flip = counts.get("read_flipping_readers") or []
    return (
        "The pointer face carries %s. E594 graded %d (reader, spelling) pairs against it and %d "
        "reader(s) as silent (%s). Its basename ``latest.json`` is shared by %d faces on disk, and "
        "reading each reader's own literals, only %d of the graded pairs name this face (%s); the "
        "rest name a different face or spell the basename only in prose, and %d reader(s) both "
        "name it and show an open witness on it (%s). Aliasing the bar under %d spelling(s) flips "
        "%d pair(s) -- %d of those flips belong to a reader that opens this face (%s), and only %d "
        "belong to a reader that actually ASKS this face for the key the alias would add (%s). %s"
        % (", ".join(sorted(shipped_keys)), counts.get("graded_pairs", 0), len(silent),
           ", ".join(silent) or "none", n_faces,
           (counts.get("by_addressing") or {}).get(A_THIS, {}).get("pairs", 0),
           ", ".join(counts.get("readers_addressing_this_face") or []) or "none",
           len(counts.get("readers_that_address_and_open_this_face") or []),
           ", ".join(counts.get("readers_that_address_and_open_this_face") or []) or "none",
           len(BAR_ARM), counts.get("bar_arm_moved_pairs", 0), len(openers),
           ", ".join(openers) or "none",
           len(read_flip), ", ".join(read_flip)
           or "none (every flip is a payload-key grade on a reader that never asks for that key)",
           ("Aliasing decision-bar names would additionally flip %d pair(s): %s -- a decision bar "
            "is a different instant from the pricing bar, so that arm fabricates an answer and is "
            "published as a hazard, not as a repair."
            % (counts.get("decision_arm_moved_pairs", 0),
               ", ".join(counts.get("decision_arm_moved_readers") or []) or "none"))
           if counts.get("decision_arm_moved_pairs") else
           "No pair would be 'fixed' by aliasing a decision-bar name, so that hazard is unpriced "
           "here."))


# --------------------------------------------------------------------------- build
def pointer_keys():
    with io.open(POINTER, encoding="utf-8") as f:
        payload = json.load(f)
    return payload, e594.e586.walk_keys(payload)


def facts_for(modules):
    """Per module: the ``latest.json`` paths it spells, and where it opens one."""
    facts = {}
    for mod in modules:
        try:
            src = io.open(os.path.join(ROOT, mod), encoding="utf-8", errors="replace").read()
        except OSError:
            src = ""
        facts[mod] = {"literals": latest_literals(src), "opens": _open_witnesses(src),
                      "keys": keys_requested(src)}
    return facts


def build(write=True):
    payload, shipped_keys = pointer_keys()
    census = e594.build(write=False)
    joins = [p for p in (census.get("joins") or [])
             if p.get("target") == BASENAME and not str(p.get("reader")).endswith(SELF_NAME)]
    modules = sorted({p.get("reader") for p in joins})
    facts = facts_for(modules)
    rows, bar_moved, dec_moved = classify_pairs(joins, facts, shipped_keys)
    counts = summarise(rows, bar_moved["moved"], dec_moved["moved"])
    n_faces = len(glob.glob(os.path.join(ROOT, "results", "**", BASENAME), recursive=True))

    # the blast radius that only exists when a reader supplies a default for the name
    fallbacks = {}
    for mod in sorted({r["reader"] for r in rows if r["addressing"] == A_THIS}):
        try:
            src = io.open(os.path.join(ROOT, mod), encoding="utf-8", errors="replace").read()
        except OSError:
            src = ""
        hits = fallback_sites(src, BAR_ARM + DECISION_ARM)
        fallbacks[mod] = hits

    face = {
        "study": "E595_pointer_alias_blast",
        "evidence_cutoff": payload.get("as_of"),
        "pointer_face": {"path": POINTER_REL, "keys": sorted(shipped_keys),
                         "as_of": payload.get("as_of"), "file": payload.get("file")},
        "basename_collision": {"basename": BASENAME, "faces_on_disk": n_faces,
                               "resolver": "E594 resolves targets by basename, so a face sharing "
                                           "the basename is indistinguishable from the pointer"},
        "alias_arms": {"bar": BAR_ARM, "decision": DECISION_ARM},
        "addressing_vocab": [A_THIS, A_SIBLING, A_PROSE],
        "pairs": rows,
        "counts": counts,
        "default_fallbacks": {k: v for k, v in sorted(fallbacks.items())},
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, shipped_keys, n_faces),
        "limits": [
            "addressing is decided from the reader's own string literals; a path composed at "
            "runtime from parts is visible only through the parts it spells",
            "a 'flip' is a payload-key grade, not a proven runtime read: a module that opens this "
            "face and never asks for the name is not moved by aliasing it",
            "the alias arms are published side by side on purpose -- the decision arm is a "
            "hazard, and calling its flips a repair would fabricate a decision bar",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, "BARALIAS-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


# --------------------------------------------------------------------------- guard
REQUIRED_PAIR_KEYS = ("reader", "spelling", "names", "addressing", "shipped_outcome",
                      "bar_arm_outcome", "decision_arm_outcome", "reader_opens_this_face",
                      "open_witnesses")


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    rows = face.get("pairs") or []
    counts = face.get("counts") or {}
    if not rows:
        p.append("no graded pair is published")
    for r in rows:
        missing = [k for k in REQUIRED_PAIR_KEYS if k not in r]
        if missing:
            p.append("pair %s/%s lacks %s" % (r.get("reader"), r.get("spelling"),
                                              ",".join(missing)))
            break
        if r["addressing"] not in (A_THIS, A_SIBLING, A_PROSE):
            p.append("pair %s carries an unknown addressing %r" % (r["reader"], r["addressing"]))
            break
        if r["bar_arm_outcome"] == "carried" and r["shipped_outcome"] == "carried":
            pass        # an alias never removes a carried name; it may leave it carried
        if r["bar_arm_outcome"] == "not_carried" and any(
                n in (face.get("alias_arms") or {}).get("bar", []) for n in r["names"]):
            p.append("pair %s/%s is graded not_carried under the bar arm although the arm "
                     "carries one of its names" % (r["reader"], r["spelling"]))
            break
    # counts must re-derive from the published pairs, through the same summariser that built them;
    # the movers are rebuilt from the rows so a hand-edited mover list cannot survive
    bar_moved = [{"reader": r["reader"], "spelling": r["spelling"],
                  "addressing": r["addressing"], "opens": r["reader_opens_this_face"],
                  "read_flip": r["flip_is_a_read_flip"]}
                 for r in rows if r["bar_arm_outcome"] == "carried"
                 and r["shipped_outcome"] != "carried"]
    dec_moved = [{"reader": r["reader"], "spelling": r["spelling"],
                  "addressing": r["addressing"], "opens": r["reader_opens_this_face"],
                  "read_flip": False}
                 for r in rows if r["decision_arm_outcome"] == "carried"
                 and r["shipped_outcome"] != "carried"]
    want = summarise(rows, bar_moved, dec_moved)
    for k, v in want.items():
        if counts.get(k) != v:
            p.append("count %s is %r but re-derives to %r" % (k, counts.get(k), v))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    coll = face.get("basename_collision") or {}
    if not coll.get("faces_on_disk"):
        p.append("the basename collision is not measured")
    arms = face.get("alias_arms") or {}
    if not arms.get("bar") or not arms.get("decision"):
        p.append("an alias arm is missing")
    if set(arms.get("bar") or []) & set(arms.get("decision") or []):
        p.append("the bar arm and the hazard arm share a name")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    shipped = {"as_of", "file", "beta_target", "k_now"}

    # leg1 addressing reads the reader's own literals, not the basename
    lits = latest_literals('p = os.path.join("results", "etf_book_order", "latest.json")')
    chk("leg1 a pointer literal is found and keeps its directory",
        lits and any("etf_book_order" in l for l in lits), lits)
    chk("leg1b that reader addresses this face",
        addressing(lits) == A_THIS, addressing(lits))
    sib = latest_literals('p = os.path.join("results", "etf_book_production", "latest.json")')
    chk("leg1c a reader of another face with the same basename is not this face",
        addressing(sib) == A_SIBLING, addressing(sib))
    chk("leg1d a module that never spells the basename is published as prose",
        addressing(latest_literals("nothing = 1")) == A_PROSE)

    # leg2 the alias never overwrites a field the writer already publishes
    out, added = alias_payload({k: 1 for k in shipped}, ["as_of", "evidence_cutoff"],
                               "2026-11-06")
    chk("leg2 an alias for a name already carried adds nothing", added == ["evidence_cutoff"], added)
    chk("leg2b the shipped value is not replaced by the alias value",
        out["as_of"] == 1 and out["evidence_cutoff"] == "2026-11-06", out)
    out2, added2 = alias_payload(dict({k: 1 for k in shipped}, as_of="2026-10-14"),
                                 ["evidence_cutoff"], "2026-11-06")
    chk("leg2c a carried name keeps its own value even when the alias points elsewhere",
        out2["as_of"] == "2026-10-14", out2)

    # leg3 grading and the flip that defines the blast radius
    chk("leg3 a spelling the face carries is carried", grade(shipped, ["as_of"])[0] == "carried")
    chk("leg3b a spelling it lacks is not", grade(shipped, ["evidence_cutoff"])[0] == "not_carried")
    alias_keys, _ = alias_payload({k: 1 for k in shipped}, ["evidence_cutoff"], "BAR")
    chk("leg3c the same pair is carried under the bar arm",
        grade(alias_keys, ["evidence_cutoff"])[0] == "carried")

    # leg4 the deciding arm: a flip on a reader that addresses this face moves the verdict,
    #      a flip on a name-collision reader does not
    joins = [
        {"reader": "a.py", "spelling": "as_of", "names": ["as_of"], "target": BASENAME},
        {"reader": "b.py", "spelling": "evidence_cutoff", "names": ["evidence_cutoff"],
         "target": BASENAME},
    ]
    facts = {"a.py": {"literals": ["results/etf_book_order/latest.json"],
                      "opens": [{"literal_line": 1, "open_line": 1, "snippet": "x"}],
                      "keys": {"keys": ["as_of"], "resolved": True}},
             "b.py": {"literals": ["results/etf_book_production/latest.json"],
                      "opens": [{"literal_line": 1, "open_line": 1, "snippet": "x"}],
                      "keys": {"keys": ["as_of"], "resolved": True}}}
    rows, bar, dec = classify_pairs(joins, facts, shipped)
    cnt = summarise(rows, bar["moved"], dec["moved"])
    chk("leg4 the reader that carries the bar is counted carried",
        cnt["by_addressing"][A_THIS]["shipped_carried"] == 1, cnt["by_addressing"])
    chk("leg4b the alias flips one pair", cnt["bar_arm_moved_pairs"] == 1, cnt)
    chk("leg4c but no flip belongs to a reader that opens this face",
        cnt["bar_arm_moved_readers_that_open_this_face"] == [], cnt)
    chk("leg4d so the repair is a no-op and the verdict says so",
        verdict_from(cnt) == V_ALIAS_NOOP, verdict_from(cnt))
    chk("leg4e the silent reader is published as a name collision, not as a broken join",
        rows[1]["addressing"] == A_SIBLING and rows[1]["shipped_outcome"] == "not_carried", rows[1])
    chk("leg4f the one reader that opens this face is published",
        cnt["readers_that_address_and_open_this_face"] == ["a.py"], cnt)

    # leg5 the verdict can move: a silent reader that opens this face AND asks for the key
    facts2 = {"a.py": {"literals": ["results/etf_book_order/latest.json"],
                       "opens": [{"literal_line": 1, "open_line": 1, "snippet": "x"}],
                       "keys": {"keys": ["as_of"], "resolved": True}},
              "b.py": {"literals": ["results/etf_book_order/latest.json"],
                       "opens": [{"literal_line": 3, "open_line": 4, "snippet": "x"}],
                       "keys": {"keys": ["evidence_cutoff"], "resolved": True}}}
    rows2, bar2, dec2 = classify_pairs(joins, facts2, shipped)
    cnt2 = summarise(rows2, bar2["moved"], dec2["moved"])
    chk("leg5 a silent reader that opens this face appears in the moved-this-face list",
        cnt2["bar_arm_moved_readers_that_open_this_face"] == ["b.py"], cnt2)
    chk("leg5b and because it asks for evidence_cutoff its flip is a READ flip",
        cnt2["read_flipping_readers"] == ["b.py"], cnt2)
    chk("leg5c so the verdict is MOVES, not NOOP", verdict_from(cnt2) == V_ALIAS_MOVES)
    # the open-without-fetch case: names the face, opens it, asks for a different key
    facts3 = {"a.py": facts2["a.py"],
              "b.py": {"literals": ["results/etf_book_order/latest.json"],
                       "opens": [{"literal_line": 3, "open_line": 4, "snippet": "x"}],
                       "keys": {"keys": ["file", "ticket_file"], "resolved": True}}}
    _r5, _b5, _d5 = classify_pairs(joins, facts3, shipped)
    _c5 = summarise(_r5, _b5["moved"], _d5["moved"])
    chk("leg5d an open without a fetch of the key is not a read flip",
        _c5["read_flipping_readers"] == [] and _c5["bar_arm_moved_pairs"] == 1, _c5)
    chk("leg5e so the verdict stays NOOP -- the alias cannot change that reader's answer",
        verdict_from(_c5) == V_ALIAS_NOOP)
    _r5b, _b5b, _d5b = classify_pairs(
        joins, {"a.py": facts2["a.py"], "b.py": {"literals": facts2["b.py"]["literals"],
                                                 "opens": [],
                                                 "keys": {"keys": [], "resolved": False}}}, shipped)
    chk("leg5f an unresolved payload binding is not counted as asking for nothing",
        summarise(_r5b, _b5b["moved"], _d5b["moved"])["read_flipping_readers"] == []
        and any(r["payload_binding_resolved"] is False for r in _r5b))

    # leg6 the hazard arm is published separately and never merged into the repair count
    chk("leg6 a decision-bar name is not in the bar arm",
        not (set(DECISION_ARM) & set(BAR_ARM)), BAR_ARM)
    dpay, dadded = alias_payload({k: 1 for k in shipped}, ["book_decided_at"], "BAR")
    chk("leg6b aliasing a decision name does supply the name (which is why it is a hazard)",
        grade(dpay, ["book_decided_at"])[0] == "carried" and dadded == ["book_decided_at"])
    joins3 = [{"reader": "c.py", "spelling": "decision", "names": ["book_decided_at"],
               "target": BASENAME}]
    rows3, bar3, dec3 = classify_pairs(
        joins3, {"c.py": {"literals": ["results/etf_book_order/latest.json"],
                          "opens": [{"literal_line": 1, "open_line": 1, "snippet": "x"}]}}, shipped)
    cnt3 = summarise(rows3, bar3["moved"], dec3["moved"])
    chk("leg6c a decision-arm flip does not move the bar-arm repair count",
        cnt3["bar_arm_moved_pairs"] == 0 and cnt3["decision_arm_moved_pairs"] == 1, cnt3)
    chk("leg6d and it does not flip the verdict to a repair", verdict_from(cnt3) == V_ALIAS_NOOP)

    # leg7 the default-fallback blast radius is its own published field
    hits = fallback_sites('x = t.get("evidence_cutoff", "2020-01-01")', ["evidence_cutoff"])
    chk("leg7 a get() with a default is found", len(hits) == 1, hits)
    chk("leg7b a bare subscript is not a default site",
        fallback_sites('x = t["evidence_cutoff"]', ["evidence_cutoff"]) == [])
    chk("leg7c a get() with no default is not a default site",
        fallback_sites('x = t.get("evidence_cutoff")', ["evidence_cutoff"]) == [])

    # leg8 the guard refuses hand-written counts, a contradicting verdict, an unknown class
    face = {"pairs": rows2, "counts": dict(cnt2), "verdict": verdict_from(cnt2), "answer": "x",
            "basename_collision": {"faces_on_disk": 27},
            "alias_arms": {"bar": BAR_ARM, "decision": DECISION_ARM}}
    chk("leg8 the guard accepts a face whose counts re-derive", face_problems(face) == [],
        face_problems(face))
    bad = json.loads(json.dumps(face))
    bad["counts"]["bar_arm_moved_pairs"] = 0
    chk("leg8b the guard refuses a moved-pair count that does not re-derive",
        any("bar_arm_moved_pairs" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(face))
    bad2["verdict"] = V_ALIAS_NOOP
    chk("leg8c the guard refuses a verdict that contradicts the moved readers",
        any("verdict does not follow" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(face))
    bad3["pairs"][1]["addressing"] = "somewhere_else"
    chk("leg8d the guard refuses an unknown addressing class",
        any("unknown addressing" in s for s in face_problems(bad3)), face_problems(bad3))
    bad4 = json.loads(json.dumps(face))
    bad4["alias_arms"]["decision"] = list(BAR_ARM)
    chk("leg8e the guard refuses two arms that share a name",
        any("share a name" in s for s in face_problems(bad4)), face_problems(bad4))
    bad5 = json.loads(json.dumps(face))
    bad5["basename_collision"]["faces_on_disk"] = 0
    chk("leg8f the guard refuses a face that never measured the basename collision",
        any("basename collision" in s for s in face_problems(bad5)), face_problems(bad5))

    # leg9 the answer sentence carries the numbers it counted
    ans = answer_sentence(cnt2, shipped, 27)
    chk("leg9 the answer names the reader whose answer moves",
        "b.py" in ans and "27" in ans, ans[:200])

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
        keys = ("pointer_face", "basename_collision", "pairs", "counts", "verdict",
                "default_fallbacks", "alias_arms")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))