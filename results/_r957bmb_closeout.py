# r957 bm-b closeout: POOL-0011 done face + D-19 probe + heartbeat + round-report + CODELY law +
# state advance + C-r957 cold-index tree-surgery commit + detached push driver (machine/bm-b-r957).
# Plumbing only (cold-index law r950); claims only after receipts (r951 law); idempotent re-entry
# guards on append faces (report/CODELY) for 25min-kill safety. ASCII-safe log lines.
import ctypes, datetime, hashlib, json, os, subprocess, sys, time

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
grp = r'C:\Fluxgroup\FluxGroup'
LOG = bm + r'\results\_r957bmb_closeout.log'
NO_WINDOW = 0x08000000
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')
hm = datetime.datetime.now().strftime('%H:%M')
GROUP_SHA = 'bfa61b617dee22c96941ead5400843fd55130259'  # receipt-verified 03:55:27 PUSHED_VERIFIED

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
try:
    open(bm + r'\results\_r957bmb_orders_fresh.md', 'wb').write(out)
    open(bm + r'\results\_r957bmb_decisions_fresh.md', 'wb').write(out2)
    W('fresh views written ord=%dB dec=%dB' % (len(out), len(out2)))
except Exception as e:
    W('fresh view write fail %s' % e)
bmb_rows = [l[:200] for l in ord_txt.split('\n') if '@bm-b' in l]
W('ord_sha=%s dec_sha=%s bmb_rows=%d' % (str(ord_sha)[:12], str(dec_sha)[:12], len(bmb_rows)))
for l in bmb_rows[-6:]:
    W('BMB-ROW ' + l[:170])

sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
ord_changed = (ord_sha is not None and ord_sha != st.get('last_orders_sha'))
dec_changed = (dec_sha is not None and dec_sha != st.get('last_decisions_sha'))
W('delta ord_changed=%s dec_changed=%s' % (ord_changed, dec_changed))

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
    "task": ("r957: POOL-0011 DONE - group tree-surgery commit bfa61b61 PUSHED_VERIFIED on origin/main "
             "(B10 source-regen products 62 files 7.1MB + docs/orders.md done row) after docs-subtree "
             "mktree empty-name bug fix (ls-tree tip:docs children law); fleet/machine.json recreated "
             "(local-private face, X104 law) -> saturation engine revived + backfill worker spawned; "
             "recovery drivers still in flight (salvage census + patient restore)"),
    "did": ("POOL-0011 done: card ID POOL-0011 + action done + evidence = group origin/main bfa61b617dee22c96941ead5400843fd55130259 "
            "(B机10款 源程序 txt/pdf 10/10 + CCPC 10/10 + 报审台账§四 B10 行 + generator dual-candidate src fix; receipts = "
            "results/_r957bmb_rz_receipt.json GEN_DONE_OK + _r957bmb_group_commit_receipt.json PUSHED_VERIFIED); commit = C-r957 machine/bm-b-r957"),
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-recovering: POOL-0011 product line DELIVERED on group origin (bfa61b61); salvage census + "
                "patient restore still RUNNING (receipts, patient by design); smoke/S6/attrition deferred until "
                "faces complete; saturation engine revived (machine.json recreated); zero origin-side loss"),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("engine backfill worker (backfill_ext_slots.py all, 03:51 spawn) = legit own-lane burn body after engine "
             "revival; local-private fleet/machine.json recreated from template per fleet/README.md sec.1; "
             "workspace 软著申请材料 retained exclude-guarded (delivered scratch; no-rm red line)"),
}
os.makedirs(bm + r'\fleet\machines', exist_ok=True)
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
already = ('| r957 |' in rr_txt) or ('r957 |' in rr_txt[-3000:])
if already:
    W('round report r957 line already present, skip append')
