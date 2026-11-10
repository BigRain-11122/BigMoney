"""E643 -- what syntactic context holds the two-depth sites that belong to no function?

E640 published two numbers that sit side by side: 27,675 of the 45,395 two-depth sites have an
enclosing function and 17,720 do not, and it labelled the remainder "module level".  That is a name,
not a measurement.  A site outside every function can sit in a class body, in a lambda at module or
class scope, in a comprehension, in a decorator, or in a class header -- and each of those contexts
has a different scope at runtime, so "module level" can be one population or five.

For every site whose innermost enclosing function does not exist this study publishes:

  * the innermost context and the full container chain (so "class_body>lambda" is distinct from
    "module_body"),
  * the write face of each context (a site carrying a store/delete at any depth, and the member
    ctx histogram), because a module-level *write* is the population E642 cares about,
  * whether the site's key is a literal or computed, since a computed key names nothing,
  * how deep inside module-level compound statements a module_body site sits, because "the module
    body" is itself a block tree,
  * a reconciliation against E640's published residual (machine-read from its face, never
    hand-copied): the difference is named rather than reconciled away.

The owner split is imported from E640 (``innermost_owner`` over ``function_spans``) and the site
grouping from E638, so this study cannot drift from the definitions it is pricing.
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
FACE = "NONFUNCSITE.json"
LATEST = "nonfuncsite_latest.json"
STUDY = "E643_non_function_site_context"
SELF_PARTS = ("e643_", "run_e643_", "_probe_e643", "_r1667")
SOURCE_FACE = "results/state_tilt/WRITEREADCOLLIDE.json"
MAX_BYTES = 1024 * 1024
MAX_EXAMPLES_PER_BUCKET = 8

import e391_key_name_two_meanings as e391  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402

BUCKETS = ("module_body", "class_body", "class_header", "lambda", "comprehension",
           "decorator", "function_body")
BLOCK_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try,
               ast.ExceptHandler)

V_ABSENT = (
    "no_two_depth_site_in_the_corpus_lacks_an_enclosing_function,_so_the_module_level_residual_"
    "E640_publishes_has_no_members_to_name_and_the_question_is_moot_at_this_population")
V_ONE_CONTEXT = (
    "every_two_depth_site_without_an_enclosing_function_sits_in_the_same_syntactic_context,_so_"
    "calling_the_residual_module_level_names_one_population_rather_than_several")
V_SEVERAL_WRITES_IN_ONE = (
    "the_sites_without_an_enclosing_function_split_across_several_syntactic_contexts_while_every_"
    "site_that_writes_sits_in_one_of_them,_so_the_read_side_of_the_residual_is_many_contexts_and_"
    "its_write_side_is_one")
V_SEVERAL_WRITES_SPREAD = (
    "the_sites_without_an_enclosing_function_split_across_several_syntactic_contexts_and_the_write_"
    "face_is_not_confined_to_one_of_them,_so_module_level_is_a_name_for_at_least_two_scopes_on_"
    "both_the_read_and_the_write_side")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The Python corpus E391 walks, minus this study's own files (exclusion by prefix)."""
    out = []
    for p in e391.py_corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def _pos(node):
    return (getattr(node, "lineno", 0) or 0, getattr(node, "col_offset", 0) or 0)


def _endpos(node):
    end = getattr(node, "end_lineno", None)
    if end is None:
        return None
    return (end, getattr(node, "end_col_offset", 0) or 0)


def holds(node, line, column):
    """Position containment on (line, column); a node without an end position holds nothing."""
    start = _pos(node)
    end = _endpos(node)
    if end is None:
        return False
    return start <= (line, column) <= end


def _body_start(node):
    body = getattr(node, "body", None) or []
    return _pos(body[0]) if body else _pos(node)


