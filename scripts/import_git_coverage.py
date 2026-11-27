"""Does every module this repo imports actually exist in git?

r2202 was the second time in three rounds that a face was green on the machine that built it
and dead on any fresh clone: `three_book_wallet.py` is imported by three committed scripts and
was itself never committed (r1783 named the same class). Both were found by accident, one at a
time, after the fact. The question this face answers needs no new data and no engine: take
every committed Python file, parse what it imports, and ask git whether the thing it imports is
in the tree.

Two lists come out, and they are the whole product:

  imports_missing_in_git  an importer that IS in the tree importing a module that is NOT
                          (exists on this disk only -> every fresh clone runs a broken leg)
  chain_missing_in_git    a script the S6 chain names in a live (uncommented) leg that is NOT
                          in the tree (the r1168 "registered but not runnable" family)

Untracked *importers* are reported separately and are not a defect by themselves: a round that
writes a new face has not committed it yet. The same rule as r1783 -- the judge is
`git ls-tree`, not "it runs on my machine".

    python scripts/import_git_coverage.py run
    python scripts/import_git_coverage.py check     # STALE when the tree/refs moved
    python scripts/import_git_coverage.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "import_git_coverage.json")
PAGE = os.path.join(ROOT, "research", "IMPORT_GIT_COVERAGE.md")
CHAIN = os.path.join(ROOT, "Tools", "s6_chain_bmc.py")

SCAN_DIRS = ("scripts", "Tools", "firm", "live", "monitor", "engine", "strategies",
             "screening", "labbench")
REFS = ("HEAD", "origin/main")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _rel(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def _git(*args, root=None):
    p = subprocess.run(["git", "-C", (ROOT if root is None else root), *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       creationflags=NO_WINDOW)
    return p.returncode, (p.stdout or ""), (p.stderr or "")


def tracked(ref, root=None):
    """Every path in the tree of `ref`, or None when the ref does not exist here."""
    rc, out, _err = _git("ls-tree", "-r", "--name-only", ref, root=root)
    if rc != 0:
        return None
    return set(x for x in out.splitlines() if x)


def py_files(roots=None, root=None):
    root = ROOT if root is None else root
    roots = SCAN_DIRS if roots is None else roots
    files = []
    for d in roots:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [x for x in dn if x != "__pycache__" and not x.startswith(".")]
            for f in fn:
                if f.endswith(".py"):
                    files.append(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/"))
    for f in sorted(os.listdir(root)):
        if f.endswith(".py"):
            files.append(f)
    return sorted(set(files))


def imports_of(path, root=None):
    """[(module, level)] for one file; (None, None) entries are dropped, parse errors reported."""
    root = ROOT if root is None else root
    try:
        with open(os.path.join(root, path), "rb") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, ValueError, OSError):
        return None
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.append((a.name, 0))
        elif isinstance(node, ast.ImportFrom):
            out.append((node.module or "", int(node.level or 0)))
    return out


def parse_error_of(path, root=None):
    root = ROOT if root is None else root
    try:
        with open(os.path.join(root, path), "rb") as f:
            ast.parse(f.read())
        return None
    except SyntaxError as e:
        return "line %s: %s" % (e.lineno, e.msg)
    except (ValueError, OSError) as e:
        return str(e)


def resolve(mod, level, importer, files, by_base=None):
    """Candidate repo paths for an import. Empty list == not a local module."""
    pool = set(files)
    cands = []
    if level:
        base = os.path.dirname(importer)
        for _ in range(level - 1):
            base = os.path.dirname(base)
        stem = (base + "/" if base else "") + (mod.replace(".", "/") if mod else "")
        stem = stem.rstrip("/")
        for c in (stem + ".py", (stem + "/__init__.py") if stem else "__init__.py"):
            if c in pool:
                cands.append(c)
        return cands
    if not mod:
        return cands
    p = mod.replace(".", "/")
    for c in (p + ".py", p + "/__init__.py"):
        if c in pool:
            cands.append(c)
    if not cands and "." not in mod:
        # 20k bare imports x 2.9k files was 150s per scan before this index: a leg that
        # expensive gets skipped, and a skipped gate is the thing this face is about.
        if by_base is not None:
            cands.extend(by_base.get(mod + ".py", ()))
        else:
            for f in files:
                if os.path.basename(f) == mod + ".py":
                    cands.append(f)
    return cands


def chain_refs(chain_path=None, root=None):
    """Live (uncommented) script paths the S6 chain names, in file order."""
    root = ROOT if root is None else root
    chain_path = CHAIN if chain_path is None else chain_path
    if not os.path.exists(chain_path):
        return None
    out = []
    with open(chain_path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for m in re.finditer(r'"((?:scripts|Tools)/[A-Za-z0-9_\-]+\.py)"', line):
                if m.group(1) not in out:
                    out.append(m.group(1))
    return out


PLACEHOLDER = re.compile(r"@@[A-Z0-9_]{2,}@@")


def is_template(path, root=None):
    """A file that cannot parse because it carries an unsubstituted @@SLOT@@ marker.

    The test is on content, not on the filename: a name-based exemption would hide the very
    break this face exists to find (r1789: judge by what is in the file, never by what it is
    called). A template is still counted and named; it is only kept out of the "broken" bucket.
    """
    try:
        with open(os.path.join(ROOT if root is None else root, path), encoding="utf-8",
                  errors="replace") as f:
            return bool(PLACEHOLDER.search(f.read()))
    except OSError:
        return False


def scan(roots=None, refs=REFS, root=None, chain_path=None):
    root = ROOT if root is None else root
    files = py_files(roots, root)
    by_base = {}
    for f in files:
        by_base.setdefault(os.path.basename(f), []).append(f)
    trees = {}
    for r in refs:
        trees[r] = tracked(r, root)
    main_ref = next((r for r in refs if trees.get(r) is not None), None)

    parse_errors, total_imports, local_edges = [], 0, 0
    missing, both_untracked, checked_edges = [], [], 0
    for f in files:
        got = imports_of(f, root)
        if got is None:
            parse_errors.append(f)
            continue
        for mod, level in got:
            total_imports += 1
            cands = resolve(mod, level, f, files, by_base)
            if not cands:
                continue
            local_edges += 1
            if main_ref is None:
                continue
            importer_in = f in trees[main_ref]
            target_in = any(c in trees[main_ref] for c in cands)
            checked_edges += 1
            if importer_in and not target_in:
                missing.append({"importer": f, "module": mod,
                                "target": sorted(cands)[0],
                                "target_candidates": sorted(cands)})
            elif not importer_in and not target_in:
                both_untracked.append({"importer": f, "module": mod,
                                       "target": sorted(cands)[0]})

    named = chain_refs(chain_path, root) or []
    chain_missing_disk, chain_missing_git = [], []
    for p in named:
        if not os.path.exists(os.path.join(root, p)):
            chain_missing_disk.append(p)
        elif main_ref is not None and p not in trees[main_ref]:
            chain_missing_git.append(p)

    digest = hashlib.sha256()
    digest.update("\n".join(files).encode("utf-8"))
    digest.update(("|head=%s" % (main_ref is not None)).encode())
    for r in refs:
        digest.update(("|%s:%s" % (r, trees.get(r) is not None)).encode())

    return {
        "refs": {r: (None if trees.get(r) is None else
                     (_git("rev-parse", r, root=root)[1].strip() or None)) for r in refs},
        "scanned": {"files": len(files), "imports": total_imports,
                    "local_edges": local_edges, "checked_edges": checked_edges,
                    "parse_errors": parse_errors,
                    "digest": digest.hexdigest()},
        # a committed .py that cannot be parsed can never be imported or run: the copy in the
        # tree is not the copy anyone executed (r2202 class, found mechanically rather than by
        # accident). Untracked ones are mid-round drafts. A file carrying an unsubstituted
        # @@SLOT@@ is a generator template and is counted in its own bucket, not as a break.
        "unparseable_tracked": ([p for p in parse_errors if main_ref and p in trees[main_ref]]
                                if main_ref is not None else []),
        "unparseable_untracked": ([p for p in parse_errors
                                   if main_ref is None or p not in trees[main_ref]]
                                  if main_ref is not None else []),
        "unparseable_templates": [p for p in parse_errors if is_template(p, root)],
        "unparseable_broken": [p for p in parse_errors
                               if main_ref is not None and p in trees[main_ref]
                               and not is_template(p, root)],
        "unparseable_reasons": {p: (parse_error_of(p, root) or "")
                                for p in parse_errors
                                if not is_template(p, root)},
        "imports_missing_in_git": sorted(missing, key=lambda d: (d["target"], d["importer"])),
        "imports_both_untracked": sorted(both_untracked, key=lambda d: d["target"]),
        "chain": {"named_scripts": len(named),
                  "missing_on_disk": sorted(chain_missing_disk),
                  "missing_in_git": sorted(chain_missing_git)},
    }


def headline(res):
    n_imp = len(res["imports_missing_in_git"])
    n_chain = len(res["chain"]["missing_in_git"]) + len(res["chain"]["missing_on_disk"])
    if n_imp or n_chain:
        return "FRESH_CLONE_RUNS_BROKEN_LEGS"
    if res.get("unparseable_broken"):
        return "SOME_COMMITTED_FILES_ARE_NOT_PYTHON"
    return "EVERY_IMPORTED_MODULE_AND_EVERY_NAMED_LEG_IS_IN_GIT"


def run():
    res = scan()
    doc = dict(res)
    doc["generated"] = None
    rc_cut, out_cut, _ = _git("show", "-s", "--format=%cd", "--date=short", "HEAD")
    doc["evidence_cutoff"] = out_cut.strip() if rc_cut == 0 else None
    doc["generated"] = subprocess.run(
        [sys.executable, "-c", "import datetime;print(datetime.datetime.now().isoformat(timespec='seconds'))"],
        capture_output=True, text=True, creationflags=NO_WINDOW).stdout.strip()
    doc["headline"] = headline(res)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    write_page(doc)
    print("headline", doc["headline"], flush=True)
    print("scanned %d files / %d imports / %d local edges (parse errors %d)"
          % (doc["scanned"]["files"], doc["scanned"]["imports"],
             doc["scanned"]["local_edges"], len(doc["scanned"]["parse_errors"])), flush=True)
    print("imports missing in git: %d" % len(doc["imports_missing_in_git"]), flush=True)
    for d in doc["imports_missing_in_git"]:
        print("   %s imports %s -> %s" % (d["importer"], d["module"], d["target"]), flush=True)
    print("committed files that cannot be parsed: %d broken / %d generator templates"
          % (len(doc["unparseable_broken"]), len(doc["unparseable_templates"])), flush=True)
    for p in doc["unparseable_broken"]:
        print("   %s is in git and is not Python (%s)"
              % (p, doc["unparseable_reasons"].get(p, "")[:70]), flush=True)
    print("chain named scripts %d: missing on disk %d / missing in git %d"
          % (doc["chain"]["named_scripts"], len(doc["chain"]["missing_on_disk"]),
             len(doc["chain"]["missing_in_git"])), flush=True)
    for p in doc["chain"]["missing_on_disk"]:
        print("   chain names %s -- not on this disk" % p, flush=True)
    for p in doc["chain"]["missing_in_git"]:
        print("   chain names %s -- on this disk, not in git" % p, flush=True)
    print("wrote", _rel(OUT), flush=True)
    return 0


def write_page(doc):
    lines = [
        "# Does every module this repo imports exist in git?",
        "",
        "Generated by `scripts/import_git_coverage.py` (evidence: `results/import_git_coverage.json`).",
        "Judge is `git ls-tree`, not `it runs here` (r1783 / r2202 class).",
        "",
        "| field | value |",
        "|---|---|",
        "| headline | `%s` |" % doc["headline"],
        "| files scanned | %d |" % doc["scanned"]["files"],
        "| imports parsed | %d |" % doc["scanned"]["imports"],
        "| local import edges | %d |" % doc["scanned"]["local_edges"],
        "| imports missing in git | %d |" % len(doc["imports_missing_in_git"]),
        "| committed files that cannot be parsed | %d broken / %d templates |"
        % (len(doc.get("unparseable_broken") or []), len(doc.get("unparseable_templates") or [])),
        "| chain legs named | %d |" % doc["chain"]["named_scripts"],
        "| chain legs missing on disk | %d |" % len(doc["chain"]["missing_on_disk"]),
        "| chain legs missing in git | %d |" % len(doc["chain"]["missing_in_git"]),
        "| evidence cutoff | %s |" % doc.get("evidence_cutoff"),
        "",
    ]
    if doc["imports_missing_in_git"]:
        lines += ["## Imports missing in git", "", "| importer (in git) | module | target |",
                  "|---|---|---|"]
        for d in doc["imports_missing_in_git"]:
            lines.append("| `%s` | `%s` | `%s` |" % (d["importer"], d["module"], d["target"]))
        lines.append("")
    if doc.get("unparseable_broken") or doc.get("unparseable_templates"):
        lines += ["## Files that cannot be parsed", ""]
        for p in doc.get("unparseable_broken") or []:
            lines.append("- `%s` -- in git and not Python (%s); repair or retire"
                         % (p, doc["unparseable_reasons"].get(p, "")))
        for p in doc.get("unparseable_templates") or []:
            lines.append("- `%s` -- carries an unsubstituted `@@SLOT@@`, so it is a generator"
                         " template by content, not a broken script" % p)
        lines.append("")
    if doc["chain"]["missing_in_git"] or doc["chain"]["missing_on_disk"]:
        lines += ["## Chain legs that are not runnable from a clone", ""]
        for p in doc["chain"]["missing_in_git"]:
            lines.append("- `%s` -- on this disk, not in git" % p)
        for p in doc["chain"]["missing_on_disk"]:
            lines.append("- `%s` -- named by the chain, absent from this disk" % p)
        lines.append("")
    if doc["imports_both_untracked"]:
        lines += ["## Imports where neither side is in git (new-file faces, not a defect)",
                  ""]
        for d in doc["imports_both_untracked"]:
            lines.append("- `%s` imports `%s`" % (d["importer"], d["target"]))
        lines.append("")
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def replay(ref):
    """Same scan, but against one named ref instead of HEAD -- the negative control.

    Replaying an older commit is how this face proves it would have caught the defect it was
    built for: r2202's commit is the one that put `scripts/three_book_wallet.py` into git, so
    replaying its parent must name that module (and must name nothing else new).
    """
    res = scan(refs=(ref,))
    print("replay %s -> %s" % (ref, (res["refs"] or {}).get(ref)), flush=True)
    print("imports missing in git: %d" % len(res["imports_missing_in_git"]), flush=True)
    for d in res["imports_missing_in_git"]:
        print("   %s imports %s -> %s" % (d["importer"], d["module"], d["target"]), flush=True)
    print("chain missing in git: %d / on disk: %d"
          % (len(res["chain"]["missing_in_git"]), len(res["chain"]["missing_on_disk"])), flush=True)
    for p in res["chain"]["missing_in_git"]:
        print("   chain names %s -- on this disk, not in %s" % (p, ref), flush=True)
    return 0


def check():
    """rc0 OK / rc3 STALE (tree or refs moved) / rc4 CHECK FAILED (same inputs, other numbers)."""
    if not os.path.exists(OUT):
        print("STALE face missing:", _rel(OUT), flush=True)
        return 3
    with open(OUT, encoding="utf-8") as f:
        old = json.load(f)
    res = scan()
    moved = []
    if old.get("scanned", {}).get("digest") != res["scanned"]["digest"]:
        moved.append("scanned set")
    for r in REFS:
        if (old.get("refs") or {}).get(r) != res["refs"].get(r):
            moved.append("ref %s" % r)
    if moved:
        print("STALE %s moved since the face was written (%s)"
              % (_rel(OUT), ", ".join(moved)), flush=True)
        return 3
    same = (old.get("imports_missing_in_git") == res["imports_missing_in_git"]
            and old.get("chain", {}).get("missing_in_git") == res["chain"]["missing_in_git"]
            and old.get("chain", {}).get("missing_on_disk") == res["chain"]["missing_on_disk"]
            and (old.get("unparseable_broken") or []) == res["unparseable_broken"]
            and (old.get("unparseable_templates") or []) == res["unparseable_templates"])
    if not same:
        print("CHECK FAILED same inputs, different coverage lists: %d vs %d imports, "
              "%d vs %d chain legs"
              % (len(old.get("imports_missing_in_git") or []), len(res["imports_missing_in_git"]),
                 len((old.get("chain") or {}).get("missing_in_git") or []),
                 len(res["chain"]["missing_in_git"])), flush=True)
        return 4
    print("OK %d files / %d imports / %d missing / chain %d missing in git (headline %s)"
          % (res["scanned"]["files"], res["scanned"]["imports"],
             len(res["imports_missing_in_git"]), len(res["chain"]["missing_in_git"]),
             headline(res)), flush=True)
    return 0


def selftest():
    import tempfile
    ok, tot = [0], [0]

    def chk(cond, msg):
        tot[0] += 1
        if cond:
            ok[0] += 1
        else:
            print("FAIL", msg, flush=True)

    files = ["scripts/alpha.py", "scripts/beta.py", "firm/risk/b_layer_filter.py",
             "scripts/deep/mod.py", "scripts/mod.py"]
    chk(resolve("alpha", 0, "scripts/beta.py", files) == ["scripts/alpha.py"],
        "bare module resolves by basename")
    chk(resolve("firm.risk.b_layer_filter", 0, "scripts/beta.py", files)
        == ["firm/risk/b_layer_filter.py"], "dotted import resolves to the file")
    chk(resolve("mod", 1, "scripts/deep/other.py", files) == ["scripts/deep/mod.py"],
        "relative import resolves against the importer's own directory")
    chk(resolve("mod", 2, "scripts/deep/other.py", files) == ["scripts/mod.py"],
        "two-dot relative import climbs out one level")
    chk(resolve("numpy", 0, "scripts/beta.py", files) == [],
        "a third-party import resolves to nothing and is never flagged")
    chk(resolve("", 0, "scripts/beta.py", files) == [], "an empty module name resolves to nothing")

    with tempfile.TemporaryDirectory() as td:
        chain = os.path.join(td, "chain.py")
        with open(chain, "w", encoding="utf-8") as f:
            f.write('    ("live", ["python", "scripts/here.py"]),\n'
                    '#    ("dead", ["python", "scripts/gone.py"]),\n')
        named = chain_refs(chain, td)
        chk(named == ["scripts/here.py"], "commented-out legs are not counted (%s)" % named)

        # a real tree: seed.py committed, user.py + ghost.py both untracked, then user.py alone
        sub = os.path.join(td, "repo")
        os.makedirs(os.path.join(sub, "scripts"))
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ.get("PATH", "")}
        subprocess.run(["git", "init", "-q", sub], capture_output=True, creationflags=NO_WINDOW)
        with open(os.path.join(sub, "scripts", "seed.py"), "w", encoding="utf-8") as f:
            f.write("K = 0\n")
        with open(os.path.join(sub, "scripts", "user.py"), "w", encoding="utf-8") as f:
            f.write("import ghost\n")
        with open(os.path.join(sub, "scripts", "ghost.py"), "w", encoding="utf-8") as f:
            f.write("K = 1\n")
        subprocess.run(["git", "-C", sub, "add", "scripts/seed.py"],
                       capture_output=True, creationflags=NO_WINDOW)
        subprocess.run(["git", "-C", sub, "commit", "-qm", "t"],
                       capture_output=True, env=env, creationflags=NO_WINDOW)

        res0 = scan(roots=("scripts",), refs=("HEAD",), root=sub)
        chk(len(res0["imports_missing_in_git"]) == 0,
            "untracked importer + untracked target is not reported as a fresh-clone break")
        chk(any(d["target"] == "scripts/ghost.py" for d in res0["imports_both_untracked"]),
            "untracked importer + untracked target is reported in its own bucket (%s)"
            % res0["imports_both_untracked"])

        subprocess.run(["git", "-C", sub, "add", "scripts/user.py"],
                       capture_output=True, creationflags=NO_WINDOW)
        subprocess.run(["git", "-C", sub, "commit", "-qm", "t2"],
                       capture_output=True, env=env, creationflags=NO_WINDOW)
        res2 = scan(roots=("scripts",), refs=("HEAD",), root=sub)
        chk(any(d["target"] == "scripts/ghost.py" for d in res2["imports_missing_in_git"]),
            "a tracked importer of an untracked module is named (%s)"
            % res2["imports_missing_in_git"])
        chk(headline(res2) == "FRESH_CLONE_RUNS_BROKEN_LEGS",
            "one break flips the headline")
        chk(headline({"imports_missing_in_git": [],
                      "chain": {"missing_in_git": [], "missing_on_disk": []}})
            == "EVERY_IMPORTED_MODULE_AND_EVERY_NAMED_LEG_IS_IN_GIT",
            "no break prints the clean headline")
        chk(headline({"imports_missing_in_git": [],
                      "chain": {"missing_in_git": [], "missing_on_disk": []},
                      "unparseable_broken": ["scripts/broken.py"]})
            == "SOME_COMMITTED_FILES_ARE_NOT_PYTHON",
            "a committed file that cannot be parsed is named, not called clean")
        with tempfile.TemporaryDirectory() as t2:
            plain = os.path.join(t2, "plain.py")
            with open(plain, "w", encoding="utf-8") as f:
                f.write("X = 'unterminated\n")
            chk(is_template(os.path.relpath(plain, t2), t2) is False,
                "a file broken for another reason is not excused as a template")
            tp = os.path.join(t2, "tpl.py")
            with open(tp, "w", encoding="utf-8") as f:
                f.write("X = 1\n@@SUB_BLOCK@@\n")
            chk(is_template(os.path.relpath(tp, t2), t2) is True,
                "an unsubstituted @@SLOT@@ is recognised by content")
            chk(parse_error_of(os.path.relpath(tp, t2), t2) is not None,
                "and the same file is still recorded as unparseable (%s)"
                % parse_error_of(os.path.relpath(tp, t2), t2))

        # behaviour leg: a missing face must say STALE, not FAIL
        g = globals()
        keep = g["OUT"]
        try:
            g["OUT"] = os.path.join(td, "nope.json")
            import io as _io
            from contextlib import redirect_stdout
            buf = _io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            chk(rc == 3 and "STALE" in buf.getvalue(),
                "check on a missing face returns 3 and says STALE (%d / %r)"
                % (rc, buf.getvalue()[:40]))
        finally:
            g["OUT"] = keep

    print("selftest %d/%d" % (ok[0], tot[0]), flush=True)
    return 0 if ok[0] == tot[0] else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    if cmd == "replay":
        if len(argv) < 3:
            print("replay needs a ref", flush=True)
            return 2
        return replay(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
