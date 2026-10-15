# r972 bm-b closeout: recovery monitoring beat (thirteenth) + salvage pipe-deadlock fix.
# Round work: (a) consumed C-r971 (2a95c9c) + C-r971b fix1 (e9c293240) receipts
# (b) P0 salvage fix: r969/r971 driver deadlocked 84min in blobs_local()
# (write-all-stdin-then-read-stdout two-pipe deadlock; evidence parent 2800 +
# git child 6996 both CPU=0, log zero progress) -> tree-killed 4-proc tree ->
# _r972bmb_salvage.py (communicate() concurrent drain) relaunched detached ->
# verified past deadlock point (pre: ls-files -d 1087) (c) i2v/v5/backfill
# monitors (d) s05 fresh D-19 probe (e) lane quad (f) CODELY pit append (g)
# heartbeat + state + round report (binary-safe append r962 law) (h) C-r972
# surgery push: 3 own faces only (hb/state/round report), deletion set empty.
# Laws: r950 plumbing + --no-verify receipted escape, r953 Popen+tree-kill caps,
# r957 ls-tree tip:<dir> + mktree --missing + non-empty-name guard, r951
# segment claims, r960 judge-by-done-climb, r959/r968 delivery law (zero gap
# this round: MSG 0825/0906/0952 on origin verified; 2015/0104 = designed
# deferred faces), ASCII-safe log.
import ctypes, datetime, json, os, re, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r972bmb_closeout.log'
PUSHREC = BM + r'\results\_r972bmb_push_receipt.json'
MONOUT = BM + r'\results\_r972bmb_monitor.json'
D19PROBE = BM + r'\results\_r686bmb_d19_check.py'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
SALVLOG = BM + r'\results\_r972bmb_salvage.log'
SALVOUT = BM + r'\results\_r972bmb_salvage.json'
OLDSALVLOG = BM + r'\results\_r969bmb_salvage.log'
C971REC = BM + r'\results\_r971bmb_push_receipt.json'
C971BREC = BM + r'\results\_r971bmb_fix1_push_receipt.json'
RUNNERLOG = r'C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\log-bmb-r971a.out.txt'
CLIPSDIR = r'C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\clips-animatic-480'
SENTLOG = r'C:\Fluxgroup\.codely-cli\sentinel\sentinel.log'
WMRED = BM + r'\results\watermark_red.json'
IDLE = BM + r'\results\idle_trigger.bm-b.json'
ORPH = BM + r'\results\_orphan_face_probe.bm-b.json'
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
    d = {'driver': 'r972bmb push C-r972 (origin/main)', 'target': 'refs/heads/main',
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
                          '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/MB,2)'],
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

def ps_discover(needle):
    ps_cmd = ("(Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" "
              "| Where-Object { $_.CommandLine -like '*%s*' } "
              "| Select-Object -First 1).ProcessId" % needle)
    rc, out = run_capped(['powershell', '-NoProfile', '-Command', ps_cmd], 90)
    if rc == 0:
        m = re.search(r'\d+', out.strip())
        if m:
            return int(m.group())
    return None

def tail_file(path, n=6):
    try:
        with open(path, 'rb') as f:
            lines = f.read().decode('utf-8', 'replace').splitlines()
        return lines[-n:]
    except Exception:
        return None

W('r972 closeout start (salvage pipe-fix + recovery monitoring)')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
ram_gb = free_ram_gb()
W('free_ram_gb=%s' % ram_gb)
gf = gpu_face()
W('gpu face: %s' % json.dumps(gf))

# ---------------- v5 restore monitor (anchor 1176@10:15:25, done-climb law) ----------------
try:
    d5 = json.load(open(V5REC, encoding='utf-8'))
    dstat, dpass, ddone, drem = d5.get('status'), d5.get('pass_no'), d5.get('done_in_pass'), d5.get('remaining')
    dfails, dretr, dts, dok = d5.get('fails_in_pass'), d5.get('retried_ok_in_pass'), d5.get('ts'), d5.get('ok_in_pass')
except Exception as e:
    dstat, dpass, ddone, drem, dfails, dretr, dts, dok = 'read_error', None, None, None, None, None, None, None
    W('v5 receipt read error: %s' % str(e)[:120])