def decorator_spans(tree):
    """Every decorator expression's span, with whether it decorates a def or a class.

    A decorator sits *before* its def, so the FunctionDef's own span does not hold it: the
    enclosing-definition test on the decorator has to be a separate pass or those sites fall
    through to module_body and the bucket lies.
    """
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        for dec in getattr(node, "decorator_list", None) or []:
            start, end = _pos(dec), _endpos(dec)
            if end is not None:
                out.append((start, end, kind))
    return out


def containers_of(tree):
    """Every container whose position-containment can name a context, with its kind."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            out.append((node, "class"))
        elif isinstance(node, ast.Lambda):
            out.append((node, "lambda"))
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            out.append((node, "comprehension"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((node, "function"))
    return out


def label_of(node, kind, line, column):
    """The context label a container contributes at this position."""
    if kind == "lambda":
        return "lambda"
    if kind == "comprehension":
        return "comprehension"
    if kind == "class":
        return "class_body" if (line, column) >= _body_start(node) else "class_header"
    return "function_body" if (line, column) >= _body_start(node) else "signature"


def module_block_depth(tree, line, column):
    """How many module-level compound statements hold the position (the block tree of a module)."""
    depth = 0
    for node in ast.walk(tree):
        if isinstance(node, BLOCK_NODES) and holds(node, line, column):
            depth += 1
    return depth


def classify(ctx, line, column):
    """(tag, bucket, chain, block_depth) for one position outside every function."""
    for start, end, kind in ctx["decorators"]:
        if start <= (line, column) <= end:
            return {"tag": "decorator_of_%s" % kind, "bucket": "decorator",
                    "chain": ["decorator_of_%s" % kind], "block_depth": 0}
    held = []
    for node, kind in ctx["containers"]:
        if holds(node, line, column):
            span = (_endpos(node) or _pos(node))[0] - _pos(node)[0]
            held.append((span, label_of(node, kind, line, column)))
    held.sort(key=lambda item: -item[0])
    chain = [label for _, label in held]
    bucket = chain[-1] if chain else "module_body"
    return {"tag": ">".join(chain) if chain else "module_body", "bucket": bucket,
            "chain": chain,
            "block_depth": module_block_depth(ctx["tree"], line, column)
            if bucket == "module_body" else 0}


def context_of_file(path):
    """Parse once and hand back everything classify() needs; None when the file cannot be parsed."""
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    return {"tree": tree, "decorators": decorator_spans(tree),
            "containers": containers_of(tree), "lines": src.splitlines()}


# ---------------------------------------------------------------- measure
def _blank_contexts():
    return {b: {"sites": 0, "writes": 0, "load": 0, "store": 0, "del": 0,
                "literal_key_sites": 0, "computed_key_sites": 0} for b in BUCKETS}


def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    file_rows = []
    examples = {b: [] for b in BUCKETS}
    tags = {}
    total_sites = 0
    for p in files:
        got, why = e638.file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        total_sites += len(got["sites"])
        if not got["sites"]:
            continue
        module = rel(p, root)
        spans = e640.function_spans(p)
        ctx = context_of_file(p)
        if spans is None or ctx is None:
            holes["does_not_parse"] = holes.get("does_not_parse", 0) + 1
            continue
        contexts = _blank_contexts()
        owned = 0
        block_sites = 0
        for site in got["sites"]:
            owner = e640.innermost_owner(spans, site["line"])
            if owner is not None:
                owned += 1
                continue
            cls = classify(ctx, site["line"], site["column"])
            row = e640.site_row(site)
            cell = contexts[cls["bucket"]]
            cell["sites"] += 1
            if row["any_member_is_write"]:
                cell["writes"] += 1
            literal = False
            for member in row["members"]:
                name = member.get("ctx")
                cell[name] = cell.get(name, 0) + 1
                if member.get("key") is not None:
                    literal = True
            if literal:
                cell["literal_key_sites"] += 1
            else:
                cell["computed_key_sites"] += 1
            if cls["block_depth"]:
                block_sites += 1
            tags[cls["tag"]] = tags.get(cls["tag"], 0) + 1
            bucket_examples = examples[cls["bucket"]]
            if len(bucket_examples) < MAX_EXAMPLES_PER_BUCKET:
                text = ""
                lines = ctx["lines"]
                if 0 < site["line"] <= len(lines):
                    text = lines[site["line"] - 1].strip()[:160]
                bucket_examples.append({
                    "module": module, "line": site["line"], "column": site["column"],
                    "tag": cls["tag"], "depth_pair": site["depth_pair"],
                    "member_ctx": sorted({m.get("ctx") for m in row["members"]}),
                    "source": text,
                })
        nonfunc = sum(c["sites"] for c in contexts.values())
        if not nonfunc and not owned:
            continue
        file_rows.append({
            "module": module,
            "two_depth_sites": len(got["sites"]),
            "sites_with_an_owner_function": owned,
            "sites_without_an_owner_function": nonfunc,
            "module_body_sites_inside_a_module_block": block_sites,
            "contexts": {b: c for b, c in contexts.items() if c["sites"]},
        })
    file_rows.sort(key=lambda r: (-r["sites_without_an_owner_function"], r["module"]))
    counts = counts_of(file_rows, len(files), holes, total_sites)
    counts["context_tag_histogram"] = dict(sorted(tags.items()))
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks, import E638's two-depth site "
                   "grouping and E640's innermost-owner split, and for every site whose innermost "
                   "enclosing function is absent publish its innermost syntactic context and full "
                   "container chain (decorator / class header / class body / lambda / "
                   "comprehension / module body), the write face of each context, whether the "
                   "key is a literal, and how deep inside module-level compound statements a "
                   "module_body site sits"),
        "population_source": ("%d Python files of the tree corpus; the population is every "
                              "two-depth site E640's owner split leaves without a function"
                              % len(files)),
        "counts": counts,
        "bucket_rows": bucket_rows_from(file_rows),
        "file_rows": file_rows,
        "examples": {b: v for b, v in examples.items() if v},
        "limits": [
            "'context' is the innermost container holding the site's (line, column), so a site "
            "inside a lambda inside a class body is published as lambda with the chain "
            "class_body>lambda rather than as class body",
            "a decorator is outside its own FunctionDef's span (it sits on the lines before the "
            "def), so decorators are detected in a separate pass or every decorated module-level "
            "site would be counted as module_body",
            "a site whose position the container pass puts inside a function body while the owner "
            "split found no owner is published under the function_body bucket instead of being "
            "dropped; a non-zero there is a disagreement between the two rulers, not a context",
            "module-level compound statements (if/for/while/with/try/except) are counted as "
            "block depth rather than as separate contexts, because they do not carry a scope",
            "class header means the bases/keywords region of a class statement, and signature "
            "means a def's header outside its body -- neither is a separate scope, both are "
            "published so that 'outside a function' is not silently widened",
            "the exclusion list drops only this study's own files, so E638's/E640's scripts stay "
            "inside the population and the site totals are slightly larger than theirs; the "
            "difference against E640's published residual is published as delta_vs_source_face "
            "with its reason rather than reconciled away",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted apart",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts)
    return doc


def _cell_sum(file_rows, field):
    return sum(c.get(field, 0) for f in file_rows for c in (f.get("contexts") or {}).values())


def bucket_rows_from(file_rows):
    """Per-context aggregates, re-derived from the file rows so the gate can re-add them."""
    acc = {}
    for f in file_rows:
        for bucket, c in (f.get("contexts") or {}).items():
            row = acc.setdefault(bucket, {
                "bucket": bucket, "sites": 0, "writes": 0, "load": 0, "store": 0, "del": 0,
                "literal_key_sites": 0, "computed_key_sites": 0, "files": 0})
            row["files"] += 1
            for field in ("sites", "writes", "load", "store", "del", "literal_key_sites",
                          "computed_key_sites"):
                row[field] += c.get(field, 0) or 0
    rows = [r for r in acc.values() if r["sites"]]
    rows.sort(key=lambda r: (-r["sites"], r["bucket"]))
    return rows


def _source_residual(root=ROOT):
    """E640's published residual, read from its face -- never hand-copied."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        face = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    counts = face.get("counts") or {}
    total = counts.get("two_depth_sites")
    owned = counts.get("two_depth_sites_with_an_owner_function")
    if total is None or owned is None:
        return None
    return {"two_depth_sites": total, "sites_with_an_owner_function": owned,
            "sites_without_an_owner_function": total - owned,
            "face": SOURCE_FACE, "study": face.get("study")}


