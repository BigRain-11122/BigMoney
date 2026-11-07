"""E516 -- is a function local the only carrier of the population a surface receives?

E513 (r1541 bm-b) reported that 58 of the 84 bindings it published as "module constants"
are in fact locals of the function that makes the call (80 of 123 sites).  A local is not a
population a reader can reconstruct: it is produced inside the call and thrown away.  This
study asks, per binding, whether some caller of the surface hands over a real population
anyway -- i.e. it separates

  readable_from_a_call_site        some call site passes a literal container or a name that
                                  resolves to a module-scope constant of the calling module
  supplied_only_by_the_default     every call site omits the argument, so the population is
                                  the parameter default and nothing else
  readable_only_through_the_local  call sites exist but every one of them passes a local, a
                                  call result or something computed at the site
  never_supplied                   the surface has no call site at all in this tree

and it publishes which of those locals are themselves produced by a call into another
in-repo module, so that "a caller passes a constant" stops counting a transient value.

Population: E508's CALLERSUPPLIED face (arguments whose kind is a module constant), resolved
through E513's own resolver.  Only bindings whose resolution scope is a local of the
enclosing function enter this study; the count is asserted against E513's published numbers
so the two faces cannot drift apart silently.

Run:  python scripts/e516_local_carrier.py [build|check|verify|selftest]
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e513_constant_origin as e513  # noqa: E402  (reuse corpus + resolver, do not clone)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "localcarrier_latest.json"
DATED_PREFIX = "LOCALCARRIER"
DATE_STAMP = "2026-11-08"
CARD = "E516-WHICH-FUNCTION-LOCAL-THAT-E508-CALLED-A-MODULE-CONSTANT-IS-THE-ONLY-CARRIER-OF-A-POPULATION"
STUDY = "E516_local_carrier"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "CONSTANTORIGIN-2026-11-08.json")
POPULATION_SOURCE = (
    "results/state_tilt/CALLERSUPPLIED-2026-11-07.json arguments whose kind is a module "
    "constant, resolved with E513's resolver (e513_constant_origin.resolve); only bindings "
    "whose scope is a local of the enclosing function are in this study"
)
SELF_EXCLUDED = ("e516_", "run_e516", "_e516", "_r1544_leg516")

# ---- what a call site passes -------------------------------------------------------
AR_LITERAL = "a_literal_container_written_at_the_call_site"
AR_MODULE_CONSTANT = "a_name_that_resolves_to_a_module_scope_constant_of_the_caller"
AR_OTHER_MODULE = "a_name_that_resolves_to_another_module"
AR_LOCAL = "a_local_bound_in_the_calling_function"
AR_CALL = "a_call_result_at_the_call_site"
AR_COMPUTED = "an_expression_computed_at_the_call_site"
AR_DEFAULT = "the_argument_is_omitted_so_the_parameter_default_stands"
ARG_VOCAB = (AR_LITERAL, AR_MODULE_CONSTANT, AR_OTHER_MODULE, AR_LOCAL, AR_CALL,
             AR_COMPUTED, AR_DEFAULT)

# ---- what a binding's callers amount to --------------------------------------------
CC_CALL_SITE = "readable_from_a_call_site"
CC_DEFAULT = "supplied_only_by_the_default"
CC_LOCAL = "readable_only_through_the_local"
CC_NEVER = "never_supplied"
CC_VOCAB = (CC_CALL_SITE, CC_DEFAULT, CC_LOCAL, CC_NEVER)

V_CALL_SITE = ("every_local_carried_binding_still_has_a_call_site_that_hands_over_a_real_"
               "population_so_the_local_is_a_fallback_not_the_only_carrier")
V_MIXED = ("some_local_carried_bindings_are_still_fed_a_real_population_by_a_caller_and_"
           "some_are_not_so_the_headline_has_to_be_read_row_by_row")
V_LOCAL_ONLY = ("no_local_carried_binding_is_ever_handed_a_population_by_a_caller_the_value_"
                "is_always_produced_inside_the_call")
V_NONE = "this_tree_has_no_local_carried_binding_to_measure"
VERDICT_VOCAB = (V_CALL_SITE, V_MIXED, V_LOCAL_ONLY, V_NONE)

HANDOFF_KINDS = (e513.HP_OTHER_MODULE_CALL, e513.HP_OTHER_MODULE_CONSTANT)


def _is_self(rel):
    name = os.path.basename(rel)
    return name.startswith(SELF_EXCLUDED)


def _read(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _short(node):
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover - py<3.9
        return type(node).__name__
    return text if len(text) <= 120 else text[:117] + "..."


class LocalCorpus(e513.Corpus):
    """E513's corpus plus the parsed trees, so call sites can be indexed in one pass."""

    def __init__(self, root):
        self.trees = {}
        e513.Corpus.__init__(self, root)
        for module, rel in self.by_module.items():
            try:
                self.trees[module] = e513._parse(_read(os.path.join(root, rel)))
            except Exception:  # pragma: no cover - defensive
                self.trees[module] = None


