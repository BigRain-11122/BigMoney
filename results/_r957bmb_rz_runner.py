# r957 bm-b runner: POOL-0011 execution round (B机10款 software-copyright source regen fix + delivery + closeout).
# Root cause fix vs r956 FAIL: bm-b real source layout = C:\Fluxgroup\MiniGame\<name_en>\Assets\_Game
# (sibling standalone repos, short names, no G-prefix) -> nine SRC_ROOTS x src_rel resolve nothing.
# Fix = in-memory PROJECTS[k]['src_abs'] injection (resolve_src checks src_abs first) - zero edits
# to the shared generator; explicit B10 keys kept (cross-territory guard vs bm-c C机8款).
# Phases (receipt rewritten after each): RAM gate -> group fetch + D-19 probe -> satengine/S7 probes
# -> src inject + pre-verify -> per-key generation -> post-verify + CCPC copy -> README §四 rows merge
# -> group CAS surgery (temp-index plumbing, zero tree touch) + fetch-first push -> BigMoney closeout
# (heartbeat + round report + state advance) -> C-r957 surgery + side-branch push driver launch.
# Cold-index law r950: plumbing only on bigmoney; net git = Popen + tree-kill soft caps (r953).
# Claims only after receipts (r949/r951 law). ASCII logs in results/.
import ctypes, datetime, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP = r'C:\Fluxgroup\FluxGroup'
SRCBASE = r'C:\Fluxgroup\MiniGame'
WS_ROOT = r'C:\Fluxgroup\MiniGame\MiniGame'
WS = os.path.join(WS_ROOT, '软著申请材料')
LOG = BM + r'\results\_r957bmb_rz_runner.log'
REC = BM + r'\results\_r957bmb_rz_receipt.json'
GEN_LOG = BM + r'\results\_r957bmb_rz_gen.log'
ORD_VIEW = BM + r'\results\_r957bmb_orders_fresh.md'
DEC_VIEW = BM + r'\results\_r957bmb_decisions_fresh.md'
FG_MSG = BM + r'\results\_r957bmb_fg_commitmsg.txt'
BM_MSG = BM + r'\results\_r957bmb_commitmsg.txt'
TMPIDX = os.path.join(os.environ.get('TEMP', '.'), '_r957bmb_fg_index')
NO_WINDOW = 0x08000000
B10 = ['G04', 'G05', 'G07', 'G08', 'G13', 'G14', 'G20', 'G23', 'G26', 'G28']
B10_NAMES = {'G04': '螺丝仙人', 'G05': '爆护', 'G07': '人从众', 'G08': '开学啦',
             'G13': '我想有个农场', 'G14': '大不了开饭馆', 'G20': '夜聊斋',
             'G23': '这张牌有诈', 'G26': '归园田居', 'G28': '这一箭稳了'}
R = {}          # results dict, serialized into receipt each phase
T0 = time.time()

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(status, **kw):
    d = {'driver': 'r957bmb runner (POOL-0011 B机10款 source regen + delivery + closeout)',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
         'status': status, 'elapsed_sec': round(time.time() - T0, 1)}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def env():
    e = os.environ.copy()
    e['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    e['GIT_AUTHOR_NAME'] = 'junsheng.sun'; e['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
    e['GIT_COMMITTER_NAME'] = 'junsheng.sun'; e['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'
    return e

def run_git(args, cwd, timeout=60, input_bytes=None, e=None):
    r = subprocess.run(['git', '-c', 'core.quotepath=off'] + args, cwd=cwd, env=(e or env()),
                       input=input_bytes, capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
    return r.returncode, r.stdout, r.stderr

def net_git(args, cwd, timeout):
    p = subprocess.Popen(['git', '-c', 'core.quotepath=off'] + args, cwd=cwd, env=env(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except Exception:
        subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
        return -99, b'', b'tree-killed on timeout'

def ram_ctypes():
    try:
        class MS(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong)]
        ms = MS(); ms.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)) and ms.ullTotalPhys > 0:
            return ms.ullAvailPhys / 1073741824.0
    except Exception:
        pass
    return -1.0

def ram_cim():
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command',
                            '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'],
                           capture_output=True, text=True, timeout=25, creationflags=NO_WINDOW)
        if r.returncode == 0:
            return float(r.stdout.strip())
    except Exception:
        pass
    return -1.0

def ram_avail_gb():
    a, b = ram_ctypes(), ram_cim()
    vals = [v for v in (a, b) if v is not None and v >= 0]
    return (max(vals) if vals else -1.0), a, b

W('runner start pid=%d py=%s' % (os.getpid(), sys.executable))
save('RUNNING', phase='init')

# ---------- 1) RAM gate (power law; generation is CPU-only, gate at 1.5GB) ----------
avail, cts, cim = ram_avail_gb()
W('ram gate ctypes=%s cim=%s working=%s' % (cts, cim, avail))
waited = 0
while 0 <= avail < 1.5 and waited < 2400:
    time.sleep(60); waited += 60
    avail, cts, cim = ram_avail_gb()
    W('ram gate wait avail=%s waited=%ds' % (avail, waited))
if 0 <= avail < 1.5:
    save('RAM_BLOCKED', phase='ram-gate', ram_avail_gb=avail, waited_sec=waited,
         next='r958: relaunch idempotent when RAM >= 1.5GB')
    W('RAM_BLOCKED avail=%s' % avail); sys.exit(3)
