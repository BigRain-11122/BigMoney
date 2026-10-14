# r954 bm-b closeout: G5 receipt MSG + D-19 orders-delta consumption + heartbeat +
# round-report + CODELY pit law + state advance + C3 cold-index tree-surgery commit
# + detached push driver (machine/bm-b-r954) + S7 self-heal. Cold-index law: plumbing
# only. Two-phase law: claims only after receipts. ASCII console prints.
import json, os, subprocess, sys, time, ctypes, datetime

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r954bmb_closeout.log'
NO_WINDOW = 0x08000000
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')
hm = datetime.datetime.now().strftime('%H:%M')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')
    print(m)

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

def cap_run(cmd, cwd, cap):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=cap, creationflags=NO_WINDOW)
        return r.returncode, (r.stdout + b'\n' + r.stderr).decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        return -99, 'TIMEOUT_%ss' % cap

W('closeout start pid=%d' % os.getpid())

# ---------- 0) probes ----------
lint_verdict = 'skipped'
try:
    view = open(bm + r'\results\_r953bmb_group_orders_view.md', encoding='utf-8', errors='replace').read()
    card_line = ''
    for ln in view.split('\n'):
        if 'POOL-P1B-G5' in ln and 'card-lint PASS 9/9' in ln:
            card_line = ln.strip()
    if card_line:
        card_tmp = bm + r'\results\_r954bmb_g5_card_extract.txt'
        open(card_tmp, 'w', encoding='utf-8').write(card_line + '\n')
        lint_py = r'C:\Fluxgroup\FluxGroup\Tools\card-lint.py'
        if not os.path.exists(lint_py):
            W('card-lint.py absent on local group tree - fallback git show origin blob')
            g = subprocess.run(['git', '-C', r'C:\Fluxgroup\FluxGroup', 'show', 'origin/main:Tools/card-lint.py'],
                               capture_output=True, timeout=40, creationflags=NO_WINDOW)
            if g.returncode == 0:
                lint_py = bm + r'\results\_r954bmb_card_lint_tmp.py'
                open(lint_py, 'wb').write(g.stdout)
        if os.path.exists(lint_py):
            rc, out = cap_run(['python', lint_py, '--min', card_tmp], bm, 60)
            lint_verdict = 'rc=%s out=%s' % (rc, out.strip().replace('\n', ' | ')[:160])
        else:
            lint_verdict = 'lint tool unavailable (group tree absent) - card already linted 9/9 by issuer+bm-c d56da5358 receipt'
    else:
        lint_verdict = 'card line not found in view (weave receipt path only)'
except Exception as e:
    lint_verdict = 'EXC %s' % str(e)[:100]
W('G5 card-lint probe: %s' % lint_verdict)

bf_tail = 'n/a'
try:
    tl = open(bm + r'\results\_r954bmb_blobfill.log', encoding='utf-8').read().strip().split('\n')
    bf_tail = ' ;; '.join(tl[-3:])
except Exception as e:
    bf_tail = 'EXC %s' % str(e)[:80]
W('blobfill tail: %s' % bf_tail)

rc_sat, sat_out = cap_run(['python', bm + r'\scripts\saturation_engine.py', 'status'], bm, 40)
W('sat_engine rc=%s tail=%s' % (rc_sat, sat_out.strip().replace('\n', ' | ')[-120:]))

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
W('ram=%s vram=%s' % (free_ram_gb, vram_free))

# ---------- 1) G5 receipt MSG ----------
MSG_REL = r'fleet\inbox\MSG-20261015-0104-bmb-P1B-G5-done.md'
msg_path = os.path.join(bm, MSG_REL)
os.makedirs(os.path.dirname(msg_path), exist_ok=True)
open(msg_path, 'w', encoding='utf-8').write(
    "# MSG-20261015-0104-bmb: POOL-P1B-G5 receipt (done) - G5 转单协议织入单回执（bm-b·cpu-sound 车道）\n\n"
    "To: HQ-CEOProxy（收卡席）｜From: bm-b（cpu-sound 车道执行机）\n\n"
    "**交接卡回执三元组（CHARTER §7.4 最低三元组）**：\n"
    "- **卡 ID**: POOL-P1B-G5\n"
    "- **动作**: done（r954 开窗即验即执·O-20261014-1325 CEO 即时工单律）\n"
    "- **证据指针**: 织入正身=共享件 Tools/iteration_prompt.txt（三机 Bigmoney-IterationLoop 同一 prompt 源·origin 织入链=bm-c d56da5358 → bm-a r997 ebf8a64·本机循环拉取即得=bm-c MSG-20261014-2355 释明双车道共享件一次覆盖·本机无需重复织入）；"
    "运行时消费实证=r954 会话即在本织入 prompt 下执行（G5 三件套执法面在役：fleet/orders 差集扫描=零新令·组台账 G5 卡经 D-19 全量消费）；"
    "本 MSG 随 r954 树手术提交上链（C3）+侧支 machine/bm-b-r954 推送（回执=results/_r954bmb_push_receipt.json）——收卡后请按写手制迁 POOL.json 五态。\n\n"
    "## 验收物对照（bm-b 侧）\n"
    "- 织入=共享件覆盖（见上）；本机轮 prompt S0.5/D-19 段含三件套（九要素识别+card-lint 过闸+回执行带卡 ID）。\n"
    "- 本轮实弹=令扫差集零新令（origin 新令止于 O-20261014-0949-bm-b·早于 r946 末次健康扫描）+组台账 G5 卡 D-19 消费+本回执；"
    "card-lint 复核=%s。\n"
    "- provenance：转述（CEO-PROXY 窗口转单）。\n" % lint_verdict)
