"""r702 bm-c S0b: churn-absorb own daemon runtime faces (r696 race law),
then pull --rebase (single atomic retry). Conflict handling per canon:
regenerable faces -> --theirs + atomic continue (r701 law)."""
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


FACES = [
    "results/_orphan_face_probe.json",
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "Tools/_r702bmc_s0.py",
    "results/_r702bmc_s0_facts.json",
]
rc, out, err = git(["add"] + FACES)
print("== add rc=%d" % rc, (out + err).strip()[:200])
rc, out, err = git(["commit", "-m", "lane: bm-c r702 churn absorb (daemon tick faces, r696 race law)"])
facts["absorb_rc"] = rc
print("== absorb commit rc=%d" % rc, (out + err).strip()[:200])

rc, out, err = git(["pull", "--rebase"])
attempt = 1
if rc != 0:
    time.sleep(2)
    rc, out, err = git(["pull", "--rebase"])
    attempt = 2
facts["pull_rc"] = rc
facts["pull_attempt"] = attempt
facts["pull_out"] = (out + err).strip()[-800:]
print("== pull rc=%d attempt=%d" % (rc, attempt))
print(facts["pull_out"][-500:])

if rc != 0:
    # conflict surface probe
    rc, out, err = git(["status", "--porcelain"])
    print("== conflicted/porcelain:")
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

with open(os.path.join(REPO, "results", "_r702bmc_s0b_facts.json"), "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts saved")