def _param_index(funcdef, parameter):
    """Positional index of ``parameter`` in a FunctionDef signature, or None."""
    names = [a.arg for a in funcdef.args.args]
    if parameter in names:
        return names.index(parameter)
    return None


def _argument_at(call, parameter, funcdef):
    """(node or None, omitted) for the argument that lands in ``parameter``."""
    for kw in call.keywords:
        if kw.arg == parameter:
            return kw.value, False
    index = _param_index(funcdef, parameter) if funcdef is not None else None
    if index is not None and index < len(call.args):
        return call.args[index], False
    return None, True


def _classify_argument(node, module, corpus):
    """What a call site hands over for one parameter."""
    if node is None:
        return AR_DEFAULT
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return AR_LITERAL
    if isinstance(node, ast.Constant) and node.value is None:
        return AR_LITERAL
    if isinstance(node, ast.Name):
        if corpus.values.get(module, {}).get(node.id) is not None:
            return AR_MODULE_CONSTANT
        if node.id in corpus.imports.get(module, {}):
            return AR_OTHER_MODULE
        return AR_LOCAL
    if isinstance(node, ast.Attribute):
        return AR_OTHER_MODULE
    if isinstance(node, ast.Call):
        return AR_CALL
    return AR_COMPUTED


def _carrier(argument_kinds, call_site_count):
    """The carrier arm of one binding, from its own call-site argument kinds."""
    if (argument_kinds.get(AR_LITERAL, 0) + argument_kinds.get(AR_MODULE_CONSTANT, 0)) > 0:
        return CC_CALL_SITE
    if not call_site_count:
        return CC_NEVER
    if argument_kinds.get(AR_DEFAULT, 0) == call_site_count:
        return CC_DEFAULT
    return CC_LOCAL


def call_index(corpus):
    """{(module, callee name): [ {line, args:[nodes], keywords, module} ]}."""
    index = {}
    for module, tree in corpus.trees.items():
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if not name:
                continue
            index.setdefault((module, name), []).append(node)
    return index


def population(root=None, upstream=None):
    """E513's function-local sites, in site order."""
    root = root or ROOT
    sites = e513.population(root, upstream)
    return sites


