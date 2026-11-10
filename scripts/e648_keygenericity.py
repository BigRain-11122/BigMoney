"""E648 -- how common are the six counted row keys corpus-wide, so a key-name hit can be priced?

E642 and E646 both rest on literal key-name equality over six keys ('verdict', 'rows', 'days',
'bar', 'x1', 'slip_exec') that are ordinary English words.  E207/E208 say a name is not a
measurement, and E646 had to classify seven hits one by one.  Every later hit/no-hit reading of
the key-name arm needs a base rate: if 'rows' names 400 files, then one collision means nothing;
if 'slip_exec' names two, one collision is the whole population.

This study publishes, per counted key, with no lineage test at all:

  * the files that spell it as a literal string anywhere (a Python string constant), split into
    the three ways a literal can appear -- a subscript key, a dict-literal key, and everything
    else (docstring prose, log messages, path fragments);
  * the read sites (Subscript in Load context), write sites (Store) and delete sites (Del) whose
    key is that literal, and the leftmost Name of each site's container, because `D["rows"]` is a
    statement about D as well as about 'rows';
  * the counted read lines themselves (E638's join), marked inside that population, so the hit
    that any later study tests can be read against its own denominator;
  * one class per key -- private to the counted faces / shared but narrow / generic word -- using
    two floors frozen before the run.

Nothing here re-reads E642's or E646's rows: the population is re-derived from the tree with the
same corpus rule, and their published figures are carried only as reconciliation numbers.
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
FACE = "KEYGENERICITY.json"
LATEST = "keygenericity_latest.json"
STUDY = "E648_keygenericity"
SELF_PARTS = ("e648_", "run_e648_", "_probe_e648", "_r1665")
SOURCE_FACE = "results/state_tilt/MODULEWRITEKEY.json"
MAX_BYTES = 1024 * 1024          # E391's read cap, carried so both studies skip the same files
TOP_ROOTS = 12                   # receiver roots published per key; the tail is summed, never dropped
MAX_EXAMPLES = 25

# ---- frozen before the run (a key that clears these is a word, not a private face) -----------
GENERIC_FLOOR_FILES = 20         # >= 20 files outside the counted faces spell it -> generic word
NARROW_FLOOR_FILES = 1           # 1..19 files outside the counted faces -> shared but narrow

import e642_module_write_key as e642  # noqa: E402
import e646_crossmodule_key as e646  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402

CLASS_PRIVATE = "private_to_the_counted_faces"
CLASS_NARROW = "narrow_shared"
CLASS_GENERIC = "generic_word"
CLASSES = (CLASS_PRIVATE, CLASS_NARROW, CLASS_GENERIC)

V_EVERY_KEY_IS_A_WORD = (
    "every counted row key is spelled as a literal in at least %d files outside the faces that "
    "hold the counted reads, so a bare key-name hit carries no lineage information at all" %
    GENERIC_FLOOR_FILES)
V_NO_KEY_IS_A_WORD = (
    "no counted row key is spelled anywhere outside the counted faces, so the key name alone is a "
    "private address and a hit anywhere else would be lineage")
V_SOME_KEYS_ARE_WORDS = (
    "the six counted row keys price differently: at least one is a generic word and at least one is "
    "private or narrow, so a key-name hit has to be priced per key rather than over the set")
V_NO_COUNTED_KEYS = (
    "the join publishes no counted row key, so there is no key name to price and the question does "
    "not apply")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def corpus(root=ROOT):
    """The corpus E642 walks, minus this study's own files (E180/E207: a census never counts itself)."""
    out = []
    for p in e642.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def read_population(root=ROOT):
    """E638's counted read lines, normalised -- the denominator every class is priced against."""
    out = []
    for r in e638.join_counted_lines(root):
        out.append({
            "module": (r.get("module") or "").replace("\\", "/"),
            "line": r.get("read_line"),
            "function": r.get("function"),
            "key": r.get("key"),
            "receiver": r.get("receiver"),
        })
    out.sort(key=lambda x: (x["module"], x["line"] or 0, x["key"] or ""))
    return out


def _parents(tree):
    out = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            out[child] = parent
    return out


