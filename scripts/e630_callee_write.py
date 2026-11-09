"""E630 -- does the callee a caller hands the object to write the key E629 could not decide?

E629 (r1647) publishes its own residue: of its 9 call sites, 6 hand the receiver object to *another
call inside the caller* (``random_masks(P, ...)``, ``rev_masks(P, W_)`` before ``simulate(P, ...)``).
A write inside that callee happens before the holder is even entered, so E629 could not see it and
could not rule it out either.

This card follows exactly that hop, one level deep:

  * for every E629 call site classed as "the argument is handed to another call in the caller",
    re-read the module, find the call on that line that carries the same argument text,
    and resolve its callee by spelled name (bare or attribute) to a definition in the same module;
  * map the argument onto that callee's parameter (positional or keyword), and
  * ask whether the callee writes ``key`` on that parameter -- using E625's write marks, so
    ``p[key] = ...``, ``p.update({key: ...})``, ``p.setdefault(key, ...)`` and ``p.pop(key)`` all
    count, while ``p.update(payload)`` with a payload this study cannot read leaves the answer open.

Two readings this card is built to keep separate:

  * whether a write exists at all in that callee (E629 could not see one), and
  * whether it could separate the two reads (it cannot: both reads sit inside the holder, and the
    callee runs before the holder is entered, so the duplicate stands either way).  The row class
    names that consequence rather than counting a found writer as a closed duplicate.

Deliberately NOT done: no second hop (a callee that hands the parameter further on is published as
such, not followed), no class/attribute resolution, no cross-module import graph, no alias analysis,
no runner, no fixture write, no re-derivation of which rows are duplicates.
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
FACE = "HANDEDWRITE.json"
LATEST = "handedwrite_latest.json"
STUDY = "E630_callee_write"
SELF_PARTS = {"e630_callee_write.py", "run_e630_smoke_leg.py", "_probe_e630.py"}

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402
import e625_sibling_read_value as e625                                              # noqa: E402
import e629_caller_write as e629                                                    # noqa: E402

FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)

H_WRITES = "the_callee_writes_the_key_on_the_parameter_it_receives"
H_UNNAMED = "the_callee_touches_the_parameter_in_a_way_this_study_cannot_name_at_the_key"
H_HANDS = "the_callee_hands_the_parameter_to_another_call"
H_SILENT = "the_callee_never_touches_the_key_on_the_parameter"
H_NO_DEF = "the_callee_is_not_defined_in_the_module"
H_NO_PARAM = "the_argument_cannot_be_mapped_to_a_parameter"
H_RECURSIVE = "the_callee_is_the_holding_function"
H_NOT_FOUND = "no_call_on_the_handoff_line_carries_the_receiver"
HANDOFF_CLASSES = [H_WRITES, H_UNNAMED, H_HANDS, H_SILENT, H_NO_DEF, H_NO_PARAM, H_RECURSIVE,
                   H_NOT_FOUND]

ROW_WRITES = ("a_callee_of_the_caller_writes_the_key_but_both_reads_sit_inside_the_holder_so_the_"
              "duplicate_stands")
ROW_SILENT = "no_callee_of_the_caller_writes_the_key_so_the_callee_arm_closes_nothing"
ROW_NO_HANDOFF = "no_handoff_in_this_row_so_the_callee_arm_has_nothing_to_follow"
ROW_UNTRACED = "the_handoff_cannot_be_resolved_so_the_callee_arm_decides_nothing"
ROW_CLASSES = [ROW_WRITES, ROW_SILENT, ROW_NO_HANDOFF, ROW_UNTRACED]

DECIDED = (H_WRITES, H_SILENT)


# ---------------------------------------------------------------- handoffs out of E629
def handoffs_of(row):
    """Every (call site, handoff call) pair E629 published for one row."""
    out = []
    for site in row.get("call_sites") or []:
        if site.get("site_class") != e629.SITE_HANDED:
            continue
        for h in site.get("handed_to_another_call") or []:
            out.append({"site_line": site.get("line"), "handoff_line": h.get("line"),
                        "argument": site.get("argument"),
                        "argument_base_name": site.get("argument_base_name")})
    return out


def calls_at(tree, line):
    return sorted([n for n in ast.walk(tree)
                   if isinstance(n, ast.Call) and n.lineno == line],
                  key=lambda c: c.col_offset)


def callee_name(call):
    f = call.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def definition_of(tree, name):
    """The module-level definition of ``name`` if there is one, else any definition of it."""
    top = [n for n in tree.body if isinstance(n, FUNC) and n.name == name]
    if top:
        return top[0]
    nested = [n for n in ast.walk(tree) if isinstance(n, FUNC) and n.name == name]
    return nested[0] if nested else None


def param_names(fn):
    a = fn.args
    return [x.arg for x in list(getattr(a, "posonlyargs", [])) + list(a.args)]


def param_for_argument(call, arg_node, fn):
    """Which parameter of ``fn`` receives ``arg_node``, plus how it was passed."""
    for i, a in enumerate(call.args):
        if a is arg_node:
            if isinstance(a, ast.Starred):
                return None, "starred"
            names = param_names(fn)
            if i < len(names):
                return names[i], "positional"
            if fn.args.vararg is not None:
                return fn.args.vararg.arg, "vararg"
            return None, "out_of_range"
    for kw in call.keywords:
        if kw.value is arg_node:
            names = param_names(fn)
            if kw.arg in names:
                return kw.arg, "keyword"
            if fn.args.kwarg is not None:
                return fn.args.kwarg.arg, "kwarg"
            return None, "keyword_not_in_signature"
    return None, "not_an_argument"


def resolve_handoff(tree, row, h):
    """Follow one handoff call to its definition and ask what it does to the key."""
    out = {"site_line": h["site_line"], "handoff_line": h["handoff_line"],
           "argument": h["argument"], "callee": None, "parameter": None,
           "passed_as": None, "writes_at_the_key": [], "unnamed_touches": [],
           "handed_on": [], "handoff_class": H_NOT_FOUND,
           "precedes_the_holder_call": bool(h["site_line"]) and
           bool(h["handoff_line"]) and h["handoff_line"] <= h["site_line"]}
    if h.get("argument") is None:
        return out
    for call in calls_at(tree, h["handoff_line"]):
        name = callee_name(call)
        if name is None:
            continue
        for node in list(call.args) + [kw.value for kw in call.keywords]:
            if e624.text_of(node) != h["argument"]:
                continue
            out["callee"] = name
            if name == row.get("function"):
                out["handoff_class"] = H_RECURSIVE
                return out
            fn = definition_of(tree, name)
            if fn is None:
                out["handoff_class"] = H_NO_DEF
                return out
            pname, how = param_for_argument(call, node, fn)
            out["passed_as"] = how
            out["parameter"] = pname
            if pname is None:
                out["handoff_class"] = H_NO_PARAM
                return out
            named, unnamed, handed = e625.write_marks(e623.own_scope(fn), pname,
                                                      row.get("key"), pname)
            out["writes_at_the_key"] = named
            out["unnamed_touches"] = unnamed
            out["handed_on"] = handed
            if named:
                out["handoff_class"] = H_WRITES
            elif unnamed:
                out["handoff_class"] = H_UNNAMED
            elif handed:
                out["handoff_class"] = H_HANDS
            else:
                out["handoff_class"] = H_SILENT
            return out
    return out


def row_class(handoffs):
    if not handoffs:
        return ROW_NO_HANDOFF
    if any(h["handoff_class"] == H_WRITES for h in handoffs):
        return ROW_WRITES
    if all(h["handoff_class"] in DECIDED for h in handoffs):
        return ROW_SILENT
    return ROW_UNTRACED


def row_facts_tree(tree, row):
    resolved = [resolve_handoff(tree, row, h) for h in handoffs_of(row)]
    handoffs = [h for h in resolved if h["handoff_class"] != H_RECURSIVE]
    out = {"module": row.get("module"), "function": row.get("function"),
           "def_line": row.get("def_line"), "line": row.get("line"), "key": row.get("key"),
           "receiver_base_name": row.get("receiver_base_name"),
           "handoffs": handoffs,
           "the_holder_call_itself": [h for h in resolved if h["handoff_class"] == H_RECURSIVE],
           "row_class_after_the_callee_arm": ROW_UNTRACED}
    out["row_class_after_the_callee_arm"] = row_class(handoffs)
    return out


# ---------------------------------------------------------------- population and measurement
def published_rows(root=ROOT):
    """E629's rows, re-read from the face it published."""
    path = os.path.join(root, "results", "state_tilt", e629.LATEST)
    out = {"published": False, "rows": [], "face_verdict": None}
    if not os.path.exists(path):
        out["note"] = "no published E629 face on disk"
        return out
    doc = json.load(io.open(path, encoding="utf-8"))
    rows = [{"module": r.get("module"), "function": r.get("function"),
             "def_line": r.get("def_line"), "line": r.get("line"), "key": r.get("key"),
             "receiver_base_name": r.get("receiver_base_name"),
             "call_sites": r.get("call_sites") or [],
             "duplicate_class_after_the_caller_arm":
                 r.get("duplicate_class_after_the_caller_arm")}
            for r in (doc.get("rows") or [])]
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
    return {"e629": pub, "rows": facts, "unparsed": unparsed}