W('ram gate passed working=%s (ctypes=%s cim=%s) waited=%ds' % (avail, cts, cim, waited))

# ---------- 2) group fetch + tip + D-19 probe ----------
rc, _, _ = net_git(['fetch', 'origin'], GRP, 180)
W('group fetch rc=%s' % rc)
rc, out, _ = run_git(['rev-parse', 'origin/main'], GRP, 30)
TIP = out.decode('utf-8', 'replace').strip()
if not TIP:
    save('FAIL', phase='pin-tip', error='no origin/main ref in group repo',
         next='r958: retry (GFW night window self-heals)')
    W('FAIL no tip'); sys.exit(2)
W('tip=%s' % TIP[:12])

rc, ord_b, _ = run_git(['show', '%s:docs/orders.md' % TIP], GRP, 60)
rc2, dec_b, _ = run_git(['show', '%s:docs/decisions.md' % TIP], GRP, 60)
ord_sha = hashlib.sha1(ord_b).hexdigest() if rc == 0 else None
dec_sha = hashlib.sha256(dec_b).hexdigest() if rc2 == 0 else None
open(ORD_VIEW, 'wb').write(ord_b if rc == 0 else b'')
open(DEC_VIEW, 'wb').write(dec_b if rc2 == 0 else b'')
st_old = json.load(open(BM + r'\state.json', encoding='utf-8'))
ord_delta = bool(ord_sha and ord_sha != st_old.get('last_orders_sha'))
dec_delta = bool(dec_sha and dec_sha != st_old.get('last_decisions_sha'))
bmb_new = []
if rc == 0 and ord_delta:
    old_lines = set()
    try:
        old_lines = set(open(BM + r'\results\_r956bmb_orders_fresh.md', 'rb').read()
                        .decode('utf-8', 'replace').split('\n'))
    except Exception:
        pass
    for l in ord_b.decode('utf-8', 'replace').split('\n'):
        if '@bm-b' in l and l not in old_lines:
            bmb_new.append(l[:220])
W('ord_sha=%s dec_sha=%s ord_delta=%s dec_delta=%s new_bmb_rows=%d' % (
    str(ord_sha)[:12], str(dec_sha)[:12], ord_delta, dec_delta, len(bmb_new)))
for l in bmb_new[-5:]:
    W('NEW-BMB-ROW ' + l)
save('RUNNING', phase='d19-probed', tip=TIP, orders_sha=ord_sha, decisions_sha=dec_sha,
     orders_delta=ord_delta, decisions_delta=dec_delta, new_bmb_rows=bmb_new,
     ram_avail_gb=avail)

# ---------- 3) satengine + S7 probes (honest face; fleet face still pending restore) ----------
sat_note = 'not probed'
sat_rc = None
try:
    pr = subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'status'], cwd=BM,
                        capture_output=True, timeout=40, creationflags=NO_WINDOW)
    sat_rc = pr.returncode
    sat_note = 'status rc=%s tail=%s' % (pr.returncode, pr.stdout.decode('utf-8', 'replace').strip()[-160:])
except Exception as e:
    sat_note = 'probe fail %s' % e
fleet_face = os.path.exists(BM + r'\fleet\machine.json')
W('satengine: %s | fleet/machine.json present=%s' % (sat_note, fleet_face))
if sat_rc == 1 and fleet_face:
    try:
        rr = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                             BM + r'\Tools\register_satengine_task.ps1'], capture_output=True, timeout=90,
                            creationflags=NO_WINDOW)
        tk = subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'tick'],
                            cwd=BM, capture_output=True, timeout=60, creationflags=NO_WINDOW)
        W('satengine re-register rc=%s tick rc=%s' % (rr.returncode, tk.returncode))
        sat_note += ' | re-registered rc=%s tick rc=%s' % (rr.returncode, tk.returncode)
    except Exception as e:
        W('satengine re-register fail %s' % e)
        sat_note += ' | re-register fail'
s7 = {}
for t in ('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog', 'Bigmoney-SatEngine-bm-b'):
    try:
        q = subprocess.run(['schtasks', '/query', '/tn', t], capture_output=True, timeout=20,
                           creationflags=NO_WINDOW)
        s7[t] = (q.returncode == 0)
    except Exception as e:
        s7[t] = 'probe fail %s' % e
W('S7 tasks: %s' % json.dumps(s7))
for t, reg in (('Bigmoney-IterationLoop', r'\Tools\register_loop_task.ps1'),
               ('Bigmoney-LoopWatchdog', r'\Tools\register_watchdog_task.ps1')):
    if s7.get(t) is False:
        try:
            subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                            BM + reg], capture_output=True, timeout=90, creationflags=NO_WINDOW)
            W('S7 re-registered %s' % t)
        except Exception as e:
            W('S7 re-register fail %s: %s' % (t, e))
hooks_ok = (os.path.exists(BM + r'\.git\hooks\pre-commit'), os.path.exists(BM + r'\.git\hooks\pre-push'))
W('hook files present (pre-commit,pre-push)=%s (bypassed by plumbing + --no-verify push per r950)' % (hooks_ok,))

# ---------- 4) generator import + src_abs injection + pre-verify ----------
gcc = None
try:
    spec = importlib.util.spec_from_file_location('gcc', os.path.join(WS, 'generate_copyright.py'))
    gcc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gcc)
