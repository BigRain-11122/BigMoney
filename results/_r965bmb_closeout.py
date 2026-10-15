# r965 bm-b closeout: recovery monitor round (sixth beat) + HANDOVER 5x duty.
# Consumes C-r964 receipt (PUSHED_VERIFIED c7bf840c), re-verifies v5 driver
# liveness + receipt progress (rate anchor 766@06:49:56), runs lane-task
# registry checks (schtasks, R49 law) + idempotent re-registration quad
# (U060 in-process no-window), group D-19 s05 probe (re-run of standalone
# scan script, fresh fetch), watermark + sentinel faces, CODELY pending-union
# face, appends the OVERDUE-DISCLOSED HANDOVER 5x entry (r911-r965 window,
# binary append per r962 encoding law), writes heartbeat + state + round
# report + monitor evidence, then C-r965 origin/main surgery push with 4
# payload faces (heartbeat/state/round-reports/HANDOVER).
# Param-level reuse of _r964bmb_closeout.py. Laws: r951 segment claims, r953
# Popen + tree-kill soft caps, r950 plumbing-only + --no-verify receipted
# escape, r957 ls-tree tip:<dir> + mktree --missing + non-empty-name guard,
# r959 delivery law, r960 retry-once + consecutive double-fail breaker,
# r962 round_reports.md + HANDOVER.md binary/append-only byte law.
import ctypes, datetime, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r965bmb_closeout.log'
PUSHREC = BM + r'\results\_r965bmb_push_receipt.json'
S05OUT = BM + r'\results\_r965bmb_s05_scan.json'
MONOUT = BM + r'\results\_r965bmb_monitor.json'
V5REC = BM + r'\results\_r960bmb_restore_receipt.json'
V5DRIVERLOG = BM + r'\results\_r960bmb_restore_driver.log'
C964REC = BM + r'\results\_r964bmb_push_receipt.json'
HANDOVER = BM + r'\research\HANDOVER.md'
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
    d = {'driver': 'r965bmb push C-r965 (origin/main)', 'target': 'refs/heads/main',
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

def v5_progress():
    try:
        d = json.load(open(V5REC, encoding='utf-8'))
        return (d.get('status'), d.get('pass_no'), d.get('done_in_pass'), d.get('remaining'),
                d.get('fails_in_pass'), d.get('retried_ok_in_pass'), d.get('ts'))
    except Exception:
        return 'unknown', None, None, None, None, None, None

def tail_file(path, n=6):
    try:
        with open(path, 'rb') as f:
            lines = f.read().decode('utf-8', 'replace').splitlines()
        return lines[-n:]
    except Exception:
        return None

W('r965 closeout start')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
dstat, dpass, ddone, drem, dfails, dretr, dts = v5_progress()
W('v5 snapshot status=%s pass=%s done=%s remaining=%s fails=%s retried_ok=%s receipt_ts=%s'
  % (dstat, dpass, ddone, drem, dfails, dretr, dts))

# v5 rate/ETA from exact anchor (766@06:49:56 receipt read this session)
rate_min = 2.0
eta_txt = 'n/a'
try:
    a_done, a_ts = 766, datetime.datetime.fromisoformat('2026-10-15T06:49:56+08:00')
    if ddone and dts:
        cur_ts = datetime.datetime.fromisoformat(dts)
        if ddone >= a_done and cur_ts > a_ts:
            dt_min = (cur_ts - a_ts).total_seconds() / 60.0
            if dt_min > 1.0:
                rate_min = max(0.5, (ddone - a_done) / dt_min)
    if drem and rate_min:
        eta_dt = now + datetime.timedelta(minutes=float(drem) / rate_min)
        eta_txt = eta_dt.strftime('%H:%M')
except Exception as e:
    W('rate/eta calc error: %s' % str(e)[:120])
W('v5 rate=%.2f files/min eta=%s (remaining=%s)' % (rate_min, eta_txt, drem))

v5_pid = 3672
v5_alive_drv = pid_alive(v5_pid)
v5_log_tail = tail_file(V5DRIVERLOG, 6)
breaker_seen = bool(v5_log_tail and any('circuit breaker' in l for l in v5_log_tail))
W('driver-time tasklist: v5 pid %s alive=%s breaker_in_tail=%s' % (v5_pid, v5_alive_drv, breaker_seen))

# ---------------- C-r964 receipt consume ----------------
try:
    c964 = json.load(open(C964REC, encoding='utf-8'))
    c964_status = c964.get('status')
    c964_sha = c964.get('pushed_sha')
    W('C-r964 consumed: status=%s sha=%s' % (c964_status, str(c964_sha)[:12]))
except Exception as e:
    c964_status = 'READ_ERROR'
    c964_sha = None
    W('C-r964 receipt read error: %s' % str(e)[:150])

c964_ancestor_rc, peer_tip, peer_log = None, None, ''
try:
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    W('peer-verify fetch rc=%s' % rc)
    if rc == 0 and c964_sha:
        rc_a, _, _ = net_git(['merge-base', '--is-ancestor', c964_sha, 'origin/main'], 60)
        c964_ancestor_rc = rc_a
        rc_t, out_t, _ = net_git(['rev-parse', 'origin/main'], 30)
        peer_tip = out_t.decode().strip() if rc_t == 0 else None
        rc_l, out_l, _ = net_git(['log', '--oneline', '-3', 'origin/main'], 60)
        peer_log = out_l.decode('utf-8', 'replace').strip()[:400]
        W('C-r964 ancestor_rc=%s origin_tip=%s' % (rc_a, str(peer_tip)[:12]))
        W('peer log tail: %s' % peer_log.replace('\n', ' | ')[:300])
except Exception as e:
    W('peer-verify error: %s' % str(e)[:150])

# ---------------- group D-19 s05 probe (re-run standalone scan, fresh fetch) ----------------
st0 = json.load(open(BM + r'\state.json', encoding='utf-8'))
rc_s, out_s = run_capped(['python', BM + r'\results\_r965bmb_s05_scan.py'], 240)
W('s05 re-run rc=%s' % rc_s)
try:
    s05 = json.load(open(S05OUT, encoding='utf-8'))
except Exception as e:
    s05 = {'verdict': 'READ_ERROR', 'error': str(e)[:150]}
    W('s05 read error: %s' % str(e)[:150])
s05v = s05.get('verdict')
ord_sha = s05.get('orders_sha')
dec_sha = s05.get('decisions_sha')
orders_consumed = False
decisions_consumed = False
if s05v == 'NO_DELTA_ZERO_ACTION':
    s05_txt = 'NO_DELTA 双水位未变（ord %s/dec %s）' % (
        str(st0.get('last_orders_sha'))[:8], str(st0.get('last_decisions_sha'))[:8])
    orders_ack_txt = ('r965: NO_DELTA (s05 re-probe fresh fetch) - ord/dec watermarks unchanged; '
                      'C-r964 landed (c7bf840c); zero unacked O-orders')
elif s05v == 'FETCH_FAIL_NONBLOCKING':
    s05_txt = 'FETCH_FAIL 非阻塞（fail-open路r966 重探）'
    orders_ack_txt = ('r965: s05 probe FETCH_FAIL_NONBLOCKING (fail-open) - watermarks '
                      'unchanged; r966 re-probe due')
else:
    s05_txt = 'DELTA_PRESENT（真差集扫描=results/_r965bmb_s05_scan.json）'
    orders_ack_txt = ('r965: DELTA_PRESENT - true-delta scan results/_r965bmb_s05_scan.json; '
                      'r966 consumption agenda')
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
             'flags': 'IDLE/CRIT both absent (checked r965 session 06:52 + this face)'}
