# W117 freeze-support probe: read band registry tails, upstream finalize state, seat vacancy.
# Read-only. r446 probe-file law; r587 machine-derive law.
import re, json, os, glob, subprocess

def read(p):
    return open(p, encoding='utf-8', errors='replace').read()

out = {}

# 1) pf N1_BANDS tail (scripts/perpetual_faces.py)
pf = read('scripts/perpetual_faces.py')
m = re.search(r'N1_BANDS[^=]*=\s*{', pf)
rows = re.findall(r'(\d+)\s*:\s*\{[^{}]*?"a"\s*:\s*"([\d_]+)\.\.([\d_]+)"[^{}]*?"b"\s*:\s*"([\d_]+)\.\.([\d_]+)"', pf)
rows = sorted({int(r[0]): r for r in rows}.items())
out['pf_band_rows'] = len(rows)
out['pf_tail'] = rows[-4:]

# engine_owner rows (ownership count)
own = re.findall(r'"engine_owner"\s*:\s*"(\w+)"', pf)
from collections import Counter
out['engine_owner_counts'] = dict(Counter(own))

# 2) n1 WAVE_CONFIGS tail
cands = [f for f in glob.glob('scripts/*.py') if 'n1' in f.lower()]
out['n1_files'] = cands
for f in cands:
    s = read(f)
    if 'WAVE_CONFIGS' in s:
        wc = re.findall(r'(\d+)\s*:\s*\{[^{}]*"a"\s*:\s*"([\d_]+)\.\.([\d_]+)"[^{}]*"b"\s*:\s*"([\d_]+)\.\.([\d_]+)"', s)
        if wc:
            wcm = sorted({int(r[0]): r for r in wc}.items())
            out.setdefault('wave_configs', {})[f] = {'n': len(wcm), 'tail': wcm[-3:]}

# 3) upstream finalize landed state: results/n1_w<NN>_results.json
res = sorted(glob.glob('results/n1_w*_results.json'), key=lambda p: int(re.search(r'n1_w(\d+)', p).group(1)))
out['finalize_files'] = [os.path.basename(p) for p in res[-4:]]
if res:
    latest = res[-1]
    try:
        j = json.load(open(latest, encoding='utf-8'))
        out['latest_finalize'] = {'file': os.path.basename(latest),
                                  'keys': [k for k in j.keys()][:20]}
    except Exception as e:
        out['latest_finalize_err'] = str(e)

# 4) any n1_w115/w116/w117 products on disk (burn state)
for w in (114, 115, 116, 117):
    prods = glob.glob(f'results/n1_w{w}/*.json') + glob.glob(f'results/n1_w{w}_*')
    out[f'n1_w{w}_products'] = len(prods)

# 5) seat vacancy: scan origin inbox+processed + local for W117/W116 seats
def git_show(path):
    r = subprocess.run(['git', 'show', f'origin/main:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None
seats = {}
for d in ('fleet/inbox', 'fleet/inbox/processed'):
    r = subprocess.run(['git', 'ls-tree', '--name-only', f'origin/main:{d}'], capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        for name in r.stdout.split():
            if 'W11' in name and ('seat' in name.lower() or 'MSG' in name):
                mm = re.findall(r'W1(1[4-9])', name)
                if mm:
                    seats.setdefault(d, {})[name] = mm
out['seat_files_recent'] = seats

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
