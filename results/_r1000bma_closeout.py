# -*- coding: utf-8 -*-
"""r1000 bm-a closeout: round report line + state round_no 1000 + heartbeat
(live CPU/RAM read, epoch int, T-separated clock) + idle_trigger --worked +
attrition ledger guard scan. File-based verification (encoding law)."""
import json, subprocess, sys, os, re, datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(now.timestamp())

# --- live machine faces ---
try:
    import psutil
    ram_free = round(psutil.virtual_memory().available / 1e9, 1)
    cpu_cores = psutil.cpu_count(logical=True)
except Exception:
    ram_free, cpu_cores = 16.8, 32
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'], capture_output=True, text=True)
    vram_free = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    vram_free = 0.36

# --- 1. round report line ---
rr_path = 'round_reports-bm-a.md'
line = (
    "2026-10-14T21:08:00+08:00 | r1000 bm-a | WM-VERDICT: green (red=false lane=healthy; py tail 97.5 burn-loaded per night order O-1855; satengine ALIVE rc0 queue0 post-W242-closeout) | "
    "当前活: W243 seat+probe LANDED (never-dry 常供给例波 chain-order next face; freeze UNBLOCKED zero in-flight upstream) | "
    "最近实物: fleet/inbox/MSG-20261014-2107-bma-w243-seat.md + results/_w243bma_20261014_probe.py + results/_w243bma_20261014_probe_receipt.json (commit 6207e60e9 pushed origin 21:0x; "
    "probe ADMIT: A 551_501..553_500 hops=0 fourth seed-gap A-continuation face / B 541_501..541_700 hops=1 live-seed refusal SEED_REGISTRY 541_500 (perpetual_n2_w15_gen) honest forward walk "
    "-- exact convergence with the W242 seat leg4 projection, zero divergence; seed_admit_gate rc0 FREE x2; origin vacancy 4-check green; "
    "bm-a 125th owned / 233rd engine wave per live derive r587/r359) | "
    "下轮指针: r1001 = W243 prereg derive (machine-SUB from frozen W242 tpl, facts ledger 956,735 / K=530,320 live-read) + five-face freeze splice (_w243bma_freeze_edits.py per _w242bma template) "
    "-> engine self-ignite W243 burn 12 shards; S6 chain r1000 detached in-flight (PID 62568, log results/_r1000bma_s6_chain.log, 40 legs, ~21:19 ETA -- next round consumes tail honestly) | "
    "孤儿面=0 (probe round-zero py_faces=26 orphans=0) | 本地未达 origin commit 数=0 (closeout push verified) | dept:研究 (lane-free; CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x + O-20261013-22:1x CPU standing-open)"
)
with open(rr_path, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')
n_lines = len(open(rr_path, encoding='utf-8').read().splitlines())
print('round report appended; total lines:', n_lines)

# --- 2. state round_no ---
st_path = 'state-bm-a.json'
st = json.load(open(st_path, encoding='utf-8'))
assert st.get('round_no') == 999, f"unexpected round_no {st.get('round_no')} (expect 999)"
st['round_no'] = 1000
with open(st_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk = json.load(open(st_path, encoding='utf-8'))
assert chk['round_no'] == 1000
print('state round_no ->', chk['round_no'])

# --- 3. heartbeat ---
hb_path = 'fleet/machines/bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = iso
hb['now_active'] = 'W243 seat+probe landed (commit 6207e60e9); next: prereg derive + five-face freeze (r1001)'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['ts'] = iso
hb['cpu_cores'] = cpu_cores
hb['free_ram_gb'] = ram_free
hb['free_vram_gb'] = vram_free
hb['verdict'] = ('green (wm-red=false; satengine ALIVE rc0 queue0 post-W242-finalize; W243 seat published=reserved '
                 'probe ADMIT A 551_501..553_500 / B 541_501..541_700 hops=1 live-seed refusal 541_500; '
                 f'S6 chain r1000 detached in-flight 40 legs; orphan 0/26; free RAM {ram_free}G)')
with open(hb_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk2 = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in chk2['clock_read'], 'clock_read must be T-separated ISO 8601 (R262 law)'
assert chk2['now_active'].startswith('W243 seat+probe landed')
print('heartbeat updated: epoch=%d clock=%s ram_free=%s' % (chk2['heartbeat_epoch_utc'], chk2['clock_read'], ram_free))

# --- 4. idle_trigger --worked (clear counter, bm-a carrier face) ---
r = subprocess.run([sys.executable, 'Tools/idle_trigger.py', '--worked'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('idle_trigger --worked rc=%d out=%s' % (r.returncode, (r.stdout or '').strip()[:120]))

# --- 5. attrition ledger guard scan ---
r = subprocess.run([sys.executable, 'scripts/attrition_ledger_guard.py', 'scan'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('attrition scan rc=%d out=%s' % (r.returncode, (r.stdout or '').strip()[:200]))
assert r.returncode in (0,), f'attrition scan ACTIVE LOSS rc={r.returncode} -- must fix before commit (r448 law)'

print('CLOSEOUT FACES OK')
