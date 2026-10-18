"""r1017 bm-b postscript: push-verified flip + W276 seat MSG consumption + ledger row."""
import datetime
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
SHA = '1eac7bf15389cd87d6a5ffd915e6c040d6580cff'
MSG = 'fleet/inbox/MSG-20261019-055x-bmc-w276-seat.md'
MSG_DST = 'fleet/inbox/processed/MSG-20261019-055x-bmc-w276-seat.md'

POST = (" POSTSCRIPT: push DELIVERED %s (first attempt claw-blocked CORRECT: origin advanced bm-c r1109 "
        "W276-seat window mid-round, my c77ee358f5-base tree would drop _w276bmc_* faces -> fetch 2 commits "
        "-> stash 5 daemon faces -> rebase replay clean, 7 shared regen UU resolved origin-newer-wins "
        "[REPORT-2026-10-19 x2 same-generator twin / attrition / compute_audit / b_layer / regime_state / "
        "update_status] -> stash pop 3 daemon UU resolved [machine-health origin-wins r1015 / "
        "watermark_red local-06:09 newer-wins r1028 / token_usage per-machine union r1008] -> delivered "
        "7ec7d2af74..1eac7bf153 four-way verified (HEAD==origin, 0/0, key faces ls-tree); W276 seat MSG "
        "@ALL consumed -> processed/ (A 622_501..624_500 25th A-hop / B 624_501..624_700 26th above-own-A; "
        "bm-b zero direct obligation per W275 precedent -- bmb 41 owner rows read-only; supply floor "
        "stays honest-starved 0/3 until W276 prereg freeze lands = bm-c r1110 first action); "
        "本地未达 origin commit 数=0 (fetch+rev-parse verified)." % SHA)

# 1) MSG -> processed (file move; commit carries it)
if os.path.exists(MSG):
    os.makedirs('fleet/inbox/processed', exist_ok=True)
    os.replace(MSG, MSG_DST)
    print('MSG moved -> processed/')

# 2) state + heartbeat postscript flips
for path in ('state.json', os.path.join('fleet', 'machines', 'bm-b.json')):
    with io.open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    d['did'] = (d.get('did') or '') + POST
    d['now_active'] = 'r1017 closed (postscript landed)'
    d['ts'] = now
    if path.endswith('state.json'):
        d['updated'] = now
        d['updated_at'] = now
        d.setdefault('sync', {})['r1017_main_push'] = {
            'status': 'PUSHED_VERIFIED',
            'pushed_sha': SHA,
            'consumed_at': 'pending r1018',
            'behind_origin_main': 0,
            'note': 'delivered after claw-block + rebase replay onto bm-c r1109 W276-seat window; '
                    '7 shared regen UU origin-newer-wins; 3 daemon-face UU per r1015/r1028/r1008 laws; '
                    'postscript rides second push',
        }
    else:
        d['last_seen'] = now
        d['heartbeat_epoch_utc'] = int(time.time())
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print('updated', path)

# 3) round report postscript row
RROW = (now + " | r1017 bm-b postscript | dept:媒体产线+数据 | " + POST)
with io.open(os.path.join('logs', 'iteration-loop', 'round_reports.md'), 'a', encoding='utf-8') as f:
    f.write(RROW + '\n')
print('postscript row appended')

# 4) assertions
with io.open(os.path.join('fleet', 'machines', 'bm-b.json'), encoding='utf-8') as f:
    hb = json.load(f)
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
print(json.dumps({'ok': True, 'sha': SHA[:10], 'epoch': hb['heartbeat_epoch_utc']}, ensure_ascii=False))
