# r969 bm-b tmp_pack salvage (r955 law): zero-network object materialization.
# 52 tmp_pack_* orphans (507MB) in .git/objects/pack = fetch packs fully
# downloaded but killed before index-pack completed (25-min runner tree-kill
# clusters 20:19/20:38/02:24-02:25). git index-pack --stdin --fix-thin
# materializes complete packs into odb; thin-base-missing packs fail
# harmlessly (kept for later windows). On rc=0 the source tmp file is
# redundant (content preserved in new indexed pack) -> safe delete.
# Effect probe: batch-check how many of the currently-missing (ls-files -d)
# files now have local blobs -> v5 driver materializes them next pass with
# rc=0 checkout (no network). No working-tree writes here (checkout lane =
# v5 driver only, no double-drive). Laws: r953 Popen+tree-kill caps,
# r955 salvage law, r960 no-race (driver owns checkout lane).
import datetime, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
PACKDIR = BM + r'\.git\objects\pack'
LOG = BM + r'\results\_r969bmb_salvage.log'
OUT = BM + r'\results\_r969bmb_salvage.json'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def index_one(path, cap):
    p = subprocess.Popen(['git', '-C', BM, 'index-pack', '--stdin', '--fix-thin'],
                         stdin=open(path, 'rb'), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    try:
        out = p.communicate(timeout=cap)[0].decode('utf-8', 'replace')
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return -99, 'TIMEOUT_%ss' % cap

def missing_paths():
    p = subprocess.run(['git', '-C', BM, 'ls-files', '-d', '-z'], capture_output=True,
                       timeout=120, creationflags=NO_WINDOW)
    return [x.decode('utf-8') for x in p.stdout.split(b'\0') if x]

def blobs_local(paths):
    # one batch-check process: feed "HEAD:<path>" revs, count resolvable+local blobs
    if not paths:
        return 0, 0
    p = subprocess.Popen(['git', '-C', BM, 'cat-file', '--batch-check=%(objectname)',
                          '--buffer'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
    n_local = n_err = 0
    for path in paths:
        try:
            p.stdin.write(('HEAD:%s\n' % path).encode('utf-8'))
        except Exception:
            n_err += 1
    try:
        p.stdin.close()
    except Exception:
        pass
    for path in paths:
        line = p.stdout.readline().decode('utf-8', 'replace').strip()
        if line and 'missing' not in line and 'dangling' not in line:
            n_local += 1
        else:
            n_err += 1
    p.wait(timeout=60)
    return n_local, n_err

W('salvage start')
res = {'driver': 'r969bmb tmp_pack salvage (r955 law)',
       'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}

pre_missing = missing_paths()
pre_local, pre_err = blobs_local(pre_missing)
W('pre: missing_files=%d blobs_already_local=%d' % (len(pre_missing), pre_local))
res['pre_missing_files'] = len(pre_missing)
res['pre_blobs_local'] = pre_local

tmps = sorted([os.path.join(PACKDIR, f) for f in os.listdir(PACKDIR)
               if f.startswith('tmp_pack_')], key=os.path.getsize)
W('tmp_pack candidates: %d' % len(tmps))
ok_count, fail_count, deleted = 0, 0, 0
results = []
for t in tmps:
    sz = os.path.getsize(t)
    cap = 300 if sz > 10 * 1024 * 1024 else 120
    rc, out = index_one(t, cap)
    entry = {'file': os.path.basename(t), 'bytes': sz, 'rc': rc, 'out_tail': out.strip()[-100:]}
    if rc == 0:
        ok_count += 1
        try:
            os.remove(t)
            deleted += 1
            entry['source_deleted'] = True
        except Exception as e:
            entry['source_delete_error'] = str(e)[:80]
        W('SALVAGED %s (%d bytes) %s' % (os.path.basename(t), sz, out.strip()[-80:]))
    else:
        fail_count += 1
        W('keep %s rc=%s (%d bytes): %s' % (os.path.basename(t), rc, sz, out.strip()[-80:]))
    results.append(entry)

post_missing = missing_paths()
post_local, post_err = blobs_local(post_missing)
W('post: missing_files=%d blobs_now_local=%d (delta=%d)'
  % (len(post_missing), post_local, post_local - pre_local))
res.update({'packs_indexed_ok': ok_count, 'packs_kept_fail': fail_count,
            'sources_deleted': deleted, 'kept_bytes': sum(
                os.path.getsize(os.path.join(PACKDIR, f)) for f in os.listdir(PACKDIR)
                if f.startswith('tmp_pack_')),
            'post_missing_files': len(post_missing), 'post_blobs_local': post_local,
            'blob_local_delta': post_local - pre_local,
            'effect_note': ('blobs now local materialize via v5 driver next pass '
                            '(checkout rc=0 instant, no network; driver owns checkout '
                            'lane, no double-drive)'),
            'ts_done': datetime.datetime.now().astimezone().isoformat(timespec='seconds')})
res['pack_results'] = results
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('salvage done ok=%d fail=%d deleted=%d blob_delta=%d'
  % (ok_count, fail_count, deleted, post_local - pre_local))
print(json.dumps({k: v for k, v in res.items() if k != 'pack_results'},
                 ensure_ascii=False, indent=1))
