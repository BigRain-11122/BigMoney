"""E602 -- what a reader does when a pointer redirect's target is missing.

Card: ``E602-WHAT-A-READER-DOES-WHEN-A-REDIRECT-TARGET-HAS-DANGLED`` (seeded r1629 bm-b).

E599 priced the two ENDS of every redirect edge and found that no module compares them.  It
also found two live edges dangling on this checkout while their payload sat next to the
pointer.  That raises a question E599 did not ask: when the target is absent at READ time,
does anything fail loudly, fall back to something else, or read nothing and publish anyway?

This is a static read-time census, not a repair:

* edges come from ``e599.scan()`` -- the same edges E599 published, so the two faces join;
* for each edge, the modules that SPELL its target (basename or a folded ``join``) are the
  candidates -- naming is not opening (E470), so each one is graded on what it does with it;
* every candidate is graded from its own source on five published flags and one class.

Classes (a name is a measurement claim -- the flags are published beside the class so a
reader can re-derive it):

    invisible      names the target, never calls a loader            -> reads nothing, silently
    bare_load      loads with no guard of any kind                   -> raises (loud)
    guarded_loud   has an existence guard AND raises/exits somewhere -> raises (loud)
    guard_silent   has a guard and never raises anywhere             -> reads nothing, silently
    unreadable     source does not parse                             -> no claim

Limits are published in the face: the flags are module-level, not site-level, so a module
that guards one load and bare-loads another is graded by the union of its guards.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e598_pointer_bar_demand as e598                                     # noqa: E402
import e599_pointer_redirect_bar as e599                                   # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "REDIRECTMISSINGATREAD.json")
LATEST_PATH = os.path.join(OUTDIR, "REDIRECTMISSINGATREAD-latest.json")
SELF_NAME = "e602_redirect_missing_at_read.py"
STUDY = "E602_redirect_missing_at_read"

LOADER_NAMES = {"open", "load", "loads", "load_json", "read_json", "read_csv", "read_text",
                "read_bytes", "read_parquet", "_load", "_read", "_load_json", "_read_json",
                "readfile", "read_file", "from_json", "read_journal"}
EXISTS_ATTRS = {"exists", "isfile", "is_file", "isdir", "is_dir", "lexists"}
SILENT_CLASSES = ("invisible", "guard_silent")
LOUD_CLASSES = ("bare_load", "guarded_loud")

C_INVISIBLE = "invisible"
C_BARE = "bare_load"
C_GUARDED_LOUD = "guarded_loud"
C_GUARD_SILENT = "guard_silent"
C_UNREADABLE = "unreadable"
CLASSES = (C_INVISIBLE, C_BARE, C_GUARDED_LOUD, C_GUARD_SILENT, C_UNREADABLE)

V_NO_EDGES = "no_pointer_face_redirects_anywhere_so_the_question_has_no_subject"
V_NO_READERS = "no_redirect_target_is_named_by_any_module_in_the_repo"
V_ALL_SILENT = ("every_module_that_names_a_redirect_target_reads_nothing_when_it_is_absent"
                "_and_none_of_them_fails_loudly")
V_NONE_SILENT = "every_module_that_names_a_redirect_target_fails_loudly_when_it_is_absent"
V_MIXED = ("some_redirect_target_readers_would_raise_on_a_missing_target_and_some_would"
           "_silently_read_nothing")
V_NO_LIVE_DANGLE = ("no_redirect_target_is_missing_on_this_checkout_so_the_answer_is_a"
                    "_latent_handling_class_not_a_live_defect")


# --------------------------------------------------------------------------- pure helpers
def normalise(literal):
    s = literal.replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return s


def is_loader(node):
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Name):
        return f.id in LOADER_NAMES
    if isinstance(f, ast.Attribute):
        return f.attr in LOADER_NAMES
    return False


def spelled_literals(src):
    """Every string constant the module spells, normalised, plus folded ``join`` paths."""
    out = set()
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lit = normalise(node.value)
            if lit:
                out.add(lit)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "join":
            parts = []
            ok = True
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    parts.append(normalise(a.value))
                elif isinstance(a, (ast.Name, ast.Attribute)):
                    continue
                else:
                    ok = False
                    break
            if ok and parts:
                out.add("/".join(p for p in parts if p))
    return out


def lits_name(lits, target_basename, target_rel):
    """``names_target`` over an already-parsed literal set (one parse per module)."""
    if not lits:
        return False
    for lit in lits:
        if lit.split("/")[-1] == target_basename:
            return True
        if target_rel and "/" in lit:
            if lit.endswith(target_rel) or target_rel.endswith(lit):
                return True
    return False


def names_target(src, target_basename, target_rel):
    """Does this module spell THIS target?

    Three shapes only, and every one of them must carry a path segment or the whole basename:
    a bare suffix such as ``.json`` is spelled by hundreds of modules and names no face at all
    (first build: 570 modules "named" every .json target because ``.json`` ends the path).
    """
    lits = spelled_literals(src)
    if not lits:
        return False
    for lit in lits:
        if lit.split("/")[-1] == target_basename:
            return True
        if target_rel and "/" in lit:
            if lit.endswith(target_rel) or target_rel.endswith(lit):
                return True
    return False


def grade_src(src):
    """Five published flags plus the derived class.  Pure function of the source text."""
    flags = {"opens": False, "existence_guard": False, "try_around_load": False,
             "or_default": False, "raise_or_exit": False}
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        flags["class"] = C_UNREADABLE
        return flags
    loads = set()
    for node in ast.walk(tree):
        if is_loader(node):
            flags["opens"] = True
            loads.add(id(node))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in EXISTS_ATTRS:
            flags["existence_guard"] = True
        elif isinstance(node, ast.Raise):
            flags["raise_or_exit"] = True
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "exit":
            flags["raise_or_exit"] = True
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            for sub in ast.walk(node):
                if is_loader(sub):
                    flags["or_default"] = True
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and not flags["try_around_load"]:
            for sub in ast.walk(node):
                if is_loader(sub):
                    if id(sub) in loads:
                        flags["try_around_load"] = True
                    break
        if isinstance(node, ast.Try) and node.handlers and not flags["try_around_load"]:
            for h in node.handlers:
                for sub in ast.walk(h):
                    if is_loader(sub):
                        flags["try_around_load"] = True
                        break
    if not flags["opens"]:
        cls = C_INVISIBLE
    elif not (flags["existence_guard"] or flags["try_around_load"] or flags["or_default"]):
        cls = C_BARE
    elif flags["raise_or_exit"]:
        cls = C_GUARDED_LOUD
    else:
        cls = C_GUARD_SILENT
    flags["class"] = cls
    return flags


# --------------------------------------------------------------------------- scan
def scan(root=None):
    root = root or ROOT
    edges = e599.scan(root)["pairs"]
    mods = [m for m in e598.modules_on_disk(root) if not m.endswith(SELF_NAME)]
    srcs = {}
    for m in mods:
        srcs[m] = e598.read_src(root, m) or ""
    # one parse per module: ``spelled_literals`` and ``grade_src`` both walk the AST, and doing
    # that 12 times per module cost 279s on the first S6 run -- the literals are computed once
    # and the grade is only computed for a module that names at least one target.
    lits = {m: spelled_literals(s) for m, s in srcs.items()}
    graded = {}

    def _grade(m):
        if m not in graded:
            graded[m] = grade_src(srcs[m])
        return graded[m]

    rows = []
    matched = set()
    for e in edges:
        raw = e["raw_value"]
        base = normalise(raw).split("/")[-1]
        target_rel = e.get("resolved_path") or normalise(raw)
        hit = [m for m in mods if lits_name(lits[m], base, target_rel)]
        matched.update(hit)
        readers = []
        for m in hit:
            g = _grade(m)
            readers.append({
                "module": m, "class": g["class"],
                "opens": g["opens"], "existence_guard": g["existence_guard"],
                "try_around_load": g["try_around_load"], "or_default": g["or_default"],
                "raise_or_exit": g["raise_or_exit"],
                "silent_if_absent": g["class"] in SILENT_CLASSES,
            })
        rows.append({
            "pointer_face": e["pointer_face"], "key": e["key"], "relation": e["relation"],
            "raw_value": raw, "target_basename": base, "target_path": target_rel,
            "exists_today": e["exists"], "target_kind": e["target_kind"],
            "repair_path": e.get("repair_path"),
            "readers": readers,
            "class_counts": {c: sum(1 for r in readers if r["class"] == c) for c in CLASSES},
        })
    dangling = [r for r in rows if not r["exists_today"]]
    silent = [{"pointer_face": r["pointer_face"], "module": x["module"], "class": x["class"]}
              for r in rows for x in r["readers"] if x["silent_if_absent"]]
    return {"edges": rows, "counts": recount(rows), "dangling": dangling,
            "silent_modules": silent, "n_modules_graded": len(mods)}


def recount(rows):
    c = {"edges": len(rows), "dangling_edges_today": sum(1 for r in rows if not r["exists_today"]),
         "edges_with_a_reader": sum(1 for r in rows if r["readers"]),
         "edges_with_no_reader": sum(1 for r in rows if not r["readers"]),
         "reader_sites": sum(len(r["readers"]) for r in rows),
         "distinct_reader_modules": len({x["module"] for r in rows for x in r["readers"]})}
    for cls in CLASSES:
        c["readers_" + cls] = sum(1 for r in rows for x in r["readers"] if x["class"] == cls)
    c["readers_silent_if_absent"] = sum(1 for r in rows for x in r["readers"]
                                        if x["silent_if_absent"])
    c["readers_loud_if_absent"] = sum(1 for r in rows for x in r["readers"]
                                      if x["class"] in LOUD_CLASSES)
    return c


def verdict_from(counts):
    if counts["edges"] == 0:
        return V_NO_EDGES
    if counts["reader_sites"] == 0:
        return V_NO_READERS
    if counts["readers_silent_if_absent"] and not counts["readers_loud_if_absent"]:
        return V_ALL_SILENT
    if counts["readers_loud_if_absent"] and not counts["readers_silent_if_absent"]:
        return V_NONE_SILENT
    return V_MIXED


def answer_sentence(counts, dangling):
    live = V_NO_LIVE_DANGLE if not dangling else ""
    base = ("%d redirect edges carry %d reader sites across %d modules: %d would read nothing "
            "without complaint and %d would raise"
            % (counts["edges"], counts["reader_sites"], counts["distinct_reader_modules"],
               counts["readers_silent_if_absent"], counts["readers_loud_if_absent"]))
    return base + ("; " + live.replace("_", " ") if live else "")


def build(write=True, root=None):
    root = root or ROOT
    s = scan(root)
    counts = s["counts"]
    face = {
        "study": STUDY,
        "card": "E602",
        "evidence_cutoff": "2026-11-06",
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, s["dangling"]),
        "edges": s["edges"],
        "silent_modules": s["silent_modules"],
        "silent_class_present": bool(s["silent_modules"]),
        "limits": [
            "flags are module-level, not site-level: a module that guards one load and "
            "bare-loads another is graded by the union of its guards",
            "naming is not opening (E470): a module that spells the target and never calls a "
            "loader is published as invisible rather than as a reader",
            "a guard inside a helper function in another module is invisible to this census",
            "targets are resolved by e599.scan, so this face inherits its resolution bases",
        ],
        "n_modules_graded": s["n_modules_graded"],
    }
    if write:
        write_face(face)
    return face


def write_face(face):
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for p in (OUT_PATH, LATEST_PATH):
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return OUT_PATH


def face_problems(face):
    problems = []
    for k in ("study", "card", "evidence_cutoff", "counts", "verdict", "answer", "edges"):
        if k not in face:
            problems.append("missing key %s" % k)
    c = face.get("counts") or {}
    if c.get("reader_sites") != sum(len(r["readers"]) for r in face.get("edges", [])):
        problems.append("reader_sites does not re-derive")
    recomputed = recount(face.get("edges", []))
    for k, v in recomputed.items():
        if c.get(k) != v:
            problems.append("counts[%s] does not re-derive (%r vs %r)" % (k, c.get(k), v))
    for r in face.get("edges", []):
        for x in r["readers"]:
            der = grade_ok(x)
            if der:
                problems.append("%s %s: %s" % (r["pointer_face"], x["module"], der))
    return problems


def grade_ok(x):
    cls = x["class"]
    if cls == C_INVISIBLE and x["opens"]:
        return "invisible but opens"
    if cls == C_BARE and (x["existence_guard"] or x["try_around_load"] or x["or_default"]):
        return "bare_load but guarded"
    if cls == C_GUARD_SILENT and x["raise_or_exit"]:
        return "guard_silent but raises"
    if cls in SILENT_CLASSES and not x["silent_if_absent"]:
        return "silent class not flagged silent"
    if cls in LOUD_CLASSES and x["silent_if_absent"]:
        return "loud class flagged silent"
    return None


# --------------------------------------------------------------------------- selftest
FIX_INVISIBLE = "p = 'results/x/latest.json'\nprint(p)\n"
FIX_BARE = "import json\nd = json.load(open('results/x/latest.json'))\n"
FIX_GUARD_SILENT = ("import os, json\np = 'results/x/latest.json'\nd = {}\n"
                    "if os.path.exists(p):\n    d = json.load(open(p))\nprint(d)\n")
FIX_GUARD_LOUD = ("import os, json, sys\np = 'results/x/latest.json'\n"
                  "if not os.path.exists(p):\n    sys.exit(2)\nd = json.load(open(p))\n")
FIX_TRY_SILENT = ("import json\np = 'results/x/latest.json'\ntry:\n"
                  "    d = json.load(open(p))\nexcept Exception:\n    d = {}\n")


def selftest():
    fails = []

    def ck(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    g = grade_src(FIX_INVISIBLE)
    ck("L1 invisible", g["class"] == C_INVISIBLE, g)
    ck("L2 invisible does not open", g["opens"] is False, g)
    ck("L3 invisible is silent", g["class"] in SILENT_CLASSES, g["class"])

    g = grade_src(FIX_BARE)
    ck("L4 bare", g["class"] == C_BARE, g)
    ck("L5 bare opens", g["opens"] is True, g)
    ck("L6 bare has no guard", not (g["existence_guard"] or g["try_around_load"]
                                    or g["or_default"]), g)
    ck("L7 bare is loud", g["class"] in LOUD_CLASSES, g["class"])

    g = grade_src(FIX_GUARD_SILENT)
    ck("L8 guard_silent", g["class"] == C_GUARD_SILENT, g)
    ck("L9 guard_silent has existence guard", g["existence_guard"] is True, g)
    ck("L10 guard_silent never raises", g["raise_or_exit"] is False, g)
    ck("L11 guard_silent is silent", g["class"] in SILENT_CLASSES, g["class"])

    g = grade_src(FIX_GUARD_LOUD)
    ck("L12 guarded_loud", g["class"] == C_GUARDED_LOUD, g)
    ck("L13 guarded_loud raises", g["raise_or_exit"] is True, g)

    g = grade_src(FIX_TRY_SILENT)
    ck("L14 try_silent graded guard_silent", g["class"] == C_GUARD_SILENT, g)
    ck("L15 try around load detected", g["try_around_load"] is True, g)

    g = grade_src("def f(:\n  pass\n")
    ck("L16 unreadable", g["class"] == C_UNREADABLE, g)

    g = grade_src("import json\nd = json.load(open(p)) or {}\n")
    ck("L17 or_default detected", g["or_default"] is True, g)
    ck("L18 or_default is not bare", g["class"] != C_BARE, g["class"])

    # naming
    ck("L19 names basename", names_target(FIX_BARE, "latest.json", "results/x/latest.json"))
    ck("L20 does not name other", not names_target(FIX_BARE, "other.json", "results/x/other.json"))
    # a bare suffix is spelt by hundreds of modules and names no face (first build's 4,284 sites)
    ck("L20b bare suffix names nothing",
       not names_target("p = '.json'\nprint(p)\n", "TICKET-2026-11-06.json",
                        "results/etf_book_order/TICKET-2026-11-06.json"))
    ck("L20c a spelling path segment does name it",
       names_target("p = 'TICKET-2026-11-06.json'\n", "TICKET-2026-11-06.json",
                    "results/etf_book_order/TICKET-2026-11-06.json"))
    ck("L20d a longer enclosing path names it",
       names_target("p = 'results/etf_book_order/TICKET-2026-11-06.json'\n",
                    "TICKET-2026-11-06.json",
                    "results/etf_book_order/TICKET-2026-11-06.json"))

    # grading is a pure function of the source: same input, same output
    a = grade_src(FIX_GUARD_SILENT)
    b = grade_src(FIX_GUARD_SILENT)
    ck("L21 grade is stable", a == b)

    # recount re-derives from rows
    rows = [{"exists_today": True, "readers": [
        {"module": "m1", "class": C_GUARD_SILENT, "silent_if_absent": True},
        {"module": "m2", "class": C_BARE, "silent_if_absent": False}]},
        {"exists_today": False, "readers": []}]
    c = recount(rows)
    ck("L22 edges", c["edges"] == 2, c)
    ck("L23 dangling", c["dangling_edges_today"] == 1, c)
    ck("L24 sites", c["reader_sites"] == 2, c)
    ck("L25 distinct modules", c["distinct_reader_modules"] == 2, c)
    ck("L26 silent count", c["readers_silent_if_absent"] == 1, c)
    ck("L27 loud count", c["readers_loud_if_absent"] == 1, c)
    ck("L28 no-reader edge", c["edges_with_no_reader"] == 1, c)

    ck("L29 verdict mixed", verdict_from(c) == V_MIXED, verdict_from(c))
    ck("L30 verdict no edges", verdict_from({"edges": 0}) == V_NO_EDGES)
    ck("L31 verdict no readers", verdict_from(
        {"edges": 1, "reader_sites": 0, "readers_silent_if_absent": 0,
         "readers_loud_if_absent": 0}) == V_NO_READERS)

    # a class whose flags contradict it is a problem, not a reading
    bad = [{"pointer_face": "f", "readers": [{"module": "m", "class": C_INVISIBLE,
                                              "opens": True, "silent_if_absent": True}]}]
    ck("L32 contradiction is caught", grade_ok(bad[0]["readers"][0]) is not None)
    good = [{"module": "m", "class": C_BARE, "opens": True, "existence_guard": False,
             "try_around_load": False, "or_default": False, "raise_or_exit": False,
             "silent_if_absent": False}]
    ck("L33 consistent row is clean", grade_ok(good[0]) is None, grade_ok(good[0]))

    total = 37
    print("selftest %d/%d" % (total - len(fails), total))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    # ``check`` re-derives in memory and refuses a face that would change; it never writes, so a
    # S6 leg cannot rewrite a published face while another machine is reading it.
    check_only = "check" in argv
    face = build(write=not check_only)
    if check_only:
        on_disk = e599.load_json(OUT_PATH)
        if not isinstance(on_disk, dict):
            print("problems=['the face is not on disk; run without check first']")
            return 1
        diffs = [k for k in face if on_disk.get(k) != face[k]]
        if diffs:
            print("problems=['the published face does not re-derive: %s']" % diffs)
            return 1
    print(json.dumps({"counts": face["counts"], "verdict": face["verdict"],
                      "answer": face["answer"], "out": OUT_PATH}, ensure_ascii=False, indent=1))
    probs = face_problems(face)
    if probs:
        print("problems=%s" % probs)
        return 1
    print("problems=[]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
