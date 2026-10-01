"""T-134 s2 fourth-candidate evidence rescan (r311 bm-c).

r304 evidence-order law: rank single_core conversion candidates by
historical burn elapsed x re-burn likelihood -- NOT by family reputation
or file size. Both prior magnitude-ranked candidates were falsified
(p1e_synth = write-once delivered family 6/6 dormant; grid_dualface =
judged 0/30 line closed), so the matrix is rebuilt from pool truth:
burn counts x recency x family activity, with honest elapsed faces where
artifact audit blocks are findable.
"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEN = json.load(open(os.path.join(ROOT, 'results/multicore_census.json'), encoding='utf-8'))
pool = json.load(open(os.path.join(ROOT, 'results/runnable_pool.json'), encoding='utf-8'))
entries = pool.get('entries', pool) if isinstance(pool, dict) else pool

single = {k: v for k, v in CEN['verdicts'].items() if v.get('verdict') == 'single_core'}
print('single_core census count:', len(single))

# pool truth: entries by runner script name
by_runner = defaultdict(list)
for e in entries:
    r = str(e.get('runner', ''))
    name = os.path.basename(r) if r else '(none)'
    by_runner[name].append(e)

# artifact audit elapsed scan: find audit blocks in results/ JSONs with
# workers==1 and a batch-ish id; map back to runner by known output dirs
# is unreliable, so elapsed faces here come from a bounded grep of the
# runners' own declared output paths (OUT/... constants) -- best-effort,
# honest when absent.
ELAPSED_HINTS = {}
for path, info in single.items():
    name = os.path.basename(path)
    src = ''
    try:
        src = open(os.path.join(ROOT, path), encoding='utf-8', errors='replace').read()
    except OSError:
        ELAPSED_HINTS[name] = {'artifact_scan': 'source-unreadable'}
        continue
    outs = set(re.findall(r'results[/\\][\w./\\-]+\.(?:json|jsonl)', src))
    hits = []
    for rel in list(outs)[:8]:
        fp = os.path.join(ROOT, rel.replace('\\', '/'))
        if not os.path.exists(fp):
            continue
        try:
            d = json.load(open(fp, encoding='utf-8'))
        except Exception:
            continue
        aud = d.get('audit') if isinstance(d, dict) else None
        if isinstance(aud, dict) and aud.get('elapsed_sec'):
            hits.append({'file': rel, 'elapsed_sec': aud.get('elapsed_sec'),
                         'workers': aud.get('workers'),
                         'machine': aud.get('machine')})
    ELAPSED_HINTS[name] = {'declared_outputs': len(outs), 'audit_hits': hits[:4]}

# known family-activity annotations from prior falsification rounds
# (r304/r305 measured or judged; kept as explicit priors with sources)
KNOWN = {
    'quota_w10_nulls.py': 'light 0.09s/cell measured (r304) - deprioritized',
    'national_team_scan.py': 'segment-light perm path (r304) - deprioritized',
    'sentiment_axes_gate.py': 'numpy-vectorized short batch (r304) - deprioritized',
    'p1e_synth.py': 'FALSIFIED: write-once delivered, family 6/6 dormant (r310)',
    'grid_dualface_backtest.py': 'FALSIFIED: judged 0/30 line closed (r310)',
}

rows = []
for path in sorted(single):
    name = os.path.basename(path)
    ents = by_runner.get(name, [])
    st = Counter(e.get('status', '?') for e in ents)
    latest = max((str(e.get('entered_at', '')) for e in ents), default='')
    rows.append({
        'runner': name, 'path': path,
        'pool_entries': len(ents), 'pool_statuses': dict(st),
        'latest_entered_at': latest or None,
        'census_pool_entry_count': single[path].get('pool_entry_count'),
        'elapsed_faces': ELAPSED_HINTS.get(name),
        'prior': KNOWN.get(name),
    })

# rank: burned-via-pool count desc, then recency, falsified/known-light last
def rank_key(r):
    falsified = 1 if (r['prior'] or '').startswith('FALSIFIED') else 0
    light = 1 if (r['prior'] or '').startswith('light') or \
              (r['prior'] or '').startswith('segment') or \
              (r['prior'] or '').startswith('numpy') else 0
    return (falsified, light, -r['pool_entries'], r['latest_entered_at'] or '')

rows.sort(key=rank_key)
out = {
    'scan': 'T-134 s2 fourth-candidate evidence rescan',
    'round': 'r311 bm-c',
    'law': 'r304 evidence-order law (elapsed x likelihood, no intuition)',
    'census_summary': CEN.get('summary'),
    'single_core_count': len(single),
    'falsified_candidates': {k: v for k, v in KNOWN.items() if v.startswith('FALSIFIED')},
    'ranking': rows,
}
fp = os.path.join(ROOT, 'results/_r311bmc_s2_evidence_scan.json')
json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('top 10 by pool-truth rank:')
for r in rows[:10]:
    print(f"  {r['runner']}: entries={r['pool_entries']} {r['pool_statuses']} "
          f"latest={r['latest_entered_at']} prior={r['prior']}")
print('artifact:', fp)
