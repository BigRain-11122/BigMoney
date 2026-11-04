"""E406 -- a reader of a committed blob can disagree with the file beside it, and nobody measures it.

E401 priced every site the stdlib call table called ``other`` and found all 10 are git-object reads:
``subprocess.run(["git", "show", "HEAD:"+path])`` and family, across 4 keys and 63 direct helpers.
A working-tree read and a committed-blob read of the same published face disagree whenever the face
is newer than the last commit -- which it is, all day, because the round publishes and then commits.

This study asks the question per reader, not per key:

    mode      does the site read a git object, the working tree, or both
    compare   does the module holding the reader ever put the two readings side by side
    gap       for every published face the reader can name, how far apart are the blob and the file
              *right now* -- top-level keys that differ, headline scalars that moved, bytes

Nothing is rewritten and git is only read (``git show``, never a write).  The bill is the reader
table plus the measured disagreement per face.

    python scripts/e406_blob_vs_tree_readers.py run
    python scripts/e406_blob_vs_tree_readers.py verify
    python scripts/e406_blob_vs_tree_readers.py selftest
"""
import ast
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e401_local_reader as e401  # noqa: E402

TODAY = "2026-11-05"
STUDY = "E406_blob_vs_tree_readers"
FACE = "BLOBREAD-%s.json" % TODAY
LATEST = "blobread_latest.json"
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
PUBLISHED_DIR = OUTDIR
SELF_REL = "scripts/e406_blob_vs_tree_readers.py"
OWN_FILES = (FACE, LATEST, "scripts/run_e406_smoke_leg.py")

MAX_FACES = 200
MAX_ROWS = 400

# A face name is a file name under results/ that a round publishes: either a dated face or a
# ``*_latest.json`` mirror.  Names, not paths -- the reader may join a directory onto them.
FACE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]*(_latest\.json|-\d{4}-\d{2}-\d{2}\.json)$")
PATHISH_RE = re.compile(r"^(results/|docs/|state/|fleet/).+\.(json|md|csv)$")

MODE_GIT = "git_object"
MODE_BOTH = "both_arms_in_one_module"

V_NEVER_COMPARED = "no_module_that_reads_a_committed_blob_ever_compares_it_to_the_file"
V_SOME_COMPARE = "some_module_compares_the_blob_to_the_file_and_the_rest_cannot_notice_a_drift"
V_NO_READERS = "no_git_object_reader_in_the_corpus"
V_EMPTY = "no_published_face_is_read_from_a_blob_so_the_question_does_not_apply"
VERDICTS = (V_NEVER_COMPARED, V_SOME_COMPARE, V_NO_READERS, V_EMPTY)


def say(message):
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


def _no_window():
    if os.name != "nt":
        return {}
    return {"creationflags": 0x08000000}


def git_show_text(rev, path):
    """The blob as a commit has it; (None, reason) when that revision does not hold the path."""
    try:
        p = subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=ROOT,
                           capture_output=True, **_no_window())
    except Exception as exc:  # pragma: no cover - git absent
        return None, "git_unavailable:%r" % (exc,)
    if p.returncode != 0:
        return None, "absent_at_rev"
    return p.stdout, "ok"


def head_rev():
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, **_no_window())
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace").strip() or None


