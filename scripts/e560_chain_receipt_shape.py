"""E560 (r1586 bm-b): does the chain receipt carry enough to triage without the console?

E559 established that nothing reads a chain receipt and nothing schedules the chain, so the only
record of a failing leg is the file the runner writes.  This study prices that file.

Population = the three chain runners on disk (Tools/s6_chain_bm{a,b,c}.py), read statically, plus
every receipt they have already written under results/.  Per runner the study measures:

  * the loop's failure policy (does a non-zero rc stop the remaining legs?),
  * the row schema (which keys a leg row carries, whether stderr is kept, how many characters of
    output survive),
  * whether an exception and a timeout are distinguishable from a plain non-zero exit,
  * whether a leg that never ran is representable at all, and
  * whether the receipt is written incrementally (a killed run keeps nothing).

Then it asks the only question a reader cares about: of the three fields a triager needs -- the
failing leg's name, its rc with its kind, and enough of its output -- how many survive into the
file.  Every class is re-derived from the published row, never trusted.
"""

import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "chainreceiptshape_latest.json")
DATED_PREFIX = "CHAINRECEIPTSHAPE"
EVIDENCE_CUTOFF = "2026-11-08"

RUNNERS = [
    "Tools/s6_chain_bma.py",
    "Tools/s6_chain_bmb.py",
    "Tools/s6_chain_bmc.py",
]

# failure policies
P_CONTINUES = "runs_every_leg_after_a_failure"
P_ABORTS = "stops_the_chain_at_the_first_failure"

# rc-kind arms
RC_SPLIT = "timeout_is_distinct_from_a_plain_exit"
RC_COLLAPSED = "every_exception_collapses_into_one_sentinel"

# output arms
OUT_ONE_LINE = "one_truncated_stdout_line"
OUT_WITH_STDERR = "stdout_and_stderr_kept"

# expected-total arms
TOT_EXPECTED = "the_receipt_states_the_table_size"
TOT_ATTEMPTED = "the_receipt_counts_only_the_rows_it_attempted"
TOT_NONE = "the_receipt_states_no_total_at_all"

# unrun arms
UN_SYNTHETIC = "a_missing_script_gets_a_placeholder_row"
UN_NONE = "a_leg_that_never_ran_leaves_no_row"

TRIAGE_FIELDS = ("first_failing_leg", "rc_with_its_kind", "its_own_output")


# ---- source reading ------------------------------------------------------------
def _read(path):
    # utf-8-sig: Tools/s6_chain_bmb.py carries a BOM, and ast.parse rejects U+FEFF (E559's trap,
    # hit again here: the first build died on "invalid non-printable character U+FEFF").
    with io.open(os.path.join(ROOT, path), encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def _tail(src, node):
    return ast.get_source_segment(src, node) or ""


def _legs_table(tree, path, depth=0):
    """(count, source) for the LEGS table.

    bm-a's runner does not own a table: it imports LEGS from bm-c's file so the two lists cannot
    drift.  A scan that only looks for ``LEGS = [...]`` reads that runner as having no legs at
    all, which is the first version of this study's own defect.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                return len(node.value.elts), "own"
            # LEGS = canonical.LEGS, where canonical was imported from a sibling module
            if isinstance(node.value, ast.Attribute) and node.value.attr == "LEGS" \
                    and isinstance(node.value.value, ast.Name):
                alias = node.value.value.id
                for imp in ast.walk(tree):
                    if isinstance(imp, ast.Import) and depth < 2:
                        for a in imp.names:
                            if (a.asname or a.name) != alias:
                                continue
                            base = os.path.dirname(path)
                            cand = os.path.join(base, a.name.split(".")[-1] + ".py")
                            if os.path.isfile(os.path.join(ROOT, cand)):
                                with io.open(os.path.join(ROOT, cand), encoding="utf-8-sig",
                                             errors="replace") as fh:
                                    sub = ast.parse(fh.read())
                                n, _ = _legs_table(sub, cand, depth + 1)
                                return n, "imported:" + cand.replace("\\", "/")
    if depth >= 2:
        return 0, "unresolved"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and any(
                a.name == "LEGS" for a in node.names):
            base = os.path.dirname(path)
            cand = os.path.join(base, node.module.split(".")[-1] + ".py")
            if os.path.isfile(os.path.join(ROOT, cand)):
                with io.open(os.path.join(ROOT, cand), encoding="utf-8-sig",
                             errors="replace") as fh:
                    sub = ast.parse(fh.read())
                n, _ = _legs_table(sub, cand, depth + 1)
                return n, "imported:" + cand.replace("\\", "/")
    return 0, "unresolved"


def _dict_keys(node):
    out = []
    if isinstance(node, ast.Dict):
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                out.append(k.value)
    return out


def _name_of(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_name(call):
    f = call.func
    if isinstance(f, ast.Attribute):
        base = _name_of(f.value)
        return (base + "." + f.attr) if base else f.attr
    return _name_of(f)


def _loop_nodes(tree):
    """The leg loop: a For whose body spawns a subprocess and appends a row."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        body_src = " ".join(_call_name(c) or "" for c in ast.walk(node)
                            if isinstance(c, ast.Call))
        appends = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                      and c.func.attr == "append" for c in ast.walk(node))
        if "subprocess" in body_src and appends:
            hits.append(node)
    return hits


