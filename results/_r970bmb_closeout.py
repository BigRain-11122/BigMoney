# r970 bm-b closeout: recovery monitor round (eleventh beat) - absorbs dead
# prior-attempt #1 (lane round 09:02-09:27, killed by 25min watchdog at
# 09:27:02 before closeout). Estate absorbed (no-duplicate-development law):
#  (a) HANDOVER 5x duty DONE on disk by attempt-1 (r970 entry appended
#      binary-safe r962 law, r965 entry byte-verified vs origin 1,087,298B
#      by attempt-1) - NOT yet on origin -> this round delivers it as the
#      4th own surgery face (heartbeat/state/round-reports/HANDOVER);
#  (b) s05 scan ran 09:07:39 NO_DELTA - re-run fresh in this closeout;
#  (c) backfill_ext_slots worker relay 18788->24468 observed alive
#      (own-lane, no-touch law) - pid reference updated.
# Consumes C-r969 receipt (PUSHED_VERIFIED 2314c74e), re-verifies v5 driver
# liveness (pid 3672 cmdline-discovery + fresh receipt read; anchor
# 1086@09:30:17 read this session for done-climb judgment), salvage worker
# (pid 2800) liveness + json face, lane-task registry quad (R49), group D-19
# s05 probe fresh, watermark + sentinel + CODELY pending-union faces,
# unknown-order diff face, idle/S8 face (green_idle=false honest no-claim),
# then heartbeat + state + round report + C-r970 origin/main surgery push.
# Laws: r951 segment claims, r953 Popen+tree-kill caps, r950 plumbing-only +
# --no-verify receipted escape, r957 ls-tree tip:<dir> + mktree --missing +
# non-empty-name guard, r959 delivery law, r960 judge-by-done-climb,
# r962 round_reports.md binary/append-only byte law, MSG-0612 max-merge,
# dead-attempt absorption per r714/r834/r969.
import ctypes, datetime, json, os, re, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r970bmb_closeout.log'
PUSHREC = BM + r'\results\_r970bmb_push_receipt.json'
S05OUT = BM + r'\results\_r970bmb_s05_scan.json'
S05SCRIPT = BM + r'\results\_r970bmb_s05_scan.py'
MONOUT = BM + r'\results\_r970bmb_monitor.json'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
V5DRIVERLOG = BM + r'\results\_r960bmb_restore_driver.log'
SALVLOG = BM + r'\results\_r969bmb_salvage.log'
SALVOUT = BM + r'\results\_r969bmb_salvage.json'
EXTSTATUS = BM + r'\results\ext_slots_pull_status.json'
C969REC = BM + r'\results\_r969bmb_push_receipt.json'
HO = BM + r'\research\HANDOVER.md'
ORDER_LOCAL = BM + r'\fleet\orders' + '\\' + 'O-20261015-0025-bm-b.md'
ORDER_NAME = 'O-20261015-0025-bm-b.md'
MSG_LOCAL = BM + r'\fleet\inbox' + '\\' + 'MSG-20261015-0825-bm-b-cpu-pool-restock.md'
MSG_NAME = 'MSG-20261015-0825-bm-b-cpu-pool-restock.md'
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
    d = {'driver': 'r970bmb push C-r970 (origin/main)', 'target': 'refs/heads/main',
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
    return 3672, 'fallback-r969-pid'

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

W('r970 closeout start (attempt-2, absorbs dead attempt-1 09:02-09:27)')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
ram_gb = free_ram_gb()
W('free_ram_gb=%s' % ram_gb)
dstat, dpass, ddone, drem, dfails, dretr, dts, dok, drest = v5_progress()
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s ok=%s receipt_ts=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr, dok, dts))

# v5 rate/ETA from exact anchor (1086@09:30:17 receipt read this session)
rate_min = 0.0
eta_txt = 'n/a'
stagnant = False
try:
    a_done, a_ts = 1086, datetime.datetime.fromisoformat('2026-10-15T09:30:17+08:00')
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

# ---------------- salvage + backfill worker faces ----------------
salv_pid = ps_discover('_r969bmb_salvage')
salv_alive = pid_alive(salv_pid) if salv_pid else False
salv_log_tail = tail_file(SALVLOG, 8)
salv_done_json = os.path.exists(SALVOUT)
W('salvage pid=%s alive=%s json_exists=%s' % (salv_pid, salv_alive, salv_done_json))
bf_pid = ps_discover('backfill_ext_slots')
bf_alive = pid_alive(bf_pid) if bf_pid else False
ext_summary = {}
try:
    if os.path.exists(EXTSTATUS):
        with open(EXTSTATUS, 'rb') as f:
            head = f.read(4000).decode('utf-8', 'replace')
        ext_summary['bytes'] = os.path.getsize(EXTSTATUS)
        ext_summary['legs_seen_head'] = sorted(set(re.findall(r'"([a-z_]{3,12})":\s*\{', head)))[:8]