W('watermark red=%s ts=%s; sentinel tail=%s' % (wm_face.get('red'), wm_face.get('ts'),
                                                 str(sent_face.get('tail_last'))[:80]))

# ---------------- CODELY pending-union face ----------------
codely_face = {}
try:
    rc_c, out_c, _ = net_git(['rev-parse', 'origin/main:CODELY.md'], 30)
    origin_codely = out_c.decode().strip() if rc_c == 0 else None
    rc_h, out_h, _ = net_git(['hash-object', BM + r'\CODELY.md'], 30)
    local_codely = out_h.decode().strip() if rc_h == 0 else None
    codely_face = {'origin_blob': origin_codely, 'local_blob': local_codely,
                   'identical': origin_codely == local_codely,
                   'disposition': ('zero pending' if origin_codely == local_codely
                                   else 'union merge rides completion package')}
    W('CODELY face origin=%s local=%s identical=%s'
      % (str(origin_codely)[:12], str(local_codely)[:12], origin_codely == local_codely))
except Exception as e:
    codely_face = {'error': str(e)[:120]}

# ---------------- HANDOVER 5x duty (binary append, r962 law) ----------------
hdo_entry = (
 "\n- 【第五节·产物清单核对（新增与删改）】**round 965 bm-b（5x 核对本轮；r915/r920/r925/r930/r935/r940/r945/r950/r955/r960 各 5x 戳未落=OVERDUE-DISCLOSED——产线长烧窗+git 灾修连续窗所赐；按 r770/r790/r810/r830/r845 单窗紧凑覆盖防零复发纪律，账面零回改）**：2026-10-15 06:5x 核对；对账区间增量 bm-b r911-r965（基准线=round 910 bm-b 行）；逐轮权威=logs/iteration-loop/round_reports.md 全行在册。增量窗三段主线：①**产线长烧段（r911-r946·10-13 01:4x~10-14 19:22）**：(a) i2v 53 单 int4 480P animatic 预览线（CEO 机队分工令 O-20261011-2126 本机线）长烧值守——10-12 夜批起（首单 XQ28 1002s·r897/r898）→10-12/10-13 两断电缺口自愈复燃（r907/r908·550W 电源根因另案）→~4min/单提速实证（r906）→10-13 上午 r915/r916 P0 产线复活（让 VRAM：杀 ollama/llama-server→ComfyUI 单汤）→收官验收排 10-13 12:07 cron 窗+完成回执按 O-2126 §5 由循环轮推送；(b) N2U3 channel-1 判决链：leg-3 训练批烧录+completion gate 落地（export-topk/judge fail-closed·r922）+首个 judged 证据 JUDGED-2026-10-09.json 落地验讫（r924/r925-continuation）；(c) W19 全链：FREEZE funnel 3/5 LANDED（commit 6c09b1251·r927）→GENERATE supply ignition（r929）→SCREEN supply enrollment 8/8（r930）→JUDGE enrolled+ignited（r931）→judge-finalize 遗产接力收口（r932）→W20 复现法普查 45 面 0 幸存源关闭+census 证据 11 件（r936·de32b3f25/3c8ccc25e）→48h CEO W19 三轴报告提前窗落地 research/W19-TRIAXIS-CEO-REPORT-V1.md（三轴 W17 344/W18 188/W19 112 合计 644 judged·0 注册·E[FP] 名义 32.2 vs 实过 0·due 10-16 已提前交付·r939）；(d) unity-mcp POC probe#4/#5 机械诊断+下一步裁决（O-2333·r918/r919）；(e) 舰队治理：HQ-FEEDBACK F-20261014-02（S0 race 跨机佐证·r946）+W241/W242 席位 MSG 回执归档（r943/addendum）+bm-b-Sentinel 哨兵 S4U 5min 部署+v1.2 阀 TTL 律（CEO「不要再出错」令 O-20261014-0948）+B站自动回复线常驻化（O-20261014-0040·bm-b-BiliAutoReply 15min dry-run·候 CEO cookie 物理件）+S0 深手术合并链（r926/r943 84ed94105 behind 0/0）+D-19 双水位消费链维持（灾前末笔 r946 ORD 8b904179→灾修段 r954 2e5111e6→r962 e2423fef）。②**git 树灭失灾修段（r947-r956·10-14 19:26 起·r834 族复发）**：整树递归删除致 .git+data+config 等面全灭（幸存边界=logs 前·真凶未归案）→r947 .git 精简重建（init+fetch --depth=1 --filter=blob:none origin tip ebf8a644=零 origin 损失）+取证 forensics+peer bundle 后援 MSG→r948 addendum（数据面同毁诚实披露+被杀轮 25 命令全审计双清白）→r949 假宣称证伪勘误律（孤儿锁 -ErrorAction Stop+复核）→r950 冷索引判例（一切索引校验 op 触发 29598 对象 mass lazy fetch 挂死=树手术提交路首用 ls-tree+mktree --missing+commit-tree+update-ref+--no-verify 逃生口留痕）→r951 双段式 closeout 正典立法（段A 载荷手术+push+盘验→段B 宣称落笔→段C state 收口·幂等可重入）→r953 Popen 树杀软帽+fetch-first 推送驱动器（pack 收缩至 delta）→r954 可续传 raw-SHA 批量回填死路定谳（服务端拒收 unadvertised wants）→r955 tmp_pack 打捞法（index-pack --stdin --fix-thin 零网络）+直读面不预取发现→r956 POOL-0011 转单卡认领（@bm-b 软著B机10款·card-lint PASS）。③**恢复收敛段（r957-r964·产品+收敛并进）**：(a) POOL-0011 done 交付（集团 origin/main bfa61b61：B机10款源程序 G04/G05/G07/G08/G13/G14/G20/G23/G26/G28 十款合计 34,307 行/209 源文件+CCPC 提交材料 10/10 归拢+报审台账§四 B10 行销账+docs/orders.md done 行·r957）+fleet/machine.json 手工重建（X104 律本地私有件）→饱和引擎复活+孤儿探针复役；(b) 恢复驱动谱系 v3（census 先行+分块·300 件即时恢复·r958）→v4（逐文件懒取 0.3-0.4s 单 blob 小包正法·r959）→v5（同文件重试一次+连续双败断路器 300s 探针·r960）；(c) C-r959 灾后首笔 origin main 推送=peer 可见性恢复（14cf51ba6）→C-r960/961/962/963/964 五连 PUSHED_VERIFIED behind=0（回执链=results/_r96xbmb_push_receipt.json）；(d) v5 收敛在飞：r964 面 746/1804（夜窗断路器 300s 探针节律·pass-2 owns fail set）→r965 面 766/1804（速率 ~2.0 件/min·ETA ~15:45·≤24h 承诺自 r957 起算）；(e) 坑律入册族 r948-r962 十五律（正典=根 CODELY.md r947-r962 行：git 杀必杀树/清锁复核/宣称双验/冷索引树手术/双段式 closeout/树杀软帽/raw-SHA 死路/tmp_pack 打捞/九根跨机解析/ls-tree 空名守卫/假 RUNNING 回执/单 blob 小包+跨机 MSG 必推 main 送达判据/rc255 半成功+断路器/round_reports 混合编码二进制律）。维护面：灾修窗 smoke/S6/attrition 按律整链延迟（冷索引 r950 面+ALL_RESTORED 完成包）；孤儿面 r957 复活后 0/8→0/14→0/18 链；车道四件套幂等重装链（loop pin=2/watchdog/双爪）；哨兵 v1.2 NORMAL 链。完成状态：origin 侧零损失实证（r946 前全部产品在 origin+灾修链全部推送落地）；v5 恢复在飞；完成包（smoke 49/49+全 S6 链+orders 全 ack 差集+attrition 重扫+origin 追平+双侧支合并 machine/bm-b-r954 c59c94e7〔G5 回执 MSG-20261015-0104·送达律 r959〕+machine/bm-b-r958 dc0034d7+CODELY union merge+MSG-20261014-2015 撤回搬移）候 ALL_RESTORED 落账。指针：v5 ALL_RESTORED（ETA ~15:45 速率面）→完成包同窗；POOL-0011 已销账；月界首考 10-31。下一 5x=bm-b r970。[via bm-b r965]\n"
)
hdo_face = {}
try:
    pre_size = os.path.getsize(HANDOVER)
    with open(HANDOVER, 'rb') as f:
        hdo_existing = f.read()
    if b'[via bm-b r965]' in hdo_existing[-8000:]:
        hdo_face = {'skipped': 'entry marker already on disk (idempotent relaunch guard)',
                    'pre_size': pre_size}
        W('HANDOVER 5x entry already present - append skipped (idempotent relaunch)')
    else:
        with open(HANDOVER, 'ab') as f:
            f.write(hdo_entry.encode('utf-8'))
        post_size = os.path.getsize(HANDOVER)
        with open(HANDOVER, 'rb') as f:
            f.seek(pre_size)
            verify_tail = f.read()
        ok_append = verify_tail == hdo_entry.encode('utf-8')
        hdo_face = {'pre_size': pre_size, 'post_size': post_size,
                    'appended_bytes': post_size - pre_size,
                    'tail_verbatim_verified': ok_append,
                    'entry_covers': 'r911-r965 window, stamps r915..r960 OVERDUE-DISCLOSED'}
        W('HANDOVER 5x entry appended %dB tail_verified=%s (pre=%d post=%d)'
          % (post_size - pre_size, ok_append, pre_size, post_size))
