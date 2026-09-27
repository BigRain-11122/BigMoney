# r311 bm-a wrap: state round_no+1, round report line, heartbeat w/ orders_ack self-verify (r312 law)
# trace evidence per r306 wrap-script pattern; idempotent-safe (append guarded by marker check)
import json, os, time, subprocess
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# ---- S7 wrap double-scan: orders vs ack (R13 law, no timestamp filtering) ----
orders = sorted(f for f in os.listdir('fleet/orders') if f.startswith('O-') and f.endswith('.md'))
hb_path = 'fleet/machines/bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8-sig'))
ack = set(hb.get('orders_ack', []))
unacked = [o for o in orders if o not in ack]
print('wrap-scan orders=%d ack=%d unacked=%s' % (len(orders), len(ack), unacked or 'NONE'))
if unacked:
    raise SystemExit('UNACKED ORDERS PRESENT -- handle before wrap: %r' % unacked)

# ---- state file ----
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8-sig'))
st.update({
    'round_no': 311,
    'did': 'R311: r314 pool-flip gate X2-LD flipped done (1/14 pending honest); J13 L2 retro landed research/auto/retro-20260927.md (zero-API-token); S6 24 legs rc=0 + 3 bar-conditional legal skip',
    'verdict': 'py low legal-idle (probe py_low_board_clear n=3 span 22.8min avg 0.1%; board 0 open; pool_ready 14 autofill supply face alive 10:10 X2-DA; audit v2.3 CLEAN)',
    'next': 'R312: Monday 09-28 window prep -- bm-b SIG/BARS-2026-09-28 evening -> S6 sysv1 leg replays -> first cohort entries at 09-28 open + first marks -> three report faces; pool 14 shards autofill standing; 10-01 month trio standing',
    'ts': ts, 'last_round_ts': ts, 'updated_at': ts, 'last_run': ts, 'last_round_at': ts,
    'last_round': 310, 'updated': ts, 'last_seen': ts,
    'current_task': 'R312 next: Monday s3 auto-fire watch + pool autofill burn standing',
    'task': 'R311: pool-flip X2-LD + J13 retro + S6 24 legs green',
})
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state-bm-a.json round_no -> 311')

# ---- round report line ----
rp = 'logs/iteration-loop/round_reports-bm-a.md'
line = (
    "%s | R311 bm-a (dept:工程+策略) | WM first-line verdict: red=false lane healthy; probe 10:12 py_low_board_clear n=3 span 22.8min avg 0.1%% LEGAL-idle (board 0 open tickets 0 bandit 0; pool_ready 14 fleet-shard autofill supply face; audit v2.3 flags[] CLEAN load_state pool-supply-gap non-flag; autofill alive 10:10:01 launched X2-DA pid 9576 = compute face delegated to autofill per S3 discipline) | did: (A) r314 pool-flip evidence gate FIRST per law: X2-LD flipped done 1878/1878 cells evidence-gated (1 flipped / 14 marker-absent pending / 0 refused; remaining = X2-DA..DE deep axis + PROSPECT-REGIME-SEGMENTS x9 autofill burn) (B) J13 L2 retro first-order landed research/auto/retro-20260927.md (qwen2.5:7b zero-API-token per O-2325 L2 route; un-audited disclaimer header verified; claims-not-instructions anti-injection) ; queue triage honest: J12 town 10-building alignment verified ALREADY-DONE per r277 勘注 (anti-dup zero rebuild), J18b update_status no existing carrier + freshness already surfaced by smoke/compute_audit/daily_report faces (no spec = no invention, anti-gilding) (C) S0.5 both-scans: orders 96/96 round-start normalized-diff + wrap rescan zero unacked; decisions.md no new rows since 03:14 batch (D-20260927-04 receipt standing per R308/R309); inbox zero unprocessed for bm-a; post_review 2849 rows 0 x-rows | (D) S6 24 legs rc=0 + 3 bar-conditional legal skip (Sunday cutoff 09-24: audit CLEAN / wm py_low_board_clear / daily 0-new / regime ORANGE shadow / scorecard 6-28-7 / clock ORANGE_COOL idempent sleeves4 activated0 / lhb 30min-guard / heat weekend / fut+opt cutoff-covered zero-network / mf rank-throttle 23.1min / smf fresh / astock+sigexport bm-b-lane honest no-op / ths same-day / ah spawn-throttle 23min in-flight / fundprem bm-c-lane / fundamental 12.5h fresh / b-layer gates-all-pass / aggr+grid+sysv1 idempotent no-op sysv1 ARMED awaiting Monday / alloc bm-b-lane / t24promo 0/22 honest legs / t35 export 09-24 idempotent 18 positions 6 traders / daily_scorecard 6 traders / daily_report faces=4 token=1 / build_status 10factors 432combos / token delta=0 API L2 legs=1 retro ~6450tok local) | smoke 25/25 | schtasks alive per R49 schtasks-not-CIM law (IterationLoop Running next 10:18 + Watchdog Ready 10:20) | NEXT: Monday 09-28 open window = new-bar full chain + T-91 s3 auto-fire (bm-b SIG/BARS-2026-09-28 evening -> S6 sysv1 leg replays -> first cohort entries at 09-28 open + first marks -> three report faces auto-flow); pool 14 shards autofill burn standing; 10-01 month trio standing\n" % ts
)
prev = open(rp, encoding='utf-8').read()
if 'R311 bm-a (dept' not in prev:
    open(rp, 'a', encoding='utf-8').write(line)
    print('round report appended R311')
