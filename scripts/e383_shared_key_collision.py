"""E383 -- how many distinct files on disk are named by one published face key, and who reads a merged one.

``e350._face_key`` keeps the path from the first recognised root and falls back to the basename
otherwise; its own docstring calls that the unsafe direction because two unresolved ``meta.json``
reads merge.  E381 then showed the fallback firing on a path that *did* resolve -- the join was
keyed by its operands -- which makes the fallback live ammunition rather than a footnote.

So ask the collision question directly, in the direction a census cannot see:

  * the population is every face-shaped path value in the same corpus E350/E353/E377 walk, read from
    load bindings AND dump sinks (the two halves of the published key set);
  * two values that differ only by ``./`` or a backslash are ONE file, so normalise before counting
    -- otherwise the census invents a collision out of spelling;
  * a key with two or more distinct normalised values that resolve to two or more distinct existing
    files is a merged face: the census cannot tell those files apart;
  * a published face that lists a merged key in a list of keys is consuming the merge.

The bill is the collision table plus the sentence that consumes it, not a count.  Nothing here
rewrites the published E350/E353/E377 faces; they are read as published.

Usage:
  python scripts/e383_shared_key_collision.py run       # build the face
  python scripts/e383_shared_key_collision.py verify    # re-derive the arithmetic
  python scripts/e383_shared_key_collision.py selftest  # offline fixture legs
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

TODAY = "2026-11-03"
FACE = "COLLISIONKEY-%s.json" % TODAY
LATEST = "collisionkey_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E383_shared_key_collision"
SELF_REL = "scripts/e383_shared_key_collision.py"
# This study's own outputs are named here so they cannot enter the published-face scan on the next
# run: the scan reads the directory it publishes into (E319/E327 family).
OWN_FILES = ("collisionkey_latest.json", FACE)
MAX_ROWS = 300
MAX_CONSUMERS = 400

ROLE_READ = "read"
ROLE_WRITE = "write"

V_CONSUMED = ("one_key_names_two_or_more_files_on_disk_and_a_published_face_lists_that_key_beside_"
              "other_keys_so_the_census_treats_two_files_as_one_face")
V_MERGED_UNREAD = ("one_key_names_two_or_more_files_on_disk_but_no_published_face_consumes_the_"
                   "merged_key_so_the_merge_costs_no_published_number_yet")
V_NO_COLLISION = ("no_key_names_two_files_on_disk_so_the_basename_fallback_merges_nothing_here")
V_EMPTY = "the_corpus_named_no_face_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ the values, and the key they land under

def _norm(value):
    """One spelling per file: the normalisation ``_face_key`` itself applies."""
    return value.replace("\\", "/").strip("./")


def _is_face_value(value):
    return _norm(value).endswith((".json", ".jsonl"))


def keyed_sites(sources):
    """``{key: {"values": set, "sites": [row]}}`` over load bindings and dump sinks.

    Both halves are walked because the published key set is their union: a writer-only key is as
    much a face identity as a reader's key, and a collision in either half merges two files for the
    same census.
    """
    keyed = {}
    parsed = 0
    read_rows = 0
    write_rows = 0
    for rel, text in sources:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        parsed += 1
        consts = e347.constants(tree)
        for row in e347.load_bindings(tree, consts):
            read_rows += 1
            _add(keyed, rel, row["line"], ROLE_READ, row["values"])
        for line, values in _dump_rows(tree, consts):
            write_rows += 1
            _add(keyed, rel, line, ROLE_WRITE, values)
    return {"keyed": keyed, "parsed": parsed, "read_rows": read_rows, "write_rows": write_rows}


def _dump_rows(tree, consts):
    """``[(line, values)]`` for json.dump destinations, mirroring ``e350._dump_sinks`` exactly.

    The published helper keeps only ``{variable: [keys]}``, so the line that produced a key is not
    recoverable from it; a collision table without the line would be a decree.
    """
    handles = e347.file_handles(tree, consts)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if e347._fname(node.func) != "dump" or len(node.args) < 2:
            continue
        if not isinstance(node.args[0], ast.Name):
            continue
        path_arg = node.args[1]
        values = []
        if isinstance(path_arg, ast.Name) and path_arg.id in handles:
            values.extend(handles[path_arg.id])
        values.extend(e347.values_in(path_arg, consts))
        out.append((node.lineno, values))
    return out


def _add(keyed, rel, line, role, values):
    for value in values:
        if not _is_face_value(value):
            continue
        norm = _norm(value)
        key = e350._face_key(value)
        if not key:
            continue
        slot = keyed.setdefault(key, {"values": set(), "sites": []})
        slot["values"].add(norm)
        entry = {"source": rel, "line": line, "role": role, "value": norm}
        if entry not in slot["sites"]:
            slot["sites"].append(entry)


# Resolving a folded value against the repo root alone would call ``prospect_paper/_summary.json``
# unresolved: that value is relative to the directory its producer was writing into, and nothing in
# the source says which.  A suffix match against one index of the tree is the weakest claim that
# still distinguishes two files, and the hit count is published per value, so a value that names
# many files is never counted as one identified file.
SKIP_DIRS = frozenset((".git", "__pycache__", ".codely-cli", "media", "legacy", "Money02"))
_INDEX = None

STATE_TWO_FILES = "two_identified_files"
STATE_MANY = "a_value_names_many_files"
STATE_ALIAS = "one_file_two_spellings"
STATE_UNRESOLVED = "no_value_names_a_file"

BASES_NOTE = ("a folded value is resolved by suffix against one index of the tree (a value with "
              "exactly one hit is an identified file; a value with two or more hits is published "
              "as ambiguous and never counted as one file); absolute values are tested on disk "
              "directly")


def _file_index():
    """``{basename: [repo-relative posix paths]}`` -- built once per process, skipped dirs excluded."""
    global _INDEX
    if _INDEX is None:
        index = {}
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            rel_dir = os.path.relpath(dirpath, ROOT).replace("\\", "/")
            for name in filenames:
                rel = name if rel_dir == "." else rel_dir + "/" + name
                index.setdefault(name, []).append(rel)
        _INDEX = index
    return _INDEX


def _resolve(value):
    """Every repo-relative file a folded value can name, by suffix; ``[]`` when it names none."""
    v = value.strip()
    if (len(v) > 1 and v[1] == ":") or v.startswith("/"):
        path = os.path.normpath(v)
        if not os.path.isfile(path):
            return []
        try:
            return [os.path.relpath(path, ROOT).replace("\\", "/")]
        except ValueError:
            return []
    base = v.rsplit("/", 1)[-1]
    return sorted({rel for rel in _file_index().get(base, ())
                   if rel == v or rel.endswith("/" + v)})


def collision_rows(keyed):
    """One row per key that names more than one file.

    Four states, because they are four different repairs:
      * ``two_identified_files`` -- two values each naming exactly one file, and different files:
        the census merges two faces it could have told apart;
      * ``a_value_names_many_files`` -- a value that names several files by itself (a bare
        basename from a join that did not fold): the key is coarser than any one file;
      * ``one_file_two_spellings`` -- the same file written two ways: normalisation's job, not a
        collision;
      * ``no_value_names_a_file`` -- nothing resolves here, so the merge is stated but unpriced.
    """
    rows = []
    for key, slot in keyed.items():
        values = sorted(slot["values"])
        if len(values) < 2:
            continue
        resolved = {v: _resolve(v) for v in values}
        ambiguous = [(v, len(files)) for v, files in resolved.items() if len(files) > 1]
        identified = sorted({f for files in resolved.values() if len(files) == 1 for f in files})
        if len(identified) >= 2:
            state = STATE_TWO_FILES
        elif ambiguous:
            state = STATE_MANY
        elif len(identified) == 1:
            state = STATE_ALIAS
        else:
            state = STATE_UNRESOLVED
        rows.append({"key": key,
                     "files_on_disk": len(identified),
                     "identified_files": identified[:8],
                     "identified_files_truncated": max(0, len(identified) - 8),
                     "values": values[:12],
                     "values_truncated": max(0, len(values) - 12),
                     "state": state,
                     "ambiguous_values": [{"value": v, "files": n} for v, n in ambiguous[:6]],
                     "basename_fallback": "/" not in key,
                     "sites": sorted(slot["sites"], key=lambda s: (s["source"], s["line"]))[:12],
                     "site_count": len(slot["sites"]),
                     "roles": sorted({s["role"] for s in slot["sites"]})})
    order = {STATE_TWO_FILES: 0, STATE_MANY: 1, STATE_ALIAS: 2, STATE_UNRESOLVED: 3}
    rows.sort(key=lambda r: (order[r["state"]], -r["files_on_disk"], r["key"]))
    return rows


# ------------------------------------------------------------------ who consumes a merged key

def published_faces():
    """Every published census face in ``results/state_tilt`` except this study's own."""
    out = []
    if not os.path.isdir(PUBLISHED_DIR):
        return out
    for name in sorted(os.listdir(PUBLISHED_DIR)):
        if not name.endswith(".json") or name in OWN_FILES:
            continue
        path = os.path.join(PUBLISHED_DIR, name)
        try:
            with io.open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:  # noqa: BLE001 -- an unreadable face is not evidence of anything
            continue
        out.append((name, data))
    return out


