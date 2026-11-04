"""Smoke leg for E408 -- the published refresh-surface census must re-derive.

The leg does three things and refuses rather than repairing:
  1. `verify` must exit clean: every published count and writer role re-derives
     from the live tree (a stale face re-reds every run -- E387's subject).
  2. the verdict must follow from the published counts alone.
  3. the headline claim must still hold: no face is refreshed on the surface that
     reads it, and the seed population's mention-only members are still named.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "state_tilt", "refreshsignal_latest.json")
SCRIPT = os.path.join(ROOT, "scripts", "e408_writer_refresh_signal.py")


def main():
    problems = []
    if not os.path.exists(FACE):
        print("FAIL: no published face at %s" % FACE)
        return 1
    face = json.load(open(FACE, encoding="utf-8"))

    r = subprocess.run([sys.executable, SCRIPT, "verify"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=900)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        problems.append("verify rc=%d: %s" % (r.returncode, out.strip()[:400]))
    else:
        try:
            payload = json.loads(out.strip().splitlines()[-1])
            if payload.get("problems"):
                problems.append("verify reported %d problems" % len(payload["problems"]))
        except Exception as e:
            problems.append("verify output unreadable: %s" % e)

    s = face.get("summary") or {}
    if s.get("faces_refreshed_on_the_reading_surface") != 0:
        problems.append("a face is now refreshed on its reading surface -- the claim "
                        "must be re-read, not silently kept")
    if s.get("faces") != len(face.get("faces") or []):
        problems.append("summary.faces does not match the published rows")
    if not s.get("writers_mention_only"):
        problems.append("the seed population no longer contains a mention-only member, "
                        "so the correction clause is stale")
    if "no_face_in_this_set_is_refreshed" not in (face.get("verdict") or ""):
        problems.append("verdict does not carry the headline")

    one_off = [w for r_ in face.get("faces") or [] for w in r_["writers"]
               if w.get("role") == "one_off"]
    if not one_off:
        problems.append("no one-off writer is published; the t35 row should carry five")

    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    print("PASS: E408 face re-derives (verify clean, %d rows, %d seed-named / %d write / "
          "%d mention-only, 0 refreshed on the reading surface)"
          % (s["faces"], s["writers_named_by_the_seed"], s["writers_that_actually_write"],
             s["writers_mention_only"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())