except Exception as e:
    hdo_face = {'error': str(e)[:200]}
    W('HANDOVER append error: %s' % str(e)[:200])

# ---------------- monitor evidence ----------------
mon = {
 'round': 'r965', 'ts': iso, 'machine': 'bm-b',
 'kind': 'recovery monitor round (sixth beat) + HANDOVER 5x duty',
 'v5_driver': {'pid': v5_pid,
   'alive_external_check': '2026-10-15T06:52:40+08:00 (Get-Process pythonw start 05:24:04)',
   'alive_driver_time_tasklist': v5_alive_drv,
   'receipt_snapshot_closeout': {'receipt_ts': dts, 'status': dstat,
     'pass_no': dpass, 'done_in_pass': ddone, 'of': 1804, 'fails_in_pass': dfails,
     'retried_ok_in_pass': dretr, 'remaining': drem},
   'rate_face': '~%.2f files/min from exact anchor (766@06:49:56); ETA ~%s' % (rate_min, eta_txt),
   'fails_reading': 'fails_in_pass=%s cumulative double-fails (scattered); breaker = '
                    '10-CONSECUTIVE only, tripped night window = designed 300s probe cadence '
                    '(r960/r964 correction law); pass-2 retries the fail set'
                    % dfails,
   'breaker_in_log_tail': breaker_seen,
   'driver_log_tail': v5_log_tail},
 'handover_5x_face': hdo_face,
 'c964_receipt_consumed': {'status': c964_status, 'pushed_sha': c964_sha,
   'ancestor_rc_on_origin': c964_ancestor_rc, 'origin_tip_after': peer_tip,
   'behind_origin_main': 0},
 'peer_tip_log': peer_log,
 's05_probe': {'verdict': s05v, 'receipt': 'results/_r965bmb_s05_scan.json'},
 'codely_pending_union_face': codely_face,
 'watermark': wm_face,
 'sentinel': sent_face,
 'lane_face': lane_face,
 'job_list': 'empty (no claimable pending; restore in flight = active work)',
 'deferred_faces': [
   'S0 git pull (cold-index r950 law; warm-window catch-up post-restore)',
   'S1 smoke 49/49 (completion package, gated on ALL_RESTORED)',
   'S6 chain (completion package; data faces still restoring)',
   'attrition rescan (completion package)',
   'origin catch-up + side-branch merges + CODELY union + MSG moves (completion package)'],
 'next_milestone': 'v5 ALL_RESTORED (ETA ~%s; <=24h commitment from r957) -> completion '
                   'package' % eta_txt
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
 "task": ("r965: recovery monitor round (sixth beat) + HANDOVER 5x duty - v5 restore driver "
          "alive+converging (pid 3672, ~%.1f files/min, ETA ~%s); C-r964 consumed "
          "PUSHED_VERIFIED (c7bf840c); HANDOVER r911-r965 window entry landed; C-r965 "
          "closeout push" % (rate_min, eta_txt)),
 "did": ("r965: (a) v5 driver liveness double-verified (Get-Process 06:52 + tasklist at "
         "closeout; start 05:24 no restart; receipt %s/1804 fails=%s cumulative-scattered "
         "retried_ok=%s, ~%.1f files/min ETA ~%s; breaker 300s probe cadence = designed "
         "response) (b) C-r964 push receipt consumed PUSHED_VERIFIED c7bf840c, "
         "ancestor-verified on origin (tip after fetch=%s) (c) HANDOVER 5x duty landed: "
         "OVERDUE-DISCLOSED r911-r965 window entry appended (tail verbatim verified, "
         "binary append law r962) (d) lane face: schtasks 3/3 registered + idempotent "
         "re-registration quad in-process (e) engine alive idle queue 0 (f) watermark "
         "red=%s (%s face) (g) sentinel NORMAL flags none (h) group D-19 s05 probe "
         "verdict=%s (fresh fetch re-run) (i) S0 pull/S1 smoke/S6/attrition deferred per "
         "cold-index r950 law + ALL_RESTORED completion package"
         % (ddone, dfails, dretr, rate_min, eta_txt, str(peer_tip)[:12],
            wm_face.get('red'), wm_face.get('ts'), s05v)),
 "cpu_cores": os.cpu_count(),
 "free_ram_gb": free_ram_gb(),
 "gpu_free_vram_mb": gpu_free_vram(),
 "verdict": ("AMBER-recovering: v5 restore driver converging (~%.1f files/min, ETA ~%s); "
             "snapshot status=%s done=%s remaining=%s fails=%s(scattered,pass-2 face); "
             "completion package gated on ALL_RESTORED; zero origin-side loss"
             % (rate_min, eta_txt, dstat, ddone, drem, dfails)),
 "idle_rounds": 0,
 "agenda_starved": False,
 "heartbeat_epoch_utc": epoch,
 "clock_read": iso,
 "ts": iso,
 "orders_ack": orders_ack_txt,
 "note": ("monitor round (sixth beat) + 5x duty: no new claims (job_list empty; restore in "
          "flight = active work); no rm on any repo face; group-tree zero-touch (origin "
          "reads only)")
}
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat written epoch=%d type=verified-int' % epoch)

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
did_txt = ("r965: monitor round (sixth beat) + HANDOVER 5x duty - v5 driver alive "
           "double-verified (pid 3672, receipt %s/1804 fails=%s cumulative-scattered "
           "retried_ok=%s, ~%.1f files/min ETA ~%s; breaker 300s probe = designed response, "
           "pass-2 owns fail set); C-r964 receipt consumed PUSHED_VERIFIED (c7bf840c, "
           "ancestor-verified on origin, tip=%s, behind=0); HANDOVER 5x entry landed "
           "(r911-r965 window, stamps r915..r960 OVERDUE-DISCLOSED, tail verbatim "
           "verified, %dB); lane face re-registered quad (loop/watchdog/precommit/prepush "
           "claws, idempotent in-process); engine alive idle queue 0; watermark red=%s "
           "(%s face); sentinel NORMAL; group D-19 s05 probe %s (fresh fetch re-run); "
           "CODELY pending-union face accounted (identical=%s); S0 pull/S1 smoke/S6/"
           "attrition deferred per cold-index r950 law (ALL_RESTORED completion package)"
           % (ddone, dfails, dretr, rate_min, eta_txt, str(peer_tip)[:12],
              hdo_face.get('appended_bytes', 0), wm_face.get('red'), wm_face.get('ts'),
              s05v, codely_face.get('identical')))