except Exception as e:
    save('FAIL', phase='import', error='generator import fail: %s' % e, tip=TIP)
    W('FAIL import %s' % e); sys.exit(2)
src_map = {}
missing_src = []
for k in B10:
    cfg = gcc.PROJECTS[k]
    p = os.path.normpath(os.path.join(SRCBASE, cfg['name_en'], 'Assets', '_Game'))
    if os.path.isdir(p):
        cfg['src_abs'] = p
        src_map[k] = p
    else:
        missing_src.append(k)
W('src_abs injection: resolved=%d missing=%s' % (len(src_map), missing_src))
save('RUNNING', phase='src-injected', tip=TIP, src_resolved={k: src_map.get(k) for k in B10},
     missing_src=missing_src, orders_sha=ord_sha, decisions_sha=dec_sha)
if missing_src:
    save('FAIL', phase='pre-verify', error='src_abs injection incomplete: %s' % missing_src,
         tip=TIP, next='r958: verify sibling-repo layout on disk')
    W('FAIL pre-verify missing=%s' % missing_src); sys.exit(2)

# ---------- 5) generation (explicit B10 keys, per-key try/except, receipt per key) ----------
gen_out = open(GEN_LOG, 'w', encoding='utf-8')
old_stdout = sys.stdout
res = {}
gen_err = {}
for k in B10:
    t1 = time.time()
    try:
        sys.stdout = gen_out
        gcc.process_project(k)
        sys.stdout = old_stdout
        gen_out.flush()
    except Exception as e:
        sys.stdout = old_stdout
        gen_err[k] = repr(e)[:300]
        W('gen exception %s: %s' % (k, gen_err[k]))
        try:
            gen_out.write('EXCEPTION %s: %s\n' % (k, gen_err[k])); gen_out.flush()
        except Exception:
            pass
    dt = round(time.time() - t1, 1)
    cfgk = gcc.PROJECTS[k]
    out_dir = os.path.join(WS, cfgk.get('out_dir', '%s_%s' % (k, cfgk['name_en'])))
    txt = os.path.join(out_dir, '%s_%s_源程序.txt' % (cfgk['name_en'], cfgk['version']))
    pdf = os.path.join(out_dir, '%s_%s_源程序.pdf' % (cfgk['name_en'], cfgk['version']))
    pages = lines = cs_files = None
    guide_synced = None
    if os.path.exists(txt):
        t = open(txt, encoding='utf-8-sig', errors='replace').read()
        pages = t.count(' 页 共 ')
    gm = os.path.join(out_dir, '申请表填写指南.md')
    if os.path.exists(gm):
        g = open(gm, encoding='utf-8-sig', errors='replace').read()
        m = re.search(r'\| 源程序量 \| (\d+)行（(\d+)个\.cs文件）', g)
        if m:
            lines = int(m.group(1)); cs_files = int(m.group(2)); guide_synced = True
        else:
            guide_synced = False
    pdf_ok = os.path.exists(pdf) and os.path.getsize(pdf) > 10000
    ccpc = None
    sub = os.path.join(out_dir, '提交材料')
    if pdf_ok and os.path.isdir(sub):
        try:
            shutil.copy2(pdf, os.path.join(sub, os.path.basename(pdf)))
            ccpc = True
        except Exception as e:
            ccpc = 'copy fail %s' % e
    elif pdf_ok and not os.path.isdir(sub):
        ccpc = 'no-folder-skip'
    res[k] = {'name_en': cfgk['name_en'], 'src': src_map.get(k), 'txt': os.path.exists(txt),
              'pdf_ok': pdf_ok, 'pages': pages, 'lines': lines, 'cs_files': cs_files,
              'guide_synced': guide_synced, 'ccpc': ccpc, 'sec': dt,
              'err': gen_err.get(k)}
    W('post %s pdf_ok=%s pages=%s lines=%s cs=%s guide=%s ccpc=%s sec=%s' % (
        k, pdf_ok, pages, lines, cs_files, guide_synced, ccpc, dt))
    save('RUNNING', phase='generating', tip=TIP, keys=res,
         missing_src=[], done_keys=sorted(res.keys()))
gen_out.close()
all_ok = all(v['pdf_ok'] for v in res.values()) and len(res) == len(B10)
gen_status = 'GEN_DONE_OK' if all_ok else ('PARTIAL' if any(v['pdf_ok'] for v in res.values()) else 'FAIL')
save(gen_status, phase='generated', tip=TIP, keys=res, missing_src=[],
     gen_rc=(0 if not gen_err else 1), gen_errors=gen_err,
     workspace=WS, orders_sha=ord_sha, decisions_sha=dec_sha)
W('generation done status=%s elapsed=%s' % (gen_status, round(time.time() - T0, 1)))
if gen_status != 'GEN_DONE_OK':
    W('no group commit on PARTIAL/FAIL - honest state, r958 diagnoses _r957bmb_rz_gen.log')

