"""E509 -- which of the unlisted date fields is a freshness witness and which is a constant.

E506 priced 68 faces whose payload carries no date under a witness field name and split them by
what the payload actually holds.  One of its classes -- 16 faces that carry a *structured* date
under a top-level (or shallow nested) name that is not in the witness vocabulary -- was a fact
about the field name, never about the value.  `inception` can be a frozen literal (2024-01-01) and
`report_date` can be the day the face was built; both look the same to a name check.

So this study asks the counterfactual question for each (face, field) pair in that class: does the
value move when the face is rebuilt over new data?  Two arms, both published per row:

* the **vintage arm** reads other vintages of the same face -- dated siblings and archival copies on
  disk, and the versions of the same path in git history -- and compares the field's value with the
  date anchor of the rest of the same payload (the newest date anywhere else in it, which is what
  the face knows about its own data);
* the **writing arm** reads every dict literal and subscript assignment in ``scripts/`` and
  ``Tools/`` that writes that field name and classifies the right-hand side (string literal / name /
  call / expression).  A literal is proof of a constant where only one vintage exists.

A field then gets one class: a constant written as a literal, a constant the face moved under, a
date that moves on its own clock (a run or period stamp), a freshness witness, or -- where no second
vintage exists -- an honest undecided.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.

The population is E506's own published face; it is never re-derived here.  Nothing in the tree is
written except the two face files this study owns.
"""
import ast
import io
import json
import os
import posixpath
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "unlisteddateorigin_latest.json"
DATED_PREFIX = "UNLISTEDDATEORIGIN"
DATE_STAMP = "2026-11-07"
CARD = ("E509-WHICH-OF-THE-17-UNLISTED-DATE-FIELDS-IS-A-FRESHNESS-WITNESS-AND-WHICH-IS-A-"
        "CONSTANT")
STUDY = "E509_unlisted_date_origin"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "NODATEWITNESS-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/NODATEWITNESS-2026-11-07.json rows whose witness_class is "
                     "a structured date under a name outside the witness list")
CARD_POPULATION_CLAIM = 17

C_TOP = "the_face_carries_a_top_level_date_field_whose_name_is_not_in_the_witness_list"
C_NESTED = ("the_face_carries_a_structured_date_under_a_nested_field_whose_name_is_not_in_the_"
            "witness_list")
UNLISTED_CLASSES = (C_TOP, C_NESTED)

# ------------------------------------------------------------------------ vocabulary
K_CONST_LITERAL = "a_constant_written_as_a_string_literal"
K_CONST_MOVED = "a_constant_the_face_was_rebuilt_under_and_it_did_not_move"
K_CONST_STILL = ("a_constant_but_no_vintage_shows_the_face_itself_moving_so_the_axis_is_"
                 "unexercised")
K_PARTIAL = "a_date_that_is_the_newest_one_in_its_face_in_some_vintages_but_not_in_others"
K_OWN_CLOCK = "a_date_that_moves_but_never_agrees_with_the_newest_date_elsewhere_in_the_face"
K_WITNESS = "a_freshness_witness_it_equals_the_newest_date_elsewhere_in_every_vintage"
K_ONE_VINTAGE = "no_second_vintage_so_no_counterfactual"
K_ABSENT = "the_field_is_not_readable_in_any_vintage"
CLASS_VOCAB = (K_CONST_LITERAL, K_CONST_MOVED, K_CONST_STILL, K_PARTIAL, K_OWN_CLOCK, K_WITNESS,
               K_ONE_VINTAGE, K_ABSENT)
DECIDED = (K_CONST_LITERAL, K_CONST_MOVED, K_CONST_STILL, K_PARTIAL, K_OWN_CLOCK, K_WITNESS)
NON_WITNESS = (K_CONST_LITERAL, K_CONST_MOVED, K_CONST_STILL, K_PARTIAL, K_OWN_CLOCK)

V_ALL_NONWITNESS = ("every_unlisted_date_that_has_a_counterfactual_is_a_constant_or_a_stamp_of_"
                    "its_own_clock_and_none_of_them_tracks_the_data")
V_ALL_WITNESS = "every_unlisted_date_that_has_a_counterfactual_tracks_the_data"
V_SPLIT = "the_unlisted_dates_split_between_ones_that_track_the_data_and_ones_that_do_not"
V_UNDECIDED = "no_pair_had_a_counterfactual_so_nothing_is_decided"
VERDICT_VOCAB = (V_ALL_NONWITNESS, V_ALL_WITNESS, V_SPLIT, V_UNDECIDED)