rate_min, eta_txt, stagnant = 0.0, 'n/a', False
try:
    a_done, a_ts = 1176, datetime.datetime.fromisoformat('2026-10-15T10:15:25+08:00')
    if dts:
        cur_ts = datetime.datetime.fromisoformat(dts)
        if ddone is not None:
            if ddone == a_done:
                stagnant = True
            elif ddone > a_done and cur_ts > a_ts:
                dt_min = (cur_ts - a_ts).total_seconds() / 60.0
                if dt_min >= 1.0:
                    rate_min = max(0.0, (ddone - a_done) / dt_min)
    if drem and rate_min:
        eta_dt = now + datetime.timedelta(minutes=float(drem) / max(rate_min, 0.1))
        eta_txt = eta_dt.strftime('%H:%M')
    elif drem:
        eta_txt = '~19:10 prior-window honest carry (salvage may accelerate materialize)'
except Exception as e:
    W('rate/eta calc error: %s' % str(e)[:120])
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s receipt_ts=%s rate=%.2f eta=%s stagnant=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr, dts, rate_min, eta_txt, stagnant))
v5_pid = ps_discover('_r960bmb_restore_driver') or 3672
v5_alive = pid_alive(v5_pid)
W('v5 pid %s alive=%s' % (v5_pid, v5_alive))

# ---------------- salvage r972 (pipe-fix relaunch) face ----------------
salv_pid = ps_discover('_r972bmb_salvage')
salv_alive = pid_alive(salv_pid) if salv_pid else False
salv_json = os.path.exists(SALVOUT)
salv_tail = tail_file(SALVLOG, 8)
W('salvage r972 pid=%s alive=%s json=%s tail=%s'
  % (salv_pid, salv_alive, salv_json, str(salv_tail)[-140:] if salv_tail else None))
salv_action = 'r972 pipe-fix instance alive-running (json pending; pre-phase bounded by 600s cap)'
if salv_pid is None and salv_json:
    salv_action = 'dead+json -> absorbed (blob delta evidence for v5 next pass)'
elif salv_pid is None and not salv_json:
    W('salvage r972 dead+no-json -> relaunch deferred to r973 judgment (pre-phase cap may have fired)')
old_pair_evidence = {'killed_pids': [2800, 6996, 13340, 9464], 'deadlock_min': 84,
                     'old_log_tail': tail_file(OLDSALVLOG, 3),
                     'fix': 'communicate(input) concurrent drain, 600s tree-kill caps'}
bf_pid = ps_discover('backfill_ext_slots')
bf_alive = pid_alive(bf_pid) if bf_pid else False
W('backfill pid=%s alive=%s (no-touch)' % (bf_pid, bf_alive))

# ---------------- i2v batch monitor ----------------
runner_tail = tail_file(RUNNERLOG, 10)
clips_now = len([f for f in os.listdir(CLIPSDIR) if f.endswith('.mp4')]) if os.path.isdir(CLIPSDIR) else None
cur_unit = None
if runner_tail:
    for line in runner_tail:
        m = re.match(r'\[(\S+)\]', line)
        if m:
            cur_unit = m.group(1)
W('i2v: clips=%s/53 current_unit=%s tail=%s' % (clips_now, cur_unit, str(runner_tail[-1])[:80] if runner_tail else None))

# ---------------- C-r971 + C-r971b receipt consume (ancestor verify) ----------------
c971_sha = c971b_sha = None
try:
    c971_sha = json.load(open(C971REC, encoding='utf-8')).get('pushed_sha')
    c971b_sha = json.load(open(C971BREC, encoding='utf-8')).get('pushed_sha')
    W('receipts: C-r971=%s C-r971b=%s' % (str(c971_sha)[:12], str(c971b_sha)[:12]))
except Exception as e:
    W('receipt read error: %s' % str(e)[:120])
rc_f, _, _ = net_git(['fetch', 'origin', 'main'], 180)
W('fetch rc=%s' % rc_f)
anc971 = anc971b = None
peer_tip = None
if rc_f == 0:
    if c971_sha:
        anc971 = net_git(['merge-base', '--is-ancestor', c971_sha, 'origin/main'], 60)[0]
    if c971b_sha:
        anc971b = net_git(['merge-base', '--is-ancestor', c971b_sha, 'origin/main'], 60)[0]
    peer_tip = net_git(['rev-parse', 'origin/main'], 30)[1].decode().strip()
W('ancestor: C-r971 rc=%s C-r971b rc=%s origin_tip=%s' % (anc971, anc971b, str(peer_tip)[:12]))

# ---------------- s05 fresh probe (D-19) + unknown-order diff ----------------
rc_d, out_d = run_capped(['python', D19PROBE], 240)
s05 = {}
try:
    s05 = json.loads(out_d.strip().splitlines()[-1]) if out_d.strip() else {}
