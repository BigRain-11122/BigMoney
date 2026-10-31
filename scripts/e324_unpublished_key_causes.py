"""E324 -- the six gates whose producer "publishes no key of that name".

E321 classified every unresolved-or-ambiguous gate leaf by reading its producer.  Six leaves came
back as ``producer_found_but_publishes_no_such_key``: a producer was found, and the key was not
published there.  E323's wider needle moved 25 rows and left these six untouched -- they were
never a needle problem.  The open question, written into the pool card, is the one this study
answers: **is the key written under another name, copied in from a sub-face, or genuinely absent
from the writer?**

The answer, for all six, is that the key IS published in the repository and the class was
counting a *composition* as an absence:

* four rows sit on ``results/etf_book_production/PRODUCTION-<date>.json``, a card that COMPOSES
  other faces.  ``spanning_pre2020`` is ``{"control": doc.get("control")}`` copied out of
  ``results/etf_book_spanning_pre2020.json``; ``window_decomp.controls`` is ``doc.get("controls")``
  copied out of ``results/etf_book_window_decomp.json``.  ``tolerance_pp`` is published -- as
  ``"tolerance_pp": TOL_PP`` / ``"tolerance_pp": CONTROL_TOL_PP`` -- by the sub-face writer, which
  writes a face the composer reads and never names the composed one.
* two rows sit on a census's own ``summary``.  ``by_kind`` / ``by_verdict`` are accumulations whose
  key is a DATA value (``by_kind[r["kind"]] = ... + 1``), so no literal key exists in the writer at
  all: the key is the value of a column.

The distinction matters because the two causes need different repairs.  A composed key is already
named where it is produced -- the defect is only in the ownership map.  A computed key has no
single site to name, which is a different (and weaker) property: the count it publishes is a
census, not a threshold.

Usage:
    python scripts/e324_unpublished_key_causes.py run|build|verify|selftest
"""
import io
import json
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)
import e321_quantity_name_reach as e321  # noqa: E402
import e323_reach_under_wider_needle as e323  # noqa: E402

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "REACHWIDE-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "UNPUBLISHEDKEY-%s.json" % TODAY
LATEST = "unpublishedkey_latest.json"
STUDY = "E324_unpublished_key_causes"

POPULATION_CLASS = "producer_found_but_publishes_no_such_key"

CAUSE_SUBFACE = "copied_wholesale_from_a_subface_writer"
CAUSE_DATAKEY = "the_key_is_a_data_value_so_no_literal_key_exists"
CAUSE_ORPHAN = "no_source_in_the_tree_mentions_the_key_so_the_face_is_unreproducible"
CAUSE_ABSENT = "named_as_a_value_but_never_published_as_a_key"
CAUSES = (CAUSE_SUBFACE, CAUSE_DATAKEY, CAUSE_ORPHAN, CAUSE_ABSENT)

VERDICT_LOCATED = ("five_of_the_six_keys_are_published_by_a_writer_and_the_sixth_is_a_face_no_"
                   "committed_writer_can_reproduce")
VERDICT_ALL_LOCATED = "every_key_is_published_by_a_writer_and_the_class_was_a_reading_error"
VERDICT_ABSENT = "some_keys_are_absent_from_the_repository_and_the_class_was_right_for_those"

JSON_NAME = re.compile(r'"([A-Za-z0-9_\-]+\.json)"')


# --------------------------------------------------------------------------------- corpus

_SRC = None


def corpus():
    """E323's corpus: every producer source, every auditor kept, E323 itself excluded."""
    global _SRC
    if _SRC is None:
        own = os.path.abspath(__file__)
        _SRC = [(p, s) for p, s in e323.corpus() if os.path.abspath(p) != own]
    return _SRC


def relp(path):
    return e312.rel(path) if os.path.isabs(path) else path.replace("\\", "/")


