"""Extract the E496 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e483_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is
proven against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it moves the write-only twin's reads-only residue to a
leg class, runs the same leg text, and restores the face byte-identically (sha in / sha out are
printed and must match).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "twinmode_latest.json")
START = "# E496 -- does E479's residue class survive"
END = "if __name__ == "


def leg_body():
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    except StopIteration:
        raise SystemExit("the E496 leg is not in smoke_test.py")
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
    return lines[start:end]


HARNESS = [
    "import json, os, sys",
    "RESULTS = []",
    "def check(name, ok, detail=''):",
    "    RESULTS.append((name, bool(ok), detail))",
    "    print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
    "",
]


def run(tag="e496_leg", quiet=False):
    os.chdir(ROOT)
    for path in (os.path.join(ROOT, "scripts"), ROOT):
        if path not in sys.path:
            sys.path.insert(0, path)
    body = "\n".join(HARNESS + leg_body())
    ns = {"__name__": tag}
    exec(compile(body, tag, "exec"), ns)
    results = ns["RESULTS"]
    bad = [r for r in results if not r[1]]
    if not quiet:
        print("%d/%d legs passed" % (len(results) - len(bad), len(results)))
    return results


def sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def doctor():
    original = io.open(FACE, "rb").read()
    before = sha16(FACE)
    face = json.loads(original.decode("utf-8"))
    rows = face.get("rows") or []
    moved = None
    for row in rows:
        if row.get("twin") == "results/market_clock/CALL_latest.json":
            row["read_only_residue"] = "opened_only_by_a_smoke_or_runner_leg"
            moved = row.get("twin_basename")
            break
    if moved is None:
        raise SystemExit("the write-only twin is not on the face: nothing to doctor")
    try:
        with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1))
        results = run(tag="e496_doctor", quiet=True)
    finally:
        with open(FACE, "wb") as fh:
            fh.write(original)
    after = sha16(FACE)
    red = [r for r in results if not r[1]]
    print("doctor moved %s off the residue its sites imply: %d/%d legs red"
          % (moved, len(red), len(results)))
    print("face restored: sha %s -> %s (%s)"
          % (before, after, "identical" if before == after else "CHANGED"))
    if before != after:
        raise SystemExit(2)
    return 0 if red else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--doctor" in argv:
        return doctor()
    results = run()
    return 0 if not [r for r in results if not r[1]] else 1


if __name__ == "__main__":
    sys.exit(main())