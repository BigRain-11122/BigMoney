# -*- coding: utf-8 -*-
"""R246 bm-a closeout: state bump + round report + CODELY pit + heartbeat.
Byte-faithful appends for shared/text files; whole-rewrite for own state file
(producer pattern). Heartbeat epoch must be JSON int (R170/R178 law).
"""
import io
import json
import time
import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# ---------- 1) state-bm-a.json (own producer file, whole rewrite) ----------
SP = "state-bm-a.json"
st = json.loads(io.open(SP, encoding="utf-8").read())
prev_round = st["round_no"]
assert prev_round == 245, f"unexpected round_no {prev_round}"
st.update({
    "round_no": 246,
    "did": ("R246: S0 pull-rebase clean (bm-b r245/r246 3 commits: T-78 closeout family) + "
            "dead-debris adoption; S0.5 orders 79/79 both-scans zero-diff + decisions mtime 12:07 "
            "no new lines; S1 smoke 25/25; S3 = dead 12:18-instance (R246-prior) debris ADOPTED per "
            "R241 law (run-log forensics: author instance exited 12:25:24 exit=0 uncommitted; "
            "12:28-instance retreat was over-conservative): SEED_REGISTRY cn_rev_tilt_p1=20260930 "
            "(collision w/ pa1e_premium_event caught at pre-run scan) + prereg s2 evidence_cutoff="
            "2026-09-22 backfill (T=8792 N=5222 same-source probe) + s3.4 zero-run amendment -> "
            "science_gates selftest 35/35 -> commit 1a64747c = FREEZE COMPLETE zero runs; ticket "
            "progress_r246 landed with sharpened runner-writing contract (all judgment/cost/null "
            "contracts recorded, next round writes scripts/cn_rev_tilt_p1.py directly, no re-read); "
            "S6 27 legs green (weekend no-op family, cutoff 09-24); S7 schtasks dual-healthy"),
    "verdict": "GREEN",
    "next": ("T-73 s3: WRITE scripts/cn_rev_tilt_p1.py directly per ticket progress_r246 contract "
             "-> selftest -> pool-submit (>5min discipline); then s3 remaining model preregs; "
             "09-28 Monday new-bar chain; 10-01 month-boundary trio + REGIME_GUARD v3 date gate; "
             "T-70 verdict window 10-09"),
    "ts": now,
    "updated_at": now,
    "current_task": ("R246 done: dead-debris adopted+committed (freeze complete), runner contract "
                     "landed in ticket; next=write cn_rev_tilt_p1.py + pool submit"),
    "last_round_ts": st["ts"],
})
io.open(SP, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---------- 2) round report (append one line, own file) ----------
RP = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    "2026-09-26 12:5x | R246 | [wm:probe insufficient_history n=1 (window needs samples) + audit "
    "FLAG:pool_starvation=legal idle whitelist same-state R236/243 (board fully closed pool ready 0; "
    "T-73 s3 batch feeds pool next round); red=false] | did: S0 pull-rebase clean (bm-b 3 commits "
    "T-78 closeout); S0.5 orders 79/79 both-scans zero-diff + decisions zero new lines (mtime 12:07); "
    "S1 25/25; S3 MAIN = dead-round debris ADOPTION + T-73 s3 freeze closure: round-start dirty x3 "
    "(12:24:46-53) forensically attributed via run_20260926_121801.log + round_*.out transcript = "
    "dead 12:18-instance (R246-prior) half-product, NOT a live session (12:28-instance retreat was "
    "over-conservative false-negative) -> R241 adoption law: SEED_REGISTRY cn_rev_tilt_p1=20260930 "
    "(20260926 collided with pa1e_premium_event band, caught at pre-run registration scan, xstock "
    "51_100 rejection precedent) + prereg s2 evidence_cutoff=2026-09-22 backfilled (same-source probe "
    "T=8792 N=5222) + s3.4 zero-run in-place disclosure -> science_gates selftest 35/35 -> commit "
    "1a64747c = prereg FREEZE COMPLETE, zero runs; ticket progress_r246 = sharpened resume pointer "
    "(runner-writing contract fully recorded: loader assert cutoff==2026-09-22/T>=8000/N>=5000 "
    "fail-closed, top-20-of-decile equal-weight h10 T+1 cash-leg, V1 13bp x2 + x2/x3 stress, tilt "
    "252d REV-minus-MOM shift(1) 0.9/0.1 warmup-cash, nulls own K=50 seed band 20260930+i -> "
    "null_pool -> g1_prime_v2, G2 g2_registration_v2 + DSR + PBO CSCV-8, D6 corr admission >=0.7 "
    "reject, census-EW + random baselines trial-N, hard-bounds trio crisis windows, regime v3 "
    "descriptive column, artifact+checkpoint+selftest+audit, append_ledger, pool-submit); "
    "S6 27 legs green (weekend no-ops: daily 0 rows cutoff 09-24, regime ORANGE shadow #10 breadth "
    "0.77, clock ORANGE_COOL idempotent, lhb 30min throttle, heat weekend, futures/options/sina_mf/ths "
    "zero-network, moneyflow rank spawn never-fired, AH spawn self-heal, fp bm-c lane, fundamental "
    "15.3h fresh, blf mask regen, paper 6 anchors OK, t35 zero-pending PASS, prospect 22/22 drift=0, "
    "promotion 0/22 legal, aggr marks idempotent, alloc bm-b lane, export idempotent, scorecard 6, "
    "report 4 faces, build_status 10f/432combos/6traders, token delta=75); S7 schtasks dual-healthy "
    "(Loop Running=this instance, Watchdog Ready), inbox zero unread | evidence: commit 1a64747c + "
    "science_gates 35/35 + results/_r246bma_t73_progress_insert.py + smoke 25/25 + S6 27 exit-0 "
    "legs | next: WRITE scripts/cn_rev_tilt_p1.py directly (contract in ticket progress_r246, "
    "NO re-reading) -> selftest -> pool-submit; s3 remaining preregs; 09-28 new-bar chain; 10-01 "
    "month-boundary trio + REGIME_GUARD v3\n")
