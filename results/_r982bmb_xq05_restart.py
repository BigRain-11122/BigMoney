# r982b bm-b XQ_XQ05 second attempt: ComfyUI server clean restart + runner re-ignite.
# Evidence chain (r982): attempt #1 (15:34, timeout 4200->10800) OOM-errored at
# 184s: torch.AcceleratorError CUDA OOM inside res_multistep model forward +
# aimdo cleanup crash (comfyui_8188.log L388-521). Idle VRAM 3951/8192MiB held
# by a 5.5h-old server session (60 renders, allocator fragmentation). Kin
# evidence: len=226 items CAN complete (KN28 1757s on fresh server as first
# item 10:0x; XQ26 318s mid-session) - XQ05 sits at the VRAM edge; the earlier
# 4200s cap-kills were OOM-crawl, not hangs. Fix = fresh CUDA context + 3h cap.
# Canonical server args per r971 driver section D (zero invention). U060
# NO_WINDOW, r953 tree-kill, r949 log-verified claims only.
import datetime, json, os, subprocess, sys, time, urllib.request

GRP = r'C:\Fluxgroup\FluxGroup'
PKG = GRP + r'\cph4\fleet\mv-album-001-jay\local-i2v'
MEDIA = GRP + r'\media\mv-album-001-jay'
OLLAMA = r'C:\Fluxgroup\MiniGame\Tools\Ollama'
COMFY = r'C:\Fluxgroup\MiniGame\Tools\ComfyUI_windows_portable'
PY311W = r'C:\Program Files\Python311\pythonw.exe'
LOG = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r982bmb_xq05_restart.log'
OUT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r982bmb_xq05_restart.json'
TAG = 'r982b'
NO_WINDOW = 0x08000000
TARGET = 'XQ_XQ05'
TIMEOUT_S = 10800

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def gpu_used_mib():
    try:
        p = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                           capture_output=True, timeout=25, creationflags=NO_WINDOW)
        return int(float(p.stdout.decode().strip().splitlines()[0]))
    except Exception as e:
        return -1

res = {'driver': 'r982bmb XQ05 server-restart re-ignite (clean CUDA context)',
       'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
W('r982b start: server restart + XQ05 re-ignite')

# 1) valve must be IN
res['keepwarm_pause_present'] = os.path.exists(OLLAMA + r'\keepwarm.pause')
# 2) target clip must still be absent
clip = MEDIA + r'\clips-animatic-480' + '\\' + TARGET + '.mp4'
res['target_clip_exists'] = os.path.isfile(clip) and os.path.getsize(clip) > 100000
# 3) no live runner (single-flight)
try:
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" | "
        "Where-Object {$_.CommandLine -match 'h3_i2v_album'} | Select-Object -ExpandProperty ProcessId"],
        capture_output=True, timeout=30, creationflags=NO_WINDOW).stdout.decode()
    res['live_runner_pids'] = [x.strip() for x in out.split() if x.strip().isdigit()]
except Exception as e:
    res['live_runner_pids'] = ['ERR:' + str(e)[:60]]
if not res['keepwarm_pause_present'] or res['target_clip_exists'] or res['live_runner_pids']:
    res['status'] = 'GUARD_FAIL'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('ABORT guards: valve=%s clip=%s runner=%s' % (
        res['keepwarm_pause_present'], res['target_clip_exists'], res['live_runner_pids']))
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 4) tree-kill the live ComfyUI server (match by command line, r953 tree law)
srv_pids = []
try:
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" | "
        "Where-Object {$_.CommandLine -match 'ComfyUI\\\\main.py'} | Select-Object -ExpandProperty ProcessId"],
        capture_output=True, timeout=30, creationflags=NO_WINDOW).stdout.decode()
    srv_pids = [x.strip() for x in out.split() if x.strip().isdigit()]
except Exception as e:
    res['srv_find_err'] = str(e)[:80]
