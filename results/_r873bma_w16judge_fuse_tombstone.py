"""r873 bm-a: tombstone of fused W16-JUDGE sig (fake crash #3, r824
W14-screen / r860 W16-JUDGE manual-tombstone precedent, same bug class).

Root cause of the 04:52:04 "crash": trial-labor runners write no
pool_claims worker handshake; the post-completion 30-min confirm
window misreads the (already-cleanly-exited) runner as dead and
records a crash (r860 pit law, W16-SCREEN same-morning precedent).
Completion evidence: logs/autofill_TRIAL-LABOR-W16-JUDGE.log ends
"judge shard 0of1 complete" 40/40 cells (04:24:08, post-r861-fix
runner sha 946458bc unchanged since); checkpoint 40/40 full;
judge-finalize consumed r862 (w16_judge.json + ledger 802,318);
intake lawful-zero. Runner code never at fault for this entry.
Worker-claim umbrella landed this round ->
results/pool_claims/TRIAL-LABOR-W16-JUDGE/w16-judge-0of1.bm-a.json.
Both faces (shared + bm-a lane mirror) edited identically so no
lane-union can resurrect the sig (merge_crash_fuse newer-event-wins:
cleared_ts now > last_crash_ts 04:52:04).
"""
import json
import datetime
import os

FACES = [r"results/crash_fuse.json", r"results/crash_fuse.bm-a.json"]
SIG = "scripts/trial_labor_w16.py|judge,--shard,0,--shards,1"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for FACE in FACES:
    f = json.load(open(FACE, encoding="utf-8"))
    sigs = f.setdefault("sigs", {})
    cleared = f.setdefault("cleared", {})
    assert SIG in sigs, f"fused sig present in {FACE}"
    reg = sigs.pop(SIG)
    cleared[SIG] = {
        "crashes": int(reg.get("count", 1)),
        "old_code_sha256": reg.get("code_sha256"),
        "cleared_by": "bm-a",
        "cleared_ts": now,
        "reason": ("r873 bm-a manual tombstone: 04:52:04 crash = post-"
                   "completion 30-min-confirm artifact (no pool_claims "
                   "handshake, r860 pit law; W16-SCREEN same-morning "
                   "precedent); burn completed cleanly 40/40 cells "
                   "runner-log 'judge shard 0of1 complete' 04:24:08 "
                   "rc0, checkpoint full, judge-finalize consumed r862 "
                   "(w16_judge.json + ledger 802,318), intake "
                   "lawful-zero; runner sha 946458bc not at fault; "
                   "worker-claim umbrella landed same round"),
        "entry": reg.get("entry"),
        "shard": reg.get("shard"),
    }
    tmp = FACE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(f, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FACE)
    # post-write gates (r859 law: parse BEFORE declaring done is for
    # inserts; here reparse after replace)
    f2 = json.load(open(FACE, encoding="utf-8"))
    assert SIG not in f2.get("sigs", {})
    assert SIG in f2.get("cleared", {})
    print("TOMBSTONED", FACE, "| sigs:", len(f2.get("sigs", {})),
          "| cleared:", len(f2.get("cleared", {})))
print("BOTH FACES OK")
