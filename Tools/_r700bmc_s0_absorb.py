"""r700 bm-c S0 absorb + pull: targeted add of own daemon live-faces
(r620/r832 laws) + this round's probe tool, commit, then pull --rebase.
Pattern credit: Tools/_r693bmc_s0_absorb.py."""
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r700bmc_commitmsg.txt")


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GIT FAIL rc=%d: %s" % (p.returncode, out[:500]))
        raise SystemExit(2)
    return p.returncode, out


targets = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/pool_red_flags.jsonl",
    "results/runnable_pool.bm-c.json",
    "results/runnable_pool.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "Tools/_r700bmc_s0.py",
]
live = [t for t in targets if os.path.exists(os.path.join(REPO, t))]
rc, out = git(["add", "--"] + live)
print("add rc=%d files=%d" % (rc, len(live)))

with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("lane: bm-c daemon churn absorb r700 (r620/r832 laws, judge-park window)\n")
rc, out = git(["commit", "-F", MSG])
print("commit rc=%d" % rc)
print(out[:300])

rc, out = git(["pull", "--rebase"], check=False)
if rc != 0:
    time.sleep(3)
    rc, out = git(["pull", "--rebase"], check=False)
    print("(retry2)")
print("pull rc=%d" % rc)
print(out[-600:])

rc, out = git(["status", "--porcelain"])
print("== dirty after:", out.strip() or "(clean)")
rc, out = git(["log", "--oneline", "-3"])
print(out)
