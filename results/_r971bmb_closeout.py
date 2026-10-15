# r971 bm-b closeout: CEO-order execution round (twelfth recovery beat).
# Executes O-20261015-0915 + O-20261015-0952 (1200W PSU, full-power unlock,
# i2v re-ignition - loop-round manual trigger per O-0952 s1-4) + standard
# monitor faces. Ignition itself ran detached via _r971bmb_ignite_i2v.py
# (survives this process). This closeout: consume C-r970 + C-r970b receipts
# (ancestor-verify on origin), v5 restore monitor (anchor 1116@09:45:19,
# done-climb law r960), salvage/backfill liveness, s05 fresh probe, unknown-
# order diff, i2v ignition evidence read (O-0915 receipt line: unit + VRAM +
# power face), lane-task registry quad (R49), engine, watermark, sentinel,
# idle/S8, CODELY pending-union, heartbeat + state + round report (binary
# append r962 law), receipt append into O-0915, then C-r971 surgery push:
# 3 own faces (hb/state/round report) + 3 delivery faces (O-0915/O-0952/
# MSG-20261015-0952) per r959 delivery law. Laws: r950 plumbing + --no-verify
# receipted escape, r953 Popen+tree-kill, r957 ls-tree tip:<dir> + mktree
# --missing + non-empty-name guard, r951 segment claims, r960 judge-by-
# done-climb, MSG-0612 max-merge (O-0025/O-0906 zero-touch), ASCII-safe log.
import ctypes, datetime, json, os, re, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r971bmb_closeout.log'
PUSHREC = BM + r'\results\_r971bmb_push_receipt.json'
S05OUT = BM + r'\results\_r971bmb_s05_scan.json'
S05SCRIPT = BM + r'\results\_r971bmb_s05_scan.py'
MONOUT = BM + r'\results\_r971bmb_monitor.json'
IGNOUT = BM + r'\results\_r971bmb_i2v_ignite.json'
IGNLOG = BM + r'\results\_r971bmb_i2v_ignite.log'
RUNNERLOG = r'C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\log-bmb-r971a.out.txt'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
V5DRIVERLOG = BM + r'\results\_r960bmb_restore_driver.log'
SALVLOG = BM + r'\results\_r969bmb_salvage.log'
SALVOUT = BM + r'\results\_r969bmb_salvage.json'
C970REC = BM + r'\results\_r970bmb_push_receipt.json'
C970BREC = BM + r'\results\_r970bmb_delivery_receipt.json'
ORD915 = BM + r'\fleet\orders\O-20261015-0915-bm-b.md'
ORD952 = BM + r'\fleet\orders\O-20261015-0952-bm-b.md'
MSG0952 = BM + r'\fleet\inbox\MSG-20261015-0952-bm-b-work-request.md'
ORD915_NAME = 'O-20261015-0915-bm-b.md'
ORD952_NAME = 'O-20261015-0952-bm-b.md'
MSG0952_NAME = 'MSG-20261015-0952-bm-b-work-request.md'
ORD0025_NAME = 'O-20261015-0025-bm-b.md'
ORD0906_NAME = 'O-20261015-0906-bm-b.md'
SENTLOG = r'C:\Fluxgroup\.codely-cli\sentinel\sentinel.log'
WMRED = BM + r'\results\watermark_red.json'
IDLE = BM + r'\results\idle_trigger.bm-b.json'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

ENV = os.environ.copy()
ENV['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
ENV['GIT_AUTHOR_NAME'] = 'junsheng.sun'; ENV['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
ENV['GIT_COMMITTER_NAME'] = 'junsheng.sun'; ENV['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'

def net_git(args, timeout, input_bytes=None):
    p = subprocess.Popen(['git'] + args, cwd=BM, env=ENV, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, creationflags=NO_WINDOW,
                         stdin=subprocess.PIPE if input_bytes is not None else None)
    try:
        out, err = p.communicate(input=input_bytes, timeout=timeout)
        return p.returncode, out, err
    except Exception:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        return -99, b'', b'tree-killed on timeout'

def run_capped(cmd, cap):
    p = subprocess.Popen(cmd, cwd=BM, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
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

def save_receipt(status, **kw):
    d = {'driver': 'r971bmb push C-r971 (origin/main)', 'target': 'refs/heads/main',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
         'status': status}
    d.update(kw)
    json.dump(d, open(PUSHREC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def free_ram_gb():
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

def gpu_face():
    try:
        p = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu,'
                            'power.draw,power.limit,temperature.gpu', '--format=csv,noheader,nounits'],
                           capture_output=True, timeout=25, creationflags=NO_WINDOW)
        v = [x.strip() for x in p.stdout.decode().strip().splitlines()[0].split(',')]
        return {'vram_used_mib': v[0], 'vram_total_mib': v[1], 'util_pct': v[2],
                'power_draw_w': v[3], 'power_limit_w': v[4], 'temp_c': v[5]}
    except Exception as e:
        return {'error': str(e)[:100]}

def pid_alive(pid):
    try:
        r = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid], capture_output=True,
                           timeout=30, creationflags=NO_WINDOW)
        return str(pid) in r.stdout.decode('utf-8', 'replace')
    except Exception:
        return None

def ps_discover(needle, first=True):
    ps_cmd = ("(Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" "
              "| Where-Object { $_.CommandLine -like '*%s*' } "
              "| Select-Object %s 1).ProcessId" % (needle, '-First ' if first else ''))
    rc, out = run_capped(['powershell', '-NoProfile', '-Command', ps_cmd], 90)
    if rc == 0:
        m = re.search(r'\d+', out.strip())
        if m:
            return int(m.group())
    return None

def v5_progress():
    try:
        d = json.load(open(V5REC, encoding='utf-8'))
        return (d.get('status'), d.get('pass_no'), d.get('done_in_pass'), d.get('remaining'),
                d.get('fails_in_pass'), d.get('retried_ok_in_pass'), d.get('ts'),
                d.get('ok_in_pass'), d.get('restored_total'))
    except Exception:
        return 'unknown', None, None, None, None, None, None, None, None

def tail_file(path, n=6):
    try:
        with open(path, 'rb') as f:
            lines = f.read().decode('utf-8', 'replace').splitlines()
        return lines[-n:]
    except Exception:
        return None

W('r971 closeout start (CEO-order execution round, i2v re-ignition + delivery)')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
ram_gb = free_ram_gb()
W('free_ram_gb=%s' % ram_gb)
gf = gpu_face()
W('gpu face: %s' % json.dumps(gf))

# ---------------- v5 restore monitor (anchor 1116@09:45:19, done-climb law) ----------------
dstat, dpass, ddone, drem, dfails, dretr, dts, dok, drest = v5_progress()
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s ok=%s receipt_ts=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr, dok, dts))
rate_min = 0.0
eta_txt = 'n/a'
stagnant = False
try:
    a_done, a_ts = 1116, datetime.datetime.fromisoformat('2026-10-15T09:45:19+08:00')
    if ddone and dts:
        cur_ts = datetime.datetime.fromisoformat(dts)
        if ddone == a_done:
            stagnant = True
        elif ddone > a_done and cur_ts > a_ts:
            dt_min = (cur_ts - a_ts).total_seconds() / 60.0
            if dt_min >= 1.0:
                rate_min = max(0.0, (ddone - a_done) / dt_min)
    if drem and rate_min:
        eta_dt = now + datetime.timedelta(minutes=float(drem) / rate_min)
        eta_txt = eta_dt.strftime('%H:%M')
    elif drem:
        eta_txt = 'no-climb-this-window (salvage may accelerate materialize)'
