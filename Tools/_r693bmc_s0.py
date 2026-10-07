"""r693 bm-c S0 probe: round-start dirty face, recent commits, fleet
heartbeat freshness (bm-a/bm-b stall watch per r692 next-pointer (c)),
satengine daemon live-face mtimes. Facts -> stdout (small). Pattern
credit: Tools/_r692bmc_close.py + r691/r692 S0 sequence."""
import datetime
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now()


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


print("== now:", NOW.isoformat())
rc, out, err = git(["status", "--porcelain"])
print("== status rc=%d" % rc)
print(out if out else "(clean)")
if err:
    print("ERR:", err[:300])

rc, out, err = git(["log", "--oneline", "-5"])
print("== log rc=%d" % rc)
print(out)

for mid in ("bm-a", "bm-b"):
    p = os.path.join(REPO, "fleet", "machines", "%s.json" % mid)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            hb = json.load(fh)
        ts = hb.get("clock_read") or hb.get("ts") or hb.get("last_seen")
        ep = hb.get("heartbeat_epoch_utc")
        age_min = None
        if isinstance(ep, int):
            age_min = round((datetime.datetime.now().timestamp() - ep) / 60.0, 1)
        print("== hb %s: clock_read=%s epoch_age_min=%s round=%s" % (mid, ts, age_min, hb.get("round_no_label")))
    except Exception as exc:
        print("== hb %s: READ FAIL %s" % (mid, exc))

# satengine daemon live faces (own) -- what dirtied the tree in r692
for cand in ("results/satengine", "results"):
    d = os.path.join(REPO, cand)
    if not os.path.isdir(d):
        continue
    hits = []
    for f in sorted(os.listdir(d)):
        if "satengine" in f.lower() or "sate" in f.lower():
            fp = os.path.join(d, f)
            try:
                m = os.path.getmtime(fp)
                hits.append((f, datetime.datetime.fromtimestamp(m).isoformat(), os.path.getsize(fp)))
            except OSError:
                pass
    for h in hits:
        print("== sateface:", h)
    if hits:
        break