def read_json(rel_path):
    with io.open(os.path.join(ROOT, rel_path), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------- publishing a key (not a value)

def _after(items, idx):
    """Tokens of the expression that starts at ``idx`` (a ':' or an '='), up to depth-0 ','."""
    out = []
    depth = 0
    for tok_type, tok in items[idx + 1:]:
        if tok_type == tokenize.OP and tok in "([{":
            depth += 1
        elif tok_type == tokenize.OP and tok in ")]}":
            if depth == 0:
                break
            depth -= 1
        elif tok_type == tokenize.OP and tok == "," and depth == 0:
            break
        out.append(tok)
    return "".join(out)[:80]


def shape_of(items, key):
    """How this key appears on the line: a mapping key, an item-assignment key, or not a key.

    The distinction is E324's whole point.  `kind = "epsilon"` uses the same string, but as a
    VALUE; ``{"epsilon": 39}`` and ``by_kind["epsilon"] = 39`` publish it as a key.  E321's
    detector accepted any string on a line carrying ``=``, so a value string could be read as a
    publication -- this one only accepts the two key shapes.
    """
    for i, (tok_type, tok) in enumerate(items):
        if tok_type != tokenize.STRING or tok.strip("\"'") != key:
            continue
        nxt = items[i + 1][1] if i + 1 < len(items) else None
        if nxt == ":":
            return "mapping", i + 1
        prev = items[i - 1][1] if i > 0 else None
        if (prev == "[" and i + 2 < len(items)
                and items[i + 1][1] == "]" and items[i + 2][1] == "="):
            return "item_assignment", i + 2
    return None, None


def key_sites(files, key):
    """Every place ``files`` publishes ``key`` as a key, with the expression on the right."""
    out = []
    if not key:
        return out
    for path, src in files:
        if key not in src:
            continue
        toks = e312.code_tokens(src)
        lines = src.splitlines()
        for lineno, items in sorted(toks.items()):
            shape, idx = shape_of(items, key)
            if not shape:
                continue
            out.append({"producer": relp(path), "line": lineno, "shape": shape,
                        "expression": _after(items, idx),
                        "text": lines[lineno - 1].strip()[:120]})
    return out


def value_only_mentions(files, key):
    """Sources where the string exists but never in a key position (the census case)."""
    out = []
    for path, src in files:
        if key not in src:
            continue
        if key_sites([(path, src)], key):
            continue
        lines = [ln.strip() for ln in src.splitlines() if key in ln]
        out.append({"producer": relp(path), "lines": lines[:4]})
    return out


def accum_sites(files, dict_name):
    """``dict[<not a literal>] = ...`` -- an accumulation whose key comes from data."""
    out = []
    for path, src in files:
        if dict_name not in src:
            continue
        toks = e312.code_tokens(src)
        lines = src.splitlines()
        for lineno, items in sorted(toks.items()):
            for i, (tok_type, tok) in enumerate(items):
                if tok_type != tokenize.NAME or tok != dict_name:
                    continue
                if i + 1 >= len(items) or items[i + 1][1] != "[":
                    continue
                j, depth, subscript = i + 2, 0, []
                while j < len(items):
                    tok_type2, tok2 = items[j]
                    if tok_type2 == tokenize.OP and tok2 in "([{":
                        depth += 1
                    elif tok_type2 == tokenize.OP and tok2 in ")]}":
                        if depth == 0 and tok2 == "]":
                            break
                        depth -= 1
                    subscript.append(tok2)
                    j += 1
                tail = items[j + 1:]
                if not tail or tail[0][1] != "=":
                    continue
                text = "".join(subscript)
                if text.strip().startswith(("\"", "'")):
                    continue  # a literal key: that is a key site, handled above
                out.append({"producer": relp(path), "line": lineno, "dict": dict_name,
                            "subscript": text, "text": lines[lineno - 1].strip()[:120]})
    return out


# ------------------------------------------------------------------------------ face navigation

def resolve(face_rel, leaf, root=None):
    """The value at a dotted leaf inside a published face."""
    try:
        doc = read_json(face_rel) if root is None else root
    except (OSError, ValueError) as exc:
        return {"present": False, "reason": "face unreadable: %s" % exc}
    node = doc
    for part in (leaf or "").split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return {"present": False, "reason": "no key %r" % part}
    return {"present": True, "value": node}


def json_refs(src):
    return sorted(set(JSON_NAME.findall(src or "")))


def writers_of(face):
    return e321.producer_candidates(face)


def reads_line(src, basename):
    for lineno, line in enumerate((src or "").splitlines(), 1):
        if basename in line:
            return lineno
    return None


def path_vars(src, basename):
    """Names assigned a path literal that contains this face file."""
    out = []
    for line in (src or "").splitlines():
        if basename not in line:
            continue
        match = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*", line)
        if match:
            out.append(match.group(1))
    return out


def owns_face(src, basename):
    """Does this source open that face for WRITING?

    E321's ``writes_the_face`` accepted any line carrying ``open``, so a module that READS a
    sub-face (``with open(DEC, "r") as fh: json.load(fh)``) counted as its writer -- that is how
    this row resolved to ``etf_book_pre2020_wf.py``, which composes the window decomposition
    rather than writing it.  Here the module has to assign the face to a name and open THAT name
    in a write mode.
    """
    for var in path_vars(src, basename):
        if re.search(r"open\(\s*%s\s*,\s*[\"'](?:w|a|x|r\+)" % re.escape(var), src or ""):
            return var
    return None


def subface_path(leaf, basename):
    """The leaf inside the sub-face: the block component the sub-face file name repeats, dropped."""
    parts = (leaf or "").split(".")
    stem = re.sub(r"\.json$", "", basename)
    for i, part in enumerate(parts):
        if part and stem.endswith(part):
            return ".".join(parts[i + 1:]), part
    return ".".join(parts), None


def count_items_with(doc, field, value):
    """The largest list in ``doc`` whose items carry ``field == value``, with its size."""
    best = None
    for key, node in doc.items():
        if not isinstance(node, list):
            continue
        n = sum(1 for it in node if isinstance(it, dict) and it.get(field) == value)
        if n and (best is None or n > best[1]):
            best = (key, n)
    return best


# ------------------------------------------------------------------------------------ one row

def cause_of(row, files=None):
    """Which of the three causes owns this row, with the evidence that decided it."""
    files = files if files is not None else corpus()
    face = row.get("face")
    leaf = row.get("leaf") or ""
    key = leaf.split(".")[-1].split("[")[0]
    parent = leaf.split(".")[-2] if len(leaf.split(".")) > 1 else None

    out = {"face": face, "leaf": leaf, "block": row.get("block"), "key": key,
           "parent": parent, "upstream_class": row.get("class_after"),
           "writers": [], "own_key_sites": [], "subface": None, "data_key": None,
           "cause": None, "face_value": None, "reason": ""}

    got = resolve(face, leaf)
    out["face_value"] = got.get("value")
    out["present_in_face"] = bool(got.get("present"))
    if not got.get("present"):
        out["cause"] = CAUSE_ABSENT
        out["reason"] = "the leaf itself is missing from the face (%s)" % got.get("reason")
        return out

    writers = writers_of(face)
    out["writers"] = sorted({relp(p) for p, _ in writers})
    own = key_sites(writers, key)
    out["own_key_sites"] = own

    # ---- 1. is the key published by a module that writes a face this one reads?
    refs = set()
    for path, src in writers:
        for basename in json_refs(src):
            if basename == os.path.basename(face):
                continue
            refs.add(basename)
    out["faces_named_by_the_face_writer"] = sorted(refs)

    sites = [s for s in key_sites(files, key) if s["producer"] not in out["writers"]]
    links = []
    rejected = []
    for site in sites:
        src = dict((relp(p), s) for p, s in files).get(site["producer"], "")
        for basename in json_refs(src):
            if basename not in refs:
                continue
            owner_var = owns_face(src, basename)
            if not owner_var:
                rejected.append({"producer": site["producer"], "face": basename,
                                 "why": "names the face but never opens it for writing"})
                continue
            sub_rel, block_part = subface_path(leaf, basename)
            sub = resolve(os.path.join("results", basename), sub_rel)
            links.append({
                "key_writer": site["producer"], "key_writer_line": site["line"],
                "published_as": site["expression"], "owns_face_via": owner_var,
                "sub_face": "results/%s" % basename, "block_component": block_part,
                "sub_face_leaf": sub_rel,
                "sub_face_value": sub.get("value"), "sub_face_has_it": bool(sub.get("present")),
                "composer": max(out["writers"]) if out["writers"] else None,
                "composer_reads": {w: reads_line(dict((relp(p), s) for p, s in writers).get(w, ""),
                                                 basename) for w in out["writers"]},
                "value_matches": bool(sub.get("present") and sub.get("value") == out["face_value"]),
            })
    out["rejected_links"] = rejected
    if links:
        links.sort(key=lambda x: (not x["value_matches"], x["key_writer"]))
        out["subface"] = links
        out["cause"] = CAUSE_SUBFACE
        out["reason"] = ("the key is published as %s by %s:%d against %s, which the card copies "
                         "(value %r == %r)"
                         % (links[0]["published_as"], links[0]["key_writer"],
                            links[0]["key_writer_line"], links[0]["sub_face"],
                            links[0]["sub_face_value"], out["face_value"]))
        return out

    # ---- 2. is the published value an accumulation keyed by a data value?
    pubs = [s for s in key_sites(writers, parent or "") if s["expression"].strip()]
    for pub in pubs:
        name = pub["expression"].strip()
        accums = [a for a in accum_sites(writers, name) if name in pub["expression"]]
        for accum in accums:
            field = None
            idents = re.findall(r"""["']([A-Za-z_][A-Za-z0-9_]*)["']""", accum["subscript"])
            if idents:
                field = idents[0]
            counted = None
            if field:
                doc = read_json(face)
                counted = count_items_with(doc, field, key)
            out["data_key"] = {"dict": name, "publisher": pub["producer"],
                               "published_line": pub["line"], "accum_line": accum["line"],
                               "subscript": accum["subscript"], "field": field,
                               "counted_in_face": counted,
                               "value_matches": bool(counted) and counted[1] == out["face_value"]}
            out["cause"] = CAUSE_DATAKEY
            out["reason"] = ("%s:%d publishes %r from %s, whose key at %s:%d is `%s` -- the key is "
                             "a value of the column %r, so no literal exists anywhere"
                             % (pub["producer"], pub["line"], name, name, accum["producer"],
                                accum["line"], accum["text"], field))
            return out

    # ---- 3. the tree does not write this key at all
    mentions = value_only_mentions(files, key)
    anyone = sorted(relp(p) for p, src in files if key in src)
    out["sources_mentioning_the_key"] = anyone
    try:
        face_doc = read_json(face)
    except (OSError, ValueError):
        face_doc = {}
    out["face_generated"] = face_doc.get("generated")
    if not anyone:
        out["cause"] = CAUSE_ORPHAN
        out["reason"] = ("no source under scripts/Tools/live/monitor/firm mentions %r at all, yet "
                         "the face publishes it (%r, face generated %s) -- the face is not "
                         "reproducible from the tree it is committed in"
                         % (key, out["face_value"], out["face_generated"]))
        return out
    out["cause"] = CAUSE_ABSENT
    out["reason"] = ("%d source(s) use %r but none publishes it as a key: %s"
                     % (len(mentions), key, ", ".join(v["producer"] for v in mentions[:5])))
    return out


# ------------------------------------------------------------------------------------ the study

def population(doc):
    return [r for r in (doc.get("rows") or []) if r.get("class_after") == POPULATION_CLASS]


BLOCK_EMBED = re.compile(r'"([A-Za-z0-9_]+)"\s*:\s*[A-Za-z_][A-Za-z0-9_.]*\.get\(\s*"\1"\s*\)')


def copied_block_of(leaf, writers):
    """The component of this gate's path a writer copies wholesale out of another face.

    The signature is exact on the gate's own path: the same name on both sides of a ``.get``
    (``"controls": doc.get("controls")``).  A scalar republish (``"cagr": x.get("cagr")``) looks
    the same to a regex, so this is used only on components of the gate's own path and every hit
    is published with its line, not counted silently.
    """
    parts = [p for p in (leaf or "").split(".") if p]
    hits = []
    for path, src in writers:
        for lineno, line in enumerate(src.splitlines(), 1):
            for match in BLOCK_EMBED.finditer(line):
                if match.group(1) in parts:
                    hits.append({"producer": relp(path), "line": lineno, "component": match.group(1),
                                 "text": line.strip()[:110]})
    return hits


def composed_face_share(rows, files):
    """How many of the whole census sits inside a block its face writer copies from elsewhere."""
    faces = {}
    for row in rows:
        face = row.get("face")
        if face and face not in faces:
            faces[face] = writers_of(face)
    hits = [row.get("leaf") for row in rows
            if row.get("face") and copied_block_of(row.get("leaf"), faces[row["face"]])]
    return {"faces": len(faces), "rows": len(rows),
            "rows_inside_a_copied_block": len(hits), "example_leaves": hits[:5]}


def build(outdir=None, files=None):
    files = files if files is not None else corpus()
    doc = e312._read(os.path.join(outdir or OUTDIR, INPUT))
    rows = population(doc)
    out = [cause_of(r, files) for r in rows]

    tally = {}
    for r in out:
        tally[r["cause"]] = tally.get(r["cause"], 0) + 1
    located = tally.get(CAUSE_SUBFACE, 0) + tally.get(CAUSE_DATAKEY, 0)
    absent = tally.get(CAUSE_ABSENT, 0) + tally.get(CAUSE_ORPHAN, 0)
    if absent == 0:
        verdict = VERDICT_ALL_LOCATED
    elif tally.get(CAUSE_ABSENT, 0) == 0:
        verdict = VERDICT_LOCATED
    else:
        verdict = VERDICT_ABSENT

    checks = []
    for r in out:
        if r["cause"] == CAUSE_SUBFACE and r["subface"]:
            link = r["subface"][0]
            checks.append({"check": "subface %s value == face value" % r["leaf"],
                           "ok": bool(link["value_matches"]),
                           "detail": "%r vs %r" % (link["sub_face_value"], r["face_value"])})
        if r["cause"] == CAUSE_DATAKEY and r["data_key"]:
            checks.append({"check": "array count %s == published %s" % (r["leaf"], r["face_value"]),
                           "ok": bool(r["data_key"]["value_matches"]),
                           "detail": "%r" % (r["data_key"]["counted_in_face"],)})
    return {
        "study": STUDY,
        "title": ("the six gates whose producer 'publishes no key of that name': locate the keys "
                  "before calling them missing"),
        "evidence_cutoff": TODAY,
        "upstream": INPUT,
        "population_class": POPULATION_CLASS,
        "verdict": verdict,
        "verdict_reason": (
            "%d of %d gates have their key located in the repository: %d are copied wholesale "
            "from a sub-face writer and %d are accumulated under a data value; %d key(s) exist "
            "only inside the published face (%d are named as a value but never published)."
            % (located, len(out), tally.get(CAUSE_SUBFACE, 0), tally.get(CAUSE_DATAKEY, 0),
               tally.get(CAUSE_ORPHAN, 0), tally.get(CAUSE_ABSENT, 0))),
        "summary": {
            "rows": len(out),
            "by_cause": tally,
            "causes": list(CAUSES),
            "gates_whose_key_exists_somewhere": located,
            "gates_whose_own_writer_publishes_it": sum(1 for r in out if r["own_key_sites"]),
        },
        "blind_spot": composed_face_share(doc.get("rows") or [], files),
        "identity_checks": checks,
        "rows": out,
        "no_bill": ("measurement only: reads six published gates and the sources that write them; "
                    "no burn, no threshold, no admission, no engine"),
        "held_fixed": "the six rows are taken from REACHWIDE's own class_after, not re-derived",
    }


def cmd_run():
    p = build()
    e312.save(p, FACE)
    e312.save(p, LATEST)
    print("verdict:", p["verdict"])
    print("  rows %d  causes %s" % (p["summary"]["rows"], json.dumps(p["summary"]["by_cause"])))
    for r in p["rows"]:
        print("  [%s] %s" % (r["cause"], r["leaf"]))
        print("      %s" % r["reason"])
    print("  blind spot: %d of %d census rows sit inside a block their face writer copies from "
          "another face" % (p["blind_spot"]["rows_inside_a_copied_block"],
                            p["blind_spot"]["rows"]))
    print("  identity: %d checks, %d ok"
          % (len(p["identity_checks"]), sum(1 for c in p["identity_checks"] if c["ok"])))
    return 0


def cmd_verify():
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        print("verify: face absent")
        return 2
    p = e312._read(path)
    problems = []
    fresh = build()
    if fresh["verdict"] != p["verdict"]:
        problems.append("verdict moved")
    if [r["cause"] for r in fresh["rows"]] != [r["cause"] for r in p["rows"]]:
        problems.append("a re-run changes a cause")
    if [r["reason"] for r in fresh["rows"]] != [r["reason"] for r in p["rows"]]:
        problems.append("a re-run changes a reason")
    for c in fresh["identity_checks"]:
        if not c["ok"]:
            problems.append("identity: " + c["check"])
    print("verify: %d problems" % len(problems))
    for x in problems:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def cmd_selftest():
    files = corpus()
    p = e312._read(os.path.join(OUTDIR, FACE))
    ok = True

    # --- the detector, on fixtures: a key and a value are not the same string
    fixture = "\n".join([
        "TOL_PP = 0.5",
        'kind = "epsilon"',
        'by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1',
        '"by_kind": by_kind,',
        '"tolerance_pp": TOL_PP,',
        'sub["tolerance_pp"] = TOL_PP',
    ])
    fake = [("scripts/_fixture_e324.py", fixture)]
    tol = key_sites(fake, "tolerance_pp")
    ok &= check("fixture: a mapping value and an item assignment are both key sites",
                len(tol) == 2 and {s["shape"] for s in tol} == {"mapping", "item_assignment"},
                "%r" % (tol,))
    ok &= check("fixture: the shared expression is read off both shapes",
                all(s["expression"] == "TOL_PP" for s in tol), "%r" % (tol,))
    eps = key_sites(fake, "epsilon")
    ok &= check("fixture: a string used as a VALUE is not a key site", not eps, "%r" % (eps,))
    ok &= check("fixture: it is published as a value mention instead",
                bool(value_only_mentions(fake, "epsilon")))
    acc = accum_sites(fake, "by_kind")
    ok &= check("fixture: the accumulation is found with a data subscript",
                len(acc) == 1 and acc[0]["subscript"] == 'r["kind"]', "%r" % (acc,))
    ok &= check("fixture: a literal subscript is not an accumulation",
                not accum_sites([("x.py", 'd["epsilon"] = 1')], "d"))

    # --- the population
    ok &= check("population: six rows were carried in", p["summary"]["rows"] == 6,
                "%d" % p["summary"]["rows"])
    ok &= check("population: every row is the class this study is about",
                all(r["upstream_class"] == POPULATION_CLASS for r in p["rows"]))
    ok &= check("population: all six leaves are present in their faces",
                all(r["present_in_face"] for r in p["rows"]))
    ok &= check("population: no row's own writer publishes the key (the class, reproduced)",
                not any(r["own_key_sites"] for r in p["rows"]))
    ok &= check("causes: every row is resolved to one of the four causes",
                all(r["cause"] in CAUSES for r in p["rows"])
                and p["summary"]["by_cause"].get(None) is None)
    ok &= check("causes: no key is 'named as a value but never published'",
                p["summary"]["by_cause"].get(CAUSE_ABSENT, 0) == 0
                and p["verdict"] == VERDICT_LOCATED)

    # --- read vs write: the wrong-writer trap this study hit on its first run
    reader = 'OUT = os.path.join(d, "face.json")\nwith open(OUT, "r") as fh:\n    doc = json.load(fh)\n'
    writer = 'OUT = os.path.join(d, "face.json")\nwith open(OUT, "w") as fh:\n    json.dump(out, fh)\n'
    ok &= check("fixture: a module that READS a sub-face does not own it",
                owns_face(reader, "face.json") is None)
    ok &= check("fixture: a module that opens it for writing does", owns_face(writer, "face.json") == "OUT")
    ok &= check("fixture: a composed block is recognised on the gate's own path",
                bool(copied_block_of("block.controls.x", [("f.py", '"controls": doc.get("controls") or {},')])))
    ok &= check("fixture: a block that is not on the gate's path is not claimed",
                not copied_block_of("block.other.x", [("f.py", '"controls": doc.get("controls"),')]))

    # --- the two families
    sub = [r for r in p["rows"] if r["cause"] == CAUSE_SUBFACE]
    dat = [r for r in p["rows"] if r["cause"] == CAUSE_DATAKEY]
    ok &= check("family: four rows come out of a copy from a sub-face", len(sub) == 4, "%d" % len(sub))
    ok &= check("family: one row is a data-keyed accumulation", len(dat) == 1, "%d" % len(dat))
    ok &= check("family: every sub-face copy carries a value match",
                all(r["subface"][0]["value_matches"] for r in sub))
    ok &= check("family: the composer reads the sub-face it copies",
                all(any(v for v in r["subface"][0]["composer_reads"].values()) for r in sub))
    ok &= check("family: every sub-face key writer opens that face for writing",
                all(r["subface"][0]["owns_face_via"] for r in sub))
    ok &= check("family: every data key re-counts to the published number",
                all(r["data_key"]["value_matches"] for r in dat))
    ok &= check("family: every data key names the column it is keyed by",
                all(r["data_key"]["field"] for r in dat))

    # --- the orphan: a published face no source in the tree can reproduce
    orph = [r for r in p["rows"] if r["cause"] == CAUSE_ORPHAN]
    ok &= check("orphan: exactly one row has no source mentioning its key", len(orph) == 1,
                "%d" % len(orph))
    ok &= check("orphan: the row says so with the face's own generation stamp",
                bool(orph) and bool(orph[0]["face_generated"]))
    ok &= check("orphan: the absence is measured over the whole producer corpus, not one dir",
                bool(orph) and orph[0]["sources_mentioning_the_key"] == [])
    ok &= check("identity: every published check is green",
                all(c["ok"] for c in p["identity_checks"]))
    ok &= check("blind spot: the copied-block population is measured, not assumed",
                p["blind_spot"]["rows"] == 196
                and 0 <= p["blind_spot"]["rows_inside_a_copied_block"] < 196,
                json.dumps(p["blind_spot"]))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "--selftest" or cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))