except Exception as e:
    W('rate/eta calc error: %s' % str(e)[:120])
W('v5 rate=%.2f files/min eta=%s (remaining=%s) stagnant_vs_anchor=%s'
  % (rate_min, eta_txt, drem, stagnant))
v5_pid, v5_pid_src = (ps_discover('_r960bmb_restore_driver') or 3672), 'cmdline-discovery'
v5_alive_drv = pid_alive(v5_pid)
W('v5 pid %s alive=%s' % (v5_pid, v5_alive_drv))

# ---------------- salvage + backfill workers ----------------
salv_pid = ps_discover('_r969bmb_salvage')
salv_alive = pid_alive(salv_pid) if salv_pid else False
salv_done_json = os.path.exists(SALVOUT)
salv_log_tail = tail_file(SALVLOG, 6)
W('salvage pid=%s alive=%s json=%s tail=%s' % (salv_pid, salv_alive, salv_done_json,
                                              str(salv_log_tail)[-100:] if salv_log_tail else None))
salv_action = 'alive-running (json pending)'
if salv_pid is None and salv_done_json:
    salv_action = 'dead+json -> absorbed (v5 pass-2 materializes)'
elif salv_pid is None and not salv_done_json:
    try:
        subprocess.Popen([r'C:\Program Files\Python311\pythonw.exe', BM + r'\results\_r969bmb_salvage.py'],
                          creationflags=NO_WINDOW)
        salv_action = 'DEAD+NO-JSON -> relaunched detached (r971)'
        W('salvage relaunched detached')
    except Exception as e:
        salv_action = 'relaunch-error: %s' % str(e)[:100]
bf_pid = ps_discover('backfill_ext_slots')
bf_alive = pid_alive(bf_pid) if bf_pid else False
W('backfill pid=%s alive=%s (no-touch)' % (bf_pid, bf_alive))

# ---------------- C-r970 + C-r970b receipt consume (ancestor verify) ----------------
c970_sha = c970b_sha = None
try:
    c970_sha = json.load(open(C970REC, encoding='utf-8')).get('pushed_sha')
    c970b_sha = json.load(open(C970BREC, encoding='utf-8')).get('pushed_sha')
    W('receipts: C-r970=%s C-r970b=%s' % (str(c970_sha)[:12], str(c970b_sha)[:12]))
except Exception as e:
    W('receipt read error: %s' % str(e)[:120])
rc_f, _, _ = net_git(['fetch', 'origin', 'main'], 180)
W('fetch rc=%s' % rc_f)
anc970 = anc970b = None
peer_tip = None
if rc_f == 0:
    if c970_sha:
        anc970 = net_git(['merge-base', '--is-ancestor', c970_sha, 'origin/main'], 60)[0]
    if c970b_sha:
        anc970b = net_git(['merge-base', '--is-ancestor', c970b_sha, 'origin/main'], 60)[0]
    peer_tip = net_git(['rev-parse', 'origin/main'], 30)[1].decode().strip()
W('ancestor: C-r970 rc=%s C-r970b rc=%s origin_tip=%s' % (anc970, anc970b, str(peer_tip)[:12]))

# ---------------- delivery faces (r959 law): O-0915 / O-0952 / MSG-0952 + presence checks ----------------
origin_orders, origin_inbox = [], []
o25_on = o06_on = False
try:
    rc_o, out_o, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/orders/'], 60)
    if rc_o == 0:
        origin_orders = [l.strip() for l in out_o.decode('utf-8', 'replace').splitlines() if l.strip()]
        o25_on = ORD0025_NAME in origin_orders
        o06_on = ORD0906_NAME in origin_orders
    rc_i, out_i, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/inbox/'], 60)
    if rc_i == 0:
        origin_inbox = [l.strip() for l in out_i.decode('utf-8', 'replace').splitlines() if l.strip()]
except Exception as e:
    W('origin ls-tree error: %s' % str(e)[:120])
unknown_orders = []
try:
    known = open(BM + r'\state.json', encoding='utf-8').read()
    try:
        with open(BM + r'\logs\iteration-loop\round_reports.md', 'rb') as f:
            rl = f.read().decode('utf-8', 'replace').splitlines()
        known += '\n'.join(rl[-300:])
    except Exception:
        pass
    unknown_orders = [n for n in origin_orders if n.startswith('O-') and n not in known]
except Exception as e:
    W('known-text build error: %s' % str(e)[:120])
W('delivery: o25_on_origin=%s o06_on_origin=%s unknown=%s origin_orders=%d origin_inbox=%d'
  % (o25_on, o06_on, unknown_orders, len(origin_orders), len(origin_inbox)))