def _handler_types(loop):
    found = []
    for node in ast.walk(loop):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                found.append("bare")
            elif isinstance(node.type, ast.Name):
                found.append(node.type.id)
            elif isinstance(node.type, ast.Attribute):
                found.append(_name_of(node.type))
    return sorted(set(found))


def _constant_rc(src, loop):
    """rc sentinels assigned inside a handler body (rc = 124 / rc = 99)."""
    out = {}
    handlers = [h for n in ast.walk(loop) if isinstance(n, ast.Try)
                for h in n.handlers]
    for h in handlers:
        tnames = []
        if isinstance(h.type, ast.Name):
            tnames = [h.type.id]
        elif isinstance(h.type, ast.Attribute):
            tnames = [_name_of(h.type)]
        elif isinstance(h.type, ast.Tuple):
            tnames = [_name_of(e) for e in h.type.elts]
        for sub in ast.walk(h):
            if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Constant) \
                    and isinstance(sub.value.value, int):
                for t in sub.targets:
                    if isinstance(t, ast.Name) and t.id == "rc":
                        for tname in tnames or ["bare"]:
                            out[tname] = sub.value.value
    return out


def _row_dicts(loop):
    """Every dict literal appended to the rows list inside the leg loop.

    A runner may append from more than one branch (a placeholder row for a script that is not on
    disk, the normal row otherwise); reading only the first one made the placeholder invisible.
    """
    out = []
    for node in ast.walk(loop):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "append":
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    out.append(arg)
    return out


def _tail_slice(rowdicts):
    """The character budget applied to the output line, if any."""
    best = None
    for rowdict in rowdicts:
        for node in ast.walk(rowdict):
            if not isinstance(node, ast.Subscript):
                continue
            # tail[0][:220] -- the budget lives in the Slice's upper bound, not in a Constant
            # slice; reading only Constant slices reported 0 characters kept for all three
            # runners while their rows keep 220/300.
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
                best = node.slice.value if best is None else max(best, node.slice.value)
            elif isinstance(node.slice, ast.Slice) and isinstance(node.slice.upper, ast.Constant) \
                    and isinstance(node.slice.upper.value, int):
                v = node.slice.upper.value
                best = v if best is None else max(best, v)
    return best


def _payload_call(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) == "json.dump" and node.args:
            return node
    return None


def _receipt_shape(tree):
    call = _payload_call(tree)
    if call is None:
        return None, [], None
    arg = call.args[0]
    if isinstance(arg, ast.Dict):
        return "dict", _dict_keys(arg), arg
    if isinstance(arg, ast.Name):
        return "list", [], arg
    return "other", [], arg


