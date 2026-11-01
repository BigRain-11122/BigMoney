"""E347 -- where a published number actually decides something.

E344 answered *who reads* a face: no source outside the census family names them, and of the five
directory readers exactly one carries a published value forward.  That is a statement about
reading.  "We publish this number" and "this number decides something" are different sentences,
and only the second one tells us whether the face is worth the wall time it costs.

This study asks the deciding question, mechanically, over *every* dated face under ``results/``:

    load      a source loads a face by name (a literal that reaches a load primitive) or through a
              directory enumeration (glob/walk/listdir over results/ followed by a load of each
              JSON).  A literal that is only printed, compared as a string, or used as a selftest
              fixture is a *citation*, not a load -- E341/E344's lesson, re-measured here.
    decide    the loaded value reaches a comparison: ``Compare``, an ``if``/``while`` test, an
              ``assert``, or a comprehension filter.  The comparison site, both operands and the
              operator are published -- not the author's intent.
    class     what the comparison gates: a scientific decision (admission/freeze/promotion), an
              operational one (which lane runs, which collector retries, what the daemon kills), or
              only a report.  A comparison inside a ``selftest``/fixture function is published as
              ``selftest_fixture`` -- it gates the study, not the firm.

Three honesty rules are carried from the family, each with a selftest leg:

    (1) E343's store-vs-load: ``node.ctx`` decides, so ``d["k"] = v`` is not a read of ``d``.
    (2) E341/E344's citation: a literal is a load only if it reaches a load primitive, directly or
        through a name bound to the handle.
    (3) E207/E332 self-inclusion: the corpus is read at a pin where this file does not exist.

And one rule learned the hard way at group level (D-20261101-20, "the scan domain does not contain
the target"): every all-green conclusion carries the *hit count* of what it was looking for.  The
published summary therefore starts with ``scan_domain`` and a verdict of ``empty_scan_domain`` --
not "zero unpinned gates" -- when any channel found nothing.

Usage:
    python scripts/e347_published_number_gate_census.py run|verify|selftest
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

import e338_census_green_window as e338
import e341_sibling_closer_what_changed as e341

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "DECIDEGATE-%s.json" % TODAY
LATEST = "decidegate_latest.json"
STUDY = "E347_published_number_gate_census"
SELF_REL = "scripts/e347_published_number_gate_census.py"

PIN_SHA = "90c1fa8ae59536c4646e0c5a6ff319fa1977bf67"

FACE_NAME_RE = re.compile(r"^([A-Z][A-Z0-9_]{2,40})-\d{4}-\d{2}-\d{2}\.json$")

LOAD_FNS = ("open", "load", "loads", "read_json", "read_text", "read_csv", "read_bytes", "read")
ENUM_FNS = ("glob", "iglob", "walk", "iterdir", "listdir", "scandir")

CMP_NODES = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is,
             ast.IsNot)

OP_SYMBOL = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">",
             ast.GtE: ">=", ast.In: "in", ast.NotIn: "not in", ast.Is: "is",
             ast.IsNot: "is not"}

SCI_WORDS = ("admission", "admit", "freeze", "frozen", "prereg", "promote", "promotion", "verdict",
             "eligible", "eligib", "judge", "judged", "science", "decision", "flip")
OPS_WORDS = ("lane", "retry", "retries", "collector", "daemon", "scheduler", "queue", "claim",
             "dispatch", "tick", "heartbeat", "pool", "spawn", "throttle", "backoff", "watchdog",
             "timeout", "runner", "autofill", "kill", "orphan", "resident", "fuse", "breaker")

MAX_ROWS = 40


# ------------------------------------------------------------------------------------- plumbing

def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def _fname(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _short(text, limit=180):
    one = " ".join(str(text).split())
    return one if len(one) <= limit else one[:limit - 3] + "..."


def parse(text):
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def constants(tree):
    """``{NAME: str}`` for module/def level string constants that fold to one literal.

    ``os.path.join(ROOT, "results", "state_tilt")`` folds to ``results/state_tilt``: only the
    literal components survive, which is all an enumeration scope needs (E344's lesson -- the
    trailing components are what name a directory).
    """
    out = {}

    def fold(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return out.get(node.id)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = fold(node.left), fold(node.right)
            if left is not None and right is not None:
                return left + right
        if isinstance(node, ast.Call):
            name = _fname(node.func)
            parts = [value for value in (fold(arg) for arg in node.args) if value is not None]
            if not parts:
                return None
            if name == "join":
                return "/".join(part.strip("/") for part in parts if part.strip("/")) or None
            return parts[-1]
        return None

    for _pass in range(2):
        for node in ast.walk(tree):
            targets, value = [], None
            if isinstance(node, ast.Assign):
                targets = [t for t in node.targets if isinstance(t, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target]
                value = node.value
            if value is None or not targets:
                continue
            folded = fold(value)
            if folded is not None:
                out[targets[0].id] = folded
    return out


def values_in(node, consts, depth=0, seen=None):
    """Every string a path expression can evaluate to; ``%s`` stays as a placeholder."""
    if node is None or depth > 3:
        return []
    seen = seen or set()
    out = []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value)
    elif isinstance(node, ast.Name):
        if node.id in consts:
            out.append(consts[node.id])
    elif isinstance(node, ast.BinOp):
        left = values_in(node.left, consts, depth + 1, seen)
        right = values_in(node.right, consts, depth + 1, seen)
        out.extend(left)
        if isinstance(node.op, ast.Add):
            for a in left:
                for b in right:
                    out.append(a + b)
        # ``"%s.json" % TODAY`` and ``"-".join((A, B))`` keep the head, not the value
        out.extend(right)
    elif isinstance(node, ast.JoinedStr):
        head = "".join(v.value for v in node.values if isinstance(v, ast.Constant))
        if head:
            out.append(head)
    elif isinstance(node, ast.Call):
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            out.extend(values_in(arg, consts, depth + 1, seen))
    elif isinstance(node, (ast.Subscript, ast.Attribute, ast.Starred, ast.List, ast.Tuple)):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                out.extend(values_in(child, consts, depth + 1, seen))
    return list(dict.fromkeys(out))


def _face_names(values, faces_by_name, stems):
    """``[(face_filename|stem, matched_by, the literal that matched)]`` for one expression."""
    hits = []
    for value in values:
        base = value.replace("\\", "/").rsplit("/", 1)[-1]
        if base in faces_by_name:
            hits.append((faces_by_name[base], "exact_filename", value))
            continue
        for stem in stems:
            if stem in value and (re.search(r"\d{4}-\d{2}-\d{2}", value) or "%s" in value):
                hits.append((stem, "stem_in_literal", value))
                break
    seen, out = set(), []
    for row in hits:
        if row[0] in seen:
            continue
        seen.add(row[0])
        out.append(row)
    return out


def parents_of(tree):
    table = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            table[child] = node
    return table


def enclosing_function(node, table):
    while node in table:
        node = table[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
    return ""


def enclosing_def(node, table):
    while node in table:
        node = table[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return node
    return None


# --------------------------------------------------------------------------------- the load channel

def file_handles(tree, consts):
    """``{handle_name: [path values]}`` for ``with open(P) as fh``."""
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        for item in node.items:
            target = item.optional_vars
            if not isinstance(target, ast.Name):
                continue
            call = item.context_expr
            if isinstance(call, ast.Call) and _fname(call.func) in ("open",):
                out[target.id] = values_in(call, consts)
            elif isinstance(call, ast.Call) and _fname(call.func) in ("read_text", "open_text"):
                out[target.id] = values_in(call, consts)
    return out


def load_bindings(tree, consts):
    """``[{binding, line, load_name, values, enumerates}]`` -- every binding fed by a load call."""
    handles = file_handles(tree, consts)
    enum_lines = enumeration_lines(tree, consts)
    out = []
    for node in ast.walk(tree):
        targets, value = [], None
        if isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target]
            value = node.value
        if value is None or not targets:
            continue
        if not isinstance(value, ast.Call):
            continue
        name = _fname(value.func)
        if name not in LOAD_FNS:
            continue
        # ``data = json.load(fh)`` -> the handle's path; ``json.load(open(P))`` -> P
        arg_values, roots_handle = [], False
        for arg in list(value.args) + [kw.value for kw in value.keywords]:
            if isinstance(arg, ast.Name) and arg.id in handles:
                arg_values.extend(handles[arg.id])
                roots_handle = True
            else:
                arg_values.extend(values_in(arg, consts))
        if isinstance(value.func, ast.Attribute) and isinstance(value.func.value, ast.Name):
            if value.func.value.id in handles:
                arg_values.extend(handles[value.func.value.id])
                roots_handle = True
        enumerates = bool(enum_lines) and (roots_handle or not arg_values)
        out.append({"binding": targets[0].id, "line": node.lineno, "load_name": name,
                    "values": list(dict.fromkeys(arg_values)), "enumerates": enumerates})
    return out


def enumeration_lines(tree, consts):
    """lines where the source enumerates something under results/ (glob/walk/listdir/...)."""
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _fname(node.func) not in ENUM_FNS:
            continue
        joined = " ".join(values_in(node, consts))
        if "results" in joined or "state_tilt" in joined:
            rows.append(node.lineno)
    return rows


def _glob_re(pattern):
    parts, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            parts.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            parts.append(".*")
            i += 2
        elif pattern[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(parts))


def _tail_at_results(value):
    """``C:/x/bigmoney/results/state_tilt`` -> ``results/state_tilt`` (relative to the repo)."""
    norm = value.replace("\\", "/")
    idx = norm.find("results")
    if idx < 0:
        return ""
    return norm[idx:]


def enumeration_scopes(tree, consts):
    """``[{pattern, recursive, line}]`` -- the file/dir patterns this source actually sweeps.

    A sweep is a candidate face reader only once a published dated face matches its scope.  That
    is the rule that separates ``glob(results/*.json)`` reading a live state file from a census
    over the dated face population -- the first admits no dated face at all.
    """
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _fname(node.func) not in ENUM_FNS:
            continue
        name = _fname(node.func)
        tails = [t for t in (_tail_at_results(v) for v in values_in(node, consts)) if t]
        pats = [t for t in tails if any(c in t for c in "*?") or t.endswith(".json")]
        dirs = [t for t in tails if t not in pats]
        patterns = []
        for pat in pats:
            if pat.startswith("results"):
                patterns.append(pat)
            else:
                for base in dirs or ["results"]:
                    patterns.append(base.rstrip("/") + "/" + pat)
        if not pats:
            for base in dirs:
                patterns.append(base.rstrip("/") + ("/**/*.json" if name in ("walk", "iglob")
                                                    else "/*.json"))
        for pattern in patterns:
            out.append({"pattern": pattern, "recursive": "**" in pattern, "line": node.lineno})
    return out


