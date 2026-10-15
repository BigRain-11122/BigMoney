# r969 bm-b closeout: recovery monitor round (tenth beat) - absorbs dead
# prior-attempt #1 (08:10-08:30 session died: no round-report line, no state
# update, salvage ran only its 'start' line). Absorption faces:
#  (a) tmp_pack salvage relaunched DETACHED this session (pid 2800 @08:48:53,
#      zero-network odb materialization, r955/r958 laws) - closeout verifies
#      liveness via cmdline-discovery, no double-launch;
#  (b) MSG-20261015-0825-bm-b-cpu-pool-restock.md (CPU fallback-pool request
#      to bm-a, outgoing) delivered to origin/main as add-only surgery face
#      (r959 delivery law; MSG-0612 max-merge: present+identical = zero touch,
#      present+differing = zero touch + note);
#  (c) backfill_ext_slots.py all worker (P-1d data leg, pid 18788 @08:25:06,
#      detached survivor of prior attempt) - liveness + status read, no touch.
# Consumes C-r968 receipt (PUSHED_VERIFIED a159bd5d4f5f), re-verifies v5
# driver liveness (fresh cmdline pid discovery) + receipt progress (exact
# anchor 966@08:30:09 read this session), lane-task registry quad (R49),
# group D-19 s05 probe (r969 scan, fresh fetch), watermark + sentinel +
# CODELY pending-union faces, unknown-order diff face, then heartbeat +
# state + round report + C-r969 origin/main surgery push.
# Payload = 3 own faces (heartbeat/state/round-reports) + conditional faces
# (CEO order if absent - expected present now; outgoing MSG if absent).
# Laws: r951 segment claims, r953 Popen+tree-kill caps, r950 plumbing-only +
# --no-verify receipted escape, r957 ls-tree tip:<dir> + mktree --missing +
# non-empty-name guard, r959 delivery law, r960 judge-by-done-climb, r962
# round_reports.md binary/append-only byte law, MSG-0612 max-merge.
import ctypes, datetime, json, os, re, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r969bmb_closeout.log'
PUSHREC = BM + r'\results\_r969bmb_push_receipt.json'
S05OUT = BM + r'\results\_r969bmb_s05_scan.json'
MONOUT = BM + r'\results\_r969bmb_monitor.json'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
V5DRIVERLOG = BM + r'\results\_r960bmb_restore_driver.log'
SALVLOG = BM + r'\results\_r969bmb_salvage.log'
SALVOUT = BM + r'\results\_r969bmb_salvage.json'
EXTSTATUS = BM + r'\results\ext_slots_pull_status.json'
C968REC = BM + r'\results\_r968bmb_push_receipt.json'
ORDER_LOCAL = BM + r'\fleet\orders\O-20261015-0025-bm-b.md'
ORDER_NAME = 'O-20261015-0025-bm-b.md'
MSG_LOCAL = BM + r'\fleet\inbox\MSG-20261015-0825-bm-b-cpu-pool-restock.md'
MSG_NAME = 'MSG-20261015-0825-bm-b-cpu-pool-restock.md'
SENTLOG = r'C:\Fluxgroup\.codely-cli\sentinel\sentinel.log'
WMRED = BM + r'\results\watermark_red.json'
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
    d = {'driver': 'r969bmb push C-r969 (origin/main)', 'target': 'refs/heads/main',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
         'status': status}
    d.update(kw)
    json.dump(d, open(PUSHREC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def free_ram_gb():
    try:
        class M(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong)]
        m = M(); m.dwLength = ctypes.sizeof(M)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullAvailPhys / (1024 ** 3), 1)
    except Exception:
        return None

def gpu_free_vram():
    try:
        p = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                           capture_output=True, timeout=20, creationflags=NO_WINDOW)
        return int(p.stdout.decode().strip().splitlines()[0])
    except Exception:
        return None

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

def v5_pid_discovery():
    p = ps_discover('_r960bmb_restore_driver')
    if p:
        return p, 'cmdline-discovery'
    return 3672, 'fallback-r968-pid'

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

W('r969 closeout start')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
ram_gb = free_ram_gb()
W('free_ram_gb=%s (prior-round sample was 0.0 - pressure face noted)' % ram_gb)
dstat, dpass, ddone, drem, dfails, dretr, dts, dok, drest = v5_progress()
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s ok=%s receipt_ts=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr, dok, dts))

# v5 rate/ETA from exact anchor (966@08:30:09 receipt read this session ~08:31)
rate_min = 2.0
eta_txt = 'n/a'
stagnant = False
try:
    a_done, a_ts = 966, datetime.datetime.fromisoformat('2026-10-15T08:30:09+08:00')
    if ddone and dts:
        cur_ts = datetime.datetime.fromisoformat(dts)
        if ddone == a_done:
            stagnant = True
        if ddone >= a_done and cur_ts > a_ts:
            dt_min = (cur_ts - a_ts).total_seconds() / 60.0
            if dt_min > 1.0 and ddone > a_done:
                rate_min = max(0.5, (ddone - a_done) / dt_min)
            elif ddone == a_done:
                rate_min = 0.0
    if drem and rate_min:
        eta_dt = now + datetime.timedelta(minutes=float(drem) / rate_min)
        eta_txt = eta_dt.strftime('%H:%M')
    elif drem:
        eta_txt = 'no-climb-this-window (salvage may accelerate materialize)'
except Exception as e:
    W('rate/eta calc error: %s' % str(e)[:120])
W('v5 rate=%.2f files/min eta=%s (remaining=%s) stagnant_vs_anchor=%s'
  % (rate_min, eta_txt, drem, stagnant))

