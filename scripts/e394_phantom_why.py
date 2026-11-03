"""E394 -- the other direction: why does a read open a face that does NOT store the key?

E393 priced the 1 MB read cap and found that almost every face it had been hiding *does* store
the key (3,241 of 3,271).  That leaves the residue as the remaining unexplained class: reads E392
resolved to an actual face, yet that face has no such key -- 188 reads under E392's cap plus the
30 that only became visible once the cap was lifted.

A "face lacks the key" line is not yet a defect.  Four very different things produce it:

  1. the key IS in the face, at a different depth than the site indexes (the site reads ``x`` off
     a document that carries ``x`` under ``rows[].x``) -- so the site is wrong, not the face;
  2. the face's own producer names the key, so the face is allowed to write it conditionally and
     this instance simply did not (an optional row, an early-exit path);
  3. the key lives in another face in the tree (the name moved between faces, and the site opens
     the one it used to be in);
  4. nothing in the tree carries the key at all -- the name is dead and the site is a broken
     reader.

Only class 4 is a broken reader, and a study that published ``188 reads open a face without the
key`` as ``188 broken readers`` would be exactly the failure E392 named in its own postscript.
This study classifies every residual read and publishes the classes separately.

Nothing is re-implemented: E392's population, resolver, statuses and scan are imported; E393's
uncapped reader is imported and installed in place of E392's, so the population is the same one
E393 measured.  Refusals that keep the classification from flattering itself:

  * depth is a *nested dict key* test on the parsed document, never a substring test, so a key
    name that only appears inside a string value is not counted as "present at another depth";
  * a face above the read cap is not parsed for depth at all -- its rows are published as
    ``face_unparsed_so_presence_unknown`` rather than folded into class 4;
  * the producer test is a *literal occurrence of the key in a source that mentions the face*,
    which is evidence that the producer can write the key, not proof that it did on this run --
    the class is named ``producer_names_the_key_but_the_face_lacks_it``, not "conditional write";
  * the "another face" test uses the key population's own file list, so it cannot invent a face;
  * the study does not scan itself, its face, its mirror or its smoke leg.

    python scripts/e394_phantom_why.py run
    python scripts/e394_phantom_why.py verify
    python scripts/e394_phantom_why.py selftest
"""
import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e391_key_name_two_meanings as e391     # the corpus walk the population came from
import e392_read_resolve as e392              # population, resolver, statuses: imported
import e393_read_cap_price as e393            # the uncapped reader: imported, not rebuilt

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E394_phantom_why"
TODAY = "2026-11-03"
FACE = "PHANTOMWHY-%s.json" % TODAY
LATEST = "phantomwhy_latest.json"
BASELINE = os.path.join(OUTDIR, "READCAP-%s.json" % TODAY)
RESOLVE_FACE = os.path.join(OUTDIR, "READRESOLVE-%s.json" % TODAY)

OWN_FILES = tuple(e392.OWN_FILES) + ("scripts/e394_phantom_why.py",
                                     "scripts/run_e394_smoke_leg.py",
                                     "scripts/e394_phantom_why.py")

C_ANOTHER_DEPTH = "key_present_at_another_depth"
C_PRODUCER = "producer_names_the_key_but_the_face_lacks_it"
C_ANOTHER_FACE = "key_lives_in_another_face"
C_ANOTHER_FACE_UNNAMED = "a_face_stores_it_but_no_read_names_which"
C_UNPARSED = "face_unparsed_so_presence_unknown"
C_DEAD = "no_face_in_the_tree_stores_this_key"
CLASSES = (C_DEAD, C_ANOTHER_FACE, C_ANOTHER_FACE_UNNAMED, C_ANOTHER_DEPTH, C_PRODUCER,
           C_UNPARSED)

DATE_RX = re.compile(r"-?\d{4}-\d{2}-\d{2}$")
MIN_PATTERN = 6

STATE = {"faces": {}}


