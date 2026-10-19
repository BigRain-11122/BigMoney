import io, json, time, datetime, subprocess, os

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')
iso = iso[:-2] + ':' + iso[-2:]
ts = iso
epoch = int(time.time())

st_path = os.path.join(REPO, 'state-bm-c.json')
st = json.load(io.open(st_path, encoding='utf-8'))
prev_round = st.get('round_no')
st['round_no'] = 1138
st['last_seen'] = iso
st['clock_read'] = iso
st['ts'] = iso
st['heartbeat_epoch_utc'] = epoch
st['current_task'] = 'r1137 closeout (W282 prereg freeze product window)'
st['current_task_at'] = iso
st['current_task_ts'] = iso
st['activity_now'] = ('W282 prereg FROZEN (research/PERPETUAL_N1_W282_PREREG.md); next = W282 five-face splice '
                      '(pf row + n1 WAVE_CONFIGS + materializer + print) then engine self-burn 12/12 -> sixgate -> '
                      'finalize ledger 1,044,735 / K 618,320 -> fivekeys -> W283 seat')
st['did'] = ('W282 per-wave prereg FREEZE (derive from frozen W281 pre-run face, 59 count-gated rules, banned_direction_gate ADMIT rc0) '
             '+ S6 light 10/10 rc0 + S7 attrition/loop/claws + orphan face=0')
st['verdict'] = ('green r1137 product window: W282 prereg FREEZE (A 635_701..637_700 32nd A-hop / B 637_701..637_900 own-A cascade, '
                 'chain K 616,120->618,320 proj, ledger 1,042,535->1,044,735 proj); next = r1138 splice')
st['agenda_starved'] = False
st['idle_rounds'] = 0
json.dump(st, io.open(st_path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)
json.loads(io.open(st_path, encoding='utf-8').read())
assert isinstance(st['heartbeat_epoch_utc'], int)

hb_path = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
hb = json.load(io.open(hb_path, encoding='utf-8'))
hb['last_seen'] = iso
hb['ts'] = ts
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['current_task'] = 'W282 prereg freeze done; W282 five-face splice next'
hb['cpu_cores'] = 32
hb['free_ram_gb'] = 1.7
hb['free_vram_mb'] = 14276
hb['verdict'] = 'green: W282 prereg frozen (635_701..637_700 / 637_701..637_900); splice next'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
json.dump(hb, io.open(hb_path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)
check = json.loads(io.open(hb_path, encoding='utf-8').read())
assert isinstance(check['heartbeat_epoch_utc'], int) and 'T' in check['clock_read']

line = ('%s | r1137 | P0=W282 PREREG FREEZE: research/PERPETUAL_N1_W282_PREREG.md derived from the frozen W281 pre-run face '
        '(git show f51afd09ad:..., blob bit-identical) via results/_r1137bmc_prereg_derive_w282.py (59 ordered count-gated rules; '
        'zero-hit fail-closed; residual-token scan clean; MUST/MUST-NOT both green) -- bands A 635_701..637_700 (32nd consecutive A-hop, '
        '1-hop walk, naive A 635_501..637_500 refused by REGISTERED W281 B 635_501..635_700, base==B tail 635_700+1) / B 637_701..637_900 '
        '(33rd above-own-A, own-A reservation cascade, base==own-A tail 637_700+1); chain anchors live-read from W281 fivekeys '
        '(ledger 1,042,535 / K 616,120 / mu -0.09283133 / sigma 0.24507389 / p95 0.3228 / se_mu 0.000312) -> projections '
        'K 618,320 / ledger 1,044,735 / n_eff 1,042,535; sec.5 item5 W283+ projection carries the W282 leg4 machine receipt '
        '(A naive 637_701..639_700 hops=0, B naive 637_901..638_100 inside projected A) | gates: banned_direction_gate ADMIT rc0, '
        'src blob identity, fivekeys all_pass, seat receipt ADMIT (271 owner rows / 100 bm-c rows / ordinal 272) | '
        'S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51 / audit FLAG pool_starvation+supply_floor [board clear, legal idle] / '
        'watermark py_low_board_clear / update_daily 0 / regime rc0 / clock CALL-2026-10-19 / fund_premium no-op / b_layer rc0 / '
        'REPORT-2026-10-20 / token delta=0) | 当前活=W282 prereg frozen, splice next | '
        '最近实物=research/PERPETUAL_N1_W282_PREREG.md (2026-10-20T03:5x) | 下个里程碑=W282 five-face splice + engine burn 12/12 (窗 ≤48h) | '
        '本地未达 origin commit 数=0\n')
rp = os.path.join(REPO, 'round_reports-bm-c.md')
with io.open(rp, 'a', encoding='utf-8', newline='') as fh:
    fh.write(line)
print('state round_no', prev_round, '->', st['round_no'], '| heartbeat epoch int ok | report appended')
print(iso)