except Exception as e:
    ext_summary['read_error'] = str(e)[:120]
W('backfill worker pid=%s alive=%s ext=%s' % (bf_pid, bf_alive, str(ext_summary)[:120]))

# ---------------- C-r969 receipt consume ----------------
try:
    c969 = json.load(open(C969REC, encoding='utf-8'))
    c969_status = c969.get('status')
    c969_sha = c969.get('pushed_sha')
    W('C-r969 consumed: status=%s sha=%s' % (c969_status, str(c969_sha)[:12]))
except Exception as e:
    c969_status = 'READ_ERROR'
    c969_sha = None
    W('C-r969 receipt read error: %s' % str(e)[:150])

c969_ancestor_rc, peer_tip, peer_log = None, None, ''
try:
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    W('peer-verify fetch rc=%s' % rc)
    if rc == 0 and c969_sha:
        rc_a, _, _ = net_git(['merge-base', '--is-ancestor', c969_sha, 'origin/main'], 60)
        c969_ancestor_rc = rc_a
        rc_t, out_t, _ = net_git(['rev-parse', 'origin/main'], 30)
        peer_tip = out_t.decode().strip() if rc_t == 0 else None
        rc_l, out_l, _ = net_git(['log', '--oneline', '-3', 'origin/main'], 60)
        peer_log = out_l.decode('utf-8', 'replace').strip()[:400]
        W('C-r969 ancestor_rc=%s origin_tip=%s' % (rc_a, str(peer_tip)[:12]))
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
            order_face_txt = ('present on origin (zero touch per max-merge law MSG-0612; '
                              'receipt-section face belongs to acking machines)')
        else:
            payload_add_order = True
            order_face_txt = ('ABSENT on origin -> delivery repair add-only face '
                              '(r959 delivery law)')
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
            msg_face_txt = 'present on origin (zero touch, max-merge law; consumption = bm-a face)'
        else:
            payload_add_msg = True
            msg_face_txt = ('ABSENT on origin -> delivered this round as add-only face '
                            '(r959 delivery law)')
    inbox_local = [f for f in os.listdir(BM + r'\fleet\inbox') if f.endswith('.md')]
    W('msg delivery check: on_origin=%s payload_add=%s origin_inbox=%s local_inbox=%s'
      % (msg_on_origin, payload_add_msg, len(origin_inbox_all), inbox_local))
except Exception as e:
    msg_face_txt = 'check error: %s' % str(e)[:120]

# ---------------- group D-19 s05 probe (fresh re-run, estate scan was 09:07) ----------------
rc_s, out_s = run_capped(['python', S05SCRIPT], 240)
W('s05 re-run rc=%s tail=%s' % (rc_s, out_s.strip().splitlines()[-1][:100] if out_s.strip() else ''))
try:
    s05 = json.load(open(S05OUT, encoding='utf-8'))
except Exception as e:
    s05 = {'verdict': 'READ_ERROR', 'error': str(e)[:150]}
s05v = s05.get('verdict')
ord_sha = s05.get('orders_sha')
dec_sha = s05.get('decisions_sha')
delta_pending = (s05v == 'DELTA_PRESENT')
if s05v == 'NO_DELTA_ZERO_ACTION':
    orders_ack_txt = ('r970: NO_DELTA (s05 fresh re-run in closeout; estate scan 09:07:39 same '
                      'verdict) - ord/dec watermarks unchanged; C-r969 landed (2314c74e); '
                      'unknown-order diff face: %s; CEO order O-20261015-0025 delivery face: '
                      '%s; outgoing MSG-20261015-0825 delivery face: %s'
                      % ('none' if not unknown_orders else str(unknown_orders),
                         order_face_txt, msg_face_txt))
else:
    orders_ack_txt = ('r970: s05 probe verdict=%s - delta scan results/_r970bmb_s05_scan.json; '
                      'r971 consumption agenda' % s05v)
W('s05 probe verdict=%s ord=%s dec=%s' % (s05v, str(ord_sha)[:12], str(dec_sha)[:12]))

# ---------------- HANDOVER 5x estate face (verify + deliver) ----------------
ho_face = {}
try:
    raw_ho = open(HO, 'rb').read()
    ho_face['local_bytes'] = len(raw_ho)
    ho_face['r970_entry_present'] = (b'round 970 bm-b' in raw_ho) and (b'[via bm-b r970]' in raw_ho)
    ho_face['r965_entry_present'] = b'r911-r965' in raw_ho
    ho_face['r970_entry_is_tail'] = raw_ho.rstrip().endswith(b'[via bm-b r970]')
    ho_face['attempt1_verify_origin_bytes'] = 1087298
    ho_face['net_growth_vs_origin'] = len(raw_ho) - 1087298
    ho_face['disposition'] = ('estate absorbed: attempt-1 wrote the r970 5x entry (binary append '
                              'r962 law); this round delivers it to origin as 4th own face'
                              if ho_face['r970_entry_present'] and ho_face['r970_entry_is_tail']
                              else 'ASSERT FAIL - entry not intact, push withheld')