def _str_constants(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
    return out


def git_callables(sources):
    """The E401 arm reused, not rewritten: every corpus callable that spawns a git object read."""
    defs, parsed, failed = e401.local_defs(sources)
    resolved = e401.resolve(defs)
    rows = []
    for name, info in sorted(resolved.items()):
        if not info.get("git_object"):
            continue
        entries = defs.get(name) or []
        rows.append({
            "callable": name,
            "depth": info.get("depth"),
            "chain": list(info.get("chain") or []),
            "sources": sorted({e["source"] for e in entries}),
            "sites": sorted({"%s:%d" % (e["source"], e["line"]) for e in entries}),
        })
    return rows, {"corpus_sources": len(sources), "parsed": parsed, "parse_failed": failed,
                  "definitions": len(defs), "git_callables": len(rows)}


def face_names_in(node, source_text_literals):
    """Names this callable can put in front of git: literals in the body, plus (only for a
    parameterised reader) the face-name literals of the module that calls it."""
    names = set()
    for lit in _str_constants(node):
        base = lit.split(":", 1)[1] if lit.startswith("HEAD:") else lit
        tail = os.path.basename(base.strip())
        if FACE_NAME_RE.match(tail):
            names.add(tail)
    return names


def call_sites(sources, git_names):
    """Deprecated shim kept for the selftest's older fixtures: same-module attribution only."""
    sites, _unresolved, _arms, _owner = census_modules(sources, git_names)
    return sites


def _face_tail(text):
    base = text.split(":", 1)[1] if text.startswith("HEAD:") else text
    tail = os.path.basename(base.strip())
    return tail if FACE_NAME_RE.match(tail) else None


def census_modules(sources, git_names):
    """One pass per module: which calls actually reach a git-object helper, and what it reads.

    A corpus-wide name match is the wrong instrument: ``_head``/``main``/``raw`` are reused by
    unrelated modules (E366's one-name-two-entities), and the first build inflated to 2,811 sites
    over 1,729 modules on exactly that.  A call is attributed when the callee is defined as a
    git-object helper in this module, or is imported here from the module that defines it.  A bare
    name that no import resolves stays in ``unresolved_name_rows`` and is never counted.

    Face names are collected with a disclosed basis, because a helper usually takes the path as a
    parameter and the literal then lives at the call site -- or, one step weaker, anywhere in a
    module that passes a path at runtime.
    """
    parsed = {}
    stem_map = {}
    for rel, text in sources:
        try:
            parsed[rel] = ast.parse(text)
        except SyntaxError:
            continue
        stem_map.setdefault(os.path.splitext(os.path.basename(rel))[0], rel)

    owner = {}
    for rel, tree in parsed.items():
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name in git_names and e401.git_object_read(node):
                owner.setdefault(node.name, set()).add(rel)

    sites, unresolved, arms = [], [], {}
    for rel, tree in sorted(parsed.items()):
        local = {name for name, mods in owner.items() if rel in mods}
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                src = stem_map.get(node.module.split(".")[-1])
                if not src:
                    continue
                for alias in node.names:
                    if alias.name in owner and src in owner[alias.name]:
                        imports[alias.name] = src
        reachable = set(local) | set(imports)
        arm = {"git": set(), "git_basis": {}, "tree": set()}
        arms[rel] = arm
        takes_a_path = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in local:
                if node.args.args:
                    takes_a_path = True
                for lit in _str_constants(node):
                    tail = _face_tail(lit)
                    if tail:
                        arm["git"].add(tail)
                        arm["git_basis"][tail] = "literal_in_body"
            if not isinstance(node, ast.Call):
                continue
            callee = e401.e384.callee_name(node)
            if isinstance(node.func, ast.Attribute) is False and node.args:
                pass
            klass = e401.e384.classify_call(callee)
            for arg in node.args[:3]:
                # ``json.load(open("x.json"))`` nests the path one call deep, so the literal is
                # collected from the whole argument subtree rather than only a bare Constant.
                for lit in _str_constants(arg):
                    tail = _face_tail(lit)
                    if not tail:
                        continue
                    if callee in reachable:
                        arm["git"].add(tail)
                        arm["git_basis"].setdefault(tail, "literal_at_call_site")
                    elif klass == e401.e384.SITE_LOAD:
                        arm["tree"].add(tail)
            if callee in local:
                sites.append({"module": rel, "line": node.lineno, "callee": callee,
                              "resolved_by": "defined_here"})
            elif callee in imports:
                sites.append({"module": rel, "line": node.lineno, "callee": callee,
                              "resolved_by": "imported_from:" + imports[callee]})
            elif callee in git_names:
                unresolved.append({"module": rel, "line": node.lineno, "callee": callee})
        if reachable and takes_a_path:
            for node in ast.walk(tree):
                for lit in _str_constants(node):
                    tail = _face_tail(lit)
                    if tail and tail not in arm["git_basis"]:
                        arm["git"].add(tail)
                        arm["git_basis"][tail] = "module_face_literal"
    return sites, unresolved, arms, owner


def locate(name):
    """The on-disk face a bare name refers to, searching the published families only."""
    for rel in (os.path.join("results", "state_tilt", name), os.path.join("results", name)):
        if os.path.exists(os.path.join(ROOT, rel)):
            return rel.replace(os.sep, "/")
    stack = [os.path.join(ROOT, "results")]
    while stack:
        cur = stack.pop()
        try:
            entries = os.listdir(cur)
        except OSError:
            continue
        for entry in entries:
            full = os.path.join(cur, entry)
            if os.path.isdir(full):
                if entry.startswith("_"):
                    continue
                stack.append(full)
            elif entry == name:
                return os.path.relpath(full, ROOT).replace(os.sep, "/")
    return None


def headline(doc):
    out = {}
    if not isinstance(doc, dict):
        return out
    if "verdict" in doc:
        out["verdict"] = doc["verdict"]
    s = doc.get("summary")
    if isinstance(s, dict):
        for k in sorted(s):
            if isinstance(s[k], (int, float, str)) and not isinstance(s[k], bool):
                out["summary.%s" % k] = s[k]
    return out


def gap_for(rel, rev):
    """How far apart the committed blob and the working-tree file are right now."""
    row = {"face": rel, "rev": rev}
    if not os.path.exists(os.path.join(ROOT, rel)):
        row.update({"state": "not_on_disk", "keys_moved": 0, "headline_moved": 0})
        return row
    with io.open(os.path.join(ROOT, rel), "rb") as fh:
        disk_bytes = fh.read()
    blob, reason = git_show_text(rev or "HEAD", rel)
    if blob is None:
        row.update({"state": "absent_at_head", "keys_moved": 0, "headline_moved": 0,
                    "disk_bytes": len(disk_bytes), "why": reason})
        return row
    row["disk_bytes"] = len(disk_bytes)
    row["blob_bytes"] = len(blob)
    row["bytes_differ"] = len(disk_bytes) != len(blob)
    try:
        disk_doc = json.loads(disk_bytes.decode("utf-8"))
        blob_doc = json.loads(blob.decode("utf-8"))
    except Exception:
        row.update({"state": "unparsed", "keys_moved": 0, "headline_moved": 0,
                    "bytes_differ": len(disk_bytes) != len(blob)})
        return row
    dk = set(disk_doc) if isinstance(disk_doc, dict) else set()
    bk = set(blob_doc) if isinstance(blob_doc, dict) else set()
    keys_moved = len(dk ^ bk)
    if isinstance(disk_doc, dict) and isinstance(blob_doc, dict):
        keys_moved += sum(1 for k in (dk & bk) if disk_doc.get(k) != blob_doc.get(k))
    hd = headline(disk_doc)
    hb = headline(blob_doc)
    moved = [k for k in set(hd) | set(hb) if hd.get(k) != hb.get(k)]
    row.update({
        "state": "compared",
        "top_keys_disk": len(dk),
        "top_keys_blob": len(bk),
        "keys_moved": keys_moved,
        "headline_moved": len(moved),
        "headline_samples": sorted(moved)[:6],
        "verdict_disk": hd.get("verdict"),
        "verdict_blob": hb.get("verdict"),
    })
    return row


def build(write_face=True, sources=None, rev=None):
    sources = sources if sources is not None else e401.corpus()
    rev = rev or head_rev()
    rows, census = git_callables(sources)
    names = {r["callable"] for r in rows}
    sites, unresolved, arms, _owner = census_modules(sources, names)

    reader_rows = []
    for site in sites:
        module = site["module"]
        arm = arms.get(module) or {"git": set(), "tree": set()}
        paired = sorted(arm["git"] & arm["tree"])
        reader_rows.append({
            "module": module,
            "line": site["line"],
            "callee": site["callee"],
            "resolved_by": site.get("resolved_by"),
            "mode": MODE_GIT if not arm["tree"] else MODE_BOTH,
            "compares_the_two_arms": bool(paired),
            "paired_faces": paired[:6],
            "faces_read_from_a_blob": sorted(arm["git"])[:12],
            "faces_read_from_the_tree": sorted(arm["tree"])[:12],
        })

    declared = {}
    for module, arm in arms.items():
        for name in arm.get("git") or ():
            entry = declared.setdefault(name, {"modules": set(),
                                               "basis": arm["git_basis"].get(name, "unknown")})
            entry["modules"].add(module)
    paired_anywhere = sorted(n for n, e in declared.items()
                             if any(n in ((arms.get(m) or {}).get("tree") or set())
                                    for m in e["modules"]))

    gaps = []
    for name in sorted(declared)[:MAX_FACES]:
        entry = declared[name]
        rel = locate(name)
        if rel is None:
            gaps.append({"face": name, "state": "name_resolved_to_no_file", "keys_moved": 0,
                         "headline_moved": 0, "basis": entry["basis"],
                         "read_by": sorted(entry["modules"])[:6]})
            continue
        row = gap_for(rel, rev)
        row["face_name"] = name
        row["basis"] = entry["basis"]
        row["read_by"] = sorted(entry["modules"])[:6]
        gaps.append(row)

    compared = [g for g in gaps if g.get("state") == "compared"]
    disagreeing = [g for g in compared if g.get("keys_moved") or g.get("headline_moved")
                   or g.get("bytes_differ")]
    verdict_moved = [g for g in compared
                     if g.get("verdict_disk") is not None
                     and g.get("verdict_disk") != g.get("verdict_blob")]
    comparing_modules = sorted({r["module"] for r in reader_rows if r["compares_the_two_arms"]})

    if not reader_rows:
        verdict = V_NO_READERS
    elif not gaps:
        verdict = V_EMPTY
    elif comparing_modules:
        verdict = V_SOME_COMPARE
    else:
        verdict = V_NEVER_COMPARED

    summary = {
        "git_object_callables": census["git_callables"],
        "corpus_sources": census["corpus_sources"],
        "parse_failed": census["parse_failed"],
        "call_sites": len(reader_rows),
        "unresolved_name_rows": len(unresolved),
        "modules_holding_a_reader": len({r["module"] for r in reader_rows}),
        "modules_that_compare_both_arms": len(comparing_modules),
        "faces_named_by_a_blob_reader": len(declared),
        "faces_measured": len(gaps),
        "faces_compared": len(compared),
        "faces_whose_blob_and_file_differ": len(disagreeing),
        "faces_whose_verdict_string_moved": len(verdict_moved),
        "faces_absent_at_head": sum(1 for g in gaps if g.get("state") == "absent_at_head"),
        "faces_the_name_resolves_to_nothing": sum(
            1 for g in gaps if g.get("state") == "name_resolved_to_no_file"),
        "largest_key_delta": max([g.get("keys_moved") or 0 for g in compared] or [0]),
        "largest_headline_delta": max([g.get("headline_moved") or 0 for g in compared] or [0]),
        "paired_faces": len(paired_anywhere),
        "max_faces_cap": MAX_FACES,
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "rev": rev,
        "verdict": verdict,
        "rule": {
            "mode": "the E401 arm resolves the callable; the module's own load literals say whether "
                    "a working-tree arm exists at all",
            "compare": "a module compares the two only if the SAME face name appears in both arms",
            "gap": "git show <rev>:<face> against the bytes on disk, at this moment; git is read, "
                   "never written",
            "no_rewrite": "no reader was edited; the fix stays a separate card",
        },
        "summary": summary,
        "reader_rows": reader_rows[:MAX_ROWS],
        "unresolved_name_rows": unresolved[:MAX_ROWS],
        "faces_by_basis": {b: sorted(n for n, e in declared.items() if e["basis"] == b)[:20]
                           for b in sorted({e["basis"] for e in declared.values()})},
        "modules": [{"module": m, "git_faces": sorted((arms.get(m) or {}).get("git") or []),
                     "tree_faces": sorted((arms.get(m) or {}).get("tree") or []),
                     "compares_the_two_arms": bool(
                         ((arms.get(m) or {}).get("git") or set())
                         & ((arms.get(m) or {}).get("tree") or set()))}
                    for m in sorted({r["module"] for r in reader_rows})],
        "faces": gaps,
        "large_deltas": sorted(
            [g for g in compared if (g.get("keys_moved") or 0) > 0],
            key=lambda g: (-(g.get("keys_moved") or 0), g["face"]))[:15],
    }
    if write_face:
        _write(doc)
    return doc


def _write(doc):
    os.makedirs(OUTDIR, exist_ok=True)
    with io.open(os.path.join(OUTDIR, FACE), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    mirror = dict(doc)
    mirror["face"] = FACE
    with io.open(os.path.join(OUTDIR, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def verify(path=None):
    path = path or os.path.join(OUTDIR, FACE)
    problems = []
    if not os.path.exists(path):
        return ["no published blob-read face"]
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    s = doc.get("summary") or {}
    if doc.get("verdict") not in VERDICTS:
        problems.append("verdict outside the frozen vocabulary")
    rows = doc.get("reader_rows") or []
    if len(rows) > MAX_ROWS:
        problems.append("the reader table is over its own cap")
    if s.get("call_sites") != len(rows):
        problems.append("the call-site count does not match the reader rows")
    if len({r["module"] for r in rows}) != s.get("modules_holding_a_reader"):
        problems.append("the module count does not re-derive from the rows")
    faces = doc.get("faces") or []
    if s.get("faces_measured") != len(faces):
        problems.append("the measured-face count does not match the face rows")
    compared = [g for g in faces if g.get("state") == "compared"]
    if s.get("faces_compared") != len(compared):
        problems.append("the compared-face count does not re-derive")
    disagreeing = [g for g in compared if g.get("keys_moved") or g.get("headline_moved")
                   or g.get("bytes_differ")]
    if s.get("faces_whose_blob_and_file_differ") != len(disagreeing):
        problems.append("the disagreement count does not re-derive from the rows")
    for g in faces:
        if g.get("state") == "compared" and g.get("headline_moved") != len(
                g.get("headline_samples") or []) and (g.get("headline_moved") or 0) <= 6:
            problems.append("%s: headline samples do not match the moved count" % g.get("face"))
            break
    for r in rows:
        if r.get("compares_the_two_arms") and not r.get("paired_faces"):
            problems.append("a comparing module names no paired face: %s" % r.get("module"))
            break
    if doc.get("rev") is None and compared:
        problems.append("a comparison was published without a revision")
    return problems


def selftest():
    fails = []

    def ok(cond, name):
        if not cond:
            fails.append(name)

    ok(FACE_NAME_RE.match("siblingentry_latest.json") is not None, "L1 a latest mirror is a face name")
    ok(FACE_NAME_RE.match("REPUBLISH-2026-11-03.json") is not None, "L2 a dated face is a face name")
    ok(FACE_NAME_RE.match("notes.txt") is None, "L3 a non-face is not a face name")
    ok(FACE_NAME_RE.match("results/state_tilt/x_latest.json") is None,
       "L4 a path is not a bare face name")

    src = ('import subprocess\n'
           'def show(p):\n'
           '    return subprocess.run(["git", "show", "HEAD:" + p], capture_output=True)\n'
           'def use():\n'
           '    return show("alpha_latest.json")\n')
    _s, _u, arms, _o = census_modules([("scripts/fake.py", src)], {"show"})
    ok(arms["scripts/fake.py"]["git"] == {"alpha_latest.json"},
       "L5 the git arm comes from the call site when the helper takes a path")
    ok(arms["scripts/fake.py"]["tree"] == set(),
       "L6 a git read does not become a tree arm")

    src2 = ('import json, subprocess\n'
            'def show(p):\n'
            '    return subprocess.run(["git", "show", "HEAD:" + p], capture_output=True)\n'
            'def read():\n'
            '    return json.load(open("beta_latest.json", encoding="utf-8"))\n'
            'def both():\n'
            '    return show("beta_latest.json"), read()\n')
    _s2, _u2, arms2, _o2 = census_modules([("scripts/fake2.py", src2)], {"show"})
    ok(arms2["scripts/fake2.py"]["git"] == {"beta_latest.json"}, "L7 git arm found beside a tree arm")
    ok(arms2["scripts/fake2.py"]["tree"] == {"beta_latest.json"}, "L8 tree arm found for a literal load")
    ok(bool(arms2["scripts/fake2.py"]["git"] & arms2["scripts/fake2.py"]["tree"]),
       "L9 the same name in both arms is a comparison")

    src3 = ('import subprocess\n'
            'def show(p):\n'
            '    return subprocess.run(["git", "show", "HEAD:" + p], capture_output=True)\n'
            'def show_fixed():\n'
            '    return subprocess.run(["git", "show", "HEAD:gamma_latest.json"], '
            'capture_output=True)\n')
    _s3, _u3, arms3, _o3 = census_modules([("scripts/fake3.py", src3)], {"show", "show_fixed"})
    ok(arms3["scripts/fake3.py"]["git"] == {"gamma_latest.json"},
       "L14 a hard-coded name in the helper body is still a git arm")

    # the name-collision case the first build got wrong: a module that merely HAS a function of
    # the same name must contribute no site and no face.
    src4 = ('import subprocess\n'
            'def _head(x):\n'
            '    return subprocess.run(["git", "show", "HEAD:x_latest.json"], capture_output=True)\n'
            'def run():\n'
            '    return _head(1)\n')
    src5 = ('def _head(x):\n'
            '    return x\n'
            'def use():\n'
            '    return _head("delta_latest.json")\n')
    _s4, _u4, arms4, _o4 = census_modules(
        [("scripts/owner.py", src4), ("scripts/other.py", src5)], {"_head"})
    ok(_s4 and all(r["module"] == "scripts/owner.py" for r in _s4),
       "L15 a same-name definition in another module is not a call site")
    ok("delta_latest.json" not in arms4.get("scripts/other.py", {}).get("git", set()),
       "L16 and it contributes no blob face")

    ok(headline({"verdict": "v", "summary": {"a": 1, "flag": True}}) == {"verdict": "v", "summary.a": 1},
       "L10 booleans are not measurements")
    ok(headline(None) == {}, "L11 a missing document has no headline")
    ok(set(VERDICTS) == {V_NEVER_COMPARED, V_SOME_COMPARE, V_NO_READERS, V_EMPTY},
       "L12 frozen vocabulary")
    ok(os.path.basename("HEAD:results/state_tilt/x_latest.json").startswith("x_"),
       "L13 the HEAD: prefix is stripped before matching")
    return _report(fails, 14)


def _report(fails, total):
    print("E406 selftest %d/%d" % (total - len(fails), total))
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "run":
        doc = build()
        s = doc["summary"]
        print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
        print("verdict: %s" % doc["verdict"])
        print("%d call sites / %d modules / %d faces measured: %d differ now, %d verdict strings "
              "moved, %d comparing modules"
              % (s["call_sites"], s["modules_holding_a_reader"], s["faces_measured"],
                 s["faces_whose_blob_and_file_differ"], s["faces_whose_verdict_string_moved"],
                 s["modules_that_compare_both_arms"]))
        return 0
    print("unknown mode: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))