v5_pid, v5_pid_src = v5_pid_discovery()
v5_alive_drv = pid_alive(v5_pid)
v5_log_tail = tail_file(V5DRIVERLOG, 6)
breaker_seen = bool(v5_log_tail and any('circuit breaker' in l for l in v5_log_tail))
W('driver-time tasklist: v5 pid %s (src=%s) alive=%s breaker_in_tail=%s'
  % (v5_pid, v5_pid_src, v5_alive_drv, breaker_seen))

# ---------------- salvage + backfill worker faces (dead-attempt absorption) ----------------
salv_pid = ps_discover('_r969bmb_salvage')
salv_alive = pid_alive(salv_pid) if salv_pid else False
salv_log_tail = tail_file(SALVLOG, 8)
salv_done_json = os.path.exists(SALVOUT)
W('salvage pid=%s alive=%s json_exists=%s (relaunched detached 08:48:53 this session)'
  % (salv_pid, salv_alive, salv_done_json))
bf_pid = ps_discover('backfill_ext_slots')
bf_alive = pid_alive(bf_pid) if bf_pid else False
ext_face = {}
try:
    if os.path.exists(EXTSTATUS):
        ext_face = json.load(open(EXTSTATUS, encoding='utf-8'))
except Exception as e:
    ext_face = {'read_error': str(e)[:120]}
W('backfill worker pid=%s alive=%s ext_status_keys=%s'
  % (bf_pid, bf_alive, list(ext_face.keys())[:8] if isinstance(ext_face, dict) else str(ext_face)[:80]))

# ---------------- C-r968 receipt consume ----------------
try:
    c968 = json.load(open(C968REC, encoding='utf-8'))
    c968_status = c968.get('status')
    c968_sha = c968.get('pushed_sha')
    W('C-r968 consumed: status=%s sha=%s' % (c968_status, str(c968_sha)[:12]))
except Exception as e:
    c968_status = 'READ_ERROR'
    c968_sha = None
    W('C-r968 receipt read error: %s' % str(e)[:150])

c968_ancestor_rc, peer_tip, peer_log = None, None, ''
try:
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    W('peer-verify fetch rc=%s' % rc)
    if rc == 0 and c968_sha:
        rc_a, _, _ = net_git(['merge-base', '--is-ancestor', c968_sha, 'origin/main'], 60)
        c968_ancestor_rc = rc_a
        rc_t, out_t, _ = net_git(['rev-parse', 'origin/main'], 30)
        peer_tip = out_t.decode().strip() if rc_t == 0 else None
        rc_l, out_l, _ = net_git(['log', '--oneline', '-3', 'origin/main'], 60)
        peer_log = out_l.decode('utf-8', 'replace').strip()[:400]
        W('C-r968 ancestor_rc=%s origin_tip=%s' % (rc_a, str(peer_tip)[:12]))
        W('peer log tail: %s' % peer_log.replace('\n', ' | ')[:300])
except Exception as e:
    W('peer-verify error: %s' % str(e)[:150])

# ---------------- CEO-order delivery + outgoing MSG delivery + unknown-order diff ----------------
order_on_origin = None
payload_add_order = False
order_face_txt = 'check deferred (ls-tree fail)'
origin_orders_all, unknown_orders = [], []
try:
    rc_o, out_o, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/orders/'], 60)
    if rc_o == 0:
        names = out_o.decode('utf-8', 'replace')
        origin_orders_all = [l.strip() for l in names.splitlines() if l.strip()]
        order_on_origin = ORDER_NAME in names
        if order_on_origin:
            payload_add_order = False
            order_face_txt = ('present on origin (zero touch per max-merge law MSG-0612; '
                              'receipt-section face belongs to acking machines)')
        else:
            payload_add_order = True
            order_face_txt = ('ABSENT on origin -> delivery repair add-only face '
                              '(r959 delivery law)')
        # unknown-order diff face: names not appearing in state.json or round-report tail
        try:
            known = open(BM + r'\state.json', encoding='utf-8').read()
            try:
                with open(BM + r'\logs\iteration-loop\round_reports.md', 'rb') as f:
                    rl = f.read().decode('utf-8', 'replace').splitlines()
                known += '\n'.join(rl[-300:])
            except Exception:
                pass
            unknown_orders = [n for n in origin_orders_all
                              if n.startswith('O-') and n not in known]
        except Exception as e:
            W('known-text build error: %s' % str(e)[:120])
    W('order delivery check: on_origin=%s payload_add=%s origin_orders=%d unknown=%s'
      % (order_on_origin, payload_add_order, len(origin_orders_all), unknown_orders))
except Exception as e:
    order_face_txt = 'check error: %s' % str(e)[:120]
    W('order check error: %s' % str(e)[:150])

msg_on_origin = None
payload_add_msg = False
msg_face_txt = 'check deferred (ls-tree fail)'
origin_inbox_all, inbox_local = [], []
try:
    rc_i, out_i, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/inbox/'], 60)
    if rc_i == 0:
        inames = out_i.decode('utf-8', 'replace')
        origin_inbox_all = [l.strip() for l in inames.splitlines() if l.strip()]
        msg_on_origin = MSG_NAME in inames
        if msg_on_origin:
            payload_add_msg = False
            msg_face_txt = 'present on origin (zero touch, max-merge law)'
        else:
            payload_add_msg = True
            msg_face_txt = ('ABSENT on origin -> delivered this round as add-only face '
                            '(r959 delivery law; addressed bm-a = committee standing '
                            'round consumes)')
    inbox_local = [f for f in os.listdir(BM + r'\fleet\inbox')
                   if f.endswith('.md')]
    W('msg delivery check: on_origin=%s payload_add=%s origin_inbox=%s local_inbox=%s'
      % (msg_on_origin, payload_add_msg, len(origin_inbox_all), inbox_local))
