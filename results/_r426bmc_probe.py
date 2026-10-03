# -*- coding: utf-8 -*-
"""_r426bmc_probe.py -- r426 fact probe (read-only, stdout only).

Checks: (1) orders dir vs heartbeat orders_ack diff (zero-unacked law, no ts filter);
(2) MASS-TRIAL-W2-JUDGE 4-shard pool two-layer state; (3) local shard product row
counts + origin presence; (4) live mass-trial processes (double-burn guard r616
family; self-match excluded by pattern on runner script path only); (5) judge state
summary; (6) WM red/lane + bandit next_pick; (7) r425 finalize log face.
"""
import json
import os
import subprocess
import datetime

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
CREATE_NO_WINDOW = 0x08000000


def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# 1) orders diff (mechanical, no timestamp filtering)
ack = set(json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))["orders_ack"])
dirfiles = set(f for f in os.listdir("fleet/orders") if f.endswith(".md"))
print("ORDERS: dir=%d ack=%d unacked=%s missing_from_dir=%s"
      % (len(dirfiles), len(ack), sorted(dirfiles - ack), sorted(ack - dirfiles)))

# 2) pool 4-shard two-layer state
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
ents = pool["entries"] if isinstance(pool, dict) else pool
for i in range(4):
    e = next(x for x in ents if x.get("id") == "MASS-TRIAL-W2-JUDGE-SHARD-%d" % i)
    s = e["shards"][0]
    print("SHARD-%d: entry=%s shard=%s owner=%s done_at=%s finished_at=%s"
          % (i, e.get("status"), s.get("status"), s.get("owner"),
             s.get("done_at"), s.get("finished_at")))

# 3) shard product rows local + origin
tot = 0
for i in range(4):
    p = "results/mass_trial/w2_judge_shard_%dof4.jsonl" % i
    n = 0
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            n = sum(1 for _ in fh)
    tot += n
    rc, out = sg(["ls-tree", "origin/main", "--", p])
    on_origin = (p.split("/")[-1] in out)
    print("SHARD-%d product rows=%d on_origin=%s" % (i, n, on_origin))
print("TOTAL_ROWS=%d (expect 805)" % tot)
rc, out = sg(["ls-tree", "origin/main", "--", "results/mass_trial/w2_judge.json"])
print("w2_judge.json on_origin=%s local=%s"
      % ("w2_judge.json" in out, os.path.exists("results/mass_trial/w2_judge.json")))

# 4) live mass-trial processes (double-burn guard)
try:
    import psutil
    n_live = 0
    for pr in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            cmd = " ".join(pr.info["cmdline"] or [])
            if ("mass_trial" in cmd) and ("_r426bmc_probe" not in cmd):
                n_live += 1
                ct = datetime.datetime.fromtimestamp(pr.info["create_time"]).strftime("%H:%M:%S")
                print("LIVE_PROC pid=%s started=%s %s" % (pr.info["pid"], ct, cmd[:150]))
        except Exception:
            pass
    print("LIVE mass-trial processes: %d" % n_live)
except ImportError:
    print("LIVE scan skipped (no psutil)")

# 5) judge state summary
js = json.load(open("results/mass_trial/w2_judge_state.json", encoding="utf-8"))
print("w2_judge_state keys: %s" % sorted(js.keys())[:24])
for k in ("n_judge", "N_judge", "expected_cells", "cells", "shards", "wave",
          "candidates_sha16", "frozen_sha16", "manifest"):
    if k in js:
        print("  %s=%s" % (k, str(js[k])[:240]))

# 6) WM + bandit
wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("WM: red=%s lane=%s ts=%s" % (wm.get("red"), wm.get("lane"), wm.get("ts")))
print("WM next_pick=%s" % str(wm.get("next_pick") or wm.get("bandit") or {})[:200])

# 7) r425 finalize log face
lp = "results/_r425bmc_w2_finalize_log.txt"
if os.path.exists(lp):
    print("finalize_log size=%d mtime=%s"
          % (os.path.getsize(lp),
             datetime.datetime.fromtimestamp(os.path.getmtime(lp)).strftime("%m-%d %H:%M:%S")))
else:
    print("finalize_log absent")
print("PROBE_DONE")
