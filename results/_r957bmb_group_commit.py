# r957 bm-b group-repo tree-surgery commit: POOL-0011 B机10款 delivery.
# Cold-index law: pure object-db ops only (ls-tree/hash-object/mktree/commit-tree/push);
# zero worktree/index touch. Overlay merge: origin tip subtree entries are KEPT unless
# workspace file differs (never delete remote-only entries e.g. 111 skipped PDFs).
# Staleness guards: generate_copyright.py + README.md origin blobs must equal the
# r956 extraction base tip (717d5fb4b9a2) or abort STALE (manual merge face).
# Push: fetch-first (r953 pack-shrink law) + Popen taskkill /T /F soft cap (r953 timeout law).
# One idempotent retry on non-FF reject. Receipt = results/_r957bmb_group_commit_receipt.json.
import datetime, json, os, subprocess, sys, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP = r'C:\Fluxgroup\FluxGroup'
WS = r'C:\Fluxgroup\MiniGame\MiniGame\软著申请材料'
LOG = BM + r'\results\_r957bmb_group_commit.log'
REC = BM + r'\results\_r957bmb_group_commit_receipt.json'
BASE_TIP = '717d5fb4b9a29cd49fbcf7994dc26ebf5d7bb272'  # r956 extraction base
SUB = '软著申请材料'
ORDERS_ROW = ('| 10-15 03:5x | **软著B机10款源程序复跑批交付回执（POOL-0011 done·O-20261014-1035 B10 段执行件·bm-b r957）** '
             '| ①B机10款源程序全产出（源程序 txt/pdf+指南源程序量自动回写）：G04 螺丝仙人 2869行/24文件/58页·G05 爆护 5235行/30文件/60页·'
             'G07 人从众 3073行/20文件/60页·G08 开学啦 5725行/29文件/60页·G13 我想有个农场 3910行/24文件/60页·G14 大不了开饭馆 3535行/19文件/60页·'
             'G20 夜聊斋 2385行/21文件/48页·G23 这张牌有诈 1862行/13文件/38页·G26 归园田居 3121行/17文件/60页（现盘波2填充最新代码）·'
             'G28 这一箭稳了 2592行/12文件/52页——不足60页四款（G04/G20/G23/G28）全部提交诚实标注；②r956 FAIL 根因定谳=bm-b 盘源码目录为裸名'
             '（ScrewOut/... 无 G 前缀·九根零命中）→修复=generate_copyright.py B机10款 src_rel 双候选（C机 G09Y/G10 先例范式）+SRC_ROOTS 第十根 '
             r'C:\Fluxgroup\MiniGame；③CCPC 提交材料 源程序 PDF 10/10 归拢（_r957bmb_rz_receipt.json GEN_DONE_OK）；④报审台账§四 B机10款行销账'
             '（软著申请材料/README.md）；⑤组仓树手术 commit+push（本 commit sha）+证据=bigmoney results/_r957bmb_rz_receipt.json+'
             '_r957bmb_group_commit_receipt.json | done（bm-b 收口·POOL-0011+done+本行+双 receipt 证据指针） |')
MSG = ('bm-b r957: POOL-0011 B机10款 源程序复跑批交付（B10 源程序 txt/pdf 10/10 + CCPC 10/10 + 报审台账§四 B10 行销账 + orders done 回执；'
       'src 双候选根因修复=裸名源码目录九根零命中→C机 G09Y/G10 双候选先例+第十根；证据=bigmoney results/_r957bmb_rz_receipt.json GEN_DONE_OK）')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(status, **kw):
    d = {'driver': 'r957bmb group tree-surgery commit (POOL-0011 delivery)',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'status': status}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('save status=%s %s' % (status, {k: kw[k] for k in list(kw)[:6]}))

