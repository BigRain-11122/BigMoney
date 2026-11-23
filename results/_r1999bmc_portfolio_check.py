"""Negative controls for idx_fut_carry_portfolio.check().

A check that re-derives the face from in-memory numbers is self-consistent by construction
(r1850 / r1935): it can only ever say "yes".  The only way to know it would catch a real
defect is to poison the published file and watch it go red -- and to know it distinguishes
a *stale* input from a *wrong* number, because the S6 chain only pays to rebuild on the word
STALE (r1934).

Every mutation is applied to a copy, the real file is restored byte-for-byte, and the
restore is asserted by sha256 in finally.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE = os.path.join(ROOT, "results", "idx_fut_carry_portfolio.json")
SCRIPT = os.path.join(ROOT, "scripts", "idx_fut_carry_portfolio.py")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_check():
    p = subprocess.run([sys.executable, SCRIPT, "check"],
                       cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def mutate(fn, pristine):
    """Apply one mutation on top of the pristine bytes.

    Each leg must start from the untouched file: if leg 1 leaves the cutoff moved, leg 2
    inherits it and reports STALE alongside its own defect, which makes the legs lie about
    what they proved.
    """
    with open(FACE, "wb") as f:
        f.write(pristine)
    with open(FACE, encoding="utf-8") as f:
        doc = json.load(f)
    fn(doc)
    with open(FACE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def main():
    if not os.path.exists(FACE):
        print("HARNESS BLOCKED: published face missing, run it first")
        return 2
    orig = sha256(FACE)
    backup = os.path.join(tempfile.gettempdir(), "_r1999bmc_portfolio_backup.json")
    with open(FACE, "rb") as f:
        raw = f.read()
    with open(backup, "wb") as f:
        f.write(raw)

    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    try:
        # 0 baseline: the untouched file must pass
        rc, out = run_check()
        leg("clean face passes", rc == 0, "rc=%d" % rc)

        # 1 a moved cutoff is STALE
        mutate(lambda d: d.__setitem__("evidence_cutoff", "2026-11-19"), raw)
        rc, out = run_check()
        leg("moved cutoff -> rc3", rc == 3, "rc=%d" % rc)
        leg("moved cutoff says STALE", "STALE" in out, out.strip()[:120])

        # 2 a wrong return is a defect, not staleness
        def bad_ann(d):
            d["equal_weight_full"]["ann_pct"] = round(d["equal_weight_full"]["ann_pct"] + 1.5, 3)
        mutate(bad_ann, raw)
        rc, out = run_check()
        leg("wrong ann -> rc3", rc == 3, "rc=%d" % rc)
        leg("wrong ann is CHECK FAILED, not STALE", "STALE" not in out, out.strip()[:120])

        # 3 a flipped criterion must be caught (published claims a PASS the math denies)
        def flip(d):
            d["checks"]["P3_the_drawdown_actually_diversifies"] = False
        mutate(flip, raw)
        rc, out = run_check()
        leg("flipped criterion -> rc3", rc == 3, "rc=%d" % rc)
        leg("flipped criterion names the leg", "P3_the_drawdown" in out, out.strip()[:140])

        # 4 a corrupted correlation cell must be caught
        def bad_corr(d):
            m = d["correlation"]["matrix"]
            m[0][1] = round((m[0][1] or 0.0) + 0.12, 4)
            m[1][0] = m[0][1]
        mutate(bad_corr, raw)
        rc, out = run_check()
        leg("wrong correlation -> rc3", rc == 3, "rc=%d" % rc)

        # 5 a missing face is not "no problem"
        os.remove(FACE)
        rc, out = run_check()
        leg("missing face -> rc3", rc == 3, "rc=%d" % rc)
        leg("missing face says face missing", "face missing" in out, out.strip()[:120])
    finally:
        with open(FACE, "wb") as f:
            f.write(raw)

    after = sha256(FACE)
    leg("file restored byte-for-byte", after == orig, "%s vs %s" % (after[:16], orig[:16]))

    failed = [l for l in legs if not l[1]]
    for name, ok, detail in legs:
        print("  %-42s %s%s" % (name, "PASS" if ok else "FAIL",
                                "" if ok else "  <- " + detail))
    if failed:
        print("NEGATIVE CONTROLS FAILED: %d/%d" % (len(failed), len(legs)))
        return 1
    print("NEGATIVE CONTROLS OK: %d/%d legs pass." % (len(legs), len(legs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
