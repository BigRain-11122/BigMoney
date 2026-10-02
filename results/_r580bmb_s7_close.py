# r580 bm-b S7 closeout: state, heartbeat, round report (JSON int epoch law)
import json, time, datetime, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec='seconds')
epoch = int(time.time())

# state.json (bm-b file per S5)
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
assert st['round_no'] == 578, 'round_no drift: %s' % st['round_no']
st['round_no'] = 580  # skip dead-r579 per r529 law
st['note'] = ('r580: dead-r579 diagnosis (r529 law: state 578 vs git self-label 579) + '
              'S0 surgery per-file-payload paradigm (W93 shards 4-11 landed, pool_core '
              'union 934+8 dict rows) + W94 registration revert HEALED (dead-r579 replay '
              'clobbered bm-a W94 five-face on origin, r560 family 7th instance; '
              'byte-exact restore from holding 9a9d05857 + r307 two-state assert fix; '
              'MSG-20261002-1533-bmb) + W93 12/12 burned (shards all on origin, finalize '
              'pending W92 bm-c chain order r518) + W95 seat+freeze+ignition (85th wave, '
              'bm-b 32nd owned, A 233_004..235_003 + B 57_501..57_700 both-sides arithmetic '
              'CLEAN, ADMIT rc0 single state, engine self-ignited within 2 ticks) + '
              'S6 28 legs all-green holiday no-ops (dualrun ZERO-DRIFT streak 24/3); '
              'next = W95 12/12 burn track + W93/W95 finalize after W92 lands')
st['last_round_at'] = epoch
st['last_round_ts'] = clock
st['ts'] = clock
st['updated'] = 'r580 bm-b: W94 heal + W93 12/12 + W95 freeze+ignition + S6 all-green'
st['updated_at'] = clock
with open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state.json -> round_no=%d' % st['round_no'])

# heartbeat
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
hb['verdict'] = 'burning-healthy (engine W95 burn in flight; W94 heal landed; W93 12/12 finalize pending W92)'
hb['current_task'] = 'W95 burn in flight (85th engine wave); W93/W95 finalize pending W92 bm-c chain order'
hb['cpu_cores'] = 16
try:
    import psutil
    hb['idle_ram_gb'] = round(psutil.virtual_memory().available / (1 << 30), 1)
except Exception:
    pass
with open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated ISO8601 (R262 law)'
print('heartbeat: epoch=%d (int OK) clock=%s' % (chk['heartbeat_epoch_utc'], chk['clock_read']))

# round report (bm-b file)
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
line = ('%s | r580 | dead-r579 three-face diagnosis (r529) + S0 surgery new paradigm '
        '(per-file payload onto origin tree, Tools/_r580bmb_s0_surgery.py; W93 shards '
        '4-11 + telemetry landed, pool_core union 934+8) + W94 registration revert HEALED '
        '(r560 family 7th: dead-r579 replay whole-file-snapshot clobbered bm-a W94 '
        'five-face on origin; byte-exact restore from holding 9a9d05857 via '
        'results/_r580bmb_w94_heal.py, five faces 1/1 byte-identical, r307 two-state '
        'prior-wave assert fix, MSG-20261002-1533-bmb notify bm-a) + W95 seat published '
        '(MSG-20261002-1536-bmb per r565) + W95 FREEZE five-face + self-ignition (85th '
        'engine wave, bm-b 32nd owned, A 233_004..235_003 + B 57_501..57_700 both-sides '
        'arithmetic continuation CLEAN, ADMIT receipt results/_r580bmb_w95_band_gate.py '
        'rc0; banned gate ADMIT 0) + S6 28 legs all-green holiday no-ops (paper block '
        'skipped no-new-bar LAST_BAR=2026-09-30; dualrun ZERO-DRIFT streak 24/3 before '
        'compute_audit) + CODELY 3 pit entries | W93 12/12 shards on origin (finalize '
        'pending W92 bm-c chain order r518) | W95 ignition proof = shard-0 product + '
        'shard-1 in flight (product growth law r325); pf selftest 9/9 + n1 default-wave '
        'selftest PASS on healed+extended tree; smoke 47/47; attrition scan CLEAN; '
        'orders 143/143 zero-delta (double scan); D-19 honest skip (bm-b no group tree, '
        'r481 special case) | next: W95 12/12 burn track; W93/W95 finalize after W92 '
        'finalize lands (bm-c); W96 seat per never-dry standing line\n' % clock)
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended (r580)')