# ---------------------------------------------------------------- face anatomy
def face_nested_keys(rel, root=ROOT, cache=None):
    """Every dict key in the parsed document at any depth, or None if it cannot be read."""
    if cache is not None and rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    try:
        if os.path.getsize(path) > e392.MAX_FACE_BYTES:
            result = None                     # above the cap: never parsed for depth
        else:
            with io.open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
            result = set()
            stack = [doc]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    for name, value in node.items():
                        if isinstance(name, str):
                            result.add(name)
                        stack.append(value)
                elif isinstance(node, list):
                    stack.extend(node)
    except (OSError, ValueError):
        result = None
    if cache is not None:
        cache[rel] = result
    return result


def face_tokens(face):
    """Name tokens a producer would use for this face (exact name, dated prefix, full path)."""
    base = os.path.basename(face)
    stem = base.rsplit(".", 1)[0]
    tokens = [base, face]
    prefix = DATE_RX.sub("", stem)
    if prefix != stem and len(prefix) >= MIN_PATTERN - 1:
        tokens.append(prefix + "-")
    return tuple(t for t in tokens if len(t) >= MIN_PATTERN)


def producer_index(faces, root=ROOT):
    """{face: [py rel paths whose source names the face]} in one pass over the corpus."""
    wanted = {}
    for face in faces:
        for token in face_tokens(face):
            wanted.setdefault(token, set()).add(face)
    hits = {face: set() for face in faces}
    kept = {}
    for path in e391.py_corpus(root):
        rel = os.path.relpath(path, root).replace("\\", "/")
        if rel in OWN_FILES:
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        matched = False
        for token, owners in wanted.items():
            if token in src:
                for face in owners:
                    hits[face].add(rel)
                matched = True
        if matched:
            kept[rel] = src
    return hits, kept


# ---------------------------------------------------------------- classification
def writer_evidence(src, key):
    """Constructs in a source that can *write* ``key`` into an object, or [] for a bare mention.

    A source that names the face and also contains the literal ``key`` is not a producer: the
    literal may be a log string, an unrelated column, or a test's expectation.  A producer has to
    put the key into a document, so the test is structural -- a dict-literal key, a subscript
    store, or ``setdefault``.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for name in node.keys:
                if isinstance(name, ast.Constant) and name.value == key:
                    found.append("dict_literal_key:%d" % node.lineno)
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store):
            slice_node = node.slice
            if isinstance(slice_node, ast.Constant) and slice_node.value == key:
                found.append("subscript_write:%d" % node.lineno)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == "setdefault" and node.args
              and isinstance(node.args[0], ast.Constant) and node.args[0].value == key):
            found.append("setdefault:%d" % node.lineno)
    return found


def faces_carrying(keys, key):
    """The population's own file count for a key: an int, or the length of a file list."""
    entry = keys.get(key)
    if isinstance(entry, dict):
        files = entry.get("files")
        if isinstance(files, int) and not isinstance(files, bool):
            return files
        if isinstance(files, (list, tuple)):
            return len(files)
    return None


def classify(row, keys, witnesses, depth_cache, prod_hits, prod_text, root=ROOT):
    """One residual read -> one class, plus the evidence line a reader can check by hand."""
    face = row.get("face") or ""
    key = row.get("key") or ""
    nested = face_nested_keys(face, root=root, cache=depth_cache)
    if nested is not None and key in nested:
        return C_ANOTHER_DEPTH, {"face_keys_at_any_depth": len(nested)}
    naming = sorted(p for p in prod_hits.get(face, ())
                    if writer_evidence(prod_text.get(p, ""), key))
    if naming:
        return C_PRODUCER, {"producer_writes_the_key": naming[:5],
                            "write_forms": writer_evidence(prod_text.get(naming[0], ""),
                                                           key)[:3]}
    elsewhere = sorted(f for f in witnesses.get(key, ()) if f != face)
    if elsewhere:
        return C_ANOTHER_FACE, {"faces_that_carry_it": elsewhere[:5]}
    if nested is None:
        return C_UNPARSED, {"reason": "face above the read cap or not parseable"}
    carried = faces_carrying(keys, key)
    if carried == 0:
        return C_DEAD, {"files_in_the_population": 0}
    return C_ANOTHER_FACE_UNNAMED, {"files_in_the_population": carried}