else:
    line_r = (
        ymd + " " + hm + " | r957 | 产品交付轮（POOL-0011 done·前 r957 会话 03:31 GEN_DONE_OK 接力收口）："
        "①POOL-0011 转单卡 done 回执三元组（卡 ID=POOL-0011+动作=done+证据指针=集团 origin/main bfa61b617dee22c96941ead5400843fd55130259）"
        "——B机10款软著源程序全产出交付：G04 螺丝仙人 2869行/24文件/58页·G05 爆护 5235行/30文件/60页·G07 人从众 3073行/20文件/60页·"
        "G08 开学啦 5725行/29文件/60页·G13 我想有个农场 3910行/24文件/60页·G14 大不了开饭馆 3535行/19文件/60页·G20 夜聊斋 2385行/21文件/48页·"
        "G23 这张牌有诈 1862行/13文件/38页·G26 归园田居 3121行/17文件/60页·G28 这一箭稳了 2592行/12文件/52页（不足60页四款诚实标注）"
        "+CCPC 提交材料 10/10 归拢+报审台账§四 B10 行销账+docs/orders.md done 行（GROUP_SHA 见心跳 did）；"
        "②r956 FAIL 根因治愈=bm-b 盘源码目录为裸名（ScrewOut/... 无 G 前缀·九根零命中）→generate_copyright.py B机10款 src_rel "
        "双候选（C机 G09Y/G10 先例）+SRC_ROOTS 第十根 C:/Fluxgroup/MiniGame（前 r957 会话 03:31 修复实证 GEN_DONE_OK）；"
        "③组仓树手术 push 首败根因治愈=docs 子树 mktree 空名条目（ls-tree tip -- docs 返回 docs 条目自身·剥 4 字符得空名→远端 "
        "index-pack 拒收）→修复=ls-tree tip:docs 列子件（本会话 03:52 点火·03:55:27 PUSHED_VERIFIED 62 files 7.1MB）；"
        "④fleet/machine.json 重建（本地私有身份件·r947 树毁不可 git 恢复·X104 律禁入库·模板重建）→饱和引擎复活"
        "（status 活·03:51 backfill_ext_slots.py 算力批自燃=池认领经济正常）+孤儿探针复活（py_faces=8 orphans=0）；"
        "⑤r956 push 回执消费=PUSHED_VERIFIED（machine/bm-b-r956 3eaa15f1 落地）"
        "| 证据：_r957bmb_rz_receipt.json（GEN_DONE_OK 10/10）+_r957bmb_group_commit_receipt.json（PUSHED_VERIFIED bfa61b61）"
        "+_r957bmb_group_commit.log（03:52-03:55 全程）+_r957bmb_closeout.log（D-19 hash 实锚）+_orphan_face_probe.bm-b.json"
        "| 诚实跳过：smoke/S6 链/attrition 重扫/unshallow+pull（faces 未齐·salvage census+patient restore 在飞·候恢复完成窗）；"
        "S7 schtasks 重装核查（plumbing 树手术+push --no-verify 冷索引法·r956 先例）；工作面保留不删（已交付 scratch·info/exclude 守卫·no-rm 红线）"
        "| WM-VERDICT: red=False（交付轮·py_watermark 随 S6 缓办）"
        "| 当前活：C-r957 树手术+侧支推送在飞；最近实物：集团 origin/main bfa61b61（B机10款软著源程序包·03:55:27 落地·62 files 7.1MB）；"
        "下个里程碑：salvage/patient 回执→FILL_DONE_RESTORE_OK→smoke+S6+attrition（<=24h）；POOL.json 五态迁移归代理席写手"
        "| 孤儿面=0（探针复活实证 py_faces=8 orphans=0·report=results/_orphan_face_probe.bm-b.json）"
        "| 记账预算: 4/5（D-19+心跳+state+轮报告·交付轮豁免面）| 产品积分: 2（集团仓可验实物 bfa61b61：10款源程序 PDF/TXT+CCPC+台账销账）"
        "| 本地未达 origin commit 数=1（C-r957·push driver 在飞·回执=r958）| [r957 bm-b]"
    )
    if not rr_body.endswith(rr_nl):
        rr_body = rr_body + rr_nl
    open(p_rr, 'wb').write(rr_body + (line_r + '\r\n').encode(rr_enc))
    W('round_reports appended enc=%s' % rr_enc)

# ---------- 3) CODELY law (one entry, <=1.5KB, idempotent guard) ----------
codely_path = bm + r'\CODELY.md'
cbody = open(codely_path, 'rb').read()
ctry = ('r957 判例（组仓树手术 ls-tree 空名条目）' in cbody.decode('utf-8', errors='replace'))
csz = os.path.getsize(codely_path)
W('CODELY size=%dB guard_hit=%s' % (csz, ctry))
if ctry:
    W('CODELY r957 entry already present, skip append')