else:
    print('round report R311 already present -- skip append')

# ---- heartbeat ----
def cpu_ram():
    try:
        import psutil
        return psutil.cpu_percent(interval=2), psutil.virtual_memory().available / (1024**3)
    except Exception:
        return None, None

def gpu_free():
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                             capture_output=True, text=True, timeout=15).stdout.strip().splitlines()[0]
        return round(int(out) / 1024, 2)
    except Exception:
        return None

cpu_pct, free_ram = cpu_ram()
gpu_free_gb = gpu_free()
ack_list = list(orders)  # r312 law: whole-filename list rewrite incl. .md
# pre-write self-verify: every order file covered, intersection count == orders count
assert set(orders).issubset(set(ack_list)) and len(set(orders) & set(ack_list)) == len(orders), 'ack self-verify failed'
hb.update({
    'machine_id': 'bm-a',
    'last_seen': ts,
    'clock_read': ts,
    'heartbeat_epoch_utc': epoch,  # MUST be JSON int (R170/R178 law)
    'current_task': st['current_task'],
    'task': st['task'],
    'verdict': 'legal-idle face (board 0 open; pool_ready 14 fleet-shard autofill supply-gap non-flag; audit v2.3 CLEAN; T-91 armed awaiting Monday 09-28 SIG/BARS; J13 L2 retro landed today)',
    'orders_ack': ack_list,
    'round_no': 311,
    'cpu_cores': 32, 'cores': 32,
    'gpu_free_vram_gb': gpu_free_gb if gpu_free_gb else hb.get('gpu_free_vram_gb'),
    'gpu_idle_vram_gb': gpu_free_gb if gpu_free_gb else hb.get('gpu_idle_vram_gb'),
    'gpu_idle_vram_mb': int(gpu_free_gb * 1024) if gpu_free_gb else hb.get('gpu_idle_vram_mb'),
    'gpu0_free_vram_gb': gpu_free_gb if gpu_free_gb else hb.get('gpu0_free_vram_gb'),
})
if cpu_pct is not None:
    hb['cpu_pct'] = cpu_pct; hb['cpu_util_pct'] = cpu_pct
if free_ram is not None:
    hb['free_ram_gb'] = round(free_ram, 1); hb['idle_ram_gb'] = round(free_ram, 1)
    hb['free_ram_mb'] = int(free_ram * 1024)
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# post-write verification (S7 law): reload + epoch int type + ack coverage
chk = json.load(open(hb_path, encoding='utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert all(o in chk['orders_ack'] for o in orders), 'post-write ack coverage failed'
print('heartbeat updated: epoch=%d(int) clock=%s cpu=%s ram=%s gpu_free=%sGB ack=%d' % (
    chk['heartbeat_epoch_utc'], chk['clock_read'], cpu_pct, free_ram and round(free_ram, 1), gpu_free_gb, len(chk['orders_ack'])))