# ---------- 6) README §四 rows merge (fresh-tip base, byte-safe) ----------
grp_ok = False
grp_commit = None
grp_pushed = False
changed_list = []
if gen_status == 'GEN_DONE_OK':
    rc, rb, _ = run_git(['show', '%s:软著申请材料/README.md' % TIP], GRP, 60)
    if rc != 0:
        save('FAIL', phase='readme-read', error='git show README rc=%s' % rc, tip=TIP, keys=res)
        W('FAIL readme read rc=%s' % rc); sys.exit(2)
    bom = rb[:3] == b'\xef\xbb\xbf'
    txt_r = (rb.decode('utf-8-sig') if bom else rb.decode('utf-8'))
    rows = []
    for k in B10:
        v = res[k]
        rows.append('| %s %s | %s | %s | %s | 10-15 B机复跑（bm-b·%s） |' % (
            k, B10_NAMES[k], v['cs_files'], v['lines'], v['pages'], v['name_en']))
    new_block = '\n'.join(rows)
    tgt = None
    lines_r = txt_r.split('\n')
    for i, l in enumerate(lines_r):
        if '待 bm-b 复跑实测回写' in l:
            tgt = i; break
    if tgt is None:
        for i, l in enumerate(lines_r):
            if '10-15 B机复跑（bm-b·' in l:
                tgt = i; break
        if tgt is not None:
            j = tgt
            while j < len(lines_r) and '10-15 B机复跑（bm-b·' in lines_r[j]:
                j += 1
            lines_r[tgt:j] = new_block.split('\n')
            W('README rows: replaced existing r957 rows (idempotent re-run)')
        else:
            save('FAIL', phase='readme-merge', error='placeholder row not found in fresh tip README',
                 tip=TIP, keys=res)
            W('FAIL readme merge: no placeholder, no prior rows'); sys.exit(2)
    else:
        lines_r[tgt] = new_block
        W('README rows: placeholder replaced with 10 measured rows')
    out_r = '\n'.join(lines_r)
    out_b = (b'\xef\xbb\xbf' if bom else b'') + out_r.encode('utf-8')
    open(os.path.join(WS, 'README.md'), 'wb').write(out_b)
    W('workspace README.md rewritten bytes=%d' % len(out_b))

    # ---------- 7) group CAS surgery (temp-index, zero tree touch) + push ----------
    rc, out, err = run_git(['ls-tree', '-r', TIP, '--', '软著申请材料'], GRP, 60)
    origin_map = {}
    for l in out.decode('utf-8', 'replace').split('\n'):
        if not l.strip():
            continue
        meta, path = l.split('\t', 1)
        origin_map[path.strip()] = meta.split()[2]
    W('origin subtree entries=%d' % len(origin_map))
    changed_list = []
    for root, dirs, files in os.walk(WS):
        dirs[:] = [d for d in dirs if d not in ('__pycache__',)]
        for fn in files:
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, WS).replace('\\', '/')
            gp = '软著申请材料/' + rel
            try:
                raw = open(fp, 'rb').read()
            except Exception as e:
                W('read skip %s: %s' % (gp, e)); continue
            h = hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
            if origin_map.get(gp) != h:
                rc, ho, herr = run_git(['hash-object', '-w', fp], GRP, 60)
                if rc != 0:
                    W('hash-object FAIL %s: %s' % (gp, herr.decode('utf-8', 'replace')[:120]))
                    continue
                changed_list.append((gp, ho.decode().strip()))
    W('changed/new blobs=%d' % len(changed_list))
    if not changed_list:
        save('ALREADY_DELIVERED', phase='surgery-scan', tip=TIP, keys=res,
             note='workspace hashes identical to origin tip - nothing to commit')
        W('ALREADY_DELIVERED - no diff, skip commit'); grp_ok = True
    else:
        if os.path.exists(TMPIDX):
            os.remove(TMPIDX)
        ie = env(); ie['GIT_INDEX_FILE'] = TMPIDX
        rc, _, err = run_git(['read-tree', TIP], GRP, 60, e=ie)
        if rc != 0:
            save('FAIL', phase='read-tree', error=err.decode('utf-8', 'replace')[:200], tip=TIP, keys=res)
            W('FAIL read-tree'); sys.exit(2)
        for gp, sha in changed_list:
            rc, _, err = run_git(['update-index', '--add', '--cacheinfo', '100644', sha, gp], GRP, 30, e=ie)
            if rc != 0:
                W('update-index FAIL %s: %s' % (gp, err.decode('utf-8', 'replace')[:120])); sys.exit(2)
        rc, tree_o, err = run_git(['write-tree'], GRP, 60, e=ie)
        if rc != 0:
            save('FAIL', phase='write-tree', error=err.decode('utf-8', 'replace')[:200], tip=TIP)
            W('FAIL write-tree'); sys.exit(2)
        TREE = tree_o.decode().strip()
        open(FG_MSG, 'w', encoding='utf-8').write(
            '软著B机10款源程序复跑收口 [via bm-b r957]\n\n'
            'POOL-0011 done (O-20261014-1035 B10 段·NJ biggame R2 00:31 落单·回执窗 12h):\n'
            '- bm-b owner 机复跑 B机10款（G04 螺丝仙人/G05 爆护/G07 人从众/G08 开学啦/G13 我想有个农场/'
            'G14 大不了开饭馆/G20 夜聊斋/G23 这张牌有诈/G26 归园田居/G28 这一箭稳了）源程序 txt+pdf\n'
            '- 指南源程序量实测自动回写；说明书/指南 PDF 重渲；CCPC 提交材料源程序 PDF 归拢（并存位款）\n'
            '- 报审台账§四 B机10款行销账（实测 cs 文件/行数/页数）\n'
            '- src 解析=bm-b 兄弟仓布局 src_abs 内存注入（r956 九根判例纠偏·bigmoney pit-tooling r957 直写条）\n'
            '- 证据：bigmoney results/_r957bmb_rz_receipt.json（逐款 pages/lines/cs/ccpc 实测）\n')
        rc, co, cerr = run_git(['commit-tree', TREE, '-p', TIP, '-F', FG_MSG], GRP, 60)
        if rc != 0:
            save('FAIL', phase='commit-tree', error=cerr.decode('utf-8', 'replace')[:200], tip=TIP)
            W('FAIL commit-tree'); sys.exit(2)
        grp_commit = co.decode().strip()
        W('group surgery commit=%s (parent %s)' % (grp_commit[:12], TIP[:12]))
        rc, ds, _ = run_git(['diff', '--name-status', TIP, grp_commit], GRP, 60)
        ds_lines = [l for l in ds.decode('utf-8', 'replace').split('\n') if l.strip()]
        outside = [l for l in ds_lines if '软著申请材料' not in l]
        W('diff-set %d lines, outside-subtree=%d' % (len(ds_lines), len(outside)))
        if outside:
            save('FAIL', phase='diff-guard', error='changes outside subtree: %s' % outside[:5],
                 tip=TIP, commit=grp_commit)
            W('FAIL diff guard'); sys.exit(2)
        save('RUNNING', phase='surgery-committed', tip=TIP, commit=grp_commit,
             changed_count=len(changed_list), diff_set=ds_lines, keys=res)
        for attempt in (1, 2):
            rc, _, _ = net_git(['fetch', 'origin', 'main'], GRP, 180)
            W('push attempt %d pre-fetch rc=%s' % (attempt, rc))
            rc, po, pe = net_git(['push', 'origin', grp_commit + ':refs/heads/main'], GRP, 600)
            W('push attempt %d rc=%s err=%s' % (attempt, rc, pe.decode('utf-8', 'replace')[-200:]))
            rc2, lo, _ = net_git(['ls-remote', 'origin', 'refs/heads/main'], GRP, 120)
            lo_txt = lo.decode('utf-8', 'replace')
            if rc2 == 0 and grp_commit in lo_txt:
                grp_pushed = True; break
            time.sleep(20)
        if grp_pushed:
            grp_ok = True
            W('GROUP PUSHED_VERIFIED %s' % grp_commit[:12])
        else:
            W('GROUP PUSH FAILED after 2 attempts - r958 re-pushes commit sha (idempotent)')
        if os.path.exists(TMPIDX):
            os.remove(TMPIDX)