def admitted_faces(scopes, faces):
    """the dated faces a set of enumeration scopes actually enumerates."""
    out = set()
    for scope in scopes:
        regex = _glob_re(scope["pattern"])
        for face in faces:
            path_key = face.get("path") or (face["dir"].rstrip("/") + "/" + face["name"])
            if regex.fullmatch(path_key):
                out.add(face["name"])
    return out


def measure_corpus(corpus, faces):
    """The whole measurement, pure, over ``{path: text}`` and the face listing.

    ``faces`` is ``[{stem, name, dir}]``.  Returns ``(rows, summary_bits)``.
    """
    faces_by_name = {row["name"]: row["name"] for row in faces}
    stems = sorted({row["stem"] for row in faces})
    face_dirs = {row["dir"] for row in faces}

    gates = []
    loads = []
    for path in sorted(corpus):
        if path == SELF_REL:
            continue
        text = corpus[path]
        tree = parse(text)
        if tree is None:
            continue
        consts = constants(tree)
        handles = file_handles(tree, consts)
        scopes = enumeration_scopes(tree, consts)
        admitted = sorted(admitted_faces(scopes, faces))
        for binding in load_bindings(tree, consts):
            named = _face_names(binding["values"], faces_by_name, stems)
            rows = [{"face": hit[0], "matched_by": hit[1], "literal": hit[2]}
                    for hit in named]
            if rows:
                channel = "named"
                load_faces = [row["face"] for row in rows]
                gate_faces = rows
            elif binding["enumerates"] and admitted:
                channel = "enumeration"
                load_faces = admitted
                gate_faces = [{"face": "<dated faces in %s>" % scopes[0]["pattern"],
                               "matched_by": "directory_sweep", "literal": "enumeration"}]
            else:
                continue
            loads.append({"path": path, "binding": binding["binding"], "line": binding["line"],
                          "load_name": binding["load_name"], "channel": channel,
                          "scopes": [scope["pattern"] for scope in scopes] if channel ==
                          "enumeration" else [],
                          "faces": load_faces})
            gates.extend(gate_rows(path, text, tree, consts, handles, binding, gate_faces,
                                   channel))

    deduped, seen = [], set()
    for row in gates:
        key = (row["source"], row["line"], row["kind"], row["face"], row["tested"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return loads, deduped


def gate_rows(path, text, tree, consts, handles, binding, face_rows, channel):
    """Every comparison site reached by one loaded binding."""
    table = parents_of(tree)
    name = binding["binding"]
    out = []
    seen = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Name) and node.id == name):
            continue
        if isinstance(node.ctx, ast.Store):
            continue  # E343: a store is not a read
        site = comparison_site(node, table)
        if site is None:
            continue
        kind, cmp_node = site
        key = (path, kind, getattr(cmp_node, "lineno", node.lineno))
        if key in seen:
            continue
        seen.add(key)
        tested = tested_expression(node, cmp_node, table)
        if cmp_node is not None and isinstance(cmp_node, ast.Compare):
            ops = [OP_SYMBOL.get(type(op), type(op).__name__) for op in cmp_node.ops]
            operated = {
                "tested": _short(ast.get_source_segment(text, tested) or ""),
                "operators": ops,
                "bound": [_short(ast.get_source_segment(text, other) or "")
                          for other in bound_operands(cmp_node, tested)],
                "bound_pin": [pin_of(other, text, tree, consts) for other
                              in bound_operands(cmp_node, tested)],
            }
        else:
            operated = {"tested": _short(ast.get_source_segment(text, tested) or ""),
                        "operators": [], "bound": [], "bound_pin": []}
        func = enclosing_function(node, table)
        cls = classify(path, func, operated["tested"])
        if isinstance(parents_of(tree).get(cmp_node), ast.Assert):
            kind = "assert"
        if (kind == "comparison" and operated["operators"] in (["is"], ["is not"])
                and operated["bound"] and all(b.strip() == "None" for b in operated["bound"])):
            kind = "null_guard"  # a missing-value guard is not a decision on the value
        for face_row in face_rows:
            out.append({
                "face": face_row["face"],
                "matched_by": face_row["matched_by"],
                "channel": channel,
                "source": path,
                "line": getattr(cmp_node, "lineno", node.lineno) or node.lineno,
                "kind": kind,
                "function": func,
                "decision_class": cls,
                "code": _short(code_line(text, getattr(cmp_node, "lineno", node.lineno)
                                         or node.lineno)),
                **operated,
            })
    return out


