# -*- coding: utf-8 -*-
# r918 bm-a closeout tri-write: state bump 917->918 + heartbeat refresh (fresh
# single-source stat sample) + self-verify epoch int / T-separator clock.
import json, time, subprocess, psutil
from datetime import datetime, timezone, timedelta

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())

R = 918
NOW_ACTIVE = ('r918 closed: W199 seat chain landed (probe rc0 ADMIT A 452_604..454_603 + '
              'B 454_604..454_803 staircase FIFTY-NINTH hops 1/1; seat MSG published r565 law)')
TASK = ('r919: 10-09 15:30 bars -> evening marks chain (REGIME_GUARD enforce + live.paper + '
        't35/t24 family + evening S6 rerun); W199 prereg build + five-face freeze (window '
        '<=24h from seat 15:07); PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)')
LAST_ACTION = 'r918 closeout: W199 seat chain landed + push 3a875bf43 self-verified 0/0'
ART = ('r918 products: fleet/inbox/MSG-2026-10-09-1507-bma-w199-seat.md + '
       'results/_r918bma_w199_probe.py + results/_r918bma_w199_probe_receipt.json '
       '(probe rc0 ADMIT: A 452_604..454_603 hops=1 + B 454_604..454_803 hops=1 staircase '
       'FIFTY-NINTH; leg0 196 rows tail=W198 anchor 849,945; leg4 W200+ projection A '
       '454_604..456_603 / B 454_804..455_003) + results/_r918bma_roll_w199_probe.py')
DID = ('r918: S0 fetch 0/0 clean + S0.5 orders double-scan unacked=0 + DEC bd94a27b/ORD '
       'b38eaaf8 python-raw UNCHANGED zero action + S1 smoke 49/49 + S3 main product W199 '
       'seat chain (roll script r915 bloodline one-gen anchor-cut; probe 5-leg rc0 ADMIT: '
       'leg0 196 rows tail=W198 owner=188 -> 189th wave bm-a 114th, anchor W198 finalize '
       'ledger head 849,945 cross-file prev==total; leg1 staircase FIFTY-NINTH A refused '
       'at own start by registered W198 B 452_404..452_603 -> A 452_604..454_603 hops=1 + '
       'naive B inside own-A -> reserved B 454_604..454_803 hops=1; leg2 conflicts=0; leg3 '
       'origin vacancy 4/4; leg4 W200+ projection A 454_604..456_603 / B 454_804..455_003 '
       'B-inside-A True re-derive-mandatory note) + seat MSG published + 4-file commit '
       '3a875bf43 push 0/0 self-verified + S6 38-leg rc0 bad NONE (r916 driver bloodline '
       'reuse, pre-15:30 no-new-bar honest no-op family, options-skip per O-20261009-1105) '
       '+ S7 attrition CLEAN + quartet GREEN (loop pin=8 no-op first-fire 15:18 / watchdog '
       're-registered -Force / precommit+prepush claws LF-normalized) + idle_trigger '
       '--worked (idle_rounds 0) + closeout double-scan unacked=0 + DEC/ORD recheck '
       'UNCHANGED')
ORD_SEEN = ('r918 closeout re-scan: ORD b38eaaf8 UNCHANGED vs r917 consumption -- zero '
            'delta; zero action')
DEC_SEEN = ('r918 closeout re-scan: DEC bd94a27b UNCHANGED vs r917 consumption -- zero '
            'delta; zero action')
VERDICT = ('green (r918 closed: W199 seat chain landed probe rc0 ADMIT staircase 59th; '
           'engine ALIVE idle; S6 38-leg bad NONE)')

# fresh single-source stats
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1024**3, 1)
ram_free_mb = int(round(vm.available / 1024**2))
total_ram_gb = round(vm.total / 1024**3, 1)
ram_free_pct = round(vm.available / vm.total * 100, 1)
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,memory.total',
                           '--format=csv,noheader,nounits'], capture_output=True,
                         text=True, timeout=10).stdout.strip().split('\n')[0]
    vfree_mib, vtot_mib = (int(x.strip()) for x in out.split(','))
except Exception:
    vfree_mib, vtot_mib = None, None
vfree_gb = round(vfree_mib / 1024, 2) if vfree_mib is not None else None
vfree_mb = int(round(vfree_mib * 1024**2 / 1000**2)) if vfree_mib is not None else None

