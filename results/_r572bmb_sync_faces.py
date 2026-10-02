import subprocess, os, json, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'

def git_bytes(args):
    r = subprocess.run(['git', '-C', REPO] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s failed: %s' % (args, r.stderr.decode('utf-8', 'replace')[:300]))
    return r.stdout

# 1) origin-owned stale/missing faces -> checkout list
status = git_bytes(['status', '--porcelain']).decode('utf-8', 'replace')
keep_local = {
    'results/autofill_state.bm-b.json',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
}
jsonl_union = ['results/pool_core_samples.jsonl', 'results/x2_watch_log.jsonl']
checkout = []
for line in status.splitlines():
    line = line.strip()
    if not line:
        continue
    st, path = line[:2], line[3:].strip()
    if path in keep_local:
        print('KEEP-LOCAL  %s' % path)
        continue
    if path in jsonl_union:
        continue
    if st.strip() in ('D', 'M'):
        checkout.append(path)
print('CHECKOUT_COUNT=%d' % len(checkout))

# 2) jsonl union faces (r570 law): origin bytes verbatim base + local unique dict lines
for path in jsonl_union:
    ob = git_bytes(['show', 'origin/main:' + path])
    with open(os.path.join(REPO, path), 'rb') as f:
        lb = f.read()
    if lb == ob:
        print('UNION %s: identical, skip' % path)
        continue
    o_lines = [l for l in ob.split(b'\n') if l.strip()]
    l_lines = [l for l in lb.split(b'\n') if l.strip()]
    o_set = set(o_lines)
    uniq = [l for l in l_lines if l not in o_set]
    # r570 type gate: local unique lines must parse as dict
    good = []
    for l in uniq:
        try:
            if isinstance(json.loads(l.decode('utf-8')), dict):
                good.append(l)
        except Exception:
            print('UNION %s: NON-DICT local line dropped: %s' % (path, l[:80]))
    print('UNION %s: origin=%d local=%d local_unique=%d (dict-ok=%d)' % (path, len(o_lines), len(l_lines), len(uniq), len(good)))
    if not good:
        checkout.append(path)
        print('  -> local subset/stale, checkout origin')
    else:
        # r530 bytes law: preserve origin trailing newline shape then append unique lines
        base = ob if ob.endswith(b'\n') or ob.endswith(b'\r\n') else ob + b'\n'
        out = base + b'\n'.join(good) + b'\n'
        with open(os.path.join(REPO, path), 'wb') as f:
            f.write(out)
        # post-verify: all lines dict-parse (r570 two-gate)
        bad = 0
        for l in out.split(b'\n'):
            if not l.strip():
                continue
            try:
                assert isinstance(json.loads(l.decode('utf-8')), dict)
            except Exception:
                bad += 1
        assert bad == 0, 'post-verify non-dict lines=%d' % bad
        print('  -> union written: origin base + %d local lines, post-verify all-dict OK' % len(good))

# 3) checkout
if checkout:
    r = subprocess.run(['git', '-C', REPO, 'checkout', '--', '--'] + checkout, capture_output=True)
    if r.returncode != 0:
        # r326: multi-pathspec checkout with one invalid = whole batch silently abandoned; retry per-file
        print('BATCH CHECKOUT FAILED, per-file retry: %s' % r.stderr.decode('utf-8', 'replace')[:200])
        ok = 0
        for p in checkout:
            r2 = subprocess.run(['git', '-C', REPO, 'checkout', '--', p], capture_output=True)
            if r2.returncode != 0:
                print('  FAIL %s: %s' % (p, r2.stderr.decode('utf-8', 'replace')[:150]))
            else:
                ok += 1
        print('PER-FILE OK=%d/%d' % (ok, len(checkout)))
    else:
        print('BATCH CHECKOUT OK')

# 4) final status
st2 = git_bytes(['status', '--porcelain']).decode('utf-8', 'replace')
print('===FINAL STATUS===')
print(st2)
