# r971 bm-b i2v re-ignition executor (CEO orders O-20261015-0915 + O-20261015-0952).
# Facts at r971 probe: 1200W PSU installed, power.limit=220W (cap lifted), PowerCap
# Boot/Hourly + BiliAutoReply tasks disabled (GUI session did these), frames 53/53,
# clips 29/53 - but i2v runner + ComfyUI server BOTH DEAD (09:52 MSG "复火中" claim
# did not hold; 10-13 09:5x power-cut killed batch mid-KN_KN28; never re-ignited).
# This driver executes O-0952 §1-2/§1-4 (loop round manual trigger, no grid wait):
#   A) work-registry W001-W004 retirement per §1-3 (bili line off bm-b)
#   B) valve-in: keepwarm.pause + ollama stop (serve-warm.ps1 header law)
#   C) materialize canonical runner trio from origin (git show, zero invention)
#   D) start ComfyUI server detached (pythonw, port 8188 = 10-13 run precedent)
#   E) start runner detached (pythonw h3_i2v_album.py --lane bmb, README-RUN law)
#   F) verify first unit SUBMITTED + running (O-0915 receipt: unit+VRAM+power face)
# Laws: r953 Popen+tree-kill caps, U060 NO_WINDOW, README-RUN.md canonical ignition,
# r959 delivery (orders/MSG ride closeout push), RAM<4GB hard veto (BM shared law).
import ctypes, datetime, json, os, subprocess, sys, time, urllib.request

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP = r'C:\Fluxgroup\FluxGroup'
PKG_REL = 'cph4/fleet/mv-album-001-jay/local-i2v'
PKG = GRP + r'\cph4\fleet\mv-album-001-jay\local-i2v'
MEDIA = GRP + r'\media\mv-album-001-jay'
OLLAMA = r'C:\Fluxgroup\MiniGame\Tools\Ollama'
COMFY = r'C:\Fluxgroup\MiniGame\Tools\ComfyUI_windows_portable'
PY311W = r'C:\Program Files\Python311\pythonw.exe'
REG = r'C:\Fluxgroup\.codely-cli\sentinel\bmb-work-registry.json'
LOG = BM + r'\results\_r971bmb_i2v_ignite.log'
OUT = BM + r'\results\_r971bmb_i2v_ignite.json'
TAG = 'r971a'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def run_capped(cmd, cap, cwd=None):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         creationflags=NO_WINDOW)
    try:
        out = p.communicate(timeout=cap)[0].decode('utf-8', 'replace')
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return -99, 'TIMEOUT_%ss' % cap

def free_ram_gb():
    # r971 fix: pythonw first call returned ullAvailPhys=0 (glitch face) - retry
    # with plausibility guard (0 < avail < total), else WMI fallback read.
    class M(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong)]
    for _ in (1, 2, 3):
        m = M(); m.dwLength = ctypes.sizeof(M)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)) \
                and 0 < m.ullAvailPhys < m.ullTotalPhys:
            return round(m.ullAvailPhys / (1024 ** 3), 2)
    rc, out = run_capped(['powershell', '-NoProfile', '-Command',
                          '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)'],
                         60)
    try:
        return round(float(out.strip()), 2)
    except Exception:
        return 0.0

def nvidia(fields):
    try:
        p = subprocess.run(['nvidia-smi', '--query-gpu=' + fields,
                            '--format=csv,noheader,nounits'], capture_output=True,
                           timeout=25, creationflags=NO_WINDOW)
        vals = [x.strip() for x in p.stdout.decode().strip().splitlines()[0].split(',')]
        return vals
    except Exception as e:
        return ['ERR:' + str(e)[:60]]

