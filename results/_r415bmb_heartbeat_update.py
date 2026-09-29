# r415 bm-b heartbeat updater (file-face write law; CJK never through command channel)
import json, time

HB = 'fleet/machines/bm-b.json'
d = json.load(open(HB, encoding='utf-8'))
now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

d['last_seen'] = now
d['heartbeat_epoch_utc'] = epoch
d['clock_read'] = now
d['current_task'] = (
    'round 415 closed: W6-JUDGE judge-finalize harvested from dead predecessor session '
    '(detached pid2432 outlived parent, landed 08:14:22) -- w6_judge.json 293 judged ALL-face '
    'G1 total-zero, E[FP]=14.65, G2 0, ledger 333432; pit-89 dual-face entry flip + intake '
    'zero-face + 48h CEO clock (deadline 2026-10-01 08:14). Next: W6 48h CEO report draft '
    'window, 09:15 T-105 intraday first-live window (bm-b P0), V3 flip gate 2nd condition watch'
)
d['cpu_util_pct'] = 2.0
d['free_ram_gb'] = 13.9
d['idle_ram_gb'] = 13.9
d['gpu_free_vram_gb'] = 2.6
d['gpu_idle_vram_gb'] = 2.6
d['round_no'] = 415
d['round'] = 415
d['loop_round'] = 415
d['verdict'] = (
    'healthy: smoke 26/26; r415 successor harvest complete -- W6-JUDGE full closure (judge-finalize '
    'landed 08:14:22, receipt 4-assert pass, ALL-face G1 total-zero 0/293, E[FP]=14.65, ledger '
    '333139+293=333432 linear, dual-face pool flip + intake zero-face + 48h CEO clock armed); '
    'orders 122/122 zero-diff (normalized); S7 trio green (loop pin=2, watchdog 08:40, claw in-sync)'
)
# preserve orders_ack as-is (122 entries, zero new)

with open(HB, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write('\n')

# self-verification: epoch must be JSON int
d2 = json.load(open(HB, encoding='utf-8'))
assert isinstance(d2['heartbeat_epoch_utc'], int), 'epoch not int'
assert d2['round_no'] == 415 and len(d2['orders_ack']) == 122
assert 'T' in d2['clock_read']
print('heartbeat OK: epoch=%d (int verified) round=%d ack=%d' % (
    d2['heartbeat_epoch_utc'], d2['round_no'], len(d2['orders_ack'])))
