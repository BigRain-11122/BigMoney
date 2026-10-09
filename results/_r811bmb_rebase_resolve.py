# _r811bmb_rebase_resolve.py - rebase conflict resolver for r811 commit replay
# Canon: r810 resolver lineage (_r810bmb_rebase_resolve.py, r803 generic lineage). Rules:
#  - rolling ledgers (compute_audit.json, regime_state.json): ts-keyed row union zero-loss
#  - token_usage.json: per-key max merge
#  - single-writer bm-a faces (dashboard_status.json/.js, daily_scorecard.json,
#    strategy_scorecard.json, scorecard_v1.json): take ours (=origin/bm-a, r378 law,
#    r809 addendum "dashboard+scorecard faces r378 law" precedent)
#  - everything else (same-day deterministic S6 regen faces): take theirs (=replayed bm-b side,
#    later-ignition law, r810 precedent)
# In a rebase replay: stage2=ours=origin/base side, stage3=theirs=replayed bm-b commit.
import subprocess, json, sys, os

def git(*args):
    return subprocess.run(['git']+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

def ours(p): return git('show', ':2:'+p)
def theirs(p): return git('show', ':3:'+p)

out = subprocess.run(['git','status','--porcelain'], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
uu = [l[3:].strip().replace('"','') for l in out.splitlines() if l[:2] in ('UU','AA')]
receipt = {'round': 'r811', 'resolved': [], 'skipped_ours': [], 'merged': [], 'uu_count': len(uu)}

A_FACES = {'results/dashboard_status.json','results/dashboard_status.js','results/daily_scorecard.json',
           'results/strategy_scorecard.json','results/scorecard_v1.json'}
LEDGER_UNION = {'results/compute_audit.json','results/regime_state.json'}
LEDGER_MAX = {'results/token_usage.json'}
UNION_KEYS = ('history','rows','samples','transitions','triggers')

for p in uu:
    if p in A_FACES:
        body = ours(p)
        receipt['skipped_ours'].append(p)
    elif p in LEDGER_UNION:
        try:
            a = json.loads(ours(p) or '{}'); b = json.loads(theirs(p) or '{}')
            merged = dict(a)
            for k, v in b.items():
                if k in UNION_KEYS and isinstance(v, list) and isinstance(merged.get(k), list):
                    seen = {(r.get('ts'), r.get('machine', r.get('host',''))) for r in merged[k] if isinstance(r, dict)}
                    for r in v:
                        key = (r.get('ts'), r.get('machine', r.get('host',''))) if isinstance(r, dict) else (str(r),'')
                        if key not in seen:
                            merged[k].append(r); seen.add(key)
                elif k not in merged:
                    merged[k] = v
                elif isinstance(v, (int, float)) and isinstance(merged[k], (int, float)):
                    merged[k] = max(merged[k], v)
                elif isinstance(v, str) and isinstance(merged[k], str):
                    merged[k] = v if v >= merged[k] else merged[k]
            body = json.dumps(merged, ensure_ascii=False, indent=2)
        except Exception as e:
            body = theirs(p); receipt.setdefault('merge_fallback', {})[p] = str(e)
        receipt['merged'].append(p)
    elif p in LEDGER_MAX:
        try:
            a = json.loads(ours(p) or '{}'); b = json.loads(theirs(p) or '{}')
            merged = dict(a)
            for k, v in b.items():
                if isinstance(v, (int, float)) and isinstance(merged.get(k), (int, float)):
                    merged[k] = max(merged[k], v)
                elif k not in merged:
                    merged[k] = v
            body = json.dumps(merged, ensure_ascii=False, indent=2)
        except Exception:
            body = theirs(p)
        receipt['merged'].append(p)
    else:
        body = theirs(p)
        receipt['resolved'].append(p)
    if body is not None and not body.endswith('\n'):
        body += '\n'
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(body or '')

for p in uu:
    subprocess.run(['git','add',p], capture_output=True)

with open('results/_r811bmb_rebase_resolve.json','w',encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
print('RESOLVED', len(uu), 'faces; ours:', len(receipt['skipped_ours']), 'merged:', len(receipt['merged']), 'theirs:', len(receipt['resolved']))
