# -*- coding: utf-8 -*-
# r1003 bm-c closeout: state round_no+1, heartbeat, inbox W241-seat msg -> processed, round report line
import json, time, shutil, os

# 1) state round_no 1003 -> 1004
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
old_round = st.get('round_no')
assert old_round == 1003, old_round
st['round_no'] = 1004
st['last_round'] = 'r1003'
st['last_round_at'] = '2026-10-14T18:35:00+08:00'
st['last_round_ts'] = time.time()
st['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
st['heartbeat_epoch_utc'] = int(time.time())
st['current_task'] = 'W241 prereg derive landed; freeze splice = r1004 first action'
st['current_task_at'] = st['clock_read']
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round ->', st['round_no'])

# 2) heartbeat fleet/machines/bm-c.json
hp = 'fleet/machines/bm-c.json'
h = json.load(open(hp, encoding='utf-8'))
now = int(time.time())
h['last_seen'] = time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
h['ts'] = h['last_seen']
h['clock_read'] = h['last_seen']
h['heartbeat_epoch_utc'] = now
h['cpu_cores'] = 32
try:
    import psutil
    h['free_ram_gb'] = round(psutil.virtual_memory().available / 1e9, 1)
    h['idle_ram_gb'] = h['free_ram_gb']
    v = psutil.virtual_memory()
    def gpuram():
        try:
            import subprocess as sp2
            r = sp2.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], capture_output=True)
            return int(r.stdout.decode().strip().splitlines()[0])
        except Exception:
            return None
    h['gpu_free_vram_mib'] = gpuram()
    h['gpu_free_vram_mb'] = h['gpu_free_vram_mib']
except Exception as e:
    print('psutil face skip:', e)
h['verdict'] = 'r1003: W241 prereg derive landed (PERPETUAL_N1_W241_PREREG.md 29302B, banned ADMIT rc0, receipt _r1003bmc_w241_prereg_derive_receipt.json); freeze splice = r1004 first action; S6 chain rc0 (dualrun streak 51, bars 10-14 pending sina, daily REPORT-2026-10-14 regenerated)'
h['current_task'] = 'W241 freeze splice (r1004 first action)'
h['idle_rounds'] = 0
h['agenda_starved'] = False
# idle_trigger --worked semantics: real output produced this window
its = 'results/idle_trigger_state.bm-c.json'
it = json.load(open(its, encoding='utf-8'))
it['streak'] = 0
it['last_touch'] = time.time()
it['last_declare'] = 'worked'
json.dump(it, open(its, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
d2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(d2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
print('heartbeat ok epoch=', d2['heartbeat_epoch_utc'])

# 3) inbox: W241 seat msg -> processed
src = 'fleet/inbox/MSG-20261014-1755-bmc-w241-seat.md'
dst = 'fleet/inbox/processed/MSG-20261014-1755-bmc-w241-seat.md'
if os.path.exists(src):
    shutil.move(src, dst)
    print('seat msg -> processed')

# 4) round report line (canonical path per r750 law)
rp = 'logs/iteration-loop/round_reports-bm-c.md'
row = ('2026-10-14T18:35:00+08:00 | r1003 | bm-c | '
 'W241 PREREG DERIVE LANDED (M12 trigger open: W240 finalize landed 22c6c3374 K=525,920/ledger 952,335) -- '
 'PERPETUAL_N1_W241_PREREG.md 29,302B machine-generated SUB from frozen W240 tpl 22c6c3374 '
 '(line-anchored editor, facts live machine-read: probe ADMIT A 547501..549500/B 541004..541203 hops=0 both, '
 'seed-decoupled A-continuation face second consecutive + B third consecutive, n1_bands live 238 rows owner 230 bmc 66+candidate=67th, '
 'ledger 950,135+2,200=952,335 EXACT/K 525,920 EXACT, A p95 0.316, se_mu 0.000338, K-lift 0.0, line 1.1932, '
 'W242+ projection A 549501..551500/B 541204..541403 both CLEAN hops=0) + banned_direction_gate ADMIT rc0 + '
 'derive receipt _r1003bmc_w241_prereg_derive_receipt.json + satengine alive burns=[] queue=[] + orphan face 3/10 zero-kill (all non-BigMoney lanes) + '
 'S0.5 ORD unacked=0 (89/89) + DEC hash-hold c61d7884 + S6 chain rc0 (dualrun ZERO-DRIFT streak 51/456, compute_audit FLAG pool_starvation=supply_floor answered-by-chain W241 standing, '
 'watermark insufficient_history honest, bars 10-14 pending sina cutoff 10-13 = papers no-op, regime rc0 crash10d+breadth triggers disclosed, '
 'clock ORANGE_COOL cutoff 10-13, daily REPORT-2026-10-14 regenerated, token delta=0) + attrition CLEAN + claws idempotent + pin=5 no-op + '
 'seat msg archived processed '
 '| smoke 49/49 at S1 + freeze UNBLOCKED chain: derive DONE this window, freeze splice (five-face, clone of _w240bma_freeze_edits.py lineage) = r1004 FIRST ACTION + '
 'wave2 watch runner PID 24076 alive GPU 100% MV-legal '
 '| behind-origin=0 | next r1004: W241 freeze splice -> engine self-ignite watch -> finalize -> W242 seat probe')
with open(rp, 'a', encoding='utf-8') as f:
    f.write(row + '\n')
print('round report appended')

# 5) cleanup temp dumps (non-estate scratch)
for t in ['_r1003_tpl_dump.md', '_r1003_l2_dump.txt', '_r1003_w239_tpl.md', '_r1003bmc_linemap.py', '_r1003bmc_count_probe.py']:
    if os.path.exists(t):
        os.remove(t)
        print('cleaned', t)
print('done')