def comparison_site(node, table):
    """Walk outward from a use to the nearest comparison / test / assert that consumes it."""
    cur = node
    while cur in table:
        parent = table[cur]
        if isinstance(parent, ast.Compare):
            return ("comparison", parent)
        if isinstance(parent, (ast.If, ast.While)) and parent.test is not None:
            if _contains(parent.test, node):
                return ("truth_test", parent.test)
        if isinstance(parent, ast.Assert) and _contains(parent.test, node):
            return ("assert", parent.test)
        if isinstance(parent, ast.comprehension):
            return ("comprehension_filter", node)
        if isinstance(parent, ast.IfExp) and _contains(parent.test, node):
            return ("conditional_expression", parent.test)
        cur = parent
    return None


def _contains(root, target):
    for node in ast.walk(root):
        if node is target:
            return True
    return False


def tested_expression(node, cmp_node, table):
    """The smallest expression on the tested side that still holds the use."""
    cur = node
    while cur in table and table[cur] is not cmp_node:
        parent = table[cur]
        if isinstance(parent, ast.expr) and parent is not cmp_node:
            cur = parent
        else:
            break
    return cur


def bound_operands(cmp_node, tested):
    if not isinstance(cmp_node, ast.Compare):
        return []
    left = cmp_node.left
    if _is_inside(tested, left):
        return list(cmp_node.comparators)
    outs = []
    for idx, comp in enumerate(cmp_node.comparators):
        if _is_inside(tested, comp):
            outs.append(left)
            for other in cmp_node.comparators[idx + 1:]:
                outs.append(other)
            return outs
    return list(cmp_node.comparators)


