# -*- coding: utf-8 -*-
"""r849 bm-a closeout classifier executor: restore other-machine faces from
index (reset-leftover stale worktree copies, r523iii checkout-restore law),
then stage this machine's own outputs only (anti-swallow law)."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESTORE = [
    "Tools/_r706bmc_qa_ignite.py",
    "fleet/machines/bm-c.json",
    "fleet/orders/O-20261007-2315-bm-c.md",
    "logs/iteration-loop/round_reports-bm-c.md",
    "qa/equity-curve-r706.png",
    "qa/smoke-r706.md",
    "results/_r706bmc_qa_runner.err",
    "results/_r706bmc_qa_runner.out",
    "results/_r706bmc_s05_facts.json",
    "results/_r706bmc_s6_log.txt",
    "results/autofill_state.bm-c.json",
    "results/compute_audit.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/futures_update_status.bm-c.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/lhb_update_status.bm-c.json",
    "results/oss_eng_scan/scan-20261007.json",
    "results/pool_dualrun.bm-c.jsonl",
    "results/regime_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/token_usage.bm-c.json",
    "results/update_status.bm-c.json",
    "scripts/oss_eng_scan.py",
    "state-bm-c.json",
    # owner=bm-c, this round's local session did NOT write it (anti-revert)
    "research/OSS_HARVEST_LEDGER.md",
]

r = subprocess.run(["git", "restore", "--"] + RESTORE, capture_output=True, text=True)
print("restore rc:", r.returncode, r.stderr.strip()[:200] if r.returncode else "OK")

# scratch cleanup
r2 = subprocess.run(["git", "clean", "-q", "-f", "--", "_r849bma_status.txt"],
                    capture_output=True, text=True)
print("scratch clean rc:", r2.returncode)

# stage this machine's own faces: everything still dirty + new untracked
r3 = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
print("add -A rc:", r3.returncode, r3.stderr.strip()[:200] if r3.returncode else "OK")
r4 = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
lines = r4.stdout.splitlines()
staged = [l for l in lines if l and (l[0] in "AM" or (l[0] == "R" or l[0] == "D"))]
print("post-add status lines:", len(lines))
for l in lines[:12]:
    print(" ", l[:120])