def analyse(root=None, upstream=None, published_upstream=None):
    root = root or ROOT
    corpus = LocalCorpus(root)
    index = call_index(corpus)
    sites = population(root, upstream)

    rows = {}
    site_records = []
    for site in sites:
        followed = e513.resolve(site, corpus)
        if followed["scope"] != e513.SCOPE_FUNCTION:
            continue
        key = (site["site_module"], site["expression"].split(".")[0],
               followed.get("enclosing_function"))
        rec = rows.get(key)
        if rec is None:
            hop = (followed.get("hops") or [{}])[0]
            rec = rows[key] = {
                "module": site["module"],
                "surface_modules": [],
                "site_module": site["site_module"],
                "constant": site["expression"].split(".")[0],
                "source": site["source"],
                "enclosing_function": followed.get("enclosing_function"),
                "binding_line": followed.get("binding_line"),
                "binding_hop_kind": hop.get("kind"),
                "binding_hop_detail": hop.get("detail") or {},
                "sites": 0,
                "surfaces": [],
                "parameters": [],
                "call_sites": [],
                "argument_kinds": dict((k, 0) for k in ARG_VOCAB),
            }
        rec["sites"] += 1
        if site.get("surface") not in rec["surfaces"]:
            rec["surfaces"].append(site.get("surface"))
        if site.get("module") and site["module"] not in rec["surface_modules"]:
            rec["surface_modules"].append(site["module"])
        if site.get("parameter") and site["parameter"] not in rec["parameters"]:
            rec["parameters"].append(site.get("parameter"))
        site_records.append({
            "source": site["source"], "module": site["module"],
            "surface": site.get("surface"), "parameter": site.get("parameter"),
            "line": site.get("line"), "expression": site["expression"],
            "binding_key": "%s|%s|%s" % (site["site_module"],
                                         site["expression"].split(".")[0],
                                         followed.get("enclosing_function")),
        })

    for key, rec in rows.items():
        surface_module = (rec["surface_modules"] or [rec["site_module"]])[0]
        funcdef = (corpus.funcs.get(surface_module) or {}).get(rec["surfaces"][0])
        parameter = rec["parameters"][0] if rec["parameters"] else None
        for surface in rec["surfaces"]:
            calls = index.get((surface_module, surface)) or []
            if not calls:
                calls = []
                for (mod, name), nodes in index.items():
                    if name == surface:
                        calls.extend(nodes)
            for call in calls:
                node, omitted = _argument_at(call, parameter, funcdef)
                kind = _classify_argument(node, surface_module, corpus)
                rec["argument_kinds"][kind] = rec["argument_kinds"].get(kind, 0) + 1
                rec["call_sites"].append({
                    "surface": surface,
                    "module": surface_module,
                    "line": getattr(call, "lineno", None),
                    "argument_kind": kind,
                    "argument": None if omitted else _short(node),
                })
        rec["call_site_count"] = len(rec["call_sites"])
        rec["callers_that_hand_over_a_population"] = (
            rec["argument_kinds"].get(AR_LITERAL, 0)
            + rec["argument_kinds"].get(AR_MODULE_CONSTANT, 0))
        rec["produced_by_a_call_into_another_module"] = (
            rec["binding_hop_kind"] == e513.HP_OTHER_MODULE_CALL
            and (rec["binding_hop_detail"] or {}).get("module")
            in set((corpus.imports.get(rec["site_module"]) or {}).values()))
        rec["produced_by_a_method_call_on_a_value"] = (
            rec["binding_hop_kind"] == e513.HP_OTHER_MODULE_CALL
            and not rec["produced_by_a_call_into_another_module"])
        rec["carrier"] = _carrier(rec["argument_kinds"], rec["call_site_count"])
        rec["dependency_modules"] = (
            [rec["binding_hop_detail"].get("module")]
            if rec["binding_hop_detail"].get("module") else [])

    out_rows = [rows[k] for k in sorted(rows, key=lambda k: tuple(str(x) for x in k))]
    for rec in out_rows:
        rec["surfaces"] = sorted(rec["surfaces"])
        rec["surface_modules"] = sorted(rec["surface_modules"])
        rec["parameters"] = sorted(rec["parameters"])
    return {"rows": out_rows, "sites": site_records, "corpus": corpus,
            "modules_scanned": len(corpus.by_module),
            "unreadable": corpus.unreadable}


def _count(records, key, vocab):
    out = dict((v, 0) for v in vocab)
    for rec in records:
        value = rec.get(key)
        if value in out:
            out[value] += 1
        else:
            out[value] = out.get(value, 0) + 1
    return out


def _summary(rows, sites, modules_scanned, corpus):
    carriers = _count(rows, "carrier", CC_VOCAB)
    args = dict((k, 0) for k in ARG_VOCAB)
    for rec in rows:
        for kind, count in (rec.get("argument_kinds") or {}).items():
            args[kind] = args.get(kind, 0) + count
    handoff = [rec for rec in rows if rec.get("produced_by_a_call_into_another_module")]
    return {
        "modules_scanned": modules_scanned,
        "function_local_bindings": len(rows),
        "function_local_sites": len(sites),
        "function_local_surfaces": len({s for rec in rows for s in rec["surfaces"]}),
        "carrier_counts": carriers,
        "call_site_argument_counts": args,
        "call_sites_examined": sum(rec.get("call_site_count") or 0 for rec in rows),
        "bindings_no_caller_ever_hands_a_population_to": sum(
            1 for rec in rows if not rec.get("callers_that_hand_over_a_population")),
        "bindings_with_no_call_site_at_all": carriers[CC_NEVER],
        "locals_produced_by_a_call_into_another_module": len(handoff),
        "locals_produced_elsewhere_dependency_modules": sorted(
            {m for rec in handoff for m in rec.get("dependency_modules") or []}),
        "locals_produced_by_a_method_call_on_a_value_not_a_module": sum(
            1 for rec in rows if rec.get("produced_by_a_method_call_on_a_value")),
        "bindings_whose_only_population_is_a_parameter_default": carriers[CC_DEFAULT],
    }


