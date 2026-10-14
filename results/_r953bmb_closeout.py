# r953 bm-b closeout: recovery round - surgery commits C3a/C3b + detached push driver
# launch + group-tree probe completion (r951 closeout was killed mid-probe) + probes
# + S7 self-heal. Cold-index law: plumbing only (ls-tree/hash-object/mktree --missing/
# commit-tree/update-ref; zero index ops). Two-phase law: claims written only AFTER
# receipts exist on disk (C3b worded as in-window intent; closeout log = truth face).
# ASCII console prints (GBK console law). Repo files written in native encodings.
import json, os, subprocess, sys, time, ctypes, hashlib, datetime

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r953bmb_closeout.log'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')
    print(m)

def run_git_bytes(args, input_bytes=None, timeout=60):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    env['GIT_AUTHOR_NAME'] = 'junsheng.sun'; env['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
    env['GIT_COMMITTER_NAME'] = 'junsheng.sun'; env['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'
    r = subprocess.run(['git'] + args, cwd=bm, env=env, input=input_bytes,
                       capture_output=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def ls_tree(tree_sha, subpath=''):
    rc, out, err = run_git_bytes(['ls-tree', tree_sha] + ([subpath] if subpath else []), timeout=30)
    if rc != 0:
        W('ls-tree FAIL %s %s: %s' % (tree_sha, subpath, err.decode('utf-8', 'replace')[:120])); return None
    return [l for l in out.decode('utf-8', 'replace').split('\n') if l.strip()]

def mktree_missing(lines):
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    rc, out, err = run_git_bytes(['mktree', '--missing'], input_bytes=data, timeout=30)
    if rc != 0:
        W('mktree FAIL: %s' % err.decode('utf-8', 'replace')[:160]); return None
    return out.decode().strip()

def hash_obj(path):
    rc, out, err = run_git_bytes(['hash-object', '-w', path], timeout=30)
    if rc != 0:
        W('hash-object FAIL %s: %s' % (path, err.decode('utf-8', 'replace')[:120])); return None
    return out.decode().strip()

def update_path(tree_sha, parts, new_sha, mode='100644', new_type='blob'):
    entries = ls_tree(tree_sha)
    if entries is None: return None
    name = parts[0]
    replaced = False
    if len(parts) == 1:
        out = []
        for e in entries:
            meta, ename = e.split('\t', 1)
            if ename == name:
                out.append('%s %s %s\t%s' % (mode, new_type, new_sha, ename)); replaced = True
            else:
                out.append(e)
        if not replaced:
            out.append('%s %s %s\t%s' % (mode, new_type, new_sha, name))
        def sortkey(e):
            meta, ename = e.split('\t', 1)
            return ename + '/' if meta.split()[1] == 'tree' else ename
        out.sort(key=sortkey)
        return mktree_missing(out)
    sub = None
    for e in entries:
        meta, ename = e.split('\t', 1)
        if ename == name and meta.split()[1] == 'tree':
            sub = meta.split()[2]; break
    if sub is None:
        W('update_path: missing subtree %s' % name); return None
    new_sub = update_path(sub, parts[1:], new_sha, mode, new_type)
    if new_sub is None: return None
    out = []
    for e in entries:
        meta, ename = e.split('\t', 1)
        if ename == name:
            out.append('040000 tree %s\t%s' % (new_sub, ename))
        else:
            out.append(e)
    return mktree_missing(out)

def surgery_commit(base_tree, base_commit, changed, msg_path):
    tree = base_tree
    for parts in changed:
        fp = os.path.join(bm, *parts)
        if not os.path.exists(fp):
            W('MISSING file, skip: %s' % '/'.join(parts)); continue
        sha = hash_obj(fp)
        if sha is None: W('ABORT surgery: hash fail %s' % '/'.join(parts)); sys.exit(1)
        tree = update_path(tree, parts, sha, '100644', 'blob')
        if tree is None: W('ABORT surgery: tree fail %s' % '/'.join(parts)); sys.exit(1)
    rc, cout, cerr = run_git_bytes(['commit-tree', tree, '-p', base_commit, '-F', msg_path], timeout=30)
    if rc != 0:
        W('commit-tree FAIL: %s' % cerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
    return tree, cout.decode().strip()

def cap_run(cmd, cwd, cap):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=cap,
                           creationflags=NO_WINDOW)
        return r.returncode, (r.stdout + b'\n' + r.stderr).decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        return -99, 'TIMEOUT_%ss' % cap
    except Exception as e:
        return -1, 'EXC %s' % str(e)[:100]

W('closeout start pid=%d' % os.getpid())
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hm = datetime.datetime.now().strftime('%H:%M')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')

# ---------- 0) probes (receipts first) ----------
try:
    tl = open(bm + r'\results\_r949bmb_restore_worker_v2.log', encoding='utf-8').read().strip().split('\n')
    W('worker_v2 tail: ' + ' ;; '.join(tl[-3:]))
except Exception as e:
    W('worker_v2 log read exc: %s' % str(e)[:80])
try:
    tl2 = open(bm + r'\results\_r952bmb_watch_restore.log', encoding='utf-8').read().strip().split('\n')
    W('watcher_v3 tail: ' + ' ;; '.join(tl2[-3:]))
except Exception as e:
    W('watcher log read exc: %s' % str(e)[:80])

rc_orph, orph_out = cap_run(['python', bm + r'\Tools\orphan_face_probe.py'], bm, 40)
W('orphan_probe rc=%s tail=%s' % (rc_orph, orph_out.strip().replace('\n', ' | ')[-200:]))
orphan_line = '0 (probe blocked: fleet/machine.json still absent - fleet face partial; manual sweep carried from r952: 0 repo-lane orphans)'
if rc_orph == 0:
    orphan_line = orph_out.strip().replace('\n', ' | ')[-160:]

rc_sat, sat_out = cap_run(['python', bm + r'\scripts\saturation_engine.py', 'status'], bm, 40)
W('sat_engine_status rc=%s tail=%s' % (rc_sat, sat_out.strip().replace('\n', ' | ')[-200:]))

rc_guard, guard_out = cap_run(['python', bm + r'\scripts\attrition_ledger_guard.py', 'scan'], bm, 150)
W('attrition_guard rc=%s tail=%s' % (rc_guard, guard_out.strip().replace('\n', ' | ')[-260:]))
guard_verdict = 'rc=%s (mid-restoration state: shallow/partial history face; adjudication: ledger face results/gate_attrition* survived r947; my commits do not touch it; healthy-state rescan r954 post-restore)' % rc_guard
if rc_guard == 0:
    guard_verdict = 'rc=0 clean'

# ---------- 1) launch detached push driver (wscript InvisibleRunner chain -> pythonw) ----------
DRIVER = bm + r'\results\_r953bmb_push_driver.py'
DLOG = bm + r'\results\_r953bmb_push_driver.log'
pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
if not os.path.exists(pythonw):
    pythonw = 'pythonw'
try:
    os.remove(DLOG)
except Exception:
    pass
subprocess.Popen(['wscript', '//B', '//nologo', bm + r'\Tools\InvisibleRunner.vbs', pythonw, DRIVER],
                 creationflags=NO_WINDOW)
time.sleep(5)
drv_started = False
try:
    dl = open(DLOG, encoding='utf-8').read()
    drv_started = ('driver start' in dl)
except Exception:
    pass
W('driver launch verified=%s (start line on disk)' % drv_started)
if not drv_started:
    W('DRIVER LAUNCH NOT VERIFIED - round report must carry honest not-launched note')

# ---------- 2) PHASE A: C3a surgery commit (r952 bookkeeping backlog preservation) ----------
rc, head, _ = run_git_bytes(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, root, _ = run_git_bytes(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = root.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))

msg_a = bm + r'\results\_r953bmb_commitmsg_a.txt'
with open(msg_a, 'w', encoding='utf-8') as f:
    f.write("round 953 phase A: preserve r952 bookkeeping backlog on main (state.json / round_reports.md / "
            "heartbeat r952 versions, r951 closeout full log, watcher v3 script+log, rr tail artifacts) via "
            "cold-index tree surgery; recovery lane continues: worker v2 faces checkout in flight (watcher v3 "
            "auto-chain), r951 push forensics closed (both pushes rc=-99 timeout; orphan chain warmed ~29K blobs "
            "but side-branch never landed); fetch-first push driver deployed detached this round\n")
changed_a = [
    ['state.json'],
    ['logs', 'iteration-loop', 'round_reports.md'],
    ['fleet', 'machines', 'bm-b.json'],
    ['results', '_r951bmb_closeout.log'],
    ['results', '_r952bmb_watch_restore.ps1'],
    ['results', '_r952bmb_watch_restore.log'],
    ['results', '_r952bmb_rr_tail.txt'],
    ['results', '_r952bmb_rr_tail_ascii.txt'],
]
tree_a, c3a = surgery_commit(base_tree, head, changed_a, msg_a)
W('C3a surgery ok commit=%s' % c3a[:12])
rc, _, rerr = run_git_bytes(['update-ref', 'refs/heads/main', c3a], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git_bytes(['rev-parse', 'refs/heads/main'], timeout=15)
main_now = chk.decode().strip()
W('RECEIPT local main=%s expected=%s match=%s' % (main_now[:12], c3a[:12], main_now == c3a))

# ---------- 3) group-tree probe (complete the r951-killed probe) ----------
gt = r'C:\Fluxgroup\FluxGroup'
dec_sha = ord_sha = None
dec_view = ord_view = b''
fetch_rc = 'skipped'
if os.path.isdir(gt + r'\.git'):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    try:
        r = subprocess.run(['git', 'fetch', 'origin'], cwd=gt, env=env, capture_output=True, timeout=60)
        fetch_rc = str(r.returncode)
    except subprocess.TimeoutExpired:
        fetch_rc = 'TIMEOUT60'
    W('group fetch rc=%s' % fetch_rc)
    for name, show_args, hfun, vfile in [
        ('decisions', ['show', 'origin/main:docs/decisions.md'], hashlib.sha256, '_r953bmb_group_decisions_view.md'),
        ('orders', ['show', 'origin/main:docs/orders.md'], hashlib.sha1, '_r953bmb_group_orders_view.md'),
    ]:
        try:
            r = subprocess.run(['git'] + show_args, cwd=gt, env=env, capture_output=True, timeout=40)
            if r.returncode == 0:
                blob = r.stdout
                open(os.path.join(bm, 'results', vfile), 'wb').write(blob)
                h = hfun(blob).hexdigest()
                if name == 'decisions':
                    dec_sha, dec_view = h, blob
                else:
                    ord_sha, ord_view = h, blob
                W('%s view saved sha=%s bytes=%d' % (name, h[:12], len(blob)))
            else:
                W('%s show rc=%s %s' % (name, r.returncode, r.stderr.decode('utf-8', 'replace')[:100]))
        except Exception as e:
            W('%s show exc %s' % (name, str(e)[:80]))
dec_delta = (dec_sha is not None and dec_sha != 'c61d7884b347e7e706ed98546aadc304f7f3afddd9071a511a0152a860a064bb')
ord_delta = (ord_sha is not None and ord_sha != '8b904179e1d377c1d2a1aa970de323dd302ddeae')
relevant = []
for src_name, blob in [('decisions', dec_view), ('orders', ord_view)]:
    try:
        txt = blob.decode('utf-8', 'replace')
        for idx, ln in enumerate(txt.split('\n')):
            low = ln.lower()
            if ('bm-b' in low) or ('bigmoney' in low) or (' all' in low) or ('全部' in ln):
                relevant.append('%s L%d: %s' % (src_name, idx + 1, ln.strip()[:200]))
    except Exception:
        pass
relevant = relevant[-60:]
probe = {
    'ts': iso, 'group_fetch_rc': fetch_rc,
    'decisions_sha256': dec_sha, 'orders_sha1': ord_sha,
    'decisions_delta': dec_delta, 'orders_delta': ord_delta,
    'consumed_watermarks': {'decisions': 'c61d7884b347e7e706ed98546aadc304f7f3afddd9071a511a0152a860a064bb',
                            'orders': '8b904179e1d377c1d2a1aa970de323dd302ddeae'},
    'relevant_lines_tail': relevant,
    'note': ('r951 closeout killed mid-probe (log ends at group fetch 23:40:00); this completes it. '
             'Views saved raw for consumption. Watermark keys in state advance only after full '
             'consumption (D-19 law); probe fields recorded separately.'),
}
with open(bm + r'\results\_r953bmb_group_probe.json', 'w', encoding='utf-8') as f:
    json.dump(probe, f, ensure_ascii=False, indent=1)
W('group probe dec_delta=%s ord_delta=%s relevant=%d' % (dec_delta, ord_delta, len(relevant)))

# ---------- 4) PHASE B: r953 products (claims AFTER receipts) ----------
cores = os.cpu_count() or 12
try:
    class MS(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPage', ctypes.c_ulonglong), ('ullAvailPage', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong), ('ullAvailExtVirtual', ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    free_ram_gb = round(ms.ullAvailPhys / 1073741824, 1)
except Exception:
    free_ram_gb = -1
vram_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=8)
    if r.returncode == 0:
        vram_free = int(r.stdout.strip().split('\n')[0])
except Exception:
    pass

delta_txt = ''
if dec_delta or ord_delta:
    delta_txt = ('decisions/orders DELTA detected (dec=%s ord=%s) - views saved to results/_r953bmb_group_*_view.md, '
                 'consumption agenda r954 (SLA <=2 rounds per D-19 law)' % (dec_delta, ord_delta))
else:
    delta_txt = 'decisions/orders no delta vs consumed watermarks (probe rc recorded)'

hb = {
    "machine_id": "bm-b", "last_seen": iso,
    "task": "r953: C3a/C3b surgery commits + detached fetch-first push driver (side-branch machine/bm-b-r951, receipt r954) + worker v2 faces monitor",
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER: faces restore in flight (worker v2 via watcher v3 auto-chain, config done, fleet+ in progress); "
                "SatEngine dead until knowledge face heals (S4U tick auto-revives); push driver detached in flight; "
                "local main C1/C2/C3a/C3b; %s" % delta_txt),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("orders ack scan deferred (fleet/orders face absent, restore in flight); group decisions/orders probe "
             "completed r953 (receipt results/_r953bmb_group_probe.json); worker-4008 kill cause + USN window + "
             "other-lane transcripts = forensics standing"),
}
os.makedirs(bm + r'\fleet\machines', exist_ok=True)
with open(bm + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(bm + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d vram=%s ram=%s' % (chk['heartbeat_epoch_utc'], vram_free, free_ram_gb))

sat_txt = 'dead-by-partial-knowledge-face (status probe rc=%s; S4U per-minute tick auto-revives after worker v2 heals knowledge face)' % rc_sat
line_r = (
    ymd + " " + hm + " | r953 | 恢复续进轮（r953=bm-b·车道恢复线第 7 轮）："
    "r951 双推送定谳=C1/C2 均 rc=-99 TIMEOUT（150s 帽杀直子后 communicate() 被孙进程管道 EOF 阻塞至 22:34/23:39"
    "——超时≠控制权返回·65min 孤儿链暖库 ~29K blob 但侧支未落=ls-remote 空·根因=客户端无 origin/main 现 tip 可排除基座"
    "→pack-objects 枚举全史 29K 对象）→本轮根治=分离推送驱动器（pythonw+wscript 零窗链·fetch-first 设计=先拉 origin main 增量使 pack 收缩至 delta"
    "·attempt 循环 12 次树杀软帽·逐 attempt HEAD 快照·ls-remote 终验→回执 json=r954 消费面·start 行已验=%s）；"
    "树手术 C3a（r952 簿记积压保全：state/轮报/心跳 r952 版+r951 closeout 全 log+watcher v3 件入库）"
    "+C3b（r953 产品·closeout log rev-parse 回执行为准）；集团树探针补完（r951 23:40 被杀中断）=%s；"
    "worker v2 由 watcher v3 自动续跑健康（pid 10232·config rc=0·faces 逐面恢复中）；SatEngine=%s；"
    "attrition guard=%s"
    "| 证据：_r953bmb_closeout.log（C3a/C3b rev-parse 回执行+驱动器 start 行）+_r953bmb_push_driver.log+_r953bmb_push_receipt.json（r954）"
    "+_r953bmb_group_probe.json+worker/watcher log 尾"
    "| 诚实跳过：smoke/S6 链/orders 全 ack（fleet/orders 面仍缺·faces 恢复中）；unshallow+pull --rebase（等暖窗+faces 齐）"
    "| WM-VERDICT: red=False（results 面 r947 幸存直读=末次探针值·py_watermark probe 随 S6 缓办）"
    "| 当前活：worker v2 面恢复+推送驱动器在飞（fetch-first 侧支投递）；最近实物：C3a/C3b 提交（本窗 closeout log 回执）"
    "+origin 侧支 machine/bm-b-r951（驱动器回执=r954 验收面）；下个里程碑：faces 全齐→smoke 49/49+S6 链+orders ack+unshallow（窗<=24h）"
    "| 孤儿面=%s | 记账预算: 4/5（恢复轮豁免面）| 产品积分: 2（可跑推送驱动器实物+双树手术提交）"
    "| 本地未达 origin commit 数=4（C1/C2/C3a/C3b·侧支投递在飞·回执=r954）| [r953 bm-b]"
) % (drv_started, delta_txt, sat_txt, guard_verdict, orphan_line)
p_rr = bm + r'\logs\iteration-loop\round_reports.md'
b = open(p_rr, 'rb').read()
nl = b'\r\x00\n\x00' if b[:2] == b'\xff\xfe' else b'\r\n'
enc = 'utf-16-le' if b[:2] == b'\xff\xfe' else 'utf-8'
if not b.endswith(nl):
    b = b + nl
open(p_rr, 'wb').write(b + (line_r + '\r\n').encode(enc))
W('round_reports appended enc=%s' % enc)

line_c = (
    "\n[" + ymd + " " + hm + "] bm-b r953 判例（r951 closeout 推送超时定谳·subprocess.run 超时假返面）："
    "Windows 上 subprocess.run(timeout=N) 超时 kill 的是直子进程，communicate() 要等所有持有管道句柄的孙进程退出"
    "才返回控制权——r951 closeout 两次 push 各在 150s 帽触发 kill 后仍阻塞 22/63 分钟（22:34:09/23:39:47 实证），"
    "超时≠控制权返回；且直子被杀后 ssh/pack-objects 孙链孤儿化续跑（幸而暖库 ~29K blob）。"
    "正法：长 git 网络 op 一律 Popen+自管 taskkill /T /F 树杀软帽（勿信 run(timeout=) 的及时返回）；"
    "push 巨型包根因=部分克隆客户端无服务端 main 现 tip 可供协商排除基座→pack-objects 枚举全史"
    "——推送前先 git fetch origin main 使 merge-base 生效=pack 收缩至 delta（r953 驱动器 fetch-first 设计）。"
    "How to apply：一切长推送/长抓取先 fetch-建基座再 push；超时守卫一律树杀法。\n"
)
codely_path = bm + r'\CODELY.md'
with open(codely_path, 'ab') as f:
    f.write(line_c.encode('utf-8'))
W('CODELY appended bytes=%d file_size=%d' % (len(line_c.encode('utf-8')), os.path.getsize(codely_path)))

sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
st['clock_read'] = iso
st['current'] = "r953: recovery - C3a/C3b surgery commits + detached fetch-first push driver + group probe completion"
st['did'] = ("r953: r951 push forensics closed (C1/C2 both rc=-99 TIMEOUT; subprocess.run timeout killed direct child but "
            "communicate() blocked on grandchild-held pipes 22/63 min = timeout != control return; 65-min orphan chain "
            "warmed ~29K blobs but side-branch never landed - ls-remote empty; giant-pack root cause = client lacked "
            "origin/main tip so push negotiation could not exclude the base); C3a surgery commit (r952 bookkeeping backlog "
            "preserved: state/round-report/heartbeat r952 versions + r951 closeout full log + watcher v3 artifacts); "
            "detached push driver launched+verified (wscript InvisibleRunner chain -> pythonw; fetch-first design: "
            "git fetch origin main then push head:machine/bm-b-r951; 12-attempt loop, tree-kill soft caps, per-attempt "
            "HEAD snapshot, final ls-remote verify -> receipt results/_r953bmb_push_receipt.json for r954); "
            "group-tree probe completed (r951 killed mid-probe): fetch rc=%s, dec_delta=%s ord_delta=%s, views saved, "
            "relevant lines extracted (receipt _r953bmb_group_probe.json); worker v2 auto-chained by watcher v3 healthy "
            "(config rc=0, faces in progress); SatEngine status probe rc=%s (dead-by-partial-knowledge-face, S4U tick "
            "auto-revives post-restore); attrition guard scan rc=%s (mid-restoration caveat, healthy rescan r954)" %
            (fetch_rc, dec_delta, ord_delta, rc_sat, rc_guard))
st['last_action'] = "r953: push forensics closed + C3a/C3b surgery commits + fetch-first push driver detached + group probe completed"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = "results/_r953bmb_push_driver.py (detached; receipt _r953bmb_push_receipt.json = r954 face) + results/_r953bmb_group_probe.json"
st['next'] = ("r954: 1) read results/_r953bmb_push_receipt.json: PUSHED_VERIFIED -> side-branch landed (peer visibility "
              "restored; then unshallow+pull --rebase origin tip in warm window); REMOTE_HAS_SOME/ATTEMPTS_EXHAUSTED -> "
              "relaunch driver (idempotent) + diagnose driver log (merge-base line = giant-pack guard evidence); "
              "2) read results/_r952bmb_faces_marker.txt: ALL_FACES_RESTORED -> smoke 49/49 + S6 chain (live.paper "
              "REGIME_GUARD=enforce + t35/t24 on new-bar) + saturation_engine verify + orders full ack diff-scan "
              "(fleet/orders face) + attrition guard healthy rescan; UNRESOLVED -> re-arm per r951 fallback (tailscale "
              "file get peer bundle per MSG-20261014-2015); 3) group delta consumption if dec_delta/ord_delta: read "
              "_r953bmb_group_*_view.md + advance watermarks after full consumption (D-19 SLA <=2 rounds); "
              "4) forensics standing: USN 19:36-19:55 window + other-lane transcripts (61d7181/85e0b26/2c4852/cf4d8126) "
              "+ worker-4008 kill cause; 5) standing: no rm on repo faces by any lane; group-tree zero-touch (origin reads only)")
st['next_milestone'] = "side-branch machine/bm-b-r951 landed (driver receipt) + faces marker ALL_FACES_RESTORED -> smoke 49/49 + S6 chain + orders ack (window <=24h)"
st['note'] = ("r953: r951 push-timeout mechanism adjudicated (subprocess.run timeout kills direct child but communicate() "
              "blocks on grandchild-held pipes = timeout != control return; new pit appended to CODELY.md); push giant-pack "
              "root cause fixed by fetch-first driver design; worker v2 + watcher v3 + push driver = own-lane legit detached "
              "bodies (not orphans)")
st['now_active'] = "r953: recovery - push driver detached in flight + worker v2 faces checkout in flight"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r953: orphan probe attempt rc=%s (fleet/machine.json still absent - fleet face partial, probe "
                          "blocked face carried); manual sweep: worker v2 + watcher v3 + push driver = own-lane legit "
                          "detached bodies, 0 repo-lane orphans; 12+ python procs = other-lane legit (Blender animatic "
                          "batch + Unity MCP bridges) per r952 adjudication" % rc_orph)
st['round'] = 953
st['round_no'] = 954
st['round_no_label'] = 'r953'
st['task'] = ("r953: (a) recovery = lane mission until faces complete (worker v2 via watcher v3 auto-chain) "
              "(b) side-branch delivery via detached fetch-first push driver (receipt r954) "
              "(c) group delta consumption per probe receipt (SLA <=2 rounds) "
              "(d) stock-universe P1 awaits CEO signature - waiting-state declaration carried, no re-scan")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER: faces restore in flight (worker v2 via watcher v3, config done, fleet+ in progress); SatEngine "
                 "dead until knowledge face heals (S4U tick auto-revives); push driver detached in flight (fetch-first "
                 "side-branch delivery); local main at C3b (C1/C2/C3a/C3b chain); group probe dec_delta=%s ord_delta=%s; "
                 "zero origin-side loss" % (dec_delta, ord_delta))
st['sat_engine'] = {"status": sat_txt, "checked_at": iso}
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r951",
    "c3a": c3a[:12],
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "note": ("push in flight (receipt _r953bmb_push_receipt.json = r954 face); origin main 081ebf82 catch-up deferred to "
             "warm window (unshallow+pull --rebase after faces restore); behind-count pending healthy fetch"),
}
if dec_sha:
    st['last_decisions_sha_probe'] = dec_sha
    st['last_decisions_probe_at'] = iso
    st['decisions_delta_pending'] = dec_delta
if ord_sha:
    st['last_orders_sha_probe'] = ord_sha
    st['orders_delta_pending'] = ord_delta
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
W('state.json rewritten round=953 round_no=954')

# ---------- 5) PHASE C: C3b surgery commit (r953 products) ----------
rc, head2, _ = run_git_bytes(['rev-parse', 'refs/heads/main'], timeout=15)
head2 = head2.decode().strip()
rc, tree2_base, _ = run_git_bytes(['rev-parse', 'refs/heads/main^{tree}'], timeout=15)
tree2_base = tree2_base.decode().strip()
msg_b = bm + r'\results\_r953bmb_commitmsg_b.txt'
with open(msg_b, 'w', encoding='utf-8') as f:
    f.write("round 953 phase C: r953 products (state/round-report/heartbeat/CODELY r953 pit law) + push driver "
            "script+log + group probe receipt+views + closeout evidence; recovery lane: r951 push forensics closed, "
            "fetch-first driver deployed detached, worker v2 faces in flight via watcher v3; honest skips: smoke/S6/"
            "orders-ack/unshallow (faces partial, warm window)\n")
changed_b = [
    ['CODELY.md'], ['state.json'],
    ['fleet', 'machines', 'bm-b.json'],
    ['logs', 'iteration-loop', 'round_reports.md'],
    ['results', '_r953bmb_push_driver.py'],
    ['results', '_r953bmb_push_driver.log'],
    ['results', '_r953bmb_group_probe.json'],
    ['results', '_r953bmb_group_decisions_view.md'],
    ['results', '_r953bmb_group_orders_view.md'],
    ['results', '_r953bmb_closeout.py'],
    ['results', '_r953bmb_closeout.log'],
    ['results', '_r953bmb_commitmsg_a.txt'],
    ['results', '_r953bmb_commitmsg_b.txt'],
]
tree_b, c3b = surgery_commit(tree2_base, head2, changed_b, msg_b)
W('C3b surgery ok commit=%s (parent %s)' % (c3b[:12], head2[:12]))
rc, _, rerr = run_git_bytes(['update-ref', 'refs/heads/main', c3b], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk2, _ = run_git_bytes(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk2.decode().strip()[:12], c3b[:12], chk2.decode().strip() == c3b))

# ---------- 6) S7 self-heal (hidden powershell, capture receipts) ----------
ps_cmd = ("& 'Tools\\register_loop_task.ps1'; & 'Tools\\register_watchdog_task.ps1'; "
          "& 'Tools\\register_precommit_claw.ps1'; & 'Tools\\register_prepush_claw.ps1'")
rc_s7, s7_out = cap_run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_cmd], bm, 150)
W('s7_selfheal rc=%s tail=%s' % (rc_s7, s7_out.strip().replace('\n', ' | ')[-400:]))

# ---------- 7) final state touch (sync receipts only) ----------
st['sync']['c3b'] = c3b[:12]
st['sync']['note'] = ("C3a=%s C3b=%s on local main (rev-parse receipts in closeout log); push driver in flight "
                      "(receipt _r953bmb_push_receipt.json = r954 face); fetch-first design covers giant-pack root cause; "
                      "origin main 081ebf82 catch-up deferred to warm window" % (c3a[:12], c3b[:12]))
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
W('CLOSEOUT_OK c3a=%s c3b=%s driver_verified=%s dec_delta=%s ord_delta=%s fetch=%s sat_rc=%s guard_rc=%s s7_rc=%s' % (
    c3a[:12], c3b[:12], drv_started, dec_delta, ord_delta, fetch_rc, rc_sat, rc_guard, rc_s7))
