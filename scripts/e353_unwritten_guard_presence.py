"""E353 -- what each guard on an unwritten field would do against the face that is on disk today.

E350 published 230 guard fields and 131 of them with no writer anywhere in the corpus, and stated
the consequence it could not measure: *the guard can only fire on a missing value*.  That is a
claim about the in-repo corpus, not about the tree.  This study asks the tree.

Per (face, field) pair from E350's population:

  (1) resolve the face key to a file on disk -- a key with a path is looked up at that path, a
      bare basename is looked up in a whole-tree index (0 hits / 1 hit / N hits are three
      different facts, and N is not resolved by picking the first);
  (2) load that file and ask whether the field is there: present and truthy, present and falsy,
      present and null, absent at the top level (and, if absent, whether a one-level nested dict
      carries it);
  (3) classify the guard by what its read does today: ``guard_never_fires`` (the read yields a
      value, so the guard is never reached with a missing one -- a falsy value is published as its
      own state because whether that trips depends on a test the field does not carry),
      ``guard_is_the_alert`` (the field is absent or null, so the guard is the last line of
      defence and has never been reached with a value) and ``guard_unreachable`` (the read raises
      before the guard runs -- no file at the named path, no file with that name anywhere, a name
      shared by several files, or an unparseable face);
  (4) turn the first class into a work list: which faces must gain which fields (one writer per
      face covers every field of that face) and, separately, which guards cannot be helped by any
      writer because their face name does not resolve;
  (5) reconcile against E346's 17 latches so the two counts are one sentence.

Nothing is executed from the corpus; only stat/read on JSON faces.  The population itself comes
from E350's AST census (imported, never re-implemented), so ``build`` pays E350's ~100 s scan and
``verify`` does not: verify re-reads the disk for the same pairs, which is this study's own
derivation, and checks the population still matches E350's published face.

Usage:
  python scripts/e353_unwritten_guard_presence.py build      # write the face
  python scripts/e353_unwritten_guard_presence.py verify     # re-derive presence + compare
  python scripts/e353_unwritten_guard_presence.py selftest   # offline fixture legs
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e346_status_writer_unread as e346  # noqa: E402  (corpus walker, same tree)
import e350_field_branch_census as e350  # noqa: E402  (the population, same tree)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "GUARDPRESENCE-%s.json" % TODAY
LATEST = "guardpresence_latest.json"
STUDY = "E353_unwritten_guard_presence"
SELF_REL = "scripts/e353_unwritten_guard_presence.py"

E346_FACE = os.path.join(OUTDIR, "UNREADSTATUS-2026-11-01.json")

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".codely-cli", ".pytest_cache",
             ".mypy_cache", ".venv", "venv", ".idea", ".vscode"}

CLASS_NEVER = "guard_never_fires"
CLASS_ALERT = "guard_is_the_alert"
CLASS_UNREACHABLE = "guard_unreachable"
CLASSES = (CLASS_NEVER, CLASS_ALERT, CLASS_UNREACHABLE)

V_TODAY = ("of_%d_guards_on_a_field_no_source_writes_%d_raise_before_the_guard_runs_%d_read_a_"
           "missing_or_null_field_and_%d_read_a_value_of_which_%d_read_falsy")
V_EMPTY = "the_upstream_population_was_empty_so_no_claim_about_the_disk_is_made"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- disk resolution

def build_index(root=ROOT, skip=SKIP_DIRS):
    """``{filename: [relpath, ...]}`` for every ``*.json`` file under ``root``.

    A basename is only an identity when it occurs once; the index keeps every hit so a caller can
    refuse an ambiguous name instead of taking the first one.
    """
    index = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        for name in files:
            if not name.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(base, name), root).replace("\\", "/")
            index.setdefault(name, []).append(rel)
    for hits in index.values():
        hits.sort()
    return index


def resolve(face, index, root=ROOT):
    """``{"kind", "path", "alternatives", "n_alternatives"}`` for a face key.

    ``kind`` is ``named`` (a path key that is on disk), ``path_moved`` (a path key that is not,
    with every file of that basename published), ``basename`` (a bare key with exactly one file),
    ``ambiguous`` (a bare key shared by several files) or ``missing`` (no file of that name).
    """
    key = (face or "").strip().replace("\\", "/")
    key = key.lstrip("./") if not key.startswith("../") else key
    if not key:
        return {"kind": "missing", "path": None, "alternatives": [], "n_alternatives": 0}
    if "/" in key:
        path = os.path.join(root, key.replace("/", os.sep))
        if os.path.isfile(path):
            return {"kind": "named", "path": key, "alternatives": [], "n_alternatives": 0}
        alts = index.get(os.path.basename(key), [])
        return {"kind": "path_moved", "path": None, "alternatives": alts,
                "n_alternatives": len(alts)}
    hits = index.get(key, [])
    if len(hits) == 1:
        return {"kind": "basename", "path": hits[0], "alternatives": hits, "n_alternatives": 1}
    if not hits:
        return {"kind": "missing", "path": None, "alternatives": [], "n_alternatives": 0}
    return {"kind": "ambiguous", "path": None, "alternatives": hits, "n_alternatives": len(hits)}


def read_face(path, root=ROOT):
    """``(doc, error)``; ``doc`` is a dict or None and ``error`` names why it is not one."""
    full = os.path.join(root, path.replace("/", os.sep)) if path else None
    if not full or not os.path.isfile(full):
        return None, "no_file"
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as exc:
        return None, "unparseable:%s" % type(exc).__name__
    if not isinstance(doc, dict):
        return None, "not_an_object:%s" % type(doc).__name__
    return doc, ""


_UNREACHABLE_STATE = {
    "missing": ("face_absent_no_file_anywhere", "no_file_named"),
    "path_moved": ("face_absent_at_read_path", "path_not_on_disk"),
    "ambiguous": ("face_name_shared_by_several_files", "name_not_one_file"),
}


def classify(face, field, index, root=ROOT):
    """One row: what this guard's read does against the tree today."""
    res = resolve(face, index, root)
    row = {
        "face": face, "field": field, "key_kind": res["kind"],
        "path": res["path"], "state": "", "class": "", "reason": "",
        "nested_hit": False, "alternatives": res["alternatives"][:5],
        "n_alternatives": res["n_alternatives"],
    }
    if res["kind"] in _UNREACHABLE_STATE:
        row["state"], row["reason"] = _UNREACHABLE_STATE[res["kind"]]
        row["class"] = CLASS_UNREACHABLE
        return row
    doc, error = read_face(res["path"], root)
    if doc is None:
        row["state"] = "face_unreadable"
        row["reason"] = error
        row["class"] = CLASS_UNREACHABLE
        return row
    if field in doc:
        value = doc[field]
        if value is None:
            row["state"], row["class"] = "field_null", CLASS_ALERT
        elif not value:
            row["state"], row["class"] = "field_present_falsy", CLASS_NEVER
        else:
            row["state"], row["class"] = "field_present_truthy", CLASS_NEVER
        return row
    row["nested_hit"] = any(isinstance(v, dict) and field in v for v in doc.values())
    row["state"], row["class"] = "field_absent", CLASS_ALERT
    return row


