# r951 bm-b inventory: HEAD tree vs disk vs odb (cold-index safe: zero index ops)
# Outputs results/_r951bmb_inventory.json + console summary
import json, os, subprocess, datetime, hashlib

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
def gb(args, timeout=120, input_bytes=None):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    r = subprocess.run(['git'] + args, cwd=bm, env=env, input=input_bytes, capture_output=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

out = {'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}

# repo refs / shallow / filter
rc, o, _ = gb(['rev-parse', 'HEAD', 'refs/heads/main', 'refs/remotes/origin/main'])
out['refs'] = o.decode().split()
rc, o, _ = gb(['rev-parse', '--is-shallow-repository'])
out['shallow'] = o.decode().strip()
rc, o, _ = gb(['config', '--get', 'remote.origin.promisor'])
out['promisor'] = o.decode().strip()
rc, o, _ = gb(['config', '--get', 'remote.origin.partialclonefilter'])
out['filter'] = o.decode().strip()
rc, o, _ = gb(['config', '--get', 'remote.origin.url'])
out['url'] = o.decode().strip()

# HEAD tree blobs (sha -> path, size)
rc, o, e = gb(['ls-tree', '-r', '-l', 'HEAD'])
blobs = {}
for line in o.decode('utf-8', 'replace').split('\n'):
    if not line.strip():
        continue
    meta, path = line.split('\t', 1)
    parts = meta.split()
    # <mode> <type> <sha>\t<size>\tpath   (with -l: size in meta after sha, separated by tab)
    mode, typ, sha = parts[0], parts[1], parts[2]
    if typ == 'blob':
        size = parts[3] if len(parts) > 3 else '-'
        blobs[sha] = (path, int(size) if size != '-' else 0)
out['head_blob_count'] = len(blobs)
out['head_blob_bytes'] = sum(v[1] for v in blobs.values())

# have-set: objects present in local odb (blobs only)
rc, o, e = gb(['cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)'])
have = set()
for line in o.decode('utf-8', 'replace').split('\n'):
    if not line.strip():
        continue
    sha, typ = line.split()
    if typ == 'blob':
        have.add(sha)
out['odb_blob_count'] = len(have)

missing = {sha: blobs[sha] for sha in blobs if sha not in have}
out['missing_head_blobs'] = len(missing)
out['missing_head_bytes'] = sum(v[1] for v in missing.values())

# disk walk
disk = {}
for root, dirs, files in os.walk(bm):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '.codely-cli')]
    for fn in files:
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, bm).replace('\\', '/')
        try:
            disk[rel] = os.path.getsize(p)
        except OSError:
            pass
out['disk_file_count'] = len(disk)

# per-face stats
faces = ['config', 'fleet', 'docs', 'engine', 'firm', 'knowledge', 'legacy', 'live', 'data']
face_stats = {}
by_path = {v[0]: (sha, v[1]) for sha, v in blobs.items()}
for f in faces:
    tree_files = {p: (sha, sz) for p, (sha, sz) in by_path.items() if p == f or p.startswith(f + '/')}
    missing_on_disk = [p for p in tree_files if p not in disk]
    present = [p for p in tree_files if p in disk]
    missing_blob_missing_disk = [p for p, (sha, sz) in tree_files.items() if sha not in have and p not in disk]
    face_stats[f] = {
        'tree_files': len(tree_files),
        'on_disk': len(present),
        'missing_on_disk': len(missing_on_disk),
        'need_fetch': len(missing_blob_missing_disk),
        'bytes_needed': sum(tree_files[p][1] for p in missing_blob_missing_disk),
    }
out['faces'] = face_stats

# blobs warmable by hash-object (on disk + not in odb)
warmable = [(p, sz) for sha, (p, sz) in missing.items() if p in disk]
out['warmable_by_hash_object'] = len(warmable)
out['warmable_bytes'] = sum(w[1] for w in warmable)
out['must_fetch'] = len(missing) - len(warmable)
out['must_fetch_bytes'] = sum(v[1] for sha, v in missing.items() if v[0] not in disk)

with open(bm + r'\results\_r951bmb_inventory.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print('REFS main=%s origin/main=%s shallow=%s filter=%s' % (
    out['refs'][1][:12] if len(out['refs']) > 1 else '?',
    out['refs'][2][:12] if len(out['refs']) > 2 else 'ABSENT',
    out['shallow'], out['filter']))
print('HEAD blobs=%d (bytes=%d) odb_blobs=%d missing=%d (bytes=%d)' % (
    out['head_blob_count'], out['head_blob_bytes'], out['odb_blob_count'],
    out['missing_head_blobs'], out['missing_head_bytes']))
print('warmable_by_hash_object=%d (bytes=%d) must_fetch=%d (bytes=%d)' % (
    out['warmable_by_hash_object'], out['warmable_bytes'], out['must_fetch'], out['must_fetch_bytes']))
for f in faces:
    s = face_stats[f]
    print('FACE %-10s tree=%-5d disk=%-5d miss_disk=%-5d need_fetch=%-5d (%d B)' % (
        f, s['tree_files'], s['on_disk'], s['missing_on_disk'], s['need_fetch'], s['bytes_needed']))
print('INVENTORY_OK')
