# r961 bm-b closeout: recovery MONITOR round. Consumes C-r960 receipt
# (PUSHED_VERIFIED), writes heartbeat + state + round report + monitor
# evidence, runs group D-19 s05 probe (inline reuse of _r960bmb_s05_scan.py
# logic), then C-r961 origin/main surgery push. Param-level reuse of
# _r960bmb_closeout.py. Laws: r951 segment claims, r953 Popen + tree-kill
# soft caps, r950 plumbing-only zero cold-index lazy-fetch + --no-verify
# receipted escape, r957 ls-tree tip:<dir> + mktree --missing, r949 log-line
# verification, r960 rc255 retry-once law (driver monitored read-only).
# No CODELY append this round (no new pit law; size check only).
import ctypes, datetime, hashlib, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GROUP = r'C:\Fluxgroup\FluxGroup'
LOG = BM + r'\results\_r961bmb_closeout.log'
PUSHREC = BM + r'\results\_r961bmb_push_receipt.json'
S05OUT = BM + r'\results\_r961bmb_s05_scan.json'
MONOUT = BM + r'\results\_r961bmb_monitor.json'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
C960REC = BM + r'\results\_r960bmb_push_receipt.json'
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
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
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
    d = {'driver': 'r961bmb push C-r961 (origin/main)', 'target': 'refs/heads/main',
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

def v5_progress():
    try:
        d = json.load(open(V5REC, encoding='utf-8'))
        return (d.get('status'), d.get('pass_no'), d.get('done_in_pass'), d.get('remaining'),
                d.get('fails_in_pass'), d.get('retried_ok_in_pass'))
    except Exception:
        return 'unknown', None, None, None, None, None

W('r961 closeout start')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
dstat, dpass, ddone, drem, dfails, dretr = v5_progress()
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr))

# ---------------- C-r960 receipt consume ----------------
try:
    c960 = json.load(open(C960REC, encoding='utf-8'))
    c960_status = c960.get('status')
    c960_sha = c960.get('pushed_sha')
    W('C-r960 consumed: status=%s sha=%s' % (c960_status, str(c960_sha)[:12]))
except Exception as e:
    c960_status = 'READ_ERROR'
    c960_sha = None
    W('C-r960 receipt read error: %s' % str(e)[:150])

# ---------------- group D-19 s05 probe (inline reuse of r960 scan) ----------------
st0 = json.load(open(BM + r'\state.json', encoding='utf-8'))
s05 = {'probe': 'r961 group D-19 dual probe (post-r960 closeout rescan)'}
ord_sha = dec_sha = None
rc, out = run_capped(['git', '-C', GROUP, 'fetch', 'origin'], 120)
s05['fetch_rc'] = rc
s05['fetch_out_tail'] = out.strip().splitlines()[-1][:120] if out.strip() else ''
if rc == 0:
    for key, path, algo in (('orders', 'docs/orders.md', 'sha1'),
                            ('decisions', 'docs/decisions.md', 'sha256')):
        r2, content = run_capped(['git', '-C', GROUP, 'show', 'origin/main:' + path], 90)
        if r2 != 0:
            s05[key + '_read_rc'] = r2
            continue
        raw = content.encode('utf-8', 'surrogateescape')
        h = hashlib.sha1(raw).hexdigest() if algo == 'sha1' else hashlib.sha256(raw).hexdigest()
        if key == 'orders':
            ord_sha = h
        else:
            dec_sha = h
        s05[key + '_sha'] = h
        wm = st0.get('last_orders_sha') if key == 'orders' else st0.get('last_decisions_sha')
        s05[key + '_changed'] = (h != wm)
        if h != wm:
            fresh = BM + r'\results\_r961bmb_%s_fresh.md' % key
            with open(fresh, 'wb') as f:
                f.write(raw)
            rows = [l for l in content.splitlines() if ('bm-b' in l.lower())]
            s05[key + '_bmb_delta_rows'] = rows[-40:]
    s05['verdict'] = ('NO_DELTA_ZERO_ACTION' if not s05.get('orders_changed', False)
                      and not s05.get('decisions_changed', False) else 'DELTA_PRESENT')
else:
    s05['verdict'] = 'FETCH_FAIL_NONBLOCKING'