def _verdict(summary):
    if not summary["function_local_bindings"]:
        return V_NONE
    call_site = summary["carrier_counts"][CC_CALL_SITE]
    if call_site == summary["function_local_bindings"]:
        return V_CALL_SITE
    if call_site == 0:
        return V_LOCAL_ONLY
    return V_MIXED


def _answers(summary):
    return [
        ["How many bindings that E508 called module constants are function locals?",
         "%d of the bindings (%d sites, %d distinct surfaces)."
         % (summary["function_local_bindings"], summary["function_local_sites"],
            summary["function_local_surfaces"])],
        ["Does any caller hand a real population to those surfaces?",
         "%d of %d bindings have at least one call site passing a literal container or a "
         "module-scope constant; %d have no such caller."
         % (summary["function_local_bindings"]
            - summary["bindings_no_caller_ever_hands_a_population_to"],
            summary["function_local_bindings"],
            summary["bindings_no_caller_ever_hands_a_population_to"])],
        ["How many of those surfaces are never called at all in this tree?",
         "%d of %d bindings have no call site."
         % (summary["bindings_with_no_call_site_at_all"],
            summary["function_local_bindings"])],
        ["Which locals are themselves produced by a call into another module?",
         "%d bindings, into %d distinct dependency modules; a further %d are a method call on "
         "a value the caller already holds, which is not another module."
         % (summary["locals_produced_by_a_call_into_another_module"],
            len(summary["locals_produced_elsewhere_dependency_modules"]),
            summary["locals_produced_by_a_method_call_on_a_value_not_a_module"])],
        ["Are the call sites mostly omitting the argument?",
         "%d call sites were read: %d pass a default, %d a literal, %d a module constant, "
         "%d a local, %d a call result."
         % (summary["call_sites_examined"],
            summary["call_site_argument_counts"].get(AR_DEFAULT, 0),
            summary["call_site_argument_counts"].get(AR_LITERAL, 0),
            summary["call_site_argument_counts"].get(AR_MODULE_CONSTANT, 0),
            summary["call_site_argument_counts"].get(AR_LOCAL, 0),
            summary["call_site_argument_counts"].get(AR_CALL, 0))],
    ]


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    found = analyse(root, upstream)
    summary = _summary(found["rows"], found["sites"], found["modules_scanned"],
                       found["corpus"])
    face = {
        "card": CARD,
        "study": STUDY,
        "title": ("Which function local that E508 called a module constant is the only "
                  "carrier of a population"),
        "kind": "static_read_of_the_repo_plus_its_own_published_upstream_faces",
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "carrier_vocab": list(CC_VOCAB),
        "argument_vocab": list(ARG_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "answers": _answers(summary),
        "verdict": _verdict(summary),
        "rows": found["rows"],
        "unreadable": found["unreadable"],
        "method_limits": [
            ("call sites are matched by callee name inside the module that defines the "
             "surface (a fallback pass matches the bare name across the tree); a call "
             "through an alias of the surface is not seen"),
            ("an argument that is a name counts as a population only when that name is "
             "bound at module scope of the surface's own module; a local is recorded as a "
             "local even when the caller's local is itself a module constant"),
            ("only the first parameter of each binding is used to index call arguments; a "
             "binding that reaches two different parameters is counted under the first"),
            ("a local produced by ``x.method()`` is counted as built by another module only "
             "when ``x`` is an import alias of that module; when ``x`` is a value the caller "
             "already holds the call is published under its own counter, because a method on a "
             "value names no module"),
            ("whether a caller's expression really covers every branch is not measured "
             "here: this face answers who supplies what, not whether the branch is guarded"),
        ],
    }
    if write:
        write_face(face, root)
    return face


def _now():
    return e513.base._now()


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in ("%s-%s.json" % (DATED_PREFIX, DATE_STAMP), FACE_NAME):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return face


def load_face(root=None):
    root = root or ROOT
    return e513.base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))


