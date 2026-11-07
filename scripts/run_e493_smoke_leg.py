"""Run the E493 smoke leg standalone (the full suite is ~20-30 min).

The leg text is extracted verbatim from ``smoke_test.py`` and executed under a minimal
``check()`` harness, so what is proven here is the shipped leg, not a paraphrase.

``--doctor`` proves the leg can go red: it flips one row's producer-shape flag so the
published payload no longer re-derives, runs the same leg text, and restores the face
byte-identically (sha in / sha out).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "state_tilt", "latestcopyowner_latest.json")
START = "# E493 -- who owns the bytes of the two faces"
END = 'if __name__ == "__main__":'


def run_leg(quiet=False):
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    tail = [i for i, ln in enumerate(lines) if ln.startswith(END)]
    end = min(i for i in tail if i > start)
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
    ns = {"__name__": "e493_leg"}
    exec(compile("\n".join(harness + body), "e493_leg", "exec"), ns)
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
            print("  FAIL ::", name, "|", detail[:200])
        return 0 if not bad else 1

    before = sha(FACE)
    original = open(FACE, "rb").read()
    data = json.loads(original.decode("utf-8"))
    data["rows"][0]["producer_arm"]["payload_re_derives_from_the_disk_copy"] = not data["rows"][0][
        "producer_arm"]["payload_re_derives_from_the_disk_copy"]
    text = json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        rows = run_leg(quiet=True)
    finally:
        with open(FACE, "wb") as fh:
            fh.write(original)
    after = sha(FACE)
    bad = [r for r in rows if not r[1]]
    print("doctored run: %d/%d failed (expected >=1); face sha restored: %s"
          % (len(bad), len(rows), before == after))
    for name, ok, detail in bad[:3]:
        print("  FAIL ::", name, "|", detail[:200])
    return 0 if bad and before == after else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))