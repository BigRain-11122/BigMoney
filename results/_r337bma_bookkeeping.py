# r337 bm-a bookkeeping: T-46 progress_r337 + state-bm-a + heartbeat + round report line
import json, time, datetime, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ---- 1. T-46 progress_r337 ----
tp = r'fleet\tasks\T-2026-09-25-46-P1.json'
t = json.load(open(tp, encoding='utf-8'))
t['progress_r337'] = ("2026-09-27 16:40:09 sina-construct leg census burn C8-AUTO-LAUNCHED on bm-a box (autofill tick 16:40:09 "
    "claim OK sinac-0of1 owner=bm-a + C8 LAUNCH pid=41360 latency=4.5min target_met=True; pool entry entered 16:35:37 r336 -> "
    "fill latency 4.5min well under target); burn running single-process L1 (K=100 nulls, IS167/OOS83, V1/V2/V3 h10 sole gating); "
    "judgment face (prereg sec.7/sec.8 backfill + V1/V2/V3 verdicts) follows in next rounds after runner completion; products "
    "expected results/shortline/sina_construct_p1.json (top-level evidence_cutoff) + research/shortline/sina_construct_p1_results.csv")
json.dump(t, open(tp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T-46 progress_r337 written')

# ---- 2. state-bm-a.json ----
sp = r'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 337
s['did'] = ("R337: S6 33/33 rc=0 (Sunday no-new-bar statutory no-op family; moneyflow rank spawn 16:31:16 + AH EM-mapping spawn "
    "~16:32 background in-flight) + SINA-CONSTRUCT-P1 census burn C8-AUTO-LAUNCHED 16:40:09 pid=41360 (claim OK sinac-0of1 "
    "owner=bm-a latency 4.5min target_met=True; audit @16:40:02 snapshot pool-supply-gap = 7s pre-launch race, next probe flips) "
    "+ orders 96/96 zero-unacked + decisions zero-new-lines (mtime 15:14 r334 horizon) + smoke 25/25")
s['verify'] = ("chain 33/33 rc=0 (logs/_r337bma_s6_chain.log); autofill.log 16:40:09 C8 LAUNCH SINA-CONSTRUCT-P1/sinac-0of1 "
    "pid=41360 latency=4.5min target_met=True; burn process alive CPU accumulating; WM 16:40:09 py_low_board_clear (probe raced "
    "C8 launch by seconds, batch now burning = supply face closed); T-46 progress_r337 landed")
s['next'] = ("R338+: (1) SINA-CONSTRUCT-P1 burn completion check (est 10-20min, done ~16:50-17:00) -> products "
    "results/shortline/sina_construct_p1.json + research/shortline/sina_construct_p1_results.csv -> judgment face sec.7/sec.8 "
    "backfill + V1/V2/V3 h10 verdicts + pool entry done-state verify + T-46 progress; (2) Mon 09-28 09:15 T-91 s3 first-marks "
    "chain auto-fire; (3) 10-01 month trio standing; (4) AH EM-mapping + moneyflow rank-spawn background watch; (5) W2-A burn "
    "watch bm-b lane; (6) C-01 council window 09-29 12:00")
json.dump(s, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state-bm-a round_no=337 written')

# ---- 3. heartbeat ----
hp = r'fleet\machines\bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
now = datetime.datetime.now(datetime.timezone.utc).astimezone()
cpu_pct = None; free_ram = None
try:
    import psutil
    psutil.cpu_percent(interval=2)
    cpu_pct = round(psutil.cpu_percent(interval=None), 1)
    free_ram = round(psutil.virtual_memory().available / 1024**3, 2)
except Exception as e:
    print('psutil fail:', e)
gpu_v = h.get('gpu_free_vram_gb', 5.24)
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=15)
    if out.returncode == 0 and out.stdout.strip():
        gpu_v = round(float(out.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception as e:
    print('nvidia-smi fail:', e)
h['last_seen'] = now.isoformat()
h['current_task'] = ("R337: SINA-CONSTRUCT-P1 census burn RUNNING via autofill C8 pid=41360 (launched 16:40:09 est 10-20min, "
    "judgment face next rounds); board 0 open otherwise")
if cpu_pct is not None: h['cpu_pct'] = cpu_pct
if free_ram is not None: h['free_ram_gb'] = free_ram
h['gpu_free_vram_gb'] = gpu_v
h['verdict'] = ("burning: sina-construct census C8 pid=41360 (SINA-CONSTRUCT-P1 sinac-0of1 lane_owner=bm-a, prereg FROZEN "
    "f5acd8fa, burn-unblock receipt MSG-1642 fully consumed r336); board 0 open / all-claimed; smoke 25/25; audit CLEAN")
epoch = int(time.time())
assert isinstance(epoch, int)
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now.isoformat()
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO with T separator'
print('heartbeat written epoch=', chk['heartbeat_epoch_utc'], 'clock=', chk['clock_read'], 'cpu=', cpu_pct, 'ram=', free_ram, 'gpu=', gpu_v)

# ---- 4. round report line ----
rp = r'logs\iteration-loop\round_reports-bm-a.md'
line = (now.isoformat(timespec='seconds') + " | R337 bm-a (dept:engineering+fleet) | WM first-line verdict: green (red=false lane "
    "healthy @16:40:09 probe py_low_board_clear n=probe-raced-C8-launch-by-seconds -- pool SINA-CONSTRUCT-P1 entered 16:35:37 "
    "takeable lane_owner=bm-a + autofill C8 LAUNCH 16:40:09 pid=41360 latency=4.5min target_met=True = supply face closed, py "
    "loads next probe; audit v2.3 @16:40:02 CLEAN flags=[] py 0.1% load_state=pool-supply-gap = 7s pre-launch snapshot race, "
    "disclosed not flagged) | DID: (1) S0 pull up-to-date; (2) S0.5 orders 96/96 acked zero-unacked (python authoritative scan "
    "per r335 pitlaw; PS-diff artifact caught: ack keys carry .md suffix, extension-stripped diff false-positives 95/96 -- "
    "verification discipline = compare full basenames) + decisions.md zero-new-lines (mtime 15:14 = r334 horizon, zero action); "
    "(3) S1 smoke 25/25 PASS; (4) S2 board scan python 93 tickets: 0 open / board all-claimed-or-done (T-91 mine: s1/s2 landed "
    "r308/r309, s3 auto-fires 09-28 09:15) + Codely job_list empty; (5) S3 SINA-CONSTRUCT-P1 burn lane: NO inline run per S3 "
    "discipline (pool batch = C8 autofill's), C8 pickup verified same round (claim OK sinac-0of1 + LAUNCH pid=41360 16:40:09, "
    "autofill.log) + burn process liveness verified CPU accumulating + T-46 progress_r337 landed (ticket bookkeeping; "
    "burn-unblock receipt MSG-1642 chain fully closed: prereg FROZEN f5acd8fa + runner 6c9fb92f + pool entry + C8 launch); "
    "(6) S6 chain 33/33 rc=0 Sunday statutory no-op family (moneyflow rank spawn 16:31:16 + AH EM-mapping spawn ~16:32 "
    "background in-flight 30min-throttle post-expiry retries; astock_daily/rev_osc/fund_premium/alloc_paper lane-guarded no-ops "
    "R31; live_paper OK; t35_open_fill day=2026-09-24 PASS zero-pending 6; grid_paper no markable bar; daily_report "
    "REPORT-2026-09-27 faces=4 token=1; token_meter L2 legs 1 today) | VERIFY: logs/_r337bma_s6_chain.log 33/33 rc=0 NON-ZERO "
    "empty; autofill.log 16:40:09 LAUNCH line + Get-Process 41360 alive; orders diff zero; smoke 25/25 | NEXT: R338 burn "
    "completion check -> judgment face sec.7/sec.8 backfill + V1/V2/V3 h10 verdicts + pool done-state verify + T-46 progress; "
    "Mon 09-28 09:15 T-91 s3 first-marks auto-fire; 10-01 month trio; AH/moneyflow background watch; W2-A bm-b lane watch; "
    "C-01 council 09-29 12:00\n")
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report R337 line appended')
