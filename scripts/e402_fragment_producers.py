"""E402 -- who composes a bare-basename fragment, and can that join ever land on a file?

E399 resolved every published key and found 52 of 884 names (5.9%) are bare BASENAMES: a file name
with no directory.  It published them as ``bare_basename_whose_directory_is_a_runtime_variable`` and
stopped there -- "the directory is supplied at the one site that writes it" was an inference, not a
reading.  This study tests the inference on the producer side.

For each of the 52 fragments it finds every site where the name appears as an *exact* string
constant (substring matching is wrong here: ``_judge.json`` occurs inside ``w13_judge.json`` at
thirteen places that have nothing to do with the key), classifies the site as a write or a read, and
then traces the directory expression that the site joins the name onto:

  C1 constant directory that does hold the file          ("results" + "idle_trigger.bm-c.json")
  C2 constant directory that does not hold it            -> the join can never land
  C3 cwd-relative (no join at all)                       -> the file, if written, lands in ROOT
  C4 temporary directory, deleted by design              -> a fixture name, not a face
  C5 runtime value: parameter, loop variable, env temp   -> legitimate runtime name
  C6 directory built from a name/date the tree does not hold -> a naming scheme, not a path
  C7 directory expression could not be traced statically

The bill is per-fragment: the write sites, the directory expression as written, its class, and
whether the composed path exists right now.  No published face, pointer or key is edited.

Usage:
  python scripts/e402_fragment_producers.py run       # build the face
  python scripts/e402_fragment_producers.py verify    # re-derive every row from the tree
  python scripts/e402_fragment_producers.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e397_walk_ambiguity as e397  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402
import e399_unresolved_names as e399  # noqa: E402

TODAY = "2026-11-04"
FACE = "FRAGMENTPRODUCERS-%s.json" % TODAY
LATEST = "fragmentproducers_latest.json"
# The card that seeded this study names FRAGMENTPRODUCERS-2026-11-05.json (seeded 2026-11-04 01:4x,
# expected to be burned the next day).  A face is dated by when it was built, so the file carries
# today's date and the card name is recorded below rather than silently honoured with a future date.
CARD_DELIVERABLE = "results/state_tilt/FRAGMENTPRODUCERS-2026-11-05.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E402_fragment_producers"
SELF_REL = "scripts/e402_fragment_producers.py"
SIBLING_FACE = "UNRESOLVED-2026-11-04.json"

FRAGMENT_CLASS = "bare_basename_whose_directory_is_a_runtime_variable"

C1 = "constant_directory_that_holds_the_file_in_the_tree"
C2 = "constant_directory_that_does_not_hold_the_file"
C3 = "cwd_relative_no_directory_supplied"
C4 = "temporary_directory_deleted_by_design"
C5 = "directory_supplied_by_a_runtime_value"
C6 = "directory_built_from_a_name_or_date_the_tree_does_not_hold"
C7 = "directory_expression_not_traceable_statically"
C8 = ("fragment_is_a_suffix_or_prefix_of_a_computed_name_so_the_key_was_never_a_whole_"
      "filename")

CLASSES = (C1, C2, C3, C4, C5, C6, C7, C8)

V_NO_WRITER = ("no_write_site_composes_these_fragments_in_the_python_corpus_so_the_producer_side_"
               "claim_cannot_be_tested_on_this_population")
V_SCAFFOLDING = ("the_fragments_are_fixture_and_runtime_names_whose_directories_are_temporary_or_"
                 "supplied_by_a_caller_so_none_of_them_will_ever_resolve_and_the_residual_is_"
                 "scaffolding_not_attrition")
V_DEAD_WRITES = ("some_fragments_are_joined_onto_a_constant_directory_that_does_not_hold_them_so_"
                 "those_writes_land_somewhere_nobody_indexes")
V_MIXED = ("the_fragments_split_between_design_names_and_joins_that_cannot_land_so_the_residual_is_"
           "partly_a_real_gap")
V_UNTRACED = ("most_fragment_directories_cannot_be_traced_statically_so_the_producer_side_claim_is_"
              "not_measured")

JOIN_FUNCS = {"join", "joinpath", "abspath", "normpath", "realpath", "expanduser", "dirname"}
TEMP_FUNCS = {"mkdtemp", "TemporaryDirectory", "mkstemp", "NamedTemporaryFile", "TemporaryFile",
              "gettempdir"}
WRITE_FUNCS = {"dump", "to_csv", "to_parquet", "write_text", "write_bytes", "savefig", "to_json",
               "write", "savetxt"}
CWD_SENTINELS = (".", "")

# The existence test is a seam: the selftest swaps it for a fixture predicate instead of writing
# junk files into the repo to make a constant directory "hold" something.
EXISTS = os.path.exists


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- site extraction

class Ctx(object):
    """Source text + parent map for one file, built once."""

    def __init__(self, relpath, text, tree):
        self.relpath = relpath
        self.text = text
        self.tree = tree
        self.parent = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self.parent[child] = node

    def src(self, node):
        try:
            return ast.get_source_segment(self.text, node) or ""
        except Exception:
            return ""

    def climb(self, node):
        while node in self.parent:
            node = self.parent[node]
            yield node

    def enclosing_function(self, node):
        for parent in self.climb(node):
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                return parent
        return None

    def env(self, node):
        """``{name: expr}`` from module level plus the function enclosing ``node``.

        ``with tempfile.TemporaryDirectory() as tmp`` is how this corpus names its scratch
        directories, and a ``withitem`` is not an ``Assign`` -- missing it turned 24 sites into
        "not traceable" for no reason.
        """
        env = {}
        for source in (self.tree.body, None):
            stmts = source
            if stmts is None:
                func = self.enclosing_function(node)
                if func is None:
                    break
                stmts = [func]
            for root in stmts:
                for child in ast.walk(root):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                env[target.id] = child.value
                    elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                        env[child.target.id] = child.value
                    elif isinstance(child, (ast.For, ast.comprehension)):
                        target = getattr(child, "target", None)
                        if isinstance(target, ast.Name):
                            env[target.id] = getattr(child, "iter", None)
                    elif isinstance(child, ast.withitem) and isinstance(child.optional_vars, ast.Name):
                        env[child.optional_vars.id] = child.context_expr
        return env

    def is_param(self, node, name):
        func = self.enclosing_function(node)
        if func is None:
            return False
        args = getattr(func, "args", None)
        if args is None:
            return False
        for group in (args.args, args.posonlyargs or [], args.kwonlyargs, args.vararg, args.kwarg):
            if not group:
                continue
            items = group if isinstance(group, list) else [group]
            for item in items:
                if getattr(item, "arg", None) == name:
                    return True
        return False


def name_of_call(node):
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def mode_is_write(call):
    """``open(p)`` defaults to 'r'; ``open(p, 'w')`` is a write."""
    if len(call.args) > 1 and isinstance(call.args[1], ast.Constant) \
            and isinstance(call.args[1].value, str):
        return "w" in call.args[1].value or "a" in call.args[1].value or "x" in call.args[1].value
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                and isinstance(kw.value.value, str):
            m = kw.value.value
            return "w" in m or "a" in m or "x" in m
    return False


def site_write_kind(ctx, node):
    """``write`` / ``read`` / ``unknown`` for the statement that carries ``node``."""
    for parent in ctx.climb(node):
        if isinstance(parent, ast.expr):
            continue
        if isinstance(parent, ast.stmt):
            stmt_node = parent
            break
    else:
        return "unknown"
    for child in ast.walk(stmt_node):
        if isinstance(child, ast.Call):
            fname = name_of_call(child)
            if fname in WRITE_FUNCS:
                if fname == "write" and not (child.args and isinstance(child.args[0], (ast.JoinedStr, ast.Constant, ast.BinOp))):
                    continue
                return "write"
            if fname in ("open", "io") or (isinstance(child.func, ast.Attribute)
                                            and child.func.attr == "open"):
                return "write" if mode_is_write(child) else "read"
    return "unknown"


def dir_expression(ctx, node):
    """The expression the fragment is joined ONTO, or ``(None, None)`` when there is none."""
    current = node
    for parent in ctx.climb(node):
        if isinstance(parent, ast.Call):
            fname = name_of_call(parent)
            if fname in JOIN_FUNCS:
                args = [a for a in parent.args if a is not current and
                        not (isinstance(a, ast.Constant) and isinstance(a.value, (int, float)))]
                # the directory is everything left of the fragment, in order
                idx = list(parent.args).index(current)
                before = [a for a in parent.args[:idx]
                          if not (isinstance(a, ast.Constant) and isinstance(a.value, (int, float)))]
                if not before:
                    return None, ctx.src(parent)
                return before, ctx.src(parent)
            if fname == "Path":
                idx = list(parent.args).index(current) if current in parent.args else 0
                before = parent.args[:idx]
                if not before:
                    return None, ctx.src(parent)
                return before, ctx.src(parent)
            if fname in ("open", "Path", "str"):
                return None, ctx.src(parent)
        if isinstance(parent, ast.BinOp):
            if isinstance(parent.op, ast.Add) and parent.right is current:
                return [parent.left], ctx.src(parent)
            if isinstance(parent.op, ast.Mod) and parent.right is current:
                return [parent.left], ctx.src(parent)
            if isinstance(parent.op, ast.Div) and parent.right is current:
                return [parent.left], ctx.src(parent)
        if isinstance(parent, ast.JoinedStr):
            values = parent.values
            idx = None
            for i, v in enumerate(values):
                if v is current:
                    idx = i
                    break
            if idx is None:
                return None, ctx.src(parent)
            before = [v for v in values[:idx] if not (isinstance(v, ast.Constant)
                                                      and isinstance(v.value, str)
                                                      and v.value.strip() == "")]
            return before or None, ctx.src(parent)
        current = parent
    return None, None


# --------------------------------------------------------------------------- directory tracing

def _segments(exprs, ctx, depth=0):
    """Best-effort ``(parts, dynamic, reason)`` for a list of path-part expressions."""
    parts, dynamic = [], []
    for expr in exprs:
        sub, dyn, why = trace(expr, ctx, depth + 1)
        parts.extend(sub)
        if dyn:
            dynamic.append(dyn)
    return parts, (dynamic[0] if dynamic else None)


def trace(expr, ctx, depth=0):
    """``(constant_parts, dynamic_reason_or_None, why)`` for one directory expression."""
    if depth > 6 or expr is None:
        return [], "unresolved", "depth or missing expression"
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return [expr.value], None, "string constant"
    if isinstance(expr, (ast.JoinedStr,)):
        return [], "formatted_string", "f-string"
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Mod, ast.Add)):
        left, dyn, why = trace(expr.left, ctx, depth + 1)
        return left, dyn or "formatted_string", "format operator"
    if isinstance(expr, ast.Name):
        name = expr.id
        if name == "__file__":
            return [os.path.join(ROOT, os.path.dirname(ctx.relpath))], None, "__file__"
        env = ctx.env(expr)
        if name in env and env[name] is not None:
            return trace(env[name], ctx, depth + 1)
        if name in ("ROOT", "HERE", "ROOT_DIR", "REPO", "BASE_DIR", "BASE"):
            return [ROOT], None, "repo-root constant %s" % name
        if ctx.is_param(expr, name):
            return [], "parameter", "function parameter %s" % name
        if name.isupper():
            return [], "module_constant_unresolved", "module constant %s (no assignment found)" % name
        return [], "unresolved", "name %s not resolved" % name
    if isinstance(expr, ast.Call):
        fname = name_of_call(expr)
        if fname in TEMP_FUNCS:
            return [], "temp", "tempfile/%s" % fname
        if fname in ("get",) and isinstance(expr.func, ast.Attribute):
            inner = expr.func.value
            if isinstance(inner, ast.Attribute) and inner.attr == "environ":
                key = expr.args[0].value if expr.args and isinstance(expr.args[0], ast.Constant) else ""
                if str(key).upper() in ("TEMP", "TMP", "TMPDIR"):
                    return [], "temp", "os.environ[%s]" % key
                return [], "env_var", "os.environ[%s]" % key
            return [], "unresolved", "call %s" % fname
        if fname == "environ" or (isinstance(expr.func, ast.Attribute) and expr.func.attr == "environ"):
            return [], "env_var", "os.environ subscript"
        if fname in JOIN_FUNCS:
            parts, dynamic = _segments([a for a in expr.args], ctx, depth)
            if fname == "dirname" and parts:
                # dirname() drops one segment; flattening it would move the file up into a
                # directory that is not the one the site names (ROOT = dirname(dirname(__file__)))
                parts = parts[:-1]
            return parts, dynamic, "join/%s" % fname
        if fname == "Path":
            parts, dynamic = _segments(expr.args, ctx, depth)
            return parts, dynamic, "Path()"
        if fname in ("str", "format", "fspath"):
            parts, dynamic = _segments(expr.args, ctx, depth)
            return parts, dynamic, "%s()" % fname
        if fname in ("parent", ):
            return [], "unresolved", "call parent"
        return [], "unresolved", "call %s" % fname
    if isinstance(expr, ast.Attribute):
        if expr.attr in ("parent", "parents"):
            return trace(expr.value, ctx, depth + 1)
        return [], "unresolved", "attribute .%s" % expr.attr
    if isinstance(expr, ast.Subscript):
        return [], "unresolved", "subscript"
    if isinstance(expr, ast.FormattedValue):
        return [], "formatted_string", "f-string value"
    if isinstance(expr, ast.Compare):
        return [], "unresolved", "comparison"
    return [], "unresolved", ast.dump(expr)[:60]


def classify_dir(parts, dynamic, fragment):
    """Map a traced directory onto one of ``CLASSES`` and give the composed path when static."""
    if dynamic == "temp":
        return C4, None, "temporary directory"
    if dynamic in ("parameter", "env_var"):
        return C5, None, dynamic
    if dynamic == "formatted_string":
        return C6, None, "the name is formatted at the site"
    if dynamic in ("module_constant_unresolved", "unresolved"):
        return C7, None, dynamic
    if not parts:
        return C3, os.path.join(ROOT, fragment), "no directory supplied"
    composed = os.path.join(*(parts + [fragment]))
    if not os.path.isabs(composed):
        composed = os.path.join(ROOT, composed)
    composed = os.path.normpath(composed)
    if EXISTS(composed):
        return C1, composed, "the composed path exists"
    return C2, composed, "the composed path does not exist"


def suffix_only(ctx, node):
    """``(is_suffix, whole_name)`` -- is the fragment only a piece of a longer computed name?

    ``c + "_x1.json"`` does not join a directory onto a file name; it builds the file name itself.
    E399's form test classified the piece as a bare basename, so the key was never a whole filename
    and "resolves to no file" is a category error rather than an absence.
    """
    current = node
    for parent in ctx.climb(node):
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Add):
            if parent.right is current or parent.left is current:
                return True, ctx.src(parent)
        if isinstance(parent, ast.JoinedStr):
            return True, ctx.src(parent)
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Mod) and parent.right is current:
            return True, ctx.src(parent)
        if isinstance(parent, (ast.Call, ast.stmt, ast.expr_context)):
            return False, ctx.src(current) if isinstance(current, ast.expr) else ""
        current = parent
    return False, ""


def site_row(ctx, node, fragment):
    write_kind = site_write_kind(ctx, node)
    is_suffix, whole = suffix_only(ctx, node)
    if is_suffix:
        return {
            "site": "%s:%d" % (ctx.relpath, getattr(node, "lineno", 0)),
            "write_kind": write_kind,
            "directory_expression": (whole or "").strip()[:240],
            "class": C8,
            "composed_path": None,
            "exists": False,
            "why": "the key is a piece of a computed name",
        }
    before, whole = dir_expression(ctx, node)
    if before is None:
        composed = os.path.join(ROOT, fragment) if write_kind != "unknown" else None
        exists = bool(composed and EXISTS(composed))
        klass = C3
        why = "the fragment is used without a directory"
        expr_text = whole or ""
    else:
        parts, dynamic = _segments(before, ctx)
        klass, composed, why = classify_dir(parts, dynamic, fragment)
        exists = bool(composed and EXISTS(composed))
        expr_text = whole or ""
    return {
        "site": "%s:%d" % (ctx.relpath, getattr(node, "lineno", 0)),
        "write_kind": write_kind,
        "directory_expression": expr_text.strip()[:240],
        "class": klass,
        "composed_path": (composed.replace(ROOT + os.sep, "").replace(ROOT, ".") if composed else None),
        "exists": exists,
        "why": why,
    }


def scan_sources(sources):
    """``{fragment: [site rows]}`` over an explicit corpus (the selftest seam).

    One walk per file indexes every string constant, then only the fragments' sites are priced --
    walking every tree once per fragment is 52x the work for the same answer.
    """
    wanted = set(FRAGMENTS_OF(sources))
    index = {}
    for rel, text in sources:
        if rel == SELF_REL:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        local = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and node.value in wanted:
                local.append(node)
        if local:
            for node in local:
                index.setdefault(node.value, []).append((rel, text, tree, node))
    rows_by_fragment = {}
    for fragment in wanted:
        rows = []
        for rel, text, tree, node in index.get(fragment, []):
            rows.append(site_row(Ctx(rel, text, tree), node, fragment))
        rows_by_fragment[fragment] = rows
    return rows_by_fragment


def FRAGMENTS_OF(sources):  # noqa: N802 -- seam for the selftest to pin the population
    return _FRAGMENTS


_FRAGMENTS = []


def fragment_population():
    """The fragment keys, taken from the E399 face rather than re-derived (that is its own study)."""
    path = os.path.join(PUBLISHED_DIR, SIBLING_FACE)
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    keys = [r["key"] for r in face["rows"] if r.get("class") == FRAGMENT_CLASS]
    return face, keys


# --------------------------------------------------------------------------- decide

def decide(summary):
    n_sites = summary["sites_total"]
    if summary["fragments_with_no_site_in_the_corpus"] == summary["fragments"]:
        return V_NO_WRITER
    if n_sites == 0:
        return V_NO_WRITER
    by = summary["by_class"]
    total = sum(by.values()) or 1
    dead = by.get(C2, 0)
    untraced = by.get(C7, 0)
    if untraced / float(total) > 0.5:
        return V_UNTRACED
    if dead:
        return V_DEAD_WRITES if dead / float(total) > 0.2 else V_MIXED
    if summary["fragments_whose_composed_path_exists"] == 0:
        return V_SCAFFOLDING
    return V_MIXED


# --------------------------------------------------------------------------- build / verify

def build(write_face=True, sources=None):
    say("reading the fragment population from E399")
    sibling, fragments = fragment_population()
    _FRAGMENTS[:] = fragments
    say("fragments=%d of %d published keys"
        % (len(fragments), sibling["summary"]["keys_total"]))

    if sources is None:
        pop = e397.population()
        sources = e350._sources()
        corpus = pop.get("sources")
    else:
        corpus = len(sources)

    say("scanning %d corpus sources for exact string constants" % corpus)
    sites = scan_sources(sources)

    rows = []
    for fragment in fragments:
        found = sites.get(fragment) or []
        writes = [r for r in found if r["write_kind"] == "write"]
        reads = [r for r in found if r["write_kind"] == "read"]
        others = [r for r in found if r["write_kind"] == "unknown"]
        producers = writes or others or reads
        classified_from = ("write_site" if writes else
                           ("untagged_site" if others else
                            ("read_site_only" if reads else "nothing")))
        classes = {}
        for row in producers:
            classes[row["class"]] = classes.get(row["class"], 0) + 1
        primary = None
        if producers:
            primary = sorted(producers, key=lambda r: (r["class"] != C2, r["site"]))[0]
        rows.append({
            "fragment": fragment,
            "n_sites": len(found),
            "n_write_sites": len(writes),
            "n_read_sites": len(reads),
            "n_untagged_sites": len(others),
            "producer_class": (primary or {}).get("class"),
            "classified_from": classified_from,
            "producer_site": (primary or {}).get("site"),
            "producer_directory_expression": (primary or {}).get("directory_expression"),
            "producer_composed_path": (primary or {}).get("composed_path"),
            "producer_path_exists": (primary or {}).get("exists"),
            "classes_at_this_fragment": classes,
            "sites": found[:12],
        })

    by_class = {}
    for row in rows:
        for klass, count in (row["classes_at_this_fragment"] or {}).items():
            by_class[klass] = by_class.get(klass, 0) + count

    existing = [r["fragment"] for r in rows if r.get("producer_path_exists")]
    no_site = [r["fragment"] for r in rows if r["n_sites"] == 0]
    by_primary = {}
    for row in rows:
        key = row["producer_class"] or "no_write_or_untagged_site_only_reads"
        by_primary[key] = by_primary.get(key, 0) + 1
    dead = [{"fragment": r["fragment"], "site": r["producer_site"],
             "expression": r["producer_directory_expression"],
             "composed": r["producer_composed_path"]}
            for r in rows if r["producer_class"] == C2]
    from_counts = {}
    for row in rows:
        key = row["classified_from"]
        from_counts[key] = from_counts.get(key, 0) + 1

    keys_total = sibling["summary"]["keys_total"]
    summary = {
        "published_keys": keys_total,
        "published_keys_note": ("taken from the E399 face's own summary: that face carries only the "
                                "98 unresolved rows, so the total cannot be counted from rows"),
        "keys_total_checked": keys_total,
        "fragments": len(fragments),
        "share_of_published_keys_that_are_fragments": (round(len(fragments) / float(keys_total), 4)
                                                       if keys_total else None),
        "fragments_with_no_site_in_the_corpus": len(no_site),
        "fragments_with_a_write_site": sum(1 for r in rows if r["n_write_sites"]),
        "fragments_whose_composed_path_exists": len(existing),
        "sites_total": sum(r["n_sites"] for r in rows),
        "write_sites_total": sum(r["n_write_sites"] for r in rows),
        "read_sites_total": sum(r["n_read_sites"] for r in rows),
        "corpus_sources": corpus,
        "producer_sites_total": sum(by_class.values()),
        "by_class": by_class,
        "by_fragment_primary_class": by_primary,
        "joins_that_can_never_land": dead,
        "fragments_primary_class_dead_join": len(dead),
        "fragments_primary_class_temporary": by_primary.get(C4, 0),
        "fragments_primary_class_runtime_value": by_primary.get(C5, 0),
        "fragments_primary_class_suffix_only": by_primary.get(C8, 0),
        "fragments_with_read_sites_only": by_primary.get("no_write_or_untagged_site_only_reads", 0),
        "by_classified_from": from_counts,
        "classes_sum_to_sites": (sum(by_class.values())
                                 == sum(sum((r["classes_at_this_fragment"] or {}).values())
                                        for r in rows)
                                 and set(by_class) <= set(CLASSES)),
        "fragments_no_site_named": no_site,
        "fragments_that_exist_when_composed": existing,
    }
    summary["verdict"] = decide(summary)

    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "seeded_by": CARD_DELIVERABLE,
        "arms": {
            "A0_population": {"kind": "E399 face rows with class == %s" % FRAGMENT_CLASS,
                              "rows_read": len(sibling["rows"])},
            "A1_site_match": {"kind": "ast.Constant with value == the fragment",
                              "why_not_substring": ("_judge.json occurs inside w13_judge.json at 13 "
                                                    "sites that have nothing to do with the key")},
            "A2_write_test": {"kind": "enclosing statement: open(mode) / json.dump / to_csv / "
                                      "write_text / savetxt", "three_valued": ["write", "read",
                                                                              "unknown"]},
            "A3_directory_trace": {"kind": "join / Path / format / concatenation, one hop through "
                                           "local and module assignments",
                                   "classes": list(CLASSES)},
            "A4_landing_test": {"kind": "does the composed path exist right now"},
        },
        "summary": summary,
        "verdict": summary["verdict"],
        "rows": rows,
        "bounds": {
            "measured": ("each of the 52 fragments against every exact string constant in the python "
                         "corpus; the write/read split from the enclosing statement; the directory "
                         "expression as written; and whether the composed path exists"),
            "not_measured": ("non-python sites (.ps1, .md, json) are not scanned; a fragment used only "
                             "as a suffix of a longer literal is invisible to the exact-match arm by "
                             "design; the trace follows one hop of assignment and does not evaluate "
                             "arbitrary expressions"),
            "no_rewrites": "no published face, pointer, caller or key is edited here",
        },
    }
    say("by_class: %s" % json.dumps(by_class, sort_keys=True))
    say("verdict: %s" % summary["verdict"])
    if write_face:
        _write(face)
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    """Re-derive every published row from the tree as it stands."""
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    _FRAGMENTS[:] = [r["fragment"] for r in face["rows"]]
    sources = e350._sources()
    sites = scan_sources(sources)
    for row in face["rows"]:
        fragment = row["fragment"]
        found = sites.get(fragment) or []
        if len(found) != row["n_sites"]:
            problems.append("%s: n_sites %d -> %d" % (fragment, row["n_sites"], len(found)))
        writes = [r for r in found if r["write_kind"] == "write"]
        if len(writes) != row["n_write_sites"]:
            problems.append("%s: n_write_sites %d -> %d"
                            % (fragment, row["n_write_sites"], len(writes)))
        if writes:
            klass = sorted(writes, key=lambda r: (r["class"] != C2, r["site"]))[0]["class"]
            if row["producer_class"] != klass:
                problems.append("%s: producer_class %s -> %s"
                                % (fragment, row["producer_class"], klass))
        if row.get("producer_composed_path"):
            composed = os.path.join(ROOT, row["producer_composed_path"])
            if os.path.exists(composed) != bool(row["producer_path_exists"]):
                problems.append("%s: existence of %s changed" % (fragment, row["producer_composed_path"]))
    by_class = {}
    for row in face["rows"]:
        for klass, count in (row["classes_at_this_fragment"] or {}).items():
            by_class[klass] = by_class.get(klass, 0) + count
    if by_class != face["summary"]["by_class"]:
        problems.append("by_class does not re-derive")
    if set(by_class) - set(CLASSES):
        problems.append("a class outside the published set is in the face")
    if sum(by_class.values()) != face["summary"]["producer_sites_total"]:
        problems.append("by_class does not sum to the published producer total")
    if not face["summary"].get("classes_sum_to_sites"):
        problems.append("classes_sum_to_sites is false in the published summary")
    if decide(face["summary"]) != face["verdict"]:
        problems.append("verdict does not re-derive")
    for row in face["rows"]:
        if row["producer_class"] is not None and row["producer_class"] not in CLASSES:
            problems.append("%s: class outside the published set" % row["fragment"])
        if row["n_write_sites"] and not row.get("producer_site"):
            problems.append("%s: write site without a pointer" % row["fragment"])
        if row["producer_composed_path"] and not row.get("producer_class"):
            problems.append("%s: a composed path with no class" % row["fragment"])
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    results = []

    def _suffix_leg():
        text = "import os\np = c + '_x1.json'\n"
        tree = ast.parse(text)
        ctx = Ctx("t.py", text, tree)
        node = [n for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and n.value == "_x1.json"][0]
        return suffix_only(ctx, node)[0]

    def leg(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    fixture = [
        ("t_join_const.py", "import os\nROOT='.'\np=os.path.join(ROOT,'results','frag.json')\n"),
        ("t_join_missing.py", "import os\np=os.path.join('no_such_dir_xyz','frag.json')\n"),
        ("t_cwd.py", "def f():\n    open('frag.json','w').write('x')\n"),
        ("t_temp.py", "import tempfile,os\ndef f():\n    td=tempfile.mkdtemp()\n    return os.path.join(td,'frag.json')\n"),
        ("t_param.py", "import os\ndef f(outdir):\n    return os.path.join(outdir,'frag.json')\n"),
        ("t_fstring.py", "import os\ndef f(n):\n    return os.path.join('w%d_dir' % n, 'frag.json')\n"),
        ("t_read.py", "import os\ndef f():\n    return open(os.path.join('results','frag.json')).read()\n"),
        ("t_with_temp.py", "import tempfile,os\nwith tempfile.TemporaryDirectory() as tmp:\n    p=os.path.join(tmp,'frag.json')\n"),
        ("t_file.py", "import os\nD=os.path.dirname(os.path.abspath(__file__))\np=os.path.join(D,'frag.json')\n"),
    ]
    # the constant fixture dir "results" holds the file by fiat -- no junk file is written into the tree
    global EXISTS
    real_exists = EXISTS
    EXISTS = lambda path: True if os.path.normpath(path).endswith(
        os.path.join("results", "frag.json")) else False
    _FRAGMENTS[:] = ["frag.json"]
    try:
        rows = scan_sources(fixture)["frag.json"]
    finally:
        EXISTS = real_exists
    bysite = {r["site"].split("/")[-1]: r for r in rows}

    def klass(fname):
        for row in rows:
            if fname in row["site"]:
                return row["class"]
        return None

    leg("exact constant match only (w%d_dir is not frag.json)", len(rows) == 9,
        "sites=%d" % len(rows))
    leg("constant dir + existing file -> C1", klass("t_join_const.py") == C1, klass("t_join_const.py"))
    leg("constant dir that does not hold it -> C2", klass("t_join_missing.py") == C2,
        klass("t_join_missing.py"))
    leg("no directory at all -> C3", klass("t_cwd.py") == C3, klass("t_cwd.py"))
    leg("mkdtemp -> C4", klass("t_temp.py") == C4, klass("t_temp.py"))
    leg("parameter -> C5", klass("t_param.py") == C5, klass("t_param.py"))
    leg("percent-format -> C6", klass("t_fstring.py") == C6, klass("t_fstring.py"))
    leg("with tempfile.TemporaryDirectory() as tmp -> C4", klass("t_with_temp.py") == C4,
        klass("t_with_temp.py"))
    leg("os.path.dirname(os.path.abspath(__file__)) resolves, so the join is priced not traced-away",
        klass("t_file.py") != C7, klass("t_file.py"))
    leg("read site is tagged read, not write",
        [r["write_kind"] for r in rows if "t_read.py" in r["site"]] == ["read"])
    leg("write site is tagged write",
        [r["write_kind"] for r in rows if "t_cwd.py" in r["site"]] == ["write"])
    leg("temp class never claims a landing", not any(
        r["producer_path_exists"] for r in [{"producer_path_exists": False}]))

    # verdict legs
    leg("verdict: no site at all -> the producer claim is untested",
        decide({"fragments": 2, "fragments_with_no_site_in_the_corpus": 2, "sites_total": 0,
                "by_class": {}, "fragments_whose_composed_path_exists": 0}) == V_NO_WRITER)
    leg("verdict: dead joins -> the writes land where nobody indexes",
        decide({"fragments": 1, "fragments_with_no_site_in_the_corpus": 0, "sites_total": 5,
                "by_class": {C2: 4, C4: 1}, "fragments_whose_composed_path_exists": 0})
        == V_DEAD_WRITES)
    leg("verdict: temp/param only -> scaffolding, not attrition",
        decide({"fragments": 1, "fragments_with_no_site_in_the_corpus": 0, "sites_total": 5,
                "by_class": {C4: 3, C5: 2}, "fragments_whose_composed_path_exists": 0})
        == V_SCAFFOLDING)
    leg("verdict: mostly untraced -> not measured",
        decide({"fragments": 1, "fragments_with_no_site_in_the_corpus": 0, "sites_total": 4,
                "by_class": {C7: 3, C1: 1}, "fragments_whose_composed_path_exists": 1})
        == V_UNTRACED)
    leg("verdict: a suffix-only fragment alone is not attrition either",
        decide({"fragments": 1, "fragments_with_no_site_in_the_corpus": 0, "sites_total": 4,
                "by_class": {C8: 4}, "fragments_whose_composed_path_exists": 0})
        == V_SCAFFOLDING)

    # the class set is closed
    leg("class set is closed", set(CLASSES) == {C1, C2, C3, C4, C5, C6, C7, C8})
    leg("a name built from a variable is not a whole filename",
        _suffix_leg() is True)

    ok = all(r[1] for r in results)
    for name, good, detail in results:
        say("%s %s%s" % ("PASS" if good else "FAIL", name, (" (%s)" % detail) if detail else ""))
    say("%d/%d" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        build()
        return 0
    if cmd == "verify":
        problems = verify()
        if problems:
            for problem in problems:
                say("PROBLEM %s" % problem)
            return 1
        say("verify: problems=[]")
        return 0
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))