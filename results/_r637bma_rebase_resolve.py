"""r637 bm-a rebase conflict resolution per canon (r630 union for append-only, take-new for derive/status)."""
import subprocess

APPEND_ONLY = ['results/pool_core_samples.jsonl']

def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace')
    print((r.stdout or r.stderr).strip()[:300])
    return r

# 1) three-way union for append-only faces (r630: :2: U :3: U worktree-clean-lines)
for p in APPEND_ONLY:
    b2 = subprocess.run(['git', 'show', ':2:%s' % p], capture_output=True).stdout.decode('utf-8', 'ignore')
    b3 = subprocess.run(['git', 'show', ':3:%s' % p], capture_output=True).stdout.decode('utf-8', 'ignore')
    wt = open(p, encoding='utf-8', errors='replace').read()
    def clean(t):
        out, skip = [], False
        for ln in t.splitlines():
            if ln.startswith('<<<<<<<') or ln.startswith('>>>>>>>'):
                skip = not ln.startswith('>>>>>>>') if ln.startswith('<<<<<<<') else False
                continue
            if ln.startswith('=======') and skip:
                continue
            if ln.startswith('======='):
                continue
            out.append(ln)
        return out
    # simpler: strip the three marker kinds entirely, keep all content lines from all three sources
    def lines_of(t):
        return [l for l in t.splitlines() if not (l.startswith('<<<<<<<') or l.startswith('=======') or l.startswith('>>>>>>>'))]
    L2, L3, LW = lines_of(b2), lines_of(b3), lines_of(wt)
    seen, merged = set(), []
    for src in (L2, L3, LW):
        for l in src:
            k = l.rstrip('\r')
            if k not in seen and k.strip():
                seen.add(k)
                merged.append(k)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(merged) + '\n')
    print('%s union: %d+%d+%d -> %d unique' % (p, len(L2), len(L3), len(LW), len(merged)))
    git('add', p)

# 2) take-new (theirs) for the rest
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8')
take = [l[3:].strip() for l in r.stdout.splitlines()
        if l[:2] in ('UU', 'AA') and l[3:].strip() not in APPEND_ONLY]
print('take-new count:', len(take))
for p in take:
    git('checkout', '--theirs', '--', p)
    git('add', p)

r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8')
left = [l for l in r.stdout.splitlines() if l[:2] in ('UU', 'AA', 'AU', 'UA', 'DU', 'UD')]
print('remaining conflicts:', len(left))
for l in left[:10]:
    print(' ', l)
