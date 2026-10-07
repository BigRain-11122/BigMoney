"""r702 bm-c S0d: debug absorb failure - step-by-step add/commit with full output."""
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rc, out, err = git(["status", "--porcelain"])
print("== porcelain rc=%d" % rc)
print(out)

rc, out, err = git(["add", "-A"])
print("== add -A rc=%d" % rc)
print("OUT:", out[:500])
print("ERR:", err[:500])

rc, out, err = git(["diff", "--cached", "--stat"])
print("== cached stat rc=%d" % rc)
print(out[:500])

rc, out, err = git(["commit", "-m", "lane: bm-c r702 churn absorb w2 (daemon tick faces, r696 race law)"])
print("== commit rc=%d" % rc)
print("OUT:", out[:800])
print("ERR:", err[:800])