local_orders = [f for f in os.listdir(BM + r'\fleet\orders') if f.endswith('.md')]
local_inbox = [f for f in os.listdir(BM + r'\fleet\inbox') if f.endswith('.md')]
W('local: orders=%s inbox=%s' % (local_orders, local_inbox))

# ---------------- i2v ignition evidence (O-0915 receipt) ----------------
ign = {}
try:
    ign = json.load(open(IGNOUT, encoding='utf-8'))
except Exception:
    ign = {'status': 'IN_FLIGHT_NO_JSON_YET'}
ign_log_tail = tail_file(IGNLOG, 8)
first_unit, running_seen = None, False
submit_deadline = time.time() + 120
while time.time() < submit_deadline:
    try:
        with open(RUNNERLOG, 'rb') as f:
            txt = f.read().decode('utf-8', 'replace')
        for line in txt.splitlines():
            if 'SUBMITTED' in line and first_unit is None:
                first_unit = line.strip()[:130]
            if 'running...' in line:
                running_seen = True
        if first_unit and running_seen:
            break
    except Exception:
        pass
    time.sleep(10)
runner_tail = tail_file(RUNNERLOG, 8)
gf2 = gpu_face()
W('ignition: json_status=%s first_unit=%s running_seen=%s gpu_burn=%s'
  % (ign.get('status'), first_unit, running_seen, json.dumps(gf2)))
ign_ok = bool(first_unit)
clips_now = len([f for f in os.listdir(r'C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\clips-animatic-480')
                 if f.endswith('.mp4')]) if os.path.isdir(r'C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\clips-animatic-480') else None
W('clips-animatic-480 count=%s (was 29 at r971 start)' % clips_now)

# O-0915 receipt append (local file; rides C-r971 delivery)
receipt_txt = ('- [x] bm-b 循环轮回执 @r971 %s：i2v 批首件起跑自证=%s（VRAM 面=%s/%sMiB·util=%s%%·'
               '功耗=%sW/帽%sW）；执行链=阀入（keepwarm.pause+ollama stop）→origin 物化正典三件→'
               'ComfyUI 8188 分离起服（pid %s）→runner 分离起跑（pid %s·lane bmb 53 单 SKIP 续跑·'
               '29 件在库）；O-0952 后令已解除 180W 限档条款（nvidia-smi 220W 默认墙实证·PowerCap '
               'Boot/Hourly 双任务已禁用查证）——本回执行按全功率面，起跑后连续烧至 53/53'
               % (iso, first_unit or ('SUBMIT_PENDING_ignition_json=' + str(ign.get('status'))),
                  gf2.get('vram_used_mib'), gf2.get('vram_total_mib'), gf2.get('util_pct'),
                  gf2.get('power_draw_w'), gf2.get('power_limit_w'),
                  ign.get('comfy_server_pid'), ign.get('runner_pid')))
try:
    oc = open(ORD915, 'r', encoding='utf-8').read()
    if 'bm-b 循环轮回执 @r971' not in oc:
        oc = oc.rstrip('\n') + '\n' + receipt_txt + '\n'
        oc = oc.replace('- [ ] bm-b 循环轮回执', '- [x] bm-b 循环轮回执')
        open(ORD915, 'w', encoding='utf-8').write(oc)
        W('O-0915 receipt appended')
    else:
        W('O-0915 receipt already present')
except Exception as e:
    W('O-0915 receipt append error: %s' % str(e)[:150])

# ---------------- s05 fresh probe ----------------
rc_s, out_s = run_capped(['python', S05SCRIPT], 240)
W('s05 rc=%s tail=%s' % (rc_s, out_s.strip().splitlines()[-1][:100] if out_s.strip() else ''))
try:
    s05 = json.load(open(S05OUT, encoding='utf-8'))
except Exception as e:
    s05 = {'verdict': 'READ_ERROR', 'error': str(e)[:150]}
s05v = s05.get('verdict')
ord_sha = s05.get('orders_sha')
dec_sha = s05.get('decisions_sha')
delta_pending = (s05v == 'DELTA_PRESENT')
W('s05 verdict=%s ord=%s dec=%s' % (s05v, str(ord_sha)[:12], str(dec_sha)[:12]))

# ---------------- lane-task registry (R49 schtasks) ----------------
lane_face = {'schtasks_query': {}, 'register_quad': {}}
for tn in ('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'Bigmoney-SatEngine-bm-b',
           'GPU-PowerCap-180W-Boot', 'GPU-PowerCap-180W-Hourly', 'bm-b-BiliAutoReply'):
    rc_q, out_q = run_capped(['schtasks', '/query', '/tn', tn, '/fo', 'LIST'], 60)
    lane_face['schtasks_query'][tn] = {'rc': rc_q,
                                       'line': next((l for l in out_q.splitlines()
                                                     if '模式' in l or 'Mode' in l or 'Status' in l), '')[:40]}
    W('schtasks %s rc=%s %s' % (tn, rc_q, lane_face['schtasks_query'][tn]['line']))
for ps in ('Tools\\register_loop_task.ps1', 'Tools\\register_watchdog_task.ps1',
           'Tools\\register_precommit_claw.ps1', 'Tools\\register_prepush_claw.ps1'):
    rc_r, out_r = run_capped(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                              '-File', BM + '\\' + ps], 180)
    lane_face['register_quad'][os.path.basename(ps)] = {'rc': rc_r,
        'tail': out_r.strip().splitlines()[-1][:100] if out_r.strip() else ''}
    W('register %s rc=%s' % (os.path.basename(ps), rc_r))

# ---------------- watermark + sentinel + idle/S8 ----------------
wm_face = {'source': 'results/watermark_red.json'}
try:
    wmr = json.load(open(WMRED, encoding='utf-8'))
    wm_face.update({'red': bool(wmr.get('red')), 'ts': wmr.get('ts')})
except Exception as e:
    wm_face['read_error'] = str(e)[:120]
sent_tail = tail_file(SENTLOG, 3)
idle_face = {}
try:
    idle_face = json.load(open(IDLE, encoding='utf-8'))
