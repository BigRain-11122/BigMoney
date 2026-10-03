"""r637 bm-a S7 closeout: inbox moves, state, heartbeat, round report, orders re-scan."""
import json, time, os, shutil, subprocess, glob

TS = time.strftime('%Y-%m-%d %H:%M:%S')
now = time.time()
print('close ts:', TS)

# 1) inbox: move processed MSGs (bm-b -> bm-a, both read+receipted this round)
moved = []
for f in ['fleet/inbox/MSG-2026-10-03-1815-bmb-bma-fund-trio-findings-reply.md',
          'fleet/inbox/MSG-2026-10-03-1838-bmb-bma-rehearsal-mirror-drift.md']:
    if os.path.exists(f):
        shutil.move(f, f.replace('fleet/inbox/', 'fleet/inbox/processed/'))
        moved.append(os.path.basename(f))
print('inbox moved:', moved)

# 2) watermark verdict + next_pick for report lines
wm = json.load(open('results/watermark_red.json', encoding='utf-8'))
print('watermark red:', wm.get('red'), '| reason:', str(wm.get('reason'))[:80], '| next_pick:', str(wm.get('next_pick'))[:60])

# 3) state file: round 637 (r636 session died pre-close; its commits adopted)
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 637
st['did'] = ('r637: (1) S0 surgical delivery origin-base: NULLS value/divlowvol ghost-claim strip FOUR-FACE '
             '(bm-a@18:16:08/18:48:08 burns killed 18:38/18:53; fuse pins holding refusals@19:02) + rightful '
             'owner bm-b restore (pids per MSG-1838; action-ts r400) + MSG-1909 receipts -- push 0b845bb11 clean '
             'ff, claw pass; (2) w2-judge-3of4 double-burn forensics: bm-a first-claim 18:52:08 burn COMPLETE '
             '201/201 @18:56:24, r636 7635f7749 whole-face revert collaterally stripped live claim -> bm-c '
             '18:57:08 legal re-claim; local artifact verified BYTE-IDENTICAL to bm-c r425 delivered origin blob '
             '(sha256 a63a8f2e, 2,827,191B) = cross-machine determinism PASS, duplicate discarded; (3) r636 dead-session '
             'adoption (state was 635, commits already at 636); local ff-sync r589 reset+face checkout; (4) S0.5 orders '
             '151/151 ack-set diff 0 both scans; D-19 decisions hash check; (5) smoke 47/47; sat-engine alive '
             '(idle, queue 0, 462 shards done); (6) S6 34/34 rc0 (dualrun ZERO-DRIFT streak15 -> compute_audit settle '
             '-> watermark green -> weekend data no-ops; scorecard+clock CALL-09-30+daily_report+LIVE-2026-10-03+'
             'build_status regenerated); (7) pit-pool.md direct-write r637 whole-face-revert-vs-live-claim law; '
             '(8) inbox 2 bm-b MSGs processed+receipted (fund-trio B-fix on origin A=accept-frozen GM attn; '
             'rehearsal mirror leg-3 fix delegated bm-b family owner). Next: w2-judge 1of4 (bm-c re-claimed after '
             'bm-b stale) -> wave finalize + 805-cell probe when landed.')
with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state round_no ->', st['round_no'])

# 4) heartbeat
import psutil
hb_path = 'fleet/machines/bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = TS
hb['current_task'] = 'w2-judge wave-2 3/4 done (0/2/3 bm-c; 1of4 bm-c re-claimed after bm-b stale 18:44:20); NULLS trio bm-b canonical burning'
hb['cpu_cores'] = psutil.cpu_count()
hb['free_ram_gb'] = round(psutil.virtual_memory().available / 1e9, 1)
gpu = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        gpu = int(r.stdout.strip().splitlines()[0])
except Exception:
    gpu = None
hb['gpu_free_vram_mb'] = gpu
hb['verdict'] = 'idle-green'
hb['heartbeat_epoch_utc'] = int(now)
hb['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
with open(hb_path, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
d2 = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(d2['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat epoch int OK:', d2['heartbeat_epoch_utc'], '| clock:', d2['clock_read'])

# 5) orders re-scan (S7 second sweep)
h2 = json.load(open(hb_path, encoding='utf-8'))
ack = set(h2.get('orders_ack', []))
files = sorted(glob.glob('fleet/orders/O-*.md'))
unacked = [os.path.basename(f) for f in files if os.path.basename(f) not in ack]
print('orders re-scan unacked:', len(unacked), unacked[:5])

# 6) round report append
line = ('%s | r637 | S0 surgical: NULLS val/divlowvol ghost strip 4-face + bm-b restore (push 0b845bb11, claw pass) '
        '+ w2-judge-3of4 forensics (first-claim complete 201/201 local; bm-c later-claim delivered r425; BYTE-IDENTICAL '
        'sha256 a63a8f2e cross-machine determinism PASS; r636 whole-face-revert collateral = new pit-pool law) | '
        'verify: smoke 47/47, sat-engine alive, S6 34/34 rc0, dualrun streak15, attrition CLEAN, claws+watchdog '
        're-registered, pin8 no-op | next: w2-judge 1of4 landed? -> wave-2 finalize + 805-cell probe (bm-c ticket); '
        'NULLS trio watch (V 317/Q 211/D 106 of 2000 @18:29, ETA ~10-06..09); rehearsal mirror fix = bm-b next '
        'pre-finalize watch round\n' % TS)
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write('watermark: %s | %s\n' % ('RED: ' + str(wm.get('reason'))[:80] if wm.get('red') else 'green (py_low legal idle: board closed for bm-a lanes, w2-judge owned by bm-c/bm-b, nulls trio bm-b in flight)', line.rstrip('\n')))
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write('  ceo-visibility: [当前活] w2-judge wave-2 finalize 待 1of4（bm-c 手）+NULLS 三族 bm-b 在烧 | '
            '[最近实物] results/mass_trial/w2_judge_shard_3of4.jsonl（origin bm-c r425 交付·本机双源字节恒等实证 '
            '19:09）+ MSG-2026-10-03-1909 + pit-pool r637 律 | [下个里程碑] w2-judge 805 格判决 finalize（1of4 '
            '落地即烧，预计 <48h）\n')
    f.write('  local-behind-origin: 0 commits (synced at 0b845bb11 + round commit)\n')
print('round report appended')
