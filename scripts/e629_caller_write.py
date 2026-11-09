"""E629 -- does the caller of the holding function write the key E628 could not find a writer for?

E628 (r1646) publishes its own bound: the writer arm searches the module *outside the function that
holds the dead line*, but it only ever looks at places where that name is spelled.  For the two
duplicate rows whose receiver is a parameter, no site inside the module writes the key, and the name
does not exist anywhere else in the module -- the only remaining place a write can live is the
caller of the holding function, where the object is handed in under the caller's own name.

This card follows exactly that hop.  For each duplicate row whose receiver arrives as a parameter:

  * find the holding definition in the module and the parameter's position in its signature;
  * find every call site of that name in the same module (``f(...)`` and ``mod.f(...)``);
  * map the argument that reaches the parameter (positional, keyword, or missing);
  * resolve the caller's scope -- the innermost enclosing definition, or the module body -- and ask
    whether that scope writes the key on the argument's leftmost name (E625's write marks).

The reading this card is built to publish is the one E628 could not: a caller write happens *before
the callee is entered*, so both the dead line and its sibling read see the post-write value.  A
caller write therefore cannot separate the two reads even where one exists.  The row classes name
that explicitly rather than treating "found a writer" as "closed the duplicate".

Deliberately NOT done: no interprocedural descent beyond the one hop up (a caller whose own argument
comes from its caller is out of reach), no class/attribute resolution, no alias analysis inside the
caller beyond E625's write marks, no cross-module import graph, no concurrency model, no fixture
write, no runner.

Deterministic, static, no network, no runner, no fixture write.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "CALLERWRITE.json"
LATEST = "callerwrite_latest.json"
STUDY = "E629_caller_write"
SELF_PARTS = {"e629_caller_write.py", "run_e629_smoke_leg.py", "_probe_e629.py"}

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402
import e625_sibling_read_value as e625                                              # noqa: E402
import e628_receiver_origin as e628                                                 # noqa: E402

FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)

FORM_PLAIN = "a_plain_name"
FORM_ATTRIBUTE = "an_attribute_chain"
FORM_SUBSCRIPT = "a_subscript"
FORM_OTHER = "another_expression"
FORM_MISSING = "no_argument_for_that_parameter"
ARG_FORMS = [FORM_PLAIN, FORM_ATTRIBUTE, FORM_SUBSCRIPT, FORM_OTHER, FORM_MISSING]

SITE_RECURSIVE = "the_call_site_is_inside_the_holding_function_itself"
SITE_MISSING = "no_argument_reaches_the_parameter_so_the_default_stands"
SITE_NOT_A_NAME = "the_argument_is_not_a_name_so_no_key_can_be_located"
SITE_UNWRITTEN = "the_argument_is_a_name_the_caller_does_not_write_at_the_key"
SITE_BEFORE = "the_caller_writes_the_key_on_the_argument_before_the_call"
SITE_AFTER = "the_caller_writes_the_key_on_the_argument_after_the_call"
SITE_HANDED = "the_argument_is_handed_to_another_call_in_the_caller"
SITE_NO_SCOPE = "the_caller_scope_cannot_be_resolved"
SITE_CLASSES = [SITE_RECURSIVE, SITE_MISSING, SITE_NOT_A_NAME, SITE_UNWRITTEN, SITE_BEFORE,
                SITE_AFTER, SITE_HANDED, SITE_NO_SCOPE]

ROW_NO_CALL = "no_call_site_in_the_module"
ROW_UNWRITTEN = "every_call_site_leaves_the_argument_unwritten"
ROW_BEFORE = "a_caller_writes_the_key_but_the_write_precedes_both_reads_so_the_duplicate_stands"
ROW_AFTER = "a_caller_writes_the_key_only_after_the_call_so_it_cannot_reach_this_read"
ROW_UNTRACED = "the_call_sites_cannot_be_traced"
ROW_CLASSES = [ROW_NO_CALL, ROW_UNWRITTEN, ROW_BEFORE, ROW_AFTER, ROW_UNTRACED]


# ---------------------------------------------------------------- the signature and the call sites
def param_position(fn, name):
    """Where ``name`` sits in the signature, as ('positional'|'keyword'|'vararg'|'kwarg', index)."""
    a = fn.args
    pos = [x.arg for x in list(getattr(a, "posonlyargs", [])) + list(a.args)]
    if name in pos:
        return ("positional", pos.index(name))
    kw = [x.arg for x in a.kwonlyargs]
    if name in kw:
        return ("keyword", kw.index(name))
    if a.vararg is not None and a.vararg.arg == name:
        return ("vararg", None)
    if a.kwarg is not None and a.kwarg.arg == name:
        return ("kwarg", None)
    return None


def enclosing(fns, line):
    """The innermost definition whose span holds ``line``."""
    cand = [f for f in fns if f.lineno <= line <= (f.end_lineno or f.lineno)]
    if not cand:
        return None
    cand.sort(key=lambda f: (f.lineno, -(f.end_lineno or f.lineno)))
    return cand[-1]


def calls_of(tree, fname):
    """Every call in the module whose callee is spelled ``fname`` (bare or attribute)."""
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name) and f.id == fname:
            out.append(n)
        elif isinstance(f, ast.Attribute) and f.attr == fname:
            out.append(n)
    out.sort(key=lambda c: (c.lineno, c.col_offset))
    return out


def leftmost_name(node):
    """The leftmost Name of an attribute/subscript chain, or None."""
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def argument_form(node):
    if isinstance(node, ast.Name):
        return FORM_PLAIN
    if isinstance(node, ast.Attribute):
        return FORM_ATTRIBUTE
    if isinstance(node, ast.Subscript):
        return FORM_SUBSCRIPT
    return FORM_OTHER


def argument_at(call, fn, name, position):
    """The expression that reaches the parameter, plus how it was passed."""
    kind, idx = position
    if kind == "positional":
        if idx < len(call.args):
            if any(isinstance(a, ast.Starred) for a in call.args[:idx + 1]):
                return None, "starred"
            return call.args[idx], "positional"
        for kw in call.keywords:
            if kw.arg == name:
                return kw.value, "keyword"
        return None, "missing"
    if kind == "keyword":
        for kw in call.keywords:
            if kw.arg == name:
                return kw.value, "keyword"
        return None, "missing"
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value, "keyword"
    return None, "missing"


def module_body_nodes(tree):
    return [n for n in tree.body if not isinstance(n, FUNC)]


def site_facts(tree, graph, call, fn, pname, key, module_body):
    """What one call site does to the object it hands the parameter."""
    position = param_position(fn, pname)
    holder = enclosing(graph["fns"], call.lineno)
    out = {"line": call.lineno, "caller": holder.name if holder is not None else None,
           "caller_is_the_holding_function": holder is fn}
    node, how = argument_at(call, fn, pname, position or ("positional", None))
    out["passed_as"] = how
    if holder is fn:
        out.update({"argument": None, "argument_form": None, "argument_base_name": None,
                    "site_class": SITE_RECURSIVE, "writes_before_the_call": [],
                    "writes_after_the_call": [], "handed_to_another_call": []})
        return out
    if node is None:
        out.update({"argument": None, "argument_form": FORM_MISSING, "argument_base_name": None,
                    "site_class": SITE_MISSING, "writes_before_the_call": [],
                    "writes_after_the_call": [], "handed_to_another_call": []})
        return out
    text = e624.text_of(node)
    base = leftmost_name(node)
    out.update({"argument": text, "argument_form": argument_form(node),
                "argument_base_name": base})
    if base is None:
        out.update({"site_class": SITE_NOT_A_NAME, "writes_before_the_call": [],
                    "writes_after_the_call": [], "handed_to_another_call": []})
        return out
    if holder is None:
        scope = module_body
    else:
        scope = e623.own_scope(holder)
    named, _unnamed, handed = e625.write_marks(scope, text, key, base)
    named = [s for s in named if s["line"] != call.lineno]
    handed = [s for s in handed if s["line"] < call.lineno]
    before = [s for s in named if s["line"] < call.lineno]
    after = [s for s in named if s["line"] > call.lineno]
    out["writes_before_the_call"] = before
    out["writes_after_the_call"] = after
    out["handed_to_another_call"] = handed
    if before:
        cls = SITE_BEFORE
    elif after:
        cls = SITE_AFTER
    elif handed:
        cls = SITE_HANDED
    else:
        cls = SITE_UNWRITTEN
    out["site_class"] = cls
    return out


def row_class(sites, param_verified):
    if not param_verified:
        return ROW_UNTRACED
    live = [s for s in sites if s["site_class"] != SITE_RECURSIVE]
    if not live:
        return ROW_NO_CALL
    if any(s["site_class"] == SITE_BEFORE for s in live):
        return ROW_BEFORE
    if any(s["site_class"] == SITE_AFTER for s in live):
        return ROW_AFTER
    if all(s["site_class"] in (SITE_UNWRITTEN, SITE_MISSING, SITE_NOT_A_NAME) for s in live):
        if any(s["site_class"] == SITE_UNWRITTEN for s in live):
            return ROW_UNWRITTEN
        return ROW_UNTRACED
    return ROW_UNTRACED


def row_facts_tree(tree, row):
    """Follow one outside-origin duplicate row one hop into its callers."""
    graph = e622_call_graph(tree)
    fns = graph["fns"]
    holder = None
    for f in fns:
        if f.name == row["function"] and f.lineno == row.get("def_line"):
            holder = f
            break
    if holder is None:
        for f in fns:
            if f.name == row["function"] and f.lineno <= row["line"] <= (f.end_lineno or f.lineno):
                holder = f
                break
    pname = row.get("receiver_base_name")
    out = {"module": row.get("module"), "function": row.get("function"),
           "def_line": row.get("def_line"), "line": row.get("line"), "key": row.get("key"),
           "receiver_base_name": pname,
           "parameter_position": None, "parameter_verified": False,
           "call_sites": [], "duplicate_class_after_the_caller_arm": ROW_UNTRACED}
    if holder is None or pname is None:
        out["trace_note"] = "the holding definition or the receiver name is not in the module"
        return out
    position = param_position(holder, pname)
    out["parameter_position"] = list(position) if position else None
    out["parameter_verified"] = position is not None
    if position is None:
        out["trace_note"] = "the receiver name is not a parameter of the holding definition"
        return out
    body = module_body_nodes(tree)
    out["call_sites"] = [site_facts(tree, graph, c, holder, pname, row["key"], body)
                         for c in calls_of(tree, holder.name)]
    out["duplicate_class_after_the_caller_arm"] = row_class(out["call_sites"], True)
    return out


def e622_call_graph(tree, stem=""):
    import e622_deadlocal_reach as e622
    return e622.call_graph(tree, stem)


# ---------------------------------------------------------------- population and measurement
def published_rows(root=ROOT):
    """E628's duplicate rows whose receiver arrives from outside the interval."""
    path = os.path.join(root, "results", "state_tilt", e628.LATEST)
    out = {"published": False, "rows": [], "face_verdict": None}
    if not os.path.exists(path):
        out["note"] = "no published E628 face on disk"
        return out
    doc = json.load(io.open(path, encoding="utf-8"))
    rows = []
    for r in (doc.get("lines") or []):
        if r.get("corrected_class") != e624.CORRECTED[0]:
            continue
        if not r.get("sibling_read_reads_the_same_object_after_the_dead_line"):
            continue
        if r.get("origin_before_the_e627_interval_start") is not True:
            continue
        rows.append({k: r.get(k) for k in
                     ("module", "function", "def_line", "line", "key", "receiver_origin",
                      "receiver_base_name", "base_binding_origin")})
    rows.sort(key=lambda r: (r["module"] or "", r["line"] or 0))
    out.update({"published": True, "rows": rows, "face_verdict": doc.get("verdict"),
                "face_counts": doc.get("counts") or {}})
    return out


