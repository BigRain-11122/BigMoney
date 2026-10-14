# -*- coding: utf-8 -*-
# _r997bmc_commit.py -- surgical commit + push (pathspec, no -A: _r996bmc backup dir excluded)
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def git(*a, **kw):
    r = subprocess.run(["git"] + list(a), capture_output=True, timeout=kw.get("timeout", 180))
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return out, r.returncode

paths = ["state-bm-c.json", "fleet/machines/bm-c.json", "logs/iteration-loop/round_reports-bm-c.md",
         "results/_attrition_guard_scan.json", "results/_orphan_face_probe.bm-c.json",
         "results/_sentinel_bm-c.json", "results/autofill_state.bm-c.json",
         "results/compute_audit.bm-c.json", "results/compute_audit.json",
         "results/dispatcher_state.bm-c.json", "results/gate_attrition.bm-c.json",
         "results/idle_trigger_state.bm-c.json", "results/pool_dualrun.bm-c.jsonl",
         "results/runnable_pool.bm-c.json", "results/saturation_engine/face_bm-c.json",
         "results/saturation_engine_state.bm-c.json",
         "results/_r997bmc_softverify.py", "results/_r997bmc_softcommit.py",
         "results/_r997bmc_wave2_manifest.py", "results/_r997bmc_ignite_wave15.py",
         "results/_r997bmc_schtask_check.ps1", "results/_r997bmc_closeout.py",
         "results/_r997bmc_orders_dump.txt"]
add_out, add_rc = git("add", "--", *paths)
print("add rc:", add_rc)
if add_out.strip():
    print(add_out[:500])
cm_out, cm_rc = git("commit", "-m", "round 997: wave1.5 runner rebuilt+ignited (probe burning) + wave2 manifest fact-frozen (39 local slots) + soft-copyright verified-landed fc1b936 + group-tree autostash-conflict live-wins reset + lane bookkeeping faces", "--", *paths)
print("commit rc:", cm_rc)
print(cm_out[:600])
if cm_rc != 0:
    sys.exit(1)
push_out, push_rc = git("push", "origin", "main", timeout=300)
print("push rc:", push_rc)
print(push_out[:600])
if push_rc != 0:
    rb_out, rb_rc = git("pull", "--rebase", "--autostash", timeout=300)
    print("pull-rebase rc:", rb_rc)
    p2_out, p2_rc = git("push", "origin", "main", timeout=300)
    print("push2 rc:", p2_rc)
    print(p2_out[:400])
    if p2_rc != 0:
        b_out, b_rc = git("push", "origin", "HEAD:refs/heads/machine/bm-c-r997", timeout=300)
        print("machine-branch push rc:", b_rc)
        print(b_out[:300])
fh_out, fh_rc = git("fetch", "origin", timeout=180)
rl_out, rl_rc = git("rev-list", "--count", "HEAD..origin/main")
print("behind origin after:", rl_out.strip())