def check(face=None, root=None):
    """Re-derive every published number from the face's own rows."""
    root = root or ROOT
    face = face or load_face(root)
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if len(rows) != summary.get("function_local_bindings"):
        problems.append("row count %d != summary bindings %r"
                        % (len(rows), summary.get("function_local_bindings")))
    carriers = _count(rows, "carrier", CC_VOCAB)
    if carriers != summary.get("carrier_counts"):
        problems.append("carrier counts do not re-derive")
    sites = sum(rec.get("sites") or 0 for rec in rows)
    if sites != summary.get("function_local_sites"):
        problems.append("site total %d != summary %r"
                        % (sites, summary.get("function_local_sites")))
    surfaces = {s for rec in rows for s in rec.get("surfaces") or []}
    if len(surfaces) != summary.get("function_local_surfaces"):
        problems.append("surface count does not re-derive")
    examined = sum(rec.get("call_site_count") or 0 for rec in rows)
    if examined != summary.get("call_sites_examined"):
        problems.append("call site total does not re-derive")
    handoff = sum(1 for rec in rows if rec.get("produced_by_a_call_into_another_module"))
    if handoff != summary.get("locals_produced_by_a_call_into_another_module"):
        problems.append("cross-module local count does not re-derive")
    none = sum(1 for rec in rows if not rec.get("callers_that_hand_over_a_population"))
    if none != summary.get("bindings_no_caller_ever_hands_a_population_to"):
        problems.append("unsupplied binding count does not re-derive")
    if carriers[CC_NEVER] != summary.get("bindings_with_no_call_site_at_all"):
        problems.append("never-called count does not re-derive")
    if carriers[CC_DEFAULT] != summary.get("bindings_whose_only_population_is_a_parameter_default"):
        problems.append("default-only count does not re-derive")
    value_calls = sum(1 for rec in rows if rec.get("produced_by_a_method_call_on_a_value"))
    if value_calls != summary.get("locals_produced_by_a_method_call_on_a_value_not_a_module"):
        problems.append("value-level method call count does not re-derive")
    args = dict((k, 0) for k in ARG_VOCAB)
    for rec in rows:
        for kind, count in (rec.get("argument_kinds") or {}).items():
            args[kind] = args.get(kind, 0) + count
    if args != summary.get("call_site_argument_counts"):
        problems.append("argument counts do not re-derive")
    for rec in rows:
        if rec.get("carrier") not in CC_VOCAB:
            problems.append("%s.%s carrier outside the vocabulary"
                            % (rec.get("source"), rec.get("constant")))
        supplied = ((rec.get("argument_kinds") or {}).get(AR_LITERAL, 0)
                    + (rec.get("argument_kinds") or {}).get(AR_MODULE_CONSTANT, 0))
        if supplied != rec.get("callers_that_hand_over_a_population"):
            problems.append("%s.%s supply count does not re-derive"
                            % (rec.get("source"), rec.get("constant")))
        if (rec.get("carrier") == CC_CALL_SITE) != (supplied > 0):
            problems.append("%s.%s carrier contradicts its own argument kinds"
                            % (rec.get("source"), rec.get("constant")))
        if len(rec.get("call_sites") or []) != rec.get("call_site_count"):
            problems.append("%s.%s call site list length disagrees with its count"
                            % (rec.get("source"), rec.get("constant")))
        if rec.get("argument_kinds") and sum(
                rec["argument_kinds"].values()) != rec.get("call_site_count"):
            problems.append("%s.%s argument kinds do not add up to the call site count"
                            % (rec.get("source"), rec.get("constant")))
    if _verdict(summary) != face.get("verdict"):
        problems.append("verdict does not follow from the summary")
    if _answers(summary) != face.get("answers"):
        problems.append("answers do not re-derive")
    return problems


