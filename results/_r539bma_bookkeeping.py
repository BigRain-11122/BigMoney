"""r539 bm-a S7 bookkeeping: state round bump + heartbeat write (JSON int epoch law)."""
import json
import time
from datetime import datetime, timezone, timedelta

# --- state-bm-a.json: round bump (538 -> 539) ---
st = json.load(open('state-bm-a.json', encoding='utf-8'))
assert st['round_no'] == 538, f"unexpected round_no {st['round_no']}"
st['round_no'] = 539
st['last_round'] = 539
st['last_round_at'] = '2026-10-01T21:40:00+08:00'
st['last_round_ts'] = '2026-10-01 21:40'
st['current_task'] = 'W27 freeze+burn (16th engine wave, bm-a 5th-owned) + S6 chain'
st['next'] = ('W27 12/12 product delivery -> W27 finalize after bm-c W26 finalize '
              '(chain-gated, FAIL-CLOSED cumulative deps) -> S5 4/4 verdict')
with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=2)

# --- heartbeat fleet/machines/bm-a.json ---
epoch = int(time.time())  # JSON int type law (R170/R178)
clock = datetime.now(timezone(timedelta(hours=8))).isoformat(
    timespec='seconds')
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = clock
hb['current_task'] = st['current_task']
hb['verdict'] = 'W27 frozen+burning (engine supply line active)'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

# self-verify: epoch int + json.loads round-trip
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO 8601 T-separated'
print('state round_no ->', st['round_no'])
print('heartbeat epoch:', chk['heartbeat_epoch_utc'], 'int OK | clock:', chk['clock_read'])
