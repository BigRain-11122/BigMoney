"""Extract the E649 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e651_smoke_leg.py``: the leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it swaps a count for one the rows do not add up to, runs the
same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "guardedwrite_latest.json")
START = "# E649 prices the population E643 published as two independent columns"
STOP = 'check(_name649, not _bad649, "; ".join(_bad649)[:240] or _d649)'


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
    env = {"__name__": "e649_leg"}
    exec(compile("\n".join(harness + body), "<e649-leg>", "exec"), env)
    return env["RESULTS"]


def doctor():
    raw = io.open(FACE, "rb").read()
    sha_in = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("utf-8"))
    keep = doc.get("verdict")
    doc["verdict"] = (
        "every residual module-level write site sits directly in the module body at guard depth "
        "zero and therefore runs at import")
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
    for name, ok, detail in results:
        print(("PASS" if ok else "FAIL") + " :: " + name, "" if ok else detail)
    failed = [r for r in results if not r[1]]
    print("leg: %d/%d checks green" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))