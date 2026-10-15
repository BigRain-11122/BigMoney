# r1009 bm-a closeout bookkeeping (state + heartbeat + round report append)
import json, time, datetime

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# --- state-bm-a.json ---
sp = r'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 1010
s['last_round'] = 'r1009'
s['last_round_at'] = now_iso()
s['last_round_closed'] = 'r1009 bm-a: CEO order O-20261015-0025 receipt+ack + S6 chain 43 legs rc0 (live_paper leg restored) + quartet green + watch window (W245=bm-c turn)'
s['now_active'] = 'r1009 closeout: post-W244 idle-watch (engine queue 0, W245 seat/freezer=bm-c turn per declared intent; bm-a W246-class derive fires after W245 chain lands)'
s['next'] = ('r1010: W245 chain watch (bm-c seat/freeze/burn/finalize) -> on W245 finalize landing: bm-a next own wave derive (W246 class: '
             'seat publish+probe leg1 B_semantics+prereg buildgen from PERPETUAL_N1_W245 tpl+five-face freeze+engine self-burn per c1010 template); '
             'if bm-c cedes/stalls >1 round -> GM re-assignment takeover lane; 15:30 bars 10-15 -> S6 papers/marks legs; S6 chain per round; '
             'no pool/board claimables (pool 0 pending, P2/P3 boards all done/closed)')
s['idle_rounds'] = 0
s['agenda_starved'] = False
s['ts'] = now_iso()
json.dump(s, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-a.json ---
hp = r'fleet\machines\bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
ack = h.get('orders_ack', [])
if isinstance(ack, list):
    for k in ('O-20261015-0025-bm-b.md',):
        if k not in ack:
            ack.append(k)
    h['orders_ack'] = ack
h['last_seen'] = now_iso()
h['round_no'] = 1009
h['now_active'] = 'r1009 watch: W245=bm-c turn; bm-a W246-class derive after W245 chain lands; S6 chain 43 legs rc0'
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = now_iso()
h['ts'] = now_iso()
h['verdict'] = 'green (watermark py_low_board_clear legal idle whitelist: engine sequential lane W245=bm-c turn, pool 0, boards closed)'
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# verify epoch int type
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
print('state round_no ->', 1010, '| heartbeat epoch int ok:', h2['heartbeat_epoch_utc'])
