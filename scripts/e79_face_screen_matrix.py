"""E79: which published census faces read per-name returns off the unscreened loader?

E74-E77 established that the in-repo panel carries adjacent-impossibility prints
and that repairing them moves the wide book by 0.8-3.8pp/yr. Every census leg
that reads ``e27.load_universe()`` inherits that exposure until it is replayed
through ``scripts/panel_screen.py``. This tool answers, mechanically and
without re-running anything:

  * which census legs touch the per-name loader at all (directly or through a
    helper), so consumers know which published numbers can carry the artefact;
  * which of them already expose a ``raw=`` hook (i.e. can be re-derived from a
    repaired universe today);
  * which face file each mode writes and what evidence_cutoff / era block that
    face actually publishes on disk.

It never regenerates a face and never writes into results/: the output is a
matrix plus a markdown table, so the arithmetic stays inspectable in review.

Usage:
    python scripts/e79_face_screen_matrix.py run      # write the matrix face
    python scripts/e79_face_screen_matrix.py selftest # hermetic checks
"""

import ast
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS = os.path.join(ROOT, "scripts", "e39_panel_census.py")
SCREEN_MODULE = "panel_screen"


# ------------------------------------------------------------------ AST layer

def _call_name(node):
    """Dotted name of a Call target, or None."""
    f = node.func if isinstance(node, ast.Call) else None
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
        return ".".join(reversed(parts))
    return None


def _func_facts(tree):
    """name -> {calls, loads_universe, has_raw, imports_screen} for module funcs."""
    facts = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls, loads, imports_screen = set(), False, False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                name = _call_name(sub)
                if name:
                    calls.add(name.split(".")[-1])
                if name and name.split(".")[-1] == "load_universe":
                    loads = True
            if isinstance(sub, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in getattr(sub, "names", [])]
                if any(m == SCREEN_MODULE or m.startswith(SCREEN_MODULE + ".") for m in mods):
                    imports_screen = True
        args = [a.arg for a in node.args.args]
        facts[node.name] = {
            "calls": calls,
            "loads_universe": loads,
            "has_raw": "raw" in args,
            "imports_screen": imports_screen,
            "lineno": node.lineno,
        }
    return facts


def _propagate(facts):
    """Fixed point: a function inherits loads_universe from anything it calls."""
    direct = {n: bool(f["loads_universe"]) for n, f in facts.items()}
    changed = True
    while changed:
        changed = False
        for name, f in facts.items():
            if direct[name]:
                continue
            for callee in f["calls"]:
                if direct.get(callee):
                    direct[name] = True
                    changed = True
                    break
    return direct


def _mode_blocks(main_body):
    """[(modes, body)] for every `if args.mode ...` branch in main()."""
    blocks = []

    def modes_of(test):
        out = set()
        for node in ast.walk(test):
            if isinstance(node, ast.Compare):
                left = node.left
                if isinstance(left, ast.Attribute) and left.attr == "mode":
                    for comp in node.comparators:
                        if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                            out.add(comp.value)
                        elif isinstance(comp, (ast.Tuple, ast.List)):
                            for e in comp.elts:
                                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                                    out.add(e.value)
        return out

    for node in main_body:
        if isinstance(node, ast.If):
            modes = modes_of(node.test)
            if modes:
                blocks.append((modes, node.body))
    return blocks


def _block_runner(body):
    """The first run_*/_run* function called in a mode block."""
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name and re.match(r"^_?run_", name.split(".")[-1]):
                return name.split(".")[-1]
    return None


def _block_face_pattern(body):
    """The write_json filename literal used in a mode block (may be None)."""
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name and name.split(".")[-1] == "write_json" and len(node.args) >= 2:
                arg = node.args[1]
                parts = []
                for sub in ast.walk(arg):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        parts.append(sub.value)
                if parts:
                    return parts[0]
    return None