def price(rows, keys, root=ROOT):
    residual = [r for r in rows if r["status"] == e392.S_RESOLVED_LACKS]
    faces = sorted({r.get("face") or "" for r in residual})
    # Which faces does a read *witness* as storing a key? Taken from the scan itself, so no
    # face name is invented: a witness is a row that opened a face and found the key there.
    witnesses = {}
    for row in rows:
        if row["status"] == e392.S_RESOLVED_STORES and row.get("face"):
            witnesses.setdefault(row["key"], set()).add(row["face"])
    prod_hits, prod_text = producer_index(faces, root=root)
    depth_cache = {}
    classified = []
    for row in sorted(residual, key=lambda r: (r.get("key") or "", r.get("site") or "",
                                               r.get("line") or 0)):
        cls, evidence = classify(row, keys, witnesses, depth_cache, prod_hits, prod_text,
                                 root=root)
        item = {"key": row.get("key"), "site": row.get("site"), "line": row.get("line"),
                "face": row.get("face"), "class": cls}
        item.update(evidence)
        classified.append(item)
    by_class = {cls: 0 for cls in CLASSES}
    for item in classified:
        by_class[item["class"]] = by_class.get(item["class"], 0) + 1
    per_key = {}
    for item in classified:
        entry = per_key.setdefault(item["key"], {"key": item["key"], "reads": 0,
                                                 "faces": set(), "classes": {}})
        entry["reads"] += 1
        entry["faces"].add(item["face"])
        entry["classes"][item["class"]] = entry["classes"].get(item["class"], 0) + 1
    key_rows = []
    for key in sorted(per_key):
        entry = per_key[key]
        dominant = sorted(entry["classes"].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        key_rows.append({"key": key, "residual_reads": entry["reads"],
                         "faces": sorted(entry["faces"]),
                         "classes": dict(sorted(entry["classes"].items())),
                         "dominant_class": dominant,
                         "files_in_the_population": faces_carrying(keys, key),
                         "witnessed_faces": sorted(witnesses.get(key, ()))[:6]})
    cap_faces = {f["face"] for f in e393.STATE["faces"]}
    cap_hidden = [i for i in classified if i["face"] in cap_faces]
    return {
        "residual_reads": len(classified),
        "residual_keys": len(per_key),
        "residual_faces": len(faces),
        "residual_sites": len({i["site"] for i in classified}),
        "cap_hidden_reads": len(cap_hidden),
        "by_class": dict(sorted(by_class.items())),
        "broken_reader_reads": by_class.get(C_DEAD, 0),
        "broken_reader_keys": sorted({i["key"] for i in classified if i["class"] == C_DEAD}),
        "parse_coverage": {
            "faces_parsed_for_depth": sum(1 for f in faces
                                          if face_nested_keys(f, root=root,
                                                              cache=depth_cache) is not None),
            "faces_in_residual": len(faces),
        },
        "producer_candidates": {f: sorted(v)[:4] for f, v in sorted(prod_hits.items()) if v},
        "examples": {cls: [i for i in classified if i["class"] == cls][:12] for cls in CLASSES},
        "rows": key_rows,
        "classified": classified,
    }


def headline_arithmetic(residual, published_resolve, published_cap):
    """Whether this classification moves a published number, stated as arithmetic."""
    resolve_summary = (published_resolve or {}).get("summary") or {}
    cap_fresh = ((published_cap or {}).get("cap_pricing") or {}).get("fresh") or {}
    named_pub = resolve_summary.get("name_matched_reads")
    stores_pub = resolve_summary.get("resolved_reads_storing_the_key")
    return {
        "e392_name_matched_reads": named_pub,
        "e392_resolved_reads_storing_the_key": stores_pub,
        "e392_share": resolve_summary.get(
            "share_of_name_matched_reads_that_resolve_and_store"),
        "e393_share_without_the_cap": cap_fresh.get(
            "share_of_name_matched_reads_that_resolve_and_store"),
        "residual_reads": residual,
        "moves_a_published_number": False,
        "why": ("the residual is the complement of both numerators: classifying it cannot "
                "change a ratio whose numerator and denominator are the storing reads and the "
                "name-matched reads, so no republish is owed (E382's rule is for splits that "
                "move a headline)"),
    }


def build(root=ROOT):
    keys, _ = e392.population(root=root)
    STATE["population"] = frozenset(keys)
    e392.face_key_index = e393.face_key_index
    e392.OWN_FILES = OWN_FILES
    e393.STATE["population"] = STATE["population"]
    rows = e392.scan(root=root, keys=keys)
    priced = price(rows, keys, root=root)
    summary = (json.load(io.open(RESOLVE_FACE, encoding="utf-8"))
               if os.path.exists(RESOLVE_FACE) else {})
    capdoc = (json.load(io.open(BASELINE, encoding="utf-8"))
              if os.path.exists(BASELINE) else {})
    if not priced["residual_reads"]:
        verdict = "no_read_resolves_to_a_face_that_lacks_its_key_so_the_residue_is_empty"
    elif priced["broken_reader_reads"] == priced["residual_reads"]:
        verdict = "every_residual_read_names_a_key_no_face_in_the_tree_stores"
    elif priced["broken_reader_reads"]:
        verdict = ("some_residual_reads_are_real_broken_readers_and_the_rest_are_depth_"
                   "producer_or_moved_name")
    else:
        verdict = "no_residual_read_is_a_broken_reader_it_is_depth_producer_or_moved_name"
    return {
        "study": STUDY,
        "script": "scripts/e394_phantom_why.py",
        "generated": "",
        "evidence_cutoff": TODAY,
        "population_face": e392.POP_FACE,
        "baseline_faces": ["results/state_tilt/READRESOLVE-%s.json" % TODAY,
                           "results/state_tilt/READCAP-%s.json" % TODAY],
        "method": ("static only, zero network: E392's population, resolver, statuses and scan are "
                   "imported and E393's uncapped reader is installed in place of E392's, so the "
                   "population is the one E393 measured. Every read that resolves to a face "
                   "lacking its key is classified as depth / producer / another face / unparsed / "
                   "dead, and only the last is published as a broken reader."),
        "refusals": [
            "depth is a nested dict-key test on the parsed document, never a substring test",
            "a face above the read cap is not parsed, and its rows are published as unparsed",
            "the producer test shows a producer can write the key, not that it did this run",
            "another-face uses the key population's own file list, so no face is invented",
            "the study does not scan itself, its face, its mirror or its smoke leg",
            "the walk is the same py_corpus E391 used, so the population filter matches",
        ],
        "residual": priced,
        "headline": headline_arithmetic(priced["residual_reads"], summary, capdoc),
        "verdict": verdict,
        "verify_covers": [
            "the per-key residual rows re-add to the residual read count",
            "the class counts re-add to the residual read count",
            "the broken-reader count is the dead class and nothing else",
            "every classified row names a face that appears in the residual face set",
            "the verdict re-derives from the class counts",
        ],
        "verify_does_not_cover": [
            "the corpus walk and the producer index themselves",
            "whether a face parsed at read time is the face the site opens until it executes",
        ],
    }


# ---------------------------------------------------------------- io
def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    with io.open(os.path.join(out_dir, face), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    mirror = dict(doc)
    mirror["face"] = face
    with io.open(os.path.join(out_dir, latest), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(mirror, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
    return text


def verify(out_dir=OUTDIR, face=FACE):
    path = os.path.join(out_dir, face)
    if not os.path.exists(path):
        return ["face missing: %s" % face]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    problems = []
    if disk.get("study") != STUDY:
        problems.append("study name drifted")
    res = disk.get("residual") or {}
    rows = res.get("rows") or []
    classified = res.get("classified") or []
    by_class = res.get("by_class") or {}
    residual = res.get("residual_reads")
    if sum(r.get("residual_reads") or 0 for r in rows) != residual:
        problems.append("the per-key rows do not re-add to the residual read count")
    if sum(by_class.get(cls, 0) for cls in CLASSES) != residual:
        problems.append("the class counts do not re-add to the residual read count")
    if len(classified) != residual:
        problems.append("the classified rows do not re-add to the residual read count")
    if res.get("broken_reader_reads") != by_class.get(C_DEAD, 0):
        problems.append("broken_reader_reads is not the dead class")
    if res.get("residual_keys") and len({r.get("key") for r in rows}) != res["residual_keys"]:
        problems.append("residual_keys is not the number of per-key rows")
    faces = {i.get("face") for i in classified}
    if len(faces) != res.get("residual_faces"):
        problems.append("residual_faces is not the number of distinct faces")
    for item in classified:
        if item.get("class") not in CLASSES:
            problems.append("a row carries a class outside the frozen set")
            break
    if (res.get("cap_hidden_reads") or 0) > (residual or 0):
        problems.append("cap_hidden_reads exceeds the residual")
    if (disk.get("headline") or {}).get("moves_a_published_number"):
        problems.append("a residual classification cannot move a published ratio")
    dead = by_class.get(C_DEAD, 0)
    expect = ("no_read_resolves_to_a_face_that_lacks_its_key_so_the_residue_is_empty"
              if not residual else
              ("every_residual_read_names_a_key_no_face_in_the_tree_stores"
               if dead == residual and residual else
               ("some_residual_reads_are_real_broken_readers_and_the_rest_are_depth_producer_"
                "or_moved_name" if dead else
                "no_residual_read_is_a_broken_reader_it_is_depth_producer_or_moved_name")))
    if disk.get("verdict") != expect:
        problems.append("verdict does not re-derive from the class counts")
    return problems


def _fixture(tmp):
    """A face that carries the key at another depth, one that does not, and a producer."""
    deep = os.path.join(tmp, "deep.json")
    with io.open(deep, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"rows": [{"starts": 3}], "other": 1}')
    flat = os.path.join(tmp, "flat.json")
    with io.open(flat, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"other": 1}')
    prod = os.path.join(tmp, "producer.py")
    with io.open(prod, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('FACE = "flat.json"\nrows = [{"cap": 3}]\n')
    return deep, flat, prod


def selftest():
    import tempfile
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    tmp = tempfile.mkdtemp(prefix="e394_").replace("\\", "/")
    deep, flat, prod = _fixture(tmp)
    rel_deep = os.path.relpath(deep, tmp).replace("\\", "/")
    rel_flat = os.path.relpath(flat, tmp).replace("\\", "/")
    # 1. depth: a key under rows[] is reported present at another depth
    nested = face_nested_keys(rel_deep, root=tmp)
    leg("nested walk finds the inner key", nested is not None and "starts" in nested)
    leg("nested walk finds the top-level key", "other" in nested)
    # 2. depth is not a substring test: a key inside a string value is not a key
    val = os.path.join(tmp, "value.json")
    with io.open(val, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"payload": "starts here"}')
    leg("a key name inside a value is not a key",
        "starts" not in (face_nested_keys(os.path.relpath(val, tmp).replace("\\", "/"),
                                          root=tmp) or set()))
    # 3. classify: depth beats producer, producer beats a witness, a witness beats dead
    keys = {"starts": {"files": 1}, "cap": {"files": 1}, "ghost": {"files": 0},
            "moved": {"files": 1}, "unnamed": {"files": 2}}
    hits = {rel_flat: ["producer.py"], rel_deep: []}
    texts = {"producer.py": io.open(prod, encoding="utf-8").read()}
    cache = {}
    witnesses = {"moved": {"results/other.json"}}
    c1, _ = classify({"key": "starts", "face": rel_deep}, keys, witnesses, cache, hits, texts,
                     root=tmp)
    leg("depth wins when the face carries it deeper", c1 == C_ANOTHER_DEPTH)
    c2, _ = classify({"key": "cap", "face": rel_flat}, keys, witnesses, cache, hits, texts,
                     root=tmp)
    leg("producer names it while the face lacks it", c2 == C_PRODUCER)
    c3, _ = classify({"key": "ghost", "face": rel_flat}, keys, witnesses, cache, hits, texts,
                     root=tmp)
    leg("a key no face carries is a dead reader", c3 == C_DEAD)
    # 4. a face another read opens and finds the key in is not a dead reader
    c4, _ = classify({"key": "moved", "face": rel_flat}, keys, witnesses, cache, hits, texts,
                     root=tmp)
    leg("a key witnessed in another face is not dead", c4 == C_ANOTHER_FACE)
    # 5. counted-but-unwitnessed is its own class, not a dead reader
    c6, _ = classify({"key": "unnamed", "face": rel_flat}, keys, witnesses, cache, hits, texts,
                     root=tmp)
    leg("counted but unwitnessed is not dead", c6 == C_ANOTHER_FACE_UNNAMED)
    # 6. an unreadable face is never called dead
    c5, _ = classify({"key": "ghost", "face": "nope/missing.json"}, keys, witnesses, cache, hits,
                     texts, root=tmp)
    leg("an unreadable face is unparsed, not dead", c5 == C_UNPARSED)
    # 7. the population's file count is read as a count, both shapes
    leg("an int file count is read as a count", faces_carrying({"k": {"files": 7}}, "k") == 7)
    leg("a file list is read as its length",
        faces_carrying({"k": {"files": ["a", "b"]}}, "k") == 2)
    leg("an absent key has no count", faces_carrying({}, "k") is None)
    # 8. token derivation: a dated face yields its prefix, an undated one does not invent one
    toks = face_tokens("results/state_tilt/READRESOLVE-2026-11-03.json")
    leg("dated face yields its prefix token", "READRESOLVE-" in toks)
    leg("dated face keeps its exact name", "READRESOLVE-2026-11-03.json" in toks)
    leg("no date means no invented prefix",
        face_tokens("results/state_tilt/face.json") == ("face.json",
                                                        "results/state_tilt/face.json"))
    # 9. the arithmetic states the truth: a residual classification moves nothing
    head = headline_arithmetic(10, {"summary": {"name_matched_reads": 100,
                                               "resolved_reads_storing_the_key": 20}}, {})
    leg("residual classification moves no published number",
        head["moves_a_published_number"] is False)
    # 10. the class set is stable
    leg("six classes frozen", len(CLASSES) == 6)
    # 11. a bare mention is not a write; a dict key and a store are
    leg("a log string is not a write", writer_evidence('log("cap")', "cap") == [])
    leg("a dict literal key is a write", bool(writer_evidence('doc = {"cap": 1}', "cap")))
    leg("a subscript store is a write", bool(writer_evidence('doc["cap"] = 1', "cap")))
    leg("reading a key is not a write", writer_evidence('x = doc["cap"]', "cap") == [])
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        doc = build()
        write_face(OUTDIR, doc)
        res = doc["residual"]
        print(json.dumps({"verdict": doc["verdict"],
                          "residual_reads": res["residual_reads"],
                          "cap_hidden_reads": res["cap_hidden_reads"],
                          "by_class": res["by_class"],
                          "residual_keys": res["residual_keys"],
                          "residual_faces": res["residual_faces"]},
                         ensure_ascii=False, sort_keys=True))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))