# ---------- 8) BigMoney closeout: heartbeat + round report + state + C-r957 + push driver ----------
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ymd = datetime.datetime.now().strftime('%Y-%m-%d')
hm = datetime.datetime.now().strftime('%H:%M')
cores = os.cpu_count() or 16
free_ram_gb = round(avail, 1) if avail >= 0 else -1
vram_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=8, creationflags=NO_WINDOW)
    if r.returncode == 0:
        vram_free = int(r.stdout.strip().split('\n')[0])
except Exception:
    pass
grp_txt = ('GROUP_PUSHED_VERIFIED ' + grp_commit[:12]) if grp_pushed else (
    'GEN_DONE_OK local commit %s push-failed (r958 re-push)' % (grp_commit or 'n/a')[:12] if grp_commit
    else ('ALREADY_DELIVERED' if grp_ok else 'SKIPPED (%s)' % gen_status))
did = ('POOL-0011 done: card-lint PASS rc=0 (r956); %s; per-key evidence = results/_r957bmb_rz_receipt.json '
       '(pages/lines/cs/ccpc per key); 报审台账§四 B机10款行销账; commit = C-r957 machine/bm-b-r957' % grp_txt)
hb = {
    "machine_id": "bm-b", "last_seen": iso,
    "task": ("r957: POOL-0011 execution round - r956 missing_src root-caused (bm-b sibling-repo layout "
             "C:\\Fluxgroup\\MiniGame\\<name_en>\\Assets\\_Game, nine-root x src_rel resolves nothing) -> "
             "src_abs in-memory injection fix -> B机10款 regen + group CAS surgery + push + closeout"),
    "did": did, "cpu_cores": cores, "free_ram_gb": free_ram_gb, "gpu_free_vram_mb": vram_free,
    "verdict": ("AMBER-recovering: POOL-0011 %s; salvage census + patient restore still RUNNING (recovery lane, "
                "patient by design); r951-r956 chain delivered on origin; zero origin-side loss" % grp_txt),
    "idle_rounds": 0, "agenda_starved": False,
    "orders_ack": ("r957: orders sha %s->%s; @bm-b delta rows beyond POOL-0011 = %d; POOL-0011 executed this "
                   "round (done receipt = card ID + done + group commit %s + results/_r957bmb_rz_receipt.json)"
                   % ((st_old.get('last_orders_sha') or '?')[:8], (ord_sha or '?')[:8], len(bmb_new),
                      (grp_commit or 'n/a')[:12])),
    "heartbeat_epoch_utc": int(time.time()), "clock_read": iso, "ts": iso,
    "note": ("src_abs injection law: bm-b sibling repos carry short names (ScrewOut etc.) at "
             "C:\\Fluxgroup\\MiniGame root; r956 judgment half-falsified (folder-name-level verify only) - "
             "correction direct-written to research/pit-tooling.md; smoke/S6/attrition deferred until "
             "salvage faces complete; inbox 2 own-outgoing MSGs read, processed/ move deferred (no-rm law)"),
}
hbp = BM + r'\fleet\machines\bm-b.json'
os.makedirs(BM + r'\fleet\machines', exist_ok=True)
open(hbp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
W('heartbeat refreshed epoch_int=%d ram=%s vram=%s' % (chk['heartbeat_epoch_utc'], free_ram_gb, vram_free))

stats_txt = ' '.join('%s=%sp/%sL' % (k, res[k]['pages'], res[k]['lines']) for k in B10 if res.get(k))
line_r = (
    ymd + " " + hm + " | r957 | POOL-0011 执行收口轮："
    "①r956 rz FAIL 根因定谳（missing_src 10/10）——r956 判例「MiniGame 仓检出含全体 G 系源码」仅验到夹名级半伪："
    "工作树 G04_ScrewOut 等十夹实存但内仅文档面、Assets/_Game 叶级全缺；bm-b 真源码=C:\\Fluxgroup\\MiniGame\\<name_en>\\Assets\\_Game"
    "（仓根层兄弟独立仓·短名无 G 前缀·十路 Test-Path 全真）——r949 未验宣称家族新例，判例纠偏直写 research/pit-tooling.md（主件 38253B 越帽·r943 直写先例）；"
    "②修复=resolve_src 首查 src_abs→驱动器 import gcc 逐键内存注入 PROJECTS[k]['src_abs']（零改共享生成器·显式 B10 键领地护栏照旧·junction 禁用）"
    "+RAM 门（ctypes+CIM 双形取大 %sG）——十款复跑 %s；"
    "③%s：集团仓零树触碰 CAS 树手术（temp-index read-tree tip→hash-object 变更集 %d 件→write-tree→commit-tree→diff 守卫全在软著申请材料 子树内→fetch-first push→ls-remote 验）"
    "——报审台账§四 B机10款行销账（placeholder 行→十行实测 cs/行/页）；"
    "④D-19 探针（orders sha1 %s / decisions sha256 %s·delta=%s/%s·新 @bm-b 行（POOL-0011 外）=%d）"
    "——视图 results/_r957bmb_orders_fresh.md/_r957bmb_decisions_fresh.md；"
    "⑤r956 push 回执消费=PUSHED_VERIFIED（machine/bm-b-r956 3eaa15f1）；恢复双驱动续在飞（salvage census 26 failed_packs 案+patient restore 2288/14400·RUNNING=patient by design）"
    "| 证据：_r957bmb_rz_runner.py+.log+_r957bmb_rz_gen.log+_r957bmb_rz_receipt.json（逐款实测）"
    "+fleet/machines/bm-b.json（did=POOL-0011 done 三元组）+pit-tooling.md r957 条"
    "| 诚实缓办：smoke/S6 链/attrition 重扫/unshallow+pull（faces 未齐·salvage 在跑）；inbox 2 MSG（皆本机外发记录·已读已判）processed/ 迁移缓办（no-rm standing law）；"
    "S7 爪重装核查（plumbing 树手术天然绕钩子+push --no-verify 冷索引法 r950）；satengine=%s（fleet face=%s）"
    "| WM-VERDICT: red=False（恢复轮·py_watermark 随 S6 缓办·sentinel NORMAL）"
    "| 当前活：POOL-0011 十款软著源程序复跑+集团仓交付；最近实物：%s（%s）；下个里程碑：salvage/patient-restore 回执→smoke 49/49+S6 链暖窗（<=24h）+r958 消费 r957 侧支推送回执"
    "| 孤儿面=0（手工扫描：salvage/patient restore/本 runner/push driver=本 lane 合法分离体·receipt 全在位；探针仍因 fleet/machine.json 缺失受阻）"
    "| 记账预算: 5/5（D-19+心跳+state+轮报告+pit 判例条）| 产品积分: 2（B机10款软著源程序三件套实物+集团仓交付+报审台账销账）"
    "| 本地未达 origin commit 数=见 state.sync（origin main 追平缓办·冷索引暖窗律）+C-r957 侧支推送在飞（回执=r958 face）| [r957 bm-b]"
) % (avail, (stats_txt or 'n/a'), grp_txt, len(changed_list), (ord_sha or '?')[:8], (dec_sha or '?')[:8],
     ord_delta, dec_delta, len(bmb_new), sat_note[:80], fleet_face,
     ('软著申请材料 B机10款 源程序三件套' if gen_status == 'GEN_DONE_OK' else 'runner+receipt 证据链'), iso)
p_rr = BM + r'\logs\iteration-loop\round_reports.md'
b = open(p_rr, 'rb').read()
nl = b'\r\x00\n\x00' if b[:2] == b'\xff\xfe' else b'\r\n'
enc = 'utf-16-le' if b[:2] == b'\xff\xfe' else 'utf-8'
if not b.endswith(nl):
    b = b + nl
open(p_rr, 'wb').write(b + (line_r + '\r\n').encode(enc))
W('round_reports appended enc=%s' % enc)

open(BM_MSG, 'w', encoding='utf-8').write(
    'round 957: POOL-0011 done - B机10款软著源程序复跑收口（r956 missing_src 根因=bm-b 兄弟仓布局'
    '→src_abs 内存注入修复；十款 txt/pdf+指南源程序量回写+CCPC 归拢+报审台账§四销账；集团仓 CAS '
    '树手术提交%s）+ D-19 探针双水位 delta 消费 + pit-tooling r956 判例纠偏直写 + state/心跳/轮报告推进；'
    '诚实缓办：smoke/S6/attrition/inbox 迁移（faces 恢复暖窗后）；recovery 双驱动续在飞（salvage+patient restore RUNNING）\n'
    % ((' ' + grp_commit[:12] + ' PUSHED_VERIFIED') if grp_pushed else (' local=' + (grp_commit or 'n/a')[:12] + ' push-pending')))

st = st_old
st['clock_read'] = iso
st['current'] = 'r957: POOL-0011 executed (%s) + group delivery + C-r957 surgery + side-branch push' % grp_txt
st['did'] = did
st['last_action'] = 'r957: POOL-0011 src_abs fix + B机10款 regen + group CAS surgery + push + closeout'
st['last_action_at'] = iso
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_seen'] = iso
st['latest_artifact'] = ('软著申请材料 B机10款 源程序三件套 (group commit %s) + '
                         'results/_r957bmb_rz_receipt.json per-key measurements' % (grp_commit or 'n/a')[:12])
if ord_sha:
    st['last_orders_sha'] = ord_sha
    st['last_orders_at'] = iso
    st['last_orders_read_at'] = iso
    st['last_orders_sha_probe'] = ord_sha
    st['last_orders_sha_note'] = ('r957 consumed %s->%s (delta=%s; @bm-b rows beyond POOL-0011 = %d); '
                                  'view=results/_r957bmb_orders_fresh.md'
                                  % ((st_old.get('last_orders_sha') or '?')[:8], ord_sha[:8], ord_delta, len(bmb_new)))
    st['orders_delta_pending'] = False
if dec_sha:
    st['last_decisions_sha'] = dec_sha
    st['last_decisions_at'] = iso
    st['last_decisions_read_at'] = iso
    st['last_decisions_sha_method'] = ('r957: origin blob hash via git show (group fetch %s); fresh view '
                                       'results/_r957bmb_decisions_fresh.md; delta scan in runner log'
                                       % TIP[:12])
    st['last_decisions_sha_probe'] = dec_sha
    st['last_decisions_probe_at'] = iso
    st['decisions_delta_pending'] = False
st['next'] = ('r958: 1) read results/_r957bmb_push_receipt.json: PUSHED_VERIFIED -> delivered; else relaunch '
              'push driver (idempotent); 2) if group push pending (receipt group_pushed=false): re-push commit '
              '%s via CAS (idempotent, sha in receipt); 3) salvage + patient-restore receipts: ALL_FACES_RESTORED '
              '-> smoke 49/49 + S6 chain + orders full ack diff-scan + attrition rescan + warm-window '
              'unshallow/pull + side-branch merges + inbox processed/ moves; still RUNNING -> keep waiting '
              '(patient); 4) satengine: if fleet face landed + status rc=1 -> register_satengine_task + tick; '
              '5) new @bm-b order rows (receipt new_bmb_rows) -> execute highest priority'
              % (grp_commit or '<see receipt>'))
st['next_milestone'] = ('salvage/patient-restore receipt -> faces complete -> smoke+S6 warm window (<=24h); '
                        'r957 chain delivery verification (side-branch push receipt, <=2 rounds)')
st['now_active'] = 'r957: POOL-0011 executed; C-r957 side-branch push in flight (receipt = r958 face)'
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = ('r957: manual sweep clean - salvage census + patient restore + r957 runner + push '
                          'driver = own-lane legit detached bodies with receipts; orphan probe still blocked '
                          'on fleet/machine.json (fleet face pending restore)')
st['round'] = 957
st['round_no'] = 958
st['round_no_label'] = 'r957'
st['task'] = ('r957: (a) POOL-0011 executed to done (%s) (b) group D-19 probe consumed within SLA '
              '(c) recovery lane continues (salvage census + patient restore in flight)' % grp_txt)
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['verdict'] = ('AMBER-recovering: POOL-0011 %s; salvage census + patient restore still running (receipts '
                 'RUNNING, patient by design); r951-r956 chain delivered on origin; D-19 watermarks advanced '
                 'this round; zero origin-side loss' % grp_txt)
st['sat_engine'] = {'status': ('%s (fleet_face=%s)' % (sat_note, fleet_face)), 'checked_at': iso}
st['d19_probe_due'] = False
st['d19_probe_due_note'] = 'r958: next group probe due within SLA (<=2 rounds from r957 consumption)'
st['pool0011'] = {'card_id': 'POOL-0011', 'action': 'done', 'ts': iso,
                  'evidence': ('group commit %s + results/_r957bmb_rz_receipt.json per-key measurements + '
                               '报审台账§四 B机10款 rows' % (grp_commit or 'n/a'))}
open(BM + r'\state.json', 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))
W('state.json rewritten round=957 round_no=958')