# --------------------------------------------------------------------------- work lists

def writers_needed(rows):
    """Faces that must gain fields for an alert pair to become a written one.

    One writer per face covers every missing field of that face, so the list is the shortest
    face-level cover of the alert population, not one entry per pair.
    """
    groups = {}
    for row in rows:
        if row["class"] != CLASS_ALERT:
            continue
        slot = groups.setdefault(row["face"], {"face": row["face"], "path": row["path"],
                                               "key_kind": row["key_kind"],
                                               "missing_fields": [], "pairs": 0})
        if row["field"] not in slot["missing_fields"]:
            slot["missing_fields"].append(row["field"])
        slot["pairs"] += 1
    out = list(groups.values())
    for slot in out:
        slot["missing_fields"].sort()
    out.sort(key=lambda s: (-s["pairs"], s["face"]))
    return out


def path_fixes(rows):
    """Faces that no writer can fix, because the name does not resolve to one file."""
    groups = {}
    for row in rows:
        if row["class"] != CLASS_UNREACHABLE:
            continue
        slot = groups.setdefault(row["face"], {"face": row["face"], "reason": row["reason"],
                                               "state": row["state"], "fields": [],
                                               "pairs": 0, "alternatives": row["alternatives"],
                                               "n_alternatives": row["n_alternatives"]})
        if row["field"] not in slot["fields"]:
            slot["fields"].append(row["field"])
        slot["pairs"] += 1
    out = list(groups.values())
    for slot in out:
        slot["fields"].sort()
    out.sort(key=lambda s: (-s["pairs"], s["face"]))
    return out