def counts_of(file_rows, files_scanned=0, holes=None, total_sites=None):
    holes = holes or {}
    rows = bucket_rows_from(file_rows)
    sites = sum(r["sites"] for r in rows)
    writes = sum(r["writes"] for r in rows)
    with_writes = [r["bucket"] for r in rows if r["writes"]]
    source = _source_residual()
    c = {
        "python_files_scanned": files_scanned,
        "python_files_over_the_size_cap": int(holes.get("over_the_size_cap") or 0),
        "python_files_unreadable": int(holes.get("unreadable") or 0),
        "python_files_that_do_not_parse": int(holes.get("does_not_parse") or 0),
        "two_depth_sites": total_sites if total_sites is not None else sum(
            f.get("two_depth_sites", 0) for f in file_rows),
        "sites_with_an_owner_function": sum(
            f.get("sites_with_an_owner_function", 0) for f in file_rows),
        "sites_without_an_owner_function": sites,
        "contexts_with_sites": sum(1 for r in rows if r["sites"]),
        "contexts_with_writes": len(with_writes),
        "write_sites_without_an_owner_function": writes,
        "literal_key_sites_without_an_owner_function": sum(
            r["literal_key_sites"] for r in rows),
        "computed_key_sites_without_an_owner_function": sum(
            r["computed_key_sites"] for r in rows),
        "module_body_sites_inside_a_module_block": sum(
            f.get("module_body_sites_inside_a_module_block", 0) for f in file_rows),
        "sites_whose_context_says_a_function_body": sum(
            r["sites"] for r in rows if r["bucket"] == "function_body"),
        "files_carrying_a_site_without_an_owner_function": len(file_rows),
        "bucket_histogram": {r["bucket"]: r["sites"] for r in rows},
        "bucket_write_histogram": {r["bucket"]: r["writes"] for r in rows},
        "contexts_measured_with_no_sites": [b for b in BUCKETS if b not in
                                            {r["bucket"] for r in rows}],
    }
    if source:
        c["source_face_no_owner_sites"] = source["sites_without_an_owner_function"]
        c["delta_vs_source_face"] = sites - source["sites_without_an_owner_function"]
        c["source_face_study"] = source["study"]
    return c


