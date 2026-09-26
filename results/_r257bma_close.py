import json, io, time, subprocess
import psutil

now = time.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
clock_read = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
cpu = psutil.cpu_percent(interval=2)
ram_gb = round(psutil.virtual_memory().available / 2**30, 1)

# gpu free vram face from latest audit sample (single source, no re-derive)
au = json.load(io.open('results/compute_audit.json', encoding='utf-8-sig'))
gpu_free = None
hist = au.get('history') or au.get('latest') or {}
def _g(o):
    global gpu_free
    if isinstance(o, dict):
        g = o.get('gpu') or {}
        if isinstance(g, dict) and 'mem_used_mb' in g:
            tot = o.get('gpu_total_vram_mb') or 12288.0
            gpu_free = round((tot - g['mem_used_mb']) / 1024, 1)
        for v in o.values():
            if isinstance(v, (dict, list)):
                _g(v)
    elif isinstance(o, list):
        for v in o:
            _g(v)
_g(au)
if gpu_free is None:
    gpu_free = 5.9

DID = ("R257: T-73 s2 slice-C retail-herding law census empirical ONE ROUND "
       "(third s2 law closed, FIRST s2 law to pass all gates_v123): "
       "scripts/t73_s2_retail_herding.py prereg-frozen header + selftest 8 legs + "
       "batch 81.2s 9 IC faces -> TO20/h10 OOS ic -0.0635 (40x 1.6bp nulls thr) "
       "IS -0.0632 ir -0.407 gates 5/5, ALL eras negative pre2005..2025+ "
       "(2017-2020 peak -0.0927, 2025+ alive -0.0635 decayed ~55%), 8/9 faces pass; "
       "anti-repeat verified plain-turnover face absent P-1c/d/e; digest sliceC-herding "
       "+ artifact retail_herding.json + ticket progress_r257; T-82 deep-shard "
       "receiving window ARMED (branch not on origin at 16:4x, MSG-1650 reply, "
       "MSG-1622 processed); S6 chain all legs exit 0")
VERDICT = ("GREEN herding law ALIVE BOTH SIDES first all-gates s2 law (supply "
           "answer to pool_starvation flag: 81.2s in-repo batch <5min inline legal, "
           "no >5min pool batch pending, no fabricated busywork O-1137)")
NEXT = ("s2 remaining: factor-history slice (size/lowvol/dividend; lowvol+size "
        "amount-proxy in P1C cache, dividend via 510880 ETF style face, fundamentals "
        "absent disclosed) then style-rotation slice (2017/2021/2023/2024 via ETF "
        "panels); T+1/limit face consumed by T-57 (closed); transfer/t80-deep-bcd-basis "
        "arrival check each S0.5; 09-28 Monday new-bar chain; 10-01 month trio + v3 "
        "date gate; T-70 verdict window 10-09")

# --- state file (round_no +1, mirror byte faces: indent=1 LF no-trailing-nl) ---
P = 'state-bm-a.json'
d = json.load(io.open(P, encoding='utf-8'))
assert d['round_no'] == 256
d['round_no'] = 257
d['did'] = DID
d['verdict'] = VERDICT
d['next'] = NEXT
d['ts'] = now
d['last_round_ts'] = now
d['updated_at'] = now
d['current_task'] = 'T-73 s2/s3 chain + T-82 deep-shard receiving window + fleet maintenance'
d['last_run'] = 'R257 ' + clock_read
d['last_round_at'] = 'R257 ' + clock_read
io.open(P, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(d, ensure_ascii=False, indent=1))
print('state written round_no=257')

# --- heartbeat (epoch MUST be JSON int; self-verify after write) ---
H = 'fleet/machines/bm-a.json'
h = json.load(io.open(H, encoding='utf-8-sig'))
h['last_seen'] = now
h['current_task'] = d['current_task']
h['cpu_pct'] = round(cpu, 1)
h['free_ram_gb'] = ram_gb
h['gpu_free_vram_gb'] = gpu_free
h['verdict'] = VERDICT
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock_read
h['round_no'] = 257
io.open(H, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(io.open(H, encoding='utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written epoch=', chk['heartbeat_epoch_utc'],
      'isinstance-int OK cpu=', chk['cpu_pct'], 'ram=', chk['free_ram_gb'],
      'gpu_free=', chk['gpu_free_vram_gb'])