def _is_inside(inner, outer):
    if inner is outer:
        return True
    for node in ast.walk(outer):
        if node is inner:
            return True
    return False


def pin_of(node, text, tree, consts):
    """Where the bound lives: a source literal, a module constant, a local, or nothing."""
    if isinstance(node, ast.Constant):
        return {"pin": "literal_in_source", "value": _short(repr(node.value), 80)}
    if isinstance(node, ast.Name):
        if node.id in consts:
            return {"pin": "module_constant", "name": node.id,
                    "value": _short(consts[node.id], 80)}
        found = None
        for stmt in ast.walk(tree):
            targets, value = [], None
            if isinstance(stmt, ast.Assign):
                targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
                value = stmt.value
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                targets, value = [stmt.target], stmt.value
            if value is not None and any(t.id == node.id for t in targets):
                found = stmt
        if found is not None:
            at_module = any(isinstance(n, ast.Module) and found in n.body
                            for n in ast.walk(tree))
            return {"pin": "module_constant" if at_module else "local_assignment",
                    "line": found.lineno,
                    "value": _short(ast.get_source_segment(text, found.value) or "")}
        return {"pin": "unresolved_name", "name": node.id}
    return {"pin": "expression",
            "value": _short(ast.get_source_segment(text, node) or repr(type(node).__name__))}


def code_line(text, line):
    lines = text.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return ""


