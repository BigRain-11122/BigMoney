"""E466 -- does a face pointer resolve, and is it the join anyone uses?

E464 found that every face in its (tiny, four-face) population also carries a pointer key --
source_face / face / face_path -- and that on NAMERESOLVE the pointer is the only exact identity
match while both study voices are slugs.  That population was four faces.  Nothing had asked the
question tree-wide: of every face under results/ that carries one of those keys, does the value
NAME a file at all, does it resolve against the working tree, and does any source outside the
producer ever READ it to reach the upstream face?

The measurement is deliberately three-layered, because the first draft of this study (and E207
before it) learned that a key name is not a measurement:

  FORM     what the value is: a path with a .json suffix, a path-like string without one, a bare
           face stem, or free text.  The key named `face` is asked this question first; only a
           path can be resolved, so a stem or a label is published as a form and never counted as
           a broken pointer.
  RESOLVE  for path forms: does it resolve from the repo root, only from the pointing face's own
           directory, as an absolute path on this box, or nowhere?  Separators are normalised
           explicitly (backslash -> forward) so the answer does not depend on the host parser, and
           the spelling that would fail on a POSIX reader is published apart.
  JOIN     over the .py corpus, which sources name the target path (or its basename) as a string,
           and -- of those -- which are not the producer of the pointing face.  A reader that
           only keys on the literal word "face" is counted separately, because reading a key name
           is not reading a pointer.

Residue is split three ways and none of the three is folded into another: a path that names a file
on disk, a path that names a file that exists only in git history, a path that never existed.

Run:      python scripts/e466_pointer_join.py run
Verify:   python scripts/e466_pointer_join.py verify     (re-derives from the live tree)
Check:    python scripts/e466_pointer_join.py check      (tallies re-derive from the face)
Selftest: python scripts/e466_pointer_join.py selftest
"""

import argparse
import ast
import datetime
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text)
import e461_identity_consumers as e461  # noqa: E402  (string_constants)
import e464_producer_intent as e464  # noqa: E402  (face_stem / write_sites)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "pointerjoin_latest.json"
DATED_PREFIX = "POINTERJOIN"
CARD = "E466-DOES-A-FACE-POINTER-RESOLVE-AND-IS-IT-THE-JOIN-ANYONE-USES"

POINTER_KEYS = ("source_face", "face", "face_path")

F_PATH = "names_a_path_with_a_json_suffix"
F_PATH_NO_JSON = "names_a_path_without_a_json_suffix"
F_TOKEN = "is_a_single_token_that_has_not_been_resolved_yet"
F_STEM = "names_a_face_that_exists_on_disk"
F_LEAF = "is_a_token_that_names_no_face_on_disk"
F_LABEL = "carries_free_text_not_a_pointer"
FORMS = (F_PATH, F_PATH_NO_JSON, F_STEM, F_LEAF, F_LABEL)

S_BARE = "bare_filename_no_directory"
S_FORWARD = "forward_separated_relative_path"
S_BACKSLASH = "backslash_separated_relative_path"
S_MIXED = "mixed_separators"
S_ABS = "absolute_path_on_this_machine"
SPELLINGS = (S_BARE, S_FORWARD, S_BACKSLASH, S_MIXED, S_ABS)

B_ROOT = "repo_root"
B_OWN = "the_pointing_faces_own_directory"
B_ABS = "as_an_absolute_path"
B_NONE = "nowhere_on_disk"

R_ON_DISK = "names_a_file_on_disk"
R_HISTORY = "names_a_file_that_exists_only_in_git_history"
R_NEVER = "names_a_path_that_never_existed"
RESIDUES = (R_ON_DISK, R_HISTORY, R_NEVER)

V_EMPTY = "no_face_carries_a_pointer_key"
V_NEVER = "some_pointers_name_a_path_that_never_existed"
V_HISTORY = "some_pointers_name_a_file_that_exists_only_in_git_history"
V_JOINED = "some_source_outside_a_producer_turns_a_source_face_or_face_path_value_into_a_path"
V_ROWSCHEMA = ("only_the_generic_face_key_flows_into_a_path_and_every_candidate_read_site_"
               "names_a_row_the_source_built_itself")
V_UNJOINED = ("every_path_form_pointer_resolves_on_disk_and_no_source_outside_a_producer_"
              "turns_one_into_a_path")
VERDICT_VOCAB = (V_EMPTY, V_NEVER, V_HISTORY, V_JOINED, V_ROWSCHEMA, V_UNJOINED)

NON_GENERIC_KEYS = ("source_face", "face_path")

NO_WRITER = "no_source_in_the_corpus_writes_this_face"

MAX_READ_BYTES = 2 * 1024 * 1024
MAX_ROWS = 600
SKIP_DIRS = (".git", ".codely-cli", "_smoke", "_quarantine", "__pycache__")
# The identity family reads names as names; it writes faces of its own and must not be counted as a
# consumer of the family it is measuring (E180/E207 self-inclusion law).
SELF_SKIP = ("e461_", "e462_", "e463_", "e464_", "e466_", "run_e461", "run_e462", "run_e463",
             "run_e464", "run_e465")


# ----------------------------------------------------------------------------- helpers


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


def spelling_of(value):
    v = value.strip()
    if re.match(r"^[A-Za-z]:[\\/]", v) or v.startswith("\\\\"):
        return S_ABS
    has_b = "\\" in v
    has_f = "/" in v
    if has_b and has_f:
        return S_MIXED
    if has_b:
        return S_BACKSLASH
    if has_f:
        return S_FORWARD
    return S_BARE


def normalise(value):
    """Backslashes are folded on purpose: a published answer must not depend on the host parser."""
    return value.strip().replace("\\", "/")


PATH_SEGMENT_RE = re.compile(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)+$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