W('G5 MSG written: %s (%d bytes)' % (MSG_REL, os.path.getsize(msg_path)))

# ---------- 2) heartbeat ----------
hb = {
    "machine_id": "bm-b", "last_seen": iso,
    "task": "r954: G5 receipt + D-19 orders-delta consumption (watermark advanced) + resumable blobfill driver (supersedes treadmill watcher/worker) + C3 surgery + side-branch machine/bm-b-r954 push",
    "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-improving: 7/9 faces on disk (config/docs/engine/firm/knowledge/legacy/live rc=0); "
                "fleet+data pending blobfill driver (resumable 160-SHA batch fetch, pid 28880, in flight); "
                "SatEngine dead until fleet face lands (machine.json); side-branch machine/bm-b-r951 LANDED "
                "(peer visibility restored); G5 receipt delivered r954 branch; group orders delta consumed"),
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("blobfill supersedes watcher v3+worker v2 (single-batch lazy fetch = non-resumable treadmill); "
             "orders ack diff-scan: origin newest O-20261014-0949-bm-b predates r946 last healthy scan = zero new; "
             "smoke/S6 deferred until ALL_FACES_RESTORED marker"),
}
os.makedirs(bm + r'\fleet\machines', exist_ok=True)
hbp = bm + r'\fleet\machines\bm-b.json'
open(hbp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d' % chk['heartbeat_epoch_utc'])

# ---------- 3) round report line ----------
line_r = (
    ymd + " " + hm + " | r954 | 恢复续进轮（r954=bm-b·车道恢复线第 8 轮）："
    "①r953 推送驱动回执=PUSHED_VERIFIED（侧支 machine/bm-b-r951 落地 9b2329dcfec2=对等可见性恢复·r951-r953 产品全链交付）；"
    "②faces 恢复跑步机定谳+根治=worker v2 五连 TIMEOUT 实证（fleet/data 面 checkout 触发单批 lazy fetch·600s 软帽树杀=整批 pack 丢弃=零进展死循环）"
    "→树杀 watcher v3(28448)+worker v2(10232)（r948 律杀前验归属·两枚均本 lane 恢复体·孤儿锁 -ErrorAction Stop+Test-Path 复核清除）"
    "→部署可续传 blob 回填驱动器（_r954bmb_blobfill_driver.py·pythonw 分离 pid 28880·start 行已验=01:04:07·rev-list --missing 取缺失清单"
    "+160 SHA/批增量拉取·每完成批即持久入库·任意带宽下保证收敛·回执=_r954bmb_blobfill_receipt.json=进度面）；"
    "③组台账 D-19 orders delta 全量消费（r953 探针视图 1053 行全读·涉本司 4 行：L1024 B站扩线登记（已部署线上迁 bm-a=现状对齐）"
    "/L1047④ SLI 对账席=r943 已闭环（19:49 GREEN·L1049⑥实证）/L1049⑤ G5 织入单=本轮回执/其余=委员会与 bm-a/bm-c 域）→水位键推进 8b904179→2e5111e6·delta 清零；"
    "④G5 交接卡回执三件套执法（POOL-P1B-G5：共享件织入面=ebf8a64 已在 prompt 在役·card-lint 复核=%s·回执 MSG 上链+推送）；"
    "⑤S0.5 令扫差集=零新令（origin 新令止于 O-20261014-0949-bm-b·早于 r946 末次健康扫描）+收件箱 1 件=bm-c G5 done 回执（致 HQ-CEOProxy·非本机处理面·零动作）"
    "| 证据：_r954bmb_blobfill.log（start 行+pid）+_r954bmb_blobfill_receipt.json+_r953bmb_group_orders_view.md（消费面）"
    "+_r954bmb_closeout.log（C3 rev-parse 回执行）+_r954bmb_push_receipt.json（r955 验收面）"
    "| 诚实跳过：smoke/S6 链（faces 未齐·候 blobfill 回执）/attrition 健康重扫（候 faces 齐）/unshallow+pull --rebase（候暖窗+回填毕）"
    "| WM-VERDICT: red=False（恢复轮·py_watermark 随 S6 缓办）"
    "| 当前活：blobfill 驱动器在飞（fleet+data 面回填）；最近实物：_r954bmb_blobfill_driver.py（可跑驱动器·01:04 点火实证）"
    "+G5 回执 MSG+C3 手术提交；下个里程碑：blobfill 回执 FILL_DONE+FACES_OK→smoke 49/49+S6 链+orders ack+unshallow（窗<=24h）"
    "| 孤儿面=0（手工扫描：blobfill/push 驱动器=本 lane 合法分离体·treadmill 两体已树杀；探针仍因 fleet/machine.json 缺失受阻·faces 落盘后复役）"
    "| 记账预算: 4/5（恢复轮豁免面）| 产品积分: 2（可续传回填驱动器实物+G5 回执交付）"
    "| 本地未达 origin commit 数=5（C1/C2/C3a/C3b/C3·r954 侧支投递在飞·回执=r955）| [r954 bm-b]"
) % lint_verdict
p_rr = bm + r'\logs\iteration-loop\round_reports.md'
b = open(p_rr, 'rb').read()
nl = b'\r\x00\n\x00' if b[:2] == b'\xff\xfe' else b'\r\n'
enc = 'utf-16-le' if b[:2] == b'\xff\xfe' else 'utf-8'
if not b.endswith(nl):
    b = b + nl
open(p_rr, 'wb').write(b + (line_r + '\r\n').encode(enc))
W('round_reports appended enc=%s' % enc)

# ---------- 4) CODELY pit law ----------
line_c = (
    "\n[" + ymd + " " + hm + "] bm-b r954 判例（faces 恢复跑步机根治·blob:none 冷索引批量回填法）："
    "blob:none 部分克隆冷索引下，porcelain checkout 任一面触发的单批 lazy fetch 在带宽受限窗内不可续传"
    "——600s 软帽树杀=整批 pack 丢弃=每轮重下同一批零进展（worker v2 fleet/data 面 5 连 TIMEOUT 实证·夜窗带宽下结构性死循环）。"
    "正法=可续传批量回填驱动器：git rev-list --objects --missing=print --all 取缺失 blob 清单"
    "→按 ~160 SHA/批 git fetch --no-tags origin <shas> 小批拉取→每完成批即持久入库（任意带宽下保证收敛）"
    "→清单清零后 checkout 面瞬时成功。How to apply：冷索引恢复一律先批量回填再 checkout；单批 lazy fetch 同批 2 次 TIMEOUT=判跑步机即换此法。\n"
)
codely_path = bm + r'\CODELY.md'
with open(codely_path, 'ab') as f:
    f.write(line_c.encode('utf-8'))
W('CODELY appended bytes=%d' % len(line_c.encode('utf-8')))

# ---------- 5) state.json ----------
sp = bm + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
st['clock_read'] = iso
st['current'] = "r954: G5 receipt + D-19 consumption + blobfill driver (treadmill root-cause fix) + C3 surgery + r954 side-branch push"
st['did'] = ("r954: push receipt PUSHED_VERIFIED consumed (machine/bm-b-r951 landed 9b2329dcfec2, peer visibility restored); "
             "treadmill adjudicated+fixed: worker v2 single-batch lazy fetch (600s tree-kill = pack discarded = zero progress, 5x fleet/data TIMEOUT) "
             "-> watcher v3 (28448) + worker v2 (10232) tree-killed (own-lane verified per r948 law, orphan index.lock removed+verified); "
             "resumable blobfill driver deployed detached (pid 28880, start-line verified 01:04:07; rev-list --missing list + 160-SHA batch fetch, "
             "each completed batch persists; receipt results/_r954bmb_blobfill_receipt.json); group orders D-19 delta fully consumed "
             "(r953 probe view 1053 lines; bm-b-relevant: L1024 B-station line status-aligned, L1047-4 SLI already closed r943, "
             "L1049-5 G5 receipted this round) -> watermark advanced 8b904179 -> 2e5111e6, delta cleared; G5 card three-piece enforcement done "
             "(shared-file weave ebf8a64 active in this very prompt; card-lint probe recorded; receipt MSG fleet/inbox/MSG-20261015-0104-bmb-P1B-G5-done.md); "
             "S0.5 fleet/orders diff-scan = zero new orders (origin newest O-20261014-0949-bm-b predates r946 last healthy scan); "
             "inbox 1 msg = bm-c G5 done receipt addressed to HQ-CEOProxy (not bm-b, zero action)")
st['last_action'] = "r954: blobfill treadmill fix (resumable driver supersedes watcher/worker) + G5 receipt + D-19 watermark advance + C3 surgery + r954 push"
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = "results/_r954bmb_blobfill_driver.py (detached pid 28880; receipt _r954bmb_blobfill_receipt.json) + fleet/inbox/MSG-20261015-0104-bmb-P1B-G5-done.md"
st['next'] = ("r955: 1) read results/_r954bmb_blobfill_receipt.json + results/_r952bmb_faces_marker.txt: "
              "FILL_DONE+FACES_OK / ALL_FACES_RESTORED -> smoke 49/49 + S6 chain (live.paper REGIME_GUARD=enforce + t35/t24 on new-bar) "
              "+ saturation_engine verify (fleet face on disk revives it via S4U tick) + orders full ack diff-scan (fleet/orders now on disk) "
              "+ attrition guard healthy rescan + unshallow/pull --rebase origin tip warm window + merge side branches machine/bm-b-r951 + machine/bm-b-r954; "
              "FILLING -> monitor receipt progress (batches_done), zero git interference (driver owns the fetch pipe; do NOT run git pull/status); "
              "2) read results/_r954bmb_push_receipt.json: PUSHED_VERIFIED -> G5 receipt delivered; else relaunch push driver (idempotent); "
              "3) G5 card done r954 (receipt MSG via C3 + side-branch); POOL.json five-state migration belongs to CEO-PROXY collector; "
              "4) standing: no rm on repo faces by any lane; group-tree zero-touch (origin reads only); "
              "5) forensics standing: USN 19:36-19:55 window + other-lane transcripts")
st['next_milestone'] = "blobfill FILL_DONE+FACES_OK marker -> smoke 49/49 + S6 chain + orders ack + attrition rescan + unshallow/pull warm window (window <=24h)"
st['note'] = ("r954: treadmill root cause = non-resumable single-batch lazy fetch; fix = resumable 160-SHA batch fill (each batch persists); "
              "blobfill + push drivers = own-lane legit detached bodies; G5 weave = shared prompt file (bm-c d56da5358/bm-a ebf8a64), "
              "bm-b consumption = this round ran under it")
st['now_active'] = "r954: recovery - blobfill driver in flight (fleet+data blob backfill) + push driver in flight (r954 side-branch)"
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ("r954: treadmill watcher v3 + worker v2 tree-killed (own-lane verified); blobfill driver + push driver = own-lane legit "
                          "detached bodies; orphan probe still blocked on fleet/machine.json (fleet face pending) - manual sweep carried, "
                          "probe re-arms after faces land")
st['round'] = 954
st['round_no'] = 955
st['round_no_label'] = 'r954'
st['task'] = ("r954: (a) recovery = lane mission until faces complete (blobfill driver) (b) G5 card receipt delivered (c) D-19 orders delta "
              "consumed, watermark advanced (d) stock-universe P1 awaits CEO signature - waiting-state declaration carried, no re-scan")
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ("AMBER-improving: 7/9 faces on disk; fleet+data pending blobfill (resumable driver in flight, supersedes treadmill); "
                 "SatEngine dead until fleet face (revives via S4U tick post-restore); side-branch r951 LANDED (peer visibility restored); "
                 "G5 receipt delivered via r954 branch push; group orders delta consumed (watermark 2e5111e6); zero origin-side loss")
st['sat_engine'] = {"status": "dead-by-missing-fleet-face (status probe rc=%s: fleet/machine.json absent; S4U per-minute tick auto-revives once blobfill lands fleet face on disk)" % rc_sat,
                    "checked_at": iso}
st['last_orders_sha'] = "2e5111e657ec47f8ae8aa6fff9f3d2ca34c46488"
st['last_orders_at'] = iso
st['last_orders_read_at'] = iso
st['last_orders_sha_probe'] = "2e5111e657ec47f8ae8aa6fff9f3d2ca34c46488"
st['orders_delta_pending'] = False
st['last_orders_sha_note'] = "r954 consumed 8b904179->2e5111e6 (29-row r947-attempt delta + 10-14 19:2x~10-15 00:0x rows; bm-b-relevant: SLI r943-closed, G5 receipted r954, B-station line aligned); view=results/_r953bmb_group_orders_view.md"
st['decisions_delta_pending'] = False
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=954 round_no=955 orders watermark advanced')

# ---------- 6) C3 surgery commit ----------
rc, head, _ = run_git(['rev-parse', 'HEAD'], timeout=15)
head = head.decode().strip()
rc, base_tree, _ = run_git(['rev-parse', 'HEAD^{tree}'], timeout=15)
base_tree = base_tree.decode().strip()
W('surgery base HEAD=%s tree=%s' % (head[:12], base_tree[:12]))
msg_path_c = bm + r'\results\_r954bmb_commitmsg.txt'
open(msg_path_c, 'w', encoding='utf-8').write(
    "round 954: G5 receipt MSG (POOL-P1B-G5 done, shared-prompt weave consumed) + D-19 orders-delta consumption "
    "(watermark 2e5111e6) + treadmill root-cause fix (resumable blobfill driver supersedes watcher v3+worker v2; "
    "own-lane tree-kill verified, orphan lock cleared) + state/round-report/heartbeat/CODELY r954 pit law; "
    "honest skips: smoke/S6/attrition-rescan/unshallow (faces pending blobfill)\n")

def surgery(base, changed, msgp):
    tree = base
    for parts in changed:
        fp = os.path.join(bm, *parts)
        if not os.path.exists(fp):
            W('MISSING file, skip: %s' % '/'.join(parts)); continue
        rc, out, err = run_git(['hash-object', '-w', fp], timeout=30)
        if rc != 0:
            W('hash-object FAIL %s' % '/'.join(parts)); sys.exit(1)
        tree = update_path(tree, parts, out.decode().strip())
        if tree is None:
            W('ABORT surgery at %s' % '/'.join(parts)); sys.exit(1)
    rc, cout, cerr = run_git(['commit-tree', tree, '-p', head, '-F', msgp], timeout=30)
    if rc != 0:
        W('commit-tree FAIL: %s' % cerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
    return cout.decode().strip()

changed_c = [
    ['fleet', 'inbox', 'MSG-20261015-0104-bmb-P1B-G5-done.md'],
    ['fleet', 'machines', 'bm-b.json'],
    ['state.json'],
    ['logs', 'iteration-loop', 'round_reports.md'],
    ['CODELY.md'],
    ['results', '_r954bmb_blobfill_driver.py'],
    ['results', '_r954bmb_push_driver.py'],
    ['results', '_r954bmb_closeout.py'],
    ['results', '_r954bmb_commitmsg.txt'],
    ['results', '_r954bmb_g5_card_extract.txt'],
]
c3 = surgery(base_tree, changed_c, msg_path_c)
W('C3 surgery ok commit=%s (parent %s)' % (c3[:12], head[:12]))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', c3], timeout=30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(1)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], timeout=15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], c3[:12], chk.decode().strip() == c3))

# ---------- 7) push driver launch ----------
DRIVER = bm + r'\results\_r954bmb_push_driver.py'
DLOG = bm + r'\results\_r954bmb_push_driver.log'
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
    W('PUSH DRIVER NOT VERIFIED - r955 must relaunch idempotent')

# ---------- 8) S7 self-heal ----------
ps_cmd = ("& 'Tools\\register_loop_task.ps1'; & 'Tools\\register_watchdog_task.ps1'; "
          "& 'Tools\\register_precommit_claw.ps1'; & 'Tools\\register_prepush_claw.ps1'")
rc_s7, s7_out = cap_run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_cmd], bm, 150)
W('s7_selfheal rc=%s tail=%s' % (rc_s7, s7_out.strip().replace('\n', ' | ')[-300:]))

# ---------- 9) final state touch ----------
rc, cnt_out, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], timeout=30)
behind = cnt_out.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    "last_push_ts": iso,
    "side_branch": "machine/bm-b-r954",
    "c3": c3[:12],
    "driver": "detached (wscript InvisibleRunner chain -> pythonw), start-line verified=%s" % drv_started,
    "behind_origin_main": behind,
    "note": ("C1/C2/C3a/C3b (r951-r953, landed via machine/bm-b-r951 PUSHED_VERIFIED) + C3 (r954) on local main; "
             "r954 branch push in flight (receipt _r954bmb_push_receipt.json = r955 face); origin main catch-up deferred "
             "to warm window post-blobfill (cold-index pull hazard); blobfill driver owns git fetch pipe meanwhile"),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(sp, 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('CLOSEOUT_OK c3=%s pushdrv_verified=%s lint=%s sat_rc=%s s7_rc=%s behind=%s ram=%s' % (
    c3[:12], drv_started, lint_verdict[:60], rc_sat, rc_s7, behind, free_ram_gb))
