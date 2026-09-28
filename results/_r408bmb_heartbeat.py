import json, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

epoch = int(time.time())
clock = time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
h = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
h['last_seen'] = clock
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock
h['current_task'] = 'round 408 done: consolidated CEO report W2-W5 landed (four 48h clocks discharged in-window, 14212->1750->14 G1->0 G2 lawful-zero, ledger 328987 linear, 62-assert verify ALL PASS) + S6 37 legs rc=0 (pool_dualrun bm-b evidence row ZERO-DRIFT streak 1/3; scorecard family stale-takeover lawful bm-a 51min stale)'
h['round_no'] = 408
h['loop_round'] = 408
h['round'] = 408
h['verdict'] = 'healthy: smoke 26/26; W1-W5 six trial waves fully closed 0-registration honest (W2-W5 CEO report landed, W5 clock discharged 47.5h early); astock repull in-flight ETA ~04:30 (rev_osc waits panel cutoff 09-24); V3-TOURNAMENT still awaiting bm-c runner; W6 prereg bm-a in-flight; orders ack 122/122; audit idle-starvation + supply_floor standing (supply in flight: repull + V3 runner gap + W6 prereg)'
# refresh dynamic resource fields (best-effort read)
try:
    import psutil
    vm = psutil.virtual_memory()
    h['free_ram_gb'] = round(vm.available / 1024**3, 2)
    h['idle_ram_gb'] = h['free_ram_gb']
    h['free_ram_mb'] = int(vm.available / 1024**2)
    h['idle_ram_mb'] = h['free_ram_mb']
    h['cpu_util_pct'] = psutil.cpu_percent(interval=1)
    h['cpu_pct'] = h['cpu_util_pct']
except Exception:
    pass
with open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8') as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
# self-assert: epoch must be JSON int
rt = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(rt['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in rt['clock_read'] and ' ' not in rt['clock_read'].split('+')[0], 'clock_read must be T-separated'
print('heartbeat written: epoch=%d (int OK) clock=%s round=%d' % (rt['heartbeat_epoch_utc'], rt['clock_read'], rt['round_no']))
