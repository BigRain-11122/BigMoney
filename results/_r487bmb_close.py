import json, time
from datetime import datetime

# --- heartbeat fleet/machines/bm-b.json ---
hb = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
now = datetime.now().astimezone().isoformat(timespec='seconds')
hb['last_seen'] = now
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now
hb['round_no'] = 487
hb['round'] = 487
hb['loop_round'] = 487
hb['current_task'] = 'T-133 s2: N1-W2 wave 6/12 done (bm-b shards 8-11 burned multicore 22s each); finalize pending all-12; W3 band supply next'
hb['verdict'] = ('healthy: r487 O-2355 bm-b multicore law fully landed (N1 r486 + ems19/face_b22 carried commits + '
                 'pool workers_plan code-backed fix + 22s@8w vs 2min serial live proof) + autofill 2-min S4U '
                 're-registered; WM RED idle-low-cpu remediation in flight (cadence fix + claims racing)')
if 'O-2026-09-30-2355-bm-a.md' not in hb.get('orders_ack', []):
    hb['orders_ack'].append('O-2026-09-30-2355-bm-a.md')
hb['n_orders_ack'] = len(hb['orders_ack'])
hb['last_round_at'] = '2026-10-01T01:5x'
hb['last_round_ts'] = now
json.dump(hb, open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
e = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))['heartbeat_epoch_utc']
assert isinstance(e, int), 'epoch must be int'

# --- state.json ---
st = json.load(open(r'state.json', encoding='utf-8'))
st['machine_id'] = 'bm-b'
st['round_no'] = 487
st['note'] = ('r487: O-2355 acked -- bm-b multicore law fully landed (N1 runner r486 + crashed-session ems19/face_b22 '
              'commits rebase-carried+pushed + 12xN1W2 pool workers_plan declaration->code fix + 4 shards inline '
              'burned 22s@8workers vs ~2min serial) ; T-133 s2 N1-W2 6/12 done (bm-b 8-11 + bm-a 0-1; 2-7 in flight '
              'on bm-a), finalize pending; monthly first-round triple landed (science_audit 4-paper enforce=REGIME v3 '
              'date-gate legit activation + BRIEF-202609 + SELF-REVIEW-202609 P1x2 findings honest); D-19 fresh-read '
              'consumed 7 new decisions (sha 21B5C469->ED4E0EAB; D-02 Bonsai observe kept + T-135 night-window trigger '
              'not met 2150MB<9000; D-03 consumption canon = bm-b r481 recipe already conformant, acked); WM RED '
              'runnable-work-idle-low-cpu remediation: bm-b autofill cadence 10->2min S4U re-registered (T-134 s1 '
              'bm-b gap closed, register script S4U principal fixed) + claim races yielding healthy + LOWAMP runner '
              'sha updated by bm-a (9538b4e2 != crashed 5da5664a); next slice: N1-W2 all-12 -> finalize merge K=4520 '
              '-> W3 supply per law sec.4; astock refresh in flight (data gate for EXCLUSION/FACEB)')
st['last_round_at'] = '2026-10-01T01:5x'
st['last_round_ts'] = now
st['ts'] = '2026-10-01 01:5x'
st['last_decisions_sha'] = 'ED4E0EABF941B4299A6F26B243082EE74A83517B462D352D9C047F95A49A1F07'
st['last_decisions_at'] = now
st['updated_at'] = now
json.dump(st, open(r'state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('heartbeat+state written; epoch int ok:', e)
