# -*- coding: utf-8 -*-
# r570 bm-a S7: heartbeat update (epoch int + T-clock) + inbox consumed-MSG archiving
import json, time, datetime, os, shutil

now = datetime.datetime.now()
fp = 'fleet/machines/bm-a.json'
h = json.load(open(fp, encoding='utf-8'))
epoch = int(time.time())
h['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
h['current_task'] = ('W73 registered + burn in flight (tick self-ignited shard-0 10:38:19, '
                      'engine_owner=bm-a SIXTY-SECOND wave); W72 collision yielded to bm-b '
                      '(r511, zero-cost draft yield)')
h['heartbeat_epoch_utc'] = epoch
assert isinstance(h['heartbeat_epoch_utc'], int)
h['clock_read'] = now.isoformat(timespec='seconds') + '+08:00'
assert 'T' in h['clock_read']
h['verdict'] = ('r570: W73 FREEZE landed + ignition verified (A 189_004..191_003 / '
                'B 51_601..51_800 both arithmetic zero-skip, gate ADMIT + banned ADMIT + '
                'full-chain selftest W2..W73 PASS + MSG-0640 FIX-A/B/C five-face '
                'pure-insertion, commit cd2e57af6) + W72 same-window collision yielded to '
                'bm-b c7babddec first-land per r511 commit-order (zero-cost draft yield: '
                'FIX-A intercept 9th, zero ignition zero push, bitwise ADMIT = r530 '
                'family 9th cross-validation, yield receipt MSG-20261002-1036-bma) + '
                'pool_core_samples.jsonl local redirect-clobber repaired by union (750 '
                'origin + 3 live burn samples, compute_audit red->green retest) + S6 '
                'chain all-green (reconcile streak 35/3 ZERO-DRIFT, watermark '
                'insufficient_history fresh-series, scorecard 22.8s, ORANGE_COOL clock '
                'call, LIVE-2026-10-02 written)')
open(fp, 'w', encoding='utf-8', newline='').write(json.dumps(h, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open(fp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
print('heartbeat OK: epoch int', chk['heartbeat_epoch_utc'], '| clock', chk['clock_read'])

# --- inbox: archive superseded seat MSGs (knowledge fully superseded by landed registry rows)
consumed = [
    'MSG-20261002-1040-bmb-w70-seat.md',      # W70 seat pub -> W70 registered+finalized (bm-b r570)
    'MSG-20261002-1015-bma-w70-yield-w71-seat.md',  # own r569 yield+seat -> W71 taken by bm-c r361, superseded
    'MSG-20261002-1017-bmc-w71-seat.md',      # W71 seat pub -> W71 registered+burned 12/12 (bm-c r361)
]
os.makedirs('fleet/inbox/processed', exist_ok=True)
for m in consumed:
    src = os.path.join('fleet/inbox', m)
    if os.path.exists(src):
        shutil.move(src, os.path.join('fleet/inbox/processed', m))
        print('archived:', m)
    else:
        print('already gone:', m)