def git(args, timeout=90, inp=None, cap=0):
    """Run git in GRP. cap>0 => Popen with taskkill /T /F soft cap (r953 law)."""
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    full = ['git', '-c', 'core.quotepath=off'] + args
    if not cap:
        try:
            r = subprocess.run(full, cwd=GRP, env=env, input=inp, capture_output=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return -1, b'', b'TIMEOUT'
    p = subprocess.Popen(full, cwd=GRP, env=env, stdin=subprocess.PIPE if inp is not None else None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(input=inp, timeout=cap)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True)
        try:
            out, err = p.communicate(timeout=30)
        except Exception:
            out, err = b'', b''
        return -9, out, b'SOFTCAP_KILLED ' + err[:200]

def lsz_split(data):
    """Parse 'mode SP type SP sha TAB path NUL' -z listing."""
    ents = []
    for chunk in data.split(b'\x00'):
        if not chunk:
            continue
        meta, _, path = chunk.partition(b'\t')
        mode, typ, sha = meta.split(b' ')
        ents.append((mode.decode(), typ.decode(), sha.decode(), path.decode('utf-8')))
    return ents

def mktree(entries):
    """entries: list of (mode, type, sha, name). Returns tree sha. --missing: blob:none
    partial clone keeps unchanged blobs lazy (r950 recipe: mktree --missing)."""
    payload = b''
    for mode, typ, sha, name in entries:
        payload += ('%s %s %s\t' % (mode, typ, sha)).encode('ascii') + name.encode('utf-8') + b'\x00'
    rc, out, err = git(['mktree', '-z', '--missing'], inp=payload, timeout=60)
    if rc != 0:
        raise RuntimeError('mktree rc=%s err=%s' % (rc, err.decode('utf-8', 'replace')[:200]))
    return out.decode().strip()

def build_tree(flat, prefix):
    """flat: dict path->(mode,typ,sha) for paths strictly under prefix (posix rel). Build nested tree."""
    children = {}
    subdirs = set()
    for path, ent in flat.items():
        if '/' in path:
            head = path.split('/', 1)[0]
            subdirs.add(head)
        else:
            children[path] = ent
    entries = []
    for name, (mode, typ, sha) in sorted(children.items()):
        entries.append((mode, typ, sha, name))
    for head in sorted(subdirs):
        sub = {p.split('/', 1)[1]: e for p, e in flat.items() if p.split('/', 1)[0] == head}
        entries.append(('040000', 'tree', build_tree(sub, prefix + head + '/'), head))
    return mktree(entries)

def surgery(tip):
    """One full surgery pass on given tip. Returns (new_commit_sha, changed_files, orders_blob)."""
    # staleness guards
    for f in (SUB + '/generate_copyright.py', SUB + '/README.md'):
        rc1, o1, _ = git(['ls-tree', tip, '--', f])
        rc2, o2, _ = git(['ls-tree', BASE_TIP, '--', f])
        s1 = o1.decode().split('\t')[0].strip() if rc1 == 0 else '?'
        s2 = o2.decode().split('\t')[0].strip() if rc2 == 0 else '?'
        if rc1 != 0 or s1 != s2:
            raise RuntimeError('STALE_BASE %s tip_blob=%s base_blob=%s' % (f, s1, s2))
    # flat map of subtree at tip
    rc, out, _ = git(['ls-tree', '-r', '-z', tip, '--', SUB])
    if rc != 0:
        raise RuntimeError('ls-tree subtree rc=%s' % rc)
    flat = {}
    for mode, typ, sha, path in lsz_split(out):
        rel = path[len(SUB) + 1:]
        flat[rel] = (mode, typ, sha)
    # overlay workspace files
    changed = []
    payload_bytes = 0
    for root, dirs, files in os.walk(WS):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            if fn.endswith('.pyc'):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, WS).replace(os.sep, '/')
            rc, out, _ = git(['hash-object', '--', full])
            if rc != 0:
                W('hash-object(read) fail %s rc=%s' % (rel, rc)); continue
            new_sha = out.decode().strip()
            old = flat.get(rel)
            if old and old[2] == new_sha:
                continue
            rc, out, err = git(['hash-object', '-w', '--', full])
            if rc != 0:
                raise RuntimeError('hash-object -w fail %s: %s' % (rel, err.decode('utf-8', 'replace')[:150]))
            flat[rel] = ('100644', 'blob', out.decode().strip())
            changed.append(rel)
            payload_bytes += os.path.getsize(full)
    W('overlay changed=%d payload=%.1fMB' % (len(changed), payload_bytes / 1048576.0))
    # rebuild subtree tree
    sub_tree = build_tree(flat, SUB + '/')
    # orders.md append
    rc, out, _ = git(['show', tip + ':docs/orders.md'], timeout=120)
    if rc != 0:
        raise RuntimeError('orders show rc=%s' % rc)
    orders_txt = out.decode('utf-8')
    if 'POOL-0011 done' in orders_txt:
        raise RuntimeError('ORDERS_ROW_ALREADY_PRESENT')
    orders_txt = orders_txt.rstrip('\n') + '\n' + ORDERS_ROW + '\n'
    rc, out, err = git(['hash-object', '-w', '--stdin'], inp=orders_txt.encode('utf-8'), timeout=60)
    if rc != 0:
        raise RuntimeError('orders hash-object rc=%s' % rc)
    orders_blob = out.decode().strip()
    # docs subtree (r957 fix: 'ls-tree tip -- docs' returns the docs entry ITSELF,
    # so stripping len('docs') yielded name='' -> empty-filename tree entry -> remote
    # index-pack reject 03:40. 'ls-tree tip:docs' lists CHILDREN with names relative
    # to docs/, which is what the replace loop expects.)
    rc, out, _ = git(['ls-tree', '-z', tip + ':docs'])
    if rc != 0:
        raise RuntimeError('ls-tree docs rc=%s' % rc)
    docs_entries = []
    for mode, typ, sha, name in lsz_split(out):
        sha2 = orders_blob if name == 'orders.md' else sha
        docs_entries.append((mode, typ, sha2, name))
    docs_tree = mktree(docs_entries)
    # root tree
    rc, out, _ = git(['ls-tree', '-z', tip])
    if rc != 0:
        raise RuntimeError('ls-tree root rc=%s' % rc)
    root_entries = []
    for mode, typ, sha, path in lsz_split(out):
        if path == SUB:
            root_entries.append((mode, typ, sub_tree, path))
        elif path == 'docs':
            root_entries.append((mode, typ, docs_tree, path))
        else:
            root_entries.append((mode, typ, sha, path))
    root_tree = mktree(root_entries)
    rc, out, err = git(['commit-tree', root_tree, '-p', tip, '-m', MSG], timeout=60)
    if rc != 0:
        raise RuntimeError('commit-tree rc=%s %s' % (rc, err.decode('utf-8', 'replace')[:150]))
    return out.decode().strip(), changed, payload_bytes, orders_blob