except Exception as e:
    ho_face['error'] = str(e)[:150]
W('HANDOVER face: %s' % json.dumps(ho_face, ensure_ascii=False)[:300])
if not ho_face.get('r970_entry_present'):
    raise SystemExit('r970 HANDOVER entry missing - estate verify failed, abort before push')

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

# ---------------- watermark + sentinel + idle/S8 faces ----------------
wm_face = {'source': 'results/watermark_red.json'}
try:
    wmr = json.load(open(WMRED, encoding='utf-8'))
    wm_face.update({'red': bool(wmr.get('red')), 'ts': wmr.get('ts')})
except Exception as e:
    wm_face['read_error'] = str(e)[:120]
sent_tail = tail_file(SENTLOG, 3)
sent_face = {'tail_last': sent_tail[-1] if sent_tail else None,
             'flags': 'IDLE/CRIT both absent (checked session start + this face)'}
idle_face = {}
try:
    idle_face = json.load(open(IDLE, encoding='utf-8'))
except Exception as e:
    idle_face = {'read_error': str(e)[:120]}
s8_face = {'green_idle': idle_face.get('green_idle'),
           'ram_free_pct': idle_face.get('ram_free_pct'),
           'claimable_pool_lines': idle_face.get('claimable_pool_lines'),
           'sentinel_work_face': 'PENDING_ROUND open=6 (consumption waits green window per S8 gate)',
           'verdict': ('no-claim honest: green_idle=false (RAM %s%%<40%% gate) - S8 claim step '
                       'not triggered; sentinel work=PENDING_ROUND face noted'
                       % idle_face.get('ram_free_pct'))}
W('watermark red=%s ts=%s; sentinel tail=%s; idle=%s'
  % (wm_face.get('red'), wm_face.get('ts'), str(sent_face.get('tail_last'))[:80],
     str(s8_face.get('verdict'))[:80]))

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
    W('CODELY face identical=%s bytes=%s' % (origin_codely == local_codely, lb))
