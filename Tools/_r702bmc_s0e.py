"""r702 bm-c S0e: pull --rebase on clean tree, conflict probe if any."""
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rc, out, err = git(["pull", "--rebase"])
if rc != 0:
    time.sleep(3)
    rc, out, err = git(["pull", "--rebase"])
facts["pull_rc"] = rc
facts["pull_out"] = (out + err).strip()[-1200:]
print("== pull rc=%d" % rc)
print(facts["pull_out"][-800:])

if rc != 0:
    rc, out, err = git(["status", "--porcelain"])
    print("== porcelain (conflict face probe):")
    print(out)
    rc, out, err = git(["ls-files", "-u"])
    facts["uu"] = out.strip().splitlines() if out.strip() else []
    print("== ls-files -u count=%d" % len(facts["uu"]))
    for ln in facts["uu"]:
        print("  U:", ln)
    rc, out, err = git(["log", "--oneline", "-3", "origin/main"])
    print("== origin tip:")
    print(out)

rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind_post"] = int(out.strip() or 0)
rc2, out2, _ = git(["status", "--porcelain"])
facts["dirty_post"] = out2.strip().splitlines() if out2.strip() else []
print("== behind_post:", facts["behind_post"], "dirty_post:", len(facts["dirty_post"]))
for ln in facts["dirty_post"]:
    print("  DP:", ln)
rc, out, err = git(["log", "--oneline", "-8"])
print("== log after:")
print(out)

with open(os.path.join(REPO, "results", "_r702bmc_s0e_facts.json"), "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts saved")