def push(sha):
    rc, out, _ = git(['fetch', 'origin', 'main'], timeout=180, cap=240)
    W('pre-push fetch rc=%s' % rc)
    rc, out, err = git(['push', 'origin', sha + ':refs/heads/main'], timeout=300, cap=420)
    W('push rc=%s out=%s err=%s' % (rc, out.decode('utf-8', 'replace')[-300:], err.decode('utf-8', 'replace')[-300:]))
    if rc != 0:
        return False, err.decode('utf-8', 'replace')
    rc, out, _ = git(['ls-remote', 'origin', 'main'], timeout=90, cap=120)
    remote = out.decode().split()[0] if out else ''
    return remote == sha, remote

W('driver start pid=%d' % os.getpid())
save('RUNNING', phase='init')
rc, out, _ = git(['fetch', 'origin'], timeout=180, cap=240)
W('fetch rc=%s' % rc)
if rc != 0:
    save('FAIL', error='fetch rc=%s' % rc, phase='fetch'); sys.exit(2)
rc, out, _ = git(['rev-parse', 'origin/main'])
tip = out.decode().strip()
W('tip=%s' % tip[:12])
try:
    sha, changed, payload, orders_blob = surgery(tip)
except RuntimeError as e:
    save('ABORT', error=str(e), phase='surgery'); sys.exit(3)
save('RUNNING', phase='surgery-done', new_commit=sha, changed_count=len(changed),
     payload_mb=round(payload / 1048576.0, 1), changed_sample=changed[:8])
ok, remote = push(sha)
if not ok:
    W('retry once after refetch')
    rc, out, _ = git(['fetch', 'origin'], timeout=180, cap=240)
    if rc == 0:
        rc, out, _ = git(['rev-parse', 'origin/main'])
        tip2 = out.decode().strip()
        if tip2 != tip:
            W('tip moved %s -> %s, re-surgery' % (tip[:12], tip2[:12]))
            try:
                sha, changed, payload, orders_blob = surgery(tip2)
            except RuntimeError as e:
                save('ABORT', error='retry: ' + str(e), phase='surgery-retry'); sys.exit(3)
        ok, remote = push(sha)
if not ok:
    save('FAIL', error='push not verified', remote=remote, new_commit=sha, phase='push'); sys.exit(4)
save('PUSHED_VERIFIED', new_commit=sha, remote_main=remote, changed_count=len(changed),
     payload_mb=round(payload / 1048576.0, 1), base_tip=tip, orders_blob=orders_blob,
     changed_files=changed,
     note='POOL-0011 done evidence: group commit sha + bigmoney results/_r957bmb_rz_receipt.json')
W('DONE PUSHED_VERIFIED sha=%s' % sha)
