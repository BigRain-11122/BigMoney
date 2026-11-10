"""E652 -- the corpus-wide size of the string arm E647 measured only at its hits.

E647 asked the question of the six modules that already had a cross-module key-name collision, using
the two counted read modules those hits joined. That answers "is there a string route from these
hits" and it cannot answer "is a string route a property of these six modules or of the tree". This
study runs the same instrument unchanged over the whole corpus and all six counted read modules, so
every module that spells a counted read module -- by path, basename, stem, dotted name, or one of the
face constants it assigns itself -- is priced by two things at once: what consumes that string
(import machinery, a file open, exec/sys.path, a path join, nothing) and whether the spelling module
also carries a counted row key at all.

The pair matters because a spelling and a container are different claims. A module can name another
module in a string and still never hold the dict the counted read line reads; a module can hold that
dict and never name the read module. Only a module that does both has the route E646 called
invisible, so the face publishes that intersection rather than the spellers alone.

Deliverable: results/state_tilt/STRINGARMCENSUS.json
Run:      python scripts/e652_string_arm_census.py [run|check|verify|selftest]
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "STRINGARMCENSUS.json"
LATEST = "stringarmcensus_latest.json"
STUDY = "E652_string_arm_census"
SOURCE_FACE = "results/state_tilt/STRINGREACH.json"
SELF_PARTS = ("e652_", "run_e652_", "_probe_e652", "_r1672")
MAX_BYTES = 1024 * 1024
MAX_LITERALS_PER_ROW = 12
VALUE_TRUNC = 120

import e642_module_write_key as e642  # noqa: E402
import e646_crossmodule_key as e646  # noqa: E402
import e647_string_reach as e647  # noqa: E402
import e648_keygenericity as e648  # noqa: E402

MATCH_ORDER = ("exact_path", "exact_basename", "exact_stem", "exact_dotted", "exact_face",
               "token_contains_stem")
LOADER_REACH = ("import_string_reach", "loader_machinery_without_a_module_name")

V_NO_READ_POPULATION = (
    "the_counted_read_population_is_empty,_so_there_is_no_module_for_a_string_to_name_and_the_"
    "question_does_not_apply")
V_NO_SPELLER = (
    "no_file_in_the_corpus_spells_a_counted_read_module,_its_stem_or_one_of_its_own_face_constants_"
    "in_a_string_it_can_be_asked_to_spell,_so_the_string_arm_is_empty_corpus-wide_and_not_only_at_"
    "the_hits_E647_measured")
V_KEY_AND_A_LOADER = (
    "at_least_one_module_that_names_a_counted_read_module_reaches_it_through_a_string_the_import_"
    "or_loader_machinery_consumes_and_also_carries_a_counted_row_key,_so_the_invisible_arm_is_a_"
    "property_of_the_tree_rather_than_of_the_hits")
V_LOADER_BUT_NO_KEY = (
    "modules_spell_a_counted_read_module_inside_a_string_a_loader_consumes_but_none_of_them_"
    "carries_a_counted_row_key,_so_the_route_exists_and_lands_where_none_of_the_counted_read_"
    "lines_read")
V_KEY_BUT_NO_LOADER = (
    "modules_that_spell_a_counted_read_module_do_carry_a_counted_row_key_but_only_in_strings_no_"
    "loader_consumes,_so_the_key_is_present_and_the_module_is_never_resolved_from_that_string")
V_NAME_ONLY = (
    "modules_name_a_counted_read_module_in_strings_no_loader_consumes_and_none_of_them_carries_a_"
    "counted_row_key,_so_a_spelling_names_a_module_without_reaching_the_container")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def corpus(root=ROOT):
    """E642's population, minus this study's own files (E180/E207: a census never counts itself)."""
    out = []
    for p in e642.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def _norm(value):
    return e647._strip_dot(str(value).replace("\\", "/").strip())


# ---------------------------------------------------------------- target index
def target_index(read_modules, root=ROOT):
    """Every spelling of every counted read module, exact classes in one lookup and stems apart."""
    exact, tokens, spellings = {}, [], {}
    for rm in read_modules:
        sp = e647.spellings_of(rm, root)
        spellings[rm] = sp
        for value, cls in ((sp["path"], "exact_path"), (sp["basename"], "exact_basename"),
                           (sp["stem"], "exact_stem"), (sp["dotted"], "exact_dotted")):
            key_value = _norm(value)
            if key_value:
                exact.setdefault(key_value, []).append((rm, cls))
        for face in sp["faces"]:
            exact.setdefault(_norm(face), []).append((rm, "exact_face"))
        if sp["stem"]:
            tokens.append((e647._stem_pattern(sp["stem"]), rm))
    for value, hits in list(exact.items()):
        best = {}
        for rm, cls in hits:
            if rm not in best or MATCH_ORDER.index(cls) < MATCH_ORDER.index(best[rm]):
                best[rm] = cls
        exact[value] = sorted(best.items())
    return {"exact": exact, "tokens": tokens, "spellings": spellings}


def match_literal(value, index):
    """(read_module, match_class) pairs for one measurable string -- exact first, tokens apart."""
    text = _norm(value)
    out = {}
    for rm, cls in index["exact"].get(text, []):
        out[rm] = cls
    for pattern, rm in index["tokens"]:
        if rm in out:
            continue
        if pattern.search(text):
            out[rm] = "token_contains_stem"
    return sorted(out.items())


def reach_from_consumers(classes):
    """The strongest route a set of consumer classes gives, in E647's own vocabulary."""
    return e647.reach_class_of([{"consumer_class": c} for c in sorted(classes)])