def form_of(value):
    """Lexical form only.  A label that happens to contain a slash is still a label.

    The first draft let any string with a "/" be a path, so "EXPLORATION/NEIGHBORHOOD deep-scan
    (no judgment)" was published as a pointer to a file that never existed.  A path is a token
    with no whitespace, not a sentence that mentions two words with a slash between them.
    """
    v = value.strip()
    if not v or re.search(r"\s", v):
        return F_LABEL
    norm = normalise(v)
    if norm.lower().endswith(".json"):
        return F_PATH
    if PATH_SEGMENT_RE.match(norm):
        return F_PATH_NO_JSON
    if TOKEN_RE.match(norm):
        return F_TOKEN
    return F_LABEL


def resolve_pointer(value, face_rel, root=None):
    """Three bases, published apart.  Nothing is inferred: each base is asked of the filesystem."""
    root = root or ROOT
    norm = normalise(value)
    out = {
        "value": value,
        "normalised": norm,
        "spelling": spelling_of(value),
        "resolves_from_repo_root": False,
        "resolves_from_the_pointing_faces_own_directory": False,
        "resolves_as_an_absolute_path": False,
    }
    if out["spelling"] == S_ABS:
        out["resolves_as_an_absolute_path"] = os.path.isfile(value)
    else:
        out["resolves_from_repo_root"] = os.path.isfile(os.path.join(root, norm))
        own_dir = os.path.dirname(face_rel)
        out["resolves_from_the_pointing_faces_own_directory"] = os.path.isfile(
            os.path.join(root, own_dir, norm))
    out["required_base"] = required_base(out)
    return out


def required_base(res):
    if res.get("resolves_from_repo_root"):
        return B_ROOT
    if res.get("resolves_from_the_pointing_faces_own_directory"):
        return B_OWN
    if res.get("resolves_as_an_absolute_path"):
        return B_ABS
    return B_NONE


def exists_in_git_history(norm_path, root=None):
    """A path that is not on disk: does any commit in any ref ever name it?"""
    root = root or ROOT
    try:
        p = subprocess.run(["git", "-C", root, "log", "--all", "--format=%h", "-1", "--",
                            norm_path], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return bool((p.stdout or "").strip())


def residue_of(value, face_rel, root=None, history_probe=None):
    """Three-way split.  A non-path value has no residue: it was never a pointer."""
    if form_of(value) not in (F_PATH, F_PATH_NO_JSON):
        return ""
    res = resolve_pointer(value, face_rel, root=root)
    if res["required_base"] != B_NONE:
        return R_ON_DISK
    probe = history_probe or exists_in_git_history
    if probe(normalise(value), root=root):
        return R_HISTORY
    return R_NEVER


# ----------------------------------------------------------------------------- corpus


def census(root=None):
    """Every (face, key, value) instance of a pointer key under results/, own outputs excluded."""
    root = root or ROOT
    rows = []
    files = 0
    errors = []
    skipped_large = 0
    non_string = {k: 0 for k in POINTER_KEYS}
    non_string_faces = set()
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "results")):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            if is_own_output(rel):
                continue
            files += 1
            try:
                if os.path.getsize(path) > MAX_READ_BYTES:
                    skipped_large += 1
                    continue
                payload = _load(path)
            except (OSError, ValueError):
                errors.append(rel)
                continue
            if not isinstance(payload, dict):
                continue
            for key in POINTER_KEYS:
                val = payload.get(key)
                if isinstance(val, str) and val.strip():
                    rows.append({"face": rel, "key": key, "value": val.strip()})
                elif isinstance(val, (dict, list)):
                    # the same key name also carries a provenance block (sha256/population) and
                    # never a path; it is outside this population and published as such
                    non_string[key] += 1
                    non_string_faces.add(rel)
    return rows, {"json_files_read": files, "parse_errors": errors,
                  "skipped_above_read_cap": skipped_large,
                  "non_string_pointer_values": non_string,
                  "faces_with_a_non_string_pointer_value": len(non_string_faces)}


def stem_index(root=None):
    """face stem -> the face files that carry it (reuses E464's stem rule, no second definition)."""
    root = root or ROOT
    idx = {}
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "results")):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            if is_own_output(rel):
                continue
            stem = e464.face_stem(name)
            if stem:
                idx.setdefault(stem, []).append(rel)
    return idx


def stem_resolves(value, idx):
    """A stem names a face when a file on disk carries that stem (or that stem plus a tail)."""
    text = value.strip()
    if not text.lower().endswith(".json"):
        text = text + ".json"  # a stem is a face name with the suffix left out
    stem = e464.face_stem(text)
    if not stem:
        return []
    if stem in idx:
        return list(idx[stem])
    tail = [s for s in idx if s.startswith(stem) and len(s) > len(stem)]
    if stem and len(stem) >= 6:
        return [p for s in tail for p in idx[s]]
    return []


PATH_CONSUMERS = ("open", "_load", "load", "loads", "read_text", "read_bytes", "isfile", "exists",
                  "Path", "join", "dirname", "basename", "stat", "getsize")


def _key_of(expr, keys):
    """The pointer key a read expression reads, or None."""
    if isinstance(expr, ast.Subscript):
        val = e464._const_str(expr.slice)
        if val in keys:
            return val
    elif isinstance(expr, ast.Call) and expr.args:
        fname = expr.func.attr if isinstance(expr.func, ast.Attribute) else ""
        if fname in ("get", "pop"):
            val = e464._const_str(expr.args[0])
            if val in keys:
                return val
    return None


def follows_pointer(tree, keys):
    """Which pointer keys this source turns into a filesystem path.

    Reading a key is not following it.  A follow is one of two shapes:

      named    x = payload.get("source_face")  ...  open(os.path.join(ROOT, x))
      inline   open(os.path.join(ROOT, payload["face"]))

    Anything else (x.get("sha256") on the value, a name that is never used as a path, a literal
    that merely spells the same file) is published as a reader that does not follow.
    """
    derived = {}
    inline = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            key = _key_of(node.value, keys)
            if key:
                derived[node.targets[0].id] = key
        elif isinstance(node, ast.Call):
            fname = node.func.attr if isinstance(node.func, ast.Attribute) else (
                node.func.id if isinstance(node.func, ast.Name) else "")
            if fname not in PATH_CONSUMERS:
                continue
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                key = _key_of(arg, keys)
                if key:
                    inline.add(key)
    path_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fname = node.func.attr if isinstance(node.func, ast.Attribute) else (
                node.func.id if isinstance(node.func, ast.Name) else "")
            if fname not in PATH_CONSUMERS:
                continue
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                path_names |= {n.id for n in ast.walk(arg) if isinstance(n, ast.Name)}
    followed = set(inline)
    for name, key in derived.items():
        if name in path_names:
            followed.add(key)
    return sorted(followed), sorted({k for k in derived.values()}), sorted(derived)


