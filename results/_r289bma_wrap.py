import json, time, subprocess
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
now_ts = now.strftime('%Y-%m-%d %H:%M:%S')
epoch = int(time.time())

cpu_pct = 15.0; free_ram_gb = 50.0; cores = 32
try:
    import psutil
    cores = psutil.cpu_count(logical=True)
    cpu_pct = psutil.cpu_percent(interval=2)
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
gpu_free_gb = 5.4
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10)
    if out.returncode == 0 and out.stdout.strip():
        gpu_free_gb = round(float(out.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass

REPORT_LINE = (
    f"{now_ts} | R289 bm-a (dept:research+fleet) | "
    "WM first-line verdict: GREEN (red=false lane healthy; py_low_with_work_cands 13.7% = legitimate ordered supply: "
    "CN-TREND 4-worker burn in flight since 02:10 (pid1256+4 spawn workers ~93% CPU each, ~50min wall vs 5-8min plan est = "
    "serial-null phase slower than plan, honest note, autofill lane owns it) + CENSUS-FUS-S2-W1 claimed queued behind "
    "= supply chain burning not stalled, O-2320 quench line 3 batches tonight) | "
    "S0.5 double-scan clean (fleet/orders diff 0; group docs/orders.md FULL-FILE scan zero new @BigMoney lines post-O-0302; "
    "decisions.md D-20260927-01..05 no new lines after R288 audit) | "
    "S2 boards: job_list empty + fleet/tasks zero open tickets (32 claimed in-flight) + post_review 1323 rows 0-X | "
    "MAIN (S3 closed loop = T-87 s2 queue#3 folklore gate): DIGEST-20260927-kline-folklore.md delivered "
    "(fetch 8: MBAlib x4 SUCCESS canonical patterns morning-star/red-three-soldiers/dark-cloud/three-crows with "
    "terminal quantified formulas; dead-ends honest: zh wiki K-xian+candlestick=redirect stubs, baidu laoyatou=empty "
    "return, MBAlib laoyatou=404) -> five-element convergence: definition STRONG 4/4 quantifiable (THS/analyst terminal "
    "formulas = industry-grade folklore encoding), entry MEDIUM, stop MEDIUM (pattern-extreme convention), exit NONE, "
    "sizing NONE -> GATE=PASS with 3 boundary disclosures (exit/sizing no community consensus = prereg "
    "engineering-frozen params labeled non-folklore; bearish patterns in T+1 long-only domain = exit/skip signal face "
    "only; high-crowding annotation + RANDOM_LARGE_SAMPLE_LAW binding) | SCHOOL_SUPPLY_S1.md row13 + queue#3 + sec4 "
    "ledger updated; laoyatou family sources-blocked = gate-not-judged next wave | "
    "S6 22 legs rc=0 (audit CLEAN v2.3 flags[] pool-supply-gap=2-ready-queued, WM probe batch-alive, daily no-op "
    "cutoff 09-24 mid-autumn holiday weekend, regime ORANGE breadth 0.77, clock CALL-2026-09-24 ORANGE_COOL 4 sleeves "
    "0 activated, weekend no-ops/throttles honest, scorecard 6/28/7, report regen, token delta 0; paper legs skipped "
    "no-new-bar) | smoke 25/25 | loop Running/watchdog Ready, inbox empty | "
    "next: CN-TREND harvest three-piece on landing (prereg s7/s8 + post_review row + attrition per r285 law, "
    "bm-a-face-governs per r288 ruling) + censusfus autofill burn then harvest; CN-KLINE-PATTERN-P1 prereg draft per "
    "DIGEST boundary disclosures [via bm-a]"
)

with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(REPORT_LINE + '\n')

sp = 'state-bm-a.json'
with open(sp, encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 289
st['did'] = ("R289: T-87 queue#3 K-line folklore gate PASS (DIGEST-20260927-kline-folklore + SCHOOL_SUPPLY_S1 row13/"
             "queue/sec4 ledger) + S6 22 legs rc=0 + smoke 25/25 + orders/decisions double-scan zero-new")
st['verdict'] = 'ok'
st['next'] = ("CN-TREND harvest three-piece on landing (prereg s7/s8+post_review+attrition, r285 law, bm-a face "
              "governs per r288 ruling); censusfus autofill burn then harvest; CN-KLINE-PATTERN-P1 prereg draft per "
              "DIGEST boundary disclosures")
st['ts'] = now_ts; st['last_round_ts'] = now_ts; st['updated_at'] = now_ts
st['current_task'] = 'R289 done: queue#3 folklore gate PASS; next = harvests + CN-KLINE-PATTERN-P1 prereg'
st['last_run'] = now_ts; st['last_round_at'] = now_ts; st['last_round'] = 288
st['updated'] = now_ts; st['last_seen'] = now_iso
st['task'] = st['current_task']
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

hp = 'fleet/machines/bm-a.json'
with open(hp, encoding='utf-8') as f:
    h = json.load(f)
h['machine_id'] = 'bm-a'
h['last_seen'] = now_iso
h['current_task'] = st['current_task']
h['cpu_cores'] = cores
h['cpu_pct'] = round(float(cpu_pct), 1)
h['free_ram_gb'] = free_ram_gb
h['gpu_free_vram_gb'] = gpu_free_gb
h['verdict'] = 'queue3_folklore_gate_pass_burn_in_flight'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_iso
h['round_no'] = 289
h['task'] = h['current_task']
with open(hp, 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

with open(hp, encoding='utf-8') as f:
    h2 = json.load(f)
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be json int'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated ISO8601'
print('WRAP OK', now_iso, 'epoch', epoch, 'cpu', cpu_pct, 'ram', free_ram_gb, 'gpu', gpu_free_gb)