def counts_of(m):
    rows = m["rows"]
    rc = {k: 0 for k in ROW_CLASSES}
    hc = {k: 0 for k in HANDOFF_CLASSES}
    handoffs = []
    for r in rows:
        rc[r["row_class_after_the_callee_arm"]] = rc.get(r["row_class_after_the_callee_arm"], 0) + 1
        for h in r["handoffs"]:
            handoffs.append(h)
            hc[h["handoff_class"]] = hc.get(h["handoff_class"], 0) + 1
    c = {
        "population_rows": len(rows),
        "e629_published_rows": len(m["e629"]["rows"]),
        "modules_that_will_not_parse": len(m["unparsed"]),
        "rows_with_a_handoff": sum(1 for r in rows if r["handoffs"]),
        "handoffs_total": len(handoffs),
        "handoffs_that_are_the_holder_call_itself": sum(
            len(r.get("the_holder_call_itself") or []) for r in rows),
        "handoffs_resolved_to_a_definition": sum(
            1 for h in handoffs
            if h["handoff_class"] in (H_WRITES, H_UNNAMED, H_HANDS, H_SILENT)),
        "handoffs_the_callee_writes_the_key": hc[H_WRITES],
        "handoffs_the_callee_touches_the_key_unnamed": hc[H_UNNAMED],
        "handoffs_the_callee_hands_the_parameter_on": hc[H_HANDS],
        "handoffs_the_callee_never_touches_the_key": hc[H_SILENT],
        "handoffs_without_a_definition_in_the_module": hc[H_NO_DEF],
        "handoffs_the_argument_cannot_be_mapped": hc[H_NO_PARAM],
        "handoffs_that_are_recursive": hc[H_RECURSIVE],
        "handoffs_not_found_on_the_line": hc[H_NOT_FOUND],
        "handoffs_that_precede_the_holder_call": sum(
            1 for h in handoffs if h["precedes_the_holder_call"]),
        "rows_a_callee_writes_the_key": rc[ROW_WRITES],
        "rows_no_callee_writes_the_key": rc[ROW_SILENT],
        "rows_with_no_handoff": rc[ROW_NO_HANDOFF],
        "rows_untraced": rc[ROW_UNTRACED],
        "rows_closed_by_the_callee_arm": 0,
        "rows_left_open": rc[ROW_WRITES] + rc[ROW_SILENT] + rc[ROW_NO_HANDOFF] + rc[ROW_UNTRACED],
    }
    for k in ROW_CLASSES:
        c["row_" + k] = rc[k]
    for k in HANDOFF_CLASSES:
        c["handoff_" + k] = hc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if not m["e629"]["published"]:
        return "no_published_e629_face_to_price"
    if c["handoffs_total"] == 0:
        return "e629_published_no_handoff_so_the_callee_arm_has_nothing_to_price"
    if c["modules_that_will_not_parse"]:
        return "some_holder_modules_no_longer_parse_so_the_callee_arm_is_incomplete"
    if c["handoffs_the_callee_writes_the_key"] == 0:
        if c["handoffs_the_callee_touches_the_key_unnamed"] == 0:
            return ("none_of_the_%d_handoffs_reaches_a_callee_that_writes_the_key_so_the_callee_arm_"
                    "closes_none_of_the_%d_row" % (c["handoffs_total"], c["population_rows"]))
        return ("none_of_the_%d_handoffs_reaches_a_callee_that_names_the_key_and_%d_touch_it_"
                "unnamed_so_the_callee_arm_closes_none_of_the_%d_row"
                % (c["handoffs_total"], c["handoffs_the_callee_touches_the_key_unnamed"],
                   c["population_rows"]))
    return ("%d_of_the_%d_handoffs_reaches_a_callee_that_writes_the_key_but_that_write_precedes_"
            "both_reads_so_the_callee_arm_closes_none_of_the_%d_row"
            % (c["handoffs_the_callee_writes_the_key"], c["handoffs_total"], c["population_rows"]))