# ---------------------------------------------------------------- per-file
def _string_positions(tree):
    """(line, column) -> node for every string-bearing node, so a literal is found in O(1)."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out[(node.lineno, node.col_offset)] = node
        elif isinstance(node, ast.JoinedStr):
            out[(node.lineno, node.col_offset)] = node
        elif isinstance(node, ast.BinOp):
            out[(node.lineno, node.col_offset)] = node
    return out


def scan_file(path, keys, index, root=ROOT):
    """(payload, None) or (None, why): the strings of one file priced against every read module."""
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None, "over_the_size_cap"
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, "unreadable"
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None, "does_not_parse"
    parents = e647.parents_of(tree)
    literals, unresolved = e647.collect_strings(tree)
    counted_keys_named = sorted({lit["value"] for lit in literals if lit["value"] in keys})
    subscript_sites = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str) and sl.value in keys:
                subscript_sites += 1
    naming = []
    if index["spellings"]:
        positions = _string_positions(tree)
        for lit in literals:
            for rm, cls in match_literal(lit["value"], index):
                node = positions.get((lit["line"], lit["column"]))
                cons = (e647.consumption(parents, node) if node is not None
                        else {"call": None, "consumer_class": "no_call",
                              "bound_name": None, "hops": 0})
                naming.append({
                    "read_module": rm,
                    "line": lit["line"],
                    "column": lit["column"],
                    "value": lit["value"][:VALUE_TRUNC],
                    "built": lit["built"],
                    "match": cls,
                    "consumer": cons["call"],
                    "consumer_class": cons["consumer_class"],
                    "bound_name": cons["bound_name"],
                })
        naming.sort(key=lambda r: (r["read_module"], r["line"], r["column"], r["match"]))
    # a module that IS the read module spells its own stem and its own face constants by
    # definition; that is not a route, so it is excluded and the exclusion is counted
    own = rel(path, root)
    self_spellings = len([n for n in naming if n["read_module"] == own])
    naming = [n for n in naming if n["read_module"] != own]
    return {"naming": naming,
            "self_spellings_excluded": self_spellings,
            "counted_keys_named": counted_keys_named,
            "subscript_key_sites": subscript_sites,
            "string_literals": len(literals),
            "unresolved_strings": len(unresolved)}, None


# ---------------------------------------------------------------- measure
def measure(root=ROOT, counted=None):
    reads = e648.read_population() if counted is None else counted
    keys = {r["key"] for r in reads if r.get("key")}
    read_modules = sorted({r["module"] for r in reads if r.get("module")})
    index = target_index(read_modules, root)
    files = corpus(root)

    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    rows = []
    volume = {"string_literals_examined": 0, "unresolved_strings": 0,
              "files_carrying_a_counted_row_key": 0, "self_spellings_excluded": 0}
    for path in files:
        got, why = scan_file(path, keys, index, root)
        if why is not None:
            holes[why] = holes.get(why, 0) + 1
            continue
        volume["string_literals_examined"] += got["string_literals"]
        volume["unresolved_strings"] += got["unresolved_strings"]
        volume["self_spellings_excluded"] += got["self_spellings_excluded"]
        if got["counted_keys_named"] or got["subscript_key_sites"]:
            volume["files_carrying_a_counted_row_key"] += 1
        if not got["naming"]:
            continue
        naming = got["naming"]
        by_match, by_consumer, per_rm = {}, {}, {}
        for n in naming:
            by_match[n["match"]] = by_match.get(n["match"], 0) + 1
            by_consumer[n["consumer_class"]] = by_consumer.get(n["consumer_class"], 0) + 1
            per_rm.setdefault(n["read_module"], []).append(n)
        module_reach = {rm: e647.reach_class_of(hits)
                        for rm, hits in sorted(per_rm.items())}
        strongest = max(module_reach.values(),
                        key=lambda r: e647.SEVERITY.get(r, 0))
        published = naming[:MAX_LITERALS_PER_ROW]
        rows.append({
            "module": rel(path, root),
            "module_class": e646.module_class(rel(path, root)),
            "read_modules": sorted(per_rm),
            "read_module_reach": module_reach,
            "reach": strongest,
            "match_classes": sorted(by_match),
            "consumer_classes": sorted(by_consumer),
            "naming_literal_count": len(naming),
            "naming_by_match": {k: by_match[k] for k in sorted(by_match)},
            "naming_by_consumer": {k: by_consumer[k] for k in sorted(by_consumer)},
            "carries_a_counted_row_key": bool(got["counted_keys_named"]),
            "counted_keys_named": got["counted_keys_named"],
            "subscript_key_sites": got["subscript_key_sites"],
            "string_literals": got["string_literals"],
            "unresolved_strings": got["unresolved_strings"],
            "naming_literals": published,
            "naming_literals_elided": max(0, len(naming) - len(published)),
        })
    rows.sort(key=lambda r: r["module"])

    counts = counts_of(rows)
    volume.update({
        "python_files_seen": len(files),
        "python_files_scanned": len(files) - sum(holes.values()),
        "holes": holes,
        "counted_read_lines": len(reads),
        "counted_row_keys": len(keys),
        "counted_read_modules": len(read_modules),
        "read_modules": read_modules,
    })
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": (
            "re-derive the counted read population E638 joins, then run E647's string instrument "
            "unchanged over the whole Python corpus: every string a file can be asked to spell "
            "(literals, all-constant f-strings, constant concatenations) is matched against each "
            "counted read module's measured spellings (path, basename, stem, dotted name, and the "
            "FACE/LATEST constants that module assigns itself), exact classes first and whole-token "
            "containment apart, and every naming string is priced by the call that consumes it; each "
            "spelling module is then crossed with whether the same file spells or subscripts a "
            "counted row key at all"),
        "population_source": (
            "%d Python files of E642's corpus over %d counted read line(s) in %d module(s) and %d "
            "key(s); %d string(s) examined corpus-wide, %d built from an expression"
            % (len(files), len(reads), len(read_modules), len(keys),
               volume["string_literals_examined"], volume["unresolved_strings"])),
        "volume": volume,
        "counts": counts,
        "by_spelling_class": by_spelling_class(rows),
        "rows": rows,
        "limits": [
            "a spelling is a route and not a demonstration: naming a module never proves the object "
            "resolved from that string is the container the counted read line reads, so the "
            "key-and-loader intersection is the strongest claim this face makes",
            "strings built from an expression (f-string with a value, str.format, percent formatting) "
            "are counted as unresolved rather than matched, so a computed route is outside this arm "
            "by construction and is published as a volume, not as a zero",
            "'carries a counted row key' is a file-level fact (the key appears as a string constant "
            "or as a literal subscript key), so it says the key is present in the module and says "
            "nothing about whether the spelling reaches the same dict object",
            "consumer classes are read from the call name that the string is an argument of, up to 8 "
            "hops of assignment; a string consumed by a callee that the walk cannot name is published "
            "as no_call, which is a limit and not a zero",
            "face constants are the upper-case module-level names containing FACE or LATEST that are "
            "assigned string literals; a face assigned through an expression is not spellable here "
            "and is published by E647's face_constants_unmeasured, not by this study",
            "the read population is E638's join (one definition); a change to that join moves this "
            "study's speller set without touching its string census",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately as "
            "a hole",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts, volume)
    return m


def by_spelling_class(rows):
    """The deliverable's shape: for each spelling class, every module that names a target that way."""
    out = {}
    for row in rows:
        for cls in row["match_classes"]:
            out.setdefault(cls, []).append(row["module"])
    for cls in out:
        out[cls] = sorted(out[cls])
    return {cls: out[cls] for cls in sorted(out)}