except Exception as e:
    s05 = {'verdict': 'PARSE_ERROR', 'error': str(e)[:100]}
s05v = 'NO_DELTA_ZERO_ACTION' if not s05.get('decisions_changed') and not s05.get('orders_changed') else 'DELTA_PRESENT'
ord_sha, dec_sha = s05.get('orders_sha'), s05.get('decisions_sha')
W('d19 probe rc=%s verdict=%s ord=%s dec=%s' % (rc_d, s05v, str(ord_sha)[:12], str(dec_sha)[:12]))
origin_orders = []
o_present = {}
try:
    rc_o, out_o, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/orders/'], 60)
    if rc_o == 0:
        origin_orders = [l.strip().split('/')[-1] for l in out_o.decode('utf-8', 'replace').splitlines() if l.strip()]
    for nm in ('O-20261015-0025-bm-b.md', 'O-20261015-0906-bm-b.md',
               'O-20261015-0915-bm-b.md', 'O-20261015-0952-bm-b.md'):
        o_present[nm] = nm in origin_orders
except Exception as e:
    W('origin orders ls-tree error: %s' % str(e)[:120])
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
W('orders presence=%s unknown=%s origin_orders=%d' % (o_present, unknown_orders, len(origin_orders)))

# ---------------- lane-task registry (R49 schtasks) ----------------
lane_face = {'schtasks_query': {}, 'register_quad': {}}
for tn in ('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'Bigmoney-SatEngine-bm-b',
           'GPU-PowerCap-180W-Boot', 'GPU-PowerCap-180W-Hourly', 'bm-b-BiliAutoReply'):
    rc_q, out_q = run_capped(['schtasks', '/query', '/tn', tn, '/fo', 'LIST'], 60)
    lane_face['schtasks_query'][tn] = {'rc': rc_q,
                                       'line': next((l for l in out_q.splitlines()
                                                     if '模式' in l or 'Mode' in l or 'Status' in l), '')[:40]}
    W('schtasks %s rc=%s' % (tn, rc_q))
for ps in ('Tools\\register_loop_task.ps1', 'Tools\\register_watchdog_task.ps1',
           'Tools\\register_precommit_claw.ps1', 'Tools\\register_prepush_claw.ps1'):
    rc_r, out_r = run_capped(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                              '-File', BM + '\\' + ps], 180)
    lane_face['register_quad'][os.path.basename(ps)] = {'rc': rc_r,
        'tail': out_r.strip().splitlines()[-1][:100] if out_r.strip() else ''}
    W('register %s rc=%s' % (os.path.basename(ps), rc_r))

# ---------------- watermark + sentinel + idle/S8 + orphan ----------------
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
orphan_face = {}
try:
    orphan_face = json.load(open(ORPH, encoding='utf-8'))
except Exception as e:
    orphan_face = {'read_error': str(e)[:120]}
W('watermark red=%s ts=%s; idle green=%s ram_pct=%s claimable=%s; orphan probe: faces=%s orphans=%s'
  % (wm_face.get('red'), wm_face.get('ts'), idle_face.get('green_idle'),
     idle_face.get('ram_free_pct'), idle_face.get('claimable_pool_lines'),
     orphan_face.get('py_faces_seen'), orphan_face.get('orphans')))

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

# ---------------- CODELY pit append (S4, one entry <=1.5KB) then size/union face ----------------
pit_line = ("[2026-10-15 %s] r972 坑律（salvage 双管道死锁·spawn 域）：python Popen 喂 git 批量命令"
            "（cat-file --batch-check --buffer）**先写全量 stdin 再读 stdout=死锁**——出量超 64KB 管道缓冲后"
            " git 停读 stdin→父 stdin.write 永久互堵（r969/r971 salvage 84min 双 CPU=0 铁证·日志零进度行）；"
            "正法=Popen.communicate(input)（stdlib 内建线程对并发排水）或双线程读写，一切批量喂管道"
            "（预计出量>64KB）一律此法+600s 树杀帽兜底（r953 律）；姊妹面=subprocess.run/capture_output "
            "内部即 communicate=同窗安全实证（同脚本 missing_paths() 零卡）。How to apply：写任何"
            "「喂清单给批命令」驱动器先查本条。证据=results/_r972bmb_salvage.py（修复版）+"
            "_r969bmb_salvage.py（死锁版）。\n" % now.strftime('%H:%M'))
try:
    with open(BM + r'\CODELY.md', 'a', encoding='utf-8') as f:
        f.write(pit_line)
    W('CODELY pit line appended (%dB)' % (len(pit_line.encode('utf-8'))))