raw = io.open(RP, encoding="utf-8", newline="").read()
nl = "\r\n" if raw.endswith("\r\n") or "\r\n" in raw[-200:] else "\n"
if not raw.endswith("\n"):
    raw += nl
io.open(RP, "w", encoding="utf-8", newline="").write(raw + line)

# ---------- 3) CODELY.md pitfall entry (line-level append) ----------
CM = "CODELY.md"
pit = (
    "- [2026-09-26 12:5x] 坑律（bm-a R246·死轮残骸判别律·12:28 误判面·E1）：轮首遇极新未提交改动，"
    "禁仅凭 mtime 新鲜度判「活跃并发会话」而退避——判别器=logs/iteration-loop/run_*.log+round_*.out "
    "取证（作者实例结束时间 vs 改动时间 vs transcript 是否记录该改动；兄弟仓 loop 进程存活≠本仓会话在飞）"
    "→死轮残骸（作者实例已结束）=R241 收养范式：验内容+commit 带收养出处续走；活跃会话=退避。实弹：12:24:46 "
    "改动 3.5min 新鲜+4 个 codely 进程存活（实为 BigLife/FluxVerse/MiniGame loop）→12:28 实例误判静默退避，"
    "链条若照抄=残骸永挂 T-73 链卡死。指针=run_20260926_1218/122801.log+commit 1a64747c。\n")
raw = io.open(CM, encoding="utf-8", newline="").read()
if "死轮残骸判别律" not in raw:
    if not raw.endswith("\n"):
        raw += "\n"
    io.open(CM, "w", encoding="utf-8", newline="").write(raw + pit)
    print("CODELY pit appended")
else:
    print("CODELY pit already present")

# ---------- 4) heartbeat (own file, whole rewrite, epoch int) ----------
HB = "fleet/machines/bm-a.json"
hb = json.loads(io.open(HB, encoding="utf-8").read())
epoch = int(time.time())
hb.update({
    "last_seen": now,
    "current_task": ("R246 done: dead-debris adopted (freeze complete) + runner contract landed; "
                     "next=write cn_rev_tilt_p1.py + pool submit"),
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_iso,
    "round_no": 246,
    "task": "R246 done: T-73 s3 freeze complete (seed+cutoff adopted committed 1a64747c); next=runner write+pool",
    "verdict": "alive",
})
io.open(HB, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
re = json.loads(io.open(HB, encoding="utf-8").read())
assert isinstance(re["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
print("closeout OK: state 246, report+CODELY appended, heartbeat epoch int", epoch)