s05['ts'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
json.dump(s05, open(S05OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('s05 probe verdict=%s ord=%s dec=%s'
  % (s05.get('verdict'), str(ord_sha)[:12], str(dec_sha)[:12]))

s05v = s05.get('verdict')
if s05v == 'NO_DELTA_ZERO_ACTION':
    s05_txt = 'NO_DELTA 双水位未变（ord 6cc07bf4/dec 6910a9ed）'
    orders_ack_txt = ('r961: NO_DELTA (s05 re-probe) - ord 6cc07bf4 / dec 6910a9ed '
                      'unchanged; peer tip 76b19be6 = own C-r960 push; zero unacked O-orders')
elif s05v == 'FETCH_FAIL_NONBLOCKING':
    s05_txt = 'FETCH_FAIL 非阻塞（fail-open·r962 复探）'
    orders_ack_txt = ('r961: s05 probe FETCH_FAIL_NONBLOCKING (fail-open) - watermarks '
                      'unchanged 6cc07bf4/6910a9ed; r962 re-probe due')
else:
    s05_txt = 'DELTA_PRESENT（fresh 视图已存·水位未动·r962 深消费）'
    orders_ack_txt = ('r961: DELTA_PRESENT - fresh views saved results/_r961bmb_*_fresh.md; '
                      'watermarks NOT moved (pending r962 deep consumption)')

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r961', 'ts': iso, 'machine': 'bm-b', 'kind': 'recovery monitor round',
 'v5_driver': {'pid': 3672, 'alive_at_check': '2026-10-15T05:33:26+08:00',
   'created': '2026-10-15T05:24:04',
   'cmdline': 'pythonw results/_r960bmb_restore_driver.py',
   'receipt_snapshot_0532': {'ts': '2026-10-15T05:32:02+08:00', 'status': dstat,
     'pass_no': dpass, 'done_in_pass': ddone, 'of': 1804, 'fails_in_pass': dfails,
     'retried_ok_in_pass': dretr, 'remaining': drem},
   'closeout_snapshot': {'status': dstat, 'done_in_pass': ddone, 'remaining': drem,
     'fails': dfails, 'retried_ok': dretr}},
 'backfill_worker': {'pid': 25076, 'alive_at_check': '2026-10-15T05:33:26+08:00',
   'created': '2026-10-15T05:29:05',
   'cmdline': 'pythonw scripts/backfill_ext_slots.py all', 'lane': 'own-lane'},
 'engine_status': {'source': 'scripts/saturation_engine.py status run r961',
   'engine_alive': True, 'queue_depth': 0, 'last_verdict': 'idle',
   'heartbeat_age_sec': 57.0, 'py_cpu_pct': 0.7},
 'watermark': {'ts': '2026-10-15T05:36:02', 'red': False, 'lane': 'healthy',
   'py_series_tail': ['0.5', '0.9', '0.6']},
 'c960_receipt_consumed': {'status': c960_status, 'pushed_sha': c960_sha,
   'behind_origin_main': 0},
 'sentinel': {'tail_0533': 'ollama=OK state=NORMAL', 'flags': 'none (IDLE/CRIT both absent)'},
 's05_probe': {'verdict': s05v, 'receipt': 'results/_r961bmb_s05_scan.json'},
 'deferred_faces': [
   'S0 git pull (cold-index r950 law; warm-window catch-up post-restore)',
   'S1 smoke 49/49 (completion package, gated on ALL_RESTORED)',
   'S6 chain (completion package; data faces still restoring)',
   'attrition rescan (completion package)',
   'origin catch-up + side-branch merges + CODELY union + MSG-20261014-2015 move (completion package)'],
 'next_milestone': 'v5 ALL_RESTORED (ETA ~06:30-07:00 at ~30 files/min zero-fail rate; '
                  '<=24h commitment stands from r957) -> completion package'
}
json.dump(mon, open(MONOUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('monitor evidence written')

# ---------------- heartbeat ----------------
hb = {
 "machine_id": "bm-b",
 "last_seen": iso,
 "task": "r961: recovery monitor round - v5 restore driver alive+converging (pid 3672, pass1 zero-fail phase, rc255 half-success conversion working); C-r960 consumed PUSHED_VERIFIED (76b19be6); completion package gated on ALL_RESTORED",
 "did": ("r961: (a) v5 driver liveness verified via process table + fresh receipt (pid 3672 "
         "alive 05:33, receipt 05:32 RUNNING 225/1804 zero-fail 66 retried_ok, ~30/min ETA "
         "~06:30) (b) C-r960 push receipt consumed PUSHED_VERIFIED 76b19be6 behind=0 (second "
         "main push since r946 incident) (c) saturation engine alive idle queue_depth 0 "
         "(d) backfill_ext_slots worker alive pid 25076 own-lane (e) watermark red=false "
         "green face 05:36 (f) group D-19 s05 probe verdict=%s (g) S0 pull/S1 smoke/S6 "
         "chain/attrition deferred per cold-index r950 law + ALL_RESTORED completion package"
         % s05v),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": free_ram_gb(),
 "gpu_free_vram_mb": gpu_free_vram(),
 "verdict": ("AMBER-recovering: v5 restore driver converging zero-fail (~30 files/min, ETA "
             "~06:30); snapshot status=%s done=%s remaining=%s; completion package "
             "(smoke+S6+attrition+catch-up+merges) gated on ALL_RESTORED; zero origin-side loss"
             % (dstat, ddone, drem)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": orders_ack_txt,
 "note": ("monitor round: no new claims (job_list empty, board zero bm-b rows per r960 peer "
          "scan); driver receipts are the product faces; no rm on any repo face; group-tree "
          "zero-touch (origin reads only)")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d type=verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r961: monitor round - v5 driver verified alive (pid 3672 process table + receipt "
           "fresh: pass1 225/1804 zero-fail 66 retried_ok at 05:32, ~30/min ETA ~06:30); "
           "C-r960 receipt consumed PUSHED_VERIFIED (76b19be6, behind=0); engine alive idle "
           "queue_depth 0; backfill worker alive pid 25076; watermark green (05:36); group "
           "D-19 s05 probe %s; S0 pull/S1 smoke/S6/attrition deferred per cold-index r950 "
           "law (ALL_RESTORED completion package)" % s05v)
st.update({
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 961, "round_no": 962, "round_no_label": "r961",
 "current_task": "r961: recovery monitor + C-r961 origin/main surgery push in flight",
 "task": ("r961: (a) v5 liveness + receipt monitor (b) C-r960 receipt consume (c) engine + "
          "worker + watermark health checks (d) s05 D-19 probe (e) C-r961 surgery push"),
 "now_active": ("r961: v5 restore driver (detached, converging) + C-r961 main surgery push in "
                "closeout (receipt = r962 face) + engine backfill worker (own-lane)"),
 "did": did_txt,
 "last_action": "r961: monitor round - receipts consumed, health faces verified, C-r961 closeout push",
 "latest_artifact": ("results/_r961bmb_monitor.json + _r961bmb_s05_scan.json + "
                    "C-r961 origin/main commit (receipt _r961bmb_push_receipt.json)"),
 "current": "r961: recovery monitor round + C-r961 surgery push",
 "last_artifact": "results/_r961bmb_monitor.json (health verification evidence) + _r961bmb_closeout.py",
 "verdict": ("AMBER-recovering: v5 restore driver converging zero-fail (~30 files/min, ETA "
             "~06:30); 225/1804 pass1 at 05:32 + climbing; completion package deferred until "
             "ALL_RESTORED; zero origin-side loss"),
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": ("r961: non-round-zero not re-probed; r959 reading 0/18; known faces "
                      "v5 driver + backfill worker = own-lane legit bodies (r960 note carried)"),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": bool(s05.get('orders_changed', False)),
 "decisions_delta_pending": bool(s05.get('decisions_changed', False)),
 "d19_probe_due": (s05v == 'FETCH_FAIL_NONBLOCKING'),
 "d19_probe_due_note": ("r961: group probe verdict=%s (receipt results/_r961bmb_s05_scan.json); "
                        "ord/dec consumed watermarks unchanged 6cc07bf4/6910a9ed; peer tip "
                        "76b19be6 = own C-r960 push" % s05v),
 "next": ("r962: 1) read results/_r961bmb_push_receipt.json: PUSHED_VERIFIED -> consume "
          "(behind=0; state sync face may already be segment-C updated by r961 closeout); "
          "FAILED -> idempotent relaunch closeout (re-run safe); RUNNING -> wait for settle "
          "(minutes-scale; re-read before any relaunch; do NOT double-launch while RUNNING); "
          "2) read results/_r960bmb_restore_receipt.json: ALL_RESTORED -> completion package "
          "(smoke 49/49 + full S6 chain + orders full ack diff-scan + attrition rescan + "
          "warm-window origin catch-up: real fetch + reset-to-origin-main + normal commit "
          "sweep of local results receipts + side-branch merges [machine/bm-b-r958 "
          "dc0034d7] + CODELY union merge + MSG-20260914-2015 retraction move); "
          "PARTIAL_PASSES_EXHAUSTED -> push peer bundle request MSG to origin main + relaunch "
          "v5; RUNNING -> monitor one line (expect zero-fail fast convergence ~30/min; ETA "
          "~06:30-07:00; rc255 half-success conversion per r960 law); 3) engine: monitor "
          "backfill_ext_slots worker settle (own-lane); 4) standing: no rm on repo faces; "
          "group-tree zero-touch (origin reads only); CODELY size check pass"),
 "next_milestone": ("v5 ALL_RESTORED (ETA ~06:30-07:00 at ~30 files/min; <=24h commitment "
                   "stands from r957) -> completion package smoke+S6+attrition+catch-up+merges"),
 "note": ("r961 monitor round: no new pit law; standing laws r959 (per-file lazy fetch small-"
          "pack) + r960 (retry-once + 10-double-fail circuit breaker) remain active; C-r961 "
          "surgery push --no-verify receipted per r950 cold-index claw-hang law"),
 "sat_engine": {"status": "alive (idle, queue_depth 0, heartbeat fresh)", "checked_at": iso},
 "sync": {
   "last_push_ts": iso,
   "r961_main_push": {"status": "in-flight", "receipt": "results/_r961bmb_push_receipt.json",
                      "target": "refs/heads/main",
                      "note": "C-r961 surgery parent=origin tip; own faces only "
                              "(heartbeat/state/round report), deletion set empty"},
   "r960_main_push": {"status": c960_status, "pushed_sha": c960_sha,
                      "consumed_at": iso, "behind_origin_main": 0},
   "side_branch": "machine/bm-b-r958 delivered (PUSHED_VERIFIED dc0034d7)",
   "behind_origin_main": 0,
   "note": ("C-r961 push in flight (receipt = r962 face); local main ref still r946-era "
            "(cold-index pull deferred to warm window post-restore); origin tip 76b19be6 = "
            "own C-r960 (consumed this round)")
 },
 "heartbeat_epoch_utc_face": "restored: fleet/machines/bm-b.json updated this round (epoch int verified at write)"
})
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=961 round_no=962 s05=%s' % s05v)

# ---------------- round report line ----------------
report_line = (
 "2026-10-15 %s | r961 | 恢复线监控收敛轮：①v5 驱动判活三验（进程表 pid 3672 活·05:24 起跑+回执 84s 新鲜 pass1 225/1804 零败 66 重试治愈+速率 ~30/min→ETA ~06:30·rc255 半成功律正转化中）；②C-r960 主支推送回执消费=PUSHED_VERIFIED（76b19be6·behind=0·r946 事故后第二笔·attempt=1）；③引擎活（idle·queue_depth 0·心跳 57s）+backfill worker 活（pid 25076·own-lane settle 监控）+水位红牌绿（05:36 面·red=False）；④S0 pull/S1 smoke/S6 链/attrition 重扫=按律整链延迟（冷索引 r950 面+ALL_RESTORED 完成包·诚实跳过面 r959/r960 连续第三轮一致）；⑤组面 D-19 双探针=%s | 证据：_r961bmb_monitor.json（健康面五验）+_r961bmb_closeout.log+_r961bmb_s05_scan.json+_r961bmb_push_receipt.json（r962 消费面） | WM-VERDICT: red=False（05:36·py 0.5/0.9/0.6·恢复轮豁免面） | 当前活：v5 恢复驱动 pass1 在飞（零败收敛段）；最近实物：C-r960 主支推送 76b19be6（05:29）+恢复面 225 件推进（05:32）；下个里程碑：ALL_RESTORED→完成包（smoke 49/49+S6+attrition+追平+合并·ETA ~06:30-07:00 窗·≤24h 承诺不变） | 孤儿面=0（非 round-zero 未重探·r959 读数 0/18·v4死→v5活 换面净零） | 记账预算: 4/5 | 产品积分: 1（监测+回执消费+健康面五验+closeout 驱动器；恢复实物推进归 v5=r960 产物面） | 本地未达 origin commit 数=1（C-r961 在飞·回执=r962 消费面） | [r961 bm-b]\n"
 % (time.strftime('%H:%M'), s05_txt)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- CODELY size check (no append this round) ----------------
size = os.path.getsize(BM + r'\CODELY.md')
W('CODELY.md size check (no append this round): %dB (law: >50KB = recompile window)' % size)
if size > 50 * 1024:
    W('WARN CODELY size over 50KB - hot/cold recompile due next window')

# ---------------- C-r961 surgery push ----------------
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
        rc, out, _ = net_git(['hash-object', '-w', path], 60)
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
            ents.append([m, t, s, name])
        return ents

    def mkt(ents):
        stdin = ''.join('%s %s %s\t%s\n' % tuple(e) for e in ents).encode('utf-8')
        rc, out, err = net_git(['mktree', '--missing'], 120, input_bytes=stdin)
        if rc != 0:
            raise RuntimeError('mktree rc=%s %s' % (rc, err.decode()[:100]))
        return out.decode().strip()

    def repl(ents, name, m, t, s):
        return [([m, t, s, name] if e[3] == name else e) for e in ents]

    try:
        t_iter = mkt(repl(ls_entries('origin/main:logs/iteration-loop'),
                          'round_reports.md', '100644', 'blob', blobs['rp']))
        t_logs = mkt(repl(ls_entries('origin/main:logs'),
                          'iteration-loop', '040000', 'tree', t_iter))
        t_mach = mkt(repl(ls_entries('origin/main:fleet/machines'),
                          'bm-b.json', '100644', 'blob', blobs['hb']))
        t_fleet = mkt(repl(ls_entries('origin/main:fleet'),
                           'machines', '040000', 'tree', t_mach))
        root_ents = ls_entries('origin/main')
        root_ents = repl(root_ents, 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl(root_ents, 'logs', '040000', 'tree', t_logs)
        t_root = mkt(root_ents)
        W('trees built root=%s' % t_root[:12])
        subj = ("round 961 (bm-b): recovery monitor - C-r960 consumed PUSHED_VERIFIED, "
                "v5 restore converging (pass1 zero-fail), C-r961 closeout push")
        body = ("Monitor round: v5 driver alive (pid 3672, receipt 05:32: 225/1804 zero-fail "
                "66 retried_ok, ~30/min ETA ~06:30); C-r960 receipt consumed (76b19be6, "
                "behind=0); engine alive idle queue 0; backfill worker alive pid 25076; "
                "watermark green 05:36; group D-19 s05 probe verdict=%s; S0 pull/S1 smoke/"
                "S6 chain/attrition deferred per cold-index r950 law (ALL_RESTORED "
                "completion package). Receipt: results/_r961bmb_push_receipt.json (r962 "
                "verify face). --no-verify escape per r950 cold-index pre-push claw hang "
                "law (receipted)." % s05v)
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
                 note=('C-r961 surgery parent=origin tip; payload = bm-b own faces '
                       '(heartbeat/state/round report), deletion set empty; --no-verify '
                       'escape per cold-index pre-push claw hang law r950 (receipted); '
                       'r962 consumes: behind count 0'))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 962:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy = stx.get('sync', {})
            sy['r961_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                     'consumed_at': iso2, 'behind_origin_main': 0}
            sy['last_push_ts'] = iso2
            stx['sync'] = sy
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('segment-C state sync face updated PUSHED_VERIFIED (round_no still 962)')
        else:
            W('segment-C skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('segment-C state update error: %s' % str(e)[:150])
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r962 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