def read_sites(tree, keys):
    """[(key, how)] for every place the source READS a pointer key by its literal name."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            val = e464._const_str(node.slice)
            if val in keys:
                out.append((val, "subscript"))
        elif isinstance(node, ast.Call) and node.args:
            fname = node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if fname in ("get", "pop", "setdefault"):
                val = e464._const_str(node.args[0])
                if val in keys:
                    out.append((val, fname))
    return out


def reader_index(pointer_values, key_names):
    """Sources that name a target path/basename as a string, and sources that read a key name.

    Two stages on purpose: a text prefilter keeps the AST pass to the files that can possibly
    match (E442's lesson: parsing everything per site is the expensive part).

    Naming the exact string and naming only the basename are published apart: hundreds of scripts
    mention "compute_audit.json" without ever joining a face to its upstream through a pointer.
    """
    by_value = {}
    by_basename = {}
    key_reads = {}
    followers = {}
    derivers = {}
    basenames = sorted({os.path.basename(normalise(v)) for v in pointer_values if v})
    sources_scanned = 0
    for rel in e451.walk_py(ROOT):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        sources_scanned += 1
        keys_hit = [k for k in key_names
                    if ('"%s"' % k) in text or ("'%s'" % k) in text]
        names_hit = [b for b in basenames if b and b in text]
        if not keys_hit and not names_hit:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        lits = e461.string_constants(tree)
        for value in pointer_values:
            norm = normalise(value)
            if norm in lits or value in lits:
                by_value.setdefault(value, set()).add(rel)
            elif os.path.basename(norm) in lits:
                by_basename.setdefault(os.path.basename(norm), set()).add(rel)
        if keys_hit:
            sites = read_sites(tree, keys_hit)
            for key, how in sites:
                entry = key_reads.setdefault(key, {"sources": set(), "sites": 0,
                                                   "by_kind": {}})
                entry["sources"].add(rel)
                entry["sites"] += 1
                entry["by_kind"][how] = entry["by_kind"].get(how, 0) + 1
            followed, read_keys, derived = follows_pointer(tree, keys_hit)
            for key in followed:
                followers.setdefault(key, set()).add(rel)
            for key in read_keys:
                derivers.setdefault(key, set()).add(rel)
    return by_value, by_basename, key_reads, followers, derivers, sources_scanned


def producer_index():
    """Source -> face stems it writes (E464's data-flow writer test, not a name match)."""
    out = {}
    for rel in e451.walk_py(ROOT):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            tree = ast.parse(e451.read_text(path))
        except (SyntaxError, ValueError, OSError):
            continue
        stems = e464.write_sites(tree)
        if stems:
            out[rel] = stems
    return out


# ----------------------------------------------------------------------------- build


def build(write=True, root=None):
    root = root or ROOT
    rows, meta = census(root)
    values = sorted({r["value"] for r in rows if form_of(r["value"]) in (F_PATH, F_PATH_NO_JSON)})
    by_value, by_basename, key_reads, followers, derivers, py_scanned = reader_index(
        values, POINTER_KEYS)
    producers = producer_index()
    stems = stem_index(root)

    graded = []
    for row in rows:
        lexical = form_of(row["value"])
        form = F_STEM if (lexical == F_TOKEN and stem_resolves(row["value"], stems)) \
            else (F_LEAF if lexical == F_TOKEN else lexical)
        entry = {
            "face": row["face"],
            "key": row["key"],
            "value": row["value"],
            "form": form,
            "spelling": spelling_of(row["value"]),
        }
        if form in (F_PATH, F_PATH_NO_JSON):
            res = resolve_pointer(row["value"], row["face"], root=root)
            entry.update({
                "required_base": res["required_base"],
                "resolves_from_repo_root": res["resolves_from_repo_root"],
                "resolves_from_the_pointing_faces_own_directory":
                    res["resolves_from_the_pointing_faces_own_directory"],
                "resolves_as_an_absolute_path": res["resolves_as_an_absolute_path"],
            })
            entry["residue"] = (R_ON_DISK if res["required_base"] != B_NONE
                                else (R_HISTORY if exists_in_git_history(
                                    res["normalised"], root=root) else R_NEVER))
            exact = sorted(by_value.get(row["value"]) or [])
            stem = e464.face_stem(os.path.basename(row["face"]))
            face_producers = sorted(rel for rel, ws in producers.items() if stem in ws)
            entry["sources_naming_the_exact_string"] = exact
            entry["producers_of_the_pointing_face"] = face_producers
            entry["sources_outside_a_producer_naming_the_exact_string"] = [
                s for s in exact if s not in face_producers]
            entry["sources_naming_only_the_targets_basename"] = sorted(
                by_basename.get(os.path.basename(res["normalised"])) or [])
        else:
            entry["residue"] = ""
            entry["sources_naming_the_exact_string"] = []
            entry["producers_of_the_pointing_face"] = []
            entry["sources_outside_a_producer_naming_the_exact_string"] = []
            entry["sources_naming_only_the_targets_basename"] = []
            entry["stem_targets"] = (stem_resolves(row["value"], stems)[:5]
                                     if form == F_STEM else [])
        graded.append(entry)

    path_rows = [r for r in graded if r["form"] in (F_PATH, F_PATH_NO_JSON)]
    joiners = sorted({s for r in path_rows
                      for s in r["sources_outside_a_producer_naming_the_exact_string"]})
    weak = sorted({s for r in path_rows
                   for s in r["sources_naming_only_the_targets_basename"]
                   if s not in set(r["producers_of_the_pointing_face"] or [])})
    # who FOLLOWS a pointer rather than merely reading its key name: a source that turns the value
    # into a path, and is not the producer of a face that writes that key
    outside_followers = []
    outside_rowkey_followers = []
    for key in POINTER_KEYS:
        owners = set()
        for r in path_rows:
            if r["key"] == key:
                owners |= set(r["producers_of_the_pointing_face"] or [])
        hits = sorted(x for x in (followers.get(key) or set()) if x not in owners)
        if key in NON_GENERIC_KEYS:
            outside_followers.extend(hits)
        else:
            outside_rowkey_followers.extend(hits)
    outside_followers = sorted(set(outside_followers))
    outside_rowkey_followers = sorted(set(outside_rowkey_followers) - set(outside_followers))
    blocks = meta["faces_with_a_non_string_pointer_value"]

    summary = {
        "card": CARD,
        "corpus_sources": py_scanned,
        "json_files_read": meta["json_files_read"],
        "json_parse_errors": len(meta["parse_errors"]),
        "json_skipped_above_read_cap": meta["skipped_above_read_cap"],
        "faces_carrying_a_pointer_key": len({r["face"] for r in graded}),
        "pointer_instances": len(graded),
        "pointer_instances_by_key": {k: sum(1 for r in graded if r["key"] == k)
                                     for k in POINTER_KEYS},
        "value_form_by_key": {k: {f: sum(1 for r in graded if r["key"] == k and r["form"] == f)
                                  for f in FORMS} for k in POINTER_KEYS},
        "path_form_instances": len(path_rows),
        "path_form_instances_by_key": {k: sum(1 for r in path_rows if r["key"] == k)
                                       for k in POINTER_KEYS},
        "path_form_resolving_from_the_repo_root": sum(
            1 for r in path_rows if r["required_base"] == B_ROOT),
        "path_form_resolving_only_from_the_pointing_faces_own_directory": sum(
            1 for r in path_rows if r["required_base"] == B_OWN),
        "path_form_resolving_as_an_absolute_path": sum(
            1 for r in path_rows if r["required_base"] == B_ABS),
        "path_form_that_do_not_resolve": sum(1 for r in path_rows if r["required_base"] == B_NONE),
        "residue_classes": {c: sum(1 for r in path_rows if r["residue"] == c) for c in RESIDUES},
        "spelling_by_form": {s: sum(1 for r in graded if r["spelling"] == s and
                                    r["form"] in (F_PATH, F_PATH_NO_JSON)) for s in SPELLINGS},
        "spellings_a_posix_reader_would_reject": sum(
            1 for r in path_rows if r["spelling"] in (S_BACKSLASH, S_ABS, S_MIXED)),
        "stem_form_instances": sum(1 for r in graded if r["form"] == F_STEM),
        "token_instances_naming_no_face_on_disk": sum(
            1 for r in graded if r["form"] == F_LEAF),
        "label_form_instances": sum(1 for r in graded if r["form"] == F_LABEL),
        "faces_whose_face_key_is_a_path": len(
            {r["face"] for r in graded if r["key"] == "face" and
             r["form"] in (F_PATH, F_PATH_NO_JSON)}),
        "faces_whose_face_key_is_not_a_path": len(
            {r["face"] for r in graded if r["key"] == "face" and
             r["form"] not in (F_PATH, F_PATH_NO_JSON)}),
        "target_paths_named_by_a_source_outside_a_producer": len(joiners),
        "sources_outside_a_producer_that_name_a_target": joiners,
        "sources_naming_only_a_target_basename": len(weak),
        "sources_that_read_a_pointer_key_name": sorted(
            {x for v in key_reads.values() for x in v["sources"]}),
        "sources_that_derive_a_value_from_a_pointer_key": {
            k: sorted(v) for k, v in sorted(derivers.items())},
        "sources_that_turn_a_pointer_into_a_path": {
            k: sorted(v) for k, v in sorted(followers.items())},
        "sources_outside_a_producer_that_follow_a_pointer": outside_followers,
        "sources_outside_a_producer_that_follow_the_generic_face_key": outside_rowkey_followers,
        "faces_whose_pointer_key_is_a_block_not_a_string": blocks,
        "key_name_reads": {k: {"sources": len(v["sources"]), "sites": v["sites"],
                               "by_kind": v["by_kind"]}
                           for k, v in sorted(key_reads.items())},
        "faces_with_no_writer_in_the_corpus": sum(
            1 for r in path_rows if not r["producers_of_the_pointing_face"]),
    }
    face = {
        "card": CARD,
        "study": "E466",
        "title": "does a face pointer resolve, and is it the join anyone uses",
        "evidence_cutoff": datetime.date.today().isoformat(),
        "population_source": (
            "every *.json under results/ (own outputs excluded, .codely-cli/_smoke/_quarantine "
            "pruned) whose top level carries a non-empty string under one of "
            + "/".join(POINTER_KEYS) +
            "; read cap " + str(MAX_READ_BYTES) + " bytes; reader census over the .py corpus with "
            "the identity family excluded (" + "/".join(SELF_SKIP) + ")"),
        "verdict": verdict_for(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "forms": list(FORMS),
        "spellings": list(SPELLINGS),
        "residue_classes": list(RESIDUES),
        "summary": summary,
        "rows": graded[:MAX_ROWS],
        "parse_errors": meta["parse_errors"][:50],
        "method_limits": [
            "only top-level keys are asked; a pointer stored inside a row or a nested block is "
            "invisible here",
            "the three key names are the ones E464 found; a face that points at another with a "
            "fourth name is not in this population",
            "resolution asks the filesystem on this box: an absolute Windows path resolves here "
            "and would not resolve on another host, which is why the spelling is published apart",
            "a stem is counted as resolving only when a face file on disk carries that stem; a "
            "stem that names a directory leaf or a study (not a face) is published as unresolved "
            "and is not evidence of a broken pointer",
            "a reader is recognised through a string constant equal to the pointer value or its "
            "basename; a reader that assembles the path from parts is not resolved and is "
            "published as not naming the target",
            "the producer of the pointing face is resolved with E464's write-site data flow, so a "
            "path assembled by a function call makes the producer look like an outside reader",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"])):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
    return face


def restricted(rows):
    """Rows that can carry a join: a label is not a pointer, so it can never join anything."""
    return [r for r in rows if r["form"] in (F_PATH, F_PATH_NO_JSON)]


# ----------------------------------------------------------------------------- verdict


def verdict_for(summary):
    s = summary
    if not s.get("pointer_instances"):
        return V_EMPTY
    if s.get("residue_classes", {}).get(R_NEVER):
        return V_NEVER
    if s.get("residue_classes", {}).get(R_HISTORY):
        return V_HISTORY
    if s.get("sources_outside_a_producer_that_follow_a_pointer"):
        return V_JOINED
    if s.get("sources_outside_a_producer_that_follow_the_generic_face_key"):
        return V_ROWSCHEMA
    return V_UNJOINED


# ----------------------------------------------------------------------------- gates


def tally_problems(face):
    """Every published number must re-derive from the published rows."""
    problems = []
    s = face.get("summary", {})
    rows = face.get("rows") or []
    path_rows = [r for r in rows if r.get("form") in (F_PATH, F_PATH_NO_JSON)]
    if s.get("pointer_instances") != len(rows):
        problems.append("pointer instances %r != rows %r" % (s.get("pointer_instances"), len(rows)))
    if s.get("faces_carrying_a_pointer_key") != len({r.get("face") for r in rows}):
        problems.append("face count does not re-derive from the rows")
    for key in POINTER_KEYS:
        got = sum(1 for r in rows if r.get("key") == key)
        if (s.get("pointer_instances_by_key") or {}).get(key) != got:
            problems.append("instance count for key %s: published %r rows %r"
                            % (key, (s.get("pointer_instances_by_key") or {}).get(key), got))
        for form in FORMS:
            got = sum(1 for r in rows if r.get("key") == key and r.get("form") == form)
            if ((s.get("value_form_by_key") or {}).get(key) or {}).get(form) != got:
                problems.append("form %s for key %s: published %r rows %r"
                                % (form, key,
                                   ((s.get("value_form_by_key") or {}).get(key) or {}).get(form),
                                   got))
    if s.get("path_form_instances") != len(path_rows):
        problems.append("path-form total does not re-derive from the rows")
    for key in POINTER_KEYS:
        got = sum(1 for r in path_rows if r.get("key") == key)
        if (s.get("path_form_instances_by_key") or {}).get(key) != got:
            problems.append("path-form count for key %s does not re-derive" % key)
    for base, field in ((B_ROOT, "path_form_resolving_from_the_repo_root"),
                        (B_OWN, "path_form_resolving_only_from_the_pointing_faces_own_directory"),
                        (B_ABS, "path_form_resolving_as_an_absolute_path"),
                        (B_NONE, "path_form_that_do_not_resolve")):
        got = sum(1 for r in path_rows if r.get("required_base") == base)
        if s.get(field) != got:
            problems.append("%s: published %r rows %r" % (field, s.get(field), got))
    for c in RESIDUES:
        got = sum(1 for r in path_rows if r.get("residue") == c)
        if (s.get("residue_classes") or {}).get(c) != got:
            problems.append("residue class %s: published %r rows %r"
                            % (c, (s.get("residue_classes") or {}).get(c), got))
    for sp in SPELLINGS:
        got = sum(1 for r in rows if r.get("spelling") == sp and
                  r.get("form") in (F_PATH, F_PATH_NO_JSON))
        if (s.get("spelling_by_form") or {}).get(sp) != got:
            problems.append("spelling %s: published %r rows %r"
                            % (sp, (s.get("spelling_by_form") or {}).get(sp), got))
    if s.get("spellings_a_posix_reader_would_reject") != sum(
            1 for r in path_rows if r.get("spelling") in (S_BACKSLASH, S_ABS, S_MIXED)):
        problems.append("posix-hostile spelling total does not re-derive from the rows")
    if s.get("stem_form_instances") != sum(1 for r in rows if r.get("form") == F_STEM):
        problems.append("stem-form total does not re-derive from the rows")
    if s.get("token_instances_naming_no_face_on_disk") != sum(
            1 for r in rows if r.get("form") == F_LEAF):
        problems.append("token-with-no-face total does not re-derive from the rows")
    if s.get("label_form_instances") != sum(1 for r in rows if r.get("form") == F_LABEL):
        problems.append("label-form total does not re-derive from the rows")
    if s.get("faces_whose_face_key_is_a_path") != len(
            {r["face"] for r in rows if r.get("key") == "face" and
             r.get("form") in (F_PATH, F_PATH_NO_JSON)}):
        problems.append("face-key-as-path face total does not re-derive from the rows")
    if s.get("faces_whose_face_key_is_not_a_path") != len(
            {r["face"] for r in rows if r.get("key") == "face" and
             r.get("form") not in (F_PATH, F_PATH_NO_JSON)}):
        problems.append("face-key-as-not-a-path face total does not re-derive from the rows")
    if s.get("faces_with_no_writer_in_the_corpus") != sum(
            1 for r in path_rows if not r.get("producers_of_the_pointing_face")):
        problems.append("writerless-face total does not re-derive from the rows")
    joiners = sorted({x for r in path_rows
                      for x in (r.get("sources_naming_the_exact_string") or [])
                      if x not in set(r.get("producers_of_the_pointing_face") or [])})
    if s.get("target_paths_named_by_a_source_outside_a_producer") != len(joiners):
        problems.append("outside-reader total does not re-derive from the rows")
    if sorted(s.get("sources_outside_a_producer_that_name_a_target") or []) != joiners:
        problems.append("outside-reader list does not re-derive from the rows")
    weak = sorted({x for r in path_rows
                   for x in (r.get("sources_naming_only_the_targets_basename") or [])
                   if x not in set(r.get("producers_of_the_pointing_face") or [])})
    if s.get("sources_naming_only_a_target_basename") != len(weak):
        problems.append("basename-only reader total does not re-derive from the rows")
    if len({x for k, v in (s.get("sources_that_derive_a_value_from_a_pointer_key") or {}).items()
            for x in v} - set(s.get("sources_that_read_a_pointer_key_name") or [])):
        problems.append("a source derives a value from a key it never reads")
    if len({x for k, v in (s.get("sources_that_turn_a_pointer_into_a_path") or {}).items()
            for x in v} - set(s.get("sources_that_read_a_pointer_key_name") or [])):
        problems.append("a source turns a pointer into a path without reading the key")
    followers_all = sorted({x for k, v in
                            (s.get("sources_that_turn_a_pointer_into_a_path") or {}).items()
                            for x in v})
    if not set(s.get("sources_outside_a_producer_that_follow_a_pointer") or []) <= set(
            followers_all):
        problems.append("an outside follower is not in the follower lists")
    for r in rows:
        if r.get("key") not in POINTER_KEYS:
            problems.append("row %s carries a key outside the pointer vocabulary" % r.get("face"))
        if r.get("form") not in FORMS:
            problems.append("row %s carries a form outside the vocabulary" % r.get("face"))
        if r.get("spelling") not in SPELLINGS:
            problems.append("row %s carries a spelling outside the vocabulary" % r.get("face"))
        if r.get("form") in (F_PATH, F_PATH_NO_JSON):
            if r.get("residue") not in RESIDUES:
                problems.append("row %s path carries no residue class" % r.get("face"))
            if r.get("required_base") not in (B_ROOT, B_OWN, B_ABS, B_NONE):
                problems.append("row %s carries no required base" % r.get("face"))
            want = (R_ON_DISK if r.get("required_base") != B_NONE
                    else r.get("residue"))
            if r.get("residue") != want:
                problems.append("row %s residue disagrees with the base that resolved it"
                                % r.get("face"))
            owners = set(r.get("producers_of_the_pointing_face") or [])
            outside = [x for x in (r.get("sources_naming_the_exact_string") or [])
                       if x not in owners]
            if sorted(r.get("sources_outside_a_producer_naming_the_exact_string") or []) != sorted(
                    outside):
                problems.append("row %s outside-reader list does not re-derive" % r.get("face"))
        else:
            if r.get("residue"):
                problems.append("row %s carries a residue but its value is not a path"
                                % r.get("face"))
            if r.get("sources_naming_the_exact_string"):
                problems.append("row %s carries a reader join but its value is not a path"
                                % r.get("face"))
            if r.get("form") == F_STEM and not r.get("stem_targets"):
                problems.append("row %s is a stem but names no face on disk" % r.get("face"))
            if r.get("form") in (F_LEAF, F_LABEL) and r.get("stem_targets"):
                problems.append("row %s names a face on disk but was published as unresolved"
                                % r.get("face"))
    if face.get("verdict") != verdict_for(s):
        problems.append("verdict does not re-derive from the summary")
    return problems


def verify():
    problems = []
    live = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    if live["summary"] != on_disk.get("summary"):
        diff = sorted(k for k in live["summary"]
                      if live["summary"][k] != on_disk["summary"].get(k))
        problems.append("summary is stale against the live tree: %s" % ", ".join(diff))
    if live.get("verdict") != on_disk.get("verdict"):
        problems.append("verdict differs: live %r disk %r"
                        % (live.get("verdict"), on_disk.get("verdict")))
    problems.extend(tally_problems(on_disk))
    return problems


def check():
    return tally_problems(_load(os.path.join(OUTDIR, FACE_NAME)))


# ----------------------------------------------------------------------------- selftest


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # --- forms and spellings
    leg("a .json suffix makes a path", form_of("results/x/A-2026-11-06.json") == F_PATH)
    leg("a separator without .json is still a path-like string",
        form_of("results/post_review.jsonl") == F_PATH_NO_JSON)
    leg("a bare token is unresolved until a face index is asked",
        form_of("cycle_position_census") == F_TOKEN)
    leg("free text with spaces is a label",
        form_of("descriptive sweep; selects no arm") == F_LABEL)
    leg("a sentence that merely contains a slash is not a path (r1487-style draft bug)",
        form_of("EXPLORATION/NEIGHBORHOOD deep-scan (no judgment)") == F_LABEL)
    leg("a label with punctuation is not a token",
        form_of("judged (leg-4: A158-TSGATE-P1)") == F_LABEL)
    leg("backslashes are the backslash spelling",
        spelling_of("results\\x\\A.json") == S_BACKSLASH)
    leg("forward slashes are the forward spelling",
        spelling_of("results/x/A.json") == S_FORWARD)
    leg("a bare filename has no directory", spelling_of("A.json") == S_BARE)
    leg("a windows drive path is absolute", spelling_of("C:\\x\\A.json") == S_ABS)
    leg("both separators at once are mixed", spelling_of("results\\x/A.json") == S_MIXED)
    leg("normalising folds backslashes only", normalise("a\\b/c") == "a/b/c")

    # --- resolution (a temp tree, so the leg cannot depend on the repo)
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e465selftest_")
    os.makedirs(os.path.join(tmp, "results", "fam"), exist_ok=True)
    with io.open(os.path.join(tmp, "results", "fam", "TARGET-2026-11-06.json"), "w",
                 encoding="utf-8") as fh:
        fh.write("{}")
    rel_face = "results/fam/POINTING-2026-11-06.json"
    with io.open(os.path.join(tmp, rel_face), "w", encoding="utf-8") as fh:
        fh.write("{}")
    bare = resolve_pointer("TARGET-2026-11-06.json", rel_face, root=tmp)
    leg("a bare filename resolves only from the pointing face's own directory",
        bare["required_base"] == B_OWN)
    rooted = resolve_pointer("results/fam/TARGET-2026-11-06.json", rel_face, root=tmp)
    leg("a repo-relative path resolves from the root", rooted["required_base"] == B_ROOT)
    back = resolve_pointer("results\\fam\\TARGET-2026-11-06.json", rel_face, root=tmp)
    leg("a backslash path resolves after explicit normalisation",
        back["required_base"] == B_ROOT and back["spelling"] == S_BACKSLASH)
    gone = resolve_pointer("results/fam/NOPE.json", rel_face, root=tmp)
    leg("a path that is nowhere gets no base", gone["required_base"] == B_NONE)
    leg("residue of a resolving path is on disk",
        residue_of("TARGET-2026-11-06.json", rel_face, root=tmp) == R_ON_DISK)
    leg("residue of a non-path value is empty",
        residue_of("just a label here", rel_face, root=tmp) == "")

    # --- residue with an injected history probe, so the leg does not need a git checkout
    def _history_yes(_norm, root=None):
        return True

    def _history_no(_norm, root=None):
        return False

    leg("a missing path found in git history is published as history, not as never",
        residue_of("results/fam/GONE.json", rel_face, root=tmp,
                   history_probe=_history_yes) == R_HISTORY)
    leg("a missing path found nowhere is published as never",
        residue_of("results/fam/GONE.json", rel_face, root=tmp,
                   history_probe=_history_no) == R_NEVER)

    # --- stems
    idx = {"pointerjoin": ["results/state_tilt/POINTERJOIN-2026-11-06.json"]}
    leg("a stem resolves when a face on disk carries it",
        stem_resolves("pointerjoin", idx) == ["results/state_tilt/POINTERJOIN-2026-11-06.json"])
    leg("a stem nobody carries does not resolve", stem_resolves("nosuchface", idx) == [])
    leg("a value that is not a json name has no stem at all", e464.face_stem("income") == "")

    # --- readers
    tree = ast.parse('x = d.get("source_face")\ny = d["face_path"]\nz = d["face"]\n')
    sites = read_sites(tree, POINTER_KEYS)
    leg("all three pointer keys are read by literal name",
        sorted({k for k, _h in sites}) == sorted(POINTER_KEYS))
    leg("a subscript and a get are different read kinds",
        {h for _k, h in sites} == {"subscript", "get"})
    tree = ast.parse('x = d["card"]\ny = getattr(d, "face")')
    leg("an identity key and an attribute name are not pointer reads",
        read_sites(tree, POINTER_KEYS) == [])

    # --- following a pointer (reading the key is not following it)
    tree = ast.parse('p = d.get("source_face")\n'
                     'q = json.load(open(os.path.join(ROOT, p), encoding="utf-8"))\n')
    leg("a value read from the key and used as a path is followed",
        follows_pointer(tree, POINTER_KEYS)[0] == ["source_face"])
    tree = ast.parse('p = d.get("source_face")\nsha = p.get("sha256")\n')
    leg("a value read from the key and treated as a block is not followed",
        follows_pointer(tree, POINTER_KEYS)[0] == [])
    tree = ast.parse('open(os.path.join(ROOT, d["face"]))\n')
    leg("an inline key inside an open is followed",
        follows_pointer(tree, POINTER_KEYS)[0] == ["face"])
    tree = ast.parse('x = "results/compute_audit.json"\nopen(x)\n')
    leg("a literal that spells a face is not a pointer follow",
        follows_pointer(tree, POINTER_KEYS)[0] == [])
    tree = ast.parse('s = d["face"]\nlabel = "face: " + s\n')
    leg("a derived value used only as text is not followed",
        follows_pointer(tree, POINTER_KEYS)[0] == [])

    # --- gates
    empty_forms = {k: {f: 0 for f in FORMS} for k in POINTER_KEYS}
    good = {
        "verdict": V_UNJOINED,
        "summary": {
            "pointer_instances": 2,
            "faces_carrying_a_pointer_key": 2,
            "pointer_instances_by_key": {"source_face": 1, "face": 1, "face_path": 0},
            "value_form_by_key": {
                "source_face": dict(empty_forms["source_face"], **{F_PATH: 1}),
                "face": dict(empty_forms["face"], **{F_STEM: 1}),
                "face_path": dict(empty_forms["face_path"]),
            },
            "path_form_instances": 1,
            "path_form_instances_by_key": {"source_face": 1, "face": 0, "face_path": 0},
            "path_form_resolving_from_the_repo_root": 1,
            "path_form_resolving_only_from_the_pointing_faces_own_directory": 0,
            "path_form_resolving_as_an_absolute_path": 0,
            "path_form_that_do_not_resolve": 0,
            "residue_classes": {R_ON_DISK: 1, R_HISTORY: 0, R_NEVER: 0},
            "spelling_by_form": {S_BARE: 0, S_FORWARD: 1, S_BACKSLASH: 0, S_MIXED: 0, S_ABS: 0},
            "spellings_a_posix_reader_would_reject": 0,
            "stem_form_instances": 1,
            "token_instances_naming_no_face_on_disk": 0,
            "label_form_instances": 0,
            "faces_whose_face_key_is_a_path": 0,
            "faces_whose_face_key_is_not_a_path": 1,
            "target_paths_named_by_a_source_outside_a_producer": 0,
            "sources_outside_a_producer_that_name_a_target": [],
            "sources_naming_only_a_target_basename": 0,
            "sources_that_read_a_pointer_key_name": [],
            "sources_that_derive_a_value_from_a_pointer_key": {},
            "sources_that_turn_a_pointer_into_a_path": {},
            "sources_outside_a_producer_that_follow_a_pointer": [],
            "sources_outside_a_producer_that_follow_the_generic_face_key": [],
            "faces_whose_pointer_key_is_a_block_not_a_string": 0,
            "key_name_reads": {},
            "faces_with_no_writer_in_the_corpus": 0,
        },
        "rows": [
            {"face": "results/a/X.json", "key": "source_face",
             "value": "results/b/Y.json", "form": F_PATH, "spelling": S_FORWARD,
             "required_base": B_ROOT, "residue": R_ON_DISK,
             "resolves_from_repo_root": True,
             "resolves_from_the_pointing_faces_own_directory": False,
             "resolves_as_an_absolute_path": False,
             "sources_naming_the_exact_string": [],
             "producers_of_the_pointing_face": ["p0.py"],
             "sources_outside_a_producer_naming_the_exact_string": [],
             "sources_naming_only_the_targets_basename": [], "stem_targets": []},
            {"face": "results/a/Z.json", "key": "face", "value": "plainstem",
             "form": F_STEM, "spelling": S_BARE, "residue": "",
             "sources_naming_the_exact_string": [], "producers_of_the_pointing_face": [],
             "sources_outside_a_producer_naming_the_exact_string": [],
             "sources_naming_only_the_targets_basename": [],
             "stem_targets": ["results/a/plainstem_latest.json"]},
        ],
    }
    leg("gate accepts a consistent face", tally_problems(good) == [])
    good["summary"]["pointer_instances"] = 3
    leg("gate refuses an instance count that does not re-derive",
        any("pointer instances" in p for p in tally_problems(good)))
    good["summary"]["pointer_instances"] = 2
    good["summary"]["value_form_by_key"]["face"][F_STEM] = 0
    leg("gate refuses a form tally that does not re-derive",
        any("form" in p for p in tally_problems(good)))
    good["summary"]["value_form_by_key"]["face"][F_STEM] = 1
    good["summary"]["residue_classes"][R_ON_DISK] = 0
    leg("gate refuses a residue tally that does not re-derive",
        any("residue" in p for p in tally_problems(good)))
    good["summary"]["residue_classes"][R_ON_DISK] = 1
    good["rows"][1]["residue"] = R_NEVER
    leg("gate refuses a residue on a value that is not a path",
        any("not a path" in p for p in tally_problems(good)))
    good["rows"][1]["residue"] = ""
    good["rows"][1]["stem_targets"] = []
    leg("gate refuses a stem that names no face on disk",
        any("names no face" in p for p in tally_problems(good)))
    good["rows"][1]["stem_targets"] = ["results/a/plainstem_latest.json"]
    good["rows"][0]["producers_of_the_pointing_face"] = []
    good["rows"][0]["sources_naming_the_exact_string"] = ["r.py"]
    good["summary"]["target_paths_named_by_a_source_outside_a_producer"] = 0
    leg("gate refuses an outside-reader total that does not re-derive",
        any("outside-reader total" in p for p in tally_problems(good)))
    good["summary"]["target_paths_named_by_a_source_outside_a_producer"] = 1
    good["summary"]["sources_outside_a_producer_that_name_a_target"] = ["r.py"]
    good["summary"]["faces_with_no_writer_in_the_corpus"] = 0
    leg("gate refuses a writerless count that does not re-derive",
        any("writerless" in p for p in tally_problems(good)))
    good["summary"]["faces_with_no_writer_in_the_corpus"] = 1
    good["summary"]["sources_naming_only_a_target_basename"] = 1
    leg("gate refuses a basename-only reader count that does not re-derive",
        any("basename-only" in p for p in tally_problems(good)))
    good["summary"]["sources_naming_only_a_target_basename"] = 0
    good["summary"]["sources_that_turn_a_pointer_into_a_path"] = {"source_face": ["ghost.py"]}
    leg("gate refuses a follower that reads no pointer key",
        any("without reading the key" in p for p in tally_problems(good)))
    good["summary"]["sources_that_turn_a_pointer_into_a_path"] = {}
    good["verdict"] = V_JOINED
    leg("gate refuses a verdict that does not re-derive from the summary",
        any("verdict" in p for p in tally_problems(good)))
    good["summary"]["sources_outside_a_producer_that_follow_a_pointer"] = ["r.py"]
    good["summary"]["sources_that_read_a_pointer_key_name"] = ["r.py"]
    good["summary"]["sources_that_turn_a_pointer_into_a_path"] = {"source_face": ["r.py"]}
    good["verdict"] = V_JOINED
    leg("gate accepts a followed pointer as the joined verdict",
        not any("verdict" in p or "follow" in p for p in tally_problems(good)))

    # --- own-output skip (E180/E207 self-inclusion law)
    leg("own face is skipped by name", is_own_output("results/state_tilt/" + FACE_NAME))
    leg("a dated own output is skipped",
        is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    leg("the parent family's face is not own output", not is_own_output(
        "results/state_tilt/identitydialect_latest.json"))

    ok = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        print(("PASS " if cond else "FAIL ") + name)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ----------------------------------------------------------------------------- main


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build(write=True)
        s = face["summary"]
        print("verdict:", face["verdict"])
        print("instances:", s["pointer_instances"],
              "| faces:", s["faces_carrying_a_pointer_key"],
              "| by key:", s["pointer_instances_by_key"])
        print("forms by key:", s["value_form_by_key"])
        print("path-form:", s["path_form_instances"],
              "| bases:", {B_ROOT: s["path_form_resolving_from_the_repo_root"],
                           B_OWN: s["path_form_resolving_only_from_the_pointing_faces_own_directory"],
                           B_ABS: s["path_form_resolving_as_an_absolute_path"],
                           B_NONE: s["path_form_that_do_not_resolve"]})
        print("residue:", s["residue_classes"], "| spellings:", s["spelling_by_form"])
        print("face key as path:", s["faces_whose_face_key_is_a_path"],
              "| not a path:", s["faces_whose_face_key_is_not_a_path"],
              "| stem instances:", s["stem_form_instances"],
              "| tokens naming no face:", s["token_instances_naming_no_face_on_disk"],
              "| labels:", s["label_form_instances"])
        print("readers naming a target:", s["target_paths_named_by_a_source_outside_a_producer"],
              "| sources reading a key name:", len(s["sources_that_read_a_pointer_key_name"]),
              "| deriving a value:", s["sources_that_derive_a_value_from_a_pointer_key"],
              "| turning one into a path:", s["sources_that_turn_a_pointer_into_a_path"],
              "| outside followers (source_face/face_path):",
              len(s["sources_outside_a_producer_that_follow_a_pointer"]),
              "| outside followers of the generic face key:",
              len(s["sources_outside_a_producer_that_follow_the_generic_face_key"]),
              "| blocks:", s["faces_whose_pointer_key_is_a_block_not_a_string"])
        problems = tally_problems(face)
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "check":
        problems = check()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e466_pointer_join.py [run|verify|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))