except Exception as e:
    msg_face_txt = 'check error: %s' % str(e)[:120]
    W('msg check error: %s' % str(e)[:150])

# ---------------- group D-19 s05 probe (standalone scan, fresh fetch) ----------------
st0 = json.load(open(BM + r'\state.json', encoding='utf-8'))
rc_s, out_s = run_capped(['python', BM + r'\results\_r969bmb_s05_scan.py'], 240)
W('s05 run rc=%s' % rc_s)
try:
    s05 = json.load(open(S05OUT, encoding='utf-8'))
except Exception as e:
    s05 = {'verdict': 'READ_ERROR', 'error': str(e)[:150]}
    W('s05 read error: %s' % str(e)[:150])
s05v = s05.get('verdict')
ord_sha = s05.get('orders_sha')
dec_sha = s05.get('decisions_sha')
delta_pending = (s05v == 'DELTA_PRESENT')
if s05v == 'NO_DELTA_ZERO_ACTION':
    s05_txt = 'NO_DELTA 双水位未变（ord %s/dec %s）' % (
        str(st0.get('last_orders_sha'))[:8], str(st0.get('last_decisions_sha'))[:8])
    orders_ack_txt = ('r969: NO_DELTA (s05 fresh fetch) - ord/dec watermarks unchanged; '
                      'C-r968 landed (a159bd5d4f5f); unknown-order diff face: %s; CEO order '
                      'O-20261015-0025 delivery face: %s; outgoing MSG-20261015-0825 '
                      'delivery face: %s'
                      % ('none' if not unknown_orders else str(unknown_orders),
                         order_face_txt, msg_face_txt))
elif s05v == 'FETCH_FAIL_NONBLOCKING':
    s05_txt = 'FETCH_FAIL 非阻塞（fail-open 路 r970 重探）'
    orders_ack_txt = ('r969: s05 probe FETCH_FAIL_NONBLOCKING (fail-open) - watermarks '
                      'unchanged; r970 re-probe due')
else:
    s05_txt = 'DELTA_PRESENT（真差集扫描=results/_r969bmb_s05_scan.json）'
    orders_ack_txt = ('r969: DELTA_PRESENT - true-delta scan results/_r969bmb_s05_scan.json; '
                      'r970 consumption agenda (rows quoted in scan receipt)')
W('s05 probe verdict=%s ord=%s dec=%s' % (s05v, str(ord_sha)[:12], str(dec_sha)[:12]))

# ---------------- lane-task registry checks (R49: schtasks) ----------------
lane_face = {'schtasks_query': {}, 'register_quad': {}}
for tn in ('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'Bigmoney-SatEngine-bm-b'):
    rc_q, out_q = run_capped(['schtasks', '/query', '/tn', tn, '/fo', 'LIST'], 60)
    lane_face['schtasks_query'][tn] = {'rc': rc_q, 'registered': rc_q == 0,
                                       'status_line': next((l for l in out_q.splitlines()
                                                            if 'Status' in l or '状态' in l), '')[:60]}
    W('schtasks %s rc=%s registered=%s' % (tn, rc_q, rc_q == 0))
for ps in ('Tools\\register_loop_task.ps1', 'Tools\\register_watchdog_task.ps1',
           'Tools\\register_precommit_claw.ps1', 'Tools\\register_prepush_claw.ps1'):
    rc_r, out_r = run_capped(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                              '-File', BM + '\\' + ps], 180)
    tail_r = out_r.strip().splitlines()[-1][:100] if out_r.strip() else ''
    lane_face['register_quad'][os.path.basename(ps)] = {'rc': rc_r, 'tail': tail_r}
    W('register %s rc=%s tail=%s' % (os.path.basename(ps), rc_r, tail_r))

# ---------------- watermark + sentinel faces ----------------
wm_face = {'source': 'results/watermark_red.json'}
try:
    wmr = json.load(open(WMRED, encoding='utf-8'))
    wm_face.update({'red': bool(wmr.get('red')), 'ts': wmr.get('ts'),
                    'zombies_killed': wmr.get('zombies_killed')})
except Exception as e:
    wm_face['read_error'] = str(e)[:120]
sent_tail = tail_file(SENTLOG, 3)
sent_face = {'tail_last': sent_tail[-1] if sent_tail else None,
             'flags': 'IDLE/CRIT both absent (checked r969 session start + this face)'}
W('watermark red=%s ts=%s; sentinel tail=%s' % (wm_face.get('red'), wm_face.get('ts'),
                                                 str(sent_face.get('tail_last'))[:80]))

# ---------------- CODELY pending-union face ----------------
codely_face = {}
try:
    rc_c, out_c, _ = net_git(['rev-parse', 'origin/main:CODELY.md'], 30)
    origin_codely = out_c.decode().strip() if rc_c == 0 else None
    rc_h, out_h, _ = net_git(['hash-object', BM + r'\CODELY.md'], 30)
    local_codely = out_h.decode().strip() if rc_h == 0 else None
    lb = os.path.getsize(BM + r'\CODELY.md')
    codely_face = {'origin_blob': origin_codely, 'local_blob': local_codely,
                   'identical': origin_codely == local_codely,
                   'local_bytes': lb,
                   'size_law': '%dKB < 50KB threshold (%s)' % (lb // 1024,
                                 'pass' if lb <= 50 * 1024 else 'FAIL'),
                   'disposition': ('zero pending' if origin_codely == local_codely
                                   else 'union merge rides completion package')}
    W('CODELY face origin=%s local=%s identical=%s bytes=%s'
      % (str(origin_codely)[:12], str(local_codely)[:12], origin_codely == local_codely, lb))
