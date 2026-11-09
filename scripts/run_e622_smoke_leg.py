"""Extract the E622 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e619_smoke_leg.py``: the leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it swaps the published verdict for a claim the holder
rows do not force, runs the same leg text, and restores the face byte-identically (sha in / sha
out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "deadlocalreach_latest.json")
START = "# E622: E619 closed over the dead reader lines themselves"
STOP = 'check(_name622, not _bad622, "; ".join(_bad622)[:240] or _d622)'


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(STOP))
    body = lines[start:end + 1]
    harness = [
        "import importlib, json, os, sys",
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
    ns = {"__name__": "e622_leg"}
    exec(compile("\n".join(harness + body), "e622_leg", "exec"), ns)
    return ns["RESULTS"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    if "--doctor" not in argv:
        rows = run_leg()
        bad = [r for r in rows if not r[1]]
        print("%d/%d legs passed" % (len(rows) - len(bad), len(rows)))
        return 0 if not bad else 1
    before = sha(FACE)
    original = io.open(FACE, encoding="utf-8").read()
    face = json.loads(original)
    if not face.get("verdict"):
        print("no verdict to perturb -- the doctor cannot go red here")
        return 2
    face["verdict"] = "no_function_holds_a_dead_reader_line"
    if face["verdict"] == json.loads(original).get("verdict"):
        face["verdict"] = "other"
    io.open(FACE, "w", encoding="utf-8", newline="\n").write(
        json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False) + "\n")
    try:
        out = run_leg(quiet=True)
    finally:
        io.open(FACE, "w", encoding="utf-8", newline="\n").write(original)
    after = sha(FACE)
    red = [r for r in out if not r[1]]
    print("doctor: %d/%d legs red with the verdict flipped" % (len(red), len(out)))
    print("face restored byte-identically: %s" % (before == after))
    return 0 if red and before == after else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))