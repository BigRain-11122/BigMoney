"""r619 bm-b: locate exact k-holes in live nulls faces + hunt missing lines in all candidate blobs.

r614 cure: churn-commit blob byte-identical k-union backfill + os.replace + contiguity assert.
Hunt space: origin/main b6fa63650, 0a1e2eb5e, e44df6cf2, 98a88490f, f275451fd, a9c3d35eb,
5952f0e3b, index :0:, pre-rebase main tip (5952f0e3b is tip), worktree.
"""
import subprocess, json, sys

def blob(rev, path):
    spec = f':{rev}:{path}' if isinstance(rev, int) else f'{rev}:{path}'
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None

def jlines(text):
    if text is None:
        return []
    return [l for l in text.strip().splitlines() if l.strip()]

FACES = ['results/fund_value_p1/nulls.jsonl', 'results/fund_quality_p1/nulls.jsonl',
         'results/fund_divlowvol_p1/nulls.jsonl']
REVS = ['b6fa63650', '0a1e2eb5e', 'e44df6cf2', '98a88490f', 'f275451fd', 'a9c3d35eb', '5952f0e3b', 0]

for p in FACES:
    wt = jlines(open(p, encoding='utf-8').read())
    by_k = {}
    dup = []
    for l in wt:
        k = json.loads(l)['k']
        if k in by_k:
            dup.append(k)
        by_k[k] = l
    ks = sorted(by_k)
    holes = [k for k in range(0, ks[-1] + 1) if k not in by_k]
    print(f'== {p}: wt n={len(wt)} k 0..{ks[-1]} holes={holes} dup={dup}')
    for h in holes:
        found = []
        for rev in REVS:
            for l in jlines(blob(rev, p)):
                if json.loads(l)['k'] == h:
                    found.append((str(rev), l))
                    break
        print(f'   hole k={h}: ' + ('RECOVERABLE from ' + found[0][0] if found else 'NOT IN ANY BLOB'))
        for src, l in found[:1]:
            print(f'      line: {l[:140]}')

# engine history window analysis
p = 'results/saturation_engine/history_bm-b.jsonl'
wt = jlines(open(p, encoding='utf-8').read())
wt_ts = [json.loads(l)['ts'] for l in wt]
print(f'== {p}: wt n={len(wt)} oldest={wt_ts[0]} newest={wt_ts[-1]}')
for rev in ['5952f0e3b', 'a9c3d35eb', 'f275451fd', '98a88490f', 'e44df6cf2', '0a1e2eb5e', 'b6fa63650']:
    rev_lines = jlines(blob(rev, p))
    rev_by_ts = {json.loads(l)['ts']: l for l in rev_lines}
    missing = [t for t in rev_by_ts if t > wt_ts[0] and t not in set(wt_ts)]
    if missing:
        print(f'   {rev}: lines within wt window but absent from wt: {missing}')
    # also lines <= wt oldest that rev has (cap-trimmed, do not restore)