def facts_for(path):
    src = _read(path)
    tree = ast.parse(src)
    loops = _loop_nodes(tree)
    breaks = 0
    writes_inside = 0
    for loop in loops:
        breaks += sum(1 for n in ast.walk(loop)
                      if isinstance(n, (ast.Break, ast.Return)))
        writes_inside += sum(1 for n in ast.walk(loop)
                            if isinstance(n, ast.Call) and _call_name(n) == "json.dump")
    rc_const = _constant_rc(src, loops[0]) if loops else {}
    rowdicts = _row_dicts(loops[0]) if loops else []
    row_keys = sorted({k for d in rowdicts for k in _dict_keys(d)})
    shape, keys, _arg = _receipt_shape(tree)

    # counts of legs in the LEGS table (a list of (name, argv) tuples, possibly imported)
    legs_count, legs_src = _legs_table(tree, path)

    stderr_read = ".stderr" in src
    rowdict_src = "\n".join(ast.get_source_segment(src, d) or "" for d in rowdicts)
    synthetic = "MISSING" in rowdict_src

    f = {
        "path": path,
        "legs_in_table": legs_count,
        "legs_table_source": legs_src,
        "leg_loops": len(loops),
        "loop_failure_policy": P_ABORTS if breaks else P_CONTINUES,
        "breaks_or_returns_in_loop": breaks,
        "row_keys": sorted(row_keys),
        "output_chars_kept": _tail_slice(rowdicts),
        "stderr_read": stderr_read,
        "caught_exceptions": _handler_types(loops[0]) if loops else [],
        "rc_constants": rc_const,
        "receipt_shape": shape,
        "receipt_keys": sorted(keys),
        "receipt_written_inside_loop": writes_inside > 0,
        "synthetic_unrun_row": synthetic,
        "row_names_stderr": "stderr" in rowdict_src,
    }
    f.update(triage_from_facts(f))
    return f


def triage_from_facts(f):
    """The three fields a triager needs, each decided only by the row's own facts."""
    caught = set(f["caught_exceptions"])
    # "one sentinel for everything" only when a generic handler swallows every exception; a
    # runner that catches just TimeoutExpired keeps 124 distinct from a process exit code.
    rc_kind = RC_COLLAPSED if ("Exception" in caught or "bare" in caught) else RC_SPLIT
    # ... but that same narrow handler ends the run for any other exception, so the receipt may
    # not exist at all.  Published beside the rc arm, never folded into it.
    no_receipt_on_other_errors = rc_kind == RC_SPLIT
    output = OUT_WITH_STDERR if (f["stderr_read"] and f["row_names_stderr"]) else OUT_ONE_LINE
    keys = set(f["receipt_keys"])
    if "legs_in_table" in keys or "expected_legs" in keys or "legs_expected" in keys:
        total = TOT_EXPECTED
    elif keys & {"legs_total", "legs"}:
        total = TOT_ATTEMPTED
    else:
        total = TOT_NONE
    unrun = UN_SYNTHETIC if f["synthetic_unrun_row"] else UN_NONE
    # the first failing leg is implicit in any row list: the first row whose rc != 0
    first = "derivable_from_the_first_nonzero_row" if "rc" in set(f["row_keys"]) else "absent"
    return {
        "first_failing_leg": first,
        "rc_with_its_kind": rc_kind,
        "a_non_timeout_exception_ends_the_run": no_receipt_on_other_errors,
        "its_own_output": output,
        "expected_total": total,
        "unrun_representable": unrun,
        "triage_fields_usable": sum([
            first.startswith("derivable"),
            rc_kind == RC_SPLIT,
            output == OUT_WITH_STDERR,
        ]),
    }


# ---- already written receipts -------------------------------------------------
RECEIPT_RE = re.compile(r"^_r.+bm([abc])_s6_chain\.json$")


