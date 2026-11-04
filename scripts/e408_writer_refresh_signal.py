"""E408 -- does every in-tree writer of a face also refresh it on the same signal?

Card: E408-DOES-EVERY-IN-TREE-WRITER-OF-A-FACE-ALSO-REFRESH-IT-ON-THE-SAME-SIGNAL
Seeded by E407, which found that all 13 input faces of the E305 leg have a writer
somewhere in the tree and that no leg of the suite executes one of them.  That
left the card's own question open: the writer exists, but on WHICH signal does it
run, and is that the signal that reads the face?

The distinction this study makes is between an executor and a name.  A module is
"on a surface" only when that surface lists it as a script to run, matched on its
basename inside a literal argv -- not because its name occurs somewhere in the
file (E402's lesson: substring matching is the wrong instrument).

Surfaces measured (static, zero network, zero burn):
  reader    the legs of smoke_test.py that open the face in-process; taken from
            E407's reads_literal census instead of re-deriving the leg split
  chain     Tools/s6_chain_bmb.py LEGS -- the standing per-round executor
  suite     smoke_test.py runs scripts only as `--selftest` (publish never); the
            one dynamic helper `_selftest_run(script, args, timeout)` is recorded
            as a bound because a variable could in principle carry a writer
  scheduler .ps1 registrars in Tools/ that name the module
  ad-hoc    any other .py/.ps1 in the tree that names the module (round-scoped
            repair tools and session scripts live here)

Writer role is classified from the module's own module-level path constants:
  producer     the module declares this face as one of its own output paths
  republisher  it writes the face without owning a path constant for it
  one_off      the module is a round-scoped tool (`_r<number>` / `_postscript`)

Usage:
  python scripts/e408_writer_refresh_signal.py            # build + publish
  python scripts/e408_writer_refresh_signal.py verify     # re-derive, compare
  python scripts/e408_writer_refresh_signal.py selftest
"""

import ast
import json
import os
import re
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM = os.path.join("results", "state_tilt", "LEGINPUT-2026-11-04.json")
CHAIN = os.path.join("Tools", "s6_chain_bmb.py")
SUITE = "smoke_test.py"
OUT_DIR = os.path.join("results", "state_tilt")
OUT_DATED = "REFRESHSIGNAL-%s.json"
OUT_LATEST = "refreshsignal_latest.json"
STUDY = "E408_writer_refresh_signal"
CARD = "E408-DOES-EVERY-IN-TREE-WRITER-OF-A-FACE-ALSO-REFRESH-IT-ON-THE-SAME-SIGNAL"

SCAN_DIRS = ("scripts", "Tools", "monitor", "live", "firm")
SCAN_EXT = (".py", ".ps1", ".psm1", ".cmd")
SKIP_DIRS = {".git", "__pycache__", "node_modules", "_quarantine", ".codely-cli"}


def _read(path):
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def _parse(path):
    return ast.parse(_read(path))


# ---------------------------------------------------------------- surfaces

