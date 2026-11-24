"""Negative control for `etf_book_cash_rate_flip --check` (r2067 bm-c).

The rule this exercises is the r1934/r1850 one: a check that only re-derives its own face
is green forever, and a check whose drift message does not say STALE never gets its writer
paid by the chain.  So the control moves one number the face publishes and asserts

  1. `--check` goes rc3 rather than quietly agreeing,
  2. the message names the disagreement (CHECK FAILED),
  3. the message does NOT contain the chain's rebuild word `STALE` -- this is a real
     disagreement, not a face that needs re-deriving, and putting that word in would make
     the chain pay ~50s to rebuild a face nobody disputed,
  4. restoring the bytes restores rc0 and the file is byte-identical to the backup.

Runs the real CLI twice (each build is one engine pass).  Restores in a `finally` so a
failed control cannot leave the published face poisoned.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "etf_book_cash_rate_flip.json")
SCRIPT = os.path.join(ROOT, "scripts", "etf_book_cash_rate_flip.py")


def sha(path):
    with io.open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_check():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([sys.executable, SCRIPT, "--check"], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    if not os.path.exists(FACE):
        print("[FAIL] face missing -- nothing to control")
        return 1
    backup = os.path.join(tempfile.gettempdir(), "flip_face_backup.json")
    shutil.copyfile(FACE, backup)
    before = sha(FACE)
    legs = []
    try:
        with io.open(FACE, encoding="utf-8") as f:
            face = json.load(f)
        original = face["facts"]["flip_rate_c2_pct"]
        face["facts"]["flip_rate_c2_pct"] = round(float(original) + 0.01, 4)
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")

        rc_bad, out_bad = run_check()
        legs.append(("a moved number makes --check fail", rc_bad == 3, "rc=%d" % rc_bad))
        legs.append(("the failure names itself", "CHECK FAILED" in out_bad, out_bad[-160:]))
        legs.append(("the failure is not stamped STALE",
                     "STALE" not in out_bad, out_bad[-160:]))
        legs.append(("it names what moved",
                     "facts differs" in out_bad or "verdict differs" in out_bad
                     or "gates differs" in out_bad, out_bad[-160:]))
    finally:
        shutil.copyfile(backup, FACE)

    after = sha(FACE)
    legs.append(("restore is byte-identical", after == before, "%s != %s" % (after, before)))

    rc_ok, out_ok = run_check()
    legs.append(("restored face checks clean", rc_ok == 0, "rc=%d %s" % (rc_ok, out_ok[-160:])))
    legs.append(("clean run does not print CHECK FAILED", "CHECK FAILED" not in out_ok,
                 out_ok[-160:]))

    bad = [l for l in legs if not l[1]]
    for name, ok, why in legs:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", name, "" if ok else " | " + why))
    print("%d/%d control legs pass" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
