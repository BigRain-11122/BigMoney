"""Negative controls for astock_veto_year_source.py --check.

Each leg starts from the ORIGINAL bytes of the published face (legs must not inherit each
other's damage), writes one change, runs the real cmd_check(), and restores.  The point is
the split the family learned to require (r1934): a face that merely moved must say STALE,
a face whose numbers stopped adding up must fail without that word, and the verdict tokens
must flip back when the numbers do.
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import astock_veto_year_source as face  # noqa: E402

ORIG = os.path.join(ROOT, "results", "astock_veto_year_source.json")
BACKUP = ORIG + ".negbak"
LEGS = []


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def with_face(mutate):
    """Run cmd_check against a copy of the face with `mutate` applied, then restore."""
    with io.open(BACKUP, "rb") as fh:
        raw = fh.read()
    p = json.loads(raw.decode("utf-8"))
    mutate(p)
    with io.open(ORIG, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(p, ensure_ascii=False, indent=1))
    out = io.StringIO()
    old = sys.stdout
    sys.stdout = out
    try:
        rc = face.cmd_check()
    finally:
        sys.stdout = old
        with io.open(ORIG, "wb") as fh:
            fh.write(raw)
    return rc, out.getvalue()


def leg(name, ok, detail=""):
    LEGS.append((name, bool(ok), detail))


def main():
    shutil.copyfile(ORIG, BACKUP)
    base = sha(ORIG)
    try:
        def call():
            out = io.StringIO()
            old = sys.stdout
            sys.stdout = out
            try:
                rc = face.cmd_check()
            finally:
                sys.stdout = old
            return rc, out.getvalue()

        rc, text = call()
        leg("control: untouched face passes", rc == 0, text.strip()[:120])

        # 1. beta leg tampered -> identity breaks, and it must NOT be called STALE
        def m1(p):
            p["by_year"]["2026"]["beta_implied"]["B"] -= 0.05
        rc, text = with_face(m1)
        leg("tampered beta leg fails", rc == 3 and "identity" in text, text.strip()[:120])
        leg("tampered beta leg is not labelled STALE", "STALE" not in text)

        # 2. a series point moved -> the parent cross-check must catch it
        def m2(p):
            p["series"][10]["B"] += 0.02
        rc, text = with_face(m2)
        leg("moved series point fails (parent cross-check)", rc == 3 and "L1" in text, text.strip()[:120])

        # 3. panel frontier moved -> STALE, not a maths failure
        def m3(p):
            p["panel"]["last"] = "2026-11-19"
        rc, text = with_face(m3)
        leg("moved panel frontier is STALE", rc == 3 and "STALE" in text, text.strip()[:120])

        # 4. year verdict flipped -> must be caught by arithmetic
        def m4(p):
            p["attribution"]["verdict"] = "Y_NOT_BETA"
        rc, text = with_face(m4)
        leg("flipped year verdict fails", rc == 3 and "L8" in text, text.strip()[:120])

        # 5. sort verdict flipped
        def m5(p):
            p["verdict"]["sort"] = "SORT_DECAYING"
        rc, text = with_face(m5)
        leg("flipped sort verdict fails", rc == 3 and "L9" in text, text.strip()[:120])

        # 6. a period removed -> year periods drift from the parent
        def m6(p):
            drop = [i for i, r in enumerate(p["series"]) if r["date"][:4] == "2025"][-1]
            del p["series"][drop]
        rc, text = with_face(m6)
        leg("dropped period fails", rc == 3, text.strip()[:120])

        # 7. year total tampered without touching the series
        def m7(p):
            p["by_year"]["2024"]["year_total"]["A"] += 0.001
        rc, text = with_face(m7)
        leg("tampered year total fails", rc == 3 and "L3" in text, text.strip()[:120])

        # 8. beta log-share hand-edited
        def m8(p):
            p["attribution"]["beta_log_share"] = 0.5
        rc, text = with_face(m8)
        leg("hand-edited log-share fails", rc == 3 and "L7" in text, text.strip()[:120])
    finally:
        shutil.copyfile(BACKUP, ORIG)
        os.remove(BACKUP)

    after = sha(ORIG)
    leg("published face restored byte-for-byte (sha256)", after == base, "%s vs %s" % (after[:12], base[:12]))

    bad = [n for n, ok, _d in LEGS if not ok]
    for n, ok, d in LEGS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", n, ("  [" + d + "]") if not ok and d else ""))
    print("%d/%d legs PASS" % (len(LEGS) - len(bad), len(LEGS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