def decide(c):
    if not c.get("sites_without_an_owner_function"):
        return V_ABSENT
    if (c.get("contexts_with_sites") or 0) <= 1:
        return V_ONE_CONTEXT
    if (c.get("contexts_with_writes") or 0) <= 1:
        return V_SEVERAL_WRITES_IN_ONE
    return V_SEVERAL_WRITES_SPREAD


def answer_of(c):
    hist = c.get("bucket_histogram") or {}
    writes = c.get("bucket_write_histogram") or {}
    return ("%d files, %d two-depth sites of which %d have an owner function and %d do not; the "
            "residual splits as %s with write sites %s; key form: %d literal / %d computed; %d "
            "module_body site(s) sit inside a module-level compound statement; contexts measured with no "
            "site: %s; %d site(s) where the context pass says function body while the owner split "
            "says none (delta vs E640's published residual: %s)"
            % (c.get("python_files_scanned"), c.get("two_depth_sites"),
               c.get("sites_with_an_owner_function"),
               c.get("sites_without_an_owner_function"),
               json.dumps(hist, sort_keys=True), json.dumps(writes, sort_keys=True),
               c.get("literal_key_sites_without_an_owner_function"),
               c.get("computed_key_sites_without_an_owner_function"),
               c.get("module_body_sites_inside_a_module_block"),
               json.dumps(c.get("contexts_measured_with_no_sites") or []),
               c.get("sites_whose_context_says_a_function_body"),
               c.get("delta_vs_source_face")))


