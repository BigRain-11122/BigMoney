import json, time, datetime, subprocess

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 516
st['last_round'] = 515
st['loop_round'] = 515
st['did'] = ('r515: LOWAMP-P2 integration + claim-race resolution (round product): committed 10/16 cell burn products '
             '(LAT3 legacy pair cells+cont, pool_core_samples, daemon state) -> rebased 3 commits onto moved origin '
             '(2 stale push-fault claims yielded to bm-c per r297, conflicts resolved take-origin) -> push delivered '
             '(c7cf315ba..2134412d9, 0/0 convergence); daemon push-blockage root-cleared (r513 stale-view cured); '
             'LAT3-DEEP-BASE takeover: bm-c claim 12:58:09 + bm-c push-race (their r314 addendum disclosed) -> our daemon '
             're-claimed 13:04:09 pushed to origin + re-burn launched (pid 45100, deterministic duplicate disclosed, '
             'r499 union law on AA if bm-c product surfaces); audit trio ran (dualrun DRIFT=claim-race observation-phase '
             'streak reset 0; audit flags supply_gap/ignition_sla transient; watermark py_low_with_work_cands=P2 in-flight transient)')
st['verify'] = ('smoke 47/47; orders 136/136 zero-diff; D-19 MATCH-unchanged 753F99E8; attrition 4 ledgers CLEAN; '
                'loop pin Running + watchdog Ready; products on origin 21 files ls-tree verified')
st['next'] = ('r516: LOWAMP-P2 finalize when 18/18 done (harvest flip + sec.7/sec.8 backfill + append_ledger +2008 '
              '+ E1 known-answer reconciliation r492 law BEFORE consuming verdict); monitor daemon completion of '
              'LAT3-DEEP-BASE + LAEDGE x3 + NULLS + SENS claims; T-139 stage-B REV stock prereg draft per r513 D6 probe')
st['current_task'] = 'LOWAMP-P2 burn near-complete: 10/16 cells on origin + LAT3-DEEP-BASE re-burn in flight; finalize gate next round'
st['last_round_at'] = now
st['last_round_ts'] = now
st['updated'] = now
json.dump(st, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# heartbeat
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = now
hb['current_task'] = st['current_task']
hb['round_no'] = 516
hb['loop_round'] = 515
hb['round'] = 515
try:
    import psutil
    hb['cpu_pct'] = psutil.cpu_percent(interval=0.3)
    hb['cpu_util_pct'] = hb['cpu_pct']
    vm = psutil.virtual_memory()
    hb['free_ram_gb'] = round(vm.available / (1024**3), 1)
    hb['idle_ram_gb'] = hb['free_ram_gb']
    hb['cpu_cores'] = psutil.cpu_count()
    hb['cores'] = hb['cpu_cores']
except Exception:
    pass
epoch = int(time.time())
assert isinstance(epoch, int)
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now
hb['verdict'] = 'r515 done: P2 products delivered, burn in flight, finalize next'
json.dump(hb, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# round report line
line = (f"{now} | r515 | P2整合+claim竞态收敛：10/16 cell产物送达origin（rebase 3 commit、2滞留claim按r297让bm-c、"
        f"push c7cf315ba..2134412d9 0/0）+LAT3-DEEP-BASE接管（bm-c push-race实况、我方daemon 13:04:09 re-claim落origin+重烧在飞pid45100确定性重复披露）"
        f"| 验证：smoke 47/47、orders 136/136、D-19 MATCH、attrition CLEAN、audit三腿照录（dualrun DRIFT=claim竞态观察相streak清零、watermark py_low=P2在飞暂态）"
        f"| 本地未达 origin commit 数=0 | 下轮：18/18 done后finalize（sec.7/8+ledger +2008+E1对账r492律）+LAEDGE/NULLS/SENS续烧监控")
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('state + heartbeat + report OK; epoch=', epoch, 'int:', isinstance(epoch, int))
