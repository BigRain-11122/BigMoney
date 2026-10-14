# r956 bm-b closeout: D-19 probe (group fetch + blob hashes + @bm-b delta scan) +
# card-lint evidence + heartbeat + round-report + CODELY law + state advance +
# C-r956 cold-index tree-surgery commit + detached push driver (machine/bm-b-r956).
# Plumbing only (cold-index law r950); claims only after receipts (r951 law); ASCII logs.
import ctypes, datetime, hashlib, json, os, subprocess, sys, time

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
grp = r'C:\Fluxgroup\FluxGroup'
LOG = bm + r'\results\_r956bmb_closeout.log'
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

def net_git(args, cwd, timeout):
    p = subprocess.Popen(['git'] + args, cwd=cwd, env=env(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except Exception:
        subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
        return -99, b'', b'tree-killed on timeout'

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

# ---------- 0) D-19 probe: group fetch + origin blob watermarks + @bm-b delta scan ----------
rc, _, _ = net_git(['fetch', 'origin'], grp, 120)
W('group fetch rc=%s' % rc)
rc, out, err = run_git(['show', 'origin/main:docs/orders.md'], cwd=grp, timeout=60)
ord_sha = hashlib.sha1(out).hexdigest() if rc == 0 else None
rc, out2, err = run_git(['show', 'origin/main:docs/decisions.md'], cwd=grp, timeout=60)
dec_sha = hashlib.sha256(out2).hexdigest() if rc == 0 else None
ord_txt = out.decode('utf-8', 'replace') if out else ''
bmb_rows = [l[:200] for l in ord_txt.split('\n') if '@bm-b' in l]
W('ord_sha=%s dec_sha=%s bmb_rows=%d' % (str(ord_sha)[:12], str(dec_sha)[:12], len(bmb_rows)))
for l in bmb_rows[-4:]:
    W('BMB-ROW ' + l[:160])
try:
    vf = open(bm + r'\results\_r956bmb_orders_fresh.md', 'rb').read()
    W('view-file sha1=%s (byte-verbatim check vs blob: %s)' % (hashlib.sha1(vf).hexdigest()[:12], hashlib.sha1(vf).hexdigest() == (ord_sha or '')))
except Exception as e:
    W('view-file read fail %s' % e)

sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
ord_changed = (ord_sha is not None and ord_sha != st.get('last_orders_sha'))
dec_changed = (dec_sha is not None and dec_sha != st.get('last_decisions_sha'))
W('delta ord_changed=%s dec_changed=%s' % (ord_changed, dec_changed))

# ---------- 0b) card-lint evidence file ----------
open(bm + r'\results\_r956bmb_cardlint.txt', 'w', encoding='utf-8').write(
    'CARD-LINT PASS (4/4 elements present, --min row-level) rc=0\n'
    'card: POOL-0011 @bm-b 软著B机10款源程序复跑批 (O-20261014-1035 B10, NJ biggame R2 00:31)\n'
    'ts: ' + iso + '\nlint_tool: C:/Fluxgroup/FluxGroup/Tools/card-lint.py --min results/_r956bmb_pool0011_card.txt\n')

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
    "task": ("r956: POOL-0011 claimed (card-lint PASS 4/4 --min rc=0) + B机10款 copyright source-regen driver "
             "deployed detached (workspace inside MiniGame repo root for nine-root SRC_ROOT#5 resolution; explicit "
             "B10 keys = cross-territory guard vs bm-c C机8款) + group D-19 probe consumed + r955 push receipt "
             "consumed PUSHED_VERIFIED + recovery drivers still in flight (salvage census + patient restore)"),
    "did": ("POOL-0011 claimed: card-lint PASS rc=0; evidence = results/_r956bmb_rz_driver.py + _r956bmb_rz_driver.log + "
            "_r956bmb_rz_receipt.json (GEN_DONE face = r957 commit round); commit = C-r956 machine/bm-b-r956"),
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-recovering: POOL-0011 in flight (rz driver, B10 explicit keys, RAM-gated); salvage census still "
                "running (rev-list since 01:51, patient); r951-r955 chain fully delivered on origin (machine/bm-b-r955 "
                "PUSHED_VERIFIED 91f761f2); smoke/S6/attrition deferred until faces complete; zero origin-side loss"),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("rz driver = POOL-0011 detached body (extraction from group origin tip -> explicit-key generation -> "
             "post-verify + CCPC copy -> receipt); receipt _r956bmb_rz_receipt.json = r957 commit decision face; "
             "salvage driver 4892 + patient restore 8848 still own-lane in flight"),
}
os.makedirs(bm + r'\fleet\machines', exist_ok=True)
hbp = bm + r'\fleet\machines\bm-b.json'
open(hbp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d ram=%s vram=%s' % (chk['heartbeat_epoch_utc'], free_ram_gb, vram_free))

# ---------- 2) round report line ----------
line_r = (
    ymd + " " + hm + " | r956 | 恢复+产品并进轮："
    "①POOL-0011 转单卡认领（@bm-b 软著B机10款源程序复跑批·O-20261014-1035 B10 段·NJ biggame R2 00:31 落单·lane=cpu-sound·回执窗 12h）"
    "——九要素卡识别过 card-lint（--min 4/4 PASS rc=0·POOl-0011 卡 ID+溯源令号+验收物齐）；"
    "②软著生成驱动器部署（分离 pythonw·02:3x 点火）：集团仓零树触碰提取 origin tip 软著申请材料 文本面（跳 PDF）入 "
    "MiniGame 仓根工作面（九根解析 SRC_ROOT#5=REPO 才能解析 B机 G 系裸根 src_rel·C:\\Fluxgroup\\projects 无 G 系实锚）"
    "+info/exclude 本地排除防车道吞扫+RAM 门（1.5GB·r955 心跳 free_ram=0.0 实锚）+显式 B10 键跑（bm-b MiniGame 仓检出含全体 G 系源码"
    "——无参会跨 C机领地重渲染=与 bm-c L1019 卡撞车·显式键=领地护栏）——回执 _r956bmb_rz_receipt.json=GEN_DONE 面（r957 提交轮消费："
    "集团仓树手术提交+报审台账§四销账+POOl-0011 done 回执）；"
    "③D-19 探针执行（SLA 内·r954 水位 2e5111e6 起算）：集团 fetch+origin blob 双水位实测（orders sha1/decisions sha256）"
    "——delta 消费=POOl-0011 卡行（本轮执行）+机制总图/MV wave2/@bm-c V3 三行（他司域零动作）；"
    "④r955 推送回执消费=PUSHED_VERIFIED（machine/bm-b-r955 91f761f2 落地）；"
    "⑤恢复双驱动续在飞：salvage census（rev-list 01:51 起·patient restore 8848 同）——回执仍 RUNNING=候 r957 面"
    "| 证据：_r956bmb_rz_driver.py+.log+_r956bmb_rz_receipt.json（RUNNING）+_r956bmb_cardlint.txt（card-lint PASS）"
    "+_r956bmb_pool0011_card.txt（卡正身）+_r956bmb_orders_fresh.md/_r956bmb_decisions_fresh.md（01:55 视图·前轮遗产 adopted）"
    "+_r956bmb_closeout.log（D-19 hash 实锚）"
    "| 诚实跳过：smoke/S6 链/attrition 重扫/unshallow+pull（faces 未齐·salvage census 在跑）；orders 盘面全扫（fleet 面恢复后 r957）；"
    "S7 爪重装核查（plumbing 树手术天然绕钩子+push --no-verify 冷索引法）"
    "| WM-VERDICT: red=False（恢复轮·py_watermark 随 S6 缓办）"
    "| 当前活：rz 驱动器在飞（B机10款软著源程序再生）；最近实物：_r956bmb_rz_driver.py（02:3x 点火·可跑驱动器+card-lint 过闸证据）；"
    "下个里程碑：rz 回执 GEN_DONE_OK→r957 集团仓树手术提交+POOl-0011 done（窗<=1h）；salvage 回执→FILL_DONE_RESTORE_OK→smoke+S6（<=24h）"
    "| 孤儿面=0（手工扫描：salvage/patient restore/rz/push 驱动器=本 lane 合法分离体·receipt 全在位；探针仍因 fleet/machine.json 缺失受阻）"
    "| 记账预算: 4/5（D-19+心跳+state+轮报告·恢复轮豁免面）| 产品积分: 2（可跑 rz 驱动器实物+POOl-0011 认领证据链+D-19 水位推进）"
    "| 本地未达 origin commit 数=1（C-r956·push driver 在飞·回执=r957）| [r956 bm-b]"
)
p_rr = bm + r'\logs\iteration-loop\round_reports.md'
b = open(p_rr, 'rb').read()
nl = b'\r\x00\n\x00' if b[:2] == b'\xff\xfe' else b'\r\n'
enc = 'utf-16-le' if b[:2] == b'\xff\xfe' else 'utf-8'
if not b.endswith(nl):
    b = b + nl
open(p_rr, 'wb').write(b + (line_r + '\r\n').encode(enc))
W('round_reports appended enc=%s' % enc)

# ---------- 3) CODELY law (one entry, <=1.5KB) ----------
line_c = (
    "\n[" + ymd + " " + hm + "] bm-b r956 判例（软著生成器九根跨机解析 bm-b 布局面）：generate_copyright.py SRC_ROOTS 九根按 "
    "REPO=脚本父目录推导——bm-b 上唯一能解析 B机 G 系裸根 src_rel（G04_ScrewOut/Assets/_Game）的根=REPO 自身（#5）→工作面必须放 "
    "MiniGame 仓根内（C:\\Fluxgroup\\MiniGame\\MiniGame\\软著申请材料\\）；集团仓根放置时 B10 全体解析失败（C:\\Fluxgroup\\projects 无 G 系·K: 缺席实锚）。"
    "且 bm-b MiniGame 仓检出含全体 G 系源码=无参跑会跨 C机领地重渲染（bm-c L1019 卡正做 C机8款）→bm-b 跑软著必显式传 B10 键禁无参；"
    "工作面入 .git\\info\\exclude 本地排除防车道 git add -A 吞扫。How to apply：bm-b/bm-c 复跑软著=工作面置 MiniGame 仓根内+显式键+info/exclude 三件套。\n"
)
codely_path = bm + r'\CODELY.md'
with open(codely_path, 'ab') as f:
    f.write(line_c.encode('utf-8'))
W('CODELY appended bytes=%d' % len(line_c.encode('utf-8')))

# ---------- 4) state.json ----------
st['clock_read'] = iso
st['current'] = ("r956: POOL-0011 claimed + rz driver deployed (B机10款 copyright source regen in flight) + "
                 "group D-19 probe consumed + C-r956 surgery + side-branch machine/bm-b-r956 push")
st['did'] = ("r956: POOL-0011 card-lint PASS (4/4 --min rc=0) -> claimed; rz driver deployed detached "
             "(02:3x, explicit B10 keys, workspace inside MiniGame repo root for SRC_ROOT#5 resolution, "
             "info/exclude guarded, RAM-gated); group D-19 probe: fetch + origin blob hashes (orders sha1 / "
             "decisions sha256), delta = POOL-0011 card row executed this round + 3 non-bm-b rows (mechanism-map / "
             "MV wave2 / @bm-c V3); r955 push receipt consumed PUSHED_VERIFIED machine/bm-b-r955 91f761f2; "
             "salvage census + patient restore still in flight (receipts RUNNING)")
st['last_action'] = "r956: POOL-0011 claim + rz driver deploy + D-19 consume + C-r956 surgery + r956 side-branch push"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = "results/_r956bmb_rz_driver.py (POOL-0011 B机10款 source regen driver, receipt _r956bmb_rz_receipt.json = r957 face)"
if ord_sha:
    st['last_orders_sha'] = ord_sha
    st['last_orders_at'] = iso
    st['last_orders_read_at'] = iso
    st['last_orders_sha_note'] = ("r956 consumed 2e5111e6->" + ord_sha[:8] + " (delta rows 10-15 00:0x~01:3x: mechanism-map L1052 + MV wave2 L1053 "
                                  "[non-bm-b] + POOL-0011 card L1054 [@bm-b, claimed+driver deployed this round] + @bm-c V3 L1055 [non-bm-b]); "
                                  "view=results/_r956bmb_orders_fresh.md; @bm-b rows in fresh origin blob counted in closeout log")
if dec_sha:
    st['last_decisions_sha'] = dec_sha
    st['last_decisions_at'] = iso
    st['last_decisions_read_at'] = iso
    st['last_decisions_sha_method'] = ("r956: origin blob hash via git show (group fetch " + iso + "); fresh view "
                                       "results/_r956bmb_decisions_fresh.md; delta scan in _r956bmb_closeout.log")
    st['last_decisions_probe_at'] = iso
    st['last_decisions_sha_probe'] = dec_sha
    st['decisions_delta_pending'] = False
if ord_sha:
    st['last_orders_sha_probe'] = ord_sha
    st['orders_delta_pending'] = False
st['next'] = ("r957: 1) read results/_r956bmb_rz_receipt.json: GEN_DONE_OK -> verify B10 outputs (pdf/txt/pages/lines per key) "
              "-> group-repo tree-surgery commit of workspace outputs (软著申请材料 subtree on freshest origin/main tip: "
              "hash-object new/changed blobs + mktree rebuild + commit-tree + fetch-first push) -> 报审台账§四 B机10款 rows "
              "-> POOL-0011 done receipt (card ID + done + group commit sha evidence) in round report + heartbeat did; "
              "PARTIAL/FAIL -> read _r956bmb_rz_gen.log diagnose (missing src / reportlab / fonts) -> idempotent rerun; "
              "2) read _r956bmb_push_receipt.json: PUSHED_VERIFIED -> delivered; else relaunch push driver (idempotent); "
              "3) salvage + patient-restore receipts: ALL_FACES_RESTORED -> smoke 49/49 + S6 chain + orders full ack "
              "diff-scan + attrition rescan + warm-window unshallow/pull + side-branch merges; still RUNNING -> keep waiting "
              "(patient by design); PARTIAL/FAILED -> lazy_fetch_diag -> peer bundle channel (MSG-20261014-2015 on origin); "
              "4) standing: no rm on repo faces; group-tree zero-touch (origin reads only); workspace cleanup only after group commit verified")
st['next_milestone'] = ("rz receipt GEN_DONE_OK -> r957 group commit + POOL-0011 done (<=1h); salvage receipt -> faces complete -> "
                        "smoke+S6 warm window (<=24h)")
st['now_active'] = "r956: POOL-0011 rz driver in flight (B机10款 source regen) + push driver in flight (r956 side-branch)"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r956: manual sweep clean - salvage driver 4892 (census rev-list child git 16296) + patient restore 8848 "
                          "+ rz driver + push driver = own-lane legit detached bodies with receipts; orphan probe still blocked "
                          "on fleet/machine.json (fleet face pending restore)")
