"""r688 bm-a S7 closeout: state round_no + heartbeat + round report append."""
import datetime
import json
import time

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- state round_no 687 -> 688 (programmatic write + reparse self-proof per r645) ----
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 688
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(sp, encoding="utf-8-sig"))
assert chk["round_no"] == 688
print("state round_no -> 688, reparse OK")

# ---- heartbeat (epoch int + T-form clock per R170/R178/R262) ----
hb_path = r"fleet\machines\bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8-sig"))
hb["last_seen"] = NOW
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["current_task"] = "W3-judge wave-3 finalize detached in flight (pid 32480); shard-2 flip DELIVERED"
hb["cpu_cores"] = 32
with open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(hb_path, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"]
print("heartbeat updated, epoch int + T-clock self-proof OK")

# ---- round report append (marker idempotence per r679) ----
rp = "round_reports-bm-a.md"
line = (
    "2026-10-04T18:0x+08:00 | r688 (bm-a) | watermark=green (red=false; satengine alive rc0 queue0 idle; "
    "compute_audit CLEAN v2.4.2; pool dualrun ZERO-DRIFT streak 51 @cutoff 17:00:27) | "
    "褰撳墠娲? W3-judge wave-3 finalize detached in flight (pid 32480, end-only writes + single-shot guard, "
    "pre-finalize probe 777/777 PASS) | 鏈€杩戝疄鐗? results/mass_trial/w3_judge_shard_2of4.jsonl (194-cell judged "
    "ckpt complete) + SHARD-2 two-layer done-flip (pool+lane owner=bm-a 17:29:26, r497 claim file backfilled) "
    "DELIVERED a3528b102 @ 2026-10-04T17:5x | 涓嬩釜閲岀▼纰? W3 judge verdict product (finalize lands <=1h, "
    "next round consumes + CEO 48h report clock starts at judge-finalize) + fund trio NULLS finalize 10-05..09 "
    "(bm-b canonical) + 10-06+ style-rotation next-wave drafting | "
    "DONE-1 S0: pre-merge absorb + merge bm-c r485 wave (1 UU pool_core_samples tail-append canon union, "
    "zero-loss containment PASS both parents) + mid-round wave-2 merge (our claim owner=bm-a 17:15:08 restored "
    "at origin by bm-b r689 per-face settle -- r687 theirs-canonical merge artifact healed) | "
    "DONE-2 S0.5: orders 154/154 zero-unacked (same-form full-name diff) + D-19 decisions MATCH 4e5be321 "
    "(sparse-clone ssh-first r631/r677) + inbox 1 archived (own r687 yield notice, no reply required) | "
    "DONE-3 S1: smoke 48/48 | "
    "DONE-4 S2/S3: board 0 open (4 claimed-lane tickets unchanged); W3 SHARD-2 burn completion verified "
    "(194/194 unique i%4==2, zero byte-dups r482, crash-fuse clean, gates pre-flip origin re-check) -> two-layer "
    "done-flip landed same-window per r668 (burn pid 26224 launched 17:15:02, ckpt mtime 17:19:23, claim lineage "
    "03f7ac259); family relay complete: 0=bm-c 17:11:50 / 1=bm-b 17:27:12 / 2=bm-a 17:29:26 / 3=bm-c 17:29:13; "
    "judge-finalize first foreground run eaten by harness 5-min silent kill (zero writes: log 0B + no out file "
    "-> idempotent re-spawn detached safe, r680 lesson applied to frozen shared runner) | "
    "DONE-5 S6: 37/37 rc0 152.0s (golden-week no-new-bar honest no-ops; daily_report REPORT-2026-10-04 + "
    "ceo_live_usage LIVE-2026-10-04 written; REGIME_GUARD not set per r660) | "
    "DONE-6 S7: self-heal 4/4 (loop pin=8 no-op + watchdog re-reg + precommit/prepush claws reinstalled) + "
    "attrition guard CLEAN 4 ledgers | "
    "璁板垎: 2 (194-cell judged ckpt + two-layer pool flip = runnable/visible artifacts delivered to origin; "
    "S6 37-leg products) | 璁拌处棰勭畻: 4/5 (state + heartbeat + report + CODELY 1 line) | "
    "鏈湴鏈怅 origin commit 鏁? 0 (closeout push_verify self-proof) | "
    "鐧昏板唽闆跺懡涓? 鏈妗? treasure_guard restore-class rc0 on 2 touched faces (runnable_pool.json + "
    "runnable_pool.bm-a.json); ckpt jsonl = registry-class READ-ONLY this round (never written); zero "
    "clean/archive/delete actions | 瀹濊棌鎹曡幏: W3 judge batch methodology question deferred to finalize "
    "closeout round (batch not yet finalized) | "
    "CODELY 姘翠綅娉? 92KB post-append (structural in-service pit-laws per r504 note; domain-split/GM "
    "threshold re-anchor = dedicated window, not unattended mid-round) | "
    "涓嬭疆鎸囬拡: 鈮爖3 judge finalize product consumption (verdict + G1/G2 + E[FP] + CEO 48h clock) "
    "鈹?fund trio finalize watch 10-05..09 鈹?10-06+ style-rotation drafting (needs bm-b astock panel) "
    "鈹?in-flight pid 32480 liveness probe first thing\n"
)
b = open(rp, "rb").read()
assert b"r688 (bm-a) | watermark=green" not in b, "marker present (r679 idempotence)"
if not b.endswith(b"\n"):
    b += b"\n"
open(rp, "ab").write(line.encode("utf-8"))
nb = open(rp, "rb").read()
assert nb.count(b"r688 (bm-a) | watermark=green") == 1
print("round report appended:", len(nb))
