# r956 bm-b rz driver: POOL-0011 B机10款 software-copyright source regeneration.
# Detached (pythonw via InvisibleRunner). Card: O-20261014-1035 B10 segment, NJ biggame R2 00:31.
# Phases: fetch-group -> pin tip -> extract text files (skip pdf) -> per-key src pre-verify
# -> RAM gate (power law) -> run generator with EXPLICIT B10 keys (cross-territory guard vs
# bm-c L1019 C机8款) -> post-verify stats -> CCPC copy -> receipt (r957 commit face).
# Workspace = C:\Fluxgroup\MiniGame\MiniGame\软著申请材料 (inside MiniGame repo root so
# generator SRC_ROOT #5 REPO resolves bare G04_ScrewOut/... src_rel; r956 placement law).
# No kill; patient. Log ASCII-safe, this dir.
import ctypes, datetime, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP = r'C:\Fluxgroup\FluxGroup'
WS_ROOT = r'C:\Fluxgroup\MiniGame\MiniGame'
WS = os.path.join(WS_ROOT, '软著申请材料')
LOG = BM + r'\results\_r956bmb_rz_driver.log'
REC = BM + r'\results\_r956bmb_rz_receipt.json'
GEN_LOG = BM + r'\results\_r956bmb_rz_gen.log'
B10 = ['G04', 'G05', 'G07', 'G08', 'G13', 'G14', 'G20', 'G23', 'G26', 'G28']
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(status, **kw):
    d = {'driver': 'r956bmb rz (POOL-0011 B机10款 source regen, O-20261014-1035 B10)',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'status': status}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def run_git(args, cwd, timeout=90, inp=None):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    try:
        r = subprocess.run(['git', '-c', 'core.quotepath=off'] + args, cwd=cwd, env=env,
                           input=inp, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, b'', str(e).encode('utf-8', 'replace')

def ram_avail_gb():
    class MS(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPage', ctypes.c_ulonglong), ('ullAvailPage', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong), ('ullAvailExtVirtual', ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
        return ms.ullAvailPhys / 1073741824.0
    return -1.0

W('driver start pid=%d' % os.getpid())
save('RUNNING', phase='init', note='detached body, own-lane; receipt = r957 commit face')

# 1) fetch group origin (fail-open: refs from previous fetch remain usable)
rc, _, _ = run_git(['fetch', 'origin'], GRP, timeout=150)
W('group fetch rc=%s' % rc)
rc, out, _ = run_git(['rev-parse', 'origin/main'], GRP, timeout=30)
tip = out.decode('utf-8', 'replace').strip()
if not tip:
    save('FAIL', error='no origin/main ref in group repo', phase='pin-tip')
    W('FAIL no tip'); sys.exit(2)
W('tip=%s' % tip[:12])

# 2) subtree listing (quotepath=off, python unicode args)
rc, out, err = run_git(['ls-tree', '-r', tip, '--name-only', '--', '软著申请材料'], GRP, timeout=60)
files = [l.strip() for l in out.decode('utf-8', 'replace').split('\n') if l.strip()]
if rc != 0 or not files:
    save('FAIL', error='ls-tree empty rc=%s' % rc, tip=tip, phase='ls-tree')
    W('FAIL ls-tree rc=%s err=%s' % (rc, err.decode('utf-8', 'replace')[:120])); sys.exit(2)
keep = [f for f in files if not f.lower().endswith('.pdf')]
skip = [f for f in files if f.lower().endswith('.pdf')]
W('subtree total=%d keep=%d skip_pdf=%d' % (len(files), len(keep), len(skip)))

# 3) extract text files into workspace (byte-verbatim)
prefix = '软著申请材料/'
os.makedirs(WS, exist_ok=True)
bad = 0
for f in keep:
    rel = f[len(prefix):] if f.startswith(prefix) else f
    dest = os.path.join(WS, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    rc, out, err = run_git(['show', '%s:%s' % (tip, f)], GRP, timeout=60)
    if rc != 0:
        bad += 1; W('extract fail %s' % f)
        continue
    open(dest, 'wb').write(out)
W('extract done keep=%d bad=%d' % (len(keep), bad))
if bad:
    save('PARTIAL', error='extraction bad=%d' % bad, tip=tip, phase='extract')

# 3b) local-only exclude guard so MiniGame loops never sweep the workspace
try:
    ex = os.path.join(WS_ROOT, '.git', 'info', 'exclude')
    os.makedirs(os.path.dirname(ex), exist_ok=True)
    body = ''
    if os.path.exists(ex):
        body = open(ex, encoding='utf-8', errors='replace').read()
    if '软著申请材料/' not in body:
        with open(ex, 'a', encoding='utf-8') as f:
            f.write('\n# r956 bm-b rz workspace (POOL-0011 scratch; do not sweep)\n软著申请材料/\n')
    W('info/exclude guarded')
except Exception as e:
    W('exclude guard fail %s' % e)

# 4) import generator module (registers fonts; BASE=workspace, REPO=MiniGame repo root)
gcc = None
try:
    spec = importlib.util.spec_from_file_location('gcc', os.path.join(WS, 'generate_copyright.py'))
    gcc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gcc)
except Exception as e:
    save('FAIL', error='generator import fail: %s' % e, tip=tip, phase='import')
    W('FAIL import %s' % e); sys.exit(2)

pre = {}
for k in B10:
    d = gcc.resolve_src(gcc.PROJECTS[k]) if k in gcc.PROJECTS else None
    pre[k] = d
    W('pre-verify %s src=%s' % (k, d))
missing_src = [k for k in B10 if not pre[k]]
W('pre-verify missing_src=%s' % missing_src)
save('RUNNING', phase='pre-verified', tip=tip, missing_src=missing_src,
     src_resolved={k: pre[k] for k in B10})

# 5) RAM gate (power law: r955 heartbeat measured free_ram=0.0; light batch, gate at 1.5GB)
waited = 0
ram0 = ram_avail_gb()
while ram_avail_gb() < 1.5 and waited < 2400:
    time.sleep(60); waited += 60
    W('ram gate wait avail=%.1fG waited=%ds' % (ram_avail_gb(), waited))
W('ram gate passed start_avail=%.1fG waited=%ds' % (ram0, waited))

# 6) run generator with EXPLICIT B10 keys
pyexe = sys.executable.replace('pythonw.exe', 'python.exe')
if not os.path.exists(pyexe):
    pyexe = sys.executable
rc_gen = -1
with open(GEN_LOG, 'w', encoding='utf-8') as gf:
    try:
        p = subprocess.Popen([pyexe, 'generate_copyright.py'] + B10, cwd=WS,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             creationflags=NO_WINDOW)
        for ln in p.stdout:
            gf.write(ln.decode('utf-8', 'replace').rstrip() + '\n')
            gf.flush()
        rc_gen = p.wait()
    except Exception as e:
        gf.write('GEN SPAWN FAIL: %s\n' % e)
W('generator rc=%s' % rc_gen)

# 7) post-verify + stats + CCPC copy
res = {}
for k in B10:
    cfg = gcc.PROJECTS[k]
    out_dir = os.path.join(WS, cfg.get('out_dir', '%s_%s' % (k, cfg['name_en'])))
    txt = os.path.join(out_dir, '%s_%s_源程序.txt' % (cfg['name_en'], cfg['version']))
    pdf = os.path.join(out_dir, '%s_%s_源程序.pdf' % (cfg['name_en'], cfg['version']))
    ok = os.path.exists(txt) and os.path.exists(pdf) and os.path.getsize(pdf) > 10000
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
    ccpc_ok = None
    if os.path.exists(pdf):
        ccpc = os.path.join(out_dir, 'CCPC 提交材料')
        os.makedirs(ccpc, exist_ok=True)
        try:
            shutil.copy2(pdf, os.path.join(ccpc, os.path.basename(pdf)))
            ccpc_ok = True
        except Exception as e:
            ccpc_ok = 'copy fail %s' % e
    res[k] = {'src': pre[k], 'txt': os.path.exists(txt), 'pdf_ok': ok, 'pages': pages,
              'lines': lines, 'cs_files': cs_files, 'guide_synced': guide_synced, 'ccpc': ccpc_ok}
    W('post %s pdf_ok=%s pages=%s lines=%s guide=%s ccpc=%s' % (k, ok, pages, lines, guide_synced, ccpc_ok))

gen_ok = (not missing_src) and all(v['pdf_ok'] for v in res.values())
status = 'GEN_DONE_OK' if gen_ok else ('PARTIAL' if any(v['pdf_ok'] for v in res.values()) else 'FAIL')
save(status, tip=tip, keys=res, missing_src=missing_src, gen_rc=rc_gen,
     workspace=WS, extracted=len(keep), skipped_pdfs=len(skip),
     next=('r957: verify B10 outputs -> group-repo tree-surgery commit on freshest origin/main tip '
           '(hash-object + mktree rebuild 软著申请材料 subtree + commit-tree + push) -> 报审台账§四 B机10款 rows '
           '-> POOL-0011 done receipt (card ID + done + commit sha evidence) in round report + heartbeat did'))
W('DONE status=%s gen_rc=%s tip=%s' % (status, rc_gen, tip[:12]))