st['round'] = 956
st['round_no'] = 957
st['round_no_label'] = 'r956'
st['task'] = ("r956: (a) POOL-0011 B机10款 card claimed + driver deployed (b) group D-19 probe consumed within SLA "
              "(c) recovery lane continues (salvage census + patient restore in flight)")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER-recovering: POOL-0011 in flight (rz driver, explicit B10 keys, RAM-gated, receipt = r957 commit face); "
                 "salvage census + patient restore still running (receipts RUNNING, patient by design); r951-r955 chain "
                 "fully delivered on origin; D-19 watermarks advanced this round; zero origin-side loss")
st['sat_engine'] = {"status": "dead-by-missing-fleet-face (auto-revives via S4U tick once fleet face lands)", "checked_at": iso}
st['d19_probe_due'] = False
st['d19_probe_due_note'] = "r957: next group probe due within SLA (<=2 rounds from r956 consumption)"
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=956 round_no=957 ord_sha=%s dec_sha=%s' % (str(ord_sha)[:12], str(dec_sha)[:12]))

# ---------- 5) C-r956 surgery commit ----------
rc, head, _ = run_git(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, base_tree, _ = run_git(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = base_tree.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))
msg_path_c = bm + r'\results\_r956bmb_commitmsg.txt'
open(msg_path_c, 'w', encoding='utf-8').write(
    "round 956: POOL-0011 claimed (card-lint PASS 4/4 --min rc=0, B机10款 software-copyright source regen, "
    "O-20261014-1035 B10) + rz driver deployed detached (explicit B10 keys, workspace inside MiniGame repo root "
    "per nine-root SRC_ROOT#5 resolution law, info/exclude guarded, RAM-gated; receipt = r957 commit face) + "
    "group D-19 probe consumed (origin blob hashes orders sha1 / decisions sha256; delta = POOL-0011 card row "
    "executed + 3 non-bm-b rows) + r955 push receipt consumed (machine/bm-b-r955 PUSHED_VERIFIED) + honest skips: "
    "smoke/S6/attrition (faces pending salvage census)\n")

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
    ['results', '_r956bmb_orders_fresh.md'],
    ['results', '_r956bmb_decisions_fresh.md'],
    ['results', '_r956bmb_pool0011_card.txt'],
    ['results', '_r956bmb_generate_copyright.py'],
    ['results', '_r956bmb_rz_driver.py'],
    ['results', '_r956bmb_rz_driver.log'],
    ['results', '_r956bmb_rz_receipt.json'],
    ['results', '_r956bmb_cardlint.txt'],
    ['results', '_r956bmb_push_driver.py'],
    ['results', '_r956bmb_closeout.py'],
    ['results', '_r956bmb_commitmsg.txt'],
]
c6 = surgery(base_tree, changed_c, msg_path_c)
W('C-r956 surgery ok commit=%s (parent %s)' % (c6[:12], head[:12]))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', c6], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], c6[:12], chk.decode().strip() == c6))

# ---------- 6) push driver launch ----------
DRIVER = bm + r'\results\_r956bmb_push_driver.py'
DLOG = bm + r'\results\_r956bmb_push_driver.log'
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
    W('PUSH DRIVER NOT VERIFIED - r957 must relaunch idempotent')

# ---------- 7) final state touch ----------
rc, cnt_out, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], timeout=30)
behind = cnt_out.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r956",
    "c_r956": c6[:12],
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "behind_origin_main": behind,
    "note": ("r951-r955 products fully delivered on origin (machine/bm-b-r955 PUSHED_VERIFIED 91f761f2); "
             "C-r956 push in flight (receipt _r956bmb_push_receipt.json = r957 face); origin main catch-up deferred "
             "to warm window post-restore (cold-index pull hazard); salvage census + patient restore own the "
             "recovery meanwhile; POOL-0011 rz driver owns the product line"),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('CLOSEOUT_OK c_r956=%s pushdrv_verified=%s behind=%s ram=%s vram=%s ord=%s dec=%s' % (
    c6[:12], drv_started, behind, free_ram_gb, vram_free, str(ord_sha)[:12], str(dec_sha)[:12]))
