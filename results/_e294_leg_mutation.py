"""Prove the E294 smoke leg can fail: mutate the published face, run the leg, restore the bytes."""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "state_tilt", "bandfrozen_latest.json")


def run_leg():
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "results", "_e294_leg_run.py")],
                          capture_output=True, text=True, cwd=ROOT)
    return proc.returncode, (proc.stdout or "").strip().splitlines()[-1:]


def mutate(mutator, label):
    stored = io.open(FACE, "rb").read()
    try:
        face = json.loads(stored.decode("utf-8"))
        mutator(face)
        with io.open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1))
        rc, tail = run_leg()
        print("%-46s rc=%d %s" % (label, rc, tail))
        return rc != 0
    finally:
        with io.open(FACE, "wb") as fh:
            fh.write(stored)


def flip_a_row(face):
    for row in face.get("rows") or []:
        if row.get("status") == "reproduces_and_stable":
            row["live_verdict"] = "a_verdict_nobody_measured"
            return


def self_include(face):
    face.setdefault("rows", []).append({"script": "e294_live_universe_drift.py",
                                        "status": "not_measurable", "reason": "x"})


def inflate_shape(face):
    face["directory_shape"]["census_the_directory"] = 99


def drop_a_count(face):
    face["summary"]["status_counts"] = {"reproduces_and_stable": 1}


def main():
    base_rc, base_tail = run_leg()
    print("%-46s rc=%d %s" % ("baseline", base_rc, base_tail))
    caught = [mutate(flip_a_row, "mutation: a stable row's live verdict changed"),
              mutate(self_include, "mutation: the census lists itself"),
              mutate(inflate_shape, "mutation: the family shape inflated"),
              mutate(drop_a_count, "mutation: the status counts lose a row")]
    print("caught %d/4" % sum(caught))
    return 0 if base_rc == 0 and all(caught) else 1


if __name__ == "__main__":
    sys.exit(main())