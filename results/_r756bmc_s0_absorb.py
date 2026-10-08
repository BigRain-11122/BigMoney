# -*- coding: utf-8 -*-
"""r756 bm-c S0 absorb: commit own daemon live faces (6 faces), match commit
message style. Probe showed ahead=0 behind=0 -> no rebase needed (C-01 pull
check: head d4e7b4a19 == origin/main, last pull verified same-round)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


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
                    "round 756 bm-c churn absorb: own daemon live faces x6 (idle/satengine/autofill/dispatcher state regen) [via bm-c r756]"])
print("commit rc=%d" % rc)
if rc != 0:
    print("commit err: %s" % err[:400])
rc, out, _ = git(["log", "-1", "--format=%h %s"])
print("head now: %s" % out.strip()[:80])
rc, out, _ = git(["status", "--porcelain"])
print("post-status dirty=%d" % len([ln for ln in out.splitlines() if ln.strip()]))
