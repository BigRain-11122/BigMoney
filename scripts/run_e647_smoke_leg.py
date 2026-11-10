"""Extract the E647 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e643_smoke_leg.py``: the leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it swaps the published verdict for one the counts do not
force, runs the same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "stringreach_latest.json")
START = "# E647 prices the string arm E646 published as a limit"
STOP = 'check(_name647, not _bad647, "; ".join(_bad647)[:240] or _d647)'


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
    env = {"__name__": "e647_leg"}
    exec(compile("\n".join(harness + body), "<e647-leg>", "exec"), env)
    return env["RESULTS"]


def doctor():
    raw = io.open(FACE, "rb").read()
    sha_in = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("utf-8"))
    keep = doc.get("verdict")
    doc["verdict"] = (
        "at least one hit module reaches a counted read module through a string that import "
        "machinery consumes, so the collision has a non-import route to a module object")
    payload = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    try:
        with io.open(FACE, "wb") as fh:
            fh.write(payload)
        red = run_leg(quiet=True)
    finally:
        with io.open(FACE, "wb") as fh:
            fh.write(raw)
    restored = hashlib.sha256(io.open(FACE, "rb").read()).hexdigest()
    return sha_in, restored, red, keep


def main(argv):
    if "--doctor" in argv:
        sha_in, restored, red, keep = doctor()
        bad = [name for name, ok, _ in red if not ok]
        print("doctor: sha_in=%s sha_out=%s restored=%s red_legs=%d %s"
              % (sha_in[:12], restored[:12], sha_in == restored, len(bad), bad))
        return 0 if (sha_in == restored and bad) else 1
    results = run_leg(quiet=True)
    failed = [r for r in results
              if not r[1] and "could not be read" not in (r[2] or "")]
    for name, ok, detail in results:
        print(("PASS" if ok else "FAIL") + " :: " + name, "" if ok else detail)
    print("leg: %d/%d checks green" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))