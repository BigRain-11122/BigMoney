"""r693 bm-c S0 absorb + pull: targeted add of own daemon satengine
live-faces (r620 law) + this round's probe tools, commit, then
pull --rebase (zero-window python subprocess git, established r69x
pattern). Facts -> stdout."""
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r693bmc_commitmsg.txt")


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GIT FAIL rc=%d: %s" % (p.returncode, out[:500]))
        raise SystemExit(2)
    return p.returncode, out


targets = [
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "Tools/_r693bmc_s0.py",
    "Tools/_r693bmc_adv_probe.py",
    "Tools/_r693bmc_adv_probe2.py",
]
for t in targets:
    if not os.path.exists(os.path.join(REPO, t)):
        print("MISSING target (skip):", t)
rc, out = git(["add", "--"] + [t for t in targets if os.path.exists(os.path.join(REPO, t))])
print("add rc=%d" % rc)

with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("round 693 bm-c S0: absorb own daemon satengine live-faces (r620 law) + r693 s0/adv probe tools\n")
rc, out = git(["commit", "-F", MSG])
print("commit rc=%d" % rc)
print(out[:400])

rc, out = git(["pull", "--rebase"], check=False)
print("pull rc=%d" % rc)
print(out[:600])