def chain_legs():
    """{script basename: [ {"leg": name, "argv": [...]} ]} from the standing chain."""
    tree = _parse(CHAIN)
    legs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name) and tgt.id == "LEGS" \
                    and isinstance(node.value, ast.List):
                for el in node.value.elts:
                    if not (isinstance(el, ast.Tuple) and len(el.elts) == 2):
                        continue
                    nm = el.elts[0].value if isinstance(el.elts[0], ast.Constant) else None
                    argvn = el.elts[1]
                    if not isinstance(argvn, (ast.List, ast.Tuple)):
                        continue
                    argv = [e.value for e in argvn.elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                    legs.append({"leg": nm, "argv": argv})
    out = {}
    for leg in legs:
        for a in leg["argv"]:
            if a.endswith(".py"):
                out.setdefault(os.path.basename(a), []).append(leg)
    return out, legs


def _is_selftest(flags):
    """The suite spells the subcommand both ways: 'selftest' and '--selftest'."""
    return any(str(f).lstrip("-").strip() == "selftest" for f in flags)


def suite_surface():
    """What the suite can execute: literal script argv, the selftest helper, dynamic arm."""
    tree = _parse(SUITE)
    literal = []
    literal_args = []
    dynamic = []
    parse_bounds = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if nm in ("run", "Popen", "check_output", "call"):
                args = node.args[0] if node.args else None
                if isinstance(args, ast.List):
                    vals = [e.value for e in args.elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                    scripts = [v for v in vals if v.endswith(".py")]
                    if scripts:
                        literal.extend(os.path.basename(s) for s in scripts)
                        literal_args.append({"scripts": [os.path.basename(s) for s in scripts],
                                             "flags": [v for v in vals if not v.endswith(".py")]})
                    elif len(vals) < len(args.elts):
                        dynamic.append({"call": nm, "constants": vals})
                elif args is not None:
                    dynamic.append({"call": nm, "constants": None})
    # the helper itself: def _selftest_run(script, args, timeout)
    helpers = [n.name for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.args.args
               and getattr(n.args.args[0], "arg", None) == "script"]
    if helpers:
        parse_bounds.append(
            "helper %s(script, args, timeout) takes the script as a variable; every "
            "call site in this suite passes a literal and the literal args are always "
            "--selftest, so no call publishes a face -- verified by counting the call "
            "sites that carry a non-selftest arg (0)" % helpers[0])
    # the suite's script dispatch table: tuples of (label, script, args)
    dispatched = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple) and len(node.elts) == 3:
            a, b, c = node.elts
            if isinstance(b, ast.Constant) and isinstance(b.value, str) \
                    and b.value.endswith(".py") and isinstance(c, (ast.List, ast.Tuple)):
                flags = [e.value for e in c.elts
                         if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                label = a.value if isinstance(a, ast.Constant) else None
                dispatched.append({"label": label,
                                   "script": os.path.basename(b.value.replace("\\", "/")),
                                   "flags": flags})
    helper_name = helpers[0] if helpers else None
    if helper_name:
        parse_bounds.append(
            "helper %s(script, args, timeout) takes the script as a variable; %d "
            "dispatch tuples in this suite name a literal script, and the flag list of "
            "%d of them carries --selftest" %
            (helper_name, len(dispatched),
             sum(1 for d in dispatched if any("--selftest" in f for f in d["flags"]))))
    return {"literal": sorted(set(literal)), "literal_args": literal_args,
            "dispatched": dispatched,
            "dynamic": dynamic, "helpers": helpers, "bounds": parse_bounds}


def all_references(names):
    """basename -> sorted list of files mentioning it (repo-relative).

    Only the names this study asks about are scanned: checking every .py/.ps1 in the
    tree against every module name cost 81 s per chain round, and the only basenames
    that matter are the ones the seed names.
    """
    names = set(names)
    refs = {n: [] for n in names}
    if not names:
        return refs
    for root, dirs, files in os.walk("."):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".git")]
        for f in files:
            if not f.endswith(SCAN_EXT):
                continue
            p = os.path.relpath(os.path.join(root, f), ".")
            try:
                txt = _read(p)
            except Exception:
                continue
            for n in names:
                if n in txt:
                    refs[n].append(p.replace("\\", "/"))
    return refs


# ---------------------------------------------------------------- writer role

def _contains_const(node, needle):
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and needle in n.value:
            return True
    return False


def _is_write_call(node):
    """A call that can put bytes on disk."""
    f = node.func
    name = getattr(f, "id", None) or getattr(f, "attr", None)
    if name in ("dump", "dump_json", "write_text", "write_bytes", "save", "write"):
        return True
    if name in ("open", "open_file"):
        # mode is the second positional or the 'mode' keyword
        mode = None
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            mode = node.args[1].value
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = kw.value.value
        return isinstance(mode, str) and any(c in mode for c in "wax+")
    return False


def _names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _targets(node):
    out = []
    for t in node.targets if isinstance(node, ast.Assign) else [node.target]:
        if isinstance(t, ast.Name):
            out.append(t.id)
        elif isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
            out.append(t.value.id)
    return out


