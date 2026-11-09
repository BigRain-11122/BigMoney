"""E619 -- does "assigned from a face key and never read again" generalise past one module?

E617 (r1638) closed over the live sweep's census and found one reader line that reads nothing:
``derive_verdict`` assigns ``census = m["basename_census"]`` and never loads ``census`` again.
One dead line is an anecdote.  This study asks whether the class exists in the producers that
publish the ``results/state_tilt`` faces at all.

Population, fixed before the scan (not derived from the readings):

  * a *face publisher* = a module under ``scripts/`` that both dumps JSON and opens a file for
    writing (``json.dump`` plus a ``"w"`` mode) or calls ``write_face(...)``;
  * a *face-field name* of that module = any string constant used as a key of a dict literal
    somewhere in the module (the shape a published face is built in);
  * a *reader local* = a single-name ``Assign`` whose value is a subscript with a string
    constant (``x = m["k"]``) or a ``.get("k")`` call on a name/subscript.

A reader local is *dead* when no ``Name`` load of that name occurs in its own function after
the assignment line.  Three scopes are published, narrowest last:

  scope_all        every dead reader local, whatever the key
  scope_facekey    only those whose key is a face-field name of the module (the direct test)
  scope_incoming   only those whose indexed object is a function parameter or a local bound
                   from a call -- i.e. a dict the function *received*, not one it built

The verdict is stated on ``scope_facekey``; the other two are published beside it so the
reading can be checked against a wider and a stricter population.

Deterministic, static, no network, no runner, no fixture write.  ``selftest`` proves the
classifier on a synthetic module and on the real population.
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
TODAY = "2026-11-09"
FACE = "DEADREADERLOCALS-%s.json" % TODAY
LATEST = "deadreaderlocals_latest.json"
STUDY = "E619_dead_reader_locals"
POPDIR = "scripts"
SELF_PARTS = {"e619_dead_reader_locals.py", "run_e619_smoke_leg.py", "_probe_e619.py"}
SCOPES = ["scope_all", "scope_facekey", "scope_incoming"]


# ---------------------------------------------------------------- AST helpers
def sub_key(node):
    """The string key a value expression reads, or None.

    ``m["k"]`` -> "k"; ``m.get("k")`` -> "k"; ``d["a"]["b"]`` -> "b".
    """
    if isinstance(node, ast.Subscript):
        sl = node.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            return sl.value
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "get" and node.args:
        a0 = node.args[0]
        if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
            return a0.value
    return None


def indexed_object(node):
    """The object a value expression indexes (``m`` in ``m["k"]`` / ``m.get("k")``)."""
    if isinstance(node, ast.Subscript):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.value
    return None


def dict_key_names(tree):
    """Every string constant used as a key of a dict literal in the module."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    names.add(k.value)
    return names


def functions(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def load_lines(fn):
    """Line numbers of every ``Name`` load inside the function, nested scopes included."""
    return [(n.id, n.lineno) for n in ast.walk(fn)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]


def dead_reader_locals(tree):
    """Reader locals whose bound name is never loaded again in their own function."""
    face_keys = dict_key_names(tree)
    rows = []
    for fn in functions(tree):
        loads = load_lines(fn)
        params = {a.arg for a in list(fn.args.args) + list(fn.args.kwonlyargs)}
        from_call = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call):
                from_call.add(node.targets[0].id)
        for node in ast.walk(fn):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            if not isinstance(node.targets[0], ast.Name):
                continue
            key = sub_key(node.value)
            if key is None:
                continue
            name = node.targets[0].id
            later = [ln for (nm, ln) in loads if nm == name and ln > node.lineno]
            if later:
                continue
            obj = indexed_object(node.value)
            incoming = isinstance(obj, ast.Name) and (obj.id in params or obj.id in from_call)
            rows.append({
                "function": fn.name,
                "local": name,
                "key": key,
                "line": node.lineno,
                "key_is_a_dict_literal_key": key in face_keys,
                "indexed_object_is_incoming": bool(incoming),
            })
    rows.sort(key=lambda r: (r["function"], r["line"]))
    return rows


def publish_signal(tree):
    """Whether this module dumps JSON and opens a file for writing (a face publisher)."""
    dumps = False
    writes = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            attr = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if attr in ("dump", "dumps"):
                dumps = True
            if attr == "write_face":
                writes = True
            if attr in ("open",) and len(node.args) >= 2:
                mode = node.args[1]
                if isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
                        and ("w" in mode.value or "a" in mode.value):
                    writes = True
    return dumps and writes