def answer_of(m):
    c = counts_of(m)
    if not m["e629"]["published"]:
        return "E629's face is not on disk, so there is no callee arm to price"
    sites = m["e629"].get("face_counts", {}).get("call_sites_total")
    sites = sites if isinstance(sites, int) else 0
    return ("E629 published %d row(s) over %d call site(s).  %d of those rows hand the object to "
            "another call inside the caller, for %d handoff(s) in total; %d resolve to a definition "
            "in the same module and %d do not.  Of the resolved handoffs, %d land in a callee that "
            "writes the key on the parameter it receives, %d touch it in a way this study cannot "
            "name, %d hand the parameter further on and %d never touch it.  Every handoff call sits "
            "before the holder call (%d of %d), so even a callee write precedes both reads: the "
            "callee arm closes none of the %d row, and %d row(s) stay untraced at this hop"
            % (c["e629_published_rows"], sites,
               c["rows_with_a_handoff"], c["handoffs_total"],
               c["handoffs_resolved_to_a_definition"],
               c["handoffs_total"] - c["handoffs_resolved_to_a_definition"],
               c["handoffs_the_callee_writes_the_key"],
               c["handoffs_the_callee_touches_the_key_unnamed"],
               c["handoffs_the_callee_hands_the_parameter_on"],
               c["handoffs_the_callee_never_touches_the_key"],
               c["handoffs_that_precede_the_holder_call"], c["handoffs_total"],
               c["population_rows"], c["rows_untraced"] + c["rows_with_no_handoff"]))


