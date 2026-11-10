"""Extract the E645 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e648_smoke_leg.py``: the leg text is pulled out of ``smoke_test.py``
and executed under a minimal ``check()`` harness, so the published leg is proven against the
published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it rewrites one count to a value its own rows contradict,
runs the same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "computedreach_latest.json")
START = "# E645 asks what E644's own limits left open"
STOP = 'check(_name645, not _bad645, "; ".join(_bad645)[:240] or _d645)'


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
    ns = {}
    exec(compile("\n".join(harness + body), "<e645-leg>", "exec"), ns)
    return ns["RESULTS"]


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def doctor():
    before = _sha(FACE)
    doc = json.load(io.open(FACE, encoding="utf-8"))
    saved = json.loads(json.dumps(doc))
    doc["counts"]["sites_reaching_a_counted_row_key"] = 1
    with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    try:
        results = run_leg(quiet=True)
        bad = [name for name, ok, _ in results if not ok]
    finally:
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(saved, ensure_ascii=False, indent=1) + "\n")
    after = _sha(FACE)
    print("doctor: leg bad=%d %s" % (len(bad), bad[:1]))
    print("doctor: sha in=%s out=%s same=%s" % (before[:12], after[:12], before == after))
    return 0 if bad and before == after else 1


def main(argv):
    if "--doctor" in argv:
        return doctor()
    results = run_leg()
    bad = [name for name, ok, _ in results if not ok]
    for name, ok, detail in results:
        print(("PASS" if ok else "FAIL") + " :: " + name + ("" if ok else " :: " + detail))
    print("legcheck: %d/%d green" % (len(results) - len(bad), len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