def population(root):
    """Parse every module under scripts/ and keep the face publishers."""
    out = []
    skipped = []
    pdir = os.path.join(root, POPDIR)
    for name in sorted(os.listdir(pdir)):
        if not name.endswith(".py") or name in SELF_PARTS:
            continue
        path = os.path.join(pdir, name)
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
            tree = ast.parse(src)
        except (SyntaxError, ValueError, OSError) as exc:
            skipped.append({"module": "%s/%s" % (POPDIR, name), "why": type(exc).__name__})
            continue
        if not publish_signal(tree):
            continue
        out.append(("%s/%s" % (POPDIR, name), tree))
    return out, skipped


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    mods, skipped = population(root)
    per_module = []
    for rel, tree in mods:
        dead = dead_reader_locals(tree)
        facekey = [r for r in dead if r["key_is_a_dict_literal_key"]]
        incoming = [r for r in facekey if r["indexed_object_is_incoming"]]
        per_module.append({
            "module": rel,
            "dict_keys": len(dict_key_names(tree)),
            "dead_reader_locals": dead,
            "scope_all": len(dead),
            "scope_facekey": len(facekey),
            "scope_incoming": len(incoming),
        })
    return {"modules": per_module, "skipped": skipped,
            "population": len(per_module)}


def counts_of(m):
    c = {
        "population_modules": m["population"],
        "skipped_modules": len(m["skipped"]),
        "modules_with_a_dead_local_scope_all": sum(1 for r in m["modules"] if r["scope_all"]),
        "modules_with_a_dead_local_scope_facekey": sum(
            1 for r in m["modules"] if r["scope_facekey"]),
        "modules_with_a_dead_local_scope_incoming": sum(
            1 for r in m["modules"] if r["scope_incoming"]),
    }
    for s in SCOPES:
        c[s + "_lines"] = sum(r[s] for r in m["modules"])
    c["dead_locals_total"] = c["scope_all_lines"]
    c["modules_with_no_dead_local"] = sum(1 for r in m["modules"] if not r["scope_all"])
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["modules_with_a_dead_local_scope_facekey"] == 0:
        return "no_face_publisher_carries_an_assigned_and_never_read_face_key_local"
    return ("%d_of_%d_face_publishers_carry_a_local_assigned_from_a_face_key_and_never_read"
            % (c["modules_with_a_dead_local_scope_facekey"], c["population_modules"]))


