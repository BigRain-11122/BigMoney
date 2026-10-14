# -*- coding: utf-8 -*-
"""r994 bm-a closeout: state round_no, heartbeat (orders_ack +7, idle --worked), round report."""
import json, time, datetime, io, sys

# --- state round_no +1 ---
with open('state-bm-a.json', encoding='utf-8') as f:
    s = json.load(f)
s['round_no'] = int(s.get('round_no', 0)) + 1
with open('state-bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print('state round_no ->', s['round_no'])

# --- heartbeat ---
with open('fleet/machines/bm-a.json', encoding='utf-8') as f:
    h = json.load(f)
NEW_ACK = ['O-20261013-0951-bm-b', 'O-20261014-0030-bm-b', 'O-20261014-0312-bm-c',
           'O-20261014-0040-bm-b', 'O-20261014-0942-bm-b', 'O-20261014-0948-bm-b',
           'O-20261014-0949-bm-b']
ack = h.get('orders_ack', [])
for a in NEW_ACK:
    if a not in ack:
        ack.append(a)
h['orders_ack'] = ack
h['orders_ack_note'] = 'r994: +7 acks (0951/0030 bm-a knowledge-face self-audit done; 0040/0942/0948 bm-b-target; 0312 bm-c-target; 0949 fleetwide: bm-a llama-server :8090 35B resident ALIVE self-check PASS, queue-water audit = satengine rc0 alive queue0 + pool_ready 0 < floor3 starvation flag standing=W241 re-arm window, supply fix = W241 freeze slice next round)'
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['round_no'] = s['round_no']
now = datetime.datetime.now().astimezone()
h['ts'] = now.isoformat(timespec='seconds')
h['clock_read'] = now.isoformat(timespec='seconds')
h['heartbeat_epoch_utc'] = int(time.time())
h['last_seen'] = now.isoformat(timespec='seconds')
h['last_round_at'] = now.isoformat(timespec='seconds')
h['current_task'] = 'r994 S6 full-chain + orders ack + W241 re-arm assessment'
h['last_artifact'] = 'docs/live_usage/LIVE-2026-10-14.md + docs/daily_report/REPORT-2026-10-14.md (2026-10-14 17:3x)'
h['verdict'] = 'green (wm-red=false; satengine ALIVE rc0 idle queue0; llama-server :8090 35B resident ALIVE per O-0949 s1; pool_starvation=W241 standing -> supply fix next round; orphan 0/38; dualrun streak 26; S6 25 legs rc0)'
h['orphan_face'] = '0/38'
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
print('heartbeat ok, acks:', len(ack))

# --- round report ---
line = ('2026-10-14 17:3x | r994 bm-a | S0-1 anchor bm-a + orphan 0/38; S0 fetch behind=0 (dirty=runtime state faces only); '
        'S0.5 orders +7 acked (O-0951/O-0030 bm-a knowledge-face load self-audit CPU-lane open per CEO 1013 order, O-0949 fleetwide: '
        'llama-server :8090 35B resident ALIVE self-check PASS s1 + queue-water audit honest, 0312/0040/0942/0948 target-machine items acked no-op for bm-a); '
        'S1 smoke 49/49 PASS; S2 boards empty (jobs 0 / fleet-tasks 0 open / backlog rows all claimed); S3 watermark GREEN lane=healthy next_pick=claimed(moneyflow IC batch waits panel first-pull 2152/5222 in-flight detached); '
        'satengine ALIVE rc0 idle queue0; verdict chain consumption VERIFIED already closed by r933 (N2U3 judged-NEGATIVE E65) + r935 (W19 three-axis X/S/T adjudication CLOSED E66, 48h CEO clock due 10-16 13:49); '
        'compute_audit flags pool_starvation+supply_floor (ready 0<3) -> W241 waits-upstream disarmed after W240 finalize r993 -> W241 freeze slice = next-round P0 supply fix; '
        'S6 25-leg full chain rc0: dualrun ZERO-DRIFT streak26, watermark probe py_low_board_clear legal-idle, bars 10-14 honest pending-upstream (sina late-bar, cutoff 10-13), '
        'thermo DONE, dualarm no-op (bm-b lane), zt_pool/lhb/heat no-op covered, scorecard/clock/daily_scorecard/REPORT-2026-10-14/LIVE-2026-10-14/dashboard/token regenerated, paper legs gated no-new-bar legal skip; '
        'idle --worked (orders ack + chain burn + supply assessment); evidence: smoke 49/49 + S6 leg outputs + heartbeat r994 | next: W241 perpetual-N1 freeze window (perpetual_faces.py L7822 pre-seat probe leg4) as P0 supply fix round')
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(line + '\n')
print('report appended')

# self-verify heartbeat epoch int
with open('fleet/machines/bm-a.json', encoding='utf-8') as f:
    v = json.load(f)
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in v['clock_read'], 'clock_read must be T-separated'
print('self-verify PASS')