# ---------------------------------------------------------------- face problems
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    rows = face.get("rows") or []
    if counts.get("population_rows") != len(rows):
        p.append("counts.population_rows says %r but the face publishes %d rows"
                 % (counts.get("population_rows"), len(rows)))
    rc = {k: 0 for k in ROW_CLASSES}
    hc = {k: 0 for k in HANDOFF_CLASSES}
    handoffs = []
    for r in rows:
        cls = r.get("row_class_after_the_callee_arm")
        if cls not in ROW_CLASSES:
            p.append("row %r in %r carries row_class_after_the_callee_arm=%r"
                     % (r.get("line"), r.get("function"), cls))
        else:
            rc[cls] += 1
        for h in r.get("handoffs") or []:
            handoffs.append(h)
            hcls = h.get("handoff_class")
            if hcls not in HANDOFF_CLASSES:
                p.append("handoff on line %r of %r carries class %r"
                         % (h.get("handoff_line"), r.get("function"), hcls))
                continue
            hc[hcls] += 1
            if bool(h.get("writes_at_the_key")) != (hcls == H_WRITES):
                p.append("handoff on line %r of %r publishes %d named write(s) under class %r"
                         % (h.get("handoff_line"), r.get("function"),
                            len(h.get("writes_at_the_key") or []), hcls))
        if cls in ROW_CLASSES:
            want = row_class([h for h in (r.get("handoffs") or [])
                              if h.get("handoff_class") in HANDOFF_CLASSES])
            if want != cls:
                p.append("row %r in %r says %r but its handoffs force %r"
                         % (r.get("line"), r.get("function"), cls, want))
    for k in ROW_CLASSES:
        if counts.get("row_" + k) != rc[k]:
            p.append("counts.row_%s does not re-derive from the rows" % k)
    if sum(rc.values()) != len(rows):
        p.append("the row classes do not add up to the published row count")
    for k in HANDOFF_CLASSES:
        if counts.get("handoff_" + k, 0) != hc.get(k, 0):
            p.append("counts.handoff_%s does not re-derive from the handoffs" % k)
    if len(handoffs) != counts.get("handoffs_total"):
        p.append("counts.handoffs_total says %r but the rows publish %d"
                 % (counts.get("handoffs_total"), len(handoffs)))
    if counts.get("rows_closed_by_the_callee_arm") != 0:
        p.append("counts.rows_closed_by_the_callee_arm is %r -- a callee write precedes both reads"
                 % counts.get("rows_closed_by_the_callee_arm"))
    if counts.get("handoffs_that_precede_the_holder_call") != \
            sum(1 for h in handoffs if h.get("precedes_the_holder_call")):
        p.append("counts.handoffs_that_precede_the_holder_call does not re-derive")
    if counts.get("handoffs_that_are_the_holder_call_itself") != \
            sum(len(r.get("the_holder_call_itself") or []) for r in rows):
        p.append("counts.handoffs_that_are_the_holder_call_itself does not re-derive")
    derived = derive_verdict({
        "e629": {"published": True,
                 "rows": [None] * (counts.get("e629_published_rows") or 0)},
        "rows": rows,
        "unparsed": [None] * (counts.get("modules_that_will_not_parse") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the row table forces (%r)"
                 % (face.get("verdict"), derived))
    cc = face.get("e629_cross_check") or {}
    if cc.get("published") is False:
        p.append("the E629 cross-check did not read a published face")
    elif cc.get("rows_read") != counts.get("e629_published_rows"):
        p.append("the E629 cross-check read %r rows against the published %r"
                 % (cc.get("rows_read"), counts.get("e629_published_rows")))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e630_callee_write.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("for every E629 call site classed as handing the receiver to another call in the "
                   "caller, re-read the module, find the call on the handoff line that carries the "
                   "same argument text, resolve its callee to a definition in the same module, map "
                   "the argument to that callee's parameter and ask whether the callee writes the "
                   "key on that parameter"),
        "population_source": ("the rows of results/state_tilt/callerwrite_latest.json and their "
                              "call sites E629 classed as 'the argument is handed to another call in "
                              "the caller', re-read from their modules in scripts/ with ast.parse"),
        "counts": counts_of(m),
        "e629_cross_check": {
            "published": m["e629"]["published"],
            "rows_read": len(m["e629"]["rows"]),
            "e629_verdict": m["e629"].get("face_verdict"),
            "unparsed": m["unparsed"],
        },
        "rows": m["rows"],
        "limits": [
            "one hop only: a callee that hands the parameter further on is published as such and "
            "not followed, so 'no callee writes it' is a bound on this hop",
            "a write is read at name level through E625's marks on the callee's parameter name; an "
            "alias of the parameter inside the callee is not tracked",
            "callees are resolved by spelled name inside the same module, so a function imported "
            "under a different name, a lambda, or a method on a class is not resolved",
            "the handoff call is located by line and by an argument whose text equals the receiver "
            "text; a handoff on a line with two identical arguments picks the first match",
            "a callee write happens before the holder is entered, so it reaches both the dead line "
            "and its sibling read -- the study publishes that consequence instead of counting a "
            "found writer as a closed duplicate",
            "the population is E629's published rows; this study offers no re-derivation of which "
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
MOD = {"k": 1}

def holder_written(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def helper_write(p):
    p["k"] = 2
    return p

def call_written(m):
    helper_write(m)
    return holder_written(m)

def holder_silent(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def helper_read(p):
    return p["n"]

def call_silent(m):
    helper_read(m)
    return holder_silent(m)

def holder_unnamed(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def helper_unnamed(p, payload):
    p.update(payload)

def call_unnamed(m):
    helper_unnamed(m, MOD)
    return holder_unnamed(m)

def holder_undefined(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def call_undefined(m):
    not_there(m)
    return holder_undefined(m)

def holder_two(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def helper_silent2(p):
    return p["k"]

def call_two_handoffs(m):
    helper_write(m)
    helper_silent2(m)
    return holder_two(m)

def holder_keyword(m):
    seen = []
    first = m["k"]
    seen.append(m["k"])
    return seen

def helper_kw(p):
    p.setdefault("k", 0)

def call_keyword(m):
    helper_kw(p=m)
    return holder_keyword(m)
'''


def _fixture_rows(tree):
    fns = {f.name: f for f in ast.walk(tree) if isinstance(f, FUNC)}
    specs = [("call_written", "holder_written"), ("call_silent", "holder_silent"),
             ("call_unnamed", "holder_unnamed"), ("call_undefined", "holder_undefined"),
             ("call_two_handoffs", "holder_two"), ("call_keyword", "holder_keyword")]
    rows = []
    for caller, holder in specs:
        scope = e623.own_scope(fns[caller])
        calls = [n for n in scope if isinstance(n, ast.Call)]
        holder_calls = [c for c in calls
                        if isinstance(c.func, ast.Name) and c.func.id == holder]
        handoffs = [c for c in calls
                    if isinstance(c.func, ast.Name) and c.func.id != holder
                    and any(e624.text_of(a) == "m"
                            for a in list(c.args) + [kw.value for kw in c.keywords])]
        rows.append({
            "module": "scripts/fixture.py", "function": holder,
            "def_line": fns[holder].lineno, "line": fns[holder].lineno + 2,
            "key": "k", "receiver_base_name": "m",
            "call_sites": [{
                "line": holder_calls[0].lineno if holder_calls else None,
                "site_class": e629.SITE_HANDED, "argument": "m",
                "argument_base_name": "m",
                "handed_to_another_call": [
                    {"line": c.lineno, "form": "receiver_handed_to_a_call"} for c in handoffs],
            }],
        })
    return rows


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    facts = [row_facts_tree(tree, r) for r in _fixture_rows(tree)]
    by_fn = {f["function"]: f for f in facts}

    def rcls(name):
        f = by_fn.get(name)
        return f["row_class_after_the_callee_arm"] if f else None

    legs.append(("the fixture yields one row per holder", len(facts) == 6))
    legs.append(("a callee that writes the key is found", rcls("holder_written") == ROW_WRITES))
    legs.append(("a callee that only reads leaves the row silent",
                 rcls("holder_silent") == ROW_SILENT))
    legs.append(("a callee that touches the key unnamed leaves the row untraced",
                 rcls("holder_unnamed") == ROW_UNTRACED))
    legs.append(("a callee with no definition in the module leaves the row untraced",
                 rcls("holder_undefined") == ROW_UNTRACED))
    legs.append(("one writing handoff among two decides the row",
                 rcls("holder_two") == ROW_WRITES))
    legs.append(("a keyword handoff maps to the parameter and finds setdefault",
                 rcls("holder_keyword") == ROW_WRITES))
    hc = {f["function"]: f["handoffs"] for f in facts}
    legs.append(("the written handoff names the key it stores",
                 any(w["form"] == "store_at_key"
                     for h in hc["holder_two"] for w in h["writes_at_the_key"])))
    legs.append(("a keyword handoff is published as keyword",
                 any(h["passed_as"] == "keyword" for h in hc["holder_keyword"])))
    legs.append(("every handoff precedes the holder call in the fixture",
                 all(h["precedes_the_holder_call"] for f in facts for h in f["handoffs"])))

    m = {"e629": {"published": True, "rows": [{}] * len(facts), "face_counts": {}},
         "rows": facts, "unparsed": []}
    c = counts_of(m)
    legs.append(("counts re-add the row table", c["population_rows"] == len(facts)))
    legs.append(("the row classes add up to the row count",
                 sum(c["row_" + k] for k in ROW_CLASSES) == len(facts)))
    legs.append(("the handoff classes add up to the handoff count",
                 sum(c["handoff_" + k] for k in HANDOFF_CLASSES) == c["handoffs_total"]))
    legs.append(("the callee arm closes nothing", c["rows_closed_by_the_callee_arm"] == 0))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems (%r)" % (problems[:2],), problems == []))
    bad = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
           "verdict": face["verdict"], "e629_cross_check": face["e629_cross_check"]}
    bad["counts"]["handoff_" + H_WRITES] = int(bad["counts"]["handoff_" + H_WRITES]) + 1
    legs.append(("a perturbed handoff count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
            "verdict": "other", "e629_cross_check": face["e629_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]][:-1],
            "verdict": face["verdict"], "e629_cross_check": face["e629_cross_check"]}
    legs.append(("a dropped row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["rows"]]
    done = False
    for r in flipped:
        if r["row_class_after_the_callee_arm"] == ROW_WRITES:
            r["row_class_after_the_callee_arm"] = ROW_SILENT
            done = True
            break
    bad4 = {"counts": dict(face["counts"]), "rows": flipped, "verdict": face["verdict"],
            "e629_cross_check": face["e629_cross_check"]}
    legs.append(("a row class silently changed fails face_problems",
                 done and face_problems(bad4) != []))
    bad5 = {"counts": dict(face["counts"]), "rows": [dict(r) for r in face["rows"]],
            "verdict": face["verdict"], "e629_cross_check": face["e629_cross_check"]}
    bad5["counts"]["rows_closed_by_the_callee_arm"] = 1
    legs.append(("claiming a closed duplicate fails face_problems", face_problems(bad5) != []))

    real = published_rows(ROOT)
    legs.append(("the real E629 face is on disk", real["published"] is True))
    legs.append(("this study excludes itself from the population it reads",
                 not any(r["module"] and r["module"].split("/")[-1] in SELF_PARTS
                         for r in real["rows"])))
    built = measure(ROOT)
    legs.append(("the real population parses every holder module", built["unparsed"] == []))
    face2, problems2 = face_from(built)
    legs.append(("the built face has no problems (%r)" % (problems2[:2],), problems2 == []))
    if built["rows"]:
        legs.append(("the built face prices at least one handoff",
                     face2["counts"]["handoffs_total"] > 0))

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
    print("rows=%d handoffs=%d writes=%d silent=%d untraced_rows=%d closed=%d"
          % (c["population_rows"], c["handoffs_total"],
             c["handoffs_the_callee_writes_the_key"],
             c["handoffs_the_callee_never_touches_the_key"], c["rows_untraced"],
             c["rows_closed_by_the_callee_arm"]))
    for k in ROW_CLASSES:
        print("  %s=%d" % (k, c["row_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))