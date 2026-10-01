import json, subprocess, os, re

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(args):
    r = subprocess.run(['git'] + args, capture_output=True)
    return r.stdout.decode('utf-8', 'replace')

print('=== PERPETUAL_FACES.md sec4 table tail (origin) ===')
txt = git(['show', 'origin/main:research/PERPETUAL_FACES.md'])
rows = [l for l in txt.splitlines() if re.match(r'\|\s*W\d+\s*\|', l)]
print('table rows:', len(rows))
for l in rows[-4:]:
    print(l[:200])

print()
print('=== N1_BANDS tail (scripts/perpetual_faces.py, origin) ===')
pf = git(['show', 'origin/main:scripts/perpetual_faces.py'])
for l in pf.splitlines():
    if re.search(r'N1_BANDS|WAVE_CONFIGS\s*=|SEED_REGISTRY\s*=', l):
        print(l[:120])
# extract last N1_BANDS entries
m = re.search(r'N1_BANDS\s*=\s*\{(.*?)\n\}', pf, re.S)
if m:
    entries = re.findall(r'\s*(\d+):\s*\(([^)]*)\)\s*,?\s*\n', m.group(1))
    for k, v in entries[-4:]:
        print('N1_BANDS[%s] = (%s)' % (k, v[:100]))
m2 = re.search(r'WAVE_CONFIGS\s*=\s*\{(.*?)\n\}', pf, re.S)
if m2:
    wkeys = re.findall(r'\s*(\d+):\s*\{', m2.group(1))
    print('WAVE_CONFIGS keys:', wkeys)
    tail = m2.group(1)
    idx = tail.rfind('}'), 
    print('WAVE_CONFIGS tail rows:')
    for l in tail.splitlines()[-16:]:
        if l.strip():
            print('  ', l[:150])

print()
print('=== SEED_REGISTRY (origin) ===')
m3 = re.search(r'SEED_REGISTRY\s*=\s*\{(.*?)\n\}', pf, re.S)
if m3:
    print(m3.group(1)[:800])

print()
print('=== probe seeds (r335 law: runner probe seed cluster) ===')
for l in pf.splitlines():
    if 'PROBE_SEEDS' in l or re.search(r'= 95_00\d|=95_00\d', l):
        print(l[:150])

print()
print('=== LOWAMP-P3-NULLS status (pool origin truth) ===')
pool_raw = git(['show', 'origin/main:results/runnable_pool.json'])
try:
    pool = json.loads(pool_raw)
except Exception as e:
    print('pool parse fail:', e)
    pool = {}
found = 0
for k, v in pool.items():
    if isinstance(v, dict) and 'LOWAMP-P3-NULLS' in str(k):
        found += 1
        print('entry:', k)
        print('  status:', v.get('status'), '| owner:', v.get('owner'))
        sh = v.get('shards', [])
        print('  shards:', [(s.get('shard_key', s.get('id', '?')), s.get('status'), s.get('owner')) for s in sh][:5])
        print('  shard done count:', sum(1 for s in sh if s.get('status') == 'done'), '/', len(sh))
print('LOWAMP-P3-NULLS entries found:', found)

print()
print('=== nulls.jsonl row count (local product) ===')
for cand in ['results/lowamp_p3/nulls.jsonl', 'results/lowamp_p2/nulls.jsonl']:
    if os.path.exists(cand):
        n = sum(1 for _ in open(cand, 'rb'))
        print(cand, 'lines:', n)
