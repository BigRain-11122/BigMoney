# r955 bm-b patient restore driver (supersedes r954 blobfill = treadmill #2)
# Root cause: raw-SHA chunk fetch ("git fetch --no-tags origin <shas>") is REJECTED by
# GitHub server ("fatal: bad revision" + "did not send all necessary objects") - server
# does not serve unadvertised wants outside promisor lazy-fetch negotiation (9+ batches
# x 2 attempts, zero progress, r954 receipt batches_done=0).
# Only proven bulk channel = lazy fetch triggered by a checkout (r951: one pack warmed
# ~29K objects over ~65min at night bandwidth). r951-r954 treadmill pattern = soft caps
# (600s etc) killed each pack mid-receive = whole pack discarded = zero progress.
# This driver: NO timeout kill (soft cap 4h only as anti-zombie). Restores ONLY deleted
# worktree paths (git ls-files -d -> pathspec-from-file), preserving modified files
# owned by other sessions (CODELY.md staged state, Tools/iteration_prompt.txt G5 weave).
# Progress logged every 60s (incoming tmp_pack growth = visibility for next rounds).
# Receipt json = r956 consumption face. Idempotent relaunch. ASCII only. pythonw detached.
import json, os, subprocess, sys, time, datetime

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r955bmb_patient_restore.log'
RECEIPT = bm + r'\results\_r955bmb_patient_restore_receipt.json'
PATHS = bm + r'\results\_r955bmb_restore_paths.bin'
MARKER = bm + r'\results\_r955bmb_faces_marker.txt'
NO_WINDOW = 0x08000000
SOFT_CAP = 4 * 3600  # anti-zombie only; observed full lazy fetch ~65min r951

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def receipt(d):
    base = {'driver': 'r955bmb patient restore (single lazy fetch, no timeout kill)',
            'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
    base.update(d)
    with open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False, indent=1)

def pack_progress():
    d = os.path.join(bm, '.git', 'objects', 'pack')
    try:
        tmps = [os.path.getsize(os.path.join(d, x)) for x in os.listdir(d) if x.startswith('tmp_pack')]
        packs = len([x for x in os.listdir(d) if x.endswith('.pack')])
        return 'tmp_packs=%d tmp_bytes=%d packs=%d' % (len(tmps), sum(tmps), packs)
    except Exception as e:
        return 'pack_probe_err %s' % str(e)[:60]

W('patient restore start pid=%d soft_cap=%ds' % (os.getpid(), SOFT_CAP))

# 1) snapshot deleted paths (restore targets; index-only op, no blobs needed)
p = subprocess.run(['git', '-C', bm, 'ls-files', '-d', '-z'], capture_output=True, timeout=60)
n = p.stdout.count(b'\0')
W('deleted paths snapshot=%d' % n)
if n == 0:
    # still write marker if nothing to restore
    open(MARKER, 'w', encoding='utf-8').write('ALL_PRESENT %s\n' % datetime.datetime.now().isoformat(timespec='seconds'))
    receipt({'status': 'ALL_PRESENT', 'deleted_paths': 0,
             'note': 'nothing deleted on worktree; r956: recheck + missing-blob census'})
    W('driver done ALL_PRESENT')
    sys.exit(0)
with open(PATHS, 'wb') as f:
    f.write(p.stdout)
receipt({'status': 'RUNNING', 'deleted_paths': n, 'soft_cap': SOFT_CAP,
         'note': 'r956: on FILL_DONE_RESTORE_OK -> smoke 49/49 + S6 chain + orders ack + attrition rescan + unshallow/pull warm window'})

# 2) checkout restore - the ONE operation whose lazy fetch must never be killed
cmd = ['git', '-C', bm, 'checkout', '--pathspec-from-file=' + PATHS, '--pathspec-file-nul', '--']
W('checkout start: restore %d deleted paths (lazy fetch in pack, patient)' % n)
proc = subprocess.Popen(cmd, stdout=open(LOG, 'a', encoding='utf-8'),
                         stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
t0 = time.time()
rc = None
while True:
    rc = proc.poll()
    if rc is not None:
        break
    el = int(time.time() - t0)
    if el > SOFT_CAP:
        W('SOFT CAP %ds exceeded -> tree-kill checkout (anti-zombie), receipt for r956 decision' % SOFT_CAP)
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(proc.pid)], capture_output=True, creationflags=NO_WINDOW)
        try:
            proc.communicate(timeout=30)
        except Exception:
            pass
        receipt({'status': 'TIMEOUT_CAPPED', 'deleted_paths': n, 'elapsed_sec': el,
                 'last_progress': pack_progress(),
                 'note': 'r956: if progress showed bytes flowing -> relaunch patient (idempotent); if stalled -> peer bundle channel'})
        W('driver done TIMEOUT_CAPPED elapsed=%ds' % el)
        sys.exit(2)
    if el % 60 < 2:
        W('waiting elapsed=%ds rc=None %s' % (el, pack_progress()))
    time.sleep(2)

# 3) verify
el = int(time.time() - t0)
W('checkout exited rc=%s elapsed=%ds' % (rc, el))
p2 = subprocess.run(['git', '-C', bm, 'ls-files', '-d'], capture_output=True, timeout=60)
remaining = len([l for l in p2.stdout.decode('utf-8', 'replace').splitlines() if l.strip()])
# missing-blob census (plumbing rev-list, no index op)
p3 = subprocess.run(['git', '-C', bm, 'rev-list', '--objects', '--missing=print', '--all'],
                    capture_output=True, timeout=600)
missing = 0
if p3.returncode == 0:
    for l in p3.stdout.decode('utf-8', 'replace').splitlines():
        if l.startswith('?'):
            missing += 1
if rc == 0 and remaining == 0:
    open(MARKER, 'w', encoding='utf-8').write(
        'ALL_DELETED_RESTORED %s missing_blobs_after=%d\n' % (datetime.datetime.now().isoformat(timespec='seconds'), missing))
    receipt({'status': 'FILL_DONE_RESTORE_OK', 'deleted_paths': n, 'elapsed_sec': el,
             'remaining_deleted': remaining, 'missing_blobs_after': missing,
             'pack_tail': pack_progress(),
             'note': 'r956: faces on disk -> smoke 49/49 + S6 chain + orders full ack + saturation_engine verify (S4U tick auto-revive) + attrition rescan + unshallow/pull --rebase warm window + merge side branches r951/r954'})
    W('driver done FILL_DONE_RESTORE_OK remaining=%d missing_after=%d' % (remaining, missing))
else:
    receipt({'status': 'PARTIAL_OR_FAILED', 'deleted_paths': n, 'checkout_rc': rc,
             'elapsed_sec': el, 'remaining_deleted': remaining,
             'missing_blobs_after': missing, 'pack_tail': pack_progress(),
             'note': 'r956: read log tail; PARTIAL -> relaunch idempotent (resumes); FAILED -> forensics'})
    W('driver done PARTIAL_OR_FAILED rc=%s remaining=%d' % (rc, remaining))