def counts_of(rows):
    by_match, by_consumer, by_reach = {}, {}, {}
    mods_by_match, mods_by_consumer = {}, {}
    pairs = 0
    pairs_by_reach = {}
    with_key = with_key_and_loader = loader = keyed_no_loader = unconsumed_only = 0
    for row in rows:
        for cls in row["match_classes"]:
            mods_by_match[cls] = mods_by_match.get(cls, 0) + 1
        for cls in row["consumer_classes"]:
            mods_by_consumer[cls] = mods_by_consumer.get(cls, 0) + 1
        for cls, n in row["naming_by_match"].items():
            by_match[cls] = by_match.get(cls, 0) + n
        for cls, n in row["naming_by_consumer"].items():
            by_consumer[cls] = by_consumer.get(cls, 0) + n
        by_reach[row["reach"]] = by_reach.get(row["reach"], 0) + 1
        for rm, reach in row["read_module_reach"].items():
            pairs += 1
            pairs_by_reach[reach] = pairs_by_reach.get(reach, 0) + 1
        if row["carries_a_counted_row_key"]:
            with_key += 1
            if row["reach"] in LOADER_REACH:
                with_key_and_loader += 1
            elif row["reach"] == "string_not_consumed":
                keyed_no_loader += 1
        if row["reach"] in LOADER_REACH:
            loader += 1
        if row["reach"] == "string_not_consumed":
            unconsumed_only += 1
    return {
        "modules_naming_a_read_module": len(rows),
        "naming_literals": sum(r["naming_literal_count"] for r in rows),
        "literals_by_match_class": {k: by_match[k] for k in sorted(by_match)},
        "literals_by_consumer_class": {k: by_consumer[k] for k in sorted(by_consumer)},
        "modules_by_spelling_class": {k: mods_by_match[k] for k in sorted(mods_by_match)},
        "modules_by_consumer_class": {k: mods_by_consumer[k] for k in sorted(mods_by_consumer)},
        "modules_by_reach_class": {k: by_reach[k] for k in sorted(by_reach)},
        "modules_naming_by_an_import_or_loader_consumer": loader,
        "modules_naming_only_in_unconsumed_strings": unconsumed_only,
        "modules_naming_and_carrying_a_counted_key": with_key,
        "modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader": with_key_and_loader,
        "modules_naming_without_a_counted_key": len(rows) - with_key,
        "modules_carrying_a_key_but_naming_only_unconsumed_strings": keyed_no_loader,
        "speller_read_module_pairs": pairs,
        "speller_read_module_pairs_by_reach": {k: pairs_by_reach[k] for k in sorted(pairs_by_reach)},
        "module_class_histogram": _hist([r["module_class"] for r in rows]),
    }


