import json, os, glob, time, datetime

# 1) round-end orders double scan
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
ack = set(h.get('orders_ack', []))
orders = sorted(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
unacked = [o for o in orders if o not in ack]
print('round-end orders scan: files=%d ack=%d UNACKED=%s' % (len(orders), len(ack), unacked))

# 2) state update: round_no 528, did
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s['round_no'] = 528
s['did'] = ('r527: (1) W14-GENERATE harvest: r526 detached burn completed 17:28:17 (raw 10000 -> dedup 293, zero engine cells, '
            'trials ledger untouched N=0 held) -> w14_candidates.json + TRIAL_GRAMMAR_LEDGER row committed as consumed-grammar inventory; '
            'pool shard flipped done (W2 r138 shape), ENTRY PARK HONORED (screen/judge legs NOT started, no new prereg); governance conflict '
            '(r526 ignition on shard-layer r493 re-arm verdict vs entry-layer r494/r504 park_note shared-verdict) disclosed MSG-20261001-173x '
            'to bm-b+GM -- my error face acknowledged (ignition precheck must read entry park_note); N2-W15 slice-2/3 self-held pending same '
            'ruling (shared 18-tuple grammar family); (2) origin intake: bm-c r326 heal (r526 closeout stale-sweep 3rd occurrence -- N1-W14 '
            'engine-wave finalize restored, K=30,920 ledger 397,548) + bm-b r515 W16 freeze (wave no.15 held by my N2-W15 draft; my next N1 '
            'engine wave = W18 after W17=bm-c); (3) S6 33 legs rc0 (holiday no-bar honest skips, dualrun ZERO-DRIFT 5/3, WM=py_low_with_work_cands '
            'T-141 design-ticket only, supply vacuum = all four surfaces governance-held); smoke 47/47')
json.dump(s, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('state round_no ->', s['round_no'])

# 3) heartbeat update
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
h['last_seen'] = clock
h['current_task'] = ('r527 close: W14-GENERATE harvested (293-face candidates committed as consumed-grammar inventory, entry park honored, '
                     'conflict disclosed MSG-173x); N2-W15 self-held pending GM grammar-family ruling; next N1 engine wave W18 (after bm-c W17)')
h['cpu_pct'] = 4.0
h['verdict'] = 'harvest-done-governance-hold'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written, epoch int self-proof:', chk['heartbeat_epoch_utc'], chk['clock_read'])