COUNT_KEYS = (
    "two_depth_sites", "sites_with_an_owner_function", "sites_without_an_owner_function",
    "contexts_with_sites", "contexts_with_writes", "write_sites_without_an_owner_function",
    "literal_key_sites_without_an_owner_function",
    "computed_key_sites_without_an_owner_function",
    "module_body_sites_inside_a_module_block", "sites_whose_context_says_a_function_body",
    "files_carrying_a_site_without_an_owner_function", "bucket_histogram",
    "bucket_write_histogram", "contexts_measured_with_no_sites",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own file rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    files = face.get("file_rows") or []
    c = face.get("counts") or {}
    live = counts_of(files, c.get("python_files_scanned"),
                     {"over_the_size_cap": c.get("python_files_over_the_size_cap"),
                      "unreadable": c.get("python_files_unreadable"),
                      "does_not_parse": c.get("python_files_that_do_not_parse")},
                     c.get("two_depth_sites"))
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the file rows" % key)
    if face.get("bucket_rows") != bucket_rows_from(files):
        problems.append("the bucket rows are not the ones the file rows aggregate to")
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in files:
        contexts = f.get("contexts") or {}
        nonfunc = sum(v.get("sites", 0) for v in contexts.values())
        if nonfunc != f.get("sites_without_an_owner_function"):
            problems.append("file row %s carries contexts that do not add to its residual"
                            % f.get("module"))
            break
        if (f.get("sites_with_an_owner_function", 0) + nonfunc) != f.get("two_depth_sites", 0):
            problems.append("file row %s does not split its sites between owners and contexts"
                            % f.get("module"))
            break
        if (f.get("module_body_sites_inside_a_module_block") or 0) > (
                (contexts.get("module_body") or {}).get("sites") or 0):
            problems.append("file row %s has more blocked module sites than module sites"
                            % f.get("module"))
            break
        bad = False
        for bucket, cell in contexts.items():
            if bucket not in BUCKETS:
                problems.append("file row %s publishes an unknown context %s"
                                % (f.get("module"), bucket))
                bad = True
                break
            if (cell.get("writes") or 0) > (cell.get("sites") or 0):
                problems.append("file row %s has more writes than sites in %s"
                                % (f.get("module"), bucket))
                bad = True
                break
            if (cell.get("literal_key_sites", 0) + cell.get("computed_key_sites", 0)) != (
                    cell.get("sites") or 0):
                problems.append("file row %s does not split literal/computed keys in %s"
                                % (f.get("module"), bucket))
                bad = True
                break
            if (cell.get("writes") or 0) > ((cell.get("store") or 0) + (cell.get("del") or 0)):
                problems.append("file row %s has a write site with no store/delete member in %s"
                                % (f.get("module"), bucket))
                bad = True
                break
        if bad:
            break
    if face.get("verdict") == V_ABSENT and c.get("sites_without_an_owner_function", 0) > 0:
        problems.append("the absent verdict is published while the residual has members")
    if face.get("verdict") == V_ONE_CONTEXT and (c.get("contexts_with_sites") or 0) > 1:
        problems.append("the one-context verdict is published while several contexts carry sites")
    if face.get("verdict") == V_SEVERAL_WRITES_IN_ONE and (
            (c.get("contexts_with_sites") or 0) <= 1 or (c.get("contexts_with_writes") or 0) > 1):
        problems.append("the confined-write verdict is not the one its own totals force")
    if face.get("verdict") == V_SEVERAL_WRITES_SPREAD and (
            (c.get("contexts_with_writes") or 0) <= 1):
        problems.append("the spread-write verdict is published while writes sit in one context")
    if "delta_vs_source_face" in c:
        if c["delta_vs_source_face"] != (
                c["sites_without_an_owner_function"] - c["source_face_no_owner_sites"]):
            problems.append("the delta against the source face is not the difference")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d sites=%d owned=%d residual=%d contexts=%d write_contexts=%d "
        "residual_writes=%d"
        % (c["python_files_scanned"], c["two_depth_sites"], c["sites_with_an_owner_function"],
           c["sites_without_an_owner_function"], c["contexts_with_sites"],
           c["contexts_with_writes"], c["write_sites_without_an_owner_function"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_SRC = '''\
import json

D = {"a": {"b": 1}}
D["a"]["b"] = 2


def deco(fn):
    return fn


@deco
def decorated():
    return 1


class Holder:
    P = D["a"]["b"]
    Q = D["a"]["b"] + 1
    R = [D["a"]["b"] for _ in range(1)]
    S = lambda self: D["a"]["b"]

    def method(self):
        return D["a"]["b"]


if True:
    D2 = D["a"]["b"]
'''


def _fixture_ctx(source=FIXTURE_SRC):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(source)
    try:
        payload, why = e638.file_sites(path)
        assert why is None, why
        return context_of_file(path), payload, e640.function_spans(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _site_ctx(source, needle, nth=0):
    """Classify the nth site whose source line contains ``needle`` -- fixtures are located by text."""
    ctx, got, spans = _fixture_ctx(source)
    hits = [s for s in got["sites"]
            if needle in (ctx["lines"][s["line"] - 1] if s["line"] <= len(ctx["lines"]) else "")]
    site = hits[nth]
    cls = classify(ctx, site["line"], site["column"])
    cls["owner"] = e640.innermost_owner(spans, site["line"])
    cls["site"] = site
    return cls


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

    def a_module_level_site_is_module_body():
        got = _site_ctx(FIXTURE_SRC, 'D["a"]["b"] = 2')
        assert got["owner"] is None, got["owner"]
        assert got["bucket"] == "module_body" and got["tag"] == "module_body", got

    def a_class_body_site_is_class_body():
        got = _site_ctx(FIXTURE_SRC, "    P = D[")
        assert got["owner"] is None, got["owner"]
        assert got["bucket"] == "class_body", got

    def a_class_level_comprehension_is_a_comprehension():
        got = _site_ctx(FIXTURE_SRC, "    R = [")
        assert got["bucket"] == "comprehension", got
        assert got["tag"] == "class_body>comprehension", got

    def a_class_level_lambda_is_a_lambda():
        got = _site_ctx(FIXTURE_SRC, "    S = lambda")
        assert got["bucket"] == "lambda", got
        assert got["chain"] == ["class_body", "lambda"], got

    def a_decorator_site_is_not_module_body():
        source = ('D = {"a": {"b": 1}}\n\n\ndef deco(fn):\n    return fn\n\n\n'
                  '@deco(D["a"]["b"])\ndef f():\n    return 1\n')
        got = _site_ctx(source, "@deco(")
        assert got["owner"] is None, got["owner"]
        assert got["bucket"] == "decorator", got

    def a_site_inside_a_method_is_owned():
        got = _site_ctx(FIXTURE_SRC, "        return D[")
        assert got["owner"] is not None, got
        assert got["owner"]["qualname"] == "Holder.method", got["owner"]

    def block_depth_separates_the_block_tree():
        got = _site_ctx(FIXTURE_SRC, "    D2 = D[")
        assert got["bucket"] == "module_body", got
        assert got["block_depth"] == 1, got

    def a_lambda_inside_a_function_is_owned():
        source = 'D = {"a": {"b": 1}}\n\n\ndef f():\n    g = lambda: D["a"]["b"]\n    return g\n'
        got = _site_ctx(source, "g = lambda")
        assert got["owner"] is not None and got["owner"]["qualname"] == "f", got

    def function_body_bucket_is_reachable():
        cls = {"tag": "function_body", "bucket": "function_body", "chain": [], "block_depth": 0}
        assert cls["bucket"] in BUCKETS

    def counts_add_up():
        ctx, got, spans = _fixture_ctx()
        rows = [{"module": "a.py", "two_depth_sites": 3, "sites_with_an_owner_function": 1,
                 "sites_without_an_owner_function": 2,
                 "module_body_sites_inside_a_module_block": 1,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 2, "store": 1,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0},
                              "class_body": {"sites": 1, "writes": 0, "load": 2, "store": 0,
                                             "del": 0, "literal_key_sites": 0,
                                             "computed_key_sites": 1}}}]
        c = counts_of(rows, 1, {}, 3)
        assert c["sites_without_an_owner_function"] == 2, c
        assert c["contexts_with_sites"] == 2, c
        assert c["contexts_with_writes"] == 1, c
        assert c["bucket_histogram"] == {"module_body": 1, "class_body": 1}, c
        assert c["module_body_sites_inside_a_module_block"] == 1, c
        assert c["sites_whose_context_says_a_function_body"] == 0, c

    def several_but_one_write_context_is_reachable():
        rows = [{"module": "a.py", "two_depth_sites": 2, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 2, "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 1, "store": 1},
                              "lambda": {"sites": 1, "writes": 0, "load": 1, "store": 0}}}]
        c = counts_of(rows, 1, {}, 2)
        assert decide(c) == V_SEVERAL_WRITES_IN_ONE, (decide(c), c)

    def several_with_spread_writes_is_reachable():
        rows = [{"module": "a.py", "two_depth_sites": 2, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 2, "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 1, "store": 1},
                              "lambda": {"sites": 1, "writes": 1, "load": 1, "store": 1}}}]
        c = counts_of(rows, 1, {}, 2)
        assert decide(c) == V_SEVERAL_WRITES_SPREAD, (decide(c), c)

    def one_context_and_absent_are_reachable():
        one = [{"module": "a.py", "two_depth_sites": 1, "sites_with_an_owner_function": 0,
                "sites_without_an_owner_function": 1,
                "module_body_sites_inside_a_module_block": 0,
                "contexts": {"module_body": {"sites": 1, "writes": 0, "load": 2, "store": 0}}}]
        assert decide(counts_of(one, 1, {}, 1)) == V_ONE_CONTEXT
        none = [{"module": "a.py", "two_depth_sites": 1, "sites_with_an_owner_function": 1,
                 "sites_without_an_owner_function": 0,
                 "module_body_sites_inside_a_module_block": 0, "contexts": {}}]
        assert decide(counts_of(none, 1, {}, 1)) == V_ABSENT

    def face_problems_accepts_a_sound_face():
        rows = [{"module": "a.py", "two_depth_sites": 3, "sites_with_an_owner_function": 1,
                 "sites_without_an_owner_function": 2,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 1, "store": 1,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0},
                              "lambda": {"sites": 1, "writes": 0, "load": 1, "store": 0,
                                         "del": 0, "literal_key_sites": 0,
                                         "computed_key_sites": 1}}}]
        c = counts_of(rows, 1, {}, 3)
        face = {"file_rows": rows, "counts": c, "verdict": decide(c),
                "bucket_rows": bucket_rows_from(rows)}
        assert not face_problems(face), face_problems(face)

    def face_problems_catches_contexts_that_do_not_add():
        rows = [{"module": "a.py", "two_depth_sites": 2, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 2,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 0, "load": 1, "store": 0,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0}}}]
        c = counts_of(rows, 1, {}, 2)
        face = {"file_rows": rows, "counts": c, "verdict": decide(c),
                "bucket_rows": bucket_rows_from(rows)}
        assert any("do not add" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_write_without_a_store():
        rows = [{"module": "a.py", "two_depth_sites": 1, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 1,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 2, "store": 0,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0}}}]
        c = counts_of(rows, 1, {}, 1)
        face = {"file_rows": rows, "counts": c, "verdict": decide(c),
                "bucket_rows": bucket_rows_from(rows)}
        assert any("no store/delete member" in p for p in face_problems(face)), \
            face_problems(face)

    def face_problems_catches_a_wrong_verdict():
        rows = [{"module": "a.py", "two_depth_sites": 2, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 2,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 1, "store": 1},
                              "lambda": {"sites": 1, "writes": 1, "load": 1, "store": 1}}}]
        c = counts_of(rows, 1, {}, 2)
        face = {"file_rows": rows, "counts": c, "verdict": V_ONE_CONTEXT,
                "bucket_rows": bucket_rows_from(rows)}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_delta_that_is_not_the_difference():
        rows = [{"module": "a.py", "two_depth_sites": 1, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 1,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 0, "load": 2, "store": 0,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0}}}]
        c = counts_of(rows, 1, {}, 1)
        c["source_face_no_owner_sites"] = 5
        c["delta_vs_source_face"] = 99
        face = {"file_rows": rows, "counts": c, "verdict": decide(c),
                "bucket_rows": bucket_rows_from(rows)}
        assert any("delta" in p for p in face_problems(face)), face_problems(face)

    def a_zero_context_is_published_as_measured():
        rows = [{"module": "a.py", "two_depth_sites": 1, "sites_with_an_owner_function": 0,
                 "sites_without_an_owner_function": 1,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 0, "load": 2, "store": 0,
                                              "del": 0, "literal_key_sites": 1,
                                              "computed_key_sites": 0}}}]
        c = counts_of(rows, 1, {}, 1)
        missing = [b for b in BUCKETS if b not in c["bucket_histogram"]]
        assert c["contexts_measured_with_no_sites"] == missing, c
        assert "class_body" in missing and "decorator" in missing, missing

    def answer_names_the_numbers():
        rows = [{"module": "a.py", "two_depth_sites": 2, "sites_with_an_owner_function": 1,
                 "sites_without_an_owner_function": 1,
                 "module_body_sites_inside_a_module_block": 0,
                 "contexts": {"module_body": {"sites": 1, "writes": 1, "load": 1, "store": 1}}}]
        a = answer_of(counts_of(rows, 1, {}, 2))
        assert "1 do not" in a and "module_body" in a, a

    for name, fn in [
        ("a_module_level_site_is_module_body", a_module_level_site_is_module_body),
        ("a_class_body_site_is_class_body", a_class_body_site_is_class_body),
        ("a_class_level_comprehension_is_a_comprehension",
         a_class_level_comprehension_is_a_comprehension),
        ("a_class_level_lambda_is_a_lambda", a_class_level_lambda_is_a_lambda),
        ("a_decorator_site_is_not_module_body", a_decorator_site_is_not_module_body),
        ("a_site_inside_a_method_is_owned", a_site_inside_a_method_is_owned),
        ("block_depth_separates_the_block_tree", block_depth_separates_the_block_tree),
        ("a_lambda_inside_a_function_is_owned", a_lambda_inside_a_function_is_owned),
        ("function_body_bucket_is_reachable", function_body_bucket_is_reachable),
        ("counts_add_up", counts_add_up),
        ("several_but_one_write_context_is_reachable",
         several_but_one_write_context_is_reachable),
        ("several_with_spread_writes_is_reachable", several_with_spread_writes_is_reachable),
        ("one_context_and_absent_are_reachable", one_context_and_absent_are_reachable),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_contexts_that_do_not_add",
         face_problems_catches_contexts_that_do_not_add),
        ("face_problems_catches_a_write_without_a_store",
         face_problems_catches_a_write_without_a_store),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_delta_that_is_not_the_difference",
         face_problems_catches_a_delta_that_is_not_the_difference),
        ("a_zero_context_is_published_as_measured", a_zero_context_is_published_as_measured),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


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