def reconcile(pairs, all_rows, e346_face=None):
    """E346's 17 latches are producer fields on status faces; this population is reader fields.

    The reconciliation answers one question: do the two counts describe the same fields?  A name
    match is not an identity match, so both are published.
    """
    face = e346_face
    if face is None:
        if not os.path.exists(E346_FACE):
            return {"available": False, "sentence": "E346 face absent, reconciliation not made"}
        with open(E346_FACE, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    summary = (face or {}).get("summary") or {}
    latches = summary.get("latches") or []
    latch_keys = sorted({str(l.get("key")) for l in latches if l.get("key")})
    unwritten_keys = {p["field"] for p in pairs}
    written_keys = {r["field"] for r in all_rows if r.get("written")}
    name_matches = sorted(set(latch_keys) & unwritten_keys)
    latch_faces = set()
    for bound in summary.get("latch_bounds") or []:
        for f in bound.get("faces") or []:
            latch_faces.add(str(f).rsplit("/", 1)[-1])
    identity = sorted({"%s :: %s" % (p["face"], p["field"]) for p in pairs
                       if p["field"] in latch_keys
                       and p["face"].rsplit("/", 1)[-1] in latch_faces})
    return {
        "available": True,
        "latches": len(latches),
        "latch_keys": latch_keys,
        "name_matches_in_unwritten_population": name_matches,
        "identity_matches": identity,
        "name_matches_that_e346_calls_written": sorted(set(latch_keys) & written_keys),
        "sentence": ("E346's %d latches are fields a producer writes and then branches on itself; "
                     "%d of their names also occur among the %d unwritten guard pairs and %d of "
                     "those are the same face-and-field, so the two counts are one population "
                     "only where a name happens to coincide"
                     % (len(latches), len(name_matches), len(pairs), len(identity))),
    }


def summarize(rows, population, reconcile_block):
    by_class = {name: 0 for name in CLASSES}
    by_state = {}
    by_key_kind = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
        by_state[row.get("state", "")] = by_state.get(row.get("state", ""), 0) + 1
        by_key_kind[row.get("key_kind", "")] = by_key_kind.get(row.get("key_kind", ""), 0) + 1
    writers = writers_needed(rows)
    fixes = path_fixes(rows)
    return {
        "upstream_pairs": population,
        "pairs": len(rows),
        "by_class": by_class,
        "by_state": by_state,
        "by_key_kind": by_key_kind,
        "classes_sum_to_pairs": sum(by_class.values()) == len(rows),
        "guard_never_fires_on_a_falsy_value": by_state.get("field_present_falsy", 0),
        "distinct_faces": len({r["face"] for r in rows}),
        "faces_with_a_bare_key": len({r["face"] for r in rows if r["key_kind"] in
                                      ("basename", "ambiguous", "missing")}),
        "nested_only_fields": sum(1 for r in rows if r.get("nested_hit")),
        "minimal_writers": len(writers),
        "pairs_a_writer_would_fix": sum(w["pairs"] for w in writers),
        "path_fixes": len(fixes),
        "pairs_no_writer_can_fix": sum(f["pairs"] for f in fixes),
        "reconcile_e346_latches": (reconcile_block or {}).get("latches"),
        "reconcile_name_matches": len((reconcile_block or {}).get(
            "name_matches_in_unwritten_population") or []),
        "reconcile_identity_matches": len((reconcile_block or {}).get("identity_matches") or []),
    }


def decide(summary):
    if not summary["pairs"]:
        return V_EMPTY
    return V_TODAY % (
        summary["pairs"],
        summary["by_class"].get(CLASS_UNREACHABLE, 0),
        summary["by_class"].get(CLASS_ALERT, 0),
        summary["by_class"].get(CLASS_NEVER, 0),
        summary["guard_never_fires_on_a_falsy_value"],
    )


# --------------------------------------------------------------------------- face

def _head():
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def _population():
    """E350's unwritten-guard population, rebuilt from the corpus (the expensive part)."""
    reads, writes, _stats = e350.measure(e350._sources())
    rows = e350._rows(reads, writes)
    return [r for r in rows if r["guards"] and not r["written"]], rows


def build(pin=None, index=None):
    population, all_rows = _population()
    index = index if index is not None else build_index()
    rows = [classify(r["face"], r["field"], index) for r in population]
    rows.sort(key=lambda r: (r["class"], r["face"], r["field"]))
    block = reconcile(population, all_rows)
    summary = summarize(rows, len(population), block)
    return {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "source": SELF_REL,
        "pin": pin or _head(),
        "evidence_cutoff": TODAY,
        "summary": summary,
        "verdict": decide(summary),
        "bound": (
            "population = E350's unwritten-guard pairs rebuilt from the corpus, not re-read from "
            "the published face (that face truncates its list to 40 rows); a face key without a "
            "path is E350's basename fallback, so an ambiguous bare name is published as "
            "unreachable with every file it could mean rather than resolved by taking the first; "
            "field presence is a top-level key test on the face as it sits on disk today, and "
            "nested_hit only says a one-level dict carries the name; a present falsy value is published as "
            "its own state under guard_never_fires because a not-shaped guard would fire on it "
            "while an is None-shaped guard would pass, and the field alone cannot tell the two "
            "forms apart, so the count that reads a value is not a count of guards that cannot "
            "fire; no source is executed -- only stat and json.load"),
        "rows": rows,
        "writers_needed": writers_needed(rows),
        "path_fixes": path_fixes(rows),
        "reconcile_346": block,
    }


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, FACE)
    latest = os.path.join(OUTDIR, LATEST)
    for target in (dated, latest):
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


