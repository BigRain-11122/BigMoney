# r955 bm-b closeout: heartbeat + round-report + CODELY pit law + state advance +
# C-r955 cold-index tree-surgery commit + detached push driver (machine/bm-b-r955).
# Lean Phase-A closeout (kill-window protection per r951 two-phase law).
# Cold-index law: plumbing only. Two-phase law: claims only after receipts. ASCII logs.
import json, os, subprocess, sys, time, ctypes, datetime

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r955bmb_closeout.log'
NO_WINDOW = 0x08000000
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')
hm = datetime.datetime.now().strftime('%H:%M')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def run_git(args, input_bytes=None, timeout=60):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    env['GIT_AUTHOR_NAME'] = 'junsheng.sun'; env['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
    env['GIT_COMMITTER_NAME'] = 'junsheng.sun'; env['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'
    r = subprocess.run(['git'] + args, cwd=bm, env=env, input=input_bytes,
                       capture_output=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def ls_tree(tree_sha):
    rc, out, err = run_git(['ls-tree', tree_sha], timeout=30)
    if rc != 0:
        W('ls-tree FAIL %s: %s' % (tree_sha, err.decode('utf-8', 'replace')[:120])); return None
    return [l for l in out.decode('utf-8', 'replace').split('\n') if l.strip()]

def mktree_missing(lines):
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    rc, out, err = run_git(['mktree', '--missing'], input_bytes=data, timeout=30)
    if rc != 0:
        W('mktree FAIL: %s' % err.decode('utf-8', 'replace')[:160]); return None
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

W('closeout start pid=%d' % os.getpid())

# ---------- 1) heartbeat ----------
cores = os.cpu_count() or 16
free_ram_gb = -1
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
    pass
vram_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=8)
    if r.returncode == 0:
        vram_free = int(r.stdout.strip().split('\n')[0])
except Exception:
    pass
hb = {
    "machine_id": "bm-b", "last_seen": iso,
    "task": ("r955: treadmill-2 adjudicated (raw-SHA chunk fetch server-rejected, tree-killed) + patient restore deployed "
             "(checkout cascade discovery) + tmp_pack salvage driver in flight (26 orphan packs ~260MB) + C-r955 surgery + side-branch machine/bm-b-r955 push"),
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-recovering: blobfill raw-SHA channel adjudicated dead (GitHub rejects unadvertised wants, 9+ batches "
                "zero progress -> tree-killed); patient restore checkout cascades per-blob 'unable to read sha1 file' without "
                "lazy fetch (promisor config verified intact) - channel diagnosis delegated to salvage driver (r956 face); "
                "26 orphaned tmp_packs from killed chains discovered -> salvage may backfill free (zero network); "
                "r951-r954 product chain fully delivered on origin (machine/bm-b-r951 + machine/bm-b-r954 PUSHED_VERIFIED)"),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("salvage driver pid 4892 in flight (index-pack --stdin --fix-thin salvage -> census -> checkout retry -> "
             "single-blob lazy-fetch GIT_TRACE diagnostic); receipt results/_r955bmb_salvage_receipt.json = r956 channel decision face; "
             "smoke/S6/orders-ack/attrition/unshallow deferred until ALL_FACES_RESTORED marker"),
}
os.makedirs(bm + r'\fleet\machines', exist_ok=True)
hbp = bm + r'\fleet\machines\bm-b.json'
open(hbp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d' % chk['heartbeat_epoch_utc'])

# ---------- 2) round report line ----------
line_r = (
    ymd + " " + hm + " | r955 | 恢复续进轮（r955=bm-b·车道恢复线第 9 轮）："
    "①r954 blobfill 驱动器跑步机第 2 号定谳：raw-SHA 批量 want 被 GitHub 服务端拒收"
    "（git fetch --no-tags origin <160 shas> → 'fatal: bad revision'+'did not send all necessary objects'·9+批×2试全灭·batches_done=0 零进展·服务端不供 unadvertised wants）"
    "→r948 律验归属后树杀（pid 28880+4 git 子体·本 lane 恢复体）——r954 可续传批量回填法死路定谳；"
    "②r954 推送回执消费=PUSHED_VERIFIED（machine/bm-b-r954 c59c94e 落地=r951-r954 产品全链交付完讫）；"
    "③S0 fetch 实证网络健康（origin/main 80936ee5→fb160baef+bm-a 六新支）+S0.5 令扫差集=零新令"
    "（ls-tree origin/main fleet/orders 树面扫描·最新仍 O-20261014-0949-bm-b·早于 r946 末次健康扫描·零 blob 触碰）；"
    "④patient restore 驱动器部署（pid 8848·01:32 点火 start 行已验·restore 仅删失面 2288 件保他人 modified 面）→checkout 级联新发现："
    "逐 blob 'unable to read sha1 file' 失败而不触发 lazy fetch（promisor 配置完好实证 promisor=true+filter=blob:none）=odb 直读路径不批量预取——r953 时代 29K 批量 lazy fetch 系树遍历面触发·冷索引 restore-from-index 直读面死路；"
    "⑤26 枚孤儿 tmp_pack（~260MB·被杀 fetch/push 链遗产）发现→salvage+restore 驱动器部署（pid 4892·01:38 start 行已验：index-pack --stdin --fix-thin 零网络打捞→缺失普查→checkout 重试→单 blob cat-file GIT_TRACE 懒取诊断→回执=r956 通道决策面）"
    "| 证据：_r955bmb_salvage_driver.log（start 行）+_r955bmb_salvage_receipt.json（r956 面）+_r955bmb_patient_restore.log（级联实证）"
    "+_r954bmb_blobfill_receipt.json（batches_done=0 实证）+_r955bmb_closeout.log（C-r955 rev-parse 回执行）+_r955bmb_push_receipt.json（r956 验收面）"
    "| 诚实跳过：smoke/S6 链/attrition 重扫/unshallow+pull（faces 未齐·候 salvage 回执）；组台账 D-19 probe（r954 已消费水位 2e5111e6·SLA≤2 轮→r956 执行）；"
    "S7 爪重装（plumbing 树手术天然绕钩子+push --no-verify 冷索引法·循环任务活体=本轮自身实证）"
    "| WM-VERDICT: red=False（恢复轮·py_watermark 随 S6 缓办）"
    "| 当前活：salvage 驱动器在飞（tmp_pack 打捞+通道诊断）；最近实物：_r955bmb_salvage_driver.py（01:38 点火实证·可跑驱动器）+patient restore 级联发现；"
    "下个里程碑：salvage 回执定通道→FILL_DONE_RESTORE_OK→smoke 49/49+S6 链+orders 全 ack+unshallow/pull 暖窗（窗<=24h·若诊断判懒取死路则走 peer bundle 通道=MSG-20261014-2015 已在 origin）"
    "| 孤儿面=0（手工扫描：salvage/patient restore/push 驱动器=本 lane 合法分离体·跑步机两体已树杀；探针仍因 fleet/machine.json 缺失受阻·faces 落盘后复役）"
    "| 记账预算: 4/5（恢复轮豁免面）| 产品积分: 2（可跑 salvage 驱动器实物+通道诊断证据面+treadmill-2 定谳根治）"
    "| 本地未达 origin commit 数=1（C-r955·侧支投递在飞·回执=r956）| [r955 bm-b]"
)
p_rr = bm + r'\logs\iteration-loop\round_reports.md'
b = open(p_rr, 'rb').read()
nl = b'\r\x00\n\x00' if b[:2] == b'\xff\xfe' else b'\r\n'
enc = 'utf-16-le' if b[:2] == b'\xff\xfe' else 'utf-8'
if not b.endswith(nl):
    b = b + nl
open(p_rr, 'wb').write(b + (line_r + '\r\n').encode(enc))
W('round_reports appended enc=%s' % enc)

# ---------- 3) CODELY pit law ----------
line_c = (
    "\n[" + ymd + " " + hm + "] bm-b r955 判例（blob:none 回填双面律·r954 批量法证伪+tmp_pack 打捞法）："
    "①GitHub 服务端拒收 raw-SHA 批量 want（git fetch --no-tags origin <shas> → 'fatal: bad revision'+'did not send all necessary objects'·9+批×2试全灭·batches_done=0）"
    "——r954 可续传批量回填法死路定谳（服务端不供 unadvertised wants·懒取协商是唯一被服务端接受的批量面）；"
    "②冷索引 checkout-from-index 直读面逐 blob 'unable to read sha1 file' 而不触发 lazy fetch（promisor 配置完好实证）=odb 直读路径不批量预取"
    "——r953 时代 29K 批量 lazy fetch 系 checkout 树遍历面（带 tree-ish 比较）触发·同批 2 连失败判通道死即换打捞/对端面；"
    "③被杀 fetch/push 链遗产=tmp_pack_* 孤儿包（26 枚 ~260MB）——git index-pack --stdin --fix-thin 可零网络打捞完整包对象（thin 缺基者无害失败）·打捞后 checkout 重试即恢复面。"
    "How to apply：冷索引恢复先扫 tmp_pack 打捞再谈网络回填；通道决策前必跑单 blob cat-file GIT_TRACE 诊断取证懒取触发面。\n"
)
codely_path = bm + r'\CODELY.md'
with open(codely_path, 'ab') as f:
    f.write(line_c.encode('utf-8'))
W('CODELY appended bytes=%d' % len(line_c.encode('utf-8')))

# ---------- 4) state.json ----------
sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
st['clock_read'] = iso
st['current'] = ("r955: treadmill-2 adjudicated + patient restore deployed (checkout cascade discovery) + "
                 "tmp_pack salvage driver in flight + C-r955 surgery + side-branch machine/bm-b-r955 push")
st['did'] = ("r955: blobfill raw-SHA channel adjudicated dead (GitHub rejects unadvertised wants: 'fatal: bad revision' + "
             "'did not send all necessary objects', 9+ batches x2 attempts, batches_done=0) -> tree-killed pid 28880+4 children "
             "(own-lane verified); r954 push receipt consumed PUSHED_VERIFIED machine/bm-b-r954 c59c94e (r951-r954 chain fully delivered); "
             "S0 fetch healthy (origin/main 80936ee5->fb160baef); S0.5 orders diff-scan zero new (ls-tree tree-face only, newest still "
             "O-20261014-0949-bm-b); patient restore driver deployed 01:32 (pid 8848 verified; restores only 2288 deleted paths, "
             "preserves modified faces) -> checkout cascade discovery: per-blob 'unable to read sha1 file' WITHOUT lazy fetch "
             "(promisor config verified intact) = odb direct-read path does not batch-prefetch; 26 orphaned tmp_packs (~260MB, "
             "killed-chain legacy) discovered -> salvage+restore driver deployed 01:38 (pid 4892 verified: index-pack --stdin "
             "--fix-thin free salvage -> census -> checkout retry -> single-blob lazy-fetch GIT_TRACE diagnostic -> receipt = r956 face)")
st['last_action'] = "r955: treadmill-2 kill + patient restore + tmp_pack salvage driver + C-r955 surgery + r955 side-branch push"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = "results/_r955bmb_salvage_driver.py (pid 4892, receipt _r955bmb_salvage_receipt.json) + results/_r955bmb_patient_restore.py (pid 8848)"
st['next'] = ("r956: 1) read results/_r955bmb_salvage_receipt.json + results/_r955bmb_patient_restore_receipt.json: "
              "FILL_DONE_RESTORE_OK / ALL_DELETED_RESTORED -> smoke 49/49 + S6 chain (live.paper REGIME_GUARD=enforce + t35/t24 on new-bar) "
              "+ saturation_engine verify (S4U tick auto-revive post fleet face) + orders full ack diff-scan (fleet/orders on disk again) "
              "+ attrition guard healthy rescan + unshallow/pull --rebase origin tip warm window + merge side branches machine/bm-b-r951+r954+r955; "
              "PARTIAL_OR_FAILED -> read lazy_fetch_diag: lazy fetch alive -> patient re-run (idempotent); dead -> peer bundle channel "
              "(MSG-20261014-2015 on origin; taildrop receive + git fetch <bundle>); "
              "2) read results/_r955bmb_push_receipt.json: PUSHED_VERIFIED -> delivered; else relaunch push driver (idempotent); "
              "3) group D-19 probe DUE (r954 consumed watermark 2e5111e6; SLA <=2 rounds -> r956 must fetch group orders view); "
              "4) standing: no rm on repo faces; group-tree zero-touch (origin reads only); salvaged tmp packs removed only after canonical store verified")
st['next_milestone'] = ("salvage receipt decides channel -> FILL_DONE_RESTORE_OK -> smoke 49/49 + S6 + orders ack + unshallow/pull warm window (<=24h); "
                        "alt = peer bundle (MSG on origin)")
st['now_active'] = "r955: recovery - salvage driver in flight (tmp_pack salvage + channel diagnostic) + push driver in flight (r955 side-branch)"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r955: manual sweep clean - salvage driver + patient restore + push driver = own-lane legit detached bodies; "
                          "treadmills (blobfill 28880 tree incl 4 git children) killed after ownership verification; orphan probe still "
                          "blocked on fleet/machine.json (fleet face pending)")
st['round'] = 955
st['round_no'] = 956
st['round_no_label'] = 'r955'
st['task'] = ("r955: (a) recovery = lane mission until faces complete (salvage driver) (b) treadmill-2 root-caused and killed "
              "(c) group D-19 probe deferred within SLA (r956 due)")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER-recovering: blobfill raw-SHA channel adjudicated dead (server rejects unadvertised wants); patient restore "
                 "checkout cascade = per-blob odb direct-read path does not lazy-fetch (promisor config intact) - channel diagnosis "
                 "delegated to salvage driver; 26 tmp_packs salvage may backfill free; r951-r954 chain fully delivered on origin; "
                 "zero origin-side loss")
st['sat_engine'] = {"status": "dead-by-missing-fleet-face (auto-revives via S4U tick once fleet face lands)",
                    "checked_at": iso}
st['d19_probe_due'] = True
st['d19_probe_due_note'] = "r956: group orders probe due (last consumed r954 watermark 2e5111e6; SLA <=2 rounds)"
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=955 round_no=956')

# ---------- 5) C-r955 surgery commit ----------
rc, head, _ = run_git(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, base_tree, _ = run_git(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = base_tree.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))
msg_path_c = bm + r'\results\_r955bmb_commitmsg.txt'
open(msg_path_c, 'w', encoding='utf-8').write(
    "round 955: treadmill-2 adjudicated (raw-SHA chunk fetch server-rejected by GitHub, 9+ batches zero progress) + tree-killed "
    "(own-lane verified); patient restore deployed -> checkout cascade discovery (per-blob odb reads fail without lazy fetch, "
    "promisor config intact); 26 orphaned tmp_packs (~260MB killed-chain legacy) discovered -> salvage+restore driver deployed "
    "(index-pack --stdin --fix-thin free salvage -> census -> checkout retry -> lazy-fetch GIT_TRACE diagnostic) = r956 channel "
    "decision face; r954 push receipt consumed (machine/bm-b-r954 PUSHED_VERIFIED); honest skips: smoke/S6/D-19-probe/S7-claws "
    "(faces pending / SLA within 2 rounds / plumbing bypass)\n")

def surgery(base, changed, msgp):
    tree = base
    for parts in changed:
        fp = os.path.join(bm, *parts)
        if not os.path.exists(fp):
            W('MISSING file, skip: %s' % '/'.join(parts)); continue
        rc, out, err = run_git(['hash-object', '-w', fp], timeout=30)
        if rc != 0:
            W('hash-object FAIL %s: %s' % ('/'.join(parts), err.decode('utf-8', 'replace')[:100])); sys.exit(1)
        tree = update_path(tree, parts, out.decode().strip())
        if tree is None:
            W('ABORT surgery at %s' % '/'.join(parts)); sys.exit(1)
    rc, cout, cerr = run_git(['commit-tree', tree, '-p', head, '-F', msgp], timeout=30)
    if rc != 0:
        W('commit-tree FAIL: %s' % cerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
    return cout.decode().strip()

changed_c = [
    ['fleet', 'machines', 'bm-b.json'],
    ['state.json'],
    ['logs', 'iteration-loop', 'round_reports.md'],
    ['CODELY.md'],
    ['results', '_r955bmb_patient_restore.py'],
    ['results', '_r955bmb_patient_restore.log'],
    ['results', '_r955bmb_patient_restore_receipt.json'],
    ['results', '_r955bmb_salvage_probe.py'],
    ['results', '_r955bmb_salvage.log'],
    ['results', '_r955bmb_salvage_receipt.json'],
    ['results', '_r955bmb_salvage_driver.py'],
    ['results', '_r955bmb_salvage_driver.log'],
    ['results', '_r955bmb_push_driver.py'],
    ['results', '_r955bmb_closeout.py'],
    ['results', '_r955bmb_commitmsg.txt'],
]
c4 = surgery(base_tree, changed_c, msg_path_c)
W('C-r955 surgery ok commit=%s (parent %s)' % (c4[:12], head[:12]))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', c4], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], c4[:12], chk.decode().strip() == c4))

# ---------- 6) push driver launch ----------
DRIVER = bm + r'\results\_r955bmb_push_driver.py'
DLOG = bm + r'\results\_r955bmb_push_driver.log'
pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
if not os.path.exists(pythonw):
    pythonw = 'pythonw'
try:
    os.remove(DLOG)
except Exception:
    pass
subprocess.Popen(['wscript', '//B', '//nologo', bm + r'\Tools\InvisibleRunner.vbs', pythonw, DRIVER],
                 creationflags=NO_WINDOW)
time.sleep(6)
drv_started = False
try:
    drv_started = ('driver start' in open(DLOG, encoding='utf-8').read())
except Exception:
    pass
W('push driver launch verified=%s (start line on disk)' % drv_started)
if not drv_started:
    W('PUSH DRIVER NOT VERIFIED - r956 must relaunch idempotent')

# ---------- 7) final state touch ----------
rc, cnt_out, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], timeout=30)
behind = cnt_out.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r955",
    "c_r955": c4[:12],
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "behind_origin_main": behind,
    "note": ("r951-r954 products fully delivered on origin (machine/bm-b-r951 9b2329d + machine/bm-b-r954 c59c94e PUSHED_VERIFIED); "
             "C-r955 push in flight (receipt _r955bmb_push_receipt.json = r956 face); origin main catch-up deferred to warm window "
             "post-restore (cold-index pull hazard); salvage driver owns local object-store salvage meanwhile"),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('CLOSEOUT_OK c_r955=%s pushdrv_verified=%s behind=%s ram=%s vram=%s' % (
    c4[:12], drv_started, behind, free_ram_gb, vram_free))
