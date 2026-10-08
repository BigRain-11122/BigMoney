# -*- coding: utf-8 -*-
"""r754 bm-c S0 absorb: commit own daemon live faces (6 faces), match commit
message style. No rebase needed (probe showed ahead=0 behind=0)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


# show recent commit subject style for absorb message matching
rc, out, _ = git(["log", "-6", "--format=%h %s"])
print("recent subjects:")
print(out)

FACES = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
rc, out, err = git(["add", "--"] + FACES)
print("add rc=%d %s" % (rc, err.strip()[:200]))
rc, out, err = git(["diff", "--cached", "--stat"])
print("staged stat:\n%s" % out)
rc, out, err = git(["commit", "-m",
                    "round 754 bm-c churn absorb: own daemon live faces x6 (idle/satengine/autofill/dispatcher state regen) [via bm-c r754]"])
print("commit rc=%d" % rc)
if rc != 0:
    print("commit err: %s" % err[:400])
rc, out, _ = git(["log", "-1", "--format=%h %s"])
print("head now: %s" % out.strip())
rc, out, _ = git(["status", "--porcelain"])
print("post-status:\n%s" % out)