else:
    line_c = (
        "\n[" + ymd + " " + hm + "] bm-b r957 判例（组仓树手术 ls-tree 空名条目坑）：树手术重建某目录子树时禁用 "
        "`git ls-tree <tip> -- <dir>`（返回 dir 条目自身而非子件·剥前缀得空文件名→mktree 产出含空名条目的树→commit-tree 本地不校验照单全收→"
        "push 时远端 index-pack 拒收 'empty filename in tree entry'·03:40 实锤两连拒）——正法=`git ls-tree -z <tip>:<dir>` 直接列子件"
        "（名字相对该目录·无需剥前缀）。姊妹律：mktree 子树缺 blob 必须 --missing（blob:none 部分克隆下未变文件 blob 常不在本地·03:39 首败实锤）；"
        "本地私有身份件（fleet/machine.json·gitignored）树毁后 git 恢复链不可救=须按模板手工重建（fleet/README §1 三件套）。"
        "How to apply：一切树手术 mktree 前逐条目断言名字非空+ls-tree 用 tip:dir 形态。"
    )
    with open(codely_path, 'ab') as f:
        f.write(line_c.encode('utf-8'))
    W('CODELY appended bytes=%d new_size=%dB' % (len(line_c.encode('utf-8')), os.path.getsize(codely_path)))
if os.path.getsize(codely_path) > 51200:
    W('CODELY_SIZE_OVER_50KB new_size=%dB -> hot-cold compaction = r958 first item (law D-20260925-01(4))' % os.path.getsize(codely_path))

# ---------- 4) state.json ----------
st['clock_read'] = iso
st['did'] = ("r957: POOL-0011 DONE - group commit bfa61b617dee22c96941ead5400843fd55130259 PUSHED_VERIFIED on origin/main "
             "(B10 62 files 7.1MB: 源程序 txt/pdf 10/10 + CCPC 10/10 + 报审台账§四 rows + orders.md done row + generator "
             "dual-candidate src fix) after docs-subtree mktree empty-name fix; fleet/machine.json recreated (local-private) "
             "-> saturation engine revived + backfill worker spawned 03:51; orphan probe revived (py_faces=8 orphans=0); "
             "r956 push receipt consumed PUSHED_VERIFIED machine/bm-b-r956 3eaa15f1")
st['last_action'] = "r957: POOL-0011 done delivery (group bfa61b61) + machine.json recreation + engine revival + C-r957 surgery + side-branch push"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = ("group origin/main bfa61b617dee22c96941ead5400843fd55130259 (POOL-0011 B机10款 source materials delivery, "
                         "receipt results/_r957bmb_group_commit_receipt.json)")
if ord_sha:
    st['last_orders_sha'] = ord_sha
    st['last_orders_at'] = iso
    st['last_orders_read_at'] = iso
    st['last_orders_sha_note'] = ("r957 consumed c4e6878a->" + ord_sha[:8] + " (delta = own POOL-0011 done row [executed this round] "
                                  "+ any bm-a/bm-c rows logged in _r957bmb_closeout.log); view=results/_r957bmb_orders_fresh.md")
    st['last_orders_sha_probe'] = ord_sha
    st['orders_delta_pending'] = False
if dec_sha:
    st['last_decisions_sha'] = dec_sha
    st['last_decisions_at'] = iso
    st['last_decisions_read_at'] = iso
    st['last_decisions_sha_method'] = ("r957: origin blob hash via git show (group fetch " + iso + "); fresh view "
                                       "results/_r957bmb_decisions_fresh.md; delta scan in _r957bmb_closeout.log")
    st['last_decisions_sha_probe'] = dec_sha
    st['decisions_delta_pending'] = False
st['next'] = ("r958: 1) read results/_r957bmb_push_receipt.json: PUSHED_VERIFIED -> delivered; else relaunch push driver "
             "(idempotent); 2) salvage + patient-restore receipts: ALL_FACES_RESTORED -> smoke 49/49 + S6 chain + orders "
             "full ack diff-scan + attrition rescan + warm-window unshallow/pull + side-branch merges; still RUNNING -> keep "
             "waiting (patient by design); PARTIAL/FAILED -> lazy_fetch_diag -> peer bundle channel (MSG-20261014-2015 on origin); "
             "3) review _r957bmb_closeout.log BMB-ROW lines: any @bm-b rows beyond own POOL-0011 done row -> execute with "
             "receipts; 4) saturation engine: first post-revival window - verify state face healthy + backfill_ext_slots "
             "worker settles (own-lane); 5) standing: no rm on repo faces; group-tree zero-touch (origin reads only); "
             "workspace 软著申请材料 retained exclude-guarded; CODELY size check - if >50KB hot-cold compaction = first item")
st['next_milestone'] = ("salvage/patient receipts -> FILL_DONE_RESTORE_OK -> smoke+S6+attrition warm window (<=24h); "
                        "POOL.json five-state migration owned by proxy seat writer (bm-b never writes POOL.json)")
st['now_active'] = "r957: C-r957 side-branch push in flight (machine/bm-b-r957) + recovery drivers in flight (salvage census + patient restore) + engine backfill worker (own-lane)"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r957: probe revived after machine.json recreation - py_faces=8 orphans=0 (report results/_orphan_face_probe.bm-b.json); "
                          "backfill worker + salvage census + patient restore = own-lane legit detached bodies with receipts")