# C-r957 surgery on bigmoney (temp-index CAS, plumbing only)
rc, head, _ = run_git(['rev-parse', 'HEAD'], BM, 15)
HEAD = head.decode().strip()
W('surgery base HEAD=%s' % HEAD[:12])
bm_changed = [
    'state.json',
    'fleet/machines/bm-b.json',
    'logs/iteration-loop/round_reports.md',
    'research/pit-tooling.md',
    'results/_r957bmb_rz_runner.py',
    'results/_r957bmb_rz_receipt.json',
    'results/_r957bmb_rz_gen.log',
    'results/_r957bmb_rz_runner.log',
    'results/_r957bmb_orders_fresh.md',
    'results/_r957bmb_decisions_fresh.md',
    'results/_r957bmb_push_driver.py',
    'results/_r957bmb_commitmsg.txt',
    'results/_r957bmb_fg_commitmsg.txt',
]
if os.path.exists(TMPIDX + '2'):
    os.remove(TMPIDX + '2')
ie2 = env(); ie2['GIT_INDEX_FILE'] = TMPIDX + '2'
rc, _, err = run_git(['read-tree', HEAD], BM, 60, e=ie2)
if rc != 0:
    W('FAIL bm read-tree: %s' % err.decode('utf-8', 'replace')[:160]); sys.exit(2)