# writing-arm kinds
W_LITERAL = "a_string_literal_at_the_writing_site"
W_NAME = "a_name_that_is_not_a_literal_at_the_writing_site"
W_CALL = "a_call_result_at_the_writing_site"
W_EXPR = "another_expression_at_the_writing_site"
W_NONE = "no_writing_site_found_in_the_static_arm"
WRITE_VOCAB = (W_LITERAL, W_NAME, W_CALL, W_EXPR, W_NONE)

DATE_RE = re.compile(r"^((?:19|20)\d{2})-(\d{2})-(\d{2})$")
DATE_TOKEN = re.compile(r"(?:19|20)\d{6}|(?:19|20)\d{2}[-_]\d{2}[-_]\d{2}")
SKIP_DIRS = (".git", "node_modules", "__pycache__", ".codely-cli", "_quarantine_backup")
GIT_VINTAGES = 12
GIT_TIMEOUT = 25
CODE_DIRS = ("scripts", "Tools")


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _date_key(value):
    if not isinstance(value, str):
        return None
    m = DATE_RE.match(value.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _date_leaves(payload, prefix=""):
    out = []
    if isinstance(payload, dict):
        for key in sorted(payload, key=str):
            out.extend(_date_leaves(payload[key], "%s.%s" % (prefix, key) if prefix else str(key)))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            out.extend(_date_leaves(item, "%s.[%d]" % (prefix, i)))
    elif _date_key(payload):
        out.append((prefix, payload.strip()))
    return out


def _resolve(payload, field):
    """Read a field path like ``combat.traders.[0].guard.active_from``."""
    cur = payload
    for part in field.split("."):
        if not part:
            continue
        if part.startswith("[") and part.endswith("]"):
            try:
                idx = int(part[1:-1])
            except ValueError:
                return None
            if not isinstance(cur, list) or idx >= len(cur) or idx < -len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return cur


def _anchor(payload, field):
    """Newest date anywhere in the payload except the field under test."""
    best = None
    for path, value in _date_leaves(payload):
        if path == field:
            continue
        key = _date_key(value)
        if key and (best is None or key > best[0]):
            best = (key, value, path)
    return best


# ------------------------------------------------------------------ vintage discovery
def _norm(rel):
    return rel.replace("\\", "/").replace("__", "/")


def _stem_key(rel):
    norm = _norm(rel)
    name = posixpath.basename(norm)
    stem = name[:-5] if name.lower().endswith(".json") else name
    stem = DATE_TOKEN.sub("", stem)
    stem = re.sub(r"(?i)[-_]?latest$", "", stem)
    stem = re.sub(r"(?i)[-_]latest[-_]?", "", stem)
    stem = stem.strip("-_ ")
    letters = re.match(r"[A-Za-z]+", stem)
    return letters.group(0).lower() if letters else ""


def _dir_key(rel):
    norm = _norm(rel)
    directory = posixpath.dirname(norm)
    parts = [p for p in directory.split("/") if p]
    return "/".join(parts[-2:])


def _walk_json(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(".json"):
                full = os.path.join(dirpath, name)
                found.append(os.path.relpath(full, root).replace("\\", "/"))
    return sorted(found)


def _vintage_index(root):
    index = {}
    for rel in _walk_json(root):
        index.setdefault((_dir_key(rel), _stem_key(rel)), []).append(rel)
    return index


def _git(root, args):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        return subprocess.run(["git", "-C", root] + args, capture_output=True, timeout=GIT_TIMEOUT,
                              env=env)
    except (subprocess.TimeoutExpired, OSError):
        return None


def _git_available(root):
    got = _git(root, ["rev-parse", "--git-dir"])
    return bool(got is not None and got.returncode == 0)


def _git_vintages(root, rel):
    """Committed versions of the same path, newest first.  A lazy-fetch clone can stall one of
    these; a timeout is reported as unread rather than retried."""
    out = []
    got = _git(root, ["log", "--format=%H", "-n", str(GIT_VINTAGES), "--", rel])
    if got is None or got.returncode != 0:
        return out, "git_log_unavailable"
    shas = [line.strip() for line in got.stdout.decode("utf-8", "replace").splitlines()
            if line.strip()]
    stalled = 0
    for sha in shas:
        blob = _git(root, ["show", "%s:%s" % (sha, rel)])
        if blob is None:
            stalled += 1
            continue
        if blob.returncode != 0:
            continue
        try:
            out.append((sha[:10], json.loads(blob.stdout.decode("utf-8", "replace"))))
        except ValueError:
            continue
    return out, ("git_vintages_stalled=%d" % stalled if stalled else "ok")


def _disk_vintages(root, index, rel):
    key = (_dir_key(rel), _stem_key(rel))
    peers = [p for p in index.get(key, []) if _norm(p) != _norm(rel)]
    out = []
    for peer in sorted(peers):
        try:
            out.append((peer, _load(os.path.join(root, peer))))
        except (ValueError, OSError):
            continue
    return out


# ------------------------------------------------------------------- writing arm
def _code_files(root):
    files = []
    for base in CODE_DIRS:
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if name.endswith(".py") and not name.startswith("e509"):
                    files.append(os.path.join(dirpath, name))
    return sorted(files)


def _write_kind(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return W_LITERAL
    if isinstance(node, ast.Name):
        return W_NAME
    if isinstance(node, ast.Call):
        return W_CALL
    return W_EXPR


def _writing_sites(root, field, hints):
    """Every dict literal key / subscript assignment in the code dirs that writes `field`.

    A site only counts if its file also names the face it belongs to: the tree holds thousands of
    one-off round scripts, and a literal `"asof": "2026-10-29"` inside a study that computes a
    different thing says nothing about the asof of the face under test.  Rejected sites are
    counted, not silently dropped.
    """
    sites, rejected = [], 0
    for path in _code_files(root):
        try:
            source = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if field not in source:
            continue
        low = source.lower()
        in_scope = any(hint and hint.lower() in low for hint in hints)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == field:
                        kind = _write_kind(value)
                        found.append({"file": rel, "line": int(getattr(node, "lineno", 0)),
                                      "kind": kind,
                                      "sample": (value.value if kind == W_LITERAL else None)})
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if (isinstance(target, ast.Subscript)
                            and isinstance(target.slice, ast.Constant)
                            and target.slice.value == field):
                        kind = _write_kind(node.value)
                        found.append({"file": rel, "line": int(getattr(node, "lineno", 0)),
                                      "kind": kind,
                                      "sample": (node.value.value if kind == W_LITERAL else None)})
            elif isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "attr", None) or getattr(func, "id", None)
                if name in ("setdefault", "update") and node.args:
                    first = node.args[0]
                    if isinstance(first, ast.Constant) and first.value == field and len(node.args) > 1:
                        kind = _write_kind(node.args[1])
                        found.append({"file": rel, "line": int(getattr(node, "lineno", 0)),
                                      "kind": kind,
                                      "sample": (node.args[1].value if kind == W_LITERAL else None)})
        if in_scope:
            sites.extend(found)
        else:
            rejected += len(found)
    return sites, rejected


def _writing_class(sites):
    if not sites:
        return W_NONE
    kinds = {s["kind"] for s in sites}
    if kinds == {W_LITERAL}:
        return W_LITERAL
    if W_LITERAL in kinds:
        return W_LITERAL
    if kinds == {W_NAME}:
        return W_NAME
    if kinds == {W_CALL}:
        return W_CALL
    return W_EXPR


# ---------------------------------------------------------------------- population
def population(upstream):
    rows = []
    for row in (upstream.get("rows") or []):
        cls = row.get("witness_class")
        if cls not in UNLISTED_CLASSES:
            continue
        structured = [h for h in (row.get("hits") or []) if h.get("kind") == "structured"]
        if not structured:
            continue
        if cls == C_TOP:
            candidates = [h for h in structured if "." not in h.get("field", "")]
        else:
            candidates = [h for h in structured
                          if h.get("field", "").startswith("[")
                          or ("." in h.get("field", "") and not h.get("field", "").startswith("["))]
        for hit in candidates:
            rows.append({"face": row.get("face"), "field": hit.get("field"),
                         "sample": hit.get("sample"), "witness_class": cls,
                         "face_bytes": row.get("bytes"),
                         "face_mtime_age_days": row.get("mtime_age_days")})
    return rows


# ------------------------------------------------------------------------- analysis
def _days_between(later, earlier):
    import datetime
    a, b = _date_key(later), _date_key(earlier)
    if not a or not b:
        return None
    return (datetime.date(*a) - datetime.date(*b)).days


def _classify(pair, vintages, writing):
    """The vintage arm outranks the writing arm wherever it can speak.

    A field that a committed vintage shows moving is not a constant, whatever a one-off script
    somewhere writes about that name; the writing arm is what decides a face with no second
    reading, which is exactly the case in which no counterfactual exists.
    """
    present = [v for v in vintages if v["value"] is not None]
    values = [v["value"] for v in present]
    if not values:
        return K_ABSENT, present
    if len(values) >= 2 and len(set(values)) > 1:
        deltas = [_days_between(v["anchor"], v["value"]) for v in present]
        if all(d == 0 for d in deltas):
            return K_WITNESS, present
        if any(d == 0 for d in deltas):
            return K_PARTIAL, present
        return K_OWN_CLOCK, present
    if len(values) >= 2:
        anchors = {v["anchor"] for v in present if v["anchor"]}
        return (K_CONST_MOVED if len(anchors) > 1 else K_CONST_STILL), present
    if writing["class"] == W_LITERAL:
        return K_CONST_LITERAL, present
    return K_ONE_VINTAGE, present


def analyse(root=None, upstream=None):
    root = root or ROOT
    if upstream is None:
        upstream = _load(os.path.join(root, UPSTREAM_FACE))
    pairs = population(upstream)
    index = _vintage_index(root)
    git_ok = _git_available(root)
    rows = []
    write_cache = {}
    for pair in pairs:
        rel = pair["face"]
        field = pair["field"]
        field_path = field.lstrip(".[]") if not field.startswith("[") else field
        vintages = []
        sources = []
        try:
            current = _load(os.path.join(root, rel))
        except (ValueError, OSError):
            current = None
        if current is not None:
            vintages.append({"source": "disk:current", "kind": "current",
                             "value": _resolve(current, field_path),
                             "anchor": (_anchor(current, field_path) or [None, None, None])[1]})
            sources.append("disk:current")
        for peer, payload in _disk_vintages(root, index, rel):
            vintages.append({"source": "disk:%s" % peer, "kind": "sibling",
                             "value": _resolve(payload, field_path),
                             "anchor": (_anchor(payload, field_path) or [None, None, None])[1]})
            sources.append("disk:%s" % peer)
        git_note = "git_arm_off"
        if git_ok:
            got, git_note = _git_vintages(root, rel)
            for sha, payload in got:
                vintages.append({"source": "git:%s" % sha, "kind": "commit",
                                 "value": _resolve(payload, field_path),
                                 "anchor": (_anchor(payload, field_path) or [None, None, None])[1]})
                sources.append("git:%s" % sha)
        name = field_path.split(".")[-1].strip("[]")
        hints = {posixpath.dirname(_norm(rel)).split("/")[-1], _stem_key(rel)}
        key = (name, tuple(sorted(h for h in hints if h)))
        if key not in write_cache:
            found, rejected = _writing_sites(root, name, hints)
            write_cache[key] = ({"class": _writing_class(found), "sites": found[:8],
                                 "count": len(found)}, rejected)
        writing, rejected = write_cache[key]
        cls, present = _classify(pair, vintages, writing)
        rows.append({
            "face": rel,
            "field": field,
            "field_name": name,
            "witness_class": pair["witness_class"],
            "sample": pair["sample"],
            "face_bytes": pair["face_bytes"],
            "face_mtime_age_days": pair["face_mtime_age_days"],
            "class": cls,
            "vintages_read": len(vintages),
            "vintages_with_the_field": len(present),
            "vintage_sources": sources,
            "vintage_values": [{"source": v["source"], "value": v["value"],
                                "anchor": v["anchor"],
                                "days_behind_the_newest_date": _days_between(v["anchor"],
                                                                            v["value"])
                                if (v["anchor"] and v["value"]) else None}
                               for v in vintages],
            "writing_site_class": writing["class"],
            "writing_sites": writing["sites"],
            "writing_site_count": writing["count"],
            "writing_sites_rejected_for_not_naming_the_face": rejected,
            "git_note": git_note,
        })
    return {"pairs": rows}


def _count(rows, key, vocab):
    out = {name: 0 for name in vocab}
    for row in rows:
        value = row.get(key)
        if value in out:
            out[value] += 1
    return out


def _summary(rows, upstream):
    by_class = _count(rows, "class", CLASS_VOCAB)
    by_writing = _count(rows, "writing_site_class", WRITE_VOCAB)
    faces = sorted({r["face"] for r in rows})
    decided = [r for r in rows if r["class"] in DECIDED]
    non_witness = [r for r in rows if r["class"] in NON_WITNESS]
    witness = [r for r in rows if r["class"] == K_WITNESS]
    constant_faces = sorted({r["face"] for r in rows
                             if r["class"] in (K_CONST_LITERAL, K_CONST_MOVED, K_CONST_STILL)})
    certified = {r["face"] for r in rows if r["class"] in (K_WITNESS, K_PARTIAL)}
    only_constant = [f for f in constant_faces if f not in certified]
    first_of = {}
    for row in rows:
        first_of.setdefault(row["face"], row)
    multi = [r for r in rows if r["vintages_read"] > 1]
    return {
        "faces": len(faces),
        "fields": len({r["field_name"] for r in rows}),
        "pairs": len(rows),
        "pairs_with_a_second_vintage": len(multi),
        "pairs_decided": len(decided),
        "pairs_undecided": len(rows) - len(decided),
        "pairs_with_a_witness": len(witness),
        "pairs_that_are_not_a_witness": len(non_witness),
        "by_class": by_class,
        "by_writing_site_class": by_writing,
        "faces_carrying_a_constant_date": len(constant_faces),
        "faces_whose_unlisted_dates_never_track_the_data": len(only_constant),
        "faces_with_a_witness_or_a_partial_witness": len(certified),
        "bytes_of_faces_carrying_a_constant_date": sum(
            int(first_of[f]["face_bytes"] or 0) for f in constant_faces),
        "bytes_of_faces_whose_unlisted_dates_never_track_the_data": sum(
            int(first_of[f]["face_bytes"] or 0) for f in only_constant),
        "bytes_total": sum(int(first_of[f]["face_bytes"] or 0) for f in faces),
        "vintages_read": sum(r["vintages_read"] for r in rows),
        "vintages_from_git": sum(1 for r in rows for s in r["vintage_sources"]
                                 if str(s).startswith("git:")),
        "vintages_from_disk_siblings": sum(1 for r in rows for s in r["vintage_sources"]
                                           if str(s).startswith("disk:") and not
                                           str(s).endswith("current")),
        "card_population_claim": CARD_POPULATION_CLAIM,
        "population_re_derived": len(rows),
        "population_delta_vs_card": len(rows) - CARD_POPULATION_CLAIM,
        "upstream_faces_in_this_class": len({r["face"] for r in (upstream.get("rows") or [])
                                             if r.get("witness_class") in UNLISTED_CLASSES}),
        "evidence_cutoff": DATE_STAMP,
    }


def _verdict(summary):
    decided = summary["pairs_decided"]
    if not decided:
        return V_UNDECIDED
    if summary["pairs_with_a_witness"] == 0:
        return V_ALL_NONWITNESS
    if summary["pairs_that_are_not_a_witness"] == 0:
        return V_ALL_WITNESS
    return V_SPLIT


def _answers(summary):
    return {
        "how_many_pairs_have_a_counterfactual": summary["pairs_with_a_second_vintage"],
        "how_many_pairs_are_decided": summary["pairs_decided"],
        "how_many_unlisted_dates_track_the_data": summary["pairs_with_a_witness"],
        "how_many_are_constant_or_own_clock": summary["pairs_that_are_not_a_witness"],
        "how_many_faces_do_their_unlisted_dates_never_certify":
            summary["faces_whose_unlisted_dates_never_track_the_data"],
        "how_many_bytes_do_those_faces_hold":
            summary["bytes_of_faces_whose_unlisted_dates_never_track_the_data"],
        "how_many_pairs_does_the_card_name_and_how_many_are_here":
            [summary["card_population_claim"], summary["population_re_derived"]],
    }


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    if upstream is None:
        upstream = _load(os.path.join(root, UPSTREAM_FACE))
    got = analyse(root, upstream=upstream)
    rows = got["pairs"]
    summary = _summary(rows, upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For every face E506 classed as carrying a structured date under a name outside "
                  "the witness list: does that field move when the face is rebuilt, and is it a "
                  "freshness witness at all?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "class_vocab": list(CLASS_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "writing_site_vocab": list(WRITE_VOCAB),
        "method_limits": [
            "the population is E506's published face; a pair appears here because that face "
            "classed the name as outside the witness vocabulary, not because this study re-read "
            "E506's rows",
            "a vintage is only evidence if the field is readable in it; a commit whose blob is not "
            "local to this promisor clone is counted as unread, never as unchanged",
            "the writing arm reads dict literals and subscript assignments in scripts/ and Tools/ "
            "only; a face written by a YAML/JSON template, by a pandas to_json, or by code outside "
            "those two directories shows no writing site",
            "a literal writing site is treated as proof of a constant even where vintages exist: "
            "one literal in the producer outweighs a value that happened to be equal in two "
            "siblings",
            "the date anchor is the newest date anywhere else in the same payload; a face that "
            "knows its data only under a non-date-shaped string (a bar number, an epoch int) has no "
            "anchor and its field is classed undecided rather than guessed",
            "archival copies under results/_quarantine/ and results/_r*_rollback_side/ are read as "
            "vintages of the live face and are published as such beside the live one",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


# ------------------------------------------------------------------------- gate
def surface_problems(face, upstream=None):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if upstream is None:
        upstream = _load(os.path.join(ROOT, UPSTREAM_FACE))
    if summary.get("pairs") != len(rows):
        problems.append("pairs=%r is not the row count %d" % (summary.get("pairs"), len(rows)))
    if summary.get("faces") != len({r.get("face") for r in rows}):
        problems.append("the face count does not re-derive")
    if summary.get("fields") != len({r.get("field_name") for r in rows}):
        problems.append("the field count does not re-derive")
    if summary.get("by_class") != _count(rows, "class", CLASS_VOCAB):
        problems.append("by_class does not re-derive from the rows")
    if summary.get("by_writing_site_class") != _count(rows, "writing_site_class", WRITE_VOCAB):
        problems.append("by_writing_site_class does not re-derive from the rows")
    if summary.get("pairs_decided") != len([r for r in rows if r.get("class") in DECIDED]):
        problems.append("the decided count does not re-derive")
    if summary.get("pairs_with_a_witness") != len([r for r in rows if r.get("class") == K_WITNESS]):
        problems.append("the witness count does not re-derive")
    if summary.get("pairs_that_are_not_a_witness") != len(
            [r for r in rows if r.get("class") in NON_WITNESS]):
        problems.append("the non-witness count does not re-derive")
    if summary.get("pairs_with_a_second_vintage") != len(
            [r for r in rows if r.get("vintages_read", 0) > 1]):
        problems.append("the second-vintage count does not re-derive")
    if summary.get("vintages_read") != sum(r.get("vintages_read", 0) for r in rows):
        problems.append("the vintage total does not re-derive")
    constant_faces = {r.get("face") for r in rows
                      if r.get("class") in (K_CONST_LITERAL, K_CONST_MOVED, K_CONST_STILL)}
    certified = {r.get("face") for r in rows if r.get("class") in (K_WITNESS, K_PARTIAL)}
    if summary.get("faces_carrying_a_constant_date") != len(constant_faces):
        problems.append("the constant-face count does not re-derive")
    if summary.get("faces_with_a_witness_or_a_partial_witness") != len(certified):
        problems.append("the certified-face count does not re-derive")
    if summary.get("faces_whose_unlisted_dates_never_track_the_data") != len(
            constant_faces - certified):
        problems.append("the never-certified face count does not re-derive")
    if face.get("verdict") != _verdict(summary):
        problems.append("the verdict is not the one the summary implies")
    if face.get("answers") != _answers(summary):
        problems.append("the answers do not re-derive from the summary")
    if summary.get("upstream_faces_in_this_class") != len(
            {r.get("face") for r in (upstream.get("rows") or [])
             if r.get("witness_class") in UNLISTED_CLASSES}):
        problems.append("the upstream face count does not re-derive")
    if summary.get("evidence_cutoff") != face.get("evidence_cutoff"):
        problems.append("the summary cutoff is not the face cutoff")
    published = {(p["face"], p["field"]) for p in population(upstream)}
    for row in rows:
        pair = (row.get("face"), row.get("field"))
        if pair not in published:
            problems.append("row %r is not in E506's population" % (pair,))
        cls = row.get("class")
        if cls not in CLASS_VOCAB:
            problems.append("row %r carries a class outside the vocabulary" % (pair,))
        if row.get("writing_site_class") not in WRITE_VOCAB:
            problems.append("row %r carries a writing-site class outside the vocabulary" % (pair,))
        values = [v.get("value") for v in (row.get("vintage_values") or [])]
        if len(values) != row.get("vintages_read"):
            problems.append("row %r publishes %d vintage values for %r vintages"
                            % (pair, len(values), row.get("vintages_read")))
        present = [v for v in values if v is not None]
        if row.get("vintages_with_the_field") != len(present):
            problems.append("row %r's readable-vintage count does not re-derive" % (pair,))
        if cls == K_CONST_LITERAL:
            if row.get("writing_site_class") != W_LITERAL:
                problems.append("row %r claims a literal constant with no literal writing site"
                                % (pair,))
            if len(present) >= 2:
                problems.append("row %r calls a literal what two vintages show moving" % (pair,))
        if cls in (K_CONST_MOVED, K_CONST_STILL):
            if len(present) < 2 or len(set(present)) != 1:
                problems.append("row %r claims a constant without two equal readings" % (pair,))
            anchors = [v.get("anchor") for v in (row.get("vintage_values") or [])
                       if v.get("value") is not None]
            spread = len({a for a in anchors if a is not None})
            if cls == K_CONST_MOVED and spread < 2:
                problems.append("row %r claims the face moved but publishes one anchor" % (pair,))
            if cls == K_CONST_STILL and spread > 1:
                problems.append("row %r claims the face did not move but its anchors differ"
                                % (pair,))
        if cls in (K_WITNESS, K_PARTIAL, K_OWN_CLOCK):
            if len(present) < 2:
                problems.append("row %r claims a moving field on fewer than two readings"
                                % (pair,))
            if len(set(present)) < 2:
                problems.append("row %r calls a field moving what never moved" % (pair,))
            deltas = [v.get("days_behind_the_newest_date")
                      for v in (row.get("vintage_values") or []) if v.get("value") is not None]
            if any(d is None for d in deltas):
                problems.append("row %r publishes a reading with no delta against its anchor"
                                % (pair,))
            elif cls == K_WITNESS and any(d != 0 for d in deltas):
                problems.append("row %r claims a witness its own deltas contradict" % (pair,))
            elif cls == K_PARTIAL and not (any(d == 0 for d in deltas)
                                           and any(d != 0 for d in deltas)):
                problems.append("row %r claims a partial witness its deltas contradict" % (pair,))
            elif cls == K_OWN_CLOCK and any(d == 0 for d in deltas):
                problems.append("row %r claims its own clock but a reading ties the anchor"
                                % (pair,))
        if cls == K_ABSENT and present:
            problems.append("row %r is classed absent but has readings" % (pair,))
        if row.get("vintage_sources") is None or len(row.get("vintage_sources") or []) != \
                row.get("vintages_read"):
            problems.append("row %r does not publish one source per vintage" % (pair,))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = surface_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = surface_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# -------------------------------------------------------------------- selftest
FIXTURE_FILES = {
    "results/fx_a/asofbook_latest.json":
        '{"book_asof": "2024-06-01", "last_bar": "2026-03-05"}',
    "results/fx_a/ASOFBOOK-2026-01-05.json":
        '{"book_asof": "2024-06-01", "last_bar": "2026-01-05"}',
    "results/fx_a/ASOFBOOK-2026-02-05.json":
        '{"book_asof": "2024-06-01", "last_bar": "2026-02-05"}',
    "results/fx_b/witness_latest.json":
        '{"report_date": "2026-03-05", "last_bar": "2026-03-05"}',
    "results/fx_b/WITNESS-2026-01-05.json":
        '{"report_date": "2026-01-05", "last_bar": "2026-01-05"}',
    "results/fx_b/WITNESS-2026-02-05.json":
        '{"report_date": "2026-02-05", "last_bar": "2026-02-05"}',
    "results/fx_c/pinned_latest.json":
        '{"cutoff_pin": "2026-10-09", "panel_gate": {"cutoff": "2026-10-09"}}',
    "results/fx_d/single_latest.json":
        '{"generated_for_bar": "2026-10-28", "panel": {"first_bar": "2024-01-02"}}',
    "results/fx_e/ownclock_latest.json":
        '{"book": {"inception": "2026-02-01"}, "last_bar": "2026-03-05"}',
    "results/fx_e/OWNCLOCK-2026-01-05.json":
        '{"book": {"inception": "2026-01-01"}, "last_bar": "2026-01-05"}',
    "scripts/fx_producer.py":
        'def build_pinned(bar):\n'
        '    face = {"cutoff_pin": "2026-10-09"}\n'
        '    face["book_asof"] = bar["last_bar"]\n'
        '    return face\n',
    "results/fx_f/mixed_latest.json":
        '{"mixed_date": "2026-01-05", "last_bar": "2026-01-05"}',
    "results/fx_f/MIXED-2026-02-05.json":
        '{"mixed_date": "2026-01-20", "last_bar": "2026-02-05"}',
}
FIXTURE_ROWS = [
    ("results/fx_a/asofbook_latest.json", "book_asof", C_TOP, 120),
    ("results/fx_b/witness_latest.json", "report_date", C_TOP, 240),
    ("results/fx_c/pinned_latest.json", "cutoff_pin", C_TOP, 60),
    ("results/fx_d/single_latest.json", "generated_for_bar", C_TOP, 80),
    ("results/fx_e/ownclock_latest.json", "book.inception", C_NESTED, 90),
    ("results/fx_f/mixed_latest.json", "mixed_date", C_TOP, 50),
]


def _fixture_upstream():
    rows = []
    for face, field, cls, size in FIXTURE_ROWS:
        rows.append({"face": face, "witness_class": cls, "bytes": size, "mtime_age_days": 3,
                     "hits": [{"field": field, "kind": "structured", "sample": "2026-01-01"}]})
    return {"rows": rows}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e509_selftest_")
    try:
        for rel, body in FIXTURE_FILES.items():
            path = os.path.join(tmp, rel.replace("/", os.sep))
            if not os.path.isdir(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
        upstream = _fixture_upstream()
        face = build(root=tmp, write=False, upstream=upstream)
        by = {row["field_name"]: row for row in face["rows"]}

        ok("a field that never moves while the face is rebuilt twice is a constant",
           by["book_asof"]["class"] == K_CONST_MOVED, by["book_asof"]["class"])
        ok("a field that equals the newest date elsewhere in every vintage is a witness",
           by["report_date"]["class"] == K_WITNESS, by["report_date"]["class"])
        ok("a single-vintage field whose own producer writes a literal is a literal constant",
           by["cutoff_pin"]["class"] == K_CONST_LITERAL, by["cutoff_pin"]["class"])
        ok("a single-vintage field with no literal is undecided, not guessed",
           by["generated_for_bar"]["class"] == K_ONE_VINTAGE, by["generated_for_bar"]["class"])
        ok("a field that moves but never matches the anchor is its own clock",
           by["inception"]["class"] == K_OWN_CLOCK, by["inception"]["class"])
        ok("a field that ties the anchor in one vintage and not in the other is partial",
           by["mixed_date"]["class"] == K_PARTIAL, by["mixed_date"]["class"])
        ok("a literal written by a script that never names the face is not attributed to it",
           by["generated_for_bar"]["writing_site_class"] == W_NONE,
           by["generated_for_bar"]["writing_site_class"])
        ok("sibling vintages are discovered on disk",
           by["report_date"]["vintages_with_the_field"] == 3,
           by["report_date"]["vintages_with_the_field"])
        ok("the fixture verdict is the split one",
           face["verdict"] == V_SPLIT, face["verdict"])
        ok("the gate passes on the built fixture",
           surface_problems(face, upstream) == [], surface_problems(face, upstream))

        doctored = json.loads(json.dumps(face))
        next(r for r in doctored["rows"] if r["field_name"] == "report_date")["class"] = K_ONE_VINTAGE
        ok("gate refuses a class its own readings contradict",
           surface_problems(doctored, upstream) != [])

        doctored2 = json.loads(json.dumps(face))
        next(r for r in doctored2["rows"] if r["field_name"] == "cutoff_pin")["class"] = K_WITNESS
        ok("gate refuses a witness with one reading", surface_problems(doctored2, upstream) != [])

        doctored9 = json.loads(json.dumps(face))
        next(r for r in doctored9["rows"] if r["field_name"] == "report_date")["class"] = K_PARTIAL
        ok("gate refuses a partial witness whose deltas are all zero",
           surface_problems(doctored9, upstream) != [])

        doctored10 = json.loads(json.dumps(face))
        next(r for r in doctored10["rows"] if r["field_name"] == "book_asof")["class"] = \
            K_CONST_LITERAL
        ok("gate refuses a literal constant whose own vintages move",
           surface_problems(doctored10, upstream) != [])

        doctored3 = json.loads(json.dumps(face))
        doctored3["summary"]["pairs_with_a_witness"] += 1
        ok("gate refuses a hand-written witness count",
           surface_problems(doctored3, upstream) != [])

        doctored4 = json.loads(json.dumps(face))
        doctored4["verdict"] = V_ALL_WITNESS
        ok("gate refuses a hand-written verdict", surface_problems(doctored4, upstream) != [])

        doctored5 = json.loads(json.dumps(face))
        doctored5["rows"][0]["class"] = "guessed"
        ok("gate refuses a class outside the vocabulary",
           surface_problems(doctored5, upstream) != [])

        doctored6 = json.loads(json.dumps(face))
        doctored6["rows"].append(dict(doctored6["rows"][0], face="results/fx_z/none_latest.json"))
        ok("gate refuses a pair E506 never published",
           surface_problems(doctored6, upstream) != [])

        doctored7 = json.loads(json.dumps(face))
        next(r for r in doctored7["rows"] if r["field_name"] == "cutoff_pin")["writing_site_class"] \
            = W_NONE
        ok("gate refuses a literal constant with no literal site",
           surface_problems(doctored7, upstream) != [])

        doctored8 = json.loads(json.dumps(face))
        doctored8["answers"]["how_many_unlisted_dates_track_the_data"] += 1
        ok("gate refuses a hand-written answer", surface_problems(doctored8, upstream) != [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())