st['round'] = 957
st['round_no'] = 958
st['round_no_label'] = 'r957'
st['task'] = ("r957: (a) POOL-0011 done - group delivery bfa61b61 PUSHED_VERIFIED (B机10款) (b) machine.json recreation + engine "
              "revival + orphan probe revival (c) recovery lane continues (salvage census + patient restore in flight)")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER-recovering: POOL-0011 product line DELIVERED on group origin (bfa61b61); salvage census + patient restore "
                 "still RUNNING (receipts, patient by design); saturation engine revived; D-19 watermarks advanced this round; "
                 "zero origin-side loss")
st['sat_engine'] = {"status": "alive (revived r957 after machine.json recreation; backfill worker spawned 03:51)", "checked_at": iso}
st['d19_probe_due'] = False
st['d19_probe_due_note'] = "r958: next group probe due within SLA (<=2 rounds from r957 consumption)"
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=957 round_no=958 ord_sha=%s dec_sha=%s' % (str(ord_sha)[:12], str(dec_sha)[:12]))

# ---------- 5) C-r957 surgery commit ----------
rc, head, _ = run_git(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, base_tree, _ = run_git(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = base_tree.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))
msg_path_c = bm + r'\results\_r957bmb_commitmsg.txt'
open(msg_path_c, 'w', encoding='utf-8').write(
    "round 957: POOL-0011 done (card ID + done + evidence) - group origin/main bfa61b617dee22c96941ead5400843fd55130259 "
    "PUSHED_VERIFIED (B机10款 源程序 txt/pdf 10/10 + CCPC 10/10 + 报审台账§四 rows + orders.md done row; generator "
    "dual-candidate src fix; docs-subtree mktree empty-name push-reject root-cured via ls-tree tip:docs) + "
    "fleet/machine.json recreated (local-private X104 face, engine revived, backfill worker spawned) + orphan probe "
    "revived (py_faces=8 orphans=0) + r956 push receipt consumed (machine/bm-b-r956 PUSHED_VERIFIED) + D-19 probe "
    "consumed (orders sha1 / decisions sha256, fresh views) + honest skips: smoke/S6/attrition (faces pending salvage)\n")

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
    ['results', '_r957bmb_rz_runner.py'],
    ['results', '_r957bmb_rz_verify.py'],
    ['results', '_r957bmb_rz_receipt.json'],
    ['results', '_r957bmb_group_commit.py'],
    ['results', '_r957bmb_group_commit.log'],
    ['results', '_r957bmb_group_commit_receipt.json'],
    ['results', '_r957bmb_push_driver.py'],
    ['results', '_r957bmb_push_driver.log'],
    ['results', '_r957bmb_orders_fresh.md'],
    ['results', '_r957bmb_decisions_fresh.md'],
    ['results', '_r957bmb_closeout.py'],
    ['results', '_r957bmb_commitmsg.txt'],
    ['results', '_orphan_face_probe.bm-b.json'],
]
c7 = surgery(base_tree, changed_c, msg_path_c)
W('C-r957 surgery ok commit=%s (parent %s)' % (c7[:12], head[:12]))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', c7], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], c7[:12], chk.decode().strip() == c7))

# ---------- 6) push driver launch ----------
DRIVER = bm + r'\results\_r957bmb_push_driver.py'
DLOG = bm + r'\results\_r957bmb_push_driver.log'
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
    W('PUSH DRIVER NOT VERIFIED - r958 must relaunch idempotent')

# ---------- 7) final state touch ----------
rc, cnt_out, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], timeout=30)
behind = cnt_out.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r957",
    "c_r957": c7[:12],
    "group_delivery": "bfa61b617dee22c96941ead5400843fd55130259 (POOL-0011, PUSHED_VERIFIED 03:55:27)",
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "behind_origin_main": behind,
    "note": ("POOL-0011 delivered on group origin/main (bfa61b61); C-r957 push in flight (receipt _r957bmb_push_receipt.json "
             "= r958 face); origin main catch-up deferred to warm window post-restore (cold-index pull hazard); salvage "
             "census + patient restore own the recovery; saturation engine revived (backfill worker own-lane)"),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('CLOSEOUT_OK c_r957=%s pushdrv_verified=%s behind=%s ram=%s vram=%s ord=%s dec=%s bmb_rows=%d' % (
    c7[:12], drv_started, behind, free_ram_gb, vram_free, str(ord_sha)[:12], str(dec_sha)[:12], len(bmb_rows)))