def receipt_rows():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "_r*bm*_s6_chain.json"))):
        name = os.path.basename(path)
        m = RECEIPT_RE.match(name)
        if not m:
            continue
        try:
            with io.open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as exc:
            out.append({"file": name, "machine": "bm-" + m.group(1), "unreadable": str(exc)[:80]})
            continue
        if isinstance(payload, list):
            rows, shape = payload, "list"
        elif isinstance(payload, dict):
            shape = "dict"
            got = payload.get("legs")
            # some receipts carry "legs" as a COUNT, not a row list; only a list is rows
            rows = got if isinstance(got, list) else []
        else:
            rows, shape = [], "other"
        rcs = [r.get("rc") for r in rows if isinstance(r, dict)]
        out.append({
            "file": name,
            "machine": "bm-" + m.group(1),
            "shape": shape,
            "rows": len(rows),
            "top_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
            "nonzero_rows": sum(1 for r in rcs if r not in (0, None)),
            "rc_values": sorted({r for r in rcs if r is not None}),
            "carries_stderr": bool(rows) and any(
                isinstance(r, dict) and ("stderr" in r or "err" in r) for r in rows),
        })
    return out


# ---- controls -----------------------------------------------------------------
CONTROL_SOURCES = {
    "abort_on_failure": '''
import json, subprocess
LEGS = [("a", ["python", "x.py"]), ("b", ["python", "y.py"])]
out = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True)
    out.append({"leg": name, "rc": r.returncode})
    if r.returncode != 0:
        break
json.dump(out, open("results/_r0bmb_s6_chain.json", "w"))
''',
    "stderr_kept": '''
import json, subprocess
LEGS = [("a", ["python", "x.py"])]
out = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True)
    out.append({"leg": name, "rc": r.returncode, "stderr": r.stderr[-400:]})
json.dump(out, open("results/_r0bmb_s6_chain.json", "w"))
''',
    "incremental_write": '''
import json, subprocess
LEGS = [("a", ["python", "x.py"])]
out = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True)
    out.append({"leg": name, "rc": r.returncode})
    json.dump(out, open("results/_r0bmb_s6_chain.json", "w"))
''',
    "states_table_size": '''
import json, subprocess
LEGS = [("a", ["python", "x.py"]), ("b", ["python", "y.py"])]
rows = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True)
    rows.append({"leg": name, "rc": r.returncode})
json.dump({"legs_expected": len(LEGS), "legs": rows},
          open("results/_r0bmb_s6_chain.json", "w"))
''',
    "collapses_exceptions": '''
import json, subprocess
LEGS = [("a", ["python", "x.py"])]
rows = []
for name, cmd in LEGS:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        rc = r.returncode
    except Exception as exc:
        rc = 99
    rows.append({"leg": name, "rc": rc})
json.dump({"legs": rows}, open("results/_r0bmb_s6_chain.json", "w"))
''',
    "synthetic_unrun_row": '''
import os, json, subprocess
LEGS = [("a", ["python", "x.py"])]
out = []
for name, cmd in LEGS:
    if not os.path.exists(cmd[1]):
        out.append({"leg": name, "rc": 127, "tail": "MISSING " + cmd[1]})
        continue
    r = subprocess.run(cmd, capture_output=True, text=True)
    out.append({"leg": name, "rc": r.returncode})
json.dump(out, open("results/_r0bmb_s6_chain.json", "w"))
''',
}


def _facts_from_source(src):
    """Run the same classifier over a fixture without touching disk."""
    tree = ast.parse(src)
    loops = _loop_nodes(tree)
    rc_const = _constant_rc(src, loops[0]) if loops else {}
    rowdicts = _row_dicts(loops[0]) if loops else []
    shape, keys, _arg = _receipt_shape(tree)
    legs_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                legs_count = len(node.value.elts)
    rowdict_src = "\n".join(ast.get_source_segment(src, d) or "" for d in rowdicts)
    f = {
        "path": "<fixture>",
        "legs_in_table": legs_count,
        "legs_table_source": "own",
        "leg_loops": len(loops),
        "loop_failure_policy": P_ABORTS if any(
            isinstance(n, (ast.Break, ast.Return)) for loop in loops for n in ast.walk(loop))
        else P_CONTINUES,
        "breaks_or_returns_in_loop": 0,
        "row_keys": sorted({k for d in rowdicts for k in _dict_keys(d)}),
        "output_chars_kept": _tail_slice(rowdicts),
        "stderr_read": ".stderr" in src,
        "caught_exceptions": _handler_types(loops[0]) if loops else [],
        "rc_constants": rc_const,
        "receipt_shape": shape,
        "receipt_keys": sorted(keys),
        "receipt_written_inside_loop": any(
            isinstance(n, ast.Call) and _call_name(n) == "json.dump"
            for loop in loops for n in ast.walk(loop)),
        "synthetic_unrun_row": "MISSING" in rowdict_src,
        "row_names_stderr": "stderr" in rowdict_src,
    }
    f.update(triage_from_facts(f))
    return f


