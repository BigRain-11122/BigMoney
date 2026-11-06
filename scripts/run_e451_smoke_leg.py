"""Extract the E451 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e447_smoke_leg.py`` and ``scripts/run_e452_smoke_leg.py``: the
exact leg text is pulled out of ``smoke_test.py`` and executed under a minimal ``check()`` harness,
so the published leg is proven against the published face rather than paraphrased into a second
copy that can drift.

``--doctor`` proves the leg can go red: it promotes one row's class in the published face, runs the
same leg text, and restores the face byte-identically (sha in / sha out are printed and must match).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "prereghash_latest.json")
START = "# E451 (r1477 bm-b)"
END = 'if __name__ == "__main__":'


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
    ns = {"__name__": "e451_leg"}
    exec(compile("\n".join(harness + body), "e451_leg", "exec"), ns)
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
        for name, ok, detail in bad:
            print("  FAIL ::", name, "|", detail[:300])
        return 0 if not bad else 1
    print("doctor: promoting one row's class, expecting the leg to fail")
    before = sha(FACE)
    raw = io.open(FACE, encoding="utf-8", newline="").read()
    face = json.loads(raw)
    row = next(r for r in face["rows"] if r["class"] == "note_named_but_no_digest")
    row["class"] = "note_digest_published"
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    open(FACE, "w", encoding="utf-8", newline="\n").write(body)
    rows = []
    try:
        rows = run_leg(quiet=True)
        bad = [r for r in rows if not r[1]]
        print("doctor: %d/%d red" % (len(bad), len(rows)))
        for name, ok, detail in bad:
            print("  RED ::", name, "|", detail[:200])
    finally:
        open(FACE, "w", encoding="utf-8", newline="").write(raw)
    after = sha(FACE)
    print("sha in  =", before)
    print("sha out =", after)
    print("restored byte-identical:", before == after)
    return 0 if (before == after and any(not r[1] for r in rows)) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))