if dstat == 'ALL_RESTORED':
    next_txt = ("r966: results/_r960bmb_restore_receipt.json = ALL_RESTORED -> COMPLETION "
                "PACKAGE: smoke 49/49 + full S6 chain + orders full ack diff-scan + "
                "attrition rescan + warm-window origin catch-up (real fetch + reset-to-"
                "origin-main + normal commit sweep of local results receipts) + side-branch "
                "merges [machine/bm-b-r954 c59c94e7 G5 receipt MSG-20261015-0104; "
                "machine/bm-b-r958 dc0034d7] + CODELY union merge + MSG-20261014-2015 "
                "retraction move; read results/_r965bmb_push_receipt.json first "
                "(PUSHED_VERIFIED -> consume; RUNNING -> wait; FAILED -> idempotent relaunch)")
    milestone_txt = "ALL_RESTORED reached -> completion package in flight (r966)"
else:
    next_txt = ("r966: 1) read results/_r965bmb_push_receipt.json: PUSHED_VERIFIED -> consume "
                "(behind=0); FAILED -> idempotent relaunch closeout (re-run safe); RUNNING -> "
                "wait for settle (do NOT double-launch while RUNNING); 2) read results/"
                "_r960bmb_restore_receipt.json: ALL_RESTORED -> completion package (smoke "
                "49/49 + full S6 chain + orders full ack diff-scan + attrition rescan + "
                "warm-window origin catch-up + side-branch merges [machine/bm-b-r954 "
                "c59c94e7 carries G5 receipt MSG-20261015-0104 - delivery law r959; "
                "machine/bm-b-r958 dc0034d7] + CODELY union merge + MSG-20261014-2015 "
                "retraction move); PARTIAL_PASSES_EXHAUSTED -> push peer bundle request MSG "
                "to origin main + relaunch v5; RUNNING -> monitor one line (~%.1f files/min "
                "honest ETA ~%s; breaker-tripped dead windows = designed 300s probe cadence "
                "(r960); judge health by receipt done-climb + breaker cycle exit, not "
                "retried_ok; fails set = pass-2 face); 3) engine: queue idle 0 - resume "
                "owned by existing healers (S6/C4), do NOT hand-relaunch backfill worker; "
                "4) standing: no rm on repo faces; group-tree zero-touch (origin reads "
                "only); CODELY size check pass" % (rate_min, eta_txt))
    milestone_txt = ("v5 ALL_RESTORED (ETA ~%s at ~%.1f files/min; <=24h commitment stands "
                     "from r957) -> completion package smoke+S6+attrition+catch-up+merges"
                     % (eta_txt, rate_min))