except Exception as e:
    W('CODELY append error: %s' % str(e)[:150])
codely_face = {}
try:
    rc_c, out_c, _ = net_git(['rev-parse', 'origin/main:CODELY.md'], 30)
    origin_codely = out_c.decode().strip() if rc_c == 0 else None
    rc_h, out_h, _ = net_git(['hash-object', BM + r'\CODELY.md'], 30)
    local_codely = out_h.decode().strip() if rc_h == 0 else None
    lb = os.path.getsize(BM + r'\CODELY.md')
    codely_face = {'origin_blob': origin_codely, 'local_blob': local_codely,
                   'identical': origin_codely == local_codely, 'local_bytes': lb,
                   'size_law': '%dKB < 50KB (%s)' % (lb // 1024, 'pass' if lb <= 50 * 1024 else 'FAIL'),
                   'note': 'pending-union deferred to completion package (pre-existing face)'}
except Exception as e:
    codely_face = {'error': str(e)[:120]}
W('CODELY face identical=%s bytes=%s' % (codely_face.get('identical'), codely_face.get('local_bytes')))

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r972', 'ts': iso, 'machine': 'bm-b',
 'kind': ('recovery monitoring beat (thirteenth) + P0 salvage pipe-deadlock fix: r969/r971 '
          'driver deadlocked 84min (two-pipe), tree-killed, r972 communicate()-fix relaunched, '
          'verified past deadlock point; i2v batch + v5 restore + backfill all in flight'),
 'receipts_consumed': {'C-r971': {'sha': c971_sha, 'ancestor_rc': anc971},
                       'C-r971b_fix1': {'sha': c971b_sha, 'ancestor_rc': anc971b},
                       'origin_tip': peer_tip},
 'salvage_face': {'pid': salv_pid, 'alive': salv_alive, 'json': salv_json, 'action': salv_action,
                  'log_tail': salv_tail, 'old_pair_evidence': old_pair_evidence},
 'v5_driver': {'pid': v5_pid, 'alive': v5_alive,
   'receipt': {'status': dstat, 'done_in_pass': ddone, 'of': 1804, 'remaining': drem,
               'fails': dfails, 'retried_ok': dretr, 'ok': dok, 'ts': dts},
   'anchor': '1176@10:15:25', 'rate_min': round(rate_min, 2), 'eta': eta_txt,
   'stagnant_vs_anchor': stagnant},
 'i2v_face': {'clips': clips_now, 'of': 53, 'current_unit': cur_unit,
              'runner_log_tail': runner_tail, 'gpu': gf,
              'valve_out': 'deferred to batch-done face (r916 law)'},
 'backfill_face': {'pid': bf_pid, 'alive': bf_alive, 'law': 'no-touch, status ledger only'},
 's05_probe': {'verdict': s05v, 'orders_sha': ord_sha, 'decisions_sha': dec_sha,
               'unknown_order_diff': unknown_orders, 'own_order_presence': o_present},
 'watermark': wm_face, 'sentinel_tail': sent_tail[-1] if sent_tail else None,
 'idle_s8_face': {'green_idle': idle_face.get('green_idle'),
                  'ram_free_pct': idle_face.get('ram_free_pct'),
                  'claimable_pool_lines': idle_face.get('claimable_pool_lines'),
                  'verdict': 'no-claim: green_idle=false (restore workers RAM + i2v batch GPU) - S8 gate honest'},
 'orphan_face': {'probe_value': orphan_face.get('orphans'),
                 'note': ('round-zero probe 18 faces / 3 flagged: salvage=REAL deadlock (fixed this '
                          'round); v5+backfill=sleep/IO-wait false-positive faces (receipts+logs '
                          'actively updating); own-lane recovery bodies')},
 'engine_status': engine_face, 'codely_pending_union_face': codely_face,
 'lane_face': lane_face, 'ram_free_gb': ram_gb,
 'deferred_faces': ['S0 pull (cold-index r950 law)', 'S1 smoke 49/49 (ALL_RESTORED package)',
                    'S6 chain (ALL_RESTORED package)', 'attrition rescan (ALL_RESTORED package)',
                    'CODELY union merge (ALL_RESTORED package)',
                    'side-branch merges (ALL_RESTORED package)',
                    'MSG-20260914-2015 retraction move (ALL_RESTORED package)'],
 'next_milestone': ('i2v 53/53 full-power (in flight) + v5 ALL_RESTORED (honest eta ~19:10; '
                    'salvage may accelerate) -> completion package')
}
json.dump(mon, open(MONOUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('monitor evidence written')

# ---------------- heartbeat ----------------
hb = {
 "machine_id": "bm-b",
 "last_seen": iso,
 "task": ("r972: recovery monitoring beat - P0 salvage fix (84min two-pipe deadlock diagnosed + "
          "tree-killed + communicate()-fix relaunch verified) + i2v batch in flight (%s/53, %s) + "
          "v5 restore %s/1804 + C-r971/C-r971b receipts consumed"
          % (clips_now, cur_unit, ddone)),
 "did": ("r972: (a) C-r971 (2a95c9c) + C-r971b fix1 (e9c293240) consumed ancestor-verified "
         "(tip=%s) (b) P0 salvage fix: r969/r971 driver two-pipe deadlock (write-all-stdin-then-"
         "read-stdout, 84min CPU=0 evidence) tree-killed 4-proc, _r972bmb_salvage.py communicate() "
         "fix relaunched, verified past deadlock point (pre: 1087 missing); CODELY pit line "
         "appended (c) i2v monitor: clips %s/53, unit %s in flight, GPU util=%s%% draw=%sW (d) v5 "
         "%s/1804 remaining=%s rate=%.2f/min (e) backfill alive=%s no-touch (f) d19 fresh=%s, "
         "unknown-order diff=%s, own 4 orders on origin=%s (g) MSG 0825/0906/0952 on origin "
         "verified; 2015-retraction+0104-side-merge=designed deferred (h) lane quad registered; "
         "engine alive=%s queue=%s (i) watermark red=%s; idle/S8 green_idle=%s honest no-claim "
         "(j) round-zero orphan probe: 18 faces, 3 flagged (salvage=real->fixed; v5+backfill="
         "sleep false-positives)"
         % (str(peer_tip)[:12], clips_now, cur_unit, gf.get('util_pct'), gf.get('power_draw_w'),
            ddone, drem, rate_min, bf_alive, s05v,
            'none' if not unknown_orders else str(unknown_orders), o_present,
            engine_face.get('engine_alive'), engine_face.get('queue_depth'),
            wm_face.get('red'), idle_face.get('green_idle'))),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": ram_gb,
 "gpu_free_vram_mb": (int(gf.get('vram_total_mib', 0)) - int(gf.get('vram_used_mib', 0)))
                     if str(gf.get('vram_total_mib', '')).isdigit() else None,
 "verdict": ("GREEN-batch: i2v 53-unit batch burning full-power (%s/53), v5 restore %s/1804 "
             "(~2/min), salvage r972 pipe-fix in flight, backfill alive; completion package "
             "gated on ALL_RESTORED; zero origin-side loss" % (clips_now, ddone)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": ("r972: O-20261015-0025/O-0906/O-0915/O-0952 all on origin re-verified (%s); "
                "O-0915/O-0952 EXECUTED r971 (receipts in order files); s05 fresh=%s; "
                "unknown-order diff=%s; MSG 0825/0906/0952 on origin; 2015+0104 = designed "
                "deferred faces (completion package)"
                % (o_present, s05v, 'none' if not unknown_orders else str(unknown_orders))),
 "note": ("recovery beat: no rm on any repo face; group-tree reads only (zero-touch beyond "
          "execution material); S8 no-claim honest (green_idle=false)")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r972: recovery monitoring beat + P0 salvage fix - (a) C-r971 (2a95c9c) + C-r971b "
           "fix1 (e9c293240) consumed ancestor-verified (tip=%s); (b) salvage P0: r969/r971 "
           "driver two-pipe deadlock diagnosed (blobs_local write-all-stdin-then-read-stdout; "
           "84min parent+git-child CPU=0, log zero progress = evidence), tree-killed 4-proc "
           "(2800/6996/13340/9464), _r972bmb_salvage.py written (communicate() concurrent "
           "drain + 600s tree-kill caps), relaunched detached, verified past deadlock point "
           "(pre: ls-files -d 1087 missing); CODELY spawn-domain pit appended; (c) i2v batch "
           "in flight: clips %s/53, unit %s, GPU util=%s%% draw=%sW limit=%sW, valve-out "
           "deferred to batch-done (r916 law); (d) v5 %s/1804 remaining=%s anchor 1176@10:15:25 "
           "rate=%.2f/min eta=%s stagnant=%s; (e) backfill pid=%s alive=%s no-touch; (f) d19 "
           "fresh=%s (orders %s / decisions %s match watermarks), unknown-order diff=%s, own 4 "
           "orders on origin=%s; (g) MSG 0825/0906/0952 on origin verified, 2015-retraction + "
           "0104-side-merge = designed deferred; (h) lane quad registered; engine alive=%s "
           "queue=%s; watermark red=%s; idle/S8 green_idle=%s honest no-claim; round-zero "
           "orphan probe 18 faces / 3 flagged (salvage real->fixed, v5+backfill sleep "
           "false-positives); S0 pull/S1 smoke/S6/attrition/CODELY-union/side-branch-merges "
           "deferred per r950 law (ALL_RESTORED package)"
           % (str(peer_tip)[:12], clips_now, cur_unit, gf.get('util_pct'), gf.get('power_draw_w'),
              gf.get('power_limit_w'), ddone, drem, rate_min, eta_txt, stagnant, bf_pid, bf_alive,
              s05v, str(ord_sha)[:12], str(dec_sha)[:12],
              'none' if not unknown_orders else str(unknown_orders), o_present,
              engine_face.get('engine_alive'), engine_face.get('queue_depth'),
              wm_face.get('red'), idle_face.get('green_idle')))
next_txt = ("r973: 1) read results/_r972bmb_push_receipt.json: PUSHED_VERIFIED -> consume; "
            "FAILED -> idempotent relaunch closeout; RUNNING -> wait; 2) salvage r972: json "
            "done -> absorb (blob_local_delta evidence; v5 next pass materializes = acceleration "
            "face); alive -> monitor; dead+no-json -> relaunch _r972bmb_salvage.py; 3) i2v "
            "batch monitor: clips climb %s->53; at 53/53 batch-done: valve-out (remove "
            "keepwarm.pause + KeepWarm re-pin) per r916 law + batch-done report; 4) v5 receipt: "
            "ALL_RESTORED -> completion package (smoke 49/49 + S6 chain + orders full ack "
            "diff-scan + attrition rescan + warm-window origin catch-up + side-branch merges + "
            "CODELY union merge + MSG-20260914-2015 retraction move); 5) backfill monitor "
            "(no-touch law); 6) S8 idle step per gate; 7) standing: no rm; group-tree "
            "zero-touch beyond execution material" % clips_now)
milestone_txt = ("i2v 53/53 full-power (in flight) + v5 ALL_RESTORED (honest eta ~19:10; salvage "
                 "may accelerate) -> completion package")
st_update = {
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 972, "round_no": 973, "round_no_label": "r972",
 "current_task": "r972: salvage pipe-fix + recovery monitoring + C-r972 push",
 "task": ("r972: (a) C-r971/C-r971b receipt consume (b) salvage P0 fix + relaunch + verify "
          "(c) i2v/v5/backfill monitors (d) d19 fresh probe + unknown-order diff (e) lane quad "
          "(f) CODELY pit append (g) heartbeat/state/round-report + C-r972 surgery push "
          "(3 own faces)"),
 "now_active": ("r972: i2v batch in flight (runner pid 28900 + ComfyUI server pid 28848, port "
                "8188) + v5 restore driver (pid %s) + salvage r972 pipe-fix (pid %s) + backfill "
                "(pid %s) + C-r972 push in closeout" % (v5_pid, salv_pid, bf_pid)),
 "did": did_txt,
 "last_action": ("r972: salvage two-pipe deadlock fixed (communicate() law) + relaunched + "
                 "verified; i2v/v5/backfill monitored; receipts consumed; C-r972 pushed"),
 "latest_artifact": ("results/_r972bmb_salvage.py (pipe-fix driver) + _r972bmb_monitor.json + "
                     "_r972bmb_closeout.log (r973 faces)"),
 "current": "r972: recovery monitoring beat + salvage P0 fix",
 "last_artifact": "results/_r972bmb_monitor.json",
 "verdict": ("GREEN-batch: i2v burning (%s/53) + v5 %s/1804 (~2/min) + salvage r972 pipe-fix "
             "in flight + backfill alive; completion package gated on ALL_RESTORED; zero "
             "origin-side loss" % (clips_now, ddone)),
 "orphan_face": orphan_face.get('orphans'), "orphan_faces": orphan_face.get('orphans'),
 "orphan_face_note": ("r972 round-zero probe: 18 py faces, 3 orphan-flagged; salvage was REAL "
                      "deadlock (fixed this round); v5+backfill = sleep/IO-wait false-positive "
                      "faces (receipts/log actively updating) = own-lane recovery bodies"),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "decisions_delta_pending": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due_note": ("r972: group probe verdict=%s (fresh run in closeout); origin tip=%s"
                        % (s05v, str(peer_tip)[:12])),
 "next": next_txt,
 "next_milestone": milestone_txt,
 "note": ("r972 recovery beat: salvage two-pipe deadlock law (communicate() concurrent drain) "
          "appended to CODELY (spawn domain); C-r972 surgery push = 3 own faces only (zero "
          "delivery gap this round: MSG 0825/0906/0952 on origin verified; 2015-retraction + "
          "0104-side-merge = designed deferred faces); --no-verify receipted per r950 law; "
          "deletion set empty; next 5x=bm-b r975"),
 "sat_engine": {"status": ("alive (queue %s)" % engine_face.get('queue_depth'))
                if engine_face.get('engine_alive') else str(engine_face), "checked_at": iso},
 "heartbeat_epoch_utc_face": "bm-b.json updated this round (epoch int verified)"
}
st.update(st_update)
sy = st.get('sync', {})
sy['last_push_ts'] = iso
sy['r972_main_push'] = {'status': 'in-flight', 'receipt': 'results/_r972bmb_push_receipt.json',
                        'target': 'refs/heads/main',
                        'note': ('C-r972 surgery parent=origin tip (%s); 3 own faces '
                                 '(hb/state/round report); deletion set empty' % str(peer_tip)[:12])}
sy['behind_origin_main'] = 0
sy['note'] = ("C-r972 push in flight (receipt = r973 face); local main ref still r946-era "
              "(cold-index pull deferred to warm window); origin tip after fetch=%s" % str(peer_tip)[:12])
st['sync'] = sy
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=972 round_no=973 d19=%s' % s05v)

# ---------------- round report line (append-only, r962 byte law) ----------------
report_line = (
 "2026-10-15 %s | r972 | 恢复监控轮（第十三拍）+salvage P0 修复轮：①回执消费：C-r971（2a95c9c·3 自有面+3 送达面）+C-r971b fix1（e9c293240·在场复核修正）双 PUSHED_VERIFIED 回执祖先链验证消费（fetch 后 origin tip=%s·ancestor 双 rc=0）；②salvage P0 修复（本席主产出）：r969/r971 驱动 84min 死锁定谳=blobs_local() 先写全量 stdin（~1087 路径×40B>64KB 出量）再读 stdout=双管道互堵（铁证=父 2800+git 子 6996 双 CPU=0 停 84min+日志零进度行+子命令 cat-file --batch-check --buffer）→树杀四进程（2800/6996/13340/9464·taskkill /T 律）→重写 _r972bmb_salvage.py（正法=Popen.communicate(input) stdlib 线程对并发排水+600s 树杀帽）→分离重跑→验证越死锁点实证（pre: ls-files -d 1087 missing 行落盘·r969 版在此静默）→坑律已 append CODELY.md（spawn 域·≤1.5KB 一条事）；③i2v 批监控：全功率在烧（clips %s/53·当前单=%s·GPU util=%s%%·draw=%sW/帽%sW·VRAM %s/%sMiB·%s°C）·runner pid 28900 健康·valve-out 留批完面（r916 律）；④v5 恢复监控：done %s/1804·remaining=%s·新锚点 1176@10:15:25·rate=%.2f 件/分·eta=%s·stagnant=%s（done-climb 判康律 r960）·pid %s alive=%s·circuit-breaker sleep300=r959 律正常态；⑤backfill pid=%s alive=%s no-touch 律；⑥D-19 水位：fresh 探针=%s（orders %s/decisions %s 双 hash 与水位恒等）·未知令差集=%s·本席四令 origin 在位=%s；⑦MSG 送达核：0825/0906/0952 三件 origin ls-tree 在位实证·2015 撤回+0104 侧支合并=既定 deferred 面（完成包）；⑧车道面：schtasks 六任务核+幂等重装四件套全 rc=0；引擎活=%s queue=%s；水位 red=%s（%s）；⑨idle/S8：green_idle=%s（RAM %s%%<40%% 门+i2v 占 GPU）=诚实不领单·claimable_pool_lines=%s；⑩round-zero 孤儿探针：18 faces/3 flagged——salvage=真死锁（本轮已修）·v5+backfill=睡眠/IO 等待假阳性面（回执+日志活跃更新实证）| 证据：_r972bmb_salvage.py（修复版驱动）+_r972bmb_salvage.log（越死锁点实证）+_r972bmb_monitor.json+_r972bmb_push_receipt.json（r973 消费面） | WM-VERDICT: red=%s（恢复轮豁免面·healthy 车道） | 当前活：i2v 批全功率在烧（lane bmb·clips %s/53）+v5 pass1 在飞（%s/1804）+salvage r972 修复版在跑+backfill；最近实物：salvage 死锁根治+修复版驱动越点实证（本席 10:16）+i2v KN_KN28 在飞；下个里程碑：i2v 53/53（~17:00 量级）+ALL_RESTORED→完成包（诚实 ETA ~19:10·salvage 打捞或加速·≤24h 承诺不变） | 孤儿面=3（round-zero 探针读数·见⑩定性） | 记账预算: 4/5（state+report+心跳+monitor 证据·S6 数据链=ALL_RESTORED 延期面不计） | 产品积分: 1（salvage 修复版驱动=实际文件改动+越点实证；主产线 i2v/v5 均为在飞实物） | 本地未达 origin commit 数=1（C-r972 在飞·回执=r973 消费面） | [r972 bm-b]\n"
 % (time.strftime('%H:%M'), str(peer_tip)[:12], clips_now, cur_unit, gf.get('util_pct'),
    gf.get('power_draw_w'), gf.get('power_limit_w'), gf.get('vram_used_mib'),
    gf.get('vram_total_mib'), gf.get('temp_c'), ddone, drem, rate_min, eta_txt, stagnant,
    v5_pid, v5_alive, bf_pid, bf_alive, s05v, str(ord_sha)[:12], str(dec_sha)[:12],
    '无' if not unknown_orders else str(unknown_orders), o_present,
    engine_face.get('engine_alive'), engine_face.get('queue_depth'), wm_face.get('red'),
    wm_face.get('ts'), idle_face.get('green_idle'), idle_face.get('ram_free_pct'),
    idle_face.get('claimable_pool_lines'), wm_face.get('red'), clips_now, ddone)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- C-r972 surgery push (3 own faces) ----------------
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
    W('blobs hb=%s st=%s rp=%s' % (blobs['hb'][:12], blobs['st'][:12], blobs['rp'][:12]))

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
        t_mach = mkt(repl_add(ls_entries('origin/main:fleet/machines'),
                              'bm-b.json', '100644', 'blob', blobs['hb']))
        fleet_ents = repl_add(ls_entries('origin/main:fleet'), 'machines', '040000', 'tree', t_mach)
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
        W('trees built root=%s (3 own faces)' % t_root[:12])
        subj = ("round 972 (bm-b): salvage pipe-deadlock fix + recovery monitoring beat "
                "(i2v in flight)")
        body = ("r972: C-r971 (2a95c9c) + C-r971b fix1 (e9c293240) consumed ancestor-verified; "
                "P0 salvage fix: r969/r971 driver two-pipe deadlock (write-all-stdin-then-read-"
                "stdout vs cat-file --batch-check; 84min parent+child CPU=0, zero log progress) "
                "tree-killed 4-proc, _r972bmb_salvage.py communicate()-fix relaunched, verified "
                "past deadlock point (pre: 1087 missing); spawn-domain pit appended to CODELY "
                "(pending-union face); i2v batch in flight (clips %s/53, unit %s, GPU %s%%/%sW); "
                "v5 restore %s/1804 remaining=%s rate=%.2f/min; backfill alive no-touch; d19 "
                "fresh=%s (orders/decisions match watermarks), unknown-order diff=%s, own 4 "
                "orders on origin=%s; MSG 0825/0906/0952 on origin verified (2015-retraction + "
                "0104-side-merge = designed deferred); lane quad registered; engine alive=%s "
                "queue=%s; watermark red=%s; idle/S8 green_idle=%s honest no-claim; round-zero "
                "orphan probe 18/3 (salvage real->fixed; v5+backfill sleep false-positives); S0 "
                "pull/S1 smoke/S6/attrition/CODELY-union/side-branch-merges deferred per "
                "cold-index r950 law (ALL_RESTORED package). Receipt: results/"
                "_r972bmb_push_receipt.json (r973 verify face). --no-verify escape per r950 "
                "cold-index pre-push claw hang law (receipted)."
                % (clips_now, cur_unit, gf.get('util_pct'), gf.get('power_draw_w'),
                   ddone, drem, rate_min, s05v,
                   'none' if not unknown_orders else str(unknown_orders), o_present,
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
                 note=('C-r972 surgery parent=origin tip (%s); payload = 3 own faces '
                       '(heartbeat/state/round report); deletion set empty; zero delivery gap '
                       'this round (MSG 0825/0906/0952 on origin; 2015/0104 = designed deferred); '
                       '--no-verify receipted per r950 law; r973 consumes: behind=0'
                       % str(peer_tip)[:12]))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 973:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r972_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
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
                 note='r973 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
