"""Prove a smoke leg runs inside the suite, not only in the runner that extracts it.

The r1377 defect: the E350/E353 standalone runners each start with ``import re`` and lift the
leg's source out of ``smoke_test.py`` by AST, so the leg passed standalone while the suite
raised ``NameError: name 're' is not defined`` -- because ``smoke_test.py`` itself never
imported ``re``.  A runner that supplies its own imports is not a proof that the suite can
run the leg.

This tool rebuilds the suite's own module head (module-level imports, helpers and constants,
skipping ``main()``), executes an extracted leg statement block against exactly that
namespace plus ``check``/``RESULTS``, and reports what a leg may not reach.  Anything a
runner injects but the suite does not define surfaces as NameError here.

Usage:
    python scripts/prove_smoke_leg_isolation.py                 # every known leg anchor
    python scripts/prove_smoke_leg_isolation.py E350 E353       # just these
    python scripts/prove_smoke_leg_isolation.py --selftest
"""
import ast
import json
import os
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "smoke_test.py")

# Legs that are lifted into their own runner (scripts/run_eNNN_smoke_leg.py).
LEG_ANCHORS = [
    "E341", "E342", "E346", "E349", "E350", "E351", "E352", "E353",
]


def suite_head(src: str) -> dict:
    """The namespace `smoke_test.py` has before `main()` runs: imports, helpers, constants."""
    tree = ast.parse(src)
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                             ast.AsyncFunctionDef, ast.ClassDef)):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                continue
            keep.append(node)
        elif isinstance(node, ast.Assign) and all(
                isinstance(t, ast.Name) for t in node.targets):
            keep.append(node)
    mod = ast.Module(body=keep, type_ignores=[])
    ns = {"__name__": "smoke_test_head", "__file__": SMOKE}
    exec(compile(mod, "<smoke_head>", "exec"), ns)  # noqa: S102 - the suite's own source
    return ns


def extract_leg(src: str, marker: str) -> str:
    """Same extraction the standalone runners use: the statement block keyed by `_name<marker>`."""
    name = "_name" + marker.lstrip("E")
    tree = ast.parse(src)
    start = tail = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            start = node.lineno
        if (isinstance(node, ast.Call) and node.args
                and isinstance(node.args[0], ast.Name) and node.args[0].id == name):
            tail = max(tail or 0, getattr(node, "end_lineno", node.lineno))
    if not start or not tail:
        raise LookupError("could not locate the %s leg by AST" % marker)
    lines = src.splitlines()
    head = start - 1
    for i in range(start - 1, 0, -1):
        if lines[i].lstrip().startswith("# %s:" % marker):
            head = i
            break
    return textwrap.dedent("\n".join(lines[head:tail]))


def run_leg_in_suite(ns_head: dict, leg_src: str):
    """Execute the leg against the suite head only. Returns (ok, detail)."""
    rows = []

    def _check(name, ok, detail=""):
        rows.append((name, bool(ok), detail))

    ns = dict(ns_head)
    ns["RESULTS"] = rows
    ns["check"] = _check
    try:
        exec(compile(leg_src, "<leg>", "exec"), ns)  # noqa: S102 - the suite's own leg source
    except Exception as exc:  # NameError is the defect this tool exists for
        return False, "%s: %s" % (type(exc).__name__, exc)
    if not rows:
        return False, "leg called check() zero times"
    bad = [r for r in rows if not r[1]]
    if bad:
        return False, "leg reported %d failing check(s): %s" % (len(bad), bad[0][0])
    return True, rows[0][2][:160]


