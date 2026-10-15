# r955 bm-b salvage + restore driver (detached). Supersedes inline probe (--fix-thin
# requires --stdin - corrected here). Three phases, all local-first:
#  A) salvage orphaned tmp_packs (killed fetch/push chains, ~260MB): index-pack
#     --stdin --fix-thin per tmp (complete packs index, thin-with-missing-bases fail
#     harmlessly). Salvaged objects = free backfill, zero network.
#  B) missing-blob census (rev-list --missing=print), then if any deleted worktree
#     paths remain: retry the pathspec-from-file checkout (salvage may have provided
#     the blobs -> instant restore -> FACES_OK marker).
#  C) diagnostic: single-blob lazy fetch test (git cat-file blob <missing sha>) with
#     GIT_TRACE - evidence why checkout reads fail without lazy fetch (r956 channel
#     decision: patient lazy fetch vs peer bundle).
# Receipt = r956 consumption face. Idempotent relaunch. ASCII only. pythonw detached.
import json, os, subprocess, sys, time, datetime, glob

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r955bmb_salvage_driver.log'
RECEIPT = bm + r'\results\_r955bmb_salvage_receipt.json'
PATHS = bm + r'\results\_r955bmb_restore_paths.bin'
MARKER = bm + r'\results\_r955bmb_faces_marker.txt'
NO_WINDOW = 0x08000000
packdir = os.path.join(bm, '.git', 'objects', 'pack')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def receipt(d):
    base = {'driver': 'r955bmb salvage+restore (tmp_pack salvage -> census -> checkout retry -> lazy-fetch diagnostic)',
            'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
    base.update(d)
    with open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False, indent=1)

def run(cmd, cap, stdin_file=None, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=cap, creationflags=NO_WINDOW,
                           stdin=open(stdin_file, 'rb') if stdin_file else None, env=env)
        return r.returncode, (r.stdout + b'\n' + r.stderr).decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        return -99, 'TIMEOUT_%ss' % cap

W('salvage driver start pid=%d' % os.getpid())
receipt({'status': 'RUNNING', 'phase': 'salvage'})

# wait for the r955 patient-restore checkout process to exit (avoid concurrent restore)
for _ in range(360):
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              "(Get-CimInstance Win32_Process -Filter \"Name='git.exe'\" | Measure-Object).Count"],
                             capture_output=True, timeout=20, creationflags=NO_WINDOW)
        if '0' in out.stdout.decode('utf-8', 'replace'):
            break
    except Exception:
        break
    time.sleep(10)
W('checkout chains drained')

# ---- A) salvage tmp_packs ----
salvaged = 0
failed = 0
tmps = sorted(glob.glob(os.path.join(packdir, 'tmp_pack_*')))
tmps = [t for t in tmps if not t.endswith('.idx') and os.path.getsize(t) > 0]
W('phase A: tmp_packs=%d' % len(tmps))
for t in tmps:
    sz = os.path.getsize(t)
    rc, out = run(['git', '-C', bm, 'index-pack', '--stdin', '--fix-thin'], cap=900, stdin_file=t)
    tag = 'ok' if rc == 0 else 'fail'
    if rc == 0:
        salvaged += 1
    else:
        failed += 1
    W('salvage %s bytes=%d rc=%s tail=%s' % (os.path.basename(t), sz, rc,
        out.strip().split('\n')[-1][:100] if out.strip() else ''))
    if rc == 0:
        try:
            os.remove(t)  # canonical pack+idx now in store; tmp no longer needed
        except Exception:
            pass
W('phase A done: salvaged=%d failed=%d' % (salvaged, failed))
receipt({'status': 'RUNNING', 'phase': 'census', 'salvaged_packs': salvaged, 'failed_packs': failed})

# ---- B) census + checkout retry ----
p3 = subprocess.run(['git', '-C', bm, 'rev-list', '--objects', '--missing=print', '--all'],
                    capture_output=True, timeout=900)
