import json, time, io, subprocess

# ---- state.json (bm-b uses root state.json per S5 lane rule) ----
now_local = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st = json.load(io.open('state.json', encoding='utf-8'))
st['round_no'] = 458
st['note'] = (
    "r458 CLOSED: S6 33-leg mid-session chain (32xrc0 + lhb rc=3 standing quarantine r229 7th obs; bar-gated 4 legs "
    "live.paper/t35/t24x2 deferred to post-15:30 rounds; dualrun ZERO-DRIFT 49/3) -- r458 (this round): PRODUCT = "
    "T-103 s2 chain #2 ETF-OPS-BP2 prereg FROZEN commit 814269d75 (BP1 r397 family-lesson exit-discipline transplant "
    "pointer executed, not a rerun: calendar-DCA monthly-entry zero-skill claim + BP1 exit stack verbatim transplant "
    "trend_sl>hard_sl>tp2>tp1; 15 member-cells 5 members x (P1,P2) {(5,10),(6,12),(8,15)}pct; PRIMARY gate = "
    "window-paired exit-discipline increment median paired_diff>0 AND bootstrap CI95 excludes 0 over {126,252,504}td "
    "virtual windows x all starts, same-entry DCA-hold control, judged face x2; seed etf_ops_bp2=20294100 R250 "
    "same-commit band rg-scan clean; F-04 MSG-20260930-1150 dual-signal; evidence_cutoff=2026-09-29 five-member panel "
    "fresh-probed rows 5252/3487/3290/2406/1426 -- T-111 refresh leg closed BP1-era no-refresh gap) + inbox "
    "MSG-20260930-1045 bm-c SLOT-10 berth declare processed (zero overlap) + orders 0 unacked double-scan clean -- "
    "NEXT r459: BP2 runner scripts/etf_ops_bp2.py build (BP1 machinery inheritance + calendar mask + "
    "vectorized-across-starts window-paired engine + brute-force reference selftest) -> selftest -> empirical burn "
    "(<=5min inline r397 precedent / >5min pool R41) -> finalize -> verdict -> three exits; same-day 15:30 "
    "post-close unlock (09-30 bars -> live.paper/t35/prospect accrue); r460 = 5x HANDOVER window"
)
st['last_round_at'] = now_local
st['last_round_ts'] = now_local
st['ts'] = now_local
st['updated'] = now_local
json.dump(st, io.open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json round_no ->', st['round_no'])

# ---- heartbeat fleet/machines/bm-b.json ----
hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
epoch = int(time.time())
hb['last_seen'] = now_local
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_local
hb['current_task'] = ("r458: T-103 chain #2 ETF-OPS-BP2 prereg FROZEN (exit-discipline transplant: calendar-DCA + "
                      "BP1 exit stack; 15 cells; window-paired primary gate; seed 20294100; cutoff 2026-09-29) + "
                      "S6 33-leg mid-session green")
try:
    import psutil
    vm = psutil.virtual_memory()
    hb['free_ram_gb'] = round(vm.available / 1024**3, 1)
    hb['idle_ram_gb'] = hb['free_ram_gb']
    hb['ram_free_gb'] = hb['free_ram_gb']
    hb['total_ram_gb'] = round(vm.total / 1024**3, 2)
    hb['cpu_util_pct'] = round(psutil.cpu_percent(interval=1), 1)
except Exception as e:
    print('psutil sample skip:', e)
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    mb = int(float(r.stdout.strip().splitlines()[0]))
    hb['gpu_free_vram_mb'] = mb
    hb['gpu_free_vram_gb'] = round(mb / 1024, 1)
    hb['gpu_idle_vram_gb'] = hb['gpu_free_vram_gb']
except Exception as e:
    print('gpu sample skip:', e)
hb['round_no'] = 458
hb['round'] = 458
hb['loop_round'] = 458
hb['verdict'] = ("healthy: S6 33-leg mid-session green (lhb rc3 standing quarantine only) + product freeze landed "
                 "(ETF-OPS-BP2 prereg commit 814269d75, seed registered, F-04 declared) + board 0 open + pool "
                 "W13 bm-a in-flight + supply heal map live (W13/SLOT-10/MF_IC/BP2-runner-r459); no red, no unacked "
                 "orders, smoke 26/26")
hb['last_round_at'] = now_local
json.dump(hb, io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify epoch int + clock T-format (R170/R178/R262 laws)
chk = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be ISO8601 T-separated'
print('heartbeat OK: epoch', chk['heartbeat_epoch_utc'], 'type', type(chk['heartbeat_epoch_utc']).__name__,
      '| clock', chk['clock_read'], '| ram', chk['free_ram_gb'], '| gpu_mb', chk['gpu_free_vram_mb'])
