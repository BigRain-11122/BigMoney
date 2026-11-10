"""Extract the E644 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e641_smoke_leg.py``: the leg text is pulled out of ``smoke_test.py``
and executed under a minimal ``check()`` harness, so the published leg is proven against the
published face rather than paraphrased into a second copy that can drift.

``--doctor`` proves the leg can go red: it flips a published row-key claim to one the site's keys do
not carry, runs the same leg text, and restores the face byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "onedepthwrite_latest.json")
START = "# E644 asks the mirror question of E639/E640/E641"
STOP = 'check(_name644, not _bad644, "; ".join(_bad644)[:240] or _d644)'


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
    env = {"__name__": "e644_leg"}
    exec(compile("\n".join(harness + body), "<e644-leg>", "exec"), env)
    return env["RESULTS"]


def doctor():
    raw = io.open(FACE, "rb").read()
    sha_in = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("utf-8"))
    keep = None
    flipped = False
    for fn in doc.get("functions") or []:
        for site in fn.get("depth1_sites") or []:
            keep = site.get("names_a_counted_row_key")
            site["names_a_counted_row_key"] = True
            flipped = True
            break
        if flipped:
            break
    payload = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    try:
        with io.open(FACE, "wb") as fh:
            fh.write(payload)
        red = run_leg(quiet=True)
    finally:
        with io.open(FACE, "wb") as fh:
            fh.write(raw)
    sha_out = hashlib.sha256(io.open(FACE, "rb").read()).hexdigest()
    back = json.loads(io.open(FACE, encoding="utf-8").read())
    restored_flag = None
    for fn in back.get("functions") or []:
        for site in fn.get("depth1_sites") or []:
            restored_flag = site.get("names_a_counted_row_key")
            break
        if restored_flag is not None:
            break
    restored = (sha_in == sha_out and restored_flag == keep)
    went_red = any(not ok for _, ok, _ in red)
    print("doctor: legs=%d red=%d restored=%s sha_in=%s sha_out=%s"
          % (len(red), sum(1 for _, ok, _ in red if not ok), restored, sha_in[:12], sha_out[:12]))
    return 0 if (went_red and restored) else 1


def main(argv):
    if "--doctor" in argv:
        return doctor()
    results = run_leg(quiet="--quiet" in argv)
    bad = [n for n, ok, _ in results if not ok]
    print("legs=%d fail=%d" % (len(results), len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))