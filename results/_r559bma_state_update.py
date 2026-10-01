# -*- coding: utf-8 -*-
# r559 S7 closeout: targeted JSON field updates (whole-file re-dump forbidden --
# round-trip non-identical per probe; regex single-field replaces only).
import json, re, sys

CLOCK = '2026-10-02T06:11:52+08:00'
EPOCH = 1790921513

def set_str_field(t, key, val):
    esc = json.dumps(val, ensure_ascii=False)[1:-1]
    pat = re.compile(r'("%s": ")([^"]*)(")' % re.escape(key))
    n = pat.subn(lambda m: m.group(1) + esc + m.group(3), t, count=1)
    if n[1] != 1:
        sys.exit('FIELD NOT FOUND: ' + key)
    return n[0]

def set_num_field(t, key, val):
    pat = re.compile(r'("%s": )(-?[0-9.]+)' % re.escape(key))
    n = pat.subn(lambda m: m.group(1) + str(val), t, count=1)
    if n[1] != 1:
        sys.exit('NUM FIELD NOT FOUND: ' + key)
    return n[0]

# ---- state-bm-a.json ----
p = 'state-bm-a.json'
t = open(p, 'rb').read().decode('utf-8')
t = set_num_field(t, 'round_no', 560)
t = set_num_field(t, 'last_round', 559)
t = set_str_field(t, 'did',
    'r559: r554-r558 five-crash adoption window (state/heartbeat stale 03:37-04:05, '
    'git self-labels to r558; liveness three-check zero live sessions per r529 law) '
    '-> heritage adoption (r558 W52 yield MSG-0615 delivered with supersession addendum '
    '+ 9 r558 evidence tools + dangling-ref closure per r322; S0 surgical bb63f47c59 '
    '20-payload dual-state-asserted; r524 bulk checkout 49 origin-owned faces) '
    '+ W54 FREEZE one-commit bdc36af9ea (43rd engine wave, bm-a 13th owned, A '
    '151_004..153_003 / B 46_601..46_800 both arithmetic zero-skip, three-machine '
    'cross-validated, ADMIT receipt _r559bma_w54_band_gate.py, banned ADMIT, selftest '
    'n1/pf/engine green, origin slot vacancy machine-checked, yield-guard surgical push) '
    '+ tick self-ignition live (shard-0 06:02:20 <1min post-push, 9/12 at 06:11)')
t = set_str_field(t, 'verify',
    'band gate ADMIT rc0 (leg0 52-keys + leg0b prose + leg1 both-CLEAN + leg2 '
    'first-clean==arith + leg3 + N3-R1 + probe-cluster + origin vacancy) + banned ADMIT '
    'rc0 + n1 selftest PASS (W54 leg) + pf 8/8 + engine 8 legs + smoke 47/47 + S6 32 '
    'legs rc0 (dualrun streak 27, audit zero flags, holiday honest no-ops, two rc=2 = '
    'missing-subcommand usage errors, direct rerun healed) + attrition CLEAN + claw '
    'MATCH + loop pin=8 + watchdog present + push delivery ls-tree self-proof 28 files')
t = set_str_field(t, 'next',
    'W54 12/12 harvest commit (~06:2x) -> finalize one-pass chain-gated on bm-c W53 '
    'finalize (FAIL-CLOSED r307; prev=live-head derive per r518); W55 freeze window '
    'observation (B-side 47_000 registry hit = skip-family warning machine-proven); '
    'T-140 LOWAMP-P3 NULLS on bm-c burn line; T-141 engine line continues')
t = set_str_field(t, 'current_task',
    'W54 engine burn in flight (9/12, tick self-ignited); finalize chain-gated on W53')
t = set_str_field(t, 'last_round_at', CLOCK)
t = set_str_field(t, 'updated', CLOCK)
t = set_str_field(t, 'last_round_ts', CLOCK)
open(p, 'wb').write(t.encode('utf-8'))
print('state-bm-a.json updated (round_no 560, last_round 559)')

# ---- fleet/machines/bm-a.json (heartbeat) ----
p = 'fleet/machines/bm-a.json'
t = open(p, 'rb').read().decode('utf-8')
t = set_str_field(t, 'last_seen', CLOCK)
t = set_str_field(t, 'clock_read', CLOCK)
t = set_str_field(t, 'current_task',
    'r559: r558 heritage adoption (W52 yield MSG + tools) + W54 FREEZE bdc36af9ea + '
    'tick burn 9/12 in flight; S6 chain rc0')
t = set_str_field(t, 'task',
    'r559 W54 freeze+burn (43rd engine wave, bm-a 13th owned; A 151_004..153_003 / '
    'B 46_601..46_800 both arithmetic continuation, ADMIT, three-machine cross-validated)')
t = set_num_field(t, 'cpu_pct', 0.0)
t = set_num_field(t, 'free_ram_gb', 52.7)
t = set_num_field(t, 'gpu_free_vram_gb', 5.7)
t = set_str_field(t, 'verdict', 'loaded_ok')
t = set_num_field(t, 'heartbeat_epoch_utc', EPOCH)
t = set_num_field(t, 'round_no', 559)
open(p, 'wb').write(t.encode('utf-8'))
print('heartbeat updated')

# json.loads self-proof (F7 fields: epoch int + T-sep clock)
s = json.load(open('state-bm-a.json', encoding='utf-8'))
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h['clock_read'] and ' ' not in h['clock_read'], 'clock must be T-separated'
print('self-proof OK: epoch int', h['heartbeat_epoch_utc'], '| clock', h['clock_read'],
      '| state round_no', s['round_no'], 'last_round', s['last_round'])