res['server_pids_killed'] = srv_pids
for pid in srv_pids:
    subprocess.run('taskkill /T /F /PID %s' % pid, shell=True, capture_output=True, creationflags=NO_WINDOW)
    W('tree-killed server pid %s' % pid)

# 5) wait for VRAM release (up to 90s)
v0 = gpu_used_mib()
for i in range(18):
    if v0 <= 1500:
        break
    time.sleep(5)
    v0 = gpu_used_mib()
res['vram_after_kill_mib'] = v0
W('vram after kill = %s MiB' % v0)

# 6) relaunch server detached, canonical r971 args (zero invention)
srv_out = open(MEDIA + r'\comfy-%s.out.txt' % TAG, 'wb')
srv_err = open(MEDIA + r'\comfy-%s.err.txt' % TAG, 'wb')
srv = subprocess.Popen([COMFY + r'\python_embeded\pythonw.exe', '-s',
                        COMFY + r'\ComfyUI\main.py', '--windows-standalone-build',
                        '--port', '8188', '--listen', '127.0.0.1',
                        '--output-directory', MEDIA + r'\comfy-out-480'],
                       stdout=srv_out, stderr=srv_err, creationflags=NO_WINDOW)
res['new_server_pid'] = srv.pid
W('server relaunched pid=%s' % srv.pid)

up = False
for i in range(36):
    time.sleep(5)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=4) as r:
            up = (r.status == 200)
            break
    except Exception:
        pass
res['comfy_up'] = up
W('comfy poll up=%s after %ds' % (up, (i + 1) * 5))
if not up:
    res['status'] = 'SERVER_NOT_UP'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('ABORT: server not up in 180s')
    print(json.dumps(res, ensure_ascii=False)); sys.exit(3)

# 7) re-ignite runner sole-item 3h cap
run_out = open(MEDIA + r'\log-bmb-%s.out.txt' % TAG, 'wb')
run_err = open(MEDIA + r'\log-bmb-%s.err.txt' % TAG, 'wb')
rn = subprocess.Popen([PY311W, PKG + r'\h3_i2v_album.py', '--repo', GRP, '--lane', 'bmb',
                       '--only', TARGET, '--timeout', str(TIMEOUT_S)],
                      cwd=PKG, stdout=run_out, stderr=run_err, creationflags=NO_WINDOW)
res['runner_pid'] = rn.pid
W('runner started pid=%s --only %s --timeout %s' % (rn.pid, TARGET, TIMEOUT_S))

# 8) verify: SUBMITTED + running, and NO ERROR line within 420s window
#    (attempt #1 OOM-errored at 184s; passing 300s+ without ERROR = sampler
#     got past the OOM point on the clean context - ignition proof)
runner_log = MEDIA + r'\log-bmb-%s.out.txt' % TAG
first_unit, running_seen, error_seen = None, False, False
deadline = time.time() + 420
last_poll = 0
while time.time() < deadline:
    time.sleep(15)
    try:
        txt = open(runner_log, 'rb').read().decode('utf-8', 'replace')
    except Exception:
        txt = ''
    for line in txt.splitlines():
        if 'SUBMITTED' in line and first_unit is None:
            first_unit = line.strip()[:140]
        if 'running...' in line:
            running_seen = True
            last_poll = time.time()
        if 'ERROR' in line:
            error_seen = True
    if error_seen:
        break
    if first_unit and running_seen and (time.time() - deadline) < -180:
        # keep polling until at least 240s past submit for OOM-window proof
        pass
res['first_unit_line'] = first_unit
res['running_seen'] = running_seen
res['error_seen'] = error_seen
res['status'] = ('ERROR_AGAIN' if error_seen else
                 ('IGNITED_CLEAN' if (first_unit and running_seen) else 'NO_SUBMIT_420S'))
v1 = gpu_used_mib()
res['vram_end_mib'] = v1
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('verdict=%s first_unit=%s error_seen=%s vram_end=%s' % (
    res['status'], str(first_unit)[:80], error_seen, v1))
print(json.dumps(res, ensure_ascii=False))
