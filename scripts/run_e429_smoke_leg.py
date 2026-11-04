"""Extract the E429 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e417_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it perturbs one derived tally in the published face, runs
the same leg text, and restores the face byte-identically (sha in / sha out are printed and must
match).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "twohop_latest.json")
START = "# E429 (r1445 bm-b)"
END = 'if __name__ == "__main__":'


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    # r1447 bm-b: the slice used to run to the end of the file, so this runner also
    # executed every leg appended after it (the r1446 E423 leg made a 2-second check
    # take ~16 minutes and reported "1/2 legs passed" under one card's name).
    end = next((i for i, ln in enumerate(lines[start + 1:], start + 1)
                if ln.startswith("# E")), None) or next(
        i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
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
    ns = {"__name__": "e420_leg"}
    exec(compile("\n".join(harness + body), "e420_leg", "exec"), ns)
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
    face["summary"]["rows_that_became_writers"] = \
        int(face["summary"].get("rows_that_became_writers") or 0) + 1
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