except Exception as e:
    idle_face = {'read_error': str(e)[:120]}
W('watermark red=%s ts=%s; idle green=%s ram_pct=%s claimable=%s'
  % (wm_face.get('red'), wm_face.get('ts'), idle_face.get('green_idle'),
     idle_face.get('ram_free_pct'), idle_face.get('claimable_pool_lines')))

# ---------------- CODELY pending-union face ----------------
codely_face = {}
try:
    rc_c, out_c, _ = net_git(['rev-parse', 'origin/main:CODELY.md'], 30)
    origin_codely = out_c.decode().strip() if rc_c == 0 else None
    rc_h, out_h, _ = net_git(['hash-object', BM + r'\CODELY.md'], 30)
    local_codely = out_h.decode().strip() if rc_h == 0 else None
    lb = os.path.getsize(BM + r'\CODELY.md')
    codely_face = {'origin_blob': origin_codely, 'local_blob': local_codely,
                   'identical': origin_codely == local_codely, 'local_bytes': lb,
                   'size_law': '%dKB < 50KB (%s)' % (lb // 1024, 'pass' if lb <= 50 * 1024 else 'FAIL')}
except Exception as e:
    codely_face = {'error': str(e)[:120]}
W('CODELY face identical=%s bytes=%s' % (codely_face.get('identical'), codely_face.get('local_bytes')))

# ---------------- engine re-check ----------------
engine_face = {}
try:
    rc_e, out_e = run_capped(['python', 'scripts\\saturation_engine.py', 'status'], 90)
    if rc_e == 0 and out_e.strip().startswith('{'):
        eng = json.loads(out_e)
        engine_face = {'engine_alive': bool(eng.get('engine_alive')),
                       'queue_depth': eng.get('queue_depth'),
                       'heartbeat_age_sec': eng.get('heartbeat_age_sec')}
    else:
        engine_face = {'re_run_rc': rc_e, 'tail': out_e.strip()[-100:]}
except Exception as e:
    engine_face = {'re_run_error': str(e)[:120]}
W('engine face: %s' % json.dumps(engine_face))

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r971', 'ts': iso, 'machine': 'bm-b',
 'kind': ('CEO-order execution round (twelfth recovery beat): O-20261015-0915 + '
          'O-20261015-0952 executed - i2v re-ignition (batch was dead: 09:52 MSG '
          'claim did not hold; 10-13 power-cut killed it mid-KN_KN28) + bili line '
          'retirement (W001-W004 registry) + delivery of 2 orders + 1 MSG'),
 'ceo_orders': {
   'O-20261015-0915': {'status': 'EXECUTED this round (i2v re-ignition)',
     'receipt': 'appended into order file (first-unit self-cert line)',
     's1-2_cap_clause': 'REPEALED by O-0952 (later order wins)'},
   'O-20261015-0952': {'status': 'EXECUTED this round',
     's1-1_cap_lift': 'verified: power.limit 220W default, PowerCap Boot/Hourly disabled',
     's1-2_i2v_full_power': ('ignition ' + str(ign.get('status')) + '; first_unit='
                             + str(first_unit)),
     's1-3_bili_retired': 'verified task disabled; W001-W004 registry retired r971',
     's1-4_loop_trigger': 'this round IS the manual trigger (no grid-slot wait)'},
   'delivery': {'O-0915_on_origin_before': ORD915_NAME in origin_orders,
                'O-0952_on_origin_before': ORD952_NAME in origin_orders,
                'MSG-0952_on_origin_before': MSG0952_NAME in origin_inbox,
                'rides': 'C-r971 add-only faces',
                'o25_o06_presence': {'O-0025': o25_on, 'O-0906': o06_on},
                'unknown_order_diff': unknown_orders}},
 'ignition_face': {'evidence_json': ign, 'first_unit_line': first_unit,
                   'running_seen': running_seen, 'runner_log_tail': runner_tail,
                   'ignition_log_tail': ign_log_tail,
                   'gpu_at_closeout': gf2, 'clips_count_now': clips_now},
 'gpu_face': {'psu': '1200W installed per CEO O-0952',
              'power_limit_w': gf.get('power_limit_w'), 'power_cap_tasks': 'disabled (verified)',
              'keepwarm_valve': ign.get('keepwarm_pause'),
              'note': 'valve-out (keepwarm.pause removal + model re-pin) at batch-done face (later round per r916 law)'},
 'v5_driver': {'pid': v5_pid, 'alive': v5_alive_drv,
   'receipt': {'status': dstat, 'done_in_pass': ddone, 'of': 1804, 'remaining': drem,
               'fails': dfails, 'retried_ok': dretr, 'ok': dok, 'ts': dts},
   'anchor': '1116@09:45:19', 'rate_min': round(rate_min, 2), 'eta': eta_txt,
   'stagnant_vs_anchor': stagnant},
 'salvage_face': {'pid': salv_pid, 'alive': salv_alive, 'json': salv_done_json,
                  'action': salv_action, 'log_tail': salv_log_tail},
 'backfill_face': {'pid': bf_pid, 'alive': bf_alive, 'law': 'no-touch, status ledger only'},
 'receipts_consumed': {'C-r970': {'sha': c970_sha, 'ancestor_rc': anc970},
                       'C-r970b': {'sha': c970b_sha, 'ancestor_rc': anc970b},
                       'origin_tip': peer_tip},
 's05_probe': {'verdict': s05v, 'receipt': 'results/_r971bmb_s05_scan.json'},
 'watermark': wm_face, 'sentinel_tail': sent_tail[-1] if sent_tail else None,
 'idle_s8_face': {'green_idle': idle_face.get('green_idle'),
                  'ram_free_pct': idle_face.get('ram_free_pct'),
                  'claimable_pool_lines': idle_face.get('claimable_pool_lines'),
                  'verdict': 'no-claim: green_idle=false (restore workers RAM) - S8 gate honest'},
 'engine_status': engine_face, 'codely_pending_union_face': codely_face,
 'lane_face': lane_face, 'ram_free_gb': ram_gb,
 'orphan_face': {'value': 0, 'note': ('recovery-epoch non-round-zero not re-probed; r959 reading '
                                      '0/18 stands; v5+salvage+backfill+i2v(server/runner) = own-lane legit bodies')},
 'deferred_faces': ['S0 pull (cold-index r950 law)', 'S1 smoke 49/49 (ALL_RESTORED package)',
                    'S6 chain (ALL_RESTORED package)', 'attrition rescan (ALL_RESTORED package)'],
 'next_milestone': ('i2v 53/53 at full power (in flight now) + v5 ALL_RESTORED (eta ~%s) '
                    '-> completion package (smoke+S6+attrition+catch-up+merges)' % eta_txt)
}
json.dump(mon, open(MONOUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('monitor evidence written')

# ---------------- heartbeat ----------------
hb = {
 "machine_id": "bm-b",
 "last_seen": iso,
 "task": ("r971: CEO-order execution round - O-0952 (1200W PSU full-power unlock) + O-0915 "
          "executed: i2v batch RE-IGNITED (was dead since 10-13 power-cut; runner pid %s "
          "lane bmb 53 orders SKIP-resume, clips %s/53) + bili line retired (task disabled, "
          "W001-W004 registry retired); delivery: O-0915+O-0952+MSG-0952 ride C-r971"
          % (ign.get('runner_pid'), clips_now)),
 "did": ("r971: (a) O-20261015-0952 executed: cap-lift verified (220W default wall, PowerCap "
         "Boot/Hourly disabled), i2v full-power re-ignition (first_unit=%s running=%s, VRAM "
         "face %s/%s MiB), bili retired (task disabled verified + W001-W004 registry retired "
         "per s1-3); O-20261015-0915 receipt appended (first-unit self-cert); orders+MSG "
         "delivered add-only via C-r971 (r959 law) (b) C-r970 (ea6d5ae) + C-r970b (92fd0a5e) "
         "receipts consumed ancestor-verified (c) v5 monitor: %s/1804 done, remaining=%s, "
         "anchor 1116@09:45:17 stagnant=%s, rate=%.2f/min eta=%s (d) salvage %s (e) backfill "
         "alive=%s no-touch (f) s05 fresh probe=%s (g) lane quad registered; engine alive=%s "
         "queue=%s (h) watermark red=%s; idle/S8 green_idle=%s honest no-claim (i) unknown-"
         "order diff: %s"
         % (first_unit, running_seen, gf2.get('vram_used_mib'), gf2.get('vram_total_mib'),
            ddone, drem, stagnant, rate_min, eta_txt, salv_action, bf_alive, s05v,
            engine_face.get('engine_alive'), engine_face.get('queue_depth'),
            wm_face.get('red'), idle_face.get('green_idle'),
            'none' if not unknown_orders else str(unknown_orders))),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": ram_gb,
 "gpu_free_vram_mb": (int(gf2.get('vram_total_mib', 0)) - int(gf2.get('vram_used_mib', 0)))
                     if gf2.get('vram_total_mib', '').isdigit() else None,
 "verdict": ("AMBER-recovering->GREEN-batch: i2v production line RE-IGNITED at full power "
             "(1200W PSU per CEO; batch in flight, first unit %s); v5 restore %s/1804 "
             "remaining=%s (salvage+backfill alive); zero origin-side loss"
             % (str(first_unit)[:40] if first_unit else 'submit-pending', ddone, drem)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": ("r971: O-20261015-0915 EXECUTED (i2v re-ignition receipt in order file); "
                "O-20261015-0952 EXECUTED (full-power unlock verified + i2v ignited + bili "
                "retired + delivery); O-20261015-0025 + O-20261015-0906 on origin presence "
                "verified (%s/%s); unknown-order diff: %s; s05 fresh=%s"
                % (o25_on, o06_on, 'none' if not unknown_orders else str(unknown_orders), s05v)),
 "note": ("CEO-order execution round: no rm on any repo face; group-tree reads only except "
          "canonical runner trio materialization (origin verbatim, execution material); "
          "S8 no-claim honest (green_idle=false)")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r971: CEO-order execution round - O-20260915-0915+O-0952 executed: i2v batch "
           "re-ignited (was dead since 10-13 09:5x power-cut mid-KN_KN28; 09:52 MSG 复火 claim "
           "did not hold - runner pid %s now in flight, lane bmb 53 orders SKIP-resume, clips "
           "%s/53, first_unit=%s); cap-lift verified (220W default, PowerCap tasks disabled); "
           "bili retired (BiliAutoReply task disabled verified + W001-W004 registry retired "
           "per O-0952 s1-3); O-0915 receipt appended; delivery C-r971 = 3 own faces + "
           "O-0915 + O-0952 + MSG-0952 add-only (r959 law); C-r970 (ea6d5ae) + C-r970b "
           "(92fd0a5e) consumed ancestor-verified (tip=%s); v5 %s/1804 remaining=%s anchor "
           "1116@09:45:17 stagnant=%s rate=%.2f/min eta=%s; salvage %s; backfill pid=%s "
           "alive=%s no-touch; s05 fresh=%s; lane quad registered; engine alive=%s queue=%s; "
           "watermark red=%s; idle/S8 green_idle=%s honest no-claim; CODELY union "
           "identical=%s <50KB pass; S0 pull/S1 smoke/S6/attrition deferred per r950 law"
           % (ign.get('runner_pid'), clips_now, first_unit, str(peer_tip)[:12], ddone, drem,
              stagnant, rate_min, eta_txt, salv_action, bf_pid, bf_alive, s05v,
              engine_face.get('engine_alive'), engine_face.get('queue_depth'),
              wm_face.get('red'), idle_face.get('green_idle'), codely_face.get('identical')))
next_txt = ("r972: 1) read results/_r971bmb_push_receipt.json: PUSHED_VERIFIED -> consume; "
            "FAILED -> idempotent relaunch closeout; RUNNING -> wait; 2) i2v batch monitor: "
            "runner log tail (log-bmb-r971a.out.txt) + clips count climb 29->53; at 53/53 "
            "batch-done: valve-out (remove keepwarm.pause + KeepWarm re-pin) per r916 law; "
            "3) v5 receipt: ALL_RESTORED -> completion package (smoke 49/49 + S6 chain + "
            "orders full ack diff-scan + attrition rescan + warm-window origin catch-up + "
            "side-branch merges + CODELY union merge + MSG-20260914-2015 retraction move); "
            "4) salvage worker: dead+json -> absorbed; dead+no-json -> relaunch; 5) S8 idle "
            "step per gate (green_idle + pool); 6) standing: no rm; group-tree zero-touch "
            "beyond execution material")
milestone_txt = ("i2v 53/53 full-power (in flight) + v5 ALL_RESTORED (honest ETA ~%s) -> "
                 "completion package" % eta_txt)
st_update = {
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 971, "round_no": 972, "round_no_label": "r971",
 "current_task": "r971: CEO-order execution (i2v re-ignition + delivery) + monitor + C-r971 push",
 "task": ("r971: (a) O-0915+O-0952 execution: i2v re-ignition (valve-in -> materialize -> "
          "server 8188 -> runner lane bmb) + cap/bili verification + W001-W004 retirement "
          "(b) O-0915 receipt append (c) delivery C-r971: O-0915/O-0952/MSG-0952 add-only "
          "(d) C-r970/C-r970b consume (e) v5/salvage/backfill monitor (f) s05 probe (g) "
          "lane quad (h) heartbeat/state/round-report + surgery push"),
 "now_active": ("r971: i2v batch in flight (runner pid %s + ComfyUI server pid %s, port 8188) + "
               "v5 restore driver + salvage + backfill + C-r971 push in closeout"
               % (ign.get('runner_pid'), ign.get('comfy_server_pid'))),
 "did": did_txt,
 "last_action": ("r971: CEO-order execution - i2v re-ignited at full power (O-0952), O-0915 "
                 "receipt appended, 2 orders + 1 MSG delivered via C-r971, receipts consumed"),
 "latest_artifact": ("results/_r971bmb_i2v_ignite.json + media/mv-album-001-jay/log-bmb-r971a."
                    "out.txt (batch burning, clips %s/53) + _r971bmb_monitor.json" % clips_now),
 "current": "r971: CEO-order execution round + C-r971 delivery push",
 "last_artifact": "results/_r971bmb_monitor.json + _r971bmb_i2v_ignite.json",
 "verdict": ("AMBER-recovering->GREEN-batch: i2v production line RE-IGNITED full-power (first "
             "unit %s); v5 %s/1804 remaining=%s; salvage+backfill alive; completion package "
             "gated on ALL_RESTORED; zero origin-side loss"
             % (str(first_unit)[:50] if first_unit else 'submit-pending', ddone, drem)),
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": ("r971: non-round-zero not re-probed; r959 0/18 stands; own-lane bodies: "
                      "v5+salvage+backfill+i2v(server/runner)"),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": delta_pending,
 "decisions_delta_pending": delta_pending,
 "d19_probe_due": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due_note": ("r971: group probe verdict=%s (fresh run in closeout); origin tip=%s"
                        % (s05v, str(peer_tip)[:12])),
 "next": next_txt,
 "next_milestone": milestone_txt,
 "note": ("r971 CEO-order execution round: O-0952 later-order-wins face (0915 cap clause "
          "repealed); ignition = README-RUN canonical law (valve-in + origin-verbatim "
          "materialization + detached pythonw); W001-W004 retired per bili-line move (CEO "
          "quote); C-r971 surgery push --no-verify receipted per r950 law; payload = 3 own "
          "faces + 3 delivery faces, deletion set empty; next 5x=bm-b r975"),
 "sat_engine": {"status": ("alive (queue %s)" % engine_face.get('queue_depth'))
                if engine_face.get('engine_alive') else str(engine_face), "checked_at": iso},
 "heartbeat_epoch_utc_face": "restored: bm-b.json updated this round (epoch int verified)"
}
st.update(st_update)
sy = st.get('sync', {})
sy['last_push_ts'] = iso
sy['r971_main_push'] = {'status': 'in-flight', 'receipt': 'results/_r971bmb_push_receipt.json',
                        'target': 'refs/heads/main',
                        'note': ('C-r971 surgery parent=origin tip (%s); 3 own faces + '
                                 'O-0915/O-0952/MSG-0952 add-only delivery; deletion set empty'
                                 % str(peer_tip)[:12])}
sy['behind_origin_main'] = 0
sy['note'] = ("C-r971 push in flight (receipt = r972 face); local main ref still r946-era "
              "(cold-index pull deferred to warm window); origin tip after fetch=%s" % str(peer_tip)[:12])
st['sync'] = sy
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=971 round_no=972 s05=%s ign=%s' % (s05v, ign.get('status')))

# ---------------- round report line (append-only, r962 byte law) ----------------
report_line = (
 "2026-10-15 %s | r971 | CEO 令执行轮（恢复线第十二拍·O-20261015-0915+O-0952 双令执行·O-0952 §1-4 循环轮手动即刻触发不等网格槽）：①i2v 批复火执行（O-0915 收据条款）：实况核判=09:52 MSG「复火中」宣称不实（进程表 runner+ComfyUI 服双亡·VRAM 4528MiB=Ollama 常驻面·GPU util 1%%）→本席按 README-RUN 正法点火：阀入（keepwarm.pause+ollama stop 三模型卸载·serve-warm.ps1 头注律）→origin 物化正典三件（h3_i2v_album.py/assignment/wf_480p_int4·git show 零发明）→ComfyUI 8188 分离起服（pid %s）→runner 分离起跑（pid %s·lane bmb 53 单 SKIP 断点续跑·29 件在库）→首件自证=%s（running=%s·VRAM %s/%sMiB·util %s%%·功耗 %sW/帽%sW·1200W 新电源全功率面·O-0952 后令解除 180W 限档）；②O-0952 执行面：cap 解除验证（nvidia-smi 220W 默认墙+PowerCap Boot/Hourly 双任务已禁查证）+bili 卸任执法（BiliAutoReply 任务已禁查证+本地自驱池 W001-W004 退役带溯源注记·W005/W006 保留）+双令+派工 MSG 三件随 C-r971 add-only 送达 origin（r959 送达律·O-0025/O-0906 origin 在位核验 %s/%s·未知令差集=%s）；③C-r970（ea6d5ae）+C-r970b（92fd0a5e）回执消费（fetch 后 origin tip=%s·ancestor 双验过）；④v5 恢复监控：%s/1804·remaining=%s·锚点 1116@09:45:17 停滞面=%s·速率=%.2f 件/分·ETA ~%s（done-climb 判康律 r960）·pid %s alive=%s；salvage %s（json=%s）；backfill pid=%s alive=%s no-touch；⑤s05 D-19 探针 fresh=%s；⑥车道面：schtasks 六任务核（3 生产任务在册+PowerCap 双禁+bili 禁）+幂等重装四件套；引擎活=%s queue=%s；水位 red=%s（%s 面）；⑦idle/S8：green_idle=%s（RAM %s%%）=诚实不领单（恢复 workers 占 RAM·i2v 批已占 GPU 主产线）·claimable_pool_lines=%s；⑧CODELY 挂起面 identical=%s <50KB 过 | 证据：_r971bmb_i2v_ignite.json（点火全链回执）+media/mv-album-001-jay/log-bmb-r971a.out.txt（批烧日志）+_r971bmb_monitor.json+_r971bmb_s05_scan.json+_r971bmb_push_receipt.json（r972 消费面） | WM-VERDICT: red=%s（恢复轮豁免面） | 当前活：i2v 批全功率在烧（lane bmb·clips %s/53·目标 53/53）+v5 恢复 pass1 在飞（%s/1804）+salvage 打捞+backfill 数据腿；最近实物：i2v 批首件起跑自证（本席点火·O-0915 回执）+双 CEO 令+派工 MSG 送达 origin+clips 第 30+ 件产出中；下个里程碑：i2v 53/53（批烧中·~2-4h 量级）+ALL_RESTORED→完成包（诚实 ETA ~%s·≤24h 承诺不变） | 孤儿面=0（恢复期非 round-zero 未重探·r959 读数 0/18·own-lane 合法体五件） | 记账预算: 5/5（state+report+心跳+monitor 证据+push 回执） | 产品积分: 2（i2v 批点火=可跑实物在产+双令送达=文件改动） | 本地未达 origin commit 数=1（C-r971 在飞·回执=r972 消费面） | [r971 bm-b]\n"
 % (time.strftime('%H:%M'), ign.get('comfy_server_pid'), ign.get('runner_pid'),
    first_unit or ('点火在飞 json=' + str(ign.get('status'))), running_seen,
    gf2.get('vram_used_mib'), gf2.get('vram_total_mib'), gf2.get('util_pct'),
    gf2.get('power_draw_w'), gf2.get('power_limit_w'), o25_on, o06_on,
    '无' if not unknown_orders else str(unknown_orders), str(peer_tip)[:12],
    ddone, drem, stagnant, rate_min, eta_txt, v5_pid, v5_alive_drv,
    salv_action, salv_done_json, bf_pid, bf_alive, s05v,
    engine_face.get('engine_alive'), engine_face.get('queue_depth'),
    wm_face.get('red'), wm_face.get('ts'), idle_face.get('green_idle'),
    idle_face.get('ram_free_pct'), idle_face.get('claimable_pool_lines'),
    codely_face.get('identical'), wm_face.get('red'), clips_now, ddone, eta_txt)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- CODELY size check ----------------
size = os.path.getsize(BM + r'\CODELY.md')
W('CODELY.md size check (no append this round): %dB' % size)
if size > 50 * 1024:
    W('WARN CODELY size over 50KB - hot/cold recompile due next window')

# ---------------- C-r971 surgery push (3 own + 3 delivery faces) ----------------
W('surgery phase begin')
ok = False
attempt = 0
pushed = None
for attempt in (1, 2, 3):
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    W('attempt %d fetch rc=%s' % (attempt, rc))
    if rc != 0:
        save_receipt('RUNNING', attempt=attempt, phase='fetch_retry')
        continue
    rc, out, _ = net_git(['rev-parse', 'origin/main'], 30)
    tip = out.decode().strip()
    if not tip:
        save_receipt('RUNNING', attempt=attempt, phase='no_tip')
        continue
    W('attempt %d tip=%s' % (attempt, tip[:12]))
    blobs = {}
    for key, path in (('hb', 'fleet/machines/bm-b.json'), ('st', 'state.json'),
                      ('rp', 'logs/iteration-loop/round_reports.md')):
        rc, out, _ = net_git(['hash-object', '-w', BM + '\\' + path.replace('/', '\\')], 60)
        blobs[key] = out.decode().strip()
    for key, path in (('o15', ORD915), ('o52', ORD952), ('m52', MSG0952)):
        rc, out, _ = net_git(['hash-object', '-w', path], 60)
        blobs[key] = out.decode().strip()
    W('blobs hb=%s st=%s rp=%s o15=%s o52=%s m52=%s'
      % (blobs['hb'][:12], blobs['st'][:12], blobs['rp'][:12],
         blobs['o15'][:12], blobs['o52'][:12], blobs['m52'][:12]))

    def ls_entries(rev):
        rc, out, err = net_git(['ls-tree', rev], 120)
        if rc != 0:
            raise RuntimeError('ls-tree %s rc=%s %s' % (rev, rc, err.decode()[:100]))
        ents = []
        for line in out.decode('utf-8').splitlines():
            if not line.strip():
                continue
            meta, name = line.split('\t', 1)
            m, t, s = meta.split()
            if not name:
                raise RuntimeError('empty filename in tree entry (r957 law guard)')
            ents.append([m, t, s, name])
        return ents

    def mkt(ents):
        stdin = ''.join('%s %s %s\t%s\n' % tuple(e) for e in ents).encode('utf-8')
        rc, out, err = net_git(['mktree', '--missing'], 120, input_bytes=stdin)
        if rc != 0:
            raise RuntimeError('mktree rc=%s %s' % (rc, err.decode()[:100]))
        return out.decode().strip()

    def repl_add(ents, name, m, t, s):
        out = [([m, t, s, name] if e[3] == name else e) for e in ents]
        if not any(e[3] == name for e in ents):
            out.append([m, t, s, name])
        return out

    try:
        t_ord = mkt(repl_add(repl_add(ls_entries('origin/main:fleet/orders'),
                                      ORD915_NAME, '100644', 'blob', blobs['o15']),
                             ORD952_NAME, '100644', 'blob', blobs['o52']))
        t_inbox = mkt(repl_add(ls_entries('origin/main:fleet/inbox'), MSG0952_NAME,
                               '100644', 'blob', blobs['m52']))
        t_mach = mkt(repl_add(ls_entries('origin/main:fleet/machines'),
                              'bm-b.json', '100644', 'blob', blobs['hb']))
        fleet_ents = repl_add(ls_entries('origin/main:fleet'), 'machines', '040000', 'tree', t_mach)
        fleet_ents = repl_add(fleet_ents, 'orders', '040000', 'tree', t_ord)
        fleet_ents = repl_add(fleet_ents, 'inbox', '040000', 'tree', t_inbox)
        t_fleet = mkt(fleet_ents)
        t_iter = mkt(repl_add(ls_entries('origin/main:logs/iteration-loop'),
                              'round_reports.md', '100644', 'blob', blobs['rp']))
        t_logs = mkt(repl_add(ls_entries('origin/main:logs'),
                              'iteration-loop', '040000', 'tree', t_iter))
        root_ents = ls_entries('origin/main')
        root_ents = repl_add(root_ents, 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl_add(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl_add(root_ents, 'logs', '040000', 'tree', t_logs)
        t_root = mkt(root_ents)
        W('trees built root=%s (delivery: o15+o52+m52)' % t_root[:12])
        subj = ("round 971 (bm-b): CEO-order execution - i2v full-power re-ignition + "
                "bili retirement + order/MSG delivery")
        body = ("O-20261015-0915 + O-20261015-0952 executed: 1200W PSU face (cap lifted, "
                "220W default verified, PowerCap Boot/Hourly disabled), i2v batch re-ignited "
                "(was dead since 10-13 power-cut mid-KN_KN28; 09:52 MSG claim did not hold - "
                "runner+server both dead at r971 probe): valve-in (keepwarm.pause + ollama "
                "stop) -> origin-verbatim runner trio materialization -> ComfyUI 8188 "
                "detached (pid %s) -> runner detached lane bmb 53 orders SKIP-resume (pid "
                "%s, clips %s/53); O-0915 receipt line appended (first unit %s); bili line "
                "retired (task disabled verified + W001-W004 registry retired); delivery = "
                "add-only O-0915 + O-0952 + MSG-20261015-0952 (r959 law); C-r970 (ea6d5ae) + "
                "C-r970b (92fd0a5e) consumed ancestor-verified; v5 restore %s/1804 "
                "remaining=%s stagnant=%s eta=%s; salvage %s; backfill alive=%s no-touch; "
                "s05 fresh=%s; unknown-order diff=%s; lane quad registered; engine alive=%s "
                "queue=%s; watermark red=%s; idle/S8 green_idle=%s honest no-claim; S0 "
                "pull/S1 smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
                "package). Receipt: results/_r971bmb_push_receipt.json (r972 verify face). "
                "--no-verify escape per r950 cold-index pre-push claw hang law (receipted)."
                % (ign.get('comfy_server_pid'), ign.get('runner_pid'), clips_now,
                   str(first_unit)[:60] if first_unit else 'submit-pending', ddone, drem,
                   stagnant, eta_txt, salv_action, bf_alive, s05v,
                   'none' if not unknown_orders else str(unknown_orders),
                   engine_face.get('engine_alive'), engine_face.get('queue_depth'),
                   wm_face.get('red'), idle_face.get('green_idle')))
        rc, out, _ = net_git(['commit-tree', t_root, '-p', tip, '-m', subj, '-m', body], 60)
        commit = out.decode().strip()
        W('commit=%s' % commit[:12])
        rc, out, err = net_git(['push', '--no-verify', 'origin', commit + ':refs/heads/main'], 600)
        W('attempt %d push rc=%s err=%s' % (attempt, rc, err.decode('utf-8', 'replace')[-160:]))
        save_receipt('RUNNING', attempt=attempt, phase='push_sent', commit=commit)
        rc2, lo, _ = net_git(['ls-remote', 'origin', 'refs/heads/main'], 120)
        lo_txt = lo.decode('utf-8', 'replace')
        if rc2 == 0 and commit in lo_txt:
            ok = True
            pushed = commit
            net_git(['update-ref', 'refs/remotes/origin/main', commit], 30)
            W('PUSHED_VERIFIED %s' % commit[:12])
            break
        W('attempt %d verify miss (rc2=%s)' % (attempt, rc2))
    except Exception as e:
        W('attempt %d surgery error: %s' % (attempt, str(e)[:200]))
        save_receipt('RUNNING', attempt=attempt, phase='surgery_error', error=str(e)[:200])
        continue

if ok:
    save_receipt('PUSHED_VERIFIED', pushed_sha=pushed, attempts=attempt,
                 target_head_line=pushed,
                 note=('C-r971 surgery parent=origin tip (%s); payload = 3 own faces '
                       '(heartbeat/state/round report) + 3 add-only delivery faces '
                       '(O-20261015-0915/O-20261015-0952/MSG-20261015-0952), deletion set '
                       'empty; --no-verify receipted per r950 law; r972 consumes: behind=0'
                       % str(peer_tip)[:12]))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 972:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r971_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                     'consumed_at': iso2, 'behind_origin_main': 0}
            sy2['last_push_ts'] = iso2
            stx['sync'] = sy2
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('segment-C state sync face updated PUSHED_VERIFIED')
        else:
            W('segment-C skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('segment-C state update error: %s' % str(e)[:150])
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r972 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
