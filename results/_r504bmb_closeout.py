"""r504 bm-b closeout: state.json + heartbeat + round-report line append.
Self-verifies: json round-trip, epoch int type (R170/R178 law), clock T-separator (R262 law)."""
import json, time, datetime

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# ---- 1. state.json (bm-b ledger) ----
sp = REPO + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
assert st['machine_id'] == 'bm-b'
st['round_no'] = 504
st['note'] = ('r504: T-134 board JSON repair (r312 note segment appended outside string -> fleet-wide '
              'parse break; folded in-string, -3 bytes, zero content loss, origin 7e4df5568) + '
              'push-deadlock broken 2nd time (r503 recipe: runtime snapshot ride 3 commits, rebase '
              '1 UU pair resolved rolling-ledger/append-log union, r501 false-refusal net path) -> '
              'daemon claim OK 13:02 MOM SHARD-12 launch; watermark RED root-caused to stale-view '
              '+deadlock, audit supply_gap/supply_floor = stale-view false red (origin truth 10 ready); '
              'S6 42 legs rc0; D-19 753F99E8 MATCH-unchanged')
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at'):
    st[k] = now_iso
# D-19 watermark keys unchanged (753F99E8 MATCH this round)
assert st['last_decisions_sha'] == '753F99E81A27DB3E1B4F2C76CD991CA50D52B80AA7FAA63D6412CC2DA1F5FB01'
with open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')
json.loads(open(sp, encoding='utf-8').read())
print('state.json ok round_no=%d' % st['round_no'])

# ---- 2. heartbeat fleet/machines/bm-b.json ----
hp = REPO + r'\fleet\machines\bm-b.json'
h = json.load(open(hp, encoding='utf-8'))
assert h['machine_id'] == 'bm-b'
h['last_seen'] = now_iso
h['clock_read'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['current_task'] = 'r504 closeout: T-134 board JSON repair landed + push-deadlock broken (claim OK 13:02), MOM/LOWAMP-P2 pool flowing'
h['round_no'] = 504
h['loop_round'] = 504
h['verdict'] = ('r504 products: T-134 ticket JSON syntax repair (origin 7e4df5568, board parse restored) '
                '+ daemon push-deadlock broken (3-commit ride, 1 UU pair union-resolved) -> MOM SHARD-12 '
                'claim+launch 13:02; watermark RED root cause = stale-view + deadlock, remediated; '
                'S6 42 legs rc0')
h['last_round_at'] = now_iso
h['last_round_ts'] = now_iso
with open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write('\n')
v = json.loads(open(hp, encoding='utf-8').read())
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert 'T' in v['clock_read'], 'clock_read must be T-separated (R262)'
print('heartbeat ok epoch=%d clock=%s' % (v['heartbeat_epoch_utc'], v['clock_read']))