def _walk_strings(node, path="$"):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _walk_strings(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_strings(v, "%s[%d]" % (path, i))


def _siblings_are_keys(container, keys):
    """Is this list a list of face keys, i.e. does a key stand beside other keys?

    A key quoted in a sentence is a mention; a key in a list whose other members are keys is the
    census using it as one identity.  Both shapes occur: a list of key strings and a list of row
    dicts each carrying a ``face`` field.  The distinction is what makes "consumed" a measurement
    instead of a keyword hit.
    """
    if not isinstance(container, list) or len(container) < 2:
        return False
    hits = 0
    for element in container:
        if isinstance(element, str):
            if element in keys:
                hits += 1
        elif isinstance(element, dict):
            if any(isinstance(v, str) and v in keys for v in element.values()):
                hits += 1
    return hits >= 2


def consumer_scan(keys, faces=None):
    """Published faces that quote a merged key, with the JSON pointer and whether it is a key list."""
    faces = faces if faces is not None else published_faces()
    rows = []
    for name, data in faces:
        for path, value in _walk_strings(data):
            if value not in keys:
                continue
            rows.append({"face": "results/state_tilt/" + name, "pointer": path, "key": value,
                         "field": _field_name(path),
                         "in_list_of_keys": _siblings_are_keys(_sibling_list(data, path), keys)})
            if len(rows) >= MAX_CONSUMERS:
                return rows
    return rows


def _field_name(pointer):
    """The name of the field a quoted string sits in, e.g. ``face``, ``path``, ``published_keys``."""
    parts = _pointer_parts(pointer)
    for part in reversed(parts):
        if isinstance(part, str):
            return part
    return ""


def _sibling_list(data, pointer):
    """The nearest list enclosing the string at ``pointer``, climbing through dicts.

    A key stored as ``rows[i].face`` has no direct list parent, and that shape is exactly how the
    published census faces list faces; a strict parent test would call every real consumption a
    mention.
    """
    node, chain = data, []
    for part in _pointer_parts(pointer):
        chain.append(node)
        try:
            node = node[part]
        except Exception:  # noqa: BLE001 -- a pointer that does not resolve names no container
            return None
    for container in reversed(chain):
        if isinstance(container, list):
            return container
    return None


def _pointer_parts(pointer):
    parts, buf, i = [], "", 0
    while i < len(pointer):
        ch = pointer[i]
        if ch == "$":
            i += 1
            continue
        if ch in ".[":
            if buf:
                parts.append(buf)
                buf = ""
            if ch == "[":
                close = pointer.index("]", i)
                parts.append(int(pointer[i + 1:close]))
                i = close + 1
                continue
            i += 1
            continue
        if ch == "]":
            i += 1
            continue
        buf += ch
        i += 1
    if buf:
        parts.append(buf)
    return parts


# ------------------------------------------------------------------ build

def decide(summary):
    if not summary.get("keys"):
        return V_EMPTY
    if not summary.get("keys_naming_two_or_more_files"):
        return V_NO_COLLISION
    if summary.get("merged_keys_listed_beside_other_keys"):
        return V_CONSUMED
    return V_MERGED_UNREAD


def build(write_face=True):
    srcs = [(rel, text) for rel, text in e350._sources() if rel != SELF_REL]
    say("corpus: %d sources" % len(srcs))
    scanned = keyed_sites(srcs)
    keyed = scanned["keyed"]
    rows = collision_rows(keyed)
    two = [r for r in rows if r["state"] == STATE_TWO_FILES]
    many = [r for r in rows if r["state"] == STATE_MANY]
    alias = [r for r in rows if r["state"] == STATE_ALIAS]
    unresolved = [r for r in rows if r["state"] == STATE_UNRESOLVED]
    merged = [r for r in rows if r["state"] in (STATE_TWO_FILES, STATE_MANY)]
    say("keys %d | keys naming 2+ values %d | two identified files %d | value names many %d "
        "| alias %d | unresolved %d"
        % (len(keyed), len(rows), len(two), len(many), len(alias), len(unresolved)))

    consumers = consumer_scan({r["key"] for r in merged})
    listed = [c for c in consumers if c["in_list_of_keys"]]
    say("published faces quoting a merged key: %d rows (%d of them in a list of keys)"
        % (len(consumers), len(listed)))

    key_table = []
    for row in merged:
        rows_for_key = [c for c in listed if c["key"] == row["key"]]
        consumers_for_key = sorted({c["face"] for c in consumers if c["key"] == row["key"]})
        key_table.append({"key": row["key"], "state": row["state"],
                          "files_on_disk": row["files_on_disk"],
                          "identified_files": row["identified_files"][:4],
                          "consumer_faces": consumers_for_key[:6],
                          "consumer_face_count": len(consumers_for_key),
                          "counted_consumptions": len(rows_for_key),
                          "first_counted": rows_for_key[0] if rows_for_key else None})

    faces = published_faces()
    summary = {
        "corpus_sources": len(srcs),
        "sources_parsed": scanned["parsed"],
        "read_rows": scanned["read_rows"],
        "write_rows": scanned["write_rows"],
        "keys": len(keyed),
        "keys_with_multiple_values": len(rows),
        "keys_naming_two_or_more_files": len(merged),
        "keys_merging_two_identified_files": len(two),
        "keys_coarser_than_any_one_file": len(many),
        "keys_alias_only": len(alias),
        "keys_unresolved_values": len(unresolved),
        "keys_with_basename_fallback": sum(1 for r in merged if r["basename_fallback"]),
        "files_merged_by_a_key": sum(r["files_on_disk"] for r in two),
        "largest_identified_merge": max([r["files_on_disk"] for r in two] or [0]),
        "published_faces_scanned": len(faces),
        "merged_keys_quoted_by_a_published_face": len(consumers),
        "merged_keys_listed_beside_other_keys": len(listed),
        "distinct_merged_keys_consumed": len({c["key"] for c in listed}),
        "keying_scope": ("the population is load bindings AND dump sinks, the union the published "
                         "key set is built from; json.dump rows keep the published helper's "
                         "'target must be a Name' condition so a writer-only key is counted "
                         "exactly when E350 counts it"),
        "normalisation": ("values are compared after the same replace('\\\\','/').strip('./') the "
                          "key helper applies, so two spellings of one file never count as a "
                          "collision"),
        "resolution": BASES_NOTE,
        "consumer_test": ("a quoted key is 'consumed as one face' only when it sits in a list with "
                          "at least one other key; a key inside a sentence is a mention and is "
                          "reported separately in consumer_rows"),
    }

    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "summary": summary,
        "collisions": rows[:MAX_ROWS],
        "collisions_truncated": max(0, len(rows) - MAX_ROWS),
        "merged_key_table": key_table,
        "consumer_rows": consumers,
        "consumer_rows_truncated": max(0, len(consumers) - MAX_CONSUMERS),
        "verdict": decide(summary),
        "bound": ("a collision is a property of one key under one reading of the corpus: two values "
                  "that normalise apart and each resolve to a file.  A value that resolves to no "
                  "file, or to many, is published under its own state and is never counted as one "
                  "identified file, so the headline under-reports rather than invents.  The "
                  "published E350/E353/E377 faces are read, never rebuilt or rewritten.  Several of "
                  "the consuming faces are themselves keying studies (E380/E381 report the same "
                  "key set), so a consumption count is not a claim that many independent readers "
                  "rely on the merge."),
    }
    if write_face:
        for target in (os.path.join(PUBLISHED_DIR, FACE), os.path.join(PUBLISHED_DIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(PUBLISHED_DIR, FACE))
    return face


def verify():
    """Re-derive what needs no corpus scan: the row arithmetic, the states, the verdict."""
    path = os.path.join(PUBLISHED_DIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    summary = face.get("summary") or {}
    rows = face.get("collisions") or []
    truncated = face.get("collisions_truncated") or 0
    if len(rows) + truncated != summary.get("keys_with_multiple_values"):
        problems.append("the collision list does not re-add to the multi-value key count")
    by_state = {}
    for row in rows:
        by_state[row.get("state")] = by_state.get(row.get("state"), 0) + 1
        if row.get("state") not in (STATE_TWO_FILES, STATE_MANY, STATE_ALIAS, STATE_UNRESOLVED):
            problems.append("a row carries an unknown state: %s" % row.get("key"))
            break
        if len(row.get("values") or []) < 2 and not row.get("values_truncated"):
            problems.append("a collision row names fewer than two values: %s" % row.get("key"))
            break
        if row.get("site_count", 0) < 1 or not row.get("sites"):
            problems.append("a collision row names no site: %s" % row.get("key"))
            break
        if row.get("state") == STATE_TWO_FILES:
            if row.get("files_on_disk", 0) < 2:
                problems.append("a two-file row names fewer than two files: %s" % row.get("key"))
                break
            if len(row.get("identified_files") or []) \
                    + (row.get("identified_files_truncated") or 0) != row.get("files_on_disk"):
                problems.append("a two-file row's file list does not match its count: %s"
                                % row.get("key"))
        if row.get("state") == STATE_MANY and not row.get("ambiguous_values"):
            problems.append("an ambiguous row names no ambiguous value: %s" % row.get("key"))
            break
        if row.get("state") == STATE_ALIAS and row.get("files_on_disk", 0) > 1:
            problems.append("an alias row names two files: %s" % row.get("key"))
            break
        if row.get("state") == STATE_UNRESOLVED and row.get("files_on_disk", 0) != 0:
            problems.append("an unresolved row names a file: %s" % row.get("key"))
            break
    if not truncated:
        for state, key in ((STATE_TWO_FILES, "keys_merging_two_identified_files"),
                           (STATE_MANY, "keys_coarser_than_any_one_file"),
                           (STATE_ALIAS, "keys_alias_only"),
                           (STATE_UNRESOLVED, "keys_unresolved_values")):
            if by_state.get(state, 0) != summary.get(key):
                problems.append("the %s rows do not re-add to %s" % (state, key))
    if sum(summary.get(k) or 0 for k in ("keys_merging_two_identified_files",
                                         "keys_coarser_than_any_one_file",
                                         "keys_alias_only",
                                         "keys_unresolved_values")) != summary.get(
            "keys_with_multiple_values"):
        problems.append("the four states do not partition the multi-value keys")
    if sum(summary.get(k) or 0 for k in ("keys_merging_two_identified_files",
                                         "keys_coarser_than_any_one_file")) != summary.get(
            "keys_naming_two_or_more_files"):
        problems.append("the merged count is not the two merged states")
    if (summary.get("largest_identified_merge") or 0) < 2 \
            and summary.get("keys_merging_two_identified_files"):
        problems.append("a two-file key exists but the largest merge is smaller than two files")
    cons = face.get("consumer_rows") or []
    listed = [c for c in cons if c.get("in_list_of_keys")]
    if len(cons) != summary.get("merged_keys_quoted_by_a_published_face"):
        problems.append("the consumer rows do not re-add to their published count")
    if len(listed) != summary.get("merged_keys_listed_beside_other_keys"):
        problems.append("the listed consumer rows do not re-add to their published count")
    merged = {r["key"] for r in rows if r.get("state") in (STATE_TWO_FILES, STATE_MANY)}
    for c in cons:
        if c.get("key") not in merged:
            problems.append("a consumer quotes a key that is not a merged face: %s" % c.get("key"))
            break
        if not c.get("pointer", "").startswith("$"):
            problems.append("a consumer row carries no pointer: %s" % c.get("key"))
            break
    table = face.get("merged_key_table") or []
    if len(table) != summary.get("keys_naming_two_or_more_files"):
        problems.append("the merged-key table does not hold one row per merged key")
    if sum(t.get("counted_consumptions") or 0 for t in table) != \
            summary.get("merged_keys_listed_beside_other_keys"):
        problems.append("the table's counted consumptions do not re-add to the summary")
    if sum(1 for t in table if (t.get("counted_consumptions") or 0) > 0) != \
            summary.get("distinct_merged_keys_consumed"):
        problems.append("the table's consumed-key count does not re-add to the summary")
    if {t.get("key") for t in table} != merged:
        problems.append("the table names a different set of keys than the merged rows")
    if face.get("verdict") != decide(summary):
        problems.append("the verdict does not re-derive from the summary")
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ------------------------------------------------------------------ selftest

FIXT_BASENAME = '''
import json
def main():
    a = json.load(open("a/meta.json", encoding="utf-8"))
    b = json.load(open("b/meta.json", encoding="utf-8"))
    c = json.load(open(p, encoding="utf-8"))
    return a, b, c
'''


def _fixture_keyed(text):
    tree = ast.parse(text)
    consts = e347.constants(tree)
    keyed = {}
    for row in e347.load_bindings(tree, consts):
        _add(keyed, "fixture.py", row["line"], ROLE_READ, row["values"])
    return keyed


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    keyed = _fixture_keyed(FIXT_BASENAME)
    rows = collision_rows(keyed)
    leg("two basename reads that fall back collide on the shared basename",
        any(r["key"] == "meta.json" and len(r["values"]) == 2 for r in rows),
        str([(r["key"], r["values"]) for r in rows])[:160])
    leg("a caller-supplied destination contributes no value, so the key holds only the two paths",
        list(keyed) == ["meta.json"] and len(keyed["meta.json"]["values"]) == 2,
        str(keyed))

    leg("normalisation merges two spellings of one file -- alias is not a collision",
        _norm("./results/a.json") == _norm("results\\a.json") == "results/a.json")
    leg("two distinct paths under one root keep distinct keys",
        e350._face_key("results/a/latest.json") != e350._face_key("results/b/latest.json"))
    leg("the basename fallback is what makes them equal",
        e350._face_key("a/latest.json") == e350._face_key("b/latest.json") == "latest.json")
    leg("a .jsonl face is face-shaped here even though the published helpers key only .json",
        _is_face_value("results/runs.jsonl") and not _is_face_value("results/runs.parquet"))

    # The alias/unresolved/merged split is measured against the tree, so it is exercised on paths
    # that exist in this repository (they are stable fixtures: trial_labor_w1 and w10 prep_state).
    real = collision_rows({
        "prep_state.json": {"values": {"trial_labor_w1/prep_state.json",
                                       "trial_labor_w10/prep_state.json"},
                            "sites": [{"source": "s.py", "line": 1, "role": ROLE_READ,
                                       "value": "trial_labor_w1/prep_state.json"}]},
        "fleet/machines/bm-a.json": {
            "values": {"fleet/machines/bm-a.json",
                       os.path.join(ROOT, "fleet", "machines", "bm-a.json").replace("\\", "/")},
            "sites": [{"source": "s.py", "line": 2, "role": ROLE_READ,
                       "value": "fleet/machines/bm-a.json"}]},
        "a.json": {"values": {"ghost_x/a.json", "ghost_y/a.json"},
                   "sites": [{"source": "s.py", "line": 3, "role": ROLE_READ,
                              "value": "ghost_x/a.json"}]},
    })
    states = {r["key"]: r["state"] for r in real}
    leg("two values naming two different files on disk are a two-file collision",
        states.get("prep_state.json") == STATE_TWO_FILES, str(states))
    leg("a two-file row carries the identified files themselves, not just a count",
        (lambda row: len(row["identified_files"]) == min(row["files_on_disk"], 8)
         and row["files_on_disk"] >= 2)([r for r in real if r["key"] == "prep_state.json"][0]))
    leg("one file written twice (absolute and relative) is an alias, not a collision",
        states.get("fleet/machines/bm-a.json") == STATE_ALIAS, str(states))
    leg("values that name no file are published as unresolved, not as a merge",
        states.get("a.json") == STATE_UNRESOLVED, str(states))
    leg("an unresolved row names zero files",
        [r for r in real if r["key"] == "a.json"][0]["files_on_disk"] == 0)

    keys = {"latest.json", "results/a/latest.json"}
    leg("a key listed beside another key is a consumption",
        _siblings_are_keys(["results/a/latest.json", "latest.json"], keys))
    leg("a key alone in a one-element list is a mention, not a list of keys",
        not _siblings_are_keys(["latest.json"], keys))
    leg("a key in a sentence is not a key list",
        not _siblings_are_keys(["see latest.json for the numbers"], keys))

    leg("a list of row dicts carrying a face field is a list of keys",
        _siblings_are_keys([{"face": "results/a/latest.json"}, {"face": "latest.json"}], keys))
    leg("a key whose only sibling is a non-key string is not a key list",
        not _siblings_are_keys(["results/a/latest.json", "and that is the story"], keys))

    face = {"rows": [{"face": "results/a/latest.json"}, {"face": "latest.json"}],
            "note": "latest.json"}
    cons = consumer_scan(keys, faces=[("f_latest.json", face)])
    leg("the consumer walk finds the key in the key list and in a bare scalar alike",
        len(cons) == 3, str([(c["pointer"], c["in_list_of_keys"]) for c in cons]))
    leg("only the two rows are credited as a consumption; the scalar is a mention",
        sum(1 for c in cons if c["in_list_of_keys"]) == 2,
        str([(c["pointer"], c["in_list_of_keys"]) for c in cons]))
    leg("a bare scalar mention is not credited as a consumption",
        [c for c in cons if c["pointer"].endswith(".note")][0]["in_list_of_keys"] is False)

    leg("a merged key with no consumer still gets a verdict",
        decide({"keys": 3, "keys_naming_two_or_more_files": 1,
                "merged_keys_listed_beside_other_keys": 0}) == V_MERGED_UNREAD)
    leg("the consumed verdict requires a key list, not just a quote",
        decide({"keys": 3, "keys_naming_two_or_more_files": 1,
                "merged_keys_quoted_by_a_published_face": 5,
                "merged_keys_listed_beside_other_keys": 0}) == V_MERGED_UNREAD)
    leg("the consumed verdict is reachable",
        decide({"keys": 3, "keys_naming_two_or_more_files": 1,
                "merged_keys_listed_beside_other_keys": 1}) == V_CONSUMED)
    leg("no merged key means the fallback merges nothing here",
        decide({"keys": 3, "keys_naming_two_or_more_files": 0}) == V_NO_COLLISION)
    leg("no key is no claim", decide({"keys": 0}) == V_EMPTY)

    leg("the pointer resolver climbs to the nearest list, through dicts",
        _sibling_list({"a": [{"b": "x"}]}, "$.a[0].b") == [{"b": "x"}]
        and _sibling_list({"a": {"b": "x"}}, "$.a.b") is None)
    leg("the field a quote sits in is recoverable from the pointer, list indices skipped",
        _field_name("$.rows[3].published_keys[0]") == "published_keys"
        and _field_name("$.note") == "note")

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