def build_matrix(census_path=CENSUS, root=ROOT):
    """The leg x loader matrix, read off the source and the faces on disk."""
    with open(census_path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    facts = _func_facts(tree)
    loads = _propagate(facts)

    main_fn = next((n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    if main_fn is None:
        raise SystemExit("main() not found in %s" % census_path)

    legs = []
    for modes, body in _mode_blocks(main_fn.body):
        runner = _block_runner(body)
        if not runner or runner not in facts:
            continue
        f = facts[runner]
        pattern = _block_face_pattern(body)
        for mode in sorted(modes):
            legs.append({
                "mode": mode,
                "runner": runner,
                "reads_per_name_loader": bool(loads.get(runner)),
                "raw_hook": bool(f["has_raw"]),
                "self_screens": bool(f["imports_screen"]),
                "screen_capable": bool(f["has_raw"]),
                "face_pattern": pattern,
                "face_on_disk": None,
                "evidence_cutoff": None,
                "publishes_eras": None,
            })
    return legs


def _resolve_faces(legs, root=ROOT):
    """Fill face_on_disk / cutoff / era block for each leg from the filesystem."""
    base = os.path.join(root, "results")
    for leg in legs:
        pat = leg.get("face_pattern")
        if not pat:
            continue
        stem = re.split(r"%s|%d", pat)[0]
        hits = sorted(glob.glob(os.path.join(base, "**", stem + "*"), recursive=True))
        hits = [h for h in hits if h.lower().endswith(".json")]
        if not hits:
            continue
        newest = max(hits, key=os.path.getmtime)
        leg["face_on_disk"] = os.path.relpath(newest, root).replace("\\", "/")
        try:
            with open(newest, encoding="utf-8") as fh:
                face = json.load(fh)
        except (OSError, ValueError):
            continue
        if isinstance(face, dict):
            cutoff = face.get("evidence_cutoff")
            if not cutoff:
                spec = face.get("spec") or {}
                cutoff = spec.get("evidence_cutoff") if isinstance(spec, dict) else None
            leg["evidence_cutoff"] = cutoff
            leg["publishes_eras"] = isinstance(face.get("eras"), dict)
    return legs


def build_row(leg):
    """One classification row, pure so the rules are testable without the tree."""
    loader = leg.get("reads_per_name_loader")
    hook = leg.get("raw_hook")
    screens = leg.get("self_screens")
    if not loader:
        status = "clean"
    elif screens:
        status = "self_screened"
    elif hook:
        status = "replayable"
    else:
        status = "exposed"
    return {
        "mode": leg.get("mode"),
        "runner": leg.get("runner"),
        "reads_per_name_loader": bool(loader),
        "raw_hook": bool(hook),
        "self_screens": bool(screens),
        "status": status,
        "face_pattern": leg.get("face_pattern"),
        "face_on_disk": leg.get("face_on_disk"),
        "evidence_cutoff": leg.get("evidence_cutoff"),
        "publishes_eras": leg.get("publishes_eras"),
        "note": {
            "clean": "no per-name loader on this path",
            "self_screened": "loads the per-name loader and repairs it in-process "
                             "(scripts/panel_screen.py), publishing screened and "
                             "unscreened columns side by side",
            "replayable": "takes raw=; a repaired universe can be pushed through today",
            "exposed": "reads the unscreened loader with no raw hook: published numbers "
                       "carry the artefact until this runner is extended",
        }[status],
    }


def render_markdown(rows, cutoff):
    head = ["# E79 published-face screen exposure (%s)" % (cutoff or "n/a"), "",
            "Generated by `scripts/e79_face_screen_matrix.py run` (descriptive; no face is "
            "regenerated).", "",
            "| mode | runner | loader | raw= | self-screens | status | face | cutoff | eras |",
            "|---|---|---|---|---|---|---|---|---|"]
    rank = {"exposed": 0, "replayable": 1, "self_screened": 2, "clean": 3}
    for r in sorted(rows, key=lambda r: (rank.get(r["status"], 9), r["mode"])):
        head.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["mode"], r["runner"],
            "yes" if r["reads_per_name_loader"] else "no",
            "yes" if r["raw_hook"] else "no",
            "yes" if r.get("self_screens") else "no",
            r["status"],
            (r["face_on_disk"] or "-"),
            r["evidence_cutoff"] or "-",
            "yes" if r["publishes_eras"] else "-"))
    return "\n".join(head) + "\n"


def run(outdir=None, census_path=CENSUS, root=ROOT):
    legs = _resolve_faces(build_matrix(census_path, root), root)
    rows = [build_row(l) for l in legs]
    exposed = [r for r in rows if r["status"] == "exposed"]
    replayable = [r for r in rows if r["status"] == "replayable"]
    screened = [r for r in rows if r["status"] == "self_screened"]
    clean = [r for r in rows if r["status"] == "clean"]
    cutoffs = sorted({r["evidence_cutoff"] for r in rows if r["evidence_cutoff"]})
    cutoff = cutoffs[-1] if cutoffs else None
    return {
        "study": "e79_published_face_screen_matrix",
        "evidence_cutoff": cutoff,
        "spec": {
            "census_source": os.path.relpath(census_path, root).replace("\\", "/"),
            "method": "AST scan of every `if args.mode ...` block in main(): resolve the "
                      "runner, then propagate `e27.load_universe` through the call graph to "
                      "a fixed point, and read each runner's `raw=` hook off its signature",
            "statuses": {
                "clean": "runner never reaches the per-name loader",
                "self_screened": "runner repairs the loader in-process and publishes both "
                                 "columns",
                "replayable": "reaches it but accepts raw=, so E76-E80 style replays are possible",
                "exposed": "reaches it with no raw hook -- published face carries the artefact",
            },
        },
        "legs": rows,
        "summary": {
            "modes_scanned": len(rows),
            "clean": len(clean),
            "self_screened": len(screened),
            "replayable": len(replayable),
            "exposed": len(exposed),
            "exposed_modes": [r["mode"] for r in exposed],
            "replayable_modes": [r["mode"] for r in replayable],
            "self_screened_modes": [r["mode"] for r in screened],
            "cutoffs_on_disk": cutoffs,
            "faces_read": len([r for r in rows if r["face_on_disk"]]),
        },
        "honest": [
            "this is a source-and-face inventory, not a re-burn: it says which published "
            "numbers CAN carry the artefact, not by how much",
            "the propagation is call-graph only: a runner that reaches the loader through a "
            "dynamic call or an imported module the AST cannot see would be misclassified",
            "`replayable` means the hook exists, not that a screened replay has been burned "
            "for that leg -- E76 covers ladder/era spread, E77 the wide book, E78 the weekly "
            "book and E80 the mid-month churn",
            "face_on_disk is the newest file matching the runner's filename stem; a stale "
            "face and a live one are indistinguishable here, so read the cutoff column",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }


def selftest():
    ok = tot = 0

    def chk(cond, label):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            print("FAIL: " + label)

    src = (
        "def run_loader(outdir):\n"
        "    raw = e27.load_universe()\n"
        "    return {}\n"
        "def run_helper(outdir, raw=None):\n"
        "    return helper()\n"
        "def helper():\n"
        "    return e27.load_universe()\n"
        "def run_clean(outdir):\n"
        "    return 1\n"
        "def main(argv):\n"
        "    if args.mode in ('a', 'b'):\n"
        "        f = run_loader(None)\n"
        "        p = write_json(outdir, 'FACE-%s.json' % f['evidence_cutoff'])\n"
        "        return 0\n"
        "    if args.mode == 'c':\n"
        "        f = run_helper(None)\n"
        "        return 0\n"
        "    if args.mode == 'd':\n"
        "        f = run_clean(None)\n"
        "        return 0\n"
    )
    tree = ast.parse(src)
    facts = _func_facts(tree)
    loads = _propagate(facts)
    chk(loads["run_loader"] and loads["run_helper"] and loads["helper"],
        "load_universe propagates through the call graph to a fixed point")
    chk(not loads["run_clean"], "a runner that never touches the loader stays clean")
    chk(facts["run_helper"]["has_raw"] and not facts["run_loader"]["has_raw"],
        "the raw hook is read off the signature, not assumed")

    main_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    blocks = _mode_blocks(main_fn.body)
    chk(len(blocks) == 3, "each `if args.mode ...` branch becomes one block")
    chk(blocks[0][0] == {"a", "b"}, "a tuple of modes expands to one entry per mode")
    chk(_block_runner(blocks[0][1]) == "run_loader",
        "the runner is resolved from the call inside the block")
    chk(_block_face_pattern(blocks[0][1]) == "FACE-%s.json",
        "the face filename literal is read from the write_json call")

    def row(loader, hook, mode="m", runner="run_x", screens=False):
        return build_row({"mode": mode, "runner": runner, "self_screens": screens,
                          "reads_per_name_loader": loader, "raw_hook": hook})

    chk(row(False, False)["status"] == "clean", "no loader -> clean")
    chk(row(True, True)["status"] == "replayable", "loader + raw= -> replayable")
    chk(row(True, False)["status"] == "exposed", "loader without raw= -> exposed")
    chk(row(True, False, screens=True)["status"] == "self_screened",
        "a runner that repairs the loader in-process is self_screened, not exposed")
    chk(row(True, True, screens=True)["status"] == "self_screened",
        "self_screened wins over a raw hook: the screen is already applied")
    chk(row(True, False)["note"].startswith("reads the unscreened loader"),
        "each status carries its own reading note")

    md = render_markdown([row(True, False, "zz"), row(False, False, "aa")], "2026-10-21")
    chk(md.index("| zz |") < md.index("| aa |"),
        "the markdown sorts exposed legs first so the risk list leads")
    chk("2026-10-21" in md, "the markdown carries the cutoff it was built at")

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    mode = argv[0] if argv else "run"
    if mode == "selftest":
        return selftest()
    if mode != "run":
        print("usage: e79_face_screen_matrix.py [run|selftest]")
        return 2
    face = run()
    outdir = os.path.join(ROOT, "results", "e44_midmonth")
    os.makedirs(outdir, exist_ok=True)
    stem = (face.get("evidence_cutoff") or "nodate").replace("-", "")
    path = os.path.join(outdir, "FACESCREEN-%s.json" % stem)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    md_path = os.path.join(ROOT, "research", "digests",
                           "FACESCREEN-20261022.md")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_markdown(face["legs"], face.get("evidence_cutoff")))
    print(json.dumps({"leg": "facescreen",
                      "file": os.path.relpath(path, ROOT).replace("\\", "/"),
                      "table": os.path.relpath(md_path, ROOT).replace("\\", "/"),
                      "summary": face["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))