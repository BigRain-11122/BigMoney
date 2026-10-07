"""r702 bm-c S0f: r696 beat-window atomic absorb+pull (single-process
add+commit+rebase back-to-back, <2s window vs ~58s daemon beat)."""
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/saturation_engine/queue_bm-c.json",
]
facts = {"tries": []}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def face_beat_age():
    ages = {}
    now = time.time()
    for f in FACES:
        p = os.path.join(REPO, f.replace("/", os.sep))
        if os.path.exists(p):
            ages[f] = round(now - os.path.getmtime(p), 1)
    return ages


for tryno in range(1, 6):
    ages = face_beat_age()
    print("== try %d face beat ages: %s" % (tryno, ages))
    newest = min(ages.values()) if ages else 999
    if newest < 4.0:
        # a write just landed; wait out the residual beat then race
        time.sleep(6.0)
        continue
    t0 = time.time()
    git(["add", "-A"])
    rc1, o1, e1 = git(["commit", "-m", "lane: bm-c r702 tail churn absorb pre-rebase (daemon tick faces, r696 race law)"])
    if rc1 != 0:
        # nothing to commit is fine if daemon beat landed between add and commit
        rec = {"try": tryno, "commit_rc": rc1, "note": (o1 + e1).strip()[:120]}
        facts["tries"].append(rec)
        print("  commit rc=%d %s" % (rc1, rec["note"]))
        time.sleep(2)
        continue
    rc2, o2, e2 = git(["pull", "--rebase"])
    dt = time.time() - t0
    rec = {"try": tryno, "commit_rc": rc1, "pull_rc": rc2, "dt_s": round(dt, 1),
           "pull_out": (o2 + e2).strip()[-500:]}
    facts["tries"].append(rec)
    print("  commit ok + pull rc=%d in %.1fs" % (rc2, dt))
    print("  pull:", rec["pull_out"][-300:])
    if rc2 == 0:
        break
    if "unstaged" in (o2 + e2):
        time.sleep(2)
        continue
    # real conflict surface - stop and report
    break

rc, out, err = git(["status", "--porcelain"])
facts["porcelain"] = out.strip().splitlines() if out.strip() else []
print("== porcelain after:")
print(out)
rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind"] = int(out.strip() or 0)
print("== behind:", facts["behind"])
rc, out, err = git(["log", "--oneline", "-6"])
print(out)

with open(os.path.join(REPO, "results", "_r702bmc_s0f_facts.json"), "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts saved")