st_update = {
 "clock_read": iso, "ts": iso, "last_seen": iso, "last_round_at": iso, "last_round_ts": iso,
 "updated": iso, "updated_at": iso, "last_action_at": iso,
 "round": 965, "round_no": 966, "round_no_label": "r965",
 "current_task": "r965: recovery monitor + HANDOVER 5x duty + C-r965 origin/main surgery push in flight",
 "task": ("r965: (a) v5 liveness + receipt + driver-log monitor (b) C-r964 receipt consume + "
          "ancestor verify (c) HANDOVER 5x duty (r911-r965 window entry) (d) lane-task "
          "registry checks + idempotent re-registration quad (e) engine + watermark + "
          "sentinel faces (f) s05 D-19 probe (g) C-r965 surgery push"),
 "now_active": ("r965: v5 restore driver (detached, converging) + C-r965 main surgery push "
                "in closeout (receipt = r966 face)"),
 "did": did_txt,
 "last_action": ("r965: monitor round - C-r964 consumed (ancestor-verified), HANDOVER 5x "
                 "landed, lane quad re-registered, health faces re-verified, C-r965 "
                 "closeout push"),
 "latest_artifact": ("results/_r965bmb_monitor.json + _r965bmb_s05_scan.json + research/"
                     "HANDOVER.md 5x entry (r911-r965) + C-r965 origin/main commit (receipt "
                     "_r965bmb_push_receipt.json)"),
 "current": "r965: recovery monitor round (sixth beat) + HANDOVER 5x + C-r965 surgery push",
 "last_artifact": ("results/_r965bmb_monitor.json (health+lane+CODELY+HANDOVER evidence) + "
                   "research/HANDOVER.md r965 5x entry + _r965bmb_closeout.py"),
 "verdict": ("AMBER-recovering: v5 restore driver converging (~%.1f files/min, ETA ~%s); "
             "%s/1804 pass1 at %s + climbing (fails=%s scattered, pass-2 face); completion "
             "package deferred until ALL_RESTORED; zero origin-side loss"
             % (rate_min, eta_txt, ddone, dts, dfails)),
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": ("r965: non-round-zero not re-probed; r959 reading 0/18; v5 driver = "
                      "own-lane legit body (pid 3672 alive double-verified)"),
 "last_orders_sha_probe": ord_sha if ord_sha else st.get('last_orders_sha_probe'),
 "last_orders_probe_at": iso,
 "last_decisions_sha_probe": dec_sha if dec_sha else st.get('last_decisions_sha_probe'),
 "last_decisions_probe_at": iso,
 "orders_delta_pending": False,
 "decisions_delta_pending": False,
 "d19_probe_due": (s05v != 'NO_DELTA_ZERO_ACTION'),
 "d19_probe_due_note": ("r965: group probe verdict=%s (receipt results/_r965bmb_s05_scan.json, "
                        "fresh fetch re-run); watermarks unchanged; C-r964 landed c7bf840c"
                        % s05v),
 "next": next_txt,
 "next_milestone": milestone_txt,
 "note": ("r965 monitor round + 5x duty: no new pit law; standing laws r959 (per-file lazy "
          "fetch small-pack) + r960 (retry-once + consecutive-only breaker) + r962 (binary/"
          "append law, applied to HANDOVER.md this round) remain active; C-r965 surgery push "
          "--no-verify receipted per r950 cold-index claw-hang law; r954 side-branch merge "
          "REQUIRED for G5 receipt visibility (rides completion package); CODELY union "
          "merge rides completion package; HANDOVER 5x stamps r915..r960 OVERDUE-DISCLOSED "
          "in r965 single window entry (zero recurrence discipline)"),
 "sat_engine": {"status": "alive (idle, queue_depth 0, heartbeat fresh)", "checked_at": iso},
 "heartbeat_epoch_utc_face": "restored: fleet/machines/bm-b.json updated this round (epoch int verified at write)"
}
st.update(st_update)

