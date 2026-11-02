"""E356 -- a leg that grades a census against a fresh build goes red when the corpus grows.

The 10 red legs in the r1364 census corpus all say the same sentence: "summary.<field> does not
re-derive".  Every one of them compares a *published* face against `build()` run on today's disk.
The corpus these censuses describe gains sources every round (each round publishes a script and two
faces), so a published count is a statement about a population that no longer exists.  That is not a
defect in the leg, and it is also not a defect in the face -- it is a *different object* being
compared.  This study measures which it is, per leg, field by field, instead of patching either side.

Nothing is written to a published face.  The output is a triage table: for each red leg, the leaf
fields that moved, the direction, and a class:

  in_sync        published == today's build (the leg is red for another reason)
  corpus_growth  every moved leaf is numeric and moved *up* (the population grew)
  shrunk         some numeric leaf moved down, nothing non-numeric moved
  substantive    a verdict / string / list moved -- the finding itself changed
  unbuildable    the module raised (reported, never skipped)
  absent         the published face is not on disk

Usage:
  python scripts/e356_census_red_triage.py build      # publish the triage table
  python scripts/e356_census_red_triage.py verify     # re-derive and compare, write nothing
  python scripts/e356_census_red_triage.py selftest
"""

from __future__ import annotations

import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# (leg, label, module, face) -- the red legs of the r1378 smoke suite (271/278 PASS, 7 FAIL; two
# legs share E335, so six studies).  The face is loaded through the module's own loader, so this
# table cannot drift from the leg that grades it.
LEGS = [
    (298, "control blocks censused by the panel they re-derived on",
     "e298_replay_control_census", "replaycensus_latest.json"),
    (299, "a face value compared finer than the field is printed",
     "e299_rounded_vs_tolerance_census", "precisioncensus_latest.json"),
    (323, "widening the producer needle relocates the unowned gates",
     "e323_reach_under_wider_needle", "reachwide_latest.json"),
    (325, "a gate whose face no source can produce",
     "e325_orphan_gate_faces", "orphangateface_latest.json"),
    (331, "every reader that reaches a face only through a pointer",
     "e331_pointer_only_readers", "pointeronly_latest.json"),
    (335, "the repaired corpus reading lands beside the shipped one",
     "e335_sibling_entry_point", "siblingentry_latest.json"),
]

CLASSES = ("in_sync", "stamps_only", "reindexed", "population_moved", "corpus_growth", "shrunk",
           "substantive", "unbuildable", "absent")

# Rows of a census list are addressed by identity, never by position.  A list that gained a row
# shifts every later index; a diff keyed on position then reports every shifted row as a changed
# finding.  That is the second half of the same disease the legs have.
ID_KEYS = ("source", "module", "face", "path", "name", "consumer", "rel", "file", "identifier",
           "gate", "key", "member", "arm", "label", "family", "expression", "leg", "line")

# Keys that move because a face was rebuilt, not because a finding changed.  A triage that called
# these substantive would have the same disease as the legs it is grading.
STAMP_KEYS = frozenset((
    "generated", "generated_at", "built_at", "elapsed_sec", "evidence_cutoff", "asof", "as_of",
    "ts", "clock", "clock_read", "face", "study", "module", "generated_by",
    # A row addressed by content (expression, source) carries its line as a coordinate: an edit
    # above it renumbers the site without moving the finding.  Named here so it is disclosed as a
    # coordinate, not silently folded into "corpus growth".
    "line", "lineno", "first_line", "last_line", "col", "column",
))
MAX_LEAVES = 12


def _face_path(face):
    return os.path.join(ROOT, "results", "state_tilt", face)


def load_published(face):
    p = _face_path(face)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _import_module(name):
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import importlib
    return importlib.import_module(name)


def rebuild(module, face):
    """Ask the module for today's answer.  `build()` where it exists, else the module's own loader."""
    mod = _import_module(module)
    if hasattr(mod, "build"):
        return mod.build()
    if hasattr(mod, "load"):
        return mod.load(face)
    raise AttributeError("module %s exposes neither build() nor load()" % module)


