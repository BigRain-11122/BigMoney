import json

raw = open('results/crash_fuse.bm-a.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
sig = d.get('sigs', {})
# D-41 §2 five-things faces: cross-start robustness / config scan / exclusion marginal / cost-tax / behavior guardrail
keys = [k for k in sig if any(x in k for x in
        ['cross_start', 'exclusion', 'config_scan', 'cost_tax', 'behavior',
         'decision_chain', 'theme', 'tactic', 'sentiment', 'emotion'])]
for k in sorted(keys):
    v = sig[k]
    print('=====', k)
    print(' count:', v.get('count'), '| refusals:', v.get('refusals'),
          '| last_crash:', v.get('last_crash_ts'), '| machine:', v.get('machine'))
    note = v.get('note', '')
    if note:
        print(' note:', note[:400])