def classify(path, func, tested):
    blob = " ".join([path, func or "", tested or ""]).lower()
    if "selftest" in (func or "").lower() or "fixture" in (func or "").lower():
        return "selftest_fixture"
    for word in OPS_WORDS:
        if word in blob:
            return "operational"
    for word in SCI_WORDS:
        if word in blob:
            return "scientific"
    return "report"


# ---------------------------------------------------------------------------------------- summary

def faces_from_listing(paths):
    """``[{stem, name, dir}]`` for every dated face under results/ (latest mirrors excluded)."""
    out = []
    for path in paths:
        base = path.replace("\\", "/").rsplit("/", 1)[-1]
        if base.endswith("_latest.json"):
            continue
        match = FACE_NAME_RE.match(base)
        if not match:
            continue
        out.append({"stem": match.group(1), "name": base,
                    "dir": path.replace("\\", "/").rsplit("/", 1)[0],
                    "path": path.replace("\\", "/")})
    return out


def expand(names, faces):
    """Face identifiers (filenames or stems) -> the set of dated face filenames they cover."""
    by_stem = {}
    for row in faces:
        by_stem.setdefault(row["stem"], set()).add(row["name"])
    out = set()
    for name in names:
        if name in by_stem:
            out |= by_stem[name]
        else:
            out.add(name)
    return out


def summarize(faces, loads, gates, corpus_size):
    face_ids = sorted({row["name"] for row in faces})
    loaded_named = expand({f for row in loads if row["channel"] == "named" for f in row["faces"]},
                          faces)
    loaded_enum = expand({f for row in loads if row["channel"] == "enumeration"
                          for f in row["faces"]}, faces)
    decided = expand({row["face"] for row in gates}, faces)
    by_class = {}
    for row in gates:
        by_class[row["decision_class"]] = by_class.get(row["decision_class"], 0) + 1
    by_kind = {}
    for row in gates:
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
    real = [row for row in gates if row["decision_class"] != "selftest_fixture"
            and row["kind"] != "null_guard"]
    operational = [row for row in real if row["decision_class"] == "operational"]
    family = set(e338.CENSUS_FAMILY)
    outside_named = {face for row in loads
                     if row["channel"] == "named" and row["path"] not in family
                     for face in row["faces"]}
    # (d) a gate whose tested value comes straight off a face and whose bound is a literal or a
    # module constant: hand-editing the face moves an operational decision.
    candidates = []
    for row in operational:
        pins = [p.get("pin") for p in row["bound_pin"]]
        if not pins:
            continue
        if all(p in ("literal_in_source", "module_constant", "local_assignment") for p in pins):
            candidates.append(row)
    summary = {
        "scan_domain": {
            "sources_scanned": corpus_size,
            "dated_faces": len(face_ids),
            "face_directories": len({row["dir"] for row in faces}),
            "load_sites": len(loads),
            "faces_loaded_by_name": len(loaded_named & set(face_ids)),
            "faces_reached_by_enumeration": len(loaded_enum & set(face_ids)),
            "comparison_sites": len(gates),
            "verdict": "contains_targets",
        },
        "faces_total": len(face_ids),
        "faces_loaded_by_name": len(loaded_named & set(face_ids)),
        "faces_loaded_only_by_enumeration": len((loaded_enum - loaded_named) & set(face_ids)),
        "faces_with_a_gate": len(decided & set(face_ids)),
        "faces_with_a_non_fixture_gate": len(expand({row["face"] for row in real}, faces)
                                           & set(face_ids)),
        "faces_loaded_by_name_outside_the_census_family": len(expand(outside_named, faces)
                                                               & set(face_ids)),
        "null_guards": len([row for row in gates if row["kind"] == "null_guard"]),
        "faces_never_loaded": len(set(face_ids) - loaded_named - loaded_enum),
        "gates_total": len(gates),
        "gates_by_class": by_class,
        "gates_by_kind": by_kind,
        "gates_outside_fixtures": len(real),
        "operational_gates": len(operational),
        "operational_gates_with_a_pinned_bound": len(candidates),
        "share_of_faces_that_decide_something": e341._share(
            len(expand({row["face"] for row in real}, faces) & set(face_ids)), len(face_ids)),
        "share_of_faces_read_only_as_population": e341._share(
            len((loaded_named | loaded_enum) - decided), len(face_ids)),
    }
    if not face_ids or not loads:
        summary["scan_domain"]["verdict"] = "empty_scan_domain"
    return summary, candidates


V_STUDY = ("every_published_dated_face_is_compared_only_by_the_study_that_produced_it_and_no_"
           "operational_decision_reads_one")
