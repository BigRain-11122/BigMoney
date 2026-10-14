# r958 bm-b closeout: recovery-lane round. Consumes r957 push receipt (PUSHED_VERIFIED),
# records v3 driver deployment + census + instant 300-file restore + S0.5 NO_DELTA,
# heartbeat + round-report + CODELY r958 law + state advance + C-r958 cold-index
# tree-surgery commit + detached push driver (machine/bm-b-r958). Plumbing only
# (cold-index law r950); claims only after receipts (r951); idempotent re-entry
# guards on append faces. ASCII-safe log lines.
import ctypes, datetime, json, os, subprocess, sys, time

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r958bmb_closeout.log'
NO_WINDOW = 0x08000000
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')
hm = datetime.datetime.now().strftime('%H:%M')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def env():
    e = os.environ.copy()
    e['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    e['GIT_AUTHOR_NAME'] = 'junsheng.sun'; e['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
    e['GIT_COMMITTER_NAME'] = 'junsheng.sun'; e['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'
    return e

def run_git(args, cwd=bm, timeout=60, input_bytes=None):
    r = subprocess.run(['git'] + args, cwd=cwd, env=env(), input=input_bytes,
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

# ---------- 0) consume faces: r957 push receipt + s05 scan + driver receipt ----------
pr = json.load(open(bm + r'\results\_r957bmb_push_receipt.json', encoding='utf-8'))
r957_push = pr.get('status')
W('r957 push receipt consumed: %s sha=%s' % (r957_push, str(pr.get('pushed_sha'))[:12]))
s05 = json.load(open(bm + r'\results\_r958bmb_s05_scan.json', encoding='utf-8'))
W('s05 scan: verdict=%s ord_changed=%s dec_changed=%s' % (
    s05.get('verdict'), s05.get('orders_changed'), s05.get('decisions_changed')))
drv = {}
try:
    drv = json.load(open(bm + r'\results\_r958bmb_restore_receipt.json', encoding='utf-8'))
except Exception:
    pass
W('v3 driver face: status=%s remaining=%s restored=%s' % (
    drv.get('status', 'n/a'), drv.get('remaining_deleted', 'n/a'), drv.get('restored_files', 'n/a')))
cen = json.load(open(bm + r'\results\_r958bmb_census.json', encoding='utf-8'))
W('census face: deleted=%s zero_chunks=%s fetch_chunks=%s missing_blobs=%s' % (
    cen.get('deleted_paths'), cen.get('chunks_zero_missing'),
    cen.get('chunks_needs_fetch'), cen.get('missing_blobs_needs_fetch')))

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
    "task": ("r958: recovery lane - r955 patient/salvage drivers verified DEAD (patient rc=128 ssh-conn drop "
             "01:51 + salvage census-phase silent death; stale RUNNING receipts exposed by process-table+log "
             "audit); v3 batched restore driver deployed (census 2257 deleted = 331 blob-local + 1926 need "
             "lazy fetch; 300 instant files restored in-round 0.4s/chunk; fetch chunks in flight patient); "
             "r957 push receipt consumed PUSHED_VERIFIED machine/bm-b-r957"),
    "did": ("r958: restore v3 driver (results/_r958bmb_restore_driver.py) + census artifact "
            "(_r958bmb_census.json) + 300 files instant-restored + S0.5 light rescan NO_DELTA (ord 6cc07bf4 / "
            "dec 6910a9ed unchanged) + treasure_guard restore gate rc0 + engine status alive-idle + orphan "
            "probe 14 faces 0 orphans + r957 push receipt PUSHED_VERIFIED consumed"),
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-recovering: v3 restore driver in flight (fetch chunks patient, partial-persistence "
                "convergence proven: chunk7 rc=255 still wrote 8 files); 300/2257 instant-restored in-round; "
                "smoke/S6/attrition/origin-catchup deferred until ALL_RESTORED; saturation engine alive-idle; "
                "zero origin-side loss"),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("v3 driver = own-lane legit detached body (receipt progress-updated); peer bundle fallback "
             "(MSG-20260914-2015) still available if channel stalls; fleet/tasks+orders faces missing on "
             "disk (593+213 files) - board reads deferred to post-restore package; no rm on any repo face"),
}
hbp = bm + r'\fleet\machines\bm-b.json'
open(hbp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d ram=%s vram=%s' % (chk['heartbeat_epoch_utc'], free_ram_gb, vram_free))

# ---------- 2) round report line (idempotent guard) ----------
p_rr = bm + r'\logs\iteration-loop\round_reports.md'
rr_body = open(p_rr, 'rb').read()
rr_enc = 'utf-16-le' if rr_body[:2] == b'\xff\xfe' else 'utf-8'
rr_nl = b'\r\x00\n\x00' if rr_enc == 'utf-16-le' else b'\r\n'
rr_txt = rr_body.decode(rr_enc, errors='replace')
already = ('| r958 |' in rr_txt) or ('r958 |' in rr_txt[-3000:])
if already:
    W('round report r958 line already present, skip append')
else:
    line_r = (
        ymd + " " + hm + " | r958 | 恢复线续作轮：①r955 双驱动死亡定谳（patient 01:51:41 rc=128=ssh 连接被远端掐死"
        "（GFW 夜窗巨包 19min 折翼）+salvage 02:25:01 census 相静默死）——两回执停 RUNNING=假活面，进程表+log 尾双验揭穿"
        "（r949 假宣称律第三例）；②关键发现：bigmoney.html blob 已在本地 odb（cat-file 0.3s 零网络直读）→census 先行"
        "（rev-list --missing=print 分块零网络）：2257 缺失路径=331 blob 已本地（6 块）+1926 blob 需 lazy fetch（40 块）；"
        "③v3 分块恢复驱动部署（results/_r958bmb_restore_driver.py·census|run 双模式·50 件/块·420s 树杀软帽·3 连败停）"
        "——即时块 300 件 0.4s/块全部恢复（零网络）→fetch 块在飞（chunk7 rc=255 230s 但 8 件已持久写盘=分块收敛律实证·"
        "禁再走单巨包 all-or-nothing）；④treasure_guard restore 门 rc0 全放行（7 面 reproducible-artifact 级）+"
        "S0.5 轻扫 NO_DELTA（组台账双 hash 未变·r957 消费后 17min）+引擎状态 alive-idle 复核+孤儿探针 14 faces 0 orphans+"
        "r957 push 回执消费 PUSHED_VERIFIED（machine/bm-b-r957 1504047ea217 落地）"
        "| 证据：_r958bmb_census.json+_r958bmb_restore_receipt.json（进度回执）+_r958bmb_restore_driver.log（逐块行）"
        "+_r958bmb_s05_scan.json+_r957bmb_push_receipt.json（PUSHED_VERIFIED）+_orphan_face_probe.bm-b.json"
        "| 诚实跳过：smoke/S6 链/attrition/origin 追平（faces 未齐=v3 driver 在飞·恢复完成包内处理）；fleet/tasks+orders "
        "板面读（盘面缺失 593+213 件·候恢复）；taildrop peer bundle 未到件（inbox 空·fallback 待命）"
        "| WM-VERDICT: red=False（lane healthy·恢复轮豁免面）"
        "| 当前活：v3 恢复驱动 fetch 块在飞（patient）；最近实物：300 件即时恢复（data/faily 面部分+census 工件 04:30）+"
        "恢复驱动 v3；下个里程碑：ALL_RESTORED→smoke 49/49+S6 链+attrition 重扫+origin 追平暖窗（≤24h·驱动收敛 ETA 数小时内）"
        "| 孤儿面=0（14 py_faces 全活·backfill worker own-lane）"
        "| 记账预算: 4/5（S0.5+心跳+state+轮报告）| 产品积分: 1（300 件面恢复+census/驱动工件=文件改动级；"
        "ALL_RESTORED 验收后 S6 链复跑才计 2 分）| 本地未达 origin commit 数=1（C-r958·push driver 在飞·回执=r959）"
        "| [r958 bm-b]"
    )
    if not rr_body.endswith(rr_nl):
        rr_body = rr_body + rr_nl
    open(p_rr, 'wb').write(rr_body + (line_r + '\r\n').encode(rr_enc))
    W('round_reports appended enc=%s' % rr_enc)

# ---------- 3) CODELY law (one entry, <=1.5KB, idempotent guard) ----------
codely_path = bm + r'\CODELY.md'
cbody = open(codely_path, 'rb').read()
ctry = ('r958 判例（双死驱动假 RUNNING 回执）' in cbody.decode('utf-8', errors='replace'))
csz = os.path.getsize(codely_path)
W('CODELY size=%dB guard_hit=%s' % (csz, ctry))
if not ctry:
    line_c = (
        "\n[" + ymd + " " + hm + "] bm-b r958 判例（双死驱动假 RUNNING 回执+census-分块收敛恢复法）："
        "①分离恢复驱动死亡后回执停 RUNNING=假活面（patient 01:51 rc=128 ssh 被远端掐+salvage census 相静默死，"
        "两回执均 RUNNING 停更）——判活一律进程表+log 尾行双验勿信回执（r949 律第三例）；"
        "②blob:none 冷索引恢复正法=census 先行（rev-list --missing=print 分 pathspec 块零网络）→零缺失块即时 checkout "
        "（0.4s/50 件）→需拉块分块 checkout（每块 lazy fetch ~50 blob 小包·r953 树杀软帽）——单块失败仍部分持久"
        "（chunk7 rc=255 但 8 件已落盘=收敛律），禁再走单巨包 all-or-nothing（19min 巨包死证）。"
        "How to apply：恢复驱动回执必带 pid+逐块心跳行；恢复动作前先 census 分块（本机 blob 多有已本地者）。"
    )
    with open(codely_path, 'ab') as f:
        f.write(line_c.encode('utf-8'))
    W('CODELY appended bytes=%d new_size=%dB' % (len(line_c.encode('utf-8')), os.path.getsize(codely_path)))
if os.path.getsize(codely_path) > 51200:
    W('CODELY_SIZE_OVER_50KB -> hot-cold compaction = next round first item')

# ---------- 4) state.json ----------
sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
st['clock_read'] = iso
st['did'] = ("r958: r955 patient/salvage drivers verified DEAD (stale RUNNING receipts; process-table+log audit); "
             "v3 batched restore driver deployed (census: 2257 deleted = 331 blob-local instant + 1926 need lazy "
             "fetch; 300 instant files restored in-round; fetch chunks in flight patient); S0.5 light rescan "
             "NO_DELTA; treasure_guard restore gate rc0; engine alive-idle; orphan probe 14/0; r957 push "
             "receipt consumed PUSHED_VERIFIED machine/bm-b-r957")
st['last_action'] = "r958: restore v3 driver deployment + 300 instant restores + S0.5 NO_DELTA + C-r958 surgery + side-branch push"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = ("results/_r958bmb_restore_driver.py + _r958bmb_census.json (2257 deleted = 331 instant + "
                         "1926 fetch; 300 restored in-round; driver receipt = r959 face)")
st['last_orders_sha_probe'] = s05.get('orders_sha')
st['last_decisions_sha_probe'] = s05.get('decisions_sha')
st['orders_delta_pending'] = False
st['decisions_delta_pending'] = False
st['last_orders_at'] = iso
st['last_decisions_at'] = iso
st['next'] = ("r959: 1) read results/_r958bmb_restore_receipt.json: ALL_RESTORED -> completion package (smoke 49/49 "
             "+ S6 chain + orders full ack diff-scan + attrition rescan + warm-window origin catch-up + side-branch "
             "merges); PARTIAL_CHANNEL_STALLED -> idempotent driver relaunch (partial persistence converges; check "
             "taildrop inbox for peer bundle fallback MSG-20260914-2015); 2) read _r958bmb_push_receipt.json: "
             "PUSHED_VERIFIED -> delivered; else relaunch push driver; 3) engine: monitor backfill_ext_slots worker "
             "settle (own-lane); 4) standing: no rm on repo faces; group-tree zero-touch (origin reads only); "
             "CODELY size check; 5) watermark_red=false maintained")
st['next_milestone'] = ("v3 driver ALL_RESTORED -> smoke+S6+attrition+catch-up package (driver converging ETA hours, "
                        "patient by design); <=24h commitment stands from r957")
st['now_active'] = "r958: v3 restore driver fetch chunks in flight (detached patient) + C-r958 side-branch push driver in flight + engine backfill worker (own-lane)"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r958: probe py_faces=14 orphans=0 (mcp/blender faces + backfill worker + v3 restore "
                          "driver = own-lane legit detached bodies with receipts)")
st['round'] = 958
st['round_no'] = 959
st['round_no_label'] = 'r958'
st['task'] = ("r958: (a) r955 dead-drivers verdict + v3 batched restore driver deployed (census + 300 instant "
              "restores + fetch chunks in flight) (b) S0.5 NO_DELTA + engine verify (c) C-r958 surgery + push")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER-recovering: v3 restore driver in flight (fetch chunks patient; partial-persistence "
                 "convergence proven chunk7 8-files); 300/2257 restored in-round; completion package deferred "
                 "until ALL_RESTORED; zero origin-side loss")
st['sat_engine'] = {"status": "alive (idle, queue_depth 0, heartbeat fresh)", "checked_at": iso}
st['d19_probe_due'] = False
st['d19_probe_due_note'] = "r959: next group probe due within SLA (<=2 rounds from r957 consumption; r958 light rescan NO_DELTA)"
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=958 round_no=959')

# ---------- 5) C-r958 surgery commit ----------
rc, head, _ = run_git(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, base_tree, _ = run_git(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = base_tree.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))
msg_path_c = bm + r'\results\_r958bmb_commitmsg.txt'
open(msg_path_c, 'w', encoding='utf-8').write(
    "round 958: recovery lane - r955 patient/salvage drivers verified DEAD (stale RUNNING receipts; patient "
    "rc=128 ssh drop + salvage census-phase silent death); v3 batched restore driver deployed: census 2257 "
    "deleted = 331 blob-local (300 instant-restored in-round) + 1926 need lazy fetch (40 chunks, fetch in "
    "flight patient, partial-persistence convergence proven); treasure_guard restore gate rc0; S0.5 light "
    "rescan NO_DELTA (ord 6cc07bf4 / dec 6910a9ed); engine alive-idle verified; orphan probe 14 faces 0 "
    "orphans; r957 push receipt consumed PUSHED_VERIFIED machine/bm-b-r957; honest skips: smoke/S6/attrition/"
    "origin-catchup (deferred to ALL_RESTORED package)\n")

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
    ['results', '_r958bmb_restore_driver.py'],
    ['results', '_r958bmb_census.json'],
    ['results', '_r958bmb_restore_receipt.json'],
    ['results', '_r958bmb_restore_driver.log'],
    ['results', '_r958bmb_s05_scan.py'],
    ['results', '_r958bmb_s05_scan.json'],
    ['results', '_r958bmb_closeout.py'],
    ['results', '_r958bmb_commitmsg.txt'],
    ['results', '_orphan_face_probe.bm-b.json'],
]
c8 = surgery(base_tree, changed_c, msg_path_c)
W('C-r958 surgery ok commit=%s (parent %s)' % (c8[:12], head[:12]))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', c8], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], c8[:12], chk.decode().strip() == c8))

# ---------- 6) push driver launch ----------
DRIVER = bm + r'\results\_r958bmb_push_driver.py'
DLOG = bm + r'\results\_r958bmb_push_driver.log'
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
    W('PUSH DRIVER NOT VERIFIED - r959 must relaunch idempotent')

# ---------- 7) final state touch ----------
rc, cnt_out, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], timeout=30)
behind = cnt_out.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r958",
    "c_r958": c8[:12],
    "r957_push": "%s (consumed this round)" % r957_push,
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "behind_origin_main": behind,
    "note": ("C-r958 push in flight (receipt _r958bmb_push_receipt.json = r959 face); origin main catch-up "
             "deferred to warm window post-restore (cold-index pull hazard); v3 restore driver owns the "
             "recovery (fetch chunks patient); saturation engine alive-idle (backfill worker own-lane)"),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('CLOSEOUT_OK c_r958=%s pushdrv_verified=%s behind=%s ram=%s vram=%s r957push=%s s05=%s drv=%s' % (
    c8[:12], drv_started, behind, free_ram_gb, vram_free, r957_push, s05.get('verdict'),
    drv.get('status', 'n/a')))