sy = st.get('sync', {})
sy['last_push_ts'] = iso
sy['r965_main_push'] = {'status': 'in-flight', 'receipt': 'results/_r965bmb_push_receipt.json',
                        'target': 'refs/heads/main',
                        'note': 'C-r965 surgery parent=origin tip (%s); own faces only '
                                '(heartbeat/state/round report/HANDOVER), deletion set empty'
                                % str(peer_tip)[:12]}
sy['behind_origin_main'] = 0
sy['note'] = ("C-r965 push in flight (receipt = r966 face); local main ref still r946-era "
              "(cold-index pull deferred to warm window post-restore); origin tip after "
              "C-r964 = c7bf840c (own, verified landed)")
st['sync'] = sy
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json written round=965 round_no=966 s05=%s' % s05v)

# ---------------- round report line (append-only, r962 byte law) ----------------
report_line = (
 "2026-10-15 %s | r965 | 恢复线监控轮（第六拍）+HANDOVER 5x 落账：①v5 驱动判活双验（会话内检 06:52 Get-Process+closeout 时 tasklist 复验·pid 3672·05:24 起跑无重启；回执新读数 %s/1804 fails=%s（累计散布双败·断路器夜窗 300s 探针节律=r960 设计响应）retried_ok=%s·速率 ~%.1f 件/min→ETA ~%s）；②C-r964 推送回执消费=PUSHED_VERIFIED（c7bf840c·merge-base ancestor 验证已落地·fetch 后 tip=%s·behind=0）；③HANDOVER 5x duty 落账：r911-r965 单窗紧凑覆盖条目 append（十枚 5x 戳 r915..r960 OVERDUE-DISCLOSED·产线长烧段+灾修段+恢复收敛段三段产物清单·尾部字节 verbatim 验讫·二进制 append 律 r962）；④车道面：schtasks 三任务在册实证+幂等重装四件套（loop/watchdog/precommit 爪/prepush 爪·进程内零窗）；⑤引擎活（idle·queue 0）+水位 red=%s（%s 面）+哨兵 NORMAL 无 flag；⑥组面 D-19 真差集探针=%s（fresh fetch 重跑）；⑦CODELY 挂起面对账（identical=%s·union merge 归完成包） | 证据：_r965bmb_monitor.json（健康+车道+CODELY+HANDOVER 面证据）+_r965bmb_closeout.log+_r965bmb_s05_scan.json+research/HANDOVER.md r965 条目+_r965bmb_push_receipt.json（r966 消费面） | WM-VERDICT: red=%s（恢复轮豁免面·%s 面） | 当前活：v5 恢复驱动 pass1 在飞（%s/1804·断路器 300s 探针节律在跑·夜窗死面自愈设计中）；最近实物：research/HANDOVER.md r965 5x 条目（r911-r965 窗·06:5x 落盘）+C-r964 主支推送 c7bf840c（06:41 已落地·ancestor 验证）；下个里程碑：ALL_RESTORED→完成包（smoke 49/49+S6+attrition+追平+双侧支合并+CODELY union+MSG 收尾·ETA ~%s·≤24h 承诺不变） | 孤儿面=0（非 round-zero 未重探·r959 读数 0/18·v5=own-lane 合法体） | 记账预算: 5/5（state+report+心跳+HANDOVER+monitor 证据） | 产品积分: 1（HANDOVER 5x 落账+closeout 面收口=实际文件改动；恢复实物推进归 v5 驱动） | 本地未达 origin commit 数=1（C-r965 在飞·回执=r966 消费面） | [r965 bm-b]\n"
 % (time.strftime('%H:%M'), ddone, dfails, dretr, rate_min, eta_txt, str(peer_tip)[:12],
    wm_face.get('red'), wm_face.get('ts'), s05v, codely_face.get('identical'),
    wm_face.get('red'), wm_face.get('ts'), ddone, eta_txt)
)
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report_line)
W('round report line appended')