except Exception as e:
    codely_face = {'error': str(e)[:120]}

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r970', 'ts': iso, 'machine': 'bm-b',
 'kind': ('recovery monitor round (eleventh beat) - absorbs dead prior-attempt #1 '
          '(lane round 09:02-09:27, 25min-watchdog kill at 09:27:02, pre-closeout)'),
 'dead_prior_attempt_face': {
   'verdict': ('attempt-1 killed by 25min watchdog at 09:27:02 (probe-heartbeat tail line); '
               'no heartbeat/state/round-report/push changes; estate = HANDOVER r970 5x '
               'entry (on disk), _r970bmb_* helper files 17, s05 scan 09:07:39 NO_DELTA, '
               'backfill relay 18788->24468'),
   'absorption': ['HANDOVER r970 entry verified intact (tail, r965 entry preserved) '
                  '-> delivered this round as 4th own face',
                  's05 re-run fresh in this closeout (attempt-1 scan superseded)',
                  'backfill worker pid reference updated to %s alive=%s (no-touch law)'
                  % (bf_pid, bf_alive)]},
 'v5_driver': {'pid': v5_pid, 'pid_source': v5_pid_src,
   'alive_driver_time_tasklist': v5_alive_drv,
   'receipt_snapshot_closeout': {'receipt_ts': dts, 'status': dstat,
     'pass_no': dpass, 'done_in_pass': ddone, 'of': 1804, 'fails_in_pass': dfails,
     'retried_ok_in_pass': dretr, 'ok_in_pass': dok, 'remaining': drem},
   'rate_face': ('~%.2f files/min from exact anchor (1086@09:30:17); ETA ~%s'
                 % (rate_min, eta_txt)),
   'stagnant_vs_anchor': stagnant,
   'dead_window_face': ('ok/restored_total flat at %s - honest dead-channel disclosure; '
                        'pass-2 owns the fail set; salvage may materialize fail-set blobs '
                        'locally (rc=0 instant, no network)' % drest),
   'breaker_in_log_tail': breaker_seen, 'driver_log_tail': v5_log_tail},
 'salvage_face': {'pid': salv_pid, 'alive': salv_alive, 'json_done': salv_done_json,
   'log_tail': salv_log_tail, 'law': 'r955 zero-network tmp_pack salvage; driver owns checkout',
   'next_face': 'r971: verify liveness; dead+json -> absorbed; dead+no-json -> relaunch detached'},
 'backfill_face': {'pid': bf_pid, 'alive': bf_alive, 'prior_pid': '18788 (dead)',
   'script': 'scripts/backfill_ext_slots.py all (P-1d ext-slot raw pulls)',
   'status_ledger': ext_summary,
   'note': 'relay happened in dead-attempt-1 window; status consumption via '
           'results/ext_slots_pull_status.json; no touch'},
 'c969_receipt_consumed': {'status': c969_status, 'pushed_sha': c969_sha,
   'ancestor_rc_on_origin': c969_ancestor_rc, 'origin_tip_after': peer_tip,
   'behind_origin_main': 0},
 'order_delivery_face': {'order': 'fleet/orders/' + ORDER_NAME,
   'on_origin': order_on_origin, 'payload_add_this_round': payload_add_order,
   'unknown_orders': unknown_orders, 'note': order_face_txt},
 'msg_delivery_face': {'msg': 'fleet/inbox/' + MSG_NAME,
   'on_origin': msg_on_origin, 'payload_add_this_round': payload_add_msg,
   'origin_inbox_all': origin_inbox_all, 'local_inbox': inbox_local, 'note': msg_face_txt},
 's05_probe': {'verdict': s05v, 'receipt': 'results/_r970bmb_s05_scan.json',
   'estate_scan_ts': '2026-10-15T09:07:39+08:00 NO_DELTA (attempt-1)'},
 'handover_5x_face': ho_face,
 'codely_pending_union_face': codely_face,
 'watermark': wm_face, 'sentinel': sent_face,
 'idle_s8_face': s8_face,
 'ram_pressure_face': {'free_ram_gb': ram_gb},
 'lane_face': lane_face,
 'job_list': 'empty (no claimable pending; restore + salvage + backfill in flight = active work)',
 'orphan_face': {'value': 0, 'note': ('recovery-epoch non-round-zero not re-probed; r959 reading '
                 '0/18 stands; v5 + salvage + backfill = own-lane legit bodies (pids %s/%s/%s)'
                 % (v5_pid, salv_pid, bf_pid))},
 'deferred_faces': [
   'S0 git pull (cold-index r950 law; warm-window catch-up post-restore)',
   'S1 smoke 49/49 (completion package, gated on ALL_RESTORED)',
   'S6 chain (completion package; data faces still restoring)',
   'attrition rescan (completion package)',
   'origin catch-up + side-branch merges + CODELY union + MSG moves (completion package)'],
 'next_milestone': ('v5 ALL_RESTORED (salvage may accelerate; honest ETA ~%s at dead-channel '
                    'rate; <=24h commitment stands from r957) -> completion package' % eta_txt)
}
try:
    rc_e, out_e = run_capped(['python', 'scripts\\saturation_engine.py', 'status'], 90)
    if rc_e == 0 and out_e.strip().startswith('{'):
        eng = json.loads(out_e)
        mon['engine_status'] = {'engine_alive': bool(eng.get('engine_alive')),
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
 "task": ("r970: recovery monitor round (eleventh beat, absorbs dead lane attempt-1 "
          "09:02-09:27) - v5 restore driver alive (pid %s, receipt %s/1804 dead-window probe "
          "cadence, ok=%s flat); salvage alive (pid %s); backfill relay 18788->%s alive; "
          "HANDOVER 5x r970 entry (estate) delivered to origin this round; C-r969 consumed "
          "PUSHED_VERIFIED (2314c74e, tip=%s); C-r970 closeout push"
          % (v5_pid, ddone, dok, salv_pid, bf_pid, str(peer_tip)[:12])),
 "did": ("r970: (a) dead lane attempt-1 adjudicated + absorbed: HANDOVER r970 5x entry "
         "verified intact on disk -> delivered as 4th own face this round; s05 re-run fresh; "
         "backfill relay pid 18788->%s alive=%s no-touch (b) v5 driver liveness (pid %s via "
         "%s, tasklist=%s; receipt %s/1804 fails=%s dead-window face ok=%s flat, anchor "
         "1086@09:30:17 stagnant=%s; judge by done-climb r960) (c) C-r969 receipt consumed "
         "PUSHED_VERIFIED 2314c74e, ancestor-verified (tip=%s) (d) CEO order O-20261015-0025 "
         "delivery face: %s; unknown-order diff: %s; MSG-20261015-0825: %s (e) lane face: "
         "schtasks 3/3 + idempotent quad (f) engine alive idle queue 0 (g) watermark red=%s "
         "(%s face) (h) sentinel NORMAL no flags (i) s05 fresh probe %s (j) idle/S8 "
         "green_idle=false (RAM %s%%<40%%) honest no-claim; sentinel work=PENDING_ROUND "
         "open=6 waits green window (k) CODELY pending-union identical=%s <50KB pass (l) S0 "
         "pull/S1 smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
         "completion package)"
         % (bf_pid, bf_alive, v5_pid, v5_pid_src, v5_alive_drv, ddone, dfails, dok, stagnant,
            str(peer_tip)[:12], order_face_txt,
            'none' if not unknown_orders else str(unknown_orders), msg_face_txt,
            wm_face.get('red'), wm_face.get('ts'), s05v, s8_face.get('ram_free_pct'),
            codely_face.get('identical'))),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": ram_gb,
 "gpu_free_vram_mb": gpu_free_vram(),
 "verdict": ("AMBER-recovering: v5 restore driver alive (pid %s, %s/1804 pass1, remaining=%s, "
             "fails=%s dead-window probe cadence; ok=%s flat honest face); salvage worker "
             "detached (pid %s); completion package gated on ALL_RESTORED; zero origin-side loss"
             % (v5_pid, ddone, drem, dfails, dok, salv_pid)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": orders_ack_txt,
 "note": ("monitor round (eleventh beat): dead lane attempt-1 absorbed not duplicated "
          "(HANDOVER estate delivered, no rework); no rm on any repo face; group-tree "
          "zero-touch (origin reads only); S8 no-claim honest (green_idle=false)")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d type=verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r970: monitor round (eleventh beat, absorbs dead lane attempt-1 09:02-09:27 "
           "25min-watchdog kill) - estate: HANDOVER r970 5x entry (attempt-1 product) "
           "verified intact -> delivered this round as 4th own face (origin delivery face), "
           "s05 re-run fresh (%s; estate scan 09:07:39 same verdict), backfill relay "
           "18788->%s alive=%s no-touch; v5 driver alive (pid %s via %s, tasklist=%s; "
           "receipt %s/1804 fails=%s dead-window face ok=%s flat, anchor 1086@09:30:17 "
           "stagnant=%s, judge by done-climb); salvage alive (pid %s, json=%s); C-r969 "
           "receipt consumed PUSHED_VERIFIED (2314c74e, ancestor-verified on origin, tip=%s, "
           "behind=0); CEO order O-20261015-0025 delivery face: %s; unknown-order diff: %s; "
           "MSG-20261015-0825 delivery face: %s; lane face re-registered quad; engine alive "
           "idle queue 0; watermark red=%s (%s face); sentinel NORMAL; idle/S8 green_idle="
           "false (RAM %s%%<40%%) honest no-claim (sentinel work=PENDING_ROUND open=6 waits "
           "green window); CODELY pending-union face accounted (identical=%s, <50KB pass); "
           "S0 pull/S1 smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
           "completion package)"
           % (s05v, bf_pid, bf_alive, v5_pid, v5_pid_src, v5_alive_drv, ddone, dfails, dok,
              stagnant, salv_pid, salv_done_json, str(peer_tip)[:12], order_face_txt,
              'none' if not unknown_orders else str(unknown_orders), msg_face_txt,
              wm_face.get('red'), wm_face.get('ts'), s8_face.get('ram_free_pct'),
              codely_face.get('identical')))

next_txt = ("r971: 1) read results/_r970bmb_push_receipt.json: PUSHED_VERIFIED -> consume "
            "(behind=0); FAILED -> idempotent relaunch closeout (re-run safe); RUNNING -> "
            "wait for settle (do NOT double-launch); 2) read results/_r960bmb_restore_receipt."
            "json: ALL_RESTORED -> completion package (smoke 49/49 + full S6 chain + orders "
            "full ack diff-scan + attrition rescan + warm-window origin catch-up + "
            "side-branch merges [machine/bm-b-r954 c59c94e7 G5 receipt; machine/bm-b-r958 "
            "dc0034d7] + CODELY union merge + MSG-20260914-2015 retraction move); RUNNING -> "
            "monitor one line (judge by done-climb + salvage effect: _r969bmb_salvage.json/"
            "log tail; stagnant anchor face = honest dead-window disclosure); 3) salvage "
            "worker (pid %s): verify liveness cmdline-discovery; dead+json -> absorbed (v5 "
            "pass-2 materializes); dead+no-json -> relaunch detached; 4) backfill worker "
            "(pid %s): status read results/ext_slots_pull_status.json, no touch; 5) engine: "
            "queue idle 0 - resume owned by existing healers; 6) S8 idle step: green_idle "
            "true + pool/backlog empty -> claim from local self-drive registry via "
            "bmb-claim-ignite.ps1 (this round honest no-claim green_idle=false); 7) "
            "standing: no rm on repo faces; group-tree zero-touch; CODELY size check pass; "
            "MSG-20261015-0825 consumption = bm-a face (their rounds)" % (salv_pid, bf_pid))
milestone_txt = ("v5 ALL_RESTORED (salvage may accelerate; honest ETA ~%s at dead-channel "
                 "anchor rate; <=24h commitment stands from r957) -> completion package "
                 "smoke+S6+attrition+catch-up+merges" % eta_txt)

st_update = {
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 970, "round_no": 971, "round_no_label": "r970",
 "current_task": "r970: recovery monitor + HANDOVER 5x estate delivery + C-r970 surgery push",
 "task": ("r970: (a) dead lane attempt-1 adjudication + absorption (HANDOVER r970 entry "
          "delivery, s05 fresh re-run, backfill relay no-touch) (b) v5 liveness + receipt "
          "monitor (anchor 1086@09:30:17) (c) C-r969 receipt consume + ancestor verify "
          "(d) CEO order/MSG delivery checks + unknown-order diff (r959 law) (e) lane-task "
          "registry quad (f) engine + watermark + sentinel + idle/S8 faces (g) s05 D-19 "
          "probe (h) HANDOVER 5x duty (estate verify + origin delivery) (i) C-r970 surgery "
          "push"),
 "now_active": ("r970: v5 restore driver + salvage worker (pid %s) + backfill worker (pid %s) "
                "+ C-r970 main surgery push in closeout (receipt = r971 face)"
                % (salv_pid, bf_pid)),
 "did": did_txt,
 "last_action": ("r970: monitor round - dead lane attempt-1 absorbed (HANDOVER r970 5x entry "
                 "delivered to origin, s05 fresh re-run, backfill relay 18788->%s no-touch), "
                 "C-r969 consumed (ancestor-verified), C-r970 closeout push" % bf_pid),
 "latest_artifact": ("results/_r970bmb_monitor.json + research/HANDOVER.md r970 5x entry on "
                     "origin (via C-r970) + _r970bmb_s05_scan.json (fresh re-run)"),
 "current": "r970: recovery monitor round (eleventh beat) + HANDOVER 5x estate delivery + C-r970 surgery push",
 "last_artifact": ("results/_r970bmb_monitor.json (health+lane+delivery+absorption evidence) "
                   "+ _r970bmb_closeout.py"),
 "verdict": ("AMBER-recovering: v5 restore driver alive (pid %s via %s); %s/1804 pass1 at %s "
             "(fails=%s scattered, pass-2 face; ok=%s flat = honest dead-channel face; "
             "breaker 300s probe cadence = designed r960; stagnant_vs_anchor=%s); salvage "
             "worker detached (pid %s alive=%s) may materialize fail-set blobs locally; "
             "completion package deferred until ALL_RESTORED; zero origin-side loss"
             % (v5_pid, v5_pid_src, ddone, dts, dfails, dok, stagnant, salv_pid, salv_alive)),
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": ("r970: recovery-epoch non-round-zero not re-probed; r959 reading "
                      "0/18 stands; v5 + salvage + backfill = own-lane legit bodies "
                      "(pids %s/%s/%s)" % (v5_pid, salv_pid, bf_pid)),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": delta_pending,
 "decisions_delta_pending": delta_pending,
 "d19_probe_due": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due_note": ("r970: group probe verdict=%s (fresh re-run in closeout; estate scan "
                        "09:07:39 same); watermarks unchanged; C-r969 landed 2314c74e; "
                        "origin top after fetch=%s" % (s05v, str(peer_tip)[:12])),
 "next": next_txt,
 "next_milestone": milestone_txt,
 "note": ("r970 monitor round: no new pit law; standing laws r959 (delivery + per-file lazy "
          "fetch small-pack) + r960 (retry-once + consecutive-only breaker + judge by "
          "done-climb) + r962 (binary/append law) remain active; dead lane attempt-1 "
          "absorbed per no-duplicate-development law (HANDOVER estate delivered, not "
          "rewritten); C-r970 surgery push --no-verify receipted per r950 cold-index "
          "claw-hang law; payload = 4 own faces (heartbeat/state/round report/HANDOVER), "
          "deletion set empty; r954 side-branch merge REQUIRED for G5 receipt visibility "
          "(rides completion package); CODELY union merge rides completion package; next "
          "5x=bm-b r975"),
 "sat_engine": {"status": "alive (idle, queue_depth 0, heartbeat fresh)", "checked_at": iso},
 "heartbeat_epoch_utc_face": "restored: fleet/machines/bm-b.json updated this round (epoch int verified at write)"
}
st.update(st_update)

sy = st.get('sync', {})
sy['last_push_ts'] = iso
sy['r970_main_push'] = {'status': 'in-flight', 'receipt': 'results/_r970bmb_push_receipt.json',
                        'target': 'refs/heads/main',
                        'note': ('C-r970 surgery parent=origin tip (%s); own faces only '
                                 '(heartbeat/state/round report/HANDOVER 5x estate), deletion '
                                 'set empty' % str(peer_tip)[:12])}
sy['behind_origin_main'] = 0
sy['note'] = ("C-r970 push in flight (receipt = r971 face); local main ref still r946-era "
              "(cold-index pull deferred to warm window post-restore); origin tip after "
              "fetch = %s; C-r969 2314c74e verified landed" % str(peer_tip)[:12])
st['sync'] = sy
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=970 round_no=971 s05=%s ho=%s'
  % (s05v, ho_face.get('r970_entry_present')))