# ---- build --------------------------------------------------------------------
def build(write=True):
    runners = [facts_for(p) for p in RUNNERS]
    runners.sort(key=lambda r: r["path"])
    receipts = receipt_rows()

    per_total = {}
    for r in receipts:
        d = per_total.setdefault(r["machine"], {"files": 0, "rows_min": None,
                                                "rows_max": 0, "with_nonzero": 0,
                                                "with_stderr_field": 0, "shapes": []})
        d["files"] += 1
        if r.get("rows") is not None:
            d["rows_min"] = r["rows"] if d["rows_min"] is None else min(d["rows_min"], r["rows"])
            d["rows_max"] = max(d["rows_max"], r["rows"])
        if r.get("nonzero_rows"):
            d["with_nonzero"] += 1
        if r.get("carries_stderr"):
            d["with_stderr_field"] += 1
        if r.get("shape") not in d["shapes"]:
            d["shapes"].append(r.get("shape"))
    for d in per_total.values():
        d["shapes"] = sorted(x for x in d["shapes"] if x)

    table = {}
    for r in runners:
        table[os.path.basename(r["path"])] = {
            "legs_in_table": r["legs_in_table"],
            "legs_table_source": r["legs_table_source"],
            "loop_failure_policy": r["loop_failure_policy"],
            "row_keys": r["row_keys"],
            "output_chars_kept": r["output_chars_kept"],
            "caught_exceptions": r["caught_exceptions"],
            "receipt_shape": r["receipt_shape"],
            "receipt_keys": r["receipt_keys"],
            "receipt_written_inside_loop": r["receipt_written_inside_loop"],
            "rc_with_its_kind": r["rc_with_its_kind"],
            "a_non_timeout_exception_ends_the_run": r["a_non_timeout_exception_ends_the_run"],
            "its_own_output": r["its_own_output"],
            "expected_total": r["expected_total"],
            "unrun_representable": r["unrun_representable"],
            "triage_fields_usable": r["triage_fields_usable"],
        }

    summary = {
        "runners": len(runners),
        "legs_total_in_tables": sum(r["legs_in_table"] for r in runners),
        "tables_imported": sum(1 for r in runners
                               if r["legs_table_source"].startswith("imported:")),
        "continues_after_failure": sum(1 for r in runners
                                       if r["loop_failure_policy"] == P_CONTINUES),
        "aborts_after_failure": sum(1 for r in runners
                                    if r["loop_failure_policy"] == P_ABORTS),
        "keeps_stderr": sum(1 for r in runners if r["its_own_output"] == OUT_WITH_STDERR),
        "rc_kind_distinguished": sum(1 for r in runners if r["rc_with_its_kind"] == RC_SPLIT),
        "die_on_a_plain_exception": sum(1 for r in runners
                                        if r["a_non_timeout_exception_ends_the_run"]),
        "states_expected_total": sum(1 for r in runners if r["expected_total"] == TOT_EXPECTED),
        "unrun_row_exists": sum(1 for r in runners if r["unrun_representable"] == UN_SYNTHETIC),
        "receipt_written_inside_loop": sum(1 for r in runners
                                           if r["receipt_written_inside_loop"]),
        "usable_triage_fields_total": sum(r["triage_fields_usable"] for r in runners),
        "triage_fields_available": len(TRIAGE_FIELDS) * len(runners),
    }

    # The receipt census is an OBSERVATION, not part of the gate: every run of the chain adds a
    # file to the directory this census counts, so a face that gated these numbers would go red
    # the next time the chain leg itself ran (E180/E207 family: a census inside a live directory
    # must exclude what its own runner writes).  Published beside the gate, re-derived and
    # compared for drift, never compared for equality.
    receipt_census = {
        "files": receipts,
        "count": len(receipts),
        "with_a_nonzero_row": sum(1 for r in receipts if r.get("nonzero_rows")),
        "with_any_output_field": sum(1 for r in receipts
                                     if r.get("carries_stderr")),
        "by_machine": {k: per_total[k] for k in sorted(per_total)},
        "note": "observation over results/_r*bm*_s6_chain.json; grows whenever a chain runs",
    }

    face = {
        "study": "E560",
        "card": "E560",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1586",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population": {"runners": RUNNERS, "receipt_sources": "results/_r*bm*_s6_chain.json"},
        "runners": runners,
        "runner_table": table,
        "receipt_census": receipt_census,
        "summary": summary,
        "control_arms": _control_arms(),
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "producers": {
            "script": "scripts/e560_chain_receipt_shape.py",
            "selftest": "python scripts/e560_chain_receipt_shape.py selftest",
            "card": "knowledge/METHODOLOGY_ASSETS.md E560",
        },
    }
    if write:
        _write(LATEST, face)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
    return face