def measure(root=ROOT):
    pub = published_rows(root)
    facts, unparsed = [], []
    for row in pub["rows"]:
        path = os.path.join(root, row["module"] or "")
        if not os.path.exists(path):
            unparsed.append({"module": row["module"], "note": "module file is gone"})
            continue
        try:
            tree = ast.parse(io.open(path, encoding="utf-8").read())
        except Exception as exc:  # noqa: BLE001 - a module that will not parse is a published fact
            unparsed.append({"module": row["module"], "note": repr(exc)[:160]})
            continue
        facts.append(row_facts_tree(tree, row))
    return {"e628": pub, "rows": facts, "unparsed": unparsed}


def counts_of(m):
    rows = m["rows"]
    oc = {k: 0 for k in ROW_CLASSES}
    sc = {k: 0 for k in SITE_CLASSES}
    fc = {k: 0 for k in ARG_FORMS}
    sites = []
    for r in rows:
        oc[r["duplicate_class_after_the_caller_arm"]] = \
            oc.get(r["duplicate_class_after_the_caller_arm"], 0) + 1
        for s in r["call_sites"]:
            sites.append(s)
            sc[s["site_class"]] = sc.get(s["site_class"], 0) + 1
            if s["argument_form"] in fc:
                fc[s["argument_form"]] += 1
    c = {
        "population_duplicate_rows": len(rows),
        "e628_published_duplicate_rows": len(m["e628"]["rows"]),
        "modules_that_will_not_parse": len(m["unparsed"]),
        "rows_with_a_verified_parameter": sum(1 for r in rows if r["parameter_verified"]),
        "rows_with_at_least_one_call_site": sum(
            1 for r in rows if any(s["site_class"] != SITE_RECURSIVE for s in r["call_sites"])),
        "rows_with_no_call_site": oc[ROW_NO_CALL],
        "rows_a_caller_writes_the_key": oc[ROW_BEFORE] + oc[ROW_AFTER],
        "rows_a_caller_writes_the_key_before_the_call": oc[ROW_BEFORE],
        "rows_closed_by_the_caller_arm": 0,
        "rows_left_open": oc[ROW_BEFORE] + oc[ROW_UNWRITTEN],
        "rows_untraced": oc[ROW_UNTRACED],
        "call_sites_total": len(sites),
        "call_sites_whose_argument_is_a_name": sum(
            1 for s in sites if s["argument_base_name"]),
        "call_sites_that_write_the_key_before_the_call": sc.get(SITE_BEFORE, 0),
        "call_sites_that_write_the_key_only_after_the_call": sc.get(SITE_AFTER, 0),
        "call_sites_that_hand_the_argument_upward": sc.get(SITE_HANDED, 0),
        "call_sites_that_cannot_be_traced": sc.get(SITE_NOT_A_NAME, 0) + sc.get(SITE_NO_SCOPE, 0),
        "call_sites_whose_default_stands": sc.get(SITE_MISSING, 0),
    }
    for k in ROW_CLASSES:
        c["row_" + k] = oc[k]
    for k in SITE_CLASSES:
        c["site_" + k] = sc[k]
    for k in ARG_FORMS:
        c["form_" + k] = fc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if not m["e628"]["published"]:
        return "no_published_e628_face_to_price"
    if c["e628_published_duplicate_rows"] == 0:
        return "e628_published_no_outside_origin_duplicate_row"
    if c["modules_that_will_not_parse"]:
        return "some_holder_modules_no_longer_parse_so_the_caller_arm_is_incomplete"
    n = c["population_duplicate_rows"]
    if c["rows_a_caller_writes_the_key"] == 0:
        if c["rows_untraced"] == 0:
            return ("none_of_the_%d_outside_origin_rows_has_a_caller_that_writes_the_key_so_the_"
                    "caller_arm_closes_none_of_them" % n)
        return ("none_of_the_%d_outside_origin_rows_has_a_caller_that_writes_the_key_and_%d_of_them_"
                "cannot_be_traced_at_this_hop_so_the_caller_arm_closes_none_of_them"
                % (n, c["rows_untraced"]))
    k = c["rows_a_caller_writes_the_key"]
    return ("%d_of_the_%d_outside_origin_rows_does_have_a_caller_that_writes_the_key_and_those_"
            "writes_precede_both_reads_so_the_caller_arm_closes_none_of_them" % (k, n))


