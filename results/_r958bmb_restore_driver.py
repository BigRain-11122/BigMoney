# r958 bm-b batched restore driver v3 (supersedes r955 patient/salvage drivers, both dead:
# patient rc=128 at 01:51 connection dropped mid giant-pack; salvage died in census phase).
# Law lineage: r953 (Popen + tree-kill soft cap, never trust run(timeout) timely return),
# r954 (each persisted batch = guaranteed convergence vs single giant all-or-nothing pack),
# r955 (lazy fetch negotiation = only server-accepted batch face; raw-SHA wants rejected;
# tmp_pack salvage exhausted 26/26 early-EOF). Key discovery r958: some blobs already local
# (cat-file 0b6a24c 0.3s no-network read) -> census first, instant-write zero-missing chunks,
# then chunk-scoped checkout for the rest (each lazy fetch batch ~50 blobs, survives GFW night).
# Modes: census (read-only) | run (full loop, detached-safe, resumable by construction).
# Receipts: results/_r958bmb_census.json + _r958bmb_restore_receipt.json (progress-updated).
# Idempotent relaunch: fresh ls-files -d each start. ASCII only. pythonw compatible.
import json, os, subprocess, sys, time, datetime

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r958bmb_restore_driver.log'
RECEIPT = bm + r'\results\_r958bmb_restore_receipt.json'
CENSUS = bm + r'\results\_r958bmb_census.json'
CHUNK = 50
CAP = 420  # per-chunk soft cap seconds (50 blobs ~ few MB pack through night ssh)
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def write_json(path, d):
    d['ts'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

def deleted_paths():
    p = subprocess.run(['git', '-C', bm, 'ls-files', '-d', '-z'],
                       capture_output=True, timeout=120, creationflags=NO_WINDOW)
    return [x.decode('utf-8') for x in p.stdout.split(b'\0') if x]

def chunk_missing(paths):
    # rev-list --missing=print never lazy-fetches; scoped to chunk pathspecs
    cmd = ['git', '-C', bm, 'rev-list', '--objects', '--missing=print', 'HEAD', '--'] + paths
    try:
        q = subprocess.run(cmd, capture_output=True, timeout=300, creationflags=NO_WINDOW)
    except subprocess.TimeoutExpired:
        return -1
    if q.returncode != 0:
        return -1
    return sum(1 for l in q.stdout.splitlines() if l.startswith(b'?'))

def checkout_chunk(paths, cap):
    spec = bm + r'\results\_r958bmb_chunk_paths.bin'
    with open(spec, 'wb') as f:
        f.write(b'\0'.join(p.encode('utf-8') for p in paths) + b'\0')
    cmd = ['git', '-C', bm, 'checkout', '--pathspec-from-file=' + spec, '--pathspec-file-nul', '--']
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         creationflags=NO_WINDOW)
    try:
        out = p.communicate(timeout=cap)[0].decode('utf-8', 'replace')
        rc = p.returncode
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return -99, round(time.time() - t0, 1), 'TIMEOUT_TREE_KILLED'
    last = out.strip().splitlines()[-1][:150] if out.strip() else ''
    return rc, round(time.time() - t0, 1), last

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'census'
    paths = deleted_paths()
    W('start mode=%s deleted=%d' % (mode, len(paths)))
    if not paths:
        write_json(RECEIPT, {'status': 'ALL_RESTORED', 'remaining_deleted': 0,
                             'driver': 'r958bmb restore v3'})
        W('nothing to do - all faces on disk')
        return
    chunks = [paths[i:i + CHUNK] for i in range(0, len(paths), CHUNK)]
    census = [(c, chunk_missing(c)) for c in chunks]
    zero = [c for c, m in census if m == 0]
    need = [(c, m) for c, m in census if m > 0]
    unknown = [(c, m) for c, m in census if m == -1]
    write_json(CENSUS, {'deleted_paths': len(paths), 'chunks': len(chunks), 'chunk_size': CHUNK,
                        'chunks_zero_missing': len(zero), 'chunks_needs_fetch': len(need),
                        'unknown_census': len(unknown),
                        'missing_blobs_needs_fetch': sum(m for c, m in need)})
    W('census: zero=%d need=%d unknown=%d missing_blobs=%d' % (
        len(zero), len(need), len(unknown), sum(m for c, m in need)))
    if mode == 'census':
        return
    # zero-missing chunks first (instant, no network), then lazy-fetch chunks
    order = zero + [c for c, m in need] + [c for c, m in unknown]
    fails_streak = 0
    restored_files = 0
    for idx, c in enumerate(order):
        rc, el, tail = checkout_chunk(c, cap=CAP)
        rem = len(deleted_paths())
        if rc == 0:
            restored_files += len(c)
            fails_streak = 0
        else:
            fails_streak += 1
        write_json(RECEIPT, {'status': 'RUNNING', 'driver': 'r958bmb restore v3',
                             'chunk': idx + 1, 'of': len(order), 'chunk_size': len(c),
                             'chunk_rc': rc, 'chunk_elapsed_sec': el,
                             'remaining_deleted': rem, 'restored_files': restored_files,
                             'last_tail': tail})
        W('chunk %d/%d n=%d rc=%s el=%ss remaining=%d tail=%s' % (
            idx + 1, len(order), len(c), rc, el, rem, tail[:100]))
        if rem == 0:
            break
        if fails_streak >= 3:
            W('channel dead: 3 consecutive chunk fails -> PARTIAL stop')
            break
    rem = len(deleted_paths())
    status = 'ALL_RESTORED' if rem == 0 else 'PARTIAL_CHANNEL_STALLED'
    write_json(RECEIPT, {'status': status, 'driver': 'r958bmb restore v3',
                         'remaining_deleted': rem, 'restored_files': restored_files,
                         'next': 'r959: ALL_RESTORED -> smoke 49/49 + S6 chain + orders ack '
                                 'diff-scan + attrition rescan + unshallow/pull warm window + '
                                 'side-branch merges; PARTIAL -> idempotent relaunch or peer '
                                 'bundle channel MSG-20260914-2015'})
    W('done status=%s remaining=%d' % (status, rem))

main()
