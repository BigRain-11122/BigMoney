"""Extract the E522 smoke leg verbatim and run it standalone (the full suite is ~20-30 min).

Same workaround as ``scripts/run_e515_smoke_leg.py`` / ``run_e518_smoke_leg.py``: the exact leg
text is pulled out of ``smoke_test.py`` and executed under a minimal ``check()`` harness, so the
leg is proven against the published face instead of paraphrased into a second copy that can
drift.  ``--doctor`` proves the leg can go red: it relabels one unguarded arm as guarded, runs
the same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "silentarmread_latest.json")
START = "# E522:"
END = 'if __name__ == "__main__":'


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = min(i for i, ln in enumerate(lines) if ln.startswith(END) and i > start)
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
    ns = {"__name__": "e522_leg"}
    exec(compile("\n".join(harness + body), "e522_leg", "exec"), ns)
    return ns["RESULTS"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def doctor(quiet=False):
    """Refuse a face whose one arm's verdict contradicts its own site counts."""
    before = sha(FACE)
    original = open(FACE, "rb").read()
    data = json.loads(original.decode("utf-8"))
    flipped = False
    for row in data.get("arms") or []:
        if row.get("verdict") != "every_production_caller_tests_the_result_before_reading_it":
            row["verdict"] = "every_production_caller_tests_the_result_before_reading_it"
            flipped = True
            break
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    try:
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        rows = run_leg(quiet=True)
        bad = [r for r in rows if not r[1]]
        print("doctored run: %d/%d legs failed (expected >=1)" % (len(bad), len(rows)))
        # a doctor that cannot find an arm to flip must not report success
        ok = bool(bad) and flipped
    finally:
        with open(FACE, "wb") as fh:
            fh.write(original)
    after = sha(FACE)
    print("face restored: %s (sha %s -> %s)" % (before == after, before[:12], after[:12]))
    return 0 if (ok and before == after) else 1


def main(argv):
    if "--doctor" not in argv:
        rows = run_leg()
        bad = [r for r in rows if not r[1]]
        print("%d/%d legs passed" % (len(rows) - len(bad), len(rows)))
        for name, ok, detail in bad:
            print("  FAIL ::", name, "|", detail[:200])
        return 0 if not bad else 1
    return doctor()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))