def site_problems(face=None, root=None):
    """What a consumer needs: provenance intact and every row re-derivable from its own sites."""
    root = root or ROOT
    face = face or load_face(root)
    problems = list(check(face, root))
    if face.get("population_source") != POPULATION_SOURCE:
        problems.append("population_source is not the one this study used")
    if face.get("study") != STUDY or face.get("card") != CARD:
        problems.append("the study or card identity was edited")
    if face.get("evidence_cutoff") != DATE_STAMP:
        problems.append("evidence_cutoff does not match the dated file name")
    for rec in face.get("rows") or []:
        expected = _carrier(rec.get("argument_kinds") or {}, rec.get("call_site_count") or 0)
        if rec.get("carrier") != expected:
            problems.append("%s.%s carrier %r is not what its call sites give (%r)"
                            % (rec.get("source"), rec.get("constant"), rec.get("carrier"),
                               expected))
        source = rec.get("source") or ""
        if not source or not os.path.exists(os.path.join(root, source)):
            problems.append("%s names a source that is not on disk" % (source or "<empty>"))
    return problems


def verify(root=None, upstream=None):
    """Rebuild from the tree and compare with the published file."""
    root = root or ROOT
    problems = []
    face = load_face(root)
    rebuilt = build(root, write=False, upstream=upstream)
    for key in ("summary", "answers", "verdict", "carrier_vocab", "argument_vocab",
                "verdict_vocab"):
        if face.get(key) != rebuilt.get(key):
            problems.append("%s differs from a fresh build" % key)
    return problems


# ---------------------------------------------------------------- selftest fixtures
FIX_CALL_SITE = """\
NAMES = ("alpha", "beta")
def surface(groups=None):
    return groups
def go():
    gr = NAMES
    out = surface(gr)
    return surface(NAMES)
"""

FIX_LOCAL_ONLY = """\
def _names():
    return ("alpha",)
def surface(groups=None):
    return groups
def go():
    gr = _names()
    return surface(gr)
"""

FIX_HANDOFF = """\
import helper
def surface(groups=None):
    return groups
def go():
    gr = helper.names()
    return surface(gr)
"""

HELPER = """\
def names():
    return ("gamma",)
"""


