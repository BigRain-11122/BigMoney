"""T-134 s2 fifth-candidate evidence rescan (r324 bm-c).

r304 evidence-order law + r312 gap fix: candidates whose data faces are
NOT present on this machine (data-host locality, e.g. p1c_stock frozen
panel = bm-a-local) cannot get live conversion smoke here -> deferred
bucket, not deleted. Rank axis: pool burn count x recency x family
activity x elapsed faces x locality.
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

by_runner = defaultdict(list)
for e in entries:
    r = str(e.get('runner', ''))
    name = os.path.basename(r) if r else '(none)'
    by_runner[name].append(e)

# ---- data-host locality faces (r312 gap fix) ----
# in-repo relative data dirs -> presence checkable on THIS machine
IN_REPO_PAT = re.compile(r'data[/\\](?:daily|futures|fundamental|repo|etf_ops|minute_feed|options)[/\\]?[\w./\\-]*')
# host-local / big-panel faces -> NOT portable to this machine
HOST_LOCAL_PATS = {
    'p1c_stock': 'p1c_stock',                       # frozen stock panel, bm-a host
    't18_deep_panel': 't18_deep_panel',              # deep axis panels, bm-a host
    'moneyflow': 'data/mf_',                        # MF panels, bm-a lane
    'sina_mf': 'data/sina_mf',                      # sina MF, bm-a lane
    'lhb': 'data/lhb',                               # LHB deep files
    'ths_panel': 'data/ths',                         # THS agg panel, bm-a lane
    'Money02': 'Money02',                            # legacy host tree (never touch)
}

def locality_of(path):
    src = ''
    try:
        src = open(os.path.join(ROOT, path), encoding='utf-8', errors='replace').read()
    except OSError:
        return {'src': 'unreadable', 'local': 'unknown', 'faces': [], 'missing': []}
    host_hits = [n for n, p in HOST_LOCAL_PATS.items() if p in src]
    inrepo = set()
    for m in IN_REPO_PAT.findall(src):
        inrepo.add(m.replace('\\', '/'))
    missing = [d for d in sorted(inrepo)
               if not os.path.exists(os.path.join(ROOT, d.split('data/')[0] + 'data/' + d.split('data/')[1].split('/')[0]))]
    if host_hits:
        return {'src': 'read', 'local': False, 'faces': host_hits, 'missing': missing}
    if missing:
        return {'src': 'read', 'local': False, 'faces': [], 'missing': missing}
    return {'src': 'read', 'local': True, 'faces': sorted(inrepo)[:6], 'missing': []}

# ---- elapsed faces: audit blocks of declared outputs + pool product audits ----
ELAPSED_HINTS = {}
for path, info in single.items():
    name = os.path.basename(path)
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

# priors from prior falsification/measurement rounds (explicit, sourced)
KNOWN = {
    'innovation_quota_w10.py': 'light 0.09s/cell measured (r304 quota nulls) - deprioritized',
    'national_team_s3_review.py': 'segment-light perm path family (r304) - deprioritized',
    'sentiment_axes_derive.py': 'numpy-vectorized short batch (r304) - deprioritized',
    'p1e_synth.py': 'FALSIFIED: write-once delivered, family 6/6 dormant (r310)',
    'grid_dualface_backtest.py': 'FALSIFIED: judged 0/30 line closed (r310)',
    'bond_panel_puller.py': 'EXCLUDED: I/O puller not a CPU face (r311)',
    'p1e_ic_batch.py': 'EXCLUDED: family dormant (r311)',
    'decision_chain_v2.py': 'EXCLUDED: consumed via converted v3 mp path (r311)',
    'gpu_factor_matrix.py': 'EXCLUDED: GPU face, not a CPU ProcessPool target (O-1136 GPU audit lane)',
}

rows = []
for path in sorted(single):
    name = os.path.basename(path)
    ents = by_runner.get(name, [])
    st = Counter(e.get('status', '?') for e in ents)
    latest = max((str(e.get('entered_at', '')) for e in ents), default='')
    loc = locality_of(path)
    prior = KNOWN.get(name)
    if prior is None and name.startswith('innovation_quota_w') and name != 'innovation_quota_w10.py':
        prior = 'family prior: w10 nulls measured light 0.09s/cell (r304) -> family deprioritized pending per-file elapsed evidence'
    rows.append({
        'runner': name, 'path': path,
        'pool_entries': len(ents), 'pool_statuses': dict(st),
        'latest_entered_at': latest or None,
        'census_pool_entry_count': single[path].get('pool_entry_count'),
        'elapsed_faces': ELAPSED_HINTS.get(name),
        'locality': loc,
        'prior': prior,
    })

def rank_key(r):
    falsified = 1 if (r['prior'] or '').startswith(('FALSIFIED', 'EXCLUDED')) else 0
    light = 1 if r['prior'] and ('deprioritized' in r['prior'] or 'light' in r['prior']) else 0
    local = 0 if r['locality'].get('local') is True else 1
    return (falsified, light, local, -r['pool_entries'], r['latest_entered_at'] or '')

rows.sort(key=rank_key)
out = {
    'scan': 'T-134 s2 fifth-candidate evidence rescan (locality-fixed)',
    'round': 'r324 bm-c',
    'law': 'r304 evidence-order law + r312 data-host locality gap fix',
    'census_summary': CEN.get('summary'),
    'single_core_count': len(single),
    'falsified_or_excluded': {k: v for k, v in KNOWN.items()},
    'ranking': rows,
}
fp = os.path.join(ROOT, 'results/_r324bmc_s2_evidence_scan.json')
json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('top 12 by pool-truth x locality rank:')
for r in rows[:12]:
    print(f"  {r['runner']}: entries={r['pool_entries']} local={r['locality'].get('local')} "
          f"faces={r['locality'].get('faces')} latest={r['latest_entered_at']} "
          f"audit={json.dumps(r['elapsed_faces'].get('audit_hits'))[:160] if isinstance(r['elapsed_faces'], dict) else '-'} prior={r['prior']}")
print('artifact:', fp)