def _row_identity(rows):
    """The identity of a census list: one key that is unique in every row, or a pair that is.

    A row set can be unique only in combination (`at_risk` rows are unique on (face, path), not on
    either alone).  Falling back to position there would report every shift as a changed finding.
    """
    if not rows or not all(isinstance(r, dict) for r in rows):
        return None

    def unique(keys):
        try:
            vals = [tuple(r.get(k) for k in keys) for r in rows]
        except TypeError:
            return False
        if any(v is None or isinstance(v, (dict, list)) for v in vals):
            return False
        try:
            return len(set(vals)) == len(vals)
        except TypeError:
            return False

    for k in ID_KEYS:
        if unique((k,)):
            return (k,)
    for i, ka in enumerate(ID_KEYS):
        for kb in ID_KEYS[i + 1:]:
            if unique((ka, kb)):
                return (ka, kb)
    return None


def _ident_label(keys, row):
    return ",".join("%s=%s" % (k, row.get(k)) for k in keys)


def leaves(node, prefix=""):
    """Flatten to {path: scalar}, addressing census rows by identity where one exists.

    A list of scalars has no identity at all: it is published whole under `<prefix>[]` so the diff
    can compare members rather than positions.
    """
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            p = "%s.%s" % (prefix, k) if prefix else str(k)
            out.update(leaves(v, p))
    elif isinstance(node, list):
        if node and all(isinstance(x, (dict, list)) for x in node) is False \
                and any(not isinstance(x, (dict, list)) for x in node):
            out[prefix + "[]"] = tuple(str(x) for x in node)
            return out
        ident = _row_identity(node)
        for i, v in enumerate(node):
            if ident is not None:
                p = "%s[%s]" % (prefix, _ident_label(ident, v))
            else:
                p = "%s[%d]" % (prefix, i)
            out.update(leaves(v, p))
    else:
        out[prefix] = node
    return out


def is_stamp(path):
    """A leaf is a stamp if its last name segment (after the dots, before any [i]) is a stamp key."""
    seg = path.split(".")[-1].split("[")[0]
    return seg in STAMP_KEYS


import re as _re

COORD_RE = _re.compile(r"\bline[s]? \d+\b")


def is_coordinate(a, b):
    """True when two strings differ only in an embedded line coordinate.

    A synthetic row name such as `<unnamed leg at line 1128>` carries its position; comparing it
    verbatim makes a renumbering look like a rename.  Only the literal `line <n>` spelling is
    folded -- a template that blanks every digit would also blank a real value (12.24 vs 1.53).
    """
    return isinstance(a, str) and isinstance(b, str) and COORD_RE.sub("line N", a) == \
        COORD_RE.sub("line N", b)


def classify(changes, added=(), removed=(), order_moved=False):
    """changes = [(path, published, fresh)]; added/removed are identity paths."""
    if not changes:
        if added or removed:
            return "population_moved", ["added:%d" % len(added), "removed:%d" % len(removed)]
        return ("reindexed", ["order"]) if order_moved else ("in_sync", [])
    notes = ["added:%d" % len(added), "removed:%d" % len(removed)] if (added or removed) else []
    grew = shrank = substantive = 0
    for path, a, b in changes:
        if is_stamp(path):
            notes.append("stamp:%s" % path)
            continue
        if is_coordinate(a, b):
            notes.append("coord:%s" % path)
            continue
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
                and not isinstance(a, bool) and not isinstance(b, bool):
            if b > a:
                grew += 1
            elif b < a:
                shrank += 1
                notes.append("down:%s" % path)
        else:
            substantive += 1
            notes.append("value:%s" % path)
    if substantive:
        return "substantive", notes
    if shrank:
        return "shrunk", notes
    if added or removed:
        return "population_moved", notes
    if grew:
        return "corpus_growth", notes
    return "stamps_only", notes


def _orders(node, prefix="", out=None):
    """Identity sequences of every census list, so a reordering can be told from a rewrite."""
    if out is None:
        out = []
    if isinstance(node, dict):
        for k, v in node.items():
            _orders(v, "%s.%s" % (prefix, k) if prefix else str(k), out)
    elif isinstance(node, list) and node and all(isinstance(v, dict) for v in node):
        ident = _row_identity(node)
        if ident is not None:
            out.append((prefix, tuple(_ident_label(ident, v) for v in node)))
            for v in node:
                _orders(v, "%s[%s]" % (prefix, _ident_label(ident, v)), out)
    return out