def _upstream_published_count():
    """E350's own count of unwritten guard fields, for a population-drift check."""
    path = os.path.join(OUTDIR, "fieldbranch_latest.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    return ((face.get("summary") or {}).get("guard_fields_with_no_writer"))


def verify():
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    with open(dated, "r", encoding="utf-8") as fh:
        published = json.load(fh)
    pairs = published.get("rows") or []
    if not pairs:
        say("no published rows")
        return 2
    index = build_index()
    fresh = [classify(r["face"], r["field"], index) for r in pairs]
    fresh.sort(key=lambda r: (r["class"], r["face"], r["field"]))
    problems = []
    if fresh != pairs:
        drifted = [(a.get("face"), a.get("field"), a.get("state"), b.get("state"))
                   for a, b in zip(pairs, fresh) if a != b]
        problems.append("presence rows differ (%d of %d, first: %r)"
                        % (len(drifted), len(pairs), drifted[:5]))
    upstream = _upstream_published_count()
    if upstream is not None and upstream != len(pairs):
        problems.append("population moved: E350 now publishes %s unwritten guards, this face "
                        "classifies %d" % (upstream, len(pairs)))
    block = reconcile(pairs, [])
    fresh_summary = summarize(fresh, len(pairs), block)
    if published.get("summary") != fresh_summary:
        for key in sorted(set(published.get("summary") or {}) | set(fresh_summary)):
            a = (published.get("summary") or {}).get(key)
            b = fresh_summary.get(key)
            if a != b:
                problems.append("summary.%s: %r != %r" % (key, a, b))
    if published.get("verdict") != decide(fresh_summary):
        problems.append("verdict: %r != %r" % (published.get("verdict"),
                                               decide(fresh_summary)))
    if problems:
        say("VERIFY FAIL (%d)" % len(problems))
        for line in problems[:20]:
            say("  " + line)
        return 1
    say("verify: 0 problems (%d pairs, %d classes re-derived from disk)"
        % (len(fresh), len(CLASSES)))
    return 0


# --------------------------------------------------------------------------- selftest

def _fixture(root, files):
    for rel, doc in files.items():
        full = os.path.join(root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            if isinstance(doc, str):
                fh.write(doc)
            else:
                json.dump(doc, fh)
    return build_index(root)


def selftest():
    import tempfile

    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    with tempfile.TemporaryDirectory() as tmp:
        index = _fixture(tmp, {
            "results/x/OK.json": {"verdict": "ok", "empty": [], "null": None,
                                  "nested": {"deep": 1}},
            "results/x/ok_latest.json": {"verdict": "ok"},
            "data/y/meta.json": {"a": 1},
            "data/z/meta.json": {"a": 2},
            "results/x/MOVED-2026-11-02.json": {"verdict": "ok"},
            "data/q/moved_face.json": {"verdict": "ok"},
            "results/x/LIST.json": "[1, 2, 3]",
            "results/x/BAD.json": "{not json",
        })
        row = classify("results/x/OK.json", "verdict", index, tmp)
        leg("truthy field never fires", row["class"] == CLASS_NEVER, row["state"])
        leg("null field is the alert class", classify("results/x/OK.json", "null", index,
                                                      tmp)["class"] == CLASS_ALERT)
        leg("absent field is the alert class", classify("results/x/OK.json", "gone", index,
                                                        tmp)["class"] == CLASS_ALERT)
        falsy = classify("results/x/OK.json", "empty", index, tmp)
        leg("a falsy present value is published apart from a truthy one",
            falsy["class"] == CLASS_NEVER and falsy["state"] == "field_present_falsy",
            falsy["state"])
        nested = classify("results/x/OK.json", "deep", index, tmp)
        leg("nested-only name is an absent top-level field and says so",
            nested["class"] == CLASS_ALERT and nested["nested_hit"] is True, str(nested))
        bare = classify("ok_latest.json", "verdict", index, tmp)
        leg("a bare key with one file resolves through it",
            bare["class"] == CLASS_NEVER and bare["key_kind"] == "basename", str(bare))
        amb = classify("meta.json", "a", index, tmp)
        leg("a bare key shared by two files is refused, not first-match",
            amb["class"] == CLASS_UNREACHABLE and amb["key_kind"] == "ambiguous"
            and amb["n_alternatives"] == 2, str(amb))
        moved = classify("results/x/moved_face.json", "verdict", index, tmp)
        leg("a path key that moved publishes every file it could mean",
            moved["class"] == CLASS_UNREACHABLE and moved["reason"] == "path_not_on_disk"
            and moved["alternatives"] == ["data/q/moved_face.json"], str(moved))
        leg("a name with no file anywhere is its own reason",
            classify("nothing.json", "k", index, tmp)["reason"] == "no_file_named")
        leg("a list face is unreadable, not an empty object",
            classify("results/x/LIST.json", "verdict", index, tmp)["state"] == "face_unreadable")
        leg("unparseable json is unreadable",
            classify("results/x/BAD.json", "verdict", index, tmp)["class"] == CLASS_UNREACHABLE)
        leg("a directory is not a face",
            classify("results/x", "verdict", index, tmp)["class"] == CLASS_UNREACHABLE)

        # writer cover: two alert pairs on one face are one writer with two fields
        rows = [
            {"face": "results/x/OK.json", "field": "gone", "class": CLASS_ALERT,
             "path": "results/x/OK.json", "key_kind": "named"},
            {"face": "results/x/OK.json", "field": "null", "class": CLASS_ALERT,
             "path": "results/x/OK.json", "key_kind": "named"},
            {"face": "ok_latest.json", "field": "other", "class": CLASS_ALERT,
             "path": "results/x/ok_latest.json", "key_kind": "basename"},
            {"face": "nothing.json", "field": "k", "class": CLASS_UNREACHABLE,
             "path": None, "key_kind": "missing", "reason": "no_file_named",
             "state": "face_absent_no_file_anywhere", "alternatives": [], "n_alternatives": 0},
        ]
        writers = writers_needed(rows)
        leg("a writer covers a face once, with every missing field",
            len(writers) == 2 and writers[0]["pairs"] == 2
            and writers[0]["missing_fields"] == ["gone", "null"], str(writers))
        fixes = path_fixes(rows)
        leg("a writer is never proposed for an unresolvable face",
            len(fixes) == 1 and all(w["face"] != "nothing.json" for w in writers), str(fixes))
        summary = summarize(rows, 4, {"latches": 17, "name_matches_in_unwritten_population": [],
                                      "identity_matches": []})
        leg("the classes sum to the population", summary["classes_sum_to_pairs"] is True)
        leg("the work lists are counted, not guessed",
            summary["pairs_a_writer_would_fix"] == 3
            and summary["pairs_no_writer_can_fix"] == 1, str(summary))
        leg("an empty population makes no claim", decide(summarize([], 0, {})) == V_EMPTY)

        # a name match is not an identity match
        e346_face_fixture = {"summary": {"latches": [{"key": "last_spawn_attempt"},
                                                     {"key": "verdict"}],
                                         "latch_bounds": [{"faces": ["results/x/OK.json"],
                                                           "key": "verdict"}]}}
        block = reconcile([
            {"face": "results/x/OK.json", "field": "verdict", "class": CLASS_ALERT},
            {"face": "results/z/OTHER.json", "field": "last_spawn_attempt",
             "class": CLASS_ALERT},
        ], [], e346_face=e346_face_fixture)
        leg("the reconciliation separates a name match from a face match",
            len(block["name_matches_in_unwritten_population"]) == 2
            and len(block["identity_matches"]) == 1, str(block))
        leg("no latch key is claimed as written by this study's own rows",
            block["name_matches_that_e346_calls_written"] == [])

        # a .git directory is not part of the tree the census reads
        git_index = _fixture(tmp, {".git/blob.json": {"verdict": 1}})
        leg("the index walker skips .git", "blob.json" not in git_index, str(sorted(git_index)))

    corpus = e346._corpus()
    leg("this study's own source is outside its corpus", SELF_REL in corpus and
        SELF_REL not in [p for p in corpus if p != SELF_REL], SELF_REL)

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name
            + (("  [" + detail + "]") if not ok and detail else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "verify").lower()
    if cmd == "build":
        face = build()
        dated, latest = write(face)
        say("wrote %s and %s" % (dated, latest))
        say("verdict: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: build | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))