def prove(markers, suite_src=None):
    src = suite_src if suite_src is not None else open(SMOKE, encoding="utf-8").read()
    ns = suite_head(src)
    out = []
    for marker in markers:
        try:
            leg = extract_leg(src, marker)
        except LookupError as exc:
            out.append({"leg": marker, "ok": False, "detail": str(exc)})
            continue
        ok, detail = run_leg_in_suite(ns, leg)
        out.append({"leg": marker, "ok": ok, "detail": detail})
    return out


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    fixture_ok = (
        'import json\n'
        'def check(name, ok, detail=""):\n'
        '    RESULTS.append((name, ok, detail))\n'
        'RESULTS = []\n'
        'def main():\n'
        '    _name999 = "product: fixture"\n'
        '    _m = re.search(r"a(\\d+)", "a7")\n'
        '    check(_name999, _m.group(1) == "7", "reached re")\n'
    )
    # NOTE: the fixture above has no `import re`, exactly like smoke_test.py before r1377.
    res = prove(["E999"], suite_src=fixture_ok)
    leg("a suite that never imports re rejects a leg that uses it",
        res[0]["ok"] is False and "NameError" in res[0]["detail"] and "re" in res[0]["detail"],
        json.dumps(res[0]["detail"])[:120])

    fixture_fixed = fixture_ok.replace("import json\n", "import json\nimport re\n")
    res = prove(["E999"], suite_src=fixture_fixed)
    leg("the same leg passes once the suite head imports re", res[0]["ok"] is True,
        json.dumps(res[0]["detail"])[:120])

    fixture_runner_only = (
        'import json\n'
        'RESULTS = []\n'
        'def check(name, ok, detail=""):\n'
        '    RESULTS.append((name, ok, detail))\n'
        'def main():\n'
        '    _name998 = "product: fixture"\n'
        '    check(_name998, True, str(requests.__name__))\n'
    )
    res = prove(["E998"], suite_src=fixture_runner_only)
    leg("a name the runner injects but the suite lacks is caught",
        res[0]["ok"] is False and "requests" in res[0]["detail"], res[0]["detail"][:120])

    fixture_main_only = (
        'import json\n'
        'RESULTS = []\n'
        'def check(name, ok, detail=""):\n'
        '    RESULTS.append((name, ok, detail))\n'
        'def main():\n'
        '    _poison = 1\n'
        '    _name997 = "product: fixture"\n'
        '    check(_name997, True, str(_poison))\n'
    )
    res = prove(["E997"], suite_src=fixture_main_only)
    leg("main() body is not part of the head (a leg-local name is not inherited)",
        res[0]["ok"] is False and "_poison" in res[0]["detail"], res[0]["detail"][:120])

    fixture_no_check = (
        'import json\n'
        'RESULTS = []\n'
        'def check(name, ok, detail=""):\n'
        '    RESULTS.append((name, ok, detail))\n'
        'def main():\n'
        '    _name996 = "product: fixture"\n'
        '    _x = 1\n'
    )
    res = prove(["E996"], suite_src=fixture_no_check)
    leg("an anchor with no check() call is refused by extraction rather than read as a pass",
        res[0]["ok"] is False and "could not locate" in res[0]["detail"], res[0]["detail"])

    live = prove(LEG_ANCHORS)
    leg("every known leg runs against its own suite head",
        all(r["ok"] for r in live),
        "; ".join("%s=%s" % (r["leg"], "ok" if r["ok"] else r["detail"][:60]) for r in live))

    bad = [x for x in legs if not x[1]]
    for name, ok, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             " | " + detail if detail else ""))
    print("prove_smoke_leg_isolation selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


FACE_DIR = os.path.join(ROOT, "results", "state_tilt")


def build_face(asof=None) -> dict:
    """The published face: one verdict per runner-backed leg, plus the suite-head import census."""
    asof = asof or __import__("datetime").date.today().isoformat()
    src = open(SMOKE, encoding="utf-8").read()
    ns = suite_head(src)
    rows = prove(LEG_ANCHORS, suite_src=src)
    ok = [r for r in rows if r["ok"]]
    summary = {
        "legs": len(rows),
        "legs_executing_in_suite_head": len(ok),
        "legs_failing": len(rows) - len(ok),
        "suite_head_names": len(ns),
    }
    verdict = ("every_runner_backed_leg_executes_against_the_suite_module_head"
               if len(ok) == len(rows) and rows
               else "at_least_one_runner_backed_leg_needs_a_name_the_suite_does_not_define")
    return {
        "study": "E355_leg_isolation",
        "asof": asof,
        "evidence_cutoff": asof,
        "summary": summary,
        "verdict": verdict,
        "rows": rows,
        "bound": ("the prover rebuilds the suite's module-level imports, helpers and constants and "
                  "executes each leg's own source; it does not run main() end to end, so a leg can "
                  "still be wrong about a value while being reachable"),
    }


def write_face() -> dict:
    face = build_face()
    os.makedirs(FACE_DIR, exist_ok=True)
    dated = os.path.join(FACE_DIR, "LEGISOLATION-%s.json" % face["asof"])
    latest = os.path.join(FACE_DIR, "leg_isolation_latest.json")
    blob = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(blob)
    return face


def verify_face() -> list:
    latest = os.path.join(FACE_DIR, "leg_isolation_latest.json")
    problems = []
    if not os.path.exists(latest):
        return ["no published leg-isolation face"]
    disk = json.load(open(latest, encoding="utf-8"))
    fresh = build_face(asof=disk.get("asof"))
    for k in ("verdict", "summary"):
        if disk.get(k) != fresh.get(k):
            problems.append("%s does not re-derive" % k)
    if disk.get("rows") != fresh.get("rows"):
        problems.append("the per-leg rows do not re-derive")
    return problems


def main(argv) -> int:
    if argv == ["--face"]:
        face = write_face()
        print(json.dumps(face["summary"], sort_keys=True))
        return 0 if face["summary"]["legs_failing"] == 0 else 1
    if argv == ["--verify"]:
        problems = verify_face()
        print("verify problems=%s" % json.dumps(problems))
        return 0 if not problems else 1
    if not argv or argv == ["--selftest"]:
        return selftest()
    markers = [a for a in argv if not a.startswith("-")]
    rows = prove(markers)
    for r in rows:
        print("[%s] %s | %s" % ("PASS" if r["ok"] else "FAIL", r["leg"], r["detail"]))
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))