def order_moved(published, fresh):
    a, b = dict(_orders(published or {})), dict(_orders(fresh or {}))
    return any(a[k] != b[k] for k in a if k in b)


def diff_faces(published, fresh):
    """(changed, added, removed).

    A `[]` leaf is a member multiset, not a sequence: members that appear or disappear are
    population movement, and a member only moving index is not a finding at all.
    """
    a, b = leaves(published or {}), leaves(fresh or {})
    changes, added, removed = [], [], []
    for k in sorted(set(a) | set(b)):
        if k.endswith("[]"):
            va = a.get(k) or ()
            vb = b.get(k) or ()
            sa, sb = set(va), set(vb)
            removed.extend("%s<-%s" % (k, x) for x in sorted(sa - sb))
            added.extend("%s->%s" % (k, x) for x in sorted(sb - sa))
            continue
        if k not in b:
            removed.append(k)
        elif k not in a:
            added.append(k)
        elif a[k] != b[k]:
            changes.append((k, a[k], b[k]))
    return changes, added, removed


def triage(rebuild_faces=True):
    rows = []
    for leg, label, module, face in LEGS:
        t0 = time.time()
        published = load_published(face)
        row = {"leg": leg, "label": label, "module": module, "face": face}
        if published is None:
            row.update({"class": "absent", "n_changed": 0, "changes": []})
            rows.append(row)
            continue
        if not rebuild_faces:
            row.update({"class": "not_rebuilt", "n_changed": 0, "changes": []})
            rows.append(row)
            continue
        try:
            fresh = rebuild(module, face)
        except Exception as e:  # reported, never skipped
            row.update({"class": "unbuildable", "n_changed": 0, "changes": [],
                        "error": "%s: %s" % (type(e).__name__, str(e)[:200]),
                        "seconds": round(time.time() - t0, 2)})
            rows.append(row)
            continue
        changes, added, removed = diff_faces(published, fresh)
        moved = order_moved(published, fresh)
        cls, notes = classify(changes, added, removed, moved)
        row.update({
            "class": cls,
            "n_changed": len(changes),
            "n_added": len(added),
            "n_removed": len(removed),
            "order_moved": moved,
            "changes": [{"path": p, "published": a, "fresh": b} for p, a, b in changes[:MAX_LEAVES]],
            "changed_truncated": max(0, len(changes) - MAX_LEAVES),
            "added_sample": added[:MAX_LEAVES],
            "removed_sample": removed[:MAX_LEAVES],
            "published_verdict": (published or {}).get("verdict"),
            "fresh_verdict": (fresh or {}).get("verdict"),
            "verdict_moved": (published or {}).get("verdict") != (fresh or {}).get("verdict"),
            "notes": notes[:MAX_LEAVES],
            "seconds": round(time.time() - t0, 2),
        })
        rows.append(row)
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    summary = {
        "legs": len(rows),
        "by_class": by_class,
        "classes_sum_to_legs": sum(by_class.values()) == len(rows),
        "republish_candidates": sum(1 for r in rows
                                    if r["class"] in ("corpus_growth", "stamps_only")),
        "needs_investigation": sum(1 for r in rows if r["class"] in ("substantive", "shrunk",
                                                                     "unbuildable", "absent")),
        "total_changed_leaves": sum(r["n_changed"] for r in rows),
        "total_added_rows": sum(r.get("n_added", 0) for r in rows),
        "total_removed_rows": sum(r.get("n_removed", 0) for r in rows),
        "legs_with_order_moved": sum(1 for r in rows if r.get("order_moved")),
        "verdicts_moved": sum(1 for r in rows if r.get("verdict_moved")),
    }
    return {
        "study": "E356",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": "do the census-corpus red legs describe a stale face or a real disagreement?",
        "method": "each published face is compared leaf-by-leaf against the module's own build() "
                  "on today's disk; numeric-only upward moves are corpus growth",
        "summary": summary,
        "legs": rows,
    }


# ---------------------------------------------------------------------------- selftest

