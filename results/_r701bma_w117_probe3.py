# W117 probe v3: exact product paths + registry tails (engine wave state)
import re, json, glob, os

out = {}
for w in (115, 116, 117, 118):
    hits = []
    for pat in (f'results/**/n1_w{w}/shard-*.json', f'results/n1_w{w}/shard-*.json', f'results/**/n1_w{w}_results.json'):
        hits += glob.glob(pat, recursive=True)
    out[f'w{w}'] = [h.replace('results/', '') for h in sorted(set(hits))]

# registry tails: find last band rows in perpetual_faces.py via line scan
def tail_rows(path, key):
    src = open(path, encoding='utf-8', errors='replace').read().splitlines()
    rows = []
    for i, l in enumerate(src):
        m = re.match(r'\s*(\d+)\s*:\s*\{"a"', l)
        if m:
            rows.append((int(m.group(1)), i + 1, l.strip()[:120]))
    return rows

pf_rows = tail_rows('scripts/perpetual_faces.py', 'N1')
out['pf_last6'] = pf_rows[-6:]
n1_rows = tail_rows('scripts/perpetual_faces_n1.py', 'N1')
out['n1_last6'] = n1_rows[-6:]

# latest landed finalize values (anchor source)
p = 'results/perpetual_faces/n1_w115_results.json'
if os.path.exists(p):
    j = json.load(open(p, encoding='utf-8'))
    keys = {}
    for k in ('K', 'chain_head', 'mu', 'merged_mu', 'sigma', 'merged_sigma', 'se_mu', 'k', 'skill_line'):
        if k in j:
            keys[k] = j[k]
    out['w115_results_face'] = {'top_keys': list(j.keys())[:18], 'sample': keys}
    # commit-time anchor fields used by prereg
    for kk in ('audit', 'wave', 'evidence_cutoff'):
        if kk in j:
            out['w115_results_face'][kk] = j[kk] if not isinstance(j[kk], dict) else str(j[kk])[:120]

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