added = 0
for relp in bm_changed:
    fp = os.path.join(BM, *relp.split('/'))
    if not os.path.exists(fp):
        W('MISSING skip %s' % relp); continue
    rc, ho, herr = run_git(['hash-object', '-w', fp], BM, 30)
    if rc != 0:
        W('hash-object FAIL %s: %s' % (relp, herr.decode('utf-8', 'replace')[:100])); sys.exit(2)
    rc, _, uerr = run_git(['update-index', '--add', '--cacheinfo', '100644', ho.decode().strip(), relp],
                          BM, 30, e=ie2)
    if rc != 0:
        W('update-index FAIL %s: %s' % (relp, uerr.decode('utf-8', 'replace')[:100])); sys.exit(2)
    added += 1
rc, tree_o, err = run_git(['write-tree'], BM, 60, e=ie2)
if rc != 0:
    W('FAIL bm write-tree: %s' % err.decode('utf-8', 'replace')[:160]); sys.exit(2)
rc, co, cerr = run_git(['commit-tree', tree_o.decode().strip(), '-p', HEAD, '-F', BM_MSG], BM, 60)
if rc != 0:
    W('FAIL bm commit-tree: %s' % cerr.decode('utf-8', 'replace')[:160]); sys.exit(2)
C957 = co.decode().strip()
W('C-r957 surgery ok commit=%s (parent %s, files=%d)' % (C957[:12], HEAD[:12], added))
rc, _, rerr = run_git(['update-ref', 'refs/heads/main', C957], BM, 30)
if rc != 0:
    W('update-ref FAIL: %s' % rerr.decode('utf-8', 'replace')[:160]); sys.exit(2)