def answer_of(m):
    c = counts_of(m)
    if not m["e628"]["published"]:
        return "E628's face is not on disk, so there is no caller arm to price"
    return ("E628 published %d duplicate row(s) whose receiver arrives from before the interval.  "
            "%d of them has a verified parameter and %d has at least one call site in its own "
            "module.  Across %d call site(s), %d pass the receiver as a name, %d write the key on "
            "that name before the call and %d write it only after; %d hand the argument to another "
            "call in the caller and %d carry no traceable argument.  Because every caller write "
            "happens before the callee is entered, it reaches both the dead line and its sibling "
            "read, so the caller arm closes %d of the %d row(s) and leaves %d open"
            % (c["e628_published_duplicate_rows"], c["rows_with_a_verified_parameter"],
               c["rows_with_at_least_one_call_site"], c["call_sites_total"],
               c["call_sites_whose_argument_is_a_name"],
               c["call_sites_that_write_the_key_before_the_call"],
               c["call_sites_that_write_the_key_only_after_the_call"],
               c["call_sites_that_hand_the_argument_upward"],
               c["call_sites_that_cannot_be_traced"] + c["call_sites_whose_default_stands"],
               c["rows_closed_by_the_caller_arm"], len(m["rows"]), c["rows_left_open"]))


# ---------------------------------------------------------------- face problems
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    rows = face.get("rows") or []
    if counts.get("population_duplicate_rows") != len(rows):
        p.append("counts.population_duplicate_rows says %r but the face publishes %d rows"
                 % (counts.get("population_duplicate_rows"), len(rows)))
    oc = {k: 0 for k in ROW_CLASSES}
    sc = {k: 0 for k in SITE_CLASSES}
    fc = {k: 0 for k in ARG_FORMS}
    sites = []
    for r in rows:
        cls = r.get("duplicate_class_after_the_caller_arm")
        if cls not in ROW_CLASSES:
            p.append("row %r in %r carries duplicate_class_after_the_caller_arm=%r"
                     % (r.get("line"), r.get("function"), cls))
        else:
            oc[cls] += 1
        live = []
        for s in r.get("call_sites") or []:
            sites.append(s)
            live.append(s)
            sc[s.get("site_class")] = sc.get(s.get("site_class"), 0) + 1
            if s.get("argument_form") in fc:
                fc[s.get("argument_form")] += 1
            if bool(s.get("writes_before_the_call")) != (s.get("site_class") == SITE_BEFORE):
                p.append("call site %r of %r publishes %d pre-call write(s) under class %r"
                         % (s.get("line"), r.get("function"),
                            len(s.get("writes_before_the_call") or []), s.get("site_class")))
            if bool(s.get("writes_after_the_call")) and not \
                    s.get("writes_before_the_call"):
                if s.get("site_class") != SITE_AFTER:
                    p.append("call site %r of %r holds an after-call write under class %r"
                             % (s.get("line"), r.get("function"), s.get("site_class")))
        if r.get("parameter_verified") is True:
            want = row_class([s for s in live if s.get("site_class") in SITE_CLASSES], True)
            if want != cls:
                p.append("row %r in %r says %r but its call sites force %r"
                         % (r.get("line"), r.get("function"), cls, want))
        elif r.get("parameter_verified") is False and cls != ROW_UNTRACED:
            p.append("row %r in %r claims %r without a verified parameter"
                     % (r.get("line"), r.get("function"), cls))
    for k in ROW_CLASSES:
        if counts.get("row_" + k) != oc[k]:
            p.append("counts.row_%s does not re-derive from the rows" % k)
    if sum(oc.values()) != len(rows):
        p.append("the row classes do not add up to the published row count")
    for k in SITE_CLASSES:
        if counts.get("site_" + k, 0) != sc.get(k, 0):
            p.append("counts.site_%s does not re-derive from the call sites" % k)
    if len(sites) != counts.get("call_sites_total"):
        p.append("counts.call_sites_total says %r but the rows publish %d"
                 % (counts.get("call_sites_total"), len(sites)))
    if sum(fc.values()) != len(sites):
        p.append("the argument forms cover %d of %d call sites"
                 % (sum(fc.values()), len(sites)))
    for k in ARG_FORMS:
        if counts.get("form_" + k) != fc[k]:
            p.append("counts.form_%s does not re-derive from the rows" % k)
    if counts.get("rows_closed_by_the_caller_arm") != 0:
        p.append("counts.rows_closed_by_the_caller_arm is %r -- a caller write precedes both reads "
                 "and cannot separate them" % counts.get("rows_closed_by_the_caller_arm"))
    derived = derive_verdict({
        "e628": {"published": True,
                 "rows": [None] * (counts.get("e628_published_duplicate_rows") or 0)},
        "rows": rows,
        "unparsed": [None] * (counts.get("modules_that_will_not_parse") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the row table forces (%r)"
                 % (face.get("verdict"), derived))
    cc = face.get("e628_cross_check") or {}
    if cc.get("published") is False:
        p.append("the E628 cross-check did not read a published face")
    elif cc.get("rows_read") != counts.get("e628_published_duplicate_rows"):
        p.append("the E628 cross-check read %r rows against the published %r"
                 % (cc.get("rows_read"), counts.get("e628_published_duplicate_rows")))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e629_caller_write.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("for every outside-origin duplicate row E628 published, resolve the holding "
                   "definition and the receiver's parameter position, find all call sites of that "
                   "name in the same module, map the argument that reaches the parameter, and ask "
                   "whether the caller's scope writes the key on that argument's leftmost name "
                   "before or after the call"),
        "population_source": ("the duplicate rows of results/state_tilt/receiverorigin_latest.json "
                              "whose origin_before_the_e627_interval_start is true, re-read from "
                              "their modules in scripts/ with ast.parse"),
        "counts": counts_of(m),
        "e628_cross_check": {
            "published": m["e628"]["published"],
            "rows_read": len(m["e628"]["rows"]),
            "e628_verdict": m["e628"].get("face_verdict"),
            "unparsed": m["unparsed"],
        },
        "rows": m["rows"],
        "limits": [
            "one hop only: a caller whose own argument comes from its caller (or another module) "
            "is not followed, so 'no caller writes it' is a bound on this hop, not on the program",
            "a write is read at name level through E625's marks on the spelled argument text; an "
            "alias of the caller's argument is not tracked",
            "call sites are matched by spelled callee name (bare or attribute), so a call through "
            "an imported alias of a different name is invisible",
            "no class/attribute resolution: an argument spelled self.x is traced by its base name "
            "only, and no attribute write on it is looked for beyond E625's marks",
            "a caller write cannot separate the two reads because both sit inside the callee -- "
            "the study publishes that consequence explicitly rather than counting a found writer "
            "as a closed duplicate",
            "the population is E628's published rows; this study offers no re-derivation of which "
            "rows are duplicates",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def build(root=ROOT):
    return face_from(measure(root=root))


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import io, json

MOD = {"k": 1}


def simulate(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["k"]
    seen.append(m["k"])
    json.dump(face, io.open("x", "w"))
    return seen


def caller_writes_before(m):
    m["k"] = 2
    return simulate(m)


def caller_writes_after(m):
    out = simulate(m)
    m["k"] = 3
    return out


def caller_never_writes(m):
    return simulate(m)


def caller_passes_a_call_result():
    return simulate(make_face())


def no_argument():
    return simulate()


def clean_holder(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["k"]
    seen.append(m["k"])
    json.dump(face, io.open("x", "w"))
    return seen


def clean_caller(m):
    return clean_holder(m)


def late_holder(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["k"]
    seen.append(m["k"])
    json.dump(face, io.open("x", "w"))
    return seen


def late_caller(m):
    out = late_holder(m)
    m["k"] = 3
    return out


def untraced_holder(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["k"]
    seen.append(m["k"])
    json.dump(face, io.open("x", "w"))
    return seen


def untraced_caller():
    return untraced_holder(make_face())


def never_called(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["k"]
    seen.append(m["k"])
    json.dump(face, io.open("x", "w"))
    return seen


MOD["k"] = 9
simulate(MOD)
caller_writes_before({"k": 1})
caller_writes_after({"k": 1})
caller_never_writes({"k": 1})
caller_passes_a_call_result()
no_argument()
clean_caller({"k": 1})
late_caller({"k": 1})
untraced_caller()
'''


def _fixture_rows():
    tree = ast.parse(FIXTURE)
    graph = e622_call_graph(tree, "fixture")
    rows, _inert = e628.origin_facts(tree, "fixture", graph)
    for r in rows:
        r["module"] = "scripts/fixture.py"
    dup = [r for r in rows
           if r.get("corrected_class") == e624.CORRECTED[0]
           and r.get("sibling_read_reads_the_same_object_after_the_dead_line")
           and r.get("origin_before_the_e627_interval_start") is True
           and r.get("receiver_origin") == e628.PARAM]
    return tree, dup


def selftest():
    legs = []
    tree, dup = _fixture_rows()
    facts = [row_facts_tree(tree, r) for r in dup]
    by_fn = {f["function"]: f for f in facts}

    legs.append(("the fixture yields the outside-origin parameter duplicates", len(dup) >= 4))
    legs.append(("every fixture row carries a verified parameter",
                 all(f["parameter_verified"] for f in facts)))

    def cls(name):
        f = by_fn.get(name)
        return f["duplicate_class_after_the_caller_arm"] if f else None

    legs.append(("the row called from a writing caller is priced as writer-before",
                 cls("simulate") == ROW_BEFORE))
    legs.append(("the row whose only caller writes after the call is priced as after",
                 cls("late_holder") == ROW_AFTER))
    legs.append(("the row whose only caller never writes is left open",
                 cls("clean_holder") == ROW_UNWRITTEN))
    legs.append(("the row called only with a call result cannot be traced",
                 cls("untraced_holder") == ROW_UNTRACED))
    legs.append(("the row with no call site in the module is priced as no-call",
                 row_class([], True) == ROW_NO_CALL))

    sites = {s["line"]: s for s in by_fn["simulate"]["call_sites"]}
    classes = [s["site_class"] for s in by_fn["simulate"]["call_sites"]]
    legs.append(("a writing caller is marked writer-before", SITE_BEFORE in classes))
    legs.append(("a non-writing caller is marked unwritten", SITE_UNWRITTEN in classes))
    legs.append(("a call with no argument for the parameter stands on its default",
                 SITE_MISSING in classes))
    legs.append(("a call passing a call result carries no locatable name",
                 SITE_NOT_A_NAME in classes))
    legs.append(("a module-body call counts as a caller with its own scope",
                 "the_call_site_is_inside_the_holding_function_itself" not in classes
                 and any(s["caller"] is None for s in by_fn["simulate"]["call_sites"])))
    legs.append(("the module-body caller's pre-call write is seen",
                 any(s["caller"] is None and s["site_class"] == SITE_BEFORE
                     for s in by_fn["simulate"]["call_sites"])))
    legs.append(("a recursive call is not counted as a caller",
                 all(s["site_class"] != SITE_RECURSIVE for s in by_fn["simulate"]["call_sites"])))

    m = {"e628": {"published": True, "rows": [{}] * len(dup), "face_verdict": "fixture"},
         "rows": facts, "unparsed": []}
    c = counts_of(m)
    legs.append(("counts re-add the row table", c["population_duplicate_rows"] == len(facts)))
    legs.append(("the row classes add up to the row count",
                 sum(c["row_" + k] for k in ROW_CLASSES) == len(facts)))
    legs.append(("the caller arm closes nothing", c["rows_closed_by_the_caller_arm"] == 0))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems (%r)" % (problems[:2],), problems == []))
    bad = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
           "verdict": face["verdict"], "e628_cross_check": face["e628_cross_check"]}
    bad["counts"]["row_" + ROW_BEFORE] = int(bad["counts"]["row_" + ROW_BEFORE]) + 1
    legs.append(("a perturbed row count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
            "verdict": "other", "e628_cross_check": face["e628_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]) , "rows": [dict(r) for r in face["rows"]][:-1],
            "verdict": face["verdict"], "e628_cross_check": face["e628_cross_check"]}
    legs.append(("a dropped row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["rows"]]
    done = False
    for r in flipped:
        if r["duplicate_class_after_the_caller_arm"] == ROW_BEFORE:
            r["duplicate_class_after_the_caller_arm"] = ROW_UNWRITTEN
            done = True
            break
    bad4 = {"counts": dict(face["counts"]), "rows": flipped, "verdict": face["verdict"],
            "e628_cross_check": face["e628_cross_check"]}
    legs.append(("a row class silently changed fails face_problems",
                 done and face_problems(bad4) != []))
    bad5 = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
            "verdict": face["verdict"], "e628_cross_check": face["e628_cross_check"]}
    bad5["counts"]["rows_closed_by_the_caller_arm"] = 1
    legs.append(("claiming a closed duplicate fails face_problems", face_problems(bad5) != []))
    site_edit = [dict(r) for r in face["rows"]]
    hit = None
    for r in site_edit:
        for s in r["call_sites"]:
            if s["site_class"] == SITE_UNWRITTEN:
                s["writes_before_the_call"] = [{"line": 1, "form": "store_at_key"}]
                hit = True
                break
        if hit:
            break
    bad6 = {"counts": dict(face["counts"]), "rows": site_edit, "verdict": face["verdict"],
            "e628_cross_check": face["e628_cross_check"]}
    legs.append(("a pre-call write added to an unseen site fails face_problems",
                 hit and face_problems(bad6) != []))

    real = published_rows(ROOT)
    legs.append(("the real E628 face is on disk and publishes duplicate rows",
                 real["published"] is True and len(real["rows"]) >= 2))
    legs.append(("this study excludes itself from the population it reads",
                 not any(r["module"] and r["module"].split("/")[-1] in SELF_PARTS
                         for r in real["rows"])))
    built = measure(ROOT)
    legs.append(("the real population parses every holder module", built["unparsed"] == []))
    face2, problems2 = face_from(built)
    legs.append(("the built face has no problems (%r)" % (problems2[:2],), problems2 == []))

    failed = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS" if ok else "FAIL") + " :: " + name)
    print("%d/%d selftest legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        face, problems = build(root=ROOT)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("rows=%d call_sites=%d written_before=%d closed=%d open=%d untraced=%d"
          % (c["population_duplicate_rows"], c["call_sites_total"],
             c["call_sites_that_write_the_key_before_the_call"],
             c["rows_closed_by_the_caller_arm"], c["rows_left_open"], c["rows_untraced"]))
    for k in ROW_CLASSES:
        print("  %s=%d" % (k, c["row_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))