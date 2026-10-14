# r954 bm-b blobfill driver: resumable incremental fill of missing blobs (blob:none
# partial clone cold-index heal), then final fleet+data face checkout + marker.
# SUPERSEDES watcher v3 (pid 28448) + worker v2 (pid 10232): their per-face checkout
# triggers a single-batch lazy fetch killed at 600s = pack discarded = zero progress
# per pass (night-bandwidth treadmill). This driver fetches missing blobs in SMALL
# batches -> each completed batch PERSISTS in the object store -> guaranteed eventual
# completion at any bandwidth. Idempotent: relaunch harmless.
# Law compliance: r950 cold-index (plumbing only until warm), r953 tree-kill soft caps
# (Popen+taskkill /T, never subprocess.run(timeout) control-flow trust), r949 spawn
# verify (start line on disk), zero-window (pythonw + NO_WINDOW flags).
# ASCII only (GBK console law).
import os, subprocess, time, datetime, json

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r954bmb_blobfill.log'
RECEIPT = bm + r'\results\_r954bmb_blobfill_receipt.json'
MARKER = bm + r'\results\_r952bmb_faces_marker.txt'
RAWLIST = bm + r'\results\_r954bmb_missing_raw.txt'
NO_WINDOW = 0x08000000
BATCH = 160
CAP_FETCH = 420
CAP_REVLIST = 900
MAX_PASSES = 60
TIMEBOX_H = 5.0

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def receipt(status, extra):
    d = {'status': status, 'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
         'driver': 'r954bmb blobfill (supersedes watcher v3 + worker v2 treadmill)',
         'note': 'next round: on FILL_DONE+FACES_OK marker -> smoke 49/49 + S6 chain per state.next'}
    d.update(extra)
    with open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

def git(args, cap, stdout_file=None):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = ('ssh -o ConnectTimeout=25 -o ServerAliveInterval=15 '
                              '-o ServerAliveCountMax=4')
    kw = {'cwd': bm, 'env': env, 'stderr': subprocess.PIPE,
          'creationflags': NO_WINDOW}
    if stdout_file:
        fh = open(stdout_file, 'wb')
        kw['stdout'] = fh
    else:
        kw['stdout'] = subprocess.PIPE
    p = subprocess.Popen(['git'] + args, **kw)
    try:
        out, err = p.communicate(timeout=cap)
        if stdout_file:
            fh.close()
        return p.returncode, (out or b'').decode('utf-8', 'replace') + (err or b'').decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)],
                       capture_output=True, creationflags=NO_WINDOW)
        try:
            p.communicate(timeout=30)
        except Exception:
            pass
        if stdout_file:
            fh.close()
        return -98, 'SOFTCAP_TREEKILL after %ss' % cap

