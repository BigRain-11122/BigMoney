# r982 bm-b i2v XQ_XQ05 sole-item re-ignition (detached, raised timeout).
# Root cause (r982 diagnosis, evidence-backed): XQ_XQ05 is the ONLY standing
# fail of the 53-unit album lane; every prior attempt died at the runner's
# default --timeout 4200s cap (70min), NOT a hang: same-lane kin prove render
# time is content-driven up to 2431s at len=141 (XQ07), 1757s at len=226 (KN28,
# which also failed 3x at the 4200s cap on 10-14 before succeeding 10-15),
# 1758s (KN15), 1433s (KN17); XQ05 len=226 + heavy-motion content legitimately
# exceeds 70min. Fix = canonical runner UNTOUCHED, re-run with --only
# XQ_XQ05 --timeout 10800 (3h cap). Valve stays IN (keepwarm.pause) until
# 53/53 completion verdict, then valve-out per r916 law in a later round.
# Laws: U060 NO_WINDOW, r953 detached + log-verified claims only (r949/r958).
import datetime, json, os, subprocess, sys, time, urllib.request

GRP = r'C:\Fluxgroup\FluxGroup'
PKG = GRP + r'\cph4\fleet\mv-album-001-jay\local-i2v'
MEDIA = GRP + r'\media\mv-album-001-jay'
OLLAMA = r'C:\Fluxgroup\MiniGame\Tools\Ollama'
PY311W = r'C:\Program Files\Python311\pythonw.exe'
LOG = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r982bmb_xq05_reignite.log'
OUT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r982bmb_xq05_reignite.json'
TAG = 'r982a'
NO_WINDOW = 0x08000000
TARGET = 'XQ_XQ05'
TIMEOUT_S = 10800

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

res = {'driver': 'r982bmb XQ05 sole-item re-ignition (timeout 4200->10800)',
       'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
W('r982 XQ05 re-ignition start')

# 1) valve must be IN (batch not complete)
pause = OLLAMA + r'\keepwarm.pause'
res['keepwarm_pause_present'] = os.path.exists(pause)
if not res['keepwarm_pause_present']:
    W('ABORT: keepwarm.pause missing - valve state unexpected, refusing to burn')
    res['status'] = 'VALVE_STATE_UNEXPECTED'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 2) ComfyUI server must be up
try:
    with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=6) as r:
        res['comfy_up'] = (r.status == 200)
except Exception as e:
    res['comfy_up'] = False
    res['comfy_err'] = str(e)[:100]
if not res.get('comfy_up'):
    W('ABORT: ComfyUI 8188 not responding')
    res['status'] = 'SERVER_DOWN'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 3) canonical trio on disk
trio = {}
for fn in ('h3_i2v_album.py', 'assignment-album-v1.json', 'wf_h3_i2v_480p_int4.json'):
    p = os.path.join(PKG, fn)
    trio[fn] = os.path.getsize(p) if os.path.isfile(p) else -1
res['trio_bytes'] = trio
if any(v < 500 for v in trio.values()):
    W('ABORT: canonical trio incomplete %s' % trio)
    res['status'] = 'TRIO_MISSING'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 4) target clip must be absent (else nothing to do)
clip = MEDIA + r'\clips-animatic-480' + '\\' + TARGET + '.mp4'
res['target_clip_exists'] = os.path.isfile(clip) and os.path.getsize(clip) > 100000
if res['target_clip_exists']:
    W('ABORT: %s.mp4 already in library - nothing to burn' % TARGET)
    res['status'] = 'ALREADY_DONE'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)); sys.exit(0)

# 5) no duplicate runner for same target (single-flight)
dup = False
try:
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" | "
        "Where-Object {$_.CommandLine -match 'h3_i2v_album'} | "
        "Select-Object -ExpandProperty ProcessId"],
        capture_output=True, timeout=30, creationflags=NO_WINDOW).stdout.decode()
    pids = [x.strip() for x in out.split() if x.strip().isdigit()]
    dup = len(pids) > 0
    res['existing_runner_pids'] = pids
except Exception as e:
    res['dup_check_err'] = str(e)[:100]
if dup:
    W('ABORT: runner already alive pids=%s (single-flight law)' % res.get('existing_runner_pids'))
    res['status'] = 'RUNNER_ALREADY_ALIVE'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 6) ignite detached (U060)
run_out = open(MEDIA + r'\log-bmb-%s.out.txt' % TAG, 'wb')
run_err = open(MEDIA + r'\log-bmb-%s.err.txt' % TAG, 'wb')
rn = subprocess.Popen([PY311W, PKG + r'\h3_i2v_album.py', '--repo', GRP, '--lane', 'bmb',
                       '--only', TARGET, '--timeout', str(TIMEOUT_S)],
                      cwd=PKG, stdout=run_out, stderr=run_err, creationflags=NO_WINDOW)
res['runner_pid'] = rn.pid
W('runner started pid=%s --only %s --timeout %s' % (rn.pid, TARGET, TIMEOUT_S))

# 7) verify SUBMITTED + running (300s window; model reload after /free allowed)
runner_log = MEDIA + r'\log-bmb-%s.out.txt' % TAG
first_unit, running_seen = None, False
deadline = time.time() + 300
while time.time() < deadline:
    time.sleep(10)
    try:
        txt = open(runner_log, 'rb').read().decode('utf-8', 'replace')
    except Exception:
        txt = ''
    for line in txt.splitlines():
        if 'SUBMITTED' in line and first_unit is None:
            first_unit = line.strip()[:140]
        if 'running...' in line:
            running_seen = True
    if first_unit and running_seen:
        break
res['first_unit_line'] = first_unit
res['running_seen'] = running_seen
res['status'] = 'IGNITED' if (first_unit and running_seen) else 'NO_SUBMIT_300S'
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('verdict=%s first_unit=%s' % (res['status'], str(first_unit)[:90]))
print(json.dumps(res, ensure_ascii=False))
