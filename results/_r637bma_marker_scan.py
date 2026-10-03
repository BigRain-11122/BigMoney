"""r637 bm-a: post-rebase marker scan (r423 law: python re.M full-repo, PS Select-String misses ^=======$)."""
import re, subprocess, sys

r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8')
tracked_dirty = [l[3:].strip() for l in r.stdout.splitlines() if l[:2] != '??']
pat = re.compile(r'<<<<<<<|^=======$|>>>>>>>|\|\|\|\|\|\|\|')
hits = []
files = tracked_dirty + ['round_reports-bm-a.md', 'state-bm-a.json', 'research/pit-pool.md',
                         'results/runnable_pool.json', 'fleet/machines/bm-a.json']
for f in files:
    try:
        t = open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    for i, ln in enumerate(t.splitlines(), 1):
        if pat.search(ln.rstrip('\r')):
            hits.append((f, i, ln[:60]))
print('marker hits:', len(hits))
for h in hits[:10]:
    print(' ', h)
sys.exit(1 if hits else 0)