def _hist(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return {k: out[k] for k in sorted(out)}


def decide(c):
    if not c.get("modules_naming_a_read_module"):
        return V_NO_SPELLER
    if c.get("modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader"):
        return V_KEY_AND_A_LOADER
    if c.get("modules_naming_by_an_import_or_loader_consumer"):
        return V_LOADER_BUT_NO_KEY
    if c.get("modules_naming_and_carrying_a_counted_key"):
        return V_KEY_BUT_NO_LOADER
    return V_NAME_ONLY


def answer_of(c, volume):
    return ("%d file(s), %d string(s) examined (%d expression-built); %d counted read line(s) in %d "
            "module(s) over %d key(s); %d file(s) spell a counted read module in %d literal(s), by "
            "class %s, consumed by %s; %d speller module(s) carry a counted row key of which %d also "
            "reach a read module through a loader-consumed string; the %d speller x read-module "
            "pair(s) split %s"
            % (volume["python_files_seen"], volume["string_literals_examined"],
               volume["unresolved_strings"], volume["counted_read_lines"],
               volume["counted_read_modules"], volume["counted_row_keys"],
               c["modules_naming_a_read_module"], c["naming_literals"],
               json.dumps(c["literals_by_match_class"], sort_keys=True),
               json.dumps(c["literals_by_consumer_class"], sort_keys=True),
               c["modules_naming_and_carrying_a_counted_key"],
               c["modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader"],
               c["speller_read_module_pairs"],
               json.dumps(c["speller_read_module_pairs_by_reach"], sort_keys=True)))


# ---------------------------------------------------------------- gate
def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "volume": m["volume"],
        "counts": m["counts"],
        "by_spelling_class": m["by_spelling_class"],
        "rows": m["rows"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "modules_naming_a_read_module", "naming_literals",
    "modules_naming_by_an_import_or_loader_consumer",
    "modules_naming_only_in_unconsumed_strings",
    "modules_naming_and_carrying_a_counted_key",
    "modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader",
    "modules_naming_without_a_counted_key",
    "modules_carrying_a_key_but_naming_only_unconsumed_strings",
    "speller_read_module_pairs",
)


def live_counts(rows):
    """The aggregates a reader can re-add from the rows alone."""
    return counts_of(rows)


def face_problems(face):
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    volume = face.get("volume") or {}
    live = live_counts(rows)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s is not the row-derived value (%r vs %r)"
                            % (key, c.get(key), live.get(key)))
    for key in ("literals_by_match_class", "literals_by_consumer_class",
                "modules_by_spelling_class", "modules_by_consumer_class",
                "modules_by_reach_class", "speller_read_module_pairs_by_reach",
                "module_class_histogram"):
        if (c.get(key) or {}) != (live.get(key) or {}):
            problems.append("counts.%s is not the aggregate its rows force" % key)
    if sum((c.get("literals_by_match_class") or {}).values()) != c.get("naming_literals"):
        problems.append("the match-class histogram does not add up to the naming literals")
    if sum((c.get("literals_by_consumer_class") or {}).values()) != c.get("naming_literals"):
        problems.append("the consumer-class histogram does not add up to the naming literals")
    if sum((c.get("modules_by_reach_class") or {}).values()) != len(rows):
        problems.append("the reach histogram does not add up to the spellers")
    if sum((c.get("speller_read_module_pairs_by_reach") or {}).values()) \
            != c.get("speller_read_module_pairs"):
        problems.append("the pair reach histogram does not add up to the pairs")
    expected_by_class = by_spelling_class(rows)
    if (face.get("by_spelling_class") or {}) != expected_by_class:
        problems.append("by_spelling_class is not the per-class roll-up of the rows")
    seen = volume.get("python_files_seen")
    scanned = volume.get("python_files_scanned")
    holes = volume.get("holes") or {}
    if isinstance(seen, int) and isinstance(scanned, int) \
            and scanned + sum(holes.values()) != seen:
        problems.append("scanned + holes != seen (%r + %r != %r)"
                        % (scanned, sum(holes.values()), seen))
    for row in rows:
        if row.get("naming_literal_count") != sum((row.get("naming_by_match") or {}).values()):
            problems.append("module %r publishes a literal count its own histogram does not force"
                            % row.get("module"))
            break
        if row.get("naming_literal_count") != sum((row.get("naming_by_consumer") or {}).values()):
            problems.append("module %r publishes a consumer split that does not add up"
                            % row.get("module"))
            break
        if len(row.get("naming_literals") or []) + (row.get("naming_literals_elided") or 0) \
                != row.get("naming_literal_count"):
            problems.append("module %r publishes %d example(s) + %r elided for %r literal(s)"
                            % (row.get("module"), len(row.get("naming_literals") or []),
                               row.get("naming_literals_elided"), row.get("naming_literal_count")))
            break
        recomputed = {rm: reach_from_consumers({n["consumer_class"]
                                               for n in (row.get("naming_literals") or [])
                                               if n.get("read_module") == rm})
                      for rm in (row.get("read_modules") or [])}
        if any(row.get("naming_literals_elided") or 0 for _ in [0]):
            continue
        if recomputed != (row.get("read_module_reach") or {}):
            problems.append("module %r publishes a reach its own literals do not force"
                            % row.get("module"))
            break
    if decide(c) != face.get("verdict"):
        problems.append("the published verdict is not the one its own counts force")
    if face.get("verdict") == V_NO_SPELLER and rows:
        problems.append("the no-speller verdict is not the one its own rows force")
    if face.get("verdict") == V_KEY_AND_A_LOADER \
            and not c.get("modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader"):
        problems.append("the key-and-loader verdict is not the one its own counts force")
    for cls in (c.get("modules_by_spelling_class") or {}):
        if cls not in MATCH_ORDER:
            problems.append("a spelling class outside the frozen vocabulary was published: %r" % cls)
            break
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = face_from(measure(root))
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    v = doc["volume"]
    say("run: files=%d scanned=%d holes=%s spellers=%d literals=%d with_key=%d strict=%d"
        % (v["python_files_seen"], v["python_files_scanned"], json.dumps(v["holes"], sort_keys=True),
           c["modules_naming_a_read_module"], c["naming_literals"],
           c["modules_naming_and_carrying_a_counted_key"],
           c["modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _fixture_root(files):
    import tempfile
    root = tempfile.mkdtemp(prefix="e652_")
    for name, body in files.items():
        path = os.path.join(root, name)
        os.makedirs(os.path.dirname(path) or root, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root


def _counted(module="scripts/target_mod.py", key="verdict"):
    return [{"module": module, "line": 1, "function": "f", "key": key, "receiver": "R"}]


TARGET_BODY = ('FACE = "targetface.json"\n'
               'LATEST = "targetlatest.json"\n'
               'def run():\n'
               '    R = {}\n'
               '    return R["verdict"]\n')


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
            say("PASS :: " + name)
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL :: %s :: %s" % (name, exc))

    def an_import_string_naming_the_stem_is_an_import_route():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nm = importlib.import_module("target_mod")\n'})
        m = measure(root, counted=_counted())
        row = m["rows"][0]
        assert row["module"] == "scripts/a.py", row["module"]
        assert row["read_module_reach"] == {"scripts/target_mod.py": "import_string_reach"}, row
        assert m["counts"]["modules_naming_by_an_import_or_loader_consumer"] == 1, m["counts"]

    def a_face_constant_is_its_own_spelling_class():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'def f():\n    return open("targetface.json")\n'})
        m = measure(root, counted=_counted())
        row = m["rows"][0]
        assert row["match_classes"] == ["exact_face"], row["match_classes"]
        assert row["read_module_reach"] == {"scripts/target_mod.py": "file_text_or_face_read"}, row

    def a_name_with_a_digit_suffix_is_not_a_token_match():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'x = "target_mod2"\n'})
        m = measure(root, counted=_counted())
        assert m["rows"] == [], m["rows"]

    def a_whole_token_inside_a_longer_name_is_a_match():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'x = "target_mod.json"\n'})
        m = measure(root, counted=_counted())
        assert m["rows"][0]["match_classes"] == ["token_contains_stem"], m["rows"][0]

    def an_unconsumed_spelling_is_its_own_reach():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'NOTE = "target_mod"\n'})
        m = measure(root, counted=_counted())
        row = m["rows"][0]
        assert row["reach"] == "string_not_consumed", row
        assert m["counts"]["modules_naming_only_in_unconsumed_strings"] == 1, m["counts"]

    def the_key_cross_tab_separates_spellers_from_holders():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/with_key.py": 'import importlib\nK = {"verdict": 1}\n'
                                                     'm = importlib.import_module("target_mod")\n',
                              "scripts/without_key.py": 'import importlib\n'
                                                        'm = importlib.import_module("target_mod")\n'})
        m = measure(root, counted=_counted())
        c = m["counts"]
        assert c["modules_naming_a_read_module"] == 2, c
        assert c["modules_naming_and_carrying_a_counted_key"] == 1, c
        assert c["modules_naming_and_carrying_a_counted_key_and_reached_by_a_loader"] == 1, c
        assert c["modules_naming_without_a_counted_key"] == 1, c
        assert m["verdict"] == V_KEY_AND_A_LOADER, m["verdict"]

    def a_computed_spelling_is_not_matched_and_is_published_as_a_volume():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'name = "x"\n'
                                              'x = "{}.json".format(name)\n'
                                              'y = "target" + "_mod"\n'})
        m = measure(root, counted=_counted())
        row = m["rows"][0]
        assert m["volume"]["unresolved_strings"] == 1, m["volume"]
        # the format site contributes nothing; only the folded concatenation names the target
        assert row["match_classes"] == ["exact_stem"], row
        assert row["naming_literal_count"] == 1, row
        assert row["naming_literals"][0]["built"] == "constant_concatenation", row

    def a_read_module_spelling_itself_is_not_a_route():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY})
        m = measure(root, counted=_counted())
        assert m["rows"] == [], m["rows"]
        assert m["volume"]["self_spellings_excluded"] >= 2, m["volume"]
        assert m["verdict"] == V_NO_SPELLER, m["verdict"]

    def a_file_that_does_not_parse_is_a_hole_and_the_holes_close():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/bad.py": "def (:\n"})
        m = measure(root, counted=_counted())
        v = m["volume"]
        assert v["holes"]["does_not_parse"] == 1, v
        assert v["python_files_scanned"] + sum(v["holes"].values()) == v["python_files_seen"], v

    def the_zero_class_is_a_verdict_not_an_empty_face():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": "x = 1\n"})
        m = measure(root, counted=_counted())
        assert m["verdict"] == V_NO_SPELLER, m["verdict"]
        assert m["rows"] == [], m["rows"]

    def a_loader_route_without_the_key_is_not_the_strict_verdict():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\n'
                                              'm = importlib.import_module("target_mod")\n'})
        m = measure(root, counted=_counted())
        assert m["verdict"] == V_LOADER_BUT_NO_KEY, m["verdict"]

    def a_key_without_a_loader_route_is_not_the_strict_verdict():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'K = {"verdict": 1}\nNOTE = "target_mod"\n'})
        m = measure(root, counted=_counted())
        assert m["verdict"] == V_KEY_BUT_NO_LOADER, m["verdict"]

    def the_face_re_adds_from_its_own_rows():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nK = {"verdict": 1}\n'
                                              'm = importlib.import_module("target_mod")\n'})
        m = measure(root, counted=_counted())
        doc = face_from(m)
        assert face_problems(doc) == [], face_problems(doc)

    def a_tampered_count_is_refused():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nK = {"verdict": 1}\n'
                                              'm = importlib.import_module("target_mod")\n'})
        doc = face_from(measure(root, counted=_counted()))
        doc["counts"]["modules_naming_a_read_module"] = 7
        assert any("modules_naming_a_read_module" in p for p in face_problems(doc)), \
            face_problems(doc)

    def a_tampered_verdict_is_refused():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nK = {"verdict": 1}\n'
                                              'm = importlib.import_module("target_mod")\n'})
        doc = face_from(measure(root, counted=_counted()))
        doc["verdict"] = V_NAME_ONLY
        assert any("verdict" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_spelling_class_rollup_is_refused():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nm = importlib.import_module("target_mod")\n'})
        doc = face_from(measure(root, counted=_counted()))
        doc["by_spelling_class"] = {"exact_path": ["scripts/a.py"]}
        assert any("by_spelling_class" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_literal_count_is_refused():
        root = _fixture_root({"scripts/target_mod.py": TARGET_BODY,
                              "scripts/a.py": 'import importlib\nm = importlib.import_module("target_mod")\n'})
        doc = face_from(measure(root, counted=_counted()))
        doc["rows"][0]["naming_literal_count"] = 9
        assert any("literal" in p for p in face_problems(doc)), face_problems(doc)

    leg("an import string naming the stem is an import route",
        an_import_string_naming_the_stem_is_an_import_route)
    leg("a face constant is its own spelling class", a_face_constant_is_its_own_spelling_class)
    leg("a name with a digit suffix is not a token match",
        a_name_with_a_digit_suffix_is_not_a_token_match)
    leg("a whole token inside a longer name is a match",
        a_whole_token_inside_a_longer_name_is_a_match)
    leg("an unconsumed spelling is its own reach", an_unconsumed_spelling_is_its_own_reach)
    leg("the key cross-tab separates spellers from holders",
        the_key_cross_tab_separates_spellers_from_holders)
    leg("a computed spelling is published as a volume, not matched",
        a_computed_spelling_is_not_matched_and_is_published_as_a_volume)
    leg("a read module spelling itself is not a route",
        a_read_module_spelling_itself_is_not_a_route)
    leg("a file that does not parse is a hole and the holes close",
        a_file_that_does_not_parse_is_a_hole_and_the_holes_close)
    leg("the zero class is a verdict, not an empty face",
        the_zero_class_is_a_verdict_not_an_empty_face)
    leg("a loader route without the key is not the strict verdict",
        a_loader_route_without_the_key_is_not_the_strict_verdict)
    leg("a key without a loader route is not the strict verdict",
        a_key_without_a_loader_route_is_not_the_strict_verdict)
    leg("the face re-adds from its own rows", the_face_re_adds_from_its_own_rows)
    leg("a tampered count is refused", a_tampered_count_is_refused)
    leg("a tampered verdict is refused", a_tampered_verdict_is_refused)
    leg("a tampered spelling-class roll-up is refused", a_tampered_spelling_class_rollup_is_refused)
    leg("a tampered literal count is refused", a_tampered_literal_count_is_refused)
    failed = [n for n, okd in legs if not okd]
    say("selftest: %d/%d green" % (len(legs) - len(failed), len(legs)))
    if failed:
        say("selftest: failing legs -> " + "; ".join(failed))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