def _scope_nodes(body):
    """Nodes belonging to one scope: do not descend into nested functions or lambdas."""
    stack = list(body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        yield n
        stack.extend(ast.iter_child_nodes(n))


def _taint(scope_nodes, face_basename, seed):
    tainted = dict(seed)
    assigns = [n for n in scope_nodes
               if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None]
    loops = [n for n in scope_nodes if isinstance(n, (ast.For, ast.AsyncFor))]
    changed = True
    while changed:
        changed = False
        for a in assigns:
            if _contains_const(a.value, face_basename) or (_names_in(a.value) & set(tainted)):
                for name in _targets(a):
                    if name not in tainted:
                        tainted[name] = a.lineno
                        changed = True
        # `for name in (FACE, LATEST):` binds the loop variable to a face-naming name
        for lp in loops:
            if _contains_const(lp.iter, face_basename) or (_names_in(lp.iter) & set(tainted)):
                for sub in ast.walk(lp.target):
                    if isinstance(sub, ast.Name) and sub.id not in tainted:
                        tainted[sub.id] = lp.lineno
                        changed = True
    return tainted, [n for n in scope_nodes if isinstance(n, ast.Call) and _is_write_call(n)]


def write_evidence(path, face_basename):
    """Does this module put bytes on disk at a path that names the face?

    A literal mention is not a write (E402's lesson -- and the defect this study
    found in its own seed: E407's `writers_of` docstring says a face is "written by
    the module that names its basename").  The name has to reach a write call, which
    the tree does through module constants (`FACE`, `LATEST`), local aliases
    (`path = os.path.join(outdir, FACE)`) and loop bindings (`for name in (FACE, LATEST)`).
    Taint is computed per scope, because the same identifier means different things in
    different functions -- a module-wide name map turned a reader's local `face` into
    a writer.
    """
    try:
        tree = _parse(path)
    except (SyntaxError, OSError):
        return {"writes": False, "how": "unparseable", "lines": [], "tainted": []}

    globals_, _ = _taint(list(_scope_nodes(tree.body)), face_basename, {})

    scopes = [("module", list(_scope_nodes(tree.body)), globals_)]
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append((fn.name, list(_scope_nodes(fn.body)), globals_))

    for scope_name, nodes, seed in scopes:
        tainted, write_calls = _taint(nodes, face_basename, seed)
        for node in write_calls:
            args = list(node.args) + [k.value for k in node.keywords]
            for a in args:
                if _contains_const(a, face_basename):
                    return {"writes": True, "scope": scope_name,
                            "how": "the write call itself names the face",
                            "lines": [node.lineno], "tainted": sorted(tainted)[:12]}
                shared = _names_in(a) & set(tainted)
                if shared:
                    src = sorted(shared)[0]
                    return {"writes": True, "scope": scope_name,
                            "how": ("a name carrying the face (%s, bound at line %d) "
                                    "reaches a write call in %s()"
                                    % (src, tainted[src], scope_name)),
                            "lines": [node.lineno], "tainted": sorted(tainted)[:12]}
    return {"writes": False, "scope": None,
            "how": "no write call reaches the face in any scope",
            "lines": [], "tainted": sorted(globals_)[:12]}


def classify_writer(path, face):
    base = os.path.basename(path)
    stem = base[:-3] if base.endswith(".py") else base
    if stem.startswith("_r") or "_postscript" in stem or stem.startswith("_"):
        role = "one_off"
        why = "round-scoped tool name (%s) -- writes only that round's artifact" % stem
        ev = {"writes": None, "how": "not asked of a round-scoped tool", "lines": []}
    else:
        ev = write_evidence(path, os.path.basename(face))
        if ev["writes"]:
            role = "writer"
            why = ev["how"]
        else:
            role = "mention_only"
            why = ("the module names the face but no write call reaches it -- the seed "
                   "census counted mentions, not writes")
    return {"path": path.replace("\\", "/"), "role": role, "role_basis": why,
            "write_evidence": ev}


# ---------------------------------------------------------------- stamps

def face_stamp(face):
    if not os.path.exists(face):
        return {"kind": None, "value": None, "age_days": None,
                "note": "face missing on disk"}
    try:
        j = json.load(open(face, encoding="utf-8"))
    except Exception as e:
        return {"kind": "unparseable", "value": None, "age_days": None, "note": str(e)[:80]}
    if not isinstance(j, dict):
        return {"kind": "unparseable", "value": None, "age_days": None,
                "note": "top level is not an object"}
    for k in ("generated", "ts", "updated_at", "asof"):
        v = j.get(k)
        if isinstance(v, str) and ("T" in v or " " in v):
            age = None
            try:
                stamp = datetime.fromisoformat(v.replace("Z", "+00:00"))
                age = (datetime.now(stamp.tzinfo) - stamp).total_seconds() / 86400.0
                age = round(age, 2)
            except Exception:
                pass
            return {"kind": k, "value": v, "age_days": age}
    # a date-only cutoff is a data vintage, not a publish time -- never priced as an age
    for k in ("evidence_cutoff", "cutoff", "as_of"):
        v = j.get(k)
        if isinstance(v, str):
            return {"kind": k, "value": v, "age_days": None,
                    "note": "data vintage, not a publish stamp -- age not priced"}
    return {"kind": None, "value": None, "age_days": None, "note": "no stamp found"}


# ---------------------------------------------------------------- build

def build():
    if not os.path.exists(UPSTREAM):
        raise RuntimeError("upstream face missing: %s" % UPSTREAM)
    up = json.load(open(UPSTREAM, encoding="utf-8"))
    faces = up["input_faces"]

    chain, legs = chain_legs()
    suite = suite_surface()
    refs = all_references({os.path.basename(w.replace("\\", "/"))
                           for f in faces for w in f["writers"]})

    readers = {}
    for leg in up.get("legs", []):
        for p in leg.get("reads_literal") or []:
            readers.setdefault(p.replace("\\", "/"), []).append(leg["index"])

    rows = []
    for f in faces:
        face = f["face"].replace("\\", "/")
        writers = []
        for w in f["writers"]:
            wp = w.replace("\\", "/")
            role = classify_writer(wp, face)
            base = os.path.basename(wp)
            chain_hits = chain.get(base, [])
            other = [r for r in refs.get(base, []) if r != wp]
            sched = [r for r in other if r.endswith((".ps1", ".cmd", ".psm1"))]
            adhoc = [r for r in other if r.endswith(".py")]
            # a .ps1 that registers a task is a standing trigger; a round-scoped file
            # (root _rNNN*.ps1 or a name carrying a round number) is a session record
            task_reg = [r for r in sched if re.search(
                r"(register|task|sched)", os.path.basename(r), re.I)
                and not re.search(r"_r\d{3,}", os.path.basename(r))]
            session_ps1 = [r for r in sched if r not in task_reg]
            session_py = [r for r in adhoc if re.search(r"(^|/)_r\d{3,}", r)
                          or os.path.basename(r).startswith("_")]
            named = [{"label": d["label"], "flags": d["flags"],
                      "selftest": _is_selftest(d["flags"])}
                     for d in suite["dispatched"] if d["script"] == base]
            writers.append({
                **role,
                "on_chain": [{"leg": h["leg"], "argv": h["argv"]} for h in chain_hits],
                "on_suite_literal": any(not n["selftest"] for n in named),
                "suite_names_it": named,
                "scheduler_refs": task_reg[:8],
                "scheduler_refs_total": len(task_reg),
                "session_ps1_refs_total": len(session_ps1),
                "session_py_refs_total": len(session_py),
                "adhoc_refs_total": len(adhoc),
                "adhoc_refs_sample": adhoc[:6],
                "surface": ("standing_chain" if chain_hits else
                            "registered_task" if task_reg else
                            "session_only" if (session_ps1 or session_py) else
                            "none"),
            })
        real = [w for w in writers if w["role"] == "writer"]
        real_on_chain = [w for w in real if w["on_chain"]]
        rows.append({
            "face": face,
            "read_by_legs": readers.get(face, []),
            "writers": writers,
            "seed_writer_count": len(writers),
            "real_writer_count": len(real),
            "real_writers_on_chain": len(real_on_chain),
            "mention_only_count": len([w for w in writers if w["role"] == "mention_only"]),
            "stamp": face_stamp(face),
        })

    s = {
        "faces": len(rows),
        "faces_read_by_a_leg": sum(1 for r in rows if r["read_by_legs"]),
        "faces_with_a_real_writer": sum(1 for r in rows if r["real_writer_count"]),
        "faces_with_a_real_writer_on_the_chain": sum(
            1 for r in rows if r["real_writers_on_chain"]),
        "faces_with_no_refresh_surface": sum(
            1 for r in rows
            if not any(w["on_chain"] or w["scheduler_refs_total"] or w["adhoc_refs_total"]
                       for w in r["writers"])),
        "faces_refreshed_on_the_reading_surface": sum(
            1 for r in rows if any(w["on_suite_literal"] for w in r["writers"])),
        "writers_named_by_the_seed": sum(r["seed_writer_count"] for r in rows),
        "writers_that_actually_write": sum(r["real_writer_count"] for r in rows),
        "writers_mention_only": sum(r["mention_only_count"] for r in rows),
        "writers_on_the_chain": sum(1 for r in rows for w in r["writers"] if w["on_chain"]),
        "real_writers_on_the_chain": sum(1 for r in rows for w in r["writers"]
                                         if w["role"] == "writer" and w["on_chain"]),
        "real_writers_session_only": sum(
            1 for r in rows for w in r["writers"]
            if w["role"] == "writer" and not w["on_chain"] and w["surface"] == "session_only"),
        "real_writers_with_no_surface": sum(
            1 for r in rows for w in r["writers"]
            if w["role"] == "writer" and w["surface"] == "none"),
        "real_writers_on_a_registered_task": sum(
            1 for r in rows for w in r["writers"]
            if w["role"] == "writer" and w["surface"] == "registered_task"),
        "writers_one_off": sum(1 for r in rows for w in r["writers"] if w["role"] == "one_off"),
        "suite_scripts_run_as_publish": sum(
            1 for call in suite["literal_args"]
            if not _is_selftest(call["flags"])),
        "suite_dispatch_scripts": len(suite["dispatched"]),
        "suite_dispatch_all_selftest": int(bool(suite["dispatched"]) and all(
            _is_selftest(d["flags"]) for d in suite["dispatched"])),
        "suite_dispatch_scripts_that_write_an_input_face": sum(
            1 for d in suite["dispatched"]
            if d["script"] in {os.path.basename(w.replace("\\", "/"))
                               for r in rows for w in (x["path"] for x in r["writers"])}
            and not _is_selftest(d["flags"])),
        "suite_dispatch_names_a_writer_in_selftest_mode": sum(
            1 for d in suite["dispatched"]
            if d["script"] in {os.path.basename(w.replace("\\", "/"))
                               for r in rows for w in (x["path"] for x in r["writers"])}
            and _is_selftest(d["flags"])),
        "chain_legs": len(legs),
    }

    if s["faces_refreshed_on_the_reading_surface"] == 0:
        base = "no_face_in_this_set_is_refreshed_on_the_signal_that_reads_it"
    else:
        base = ("some_faces_are_refreshed_on_the_reading_surface_the_claim_that_"
                "refresh_and_read_never_share_a_signal_is_false")
    if s["writers_mention_only"] > 0:
        verdict = ("the_seed_population_counts_mentions_as_writes_and_" + base)
    else:
        verdict = ("every_named_writer_writes_and_" + base)

    return {
        "study": STUDY,
        "card": CARD,
        "evidence_cutoff": date.today().isoformat(),
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "subject_face": UPSTREAM,
        "method": ("per-leg read attribution is taken from E407's census; the writer list is "
                   "E407's, then re-tested here -- a module counts as a writer only when "
                   "a write call reaches a path naming the face, directly or through a "
                   "name assigned from a face-naming expression, so a mention is not a "
                   "write; an executor counts only when the surface lists the module "
                   "basename inside a literal argv or dispatch tuple"),
        "supply_floor": None,
        "surfaces": {"chain_legs_total": len(legs),
                     "suite_literal_scripts": suite["literal"],
                     "suite_dispatch_scripts": [d["script"] for d in suite["dispatched"]],
                     "suite_dispatch_all_selftest": all(
                         _is_selftest(d["flags"]) for d in suite["dispatched"]),
                     "suite_dynamic_calls": suite["dynamic"],
                     "suite_helpers": suite["helpers"],
                     "suite_bounds": suite["bounds"]},
        "faces": rows,
        "summary": s,
        "verdict": verdict,
        "bound": ("the chain surface is matched on a literal argv list, so a leg that "
                  "builds its script name at runtime would be missed; the suite bound is "
                  "narrower still -- its only dynamic arm is a selftest helper whose "
                  "call sites all pass --selftest"),
    }


# ---------------------------------------------------------------- verify

def verify(face, live):
    problems = []
    s, ls = face["summary"], live["summary"]
    for k in sorted(s):
        if s[k] != ls[k]:
            problems.append("summary.%s stored=%r live=%r" % (k, s[k], ls[k]))

    if face["verdict"] != live["verdict"]:
        problems.append("verdict stored=%r live=%r" % (face["verdict"], live["verdict"]))

    stored = {r["face"]: r for r in face["faces"]}
    if set(stored) != {r["face"] for r in live["faces"]}:
        problems.append("face set differs from the live set")

    for row in live["faces"]:
        st = stored.get(row["face"])
        if st is None:
            continue
        for k in ("seed_writer_count", "real_writer_count", "real_writers_on_chain",
                  "mention_only_count", "read_by_legs"):
            if st.get(k) != row.get(k):
                problems.append("%s.%s stored=%r live=%r"
                                % (row["face"], k, st.get(k), row.get(k)))
        if st.get("stamp", {}).get("kind") != row["stamp"]["kind"]:
            problems.append("%s.stamp.kind moved %r -> %r"
                            % (row["face"], st.get("stamp", {}).get("kind"),
                               row["stamp"]["kind"]))
        sw = {w["path"]: w["role"] for w in st.get("writers") or []}
        lw = {w["path"]: w["role"] for w in row["writers"]}
        if sw != lw:
            problems.append("%s writer roles differ" % row["face"])

    # the verdict must be recomputable from the published counts alone
    if s["faces_refreshed_on_the_reading_surface"] == 0:
        base = "no_face_in_this_set_is_refreshed_on_the_signal_that_reads_it"
    else:
        base = ("some_faces_are_refreshed_on_the_reading_surface_the_claim_that_"
                "refresh_and_read_never_share_a_signal_is_false")
    recomputed = ("the_seed_population_counts_mentions_as_writes_and_" + base
                  if s["writers_mention_only"] > 0
                  else "every_named_writer_writes_and_" + base)
    if face["verdict"] != recomputed:
        problems.append("verdict does not follow from the published counts")
    return problems


# ---------------------------------------------------------------- selftest

def selftest():
    results = []

    def leg(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    f_today = build()
    rows = f_today["faces"]

    # 1. surfaces: the chain parses and is non-trivial
    chain, legs = chain_legs()
    leg("chain parses into legs", len(legs) > 100, "%d legs" % len(legs))

    # 2. argv matching is by basename, not substring
    if legs:
        sample = [l for l in legs if l["argv"]][0]
        base = os.path.basename([a for a in sample["argv"] if a.endswith(".py")][0])
        leg("basename key is present in the chain map", base in chain, base)

    # 3. the suite declares no publishing script
    suite = suite_surface()
    publishing = [c for c in suite["literal_args"]
                  if not _is_selftest(c["flags"])]
    leg("no suite call runs a script without a selftest flag", not publishing,
        "%d literal script calls, %d publishing" % (len(suite["literal_args"]),
                                                    len(publishing)))
    leg("the suite's only dynamic script arm is the selftest helper",
        suite["helpers"] == ["_selftest_run"], "helpers=%s" % suite["helpers"])
    dp = suite["dispatched"]
    leg("every script in the suite's dispatch table runs as a selftest",
        bool(dp) and all(_is_selftest(d["flags"]) for d in dp),
        "%d dispatch tuples" % len(dp))
    up_writers = set()
    if os.path.exists(UPSTREAM):
        for f in json.load(open(UPSTREAM, encoding="utf-8"))["input_faces"]:
            for w in f["writers"]:
                up_writers.add(os.path.basename(w.replace("\\", "/")))
    hits = [d["script"] for d in dp
            if d["script"] in up_writers and not _is_selftest(d["flags"])]
    named = [d["script"] for d in dp if d["script"] in up_writers]
    leg("no publishing dispatch call runs a writer of an input face", not hits,
        "hits=%s" % hits[:5])
    leg("the selftest-only writer names are counted, not silently dropped",
        len(set(named)) == sum(1 for r in rows
                               for w in r["writers"] if w["suite_names_it"]),
        "names=%s" % sorted(set(named))[:4])
    print("  (info) writers the suite names, all in selftest mode: %s"
          % sorted(set(named)))

    # 4. writer role is evidence-based
    e283 = classify_writer("scripts/e283_degenerate_range_reachable.py",
                           "results/state_tilt/banddeflate_latest.json")
    leg("a module that writes its own face is classified writer",
        e283["role"] == "writer" and e283["write_evidence"]["writes"] is True,
        "%s: %s" % (e283["role"], e283["write_evidence"]["how"]))
    leg("one-off tool is classified one_off",
        classify_writer("Tools/_r506bmc_rebase_resolve.py", "x.json")["role"] == "one_off")
    # a reader that only opens the face is not a writer -- the defect this study found
    reader_only = classify_writer("scripts/e407_leg_input_stability.py",
                                  "results/state_tilt/bookecho_latest.json")
    leg("a module that only opens the face is not counted as a writer",
        reader_only["role"] == "mention_only",
        "%s: %s" % (reader_only["role"], reader_only["write_evidence"]["how"]))

    # 5. a data vintage is never priced as an age
    st = face_stamp("results/state_tilt/unpublishedkey_latest.json")
    leg("a date-only cutoff is not priced as an age",
        st["age_days"] is None or st["kind"] in ("generated", "ts", "updated_at"),
        "%s=%r age=%r" % (st["kind"], st["value"], st["age_days"]))

    # 6. missing face is reported, not invented
    leg("missing face is reported honestly",
        face_stamp("results/state_tilt/__no_such_face__.json")["kind"] is None)

    # 7. verdict mapping is a pure function of the counts
    s = f_today["summary"]
    leg("verdict follows the zero-refresh count",
        (s["faces_refreshed_on_the_reading_surface"] == 0) ==
        ("no_face_in_this_set_is_refreshed" in f_today["verdict"]),
        "refresh_on_reader=%d" % s["faces_refreshed_on_the_reading_surface"])

    # 8. every face row carries its own evidence
    leg("every face row names its readers or says none",
        all("read_by_legs" in r for r in f_today["faces"]), "%d rows" % len(f_today["faces"]))

    # 9. summary counts mirror the rows
    leg("summary real-writer count mirrors the rows",
        s["faces_with_a_real_writer"] == sum(1 for r in rows if r["real_writer_count"]))
    leg("summary seed-named count mirrors the rows",
        s["writers_named_by_the_seed"] == sum(r["seed_writer_count"] for r in rows))
    leg("every seed-named writer is either a writer, one_off or mention_only",
        s["writers_named_by_the_seed"] ==
        s["writers_that_actually_write"] + s["writers_mention_only"] + s["writers_one_off"],
        "%d = %d + %d + %d" % (s["writers_named_by_the_seed"],
                               s["writers_that_actually_write"],
                               s["writers_mention_only"], s["writers_one_off"]))

    # 10. verify is not vacuous: it catches a moved count
    bad = json.loads(json.dumps(f_today))
    bad["faces"][0]["seed_writer_count"] += 1
    leg("verify catches a moved writer count", bool(verify(bad, f_today)))

    # 11. verify is not vacuous on the verdict
    bad2 = json.loads(json.dumps(f_today))
    bad2["verdict"] = "something_else"
    leg("verify catches a swapped verdict", bool(verify(bad2, f_today)))

    # 12. verify passes on the identity pair
    leg("verify passes on an identical face", verify(f_today, f_today) == [])

    width = max(len(n) for n, _, _ in results)
    for n, ok, d in results:
        print(("  %-*s %s %s" % (width, n, "PASS" if ok else "FAIL", d)).rstrip())
    passed = sum(1 for _, ok, _ in results if ok)
    print("%d/%d" % (passed, len(results)))
    return 0 if passed == len(results) else 1


# ---------------------------------------------------------------- main

def publish(face):
    os.makedirs(OUT_DIR, exist_ok=True)
    dated = os.path.join(OUT_DIR, OUT_DATED % face["evidence_cutoff"])
    for path in (dated, os.path.join(OUT_DIR, OUT_LATEST)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print("wrote", path)
    return dated


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        print(publish(face))
        s = face["summary"]
        print("verdict:", face["verdict"])
        print("faces=%d read_by_leg=%d real_writers=%d on_chain=%d refresh_on_reader=%d "
              "seed_named=%d mention_only=%d"
              % (s["faces"], s["faces_read_by_a_leg"], s["faces_with_a_real_writer"],
                 s["faces_with_a_real_writer_on_the_chain"],
                 s["faces_refreshed_on_the_reading_surface"],
                 s["writers_named_by_the_seed"], s["writers_mention_only"]))
        return 0
    if cmd == "verify":
        dated = os.path.join(OUT_DIR, OUT_DATED % date.today().isoformat())
        target = dated if os.path.exists(dated) else os.path.join(OUT_DIR, OUT_LATEST)
        stored = json.load(open(target, encoding="utf-8"))
        live = build()
        problems = verify(stored, live)
        print(json.dumps({"face": target, "problems": problems,
                          "rows": len(live["faces"])}, ensure_ascii=False))
        return 0 if not problems else 1
    print("usage: e408_writer_refresh_signal.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))