"""r700 bm-c S0: round-start status, dirty-face scan, recent log, pull --rebase
(atomic retry once on daemon-race per r832 law), behind-count. Pattern credit:
Tools/_r693bmc_s0.py + r699 S0 sequence."""
import datetime
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now()
facts = {"now": NOW.isoformat()}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rc, out, err = git(["status", "--porcelain"])
facts["dirty"] = out.strip().splitlines() if out.strip() else []
print("== status rc=%d dirty=%d" % (rc, len(facts["dirty"])))
for ln in facts["dirty"]:
    print("  D:", ln)

rc, out, err = git(["log", "--oneline", "-5"])
print("== log rc=%d" % rc)
print(out)

# pre-pull behind count
git(["fetch", "origin"])
rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind_pre"] = int(out.strip() or 0)
print("== behind_pre:", facts["behind_pre"])

# pull --rebase with single atomic retry on transient daemon-write race
rc, out, err = git(["pull", "--rebase"])
attempt = 1
if rc != 0:
    time.sleep(2)
    rc, out, err = git(["pull", "--rebase"])
    attempt = 2
facts["pull_rc"] = rc
facts["pull_attempt"] = attempt
facts["pull_out"] = (out + err).strip()[-600:]
print("== pull rc=%d attempt=%d" % (rc, attempt))
print(facts["pull_out"][-400:])

rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind_post"] = int(out.strip() or 0)
rc2, out2, _ = git(["status", "--porcelain"])
facts["dirty_post"] = out2.strip().splitlines() if out2.strip() else []
print("== behind_post:", facts["behind_post"], "dirty_post:", len(facts["dirty_post"]))
for ln in facts["dirty_post"]:
    print("  DP:", ln)

# fleet heartbeat freshness
for mid in ("bm-a", "bm-b"):
    p = os.path.join(REPO, "fleet", "machines", "%s.json" % mid)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            hb = json.load(fh)
        ep = hb.get("heartbeat_epoch_utc")
        age_min = round((time.time() - ep) / 60.0, 1) if isinstance(ep, int) else None
        print("== hb %s: clock=%s age_min=%s round=%s" % (mid, hb.get("clock_read"), age_min, hb.get("round_no_label")))
    except Exception as exc:
        print("== hb %s: READ FAIL %s" % (mid, exc))

out_path = os.path.join(REPO, "results", "_r700bmc_s0_facts.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts ->", out_path)