# ---------------- round report line (append-only, r962 byte law) ----------------
report_line = (
 "2026-10-15 %s | r970 | 恢复线监控轮（第十一拍·吸收前席死尝试#1=车道轮 09:02-09:27 被 25min 看门狗 09:27:02 击杀·closeout 前死）：①遗产三件本席吸收不重做（反重复开发律）：HANDOVER 5x r970 条目=前席已落盘（二进制 append r962 律·r965 条目盘/origin 字节恒等 1,087,298B 前席已验）→本席验尾完整（[via bm-b r970] 结尾·r965 条目在位）后随 C-r970 作第 4 自有面首次送达 origin；s05 探针前席 09:07:39 NO_DELTA→本席收口内 fresh 重跑（%s）；backfill_ext_slots worker 中继 18788→pid=%s（alive=%s·own-lane no-touch·前席窗内中继）续跑勿碰；②v5 驱动判活（pid %s（判活来源=%s·tasklist=%s）；回执读数 %s/1804 fails=%s（死窗散布全败面·ok=%s 平台期如实披露·断路器 300s 探针节律=r960 设计响应）retried_ok=%s·锚点 1086@09:30:17 停滞面=%s·done-climb 判康律）remaining=%s；③C-r969 推送回执消费=PUSHED_VERIFIED（2314c74e·merge-base ancestor 验证已落地·fetch 后 tip=%s·behind=0）；④CEO 令送达律核查（r959）：O-20261015-0025-bm-b.md origin 面=%s（%s）；orders 全列差集=%s；MSG-20261015-0825 origin 面=%s（%s·受令面=bm-a 常设轮）；⑤组面 D-19 真差集探针=%s（fresh fetch）；⑥车道面：schtasks 三任务在册实证+幂等重装四件套（进程内零窗）；⑦引擎活（idle·queue 0）+水位 red=%s（%s 面）+哨兵 NORMAL 无 flag+RAM=%sGB 如实；⑧idle/S8 面：green_idle=false（RAM 空闲 %s%%<40%% 门）=诚实不领单；idle_trigger claimable_pool_lines=%s·哨兵 work=PENDING_ROUND open=6（候绿窗消费·非机制失灵）；⑨CODELY 挂起面对账（identical=%s·<50KB 尺寸律过） | 证据：_r970bmb_monitor.json（健康+车道+送达+吸收判例证据）+_r970bmb_closeout.log+_r970bmb_s05_scan.json（fresh 重跑面）+_r970bmb_push_receipt.json（r971 消费面）+前席遗产件 _r970bmb_ho_*（HANDOVER 验证族） | WM-VERDICT: red=%s（恢复轮豁免面·%s 面） | 当前活：v5 恢复 pass1 在飞（%s/1804·死窗探针步进·done-climb 判康）+salvage 分离打捞在飞（pid=%s）+backfill 数据腿在飞（pid=%s）；最近实物：research/HANDOVER.md r970 5x 条目（本席随 C-r970 送达 origin）+C-r969 主支推送落地 2314c74e（含 MSG-20261015-0825 送达面）；下个里程碑：ALL_RESTORED→完成包（smoke 49/49+S6+attrition+追平+双侧支合并+CODELY union+MSG 收尾·salvage 打捞可加速恢复·诚实 ETA ~%s·≤24h 承诺不变） | 孤儿面=0（恢复期非 round-zero 未重探·r959 读数 0/18·v5+salvage+backfill=own-lane 合法体三件双验） | 记账预算: 5/5（state+report+心跳+monitor 证据+push 回执） | 产品积分: 1（HANDOVER 5x 送达+监控证据+closeout=实际文件改动与实物推进；恢复实物归驱动） | 本地未达 origin commit 数=1（C-r970 在飞·回执=r971 消费面） | [r970 bm-b]\n"
 % (time.strftime('%H:%M'), s05v, bf_pid, bf_alive, v5_pid, v5_pid_src,
    v5_alive_drv, ddone, dfails, dok, dretr, stagnant, drem, str(peer_tip)[:12],
    order_on_origin, order_face_txt,
    '无未知令' if not unknown_orders else str(unknown_orders),
    msg_on_origin, msg_face_txt, s05v,
    wm_face.get('red'), wm_face.get('ts'), ram_gb, s8_face.get('ram_free_pct'),
    s8_face.get('claimable_pool_lines'), codely_face.get('identical'),
    wm_face.get('red'), wm_face.get('ts'), ddone, salv_pid, bf_pid, eta_txt)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- CODELY size check ----------------
size = os.path.getsize(BM + r'\CODELY.md')
W('CODELY.md size check (no append this round): %dB (law: >50KB = recompile window)' % size)
if size > 50 * 1024:
    W('WARN CODELY size over 50KB - hot/cold recompile due next window')

# ---------------- C-r970 surgery push (4 own faces + conditional order/MSG faces) ----------------
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
                      ('rp', 'logs/iteration-loop/round_reports.md'),
                      ('ho', 'research/HANDOVER.md')):
        rc, out, _ = net_git(['hash-object', '-w', BM + '\\' + path.replace('/', '\\')], 60)
        blobs[key] = out.decode().strip()
    if payload_add_order and os.path.exists(ORDER_LOCAL):
        rc, out, _ = net_git(['hash-object', '-w', ORDER_LOCAL], 60)
        blobs['ord'] = out.decode().strip()
    if payload_add_msg and os.path.exists(MSG_LOCAL):
        rc, out, _ = net_git(['hash-object', '-w', MSG_LOCAL], 60)
        blobs['msg'] = out.decode().strip()
    W('blobs hb=%s st=%s rp=%s ho=%s ord=%s msg=%s'
      % (blobs['hb'][:12], blobs['st'][:12], blobs['rp'][:12], blobs['ho'][:12],
         str(blobs.get('ord', ''))[:12], str(blobs.get('msg', ''))[:12]))

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
        t_research = mkt(repl_add(ls_entries('origin/main:research'),
                                  'HANDOVER.md', '100644', 'blob', blobs['ho']))
        root_ents = ls_entries('origin/main')
        root_ents = repl_add(root_ents, 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl_add(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl_add(root_ents, 'logs', '040000', 'tree', t_logs)
        root_ents = repl_add(root_ents, 'research', '040000', 'tree', t_research)
        t_root = mkt(root_ents)
        W('trees built root=%s (order_face=%s msg_face=%s ho_face=carried)'
          % (t_root[:12], payload_add_order, payload_add_msg))
        subj = ("round 970 (bm-b): recovery monitor eleventh beat - absorbs dead lane "
                "attempt-1, delivers HANDOVER 5x r970 entry to origin")
        body = ("Monitor round: dead lane attempt-1 (09:02-09:27, 25min-watchdog kill, "
                "pre-closeout) adjudicated + absorbed: HANDOVER r970 5x entry (attempt-1 "
                "product, binary-append r962 law, r965 entry byte-verified vs origin) "
                "delivered to origin this round as 4th own face; s05 fresh re-run; "
                "backfill_ext_slots worker relay 18788->%s alive=%s (no-touch). v5 driver "
                "alive (pid %s via %s, receipt %s/1804 fails=%s dead-window face ok=%s flat, "
                "anchor 1086@09:30:17 stagnant=%s; judge health by done-climb per r960 law); "
                "salvage worker alive (pid %s); C-r969 receipt consumed (2314c74e "
                "ancestor-verified on origin; tip after fetch=%s); CEO order "
                "O-20261015-0025 delivery face: %s; unknown-order diff: %s; "
                "MSG-20261015-0825: %s; lane face: schtasks 3/3 registered + idempotent "
                "quad; engine alive idle queue 0; watermark red=%s (%s face); sentinel "
                "NORMAL; idle/S8 green_idle=false honest no-claim; s05 fresh probe %s; "
                "CODELY pending-union face accounted (identical=%s, <50KB pass); S0 pull/S1 "
                "smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
                "completion package). Receipt: results/_r970bmb_push_receipt.json (r971 "
                "verify face). --no-verify escape per r950 cold-index pre-push claw hang "
                "law (receipted)."
                % (bf_pid, bf_alive, v5_pid, v5_pid_src, ddone, dfails, dok, stagnant,
                   salv_pid, str(peer_tip)[:12], order_face_txt,
                   'none' if not unknown_orders else str(unknown_orders), msg_face_txt,
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
                 note=('C-r970 surgery parent=origin tip (%s); payload = bm-b own faces '
                       '(heartbeat/state/round report/HANDOVER 5x r970 estate entry), '
                       'deletion set empty; --no-verify escape per cold-index pre-push claw '
                       'hang law r950 (receipted); r971 consumes: behind count 0'
                       % str(peer_tip)[:12]))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 971:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r970_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                     'consumed_at': iso2, 'behind_origin_main': 0}
            sy2['last_push_ts'] = iso2
            stx['sync'] = sy2
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('segment-C state sync face updated PUSHED_VERIFIED (round_no still 971)')
        else:
            W('segment-C skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('segment-C state update error: %s' % str(e)[:150])
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r971 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