missing = sum(1 for l in p3.stdout.decode('utf-8', 'replace').splitlines() if l.startswith('?')) if p3.returncode == 0 else -1
W('phase B: missing census=%s' % missing)
p2 = subprocess.run(['git', '-C', bm, 'ls-files', '-d', '-z'], capture_output=True, timeout=120)
n = p2.stdout.count(b'\0')
W('phase B: deleted worktree paths=%d' % n)
if n > 0:
    with open(PATHS, 'wb') as f:
        f.write(p2.stdout)
    rc, out = run(['git', '-C', bm, 'checkout', '--pathspec-from-file=' + PATHS, '--pathspec-file-nul', '--'], cap=3600)
    W('checkout retry rc=%s tail=%s' % (rc, out.strip().split('\n')[-1][:120] if out.strip() else ''))
    p2b = subprocess.run(['git', '-C', bm, 'ls-files', '-d'], capture_output=True, timeout=120)
    remaining = len([l for l in p2b.stdout.decode('utf-8', 'replace').splitlines() if l.strip()])
else:
    rc, remaining = 0, 0
p3b = subprocess.run(['git', '-C', bm, 'rev-list', '--objects', '--missing=print', '--all'],
                     capture_output=True, timeout=900)
missing2 = sum(1 for l in p3b.stdout.decode('utf-8', 'replace').splitlines() if l.startswith('?')) if p3b.returncode == 0 else -1
W('phase B done: remaining_deleted=%d missing_after=%s' % (remaining, missing2))
if remaining == 0:
    open(MARKER, 'w', encoding='utf-8').write('ALL_DELETED_RESTORED %s missing_after=%d\n' % (
        datetime.datetime.now().isoformat(timespec='seconds'), missing2))
    receipt({'status': 'FILL_DONE_RESTORE_OK', 'salvaged_packs': salvaged, 'failed_packs': failed,
             'deleted_paths': n, 'remaining_deleted': remaining, 'missing_blobs_after': missing2,
             'note': 'r956: faces on disk -> smoke 49/49 + S6 chain + orders full ack + SatEngine verify + attrition rescan + unshallow/pull warm window + merge side branches r951/r954'})
    W('driver done FILL_DONE_RESTORE_OK')
    sys.exit(0)

# ---- C) diagnostic: single-blob lazy fetch test ----
diag = {}
env = os.environ.copy()
env['GIT_TRACE'] = '1'
env['GIT_TRACE_PACKET'] = '1'
test_sha = None
p4 = subprocess.run(['git', '-C', bm, 'rev-list', '--objects', '--missing=print', '--all'],
                    capture_output=True, timeout=900)
for l in p4.stdout.decode('utf-8', 'replace').splitlines():
    if l.startswith('?'):
        test_sha = l[1:].split()[0]
        break
if test_sha:
    t0 = time.time()
    rc, out = run(['git', '-C', bm, 'cat-file', 'blob', test_sha], cap=120, env=env)
    diag = {'test_sha': test_sha, 'cat_file_rc': rc, 'elapsed': round(time.time() - t0, 1),
            'trace_tail': ' | '.join([x for x in out.split('\n') if x.strip()][-8:])[:600]}
    W('phase C: cat-file %s rc=%s elapsed=%ss trace_tail=%s' % (test_sha[:12], rc, diag['elapsed'], diag['trace_tail'][:200]))
receipt({'status': 'PARTIAL_OR_FAILED', 'salvaged_packs': salvaged, 'failed_packs': failed,
         'deleted_paths': n, 'remaining_deleted': remaining, 'missing_blobs_after': missing2,
         'checkout_retry_rc': rc, 'lazy_fetch_diag': diag,
         'note': 'r956: diag decides channel - lazy fetch alive -> patient re-run; dead -> peer bundle (MSG-20261014-2015) or alternate restore source'})
W('driver done PARTIAL_OR_FAILED remaining=%d' % remaining)