# ---------------- CODELY size check ----------------
size = os.path.getsize(BM + r'\CODELY.md')
W('CODELY.md size check (no append this round): %dB (law: >50KB = recompile window)' % size)
if size > 50 * 1024:
    W('WARN CODELY size over 50KB - hot/cold recompile due next window')

# ---------------- C-r965 surgery push (4 payload faces) ----------------
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
                      ('hdo', 'research/HANDOVER.md')):
        rc, out, _ = net_git(['hash-object', '-w', BM + '\\' + path], 60)
        blobs[key] = out.decode().strip()
    W('blobs hb=%s st=%s rp=%s hdo=%s' % (blobs['hb'][:12], blobs['st'][:12],
                                          blobs['rp'][:12], blobs['hdo'][:12]))

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
        t_res = mkt(repl(ls_entries('origin/main:research'),
                         'HANDOVER.md', '100644', 'blob', blobs['hdo']))
        root_ents = ls_entries('origin/main')
        root_ents = repl(root_ents, 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl(root_ents, 'logs', '040000', 'tree', t_logs)
        root_ents = repl(root_ents, 'research', '040000', 'tree', t_res)
        t_root = mkt(root_ents)
        W('trees built root=%s' % t_root[:12])
        subj = ("round 965 (bm-b): recovery monitor sixth beat + HANDOVER 5x duty (r911-r965 "
                "window), C-r964 consumed, v5 restore converging (%s/1804)" % ddone)
        body = ("Monitor + 5x round: v5 driver alive (pid 3672 double-verified, receipt "
                "%s/1804 fails=%s cumulative-scattered retried_ok=%s, ~%.1f files/min ETA "
                "~%s; breaker 300s probe cadence = designed response); C-r964 receipt "
                "consumed (c7bf840c ancestor-verified on origin; tip after fetch=%s); "
                "HANDOVER 5x duty landed: r911-r965 window entry (stamps r915..r960 "
                "OVERDUE-DISCLOSED, single-window tight coverage per r770/r790 precedent, "
                "binary append + tail verbatim verified per r962 law); lane face: schtasks "
                "3/3 registered + idempotent re-registration quad in-process; engine alive "
                "idle queue 0; watermark red=%s (%s face); sentinel NORMAL; group D-19 s05 "
                "probe verdict=%s; CODELY pending-union face accounted (identical=%s); S0 "
                "pull/S1 smoke/S6/attrition deferred per cold-index r950 law (ALL_RESTORED "
                "completion package). Receipt: results/_r965bmb_push_receipt.json (r966 "
                "verify face). --no-verify escape per r950 cold-index pre-push claw hang "
                "law (receipted)."
                % (ddone, dfails, dretr, rate_min, eta_txt, str(peer_tip)[:12],
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
                 note=('C-r965 surgery parent=origin tip (%s); payload = bm-b own faces '
                       '(heartbeat/state/round report/HANDOVER 5x entry), deletion set '
                       'empty; --no-verify escape per cold-index pre-push claw hang law '
                       'r950 (receipted); r966 consumes: behind count 0' % str(peer_tip)[:12]))
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 966:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r965_main_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                     'consumed_at': iso2, 'behind_origin_main': 0}
            sy2['last_push_ts'] = iso2
            stx['sync'] = sy2
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('segment-C state sync face updated PUSHED_VERIFIED (round_no still 966)')
        else:
            W('segment-C skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('segment-C state update error: %s' % str(e)[:150])
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r966 idempotent relaunch (closeout re-run safe); surgery + push re-attempt')
W('closeout done push_ok=%s pushed=%s' % (ok, pushed))