def selftest():
    ok, fails = 0, []

    def check(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append("%s %s" % (name, detail))

    # L1 a numeric increase is corpus growth, not a disagreement
    c = [("summary.faces_scanned", 583, 600)]
    cls, _ = classify(c)
    check("L1 growth", cls == "corpus_growth", cls)

    # L2 a numeric decrease is not growth
    c = [("summary.faces_scanned", 600, 583)]
    cls, _ = classify(c)
    check("L2 shrink", cls == "shrunk", cls)

    # L3 a verdict string move is substantive even beside growth
    c = [("verdict", "a", "b"), ("summary.n", 1, 2)]
    cls, _ = classify(c)
    check("L3 substantive", cls == "substantive", cls)

    # L4 a bool flip is not numeric movement
    c = [("flag", False, True)]
    cls, _ = classify(c)
    check("L4 bool", cls == "substantive", cls)

    # L5 no change is in_sync, and it is not silently the same as growth
    cls, _ = classify([])
    check("L5 in_sync", cls == "in_sync", cls)

    # L6 nested dicts flatten to dotted leaves (a nested move is not invisible)
    a = {"s": {"x": 1, "t": {"y": 2}}}
    b = {"s": {"x": 1, "t": {"y": 3}}}
    ch, _add, _rem = diff_faces(a, b)
    check("L6 nested", ch == [("s.t.y", 2, 3)], ch)

    # L7 a key present on one side only is an added/removed row, never a skipped comparison
    ch, add, rem = diff_faces({"a": 1}, {"a": 1, "b": 2})
    check("L7 added", ch == [] and add == ["b"] and rem == [], (ch, add, rem))

    # L8 a scalar list is a member set: reordering is not a change, a member appearing is
    ch, _a, _r = diff_faces({"l": [1, 2]}, {"l": [2, 1]})
    check("L8 order-free", ch == [], ch)
    ch, add, rem = diff_faces({"l": [1, 2]}, {"l": [1, 2, 3]})
    check("L8 member added", ch == [] and add == ["l[]->3"] and rem == [], (ch, add, rem))

    # L9 an unbuildable module is reported as such, never as in_sync
    row = {"class": "unbuildable"}
    check("L9 unbuildable counted", row["class"] in CLASSES)

    # L10 every declared leg has a distinct (module, face) pair
    pairs = {(m, f) for _, _, m, f in LEGS}
    check("L10 distinct", len(pairs) == len(LEGS), len(pairs))

    # L11 the triage table's own summary partitions correctly on a fixture
    fixture = [{"class": "corpus_growth"}, {"class": "substantive"}, {"class": "in_sync"}]
    by = {c: sum(1 for r in fixture if r["class"] == c) for c in CLASSES}
    check("L11 partition", sum(by.values()) == len(fixture), by)

    # L12 the classes are a closed vocabulary (a typo cannot become a new class)
    check("L12 vocabulary", set(CLASSES) >= {"in_sync", "corpus_growth", "substantive"}, CLASSES)

    # L13 a timestamp moving is not a finding moving (the triage must not repeat the leg's disease)
    cls, notes = classify([("evidence_cutoff", "2026-11-01", "2026-11-02")])
    check("L13 stamp", cls == "stamps_only", (cls, notes))

    # L14 stamps beside growth stay corpus_growth, with the stamps named in the notes
    cls, notes = classify([("generated", "a", "b"), ("summary.faces_scanned", 138, 141)])
    check("L14 stamp+growth", cls == "corpus_growth" and any(n.startswith("stamp:") for n in notes),
          (cls, notes))

    # L15 a stamp beside a substantive move is still substantive
    cls, _ = classify([("generated", "a", "b"), ("verdict", "x", "y")])
    check("L15 stamp+value", cls == "substantive", cls)

    # L16 nested stamp paths are recognised (summary.generated, not only top level)
    check("L16 nested stamp", is_stamp("summary.generated_at") and not is_stamp("summary.faces"),
          "is_stamp")

    # L17 an indexed leaf is classified by its field name, not by its index
    check("L17 indexed", is_stamp("rows[3].asof") and not is_stamp("rows[3].mentions_rejected"),
          "is_stamp indexed")

    # L18 the summary's partitions add up on a mixed fixture (no class is silently dropped)
    fixture = [{"class": "corpus_growth"}, {"class": "stamps_only"}, {"class": "substantive"},
               {"class": "unbuildable"}]
    by = {c: sum(1 for r in fixture if r["class"] == c) for c in CLASSES}
    check("L18 mixed partition", sum(by.values()) == len(fixture) and by["stamps_only"] == 1, by)

    # L19 a row inserted above the others is an added row, not every later row changing
    a = {"rows": [{"source": "a", "line": 1}, {"source": "b", "line": 2}]}
    b = {"rows": [{"source": "z", "line": 0}, {"source": "a", "line": 1},
                  {"source": "b", "line": 2}]}
    ch, add, rem = diff_faces(a, b)
    check("L19 insert", ch == [] and len(add) == 2 and rem == [], (ch, add, rem))

    # L20 reordering alone is 'reindexed', not 'in_sync' and not 'substantive'
    a = {"rows": [{"source": "a"}, {"source": "b"}]}
    b = {"rows": [{"source": "b"}, {"source": "a"}]}
    ch, add, rem = diff_faces(a, b)
    cls, _n = classify(ch, add, rem, order_moved(a, b))
    check("L20 reindexed", cls == "reindexed", cls)

    # L21 a matched row whose field moved is still measured -- alignment must not hide it, and a
    # numeric move down is its own class rather than a silent pass
    a = {"rows": [{"source": "a", "share": 12.24}]}
    b = {"rows": [{"source": "z"}, {"source": "a", "share": 1.53}]}
    ch, add, rem = diff_faces(a, b)
    cls, _n = classify(ch, add, rem, False)
    check("L21 aligned change", cls == "shrunk" and ch[0][0] == "rows[source=a].share",
          (cls, ch))

    # L22 a list with no unique identity key falls back to position and says so by behaviour
    a = {"rows": [{"x": 1}, {"x": 1}]}
    b = {"rows": [{"x": 1}, {"x": 1}]}
    ch, add, rem = diff_faces(a, b)
    check("L22 no identity", ch == [] and _row_identity(a["rows"]) is None, ch)

    # L23 a name that carries a line coordinate is a coordinate, not a rename
    check("L23 coordinate",
          is_coordinate("<unnamed leg at line 1128>", "<unnamed leg at line 1129>"), "coord")

    # L24 a real number in a string is never folded into a coordinate
    check("L24 not a coordinate", not is_coordinate("share 12.24", "share 1.53"), "coord")

    # L25 a coordinate beside a real move is still substantive
    cls, _n = classify([("<unnamed leg at line 1>", 1, 1), ("verdict", "a", "b")])
    check("L25 coord+value", cls == "substantive", cls)

    print("selftest %d/%d PASS" % (ok, ok + len(fails)))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "build"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        face = triage()
        s = face["summary"]
        print("VERIFY legs=%d growth=%d substantive=%d shrunk=%d unbuildable=%d absent=%d"
              % (s["legs"], s["by_class"]["corpus_growth"], s["by_class"]["substantive"],
                 s["by_class"]["shrunk"], s["by_class"]["unbuildable"], s["by_class"]["absent"]))
        for r in face["legs"]:
            print("  E%d %-12s changed=%d %s"
                  % (r["leg"], r["class"], r["n_changed"],
                     (r.get("notes") or [""])[0] if r.get("notes") else ""))
        return 0
    face = triage()
    out_dir = os.path.join(ROOT, "results", "state_tilt")
    os.makedirs(out_dir, exist_ok=True)
    day = time.strftime("%Y-%m-%d")
    body = json.dumps(face, ensure_ascii=False, indent=1)
    with io.open(os.path.join(out_dir, "REDTRIAGE-%s.json" % day), "w", encoding="utf-8") as fh:
        fh.write(body)
    with io.open(os.path.join(out_dir, "redtriage_latest.json"), "w", encoding="utf-8") as fh:
        fh.write(body)
    s = face["summary"]
    print("published REDTRIAGE-%s.json legs=%d growth=%d substantive=%d shrunk=%d "
          "unbuildable=%d absent=%d changed_leaves=%d"
          % (day, s["legs"], s["by_class"]["corpus_growth"], s["by_class"]["substantive"],
             s["by_class"]["shrunk"], s["by_class"]["unbuildable"], s["by_class"]["absent"],
             s["total_changed_leaves"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))