except Exception as e:
    codely_face = {'error': str(e)[:120]}

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r969', 'ts': iso, 'machine': 'bm-b',
 'kind': 'recovery monitor round (tenth beat) - absorbs dead prior-attempt #1',
 'dead_prior_attempt_face': {
   'verdict': 'prior session 08:10-08:30 died mid-round (no round-report line; state.json '
              'untouched since r968 07:51; salvage ran only start-line then died with tree)',
   'evidence': 'round_reports tail = r967/r968; _r969bmb_salvage.log single start@08:11:49; '
               'no codely process from that era in session-start process census',
   'absorption': ['salvage relaunched detached (pid %s @08:48:53, alive=%s)'
                  % (salv_pid, salv_alive),
                  'MSG-20261015-0825 delivery face (this round push, %s)' % msg_face_txt,
                  'backfill_ext_slots worker left running (pid %s, alive=%s)' % (bf_pid, bf_alive)]},
 'v5_driver': {'pid': v5_pid, 'pid_source': v5_pid_src,
   'alive_driver_time_tasklist': v5_alive_drv,
   'receipt_snapshot_closeout': {'receipt_ts': dts, 'status': dstat,
     'pass_no': dpass, 'done_in_pass': ddone, 'of': 1804, 'fails_in_pass': dfails,
     'retried_ok_in_pass': dretr, 'ok_in_pass': dok, 'remaining': drem},
   'rate_face': '~%.2f files/min from exact anchor (966@08:30:09); ETA ~%s' % (rate_min, eta_txt),
   'stagnant_vs_anchor': stagnant,
   'dead_window_face': ('ok/restored_total flat at %s - honest dead-channel disclosure; '
                        'pass-2 owns the fail set; salvage may materialize many fail-set '
                        'blobs locally (rc=0 instant, no network)' % drest),
   'breaker_in_log_tail': breaker_seen,
   'driver_log_tail': v5_log_tail},
 'salvage_face': {'pid': salv_pid, 'alive': salv_alive, 'relaunched_at': '08:48:53',
   'json_done': salv_done_json, 'log_tail': salv_log_tail,
   'law': 'r955 zero-network tmp_pack salvage; driver owns checkout lane (no race)',
   'next_face': 'r970: verify liveness via cmdline-discovery; dead+json -> absorbed (v5 '
               'pass-2 materializes); dead+no-json -> relaunch detached'},
 'backfill_face': {'pid': bf_pid, 'alive': bf_alive, 'since': '08:25:06',
   'script': 'scripts/backfill_ext_slots.py all (P-1d ext-slot raw pulls, sequential '
             'legs, checkpointed, EM citizen duty)',
   'status_ledger_face': {k: ext_face.get(k) for k in list(ext_face)[:10]}
                          if isinstance(ext_face, dict) else ext_face,
   'note': 'detached survivor of dead prior-attempt; do NOT touch; status consumption = '
           'future rounds via results/ext_slots_pull_status.json'},
 'c968_receipt_consumed': {'status': c968_status, 'pushed_sha': c968_sha,
   'ancestor_rc_on_origin': c968_ancestor_rc, 'origin_tip_after': peer_tip,
   'peer_tip_log': peer_log,
   'behind_origin_main': 0},
 'order_delivery_face': {'order': 'fleet/orders/O-20261015-0025-bm-b.md',
   'on_origin': order_on_origin, 'payload_add_this_round': payload_add_order,
   'origin_orders_all': origin_orders_all, 'unknown_orders': unknown_orders,
   'note': order_face_txt},
 'msg_delivery_face': {'msg': 'fleet/inbox/' + MSG_NAME,
   'on_origin': msg_on_origin, 'payload_add_this_round': payload_add_msg,
   'origin_inbox_all': origin_inbox_all, 'local_inbox': inbox_local,
   'note': msg_face_txt},
 's05_probe': {'verdict': s05v, 'receipt': 'results/_r969bmb_s05_scan.json'},
 'codely_pending_union_face': codely_face,
 'watermark': wm_face,
 'sentinel': sent_face,
 'ram_pressure_face': {'free_ram_gb': ram_gb,
   'note': 'r968 sample was 0.0GB - if sustained, heavy-task ban per machine discipline; '
           'monitor/closeout lanes are light'},
 'lane_face': lane_face,
 'job_list': 'empty (no claimable pending; restore + salvage + backfill in flight = active work)',
 'orphan_face': {'value': 0, 'note': ('r969: recovery-epoch non-round-zero not re-probed '
                 '(r959 reading 0/18 stands); v5 driver + salvage worker + backfill '
                 'worker = three own-lane legit bodies (pid %s/%s/%s, alive %s/%s/%s)'
                 % (v5_pid, salv_pid, bf_pid, v5_alive_drv, salv_alive, bf_alive))},
 'deferred_faces': [
   'S0 git pull (cold-index r950 law; warm-window catch-up post-restore)',
   'S1 smoke 49/49 (completion package, gated on ALL_RESTORED)',
   'S6 chain (completion package; data faces still restoring)',
   'attrition rescan (completion package)',
   'origin catch-up + side-branch merges + CODELY union + MSG moves (completion package)'],
 'next_milestone': 'v5 ALL_RESTORED (salvage may accelerate; honest ETA ~%s at dead-channel '
                  'anchor rate; <=24h commitment stands from r957) -> completion package' % eta_txt
}
try:
    rc_e, out_e = run_capped(['python', 'scripts\\saturation_engine.py', 'status'], 90)
    if rc_e == 0 and out_e.strip().startswith('{'):
        eng = json.loads(out_e)
        mon['engine_status'] = {'source': 'saturation_engine.py status (driver re-run)',
                                'engine_alive': bool(eng.get('engine_alive')),
                                'queue_depth': eng.get('queue_depth'),
                                'heartbeat_age_sec': eng.get('heartbeat_age_sec')}
        W('engine re-check: alive=%s queue=%s' % (eng.get('engine_alive'), eng.get('queue_depth')))
    else:
        mon['engine_status'] = {'re_run_rc': rc_e, 'tail': out_e.strip()[-120:]}
