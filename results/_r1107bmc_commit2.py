# -*- coding: utf-8 -*-
# r1107 closeout commit + push.
import io, os, subprocess, sys

def g(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rc, out = g("add", "-A")
print("add rc", rc, out.strip()[:150])
if rc:
    sys.exit(1)
rc, out = g("diff", "--staged", "--numstat")
tot = len(out.strip().splitlines())
print("staged files:", tot)
MSG = u"""round 1107 closeout: W275 PREREG CYCLE-HEAD LANDED (bm-c) -- prereg on origin 1fcc0bc30f (byte-identical sim sha e4e1ce44f5afd03b, banned gate ADMIT rc0, bands A 620_301..622_300 24th consecutive A-hop / B 622_301..622_500 25th above-own-A); S6 light 10/10 rc0 (r1096-r1106 canon clone _r1107bmc_s6_light.py: dualrun reconcile / compute_audit / py_watermark / update_daily 0 rows cutoff 10-16 pre-15:30 Monday honest / market_regime shadow / CALL-2026-10-16 ORANGE_COOL idempotent sleeves=4 activated=0 / fund_premium no-op pre-15:30 / b_layer gates all_pass / REPORT-2026-10-19 faces=5 token=1 / token delta=0); S7: attrition 4/4 fresh CLEAN (bm-a 0.05h / bm-b 0.05h / bm-c 1.04h / machine-health 0.16h); D-19 dual-scan NOOP hold (ord 57d1f5de / dec 8706acd8, expected hold confirmed); claws CR-normalized identical both (pre-commit 1141B / pre-push 1345B); loop+watchdog PRESENT -- LogonType=InteractiveToken REGRESSION DISCLOSED (pre-existing post-10-17-cleanup face; S4U XML-flip re-pass DENIED non-elevated via Register-ScheduledTask AND schtasks rc=access-denied x2 disclosed; tasks restored from backup _r1107bmc_s4u_backup_*.xml lane alive at pre-window state; elevated S4U re-pass = deploy-channel backlog; register_loop_task.ps1 fail-open design confirmed r981 face); inbox sweep zero files; watermark_red ts-newer-wins heal (bm-c 04:42:03 vs origin bm-a 04:18:04, r1028 family, ff-pull be7c129d32 clean); idle --worked rc0 idle_rounds=0; counter 1107->1108. Next: r1108 W275 five-face freeze splice chain FIRST ACTION (_w275bmc_freeze_edits.py per _w274bmc template, gate0.5 W274-face green) + TODAY Monday 2026-10-19 15:30 papers chain + BM automation-plan <=10-25/<=10-31"""
msgfile = os.path.join("results", "_r1107bmc_commit_msg2.txt")
io.open(msgfile, "w", encoding="utf-8", newline="\n").write(MSG)
g("add", "--", msgfile)
rc, out = g("commit", "-F", msgfile)
print("commit rc", rc)
print(out.strip()[:300])
if rc:
    sys.exit(1)
rc, out = g("push", "origin", "main")
print("push rc", rc)
print(out.strip()[:300])
rc, out = g("status", "--porcelain")
print("status after push:")
print(out[:300])
