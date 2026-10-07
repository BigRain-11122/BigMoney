"""r702 bm-c S0c: second churn absorb (daemon live-write race) + pull --rebase
retry loop (max 3 attempts). Pattern credit: r701 two-commit absorb law."""
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {"attempts": []}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


for attempt in range(1, 4):
    rc, out, err = git(["status", "--porcelain"])
    dirty = out.strip().splitlines() if out.strip() else []
    if dirty:
        faces = [ln[3:].strip() for ln in dirty]
        git(["add"] + faces)
        rc2, out2, err2 = git(["commit", "-m", "lane: bm-c r702 churn absorb w%d (daemon tick faces, r696 race law)" % attempt])
        print("== absorb w%d commit rc=%d" % (attempt, rc2), (out2 + err2).strip()[:120])
    rc, out, err = git(["pull", "--rebase"])
    rec = {"attempt": attempt, "pull_rc": rc, "pull_out": (out + err).strip()[-300:]}
    facts["attempts"].append(rec)
    print("== pull attempt %d rc=%d" % (attempt, rc))
    print(rec["pull_out"][-250:])
    if rc == 0:
        break
    time.sleep(2)

rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind_post"] = int(out.strip() or 0)
rc2, out2, _ = git(["status", "--porcelain"])
facts["dirty_post"] = out2.strip().splitlines() if out2.strip() else []
print("== behind_post:", facts["behind_post"], "dirty_post:", len(facts["dirty_post"]))
for ln in facts["dirty_post"]:
    print("  DP:", ln)
rc, out, err = git(["log", "--oneline", "-6"])
print("== log after:")
print(out)

with open(os.path.join(REPO, "results", "_r702bmc_s0c_facts.json"), "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts saved")
