"""Extract the E606 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e432_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it perturbs the published ``reader_pairs_that_compare``
tally, runs the same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "COUNTRYCOMPARE.json")
START = "# E606: where a published count disagrees"
STOP = "# E597: every published block that carries a bar count"


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(STOP))
    body = lines[start:end]
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
    ns = {"__name__": "e606_leg"}
    exec(compile("\n".join(harness + body), "e606_leg", "exec"), ns)
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
    face["counts"]["reader_pairs_that_compare"] = int(
        face["counts"]["reader_pairs_that_compare"]) + 1
    try:
        with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        rows = run_leg(quiet=True)
        bad = [r for r in rows if not r[1]]
        print("doctored run: %d/%d red" % (len(bad), len(rows)))
        for name, ok, detail in bad:
            print("  FAIL ::", name, "|", detail[:160])
    finally:
        with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(original)
    after = sha(FACE)
    print("face restored byte-identical:", before == after, before[:16], after[:16])
    return 0 if bad and before == after else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))