def _control_arms():
    arms = {}
    f = _facts_from_source(CONTROL_SOURCES["abort_on_failure"])
    arms["abort_on_failure"] = {"found": f["loop_failure_policy"] == P_ABORTS,
                                "value": f["loop_failure_policy"]}
    f = _facts_from_source(CONTROL_SOURCES["stderr_kept"])
    arms["stderr_kept"] = {"found": f["its_own_output"] == OUT_WITH_STDERR,
                           "value": f["its_own_output"]}
    f = _facts_from_source(CONTROL_SOURCES["incremental_write"])
    arms["incremental_receipt"] = {"found": f["receipt_written_inside_loop"],
                                   "value": f["receipt_written_inside_loop"]}
    f = _facts_from_source(CONTROL_SOURCES["states_table_size"])
    arms["states_table_size"] = {"found": f["expected_total"] == TOT_EXPECTED,
                                 "value": f["expected_total"]}
    f = _facts_from_source(CONTROL_SOURCES["collapses_exceptions"])
    arms["collapses_exceptions"] = {"found": f["rc_with_its_kind"] == RC_COLLAPSED,
                                    "value": f["rc_with_its_kind"]}
    f = _facts_from_source(CONTROL_SOURCES["synthetic_unrun_row"])
    arms["synthetic_unrun_row"] = {"found": f["unrun_representable"] == UN_SYNTHETIC,
                                   "value": f["unrun_representable"]}
    return arms


def _verdict(s):
    if s["continues_after_failure"] + s["aborts_after_failure"] != s["runners"]:
        return "unclassified"
    if s["keeps_stderr"] == 0 and s["states_expected_total"] == 0:
        return ("the_receipt_names_every_leg_that_ran_but_no_leg_that_did_not_and_keeps_one_"
                "truncated_stdout_line")
    return "some_receipt_carries_what_a_triager_needs"


def _verdict_line(s):
    return ("%d runners continue past a failing leg (of %d), %d keep stderr, %d distinguish a "
            "timeout from an exit (but %d of those end the run with no receipt at all on any "
            "other exception), %d state the table size and %d can represent a leg that never "
            "ran; %d of %d triage fields survive into the file."
            % (s["continues_after_failure"], s["runners"], s["keeps_stderr"],
               s["rc_kind_distinguished"], s["die_on_a_plain_exception"],
               s["states_expected_total"], s["unrun_row_exists"],
               s["usable_triage_fields_total"], s["triage_fields_available"]))