def _enclosing_function(node, parents):
    cur = parents.get(node)
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
        cur = parents.get(cur)
    return None


def _unparse(node):
    try:
        return ast.unparse(node)
    except Exception:                                          # pragma: no cover - old parsers
        return None


def _literal_key(node):
    """The literal string a Subscript is keyed by, or None for a computed subscript."""
    sl = node.slice
    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
        return sl.value
    return None


def file_profile(path, keys):
    """(payload, None) or (None, why): the three literal faces plus the subscript sites of one file."""
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
    parents = _parents(tree)
    prof = {
        "literal_string_occurrences": {},     # any string constant spelled as the key
        "subscript_key_sites": 0,             # literal key on a Subscript, any context
        "dict_key_literal_sites": 0,          # literal key as a dict literal's key
        "read_sites": [],
        "write_sites": [],
        "delete_sites": [],
        "computed_subscripts": 0,             # named for completeness, never counted as a hit
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            key = _literal_key(node)
            if key is None:
                prof["computed_subscripts"] += 1
                continue
            if key not in keys:
                continue
            prof["subscript_key_sites"] += 1
            rec = {
                "key": key,
                "line": node.lineno,
                "column": node.col_offset,
                "function": _enclosing_function(node, parents),
                "receiver_root": e646.root_name_of(node.value),
                "container": _unparse(node.value),
            }
            ctx = type(node.ctx).__name__
            if ctx == "Load":
                prof["read_sites"].append(rec)
            elif ctx == "Store":
                prof["write_sites"].append(rec)
            elif ctx == "Del":
                prof["delete_sites"].append(rec)
        elif isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and k.value in keys:
                    prof["dict_key_literal_sites"] += 1
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in keys:
            prof["literal_string_occurrences"][node.value] = (
                prof["literal_string_occurrences"].get(node.value, 0) + 1)
    return prof, None


def measure(root=ROOT, counted=None):
    counted = read_population(root) if counted is None else counted
    keys = sorted({r.get("key") for r in counted if r.get("key")})
    counted_modules = {r.get("module") for r in counted if r.get("module")}
    files = corpus(root)

    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    per_key = {k: {"files_naming_it": 0, "files_outside_the_counted_faces": 0,
                   "literal_string_occurrences": 0, "subscript_key_sites": 0,
                   "dict_key_literal_sites": 0, "read_sites": 0, "write_sites": 0,
                   "delete_sites": 0, "files_with_a_read_site": 0,
                   "roots": {}} for k in keys}
    computed = 0
    files_naming_any_key = 0
    examples = []

    for p in files:
        prof, why = file_profile(p, set(keys))
        if prof is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        computed += prof["computed_subscripts"]
        module = rel(p, root)
        named_here = set(prof["literal_string_occurrences"])
        for site in prof["read_sites"] + prof["write_sites"] + prof["delete_sites"]:
            named_here.add(site["key"])
        if named_here:
            files_naming_any_key += 1
        for k in named_here:
            rec = per_key.get(k)
            if rec is None:
                continue
            rec["files_naming_it"] += 1
            if module not in counted_modules:
                rec["files_outside_the_counted_faces"] += 1
        for k, n in prof["literal_string_occurrences"].items():
            if k in per_key:
                per_key[k]["literal_string_occurrences"] += n
        for kind, bucket in (("read_sites", "read_sites"), ("write_sites", "write_sites"),
                             ("delete_sites", "delete_sites")):
            for site in prof[kind]:
                rec = per_key.get(site["key"])
                if rec is None:
                    continue
                rec[bucket] += 1
                root_name = site["receiver_root"]
                rec["roots"][root_name] = rec["roots"].get(root_name, 0) + 1
                if kind == "read_sites":
                    if len(examples) < MAX_EXAMPLES * 4:
                        examples.append({"module": module, "line": site["line"],
                                         "key": site["key"],
                                         "receiver_root": site["receiver_root"],
                                         "function": site["function"]})
        for k in per_key:
            if any(s["key"] == k for s in prof["read_sites"]):
                per_key[k]["files_with_a_read_site"] += 1
        per_key_key_list = set(keys)
        # dict-literal keys are counted per file by the profile; attribute them where unique
        if prof["dict_key_literal_sites"]:
            _spread_dict_keys(prof, per_key, per_key_key_list)

    rows = []
    for k in keys:
        rec = per_key[k]
        roots = rec.pop("roots")
        top = sorted(roots.items(), key=lambda x: (-x[1], x[0] or ""))
        published_roots = [{"root": r, "read_and_write_sites": n} for r, n in top[:TOP_ROOTS]]
        tail = top[TOP_ROOTS:]
        rec = dict(rec)
        rec["subscript_key_sites"] = (rec["read_sites"] + rec["write_sites"]
                                      + rec["delete_sites"])
        rec["literal_string_occurrences"] = max(rec["literal_string_occurrences"],
                                                rec["subscript_key_sites"])
        rec["prose_or_other_strings"] = max(
            0, rec["literal_string_occurrences"] - rec["subscript_key_sites"]
            - rec["dict_key_literal_sites"])
        row = {
            "key": k,
            "files_naming_it": rec["files_naming_it"],
            "files_outside_the_counted_faces": rec["files_outside_the_counted_faces"],
            "literal_string_occurrences": rec["literal_string_occurrences"],
            "subscript_key_sites": rec["subscript_key_sites"],
            "read_sites": rec["read_sites"],
            "write_sites": rec["write_sites"],
            "delete_sites": rec["delete_sites"],
            "dict_key_literal_sites": rec["dict_key_literal_sites"],
            "prose_or_other_strings": rec["prose_or_other_strings"],
            "files_with_a_read_site": rec["files_with_a_read_site"],
            "distinct_receiver_roots": len(roots),
            "receiver_roots": published_roots,
            "receiver_root_tail_sites": sum(n for _, n in tail),
            "counted_read_lines": [c for c in counted if c.get("key") == k],
        }
        row["key_class"] = classify_key(row)
        row["base_rate_note"] = (
            "one key-name hit for %r competes with %d file(s) that spell it outside the counted "
            "faces and %d read site(s) corpus-wide"
            % (k, row["files_outside_the_counted_faces"], row["read_sites"]))
        rows.append(row)

    counts = counts_of(rows, len(files), holes, counted, computed, files_naming_any_key)
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every Python file of E642's corpus, and per counted row key publish "
                   "three literal faces (subscript key / dict-literal key / other strings), the "
                   "read/write/delete sites keyed by that literal with each site's leftmost "
                   "container name, and the corpus-wide file count outside the faces holding the "
                   "counted reads"),
        "population_source": ("%d Python files of the corpus E640/E642 walk, of which %d spell at "
                              "least one counted row key; %d counted read lines in %d module(s)"
                              % (len(files), files_naming_any_key, len(counted),
                                 len(counted_modules))),
        "floors": {"generic_floor_files": GENERIC_FLOOR_FILES,
                   "narrow_floor_files": NARROW_FLOOR_FILES},
        "counts": counts,
        "rows": rows,
        "examples": examples[:MAX_EXAMPLES],
        "limits": [
            "a literal string is not an access: the 'files naming it' column counts spellings, so "
            "a docstring line that says 'verdict' raises the base rate without any code reading a key",
            "the subscript arm matches only a string-literal slice; a computed key (k = 'verdict'; "
            "D[k]) is invisible to it by construction and is counted separately as "
            "computed_subscripts rather than folded into the zero",
            "the class is a base rate, not a lineage test: generic_word says a hit needs lineage "
            "evidence before it means anything, not that any particular hit is a collision",
            "files over 1MB are skipped and counted as a hole (E391's cap), so a very large module "
            "that spells a key is absent from its denominator while present in any consumer that "
            "reads the file directly",
            "the receiver root is the leftmost Name of the container, so `self.report['rows']` is "
            "published under 'self' and two different objects under one name share a row",
            "the counted read lines are the ones E638's join publishes; a key spelled in a module "
            "that holds no counted read is counted in files_naming_it only",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(rows, counts)
    return m


def _spread_dict_keys(prof, per_key, keys):
    """Attribute dict-literal key counts to the keys the profile spells (all of them, per file)."""
    for k in keys:
        if k in prof["literal_string_occurrences"]:
            per_key[k]["dict_key_literal_sites"] += 1 if prof["dict_key_literal_sites"] else 0


def classify_key(row):
    if row["files_outside_the_counted_faces"] <= 0:
        return CLASS_PRIVATE
    if row["files_outside_the_counted_faces"] >= GENERIC_FLOOR_FILES:
        return CLASS_GENERIC
    return CLASS_NARROW


def counts_of(rows, files_scanned, holes, counted, computed, files_naming_any_key):
    hist = {c: 0 for c in CLASSES}
    for r in rows:
        hist[r["key_class"]] = hist.get(r["key_class"], 0) + 1
    holes_total = sum(holes.values())
    return {
        "python_files_seen": files_scanned,
        "python_files_scanned": files_scanned - holes_total,
        "holes": dict(holes),
        "files_naming_any_counted_row_key": files_naming_any_key,
        "counted_read_lines": len(counted),
        "counted_row_keys": len(rows),
        "counted_modules": len({c.get("module") for c in counted if c.get("module")}),
        "literal_string_occurrences": sum(r["literal_string_occurrences"] for r in rows),
        "subscript_key_sites": sum(r["subscript_key_sites"] for r in rows),
        "read_sites": sum(r["read_sites"] for r in rows),
        "write_sites": sum(r["write_sites"] for r in rows),
        "delete_sites": sum(r["delete_sites"] for r in rows),
        "dict_key_literal_sites": sum(r["dict_key_literal_sites"] for r in rows),
        "computed_subscripts": computed,
        "distinct_receiver_roots": len({x["root"] for r in rows for x in r["receiver_roots"]}),
        "key_class_histogram": hist,
        "keys_whose_read_sites_all_sit_in_counted_modules": sum(
            1 for r in rows
            if r["read_sites"] and r["files_outside_the_counted_faces"] == 0),
        "floor_generic": GENERIC_FLOOR_FILES,
        "floor_narrow": NARROW_FLOOR_FILES,
    }


def decide(c):
    keys = c.get("counted_row_keys") or 0
    if not keys:
        return V_NO_COUNTED_KEYS
    hist = c.get("key_class_histogram") or {}
    generic = hist.get(CLASS_GENERIC, 0)
    private_or_narrow = hist.get(CLASS_PRIVATE, 0) + hist.get(CLASS_NARROW, 0)
    if generic == keys:
        return V_EVERY_KEY_IS_A_WORD
    if private_or_narrow == keys:
        return V_NO_KEY_IS_A_WORD
    return V_SOME_KEYS_ARE_WORDS


def answer_of(rows, c):
    if not rows:
        return V_NO_COUNTED_KEYS
    ranked = sorted(rows, key=lambda r: (-r["files_outside_the_counted_faces"], r["key"]))
    widest = ranked[0]
    narrowest = ranked[-1]
    hist = c.get("key_class_histogram") or {}
    return (
        "%d of %d counted row keys are generic words (>=%d files outside the counted faces), %d "
        "are shared but narrow, %d are private to the counted faces. The widest is %r (%d files, "
        "%d read sites) and the narrowest is %r (%d files, %d read sites), so a single key-name "
        "hit is worth most on %r and least on %r."
        % (hist.get(CLASS_GENERIC, 0), len(rows), GENERIC_FLOOR_FILES,
           hist.get(CLASS_NARROW, 0), hist.get(CLASS_PRIVATE, 0),
           widest["key"], widest["files_outside_the_counted_faces"], widest["read_sites"],
           narrowest["key"], narrowest["files_outside_the_counted_faces"],
           narrowest["read_sites"], narrowest["key"], widest["key"]))


def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "floors": m["floors"],
        "counts": m["counts"],
        "rows": m["rows"],
        "examples": m["examples"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "python_files_seen", "python_files_scanned",
    "files_naming_any_counted_row_key", "counted_read_lines",
    "counted_row_keys", "counted_modules", "literal_string_occurrences", "subscript_key_sites",
    "read_sites", "write_sites", "delete_sites", "dict_key_literal_sites", "computed_subscripts",
    "distinct_receiver_roots", "keys_whose_read_sites_all_sit_in_counted_modules",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    live = {
        "files_naming_any_counted_row_key": c.get("files_naming_any_counted_row_key"),
        "counted_read_lines": len([x for r in rows for x in (r.get("counted_read_lines") or [])]),
        "counted_row_keys": len(rows),
        "counted_modules": len({x.get("module") for r in rows
                                for x in (r.get("counted_read_lines") or []) if x.get("module")}),
        "literal_string_occurrences": sum(r.get("literal_string_occurrences") or 0 for r in rows),
        "subscript_key_sites": sum(r.get("subscript_key_sites") or 0 for r in rows),
        "read_sites": sum(r.get("read_sites") or 0 for r in rows),
        "write_sites": sum(r.get("write_sites") or 0 for r in rows),
        "delete_sites": sum(r.get("delete_sites") or 0 for r in rows),
        "dict_key_literal_sites": sum(r.get("dict_key_literal_sites") or 0 for r in rows),
        "distinct_receiver_roots": len({x.get("root") for r in rows
                                        for x in (r.get("receiver_roots") or [])}),
        "keys_whose_read_sites_all_sit_in_counted_modules": sum(
            1 for r in rows if (r.get("read_sites") or 0)
            and (r.get("files_outside_the_counted_faces") or 0) == 0),
    }
    for key in COUNT_KEYS:
        if key in ("files_naming_any_counted_row_key", "computed_subscripts",
                   "python_files_seen", "python_files_scanned"):
            continue
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows (%r vs %r)"
                            % (key, c.get(key), live.get(key)))
    holes = c.get("holes") or {}
    if (c.get("python_files_scanned") or 0) + sum(holes.values()) != (c.get("python_files_seen") or 0):
        problems.append("scanned + holes != seen (%r + %r != %r)"
                        % (c.get("python_files_scanned"), sum(holes.values()),
                           c.get("python_files_seen")))
    for r in rows:
        subs = (r.get("read_sites") or 0) + (r.get("write_sites") or 0) + (r.get("delete_sites") or 0)
        if r.get("subscript_key_sites") != subs:
            problems.append("key %r publishes %r subscript sites for %d sites"
                            % (r.get("key"), r.get("subscript_key_sites"), subs))
            break
        if (r.get("literal_string_occurrences") or 0) < subs:
            problems.append("key %r spells fewer strings than it has subscript sites" % r.get("key"))
            break
        if (r.get("prose_or_other_strings") or 0) < 0:
            problems.append("key %r publishes a negative prose remainder" % r.get("key"))
            break
        if r.get("key_class") != classify_key(r):
            problems.append("key %r is classed %r but its own file count forces %r"
                            % (r.get("key"), r.get("key_class"), classify_key(r)))
            break
    hist = c.get("key_class_histogram") or {}
    if sum(hist.values()) != len(rows):
        problems.append("the class histogram is not the per-key count")
    if c.get("floor_generic") != GENERIC_FLOOR_FILES or c.get("floor_narrow") != NARROW_FLOOR_FILES:
        problems.append("the published floors are not the frozen ones")
    if decide(c) != face.get("verdict"):
        problems.append("the published verdict is not the one its own counts force")
    if face.get("verdict") == V_EVERY_KEY_IS_A_WORD \
            and hist.get(CLASS_GENERIC, 0) != len(rows):
        problems.append("the every-key-is-a-word verdict is not the one the class histogram forces")
    if face.get("verdict") == V_NO_KEY_IS_A_WORD \
            and hist.get(CLASS_PRIVATE, 0) + hist.get(CLASS_NARROW, 0) != len(rows):
        problems.append("the no-key-is-a-word verdict is not the one the class histogram forces")
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
    say("run: files=%d keys=%d reads=%d spells=%d dict_keys=%d roots=%d classes=%s"
        % (c["python_files_scanned"], c["counted_row_keys"], c["read_sites"],
           c["literal_string_occurrences"], c["dict_key_literal_sites"],
           c["distinct_receiver_roots"], json.dumps(c["key_class_histogram"], sort_keys=True)))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _fixture_root(files):
    """A throwaway corpus; keys default to the counted set the tests inject."""
    import tempfile
    root = tempfile.mkdtemp(prefix="e648_")
    for name, body in files.items():
        path = os.path.join(root, name)
        os.makedirs(os.path.dirname(path) or root, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root


def _fixture_path(body, name="a.py"):
    """One throwaway file, returned by path (E648 owns its fixtures, not its siblings')."""
    return os.path.join(_fixture_root({name: body}), name)


def _counted(module="a.py", line=1, key="verdict"):
    return [{"module": module, "line": line, "function": "f", "key": key, "receiver": "R"}]


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

    def a_literal_subscript_read_is_counted_with_its_root():
        prof, why = file_profile(_fixture_path("R = {}\nx = R['verdict']\n"), {"verdict"})
        assert why is None, why
        assert len(prof["read_sites"]) == 1, prof
        assert prof["read_sites"][0]["receiver_root"] == "R", prof
        assert prof["read_sites"][0]["function"] is None, prof

    def a_computed_subscript_names_nothing():
        prof, why = file_profile(
            _fixture_path("R = {}\nk = 'verdict'\nx = R[k]\n"), {"verdict"})
        assert why is None, why
        assert prof["read_sites"] == [], prof
        assert prof["computed_subscripts"] == 1, prof

    def write_and_delete_are_not_reads():
        prof, why = file_profile(
            _fixture_path("R = {}\nR['verdict'] = 1\ndel R['verdict']\n"), {"verdict"})
        assert why is None, why
        assert prof["read_sites"] == [], prof
        assert len(prof["write_sites"]) == 1 and len(prof["delete_sites"]) == 1, prof

    def a_dict_literal_key_is_its_own_face():
        prof, why = file_profile(_fixture_path("D = {'verdict': 1}\n"), {"verdict"})
        assert why is None, why
        assert prof["dict_key_literal_sites"] == 1, prof
        assert prof["read_sites"] == [] and prof["write_sites"] == [], prof
        assert prof["literal_string_occurrences"]["verdict"] == 1, prof

    def prose_remainder_never_goes_negative():
        prof, why = file_profile(
            _fixture_path('"""a verdict here"""\nR = {}\nR["verdict"] = 1\n'), {"verdict"})
        assert why is None, why
        row = {"key": "verdict", "read_sites": 0, "write_sites": 1, "delete_sites": 0,
               "subscript_key_sites": 1, "dict_key_literal_sites": 0,
               "literal_string_occurrences": max(prof["literal_string_occurrences"]["verdict"], 1),
               "files_outside_the_counted_faces": 1}
        rem = row["literal_string_occurrences"] - row["subscript_key_sites"] \
            - row["dict_key_literal_sites"]
        assert rem >= 0, row

    def a_file_that_does_not_parse_is_a_hole():
        root = _fixture_root({"a.py": "R = {}\nx = R['verdict']\n", "bad.py": "def (:\n"})
        try:
            m = measure(root, counted=_counted())
            assert m["counts"]["holes"]["does_not_parse"] == 1, m["counts"]["holes"]
            assert m["counts"]["python_files_scanned"] == 1, m["counts"]
        finally:
            pass

    def a_key_absent_from_the_tree_still_publishes_a_row():
        root = _fixture_root({"a.py": "R = {}\nx = R['verdict']\n"})
        m = measure(root, counted=_counted() + [
            {"module": "a.py", "line": 1, "function": "f", "key": "slip_exec", "receiver": "R"}])
        keys = {r["key"]: r for r in m["rows"]}
        assert "slip_exec" in keys, keys
        assert keys["slip_exec"]["files_naming_it"] == 0, keys["slip_exec"]
        assert keys["slip_exec"]["key_class"] == CLASS_PRIVATE, keys["slip_exec"]

    def a_key_naming_only_the_counted_module_is_private():
        root = _fixture_root({"a.py": "R = {}\nx = R['verdict']\n"})
        m = measure(root, counted=_counted())
        row = [r for r in m["rows"] if r["key"] == "verdict"][0]
        assert row["files_outside_the_counted_faces"] == 0, row
        assert row["key_class"] == CLASS_PRIVATE, row
        assert m["verdict"] == V_NO_KEY_IS_A_WORD, m["verdict"]

    def a_key_naming_many_files_outside_is_generic():
        files = {"a.py": "R = {}\nx = R['verdict']\n"}
        for i in range(GENERIC_FLOOR_FILES):
            files["m%02d.py" % i] = "D = {}\nD['verdict'] = %d\n" % i
        root = _fixture_root(files)
        m = measure(root, counted=_counted())
        row = [r for r in m["rows"] if r["key"] == "verdict"][0]
        assert row["files_outside_the_counted_faces"] >= GENERIC_FLOOR_FILES, row
        assert row["key_class"] == CLASS_GENERIC, row
        assert m["verdict"] == V_EVERY_KEY_IS_A_WORD, m["verdict"]

    def a_mixed_set_is_its_own_verdict():
        files = {"a.py": "R = {}\nx = R['verdict']\nD = {}\ny = D['slip_exec']\n"}
        for i in range(GENERIC_FLOOR_FILES):
            files["m%02d.py" % i] = "E = {}\nE['verdict'] = %d\n" % i
        root = _fixture_root(files)
        m = measure(root, counted=_counted() + [
            {"module": "a.py", "line": 1, "function": "f", "key": "slip_exec", "receiver": "D"}])
        assert m["verdict"] == V_SOME_KEYS_ARE_WORDS, (m["verdict"], m["counts"])
        assert m["counts"]["key_class_histogram"][CLASS_GENERIC] == 1, m["counts"]

    def a_site_inside_a_function_reports_it():
        prof, why = file_profile(
            _fixture_path("R = {}\ndef g():\n    return R['verdict']\n"), {"verdict"})
        assert why is None, why
        assert prof["read_sites"][0]["function"] == "g", prof

    def the_face_re_adds_from_its_own_rows():
        files = {"a.py": "R = {}\nx = R['verdict']\ny = R['rows']\nD = {'verdict': 1}\n"}
        root = _fixture_root(files)
        two_keys = _counted() + [
            {"module": "a.py", "line": 2, "function": "f", "key": "rows", "receiver": "R"}]
        doc = face_from(measure(root, counted=two_keys))
        problems = face_problems(doc)
        assert not problems, problems
        assert doc["counts"]["read_sites"] == 2, doc["counts"]
        assert doc["counts"]["counted_row_keys"] == 2, doc["counts"]

    def a_tampered_class_is_refused():
        files = {"a.py": "R = {}\nx = R['verdict']\n"}
        root = _fixture_root(files)
        doc = face_from(measure(root, counted=_counted()))
        doc["rows"][0]["key_class"] = CLASS_GENERIC
        assert any("classed" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_verdict_is_refused():
        files = {"a.py": "R = {}\nx = R['verdict']\n"}
        root = _fixture_root(files)
        doc = face_from(measure(root, counted=_counted()))
        doc["verdict"] = V_EVERY_KEY_IS_A_WORD
        assert any("verdict" in p for p in face_problems(doc)), face_problems(doc)

    leg("a literal subscript read is counted with its root name", a_literal_subscript_read_is_counted_with_its_root)
    leg("a computed subscript names nothing", a_computed_subscript_names_nothing)
    leg("write and delete sites are not reads", write_and_delete_are_not_reads)
    leg("a dict-literal key is its own face", a_dict_literal_key_is_its_own_face)
    leg("the prose remainder never goes negative", prose_remainder_never_goes_negative)
    leg("a file that does not parse is a hole", a_file_that_does_not_parse_is_a_hole)
    leg("a key absent from the tree still publishes a row", a_key_absent_from_the_tree_still_publishes_a_row)
    leg("a key naming only the counted module is private", a_key_naming_only_the_counted_module_is_private)
    leg("a key naming many files outside is generic", a_key_naming_many_files_outside_is_generic)
    leg("a mixed set is its own verdict", a_mixed_set_is_its_own_verdict)
    leg("a site inside a function reports it", a_site_inside_a_function_reports_it)
    leg("the face re-adds from its own rows", the_face_re_adds_from_its_own_rows)
    leg("a tampered class is refused", a_tampered_class_is_refused)
    leg("a tampered verdict is refused", a_tampered_verdict_is_refused)
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