"""Extract the E448 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e436_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it flips a published orphan into a supersession with no
open under its parent, runs the same leg text, and restores the face byte-identically (the sha in
and the sha out are printed and must match).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "droppedpath_latest.json")
START = "# E448 (r1466 bm-b)"
END = "if __name__ =="


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
    body = lines[start:end]
    harness = [
        "import json, os, sys",
        "RESULTS = []",
        "def check(name, ok, detail=''):",
        "    RESULTS.append((name, bool(ok), detail))",
        "    if not %r:" % quiet,
        "        print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
        "",
    ]
    os.chdir(ROOT)
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    code = "\n".join(harness + body)
    scope: dict = {}
    exec(compile(code, "<e448 leg>", "exec"), scope)
    return scope["RESULTS"]


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def main(argv):
    doctor = "--doctor" in argv
    face = json.load(io.open(FACE, encoding="utf-8"))
    before = sha(FACE)
    if doctor:
        rows = face.get("rows") or []
        target = next(r for r in rows if r.get("class") == "opened_nowhere_in_the_file")
        target["class"] = "superseded_by_a_wider_open"
        target["basis"] = "exact_path"
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    try:
        results = run_leg(quiet=False)
    finally:
        if doctor:
            restored = json.loads(json.dumps(face))
            for r in restored.get("rows") or []:
                if r.get("class") == "superseded_by_a_wider_open" and not (r.get("hits") or []):
                    r["class"] = "opened_nowhere_in_the_file"
                    r["basis"] = None
            with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(restored, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    after = sha(FACE)
    passed = sum(1 for _, ok, _ in results if ok)
    print("%d/%d leg(s) pass" % (passed, len(results)))
    if doctor:
        print("doctor: expected FAIL; sha in %s sha out %s %s"
              % (before[:16], after[:16], "MATCH" if before == after else "MISMATCH"))
        return 0 if (passed < len(results) and before == after) else 1
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))