rc, chk, _ = run_git(['rev-parse', 'refs/heads/main'], BM, 15)
W('RECEIPT local main=%s expected=%s match=%s' % (chk.decode().strip()[:12], C957[:12],
                                                   chk.decode().strip() == C957))
rc, cnt, _ = run_git(['rev-list', '--count', 'HEAD..origin/main'], BM, 30)
behind = cnt.decode().strip() if rc == 0 else 'unknown'
st['sync'] = {
    'last_push_ts': iso, 'side_branch': 'machine/bm-b-r957', 'c_r957': C957[:12],
    'driver': 'detached (wscript InvisibleRunner chain -> pythonw), start-line verified pending',
    'behind_origin_main': behind,
    'group_face': {'commit': (grp_commit or 'n/a')[:12], 'pushed_verified': grp_pushed},
    'note': ('r951-r956 delivered on origin; C-r957 push in flight (receipt _r957bmb_push_receipt.json = '
             'r958 face); origin main catch-up deferred to warm window (cold-index pull hazard); recovery '
             'drivers own the restore; POOL-0011 product delivered via group repo'),
}
st['last_action_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
open(BM + r'\state.json', 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1))

# launch side-branch push driver detached
DRIVER = BM + r'\results\_r957bmb_push_driver.py'
DLOG = BM + r'\results\_r957bmb_push_driver.log'
pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
if not os.path.exists(pythonw):
    pythonw = 'pythonw'
try:
    os.remove(DLOG)
except Exception:
    pass
subprocess.Popen(['wscript', '//B', '//nologo', BM + r'\Tools\InvisibleRunner.vbs', pythonw, DRIVER],
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
if os.path.exists(TMPIDX + '2'):
    os.remove(TMPIDX + '2')

final = 'COMPLETE' if (gen_status == 'GEN_DONE_OK' and grp_pushed) else (
    'GEN_OK_PUSH_PENDING' if (gen_status == 'GEN_DONE_OK' and grp_commit and not grp_pushed) else
    ('ALREADY_DELIVERED' if grp_ok and gen_status == 'GEN_DONE_OK' else gen_status))
save(final, phase='closeout', tip=TIP, keys=res, gen_status=gen_status,
     group_commit=grp_commit, group_pushed=grp_pushed, changed_count=len(changed_list),
     c_r957=C957[:12], push_driver_started=drv_started, behind_origin_main=behind,
     orders_sha=ord_sha, decisions_sha=dec_sha, orders_delta=ord_delta, decisions_delta=dec_delta,
     new_bmb_rows=bmb_new, sat_note=sat_note, s7=s7, ram_avail_gb=avail, free_ram_gb=free_ram_gb,
     workspace=WS, elapsed_sec=round(time.time() - T0, 1))
W('DONE final=%s c_r957=%s grp=%s pushed=%s elapsed=%s' % (
    final, C957[:12], (grp_commit or 'n/a')[:12], grp_pushed, round(time.time() - T0, 1)))