res = {'driver': 'r971bmb i2v re-ignition (O-20261015-0915+0952 executor)',
       'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
W('r971 i2v ignition start')

# ---------------- A) work-registry W001-W004 retirement (O-0952 s1-3) ----------------
try:
    reg = json.load(open(REG, encoding='utf-8'))
    retired = []
    for it in reg.get('items', []):
        if it.get('id') in ('W001', 'W002', 'W003', 'W004') and it.get('status') == 'open':
            it['status'] = 'retired'
            it['retire_note'] = ('2026-10-15 r971 per CEO order O-20261015-0952-bm-b s1-3 '
                                 '(本机不做bili bot了) - bili line moves off bm-b, any '
                                 'machine may take it; re-charter via committee if re-dispatched')
            retired.append(it['id'])
    json.dump(reg, open(REG, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    res['registry_retired'] = retired
    W('registry: retired %s (W005/W006 untouched, remain open)' % retired)
except Exception as e:
    res['registry_retired'] = 'ERROR:' + str(e)[:120]
    W('registry edit error: %s' % str(e)[:150])

# ---------------- RAM hard veto ----------------
ram0 = free_ram_gb()
res['ram_free_gb_start'] = ram0
W('free RAM start = %s GB' % ram0)
if ram0 < 4.0:
    res['status'] = 'VETO_RAM'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('ABORT: RAM below 4GB hard veto')
    print(json.dumps(res, ensure_ascii=False))
    sys.exit(3)

# ---------------- B) valve-in (serve-warm.ps1 header law) ----------------
pause = OLLAMA + r'\keepwarm.pause'
try:
    if not os.path.exists(pause):
        open(pause, 'w').write('r971 i2v batch valve-in %s\n' % res['ts'])
        res['keepwarm_pause'] = 'created'
    else:
        res['keepwarm_pause'] = 'already-present'
except Exception as e:
    res['keepwarm_pause'] = 'ERROR:' + str(e)[:100]
for model in ('qwen3.8:4b', 'qwen2.5:7b-instruct', 'qwen2.5:7b'):
    rc, out = run_capped([OLLAMA + r'\ollama.exe', 'stop', model], 60)
    W('ollama stop %s rc=%s out=%s' % (model, rc, out.strip()[:60]))
time.sleep(4)
v0 = nvidia('memory.used,memory.total,power.limit')
res['vram_after_valve_mib'] = v0[0]
res['vram_total_mib'] = v0[1]
res['power_limit_w'] = v0[2]
W('after valve: VRAM used=%s/total=%s power_limit=%sW' % (v0[0], v0[1], v0[2]))

# ---------------- C) materialize canonical runner trio from origin ----------------
os.makedirs(PKG, exist_ok=True)
mat = {}
for fn in ('h3_i2v_album.py', 'assignment-album-v1.json', 'wf_h3_i2v_480p_int4.json'):
    dst = os.path.join(PKG, fn)
    p = subprocess.Popen(['git', '-C', GRP, 'show', 'origin/main:%s/%s' % (PKG_REL, fn)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW)
    try:
        blob, err = p.communicate(timeout=90)
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        blob, err = b'', b'timeout'
    if p.returncode == 0 and blob:
        with open(dst, 'wb') as f:
            f.write(blob)
        mat[fn] = len(blob)
    else:
        mat[fn] = 'FAIL rc=%s %s' % (p.returncode, err.decode('utf-8', 'replace')[:100])
    W('materialize %s -> %s bytes' % (fn, mat[fn]))
res['materialized'] = mat
bad = [k for k, v in mat.items() if not isinstance(v, int) or v < 500]
if bad:
    res['status'] = 'MATERIALIZE_FAIL'
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('ABORT: materialize failed for %s' % bad)
    print(json.dumps(res, ensure_ascii=False))
    sys.exit(3)

# ---------------- D) start ComfyUI server detached (port 8188 precedent) ----------------
srv_out = open(MEDIA + r'\comfy-%s.out.txt' % TAG, 'wb')
srv_err = open(MEDIA + r'\comfy-%s.err.txt' % TAG, 'wb')
srv = subprocess.Popen([COMFY + r'\python_embeded\pythonw.exe', '-s',
                        COMFY + r'\ComfyUI\main.py', '--windows-standalone-build',
                        '--port', '8188', '--listen', '127.0.0.1',
                        '--output-directory', MEDIA + r'\comfy-out-480'],
                       stdout=srv_out, stderr=srv_err, creationflags=NO_WINDOW)
res['comfy_server_pid'] = srv.pid
W('ComfyUI server started pid=%s (port 8188, out-dir comfy-out-480)' % srv.pid)

up = False
for i in range(36):  # up to 180s
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
    print(json.dumps(res, ensure_ascii=False))
    sys.exit(3)

# ---------------- E) start runner detached (README-RUN law) ----------------
run_out = open(MEDIA + r'\log-bmb-%s.out.txt' % TAG, 'wb')
run_err = open(MEDIA + r'\log-bmb-%s.err.txt' % TAG, 'wb')
rn = subprocess.Popen([PY311W, PKG + r'\h3_i2v_album.py', '--repo', GRP, '--lane', 'bmb'],
                      cwd=PKG, stdout=run_out, stderr=run_err, creationflags=NO_WINDOW)
res['runner_pid'] = rn.pid
W('runner started pid=%s (lane bmb, 53 orders, SKIP-resume)' % rn.pid)

# ---------------- F) verify first unit SUBMITTED + running (O-0915 receipt) ----------------
runner_log = MEDIA + r'\log-bmb-%s.out.txt' % TAG
first_unit, first_running = None, False
deadline = time.time() + 300
while time.time() < deadline:
    time.sleep(10)
    try:
        with open(runner_log, 'rb') as f:
            txt = f.read().decode('utf-8', 'replace')
    except Exception:
        txt = ''
    for line in txt.splitlines():
        if 'SUBMITTED' in line and first_unit is None:
            first_unit = line.strip()[:120]
        if 'running...' in line:
            first_running = True
    if first_unit and first_running:
        break
v1 = nvidia('memory.used,memory.total,utilization.gpu,power.draw,power.limit,temperature.gpu')
res.update({'first_unit_line': first_unit, 'first_unit_running_seen': first_running,
            'vram_used_mib_burn': v1[0], 'vram_total_mib': v1[1],
            'gpu_util_pct': v1[2], 'power_draw_w': v1[3],
            'power_limit_w_final': v1[4], 'gpu_temp_c': v1[5],
            'ram_free_gb_end': free_ram_gb(),
            'status': ('IGNITED' if (first_unit and first_running) else
                       ('SUBMIT_SEEN_POLL_CONTINUES' if first_unit else 'NO_SUBMIT_300S'))})
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('ignition verdict=%s first_unit=%s vram=%s util=%s%% draw=%sW limit=%sW'
  % (res['status'], str(first_unit)[:60], v1[0], v1[2], v1[3], v1[4]))
print(json.dumps(res, ensure_ascii=False, indent=1))