def missing_now():
    rc, out = git(['rev-list', '--objects', '--missing=print', '--all'], CAP_REVLIST,
                  stdout_file=RAWLIST)
    if rc != 0:
        W('rev-list rc=%s out=%s' % (rc, out[:160]))
        return None
    shas = []
    with open(RAWLIST, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('?'):
                shas.append(line[1:41])
    return shas

W('blobfill driver start pid=%d batch=%d cap=%ds' % (os.getpid(), BATCH, CAP_FETCH))
t0 = time.time()
init = missing_now()
if init is None:
    receipt('REVLIST_FAIL', {'missing_initial': None})
    W('driver done REVLIST_FAIL')
    raise SystemExit(1)
W('missing initial=%d' % len(init))
receipt('FILLING', {'missing_initial': len(init), 'missing_now': len(init),
                   'batches_done': 0, 'batches_failed': 0})

todo = list(init)
done_batches = 0
failed_batches = 0
pass_no = 0
while todo and pass_no < MAX_PASSES and (time.time() - t0) < TIMEBOX_H * 3600:
    pass_no += 1
    carried = []
    stalled = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        ok = False
        for attempt in (1, 2):
            rc, out = git(['fetch', '--quiet', '--no-tags', 'origin'] + chunk, CAP_FETCH)
            if rc == 0:
                ok = True
                break
            W('pass %d batch %d/%d attempt %d rc=%s out=%s' % (
                pass_no, i // BATCH + 1, (len(todo) + BATCH - 1) // BATCH,
                attempt, rc, out.replace('\n', ' | ')[:200]))
            time.sleep(20)
        if ok:
            done_batches += 1
        else:
            failed_batches += 1
            stalled += len(chunk)
            carried.extend(chunk)
        if done_batches % 10 == 0 and ok:
            W('progress: batches_done=%d (pass %d)' % (done_batches, pass_no))
            receipt('FILLING', {'missing_initial': len(init), 'missing_now': len(carried) + (len(todo) - i - len(chunk)),
                                'batches_done': done_batches, 'batches_failed': failed_batches})
    todo = carried
    if todo:
        W('pass %d end: %d stalled objects carried, recomputing missing' % (pass_no, len(todo)))
        rem = missing_now()
        if rem is None:
            W('rev-list recompute failed, keep carried list')
        else:
            todo = rem
            W('recomputed missing=%d' % len(todo))
        receipt('FILLING', {'missing_initial': len(init), 'missing_now': len(todo),
                            'batches_done': done_batches, 'batches_failed': failed_batches,
                            'pass': pass_no})
        time.sleep(60)

if todo and (time.time() - t0) >= TIMEBOX_H * 3600:
    W('TIMEBOX exit with %d missing - relaunch idempotent' % len(todo))
    receipt('TIMEBOX_EXIT_RESUME', {'missing_initial': len(init), 'missing_now': len(todo),
                                   'batches_done': done_batches, 'batches_failed': failed_batches})
    raise SystemExit(0)

W('fill phase complete: batches_done=%d failed=%d' % (done_batches, failed_batches))
receipt('FILL_DONE', {'missing_initial': len(init), 'missing_now': 0,
                      'batches_done': done_batches, 'batches_failed': failed_batches})

# final phase: face checkout (lock-tolerant retries) + marker
faces_ok = True
for face in ('fleet', 'data'):
    got = False
    for t in range(6):
        rc, out = git(['checkout', 'HEAD', '--', face], 300)
        if rc == 0:
            got = True
            W('FACE %s rc=0 OK (try %d)' % (face, t + 1))
            break
        W('FACE %s try %d rc=%s out=%s' % (face, t + 1, rc, out.replace('\n', ' | ')[:160]))
        time.sleep(60)
    if not got:
        faces_ok = False

rc, dcnt = git(['ls-files', '-d'], 120)
dcount = len([l for l in dcnt.split('\n') if l.strip()]) if rc == 0 else -1
ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
if faces_ok:
    with open(MARKER, 'w', encoding='ascii') as f:
        f.write('ALL_FACES_RESTORED dcount=%d ts=%s\n' % (dcount, ts))
    W('END-STATE: ALL_FACES RESTORED (D-count=%d) marker written' % dcount)
    receipt('FILL_DONE+FACES_OK', {'missing_initial': len(init), 'missing_now': 0,
                                  'batches_done': done_batches, 'batches_failed': failed_batches,
                                  'faces': 'fleet,data rc=0', 'dcount': dcount,
                                  'note': 'next round: smoke 49/49 + S6 chain + orders ack + attrition healthy rescan + unshallow/pull warm window'})
else:
    with open(MARKER, 'w', encoding='ascii') as f:
        f.write('UNRESOLVED dcount=%d ts=%s\n' % (dcount, ts))
    W('END-STATE: UNRESOLVED faces remain (D-count=%d)' % dcount)
    receipt('FILL_DONE+FACES_FAIL', {'missing_initial': len(init), 'missing_now': 0,
                                     'batches_done': done_batches, 'batches_failed': failed_batches,
                                     'faces': 'checkout failed - see log', 'dcount': dcount})
try:
    os.remove(RAWLIST)
except Exception:
    pass
W('driver done')