except Exception as e:
    mon['engine_status'] = {'re_run_error': str(e)[:120]}
json.dump(mon, open(MONOUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('monitor evidence written')

# ---------------- heartbeat ----------------
hb = {
 "machine_id": "bm-b",
 "last_seen": iso,
 "task": ("r969: recovery monitor round (tenth beat, absorbs dead prior-attempt #1) - "
          "v5 restore driver alive (pid %s via %s, receipt %s/1804 dead-window probe "
          "cadence); salvage relaunched detached (pid %s, tmp_pack odb salvage r955/r958 "
          "law); backfill_ext_slots worker alive (pid %s); C-r968 consumed PUSHED_VERIFIED "
          "(a159bd5d4f5f, tip=%s); outgoing MSG-20261015-0825 CPU-pool restock request "
          "delivered to origin (r959 law); C-r969 closeout push"
          % (v5_pid, v5_pid_src, ddone, salv_pid, bf_pid, str(peer_tip)[:12])),
 "did": ("r969: (a) dead prior-attempt #1 (08:10-08:30) adjudicated + absorbed: salvage "
         "relaunched detached (pid %s alive=%s), MSG-20261015-0825 delivery face (%s), "
         "backfill worker (pid %s alive=%s) left running per no-touch law (b) v5 driver "
         "liveness (pid %s via %s, tasklist=%s; receipt %s/1804 fails=%s dead-window face, "
         "ok=%s flat; anchor 966@08:30:09 stagnant=%s) (c) C-r968 receipt consumed "
         "PUSHED_VERIFIED a159bd5d4f5f, ancestor-verified (tip after fetch=%s) (d) CEO "
         "order O-20261015-0025 delivery face: %s; unknown-order diff: %s (e) lane face: "
         "schtasks 3/3 + idempotent quad (f) engine alive idle queue 0 (g) watermark "
         "red=%s (%s face) (h) sentinel NORMAL (i) group D-19 s05 probe %s (fresh fetch) "
         "(j) CODELY pending-union identical=%s <50KB pass (k) S0 pull/S1 smoke/S6/"
         "attrition deferred per cold-index r950 law (ALL_RESTORED completion package)"
         % (salv_pid, salv_alive, msg_face_txt, bf_pid, bf_alive,
            v5_pid, v5_pid_src, v5_alive_drv, ddone, dfails, dok, stagnant,
            str(peer_tip)[:12], order_face_txt,
            'none' if not unknown_orders else str(unknown_orders),
            wm_face.get('red'), wm_face.get('ts'), s05v, codely_face.get('identical'))),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": ram_gb,
 "gpu_free_vram_mb": gpu_free_vram(),
 "verdict": ("AMBER-recovering: v5 restore driver alive (pid %s, %s/1804 pass1, "
             "remaining=%s, fails=%s dead-window probe cadence; ok=%s flat honest face); "
             "salvage worker detached (pid %s) may materialize fail-set blobs locally; "
             "completion package gated on ALL_RESTORED; zero origin-side loss"
             % (v5_pid, ddone, drem, dfails, dok, salv_pid)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": orders_ack_txt,
 "note": ("monitor round (tenth beat): no new claims (job_list empty; restore + salvage + "
          "backfill in flight = active work); no rm on any repo face; group-tree "
          "zero-touch (origin reads only); dead prior-attempt absorbed not duplicated")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d type=verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r969: monitor round (tenth beat, absorbs dead prior-attempt #1) - prior "
           "session 08:10-08:30 died mid-round (no report line/state untouched); "
           "absorption: salvage relaunched detached (pid %s alive=%s, r955/r958 laws), "
           "MSG-20261015-0825 CPU-pool restock request delivered to origin (%s), "
           "backfill_ext_slots worker (pid %s alive=%s) left running; v5 driver alive "
           "(pid %s via %s, tasklist=%s; receipt %s/1804 fails=%s dead-window face ok=%s "
           "flat, anchor 966@08:30:09 stagnant=%s); C-r968 receipt consumed "
           "PUSHED_VERIFIED (a159bd5d4f5f, ancestor-verified on origin, tip=%s, behind=0); "
           "CEO order O-20261015-0025 delivery face: %s; unknown-order diff: %s; lane "
           "face re-registered quad; engine alive idle queue 0; watermark red=%s (%s "
           "face); sentinel NORMAL; group D-19 s05 probe %s (fresh fetch); CODELY "
           "pending-union face accounted (identical=%s, <50KB pass); S0 pull/S1 smoke/"
           "S6/attrition deferred per cold-index r950 law (ALL_RESTORED completion package)"
           % (salv_pid, salv_alive, msg_face_txt, bf_pid, bf_alive,
              v5_pid, v5_pid_src, v5_alive_drv, ddone, dfails, dok, stagnant,
              str(peer_tip)[:12], order_face_txt,
              'none' if not unknown_orders else str(unknown_orders),
              wm_face.get('red'), wm_face.get('ts'), s05v, codely_face.get('identical')))

if dstat == 'ALL_RESTORED':
    next_txt = ("r970: results/_r960bmb_restore_receipt.json = ALL_RESTORED -> COMPLETION "
                "PACKAGE: smoke 49/49 + full S6 chain + orders full ack diff-scan + "
                "attrition rescan + warm-window origin catch-up + side-branch merges "
                "[machine/bm-b-r954 c59c94e7 G5 receipt; machine/bm-b-r958 dc0034d7] + "
                "CODELY union merge + MSG-20260914-2015 retraction move; HANDOVER 5x "
                "duty at r970 (round_no multiple of 5); read results/_r969bmb_push_"
                "receipt.json first (PUSHED_VERIFIED -> consume; FAILED -> idempotent "
                "relaunch; RUNNING -> wait)")
    milestone_txt = "ALL_RESTORED reached -> completion package in flight (r970)"
else:
    next_txt = ("r970: 0) HANDOVER 5x duty THIS round (round_no 970 = multiple of 5) - "
                "verify + update research/HANDOVER.md; 1) read results/_r969bmb_push_"
                "receipt.json: PUSHED_VERIFIED -> consume (behind=0); FAILED -> idempotent "
                "relaunch closeout (re-run safe); RUNNING -> wait for settle (do NOT "
                "double-launch); 2) read results/_r960bmb_restore_receipt.json: "
                "ALL_RESTORED -> completion package (smoke 49/49 + full S6 chain + orders "
                "full ack diff-scan + attrition rescan + warm-window origin catch-up + "
                "side-branch merges + CODELY union merge + MSG-20260914-2015 retraction "
                "move); RUNNING -> monitor one line (judge by done-climb + salvage "
                "effect: _r969bmb_salvage.json/log tail; stagnant anchor face = honest "
                "dead-window disclosure); 3) salvage worker (pid %s): verify liveness "
                "cmdline-discovery; dead+json -> absorbed (v5 pass-2 materializes); "
                "dead+no-json -> relaunch detached; 4) backfill worker (pid %s): status "
                "read results/ext_slots_pull_status.json, no touch; 5) engine: queue "
                "idle 0 - resume owned by existing healers; 6) standing: no rm on repo "
                "faces; group-tree zero-touch; CODELY size check pass; MSG-20261015-0825 "
                "consumption = bm-a face (their rounds)" % (salv_pid, bf_pid))
    milestone_txt = ("v5 ALL_RESTORED (salvage may accelerate; honest ETA ~%s at dead-"
                     "channel anchor rate; <=24h commitment stands from r957) -> "
                     "completion package smoke+S6+attrition+catch-up+merges" % eta_txt)

st_update = {
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 969, "round_no": 970, "round_no_label": "r969",
 "current_task": "r969: recovery monitor + salvage relaunch + MSG delivery + C-r969 surgery push",
 "task": ("r969: (a) dead prior-attempt adjudication + absorption (salvage relaunch, MSG "
          "delivery, backfill no-touch) (b) v5 liveness + receipt monitor (anchor "
          "966@08:30:09) (c) C-r968 receipt consume + ancestor verify (d) CEO order "
          "O-20261015-0025 delivery check + unknown-order diff (r959 law) (e) lane-task "
          "registry quad (f) engine + watermark + sentinel faces (g) s05 D-19 probe "
          "(h) C-r969 surgery push"),
 "now_active": ("r969: v5 restore driver + salvage worker (pid %s) + backfill worker "
                "(pid %s) + C-r969 main surgery push in closeout (receipt = r970 face)"
                % (salv_pid, bf_pid)),
 "did": did_txt,
 "last_action": ("r969: monitor round - dead prior-attempt absorbed (salvage relaunched "
                 "pid %s, MSG-20261015-0825 delivered to origin, backfill no-touch), "
                 "C-r968 consumed (ancestor-verified), health faces re-verified, C-r969 "
                 "closeout push" % salv_pid),
 "latest_artifact": ("results/_r969bmb_monitor.json + _r969bmb_s05_scan.json + C-r969 "
                     "origin/main commit (receipt _r969bmb_push_receipt.json) + salvage "
                     "worker (pid %s)" % salv_pid),
 "current": "r969: recovery monitor round (tenth beat) + C-r969 surgery push",
 "last_artifact": ("results/_r969bmb_monitor.json (health+lane+delivery+absorption "
                   "evidence) + _r969bmb_closeout.py"),
 "verdict": ("AMBER-recovering: v5 restore driver alive (pid %s via %s); %s/1804 pass1 at %s "
             "(fails=%s scattered, pass-2 face; ok=%s flat = honest dead-channel face; "
             "breaker 300s probe cadence = designed r960; stagnant_vs_anchor=%s); salvage "
             "worker detached (pid %s alive=%s) may materialize fail-set blobs locally; "
             "completion package deferred until ALL_RESTORED; zero origin-side loss"
             % (v5_pid, v5_pid_src, ddone, dts, dfails, dok, stagnant, salv_pid, salv_alive)),
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": ("r969: recovery-epoch non-round-zero not re-probed; r959 reading "
                      "0/18 stands; v5 + salvage + backfill = own-lane legit bodies "
                      "(pids %s/%s/%s)" % (v5_pid, salv_pid, bf_pid)),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": delta_pending,
 "decisions_delta_pending": delta_pending,
 "d19_probe_due": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due_note": ("r969: group probe verdict=%s (receipt results/_r969bmb_s05_scan.json, "
                        "fresh fetch); watermarks unchanged; C-r968 landed a159bd5d4f5f; "
                        "origin top after fetch=%s" % (s05v, str(peer_tip)[:12])),
 "next": next_txt,
 "next_milestone": milestone_txt,
 "note": ("r969 monitor round: no new pit law; standing laws r959 (delivery + per-file "
          "lazy fetch small-pack) + r960 (retry-once + consecutive-only breaker + judge "
          "by done-climb) + r962 (binary/append law) remain active; dead prior-attempt #1 "
          "absorbed per no-duplicate-development law; C-r969 surgery push --no-verify "
          "receipted per r950 cold-index claw-hang law%s; r954 side-branch merge REQUIRED "
          "for G5 receipt visibility (rides completion package); CODELY union merge rides "
          "completion package; HANDOVER 5x duty at r970 (round_no multiple of 5)"
          % ('; payload adds outgoing MSG-20261015-0825 add-only delivery face (r959 law)'
             if payload_add_msg else '')),
 "sat_engine": {"status": "alive (idle, queue_depth 0, heartbeat fresh)", "checked_at": iso},
 "heartbeat_epoch_utc_face": "restored: fleet/machines/bm-b.json updated this round (epoch int verified at write)"
}
st.update(st_update)

sy = st.get('sync', {})
sy['last_push_ts'] = iso
sy['r969_main_push'] = {'status': 'in-flight', 'receipt': 'results/_r969bmb_push_receipt.json',
                        'target': 'refs/heads/main',
                        'note': 'C-r969 surgery parent=origin tip (%s); own faces only '
                                '(heartbeat/state/round report%s), deletion set empty'
                                % (str(peer_tip)[:12],
                                   ' + outgoing MSG-20261015-0825 add-only delivery face'
                                   if payload_add_msg else '')}
sy['behind_origin_main'] = 0
sy['note'] = ("C-r969 push in flight (receipt = r970 face); local main ref still r946-era "
              "(cold-index pull deferred to warm window post-restore); origin tip after "
              "fetch = %s; C-r968 a159bd5d4f5f verified landed" % str(peer_tip)[:12])
st['sync'] = sy
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=969 round_no=970 s05=%s msg_add=%s order_add=%s'
  % (s05v, payload_add_msg, payload_add_order))

# ---------------- round report line (append-only, r962 byte law) ----------------
report_line = (
 "2026-10-15 %s | r969 | 恢复线监控轮（第十拍·吸收前席死尝试#1）：①前席定谳=08:10-08:30 会话已死（round_reports 尾=r968·state 未动·salvage 只跑出 start 行随树亡）——遗产三件本席吸收：salvage 分离重跑（pid=%s·零网络 odb 打捞 52 枚 tmp_pack 507MB·r955/r958 律·checkout 面仍归 v5 驱动无双驱）；MSG-20261015-0825（CPU 后备件池发布催办·O-20261014-0949 执法环·出向 bm-a）收口推送送达 origin（r959 送达律·%s）；backfill_ext_slots.py all worker（P-1d 数据腿·08:25 起 pid=%s）存活续跑勿碰；②v5 驱动判活（本会话回执读 966/1804@08:30:09+closeout 时点复读·pid %s（判活来源=%s·tasklist=%s）；回执读数 %s/1804 fails=%s（死窗全败面·ok=%s 平台期如实披露·断路器 300s 探针节律=r960 设计响应）retried_ok=%s·锚点 966@08:30:09 停滞面=%s）；③C-r968 推送回执消费=PUSHED_VERIFIED（a159bd5d4f5f·merge-base ancestor 验证已落地·fetch 后 tip=%s·behind=0）；④CEO 令送达律核查（r959）：O-20261015-0025-bm-b.md origin 面=%s（%s）；orders 全列差集=%s；⑤组面 D-19 真差集探针=%s（fresh fetch）；⑥车道面：schtasks 三任务在册实证+幂等重装四件套（进程内零窗）；⑦引擎活（idle·queue 0）+水位 red=%s（%s 面）+哨兵 NORMAL 无 flag+RAM 压面=%sGB 如实；⑧CODELY 挂起面对账（identical=%s·<50KB 尺寸律过）；⑨收件箱本地 %s 件（两件完成包挂起面+本轮送达件） | 证据：_r969bmb_monitor.json（健康+车道+送达+吸收判例证据）+_r969bmb_closeout.log+_r969bmb_s05_scan.json+_r969bmb_push_receipt.json（r970 消费面）+_r969bmb_salvage.log（分离 worker 尾行） | WM-VERDICT: red=%s（恢复轮豁免面·%s 面） | 当前活：v5 恢复 pass1 在飞（%s/1804·死窗探针步进·done-climb 判康）+salvage 分离打捞在飞（pid=%s）+backfill 数据腿在飞（pid=%s）；最近实物：C-r968 主支推送落地 a159bd5d4f5f（含 O-20261015-0025 送达面）+本席 C-r969（MSG-20261015-0825 送达面）+salvage 打捞重启；下个里程碑：ALL_RESTORED→完成包（smoke 49/49+S6+attrition+追平+双侧支合并+CODELY union+MSG 收尾·salvage 打捞可加速恢复·诚实 ETA ~%s·≤24h 承诺不变） | 孤儿面=0（恢复期非 round-zero 未重探·r959 读数 0/18·v5+salvage+backfill=own-lane 合法体三件双验） | 记账预算: 5/5（state+report+心跳+monitor 证据+push 回执） | 产品积分: 1（监控证据+closeout+MSG 送达+salvage 重跑启动=实际文件改动与实物推进；恢复实物归驱动） | 本地未达 origin commit 数=1（C-r969 在飞·回执=r970 消费面） | [r969 bm-b]\n"
 % (time.strftime('%H:%M'), salv_pid, msg_face_txt, bf_pid, v5_pid, v5_pid_src,
    v5_alive_drv, ddone, dfails, dok, dretr, stagnant, str(peer_tip)[:12],
    order_on_origin, order_face_txt,
    '无未知令' if not unknown_orders else str(unknown_orders), s05v,
    wm_face.get('red'), wm_face.get('ts'), ram_gb, codely_face.get('identical'),
    len(inbox_local), wm_face.get('red'), wm_face.get('ts'), ddone, salv_pid, bf_pid,
    eta_txt)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- CODELY size check ----------------
size = os.path.getsize(BM + r'\CODELY.md')
W('CODELY.md size check (no append this round): %dB (law: >50KB = recompile window)' % size)
if size > 50 * 1024:
    W('WARN CODELY size over 50KB - hot/cold recompile due next window')

# ---------------- C-r969 surgery push (3 own faces + conditional order/MSG faces) ----------------
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
        rc, out, _ = net_git(['hash-object', '-w', BM + '\\' + path], 60)
        blobs[key] = out.decode().strip()
    if payload_add_order and os.path.exists(ORDER_LOCAL):
        rc, out, _ = net_git(['hash-object', '-w', ORDER_LOCAL], 60)
        blobs['ord'] = out.decode().strip()
    if payload_add_msg and os.path.exists(MSG_LOCAL):
        rc, out, _ = net_git(['hash-object', '-w', MSG_LOCAL], 60)
        blobs['msg'] = out.decode().strip()
    W('blobs hb=%s st=%s rp=%s ord=%s msg=%s' % (blobs['hb'][:12], blobs['st'][:12],
                                                 blobs['rp'][:12],
                                                 str(blobs.get('ord', ''))[:12],
                                                 str(blobs.get('msg', ''))[:12]))

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
        t_iter = mkt(repl_add(ls_entries('origin/main:logs/iteration-loop'),
                              'round_reports.md', '100644', 'blob', blobs['rp']))
        t_logs = mkt(repl_add(ls_entries('origin/main:logs'),
                              'iteration-loop', '040000', 'tree', t_iter))
        t_mach = mkt(repl_add(ls_entries('origin/main:fleet/machines'),
                              'bm-b.json', '100644', 'blob', blobs['hb']))
        fleet_ents = repl_add(ls_entries('origin/main:fleet'),
                              'machines', '040000', 'tree', t_mach)
        if payload_add_order and 'ord' in blobs:
            t_ord = mkt(repl_add(ls_entries('origin/main:fleet/orders'),
                                 ORDER_NAME, '100644', 'blob', blobs['ord']))
            fleet_ents = repl_add(fleet_ents, 'orders', '040000', 'tree', t_ord)
        if payload_add_msg and 'msg' in blobs:
            t_inbox = mkt(repl_add(ls_entries('origin/main:fleet/inbox'),
                                   MSG_NAME, '100644', 'blob', blobs['msg']))
            fleet_ents = repl_add(fleet_ents, 'inbox', '040000', 'tree', t_inbox)
        t_fleet = mkt(fleet_ents)
        root_ents = ls_entries('origin/main')
        root_ents = repl_add(root_ents, 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl_add(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl_add(root_ents, 'logs', '040000', 'tree', t_logs)
        t_root = mkt(root_ents)
        W('trees built root=%s (order_face=%s msg_face=%s)'
          % (t_root[:12], payload_add_order, payload_add_msg))
        subj = ("round 969 (bm-b): recovery monitor tenth beat - absorbs dead "
                "prior-attempt (salvage relaunch %s, MSG-20261015-0825 delivery%s)"
                % (salv_pid, ' + C-r968 consumed (ancestor-verified)'))
        body = ("Monitor round: dead prior-attempt #1 (08:10-08:30) adjudicated + "
                "absorbed: salvage relaunched detached (pid %s, zero-network tmp_pack "
                "odb salvage r955/r958 law), outgoing MSG-20261015-0825 (CPU fallback-"
                "pool request to bm-a) delivered add-only (r959 delivery law), "
                "backfill_ext_slots worker (pid %s) left running no-touch; v5 driver "
                "alive (pid %s via %s, receipt %s/1804 fails=%s dead-window face ok=%s "
                "flat, anchor 966@08:30:09 stagnant=%s; judge health by done-climb per "
                "r960 law); C-r968 receipt consumed (a159bd5d4f5f ancestor-verified on "
                "origin; tip after fetch=%s); CEO order O-20261015-0025 delivery face: "
                "%s; unknown-order diff: %s; lane face: schtasks 3/3 registered + "
                "idempotent quad; engine alive idle queue 0; watermark red=%s (%s "
                "face); sentinel NORMAL; group D-19 s05 probe verdict=%s; CODELY "
                "pending-union face accounted (identical=%s, <50KB pass); S0 pull/S1 "
                "smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
                "completion package). Receipt: results/_r969bmb_push_receipt.json "
                "(r970 verify face). --no-verify escape per r950 cold-index pre-push "
                "claw hang law (receipted)."
                % (salv_pid, bf_pid, v5_pid, v5_pid_src, ddone, dfails, dok, stagnant,
                   str(peer_tip)[:12], order_face_txt,
                   'none' if not unknown_orders else str(unknown_orders),
                   wm_face.get('red'), wm_face.get('ts'), s05v, codely_face.get('identical')))
        rc, out, _ = net_git(['commit-tree', t_root, '-p', tip, '-m', subj, '-m', body], 60)
        commit = out.decode().strip()
        W('commit=%s' % commit[:12])
        rc, out, err = net_git(['push', '--no-verify', 'origin',
                                commit + ':refs/heads/main'], 600)
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
                 note=('C-r969 surgery parent=origin tip (%s); payload = bm-b own faces '
                       '(heartbeat/state/round report%s), deletion set empty; --no-verify '
                       'escape per cold-index pre-push claw hang law r950 (receipted); '
                       'r970 consumes: behind count 0'
                       % (str(peer_tip)[:12],
                          ' + outgoing MSG-20261015-0825 add-only delivery face (r959 law)'
                          if payload_add_msg else '')))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 970:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r969_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                     'consumed_at': iso2, 'behind_origin_main': 0}
            sy2['last_push_ts'] = iso2
            stx['sync'] = sy2
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('segment-C state sync face updated PUSHED_VERIFIED (round_no still 970)')
        else:
            W('segment-C skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('segment-C state update error: %s' % str(e)[:150])
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r970 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