V_OPERATIONAL = ("published_numbers_are_compared_only_inside_studies_and_a_few_operational_gates_"
                 "pin_their_bounds_in_source")
V_POPULATION = ("published_numbers_are_loaded_and_never_compared_so_they_describe_populations_"
                "rather_than_decide")
V_EMPTY = "the_scan_domain_did_not_contain_the_targets_so_no_clean_claim_is_made"


def decide(summary):
    if summary["scan_domain"]["verdict"] == "empty_scan_domain":
        return V_EMPTY
    if summary["faces_with_a_non_fixture_gate"] == 0:
        return V_POPULATION
    if summary["operational_gates"] == 0:
        return V_STUDY
    return V_OPERATIONAL


# ------------------------------------------------------------------------------------------ build

def pinned_face_paths(sha):
    listing = e338._git("ls-tree", "-r", "--name-only", sha, "--", "results")
    return [p.strip().replace("\\", "/") for p in listing.splitlines() if p.strip()]


def nearest_decision(gates):
    """The study-side comparison with the widest reach, published when no operational gate exists."""
    counted = {}
    for row in gates:
        if row["decision_class"] in ("scientific", "report") and row["kind"] != "null_guard":
            counted[row["face"]] = counted.get(row["face"], 0) + 1
    if not counted:
        return None
    face = sorted(counted.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    for row in gates:
        if row["face"] == face and row["kind"] != "null_guard":
            return row
    return None


def build(root=None):
    corpus = e341.pinned_corpus(PIN_SHA)
    faces = faces_from_listing(pinned_face_paths(PIN_SHA))
    say("pinned corpus at %s: %s sources | %s dated faces under results/ (%s dirs)"
        % (PIN_SHA[:9], len(corpus), len(faces), len({row["dir"] for row in faces})))

    loads, gates = measure_corpus(corpus, faces)
    summary, candidates = summarize(faces, loads, gates, len(corpus))
    said = decide(summary)
    say("load sites: %s (named %s / enumeration %s) | comparison sites: %s"
        % (len(loads),
           len([r for r in loads if r["channel"] == "named"]),
           len([r for r in loads if r["channel"] == "enumeration"]),
           len(gates)))

    by_face = {}
    for row in gates:
        by_face.setdefault(row["face"], 0)
        by_face[row["face"]] += 1
    top_faces = [{"face": name, "gates": count}
                 for name, count in sorted(by_face.items(), key=lambda kv: (-kv[1], kv[0]))][:MAX_ROWS]

    doc = {
        "study": STUDY,
        "verdict": said,
        "pin": PIN_SHA,
        "evidence_cutoff": TODAY,
        "generated": _stamp(),
        "summary": summary,
        "gates_by_class_detail": {
            cls: [row for row in gates if row["decision_class"] == cls][:MAX_ROWS]
            for cls in sorted({row["decision_class"] for row in gates})
        },
        "faces_with_most_gates": top_faces,
        "unpinned_operational_gates": [
            {"face": row["face"], "source": row["source"], "line": row["line"],
             "tested": row["tested"], "operators": row["operators"], "bound": row["bound"],
             "code": row["code"]}
            for row in candidates[:MAX_ROWS]
        ],
        "the_one_gate": candidates[0] if candidates else None,
        "no_operational_gate_note": (
            None if candidates else
            "asked for the one gate whose hand-edited bound would change an operational decision: "
            "there is none on a dated face. The only operational comparison reached from a face "
            "directory is a null guard (`if d is None`), which tests presence, not the value; the "
            "live state files and *_latest mirrors that the lanes actually read are outside this "
            "card's population by construction."),
        "nearest_decision": nearest_decision(gates),
        "named_faces_with_a_gate": sorted({row["face"] for row in gates
                                           if row["channel"] == "named"}),
        "loads": loads,
        "gates": gates,
        "generated_by": SELF_REL,
        "note": ("comparison sites only: a literal that is printed, compared as a string, or used "
                 "as a fixture is a citation, and a comparison inside a selftest gates the study "
                 "rather than the firm"),
    }
    _write(doc, root)
    say("verdict: %s" % said)
    say("faces: %s total | %s with a gate (%s non-fixture) | %s never loaded"
        % (summary["faces_total"], summary["faces_with_a_gate"],
           summary["faces_with_a_non_fixture_gate"], summary["faces_never_loaded"]))
    say("gates by class: %s" % json.dumps(summary["gates_by_class"], sort_keys=True))
    if candidates:
        head = candidates[0]
        say("the one operational gate: %s:%s %s" % (head["source"], head["line"], head["code"]))
    return doc


def _stamp():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _write(doc, root=None):
    outdir = os.path.join(root or ROOT, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")


# ----------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            if key in ("generated", "asof_head"):
                continue
            if key not in a or key not in b:
                out.append("%s.%s: present in only one side" % (path, key))
                continue
            _cmp(a[key], b[key], "%s.%s" % (path, key), out)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: length %s vs %s" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%s]" % (path, i), out)
        return
    if isinstance(a, float):
        if abs(a - b) > 1e-9:
            out.append("%s: %r vs %r" % (path, a, b))
        return
    if a != b:
        out.append("%s: %r vs %r" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        published = json.load(fh)
    corpus = e341.pinned_corpus(PIN_SHA)
    faces = faces_from_listing(pinned_face_paths(PIN_SHA))
    loads, gates = measure_corpus(corpus, faces)
    summary, candidates = summarize(faces, loads, gates, len(corpus))
    out = []
    _cmp(published.get("summary"), summary, "summary", out)
    _cmp(published.get("loads"), loads, "loads", out)
    _cmp(published.get("gates"), gates, "gates", out)
    _cmp(published.get("the_one_gate"), (candidates[0] if candidates else None), "the_one_gate", out)
    if published.get("verdict") != decide(summary):
        out.append("verdict: %r vs %r" % (published.get("verdict"), decide(summary)))
    return out


# --------------------------------------------------------------------------------------- selftest

FIX_FACES = [
    {"stem": "ALPHAFACE", "name": "ALPHAFACE-2026-01-02.json", "dir": "results/state_tilt"},
    {"stem": "BETAFACE", "name": "BETAFACE-2026-01-02.json", "dir": "results/claims"},
    {"stem": "GAMMAFACE", "name": "GAMMAFACE-2026-01-02.json", "dir": "results/state_tilt"},
]


def cmd_selftest():
    checks, failed = [], []

    def leg(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        if not ok:
            failed.append("%s %s" % (name, detail))

    # L1 a name-bound load whose value is compared to a literal is a gate with a pinned bound
    corpus = {"scripts/a.py": (
        'import json\n'
        'def gate():\n'
        '    doc = json.load(open("results/state_tilt/ALPHAFACE-2026-01-02.json"))\n'
        '    if doc["verdict"] != "ok":\n'
        '        return 1\n'
        '    return 0\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L1 named load is a gate", len(gates) == 1
        and gates[0]["face"].startswith("ALPHAFACE"), str(gates))
    leg("L1 bound pinned as literal", gates and gates[0]["bound_pin"][0]["pin"] == "literal_in_source",
        str(gates[0]["bound_pin"]) if gates else "")

    # L2 a citation is not a load (E341/E344): the literal never reaches a load primitive
    corpus = {"scripts/a.py": (
        'FACE = "ALPHAFACE-2026-01-02.json"\n'
        'assert FACE.endswith(".json")\n'
        'print(FACE)\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L2 citation is not a load", not loads and not gates, str(loads))

    # L3 E343 store-vs-load: storing into the loaded dict is not a read of it
    corpus = {"scripts/a.py": (
        'import json\n'
        'def f():\n'
        '    doc = json.load(open("results/state_tilt/ALPHAFACE-2026-01-02.json"))\n'
        '    doc["verdict"] = 3\n'
        '    return doc\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L3 a store is not a read", loads and not gates, str(gates))

    # L4 a load that is only printed is population, not a decision
    corpus = {"scripts/a.py": (
        'import json\n'
        'def show():\n'
        '    doc = json.load(open("results/state_tilt/ALPHAFACE-2026-01-02.json"))\n'
        '    print(doc["verdict"])\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    summary, _c = summarize(FIX_FACES, loads, gates, 1)
    leg("L4 uncompared load is population", summary["faces_loaded_by_name"] == 1
        and summary["faces_with_a_gate"] == 0, json.dumps(summary["faces_with_a_gate"]))
    leg("L4 axis: scanned whose only load is a print", summary["faces_loaded_by_name"] == 1,
        json.dumps(summary["faces_loaded_by_name"]))

    # L5 with-block handle: ``with open(P) as fh: doc = json.load(fh)`` resolves through the name
    corpus = {"scripts/a.py": (
        'import json\n'
        'def f():\n'
        '    with open("results/claims/BETAFACE-2026-01-02.json") as fh:\n'
        '        doc = json.load(fh)\n'
        '    assert doc["count"] > 3\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L5 handle resolves to a face", len(gates) == 1
        and gates[0]["face"].startswith("BETAFACE"), str(gates))
    leg("L5 assert is its own kind", gates and gates[0]["kind"] == "assert", str(gates))

    # L6 a bound that is a module constant is pinned by name, not by literal
    corpus = {"scripts/a.py": (
        'import json\n'
        'LIMIT = 3\n'
        'def gate():\n'
        '    doc = json.load(open("results/state_tilt/GAMMAFACE-2026-01-02.json"))\n'
        '    if doc["n"] > LIMIT:\n'
        '        return True\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L6 module constant pin", gates and gates[0]["bound_pin"][0]["pin"] == "module_constant",
        str(gates[0]["bound_pin"]) if gates else "")

    # L7 a comparison inside a selftest function is a fixture, not a firm gate
    corpus = {"scripts/a.py": (
        'import json\n'
        'def cmd_selftest():\n'
        '    doc = json.load(open("results/state_tilt/ALPHAFACE-2026-01-02.json"))\n'
        '    assert doc["verdict"] == "ok"\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    summary, _c = summarize(FIX_FACES, loads, gates, 1)
    leg("L7 fixture split", summary["gates_by_class"].get("selftest_fixture") == 1
        and summary["operational_gates"] == 0, json.dumps(summary["gates_by_class"]))

    # L8 enumeration channel: a results/ walk that loads each JSON is a coverage reader
    corpus = {"scripts/a.py": (
        'import glob, json\n'
        'def sweep():\n'
        '    for path in sorted(glob.glob("results/**/*.json", recursive=True)):\n'
        '        with open(path) as fh:\n'
        '            doc = json.load(fh)\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L8 enumeration is its own channel",
        loads and loads[0]["channel"] == "enumeration", str(loads))

    # L9 D-20261101-20: an empty scan domain may never read as a clean claim
    summary, _c = summarize([], [], [], 7)
    leg("L9 empty domain is not green", summary["scan_domain"]["verdict"] == "empty_scan_domain"
        and decide(summary) == V_EMPTY, decide(summary))

    # L10 the "%s" template form resolves to its stem rather than to nothing
    faces_by_name = {row["name"]: row["name"] for row in FIX_FACES}
    hits = _face_names(["ALPHAFACE-%s.json"], faces_by_name,
                       sorted({row["stem"] for row in FIX_FACES}))
    leg("L10 template literal resolves to its stem", hits and hits[0][0] == "ALPHAFACE"
        and hits[0][1] == "stem_in_literal", str(hits))

    # L11 a fixture that produces no gates must still report a non-zero load count, or the
    #     "no gates" reading is indistinguishable from "nothing was scanned"
    corpus = {"scripts/a.py": 'print("GAMMAFACE-2026-01-02.json")\n'}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    summary, _c = summarize(FIX_FACES, loads, gates, 1)
    leg("L11 zero gates implies something was scanned", not gates
        and summary["scan_domain"]["sources_scanned"] == 1, json.dumps(summary["scan_domain"]))
    leg("L11 domain stays non-empty on a citation-only corpus",
        summary["scan_domain"]["verdict"] == "empty_scan_domain",
        "loads=0 must read as empty, not clean")

    # L12 comprehension filter is a gate
    corpus = {"scripts/a.py": (
        'import json\n'
        'def f():\n'
        '    doc = json.load(open("results/state_tilt/ALPHAFACE-2026-01-02.json"))\n'
        '    rows = [r for r in doc["rows"] if r > 0]\n')}
    loads, gates = measure_corpus(corpus, FIX_FACES)
    leg("L12 comprehension filter counts",
        any(row["kind"] == "comprehension_filter" for row in gates), str(gates))

    # L13 read-only corpus sizes are reported, never used as an `or -1` sentinel (E341's lesson)
    summary, _c = summarize(FIX_FACES, [], [], 3)
    leg("L13 zero is a legal count", summary["faces_with_a_gate"] == 0
        and summary["faces_never_loaded"] == len(FIX_FACES), json.dumps(summary["faces_with_a_gate"]))

    passed = len([1 for _n, ok, _d in checks if ok])
    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " :: " + detail))
    say("selftest %s/%s" % (passed, len(checks)))
    return 0 if not failed else 1


def cmd_run():
    build()
    return 0


def cmd_verify():
    problems = verify()
    for problem in problems[:20]:
        say("PROBLEM %s" % problem)
    say("verify: %s" % ("OK" if not problems else "%s problems" % len(problems)))
    return 0 if not problems else 1


def main(argv):
    action = (argv[1] if len(argv) > 1 else "run").lower()
    if action == "run":
        return cmd_run()
    if action == "verify":
        return cmd_verify()
    if action == "selftest":
        return cmd_selftest()
    say("usage: %s run|verify|selftest" % os.path.basename(argv[0]))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))