# ---- persistence / gates -------------------------------------------------------
def _write(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def face_problems(face):
    p = []
    runners = face.get("runners") or []
    if not runners:
        p.append("the runner population is empty")
    for r in runners:
        want = triage_from_facts(r)
        for k, v in want.items():
            if r.get(k) != v:
                p.append("%s: %s is not what the row's own fields say (%r vs %r)"
                         % (r.get("path"), k, r.get(k), v))
        if r.get("legs_in_table", 0) <= 0:
            p.append("%s: the LEGS table could not be read" % r.get("path"))
        if r["loop_failure_policy"] == P_ABORTS and not r["breaks_or_returns_in_loop"]:
            p.append("%s: published as aborting without a break" % r.get("path"))
        if r["its_own_output"] == OUT_WITH_STDERR and not (
                r["stderr_read"] and r["row_names_stderr"]):
            p.append("%s: claims stderr without reading it" % r.get("path"))
    s = face.get("summary") or {}
    if s.get("runners") != len(runners):
        p.append("the runner count is not the length of the row list")
    if s.get("continues_after_failure") != sum(
            1 for r in runners if r["loop_failure_policy"] == P_CONTINUES):
        p.append("the continues-after-failure count is not the number of rows in that class")
    if s.get("keeps_stderr") != sum(1 for r in runners if r["its_own_output"] == OUT_WITH_STDERR):
        p.append("the stderr count is not the number of rows in that class")
    if s.get("usable_triage_fields_total") != sum(r["triage_fields_usable"] for r in runners):
        p.append("the triage field total is not the sum of the row counters")
    rec = face.get("receipt_census") or {}
    files = rec.get("files") or []
    if rec.get("count") != len(files):
        p.append("the receipt census count is not the length of the file list")
    for r in files:
        if r.get("rows") is not None and r["rows"] < 0:
            p.append("a receipt row count is negative (%s)" % r.get("file"))
    for name, arm in (face.get("control_arms") or {}).items():
        if not (arm or {}).get("found"):
            p.append("control arm %s is blind" % name)
    if face.get("verdict") != _verdict(s):
        p.append("the verdict is not what the rows say")
    if not face.get("verdict_line"):
        p.append("the face carries no verdict line")
    return p


def check():
    face = build(write=False)
    if not os.path.isfile(LATEST):
        print("problems: the published face is missing")
        return 2
    with io.open(LATEST, encoding="utf-8") as fh:
        published = json.load(fh)
    problems = []
    for key in ("runners", "runner_table", "summary", "verdict", "verdict_line", "control_arms"):
        if _canon(published.get(key)) != _canon(face.get(key)):
            problems.append("%s does not re-derive from source" % key)
    problems.extend(face_problems(published))
    old_census = (published.get("receipt_census") or {}).get("count")
    new_census = (face.get("receipt_census") or {}).get("count")
    if old_census != new_census:
        # not a defect: the directory this census reads grows every time the chain runs
        print("receipt census drift: %s -> %s files (observation, not gated)" % (old_census,
                                                                               new_census))
    if problems:
        for x in problems:
            print("PROBLEM:", x)
        return 1
    print("problems=[] runners=%d legs=%d receipts=%s verdict=%s"
          % (len(published["runners"]), published["summary"]["legs_total_in_tables"],
             new_census, published.get("verdict")))
    return 0


def verify():
    a = _canon(build(write=False))
    b = _canon(build(write=False))
    if a != b:
        print("VERIFY FAIL: two builds differ")
        return 1
    print("VERIFY PASS: two builds identical (%d bytes)" % len(a))
    return 0


# ---- selftest -----------------------------------------------------------------
def selftest():
    bad = []
    total = 0

    def leg(name, cond):
        nonlocal total
        total += 1
        if not cond:
            bad.append(name)

    arms = _control_arms()
    leg("fixture: a break in the loop reads as abort", arms["abort_on_failure"]["found"])
    leg("fixture: a stderr field reads as output kept", arms["stderr_kept"]["found"])
    leg("fixture: a dump inside the loop reads as incremental", arms["incremental_receipt"]["found"])
    leg("fixture: len(LEGS) in the payload reads as the table size",
        arms["states_table_size"]["found"])
    leg("fixture: except Exception reads as collapsed", arms["collapses_exceptions"]["found"])
    leg("fixture: a MISSING row reads as representable", arms["synthetic_unrun_row"]["found"])

    # the live rows obey the same classifiers
    face = build(write=False)
    leg("live face has no self-detected problems", face_problems(face) == [])
    leg("live face re-derives", _canon(face) == _canon(build(write=False)))
    leg("all control arms are found",
        all(a.get("found") for a in face["control_arms"].values()))
    three = triage_from_facts({"caught_exceptions": ["Exception"], "rc_constants": {},
                               "stderr_read": False, "row_names_stderr": False,
                               "receipt_keys": ["legs"], "row_keys": ["leg", "rc", "tail"],
                               "synthetic_unrun_row": False})
    leg("a collapsing catcher is not credited with a split", three["rc_with_its_kind"] == RC_COLLAPSED)
    leg("a stdout-only row is not credited with output", three["its_own_output"] == OUT_ONE_LINE)
    leg("a receipt counting only rows attempted has no expected total",
        three["expected_total"] == TOT_ATTEMPTED)
    leg("no synthetic row means an unrun leg is invisible", three["unrun_representable"] == UN_NONE)
    leg("exactly one of three triage fields is usable there",
        three["triage_fields_usable"] == 1)
    narrow = triage_from_facts({"caught_exceptions": ["TimeoutExpired"], "rc_constants": {},
                                "stderr_read": False, "row_names_stderr": False,
                                "receipt_keys": [], "row_keys": ["leg", "rc", "tail"],
                                "synthetic_unrun_row": False})
    leg("a narrow timeout handler keeps the rc distinct", narrow["rc_with_its_kind"] == RC_SPLIT)
    leg("and is published as dying on any other exception",
        narrow["a_non_timeout_exception_ends_the_run"])

    # a published face must not be able to lie about one runner
    f2 = json.loads(json.dumps(face))
    if f2["runners"]:
        f2["runners"][0]["its_own_output"] = OUT_WITH_STDERR
        leg("a runner credited with stderr it never reads is refused", bool(face_problems(f2)))
    else:
        leg("a runner credited with stderr it never reads is refused", True)

    f3 = json.loads(json.dumps(face))
    f3["verdict"] = "a_verdict_this_study_never_publishes"
    leg("a hand-written verdict is refused", bool(face_problems(f3)))

    f4 = json.loads(json.dumps(face))
    f4["summary"]["runners"] = f4["summary"]["runners"] + 1
    leg("an inflated runner count is refused", bool(face_problems(f4)))

    f5 = json.loads(json.dumps(face))
    f5["summary"]["usable_triage_fields_total"] = 99
    leg("an inflated triage total is refused", bool(face_problems(f5)))

    f6 = json.loads(json.dumps(face))
    f6["receipt_census"]["files"] = f6["receipt_census"]["files"] + [
        {"file": "x", "rows": -1, "machine": "bm-b"}]
    f6["receipt_census"]["count"] = len(f6["receipt_census"]["files"])
    leg("a negative receipt row count is refused", bool(face_problems(f6)))

    if bad:
        print("SELFTEST FAIL %d/%d" % (total - len(bad), total))
        for x in bad:
            print("  -", x)
        return 1
    print("SELFTEST PASS %d/%d" % (total, total))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        s = face["summary"]
        print("built %s: runners=%d legs=%d continue=%d stderr=%d expected_total=%d "
              "unrun_rows=%d triage=%d/%d receipts=%d verdict=%s"
              % (os.path.basename(LATEST), s["runners"], s["legs_total_in_tables"],
                 s["continues_after_failure"], s["keeps_stderr"],
                 s["states_expected_total"], s["unrun_row_exists"],
                 s["usable_triage_fields_total"], s["triage_fields_available"],
                 face["receipt_census"]["count"], face["verdict"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e560_chain_receipt_shape.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())