def _fixture(root):
    scripts = os.path.join(root, "scripts")
    os.makedirs(scripts)
    for name, text in (("fix_call_site", FIX_CALL_SITE), ("fix_local_only", FIX_LOCAL_ONLY),
                       ("fix_handoff", FIX_HANDOFF), ("helper", HELPER)):
        with io.open(os.path.join(scripts, name + ".py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(text)
    return scripts


def _fixture_upstream(sites):
    return {
        "rows": [
            {
                "module": site["module"],
                "surface": site["surface"],
                "call": site["surface"],
                "line": site["line"],
                "source": site["source"],
                "in_selftest": False,
                "arguments": [{"parameter": site["parameter"],
                               "expression": site["expression"],
                               "kind": e513.CONSTANT_KINDS[0]}],
            }
            for site in sites
        ]
    }


def _fixture_sites():
    return [
        {"module": "fix_call_site", "source": "scripts/fix_call_site.py",
         "surface": "surface", "parameter": "groups", "line": 6, "expression": "gr"},
        {"module": "fix_local_only", "source": "scripts/fix_local_only.py",
         "surface": "surface", "parameter": "groups", "line": 6, "expression": "gr"},
        {"module": "fix_handoff", "source": "scripts/fix_handoff.py",
         "surface": "surface", "parameter": "groups", "line": 5, "expression": "gr"},
    ]


def selftest():
    import shutil
    import tempfile

    problems = []
    root = tempfile.mkdtemp(prefix="e516_")
    try:
        _fixture(root)
        upstream = _fixture_upstream(_fixture_sites())
        found = analyse(root, upstream)
        rows = dict((rec["module"], rec) for rec in found["rows"])

        # the population is the three fixture bindings, each a local of its own go()
        if len(found["rows"]) != 3:
            problems.append("fixture population %d != 3" % len(found["rows"]))
        # a sibling call site that hands over a module-scope constant makes it call-site readable
        call_site = rows.get("fix_call_site") or {}
        if call_site.get("carrier") != CC_CALL_SITE:
            problems.append("a module-constant argument was not read as a call-site carrier")
        if call_site.get("argument_kinds", {}).get(AR_MODULE_CONSTANT) != 1:
            problems.append("a module-constant argument was not classified as one")
        if call_site.get("argument_kinds", {}).get(AR_LOCAL) != 1:
            problems.append("the local argument of the same surface was not counted")
        # a caller that only ever passes a local is not a call-site carrier
        local_only = rows.get("fix_local_only") or {}
        if local_only.get("carrier") != CC_LOCAL:
            problems.append("a local-only caller was not read as readable-only-through-the-local")
        if local_only.get("argument_kinds", {}).get(AR_LOCAL) != 1:
            problems.append("a local argument was not classified as a local")
        # a local produced by a call into another module is published as such
        handoff = rows.get("fix_handoff") or {}
        if handoff.get("carrier") != CC_LOCAL:
            problems.append("a cross-module call argument was not read as a local")
        if not handoff.get("produced_by_a_call_into_another_module"):
            problems.append("a local produced by another module was not flagged")

        # the two arms the pipeline cannot reach are pinned on the decision function
        if _carrier({}, 0) != CC_NEVER:
            problems.append("the never-supplied arm does not follow from zero call sites")
        if _carrier({AR_DEFAULT: 2}, 2) != CC_DEFAULT:
            problems.append("the default arm does not follow from all-omitted call sites")
        if _carrier({AR_DEFAULT: 1, AR_LOCAL: 1}, 2) != CC_LOCAL:
            problems.append("a mixed default/local surface was not read as local")
        if _carrier({AR_LITERAL: 1, AR_LOCAL: 3}, 4) != CC_CALL_SITE:
            problems.append("one literal argument did not make the binding call-site readable")
        if _classify_argument(None, "x", None) != AR_DEFAULT:
            problems.append("an omitted argument was not classified as default")
        if _classify_argument(ast.parse("('a',)").body[0].value, "x", None) != AR_LITERAL:
            problems.append("a container at the call site was not classified as a literal")

        # verdict and the face's own arithmetic
        summary = _summary(found["rows"], found["sites"], found["modules_scanned"],
                           found["corpus"])
        if _verdict(summary) != V_MIXED:
            problems.append("fixture verdict %r != mixed" % _verdict(summary))
        face = build(root, write=False, upstream=upstream)
        problems.extend(["check: " + p for p in check(face, root)])

        # a keyword argument lands in the parameter regardless of position
        with io.open(os.path.join(root, "scripts", "fix_keyword.py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write("NAMES = ('alpha',)\ndef surface(seed=None, groups=None):\n"
                     "    return groups\ndef go():\n    gr = NAMES\n"
                     "    return surface(groups=NAMES)\n")
        sites = _fixture_sites() + [{"module": "fix_keyword",
                                     "source": "scripts/fix_keyword.py",
                                     "surface": "surface", "parameter": "groups",
                                     "line": 4, "expression": "gr"}]
        found = analyse(root, _fixture_upstream(sites))
        kw = dict((rec["module"], rec) for rec in found["rows"]).get("fix_keyword") or {}
        if kw.get("carrier") != CC_CALL_SITE:
            problems.append("a keyword argument was not matched to its parameter")

        # verify() must see a stale file
        face = build(root, write=True, upstream=_fixture_upstream(sites))
        if verify(root, upstream=_fixture_upstream(sites)):
            problems.append("a freshly written fixture face does not verify against itself")
        face["summary"]["function_local_bindings"] += 1
        write_face(face, root)
        if not verify(root, upstream=_fixture_upstream(sites)):
            problems.append("a tampered summary still verified")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print("LOCALCARRIER %s verdict=%s rows=%d sites=%d"
              % (DATE_STAMP, face["verdict"], face["summary"]["function_local_bindings"],
                 face["summary"]["function_local_sites"]))
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        problems = check()
        for problem in problems:
            print("[FAIL] " + problem)
        print("check problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        for problem in problems:
            print("[FAIL] " + problem)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "selftest":
        problems = selftest()
        for problem in problems:
            print("[FAIL] " + problem)
        print("selftest problems=%d" % len(problems))
        return 0 if not problems else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())