# --- state-bm-a.json ---
sp = ROOT + r'\state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
prev_round = st.get('round_no', R - 1)
assert prev_round == 917, f'state round drift: {prev_round}'
st.update({
    'round_no': R, 'round': R, 'loop_round': R, 'last_round': prev_round,
    'clock_read': ts, 'ts': ts, 'last_seen': ts, 'last_run': ts, 'updated': ts,
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': epoch,
    'now_active': NOW_ACTIVE, 'current': NOW_ACTIVE,
    'current_task': TASK, 'task': TASK,
    'last_action': LAST_ACTION,
    'last_artifact': ART, 'latest_artifact': ART,
    'next_milestone': TASK, 'next': TASK,
    'did': DID, 'verdict': VERDICT, 'verify': VERDICT,
    'idle_rounds': 0, 'agenda_starved': False, 'orphan_faces': 0,
    'last_orders_seen': ORD_SEEN, 'last_decisions_seen': DEC_SEEN,
    'last_orders_at': ts, 'last_decisions_at': ts,
    'last_round_at': ts, 'last_round_at_': ts, 'last_round_ts': ts,
    'last_round_closed': ts,
    'sync': {'ts': ts, 'origin_tip': '3a875bf43', 'ahead_behind': '0/0',
             'note': 'r918 closeout: W199 seat chain push self-verified post-push fetch+rev-list'},
    'push_verified': {'ts': ts, 'origin_tip': '3a875bf43', 'ahead_behind': '0/0',
                      'note': 'r918 closeout: W199 seat chain push self-verified post-push fetch+rev-list'},
})
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- fleet/machines/bm-a.json heartbeat ---
hp = ROOT + r'\fleet\machines\bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
hb.update({
    'round': R, 'round_no': R, 'loop_round': R, 'last_round': prev_round,
    'clock_read': ts, 'ts': ts, 'last_seen': ts, 'last_run': ts,
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': epoch,
    'now_active': NOW_ACTIVE, 'current': NOW_ACTIVE,
    'current_task': TASK, 'task': TASK,
    'last_action': LAST_ACTION,
    'last_artifact': ART, 'latest_artifact': ART,
    'next_milestone': TASK, 'next': TASK,
    'did': DID, 'verdict': VERDICT,
    'idle_rounds': 0, 'agenda_starved': False, 'orphan_faces': 0, 'orphan_killed': 0,
    'last_orders_seen': ORD_SEEN, 'last_decisions_seen': DEC_SEEN,
    'last_orders_at': ts, 'last_decisions_at': ts,
    'cpu_pct': cpu, 'cpu_load_pct': cpu, 'cpu_total_pct': cpu, 'cpu_util_pct': cpu,
    'free_ram_gb': ram_free_gb, 'idle_ram_gb': ram_free_gb, 'ram_free_gb': ram_free_gb,
    'idle_ram_mb': ram_free_mb, 'ram_free_mb': ram_free_mb,
    'ram_free_pct': ram_free_pct, 'free_ram_pct': ram_free_pct,
    'total_ram_gb': total_ram_gb,
    'sync': {'ts': ts, 'origin_tip': '3a875bf43', 'ahead_behind': '0/0',
             'note': 'r918 closeout: W199 seat chain push self-verified post-push fetch+rev-list'},
    'push_verified': {'ts': ts, 'origin_tip': '3a875bf43', 'ahead_behind': '0/0',
                      'note': 'r918 closeout: W199 seat chain push self-verified post-push fetch+rev-list'},
})
if vfree_mib is not None:
    vtot_mb = int(round(vtot_mib * 1024**2 / 1000**2))
    for k in ('gpu0_free_vram_gb', 'gpu_free_vram', 'gpu_free_vram_gb', 'gpu_idle_vram',
              'gpu_idle_vram_gb', 'gpu_vram_free_gb', 'idle_gpu_vram_gb', 'idle_vram_gb',
              'vram_free_gb'):
        hb[k] = vfree_gb
    for k in ('gpu_idle_vram_mb', 'gpu_free_vram_mb', 'vram_free_mb'):
        hb[k] = vfree_mb
    for k in ('gpu_free_vram_mib', 'gpu_idle_vram_mib'):
        hb[k] = vfree_mib
    hb['gpu_total_vram_mb'] = vtot_mb
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- self-verify ---
st2 = json.load(open(sp, encoding='utf-8'))
hb2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(st2['heartbeat_epoch_utc'], int) and isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in st2['clock_read'] and 'T' in hb2['clock_read'], 'clock not T-separated'
assert st2['round_no'] == R and hb2['round_no'] == R
print('tri-write OK: round', R, '| epoch int', hb2['heartbeat_epoch_utc'],
      '| clock', hb2['clock_read'], '| cpu', cpu, '| ram_free_gb', ram_free_gb,
      '| vram_free_gb', vfree_gb)