def answer_of(m):
    c = counts_of(m)
    worst = sorted(m["modules"], key=lambda r: -r["scope_facekey"])[:3]
    named = ", ".join("%s (%d)" % (r["module"], r["scope_facekey"]) for r in worst
                      if r["scope_facekey"])
    return ("of %d modules under scripts/ that publish a JSON face, %d carry at least one local "
            "assigned from a face key and never read again (%d such lines); the same population "
            "holds %d dead reader lines whatever the key and %d whose dict was handed to the "
            "function. Worst present-day holders: %s"
            % (c["population_modules"], c["modules_with_a_dead_local_scope_facekey"],
               c["scope_facekey_lines"], c["scope_all_lines"], c["scope_incoming_lines"],
               named or "none"))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    mods = face.get("modules") or []
    if counts.get("population_modules") != len(mods):
        p.append("counts.population_modules says %r but the face publishes %d modules"
                 % (counts.get("population_modules"), len(mods)))
    for s in SCOPES:
        n = sum(r.get(s, 0) for r in mods)
        if counts.get(s + "_lines") != n:
            p.append("counts.%s_lines does not re-derive from the module rows" % s)
        held = sum(1 for r in mods if r.get(s))
        if counts.get("modules_with_a_dead_local_" + s) != held:
            p.append("counts.modules_with_a_dead_local_%s does not re-derive (%r vs %r)"
                     % (s, counts.get("modules_with_a_dead_local_" + s), held))
    for r in mods:
        for k in ("scope_all", "scope_facekey", "scope_incoming"):
            listed = len(r.get("dead_reader_locals") or [])
            if k == "scope_all" and r.get(k) != listed:
                p.append("module %r publishes scope_all=%r with %d dead rows"
                         % (r.get("module"), r.get(k), listed))
        fk = [x for x in (r.get("dead_reader_locals") or []) if x.get("key_is_a_dict_literal_key")]
        if r.get("scope_facekey") != len(fk):
            p.append("module %r scope_facekey does not re-derive from its rows" % r.get("module"))
        fki = [x for x in fk if x.get("indexed_object_is_incoming")]
        if r.get("scope_incoming") != len(fki):
            p.append("module %r scope_incoming does not re-derive from its rows" % r.get("module"))
    derived = derive_verdict({"population": counts.get("population_modules"),
                              "modules": mods, "skipped": [None] * (
                                  counts.get("skipped_modules") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def build(root=ROOT):
    m = measure(root=root)
    face = {
        "study": STUDY,
        "script": "scripts/e619_dead_reader_locals.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("parse every module under scripts/ that dumps JSON and opens a file for "
                   "writing; a reader local is a single-name Assign from a string subscript or a "
                   ".get(\"k\") call; it is dead when no Name load of that local occurs in its "
                   "own function after the assignment line"),
        "population_source": POPDIR + "/*.py (AST), face publishers only",
        "counts": counts_of(m),
        "modules": m["modules"],
        "skipped": m["skipped"],
        "limits": [
            "the names a dead local is compared against are the module's dict-literal keys; a "
            "face key read from a config file or built from a format string is outside that set",
            "a load anywhere in the function counts as a reader, including inside a nested "
            "function: a closure use would otherwise be published as a dead line",
            "only single-name assignments are examined; tuple unpacking "
            "(a, b = m[\"x\"], m[\"y\"]) and augmented writes are not reader locals",
            "the subscript key has to be a literal string; a local key variable is not resolved",
            "this script excludes itself and its smoke leg from the population",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import io, json, os


def build(m, out="x"):
    face = {"counts": {"n": 1}, "rows": []}
    doc = {"study": "X"}
    reader = m["counts"]
    used = m["counts"]
    keeper = m.get("rows")
    if keeper:
        face["rows"] = keeper
    face["used"] = used
    path = os.path.join(out, "face.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    return face


def helper(d):
    tmp = d["nope"]
    return d["counts"]
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    keys = dict_key_names(tree)
    legs.append(("fixture dict keys are found",
                 {"counts", "rows", "n", "study"} <= keys))
    dead = dead_reader_locals(tree)
    by_local = {(d["function"], d["local"]): d for d in dead}
    legs.append(("an assigned-and-never-loaded local in build is caught",
                 ("build", "reader") in by_local))
    legs.append(("a local that is loaded later is not caught", ("build", "used") not in by_local))
    legs.append(("a .get() local that is tested is not caught", ("build", "keeper") not in
                 by_local))
    legs.append(("a dead local in a second function is caught",
                 ("helper", "tmp") in by_local))
    legs.append(("the dead local carries its key", by_local[("build", "reader")]["key"] ==
                 "counts"))
    legs.append(("the dead local is marked as a face-key read",
                 by_local[("build", "reader")]["key_is_a_dict_literal_key"] is True))
    legs.append(("a parameter dict is published as incoming",
                 by_local[("build", "reader")]["indexed_object_is_incoming"] is True))
    legs.append(("the return value of a call is not a parameter",
                 ("helper", "tmp") in by_local))
    legs.append(("the fixture is a face publisher", publish_signal(tree) is True))
    no_dump = ast.parse("def f(m):\n    x = m['k']\n    return 1\n")
    legs.append(("a module that never dumps is not a publisher",
                 publish_signal(no_dump) is False))

    mods, skipped = population(ROOT)
    names = [r for r, _ in mods]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself",
                 "scripts/e619_dead_reader_locals.py" not in names))
    m = measure(root=ROOT)
    c = counts_of(m)
    legs.append(("counts re-add the module rows",
                 c["scope_facekey_lines"] == sum(r["scope_facekey"] for r in m["modules"])))
    legs.append(("every dead row carries a line and a key",
                 all(isinstance(r.get("line"), int) and isinstance(r.get("key"), str)
                     for mod in m["modules"] for r in mod["dead_reader_locals"])))
    legs.append(("scope_incoming is a subset of scope_facekey",
                 all(r["scope_incoming"] <= r["scope_facekey"] for r in m["modules"])))
    legs.append(("scope_facekey never exceeds scope_all",
                 all(r["scope_facekey"] <= r["scope_all"] for r in m["modules"])))
    e617 = [mod for mod in m["modules"] if mod["module"].endswith(
        "e396_face_basename_suffix.py")]
    legs.append(("the module E617 named is in the population", len(e617) == 1))
    anchor = [r for r in (e617[0]["dead_reader_locals"] if e617 else [])
              if r["function"] == "derive_verdict" and r["local"] == "census"]
    legs.append(("the E617 anchor line reproduces", len(anchor) == 1
                 and anchor[0]["key"] == "basename_census"))
    face, problems = build(root=ROOT)
    legs.append(("the built face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "modules": [dict(r) for r in face["modules"]],
           "verdict": face["verdict"]}
    bad["counts"]["scope_facekey_lines"] = int(bad["counts"]["scope_facekey_lines"]) + 1
    legs.append(("a perturbed count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "modules": [dict(r) for r in face["modules"]],
            "verdict": "no_face_publisher_carries_an_assigned_and_never_read_face_key_local"
            if face["verdict"] !=
            "no_face_publisher_carries_an_assigned_and_never_read_face_key_local" else "other"}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "modules": [dict(r) for r in face["modules"]],
            "verdict": face["verdict"]}
    bad3["modules"] = bad3["modules"][:-1]
    legs.append(("a dropped module row fails face_problems", face_problems(bad3) != []))

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
    print("population=%d modules_with_dead_scope_facekey=%d lines=%d all_lines=%d "
          "incoming_lines=%d skipped=%d"
          % (c["population_modules"], c["modules_with_a_dead_local_scope_facekey"],
             c["scope_facekey_lines"], c["scope_all_lines"], c["scope_incoming_lines"],
             c["skipped_modules"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))